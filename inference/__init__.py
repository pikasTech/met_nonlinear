"""
Inference模块

提供模型推理功能，包括多种推理后端、可视化和分析工具。
"""
import logging

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
from .processor import InferenceProcessor
from .visualization import InferenceVisualizer
from .data_processing import InferenceDataProcessor
from .spice_analysis import SPICEAnalyzer
from .cli import main
from .manager import InferenceManager
from .backends.base import InferenceBackend
from .backends.timeseries_backend import TimeSeriesBackend
from .backends.batch_backend import BatchPredictBackend
from .backends.layered_backend import LayerByLayerBackend
from .backends.spice.backend import SPICEBackend
from .wavenet5_spice_backend import WaveNet5SPICEBackend
from .utils import get_layer_paths
__all__ = ['InferenceProcessor', 'InferenceVisualizer', 'InferenceDataProcessor', 'SPICEAnalyzer', 'InferenceManager', 'InferenceBackend', 'TimeSeriesBackend', 'BatchPredictBackend', 'LayerByLayerBackend', 'SPICEBackend', 'WaveNet5SPICEBackend', 'get_layer_paths', 'main']
__version__ = '1.0.0'