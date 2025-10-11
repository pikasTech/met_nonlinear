"""
推理结果可视化模块（兼容层）

这个文件保持向后兼容性，实际功能已经迁移到 visualization/ 子模块
"""

# 保持向后兼容的导入
from .visualization import InferenceVisualizer

# 导出主要接口
__all__ = ['InferenceVisualizer']