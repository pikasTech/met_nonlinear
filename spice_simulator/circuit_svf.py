"""
状态变量滤波器电路实现模块

该模块提供了状态变量滤波器(State Variable Filter, SVF)的实现。
SVF是一种多模式滤波器，可以同时提供高通、低通和带通输出。

基于以下网表实现电路示例：
V1 N004 0 AC 1.
R1 N001 N004 10K
R2 out3 N001 10K
R3 out1 N001 10K
R4 N002 out1 10K
R5 N003 out2 10K
C1 out2 N002 .1µ
C2 out3 N003 .1µ
R6 out2 N005 100K
R7 N005 0 10K
XU1 N001 N005 out1 opamp
XU2 N002 0 out2 opamp
XU3 N003 0 out3 opamp

主要类:
- SVFilter: 状态变量滤波器电路类

支持多 SVF 组成 SIMO 电路结构，例如 4 SVF 组成 12 个输出通道的 SVF，分别是 HP0, BP0, LP0, HP1, BP1, LP1, HP2, BP2, LP2, HP3, BP3, LP3, 对应输出 out1~out12
"""
import numpy as np
import logging
from typing import Dict, List, Union, Optional, Tuple, Any, Type, ClassVar, TypedDict, cast
from circuit_base import BaseCircuit

# 创建 logger
logger = logging.getLogger(__name__)
from opamp_models import OpAmpModelFactory, OpAmpModel, OpAmpConfigDict


class RValuesDict(TypedDict, total=False):
    """电阻值配置的类型定义"""
    R1: float      # 输入电阻 (N001 to N004)
    R2: float      # 反馈电阻 (out1 to N001)
    R3: float      # 反馈电阻 (out3 to N001)
    R4: float      # 积分器电阻 (N002 to out1)
    R5: float      # 积分器电阻 (N003 to out2)
    R6: float      # 参考电阻 (N005 to 0)
    R7: float      # Q因子控制电阻 (out2 to N005)


