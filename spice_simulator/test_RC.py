import numpy as np
import matplotlib.pyplot as plt
from simulation import CircuitSimulation
from circuit_RC import RCLowPassFilter


def plot_rc_filter_results(t, input_signal, result, title="RC低通滤波器仿真结果", save_path=None):
    """
    绘制RC低通滤波器仿真结果

    参数:
        t: 时间向量
        input_signal: 输入信号，形状为[time_steps]或[time_steps, 1]
        result: 仿真结果字典
        title: 图表标题
        save_path: 保存图片的路径，如果为None则不保存
    """
    # 确保输入信号是一维数组
    if input_signal.ndim > 1:
        input_signal_1d = input_signal.flatten()
    else:
        input_signal_1d = input_signal

    # 获取NumPy和SPICE仿真结果
    v_out_numpy = result.get('v_out_numpy', np.array([]))
    v_out_spice = result.get('v_out_spice', np.array([]))

    # 确保输出也是一维数组
    if v_out_numpy.ndim > 1:
        v_out_numpy_1d = v_out_numpy.flatten()
    else:
        v_out_numpy_1d = v_out_numpy

    if isinstance(v_out_spice, dict):
        # 如果是字典形式，提取第一个通道数据
        v_out_spice_1d = next(iter(v_out_spice.values()))
    elif v_out_spice.ndim > 1:
        v_out_spice_1d = v_out_spice.flatten()
    else:
        v_out_spice_1d = v_out_spice

    # 计算差异
    if 'diff' in result:
        diff = result['diff']
        if isinstance(diff, dict):
            diff_1d = next(iter(diff.values()))
        elif diff.ndim > 1:
            diff_1d = diff.flatten()
        else:
            diff_1d = diff
    else:
        diff_1d = v_out_numpy_1d - v_out_spice_1d

    # 创建图表
    fig, axs = plt.subplots(3, 1, figsize=(10, 10))

    # 绘制输入信号
    axs[0].plot(t*1000, input_signal_1d, 'b-')
    axs[0].set_xlabel('时间 (ms)')
    axs[0].set_ylabel('电压 (V)')
    axs[0].grid(True)
    axs[0].set_title('输入信号')

    # 绘制输出信号
    axs[1].plot(t*1000, v_out_numpy_1d, 'g-', label='NumPy (理想值)')
    axs[1].plot(t*1000, v_out_spice_1d, 'r--', label='SPICE仿真')
    axs[1].set_xlabel('时间 (ms)')
    axs[1].set_ylabel('电压 (V)')
    axs[1].grid(True)
    axs[1].legend()
    axs[1].set_title('输出信号')

    # 绘制差异
    axs[2].plot(t*1000, diff_1d*1000, 'b-')  # 显示为mV
    axs[2].set_xlabel('时间 (ms)')
    axs[2].set_ylabel('差异 (mV)')
    axs[2].grid(True)

    # 计算最大、平均误差和RMSE
    max_diff = np.max(np.abs(diff_1d))
    mean_diff = np.mean(np.abs(diff_1d))
    rmse = np.sqrt(np.mean(np.square(diff_1d)))

    axs[2].set_title(
        f'差异 (最大: {max_diff*1000:.2f} mV, 平均: {mean_diff*1000:.2f} mV, RMSE: {rmse*1000:.2f} mV)')

    plt.tight_layout()
    plt.suptitle(title, fontsize=16, y=1.02)

    # 保存图形
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图像已保存到 {save_path}")


def plot_rc_frequency_response(t, input_signals, result, freqs, title="RC低通滤波器频率响应", save_path=None):
    """
    绘制RC低通滤波器的频率响应

    参数:
        t: 时间向量
        input_signals: 多个频率的输入信号，形状为[time_steps, n_freqs]或[n_freqs, time_steps]
        result: 仿真结果字典
        freqs: 频率列表
        title: 图表标题
        save_path: 保存图片的路径，如果为None则不保存
    """
    # 获取频率数量
    n_freqs = len(freqs)

    # 创建图表
    fig, axs = plt.subplots(n_freqs, 1, figsize=(10, 3 * n_freqs))

    # 如果只有一个频率，将axs转换为列表以统一处理
    if n_freqs == 1:
        axs = [axs]

    # 获取输出信号
    v_out_numpy = result.get('v_out_numpy', np.array([]))
    v_out_spice = result.get('v_out_spice', np.array([]))

    # 检查输入信号的维度并进行必要的转置
    if input_signals.shape[0] == len(t) and input_signals.shape[1] == n_freqs:
        # 形状为 [time_steps, n_freqs]
        input_signals_t = input_signals
    else:
        # 假设形状为 [n_freqs, time_steps]，需要转置
        input_signals_t = input_signals.T if input_signals.ndim == 2 else input_signals

    # 对每个频率分别绘图
    for i in range(n_freqs):
        # 获取该频率的输入信号
        input_signal = input_signals_t[:,
                                       i] if input_signals_t.ndim > 1 else input_signals_t

        # 获取该频率的输出信号
        if isinstance(v_out_numpy, np.ndarray):
            if v_out_numpy.ndim == 3:  # [batch_size, time_steps, outputs]
                v_out_numpy_i = v_out_numpy[i, :, 0]
            elif v_out_numpy.ndim == 2:
                if v_out_numpy.shape[0] == n_freqs:
                    v_out_numpy_i = v_out_numpy[i]
                else:
                    v_out_numpy_i = v_out_numpy[:, i]
            else:
                v_out_numpy_i = v_out_numpy
        else:
            v_out_numpy_i = np.array([])

        if isinstance(v_out_spice, np.ndarray):
            if v_out_spice.ndim == 3:  # [batch_size, time_steps, outputs]
                v_out_spice_i = v_out_spice[i, :, 0]
            elif v_out_spice.ndim == 2:
                if v_out_spice.shape[0] == n_freqs:
                    v_out_spice_i = v_out_spice[i]
                else:
                    v_out_spice_i = v_out_spice[:, i]
            else:
                v_out_spice_i = v_out_spice
        elif isinstance(v_out_spice, dict):
            # 如果是字典形式，根据索引选择通道
            keys = list(v_out_spice.keys())
            v_out_spice_i = v_out_spice[keys[i]] if i < len(
                keys) else np.array([])
        else:
            v_out_spice_i = np.array([])

        # 绘制该频率的输入和输出信号
        axs[i].plot(t*1000, input_signal, 'b-', label='输入信号')
        axs[i].plot(t*1000, v_out_numpy_i, 'g-', label='NumPy (理想值)')
        axs[i].plot(t*1000, v_out_spice_i, 'r--', label='SPICE仿真')

        axs[i].set_xlabel('时间 (ms)')
        axs[i].set_ylabel('电压 (V)')
        axs[i].grid(True)
        axs[i].set_title(f'频率: {freqs[i]} Hz')
        axs[i].legend()

    plt.tight_layout()
    plt.suptitle(title, fontsize=16, y=1.02)

    # 保存图形
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图像已保存到 {save_path}")


