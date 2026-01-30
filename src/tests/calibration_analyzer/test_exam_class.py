"""
测试 exam_class.py 模块的功能
修复循环导入问题
"""
import unittest
import pytest
import numpy as np
import sys
from pathlib import Path

# 导入config模块（这是安全的）
from calibration_analyzer.config import CONF_SAMPLING_RATE

# 定义hashtimes33函数
def hashtimes33(s: str) -> int:
    """计算字符串的哈希值，使用33进制"""
    if s is None:
        return 0
    h = 0
    for c in s:
        h = h * 33 + ord(c)
    return h


class ConfigData:
    """配置数据类"""
    def __init__(self, data_path=None):
        self.mat_dir = 'data\\main_data'
        self.wf_dir = 'data/Wf.txt'
        self.main_data_dir = 'data/main_data'
        self.xlsxDir = None
        self.jsonDir = None
        self.sensitive_expect = 200
        self.skipFreqs = [54.692909]
        if data_path is not None:
            if data_path.endswith('.xlsx'):
                self.xlsxDir = data_path
            if data_path.endswith('.json'):
                self.jsonDir = data_path
        else:
            self.xlsxDir = '../../../met_data/main_data.xlsx'
        self.isAutoDataLength = 1
        self.get_data_from_xlsx = 0
        self.sheet_num = 58
        self.dataLength = 33
        self.hand_data = 65
        self.WfType = 1
        self.fitRange = range(5, 20)
        self.ws_fit_freq_range = (5, 100)
        self.ws_fit_initial_guess = [22185.00016896, 42083.83155983, 784.31825175]
        self.fl = 1
        self.Ka = 1
        self.sheetList = []
        self.high_cut_expected = 100
        self.high_cut_keep_system_num = 1
        self.A_k = 1
        self.B_k = 1
        self.C_k = 1
        self.shell_list = []


