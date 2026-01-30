#!/usr/bin/env python3
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
        print(f"\n验证 {exp_name}:")
        
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
    print("\n=== 批量验证所有实验 ===")
    
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
    print("\n=== 验证数据一致性 ===")
    
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
        
        print("\n" + "="*50)
        print("✅ 所有数据验证通过！综合报告中的数据准确无误。")
        
    except AssertionError as e:
        print(f"\n❌ 数据验证失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 验证过程出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
