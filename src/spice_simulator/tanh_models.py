"""
Tanh激活函数模型实现模块

该模块提供了基于模拟电路的tanh激活函数实现，
可以解决模拟神经网络中的DC偏置问题。

主要特点：
1. 使用双运放实现tanh激活函数
2. 对称的传递特性，天然消除DC偏置
3. 可配置的输出增益和偏移
4. 支持高通滤波器集成以进一步消除DC偏置
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from relu_models import ReluModel
from opamp_models import OpAmpModel


class TanhActivationModel(ReluModel):
    """基于双运放实现的tanh激活函数模型
    
    该模型使用两个运放实现tanh激活函数，具有以下优势：
    1. 对称的传递特性，理论上无DC偏置
    2. 平滑的激活函数，有利于梯度传播
    3. 有界输出（-1到+1），避免饱和问题
    
    电路原理：
    - 第一个运放实现指数放大
    - 第二个运放实现归一化和偏移
    - 整体实现tanh(k*x)的传递函数
    """
    
    def __init__(self, 
                 opamp_model: OpAmpModel,
                 gain: float = 1.0,
                 scaling_factor: float = 1.0,
                 r_base: float = 10e3,
                 add_high_pass: bool = True,
                 high_pass_cutoff: float = 1.0):
        """
        初始化tanh激活模型
        
        参数:
            opamp_model: 运放模型实例
            gain: 输出增益，默认为1.0
            scaling_factor: tanh函数的缩放因子k，控制激活函数的陡峭程度
            r_base: 基准电阻值，默认为10kΩ
            add_high_pass: 是否添加高通滤波器，默认为True
            high_pass_cutoff: 高通滤波器截止频率(Hz)，默认为1Hz
        """
        self.opamp_model = opamp_model
        self.gain = gain
        self.scaling_factor = scaling_factor
        self.r_base = r_base
        self.add_high_pass = add_high_pass
        self.high_pass_cutoff = high_pass_cutoff
        
        # 计算电路参数
        self._calculate_circuit_parameters()
    
    def _calculate_circuit_parameters(self):
        """计算tanh电路的电阻和电容参数"""
        # 基于tanh电路设计计算电阻值
        # 参考README_circuit.md中的tanh电路实现
        
        # 输入电阻 - 控制输入信号强度
        self.r_input = self.r_base
        
        # 反馈电阻 - 控制增益和缩放
        self.r_feedback1 = self.r_base * 2  # 第一级运放
        self.r_feedback2 = self.r_base * self.gain  # 第二级运放，控制输出增益
        
        # 缩放电阻 - 控制tanh函数的陡峭程度
        self.r_scaling = self.r_base / self.scaling_factor
        
        # 偏置电阻 - 用于设置工作点
        self.r_bias = self.r_base * 10  # 高阻值，减少偏置影响
        
        # 高通滤波器参数（如果启用）
        if self.add_high_pass:
            # 计算高通滤波器的RC参数
            # fc = 1/(2*π*R*C)
            # C = 1/(2*π*R*fc)
            self.r_hp = self.r_base
            self.c_hp = 1.0 / (2 * np.pi * self.r_hp * self.high_pass_cutoff)
    
    def get_netlist_text(self, channel_index: int, pre_output_node: str, 
                        output_node: str, diode_model: Optional[str] = None) -> str:
        """
        获取tanh激活电路的网表文本
        
        参数:
            channel_index: 输出通道索引，从1开始
            pre_output_node: 激活函数输入节点名称
            output_node: 激活函数输出节点名称
            diode_model: 二极管模型名称（tanh不需要，保持接口兼容性）
            
        返回:
            str: tanh激活电路的网表文本
        """
        # 中间节点命名
        mid_node1 = f"tanh_mid1_{channel_index}"
        mid_node2 = f"tanh_mid2_{channel_index}"
        inv_node1 = f"tanh_inv1_{channel_index}"
        inv_node2 = f"tanh_inv2_{channel_index}"
        bias_node = f"tanh_bias_{channel_index}"
        
        # 如果启用高通滤波，添加中间节点
        if self.add_high_pass:
            hp_node = f"tanh_hp_{channel_index}"
            final_output_node = hp_node
        else:
            final_output_node = output_node
        
        netlist_text = f"""
* 通道 {channel_index} 的tanh激活电路
* 基于双运放实现，具有对称传递特性，减少DC偏置

* 偏置电压源（设置工作点）
Vbias_tanh{channel_index} {bias_node} 0 DC 0