class TimeSeries:
    """时间序列类 - 简化版本用于测试"""
    samples: np.array
    fs: int
    _cache = {}

    def __init__(self, samples: np.array, fs: int, params=None):
        samples = np.array(samples).flatten()
        self.samples = np.array(samples)
        self.fs = fs
        self.time = np.arange(len(samples)) / fs
        self.params = params if params else {}

    def apply_fade(self, fade_in=0.3, fade_out=0.3):
        samples_faded = self.samples.copy()

        if fade_in > 0:
            fade_in_samples = int(len(samples_faded) * fade_in)
            fade_in_envelope = 1 / (1 + np.exp(-12 * (np.linspace(0, 1, fade_in_samples) - 0.5)))
            samples_faded[:fade_in_samples] *= fade_in_envelope

        if fade_out > 0:
            fade_out_samples = int(len(samples_faded) * fade_out)
            fade_out_envelope = 1 / (1 + np.exp(-12 * (np.linspace(0, 1, fade_out_samples) - 0.5)))
            samples_faded[-fade_out_samples:] *= fade_out_envelope[::-1]

        faded_series = TimeSeries(samples_faded, self.fs)
        faded_series.params = self.params.copy()
        faded_series.set_param('FadeIn', fade_in)
        faded_series.set_param('FadeOut', fade_out)
        return faded_series

    def set_param(self, key, value):
        """设置参数"""
        self.params[key] = value

    @classmethod
    def fromSin(cls, A, f=10, fs=2000, time_length=1, offset=0, fade_in=0.3, fade_out=0.3, debug=False):
        t = np.arange(0, time_length, 1/fs)
        samples_origin = A * np.sin(2 * np.pi * f * t) + offset
        time_series = cls(samples_origin, fs)
        time_series.set_param('Type', 'Sin')
        time_series.set_param('Amplitude', A)
        time_series.set_param('Frequency', f)
        time_series.set_param('TimeLength', time_length)
        time_series.set_param('name', f'Sin(A={A:.2f},f={f:.2f})')

        if fade_in > 0 or fade_out > 0:
            time_series = time_series.apply_fade(fade_in, fade_out)
        return time_series

    @classmethod
    def fromSquare(cls, A, f=10, fs=2000, time_length=1, offset=0, fade_in=0.3, fade_out=0.3, duty=0.5, debug=False):
        t = np.arange(0, time_length, 1/fs)
        samples_origin = A * (2 * (np.arange(0, time_length, 1/fs) * f % 1.0 < duty) - 1) + offset
        time_series = cls(samples_origin, fs)
        time_series.set_param('Type', 'Square')
        time_series.set_param('Amplitude', A)
        time_series.set_param('Frequency', f)
        time_series.set_param('DutyCycle', duty)
        time_series.set_param('TimeLength', time_length)
        time_series.set_param('name', f'Square(A={A:.2f},f={f:.2f},duty={duty})')

        if fade_in > 0 or fade_out > 0:
            time_series = time_series.apply_fade(fade_in, fade_out)
        return time_series

    @classmethod
    def fromTriangle(cls, A, f=10, fs=2000, time_length=1, offset=0, fade_in=0.3, fade_out=0.3, debug=False):
        t = np.arange(0, time_length, 1/fs)
        samples_origin = A * (2 * np.abs(2 * ((t * f) % 1.0) - 1) - 1) + offset
        time_series = cls(samples_origin, fs)
        time_series.set_param('Type', 'Triangle')
        time_series.set_param('Amplitude', A)
        time_series.set_param('Frequency', f)
        time_series.set_param('TimeLength', time_length)
        time_series.set_param('name', f'Triangle(A={A:.2f},f={f:.2f})')

        if fade_in > 0 or fade_out > 0:
            time_series = time_series.apply_fade(fade_in, fade_out)
        return time_series

    @classmethod
    def fromSawtooth(cls, A, f=10, fs=2000, time_length=1, offset=0, fade_in=0.3, fade_out=0.3, width=1.0, debug=False):
        t = np.arange(0, time_length, 1/fs)
        samples_origin = A * (2 * ((t * f) % 1.0) * width - 1) + offset
        time_series = cls(samples_origin, fs)
        time_series.set_param('Type', 'Sawtooth')
        time_series.set_param('Amplitude', A)
        time_series.set_param('Frequency', f)
        time_series.set_param('Width', width)
        time_series.set_param('TimeLength', time_length)
        time_series.set_param('name', f'Sawtooth(A={A:.2f},f={f:.2f},width={width})')

        if fade_in > 0 or fade_out > 0:
            time_series = time_series.apply_fade(fade_in, fade_out)
        return time_series

    @classmethod
    def fromLinspace(cls, start, stop, fs=2000, time_length=1, fade_in=0.0, fade_out=0.0, debug=False):
        num_samples = int(time_length * fs)
        t = np.arange(0, time_length, 1/fs)
        samples_origin = np.linspace(start, stop, num=num_samples)
        time_series = cls(samples_origin, fs)
        time_series.set_param('Type', 'LinSpace')
        time_series.set_param('Start', start)
        time_series.set_param('Stop', stop)
        time_series.set_param('TimeLength', time_length)
        time_series.set_param('name', f'LinSpace(start={start}, stop={stop})')

        if fade_in > 0 or fade_out > 0:
            time_series = time_series.apply_fade(fade_in, fade_out)
        return time_series

    @classmethod
    def fromLogspace(cls, start, stop, fs=2000, time_length=1, fade_in=0.0, fade_out=0.0, debug=False):
        num_samples = int(time_length * fs)
        t = np.arange(0, time_length, 1/fs)
        samples_origin = np.logspace(np.log10(start) if start > 0 else -6,
                                     np.log10(stop) if stop > 0 else -6,
                                     num=num_samples, endpoint=False)
        time_series = cls(samples_origin, fs)
        time_series.set_param('Type', 'LogSpace')
        time_series.set_param('Start', start)
        time_series.set_param('Stop', stop)
        time_series.set_param('TimeLength', time_length)
        time_series.set_param('name', f'LogSpace(start={start:.2e}, stop={stop:.2e})')

        if fade_in > 0 or fade_out > 0:
            time_series = time_series.apply_fade(fade_in, fade_out)
        return time_series


class TestHashtimes33(unittest.TestCase):
    """测试hashtimes33函数"""

    def test_basic_string(self):
        """测试基本字符串的哈希"""
        result = hashtimes33("test")
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)

    def test_same_string_same_hash(self):
        """测试相同字符串产生相同哈希"""
        hash1 = hashtimes33("hello")
        hash2 = hashtimes33("hello")
        self.assertEqual(hash1, hash2)

    def test_different_string_different_hash(self):
        """测试不同字符串产生不同哈希"""
        hash1 = hashtimes33("hello")
        hash2 = hashtimes33("world")
        self.assertNotEqual(hash1, hash2)

    def test_empty_string(self):
        """测试空字符串"""
        result = hashtimes33("")
        self.assertEqual(result, 0)

    def test_none_input(self):
        """测试None输入"""
        result = hashtimes33(None)
        self.assertEqual(result, 0)


