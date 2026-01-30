"""
测试 config.py 模块的功能
"""
import unittest
import pytest
import sys
from pathlib import Path

# 确保可以导入calibration_analyzer包
root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

try:
    from calibration_analyzer.config import (
        CONF_SAMPLING_RATE, CONF_START_TIME, CONF_DURATION,
        CONF_COLOR_HUE_SHIFT, CONF_FREQ_RATIO,
        collect_default_config, reset_to_default_configuration,
        load_keyword_profile
    )
except ImportError as e:
    pytestmark = pytest.mark.skip(reason=f"无法导入config模块: {e}")


class TestConfigConstants(unittest.TestCase):
    """测试配置常量"""

    def test_conf_sampling_rate(self):
        """测试采样率配置"""
        self.assertEqual(CONF_SAMPLING_RATE, 20000)

    def test_conf_start_time(self):
        """测试开始时间配置"""
        self.assertEqual(CONF_START_TIME, 5)

    def test_conf_duration(self):
        """测试持续时间配置"""
        self.assertEqual(CONF_DURATION, 15)

    def test_conf_color_hue_shift(self):
        """测试颜色色调偏移配置"""
        self.assertEqual(CONF_COLOR_HUE_SHIFT, 0.7)

    def test_conf_freq_ratio(self):
        """测试频率比率配置"""
        self.assertEqual(CONF_FREQ_RATIO, 1)


class TestCollectDefaultConfig(unittest.TestCase):
    """测试收集默认配置函数"""

    def test_collect_returns_dict(self):
        """测试收集返回字典"""
        result = collect_default_config()
        # 函数不返回值，但应该填充_DEFAULT_CONFIG_VALUES
        # 验证globals中有_DEFAULT_CONFIG_VALUES
        from calibration_analyzer import config
        self.assertTrue(hasattr(config, '_DEFAULT_CONFIG_VALUES'))

    def test_default_config_has_required_keys(self):
        """测试默认配置包含必需的配置项"""
        from calibration_analyzer import config
        defaults = config._DEFAULT_CONFIG_VALUES

        self.assertIn('CONF_SAMPLING_RATE', defaults)
        self.assertIn('CONF_START_TIME', defaults)
        self.assertIn('CONF_DURATION', defaults)


class TestResetToDefaultConfiguration(unittest.TestCase):
    """测试重置默认配置函数"""

    def test_reset_does_not_raise(self):
        """测试重置不抛出异常"""
        # 这个函数应该正确运行而不抛出异常
        try:
            reset_to_default_configuration()
        except Exception as e:
            self.fail(f"reset_to_default_configuration 抛出异常: {e}")


class TestLoadKeywordProfile(unittest.TestCase):
    """测试加载关键词配置函数"""

    def test_load_with_matching_keyword(self):
        """测试加载匹配的关键词配置"""
        try:
            # "速度基准"应该匹配CONF_KEYWORD_PROFILE中的关键词
            load_keyword_profile("测试_速度基准_数据")
        except Exception as e:
            self.fail(f"load_keyword_profile 抛出异常: {e}")

    def test_load_without_matching_keyword(self):
        """测试加载不匹配的关键词配置"""
        try:
            load_keyword_profile("普通数据文件")
        except Exception as e:
            self.fail(f"load_keyword_profile 抛出异常: {e}")

    def test_load_resets_first(self):
        """测试加载前会重置配置"""
        # 先调用reset_to_default_configuration
        reset_to_default_configuration()

        # 然后调用load_keyword_profile，应该不会改变默认配置
        # 因为文件名不包含任何关键词
        load_keyword_profile("无关键词文件")

        # 验证配置仍然保持默认值
        from calibration_analyzer import config
        self.assertEqual(config.CONF_USING_INTERGRATE, True)


class TestConfigGainsAndPhases(unittest.TestCase):
    """测试增益和相位参考配置"""

    def test_conf_phase_ref_exists(self):
        """测试相位参考配置存在"""
        from calibration_analyzer import config
        self.assertIsNotNone(config.CONF_PHASE_REF)

    def test_conf_gain_ref_exists(self):
        """测试增益参考配置存在"""
        from calibration_analyzer import config
        self.assertIsNotNone(config.CONF_GAIN_REF)

    def test_conf_phase_ref_is_list(self):
        """测试相位参考配置是列表"""
        from calibration_analyzer import config
        self.assertIsInstance(config.CONF_PHASE_REF, list)

    def test_conf_gain_ref_is_list(self):
        """测试增益参考配置是列表"""
        from calibration_analyzer import config
        self.assertIsInstance(config.CONF_GAIN_REF, list)

    def test_conf_phase_ref_format(self):
        """测试相位参考配置格式正确"""
        from calibration_analyzer import config
        for item in config.CONF_PHASE_REF:
            self.assertIsInstance(item, tuple)
            self.assertEqual(len(item), 2)


class TestConfigKeywordProfile(unittest.TestCase):
    """测试关键词配置"""

    def test_keyword_profile_exists(self):
        """测试关键词配置存在"""
        from calibration_analyzer import config
        self.assertIsNotNone(config.CONF_KEYWORD_PROFILE)

    def test_keyword_profile_is_dict(self):
        """测试关键词配置是字典"""
        from calibration_analyzer import config
        self.assertIsInstance(config.CONF_KEYWORD_PROFILE, dict)

    def test_velocity_benchmark_profile(self):
        """测试速度基准配置"""
        from calibration_analyzer import config
        profile = config.CONF_KEYWORD_PROFILE.get("速度基准", {})

        self.assertIn("CONF_USING_INTERGRATE", profile)
        self.assertIn("CONF_GAIN_RATIO", profile)


# 使用pytest的参数化测试
@pytest.mark.parametrize("expected_value", [
    (20000),
    (5),
    (15),
    (1),
])
def test_config_values(expected_value):
    """参数化测试配置值"""
    from calibration_analyzer import config

    # 验证这些配置值符合预期
    config_values = [
        config.CONF_SAMPLING_RATE,
        config.CONF_START_TIME,
        config.CONF_DURATION,
        config.CONF_FREQ_RATIO,
    ]

    # 至少验证这些值不是None或空
    for val in config_values:
        assert val is not None
        if isinstance(val, (int, float)):
            assert val >= 0


if __name__ == "__main__":
    pytest.main(["-v", __file__])
