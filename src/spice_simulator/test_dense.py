import numpy as np
import math
from simulation import CircuitSimulation
from circuit_dense import DenseCircuitFactory
import matplotlib.pyplot as plt

# 导入中文字体配置
try:
    import matplotlib_chinese_config
    print("已加载中文字体配置")
except ImportError:
    print("警告: 未找到中文字体配置文件，中文可能显示为方框")

# 使用理想运放配置
# OPAMP_CONFIG = {
#     'model': 'OPAx205A',
#     'include_file': "spice_models\OPAx205A.LIB",
# }    # 创建电路

OPAMP_CONFIG = {
    'model': 'ada4528',
    'include_file': "spice_models/ada4528.cir",
}

# OPAMP_CONFIG = None


def plot_simulation_results(t, input_signals, result, title="带符号加法器仿真结果", save_path=None):
    """
    通用的仿真结果绘图函数 - 只处理(time_steps, weights)维度格式的输入输出

    参数:
        t: 时间向量
        input_signals: 输入信号矩阵，形状为[time_steps, weights]
        result: 仿真结果字典
        title: 图表标题
        save_path: 保存图片的路径，如果为None则不保存
    """
    # 假设输入信号已经是[time_steps, weights]格式
    input_signals_plot = input_signals

    # 处理输出矩阵 - 假设已经是[time_steps, channels]格式
    v_out_numpy = result.get('v_out_numpy', [])
    if not isinstance(v_out_numpy, np.ndarray) or v_out_numpy.size == 0:
        v_out_numpy_plot = np.array([]).reshape(-1, 0)
    else:
        # 假设已经是[time_steps, channels]格式
        v_out_numpy_plot = v_out_numpy

    # 处理SPICE仿真结果 - 假设已经是[timesteps, channels]格式
    if 'v_out_spice' in result:
        if isinstance(result['v_out_spice'], dict):
            # 将字典形式转换为数组[time_steps, channels]
            channels = sorted(result['v_out_spice'].keys(
            ), key=lambda x: int(x.replace('out', '')))
            v_out_spice_plot = np.zeros((len(t), len(channels)))
            for i, ch in enumerate(channels):
                v_out_spice_plot[:, i] = result['v_out_spice'][ch]
        else:
            # 假设已经是[time_steps, channels]格式
            v_out_spice_plot = result['v_out_spice']
    else:
        v_out_spice_plot = np.array([]).reshape(-1, 0)

    # 确定输出通道数
    num_output_channels = max(v_out_numpy_plot.shape[1] if v_out_numpy_plot.size > 0 else 0,
                              v_out_spice_plot.shape[1] if v_out_spice_plot.size > 0 else 0)

    if num_output_channels == 0:
        print("警告: 没有输出通道数据，无法绘图")
        return

    # 计算子图布局 - 输入信号占一个子图，其余为输出通道
    total_subplots = num_output_channels + 1  # 所有输出通道 + 1个输入信号子图

    # 计算最佳的网格布局 (近似正方形布局)
    grid_size = math.ceil(math.sqrt(total_subplots))

    # 创建图形
    fig = plt.figure(figsize=(9, 6))
    fig.suptitle(title, fontsize=16)

    # 绘制输入信号 (所有通道叠加在一个子图中)
    ax_input = plt.subplot(grid_size, grid_size, 1)
    for i in range(input_signals_plot.shape[1]):
        ax_input.plot(t*1e3, input_signals_plot[:, i], label=f'Input {i+1}')
    ax_input.set_xlabel('Time (ms)')
    ax_input.set_ylabel('Voltage (V)')
    ax_input.grid(True)
    ax_input.legend()
    ax_input.set_title('Input Signals')

    # 绘制每个输出通道 (NumPy和SPICE结果叠加在同一个子图中)
    for ch in range(num_output_channels):
        ax_output = plt.subplot(grid_size, grid_size,
                                ch + 2)  # +2是因为第一个位置已经用于输入信号

        # 绘制NumPy结果
        if ch < v_out_numpy_plot.shape[1]:
            ax_output.plot(
                t*1e3, v_out_numpy_plot[:, ch], 'g-', label=f'NumPy')

        # 绘制SPICE结果
        if ch < v_out_spice_plot.shape[1]:
            ax_output.plot(
                t*1e3, v_out_spice_plot[:, ch], 'r--', label=f'SPICE')

        ax_output.set_xlabel('Time (ms)')
        ax_output.set_ylabel('Voltage (V)')
        ax_output.grid(True)
        ax_output.legend()
        ax_output.set_title(f'Output Channel {ch+1}')

        # 如果有差异数据，显示最大差异值
        if 'diff' in result:
            if isinstance(result['diff'], dict):
                key = f'out{ch+1}'
                if key in result['diff']:
                    max_diff = np.max(np.abs(result['diff'][key]))
                    ax_output.set_title(
                        f'Output Channel {ch+1} (Max Diff: {max_diff*1000:.2f} mV)')
            elif isinstance(result['diff'], np.ndarray) and result['diff'].ndim > 1 and ch < result['diff'].shape[1]:
                max_diff = np.max(np.abs(result['diff'][:, ch]))
                ax_output.set_title(
                    f'Output Channel {ch+1} (Max Diff: {max_diff*1000:.2f} mV)')

    plt.tight_layout()

    # 保存图形
    if save_path:
        plt.savefig(save_path, dpi=300)
        print(f"图像已保存到 {save_path}")

    # 打印数据差异信息
    if 'diff' in result:
        print("\n=== 仿真差异分析 ===")
        if isinstance(result['diff'], dict):
            for ch, diff_data in result['diff'].items():
                max_diff = np.max(np.abs(diff_data))
                print(f"通道 {ch} 最大差异: {max_diff:.6f} V ({max_diff*1000:.2f} mV)")
        elif isinstance(result['diff'], np.ndarray) and result['diff'].ndim > 1:
            for ch in range(result['diff'].shape[1]):
                max_diff = np.max(np.abs(result['diff'][:, ch]))
                print(
                    f"通道 {ch+1} 最大差异: {max_diff:.6f} V ({max_diff*1000:.2f} mV)")
        else:
            max_diff = np.max(np.abs(result['diff']))
            print(f"输出信号最大差异: {max_diff:.6f} V ({max_diff*1000:.2f} mV)")


