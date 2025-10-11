import logging

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
'\n推理模块包装器\n\n此文件提供向后兼容的接口，将调用重定向到重构后的模块。\n'
from .processor import InferenceProcessor, USE_SCALER
from .cli import main
__all__ = ['InferenceProcessor', 'main', 'USE_SCALER']
if __name__ == '__main__':
    main()