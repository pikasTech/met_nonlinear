"""
偏置分析器单元测试

使用pytest测试偏置分析算法的准确性和鲁棒性
"""

import pytest
import numpy as np
from typing import Tuple, Dict

# 导入测试信号生成器
from tests.inference.fixtures.bias_test_signals import (
    generate_pure_dc_signal,
    generate_dc_with_sine,
    generate_transient_signal,
    generate_multi_frequency_signal,
    generate_noisy_signal,
    generate_drift_signal,
    create_test_signal_suite
)

# 导入偏置分析器
from inference.analysis.bias_analyzer import (
    SteadyStateBiasAnalyzer,
    FrequencyDomainBiasAnalyzer,
    AutoBiasAnalyzer,
    ChannelBiasAnalyzer
)


class TestSteadyStateBiasAnalyzer:
    """稳态段提取法测试"""
    
    def test_pure_dc_signal(self):
        """测试纯DC信号"""
        # 生成测试信号
        dc_level = 2.5
        data, sample_rate = generate_pure_dc_signal(dc_level=dc_level, n_channels=1)
        
        # 创建分析器
        analyzer = SteadyStateBiasAnalyzer(steady_ratio=0.3)
        
        # 计算偏置
        bias = analyzer.calculate_bias(data[:, 0], sample_rate)
        
        # 验证结果
        assert abs(bias - dc_level) < 0.001, f"期望偏置{dc_level}，实际{bias}"
    
    def test_with_transient(self):
        """测试带瞬态响应的信号"""
        # 生成瞬态信号
        initial = 0.0
        final = 3.0
        data, sample_rate = generate_transient_signal(
            initial_level=initial,
            final_level=final,
            transient_duration=0.1,
            n_samples=10000,
            n_channels=1
        )
        
        # 创建分析器，使用较大的稳态比例
        analyzer = SteadyStateBiasAnalyzer(steady_ratio=0.5)
        
        # 计算偏置
        bias = analyzer.calculate_bias(data[:, 0], sample_rate)
        
        # 验证结果（应该接近最终值）
        assert abs(bias - final) < 0.01, f"期望偏置{final}，实际{bias}"
    
    def test_oscillating_signal(self):
        """测试持续振荡信号"""
        # 生成DC + 正弦波
        dc_level = 1.5
        data, sample_rate = generate_dc_with_sine(
            dc_level=dc_level,
            sine_amplitude=0.5,
            n_channels=1
        )
        
        # 创建分析器
        analyzer = SteadyStateBiasAnalyzer(steady_ratio=0.3)
        
        # 计算偏置
        bias = analyzer.calculate_bias(data[:, 0], sample_rate)
        
        # 对于正弦波，稳态平均应该接近DC电平
        assert abs(bias - dc_level) < 0.05, f"期望偏置{dc_level}，实际{bias}"
    
    def test_parameter_sensitivity(self):
        """测试参数敏感性"""
        # 生成带漂移的信号
        data, sample_rate = generate_drift_signal(
            initial_dc=1.0,
            drift_rate=0.1,
            n_samples=10000,
            n_channels=1,
            drift_type='linear'
        )
        
        # 测试不同的steady_ratio
        ratios = [0.1, 0.3, 0.5]
        biases = []
        
        for ratio in ratios:
            analyzer = SteadyStateBiasAnalyzer(steady_ratio=ratio)
            bias = analyzer.calculate_bias(data[:, 0], sample_rate)
            biases.append(bias)
        
        # 验证：更大的ratio应该导致更高的偏置（因为线性漂移）
        assert biases[0] < biases[1] < biases[2], f"偏置应该递增: {biases}"
    
    def test_stability_analysis(self):
        """测试稳定性分析功能"""
        # 生成瞬态信号
        data, sample_rate = generate_transient_signal(n_channels=1)
        
        analyzer = SteadyStateBiasAnalyzer()
        
        # 分析稳定性
        stability_info = analyzer.analyze_segment_stability(data[:, 0])
        
        # 验证返回结构
        assert 'segments' in stability_info
        assert 'most_stable_segment' in stability_info
        assert 'recommended_steady_ratio' in stability_info
        
        # 最稳定的段应该在后期
        if stability_info['most_stable_segment']:
            assert stability_info['most_stable_segment']['start_ratio'] > 0.5
    
    def test_edge_cases(self):
        """测试边界条件"""
        # 测试极短信号
        short_data = np.array([1.0, 1.1, 1.2, 1.3, 1.4])
        analyzer = SteadyStateBiasAnalyzer(steady_ratio=0.5)
        bias = analyzer.calculate_bias(short_data, 1000.0)
        assert isinstance(bias, float)
        
        # 测试常数信号
        const_data = np.ones(1000) * 2.5
        bias = analyzer.calculate_bias(const_data, 1000.0)
        assert abs(bias - 2.5) < 1e-10
        
        # 测试零信号
        zero_data = np.zeros(1000)
        bias = analyzer.calculate_bias(zero_data, 1000.0)
        assert abs(bias) < 1e-10


