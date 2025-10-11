"""
状态变量滤波器(SVF)电路测试模块

本模块包含用于测试SVF电路的函数和测试案例，测试内容包括：
1. 基本的时间域测试，输入一个正弦波，输出三种滤波信号
2. 不同频率的正弦波输入和输出对比测试
3. 频率响应测试
"""

import numpy as np
import matplotlib.pyplot as plt
from simulation import CircuitSimulation
from circuit_svf import SVFFilter
import os


# OPAMP_CONFIG = {
#     'model': 'OPAx205A',
#     'include_file': "spice_models\OPAx205A.LIB",
# }

# OPAMP_CONFIG = {
#     'model': 'opa1611',
#     'include_file': "spice_models\OPA1611.LIB",
# }

# OPAMP_CONFIG = {
#     'model': 'ada4528',
#     'include_file': "spice_models/ada4528.cir",
# }

OPAMP_CONFIG = None


def plot_svf_time_domain(t, input_signal, result, title="SVF滤波器时域仿真结果", save_path=None):
    """
    绘制SVF滤波器时域仿真结果

    参数:
        t: 时间向量
        input_signal: 输入信号，形状为[time_steps]或[time_steps, 1]
        result: 仿真结果字典，包含'HP', 'BP', 'LP'三个输出的NumPy和SPICE仿真结果
        title: 图表标题
        save_path: 保存图片的路径，如果为None则不保存
    """
    # 确保输入信号是一维数组
    if input_signal.ndim > 1:
        input_signal_1d = input_signal.flatten()
    else:
        input_signal_1d = input_signal

    # 创建图表
    fig, axs = plt.subplots(3, 1, figsize=(12, 12), sharex=True)
    fig.suptitle(title, fontsize=16)

    # 输出类型列表
    output_types = ['HP', 'BP', 'LP']
    output_names = ['高通输出', '带通输出', '低通输出']

    # 绘制每种输出类型的对比图
    for i, (output_type, output_name) in enumerate(zip(output_types, output_names)):
        ax = axs[i]

        # 绘制输入信号
        ax.plot(t, input_signal_1d, 'k-', label='输入信号', alpha=0.5)

        # 绘制NumPy理论输出
        if f'{output_type}_numpy' in result:
            numpy_output = result[f'{output_type}_numpy']
            ax.plot(t, numpy_output, 'b-', label=f'NumPy {output_name}')

        # 绘制SPICE仿真输出
        if f'{output_type}_spice' in result:
            spice_output = result[f'{output_type}_spice']
            ax.plot(t, spice_output, 'r--', label=f'SPICE {output_name}')

        # 如果有差异数据，绘制差异
        if f'{output_type}_diff' in result:
            diff = result[f'{output_type}_diff']
            ax_diff = ax.twinx()
            ax_diff.plot(t, diff, 'g-', alpha=0.5, label='差异')
            ax_diff.set_ylabel('差异', color='g')
            ax_diff.tick_params(axis='y', labelcolor='g')
            ax_diff.set_ylim([-1, 1])  # 设置差异轴的范围

        ax.set_title(f'{output_name}')
        ax.set_ylabel('电压 (V)')
        ax.grid(True)
        ax.legend(loc='upper right')

    # 设置x轴标签
    axs[-1].set_xlabel('时间 (s)')

    # 调整子图间距
    plt.tight_layout()

    # 保存图像
    if save_path:
        plt.savefig(save_path, dpi=300)


