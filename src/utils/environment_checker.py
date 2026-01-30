"""
环境检查模块

负责检查 Python 和 TensorFlow 版本，确保运行环境符合要求。
此模块必须在主进程中调用，不能作为独立模块运行。
"""

import logging
import sys

logger = logging.getLogger(__name__)

# 要求的版本常量
REQUIRED_PYTHON_VERSION = '3.9'
REQUIRED_TENSORFLOW_PREFIX = '2.6'


def get_python_version():
    """
    获取当前Python版本字符串。

    Returns:
        str: 版本字符串，格式为 'major.minor'
    """
    return f'{sys.version_info.major}.{sys.version_info.minor}'


def check_python_version():
    """
    检查Python版本是否符合要求。

    Returns:
        tuple: (bool, str) - (是否通过, 错误消息或空字符串)
    """
    python_version = get_python_version()
    if python_version != REQUIRED_PYTHON_VERSION:
        return False, f'Python版本 {python_version} 不符合要求，需要 {REQUIRED_PYTHON_VERSION}'
    return True, ''


def get_tensorflow_version():
    """
    获取当前TensorFlow版本。

    Returns:
        str: TensorFlow版本字符串，如果未安装则返回None
    """
    try:
        import tensorflow as tf
        return tf.__version__
    except ImportError:
        return None


def check_tensorflow_version():
    """
    检查TensorFlow版本是否符合要求。

    Returns:
        tuple: (bool, str) - (是否通过, 错误消息或空字符串)
    """
    tf_version = get_tensorflow_version()
    if tf_version is None:
        return False, 'TensorFlow未安装'
    if not tf_version.startswith(REQUIRED_TENSORFLOW_PREFIX):
        return False, f'TensorFlow版本 {tf_version} 不符合要求，需要 {REQUIRED_TENSORFLOW_PREFIX}.x'
    return True, ''


def check_environment():
    """
    检查运行环境是否正确

    要求：
    - Python 版本必须是 3.9
    - TensorFlow 版本必须是 2.6.x

    如果环境不符合要求，将打印错误信息并退出程序
    """
    # 检查 Python 版本
    passed, error_msg = check_python_version()
    if not passed:
        logger.error('\n' + '=' * 60)
        logger.error('错误：Python版本不正确')
        logger.error('=' * 60)
        logger.error(f'当前版本: Python {get_python_version()}')
        logger.error(f'需要版本: Python {REQUIRED_PYTHON_VERSION}')
        logger.error(f'\n请使用以下命令在正确的环境中运行：')
        logger.error('  conda run -n tf26 python cli.py [参数]')
        logger.error('=' * 60 + '\n')
        sys.exit(1)

    # 检查 TensorFlow 版本
    passed, error_msg = check_tensorflow_version()
    if not passed:
        logger.error('\n' + '=' * 60)
        logger.error('错误：TensorFlow版本不正确')
        logger.error('=' * 60)
        logger.error(f'当前版本: TensorFlow {get_tensorflow_version()}')
        logger.error(f'需要版本: TensorFlow {REQUIRED_TENSORFLOW_PREFIX}.x')
        logger.error(f'\n请使用以下命令在正确的环境中运行：')
        logger.error('  conda run -n tf26 python cli.py [参数]')
        logger.error('=' * 60 + '\n')
        sys.exit(1)

    logger.info("环境检查通过")
