"""
日志系统设置模块

基于 Python 标准 logging 库的模块化日志系统实现。
支持分层日志、多处理器输出、灵活配置。
"""

import logging
import logging.config
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import yaml
import json
from datetime import datetime


def setup_logging(
    config_path: Optional[str] = None,
    log_dir: str = 'logs',
    default_level: str = 'INFO',
    use_timestamp: bool = True
) -> logging.Logger:
    """
    设置日志系统
    
    Args:
        config_path: 日志配置文件路径（YAML 或 JSON）
        log_dir: 日志文件目录
        default_level: 默认日志级别
        use_timestamp: 是否在日志文件名中使用时间戳
        
    Returns:
        主 logger 实例
    """
    print('正在配置 logging_setup...')
    # 确保日志目录存在
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # 如果没有指定配置文件，使用默认配置文件
    if config_path is None:
        default_config_path = Path(__file__).parent / 'logging_config.yaml'
        if default_config_path.exists():
            config_path = str(default_config_path)
    
    if config_path and Path(config_path).exists():
        # 从配置文件加载
        print(f'logging_setup 从配置文件加载: {config_path}')
        config = _load_config(config_path)
    else:
        # 使用默认配置
        print('logging_setup 使用默认配置')
        config = _get_default_config(log_dir, default_level)
    
    # 生成时间戳
    if use_timestamp:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # 更新配置中的文件名
        _update_log_filenames(config, log_dir, timestamp)
    
    # 应用配置
    logging.config.dictConfig(config)
    print(f'log 文件路径: logs/metnl.log')
    
    # 打印日志文件路径
    _print_log_file_paths(config)
    
    # 返回主 logger
    return logging.getLogger('cli')


def get_module_logger(module_name: str) -> logging.Logger:
    """
    获取模块专用 logger
    
    Args:
        module_name: 模块名称（如 'core.training'）
        
    Returns:
        配置好的 logger 实例
    """
    return logging.getLogger(f'metnl.{module_name}')


def _load_config(config_path: str) -> Dict[str, Any]:
    """加载配置文件"""
    config_path = Path(config_path)
    
    if config_path.suffix in ['.yaml', '.yml']:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    elif config_path.suffix == '.json':
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        raise ValueError(f"不支持的配置文件格式: {config_path.suffix}")


def _get_default_config(log_dir: str, default_level: str) -> Dict[str, Any]:
    """获取默认配置"""
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '%(levelname)-8s - %(filename)s:%(lineno)d - %(message)s'
            },
            'detailed': {
                'format': '%(asctime)s - %(levelname)-8s - %(filename)s:%(lineno)d - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'console_simple',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'detailed',
                'filename': f'{log_dir}/cli.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf-8'
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'detailed',
                'filename': f'{log_dir}/cli_errors.log',
                'maxBytes': 10485760,
                'backupCount': 5,
                'encoding': 'utf-8'
            }
        },
        'root': {
            'level': default_level,
            'handlers': ['console', 'file', 'error_file']
        },
        'loggers': {
            'cli': {
                'level': 'DEBUG',
                'handlers': ['console', 'file', 'error_file'],
                'propagate': False
            }
        }
    }


class ColoredFormatter(logging.Formatter):
    """带颜色的控制台输出格式化器"""
    
    # ANSI 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',     # 青色
        'INFO': '\033[32m',      # 绿色
        'WARNING': '\033[33m',   # 黄色
        'ERROR': '\033[31m',     # 红色
        'CRITICAL': '\033[35m',  # 紫色
    }
    RESET = '\033[0m'
    
    def format(self, record):
        # 添加颜色
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
        
        # 调用父类格式化
        result = super().format(record)
        
        # 恢复原始级别名称
        record.levelname = levelname
        
        return result


class LogContext:
    """日志上下文管理器"""
    
    def __init__(self, logger_name: str, extra: Dict[str, Any] = None):
        self.logger = logging.getLogger(logger_name)
        self.extra = extra or {}
        self._old_extra = {}
        
    def __enter__(self):
        # 保存旧的 extra 并设置新的
        for key, value in self.extra.items():
            if hasattr(self.logger, key):
                self._old_extra[key] = getattr(self.logger, key)
            setattr(self.logger, key, value)
        return self.logger
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # 恢复旧的 extra
        for key in self.extra:
            if key in self._old_extra:
                setattr(self.logger, key, self._old_extra[key])
            else:
                delattr(self.logger, key)


def configure_colored_output():
    """配置彩色输出（仅在支持的终端中）"""
    if sys.stdout.isatty() and os.name != 'nt':  # Unix/Linux 终端
        # 获取控制台 handler
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
                # 使用彩色格式化器
                handler.setFormatter(ColoredFormatter(handler.formatter._fmt))


def set_module_log_level(module_name: str, level: str):
    """
    动态设置模块日志级别
    
    Args:
        module_name: 模块名称
        level: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
    """
    logger = get_module_logger(module_name)
    logger.setLevel(getattr(logging, level.upper()))


def _update_log_filenames(config: Dict[str, Any], log_dir: str, timestamp: str):
    """更新配置中的日志文件名，添加时间戳"""
    if 'handlers' in config:
        for handler_name, handler_config in config['handlers'].items():
            if 'filename' in handler_config:
                # 从原文件名中提取基础名称
                original_filename = Path(handler_config['filename'])
                base_name = original_filename.stem
                extension = original_filename.suffix
                
                # 构建新的文件名
                new_filename = f"{log_dir}/{timestamp}_{base_name}{extension}"
                handler_config['filename'] = new_filename


def _print_log_file_paths(config: Dict[str, Any]):
    """打印日志文件路径"""
    print("\n日志文件已创建：")
    if 'handlers' in config:
        for handler_name, handler_config in config['handlers'].items():
            if 'filename' in handler_config:
                print(f"  {handler_name}: {handler_config['filename']}")
    print("")


def add_file_handler(
    logger_name: str,
    filename: str,
    level: str = 'DEBUG',
    formatter_name: str = 'detailed'
):
    """
    为特定 logger 添加文件处理器
    
    Args:
        logger_name: Logger 名称
        filename: 日志文件名
        level: 日志级别
        formatter_name: 格式化器名称
    """
    logger = logging.getLogger(logger_name)
    
    # 创建文件处理器
    handler = logging.handlers.RotatingFileHandler(
        filename, 
        encoding='utf-8',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    handler.setLevel(getattr(logging, level.upper()))
    
    # 设置格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)-8s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)