"""
模型分层输出支持模块

此模块提供模型分层输出的接口定义和实现。
"""
from typing import List, Dict, Any, Tuple, Optional, Union
import tensorflow as tf
from tensorflow.keras import models, layers
from .base_models import BaseModel
from calibration_analyzer.wavedata import WaveData


class LayeredModelSupport:
    """
    分层模型支持接口

    实现此接口的模型可以返回每一层的输出结果
    """

    def get_layered_models(self):
        """
        获取模型的分层版本列表

        Returns:
            List[tf.keras.Model]: 模型的分层版本列表，按照数据流顺序排列
        """
        raise NotImplementedError("子类必须实现此方法")

    def get_layers_info(self) -> List[Dict[str, Any]]:
        """
        获取每一层的信息

        Returns:
            List[Dict[str, Any]]: 包含每一层信息的字典列表
        """
        raise NotImplementedError("子类必须实现此方法")


class SpiceModelSupport:
    """
    SPICE模型支持接口

    实现此接口的模型可以返回SPICE分层输出结果
    """

    def to_spice(self, output_path: str = None, opamp_config: Dict[str, Any] = None, use_e96: bool = False, amp=1.0):
        pass

    def post_process(self, output_wave: WaveData):
        return output_wave
