#!/usr/bin/env python3
"""
WaveNet5效率优化实验结果分析脚本

分析Phase1(EFF_A1到EFF_D1)和Phase2(EFF2_A1到EFF2_C2)的效率优化实验结果
生成与原项目相同格式的综合分析报告
"""

import json
import sys
import os
import numpy as np

# 添加项目路径
sys.path.append('/home/ubuntu/met_nonlinear')
from analysis.alias_suppression import evaluate_alias_suppression, batch_evaluate_experiments

def analyze_efficiency_experiments():
    """分析效率优化实验结果"""
    print("WaveNet5效率优化实验结果分析")
    print("="*60)
    
    # 定义实验列表（包含E05基准和Phase2实验）
    efficiency_experiments = [
        'WNET5_RealAlias_E05',  # 基准
        'WNET5_EFF_A1',         # Phase1: 减少Dense层数 (3→2)
        'WNET5_EFF_A2',         # Phase1: 减少Dense单元数 (16→8)
        'WNET5_EFF_B1',         # Phase1: 4个IIR滤波器
        'WNET5_EFF_C1',         # Phase1: 4 IIR + 8单元 (平衡优化)
        'WNET5_EFF_C2',         # Phase1: 4 IIR + 2层12单元 (结构重组)
        'WNET5_EFF_D1',         # Phase1: 3 IIR + 1层32单元 (极简架构)
        'WNET5_EFF2_A1',        # Phase2: 保守Dense微调 (16→14)
        'WNET5_EFF2_A2',        # Phase2: 中度Dense调整 (16→12)
        'WNET5_EFF2_B1',        # Phase2: 5个IIR探索
        'WNET5_EFF2_B2',        # Phase2: Dense层数微调 (3→2层+宽度)
        'WNET5_EFF2_C1',        # Phase2: 训练策略优化
        'WNET5_EFF2_C2'         # Phase2: EFF_B1改进版
    ]
    
    # 批量评估实验
    results = batch_evaluate_experiments(efficiency_experiments)
    
    # 计算参数效率并扩展结果
    for result in results:
        params = result['total_params']
        asr = result['ASR_core']
        
        # 计算参数效率 (ASR/千参数)
        if params > 0:
            efficiency = asr / (params / 1000)
            result['parameter_efficiency'] = efficiency
        else:
            result['parameter_efficiency'] = 0
            
        # 相对于E05的参数减少百分比
        e05_params = 8641  # E05基准参数量
        param_reduction = (e05_params - params) / e05_params * 100
        result['param_reduction_pct'] = param_reduction
        
        # 相对于E05的ASR变化
        e05_asr = 90.3  # E05基准ASR
        asr_change = asr - e05_asr
        result['asr_change'] = asr_change
        
        # 效率等级判定
        if efficiency >= 15:
            result['efficiency_grade'] = 'S'
        elif efficiency >= 12:
            result['efficiency_grade'] = 'A'
        elif efficiency >= 9:
            result['efficiency_grade'] = 'B'
        elif efficiency >= 6:
            result['efficiency_grade'] = 'C'
        else:
            result['efficiency_grade'] = 'D'
    
    return results

def generate_summary_table(results):
    """生成汇总表格"""
    print("\n" + "="*100)
    print("WaveNet5效率优化实验结果汇总表")
    print("="*100)
    print(f"{'实验名':<15} {'参数量':<8} {'ASR(%)':<8} {'效率':<8} {'等级':<6} {'参数减少':<10} {'ASR变化':<10} {'成功标准':<10}")
    print("-"*100)
    
    for result in results:
        exp_name = result['experiment'].replace('WNET5_', '')
        params = result['total_params']
        asr = result['ASR_core']
        efficiency = result['parameter_efficiency']
        grade = result['efficiency_grade']
        param_reduction = result['param_reduction_pct']
        asr_change = result['asr_change']
        
        # 判断是否达到成功标准
        if asr >= 80 and param_reduction > 0:
            success = "✅达标"
        elif asr >= 78:
            success = "⚠️接近"
        else:
            success = "❌未达标"
        
        print(f"{exp_name:<15} "
              f"{params:<8,} "
              f"{asr:>6.1f}% "
              f"{efficiency:>6.2f} "
              f"{grade:>4} "
              f"{param_reduction:>8.1f}% "
              f"{asr_change:>+8.1f}% "
              f"{success:<10}")
    
    print("="*100)

