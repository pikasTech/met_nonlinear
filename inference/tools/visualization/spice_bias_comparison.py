#!/usr/bin/env python3
"""
SPICE偏置补偿对比可视化工具

用于对比分析基准和补偿后的SPICE推理结果，
生成学术风格的可视化图表和原始数据。
"""

import argparse
import json
import sys
import os
from pathlib import Path
from datetime import datetime
import traceback
import matplotlib.pyplot as plt
import numpy as np

# 添加模块路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_loader import compare_inference_results, InferenceDataLoader
from utils.plot_helpers import (
    setup_academic_style,
    plot_layer_bias_comparison,
    plot_layer_bias_comparison_simple,
    plot_global_improvement_bar,
    plot_bias_error_heatmap,
    plot_rms_layer_comparison,
    plot_combined_improvement_comparison,
    save_plot_data
)
from utils.statistics import (
    generate_statistics_summary,
    format_statistics_table
)
from utils.report_generator import (
    generate_markdown_report,
    generate_summary_statistics
)


def load_config(config_path: str = None) -> dict:
    """加载配置文件"""
    if config_path is None:
        # 使用默认配置文件
        config_path = Path(__file__).parent / 'config.json'
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_output_directories(output_base: str) -> dict:
    """创建输出目录结构"""
    base_path = Path(output_base)
    
    # 创建主要目录
    figures_dir = base_path / 'figures'
    raw_dir = base_path / 'figures' / 'raw'
    
    # 创建子目录
    subdirs = ['overview', 'layer_analysis', 'channel_analysis', 
               'distribution', 'statistics']
    
    paths = {}
    for subdir in subdirs:
        fig_path = figures_dir / subdir
        raw_path = raw_dir / subdir
        fig_path.mkdir(parents=True, exist_ok=True)
        raw_path.mkdir(parents=True, exist_ok=True)
        paths[subdir] = str(fig_path)
    
    return paths


def plot_layer_improvements(comparison_data: dict, output_paths: dict, config: dict):
    """绘制逐层改进分析图"""
    
    baseline = comparison_data['baseline']
    compensated = comparison_data['compensated']
    layer_dir = output_paths['layer_analysis']
    
    # 检查是否启用RMS分析
    include_rms = config.get('plots', {}).get('rms_analysis', False)
    
    if include_rms:
        print("绘制逐层偏置误差与RMS误差对比...")
        # 绘制每层的偏置误差+RMS误差对比图（合并版本）
        for layer_idx in baseline['layers']:
            print(f"  - 第{layer_idx}层偏置误差+RMS误差...")
            plot_layer_bias_comparison(baseline, compensated, layer_idx, 
                                     layer_dir, config)
        
        print("绘制单独的RMS误差对比...")
        # 仍然保留单独的RMS误差对比图
        for layer_idx in baseline['layers']:
            print(f"  - 第{layer_idx}层RMS误差...")
            plot_rms_layer_comparison(baseline['analysis'], compensated['analysis'], 
                                    layer_idx, layer_dir, config)
    else:
        print("绘制逐层偏置误差对比...")
        # 只绘制偏置误差对比图（不包含RMS）
        for layer_idx in baseline['layers']:
            print(f"  - 第{layer_idx}层偏置误差...")
            plot_layer_bias_comparison_simple(baseline, compensated, layer_idx, 
                                            layer_dir, config)


def plot_overview_analysis(comparison_data: dict, output_paths: dict, config: dict):
    """绘制总览分析图"""
    print("绘制总览分析...")
    
    improvements = comparison_data['improvements']['bias_global']
    overview_dir = output_paths['overview']
    
    # 绘制全局改进条形图
    plot_global_improvement_bar(improvements, overview_dir, config)
    
    # 绘制逐层偏置误差改进趋势图
    layer_improvements = comparison_data['improvements']['bias_layer']
    
    setup_academic_style(config)
    fig, ax = plt.subplots(figsize=(10, 6))
    
    layers = sorted(layer_improvements.keys())
    improvements_values = [layer_improvements[l] for l in layers]
    
    ax.plot(layers, improvements_values, 'o-', linewidth=2, markersize=8)
    ax.set_xlabel('层')
    ax.set_ylabel('改进百分比 (%)')
    ax.set_title('逐层偏置误差改进趋势')
    ax.set_xticks(layers)
    ax.set_xticklabels([f'Layer {l}' for l in layers])
    ax.grid(True, alpha=0.3)
    
    # 添加数值标注
    for i, (layer, improvement) in enumerate(zip(layers, improvements_values)):
        ax.annotate(f'{improvement:.1f}%', 
                   xy=(layer, improvement),
                   xytext=(0, 10),
                   textcoords='offset points',
                   ha='center', fontsize=10)
    
    plt.tight_layout()
    plot_name = "overview_layer_improvement_trend"
    fig_path = Path(overview_dir) / f"{plot_name}.png"
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    # 保存原始数据
    plot_data = {
        'plot_type': 'layer_improvement_trend',
        'data': {
            'layers': layers,
            'improvements': improvements_values
        },
        'metadata': {
            'units': 'percent'
        }
    }
    save_plot_data(plot_data, overview_dir, plot_name)
    
    # 检查是否启用RMS分析
    include_rms = config.get('plots', {}).get('rms_analysis', False)
    
    if include_rms:
        # 绘制偏置误差与RMS误差绝对值对比图
        print("绘制偏置误差与RMS误差绝对值对比...")
        plot_combined_improvement_comparison(comparison_data, overview_dir, config)


