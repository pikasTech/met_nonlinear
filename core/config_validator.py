"""
外部项目配置文件验证器

严格验证JSON配置文件的格式和内容，确保：
1. 必需字段完整性
2. 数据类型正确性  
3. 不允许额外字段
4. 字段值的合理性
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger(__name__)


class ConfigValidationError(Exception):
    """配置验证错误"""
    pass


class VisualizationConfigValidator:
    """可视化配置验证器（用于 EP 的可视化与其他外部任务）"""
    
    # 频率响应对比任务的严格schema
    FREQ_RESPONSE_SCHEMA = {
        "type": "object",
        "required": ["task_info", "visualization_config", "data_sources"],
        "additionalProperties": False,  # 不允许额外字段
        "properties": {
            "task_info": {
                "type": "object",
                "required": ["task_type"],
                "additionalProperties": False,
                "properties": {
                    "task_type": {
                        "type": "string",
                        "enum": ["freq-response-compare"]
                    }
                }
            },
            "visualization_config": {
                "type": "object",
                "required": [],  # 都有默认值
                "additionalProperties": False,
                "properties": {
                    "layout": {
                        "type": "string", 
                        "enum": ["side_by_side", "overlaid", "separate"]
                    },
                    "freq_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2
                    },
                    "gain_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["png", "jpg", "jpeg", "pdf", "svg"]
                    },
                    "dpi": {
                        "type": "integer",
                        "minimum": 72,
                        "maximum": 600
                    },
                    "figsize": {
                        "type": "array", 
                        "items": {"type": "number", "minimum": 1},
                        "minItems": 2,
                        "maxItems": 2
                    },
                    "title": {"type": "string"}
                }
            },
            "data_sources": {
                "type": "array",
                "minItems": 1,
                "maxItems": 10,  # 合理的上限
                "items": {
                    "type": "object",
                    "required": ["project", "label"],
                    "additionalProperties": False,
                    "properties": {
                        "project": {"type": "string", "minLength": 1},
                        "state": {
                            "type": "string",
                            "enum": ["origin", "compensation", "training", "testing"]
                        },
                        "label": {"type": "string", "minLength": 1}
                    }
                }
            }
        }
    }
    
    # 偏置可视化任务schema
    BIAS_VISUALIZATION_SCHEMA = {
        "type": "object",
        "required": ["task_info", "visualization_config", "data_sources"],
        "additionalProperties": False,
        "properties": {
            "task_info": {
                "type": "object",
                "required": ["task_type"],
                "additionalProperties": False,
                "properties": {
                    "task_type": {
                        "type": "string",
                        "enum": ["bias-visualization"]
                    }
                }
            },
            "visualization_config": {
                "type": "object",
                "required": [],
                "additionalProperties": False,
                "properties": {
                    "output_format": {
                        "type": "string",
                        "enum": ["png", "jpg", "jpeg", "pdf", "svg"]
                    },
                    "dpi": {
                        "type": "integer",
                        "minimum": 72,
                        "maximum": 600
                    },
                    "figsize": {
                        "type": "array",
                        "items": {"type": "number", "minimum": 1},
                        "minItems": 2,
                        "maxItems": 2
                    },
                    "points": {
                        "type": "integer",
                        "minimum": 10,
                        "maximum": 100000
                    },
                    "title": {"type": "string"}
                }
            },
            "data_sources": {
                "type": "array",
                "minItems": 1,
                "maxItems": 5,
                "items": {
                    "type": "object",
                    "required": ["project", "label"],
                    "additionalProperties": False,
                    "properties": {
                        "project": {"type": "string", "minLength": 1},
                        "state": {
                            "type": "string",
                            "enum": ["origin", "compensation", "training", "testing"]
                        },
                        "label": {"type": "string", "minLength": 1}
                    }
                }
            }
        }
    }
    
    # 波形分析任务schema
    WAVEFORM_ANALYSIS_SCHEMA = {
        "type": "object",
        "required": ["task_info", "visualization_config", "data_sources"],
        "additionalProperties": False,
        "properties": {
            "task_info": {
                "type": "object",
                "required": ["task_type"],
                "additionalProperties": False,
                "properties": {
                    "task_type": {
                        "type": "string",
                        "enum": ["waveform-analysis"]
                    }
                }
            },
            "visualization_config": {
                "type": "object",
                "required": [],
                "additionalProperties": False,
                "properties": {
                    "output_format": {
                        "type": "string",
                        "enum": ["png", "jpg", "jpeg", "pdf", "svg"]
                    },
                    "dpi": {
                        "type": "integer",
                        "minimum": 72,
                        "maximum": 600
                    },
                    "figsize": {
                        "type": "array",
                        "items": {"type": "number", "minimum": 1},
                        "minItems": 2,
                        "maxItems": 2
                    },
                    "title": {"type": "string"}
                }
            },
            "data_sources": {
                "type": "array",
                "minItems": 1,
                "maxItems": 5,
                "items": {
                    "type": "object",
                    "required": ["project", "label"],
                    "additionalProperties": False,
                    "properties": {
                        "project": {"type": "string", "minLength": 1},
                        "state": {
                            "type": "string",
                            "enum": ["origin", "compensation", "training", "testing"]
                        },
                        "label": {"type": "string", "minLength": 1}
                    }
                }
            }
        }
    }
    
    # WNET5电路验证任务schema
    WNET5_CIRCUIT_VALIDATION_SCHEMA = {
        "type": "object",
        "required": ["task_info", "model_project_name", "frequency_range"],
        "additionalProperties": False,
        "properties": {
            "task_info": {
                "type": "object",
                "required": ["task_type"],
                "additionalProperties": False,
                "properties": {
                    "task_type": {
                        "type": "string",
                        "enum": ["wnet5-circuit-validation"]
                    },
                    "description": {"type": "string"}
                }
            },
            "model_project_name": {
                "type": "string",
                "minLength": 1
            },
            "analysis_layer": {
                "type": "integer",
                "minimum": 1,
                "maximum": 10
            },
            "frequency_range": {
                "type": "object",
                "required": ["start_freq", "stop_freq"],
                "additionalProperties": False,
                "properties": {
                    "start_freq": {
                        "type": "number",
                        "minimum": 0.001,
                        "maximum": 1000000
                    },
                    "stop_freq": {
                        "type": "number",
                        "minimum": 0.001,
                        "maximum": 1000000
                    },
                    "points": {
                        "type": "integer",
                        "minimum": 10,
                        "maximum": 100000
                    }
                }
            },
            "compare_with_experiment": {
                "type": "string",
                "minLength": 1
            },
            "experiment_comparison": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "enable": {
                        "type": "boolean"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["single_file", "multi_file"]
                    },
                    "experiment_data_dir": {
                        "type": "string",
                        "minLength": 1
                    },
                    "selftest_file": {
                        "type": "string",
                        "minLength": 1
                    },
                    "experiment_sheet_name": {
                        "type": "string",
                        "minLength": 1
                    },
                    "plot_config": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "coordinate_system": {
                                "type": "string",
                                "enum": ["loglog", "semilogx", "semilogy", "linear"]
                            },
                            "y_unit": {
                                "type": "string",
                                "enum": ["dB", "linear"]
                            },
                            "merged_plot_mode": {
                                "type": "boolean",
                                "description": "启用合并模式：将上下两个图绘制到一张图里面，仿真结果用虚线，实测结果用实线"
                            }
                        }
                    }
                }
            },
            "inference_config": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "use_e96": {
                        "type": "boolean",
                        "description": "是否使用E96标准电阻值"
                    },
                    "include_quantization_comparison": {
                        "type": "boolean",
                        "description": "是否包含E96量化对比数据"
                    },
                    "opamp_config": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "model": {
                                "type": "string",
                                "enum": ["ideal", "LM324", "TL084", "OPAx205A", "AD8622", "OPA1611"]
                            },
                            "include_file": {
                                "type": "string"
                            },
                            "power_pins": {
                                "type": "boolean"
                            },
                            "params": {
                                "type": "object"
                            }
                        }
                    },
                    "power_supply": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "vcc": {
                                "type": "number"
                            },
                            "vee": {
                                "type": "number"
                            }
                        }
                    },
                    "high_pass_config": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "enable": {
                                "type": "boolean"
                            },
                            "cutoff_freq": {
                                "type": "number"
                            }
                        }
                    },
                    "bias_compensation": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "enabled": {
                                "type": "boolean"
                            },
                            "layer_bias_adjustments": {
                                "type": "object"
                            }
                        }
                    }
                }
            },
            "svf_error_simulation": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "enable": {
                        "type": "boolean"
                    },
                    "measured_data_file": {
                        "type": "string",
                        "minLength": 1
                    },
                    "include_dense_layer": {
                        "type": "boolean"
                    },
                    "compensation": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "enabled": {
                                "type": "boolean"
                            },
                            "selftest_file": {
                                "type": "string",
                                "minLength": 1
                            }
                        }
                    },
                    "plot_config": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "merged_plot_mode": {
                                "type": "boolean"
                            },
                            "output_filename": {
                                "type": "string",
                                "minLength": 1
                            },
                            "dense_output_filename": {
                                "type": "string",
                                "minLength": 1
                            }
                        }
                    },
                    "fitting": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "enabled": {
                                "type": "boolean"
                            },
                            "output_filename": {
                                "type": "string",
                                "minLength": 1
                            },
                            "save_fitted_params": {
                                "type": "boolean"
                            }
                        }
                    }
                }
            }
        }
    }

    # 频率响应补偿器任务 schema (基于 linear_response.json 绘制 origin vs comped)
    FREQ_RESPONSE_COMPENSATOR_SCHEMA = {
        "type": "object",
        "required": ["task_info", "project_name"],
        "additionalProperties": False,
        "properties": {
            "task_info": {
                "type": "object",
                "required": ["task_type"],
                "additionalProperties": False,
                "properties": {
                    "task_type": {"type": "string", "enum": ["freq-response-compensator"]},
                    "description": {"type": "string"}
                }
            },
            "project_name": {"type": "string", "minLength": 1},
            "visualization_config": {
                "type": "object",
                "required": [],
                "additionalProperties": False,
                "properties": {
                    "output_format": {"type": "string", "enum": ["png", "jpg", "jpeg", "pdf", "svg"]},
                    "dpi": {"type": "integer", "minimum": 72, "maximum": 600},
                    "figsize": {"type": "array", "items": {"type": "number", "minimum": 1}, "minItems": 2, "maxItems": 2},
                    "freq_range": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2},
                    "gain_range": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2},
                    "title": {"type": "string"},
                    "log_scale": {"type": "boolean"},
                    "target_magnitudes": {"type": "array", "items": {"type": "number"}}
                }
            }
        }
    }

    def __init__(self):
        """初始化验证器"""
        self.schemas = {
            "freq-response-compare": self.FREQ_RESPONSE_SCHEMA,
            "freq-response-compensator": self.FREQ_RESPONSE_COMPENSATOR_SCHEMA,
            "bias-visualization": self.BIAS_VISUALIZATION_SCHEMA,
            "waveform-analysis": self.WAVEFORM_ANALYSIS_SCHEMA,
            "wnet5-circuit-validation": self.WNET5_CIRCUIT_VALIDATION_SCHEMA
        }

    def validate_config_file(self, config_path: Union[str, Path], task_type: str) -> Dict[str, Any]:
        """
        验证配置文件
        
        Args:
            config_path: 配置文件路径
            task_type: 任务类型
            
        Returns:
            Dict: 验证通过的配置数据
            
        Raises:
            ConfigValidationError: 验证失败时抛出
        """
        config_path = Path(config_path)
        
        # 检查文件存在性
        if not config_path.exists():
            raise ConfigValidationError(f"配置文件不存在: {config_path}")
        
        # 加载JSON
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigValidationError(f"JSON格式错误: {e}")
        except Exception as e:
            raise ConfigValidationError(f"读取配置文件失败: {e}")
        
        # 验证配置
        return self.validate_config_data(config, task_type)

    def validate_config_data(self, config: Dict[str, Any], task_type: str) -> Dict[str, Any]:
        """
        验证配置数据
        
        Args:
            config: 配置数据字典
            task_type: 任务类型
            
        Returns:
            Dict: 验证通过的配置数据
            
        Raises:
            ConfigValidationError: 验证失败时抛出
        """
        if not isinstance(config, dict):
            raise ConfigValidationError("配置必须是一个JSON对象")
        
        # 获取对应的schema
        if task_type not in self.schemas:
            raise ConfigValidationError(f"不支持的任务类型: {task_type}")
        
        schema = self.schemas[task_type]
        
        # 收集所有验证错误
        errors = []
        
        # 执行严格验证
        try:
            self._validate_against_schema(config, schema, "root", errors)
        except Exception as e:
            if not errors:  # 如果没有收集到具体错误，添加通用错误
                errors.append(str(e))
        
        # 额外的业务逻辑验证
        try:
            self._validate_business_logic(config, task_type)
        except ConfigValidationError as e:
            errors.append(str(e))
        except Exception as e:
            errors.append(f"业务逻辑验证失败: {e}")
        
        # 如果有错误，抛出包含所有错误的异常
        if errors:
            raise ConfigValidationError("; ".join(errors))
        
        logger.info(f"✅ 配置验证通过: {task_type}")
        return config

    def _validate_against_schema(self, data: Any, schema: Dict[str, Any], path: str = "root", errors: Optional[List[str]] = None) -> None:
        """根据schema验证数据，收集所有错误"""
        if errors is None:
            errors = []
        
        # 检查类型
        if "type" in schema:
            expected_type = schema["type"]
            if not self._check_type(data, expected_type):
                errors.append(f"{path}: 期望类型 {expected_type}, 实际类型 {type(data).__name__}")
                return  # 类型错误时不继续验证
        
        if schema.get("type") == "object":
            self._validate_object(data, schema, path, errors)
        elif schema.get("type") == "array":
            self._validate_array(data, schema, path, errors)
        elif schema.get("type") == "string":
            self._validate_string(data, schema, path, errors)
        elif schema.get("type") == "integer":
            self._validate_integer(data, schema, path, errors)
        elif schema.get("type") == "number":
            self._validate_number(data, schema, path, errors)

    def _validate_object(self, data: Dict[str, Any], schema: Dict[str, Any], path: str, errors: List[str]) -> None:
        """验证对象类型"""
        if not isinstance(data, dict):
            errors.append(f"{path}: 必须是对象类型")
            return
        
        # 检查必需字段
        required = schema.get("required", [])
        for field in required:
            if field not in data:
                errors.append(f"{path}: 缺少必需字段 '{field}'")
        
        # 检查额外字段
        if schema.get("additionalProperties") is False:
            allowed_fields = set(schema.get("properties", {}).keys())
            actual_fields = set(data.keys())
            extra_fields = actual_fields - allowed_fields
            if extra_fields:
                errors.append(f"{path}: 包含不允许的字段: {sorted(list(extra_fields))}")
        
        # 验证每个属性
        properties = schema.get("properties", {})
        for field, value in data.items():
            if field in properties:
                field_path = f"{path}.{field}"
                self._validate_against_schema(value, properties[field], field_path, errors)

    def _validate_array(self, data: List[Any], schema: Dict[str, Any], path: str, errors: List[str]) -> None:
        """验证数组类型"""
        if not isinstance(data, list):
            errors.append(f"{path}: 必须是数组类型")
            return
        
        # 检查长度限制
        if "minItems" in schema and len(data) < schema["minItems"]:
            errors.append(f"{path}: 数组长度不能少于 {schema['minItems']}")
        
        if "maxItems" in schema and len(data) > schema["maxItems"]:
            errors.append(f"{path}: 数组长度不能超过 {schema['maxItems']}")
        
        # 验证每个元素
        if "items" in schema:
            item_schema = schema["items"]
            for i, item in enumerate(data):
                item_path = f"{path}[{i}]"
                self._validate_against_schema(item, item_schema, item_path, errors)

    def _validate_string(self, data: str, schema: Dict[str, Any], path: str, errors: List[str]) -> None:
        """验证字符串类型"""
        if not isinstance(data, str):
            errors.append(f"{path}: 必须是字符串类型")
            return
        
        # 检查枚举值
        if "enum" in schema and data not in schema["enum"]:
            errors.append(f"{path}: 值 '{data}' 不在允许的枚举值中: {schema['enum']}")
        
        # 检查最小长度
        if "minLength" in schema and len(data) < schema["minLength"]:
            errors.append(f"{path}: 字符串长度不能少于 {schema['minLength']}")

    def _validate_integer(self, data: int, schema: Dict[str, Any], path: str, errors: List[str]) -> None:
        """验证整数类型"""
        if not isinstance(data, int):
            errors.append(f"{path}: 必须是整数类型")
            return
        
        # 检查范围
        if "minimum" in schema and data < schema["minimum"]:
            errors.append(f"{path}: 值 {data} 不能小于 {schema['minimum']}")
        
        if "maximum" in schema and data > schema["maximum"]:
            errors.append(f"{path}: 值 {data} 不能大于 {schema['maximum']}")

    def _validate_number(self, data: Union[int, float], schema: Dict[str, Any], path: str, errors: List[str]) -> None:
        """验证数字类型"""
        if not isinstance(data, (int, float)):
            errors.append(f"{path}: 必须是数字类型")
            return
        
        # 检查范围
        if "minimum" in schema and data < schema["minimum"]:
            errors.append(f"{path}: 值 {data} 不能小于 {schema['minimum']}")
        
        if "maximum" in schema and data > schema["maximum"]:
            errors.append(f"{path}: 值 {data} 不能大于 {schema['maximum']}")

    def _check_type(self, data: Any, expected_type: str) -> bool:
        """检查数据类型"""
        type_map = {
            "object": dict,
            "array": list,
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "null": type(None)
        }
        
        expected_python_type = type_map.get(expected_type)
        if expected_python_type is None:
            return False
        
        return isinstance(data, expected_python_type)

    def _validate_business_logic(self, config: Dict[str, Any], task_type: str) -> None:
        """验证业务逻辑"""
        
        # 检查task_type一致性
        config_task_type = config.get("task_info", {}).get("task_type")
        if config_task_type != task_type:
            raise ConfigValidationError(
                f"配置文件中的任务类型 '{config_task_type}' 与指定的任务类型 '{task_type}' 不匹配"
            )
        
        # 频率响应特殊验证
        if task_type == "freq-response-compare":
            self._validate_freq_response_logic(config)

    def _validate_freq_response_logic(self, config: Dict[str, Any]) -> None:
        """频率响应任务的特殊验证"""
        viz_config = config.get("visualization_config", {})
        
        # 验证频率范围
        if "freq_range" in viz_config:
            freq_range = viz_config["freq_range"]
            if len(freq_range) == 2 and freq_range[0] >= freq_range[1]:
                raise ConfigValidationError("freq_range: 起始频率必须小于结束频率")
        
        # 验证数据源
        data_sources = config.get("data_sources", [])
        if len(data_sources) < 1:
            raise ConfigValidationError("freq-response-compare任务至少需要1个数据源")


# 全局验证器实例
validator = VisualizationConfigValidator()


def validate_visualization_config(config_path: Union[str, Path], task_type: str) -> Dict[str, Any]:
    """
    验证可视化配置文件（便捷函数）
    
    Args:
        config_path: 配置文件路径
        task_type: 任务类型
        
    Returns:
        Dict: 验证通过的配置数据
        
    Raises:
        ConfigValidationError: 验证失败时抛出
    """
    return validator.validate_config_file(config_path, task_type)


def validate_visualization_config_data(config: Dict[str, Any], task_type: str) -> Dict[str, Any]:
    """
    验证可视化配置数据（便捷函数）
    
    Args:
        config: 配置数据字典
        task_type: 任务类型
        
    Returns:
        Dict: 验证通过的配置数据
        
    Raises:
        ConfigValidationError: 验证失败时抛出
    """
    return validator.validate_config_data(config, task_type)


if __name__ == "__main__":
    # 测试代码
    import sys
    from pathlib import Path
    
    if len(sys.argv) != 3:
        print("用法: python config_validator.py <config_file> <task_type>")
        sys.exit(1)
    
    config_file = Path(sys.argv[1])
    task_type = sys.argv[2]
    
    try:
        config = validate_visualization_config(config_file, task_type)
        print("✅ 配置验证通过")
        print(f"项目: {config['data_sources'][0]['project']}")
        print(f"数据源数量: {len(config['data_sources'])}")
    except ConfigValidationError as e:
        print(f"❌ 配置验证失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 验证过程出错: {e}")
        sys.exit(1)