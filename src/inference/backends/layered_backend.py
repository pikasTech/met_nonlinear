import logging
logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
'\nLayer-by-layer inference backend.\n\nThis backend performs inference layer by layer for models that support\nlayered execution, allowing inspection of intermediate outputs.\n'
from typing import Union, List
from calibration_analyzer.wavedata import WaveData, WaveRecord
from models.layer_support import LayeredModelSupport
from .base import InferenceBackend
from .utils import prepare_batch_data

class LayerByLayerBackend(InferenceBackend):
    """
    分层推理后端，用于对支持分层的模型进行逐层推理

    适用于实现了LayeredModelSupport接口的模型，可以返回每一层的输出结果
    """

    def __init__(self, model=None):
        """
        初始化分层推理后端

        参数:
            model: 必须实现LayeredModelSupport接口的模型实例
        """
        super().__init__(model)
        if model is not None and (not isinstance(model, LayeredModelSupport)):
            raise ValueError('模型必须实现LayeredModelSupport接口才能使用分层推理')

    def infer(self, input_wave_data: Union[str, WaveData], use_scaler=False, layers=None) -> List[WaveData]:
        """
        对输入波形进行分层推理

        参数:
            input_wave_data: 输入波形数据对象或波形文件路径
            use_scaler: 是否使用缩放器
            layers: 只推理前N层（None表示推理所有层）

        返回:
            List[WaveData]: 包含每一层推理结果的波形数据对象列表
        """
        if not isinstance(self.model, LayeredModelSupport):
            raise ValueError('模型必须实现LayeredModelSupport接口才能使用分层推理')
        input_wave_data = self._prepare_input_data(input_wave_data)
        layered_models = self.model.get_layered_models()
        if len(layered_models) == 0:
            raise ValueError('未找到任何分层模型')
        
        # 确定要推理的层数
        total_layers = len(layered_models)
        if layers is not None:
            num_layers_to_infer = min(layers, total_layers)
            if layers > total_layers:
                logger.warning(f'请求推理 {layers} 层，但模型只有 {total_layers} 层。将推理所有 {total_layers} 层。')
        else:
            num_layers_to_infer = total_layers
        
        logger.info(f'将推理前 {num_layers_to_infer}/{total_layers} 层')
        
        batch_inputs, record_refs = prepare_batch_data(input_wave_data)
        total_records = len(batch_inputs)
        if total_records == 0:
            logger.info('没有记录需要处理')
            return []
        layer_results = []
        for layer_idx in range(num_layers_to_infer):
            layer_model = layered_models[layer_idx]
            logger.info(f'正在处理第 {layer_idx + 1}/{num_layers_to_infer} 层（模型共 {total_layers} 层）')
            layer_output = self._create_layer_output_container(input_wave_data)
            if layer_idx == 0:
                layer_inputs = batch_inputs
            else:
                previous_outputs = layer_outputs
                layer_inputs = previous_outputs
            layer_outputs = layer_model.predict(layer_inputs, batch_size=32)
            for idx, (record_ref, output) in enumerate(zip(record_refs, layer_outputs)):
                output_channels = output.shape[-1]
                channel_names = [f'Channel_{i + 1}' for i in range(output_channels)]
                fs = record_ref.to_time_series(0).fs
                output_record = WaveRecord(data=output, sample_rate=fs, channel_names=channel_names, record_id=f'{record_ref.record_id}_layer{layer_idx + 1}', user_metadata={**record_ref.user_metadata, 'layer_index': layer_idx})
                layer_output.add_record(output_record)
            self._add_metadata(layer_output, input_wave_data, f'LayerByLayerBackend_Layer{layer_idx + 1}')
            layer_output.add_user_metadata('layer_index', layer_idx)
            layer_output.add_user_metadata('total_layers_in_model', total_layers)
            layer_output.add_user_metadata('layers_inferred', num_layers_to_infer)
            layer_results.append(layer_output)
            logger.info(f'已完成第 {layer_idx + 1}/{num_layers_to_infer} 层的推理')
            layer_min, layer_max = (float('inf'), float('-inf'))
            for record in layer_output.records:
                data = record.data.flatten()
                layer_min = min(layer_min, data.min())
                layer_max = max(layer_max, data.max())
            logger.info(f'  第{layer_idx + 1}层输出范围: 最小值={layer_min:.6f}, 最大值={layer_max:.6f}')
        return layer_results

    def _create_layer_output_container(self, input_wave_data: WaveData) -> WaveData:
        """
        创建用于存储层推理结果的WaveData对象

        参数:
            input_wave_data: 输入波形数据对象

        返回:
            WaveData: 用于存储层推理结果的新WaveData对象
        """
        model_name = getattr(self.model, 'model_name', type(self.model).__name__)
        return WaveData(description=f'推理结果 - 模型: {model_name} - 层 - 输入: {input_wave_data.description}', author='Layer Inference')