class TestFrequencyDomainBiasAnalyzer:
    """频域滤波法测试"""
    
    def test_pure_dc_signal(self):
        """测试纯DC信号"""
        # 生成测试信号
        dc_level = 2.5
        data, sample_rate = generate_pure_dc_signal(dc_level=dc_level, n_channels=1)
        
        # 创建分析器
        analyzer = FrequencyDomainBiasAnalyzer(dc_bandwidth=1.0)
        
        # 计算偏置
        bias = analyzer.calculate_bias(data[:, 0], sample_rate)
        
        # 验证结果
        assert abs(bias - dc_level) < 0.001, f"期望偏置{dc_level}，实际{bias}"
    
    def test_multi_frequency(self):
        """测试多频率信号"""
        # 生成多频率信号
        dc_level = 2.0
        data, sample_rate = generate_multi_frequency_signal(
            dc_level=dc_level,
            frequencies=[50, 150, 300],
            amplitudes=[0.3, 0.2, 0.1],
            n_channels=1
        )
        
        # 创建分析器
        analyzer = FrequencyDomainBiasAnalyzer(dc_bandwidth=10.0)
        
        # 计算偏置
        bias = analyzer.calculate_bias(data[:, 0], sample_rate)
        
        # 验证结果（应该准确提取DC分量）
        assert abs(bias - dc_level) < 0.01, f"期望偏置{dc_level}，实际{bias}"
    
    def test_bandwidth_effect(self):
        """测试带宽参数的影响"""
        # 生成带低频成分的信号
        dc_level = 1.5
        low_freq = 0.5  # 0.5Hz低频
        data, sample_rate = generate_dc_with_sine(
            dc_level=dc_level,
            sine_amplitude=0.3,
            sine_frequency=low_freq,
            n_channels=1
        )
        
        # 测试不同带宽
        bandwidths = [0.1, 1.0, 5.0]
        biases = []
        
        for bw in bandwidths:
            analyzer = FrequencyDomainBiasAnalyzer(dc_bandwidth=bw)
            bias = analyzer.calculate_bias(data[:, 0], sample_rate)
            biases.append(bias)
        
        # 更窄的带宽应该更接近纯DC
        assert abs(biases[0] - dc_level) < abs(biases[2] - dc_level)
    
    def test_window_functions(self):
        """测试不同窗函数的效果"""
        # 生成测试信号
        dc_level = 2.0
        data, sample_rate = generate_dc_with_sine(dc_level=dc_level, n_channels=1)
        
        windows = ['hann', 'hamming', 'blackman', None]
        biases = []
        
        for window in windows:
            analyzer = FrequencyDomainBiasAnalyzer(dc_bandwidth=1.0, window=window)
            bias = analyzer.calculate_bias(data[:, 0], sample_rate)
            biases.append(bias)
        
        # 所有窗函数的结果应该相近
        for bias in biases:
            assert abs(bias - dc_level) < 0.05, f"窗函数{window}的偏置{bias}偏离期望值{dc_level}"
    
    def test_spectrum_analysis(self):
        """测试频谱分析功能"""
        # 生成多频率信号
        data, sample_rate = generate_multi_frequency_signal(
            frequencies=[50, 150],
            amplitudes=[0.3, 0.2],
            n_channels=1
        )
        
        analyzer = FrequencyDomainBiasAnalyzer()
        
        # 分析频谱
        spectrum_info = analyzer.analyze_spectrum(data[:, 0], sample_rate)
        
        # 验证返回结构
        assert 'dc_magnitude' in spectrum_info
        assert 'dominant_frequencies' in spectrum_info
        assert 'total_energy' in spectrum_info
        assert 'dc_energy_ratio' in spectrum_info
        
        # 应该检测到两个主要频率
        assert len(spectrum_info['dominant_frequencies']) >= 2
        
        # 检查频率是否正确
        detected_freqs = [f[0] for f in spectrum_info['dominant_frequencies']]
        assert any(abs(f - 50) < 1 for f in detected_freqs)
        assert any(abs(f - 150) < 1 for f in detected_freqs)
    
    def test_spectral_leakage(self):
        """测试频谱泄漏处理"""
        # 生成非整数周期的正弦波
        sample_rate = 1000.0
        duration = 1.0
        n_samples = int(sample_rate * duration)
        frequency = 50.3  # 非整数周期
        
        t = np.arange(n_samples) / sample_rate
        dc_level = 1.0
        data = dc_level + 0.5 * np.sin(2 * np.pi * frequency * t)
        
        # 比较有窗和无窗的结果
        analyzer_no_window = FrequencyDomainBiasAnalyzer(window=None)
        analyzer_with_window = FrequencyDomainBiasAnalyzer(window='hann')
        
        bias_no_window = analyzer_no_window.calculate_bias(data, sample_rate)
        bias_with_window = analyzer_with_window.calculate_bias(data, sample_rate)
        
        # 两种方法都应该接近真实DC值
        assert abs(bias_no_window - dc_level) < 0.1
        assert abs(bias_with_window - dc_level) < 0.1


