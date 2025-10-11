"""
管理模块工具函数

提供通用的工具函数
"""

import numpy as np
import logging
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)


def combine_layer_outputs(layer_outputs: List, prefix: str, wave_processor):
    """
    合并分层输出为单个WaveData，每层一个记录
    
    参数:
        layer_outputs: 层输出列表
        prefix: 前缀标识
        wave_processor: Wave处理器实例
        
    返回:
        WaveData: 合并后的数据
    """
    from calibration_analyzer.wavedata import WaveData, WaveRecord
    
    combined_data = WaveData()
    combined_data.description = f'{prefix} layer outputs'
    
    for i, layer_output in enumerate(layer_outputs):
        if not layer_output.records:
            continue
        
        # 合并该层的所有记录数据
        all_data = []
        for record in layer_output.records:
            all_data.append(record.data)
        
        layer_data = np.concatenate(all_data, axis=0)
        
        # 创建层记录
        layer_record = WaveRecord(
            data=layer_data,
            sample_rate=layer_output.records[0].sample_rate,
            channel_names=layer_output.records[0].channel_names,
            record_id=f'{prefix}_layer_{i + 1}',
            user_metadata={
                'layer_index': i + 1,
                'num_input_records': len(layer_output.records),
                'original_description': getattr(layer_output, 'description', ''),
                'data_shape': layer_data.shape
            }
        )
        combined_data.records.append(layer_record)
    
    logger.info(f'{prefix} 后端成功合并 {len(layer_outputs)} 层输出'
               f'（每层包含 {len(layer_output.records) if layer_outputs else 0} 个原始记录）')
    
    return combined_data


def generate_error_statistics(layer_errors: List[Dict]) -> Dict:
    """
    生成误差统计摘要
    
    参数:
        layer_errors: 逐层误差列表
        
    返回:
        Dict: 统计摘要
    """
    if not layer_errors:
        return {}
    
    # 提取各项指标
    rms_errors = [layer['rms_error'] for layer in layer_errors]
    max_errors = [layer['max_error'] for layer in layer_errors]
    mean_errors = [layer['mean_error'] for layer in layer_errors]
    
    return {
        'average_rms_error': float(np.mean(rms_errors)),
        'max_rms_error': float(np.max(rms_errors)),
        'average_max_error': float(np.mean(max_errors)),
        'worst_case_error': float(np.max(max_errors)),
        'average_mean_error': float(np.mean(mean_errors)),
        'total_layers': len(layer_errors)
    }


def compute_error_metrics(ref_output: np.ndarray, comp_output: np.ndarray) -> Dict[str, float]:
    """
    计算两个输出之间的误差指标
    
    参数:
        ref_output: 参考输出
        comp_output: 对比输出
        
    返回:
        Dict: 包含各种误差指标的字典
    """
    # 确保数据长度一致
    min_length = min(len(ref_output), len(comp_output))
    ref_output = ref_output[:min_length]
    comp_output = comp_output[:min_length]
    
    # 计算误差
    error = ref_output - comp_output
    
    return {
        'mean_error': float(np.mean(error)),
        'std_error': float(np.std(error)),
        'rms_error': float(np.sqrt(np.mean(np.square(error)))),
        'max_error': float(np.max(np.abs(error))),
        'num_samples': error.size,
        'error_shape': list(error.shape)
    }


def flatten_wave_records(wave_data) -> np.ndarray:
    """
    将WaveData的所有记录展平为一维数组
    
    参数:
        wave_data: WaveData对象
        
    返回:
        np.ndarray: 展平后的数据
    """
    all_data = []
    
    for record in wave_data.records:
        data = record.data
        if hasattr(data, 'flatten'):
            all_data.append(data.flatten())
        else:
            all_data.append(np.array(data).flatten())
    
    return np.concatenate(all_data) if all_data else np.array([])


def extract_channel_data(wave_data) -> Tuple[np.ndarray, float]:
    """
    从WaveData提取通道数据
    
    参数:
        wave_data: WaveData对象
        
    返回:
        (data, sample_rate): shape为(time_steps, channels)的数据和采样率
    """
    if not wave_data.records:
        return np.array([[]]), 0.0
    
    # 合并所有记录的数据
    all_data = []
    sample_rate = wave_data.records[0].sample_rate
    
    for record in wave_data.records:
        all_data.append(record.data)
    
    # 垂直堆叠所有记录
    if all_data:
        combined_data = np.vstack(all_data)
    else:
        combined_data = np.array([[]])
    
    return combined_data, sample_rate


