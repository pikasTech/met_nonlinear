"""
Base class for inference backends.

This module defines the abstract base class for all inference backends,
providing a unified interface for model inference operations.
"""
import logging
import numpy as np

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
from typing import Union, List, Dict, Optional
from abc import ABC, abstractmethod
from models.base_models import BaseModel
from calibration_analyzer.waveprocessor import WaveProcessor
from calibration_analyzer.wavedata import WaveData
from inference.unified import InferenceResult, LayerInfo, DataRange

class InferenceBackend(ABC):
    """
    推理后端抽象基类，定义推理后端的通用接口

    所有具体的推理后端都应该继承此类并实现其方法
    """

    def __init__(self, model: BaseModel=None):
        """
        初始化推理后端

        参数:
            model: 要使用的模型对象，具体类型由子类定义
        """
        self.model: BaseModel = model
        self.wave_processor = WaveProcessor()

    def set_model(self, model: BaseModel):
        """
        设置模型

        参数:
            model: 要使用的模型对象
        """
        self.model: BaseModel = model

    def _prepare_input_data(self, input_wave_data: Union[str, WaveData]) -> WaveData:
        """
        准备输入数据，如果是文件路径则加载波形文件

        参数:
            input_wave_data: 输入波形数据对象或波形文件路径

        返回:
            WaveData: 波形数据对象
        """
        if isinstance(input_wave_data, str):
            input_wave_data = self.wave_processor.load_waveform(input_wave_data)
        if self.model is None:
            raise ValueError('推理前必须先设置模型')
        return input_wave_data

    def _create_output_container(self, input_wave_data: WaveData) -> WaveData:
        """
        创建用于存储推理结果的WaveData对象

        参数:
            input_wave_data: 输入波形数据对象

        返回:
            WaveData: 用于存储推理结果的新WaveData对象
        """
        model_name = getattr(self.model, 'model_name', type(self.model).__name__)
        return WaveData(description=f'推理结果 - 模型: {model_name} - 输入: {input_wave_data.description}', author='Model Inference')

    def _add_metadata(self, output_wave_data: WaveData, input_wave_data: WaveData, backend_name: str) -> None:
        """
        为输出波形数据添加元数据

        参数:
            output_wave_data: 输出波形数据对象
            input_wave_data: 输入波形数据对象 
            backend_name: 后端名称
        """
        input_metadata = {'input_description': input_wave_data.description, 'input_author': input_wave_data.author, 'input_records_count': len(input_wave_data.records)}
        model_name = getattr(self.model, 'model_name', type(self.model).__name__)
        model_metadata = {'model_name': model_name, 'model_type': type(self.model).__name__}
        process_record = {'operation': 'model_inference', 'timestamp': np.datetime64('now').astype(str), 'model_info': model_metadata, 'input_info': input_metadata, 'backend': backend_name}
        output_wave_data.add_user_metadata('process_history', [process_record])
        output_wave_data.add_user_metadata('model_info', model_metadata)
        output_wave_data.add_user_metadata('input_info', input_metadata)
        output_wave_data.add_user_metadata('backend_info', {'type': backend_name})
        output_wave_data.add_user_metadata('type', 'inference_result')

    @abstractmethod
    def infer(self, input_wave_data: Union[str, WaveData], use_scaler=False) -> WaveData:
        """
        对输入波形进行推理

        参数:
            input_wave_data: 输入波形数据对象或波形文件路径
            use_scaler: 是否使用缩放器

        返回:
            WaveData: 包含推理结果的波形数据对象
        """
        raise NotImplementedError('子类必须实现此方法')

    def _create_unified_result(self, backend_type: str, layers_data: Union[WaveData, List[WaveData]], input_path: str='', output_dir: str='', numpy_layers: Optional[List[WaveData]]=None) -> InferenceResult:
        """
        创建统一的推理结果对象
        
        参数:
            backend_type: 后端类型 ('nn', 'spice', 'numpy')
            layers_data: 层数据，可以是单个WaveData或列表
            input_path: 输入文件路径
            output_dir: 输出目录
            numpy_layers: NumPy层数据（可选）
            
        返回:
            InferenceResult: 统一格式的推理结果
        """
        if isinstance(layers_data, WaveData):
            layers_list = [layers_data]
        else:
            layers_list = layers_data
        layer_infos = []
        for i, wave_data in enumerate(layers_list):
            layer_info = LayerInfo(layer_index=i, layer_name=f'Layer_{i + 1}', data=wave_data, data_range=DataRange.from_wavedata(wave_data), is_scaled=False, metadata={})
            layer_infos.append(layer_info)
        numpy_layer_infos = None
        if numpy_layers:
            numpy_layer_infos = []
            for i, wave_data in enumerate(numpy_layers):
                layer_info = LayerInfo(layer_index=i, layer_name=f'NumPy_Layer_{i + 1}', data=wave_data, data_range=DataRange.from_wavedata(wave_data), is_scaled=False, metadata={'backend': 'numpy'})
                numpy_layer_infos.append(layer_info)
        model_name = getattr(self.model, 'model_name', type(self.model).__name__)
        result = InferenceResult(backend_type=backend_type, model_name=model_name, input_path=input_path, output_dir=output_dir, layers=layer_infos, numpy_layers=numpy_layer_infos, metadata={'model_type': type(self.model).__name__, 'backend_class': type(self).__name__})
        return result

    def infer_unified(self, input_wave_data: Union[str, WaveData], use_scaler: bool=False, **kwargs) -> InferenceResult:
        """
        统一格式的推理接口
        
        参数:
            input_wave_data: 输入波形数据对象或波形文件路径
            use_scaler: 是否使用缩放器
            **kwargs: 其他后端特定参数
            
        返回:
            InferenceResult: 统一格式的推理结果
        """
        result = self.infer(input_wave_data, use_scaler, **kwargs)
        input_path = ''
        if isinstance(input_wave_data, str):
            input_path = input_wave_data
        backend_type = 'nn'
        if 'spice' in self.__class__.__name__.lower():
            backend_type = 'spice'
        elif 'numpy' in self.__class__.__name__.lower():
            backend_type = 'numpy'
        return self._create_unified_result(backend_type=backend_type, layers_data=result, input_path=input_path, output_dir='', numpy_layers=None)