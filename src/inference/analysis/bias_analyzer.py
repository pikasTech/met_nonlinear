"""
偏置误差分析模块

实现稳态段提取法和频域滤波法两种偏置计算方法
"""

import numpy as np
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any, Union

logger = logging.getLogger(__name__)


class BiasAnalyzer(ABC):
    """偏置分析器基类"""
    
    def __init__(self, **kwargs):
        """
        初始化偏置分析器
        
        参数:
            kwargs: 方法特定参数
        """
        self.params = kwargs
    
    @abstractmethod
    def calculate_bias(self, channel_data: np.ndarray, sample_rate: float) -> float:
        """
        计算单通道偏置
        
        参数:
            channel_data: shape (time_steps,) 的单通道数据
            sample_rate: 采样率 (Hz)
            
        返回:
            float: 偏置估计值
        """
        pass
    
    @abstractmethod
    def get_method_name(self) -> str:
        """返回方法名称"""
        pass
    
    def analyze_wavedata(self, wave_data) -> Dict[str, Any]:
        """
        分析WaveData对象的所有通道
        
        参数:
            wave_data: WaveData对象
            
        返回:
            Dict: 包含每个通道偏置的字典
        """
        results = []
        
        for record in wave_data.records:
            record_results = []
            n_channels = record.data.shape[1]
            
            for ch in range(n_channels):
                channel_data = record.data[:, ch]
                bias = self.calculate_bias(channel_data, record.sample_rate)
                
                channel_result = {
                    'channel': ch,
                    'bias': float(bias),
                    'channel_name': record.channel_names[ch] if ch < len(record.channel_names) else f'Channel_{ch}'
                }
                record_results.append(channel_result)
            
            results.append({
                'record_id': record.record_id,
                'channels': record_results,
                'n_channels': n_channels,
                'n_samples': record.data.shape[0]
            })
        
        return {
            'method': self.get_method_name(),
            'parameters': self.params,
            'records': results
        }


