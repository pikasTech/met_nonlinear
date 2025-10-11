import logging
logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
'\nSPICE inference backend main class.\n\nThis module provides the core SPICEBackend class that coordinates\nSPICE circuit simulation for neural network models.\n'
import os
import sys
import shutil
import traceback
from typing import Union, List, Dict
from pathlib import Path
import numpy as np
from inference.common import DataRangeChecker
from inference.unified import InferenceResult
from models.layer_support import SpiceModelSupport
from calibration_analyzer.wavedata import WaveData, WaveRecord
from ..base import InferenceBackend
from .simulation import SPICESimulator
from .phase_correction import PhaseCorrector

class SPICEBackend(InferenceBackend):
    """
    SPICEBackend 类，用于将模型导出为 SPICE 格式并进行推理

    导出过程参考 export_svf_to_spice.py，使用 SPICE 模型进行推理得到 wave，参考 simu_sweep.py 文件。
    转换的实现在 model_layers.py。

    在转换时逐层转换，转换完成后，逐层进行推理，输入输出都是 wave 格式。
    """

    def __init__(self, model=None, output_folder=None, ngspice_path=None, inference_config=None):
        """
        初始化 SPICE 推理后端

        参数:
            model: 要使用的模型对象，必须支持分层导出到 SPICE
            output_folder: SPICE 临时文件和模型输出的文件夹(None时使用项目data目录)
            ngspice_path: NGspice 可执行文件路径，如果为 None 则使用默认路径
            inference_config: 推理配置对象，包含high_pass_config等信息
        """
        # 智能路径处理，与WaveNet5SPICEBackend保持一致
        if output_folder is None:
            # 尝试从模型获取项目路径
            if hasattr(model, 'project_path'):
                output_folder = os.path.join(model.project_path, 'data', 'spice_netlists')
            else:
                # 使用当前项目的默认路径
                output_folder = os.path.join('data', 'spice_netlists')
            # 确保目录存在
            os.makedirs(output_folder, exist_ok=True)
        
        # 设置临时文件目录 - 使用data/temp而不是spice_netlists
        if hasattr(model, 'project_path'):
            temp_folder = os.path.join(model.project_path, 'data', 'temp')
        else:
            temp_folder = os.path.join('data', 'temp')
        # 确保临时目录存在
        os.makedirs(temp_folder, exist_ok=True)
        
        super().__init__(model)
        self.output_folder = output_folder
        self.temp_folder = temp_folder
        self.ngspice_path = self._setup_ngspice_path(ngspice_path)
        # 将temp_folder传递给SPICESimulator，用于仿真临时文件
        self.simulator = SPICESimulator(self.temp_folder, self.ngspice_path)
        self.phase_corrector = PhaseCorrector()
        self.data_range_checker = DataRangeChecker()
        self.inference_config = inference_config or {}

    def _setup_ngspice_path(self, ngspice_path):
        """Setup NGspice executable path"""
        if ngspice_path is None:
            system_ngspice = shutil.which('ngspice')
            if system_ngspice:
                return system_ngspice
            else:
                current_dir = Path(__file__).parent.absolute()
                parent_dir = current_dir.parent.parent.parent
                return os.path.join(parent_dir, 'spice_simulator', 'Spice64', 'bin', 'ngspice_con.exe')
        else:
            return ngspice_path

    def export_model_to_spice(self, output_path=None):
        """
        将模型导出为 SPICE 格式

        参数:
            output_path: 输出 SPICE 模型文件路径，如果为 None 则使用默认路径

        返回:
            Union[str, object]: SPICE 模型文件的路径或 SPICE 对象
        """
        Path(self.output_folder).mkdir(exist_ok=True)
        if output_path is None:
            model_name = getattr(self.model, 'model_name', type(self.model).__name__)
            output_path = os.path.join(self.output_folder, f'{model_name}_spice_model.cir')
        if not hasattr(self.model, 'to_spice'):
            raise ValueError('模型不支持导出到 SPICE 格式，必须实现 to_spice 方法或支持分层导出')
        
        # 准备配置参数
        high_pass_config = None
        opamp_config = None
        if self.inference_config:
            high_pass_config = self.inference_config.get('high_pass_config', None)
            opamp_config = self.inference_config.get('opamp_config', None)
        
        spice_obj = self.model.to_spice(output_path=output_path, amp=1, 
                                       high_pass_config=high_pass_config,
                                       opamp_config=opamp_config)
        return spice_obj

    def infer(self, input_wave_data: Union[str, WaveData], use_scaler=False, return_layers=False, return_numpy=False, layers=None) -> Union[WaveData, List[WaveData], Dict[str, List[WaveData]]]:
        """
        使用 SPICE 模型对输入波形进行推理

        参数:
            input_wave_data: 输入波形数据对象或波形文件路径
            use_scaler: 是否使用缩放器
            return_layers: 是否返回每一层的推理结果
            return_numpy: 是否同时返回NumPy仿真结果
            layers: 只推理前N层（None表示推理所有层）

        返回:
            Union[WaveData, List[WaveData], Dict[str, List[WaveData]]]: 
            - 如果 return_layers=False: 返回最终推理结果 (WaveData)
            - 如果 return_layers=True, return_numpy=False: 返回各层SPICE结果列表 (List[WaveData])
            - 如果 return_layers=True, return_numpy=True: 返回字典 {'spice': List[WaveData], 'numpy': List[WaveData]}
        """
        input_wave_data = self._prepare_input_data(input_wave_data)
        try:
            spice_model = self.export_model_to_spice()
            if isinstance(spice_model, list):
                layered_spice_models = spice_model
                total_layers = len(layered_spice_models)
                
                # 确定要推理的层数
                if layers is not None:
                    num_layers_to_infer = min(layers, total_layers)
                    if layers > total_layers:
                        logger.warning(f'请求推理 {layers} 层，但模型只有 {total_layers} 层。将推理所有 {total_layers} 层。')
                else:
                    num_layers_to_infer = total_layers
                
                logger.info(f'模型支持分层推理，共有 {total_layers} 层，将推理前 {num_layers_to_infer} 层')
                current_input = input_wave_data
                current_input_numpy = input_wave_data
                layer_results = []
                numpy_layer_results = []
                
                # 确保SPICE和NumPy都只处理指定的层数
                for i in range(num_layers_to_infer):
                    layer_circuit = layered_spice_models[i]
                    logger.info(f'正在处理第 {i + 1}/{num_layers_to_infer} 层（模型共 {total_layers} 层）...')
                    layer_output = self.simulator.simulate_with_spice(layer_circuit, current_input, f'layer_{i + 1}_output')
                    if self.phase_corrector.needs_phase_correction(self.model, i + 1):
                        logger.info(f'第{i + 1}层相位修正:')
                        self.data_range_checker.check_wave_data(layer_output, f'SPICE修正前')
                        layer_output = self.phase_corrector.apply_immediate_phase_correction(layer_output, i + 1, self.model)
                        self.data_range_checker.check_wave_data(layer_output, f'SPICE修正后')
                    if return_layers:
                        layer_copy = WaveData(description=f'SPICE Layer {i + 1} Output', author='SPICE Simulation')
                        for record in layer_output.records:
                            layer_copy.add_record(record)
                        self._add_metadata(layer_copy, input_wave_data, f'SPICEBackend_Layer{i + 1}')
                        layer_copy.add_user_metadata('layer_index', i + 1)
                        layer_results.append(layer_copy)
                    if return_numpy:
                        logger.info(f'执行第{i + 1}层的NumPy仿真...')
                        numpy_layer_output = self.simulator.simulate_with_numpy(layer_circuit, current_input_numpy, f'numpy_layer_{i + 1}_output')
                        if self.phase_corrector.needs_phase_correction(self.model, i + 1):
                            logger.info(f'第{i + 1}层NumPy相位修正:')
                            self.data_range_checker.check_wave_data(numpy_layer_output, f'NumPy修正前')
                            numpy_layer_output = self.phase_corrector.apply_immediate_phase_correction(numpy_layer_output, i + 1, self.model)
                            self.data_range_checker.check_wave_data(numpy_layer_output, f'NumPy修正后')
                        if return_layers:
                            numpy_layer_copy = WaveData(description=f'NumPy Layer {i + 1} Output', author='NumPy Simulation')
                            for record in numpy_layer_output.records:
                                numpy_layer_copy.add_record(record)
                            self._add_metadata(numpy_layer_copy, input_wave_data, f'NumPyBackend_Layer{i + 1}')
                            numpy_layer_copy.add_user_metadata('layer_index', i + 1)
                            numpy_layer_results.append(numpy_layer_copy)
                        current_input_numpy = numpy_layer_output
                    current_input = layer_output
                if return_layers:
                    if return_numpy and numpy_layer_results:
                        return {'spice': layer_results, 'numpy': numpy_layer_results}
                    else:
                        return layer_results
                else:
                    output_wave_data = current_input
            else:
                circuit = spice_model
                output_wave_data = self.simulator.simulate_with_spice(circuit, input_wave_data)
                if return_layers:
                    self._add_metadata(output_wave_data, input_wave_data, 'SPICEBackend_Layer1')
                    output_wave_data.add_user_metadata('layer_index', 1)
                    return [output_wave_data]
            self._add_metadata(output_wave_data, input_wave_data, 'SPICEBackend')
            return output_wave_data
        except Exception as e:
            logger.info(f'SPICE 仿真过程中出错: {str(e)}')
            traceback.print_exc()
            raise

    def infer_unified(self, input_wave_data: Union[str, WaveData], use_scaler: bool=False, return_layers: bool=False, return_numpy: bool=False, **kwargs) -> InferenceResult:
        """
        统一格式的SPICE推理接口
        
        参数:
            input_wave_data: 输入波形数据对象或波形文件路径
            use_scaler: 是否使用缩放器
            return_layers: 是否返回分层结果
            return_numpy: 是否同时返回NumPy仿真结果
            **kwargs: 其他参数（包括layers参数）
            
        返回:
            InferenceResult: 统一格式的推理结果
        """
        layers = kwargs.get('layers', None)
        result = self.infer(input_wave_data, use_scaler, return_layers, return_numpy, layers=layers)
        input_path = ''
        if isinstance(input_wave_data, str):
            input_path = input_wave_data
        if isinstance(result, dict) and 'spice' in result and ('numpy' in result):
            return self._create_unified_result(backend_type='spice', layers_data=result['spice'], input_path=input_path, output_dir='', numpy_layers=result['numpy'])
        elif isinstance(result, list):
            return self._create_unified_result(backend_type='spice', layers_data=result, input_path=input_path, output_dir='', numpy_layers=None)
        else:
            return self._create_unified_result(backend_type='spice', layers_data=result, input_path=input_path, output_dir='', numpy_layers=None)