class TestAutoBiasAnalyzer:
    """自动选择方法测试"""
    
    def test_method_selection_transient(self):
        """测试瞬态信号的方法选择"""
        # 生成强瞬态信号
        data, sample_rate = generate_transient_signal(
            initial_level=0.0,
            final_level=5.0,
            transient_duration=0.3,
            n_channels=1
        )
        
        analyzer = AutoBiasAnalyzer()
        bias = analyzer.calculate_bias(data[:, 0], sample_rate)
        
        # 应该选择稳态段方法
        assert 'steady_state' in analyzer.get_method_name()
        assert abs(bias - 5.0) < 0.1
    
    def test_method_selection_multi_freq(self):
        """测试多频率信号的方法选择"""
        # 生成多频率信号
        data, sample_rate = generate_multi_frequency_signal(
            dc_level=2.0,
            frequencies=[30, 60, 120, 240],
            amplitudes=[0.2, 0.15, 0.1, 0.05],
            n_channels=1
        )
        
        analyzer = AutoBiasAnalyzer()
        bias = analyzer.calculate_bias(data[:, 0], sample_rate)
        
        # 应该选择频域方法
        assert 'frequency_domain' in analyzer.get_method_name()
        assert abs(bias - 2.0) < 0.05
    
    def test_complex_signal(self):
        """测试复杂信号"""
        # 使用预定义的测试信号套件
        test_signals = create_test_signal_suite()
        
        # 测试复杂信号
        data, sample_rate, info = test_signals['complex']
        
        analyzer = AutoBiasAnalyzer()
        
        # 分析所有通道
        biases = []
        for ch in range(data.shape[1]):
            bias = analyzer.calculate_bias(data[:, ch], sample_rate)
            biases.append(bias)
        
        # 验证结果合理性
        assert all(0 < b < 5 for b in biases), f"偏置应该在合理范围内: {biases}"


