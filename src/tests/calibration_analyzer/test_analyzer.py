"""
测试 analyzer.py 模块的功能
"""
import unittest
import pytest
import numpy as np
import json
import tempfile
import os
import sys
from pathlib import Path

# 确保可以导入模块
root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

try:
    from calibration_analyzer.analyzer import (
        ChannelAnalyzeResult,
        DataAnalyzeResult,
        DataAnalyzeResultList,
        shift_phase,
        extract_values_to_dict
    )
    from calibration_analyzer.config import (
        CONF_SAMPLING_RATE,
        CONF_RAW_VOLTAGE_RATEIO,
        CONF_DURATION_PERIOD_MIN,
        CONF_DURATION_PERIOD_MAX,
        CONF_USING_ANTI_ALIASING,
        CONF_USING_HANNING,
        CONF_FREQ_RATIO,
        CONF_USING_IFFT
    )
    from calibration_analyzer.datastruct import DataRecord, DataRecordList, DataIdentifierParam
except ImportError as e:
    pytestmark = pytest.mark.skip(reason=f"无法导入analyzer模块: {e}")


class TestChannelAnalyzeResult(unittest.TestCase):
    """测试ChannelAnalyzeResult类"""

    def setUp(self):
        """设置测试数据"""
        self.sampling_rate = CONF_SAMPLING_RATE
        # 创建简单的正弦波数据
        t = np.arange(0, 1, 1/self.sampling_rate)
        freq = 10  # 10Hz
        self.channel_data = np.sin(2 * np.pi * freq * t)
        self.result = ChannelAnalyzeResult(
            channel=self.channel_data,
            sampling_rate=self.sampling_rate
        )

    def test_init_with_data(self):
        """测试带数据初始化"""
        result = ChannelAnalyzeResult(
            channel=[1.0, 2.0, 3.0],
            sampling_rate=1000
        )
        self.assertEqual(result.sampling_rate, 1000)
        self.assertEqual(len(result.channel), 3)

    def test_init_without_data(self):
        """测试不带数据初始化"""
        result = ChannelAnalyzeResult()
        # 不带数据初始化时，channel 属性不存在
        self.assertFalse(hasattr(result, 'channel'))

    def test_analyze_fft_basic(self):
        """测试FFT分析基本功能"""
        self.result.analyze_fft(freq_select=10, start_s=0, time_s=1)
        self.assertIsNotNone(self.result.fft)
        self.assertIsNotNone(self.result.fft_abs)
        self.assertIsNotNone(self.result.fft_freq)

    def test_get_index(self):
        """测试频率索引获取"""
        self.result.analyze_fft(freq_select=10, start_s=0, time_s=1)
        index = self.result.get_index(10)
        self.assertIsInstance(index, (int, np.integer))
        self.assertGreaterEqual(index, 0)

    def test_get_power_single_frequency(self):
        """测试单频率功率计算"""
        self.result.analyze_fft(freq_select=10, start_s=0, time_s=1)
        power = self.result.get_power(freq_select=10)
        self.assertIsInstance(power, (float, np.floating))
        self.assertGreater(power, 0)

    def test_get_power_with_ratio(self):
        """测试带频率比的功率计算"""
        self.result.analyze_fft(freq_select=10, start_s=0, time_s=1)
        power = self.result.get_power(freq_select=10, freq_ratio=1.1)
        self.assertIsInstance(power, (float, np.floating))
        self.assertGreater(power, 0)

    def test_get_phase(self):
        """测试相位计算"""
        self.result.analyze_fft(freq_select=10, start_s=0, time_s=1)
        self.result.analyze_indicators(freq_select=10)
        phase = self.result.get_phase(freq_select=10)
        self.assertIsInstance(phase, (float, np.floating))
        # 相位可以是任意值（正或负），取决于信号特性

    def test_get_amp(self):
        """测试幅度计算"""
        self.result.analyze_fft(freq_select=10, start_s=0, time_s=1)
        amp = self.result.get_amp(freq_select=10)
        self.assertIsInstance(amp, (float, np.floating, type(None)))

    def test_get_ifft(self):
        """测试逆FFT计算"""
        self.result.analyze_fft(freq_select=10, start_s=0, time_s=1)
        self.assertIsNotNone(self.result.ifft)
        self.assertEqual(len(self.result.ifft), len(self.result.fft))

    def test_analyze_indicators(self):
        """测试分析指标计算"""
        self.result.analyze_fft(freq_select=10, start_s=0, time_s=1)
        self.result.analyze_indicators(freq_select=10)

        self.assertTrue(hasattr(self.result, 'thd'))
        self.assertTrue(hasattr(self.result, 'main_freq_amplitude'))
        self.assertTrue(hasattr(self.result, 'distortion'))
        self.assertTrue(hasattr(self.result, 'phase'))

    def test_analyze_indicators_with_ratio(self):
        """测试带频率比的指标分析"""
        self.result.analyze_fft(freq_select=10, start_s=0, time_s=1)
        self.result.analyze_indicators(freq_select=10, freq_ratio=1.1)

        self.assertIsNotNone(self.result.thd)
        self.assertIsNotNone(self.result.main_freq_amplitude)

    def test_to_dict(self):
        """测试转换为字典"""
        self.result.analyze_fft(freq_select=10, start_s=0, time_s=1)
        self.result.analyze_indicators(freq_select=10)

        result_dict = self.result.to_dict()

        self.assertIsInstance(result_dict, dict)
        self.assertIn('sampling_rate', result_dict)
        self.assertIn('start_s', result_dict)
        self.assertIn('time_s', result_dict)
        self.assertIn('main_freq_amplitude', result_dict)
        self.assertIn('distortion', result_dict)
        self.assertIn('thd', result_dict)
        self.assertIn('phase', result_dict)

    def test_load_from_dict(self):
        """测试从字典加载"""
        # 先获取字典
        self.result.analyze_fft(freq_select=10, start_s=0, time_s=1)
        self.result.analyze_indicators(freq_select=10)
        original_dict = self.result.to_dict()

        # 创建新对象并加载
        new_result = ChannelAnalyzeResult()
        new_result.load_from_dict(original_dict)

        self.assertEqual(new_result.sampling_rate, self.result.sampling_rate)
        self.assertEqual(new_result.start_s, self.result.start_s)
        self.assertEqual(new_result.time_s, self.result.time_s)