class SteadyStateBiasAnalyzer(BiasAnalyzer):
    """稳态段提取法偏置分析器"""
    
    def __init__(self, steady_ratio: float = 0.3, stability_threshold: float = 0.1, **kwargs):
        """
        初始化稳态段提取法分析器
        
        参数:
            steady_ratio: 用于计算偏置的信号末尾部分比例 (0-1)
            stability_threshold: 稳定性阈值，std/mean 的比值
            kwargs: 其他参数
        """
        super().__init__(steady_ratio=steady_ratio, stability_threshold=stability_threshold, **kwargs)
        self.steady_ratio = steady_ratio
        self.stability_threshold = stability_threshold
    
    def calculate_bias(self, channel_data: np.ndarray, sample_rate: float) -> float:
        """
        通过稳态段提取计算偏置
        
        参数:
            channel_data: shape (time_steps,) 的单通道数据
            sample_rate: 采样率 (Hz)
            
        返回:
            float: 偏置估计值
        """
        n_samples = len(channel_data)
        
        # 对于大数据集，采用采样策略避免计算超时
        if n_samples > 100000:  # 超过10万样本点时启用采样
            logger.info(f"          大数据集检测({n_samples}个样本)，启用快速采样计算")
            # 采样到最多50000个点进行计算
            sample_stride = max(1, n_samples // 50000)
            channel_data = channel_data[::sample_stride]
            n_samples = len(channel_data)
            logger.info(f"          采样后数据量: {n_samples}个样本")
        
        # 计算稳态段起始位置
        steady_start = int(n_samples * (1 - self.steady_ratio))
        
        # 确保至少有10个样本
        if n_samples - steady_start < 10:
            steady_start = max(0, n_samples - 10)
        
        steady_data = channel_data[steady_start:]
        logger.info(f"          稳态段数据量: {len(steady_data)}个样本")
        
        # 计算稳态段的统计特性
        mean_val = np.mean(steady_data)
        std_val = np.std(steady_data)
        
        # 检查稳态段的稳定性
        if np.abs(mean_val) > 1e-10:  # 避免除零
            stability_ratio = std_val / np.abs(mean_val)
            if stability_ratio > self.stability_threshold:
                logger.warning(f"稳态段可能包含振荡成分，稳定性比值: {stability_ratio:.3f}")
        
        logger.info(f"          偏置计算完成: {mean_val:.6f}")
        return mean_val
    
    def get_method_name(self) -> str:
        return "steady_state"
    
    def analyze_segment_stability(self, channel_data: np.ndarray, 
                                segment_ratio: float = 0.1) -> Dict[str, Any]:
        """
        分析信号不同段的稳定性，帮助确定最佳的steady_ratio
        
        参数:
            channel_data: 单通道数据
            segment_ratio: 每段占总长度的比例
            
        返回:
            Dict: 稳定性分析结果
        """
        n_samples = len(channel_data)
        segment_size = int(n_samples * segment_ratio)
        n_segments = int(1 / segment_ratio)
        
        stability_metrics = []
        
        for i in range(n_segments):
            start = i * segment_size
            end = min((i + 1) * segment_size, n_samples)
            segment = channel_data[start:end]
            
            if len(segment) > 0:
                mean_val = np.mean(segment)
                std_val = np.std(segment)
                
                stability_metrics.append({
                    'segment': i,
                    'start_ratio': start / n_samples,
                    'end_ratio': end / n_samples,
                    'mean': float(mean_val),
                    'std': float(std_val),
                    'cv': float(std_val / np.abs(mean_val)) if np.abs(mean_val) > 1e-10 else float('inf')
                })
        
        # 找出最稳定的段
        cvs = [m['cv'] for m in stability_metrics if m['cv'] != float('inf')]
        if cvs:
            min_cv_idx = np.argmin(cvs)
            most_stable = stability_metrics[min_cv_idx]
        else:
            most_stable = None
        
        return {
            'segments': stability_metrics,
            'most_stable_segment': most_stable,
            'recommended_steady_ratio': 1.0 - most_stable['start_ratio'] if most_stable else self.steady_ratio
        }


class FrequencyDomainBiasAnalyzer(BiasAnalyzer):
    """频域滤波法偏置分析器"""
    
    def __init__(self, dc_bandwidth: float = 1.0, window: str = 'hann', **kwargs):
        """
        初始化频域滤波法分析器
        
        参数:
            dc_bandwidth: DC分量的带宽 (Hz)，用于低通滤波
            window: 窗函数类型 ('hann', 'hamming', 'blackman', None)
            kwargs: 其他参数
        """
        super().__init__(dc_bandwidth=dc_bandwidth, window=window, **kwargs)
        self.dc_bandwidth = dc_bandwidth
        self.window = window
    
    def calculate_bias(self, channel_data: np.ndarray, sample_rate: float) -> float:
        """
        通过频域分析提取DC偏置
        
        参数:
            channel_data: shape (time_steps,) 的单通道数据
            sample_rate: 采样率 (Hz)
            
        返回:
            float: 偏置估计值
        """
        n_samples = len(channel_data)
        
        # 应用窗函数减少频谱泄漏
        if self.window is not None:
            if self.window == 'hann':
                window = np.hanning(n_samples)
            elif self.window == 'hamming':
                window = np.hamming(n_samples)
            elif self.window == 'blackman':
                window = np.blackman(n_samples)
            else:
                window = np.ones(n_samples)
            
            # 应用窗函数并补偿能量损失
            windowed_data = channel_data * window
            window_correction = np.mean(window)
            windowed_data = windowed_data / window_correction
        else:
            windowed_data = channel_data
        
        # 执行FFT
        fft_data = np.fft.fft(windowed_data)
        freqs = np.fft.fftfreq(n_samples, 1/sample_rate)
        
        # 方法1：直接提取DC分量
        dc_component = fft_data[0].real / n_samples
        
        # 方法2：低通滤波提取低频分量（更鲁棒）
        if self.dc_bandwidth > 0:
            # 创建低通滤波器
            mask = np.abs(freqs) <= self.dc_bandwidth
            filtered_fft = np.zeros_like(fft_data)
            filtered_fft[mask] = fft_data[mask]
            
            # 逆FFT获取低频信号
            low_freq_signal = np.fft.ifft(filtered_fft).real
            
            # 使用低频信号的平均值作为偏置估计
            robust_dc = np.mean(low_freq_signal)
            
            # 记录两种方法的差异
            if np.abs(dc_component - robust_dc) > 0.001:
                logger.debug(f"DC分量: {dc_component:.6f}, 低通滤波: {robust_dc:.6f}")
            
            return robust_dc
        else:
            return dc_component
    
    def get_method_name(self) -> str:
        return "frequency_domain"
    
    def analyze_spectrum(self, channel_data: np.ndarray, 
                        sample_rate: float) -> Dict[str, Any]:
        """
        分析信号的频谱特性
        
        参数:
            channel_data: 单通道数据
            sample_rate: 采样率
            
        返回:
            Dict: 频谱分析结果
        """
        n_samples = len(channel_data)
        
        # 执行FFT
        fft_data = np.fft.fft(channel_data)
        freqs = np.fft.fftfreq(n_samples, 1/sample_rate)
        magnitude = np.abs(fft_data) / n_samples
        
        # 只分析正频率部分
        pos_mask = freqs >= 0
        pos_freqs = freqs[pos_mask]
        pos_magnitude = magnitude[pos_mask]
        
        # 找出主要频率成分
        # 排除DC分量，找出最大的5个频率成分
        if len(pos_freqs) > 1:
            non_dc_mask = pos_freqs > 0.1
            if np.any(non_dc_mask):
                non_dc_mags = pos_magnitude[non_dc_mask]
                non_dc_freqs = pos_freqs[non_dc_mask]
                
                # 找出最大的频率成分
                top_indices = np.argsort(non_dc_mags)[-5:][::-1]
                dominant_freqs = [(float(non_dc_freqs[i]), float(non_dc_mags[i])) 
                                for i in top_indices if non_dc_mags[i] > 0.001]
            else:
                dominant_freqs = []
        else:
            dominant_freqs = []
        
        return {
            'dc_magnitude': float(magnitude[0]),
            'dominant_frequencies': dominant_freqs,
            'total_energy': float(np.sum(magnitude**2)),
            'dc_energy_ratio': float(magnitude[0]**2 / np.sum(magnitude**2)) if np.sum(magnitude**2) > 0 else 0
        }


class AutoBiasAnalyzer(BiasAnalyzer):
    """自动选择最佳方法的偏置分析器"""
    
    def __init__(self, **kwargs):
        """初始化自动分析器"""
        super().__init__(**kwargs)
        self.steady_analyzer = SteadyStateBiasAnalyzer()
        self.freq_analyzer = FrequencyDomainBiasAnalyzer()
        self.selected_method = None
    
    def calculate_bias(self, channel_data: np.ndarray, sample_rate: float) -> float:
        """
        自动选择最佳方法计算偏置
        
        参数:
            channel_data: shape (time_steps,) 的单通道数据
            sample_rate: 采样率 (Hz)
            
        返回:
            float: 偏置估计值
        """
        # 分析信号特性
        signal_properties = self._analyze_signal_properties(channel_data, sample_rate)
        
        # 根据信号特性选择方法
        if signal_properties['has_strong_transient']:
            # 有强瞬态，使用稳态段提取法
            self.selected_method = 'steady_state'
            return self.steady_analyzer.calculate_bias(channel_data, sample_rate)
        elif signal_properties['has_multiple_frequencies']:
            # 有多个频率成分，使用频域滤波法
            self.selected_method = 'frequency_domain'
            return self.freq_analyzer.calculate_bias(channel_data, sample_rate)
        else:
            # 默认使用频域滤波法（更准确）
            self.selected_method = 'frequency_domain'
            return self.freq_analyzer.calculate_bias(channel_data, sample_rate)
    
    def get_method_name(self) -> str:
        return f"auto({self.selected_method})" if self.selected_method else "auto"
    
    def _analyze_signal_properties(self, channel_data: np.ndarray, 
                                  sample_rate: float) -> Dict[str, bool]:
        """
        分析信号特性以选择最佳方法
        
        参数:
            channel_data: 单通道数据
            sample_rate: 采样率
            
        返回:
            Dict: 信号特性
        """
        n_samples = len(channel_data)
        
        # 检查瞬态响应
        # 比较前后部分的统计特性
        front_part = channel_data[:n_samples//4]
        back_part = channel_data[-n_samples//4:]
        
        front_mean = np.mean(front_part)
        back_mean = np.mean(back_part)
        mean_diff = np.abs(front_mean - back_mean)
        
        front_std = np.std(front_part)
        back_std = np.std(back_part)
        std_diff = np.abs(front_std - back_std)
        
        # 判断是否有强瞬态
        signal_range = np.ptp(channel_data)
        has_strong_transient = (mean_diff > 0.1 * signal_range) or (std_diff > 0.2 * np.mean([front_std, back_std]))
        
        # 使用频谱分析检查多频率成分
        spectrum_info = self.freq_analyzer.analyze_spectrum(channel_data, sample_rate)
        has_multiple_frequencies = len(spectrum_info['dominant_frequencies']) > 2
        
        return {
            'has_strong_transient': has_strong_transient,
            'has_multiple_frequencies': has_multiple_frequencies,
            'dc_energy_ratio': spectrum_info['dc_energy_ratio']
        }


class ChannelBiasAnalyzer:
    """通道偏置误差分析器"""
    
    def __init__(self, method: str = 'auto', **kwargs):
        """
        初始化分析器
        
        参数:
            method: 分析方法 ('frequency_domain', 'steady_state', 'auto')
            kwargs: 方法特定参数
        """
        self.method = method
        self.params = kwargs
        
        # 创建具体的分析器
        if method == 'steady_state':
            self.analyzer = SteadyStateBiasAnalyzer(**kwargs)
        elif method == 'frequency_domain':
            self.analyzer = FrequencyDomainBiasAnalyzer(**kwargs)
        elif method == 'auto':
            self.analyzer = AutoBiasAnalyzer(**kwargs)
        else:
            raise ValueError(f"未知的分析方法: {method}")
    
    def analyze_bias_errors(self, ref_data: np.ndarray, comp_data: np.ndarray, 
                          sample_rate: float, layer_info: Optional[Dict] = None) -> Dict[str, Any]:
        """
        分析偏置误差
        
        参数:
            ref_data: 参考数据 (time_steps, channels)
            comp_data: 对比数据 (time_steps, channels)
            sample_rate: 采样率
            layer_info: 层信息（可选）
        
        返回:
            dict: 包含偏置误差分析结果
        """
        logger.info(f'        [analyze_bias_errors] 开始分析，数据形状: ref={ref_data.shape}, comp={comp_data.shape}')
        
        # 确保数据形状一致
        if ref_data.shape != comp_data.shape:
            raise ValueError(f"数据形状不一致: ref={ref_data.shape}, comp={comp_data.shape}")
        
        n_channels = ref_data.shape[1] if ref_data.ndim > 1 else 1
        logger.info(f'        [analyze_bias_errors] 检测到{n_channels}个通道')
        
        # 处理一维数据
        if ref_data.ndim == 1:
            ref_data = ref_data.reshape(-1, 1)
            comp_data = comp_data.reshape(-1, 1)
            logger.info('        [analyze_bias_errors] 已将一维数据转换为二维')
        
        bias_errors = []
        
        for ch in range(n_channels):
            logger.info(f'        [analyze_bias_errors] 计算第{ch+1}/{n_channels}通道偏置误差...')
            ref_bias = self.analyzer.calculate_bias(ref_data[:, ch], sample_rate)
            comp_bias = self.analyzer.calculate_bias(comp_data[:, ch], sample_rate)
            bias_error = ref_bias - comp_bias
            logger.info(f'        [analyze_bias_errors] 第{ch+1}通道: ref_bias={ref_bias:.6f}, comp_bias={comp_bias:.6f}, error={bias_error:.6f}')
            
            bias_errors.append({
                'channel': ch,
                'ref_bias': float(ref_bias),
                'comp_bias': float(comp_bias),
                'bias_error': float(bias_error),
                'relative_error': float(bias_error / ref_bias) if abs(ref_bias) > 1e-10 else None
            })
        
        # 计算统计信息
        logger.info('        [analyze_bias_errors] 计算统计信息...')
        bias_error_values = [e['bias_error'] for e in bias_errors]
        
        result = {
            'layer_info': layer_info,
            'channel_count': n_channels,
            'bias_errors': bias_errors,
            'summary': {
                'mean_bias_error': float(np.mean(bias_error_values)),
                'std_bias_error': float(np.std(bias_error_values)),
                'max_bias_error': float(np.max(np.abs(bias_error_values))),
                'method': self.analyzer.get_method_name(),
                'parameters': self.params
            }
        }
        logger.info(f'        [analyze_bias_errors] 单层偏置分析完成，{n_channels}个通道')
        return result
    
    def _validate_layer_data(self, layer_data_pairs: List[Tuple]) -> Dict[str, Any]:
        """验证输入数据的一致性"""
        if not layer_data_pairs:
            raise ValueError("layer_data_pairs 不能为空")
        
        validation_info = {
            'layer_count': len(layer_data_pairs),
            'channel_counts': [],
            'data_shapes': [],
            'sample_rates': []
        }
        
        for i, (ref_data, comp_data, sample_rate, layer_info) in enumerate(layer_data_pairs):
            # 验证数据形状
            if ref_data.shape != comp_data.shape:
                raise ValueError(f"第{i}层数据形状不一致: ref={ref_data.shape}, comp={comp_data.shape}")
            
            # 记录通道数
            n_channels = ref_data.shape[1] if ref_data.ndim > 1 else 1
            validation_info['channel_counts'].append(n_channels)
            validation_info['data_shapes'].append(ref_data.shape)
            validation_info['sample_rates'].append(sample_rate)
        
        return validation_info
    
    def analyze_multilayer_bias(self, layer_data_pairs: List[Tuple[np.ndarray, np.ndarray, float, Dict]]) -> Dict[str, Any]:
        """
        分析多层网络的偏置误差
        
        参数:
            layer_data_pairs: [(ref_data, comp_data, sample_rate, layer_info), ...]
        
        返回:
            dict: 包含多层偏置误差统计信息
        """
        logger.info(f'      [analyze_multilayer_bias] 开始分析，共{len(layer_data_pairs)}层')
        
        # 验证输入数据
        logger.info('      [analyze_multilayer_bias] 验证输入数据...')
        validation_info = self._validate_layer_data(layer_data_pairs)
        logger.info(f'      [analyze_multilayer_bias] 数据验证完成: {validation_info}')
        
        results = []
        bias_matrix = []  # 嵌套列表格式，每层可能有不同通道数
        
        # 分析每层的偏置误差
        logger.info('      [analyze_multilayer_bias] 开始分层偏置误差分析...')
        for i, (ref_data, comp_data, sample_rate, layer_info) in enumerate(layer_data_pairs):
            logger.info(f'      [analyze_multilayer_bias] 分析第{i+1}层，数据形状: ref={ref_data.shape}, comp={comp_data.shape}')
            layer_result = self.analyze_bias_errors(ref_data, comp_data, sample_rate, layer_info)
            results.append(layer_result)
            logger.info(f'      [analyze_multilayer_bias] 第{i+1}层偏置误差分析完成')
            
            # 提取偏置误差向量
            bias_vector = [e['bias_error'] for e in layer_result['bias_errors']]
            bias_matrix.append(bias_vector)
            logger.info(f'      [analyze_multilayer_bias] 第{i+1}层偏置向量长度: {len(bias_vector)}')
        
        # 使用分层统计法计算统计信息
        logger.info('      [analyze_multilayer_bias] 开始计算分层统计信息...')
        per_layer_stats = []
        all_bias_errors = []
        layer_channel_counts = []
        
        for i, bias_vector in enumerate(bias_matrix):
            logger.info(f'      [analyze_multilayer_bias] 计算第{i+1}层统计，偏置向量: {bias_vector[:5] if len(bias_vector) > 5 else bias_vector}...')
            if bias_vector:  # 确保非空
                layer_mean = np.mean(bias_vector)
                layer_std = np.std(bias_vector)
                layer_max = np.max(np.abs(bias_vector))
                
                per_layer_stats.append({
                    'layer': i,
                    'mean': float(layer_mean),
                    'std': float(layer_std),
                    'max_abs': float(layer_max),
                    'channel_count': len(bias_vector)
                })
                all_bias_errors.extend(bias_vector)
                layer_channel_counts.append(len(bias_vector))
                logger.info(f'      [analyze_multilayer_bias] 第{i+1}层统计完成: mean={layer_mean:.6f}, channels={len(bias_vector)}')
            else:
                # 处理空的偏置向量
                per_layer_stats.append({
                    'layer': i,
                    'mean': 0.0,
                    'std': 0.0,
                    'max_abs': 0.0,
                    'channel_count': 0
                })
                logger.info(f'      [analyze_multilayer_bias] 第{i+1}层为空偏置向量')
        
        # 计算全局统计
        logger.info('      [analyze_multilayer_bias] 开始计算全局统计...')
        if all_bias_errors:
            logger.info(f'      [analyze_multilayer_bias] 全局偏置误差数量: {len(all_bias_errors)}')
            global_mean = np.mean(all_bias_errors)
            global_std = np.std(all_bias_errors)
            global_max = np.max(np.abs(all_bias_errors))
            max_channels = max(layer_channel_counts) if layer_channel_counts else 0
            min_channels = min(layer_channel_counts) if layer_channel_counts else 0
            
            logger.info(f'      [analyze_multilayer_bias] 全局统计: mean={global_mean:.6f}, std={global_std:.6f}, max={global_max:.6f}')
            
            # 找出最差的偏置误差位置
            logger.info('      [analyze_multilayer_bias] 查找最差偏置误差位置...')
            worst_value = 0.0
            worst_layer = 0
            worst_channel = 0
            for layer_idx, bias_vector in enumerate(bias_matrix):
                if bias_vector:
                    layer_max_idx = np.argmax(np.abs(bias_vector))
                    layer_max_value = bias_vector[layer_max_idx]
                    if abs(layer_max_value) > abs(worst_value):
                        worst_value = layer_max_value
                        worst_layer = layer_idx
                        worst_channel = layer_max_idx
            logger.info(f'      [analyze_multilayer_bias] 最差偏置误差: 第{worst_layer+1}层第{worst_channel}通道，值={worst_value:.6f}')
        else:
            logger.warning('      [analyze_multilayer_bias] 警告：没有偏置误差数据')
            global_mean = 0.0
            global_std = 0.0
            global_max = 0.0
            max_channels = 0
            min_channels = 0
            worst_value = 0.0
            worst_layer = 0
            worst_channel = 0
        
        logger.info('      [analyze_multilayer_bias] 构造返回结果...')
        result = {
            'layer_count': len(results),
            'layer_results': results,
            'layer_statistics': per_layer_stats,
            'bias_error_matrix': bias_matrix,
            'global_statistics': {
                'mean_bias_error': float(global_mean),
                'std_bias_error': float(global_std),
                'max_bias_error': float(global_max),
                'total_channels': len(all_bias_errors),
                'max_channels_per_layer': max_channels,
                'min_channels_per_layer': min_channels
            },
            'worst_case': {
                'layer': int(worst_layer + 1),
                'channel': int(worst_channel),
                'bias_error': float(worst_value)
            } if all_bias_errors else None,
            'validation_info': validation_info,
            'method_info': {
                'method': self.analyzer.get_method_name(),
                'parameters': self.params
            }
        }
        logger.info(f'      [analyze_multilayer_bias] 多层偏置分析完成！总共{len(results)}层，总通道数{len(all_bias_errors)}')
        return result