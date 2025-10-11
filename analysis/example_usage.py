#!/usr/bin/env python3
"""
假频抑制评估模块使用示例
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from analysis import evaluate_alias_suppression, batch_evaluate_experiments
from analysis.visualization import visualize_alias_suppression, visualize_batch_results


def example_single_evaluation():
    """单个项目评估示例"""
    print("="*60)
    print("示例1: 单个项目评估")
    print("="*60)
    
    # 评估WNET5_RealAlias项目
    data_path = 'projects/WNET5_RealAlias/data/linear_response.json'
    
    try:
        results = evaluate_alias_suppression(data_path)
        
        print(f"\n评估结果:")
        print(f"- 核心区间(90-100Hz)抑制率: {results['ASR_core']['suppression_ratio']:.1f}%")
        print(f"- 扩展区间(85-105Hz)抑制率: {results['ASR_extended']['suppression_ratio']:.1f}%")
        print(f"- 峰值改善率: {results['peak_improvement_ratio']:.1f}%")
        print(f"- 平滑度提升: {results['smoothness_enhancement']:.1f}%")
        print(f"- 综合评分: {results['overall_score']:.1f}")
        print(f"- 等级: {results['grade']}")
        
        # 可视化结果
        print("\n生成可视化图像...")
        visualize_alias_suppression(
            data_path,
            save_path='analysis/output/WNET5_RealAlias_visualization.png',
            show=False
        )
        print("可视化完成!")
        
    except FileNotFoundError:
        print(f"错误: 未找到文件 {data_path}")
    except Exception as e:
        print(f"错误: {e}")


def example_batch_evaluation():
    """批量评估示例"""
    print("\n\n" + "="*60)
    print("示例2: 批量项目评估")
    print("="*60)
    
    # 评估所有WNET5相关项目
    experiments = [
        'WNET5_RealAlias',
        # 可以添加更多实验，例如:
        # 'WNET5_RealAlias_E01',
        # 'WNET5_RealAlias_E02',
    ]
    
    # 过滤存在的实验
    existing_experiments = []
    for exp in experiments:
        if Path(f'projects/{exp}/data/linear_response.json').exists():
            existing_experiments.append(exp)
    
    if existing_experiments:
        print(f"找到 {len(existing_experiments)} 个实验进行评估")
        
        # 执行批量评估
        results = batch_evaluate_experiments(
            existing_experiments,
            output_file='analysis/output/batch_evaluation_results.json'
        )
        
        # 可视化批量结果
        if results:
            print("\n生成批量结果对比图...")
            visualize_batch_results(
                results,
                save_path='analysis/output/batch_comparison.png',
                show=False
            )
            print("批量可视化完成!")
    else:
        print("未找到任何实验数据")


def example_custom_analysis():
    """自定义分析示例"""
    import numpy as np
    
    print("\n\n" + "="*60)
    print("示例3: 自定义分析")
    print("="*60)
    
    # 创建自定义测试数据
    custom_data = {
        'gains_origin': [[200 + 50*np.sin(i/10) for i in range(100)]],
        'gains_comped': [[200 + 10*np.sin(i/10) for i in range(100)]],
        'frequencies': list(range(50, 150)),
        'magnitudes': [1.0],
        'fit_params_origin': [[1, 1, 1]],
        'fit_params_comped': [[1, 1, 1]]
    }
    
    # 评估自定义数据
    results = evaluate_alias_suppression(custom_data)
    
    print(f"\n自定义数据评估结果:")
    print(f"- 核心区间抑制率: {results['ASR_core']['suppression_ratio']:.1f}%")
    print(f"- 综合评分: {results['overall_score']:.1f}")
    print(f"- 等级: {results['grade']}")


def main():
    """主函数"""
    # 创建输出目录
    Path('analysis/output').mkdir(parents=True, exist_ok=True)
    
    print("假频抑制评估模块使用示例")
    print("="*60)
    
    # 运行示例
    example_single_evaluation()
    example_batch_evaluation()
    example_custom_analysis()
    
    print("\n\n所有示例运行完成!")
    print("结果文件保存在 analysis/output/ 目录下")


if __name__ == "__main__":
    main()