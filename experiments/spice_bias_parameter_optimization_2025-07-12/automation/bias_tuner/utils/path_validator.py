"""
严格路径验证器 - 零容错路径验证系统

核心原则：精确验证 + FAIL FAST + 零容错机制
严禁：模糊匹配、自动发现、容错机制

设计目标：防止读取错误文件造成极其严重的毁灭性的学术不端问题
"""

from pathlib import Path
from typing import Dict, List
import os
import json
import logging

logger = logging.getLogger(__name__)


class StrictPathValidator:
    """严格路径验证器 - 零容错设计"""
    
    def __init__(self, project_name: str, project_root: str):
        self.project_name = project_name
        self.project_root = Path(project_root).resolve()
        self.project_path = self.project_root / "projects" / project_name
        
        # 必需文件清单 - 精确路径
        self.required_files = {
            "config": self.project_path / "config.json",
            "error_analysis": self.project_path / "data" / "inference" / "error_analysis.json",
            "inference_metadata": self.project_path / "data" / "inference" / "inference_metadata.json",
            "model_info": self.project_path / "data" / "model_info.json"
        }
        
    def validate_all_paths(self) -> Dict[str, bool]:
        """验证所有必需路径 - 严格模式"""
        validation_results = {}
        
        # 验证项目目录存在
        if not self.project_path.exists():
            raise FileNotFoundError(
                f"项目目录不存在: {self.project_path}\n"
                f"严格验证失败 - 学术不端风险阻止"
            )
            
        # 逐个验证必需文件
        for file_type, file_path in self.required_files.items():
            if not file_path.exists():
                raise FileNotFoundError(
                    f"必需文件不存在: {file_path}\n"
                    f"文件类型: {file_type}\n"
                    f"严格验证失败 - 学术不端风险阻止"
                )
            validation_results[file_type] = True
            
        return validation_results
    
    def validate_json_integrity(self) -> Dict[str, bool]:
        """验证JSON文件完整性 - 严格模式"""
        integrity_results = {}
        
        for file_type, file_path in self.required_files.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # 基本结构验证
                if file_type == "config":
                    self._validate_config_structure(data, file_path)
                elif file_type == "error_analysis":
                    self._validate_error_analysis_structure(data, file_path)
                elif file_type == "inference_metadata":
                    self._validate_inference_metadata_structure(data, file_path)
                elif file_type == "model_info":
                    self._validate_model_info_structure(data, file_path)
                    
                integrity_results[file_type] = True
                
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"JSON格式错误: {file_path}\n"
                    f"错误详情: {e}\n"
                    f"严格验证失败 - 学术不端风险阻止"
                )
            except Exception as e:
                raise RuntimeError(
                    f"文件验证失败: {file_path}\n"
                    f"错误详情: {e}\n"
                    f"严格验证失败 - 学术不端风险阻止"
                )
                
        return integrity_results
    
    def _validate_config_structure(self, data: Dict, file_path: Path) -> None:
        """验证config.json结构 - 严格模式"""
        required_keys = ["inference_config", "use_model"]
        for key in required_keys:
            if key not in data:
                raise KeyError(
                    f"配置文件缺少必需键: {key}\n"
                    f"文件路径: {file_path}\n"
                    f"严格验证失败 - 学术不端风险阻止"
                )
                
        # 验证bias_compensation结构
        if "bias_compensation" in data.get("inference_config", {}):
            bias_config = data["inference_config"]["bias_compensation"]
            if "layer_bias_adjustments" not in bias_config:
                raise KeyError(
                    f"偏置配置缺少layer_bias_adjustments\n"
                    f"文件路径: {file_path}\n"
                    f"严格验证失败 - 学术不端风险阻止"
                )
    
    def _validate_error_analysis_structure(self, data: Dict, file_path: Path) -> None:
        """验证error_analysis.json结构 - 严格模式"""
        required_keys = ["project_name", "nn_spice_analysis"]
        for key in required_keys:
            if key not in data:
                raise KeyError(
                    f"错误分析文件缺少必需键: {key}\n"
                    f"文件路径: {file_path}\n"
                    f"严格验证失败 - 学术不端风险阻止"
                )
                
        # 验证项目名匹配
        if data["project_name"] != self.project_name:
            raise ValueError(
                f"项目名不匹配\n"
                f"期望: {self.project_name}\n"
                f"实际: {data['project_name']}\n"
                f"文件路径: {file_path}\n"
                f"严格验证失败 - 学术不端风险阻止"
            )
    
    def _validate_inference_metadata_structure(self, data: Dict, file_path: Path) -> None:
        """验证inference_metadata.json结构 - 严格模式"""
        required_keys = ["project_name", "project_path", "config"]
        for key in required_keys:
            if key not in data:
                raise KeyError(
                    f"推理元数据文件缺少必需键: {key}\n"
                    f"文件路径: {file_path}\n"
                    f"严格验证失败 - 学术不端风险阻止"
                )
                
        # 验证项目名匹配
        if data["project_name"] != self.project_name:
            raise ValueError(
                f"项目名不匹配\n"
                f"期望: {self.project_name}\n"
                f"实际: {data['project_name']}\n"
                f"文件路径: {file_path}\n"
                f"严格验证失败 - 学术不端风险阻止"
            )
    
    def _validate_model_info_structure(self, data: Dict, file_path: Path) -> None:
        """验证model_info.json结构 - 严格模式"""
        # model_info.json的验证相对宽松，因为其结构可能因模型而异
        # 但仍需要确保文件可以正常读取
        if not isinstance(data, dict):
            raise ValueError(
                f"模型信息文件格式错误\n"
                f"文件路径: {file_path}\n"
                f"严格验证失败 - 学术不端风险阻止"
            )
    
    def get_validated_paths(self) -> Dict[str, Path]:
        """获取验证通过的路径 - 仅在完全验证后返回"""
        self.validate_all_paths()
        self.validate_json_integrity()
        return self.required_files.copy()


