"""
参数效率分析模块

分析模型参数量与假频抑制性能的关系，生成参数效率图表和综合报告。
"""

import os
import sys
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime

# 添加项目路径
sys.path.append('/home/ubuntu/met_nonlinear')
from analysis.alias_suppression import batch_evaluate_experiments

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def analyze_parameter_efficiency(save_path='documentation/images'):
    """分析所有实验的参数效率"""
    
    # 确保保存路径存在
    os.makedirs(save_path, exist_ok=True)
    
    # 定义所有实验
    all_experiments = [
        'WNET5_RealAlias',  # 基线
        'WNET5_RealAlias_E01',
        'WNET5_RealAlias_E02',
        'WNET5_RealAlias_E03',
        'WNET5_RealAlias_E04',
        'WNET5_RealAlias_E05',
        'WNET5_RealAlias_E06',
        'WNET5_RealAlias_E07',
        'WNET5_RealAlias_E08',
        'WNET5_RealAlias_E09',
        'WNET5_RealAlias_E10',
        'WNET5_RealAlias_E11',
        'WNET5_RealAlias_E12'
    ]
    
    # 批量评估实验
    print("=== 评估所有实验 ===")
    results = batch_evaluate_experiments(all_experiments)
    
    # 提取数据用于绘图
    params_list = []
    asr_list = []
    names_list = []
    colors_list = []
    
    # 定义颜色方案
    color_map = {
        'baseline': '#808080',  # 灰色
        'phase1': '#1f77b4',    # 蓝色
        'phase2': '#ff7f0e',    # 橙色
        'best': '#2ca02c'       # 绿色
    }
    
    for result in results:
        if result['total_params'] > 0:  # 只包含有参数信息的实验
            params_list.append(result['total_params'])
            asr_list.append(result['ASR_core'])
            
            # 简化实验名称
            name = result['experiment'].replace('WNET5_RealAlias_', '')
            if name == 'WNET5_RealAlias':
                name = 'Baseline'
            names_list.append(name)
            
            # 确定颜色
            if name == 'Baseline':
                colors_list.append(color_map['baseline'])
            elif name == 'E05':
                colors_list.append(color_map['best'])
            elif name in ['E01', 'E02', 'E03', 'E04', 'E06']:
                colors_list.append(color_map['phase1'])
            else:
                colors_list.append(color_map['phase2'])
    
    # 创建图表
    plt.figure(figsize=(12, 8))
    
    # 绘制散点图
    scatter = plt.scatter(params_list, asr_list, s=150, alpha=0.7, c=colors_list, edgecolors='black', linewidth=1.5)
    
    # 为每个点添加标签
    for i, name in enumerate(names_list):
        plt.annotate(name, (params_list[i], asr_list[i]), 
                    xytext=(5, 5), textcoords='offset points', 
                    fontsize=10, fontweight='bold' if name in ['Baseline', 'E05'] else 'normal')
    
    # 添加帕累托前沿线（连接效率最优的点）
    # 找出帕累托最优点：对于每个参数量，找出最高的ASR
    pareto_points = []
    unique_params = sorted(set(params_list))
    for param in unique_params:
        indices = [i for i, p in enumerate(params_list) if p == param]
        max_asr = max(asr_list[i] for i in indices)
        pareto_points.append((param, max_asr))
    
    # 绘制帕累托前沿
    pareto_params, pareto_asr = zip(*pareto_points)
    plt.plot(pareto_params, pareto_asr, 'r--', alpha=0.5, linewidth=2, label='Pareto Frontier')
    
    # 设置图表属性
    plt.xlabel('Total Parameters', fontsize=14)
    plt.ylabel('Alias Suppression Ratio (%)', fontsize=14)
    plt.title('Parameter Efficiency Analysis: Parameters vs Performance', fontsize=16, fontweight='bold')
    
    # 添加网格
    plt.grid(True, alpha=0.3, linestyle='--')
    
    # 设置坐标轴范围
    plt.xlim(min(params_list) * 0.9, max(params_list) * 1.1)
    plt.ylim(0, max(asr_list) * 1.1)
    
    # 添加图例
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=color_map['baseline'], label='Baseline'),
        Patch(facecolor=color_map['phase1'], label='Phase1 (E01-E06)'),
        Patch(facecolor=color_map['phase2'], label='Phase2 (E07-E12)'),
        Patch(facecolor=color_map['best'], label='Best (E05)'),
        plt.Line2D([0], [0], color='red', linestyle='--', label='Pareto Frontier')
    ]
    plt.legend(handles=legend_elements, loc='lower right', fontsize=12)
    
    # 保存图表
    plot_path = os.path.join(save_path, 'parameter_efficiency_analysis.png')
    plt.tight_layout()
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\n参数效率分析图已保存到: {plot_path}")
    
    # 生成参数效率分析表格
    generate_efficiency_table(results, save_path)
    
    return results, plot_path


def generate_efficiency_table(results, save_path):
    """生成参数效率分析表格"""
    
    # 计算效率指标：ASR per 1000 parameters
    efficiency_data = []
    
    for result in results:
        if result['total_params'] > 0:
            efficiency = result['ASR_core'] / (result['total_params'] / 1000)
            efficiency_data.append({
                'experiment': result['experiment'],
                'total_params': result['total_params'],
                'trainable_params': result['trainable_params'],
                'ASR_core': result['ASR_core'],
                'efficiency': efficiency,
                'overall_score': result['overall_score'],
                'grade': result['grade']
            })
    
    # 按效率排序
    efficiency_data.sort(key=lambda x: x['efficiency'], reverse=True)
    
    # 生成Markdown表格
    table_md = "# 参数效率分析表\n\n"
    table_md += "| 实验 | 总参数量 | 可训练参数 | 核心ASR | 效率(ASR/千参数) | 综合评分 | 等级 |\n"
    table_md += "|------|----------|------------|---------|------------------|----------|------|\n"
    
    for data in efficiency_data:
        exp_name = data['experiment'].replace('WNET5_RealAlias_', '').replace('WNET5_RealAlias', 'Baseline')
        table_md += f"| {exp_name} | {data['total_params']:,} | {data['trainable_params']:,} | "
        table_md += f"{data['ASR_core']:.1f}% | {data['efficiency']:.2f} | "
        table_md += f"{data['overall_score']:.1f} | {data['grade']} |\n"
    
    # 保存表格
    table_path = os.path.join(save_path, 'parameter_efficiency_table.md')
    with open(table_path, 'w', encoding='utf-8') as f:
        f.write(table_md)
    
    print(f"参数效率表格已保存到: {table_path}")
    
    # 输出关键发现
    print("\n=== 参数效率分析关键发现 ===")
    print(f"最高效率实验: {efficiency_data[0]['experiment']} ({efficiency_data[0]['efficiency']:.2f} ASR/千参数)")
    print(f"最高性能实验: E05 (90.3% ASR)")
    
    # 找出最优参数量区间
    high_perf = [d for d in efficiency_data if d['ASR_core'] > 80]
    if high_perf:
        param_range = (min(d['total_params'] for d in high_perf), 
                      max(d['total_params'] for d in high_perf))
        print(f"高性能参数区间: {param_range[0]:,} - {param_range[1]:,}")


if __name__ == "__main__":
    results, plot_path = analyze_parameter_efficiency()