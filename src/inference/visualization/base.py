"""
基础可视化器模块

提供可视化器的基础类和通用功能
"""

import logging
import matplotlib.pyplot as plt
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..processor import InferenceProcessor

logger = logging.getLogger(__name__)


class InferenceVisualizer:
    """
    推理结果可视化器
    
    负责处理所有与推理结果可视化相关的功能
    """
    
    def __init__(self, processor: 'InferenceProcessor'):
        """
        初始化可视化器
        
        参数:
            processor: InferenceProcessor实例
        """
        self.processor = processor
        self.wave_processor = processor.wave_processor
        self.model = processor.model
        self.model_engine = processor.model_engine
        
        # 延迟加载的组件
        self._waveform_visualizer = None
        self._layered_visualizer = None
        self._comparison_visualizer = None
    
    @property
    def waveform_visualizer(self):
        """延迟加载波形可视化器"""
        if self._waveform_visualizer is None:
            from .waveform import WaveformVisualizer
            self._waveform_visualizer = WaveformVisualizer(self)
        return self._waveform_visualizer
    
    @property
    def layered_visualizer(self):
        """延迟加载分层可视化器"""
        if self._layered_visualizer is None:
            from .layered import LayeredVisualizer
            self._layered_visualizer = LayeredVisualizer(self)
        return self._layered_visualizer
    
    @property
    def comparison_visualizer(self):
        """延迟加载对比可视化器"""
        if self._comparison_visualizer is None:
            from .comparison import ComparisonVisualizer
            self._comparison_visualizer = ComparisonVisualizer(self)
        return self._comparison_visualizer
    
    # === 委托方法 ===
    
    def visualize_results(self, input_wave_path: str, output_wave_path: str, 
                         max_samples: int = 5):
        """委托给波形可视化器"""
        return self.waveform_visualizer.visualize_results(
            input_wave_path, output_wave_path, max_samples
        )
    
    def visualize_layer_results(self, input_wave_path: str, layer_dir: str, 
                               max_samples: int = 2, max_channels: int = 8):
        """委托给分层可视化器"""
        return self.layered_visualizer.visualize_layer_results(
            input_wave_path, layer_dir, max_samples, max_channels
        )
    
    def compare_layer_with_direct_output(self, input_wave_path: str, layer_dir: str, 
                                       direct_output_path: str, max_samples: int = 2):
        """委托给对比可视化器"""
        return self.comparison_visualizer.compare_layer_with_direct_output(
            input_wave_path, layer_dir, direct_output_path, max_samples
        )
    
    def visualize_layer_comparison(self, layer_output, spice_layer_output, 
                                 layer_idx: int, layer_name: str, max_samples: int = 5):
        """委托给对比可视化器"""
        return self.comparison_visualizer.visualize_layer_comparison(
            layer_output, spice_layer_output, layer_idx, layer_name, max_samples
        )