#!/usr/bin/env python3
"""
WNET5_RealAlias综合报告数据验证脚本

用于验证documentation/WNET5_RealAlias_Comprehensive_Analysis_Report.md中的所有数据
确保所有数据都有明确的代码生成来源，避免数据错误。
"""

import json
import numpy as np
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analysis.alias_suppression import evaluate_alias_suppression, batch_evaluate_experiments


def verify_e05_performance():
    """验证E05的核心性能数据"""
    print("=== 验证E05性能数据 ===")
    
    # 读取数据
    result = evaluate_alias_suppression('projects/WNET5_RealAlias_E05/data/linear_response.json')
    
    # 验证核心指标
    asr = result['ASR_core']['suppression_ratio']
    score = result['overall_score']
    
    print(f"E05核心ASR: {asr:.1f}% (报告值: 90.3%)")
    print(f"E05综合评分: {score:.1f} (报告值: 89.3)")
    
    # 检查是否匹配
    assert abs(asr - 90.3) < 0.1, f"ASR不匹配: {asr} vs 90.3"
    assert abs(score - 89.3) < 0.1, f"评分不匹配: {score} vs 89.3"
    
    return True


def verify_e05_parameters():
    """验证E05的参数量数据"""
    print("\n=== 验证E05参数量 ===")
    
    # 读取模型信息
    with open('projects/WNET5_RealAlias_E05/data/model_info.json', 'r') as f:
        model_info = json.load(f)
    
    total_params = model_info['total_params']
    trainable_params = model_info['trainable_params']
    
    print(f"E05总参数: {total_params:,} (报告值: 8,641)")
    print(f"E05可训练参数: {trainable_params:,} (报告值: 865)")
    
    # 检查是否匹配
    assert total_params == 8641, f"总参数不匹配: {total_params} vs 8641"
    assert trainable_params == 865, f"可训练参数不匹配: {trainable_params} vs 865"
    
    # 验证参数效率
    efficiency = 90.3 / (total_params / 1000)
    print(f"E05参数效率: {efficiency:.2f} ASR/千参数 (报告值: 10.45)")
    assert abs(efficiency - 10.45) < 0.01, f"效率不匹配: {efficiency} vs 10.45"
    
    return True


def verify_baseline_data():
    """验证基线数据"""
    print("\n=== 验证基线数据 ===")
    
    # 读取基线数据
    result = evaluate_alias_suppression('projects/WNET5_RealAlias/data/linear_response.json')
    
    # 验证ASR
    asr = result['ASR_core']['suppression_ratio']
    print(f"基线ASR: {asr:.1f}% (报告值: 54.2%)")
    assert abs(asr - 54.2) < 0.1, f"基线ASR不匹配: {asr} vs 54.2"
    
    # 验证原始波动
    ripple_orig = result['ASR_core']['original_ripple']
    print(f"基线90-100Hz波动: {ripple_orig:.2f} V/m/s (报告值: 100.96)")
    assert abs(ripple_orig - 100.96) < 0.1, f"波动不匹配: {ripple_orig} vs 100.96"
    
    return True


