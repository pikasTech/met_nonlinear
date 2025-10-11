"""
假频抑制效果评估模块

用于评估神经网络模型对电化学系统中假频（aliasing）的抑制效果。
主要评估指标包括：假频抑制率（ASR）、峰值改善率、平滑度提升等。
"""

import os
import json
import numpy as np


def evaluate_alias_suppression(linear_response_data):
    """
    评估假频抑制效果
    
    参数:
        linear_response_data: 包含gains_origin, gains_comped, frequencies的字典
                            或linear_response.json的文件路径
    
    返回:
        evaluation_results: 包含各项评估指标的字典
    """
    
    # 如果输入是文件路径，加载数据
    if isinstance(linear_response_data, str):
        with open(linear_response_data, 'r') as f:
            linear_response_data = json.load(f)
    
    # 1. 提取数据
    gains_origin = np.array(linear_response_data['gains_origin'][0])
    gains_comped = np.array(linear_response_data['gains_comped'][0])
    frequencies = np.array(linear_response_data['frequencies'])
    
    # 2. 定义评估频段
    freq_bands = {
        'core': (90, 100),      # 核心假频区间
        'extended': (85, 105),  # 扩展评估区间
        'full': (10, 120)       # 完整低频段
    }
    
    # 3. 计算各频段指标
    results = {}
    for band_name, (f_min, f_max) in freq_bands.items():
        # 获取频段内的数据索引
        indices = np.where((frequencies >= f_min) & (frequencies <= f_max))[0]
        
        # 提取频段内的增益值
        gains_orig_band = gains_origin[indices]
        gains_comp_band = gains_comped[indices]
        
        # 计算波动幅度（单位：V/m/s）
        ripple_orig = float(np.max(gains_orig_band) - np.min(gains_orig_band))
        ripple_comp = float(np.max(gains_comp_band) - np.min(gains_comp_band))
        
        # 计算抑制率
        if ripple_orig > 0:
            suppression_ratio = (ripple_orig - ripple_comp) / ripple_orig * 100
        else:
            suppression_ratio = 0.0
        
        # 存储结果
        results[f'ASR_{band_name}'] = {
            'suppression_ratio': suppression_ratio,
            'original_ripple': ripple_orig,
            'compensated_ripple': ripple_comp,
            'frequency_range': (f_min, f_max),
            'max_orig': float(np.max(gains_orig_band)),
            'min_orig': float(np.min(gains_orig_band)),
            'max_comp': float(np.max(gains_comp_band)),
            'min_comp': float(np.min(gains_comp_band))
        }
    
    # 4. 计算平滑度指标（基于一阶导数）
    core_indices = np.where((frequencies >= 90) & (frequencies <= 100))[0]
    smoothness_orig = calculate_smoothness(gains_origin, core_indices)
    smoothness_comp = calculate_smoothness(gains_comped, core_indices)
    
    if smoothness_orig > 0:
        smoothness_enhancement = (smoothness_orig - smoothness_comp) / smoothness_orig * 100
    else:
        smoothness_enhancement = 0.0
    
    results['smoothness_enhancement'] = smoothness_enhancement
    
    # 5. 计算峰值改善率
    peak_improvement = calculate_peak_improvement(
        gains_origin[core_indices], 
        gains_comped[core_indices]
    )
    results['peak_improvement_ratio'] = peak_improvement
    
    # 6. 计算综合评分
    weights = {
        'ASR_core': 0.4,
        'ASR_extended': 0.3,
        'peak_improvement_ratio': 0.2,
        'smoothness_enhancement': 0.1
    }
    
    overall_score = calculate_weighted_score(results, weights)
    results['overall_score'] = overall_score
    
    # 7. 确定评级
    results['grade'] = determine_grade(overall_score)
    
    return results


def calculate_smoothness(gains, indices):
    """
    计算频响曲线的平滑度（基于一阶导数的标准差）
    
    参数:
        gains: 增益数组
        indices: 要计算的索引范围
    
    返回:
        smoothness: 平滑度指标（越小越平滑）
    """
    if len(indices) < 2:
        return 0.0
    
    gains_band = gains[indices]
    # 计算一阶差分
    diff = np.diff(gains_band)
    # 返回差分的标准差作为平滑度指标
    return float(np.std(diff))


def calculate_peak_improvement(gains_orig, gains_comp):
    """
    计算峰值改善率
    
    参数:
        gains_orig: 原始增益数组
        gains_comp: 补偿后增益数组
    
    返回:
        peak_improvement: 峰值改善率（百分比）
    """
    # 计算平均值
    mean_orig = np.mean(gains_orig)
    mean_comp = np.mean(gains_comp)
    
    # 计算最大偏离
    max_deviation_orig = float(np.max(np.abs(gains_orig - mean_orig)))
    max_deviation_comp = float(np.max(np.abs(gains_comp - mean_comp)))
    
    if max_deviation_orig > 0:
        improvement = (max_deviation_orig - max_deviation_comp) / max_deviation_orig * 100
    else:
        improvement = 0.0
    
    return improvement


