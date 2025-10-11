"""
基于 simulation.py，使用 simulation 里面的 spice 仿真生成扫频波形，扫频波形的数据格式和保存方式参考 waveprocessor.py，要求生成的波形文件能够被 waveprocessor.py 的 load_waveform 方法加载。

本模块提供三个主要的工具函数，实现完整的扫频分析流程：
1. generate_sweep_input_waveform - 根据扫频配置生成扫频输入波形的波形文件。
2. simulate_circuit_with_sweep - 导入扫频输入波形文件，仿真得到扫频输出波形文件。
3. analyze_sweep_response - 导入扫频输出波形文件，分析得到system或者system的列表。

扫频分析流程：
- 首先使用generate_sweep_input_waveform生成输入波形
- 然后用simulate_circuit_with_sweep进行电路仿真得到输出波形
- 最后通过analyze_sweep_response分析得到频率响应

注意：扫频输出文件可以有多个channel，第0channel永远是扫频输入波形，其他channel是扫频输出波形。如果有多个channel的扫频输出波形，则analyze_sweep_response输出的就是system的列表。

通过添加 spice_simulator/ 目录到 sys.path 来导入 simulation.py 和 spice_simulator.py 等文件。
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import matplotlib
from typing import List, Tuple, Optional, Dict, Any, Union
import re


# 添加当前目录到路径，确保可以导入所有相关模块
current_dir = Path(__file__).parent.absolute()
sys.path.append(str(current_dir))

# 添加 spice_simulator 目录到 sys.path
spice_simulator_dir = current_dir.parent / "spice_simulator"
sys.path.append(str(spice_simulator_dir))
sys.path.append(str(current_dir.parent / "calibration_analyzer"))

# 尝试导入所需模块
try:
    from spice_simulator.simulation import CircuitSimulation
    from spice_simulator.circuit_RC import RCLowPassFilter
    from spice_simulator.circuit_base import BaseCircuit
    from calibration_analyzer.waveprocessor import WaveProcessor
    from calibration_analyzer.wavedata import WaveData, WaveRecord
    from calibration_analyzer.exam_class import TimeSeries, System
except ImportError as e:
    print(f"导入错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


def simulate_circuit_with_sweep(circuit: BaseCircuit,
                                input_wave_data: Union[WaveData, str],
                                output_folder='./temp',
                                ngspice_path=r".\spice_simulator\Spice64\bin\ngspice_con.exe",
                                output_file_path=None) -> WaveData:
    """
    导入扫频输入波形文件，使用电路仿真生成扫频输出波形文件

    参数:
        circuit: 电路对象，例如RCLowPassFilter
        input_wave_data: 输入扫频波形数据或波形文件路径
        output_folder: 输出文件夹
        ngspice_path: NGspice可执行文件路径
        output_file_path: 输出波形文件路径

    返回:
        WaveData: 只包含输出波形的WaveData对象（不包含输入通道）
    """
    # 如果输入是路径，加载波形文件
    if isinstance(input_wave_data, str):
        input_file_path = input_wave_data
        processor = WaveProcessor()
        input_wave_data = processor.load_waveform(input_wave_data)
    else:
        input_file_path = None
        if not isinstance(input_wave_data, WaveData):
            raise ValueError("输入波形数据必须是WaveData对象或文件路径")

    # 创建波形数据对象
    wave_data = WaveData(
        description=f"电路仿真结果 - {input_wave_data.description}",
        author="SPICE Simulator"
    )

    # 创建仿真实例
    sim = CircuitSimulation(output_folder=output_folder,
                            ngspice_path=ngspice_path)

    # 批量处理所有频点记录，零填充并使用 run_simulation
    records = input_wave_data.records
    batch_size = len(records)
    # 获取原始信号长度和频率，确保采样率一致
    lengths = [len(rec.get_channel(0)) for rec in records]
    sample_rates = {rec.sample_rate for rec in records}
    if len(sample_rates) != 1:
        raise ValueError("所有记录的采样率必须相同，才能批量仿真")
    fs = sample_rates.pop()
    max_len = max(lengths)
    # 构造批量信号，并零填充至 max_len
    max_input_channels = input_wave_data.num_channels_range[1]
    batch_signals = np.zeros((batch_size, max_len, max_input_channels))
    for idx, rec in enumerate(records):
        data = rec.data
        batch_signals[idx, :len(data), :] = data

    # 调用批量仿真，传入截断长度以跳过填充的零
    sim_result = sim.run_simulation(
        batch_signals,
        circuit,
        sample_rate=fs,
        truncate_lengths=lengths
    )
    # 形状 [batch_size, time_steps, outputs]
    spice_out = sim_result['spice_outputs']

    # 根据原始长度构造每条记录，并添加至 wave_data（只包含输出通道）
    for idx, rec in enumerate(records):
        freq = rec.user_metadata.get("frequency")
        L = lengths[idx]
        out_mat = spice_out[idx, :L, :]        # 构建数据列和通道名（不再包含输入通道）
        if out_mat.ndim == 1 or out_mat.shape[1] == 1:
            rec_data = out_mat.flatten().reshape(-1, 1)
            ch_names = ["Output"]
        else:
            cols = [out_mat[:, j] for j in range(out_mat.shape[1])]
            rec_data = np.column_stack(cols)
            ch_names = [f"Output_{j+1}" for j in range(out_mat.shape[1])]

        # 创建新的 recard_id，如果已经有 _spice 后缀，则改成 _spice1、_spice2 等
        # 用正则匹配
        match = re.search(r'_spice(\d+)?$', rec.record_id)
        if match:
            if match.group(1) is None:
                new_record_id = rec.record_id.replace('_spice', '_spice2')
            else:
                num = int(match.group(1)) + 1
                new_record_id = rec.record_id[:-
                                              len(match.group(0))] + f"_spice{num}"
        else:
            new_record_id = rec.record_id + "_spice"

        sim_rec = WaveRecord(
            data=rec_data,
            sample_rate=fs,
            channel_names=ch_names,
            units="V",
            record_id=new_record_id,
            user_metadata={
                **rec.user_metadata,  # 保留原始元数据
                "spice_simulation": True  # 添加SPICE仿真标记
            }
        )
        wave_data.add_record(sim_rec)

    # 添加电路信息到元数据
    wave_data.add_user_metadata("circuit_type", type(circuit).__name__)
    # 添加输入波形信息作为参考
    wave_data.add_user_metadata(
        "input_waveform_description", input_wave_data.description)
    wave_data.add_user_metadata("type", "output_sweep")
    wave_data.add_user_metadata(
        "input_waveform_description", input_wave_data.description)
    wave_data.add_user_metadata("type", "output_sweep")

    # 添加电路参数(如果存在)
    if hasattr(circuit, 'R'):
        wave_data.add_user_metadata("R_value", circuit.R)
    if hasattr(circuit, 'C'):
        wave_data.add_user_metadata("C_value", circuit.C)
    if hasattr(circuit, 'cutoff_freq'):
        wave_data.add_user_metadata("cutoff_freq", circuit.cutoff_freq)

    # 添加处理记录到元数据
    # 获取输入波形文件的元数据作为参考
    input_metadata = {
        "file_info": {
            "input_file_path": input_file_path or "未指定路径",
            "has_been_saved": input_file_path is not None and isinstance(input_file_path, str)
        },
        "wave_info": {
            "description": input_wave_data.description,
            "author": input_wave_data.author,
            "type": input_wave_data.user_metadata.get("type", "unknown"),
            "freq_range": input_wave_data.user_metadata.get("freq_range", []),
            "amplitude": input_wave_data.user_metadata.get("amplitude", None),
            "records_count": len(input_wave_data.records) if hasattr(input_wave_data, "records") else 0
        },
        "metadata": dict(input_wave_data.user_metadata) if hasattr(input_wave_data, "user_metadata") else {}
    }    # 如果输入波形有处理历史，也将其复制
    if "process_history" in input_wave_data.user_metadata:
        input_metadata["process_history"] = input_wave_data.user_metadata["process_history"]

    # 创建本次仿真的处理记录
    process_record = {
        "operation": "simulate_circuit_with_sweep",
        "timestamp": np.datetime64('now').astype(str),
        "parameters": {
            "circuit_type": type(circuit).__name__,
            "output_folder": str(output_folder),
            "ngspice_path": ngspice_path,
            "sample_rate": fs,
            "num_frequency_points": batch_size
        },
        "source_info": {
            "function": "simulate_circuit_with_sweep",
            "input_file_path": input_file_path or "未指定路径",
            "output_file_path": output_file_path or "未指定路径"
        },
        "circuit_info": {
            "type": type(circuit).__name__,
            "R": getattr(circuit, "R", None),
            "C": getattr(circuit, "C", None),
            "cutoff_freq": getattr(circuit, "cutoff_freq", None)
        },
        "input_wave_metadata": input_metadata
    }

    # 初始化处理记录列表，如果不存在
    if "process_history" not in wave_data.user_metadata:
        wave_data.add_user_metadata("process_history", [])

    # 添加输入波形的处理历史记录到输出波形中
    process_history = []
    if "process_history" in input_wave_data.user_metadata:
        process_history.extend(
            input_wave_data.user_metadata["process_history"])

    # 添加当前处理记录到历史列表
    process_history.append(process_record)
    wave_data.add_user_metadata("process_history", process_history)

    return wave_data


def main():
    """使用新工具函数的主函数实现，用于RC滤波器的频率响应分析"""
    # 创建输出目录
    output_dir = Path(__file__).parent / "temp"
    output_dir.mkdir(exist_ok=True)

    # 创建波形处理器
    processor = WaveProcessor()

    # 创建RC低通滤波器
    rc_filter = RCLowPassFilter(R_value=10e3, C_value=1e-5)
    cutoff_freq = rc_filter.cutoff_freq
    print(f"RC滤波器截止频率: {cutoff_freq:.2f} Hz")

    # 设置扫频范围，从截止频率的0.1倍到10倍，取10个点
    freq_min = cutoff_freq * 0.1
    freq_max = cutoff_freq * 10
    freq_range = np.logspace(np.log10(freq_min), np.log10(freq_max), 10)
    print(f"扫频范围: {freq_range} Hz")

    # 步骤1: 生成扫频输入波形
    print("1. 正在生成扫频输入波形...")
    input_wave_path = output_dir / "rc_sweep_input"
    input_wave_file = str(input_wave_path) + ".wave"
    input_wave_data = processor.generate_sweep_input_waveform(
        freq_range=freq_range,
        amplitude=1.0,
        fs=2000,
        time_length=0.1,
        min_periods=4,
        max_periods=10,
        description="RC电路测试输入扫频波形",
        output_file_path=input_wave_file
    )
    # 保存输入波形
    processor.save_waveform(str(input_wave_path), input_wave_data)
    print(f"输入波形已保存到: {input_wave_path}.wave")

    # 步骤2: 使用电路仿真生成输出波形
    print("2. 正在进行电路仿真...")
    # 可以直接使用文件路径或之前加载的 WaveData 对象
    output_wave_path = output_dir / "rc_sweep_output"
    output_wave_file = str(output_wave_path) + ".wave"
    output_wave_data = simulate_circuit_with_sweep(
        circuit=rc_filter,
        input_wave_data=str(input_wave_path),  # 使用文件路径而不是加载的对象
        output_folder=str(output_dir),
        output_file_path=output_wave_file
    )
    # 保存输出波形
    processor.save_waveform(str(output_wave_path), output_wave_data)
    print(f"输出波形已保存到: {output_wave_path}.wave")

    # 步骤3: 分析频率响应
    print("3. 正在分析频率响应...")
    # 可以直接使用文件路径或加载的 WaveData 对象
    system = processor.analyze_sweep_response(
        input_wave_data=str(input_wave_path),  # 使用文件路径
        output_wave_data=str(output_wave_path)  # 使用文件路径
    )

    # 获取频率、增益和相位数据
    frequencies = system.f
    gains = system.toabs()
    phases = system.tophase()

    # 计算理论频响
    theoretical_freqs = np.logspace(
        np.log10(freq_min/2), np.log10(freq_max*2), 100)
    theoretical_gains = []
    theoretical_phases = []

    for f in theoretical_freqs:
        # RC低通滤波器的理论增益和相位
        w = 2 * np.pi * f
        tau = rc_filter.tau
        gain = 1 / np.sqrt(1 + (w * tau) ** 2)
        phase = -np.arctan(w * tau) * 180 / np.pi  # 转换为度

        theoretical_gains.append(gain)
        theoretical_phases.append(phase)

    # 绘制频率响应图表
    plt.figure(figsize=(10, 8))

    # 增益响应
    plt.subplot(2, 1, 1)
    plt.semilogx(theoretical_freqs, 20 *
                 np.log10(theoretical_gains), 'b-', label='理论值')
    plt.semilogx(frequencies, 20*np.log10(gains), 'ro', label='SPICE仿真')
    plt.axvline(x=cutoff_freq, color='g', linestyle='--',
                label=f'截止频率 ({cutoff_freq:.2f} Hz)')
    plt.axhline(y=-3, color='k', linestyle=':', label='-3dB')
    plt.grid(True, which="both", ls="--")
    plt.xlabel('频率 (Hz)')
    plt.ylabel('增益 (dB)')
    plt.title('RC低通滤波器增益响应')
    plt.legend()

    # 相位响应
    plt.subplot(2, 1, 2)
    plt.semilogx(theoretical_freqs, theoretical_phases, 'b-', label='理论值')
    plt.semilogx(frequencies, phases, 'ro', label='SPICE仿真')
    plt.axvline(x=cutoff_freq, color='g', linestyle='--',
                label=f'截止频率 ({cutoff_freq:.2f} Hz)')
    plt.grid(True, which="both", ls="--")
    plt.xlabel('频率 (Hz)')
    plt.ylabel('相位 (度)')
    plt.title('RC低通滤波器相位响应')
    plt.legend()

    plt.tight_layout()
    plt.savefig(str(output_dir / "rc_frequency_response.png"), dpi=300)
    plt.show()

    print("程序执行完成!")


if __name__ == "__main__":
    # 使用新的工具函数运行示例
    main()
