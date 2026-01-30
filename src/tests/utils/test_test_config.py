"""
test_config模块的单元测试

测试测试配置功能
"""

import pytest
import os


class TestTestConfig:
    """Test cases for test_config module."""

    def test_module_import(self):
        """测试模块可以正确导入。"""
        from utils import test_config
        assert test_config is not None

    def test_norm_path_function(self):
        """测试路径标准化函数。"""
        from utils.test_config import norm_path
        # 测试基本路径标准化
        result = norm_path('path/to/file')
        assert result == os.path.normpath('path/to/file')

    def test_norm_path_with_relative_parts(self):
        """测试路径标准化处理相对路径部分。"""
        from utils.test_config import norm_path
        result = norm_path('path/./to/../file')
        assert result == os.path.normpath('path/./to/../file')

    def test_skip_tests_exists(self):
        """测试SKIP_TESTS配置存在。"""
        from utils.test_config import SKIP_TESTS
        assert isinstance(SKIP_TESTS, list)

    def test_test_timeout_exists(self):
        """测试TEST_TIMEOUT配置存在。"""
        from utils.test_config import TEST_TIMEOUT
        assert isinstance(TEST_TIMEOUT, (int, float))
        assert TEST_TIMEOUT > 0

    def test_custom_timeouts_exists(self):
        """测试CUSTOM_TIMEOUTS配置存在。"""
        from utils.test_config import CUSTOM_TIMEOUTS
        assert isinstance(CUSTOM_TIMEOUTS, dict)

    def test_default_mode_exists(self):
        """测试DEFAULT_MODE配置存在。"""
        from utils.test_config import DEFAULT_MODE
        assert DEFAULT_MODE in ['all', 'quick', 'slow', 'single']

    def test_slow_tests_exists(self):
        """测试SLOW_TESTS配置存在。"""
        from utils.test_config import SLOW_TESTS
        assert isinstance(SLOW_TESTS, list)

    def test_coverage_enabled_exists(self):
        """测试COVERAGE_ENABLED配置存在。"""
        from utils.test_config import COVERAGE_ENABLED
        assert isinstance(COVERAGE_ENABLED, bool)

    def test_coverage_report_dir_exists(self):
        """测试COVERAGE_REPORT_DIR配置存在。"""
        from utils.test_config import COVERAGE_REPORT_DIR
        assert isinstance(COVERAGE_REPORT_DIR, str)

    def test_coverage_source_exists(self):
        """测试COVERAGE_SOURCE配置存在。"""
        from utils.test_config import COVERAGE_SOURCE
        assert isinstance(COVERAGE_SOURCE, list)

    def test_coverage_omit_exists(self):
        """测试COVERAGE_OMIT配置存在。"""
        from utils.test_config import COVERAGE_OMIT
        assert isinstance(COVERAGE_OMIT, list)

    def test_coverage_fail_under_exists(self):
        """测试COVERAGE_FAIL_UNDER配置存在。"""
        from utils.test_config import COVERAGE_FAIL_UNDER
        assert isinstance(COVERAGE_FAIL_UNDER, (int, float))
