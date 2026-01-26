"""
可视化工具模块

提供可视化相关的通用工具函数
"""

import numpy as np
from typing import Optional, List, Tuple


def calculate_error_statistics(error: np.ndarray) -> dict:
    """
    计算误差统计信息
    
    参数:
        error: 误差数组
        
    返回:
        dict: 包含mean_error, std_error, max_error, rms_error的字典
    """
    return {
        'mean_error': np.mean(error),
        'std_error': np.std(error),
        'max_error': np.max(np.abs(error)),
        'rms_error': np.sqrt(np.mean(np.square(error)))
    }


def format_error_stats_text(stats: dict, prefix: str = "") -> str:
    """
    格式化误差统计文本
    
    参数:
        stats: 误差统计字典
        prefix: 文本前缀
        
    返回:
        str: 格式化的文本
    """
    if prefix:
        prefix = f"{prefix}\n"
    
    return (
        f'{prefix}'
        f'均值: {stats.get("mean_error", 0):.6f}\n'
        f'标准差: {stats.get("std_error", 0):.6f}\n'
        f'最大绝对值: {stats.get("max_error", 0):.6f}\n'
        f'RMS: {stats.get("rms_error", 0):.6f}'
    )


def calculate_channel_error(layer_samples: np.ndarray, 
                          comparison_samples: np.ndarray) -> Optional[np.ndarray]:
    """
    计算通道误差
    
    参数:
        layer_samples: 层输出样本
        comparison_samples: 对比样本
        
    返回:
        np.ndarray: 误差数组，如果无法计算则返回None
    """
    if len(layer_samples) == 0 or len(comparison_samples) == 0:
        return None
    
    if len(layer_samples) == len(comparison_samples):
        return layer_samples - comparison_samples
    else:
        min_len = min(len(layer_samples), len(comparison_samples))
        return layer_samples[:min_len] - comparison_samples[:min_len]


def find_matching_record(records: List, target_id: str, 
                        idx: int, layer_idx: Optional[int] = None):
    """
    查找匹配的记录
    
    参数:
        records: 记录列表
        target_id: 目标记录ID
        idx: 记录索引
        layer_idx: 层索引（可选）
        
    返回:
        匹配的记录或None
    """
    # 构建可能的ID列表
    possible_ids = [target_id, str(idx)]
    if layer_idx is not None:
        possible_ids.append(f'{target_id}_layer{layer_idx}')
    
    # 按ID查找
    for record in records:
        if record.record_id in possible_ids:
            return record
        
        # 检查original_id属性
        if hasattr(record, 'original_id') and record.original_id in possible_ids:
            return record
    
    # 按索引查找
    if idx < len(records):
        return records[idx]
    
    return None


def calculate_subplot_layout(num_plots: int) -> Tuple[int, int]:
    """
    计算子图布局
    
    参数:
        num_plots: 需要的子图数量
        
    返回:
        Tuple[int, int]: (行数, 列数)
    """
    n_rows = int(np.ceil(np.sqrt(num_plots)))
    n_cols = int(np.ceil(num_plots / n_rows))
    return n_rows, n_cols


def create_figure_with_error_subplot(title: str, record_idx: int, 
                                   figsize: Tuple[int, int] = (12, 8)):
    """
    创建带有误差子图的图形
    
    参数:
        title: 图形标题
        record_idx: 记录索引
        figsize: 图形大小
        
    返回:
        fig, ax_main, ax_error: 图形和两个子图
    """
    import matplotlib.pyplot as plt
    
    fig = plt.figure(figsize=figsize)
    ax_main = plt.subplot2grid((4, 1), (0, 0), rowspan=3)
    ax_error = plt.subplot2grid((4, 1), (3, 0), rowspan=1)
    
    ax_main.set_title(f'{title} - 记录 {record_idx + 1}')
    ax_main.set_xlabel('时间 (秒)')
    ax_main.set_ylabel('幅值')
    ax_main.grid(True)
    
    ax_error.set_title('误差')
    ax_error.set_xlabel('时间 (秒)')
    ax_error.set_ylabel('幅值差')
    ax_error.grid(True)
    
    return fig, ax_main, ax_error


def add_text_box(ax, text: str, x: float = 0.02, y: float = 0.95,
                ha: str = 'left', va: str = 'top', fontsize: int = None,
                alpha: float = 0.8):
    """
    在图形上添加文本框
    
    参数:
        ax: matplotlib轴对象
        text: 要显示的文本
        x, y: 文本位置（相对坐标）
        ha, va: 水平和垂直对齐方式
        fontsize: 字体大小
        alpha: 透明度
    """
    kwargs = {
        'transform': ax.transAxes,
        'verticalalignment': va,
        'horizontalalignment': ha,
        'bbox': dict(boxstyle='round', facecolor='white', alpha=alpha)
    }
    if fontsize:
        kwargs['fontsize'] = fontsize
    
    ax.text(x, y, text, **kwargs)