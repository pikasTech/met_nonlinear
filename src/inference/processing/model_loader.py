"""
模型加载模块

负责模型初始化、权重加载和缩放器管理
"""

import os
import sys
import logging
from typing import Optional, Any
from pathlib import Path

from models.base_models import BaseModel
from core.model_engine import ModelEngine

logger = logging.getLogger(__name__)


class ModelLoader:
    """模型加载器类"""
    
    def __init__(self, project_path: str, project_manager=None):
        """
        初始化模型加载器
        
        参数:
            project_path: 模型项目路径
            project_manager: 项目管理器实例（依赖注入）
        """
        self.project_path = project_path
        self.project_name = os.path.basename(project_path)
        self.project_manager = project_manager
        self.model_engine = None
        self.model = None
        self.model_name = None
    
    def initialize_model(self) -> BaseModel:
        """
        初始化模型，包括加载项目管理器和模型引擎
        
        返回:
            BaseModel: 初始化完成的模型实例
        """
        logger.info(f'正在初始化模型: {self.project_name}')
        
        # 项目管理器必须通过依赖注入提供
        if self.project_manager is None:
            raise ValueError(f"项目管理器未提供，无法初始化模型: {self.project_name}")
        
        # 初始化模型引擎
        self.model_engine = ModelEngine(
            self.project_manager, 
            checkpoint_dir=f'{self.project_path}/data'
        )
        
        # 加载缩放器
        self._load_scalers()
        
        # 构建模型
        self.model_engine.build_model()
        
        # 加载权重
        self._load_best_weights()
        
        # 获取模型实例
        self.model = self.model_engine.model_comp
        self.model_name = getattr(self.model, 'model_name', 'Unknown')
        
        logger.info(f'模型初始化完成: {self.model_name}')
        
        return self.model
    
    def _load_scalers(self):
        """加载或创建缩放器"""
        logger.info('尝试加载模型缩放器...')
        scaler_loaded = self.model_engine.load_scalers()
        
        if not scaler_loaded:
            logger.warning('警告: 无法加载缩放器，可能会影响推理结果的准确性')
            try:
                # 添加父目录到系统路径（如果需要）
                parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                if parent_dir not in sys.path:
                    sys.path.insert(0, parent_dir)
                
                from core.data_processing import CombinedScaler
                self.model_engine.scaler = CombinedScaler(feature_range=(-1, 1))
                logger.info('已创建默认集成缩放器（范围 -1 到 1）')
            except ImportError as e:
                raise ImportError(
                    f'无法导入CombinedScaler模块，这是推理所必需的。\n'
                    f'错误详情: {str(e)}\n'
                    f'请确保data_processing模块在正确的位置。'
                ) from e
    
    def _load_best_weights(self):
        """加载模型的最佳权重"""
        try:
            self.model_engine.load_val_best_weights()
            logger.info('已加载验证集最佳权重')
        except Exception as e:
            logger.info(f'加载验证集最佳权重失败: {e}')
            try:
                self.model_engine.load_best_weights()
                logger.info('已加载训练集最佳权重')
            except Exception as e2:
                error_msg = (
                    f'无法加载模型权重，推理无法继续。\n'
                    f'验证集权重错误: {str(e)}\n'
                    f'训练集权重错误: {str(e2)}\n'
                    f'请确保模型已训练并保存了权重文件。'
                )
                raise RuntimeError(error_msg) from e2
    
    def get_model_engine(self) -> ModelEngine:
        """获取模型引擎实例"""
        return self.model_engine
    
    def get_project_manager(self):
        """获取项目管理器实例"""
        if self.project_manager is None:
            raise ValueError("项目管理器未初始化")
        return self.project_manager
    
    def validate_model_config(self) -> bool:
        """
        验证模型配置
        
        返回:
            bool: 配置是否有效
        """
        if not self.model:
            logger.error('模型尚未初始化')
            return False
        
        # 检查必要的属性
        required_attrs = ['predict', 'model_name']
        for attr in required_attrs:
            if not hasattr(self.model, attr):
                logger.error(f'模型缺少必需的属性: {attr}')
                return False
        
        # 检查权重文件
        weights_dir = Path(self.project_path) / 'data'
        if not weights_dir.exists():
            logger.error(f'权重目录不存在: {weights_dir}')
            return False
        
        # 查找权重文件
        weights_files = list(weights_dir.glob('*.weights.*'))
        if not weights_files:
            logger.error(f'未找到权重文件: {weights_dir}')
            return False
        
        logger.info(f'模型配置验证通过')
        return True