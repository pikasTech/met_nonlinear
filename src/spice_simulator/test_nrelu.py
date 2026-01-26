import numpy as np
import matplotlib.pyplot as plt
from simulation import CircuitSimulation
from circuit_nrelu import ReluCircuit

# OPAMP_CONFIG = {
#     'model': 'ada4528',
#     'include_file': 'spice_models/ada4528.cir'
# }

OPAMP_CONFIG = {
    'model': 'opax205a',  # 使用OPAx205A运放模型
    'include_file': 'spice_models/OPAx205A.lib',  # 包含文件路径
}

def plot_relu_results(t, input_signal, result, title="ReLU电路仿真结果", save_path=None):
    """
    绘制ReLU电路仿真结果

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
    fig, axs = plt.subplots(3, 1, figsize=(8, 10))

    # 绘制输入信号
    axs[0].plot(t*1e3, input_signal_1d, 'b-')
    axs[0].set_xlabel('时间 (ms)')
    axs[0].set_ylabel('电压 (V)')
    axs[0].grid(True)
    axs[0].set_title('输入信号')

    # 绘制输出信号
    axs[1].plot(t*1e3, v_out_numpy_1d, 'g-', label='NumPy (理想值)')
    axs[1].plot(t*1e3, v_out_spice_1d, 'r--', label='SPICE仿真')
    axs[1].set_xlabel('时间 (ms)')
    axs[1].set_ylabel('电压 (V)')
    axs[1].grid(True)
    axs[1].legend()
    axs[1].set_title('输出信号')

    # 绘制差异
    axs[2].plot(t*1e3, diff_1d*1000, 'b-')  # 显示为mV
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


def plot_io_curve(input_signal, output_signal, result=None, title="ReLU输入/输出特性曲线", save_path=None):
    """
    绘制ReLU电路的输入/输出传递特性曲线

    参数:
        input_signal: 输入信号
        output_signal: 输出信号（SPICE仿真结果）
        result: 包含NumPy仿真结果的字典（可选），用于绘制理想曲线
        title: 图表标题
        save_path: 保存图片的路径，如果为None则不保存
    """
    # 确保信号是一维数组
    if input_signal.ndim > 1:
        input_signal = input_signal.flatten()
    if output_signal.ndim > 1:
        output_signal = output_signal.flatten()

    # 对输入信号进行排序，以便绘制平滑的曲线
    sort_idx = np.argsort(input_signal)
    input_sorted = input_signal[sort_idx]
    output_sorted = output_signal[sort_idx]

    # 创建一个新图
    plt.figure(figsize=(8, 6))

    # 绘制输入/输出曲线
    plt.scatter(input_signal, output_signal, s=2, alpha=0.5, label='SPICE测量点')
    plt.plot(input_sorted, output_sorted, 'r-',
             linewidth=2, label='SPICE I/O曲线')

    # 添加理想ReLU曲线作为参考（使用NumPy仿真结果）
    if result and 'v_out_numpy' in result:
        v_out_numpy = result['v_out_numpy']
        if v_out_numpy.ndim > 1:
            v_out_numpy = v_out_numpy.flatten()

        # 对NumPy结果进行排序，以便绘制平滑的曲线
        numpy_sorted_input = input_signal[sort_idx]
        numpy_sorted_output = v_out_numpy[sort_idx]

        plt.plot(numpy_sorted_input, numpy_sorted_output,
                 'g--', linewidth=1.5, label='NumPy理想曲线')
    else:
        # 如果没有NumPy结果，则使用公式绘制理想ReLU
        x_min, x_max = input_signal.min(), input_signal.max()
        x_ref = np.linspace(x_min, x_max, 100)
        y_ref = np.maximum(0, x_ref)  # 理想ReLU函数
        plt.plot(x_ref, y_ref, 'g--', linewidth=1.5, label='理想ReLU')

    # 添加零点参考线
    plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    plt.axvline(x=0, color='k', linestyle='-', alpha=0.3)

    # 设置图表属性
    plt.xlabel('输入电压 (V)')
    plt.ylabel('输出电压 (V)')
    plt.grid(True, alpha=0.3)
    plt.title(title)
    plt.legend()

    # 保存图形
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"I/O曲线已保存到 {save_path}")


def test_relu_basic():
    """
    测试ReLU电路的基本功能，使用正弦波输入
    """
    # 创建仿真环境
    sim = CircuitSimulation(output_folder='./temp')

    # 测试参数
    t_max = 1e-2  # 10ms
    fs = 1e5      # 100kHz采样率

    # 创建ReLU电路，使用默认参数
    circuit = ReluCircuit(
        gain=1.0,          # 默认增益为1
        R_value=10e3,      # 10kΩ电阻
        diode_model='1N4148',
        opamp_config=OPAMP_CONFIG,
        use_e96=True
    )

    # 生成时间向量
    t = np.arange(0, t_max, 1/fs)

    # 生成正弦波输入信号，振幅为2V，频率为1kHz，均值为0V
    freq = 1e3
    input_signal = 2.0 * np.sin(2 * np.pi * freq * t)

    # 运行仿真
    print("\n=== 运行ReLU电路基本功能测试（正弦波输入）===")
    result = sim.run_simulation_once(input_signal, circuit, print_netlist=True)

    # 绘制结果
    if result:
        plot_relu_results(
            t,
            input_signal,
            result,
            title="ReLU电路仿真结果 - 正弦波输入",
            save_path="./temp/relu_sine_result.png"
        )

        # 绘制输入/输出特性曲线
        if 'v_out_spice' in result:
            output_signal = result['v_out_spice']
            if isinstance(output_signal, dict):
                output_signal = next(iter(output_signal.values()))
            plot_io_curve(
                input_signal,
                output_signal,
                result=result,  # 传入完整的result字典，包含NumPy仿真结果
                title="ReLU电路输入/输出特性曲线 - 正弦波输入",
                save_path="./temp/relu_io_curve_sine.png"
            )

    return result


if __name__ == "__main__":
    print("=== 测试ReLU电路的基本功能 ===")
    test_relu_basic()

    plt.show()
