"""
偏置测试信号生成器

生成各种测试信号用于验证偏置分析算法
"""

import numpy as np
from typing import Dict, Tuple, Optional


def generate_pure_dc_signal(dc_level: float = 2.5, 
                          n_samples: int = 10000,
                          n_channels: int = 3,
                          noise_level: float = 0.0) -> Tuple[np.ndarray, float]:
    """
    生成纯DC信号
    
    参数:
        dc_level: DC电平
        n_samples: 样本数
        n_channels: 通道数
        noise_level: 噪声水平（相对于DC电平）
        
    返回:
        (data, sample_rate): 数据和采样率
    """
    sample_rate = 10000.0  # 10kHz
    
    # 生成纯DC信号
    data = np.ones((n_samples, n_channels)) * dc_level
    
    # 添加噪声
    if noise_level > 0:
        noise = np.random.normal(0, dc_level * noise_level, (n_samples, n_channels))
        data += noise
    
    return data, sample_rate


def generate_dc_with_sine(dc_level: float = 1.0,
                         sine_amplitude: float = 0.5,
                         sine_frequency: float = 50.0,
                         n_samples: int = 10000,
                         n_channels: int = 3,
                         phase_shift: bool = True) -> Tuple[np.ndarray, float]:
    """
    生成DC + 正弦波信号
    
    参数:
        dc_level: DC电平
        sine_amplitude: 正弦波幅度
        sine_frequency: 正弦波频率 (Hz)
        n_samples: 样本数
        n_channels: 通道数
        phase_shift: 是否在不同通道间添加相位偏移
        
    返回:
        (data, sample_rate): 数据和采样率
    """
    sample_rate = 10000.0  # 10kHz
    t = np.arange(n_samples) / sample_rate
    
    data = np.zeros((n_samples, n_channels))
    
    for ch in range(n_channels):
        # 每个通道可以有不同的相位
        phase = (2 * np.pi * ch / n_channels) if phase_shift else 0
        data[:, ch] = dc_level + sine_amplitude * np.sin(2 * np.pi * sine_frequency * t + phase)
    
    return data, sample_rate


def generate_transient_signal(initial_level: float = 0.0,
                            final_level: float = 2.0,
                            transient_duration: float = 0.1,
                            n_samples: int = 10000,
                            n_channels: int = 3,
                            transient_type: str = 'exponential') -> Tuple[np.ndarray, float]:
    """
    生成带瞬态响应的信号
    
    参数:
        initial_level: 初始电平
        final_level: 最终电平
        transient_duration: 瞬态持续时间 (秒)
        n_samples: 样本数
        n_channels: 通道数
        transient_type: 瞬态类型 ('exponential', 'linear', 'step')
        
    返回:
        (data, sample_rate): 数据和采样率
    """
    sample_rate = 10000.0  # 10kHz
    t = np.arange(n_samples) / sample_rate
    transient_samples = int(transient_duration * sample_rate)
    
    data = np.zeros((n_samples, n_channels))
    
    for ch in range(n_channels):
        if transient_type == 'exponential':
            # 指数响应
            tau = transient_duration / 3  # 时间常数
            transient = initial_level + (final_level - initial_level) * (1 - np.exp(-t[:transient_samples] / tau))
            data[:transient_samples, ch] = transient
            data[transient_samples:, ch] = final_level
            
        elif transient_type == 'linear':
            # 线性响应
            transient = np.linspace(initial_level, final_level, transient_samples)
            data[:transient_samples, ch] = transient
            data[transient_samples:, ch] = final_level
            
        elif transient_type == 'step':
            # 阶跃响应
            data[:, ch] = initial_level
            data[transient_samples:, ch] = final_level
        
        # 为每个通道添加略微不同的最终值
        data[transient_samples:, ch] += ch * 0.01
    
    return data, sample_rate


