import logging
logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
"\nBatch prediction inference backend.\n\nThis backend processes data in batches using the model's predict method\nfor improved efficiency.\n"
from typing import Union
from calibration_analyzer.wavedata import WaveData, WaveRecord
from calibration_analyzer.exam_class import TimeSeries
from .base import InferenceBackend
from .utils import prepare_batch_data

class BatchPredictBackend(InferenceBackend):
    """
    BatchPredict推理后端，用于批量处理数据的推理

    基于模型的predict方法进行批量推理，效率更高
    """

    def __init__(self, model=None, batch_size: int=32):
        """
        初始化BatchPredict推理后端

        参数:
            model: 必须实现predict方法的模型实例
            batch_size: 批处理大小
        """
        super().__init__(model)
        self.batch_size = batch_size
        if model is not None and (not hasattr(model, 'predict')):
            raise ValueError('模型必须实现predict方法')

    def infer(self, input_wave_data: Union[str, WaveData], use_scaler=False, layers=None) -> WaveData:
        """
        使用模型的predict方法对输入波形进行批量推理

        参数:
            input_wave_data: 输入波形数据对象或波形文件路径
            use_scaler: 是否使用缩放器
            layers: 此后端不支持部分层推理，该参数被忽略

        返回:
            WaveData: 包含推理结果的波形数据对象
        """
        input_wave_data = self._prepare_input_data(input_wave_data)
        output_wave_data = self._create_output_container(input_wave_data)
        batch_inputs, record_refs = prepare_batch_data(input_wave_data)
        total_records = len(batch_inputs)
        if total_records == 0:
            logger.info('没有记录需要处理')
            return output_wave_data
        time_steps = batch_inputs.shape[1] if batch_inputs.shape[0] > 0 else 0
        batch_size_for_predict = self.batch_size
        all_outputs = self.model.predict(batch_inputs, batch_size=batch_size_for_predict, use_scaler=use_scaler)
        for idx, (record_ref, output) in enumerate(zip(record_refs, all_outputs)):
            fs = record_ref.to_time_series(0).fs
            output_ts = TimeSeries(output, fs)
            output_record = WaveRecord.from_time_series(output_ts, channel_names=['Output'], record_id=record_ref.record_id, user_metadata=record_ref.user_metadata)
            output_wave_data.add_record(output_record)
        logger.info(f'已完成 {total_records} 条记录的推理')
        self._add_metadata(output_wave_data, input_wave_data, 'BatchPredictBackend')
        return output_wave_data