def test_rc_filter():
    """测试RC低通滤波器的基本功能"""
    # 创建RC低通滤波器实例
    # 10kΩ, 0.1μF, fc ≈ 159.15 Hz
    rc_filter = RCLowPassFilter(R_value=10e3, C_value=1e-7)

    # 创建仿真实例
    sim = CircuitSimulation(output_folder='./temp')
    # 生成输入信号：100Hz正弦波
    t_max = 0.05  # 50ms
    fs = 100e3  # 100kHz采样率
    t, signals = sim.generate_sine_signals(
        t_max=t_max, fs=fs, n_outputs=1, freqs=[100])

    # 运行仿真
    result = sim.run_simulation_once(signals, rc_filter)

    # 绘制结果
    if result:
        plot_rc_filter_results(
            t,
            signals[:, 0],
            result,
            title="RC低通滤波器仿真结果 - 100Hz输入",
            save_path="./temp/rc_filter_response.png"
        )

    return result


def test_rc_filter_frequency_sweep():
    """测试RC低通滤波器在不同频率下的响应"""
    # 创建RC低通滤波器实例
    # 10kΩ, 0.1μF, fc ≈ 159.15 Hz
    rc_filter = RCLowPassFilter(R_value=10e3, C_value=1e-7)

    # 计算截止频率
    cutoff_freq = rc_filter.cutoff_freq
    print(f"RC滤波器截止频率: {cutoff_freq:.2f} Hz")

    # 创建仿真实例
    sim = CircuitSimulation(output_folder='./temp')

    # 生成不同频率的输入信号: 0.1fc, fc, 10fc
    t_max = 0.05  # 50ms
    fs = 100e3  # 100kHz采样率
    test_freqs = [0.1 * cutoff_freq, cutoff_freq, 10 * cutoff_freq]

    # 生成时间向量
    t = np.arange(0, t_max, 1/fs)

    # 生成多频率信号，形状为 [batch_size, time_steps, 1]
    batch_size = len(test_freqs)
    batch_signals = np.zeros((batch_size, len(t), 1))
    for i, freq in enumerate(test_freqs):
        batch_signals[i, :, 0] = np.sin(
            2 * np.pi * freq * t)    # 使用run_simulation函数运行批量仿真
    batch_result = sim.run_simulation(
        batch_signals,
        rc_filter,
        sample_rate=fs,
    )

    # 构造用于绘图的信号矩阵 [time_steps, batch_size]
    plot_signals = np.zeros((len(t), batch_size))
    for i in range(batch_size):
        plot_signals[:, i] = batch_signals[i, :, 0]

    # 构造单次仿真的结果格式以兼容绘图函数
    result = {
        # [batch_size, time_steps, outputs]
        'v_out_numpy': batch_result['numpy_outputs'],
        # [batch_size, time_steps, outputs]
        'v_out_spice': batch_result['spice_outputs']
    }    # 绘制不同频率的结果
    if result:
        plot_rc_frequency_response(
            t,
            plot_signals,
            result,
            freqs=test_freqs,
            title="RC低通滤波器频率响应（批量仿真）",
            save_path="./temp/rc_filter_frequency_sweep.png"
        )

    return result


if __name__ == "__main__":
    # 运行测试 - 一次只运行一个测试函数
    print("=== 测试RC低通滤波器的基本功能 ===")
    test_rc_filter()

    print("\n=== 测试RC低通滤波器在不同频率下的响应 ===")
    test_rc_filter_frequency_sweep()

    plt.show()
