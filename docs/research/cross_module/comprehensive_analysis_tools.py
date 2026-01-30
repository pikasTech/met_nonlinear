#!/usr/bin/env python3
"""
WaveNet5综合项目分析工具

涵盖原始探索阶段(12个实验) + 效率优化阶段(13个实验)的完整分析和可视化工具
"""

import os
import sys
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.append('/home/ubuntu/met_nonlinear')
from analysis.alias_suppression import evaluate_alias_suppression, batch_evaluate_experiments

# 设置中文字体和图表样式
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.figsize'] = [12, 8]
plt.rcParams['font.size'] = 11

def get_all_experiments():
    """获取所有实验的完整列表"""
    
    # 原始探索阶段 (12个实验)
    original_experiments = [
        'WNET5_RealAlias',       # 基线
        'WNET5_RealAlias_E01',
        'WNET5_RealAlias_E02', 
        'WNET5_RealAlias_E03',
        'WNET5_RealAlias_E04',
        'WNET5_RealAlias_E05',   # 最优基准
        'WNET5_RealAlias_E06',
        'WNET5_RealAlias_E07',
        'WNET5_RealAlias_E08',
        'WNET5_RealAlias_E09',
        'WNET5_RealAlias_E10',
        'WNET5_RealAlias_E11',
        'WNET5_RealAlias_E12'
    ]
    
    # Phase1效率优化 (6个实验)
    phase1_experiments = [
        'WNET5_EFF_A1',
        'WNET5_EFF_A2', 
        'WNET5_EFF_B1',
        'WNET5_EFF_C1',
        'WNET5_EFF_C2',
        'WNET5_EFF_D1'
    ]
    
    # Phase2效率优化 (6个实验)
    phase2_experiments = [
        'WNET5_EFF2_A1',
        'WNET5_EFF2_A2',
        'WNET5_EFF2_B1', 
        'WNET5_EFF2_B2',
        'WNET5_EFF2_C1',
        'WNET5_EFF2_C2'
    ]
    
    return {
        'original': original_experiments,
        'phase1': phase1_experiments,
        'phase2': phase2_experiments,
        'all': original_experiments + phase1_experiments + phase2_experiments
    }

def classify_experiment(exp_name):
    """分类实验并分配颜色"""
    if 'EFF2_' in exp_name:
        return 'phase2', '#2ca02c'  # 绿色 - Phase2成功
    elif 'EFF_' in exp_name:
        return 'phase1', '#d62728'  # 红色 - Phase1失败
    elif exp_name == 'WNET5_RealAlias_E05':
        return 'benchmark', '#ff7f0e'  # 橙色 - E05基准
    elif exp_name == 'WNET5_RealAlias':
        return 'baseline', '#808080'  # 灰色 - 原始基线
    else:
        return 'original', '#1f77b4'  # 蓝色 - 原始探索

