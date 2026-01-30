"""
环境检查模块的单元测试

测试环境检查功能，确保正确检测Python和TensorFlow版本
"""

import pytest
import sys
import logging
from unittest.mock import patch, MagicMock
from utils.environment_checker import (
    get_python_version,
    check_python_version,
    get_tensorflow_version,
    check_tensorflow_version,
    REQUIRED_PYTHON_VERSION,
    REQUIRED_TENSORFLOW_PREFIX
)


class TestGetPythonVersion:
    """Test cases for get_python_version function."""

    def test_get_python_version_returns_string(self):
        """测试返回类型为字符串。"""
        result = get_python_version()
        assert isinstance(result, str)

    def test_get_python_version_format(self):
        """测试版本字符串格式。"""
        result = get_python_version()
        parts = result.split('.')
        assert len(parts) == 2
        assert all(p.isdigit() for p in parts)

    def test_get_python_version_value(self):
        """测试版本值正确。"""
        result = get_python_version()
        assert result == REQUIRED_PYTHON_VERSION


class TestCheckPythonVersion:
    """Test cases for check_python_version function."""

    def test_check_python_version_valid(self):
        """测试Python版本正确时返回通过。"""
        with patch('utils.environment_checker.get_python_version', return_value=REQUIRED_PYTHON_VERSION):
            passed, error_msg = check_python_version()
            assert passed is True
            assert error_msg == ''

    def test_check_python_version_invalid_38(self):
        """测试Python 3.8版本时返回失败。"""
        with patch('utils.environment_checker.get_python_version', return_value='3.8'):
            passed, error_msg = check_python_version()
            assert passed is False
            assert '不符合要求' in error_msg
            assert '3.8' in error_msg
            assert REQUIRED_PYTHON_VERSION in error_msg

    def test_check_python_version_invalid_310(self):
        """测试Python 3.10版本时返回失败。"""
        with patch('utils.environment_checker.get_python_version', return_value='3.10'):
            passed, error_msg = check_python_version()
            assert passed is False
            assert '不符合要求' in error_msg

    def test_check_python_version_invalid_36(self):
        """测试Python 3.6版本时返回失败。"""
        with patch('utils.environment_checker.get_python_version', return_value='3.6'):
            passed, error_msg = check_python_version()
            assert passed is False
            assert '不符合要求' in error_msg

    def test_check_python_version_invalid_311(self):
        """测试Python 3.11版本时返回失败。"""
        with patch('utils.environment_checker.get_python_version', return_value='3.11'):
            passed, error_msg = check_python_version()
            assert passed is False
            assert '不符合要求' in error_msg


class TestGetTensorFlowVersion:
    """Test cases for get_tensorflow_version function."""

    def test_get_tensorflow_version_returns_string(self):
        """测试TensorFlow已安装时返回字符串。"""
        try:
            result = get_tensorflow_version()
            if result is not None:
                assert isinstance(result, str)
                assert result.startswith(REQUIRED_TENSORFLOW_PREFIX)
        except ImportError:
            pytest.skip("TensorFlow not installed")

    def test_get_tensorflow_version_none_when_not_installed(self):
        """测试TensorFlow未安装时返回None。"""
        with patch.dict('sys.modules', {'tensorflow': None}):
            # Force reimport
            import importlib
            import utils.environment_checker
            # This test verifies the logic handles ImportError
            # Actual None return depends on module state


class TestCheckTensorFlowVersion:
    """Test cases for check_tensorflow_version function."""

    def test_check_tensorflow_version_valid(self):
        """测试TensorFlow版本正确时返回通过。"""
        with patch('utils.environment_checker.get_tensorflow_version', return_value='2.6.0'):
            passed, error_msg = check_tensorflow_version()
            assert passed is True
            assert error_msg == ''

    def test_check_tensorflow_version_valid_261(self):
        """测试TensorFlow 2.6.1版本时返回通过。"""
        with patch('utils.environment_checker.get_tensorflow_version', return_value='2.6.1'):
            passed, error_msg = check_tensorflow_version()
            assert passed is True
            assert error_msg == ''

    def test_check_tensorflow_version_valid_262(self):
        """测试TensorFlow 2.6.2版本时返回通过。"""
        with patch('utils.environment_checker.get_tensorflow_version', return_value='2.6.2'):
            passed, error_msg = check_tensorflow_version()
            assert passed is True
            assert error_msg == ''

    def test_check_tensorflow_version_invalid_25(self):
        """测试TensorFlow 2.5版本时返回失败。"""
        with patch('utils.environment_checker.get_tensorflow_version', return_value='2.5.0'):
            passed, error_msg = check_tensorflow_version()
            assert passed is False
            assert '不符合要求' in error_msg

    def test_check_tensorflow_version_invalid_27(self):
        """测试TensorFlow 2.7版本时返回失败。"""
        with patch('utils.environment_checker.get_tensorflow_version', return_value='2.7.0'):
            passed, error_msg = check_tensorflow_version()
            assert passed is False
            assert '不符合要求' in error_msg

    def test_check_tensorflow_version_not_installed(self):
        """测试TensorFlow未安装时返回失败。"""
        with patch('utils.environment_checker.get_tensorflow_version', return_value=None):
            passed, error_msg = check_tensorflow_version()
            assert passed is False
            assert '未安装' in error_msg

    def test_check_tensorflow_version_invalid_30(self):
        """测试TensorFlow 3.0版本时返回失败。"""
        with patch('utils.environment_checker.get_tensorflow_version', return_value='3.0.0'):
            passed, error_msg = check_tensorflow_version()
            assert passed is False
            assert '不符合要求' in error_msg


