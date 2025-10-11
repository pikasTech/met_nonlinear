#!/usr/bin/env python3
"""
严格验证测试脚本 - 独立测试WNET5q1h2u6l3项目

用于测试严格路径验证系统的功能
"""

import json
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO, format='🔒 [测试] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class TestStrictPathValidator:
    """测试用的严格路径验证器"""
    
    def __init__(self, project_name: str, project_root: str):
        self.project_name = project_name
        self.project_root = Path(project_root).resolve()
        self.project_path = self.project_root / "projects" / project_name
        
        # 必需文件清单
        self.required_files = {
            "config": self.project_path / "config.json",
            "error_analysis": self.project_path / "data" / "inference" / "error_analysis.json",
            "inference_metadata": self.project_path / "data" / "inference" / "inference_metadata.json",
            "model_info": self.project_path / "data" / "model_info.json"
        }
    
    def validate_all_paths(self):
        """验证所有必需路径"""
        logger.info(f"🔍 开始路径验证: {self.project_name}")
        
        # 验证项目目录存在
        if not self.project_path.exists():
            raise FileNotFoundError(f"项目目录不存在: {self.project_path}")
        logger.info(f"✅ 项目目录存在: {self.project_path}")
        
        # 验证必需文件
        for file_type, file_path in self.required_files.items():
            if not file_path.exists():
                raise FileNotFoundError(f"必需文件不存在: {file_path}")
            logger.info(f"✅ {file_type} 文件存在: {file_path}")
        
        return True
    
    def validate_json_integrity(self):
        """验证JSON文件完整性"""
        logger.info(f"🔍 开始JSON完整性验证")
        
        for file_type, file_path in self.required_files.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 基本验证
                if file_type == "config":
                    self._validate_config_structure(data, file_path)
                elif file_type == "error_analysis":
                    self._validate_error_analysis_structure(data, file_path)
                elif file_type == "inference_metadata":
                    self._validate_inference_metadata_structure(data, file_path)
                
                logger.info(f"✅ {file_type} JSON格式正确")
                
            except json.JSONDecodeError as e:
                raise ValueError(f"JSON格式错误: {file_path}, 错误: {e}")
            except Exception as e:
                raise RuntimeError(f"文件验证失败: {file_path}, 错误: {e}")
        
        return True
    
    def _validate_config_structure(self, data, file_path):
        """验证config.json结构"""
        required_keys = ["inference_config", "use_model"]
        for key in required_keys:
            if key not in data:
                raise KeyError(f"配置文件缺少必需键: {key}")
        
        # 验证bias_compensation结构
        if "bias_compensation" in data.get("inference_config", {}):
            bias_config = data["inference_config"]["bias_compensation"]
            if "layer_bias_adjustments" not in bias_config:
                raise KeyError("偏置配置缺少layer_bias_adjustments")
    
    def _validate_error_analysis_structure(self, data, file_path):
        """验证error_analysis.json结构"""
        required_keys = ["project_name", "nn_spice_analysis"]
        for key in required_keys:
            if key not in data:
                raise KeyError(f"错误分析文件缺少必需键: {key}")
        
        # 验证项目名匹配
        if data["project_name"] != self.project_name:
            raise ValueError(f"项目名不匹配: 期望 {self.project_name}, 实际 {data['project_name']}")
    
    def _validate_inference_metadata_structure(self, data, file_path):
        """验证inference_metadata.json结构"""
        required_keys = ["project_name", "project_path", "config"]
        for key in required_keys:
            if key not in data:
                raise KeyError(f"推理元数据文件缺少必需键: {key}")
        
        # 验证项目名匹配
        if data["project_name"] != self.project_name:
            raise ValueError(f"项目名不匹配: 期望 {self.project_name}, 实际 {data['project_name']}")


def test_wnet5q1h2u6l3():
    """测试WNET5q1h2u6l3项目的严格验证"""
    project_name = "WNET5q1h2u6l3"
    project_root = "/mnt/f/Work/met_nonlinear_worktrees/met_nonlinear_master"
    
    logger.info("=" * 70)
    logger.info(f"🔒 开始严格验证测试: {project_name}")
    logger.info("=" * 70)
    
    try:
        # 创建验证器
        validator = TestStrictPathValidator(project_name, project_root)
        
        # 1. 路径验证
        validator.validate_all_paths()
        logger.info("✅ 阶段1: 路径验证通过")
        
        # 2. JSON完整性验证
        validator.validate_json_integrity()
        logger.info("✅ 阶段2: JSON完整性验证通过")
        
        # 3. 显示配置信息
        config_path = validator.required_files["config"]
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 检查偏置补偿配置
        bias_config = config.get("inference_config", {}).get("bias_compensation", {})
        if bias_config.get("enabled", False):
            layer_adjustments = bias_config.get("layer_bias_adjustments", {})
            logger.info(f"📊 偏置补偿已启用，配置层数: {len(layer_adjustments)}")
            for layer, adjustments in layer_adjustments.items():
                logger.info(f"   层 {layer}: {len(adjustments)} 个调整值")
        
        logger.info("=" * 70)
        logger.info("🎉 严格验证测试完全成功！")
        logger.info("🔒 学术诚信保护：所有文件验证通过")
        logger.info("=" * 70)
        
        return True
        
    except Exception as e:
        logger.error("=" * 70)
        logger.error(f"❌ 严格验证测试失败")
        logger.error(f"错误详情: {e}")
        logger.error("🔒 学术诚信保护：验证被安全阻止")
        logger.error("=" * 70)
        return False


if __name__ == "__main__":
    success = test_wnet5q1h2u6l3()
    exit(0 if success else 1)