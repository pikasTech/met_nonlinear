"""
测试 datastruct.py 模块的功能
修复循环导入问题
"""
import unittest
import pytest
import numpy as np
import json
import tempfile
import os
import sys
from pathlib import Path

# 直接导入所需模块，避免循环导入
from scipy.integrate import cumulative_trapezoid
import base64
import traceback
from typing import List, Optional, Union

# 导入config模块获取采样率
from calibration_analyzer.config import CONF_SAMPLING_RATE


def integrate_signal_remove_dc(signal: list,
                               sampling_rate: float) -> np.ndarray:
    """积分信号并去除直流分量"""
    time_interval = 1.0 / sampling_rate
    mean = np.mean(signal)
    ac = np.array(signal) - mean
    integrated_signal = cumulative_trapezoid(ac, dx=time_interval, initial=0)
    integrated_signal += mean
    return integrated_signal


class DataIdentifierParam:
    """数据标识符参数类"""
    def __init__(self, content: str):
        self.content = content
        self.params = {}
        self.parse()

    def parse(self):
        if self.content is None:
            return
        for param in self.content.split(','):
            try:
                key, value = param.split('=')
            except Exception as e:
                continue
            self.params[key] = value


class DataRecord:
    """数据记录类"""
    def __init__(self,
                 param: DataIdentifierParam,
                 ch1: Union[List[float], np.ndarray],
                 ch2: Union[List[float], np.ndarray],
                 ch1_integrate: Optional[Union[List[float], np.ndarray]] = None):
        self.param = param
        self.ch1 = np.array(ch1, dtype=np.float64)
        self.ch2 = np.array(ch2, dtype=np.float64)
        if ch1_integrate is not None:
            self.ch1_integrate = np.array(ch1_integrate, dtype=np.float64)
        else:
            self.ch1_integrate = integrate_signal_remove_dc(self.ch1, CONF_SAMPLING_RATE)

    def to_dict(self) -> dict:
        return {
            "param": self.param.params,
            "ch1": self._encode_array(self.ch1),
            "ch2": self._encode_array(self.ch2),
            "ch1_integrate": self._encode_array(self.ch1_integrate)
        }

    @staticmethod
    def _encode_array(array: np.ndarray) -> str:
        return base64.b64encode(array.tobytes()).decode('utf-8')

    @staticmethod
    def _decode_array(encoded_data: str, dtype: type = np.float64) -> np.ndarray:
        data = base64.b64decode(encoded_data)
        return np.frombuffer(data, dtype=dtype)

    @staticmethod
    def load_from_dict(data: dict) -> 'DataRecord':
        param = DataIdentifierParam(None)
        param.params = data['param']
        return DataRecord(
            param,
            DataRecord._decode_array(data['ch1']),
            DataRecord._decode_array(data['ch2']),
            DataRecord._decode_array(data['ch1_integrate'])
        )


class DataRecordList:
    """数据记录列表类"""
    def __init__(self):
        self.dataRecords: list = []

    def to_dict(self):
        return {
            "data": [dataRecord.to_dict() for dataRecord in self.dataRecords]
        }

    def load_from_dict(self, data: dict):
        self.dataRecords = []
        for dataRecord in data['data']:
            self.dataRecords.append(DataRecord.load_from_dict(dataRecord))

    def load_from_data_records(self, dataRecords: list):
        self.dataRecords = dataRecords

    def load_from_json(self, json_data: str):
        data = json.loads(json_data)
        self.load_from_dict(data)

    def dump_to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=1)


class ByteFile:
    """字节文件类"""
    def __init__(self, bytes_data: bytes):
        self.bytes = bytes_data
        self.pos = 0

    def read(self, size: int) -> bytes:
        if self.pos + size > len(self.bytes):
            return b""
        self.pos += size
        return self.bytes[self.pos - size:self.pos]

    def __len__(self) -> int:
        return len(self.bytes)