def test_signed_adder(use_relu=False):
    """测试带符号加法器电路的功能"""

    # 创建仿真环境
    sim = CircuitSimulation(output_folder='./temp')

    # 测试参数
    t_max = 1e-1
    fs = 2e3

    # 使用直接的带符号增益矩阵创建电路（包含正负增益）
    # 形状为 (weights, channels) - 4个权重，2个输出通道
    gains = np.array([
        [1.0, -1.0],   # 第一个权重在两个通道中的增益值
        [-1.5, 0.8],   # 第二个权重在两个通道中的增益值
        [2.0, -0.5],   # 第三个权重在两个通道中的增益值
        [-0.8, 1.2]    # 第四个权重在两个通道中的增益值
    ])

    print(f"增益矩阵形状: {gains.shape}")
    print(f"增益矩阵:\n{gains}")

    relu_config = {
        'type': 'op_amp',  # 使用运放实现ReLU激活
        'gain': 1.0,       # ReLU输出增益
        'R_value': 10e3,   # ReLU电阻值
        'diode_model': '1N4148',  # 二极管型号
        'clamp_voltage': 0.0      # 钳位电压
    }  # 创建带符号加法器电路

    circuit = DenseCircuitFactory.create(
        gains=gains,
        opamp_config=OPAMP_CONFIG,
        use_e96=True,
        use_relu=use_relu,
        relu_config=relu_config
    )

    # 输出电路通道信息（用于验证）
    print(f"输入权重数量: {circuit.n_inputs}")
    print(f"输出通道数量: {circuit.n_outputs}")
    print(f"ReLU激活: {'启用' if use_relu else '禁用'}")

    # 生成测试信号
    t = np.arange(0, t_max, 1/fs)

    # 创建输入信号 - 固定使用 [time_steps, weights] 格式
    input_signals = np.zeros((len(t), circuit.n_inputs))

    # 生成不同频率的正弦波
    for i in range(circuit.n_inputs):
        freq = 1e1 * (i + 1)
        input_signals[:, i] = 0.5 * np.sin(2 * np.pi * freq * t)

    # 运行仿真
    result = sim.run_simulation_once(
        input_signals, circuit, print_netlist=False)

    # 使用通用绘图函数绘制结果
    if result:
        title = "带符号加法器电路仿真结果"
        if use_relu:
            title += " (带ReLU激活)"

        save_path = "./temp/signed_adder_result"
        if use_relu:
            save_path += "_relu"
        save_path += ".png"

        plot_simulation_results(t, input_signals, result,
                                title=title,
                                save_path=save_path)

    return result


