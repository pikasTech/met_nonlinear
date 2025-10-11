"""
分层可视化模块

负责分层推理结果的可视化
"""

import logging
import numpy as np
import matplotlib.pyplot as plt
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .base import InferenceVisualizer

logger = logging.getLogger(__name__)


class LayeredVisualizer:
    """分层可视化器"""
    
    def __init__(self, parent: 'InferenceVisualizer'):
        """
        初始化分层可视化器
        
        参数:
            parent: 父级InferenceVisualizer实例
        """
        self.parent = parent
        self.processor = parent.processor
        self.wave_processor = parent.wave_processor
    
    def visualize_layer_results(self, input_wave_path: str, layer_dir: str, 
                               max_samples: int = 2, max_channels: int = 8):
        """
        可视化分层推理结果
        
        参数:
            input_wave_path: 输入波形文件路径
            layer_dir: 分层输出目录路径
            max_samples: 最多显示的记录数
            max_channels: 每层最多显示的通道数
        """
        # 获取层文件路径
        layer_paths = self.processor.get_layer_paths(layer_dir)
        if not layer_paths:
            logger.info(f'警告: 在目录 {layer_dir} 中找不到分层输出文件')
            return
        
        # 加载数据
        input_wave_data = self.processor.load_input_wave(input_wave_path)
        layer_outputs = [self.processor.load_input_wave(path) for path in layer_paths]
        
        # 确定要显示的样本数
        num_samples = min(max_samples, len(input_wave_data.records))
        num_layers = len(layer_outputs)
        
        # 随机选择记录索引
        indices = np.random.choice(len(input_wave_data.records), num_samples, replace=False)
        
        # 计算子图布局
        n_rows = int(np.ceil(np.sqrt(num_layers + 1)))
        n_cols = int(np.ceil((num_layers + 1) / n_rows))
        
        # 为每个样本创建图形
        for sample_idx, record_idx in enumerate(indices):
            self._plot_single_sample_layers(
                record_idx, input_wave_data, layer_outputs,
                n_rows, n_cols, max_channels
            )
    
    def _plot_single_sample_layers(self, record_idx: int, input_wave_data,
                                  layer_outputs: List, n_rows: int, n_cols: int,
                                  max_channels: int):
        """绘制单个样本的分层结果"""
        # 创建图形
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(4 * n_cols, 4 * n_rows), sharex=True)
        fig.suptitle(f'分层推理结果 - 记录 {record_idx + 1}', fontsize=16)
        
        # 处理axes数组维度
        if n_rows == 1 and n_cols == 1:
            axes = np.array([[axes]])
        elif n_rows == 1:
            axes = axes.reshape(1, -1)
        elif n_cols == 1:
            axes = axes.reshape(-1, 1)
        
        axes_flat = axes.flatten()
        
        # 绘制输入信号
        input_record = input_wave_data.records[record_idx]
        self._plot_input_signal(axes_flat[0], input_record)
        
        # 绘制每层的输出
        for layer_idx, layer_output in enumerate(layer_outputs):
            if layer_idx + 1 >= len(axes_flat):
                logger.info(f'警告: 没有足够的子图来显示层 {layer_idx + 1}')
                break
            
            self._plot_layer_output(
                axes_flat[layer_idx + 1], layer_idx, layer_output,
                input_record, record_idx, max_channels
            )
        
        # 隐藏多余的子图
        for i in range(len(layer_outputs) + 1, len(axes_flat)):
            axes_flat[i].axis('off')
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.9)
        plt.show()
    
    def _plot_input_signal(self, ax, input_record):
        """绘制输入信号"""
        input_ts = input_record.to_time_series(0)
        t_input = np.arange(len(input_ts.samples)) / input_ts.fs
        
        ax.plot(t_input, input_ts.samples, 'k-', label='输入')
        ax.set_title('输入信号')
        ax.grid(True)
        ax.legend()
    
    def _plot_layer_output(self, ax, layer_idx: int, layer_output,
                          input_record, record_idx: int, max_channels: int):
        """绘制单层的输出"""
        # 获取层信息
        layer_info = layer_output.user_metadata.get('layer_info', {})
        layer_name = layer_info.get('name', f'Layer {layer_idx + 1}')
        
        # 查找对应的层记录
        layer_record = self._find_layer_record(
            layer_output, input_record, record_idx, layer_idx
        )
        
        if layer_record is None:
            ax.text(0.5, 0.5, f'无法找到层 {layer_name} 的记录 {record_idx}',
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes)
            return
        
        # 绘制各通道
        num_channels = layer_record.data.shape[1]
        channels_to_plot = min(num_channels, max_channels)
        
        for channel_idx in range(channels_to_plot):
            channel_ts = layer_record.to_time_series(channel_idx)
            t_channel = np.arange(len(channel_ts.samples)) / channel_ts.fs
            color = plt.cm.tab10(channel_idx % 10)
            ax.plot(t_channel, channel_ts.samples, color=color, 
                   label=f'通道 {channel_idx + 1}')
        
        # 显示额外通道信息
        if num_channels > max_channels:
            ax.text(0.98, 0.02, f'+{num_channels - max_channels} 个通道未显示',
                   horizontalalignment='right', verticalalignment='bottom',
                   transform=ax.transAxes, bbox=dict(facecolor='white', alpha=0.7))
        
        ax.set_title(f'层 {layer_idx + 1}: {layer_name}')
        ax.grid(True)
        ax.legend()
    
    def _find_layer_record(self, layer_output, input_record, record_idx: int, layer_idx: int):
        """查找对应的层记录"""
        layer_record_id = f'{input_record.record_id}_layer{layer_idx + 1}'
        
        # 尝试按ID查找
        for record in layer_output.records:
            if record.record_id == layer_record_id or record.record_id == str(record_idx):
                return record
        
        # 按索引查找
        if record_idx < len(layer_output.records):
            return layer_output.records[record_idx]
        
        return None