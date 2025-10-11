"""电阻值提取器模块 - 重构为统一架构"""
import os
import pandas as pd
import logging
import numpy as np
from typing import List, Dict, Optional
from inference.processing.model_loader import ModelLoader
from core.project_manager import ProjectManager
from spice_simulator.unified_resistance_calculator import UnifiedResistanceCalculator, ResistanceConsistencyValidator

logger = logging.getLogger(__name__)

class ResistanceExtractor:
    """
    电阻值提取器 - 基于统一核心架构
    
    设计原则：
    1. 统一数据源: 所有电阻计算通过UnifiedResistanceCalculator
    2. 强制验证: 每次提取都验证与网表生成的一致性
    3. 配置统一: 使用与网表生成完全相同的inference_config
    4. 失败即停: 不一致或错误立即抛SystemError
    
    NO COMPENSATION: 不使用补偿，通过统一核心解决一致性
    NO ROLLBACK: 计算失败或验证失败直接报错
    CRITICAL: 一致性验证不可跳过
    """
    
    def __init__(self, project_path: str, inference_config: Dict = None):
        self.project_path = project_path
        self.project_manager = ProjectManager(project_path)
        self.model_loader = ModelLoader(project_path, self.project_manager)
        
        # 统一核心组件
        self.unified_calculator = None
        self.consistency_validator = ResistanceConsistencyValidator(tolerance_percent=0.01)
        
        # 配置管理
        self.inference_config = inference_config or {}
        
        # 结果存储
        self.resistance_data = []
        self.validation_enabled = True  # 强制启用验证
        
        logger.info("ResistanceExtractor initialized with unified architecture")
        logger.info(f"Inference config provided: {bool(inference_config)}")
    
    def extract_from_model(self, skip_non_dense: bool = True) -> List[Dict]:
        """
        基于统一核心架构的电阻值提取
        
        统一架构特性：
        1. 使用UnifiedResistanceCalculator作为唯一计算来源
        2. 自动应用与网表生成相同的inference_config
        3. 强制验证与网表数据的一致性
        4. 任何不一致都会抛出SystemError
        
        Args:
            skip_non_dense: 是否跳过非Dense层（此参数已由统一核心处理）
            
        Returns:
            电阻值记录列表（已通过一致性验证）
            
        Raises:
            ValueError: 模型加载或计算失败
            SystemError: 数据一致性验证失败
        """
        logger.info("开始基于统一架构的电阻值提取")
        
        # 加载模型 - 不隐藏错误
        model_wrapper = self.model_loader.initialize_model()
        if model_wrapper is None:
            raise ValueError(f"Failed to load model from {self.project_path}")
        
        # 验证模型结构
        if not hasattr(model_wrapper, 'layer_to_layer_models'):
            raise ValueError("Model must have layer_to_layer_models attribute for unified architecture")
        
        # 创建统一电阻计算核心
        logger.info("初始化UnifiedResistanceCalculator")
        self.unified_calculator = UnifiedResistanceCalculator(
            model=model_wrapper,
            inference_config=self.inference_config
        )
        
        # 执行统一电阻计算
        logger.info("执行统一电阻计算")
        try:
            resistance_data_by_layer = self.unified_calculator.calculate_all_layer_resistances()
        except Exception as e:
            logger.error(f"统一电阻计算失败: {e}")
            raise ValueError(f"Unified resistance calculation failed: {e}")
        
        # 执行强制一致性验证
        logger.info("执行强制一致性验证")
        try:
            self.consistency_validator.validate_consistency_or_fail(self.unified_calculator)
        except SystemError as e:
            logger.error(f"一致性验证失败: {e}")
            raise  # 直接向上抛出SystemError
        except Exception as e:
            logger.error(f"验证过程出错: {e}")
            raise ValueError(f"Consistency validation error: {e}")
        
        # 获取验证通过的扁平化数据
        self.resistance_data = self.unified_calculator.get_flattened_resistance_data()
        
        logger.info(f"统一架构电阻提取成功: {len(self.resistance_data)} 个电阻值，已通过一致性验证")
        return self.resistance_data
    
    def get_inference_config(self) -> Dict:
        """获取当前使用的推理配置"""
        return self.inference_config.copy()
    
    def set_inference_config(self, inference_config: Dict):
        """设置推理配置（必须在extract_from_model之前调用）"""
        self.inference_config = inference_config or {}
        logger.info("Updated inference_config")
        
        # 如果已经有统一计算器实例，需要重新初始化
        if self.unified_calculator is not None:
            logger.warning("Reinitializing UnifiedResistanceCalculator with new config")
            self.unified_calculator = None
    def extract_from_netlists(self, netlist_dir: str) -> List[Dict]:
        """
        从已有网表文件提取（暂未实现，建议使用统一架构）
        
        注意：此方法不使用统一架构，可能导致数据不一致。
        建议使用extract_from_model()配合适当的inference_config。
        """
        logger.warning("extract_from_netlists不使用统一架构，可能导致数据不一致")
        logger.warning("建议使用extract_from_model()配合inference_config")
        
        if not os.path.exists(netlist_dir):
            raise ValueError(f"Netlist directory does not exist: {netlist_dir}")
        
        # 解析网表实现...
        raise NotImplementedError("Netlist parsing not yet implemented - use extract_from_model() instead")
    
    def to_dataframe(self) -> pd.DataFrame:
        """转换为DataFrame"""
        if not self.resistance_data:
            raise ValueError("No resistance data to convert")
        return pd.DataFrame(self.resistance_data)
    
    def save_csv(self, output_path: str):
        """
        保存到CSV文件
        
        # NO ROLLBACK: 保存失败直接报错
        """
        df = self.to_dataframe()
        
        # 确保目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # 直接保存，失败则报错
        df.to_csv(output_path, index=False)
        logger.info(f"Saved {len(df)} resistance values to {output_path}")
        return output_path