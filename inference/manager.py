"""
推理管理器模块（兼容层）

这个文件保持向后兼容性，实际功能已经迁移到 management/ 子模块
"""

# 保持向后兼容的导入
from .management import InferenceManager

# 导出主要接口
__all__ = ['InferenceManager']