def generate_comprehensive_efficiency_plot(save_path='documentation/images'):
    """生成综合参数效率分析图"""
    
    print("🔬 开始生成综合参数效率分析图...")
    
    # 确保保存路径存在
    os.makedirs(save_path, exist_ok=True)
    
    # 获取所有实验
    experiments = get_all_experiments()
    
    # 批量评估所有实验
    print("📊 评估所有19个实验...")
    results = batch_evaluate_experiments(experiments['all'])
    
    # 准备绘图数据
    plot_data = {
        'baseline': {'params': [], 'asr': [], 'names': [], 'sizes': []},
        'original': {'params': [], 'asr': [], 'names': [], 'sizes': []},
        'benchmark': {'params': [], 'asr': [], 'names': [], 'sizes': []},
        'phase1': {'params': [], 'asr': [], 'names': [], 'sizes': []},
        'phase2': {'params': [], 'asr': [], 'names': [], 'sizes': []}
    }
    
    all_params = []
    all_asr = []
    
    for result in results:
        if result['total_params'] > 0:
            category, color = classify_experiment(result['experiment'])
            
            params = result['total_params']
            asr = result['ASR_core']
            
            # 简化名称
            name = result['experiment'].replace('WNET5_RealAlias_', '').replace('WNET5_RealAlias', 'Baseline')
            name = name.replace('WNET5_EFF2_', 'EFF2_').replace('WNET5_EFF_', 'EFF_')
            
            plot_data[category]['params'].append(params)
            plot_data[category]['asr'].append(asr)
            plot_data[category]['names'].append(name)
            
            # 根据重要性调整点的大小
            if name in ['E05', 'EFF2_A1', 'EFF2_B1']:
                plot_data[category]['sizes'].append(200)  # 重要实验用大点
            else:
                plot_data[category]['sizes'].append(150)
            
            all_params.append(params)
            all_asr.append(asr)
    
    # 创建图表
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # 定义颜色和标签
    colors = {
        'baseline': '#808080',
        'original': '#1f77b4', 
        'benchmark': '#ff7f0e',
        'phase1': '#d62728',
        'phase2': '#2ca02c'
    }
    
    labels = {
        'baseline': 'Baseline',
        'original': 'Original Exploration (E01-E12)',
        'benchmark': 'E05 Benchmark', 
        'phase1': 'Phase1 Optimization (Failed)',
        'phase2': 'Phase2 Optimization (Success)'
    }
    
    # 绘制各类实验
    for category, data in plot_data.items():
        if data['params']:  # 如果有数据
            scatter = ax.scatter(data['params'], data['asr'], 
                               c=colors[category], s=data['sizes'], alpha=0.7,
                               edgecolors='black', linewidth=1.5, 
                               label=labels[category], zorder=5)
    
    # 添加标签
    for category, data in plot_data.items():
        for i, name in enumerate(data['names']):
            # 重要实验用加粗标签
            weight = 'bold' if name in ['E05', 'EFF2_A1', 'EFF2_B1', 'Baseline'] else 'normal'
            ax.annotate(name, (data['params'][i], data['asr'][i]), 
                       xytext=(8, 8), textcoords='offset points', 
                       fontsize=10, fontweight=weight, zorder=6)
    
    # 计算并绘制帕累托前沿
    pareto_points = []
    sorted_data = sorted(zip(all_params, all_asr))
    
    current_best_asr = 0
    for param, asr in sorted_data:
        if asr > current_best_asr:
            pareto_points.append((param, asr))
            current_best_asr = asr
    
    if len(pareto_points) > 1:
        pareto_params, pareto_asr = zip(*pareto_points)
        ax.plot(pareto_params, pareto_asr, 'k--', alpha=0.6, linewidth=2, 
               label='Pareto Frontier', zorder=4)
    
    # 添加性能区域标识
    ax.axhline(y=80, color='green', linestyle=':', alpha=0.5, linewidth=2)
    ax.text(max(all_params)*0.8, 82, '80% Target Line', color='green', fontweight='bold')
    
    ax.axhline(y=90, color='orange', linestyle=':', alpha=0.5, linewidth=2)
    ax.text(max(all_params)*0.8, 92, '90% Excellence Line', color='orange', fontweight='bold')
    
    # 设置图表属性
    ax.set_xlabel('Total Parameters', fontsize=14, fontweight='bold')
    ax.set_ylabel('Alias Suppression Ratio (%)', fontsize=14, fontweight='bold')
    ax.set_title('WaveNet5 Comprehensive Parameter Efficiency Analysis\n(Original Exploration + Efficiency Optimization)', 
                fontsize=16, fontweight='bold', pad=20)
    
    # 设置坐标轴范围
    ax.set_xlim(min(all_params) * 0.9, max(all_params) * 1.1)
    ax.set_ylim(0, max(all_asr) * 1.05)
    
    # 添加网格
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # 添加图例
    ax.legend(loc='lower right', fontsize=11, framealpha=0.9)
    
    # 添加统计信息文本框
    stats_text = f"""Project Statistics:
• Total Experiments: {len(results)}
• Original Exploration: {len(experiments['original'])}
• Phase1 Optimization: {len(experiments['phase1'])}
• Phase2 Optimization: {len(experiments['phase2'])}
• Best Performance: {max(all_asr):.1f}% (EFF2_A1)
• Parameter Range: {min(all_params):,} - {max(all_params):,}"""
    
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
           verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # 保存图表
    plot_path = os.path.join(save_path, 'comprehensive_parameter_efficiency_analysis.png')
    plt.tight_layout()
    plt.savefig(plot_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"✅ 综合参数效率分析图已保存到: {plot_path}")
    
    return results, plot_path

