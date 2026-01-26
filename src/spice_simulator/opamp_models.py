"""
运放模型封装类，用于支持不同的运放模型加载
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, TypedDict, Union, List


class OpAmpConfigDict(TypedDict, total=False):
    """运放配置的类型定义"""
    model: str          # 运放模型名称
    include_file: Optional[str]  # 包含文件路径
    power_pins: bool    # 是否使用电源引脚
    params: Dict[str, Any]  # 运放参数


class OpAmpModel(ABC):
    """运放模型基类，定义了运放模型的接口"""

    @abstractmethod
    def get_netlist_text(self, instance_name: str, pos_node: str, neg_node: str, output_node: str) -> str:
        """
        获取运放模型的网表文本

        参数:
            instance_name: 运放实例名称，例如 'Xopamp1'
            pos_node: 运放同相端节点名称
            neg_node: 运放反相端节点名称
            output_node: 运放输出节点名称

        返回:
            str: 运放实例的网表文本
        """
        pass

    @abstractmethod
    def get_include_text(self) -> str:
        """
        获取运放模型的包含语句

        返回:
            str: 包含语句文本，如果无需包含文件则返回空字符串
        """
        pass


class IdealOpAmpModel(OpAmpModel):
    """理想运放模型"""

    def __init__(self, gain: float = 1e9, input_resistance: float = 1e12, output_resistance: float = 1e-6) -> None:
        """
        初始化理想运放模型

        参数:
            gain: 运放开环增益，默认为1e9
            input_resistance: 输入电阻，默认为1e12 Ω
            output_resistance: 输出电阻，默认为1e-6 Ω
        """
        self.gain: float = gain
        self.input_resistance: float = input_resistance
        self.output_resistance: float = output_resistance

    def get_netlist_text(self, instance_name: str, pos_node: str, neg_node: str, output_node: str) -> str:
        """
        获取理想运放模型的网表文本

        参数:
            instance_name: 运放实例名称，例如 'XU1'
            pos_node: 运放同相端节点名称
            neg_node: 运放反相端节点名称
            output_node: 运放输出节点名称

        返回:
            str: 理想运放实例的网表文本
        """
        # 为理想运放生成一个E元件名称(电压控制电压源)
        # 将XU1转换为EU1
        e_name = 'E' + \
            instance_name[1:] if instance_name.startswith(
                'X') else 'E' + instance_name

        return f"""
* 理想运放模型
* 使用高增益比较反相端和同相端的电压差
{e_name} {output_node} 0 {pos_node} {neg_node} {self.gain}
* 添加极高阻抗的输入电阻以模拟理想运放
Rin_{instance_name} {neg_node} {pos_node} {self.input_resistance}
* 添加极小的输出电阻以增强驱动能力
Rout_{instance_name} {output_node} 0 {self.output_resistance}
"""

    def get_include_text(self) -> str:
        """
        获取理想运放模型的包含语句

        返回:
            str: 包含语句文本，理想运放不需要包含文件
        """
        return ""


class RealOpAmpModel(OpAmpModel):
    """实际运放模型"""

    def __init__(self, model_name: str, include_file: Optional[str] = None, power_pins: bool = True, params: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化实际运放模型

        参数:
            model_name: 运放模型名称，如 'LM324', 'TL084'等
            include_file: 运放模型文件路径，包含SPICE模型
            power_pins: 是否连接电源引脚，默认为True
            params: 自定义运放模型参数字典
        """
        self.model_name: str = model_name
        self.include_file: Optional[str] = include_file
        self.power_pins: bool = power_pins
        self.params: Dict[str, Any] = {} if params is None else params

    def get_netlist_text(self, instance_name: str, pos_node: str, neg_node: str, output_node: str) -> str:
        """
        获取实际运放模型的网表文本

        参数:
            instance_name: 运放实例名称，例如 'Xopamp1'
            pos_node: 运放同相端节点名称
            neg_node: 运放反相端节点名称
            output_node: 运放输出节点名称

        返回:
            str: 实际运放实例的网表文本
        """
        params_str = ''
        for key, value in self.params.items():
            params_str += f" {key}={value}"

        if self.power_pins:
            # 包含电源引脚的运放连接
            return f"""
* 实际运放模型: {self.model_name}
{instance_name} {pos_node} {neg_node} vcc vee {output_node} {self.model_name}{params_str}
"""
        else:
            # 不包含电源引脚的运放连接
            return f"""
* 实际运放模型: {self.model_name}
{instance_name} {pos_node} {neg_node} {output_node} {self.model_name}{params_str}
"""

    def get_include_text(self) -> str:
        """
        获取实际运放模型的包含语句

        返回:
            str: 包含语句文本，如果无需包含文件则返回空字符串
        """
        if self.include_file:
            return f"\n* 包含运放模型文件\n.include {self.include_file}\n"
        return ""


class OpAmpModelFactory:
    """运放模型工厂类，用于创建不同类型的运放模型"""

    # 静态字典，存储预定义的运放模型配置
    MODEL_CONFIGS: Dict[str, Dict[str, Union[str, bool]]] = {
        'opax205a': {
            'include_file': 'spice_simulator/spice_models/OPAx205A.LIB',
            'power_pins': True,
        },
        'ad8622': {
            'include_file': 'spice_simulator/spice_models/ad8622.cir',
            'power_pins': True,
        },
        'opa1611': {
            'include_file': 'spice_simulator/spice_models/OPA1611.LIB',
            'power_pins': True,
        }
    }

    @staticmethod
    def create_model(opamp_config: Optional[Dict[str, Any]] = None) -> OpAmpModel:
        """
        创建运放模型

        参数:
            opamp_config: 运放配置字典
            可配置参数:
            - model: 指定运放模型，如'LM324', 'TL084'等，默认为'ideal'
            - include_file: 运放模型文件路径，如包含SPICE模型的文件(可选，优先使用预定义配置)
            - power_pins: 是否连接电源引脚，默认为True(可选，优先使用预定义配置)
            - params: 自定义运放模型参数字典

        返回:
            OpAmpModel: 运放模型实例
        """
        if opamp_config is None:
            # 默认使用理想运放模型
            return IdealOpAmpModel()

        # 获取模型类型
        model_type = opamp_config.get('model', 'ideal')

        if model_type.lower() == 'ideal':
            # 创建理想运放模型，可传递自定义参数
            params = opamp_config.get('params', {})
            return IdealOpAmpModel(
                gain=params.get('gain', 1e9),
                input_resistance=params.get('input_resistance', 1e12),
                output_resistance=params.get('output_resistance', 1e-6)
            )
        else:
            # 查找预定义配置
            model_key = model_type.lower()
            model_config = OpAmpModelFactory.MODEL_CONFIGS.get(model_key, {})

            # 用户提供的配置会覆盖预定义配置
            include_file = opamp_config.get(
                'include_file', model_config.get('include_file'))
            power_pins = opamp_config.get(
                'power_pins', model_config.get('power_pins', True))

            # 创建实际运放模型
            return RealOpAmpModel(
                model_name=model_type,
                include_file=include_file,
                power_pins=power_pins,
                params=opamp_config.get('params', {})
            )
