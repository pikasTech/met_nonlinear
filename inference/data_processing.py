import logging
logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
'\n数据处理模块\n\n此模块包含与推理数据处理相关的功能，包括：\n- 波形数据加载和保存\n- 数据缩放处理\n- 推理执行和结果保存\n'
import os
import numpy as np
from typing import Union, Optional, Dict, Any, List
from calibration_analyzer.waveprocessor import WaveProcessor
from calibration_analyzer.wavedata import WaveData, WaveRecord
from calibration_analyzer.exam_class import TimeSeries
from models.layer_support import LayeredModelSupport
from .unified import UnifiedInferenceProcessor, InferenceResult, LegacyAPIError
USE_SCALER = True

class InferenceDataProcessor:
    """
    推理数据处理器
    
    负责处理所有与推理数据相关的功能，包括加载、缩放、推理执行和保存
    """

    def __init__(self, processor):
        """
        初始化数据处理器
        
        参数:
            processor: InferenceProcessor实例
        """
        self.processor = processor
        self.wave_processor = processor.wave_processor
        self.model = processor.model
        self.model_engine = processor.model_engine

    @property
    def backend(self):
        """动态获取当前的后端，确保始终使用最新的"""
        return self.processor.backend

    def load_input_wave(self, wave_file_path: str) -> WaveData:
        """
        加载输入波形文件

        参数:
            wave_file_path: 输入波形文件路径

        返回:
            WaveData: 加载的波形数据对象
        """
        logger.info(f'正在加载输入波形文件: {wave_file_path}')
        
        # 使用处理器的新过滤功能
        wave_data = self.processor._load_wave_data_with_filter(wave_file_path)
        
        logger.info(f'已加载波形文件，包含 {len(wave_data.records)} 个记录')
        
        # 显示快速模式信息
        if hasattr(wave_data, 'user_metadata') and wave_data.user_metadata.get('quick_mode', False):
            logger.info(f'⚡ 快速模式已激活，数据已筛选为最小最大震级')
        
        # 计算并显示数据范围
        all_data = []
        for record in wave_data.records:
            all_data.append(record.data.flatten())
        if all_data:
            all_data = np.concatenate(all_data)
            logger.info(f'  数据范围: 最小值={all_data.min():.6f}, 最大值={all_data.max():.6f}')
        return wave_data

    def save_output_wave(self, output_wave_data: WaveData, output_file_path: str, compress: bool=True) -> str:
        """
        保存推理结果波形到文件

        参数:
            output_wave_data: 输出波形数据对象
            output_file_path: 输出波形文件路径
            compress: 是否压缩文件

        返回:
            str: 保存的文件路径
        """
        logger.info(f'正在保存推理结果到: {output_file_path}')
        self.wave_processor.save_waveform(output_file_path, output_wave_data, compress=compress)
        logger.info(f'推理结果已保存')
        return output_file_path if output_file_path.endswith('.wave') else f'{output_file_path}.wave'

    def _apply_input_scaling(self, input_wave_data: WaveData) -> WaveData:
        """
        对输入波形数据应用缩放器

        参数:
            input_wave_data: 输入波形数据

        返回:
            WaveData: 缩放后的波形数据
        """
        if not hasattr(self.model_engine, 'scaler') or self.model_engine.scaler is None:
            return input_wave_data
        scaled_wave_data = WaveData(description=f'缩放后的输入数据 - {input_wave_data.description}', author='InferenceProcessor')
        for record in input_wave_data.records:
            original_data = record.data
            scaled_data = self.model_engine.scaler.transform_x(original_data.reshape(-1, original_data.shape[-1])).reshape(original_data.shape)
            scaled_record = WaveRecord(data=scaled_data, sample_rate=record.sample_rate, channel_names=record.channel_names, record_id=record.record_id, user_metadata={**record.user_metadata, 'scaled_input': True})
            scaled_wave_data.add_record(scaled_record)
        original_min, original_max = (float('inf'), float('-inf'))
        scaled_min, scaled_max = (float('inf'), float('-inf'))
        for orig_record, scaled_record in zip(input_wave_data.records, scaled_wave_data.records):
            orig_data = orig_record.data.flatten()
            scaled_data = scaled_record.data.flatten()
            original_min = min(original_min, orig_data.min())
            original_max = max(original_max, orig_data.max())
            scaled_min = min(scaled_min, scaled_data.min())
            scaled_max = max(scaled_max, scaled_data.max())
        logger.info(f'  缩放前范围: 最小值={original_min:.6f}, 最大值={original_max:.6f}')
        logger.info(f'  缩放后范围: 最小值={scaled_min:.6f}, 最大值={scaled_max:.6f}')
        return scaled_wave_data

    def _apply_output_inverse_scaling(self, output_wave_data: WaveData) -> WaveData:
        """
        对输出波形数据应用反缩放器

        参数:
            output_wave_data: 推理输出的波形数据

        返回:
            WaveData: 反缩放后的波形数据
        """
        if not hasattr(self.model_engine, 'scaler') or self.model_engine.scaler is None:
            return output_wave_data
        unscaled_wave_data = WaveData(description=f'反缩放后的输出数据 - {output_wave_data.description}', author='InferenceProcessor')
        for record in output_wave_data.records:
            scaled_data = record.data
            unscaled_data = self.model_engine.scaler.inverse_transform_y(scaled_data.reshape(-1, scaled_data.shape[-1])).reshape(scaled_data.shape)
            unscaled_record = WaveRecord(data=unscaled_data, sample_rate=record.sample_rate, channel_names=record.channel_names, record_id=record.record_id, user_metadata={**record.user_metadata, 'unscaled_output': True})
            unscaled_wave_data.add_record(unscaled_record)
        for key, value in output_wave_data.user_metadata.items():
            unscaled_wave_data.add_user_metadata(key, value)
        scaled_min, scaled_max = (float('inf'), float('-inf'))
        unscaled_min, unscaled_max = (float('inf'), float('-inf'))
        for scaled_record, unscaled_record in zip(output_wave_data.records, unscaled_wave_data.records):
            scaled_data = scaled_record.data.flatten()
            unscaled_data = unscaled_record.data.flatten()
            scaled_min = min(scaled_min, scaled_data.min())
            scaled_max = max(scaled_max, scaled_data.max())
            unscaled_min = min(unscaled_min, unscaled_data.min())
            unscaled_max = max(unscaled_max, unscaled_data.max())
        logger.info(f'  反缩放前范围: 最小值={scaled_min:.6f}, 最大值={scaled_max:.6f}')
        logger.info(f'  反缩放后范围: 最小值={unscaled_min:.6f}, 最大值={unscaled_max:.6f}')
        return unscaled_wave_data

    def infer_and_save(self, input_wave_path: str, output_wave_path: str=None, layer_output_dir: str=None, use_scaler=False, return_layers: bool=None, return_numpy: bool=False, numpy_output_dir: str=None, save_intermediate: bool=True, output_dir: str=None, layers: int=None, **kwargs) -> InferenceResult:
        """
        执行推理并保存结果
        
        Args:
            input_wave_path: 输入波形文件路径
            output_wave_path: [已废弃] 请使用 output_dir 参数
            layer_output_dir: [已废弃] 层输出会自动保存到 output_dir/xxx_layers/
            use_scaler: 是否使用缩放器
            return_layers: 是否返回分层结果
            return_numpy: 是否同时进行NumPy推理（仅SPICE后端）
            numpy_output_dir: [已废弃] NumPy输出会自动保存到 output_dir/numpy_layers/
            save_intermediate: [已废弃] 由 return_layers 控制
            output_dir: 输出目录路径
            layers: 只推理前N层（None表示推理所有层）
            **kwargs: 传递给后端的额外参数
            
        Returns:
            InferenceResult: 统一的推理结果
            
        Raises:
            LegacyAPIError: 如果使用了已废弃的参数组合
        """
        if output_wave_path and (not output_dir):
            output_dir = os.path.dirname(output_wave_path)
            if not output_dir:
                output_dir = '.'
            logger.info(f"警告: output_wave_path参数已废弃，自动使用output_dir='{output_dir}'")
        if layer_output_dir or numpy_output_dir:
            raise LegacyAPIError('layer_output_dir和numpy_output_dir参数已废弃。\n分层输出会自动保存到：\n- {output_dir}/nn_layers/ (NN后端)\n- {output_dir}/spice_layers/ (SPICE后端)\n- {output_dir}/numpy_layers/ (NumPy仿真)')
        if save_intermediate is not True:
            logger.warning('警告: save_intermediate参数已废弃，现在由return_layers控制')
        if not output_dir:
            raise ValueError('必须指定output_dir参数')
        if return_layers is None:
            return_layers = False
        processor = UnifiedInferenceProcessor(self.backend, self.model_engine)
        expected_backend = self.processor.backend
        if self.backend is not expected_backend:
            separator = '=' * 60
            raise RuntimeError(f'\n{separator}\n❌ 严重错误：后端不一致！\n{separator}\nInferenceDataProcessor.backend: {self.backend.__class__.__name__}\nInferenceProcessor.backend: {expected_backend.__class__.__name__}\n这种不一致可能导致使用错误的后端执行推理。\n绝对不允许这种情况发生！\n{separator}\n')
        result = processor.process(input_wave_path=input_wave_path, output_dir=output_dir, use_scaler=use_scaler, return_layers=return_layers, return_numpy=return_numpy, layers=layers, **kwargs)
        current_backend_type = self.backend.__class__.__name__.lower()
        if 'spice' in current_backend_type:
            expected_type = 'spice'
        elif 'layer' in current_backend_type or 'batch' in current_backend_type:
            expected_type = 'nn'
        else:
            expected_type = 'nn'
        if result.backend_type != expected_type:
            raise RuntimeError(f"\n{'=' * 60}\n❌ 严重错误：推理结果类型不匹配！\n{'=' * 60}\n当前后端: {self.backend.__class__.__name__}\n期望结果类型: '{expected_type}'\n实际结果类型: '{result.backend_type}'\n实际后端类: {result.metadata.get('actual_backend_class', 'Unknown')}\n\n这表明推理过程中发生了后端混淆。\n绝对不允许用一个后端的结果冒充另一个后端！\n这会使整个项目的研究结果失效。\n{'=' * 60}\n")
        logger.info(f'[DataProcessor] 推理完成，后端验证通过: {result.backend_type}')
        return result