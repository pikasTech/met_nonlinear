#!/usr/bin/env python3
"""
统计计算工具模块

提供偏置误差分析的统计计算功能。
"""

import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from scipy import stats


def calculate_improvement_stats(baseline_errors: List[float], 
                               compensated_errors: List[float]) -> Dict[str, float]:
    """
    计算改进统计指标
    
    Args:
        baseline_errors: 基准误差列表
        compensated_errors: 补偿后误差列表
        
    Returns:
        包含各种改进指标的字典
    """
    baseline_errors = np.array(baseline_errors)
    compensated_errors = np.array(compensated_errors)
    
    # 计算绝对值
    baseline_abs = np.abs(baseline_errors)
    compensated_abs = np.abs(compensated_errors)
    
    # 计算均值改进
    baseline_mean = np.mean(baseline_abs)
    compensated_mean = np.mean(compensated_abs)
    mean_improvement = (baseline_mean - compensated_mean) / baseline_mean * 100 if baseline_mean != 0 else 0
    
    # 计算标准差改进
    baseline_std = np.std(baseline_abs)
    compensated_std = np.std(compensated_abs)
    std_improvement = (baseline_std - compensated_std) / baseline_std * 100 if baseline_std != 0 else 0
    
    # 计算最大值改进
    baseline_max = np.max(baseline_abs)
    compensated_max = np.max(compensated_abs)
    max_improvement = (baseline_max - compensated_max) / baseline_max * 100 if baseline_max != 0 else 0
    
    # 计算RMS改进
    baseline_rms = np.sqrt(np.mean(baseline_errors**2))
    compensated_rms = np.sqrt(np.mean(compensated_errors**2))
    rms_improvement = (baseline_rms - compensated_rms) / baseline_rms * 100 if baseline_rms != 0 else 0
    
    return {
        'mean_improvement': mean_improvement,
        'std_improvement': std_improvement,
        'max_improvement': max_improvement,
        'rms_improvement': rms_improvement,
        'baseline_mean': baseline_mean,
        'compensated_mean': compensated_mean,
        'baseline_std': baseline_std,
        'compensated_std': compensated_std,
        'baseline_max': baseline_max,
        'compensated_max': compensated_max,
        'baseline_rms': baseline_rms,
        'compensated_rms': compensated_rms
    }


def perform_statistical_test(baseline_errors: List[float], 
                           compensated_errors: List[float],
                           test_type: str = 'wilcoxon') -> Dict[str, Any]:
    """
    执行统计显著性检验
    
    Args:
        baseline_errors: 基准误差列表
        compensated_errors: 补偿后误差列表
        test_type: 检验类型 ('wilcoxon', 'paired_t', 'mann_whitney')
        
    Returns:
        包含检验结果的字典
    """
    baseline_errors = np.array(baseline_errors)
    compensated_errors = np.array(compensated_errors)
    
    result = {
        'test_type': test_type,
        'sample_size': len(baseline_errors)
    }
    
    if test_type == 'wilcoxon':
        # Wilcoxon符号秩检验（非参数配对检验）
        if len(baseline_errors) == len(compensated_errors):
            statistic, p_value = stats.wilcoxon(baseline_errors, compensated_errors)
            result['statistic'] = statistic
            result['p_value'] = p_value
            result['significant'] = p_value < 0.05
        else:
            result['error'] = '样本大小不匹配'
            
    elif test_type == 'paired_t':
        # 配对t检验
        if len(baseline_errors) == len(compensated_errors):
            statistic, p_value = stats.ttest_rel(baseline_errors, compensated_errors)
            result['statistic'] = statistic
            result['p_value'] = p_value
            result['significant'] = p_value < 0.05
        else:
            result['error'] = '样本大小不匹配'
            
    elif test_type == 'mann_whitney':
        # Mann-Whitney U检验（非参数独立样本检验）
        statistic, p_value = stats.mannwhitneyu(baseline_errors, compensated_errors)
        result['statistic'] = statistic
        result['p_value'] = p_value
        result['significant'] = p_value < 0.05
        
    return result


def calculate_confidence_interval(data: List[float], 
                                confidence_level: float = 0.95) -> Tuple[float, float]:
    """
    计算置信区间
    
    Args:
        data: 数据列表
        confidence_level: 置信水平（默认95%）
        
    Returns:
        (下限, 上限)
    """
    data = np.array(data)
    mean = np.mean(data)
    sem = stats.sem(data)  # 标准误差
    
    # 计算置信区间
    interval = stats.t.interval(confidence_level, 
                               len(data) - 1, 
                               loc=mean, 
                               scale=sem)
    
    return interval


