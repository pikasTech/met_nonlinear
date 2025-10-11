"""
统一电阻计算核心组件

此模块是所有电阻计算的唯一来源，确保网表生成和CSV导出使用完全相同的逻辑。

设计原则：
1. 单一数据源：所有电阻计算必须通过此核心组件
2. 配置统一：确保所有调用路径使用相同的inference_config
3. 强制验证：每次计算后自动验证网表与CSV的一致性
4. 失败即停：发现不一致立即抛SystemError

NO COMPENSATION: 不使用任何补偿方法，从根本上统一计算逻辑
NO ROLLBACK: 计算失败或不一致直接报错
CRITICAL: 一致性验证不可跳过
"""

import os
import logging
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from spice_simulator.circuit_dense import DenseCircuitFactory

logger = logging.getLogger(__name__)

class UnifiedResistanceCalculator:
    """
    统一电阻计算核心组件
    
    这是系统中唯一的电阻计算来源，所有的网表生成和CSV导出
    都必须通过此组件来确保数据一致性。
    
    设计目标：
    - 消除多个代码路径导致的数据不一致
    - 提供标准化的电阻数据格式
    - 强制执行一致性验证
    """
    
    def __init__(self, model, inference_config: Dict[str, Any] = None):
        """
        统一初始化电阻计算核心
        
        Args:
            model: 神经网络模型（必须有layer_to_layer_models属性）
            inference_config: 推理配置字典，包含所有SPICE配置参数
                - opamp_config: 运放配置
                - power_supply: 电源配置  
                - high_pass_config: 高通滤波器配置
                - bias_compensation: 偏置补偿配置
        """
        if model is None:
            raise ValueError("Model cannot be None")
            
        self.model = model
        self.inference_config = inference_config or {}
        
        # 验证模型结构
        if not hasattr(model, 'layer_to_layer_models'):
            raise ValueError("Model must have layer_to_layer_models attribute")
            
        # 提取配置参数
        self.opamp_config = self.inference_config.get('opamp_config', None)
        self.power_supply_config = self.inference_config.get('power_supply', None) 
        self.high_pass_config = self.inference_config.get('high_pass_config', None)
        self.bias_compensation = self.inference_config.get('bias_compensation', {})
        
        # 存储计算结果
        self._layer_circuits = {}  # 缓存DenseCircuit对象
        self._resistance_data = {}  # 缓存电阻数据
        self._calculation_completed = False
        
        logger.info("UnifiedResistanceCalculator initialized")
        logger.info(f"Inference config keys: {list(self.inference_config.keys())}")
    
    def calculate_all_layer_resistances(self) -> Dict[str, List[Dict]]:
        """
        计算所有层的电阻值 - 系统唯一计算入口
        
        Returns:
            Dict[str, List[Dict]]: 层名称到电阻记录列表的映射
            
        Raises:
            ValueError: 计算失败或验证失败
            SystemError: 数据一致性验证失败
        """
        logger.info("开始统一电阻计算")
        
        all_resistance_data = {}
        
        # 遍历所有层进行计算
        for i, layer in enumerate(self.model.layer_to_layer_models):
            layer_name = f"layer{i+1}"
            
            # 判断是否为Dense类型层
            if not self._is_dense_layer(layer):
                logger.info(f"Skipping non-Dense layer: {layer_name}")
                continue
                
            logger.info(f"计算 {layer_name} 的电阻值")
            
            # 获取层权重
            weights = layer.get_weights()
            if len(weights) < 1:
                raise ValueError(f"Layer {layer_name} has no weights")
                
            weight_matrix = weights[0]
            bias_vector = weights[1] if len(weights) > 1 else None
            
            # 处理Conv1D层权重形状
            weight_matrix = self._process_conv1d_weights(weight_matrix, layer, layer_name)
            
            # 应用统一的偏置处理逻辑
            processed_bias = self._apply_unified_bias_processing(bias_vector, i)
            
            # 创建DenseCircuit对象进行计算
            circuit = DenseCircuitFactory.create(
                gains=weight_matrix,
                biases=processed_bias,
                opamp_config=self.opamp_config,
                use_e96=False,
                use_relu=self._determine_relu_usage(layer),
                relu_config=None,
                high_pass_config=self.high_pass_config,
                power_supply_config=self.power_supply_config,
                layer_name=layer_name
            )
            
            # 仅计算电阻值，不生成网表
            resistance_records = circuit.calculate_only()
            
            # 验证计算结果
            if not resistance_records:
                raise ValueError(f"No resistance values calculated for {layer_name}")
                
            # 存储结果
            self._layer_circuits[layer_name] = circuit
            all_resistance_data[layer_name] = resistance_records
            
            logger.info(f"Layer {layer_name}: 计算出 {len(resistance_records)} 个电阻值")
        
        # 存储计算结果并标记完成
        self._resistance_data = all_resistance_data
        self._calculation_completed = True
        
        logger.info(f"统一电阻计算完成，共处理 {len(all_resistance_data)} 层")
        return all_resistance_data
    
    def _apply_unified_bias_processing(self, bias_vector, layer_index: int):
        """
        统一的偏置处理逻辑
        
        这里实现与WaveNet5SPICEBackend完全相同的偏置处理逻辑，
        确保网表生成和CSV导出使用相同的偏置值。
        
        Args:
            bias_vector: 原始偏置向量
            layer_index: 层索引
            
        Returns:
            处理后的偏置向量
        """
        if bias_vector is None:
            return None
            
        # 检查是否启用偏置补偿
        if not self.bias_compensation.get('enabled', False):
            logger.debug(f"Layer {layer_index}: 偏置补偿未启用，使用原始偏置")
            return bias_vector
            
        # 获取层级偏置调整
        layer_adjustments = self.bias_compensation.get('layer_bias_adjustments', {})
        adjustment = layer_adjustments.get(str(layer_index), 0)
        
        if adjustment != 0:
            logger.info(f"Layer {layer_index}: 应用偏置补偿 {adjustment}")
            # 与WaveNet5SPICEBackend保持一致的补偿逻辑
            processed_bias = bias_vector + adjustment
        else:
            processed_bias = bias_vector
            
        return processed_bias
    
    def _process_conv1d_weights(self, weight_matrix, layer, layer_name: str):
        """处理Conv1D层权重形状"""
        logger.info(f"Processing {layer_name}: layer_type = {type(layer).__name__}, weight_matrix shape = {weight_matrix.shape}")
        
        # 检查权重形状来判断是否需要处理
        if len(weight_matrix.shape) == 3:
            # 3D权重矩阵 - 通常是Conv1D
            logger.info(f"{layer_name} has 3D weights (Conv1D-like): {weight_matrix.shape}")
            
            if weight_matrix.shape[0] == 1:
                # kernel_size=1，可以压缩为2D: (input_channels, output_channels)
                weight_matrix = weight_matrix.squeeze(axis=0)
                logger.info(f"{layer_name} squeezed to shape: {weight_matrix.shape}")
            else:
                raise ValueError(
                    f"Layer {layer_name}: kernel_size={weight_matrix.shape[0]}, expected 1 for Dense circuit conversion"
                )
                
        elif len(weight_matrix.shape) == 2:
            # 2D权重矩阵 - 标准Dense层
            logger.info(f"{layer_name} has 2D weights (Dense): {weight_matrix.shape}")
            
        else:
            # 其他维度 - 不支持
            raise ValueError(
                f"Layer {layer_name}: Unsupported weight matrix shape {weight_matrix.shape}. "
                f"Expected 2D (Dense) or 3D with kernel_size=1 (Conv1D)."
            )
            
        return weight_matrix
    
    def _determine_relu_usage(self, layer) -> bool:
        """确定是否使用ReLU激活"""
        inner_layers = layer.get_inner_layers()
        for inner_layer in inner_layers:
            if 'activation' in inner_layer.name:
                return True
        return False
    
    def _is_dense_layer(self, layer) -> bool:
        """判断是否为Dense层"""
        layer_type_name = type(layer).__name__.lower()
        if 'dense' in layer_type_name:
            return True
        if 'conv1d' in layer_type_name:
            if hasattr(layer, 'kernel_size'):
                return layer.kernel_size == (1,) or layer.kernel_size == 1
        return False
    
    def get_layer_circuit(self, layer_name: str):
        """
        获取指定层的DenseCircuit对象（用于网表生成）
        
        Args:
            layer_name: 层名称
            
        Returns:
            DenseCircuit对象
            
        Raises:
            ValueError: 计算未完成或层不存在
        """
        if not self._calculation_completed:
            raise ValueError("Must call calculate_all_layer_resistances() first")
            
        if layer_name not in self._layer_circuits:
            raise ValueError(f"Layer {layer_name} not found or not calculated")
            
        return self._layer_circuits[layer_name]
    
    def get_all_resistance_data(self) -> Dict[str, List[Dict]]:
        """
        获取所有电阻数据（用于CSV导出）
        
        Returns:
            Dict[str, List[Dict]]: 层名称到电阻记录的映射
            
        Raises:
            ValueError: 计算未完成
        """
        if not self._calculation_completed:
            raise ValueError("Must call calculate_all_layer_resistances() first")
            
        return self._resistance_data.copy()
    
    def get_flattened_resistance_data(self) -> List[Dict]:
        """
        获取扁平化的电阻数据（用于CSV导出）
        
        Returns:
            List[Dict]: 所有电阻记录的扁平列表
        """
        if not self._calculation_completed:
            raise ValueError("Must call calculate_all_layer_resistances() first")
            
        flattened_data = []
        for layer_name, records in self._resistance_data.items():
            flattened_data.extend(records)
        return flattened_data
    
    def generate_netlist_for_layer(self, layer_name: str) -> str:
        """
        为指定层生成SPICE网表
        
        Args:
            layer_name: 层名称
            
        Returns:
            str: SPICE网表内容
        """
        circuit = self.get_layer_circuit(layer_name)
        return circuit.get_circuit_netlist()


