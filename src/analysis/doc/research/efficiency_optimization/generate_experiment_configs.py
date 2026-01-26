#!/usr/bin/env python3
"""
WaveNet5效率优化实验配置生成器
基于E05配置生成6个效率优化实验的配置文件
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

def generate_experiment_configs():
    """生成所有实验配置"""
    
    # 读取E05基准配置
    base_config = load_base_config()
    print(f"✓ 读取E05基准配置: {base_config['use_model']}")
    print(f"  - 基准参数: kernal_units={base_config['kernal_units']}")
    print(f"  - Dense配置: {base_config['model_subcfg']['post_dense_layers']}层×{base_config['model_subcfg']['post_dense_units']}单元")
    
    # 实验配置定义
    experiments = {
        'EFF_A1': {
            'description': '减少Dense层数 (3→2)',
            'expected_params': '~7,000',
            'changes': {
                'model_subcfg': {
                    'post_dense_layers': 2  # 从3减少到2
                }
            }
        },
        
        'EFF_A2': {
            'description': '减少Dense单元数 (16→8)',
            'expected_params': '~5,500',
            'changes': {
                'model_subcfg': {
                    'post_dense_units': 8  # 从16减少到8
                }
            }
        },
        
        'EFF_B1': {
            'description': '4个IIR滤波器',
            'expected_params': '~6,500',
            'changes': {
                'kernal_units': 4,
                'model_subcfg': {
                    'init_center_freqs': [15, 40, 80, 140],
                    'init_quality_factors': [2.0, 2.5, 3.0, 3.5]
                }
            }
        },
        
        'EFF_C1': {
            'description': '4 IIR + 8单元 (平衡优化)',
            'expected_params': '~4,200',
            'changes': {
                'kernal_units': 4,
                'model_subcfg': {
                    'init_center_freqs': [15, 40, 80, 140],
                    'init_quality_factors': [2.0, 2.5, 3.0, 3.5],
                    'post_dense_units': 8
                }
            }
        },
        
        'EFF_C2': {
            'description': '4 IIR + 2层12单元 (结构重组)',
            'expected_params': '~4,500',
            'changes': {
                'kernal_units': 4,
                'model_subcfg': {
                    'init_center_freqs': [15, 40, 80, 140],
                    'init_quality_factors': [2.0, 2.5, 3.0, 3.5],
                    'post_dense_layers': 2,
                    'post_dense_units': 12
                }
            }
        },
        
        'EFF_D1': {
            'description': '3 IIR + 1层32单元 (极简架构)',
            'expected_params': '~3,000',
            'changes': {
                'kernal_units': 3,
                'model_subcfg': {
                    'init_center_freqs': [20, 60, 120],
                    'init_quality_factors': [2.5, 3.5, 4.5],
                    'post_dense_layers': 1,
                    'post_dense_units': 32
                }
            }
        }
    }
    
    # 生成配置文件
    results = {}
    for exp_name, exp_config in experiments.items():
        # 深度更新配置
        exp_full_config = deep_update(base_config, exp_config['changes'])
        
        # 保存配置文件
        output_path = f'/home/ubuntu/met_nonlinear/projects/WNET5_{exp_name}/config.json'
        with open(output_path, 'w') as f:
            json.dump(exp_full_config, f, indent=4)
        
        results[exp_name] = {
            'path': output_path,
            'description': exp_config['description'],
            'expected_params': exp_config['expected_params'],
            'kernal_units': exp_full_config['kernal_units'],
            'dense_layers': exp_full_config['model_subcfg']['post_dense_layers'],
            'dense_units': exp_full_config['model_subcfg']['post_dense_units']
        }
        
        print(f"✓ 生成 {exp_name}: {exp_config['description']}")
        print(f"  - 路径: {output_path}")
        print(f"  - IIR滤波器: {exp_full_config['kernal_units']}个")
        print(f"  - Dense配置: {exp_full_config['model_subcfg']['post_dense_layers']}层×{exp_full_config['model_subcfg']['post_dense_units']}单元")
        print(f"  - 预计参数量: {exp_config['expected_params']}")
        print()
    
    return results

def generate_summary_table(results):
    """生成实验汇总表"""
    print("=" * 80)
    print("实验配置汇总表")
    print("=" * 80)
    print(f"{'实验名':<10} {'描述':<20} {'IIR':<5} {'Dense':<10} {'预计参数':<10}")
    print("-" * 80)
    
    for exp_name, config in results.items():
        dense_config = f"{config['dense_layers']}×{config['dense_units']}"
        print(f"{exp_name:<10} {config['description']:<20} {config['kernal_units']:<5} {dense_config:<10} {config['expected_params']:<10}")
    
    print("=" * 80)
    print(f"基准E05:    3层×16单元Dense + 6个IIR滤波器 = 8,641参数")
    print(f"目标:       保持ASR≥80%，参数量最小化")
    print("=" * 80)

def main():
    """主函数"""
    print("WaveNet5效率优化实验配置生成器")
    print("基于E05配置生成6个效率优化实验的配置文件\n")
    
    try:
        # 生成实验配置
        results = generate_experiment_configs()
        
        # 生成汇总表
        generate_summary_table(results)
        
        print("\n🎉 所有实验配置生成完成！")
        print("\n下一步:")
        print("1. 运行第一批次实验: EFF_A1, EFF_A2, EFF_B1")
        print("2. 根据结果决定是否继续后续实验")
        print("\n运行命令:")
        print("python cli.py -p WNET5_EFF_A1")
        print("python cli.py -p WNET5_EFF_A2")
        print("python cli.py -p WNET5_EFF_B1")
        
    except Exception as e:
        print(f"❌ 配置生成失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())