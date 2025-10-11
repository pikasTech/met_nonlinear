"""
误差分析模块

负责计算和分析推理结果之间的误差
"""

import os
import json
import time
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

from .utils import compute_error_metrics, flatten_wave_records, combine_layer_outputs, generate_error_statistics, extract_channel_data, format_bias_error_matrix
from ..analysis.bias_analyzer import ChannelBiasAnalyzer

logger = logging.getLogger(__name__)


class ErrorAnalyzer:
    """误差分析器类"""
    
    def __init__(self, project_name: str, config: Dict, wave_processor):
        """
        初始化误差分析器
        
        参数:
            project_name: 项目名称
            config: 配置对象
            wave_processor: Wave处理器实例
        """
        self.project_name = project_name
        self.config = config
        self.wave_processor = wave_processor
        self.bias_analyzer = None  # 延迟初始化
    
    def analyze_inference_errors(self, data_dir: str) -> Dict[str, Any]:
        """
        分析推理误差，支持双重误差分析（NN-SPICE 和 NN-NumPy）
        
        参数:
            data_dir: 推理数据目录
            
        返回:
            Dict: 分析结果字典
        """
        # 检查必需的目录
        nn_layers_dir = os.path.join(data_dir, 'nn_layers')
        spice_layers_dir = os.path.join(data_dir, 'spice_layers')
        numpy_layers_dir = os.path.join(data_dir, 'numpy_layers')
        
        if not os.path.exists(nn_layers_dir):
            raise FileNotFoundError(f'未找到神经网络推理数据目录：{nn_layers_dir}')
        if not os.path.exists(spice_layers_dir):
            raise FileNotFoundError(f'未找到SPICE推理数据目录：{spice_layers_dir}')
        
        has_numpy = os.path.exists(numpy_layers_dir)
        
        # 统计层数
        nn_files = self._get_layer_files(nn_layers_dir)
        nn_layers = len(nn_files)
        
        logger.info(f'发现推理数据：神经网络 {nn_layers} 层')
        
        if has_numpy:
            numpy_files = self._get_layer_files(numpy_layers_dir)
            logger.info(f'发现NumPy推理数据：{len(numpy_files)} 层')
        
        # 验证模型特定的层数
        self._validate_layer_count(nn_layers)
        
        # 准备分析结果
        analysis_results = {
            'project_name': self.project_name,
            'timestamp': self._get_timestamp(),
            'comparison_summary': {
                'has_numpy': has_numpy,
                'comparison_types': ['nn_spice']
            }
        }
        
        # 分析NN-SPICE误差
        logger.info(f'\n[ANALYZE] 开始 NN-SPICE 误差分析...')
        nn_spice_errors = self.compute_layer_errors(
            nn_layers_dir, spice_layers_dir, 
            'nn_spice_error_layers', 'SPICE', data_dir
        )
        
        analysis_results['nn_spice_analysis'] = self._create_analysis_result(
            nn_spice_errors, nn_layers, spice_layers_dir, 'spice'
        )
        
        # 分析NN-NumPy误差（如果有）
        if has_numpy:
            logger.info(f'\n[ANALYZE] 开始 NN-NumPy 误差分析...')
            analysis_results['comparison_summary']['comparison_types'].append('nn_numpy')
            
            nn_numpy_errors = self.compute_layer_errors(
                nn_layers_dir, numpy_layers_dir, 
                'nn_numpy_error_layers', 'NumPy', data_dir
            )
            
            analysis_results['nn_numpy_analysis'] = self._create_analysis_result(
                nn_numpy_errors, nn_layers, numpy_layers_dir, 'numpy'
            )
        else:
            logger.info(f'\n[INFO] 未发现NumPy推理数据，跳过 NN-NumPy 误差分析')
            analysis_results['nn_numpy_analysis'] = None
        
        # 添加偏置分析（如果启用）
        if self.config.get('enable_bias_analysis', True):
            logger.info(f'\n[ANALYZE] 开始偏置误差分析...')
            bias_analysis_results = self._analyze_bias_errors(
                nn_layers_dir, spice_layers_dir, numpy_layers_dir if has_numpy else None
            )
            analysis_results['bias_analysis'] = bias_analysis_results
        
        # 保存分析结果
        with open(f'{data_dir}/error_analysis.json', 'w') as f:
            json.dump(analysis_results, f, indent=2)
        
        return analysis_results
    
    def compute_layer_errors(self, reference_dir: str, comparison_dir: str, 
                           error_dir_name: str, comparison_type: str, 
                           data_dir: str) -> List[Dict]:
        """
        计算两个推理结果之间的逐层误差
        
        参数:
            reference_dir: 参考数据目录（通常是 nn_layers）
            comparison_dir: 对比数据目录（spice_layers 或 numpy_layers）
            error_dir_name: 误差输出目录名
            comparison_type: 对比类型字符串（用于描述）
            data_dir: 数据根目录
        
        返回:
            List[Dict]: 包含逐层误差统计的列表
        """
        # 获取文件列表
        ref_files = self._get_layer_files(reference_dir)
        comp_files = self._get_layer_files(comparison_dir)
        
        # 验证层数一致性
        self._validate_layer_consistency(ref_files, comp_files, comparison_type)
        
        # 创建误差输出目录
        error_layers_dir = os.path.join(data_dir, error_dir_name)
        os.makedirs(error_layers_dir, exist_ok=True)
        
        layer_errors = []
        
        # 逐层计算误差
        for i in range(len(ref_files)):
            layer_error = self._compute_single_layer_error(
                i, ref_files[i], comp_files[i],
                reference_dir, comparison_dir, 
                error_layers_dir, error_dir_name,
                comparison_type
            )
            layer_errors.append(layer_error)
        
        return layer_errors
    
    def _compute_single_layer_error(self, layer_idx: int, ref_file: str, comp_file: str,
                                  ref_dir: str, comp_dir: str, error_dir: str, 
                                  error_dir_name: str, comparison_type: str) -> Dict:
        """计算单层误差"""
        ref_path = os.path.join(ref_dir, ref_file)
        comp_path = os.path.join(comp_dir, comp_file)
        
        # 加载数据
        ref_data = self.wave_processor.load_waveform(ref_path)
        comp_data = self.wave_processor.load_waveform(comp_path)
        
        logger.info(f'  计算第 {layer_idx + 1} 层 {comparison_type} 误差...')
        
        # 尝试生成误差wave文件
        self._try_save_error_wave(
            ref_data, comp_data, layer_idx, 
            comparison_type, error_dir, error_dir_name
        )
        
        # 展平数据
        ref_output = flatten_wave_records(ref_data)
        comp_output = flatten_wave_records(comp_data)
        
        # 计算误差统计
        metrics = compute_error_metrics(ref_output, comp_output)
        
        # 添加额外信息
        metrics.update({
            'layer_index': layer_idx + 1,
            'ref_records': len(ref_data.records),
            'comp_records': len(comp_data.records),
            'error_wave_path': f'{error_dir_name}/layer_{layer_idx + 1}.wave'
        })
        
        return metrics
    
    def _try_save_error_wave(self, ref_data, comp_data, layer_idx: int, 
                           comparison_type: str, error_dir: str, error_dir_name: str):
        """尝试保存误差wave文件"""
        try:
            error_wave = ref_data - comp_data
            error_wave.description = f'Error (NN - {comparison_type.upper()}) for Layer {layer_idx + 1}'
            error_wave.add_user_metadata('project_name', self.project_name)
            error_wave.add_user_metadata('layer_index', layer_idx + 1)
            error_wave.add_user_metadata('comparison_type', comparison_type)
            error_wave.add_user_metadata('analysis_timestamp', self._get_timestamp())
            
            error_path = os.path.join(error_dir, f'layer_{layer_idx + 1}.wave')
            self.wave_processor.save_waveform(error_path, error_wave)
            logger.info(f'    保存 {comparison_type} 误差wave: {error_dir_name}/layer_{layer_idx + 1}.wave')
        except Exception as e:
            logger.info(f'    警告：无法生成 {comparison_type} 误差wave - {str(e)}')
    
    def _get_layer_files(self, directory: str) -> List[str]:
        """获取目录中的层文件列表"""
        all_files = os.listdir(directory)
        layer_files = sorted([f for f in all_files 
                            if (f.startswith('layer_') or '_layer' in f) and f.endswith('.wave')])
        return layer_files
    
    def _validate_layer_count(self, nn_layers: int):
        """验证模型特定的层数"""
        if 'WaveNet5' in self.config.get('use_model', ''):
            # WaveNet5 包含SVF层 + 后处理Dense层
            # 如果配置中有post_dense_layers，则总层数 = 2 (SVF) + post_dense_layers
            model_subcfg = self.config.get('model_subcfg', {})
            svf_layers = 2  # WaveNet5 默认2个SVF层
            post_dense_layers = model_subcfg.get('post_dense_layers', 0)
            expected_layers = svf_layers + post_dense_layers
            
            if nn_layers != expected_layers:
                logger.warning(f'WaveNet5期望{expected_layers}层(SVF:{svf_layers} + Dense:{post_dense_layers})，但数据显示{nn_layers}层。')
                # 不再抛出异常，允许继续分析
    
    def _validate_layer_consistency(self, ref_files: List[str], comp_files: List[str], 
                                  comparison_type: str):
        """验证层数一致性"""
        ref_layers = len(ref_files)
        comp_layers = len(comp_files)
        
        logger.info(f'计算 {comparison_type} 误差：参考 {ref_layers} 层，对比 {comp_layers} 层')
        
        if ref_layers != comp_layers:
            error_msg = (f'{comparison_type} 推理数据层数不一致：'
                        f'参考 {ref_layers} 层，对比 {comp_layers} 层。\n'
                        f'无法进行准确的逐层误差分析。')
            logger.error(f'错误：{error_msg}')
            raise ValueError(error_msg)
    
    def _create_analysis_result(self, layer_errors: List[Dict], nn_layers: int, 
                              comp_dir: str, comp_type: str) -> Dict:
        """创建分析结果字典"""
        comp_files = self._get_layer_files(comp_dir)
        
        return {
            'layer_analysis': layer_errors,
            'validation_info': {
                'nn_layers': nn_layers,
                f'{comp_type}_layers': len(comp_files),
                'model_type': self.config.get('use_model', ''),
                'validation_passed': True
            }
        }
    
    def combine_layer_outputs(self, layer_outputs: List, prefix: str):
        """合并分层输出（委托给utils）"""
        return combine_layer_outputs(layer_outputs, prefix, self.wave_processor)
    
    def generate_error_statistics(self, layer_errors: List[Dict]) -> Dict:
        """生成误差统计摘要（委托给utils）"""
        return generate_error_statistics(layer_errors)
    
    def _get_timestamp(self):
        """获取当前时间戳"""
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    
    def _analyze_bias_errors(self, nn_dir: str, spice_dir: str, numpy_dir: Optional[str]) -> Dict[str, Any]:
        """
        分析偏置误差
        
        参数:
            nn_dir: 神经网络层输出目录
            spice_dir: SPICE层输出目录
            numpy_dir: NumPy层输出目录（可选）
            
        返回:
            Dict: 偏置分析结果
        """
        # 初始化偏置分析器
        bias_method = self.config.get('bias_method', 'auto')
        bias_params = self.config.get('bias_params', {})
        
        if self.bias_analyzer is None:
            self.bias_analyzer = ChannelBiasAnalyzer(method=bias_method, **bias_params)
        
        # 获取层文件
        nn_files = self._get_layer_files(nn_dir)
        spice_files = self._get_layer_files(spice_dir)
        
        # 准备结果
        bias_results = {
            'method': bias_method,
            'parameters': bias_params,
            'analysis_timestamp': self._get_timestamp()
        }
        
        # 分析NN-SPICE偏置误差
        logger.info('  分析 NN-SPICE 偏置误差...')
        logger.info(f'    准备分析 {len(nn_files)} 层数据')
        nn_spice_layer_data = []
        
        for i in range(len(nn_files)):
            logger.info(f'    正在加载第 {i+1}/{len(nn_files)} 层数据...')
            # 加载数据
            nn_data = self.wave_processor.load_waveform(os.path.join(nn_dir, nn_files[i]))
            spice_data = self.wave_processor.load_waveform(os.path.join(spice_dir, spice_files[i]))
            
            # 提取通道数据
            nn_channel_data, sample_rate = extract_channel_data(nn_data)
            spice_channel_data, _ = extract_channel_data(spice_data)
            
            logger.info(f'    第{i+1}层: NN数据形状={nn_channel_data.shape}, SPICE数据形状={spice_channel_data.shape}')
            
            # 确保形状一致
            min_samples = min(nn_channel_data.shape[0], spice_channel_data.shape[0])
            nn_channel_data = nn_channel_data[:min_samples]
            spice_channel_data = spice_channel_data[:min_samples]
            
            layer_info = {'layer': i + 1, 'name': f'Layer_{i + 1}'}
            nn_spice_layer_data.append((nn_channel_data, spice_channel_data, sample_rate, layer_info))
            logger.info(f'    第{i+1}层数据准备完成')
        
        logger.info('    数据加载完成，开始执行多层偏置分析...')
        # 执行多层偏置分析
        nn_spice_results = self.bias_analyzer.analyze_multilayer_bias(nn_spice_layer_data)
        logger.info('    NN-SPICE多层偏置分析完成')
        bias_results['nn_spice_bias'] = nn_spice_results
        
        logger.info('    正在格式化偏置误差矩阵...')
        nn_spice_matrix = nn_spice_results['bias_error_matrix']
        bias_results['nn_spice_matrix_formatted'] = format_bias_error_matrix(nn_spice_matrix)
        logger.info('    NN-SPICE偏置误差矩阵格式化完成')
        
        # 如果有NumPy数据，也进行分析
        if numpy_dir:
            logger.info('  分析 NN-NumPy 偏置误差...')
            numpy_files = self._get_layer_files(numpy_dir)
            nn_numpy_layer_data = []
            
            for i in range(len(nn_files)):
                # 加载数据
                nn_data = self.wave_processor.load_waveform(os.path.join(nn_dir, nn_files[i]))
                numpy_data = self.wave_processor.load_waveform(os.path.join(numpy_dir, numpy_files[i]))
                
                # 提取通道数据
                nn_channel_data, sample_rate = extract_channel_data(nn_data)
                numpy_channel_data, _ = extract_channel_data(numpy_data)
                
                # 确保形状一致
                min_samples = min(nn_channel_data.shape[0], numpy_channel_data.shape[0])
                nn_channel_data = nn_channel_data[:min_samples]
                numpy_channel_data = numpy_channel_data[:min_samples]
                
                layer_info = {'layer': i + 1, 'name': f'Layer_{i + 1}'}
                nn_numpy_layer_data.append((nn_channel_data, numpy_channel_data, sample_rate, layer_info))
            
            # 执行多层偏置分析
            nn_numpy_results = self.bias_analyzer.analyze_multilayer_bias(nn_numpy_layer_data)
            bias_results['nn_numpy_bias'] = nn_numpy_results
            
            # 格式化偏置误差矩阵
            nn_numpy_matrix = nn_numpy_results['bias_error_matrix']
            bias_results['nn_numpy_matrix_formatted'] = format_bias_error_matrix(nn_numpy_matrix)
        
        # 生成摘要
        bias_results['summary'] = self._generate_bias_summary(bias_results)
        
        logger.info('  偏置误差分析完成')
        return bias_results
    
    def _analyze_channel_bias_errors(self, ref_data, comp_data, method='auto'):
        """
        分析通道级偏置误差
        
        参数:
            ref_data: 参考数据
            comp_data: 对比数据
            method: 分析方法
            
        返回:
            Dict: 偏置分析结果
        """
        if self.bias_analyzer is None:
            self.bias_analyzer = ChannelBiasAnalyzer(method=method)
        
        # 提取通道数据
        ref_channel_data, sample_rate = extract_channel_data(ref_data)
        comp_channel_data, _ = extract_channel_data(comp_data)
        
        # 分析偏置误差
        return self.bias_analyzer.analyze_bias_errors(ref_channel_data, comp_channel_data, sample_rate)
    
    def _generate_bias_summary(self, bias_results: Dict) -> Dict:
        """生成偏置分析摘要"""
        summary = {}
        
        # NN-SPICE摘要
        if 'nn_spice_bias' in bias_results:
            nn_spice_bias = bias_results['nn_spice_bias']
            if 'global_statistics' in nn_spice_bias:
                global_stats = nn_spice_bias['global_statistics']
                summary['nn_spice'] = {
                    'overall_mean_bias': global_stats['mean_bias_error'],
                    'overall_std_bias': global_stats['std_bias_error'],
                    'overall_max_bias': global_stats['max_bias_error'],
                    'total_channels': global_stats['total_channels'],
                    'worst_case': nn_spice_bias.get('worst_case')
                }
        
        # NN-NumPy摘要
        if 'nn_numpy_bias' in bias_results:
            nn_numpy_bias = bias_results['nn_numpy_bias']
            if 'global_statistics' in nn_numpy_bias:
                global_stats = nn_numpy_bias['global_statistics']
                summary['nn_numpy'] = {
                    'overall_mean_bias': global_stats['mean_bias_error'],
                    'overall_std_bias': global_stats['std_bias_error'],
                    'overall_max_bias': global_stats['max_bias_error'],
                    'total_channels': global_stats['total_channels'],
                    'worst_case': nn_numpy_bias.get('worst_case')
                }
        
        return summary