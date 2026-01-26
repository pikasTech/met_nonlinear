"""
推理管理模块

将原有的 manager.py 拆分为更小的、职责单一的模块
"""

from .inference_manager import InferenceManager

__all__ = ['InferenceManager']