class TestDataIdentifierParam(unittest.TestCase):
    """测试DataIdentifierParam类"""

    def test_parse_valid_content(self):
        """测试解析有效的参数字符串"""
        param = DataIdentifierParam("var=1,freq=10,ctl=end")
        self.assertEqual(param.params.get("var"), "1")
        self.assertEqual(param.params.get("freq"), "10")
        self.assertEqual(param.params.get("ctl"), "end")

    def test_parse_empty_content(self):
        """测试解析空内容"""
        param = DataIdentifierParam(None)
        self.assertEqual(param.params, {})

    def test_parse_invalid_content(self):
        """测试解析无效的参数字符串"""
        param = DataIdentifierParam("valid=good,invalid_without_equals")
        self.assertEqual(param.params.get("valid"), "good")
        self.assertNotIn("invalid_without_equals", param.params)


class TestIntegrateSignalRemoveDc(unittest.TestCase):
    """测试integrate_signal_remove_dc函数"""

    def test_basic_integration(self):
        """测试基本积分功能"""
        signal = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        sampling_rate = 1000.0
        result = integrate_signal_remove_dc(signal, sampling_rate)
        self.assertEqual(len(result), len(signal))

    def test_integration_removes_dc(self):
        """测试积分后直流分量被去除"""
        signal = np.array([10.0, 11.0, 12.0, 13.0, 14.0])
        sampling_rate = 1000.0
        result = integrate_signal_remove_dc(signal, sampling_rate)
        self.assertEqual(len(result), len(signal))

    def test_integration_with_zeros(self):
        """测试零值信号积分"""
        signal = np.zeros(100)
        sampling_rate = 1000.0
        result = integrate_signal_remove_dc(signal, sampling_rate)
        np.testing.assert_array_almost_equal(result, np.zeros(100))


class TestDataRecord(unittest.TestCase):
    """测试DataRecord类"""

    def setUp(self):
        """设置测试数据"""
        self.param = DataIdentifierParam("var=1,freq=10")
        self.ch1 = [1.0, 2.0, 3.0, 4.0, 5.0]
        self.ch2 = [0.5, 1.0, 1.5, 2.0, 2.5]

    def test_init_with_ch1_integrate(self):
        """测试初始化时传入ch1_integrate"""
        ch1_integrate = [0.1, 0.2, 0.3, 0.4, 0.5]
        record = DataRecord(self.param, self.ch1, self.ch2, ch1_integrate)
        np.testing.assert_array_almost_equal(record.ch1, self.ch1)
        np.testing.assert_array_almost_equal(record.ch2, self.ch2)
        np.testing.assert_array_almost_equal(record.ch1_integrate, ch1_integrate)

    def test_init_without_ch1_integrate(self):
        """测试初始化时不传入ch1_integrate（自动计算）"""
        record = DataRecord(self.param, self.ch1, self.ch2)
        np.testing.assert_array_almost_equal(record.ch1, self.ch1)
        np.testing.assert_array_almost_equal(record.ch2, self.ch2)
        self.assertEqual(len(record.ch1_integrate), len(self.ch1))

    def test_to_dict(self):
        """测试转换为字典"""
        record = DataRecord(self.param, self.ch1, self.ch2)
        data_dict = record.to_dict()
        self.assertIn("param", data_dict)
        self.assertIn("ch1", data_dict)
        self.assertIn("ch2", data_dict)
        self.assertIn("ch1_integrate", data_dict)
        self.assertEqual(data_dict["param"]["var"], "1")

    def test_encode_decode_array(self):
        """测试数组编码解码"""
        original = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        encoded = DataRecord._encode_array(original)
        decoded = DataRecord._decode_array(encoded)
        np.testing.assert_array_almost_equal(original, decoded)

    def test_load_from_dict(self):
        """测试从字典加载"""
        record = DataRecord(self.param, self.ch1, self.ch2)
        data_dict = record.to_dict()
        loaded_record = DataRecord.load_from_dict(data_dict)
        np.testing.assert_array_almost_equal(loaded_record.ch1, record.ch1)
        np.testing.assert_array_almost_equal(loaded_record.ch2, record.ch2)
        self.assertEqual(loaded_record.param.params.get("var"), "1")