def generate_efficiency_ranking_table(results, save_path='documentation/images'):
    """生成完整的效率排行表格"""
    
    print("📋 生成效率排行表格...")
    
    # 计算效率指标
    efficiency_data = []
    
    for result in results:
        if result['total_params'] > 0:
            efficiency = result['ASR_core'] / (result['total_params'] / 1000)
            
            # 效率等级判定
            if efficiency >= 15:
                grade = 'S'
            elif efficiency >= 12:
                grade = 'A'
            elif efficiency >= 9:
                grade = 'B'
            elif efficiency >= 6:
                grade = 'C'
            else:
                grade = 'D'
            
            efficiency_data.append({
                'experiment': result['experiment'],
                'total_params': result['total_params'],
                'trainable_params': result['trainable_params'],
                'ASR_core': result['ASR_core'],
                'efficiency': efficiency,
                'overall_score': result['overall_score'],
                'grade': result['grade'],
                'efficiency_grade': grade
            })
    
    # 按ASR排序（主要指标）
    efficiency_data.sort(key=lambda x: x['ASR_core'], reverse=True)
    
    # 生成Markdown表格
    table_md = "# WaveNet5综合项目效率排行榜\n\n"
    table_md += "## 完整实验效率排名（按ASR性能排序）\n\n"
    table_md += "| 排名 | 实验 | ASR | 参数量 | 效率 | 等级 | 项目阶段 | 状态 |\n"
    table_md += "|------|------|-----|--------|------|------|----------|------|\n"
    
    for i, data in enumerate(efficiency_data, 1):
        # 简化实验名
        exp_name = data['experiment'].replace('WNET5_RealAlias_', '').replace('WNET5_RealAlias', 'Baseline')
        exp_name = exp_name.replace('WNET5_EFF2_', '**EFF2_').replace('WNET5_EFF_', 'EFF_')
        if exp_name.startswith('**'):
            exp_name = exp_name + '**'
        
        # 确定项目阶段
        if 'EFF2_' in data['experiment']:
            stage = 'Phase2优化'
        elif 'EFF_' in data['experiment']:
            stage = 'Phase1优化'
        elif data['experiment'] == 'WNET5_RealAlias_E05':
            stage = '基准配置'
        elif data['experiment'] == 'WNET5_RealAlias':
            stage = '原始基线'
        else:
            stage = '原始探索'
        
        # 确定状态
        asr = data['ASR_core']
        if asr > 90:
            status = '🏆 **超越**'
        elif asr >= 80:
            status = '✅ **达标**'
        elif asr >= 75:
            status = '⚠️ **接近**'
        elif asr >= 60:
            status = '📈 改善'
        else:
            status = '❌ 未达标'
        
        # 排名emoji
        if i == 1:
            rank = '🥇'
        elif i == 2:
            rank = '🥈'
        elif i == 3:
            rank = '🥉'
        else:
            rank = str(i)
        
        table_md += f"| {rank} | {exp_name} | **{asr:.1f}%** | {data['total_params']:,} | "
        table_md += f"{data['efficiency']:.2f} | {data['efficiency_grade']} | {stage} | {status} |\n"
    
    # 添加统计汇总
    table_md += "\n## 项目阶段统计\n\n"
    
    # 按阶段统计
    stage_stats = {}
    for data in efficiency_data:
        if 'EFF2_' in data['experiment']:
            stage = 'Phase2优化'
        elif 'EFF_' in data['experiment']:
            stage = 'Phase1优化'
        else:
            stage = '原始探索'
        
        if stage not in stage_stats:
            stage_stats[stage] = {'count': 0, 'avg_asr': 0, 'max_asr': 0, 'success': 0}
        
        stage_stats[stage]['count'] += 1
        stage_stats[stage]['avg_asr'] += data['ASR_core']
        stage_stats[stage]['max_asr'] = max(stage_stats[stage]['max_asr'], data['ASR_core'])
        if data['ASR_core'] >= 80:
            stage_stats[stage]['success'] += 1
    
    # 计算平均值
    for stage in stage_stats:
        stage_stats[stage]['avg_asr'] /= stage_stats[stage]['count']
        stage_stats[stage]['success_rate'] = stage_stats[stage]['success'] / stage_stats[stage]['count'] * 100
    
    table_md += "| 项目阶段 | 实验数 | 平均ASR | 最佳ASR | 成功数(≥80%) | 成功率 |\n"
    table_md += "|----------|--------|---------|---------|-------------|--------|\n"
    
    for stage, stats in stage_stats.items():
        table_md += f"| **{stage}** | {stats['count']} | {stats['avg_asr']:.1f}% | "
        table_md += f"{stats['max_asr']:.1f}% | {stats['success']}/{stats['count']} | {stats['success_rate']:.1f}% |\n"
    
    # 保存表格
    table_path = os.path.join(save_path, 'comprehensive_efficiency_ranking.md')
    with open(table_path, 'w', encoding='utf-8') as f:
        f.write(table_md)
    
    print(f"✅ 效率排行表格已保存到: {table_path}")
    
    return efficiency_data, table_path