def format_bias_error_matrix(bias_matrix: List[List[float]], layer_names: List[str] = None, 
                           channel_names: List[str] = None) -> Dict[str, Any]:
    """
    格式化偏置误差矩阵，便于报告和可视化
    
    参数:
        bias_matrix: 偏置误差嵌套列表，每层可能有不同的通道数
        layer_names: 层名称列表
        channel_names: 通道名称列表（已废弃，保留接口兼容）
        
    返回:
        Dict: 格式化的矩阵数据
    """
    if not isinstance(bias_matrix, (list, tuple)):
        raise ValueError(f"偏置矩阵必须是列表格式，当前类型: {type(bias_matrix)}")
    
    n_layers = len(bias_matrix)
    actual_channels_per_layer = [len(layer) for layer in bias_matrix]
    
    if layer_names is None:
        layer_names = [f'Layer_{i+1}' for i in range(n_layers)]
    
    # 计算每层统计信息
    per_layer_stats = []
    all_values = []
    
    for i in range(n_layers):
        layer_data = bias_matrix[i]
        
        if layer_data:  # 确保非空
            layer_array = np.array(layer_data)
            per_layer_stats.append({
                'layer': layer_names[i],
                'channel_count': len(layer_data),
                'mean': float(np.mean(layer_array)),
                'std': float(np.std(layer_array)),
                'max': float(np.max(np.abs(layer_array))),
                'values': layer_data
            })
            all_values.extend(layer_data)
        else:
            per_layer_stats.append({
                'layer': layer_names[i],
                'channel_count': 0,
                'mean': 0.0,
                'std': 0.0,
                'max': 0.0,
                'values': []
            })
    
    # 计算全局统计
    if all_values:
        all_array = np.array(all_values)
        overall_stats = {
            'mean': float(np.mean(all_array)),
            'std': float(np.std(all_array)),
            'max': float(np.max(np.abs(all_array))),
            'min': float(np.min(all_array)),
            'rms': float(np.sqrt(np.mean(np.square(all_array)))),
            'total_channels': len(all_values)
        }
    else:
        overall_stats = {
            'mean': 0.0, 'std': 0.0, 'max': 0.0, 'min': 0.0, 'rms': 0.0, 'total_channels': 0
        }
    
    return {
        'matrix': bias_matrix,
        'layer_count': n_layers,
        'channels_per_layer': actual_channels_per_layer,
        'layer_names': layer_names,
        'per_layer_stats': per_layer_stats,
        'overall_stats': overall_stats
    }


def validate_signal_properties(data: np.ndarray, sample_rate: float) -> Dict[str, Any]:
    """
    验证信号属性，检查是否适合进行偏置分析
    
    参数:
        data: 信号数据 (time_steps, channels)
        sample_rate: 采样率
        
    返回:
        Dict: 信号属性验证结果
    """
    n_samples, n_channels = data.shape if data.ndim > 1 else (len(data), 1)
    
    # 计算信号时长
    duration = n_samples / sample_rate
    
    # 检查信号长度
    min_duration = 0.1  # 最少0.1秒
    is_sufficient_length = duration >= min_duration
    
    # 检查信号范围
    signal_range = np.ptp(data, axis=0) if data.ndim > 1 else np.ptp(data)
    is_non_zero = np.any(signal_range > 1e-10)
    
    # 检查采样率
    is_valid_sample_rate = sample_rate > 0
    
    # 计算信噪比估计（使用高频成分作为噪声估计）
    if n_samples > 10:
        high_freq_noise = np.std(np.diff(data, axis=0), axis=0) if data.ndim > 1 else np.std(np.diff(data))
        signal_std = np.std(data, axis=0) if data.ndim > 1 else np.std(data)
        snr_estimate = signal_std / (high_freq_noise + 1e-10)
    else:
        snr_estimate = np.array([0.0])
    
    return {
        'n_samples': n_samples,
        'n_channels': n_channels,
        'duration': duration,
        'sample_rate': sample_rate,
        'is_sufficient_length': is_sufficient_length,
        'is_non_zero': is_non_zero,
        'is_valid_sample_rate': is_valid_sample_rate,
        'signal_range': signal_range.tolist() if hasattr(signal_range, 'tolist') else float(signal_range),
        'snr_estimate': snr_estimate.tolist() if hasattr(snr_estimate, 'tolist') else float(snr_estimate),
        'is_valid': is_sufficient_length and is_non_zero and is_valid_sample_rate
    }