class TestDataAnalyzeResult(unittest.TestCase):
    """测试DataAnalyzeResult类"""

    def setUp(self):
        """设置测试数据"""
        self.sampling_rate = CONF_SAMPLING_RATE

        # 创建DataRecord
        param = DataIdentifierParam("var=1,freq=10")
        param.params['freq'] = '10'

        t = np.arange(0, 1, 1/self.sampling_rate)
        ch1 = np.sin(2 * np.pi * 10 * t).tolist()
        ch2 = np.sin(2 * np.pi * 10 * t + np.pi/4).tolist()  # 45度相移

        self.record = DataRecord(param, ch1, ch2)

    def test_init_with_record(self):
        """测试带记录初始化"""
        result = DataAnalyzeResult(record=self.record, sample_rate=self.sampling_rate)
        self.assertIsNotNone(result.ch1Result)
        self.assertIsNotNone(result.ch2Result)
        self.assertIsNotNone(result.ch1IntegrateResult)

    def test_init_without_record(self):
        """测试不带记录初始化"""
        result = DataAnalyzeResult()
        # 不带记录初始化时，record 属性不存在
        self.assertFalse(hasattr(result, 'record'))

    def test_analyze_delta_ifft(self):
        """测试IFFT差分分析"""
        result = DataAnalyzeResult(record=self.record, sample_rate=self.sampling_rate)
        result.analyze()

        gain, phi = result.analyze_delta_ifft(result.ch1Result, result.ch2Result)
        self.assertIsInstance(gain, (float, np.floating))
        self.assertIsInstance(phi, (float, np.floating))

    def test_analyze_delta(self):
        """测试差分分析"""
        result = DataAnalyzeResult(record=self.record, sample_rate=self.sampling_rate)
        result.analyze()

        self.assertTrue(hasattr(result, 'gain'))
        self.assertTrue(hasattr(result, 'phase'))
        self.assertTrue(hasattr(result, 'gain_integrate'))
        self.assertTrue(hasattr(result, 'phase_integrate'))

    def test_analyze(self):
        """测试完整分析流程"""
        result = DataAnalyzeResult(record=self.record, sample_rate=self.sampling_rate)
        result.analyze(start_s=0, time_s=1, gain_ratio=1.0)

        self.assertIsNotNone(result.ch1Result.fft)
        self.assertIsNotNone(result.ch2Result.fft)

    def test_to_dict(self):
        """测试转换为字典"""
        result = DataAnalyzeResult(record=self.record, sample_rate=self.sampling_rate)
        result.analyze()

        result_dict = result.to_dict()

        self.assertIsInstance(result_dict, dict)
        self.assertIn('param', result_dict)
        self.assertIn('gain_ratio', result_dict)
        self.assertIn('freq', result_dict)
        self.assertIn('gain', result_dict)
        self.assertIn('phase', result_dict)
        self.assertIn('ch1', result_dict)
        self.assertIn('ch2', result_dict)

    def test_load_from_dict(self):
        """测试从字典加载"""
        result = DataAnalyzeResult(record=self.record, sample_rate=self.sampling_rate)
        result.analyze()
        original_dict = result.to_dict()

        new_result = DataAnalyzeResult()
        new_result.load_from_dict(original_dict)

        self.assertEqual(new_result.freq, result.freq)
        self.assertEqual(new_result.gain, result.gain)


