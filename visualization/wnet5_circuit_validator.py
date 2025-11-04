"""
WNET5电路验证可视化引擎

基于传递函数理论计算WNET5电路的频率响应，并与实测数据对比
"""

import numpy as np
import matplotlib.pyplot as plt
import json
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


class WNET5CircuitValidator:
    """WNET5电路验证器"""
    
    def __init__(self, config: Dict[str, Any], output_path: Path):
        self.config = config
        self.output_path = Path(output_path)
        self.model_project_name = config['model_project_name']
        self.frequency_range = config['frequency_range']
        # 可选: 实验对比数据 (Excel)
        self.experiment_path = config.get('compare_with_experiment')
        # 新增：指定要分析的Dense层编号（默认为1，向后兼容）
        self.analysis_layer = config.get('analysis_layer', 1)

        # 确保输出目录存在
        self._setup_output_directories()
        
    def _setup_output_directories(self):
        """设置输出目录结构"""
        self.output_path.mkdir(parents=True, exist_ok=True)
        (self.output_path / "plots").mkdir(exist_ok=True)
        # 使用 numerics 存放数值结果，避免出现 data\\data 的嵌套
        (self.output_path / "numerics").mkdir(exist_ok=True)
        (self.output_path / "reports").mkdir(exist_ok=True)

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
            
            # 1. 加载模型和提取参数
            model = self._load_model()
            svf_params = self._extract_svf_parameters(model)
            dense_weights = self._extract_dense_weights(model, self.analysis_layer)
            
            # 2. 计算传递函数
            svf_tfs = self._calculate_svf_transfer_functions(svf_params)
            combined_tfs = self._calculate_combined_transfer_functions(svf_tfs, dense_weights)
            
            # 3. 计算频率响应
            freq_response = self._calculate_frequency_response(combined_tfs)

            # 4. 生成可视化
            plots = self._generate_plots(freq_response, dense_weights)
            
            # 5. 生成报告
            report = self._generate_analysis_report(svf_params, dense_weights, freq_response)
            
            # 6. 保存结果 (单一 results.json)
            self._save_results(svf_params, svf_tfs, combined_tfs, freq_response, dense_weights, plots, report)
            
            logger.info("✅ WNET5电路验证分析完成")
            return True
            
        except Exception as e:
            logger.error(f"WNET5电路验证分析失败: {e}")
            return False
    
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
    
    def _calculate_combined_transfer_functions(self, svf_tfs, dense_weights):
        """计算SVF+Dense组合传递函数"""
        logger.info("计算组合传递函数...")
        import sympy as sp

        # 展开所有SVF通道 (顺序: 每个滤波器 HP,BP,LP)
        all_svf_channels = []
        for svf in svf_tfs:
            all_svf_channels.extend([svf['high_pass'], svf['band_pass'], svf['low_pass']])

        n_inputs = len(all_svf_channels)
        w = dense_weights['weights']  # (in_ch, out_ch)
        if w.shape[0] != n_inputs:
            raise ValueError(f"权重输入通道数 {w.shape[0]} 与SVF展开通道数 {n_inputs} 不匹配")

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
        """生成幅频响应图 (线性增益对数刻度, 支持实验对比)"""
        logger.info("生成幅频响应图 (线性增益, 对比模式)...")

        # 1. 理论幅度 (内部存储为 dB, 转线性)
        frequencies = freq_response['frequencies']
        mag_db_list = freq_response['magnitude_db']
        mag_list = [np.clip(np.power(10.0, m/20.0), 1e-20, None) for m in mag_db_list]
        # 根据当前分析的层生成标签
        analysis_layer = dense_weights.get('analysis_layer', 1)
        output_labels = [f'D{analysis_layer}_{i+1}' for i in range(len(mag_list))]

        # 2. 读取实验数据 (列名形式 D{layer}_[N]_GAIN/B1)
        exp_freq = None
        exp_mags = None
        if self.experiment_path:
            try:
                import pandas as pd, re
                exp_file = Path(self.experiment_path)
                if exp_file.exists():
                    df = pd.read_excel(exp_file)
                    freq_cols = [c for c in df.columns if str(c).strip().lower() in ['f','freq','frequency','freq(hz)','frequency(hz)','hz']]
                    fcol = freq_cols[0] if freq_cols else df.columns[0]
                    exp_freq = df[fcol].to_numpy(dtype=float)
                    # 动态匹配当前分析的层
                    pattern = re.compile(rf'^D{analysis_layer}_(\d+)_GAIN/B1$')
                    matched = {}
                    for c in df.columns:
                        if c == fcol:
                            continue
                        m = pattern.match(str(c).strip())
                        if not m:
                            continue
                        idx = int(m.group(1))
                        try:
                            arr = df[c].astype(float).to_numpy(dtype=float)
                        except Exception:
                            continue
                        matched[idx] = arr
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
    
    def _save_results(self, svf_params, svf_tfs, combined_tfs, freq_response, dense_weights, plots, report):
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

        results_path = self.output_path / 'results.json'
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        logger.info(f"结果已保存: {results_path.relative_to(self.output_path)}")