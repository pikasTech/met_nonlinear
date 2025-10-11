#!/usr/bin/env python3
"""
WaveNet5效率优化Phase2实验配置生成器
基于Phase1最佳结果(EFF_B1: 60.8% ASR)的精细调参策略
"""

import json
import os
import copy

def load_base_config():
    """读取E05基准配置"""
    base_path = '/home/ubuntu/met_nonlinear/projects/WNET5_RealAlias_E05/config.json'
    with open(base_path, 'r') as f:
        return json.load(f)

def deep_update(base_dict, update_dict):
    """深度更新字典"""
    result = copy.deepcopy(base_dict)
    for key, value in update_dict.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_update(result[key], value)
        else:
            result[key] = value
    return result

def generate_phase2_configs():
    """生成Phase2精细调参实验配置"""
    
    # 读取E05基准配置
    base_config = load_base_config()
    print(f"✓ 读取E05基准配置作为Phase2基础")
    print(f"Phase1教训: 所有实验均未达到80% ASR目标")
    print(f"调整目标: 85% ASR with 7,000-8,000参数\n")
    
    # Phase2实验配置定义 - 基于保守策略
    phase2_experiments = {
        'EFF2_A1': {
            'description': '保守Dense微调',
            'expected_params': '~8,200',
            'expected_asr': '85-89%',
            'strategy': '仅减少12.5%单元数，验证E05稳健性',
            'changes': {
                'model_subcfg': {
                    'post_dense_units': 14  # 16 → 14
                }
            }
        },
        
        'EFF2_A2': {
            'description': '中度Dense调整',
            'expected_params': '~7,700',
            'expected_asr': '78-82%',
            'strategy': '减少25%单元数，探索边界',
            'changes': {
                'model_subcfg': {
                    'post_dense_units': 12  # 16 → 12
                }
            }
        },
        
        'EFF2_B1': {
            'description': '5个IIR探索',
            'expected_params': '~7,200',
            'expected_asr': '72-82%',
            'strategy': '寻找6和4之间的平衡点',
            'changes': {
                'kernal_units': 5,
                'model_subcfg': {
                    'init_center_freqs': [10, 30, 60, 100, 160],
                    'init_quality_factors': [1.5, 2.0, 2.5, 3.5, 4.5]
                }
            }
        },
        
        'EFF2_B2': {
            'description': 'Dense层数微调',
            'expected_params': '~8,100',
            'expected_asr': '80-84%',
            'strategy': '3层→2层但增加宽度补偿',
            'changes': {
                'model_subcfg': {
                    'post_dense_layers': 2,
                    'post_dense_units': 20
                }
            }
        },
        
        'EFF2_C1': {
            'description': '训练策略优化',
            'expected_params': '~7,950',
            'expected_asr': '82-88%',
            'strategy': '延长训练+细化学习率补偿轻微削减',
            'changes': {
                'epoch_train': 40000,
                'learning_rate': 0.015,
                'auto_lr_decay_steps': 1200,
                'model_subcfg': {
                    'post_dense_units': 13
                }
            }
        },
        
        'EFF2_C2': {
            'description': 'EFF_B1改进版',
            'expected_params': '~4,600',
            'expected_asr': '62-68%',
            'strategy': '基于60.8%基线优化频率分布',
            'changes': {
                'kernal_units': 4,
                'model_subcfg': {
                    'init_center_freqs': [10, 35, 75, 150],
                    'init_quality_factors': [1.5, 2.0, 3.0, 4.0],
                    'post_dense_units': 18
                }
            }
        }
    }
    
    # 生成配置文件
    results = {}
    for exp_name, exp_config in phase2_experiments.items():
        # 深度更新配置
        exp_full_config = deep_update(base_config, exp_config['changes'])
        
        # 保存配置文件
        output_path = f'/home/ubuntu/met_nonlinear/projects/WNET5_{exp_name}/config.json'
        
        # 创建目录
        os.makedirs(f'/home/ubuntu/met_nonlinear/projects/WNET5_{exp_name}', exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(exp_full_config, f, indent=4)
        
        results[exp_name] = {
            'path': output_path,
            'description': exp_config['description'],
            'expected_params': exp_config['expected_params'],
            'expected_asr': exp_config['expected_asr'],
            'strategy': exp_config['strategy'],
            'kernal_units': exp_full_config['kernal_units'],
            'dense_layers': exp_full_config['model_subcfg']['post_dense_layers'],
            'dense_units': exp_full_config['model_subcfg']['post_dense_units'],
            'learning_rate': exp_full_config.get('learning_rate', 0.02),
            'epoch_train': exp_full_config.get('epoch_train', 30000)
        }
        
        print(f"✓ 生成 {exp_name}: {exp_config['description']}")
        print(f"  - 路径: {output_path}")
        print(f"  - IIR滤波器: {exp_full_config['kernal_units']}个")
        print(f"  - Dense配置: {exp_full_config['model_subcfg']['post_dense_layers']}层×{exp_full_config['model_subcfg']['post_dense_units']}单元")
        print(f"  - 预期ASR: {exp_config['expected_asr']}")
        print(f"  - 策略: {exp_config['strategy']}")
        print()
    
    return results

def generate_summary_table(results):
    """生成Phase2实验汇总表"""
    print("=" * 120)
    print("Phase2精细调参实验配置汇总表")
    print("=" * 120)
    print(f"{'实验名':<12} {'描述':<20} {'IIR':<5} {'Dense':<10} {'预期ASR':<10} {'预期参数':<10} {'策略':<30}")
    print("-" * 120)
    
    # 定义优先级
    priority_order = ['EFF2_A1', 'EFF2_A2', 'EFF2_B1', 'EFF2_B2', 'EFF2_C1', 'EFF2_C2']
    
    for exp_name in priority_order:
        if exp_name in results:
            config = results[exp_name]
            dense_config = f"{config['dense_layers']}×{config['dense_units']}"
            print(f"{exp_name:<12} {config['description']:<20} {config['kernal_units']:<5} {dense_config:<10} "
                  f"{config['expected_asr']:<10} {config['expected_params']:<10} {config['strategy']:<30}")
    
    print("=" * 120)
    print(f"E05基准: 90.3% ASR (6个IIR + 3×16Dense，8,641参数)")
    print(f"Phase1最佳: EFF_B1 = 60.8% ASR (损失29.5%)")
    print(f"Phase2目标: 85% ASR with 7,000-8,000参数")
    print("=" * 120)

def generate_execution_commands(results):
    """生成执行命令"""
    print("\n🚀 Phase2实验执行指南")
    print("="*60)
    
    print("\n📋 第一批次（最高优先级）")
    print("```bash")
    print("# 验证E05稳健性和IIR平衡点")
    print("python cli.py -p WNET5_EFF2_A1  # 保守Dense微调")
    print("python cli.py -p WNET5_EFF2_B1  # 5个IIR探索")
    print("```")
    
    print("\n📋 第二批次（根据第一批结果决定）")
    print("```bash")
    print("# 如果A1显示有空间，继续探索")
    print("python cli.py -p WNET5_EFF2_A2  # 中度Dense调整")
    print("python cli.py -p WNET5_EFF2_B2  # Dense层数微调")
    print("```")
    
    print("\n📋 第三批次（精细优化）")
    print("```bash")
    print("# 训练策略和基线优化")
    print("python cli.py -p WNET5_EFF2_C1  # 训练策略优化")
    print("python cli.py -p WNET5_EFF2_C2  # EFF_B1改进版")
    print("```")
    
    print("\n🎯 决策逻辑")
    print("- 如果EFF2_A1 > 85% ASR → 达到调整后目标")
    print("- 如果EFF2_B1 > 80% ASR → 找到理想平衡点")
    print("- 如果两者都 < 82% → 承认E05已接近最优")

def main():
    """主函数"""
    print("WaveNet5效率优化Phase2配置生成器")
    print("基于E05的保守优化策略\n")
    
    try:
        # 生成Phase2实验配置
        results = generate_phase2_configs()
        
        # 生成汇总表
        generate_summary_table(results)
        
        # 生成执行命令
        generate_execution_commands(results)
        
        print("\n🎉 Phase2实验配置生成完成！")
        print("\n💡 核心策略:")
        print("1. 基于E05进行保守微调")
        print("2. 调整目标: 85% ASR with 7,000-8,000参数")
        print("3. 承认E05可能已接近最优")
        print("4. 科学验证架构的优化边界")
        
    except Exception as e:
        print(f"❌ 配置生成失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())