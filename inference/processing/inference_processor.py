"""
核心推理处理器模块

此模块包含InferenceProcessor的核心功能，负责协调模型加载、后端管理和数据处理。
"""

import logging
from typing import Union, Optional, Dict, Any, List

from calibration_analyzer.waveprocessor import WaveProcessor
from models.layer_support import LayeredModelSupport

from .model_loader import ModelLoader
from .backend_manager import BackendManager
from .data_filter import DataFilter

logger = logging.getLogger(__name__)


class InferenceProcessor:
    """
    模型推理处理器类，用于加载模型并进行推理
    
    功能：
    1. 从项目路径加载模型
    2. 从wave文件读取输入数据
    3. 使用选定的后端进行推理
    4. 将推理结果保存为wave文件
    """
    
    def __init__(self, project_path: str, project_manager=None, backend_type: str = 'batch_predict', 
                 quick_mode: bool = False):
        """
        初始化推理处理器
        
        参数:
            project_path: 模型项目路径，例如 'projects/WNET5q0.5h2u6l4'
            project_manager: 项目管理器实例（依赖注入）
            backend_type: 后端类型，默认为 'batch_predict'
            quick_mode: 是否使用快速模式（只处理最小最大震级）
        """
        self.project_path = project_path
        self.backend_type = backend_type
        self.quick_mode = quick_mode
        
        # 初始化各组件
        self.wave_processor = WaveProcessor()
        self.model_loader = ModelLoader(project_path, project_manager)
        self.data_filter = DataFilter(self.wave_processor, quick_mode)
        
        # 初始化模型
        self.model: LayeredModelSupport = self.model_loader.initialize_model()
        self.model_name = self.model_loader.model_name
        self.project_name = self.model_loader.project_name
        self.project_manager = self.model_loader.get_project_manager()
        self.model_engine = self.model_loader.get_model_engine()
        
        # 初始化后端管理器
        self.backend_manager = BackendManager(
            self.model, 
            config=self.project_manager.config if self.project_manager else None,
            project_path=self.project_path
        )
        self.backend = self.backend_manager.initialize_backend(backend_type)
        
        # 延迟加载的组件
        self._visualizer = None
        self._data_processor = None
        self._spice_analyzer = None
    
    @property
    def visualizer(self):
        """延迟加载可视化器"""
        if self._visualizer is None:
            from ..visualization import InferenceVisualizer
            self._visualizer = InferenceVisualizer(self)
        return self._visualizer
    
    @property
    def data_processor(self):
        """延迟加载数据处理器"""
        if self._data_processor is None:
            from ..data_processing import InferenceDataProcessor
            self._data_processor = InferenceDataProcessor(self)
        return self._data_processor
    
    @property
    def spice_analyzer(self):
        """延迟加载SPICE分析器"""
        if self._spice_analyzer is None:
            from ..spice_analysis import SPICEAnalyzer
            self._spice_analyzer = SPICEAnalyzer(self)
        return self._spice_analyzer
    
    def get_available_backends(self) -> List[str]:
        """
        获取可用的后端类型列表
        
        返回:
            List[str]: 可用的后端类型列表
        """
        return self.backend_manager.get_available_backends()
    
    def set_backend(self, backend_type: str):
        """
        设置推理后端类型
        
        参数:
            backend_type: 后端类型名称
        """
        self.backend = self.backend_manager.switch_backend(backend_type)
        self.backend_type = backend_type
    
    # === 数据处理相关方法（委托给data_processor）===
    
    def load_input_wave(self, wave_file_path: str):
        """委托给data_processor"""
        return self.data_processor.load_input_wave(wave_file_path)
    
    def save_output_wave(self, output_wave_data, output_file_path: str, 
                        compress: bool = True):
        """委托给data_processor"""
        return self.data_processor.save_output_wave(
            output_wave_data, output_file_path, compress
        )
    
    def infer_and_save(self, input_wave_path: str, output_wave_path: str = None, 
                      layer_output_dir: str = None, use_scaler=False, **kwargs):
        """委托给data_processor（支持新旧参数）"""
        return self.data_processor.infer_and_save(
            input_wave_path, output_wave_path, layer_output_dir, use_scaler, **kwargs
        )
    
    # === 可视化相关方法（委托给visualizer）===
    
    def visualize_results(self, input_wave_path: str, output_wave_path: str, 
                         max_samples: int = 5):
        """委托给visualizer"""
        return self.visualizer.visualize_results(
            input_wave_path, output_wave_path, max_samples
        )
    
    def visualize_layer_results(self, input_wave_path: str, layer_dir: str, 
                               max_samples: int = 2, max_channels: int = 8):
        """委托给visualizer"""
        return self.visualizer.visualize_layer_results(
            input_wave_path, layer_dir, max_samples, max_channels
        )
    
    def compare_layer_with_direct_output(self, input_wave_path: str, layer_dir: str, 
                                       direct_output_path: str, max_samples: int = 2):
        """委托给visualizer"""
        return self.visualizer.compare_layer_with_direct_output(
            input_wave_path, layer_dir, direct_output_path, max_samples
        )
    
    # === SPICE分析相关方法（委托给spice_analyzer）===
    
    def generate_spice_comparison_data(self, input_wave_path: str, 
                                     output_dir: str = 'data/spice_comparison', 
                                     use_scaler: bool = False):
        """委托给spice_analyzer"""
        return self.spice_analyzer.generate_spice_comparison_data(
            input_wave_path, output_dir, use_scaler
        )
    
    def analyze_spice_comparison(self, comparison_dir: str):
        """委托给spice_analyzer"""
        return self.spice_analyzer.analyze_spice_comparison(comparison_dir)
    
    def get_spice_comparison_paths(self, comparison_dir: str):
        """委托给spice_analyzer"""
        return self.spice_analyzer.get_spice_comparison_paths(comparison_dir)
    
    # === 工具方法 ===
    
    def get_layer_paths(self, layer_dir: str):
        """委托给utils模块的函数"""
        from ..utils import get_layer_paths
        return get_layer_paths(layer_dir)
    
    def _load_wave_data_with_filter(self, wave_path: str):
        """
        加载wave数据，支持快速模式筛选
        
        参数:
            wave_path: wave文件路径
            
        返回:
            WaveData: 加载的wave数据，如果是快速模式则只包含最小最大震级
        """
        return self.data_filter.load_wave_data_with_filter(wave_path)
    
    def _filter_min_max_magnitude(self, wave_data):
        """
        从wave数据中筛选最小和最大震级的记录
        
        参数:
            wave_data: 原始WaveData对象
            
        返回:
            WaveData: 筛选后的WaveData对象，只包含最小最大震级
        """
        return self.data_filter.filter_min_max_magnitude(wave_data)