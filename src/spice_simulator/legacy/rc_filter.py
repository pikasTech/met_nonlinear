import numpy as np
from circuit_base import BaseCircuit


class RCLowPassCircuit(BaseCircuit):
    """RC低通滤波器电路类"""
    
    def __init__(self, R=10e3, C=1e-9):
        """
        初始化RC低通滤波器电路
        
        参数:
            R: 电阻值(欧姆)
            C: 电容值(法拉)
        """
        self.R = R
        self.C = C
        self.tau = R * C  # 时间常数
        
        # 生成电路网表
        self.netlist_text = self._create_circuit_netlist()
    
    def _create_circuit_netlist(self):
        """创建RC低通滤波器电路网表"""
        netlist_text = f"""* RC Low-Pass Filter Circuit - NGspice Simulation

* Input voltage source
Vin in 0 0

* RC filter components
R1 in out {self.R}
C1 out 0 {self.C}
"""
        return netlist_text
    
    def get_circuit_netlist(self):
        """获取电路的网表文本"""
        return self.netlist_text
    
    def simulate_numpy(self, t, input_signals):
        """
        使用NumPy进行RC低通滤波器的理论仿真计算
        
        参数:
            t: 时间向量
            input_signals: 输入信号矩阵 [1, time_steps] 或一维数组
            
        返回:
            np.ndarray: 输出信号
        """
        # 确保输入是单通道信号
        if input_signals.ndim > 1 and input_signals.shape[0] != 1:
            raise ValueError(f"RC低通滤波器只接受单通道输入，但收到{input_signals.shape[0]}通道")
        
        # 提取单通道信号
        if input_signals.ndim > 1:
            input_signal = input_signals[0]
        else:
            input_signal = input_signals
        
        # 计算时间步长
        dt = t[1] - t[0] if len(t) > 1 else 1e-6
        
        # 创建输出数组
        output = np.zeros_like(input_signal)
        
        # 使用数值积分模拟RC响应
        # 对于RC低通滤波器，差分方程：output[n] = alpha * output[n-1] + (1-alpha) * input[n]
        # 其中alpha = exp(-dt/tau)
        alpha = np.exp(-dt / self.tau)
        output[0] = input_signal[0]  # 初始值
        
        for i in range(1, len(t)):
            output[i] = alpha * output[i-1] + (1 - alpha) * input_signal[i]
        
        return output
    
    def get_input_source_names(self):
        """
        获取输入源的名称列表
        
        返回:
            list: 输入源名称列表
        """
        return ['Vin']  # RC滤波器只有一个输入源，名为Vin
    
    def get_output_node_names(self):
        """
        获取输出节点名称列表
        
        返回:
            list: 输出节点名称列表
        """
        return ['out']  # RC滤波器只有一个输出节点
    
    def get_output_node_name(self):
        """
        获取输出节点名称 (兼容旧接口)
        
        返回:
            str or list: 输出节点名称或名称列表
        """
        # 使用新方法实现
        nodes = self.get_output_node_names()
        # 对于RC滤波器，只有一个输出节点，返回字符串
        return nodes[0]