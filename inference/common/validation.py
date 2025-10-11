import logging
logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
'\nInput validation utilities.\n\nThis module provides common validation functions to ensure\ndata integrity and proper backend usage.\n'
from typing import Optional, Union, List, Any
import numpy as np
from pathlib import Path

class ValidationError(Exception):
    """验证错误异常"""
    pass

def validate_input(data: Any, expected_type: type=np.ndarray, expected_shape: Optional[tuple]=None, expected_range: Optional[tuple]=None, name: str='input') -> None:
    """
    验证输入数据
    
    Args:
        data: 要验证的数据
        expected_type: 期望的数据类型
        expected_shape: 期望的形状（None表示不检查）
        expected_range: 期望的值范围 (min, max)（None表示不检查）
        name: 数据名称，用于错误消息
        
    Raises:
        ValidationError: 验证失败时
    """
    if not isinstance(data, expected_type):
        raise ValidationError(f'{name} must be {expected_type.__name__}, got {type(data).__name__}')
    if expected_type == np.ndarray or isinstance(data, np.ndarray):
        if expected_shape is not None:
            if data.shape != expected_shape:
                raise ValidationError(f'{name} shape mismatch: expected {expected_shape}, got {data.shape}')
        if expected_range is not None:
            min_val, max_val = expected_range
            actual_min, actual_max = (np.min(data), np.max(data))
            if actual_min < min_val or actual_max > max_val:
                raise ValidationError(f'{name} values out of range: expected [{min_val}, {max_val}], got [{actual_min:.6f}, {actual_max:.6f}]')

def validate_backend(backend: str, model_type: Optional[str]=None, inference_result: Optional[Any]=None) -> None:
    """
    验证后端的有效性和结果一致性
    
    Args:
        backend: 后端名称
        model_type: 模型类型（可选）
        inference_result: 推理结果（可选）
        
    Raises:
        ValidationError: 验证失败时
    """
    valid_backends = ['nn', 'spice', 'numpy', 'timeseries', 'batch', 'layer']
    if backend not in valid_backends:
        raise ValidationError(f"Invalid backend '{backend}'. Valid options: {', '.join(valid_backends)}")
    if model_type == 'WaveNet5' and backend == 'spice':
        if inference_result is not None:
            validate_wavenet5_spice_result(inference_result)
    if inference_result is not None:
        validate_inference_result(inference_result, backend)

def validate_wavenet5_spice_result(result: Any) -> None:
    """
    验证WaveNet5的SPICE推理结果
    
    Args:
        result: 推理结果
        
    Raises:
        ValidationError: 验证失败时
    """
    if not hasattr(result, 'backend_type'):
        raise ValidationError("Result missing 'backend_type' attribute")
    if result.backend_type != 'spice':
        raise ValidationError(f"Result claims to be from '{result.backend_type}' backend, but was processed as 'spice'")
    if hasattr(result, 'metadata'):
        if not result.metadata.get('phase_correction_applied', False):
            logger.warning('警告: WaveNet5 SPICE推理未应用相位修正')

def validate_inference_result(result: Any, backend: str) -> None:
    """
    验证推理结果的完整性
    
    Args:
        result: 推理结果
        backend: 使用的后端
        
    Raises:
        ValidationError: 验证失败时
    """
    required_attrs = ['backend_type', 'execution_time']
    for attr in required_attrs:
        if not hasattr(result, attr):
            raise ValidationError(f"Result missing required attribute '{attr}'")
    if result.backend_type != backend:
        raise ValidationError(f"Backend mismatch: expected '{backend}', got '{result.backend_type}'")
    if hasattr(result, 'output_wave'):
        if result.output_wave is None:
            raise ValidationError('Result has null output_wave')
    elif hasattr(result, 'output'):
        if result.output is None:
            raise ValidationError('Result has null output')
    else:
        raise ValidationError('Result missing output data')

def validate_project_path(project_path: Union[str, Path]) -> Path:
    """
    验证项目路径
    
    Args:
        project_path: 项目路径
        
    Returns:
        Path: 验证后的路径对象
        
    Raises:
        ValidationError: 路径无效时
    """
    path = Path(project_path)
    if not path.exists():
        raise ValidationError(f'Project path does not exist: {path}')
    if not path.is_dir():
        raise ValidationError(f'Project path is not a directory: {path}')
    config_file = path / 'config.json'
    if not config_file.exists():
        raise ValidationError(f'Project missing config.json: {path}')
    return path

def validate_layer_index(layer_index: int, model_type: str, total_layers: Optional[int]=None) -> None:
    """
    验证层索引的有效性
    
    Args:
        layer_index: 层索引
        model_type: 模型类型
        total_layers: 总层数（可选）
        
    Raises:
        ValidationError: 层索引无效时
    """
    if layer_index < 1:
        raise ValidationError(f'Layer index must be >= 1, got {layer_index}')
    if model_type == 'WaveNet5':
        if layer_index > 5:
            raise ValidationError(f'WaveNet5 only has 5 layers, got layer {layer_index}')
    if total_layers is not None:
        if layer_index > total_layers:
            raise ValidationError(f'Layer index {layer_index} exceeds total layers {total_layers}')