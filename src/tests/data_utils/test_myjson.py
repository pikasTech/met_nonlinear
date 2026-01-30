"""
data_utils.myjson 模块的单元测试

测试 JSON 序列化/反序列化功能，包括：
- 时间戳格式化
- NaN 值处理
- 科学计数法格式化
- 嵌套数据结构处理
"""

import pytest
import io
import datetime
import math
from data_utils.myjson import (
    dumps, loads, load, dump,
    format_float, format_timestamp_number, parse_timestamp_number
)


class TestFormatFloat:
    """Test cases for format_float function."""

    def test_format_float_scientific_notation(self):
        """测试浮点数格式化为科学计数法。"""
        result = format_float(0.005723)
        assert result == "5.7230e-03"

    def test_format_float_large_number(self):
        """测试大数格式化为科学计数法。"""
        result = format_float(1234567.89)
        assert result == "1.2346e06"  # 无 + 号

    def test_format_float_small_number(self):
        """测试小数格式化为科学计数法。"""
        result = format_float(0.000001234)
        assert result == "1.2340e-06"

    def test_format_float_negative(self):
        """测试负数格式化为科学计数法。"""
        result = format_float(-0.005723)
        assert result == "-5.7230e-03"

    def test_format_float_zero(self):
        """测试零值格式化。"""
        result = format_float(0.0)
        assert result == "0.0000e00"  # 无 + 号

    def test_format_float_removes_leading_plus(self):
        """测试科学计数法不包含正号的指数部分。"""
        result = format_float(1.0e+10)
        assert '+' not in result

    def test_format_float_precision(self):
        """测试浮点数精度为4位小数。"""
        result = format_float(3.14159265359)
        assert result == "3.1416e00"  # 无 + 号


class TestFormatTimestampNumber:
    """Test cases for format_timestamp_number function."""

    def test_format_timestamp_number_basic(self):
        """测试时间戳格式化基本功能。"""
        ts = 1733256810.2
        result = format_timestamp_number(ts)
        # 格式为 YYYYMMDDHHMMSS.F
        assert isinstance(result, str)
        assert len(result) == 16  # 14 + '.' + 1 decimal
        assert result[14] == '.'  # 小数点位置

    def test_format_timestamp_number_decimal(self):
        """测试带小数部分的时间戳格式化。"""
        ts = 1733256810.123456
        result = format_timestamp_number(ts)
        # 应该保留一位小数
        assert result.endswith('.1') or result.endswith('.2')

    def test_format_timestamp_number_whole(self):
        """测试整数时间戳格式化。"""
        ts = 1733256810.0
        result = format_timestamp_number(ts)
        assert isinstance(result, str)


class TestParseTimestampNumber:
    """Test cases for parse_timestamp_number function."""

    def test_parse_timestamp_number_basic(self):
        """测试时间戳解析基本功能。"""
        ts_str = "20241203113130.2"
        result = parse_timestamp_number(ts_str)
        assert isinstance(result, float)

    def test_parse_timestamp_number_zero_fraction(self):
        """测试无小数部分的时间戳解析。"""
        ts_str = "20241203113130"
        result = parse_timestamp_number(ts_str)
        assert isinstance(result, float)

    def test_parse_timestamp_number_full_fraction(self):
        """测试完整小数部分的时间戳解析。"""
        ts_str = "20241203113130.123456"
        result = parse_timestamp_number(ts_str)
        assert isinstance(result, float)

    def test_parse_timestamp_number_invalid_format(self):
        """测试无效格式抛出异常。"""
        ts_str = "invalid"
        # 无效格式会抛出 ValueError 异常
        with pytest.raises(ValueError):
            parse_timestamp_number(ts_str)

    def test_parse_timestamp_number_fallback(self):
        """测试时间戳解析回退机制（带日期格式的字符串）。"""
        ts_str = "20241203113130.1"
        result = parse_timestamp_number(ts_str)
        assert isinstance(result, float)