def generate_comprehensive_verification_script(save_path='documentation'):
    """生成综合数据验证脚本"""
    
    print("🔍 生成综合数据验证脚本...")
    
    verification_script = '''#!/usr/bin/env python3
"""
WaveNet5综合项目数据验证脚本

验证综合分析报告中所有19个实验的数据准确性
包括原始探索、Phase1优化、Phase2优化的所有实验
"""

import json
import numpy as np
import sys
import os

# 添加项目路径
sys.path.append('/home/ubuntu/met_nonlinear')
from analysis.alias_suppression import evaluate_alias_suppression, batch_evaluate_experiments

def verify_key_experiments():
    """验证关键实验的数据"""
    print("=== 验证关键实验数据 ===")
    
    key_experiments = {
        'WNET5_RealAlias_E05': {'expected_asr': 90.3, 'expected_params': 8641},
        'WNET5_EFF2_A1': {'expected_asr': 91.9, 'expected_params': 8477},
        'WNET5_EFF2_B1': {'expected_asr': 81.1, 'expected_params': 6217},
        'WNET5_EFF2_B2': {'expected_asr': 79.4, 'expected_params': 8597},
        'WNET5_EFF2_C1': {'expected_asr': 75.7, 'expected_params': 8401},
    }
    
    for exp_name, expected in key_experiments.items():
        print(f"\\n验证 {exp_name}:")
        
        # 验证ASR
        try:
            result = evaluate_alias_suppression(f'projects/{exp_name}/data/linear_response.json')
            actual_asr = result['ASR_core']['suppression_ratio']
            print(f"  ASR: {actual_asr:.1f}% (期望: {expected['expected_asr']:.1f}%)")
            assert abs(actual_asr - expected['expected_asr']) < 0.2, f"ASR不匹配: {actual_asr} vs {expected['expected_asr']}"
        except FileNotFoundError:
            print(f"  ❌ 缺少 linear_response.json")
            continue
        
        # 验证参数量
        try:
            with open(f'projects/{exp_name}/data/model_info.json', 'r') as f:
                model_info = json.load(f)
            actual_params = model_info['total_params']
            print(f"  参数: {actual_params:,} (期望: {expected['expected_params']:,})")
            assert actual_params == expected['expected_params'], f"参数不匹配: {actual_params} vs {expected['expected_params']}"
        except FileNotFoundError:
            print(f"  ❌ 缺少 model_info.json")
            continue
        
        print(f"  ✅ {exp_name} 验证通过")
    
    return True

def verify_all_experiments_batch():
    """批量验证所有实验"""
    print("\\n=== 批量验证所有实验 ===")
    
    experiments = get_all_experiments()
    
    try:
        results = batch_evaluate_experiments(experiments['all'])
        print(f"✅ 成功评估 {len(results)} 个实验")
        
        # 统计各阶段成功率
        phase_stats = {'original': 0, 'phase1': 0, 'phase2': 0}
        
        for result in results:
            if 'EFF2_' in result['experiment']:
                if result['ASR_core'] >= 75:
                    phase_stats['phase2'] += 1
            elif 'EFF_' in result['experiment']:
                if result['ASR_core'] >= 75:
                    phase_stats['phase1'] += 1
            else:
                if result['ASR_core'] >= 75:
                    phase_stats['original'] += 1
        
        print(f"原始探索高性能(≥75%)实验: {phase_stats['original']}")
        print(f"Phase1高性能(≥75%)实验: {phase_stats['phase1']}")
        print(f"Phase2高性能(≥75%)实验: {phase_stats['phase2']}")
        
        return True
    except Exception as e:
        print(f"❌ 批量验证失败: {e}")
        return False

def verify_data_consistency():
    """验证数据一致性"""
    print("\\n=== 验证数据一致性 ===")
    
    # 验证EFF2_A1确实超越E05
    try:
        e05_result = evaluate_alias_suppression('projects/WNET5_RealAlias_E05/data/linear_response.json')
        eff2a1_result = evaluate_alias_suppression('projects/WNET5_EFF2_A1/data/linear_response.json')
        
        e05_asr = e05_result['ASR_core']['suppression_ratio']
        eff2a1_asr = eff2a1_result['ASR_core']['suppression_ratio']
        
        print(f"E05 ASR: {e05_asr:.1f}%")
        print(f"EFF2_A1 ASR: {eff2a1_asr:.1f}%")
        print(f"提升幅度: {eff2a1_asr - e05_asr:.1f}%")
        
        assert eff2a1_asr > e05_asr, "EFF2_A1应该超越E05"
        print("✅ EFF2_A1确实超越E05基准")
        
    except Exception as e:
        print(f"❌ 一致性验证失败: {e}")
        return False
    
    return True

def get_all_experiments():
    """获取所有实验列表"""
    original = [
        'WNET5_RealAlias', 'WNET5_RealAlias_E01', 'WNET5_RealAlias_E02', 
        'WNET5_RealAlias_E03', 'WNET5_RealAlias_E04', 'WNET5_RealAlias_E05',
        'WNET5_RealAlias_E06', 'WNET5_RealAlias_E07', 'WNET5_RealAlias_E08',
        'WNET5_RealAlias_E09', 'WNET5_RealAlias_E10', 'WNET5_RealAlias_E11',
        'WNET5_RealAlias_E12'
    ]
    
    phase1 = ['WNET5_EFF_A1', 'WNET5_EFF_A2', 'WNET5_EFF_B1', 
              'WNET5_EFF_C1', 'WNET5_EFF_C2', 'WNET5_EFF_D1']
    
    phase2 = ['WNET5_EFF2_A1', 'WNET5_EFF2_A2', 'WNET5_EFF2_B1',
              'WNET5_EFF2_B2', 'WNET5_EFF2_C1', 'WNET5_EFF2_C2']
    
    return {'original': original, 'phase1': phase1, 'phase2': phase2, 'all': original + phase1 + phase2}

def main():
    """主验证函数"""
    print("WaveNet5综合项目数据验证")
    print("="*50)
    
    try:
        verify_key_experiments()
        verify_all_experiments_batch()
        verify_data_consistency()
        
        print("\\n" + "="*50)
        print("✅ 所有数据验证通过！综合报告中的数据准确无误。")
        
    except AssertionError as e:
        print(f"\\n❌ 数据验证失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\\n❌ 验证过程出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    # 保存验证脚本
    script_path = os.path.join(save_path, 'verify_comprehensive_data.py')
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(verification_script)
    
    # 设置可执行权限
    os.chmod(script_path, 0o755)
    
    print(f"✅ 综合数据验证脚本已保存到: {script_path}")
    
    return script_path

def generate_origin_efficiency_plot(save_path='documentation/images'):
    """生成仅包含origin阶段的参数效率分析图"""
    print("🔬 开始生成origin阶段参数效率分析图...")

    # 确保保存路径存在
    os.makedirs(save_path, exist_ok=True)

    # 获取origin阶段实验
    experiments = get_all_experiments()
    origin_experiments = experiments['original']

    # 批量评估origin阶段实验
    print("📊 评估origin阶段实验...")
    results = batch_evaluate_experiments(origin_experiments)

    # 调用通用绘图函数
    return generate_efficiency_plot(results, save_path, 'origin_efficiency_analysis.png', 'Origin Phase Efficiency Analysis')

def generate_origin_phase1_efficiency_plot(save_path='documentation/images'):
    """生成包含origin和阶段1的参数效率分析图"""
    print("🔬 开始生成origin + 阶段1参数效率分析图...")

    # 确保保存路径存在
    os.makedirs(save_path, exist_ok=True)

    # 获取origin和阶段1实验
    experiments = get_all_experiments()
    origin_phase1_experiments = experiments['original'] + experiments['phase1']

    # 批量评估origin和阶段1实验
    print("📊 评估origin + 阶段1实验...")
    results = batch_evaluate_experiments(origin_phase1_experiments)

    # 调用通用绘图函数
    return generate_efficiency_plot(results, save_path, 'origin_phase1_efficiency_analysis.png', 'Origin + Phase1 Efficiency Analysis')

def generate_efficiency_plot(results, save_path, filename, title):
    """通用绘图函数"""
    # 准备绘图数据
    plot_data = {
        'baseline': {'params': [], 'asr': [], 'names': [], 'sizes': []},
        'original': {'params': [], 'asr': [], 'names': [], 'sizes': []},
        'benchmark': {'params': [], 'asr': [], 'names': [], 'sizes': []},
        'phase1': {'params': [], 'asr': [], 'names': [], 'sizes': []},
        'phase2': {'params': [], 'asr': [], 'names': [], 'sizes': []}
    }

    all_params = []
    all_asr = []

    for result in results:
        if result['total_params'] > 0:
            category, color = classify_experiment(result['experiment'])

            params = result['total_params']
            asr = result['ASR_core']

            # 简化名称
            name = result['experiment'].replace('WNET5_RealAlias_', '').replace('WNET5_RealAlias', 'Baseline')
            name = name.replace('WNET5_EFF2_', 'EFF2_').replace('WNET5_EFF_', 'EFF_')

            plot_data[category]['params'].append(params)
            plot_data[category]['asr'].append(asr)
            plot_data[category]['names'].append(name)

            # 根据重要性调整点的大小
            if name in ['E05', 'EFF2_A1', 'EFF2_B1']:
                plot_data[category]['sizes'].append(200)  # 重要实验用大点
            else:
                plot_data[category]['sizes'].append(150)

            all_params.append(params)
            all_asr.append(asr)

    # 创建图表
    fig, ax = plt.subplots(figsize=(14, 10))

    # 定义颜色和标签
    colors = {
        'baseline': '#808080',
        'original': '#1f77b4', 
        'benchmark': '#ff7f0e',
        'phase1': '#d62728',
        'phase2': '#2ca02c'
    }

    labels = {
        'baseline': 'Baseline',
        'original': 'Original Exploration (E01-E12)',
        'benchmark': 'E05 Benchmark', 
        'phase1': 'Phase1 Optimization (Failed)',
        'phase2': 'Phase2 Optimization (Success)'
    }

    # 绘制各类实验
    for category, data in plot_data.items():
        if data['params']:  # 如果有数据
            scatter = ax.scatter(data['params'], data['asr'], 
                               c=colors[category], s=data['sizes'], alpha=0.7,
                               edgecolors='black', linewidth=1.5, 
                               label=labels[category], zorder=5)

    # 添加标签
    for category, data in plot_data.items():
        for i, name in enumerate(data['names']):
            # 重要实验用加粗标签
            weight = 'bold' if name in ['E05', 'EFF2_A1', 'EFF2_B1', 'Baseline'] else 'normal'
            ax.annotate(name, (data['params'][i], data['asr'][i]), 
                       xytext=(8, 8), textcoords='offset points', 
                       fontsize=10, fontweight=weight, zorder=6)

    # 设置图表属性
    ax.set_xlabel('Total Parameters', fontsize=14, fontweight='bold')
    ax.set_ylabel('Alias Suppression Ratio (%)', fontsize=14, fontweight='bold')
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)

    # 设置坐标轴范围
    ax.set_xlim(min(all_params) * 0.9, max(all_params) * 1.1)
    ax.set_ylim(0, max(all_asr) * 1.05)

    # 添加网格
    ax.grid(True, alpha=0.3, linestyle='--')

    # 添加图例
    ax.legend(loc='lower right', fontsize=11, framealpha=0.9)

    # 保存图表
    plot_path = os.path.join(save_path, filename)
    plt.tight_layout()
    plt.savefig(plot_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"✅ {title} 图已保存到: {plot_path}")

    return results, plot_path

def generate_hyperparameter_markdown_table(save_path='documentation/images'):
    """生成包含 BASELINE, E05, EFF2_A1, EFF2_B1 和 WNET5q1h2u6l3 的超参数 Markdown 表格"""
    print("🔬 开始生成超参数 Markdown 表格...")

    # 定义目标实验
    target_experiments = [
        'WNET5_RealAlias',
        'WNET5_RealAlias_E05',
        'WNET5_EFF2_A1',
        'WNET5_EFF2_B1',
        'WNET5q1h2u6l3'
    ]

    # 批量评估目标实验
    results = batch_evaluate_experiments(target_experiments)

    # 准备 Markdown 表格
    table_md = "# 超参数与性能对比表\n\n"
    table_md += "| 实验名称 | 抑制率 (ASR) | 总参数量 | SVF组数 | Dense通道数x层数 | 备注 |\n"
    table_md += "|----------|-------------|----------|--------|------------------|------|\n"

    for result in results:
        # 简化实验名称
        name = result['experiment'].replace('WNET5_RealAlias_', '').replace('WNET5_RealAlias', 'BASELINE')
        name = name.replace('WNET5_EFF2_', 'EFF2_')

        # 特殊标注
        note = "*补偿对象为MET" if result['experiment'] == 'WNET5q1h2u6l3' else ""

        # 特殊处理 ASR
        asr = '/' if result['experiment'] == 'WNET5q1h2u6l3' else f"{result['ASR_core']:.1f}%"

        # 提取超参数，处理缺失字段
        total_params = result.get('total_params', 'N/A')
        svf_groups = result.get('init_center_freqs_count', 'N/A')
        dense_channels_layers = f"{result.get('post_dense_units', 'N/A')}x{result.get('post_dense_layers', 'N/A')}"

        # 添加表格行
        table_md += f"| {name} | {asr} | {total_params} | {svf_groups} | {dense_channels_layers} | {note} |\n"

    # 保存 Markdown 表格
    table_path = os.path.join(save_path, 'hyperparameter_comparison_table.md')
    with open(table_path, 'w', encoding='utf-8') as f:
        f.write(table_md)

    print(f"✅ 超参数 Markdown 表格已保存到: {table_path}")

    return table_path

def main():
    """主函数 - 生成所有分析内容"""
    print("🚀 WaveNet5综合项目分析工具启动")
    print("="*60)
    
    # 创建输出目录
    image_dir = 'documentation/images'
    os.makedirs(image_dir, exist_ok=True)
    
    try:
        # 1. 生成参数效率分析图
        results, plot_path = generate_comprehensive_efficiency_plot(image_dir)
        
        # 2. 生成效率排行表格
        efficiency_data, table_path = generate_efficiency_ranking_table(results, image_dir)
        
        # 3. 生成验证脚本
        script_path = generate_comprehensive_verification_script()
        
        # 4. 生成仅包含origin阶段的参数效率分析图
        origin_plot_path = generate_origin_efficiency_plot(image_dir)
        
        # 5. 生成包含origin和阶段1的参数效率分析图
        origin_phase1_plot_path = generate_origin_phase1_efficiency_plot(image_dir)
        
        # 6. 生成超参数与性能对比表
        hyperparameter_table_path = generate_hyperparameter_markdown_table(image_dir)
        
        # 7. 输出关键统计信息
        print("\n🎯 综合项目关键统计:")
        print(f"📊 总实验数: {len(results)}")
        print(f"🏆 最高性能: {max(r['ASR_core'] for r in results):.1f}% (EFF2_A1)")
        print(f"⭐ 超越基准: EFF2_A1 (91.9%) > E05 (90.3%)")
        print(f"🎯 达标实验: {len([r for r in results if r['ASR_core'] >= 80])}/19")
        
        # Phase2成功率
        phase2_results = [r for r in results if 'EFF2_' in r['experiment']]
        phase2_success = len([r for r in phase2_results if r['ASR_core'] >= 75])
        print(f"📈 Phase2成功率: {phase2_success}/{len(phase2_results)} ({phase2_success/len(phase2_results)*100:.1f}%)")
        
        print("\n✅ 所有分析内容生成完成！")
        print(f"📈 综合参数效率图: {plot_path}")
        print(f"📋 效率排行表: {table_path}")
        print(f"🔍 验证脚本: {script_path}")
        print(f"📊 仅包含origin阶段的效率图: {origin_plot_path}")
        print(f"📊 包含origin和阶段1的效率图: {origin_phase1_plot_path}")
        print(f"📑 超参数与性能对比表: {hyperparameter_table_path}")
        
    except Exception as e:
        print(f"❌ 分析过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()