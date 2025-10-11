"""
数据验证模块

负责推理数据的前置条件验证和文件检查
"""

import os
import logging
from pathlib import Path
from typing import Optional, List, Tuple, Dict

logger = logging.getLogger(__name__)


class DataValidator:
    """数据验证器类"""
    
    def __init__(self, project_path: str, checkpoint_dir: str, config: Dict):
        """
        初始化数据验证器
        
        参数:
            project_path: 项目路径
            checkpoint_dir: 检查点目录
            config: 配置对象
        """
        self.project_path = project_path
        self.checkpoint_dir = checkpoint_dir
        self.config = config
        self.project_name = os.path.basename(project_path)
    
    def validate_inference_prerequisites(self) -> bool:
        """
        验证推理所需的前置条件
        
        返回:
            bool: 验证是否通过
            
        抛出:
            FileNotFoundError: 当必需的文件不存在时
        """
        weight_files = [
            os.path.join(self.checkpoint_dir, 'best_val.weights.h5'),
            os.path.join(self.checkpoint_dir, 'best.weights.h5'),
            os.path.join(self.checkpoint_dir, 'best_val.weights.json'),
            os.path.join(self.checkpoint_dir, 'best.weights.json')
        ]
        
        if not any(os.path.exists(f) for f in weight_files):
            raise FileNotFoundError(
                f'未找到任何模型权重文件。\n期望位置: \n' + 
                '\n'.join(f'  - {f}' for f in weight_files) + 
                f'\n请先训练模型或确保权重文件存在。'
            )
        
        return True
    
    def check_existing_inference_data(self, data_dir: str) -> bool:
        """
        检查是否已有推理数据
        
        参数:
            data_dir: 推理数据目录
            
        返回:
            bool: 是否存在有效的推理数据
        """
        nn_layers_dir = os.path.join(data_dir, 'nn_layers')
        spice_layers_dir = os.path.join(data_dir, 'spice_layers')
        numpy_layers_dir = os.path.join(data_dir, 'numpy_layers')
        
        # 基本检查：必须有nn和spice目录
        if not os.path.exists(nn_layers_dir) or not os.path.exists(spice_layers_dir):
            return False
        
        # 检查layer文件
        nn_all_files = os.listdir(nn_layers_dir)
        spice_all_files = os.listdir(spice_layers_dir)
        
        nn_files = [f for f in nn_all_files 
                   if (f.startswith('layer_') or '_layer' in f) and f.endswith('.wave')]
        spice_files = [f for f in spice_all_files 
                      if (f.startswith('layer_') or '_layer' in f) and f.endswith('.wave')]
        
        has_data = len(nn_files) > 0 and len(spice_files) > 0
        
        return has_data
    
    def find_input_file(self, dataset_type: Optional[str] = None) -> str:
        """
        查找推理输入文件
        只查找 data/wave_output/dataset_{TYPE}_output_original.wave
            
        参数:
            dataset_type: 数据集类型，如果不提供则从config获取
            
        返回:
            str: wave文件路径
            
        抛出:
            FileNotFoundError: 文件不存在时报错并提示使用 -w 生成
        """
        if dataset_type is None:
            dataset_type = self.config.get('dataset_type', 'unknown')
            
        wave_output_dir = os.path.join(self.project_path, 'data', 'wave_output')
        target_file = f'dataset_{dataset_type}_output_original.wave'
        target_path = os.path.join(wave_output_dir, target_file)
        
        if os.path.exists(target_path):
            relative_path = os.path.relpath(target_path, self.project_path)
            logger.info(f'[OK] 使用wave文件: {relative_path}')
            return target_path
        
        # 构建详细的错误信息
        error_msg = f'未找到推理输入文件: {target_file}\n'
        
        if not os.path.exists(wave_output_dir):
            error_msg += f'\nwave输出目录不存在: {wave_output_dir}\n'
        else:
            wave_files = [f for f in os.listdir(wave_output_dir) if f.endswith('.wave')]
            if wave_files:
                error_msg += f'\nwave输出目录中找到以下文件:\n'
                for f in wave_files:
                    error_msg += f'  - {f}\n'
                error_msg += f'\n但需要的是: {target_file}\n'
            else:
                error_msg += f'\nwave输出目录为空\n'
        
        error_msg += f'\n请先运行以下命令生成wave数据:\n'
        error_msg += f'  python cli.py -w {self.project_name}\n'
        
        raise FileNotFoundError(error_msg)
    
    def validate_file_format(self, file_path: str) -> bool:
        """
        验证文件格式是否正确
        
        参数:
            file_path: 文件路径
            
        返回:
            bool: 格式是否有效
        """
        if not os.path.exists(file_path):
            return False
            
        # 这里可以添加更多的格式验证逻辑
        # 例如检查文件大小、文件头等
        
        return True
    
    def check_data_integrity(self, data_dir: str) -> Dict[str, any]:
        """
        检查数据完整性
        
        参数:
            data_dir: 数据目录
            
        返回:
            Dict: 包含完整性检查结果的字典
        """
        integrity_report = {
            'nn_layers': {'exists': False, 'count': 0, 'files': []},
            'spice_layers': {'exists': False, 'count': 0, 'files': []},
            'numpy_layers': {'exists': False, 'count': 0, 'files': []},
            'metadata': {'exists': False, 'valid': False},
            'input_data': {'exists': False, 'valid': False}
        }
        
        # 检查各层数据
        for layer_type in ['nn_layers', 'spice_layers', 'numpy_layers']:
            layer_dir = os.path.join(data_dir, layer_type)
            if os.path.exists(layer_dir):
                integrity_report[layer_type]['exists'] = True
                layer_files = [f for f in os.listdir(layer_dir) 
                             if (f.startswith('layer_') or '_layer' in f) and f.endswith('.wave')]
                integrity_report[layer_type]['count'] = len(layer_files)
                integrity_report[layer_type]['files'] = sorted(layer_files)
        
        # 检查元数据
        metadata_file = os.path.join(data_dir, 'inference_metadata.json')
        if os.path.exists(metadata_file):
            integrity_report['metadata']['exists'] = True
            try:
                import json
                with open(metadata_file, 'r') as f:
                    json.load(f)
                integrity_report['metadata']['valid'] = True
            except:
                integrity_report['metadata']['valid'] = False
        
        # 检查输入数据
        input_file = os.path.join(data_dir, 'input.wave')
        if os.path.exists(input_file):
            integrity_report['input_data']['exists'] = True
            integrity_report['input_data']['valid'] = self.validate_file_format(input_file)
        
        return integrity_report
    
    def validate_layer_consistency(self, data_dir: str) -> Tuple[bool, Optional[str]]:
        """
        验证各层数据的一致性
        
        参数:
            data_dir: 数据目录
            
        返回:
            Tuple[bool, Optional[str]]: (是否一致, 错误信息)
        """
        integrity = self.check_data_integrity(data_dir)
        
        # 检查nn和spice层数是否一致
        nn_count = integrity['nn_layers']['count']
        spice_count = integrity['spice_layers']['count']
        
        if nn_count != spice_count:
            return False, f'层数不一致：NN有{nn_count}层，SPICE有{spice_count}层'
        
        # 如果有numpy层，也要检查
        if integrity['numpy_layers']['exists'] and integrity['numpy_layers']['count'] > 0:
            numpy_count = integrity['numpy_layers']['count']
            if nn_count != numpy_count:
                return False, f'层数不一致：NN有{nn_count}层，NumPy有{numpy_count}层'
        
        # 检查模型特定的层数要求
        model_type = self.config.get('use_model', '')
        if 'WaveNet5' in model_type:
            expected_layers = 5
            if nn_count != expected_layers:
                return False, f'WaveNet5应该有{expected_layers}层，但数据显示{nn_count}层'
        
        return True, None