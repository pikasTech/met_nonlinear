import logging

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
'\nInference backends module.\n\nThis module provides various inference backend implementations\nfor different deployment scenarios.\n'
from .base import InferenceBackend
from .timeseries_backend import TimeSeriesBackend
from .batch_backend import BatchPredictBackend
from .layered_backend import LayerByLayerBackend
from .spice.backend import SPICEBackend
__all__ = ['InferenceBackend', 'TimeSeriesBackend', 'BatchPredictBackend', 'LayerByLayerBackend', 'SPICEBackend']