def calculate_weighted_score(results, weights):
    """
    计算加权综合评分
    
    参数:
        results: 包含各项指标的结果字典
        weights: 各项指标的权重字典
    
    返回:
        overall_score: 综合评分（0-100）
    """
    score = 0.0
    total_weight = 0.0
    
    for key, weight in weights.items():
        if key == 'ASR_core':
            value = results['ASR_core']['suppression_ratio']
        elif key == 'ASR_extended':
            value = results['ASR_extended']['suppression_ratio']
        else:
            value = results.get(key, 0.0)
        
        # 确保值在0-100范围内
        value = max(0.0, min(100.0, value))
        score += value * weight
        total_weight += weight
    
    if total_weight > 0:
        return score / total_weight
    else:
        return 0.0


def determine_grade(score):
    """
    根据综合评分确定等级
    
    参数:
        score: 综合评分（0-100）
    
    返回:
        grade: 评级（A/B/C/D）
    """
    if score >= 80:
        return 'A'
    elif score >= 60:
        return 'B'
    elif score >= 40:
        return 'C'
    else:
        return 'D'


def batch_evaluate_experiments(experiment_list, output_file=None):
    """
    批量评估多个实验的假频抑制效果
    
    参数:
        experiment_list: 实验名称列表
        output_file: 输出结果文件路径（可选）
    
    返回:
        results_summary: 评估结果汇总列表
    """
    results_summary = []

    for exp_name in experiment_list:
        # 构建数据文件路径
        data_path = f'projects/{exp_name}/data/linear_response.json'
        config_path = f'projects/{exp_name}/config.json'
        model_info_path = f'projects/{exp_name}/data/model_info.json'

        # 检查文件是否存在
        if not os.path.exists(data_path):
            print(f"警告：{data_path} 不存在，跳过实验 {exp_name}")
            continue

        try:
            # 执行评估
            evaluation = evaluate_alias_suppression(data_path)

            # 汇总结果
            summary = {
                'experiment': exp_name,
                'ASR_core': evaluation['ASR_core']['suppression_ratio'],
                'overall_score': evaluation['overall_score'],
                'grade': evaluation['grade']
            }

            # 尝试读取模型参数信息
            if os.path.exists(model_info_path):
                try:
                    with open(model_info_path, 'r', encoding='utf-8') as f:
                        model_info = json.load(f)
                        summary['total_params'] = model_info.get('total_params', 0)
                        summary['trainable_params'] = model_info.get('trainable_params', 0)
                except Exception as e:
                    print(f"警告：读取 {model_info_path} 时出错: {str(e)}")
                    summary['total_params'] = 0
                    summary['trainable_params'] = 0
            else:
                summary['total_params'] = 0
                summary['trainable_params'] = 0

            # 尝试读取 config.json 文件中的模型参数
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        model_subcfg = config.get('model_subcfg', {})
                        summary['post_dense_units'] = model_subcfg.get('post_dense_units', 'N/A')
                        summary['post_dense_layers'] = model_subcfg.get('post_dense_layers', 'N/A')
                        summary['init_center_freqs_count'] = len(model_subcfg.get('init_center_freqs', []))
                except Exception as e:
                    print(f"警告：读取 {config_path} 时出错: {str(e)}")
                    summary['post_dense_units'] = 'N/A'
                    summary['post_dense_layers'] = 'N/A'
                    summary['init_center_freqs_count'] = 'N/A'
            else:
                summary['post_dense_units'] = 'N/A'
                summary['post_dense_layers'] = 'N/A'
                summary['init_center_freqs_count'] = 'N/A'

            results_summary.append(summary)

            # 打印单个实验结果
            print(f"\n实验: {exp_name}")
            print(f"  核心区间抑制率: {summary['ASR_core']:.1f}%")
            print(f"  综合评分: {summary['overall_score']:.1f}")
            print(f"  等级: {summary['grade']}")
            print(f"  总参数量: {summary['total_params']}")
            print(f"  post_dense_units: {summary['post_dense_units']}")
            print(f"  post_dense_layers: {summary['post_dense_layers']}")
            print(f"  init_center_freqs_count: {summary['init_center_freqs_count']}")

        except Exception as e:
            print(f"错误：评估实验 {exp_name} 时出错: {str(e)}")
            continue

    # 按综合评分排序
    results_summary.sort(key=lambda x: x['overall_score'], reverse=True)

    # 保存结果到文件
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results_summary, f, indent=2, ensure_ascii=False)
        print(f"\n评估结果已保存到: {output_file}")

    return results_summary