class StrictPathChecker:
    """严格路径检查器 - FAIL FAST机制"""
    
    def __init__(self, validator: StrictPathValidator):
        self.validator = validator
        
    def pre_execution_check(self) -> bool:
        """执行前检查 - 严格验证模式"""
        logger.info(f"🔍 严格路径验证开始: {self.validator.project_name}")
        
        try:
            # 1. 路径存在验证
            path_results = self.validator.validate_all_paths()
            logger.info(f"✅ 路径存在验证通过: {list(path_results.keys())}")
            
            # 2. JSON完整性验证
            integrity_results = self.validator.validate_json_integrity()
            logger.info(f"✅ JSON完整性验证通过: {list(integrity_results.keys())}")
            
            # 3. 获取验证后的路径
            validated_paths = self.validator.get_validated_paths()
            logger.info(f"✅ 严格验证完成，安全执行路径已确认")
            
            return True
            
        except (FileNotFoundError, KeyError, ValueError, RuntimeError) as e:
            logger.error(f"❌ 严格验证失败: {e}")
            logger.error(f"❌ 执行被阻止 - 学术不端风险规避")
            return False
    
    def fail_fast_validation(self, required_file_type: str) -> Path:
        """单文件快速失败验证"""
        if required_file_type not in self.validator.required_files:
            raise ValueError(
                f"未知文件类型: {required_file_type}\n"
                f"严格验证失败 - 学术不端风险阻止"
            )
            
        file_path = self.validator.required_files[required_file_type]
        
        if not file_path.exists():
            raise FileNotFoundError(
                f"严格验证失败 - 文件不存在: {file_path}\n"
                f"学术不端风险阻止"
            )
            
        return file_path


# 学术诚信保护异常
class AcademicIntegrityError(Exception):
    """学术诚信保护异常 - 防止严重的学术不端问题"""
    pass


class StrictValidationError(AcademicIntegrityError):
    """严格验证错误 - 零容错验证失败"""
    pass


class PathSecurityError(AcademicIntegrityError):
    """路径安全错误 - 防止读取错误文件"""
    pass