"""
ReLU模型封装类，用于支持不同的ReLU实现
"""
from abc import ABC, abstractmethod


class ReluModel(ABC):
    """ReLU模型基类，定义了ReLU模型的接口"""

    @abstractmethod
    def get_netlist_text(self, channel_index, pre_output_node, output_node, diode_model):
        """
        获取ReLU模型的网表文本

        参数:
            channel_index: 输出通道索引，从1开始
            pre_output_node: ReLU输入节点名称，即ReLU激活前的节点
            output_node: ReLU输出节点名称
            diode_model: 二极管模型名称

        返回:
            str: ReLU实例的网表文本
        """
        pass

    def get_diode_model_text(self, diode_model):
        """
        获取二极管模型的网表文本

        参数:
            diode_model: 二极管模型名称

        返回:
            str: 二极管模型的网表文本，如果不需要则返回空字符串
        """
        return f"""
* 二极管模型 (用于ReLU激活)
 .model {diode_model} D(Is=2.52n Rs=0.568 N=1.752 Cjo=4p M=0.4 tt=20n)
* .model {diode_model} D(Is=1e-14 N=1 Rs=0 Cjo=0 tt=0)
"""

    @abstractmethod
    def modify_output_signals(self, output_signals, relu_config):
        """
        修改输出信号以模拟ReLU效果（用于理论计算）

        参数:
            output_signals: 原始输出信号矩阵
            relu_config: ReLU配置字典

        返回:
            np.ndarray: 应用ReLU后的输出信号矩阵
        """
        pass


class NoReluModel(ReluModel):
    """无ReLU激活模型（直接连接）"""

    def __init__(self, link_resistance=1e-6):
        """
        初始化无ReLU激活模型

        参数:
            link_resistance: 连接电阻，默认为1e-6 Ω（接近短路）
        """
        self.link_resistance = link_resistance

    def get_netlist_text(self, channel_index, pre_output_node, output_node, diode_model=None):
        """
        获取无ReLU激活的网表文本

        参数:
            channel_index: 输出通道索引，从1开始
            pre_output_node: ReLU输入节点名称，即ReLU激活前的节点
            output_node: ReLU输出节点名称
            diode_model: 二极管模型名称（不使用）

        返回:
            str: 直接连接的网表文本
        """
        return f"""
* 直接连接输出（无ReLU激活）
Rlink{channel_index} {pre_output_node} {output_node} {self.link_resistance}
"""

    def get_diode_model_text(self, diode_model):
        """无需二极管模型"""
        return ""

    def modify_output_signals(self, output_signals, relu_config):
        """无ReLU激活，输出信号保持不变"""
        return output_signals


class OpAmpReluModel(ReluModel):
    """基于运放实现的ReLU模型"""

    def __init__(self, opamp_model, r_value=10e3, gain=1.0, diode_model='D1N4148', clamp_voltage=0.0):
        """
        初始化运放ReLU模型

        参数:
            opamp_model: 运放模型实例
            r_value: 电阻值，默认为10kΩ
            gain: ReLU输出增益，默认为1.0
            diode_model: 二极管模型名称，默认为'D1N4148'
            clamp_voltage: 钳位电压，默认为0V
        """
        self.opamp_model = opamp_model
        self.r_value = r_value
        self.gain = gain
        self.default_diode_model = diode_model
        self.clamp_voltage = clamp_voltage

        # 计算反馈电阻，用于设置增益
        self.r_feedback = self.r_value * self.gain

    def get_netlist_text(self, channel_index, pre_output_node, output_node, diode_model=None):
        """
        获取基于运放实现的ReLU模型的网表文本

        参数:
            channel_index: 输出通道索引，从1开始
            pre_output_node: ReLU输入节点名称，即ReLU激活前的节点
            output_node: ReLU输出节点名称
            diode_model: 二极管模型名称，如果为None则使用默认模型

        返回:
            str: 运放ReLU实例的网表文本
        """
        # 如果未提供二极管模型，使用默认的
        if diode_model is None:
            diode_model = self.default_diode_model

        # 钳位电压处理
        clamp_node = "0"  # 默认钳位到地 (0V)
        clamp_voltage_text = ""

        # 如果钳位电压不是0V，需要创建一个电压源
        if self.clamp_voltage != 0.0:
            clamp_node = f"v_clamp_{channel_index}"
            clamp_voltage_text = f"""
* 钳位电压源
Vclamp{channel_index} {clamp_node} 0 DC {self.clamp_voltage}
"""

        # 运放ReLU实现
        netlist_text = f"""
* 通道 {channel_index} 的ReLU激活电路 (运放实现)
{clamp_voltage_text}
* 输入电阻
Rin_relu{channel_index} {pre_output_node} inv_relu{channel_index} {self.r_value}

* 反馈电阻 (增益为{self.gain})
Rfb_relu{channel_index} {output_node} inv_relu{channel_index} {self.r_feedback}

* 二极管D1: 运放输出到反相端
D1_relu{channel_index} op_out_relu{channel_index} inv_relu{channel_index} {diode_model}

* 二极管D2: 输出端到运放输出
D2_relu{channel_index} {output_node} op_out_relu{channel_index} {diode_model}
"""

        # 添加运放实例
        netlist_text += self.opamp_model.get_netlist_text(
            f"Xopamp_relu{channel_index}",
            "0",  # 同相端接地
            f"inv_relu{channel_index}",  # 反相端
            f"op_out_relu{channel_index}"  # 输出端
        )

        return netlist_text

    def modify_output_signals(self, output_signals, relu_config):
        """
        修改输出信号以模拟运放ReLU效果

        参数:
            output_signals: 原始输出信号矩阵
            relu_config: ReLU配置字典

        返回:
            np.ndarray: 应用ReLU后的输出信号矩阵
        """
        import numpy as np

        # 从配置中获取ReLU参数
        relu_gain = relu_config.get('gain', 1.0)
        clamp_voltage = relu_config.get('clamp_voltage', 0.0)

        # 运放ReLU实现是精确的钳位然后应用增益
        result = -np.maximum(clamp_voltage, output_signals) * relu_gain
        return result


