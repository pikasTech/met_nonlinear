"""
权重电阻BOM生成器模块

用于从完整的电阻CSV文件中提取权重电阻，并生成符合制造要求的BOM格式CSV文件。

功能特性：
1. 筛选权重电阻（type='weight'）
2. 重新编号符号（R1, R2, ...）
3. 添加BOM必需字段（封装、精度）
4. 支持可配置的封装和精度规格
"""

import os
import logging
import pandas as pd
from typing import Dict, Any, Optional
from .bom_post_processor import BOMPostProcessor

logger = logging.getLogger(__name__)


class WeightResistorBOMGenerator:
    """
    权重电阻BOM生成器
    
    从完整的电阻CSV中提取权重电阻，生成制造用BOM表格。
    
    设计原则：
    - 作为后处理步骤，不改变原有导出流程
    - 保持数据完整性和可追溯性
    - 支持灵活的配置选项
    """
    
    def __init__(self, bom_config: Optional[Dict[str, Any]] = None):
        """
        初始化BOM生成器
        
        Args:
            bom_config: BOM配置字典，包含：
                - package: 封装规格（默认"0805"）
                - tolerance: 精度规格（默认"1%"）
                - include_original_name: 是否包含原始名称（默认False）
        """
        self.bom_config = bom_config or {}
        
        # 提取配置参数
        self.package = self.bom_config.get('bom_package', '0805')
        self.tolerance = self.bom_config.get('bom_tolerance', '1%')
        self.include_original_name = self.bom_config.get('include_original_name', False)
        
        # 新增：编号模式配置
        self.numbering_mode = self.bom_config.get('numbering_mode', 'sequential')
        # 'sequential': 原有的顺序编号
        # 'grouped': 新的分组编号（R1偏置正，R2-R7输入正，R8偏置负，R9-R14输入负）
        
        logger.info(f"WeightResistorBOMGenerator initialized with config: "
                   f"package={self.package}, tolerance={self.tolerance}, "
                   f"numbering={self.numbering_mode}")
    
    def generate_bom_from_csv(self, 
                             input_csv_path: str, 
                             output_csv_path: Optional[str] = None) -> Dict[str, Any]:
        """
        从完整CSV生成权重电阻BOM
        
        Args:
            input_csv_path: 输入的完整电阻CSV文件路径
            output_csv_path: 输出的BOM CSV文件路径（可选）
            
        Returns:
            Dict包含：
                - success: 是否成功
                - count: 权重电阻数量
                - output_file: 输出文件路径
                - summary: 统计信息
                
        Raises:
            FileNotFoundError: 输入文件不存在
            ValueError: CSV格式错误或无权重电阻
        """
        # 验证输入文件
        if not os.path.exists(input_csv_path):
            raise FileNotFoundError(f"Input CSV file not found: {input_csv_path}")
        
        logger.info(f"Reading CSV from: {input_csv_path}")
        
        # 读取完整CSV
        try:
            df = pd.read_csv(input_csv_path)
        except Exception as e:
            raise ValueError(f"Failed to read CSV file: {e}")
        
        # 验证必需列
        required_columns = ['type', 'value', 'name']
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(f"CSV missing required columns: {missing_columns}")
        
        # 筛选权重电阻 - 神经网络权重在SPICE中对应input和bias电阻
        logger.info("Filtering weight resistors (including bias)...")
        weight_df = df[df['type'].isin(['input_pos', 'input_neg', 'bias_pos', 'bias_neg'])].copy()
        
        # 统计开路电阻但不排除（差分电路需要完整的电阻对）
        initial_count = len(weight_df)
        open_circuit_count = len(weight_df[weight_df['value'] >= 1e8])
        effective_count = initial_count - open_circuit_count
        
        if open_circuit_count > 0:
            logger.info(f"Found {open_circuit_count} open-circuit resistors (part of differential pairs)")
        logger.info(f"Found {effective_count} effective resistors")
        
        if weight_df.empty:
            logger.warning("No weight resistors found in CSV")
            raise ValueError("No weight resistors found in the input CSV")
        
        logger.info(f"Found {len(weight_df)} total weight resistors (including differential pairs)")
        
        # 应用排序模式
        if self.numbering_mode == 'grouped':
            logger.info("Applying grouped numbering mode...")
            # 显示分组前的前10个电阻类型
            logger.info(f"Before grouping - first 10 resistors:")
            for i in range(min(10, len(weight_df))):
                row = weight_df.iloc[i]
                logger.info(f"  {i+1}: {row.get('layer', 'N/A')}, {row.get('type', 'N/A')}, channel={row.get('channel', 'N/A')}")
            
            weight_df = self._reorder_by_groups(weight_df)
            
            # 显示分组后的前10个电阻类型
            logger.info(f"After grouping - first 10 resistors:")
            for i in range(min(10, len(weight_df))):
                row = weight_df.iloc[i]
                logger.info(f"  R{i+1}: {row.get('layer', 'N/A')}, {row.get('type', 'N/A')}, channel={row.get('channel', 'N/A')}")
        
        # 重新编号符号
        logger.info("Renumbering symbols...")
        weight_df['Designator'] = [f"R{i+1}" for i in range(len(weight_df))]
        
        # 添加BOM字段 - 自动添加R前缀如果没有
        weight_df['Footprint'] = f"R{self.package}"
        
        # 添加数量列 - 每个电阻数量固定为1
        weight_df['Quantity'] = 1
        
        # 格式化阻值并包含精度（修复双%%问题）
        tolerance_clean = self.tolerance.replace('%%', '%')
        weight_df['Value'] = weight_df['value'].apply(
            lambda v: self._format_resistance_with_tolerance(v, tolerance_clean)
        )
        
        # 选择BOM输出列 - 精度已包含在Value中
        bom_columns = ['Designator', 'Footprint', 'Quantity', 'Value']
        
        # 可选：包含原始名称以便追溯
        if self.include_original_name:
            weight_df['Original_Name'] = weight_df['name']
            bom_columns = ['Designator', 'Footprint', 'Quantity', 'Value', 'Original_Name']
        
        # 可选：包含层和通道信息
        if 'layer' in weight_df.columns and 'channel' in weight_df.columns:
            weight_df['Layer'] = weight_df['layer']
            weight_df['Channel'] = weight_df['channel']
            if self.bom_config.get('include_layer_info', False):
                bom_columns.extend(['Layer', 'Channel'])
        
        # 创建BOM DataFrame
        bom_df = weight_df[bom_columns]
        
        # 确定输出路径
        if output_csv_path is None:
            # 默认在输入文件同目录下创建BOM文件
            input_dir = os.path.dirname(input_csv_path)
            output_csv_path = os.path.join(input_dir, 'weight_resistor_bom.csv')
        
        # 步骤1：先保存原始BOM（未处理的）
        raw_bom_path = output_csv_path.replace('.csv', '_raw.csv')
        logger.info(f"Step 1: Saving raw BOM to: {raw_bom_path}")
        
        # 确保输出目录存在
        output_dir = os.path.dirname(raw_bom_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # 保存原始BOM
        bom_df.to_csv(raw_bom_path, index=False, encoding='utf-8-sig')
        logger.info(f"Raw BOM saved: {len(bom_df)} rows")
        
        # 步骤2：如果启用后处理，读取原始BOM并处理
        enable_post_processing = self.bom_config.get('enable_post_processing', True)
        if enable_post_processing:
            logger.info("Step 2: Reading raw BOM for post-processing...")
            
            # 重新读取原始BOM文件
            bom_df_for_processing = pd.read_csv(raw_bom_path, encoding='utf-8-sig')
            logger.info(f"Raw BOM loaded: {len(bom_df_for_processing)} rows")
            
            try:
                logger.info("Applying BOM post-processing...")
                # 创建后处理器配置
                post_processor_config = {
                    'enable_standardization': self.bom_config.get('standardize_format', True),
                    'enable_merging': self.bom_config.get('merge_same_values', True),
                    'sort_designators': self.bom_config.get('sort_designators', True)
                }
                
                # 创建后处理器并处理BOM
                post_processor = BOMPostProcessor(post_processor_config)
                bom_df = post_processor.process(bom_df_for_processing)
                logger.info(f"BOM post-processing completed: {len(bom_df_for_processing)} rows -> {len(bom_df)} rows")
                
            except Exception as e:
                logger.warning(f"BOM post-processing failed: {e}, using original format")
                # 后处理失败不影响主流程，使用原始格式
                bom_df = bom_df_for_processing
        else:
            logger.info("Post-processing disabled, using raw BOM as final output")
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_csv_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # 保存最终BOM CSV (使用utf-8-sig确保Windows兼容性)
        bom_df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
        logger.info(f"Final BOM saved to: {output_csv_path}")
        
        # 生成统计信息
        summary = self._generate_summary(weight_df)
        
        # 返回结果包含两个文件路径
        result = {
            'success': True,
            'count': len(bom_df),
            'output_file': output_csv_path,
            'raw_bom_file': raw_bom_path,  # 原始BOM文件路径
            'summary': summary
        }
        
        # 如果启用了后处理，添加压缩率信息
        if enable_post_processing:
            original_rows = len(weight_df)
            final_rows = len(bom_df)
            compression_rate = (1 - final_rows / original_rows) * 100 if original_rows > 0 else 0
            result['compression_rate'] = f"{compression_rate:.1f}%"
            result['original_rows'] = original_rows
            result['final_rows'] = final_rows
            logger.info(f"Compression rate: {original_rows} rows -> {final_rows} rows ({compression_rate:.1f}%)")
        
        return result
    
    def _format_resistance_with_tolerance(self, value: float, tolerance: str) -> str:
        """
        格式化电阻值显示，包含精度
        
        Args:
            value: 电阻值（欧姆）
            tolerance: 精度字符串
            
        Returns:
            格式化的字符串，如 "100K ±1%"
        """
        # 先格式化阻值
        formatted_value = self._format_resistance_value(value)
        # 组合阻值和精度
        return f"电阻 {formatted_value} ± {tolerance}" if tolerance else formatted_value
    
    def _format_resistance_value(self, value: float) -> str:
        """
        格式化电阻值显示
        
        改进：智能去除末尾零，保持有效数字
        
        Args:
            value: 电阻值（欧姆）
            
        Returns:
            格式化的字符串
        """
        if value >= 1e8:
            # 开路电阻（差分电路中表示该路径断开）
            # 在BOM中显示为高阻值，便于制造商理解
            return f"{value/1e6:.0f}MΩ"
        elif value >= 1e6:
            # 兆欧级 - 使用g格式自动去除末尾零
            return f"{value/1e6:g}MΩ"
        elif value >= 1e3:
            # 千欧级 - 使用g格式自动去除末尾零
            return f"{value/1e3:g}kΩ"
        elif value >= 1:
            # 欧姆级
            if value == int(value):
                return f"{int(value)}Ω"
            else:
                # 使用g格式自动去除末尾零
                return f"{value:g}Ω"
        else:
            # 毫欧级 - 使用g格式自动去除末尾零
            return f"{value*1e3:g}mΩ"
    
    def _reorder_by_groups(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        按新规则重新排序电阻：
        每通道内顺序：bias_pos → input_pos(1-6) → bias_neg → input_neg(1-6)
        
        Args:
            df: 原始权重电阻DataFrame
            
        Returns:
            重新排序后的DataFrame
        """
        # 创建排序键
        def get_sort_key(row):
            """生成排序键：(层优先级, 通道号, 类型优先级, 索引)"""
            # 层优先级
            layer_priority = {
                'layer2': 0,
                'layer3': 1,
                'layer4': 2,
                'layer5': 3
            }
            
            # 类型优先级（决定通道内顺序）
            type_priority = {
                'bias_pos': 0,    # R1
                'input_pos': 1,   # R2-R7
                'bias_neg': 2,    # R8
                'input_neg': 3    # R9-R14
            }
            
            # 获取层、通道、类型
            layer = row.get('layer', 'unknown')
            channel = row.get('channel', 0)
            res_type = row.get('type', 'unknown')
            
            # 处理索引（bias没有索引，设为0）
            index = row.get('index')
            if pd.isna(index) or index is None:
                index = 0
            else:
                index = float(index)
            
            return (
                layer_priority.get(layer, 999),
                channel,
                type_priority.get(res_type, 999),
                index
            )
        
        # 创建副本以避免修改原数据
        df_copy = df.copy()
        
        # 添加排序键列
        df_copy['sort_key'] = df_copy.apply(get_sort_key, axis=1)
        
        # 按排序键排序
        df_sorted = df_copy.sort_values('sort_key')
        
        # 删除临时排序键列
        df_sorted = df_sorted.drop('sort_key', axis=1)
        
        # 重置索引
        df_sorted = df_sorted.reset_index(drop=True)
        
        logger.info(f"Reordered {len(df_sorted)} resistors in grouped mode")
        
        return df_sorted
    
    def _generate_summary(self, weight_df: pd.DataFrame) -> Dict[str, Any]:
        """
        生成BOM统计摘要
        
        Args:
            weight_df: 权重电阻DataFrame
            
        Returns:
            统计信息字典
        """
        # 过滤掉极大值进行统计
        valid_mask = weight_df['value'] < 1e9
        valid_values = weight_df.loc[valid_mask, 'value']
        
        summary = {
            'total_count': len(weight_df),
            'valid_count': len(valid_values),
            'open_circuit_count': len(weight_df) - len(valid_values),
            'package': self.package,
            'tolerance': self.tolerance
        }
        
        if len(valid_values) > 0:
            summary.update({
                'min_value': float(valid_values.min()),
                'max_value': float(valid_values.max()),
                'mean_value': float(valid_values.mean()),
                'median_value': float(valid_values.median()),
                'value_range': {
                    '0-100Ω': int((valid_values <= 100).sum()),
                    '100-1kΩ': int(((valid_values > 100) & (valid_values <= 1000)).sum()),
                    '1k-10kΩ': int(((valid_values > 1000) & (valid_values <= 10000)).sum()),
                    '10k-100kΩ': int(((valid_values > 10000) & (valid_values <= 100000)).sum()),
                    '100k-1MΩ': int(((valid_values > 100000) & (valid_values <= 1e6)).sum()),
                    '>1MΩ': int((valid_values > 1e6).sum())
                }
            })
        
        # 层分布统计
        if 'layer' in weight_df.columns:
            layer_counts = weight_df['layer'].value_counts().to_dict()
            summary['layer_distribution'] = {str(k): int(v) for k, v in layer_counts.items()}
        
        return summary
    
    def update_config(self, **kwargs):
        """
        更新BOM配置参数
        
        Args:
            **kwargs: 配置参数键值对
                - package: 封装规格
                - tolerance: 精度规格
                - include_original_name: 是否包含原始名称
        """
        if 'package' in kwargs:
            self.package = kwargs['package']
        if 'tolerance' in kwargs:
            self.tolerance = kwargs['tolerance']
        if 'include_original_name' in kwargs:
            self.include_original_name = kwargs['include_original_name']
        
        # 更新配置字典
        self.bom_config.update(kwargs)
        
        logger.info(f"BOM config updated: {kwargs}")