class TestChannelBiasAnalyzer:
    """通道偏置误差分析器测试"""
    
    def test_single_channel_analysis(self):
        """测试单通道分析"""
        # 生成参考和对比信号
        ref_dc = 2.5
        comp_dc = 2.48
        
        ref_data, sample_rate = generate_pure_dc_signal(dc_level=ref_dc, n_channels=1)
        comp_data, _ = generate_pure_dc_signal(dc_level=comp_dc, n_channels=1)
        
        # 创建分析器
        analyzer = ChannelBiasAnalyzer(method='frequency_domain')
        
        # 分析偏置误差
        result = analyzer.analyze_bias_errors(ref_data, comp_data, sample_rate)
        
        # 验证结果
        assert result['channel_count'] == 1
        assert len(result['bias_errors']) == 1
        
        bias_error = result['bias_errors'][0]
        expected_error = ref_dc - comp_dc
        assert abs(bias_error['bias_error'] - expected_error) < 0.001
    
    def test_multi_channel_analysis(self):
        """测试多通道分析"""
        # 生成多通道信号，每个通道有不同的偏置
        n_channels = 5
        ref_levels = [1.0, 1.5, 2.0, 2.5, 3.0]
        comp_levels = [0.98, 1.52, 1.97, 2.53, 2.95]
        
        # 构建数据
        n_samples = 10000
        ref_data = np.zeros((n_samples, n_channels))
        comp_data = np.zeros((n_samples, n_channels))
        
        for ch in range(n_channels):
            ref_data[:, ch] = ref_levels[ch]
            comp_data[:, ch] = comp_levels[ch]
        
        # 分析
        analyzer = ChannelBiasAnalyzer(method='steady_state')
        result = analyzer.analyze_bias_errors(ref_data, comp_data, 10000.0)
        
        # 验证
        assert result['channel_count'] == n_channels
        assert len(result['bias_errors']) == n_channels
        
        # 检查每个通道的误差
        for ch in range(n_channels):
            expected_error = ref_levels[ch] - comp_levels[ch]
            actual_error = result['bias_errors'][ch]['bias_error']
            assert abs(actual_error - expected_error) < 0.001
    
    def test_multilayer_analysis(self):
        """测试多层分析"""
        # 模拟3层网络，每层4个通道
        n_layers = 3
        n_channels = 4
        n_samples = 5000
        sample_rate = 10000.0
        
        layer_data_pairs = []
        
        for layer in range(n_layers):
            # 每层的偏置误差逐渐增大
            ref_base = 2.0
            error_base = 0.01 * (layer + 1)
            
            ref_data = np.ones((n_samples, n_channels)) * ref_base
            comp_data = np.ones((n_samples, n_channels)) * (ref_base - error_base)
            
            # 每个通道添加不同的偏移
            for ch in range(n_channels):
                ref_data[:, ch] += ch * 0.1
                comp_data[:, ch] += ch * 0.1
            
            layer_info = {'layer': layer + 1, 'name': f'Layer_{layer + 1}'}
            layer_data_pairs.append((ref_data, comp_data, sample_rate, layer_info))
        
        # 分析
        analyzer = ChannelBiasAnalyzer(method='frequency_domain')
        result = analyzer.analyze_multilayer_bias(layer_data_pairs)
        
        # 验证结果结构
        assert 'layer_results' in result
        assert 'bias_error_matrix' in result
        assert 'formatted' in result
        assert 'global_statistics' in result
        
        # 验证矩阵形状（使用新格式）
        formatted = result['formatted']
        assert formatted['layer_count'] == n_layers
        assert len(formatted['channels_per_layer']) == n_layers
        assert all(ch == n_channels for ch in formatted['channels_per_layer'])
        
        # 验证偏置误差矩阵
        bias_matrix = np.array(result['bias_error_matrix'])
        assert bias_matrix.shape == (n_layers, n_channels)
        
        # 验证误差值（每层应该有不同的误差水平）
        layer_means = np.mean(np.abs(bias_matrix), axis=1)
        assert layer_means[0] < layer_means[1] < layer_means[2]
    
    def test_different_methods(self):
        """测试不同方法的一致性"""
        # 生成稳定的测试信号
        dc_level = 2.0
        data, sample_rate = generate_pure_dc_signal(dc_level=dc_level, n_channels=3)
        
        # 添加小的偏差
        comp_data = data - 0.05
        
        methods = ['steady_state', 'frequency_domain', 'auto']
        results = {}
        
        for method in methods:
            analyzer = ChannelBiasAnalyzer(method=method)
            result = analyzer.analyze_bias_errors(data, comp_data, sample_rate)
            results[method] = result
        
        # 所有方法的结果应该相近
        for method in methods:
            mean_error = results[method]['summary']['mean_bias_error']
            assert abs(mean_error - 0.05) < 0.001, f"{method}方法的误差不准确"


@pytest.fixture
def sample_wave_data():
    """创建示例WaveData对象用于测试"""
    from calibration_analyzer.wavedata import WaveData, WaveRecord
    
    wave_data = WaveData()
    
    # 添加多个记录
    for i in range(3):
        data, sample_rate = generate_pure_dc_signal(
            dc_level=1.0 + i * 0.5,
            n_channels=4,
            n_samples=1000
        )
        
        record = WaveRecord(
            data=data,
            sample_rate=sample_rate,
            channel_names=[f'Ch{j}' for j in range(4)],
            record_id=f'record_{i}'
        )
        wave_data.add_record(record)
    
    return wave_data


def test_wavedata_analysis(sample_wave_data):
    """测试WaveData对象的分析"""
    analyzer = FrequencyDomainBiasAnalyzer()
    
    # 分析WaveData
    result = analyzer.analyze_wavedata(sample_wave_data)
    
    # 验证结果结构
    assert 'method' in result
    assert 'parameters' in result
    assert 'records' in result
    
    # 验证记录数量
    assert len(result['records']) == len(sample_wave_data.records)
    
    # 验证每个记录的分析结果
    for i, record_result in enumerate(result['records']):
        assert record_result['n_channels'] == 4
        assert len(record_result['channels']) == 4
        
        # 验证偏置值（应该接近设置的DC电平）
        expected_dc = 1.0 + i * 0.5
        for ch_result in record_result['channels']:
            assert abs(ch_result['bias'] - expected_dc) < 0.01


if __name__ == '__main__':
    pytest.main([__file__, '-v'])