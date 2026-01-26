"""
推理管理器模块（重构后）

管理项目的推理数据生成和误差分析功能
"""

import os
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, Optional

from calibration_analyzer.waveprocessor import WaveProcessor
from .data_validator import DataValidator
from .inference_executor import InferenceExecutor
from .error_analyzer import ErrorAnalyzer
from .report_generator import ReportGenerator

logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)


class InferenceManager:
    """
    推理管理器
    
    负责：
    - 生成神经网络推理数据
    - 生成SPICE仿真数据
    - 生成NumPy仿真数据（待实现）
    - 分析推理误差
    - 生成对比报告
    """

    def __init__(self, project_manager):
        """
        初始化推理管理器
        
        参数:
            project_manager: ProjectManager实例
        """
        self.project = project_manager
        self.project_name = project_manager.project_name
        self.project_path = project_manager.project_path
        self.checkpoint_dir = project_manager.checkpoint_dir
        self.config = project_manager.config
        self.wave_processor = WaveProcessor()
        
        # 初始化子模块
        self.validator = DataValidator(
            self.project_path, 
            self.checkpoint_dir, 
            self.config.__dict__
        )
        self.executor = InferenceExecutor(
            self.project_path,
            self.project_name,
            self.config.__dict__,
            self.wave_processor,
            project_manager
        )
        self.analyzer = ErrorAnalyzer(
            self.project_name,
            self.config.__dict__,
            self.wave_processor
        )
        self.reporter = ReportGenerator(self.project_name)
        
        self.quick_mode = False

    def run_inference(self, force=False, quick=False, layers=None):
        """
        运行推理数据生成
        
        参数:
            force: 是否强制重新生成（删除已有数据）
            quick: 是否使用快速模式（只处理最小最大震级）
            layers: 只推理前N层（None表示推理所有层）
        """
        logger.info(f'[INFO] 推理数据生成项目: {self.project_name}')
        if quick:
            logger.info(f'⚡ 快速推理模式：只处理最小和最大震级数据')
        if layers is not None:
            logger.info(f'🔢 部分层推理模式：只推理前 {layers} 层')
        
        # 保存参数供后续使用
        self.quick_mode = quick
        self.executor.set_quick_mode(quick)
        self.executor.set_layers_limit(layers)
        
        # 前置条件验证
        self.validator.validate_inference_prerequisites()
        
        inference_data_dir = f'{self.checkpoint_dir}/inference'
        os.makedirs(inference_data_dir, exist_ok=True)
        
        # 检查已有数据
        has_existing_data = self.validator.check_existing_inference_data(inference_data_dir)
        
        if has_existing_data:
            if force:
                logger.info(f'[DELETE] 强制模式：清除已有推理数据...')
                self._clean_existing_data(inference_data_dir)
            else:
                logger.warning(f'[WARNING] 已存在推理数据。如需重新生成，请使用 -f 参数强制执行')
                logger.warning(f'   python cli.py -i -f {self.project_name}')
                return
        
        logger.info('[START] 开始生成推理数据...')
        try:
            # 查找输入文件
            input_wave = self.validator.find_input_file()
            
            # 执行推理
            self.executor.generate_inference_data(inference_data_dir, input_wave)
            
            logger.info('[SUCCESS] 推理数据生成完成')
        except FileNotFoundError as e:
            logger.error(f'\n[ERROR] 推理失败')
            logger.error(str(e))
            return

    def analyze_errors(self, force=False):
        """
        运行误差分析（要求推理数据已存在）
        
        参数:
            force: 是否强制重新分析（清除已有误差分析结果）
        """
        logger.info(f'[ANALYZE] 误差分析项目: {self.project_name}')
        
        inference_data_dir = f'{self.checkpoint_dir}/inference'
        
        # 检查推理数据是否存在
        if not os.path.exists(inference_data_dir) or \
           not self.validator.check_existing_inference_data(inference_data_dir):
            logger.info(f'[ERROR] 未找到推理数据文件。')
            logger.info(f'[TIP] 请先使用 -i 参数生成推理数据：')
            logger.info(f'   python cli.py -i {self.project_name}')
            raise SystemExit(1)
        
        # 处理强制模式
        if force:
            logger.info(f'[DELETE] 强制模式：清除已有误差分析结果...')
            self._clean_error_analysis_results(inference_data_dir)
        else:
            # 检查是否已有分析结果
            error_analysis_file = os.path.join(inference_data_dir, 'error_analysis.json')
            if os.path.exists(error_analysis_file):
                logger.info(f'[WARNING] 已存在误差分析结果。如需重新分析，请使用 -f 参数强制执行')
                logger.info(f'   python cli.py -a -f {self.project_name}')
                
                # 加载并显示已有结果
                with open(error_analysis_file, 'r') as f:
                    existing_results = json.load(f)
                self.reporter.generate_analysis_report(existing_results, inference_data_dir)
                return
        
        logger.info('[ANALYZE] 开始误差分析...')
        
        # 执行分析
        analysis_results = self.analyzer.analyze_inference_errors(inference_data_dir)
        
        # 生成报告
        self.reporter.generate_analysis_report(analysis_results, inference_data_dir)
        
        logger.info('[SUCCESS] 误差分析完成')

    def _clean_existing_data(self, data_dir: str):
        """清理已有的推理数据"""
        # 删除子目录
        for subdir in ['nn_layers', 'spice_layers', 'numpy_layers', 
                      'nn_spice_error_layers', 'nn_numpy_error_layers']:
            subdir_path = os.path.join(data_dir, subdir)
            if os.path.exists(subdir_path):
                shutil.rmtree(subdir_path)
                logger.info(f'   已删除 {subdir}')
        
        # 删除文件
        for filename in ['input.wave', 'inference_metadata.json', 'error_analysis.json']:
            file_path = os.path.join(data_dir, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f'   已删除 {filename}')

    def _clean_error_analysis_results(self, data_dir: str):
        """清理已有的误差分析结果"""
        # 删除误差目录
        for error_dir in ['nn_spice_error_layers', 'nn_numpy_error_layers']:
            error_dir_path = os.path.join(data_dir, error_dir)
            if os.path.exists(error_dir_path):
                shutil.rmtree(error_dir_path)
                logger.info(f'   已删除 {error_dir}')
        
        # 删除分析文件
        error_analysis_file = os.path.join(data_dir, 'error_analysis.json')
        if os.path.exists(error_analysis_file):
            os.remove(error_analysis_file)
            logger.info(f'   已删除 error_analysis.json')

    # 以下是为了保持向后兼容而保留的方法
    # 它们现在委托给相应的子模块
    
    def _validate_inference_prerequisites(self):
        """验证推理所需的前置条件（委托给validator）"""
        return self.validator.validate_inference_prerequisites()
    
    def _check_existing_inference_data(self, data_dir):
        """检查是否已有推理数据（委托给validator）"""
        return self.validator.check_existing_inference_data(data_dir)
    
    def _find_input_file(self):
        """查找推理输入文件（委托给validator）"""
        return self.validator.find_input_file()
    
    def _generate_inference_data(self, data_dir):
        """生成推理数据（委托给executor）"""
        input_wave = self.validator.find_input_file()
        return self.executor.generate_inference_data(data_dir, input_wave)
    
    def _compute_layer_errors(self, reference_dir, comparison_dir, 
                            error_dir_name, comparison_type, data_dir):
        """计算两个推理结果之间的逐层误差（委托给analyzer）"""
        return self.analyzer.compute_layer_errors(
            reference_dir, comparison_dir, error_dir_name, 
            comparison_type, data_dir
        )
    
    def _analyze_inference_errors(self, data_dir):
        """分析推理误差（委托给analyzer）"""
        return self.analyzer.analyze_inference_errors(data_dir)
    
    def _generate_analysis_report(self, results, data_dir):
        """生成分析报告（委托给reporter）"""
        return self.reporter.generate_analysis_report(results, data_dir)
    
    def _generate_visualization(self, results, data_dir):
        """生成可视化图表（委托给reporter）"""
        return self.reporter.generate_visualization(results, data_dir)
    
    def _combine_layer_outputs(self, layer_outputs, prefix):
        """合并分层输出为单个WaveData（委托给analyzer）"""
        return self.analyzer.combine_layer_outputs(layer_outputs, prefix)
    
    def _get_timestamp(self):
        """获取当前时间戳"""
        import time
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())