def plot_channel_analysis(comparison_data: dict, output_paths: dict, config: dict):
    """绘制通道级分析图"""
    print("绘制通道级分析...")
    
    baseline_matrix = comparison_data['baseline']['matrix']
    compensated_matrix = comparison_data['compensated']['matrix']
    channel_dir = output_paths['channel_analysis']
    
    # 绘制偏置误差热力图
    plot_bias_error_heatmap(baseline_matrix, compensated_matrix, 
                           channel_dir, config)


def plot_distribution_analysis(comparison_data: dict, output_paths: dict, config: dict):
    """绘制误差分布分析图"""
    print("绘制误差分布分析...")
    
    # 收集所有误差值
    baseline_errors = []
    compensated_errors = []
    
    for layer_idx in comparison_data['baseline']['layers']:
        layer_baseline = comparison_data['baseline']['layers'][layer_idx]
        layer_compensated = comparison_data['compensated']['layers'][layer_idx]
        
        for ch in layer_baseline['bias_errors']:
            baseline_errors.append(abs(ch['bias_error']))
        for ch in layer_compensated['bias_errors']:
            compensated_errors.append(abs(ch['bias_error']))
    
    setup_academic_style(config)
    
    # 绘制误差分布直方图
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bins = np.linspace(0, max(max(baseline_errors), max(compensated_errors)), 30)
    
    # 使用彩色显示
    colors = config.get('colors', {}) if config else {}
    baseline_color = colors.get('baseline', '#E74C3C')
    compensated_color = colors.get('compensated', '#27AE60')
    
    ax.hist(baseline_errors, bins=bins, alpha=0.7, label='基准', 
            color=baseline_color, edgecolor='darkred', linewidth=1)
    ax.hist(compensated_errors, bins=bins, alpha=0.7, label='补偿后', 
            color=compensated_color, edgecolor='darkgreen', linewidth=1)
    
    ax.set_xlabel('偏置误差绝对值')
    ax.set_ylabel('频数')
    ax.set_title('偏置误差分布对比')
    ax.legend()
    
    # 添加均值线
    ax.axvline(np.mean(baseline_errors), color=baseline_color, linestyle='--', 
               linewidth=2, alpha=0.8, label=f'基准均值: {np.mean(baseline_errors):.4f}')
    ax.axvline(np.mean(compensated_errors), color=compensated_color, linestyle='--',
               linewidth=2, alpha=0.8, label=f'补偿后均值: {np.mean(compensated_errors):.4f}')
    
    plt.tight_layout()
    plot_name = "distribution_error_histogram"
    dist_dir = output_paths['distribution']
    fig_path = Path(dist_dir) / f"{plot_name}.png"
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    # 保存原始数据
    plot_data = {
        'plot_type': 'error_distribution_histogram',
        'data': {
            'baseline_errors': baseline_errors,
            'compensated_errors': compensated_errors,
            'bins': bins.tolist(),
            'baseline_mean': float(np.mean(baseline_errors)),
            'compensated_mean': float(np.mean(compensated_errors))
        },
        'metadata': {
            'units': 'bias_error_absolute',
            'n_samples': len(baseline_errors)
        }
    }
    save_plot_data(plot_data, dist_dir, plot_name)


