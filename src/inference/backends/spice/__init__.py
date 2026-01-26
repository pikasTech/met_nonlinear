import logging

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
'\nSPICE inference backend module.\n\nThis module provides SPICE circuit simulation capabilities for neural network models.\n'
from .backend import SPICEBackend
__all__ = ['SPICEBackend']