def analyze_key_findings(results):
    """分析关键发现"""
    print("\n" + "="*60)
    print("关键发现分析")
    print("="*60)
    
    # 找到基准E05
    e05_result = next(r for r in results if 'E05' in r['experiment'])
    
    # 按效率排序（排除E05基准）
    eff_results = [r for r in results if 'EFF' in r['experiment']]
    eff_results_sorted = sorted(eff_results, key=lambda x: x['parameter_efficiency'], reverse=True)
    
    print("\n1. 效率优化成功案例:")
    success_count = 0
    for result in eff_results_sorted:
        if result['ASR_core'] >= 80:
            success_count += 1
            exp_name = result['experiment'].replace('WNET5_EFF_', '')
            print(f"   ✅ {exp_name}: {result['ASR_core']:.1f}% ASR, {result['total_params']:,} 参数, {result['parameter_efficiency']:.2f} 效率")
    
    if success_count == 0:
        print("   ❌ 无实验达到80% ASR目标")
    else:
        print(f"   📊 {success_count}/6 个实验达到目标")
    
    print("\n2. 参数精简效果:")
    best_reduction = max(eff_results, key=lambda x: x['param_reduction_pct'])
    print(f"   最大参数减少: {best_reduction['experiment'].replace('WNET5_EFF_', '')} "
          f"({best_reduction['param_reduction_pct']:.1f}%减少, {best_reduction['ASR_core']:.1f}% ASR)")
    
    print("\n3. 性能保持分析:")
    for threshold in [85, 80, 75]:
        count = sum(1 for r in eff_results if r['ASR_core'] >= threshold)
        print(f"   ASR ≥ {threshold}%: {count}/6 个实验")
    
    print("\n4. 架构洞察:")
    
    # Dense层优化效果
    a_experiments = [r for r in eff_results if '_A' in r['experiment']]
    if a_experiments:
        a_avg_asr = np.mean([r['ASR_core'] for r in a_experiments])
        print(f"   Dense层优化平均ASR: {a_avg_asr:.1f}%")
    
    # IIR优化效果  
    b_experiments = [r for r in eff_results if '_B' in r['experiment']]
    if b_experiments:
        b_avg_asr = np.mean([r['ASR_core'] for r in b_experiments])
        print(f"   IIR滤波器优化平均ASR: {b_avg_asr:.1f}%")
    
    # 综合优化效果
    c_experiments = [r for r in eff_results if '_C' in r['experiment']]
    if c_experiments:
        c_avg_asr = np.mean([r['ASR_core'] for r in c_experiments])
        print(f"   综合优化平均ASR: {c_avg_asr:.1f}%")
    
    # 极简架构效果
    d_experiments = [r for r in eff_results if '_D' in r['experiment']]
    if d_experiments:
        d_avg_asr = np.mean([r['ASR_core'] for r in d_experiments])
        print(f"   极简架构平均ASR: {d_avg_asr:.1f}%")

def generate_detailed_analysis(results):
    """生成详细分析"""
    print("\n" + "="*60)
    print("详细实验分析")
    print("="*60)
    
    # 实验配置描述
    experiment_descriptions = {
        'WNET5_EFF_A1': '减少Dense层数 (3→2)',
        'WNET5_EFF_A2': '减少Dense单元数 (16→8)', 
        'WNET5_EFF_B1': '4个IIR滤波器',
        'WNET5_EFF_C1': '4 IIR + 8单元 (平衡优化)',
        'WNET5_EFF_C2': '4 IIR + 2层12单元 (结构重组)',
        'WNET5_EFF_D1': '3 IIR + 1层32单元 (极简架构)'
    }
    
    eff_results = [r for r in results if 'EFF' in r['experiment']]
    
    for result in eff_results:
        exp_name = result['experiment']
        desc = experiment_descriptions.get(exp_name, '未知配置')
        
        print(f"\n{exp_name.replace('WNET5_EFF_', '')}: {desc}")
        print(f"  参数量: {result['total_params']:,} (减少 {result['param_reduction_pct']:.1f}%)")
        print(f"  ASR性能: {result['ASR_core']:.1f}% (变化 {result['asr_change']:+.1f}%)")
        print(f"  参数效率: {result['parameter_efficiency']:.2f} ASR/千参数 (等级: {result['efficiency_grade']})")
        print(f"  综合评分: {result['overall_score']:.1f}")
        
        # 分析预期情况
        asr = result['ASR_core']
        if asr >= 88:
            situation = "情况B - 性能保持，优化成功"
        elif asr >= 82:
            situation = "情况A - 轻微影响，可接受范围"
        elif asr >= 75:
            situation = "情况C - 性能下降，需权衡考虑"
        else:
            situation = "情况D - 性能严重下降，不推荐"
            
        print(f"  实际结果: {situation}")

def save_results_to_json(results):
    """保存结果到JSON文件"""
    output_file = '/home/ubuntu/met_nonlinear/documentation/20250706-wnet5_efficiency_optimization/efficiency_experiment_results.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n详细结果已保存到: {output_file}")

def main():
    """主函数"""
    try:
        # 分析实验结果
        results = analyze_efficiency_experiments()
        
        # 生成汇总表格
        generate_summary_table(results)
        
        # 分析关键发现
        analyze_key_findings(results)
        
        # 生成详细分析
        generate_detailed_analysis(results)
        
        # 保存结果
        save_results_to_json(results)
        
        print("\n" + "="*60)
        print("✅ 效率优化实验分析完成！")
        print("📄 请查看生成的详细分析和结果文件")
        
    except Exception as e:
        print(f"❌ 分析过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()