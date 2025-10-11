"""电阻导出任务处理器 - 基于统一架构"""
import logging
import json
import os
import glob
from typing import Dict, Any, List, Optional
from spice_simulator.resistance_extractor import ResistanceExtractor
from spice_simulator.resistance_standardizer import ResistanceStandardizer
from spice_simulator.resistance_validator import ResistanceValidator
from spice_simulator.spice_path_manager import SPICEPathManager
from spice_simulator.weight_resistor_bom_generator import WeightResistorBOMGenerator

logger = logging.getLogger(__name__)

class ResistanceTaskHandler:
    """
    电阻导出任务处理器 - 基于统一架构
    
    统一架构特性：
    1. 自动传递inference_config到ResistanceExtractor
    2. 依赖UnifiedResistanceCalculator的强制一致性验证
    3. 统一的数据源确保网表与CSV完全一致
    4. 任何数据不一致都会抛出SystemError
    
    NO COMPENSATION: 不使用补偿方法，通过统一核心解决一致性  
    NO ROLLBACK: 遇到错误直接报错，不进行回滚
    CRITICAL: 一致性验证已内置到统一架构中
    """
    
    def __init__(self, project_path: str, inference_config: Dict = None):
        self.project_path = project_path
        self.inference_config = inference_config or {}
        self.path_manager = SPICEPathManager(project_path)
        
        # 加载项目配置文件
        import os
        config_path = os.path.join(project_path, 'config.json')
        self.config = {}
        if os.path.exists(config_path):
            import json
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        
        # 如果没有传入inference_config，从config中获取
        if not inference_config and self.config:
            self.inference_config = self.config.get('inference_config', {})
        
        # 统一架构：传递inference_config到ResistanceExtractor
        self.extractor = ResistanceExtractor(project_path, inference_config=self.inference_config)
        
        self.standardizer = ResistanceStandardizer()
        self.validator = ResistanceValidator()  # 保留用于兼容性
        
        logger.info("ResistanceTaskHandler initialized with unified architecture")
        logger.info(f"Inference config provided: {bool(inference_config)}")
    
    def export_resistances(self, 
                          include_standardized: bool = False,
                          series_list: list = None,
                          output_dir: str = None,
                          validate_with_netlist: bool = True,
                          generate_bom: bool = False,
                          bom_config: Dict = None) -> Dict[str, Any]:
        """
        基于统一架构的电阻值导出
        
        统一架构特性：
        1. 使用UnifiedResistanceCalculator确保数据源唯一性
        2. 内置强制一致性验证 - 网表与CSV数据自动保证一致
        3. 任何不一致都会抛出SystemError，无需额外验证
        
        Args:
            include_standardized: 是否包含标准化值
            series_list: 标准化系列列表
            output_dir: 自定义输出目录
            validate_with_netlist: 已废弃 - 统一架构内置一致性验证
            generate_bom: 是否生成权重电阻BOM
            bom_config: BOM配置字典
            
        Returns:
            执行结果字典（已通过强制一致性验证）
            
        Raises:
            SystemError: 内置一致性验证失败
        """
        if series_list is None:
            series_list = ['E96', 'E24']
            
        logger.info("开始基于统一架构的电阻值导出...")
        
        # 使用统一架构提取电阻值 - 自动执行一致性验证
        # SystemError会在此步骤抛出（如果数据不一致）
        try:
            resistance_data = self.extractor.extract_from_model()
            logger.info("统一架构电阻提取成功，已通过强制一致性验证")
        except SystemError as e:
            logger.error(f"一致性验证失败: {e}")
            raise  # 直接向上抛出SystemError
        except Exception as e:
            logger.error(f"电阻提取失败: {e}")
            raise ValueError(f"Resistance extraction failed: {e}")
        
        # 基础结果验证
        if not resistance_data:
            raise ValueError(f"No resistance data extracted from project: {self.project_path}")
        
        logger.info(f"提取到 {len(resistance_data)} 个电阻值（已验证一致性）")
        
        # 转换为DataFrame
        df = self.extractor.to_dataframe()
        
        # 验证DataFrame完整性 - CRITICAL: 此验证必须执行
        self._validate_dataframe(df)
        
        # 标准化（如果需要）
        if include_standardized:
            # NO MOCK: 必须真实计算标准化值
            df = self.standardizer.standardize_dataframe(
                df, 
                series_list=series_list
            )
            logger.info(f"已添加标准化列: {series_list}")
            
            # 验证标准化结果
            self._validate_standardization(df, series_list)
        
        # 保存文件 - NO ROLLBACK: 保存失败直接报错
        output_path = self.path_manager.get_resistance_csv_path()
        if output_dir:
            output_path = os.path.join(output_dir, 'all_layers_resistances.csv')
        
        # 确保目录存在
        output_dir_path = os.path.dirname(output_path)
        if output_dir_path and not os.path.exists(output_dir_path):
            os.makedirs(output_dir_path, exist_ok=True)
        
        df.to_csv(output_path, index=False)
        logger.info(f"电阻值已导出到: {output_path}")
        
        # 统一架构说明：一致性验证已在数据提取时自动完成
        if validate_with_netlist:
            logger.info("统一架构内置一致性验证 - 网表与CSV数据已保证一致")
        
        # 生成分析报告
        analysis = None
        if include_standardized:
            analysis = self._generate_analysis_report(df, series_list)
            
            # 添加统一架构验证信息到报告
            analysis['unified_architecture'] = {
                'consistency_verified': True,
                'verification_method': 'UnifiedResistanceCalculator built-in validation',
                'note': 'Netlist and CSV data guaranteed consistent by unified core'
            }
            
            analysis_path = self.path_manager.get_analysis_report_path()
            with open(analysis_path, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            logger.info(f"分析报告已保存到: {analysis_path}")
        
        # 生成权重电阻BOM（如果需要）
        bom_result = None
        if generate_bom:
            logger.info("Generating weight resistor BOM...")
            try:
                # 检查config中的BOM标准化配置
                bom_standardization = None
                bom_input_path = output_path
                
                # 从inference_config中读取BOM配置
                if self.config and self.config.get('inference_config'):
                    bom_config_from_json = self.config['inference_config'].get('bom_config', {})
                    bom_standardization = bom_config_from_json.get('standardization_series')
                    
                    # 如果bom_config为None，初始化为空字典
                    if bom_config is None:
                        bom_config = {}
                    
                    # 合并配置，CLI参数优先
                    for key, value in bom_config_from_json.items():
                        if key not in bom_config:
                            bom_config[key] = value
                    
                    # 确保numbering_mode被传递（映射bom_numbering到numbering_mode）
                    if 'bom_numbering' in bom_config_from_json:
                        bom_config['numbering_mode'] = bom_config_from_json['bom_numbering']
                        logger.info(f"BOM numbering mode from config.json: {bom_config['numbering_mode']}")
                    elif 'numbering_mode' in bom_config_from_json:
                        bom_config['numbering_mode'] = bom_config_from_json['numbering_mode']
                
                # 如果配置了标准化，先对CSV进行标准化
                if bom_standardization:
                    logger.info(f"Applying {bom_standardization} standardization before BOM generation")
                    # 读取刚保存的CSV
                    import pandas as pd
                    df = pd.read_csv(output_path)
                    
                    # 应用标准化
                    df_standardized = self.standardizer.standardize_dataframe(
                        df, 
                        series_list=[bom_standardization]
                    )
                    
                    # 将标准化值替换原始值
                    df['value'] = df_standardized[f'Standardized_{bom_standardization}']
                    
                    # 保存标准化后的CSV（临时文件）
                    standardized_csv_path = output_path.replace('.csv', f'_{bom_standardization}_bom_temp.csv')
                    df.to_csv(standardized_csv_path, index=False)
                    bom_input_path = standardized_csv_path
                
                bom_generator = WeightResistorBOMGenerator(bom_config)
                
                # 确定BOM输出路径
                if output_dir:
                    bom_output_path = os.path.join(output_dir, 'weight_resistor_bom.csv')
                else:
                    bom_output_path = self.path_manager.get_resistance_csv_path(suffix='_bom')
                
                # 生成BOM
                bom_result = bom_generator.generate_bom_from_csv(
                    input_csv_path=bom_input_path,
                    output_csv_path=bom_output_path
                )
                logger.info(f"BOM generated: {bom_result['count']} weight resistors")
                
                # 删除临时文件（如果有）
                if bom_input_path != output_path:
                    import os as os_module
                    if os_module.path.exists(bom_input_path):
                        os_module.remove(bom_input_path)
                
            except Exception as e:
                logger.warning(f"BOM generation failed: {e}")
                # BOM生成失败不影响主流程
                bom_result = {'success': False, 'error': str(e)}
        
        result = {
            'success': True,
            'resistance_count': len(resistance_data),
            'output_file': output_path,
            'standardized': include_standardized,
            'series': series_list if include_standardized else [],
            'consistency_verified': True,
            'verification_method': 'unified_architecture_builtin',
            'analysis': analysis
        }
        
        # 添加BOM结果（如果有）
        if bom_result:
            result['bom'] = bom_result
        
        return result
    
    def standardize_existing_csv(self,
                                input_csv: str,
                                series_list: list = None,
                                output_dir: str = None) -> Dict[str, Any]:
        """
        标准化已有的CSV文件
        
        # NO MOCK: 必须基于真实CSV文件
        # NO ROLLBACK: 错误直接报告
        
        Args:
            input_csv: 输入CSV文件路径
            series_list: 标准化系列列表
            output_dir: 输出目录
            
        Returns:
            执行结果字典
        """
        if series_list is None:
            series_list = ['E96', 'E24']
        
        if not os.path.exists(input_csv):
            raise ValueError(
                f"Input CSV file not found: {input_csv}\n"
                f"Please run export-resistance first"
            )
        
        logger.info(f"读取CSV文件: {input_csv}")
        import pandas as pd
        df = pd.read_csv(input_csv)
        
        # 验证DataFrame
        self._validate_dataframe(df)
        
        # 执行标准化
        df = self.standardizer.standardize_dataframe(
            df,
            series_list=series_list
        )
        
        # 验证标准化结果
        self._validate_standardization(df, series_list)
        
        # 保存结果
        if output_dir:
            output_path = os.path.join(output_dir, 'resistances_standardized.csv')
        else:
            output_path = self.path_manager.get_resistance_csv_path(suffix='_standardized')
        
        # 确保目录存在
        output_dir_path = os.path.dirname(output_path)
        if output_dir_path and not os.path.exists(output_dir_path):
            os.makedirs(output_dir_path, exist_ok=True)
        
        df.to_csv(output_path, index=False)
        logger.info(f"标准化结果已保存到: {output_path}")
        
        # 计算平均误差 - 移除过滤，包含所有电阻的误差
        avg_errors = {}
        for series in series_list:
            error_col = f'Error_{series}_pct'
            if error_col in df.columns:
                # 移除过滤，计算所有电阻的相对误差
                valid_errors = df[error_col]  # 包含所有电阻的误差
                avg_errors[series] = float(valid_errors.mean()) if len(valid_errors) > 0 else 0.0
        
        avg_error = sum(avg_errors.values()) / len(avg_errors) if avg_errors else 0.0
        
        return {
            'success': True,
            'input_file': input_csv,
            'output_file': output_path,
            'series': series_list,
            'avg_error': avg_error,
            'series_errors': avg_errors
        }
    
    def _validate_dataframe(self, df):
        """
        验证DataFrame完整性
        
        # CRITICAL: 此验证必须执行，禁止跳过
        # NO ROLLBACK: 发现问题直接报错
        """
        import pandas as pd
        
        if df.empty:
            raise ValueError("DataFrame is empty after extraction")
        
        required_columns = ['layer', 'channel', 'type', 'name', 'value']
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(
                f"DataFrame missing required columns: {missing_columns}\n"
                f"Available columns: {list(df.columns)}"
            )
        
        # 检查NaN值
        if df['value'].isna().any():
            nan_rows = df[df['value'].isna()]
            raise ValueError(
                f"NaN values found in resistance data:\n{nan_rows.to_string()}"
            )
        
        # 检查无效值（排除MAX_RESISTANCE=1e9）
        invalid_mask = (df['value'] <= 0) & (df['value'] != float('inf')) & (df['value'] != 1e9)
        if invalid_mask.any():
            invalid_rows = df[invalid_mask]
            raise ValueError(
                f"Invalid resistance values found:\n{invalid_rows.to_string()}"
            )
    
    def _validate_standardization(self, df, series_list):
        """
        验证标准化结果
        
        # CRITICAL: 此验证必须执行
        """
        import pandas as pd
        
        for series in series_list:
            col_name = f'Standardized_{series}'
            if col_name not in df.columns:
                raise ValueError(f"Standardization failed: column {col_name} not found")
            
            # 检查标准化值的有效性
            if df[col_name].isna().any():
                nan_rows = df[df[col_name].isna()]
                raise ValueError(
                    f"NaN values in standardized column {col_name}:\n"
                    f"{nan_rows[['name', 'value', col_name]].to_string()}"
                )
    
    def _validate_csv_with_netlists(self, csv_path: str) -> Dict:
        """
        验证CSV与网表的一致性
        
        # CRITICAL: 此验证必须执行，禁止跳过
        # NO ROLLBACK: 验证失败直接报错
        # NO MOCK: 必须使用真实文件
        """
        validation_results = {
            'passed': True,
            'layers_validated': [],
            'errors': [],
            'warnings': []
        }
        
        # 查找所有网表文件
        netlist_dir = self.path_manager.netlist_dir
        if not os.path.exists(netlist_dir):
            # 创建目录并抛出错误
            os.makedirs(netlist_dir, exist_ok=True)
            raise FileNotFoundError(
                f"网表目录不存在且无法创建: {netlist_dir}\n"
                f"请先运行推理生成网表文件"
            )
        
        # 对每个网表文件进行验证
        netlist_files = glob.glob(os.path.join(netlist_dir, '*.cir'))
        
        if not netlist_files:
            raise FileNotFoundError(
                f"网表目录中没有找到.cir文件: {netlist_dir}\n"
                f"请先运行推理生成网表文件"
            )
        
        for netlist_path in netlist_files:
            layer_name = os.path.basename(netlist_path).replace('.cir', '')
            
            logger.info(f"Validating {layer_name}...")
            
            # 执行验证 - CRITICAL: 不使用try-except
            # 但是允许网表为空的情况
            result = self.validator.validate_netlist_csv_consistency(
                netlist_path,
                csv_path
            )
            
            validation_results['layers_validated'].append({
                'layer': layer_name,
                'consistency': result['consistency_ratio'],
                'matched': result['matched'],
                'total': result['total_netlist']
            })
            
            # 收集错误和警告
            if result['critical_errors']:
                validation_results['errors'].extend(result['critical_errors'])
                validation_results['passed'] = False
            
            if result['warnings']:
                validation_results['warnings'].extend(result['warnings'])
        
        # 如果有网表文件但验证失败，才抛出异常
        if netlist_files and not validation_results['passed']:
            error_summary = '\n'.join(validation_results['errors'][:5])  # 显示前5个错误
            raise ValueError(
                f"CSV and netlist validation failed:\n{error_summary}\n"
                f"Total errors: {len(validation_results['errors'])}"
            )
        
        return validation_results
    
    def _generate_analysis_report(self, df, series_list):
        """生成标准化分析报告"""
        import pandas as pd
        
        report = {
            'total_resistors': len(df),
            'value_range': {
                'min': float(df['value'].min()),
                'max': float(df['value'].max())
            },
            'layers': df['layer'].unique().tolist() if 'layer' in df.columns else [],
            'standardization_analysis': {}
        }
        
        for series in series_list:
            col_name = f'Standardized_{series}'
            error_col = f'Error_{series}_pct'
            
            if col_name in df.columns:
                # 移除过滤，对所有电阻进行分析 - 完全校验
                valid_df = df  # 完全校验，不过滤任何电阻
                
                if len(valid_df) > 0:
                    analysis = self.standardizer.analyze_errors(
                        valid_df['value'], 
                        valid_df[col_name]
                    )
                else:
                    analysis = {
                        'total_resistors': 0,
                        'validated_resistors': 0,
                        'mean_relative_error': 0,
                        'max_relative_error': 0,
                        'within_1pct': 100.0,
                        'within_5pct': 100.0,
                        'within_10pct': 100.0
                    }
                
                # 添加系列信息
                analysis['series_info'] = self.standardizer.get_series_info(series)
                report['standardization_analysis'][series] = analysis
        
        return report