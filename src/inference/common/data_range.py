import logging
logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
'\nData range checking utilities.\n\nThis module provides unified data range analysis functionality\nto replace scattered print statements throughout the codebase.\n'
from dataclasses import dataclass
from typing import Optional, Union, List, Tuple
import numpy as np

@dataclass
class DataRangeInfo:
    """统一的数据范围信息"""
    min_value: float
    max_value: float
    mean_value: float
    std_value: float
    shape: Tuple[int, ...]
    dtype: str
    name: str = 'Data'

    def __str__(self) -> str:
        """格式化输出数据范围信息"""
        return f'{self.name} - Shape: {self.shape}, Range: [{self.min_value:.6f}, {self.max_value:.6f}], Mean: {self.mean_value:.6f}, Std: {self.std_value:.6f}'

class DataRangeChecker:
    """数据范围检查工具类"""

    @staticmethod
    def analyze_data(data: Union[np.ndarray, List[np.ndarray]], name: str='Data', verbose: bool=True) -> DataRangeInfo:
        """
        分析数据范围并可选打印
        
        Args:
            data: 输入数据，可以是numpy数组或数组列表
            name: 数据名称，用于打印输出
            verbose: 是否打印详细信息
            
        Returns:
            DataRangeInfo: 数据范围信息
        """
        if isinstance(data, list):
            if not data:
                raise ValueError(f'{name}: 空数据列表')
            all_data = []
            for d in data:
                if isinstance(d, np.ndarray):
                    all_data.append(d.flatten())
                else:
                    all_data.append(np.array(d).flatten())
            data = np.concatenate(all_data)
        else:
            data = np.asarray(data)
        info = DataRangeInfo(min_value=float(np.min(data)), max_value=float(np.max(data)), mean_value=float(np.mean(data)), std_value=float(np.std(data)), shape=data.shape, dtype=str(data.dtype), name=name)
        if verbose:
            logger.info(f'  {name}范围: 最小值={info.min_value:.6f}, 最大值={info.max_value:.6f}')
        return info

    @staticmethod
    def compare_ranges(before: Union[DataRangeInfo, np.ndarray], after: Union[DataRangeInfo, np.ndarray], operation: str='Processing', verbose: bool=True) -> None:
        """
        比较处理前后的数据范围
        
        Args:
            before: 处理前的数据或数据范围信息
            after: 处理后的数据或数据范围信息
            operation: 操作名称
            verbose: 是否打印详细信息
        """
        if isinstance(before, np.ndarray):
            before = DataRangeChecker.analyze_data(before, f'{operation}前', False)
        if isinstance(after, np.ndarray):
            after = DataRangeChecker.analyze_data(after, f'{operation}后', False)
        if verbose:
            logger.info(f'\n{operation}:')
            logger.info(f'  修正前范围: 最小值={before.min_value:.6f}, 最大值={before.max_value:.6f}')
            logger.info(f'  修正后范围: 最小值={after.min_value:.6f}, 最大值={after.max_value:.6f}')
            if before.min_value < 0 and after.min_value >= 0:
                logger.info(f'  注意: 数据从负值修正为正值')

    @staticmethod
    def check_wave_data(wave_data, name: str='WaveData') -> DataRangeInfo:
        """
        检查WaveData对象的数据范围
        
        Args:
            wave_data: WaveData对象
            name: 数据名称
            
        Returns:
            DataRangeInfo: 数据范围信息
        """
        if hasattr(wave_data, 'records') and wave_data.records:
            all_data = []
            for record in wave_data.records:
                all_data.append(record.data.flatten())
            if all_data:
                concatenated = np.concatenate(all_data)
                return DataRangeChecker.analyze_data(concatenated, name)
        if hasattr(wave_data, 'get_single_channel_data'):
            data = wave_data.get_single_channel_data()
            return DataRangeChecker.analyze_data(data, name)
        raise ValueError(f'无法从 {name} 提取数据')

    @staticmethod
    def print_layer_range(layer_index: int, layer_output: np.ndarray, prefix: str='层') -> DataRangeInfo:
        """
        打印层输出的数据范围（用于层级推理）
        
        Args:
            layer_index: 层索引
            layer_output: 层输出数据
            prefix: 前缀文字
            
        Returns:
            DataRangeInfo: 数据范围信息
        """
        name = f'{prefix} {layer_index}'
        return DataRangeChecker.analyze_data(layer_output, name, verbose=True)