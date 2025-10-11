"""
Shared utilities for inference backends.

This module contains common functions used across multiple backends
to reduce code duplication.
"""
import logging
from typing import Tuple, List
import numpy as np
from calibration_analyzer.wavedata import WaveData, WaveRecord

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

def prepare_batch_data(input_wave_data: WaveData) -> Tuple[np.ndarray, List[WaveRecord]]:
    """
    准备批量处理数据
    
    这是一个共享的实用函数，被BatchPredictBackend和LayerByLayerBackend使用。

    参数:
        input_wave_data: 输入波形数据

    返回:
        Tuple[np.ndarray, List[WaveRecord]]: 批处理输入数据和对应的记录列表
        输出形状: (num_records, time_steps, features)
    """
    record_refs = []
    num_records = len(input_wave_data.records)
    if num_records == 0:
        return (np.array([]), [])
    time_steps = input_wave_data.time_steps_range[-1]
    batch_inputs = np.zeros((num_records, time_steps, input_wave_data.num_channels_range[-1]))
    for idx, record in enumerate(input_wave_data.records):
        single_data = record.data
        batch_inputs[idx] = single_data
        record_refs.append(record)
    return (batch_inputs, record_refs)