def generate_multi_frequency_signal(dc_level: float = 1.0,
                                  frequencies: list = [50, 150, 300],
                                  amplitudes: list = [0.3, 0.2, 0.1],
                                  n_samples: int = 10000,
                                  n_channels: int = 3) -> Tuple[np.ndarray, float]:
    """
    生成多频率成分信号
    
    参数:
        dc_level: DC电平
        frequencies: 频率列表 (Hz)
        amplitudes: 对应的幅度列表
        n_samples: 样本数
        n_channels: 通道数
        
    返回:
        (data, sample_rate): 数据和采样率
    """
    sample_rate = 10000.0  # 10kHz
    t = np.arange(n_samples) / sample_rate
    
    if len(frequencies) != len(amplitudes):
        raise ValueError("频率和幅度列表长度必须相同")
    
    data = np.ones((n_samples, n_channels)) * dc_level
    
    for ch in range(n_channels):
        for freq, amp in zip(frequencies, amplitudes):
            # 每个通道的每个频率成分有不同的相位
            phase = 2 * np.pi * ch * freq / sample_rate
            data[:, ch] += amp * np.sin(2 * np.pi * freq * t + phase)
    
    return data, sample_rate


def generate_noisy_signal(base_signal_type: str = 'dc',
                        snr_db: float = 20.0,
                        n_samples: int = 10000,
                        n_channels: int = 3,
                        **kwargs) -> Tuple[np.ndarray, float]:
    """
    生成带噪声的信号
    
    参数:
        base_signal_type: 基础信号类型 ('dc', 'sine', 'multi_freq')
        snr_db: 信噪比 (dB)
        n_samples: 样本数
        n_channels: 通道数
        kwargs: 传递给基础信号生成器的参数
        
    返回:
        (data, sample_rate): 数据和采样率
    """
    # 生成基础信号
    if base_signal_type == 'dc':
        data, sample_rate = generate_pure_dc_signal(n_samples=n_samples, n_channels=n_channels, **kwargs)
    elif base_signal_type == 'sine':
        data, sample_rate = generate_dc_with_sine(n_samples=n_samples, n_channels=n_channels, **kwargs)
    elif base_signal_type == 'multi_freq':
        data, sample_rate = generate_multi_frequency_signal(n_samples=n_samples, n_channels=n_channels, **kwargs)
    else:
        raise ValueError(f"未知的基础信号类型: {base_signal_type}")
    
    # 计算信号功率
    signal_power = np.mean(data**2, axis=0)
    
    # 根据SNR计算噪声功率
    snr_linear = 10**(snr_db / 10)
    noise_power = signal_power / snr_linear
    
    # 生成噪声
    for ch in range(n_channels):
        noise = np.random.normal(0, np.sqrt(noise_power[ch]), n_samples)
        data[:, ch] += noise
    
    return data, sample_rate


def generate_drift_signal(initial_dc: float = 1.0,
                        drift_rate: float = 0.1,
                        n_samples: int = 10000,
                        n_channels: int = 3,
                        drift_type: str = 'linear') -> Tuple[np.ndarray, float]:
    """
    生成带漂移的信号
    
    参数:
        initial_dc: 初始DC电平
        drift_rate: 漂移速率 (V/s)
        n_samples: 样本数
        n_channels: 通道数
        drift_type: 漂移类型 ('linear', 'exponential', 'sinusoidal')
        
    返回:
        (data, sample_rate): 数据和采样率
    """
    sample_rate = 10000.0  # 10kHz
    t = np.arange(n_samples) / sample_rate
    
    data = np.zeros((n_samples, n_channels))
    
    for ch in range(n_channels):
        if drift_type == 'linear':
            # 线性漂移
            data[:, ch] = initial_dc + drift_rate * t
            
        elif drift_type == 'exponential':
            # 指数漂移
            tau = 1.0 / drift_rate
            data[:, ch] = initial_dc * np.exp(t / tau)
            
        elif drift_type == 'sinusoidal':
            # 正弦漂移（模拟温度变化等周期性漂移）
            drift_period = n_samples / sample_rate / 2  # 半个信号长度为一个周期
            data[:, ch] = initial_dc + drift_rate * np.sin(2 * np.pi * t / drift_period)
        
        # 每个通道有略微不同的漂移率
        data[:, ch] *= (1 + ch * 0.05)
    
    return data, sample_rate


