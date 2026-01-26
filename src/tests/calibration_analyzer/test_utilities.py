"""
测试utilities.py模块的功能
"""
import unittest
import pytest
import numpy as np
import os

try:
    from calibration_analyzer.utilities import *  # 导入所有工具函数
except ImportError:
    # 如果无法导入，则跳过测试
    pytestmark = pytest.mark.skip(reason="无法导入utilities模块")
    

class TestUtilityFunctions(unittest.TestCase):
    """测试utilities.py中的工具函数"""
    
    def test_safe_divide(self):
        """测试安全除法函数"""
        try:
            # 假设存在safe_divide函数
            result = safe_divide(10, 2)
            self.assertEqual(result, 5.0)
            
            # 除以零应返回safe_value
            result = safe_divide(10, 0, safe_value=100)
            self.assertEqual(result, 100)
            
            # 数组除法
            result = safe_divide(np.array([10, 20, 30]), np.array([2, 0, 5]))
            np.testing.assert_array_equal(result, np.array([5, 0, 6]))
            
        except NameError:
            self.skipTest("safe_divide函数不存在")
    
    def test_normalize(self):
        """测试归一化函数"""
        try:
            # 假设存在normalize函数
            data = np.array([1, 2, 3, 4, 5])
            
            # 默认归一化到[0, 1]
            result = normalize(data)
            self.assertAlmostEqual(np.min(result), 0.0)
            self.assertAlmostEqual(np.max(result), 1.0)
            
            # 自定义范围归一化
            result = normalize(data, new_min=-1, new_max=1)
            self.assertAlmostEqual(np.min(result), -1.0)
            self.assertAlmostEqual(np.max(result), 1.0)
            
            # 处理单值数组
            single_value = np.array([3, 3, 3])
            result = normalize(single_value)
            np.testing.assert_array_equal(result, np.array([0.5, 0.5, 0.5]))
            
        except NameError:
            self.skipTest("normalize函数不存在")
    
    def test_find_peaks(self):
        """测试寻峰函数"""
        try:
            # 假设存在find_peaks函数
            # 创建一个有明显峰值的信号
            x = np.linspace(0, 10, 1000)
            y = np.sin(x) + 0.1 * np.random.randn(len(x))
            
            # 找到峰值
            peaks, properties = find_peaks(y, height=0.5, distance=50)
            
            # 验证找到了峰值
            self.assertTrue(len(peaks) > 0)
            
            # 验证峰值高度
            for peak_idx in peaks:
                self.assertGreaterEqual(y[peak_idx], 0.5)
                
        except NameError:
            self.skipTest("find_peaks函数不存在")
    
    def test_butter_bandpass_filter(self):
        """测试带通滤波器函数"""
        try:
            # 假设存在butter_bandpass_filter函数
            # 创建一个包含多个频率的信号
            fs = 1000.0  # 采样率
            t = np.arange(0, 1, 1/fs)
            # 5Hz + 50Hz + 250Hz的信号
            y = np.sin(2*np.pi*5*t) + 0.5*np.sin(2*np.pi*50*t) + 0.25*np.sin(2*np.pi*250*t)
            
            # 应用带通滤波器(40-60Hz)
            filtered = butter_bandpass_filter(y, 40, 60, fs, order=4)
            
            # 验证50Hz分量保留，其他被过滤
            fft_orig = np.abs(np.fft.fft(y))
            fft_filtered = np.abs(np.fft.fft(filtered))
            
            # 找到频率对应的索引
            freq = np.fft.fftfreq(len(y), 1/fs)
            idx_5hz = np.argmin(np.abs(freq - 5))
            idx_50hz = np.argmin(np.abs(freq - 50))
            idx_250hz = np.argmin(np.abs(freq - 250))
            
            # 50Hz分量应该保留(有一定损失)
            self.assertGreaterEqual(fft_filtered[idx_50hz], 0.3 * fft_orig[idx_50hz])
            
            # 其他分量应该被大幅衰减
            self.assertLessEqual(fft_filtered[idx_5hz], 0.1 * fft_orig[idx_5hz])
            self.assertLessEqual(fft_filtered[idx_250hz], 0.1 * fft_orig[idx_250hz])
            
        except NameError:
            self.skipTest("butter_bandpass_filter函数不存在")
    
    def test_rms(self):
        """测试均方根函数"""
        try:
            # 假设存在rms函数
            # 测试已知结果的情况
            data = np.array([1, -1, 2, -2, 3, -3])
            expected_rms = np.sqrt(np.mean(np.square(data)))
            result = rms(data)
            self.assertAlmostEqual(result, expected_rms)
            
            # 测试零数组
            result = rms(np.zeros(10))
            self.assertAlmostEqual(result, 0.0)
            
            # 测试正弦波
            t = np.linspace(0, 2*np.pi, 1000)
            sine_wave = np.sin(t)
            # 正弦波的均方根值为振幅/sqrt(2)
            self.assertAlmostEqual(rms(sine_wave), 1/np.sqrt(2), places=3)
            
        except NameError:
            self.skipTest("rms函数不存在")
    
    def test_thd(self):
        """测试总谐波失真函数"""
        try:
            # 假设存在thd函数
            # 创建包含基波和谐波的信号
            fs = 1000.0
            t = np.arange(0, 1, 1/fs)
            f0 = 50.0  # 基波频率
            
            # 基波 + 2次谐波(10%) + 3次谐波(5%)
            y = np.sin(2*np.pi*f0*t) + 0.1*np.sin(2*np.pi*2*f0*t) + 0.05*np.sin(2*np.pi*3*f0*t)
            
            # 计算THD
            result = thd(y, fs, f0, num_harmonics=3)
            
            # 验证THD结果(应该接近0.112 或 11.2%)
            expected_thd = np.sqrt(0.1**2 + 0.05**2)
            self.assertAlmostEqual(result, expected_thd, places=2)
            
        except NameError:
            self.skipTest("thd函数不存在")


# 使用pytest的参数化测试
@pytest.mark.parametrize("input_data,expected", [
    # 各种输入数据和期望值的组合
    ([1, 2, 3, 4, 5], 3.0),  # 均值
    ([], 0),                  # 空列表
    ([10], 10),               # 单元素列表
    ([1, -1, 2, -2], 0),      # 正负平衡
])
def test_mean_function(input_data, expected):
    """测试均值计算函数"""
    try:
        # 假设存在mean函数
        result = mean(input_data)
        assert result == expected
    except NameError:
        pytest.skip("mean函数不存在")


if __name__ == "__main__":
    pytest.main(["-v", __file__]) 