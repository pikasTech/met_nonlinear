import logging
logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
'\nWaveNet5专用SPICE推理后端 - 重构为统一架构\n\n基于统一电阻计算核心架构，确保与CSV导出数据完全一致。\n'
import os
import numpy as np
from typing import Union, List, Dict
from pathlib import Path
from calibration_analyzer.wavedata import WaveData, WaveRecord
from .backends.spice.backend import SPICEBackend
from spice_simulator.unified_resistance_calculator import UnifiedResistanceCalculator, ResistanceConsistencyValidator

class WaveNet5SPICEBackend(SPICEBackend):
    """
    WaveNet5专用的SPICE推理后端 - 基于统一架构
    
    统一架构特性：
    - 使用UnifiedResistanceCalculator确保数据一致性
    - 强制验证网表与CSV导出的一致性
    - 统一处理偏置补偿和配置传递
    - SVF层相位修正
    - Dense层ReLU反相处理
    """

    def __init__(self, model=None, output_folder=None, ngspice_path=None, inference_config=None):
        """
        初始化WaveNet5专用SPICE推理后端
        
        参数:
            model: WaveNet5模型对象
            output_folder: SPICE临时文件和模型输出的文件夹(None时使用项目data目录)
            ngspice_path: NGspice可执行文件路径
            inference_config: 推理配置对象，包含完整的SPICE配置信息
        """
        # 强制使用传入的output_folder（方案2实现）
        # 不依赖model.project_path，保持单一职责原则
        if output_folder is None:
            # 只有在完全没有指定时才使用默认回退路径
            output_folder = os.path.join('data', 'spice_netlists')
            logger.warning("警告：未指定output_folder，使用默认根目录路径")
        
        # 确保目录存在
        os.makedirs(output_folder, exist_ok=True)
        logger.info(f"使用SPICE输出目录: {output_folder}")
        
        super().__init__(model, output_folder, ngspice_path, inference_config)
        self.model_type = 'WaveNet5'
        
        # 统一架构组件
        self.unified_calculator = None
        self.consistency_validator = ResistanceConsistencyValidator(tolerance_percent=0.01)
        
        logger.info("WaveNet5SPICEBackend initialized with unified architecture")
        logger.info(f"Inference config provided: {bool(inference_config)}")
    
    def export_model_to_spice(self, output_path=None):
        """
        基于统一架构的SPICE模型导出
        
        统一架构特性：
        1. 使用UnifiedResistanceCalculator作为唯一计算来源
        2. 强制验证网表与CSV数据的一致性
        3. 统一处理所有inference_config参数
        
        参数:
            output_path: 输出SPICE模型文件路径，如果为None则生成默认路径
            
        返回:
            SPICE模型对象列表（保持与原有接口兼容）
            
        Raises:
            SystemError: 数据一致性验证失败
        """
        logger.info("开始基于统一架构的SPICE模型导出")
        
        # 生成默认输出路径（如果未提供）
        if output_path is None:
            model_name = getattr(self.model, 'model_name', 'WaveNet5')
            output_path = os.path.join(self.output_folder, f'{model_name}_spice_model.cir')
            logger.info(f"使用默认输出路径: {output_path}")
        
        # 验证模型结构
        if not hasattr(self.model, 'layer_to_layer_models'):
            raise ValueError("Model must have layer_to_layer_models attribute for unified architecture")
        
        # === 步骤1: 生成IIR层（第一层）的SPICE模型 ===
        logger.info("生成IIR层SPICE模型")
        if len(self.model.layer_to_layer_models) < 1:
            raise ValueError("Model has no layers in layer_to_layer_models")
        
        iir_layer = self.model.layer_to_layer_models[0]  # IIR层总是第一个
        
        # 验证第一层是否为IIR/SVF层
        if not (hasattr(iir_layer, 'center_freqs') and hasattr(iir_layer, 'quality_factors')):
            logger.warning("First layer does not have center_freqs/quality_factors, might not be IIR/SVF layer")
            logger.info(f"First layer type: {type(iir_layer).__name__}")
        
        # 调用IIR层的to_spice方法
        logger.info(f"调用 {type(iir_layer).__name__}.to_spice() 方法")
        iir_spice = iir_layer.to_spice(
            output_path=None,  # 不输出文件，只返回对象
            opamp_config=self.inference_config.get('opamp_config'),
            use_e96=False,
            amp=1.0,
            power_supply_config=self.inference_config.get('power_supply')
        )
        
        if iir_spice is None:
            raise ValueError("IIR layer to_spice() returned None")
        if isinstance(iir_spice, str):
            raise ValueError(f"IIR layer to_spice() returned error string: {iir_spice}")
        
        logger.info(f"IIR层SPICE模型生成成功: {type(iir_spice).__name__}")
        
        # === 步骤2: 处理Dense层 ===
        # 创建统一电阻计算核心
        logger.info("初始化UnifiedResistanceCalculator")
        self.unified_calculator = UnifiedResistanceCalculator(
            model=self.model,
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
        
        # === 步骤3: 组装完整的SPICE模型列表 ===
        logger.info("生成完整SPICE模型对象列表")
        spice_model_list = []
        
        # 先添加IIR层
        spice_model_list.append(iir_spice)
        logger.info(f"已添加IIR层（layer1）到SPICE模型列表，类型: {type(iir_spice).__name__}")
        
        # 保存IIR层网表文件
        if output_path:
            layer1_output_path = self._get_layer_output_path(output_path, 'layer1')
            if layer1_output_path and hasattr(iir_spice, 'get_circuit_netlist'):
                netlist_content = iir_spice.get_circuit_netlist()
                with open(layer1_output_path, 'w', encoding='utf-8') as f:
                    f.write(netlist_content)
                logger.info(f"Layer1 (IIR) netlist saved to: {layer1_output_path}")
        
        # 再添加Dense层（按层名排序确保顺序）
        for layer_name in sorted(resistance_data_by_layer.keys()):
            try:
                circuit = self.unified_calculator.get_layer_circuit(layer_name)
                spice_model_list.append(circuit)
                logger.info(f"已添加{layer_name}到SPICE模型列表，类型: {type(circuit).__name__}")
                
                # 保存层级网表文件
                if output_path:
                    layer_output_path = self._get_layer_output_path(output_path, layer_name)
                    if layer_output_path and hasattr(circuit, 'get_circuit_netlist'):
                        netlist_content = circuit.get_circuit_netlist()
                        with open(layer_output_path, 'w', encoding='utf-8') as f:
                            f.write(netlist_content)
                        logger.info(f"Layer {layer_name} netlist saved to: {layer_output_path}")
                    
            except Exception as e:
                logger.error(f"生成层 {layer_name} 的SPICE对象失败: {e}")
                raise ValueError(f"Failed to generate SPICE object for {layer_name}: {e}")
        
        logger.info(f"统一架构SPICE导出成功: {len(spice_model_list)} 层（1个IIR层 + {len(resistance_data_by_layer)}个Dense层），已通过一致性验证")
        return spice_model_list
    
    def _get_layer_output_path(self, base_output_path: str, layer_name: str) -> str:
        """生成层级网表文件路径"""
        if base_output_path:
            path_obj = Path(base_output_path)
            return str(path_obj.parent / f"{path_obj.stem}_{layer_name}.cir")
        else:
            return None

    # 注意：原有的偏置补偿方法已移除，现在由UnifiedResistanceCalculator统一处理
    # _prepare_bias_compensations, _apply_compensations_to_layers, _cleanup_compensations
    # 这些功能已集成到统一核心架构中

    def infer(self, input_wave_data: Union[str, WaveData], use_scaler=False, return_layers=False, return_numpy=False, layers=None) -> Union[WaveData, List[WaveData], Dict[str, List[WaveData]]]:
        """
        使用WaveNet5专用SPICE模型对输入波形进行推理
        
        在基类功能基础上添加WaveNet5特定的相位修正处理
        
        参数:
            input_wave_data: 输入波形数据对象或波形文件路径
            use_scaler: 是否使用缩放器
            return_layers: 是否返回分层结果
            return_numpy: 是否同时返回NumPy仿真结果
            layers: 只推理前N层（None表示推理所有层）
            
        返回:
            推理结果，格式取决于参数设置
        """
        # 偏置补偿现在在 export_model_to_spice 中处理
        results = super().infer(input_wave_data, use_scaler, return_layers, return_numpy, layers)
        if return_layers:
            if isinstance(results, dict) and 'spice' in results:
                spice_outputs = results['spice']
                corrected_spice = self._apply_wavenet5_post_processing(spice_outputs)
                results['spice'] = corrected_spice
            elif isinstance(results, list):
                results = self._apply_wavenet5_post_processing(results)
        return results

    def _apply_wavenet5_post_processing(self, spice_layer_outputs):
        """
        应用WaveNet5特定的后处理
        
        注意：相位修正已经在SPICEBackend的即时修正中完成，
        这里仅保留必要的后处理逻辑
        
        参数:
            spice_layer_outputs: SPICE推理的分层输出列表
            
        返回:
            后处理后的分层输出列表
        """
        return spice_layer_outputs

    def _is_svf_layer_output(self, wave_data, layer_index):
        """
        判断层输出是否为SVF层
        
        判断依据：
        WaveNet5有且只有第1层（索引0）是SVF层，这是固定的架构特征
        
        参数:
            wave_data: WaveData对象
            layer_index: 层索引（从0开始）
            
        返回:
            bool: 是否为SVF层
        """
        return layer_index == 0

    def _correct_svf_phase(self, wave_data):
        """
        对SVF层输出进行相位修正
        
        修正方案：
        - HP通道（索引 0, 3, 6, ...）：反相
        - BP通道（索引 1, 4, 7, ...）：保持不变
        - LP通道（索引 2, 5, 8, ...）：反相
        
        参数:
            wave_data: 原始WaveData对象
            
        返回:
            修正后的WaveData对象
        """
        corrected_data = WaveData(description=f'{wave_data.description} (WaveNet5 Phase Corrected)' if wave_data.description else 'WaveNet5 Phase Corrected', author=wave_data.author)
        if hasattr(wave_data, 'user_metadata'):
            for key, value in wave_data.user_metadata.items():
                corrected_data.add_user_metadata(key, value)
        corrected_data.add_user_metadata('wavenet5_phase_corrected', True)
        corrected_data.add_user_metadata('processed_by', 'WaveNet5SPICEBackend')
        for record in wave_data.records:
            corrected_record_data = record.data.copy()
            num_channels = corrected_record_data.shape[1]
            num_svf = num_channels // 3
            for svf_idx in range(num_svf):
                hp_channel = svf_idx * 3 + 0
                lp_channel = svf_idx * 3 + 2
                corrected_record_data[:, hp_channel] *= -1
                corrected_record_data[:, lp_channel] *= -1
            corrected_record = WaveRecord(data=corrected_record_data, sample_rate=record.sample_rate, channel_names=record.channel_names, record_id=record.record_id, user_metadata={**record.user_metadata, 'phase_corrected': True, 'wavenet5_backend': True})
            corrected_data.add_record(corrected_record)
        return corrected_data

    def post_process_layer_output(self, layer_output, layer_index, layer_type=None):
        """
        WaveNet5特定的层输出后处理
        
        参数:
            layer_output: 层输出数据
            layer_index: 层索引（从0开始）
            layer_type: 层类型（可选）
            
        返回:
            后处理后的层输出
        """
        return layer_output

    def get_model_info(self):
        """
        获取WaveNet5模型信息
        
        返回:
            dict: 模型信息字典
        """
        base_info = super().get_model_info() if hasattr(super(), 'get_model_info') else {}
        wavenet5_info = {'backend_type': 'WaveNet5SPICEBackend', 'model_type': self.model_type, 'supports_svf_phase_correction': True, 'supports_dense_relu_processing': True, 'version': '1.0.0'}
        return {**base_info, **wavenet5_info}