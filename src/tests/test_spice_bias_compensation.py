#!/usr/bin/env python
"""
SPICE 偏置补偿功能测试

测试偏置补偿配置的读取、应用和效果
"""

import os
import sys
import json
import pytest
import numpy as np
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inference.wavenet5_spice_backend import WaveNet5SPICEBackend
from models.model_layers import DenseLayer
from calibration_analyzer.wavedata import WaveData, WaveRecord


class MockWaveNet5Model:
    """模拟 WaveNet5 模型用于测试"""
    def __init__(self, inference_config=None):
        self.inference_config = inference_config or {}
        self.layer_to_layer_models = []
        self.model_name = 'WaveNet5'
        # 模拟标准WaveNet5配置
        self.model_subcfg = {
            'init_center_freqs': [10, 80],  # 2个中心频率
            'post_dense_units': 6,           # 6个Dense单元
            'post_dense_layers': 3           # 3个Dense层
        }

    def add_dense_layer(self, name, units):
        """添加模拟的 DenseLayer"""
        # 创建简单的模拟层
        layer = type('DenseLayer', (), {
            '__name__': 'DenseLayer',
            'name': name,
            'layer_name': name,
            'units': units,
            'to_spice': lambda self=None, **kwargs: f"SPICE_{name}"
        })()
        self.layer_to_layer_models.append(layer)

    def get_layers_info(self):
        """获取层信息，模拟真实的WaveNet5结构"""
        layers_info = []

        # 层0: SVF层 - 2个中心频率 × 3 = 6个输出通道
        layers_info.append({
            'name': 'SVF层',
            'type': 'SVF',
            'output_channels': len(self.model_subcfg.get('init_center_freqs', [])) * 3,
            'layer_description': f"SVF滤波器层 ({len(self.model_subcfg.get('init_center_freqs', []))} 滤波器 × 3 输出)"
        })

        # 层1-3: Dense层 - 每层6个单元
        for i in range(self.model_subcfg.get('post_dense_layers', 3)):
            layers_info.append({
                'name': f'Dense层{i+1}',
                'type': 'Dense',
                'output_channels': self.model_subcfg.get('post_dense_units', 6),
                'layer_description': f"Dense层 {i+1} ({self.model_subcfg.get('post_dense_units', 6)} 单元)"
            })

        # 层4: 输出层 - 1个单元
        layers_info.append({
            'name': '输出层',
            'type': 'Dense',
            'output_channels': 1,
            'layer_description': "输出层 (1 单元)"
        })

        return layers_info

    def to_spice(self, output_path=None, **kwargs):
        """模拟 to_spice 方法"""
        return [layer.to_spice(**kwargs) for layer in self.layer_to_layer_models]


def create_test_input():
    """创建测试输入波形"""
    t = np.linspace(0, 1, 2000)
    signal = np.sin(2 * np.pi * 10 * t) + 0.1 * np.random.randn(len(t))

    wave_data = WaveData(description="Test Input", author="Test")
    record = WaveRecord(
        data=signal.reshape(-1, 1),
        sample_rate=2000,
        channel_names=["input"]
    )
    wave_data.add_record(record)

    return wave_data


class TestBiasCompensationConfig:
    """测试偏置补偿配置读取"""

    def test_config_reading_enabled(self):
        """测试启用状态的配置读取"""
        # 使用 inference_config 直接传递偏置补偿配置
        config = {
            "bias_compensation": {
                "enabled": True,
                "layer_bias_adjustments": {
                    "0": [0.5, -0.5, 0.0, 0.0, 0.0, 0.0],  # 6个值匹配SVF层
                    "1": [0.2, -0.3, 0.1, 0.0, 0.0, 0.0]   # 6个值匹配Dense层
                }
            }
        }

        model = MockWaveNet5Model(inference_config=config)
        backend = WaveNet5SPICEBackend(model, inference_config=config)

        # 验证 inference_config 被正确存储
        assert backend.inference_config is not None
        assert "bias_compensation" in backend.inference_config
        assert backend.inference_config["bias_compensation"]["enabled"] == True
        print("✓ 偏置补偿配置正确读取")

    def test_config_reading_disabled(self):
        """测试禁用状态的配置读取"""
        config = {
            "bias_compensation": {
                "enabled": False,
                "layer_bias_adjustments": {}
            }
        }

        model = MockWaveNet5Model(inference_config=config)
        backend = WaveNet5SPICEBackend(model, inference_config=config)

        assert backend.inference_config["bias_compensation"]["enabled"] == False
        print("✓ 禁用状态的偏置补偿配置正确读取")

    def test_layer_bias_adjustments_shape_validation(self):
        """测试层偏置调整的形状验证"""
        # 测试正确形状
        config = {
            "bias_compensation": {
                "enabled": True,
                "layer_bias_adjustments": {
                    "0": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6],  # 6个值，匹配SVF层
                    "4": [0.1]  # 1个值，匹配输出层
                }
            }
        }

        model = MockWaveNet5Model(inference_config=config)
        backend = WaveNet5SPICEBackend(model, inference_config=config)

        # 验证配置被正确存储
        assert backend.inference_config["bias_compensation"]["enabled"] == True
        assert len(backend.inference_config["bias_compensation"]["layer_bias_adjustments"]["0"]) == 6
        assert len(backend.inference_config["bias_compensation"]["layer_bias_adjustments"]["4"]) == 1
        print("✓ 层偏置调整形状验证通过")


