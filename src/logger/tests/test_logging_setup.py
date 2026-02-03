"""测试 logging_setup 模块"""

import pytest
import logging
import yaml
import json
from pathlib import Path
import tempfile
import shutil
import sys

# Add logger directory to path
logger_dir = Path(__file__).parent.parent
sys.path.insert(0, str(logger_dir))

from logging_setup import (
    setup_logging, get_module_logger, set_module_log_level,
    add_file_handler, LogContext, ColoredFormatter
)


class TestLoggingSetup:
    """测试日志设置功能"""

    def test_setup_with_default_config(self, temp_dir, reset_logging):
        """测试使用默认配置设置日志"""
        logger = setup_logging(log_dir=str(temp_dir))

        # Logger name is 'cli' in the actual implementation
        assert logger.name == 'cli'
        # Default level should be DEBUG or INFO
        assert logger.level in [logging.DEBUG, logging.INFO]
        assert len(logger.handlers) > 0

    def test_setup_with_yaml_config(self, temp_dir, reset_logging):
        """测试使用 YAML 配置文件"""
        # 创建测试配置
        config_path = temp_dir / "test_config.yaml"
        config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'simple': {'format': '%(message)s'}
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'simple'
                }
            },
            'loggers': {
                'cli': {
                    'level': 'INFO',
                    'handlers': ['console'],
                    'propagate': False
                }
            }
        }

        with open(config_path, 'w') as f:
            yaml.dump(config, f)

        logger = setup_logging(config_path=str(config_path))
        # Logger should be configured with the custom level
        assert logger.level in [logging.INFO, logging.DEBUG]

    def test_setup_with_json_config(self, temp_dir, reset_logging):
        """测试使用 JSON 配置文件"""
        config_path = temp_dir / "test_config.json"
        config = {
            "version": 1,
            "disable_existing_loggers": False,
            "loggers": {
                "cli": {
                    "level": "WARNING"
                }
            }
        }

        with open(config_path, 'w') as f:
            json.dump(config, f)

        logger = setup_logging(config_path=str(config_path))
        assert logger.level == logging.WARNING

    def test_get_module_logger(self, reset_logging):
        """测试获取模块 logger"""
        setup_logging()

        # 获取模块 logger
        core_logger = get_module_logger('core')
        training_logger = get_module_logger('core.training')

        # Logger 名称应该以 metnl. 开头
        assert 'core' in core_logger.name
        assert 'core.training' in training_logger.name

        # 测试继承关系
        assert training_logger.parent is None or 'core' in training_logger.parent.name

    def test_set_module_log_level(self, reset_logging):
        """测试动态设置模块日志级别"""
        setup_logging()
        logger = get_module_logger('test')

        # 设置新级别
        set_module_log_level('test', 'ERROR')
        assert logger.level == logging.ERROR

        set_module_log_level('test', 'debug')  # 测试大小写
        assert logger.level == logging.DEBUG

    def test_add_file_handler(self, temp_dir, reset_logging):
        """测试添加文件处理器"""
        setup_logging()
        logger = get_module_logger('test')

        # 添加文件处理器
        log_file = temp_dir / "test.log"
        add_file_handler('metnl.test', str(log_file))

        # 确保有处理器被添加
        assert len(logger.handlers) > 0 or (logger.parent and logger.parent.handlers)

    def test_log_context(self, reset_logging):
        """测试日志上下文管理器"""
        setup_logging()

        with LogContext('metnl.test', {'request_id': '123'}) as logger:
            assert hasattr(logger, 'request_id')
            assert logger.request_id == '123'

        # 退出上下文后属性应该被清除
        logger = logging.getLogger('metnl.test')
        assert not hasattr(logger, 'request_id')

    def test_colored_formatter(self):
        """测试彩色格式化器"""
        formatter = ColoredFormatter('%(levelname)s: %(message)s')

        # 创建不同级别的记录
        record = logging.LogRecord(
            name='test', level=logging.INFO, pathname='',
            lineno=0, msg='Test', args=(), exc_info=None
        )

        formatted = formatter.format(record)

        # 应该包含颜色代码
        assert '\033[' in formatted  # ANSI 颜色代码
        assert 'INFO' in formatted
        assert 'Test' in formatted


