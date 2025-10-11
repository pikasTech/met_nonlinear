import logging
logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
'\nSPICE对比分析模块\n\n此模块包含SPICE后端相关的对比分析功能，包括：\n- SPICE对比数据生成\n- SPICE与分层后端的对比分析\n- SPICE相关路径管理\n'
import os
import numpy as np
from typing import Union, Optional, Dict, Any, List
from calibration_analyzer.waveprocessor import WaveProcessor
from calibration_analyzer.wavedata import WaveData, WaveRecord
from models.layer_support import LayeredModelSupport

class SPICEAnalyzer:
    """
    SPICE分析器
    
    负责处理SPICE后端相关的对比分析功能
    """

    def __init__(self, processor):
        """
        初始化SPICE分析器
        
        参数:
            processor: InferenceProcessor实例
        """
        self.processor = processor
        self.wave_processor = processor.wave_processor
        self.model = processor.model
        self.model_engine = processor.model_engine

    def get_spice_comparison_paths(self, comparison_dir: str) -> Dict[str, Any]:
        """
        从指定目录获取SPICE对比数据文件路径

        参数:
            comparison_dir: 对比数据目录路径

        返回:
            Dict[str, Any]: 包含文件路径的字典
        """
        if not os.path.exists(comparison_dir):
            return {}
        spice_paths = []
        layer_paths = []
        for f in sorted(os.listdir(comparison_dir)):
            if f.startswith('spice_layer_') and f.endswith('.wave'):
                spice_paths.append(os.path.join(comparison_dir, f))
            elif f.startswith('layer_') and f.endswith('.wave'):
                layer_paths.append(os.path.join(comparison_dir, f))
        return {'layer_output_paths': layer_paths, 'spice_output_paths': spice_paths, 'output_dir': comparison_dir}

    def generate_spice_comparison_data(self, input_wave_path: str, output_dir: str='data/spice_comparison', use_scaler: bool=False):
        """
        生成 SPICE 后端和分层后端的对比数据并保存到文件

        参数:
            input_wave_path: 输入波形文件路径
            output_dir: 输出目录路径
            use_scaler: 是否使用缩放器
        """
        logger.info('开始生成 SPICE 后端和分层后端的对比数据...')
        input_wave_data = self.processor.load_input_wave(input_wave_path)
        if use_scaler and hasattr(self.model_engine, 'scaler') and (self.model_engine.scaler is not None):
            input_wave_data = self.processor.data_processor._apply_input_scaling(input_wave_data)
            logger.info('已对输入数据应用缩放器')
        if not isinstance(self.model, LayeredModelSupport):
            raise ValueError('模型必须实现 LayeredModelSupport 接口才能进行对比实验')
        os.makedirs(output_dir, exist_ok=True)
        current_backend_type = self.processor.backend_type
        logger.info('使用分层后端进行推理...')
        self.processor.set_backend('layer_by_layer')
        layer_outputs = self.processor.backend.infer(input_wave_data, use_scaler=False)
        if use_scaler and hasattr(self.model_engine, 'scaler') and (self.model_engine.scaler is not None):
            layer_outputs[-1] = self.processor.data_processor._apply_output_inverse_scaling(layer_outputs[-1])
            logger.info('已对分层最后一层输出数据应用反缩放器')
        for i, layer_output in enumerate(layer_outputs):
            output_path = os.path.join(output_dir, f'layer_{i + 1}.wave')
            self.processor.save_output_wave(layer_output, output_path)
        logger.info('使用 SPICE 后端进行推理...')
        self.processor.set_backend('spice')
        layered_models = self.model.get_layered_models()
        logger.info('正在导出分层 SPICE 模型...')
        logger.info('正在使用 SPICE 进行逐层仿真...')
        spice_input = self.processor.load_input_wave(input_wave_path)
        current_input = spice_input
        if use_scaler and hasattr(self.model_engine, 'scaler') and (self.model_engine.scaler is not None):
            current_input = self.processor.data_processor._apply_input_scaling(spice_input)
        for i, layer_model in enumerate(layered_models):
            logger.info(f'正在对第 {i + 1}/{len(layered_models)} 层进行 SPICE 仿真...')
            layer_output = self.processor.backend.simulate_with_spice(layer_model, current_input, output_name=f'layer_{i + 1}_output')
            layer_info = {}
            if hasattr(layered_models[i], 'get_layer_info'):
                layer_info = layered_models[i].get_layer_info()
            layer_output.add_user_metadata('layer_info', layer_info)
            layer_output.add_user_metadata('layer_index', i)
            output_path = os.path.join(output_dir, f'spice_layer_{i + 1}.wave')
            if i == len(layered_models) - 1 and use_scaler and hasattr(self.model_engine, 'scaler') and (self.model_engine.scaler is not None):
                layer_output = self.processor.data_processor._apply_output_inverse_scaling(layer_output)
                logger.info('已对 SPICE 最后一层输出数据应用反缩放器')
            self.processor.save_output_wave(layer_output, output_path)
            current_input = layer_output
        self.processor.set_backend(current_backend_type)
        logger.info(f'对比数据已生成并保存到 {output_dir} 目录')

    def analyze_spice_comparison(self, comparison_dir: str) -> Dict[str, Any]:
        """
        分析 SPICE 后端和分层后端的对比数据

        参数:
            comparison_dir: 对比数据目录路径

        返回:
            Dict[str, Any]: 包含对比结果统计信息的字典
        """
        logger.info('开始分析 SPICE 后端和分层后端的对比数据...')
        comparison_data = self.get_spice_comparison_paths(comparison_dir)
        if not comparison_data:
            logger.info(f'警告: 在目录 {comparison_dir} 中找不到对比数据文件')
            return {}
        loaded_layer_outputs = []
        for path in comparison_data['layer_output_paths']:
            loaded_layer_outputs.append(self.processor.load_input_wave(path))
        loaded_spice_outputs = []
        for path in comparison_data['spice_output_paths']:
            loaded_spice_outputs.append(self.processor.load_input_wave(path))
        comparison_stats = []
        if len(loaded_layer_outputs) != len(loaded_spice_outputs):
            logger.info(f'警告: 分层后端 ({len(loaded_layer_outputs)} 层) 和 SPICE后端 ({len(loaded_spice_outputs)} 层) 的层数不同')
            min_layers = min(len(loaded_layer_outputs), len(loaded_spice_outputs))
            logger.info(f'将只对比前 {min_layers} 层')
        else:
            min_layers = len(loaded_layer_outputs)
        for i in range(min_layers):
            layer_info = loaded_layer_outputs[i].user_metadata.get('layer_info', {})
            layer_name = layer_info.get('name', f'Layer {i + 1}')
            logger.info(f'\n对比第 {i + 1}/{min_layers} 层: {layer_name}')
            layer_stats = self.processor.visualizer.visualize_layer_comparison(loaded_layer_outputs[i], loaded_spice_outputs[i], i, layer_name)
            layer_stats['layer_index'] = i
            layer_stats['layer_name'] = layer_name
            comparison_stats.append(layer_stats)
        logger.info('\n对比分析完成!')
        return {'comparison_stats': comparison_stats, 'layer_outputs': loaded_layer_outputs, 'spice_layer_outputs': loaded_spice_outputs}