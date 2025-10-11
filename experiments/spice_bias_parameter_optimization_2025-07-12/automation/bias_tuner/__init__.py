"""
Bias Tuner - Automated SPICE bias compensation tuning tool.

A zero-dependency tool for optimizing bias compensation parameters
in neural network SPICE implementations.
"""

from .tuner import BiasTuner
from .core import CompensationStrategy

__version__ = "0.1.0"
__author__ = "Claude Code Assistant"

__all__ = [
    'BiasTuner',
    'CompensationStrategy'
]