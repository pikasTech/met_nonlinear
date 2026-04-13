"""
神经网络模型库 - 提供各种非线性系统建模和补偿的神经网络模型

此模块导出了所有模型类，以保持与原有的直接从models.py导入的代码兼容。
"""

# 从各个子模块导入模型类
from .utils import merge_config
from .frikan_models import (
    FRIKAN, FRIMLP, FRIKAND, FRIKAN2, FRIKAN3, FRIKAN4, 
    FRIKAN5, FRIKAN6, FRIKAN23, CNNKAN
)
from .base_models import LSTM, GRN, RNN, LSTMTransformer
from .wavenet_models import WaveNet, WaveNet2, WaveNet3, WaveNet4, WaveNet5
from .conv_models import RVTDCNN, OneDCNN, TCN, create_image_batch
from .iir_models import IIR_ONLY, simple_iir

# 版本信息
__version__ = '0.1.0'
