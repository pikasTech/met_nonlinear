"""电阻标准化模块"""
import numpy as np
import pandas as pd
from typing import List, Dict, Union

class ResistanceStandardizer:
    """电阻值标准化器"""
    
    # 标准电阻系列
    E6_VALUES = [1.0, 1.5, 2.2, 3.3, 4.7, 6.8]
    
    E12_VALUES = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]
    
    E24_VALUES = [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
                  3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1]
    
    # E96系列（1%精度）
    E96_VALUES = [
        1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30,
        1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54, 1.58, 1.62, 1.65, 1.69, 1.74,
        1.78, 1.82, 1.87, 1.91, 1.96, 2.00, 2.05, 2.10, 2.15, 2.21, 2.26, 2.32,
        2.37, 2.43, 2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09,
        3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12,
        4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49,
        5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65, 6.81, 6.98, 7.15, 7.32,
        7.50, 7.68, 7.87, 8.06, 8.25, 8.45, 8.66, 8.87, 9.09, 9.31, 9.53, 9.76
    ]
    
    # E192系列（0.5%精度）- 192个值
    E192_VALUES = [
        1.00, 1.01, 1.02, 1.04, 1.05, 1.06, 1.07, 1.09, 1.10, 1.11, 1.13, 1.14,
        1.15, 1.17, 1.18, 1.20, 1.21, 1.23, 1.24, 1.26, 1.27, 1.29, 1.30, 1.32,
        1.33, 1.35, 1.37, 1.38, 1.40, 1.42, 1.43, 1.45, 1.47, 1.49, 1.50, 1.52,
        1.54, 1.56, 1.58, 1.60, 1.62, 1.64, 1.65, 1.67, 1.69, 1.72, 1.74, 1.76,
        1.78, 1.80, 1.82, 1.84, 1.87, 1.89, 1.91, 1.93, 1.96, 1.98, 2.00, 2.03,
        2.05, 2.08, 2.10, 2.13, 2.15, 2.18, 2.21, 2.23, 2.26, 2.29, 2.32, 2.34,
        2.37, 2.40, 2.43, 2.46, 2.49, 2.52, 2.55, 2.58, 2.61, 2.64, 2.67, 2.71,
        2.74, 2.77, 2.80, 2.84, 2.87, 2.91, 2.94, 2.98, 3.01, 3.05, 3.09, 3.12,
        3.16, 3.20, 3.24, 3.28, 3.32, 3.36, 3.40, 3.44, 3.48, 3.52, 3.57, 3.61,
        3.65, 3.70, 3.74, 3.79, 3.83, 3.88, 3.92, 3.97, 4.02, 4.07, 4.12, 4.17,
        4.22, 4.27, 4.32, 4.37, 4.42, 4.48, 4.53, 4.59, 4.64, 4.70, 4.75, 4.81,
        4.87, 4.93, 4.99, 5.05, 5.11, 5.17, 5.23, 5.30, 5.36, 5.42, 5.49, 5.56,
        5.62, 5.69, 5.76, 5.83, 5.90, 5.97, 6.04, 6.12, 6.19, 6.26, 6.34, 6.42,
        6.49, 6.57, 6.65, 6.73, 6.81, 6.90, 6.98, 7.06, 7.15, 7.23, 7.32, 7.41,
        7.50, 7.59, 7.68, 7.77, 7.87, 7.96, 8.06, 8.16, 8.25, 8.35, 8.45, 8.56,
        8.66, 8.76, 8.87, 8.98, 9.09, 9.19, 9.31, 9.42, 9.53, 9.65, 9.76, 9.88
    ]
    
    SERIES = {
        'E6': E6_VALUES,
        'E12': E12_VALUES,
        'E24': E24_VALUES,
        'E96': E96_VALUES,
        'E192': E192_VALUES
    }
    
    def standardize(self, value: float, series: str = 'E96') -> float:
        """
        将电阻值标准化到指定系列
        
        Args:
            value: 原始电阻值
            series: 标准系列名称
            
        Returns:
            标准化后的电阻值
        """
        # 特殊值处理
        if value <= 0:
            return value
        if value >= 1e9:  # MAX_RESISTANCE
            return 1e9
        if value == float('inf'):
            return float('inf')
            
        # 计算数量级
        exponent = np.floor(np.log10(value))
        mantissa = value / (10 ** exponent)
        
        # 查找最接近的标准值
        standard_values = self.SERIES.get(series, self.E96_VALUES)
        closest = min(standard_values, key=lambda x: abs(x - mantissa))
        
        return closest * (10 ** exponent)
    
    def standardize_batch(self, values: List[float], series: List[str] = None) -> Dict[str, List[float]]:
        """
        批量标准化，支持多个系列
        
        Args:
            values: 电阻值列表
            series: 标准系列列表，默认使用E96和E24
            
        Returns:
            字典，键为系列名称，值为标准化后的电阻值列表
        """
        if series is None:
            series = ['E96', 'E24']
        
        results = {}
        for s in series:
            results[s] = [self.standardize(v, s) for v in values]
        
        return results
    
    def standardize_dataframe(self, df: pd.DataFrame, 
                            value_column: str = 'value',
                            series_list: List[str] = None) -> pd.DataFrame:
        """
        批量标准化DataFrame中的电阻值
        
        Args:
            df: 包含电阻值的DataFrame
            value_column: 电阻值列名
            series_list: 要生成的标准系列列表
            
        Returns:
            添加了标准化列的DataFrame
        """
        if series_list is None:
            series_list = ['E96', 'E24']
        
        df = df.copy()
        
        for series in series_list:
            col_name = f'Standardized_{series}'
            df[col_name] = df[value_column].apply(
                lambda x: self.standardize(x, series)
            )
            
            # 计算误差
            df[f'Error_{series}_pct'] = np.where(
                df[value_column] != 0,
                np.abs((df[col_name] - df[value_column]) / df[value_column] * 100),
                0
            )
        
        return df
    
    def analyze_errors(self, original: pd.Series, 
                       standardized: pd.Series) -> Dict:
        """
        分析标准化误差 - 只计算相对误差，完全校验覆盖
        
        Args:
            original: 原始值序列
            standardized: 标准化后的值序列
            
        Returns:
            相对误差分析结果字典
        """
        # 移除绝对值过滤，保留必要的无效值过滤
        mask = (original != 0) & (original != float('inf')) & (standardized != float('inf')) & (~np.isnan(original)) & (~np.isnan(standardized))
        original_filtered = original[mask]
        standardized_filtered = standardized[mask]
        
        if len(original_filtered) == 0:
            return {
                'total_resistors': len(original),
                'validated_resistors': 0,
                'mean_relative_error': 0,
                'max_relative_error': 0,
                'within_1pct': 100.0,
                'within_5pct': 100.0,
                'within_10pct': 100.0
            }
        
        # 只计算相对误差，不计算绝对误差
        relative_errors = np.where(
            original_filtered != 0,
            np.abs(standardized_filtered - original_filtered) / original_filtered * 100,
            0
        )
        
        # 只返回相对误差统计
        return {
            'total_resistors': len(original),
            'validated_resistors': len(original_filtered),
            'mean_relative_error': float(relative_errors.mean()),
            'max_relative_error': float(relative_errors.max()),
            'within_1pct': float((relative_errors < 1).sum() / len(relative_errors) * 100),
            'within_5pct': float((relative_errors < 5).sum() / len(relative_errors) * 100),
            'within_10pct': float((relative_errors < 10).sum() / len(relative_errors) * 100)
        }
    
    def get_series_info(self, series: str = 'E96') -> Dict:
        """
        获取标准系列信息
        
        Args:
            series: 系列名称
            
        Returns:
            系列信息字典
        """
        series_tolerance = {
            'E6': 20,   # ±20%
            'E12': 10,  # ±10%
            'E24': 5,   # ±5%
            'E96': 1,   # ±1%
            'E192': 0.5 # ±0.5%
        }
        
        return {
            'name': series,
            'values': self.SERIES.get(series, []),
            'count': len(self.SERIES.get(series, [])),
            'tolerance_pct': series_tolerance.get(series, 0),
            'description': f"{series} series with ±{series_tolerance.get(series, 0)}% tolerance"
        }