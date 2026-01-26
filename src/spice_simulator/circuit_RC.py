"""
这个模块实现一个简单的 RC 无源低通滤波器的 SPICE 模拟。
基于 spice_simulator.simulation.py 模块，其他的电路实现模块可以参考，例如 spice_simulator.circuit_nrelu.py 和 spice_simulator.circuit_dense.py。

随后对这个电路模块进行测试，测试代码的示例可以参考 spice_simulator/test_nrelu.py 和 spice_simulator/test_dense.py。

需要完成的测试：

1. 基本的时间域测试，输入一个正弦波，输出一个正弦波，幅值和相位延迟符合 RC 低通滤波器的特性。

2. 不同频率的正弦波输入和输出，将同一个频率的输入和输出波形绘制在一个子图里，多个频率形成多个子图，使用 matplotlib 的子图功能进行绘制。
"""
import numpy as np
from circuit_base import BaseCircuit


class RCLowPassFilter(BaseCircuit):
    """RC低通滤波器电路类

    这个电路实现了一个简单的RC低通滤波电路:
    - 由一个电阻R和一个电容C组成
    - 输入信号连接到电阻的一端，另一端与电容相连
    - 电容的另一端接地
    - 输出电压从电容两端获取
    """

    def __init__(self, R_value=10e3, C_value=1e-7, use_e96=False):
        """
        初始化RC低通滤波器电路

        参数:
            R_value: 电阻值，默认为10kΩ
            C_value: 电容值，默认为0.1μF
            use_e96: 是否使用E96标准电阻值，默认为False
        """
        self.use_e96 = use_e96

        # 处理电阻值
        self.R = self._convert_to_standard_value(
            R_value) if use_e96 else R_value
        self.C = C_value

        # 计算时间常数和截止频率
        self.tau = self.R * self.C
        self.cutoff_freq = 1 / (2 * np.pi * self.tau)

        # 生成电路网表文本(不包含仿真指令)
        self.netlist_text = self._create_circuit_netlist()

    def _create_circuit_netlist(self):
        """
        创建RC低通滤波器电路网表

        返回:
            str: 电路网表内容
        """
        # 创建网表文本
        netlist_text = f"""* RC Low-Pass Filter Circuit - NGspice Simulation
* 简单的RC低通滤波器电路
* 电阻值: {self.R} Ω
* 电容值: {self.C} F
* 时间常数: {self.tau} s
* 截止频率: {self.cutoff_freq} Hz

* 输入电压源（将被PWL数据替换）
Vin1 in 0 0

* RC低通滤波电路实现
* 输入电阻
R1 in out1 {self.R}

* 电容
C1 out1 0 {self.C}

"""
        return netlist_text

    def get_circuit_netlist(self):
        """获取电路的网表文本(不包含仿真指令)"""
        return self.netlist_text

    def simulate_numpy(self, t, input_signals):
        """
        使用NumPy进行理论仿真计算

        该函数实现了RC低通滤波器的时域响应计算

        参数:
            t: 时间向量
            input_signals: 输入信号，形状可能是[time_steps]或[time_steps, n_inputs]

        返回:
            np.ndarray: 输出信号，与输入信号维度保持一致
        """
        # 处理输入信号维度，确保格式正确
        if input_signals.ndim == 1:
            # 一维数组，形状为[time_steps]
            input_1d = input_signals
            output_1d = True
        else:
            # 二维数组，形状为[time_steps, n_inputs]
            # 转置为[n_inputs, time_steps]以便处理
            input_1d = input_signals.T
            output_1d = False

        n_inputs = 1 if input_signals.ndim == 1 else input_signals.shape[1]
        time_steps = len(t)
        dt = t[1] - t[0]  # 时间步长

        # 初始化输出信号
        if output_1d:
            output = np.zeros_like(input_1d)
        else:
            output = np.zeros_like(input_1d)

        # 对每个输入通道进行处理
        for i in range(n_inputs):
            # 获取当前通道的输入信号
            current_input = input_1d[i] if not output_1d else input_1d
            current_output = np.zeros_like(current_input)

            # 使用一阶差分方程模拟RC滤波器响应
            # v_out[n] = exp(-dt/tau) * v_out[n-1] + (1 - exp(-dt/tau)) * v_in[n]
            exp_factor = np.exp(-dt / self.tau)

            for n in range(1, time_steps):
                current_output[n] = exp_factor * current_output[n -
                                                                1] + (1 - exp_factor) * current_input[n]

            # 保存当前通道输出
            if output_1d:
                output = current_output
            else:
                output[i] = current_output

        # 返回与输入格式一致的输出
        return output if output_1d else output.T
