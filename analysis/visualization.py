"""
假频抑制效果可视化模块
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import os


def visualize_alias_suppression(data_path, save_path=None, show=False):
    """
    可视化假频抑制效果
    
    参数:
        data_path: linear_response.json文件路径或数据字典
        save_path: 保存图像的路径（可选）
        show: 是否显示图像
    """
    # 加载数据
    if isinstance(data_path, str):
        with open(data_path, 'r') as f:
            data = json.load(f)
    else:
        data = data_path
    
    gains_origin = np.array(data['gains_origin'][0])
    gains_comped = np.array(data['gains_comped'][0])
    frequencies = np.array(data['frequencies'])
    
    # 创建图形
    plt.figure(figsize=(12, 8))
    
    # 绘制原始和补偿后的频响曲线
    plt.subplot(2, 1, 1)
    plt.plot(frequencies, gains_origin, 'b-', label='Original Response', linewidth=2)
    plt.plot(frequencies, gains_comped, 'r--', label='Compensated Response', linewidth=2)
    
    # 标注假频区间
    plt.axvspan(90, 100, alpha=0.2, color='yellow', label='Core Alias Region (90-100Hz)')
    plt.axvspan(85, 105, alpha=0.1, color='orange', label='Extended Region (85-105Hz)')
    
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Sensitivity (V/m/s)')
    plt.title('Alias Suppression Effect Comparison')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim([10, 120])
    
    # 绘制局部放大图（90-100Hz）
    plt.subplot(2, 1, 2)
    # 找出85-105Hz的索引
    core_indices = np.where((frequencies >= 85) & (frequencies <= 105))[0]
    
    plt.plot(frequencies[core_indices], gains_origin[core_indices], 'b-', 
             label='Original Response', linewidth=2, marker='o', markersize=4)
    plt.plot(frequencies[core_indices], gains_comped[core_indices], 'r--', 
             label='Compensated Response', linewidth=2, marker='s', markersize=4)
    
    # 标注核心假频区间
    plt.axvspan(90, 100, alpha=0.2, color='yellow', label='Core Alias Region')
    
    # 计算并显示波动幅度
    core_90_100_indices = np.where((frequencies >= 90) & (frequencies <= 100))[0]
    orig_ripple = np.max(gains_origin[core_90_100_indices]) - np.min(gains_origin[core_90_100_indices])
    comp_ripple = np.max(gains_comped[core_90_100_indices]) - np.min(gains_comped[core_90_100_indices])
    suppression_ratio = (orig_ripple - comp_ripple) / orig_ripple * 100 if orig_ripple > 0 else 0
    
    # 添加文本注释
    plt.text(0.02, 0.98, f'Original Ripple: {orig_ripple:.1f} V/m/s\n'
                         f'Compensated Ripple: {comp_ripple:.1f} V/m/s\n'
                         f'Suppression Ratio: {suppression_ratio:.1f}%',
             transform=plt.gca().transAxes, 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
             verticalalignment='top')
    
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Sensitivity (V/m/s)')
    plt.title('Zoomed View of Alias Region (85-105Hz)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 保存图像
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Visualization saved to: {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()
    
    return suppression_ratio


def visualize_batch_results(results, save_path=None, show=False):
    """
    可视化批量评估结果
    
    参数:
        results: 评估结果列表或结果文件路径
        save_path: 保存图像的路径（可选）
        show: 是否显示图像
    """
    # 加载评估结果
    if isinstance(results, str):
        with open(results, 'r') as f:
            results = json.load(f)
    
    if not results:
        print("No results to visualize")
        return
    
    # 提取数据
    experiments = [r['experiment'] for r in results]
    asr_core = [r['ASR_core'] for r in results]
    overall_scores = [r['overall_score'] for r in results]
    grades = [r['grade'] for r in results]
    
    # 创建图形
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # 绘制核心区间抑制率
    bars1 = ax1.bar(range(len(experiments)), asr_core, color='skyblue')
    ax1.set_xlabel('Experiment')
    ax1.set_ylabel('Core Region Suppression Ratio (%)')
    ax1.set_title('Alias Suppression Ratio Comparison')
    ax1.set_xticks(range(len(experiments)))
    ax1.set_xticklabels(experiments, rotation=45, ha='right')
    
    # 添加数值标签
    for i, (bar, value) in enumerate(zip(bars1, asr_core)):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{value:.1f}%', ha='center', va='bottom')
    
    # 绘制综合评分
    colors = ['green' if g == 'A' else 'blue' if g == 'B' 
              else 'orange' if g == 'C' else 'red' for g in grades]
    bars2 = ax2.bar(range(len(experiments)), overall_scores, color=colors)
    ax2.set_xlabel('Experiment')
    ax2.set_ylabel('Overall Score')
    ax2.set_title('Overall Performance Score')
    ax2.set_xticks(range(len(experiments)))
    ax2.set_xticklabels(experiments, rotation=45, ha='right')
    ax2.set_ylim(0, 100)
    
    # 添加等级标签
    for i, (bar, score, grade) in enumerate(zip(bars2, overall_scores, grades)):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{score:.1f}\n({grade})', ha='center', va='bottom')
    
    # 添加评级参考线
    ax2.axhline(y=80, color='green', linestyle='--', alpha=0.5, label='Grade A (≥80)')
    ax2.axhline(y=60, color='blue', linestyle='--', alpha=0.5, label='Grade B (≥60)')
    ax2.axhline(y=40, color='orange', linestyle='--', alpha=0.5, label='Grade C (≥40)')
    ax2.legend(loc='upper right')
    
    plt.tight_layout()
    
    # 保存图像
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Comparison chart saved to: {save_path}")
    
    if show:
        plt.show()
    else:
        plt.close()