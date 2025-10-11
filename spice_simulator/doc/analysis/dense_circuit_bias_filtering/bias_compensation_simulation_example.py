#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
运放偏置误差补偿仿真示例

本示例展示如何仿真验证使用输出高通滤波器补偿偏置误差的效果
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei']  # Windows
rcParams['axes.unicode_minus'] = False

class BiasCompensationAnalysis:
    """偏置补偿分析类"""
    
    def __init__(self, bias_target=2.5, op_offset=0.01, r_hp=1e6, c_hp=1.6e-6):
        """
        参数:
            bias_target: 目标偏置电压 (V)
            op_offset: 运放偏置电压 (V)
            r_hp: 高通滤波器电阻 (Ω)
            c_hp: 高通滤波器电容 (F)
        """
        self.bias_target = bias_target
        self.op_offset = op_offset
        self.r_hp = r_hp
        self.c_hp = c_hp
        self.fc = 1 / (2 * np.pi * r_hp * c_hp)  # 截止频率
        self.tau = r_hp * c_hp  # 时间常数
    
    def step_response(self, t, v_initial):
        """
        计算阶跃响应
        
        参数:
            t: 时间数组 (s)
            v_initial: 初始电压 (含偏置误差) (V)
        
        返回:
            v_out: 补偿后的输出电压
        """
        # 高通滤波器的阶跃响应
        # V_out(t) = V_bias + (V_initial - V_bias) * exp(-t/τ)
        v_out = self.bias_target + (v_initial - self.bias_target) * np.exp(-t / self.tau)
        return v_out
    
    def frequency_response(self, f):
        """
        计算频率响应
        
        参数:
            f: 频率数组 (Hz)
        
        返回:
            gain_db: 增益 (dB)
            phase_deg: 相位 (度)
        """
        s = 2j * np.pi * f
        H = s * self.tau / (1 + s * self.tau)
        gain_db = 20 * np.log10(np.abs(H))
        phase_deg = np.angle(H) * 180 / np.pi
        return gain_db, phase_deg
    
    def simulate_compensation(self):
        """仿真偏置补偿效果"""
        # 时间范围
        t = np.linspace(0, 10 * self.tau, 1000)
        
        # 不同的初始偏置误差
        offset_errors = [-0.1, -0.05, 0, 0.05, 0.1]  # V
        
        plt.figure(figsize=(12, 8))
        
        # 子图1: 阶跃响应
        plt.subplot(2, 2, 1)
        for offset in offset_errors:
            v_initial = self.bias_target + offset + self.op_offset
            v_out = self.step_response(t, v_initial)
            plt.plot(t, v_out, label=f'偏移={offset:.2f}V')
        
        plt.axhline(y=self.bias_target, color='r', linestyle='--', 
                   label=f'目标偏置={self.bias_target}V')
        plt.xlabel('时间 (s)')
        plt.ylabel('输出电压 (V)')
        plt.title('偏置补偿阶跃响应')
        plt.legend()
        plt.grid(True)
        
        # 子图2: 建立时间分析
        plt.subplot(2, 2, 2)
        settling_times = [1, 2, 3, 4, 5]  # 时间常数的倍数
        settling_percentages = [1 - np.exp(-n) for n in settling_times]
        
        plt.bar(settling_times, np.array(settling_percentages) * 100)
        plt.xlabel('时间 (τ)')
        plt.ylabel('建立百分比 (%)')
        plt.title('建立时间分析')
        plt.grid(True, axis='y')
        
        # 添加数值标签
        for i, pct in enumerate(settling_percentages):
            plt.text(i + 1, pct * 100 + 1, f'{pct*100:.1f}%', 
                    ha='center', va='bottom')
        
        # 子图3: 频率响应
        plt.subplot(2, 2, 3)
        f = np.logspace(-3, 3, 1000)  # 0.001Hz 到 1000Hz
        gain_db, phase_deg = self.frequency_response(f)
        
        plt.semilogx(f, gain_db)
        plt.axvline(x=self.fc, color='r', linestyle='--', 
                   label=f'fc={self.fc:.2f}Hz')
        plt.xlabel('频率 (Hz)')
        plt.ylabel('增益 (dB)')
        plt.title('高通滤波器幅频响应')
        plt.legend()
        plt.grid(True)
        plt.ylim(-40, 5)
        
        # 子图4: 相频响应
        plt.subplot(2, 2, 4)
        plt.semilogx(f, phase_deg)
        plt.axvline(x=self.fc, color='r', linestyle='--', 
                   label=f'fc={self.fc:.2f}Hz')
        plt.axhline(y=45, color='g', linestyle=':', label='45°')
        plt.xlabel('频率 (Hz)')
        plt.ylabel('相位 (度)')
        plt.title('高通滤波器相频响应')
        plt.legend()
        plt.grid(True)
        plt.ylim(0, 95)
        
        plt.tight_layout()
        plt.show()
    
    def analyze_drive_requirements(self):
        """分析驱动能力要求"""
        # 假设最大偏置误差
        max_offset = 0.1  # V
        
        # 不同的电阻值
        r_values = np.logspace(3, 7, 5)  # 1kΩ 到 10MΩ
        
        print("驱动电流需求分析")
        print("=" * 50)
        print(f"最大偏置误差: {max_offset}V")
        print("-" * 50)
        print("R值\t\t最大电流\tfc@C=1μF\t建立时间(99%)")
        print("-" * 50)
        
        for r in r_values:
            i_max = max_offset / r * 1e6  # 转换为μA
            fc = 1 / (2 * np.pi * r * 1e-6)  # 假设 C=1μF
            t_settle = 5 * r * 1e-6  # 5τ
            
            print(f"{r/1e3:.0f}kΩ\t\t{i_max:.1f}μA\t\t{fc:.2f}Hz\t\t{t_settle:.2f}s")


def main():
    """主函数"""
    print("运放偏置误差补偿仿真\n")
    
    # 创建分析器
    analyzer = BiasCompensationAnalysis(
        bias_target=2.5,    # 目标偏置电压 2.5V
        op_offset=0.01,     # 运放偏置 10mV
        r_hp=1e6,           # 1MΩ
        c_hp=1.6e-6         # 1.6μF
    )
    
    # 打印参数
    print(f"仿真参数:")
    print(f"  目标偏置电压: {analyzer.bias_target}V")
    print(f"  运放偏置电压: {analyzer.op_offset*1000}mV")
    print(f"  高通滤波器: R={analyzer.r_hp/1e6}MΩ, C={analyzer.c_hp*1e6}μF")
    print(f"  截止频率: {analyzer.fc:.3f}Hz")
    print(f"  时间常数: {analyzer.tau:.2f}s\n")
    
    # 分析驱动需求
    analyzer.analyze_drive_requirements()
    
    # 仿真补偿效果
    print("\n正在生成仿真图表...")
    analyzer.simulate_compensation()


if __name__ == "__main__":
    main()