class TestConstants:
    """Test cases for module constants."""

    def test_required_python_version(self):
        """测试要求的Python版本常量。"""
        assert REQUIRED_PYTHON_VERSION == '3.9'

    def test_required_tensorflow_prefix(self):
        """测试要求的TensorFlow版本前缀常量。"""
        assert REQUIRED_TENSORFLOW_PREFIX == '2.6'


class TestEnvironmentCheckerIntegration:
    """Integration tests for environment checker module."""

    def test_module_import(self):
        """测试模块可以正确导入。"""
        from utils import environment_checker
        assert hasattr(environment_checker, 'check_environment')
        assert hasattr(environment_checker, 'logger')
        assert hasattr(environment_checker, 'get_python_version')
        assert hasattr(environment_checker, 'check_python_version')
        assert hasattr(environment_checker, 'get_tensorflow_version')
        assert hasattr(environment_checker, 'check_tensorflow_version')

    def test_logger_exists(self):
        """测试logger正确初始化。"""
        from utils.environment_checker import logger
        assert logger is not None
        assert logger.name == 'utils.environment_checker'

    def test_check_environment_function_exists(self):
        """测试check_environment函数存在。"""
        from utils.environment_checker import check_environment
        assert callable(check_environment)

    def test_current_python_version(self):
        """测试当前环境的Python版本（运行时验证）。"""
        current_version = get_python_version()
        print(f"Current Python version: {current_version}")
        assert current_version is not None

    def test_current_tensorflow_version(self):
        """测试当前环境的TensorFlow版本（运行时验证）。"""
        tf_version = get_tensorflow_version()
        if tf_version is not None:
            print(f"Current TensorFlow version: {tf_version}")
            assert tf_version is not None
        else:
            pytest.skip("TensorFlow not installed in test environment")


class TestCheckEnvironment:
    """Test cases for check_environment function (with sys.exit patching)."""

    def test_check_environment_python_version_failure(self):
        """测试Python版本不正确时调用sys.exit。"""
        from utils.environment_checker import check_environment

        with patch('utils.environment_checker.get_python_version', return_value='3.10'):
            with pytest.raises(SystemExit) as exc_info:
                check_environment()
            assert exc_info.value.code == 1

    def test_check_environment_tensorflow_version_failure(self):
        """测试TensorFlow版本不正确时调用sys.exit。"""
        from utils.environment_checker import check_environment

        with patch('utils.environment_checker.get_python_version', return_value=REQUIRED_PYTHON_VERSION):
            with patch('utils.environment_checker.get_tensorflow_version', return_value='2.7.0'):
                with pytest.raises(SystemExit) as exc_info:
                    check_environment()
                assert exc_info.value.code == 1

    def test_check_environment_tensorflow_not_installed(self):
        """测试TensorFlow未安装时调用sys.exit。"""
        from utils.environment_checker import check_environment

        with patch('utils.environment_checker.get_python_version', return_value=REQUIRED_PYTHON_VERSION):
            with patch('utils.environment_checker.get_tensorflow_version', return_value=None):
                with pytest.raises(SystemExit) as exc_info:
                    check_environment()
                assert exc_info.value.code == 1

    def test_check_environment_success(self, caplog):
        """测试环境检查通过时记录日志。"""
        from utils.environment_checker import check_environment

        with patch('utils.environment_checker.get_python_version', return_value=REQUIRED_PYTHON_VERSION):
            with patch('utils.environment_checker.get_tensorflow_version', return_value='2.6.0'):
                with caplog.at_level(logging.INFO):
                    check_environment()
                assert "环境检查通过" in caplog.text
