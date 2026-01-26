"""
Unified logging utilities for inference module.

This module provides consistent logging functionality across
all inference components.
"""
import logging
import sys
from datetime import datetime
from typing import Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

class InferenceLogger:
    """统一的推理日志记录器"""
    _loggers = {}

    def __init__(self, name: str, level: int=logging.INFO):
        """
        初始化日志记录器
        
        Args:
            name: 日志记录器名称（通常是模块名）
            level: 日志级别
        """
        self.name = name
        self.logger = self._get_or_create_logger(name, level)

    @classmethod
    def _get_or_create_logger(cls, name: str, level: int) -> logging.Logger:
        """获取或创建logger实例"""
        if name in cls._loggers:
            return cls._loggers[name]
        logger = logging.getLogger(f'inference.{name}')
        logger.setLevel(level)
        if not logger.handlers:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        cls._loggers[name] = logger
        return logger

    def info(self, message: str, **kwargs) -> None:
        """记录信息级别日志"""
        self.logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """记录警告级别日志"""
        self.logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """记录错误级别日志"""
        self.logger.error(message, **kwargs)

    def debug(self, message: str, **kwargs) -> None:
        """记录调试级别日志"""
        self.logger.debug(message, **kwargs)

    def log_inference_start(self, backend: str, model_type: str, project: Optional[str]=None) -> None:
        """记录推理开始"""
        msg = f'Starting {backend} inference for {model_type}'
        if project:
            msg += f' (project: {project})'
        self.info(msg)

    def log_inference_complete(self, backend: str, execution_time: float, success: bool=True) -> None:
        """记录推理完成"""
        status = 'completed' if success else 'failed'
        self.info(f'{backend} inference {status} in {execution_time:.3f} seconds')

    def log_layer_processing(self, layer_index: int, layer_type: str, input_shape: tuple, output_shape: tuple) -> None:
        """记录层处理信息"""
        self.debug(f'Processing layer {layer_index} ({layer_type}): input {input_shape} -> output {output_shape}')

    def log_data_range(self, name: str, min_val: float, max_val: float, mean_val: Optional[float]=None) -> None:
        """记录数据范围（替代print语句）"""
        msg = f'{name} range: [{min_val:.6f}, {max_val:.6f}]'
        if mean_val is not None:
            msg += f', mean: {mean_val:.6f}'
        self.info(msg)

    def log_phase_correction(self, layer_index: int, before_range: tuple, after_range: tuple) -> None:
        """记录相位修正信息"""
        before_min, before_max = before_range
        after_min, after_max = after_range
        self.info(f'Layer {layer_index} phase correction: [{before_min:.6f}, {before_max:.6f}] -> [{after_min:.6f}, {after_max:.6f}]')

    def log_validation_error(self, error: Exception) -> None:
        """记录验证错误"""
        self.error(f'Validation error: {str(error)}')

    def log_backend_switch(self, from_backend: str, to_backend: str) -> None:
        """记录后端切换"""
        self.info(f'Switching backend: {from_backend} -> {to_backend}')

    @staticmethod
    def create_file_logger(name: str, log_file: Path, level: int=logging.INFO) -> 'InferenceLogger':
        """
        创建带文件输出的日志记录器
        
        Args:
            name: 日志记录器名称
            log_file: 日志文件路径
            level: 日志级别
            
        Returns:
            InferenceLogger: 配置好的日志记录器
        """
        logger_instance = InferenceLogger(name, level)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        logger_instance.logger.addHandler(file_handler)
        return logger_instance
_global_logger = None

def get_logger(name: str='inference') -> InferenceLogger:
    """获取全局logger实例"""
    global _global_logger
    if _global_logger is None:
        _global_logger = InferenceLogger(name)
    return _global_logger