def test_signed_adder_with_bias(use_relu=False):
    """测试带符号加法器电路的偏置功能"""

    # 创建仿真环境
    sim = CircuitSimulation(output_folder='./temp')

    # 测试参数
    t_max = 1e-1
    fs = 2e3

    # 使用直接的带符号增益矩阵创建电路（包含正负增益）
    # 形状为 (weights, channels) - 4个权重，2个输出通道
    gains = np.array([
        [1.0, -1.0],   # 第一个权重在两个通道中的增益值
        [-1.5, 0.8],   # 第二个权重在两个通道中的增益值
        [2.0, -0.5],   # 第三个权重在两个通道中的增益值
        [-0.8, 1.2]    # 第四个权重在两个通道中的增益值
    ])

    # 每个输出通道的偏置值
    biases = [0.5, -0.3]  # 第一个通道正偏置0.5V，第二个通道负偏置-0.3V

    print(f"增益矩阵形状: {gains.shape}")
    print(f"增益矩阵:\n{gains}")
    print(f"偏置值: {biases}")

    # 理想运放配置
    circuit = DenseCircuitFactory.create(
        gains=gains,
        biases=biases,  # 添加偏置值
        opamp_config=OPAMP_CONFIG,
        use_e96=True,
        use_relu=use_relu  # 添加ReLU参数
    )

    # 输出电路通道信息（用于验证）
    print(f"输入权重数量: {circuit.n_inputs}")
    print(f"输出通道数量: {circuit.n_outputs}")
    print(f"偏置功能: {'启用' if circuit.has_bias else '禁用'}")
    print(f"ReLU激活: {'启用' if use_relu else '禁用'}")

    # 生成测试信号
    t = np.arange(0, t_max, 1/fs)

    # 创建多组测试信号（每组测试与权重数量相等）
    # 1. 全零信号，用于测试纯偏置效果
    # 2. 正弦波信号，用于测试信号+偏置的综合效果

    # 测试组1：全零信号 - 固定使用 [time_steps, weights] 格式
    zero_signals = np.zeros((len(t), circuit.n_inputs))

    # 测试组2：正弦波信号 - 固定使用 [time_steps, weights] 格式
    sine_signals = np.zeros((len(t), circuit.n_inputs))
    for i in range(circuit.n_inputs):
        freq = 1e1 * (i + 1)
        sine_signals[:, i] = 0.5 * np.sin(2 * np.pi * freq * t)

    # 运行全零信号仿真（观察纯偏置效果）
    print("\n=== 运行全零信号仿真（测试纯偏置效果）===")
    zero_result = sim.run_simulation_once(
        zero_signals, circuit, print_netlist=False)

    # 使用通用绘图函数绘制零信号结果
    if zero_result:
        # 添加偏置线信息
        biases_info = f"偏置值: {biases}"
        title = f"带符号加法器电路 - 纯偏置效果 ({biases_info})"
        if use_relu:
            title += " (带ReLU激活)"

        save_path = "./temp/signed_adder_bias_zero"
        if use_relu:
            save_path += "_relu"
        save_path += ".png"

        plot_simulation_results(t, zero_signals, zero_result,
                                title=title,
                                save_path=save_path)

    # 运行正弦波信号仿真（测试信号+偏置的综合效果）
    print("\n=== 运行正弦波信号仿真（测试信号+偏置的综合效果）===")
    sine_result = sim.run_simulation_once(
        sine_signals, circuit, print_netlist=False)

    # 使用通用绘图函数绘制正弦波信号结果
    if sine_result:
        # 添加偏置线信息
        biases_info = f"偏置值: {biases}"
        title = f"带符号加法器电路 - 信号+偏置效果 ({biases_info})"
        if use_relu:
            title += " (带ReLU激活)"

        save_path = "./temp/signed_adder_bias_sine"
        if use_relu:
            save_path += "_relu"
        save_path += ".png"

        plot_simulation_results(t, sine_signals, sine_result,
                                title=title,
                                save_path=save_path)

    return zero_result, sine_result


