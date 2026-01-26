import numpy as np
import matplotlib.pyplot as plt
import os
import unittest
from circuit_base import BaseCircuit
from opamp_adder import OpAmpAdderCircuit
from rc_filter import RCLowPassCircuit
from simulation import CircuitSimulation
import time


class CircuitSimulationTests(unittest.TestCase):
    """电路仿真测试类，用于测试仿真结果与NumPy理论计算的差异"""

    def setUp(self):
        """准备测试环境"""
        self.output_folder = './temp'
        os.makedirs(self.output_folder, exist_ok=True)
        
        # 创建仿真实例
        self.sim = CircuitSimulation(output_folder=self.output_folder, max_workers=4)
        
        # 设置误差容许范围
        self.max_acceptable_diff = 20e-3
        self.mean_acceptable_diff = 5e-3
        
    def test_opamp_adder_circuit(self):
        """测试运放加法器电路"""
        print("\n=== 测试运放加法器电路 ===")
        
        # 生成测试信号，4通道
        n_channels = 4
        t, signals = self.sim.generate_sine_signals(
            t_max=1e-3,  # 1ms仿真时间
            fs=1e6,      # 1MHz采样率
            n_channels=n_channels,
            freqs=[3e3, 7e3, 12e3, 18e3],  # 不同频率的正弦波
            amps=[0.2, 0.3, 0.25, 0.15]    # 不同振幅
        )
        
        # 设置不同通道的增益并创建电路
        gains = [1.0, 2.0, 0.5, 1.5]
        circuit = OpAmpAdderCircuit(n_channels=n_channels, gains=gains)
        
        # 运行仿真
        start_time = time.time()
        result = self.sim.run_simulation_once(
            t, signals, circuit,
            t_max=1e-3,
            t_step=1e-6
        )
        elapsed = time.time() - start_time
        print(f"仿真完成，耗时: {elapsed:.2f}秒")
        
        # 检查结果是否为None
        self.assertIsNotNone(result, "仿真结果不应为None")
        
        # 验证输出值的差异
        max_diff = result['max_diff']
        mean_diff = result['mean_diff']
        rmse = result['rmse']
        
        print(f"最大差异: {max_diff*1000:.3f} mV")
        print(f"平均差异: {mean_diff*1000:.3f} mV")
        print(f"均方根误差: {rmse*1000:.3f} mV")
        
        # 检查差异是否在可接受范围内
        self.assertLess(max_diff, self.max_acceptable_diff, 
                         f"最大差异 {max_diff*1000:.3f} mV 超过允许值 {self.max_acceptable_diff*1000:.1f} mV")
        self.assertLess(mean_diff, self.mean_acceptable_diff, 
                         f"平均差异 {mean_diff*1000:.3f} mV 超过允许值 {self.mean_acceptable_diff*1000:.1f} mV")
        
        # 绘制结果
        self.sim.plot_results(result, title="运放加法器电路", 
                            save_figure=True, figure_name="opamp_adder_test.png")
    
    def test_rc_lowpass_filter(self):
        """测试RC低通滤波器电路"""
        print("\n=== 测试RC低通滤波器电路 ===")
        
        # 生成方波输入
        t = np.linspace(0, 5e-3, 5000)  # 5ms, 5000点
        square_wave = np.zeros_like(t)
        for i in range(len(t)):
            if (i // 500) % 2 == 0:  # 每500点切换一次，产生方波
                square_wave[i] = 1.0
            else:
                square_wave[i] = 0.0
        
        # 创建不同时间常数的RC低通滤波器电路
        rc_circuits = [
            {"name": "RC 0.1ms", "circuit": RCLowPassCircuit(R=10e3, C=1e-8)},   # tau = 0.1ms
            {"name": "RC 1ms", "circuit": RCLowPassCircuit(R=10e3, C=1e-7)},     # tau = 1ms
            {"name": "RC 2ms", "circuit": RCLowPassCircuit(R=20e3, C=1e-7)}      # tau = 2ms
        ]
        
        for rc_data in rc_circuits:
            circuit = rc_data["circuit"]
            name = rc_data["name"]
            tau = circuit.tau * 1000  # 转换为ms
            
            print(f"\n测试 {name} (tau = {tau:.2f}ms)")
            
            # 运行仿真
            start_time = time.time()
            result = self.sim.run_simulation_once(
                t, square_wave, circuit,
                t_max=5e-3,
                t_step=1e-6
            )
            elapsed = time.time() - start_time
            print(f"仿真完成，耗时: {elapsed:.2f}秒")
            
            # 检查结果是否为None
            self.assertIsNotNone(result, f"{name} 仿真结果不应为None")
            
            # 验证输出值的差异
            max_diff = result['max_diff']
            mean_diff = result['mean_diff']
            rmse = result['rmse']
            
            print(f"最大差异: {max_diff*1000:.3f} mV")
            print(f"平均差异: {mean_diff*1000:.3f} mV")
            print(f"均方根误差: {rmse*1000:.3f} mV")
            
            # 检查差异是否在可接受范围内
            self.assertLess(max_diff, self.max_acceptable_diff, 
                             f"最大差异 {max_diff*1000:.3f} mV 超过允许值 {self.max_acceptable_diff*1000:.1f} mV")
            self.assertLess(mean_diff, self.mean_acceptable_diff, 
                             f"平均差异 {mean_diff*1000:.3f} mV 超过允许值 {self.mean_acceptable_diff*1000:.1f} mV")
            
            # 绘制结果
            self.sim.plot_results(result, title=f"RC低通滤波器 (tau={tau:.2f}ms)", 
                                save_figure=True, figure_name=f"rc_filter_{int(tau*10)}_test.png")
    
    def test_batch_simulation(self):
        """测试批量仿真功能"""
        print("\n=== 测试批量仿真功能 ===")
        
        # 创建批量仿真数据，3个批次，每个批次为一个方波但频率不同
        batch_size = 3
        t_max = 10e-3
        fs = 1e6
        t = np.arange(0, t_max, 1/fs)
        
        # 创建批量数据 [batch_size, time_steps]
        batch_signals = np.zeros((batch_size, len(t)))
        
        # 为每个批次生成不同频率的方波
        freqs = [100, 200, 300]  # Hz
        for i in range(batch_size):
            period_samples = int(fs / freqs[i])
            for j in range(len(t)):
                if (j % period_samples) < (period_samples // 2):
                    batch_signals[i, j] = 1.0
                else:
                    batch_signals[i, j] = 0.0
        
        # 创建RC低通滤波器
        circuit = RCLowPassCircuit(R=10e3, C=1e-7)  # tau = 1ms
        
        # 定义进度回调函数
        def progress_update(progress):
            print(f"批量仿真进度: {progress*100:.1f}%")
        
        # 运行批量仿真
        start_time = time.time()
        results = self.sim.run_simulation(
            t, batch_signals, circuit,
            t_max=t_max,
            t_step=1e-6,
            progress_callback=progress_update
        )
        elapsed = time.time() - start_time
        print(f"批量仿真完成，总耗时: {elapsed:.2f}秒，平均每批次耗时: {elapsed/batch_size:.2f}秒")
        
        # 检查结果是否为空
        self.assertIsNotNone(results, "批量仿真结果不应为None")
        self.assertEqual(len(results), batch_size, f"应有{batch_size}个结果，但实际有{len(results)}个")
        
        # 验证每个批次的结果
        for i in range(batch_size):
            result = results[i]
            max_diff = result['max_diff']
            mean_diff = result['mean_diff']
            
            print(f"批次 {i+1} (频率 {freqs[i]}Hz):")
            print(f"  最大差异: {max_diff*1000:.3f} mV")
            print(f"  平均差异: {mean_diff*1000:.3f} mV")
            
            # 检查差异是否在可接受范围内
            self.assertLess(max_diff, self.max_acceptable_diff, 
                            f"批次 {i+1} 最大差异 {max_diff*1000:.3f} mV 超过允许值 {self.max_acceptable_diff*1000:.1f} mV")
            self.assertLess(mean_diff, self.mean_acceptable_diff, 
                            f"批次 {i+1} 平均差异 {mean_diff*1000:.3f} mV 超过允许值 {self.mean_acceptable_diff*1000:.1f} mV")
        
        # 绘制批量仿真结果
        self.sim.plot_batch_results(save_figure=True, figure_name='batch_simulation_test.png')
        
        # 保存批量仿真结果
        self.sim.save_results('batch_test_results.npz')


if __name__ == '__main__':
    plt.ion()  # 交互模式，防止阻塞测试
    unittest.main()