class DiodeClampReluModel(ReluModel):
    """基于二极管钳位的ReLU模型"""

    def __init__(self, input_resistance=10e3, pull_resistance=100e3, diode_model='1N4148', clamp_voltage=0.0):
        """
        初始化二极管钳位ReLU模型

        参数:
            input_resistance: 输入电阻，默认为10kΩ
            pull_resistance: 下拉电阻，默认为100kΩ
            diode_model: 二极管模型名称，默认为'1N4148'
            clamp_voltage: 钳位电压，默认为0V
        """
        self.input_resistance = input_resistance
        self.pull_resistance = pull_resistance
        self.default_diode_model = diode_model
        self.clamp_voltage = clamp_voltage

    def get_netlist_text(self, channel_index, pre_output_node, output_node, diode_model=None):
        """
        获取基于二极管钳位的ReLU模型的网表文本

        参数:
            channel_index: 输出通道索引，从1开始
            pre_output_node: ReLU输入节点名称，即ReLU激活前的节点
            output_node: ReLU输出节点名称
            diode_model: 二极管模型名称，如果为None则使用默认模型

        返回:
            str: 二极管钳位ReLU实例的网表文本
        """
        # 如果未提供二极管模型，使用默认的
        if diode_model is None:
            diode_model = self.default_diode_model

        # 二极管钳位实现的ReLU (截断小于钳位电压的信号)
        clamp_node = 0  # 默认钳位到地 (0V)

        # 如果钳位电压不是0V，需要创建一个电压源
        clamp_voltage_text = ""
        if self.clamp_voltage != 0.0:
            clamp_node = f"v_clamp_{channel_index}"
            clamp_voltage_text = f"""
* 钳位电压源
Vclamp{channel_index} {clamp_node} 0 DC {self.clamp_voltage}
"""

        return f"""
* 通道 {channel_index} 的ReLU激活电路 (无源二极管钳位实现，钳位到{self.clamp_voltage}V)
* 输入电阻 - 防止短路，允许钳位发挥作用
Rin_relu{channel_index} {pre_output_node} {output_node} {self.input_resistance}
{clamp_voltage_text}
* 钳位二极管 (阳极连接到钳位电压，阴极连接到输出信号)
* 当输出信号低于钳位电压约0.7V时，二极管导通，钳位输出
Dclamp{channel_index} {clamp_node} {output_node} {diode_model}

* 添加下拉电阻以确保直流路径和稳定的钳位电平
Rpull{channel_index} {output_node} {clamp_node} {self.pull_resistance}
"""

    def modify_output_signals(self, output_signals, relu_config):
        """
        修改输出信号以模拟二极管钳位ReLU效果

        参数:
            output_signals: 原始输出信号矩阵
            relu_config: ReLU配置字典

        返回:
            np.ndarray: 应用ReLU后的输出信号矩阵
        """
        import numpy as np

        # 从配置中获取ReLU参数
        relu_gain = relu_config.get('gain', 1.0)
        clamp_voltage = relu_config.get('clamp_voltage', 0.0)

        # 二极管钳位特性 - 信号需要达到约-0.7V才会被二极管钳位
        diode_forward_drop = 0.7  # 二极管导通压降约0.7V

        # 创建结果数组的副本
        result = output_signals.copy()

        # 应用钳位效果 (实际钳位电压是clamp_voltage - 0.7)
        # 对每个低于钳位点的值应用钳位
        result[result < (clamp_voltage - diode_forward_drop)
               ] = clamp_voltage - diode_forward_drop

        # 应用增益
        result = result * relu_gain

        return result