class TestDataRecordList(unittest.TestCase):
    """测试DataRecordList类"""

    def setUp(self):
        """设置测试数据"""
        self.record_list = DataRecordList()
        for i in range(3):
            param = DataIdentifierParam(f"var={i},freq={10*i}")
            ch1 = [float(i)] * 5
            ch2 = [float(i+1)] * 5
            self.record_list.dataRecords.append(
                DataRecord(param, ch1, ch2)
            )

    def test_to_dict(self):
        """测试转换为字典"""
        data_dict = self.record_list.to_dict()
        self.assertIn("data", data_dict)
        self.assertEqual(len(data_dict["data"]), 3)

    def test_load_from_data_records(self):
        """测试从数据记录列表加载"""
        new_list = DataRecordList()
        records = self.record_list.dataRecords
        new_list.load_from_data_records(records)
        self.assertEqual(len(new_list.dataRecords), 3)

    def test_load_from_dict(self):
        """测试从字典加载"""
        data_dict = self.record_list.to_dict()
        new_list = DataRecordList()
        new_list.load_from_dict(data_dict)
        self.assertEqual(len(new_list.dataRecords), 3)

    def test_load_from_json(self):
        """测试从JSON字符串加载"""
        data_dict = self.record_list.to_dict()
        json_str = json.dumps(data_dict)
        new_list = DataRecordList()
        new_list.load_from_json(json_str)
        self.assertEqual(len(new_list.dataRecords), 3)

    def test_dump_to_json(self):
        """测试导出为JSON字符串"""
        json_str = self.record_list.dump_to_json()
        self.assertIsInstance(json_str, str)
        parsed = json.loads(json_str)
        self.assertIn("data", parsed)


class TestByteFile(unittest.TestCase):
    """测试ByteFile类"""

    def test_init(self):
        """测试初始化"""
        data = b"Hello, World!"
        byte_file = ByteFile(data)
        self.assertEqual(len(byte_file), len(data))

    def test_read_partial(self):
        """测试部分读取"""
        data = b"Hello, World!"
        byte_file = ByteFile(data)
        result = byte_file.read(5)
        self.assertEqual(result, b"Hello")

    def test_read_beyond_end(self):
        """测试读取超出数据长度"""
        data = b"Hi"
        byte_file = ByteFile(data)
        result = byte_file.read(10)
        self.assertEqual(result, b"")

    def test_read_all(self):
        """测试完整读取"""
        data = b"Test data"
        byte_file = ByteFile(data)

        # 第一次读取5字节
        result1 = byte_file.read(5)
        self.assertEqual(result1, b"Test ")

        # 读取剩余4字节
        result2 = byte_file.read(4)
        self.assertEqual(result2, b"data")

    def test_len(self):
        """测试长度方法"""
        data = b"1234567890"
        byte_file = ByteFile(data)
        self.assertEqual(len(byte_file), 10)


# 参数化测试
@pytest.mark.parametrize("input_signal,sampling_rate", [
    ([1.0, 2.0, 3.0], 1000.0),
    ([0.0, 0.0, 0.0], 2000.0),
    ([1, 2, 3, 4, 5], 500.0),
])
def test_integrate_signal_remove_dc_params(input_signal, sampling_rate):
    """参数化测试integrate_signal_remove_dc函数"""
    result = integrate_signal_remove_dc(input_signal, sampling_rate)
    assert len(result) == len(input_signal)


@pytest.mark.parametrize("ch1_data,ch2_data", [
    ([1.0, 2.0, 3.0], [0.5, 1.0, 1.5]),
    ([10, 20, 30], [5, 10, 15]),
])
def test_data_record_creation(ch1_data, ch2_data):
    """参数化测试DataRecord创建"""
    param = DataIdentifierParam("test=1")
    record = DataRecord(param, ch1_data, ch2_data)
    np.testing.assert_array_almost_equal(record.ch1, ch1_data)
    np.testing.assert_array_almost_equal(record.ch2, ch2_data)


if __name__ == "__main__":
    pytest.main(["-v", __file__])