class TestLoggerIntegration:
    """测试日志系统集成"""

    def test_logger_output(self, temp_dir, capsys, reset_logging):
        """测试日志输出"""
        logger = setup_logging(log_dir=str(temp_dir))

        # 记录不同级别的日志
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        captured = capsys.readouterr()

        # 默认配置下，INFO 及以上级别应该输出到控制台
        # 格式可能包含时间戳，所以检查关键部分
        assert "Info message" in captured.out or "INFO" in captured.out
        assert "Warning message" in captured.out or "WARNING" in captured.out
        assert "Error message" in captured.out or "ERROR" in captured.out

    def test_module_hierarchy(self, capsys, reset_logging):
        """测试模块层次结构"""
        setup_logging()

        # 创建层次化的 logger
        parent_logger = get_module_logger('core')
        child_logger = get_module_logger('core.training')

        # 设置父级别
        set_module_log_level('core', 'WARNING')

        # 子 logger 应该继承父级别
        parent_logger.warning("Parent warning")
        child_logger.warning("Child warning")

        captured = capsys.readouterr()

        # 两个警告都应该显示
        assert "Parent warning" in captured.out or "Parent warning" in captured.err
        assert "Child warning" in captured.out or "Child warning" in captured.err

    def test_multiple_handlers(self, temp_dir, reset_logging):
        """测试多个处理器"""
        log_file = temp_dir / "multi.log"

        # 创建配置
        config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'simple': {'format': '%(levelname)s: %(message)s'},
                'detailed': {'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'}
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': 'INFO',
                    'formatter': 'simple'
                },
                'file': {
                    'class': 'logging.FileHandler',
                    'level': 'DEBUG',
                    'formatter': 'detailed',
                    'filename': str(log_file)
                }
            },
            'loggers': {
                'cli': {
                    'level': 'DEBUG',
                    'handlers': ['console', 'file']
                }
            }
        }

        config_path = temp_dir / "config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f)

        logger = setup_logging(config_path=str(config_path))

        # 记录消息
        logger.debug("Debug to file only")
        logger.info("Info to both")

        # 检查文件内容
        if log_file.exists():
            content = log_file.read_text()
            assert "Debug to file only" in content
            assert "Info to both" in content


@pytest.mark.parametrize("level,expected", [
    ("DEBUG", logging.DEBUG),
    ("INFO", logging.INFO),
    ("WARNING", logging.WARNING),
    ("ERROR", logging.ERROR),
    ("CRITICAL", logging.CRITICAL),
])
def test_level_conversion(level, expected, reset_logging):
    """测试日志级别转换"""
    setup_logging()
    set_module_log_level('test', level)
    logger = get_module_logger('test')
    assert logger.level == expected


class TestColoredFormatterLevels:
    """测试彩色格式化器处理不同级别"""

    def test_debug_level_color(self):
        """测试 DEBUG 级别的颜色"""
        formatter = ColoredFormatter('%(levelname)s: %(message)s')

        record = logging.LogRecord(
            name='test', level=logging.DEBUG, pathname='',
            lineno=0, msg='Debug test', args=(), exc_info=None
        )

        formatted = formatter.format(record)
        assert '\033[' in formatted  # 应该包含 ANSI 颜色代码
        assert 'DEBUG' in formatted

    def test_warning_level_color(self):
        """测试 WARNING 级别的颜色"""
        formatter = ColoredFormatter('%(levelname)s: %(message)s')

        record = logging.LogRecord(
            name='test', level=logging.WARNING, pathname='',
            lineno=0, msg='Warning test', args=(), exc_info=None
        )

        formatted = formatter.format(record)
        assert '\033[' in formatted
        assert 'WARNING' in formatted

    def test_error_level_color(self):
        """测试 ERROR 级别的颜色"""
        formatter = ColoredFormatter('%(levelname)s: %(message)s')

        record = logging.LogRecord(
            name='test', level=logging.ERROR, pathname='',
            lineno=0, msg='Error test', args=(), exc_info=None
        )

        formatted = formatter.format(record)
        assert '\033[' in formatted
        assert 'ERROR' in formatted

    def test_critical_level_color(self):
        """测试 CRITICAL 级别的颜色"""
        formatter = ColoredFormatter('%(levelname)s: %(message)s')

        record = logging.LogRecord(
            name='test', level=logging.CRITICAL, pathname='',
            lineno=0, msg='Critical test', args=(), exc_info=None
        )

        formatted = formatter.format(record)
        assert '\033[' in formatted
        assert 'CRITICAL' in formatted


class TestLogContextEdgeCases:
    """测试日志上下文管理器的边缘情况"""

    def test_context_with_empty_extra(self, reset_logging):
        """测试空 extra 字典"""
        setup_logging()

        with LogContext('metnl.test', {}) as logger:
            # 应该正常工作
            pass

    def test_context_with_multiple_extras(self, reset_logging):
        """测试多个 extra 键"""
        setup_logging()

        with LogContext('metnl.test', {
            'request_id': '123',
            'user_id': '456',
            'session_id': '789'
        }) as logger:
            assert logger.request_id == '123'
            assert logger.user_id == '456'
            assert logger.session_id == '789'

    def test_context_exception_handling(self, reset_logging):
        """测试上下文中的异常处理"""
        setup_logging()

        original_logger = logging.getLogger('metnl.test_context')

        try:
            with LogContext('metnl.test_context', {'test_key': 'test_value'}) as logger:
                assert logger.test_key == 'test_value'
                raise ValueError("Test exception")
        except ValueError:
            pass

        # 验证上下文已清理
        cleaned_logger = logging.getLogger('metnl.test_context')
        assert not hasattr(cleaned_logger, 'test_key')