class ReluModelFactory:
    """ReLU模型工厂类，用于创建不同类型的ReLU模型"""

    @staticmethod
    def create_model(use_relu=False, relu_config=None, opamp_model=None):
        """
        创建激活函数模型

        参数:
            use_relu: 是否启用激活函数
            relu_config: 激活函数配置字典
                可配置参数:
                - type: 激活函数实现类型，'op_amp'(运放ReLU)、'diode_clamp'(二极管钳位ReLU)或'tanh'(tanh激活)
                - gain: 激活函数输出增益
                - R_value: 激活函数电路电阻值
                - diode_model: 二极管模型（仅ReLU使用）
                - clamp_voltage: 钳位电压（仅ReLU使用）
                - opamp_config: 激活函数电路运放配置
                - scaling_factor: tanh函数缩放因子（仅tanh使用）
                - add_high_pass: 是否添加高通滤波器（仅tanh使用）
                - high_pass_cutoff: 高通滤波器截止频率（仅tanh使用）
            opamp_model: 运放模型实例，用于运放实现的激活函数

        返回:
            ReluModel: 激活函数模型实例
        """
        if not use_relu:
            return NoReluModel()

        # 使用默认配置
        if relu_config is None:
            relu_config = {}

        # 获取ReLU参数
        relu_type = relu_config.get('type', 'op_amp')
        gain = relu_config.get('gain', 1.0)
        r_value = relu_config.get('R_value', 10e3)
        diode_model = relu_config.get('diode_model', '1N4148')
        clamp_voltage = relu_config.get('clamp_voltage', 0.0)        # 根据ReLU类型创建不同的模型
        if relu_type == 'op_amp':
            # 运放实现的ReLU
            if opamp_model is None:
                # 如果没有提供运放模型，从运放配置中创建
                from opamp_models import OpAmpModelFactory
                opamp_config = relu_config.get(
                    'opamp_config', {'model': 'ideal'})
                opamp_model = OpAmpModelFactory.create_model(opamp_config)

            return OpAmpReluModel(
                opamp_model=opamp_model,
                r_value=r_value,
                gain=gain,
                diode_model=diode_model,
                clamp_voltage=clamp_voltage
            )
        elif relu_type == 'diode_clamp':
            # 二极管钳位实现的ReLU
            return DiodeClampReluModel(
                input_resistance=r_value,
                pull_resistance=r_value * 10,  # 下拉电阻通常选择较大值
                diode_model=diode_model,
                clamp_voltage=clamp_voltage
            )
        elif relu_type == 'tanh':
            # tanh激活函数实现 - 解决DC偏置问题
            if opamp_model is None:
                # 如果没有提供运放模型，从运放配置中创建
                from opamp_models import OpAmpModelFactory
                opamp_config = relu_config.get(
                    'opamp_config', {'model': 'ideal'})
                opamp_model = OpAmpModelFactory.create_model(opamp_config)

            # 导入TanhActivationModel
            from tanh_models import TanhActivationModel
            
            # 获取tanh特定的配置参数
            scaling_factor = relu_config.get('scaling_factor', 1.0)
            add_high_pass = relu_config.get('add_high_pass', True)
            high_pass_cutoff = relu_config.get('high_pass_cutoff', 1.0)
            
            return TanhActivationModel(
                opamp_model=opamp_model,
                gain=gain,
                scaling_factor=scaling_factor,
                r_base=r_value,
                add_high_pass=add_high_pass,
                high_pass_cutoff=high_pass_cutoff
            )
        else:
            # 未知类型，使用无ReLU模型
            print(f"警告：未知的激活函数类型 '{relu_type}'，使用无激活函数模型")
            return NoReluModel()