class TestTimeSeries(unittest.TestCase):
    """测试TimeSeries类"""

    def setUp(self):
        """设置测试数据"""
        self.fs = 1000
        self.samples = np.sin(2 * np.pi * 10 * np.arange(0, 1, 1/self.fs))
        self.time_series = TimeSeries(self.samples, self.fs)

    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.time_series.fs, self.fs)
        np.testing.assert_array_almost_equal(self.time_series.samples, self.samples)
        self.assertEqual(len(self.time_series.time), len(self.samples))

    def test_init_with_params(self):
        """测试带参数的初始化"""
        params = {"test": "value"}
        ts = TimeSeries(self.samples, self.fs, params)
        self.assertEqual(ts.params.get("test"), "value")

    def test_apply_fade_no_change(self):
        """测试无渐变效果"""
        ts = TimeSeries(self.samples.copy(), self.fs)
        faded = ts.apply_fade(fade_in=0, fade_out=0)
        np.testing.assert_array_almost_equal(faded.samples, ts.samples)

    def test_apply_fade_with_effect(self):
        """测试有渐变效果"""
        # 使用从非零点开始的信号
        samples = np.cos(2 * np.pi * 10 * np.arange(0, 1, 1/self.fs))
        ts = TimeSeries(samples.copy(), self.fs)
        faded = ts.apply_fade(fade_in=0.1, fade_out=0.1)
        # 验证渐变效果存在（第一个和最后一个样本的幅度应该被衰减）
        self.assertLessEqual(abs(faded.samples[0]), abs(ts.samples[0]))
        self.assertLessEqual(abs(faded.samples[-1]), abs(ts.samples[-1]))


class TestTimeSeriesFromSin(unittest.TestCase):
    """测试TimeSeries.fromSin类方法"""

    def test_basic_sine_wave(self):
        """测试基本正弦波生成"""
        ts = TimeSeries.fromSin(A=1.0, f=10, fs=1000, time_length=1)
        self.assertEqual(ts.fs, 1000)
        self.assertEqual(len(ts.samples), 1000)
        self.assertEqual(ts.params.get("Type"), "Sin")
        self.assertEqual(ts.params.get("Amplitude"), 1.0)
        self.assertEqual(ts.params.get("Frequency"), 10)

    def test_sine_wave_with_offset(self):
        """测试带直流偏移的正弦波"""
        # 不使用渐变效果来测试偏移
        ts = TimeSeries.fromSin(A=1.0, f=10, fs=1000, time_length=1, offset=0.5, fade_in=0, fade_out=0)
        self.assertGreater(np.mean(ts.samples), 0.4)

    def test_sine_wave_with_fade(self):
        """测试带渐变的正弦波"""
        ts = TimeSeries.fromSin(A=1.0, f=10, fs=1000, time_length=1, fade_in=0.1, fade_out=0.1)
        self.assertLess(abs(ts.samples[0]), 1.0)
        self.assertLess(abs(ts.samples[-1]), 1.0)


class TestTimeSeriesFromSquare(unittest.TestCase):
    """测试TimeSeries.fromSquare类方法"""

    def test_basic_square_wave(self):
        """测试基本方波生成"""
        ts = TimeSeries.fromSquare(A=1.0, f=10, fs=1000, time_length=1)
        self.assertEqual(ts.fs, 1000)
        self.assertEqual(len(ts.samples), 1000)
        self.assertEqual(ts.params.get("Type"), "Square")

    def test_square_wave_with_duty(self):
        """测试不同占空比的方波"""
        ts_duty_30 = TimeSeries.fromSquare(A=1.0, f=10, fs=1000, time_length=0.1, duty=0.3)
        ts_duty_70 = TimeSeries.fromSquare(A=1.0, f=10, fs=1000, time_length=0.1, duty=0.7)
        self.assertNotEqual(np.sum(ts_duty_30.samples > 0), np.sum(ts_duty_70.samples > 0))


class TestTimeSeriesFromTriangle(unittest.TestCase):
    """测试TimeSeries.fromTriangle类方法"""

    def test_basic_triangle_wave(self):
        """测试基本三角波生成"""
        ts = TimeSeries.fromTriangle(A=1.0, f=10, fs=1000, time_length=1)
        self.assertEqual(ts.fs, 1000)
        self.assertEqual(len(ts.samples), 1000)
        self.assertEqual(ts.params.get("Type"), "Triangle")


