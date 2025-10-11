#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试BaseCircuit类的基本功能
"""

import unittest
import numpy as np
import sys
import os

# 添加项目根目录到系统路径，以便正确导入模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from spice_simulator.circuit_base import BaseCircuit

class MockCircuit(BaseCircuit):
    """测试用的电路模拟类，实现了BaseCircuit的抽象方法"""
    
    def __init__(self, n_inputs=1, n_outputs=1):
        self.n_inputs = n_inputs
        self.n_outputs = n_outputs
    
    def get_circuit_netlist(self):
        """返回模拟的网表内容"""
        return "* 测试网表"
    
    def simulate_numpy(self, t, input_signals):
        """返回模拟的仿真结果"""
        # 创建一个简单的通过函数：输出 = 输入 * 2
        if isinstance(input_signals, list):
            return [signal * 2 for signal in input_signals]
        else:
            return input_signals * 2

class TestBaseCircuit(unittest.TestCase):
    """测试BaseCircuit类的基础功能"""
    
    def test_e96_values(self):
        """测试E96标准电阻值列表"""
        circuit = MockCircuit()
        self.assertEqual(len(circuit.E96_VALUES), 96)
        self.assertEqual(circuit.E96_VALUES[0], 1.00)
        self.assertEqual(circuit.E96_VALUES[-1], 9.76)
    
    def test_convert_to_standard_value(self):
        """测试电阻值转换为标准值的功能"""
        circuit = MockCircuit()
        
        # 测试边界情况
        self.assertEqual(circuit._convert_to_standard_value(0), 0)
        self.assertEqual(circuit._convert_to_standard_value(-1), -1)
        
        # 测试具体值转换
        self.assertAlmostEqual(circuit._convert_to_standard_value(1.03), 1.02, places=2)
        self.assertAlmostEqual(circuit._convert_to_standard_value(4.7), 4.75, places=2)
        self.assertAlmostEqual(circuit._convert_to_standard_value(10.4), 10.5, places=1)
        self.assertAlmostEqual(circuit._convert_to_standard_value(47000), 47500, delta=500)
    
    def test_get_input_source_names(self):
        """测试获取输入源名称的功能"""
        # 单输入通道
        circuit_single = MockCircuit(n_inputs=1)
        self.assertEqual(circuit_single.get_input_source_names(), ['Vin1'])
        
        # 多输入通道
        circuit_multi = MockCircuit(n_inputs=3)
        self.assertEqual(circuit_multi.get_input_source_names(), ['Vin1', 'Vin2', 'Vin3'])
    
    def test_get_output_node_names(self):
        """测试获取输出节点名称的功能"""
        # 单输出通道
        circuit_single = MockCircuit(n_outputs=1)
        self.assertEqual(circuit_single.get_output_node_names(), ['out1'])
        
        # 多输出通道
        circuit_multi = MockCircuit(n_outputs=4)
        self.assertEqual(circuit_multi.get_output_node_names(), ['out1', 'out2', 'out3', 'out4'])

if __name__ == "__main__":
    unittest.main() 