"""
WNET5电路验证可视化引擎

基于传递函数理论计算WNET5电路的频率响应，并与实测数据对比
"""

import numpy as np
import matplotlib.pyplot as plt
import json
import sys
from pathlib import Path
from typing import Dict, List, Any
import logging
import os
try:
    import tensorflow as tf  # noqa: F401
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

logger = logging.getLogger(__name__)


def _convert_to_native_types(obj):
    """递归将numpy类型转换为Python原生类型"""
    if isinstance(obj, np.ndarray):
        return [_convert_to_native_types(item) for item in obj.tolist()]
    elif isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, dict):
        return {key: _convert_to_native_types(val) for key, val in obj.items()}
    elif isinstance(obj, list):
        return [_convert_to_native_types(item) for item in obj]
    else:
        return obj


class WNET5CircuitValidator:
    """WNET5电路验证器"""
    
    def __init__(self, config: Dict[str, Any], output_path: Path):
        self.config = config
        self.output_path = Path(output_path)
        self.model_project_name = config['model_project_name']
        self.frequency_range = config['frequency_range']
        # 可选: 实验对比数据 (Excel) - 旧的单文件对比配置（向后兼容）
        self.experiment_path = config.get('compare_with_experiment')

        # ⬇️⬇️⬇️ 新增：实验对比配置（C05） ⬇️⬇️⬇️
        self.experiment_comparison = config.get('experiment_comparison', {})
        self.exp_comp_enable = self.experiment_comparison.get('enable', False)
        self.exp_comp_mode = self.experiment_comparison.get('mode', 'single_file')
        self.exp_data_dir = self.experiment_comparison.get('experiment_data_dir')
        self.selftest_file = self.experiment_comparison.get('selftest_file')
        self.plot_config = self.experiment_comparison.get('plot_config', {})
        # ⬆️⬆️⬆️ 新增结束 ⬆️⬆️⬆️

        # 新增：指定要分析的Dense层编号（默认为1，向后兼容）
        self.analysis_layer = config.get('analysis_layer', 1)

        # 新增：推理配置（用于E96量化等）
        self.inference_config = config.get('inference_config', {})

        # 确保输出目录存在
        self._setup_output_directories()
        
    def _setup_output_directories(self):
        """设置输出目录结构"""
        self.output_path.mkdir(parents=True, exist_ok=True)
        (self.output_path / "plots").mkdir(exist_ok=True)
        # 使用 numerics 存放数值结果，避免出现 data\\data 的嵌套
        (self.output_path / "numerics").mkdir(exist_ok=True)
        (self.output_path / "reports").mkdir(exist_ok=True)

    def _load_selftest_data(self) -> Dict[str, np.ndarray]:
        """加载自测试频响数据（C05新增）

        Returns:
            Dict: {'frequencies': np.ndarray, 'magnitude': np.ndarray}
                  magnitude 单位为线性增益

        Raises:
            FileNotFoundError: 如果自测试文件不存在
            ValueError: 如果文件格式不正确
        """
        if not self.selftest_file:
            raise ValueError("未配置自测试文件路径 (selftest_file)")

        selftest_path = Path(self.selftest_file)
        if not selftest_path.exists():
            raise FileNotFoundError(f"自测试文件不存在: {selftest_path}")

        logger.info(f"📂 加载自测试数据: {selftest_path}")

        try:
            import pandas as pd
            df = pd.read_excel(selftest_path)

            # 查找频率列
            freq_cols = [c for c in df.columns if str(c).strip().lower() in [
                'f', 'freq', 'frequency', 'freq(hz)', 'frequency(hz)', 'hz'
            ]]
            if not freq_cols:
                raise ValueError(f"自测试文件中未找到频率列，列名: {df.columns.tolist()}")

            freq_col = freq_cols[0]
            frequencies = df[freq_col].to_numpy(dtype=float)

            # 查找增益列（自测试通常只有一个增益列）
            # 可能的列名：GAIN, GAIN/B1, Magnitude, Amplitude
            gain_cols = [c for c in df.columns if c != freq_col and
                         any(kw in str(c).upper() for kw in ['GAIN', 'MAGNITUDE', 'AMP'])]

            if not gain_cols:
                raise ValueError(f"自测试文件中未找到增益列，列名: {df.columns.tolist()}")

            gain_col = gain_cols[0]
            magnitude = df[gain_col].to_numpy(dtype=float)

            # 检查数据有效性
            if len(frequencies) != len(magnitude):
                raise ValueError(f"频率和增益数据长度不一致: {len(frequencies)} vs {len(magnitude)}")

            # 清理无效数据（NaN, Inf）
            valid_mask = np.isfinite(frequencies) & np.isfinite(magnitude)
            frequencies = frequencies[valid_mask]
            magnitude = magnitude[valid_mask]

            # 确保增益为正值（避免log运算错误）
            magnitude = np.clip(magnitude, 1e-20, None)

            logger.info(f"✅ 自测试数据加载成功: {len(frequencies)} 个频点")
            logger.info(f"   频率范围: {frequencies.min():.2f} - {frequencies.max():.2f} Hz")
            logger.info(f"   增益范围: {magnitude.min():.6f} - {magnitude.max():.6f}")

            return {
                'frequencies': frequencies,
                'magnitude': magnitude
            }

        except Exception as e:
            logger.error(f"加载自测试数据失败: {e}")
            raise

    def _parse_experiment_filename(self, filename: str) -> Dict[str, Any]:
        """解析实验数据文件名（C05新增）

        支持的命名格式：
        - output_{时间戳}_SVF-W_DENSE{层号}_{通道号}_震级1.0.xlsx
        - output_{时间戳}_SVF-W_DENSE{层号}-{通道号}_震级1.0.xlsx  (连字符格式)

        Args:
            filename: 文件名（不含路径）

        Returns:
            Dict: {
                'layer': int,        # 层号
                'channel': int,      # 通道号
                'timestamp': str,    # 时间戳
                'magnitude': float   # 震级（默认1.0）
            }
            如果解析失败，返回 None
        """
        import re

        # 模式1：下划线分隔 SVF-W_DENSE{层号}_{通道号}
        pattern1 = r'output_(\d+_\d+)_SVF-W_DENSE(\d+)_(\d+)_震级([\d.]+)\.xlsx'
        match = re.match(pattern1, filename)

        if match:
            timestamp, layer, channel, magnitude = match.groups()
            return {
                'layer': int(layer),
                'channel': int(channel),
                'timestamp': timestamp,
                'magnitude': float(magnitude)
            }

        # 模式2：连字符分隔 SVF-W_DENSE{层号}-{通道号}
        pattern2 = r'output_(\d+_\d+)_SVF-W_DENSE(\d+)-(\d+)_震级([\d.]+)\.xlsx'
        match = re.match(pattern2, filename)

        if match:
            timestamp, layer, channel, magnitude = match.groups()
            return {
                'layer': int(layer),
                'channel': int(channel),
                'timestamp': timestamp,
                'magnitude': float(magnitude)
            }

        # 解析失败
        return None

    def _scan_experiment_files(self, target_layer: int) -> Dict[int, Path]:
        """扫描实验数据目录，查找指定层的所有通道数据文件（C05新增）

        Args:
            target_layer: 目标层号

        Returns:
            Dict[int, Path]: {通道号: 文件路径}

        Raises:
            FileNotFoundError: 如果实验数据目录不存在
        """
        if not self.exp_data_dir:
            raise ValueError("未配置实验数据目录 (experiment_data_dir)")

        exp_dir = Path(self.exp_data_dir)
        if not exp_dir.exists():
            raise FileNotFoundError(f"实验数据目录不存在: {exp_dir}")

        logger.info(f"🔍 扫描实验数据目录: {exp_dir}")
        logger.info(f"   目标层: {target_layer}")

        # 扫描目录中的所有 .xlsx 文件
        channel_files = {}

        for file_path in exp_dir.glob('*.xlsx'):
            filename = file_path.name

            # 跳过自测试文件
            if 'selftest' in filename.lower():
                continue

            # 解析文件名
            parsed = self._parse_experiment_filename(filename)

            if parsed is None:
                logger.debug(f"   跳过无法解析的文件: {filename}")
                continue

            # 检查是否匹配目标层
            if parsed['layer'] == target_layer:
                channel = parsed['channel']

                # 检查重复
                if channel in channel_files:
                    logger.warning(
                        f"   ⚠️ 发现重复通道数据: 层{target_layer}通道{channel}\n"
                        f"      已有: {channel_files[channel].name}\n"
                        f"      新文件: {filename}\n"
                        f"      将使用新文件（假设时间戳更新）"
                    )

                channel_files[channel] = file_path
                logger.info(f"   ✅ 找到: 层{target_layer}通道{channel} - {filename}")

        if not channel_files:
            logger.warning(f"⚠️ 未找到层{target_layer}的实验数据文件")
            return {}

        logger.info(f"✅ 共找到 {len(channel_files)} 个通道的实验数据")

        # 按通道号排序
        sorted_channels = dict(sorted(channel_files.items()))
        return sorted_channels

    def _load_experiment_channel_data(self, file_path: Path) -> Dict[str, np.ndarray]:
        """加载单个实验通道的数据（C05新增）

        Args:
            file_path: 实验数据文件路径

        Returns:
            Dict: {'frequencies': np.ndarray, 'magnitude': np.ndarray}
                  magnitude 单位为线性增益

        Raises:
            ValueError: 如果文件格式不正确
        """
        logger.debug(f"   加载实验数据: {file_path.name}")

        try:
            import pandas as pd
            df = pd.read_excel(file_path)

            # 查找频率列
            freq_cols = [c for c in df.columns if str(c).strip().lower() in [
                'f', 'freq', 'frequency', 'freq(hz)', 'frequency(hz)', 'hz'
            ]]
            if not freq_cols:
                raise ValueError(f"文件中未找到频率列: {file_path.name}")

            freq_col = freq_cols[0]
            frequencies = df[freq_col].to_numpy(dtype=float)

            # 查找增益列
            gain_cols = [c for c in df.columns if c != freq_col and
                         any(kw in str(c).upper() for kw in ['GAIN', 'MAGNITUDE', 'AMP'])]

            if not gain_cols:
                raise ValueError(f"文件中未找到增益列: {file_path.name}")

            gain_col = gain_cols[0]
            magnitude = df[gain_col].to_numpy(dtype=float)

            # 数据清理
            valid_mask = np.isfinite(frequencies) & np.isfinite(magnitude)
            frequencies = frequencies[valid_mask]
            magnitude = magnitude[valid_mask]
            magnitude = np.clip(magnitude, 1e-20, None)

            return {
                'frequencies': frequencies,
                'magnitude': magnitude
            }

        except Exception as e:
            logger.error(f"加载实验数据失败 {file_path.name}: {e}")
            raise

    def _compensate_with_selftest(
        self,
        exp_freq: np.ndarray,
        exp_mag: np.ndarray,
        selftest_data: Dict[str, np.ndarray]
    ) -> np.ndarray:
        """使用自测试数据补偿实验数据（C05新增）

        补偿方法：exp_compensated = exp_mag / selftest_mag
        通过插值使自测试数据与实验数据的频点对齐

        Args:
            exp_freq: 实验数据的频率点
            exp_mag: 实验数据的幅度（线性增益）
            selftest_data: 自测试数据 {'frequencies', 'magnitude'}

        Returns:
            np.ndarray: 补偿后的幅度（线性增益）
        """
        from scipy.interpolate import interp1d

        selftest_freq = selftest_data['frequencies']
        selftest_mag = selftest_data['magnitude']

        # 检查频率范围是否覆盖
        exp_min, exp_max = exp_freq.min(), exp_freq.max()
        self_min, self_max = selftest_freq.min(), selftest_freq.max()

        if exp_min < self_min or exp_max > self_max:
            logger.warning(
                f"⚠️ 实验数据频率范围 [{exp_min:.2f}, {exp_max:.2f}] Hz "
                f"超出自测试范围 [{self_min:.2f}, {self_max:.2f}] Hz"
            )

        # 使用线性插值（对数空间）
        selftest_db = 20 * np.log10(selftest_mag + 1e-20)

        # 创建插值函数
        interp_func = interp1d(
            selftest_freq,
            selftest_db,
            kind='linear',
            bounds_error=False,
            fill_value='extrapolate'
        )

        # 在实验频点处插值
        selftest_db_interp = interp_func(exp_freq)
        selftest_mag_interp = np.power(10.0, selftest_db_interp / 20.0)

        # 执行补偿（相除）
        compensated_mag = exp_mag / (selftest_mag_interp + 1e-20)

        return compensated_mag

    def _to_list_2d(self, arr):
        """将二维numpy数组转换为纯float嵌套list (确保JSON可序列化)"""
        if arr is None:
            return []
        arr = np.asarray(arr)
        if arr.ndim != 2:
            raise ValueError(f"_to_list_2d 期望二维数组, 实际ndim={arr.ndim}")
        return [[float(x) for x in row] for row in arr]
    
    def execute_validation(self) -> bool:
        """执行WNET5电路验证流程"""
        try:
            logger.info("开始WNET5电路验证分析...")

            # 统一从 project 加载权重（纯 JSON，无 TensorFlow 依赖）
            logger.info(f"从 project '{self.model_project_name}' 加载权重...")
            svf_params = self._load_svf_parameters_from_project()
            dense_weights = self._load_dense_weights_from_project(self.analysis_layer)

            # 1.5 生成E96量化对比数据（如果启用）
            quantization_comparison = self._generate_e96_quantization_comparison(dense_weights)

            # 2. 计算传递函数
            svf_tfs = self._calculate_svf_transfer_functions(svf_params)
            combined_tfs = self._calculate_combined_transfer_functions(svf_tfs, dense_weights)

            # 3. 计算频率响应（使用默认频率点保持计算精度）
            freq_response = self._calculate_frequency_response(combined_tfs)

            # 4. 生成可视化
            plots = self._generate_plots(freq_response, dense_weights)

            # 5. 生成 E96 量化频率响应对比图（与 frequency_response_comparison_merged.png 相同风格）
            if quantization_comparison:
                e96_freq_plot = self._generate_e96_frequency_response_comparison(
                    freq_response, dense_weights, quantization_comparison
                )
                if e96_freq_plot:
                    plots.append(e96_freq_plot)

            # 6. 生成报告
            report = self._generate_analysis_report(svf_params, dense_weights, freq_response)

            # 7. 保存结果 (单一 results.json)
            self._save_results(svf_params, svf_tfs, combined_tfs, freq_response, dense_weights, plots, report, quantization_comparison)

            logger.info("✅ WNET5电路验证分析完成")
            return True

        except Exception as e:
            logger.error(f"WNET5电路验证分析失败: {e}")
            return False

    def _load_svf_parameters_from_project(self) -> Dict[str, Any]:
        """从 project 的 config.json 加载 SVF 参数（纯 JSON，无 TensorFlow）"""
        project_cfg_path = Path('projects') / self.model_project_name / 'config.json'
        if not project_cfg_path.exists():
            raise FileNotFoundError(f"项目配置不存在: {project_cfg_path}")

        with open(project_cfg_path, 'r', encoding='utf-8') as f:
            project_cfg = json.load(f)

        # 兼容不同配置结构
        # 情况1: model.model_subcfg.init_center_freqs (嵌套结构)
        # 情况2: model_subcfg.init_center_freqs (扁平结构)
        if 'model' in project_cfg and 'model_subcfg' in project_cfg['model']:
            subcfg = project_cfg['model']['model_subcfg']
        else:
            subcfg = project_cfg.get('model_subcfg', {})

        center_freqs = subcfg.get('init_center_freqs', [])
        quality_factors = subcfg.get('init_quality_factors', [])

        if not center_freqs or not quality_factors:
            raise ValueError(f"项目 {self.model_project_name} 缺少 SVF 参数")

        return {
            'center_freqs': [float(f) for f in center_freqs],
            'quality_factors': [float(q) for q in quality_factors]
        }

    def _load_dense_weights_from_project(self, analysis_layer: int = 1) -> Dict[str, Any]:
        """从 project 的 best.weights.json 加载指定 Dense 层权重（纯 JSON）"""
        weights_json_path = Path('projects') / self.model_project_name / 'data' / 'best.weights.json'
        if not weights_json_path.exists():
            raise FileNotFoundError(f"权重文件不存在: {weights_json_path}")

        with open(weights_json_path, 'r', encoding='utf-8') as f:
            weights_data = json.load(f)

        # WNET5 结构: layer_to_layer_models[0]=SVF, [1]=Dense1, [2]=Dense2, [3]=Dense3
        # best.weights.json 中的命名:
        # - analysis_layer=1 -> "dense/kernel:0", "dense/bias:0"
        # - analysis_layer=2 -> "post_dense_1/kernel:0", "post_dense_1/bias:0"
        # - analysis_layer=3 -> "post_dense_2/kernel:0", "post_dense_2/bias:0"
        # - analysis_layer=4 -> "post_dense_3/kernel:0", "post_dense_3/bias:0"

        # 根据层号映射到权重名称
        # analysis_layer 对应模型中的 dense 层：
        # - analysis_layer=1 -> post_dense_1 (6→6)
        # - analysis_layer=2 -> post_dense_2 (6→6)
        # - analysis_layer=3 -> post_dense_3 (6→6)
        # - analysis_layer=4 -> dense (6→1，最终输出层)
        layer_name_map = {
            1: ('post_dense_1', 'Dense_Layer_Model_1'),
            2: ('post_dense_2', 'Dense_Layer_Model_2'),
            3: ('post_dense_3', 'Dense_Layer_Model_3'),
            4: ('dense', 'Output_Layer_Model')
        }

        if analysis_layer not in layer_name_map:
            raise ValueError(f"无效的 analysis_layer: {analysis_layer}")

        layer_prefix, layer_name = layer_name_map[analysis_layer]

        # 查找 kernel 和 bias (使用第一个匹配项)
        kernel = None
        bias = None

        for entry in weights_data:
            name = entry.get('name', '')
            if name == f"{layer_prefix}/kernel:0":
                kernel = np.array(entry['value'], dtype=np.float32)
                logger.info(f"找到 {layer_prefix}/kernel:0: shape={kernel.shape}")
            elif name == f"{layer_prefix}/bias:0" and bias is None:
                bias = np.array(entry['value'], dtype=np.float32)
                logger.info(f"找到 {layer_prefix}/bias:0: shape={bias.shape}")

        if kernel is None:
            raise ValueError(f"未找到层 {analysis_layer} ({layer_prefix}/kernel:0) 的权重")

        # 如果没有 bias，使用零向量
        if bias is None:
            bias = np.zeros(kernel.shape[1], dtype=np.float32)

        # 归一化 kernel 形状
        if kernel.ndim == 3:
            if kernel.shape[0] != 1:
                raise ValueError(f"期望 kernel_size=1，实际 {kernel.shape[0]}")
            kernel = kernel[0]

        logger.info(f"✅ 从 JSON 加载 Dense 层 {analysis_layer}: kernel={kernel.shape}, bias={bias.shape}")

        return {
            'layer_name': layer_name,
            'weights': kernel,
            'bias': bias,
            'analysis_layer': analysis_layer
        }

    def _generate_e96_quantization_comparison(self, dense_weights: Dict[str, Any]):
        """生成E96量化对比数据

        Args:
            dense_weights: 包含 'weights' 和 'bias' 的字典

        Returns:
            Dict: E96量化对比数据，如果未启用则返回None
        """
        use_e96 = self.inference_config.get('use_e96', False)
        include_comparison = self.inference_config.get('include_quantization_comparison', False)

        if not include_comparison:
            return None

        if not use_e96:
            logger.warning("include_quantization_comparison=True 但 use_e96=False，跳过量化对比生成")
            return None

        logger.info("生成E96量化对比数据...")

        try:
            from spice_simulator.circuit_dense import DenseCircuitFactory

            weights = dense_weights['weights']
            bias = dense_weights['bias']
            layer_name = dense_weights.get('layer_name', f'layer{self.analysis_layer}')

            # 创建DenseCircuit，启用E96和量化对比
            circuit = DenseCircuitFactory.create(
                gains=weights,
                biases=bias,
                use_e96=True,
                use_relu=False,
                layer_name=layer_name,
                include_quantization_comparison=True
            )

            # 生成量化对比数据
            comparison_data = circuit.generate_quantization_comparison_data()

            if comparison_data:
                logger.info(f"✅ E96量化对比数据生成完成: {comparison_data.get('statistics', {}).get('total_count', 0)} 个电阻")
            else:
                logger.warning("E96量化对比数据生成返回空")

            return comparison_data

        except Exception as e:
            logger.error(f"生成E96量化对比数据失败: {e}")
            return None

    def _load_model(self):
        """加载真实的WaveNet5模型并加载权重

        规则:
        1. 优先使用 config['weights_path'] 指定的绝对或相对路径
        2. 否则使用 projects/{model_project_name}/data/best.weights.h5
        3. 必须存在对应项目目录; 若缺失抛出异常
        4. 加载成功后返回实例化且权重已加载的模型
        """
        if not TF_AVAILABLE:
            raise ImportError("当前环境未安装TensorFlow，无法构建与加载WaveNet5模型。请先安装tensorflow或提供预导出的dense_weights.json与svf_parameters.json供频率响应计算。(建议: pip install tensorflow==2.15.*) 或在配置中添加 'offline_mode': true 以跳过。")

        from models.wavenet_models import WaveNet5

        # 决定权重路径
        weights_path_cfg = self.config.get('weights_path')
        if weights_path_cfg:
            weights_path = Path(weights_path_cfg)
        else:
            weights_path = Path('projects') / self.model_project_name / 'data' / 'best.weights.h5'

        if not weights_path.exists():
            raise FileNotFoundError(f"未找到权重文件: {weights_path}")

        # 读取项目配置(如果存在) 以获取 model_subcfg; 否则使用默认
        project_cfg_path = Path('projects') / self.model_project_name / 'config.json'
        model_subcfg = {}
        if project_cfg_path.exists():
            try:
                with open(project_cfg_path, 'r', encoding='utf-8') as f:
                    proj_cfg = json.load(f)
                model_subcfg = proj_cfg.get('model', {}).get('model_subcfg', {}) or proj_cfg.get('model_subcfg', {}) or {}
            except Exception as e:
                logger.warning(f"读取项目配置失败 {project_cfg_path}: {e}, 使用默认子配置")

        logger.info(f"加载模型权重: {weights_path}")
        model = WaveNet5(model_subcfg=model_subcfg)

        # 加载权重(包含 layer_to_layer_models 权重同步)
        model.load_weights(str(weights_path))

        # 记录第一层/后处理层信息
        logger.info(f"SVF滤波器数量: {len(model.subcfg.get('init_center_freqs', []))}")
        dense_layers = [l for l in model.layer_to_layer_models if 'Dense' in l.name or 'Output' in l.name]
        logger.info(f"检测到Dense相关分层: {[l.name for l in dense_layers]}")

        return model
    
    def _extract_svf_parameters(self, model):
        """提取SVF层参数 (真实模型)"""
        c = model.subcfg.get('init_center_freqs')
        q = model.subcfg.get('init_quality_factors')
        if c is None or q is None:
            raise ValueError("模型缺少SVF参数 init_center_freqs 或 init_quality_factors")
        if len(c) != len(q):
            raise ValueError(f"中心频率与Q数量不匹配: {len(c)} != {len(q)}")
        return {
            'center_freqs': list(map(float, c)),
            'quality_factors': list(map(float, q))
        }
    
    def _extract_dense_weights(self, model, analysis_layer: int = 1):
        """提取指定Dense层的权重

        Args:
            model: WaveNet5模型实例
            analysis_layer: 要分析的Dense层编号 (1/2/3/4)
                           1 = Dense_Layer_Model_1 (layer_to_layer_models[1])
                           2 = Dense_Layer_Model_2 (layer_to_layer_models[2])
                           3 = Dense_Layer_Model_3 (layer_to_layer_models[3])
                           4 = Output_Layer_Model (layer_to_layer_models[4])，如果存在

        Returns:
            Dict: 包含 layer_name, weights, bias, analysis_layer 的字典

        Raises:
            ValueError: 如果指定的层不存在或无法获取权重
        """
        # 验证 analysis_layer 的有效性
        if analysis_layer < 1:
            raise ValueError(f"analysis_layer 必须 >= 1，当前值: {analysis_layer}")

        # 计算目标层在 layer_to_layer_models 中的索引
        # analysis_layer=1 -> 索引1 (Dense_Layer_Model_1)
        # analysis_layer=2 -> 索引2 (Dense_Layer_Model_2)
        # analysis_layer=3 -> 索引3 (Dense_Layer_Model_3)
        target_index = analysis_layer  # 直接使用 analysis_layer 作为索引

        # 检查目标索引是否在有效范围内
        if target_index >= len(model.layer_to_layer_models):
            available_layers = len(model.layer_to_layer_models) - 1  # 减去SVF层
            raise ValueError(
                f"请求的 analysis_layer={analysis_layer} 超出范围。"
                f"模型共有 {available_layers} 个Dense/输出层 "
                f"(layer_to_layer_models 长度: {len(model.layer_to_layer_models)}, "
                f"索引0为SVF层)。"
                f"有效的 analysis_layer 值为 1-{available_layers}。"
            )

        # 获取目标层
        dense_candidate = model.layer_to_layer_models[target_index]

        # 验证目标层确实是Dense层（不是SVF层）
        if target_index == 0:
            raise ValueError(f"analysis_layer=0 对应SVF层，无法提取Dense权重。请使用 analysis_layer >= 1。")

        # 尝试获取权重
        try:
            weights_list = dense_candidate.model.get_weights()
            if not weights_list:
                raise ValueError(f"层 '{dense_candidate.name}' 没有可用的权重")
        except Exception as e:
            raise ValueError(f"无法从层 '{dense_candidate.name}' 获取权重: {e}")

        # 提取kernel和bias（与原代码逻辑相同）
        kernel = None
        bias = None
        if len(weights_list) == 2:
            kernel, bias = weights_list
        elif len(weights_list) == 1:
            kernel = weights_list[0]
        else:
            # 可能存在BN等
            kernel = weights_list[0]
            bias = weights_list[1] if len(weights_list) > 1 else None

        # 归一化形状到 (in_ch, out_ch)
        if kernel.ndim == 3:  # (k, in, out)
            if kernel.shape[0] != 1:
                raise ValueError(f"期望kernel_size=1, 实际kernel第一维={kernel.shape[0]}")
            kernel_mat = kernel[0]
        elif kernel.ndim == 2:
            kernel_mat = kernel
        else:
            raise ValueError(f"无法解析Dense/Conv权重形状: {kernel.shape}")

        if bias is None:
            bias_vec = np.zeros(kernel_mat.shape[1], dtype=np.float32)
        else:
            bias_vec = bias

        # 记录提取的层信息
        logger.info(f"✅ 提取Dense层 '{dense_candidate.name}' (analysis_layer={analysis_layer}, 索引={target_index})")
        logger.info(f"   权重形状: {kernel_mat.shape}, 偏置形状: {bias_vec.shape}")

        return {
            'layer_name': dense_candidate.name,
            'weights': kernel_mat,
            'bias': bias_vec,
            'analysis_layer': analysis_layer  # 新增：记录分析的层编号
        }
    
    def _calculate_svf_transfer_functions(self, svf_params):
        """计算SVF传递函数"""
        logger.info("计算SVF传递函数...")
        import sympy as sp
        s = sp.Symbol('s')
        
        transfer_functions = []
        for f0, Q in zip(svf_params['center_freqs'], svf_params['quality_factors']):
            omega0 = 2 * sp.pi * f0
            denominator = s**2 + (omega0/Q)*s + omega0**2
            
            H_hp = s**2 / denominator                    # 高通
            H_bp = (s * omega0/Q) / denominator          # 带通  
            H_lp = omega0**2 / denominator               # 低通
            
            transfer_functions.append({
                'high_pass': H_hp,
                'band_pass': H_bp,
                'low_pass': H_lp,
                'f0': f0,
                'Q': Q
            })
        
        return transfer_functions
    
    def _adapt_svf_channels(self, all_svf_channels: list, target_channels: int) -> tuple[list, str]:
        """自适应调整SVF通道数以匹配目标通道数

        Args:
            all_svf_channels: 原始SVF通道列表 (SymPy表达式)
            target_channels: 目标通道数 (权重输入通道数)

        Returns:
            tuple: (调整后的通道列表, 操作描述字符串)

        Raises:
            ValueError: 如果目标通道数 <= 0
        """
        current_channels = len(all_svf_channels)

        if current_channels == target_channels:
            return all_svf_channels, "通道数匹配，无需调整"

        if target_channels <= 0:
            raise ValueError(f"目标通道数必须 > 0，实际: {target_channels}")

        adapted_channels = []

        if current_channels > target_channels:
            # 裁剪模式：SVF通道 > 权重通道
            adapted_channels = all_svf_channels[:target_channels]
            operation = "裁剪"
        else:
            # 循环拓展模式：SVF通道 < 权重通道
            for i in range(target_channels):
                adapted_channels.append(all_svf_channels[i % current_channels])
            operation = "循环拓展"

        return adapted_channels, operation

    def _calculate_combined_transfer_functions(self, svf_tfs, dense_weights):
        """计算SVF+Dense组合传递函数（支持通道自适应）"""
        logger.info("计算组合传递函数...")
        import sympy as sp

        # 展开所有SVF通道 (顺序: 每个滤波器 HP,BP,LP)
        all_svf_channels = []
        for svf in svf_tfs:
            all_svf_channels.extend([svf['high_pass'], svf['band_pass'], svf['low_pass']])

        n_inputs = len(all_svf_channels)
        w = dense_weights['weights']  # (in_ch, out_ch)
        target_channels = w.shape[0]

        # 通道自适应适配
        if n_inputs != target_channels:
            adapted_channels, operation = self._adapt_svf_channels(all_svf_channels, target_channels)
            logger.warning(
                f"SVF通道数 ({n_inputs}) 与权重输入通道数 ({target_channels}) 不匹配，"
                f"已{operation}适配"
            )
            logger.warning(f"   原始SVF通道: {n_inputs} -> 适配后: {len(adapted_channels)}")
            all_svf_channels = adapted_channels
            n_inputs = len(all_svf_channels)

        # 验证适配后是否匹配
        if n_inputs != target_channels:
            raise ValueError(
                f"通道适配失败: SVF通道适配后为 {n_inputs}，但权重需要 {target_channels} 通道"
            )

        bias_vec = dense_weights['bias']
        out_ch = w.shape[1]
        combined = []
        for o in range(out_ch):
            Hc = bias_vec[o]
            for i, H_svf in enumerate(all_svf_channels):
                Hc += w[i, o] * H_svf
            combined.append(Hc)
        return combined
    
    def _calculate_frequency_response(self, transfer_functions):
        """计算所有输出通道频率响应"""
        logger.info("计算频率响应...")
        import sympy as sp

        start_freq = float(self.frequency_range['start_freq'])
        stop_freq = float(self.frequency_range['stop_freq'])
        points = int(self.frequency_range.get('points', 1000))
        frequencies = np.logspace(np.log10(start_freq), np.log10(stop_freq), points)

        omega = 2 * np.pi * frequencies
        s_vals = 1j * omega
        s = sp.Symbol('s')

        mag_db_all = []
        phase_deg_all = []
        for idx, Hsym in enumerate(transfer_functions):
            try:
                H_func = sp.lambdify(s, Hsym, 'numpy')
                H_resp = H_func(s_vals)
            except Exception as e:
                logger.error(f"通道{idx} 符号->数值失败: {e}, 使用单位响应")
                H_resp = np.ones_like(s_vals, dtype=complex)
            mag = np.abs(H_resp)
            mag_db_all.append(20 * np.log10(mag + 1e-20))
            phase_deg_all.append(np.degrees(np.angle(H_resp)))

        return {
            'frequencies': frequencies,
            'magnitude_db': mag_db_all,  # list of arrays
            'phase_deg': phase_deg_all,
        }
    
    def _generate_plots(self, freq_response, dense_weights):
        """生成幅频响应图（支持多种对比模式）（C05重构）

        根据配置选择使用单文件对比模式（旧）或多文件对比模式（新C05）
        """
        logger.info("生成幅频响应图...")

        # 决定使用哪种对比模式
        if self.exp_comp_enable and self.exp_comp_mode == 'multi_file':
            # 新模式：多文件对比（C05需求）
            return self._generate_plots_multi_file(freq_response, dense_weights)
        else:
            # 旧模式：单文件对比（保持向后兼容）
            return self._generate_plots_single_file(freq_response, dense_weights)

    def _generate_plots_single_file(self, freq_response, dense_weights):
        """单文件对比模式（旧逻辑，向后兼容）"""
        logger.info("使用单文件对比模式...")

        # 1. 理论幅度 (内部存储为 dB, 转线性)
        frequencies = freq_response['frequencies']
        mag_db_list = freq_response['magnitude_db']
        mag_list = [np.clip(np.power(10.0, m/20.0), 1e-20, None) for m in mag_db_list]
        # 根据当前分析的层生成标签
        analysis_layer = dense_weights.get('analysis_layer', 1)
        output_labels = [f'D{analysis_layer}_{i+1}' for i in range(len(mag_list))]

        # 检查是否启用合并模式
        merged_plot_mode = self.plot_config.get('merged_plot_mode', False)

        # 2. 读取实验数据 (列名形式 D{layer}_[N]_GAIN/B1)
        exp_freq = None
        exp_mags = None
        if self.experiment_path:
            try:
                import pandas as pd, re
                exp_file = Path(self.experiment_path)
                if exp_file.exists():
                    # 检查是否是新的多sheet格式
                    experiment_sheet_name = self.experiment_comparison.get('experiment_sheet_name')
                    if experiment_sheet_name:
                        # 新格式：读取指定的sheet
                        df = pd.read_excel(exp_file, sheet_name=experiment_sheet_name)
                        logger.info(f"读取实验数据sheet: {experiment_sheet_name}")
                    else:
                        # 旧格式：读取默认sheet
                        df = pd.read_excel(exp_file)
                    freq_cols = [c for c in df.columns if str(c).strip().lower() in ['f','freq','frequency','freq(hz)','frequency(hz)','hz']]
                    fcol = freq_cols[0] if freq_cols else df.columns[0]
                    exp_freq = df[fcol].to_numpy(dtype=float)

                    # 动态匹配当前分析的层
                    matched = {}

                    # 检查是否是新的GAIN/CH格式
                    gain_ch_pattern = re.compile(r'^GAIN/CH(\d+)$')
                    for c in df.columns:
                        if c == fcol:
                            continue

                        # 尝试新的GAIN/CH格式
                        m = gain_ch_pattern.match(str(c).strip())
                        if m:
                            idx = int(m.group(1))
                            try:
                                arr = df[c].astype(float).to_numpy(dtype=float)
                                matched[idx] = arr
                                logger.debug(f"匹配新格式通道: {c} -> CH{idx}")
                            except Exception:
                                continue
                            continue

                        # 尝试旧的D{layer}_N_GAIN/B1格式
                        pattern = re.compile(rf'^D{analysis_layer}_(\d+)_GAIN/B1$')
                        m = pattern.match(str(c).strip())
                        if m:
                            idx = int(m.group(1))
                            try:
                                arr = df[c].astype(float).to_numpy(dtype=float)
                                matched[idx] = arr
                                logger.debug(f"匹配旧格式通道: {c} -> CH{idx}")
                            except Exception:
                                continue
                    if matched:
                        max_theo = len(mag_list)
                        series = []
                        used_labels = []
                        for ch in range(1, max_theo+1):
                            if ch in matched:
                                series.append(np.clip(matched[ch], 1e-20, None))
                                used_labels.append(f'D{analysis_layer}_{ch}')
                        if series:
                            exp_mags = series
                            if len(exp_mags) != len(mag_list):
                                logger.warning(f"实验匹配通道数{len(exp_mags)} != 理论{len(mag_list)}. 仅对比前 {len(exp_mags)} 个")
                                mag_list = mag_list[:len(exp_mags)]
                                output_labels = output_labels[:len(exp_mags)]
                            logger.info(f"匹配实验列: {used_labels}")
                        else:
                            logger.warning("未按模式匹配到任何实验通道, 忽略对比")
                    else:
                        experiment_sheet_name = self.experiment_comparison.get('experiment_sheet_name')
                        if experiment_sheet_name:
                            logger.warning(f"实验数据sheet '{experiment_sheet_name}' 中未找到匹配列 GAIN/CH[N]")
                        else:
                            logger.warning(f"实验数据缺少匹配列 D{analysis_layer}_[N]_GAIN/B1")
                else:
                    logger.warning(f"实验数据文件不存在: {self.experiment_path}")
            except Exception as e:
                logger.warning(f"实验数据加载失败: {e}")

        # 3. 颜色
        import matplotlib as mpl
        cmap = mpl.cm.get_cmap('tab10', len(mag_list)) if len(mag_list) <= 10 else mpl.cm.get_cmap('turbo', len(mag_list))
        colors = [cmap(i) for i in range(len(mag_list))]

        plots = []
        if exp_mags is not None and exp_freq is not None:
            if merged_plot_mode:
                # 合并模式：单图显示，仿真虚线，实测实线
                logger.info("使用合并模式：单图显示，仿真虚线，实测实线")
                # 调整尺寸与原始子图保持一致（原始上下布局12x8，每个子图约12x4）
                fig, ax = plt.subplots(figsize=(12, 4))

                # 绘制仿真结果（虚线）
                for i, (m, lbl) in enumerate(zip(mag_list, output_labels)):
                    ax.semilogx(frequencies, m, color=colors[i], linewidth=1.4,
                               linestyle='--', label=f'{lbl} (仿真)', alpha=0.8)

                # 绘制实测结果（实线）
                for i, (m, lbl) in enumerate(zip(exp_mags, output_labels)):
                    ax.semilogx(exp_freq, m, color=colors[i], linewidth=1.8,
                               linestyle='-', label=f'{lbl} (实测)', alpha=0.9)

                ax.set_title(f'{self.model_project_name} Dense#{analysis_layer} 频率响应对比 (仿真虚线 vs 实测实线)', fontsize=12, fontweight='bold')
                ax.set_xlabel('频率 (Hz)', fontsize=10)
                ax.set_ylabel('增益 (线性, log刻度)', fontsize=10)
                ax.set_yscale('log')
                ax.grid(True, which='both', alpha=0.3)

                # 设置y轴范围
                all_vals = np.concatenate([*mag_list, *exp_mags])
                y_min, y_max = float(np.nanmin(all_vals)), float(np.nanmax(all_vals))
                pad = 0.05
                y_min_adj = max(1e-20, y_min / (1+pad))
                y_max_adj = y_max * (1+pad)
                ax.set_ylim(y_min_adj, y_max_adj)

                # 图例：分开仿真和实测
                ax.legend(fontsize=8, ncol=min(4, len(output_labels)*2), loc='best')
                plt.tight_layout()

                plot_path = self.output_path / 'plots' / 'frequency_response_comparison_merged.png'
                plt.savefig(plot_path, dpi=300, bbox_inches='tight')
                plt.close(fig)
                plots.append(str(plot_path))
                logger.info(f"合并对比图已保存: {plot_path}")
            else:
                # 原始模式：上下两个图
                fig, (ax_top, ax_bottom) = plt.subplots(2, 1, figsize=(12, 8))
                for i, (m, lbl) in enumerate(zip(mag_list, output_labels)):
                    ax_top.semilogx(frequencies, m, color=colors[i], linewidth=1.4, label=lbl)
                for i, (m, lbl) in enumerate(zip(exp_mags, output_labels)):
                    ax_bottom.semilogx(exp_freq, m, color=colors[i], linewidth=1.2, label=lbl)
                ax_top.set_title(f'{self.model_project_name} Dense#{analysis_layer} 输出 频率响应 (理论, 线性增益)')
                ax_bottom.set_title('实验测量 频率响应 (线性增益)')
                ax_bottom.set_xlabel('频率 (Hz)')
                for ax in (ax_top, ax_bottom):
                    ax.set_ylabel('增益 (线性, log刻度)')
                    ax.set_yscale('log')
                    ax.grid(True, which='both', alpha=0.3)
                all_vals = np.concatenate([*mag_list, *exp_mags])
                y_min, y_max = float(np.nanmin(all_vals)), float(np.nanmax(all_vals))
                pad = 0.05
                y_min_adj = max(1e-20, y_min / (1+pad))
                y_max_adj = y_max * (1+pad)
                ax_top.set_ylim(y_min_adj, y_max_adj)
                ax_bottom.set_ylim(y_min_adj, y_max_adj)
                ax_top.legend(fontsize=8, ncol=min(4, len(output_labels)))
                ax_bottom.legend(fontsize=8, ncol=min(4, len(output_labels)))
                plt.tight_layout()
                plot_path = self.output_path / 'plots' / 'frequency_response_comparison.png'
                plt.savefig(plot_path, dpi=300)
                plt.close(fig)
                plots.append(str(plot_path))
                logger.info(f"对比图已保存: {plot_path}")

            # 生成误差图：仿真数据 ÷ 实际数据
            # 只在误差计算时使用实验频率点，避免对实验数据插值
            from scipy import interpolate
            fig, ax = plt.subplots(figsize=(12, 6))

            for i, (theory_mag, exp_mag, lbl) in enumerate(zip(mag_list, exp_mags, output_labels)):
                # 将理论数据插值到实验频率点
                theory_interp = interpolate.interp1d(frequencies, theory_mag, kind='linear',
                                                   bounds_error=False, fill_value=np.nan)
                theory_mag_interp = theory_interp(exp_freq)

                # 计算误差：理论插值数据 ÷ 实验数据
                with np.errstate(divide='ignore', invalid='ignore'):
                    error_ratio = theory_mag_interp / exp_mag
                    error_ratio = np.where(np.abs(exp_mag) < 1e-20, np.nan, error_ratio)

                # 绘制误差曲线（使用实验频率点）
                ax.semilogx(exp_freq, error_ratio, color=colors[i], linewidth=1.4,
                           label=f'{lbl} (理论/实验)', marker='o', markersize=2, alpha=0.7)

            ax.set_title(f'{self.model_project_name} Dense#{analysis_layer} 频率响应误差分析 (仿真数据÷实际数据)')
            ax.set_xlabel('频率 (Hz)')
            ax.set_ylabel('误差比值 (仿真÷实际)')
            ax.set_yscale('log')
            ax.grid(True, which='both', alpha=0.3)
            ax.axhline(y=1.0, color='red', linestyle='--', alpha=0.5, label='理想匹配线 (比值=1.0)')

            # 设置更密集的Y轴刻度
            from matplotlib.ticker import MultipleLocator, LogLocator
            ax.yaxis.set_major_locator(LogLocator(base=10.0, numticks=20))
            ax.yaxis.set_minor_locator(LogLocator(base=10.0, subs='auto', numticks=100))

            ax.legend(fontsize=8, ncol=min(4, len(output_labels)))
            plt.tight_layout()

            error_plot_path = self.output_path / 'plots' / 'frequency_response_error_ratio.png'
            plt.savefig(error_plot_path, dpi=300)
            plt.close(fig)
            plots.append(str(error_plot_path))
            logger.info(f"误差比值图已保存: {error_plot_path}")

            # 保存误差数据到JSON文件，供后续results.json使用
            error_data = {
                'frequencies': exp_freq.tolist(),  # 使用实验频率点
                'error_ratios': [],
                'statistics': []
            }
            for i, (theory_mag, exp_mag, lbl) in enumerate(zip(mag_list, exp_mags, output_labels)):
                # 将理论数据插值到实验频率点
                theory_interp = interpolate.interp1d(frequencies, theory_mag, kind='linear',
                                                   bounds_error=False, fill_value=np.nan)
                theory_mag_interp = theory_interp(exp_freq)

                # 计算误差：理论插值数据 ÷ 实验数据
                with np.errstate(divide='ignore', invalid='ignore'):
                    error_ratio = theory_mag_interp / exp_mag
                    error_ratio = np.where(np.abs(exp_mag) < 1e-20, np.nan, error_ratio)

                error_data['error_ratios'].append({
                    'channel': lbl,
                    'ratios': error_ratio.tolist()
                })

                # 计算误差统计
                valid_errors = error_ratio[~np.isnan(error_ratio)]
                if len(valid_errors) > 0:
                    stats = {
                        'channel': lbl,
                        'mean_error_ratio': float(np.mean(valid_errors)),
                        'std_error_ratio': float(np.std(valid_errors)),
                        'min_error_ratio': float(np.min(valid_errors)),
                        'max_error_ratio': float(np.max(valid_errors)),
                        'median_error_ratio': float(np.median(valid_errors)),
                        'within_10_percent': float(np.sum(np.abs(valid_errors - 1.0) <= 0.1) / len(valid_errors) * 100),
                        'within_20_percent': float(np.sum(np.abs(valid_errors - 1.0) <= 0.2) / len(valid_errors) * 100)
                    }
                else:
                    stats = {
                        'channel': lbl,
                        'mean_error_ratio': None,
                        'std_error_ratio': None,
                        'min_error_ratio': None,
                        'max_error_ratio': None,
                        'median_error_ratio': None,
                        'within_10_percent': None,
                        'within_20_percent': None
                    }
                error_data['statistics'].append(stats)

            # 保存误差数据
            error_data_path = self.output_path / 'numerics' / 'error_analysis.json'
            error_data_path.parent.mkdir(exist_ok=True)
            with open(error_data_path, 'w', encoding='utf-8') as f:
                json.dump(error_data, f, indent=2, ensure_ascii=False)
            logger.info(f"误差分析数据已保存: {error_data_path}")
        else:
            fig, ax = plt.subplots(figsize=(10, 6))
            for i, (m, lbl) in enumerate(zip(mag_list, output_labels)):
                ax.semilogx(frequencies, m, color=colors[i], linewidth=1.4, label=lbl)
            ax.set_title(f'{self.model_project_name} Dense#{analysis_layer} 输出 频率响应 (理论, 线性增益)')
            ax.set_xlabel('频率 (Hz)')
            ax.set_ylabel('增益 (线性, log刻度)')
            ax.set_yscale('log')
            ax.grid(True, which='both', alpha=0.3)
            all_vals = np.concatenate(mag_list)
            y_min, y_max = float(np.nanmin(all_vals)), float(np.nanmax(all_vals))
            pad = 0.05
            y_min_adj = max(1e-20, y_min / (1+pad))
            y_max_adj = y_max * (1+pad)
            ax.set_ylim(y_min_adj, y_max_adj)
            ax.legend(fontsize=8, ncol=min(4, len(output_labels)))
            plt.tight_layout()
            plot_path = self.output_path / 'plots' / 'frequency_response.png'
            plt.savefig(plot_path, dpi=300)
            plt.close(fig)
            plots.append(str(plot_path))
            logger.info(f"理论图已保存: {plot_path}")

        return plots

    def _generate_plots_multi_file(self, freq_response, dense_weights):
        """多文件对比模式（C05新增）

        特性：
        - 从目录扫描对应层的所有通道文件
        - 使用自测试数据进行补偿
        - loglog 坐标系
        - dB 单位
        - 上下布局：上图实验，下图仿真
        """
        logger.info("使用多文件对比模式（C05）...")

        analysis_layer = dense_weights.get('analysis_layer', 1)

        # ========== 1. 准备理论数据 ==========
        theo_freq = freq_response['frequencies']
        theo_mag_db_list = freq_response['magnitude_db']  # 已经是dB
        n_channels = len(theo_mag_db_list)

        output_labels = [f'D{analysis_layer}_{i+1}' for i in range(n_channels)]

        logger.info(f"理论数据: {n_channels} 个通道, {len(theo_freq)} 个频点")

        # ========== 2. 加载自测试数据 ==========
        selftest_data = None
        try:
            selftest_data = self._load_selftest_data()
        except Exception as e:
            logger.error(f"加载自测试数据失败: {e}")
            logger.warning("将跳过实验对比，仅绘制理论曲线")

        # ========== 3. 扫描并加载实验数据 ==========
        exp_data_dict = {}  # {通道号: {'frequencies': [...], 'magnitude_db': [...]}}

        if selftest_data is not None:
            try:
                channel_files = self._scan_experiment_files(analysis_layer)

                if not channel_files:
                    logger.warning(f"未找到层{analysis_layer}的实验数据，将跳过实验对比")
                else:
                    # 逐个加载通道数据
                    for channel, file_path in channel_files.items():
                        try:
                            # 加载原始数据
                            raw_data = self._load_experiment_channel_data(file_path)

                            # 自测试补偿
                            compensated_mag = self._compensate_with_selftest(
                                raw_data['frequencies'],
                                raw_data['magnitude'],
                                selftest_data
                            )

                            # 转换为dB
                            compensated_db = 20 * np.log10(compensated_mag + 1e-20)

                            exp_data_dict[channel] = {
                                'frequencies': raw_data['frequencies'],
                                'magnitude_db': compensated_db
                            }

                            logger.info(f"   ✅ 通道{channel}: {len(raw_data['frequencies'])} 个频点")

                        except Exception as e:
                            logger.error(f"   ❌ 通道{channel} 加载失败: {e}")
                            continue

                    logger.info(f"✅ 成功加载 {len(exp_data_dict)} 个通道的实验数据")

            except Exception as e:
                logger.error(f"扫描实验数据失败: {e}")
                exp_data_dict = {}

        # ========== 4. 绘制对比图 ==========
        import matplotlib as mpl

        # 颜色映射
        cmap = mpl.cm.get_cmap('tab10', n_channels) if n_channels <= 10 else mpl.cm.get_cmap('turbo', n_channels)
        colors = [cmap(i) for i in range(n_channels)]

        plots = []

        if exp_data_dict:
            # 有实验数据：上下布局
            fig, (ax_exp, ax_theo) = plt.subplots(2, 1, figsize=(12, 10))

            # ===== 上图：实验数据 =====
            for channel, data in sorted(exp_data_dict.items()):
                color_idx = channel - 1
                if color_idx >= n_channels:
                    color_idx = n_channels - 1

                ax_exp.loglog(
                    data['frequencies'],
                    np.power(10, data['magnitude_db'] / 20),  # dB转回线性用于loglog
                    color=colors[color_idx],
                    linewidth=1.5,
                    label=f'D{analysis_layer}_{channel}',
                    alpha=0.8
                )

            ax_exp.set_title(
                f'{self.model_project_name} Dense#{analysis_layer} - 实验测量（补偿后）',
                fontsize=12,
                fontweight='bold'
            )
            ax_exp.set_xlabel('频率 (Hz)', fontsize=10)
            ax_exp.set_ylabel('幅度 (线性, loglog)', fontsize=10)
            ax_exp.grid(True, which='both', alpha=0.3, linestyle='--')
            ax_exp.legend(fontsize=8, ncol=min(3, n_channels), loc='best')

            # ===== 下图：理论数据 =====
            for i, (mag_db, lbl) in enumerate(zip(theo_mag_db_list, output_labels)):
                ax_theo.loglog(
                    theo_freq,
                    np.power(10, mag_db / 20),  # dB转回线性用于loglog
                    color=colors[i],
                    linewidth=1.5,
                    label=lbl,
                    alpha=0.8
                )

            ax_theo.set_title(
                f'{self.model_project_name} Dense#{analysis_layer} - 理论仿真',
                fontsize=12,
                fontweight='bold'
            )
            ax_theo.set_xlabel('频率 (Hz)', fontsize=10)
            ax_theo.set_ylabel('幅度 (线性, loglog)', fontsize=10)
            ax_theo.grid(True, which='both', alpha=0.3, linestyle='--')
            ax_theo.legend(fontsize=8, ncol=min(3, n_channels), loc='best')

            # 统一y轴范围（可选）
            all_exp_mag = np.concatenate([
                np.power(10, d['magnitude_db'] / 20) for d in exp_data_dict.values()
            ])
            all_theo_mag = np.concatenate([
                np.power(10, m / 20) for m in theo_mag_db_list
            ])
            all_mag = np.concatenate([all_exp_mag, all_theo_mag])

            y_min = max(1e-6, np.nanmin(all_mag) * 0.5)
            y_max = np.nanmax(all_mag) * 2.0

            ax_exp.set_ylim(y_min, y_max)
            ax_theo.set_ylim(y_min, y_max)

            plt.tight_layout()

            plot_path = self.output_path / 'plots' / 'frequency_response_comparison_multi.png'
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close(fig)

            plots.append(str(plot_path))
            logger.info(f"📊 对比图已保存: {plot_path}")

        else:
            # 无实验数据：仅绘制理论曲线
            logger.warning("⚠️ 无实验数据，仅绘制理论曲线")

            fig, ax = plt.subplots(figsize=(10, 6))

            for i, (mag_db, lbl) in enumerate(zip(theo_mag_db_list, output_labels)):
                ax.loglog(
                    theo_freq,
                    np.power(10, mag_db / 20),
                    color=colors[i],
                    linewidth=1.5,
                    label=lbl
                )

            ax.set_title(f'{self.model_project_name} Dense#{analysis_layer} - 理论仿真', fontsize=12)
            ax.set_xlabel('频率 (Hz)', fontsize=10)
            ax.set_ylabel('幅度 (线性, loglog)', fontsize=10)
            ax.grid(True, which='both', alpha=0.3)
            ax.legend(fontsize=8, ncol=min(3, n_channels))

            plt.tight_layout()

            plot_path = self.output_path / 'plots' / 'frequency_response.png'
            plt.savefig(plot_path, dpi=300)
            plt.close(fig)

            plots.append(str(plot_path))
            logger.info(f"📊 理论图已保存: {plot_path}")

        return plots

    def _generate_e96_frequency_response_comparison(self, freq_response, dense_weights, quantization_comparison):
        """生成 E96 量化前后的频率响应对比图（与 frequency_response_comparison_merged.png 相同风格）

        对比内容：原始权重 vs 带 E96 量化误差的权重
        风格：合并模式 - 单图显示，原始权重用虚线，E96量化用实线

        Args:
            freq_response: 原始权重的频率响应
            dense_weights: 原始权重数据
            quantization_comparison: E96量化对比数据

        Returns:
            str: 生成的图片路径，如果未启用E96量化则返回None
        """
        if not quantization_comparison:
            logger.info("未启用E96量化对比，跳过频率响应对比图生成")
            return None

        logger.info("生成 E96 量化前后频率响应对比图...")

        try:
            # 1. 提取原始权重和E96量化权重
            original_weights = dense_weights['weights']  # (n_inputs, n_outputs)
            weight_error = quantization_comparison.get('weight_error', {})

            # 构建 E96 量化后的权重矩阵
            weight_e96_matrix = np.zeros_like(original_weights, dtype=np.float64)
            for key, error_data in weight_error.items():
                parts = key.split('_')
                if len(parts) >= 6:
                    try:
                        layer = int(parts[1])  # 输入通道索引
                        channel = int(parts[3])  # 输出通道索引
                        r_type = parts[5]

                        # 只处理 pos 和 neg 类型
                        if r_type not in ['pos', 'neg']:
                            continue

                        if layer < original_weights.shape[0] and channel < original_weights.shape[1]:
                            w_e96 = error_data.get('weight_e96', original_weights[layer, channel])
                            weight_e96_matrix[layer, channel] = w_e96
                    except (ValueError, IndexError):
                        continue

            # 2. 计算 E96 量化权重的频率响应
            # 使用与原始相同的 SVF 参数，但使用新的权重矩阵
            dense_weights_e96 = {
                'weights': weight_e96_matrix,
                'bias': dense_weights['bias'],
                'layer_name': dense_weights.get('layer_name', f'layer{self.analysis_layer}_e96'),
                'analysis_layer': dense_weights.get('analysis_layer', 1)
            }

            # 加载 SVF 参数
            svf_params = self._load_svf_parameters_from_project()

            # 计算传递函数
            svf_tfs = self._calculate_svf_transfer_functions(svf_params)
            combined_tfs_e96 = self._calculate_combined_transfer_functions(svf_tfs, dense_weights_e96)

            # 计算频率响应
            freq_response_e96 = self._calculate_frequency_response(combined_tfs_e96)

            # 3. 绘制对比图（与 merged_plot_mode 相同风格）
            frequencies = freq_response['frequencies']
            mag_list_original = [np.clip(np.power(10.0, m/20.0), 1e-20, None)
                                 for m in freq_response['magnitude_db']]
            mag_list_e96 = [np.clip(np.power(10.0, m/20.0), 1e-20, None)
                           for m in freq_response_e96['magnitude_db']]

            analysis_layer = dense_weights.get('analysis_layer', 1)
            output_labels = [f'D{analysis_layer}_{i+1}' for i in range(len(mag_list_original))]

            # 颜色映射
            import matplotlib as mpl
            n_channels = len(mag_list_original)
            cmap = mpl.cm.get_cmap('tab10', n_channels) if n_channels <= 10 else mpl.cm.get_cmap('turbo', n_channels)
            colors = [cmap(i) for i in range(n_channels)]

            # 创建对比图（与 frequency_response_comparison_merged.png 相同风格）
            fig, ax = plt.subplots(figsize=(12, 4))

            # 绘制原始权重频率响应（虚线）
            for i, (m, lbl) in enumerate(zip(mag_list_original, output_labels)):
                ax.semilogx(frequencies, m, color=colors[i], linewidth=1.4,
                           linestyle='--', label=f'{lbl} (原始)', alpha=0.8)

            # 绘制 E96 量化后频率响应（实线）
            for i, (m, lbl) in enumerate(zip(mag_list_e96, output_labels)):
                ax.semilogx(frequencies, m, color=colors[i], linewidth=1.8,
                           linestyle='-', label=f'{lbl} (E96量化)', alpha=0.9)

            ax.set_title(f'{self.model_project_name} Dense#{analysis_layer} E96量化前后频率响应对比\n(虚线=原始权重, 实线=E96量化权重)', fontsize=12, fontweight='bold')
            ax.set_xlabel('频率 (Hz)', fontsize=10)
            ax.set_ylabel('增益 (线性, log刻度)', fontsize=10)
            ax.set_yscale('log')
            ax.grid(True, which='both', alpha=0.3)

            # 设置y轴范围
            all_vals = np.concatenate([*mag_list_original, *mag_list_e96])
            y_min, y_max = float(np.nanmin(all_vals)), float(np.nanmax(all_vals))
            pad = 0.05
            y_min_adj = max(1e-20, y_min / (1+pad))
            y_max_adj = y_max * (1+pad)
            ax.set_ylim(y_min_adj, y_max_adj)

            # 图例：分开原始和E96量化
            ax.legend(fontsize=8, ncol=min(4, len(output_labels)*2), loc='best')
            plt.tight_layout()

            # 保存图片
            plot_path = self.output_path / 'plots' / 'frequency_response_e96_comparison.png'
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close(fig)

            logger.info(f"E96量化前后频率响应对比图已保存: {plot_path}")

            # 4. 计算并保存误差分析数据
            from scipy import interpolate
            error_data = {
                'frequencies': frequencies.tolist(),
                'error_ratios': [],
                'statistics': []
            }

            for i, (mag_orig, mag_e96, lbl) in enumerate(zip(mag_list_original, mag_list_e96, output_labels)):
                # 计算误差比值：E96量化 / 原始
                with np.errstate(divide='ignore', invalid='ignore'):
                    error_ratio = np.where(np.abs(mag_orig) > 1e-20, mag_e96 / mag_orig, np.nan)
                    error_ratio = np.where(np.abs(mag_orig) < 1e-20, 1.0, error_ratio)

                error_data['error_ratios'].append({
                    'channel': lbl,
                    'ratios': error_ratio.tolist()
                })

                # 计算误差统计
                valid_errors = error_ratio[~np.isnan(error_ratio)]
                if len(valid_errors) > 0:
                    stats = {
                        'channel': lbl,
                        'mean_error_ratio': float(np.mean(valid_errors)),
                        'std_error_ratio': float(np.std(valid_errors)),
                        'min_error_ratio': float(np.min(valid_errors)),
                        'max_error_ratio': float(np.max(valid_errors)),
                        'median_error_ratio': float(np.median(valid_errors)),
                        'mean_abs_error_percent': float(np.mean(np.abs(valid_errors - 1.0) * 100)),
                        'max_abs_error_percent': float(np.max(np.abs(valid_errors - 1.0) * 100)),
                        'within_0_1pct': float(np.sum(np.abs(valid_errors - 1.0) <= 0.001) / len(valid_errors) * 100),
                        'within_0_5pct': float(np.sum(np.abs(valid_errors - 1.0) <= 0.005) / len(valid_errors) * 100),
                        'within_1pct': float(np.sum(np.abs(valid_errors - 1.0) <= 0.01) / len(valid_errors) * 100),
                        'within_2pct': float(np.sum(np.abs(valid_errors - 1.0) <= 0.02) / len(valid_errors) * 100)
                    }
                else:
                    stats = {
                        'channel': lbl,
                        'mean_error_ratio': None,
                        'std_error_ratio': None,
                        'min_error_ratio': None,
                        'max_error_ratio': None,
                        'median_error_ratio': None,
                        'mean_abs_error_percent': None,
                        'max_abs_error_percent': None,
                        'within_0_1pct': None,
                        'within_0_5pct': None,
                        'within_1pct': None,
                        'within_2pct': None
                    }
                error_data['statistics'].append(stats)

            # 保存误差数据
            error_data_path = self.output_path / 'numerics' / 'e96_error_analysis.json'
            error_data_path.parent.mkdir(exist_ok=True)
            with open(error_data_path, 'w', encoding='utf-8') as f:
                json.dump(error_data, f, indent=2, ensure_ascii=False)
            logger.info(f"E96量化误差分析数据已保存: {error_data_path}")

            return str(plot_path)

        except Exception as e:
            logger.error(f"生成E96频率响应对比图失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _generate_analysis_report(self, svf_params, dense_weights, freq_response):
        """生成分析报告"""
        logger.info("生成分析报告...")
        
        mag_concat = np.concatenate(freq_response['magnitude_db'], axis=0)
        phase_concat = np.concatenate(freq_response['phase_deg'], axis=0)
        report = {
            'project_name': self.model_project_name,
            'analysis_type': 'wnet5-circuit-validation',
            'analysis_layer': dense_weights.get('analysis_layer', 1),
            'svf_parameters': svf_params,
            'dense_layer': {
                'name': dense_weights['layer_name'],
                'analysis_layer_index': dense_weights.get('analysis_layer', 1),
                'weight_shape': list(dense_weights['weights'].shape),
                'bias_shape': list(dense_weights['bias'].shape)
            },
            'frequency_range': self.frequency_range,
            'outputs': len(freq_response['magnitude_db']),
            'analysis_results': {
                'frequency_points': len(freq_response['frequencies']),
                'magnitude_range_db': [float(mag_concat.min()), float(mag_concat.max())],
                'phase_range_deg': [float(phase_concat.min()), float(phase_concat.max())]
            }
        }
        
        # 保存报告
        report_path = self.output_path / "reports" / "analysis_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"分析报告已保存: {report_path}")
        return str(report_path)
    
    def _save_results(self, svf_params, svf_tfs, combined_tfs, freq_response, dense_weights, plots, report, quantization_comparison=None):
        """保存计算结果 (合并为单一 results.json)"""
        logger.info("保存计算结果 (results.json)...")
        
        # 保存频率响应数据
        numerics_dir = self.output_path / 'numerics'
        import sympy as sp
        s = sp.Symbol('s')

        # 构建SVF传递函数结构与系数
        svf_transfer = []
        for entry in svf_tfs:
            channels = {}
            for cname in ['high_pass', 'band_pass', 'low_pass']:
                Hsym = entry[cname]
                try:
                    num_poly, den_poly = sp.together(Hsym).as_numer_denom()
                    num_poly = sp.Poly(num_poly, s)
                    den_poly = sp.Poly(den_poly, s)
                    num_coeff = [float(c) for c in num_poly.all_coeffs()]
                    den_coeff = [float(c) for c in den_poly.all_coeffs()]
                    if den_coeff and den_coeff[0] != 0:
                        lead = den_coeff[0]
                        num_coeff = [c/lead for c in num_coeff]
                        den_coeff = [c/lead for c in den_coeff]
                except Exception as e:
                    logger.error(f"SVF通道 {cname} 系数提取失败: {e}")
                    num_coeff, den_coeff = [], []
                channels[cname] = {
                    'symbolic': str(Hsym),
                    'numerator_coeffs': num_coeff,
                    'denominator_coeffs': den_coeff
                }
            svf_transfer.append({'f0': entry['f0'], 'Q': entry['Q'], 'channels': channels})

        # 组合传递函数
        combined_serialized = []
        for idx, Hsym in enumerate(combined_tfs):
            try:
                num_poly, den_poly = sp.together(Hsym).as_numer_denom()
                num_poly = sp.Poly(num_poly, s)
                den_poly = sp.Poly(den_poly, s)
                num_coeff = [float(c) for c in num_poly.all_coeffs()]
                den_coeff = [float(c) for c in den_poly.all_coeffs()]
                if den_coeff and den_coeff[0] != 0:
                    lead = den_coeff[0]
                    num_coeff = [c/lead for c in num_coeff]
                    den_coeff = [c/lead for c in den_coeff]
            except Exception as e:
                logger.error(f"组合传递函数 out{idx} 系数提取失败: {e}")
                num_coeff, den_coeff = [], []
            combined_serialized.append({
                'output_index': idx,
                'symbolic': str(Hsym),
                'numerator_coeffs': num_coeff,
                'denominator_coeffs': den_coeff
            })

        # 频率响应
        fr = {
            'frequencies': freq_response['frequencies'].tolist(),
            'outputs': [
                {
                    'index': i,
                    'magnitude_db': m.tolist(),
                    'phase_deg': p.tolist()
                } for i, (m, p) in enumerate(zip(freq_response['magnitude_db'], freq_response['phase_deg']))
            ]
        }

        # Dense 权重
        dw = dense_weights
        dense_block = {
            'layer_name': dw.get('layer_name'),
            'weights': self._to_list_2d(dw['weights']),
            'bias': [float(x) for x in dw['bias'].tolist()]
        }

        # 相对路径（相对 output_path）
        plots_rel = [str(Path(p).relative_to(self.output_path)) for p in plots]
        report_rel = str(Path(report).relative_to(self.output_path)) if report else None

        results = {
            'project_name': self.model_project_name,
            'task_type': 'wnet5-circuit-validation',
            'analysis_layer': self.analysis_layer,
            'frequency_range': self.frequency_range,
            'svf': {
                'center_freqs': svf_params['center_freqs'],
                'quality_factors': svf_params['quality_factors'],
                'transfer_functions': svf_transfer
            },
            'dense_layer': dense_block,
            'combined_transfer_functions': combined_serialized,
            'frequency_response': fr,
            'artifacts': {
                'plots': plots_rel,
                'report': report_rel
            }
        }

        # 如果存在误差分析数据，添加到结果中
        error_data_path = self.output_path / 'numerics' / 'error_analysis.json'
        if error_data_path.exists():
            with open(error_data_path, 'r', encoding='utf-8') as f:
                error_data = json.load(f)
            results['error_analysis'] = error_data
            logger.info("误差分析数据已添加到results.json")

        # 如果存在E96量化对比数据，添加到结果中
        if quantization_comparison:
            # 转换numpy类型为Python原生类型，解决JSON序列化问题
            results['quantization_comparison'] = _convert_to_native_types(quantization_comparison)
            logger.info(f"E96量化对比数据已添加到results.json (统计: {quantization_comparison.get('statistics', {}).get('total_count', 0)} 个电阻)")

        results_path = self.output_path / 'results.json'
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        logger.info(f"结果已保存: {results_path.relative_to(self.output_path)}")

        # 如果存在E96量化对比数据，自动生成可视化图表
        if quantization_comparison:
            self._generate_e96_quantization_plots(quantization_comparison)

    def _generate_e96_quantization_plots(self, quantization_comparison: Dict[str, Any]):
        """生成E96量化对比可视化图表

        Args:
            quantization_comparison: E96量化对比数据字典
        """
        try:
            # 创建E96量化分析输出目录
            e96_output_dir = self.output_path / 'plots' / 'e96_quantization'
            e96_output_dir.mkdir(parents=True, exist_ok=True)

            # 直接使用spec从文件导入
            from importlib.machinery import SourceFileLoader

            # 加载可视化工具模块 - 修复路径
            base_dir = Path(__file__).resolve().parent.parent  # 到项目根目录
            plotter_file = base_dir / 'inference' / 'tools' / 'visualization' / 'weight_e96_quantization_plotter.py'
            if not plotter_file.exists():
                logger.warning(f"E96可视化工具文件不存在: {plotter_file}")
                return

            # 动态加载模块
            plotter_module = SourceFileLoader('weight_e96_quantization_plotter', str(plotter_file)).load_module()
            WeightE96QuantizationPlotter = plotter_module.WeightE96QuantizationPlotter

            # 生成可视化图表
            plotter = WeightE96QuantizationPlotter({'output_dir': str(e96_output_dir)})
            files = plotter.plot_quantization_comparison(quantization_comparison, str(e96_output_dir))

            # 记录生成的文件
            if files:
                logger.info(f"E96量化对比可视化已生成:")
                for name, path in files.items():
                    rel_path = Path(path).relative_to(self.output_path)
                    logger.info(f"  - {name}: {rel_path}")
            else:
                logger.warning("E96量化对比可视化未生成（可能无有效数据）")

        except Exception as e:
            logger.error(f"生成E96量化可视化失败: {e}")