def create_statistics_table(comparison_data: dict, output_paths: dict, config: dict):
    """创建统计表格"""
    print("生成统计表格...")
    
    stats_summary = generate_statistics_summary(comparison_data)
    table_data = format_statistics_table(stats_summary)
    
    setup_academic_style(config)
    
    # 创建表格图形
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('tight')
    ax.axis('off')
    
    # 创建表格
    table = ax.table(cellText=table_data[1:], colLabels=table_data[0],
                     cellLoc='center', loc='center')
    
    # 设置表格样式
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    # 设置表头样式
    for i in range(len(table_data[0])):
        table[(0, i)].set_facecolor('#E0E0E0')
        table[(0, i)].set_text_props(weight='bold')
    
    # 设置行颜色交替
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            for j in range(len(table_data[0])):
                table[(i, j)].set_facecolor('#F5F5F5')
    
    plt.title('偏置补偿效果统计汇总', fontsize=16, fontweight='bold', pad=20)
    
    plot_name = "statistics_summary_table"
    stats_dir = output_paths['statistics']
    fig_path = Path(stats_dir) / f"{plot_name}.png"
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    # 保存原始数据
    plot_data = {
        'plot_type': 'statistics_summary_table',
        'data': {
            'table': table_data,
            'statistics': stats_summary
        },
        'metadata': {
            'generated_at': datetime.now().isoformat()
        }
    }
    save_plot_data(plot_data, stats_dir, plot_name)
    
    # 如果需要，生成LaTeX表格
    if config.get('output', {}).get('latex_tables', False):
        latex_path = Path(stats_dir) / f"{plot_name}.tex"
        with open(latex_path, 'w', encoding='utf-8') as f:
            f.write("\\begin{table}[h]\n")
            f.write("\\centering\n")
            f.write("\\caption{偏置补偿效果统计汇总}\n")
            f.write("\\begin{tabular}{|l|c|c|c|c|}\n")
            f.write("\\hline\n")
            f.write(" & ".join(table_data[0]) + " \\\\\n")
            f.write("\\hline\n")
            for row in table_data[1:]:
                f.write(" & ".join(row) + " \\\\\n")
            f.write("\\hline\n")
            f.write("\\end{tabular}\n")
            f.write("\\end{table}\n")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='SPICE偏置补偿对比可视化工具',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--baseline', required=True,
                        help='基准推理结果目录')
    parser.add_argument('--compensated', required=True,
                        help='补偿后推理结果目录')
    parser.add_argument('--output', default='inference/results/bias_comparison',
                        help='输出目录 (默认: inference/results/bias_comparison)')
    parser.add_argument('--config', default=None,
                        help='配置文件路径 (默认: 使用同目录下的config.json)')
    
    args = parser.parse_args()
    
    try:
        # 加载配置
        print("加载配置文件...")
        config = load_config(args.config)
        
        # 创建输出目录
        print("创建输出目录...")
        output_paths = create_output_directories(args.output)
        
        # 加载和对比数据
        print("加载推理数据...")
        print(f"  基准: {args.baseline}")
        print(f"  补偿后: {args.compensated}")
        comparison_data = compare_inference_results(args.baseline, args.compensated)
        
        # 打印基本信息
        print(f"\n项目: {comparison_data['project_name']}")
        print(f"偏置误差全局改进:")
        print(f"  - 平均偏置: {comparison_data['improvements']['bias_global']['mean']:.1f}%")
        print(f"  - 标准差: {comparison_data['improvements']['bias_global']['std']:.1f}%")
        print(f"  - 最大误差: {comparison_data['improvements']['bias_global']['max']:.1f}%")
        
        # 只在启用RMS分析时显示RMS信息
        if config['plots'].get('rms_analysis', False):
            print(f"RMS误差全局改进:")
            print(f"  - 平均RMS: {comparison_data['improvements']['rms_global']['mean']:.1f}%")
            print(f"  - 最大RMS: {comparison_data['improvements']['rms_global']['max']:.1f}%")
        
        # 根据配置生成图表
        print("\n生成可视化图表...")
        
        if config['plots'].get('overview', True):
            plot_overview_analysis(comparison_data, output_paths, config)
            
        if config['plots'].get('layer_analysis', True):
            plot_layer_improvements(comparison_data, output_paths, config)
            
        if config['plots'].get('channel_analysis', True):
            plot_channel_analysis(comparison_data, output_paths, config)
            
        if config['plots'].get('distribution', True):
            plot_distribution_analysis(comparison_data, output_paths, config)
            
        if config['plots'].get('statistics', True):
            create_statistics_table(comparison_data, output_paths, config)
        
        print(f"\n完成! 结果保存在: {args.output}")
        
        # 生成Markdown分析报告
        print("生成汇总分析报告...")
        md_report_path = generate_markdown_report(comparison_data, args.output, config)
        print(f"分析报告已保存: {md_report_path}")
        
        # 生成完成报告
        report_path = Path(args.output) / 'visualization_report.json'
        report = {
            'timestamp': datetime.now().isoformat(),
            'baseline_dir': args.baseline,
            'compensated_dir': args.compensated,
            'output_dir': args.output,
            'config_used': config,
            'project_name': comparison_data['project_name'],
            'bias_global_improvements': comparison_data['improvements']['bias_global'],
            'files_generated': {
                'figures': len(list(Path(args.output).glob('figures/**/*.png'))),
                'raw_data': len(list(Path(args.output).glob('figures/raw/**/*.json'))),
                'analysis_report': md_report_path
            }
        }
        
        # 只在启用RMS分析时包含RMS全局改进
        if config['plots'].get('rms_analysis', False):
            report['rms_global_improvements'] = comparison_data['improvements']['rms_global']
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print(f"可视化报告已保存: {report_path}")
        
    except Exception as e:
        print(f"\n错误: {str(e)}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()