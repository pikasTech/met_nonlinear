import numpy as np
from circuit_base import BaseCircuit


class ReluCircuit(BaseCircuit):
    """模拟ReLU激活函数的电路类

    这个电路通过二极管和运放实现了模拟的ReLU特性：
    - 运放同相端接地，反相端接输入电阻R
    - 运放输出和反相端之间接一个二极管D1，方向从输出到反相端
    - 二极管D2由运放输出端接到信号输出，方向由信号输出到运放输出端
    - 第二个电阻R由信号输出端接到运放反相端
    - 该电路在输入为负时输出为零，在输入为正时输出与输入成正比
    """

    def __init__(self, gain=1.0, R_value=10e3, diode_model='1N4148', opamp_config=None, use_e96=False):
        """
        初始化ReLU电路

        参数:
            gain: 输出增益，默认为1.0
            R_value: 输入和反馈电阻值，默认为10kΩ
            diode_model: 二极管模型，默认为'1N4148'
            opamp_config: 运放配置字典，默认为None（使用理想运放模型）
                可配置参数:
                - model: 指定运放模型，如'LM324', 'TL084'等，默认为'ideal'
                - include_file: 运放模型文件路径，如包含SPICE模型的文件
                - power_pins: 是否连接电源引脚，默认为True
                - params: 自定义运放模型参数字典
            use_e96: 是否使用E96标准电阻值，默认为False
        """
        self.gain = gain
        self.use_e96 = use_e96
        self.diode_model = diode_model

        # 处理电阻值
        self.R = self._convert_to_standard_value(
            R_value) if use_e96 else R_value

        # 处理运放配置
        if opamp_config is None:
            self.opamp_config = {
                'model': 'ideal',
                'include_file': None,
                'power_pins': True,
                'params': {}
            }
        else:
            # 合并默认值和用户提供的配置
            self.opamp_config = {
                'model': opamp_config.get('model', 'ideal'),
                'include_file': opamp_config.get('include_file', None),
                'power_pins': opamp_config.get('power_pins', True),
                'params': opamp_config.get('params', {})
            }

        # 生成电路网表文本(不包含仿真指令)
        self.netlist_text = self._create_circuit_netlist()

    def _create_circuit_netlist(self):
        """
        创建ReLU电路网表

        返回:
            str: 电路网表内容
        """
        # 创建网表文本
        netlist_text = f"""* ReLU Circuit - NGspice Simulation
* 模拟ReLU激活函数的电路
* 增益: {self.gain}
* 电阻值: {self.R} Ω
* 二极管模型: {self.diode_model}

* 电源定义
Vcc vcc 0 15
Vee vee 0 -15

* 输入电压源（将被PWL数据替换） 
Vin1 in 0 0

* 二极管模型
* .model {self.diode_model} D(Is=2.52n Rs=0.568 N=1.752 Cjo=4p M=0.4 tt=20n)
.model {self.diode_model} D(Is=1e-14 N=1 Rs=0 Cjo=0 tt=0)

* ReLU电路实现
* 输入电阻
Rin in inv {self.R}

* 反馈电阻
Rfb out1 inv {self.R}

* 二极管D1: 运放输出到反相端
D1 op_out inv {self.diode_model}

* 二极管D2: 输出端到运放输出
D2 out1 op_out {self.diode_model}

"""

        # 添加运放模型
        if self.opamp_config['include_file']:
            netlist_text += f"* 包含运放模型文件\n.include {self.opamp_config['include_file']}\n\n"

        # 根据运放配置添加运放模型
        if self.opamp_config['model'] == 'ideal':
            # 添加理想运放模型
            netlist_text += f"""
* 理想运放模型
* 使用高增益比较反相端和同相端的电压差
Eop op_out 0 0 inv 1e9
* 添加极高阻抗的输入电阻以模拟理想运放
Rin_op inv 0 1e12
* 添加极小的输出电阻以增强驱动能力
Rout op_out 0 1e-6
"""
        else:
            # 添加实际运放模型
            model_name = self.opamp_config['model']
            params_str = ''

            # 添加自定义参数
            for key, value in self.opamp_config['params'].items():
                params_str += f" {key}={value}"

            if self.opamp_config['power_pins']:
                # 包含电源引脚的运放连接
                netlist_text += f"""
* 实际运放模型: {model_name}
Xopamp 0 inv vcc vee op_out {model_name}{params_str}
"""
            else:
                # 不包含电源引脚的运放连接（某些模型可能不需要明确连接电源）
                netlist_text += f"""
* 实际运放模型: {model_name}
Xopamp 0 inv op_out {model_name}{params_str}
"""

        return netlist_text

    def get_circuit_netlist(self):
        """获取电路的网表文本(不包含仿真指令)"""
        return self.netlist_text

    def simulate_numpy(self, t, input_signals):
        """
        使用NumPy进行ReLU电路的理论仿真计算

        参数:
            t: 时间向量
            input_signals: 输入信号矩阵，可以是一维数组[time_steps]或二维数组[time_steps, 1]

        返回:
            np.ndarray: 输出信号，形状为[time_steps]
        """
        # 确保输入是一维数组
        if input_signals.ndim > 1:
            input_1d = input_signals.flatten()
        else:
            input_1d = input_signals

        # 反向ReLU函数并乘以增益
        output = -np.maximum(0, input_1d) * self.gain

        return output