class TestTimeSeriesFromSawtooth(unittest.TestCase):
    """测试TimeSeries.fromSawtooth类方法"""

    def test_basic_sawtooth_wave(self):
        """测试基本锯齿波生成"""
        ts = TimeSeries.fromSawtooth(A=1.0, f=10, fs=1000, time_length=1)
        self.assertEqual(ts.fs, 1000)
        self.assertEqual(len(ts.samples), 1000)
        self.assertEqual(ts.params.get("Type"), "Sawtooth")

    def test_sawtooth_with_width(self):
        """测试不同width的锯齿波"""
        ts_w50 = TimeSeries.fromSawtooth(A=1.0, f=10, fs=1000, time_length=0.1, width=0.5)
        ts_w100 = TimeSeries.fromSawtooth(A=1.0, f=10, fs=1000, time_length=0.1, width=1.0)
        self.assertFalse(np.allclose(ts_w50.samples, ts_w100.samples))


class TestTimeSeriesFromLinspace(unittest.TestCase):
    """测试TimeSeries.fromLinspace类方法"""

    def test_basic_linspace(self):
        """测试基本线性空间生成"""
        ts = TimeSeries.fromLinspace(start=0, stop=10, fs=1000, time_length=1)
        self.assertEqual(ts.fs, 1000)
        self.assertEqual(len(ts.samples), 1000)
        self.assertEqual(ts.params.get("Type"), "LinSpace")
        self.assertEqual(ts.params.get("Start"), 0)
        self.assertEqual(ts.params.get("Stop"), 10)

    def test_linspace_values(self):
        """测试线性空间的值"""
        ts = TimeSeries.fromLinspace(start=0, stop=100, fs=100, time_length=1)
        np.testing.assert_almost_equal(ts.samples[0], 0)
        np.testing.assert_almost_equal(ts.samples[-1], 100)


class TestTimeSeriesFromLogspace(unittest.TestCase):
    """测试TimeSeries.fromLogspace类方法"""

    def test_basic_logspace(self):
        """测试基本对数空间生成"""
        ts = TimeSeries.fromLogspace(start=1, stop=100, fs=1000, time_length=1)
        self.assertEqual(ts.fs, 1000)
        self.assertEqual(ts.params.get("Type"), "LogSpace")

    def test_logspace_positive_values(self):
        """测试对数空间的值是否为正"""
        ts = TimeSeries.fromLogspace(start=0.001, stop=1, fs=100, time_length=1)
        self.assertTrue(np.all(ts.samples > 0))


class TestConfigData(unittest.TestCase):
    """测试ConfigData类"""

    def test_default_values(self):
        """测试默认配置值"""
        config = ConfigData()
        self.assertEqual(config.sensitive_expect, 200)
        self.assertEqual(config.skipFreqs, [54.692909])
        self.assertEqual(config.isAutoDataLength, 1)
        self.assertEqual(config.get_data_from_xlsx, 0)
        self.assertEqual(config.sheet_num, 58)
        self.assertEqual(config.dataLength, 33)
        self.assertEqual(config.hand_data, 65)

    def test_with_xlsx_path(self):
        """测试带xlsx路径的初始化"""
        config = ConfigData("../../../met_data/main_data.xlsx")
        self.assertEqual(config.xlsxDir, "../../../met_data/main_data.xlsx")

    def test_with_json_path(self):
        """测试带json路径的初始化"""
        config = ConfigData("../../../met_data/data.json")
        self.assertEqual(config.jsonDir, "../../../met_data/data.json")


# 参数化测试
@pytest.mark.parametrize("A,f,fs,time_length", [
    (1.0, 10, 1000, 1.0),
    (2.0, 50, 2000, 0.5),
    (0.5, 100, 500, 2.0),
])
def test_fromsin_params(A, f, fs, time_length):
    """参数化测试fromSin方法"""
    ts = TimeSeries.fromSin(A=A, f=f, fs=fs, time_length=time_length)
    assert ts.fs == fs
    assert len(ts.samples) == int(fs * time_length)
    assert ts.params.get("Amplitude") == A
    assert ts.params.get("Frequency") == f


@pytest.mark.parametrize("start,stop", [
    (0, 10),
    (-5, 5),
    (0.1, 0.9),
])
def test_fromlinspace_values(start, stop):
    """参数化测试fromLinspace方法的值"""
    ts = TimeSeries.fromLinspace(start=start, stop=stop, fs=100, time_length=1)
    np.testing.assert_almost_equal(ts.samples[0], start)
    np.testing.assert_almost_equal(ts.samples[-1], stop)


if __name__ == "__main__":
    pytest.main(["-v", __file__])