* 第一级运放 - 实现指数放大和信号调理
* 输入电阻
Rin1_tanh{channel_index} {pre_output_node} {inv_node1} {self.r_input}
* 反馈电阻
Rfb1_tanh{channel_index} {mid_node1} {inv_node1} {self.r_feedback1}
* 缩放电阻（控制tanh函数陡峭程度）
Rscale_tanh{channel_index} {bias_node} {inv_node1} {self.r_scaling}
"""
        
        # 添加第一个运放
        netlist_text += self.opamp_model.get_netlist_text(
            f"Xopamp1_tanh{channel_index}",
            bias_node,      # 同相端连接偏置
            inv_node1,      # 反相端
            mid_node1       # 输出端
        )
        
        netlist_text += f"""
* 第二级运放 - 实现归一化和输出缓冲
* 输入电阻
Rin2_tanh{channel_index} {mid_node1} {inv_node2} {self.r_base}
* 反馈电阻（控制输出增益）
Rfb2_tanh{channel_index} {final_output_node} {inv_node2} {self.r_feedback2}
* 偏置电阻
Rbias2_tanh{channel_index} {bias_node} {inv_node2} {self.r_bias}
"""
        
        # 添加第二个运放
        netlist_text += self.opamp_model.get_netlist_text(
            f"Xopamp2_tanh{channel_index}",
            bias_node,      # 同相端连接偏置
            inv_node2,      # 反相端  
            final_output_node  # 输出端
        )
        
        # 如果启用高通滤波器
        if self.add_high_pass:
            netlist_text += f"""
* 高通滤波器 - 消除DC偏置
* 耦合电容
Chp_tanh{channel_index} {hp_node} {output_node} {self.c_hp}
* 负载电阻
Rhp_tanh{channel_index} {output_node} 0 {self.r_hp}
"""
        
        return netlist_text
    
    def get_diode_model_text(self, diode_model: Optional[str] = None) -> str:
        """tanh激活不需要二极管模型"""
        return ""
    
    def modify_output_signals(self, output_signals: np.ndarray, 
                            relu_config: Dict[str, Any]) -> np.ndarray:
        """
        修改输出信号以模拟tanh效果
        
        参数:
            output_signals: 原始输出信号矩阵
            relu_config: 激活配置字典
            
        返回:
            np.ndarray: 应用tanh后的输出信号矩阵
        """
        # 从配置中获取参数
        gain = relu_config.get('gain', self.gain)
        scaling_factor = relu_config.get('scaling_factor', self.scaling_factor)
        
        # 应用tanh激活函数
        # tanh(k*x) * gain
        result = np.tanh(scaling_factor * output_signals) * gain
        
        # 如果启用高通滤波，模拟高通滤波效果
        if self.add_high_pass:
            # 简单的高通滤波近似：移除DC分量
            result = result - np.mean(result, axis=-1, keepdims=True)
        
        return result


class HighPassFilterModel:
    """高通滤波器模型类
    
    用于在tanh激活后添加高通滤波，进一步消除DC偏置
    """
    
    def __init__(self, cutoff_freq: float = 1.0, r_value: float = 10e3):
        """
        初始化高通滤波器模型
        
        参数:
            cutoff_freq: 截止频率(Hz)，默认为1Hz
            r_value: 电阻值，默认为10kΩ
        """
        self.cutoff_freq = cutoff_freq
        self.r_value = r_value
        
        # 计算电容值: C = 1/(2*π*R*fc)
        self.c_value = 1.0 / (2 * np.pi * r_value * cutoff_freq)
    
    def get_netlist_text(self, channel_index: int, input_node: str, 
                        output_node: str) -> str:
        """
        获取高通滤波器的网表文本
        
        参数:
            channel_index: 通道索引
            input_node: 输入节点
            output_node: 输出节点
            
        返回:
            str: 高通滤波器网表文本
        """
        return f"""
* 通道 {channel_index} 高通滤波器 (fc = {self.cutoff_freq} Hz)
* 用于消除DC偏置
Chp{channel_index} {input_node} {output_node} {self.c_value}
Rhp{channel_index} {output_node} 0 {self.r_value}
"""
    
    def apply_filter(self, signal: np.ndarray, sample_rate: float) -> np.ndarray:
        """
        对信号应用高通滤波
        
        参数:
            signal: 输入信号
            sample_rate: 采样率
            
        返回:
            np.ndarray: 滤波后的信号
        """
        from scipy import signal as sp_signal
        
        # 设计高通滤波器
        nyquist = sample_rate / 2
        normalized_cutoff = self.cutoff_freq / nyquist
        
        # 使用巴特沃思高通滤波器
        b, a = sp_signal.butter(1, normalized_cutoff, btype='high')
        
        # 应用滤波器
        filtered_signal = sp_signal.filtfilt(b, a, signal, axis=-1)
        
        return filtered_signal