def test_vmm_application(use_relu=False):
    """测试带符号加法器在VMM中的应用"""
    # 创建仿真环境
    sim = CircuitSimulation(output_folder='./temp')

    # 测试参数
    t_max = 2e-1
    fs = 1e3

    # VMM权重矩阵，形状为(输入数, 输出数)
    weights = np.array([
        [0.5, -0.5, 0.2],   # 第一个输入对三个输出的权重
        [-0.3, 0.7, -0.1],  # 第二个输入对三个输出的权重
        [0.8, 0.4, -0.6]    # 第三个输入对三个输出的权重
    ])

    # 注意：SignedAdderCircuit需要的增益矩阵形状为(weights, channels)
    # 因此需要对权重矩阵进行转置
    gains = weights.T  # 转置后形状为(3, 3)

    print(f"VMM权重矩阵形状: {weights.shape}")
    print(f"转置后的增益矩阵形状: {gains.shape}")
    print(f"ReLU激活: {'启用' if use_relu else '禁用'}")    # 创建带符号加法器电路
    circuit = DenseCircuitFactory.create(
        gains=gains,
        opamp_config=OPAMP_CONFIG,
        use_e96=True,
        use_relu=use_relu  # 添加ReLU参数
    )

    # 生成测试信号
    t = np.arange(0, t_max, 1/fs)

    # 创建输入信号 - 固定使用 [time_steps, weights] 格式
    input_signals = np.zeros((len(t), weights.shape[0]))

    # 生成不同频率的正弦波作为输入
    for i in range(weights.shape[0]):
        freq = 5 * (i + 1)  # 不同频率
        input_signals[:, i] = 0.8 * np.sin(2 * np.pi * freq * t)

    # 运行仿真
    result = sim.run_simulation_once(
        input_signals, circuit, print_netlist=False)

    # 使用通用绘图函数绘制结果
    if result:
        title = f"Vector-Matrix Multiplication (VMM) 应用测试"
        if use_relu:
            title += " (带ReLU激活)"

        save_path = "./temp/vmm_result"
        if use_relu:
            save_path += "_relu"
        save_path += ".png"

        plot_simulation_results(t, input_signals, result,
                                title=title,
                                save_path=save_path)

    return result