class TestDataAnalyzeResultList(unittest.TestCase):
    """测试DataAnalyzeResultList类"""

    def setUp(self):
        """设置测试数据"""
        self.sampling_rate = CONF_SAMPLING_RATE
        self.result_list = DataAnalyzeResultList()

        # 添加几个结果
        for freq in [5, 10, 20]:
            param = DataIdentifierParam(f"var=1,freq={freq}")
            param.params['freq'] = str(freq)

            t = np.arange(0, 1, 1/self.sampling_rate)
            ch1 = np.sin(2 * np.pi * freq * t).tolist()
            ch2 = np.sin(2 * np.pi * freq * t + np.pi/6).tolist()

            record = DataRecord(param, ch1, ch2)
            result = DataAnalyzeResult(record=record, sample_rate=self.sampling_rate)
            result.analyze()
            self.result_list.append(result)

    def test_append(self):
        """测试添加结果"""
        initial_count = len(self.result_list.dataAnalyzeResults)

        param = DataIdentifierParam("var=1,freq=50")
        param.params['freq'] = '50'
        t = np.arange(0, 1, 1/self.sampling_rate)
        ch1 = np.sin(2 * np.pi * 50 * t).tolist()
        ch2 = np.sin(2 * np.pi * 50 * t).tolist()
        record = DataRecord(param, ch1, ch2)
        result = DataAnalyzeResult(record=record, sample_rate=self.sampling_rate)
        result.analyze()

        self.result_list.append(result)
        self.assertEqual(len(self.result_list.dataAnalyzeResults), initial_count + 1)

    def test_to_dict(self):
        """测试转换为字典"""
        result_dict = self.result_list.to_dict()

        self.assertIsInstance(result_dict, dict)
        self.assertIn('dataAnalyzeResults', result_dict)
        self.assertEqual(len(result_dict['dataAnalyzeResults']), 3)

    def test_dump_to_json(self):
        """测试导出为JSON"""
        json_data = self.result_list.dump_to_json()

        self.assertIsInstance(json_data, str)
        parsed = json.loads(json_data)
        self.assertIn('dataAnalyzeResults', parsed)

    def test_load_from_dict(self):
        """测试从字典加载"""
        original_dict = self.result_list.to_dict()

        new_list = DataAnalyzeResultList()
        new_list.load_from_dict(original_dict)

        self.assertEqual(len(new_list.dataAnalyzeResults), 3)

    def test_load_from_json(self):
        """测试从JSON加载"""
        json_data = self.result_list.dump_to_json()

        new_list = DataAnalyzeResultList()
        new_list.load_from_json(json_data)

        self.assertEqual(len(new_list.dataAnalyzeResults), 3)

    def test_get_gain_integrate(self):
        """测试获取积分增益"""
        gains = self.result_list.get_gain_integrate()

        self.assertIsInstance(gains, list)
        self.assertEqual(len(gains), 3)

    def test_get_gain(self):
        """测试获取增益"""
        gains = self.result_list.get_gain()

        self.assertIsInstance(gains, list)
        self.assertEqual(len(gains), 3)

    def test_get_freq(self):
        """测试获取频率"""
        freqs = self.result_list.get_freq()

        self.assertIsInstance(freqs, list)
        self.assertEqual(len(freqs), 3)