class TestDumpsBasicTypes:
    """Test cases for dumps function with basic types."""

    def test_dumps_dict(self):
        """测试字典序列化。"""
        data = {"key": "value", "num": 123}
        result = dumps(data)
        assert '"key": "value"' in result
        assert '"num": 123' in result

    def test_dumps_list(self):
        """测试列表序列化。"""
        data = [1, 2, 3, "test"]
        result = dumps(data)
        assert result == "[1, 2, 3, \"test\"]"

    def test_dumps_int(self):
        """测试整数序列化。"""
        result = dumps(42)
        assert result == "42"

    def test_dumps_float(self):
        """测试浮点数序列化。"""
        result = dumps(3.1415)
        assert "3.1415" in result.lower()

    def test_dumps_bool_true(self):
        """测试布尔值 True 序列化。"""
        result = dumps(True)
        assert result == "True"  # Python str() 格式

    def test_dumps_bool_false(self):
        """测试布尔值 False 序列化。"""
        result = dumps(False)
        assert result == "False"  # Python str() 格式

    def test_dumps_none(self):
        """测试 None 序列化。"""
        result = dumps(None)
        assert result == "null"

    def test_dumps_string(self):
        """测试字符串序列化。"""
        result = dumps("hello")
        assert result == '"hello"'

    def test_dumps_nested_dict(self):
        """测试嵌套字典序列化。"""
        data = {"outer": {"inner": 123}}
        result = dumps(data)
        assert "outer" in result
        assert "inner" in result


class TestDumpsSpecialValues:
    """Test cases for dumps function with special values."""

    def test_dumps_nan(self):
        """测试 NaN 值序列化。"""
        data = {"value": float('nan')}
        result = dumps(data)
        assert 'nan' in result.lower()

    def test_dumps_timestamp(self):
        """测试时间戳序列化。"""
        ts = 1733256810.2
        data = {"timestamp": ts}
        result = dumps(data)
        # 时间戳应该被格式化为字符串
        assert "timestamp" in result

    def test_dumps_timestamps_list(self):
        """测试时间戳列表序列化。"""
        ts_list = [1733256810.2, 1733256810.1]
        data = {"timestamps": ts_list}
        result = dumps(data)
        assert "timestamps" in result

    def test_dumps_scientific_notation_float(self):
        """测试浮点数科学计数法格式化。"""
        data = {"value": 0.005723}
        result = dumps(data)
        assert "5.7230e-03" in result

    def test_dumps_epoch(self):
        """测试 epoch 值序列化（非时间戳键）。"""
        data = {"epoch": 100}
        result = dumps(data)
        assert result == "{\"epoch\": 100}"


class TestLoadsBasicTypes:
    """Test cases for loads function with basic types."""

    def test_loads_dict(self):
        """测试字典反序列化。"""
        json_str = '{"key": "value", "num": 123}'
        result = loads(json_str)
        assert result["key"] == "value"
        assert result["num"] == 123

    def test_loads_list(self):
        """测试列表反序列化。"""
        json_str = '[1, 2, 3, "test"]'
        result = loads(json_str)
        assert result == [1, 2, 3, "test"]

    def test_loads_int(self):
        """测试整数反序列化。"""
        json_str = "42"
        result = loads(json_str)
        assert result == 42

    def test_loads_float(self):
        """测试浮点数反序列化。"""
        json_str = "3.1415"
        result = loads(json_str)
        assert abs(result - 3.1415) < 0.001

    def test_loads_bool_true(self):
        """测试布尔值 True 反序列化。"""
        json_str = "true"
        result = loads(json_str)
        assert result is True

    def test_loads_bool_false(self):
        """测试布尔值 False 反序列化。"""
        json_str = "false"
        result = loads(json_str)
        assert result is False

    def test_loads_null(self):
        """测试 null 反序列化。"""
        json_str = "null"
        result = loads(json_str)
        assert result is None


class TestLoadsSpecialValues:
    """Test cases for loads function with special values."""

    def test_loads_nan(self):
        """测试 NaN 值反序列化。"""
        json_str = '{"value": "nan"}'
        result = loads(json_str)
        assert math.isnan(result["value"])

    def test_loads_timestamp(self):
        """测试时间戳反序列化。"""
        json_str = '{"timestamp": "20241203113130.2"}'
        result = loads(json_str)
        assert isinstance(result["timestamp"], float)

    def test_loads_epoch_integer(self):
        """测试 epoch 值反序列化为整数。"""
        json_str = '{"epoch": 100}'
        result = loads(json_str)
        assert result["epoch"] == 100
        assert isinstance(result["epoch"], int)

    def test_loads_scientific_notation(self):
        """测试科学计数法数值反序列化。"""
        json_str = '{"value": "5.7230e-03"}'
        result = loads(json_str)
        assert abs(result["value"] - 0.005723) < 0.0001


