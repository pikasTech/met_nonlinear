#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
circuit_dense.py 修改示例

本文件展示如何修改 circuit_dense.py 以支持在激活函数之前添加高通滤波器
用于补偿运放偏置误差
"""

import numpy as np
from opamp_models import OpAmpModelFactory
from relu_models import ReluModelFactory
from circuit_base import BaseCircuit

class DenseCircuitWithBiasFiltering(BaseCircuit):
    """带偏置滤波功能的密集连接电路类"""
    
    def __init__(self, gains, biases=None, R_values=None, opamp_config=None,
                 use_e96=False, use_relu=False, relu_config=None, 
                 bias_compensation=None, high_pass_filter=None):
        """
        初始化带偏置滤波功能的密集连接电路
        
        新增参数:
            high_pass_filter: 高通滤波器配置字典
                enabled: bool - 是否启用高通滤波器
                cutoff_freq: float - 截止频率 (Hz)
                r_value: float - 电阻值 (Ω)，None时自动计算
                c_value: float - 电容值 (F)，None时自动计算
                bias_reference: str - 'channel' 或 'global'
                global_bias: float - 全局偏置电压 (V)
                component_prefix: str - 元件名称前缀
                apply_to_channels: list - 应用的通道列表
        """
        # 调用父类构造函数（模拟原有初始化逻辑）
        super().__init__()
        
        # ... 原有的初始化代码 ...
        self.gains = np.array(gains) if not isinstance(gains, np.ndarray) else gains
        if self.gains.ndim == 1:
            self.gains = self.gains.reshape(-1, 1)
        
        self.use_e96 = use_e96
        self.use_relu = use_relu
        self.n_inputs, self.n_outputs = self.gains.shape
        
        # 偏置处理
        if biases is None:
            self.biases = np.zeros(self.n_outputs)
            self.has_bias = False
        else:
            self.has_bias = True
            biases_array = np.array(biases) if not isinstance(biases, np.ndarray) else biases
            if np.isscalar(biases_array):
                self.biases = np.full(self.n_outputs, biases_array)
            else:
                self.biases = biases_array
        
        self.bias_compensation = bias_compensation or {}
        
        # 新增：处理高通滤波器配置
        if high_pass_filter is None:
            self.high_pass_filter = {'enabled': False}
        else:
            default_config = {
                'enabled': False,
                'cutoff_freq': 1.0,
                'r_value': None,
                'c_value': None,
                'bias_reference': 'channel',
                'global_bias': 2.5,
                'component_prefix': 'hp',
                'apply_to_channels': None
            }
            # 合并用户配置和默认配置
            self.high_pass_filter = {**default_config, **high_pass_filter}
            
            # 如果启用了滤波器但没有指定元件值，则自动计算
            if self.high_pass_filter['enabled']:
                self._calculate_high_pass_components()
        
        # ... 其他初始化代码 ...
        
    def _calculate_high_pass_components(self):
        """计算高通滤波器的RC元件值"""
        fc = self.high_pass_filter['cutoff_freq']
        
        # 如果没有指定R和C值，则自动计算
        if self.high_pass_filter['r_value'] is None and self.high_pass_filter['c_value'] is None:
            # 默认选择R=1MΩ，计算对应的C值
            r_value = 1e6
            c_value = 1 / (2 * np.pi * fc * r_value)
            
            # 转换为标准值
            if self.use_e96:
                r_value = self._convert_to_standard_value(r_value)
                c_value = self._convert_to_standard_capacitor_value(c_value)
            
            self.high_pass_filter['r_value'] = r_value
            self.high_pass_filter['c_value'] = c_value
            
        elif self.high_pass_filter['r_value'] is None:
            # 已指定C，计算R
            c_value = self.high_pass_filter['c_value']
            r_value = 1 / (2 * np.pi * fc * c_value)
            if self.use_e96:
                r_value = self._convert_to_standard_value(r_value)
            self.high_pass_filter['r_value'] = r_value
            
        elif self.high_pass_filter['c_value'] is None:
            # 已指定R，计算C
            r_value = self.high_pass_filter['r_value']
            c_value = 1 / (2 * np.pi * fc * r_value)
            if self.use_e96:
                c_value = self._convert_to_standard_capacitor_value(c_value)
            self.high_pass_filter['c_value'] = c_value
        
        # 重新计算实际截止频率
        actual_fc = 1 / (2 * np.pi * self.high_pass_filter['r_value'] * self.high_pass_filter['c_value'])
        self.high_pass_filter['actual_cutoff_freq'] = actual_fc
        
        print(f"高通滤波器参数:")
        print(f"  目标截止频率: {fc:.3f} Hz")
        print(f"  实际截止频率: {actual_fc:.3f} Hz")
        print(f"  电阻值: {self.high_pass_filter['r_value']:.0f} Ω")
        print(f"  电容值: {self.high_pass_filter['c_value']*1e6:.2f} μF")
    
    def _convert_to_standard_capacitor_value(self, value):
        """转换为标准电容值"""
        # E12系列电容值 (μF)
        e12_capacitors = np.array([1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]) * 1e-6
        
        # 找到最接近的标准值
        idx = np.argmin(np.abs(e12_capacitors - value))
        return e12_capacitors[idx]
        
    def _convert_to_standard_value(self, value):
        """转换为标准电阻值（模拟方法）"""
        # 这里应该使用实际的E96系列转换
        return value  # 简化实现
    
    def _get_high_pass_filter_netlist(self, channel_index):
        """生成高通滤波器的SPICE网表"""
        if not self.high_pass_filter['enabled']:
            return ""
        
        # 检查是否应用到此通道
        apply_channels = self.high_pass_filter['apply_to_channels']
        if apply_channels is not None and channel_index not in apply_channels:
            return ""
        
        prefix = self.high_pass_filter['component_prefix']
        r_value = self.high_pass_filter['r_value']
        c_value = self.high_pass_filter['c_value']
        
        # 确定偏置参考节点
        if self.high_pass_filter['bias_reference'] == 'channel':
            # 使用各通道的偏置值
            if self.has_bias and channel_index <= len(self.biases):
                bias_voltage = self.biases[channel_index - 1]  # channel_index从1开始
                bias_node = f"bias_ch{channel_index}"
            else:
                # 如果没有偏置，使用默认值
                bias_voltage = 0.0
                bias_node = "0"  # 接地
        else:
            # 使用全局偏置
            bias_voltage = self.high_pass_filter['global_bias']
            bias_node = "bias_global"
        
        # 输入和输出节点
        input_node = f"out{channel_index}_pre"
        output_node = f"out{channel_index}_filtered"
        
        netlist_text = f"""