def generate_complex_signal(n_samples: int = 10000,
                          n_channels: int = 3) -> Tuple[np.ndarray, float]:
    """
    生成复杂的混合信号，包含多种成分
    
    参数:
        n_samples: 样本数
        n_channels: 通道数
        
    返回:
        (data, sample_rate): 数据和采样率
    """
    sample_rate = 10000.0  # 10kHz
    t = np.arange(n_samples) / sample_rate
    
    data = np.zeros((n_samples, n_channels))
    
    for ch in range(n_channels):
        # DC成分
        dc = 2.5 + ch * 0.1
        
        # 瞬态响应（前10%）
        transient_samples = n_samples // 10
        transient = np.exp(-5 * t[:transient_samples])
        
        # 多个频率成分
        f1 = 50 + ch * 10  # 基频
        f2 = 150 + ch * 20  # 二次谐波
        f3 = 300 + ch * 30  # 三次谐波
        
        # 构建信号
        data[:, ch] = dc
        data[:transient_samples, ch] += transient
        data[:, ch] += 0.3 * np.sin(2 * np.pi * f1 * t)
        data[:, ch] += 0.15 * np.sin(2 * np.pi * f2 * t + np.pi/4)
        data[:, ch] += 0.05 * np.sin(2 * np.pi * f3 * t + np.pi/2)
        
        # 添加少量噪声
        data[:, ch] += np.random.normal(0, 0.02, n_samples)
        
        # 添加慢速漂移
        data[:, ch] += 0.01 * t
    
    return data, sample_rate


def create_test_signal_suite() -> Dict[str, Tuple[np.ndarray, float, Dict]]:
    """
    创建完整的测试信号套件
    
    返回:
        Dict: 信号名称 -> (数据, 采样率, 描述信息)
    """
    test_signals = {}
    
    # 1. 纯DC信号
    data, sr = generate_pure_dc_signal(dc_level=2.5, n_channels=3)
    test_signals['pure_dc'] = (data, sr, {
        'description': '纯DC信号',
        'expected_bias': [2.5, 2.5, 2.5],
        'suitable_methods': ['frequency_domain', 'steady_state']
    })
    
    # 2. DC + 噪声
    data, sr = generate_pure_dc_signal(dc_level=1.0, noise_level=0.1, n_channels=3)
    test_signals['dc_with_noise'] = (data, sr, {
        'description': 'DC信号带10%噪声',
        'expected_bias': [1.0, 1.0, 1.0],
        'tolerance': 0.05,
        'suitable_methods': ['frequency_domain', 'steady_state']
    })
    
    # 3. DC + 正弦波
    data, sr = generate_dc_with_sine(dc_level=1.5, sine_amplitude=0.5, n_channels=3)
    test_signals['dc_with_sine'] = (data, sr, {
        'description': 'DC + 50Hz正弦波',
        'expected_bias': [1.5, 1.5, 1.5],
        'suitable_methods': ['frequency_domain']
    })
    
    # 4. 瞬态响应
    data, sr = generate_transient_signal(initial_level=0.0, final_level=3.0, n_channels=3)
    test_signals['transient'] = (data, sr, {
        'description': '指数瞬态响应',
        'expected_bias': [3.0, 3.01, 3.02],  # 每个通道略有不同
        'suitable_methods': ['steady_state']
    })
    
    # 5. 多频率信号
    data, sr = generate_multi_frequency_signal(dc_level=2.0, n_channels=3)
    test_signals['multi_freq'] = (data, sr, {
        'description': '多频率成分信号',
        'expected_bias': [2.0, 2.0, 2.0],
        'suitable_methods': ['frequency_domain']
    })
    
    # 6. 线性漂移
    data, sr = generate_drift_signal(initial_dc=1.0, drift_rate=0.1, n_channels=3)
    test_signals['linear_drift'] = (data, sr, {
        'description': '线性漂移信号',
        'expected_bias_range': [1.0, 2.0],  # 偏置在此范围内
        'suitable_methods': ['frequency_domain']
    })
    
    # 7. 复杂信号
    data, sr = generate_complex_signal(n_channels=3)
    test_signals['complex'] = (data, sr, {
        'description': '复杂混合信号',
        'suitable_methods': ['auto']
    })
    
    return test_signals


# 用于pytest的fixture
def get_test_signals():
    """获取测试信号（用于pytest fixture）"""
    return create_test_signal_suite()