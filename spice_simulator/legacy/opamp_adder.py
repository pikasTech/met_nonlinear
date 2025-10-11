import numpy as np
from circuit_base import BaseCircuit


class OpAmpAdderCircuit(BaseCircuit):
    """运放加法器电路类，封装电路的网表和增益等属性"""
    
    def __init__(self, n_channels, gains=None, R_values=None):
        """
        初始化运放加法器电路
        
        参数:
            n_channels: 通道数量
            gains: 各通道增益列表，默认为None（所有通道增益为1）
            R_values: 电阻基准值，默认为None（使用10kΩ作为基准值）
        """
        self.n_channels = n_channels
        
        # 处理增益
        if gains is None:
            self.gains = [1.0] * n_channels
        else:
            self.gains = gains.copy() if isinstance(gains, list) else gains
            # 扩展增益列表到n_channels
            if len(self.gains) < n_channels:
                self.gains = self.gains + [1.0] * (n_channels - len(self.gains))
        
        # 处理电阻值
        if R_values is None:
            self.R_base = 10e3  # 10kΩ作为基准电阻值
            self.RF = self.R_base
            self.R_channels = [self.R_base / gain if gain != 0 else 1e9 for gain in self.gains]
            self.R_channels = [max(R, 10) for R in self.R_channels]  # 确保最小电阻值不小于10Ω
        else:
            self.RF = R_values.get('RF', 10e3)
            self.R_channels = R_values.get('R_channels', [10e3] * n_channels)
        
        # 生成电路网表文本(不包含仿真指令)
        self.netlist_text = self._create_circuit_netlist()
    
    def _create_circuit_netlist(self):
        """
        创建多通道运放加法器电路网表(仅包含电路部分，不包含仿真指令)
        
        返回:
            str: 电路网表内容
        """
        # 创建网表文本
        netlist_text = f"""* Multi-Channel Op-Amp Adder Circuit - NGspice Simulation
* Using ideal op-amp model with {self.n_channels} input channels

* Power Supply
Vcc vcc 0 15
Vee vee 0 -15

* Define input voltage sources (will be replaced with PWL data)
"""
        
        # 添加电压源定义
        for i in range(self.n_channels):
            netlist_text += f"Vin{i+1} in{i+1} 0 0\n"
        
        netlist_text += "\n* Op-Amp adder circuit\n"
        
        # 添加输入电阻
        for i in range(self.n_channels):
            netlist_text += f"R{i+1} in{i+1} neg {self.R_channels[i]}\n"
        
        # 添加反馈电阻
        netlist_text += f"RF neg out {self.RF}\n"
        
        # 添加增强的理想运放模型
        netlist_text += """
* Enhanced ideal op-amp model
* 将正端接地，使用高增益比较反相和正相端的电压差
Eop out 0 pos neg 1e9
Rpos pos 0 1
* 添加极高阻抗的输入电阻以模拟理想运放
Rin neg pos 1e12
* 添加极小的输出电阻以增强驱动能力
Rout out 0 1e-6
"""
        return netlist_text
    
    def get_circuit_netlist(self):
        """获取电路的网表文本(不包含仿真指令)"""
        return self.netlist_text
    
    def simulate_numpy(self, t, input_signals):
        """
        使用NumPy进行运放加法器的理论仿真计算
        
        参数:
            t: 时间向量
            input_signals: 输入信号矩阵 [channels, time_steps]
            
        返回:
            np.ndarray: 输出信号
        """
        # 检查输入信号的通道数是否匹配
        if input_signals.shape[0] != self.n_channels:
            raise ValueError(f"输入信号通道数({input_signals.shape[0]})与电路通道数({self.n_channels})不匹配")
        
        # 计算理论输出（理想运放加法器）
        output = np.zeros_like(t)
        for i in range(self.n_channels):
            # 反相加法器，输出为负号
            output -= self.gains[i] * input_signals[i]
        
        return output
    
    def get_input_source_names(self):
        """
        获取输入源的名称列表
        
        返回:
            list: 输入源名称列表
        """
        return [f'Vin{i+1}' for i in range(self.n_channels)]
    
    def get_output_node_names(self):
        """
        获取输出节点名称列表
        
        返回:
            list: 输出节点名称列表
        """
        return ['out']  # 运放加法器只有一个输出节点
    
    def get_output_node_name(self):
        """
        获取输出节点名称 (兼容旧接口)
        
        返回:
            str or list: 输出节点名称或名称列表
        """
        # 使用新方法实现
        nodes = self.get_output_node_names()
        # 对于运放加法器，只有一个输出节点，返回字符串
        return nodes[0]