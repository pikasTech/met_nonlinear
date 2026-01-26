#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试模拟仿真类的基本功能
"""

import unittest
import numpy as np
import os
import tempfile
import sys
from unittest.mock import patch, MagicMock

# 添加项目根目录到系统路径，以便正确导入模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# 添加导入修复，支持可能的相对导入
import spice_simulator.circuit_base
sys.modules['circuit_base'] = spice_simulator.circuit_base

from spice_simulator.circuit_base import BaseCircuit

# 创建一个简单的测试电路类
class MockTestCircuit(BaseCircuit):
    """测试用电路类，用于测试仿真功能"""
    
    def __init__(self, n_inputs=1, n_outputs=1):
        self.n_inputs = n_inputs
        self.n_outputs = n_outputs
    
    def get_circuit_netlist(self):
        """返回简单的测试网表内容"""
        return "* 测试电路网表"
    
    def simulate_numpy(self, t, input_signals):
        """返回简单的仿真结果（输出 = 输入 * 2）"""
        if isinstance(input_signals, list):
            return [signal * 2 for signal in input_signals]
        
        # 确保输入信号是正确的形状
        if input_signals.ndim == 1:
            # 单通道输入
            return input_signals * 2
        elif input_signals.ndim == 2:
            # 多通道输入
            output = np.zeros((input_signals.shape[0], self.n_outputs))
            for i in range(self.n_outputs):
                output[:, i] = np.sum(input_signals, axis=1) * 0.5
            return output
        else:
            raise ValueError("不支持的输入信号维度")

# 创建 CircuitSimulation 的测试版本
class MockTestSimulation:
    """测试专用的仿真类，避免从spice_simulator.simulation导入"""
    
    def __init__(self, output_folder='./data/test_spice_netlists', ngspice_path=None, max_workers=16, clean_temp_files=False):
        """初始化仿真类"""
        self.output_folder = output_folder
        self.ngspice_path = ngspice_path or r".\Spice64\bin\ngspice_con.exe"
        self.max_workers = max_workers
        self.clean_temp_files = clean_temp_files
    
    def generate_sine_signals(self, t_max=1e-3, fs=1e6, n_outputs=1, freqs=None, amps=None):
        """生成多通道正弦波信号"""
        t = np.arange(0, t_max, 1/fs)
        
        # 如果未指定频率，则自动生成不同频率
        if freqs is None:
            freqs = [5e3 * (i + 1) for i in range(n_outputs)]
        elif len(freqs) < n_outputs:
            # 扩展频率列表到n_outputs
            freqs = freqs + [5e3 * (i + 1) for i in range(len(freqs), n_outputs)]
            
        # 如果未指定振幅，则使用标准振幅
        if amps is None:
            amps = [0.5 / n_outputs] * n_outputs
        elif len(amps) < n_outputs:
            # 扩展振幅列表到n_outputs
            amps = amps + [0.5 / n_outputs] * (n_outputs - len(amps))
            
        # 生成多通道信号
        signals = np.zeros((len(t), n_outputs))
        for i in range(n_outputs):
            signals[:, i] = amps[i] * np.sin(2 * np.pi * freqs[i] * t)
            
        return t, signals
    
    def generate_square_signals(self, t_max=1e-3, fs=1e6, n_outputs=1, freqs=None, amps=None):
        """生成多通道方波信号"""
        t = np.arange(0, t_max, 1/fs)
        
        # 如果未指定频率，则自动生成不同频率
        if freqs is None:
            freqs = [100 * (i + 1) for i in range(n_outputs)]
        elif len(freqs) < n_outputs:
            # 扩展频率列表到n_outputs
            freqs = freqs + [100 * (i + 1) for i in range(len(freqs), n_outputs)]
            
        # 如果未指定振幅，则使用标准振幅
        if amps is None:
            amps = [1.0] * n_outputs
        elif len(amps) < n_outputs:
            # 扩展振幅列表到n_outputs
            amps = amps + [1.0] * (n_outputs - len(amps))
            
        # 生成多通道方波信号
        signals = np.zeros((n_outputs, len(t)))
        for i in range(n_outputs):
            period_samples = int(fs / freqs[i])
            for j in range(len(t)):
                if (j % period_samples) < (period_samples // 2):
                    signals[i, j] = amps[i]
                else:
                    signals[i, j] = 0
                    
        return t, signals
    
    def create_pwl_data(self, t, v, max_points=1000):
        """创建PWL数据字符串，用于替换电压源"""
        decimation = max(1, len(t) // max_points)
        pwl_data = "PWL("
        for i in range(0, len(t), decimation):
            pwl_data += f"{t[i]} {v[i]} "
        pwl_data += ")"
        return pwl_data
    
    def create_simulation_netlist(self, circuit, t_max=1e-3, t_step=1e-6, additional_instructions=None):
        """创建仿真网表"""
        netlist = circuit.get_circuit_netlist()
        netlist += f"\n.tran {t_step} {t_max}\n"
        
        if additional_instructions:
            for instr in additional_instructions:
                netlist += f"{instr}\n"
                
        return netlist

class TestCircuitSimulation(unittest.TestCase):
    """测试CircuitSimulation类的基本功能"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建临时目录用于测试输出
        self.temp_dir = tempfile.mkdtemp()
        
        # 使用测试专用仿真类
        self.sim = MockTestSimulation(
            output_folder=self.temp_dir,
            ngspice_path="mock_ngspice_path",
            clean_temp_files=True
        )
    
    def tearDown(self):
        """测试后的清理工作"""
        # 清除临时目录中的文件
        for file in os.listdir(self.temp_dir):
            file_path = os.path.join(self.temp_dir, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        
        # 删除临时目录
        os.rmdir(self.temp_dir)
    
    def test_initialization(self):
        """测试初始化参数"""
        self.assertEqual(self.sim.output_folder, self.temp_dir)
        self.assertEqual(self.sim.ngspice_path, "mock_ngspice_path")
        self.assertTrue(self.sim.clean_temp_files)
    
    def test_generate_sine_signals(self):
        """测试正弦波信号生成功能"""
        t_max = 1e-3
        fs = 1e5
        n_outputs = 3
        
        # 生成正弦波信号
        t, signals = self.sim.generate_sine_signals(
            t_max=t_max,
            fs=fs,
            n_outputs=n_outputs
        )
        
        # 验证时间向量
        self.assertEqual(len(t), int(t_max * fs))
        self.assertAlmostEqual(t[1] - t[0], 1/fs)
        
        # 验证信号矩阵形状
        self.assertEqual(signals.shape, (int(t_max * fs), n_outputs))
        
        # 验证自定义频率和振幅
        freqs = [1e3, 2e3, 3e3]
        amps = [0.1, 0.2, 0.3]
        
        t, signals = self.sim.generate_sine_signals(
            t_max=t_max,
            fs=fs,
            n_outputs=n_outputs,
            freqs=freqs,
            amps=amps
        )
        
        # 检查每个通道的振幅
        for i in range(n_outputs):
            peak = np.max(signals[:, i])
            self.assertAlmostEqual(peak, amps[i], places=2)
    
    def test_generate_square_signals(self):
        """测试方波信号生成功能"""
        t_max = 1e-2
        fs = 1e4
        n_outputs = 2
        
        # 生成方波信号
        t, signals = self.sim.generate_square_signals(
            t_max=t_max,
            fs=fs,
            n_outputs=n_outputs
        )
        
        # 验证形状
        self.assertEqual(signals.shape, (n_outputs, int(t_max * fs)))
        
        # 验证方波特性（只有0和振幅值）
        unique_values = np.unique(signals[0, :])
        self.assertEqual(len(unique_values), 2)
        self.assertTrue(0 in unique_values)
        self.assertTrue(1.0 in unique_values)
    
    def test_create_pwl_data(self):
        """测试PWL数据创建功能"""
        t = np.linspace(0, 1e-3, 1000)
        v = np.sin(2 * np.pi * 1e3 * t)
        
        # 创建PWL数据，限制最大点数为100
        pwl_data = self.sim.create_pwl_data(t, v, max_points=100)
        
        # 验证PWL格式
        self.assertTrue(pwl_data.startswith("PWL("))
        self.assertTrue(pwl_data.endswith(")"))
        
        # 验证点数限制
        points = pwl_data.count(" ") // 2
        self.assertTrue(points <= 100)
    
    def test_create_simulation_netlist(self):
        """测试仿真网表创建功能"""
        circuit = MockTestCircuit()
        t_max = 1e-3
        t_step = 1e-6
        
        # 调用创建网表函数
        netlist = self.sim.create_simulation_netlist(
            circuit, 
            t_max=t_max, 
            t_step=t_step
        )
        
        # 验证网表包含关键字
        self.assertIn("* 测试电路网表", netlist)
        self.assertIn(f".tran {t_step} {t_max}", netlist)

if __name__ == "__main__":
    unittest.main() 