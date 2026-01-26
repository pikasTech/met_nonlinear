import logging
logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
'\n统一的推理架构实现\n\n本模块提供了统一的推理数据结构和处理器，解决了原有架构中\n返回值类型碎片化、处理流程分支过多等问题。\n'
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from calibration_analyzer.wavedata import WaveData, WaveRecord
import numpy as np
import os
import time

@dataclass
class DataRange:
    """数据范围统计"""
    min_value: float
    max_value: float
    mean_value: float
    std_value: float

    @classmethod
    def from_wavedata(cls, wavedata: WaveData) -> 'DataRange':
        """从WaveData计算数据范围"""
        all_data = []
        for record in wavedata.records:
            all_data.append(record.data.flatten())
        if not all_data:
            return cls(min_value=0.0, max_value=0.0, mean_value=0.0, std_value=0.0)
        data = np.concatenate(all_data)
        if data.size == 0:
            return cls(min_value=0.0, max_value=0.0, mean_value=0.0, std_value=0.0)
        return cls(min_value=float(data.min()), max_value=float(data.max()), mean_value=float(data.mean()), std_value=float(data.std()))

@dataclass
class LayerInfo:
    """单层推理信息"""
    layer_index: int
    layer_name: str
    data: WaveData
    data_range: DataRange
    is_scaled: bool
    file_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class InferenceResult:
    """统一的推理结果容器"""
    backend_type: str
    model_name: str
    input_path: str
    output_dir: str
    layers: List[LayerInfo]
    numpy_layers: Optional[List[LayerInfo]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    inference_time_ms: float = 0.0

    def get_final_output(self) -> LayerInfo:
        """获取最终输出（最后一层）"""
        return self.layers[-1]

    def has_numpy_output(self) -> bool:
        """是否包含NumPy输出"""
        return self.numpy_layers is not None

    def validate(self):
        """验证数据完整性，发现问题立即报错"""
        if not self.layers:
            raise ValueError('推理结果不能为空')
        if self.backend_type not in ['nn', 'spice', 'numpy']:
            raise ValueError(f'不支持的后端类型: {self.backend_type}')
        for i, layer in enumerate(self.layers):
            if layer.layer_index != i:
                raise ValueError(f'层索引不连续: 期望{i}, 实际{layer.layer_index}')
            if not layer.data or not layer.data.records:
                raise ValueError(f'第{i}层数据为空')

class InferenceError(Exception):
    """推理错误基类"""
    pass

class LegacyAPIError(InferenceError):
    """使用废弃API时的错误"""

    def __init__(self, message):
        super().__init__(f'检测到使用已废弃的API:\n{message}\n请参考 documentation/inference_migration_guide.md 进行迁移')

class InvalidReturnFormatError(InferenceError):
    """返回格式不正确时的错误"""
    pass

class UnifiedInferenceProcessor:
    """统一的推理处理器"""

    def __init__(self, backend, model_engine):
        self.backend = backend
        self.model_engine = model_engine
        self.scaler = model_engine.scaler if hasattr(model_engine, 'scaler') else None
        self.model_name = getattr(model_engine.config, 'use_model', 'Unknown')

    def process(self, input_wave_path: str, output_dir: str, use_scaler: bool=False, return_layers: bool=False, return_numpy: bool=False, **kwargs) -> InferenceResult:
        """
        统一的推理处理流程
        
        Args:
            input_wave_path: 输入波形文件路径
            output_dir: 输出目录
            use_scaler: 是否使用缩放器
            return_layers: 是否返回分层结果
            return_numpy: 是否同时进行NumPy推理（仅SPICE后端）
            **kwargs: 其他后端特定参数
            
        Returns:
            InferenceResult: 统一格式的推理结果
        """
        start_time = time.time()
        input_data = self._load_input(input_wave_path)
        logger.info(f'加载输入数据: {input_wave_path}')
        self._log_data_range(input_data, '输入数据')
        if use_scaler and self.scaler:
            input_data = self._apply_input_scaling(input_data)
            logger.info('已应用输入缩放')
            self._log_data_range(input_data, '缩放后输入')
        import inspect
        infer_params = {}
        if hasattr(self.backend, 'infer'):
            sig = inspect.signature(self.backend.infer)
            params = sig.parameters
            if 'return_layers' in params:
                infer_params['return_layers'] = return_layers
            if 'return_numpy' in params:
                infer_params['return_numpy'] = return_numpy
        infer_params.update(kwargs)
        raw_output = self.backend.infer(input_data, **infer_params)
        result = self._convert_to_unified(raw_output, input_wave_path, output_dir, use_scaler, return_layers, return_numpy)
        if use_scaler and self.scaler:
            self._apply_output_processing(result)
        self._save_results(result, output_dir, return_layers)
        result.inference_time_ms = (time.time() - start_time) * 1000
        result.validate()
        return result

    def _load_input(self, input_wave_path: str) -> WaveData:
        """加载输入波形文件"""
        from calibration_analyzer.waveprocessor import WaveProcessor
        wave_processor = WaveProcessor()
        input_data = wave_processor.load_waveform(input_wave_path)
        return input_data

    def _apply_input_scaling(self, input_data: WaveData) -> WaveData:
        """应用输入缩放"""
        scaled_data = WaveData(description=f'{input_data.description} (scaled)', user_metadata=input_data.user_metadata.copy() if input_data.user_metadata else {})
        for record in input_data.records:
            scaled_values = self.scaler.transform(record.data)
            scaled_record = WaveRecord(data=scaled_values, sample_rate=record.sample_rate, channel_names=record.channel_names, record_id=record.record_id, user_metadata=record.user_metadata.copy() if record.user_metadata else {})
            scaled_data.add_record(scaled_record)
        return scaled_data

    def _convert_to_unified(self, raw_output, input_path, output_dir, use_scaler, return_layers, return_numpy):
        """将后端原始输出转换为统一格式
        
        [WARNING] 关键安全检查 [WARNING]
        本方法必须严格验证后端类型，绝对不允许用一个后端的结果冒充另一个后端。
        这是项目的核心完整性保证，任何违反都会导致研究结果失效。
        """
        actual_backend_class = self.backend.__class__.__name__
        backend_type = actual_backend_class.replace('Backend', '').lower()
        if 'spice' in backend_type:
            backend_type = 'spice'
        elif 'numpy' in backend_type:
            backend_type = 'numpy'
        elif 'layer' in backend_type or 'batch' in backend_type or 'time' in backend_type:
            backend_type = 'nn'
        expected_class_patterns = {'spice': ['SPICEBackend', 'WaveNet5SPICEBackend'], 'numpy': ['NumpyBackend'], 'nn': ['LayerByLayerBackend', 'BatchPredictBackend', 'TimeSeriesBackend']}
        is_valid = False
        for pattern in expected_class_patterns.get(backend_type, []):
            if pattern in actual_backend_class:
                is_valid = True
                break
        if not is_valid:
            raise InvalidReturnFormatError(f"\n{'=' * 60}\n[FATAL ERROR] 严重错误：后端类型验证失败！\n{'=' * 60}\n检测到的后端类型: '{backend_type}'\n实际的后端类: '{actual_backend_class}'\n这种不匹配可能导致用错误的后端结果冒充正确的结果。\n这是绝对不允许的，会使整个项目的研究结果失效。\n\n请检查：\n1. 后端是否正确初始化\n2. 是否有后端切换失败但继续执行的情况\n3. 是否有代码试图伪装后端类型\n{'=' * 60}\n")
        logger.info(f'[UnifiedProcessor] 后端验证通过: {actual_backend_class} -> {backend_type}')
        result = InferenceResult(backend_type=backend_type, model_name=self.model_name, input_path=input_path, output_dir=output_dir, layers=[])
        result.metadata['actual_backend_class'] = actual_backend_class
        result.metadata['backend_validation'] = 'passed'
        if isinstance(raw_output, dict):
            if 'spice' in raw_output:
                result.layers = self._create_layer_infos(raw_output['spice'], use_scaler, 'spice')
            if 'numpy' in raw_output:
                result.numpy_layers = self._create_layer_infos(raw_output['numpy'], use_scaler, 'numpy')
        elif isinstance(raw_output, list):
            result.layers = self._create_layer_infos(raw_output, use_scaler, backend_type)
        else:
            result.layers = self._create_layer_infos([raw_output], use_scaler, backend_type)
        return result

    def _create_layer_infos(self, wave_list: List[WaveData], use_scaler: bool, prefix: str) -> List[LayerInfo]:
        """创建层信息列表"""
        layer_infos = []
        for i, wave_data in enumerate(wave_list):
            data_range = DataRange.from_wavedata(wave_data)
            layer_info = LayerInfo(layer_index=i, layer_name=f'{prefix}_layer_{i + 1}', data=wave_data, data_range=data_range, is_scaled=use_scaler, metadata=wave_data.user_metadata.copy() if wave_data.user_metadata else {})
            layer_info.metadata['layer_index'] = i
            layer_info.metadata['total_layers'] = len(wave_list)
            layer_info.metadata['layer_type'] = prefix
            if use_scaler and i < len(wave_list) - 1:
                layer_info.metadata['scaling_status'] = 'scaled'
            logger.info(f'  第{i + 1}层输出范围: 最小值={data_range.min_value:.6f}, 最大值={data_range.max_value:.6f}')
            layer_infos.append(layer_info)
        return layer_infos

    def _apply_output_processing(self, result: InferenceResult):
        """应用输出处理，包括选择性反缩放"""
        final_layer = result.get_final_output()
        if not final_layer.metadata.get('inverse_scaled', False):
            logger.info(f'对最终输出应用反缩放...')
            final_layer.data = self._apply_inverse_scaling(final_layer.data)
            final_layer.is_scaled = False
            final_layer.metadata['inverse_scaled'] = True
            final_layer.metadata['scaling_status'] = 'unscaled'
            final_layer.data_range = DataRange.from_wavedata(final_layer.data)
            self._log_data_range(final_layer.data, f'反缩放后的第{final_layer.layer_index + 1}层')
        if result.has_numpy_output():
            numpy_final = result.numpy_layers[-1]
            if not numpy_final.metadata.get('inverse_scaled', False):
                logger.info(f'对NumPy最终输出应用反缩放...')
                numpy_final.data = self._apply_inverse_scaling(numpy_final.data)
                numpy_final.is_scaled = False
                numpy_final.metadata['inverse_scaled'] = True
                numpy_final.metadata['scaling_status'] = 'unscaled'
                numpy_final.data_range = DataRange.from_wavedata(numpy_final.data)
                self._log_data_range(numpy_final.data, f'反缩放后的NumPy第{numpy_final.layer_index + 1}层')

    def _apply_inverse_scaling(self, wave_data: WaveData) -> WaveData:
        """应用反缩放"""
        unscaled_data = WaveData(description=wave_data.description, user_metadata=wave_data.user_metadata.copy() if wave_data.user_metadata else {})
        for record in wave_data.records:
            unscaled_values = self.scaler.inverse_transform(record.data)
            unscaled_record = WaveRecord(data=unscaled_values, sample_rate=record.sample_rate, channel_names=record.channel_names, record_id=record.record_id, user_metadata=record.user_metadata.copy() if record.user_metadata else {})
            unscaled_data.add_record(unscaled_record)
        return unscaled_data

    def _save_results(self, result: InferenceResult, output_dir: str, return_layers: bool):
        """保存推理结果到文件"""
        os.makedirs(output_dir, exist_ok=True)
        if return_layers:
            layer_dir = os.path.join(output_dir, f'{result.backend_type}_layers')
            os.makedirs(layer_dir, exist_ok=True)
            for layer in result.layers:
                filename = f'{self.model_name}_{result.backend_type}_layer{layer.layer_index + 1}.wave'
                file_path = os.path.join(layer_dir, filename)
                from calibration_analyzer.waveprocessor import WaveProcessor
                wave_processor = WaveProcessor()
                wave_processor.save_waveform(file_path, layer.data)
                layer.file_path = file_path
        else:
            final_layer = result.get_final_output()
            filename = f'{self.model_name}_{result.backend_type}_output.wave'
            file_path = os.path.join(output_dir, filename)
            from calibration_analyzer.waveprocessor import WaveProcessor
            wave_processor = WaveProcessor()
            wave_processor.save_waveform(file_path, final_layer.data)
            final_layer.file_path = file_path
        if result.has_numpy_output():
            numpy_dir = os.path.join(output_dir, 'numpy_layers')
            os.makedirs(numpy_dir, exist_ok=True)
            for layer in result.numpy_layers:
                filename = f'{self.model_name}_numpy_layer{layer.layer_index + 1}.wave'
                file_path = os.path.join(numpy_dir, filename)
                from calibration_analyzer.waveprocessor import WaveProcessor
                wave_processor = WaveProcessor()
                wave_processor.save_waveform(file_path, layer.data)
                layer.file_path = file_path

    def _log_data_range(self, wave_data: WaveData, description: str):
        """记录数据范围"""
        data_range = DataRange.from_wavedata(wave_data)
        logger.info(f'{description}范围: 最小值={data_range.min_value:.6f}, 最大值={data_range.max_value:.6f}')