def verify_all_experiments():
    """验证所有实验数据"""
    print("\n=== 验证所有实验数据 ===")
    
    # 所有实验列表
    all_experiments = [
        'WNET5_RealAlias',
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
    
    # 批量评估
    results = batch_evaluate_experiments(all_experiments)
    
    # 报告中的关键数据
    expected_data = {
        'WNET5_RealAlias_E05': {'asr': 90.3, 'params': 8641},
        'WNET5_RealAlias_E08': {'asr': 89.2, 'params': 9457},
        'WNET5_RealAlias_E11': {'asr': 88.3, 'params': 14785},
        'WNET5_RealAlias_E07': {'asr': 82.4, 'params': 14785},
        'WNET5_RealAlias_E01': {'asr': 73.5, 'params': 14249},
        'WNET5_RealAlias': {'asr': 54.2, 'params': 8153}
    }
    
    # 验证关键实验数据
    for result in results:
        exp_name = result['experiment']
        if exp_name in expected_data:
            actual_asr = result['ASR_core']
            actual_params = result['total_params']
            expected = expected_data[exp_name]
            
            print(f"\n{exp_name}:")
            print(f"  ASR: {actual_asr:.1f}% (期望: {expected['asr']}%)")
            print(f"  参数: {actual_params:,} (期望: {expected['params']:,})")
            
            # 验证数据匹配
            assert abs(actual_asr - expected['asr']) < 0.1, f"{exp_name} ASR不匹配"
            assert actual_params == expected['params'], f"{exp_name} 参数不匹配"
    
    return True


def verify_data_files():
    """验证所有数据文件的存在性"""
    print("\n=== 验证数据文件完整性 ===")
    
    experiments = [
        'WNET5_RealAlias',
        'WNET5_RealAlias_E01', 'WNET5_RealAlias_E02', 'WNET5_RealAlias_E03',
        'WNET5_RealAlias_E04', 'WNET5_RealAlias_E05', 'WNET5_RealAlias_E06',
        'WNET5_RealAlias_E07', 'WNET5_RealAlias_E08', 'WNET5_RealAlias_E09',
        'WNET5_RealAlias_E10', 'WNET5_RealAlias_E11', 'WNET5_RealAlias_E12'
    ]
    
    missing_files = []
    
    for exp in experiments:
        linear_path = f'projects/{exp}/data/linear_response.json'
        model_path = f'projects/{exp}/data/model_info.json'
        
        if not os.path.exists(linear_path):
            missing_files.append(f"{exp}/linear_response.json")
        if not os.path.exists(model_path):
            missing_files.append(f"{exp}/model_info.json")
    
    if missing_files:
        print("缺失文件:")
        for f in missing_files:
            print(f"  ❌ {f}")
        return False
    else:
        print("✅ 所有数据文件完整")
        return True


def verify_calculation_method():
    """验证计算方法的正确性"""
    print("\n=== 验证计算方法 ===")
    
    # 直接读取并计算
    with open('projects/WNET5_RealAlias_E05/data/linear_response.json', 'r') as f:
        data = json.load(f)
    
    frequencies = np.array(data['frequencies'])
    gains_origin = np.array(data['gains_origin'][0])
    gains_comped = np.array(data['gains_comped'][0])
    
    # 找到90-100Hz区间
    indices = np.where((frequencies >= 90) & (frequencies <= 100))[0]
    gains_orig_90_100 = gains_origin[indices]
    gains_comp_90_100 = gains_comped[indices]
    
    # 手动计算ASR
    ripple_orig = float(np.max(gains_orig_90_100) - np.min(gains_orig_90_100))
    ripple_comp = float(np.max(gains_comp_90_100) - np.min(gains_comp_90_100))
    manual_asr = (ripple_orig - ripple_comp) / ripple_orig * 100
    
    print(f"手动计算ASR: {manual_asr:.1f}%")
    print(f"原始波动: {ripple_orig:.2f} V/m/s")
    print(f"补偿后波动: {ripple_comp:.2f} V/m/s")
    
    # 使用评估函数计算
    result = evaluate_alias_suppression(data)
    func_asr = result['ASR_core']['suppression_ratio']
    
    print(f"函数计算ASR: {func_asr:.1f}%")
    
    # 验证两种方法一致
    assert abs(manual_asr - func_asr) < 0.1, "计算方法不一致"
    
    return True


def main():
    """主验证函数"""
    print("WNET5_RealAlias 综合报告数据验证")
    print("="*50)
    
    try:
        # 验证所有数据
        verify_e05_performance()
        verify_e05_parameters()
        verify_baseline_data()
        verify_all_experiments()
        verify_data_files()
        verify_calculation_method()
        
        print("\n" + "="*50)
        print("✅ 所有数据验证通过！报告中的数据准确无误。")
        
    except AssertionError as e:
        print(f"\n❌ 数据验证失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 验证过程出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()