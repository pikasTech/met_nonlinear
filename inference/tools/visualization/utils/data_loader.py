#!/usr/bin/env python3
"""
数据加载工具模块

负责从推理结果目录中加载error_analysis.json文件，
并提取偏置误差分析数据。
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class InferenceDataLoader:
    """推理数据加载器"""
    
    def __init__(self, inference_dir: str):
        """
        初始化数据加载器
        
        Args:
            inference_dir: 推理结果目录路径
        """
        self.inference_dir = Path(inference_dir)
        self.error_analysis_path = self.inference_dir / "error_analysis.json"
        self.metadata_path = self.inference_dir / "inference_metadata.json"
        
    def load_error_analysis(self) -> Dict[str, Any]:
        """
        加载误差分析数据
        
        Returns:
            包含误差分析结果的字典
            
        Raises:
            FileNotFoundError: 如果找不到error_analysis.json文件
            json.JSONDecodeError: 如果JSON文件格式错误
        """
        if not self.error_analysis_path.exists():
            raise FileNotFoundError(f"找不到误差分析文件: {self.error_analysis_path}")
            
        with open(self.error_analysis_path, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    def load_metadata(self) -> Optional[Dict[str, Any]]:
        """
        加载推理元数据（如果存在）
        
        Returns:
            元数据字典，如果文件不存在则返回None
        """
        if not self.metadata_path.exists():
            return None
            
        with open(self.metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    def get_bias_data(self) -> Dict[str, Any]:
        """
        获取偏置误差数据
        
        Returns:
            包含NN-SPICE偏置误差数据的字典
        """
        error_data = self.load_error_analysis()
        
        if 'bias_analysis' not in error_data:
            raise ValueError("误差分析文件中缺少bias_analysis部分")
            
        bias_analysis = error_data['bias_analysis']
        
        if 'nn_spice_bias' not in bias_analysis:
            raise ValueError("偏置分析中缺少nn_spice_bias数据")
            
        return bias_analysis['nn_spice_bias']
        
    def get_layer_bias_errors(self) -> Dict[int, Dict[str, Any]]:
        """
        获取每层的偏置误差数据
        
        Returns:
            以层索引为键的偏置误差字典
        """
        bias_data = self.get_bias_data()
        layer_results = bias_data.get('layer_results', [])
        
        layer_dict = {}
        for layer_data in layer_results:
            layer_info = layer_data['layer_info']
            layer_idx = layer_info['layer']
            
            layer_dict[layer_idx] = {
                'name': layer_info['name'],
                'channel_count': layer_data['channel_count'],
                'bias_errors': layer_data['bias_errors'],
                'summary': layer_data['summary']
            }
            
        return layer_dict
        
    def get_bias_error_matrix(self) -> list:
        """
        获取偏置误差矩阵
        
        Returns:
            偏置误差矩阵（列表的列表）
        """
        bias_data = self.get_bias_data()
        return bias_data.get('bias_error_matrix', [])
        
    def get_global_statistics(self) -> Dict[str, Any]:
        """
        获取全局统计信息
        
        Returns:
            包含全局统计信息的字典
        """
        bias_data = self.get_bias_data()
        return bias_data.get('global_statistics', {})
        
    def get_layer_analysis_data(self) -> Dict[str, Any]:
        """
        获取层级分析数据（包含RMS误差）
        
        Returns:
            包含层级分析数据的字典
        """
        error_data = self.load_error_analysis()
        
        if 'nn_spice_analysis' not in error_data:
            raise ValueError("误差分析文件中缺少nn_spice_analysis部分")
            
        return error_data['nn_spice_analysis']
        
    def get_project_name(self) -> str:
        """
        获取项目名称
        
        Returns:
            项目名称字符串
        """
        error_data = self.load_error_analysis()
        return error_data.get('project_name', 'Unknown')


def compare_inference_results(baseline_dir: str, compensated_dir: str) -> Dict[str, Any]:
    """
    对比两个推理结果
    
    Args:
        baseline_dir: 基准推理结果目录
        compensated_dir: 补偿后推理结果目录
        
    Returns:
        包含对比数据的字典
    """
    baseline_loader = InferenceDataLoader(baseline_dir)
    compensated_loader = InferenceDataLoader(compensated_dir)
    
    # 加载基准数据
    baseline_layers = baseline_loader.get_layer_bias_errors()
    baseline_matrix = baseline_loader.get_bias_error_matrix()
    baseline_stats = baseline_loader.get_global_statistics()
    baseline_analysis = baseline_loader.get_layer_analysis_data()
    
    # 加载补偿后数据
    compensated_layers = compensated_loader.get_layer_bias_errors()
    compensated_matrix = compensated_loader.get_bias_error_matrix()
    compensated_stats = compensated_loader.get_global_statistics()
    compensated_analysis = compensated_loader.get_layer_analysis_data()
    
    # 计算偏置误差改进百分比
    bias_improvements = {}
    rms_improvements = {}
    
    for layer_idx in baseline_layers:
        if layer_idx in compensated_layers:
            # 偏置误差改进
            baseline_mean = baseline_layers[layer_idx]['summary']['mean_bias_error']
            compensated_mean = compensated_layers[layer_idx]['summary']['mean_bias_error']
            
            if baseline_mean != 0:
                bias_improvement = (baseline_mean - compensated_mean) / abs(baseline_mean) * 100
            else:
                bias_improvement = 0.0
                
            bias_improvements[layer_idx] = bias_improvement
            
            # RMS误差改进
            baseline_rms = baseline_analysis['layer_analysis'][layer_idx-1]['rms_error']
            compensated_rms = compensated_analysis['layer_analysis'][layer_idx-1]['rms_error']
            
            if baseline_rms != 0:
                rms_improvement = (baseline_rms - compensated_rms) / baseline_rms * 100
            else:
                rms_improvement = 0.0
                
            rms_improvements[layer_idx] = rms_improvement
    
    # 全局改进
    global_bias_improvement = {
        'mean': (baseline_stats['mean_bias_error'] - compensated_stats['mean_bias_error']) / baseline_stats['mean_bias_error'] * 100,
        'std': (baseline_stats['std_bias_error'] - compensated_stats['std_bias_error']) / baseline_stats['std_bias_error'] * 100,
        'max': (baseline_stats['max_bias_error'] - compensated_stats['max_bias_error']) / baseline_stats['max_bias_error'] * 100
    }
    
    # 计算全局RMS改进
    baseline_rms_all = [layer['rms_error'] for layer in baseline_analysis['layer_analysis']]
    compensated_rms_all = [layer['rms_error'] for layer in compensated_analysis['layer_analysis']]
    baseline_rms_mean = sum(baseline_rms_all) / len(baseline_rms_all)
    compensated_rms_mean = sum(compensated_rms_all) / len(compensated_rms_all)
    
    global_rms_improvement = {
        'mean': (baseline_rms_mean - compensated_rms_mean) / baseline_rms_mean * 100,
        'max': (max(baseline_rms_all) - max(compensated_rms_all)) / max(baseline_rms_all) * 100
    }
    
    return {
        'baseline': {
            'layers': baseline_layers,
            'matrix': baseline_matrix,
            'stats': baseline_stats,
            'analysis': baseline_analysis
        },
        'compensated': {
            'layers': compensated_layers,
            'matrix': compensated_matrix,
            'stats': compensated_stats,
            'analysis': compensated_analysis
        },
        'improvements': {
            'bias_layer': bias_improvements,
            'rms_layer': rms_improvements,
            'bias_global': global_bias_improvement,
            'rms_global': global_rms_improvement
        },
        'project_name': baseline_loader.get_project_name()
    }