class TestShiftPhase(unittest.TestCase):
    """测试shift_phase函数"""

    def test_basic_phase_shift(self):
        """测试基本相位平移"""
        # 创建测试相位数据
        phase_array = np.array([0, 90, 180, 270])
        shifted = shift_phase(phase_array, period=360)

        self.assertEqual(len(shifted), len(phase_array))

    def test_phase_shift_with_manual_offset(self):
        """测试带手动偏移的相位平移"""
        phase_array = np.array([0, 90, 180, 270])
        shifted = shift_phase(phase_array, period=360, phase_shift_manual=45)

        self.assertEqual(len(shifted), len(phase_array))

    def test_phase_shift_single_value(self):
        """测试单值相位"""
        phase_array = np.array([45.0])
        shifted = shift_phase(phase_array)

        self.assertEqual(len(shifted), 1)


class TestExtractValuesToDict(unittest.TestCase):
    """测试extract_values_to_dict函数"""

    def test_basic_extraction(self):
        """测试基本提取"""
        input_str = "A10B20C30.5"
        result = extract_values_to_dict(input_str)

        self.assertIsInstance(result, dict)
        self.assertIn('A', result)
        self.assertIn('B', result)
        self.assertIn('C', result)
        self.assertEqual(result['A'], 10)
        self.assertEqual(result['B'], 20)
        self.assertEqual(result['C'], 30.5)

    def test_float_extraction(self):
        """测试浮点数提取"""
        input_str = "X1.5Y2.5Z3.0"
        result = extract_values_to_dict(input_str)

        self.assertEqual(result['X'], 1.5)
        self.assertEqual(result['Y'], 2.5)
        self.assertEqual(result['Z'], 3.0)

    def test_integer_extraction(self):
        """测试整数提取"""
        input_str = "P100Q200"
        result = extract_values_to_dict(input_str)

        self.assertEqual(result['P'], 100)
        self.assertEqual(result['Q'], 200)

    def test_empty_string(self):
        """测试空字符串"""
        result = extract_values_to_dict("")
        self.assertEqual(result, {})

    def test_no_match(self):
        """测试无匹配情况"""
        result = extract_values_to_dict("abc123")
        self.assertEqual(result, {})


class TestAnalyzeFileIntegration(unittest.TestCase):
    """测试analyze_file函数的集成场景"""

    def test_analyze_result_serialization(self):
        """测试分析结果的序列化循环"""
        # 创建DataRecordList
        param = DataIdentifierParam("var=1,freq=10")
        param.params['freq'] = '10'

        t = np.arange(0, 1, 1/CONF_SAMPLING_RATE)
        ch1 = np.sin(2 * np.pi * 10 * t).tolist()
        ch2 = np.sin(2 * np.pi * 10 * t + np.pi/4).tolist()

        record = DataRecord(param, ch1, ch2)
        record_list = DataRecordList()
        record_list.load_from_data_records([record])

        # 转换为JSON再加载
        json_data = json.dumps(record_list.to_dict())
        loaded_list = DataRecordList()
        loaded_list.load_from_dict(json.loads(json_data))

        self.assertEqual(len(loaded_list.dataRecords), 1)


# 参数化测试
@pytest.mark.parametrize("freq_select,start_s,time_s", [
    (10, 0, 1),
    (20, 0.5, 2),
    (50, 0, 0.5),
])
def test_channel_analyze_fft_parametrized(freq_select, start_s, time_s):
    """参数化测试FFT分析"""
    result = ChannelAnalyzeResult(
        channel=np.sin(2 * np.pi * freq_select * np.arange(0, 1, 1/CONF_SAMPLING_RATE)),
        sampling_rate=CONF_SAMPLING_RATE
    )
    result.analyze_fft(freq_select=freq_select, start_s=start_s, time_s=time_s)
    assert result.fft is not None
    assert result.fft_abs is not None


if __name__ == "__main__":
    pytest.main(["-v", __file__])
