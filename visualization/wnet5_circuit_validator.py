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


def _expand_env_vars(path: str) -> str:
    """展开路径中的环境变量，支持 ${VAR_NAME} 和 $VAR_NAME 格式"""
    if not path:
        return path
    expanded = os.path.expandvars(path)
    return Path(expanded).as_posix() if '/' in expanded or '\\' in expanded else expanded


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
        # 支持环境变量替换，如 ${MET_DATA_BASE}/data/xxx.xlsx
        self.experiment_path = _expand_env_vars(config.get('compare_with_experiment'))

        # ⬇️⬇️⬇️ 新增：实验对比配置（C05） ⬇️⬇️⬇️
        self.experiment_comparison = config.get('experiment_comparison', {})
        self.exp_comp_enable = self.experiment_comparison.get('enable', False)
        self.exp_comp_mode = self.experiment_comparison.get('mode', 'single_file')
        # 支持环境变量替换
        self.exp_data_dir = _expand_env_vars(self.experiment_comparison.get('experiment_data_dir'))
        self.selftest_file = _expand_env_vars(self.experiment_comparison.get('selftest_file'))
        self.plot_config = self.experiment_comparison.get('plot_config', {})
        # ⬆️⬆️⬆️ 新增结束 ⬆️⬆️⬆️

        # 新增：指定要分析的Dense层编号（默认为1，向后兼容）
        self.analysis_layer = config.get('analysis_layer', 1)

        # 新增：推理配置（用于E96量化等）
        self.inference_config = config.get('inference_config', {})

        # 新增：SVF层误差仿真配置（R3实现）
        self.svf_error_config = config.get('svf_error_simulation', {})
        self.svf_error_enable = self.svf_error_config.get('enable', False)
        self.svf_measured_file = _expand_env_vars(
            self.svf_error_config.get('measured_data_file')
        )
        self.svf_compensation_config = self.svf_error_config.get('compensation', {})
        self.svf_compensation_enabled = self.svf_compensation_config.get('enabled', False)
        self.svf_selftest_file = _expand_env_vars(
            self.svf_compensation_config.get('selftest_file')
        )

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

    def _load_svf_measured_data(self) -> Dict[str, Any]:
        """加载SVF层实测频率响应数据（R3新增）

        Returns:
            Dict: {
                'frequencies': np.ndarray,
                'magnitude': List[np.ndarray]  # 6个通道
            }
        """
        if not self.svf_measured_file:
            raise ValueError("未配置SVF实测数据文件路径 (measured_data_file)")

        import pandas as pd

        # 尝试多种路径解析方式
        file_path = Path(self.svf_measured_file)

        # 如果是相对路径，尝试相对于项目根目录解析
        if not file_path.is_absolute():
            # 尝试相对于当前工作目录
            if file_path.exists():
                pass  # 使用当前路径
            else:
                # 尝试相对于项目根目录 (met_nonlinear_master)
                project_root = Path.cwd()
                absolute_path = project_root / self.svf_measured_file
                if absolute_path.exists():
                    file_path = absolute_path
                else:
                    # 尝试相对于配置文件位置 (如果有)
                        # 遍历可能的配置目录
                    for parent in [Path.cwd() / 'ex_projects' / 'inference',
                                   Path.cwd() / 'ex_projects',
                                   Path.cwd()]:
                        test_path = parent / self.svf_measured_file
                        if test_path.exists():
                            file_path = test_path
                            break

        if not file_path.exists():
            raise FileNotFoundError(f"SVF实测数据文件不存在: {file_path} (尝试过: {self.svf_measured_file})")

        logger.info(f"加载SVF实测数据: {file_path}")

        try:
            df = pd.read_excel(file_path)

            # 解析频率列
            freq_cols = [c for c in df.columns if str(c).strip().lower() in [
                'freq', 'f', 'frequency', 'freq(hz)', 'frequency(hz)', 'hz'
            ]]
            if not freq_cols:
                raise ValueError(f"文件中未找到频率列: {df.columns.tolist()}")

            frequencies = df[freq_cols[0]].to_numpy(dtype=float)

            # 解析6个通道数据 (ch1-ch6)
            channels = []
            for i in range(1, 7):
                col_name = f'ch{i}'
                if col_name in df.columns:
                    channel_data = df[col_name].to_numpy(dtype=float)
                    channel_data = np.clip(channel_data, 1e-20, None)
                    channels.append(channel_data)

            # 数据清理
            valid_mask = np.isfinite(frequencies)
            for i, channel_data in enumerate(channels):
                valid_mask = valid_mask & np.isfinite(channel_data)

            frequencies = frequencies[valid_mask]
            for i in range(len(channels)):
                channels[i] = channels[i][valid_mask]

            logger.info(f"✅ SVF实测数据加载成功: {len(frequencies)} 频点 x {len(channels)} 通道")
            logger.info(f"   频率范围: {frequencies.min():.2f} - {frequencies.max():.2f} Hz")

            return {
                'frequencies': frequencies,
                'magnitude': channels
            }

        except Exception as e:
            logger.error(f"加载SVF实测数据失败: {e}")
            raise

    def _calculate_svf_frequency_response_only(self, svf_params: Dict) -> Dict[str, Any]:
        """计算仅SVF层的频率响应（不含Dense层）（R3新增）

        SVF层每个滤波器输出3个通道：HP, BP, LP
        共 n_filters * 3 个输出通道

        Args:
            svf_params: SVF参数字典，包含 center_freqs 和 quality_factors

        Returns:
            Dict: {
                'frequencies': np.ndarray,
                'magnitude_db': List[np.ndarray],
                'phase_deg': List[np.ndarray]
            }
        """
        import sympy as sp
        s = sp.Symbol('s')

        # 使用与实测数据相同的频率点
        if self.svf_measured_file:
            measured_data = self._load_svf_measured_data()
            frequencies = measured_data['frequencies']
        else:
            start_freq = float(self.frequency_range['start_freq'])
            stop_freq = float(self.frequency_range['stop_freq'])
            points = int(self.frequency_range.get('points', 1000))
            frequencies = np.logspace(np.log10(start_freq), np.log10(stop_freq), points)

        omega = 2 * np.pi * frequencies
        s_vals = 1j * omega

        mag_db_all = []
        phase_deg_all = []

        for f0, Q in zip(svf_params['center_freqs'], svf_params['quality_factors']):
            omega0 = 2 * sp.pi * f0
            denominator = s**2 + (omega0/Q)*s + omega0**2

            # LP, BP, HP 传递函数
            H_lp = omega0**2 / denominator
            H_bp = (s * omega0/Q) / denominator
            H_hp = s**2 / denominator

            for H_sym in [H_lp, H_bp, H_hp]:
                try:
                    H_func = sp.lambdify(s, H_sym, 'numpy')
                    H_resp = H_func(s_vals)
                except Exception:
                    H_resp = np.ones_like(s_vals, dtype=complex)

                mag = np.abs(H_resp)
                mag_db_all.append(20 * np.log10(mag + 1e-20))
                phase_deg_all.append(np.degrees(np.angle(H_resp)))

        logger.info(f"✅ SVF层理论频响计算完成: {len(mag_db_all)} 个通道")

        return {
            'frequencies': frequencies,
            'magnitude_db': mag_db_all,
            'phase_deg': phase_deg_all
        }

    def _generate_svf_error_comparison_plot(
        self,
        svf_response: Dict[str, Any],
        measured_data: Dict[str, Any]
    ) -> str:
        """生成SVF误差对比图（R3新增）

        风格与 frequency_response_comparison_merged.png 相同：
        - 单图显示，仿真虚线，实测实线
        - semilogx 坐标系
        - 线性增益

        Args:
            svf_response: SVF理论频率响应
            measured_data: SVF实测数据

        Returns:
            str: 生成的图片路径
        """
        import matplotlib as mpl

        frequencies = svf_response['frequencies']
        sim_mag_db = svf_response['magnitude_db']
        sim_mag = [np.clip(np.power(10.0, m/20.0), 1e-20, None) for m in sim_mag_db]

        exp_freq = measured_data['frequencies']
        exp_mags = measured_data['magnitude']

        # SVF层输出标签: SVF1_LP, SVF1_BP, SVF1_HP, SVF2_LP, ...
        n_filters = len(self._load_svf_parameters_from_project()['center_freqs'])
        output_labels = []
        for i in range(n_filters):
            output_labels.extend([f'SVF{i+1}_LP', f'SVF{i+1}_BP', f'SVF{i+1}_HP'])

        # 颜色映射
        n_channels = len(sim_mag)
        cmap = mpl.cm.get_cmap('tab10', n_channels) if n_channels <= 10 else mpl.cm.get_cmap('turbo', n_channels)
        colors = [cmap(i) for i in range(n_channels)]

        # 创建对比图
        fig, ax = plt.subplots(figsize=(12, 4))

        # 绘制仿真结果（虚线）
        for i, (m, lbl) in enumerate(zip(sim_mag, output_labels)):
            ax.semilogx(frequencies, m, color=colors[i], linewidth=1.4,
                       linestyle='--', label=f'{lbl} (仿真)', alpha=0.8)

        # 绘制实测结果（实线）- 映射到对应的SVF输出
        # SVF_ONLY的ch1-ch6对应: SVF1_HP, SVF1_BP, SVF1_LP, SVF2_HP, SVF2_BP, SVF2_LP
        for i, (m, lbl) in enumerate(zip(exp_mags, output_labels)):
            ax.semilogx(exp_freq, m, color=colors[i], linewidth=1.8,
                       linestyle='-', label=f'{lbl} (实测)', alpha=0.9)

        ax.set_title(f'{self.model_project_name} SVF层频率响应误差仿真对比\n(虚线=仿真, 实线=实测)',
                    fontsize=12, fontweight='bold')
        ax.set_xlabel('频率 (Hz)', fontsize=10)
        ax.set_ylabel('增益 (线性, log刻度)', fontsize=10)
        ax.set_yscale('log')
        ax.grid(True, which='both', alpha=0.3)

        # 设置y轴范围
        all_vals = np.concatenate([*sim_mag, *exp_mags])
        y_min, y_max = float(np.nanmin(all_vals)), float(np.nanmax(all_vals))
        pad = 0.05
        y_min_adj = max(1e-20, y_min / (1+pad))
        y_max_adj = y_max * (1+pad)
        ax.set_ylim(y_min_adj, y_max_adj)

        ax.legend(fontsize=8, ncol=min(4, len(output_labels)*2), loc='best')
        plt.tight_layout()

        output_filename = self.svf_error_config.get('plot_config', {}).get(
            'output_filename', 'svf_error_comparison.png'
        )
        plot_path = self.output_path / 'plots' / output_filename
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close(fig)

        logger.info(f"SVF误差对比图已保存: {plot_path}")
        return str(plot_path)

    def _compensate_svf_with_selftest(
        self,
        measured_data: Dict[str, Any],
        selftest_data: Dict[str, np.ndarray]
    ) -> Dict[str, Any]:
        """使用自测试数据补偿SVF实测数据（R3新增）

        补偿方法：compensated = measured_mag / selftest_mag_interp
        通过插值使自测试数据与测量数据的频点对齐

        Args:
            measured_data: SVF测量数据 {'frequencies', 'magnitude'}
            selftest_data: 自测试数据 {'frequencies', 'magnitude'}

        Returns:
            Dict: 补偿后的测量数据
        """
        from scipy.interpolate import interp1d

        exp_freq = measured_data['frequencies']
        selftest_freq = selftest_data['frequencies']
        selftest_mag = selftest_data['magnitude']

        # 检查频率范围是否覆盖
        exp_min, exp_max = exp_freq.min(), exp_freq.max()
        self_min, self_max = selftest_freq.min(), selftest_freq.max()

        if exp_min < self_min or exp_max > self_max:
            logger.warning(
                f"⚠️ SVF测量数据频率范围 [{exp_min:.2f}, {exp_max:.2f}] Hz "
                f"超出自测试范围 [{self_min:.2f}, {self_max:.2f}] Hz"
            )

        # 使用线性插值（对数空间）
        selftest_db = 20 * np.log10(selftest_mag + 1e-20)

        interp_func = interp1d(
            selftest_freq,
            selftest_db,
            kind='linear',
            bounds_error=False,
            fill_value='extrapolate'
        )

        # 在测量频点处插值
        selftest_db_interp = interp_func(exp_freq)
        selftest_mag_interp = np.power(10.0, selftest_db_interp / 20.0)

        # 执行补偿（相除）
        compensated_channels = []
        for channel_mag in measured_data['magnitude']:
            compensated = channel_mag / (selftest_mag_interp + 1e-20)
            compensated_channels.append(compensated)

        logger.info("✅ SVF自测试补偿完成")

        return {
            'frequencies': exp_freq,
            'magnitude': compensated_channels
        }

    def _calculate_svf_error_statistics(
        self,
        svf_response: Dict[str, Any],
        measured_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """计算SVF误差统计（R3新增）

        计算仿真数据与实测数据的误差比值和统计指标

        Args:
            svf_response: SVF理论频率响应
            measured_data: SVF实测数据

        Returns:
            Dict: 误差统计数据
        """
        from scipy import interpolate

        sim_freq = svf_response['frequencies']
        sim_mag_db = svf_response['magnitude_db']
        sim_mag = [np.power(10.0, m/20.0) for m in sim_mag_db]

        exp_freq = measured_data['frequencies']
        exp_mags = measured_data['magnitude']

        # SVF层输出标签
        n_filters = len(self._load_svf_parameters_from_project()['center_freqs'])
        output_labels = []
        for i in range(n_filters):
            output_labels.extend([f'SVF{i+1}_HP', f'SVF{i+1}_BP', f'SVF{i+1}_LP'])

        error_data = {
            'frequencies': exp_freq.tolist(),
            'error_ratios': [],
            'statistics': []
        }

        for i, (sim_ch, exp_ch, lbl) in enumerate(zip(sim_mag, exp_mags, output_labels)):
            # 将仿真数据插值到实测频率点
            sim_interp = interpolate.interp1d(
                sim_freq, sim_ch, kind='linear',
                bounds_error=False, fill_value=np.nan
            )
            sim_mag_interp = sim_interp(exp_freq)

            # 计算误差比值: sim / exp
            with np.errstate(divide='ignore', invalid='ignore'):
                error_ratio = sim_mag_interp / (exp_ch + 1e-20)
                error_ratio = np.where(np.abs(exp_ch) < 1e-20, np.nan, error_ratio)

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
                    'within_5pct': float(np.sum(np.abs(valid_errors - 1.0) <= 0.05) / len(valid_errors) * 100),
                    'within_10pct': float(np.sum(np.abs(valid_errors - 1.0) <= 0.1) / len(valid_errors) * 100)
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
                    'within_5pct': None,
                    'within_10pct': None
                }
            error_data['statistics'].append(stats)

        return error_data

    def _get_svf_magnitude_response(self, f: np.ndarray, f0: float, Q: float, filter_type: str) -> np.ndarray:
        """计算指定类型SVF滤波器的幅度响应（R10新增，R11修正公式）

        Args:
            f: 频率数组 (Hz)
            f0: 中心频率 (Hz)
            Q: 品质因数
            filter_type: 'HP', 'BP', 或 'LP'

        Returns:
            np.ndarray: 幅度响应（线性）
        """
        omega = 2 * np.pi * f
        omega0 = 2 * np.pi * f0

        # 分母平方: |(omega0^2 - omega^2) + j * (omega0 * omega / Q)|^2
        # = (omega0^2 - omega^2)^2 + (omega0 * omega / Q)^2
        denominator_sq = (omega0**2 - omega**2)**2 + (omega0 * omega / Q)**2

        if filter_type.upper() == 'HP':
            # 高通: |H| = omega^2 / sqrt(...)
            numerator = omega**4
        elif filter_type.upper() == 'BP':
            # 带通: |H| = (omega0 * omega / Q) / sqrt(...)
            numerator = (omega0 * omega / Q)**2
        elif filter_type.upper() == 'LP':
            # 低通: |H| = omega0^2 / sqrt(...)
            numerator = omega0**4
        else:
            raise ValueError(f"未知的滤波器类型: {filter_type}")

        magnitude = np.sqrt(numerator / (denominator_sq + 1e-20))
        return magnitude

    def _fit_svf_parameters(
        self,
        frequencies: np.ndarray,
        measured_magnitudes: List[np.ndarray],
        svf_params: Dict
    ) -> Dict[str, Any]:
        """拟合SVF参数以匹配实测数据（R10新增，R11改进）

        每个SVF滤波器有1个f0和1个Q，但产生3个输出通道（HP, BP, LP）。
        使用联合拟合方法，同时考虑所有3个通道的误差。
        R11改进：添加增益参数，优化初始值。

        Args:
            frequencies: 频率数组 (Hz)
            measured_magnitudes: 实测幅度数据列表（6个通道：HP/BP/LP for 2 filters）
            svf_params: 初始 SVF 参数

        Returns:
            Dict: 拟合结果
        """
        from scipy.optimize import minimize

        center_freqs = svf_params['center_freqs']
        quality_factors = svf_params['quality_factors']
        n_filters = len(center_freqs)

        # 通道标签：SVF1_LP, SVF1_BP, SVF1_HP, SVF2_LP, SVF2_BP, SVF2_HP
        channel_labels = []
        for i in range(n_filters):
            channel_labels.extend([f'SVF{i+1}_LP', f'SVF{i+1}_BP', f'SVF{i+1}_HP'])

        fitted_channels = []
        fitted_center_freqs = []
        fitted_quality_factors = []

        logger.info("开始拟合 SVF 参数 (R11改进：带增益参数)...")

        # 对每个滤波器进行联合拟合（3个通道共享相同的f0和Q，但各有自己的增益）
        for filter_idx in range(n_filters):
            # 获取该滤波器的3个通道数据
            filter_types = ['LP', 'BP', 'HP']
            filter_mags = [
                measured_magnitudes[filter_idx * 3 + i]
                for i in range(3)
            ]

            # 计算每个通道的初始增益（使用低频或高频的平均值）
            gains_init = []
            for mag, t in zip(filter_mags, filter_types):
                if t == 'HP':
                    # HP在高频时增益应该为1
                    high_freq_gain = np.mean(mag[-5:])
                    gains_init.append(high_freq_gain)
                elif t == 'LP':
                    # LP在低频时增益应该为1
                    low_freq_gain = np.mean(mag[:5])
                    gains_init.append(low_freq_gain)
                else:  # BP
                    # BP使用峰值作为初始增益估计
                    gains_init.append(np.max(mag))

            # 初始猜测值（使用理论计算值）
            f0_init = center_freqs[filter_idx]
            Q_init = quality_factors[filter_idx]

            # R11改进：使用有边界的优化器，设置合理的参数范围
            # f0范围: 1Hz - 10000Hz (基于测量频率范围)
            # Q范围: 0.01 - 50 (适当放宽，因为高Q值滤波器需要)
            # 增益范围: 0.001 - 100 (大幅放宽增益边界)
            bounds = [(1.0, 10000.0), (0.01, 50.0)] + [(0.001, 100.0) for _ in range(3)]

            # 联合目标函数：同时考虑3个通道的误差（R11：带增益参数）
            def joint_objective(params, f, mags, types):
                f0, Q = params[0], params[1]
                gains = params[2:]  # 每个通道的增益
                total_error = 0.0
                for i, (mag, t, gain) in enumerate(zip(mags, types, gains)):
                    model = self._get_svf_magnitude_response(f, f0, Q, t)
                    # 应用增益
                    model = model * gain
                    total_error += np.sum((model - mag)**2)
                return total_error

            # 初始参数：[f0, Q, gain_HP, gain_BP, gain_LP]
            x0 = [f0_init, Q_init] + gains_init

            # 使用 L-BFGS-B 优化器（有边界约束）
            result = minimize(
                joint_objective,
                x0=x0,
                args=(frequencies, filter_mags, filter_types),
                method='L-BFGS-B',
                bounds=bounds,
                options={'maxiter': 2000, 'ftol': 1e-10}
            )

            f0_fitted, Q_fitted = result.x[0], result.x[1]
            gains_fitted = result.x[2:]

            # 计算每个通道的拟合质量
            for i, (filter_type, meas_mag, gain) in enumerate(zip(filter_types, filter_mags, gains_fitted)):
                ch_idx = filter_idx * 3 + i
                label = channel_labels[ch_idx]

                fitted_mag = self._get_svf_magnitude_response(frequencies, f0_fitted, Q_fitted, filter_type) * gain
                rmse = np.sqrt(np.mean((fitted_mag - meas_mag)**2))

                # R² 计算
                ss_res = np.sum((meas_mag - fitted_mag)**2)
                ss_tot = np.sum((meas_mag - np.mean(meas_mag))**2)
                r2 = 1 - (ss_res / (ss_tot + 1e-20))

                fitted_channels.append({
                    'channel': label,
                    'f0': float(f0_fitted),
                    'Q': float(Q_fitted),
                    'gain': float(gain),
                    'rmse': float(rmse),
                    'r2': float(r2)
                })

                logger.info(f"  {label}: f0={f0_fitted:.2f}Hz, Q={Q_fitted:.4f}, gain={gain:.4f}, RMSE={rmse:.6f}, R²={r2:.4f}")

            fitted_center_freqs.append(float(f0_fitted))
            fitted_quality_factors.append(float(Q_fitted))

        # 计算整体拟合质量
        all_rmse = np.mean([ch['rmse'] for ch in fitted_channels])
        all_r2 = np.mean([ch['r2'] for ch in fitted_channels])

        logger.info(f"拟合完成: 平均RMSE={all_rmse:.6f}, 平均R²={all_r2:.4f}")

        return {
            'fitted_params': {
                'center_freqs': fitted_center_freqs,
                'quality_factors': fitted_quality_factors
            },
            'fitted_channels': fitted_channels,
            'fit_quality': {
                'overall_rmse': float(all_rmse),
                'overall_r2': float(all_r2)
            }
        }

    def _calculate_fitted_magnitudes(
        self,
        frequencies: np.ndarray,
        fitted_params: Dict[str, Any]
    ) -> List[np.ndarray]:
        """使用拟合参数计算各通道的幅度响应（R10新增，R11改进：带增益）

        Args:
            frequencies: 频率数组
            fitted_params: 拟合参数（包含fitted_channels中的gain）

        Returns:
            List[np.ndarray]: 各通道的幅度响应
        """
        center_freqs = fitted_params['fitted_params']['center_freqs']
        quality_factors = fitted_params['fitted_params']['quality_factors']
        fitted_channels = fitted_params['fitted_channels']
        n_filters = len(center_freqs)

        magnitudes = []
        channel_idx = 0
        for filter_idx in range(n_filters):
            f0 = center_freqs[filter_idx]
            Q = quality_factors[filter_idx]

            for filter_type in ['LP', 'BP', 'HP']:
                # R11改进：获取通道的增益参数
                gain = fitted_channels[channel_idx].get('gain', 1.0)
                mag = self._get_svf_magnitude_response(frequencies, f0, Q, filter_type) * gain
                magnitudes.append(mag)
                channel_idx += 1

        return magnitudes

    def _save_fitted_params(self, fitted_params: Dict[str, Any]) -> str:
        """保存拟合参数到JSON文件（R10新增）

        Args:
            fitted_params: 拟合参数

        Returns:
            str: 保存的文件路径
        """
        output_path = self.output_path / 'numerics' / 'svf_fitted_params.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(fitted_params, f, indent=2, ensure_ascii=False)
        logger.info(f"拟合参数已保存: {output_path}")
        return str(output_path)

    def _generate_fit_comparison_plot(
        self,
        frequencies: np.ndarray,
        measured_magnitudes: List[np.ndarray],
        fitted_magnitudes: List[np.ndarray],
        channel_labels: List[str]
    ) -> str:
        """生成拟合结果对比图（R10新增）

        对比实测数据与拟合曲线的吻合程度

        Args:
            frequencies: 频率数组
            measured_magnitudes: 实测幅度数据
            fitted_magnitudes: 拟合得到的幅度数据
            channel_labels: 通道标签

        Returns:
            str: 生成的图片路径
        """
        import matplotlib as mpl

        n_channels = len(channel_labels)
        cmap = mpl.cm.get_cmap('tab10', n_channels) if n_channels <= 10 else mpl.cm.get_cmap('turbo', n_channels)
        colors = [cmap(i) for i in range(n_channels)]

        fig, ax = plt.subplots(figsize=(12, 5))

        for i, (meas_mag, fit_mag, label) in enumerate(zip(measured_magnitudes, fitted_magnitudes, channel_labels)):
            # 实测数据（实线）
            ax.semilogx(frequencies, meas_mag, color=colors[i], linewidth=1.8,
                       linestyle='-', label=f'{label} (实测)', alpha=0.9)
            # 拟合曲线（虚线）
            ax.semilogx(frequencies, fit_mag, color=colors[i], linewidth=1.4,
                       linestyle='--', label=f'{label} (拟合)', alpha=0.8)

        ax.set_title(f'{self.model_project_name} SVF层拟合结果对比\n(实线=实测, 虚线=拟合)',
                    fontsize=12, fontweight='bold')
        ax.set_xlabel('频率 (Hz)', fontsize=10)
        ax.set_ylabel('增益 (线性)', fontsize=10)
        ax.set_yscale('log')
        ax.grid(True, which='both', alpha=0.3)

        # 设置y轴范围
        all_vals = np.concatenate([*measured_magnitudes, *fitted_magnitudes])
        y_min, y_max = float(np.nanmin(all_vals)), float(np.nanmax(all_vals))
        pad = 0.05
        y_min_adj = max(1e-20, y_min / (1+pad))
        y_max_adj = y_max * (1+pad)
        ax.set_ylim(y_min_adj, y_max_adj)

        ax.legend(fontsize=7, ncol=min(4, n_channels), loc='best')
        plt.tight_layout()

        output_filename = self.svf_error_config.get('fitting', {}).get(
            'output_filename', 'svf_fit_comparison.png'
        )
        plot_path = self.output_path / 'plots' / output_filename
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close(fig)

        logger.info(f"拟合对比图已保存: {plot_path}")
        return str(plot_path)

    def _generate_component_comparison_table(
        self,
        svf_params: Dict[str, Any],
        fitted_params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """生成 SVF 电路元件参数对比表 (R16)

        对比三个值：
        1. 理论计算值（R15 公式）
        2. 标称值（1.5uF 和 200nF）
        3. 实测值（从拟合结果反推）

        Args:
            svf_params: 理论 SVF 参数 (f0, Q)
            fitted_params: 拟合后的 SVF 参数 (f0, Q)

        Returns:
            List[Dict]: 包含对比数据的列表
        """
        logger.info("生成 SVF 电路元件参数对比表...")

        R_integrator = 10e3  # 10k
        R_base = 10e3        # 10k
        
        # 标称电容值 (R16 指定)
        nominal_capacitors = [1.5e-6, 200e-9]  # 1.5uF, 200nF
        
        theory_f0 = svf_params['center_freqs']
        theory_Q = svf_params['quality_factors']
        
        fitted_f0 = fitted_params['fitted_params']['center_freqs']
        fitted_Q = fitted_params['fitted_params']['quality_factors']
        
        comparison_data = []
        
        for i in range(len(theory_f0)):
            # 1. 理论计算值
            c_theory = 1 / (2 * np.pi * theory_f0[i] * R_integrator)
            r6_theory = (3 * theory_Q[i] - 1) * R_base
            
            # 2. 标称值
            c_nominal = nominal_capacitors[i] if i < len(nominal_capacitors) else None
            # R6 没有明确标称值，通常就是理论值
            r6_nominal = r6_theory 
            
            # 3. 实测值 (从拟合结果反推)
            c_measured = 1 / (2 * np.pi * fitted_f0[i] * R_integrator)
            r6_measured = (3 * fitted_Q[i] - 1) * R_base
            
            stage_data = {
                'stage': f'SVF{i+1}',
                'f0': {
                    'theory': theory_f0[i],
                    'fitted': fitted_f0[i],
                    'error_pct': (fitted_f0[i] - theory_f0[i]) / theory_f0[i] * 100
                },
                'Q': {
                    'theory': theory_Q[i],
                    'fitted': fitted_Q[i],
                    'error_pct': (fitted_Q[i] - theory_Q[i]) / theory_Q[i] * 100
                },
                'C': {
                    'theory': c_theory,
                    'nominal': c_nominal,
                    'measured': c_measured,
                    'error_vs_theory_pct': (c_measured - c_theory) / c_theory * 100
                },
                'R6': {
                    'theory': r6_theory,
                    'nominal': r6_nominal,
                    'measured': r6_measured,
                    'error_vs_theory_pct': (r6_measured - r6_theory) / r6_theory * 100
                }
            }
            comparison_data.append(stage_data)
            
        return comparison_data

    def _calculate_svf_dense_combined_response(
        self,
        svf_params: Dict,
        dense_weights: Dict,
        measured_data: Dict[str, Any] = None,
        use_measured_svf: bool = True,
        fitted_params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """计算 SVF + Dense 组合频率响应（R6新增，R10修改）

        复用已有的 _calculate_svf_transfer_functions 和 _calculate_combined_transfer_functions
        方法来构建传递函数，然后使用 _calculate_frequency_response 计算频响。

        Args:
            svf_params: SVF 参数（中心频率、Q因子）
            dense_weights: Dense 权重
            measured_data: SVF 实测数据（可选）
            use_measured_svf: True=使用拟合参数，False=使用理论值
            fitted_params: 拟合后的 SVF 参数（优先使用）

        Returns:
            Dict: {
                'frequencies': np.ndarray,
                'magnitude_db': List[np.ndarray],  # 每个输出通道
                'phase_deg': List[np.ndarray]
            }
        """
        # 选择使用的参数：如果有拟合参数，使用 fitted_params['fitted_params']
        params_to_use = fitted_params['fitted_params'] if (use_measured_svf and fitted_params) else svf_params

        # 1. 构建传递函数（使用拟合参数或原始参数）
        svf_tfs = self._calculate_svf_transfer_functions(params_to_use)
        combined_tfs = self._calculate_combined_transfer_functions(svf_tfs, dense_weights)

        # 2. 获取频率点
        if measured_data is not None:
            frequencies = measured_data['frequencies']
            # 临时修改频率范围配置以使用实测数据频率点
            original_range = self.frequency_range.copy()
            self.frequency_range = {
                'start_freq': float(frequencies.min()),
                'stop_freq': float(frequencies.max()),
                'points': len(frequencies)
            }

        # 3. 计算频率响应（复用已有方法）
        freq_response = self._calculate_frequency_response(combined_tfs)

        # 恢复原始频率范围配置
        if measured_data is not None:
            self.frequency_range = original_range

        return freq_response

    def _generate_svf_dense_error_comparison_plot(
        self,
        baseline_response: Dict[str, Any],
        target_response: Dict[str, Any],
        dense_weights: Dict[str, Any]
    ) -> str:
        """生成 SVF+Dense 误差对比图（R6新增）

        对比 baseline (SVF理想+Dense) vs target (SVF实测+Dense)

        Args:
            baseline_response: 理想情况的频响
            target_response: 实测 SVF 情况的频响
            dense_weights: Dense 权重信息

        Returns:
            str: 生成的图片路径
        """
        import matplotlib as mpl
        from scipy import interpolate

        # 使用 baseline 的频率点（确保 x 轴一致）
        frequencies = baseline_response['frequencies']
        baseline_mag = [np.clip(np.power(10.0, m/20.0), 1e-20, None) for m in baseline_response['magnitude_db']]

        # 将 target 数据插值到 baseline 频率点
        target_freq = target_response['frequencies']
        target_mag_db = [np.clip(np.power(10.0, m/20.0), 1e-20, None) for m in target_response['magnitude_db']]

        target_mag_interp = []
        for tm in target_mag_db:
            interp_func = interpolate.interp1d(
                target_freq, tm, kind='linear',
                bounds_error=False, fill_value=np.nan
            )
            target_mag_interp.append(interp_func(frequencies))

        # 输出标签
        analysis_layer = dense_weights.get('analysis_layer', 1)
        output_labels = [f'D{analysis_layer}_{i+1}' for i in range(len(baseline_mag))]

        # 颜色映射
        n_channels = len(baseline_mag)
        cmap = mpl.cm.get_cmap('tab10', n_channels) if n_channels <= 10 else mpl.cm.get_cmap('turbo', n_channels)
        colors = [cmap(i) for i in range(n_channels)]

        # 创建对比图
        fig, ax = plt.subplots(figsize=(12, 4))

        # 绘制 baseline（虚线）
        for i, (m, lbl) in enumerate(zip(baseline_mag, output_labels)):
            ax.semilogx(frequencies, m, color=colors[i], linewidth=1.4,
                       linestyle='--', label=f'{lbl} (理想)', alpha=0.8)

        # 绘制 target（实线）- 使用插值后的数据
        for i, (m, lbl) in enumerate(zip(target_mag_interp, output_labels)):
            ax.semilogx(frequencies, m, color=colors[i], linewidth=1.8,
                       linestyle='-', label=f'{lbl} (SVF实测)', alpha=0.9)

        ax.set_title(
            f'{self.model_project_name} Dense#{analysis_layer} 频率响应对比\n'
            f'(虚线=理想SVF, 实线=SVF实测误差)',
            fontsize=12, fontweight='bold'
        )
        ax.set_xlabel('频率 (Hz)', fontsize=10)
        ax.set_ylabel('增益 (线性, log刻度)', fontsize=10)
        ax.set_yscale('log')
        ax.grid(True, which='both', alpha=0.3)

        # 设置y轴范围
        all_vals = np.concatenate([*baseline_mag, *target_mag_interp])
        y_min, y_max = float(np.nanmin(all_vals)), float(np.nanmax(all_vals))
        pad = 0.05
        y_min_adj = max(1e-20, y_min / (1+pad))
        y_max_adj = y_max * (1+pad)
        ax.set_ylim(y_min_adj, y_max_adj)

        ax.legend(fontsize=8, ncol=min(4, len(output_labels)*2), loc='best')
        plt.tight_layout()

        output_filename = self.svf_error_config.get('plot_config', {}).get(
            'dense_output_filename', 'svf_dense_error_comparison.png'
        )
        plot_path = self.output_path / 'plots' / output_filename
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close(fig)

        logger.info(f"SVF+Dense误差对比图已保存: {plot_path}")
        return str(plot_path)

    def _calculate_svf_dense_error_statistics(
        self,
        baseline_response: Dict[str, Any],
        target_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """计算 SVF+Dense 误差统计（R6新增）

        计算 target / baseline 的误差比值
        """
        from scipy import interpolate

        base_freq = baseline_response['frequencies']
        base_mag = [np.clip(np.power(10.0, m/20.0), 1e-20, None) for m in baseline_response['magnitude_db']]

        target_freq = target_response['frequencies']
        target_mags = [np.clip(np.power(10.0, m/20.0), 1e-20, None) for m in target_response['magnitude_db']]

        # 使用 baseline 频率点
        error_data = {
            'frequencies': base_freq.tolist(),
            'error_ratios': [],
            'statistics': []
        }

        n_channels = len(base_mag)
        output_labels = [f'D{self.analysis_layer}_{i+1}' for i in range(n_channels)]

        for i, (base_ch, target_ch, lbl) in enumerate(zip(base_mag, target_mags, output_labels)):
            # 将 target 数据插值到 baseline 频率点
            target_interp = interpolate.interp1d(
                target_freq, target_ch, kind='linear',
                bounds_error=False, fill_value=np.nan
            )
            target_interp_vals = target_interp(base_freq)

            # 计算误差比值: target / baseline
            with np.errstate(divide='ignore', invalid='ignore'):
                error_ratio = target_interp_vals / (base_ch + 1e-20)
                error_ratio = np.where(np.abs(base_ch) < 1e-20, np.nan, error_ratio)

            error_data['error_ratios'].append({
                'channel': lbl,
                'ratios': error_ratio.tolist()
            })

            # 计算统计指标
            valid_errors = error_ratio[~np.isnan(error_ratio)]
            if len(valid_errors) > 0:
                stats = {
                    'channel': lbl,
                    'mean_error_ratio': float(np.mean(valid_errors)),
                    'std_error_ratio': float(np.std(valid_errors)),
                    'min_error_ratio': float(np.min(valid_errors)),
                    'max_error_ratio': float(np.max(valid_errors)),
                    'mean_abs_error_percent': float(np.mean(np.abs(valid_errors - 1.0) * 100)),
                    'within_5pct': float(np.sum(np.abs(valid_errors - 1.0) <= 0.05) / len(valid_errors) * 100),
                    'within_10pct': float(np.sum(np.abs(valid_errors - 1.0) <= 0.1) / len(valid_errors) * 100)
                }
            else:
                stats = {k: None for k in [
                    'channel', 'mean_error_ratio', 'std_error_ratio',
                    'min_error_ratio', 'max_error_ratio', 'mean_abs_error_percent',
                    'within_5pct', 'within_10pct'
                ]}

            error_data['statistics'].append(stats)

        logger.info(f"✅ SVF+Dense 误差统计计算完成: {n_channels} 个通道")
        return error_data

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

            # 初始化变量
            svf_tfs = None
            combined_tfs = None
            freq_response = None
            report = None
            quantization_comparison = None
            plots = []

            # 新增：SVF层误差仿真（R3实现，R10修改）
            if self.svf_error_enable:
                logger.info("执行SVF层误差仿真...")
                measured_data = self._load_svf_measured_data()

                # 自测试补偿（如果启用）
                if self.svf_compensation_enabled and self.svf_selftest_file:
                    selftest_data = self._load_selftest_data()
                    measured_data = self._compensate_svf_with_selftest(measured_data, selftest_data)

                frequencies = measured_data['frequencies']
                measured_magnitudes = measured_data['magnitude']

                # ========== R10新增：拟合SVF参数 ==========
                fitting_config = self.svf_error_config.get('fitting', {})
                fitting_enabled = fitting_config.get('enabled', False)

                if fitting_enabled:
                    logger.info("开始拟合 SVF 参数...")

                    # 拟合 SVF 参数
                    fitted_params = self._fit_svf_parameters(frequencies, measured_magnitudes, svf_params)

                    # 保存拟合参数
                    self._save_fitted_params(fitted_params)

                    # 使用拟合参数计算理论频响
                    fitted_magnitudes = self._calculate_fitted_magnitudes(frequencies, fitted_params)

                    # 生成拟合对比图
                    n_filters = len(svf_params['center_freqs'])
                    channel_labels = []
                    for i in range(n_filters):
                        channel_labels.extend([f'SVF{i+1}_LP', f'SVF{i+1}_BP', f'SVF{i+1}_HP'])

                    fit_plot = self._generate_fit_comparison_plot(
                        frequencies, measured_magnitudes, fitted_magnitudes, channel_labels
                    )
                    plots.append(fit_plot)
                else:
                    fitted_params = None

                # 计算理论 SVF 频响（用于对比图）
                svf_response = self._calculate_svf_frequency_response_only(svf_params)

                # 生成 SVF 误差对比图（理论 vs 实测）
                svf_plot = self._generate_svf_error_comparison_plot(svf_response, measured_data)
                plots.append(svf_plot)

                # 生成误差分析数据
                svf_error_data = self._calculate_svf_error_statistics(svf_response, measured_data)

                # 保存误差分析数据
                svf_error_path = self.output_path / 'numerics' / 'svf_error_analysis.json'
                with open(svf_error_path, 'w', encoding='utf-8') as f:
                    json.dump(svf_error_data, f, indent=2, ensure_ascii=False)
                logger.info(f"SVF误差分析数据已保存: {svf_error_path}")

                # ========== R6新增：SVF+Dense 误差仿真 ==========
                include_dense = self.svf_error_config.get('include_dense_layer', False)
                if include_dense:
                    logger.info("执行 SVF+Dense 误差仿真...")

                    # 计算 baseline: 理想 SVF + Dense
                    baseline_response = self._calculate_svf_dense_combined_response(
                        svf_params, dense_weights,
                        measured_data=None, use_measured_svf=False
                    )

                    # 计算 target: 拟合 SVF + Dense（使用拟合参数）
                    target_response = self._calculate_svf_dense_combined_response(
                        svf_params, dense_weights,
                        measured_data=measured_data, use_measured_svf=True,
                        fitted_params=fitted_params  # 传递拟合参数
                    )

                    # 生成对比图
                    dense_plot = self._generate_svf_dense_error_comparison_plot(
                        baseline_response, target_response, dense_weights
                    )
                    plots.append(dense_plot)

                    # 计算误差统计
                    dense_error_stats = self._calculate_svf_dense_error_statistics(
                        baseline_response, target_response
                    )

                    # 保存误差分析
                    dense_error_path = self.output_path / 'numerics' / 'svf_dense_error_analysis.json'
                    with open(dense_error_path, 'w', encoding='utf-8') as f:
                        json.dump(dense_error_stats, f, indent=2, ensure_ascii=False)
                    logger.info(f"SVF+Dense误差分析数据已保存: {dense_error_path}")

                # R16: 生成元件参数对比表
                component_comparison = None
                if fitting_enabled and fitted_params:
                    component_comparison = self._generate_component_comparison_table(svf_params, fitted_params)

                # R13: 生成SVF误差仿真报告
                report = self._generate_svf_error_report(plots, fitted_params, component_comparison)
            else:
                # 原有逻辑：Dense层分析
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

            logger.info("WNET5电路验证分析完成")
            return True

        except Exception as e:
            logger.error(f"WNET5电路验证分析失败: {e}")
            import traceback
            traceback.print_exc()
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
        if svf_tfs is not None:
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
        if combined_tfs is not None:
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
        if freq_response is not None:
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
        else:
            fr = None

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

    def _generate_svf_error_report(self, plots: List[str], fitted_params: Dict = None, component_comparison: List[Dict] = None) -> str:
        """生成SVF层误差仿真的Markdown报告（R14改进 - 逻辑重构）

        Args:
            plots: 生成的图片路径列表
            fitted_params: 拟合参数（可选）
            component_comparison: 元件参数对比数据 (R16)

        Returns:
            str: 报告文件路径
        """
        logger.info("生成SVF误差仿真报告...")
        from datetime import datetime

        # 获取配置
        fitting_config = self.svf_error_config.get('fitting', {})
        fitting_enabled = fitting_config.get('enabled', False)
        include_dense = self.svf_error_config.get('include_dense_layer', False)

        # 报告保存路径
        report_path = self.output_path / "reports" / "report.md"
        
        # 1. 概述
        report_content = f"""# WNET5 电路验证与误差分析报告

## 1. 概述

本报告展示了 {self.model_project_name} 项目中 Dense 层 {self.analysis_layer} 的电路验证结果，重点分析了仿真理论计算与实际测量之间的差异及其影响因素。

- **项目**: {self.model_project_name}
- **分析层数**: {self.analysis_layer}
- **频率范围**: {self.frequency_range['start_freq']} - {self.frequency_range['stop_freq']} Hz
- **SVF仿真模式**: {'拟合传递函数' if fitting_enabled else '实测数据对比'}
- **包含Dense层**: {'是' if include_dense else '否'}

---

## 2. 频率响应对比（仿真 vs 实测）

本章节对比了电路的理论仿真结果与实际测量数据，评估整体模型的准确性。

### 2.1 仿真与实测合并对比图

![仿真与实测合并对比图](../plots/frequency_response_comparison_merged.png)

**设计目的**: 将仿真理论值与实验测量值合并在同一张图中进行对比，直观展示两者的一致性。
**横轴**: 频率 (Hz)，对数刻度
**纵轴**: 增益（线性），对数刻度
**数据曲线**: 虚线代表仿真理论值，实线代表实验测量值。
**数据来源**: 理论计算 + 实验测量数据

### 2.2 频率响应误差比值图

![频率响应误差比值图](../plots/frequency_response_error_ratio.png)

**设计目的**: 展示仿真理论值与实验测量值之间的误差比值（仿真/实验），用于精细化误差分析。
**横轴**: 频率 (Hz)，对数刻度
**纵轴**: 误差比值（线性），对数刻度
**数据曲线**: 每条曲线代表一个通道的误差比值，红色虚线为理想匹配线（比值=1.0）。
**数据来源**: 仿真数据 ÷ 实际测量数据

---

## 3. 误差因素分析

本章节深入探讨导致仿真与实测差异的各种因素，包括硬件量化误差和模拟电路参数偏差。

### 3.1 E96 量化影响分析

在实际电路实现中，电阻电容通常采用 E96 系列标准值，这会引入一定的量化误差。

![E96量化前后对比图](../plots/frequency_response_e96_comparison.png)

**设计目的**: 对比 Dense 层权重在 E96 量化前后的频率响应差异，评估量化对精度的影响。
**横轴**: 频率 (Hz)，对数刻度
**纵轴**: 增益（线性），对数刻度
**数据曲线**: 虚线代表原始权重，实线代表 E96 量化后的权重。
**数据来源**: 原始权重计算 vs E96 量化权重计算

### 3.2 SVF 层误差对整体的影响

SVF（状态可变滤波器）作为电路的前级，其参数（中心频率、品质因数）的实际偏差会传递到最终输出。

#### 3.2.1 SVF 参数拟合验证

![SVF拟合对比图](../plots/svf_fit_comparison.png)

**设计目的**: 验证拟合传递函数是否能够准确描述实测 SVF 层的频率响应特性。
**数据曲线**: 实线为 Measured，虚线为 Fitted。
**拟合结果**: 
- 拟合中心频率: {[round(x, 2) for x in fitted_params['fitted_params']['center_freqs']] if fitted_params and 'fitted_params' in fitted_params else 'N/A'} Hz
- 拟合品质因数: {[round(x, 4) for x in fitted_params['fitted_params']['quality_factors']] if fitted_params and 'fitted_params' in fitted_params else 'N/A'}

#### 3.2.2 SVF 层原始误差分布

![SVF误差对比图](../plots/svf_error_comparison_merged.png)

**设计目的**: 对比理想 SVF 层理论计算与实际测量之间的频率响应差异。
**纵轴**: 增益比值（理论/实测），单位 dB。

#### 3.2.3 SVF 误差对整体电路（SVF+Dense）的影响

![SVF+Dense误差对比图](../plots/svf_dense_error_comparison.png)

**设计目的**: 展示当前级 SVF 存在实测误差时，对整体电路频率响应的最终影响。
**数据曲线**: 实线为 Ideal SVF + Dense，虚线为 Measured SVF + Dense。

"""

        # R16: 添加元件参数对比表
        if component_comparison:
            report_content += "#### 3.2.4 SVF 电路元件参数对比 (R16)\n\n"
            report_content += "本节对比了 SVF 电路的关键元件参数：理论计算值、设计标称值以及从实测频率响应拟合结果中反推的实际值。\n\n"
            report_content += "| 阶段 | 参数 | 理论计算值 | 标称值 | 实测值 (拟合反推) | 误差 (vs 理论) |\n"
            report_content += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
            for stage in component_comparison:
                # C
                c_theory = stage['C']['theory'] * 1e6
                c_nominal = stage['C']['nominal'] * 1e6 if stage['C']['nominal'] else 0
                c_measured = stage['C']['measured'] * 1e6
                c_err = stage['C']['error_vs_theory_pct']
                c_err_str = f"{c_err:+.2f}%" if c_err is not None else "N/A"
                report_content += f"| {stage['stage']} | 电容 C (uF) | {c_theory:.4f} | {c_nominal:.4f} | {c_measured:.4f} | {c_err_str} |\n"
                
                # R6
                r6_theory = stage['R6']['theory'] / 1e3
                r6_nominal = stage['R6']['nominal'] / 1e3 if stage['R6']['nominal'] else 0
                r6_measured = stage['R6']['measured'] / 1e3
                r6_err = stage['R6']['error_vs_theory_pct']
                r6_err_str = f"{r6_err:+.2f}%" if r6_err is not None else "N/A"
                report_content += f"| {stage['stage']} | 电阻 R6 (kΩ) | {r6_theory:.2f} | {r6_nominal:.2f} | {r6_measured:.2f} | {r6_err_str} |\n"
            report_content += "\n"

        report_content += """
---

## 4. 结论

本仿真通过对 SVF 层参数的拟合与 Dense 层权重的量化分析，得出以下结论：

1. **拟合质量**: 
"""

        # 添加拟合质量信息
        if fitted_params and 'fit_quality' in fitted_params:
            fit_quality = fitted_params['fit_quality']
            report_content += f"""
   - 整体 RMSE: {fit_quality.get('overall_rmse', 'N/A'):.6f}
   - 整体 R²: {fit_quality.get('overall_r2', 'N/A'):.6f}
   - 结论: {'拟合良好 (R² > 0.99)' if fit_quality.get('overall_r2', 0) > 0.99 else '拟合存在一定偏差'}
"""

        report_content += f"""
2. **误差来源**: 
   - 观察 3.1 节可知 E96 量化带来的偏差。
   - 观察 3.2.3 节可知 SVF 层参数偏差对最终输出的影响。

---
"""

        # R14: 确保所有图片都被插入
        # 检查是否有遗漏的图片
        plot_dir = self.output_path / "plots"
        all_plots = list(plot_dir.glob("*.png"))
        
        # 简单的正则匹配已插入的图片
        import re
        inserted_plots = re.findall(r'!\[.*?\]\(\.\./plots/(.*?)\)', report_content)
        
        missing_plots = []
        for plot_file in all_plots:
            if plot_file.name not in inserted_plots:
                missing_plots.append(plot_file.name)
        
        if missing_plots:
            # 定义已知图表的说明
            plot_descriptions = {
                'frequency_response.png': {
                    'title': 'Dense层理论频率响应图',
                    'purpose': '展示Dense层输出的理论频率响应曲线（线性增益）。',
                    'xaxis': '频率 (Hz)，对数刻度',
                    'yaxis': '增益（线性），对数刻度',
                    'curves': '每个通道一条曲线，代表该通道在不同频率下的理论增益。',
                    'source': '基于模型权重的理论计算'
                }
            }

            report_content += "\n## 5. 其他生成图表\n\n"
            for plot_name in missing_plots:
                desc = plot_descriptions.get(plot_name)
                if desc:
                    report_content += f"### {desc['title']}\n\n"
                    report_content += f"![{desc['title']}](../plots/{plot_name})\n\n"
                    report_content += f"**设计目的**: {desc['purpose']}\n\n"
                    report_content += f"**横轴**: {desc['xaxis']}\n\n"
                    report_content += f"**纵轴**: {desc['yaxis']}\n\n"
                    report_content += f"**数据曲线**: {desc['curves']}\n\n"
                    report_content += f"**数据来源**: {desc['source']}\n\n"
                else:
                    report_content += f"### {plot_name}\n\n![{plot_name}](../plots/{plot_name})\n\n"

        report_content += f"""
---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        # 保存报告
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        # R14: 验证代码
        with open(report_path, 'r', encoding='utf-8') as f:
            final_content = f.read()
        
        verification_failed = False
        for plot_file in all_plots:
            if plot_file.name not in final_content:
                logger.error(f"❌ 报告验证失败！图片 {plot_file.name} 未被插入到报告中。")
                verification_failed = True
            else:
                # 检查是否使用了正确的相对路径格式
                expected_rel_path = f"../plots/{plot_file.name}"
                if expected_rel_path not in final_content:
                    logger.error(f"❌ 报告验证失败！图片 {plot_file.name} 的路径格式不正确。")
                    verification_failed = True

        if not verification_failed:
            logger.info("✅ 报告验证通过：所有图片均已正确插入且路径正确。")
        else:
            logger.warning("⚠️ 报告验证存在问题，请检查输出。")

        logger.info(f"SVF误差仿真报告已保存: {report_path}")
        return str(report_path)