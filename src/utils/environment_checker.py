"""
环境检查模块

负责检查 Python 和 TensorFlow 版本，确保运行环境符合要求。
此模块必须在主进程中调用，不能作为独立模块运行。
"""

import logging
import sys

logger = logging.getLogger(__name__)


def check_environment():
    """
    检查运行环境是否正确
    
    要求：
    - Python 版本必须是 3.9
    - TensorFlow 版本必须是 2.6.x
    
    如果环境不符合要求，将打印错误信息并退出程序
    """
    # 检查 Python 版本
    python_version = f'{sys.version_info.major}.{sys.version_info.minor}'
    if python_version != '3.9':
        logger.error('\n' + '=' * 60)
        logger.error('❌ 错误：Python版本不正确')
        logger.error('=' * 60)
        logger.error(f'当前版本: Python {python_version}')
        logger.error(f'需要版本: Python 3.9')
        logger.error(f'\n请使用以下命令在正确的环境中运行：')
        logger.error('  conda run -n tf26 python cli.py [参数]')
        logger.error('=' * 60 + '\n')
        sys.exit(1)
    
    # 检查 TensorFlow 版本
    try:
        logger.info("importing tensorflow")
        import tensorflow as tf
        tf_version = tf.__version__
        if not tf_version.startswith('2.6'):
            logger.error('\n' + '=' * 60)
            logger.error('❌ 错误：TensorFlow版本不正确')
            logger.error('=' * 60)
            logger.error(f'当前版本: TensorFlow {tf_version}')
            logger.error(f'需要版本: TensorFlow 2.6.x')
            logger.error('\n请使用以下命令在正确的环境中运行：')
            logger.error('  conda run -n tf26 python cli.py [参数]')
            logger.error('=' * 60 + '\n')
            sys.exit(1)
    except ImportError:
        logger.error('\n' + '=' * 60)
        logger.error('❌ 错误：TensorFlow未安装')
        logger.error('=' * 60)
        logger.error(f'请使用以下命令在正确的环境中运行：')
        logger.error('  conda run -n tf26 python cli.py [参数]')
        logger.error('=' * 60 + '\n')
        sys.exit(1)
    
    logger.info("环境检查通过")