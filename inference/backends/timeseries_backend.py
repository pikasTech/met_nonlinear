import logging
logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
"\nTimeSeries inference backend.\n\nThis backend processes time series data using the model's time_response method.\n"
from typing import Union
from calibration_analyzer.wavedata import WaveData, WaveRecord
from .base import InferenceBackend

class TimeSeriesBackend(InferenceBackend):
    """
    TimeSeries推理后端，用于处理时序数据的推理

    基于模型的time_response方法进行推理
    """

    def __init__(self, model=None):
        """
        初始化TimeSeries推理后端

        参数:
            model: BaseModel的子类实例，必须实现time_response方法
        """
        super().__init__(model)
        if model is not None and (not hasattr(model, 'time_response')):
            raise ValueError('模型必须实现time_response方法')

    def infer(self, input_wave_data: Union[str, WaveData], use_scaler=False, layers=None) -> WaveData:
        """
        使用模型的time_response方法对输入波形进行推理

        参数:
            input_wave_data: 输入波形数据对象或波形文件路径
            use_scaler: 是否使用缩放器
            layers: 此后端不支持部分层推理，该参数被忽略

        返回:
            WaveData: 包含推理结果的波形数据对象
        """
        input_wave_data = self._prepare_input_data(input_wave_data)
        output_wave_data = self._create_output_container(input_wave_data)
        for idx, record in enumerate(input_wave_data.records):
            input_ts = record.to_time_series(0)
            output_ts = self.model.time_response(input_ts, batch_size=128, use_scaler=use_scaler)
            output_record = WaveRecord.from_time_series(output_ts, channel_names=['Output'], record_id=record.record_id, user_metadata=record.user_metadata)
            output_wave_data.add_record(output_record)
            if (idx + 1) % 10 == 0 or idx + 1 == len(input_wave_data.records):
                logger.info(f'已完成 {idx + 1}/{len(input_wave_data.records)} 条记录的推理')
        self._add_metadata(output_wave_data, input_wave_data, 'TimeSeriesBackend')
        return output_wave_data