"""
测试数据生成器模块
"""

from .bias_test_signals import (
    generate_pure_dc_signal,
    generate_dc_with_sine,
    generate_transient_signal,
    generate_multi_frequency_signal,
    generate_noisy_signal,
    generate_drift_signal,
    generate_complex_signal,
    create_test_signal_suite,
    get_test_signals
)

__all__ = [
    'generate_pure_dc_signal',
    'generate_dc_with_sine',
    'generate_transient_signal',
    'generate_multi_frequency_signal',
    'generate_noisy_signal',
    'generate_drift_signal',
    'generate_complex_signal',
    'create_test_signal_suite',
    'get_test_signals'
]