class SVFFilter(BaseCircuit):
    """状态变量滤波器(State Variable Filter)电路类

    该电路实现了一个基于三个运放的状态变量滤波器:
    - 可同时输出三种滤波信号：高通(out1)、带通(out2)和低通(out3)
    - 可设置滤波器的截止频率和Q因子
    - 支持不同的运放模型
    - 支持多SVF组成SIMO电路结构，例如4个SVF可提供12个输出通道
    """

    # 类变量类型标注
    R_base: ClassVar[float] = 10e3  # 基准电阻10kΩ

    # 实例变量类型标注
    use_e96: bool
    n_svf: int
    n_outputs: int
    Q: List[float]
    cutoff_freq: List[float]
    opamp_config: OpAmpConfigDict
    opamp_model: OpAmpModel
    R_values_list: List[RValuesDict]
    C_value_list: List[float]
    R_values: Optional[RValuesDict]
    C_value: Optional[float]
    netlist_text: str

    def __init__(self,
                 cutoff_freq: Union[float, List[float]] = 1000,
                 Q: Union[float, List[float]] = 1.0,
                 opamp_config: Optional[OpAmpConfigDict] = None,
                 use_e96: bool = False,
                 n_svf: int = 1,
                 power_supply_config: Optional[Dict[str, float]] = None):
        """
        初始化状态变量滤波器电路

        参数:
            cutoff_freq: 滤波器截止频率(Hz)，默认为1000Hz，
                         可以是单个值或列表(为每个SVF提供不同的截止频率)
            Q: 品质因数，控制带通滤波器的带宽，默认为1.0，
               可以是单个值或列表(为每个SVF提供不同的Q值)
            R_values: 电阻配置字典，默认为None（使用默认配置）
            opamp_config: 运放配置字典，默认为None（使用理想运放模型）
            use_e96: 是否使用E96标准电阻值，默认为False
            n_svf: SVF滤波器数量，默认为1（向后兼容模式）
            power_supply_config: 电源配置字典，包含vcc和vee电压值，默认为None（使用±15V）
        """
        self.use_e96 = use_e96
        self.n_svf = n_svf  # SVF滤波器数量
        self.n_outputs = 3 * n_svf  # 每个SVF有三个输出（高通、带通和低通）

        # 处理Q和cutoff_freq，统一转为列表形式
        # 检查Q是否为列表
        q_is_list = isinstance(Q, (list, tuple, np.ndarray))
        # 检查cutoff_freq是否为列表
        cutoff_freq_is_list = isinstance(
            cutoff_freq, (list, tuple, np.ndarray))

        # 如果其中一个是列表，确保它的长度等于n_svf
        if q_is_list:
            if len(Q) != n_svf:
                raise ValueError(f"Q参数列表长度({len(Q)})必须等于SVF数量({n_svf})")
            self.Q = list(Q)
        else:
            # 如果Q不是列表，则创建n_svf个相同值的列表
            self.Q = [Q] * n_svf

        if cutoff_freq_is_list:
            if len(cutoff_freq) != n_svf:
                raise ValueError(
                    f"cutoff_freq参数列表长度({len(cutoff_freq)})必须等于SVF数量({n_svf})")
            self.cutoff_freq = list(cutoff_freq)
        else:
            # 如果cutoff_freq不是列表，则创建n_svf个相同值的列表
            self.cutoff_freq = [cutoff_freq] * n_svf

        # 处理运放配置
        if opamp_config is None:
            self.opamp_config = {
                'model': 'ideal',
                'include_file': None,
                'power_pins': True,
                'params': {}
            }
        else:            # 合并默认值和用户提供的配置
            self.opamp_config = {
                'model': opamp_config.get('model', 'ideal'),
                'include_file': opamp_config.get('include_file', None),
                'power_pins': opamp_config.get('power_pins', True),
                'params': opamp_config.get('params', {})
            }

        # 创建运放模型
        self.opamp_model = OpAmpModelFactory.create_model(
            self.opamp_config)
        
        # 处理电源配置
        if power_supply_config is None:
            self.power_supply_config = {
                'vcc': 15.0,
                'vee': -15.0
            }
        else:
            self.power_supply_config = {
                'vcc': power_supply_config.get('vcc', 15.0),
                'vee': power_supply_config.get('vee', -15.0)
            }
        self.vcc = self.power_supply_config['vcc']
        self.vee = self.power_supply_config['vee']
        
        # 设置默认电阻电容值和电容值列表
        self.R_base = 10e3  # 基准电阻10kΩ
        self.R_values_list = []
        self.C_value_list = []

        # 为每个SVF创建电阻和电容值
        for i in range(n_svf):
            # 使用子函数计算电阻和电容值
            r_values, c_value = self._calculate_rc_values(i)

            # 添加到电阻值和电容值列表
            self.R_values_list.append(r_values)
            self.C_value_list.append(c_value)

        # 为了向后兼容，保留单一的R_values和C_value
        self.R_values = self.R_values_list[0] if n_svf > 0 else None
        self.C_value = self.C_value_list[0] if n_svf > 0 else None

        # 生成电路网表文本
        self.netlist_text = self._create_circuit_netlist()

    def _calculate_rc_values(self, svf_index: int) -> Tuple[RValuesDict, float]:
        """
        计算单个SVF的电阻和电容值

        参数:
            svf_index: SVF索引，从0开始
            R_values: 用户提供的电阻配置，如果为None则使用默认值

        返回:
            Tuple[RValuesDict, float]: 返回(电阻值字典, 电容值)
        """
        # 基础设计参数
        R_base = self.R_base    # 基准电阻值
        current_Q = self.Q[svf_index]    # 当前SVF的Q值
        current_cutoff_freq = self.cutoff_freq[svf_index]    # 当前SVF的截止频率

        # 根据公式计算增益系数 (图中公式)
        A_LP = 1.0    # 低通增益默认为-1
        A_HP = 1.0    # 高通增益默认为-1

        R1 = R_base    # 基准输入电阻
        R2 = A_LP * R1    # 低通反馈电阻
        R3 = A_HP * R1    # 高通反馈电阻

        # 计算电容值 (选择一个合适的值)
        C_base = 100e-9    # 选择100nF作为基准电容

        # 计算积分器电阻R4和R5 (假设R4 = R5 = R, C1 = C2 = C)
        # 根据公式: R = 2πf₀*√(A_HP/A_LP) / C
        # R_integrator = 1 / (2 * np.pi * current_cutoff_freq * C_base)
        R_integrator = 10e3  # 假设积分器电阻为10kΩ
        c_value = (1 / (2 * np.pi * current_cutoff_freq * R_integrator))

        R4 = R_integrator    # 积分器电阻
        R5 = R_integrator    # 积分器电阻

        # 计算R7和R6来设置Q值
        # 根据公式: A_BP = -R7 / (R1 * (1/R1 + 1/R2 + 1/R3))
        # 简化后对于Q值的计算

        # 计算分母1/(1/R1 + 1/R2 + 1/R3)
        denom_factor = 1 / (1/R1 +
                            1/R2 + 1/R3)

        # R7值可以设置为基准电阻值
        R7 = R_base

        # 根据R7计算R6 (保持增益关系)
        # R6 = R7 * \
        # np.sqrt(R2 * R3) * current_Q / denom_factor
        R6 = (3 * current_Q - 1) * R7

        A_BP = (R6 + R7) / \
            R7 / (R1 * (1/R1 + 1/R2 + 1/R3))

        logger.info(f"SVF {svf_index + 1}: A_BP = {A_BP}")

        # 如果使用E96标准电阻值，转换当前SVF的所有电阻值
        if self.use_e96:
            for key in r_values:
                r_values[key] = self._convert_to_standard_value(r_values[key])

        # 重新计算电容值，确保频率准确
        # 由于R4和R5可能已被调整为标准值，所以需要重新计算C
        # c_value = C_base

        # 计算电阻值 (根据设计公式 R2 = A_LP * R1, R3 = A_HP * R1)
        r_values = {
            'R1': R1,
            'R2': R2,
            'R3': R3,
            'R4': R4,
            'R5': R5,
            'R6': R6,
            'R7': R7,
        }

        # 返回计算结果
        return r_values, c_value

    def _convert_to_standard_value(self, value: float) -> float:
        """
        将电阻值转换为标准E96系列电阻值

        参数:
            value: 需要转换的电阻值

        返回:
            float: 最接近的E96标准电阻值
        """
        # 此方法在原代码中未定义，这里添加为占位符
        return value

    def _create_single_svf_netlist(self, svf_index: int = 0) -> str:
        """
        创建单个状态变量滤波器电路网表

        参数:
            svf_index: SVF索引，用于区分不同的SVF实例，从0开始计数

        返回:
            str: 单个SVF电路网表内容
        """
        # 计算该SVF的节点编号和输出端口
        base_index = svf_index * 3  # 每个SVF有3个输出端口
        node_offset = svf_index * 10  # 每个SVF使用10个节点编号间隔

        # 计算节点和输出端口名称
        N001 = f"N{1 + node_offset:03d}"
        N002 = f"N{2 + node_offset:03d}"
        N003 = f"N{3 + node_offset:03d}"
        N005 = f"N{5 + node_offset:03d}"

        out1 = f"out{base_index + 1}"  # 高通输出
        out2 = f"out{base_index + 2}"  # 带通输出
        out3 = f"out{base_index + 3}"  # 低通输出

        # 获取当前SVF的电阻、电容值和参数
        R_values = self.R_values_list[svf_index]
        C_value = self.C_value_list[svf_index]
        current_Q = self.Q[svf_index]
        current_cutoff_freq = self.cutoff_freq[svf_index]        # 创建当前SVF的网表文本
        svf_netlist = f"""
* SVF {svf_index + 1} 电路实现 (输出: {out1}=高通, {out2}=带通, {out3}=低通)
* 参数: 截止频率={current_cutoff_freq}Hz, Q={current_Q}
* 输入和反馈电阻
R{1 + node_offset} {N001} in {R_values['R1']}
R{2 + node_offset} {out3} {N001} {R_values['R2']}
R{3 + node_offset} {out1} {N001} {R_values['R3']}
R{4 + node_offset} {N002} {out1} {R_values['R4']}
R{5 + node_offset} {N003} {out2} {R_values['R5']}
C{1 + node_offset} {out2} {N002} {C_value}
C{2 + node_offset} {out3} {N003} {C_value}
R{6 + node_offset} {out2} {N005} {R_values['R6']}
R{7 + node_offset} {N005} 0 {R_values['R7']}

* 运放电路 - 高通、带通和低通输出
"""

        # 添加运放声明
        opamp1_name = f"XU{1 + 3*svf_index}"
        opamp2_name = f"XU{2 + 3*svf_index}"
        opamp3_name = f"XU{3 + 3*svf_index}"

        opamp1_text = self.opamp_model.get_netlist_text(
            opamp1_name,  N005, N001, out1)
        opamp2_text = self.opamp_model.get_netlist_text(
            opamp2_name,  "0", N002, out2)
        opamp3_text = self.opamp_model.get_netlist_text(
            opamp3_name,  "0", N003, out3)

        svf_netlist += f"""
* 高通滤波器运放
{opamp1_text}
* 带通滤波器运放
{opamp2_text}
* 低通滤波器运放
{opamp3_text}
"""
        return svf_netlist

    def _create_circuit_netlist(self) -> str:
        """
        创建状态变量滤波器电路网表，支持多SVF

        返回:
            str: 电路网表内容
        """
        # 创建网表文本
        netlist_text = f"""* 状态变量滤波器电路 - NGspice Simulation
* 滤波器数量: {self.n_svf}
"""

        # 添加滤波器参数信息
        for i in range(self.n_svf):
            netlist_text += f"* SVF {i+1}: 截止频率: {self.cutoff_freq[i]} Hz, Q因子: {self.Q[i]}\n"

        # 添加包含语句（如果需要）
        include_text = self.opamp_model.get_include_text()
        if include_text:
            netlist_text += include_text

        netlist_text += f"""
* Power Supply
Vcc vcc 0 {self.vcc}
Vee vee 0 {self.vee}

* 输入电压源（将被PWL数据替换）
Vin1 in 0 AC 1.
"""        # 创建所有SVF电路，使用统一的生成方法
        for i in range(self.n_svf):
            netlist_text += self._create_single_svf_netlist(i)

        return netlist_text

    def get_circuit_netlist(self) -> str:
        """
        获取电路的网表文本(不包含仿真指令)

        返回:
            str: 电路网表文本
        """
        return self.netlist_text

    def simulate_numpy(self, t: np.ndarray, input_signals: np.ndarray) -> np.ndarray:
        """
        使用NumPy进行SVF滤波器理论仿真计算

        该函数实现了SVF滤波器的时域响应计算，返回三种滤波输出

        参数:
            t: 时间向量，形状为 [time_steps]
            input_signals: 输入信号，形状可能是[time_steps]或[time_steps, n_inputs]

        返回:
            np.ndarray: 形状为[time_steps, 3*n_svf]，包含所有SVF的高通、带通和低通输出
        """
        # 处理输入信号维度，确保格式正确
        if input_signals.ndim > 1:
            # 如果是多维数组，仅使用第一个通道
            input_signal = input_signals[:, 0]
        else:
            input_signal = input_signals

        # 获取时间步长
        dt = t[1] - t[0]

        # 初始化输出信号，包含所有滤波器的输出
        outputs = np.zeros((len(t), self.n_outputs))

        # 为每个SVF滤波器计算输出
        for i in range(self.n_svf):
            # 获取当前SVF的截止频率和Q值
            current_cutoff_freq = self.cutoff_freq[i]
            current_Q = self.Q[i]

            # 角频率
            omega_0 = 2 * np.pi * current_cutoff_freq
            # 滤波器Q值
            Q = current_Q

            # 初始化当前SVF的输出信号
            out1 = np.zeros_like(input_signal)  # 高通输出
            out2 = np.zeros_like(input_signal)  # 带通输出
            out3 = np.zeros_like(input_signal)  # 低通输出

            # 使用递归滤波器算法实现SVF的时域响应
            # SVF状态变量方程的简化离散形式
            F1 = 2 * np.sin(omega_0 * dt / 2) / dt   # 频率常数
            F2 = 1 / Q                              # 阻尼常数

            # 初始状态变量
            bp_z1 = 0
            lp_z1 = 0

            # 逐点计算滤波器输出
            for j in range(len(t)):
                # 计算滤波器输出
                hp = input_signal[j] - lp_z1 - F2 * bp_z1
                bp = bp_z1 + F1 * hp * dt
                lp = lp_z1 + F1 * bp_z1 * dt

                # 保存输出
                out1[j] = -hp   # 高通输出（反相，和 spice 的行为保持一致）
                out2[j] = bp   # 带通输出
                out3[j] = -lp   # 低通输出（反相，和 spice 的行为保持一致）

                # 更新状态变量
                bp_z1 = bp
                lp_z1 = lp

            # 将当前SVF的输出保存到总输出数组中
            base_idx = i * 3
            outputs[:, base_idx] = out1      # 高通输出
            outputs[:, base_idx + 1] = out2  # 带通输出
            outputs[:, base_idx + 2] = out3  # 低通输出

        # 返回所有SVF的滤波输出
        return outputs
