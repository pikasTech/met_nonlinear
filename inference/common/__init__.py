import logging

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
'\nCommon utilities for inference module.\n\nThis package provides shared functionality to reduce code duplication:\n- Data range checking and analysis\n- Input validation\n- Unified logging\n'
from .data_range import DataRangeInfo, DataRangeChecker
from .validation import ValidationError, validate_input, validate_backend
from .logger import InferenceLogger
__all__ = ['DataRangeInfo', 'DataRangeChecker', 'ValidationError', 'validate_input', 'validate_backend', 'InferenceLogger']