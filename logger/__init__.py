"""
Logger 包 - Python 日志系统增强实现

该包提供了一个模块化的日志系统，用于替代项目中的 print 语句。
"""

# Import print replacer
from .print_replacer import PrintReplacer

# Optional imports (with yaml dependency)
try:
    from .logging_setup import setup_logging, get_module_logger
    _yaml_available = True
except ImportError:
    _yaml_available = False

__version__ = "0.1.0"

# Always available
__all__ = ['PrintReplacer']

# Add yaml-dependent functions if available
if _yaml_available:
    __all__.extend(['setup_logging', 'get_module_logger'])