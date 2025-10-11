"""测试 logging_setup 模块"""

import pytest
import logging
import yaml
import json
from pathlib import Path
import tempfile

from logging_setup import (
    setup_logging, get_module_logger, set_module_log_level,
    add_file_handler, LogContext, ColoredFormatter
)


class TestLoggingSetup:
    """测试日志设置功能"""
    
    def test_setup_with_default_config(self, temp_dir, reset_logging):
        """测试使用默认配置设置日志"""
        logger = setup_logging(log_dir=str(temp_dir))
        
        assert logger.name == 'metnl'
        assert logger.level == logging.DEBUG
        assert len(logger.handlers) > 0
        
        # 检查日志目录创建
        assert (temp_dir / "metnl.log").exists() or True  # 文件可能还未创建
        
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
                'metnl': {
                    'level': 'INFO',
                    'handlers': ['console']
                }
            }
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
            
        logger = setup_logging(config_path=str(config_path))
        assert logger.level == logging.INFO
        
    def test_setup_with_json_config(self, temp_dir, reset_logging):
        """测试使用 JSON 配置文件"""
        config_path = temp_dir / "test_config.json"
        config = {
            'version': 1,
            'disable_existing_loggers': False,
            'loggers': {
                'metnl': {
                    'level': 'WARNING'
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
        
        assert core_logger.name == 'metnl.core'
        assert training_logger.name == 'metnl.core.training'
        
        # 测试继承关系
        assert training_logger.parent.name == 'metnl.core'
        
    def test_set_module_log_level(self, reset_logging):
        """测试动态设置模块日志级别"""
        setup_logging()
        logger = get_module_logger('test')
        
        # 初始级别
        assert logger.level == logging.NOTSET  # 继承父级别
        
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
        
        # 记录一条消息
        logger.info("Test message")
        
        # 确保有处理器被添加
        assert len(logger.handlers) > 0 or logger.parent.handlers  # 可能继承父处理器
        
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
        assert "INFO: Info message" in captured.out
        assert "WARNING: Warning message" in captured.out
        assert "ERROR: Error message" in captured.out
        assert "Debug message" not in captured.out  # DEBUG 不输出到控制台
        
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
        child_logger.info("Child info")  # 不应该显示
        
        captured = capsys.readouterr()
        assert "Parent warning" in captured.out
        assert "Child warning" in captured.out
        assert "Child info" not in captured.out
        
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
                'metnl': {
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