* 通道{channel_index}高通滤波器 - 偏置误差补偿
* 耦合电容
C{prefix}{channel_index} {input_node} {output_node} {c_value}
* 偏置恢复电阻（连接到偏置电压）
R{prefix}{channel_index} {output_node} {bias_node} {r_value}
"""
        
        # 只有在使用非零偏置时才添加电压源
        if bias_node != "0" and bias_voltage != 0.0:
            netlist_text += f"* 偏置电压源\nV{bias_node} {bias_node} 0 DC {bias_voltage}\n"
        
        return netlist_text
    
    def _generate_channel_netlist_with_filtering(self, ch):
        """生成带滤波功能的通道网表（模拟原有方法）"""
        netlist_text = ""
        
        # ... 原有的加法器电路生成代码 ...
        # 这里仅展示关键部分
        
        # 添加运放输出（加法器输出）
        netlist_text += f"""
* 运放{ch+1}输出（含可能的偏置误差）
"""
        # 运放输出节点: out{ch+1}_pre
        
        # 新增：添加高通滤波器（如果启用）
        if self.high_pass_filter['enabled']:
            netlist_text += self._get_high_pass_filter_netlist(ch+1)
            activation_input_node = f"out{ch+1}_filtered"
        else:
            activation_input_node = f"out{ch+1}_pre"
        
        # 连接激活函数
        if self.use_relu:
            # 使用滤波后的节点作为激活函数输入
            netlist_text += f"""
