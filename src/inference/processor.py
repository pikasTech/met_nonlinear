"""
推理处理器模块（兼容层）

这个文件保持向后兼容性，实际功能已经迁移到 processing/ 子模块
"""

# 保持向后兼容的导入
from .processing import InferenceProcessor

# 全局常量（向后兼容）
USE_SCALER = True

# 导出主要接口
__all__ = ['InferenceProcessor', 'USE_SCALER']