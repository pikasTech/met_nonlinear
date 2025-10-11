"""
推理执行模块

负责执行神经网络、SPICE和NumPy推理
"""

import os
import json
import time
import shutil
import logging
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class InferenceExecutor:
    """推理执行器类"""
    
    def __init__(self, project_path: str, project_name: str, config: Dict, wave_processor, project_manager=None):
        """
        初始化推理执行器
        
        参数:
            project_path: 项目路径
            project_name: 项目名称
            config: 配置对象
            wave_processor: Wave处理器实例
            project_manager: 项目管理器实例（依赖注入）
        """
        self.project_path = project_path
        self.project_name = project_name
        self.config = config
        self.wave_processor = wave_processor
        self.project_manager = project_manager
        self.quick_mode = False
        self.layers_limit = None
    
    def set_quick_mode(self, quick_mode: bool):
        """设置快速模式"""
        self.quick_mode = quick_mode
    
    def set_layers_limit(self, layers: Optional[int]):
        """设置层数限制"""
        self.layers_limit = layers
    
    def generate_inference_data(self, data_dir: str, input_wave: str) -> Dict[str, Any]:
        """
        生成推理数据
        
        参数:
            data_dir: 输出数据目录
            input_wave: 输入wave文件路径
            
        返回:
            Dict: 包含推理结果信息的字典
        """
        # 导入推理处理器
        try:
            import sys
            sys.path.append('inference')
            from inference.processor import InferenceProcessor
        except ImportError as e:
            raise ImportError(f'无法导入inference模块: {e}')
        
        # 创建推理处理器，传递project_manager和quick_mode
        processor = InferenceProcessor(self.project_path, self.project_manager, quick_mode=self.quick_mode)
        
        # 创建子目录
        nn_layers_dir = os.path.join(data_dir, 'nn_layers')
        spice_layers_dir = os.path.join(data_dir, 'spice_layers')
        
        # 执行神经网络推理
        nn_result = self._execute_neural_network_inference(processor, input_wave, data_dir)
        nn_outputs = [layer.file_path for layer in nn_result.layers]
        
        # 执行SPICE/NumPy推理
        logger.info('--- SPICE/NumPy推理 ---')
        spice_result, spice_outputs, numpy_outputs = self._execute_spice_inference(
            processor, input_wave, data_dir
        )
        
        # 保存输入数据
        self._save_input_data(processor, input_wave, data_dir)
        
        # 保存元数据
        metadata = self._save_inference_metadata(
            data_dir, input_wave, nn_outputs, spice_outputs, numpy_outputs, processor
        )
        
        return {
            'nn_outputs': nn_outputs,
            'spice_outputs': spice_outputs,
            'numpy_outputs': numpy_outputs,
            'metadata': metadata
        }
    
    def _execute_neural_network_inference(self, processor, input_wave: str, data_dir: str):
        """执行神经网络推理"""
        processor.set_backend('layer_by_layer')
        
        # 在日志中记录层数限制
        if self.layers_limit is not None:
            logger.info(f'  设置层数限制: {self.layers_limit}')
        
        nn_result = processor.infer_and_save(
            input_wave, 
            output_dir=data_dir, 
            use_scaler=True, 
            return_layers=True,
            layers=self.layers_limit  # 传递层数限制
        )
        logger.info(f'神经网络分层推理完成，保存了 {len(nn_result.layers)} 个文件')
        return nn_result
    
    def _execute_spice_inference(self, processor, input_wave: str, data_dir: str):
        """执行SPICE和NumPy推理"""
        try:
            processor.set_backend('spice')
            
            # 在日志中记录层数限制
            if self.layers_limit is not None:
                logger.info(f'  设置层数限制: {self.layers_limit}')
            
            # 验证后端切换是否成功
            if not processor.backend.__class__.__name__.endswith('SPICEBackend'):
                raise RuntimeError(
                    f'后端切换失败！期望SPICE后端，但实际是: {processor.backend.__class__.__name__}\n'
                    f'这可能是因为SPICE依赖不可用'
                )
            
            # 执行SPICE推理
            spice_result = processor.infer_and_save(
                input_wave, 
                output_dir=data_dir, 
                use_scaler=True, 
                return_layers=True, 
                return_numpy=True,
                layers=self.layers_limit  # 传递层数限制
            )
            
            # 验证结果完整性
            self._validate_spice_result(spice_result)
            
            # 提取输出路径
            spice_paths = [layer.file_path for layer in spice_result.layers]
            numpy_paths = [layer.file_path for layer in spice_result.numpy_layers] if spice_result.has_numpy_output() else []
            
            # 验证文件存在
            for path in spice_paths[:1]:  # 至少检查第一个文件
                if not os.path.exists(path):
                    raise RuntimeError(f'SPICE输出文件不存在: {path}')
            
            logger.info(f'SPICE分层推理完成，保存了 {len(spice_paths)} 个文件')
            if numpy_paths:
                logger.info(f'NumPy仿真完成，保存了 {len(numpy_paths)} 个文件')
            
            return spice_result, spice_paths, numpy_paths
            
        except Exception as e:
            logger.info('\n' + '=' * 60)
            logger.info('[ERROR] SPICE/NumPy推理失败')
            logger.info('=' * 60)
            logger.error(f'错误信息：{str(e)}')
            logger.info('\n建议：请使用以下命令在正确的环境中运行：')
            logger.info(f'  conda run -n tf26 python cli.py -i {self.project_name}')
            logger.info('=' * 60 + '\n')
            raise  # 直接抛出异常，不降级处理
    
    def _validate_spice_result(self, spice_result):
        """验证SPICE结果的完整性"""
        # 验证后端类型
        if spice_result.backend_type != 'spice':
            raise RuntimeError(
                f"\n{'=' * 60}\n"
                f"[FATAL ERROR] 致命错误：后端类型伪装！\n"
                f"{'=' * 60}\n"
                f"期望结果类型: 'spice'\n"
                f"实际结果类型: '{spice_result.backend_type}'\n"
                f"实际后端类: {spice_result.metadata.get('actual_backend_class', 'Unknown')}\n"
                f"\n[WARNING] 警告 [WARNING]\n"
                f"检测到可能用NN结果冒充SPICE结果的情况。\n"
                f"这是绝对不允许的，会导致整个研究项目失败。\n"
                f"\n可能的原因：\n"
                f"1. SPICE后端初始化失败但继续使用了旧后端\n"
                f"2. 后端切换过程中状态不一致\n"
                f"3. SPICE依赖（如spicelib）未正确安装\n"
                f"\n请立即停止并修复此问题！\n"
                f"{'=' * 60}\n"
            )
        
        # 二次验证
        actual_backend = spice_result.metadata.get('actual_backend_class', '')
        if 'spice' not in actual_backend.lower():
            raise RuntimeError(
                f"\n{'=' * 60}\n"
                f"[ERROR] 二次验证失败：后端类不包含'spice'\n"
                f"{'=' * 60}\n"
                f"实际后端类: {actual_backend}\n"
                f"这确认了结果不是来自SPICE后端。\n"
                f"{'=' * 60}\n"
            )
    
    def _save_input_data(self, processor, input_wave: str, data_dir: str):
        """保存输入数据"""
        if self.quick_mode:
            # 快速模式：保存过滤后的输入数据
            filtered_wave_data = processor._load_wave_data_with_filter(input_wave)
            self.wave_processor.save_waveform(f'{data_dir}/input.wave', filtered_wave_data)
            logger.info(f'💾 已保存快速模式过滤后的输入数据到 input.wave')
        else:
            # 标准模式：保存原始输入数据
            shutil.copy2(input_wave, f'{data_dir}/input.wave')
            logger.info(f'💾 已保存原始输入数据到 input.wave')
    
    def _save_inference_metadata(self, data_dir: str, input_wave: str, 
                               nn_outputs: List[str], spice_outputs: List[str], 
                               numpy_outputs: List[str], processor) -> Dict:
        """保存推理元数据"""
        metadata = {
            "project_name": self.project_name,
            "project_path": self.project_path,
            "config": self.config,
            "timestamp": self._get_timestamp(),
            "input_file": input_wave,
            "num_layers": len(nn_outputs),
            "nn_layers": len(nn_outputs),
            "spice_layers": len(spice_outputs),
            "numpy_layers": len(numpy_outputs) if numpy_outputs else 0,
            "quick_mode": self.quick_mode
        }
        
        # 如果是快速模式，添加额外的过滤信息
        if self.quick_mode:
            filtered_wave_data = processor._load_wave_data_with_filter(input_wave)
            if hasattr(filtered_wave_data, 'user_metadata'):
                metadata.update({
                    "quick_mode_info": {
                        "original_records": filtered_wave_data.user_metadata.get('original_records', 'unknown'),
                        "filtered_records": filtered_wave_data.user_metadata.get('filtered_records', 'unknown'),
                        "min_magnitude": filtered_wave_data.user_metadata.get('min_magnitude', 'unknown'),
                        "max_magnitude": filtered_wave_data.user_metadata.get('max_magnitude', 'unknown')
                    }
                })
        
        # 保存到文件
        with open(f'{data_dir}/inference_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        return metadata
    
    def _get_timestamp(self):
        """获取当前时间戳"""
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())