def calculate_effect_size(baseline_errors: List[float], 
                         compensated_errors: List[float]) -> Dict[str, float]:
    """
    计算效应量（Cohen's d）
    
    Args:
        baseline_errors: 基准误差列表
        compensated_errors: 补偿后误差列表
        
    Returns:
        包含效应量指标的字典
    """
    baseline_errors = np.array(baseline_errors)
    compensated_errors = np.array(compensated_errors)
    
    # 计算均值差
    mean_diff = np.mean(baseline_errors) - np.mean(compensated_errors)
    
    # 计算合并标准差
    n1, n2 = len(baseline_errors), len(compensated_errors)
    var1, var2 = np.var(baseline_errors, ddof=1), np.var(compensated_errors, ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    
    # 计算Cohen's d
    cohens_d = mean_diff / pooled_std if pooled_std != 0 else 0
    
    # 解释效应量大小
    if abs(cohens_d) < 0.2:
        interpretation = "微小"
    elif abs(cohens_d) < 0.5:
        interpretation = "小"
    elif abs(cohens_d) < 0.8:
        interpretation = "中等"
    else:
        interpretation = "大"
    
    return {
        'cohens_d': cohens_d,
        'interpretation': interpretation,
        'mean_difference': mean_diff,
        'pooled_std': pooled_std
    }


def generate_statistics_summary(comparison_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    生成完整的统计摘要
    
    Args:
        comparison_data: 比较数据字典
        
    Returns:
        包含完整统计摘要的字典
    """
    baseline = comparison_data['baseline']
    compensated = comparison_data['compensated']
    
    # 收集所有误差值
    baseline_all_errors = []
    compensated_all_errors = []
    
    for layer_idx in baseline['layers']:
        layer_baseline = baseline['layers'][layer_idx]
        layer_compensated = compensated['layers'][layer_idx]
        
        for ch in layer_baseline['bias_errors']:
            baseline_all_errors.append(ch['bias_error'])
        for ch in layer_compensated['bias_errors']:
            compensated_all_errors.append(ch['bias_error'])
    
    # 计算整体统计
    overall_stats = calculate_improvement_stats(baseline_all_errors, compensated_all_errors)
    
    # 执行统计检验
    significance_test = perform_statistical_test(baseline_all_errors, compensated_all_errors)
    
    # 计算效应量
    effect_size = calculate_effect_size(baseline_all_errors, compensated_all_errors)
    
    # 逐层统计
    layer_stats = {}
    for layer_idx in baseline['layers']:
        layer_baseline = baseline['layers'][layer_idx]
        layer_compensated = compensated['layers'][layer_idx]
        
        baseline_errors = [ch['bias_error'] for ch in layer_baseline['bias_errors']]
        compensated_errors = [ch['bias_error'] for ch in layer_compensated['bias_errors']]
        
        layer_stats[layer_idx] = {
            'improvement': calculate_improvement_stats(baseline_errors, compensated_errors),
            'baseline_summary': layer_baseline['summary'],
            'compensated_summary': layer_compensated['summary']
        }
    
    return {
        'overall': overall_stats,
        'significance': significance_test,
        'effect_size': effect_size,
        'layer_statistics': layer_stats,
        'sample_info': {
            'total_channels': len(baseline_all_errors),
            'layers': len(baseline['layers'])
        }
    }


def format_statistics_table(stats_summary: Dict[str, Any]) -> List[List[str]]:
    """
    格式化统计表格数据
    
    Args:
        stats_summary: 统计摘要字典
        
    Returns:
        表格数据（二维列表）
    """
    table_data = []
    
    # 表头
    headers = ['指标', '基准', '补偿后', '改进 (%)', 'p值']
    table_data.append(headers)
    
    # 整体统计
    overall = stats_summary['overall']
    significance = stats_summary['significance']
    
    # 添加行
    table_data.append([
        '平均偏置误差',
        f"{overall['baseline_mean']:.4f}",
        f"{overall['compensated_mean']:.4f}",
        f"{overall['mean_improvement']:.1f}",
        f"{significance.get('p_value', 'N/A'):.4f}" if 'p_value' in significance else 'N/A'
    ])
    
    table_data.append([
        '标准差',
        f"{overall['baseline_std']:.4f}",
        f"{overall['compensated_std']:.4f}",
        f"{overall['std_improvement']:.1f}",
        '-'
    ])
    
    table_data.append([
        '最大误差',
        f"{overall['baseline_max']:.4f}",
        f"{overall['compensated_max']:.4f}",
        f"{overall['max_improvement']:.1f}",
        '-'
    ])
    
    table_data.append([
        'RMS误差',
        f"{overall['baseline_rms']:.4f}",
        f"{overall['compensated_rms']:.4f}",
        f"{overall['rms_improvement']:.1f}",
        '-'
    ])
    
    # 效应量
    effect = stats_summary['effect_size']
    table_data.append([
        "Cohen's d",
        '-',
        '-',
        f"{effect['cohens_d']:.3f} ({effect['interpretation']})",
        '-'
    ])
    
    return table_data