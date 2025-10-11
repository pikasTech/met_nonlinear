"""
层对比可视化辅助模块

提供层级对比可视化的辅助功能
"""

import logging
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Optional

from .utils import (
    calculate_error_statistics,
    calculate_channel_error,
    add_text_box
)

logger = logging.getLogger(__name__)


def plot_channel_comparison(ax, channel_idx: int, layer_record, spice_record) -> Optional[List[float]]:
    """
    绘制单个通道的对比
    
    参数:
        ax: matplotlib轴对象
        channel_idx: 通道索引
        layer_record: 层记录
        spice_record: SPICE记录
        
    返回:
        误差列表或None
    """
    layer_channels = layer_record.data.shape[1]
    spice_channels = spice_record.data.shape[1]
    
    layer_exists = channel_idx < layer_channels
    spice_exists = channel_idx < spice_channels
    
    errors = None
    
    # 绘制分层后端数据
    if layer_exists:
        layer_ts = layer_record.to_time_series(channel_idx)
        t_layer = np.arange(len(layer_ts.samples)) / layer_ts.fs
        ax.plot(t_layer, layer_ts.samples, 'b-', label='分层后端')
    
    # 绘制SPICE后端数据
    if spice_exists:
        spice_ts = spice_record.to_time_series(channel_idx)
        t_spice = np.arange(len(spice_ts.samples)) / spice_ts.fs
        ax.plot(t_spice, spice_ts.samples, 'r--', label='SPICE后端')
    
    # 计算误差
    if layer_exists and spice_exists:
        errors = calculate_channel_error(layer_ts.samples, spice_ts.samples)
        if errors is not None:
            add_channel_error_stats(ax, errors, channel_idx)
    
    ax.set_title(f'通道 {channel_idx + 1}')
    ax.set_xlabel('时间 (秒)')
    ax.set_ylabel('幅值')
    ax.grid(True)
    ax.legend(loc='lower right', fontsize=8)
    
    return errors


def add_channel_error_stats(ax, error: np.ndarray, channel_idx: int):
    """
    添加通道误差统计
    
    参数:
        ax: matplotlib轴对象
        error: 误差数组
        channel_idx: 通道索引
    """
    stats = calculate_error_statistics(error)
    # 简化显示格式
    stats_text = (
        f'通道 {channel_idx + 1} 误差:\n'
        f'均值: {stats["mean_error"]:.3f}\n'
        f'标准差: {stats["std_error"]:.3f}\n'
        f'最大绝对值: {stats["max_error"]:.3f}'
    )
    add_text_box(ax, stats_text, y=0.98, fontsize=8, alpha=0.7)


def create_layer_comparison_figure(layer_idx: int, layer_name: str, 
                                 record_idx: int, num_channels: int,
                                 num_rows: int, num_cols: int) -> plt.Figure:
    """
    创建层对比图形
    
    参数:
        layer_idx: 层索引
        layer_name: 层名称
        record_idx: 记录索引
        num_channels: 通道数
        num_rows: 行数
        num_cols: 列数
        
    返回:
        matplotlib图形对象
    """
    fig = plt.figure(figsize=(num_cols * 4, num_rows * 3))
    fig.suptitle(
        f'分层后端 vs SPICE后端 - 第 {layer_idx + 1} 层: {layer_name} - 记录 {record_idx + 1}',
        fontsize=16
    )
    return fig


def log_layer_statistics(layer_idx: int, layer_name: str, layer_stats: dict):
    """
    记录层统计信息
    
    参数:
        layer_idx: 层索引
        layer_name: 层名称
        layer_stats: 统计字典
    """
    logger.info(f'第 {layer_idx + 1} 层 ({layer_name}) 误差统计:')
    logger.info(f"  平均误差: {layer_stats['mean_error']:.6f}")
    logger.info(f"  误差标准差: {layer_stats['std_error']:.6f}")
    logger.info(f"  最大误差: {layer_stats['max_error']:.6f}")
    logger.info(f"  RMS误差: {layer_stats['rms_error']:.6f}")