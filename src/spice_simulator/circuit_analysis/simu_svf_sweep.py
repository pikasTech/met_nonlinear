"""
基于 simu_sweep.py，使用 simulation 里面的 spice 仿真生成SVF滤波器的扫频波形，
扫频波形的数据格式和保存方式参考 waveprocessor.py，要求生成的波形文件能够被 waveprocessor.py 的 load_waveform 方法加载。

实现状态变量滤波器(SVF)的扫频测试，保存结果，并分析频率响应。与RC滤波器不同，SVF滤波器可以同时输出高通、带通和低通滤波结果。

使用simu_sweep.py的三个工具函数实现完整的扫频分析流程：
1. generate_sweep_input_waveform - 生成扫频输入波形
2. simulate_circuit_with_sweep - 使用电路仿真生成输出波形
3. analyze_sweep_response - 分析扫频响应得到系统对象
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import matplotlib
from typing import List, Union, Dict, Any, Optional, Tuple

OPAMP_CONFIG = {
    'model': 'OPAx205A',
    'include_file': "spice_simulator\spice_models\OPAx205A.LIB",
}


# 添加当前目录到路径，确保可以导入所有相关模块
current_dir = Path(__file__).parent.absolute()
sys.path.append(str(current_dir))

# 添加 spice_simulator 目录到 sys.path
spice_simulator_dir = current_dir.parent / "spice_simulator"
sys.path.append(str(spice_simulator_dir))
sys.path.append(str(current_dir.parent / "calibration_analyzer"))

# 尝试导入所需模块
try:
    from spice_simulator.circuit_svf import SVFFilter
    from calibration_analyzer.waveprocessor import WaveProcessor
    from calibration_analyzer.wavedata import WaveData, WaveRecord
    from calibration_analyzer.exam_class import System
    # 从simu_sweep导入三个工具函数
    from simu_sweep import (
        simulate_circuit_with_sweep,
    )
except ImportError as e:
    print(f"导入错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


def main():
    """主函数"""
    # 创建输出目录
    output_dir = Path(__file__).parent / "temp"
    output_dir.mkdir(exist_ok=True)

    # 创建波形处理器
    processor = WaveProcessor()

    # 创建SVF滤波器
    cutoff_freq = 10  # 截止频率为10Hz
    filter_Q = 5  # 标准Q值
    svf_filter = SVFFilter(cutoff_freq=cutoff_freq,
                           Q=filter_Q, opamp_config=OPAMP_CONFIG)
    print(f"SVF滤波器截止频率: {cutoff_freq:.2f} Hz, Q因子: {filter_Q}")

    # 设置扫频范围，从截止频率的0.1倍到10倍，取20个点
    freq_min = 5
    freq_max = 200
    freq_range = np.logspace(np.log10(freq_min), np.log10(freq_max), 100)
    print(f"扫频范围: {min(freq_range):.2f} Hz - {max(freq_range):.2f} Hz")

    # 步骤1: 生成扫频输入波形
    print("1. 正在生成扫频输入波形...")
    input_wave_path = output_dir / "svf_sweep_input"
    input_wave_data = processor.generate_sweep_input_waveform(
        freq_range=freq_range,
        amplitude=1.0,
        fs=2000,  # 提高采样率，确保高频信号采样足够
        time_length=1.0,
        min_periods=4,
        max_periods=15,  # 增加最大周期数，改善低频信号分析
        description="SVF滤波器测试输入扫频波形"
    )
    # 保存输入波形
    processor.save_waveform(str(input_wave_path), input_wave_data)
    print(f"输入波形已保存到: {input_wave_path}.wave")

    # 步骤2: 使用电路仿真生成输出波形
    print("2. 正在进行电路仿真...")
    input_wave_data_loaded = processor.load_waveform(str(input_wave_path))
    output_wave_path = output_dir / "svf_sweep_output"
    output_wave_data = simulate_circuit_with_sweep(
        circuit=svf_filter,
        input_wave_data=input_wave_data_loaded,
        output_folder=str(output_dir)
    )
    # 保存输出波形
    processor.save_waveform(str(output_wave_path), output_wave_data)
    print(f"输出波形已保存到: {output_wave_path}.wave")    # 步骤3: 分析频率响应
    print("3. 正在分析SVF滤波器频率响应...")
    input_wave_data_loaded = processor.load_waveform(str(input_wave_path))
    output_wave_data_loaded = processor.load_waveform(str(output_wave_path))

    # analyze_sweep_response会返回System对象的列表，因为SVF滤波器有3个输出通道
    systems = processor.analyze_sweep_response(
        input_wave_data_loaded, output_wave_data_loaded)

    # 确保systems是列表
    if not isinstance(systems, list):
        systems = [systems]

    # SVF有三种输出: 高通(HP)、带通(BP)和低通(LP)
    output_types = ["HP", "BP", "LP"]

    # 将systems列表映射到命名的字典
    systems_dict = {}
    for i, output_type in enumerate(output_types[:len(systems)]):
        systems_dict[output_type] = systems[i]

    # 获取频率数据 (对所有系统相同)
    frequencies = systems[0].f

    # 计算理论频响
    theoretical_freqs = np.logspace(
        np.log10(freq_min), np.log10(freq_max), 100)

    theoretical_gains = {output_type: [] for output_type in output_types}
    theoretical_phases = {output_type: [] for output_type in output_types}

    s = System.s
    Q = filter_Q
    omega0 = 2 * np.pi * cutoff_freq

    highpass_expr = s**2 / (s**2 + (omega0/Q)*s + omega0**2)
    bandpass_expr = (s*(omega0))/(s**2 + (omega0/Q)*s + omega0**2)
    lowpass_expr = (omega0**2) / (s**2 + (omega0/Q)*s + omega0**2)

    HP_system = System.fromSymbol(highpass_expr, f=theoretical_freqs)
    BP_system = System.fromSymbol(bandpass_expr, f=theoretical_freqs)
    LP_system = System.fromSymbol(lowpass_expr, f=theoretical_freqs)

    theoretical_gains['HP'] = HP_system.toabs()
    theoretical_gains['BP'] = BP_system.toabs()
    theoretical_gains['LP'] = LP_system.toabs()
    theoretical_phases['HP'] = HP_system.tophase()
    theoretical_phases['BP'] = BP_system.tophase()
    theoretical_phases['LP'] = LP_system.tophase()

    # 绘制频率响应图表
    plt.figure(figsize=(10, 12))

    # 设置颜色和标记
    colors = {'HP': 'r', 'BP': 'g', 'LP': 'b'}
    markers = {'HP': 'o', 'BP': 's', 'LP': '^'}
    names = {'HP': '高通', 'BP': '带通', 'LP': '低通'}

    # 增益响应
    plt.subplot(2, 1, 1)
    for output_type in output_types:
        if output_type in systems_dict:
            # 理论曲线
            plt.semilogx(theoretical_freqs,
                         20 * np.log10(theoretical_gains[output_type]),
                         f'{colors[output_type]}-',
                         label=f'{names[output_type]}理论值')

            # 仿真数据点
            plt.semilogx(frequencies,
                         20 * np.log10(systems_dict[output_type].toabs()),
                         f'{colors[output_type]}{markers[output_type]}',
                         label=f'{names[output_type]}仿真值', markersize=4)

    plt.axvline(x=cutoff_freq, color='k', linestyle='--',
                label=f'截止频率 ({cutoff_freq:.1f} Hz)')
    plt.axhline(y=-3, color='k', linestyle=':', label='-3dB')
    plt.grid(True, which="both", ls="--")
    plt.xlabel('频率 (Hz)')
    plt.ylabel('增益 (dB)')
    plt.title(f'SVF滤波器增益响应 (f_c={cutoff_freq}Hz, Q={filter_Q})')
    plt.legend()

    # 相位响应
    plt.subplot(2, 1, 2)
    for output_type in output_types:
        if output_type in systems_dict:
            # 理论曲线
            plt.semilogx(theoretical_freqs,
                         theoretical_phases[output_type],
                         f'{colors[output_type]}-',
                         label=f'{names[output_type]}理论值')

            # 仿真数据点
            plt.semilogx(frequencies,
                         systems_dict[output_type].tophase(),
                         f'{colors[output_type]}{markers[output_type]}',
                         label=f'{names[output_type]}仿真值', markersize=4)

    plt.axvline(x=cutoff_freq, color='k', linestyle='--',
                label=f'截止频率 ({cutoff_freq:.1f} Hz)')
    plt.grid(True, which="both", ls="--")
    plt.xlabel('频率 (Hz)')
    plt.ylabel('相位 (度)')
    plt.title(f'SVF滤波器相位响应 (f_c={cutoff_freq}Hz, Q={filter_Q})')
    plt.legend()

    plt.tight_layout()
    plt.savefig(str(output_dir / "svf_sweep.png"), dpi=300)
    plt.show()

    print("SVF滤波器扫频测试完成!")


if __name__ == "__main__":
    main()
