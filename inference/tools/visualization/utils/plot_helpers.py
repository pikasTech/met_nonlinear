#!/usr/bin/env python3
"""
绘图辅助工具模块

提供学术风格的绘图函数和原始数据保存功能。
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl


def format_chart_number(value: float) -> str:
    """格式化图表中的数值显示"""
    if abs(value) < 1e-4:
        return "<0.0001"
    elif abs(value) < 0.001:
        return f"{value:.4f}"
    else:
        return f"{value:.4f}"


# 设置学术风格
def setup_academic_style(config: Dict[str, Any] = None):
    """
    设置学术论文风格的绘图参数
    
    Args:
        config: 配置字典（可选）
    """
    
    # 设置字体 - 优先使用支持中文的字体
    import platform
    system = platform.system()
    
    # 设置中文字体
    if system == "Windows":
        chinese_fonts = ['SimHei', 'Microsoft YaHei', 'KaiTi', 'SimSun']
        english_fonts = ['Times New Roman', 'Arial']
    elif system == "Darwin":  # macOS
        chinese_fonts = ['PingFang SC', 'STHeiti', 'Hiragino Sans GB']
        english_fonts = ['Times New Roman', 'Arial']
    else:  # Linux
        chinese_fonts = ['WenQuanYi Micro Hei', 'DejaVu Sans', 'Noto Sans CJK SC']
        english_fonts = ['Liberation Serif', 'DejaVu Serif']
    
    # 尝试设置中文字体
    available_fonts = []
    from matplotlib.font_manager import FontManager
    fm = FontManager()
    font_names = [f.name for f in fm.ttflist]
    
    for font in chinese_fonts:
        if font in font_names:
            available_fonts.append(font)
            break
    
    for font in english_fonts:
        if font in font_names:
            available_fonts.append(font)
            break
    
    if available_fonts:
        mpl.rcParams['font.sans-serif'] = available_fonts
        mpl.rcParams['font.family'] = ['sans-serif']
    else:
        # 备用设置
        mpl.rcParams['font.family'] = ['DejaVu Sans']
    
    # 解决负号显示问题
    mpl.rcParams['axes.unicode_minus'] = False
    mpl.rcParams['font.size'] = 12
    
    # 设置线宽和标记大小
    mpl.rcParams['lines.linewidth'] = 1.5
    mpl.rcParams['lines.markersize'] = 6
    
    # 设置坐标轴
    mpl.rcParams['axes.linewidth'] = 1.0
    mpl.rcParams['axes.labelsize'] = 12
    mpl.rcParams['axes.titlesize'] = 14
    mpl.rcParams['axes.grid'] = True
    mpl.rcParams['grid.alpha'] = 0.3
    mpl.rcParams['grid.linestyle'] = '--'
    
    # 设置刻度
    mpl.rcParams['xtick.labelsize'] = 10
    mpl.rcParams['ytick.labelsize'] = 10
    mpl.rcParams['xtick.direction'] = 'in'
    mpl.rcParams['ytick.direction'] = 'in'
    
    # 设置图例
    mpl.rcParams['legend.fontsize'] = 10
    mpl.rcParams['legend.frameon'] = True
    mpl.rcParams['legend.fancybox'] = False
    
    # 设置图形质量
    mpl.rcParams['figure.dpi'] = 100
    mpl.rcParams['savefig.dpi'] = 300
    
    # 如果提供了配置，应用自定义设置
    if config and 'figure' in config:
        fig_config = config['figure']
        if 'font_size' in fig_config:
            mpl.rcParams['font.size'] = fig_config['font_size']
        if 'dpi' in fig_config:
            mpl.rcParams['savefig.dpi'] = fig_config['dpi']


def save_plot_data(data: Dict[str, Any], output_path: str, plot_name: str, 
                   format: str = 'json'):
    """
    保存绘图的原始数据
    
    Args:
        data: 要保存的数据字典
        output_path: 输出基础路径
        plot_name: 图表名称（不含扩展名）
        format: 数据格式（'json' 或 'csv'）
    """
    # 构建raw数据目录路径
    raw_dir = Path(output_path).parent / 'raw' / Path(output_path).name
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    # 添加时间戳和元数据
    save_data = {
        'timestamp': datetime.now().isoformat(),
        'plot_name': plot_name,
        **data
    }
    
    # 保存数据
    if format == 'json':
        output_file = raw_dir / f"{plot_name}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False, default=str)
    else:
        # CSV格式（仅保存主数据部分）
        import csv
        output_file = raw_dir / f"{plot_name}.csv"
        # 需要根据具体数据结构实现CSV保存逻辑
        pass
        
    return output_file


def plot_layer_bias_comparison_simple(baseline_data: Dict[str, Any], 
                                     compensated_data: Dict[str, Any],
                                     layer_idx: int,
                                     output_path: str,
                                     config: Dict[str, Any] = None) -> str:
    """
    绘制单层的偏置误差对比条形图（不包含RMS）
    
    Args:
        baseline_data: 基准数据
        compensated_data: 补偿后数据
        layer_idx: 层索引
        output_path: 输出路径
        config: 配置字典
        
    Returns:
        保存的图片路径
    """
    # 设置风格
    setup_academic_style(config)
    
    # 获取数据
    baseline_layer = baseline_data['layers'][layer_idx]
    compensated_layer = compensated_data['layers'][layer_idx]
    
    # 提取通道偏置误差
    baseline_errors = [ch['bias_error'] for ch in baseline_layer['bias_errors']]
    compensated_errors = [ch['bias_error'] for ch in compensated_layer['bias_errors']]
    channel_count = len(baseline_errors)
    
    # 计算改进百分比
    baseline_mean = baseline_layer['summary']['mean_bias_error']
    compensated_mean = compensated_layer['summary']['mean_bias_error']
    improvement = (baseline_mean - compensated_mean) / abs(baseline_mean) * 100 if baseline_mean != 0 else 0
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 设置条形图参数
    x = np.arange(channel_count)
    width = 0.35
    
    # 绘制条形图
    colors = config.get('colors', {}) if config else {}
    baseline_color = colors.get('baseline', '#E74C3C')
    compensated_color = colors.get('compensated', '#27AE60')
    
    bars1 = ax.bar(x - width/2, np.abs(baseline_errors), width, 
                    label='基准', color=baseline_color, edgecolor='darkred', linewidth=0.5, alpha=0.8)
    bars2 = ax.bar(x + width/2, np.abs(compensated_errors), width,
                    label='补偿后', color=compensated_color, edgecolor='darkgreen', linewidth=0.5, alpha=0.8)
    
    # 添加数值标注
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.annotate(format_chart_number(height),
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=8, rotation=45)
    
    # 设置标签和标题
    ax.set_xlabel('通道')
    ax.set_ylabel('偏置误差绝对值')
    ax.set_title(f'第{layer_idx}层偏置误差对比 (改进: {improvement:.1f}%)')
    ax.set_xticks(x)
    ax.set_xticklabels([f'Ch{i}' for i in range(channel_count)])
    
    # 添加均值线
    ax.axhline(y=abs(baseline_mean), color=baseline_color, linestyle='--', 
               alpha=0.7, label=f'基准均值: {format_chart_number(abs(baseline_mean))}')
    ax.axhline(y=abs(compensated_mean), color=compensated_color, linestyle='--', 
               alpha=0.7, label=f'补偿后均值: {format_chart_number(abs(compensated_mean))}')
    
    # 设置图例
    ax.legend(loc='best', framealpha=0.9)
    ax.grid(True, alpha=0.3, axis='y')
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_name = f"layer_{layer_idx}_bias_comparison_simple"
    fig_path = output_dir / f"{plot_name}.png"
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    # 保存原始数据
    plot_data = {
        'plot_type': 'layer_bias_comparison',
        'data': {
            'channels': list(range(channel_count)),
            'baseline_errors': baseline_errors,
            'compensated_errors': compensated_errors,
            'baseline_mean': baseline_mean,
            'compensated_mean': compensated_mean,
            'improvement_percent': improvement
        },
        'metadata': {
            'layer': layer_idx,
            'layer_name': baseline_layer['name'],
            'channel_count': channel_count,
            'units': 'bias_error'
        }
    }
    save_plot_data(plot_data, str(output_dir), plot_name)
    
    return str(fig_path)


def plot_layer_bias_comparison(baseline_data: Dict[str, Any], 
                               compensated_data: Dict[str, Any],
                               layer_idx: int,
                               output_path: str,
                               config: Dict[str, Any] = None) -> str:
    """
    绘制单层的偏置误差对比条形图（包含RMS误差在Ch6位置）
    
    Args:
        baseline_data: 基准数据
        compensated_data: 补偿后数据
        layer_idx: 层索引
        output_path: 输出路径
        config: 配置字典
        
    Returns:
        保存的图片路径
    """
    # 设置风格
    setup_academic_style(config)
    
    # 获取数据
    baseline_layer = baseline_data['layers'][layer_idx]
    compensated_layer = compensated_data['layers'][layer_idx]
    
    # 提取通道偏置误差
    baseline_errors = [ch['bias_error'] for ch in baseline_layer['bias_errors']]
    compensated_errors = [ch['bias_error'] for ch in compensated_layer['bias_errors']]
    channel_count = len(baseline_errors)
    
    # 获取RMS误差
    baseline_rms = baseline_data['analysis']['layer_analysis'][layer_idx-1]['rms_error']
    compensated_rms = compensated_data['analysis']['layer_analysis'][layer_idx-1]['rms_error']
    
    # 扩展数据数组，将RMS误差添加到Ch6位置
    extended_baseline = baseline_errors + [baseline_rms]
    extended_compensated = compensated_errors + [compensated_rms]
    extended_count = len(extended_baseline)
    
    # 计算改进百分比
    baseline_mean = baseline_layer['summary']['mean_bias_error']
    compensated_mean = compensated_layer['summary']['mean_bias_error']
    bias_improvement = (baseline_mean - compensated_mean) / abs(baseline_mean) * 100 if baseline_mean != 0 else 0
    rms_improvement = (baseline_rms - compensated_rms) / baseline_rms * 100 if baseline_rms != 0 else 0
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 设置条形图参数
    x = np.arange(extended_count)
    width = 0.35
    
    # 绘制条形图
    colors = config.get('colors', {}) if config else {}
    baseline_color = colors.get('baseline', '#E74C3C')
    compensated_color = colors.get('compensated', '#27AE60')
    
    bars1 = ax.bar(x - width/2, np.abs(extended_baseline), width, 
                    label='基准', color=baseline_color, edgecolor='darkred', linewidth=0.5, alpha=0.8)
    bars2 = ax.bar(x + width/2, np.abs(extended_compensated), width,
                    label='补偿后', color=compensated_color, edgecolor='darkgreen', linewidth=0.5, alpha=0.8)
    
    # 特殊标识RMS误差条
    rms_idx = channel_count  # RMS在最后一个位置
    bars1[rms_idx].set_hatch('///')  # 添加斜线纹理
    bars2[rms_idx].set_hatch('///')
    
    # 添加数值标注
    for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
        for bar in [bar1, bar2]:
            height = bar.get_height()
            if height > 0:
                ax.annotate(format_chart_number(height),
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=8, rotation=45)
    
    # 设置标签和标题
    ax.set_xlabel('通道/误差类型')
    ax.set_ylabel('误差绝对值')
    ax.set_title(f'第{layer_idx}层偏置误差与RMS误差对比\n(偏置改进: {bias_improvement:.1f}%, RMS改进: {rms_improvement:.1f}%)')
    
    # 设置x轴标签
    x_labels = [f'Ch{i}' for i in range(channel_count)] + ['RMS']
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels)
    
    # 添加分隔线，区分偏置误差和RMS误差
    ax.axvline(x=channel_count-0.5, color='gray', linestyle='--', alpha=0.7)
    
    # 添加均值线（仅对偏置误差部分）
    ax.axhline(y=abs(baseline_mean), color=baseline_color, linestyle='--', 
               alpha=0.7, label=f'偏置基准均值: {abs(baseline_mean):.4f}')
    ax.axhline(y=abs(compensated_mean), color=compensated_color, linestyle='--', 
               alpha=0.7, label=f'偏置补偿后均值: {abs(compensated_mean):.4f}')
    
    # 设置图例
    ax.legend(loc='best', framealpha=0.9)
    
    # 设置对数坐标轴以更好地显示不同量级的数据
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3, axis='y')
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_name = f"layer_{layer_idx}_bias_rms_comparison"
    fig_path = output_dir / f"{plot_name}.png"
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    # 保存原始数据
    plot_data = {
        'plot_type': 'layer_bias_rms_comparison',
        'data': {
            'channels': list(range(channel_count)),
            'baseline_bias_errors': baseline_errors,
            'compensated_bias_errors': compensated_errors,
            'baseline_rms_error': baseline_rms,
            'compensated_rms_error': compensated_rms,
            'baseline_mean': baseline_mean,
            'compensated_mean': compensated_mean,
            'bias_improvement_percent': bias_improvement,
            'rms_improvement_percent': rms_improvement
        },
        'metadata': {
            'layer': layer_idx,
            'layer_name': baseline_layer['name'],
            'channel_count': channel_count,
            'units': 'mixed_bias_rms_errors'
        }
    }
    save_plot_data(plot_data, str(output_dir), plot_name)
    
    return str(fig_path)


def plot_global_improvement_bar(improvements: Dict[str, float],
                                output_path: str,
                                config: Dict[str, Any] = None) -> str:
    """
    绘制全局改进条形图
    
    Args:
        improvements: 改进百分比字典
        output_path: 输出路径
        config: 配置字典
        
    Returns:
        保存的图片路径
    """
    setup_academic_style(config)
    
    # 准备数据
    metrics = ['平均值', '标准差', '最大值']
    values = [improvements['mean'], improvements['std'], improvements['max']]
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # 绘制条形图  
    colors = config.get('colors', {}) if config else {}
    improvement_color = colors.get('improvement', '#3498DB')
    bar_colors = [improvement_color, '#2ECC71', '#E67E22']  # 蓝绿橙渐变
    bars = ax.bar(metrics, values, color=bar_colors, edgecolor='black', linewidth=1, alpha=0.8)
    
    # 添加数值标注
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax.annotate(f'{value:.1f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # 设置标签和标题
    ax.set_ylabel('改进百分比 (%)')
    ax.set_title('偏置补偿整体改进效果')
    ax.set_ylim(0, max(values) * 1.2)
    
    # 添加网格
    ax.grid(True, axis='y', alpha=0.3)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_name = "overview_global_improvement"
    fig_path = output_dir / f"{plot_name}.png"
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    # 保存原始数据
    plot_data = {
        'plot_type': 'global_improvement_bar',
        'data': {
            'metrics': metrics,
            'values': values
        },
        'metadata': {
            'units': 'percent'
        }
    }
    save_plot_data(plot_data, str(output_dir), plot_name)
    
    return str(fig_path)


def plot_bias_error_heatmap(baseline_matrix: List[List[float]],
                            compensated_matrix: List[List[float]],
                            output_path: str,
                            config: Dict[str, Any] = None) -> Tuple[str, str]:
    """
    绘制偏置误差热力图（全局概览）
    
    Args:
        baseline_matrix: 基准误差矩阵
        compensated_matrix: 补偿后误差矩阵
        output_path: 输出路径
        config: 配置字典
        
    Returns:
        (基准热力图路径, 补偿后热力图路径)
    """
    setup_academic_style(config)
    
    # 转换为numpy数组，处理不规则矩阵（只绘制前4个层）
    max_channels = 6
    n_layers = 5  # 只绘制前4个层
    
    def matrix_to_array(matrix):
        arr = np.full((n_layers, max_channels), np.nan)
        for i, row in enumerate(matrix[:n_layers]):  # 只取前4层
            for j, val in enumerate(row):
                if j < max_channels:
                    arr[i, j] = abs(val)
        return arr
    
    baseline_arr = matrix_to_array(baseline_matrix)
    compensated_arr = matrix_to_array(compensated_matrix)
    
    # 统一颜色范围以便全局对比
    all_values = np.concatenate([baseline_arr[~np.isnan(baseline_arr)], 
                                compensated_arr[~np.isnan(compensated_arr)]])
    vmin, vmax = np.min(all_values), np.max(all_values) / 4 
    
    # 创建图形
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # 颜色映射
    cmap = config.get('colors', {}).get('colormap', 'plasma') if config else 'plasma'
    
    # 绘制基准热力图
    im1 = ax1.imshow(baseline_arr, cmap=cmap, aspect='auto', vmin=vmin, vmax=vmax)
    ax1.set_title('基准偏置误差分布', fontsize=14, fontweight='bold')
    ax1.set_xlabel('通道')
    ax1.set_ylabel('层')
    ax1.set_xticks(range(max_channels))
    ax1.set_yticks(range(n_layers))
    ax1.set_yticklabels([f'Layer {i+1}' for i in range(n_layers)])
    
    # 添加数值标注
    for i in range(n_layers):
        for j in range(max_channels):
            if not np.isnan(baseline_arr[i, j]):
                # 根据值的大小选择文字颜色
                text_color = 'white' if baseline_arr[i, j] > (vmax - vmin) * 0.5 + vmin else 'black'
                ax1.text(j, i, f'{baseline_arr[i, j]:.4f}',
                        ha="center", va="center", color=text_color, fontsize=8, fontweight='bold')
    
    # 绘制补偿后热力图
    im2 = ax2.imshow(compensated_arr, cmap=cmap, aspect='auto', vmin=vmin, vmax=vmax)
    ax2.set_title('补偿后偏置误差分布', fontsize=14, fontweight='bold')
    ax2.set_xlabel('通道')
    ax2.set_ylabel('层')
    ax2.set_xticks(range(max_channels))
    ax2.set_yticks(range(n_layers))
    ax2.set_yticklabels([f'Layer {i+1}' for i in range(n_layers)])
    
    # 添加数值标注
    for i in range(n_layers):
        for j in range(max_channels):
            if not np.isnan(compensated_arr[i, j]):
                # 根据值的大小选择文字颜色
                text_color = 'white' if compensated_arr[i, j] > (vmax - vmin) * 0.5 + vmin else 'black'
                ax2.text(j, i, f'{compensated_arr[i, j]:.4f}',
                        ha="center", va="center", color=text_color, fontsize=8, fontweight='bold')
    
    # 添加共享颜色条（左边外部）
    fig.subplots_adjust(left=0.15)
    cbar = fig.colorbar(im1, ax=[ax1, ax2], shrink=0.8, pad=0.08, location='left')
    cbar.set_label('偏置误差绝对值', fontsize=12)
    
    # 调整布局
    # plt.tight_layout()
    
    # 保存图片
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_name = "channel_bias_error_heatmap"
    fig_path = output_dir / f"{plot_name}.png"
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    # 生成分层热力图
    _plot_layer_heatmaps(baseline_matrix, compensated_matrix, output_path, config)
    
    # 保存原始数据
    plot_data = {
        'plot_type': 'bias_error_heatmap',
        'data': {
            'baseline_matrix': baseline_matrix,
            'compensated_matrix': compensated_matrix,
            'baseline_array': baseline_arr.tolist(),
            'compensated_array': compensated_arr.tolist()
        },
        'metadata': {
            'n_layers': n_layers,
            'max_channels': max_channels,
            'units': 'bias_error_absolute'
        }
    }
    save_plot_data(plot_data, str(output_dir), plot_name)
    
    return str(fig_path), str(fig_path)


def _plot_layer_heatmaps(baseline_matrix: List[List[float]],
                        compensated_matrix: List[List[float]],
                        output_path: str,
                        config: Dict[str, Any] = None):
    """
    绘制每层单独的热力图对比（同一层使用相同刻度尺）
    
    Args:
        baseline_matrix: 基准误差矩阵
        compensated_matrix: 补偿后误差矩阵
        output_path: 输出路径
        config: 配置字典
    """
    setup_academic_style(config)
    
    max_channels = 6
    n_layers = min(len(baseline_matrix), len(compensated_matrix))
    
    # 颜色映射
    cmap = config.get('colors', {}).get('colormap', 'plasma') if config else 'plasma'
    
    for layer_idx in range(n_layers):
        # 获取该层数据
        baseline_layer = [abs(val) for val in baseline_matrix[layer_idx][:max_channels]]
        compensated_layer = [abs(val) for val in compensated_matrix[layer_idx][:max_channels]]
        
        # 为该层计算统一的颜色范围
        all_layer_values = baseline_layer + compensated_layer
        if all_layer_values:
            vmin, vmax = min(all_layer_values), max(all_layer_values)
            # 如果范围太小，稍微扩展以便可视化
            if vmax - vmin < 1e-6:
                vmax = vmin + 1e-6
        else:
            vmin, vmax = 0, 1
        
        # 创建该层的对比热力图（上下排布）
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
        
        # 准备数据矩阵（单行）
        baseline_row = np.array(baseline_layer + [np.nan] * (max_channels - len(baseline_layer)))
        compensated_row = np.array(compensated_layer + [np.nan] * (max_channels - len(compensated_layer)))
        
        baseline_heatmap = baseline_row.reshape(1, -1)
        compensated_heatmap = compensated_row.reshape(1, -1)
        
        # 绘制基准热力图
        im1 = ax1.imshow(baseline_heatmap, cmap=cmap, aspect='auto', vmin=vmin, vmax=vmax)
        ax1.set_title(f'第{layer_idx+1}层基准偏置误差', fontsize=12, fontweight='bold')
        ax1.set_xlabel('通道')
        ax1.set_ylabel(f'Layer {layer_idx+1}')
        ax1.set_xticks(range(len(baseline_layer)))
        ax1.set_xticklabels([f'Ch{i}' for i in range(len(baseline_layer))])
        ax1.set_yticks([0])
        ax1.set_yticklabels([f'Layer {layer_idx+1}'])
        
        # 添加数值标注
        for j in range(len(baseline_layer)):
            text_color = 'white' if baseline_layer[j] > (vmax - vmin) * 0.5 + vmin else 'black'
            ax1.text(j, 0, f'{baseline_layer[j]:.4f}',
                    ha="center", va="center", color=text_color, fontsize=10, fontweight='bold')
        
        # 绘制补偿后热力图
        im2 = ax2.imshow(compensated_heatmap, cmap=cmap, aspect='auto', vmin=vmin, vmax=vmax)
        ax2.set_title(f'第{layer_idx+1}层补偿后偏置误差', fontsize=12, fontweight='bold')
        ax2.set_xlabel('通道')
        ax2.set_ylabel(f'Layer {layer_idx+1}')
        ax2.set_xticks(range(len(compensated_layer)))
        ax2.set_xticklabels([f'Ch{i}' for i in range(len(compensated_layer))])
        ax2.set_yticks([0])
        ax2.set_yticklabels([f'Layer {layer_idx+1}'])
        
        # 添加数值标注
        for j in range(len(compensated_layer)):
            text_color = 'white' if compensated_layer[j] > (vmax - vmin) * 0.5 + vmin else 'black'
            ax2.text(j, 0, f'{compensated_layer[j]:.4f}',
                    ha="center", va="center", color=text_color, fontsize=10, fontweight='bold')
        
        # 添加颜色条（左边外部，适配上下布局）
        fig.subplots_adjust(left=0.15)
        cbar = fig.colorbar(im2, ax=[ax1, ax2], shrink=0.8, pad=0.05, location='left')
        cbar.set_label('偏置误差绝对值', fontsize=10)
        
        # 计算改进百分比
        baseline_mean = np.mean(baseline_layer) if baseline_layer else 0
        compensated_mean = np.mean(compensated_layer) if compensated_layer else 0
        improvement = ((baseline_mean - compensated_mean) / baseline_mean * 100) if baseline_mean != 0 else 0
        
        # 添加总标题
        fig.suptitle(f'第{layer_idx+1}层偏置误差对比 (改进: {improvement:.1f}%)', 
                    fontsize=14, fontweight='bold')
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图片
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        plot_name = f"layer_{layer_idx+1}_bias_error_heatmap"
        fig_path = output_dir / f"{plot_name}.png"
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        # 保存原始数据
        plot_data = {
            'plot_type': 'layer_bias_error_heatmap',
            'data': {
                'layer': layer_idx + 1,
                'baseline_values': baseline_layer,
                'compensated_values': compensated_layer,
                'vmin': vmin,
                'vmax': vmax,
                'improvement_percent': improvement
            },
            'metadata': {
                'layer': layer_idx + 1,
                'channel_count': len(baseline_layer),
                'units': 'bias_error_absolute'
            }
        }
        save_plot_data(plot_data, str(output_dir), plot_name)


def plot_rms_layer_comparison(baseline_analysis: Dict[str, Any], 
                              compensated_analysis: Dict[str, Any],
                              layer_idx: int,
                              output_path: str,
                              config: Dict[str, Any] = None) -> str:
    """
    绘制单层的RMS误差对比条形图
    
    Args:
        baseline_analysis: 基准分析数据
        compensated_analysis: 补偿后分析数据
        layer_idx: 层索引
        output_path: 输出路径
        config: 配置字典
        
    Returns:
        保存的图片路径
    """
    setup_academic_style(config)
    
    # 获取RMS误差数据
    baseline_rms = baseline_analysis['layer_analysis'][layer_idx-1]['rms_error']
    compensated_rms = compensated_analysis['layer_analysis'][layer_idx-1]['rms_error']
    
    # 计算改进百分比
    improvement = (baseline_rms - compensated_rms) / baseline_rms * 100 if baseline_rms != 0 else 0
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # 数据准备
    categories = ['RMS误差']
    baseline_values = [baseline_rms]
    compensated_values = [compensated_rms]
    
    x = np.arange(len(categories))
    width = 0.35
    
    # 绘制条形图
    colors = config.get('colors', {}) if config else {}
    baseline_color = colors.get('baseline', '#E74C3C')
    compensated_color = colors.get('compensated', '#27AE60')
    
    bars1 = ax.bar(x - width/2, baseline_values, width, 
                    label='基准', color=baseline_color, edgecolor='darkred', linewidth=1, alpha=0.8)
    bars2 = ax.bar(x + width/2, compensated_values, width,
                    label='补偿后', color=compensated_color, edgecolor='darkgreen', linewidth=1, alpha=0.8)
    
    # 添加数值标注
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(format_chart_number(height),
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # 设置标签和标题
    ax.set_ylabel('RMS误差')
    ax.set_title(f'第{layer_idx}层RMS误差对比 (改进: {improvement:.1f}%)', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3, axis='y')
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_name = f"layer_{layer_idx}_rms_comparison"
    fig_path = output_dir / f"{plot_name}.png"
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    # 保存原始数据
    plot_data = {
        'plot_type': 'layer_rms_comparison',
        'data': {
            'layer': layer_idx,
            'baseline_rms': baseline_rms,
            'compensated_rms': compensated_rms,
            'improvement_percent': improvement
        },
        'metadata': {
            'layer': layer_idx,
            'units': 'rms_error'
        }
    }
    save_plot_data(plot_data, str(output_dir), plot_name)
    
    return str(fig_path)


def plot_combined_improvement_comparison(comparison_data: Dict[str, Any],
                                       output_path: str,
                                       config: Dict[str, Any] = None) -> str:
    """
    绘制偏置误差和RMS误差绝对值对比图
    
    Args:
        comparison_data: 完整的对比数据
        output_path: 输出路径
        config: 配置字典
        
    Returns:
        保存的图片路径
    """
    setup_academic_style(config)
    
    # 提取数据
    baseline = comparison_data['baseline']
    compensated = comparison_data['compensated']
    
    layers = sorted(baseline['layers'].keys())
    
    # 准备数据
    bias_baseline_values = []
    bias_compensated_values = []
    rms_baseline_values = []
    rms_compensated_values = []
    
    for layer_idx in layers:
        # 偏置误差数据
        bias_baseline = abs(baseline['layers'][layer_idx]['summary']['mean_bias_error'])
        bias_compensated = abs(compensated['layers'][layer_idx]['summary']['mean_bias_error'])
        bias_baseline_values.append(bias_baseline)
        bias_compensated_values.append(bias_compensated)
        
        # RMS误差数据
        rms_baseline = baseline['analysis']['layer_analysis'][layer_idx-1]['rms_error']
        rms_compensated = compensated['analysis']['layer_analysis'][layer_idx-1]['rms_error']
        rms_baseline_values.append(rms_baseline)
        rms_compensated_values.append(rms_compensated)
    
    # 创建图形和双y轴
    fig, ax1 = plt.subplots(figsize=(14, 8))
    ax2 = ax1.twinx()  # 创建第二个y轴
    
    # 设置柱状图位置
    x = np.arange(len(layers))
    width = 0.2
    
    # 设置颜色：偏置误差用红绿，RMS误差用蓝紫
    colors = config.get('colors', {}) if config else {}
    bias_baseline_color = colors.get('baseline', '#E74C3C')  # 红色
    bias_compensated_color = colors.get('compensated', '#27AE60')  # 绿色
    rms_baseline_color = '#3498DB'  # 蓝色
    rms_compensated_color = '#9B59B6'  # 紫色
    
    # 偏置误差组（使用左y轴）
    bars1 = ax1.bar(x - 1.5*width, bias_baseline_values, width, 
                   label='偏置误差(基准)', color=bias_baseline_color, alpha=0.8, edgecolor='darkred')
    bars2 = ax1.bar(x - 0.5*width, bias_compensated_values, width,
                   label='偏置误差(补偿后)', color=bias_compensated_color, alpha=0.8, edgecolor='darkgreen')
    
    # RMS误差组（使用右y轴）
    bars3 = ax2.bar(x + 0.5*width, rms_baseline_values, width,
                   label='RMS误差(基准)', color=rms_baseline_color, alpha=0.8, edgecolor='darkblue')
    bars4 = ax2.bar(x + 1.5*width, rms_compensated_values, width,
                   label='RMS误差(补偿后)', color=rms_compensated_color, alpha=0.8, edgecolor='darkmagenta')
    
    # 添加数值标注
    # 偏置误差标注（使用ax1坐标）
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax1.annotate(format_chart_number(height),
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=9, fontweight='bold',
                            rotation=45)
    
    # RMS误差标注（使用ax2坐标）
    for bars in [bars3, bars4]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax2.annotate(format_chart_number(height),
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=9, fontweight='bold',
                            rotation=45)
    
    # 设置标签和标题
    ax1.set_xlabel('层', fontsize=12)
    ax1.set_ylabel('偏置误差绝对值', fontsize=12, color='black')
    ax2.set_ylabel('RMS误差', fontsize=12, color='black')
    ax1.set_title('偏置误差与RMS误差绝对值对比（双y轴）', fontsize=16, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels([f'Layer {l}' for l in layers])
    
    # 设置y轴颜色
    ax1.tick_params(axis='y', labelcolor='black')
    ax2.tick_params(axis='y', labelcolor='black')
    
    # 合并图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=10, ncol=2)
    
    # 设置网格
    ax1.grid(True, alpha=0.3, axis='y')
    
    # 在每层中间添加分隔线
    for i in range(len(layers)-1):
        ax1.axvline(x=i+0.5, color='gray', linestyle=':', alpha=0.5)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_name = "overview_bias_rms_dual_axis_comparison"
    fig_path = output_dir / f"{plot_name}.png"
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    # 保存原始数据
    plot_data = {
        'plot_type': 'bias_rms_dual_axis_comparison',
        'data': {
            'layers': layers,
            'bias_baseline': bias_baseline_values,
            'bias_compensated': bias_compensated_values,
            'rms_baseline': rms_baseline_values,
            'rms_compensated': rms_compensated_values
        },
        'metadata': {
            'units': 'absolute_values_dual_axis',
            'left_axis': 'bias_error',
            'right_axis': 'rms_error'
        }
    }
    save_plot_data(plot_data, str(output_dir), plot_name)
    
    return str(fig_path)