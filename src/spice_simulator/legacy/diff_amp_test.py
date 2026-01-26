import numpy as np
from circuit_base import BaseCircuit


class SimpleDiffAmpCircuit(BaseCircuit):
    """最简单的差分运放测试电路
    
    这个电路用于测试运放连接方式与输出相位的关系。
    包含两种配置：
    1. 正常配置：正向信号接入正向端口，负向信号接入负向端口
    2. 反转配置：正向信号接入负向端口，负向信号接入正向端口
    
    通过对比这两种配置的输出，可以确定运放连接是否导致相位反转。
    """
    
    def __init__(self, inverted=False, R_values=None):
        """
        初始化差分运放测试电路
        
        参数:
            inverted: 是否使用反转配置，默认为False
            R_values: 电阻配置字典，默认为None（使用默认配置）
        """
        # 配置类型
        self.inverted = inverted
        self.n_channels = 2  # 两个输入通道
        
        # 处理电阻值
        if R_values is None:
            # 设置默认电阻值
            self.R_in_pos = 10e3  # 正向输入电阻
            self.R_in_neg = 10e3  # 负向输入电阻
            self.R_f = 10e3      # 反馈电阻
            self.R_g = 10e3       # 接地电阻
        else:
            # 从用户提供的配置中读取电阻值
            self.R_in_pos = R_values.get('R_in_pos', 10e3)
            self.R_in_neg = R_values.get('R_in_neg', 10e3)
            self.R_f = R_values.get('R_f', 100e3)
            self.R_g = R_values.get('R_g', 10e3)
        
        # 生成电路网表文本
        self.netlist_text = self._create_circuit_netlist()
    
    def _create_circuit_netlist(self):
        """
        创建基本差分运放电路网表
        
        返回:
            str: 电路网表内容
        """
        # 创建网表文本
        netlist_text = f"""* Simple Differential Amplifier Circuit - NGspice Simulation
* 最简单的差分运放电路 - {"反转配置" if self.inverted else "正常配置"}

* Power Supply
Vcc vcc 0 15
Vee vee 0 -15

* Define input voltage sources (will be replaced with PWL data)
Vin1 in_pos 0 0  ; 正向输入信号
Vin2 in_neg 0 0  ; 负向输入信号

* Differential Amplifier Circuit
"""
        
        # 根据配置类型设置输入电阻的连接方式
        if not self.inverted:
            # 正常配置：正向信号连接到正向输入，负向信号连接到负向输入
            netlist_text += f"R_in_pos in_pos non_inv {self.R_in_pos}\n"
            netlist_text += f"R_in_neg in_neg inv {self.R_in_neg}\n"
        else:
            # 反转配置：正向信号连接到负向输入，负向信号连接到正向输入
            netlist_text += f"R_in_pos in_pos inv {self.R_in_pos}\n"
            netlist_text += f"R_in_neg in_neg non_inv {self.R_in_neg}\n"
        
        # 添加反馈电阻和接地电阻
        netlist_text += f"R_f out inv {self.R_f}\n"
        netlist_text += f"R_g non_inv 0 {self.R_g}\n"
        
        # 添加理想运放模型
        netlist_text += """
* Ideal op-amp model
* 使用高增益比较反相端和同相端的电压差
Eop out 0 non_inv inv 1e9
* 添加极高阻抗的输入电阻以模拟理想运放
Rin_op inv non_inv 1e12
* 添加极小的输出电阻以增强驱动能力
Rout out 0 1e-6
"""
        return netlist_text
    
    def get_circuit_netlist(self):
        """获取电路的网表文本(不包含仿真指令)"""
        return self.netlist_text
    
    def simulate_numpy(self, t, input_signals):
        """
        使用NumPy进行差分运放的理论仿真计算
        
        参数:
            t: 时间向量
            input_signals: 输入信号矩阵 [channels, time_steps]
            
        返回:
            np.ndarray: 输出信号
        """
        # 检查输入信号通道数
        if input_signals.shape[0] != 2:
            raise ValueError(f"输入信号通道数({input_signals.shape[0]})必须为2")
        
        # 获取正向和负向输入信号
        v_pos = input_signals[0]
        v_neg = input_signals[1]
        
        # 计算增益
        gain = self.R_f / self.R_in_pos
        
        # 根据配置计算输出
        if not self.inverted:
            # 正常配置：输出 = 增益 * (正向输入 - 负向输入)
            output = gain * (v_pos - v_neg)
        else:
            # 反转配置：输出 = 增益 * (负向输入 - 正向输入)
            output = gain * (v_neg - v_pos)
        
        return output
    
    def get_input_source_names(self):
        """
        获取输入源的名称列表
        
        返回:
            list: 输入源名称列表
        """
        return ['Vin1', 'Vin2']
    
    def get_output_node_name(self):
        """
        获取输出节点名称
        
        返回:
            str: 输出节点名称
        """
        return 'out'