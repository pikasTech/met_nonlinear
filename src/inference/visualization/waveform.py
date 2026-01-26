"""
波形可视化模块

负责基本的输入输出波形可视化
"""

import logging
import numpy as np
import matplotlib.pyplot as plt
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import InferenceVisualizer

logger = logging.getLogger(__name__)


class WaveformVisualizer:
    """波形可视化器"""
    
    def __init__(self, parent: 'InferenceVisualizer'):
        """
        初始化波形可视化器
        
        参数:
            parent: 父级InferenceVisualizer实例
        """
        self.parent = parent
        self.processor = parent.processor
        self.wave_processor = parent.wave_processor
    
    def visualize_results(self, input_wave_path: str, output_wave_path: str, 
                         max_samples: int = 5):
        """
        可视化部分推理结果
        
        参数:
            input_wave_path: 输入波形文件路径
            output_wave_path: 输出波形文件路径
            max_samples: 最多显示的记录数
        """
        # 加载波形数据
        input_wave_data = self.processor.load_input_wave(input_wave_path)
        output_wave_data = self.processor.load_input_wave(output_wave_path)
        
        # 确定要显示的样本数
        num_samples = min(max_samples, len(input_wave_data.records))
        
        # 创建子图
        fig, axes = plt.subplots(num_samples, 1, figsize=(10, 3 * num_samples))
        if num_samples == 1:
            axes = [axes]
        
        # 随机选择记录索引
        indices = np.random.choice(len(input_wave_data.records), num_samples, replace=False)
        
        # 绘制每个样本
        for i, idx in enumerate(indices):
            self._plot_single_sample(
                axes[i], idx,
                input_wave_data.records[idx],
                output_wave_data.records[idx]
            )
        
        plt.tight_layout()
        plt.show()
    
    def _plot_single_sample(self, ax, idx: int, input_record, output_record):
        """绘制单个样本的输入输出对比"""
        # 获取时间序列数据
        input_ts = input_record.to_time_series(0)
        output_ts = output_record.to_time_series(0)
        
        # 获取频率信息
        freq = input_record.user_metadata.get('frequency', '未知')
        
        # 计算时间轴
        t_input = np.arange(len(input_ts.samples)) / input_ts.fs
        t_output = np.arange(len(output_ts.samples)) / output_ts.fs
        
        # 绘制波形
        ax.plot(t_input, input_ts.samples, 'b-', label='输入', alpha=0.7)
        ax.plot(t_output, output_ts.samples, 'r-', label='输出')
        
        # 设置标签和标题
        ax.set_title(f'记录 {idx + 1}, 频率: {freq} Hz')
        ax.set_xlabel('时间 (秒)')
        ax.set_ylabel('幅值')
        ax.grid(True)
        ax.legend()