class TestLoadsNested:
    """Test cases for loads function with nested structures."""

    def test_loads_nested_dict(self):
        """测试嵌套字典反序列化。"""
        json_str = '{"outer": {"inner": 123, "data": "test"}}'
        result = loads(json_str)
        assert result["outer"]["inner"] == 123
        assert result["outer"]["data"] == "test"

    def test_loads_nested_list(self):
        """测试嵌套列表反序列化。"""
        json_str = '[[1, 2], [3, 4], [5, 6]]'
        result = loads(json_str)
        assert result == [[1, 2], [3, 4], [5, 6]]

    def test_loads_complex_nested(self):
        """测试复杂嵌套结构反序列化。"""
        json_str = '''
        {
            "data": {
                "timestamps": ["20241203113130.1", "20241203113130.2"],
                "values": [1.1, 2.2, 3.3],
                "nested": {
                    "epoch": 100,
                    "nan_value": "nan"
                }
            }
        }
        '''
        result = loads(json_str)
        assert isinstance(result["data"]["timestamps"][0], float)
        assert result["data"]["nested"]["epoch"] == 100
        assert math.isnan(result["data"]["nested"]["nan_value"])


class TestLoadDumpFile:
    """Test cases for load and dump file operations."""

    def test_dump_and_load_roundtrip(self):
        """测试 dump 和 load 完整往返。"""
        original_data = {
            "values": [0.001, 0.002, 0.003],
            "timestamp": 1733256810.5,
            "name": "test_data"
        }

        fp = io.StringIO()
        dump(original_data, fp)
        fp.seek(0)

        loaded_data = load(fp)
        assert loaded_data["name"] == original_data["name"]

    def test_dump_file_with_nan(self):
        """测试包含 NaN 的数据写入。"""
        data = {"value": float('nan'), "normal": 123}
        fp = io.StringIO()
        dump(data, fp)
        fp.seek(0)

        loaded = load(fp)
        assert math.isnan(loaded["value"])

    def test_dump_file_with_nested_structure(self):
        """测试嵌套结构写入。"""
        data = {
            "layer1": {
                "timestamps": [1733256810.1, 1733256810.2],
                "values": {"a": 1.0, "b": 2.0}
            }
        }
        fp = io.StringIO()
        dump(data, fp)
        fp.seek(0)

        loaded = load(fp)
        assert loaded["layer1"]["values"]["a"] == 1.0


class TestRoundtrip:
    """Test cases for dumps/loads roundtrip functionality."""

    def test_roundtrip_dict(self):
        """测试字典往返序列化。"""
        original = {"key": "value", "num": 42}
        json_str = dumps(original)
        result = loads(json_str)
        assert result["key"] == original["key"]
        assert result["num"] == original["num"]

    def test_roundtrip_float_precision(self):
        """测试浮点数往返精度。"""
        original = {"value": 0.005723}
        json_str = dumps(original)
        result = loads(json_str)
        assert abs(result["value"] - original["value"]) < 0.0001

    def test_roundtrip_nan(self):
        """测试 NaN 往返。"""
        original = {"value": float('nan')}
        json_str = dumps(original)
        result = loads(json_str)
        assert math.isnan(result["value"])

    def test_roundtrip_nested(self):
        """测试嵌套结构往返。"""
        original = {
            "outer": {
                "inner": [1, 2, 3],
                "data": {"x": 1.0}
            }
        }
        json_str = dumps(original)
        result = loads(json_str)
        assert result["outer"]["inner"] == original["outer"]["inner"]
        assert result["outer"]["data"]["x"] == original["outer"]["data"]["x"]


class TestEdgeCases:
    """Edge case tests for myjson functions."""

    def test_empty_dict(self):
        """测试空字典。"""
        result = dumps({})
        assert result == "{}"

    def test_empty_list(self):
        """测试空列表。"""
        result = dumps([])
        assert result == "[]"

    def test_unicode_string(self):
        """测试包含 Unicode 的字符串。"""
        data = {"text": "中文测试"}
        result = dumps(data)
        # Unicode 被转义为 \u 格式
        assert "\\u4e2d\\u6587\\u6d4b\\u8bd5" in result

    def test_special_chars_in_string(self):
        """测试包含特殊字符的字符串。"""
        data = {"text": 'line1\nline2\ttab'}
        result = dumps(data)
        # 特殊字符应该被正确转义
        assert "line1" in result

    def test_large_number(self):
        """测试大数值。"""
        data = {"value": 1e20}
        result = dumps(data)
        assert "1.0000e20" in result  # 无 + 号

    def test_very_small_number(self):
        """测试极小数值。"""
        data = {"value": 1e-20}
        result = dumps(data)
        assert "1.0000e-20" in result

    def test_negative_nan(self):
        """测试负 NaN（如果可能）。"""
        data = {"value": float('nan')}
        # NaN 序列化应该不报错
        result = dumps(data)
        assert 'nan' in result.lower()