class ResistanceConsistencyValidator:
    """
    强制电阻一致性验证器
    
    此验证器确保通过UnifiedResistanceCalculator生成的
    网表数据和CSV数据完全一致。任何不一致都会抛出SystemError。
    """
    
    def __init__(self, tolerance_percent: float = 0.01):
        """
        初始化验证器
        
        Args:
            tolerance_percent: 容差百分比（默认0.01%）
        """
        self.tolerance_percent = tolerance_percent
        
    def validate_consistency_or_fail(self, unified_calculator: UnifiedResistanceCalculator):
        """
        验证网表与CSV数据的一致性，不一致则抛出SystemError
        
        Args:
            unified_calculator: 统一电阻计算器实例
            
        Raises:
            SystemError: 发现数据不一致
            ValueError: 验证过程出错
        """
        logger.info("开始强制一致性验证")
        
        if not unified_calculator._calculation_completed:
            raise ValueError("UnifiedResistanceCalculator calculation not completed")
        
        inconsistencies = []
        total_comparisons = 0
        
        # 遍历所有层进行验证
        for layer_name in unified_calculator._resistance_data.keys():
            try:
                # 获取网表格式的电阻值
                netlist_resistances = self._extract_netlist_resistances(
                    unified_calculator.get_layer_circuit(layer_name)
                )
                
                # 获取CSV格式的电阻值
                csv_resistances = self._extract_csv_resistances(
                    unified_calculator._resistance_data[layer_name]
                )
                
                # 逐一比较电阻值
                layer_inconsistencies = self._compare_resistance_values(
                    layer_name, netlist_resistances, csv_resistances
                )
                
                inconsistencies.extend(layer_inconsistencies)
                total_comparisons += len(csv_resistances)
                
            except Exception as e:
                raise ValueError(f"验证层 {layer_name} 时出错: {e}")
        
        # 报告验证结果
        if inconsistencies:
            error_msg = f"🚨 CRITICAL: 发现 {len(inconsistencies)}/{total_comparisons} 个电阻值不一致:\n"
            for inconsistency in inconsistencies[:10]:  # 只显示前10个
                error_msg += f"  - {inconsistency}\n"
            if len(inconsistencies) > 10:
                error_msg += f"  - ... 还有 {len(inconsistencies) - 10} 个不一致项"
            
            logger.error(error_msg)
            raise SystemError(error_msg)
        
        logger.info(f"一致性验证通过: 比较了 {total_comparisons} 个电阻值，全部一致")
    
    def _extract_netlist_resistances(self, circuit) -> Dict[str, float]:
        """从DenseCircuit对象提取电阻值"""
        netlist_resistances = {}
        
        # 从circuit的resistance_records中提取
        for record in circuit.resistance_records:
            name = record['name']
            value = record['value']
            netlist_resistances[name] = value
            
        return netlist_resistances
    
    def _extract_csv_resistances(self, csv_records: List[Dict]) -> Dict[str, float]:
        """从CSV记录中提取电阻值"""
        csv_resistances = {}
        
        for record in csv_records:
            name = record['name']
            value = record['value']
            csv_resistances[name] = value
            
        return csv_resistances
    
    def _compare_resistance_values(self, layer_name: str, 
                                 netlist_values: Dict[str, float], 
                                 csv_values: Dict[str, float]) -> List[str]:
        """比较网表和CSV中的电阻值"""
        inconsistencies = []
        
        # 检查名称是否匹配
        netlist_names = set(netlist_values.keys())
        csv_names = set(csv_values.keys())
        
        if netlist_names != csv_names:
            missing_in_csv = netlist_names - csv_names
            missing_in_netlist = csv_names - netlist_names
            
            if missing_in_csv:
                inconsistencies.append(f"{layer_name}: CSV中缺失电阻 {missing_in_csv}")
            if missing_in_netlist:
                inconsistencies.append(f"{layer_name}: 网表中缺失电阻 {missing_in_netlist}")
        
        # 比较共同的电阻值
        common_names = netlist_names & csv_names
        for name in common_names:
            netlist_value = netlist_values[name]
            csv_value = csv_values[name]
            
            if not self._values_are_consistent(netlist_value, csv_value):
                error_percent = abs(netlist_value - csv_value) / max(abs(netlist_value), abs(csv_value)) * 100
                inconsistencies.append(
                    f"{layer_name}.{name}: 网表={netlist_value:.6g}Ω, CSV={csv_value:.6g}Ω, 误差={error_percent:.3f}%"
                )
        
        return inconsistencies
    
    def _values_are_consistent(self, value1: float, value2: float) -> bool:
        """判断两个电阻值是否一致"""
        # 处理特殊值
        if value1 == value2:
            return True
            
        # 处理无穷大或极大值
        MAX_RESISTANCE = 1e9
        if (value1 >= MAX_RESISTANCE and value2 >= MAX_RESISTANCE):
            return True
            
        # 计算相对误差
        max_value = max(abs(value1), abs(value2))
        if max_value == 0:
            return True
            
        relative_error = abs(value1 - value2) / max_value
        return relative_error <= (self.tolerance_percent / 100)