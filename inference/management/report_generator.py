"""
报告生成模块

负责生成分析报告和可视化
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class ReportGenerator:
    """报告生成器类"""
    
    def __init__(self, project_name: str):
        """
        初始化报告生成器
        
        参数:
            project_name: 项目名称
        """
        self.project_name = project_name
    
    def generate_analysis_report(self, results: Dict[str, Any], data_dir: str):
        """
        生成分析报告，支持双重误差分析显示
        
        参数:
            results: 分析结果字典
            data_dir: 数据目录
        """
        logger.info('[SUMMARY] 误差分析摘要:')
        
        # 处理NN-SPICE分析结果
        if 'nn_spice_analysis' in results and results['nn_spice_analysis']:
            logger.info('[ANALYSIS] NN-SPICE 误差分析:')
            self._print_layer_errors(results['nn_spice_analysis']['layer_analysis'])
        
        # 处理NN-NumPy分析结果
        if 'nn_numpy_analysis' in results and results['nn_numpy_analysis']:
            logger.info('[ANALYSIS] NN-NumPy 误差分析:')
            self._print_layer_errors(results['nn_numpy_analysis']['layer_analysis'])
            
            # 如果同时有SPICE和NumPy结果，显示对比
            if 'nn_spice_analysis' in results and results['nn_spice_analysis']:
                self._print_spice_numpy_comparison(
                    results['nn_spice_analysis']['layer_analysis'],
                    results['nn_numpy_analysis']['layer_analysis']
                )
        
        
        # 处理偏置分析结果
        if 'bias_analysis' in results and results['bias_analysis']:
            logger.info('[BIAS] 偏置误差分析:')
            self._print_bias_analysis(results['bias_analysis'])
        
        # 显示分析摘要
        if 'comparison_summary' in results:
            self._print_comparison_summary(results['comparison_summary'])
    
    def _print_layer_errors(self, layer_errors: List[Dict]):
        """打印逐层误差信息"""
        for layer in layer_errors:
            logger.info(
                f"  第{layer['layer_index']}层: "
                f"RMS={layer['rms_error']:.6f}, "
                f"最大={layer['max_error']:.6f}, "
                f"样本数={layer['num_samples']}"
            )
    
    def _print_spice_numpy_comparison(self, spice_layers: List[Dict], numpy_layers: List[Dict]):
        """打印SPICE和NumPy的对比结果"""
        logger.info('[COMPARE] SPICE vs NumPy 对比:')
        
        for i, (spice_layer, numpy_layer) in enumerate(zip(spice_layers, numpy_layers)):
            spice_rms = spice_layer['rms_error']
            numpy_rms = numpy_layer['rms_error']
            
            # 计算比值
            if numpy_rms != 0:
                ratio = spice_rms / numpy_rms
            else:
                ratio = float('inf')
            
            # 判断哪个更准确
            if spice_rms < numpy_rms:
                status = '[BETTER] SPICE更准确'
            elif spice_rms > numpy_rms:
                status = '[BETTER] NumPy更准确'
            else:
                status = '[EQUAL] 相当'
            
            logger.info(
                f'  第{i + 1}层: '
                f'SPICE={spice_rms:.6f}, '
                f'NumPy={numpy_rms:.6f}, '
                f'比值={ratio:.2f} {status}'
            )
    
    def _print_comparison_summary(self, summary: Dict):
        """打印对比摘要"""
        comparison_types = summary.get('comparison_types', [])
        logger.info(f'[INFO] 本次分析类型: {", ".join(comparison_types)}')
        
        if summary.get('has_numpy', False):
            logger.info('[OK] NumPy仿真数据已包含在分析中')
        else:
            logger.info('[TIP] 提示: 可通过 cli.py -i 重新生成推理数据以包含NumPy仿真')
    
    def generate_visualization(self, results: Dict[str, Any], data_dir: str):
        """
        生成可视化图表（预留接口）
        
        参数:
            results: 分析结果
            data_dir: 数据目录
        """
        # TODO: 未来可以在这里添加matplotlib等可视化功能
        # 例如：
        # - 误差趋势图
        # - 层间误差对比图
        # - 误差分布直方图
        # - SPICE vs NumPy对比图
        pass
    
    def generate_summary_report(self, results: Dict[str, Any], output_path: str):
        """
        生成详细的摘要报告文件
        
        参数:
            results: 分析结果
            output_path: 输出文件路径
        """
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append(f"推理误差分析报告 - {self.project_name}")
        report_lines.append("=" * 60)
        report_lines.append(f"生成时间: {results.get('timestamp', 'Unknown')}")
        report_lines.append("")
        
        # NN-SPICE分析
        if 'nn_spice_analysis' in results and results['nn_spice_analysis']:
            report_lines.append("## NN-SPICE 误差分析")
            report_lines.append("-" * 40)
            
            analysis = results['nn_spice_analysis']
            validation_info = analysis.get('validation_info', {})
            report_lines.append(f"模型类型: {validation_info.get('model_type', 'Unknown')}")
            report_lines.append(f"NN层数: {validation_info.get('nn_layers', 0)}")
            report_lines.append(f"SPICE层数: {validation_info.get('spice_layers', 0)}")
            report_lines.append("")
            
            report_lines.append("### 逐层误差统计:")
            for layer in analysis['layer_analysis']:
                report_lines.append(
                    f"  第{layer['layer_index']}层:"
                )
                report_lines.append(f"    - RMS误差: {layer['rms_error']:.6f}")
                report_lines.append(f"    - 最大误差: {layer['max_error']:.6f}")
                report_lines.append(f"    - 平均误差: {layer['mean_error']:.6f}")
                report_lines.append(f"    - 标准差: {layer['std_error']:.6f}")
                report_lines.append(f"    - 样本数: {layer['num_samples']}")
            report_lines.append("")
        
        # NN-NumPy分析
        if 'nn_numpy_analysis' in results and results['nn_numpy_analysis']:
            report_lines.append("## NN-NumPy 误差分析")
            report_lines.append("-" * 40)
            
            analysis = results['nn_numpy_analysis']
            validation_info = analysis.get('validation_info', {})
            report_lines.append(f"NumPy层数: {validation_info.get('numpy_layers', 0)}")
            report_lines.append("")
            
            report_lines.append("### 逐层误差统计:")
            for layer in analysis['layer_analysis']:
                report_lines.append(
                    f"  第{layer['layer_index']}层:"
                )
                report_lines.append(f"    - RMS误差: {layer['rms_error']:.6f}")
                report_lines.append(f"    - 最大误差: {layer['max_error']:.6f}")
                report_lines.append(f"    - 平均误差: {layer['mean_error']:.6f}")
                report_lines.append(f"    - 标准差: {layer['std_error']:.6f}")
                report_lines.append(f"    - 样本数: {layer['num_samples']}")
            report_lines.append("")
        
        # 偏置分析
        if 'bias_analysis' in results and results['bias_analysis']:
            report_lines.extend(self._generate_bias_error_section(results['bias_analysis']))
            report_lines.append("")
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(''.join(report_lines))
        
        logger.info(f'[REPORT] 已生成详细报告: {output_path}')
    
    def format_report_data(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化报告数据，便于导出或进一步处理
        
        参数:
            results: 原始分析结果
            
        返回:
            Dict: 格式化后的数据
        """
        formatted = {
            'project_name': self.project_name,
            'timestamp': results.get('timestamp', ''),
            'summary': {},
            'detailed_results': {}
        }
        
        # 提取关键指标
        if 'nn_spice_analysis' in results and results['nn_spice_analysis']:
            spice_layers = results['nn_spice_analysis']['layer_analysis']
            formatted['summary']['nn_spice'] = {
                'avg_rms_error': sum(l['rms_error'] for l in spice_layers) / len(spice_layers),
                'max_error': max(l['max_error'] for l in spice_layers),
                'total_layers': len(spice_layers)
            }
            formatted['detailed_results']['nn_spice'] = spice_layers
        
        if 'nn_numpy_analysis' in results and results['nn_numpy_analysis']:
            numpy_layers = results['nn_numpy_analysis']['layer_analysis']
            formatted['summary']['nn_numpy'] = {
                'avg_rms_error': sum(l['rms_error'] for l in numpy_layers) / len(numpy_layers),
                'max_error': max(l['max_error'] for l in numpy_layers),
                'total_layers': len(numpy_layers)
            }
            formatted['detailed_results']['nn_numpy'] = numpy_layers
        
        return formatted
    
    def _print_bias_analysis(self, bias_analysis: Dict[str, Any]):
        """打印偏置误差分析结果"""
        method = bias_analysis.get('method', 'unknown')
        logger.info(f'  分析方法: {method}')
        
        # 打印参数
        params = bias_analysis.get('parameters', {})
        if params:
            logger.info(f'  参数: {params}')
        
        # 打印NN-SPICE偏置分析
        if 'nn_spice_matrix_formatted' in bias_analysis:
            logger.info('  [DATA] NN-SPICE 偏置误差:')
            formatted = bias_analysis['nn_spice_matrix_formatted']
            self._print_bias_matrix_summary_new(formatted)
            
            # 打印格式化矩阵的统计信息
            overall_stats = formatted.get('overall_stats', {})
            logger.info(f'    总体统计:')
            logger.info(f'      平均偏置误差: {overall_stats.get("mean", 0):.6f}')
            logger.info(f'      标准差: {overall_stats.get("std", 0):.6f}')
            logger.info(f'      最大绝对误差: {overall_stats.get("max", 0):.6f}')
            logger.info(f'      RMS误差: {overall_stats.get("rms", 0):.6f}')
        
        # 打印NN-NumPy偏置分析
        if 'nn_numpy_matrix_formatted' in bias_analysis:
            logger.info('[DATA] NN-NumPy 偏置误差:')
            formatted = bias_analysis['nn_numpy_matrix_formatted']
            self._print_bias_matrix_summary_new(formatted)
            
            # 打印格式化矩阵的统计信息
            overall_stats = formatted.get('overall_stats', {})
            logger.info(f'    总体统计:')
            logger.info(f'      平均偏置误差: {overall_stats.get("mean", 0):.6f}')
            logger.info(f'      标准差: {overall_stats.get("std", 0):.6f}')
            logger.info(f'      最大绝对误差: {overall_stats.get("max", 0):.6f}')
            logger.info(f'      RMS误差: {overall_stats.get("rms", 0):.6f}')
        
        # 打印摘要
        if 'summary' in bias_analysis:
            logger.info('[SUMMARY] 偏置分析摘要:')
            summary = bias_analysis['summary']
            
            if 'nn_spice' in summary:
                nn_spice = summary['nn_spice']
                logger.info(f'    NN-SPICE:')
                logger.info(f'      平均偏置: {nn_spice.get("overall_mean_bias", 0):.6f}')
                if nn_spice.get('worst_case'):
                    worst = nn_spice['worst_case']
                    logger.info(f'      最差情况: 层{worst["layer"]}, 通道{worst["channel"]}, 误差{worst["bias_error"]:.6f}')
            
            if 'nn_numpy' in summary:
                nn_numpy = summary['nn_numpy']
                logger.info(f'    NN-NumPy:')
                logger.info(f'      平均偏置: {nn_numpy.get("overall_mean_bias", 0):.6f}')
                if nn_numpy.get('worst_case'):
                    worst = nn_numpy['worst_case']
                    logger.info(f'      最差情况: 层{worst["layer"]}, 通道{worst["channel"]}, 误差{worst["bias_error"]:.6f}')
    
    def _print_bias_matrix_summary_new(self, formatted_results: Dict[str, Any]):
        """打印偏置误差矩阵摘要（新格式）"""
        n_layers = formatted_results.get('layer_count', 0)
        channels_per_layer = formatted_results.get('channels_per_layer', [])
        
        if channels_per_layer:
            channel_desc = f"{channels_per_layer}" if len(set(channels_per_layer)) > 1 else f"{channels_per_layer[0]}"
            logger.info(f'    矩阵形状: {n_layers}层, 通道数: {channel_desc}')
        else:
            logger.info(f'    矩阵形状: {n_layers}层')
        
        # 打印详细的偏置误差矩阵
        bias_matrix = formatted_results.get('matrix', [])
        if bias_matrix:
            logger.info('    详细偏置误差:')
            for i, layer_errors in enumerate(bias_matrix):
                if layer_errors:
                    # 格式化每个通道的误差值
                    formatted_errors = [f'{err:8.6f}' for err in layer_errors]
                    logger.info(f'      层{i+1} ({len(layer_errors)}通道): [{", ".join(formatted_errors)}]')
        
        # 打印每层统计
        per_layer_stats = formatted_results.get('per_layer_stats', [])
        if per_layer_stats:
            logger.info('    每层统计:')
            for layer_stat in per_layer_stats:
                layer_name = layer_stat.get('layer', '')
                mean_val = layer_stat.get('mean', 0)
                std_val = layer_stat.get('std', 0)
                max_val = layer_stat.get('max', 0)
                channel_count = layer_stat.get('channel_count', 0)
                logger.info(f'      {layer_name}: 均值={mean_val:8.6f}, 标准差={std_val:8.6f}, 最大值={max_val:8.6f} ({channel_count}通道)')
    
    
    def _generate_bias_error_section(self, bias_analysis: Dict[str, Any]) -> List[str]:
        """生成偏置误差报告部分"""
        lines = []
        lines.append("## 偏置误差分析")
        lines.append("-" * 40)
        lines.append(f"分析方法: {bias_analysis.get('method', 'unknown')}")
        
        params = bias_analysis.get('parameters', {})
        if params:
            lines.append(f"参数: {params}")
        
        lines.append("")
        
        # NN-SPICE偏置分析
        if 'nn_spice_bias' in bias_analysis:
            lines.append("### NN-SPICE 偏置误差")
            lines.extend(self._format_bias_matrix_report(bias_analysis['nn_spice_bias']))
            lines.append("")
        
        # NN-NumPy偏置分析
        if 'nn_numpy_bias' in bias_analysis:
            lines.append("### NN-NumPy 偏置误差")
            lines.extend(self._format_bias_matrix_report(bias_analysis['nn_numpy_bias']))
            lines.append("")
        
        return lines
    
    def _format_bias_matrix_report(self, bias_results: Dict[str, Any]) -> List[str]:
        """格式化偏置误差矩阵报告"""
        lines = []
        
        # 使用新格式获取矩阵信息
        formatted = bias_results.get('formatted', {})
        if formatted:
            n_layers = formatted.get('layer_count', 0)
            channels_per_layer = formatted.get('channels_per_layer', [])
            if channels_per_layer:
                channel_desc = f"{channels_per_layer}" if len(set(channels_per_layer)) > 1 else f"{channels_per_layer[0]}"
                lines.append(f"矩阵形状: {n_layers}层, 通道数: {channel_desc}")
            else:
                lines.append(f"矩阵形状: {n_layers}层")
        else:
            lines.append("矩阵形状: 未知")
        
        # 添加统计信息
        stats = bias_results.get('global_statistics', {})
        if stats:
            lines.append(f"总体平均偏置: {stats.get('overall_mean_bias', 0):.6f}")
            lines.append(f"总体标准差: {stats.get('overall_std_bias', 0):.6f}")
            
            worst_case = stats.get('worst_case')
            if worst_case:
                lines.append(f"最大偏置误差: 层{worst_case['layer']}, 通道{worst_case['channel']}, 误差={worst_case['bias_error']:.6f}")
        
        # 添加层结果详情
        layer_results = bias_results.get('layer_results', [])
        if layer_results:
            lines.append("")
            lines.append("逐层偏置误差:")
            for layer_result in layer_results:
                layer_info = layer_result.get('layer_info', {})
                layer_num = layer_info.get('layer', 0)
                lines.append(f"  层{layer_num}:")
                
                summary = layer_result.get('summary', {})
                lines.append(f"    平均偏置误差: {summary.get('mean_bias_error', 0):.6f}")
                lines.append(f"    最大偏置误差: {summary.get('max_bias_error', 0):.6f}")
        
        return lines
    
    def _create_bias_error_heatmap(self, bias_matrix: List[List[float]], output_path: str):
        """
        创建偏置误差热力图（预留接口）
        
        参数:
            bias_matrix: 偏置误差矩阵
            output_path: 输出路径
        """
        # TODO: 使用matplotlib创建热力图
        pass