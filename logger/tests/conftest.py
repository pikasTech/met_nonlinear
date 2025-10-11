"""pytest 配置和 fixtures"""

import pytest
import sys
import os
from pathlib import Path
import tempfile
import shutil

# 添加 logger 目录到 Python 路径
logger_dir = Path(__file__).parent.parent
sys.path.insert(0, str(logger_dir))


@pytest.fixture
def temp_dir():
    """创建临时目录用于测试"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def capture_prints(capsys):
    """捕获 print 输出的 fixture"""
    def _capture():
        return capsys.readouterr()
    return _capture


@pytest.fixture
def sample_python_file(temp_dir):
    """创建一个包含 print 语句的示例 Python 文件"""
    file_path = temp_dir / "sample.py"
    content = '''
def hello():
    print("Hello, World!")
    
def calculate(x, y):
    result = x + y
    print(f"Result: {result}")
    return result
    
if __name__ == "__main__":
    print("Starting program")
    hello()
    calculate(10, 20)
    print("Program finished")
'''
    file_path.write_text(content)
    return file_path


@pytest.fixture
def logger_config():
    """提供测试用的日志配置"""
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '%(levelname)s: %(message)s'
            },
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'simple',
                'stream': 'ext://sys.stdout'
            }
        },
        'loggers': {
            'test': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False
            }
        }
    }


@pytest.fixture(autouse=True)
def reset_logging():
    """每个测试后重置 logging 配置"""
    import logging
    yield
    # 清理所有 handlers
    for logger_name in list(logging.Logger.manager.loggerDict.keys()):
        logger = logging.getLogger(logger_name)
        logger.handlers = []
        logger.filters = []
        logger.setLevel(logging.WARNING)