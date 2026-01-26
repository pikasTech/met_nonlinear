"""电阻值校验器模块 - 强制校验网表与CSV一致性"""
import os
import re
import pandas as pd
import logging
from typing import Dict, List, Tuple, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class ResistanceValidator:
    """
    电阻值校验器 - 验证网表与CSV的一致性
    
    # CRITICAL: 此校验器的所有方法必须执行，禁止跳过
    # NO ROLLBACK: 发现不一致直接报错，不进行任何回滚
    # NO MOCK: 禁止使用模拟数据，必须基于真实文件
    """
    
    def __init__(self, tolerance: float = 1e-6):
        """
        初始化校验器
        
        Args:
            tolerance: 数值比较的容差（默认1e-6）
        """
        self.tolerance = tolerance
        self.validation_results = []
        self.error_count = 0
        self.warning_count = 0
    
    def validate_netlist_csv_consistency(self, 
                                        netlist_path: str, 
                                        csv_path: str) -> Dict:
        """
        验证网表文件与CSV文件的一致性
        
        # CRITICAL: 此校验必须执行，禁止跳过
        # NO ROLLBACK: 发现不一致直接报错
        # NO MOCK: 必须使用真实文件
        
        Args:
            netlist_path: 网表文件路径
            csv_path: CSV文件路径
            
        Returns:
            验证结果字典
            
        Raises:
            ValueError: 当发现严重不一致时
        """
        # 验证文件存在性 - 不使用try-except
        if not os.path.exists(netlist_path):
            raise ValueError(
                f"Netlist file does not exist: {netlist_path}\n"
                f"This is a critical error - netlist must exist for validation"
            )
        
        if not os.path.exists(csv_path):
            raise ValueError(
                f"CSV file does not exist: {csv_path}\n"
                f"This is a critical error - CSV must exist for validation"
            )
        
        # 解析网表中的电阻值
        netlist_resistances = self._parse_netlist_resistances(netlist_path)
        
        # 读取CSV中的电阻值
        csv_resistances = self._load_csv_resistances(csv_path)
        
        # 执行详细对比 - CRITICAL: 此步骤不可跳过
        comparison_result = self._compare_resistances(
            netlist_resistances, 
            csv_resistances
        )
        
        # 如果有严重错误，直接抛出异常
        if comparison_result['critical_errors']:
            error_details = '\n'.join(comparison_result['critical_errors'])
            raise ValueError(
                f"Critical validation errors found:\n{error_details}\n"
                f"Netlist: {netlist_path}\n"
                f"CSV: {csv_path}"
            )
        
        # 记录验证结果
        self.validation_results.append({
            'netlist': netlist_path,
            'csv': csv_path,
            'result': comparison_result
        })
        
        return comparison_result
    
    def _parse_netlist_resistances(self, netlist_path: str) -> Dict[str, float]:
        """
        解析网表文件中的电阻值
        
        # NO MOCK: 必须从真实网表解析
        # NO ROLLBACK: 解析失败直接报错
        """
        resistances = {}
        
        # 读取网表文件 - 不隐藏错误
        with open(netlist_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 正则表达式匹配电阻定义
        # 格式: R<name> <node1> <node2> <value>
        pattern = r'^R(\S+)\s+\S+\s+\S+\s+([0-9.eE+-]+)'
        
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('*'):
                continue
            
            match = re.match(pattern, line)
            if match:
                res_name = f"R{match.group(1)}"
                res_value = float(match.group(2))
                
                # 验证电阻值有效性
                if res_value <= 0 and res_value != float('inf') and res_value != 1e9:
                    raise ValueError(
                        f"Invalid resistance value in netlist: {res_name}={res_value}\n"
                        f"File: {netlist_path}\n"
                        f"Line: {line}"
                    )
                
                resistances[res_name] = res_value
        
        if not resistances:
            # 可能是空网表或还未生成，这不是错误
            logger.warning(f"No resistances found in netlist: {netlist_path}")
        
        logger.info(f"Parsed {len(resistances)} resistances from netlist")
        return resistances
    
    def _load_csv_resistances(self, csv_path: str) -> Dict[str, float]:
        """
        加载CSV文件中的电阻值
        
        # NO MOCK: 必须从真实CSV加载
        """
        # 读取CSV - 不使用try-except隐藏错误
        df = pd.read_csv(csv_path)
        
        # 验证必需列存在
        required_columns = ['name', 'value']
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(
                f"CSV missing required columns: {missing_columns}\n"
                f"File: {csv_path}\n"
                f"Available columns: {list(df.columns)}"
            )
        
        # 转换为字典
        resistances = {}
        for _, row in df.iterrows():
            name = row['name']
            value = float(row['value'])
            
            # 验证值有效性
            if pd.isna(value):
                raise ValueError(
                    f"NaN value found in CSV for resistance: {name}\n"
                    f"File: {csv_path}"
                )
            
            resistances[name] = value
        
        if not resistances:
            raise ValueError(
                f"No resistances found in CSV: {csv_path}\n"
                f"DataFrame shape: {df.shape}"
            )
        
        logger.info(f"Loaded {len(resistances)} resistances from CSV")
        return resistances
    
    def _compare_resistances(self, 
                           netlist_res: Dict[str, float],
                           csv_res: Dict[str, float]) -> Dict:
        """
        详细对比两个电阻值集合
        
        # CRITICAL: 此对比必须执行，禁止跳过
        # NO ROLLBACK: 发现严重不一致直接记录
        """
        result = {
            'total_netlist': len(netlist_res),
            'total_csv': len(csv_res),
            'matched': 0,
            'mismatched_values': [],
            'missing_in_csv': [],
            'missing_in_netlist': [],
            'critical_errors': [],
            'warnings': []
        }
        
        # 如果网表为空，这可能是正常的（还未生成网表）
        if not netlist_res:
            result['warnings'].append("Netlist has no resistances - may not be generated yet")
            result['consistency_ratio'] = 0.0
            return result
        
        # 检查网表中的每个电阻
        for name, netlist_value in netlist_res.items():
            if name not in csv_res:
                result['missing_in_csv'].append(name)
                result['critical_errors'].append(
                    f"Resistance {name} exists in netlist but missing in CSV"
                )
            else:
                csv_value = csv_res[name]
                
                # 数值对比
                if abs(netlist_value - csv_value) > self.tolerance:
                    # 对于极大电阻值（1e9），允许更大的容差
                    if netlist_value == 1e9 or csv_value == 1e9:
                        if abs(netlist_value - csv_value) / 1e9 > 0.01:  # 1% of 1e9
                            relative_error = abs(netlist_value - csv_value) / max(netlist_value, csv_value) * 100
                        else:
                            result['matched'] += 1
                            continue
                    else:
                        relative_error = abs(netlist_value - csv_value) / netlist_value * 100 if netlist_value != 0 else float('inf')
                    
                    mismatch_info = {
                        'name': name,
                        'netlist_value': netlist_value,
                        'csv_value': csv_value,
                        'absolute_error': abs(netlist_value - csv_value),
                        'relative_error': relative_error
                    }
                    result['mismatched_values'].append(mismatch_info)
                    
                    # 如果误差超过1%，记为严重错误
                    if relative_error > 1.0:
                        result['critical_errors'].append(
                            f"Resistance {name}: value mismatch > 1% "
                            f"(netlist={netlist_value}, csv={csv_value}, error={relative_error:.2f}%)"
                        )
                    else:
                        result['warnings'].append(
                            f"Resistance {name}: minor value mismatch "
                            f"(error={relative_error:.4f}%)"
                        )
                else:
                    result['matched'] += 1
        
        # 检查CSV中多余的电阻
        for name in csv_res:
            if name not in netlist_res:
                result['missing_in_netlist'].append(name)
                # 这只是警告，不是严重错误（CSV可能包含所有层的数据）
                result['warnings'].append(
                    f"Resistance {name} exists in CSV but missing in netlist"
                )
        
        # 计算一致性比例
        if netlist_res:
            result['consistency_ratio'] = result['matched'] / len(netlist_res) * 100
        else:
            result['consistency_ratio'] = 0.0
        
        # 如果一致性低于95%，记为严重错误
        if result['consistency_ratio'] < 95.0 and len(netlist_res) > 0:
            result['critical_errors'].append(
                f"Overall consistency too low: {result['consistency_ratio']:.1f}% < 95%"
            )
        
        # 记录统计信息
        logger.info(f"Validation complete: {result['matched']} matched, "
                   f"{len(result['mismatched_values'])} mismatched, "
                   f"{len(result['missing_in_csv'])} missing in CSV, "
                   f"{len(result['missing_in_netlist'])} missing in netlist")
        
        return result
    
    def generate_validation_report(self, output_path: str):
        """
        生成详细的验证报告
        
        # NO ROLLBACK: 报告生成失败直接报错
        """
        if not self.validation_results:
            raise ValueError("No validation results to report")
        
        # 准备报告数据
        report_data = []
        for result in self.validation_results:
            report_data.append({
                'netlist': result['netlist'],
                'csv': result['csv'],
                'total_netlist': result['result']['total_netlist'],
                'total_csv': result['result']['total_csv'],
                'matched': result['result']['matched'],
                'consistency_ratio': result['result']['consistency_ratio'],
                'critical_errors': len(result['result']['critical_errors']),
                'warnings': len(result['result']['warnings'])
            })
        
        report_df = pd.DataFrame(report_data)
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # 保存报告
        report_df.to_csv(output_path, index=False)
        logger.info(f"Validation report saved to {output_path}")
        
        return output_path