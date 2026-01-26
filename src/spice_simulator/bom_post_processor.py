"""
BOM后处理器模块 - 数值标准化和同值合并优化

基于--ultrathink深度分析设计，解决BOM生成中的两个核心问题：
1. 数值格式化：去除末尾无意义的零（5.420k→5.42k）
2. 同值合并：合并相同阻值的电阻（R1,R43,R2合并显示）

设计原则：
- 单一职责：专注BOM后处理，不涉及生成逻辑
- 向后兼容：保持现有接口不变，可选启用
- 完全处理：不过滤任何数据，完整处理所有电阻
- 严格验证：关键操作必须成功，不允许"礼貌失败"
"""

import os
import re
import logging
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class BOMPostProcessor:
    """
    BOM后处理器 - 智能优化BOM格式
    
    功能特性：
    1. 数值标准化：智能去除末尾零，保持有效数字
    2. 同值合并：合并相同阻值电阻，累加数量
    3. Designator排序：智能排序合并后的编号
    4. 格式验证：确保处理后数据完整性
    
    技术实现：
    - 正则表达式精确解析
    - Pandas高效数据处理
    - 完整异常处理机制
    - 详细日志记录
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化BOM后处理器
        
        Args:
            config: 配置字典，包含：
                - enable_standardization: 是否启用数值标准化（默认True）
                - enable_merging: 是否启用同值合并（默认True）
                - sort_designators: 是否排序Designator（默认True）
        """
        self.config = config or {}
        
        # 提取配置参数
        self.enable_standardization = self.config.get('enable_standardization', True)
        self.enable_merging = self.config.get('enable_merging', True)
        self.sort_designators = self.config.get('sort_designators', True)
        
        logger.info(f"BOMPostProcessor initialized: "
                   f"standardization={self.enable_standardization}, "
                   f"merging={self.enable_merging}")
    
    def process(self, bom_df: pd.DataFrame) -> pd.DataFrame:
        """
        主处理流程 - 处理BOM DataFrame
        
        Args:
            bom_df: 输入的BOM DataFrame
            
        Returns:
            处理后的BOM DataFrame
            
        Raises:
            ValueError: DataFrame格式错误或处理失败
        """
        if bom_df.empty:
            logger.warning("Empty BOM DataFrame provided")
            return bom_df
        
        # 验证必需列
        required_columns = ['Designator', 'Value']
        missing_columns = set(required_columns) - set(bom_df.columns)
        if missing_columns:
            raise ValueError(f"BOM missing required columns: {missing_columns}")
        
        # 创建副本避免修改原数据
        result_df = bom_df.copy()
        
        # 步骤1：数值标准化
        if self.enable_standardization:
            logger.info("Applying value standardization...")
            result_df = self._standardize_values(result_df)
        
        # 步骤2：同值合并
        if self.enable_merging:
            logger.info("Merging same-value resistors...")
            result_df = self._merge_same_values(result_df)
        
        # 验证处理结果
        self._validate_result(result_df, bom_df)
        
        logger.info(f"BOM post-processing complete: {len(bom_df)} → {len(result_df)} rows")
        
        return result_df
    
    def process_file(self, 
                    input_path: str, 
                    output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        文件处理接口 - 处理BOM CSV文件
        
        Args:
            input_path: 输入BOM CSV文件路径
            output_path: 输出文件路径（可选，默认覆盖原文件）
            
        Returns:
            处理结果字典
            
        Raises:
            FileNotFoundError: 输入文件不存在
            ValueError: CSV格式错误
        """
        # 验证输入文件
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input BOM file not found: {input_path}")
        
        logger.info(f"Processing BOM file: {input_path}")
        
        # 读取CSV
        try:
            df = pd.read_csv(input_path, encoding='utf-8-sig')
        except Exception as e:
            # 尝试其他编码
            try:
                df = pd.read_csv(input_path, encoding='utf-8')
            except:
                raise ValueError(f"Failed to read BOM CSV: {e}")
        
        # 记录原始统计
        original_stats = {
            'row_count': len(df),
            'unique_values': df['Value'].nunique() if 'Value' in df.columns else 0
        }
        
        # 处理DataFrame
        result_df = self.process(df)
        
        # 确定输出路径
        if output_path is None:
            output_path = input_path.replace('.csv', '_optimized.csv')
        
        # 保存结果（使用utf-8-sig确保Windows兼容性）
        result_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        logger.info(f"Optimized BOM saved to: {output_path}")
        
        # 生成统计报告
        final_stats = {
            'row_count': len(result_df),
            'unique_values': result_df['Value'].nunique() if 'Value' in result_df.columns else 0
        }
        
        return {
            'success': True,
            'input_file': input_path,
            'output_file': output_path,
            'original': original_stats,
            'final': final_stats,
            'reduction': {
                'rows': original_stats['row_count'] - final_stats['row_count'],
                'percentage': ((original_stats['row_count'] - final_stats['row_count']) / 
                              original_stats['row_count'] * 100) if original_stats['row_count'] > 0 else 0
            }
        }
    
    def standardize_resistance_format(self, value_str: str) -> str:
        """
        智能标准化电阻值格式，去除末尾无意义的0
        
        Examples:
            "5.420kΩ ±0.1%" → "5.42kΩ ±0.1%"
            "142.000kΩ ±0.1%" → "142kΩ ±0.1%"
            "1.000MΩ ±0.1%" → "1MΩ ±0.1%"
            "3.300Ω ±0.1%" → "3.3Ω ±0.1%"
            "10.000mΩ ±0.1%" → "10mΩ ±0.1%"
            
        Args:
            value_str: 原始电阻值字符串
            
        Returns:
            标准化后的字符串
        """
        # 解析值和精度部分
        # 支持多种格式：数值+单位+精度
        pattern = r'^([\d.]+)\s*([mkMGTPmunpf]?)(Ω|ohm|R)?\s*(.*?)$'
        match = re.match(pattern, value_str, re.IGNORECASE)
        
        if not match:
            # 无法解析，返回原值
            return value_str
        
        number_str, prefix, unit, tolerance = match.groups()
        
        # 转换为浮点数
        try:
            number = float(number_str)
        except ValueError:
            return value_str
        
        # 智能格式化数值（去除末尾零）
        if number == int(number):
            # 整数不需要小数点
            formatted_number = str(int(number))
        else:
            # 使用Python的默认格式化，自动去除末尾零
            formatted_number = f"{number:g}"
        
        # 规范化单位前缀
        prefix_map = {
            'm': 'm', 'M': 'M', 'k': 'k', 'K': 'k',
            'G': 'G', 'T': 'T', 'P': 'P',
            'u': 'µ', 'n': 'n', 'p': 'p', 'f': 'f'
        }
        normalized_prefix = prefix_map.get(prefix, prefix)
        
        # 确保有单位
        if not unit:
            unit = 'Ω'
        elif unit.lower() in ['ohm', 'r']:
            unit = 'Ω'
        
        # 重新组装
        result = f"{formatted_number}{normalized_prefix}{unit}"
        
        # 添加精度（如果有）
        if tolerance.strip():
            result = f"{result} {tolerance.strip()}"
        
        return result
    
    def _standardize_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        对DataFrame中的Value列进行标准化
        
        Args:
            df: 输入DataFrame
            
        Returns:
            标准化后的DataFrame
        """
        if 'Value' not in df.columns:
            logger.warning("No 'Value' column found for standardization")
            return df
        
        # 应用标准化函数
        df['Value'] = df['Value'].apply(self.standardize_resistance_format)
        
        logger.info(f"Standardized {len(df)} resistance values")
        
        return df
    
    def _merge_same_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        合并相同阻值的电阻
        
        Input:
            Designator  Footprint  Quantity  Value
            R1         R0805      1         1kΩ ±0.1%
            R43        R0805      1         1kΩ ±0.1%
            R2         R0805      1         1kΩ ±0.1%
        
        Output:
            Designator  Footprint  Quantity  Value
            R1,R2,R43  R0805      3         1kΩ ±0.1%
            
        Args:
            df: 输入DataFrame
            
        Returns:
            合并后的DataFrame
        """
        # 按Value和Footprint分组（如果有Footprint列）
        group_columns = ['Value']
        if 'Footprint' in df.columns:
            group_columns.append('Footprint')
        
        # 定义聚合函数
        def merge_designators(designators):
            """合并并排序Designator"""
            # 提取所有designator
            all_designators = []
            for d in designators:
                if ',' in str(d):
                    # 已经是合并的，拆分
                    all_designators.extend(str(d).split(','))
                else:
                    all_designators.append(str(d))
            
            # 排序（智能排序，考虑数字）
            if self.sort_designators:
                all_designators = self._sort_designators(all_designators)
            
            result = ','.join(all_designators)
            
            return result
        
        # 聚合规则
        agg_rules = {
            'Designator': merge_designators,
            'Quantity': 'sum'  # 累加数量
        }
        
        # 保留其他列的第一个值
        for col in df.columns:
            if col not in ['Designator', 'Quantity'] + group_columns:
                agg_rules[col] = 'first'
        
        # 执行分组聚合
        result_df = df.groupby(group_columns, as_index=False).agg(agg_rules)
        
        # 重新排序列（保持原始顺序）
        result_df = result_df[df.columns]
        
        logger.info(f"Merged {len(df)} rows into {len(result_df)} groups")
        
        return result_df
    
    def _sort_designators(self, designators: List[str]) -> List[str]:
        """
        智能排序Designator列表
        
        支持R1, R2, R10的正确排序（数字排序而非字符串排序）
        
        Args:
            designators: Designator列表
            
        Returns:
            排序后的列表
        """
        def extract_number(designator):
            """提取Designator中的数字部分"""
            match = re.search(r'(\d+)', designator)
            if match:
                return int(match.group(1))
            return float('inf')  # 无数字的放最后
        
        # 按数字排序
        return sorted(designators, key=extract_number)
    
    def _validate_result(self, result_df: pd.DataFrame, original_df: pd.DataFrame):
        """
        验证处理结果的完整性
        
        确保：
        1. 总数量保持一致（如果启用合并）
        2. 所有必需列都存在
        3. 没有数据丢失
        
        Args:
            result_df: 处理后的DataFrame
            original_df: 原始DataFrame
            
        Raises:
            ValueError: 验证失败
        """
        # 验证列完整性
        missing_columns = set(original_df.columns) - set(result_df.columns)
        if missing_columns:
            raise ValueError(f"Columns lost during processing: {missing_columns}")
        
        # 验证数量一致性（如果有Quantity列且启用了合并）
        if 'Quantity' in result_df.columns and self.enable_merging:
            original_total = original_df['Quantity'].sum() if 'Quantity' in original_df.columns else len(original_df)
            result_total = result_df['Quantity'].sum()
            
            if not np.isclose(original_total, result_total):
                raise ValueError(
                    f"Quantity mismatch after merging: "
                    f"original={original_total}, result={result_total}"
                )
        
        # 验证没有NaN值产生
        if result_df.isnull().any().any():
            nan_columns = result_df.columns[result_df.isnull().any()].tolist()
            logger.warning(f"NaN values detected in columns: {nan_columns}")
    
    def update_config(self, **kwargs):
        """
        更新配置参数
        
        Args:
            **kwargs: 配置参数键值对
        """
        self.config.update(kwargs)
        
        # 更新实例属性
        self.enable_standardization = self.config.get('enable_standardization', self.enable_standardization)
        self.enable_merging = self.config.get('enable_merging', self.enable_merging)
        self.sort_designators = self.config.get('sort_designators', self.sort_designators)
        
        logger.info(f"BOM post-processor config updated: {kwargs}")


# 便捷函数
def optimize_bom(input_path: str, output_path: Optional[str] = None, **config) -> Dict[str, Any]:
    """
    便捷函数 - 优化BOM文件
    
    Args:
        input_path: 输入BOM文件路径
        output_path: 输出文件路径（可选）
        **config: 配置参数
        
    Returns:
        处理结果字典
    """
    processor = BOMPostProcessor(config)
    return processor.process_file(input_path, output_path)