def plot_svf_frequency_sweep(frequencies, result, title="SVF滤波器频率响应", save_path=None):
    """
    绘制SVF滤波器频率响应

    参数:
        frequencies: 频率数组
        result: 仿真结果字典，包含各频率点的增益和相位数据
        title: 图表标题
        save_path: 保存图片的路径，如果为None则不保存
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    fig.suptitle(title, fontsize=16)

    # 滤波器类型
    filter_types = ['HP', 'BP', 'LP']
    filter_names = ['高通', '带通', '低通']
    colors = ['r', 'g', 'b']

    # 绘制增益响应
    for i, (ftype, fname, color) in enumerate(zip(filter_types, filter_names, colors)):
        if f'{ftype}_gain_numpy' in result:
            ax1.semilogx(
                frequencies, result[f'{ftype}_gain_numpy'], f'{color}-', label=f'NumPy {fname}')
        if f'{ftype}_gain_spice' in result:
            ax1.semilogx(
                frequencies, result[f'{ftype}_gain_spice'], f'{color}--', label=f'SPICE {fname}')

    ax1.set_title('幅频响应')
    ax1.set_ylabel('增益 (dB)')
    ax1.grid(True, which='both')
    ax1.legend(loc='best')

    # 绘制相位响应
    for i, (ftype, fname, color) in enumerate(zip(filter_types, filter_names, colors)):
        if f'{ftype}_phase_numpy' in result:
            ax2.semilogx(
                frequencies, result[f'{ftype}_phase_numpy'], f'{color}-', label=f'NumPy {fname}')
        if f'{ftype}_phase_spice' in result:
            ax2.semilogx(
                frequencies, result[f'{ftype}_phase_spice'], f'{color}--', label=f'SPICE {fname}')

    ax2.set_title('相频响应')
    ax2.set_xlabel('频率 (Hz)')
    ax2.set_ylabel('相位 (度)')
    ax2.grid(True, which='both')
    ax2.legend(loc='best')

    # 调整子图间距
    plt.tight_layout()

    # 保存图像
    if save_path:
        plt.savefig(save_path, dpi=300)


def test_svf_filter_time_domain():
    """测试SVF滤波器的时域响应"""
    print("\n==== 测试SVF滤波器时域响应 ====")

    # 创建SVF滤波器
    cutoff_freq = 10
    filter_Q = 1.0      # 标准Q值
    svf = SVFFilter(cutoff_freq=cutoff_freq, Q=filter_Q,
                    opamp_config=OPAMP_CONFIG)

    # 创建仿真对象
    sim = CircuitSimulation(output_folder='./temp')
    # 生成测试信号 - 包含多个频率成分的输入信号
    t_max = 0.5  # 10ms仿真时间
    fs = 2000

    # 创建混合频率的测试信号
    t = np.arange(0, t_max, 1/fs)
    signal = (
        0.5 * np.sin(2 * np.pi * 5 * t) +   # 100Hz 成分 (远低于截止频率)
        0.3 * np.sin(2 * np.pi * 10 * t) +  # 1kHz 成分 (等于截止频率)
        0.2 * np.sin(2 * np.pi * 100 * t)    # 5kHz 成分 (远高于截止频率)
    )

    # 运行仿真
    result = sim.run_simulation_once(signal, svf, print_netlist=False)

    # 处理结果
    output_types = ['HP', 'BP', 'LP']
    processed_results = {}

    # 提取NumPy仿真结果
    numpy_outputs = svf.simulate_numpy(t, signal)
    for output_index, output_type in enumerate(output_types):
        # 提取SPICE仿真结果
        processed_results[f'{output_type}_numpy'] = numpy_outputs[:, output_index]
    if result is not None:
        spice_outputs = result.get('v_out_spice', {})
        for output_index, output_type in enumerate(output_types):
            # 如果 v_out_spice 是数组形式
            i = output_types.index(output_type)
            processed_results[f'{output_type}_spice'] = spice_outputs[:, i]

            # 计算差异
            numpy_output = numpy_outputs[:, output_index]
            spice_output = spice_outputs[:, i]
            processed_results[f'{output_type}_diff'] = numpy_output - spice_output
    else:
        print("警告: SPICE仿真失败，只显示NumPy理论结果")

    # 绘制时域结果
    plot_svf_time_domain(
        t, signal, processed_results,
        title=f"SVF滤波器时域响应 (fc={cutoff_freq}Hz, Q={filter_Q})",
        save_path="./temp/svf_time_domain.png"
    )

    print("SVF滤波器时域测试完成，结果已保存。")
    return processed_results


def test_dual_svf_filter_time_domain():
    """测试双SVF滤波器的时域响应（6个输出通道）"""
    print("\n==== 测试双SVF滤波器时域响应 (6个输出通道) ====")

    # 创建双SVF滤波器，使用不同的截止频率
    cutoff_freq1 = 10   # 第一个SVF的截止频率
    cutoff_freq2 = 50   # 第二个SVF的截止频率
    filter_Q1 = 1.0      # 标准Q值
    filter_Q2 = 5      # 第二个SVF的Q值

    # 创建包含2个SVF的滤波器，n_svf=2表示有2个SVF
    svf = SVFFilter(cutoff_freq=[cutoff_freq1, cutoff_freq2], Q=[
        filter_Q1, filter_Q2], n_svf=2, opamp_config=OPAMP_CONFIG)

    # 创建仿真对象
    sim = CircuitSimulation(output_folder='./temp')

    # 生成测试信号 - 包含多个频率成分的输入信号
    t_max = 0.5  # 500ms仿真时间
    fs = 2000    # 采样率

    # 创建混合频率的测试信号
    t = np.arange(0, t_max, 1/fs)
    signal = (
        0.5 * np.sin(2 * np.pi * 5 * t) +     # 5Hz 成分 (远低于截止频率)
        0.3 * np.sin(2 * np.pi * 20 * t) +    # 20Hz 成分 (介于两个SVF截止频率之间)
        0.2 * np.sin(2 * np.pi * 100 * t)     # 100Hz 成分 (远高于截止频率)
    )

    # 运行仿真
    result = sim.run_simulation_once(signal, svf, print_netlist=False)

    # 处理结果
    # 6个输出通道：[HP1, BP1, LP1, HP2, BP2, LP2]
    output_types = ['HP1', 'BP1', 'LP1', 'HP2', 'BP2', 'LP2']
    output_names = ['高通1输出', '带通1输出', '低通1输出', '高通2输出', '带通2输出', '低通2输出']
    processed_results = {}

    # 提取NumPy仿真结果
    numpy_outputs = svf.simulate_numpy(t, signal)
    for i, output_type in enumerate(output_types):
        processed_results[f'{output_type}_numpy'] = numpy_outputs[:, i]

    if result is not None:
        spice_outputs = result.get('v_out_spice', {})
        for i, output_type in enumerate(output_types):
            processed_results[f'{output_type}_spice'] = spice_outputs[:, i]

            # 计算差异
            numpy_output = numpy_outputs[:, i]
            spice_output = spice_outputs[:, i]
            processed_results[f'{output_type}_diff'] = numpy_output - spice_output
    else:
        print("警告: SPICE仿真失败，只显示NumPy理论结果")

    # 创建图表来展示所有6个通道的输出
    fig, axs = plt.subplots(6, 1, figsize=(12, 18), sharex=True)
    fig.suptitle(
        f"双SVF滤波器时域响应 (fc1={cutoff_freq1}Hz, fc2={cutoff_freq2}Hz, Q1={filter_Q1}, Q2={filter_Q2})", fontsize=16)

    # 绘制每个输出通道
    for i, (output_type, output_name) in enumerate(zip(output_types, output_names)):
        ax = axs[i]

        # 绘制输入信号
        ax.plot(t, signal, 'k-', label='输入信号', alpha=0.5)

        # 绘制NumPy理论输出
        if f'{output_type}_numpy' in processed_results:
            numpy_output = processed_results[f'{output_type}_numpy']
            ax.plot(t, numpy_output, 'b-', label=f'NumPy {output_name}')

        # 绘制SPICE仿真输出
        if f'{output_type}_spice' in processed_results:
            spice_output = processed_results[f'{output_type}_spice']
            ax.plot(t, spice_output, 'r--', label=f'SPICE {output_name}')

        # 如果有差异数据，绘制差异
        if f'{output_type}_diff' in processed_results:
            diff = processed_results[f'{output_type}_diff']
            ax_diff = ax.twinx()
            ax_diff.plot(t, diff, 'g-', alpha=0.5, label='差异')
            ax_diff.set_ylabel('差异', color='g')
            ax_diff.tick_params(axis='y', labelcolor='g')
            ax_diff.set_ylim([-1, 1])  # 设置差异轴的范围

        ax.set_title(f'{output_name}')
        ax.set_ylabel('电压 (V)')
        ax.grid(True)
        ax.legend(loc='upper right')

    # 设置x轴标签
    axs[-1].set_xlabel('时间 (s)')

    # 调整子图间距
    plt.tight_layout()

    # 保存图像
    plt.savefig("./temp/dual_svf_time_domain.png", dpi=300)

    print("双SVF滤波器时域测试完成，结果已保存。")
    return processed_results


def test_svf_filter_frequency_sweep():
    """测试SVF滤波器的频率响应"""
    print("\n==== 测试SVF滤波器频率响应 ====")

    # 创建SVF滤波器
    cutoff_freq = 10  # 1kHz截止频率
    filter_Q = 1.0      # 标准Q值
    svf = SVFFilter(cutoff_freq=cutoff_freq, Q=filter_Q,
                    opamp_config=OPAMP_CONFIG)

    # 创建仿真对象
    sim = CircuitSimulation(output_folder='./temp')

    test_freqs = np.logspace(
        np.log10(0.1 * cutoff_freq), np.log10(10 * cutoff_freq), num=20)
    print(f"测试频率: {test_freqs} Hz")

    # 仿真参数设置
    t_max = 0.5  # 20ms仿真时间
    fs = 2000

    # 生成时间向量
    t = np.arange(0, t_max, 1/fs)

    # 生成多频率信号，形状为 [batch_size, time_steps, 1]
    batch_size = len(test_freqs)
    batch_signals = np.zeros((batch_size, len(t), 1))
    for i, freq in enumerate(test_freqs):
        batch_signals[i, :, 0] = np.sin(2 * np.pi * freq * t)

    # 运行批量仿真
    batch_result = sim.run_simulation(
        batch_signals,
        svf,
        sample_rate=fs)

    # 处理仿真结果
    frequencies = np.array(test_freqs)
    output_types = ['HP', 'BP', 'LP']
    processed_results = {}

    # 从批量仿真结果中提取增益和相位数据
    # [batch_size, time_steps, outputs]
    numpy_outputs = batch_result['numpy_outputs']
    # [batch_size, time_steps, outputs]
    spice_outputs = batch_result['spice_outputs']

    # 计算各频点的增益和相位
    for i, output_type in enumerate(output_types):
        # 对NumPy理论结果计算增益和相位
        numpy_gains_db = []
        numpy_phases_deg = []

        for j, freq in enumerate(test_freqs):
            # 获取特定频率和输出类型的信号
            signal = numpy_outputs[j, :, i]

            # 通过FFT分析信号幅度和相位
            n = len(signal)
            fft_result = np.fft.fft(signal)
            freqs = np.fft.fftfreq(n, 1/fs)

            # 找到最接近测试频率的频点
            idx = np.argmin(np.abs(freqs - freq))

            # 计算增益(dB)和相位(度)
            magnitude = np.abs(fft_result[idx]) * 2 / n  # 幅度
            gain_db = 20 * np.log10(magnitude + 1e-10)    # 增益(dB)，添加小量防止零值
            phase_rad = np.angle(fft_result[idx])        # 相位(弧度)
            phase_deg = np.degrees(phase_rad)            # 相位(度)

            numpy_gains_db.append(gain_db)
            numpy_phases_deg.append(phase_deg)

        processed_results[f'{output_type}_gain_numpy'] = np.array(
            numpy_gains_db)
        processed_results[f'{output_type}_phase_numpy'] = np.array(
            numpy_phases_deg)

        # 对SPICE仿真结果计算增益和相位
        spice_gains_db = []
        spice_phases_deg = []

        for j, freq in enumerate(test_freqs):
            # 获取特定频率和输出类型的信号
            signal = spice_outputs[j, :, i]

            # 通过FFT分析信号幅度和相位
            n = len(signal)
            fft_result = np.fft.fft(signal)
            freqs = np.fft.fftfreq(n, 1/fs)

            # 找到最接近测试频率的频点
            idx = np.argmin(np.abs(freqs - freq))

            # 计算增益(dB)和相位(度)
            magnitude = np.abs(fft_result[idx]) * 2 / n  # 幅度
            gain_db = 20 * np.log10(magnitude + 1e-10)    # 增益(dB)，添加小量防止零值
            phase_rad = np.angle(fft_result[idx])        # 相位(弧度)
            phase_deg = np.degrees(phase_rad)            # 相位(度)

            spice_gains_db.append(gain_db)
            spice_phases_deg.append(phase_deg)

        processed_results[f'{output_type}_gain_spice'] = np.array(
            spice_gains_db)
        processed_results[f'{output_type}_phase_spice'] = np.array(
            spice_phases_deg)

    # 绘制频率响应图
    plot_svf_frequency_sweep(
        frequencies,
        processed_results,
        title=f"SVF滤波器频率响应 (fc={cutoff_freq}Hz, Q={filter_Q})",
        save_path="./temp/svf_frequency_sweep.png"
    )

    print("SVF滤波器频率扫描测试完成，结果已保存。")
    return processed_results


if __name__ == "__main__":
    print("开始测试状态变量滤波器(SVF)电路...")

    # 确保输出目录存在
    os.makedirs("./temp", exist_ok=True)

    # 运行单SVF时域测试
    test_svf_filter_time_domain()

    # 运行双SVF时域测试
    test_dual_svf_filter_time_domain()

    # 运行频率扫描测试
    test_svf_filter_frequency_sweep()

    print("\nSVF滤波器电路测试完成！")
    plt.show()