def test_batch_simulation(use_relu=False):
    """测试带符号加法器电路的批量仿真功能"""

    # 创建仿真环境
    sim = CircuitSimulation(output_folder='./temp')

    # 测试参数
    t_max = 1e-1
    fs = 2e3

    # 定义批量参数
    batch_size = 5

    # 创建增益矩阵 - 我们将为每个批次生成随机增益
    # 基础增益模板
    base_gains = np.array([
        [1.0, -1.0],   # 第一个权重在两个通道中的增益值
        [-1.5, 0.8],   # 第二个权重在两个通道中的增益值
        [2.0, -0.5],   # 第三个权重在两个通道中的增益值
        [-0.8, 1.2]    # 第四个权重在两个通道中的增益值
    ])

    # 创建电路对象列表，每个批次一个电路
    print(f"\n准备{batch_size}个批量仿真电路...")
    batch_gains = base_gains

    circuit = DenseCircuitFactory.create(
        gains=batch_gains,
        opamp_config=OPAMP_CONFIG,
        use_e96=True,
        use_relu=use_relu  # 添加ReLU参数
    )

    print(f"ReLU激活: {'启用' if use_relu else '禁用'}")

    # 生成测试信号
    t = np.arange(0, t_max, 1/fs)

    # 为每个批次创建输入信号 - 格式为 [batch_size, time_steps, weights]
    batch_signals = np.zeros((batch_size, len(t), circuit.n_inputs))

    # 为每个批次生成不同的正弦波输入信号
    for i in range(batch_size):
        for j in range(circuit.n_inputs):
            freq = 10 * (j + 1) * (1 + 0.2 * i)  # 每个批次略有不同的频率
            batch_signals[i, :, j] = 0.5 * np.sin(2 * np.pi * freq * t)

    # 运行批量仿真
    print(f"\n开始执行{batch_size}个批量仿真...")
    batch_results = sim.run_simulation(
        batch_signals,
        circuit,
        sample_rate=fs,
    )

    if not batch_results:
        print("批量仿真失败")
        return None

    # 从批处理结果中提取numpy和spice输出
    # [batch_size, time_steps, outputs]
    numpy_outputs = batch_results['numpy_outputs']
    # [batch_size, time_steps, outputs]
    spice_outputs = batch_results['spice_outputs']

    print(f"\n批量仿真结果形状:")
    print(f"numpy_outputs: {numpy_outputs.shape}")
    print(f"spice_outputs: {spice_outputs.shape}")

    # 为每个批次单独绘制结果图
    for i in range(batch_size):
        # 提取此批次的输入信号和输出结果
        input_signals = batch_signals[i]  # [time_steps, weights]
        numpy_output = numpy_outputs[i]   # [time_steps, outputs]
        spice_output = spice_outputs[i]   # [time_steps, outputs]

        # 创建结果字典
        result = {
            'v_out_numpy': numpy_output,
            'v_out_spice': spice_output,
            'diff': numpy_output - spice_output  # 计算差异
        }

        # 可以取消注释下面代码，为每个批次生成单独的图表
        # title = f"批次 {i+1} 仿真结果"
        # if use_relu:
        #     title += " (带ReLU激活)"
        #
        # save_path = f"./temp/batch_{i+1}_result"
        # if use_relu:
        #     save_path += "_relu"
        # save_path += ".png"
        #
        # plot_simulation_results(t, input_signals, result,
        #                       title=title,
        #                       save_path=save_path)

    # 将所有批次结果拼接处理，以演示如何将3D数据转为2D用于分析

    # 方法1：计算所有批次的平均值
    mean_numpy_outputs = np.mean(
        numpy_outputs, axis=0)  # [time_steps, outputs]
    mean_spice_outputs = np.mean(
        spice_outputs, axis=0)  # [time_steps, outputs]

    # 方法2：将所有批次数据在时间维度上拼接
    # 创建扩展的时间向量（每个批次时间依次延长）
    extended_t = np.concatenate([t + i*t_max for i in range(batch_size)])

    # 在时间维度上拼接所有批次的输出
    extended_numpy_outputs = np.vstack(
        [numpy_outputs[i] for i in range(batch_size)])
    extended_spice_outputs = np.vstack(
        [spice_outputs[i] for i in range(batch_size)])

    # 在时间维度上拼接所有批次的输入
    extended_input_signals = np.vstack(
        [batch_signals[i] for i in range(batch_size)])

    # 创建拼接结果的字典
    extended_result = {
        'v_out_numpy': extended_numpy_outputs,
        'v_out_spice': extended_spice_outputs,
        'diff': extended_numpy_outputs - extended_spice_outputs
    }

    # 绘制平均值结果
    mean_result = {
        'v_out_numpy': mean_numpy_outputs,
        'v_out_spice': mean_spice_outputs,
        'diff': mean_numpy_outputs - mean_spice_outputs
    }

    # 计算所有批次的平均输入信号
    mean_input_signals = np.mean(
        batch_signals, axis=0)  # [time_steps, weights]

    # 使用通用绘图函数绘制平均结果
    title = "批量仿真平均结果"
    if use_relu:
        title += " (带ReLU激活)"

    save_path = "./temp/batch_average_result"
    if use_relu:
        save_path += "_relu"
    save_path += ".png"

    plot_simulation_results(t, mean_input_signals, mean_result,
                            title=title,
                            save_path=save_path)

    # 使用通用绘图函数绘制拼接结果
    title = "批量仿真拼接结果"
    if use_relu:
        title += " (带ReLU激活)"

    save_path = "./temp/batch_extended_result"
    if use_relu:
        save_path += "_relu"
    save_path += ".png"

    plot_simulation_results(extended_t, extended_input_signals, extended_result,
                            title=title,
                            save_path=save_path)

    return batch_results


if __name__ == "__main__":
    print("=== 测试带符号加法器电路（多通道输出）- 不带ReLU ===")
    test_signed_adder(use_relu=False)

    print("=== 测试带符号加法器电路（多通道输出）- 带ReLU ===")
    test_signed_adder(use_relu=True)

    print("\n=== 测试带符号加法器电路的偏置功能 - 不带ReLU ===")
    test_signed_adder_with_bias(use_relu=False)

    print("\n=== 测试带符号加法器电路的偏置功能 - 带ReLU ===")
    test_signed_adder_with_bias(use_relu=True)

    print("\n=== 测试带符号加法器在VMM中的应用 - 不带ReLU ===")
    test_vmm_application(use_relu=False)

    print("\n=== 测试带符号加法器在VMM中的应用 - 带ReLU ===")
    test_vmm_application(use_relu=True)

    print("\n=== 测试带符号加法器电路的批量仿真功能 - 不带ReLU ===")
    test_batch_simulation(use_relu=False)

    print("\n=== 测试带符号加法器电路的批量仿真功能 - 带ReLU ===")
    test_batch_simulation(use_relu=True)

    plt.show()