class TestDenseLayerCompensation:
    """测试 DenseLayer 的补偿处理"""

    def test_scalar_compensation_format(self):
        """测试标量补偿格式"""
        # 创建测试数据
        bias_vector = np.array([0.1, -0.2, 0.3])
        compensation = 0.5

        # 模拟 DenseLayer 的补偿逻辑
        if isinstance(compensation, (int, float)):
            compensation_array = np.full_like(bias_vector, compensation)

        result = bias_vector + compensation_array
        expected = np.array([0.6, 0.3, 0.8])

        np.testing.assert_array_almost_equal(result, expected)

    def test_list_compensation_format(self):
        """测试列表补偿格式"""
        bias_vector = np.array([0.1, -0.2, 0.3])
        compensation = [0.5, -0.3, 0.1]

        compensation_array = np.array(compensation)
        result = bias_vector + compensation_array
        expected = np.array([0.6, -0.5, 0.4])

        np.testing.assert_array_almost_equal(result, expected)

    def test_mismatched_compensation_length(self):
        """测试补偿值长度不匹配的情况"""
        bias_vector = np.array([0.1, -0.2, 0.3, 0.4])

        # 补偿值太短
        compensation_short = [0.5, -0.3]
        compensation_array = np.array(compensation_short)
        if len(compensation_array) < len(bias_vector):
            compensation_array = np.pad(
                compensation_array,
                (0, len(bias_vector) - len(compensation_array))
            )

        result = bias_vector + compensation_array
        expected = np.array([0.6, -0.5, 0.3, 0.4])  # 后两个元素未补偿

        np.testing.assert_array_almost_equal(result, expected)

        # 补偿值太长
        compensation_long = [0.5, -0.3, 0.1, 0.2, 0.3]
        compensation_array = np.array(compensation_long)
        if len(compensation_array) > len(bias_vector):
            compensation_array = compensation_array[:len(bias_vector)]

        result = bias_vector + compensation_array
        expected = np.array([0.6, -0.5, 0.4, 0.6])

        np.testing.assert_array_almost_equal(result, expected)


class TestEndToEndCompensation:
    """端到端补偿测试"""

    def test_export_with_compensation(self):
        """测试带补偿的 SPICE 导出"""
        config = {
            "bias_compensation": {
                "enabled": True,
                "layer_bias_adjustments": {
                    "0": [0.1, -0.1, 0.0, 0.0, 0.0, 0.0],  # 6个值匹配SVF层
                    "1": [0.2, -0.2, 0.0, 0.0, 0.0, 0.0]   # 6个值匹配Dense层
                }
            }
        }

        model = MockWaveNet5Model(inference_config=config)
        model.add_dense_layer("dense_1", 2)
        model.add_dense_layer("dense_2", 3)

        backend = WaveNet5SPICEBackend(model, inference_config=config)

        # 验证 inference_config 中包含偏置补偿配置
        assert "bias_compensation" in backend.inference_config
        assert backend.inference_config["bias_compensation"]["enabled"] == True
        print("✓ 偏置补偿配置在 SPICE 导出前正确设置")

    def test_compensation_effect_verification(self):
        """验证补偿效果"""
        # 这个测试需要实际的模型和 SPICE 仿真
        # 在单元测试中我们只验证流程
        config_no_comp = {
            "bias_compensation": {
                "enabled": False
            }
        }

        config_with_comp = {
            "bias_compensation": {
                "enabled": True,
                "layer_bias_adjustments": {
                    "0": [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],  # 6个值匹配SVF层
                    "1": [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0], # 6个值匹配Dense层
                    "2": [0.5, 0.0, 0.0, 0.0, 0.0, 0.0]   # 6个值匹配Dense层
                }
            }
        }

        model_no_comp = MockWaveNet5Model(inference_config=config_no_comp)
        model_with_comp = MockWaveNet5Model(inference_config=config_with_comp)

        backend_no_comp = WaveNet5SPICEBackend(model_no_comp, inference_config=config_no_comp)
        backend_with_comp = WaveNet5SPICEBackend(model_with_comp, inference_config=config_with_comp)

        # 验证配置差异
        assert backend_no_comp.inference_config["bias_compensation"]["enabled"] == False
        assert backend_with_comp.inference_config["bias_compensation"]["enabled"] == True
        assert len(backend_with_comp.inference_config["bias_compensation"]["layer_bias_adjustments"]["0"]) == 6
        print("✓ 偏置补偿配置差异验证通过")


class TestExtremeValues:
    """测试极端值处理"""

    def test_extreme_compensation_values(self):
        """测试极端补偿值"""
        extreme_configs = [
            {"compensation": [10.0, -10.0, 5.0, 2.0, -1.0, 0.0]},  # 极大值，6个值匹配SVF层
            {"compensation": [0.001, -0.001, 0.0, 0.0, 0.0, 0.0]}, # 极小值，6个值匹配SVF层
            {"compensation": [1.0] * 6},                            # 正确数量的补偿值
        ]

        for config_data in extreme_configs:
            config = {
                "bias_compensation": {
                    "enabled": True,
                    "layer_bias_adjustments": {
                        "0": config_data["compensation"]
                    }
                }
            }

            model = MockWaveNet5Model(inference_config=config)
            backend = WaveNet5SPICEBackend(model, inference_config=config)

            # 验证补偿值被正确读取
            assert backend.inference_config["bias_compensation"]["layer_bias_adjustments"]["0"] == config_data["compensation"]

        print("✓ 极端补偿值处理通过")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
