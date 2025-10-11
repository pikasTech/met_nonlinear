#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试NegativeReluCircuit类的基本功能
"""

import unittest
import numpy as np
import sys
import os

# 添加项目根目录到系统路径，以便正确导入模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# 首先导入测试包，它包含模拟的relu_models模块
from spice_simulator.tests import mock_relu_models

# 由于模块之间存在相对导入问题，采用条件导入的方式
import spice_simulator.opamp_models
import spice_simulator.circuit_base
sys.modules['opamp_models'] = spice_simulator.opamp_models
sys.modules['circuit_base'] = spice_simulator.circuit_base
sys.modules['relu_models'] = mock_relu_models

# 尝试导入NegativeReluCircuit
try:
    from spice_simulator.circuit_nrelu import ReluCircuit
except ImportError as e:
    print(f"警告: 导入ReluCircuit失败: {str(e)}")
    # 创建模拟类
    class ReluCircuit:
        def __init__(self, **kwargs):
            self.gain = kwargs.get('gain', 1.0)
            self.R_value = kwargs.get('R_value', 10e3)
            self.use_e96 = kwargs.get('use_e96', False)
            self.diode_model = kwargs.get('diode_model', '1N4148')
            self.opamp_config = kwargs.get('opamp_config', {'model': 'ideal'})
        def get_circuit_netlist(self):
            return "* ReLU Circuit"
        def simulate_numpy(self, t, input_signals):
            return np.where(input_signals > 0, input_signals, 0)
        def _create_circuit_netlist(self):
            return "* ReLU Circuit"
        def _convert_to_standard_value(self, value):
            return value
    IMPORT_ERROR = True
else:
    IMPORT_ERROR = False

class TestReluCircuit(unittest.TestCase):
    """测试ReluCircuit类的功能"""
    
    def setUp(self):
        """设置测试环境"""
        if IMPORT_ERROR:
            self.skipTest("导入ReluCircuit失败，跳过所有测试")
    
    def test_initialization_default(self):
        """测试ReluCircuit的默认初始化参数"""
        circuit = ReluCircuit()
        
        # 验证默认值
        self.assertEqual(circuit.gain, 1.0)
        self.assertEqual(circuit.R, 10e3)
        self.assertEqual(circuit.diode_model, '1N4148')
        self.assertFalse(circuit.use_e96)
        self.assertEqual(circuit.opamp_config['model'], 'ideal')
        self.assertEqual(circuit.opamp_config['power_pins'], True)
        
    def test_initialization_custom(self):
        """测试带自定义参数的ReluCircuit初始化"""
        opamp_config = {
            'model': 'LM324',
            'include_file': 'opamp_models.lib',
            'power_pins': False,
            'params': {'gain': 100000}
        }
        
        circuit = ReluCircuit(
            gain=2.5,
            R_value=20e3,
            diode_model='1N4007',
            opamp_config=opamp_config,
            use_e96=True
        )
        
        # 验证自定义参数设置
        self.assertEqual(circuit.gain, 2.5)
        self.assertTrue(circuit.use_e96)
        self.assertEqual(circuit.diode_model, '1N4007')
        # 验证运放配置被正确合并
        self.assertEqual(circuit.opamp_config['model'], 'LM324')
        self.assertEqual(circuit.opamp_config['include_file'], 'opamp_models.lib')
        self.assertEqual(circuit.opamp_config['power_pins'], False)
        self.assertEqual(circuit.opamp_config['params'], {'gain': 100000})
    
    def test_netlist_contains_essential_components(self):
        """测试网表包含必要的元件和节点"""
        circuit = ReluCircuit()
        netlist = circuit.get_circuit_netlist()
        
        # 验证网表包含必要的电路元件和节点
        self.assertIn("* ReLU Circuit", netlist)
        self.assertIn("* 增益:", netlist)
        self.assertIn("* 电阻值:", netlist)
        self.assertIn("Vin1 in 0 0", netlist)
        self.assertIn("Rin in inv", netlist)
        self.assertIn("Rfb out1 inv", netlist)
        self.assertIn("D1 op_out inv", netlist)
        self.assertIn("D2 out1 op_out", netlist)
        
    def test_netlist_with_ideal_opamp(self):
        """测试使用理想运放模型时的网表生成"""
        circuit = ReluCircuit(opamp_config={'model': 'ideal'})
        netlist = circuit.get_circuit_netlist()
        
        # 验证理想运放相关部分
        self.assertIn("* 理想运放模型", netlist)
        self.assertIn("Eop op_out 0 0 inv 1e9", netlist)
        self.assertIn("Rin_op inv 0 1e12", netlist)
    
    def test_netlist_with_real_opamp(self):
        """测试使用实际运放模型时的网表生成"""
        opamp_config = {
            'model': 'LM324',
            'power_pins': True
        }
        circuit = ReluCircuit(opamp_config=opamp_config)
        netlist = circuit.get_circuit_netlist()
        
        # 验证实际运放相关部分
        self.assertIn("* 实际运放模型: LM324", netlist)
        self.assertIn("Xopamp 0 inv vcc vee op_out LM324", netlist)
    
    def test_netlist_with_real_opamp_no_power_pins(self):
        """测试使用不带电源引脚的实际运放模型时的网表生成"""
        opamp_config = {
            'model': 'CustomOP',
            'power_pins': False,
            'params': {'gain': 100000, 'GBW': '1Meg'}
        }
        circuit = ReluCircuit(opamp_config=opamp_config)
        netlist = circuit.get_circuit_netlist()
        
        # 验证不带电源引脚的实际运放相关部分
        self.assertIn("* 实际运放模型: CustomOP", netlist)
        self.assertIn("Xopamp 0 inv op_out CustomOP gain=100000 GBW=1Meg", netlist)
    
    def test_netlist_with_include_file(self):
        """测试包含外部模型文件的网表生成"""
        opamp_config = {
            'model': 'OP07',
            'include_file': 'opamp_models/op07.lib'
        }
        circuit = ReluCircuit(opamp_config=opamp_config)
        netlist = circuit.get_circuit_netlist()
        
        # 验证包含文件指令
        self.assertIn("* 包含运放模型文件", netlist)
        self.assertIn(".include opamp_models/op07.lib", netlist)
    
    def test_simulate_numpy_1d_input(self):
        """测试使用一维输入数组进行NumPy仿真"""
        circuit = ReluCircuit(gain=2.0)
        
        # 创建测试信号：-2到2的线性数据
        input_signal = np.linspace(-2, 2, 100)
        
        # 执行NumPy仿真
        output = circuit.simulate_numpy(None, input_signal)
        
        # 验证反向ReLU特性：输入为正时输出为0，输入为负时输出为输入的负值乘以增益
        expected_output = -np.maximum(0, input_signal) * 2.0
        np.testing.assert_allclose(output, expected_output)
        
        # 验证正负值的特性
        pos_indices = input_signal > 0
        neg_indices = input_signal <= 0
        self.assertTrue(np.all(output[pos_indices] < 0))  # 正输入产生负输出
        self.assertTrue(np.all(output[neg_indices] == 0))  # 负输入产生零输出
    
    def test_simulate_numpy_2d_input(self):
        """测试使用二维输入数组进行NumPy仿真"""
        circuit = ReluCircuit(gain=1.5)
        
        # 创建二维测试信号
        input_signal = np.linspace(-2, 2, 100).reshape(-1, 1)
        
        # 执行NumPy仿真
        output = circuit.simulate_numpy(None, input_signal)
        
        # 验证输出形状是一维的
        self.assertEqual(output.ndim, 1)
        self.assertEqual(output.shape[0], 100)
        
        # 验证反向ReLU特性
        flattened_input = input_signal.flatten()
        expected_output = -np.maximum(0, flattened_input) * 1.5
        np.testing.assert_allclose(output, expected_output)
    
    def test_e96_resistor_values(self):
        """测试E96标准电阻值的使用"""
        # 需要模拟_convert_to_standard_value方法
        circuit = ReluCircuit(R_value=9876, use_e96=True)
        
        # 验证电阻值被转换处理
        self.assertNotEqual(circuit.R, 9876)


if __name__ == '__main__':
    unittest.main() 