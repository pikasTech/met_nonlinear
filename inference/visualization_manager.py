#!/usr/bin/env python3
"""
偏置分析可视化管理器

负责管理和执行偏置补偿对比可视化任务。
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
import traceback

logger = logging.getLogger('visualization_manager')


class BiasVisualizationManager:
    """偏置分析可视化管理器"""
    
    def __init__(self, project_manager):
        """
        初始化可视化管理器
        
        Args:
            project_manager: ProjectManager 实例
        """
        self.project_manager = project_manager
        self.project_path = project_manager.project_path
        self.project_name = project_manager.project_name
        
    def run_visualization(self, baseline_dir=None, compensated_dir=None, 
                         output_dir=None, config_path=None):
        """
        执行偏置补偿对比可视化
        
        Args:
            baseline_dir: 基准推理结果目录，默认为项目的inference_baseline目录
            compensated_dir: 补偿后推理结果目录，默认为项目的inference_c123目录
            output_dir: 输出目录，默认为项目下的bias_comparison_results
            config_path: 配置文件路径，默认使用内置配置
            
        Returns:
            Dict: 包含生成的文件路径和可视化报告
        """
        try:
            # 设置默认路径
            if baseline_dir is None:
                baseline_dir = f"{self.project_path}/data/inference_baseline"
            if compensated_dir is None:
                compensated_dir = f"{self.project_path}/data/inference_c123"
            if output_dir is None:
                output_dir = f"{self.project_path}/bias_comparison_results"
                
            # 检查目录是否存在
            if not os.path.exists(baseline_dir):
                raise FileNotFoundError(f"基准推理结果目录不存在: {baseline_dir}")
            if not os.path.exists(compensated_dir):
                raise FileNotFoundError(f"补偿后推理结果目录不存在: {compensated_dir}")
            
            # 导入可视化模块
            self._setup_visualization_imports()
            
            from data_loader import compare_inference_results
            from plot_helpers import (
                setup_academic_style, plot_layer_bias_comparison_simple,
                plot_global_improvement_bar, plot_bias_error_heatmap,
                plot_combined_improvement_comparison
            )
            from report_generator import generate_markdown_report
            
            # 加载配置
            config = self._load_config(config_path)
            
            logger.info(f"开始偏置补偿对比可视化...")
            logger.info(f"  基准目录: {baseline_dir}")
            logger.info(f"  补偿后目录: {compensated_dir}")
            logger.info(f"  输出目录: {output_dir}")
            
            # 创建输出目录结构
            output_paths = self._create_output_directories(output_dir)
            
            # 加载和对比数据
            logger.info("加载推理数据...")
            comparison_data = compare_inference_results(baseline_dir, compensated_dir)
            
            # 打印基本信息
            self._log_comparison_summary(comparison_data)
            
            # 生成可视化图表
            logger.info("生成可视化图表...")
            generated_files = self._generate_visualizations(comparison_data, output_paths, config)
            
            # 生成分析报告
            logger.info("生成汇总分析报告...")
            md_report_path = generate_markdown_report(comparison_data, output_dir, config)
            generated_files.append(md_report_path)
            
            # 生成完成报告
            report = self._create_final_report(
                comparison_data, baseline_dir, compensated_dir, 
                output_dir, generated_files, md_report_path
            )
            
            self._log_completion_summary(report)
            
            return report
            
        except Exception as e:
            error_msg = f"可视化生成失败: {e}"
            logger.error(error_msg)
            traceback.print_exc()
            raise
    
    def _setup_visualization_imports(self):
        """设置可视化模块导入路径"""
        # 获取正确的可视化工具路径 - 当前文件在 inference/ 目录下
        current_dir = os.path.dirname(os.path.abspath(__file__))  # inference/
        viz_path = os.path.join(current_dir, 'tools', 'visualization')  # inference/tools/visualization
        
        if not os.path.exists(viz_path):
            raise FileNotFoundError(f"可视化工具目录不存在: {viz_path}")
        
        # 将可视化工具路径添加到Python路径
        if viz_path not in sys.path:
            sys.path.insert(0, viz_path)
        
        # 将utils目录也添加到Python路径
        utils_path = os.path.join(viz_path, 'utils')
        if utils_path not in sys.path:
            sys.path.insert(0, utils_path)
        
        # 验证导入
        try:
            # 现在直接导入模块
            import data_loader
            import plot_helpers  
            import report_generator
            logger.info(f"成功导入可视化模块，路径: {viz_path}")
        except ImportError as e:
            logger.error(f"导入可视化模块失败: {e}")
            logger.error(f"可视化工具路径: {viz_path}")
            logger.error("请确保 inference/tools/visualization/utils/ 目录下的模块文件存在")
            # 列出实际存在的文件以帮助调试
            if os.path.exists(viz_path):
                utils_path = os.path.join(viz_path, 'utils')
                if os.path.exists(utils_path):
                    files = os.listdir(utils_path)
                    logger.error(f"utils目录下的文件: {files}")
                else:
                    logger.error(f"utils目录不存在: {utils_path}")
            raise
    
    def _load_config(self, config_path=None):
        """加载可视化配置"""
        default_config = {
            "plots": {
                "overview": True,
                "layer_analysis": True,
                "channel_analysis": True,
                "distribution": True,
                "statistics": True,
                "rms_analysis": False
            },
            "figure": {
                "dpi": 300,
                "figsize": [10, 8],
                "font_size": 12
            },
            "colors": {
                "baseline": "#E74C3C",
                "compensated": "#27AE60", 
                "improvement": "#3498DB",
                "colormap": "viridis"
            },
            "output": {
                "format": "png",
                "save_raw_data": True
            }
        }
        
        # 如果提供了配置文件路径，则加载配置
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info(f"已加载自定义配置: {config_path}")
            except Exception as e:
                logger.warning(f"加载配置文件失败，使用默认配置: {e}")
                config = default_config
        else:
            config = default_config
            
        return config
    
    def _create_output_directories(self, output_dir):
        """创建输出目录结构"""
        base_path = Path(output_dir)
        figures_dir = base_path / 'figures'
        subdirs = ['overview', 'layer_analysis', 'channel_analysis', 'distribution', 'statistics']
        
        output_paths = {}
        for subdir in subdirs:
            fig_path = figures_dir / subdir
            fig_path.mkdir(parents=True, exist_ok=True)
            output_paths[subdir] = str(fig_path)
            
        return output_paths
    
    def _log_comparison_summary(self, comparison_data):
        """记录对比数据摘要"""
        logger.info(f"项目: {comparison_data['project_name']}")
        logger.info(f"偏置误差全局改进:")
        logger.info(f"  - 平均偏置: {comparison_data['improvements']['bias_global']['mean']:.1f}%")
        logger.info(f"  - 标准差: {comparison_data['improvements']['bias_global']['std']:.1f}%")
        logger.info(f"  - 最大误差: {comparison_data['improvements']['bias_global']['max']:.1f}%")
    
    def _generate_visualizations(self, comparison_data, output_paths, config):
        """生成所有可视化图表"""
        from plot_helpers import (
            plot_global_improvement_bar, plot_combined_improvement_comparison,
            plot_bias_error_heatmap, plot_layer_bias_comparison_simple
        )
        
        generated_files = []
        
        # 概览分析
        if config['plots'].get('overview', True):
            logger.info("  生成概览分析图...")
            
            # 全局改进条形图
            improvement_path = plot_global_improvement_bar(
                comparison_data['improvements']['bias_global'], 
                output_paths['overview'], config
            )
            generated_files.append(improvement_path)
            
            # 综合对比图
            combined_path = plot_combined_improvement_comparison(
                comparison_data, output_paths['overview'], config
            )
            generated_files.append(combined_path)
            
            # 偏置误差热力图
            baseline_matrix, compensated_matrix = self._prepare_heatmap_data(comparison_data)
            heatmap_path, _ = plot_bias_error_heatmap(
                baseline_matrix, compensated_matrix, 
                output_paths['overview'], config
            )
            generated_files.append(heatmap_path)
        
        # 逐层分析
        if config['plots'].get('layer_analysis', True):
            logger.info("  生成逐层分析图...")
            baseline = comparison_data['baseline']
            compensated = comparison_data['compensated']
            
            for layer_idx in baseline['layers']:
                layer_path = plot_layer_bias_comparison_simple(
                    baseline, compensated, layer_idx, 
                    output_paths['layer_analysis'], config
                )
                generated_files.append(layer_path)
        
        return generated_files
    
    def _prepare_heatmap_data(self, comparison_data):
        """准备热力图数据"""
        baseline_matrix = []
        compensated_matrix = []
        
        for layer_idx in sorted(comparison_data['baseline']['layers'].keys()):
            baseline_layer = comparison_data['baseline']['layers'][layer_idx]
            compensated_layer = comparison_data['compensated']['layers'][layer_idx]
            baseline_errors = [ch['bias_error'] for ch in baseline_layer['bias_errors']]
            compensated_errors = [ch['bias_error'] for ch in compensated_layer['bias_errors']]
            baseline_matrix.append(baseline_errors)
            compensated_matrix.append(compensated_errors)
            
        return baseline_matrix, compensated_matrix
    
    def _create_final_report(self, comparison_data, baseline_dir, compensated_dir, 
                           output_dir, generated_files, md_report_path):
        """创建最终报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'project_name': comparison_data['project_name'],
            'baseline_dir': baseline_dir,
            'compensated_dir': compensated_dir,
            'output_dir': output_dir,
            'bias_global_improvements': comparison_data['improvements']['bias_global'],
            'files_generated': {
                'total_figures': len([f for f in generated_files if f.endswith('.png')]),
                'analysis_report': md_report_path,
                'all_files': generated_files
            }
        }
        
        # 保存报告文件
        report_path = Path(output_dir) / 'visualization_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        return report
    
    def _log_completion_summary(self, report):
        """记录完成摘要"""
        logger.info(f"✅ 偏置补偿可视化完成!")
        logger.info(f"   输出目录: {report['output_dir']}")
        logger.info(f"   生成图表: {report['files_generated']['total_figures']} 个")
        logger.info(f"   分析报告: {report['files_generated']['analysis_report']}")
