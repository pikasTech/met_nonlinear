"""
对比可视化模块

负责各种推理结果的对比可视化
"""

import logging
import numpy as np
import matplotlib.pyplot as plt
from typing import TYPE_CHECKING, Dict

from .utils import (
    calculate_error_statistics,
    format_error_stats_text,
    calculate_channel_error,
    find_matching_record,
    calculate_subplot_layout,
    create_figure_with_error_subplot,
    add_text_box
)
from .layer_comparison import (
    plot_channel_comparison,
    create_layer_comparison_figure,
    log_layer_statistics
)

if TYPE_CHECKING:
    from .base import InferenceVisualizer
    from calibration_analyzer.wavedata import WaveData

logger = logging.getLogger(__name__)


class ComparisonVisualizer:
    """对比可视化器"""
    
    def __init__(self, parent: 'InferenceVisualizer'):
        """
        初始化对比可视化器
        
        参数:
            parent: 父级InferenceVisualizer实例
        """
        self.parent = parent
        self.processor = parent.processor
        self.wave_processor = parent.wave_processor
    
    def compare_layer_with_direct_output(self, input_wave_path: str, layer_dir: str, 
                                       direct_output_path: str, max_samples: int = 2):
        """
        将最后一层的输出与直接推理的结果进行对比
        
        参数:
            input_wave_path: 输入波形文件路径
            layer_dir: 分层输出目录路径
            direct_output_path: 直接推理的输出波形文件路径
            max_samples: 最多显示的记录数
        """
        # 获取层文件路径
        layer_paths = self.processor.get_layer_paths(layer_dir)
        if not layer_paths:
            logger.info(f'警告: 在目录 {layer_dir} 中找不到分层输出文件')
            return
        
        # 加载数据
        input_wave_data = self.processor.load_input_wave(input_wave_path)
        direct_output = self.processor.load_input_wave(direct_output_path)
        layer_outputs = [self.processor.load_input_wave(path) for path in layer_paths]
        
        if not layer_outputs:
            logger.error('错误: 没有分层推理结果可供比较')
            return
        
        last_layer_output = layer_outputs[-1]
        
        # 确定要显示的样本数
        num_samples = min(max_samples, len(input_wave_data.records), len(direct_output.records))
        indices = np.random.choice(len(input_wave_data.records), num_samples, replace=False)
        
        # 绘制每个样本的对比
        for i, idx in enumerate(indices):
            self._plot_comparison(
                idx, input_wave_data, last_layer_output, direct_output,
                len(layer_outputs)
            )
    
    def _plot_comparison(self, idx: int, input_wave_data, last_layer_output, 
                        direct_output, num_layers: int):
        """绘制单个样本的对比"""
        # 获取记录
        input_record = input_wave_data.records[idx]
        direct_output_record = direct_output.records[idx]
        
        # 查找最后一层的记录
        last_layer_record = self._find_last_layer_record(
            last_layer_output, input_record, idx, num_layers
        )
        
        if last_layer_record is None:
            logger.info(f'警告: 无法找到最后一层的记录 {idx}')
            return
        
        # 获取时间序列数据
        input_ts = input_record.to_time_series(0)
        last_layer_ts = last_layer_record.to_time_series(0)
        direct_output_ts = direct_output_record.to_time_series(0)
        
        # 计算时间轴
        t_input = np.arange(len(input_ts.samples)) / input_ts.fs
        t_last_layer = np.arange(len(last_layer_ts.samples)) / last_layer_ts.fs
        t_direct = np.arange(len(direct_output_ts.samples)) / direct_output_ts.fs
        
        # 计算误差
        error, t_error = self._calculate_error(
            last_layer_ts.samples, direct_output_ts.samples,
            last_layer_ts.fs, idx
        )
        
        # 获取层信息
        layer_info = last_layer_output.user_metadata.get('layer_info', {})
        layer_name = layer_info.get('name', f'Layer {num_layers}')
        
        # 创建图形
        self._create_comparison_plot(
            idx, t_input, input_ts.samples,
            t_last_layer, last_layer_ts.samples,
            t_direct, direct_output_ts.samples,
            t_error, error, layer_name
        )
    
    def _find_last_layer_record(self, last_layer_output, input_record, idx: int, num_layers: int):
        """查找最后一层的记录"""
        return find_matching_record(
            last_layer_output.records, 
            input_record.record_id,
            idx,
            num_layers
        )
    
    def _calculate_error(self, layer_samples, direct_samples, fs: float, idx: int):
        """计算误差"""
        if len(layer_samples) == len(direct_samples):
            error = layer_samples - direct_samples
            t_error = np.arange(len(error)) / fs
        else:
            min_len = min(len(layer_samples), len(direct_samples))
            error = layer_samples[:min_len] - direct_samples[:min_len]
            t_error = np.arange(min_len) / fs
            logger.info(
                f'警告: 记录 {idx} 的最后一层输出和直接输出长度不同，'
                f'已裁剪到相同长度进行比较'
            )
        
        return error, t_error
    
    def _create_comparison_plot(self, idx: int, t_input, input_samples,
                               t_last_layer, last_layer_samples,
                               t_direct, direct_samples,
                               t_error, error, layer_name: str):
        """创建对比图形"""
        fig, ax_main, ax_error = create_figure_with_error_subplot(
            f'最后一层输出 vs 直接输出', idx
        )
        
        # 主图：波形对比
        ax_main.plot(t_input, input_samples, 'k-', label='输入', alpha=0.5)
        ax_main.plot(t_last_layer, last_layer_samples, 'b-', label=f'最后一层: {layer_name}')
        ax_main.plot(t_direct, direct_samples, 'r--', label='直接输出')
        ax_main.legend()
        
        # 误差图
        ax_error.plot(t_error, error, 'g-')
        ax_error.set_title('误差 (最后一层输出 - 直接输出)')
        
        # 添加误差统计
        self._add_error_statistics(ax_error, error)
        
        plt.tight_layout()
        plt.show()
    
    def _add_error_statistics(self, ax, error):
        """添加误差统计信息"""
        stats = calculate_error_statistics(error)
        stats_text = format_error_stats_text(stats, '误差统计:')
        add_text_box(ax, stats_text)
    
    def visualize_layer_comparison(self, layer_output: 'WaveData', 
                                 spice_layer_output: 'WaveData',
                                 layer_idx: int, layer_name: str, 
                                 max_samples: int = 5) -> Dict[str, float]:
        """
        可视化对比分层后端和SPICE后端的层输出结果
        
        参数:
            layer_output: 分层后端该层的输出
            spice_layer_output: SPICE后端该层的输出
            layer_idx: 层索引
            layer_name: 层名称
            max_samples: 最多显示的记录数
            
        返回:
            Dict[str, float]: 误差统计信息
        """
        num_samples = min(max_samples, len(layer_output.records), 
                         len(spice_layer_output.records))
        indices = np.random.choice(len(layer_output.records), num_samples, replace=False)
        
        all_errors = []
        layer_stats = {'mean_error': 0, 'std_error': 0, 'max_error': 0, 'rms_error': 0}
        
        # 绘制每个样本
        for i, idx in enumerate(indices):
            channel_errors = self._plot_layer_comparison_sample(
                idx, layer_output, spice_layer_output, layer_idx, layer_name
            )
            if channel_errors:
                all_errors.extend(channel_errors)
        
        # 计算总体统计
        if all_errors:
            all_errors = np.array(all_errors)
            layer_stats = calculate_error_statistics(all_errors)
            
            log_layer_statistics(layer_idx, layer_name, layer_stats)
        
        return layer_stats
    
    def _plot_layer_comparison_sample(self, idx: int, layer_output, spice_layer_output,
                                    layer_idx: int, layer_name: str):
        """绘制单个样本的层对比"""
        # 获取记录
        layer_record = layer_output.records[idx]
        spice_record = self._find_spice_record(spice_layer_output, layer_record, idx)
        
        if spice_record is None:
            logger.info(f'警告: 无法找到SPICE后端第 {layer_idx + 1} 层的记录 {idx}')
            return []
        
        # 准备绘图
        num_channels = max(layer_record.data.shape[1], spice_record.data.shape[1])
        num_rows, num_cols = calculate_subplot_layout(num_channels)
        
        fig = create_layer_comparison_figure(
            layer_idx, layer_name, idx, num_channels, num_rows, num_cols
        )
        
        # 绘制每个通道并收集误差
        channel_errors = []
        for channel_idx in range(num_channels):
            ax = plt.subplot(num_rows, num_cols, channel_idx + 1)
            errors = plot_channel_comparison(
                ax, channel_idx, layer_record, spice_record
            )
            if errors is not None:
                channel_errors.extend(errors)
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.92)
        plt.show()
        
        return channel_errors
    
    def _find_spice_record(self, spice_layer_output, layer_record, idx: int):
        """查找对应的SPICE记录"""
        return find_matching_record(
            spice_layer_output.records,
            layer_record.record_id,
            idx
        )
    
