"""SPICE文件路径管理器"""
import os
from typing import Optional

class SPICEPathManager:
    """统一管理SPICE相关文件路径"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.data_dir = os.path.join(project_path, 'data')
        
        # 定义各类文件的目录
        self.netlist_dir = os.path.join(self.data_dir, 'spice_netlists')
        self.resistance_dir = os.path.join(self.data_dir, 'resistance_tables')
        
        # 确保目录存在
        self._ensure_directories()
    
    def _ensure_directories(self):
        """创建必要的目录"""
        for dir_path in [self.netlist_dir, self.resistance_dir]:
            os.makedirs(dir_path, exist_ok=True)
    
    def get_netlist_path(self, layer_index: int, 
                         layer_type: str = 'dense') -> str:
        """获取网表文件路径"""
        filename = f'layer{layer_index}_{layer_type}.cir'
        return os.path.join(self.netlist_dir, filename)
    
    def get_resistance_csv_path(self, layer_index: Optional[int] = None,
                                suffix: str = '') -> str:
        """
        获取电阻CSV文件路径
        
        Args:
            layer_index: 层索引，None表示汇总文件
            suffix: 文件名后缀（如'_standardized_E96'）
        """
        if layer_index is None:
            filename = f'all_layers_resistances{suffix}.csv'
        else:
            filename = f'layer{layer_index}_resistances{suffix}.csv'
        
        return os.path.join(self.resistance_dir, filename)
    
    def get_analysis_report_path(self) -> str:
        """获取分析报告路径"""
        return os.path.join(self.resistance_dir, 'standardization_analysis.json')
    
    def clean_temp_files(self):
        """清理临时网表文件（保留功能但不再需要）"""
        # 网表文件现在存储在项目data目录，不需要清理
        import logging
        logger = logging.getLogger(__name__)
        logger.debug("网表文件现已持久化存储，无需清理")
        pass