* ReLU激活函数 - 输入从 {activation_input_node}
"""
            # 这里应该调用 self.relu_model.get_netlist_text(...)
        else:
            # 直接连接输出
            netlist_text += f"""
* 直接连接输出（无ReLU激活）
Rlink{ch+1} {activation_input_node} out{ch+1} 1e-6
"""
        
        return netlist_text


class DenseCircuitFactoryExtended:
    """扩展的密集连接电路工厂类"""
    
    @staticmethod
    def create_with_bias_filtering(gains, biases=None, cutoff_freq=1.0, 
                                  use_relu=True, opamp_config=None):
        """创建带偏置滤波功能的密集连接电路"""
        high_pass_config = {
            'enabled': True,
            'cutoff_freq': cutoff_freq,
            'bias_reference': 'channel'
        }
        
        return DenseCircuitWithBiasFiltering(
            gains=gains,
            biases=biases,
            opamp_config=opamp_config,
            use_relu=use_relu,
            high_pass_filter=high_pass_config
        )
    
    @staticmethod  
    def create_with_global_bias_filtering(gains, global_bias=2.5, cutoff_freq=0.1,
                                        use_relu=True, opamp_config=None):
        """创建使用全局偏置参考的滤波电路"""
        high_pass_config = {
            'enabled': True,
            'cutoff_freq': cutoff_freq,
            'bias_reference': 'global',
            'global_bias': global_bias
        }
        
        return DenseCircuitWithBiasFiltering(
            gains=gains,
            biases=None,  # 不使用通道偏置
            opamp_config=opamp_config,
            use_relu=use_relu,
            high_pass_filter=high_pass_config
        )
    
    @staticmethod
    def create_selective_filtering(gains, biases=None, filter_channels=None,
                                 cutoff_freq=1.0, use_relu=True):
        """创建选择性滤波的电路（仅对指定通道启用滤波）"""
        high_pass_config = {
            'enabled': True,
            'cutoff_freq': cutoff_freq,
            'bias_reference': 'channel',
            'apply_to_channels': filter_channels
        }
        
        return DenseCircuitWithBiasFiltering(
            gains=gains,
            biases=biases,
            use_relu=use_relu,
            high_pass_filter=high_pass_config
        )


def demonstration_example():
    """演示示例"""
    print("偏置滤波密集连接电路演示")
    print("=" * 40)
    
    # 示例参数
    gains = np.array([[1.0, -0.5], [0.8, 1.2]])
    biases = [2.5, 1.8]
    
    print(f"\n输入参数:")
    print(f"  增益矩阵: {gains}")
    print(f"  偏置值: {biases}")
    
    # 方式1：手动配置
    print("\n=== 方式1：手动配置 ===")
    high_pass_config = {
        'enabled': True,
        'cutoff_freq': 1.0,
        'bias_reference': 'channel'
    }
    
    circuit1 = DenseCircuitWithBiasFiltering(
        gains=gains,
        biases=biases,
        use_relu=True,
        use_e96=True,
        high_pass_filter=high_pass_config
    )
    
    print(f"高通滤波器配置: {circuit1.high_pass_filter}")
    
    # 方式2：使用工厂方法
    print("\n=== 方式2：工厂方法 ===")
    circuit2 = DenseCircuitFactoryExtended.create_with_bias_filtering(
        gains=gains,
        biases=biases,
        cutoff_freq=1.0,
        use_relu=True
    )
    
    # 方式3：选择性滤波
    print("\n=== 方式3：选择性滤波 ===")
    circuit3 = DenseCircuitFactoryExtended.create_selective_filtering(
        gains=gains,
        biases=biases,
        filter_channels=[1],  # 仅对通道1启用滤波
        cutoff_freq=0.5,
        use_relu=True
    )
    
    print(f"选择性滤波配置: 仅对通道{circuit3.high_pass_filter['apply_to_channels']}启用")
    
    # 生成网表示例
    print("\n=== 网表生成示例 ===")
    filter_netlist = circuit1._get_high_pass_filter_netlist(1)
    print("通道1的高通滤波器网表:")
    print(filter_netlist)


if __name__ == "__main__":
    demonstration_example()