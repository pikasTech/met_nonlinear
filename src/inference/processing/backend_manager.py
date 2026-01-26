"""
后端管理模块

负责推理后端的初始化、切换和管理
"""

import os
import shutil
import logging
from typing import List, Optional, Type

from models.layer_support import LayeredModelSupport
from ..backends.base import InferenceBackend
from ..backends.timeseries_backend import TimeSeriesBackend
from ..backends.batch_backend import BatchPredictBackend
from ..backends.layered_backend import LayerByLayerBackend
from ..backends.spice.backend import SPICEBackend

logger = logging.getLogger(__name__)


class BackendManager:
    """后端管理器类"""
    
    def __init__(self, model: LayeredModelSupport, config=None, project_path=None):
        """
        初始化后端管理器
        
        参数:
            model: 模型实例
            config: 配置对象，包含inference_config等信息
            project_path: 项目路径，用于生成项目特定的输出路径
        """
        self.model = model
        self.model_name = getattr(model, 'model_name', 'Unknown')
        self.backend = None
        self.backend_type = None
        self.config = config
        self.project_path = project_path
    
    def initialize_backend(self, backend_type: str) -> InferenceBackend:
        """
        初始化推理后端
        
        参数:
            backend_type: 后端类型，例如 'time_series'、'batch_predict'、'layer_by_layer' 或 'spice'
            
        返回:
            InferenceBackend: 初始化的后端实例
        """
        logger.info(f'正在初始化推理后端: {backend_type}')
        
        backend_type_lower = backend_type.lower()
        
        if backend_type_lower == 'time_series':
            self.backend = TimeSeriesBackend(self.model)
        elif backend_type_lower == 'batch_predict':
            self.backend = BatchPredictBackend(self.model, batch_size=32)
        elif backend_type_lower == 'layer_by_layer':
            self._validate_layered_support()
            self.backend = LayerByLayerBackend(self.model)
        elif backend_type_lower == 'spice':
            self._validate_layered_support()
            self.backend = self._create_spice_backend()
        else:
            available = self.get_available_backends()
            raise ValueError(
                f'不支持的后端类型: {backend_type}，'
                f'可用的后端类型有: {available}'
            )
        
        self.backend_type = backend_type
        logger.info(f'推理后端初始化完成: {self.backend.__class__.__name__}')
        
        return self.backend
    
    def switch_backend(self, new_backend_type: str) -> InferenceBackend:
        """
        切换推理后端类型
        
        参数:
            new_backend_type: 新的后端类型名称
            
        返回:
            InferenceBackend: 新的后端实例
            
        [WARNING] 重要安全说明 [WARNING]
        此方法必须确保后端切换的原子性。如果切换失败，必须保持原有状态不变。
        绝对不允许出现后端类型与实际后端不匹配的情况。
        """
        if new_backend_type == self.backend_type:
            logger.info(f'当前已使用该后端类型: {new_backend_type}')
            return self.backend
        
        # 保存当前状态
        old_backend = self.backend
        old_backend_type = self.backend_type
        
        try:
            # 初始化新后端
            new_backend = self.initialize_backend(new_backend_type)
            
            # 验证后端类型匹配
            self._validate_backend_type_match(new_backend_type, new_backend)
            
            logger.info(f'已切换为后端类型: {new_backend_type}')
            logger.info(f'[BackendManager] 后端验证: {new_backend.__class__.__name__} 符合 {new_backend_type}')
            
            return new_backend
            
        except Exception as e:
            # 回滚到原始状态
            logger.info('\n' + '=' * 60)
            logger.info('[ERROR] 后端切换失败，回滚到原始状态')
            logger.info('=' * 60)
            
            self.backend = old_backend
            self.backend_type = old_backend_type
            
            logger.info(f'已恢复到后端: {old_backend_type} ({old_backend.__class__.__name__})')
            raise
    
    def get_available_backends(self) -> List[str]:
        """
        获取可用的后端类型列表
        
        返回:
            List[str]: 可用的后端类型列表
        """
        return ['time_series', 'batch_predict', 'layer_by_layer', 'spice']
    
    def get_current_backend(self) -> Optional[InferenceBackend]:
        """获取当前后端实例"""
        return self.backend
    
    def get_current_backend_type(self) -> Optional[str]:
        """获取当前后端类型"""
        return self.backend_type
    
    def _validate_layered_support(self):
        """验证模型是否支持分层推理"""
        if not isinstance(self.model, LayeredModelSupport):
            raise ValueError(
                f'模型 {self.model_name} 不支持分层推理，'
                f'它没有实现LayeredModelSupport接口'
            )
    
    def _create_spice_backend(self) -> InferenceBackend:
        """创建SPICE后端"""
        # 智能路径生成：优先使用项目路径，回退到temp目录
        output_folder = self._generate_spice_output_path()
        os.makedirs(output_folder, exist_ok=True)
        
        try:
            # 只传递需要的inference_config部分，而不是整个config
            inference_config = getattr(self.config, 'inference_config', {}) if self.config else {}
            
            backend_class = self._get_spice_backend_class()
            if backend_class:
                backend = backend_class(self.model, output_folder=output_folder, inference_config=inference_config)
            else:
                backend = SPICEBackend(self.model, output_folder=output_folder, inference_config=inference_config)
                logger.info('已选择通用SPICE后端')
            
            return backend
            
        except ImportError as e:
            logger.info('\n' + '=' * 60)
            logger.error('错误：SPICE后端初始化失败')
            logger.info('=' * 60)
            raise RuntimeError(
                f'无法初始化SPICE后端: {str(e)}\n'
                f'请确保在正确的环境中运行，或者选择其他后端类型'
            ) from e
    
    def _generate_spice_output_path(self) -> str:
        """
        生成SPICE输出路径
        
        策略：
        1. 如果有project_path，使用项目的data/spice_netlists目录（直接覆盖）
        2. 否则使用相对于当前工作目录的data目录
        
        返回:
            str: SPICE输出目录路径
        """
        if self.project_path:
            # 项目特定的网表目录（简化版，直接使用主目录）
            spice_netlists_dir = os.path.join(self.project_path, 'data', 'spice_netlists')
            logger.info(f"使用项目特定的SPICE网表目录: {spice_netlists_dir}")
            return spice_netlists_dir
        else:
            # 使用相对于当前工作目录的data目录
            logger.info("项目路径未指定，使用默认data目录")
            return os.path.join('data', 'spice_netlists')
    
    
    def _get_spice_backend_class(self) -> Optional[Type[InferenceBackend]]:
        """
        根据模型类型获取对应的SPICE后端类
        
        返回:
            class: 对应的SPICE后端类，如果没有专用后端则返回None
        """
        if hasattr(self.model, 'model_name'):
            model_name = self.model.model_name
            logger.info(f'[DETECT] 检测到模型类型: {model_name}')
            
            if model_name == 'WaveNet5':
                from ..wavenet5_spice_backend import WaveNet5SPICEBackend
                logger.info('[OK] 选择WaveNet5专用SPICE后端')
                return WaveNet5SPICEBackend
            elif model_name == 'WaveNet6':
                logger.info(f'[INFO] 模型 {model_name} 暂无专用后端，使用通用后端')
            else:
                logger.info(f'📋 模型 {model_name} 使用通用SPICE后端')
        else:
            logger.info('📋 模型没有model_name属性，使用通用SPICE后端')
        
        return None
    
    def _validate_backend_type_match(self, expected_type: str, backend: InferenceBackend):
        """验证后端实例与期望类型是否匹配"""
        backend_class_name = backend.__class__.__name__.lower()
        
        if expected_type == 'spice' and 'spice' not in backend_class_name:
            raise RuntimeError(
                f'后端切换验证失败：请求SPICE后端，'
                f'但得到{backend.__class__.__name__}'
            )
        elif expected_type == 'layer_by_layer' and 'layer' not in backend_class_name:
            raise RuntimeError(
                f'后端切换验证失败：请求layer_by_layer后端，'
                f'但得到{backend.__class__.__name__}'
            )