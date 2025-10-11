# circuit_dense.py 具体修改实施指南

## 1. 修改步骤概览

本指南将指导您逐步修改 `circuit_dense.py` 以支持在激活函数之前添加高通滤波器。

**关键修改点：**
1. 扩展构造函数参数
2. 添加高通滤波器配置处理
3. 实现元件计算方法
4. 实现网表生成方法
5. 修改主电路生成逻辑
6. 添加工厂方法

## 2. 具体修改步骤

### 步骤1：修改构造函数签名

**位置：** 第29-30行

```python
# 原代码
def __init__(self, gains, biases=None, R_values=None, opamp_config=None,
             use_e96=False, use_relu=False, relu_config=None, bias_compensation=None):

# 修改为
def __init__(self, gains, biases=None, R_values=None, opamp_config=None,
             use_e96=False, use_relu=False, relu_config=None, 
             bias_compensation=None, high_pass_filter=None):
```

### 步骤2：添加高通滤波器配置初始化

**位置：** 第93行后（`self.bias_compensation = bias_compensation or {}`之后）

```python
# 在第93行后添加
# 处理高通滤波器配置
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
```

### 步骤3：添加元件计算方法

**位置：** 在类中添加新方法（建议在 `_convert_to_standard_value` 方法附近）

```python
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

def _convert_to_standard_capacitor_value(self, value):
    """转换为标准电容值（E12系列）"""
    # E12系列电容值 (μF)
    e12_capacitors = np.array([1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]) * 1e-6
    
    # 找到最接近的标准值
    idx = np.argmin(np.abs(e12_capacitors - value))
    return e12_capacitors[idx]
```

### 步骤4：添加高通滤波器网表生成方法

**位置：** 继续在类中添加

```python
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
```

### 步骤5：修改主电路生成逻辑

**位置：** 第431-443行（在加法器电路生成后，激活函数连接之前）

**原代码：**
```python
# 添加ReLU激活电路
if self.use_relu:
    netlist_text += self.relu_model.get_netlist_text(
        ch+1,
        f"out{ch+1}_pre",
        f"out{ch+1}",
        self.relu_config['diode_model']
    )
else:
    # 如果不使用ReLU，直接连接输出
    netlist_text += f"""
* 直接连接输出（无ReLU激活）
Rlink{ch+1} out{ch+1}_pre out{ch+1} 1e-6
"""
```

**修改为：**
```python
# 添加高通滤波器（如果启用）
if self.high_pass_filter['enabled']:
    netlist_text += self._get_high_pass_filter_netlist(ch+1)
    activation_input_node = f"out{ch+1}_filtered"
else:
    activation_input_node = f"out{ch+1}_pre"

# 添加ReLU激活电路
if self.use_relu:
    netlist_text += self.relu_model.get_netlist_text(
        ch+1,
        activation_input_node,  # 使用滤波后的节点
        f"out{ch+1}",
        self.relu_config['diode_model']
    )
else:
    # 如果不使用ReLU，直接连接输出
    netlist_text += f"""
* 直接连接输出（无ReLU激活）
Rlink{ch+1} {activation_input_node} out{ch+1} 1e-6
"""
```

### 步骤6：扩展DenseCircuitFactory类

**位置：** 在 `DenseCircuitFactory` 类的末尾添加新方法

```python
@staticmethod
def create_with_bias_filtering(gains, biases=None, cutoff_freq=1.0, 
                              use_relu=True, opamp_config=None, use_e96=False):
    """创建带偏置滤波功能的密集连接电路"""
    high_pass_config = {
        'enabled': True,
        'cutoff_freq': cutoff_freq,
        'bias_reference': 'channel'
    }
    
    return DenseCircuit(
        gains=gains,
        biases=biases,
        opamp_config=opamp_config,
        use_relu=use_relu,
        use_e96=use_e96,
        high_pass_filter=high_pass_config
    )

@staticmethod  
def create_with_global_bias_filtering(gains, global_bias=2.5, cutoff_freq=0.1,
                                    use_relu=True, opamp_config=None, use_e96=False):
    """创建使用全局偏置参考的滤波电路"""
    high_pass_config = {
        'enabled': True,
        'cutoff_freq': cutoff_freq,
        'bias_reference': 'global',
        'global_bias': global_bias
    }
    
    return DenseCircuit(
        gains=gains,
        biases=None,  # 不使用通道偏置
        opamp_config=opamp_config,
        use_relu=use_relu,
        use_e96=use_e96,
        high_pass_filter=high_pass_config
    )
```

## 3. 验证步骤

### 3.1 创建测试脚本

在 `spice_simulator/` 目录下创建 `test_bias_filtering.py`：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""偏置滤波功能测试脚本"""

import numpy as np
from circuit_dense import DenseCircuitFactory

def test_bias_filtering():
    """Tests bias filtering functionality"""
    gains = np.array([[1.0, -0.5], [0.8, 1.2]])
    biases = [2.5, 1.8]
    
    # 测试基本功能
    circuit = DenseCircuitFactory.create_with_bias_filtering(
        gains=gains,
        biases=biases,
        cutoff_freq=1.0,
        use_relu=True
    )
    
    print(f"高通滤波器配置: {circuit.high_pass_filter}")
    
    # 生成网表
    netlist = circuit.get_circuit_netlist()
    print(f"\n网表片段:")
    print(netlist[:500])  # 显示前500个字符
    
    # 检查高通滤波器网表
    filter_netlist = circuit._get_high_pass_filter_netlist(1)
    print(f"\n通道1高通滤波器网表:")
    print(filter_netlist)

if __name__ == "__main__":
    test_bias_filtering()
```

### 3.2 运行测试

```bash
cd /path/to/spice_simulator
python test_bias_filtering.py
```

### 3.3 检查结果

确认以下内容：
1. 高通滤波器配置正确输出
2. 网表中包含高通滤波器元件
3. 节点连接关系正确
4. 元件值计算正确

## 4. 使用示例

### 4.1 基本使用

```python
from circuit_dense import DenseCircuitFactory
import numpy as np

# 定义电路参数
gains = np.array([[1.0, -0.5], [0.8, 1.2]])
biases = [2.5, 1.8]

# 创建带偏置滤波的电路
circuit = DenseCircuitFactory.create_with_bias_filtering(
    gains=gains,
    biases=biases,
    cutoff_freq=1.0,  # 1Hz截止频率
    use_relu=True
)

# 生成网表
netlist = circuit.get_circuit_netlist()
print(netlist)
```

### 4.2 高级配置

```python
# 手动配置高通滤波器
high_pass_config = {
    'enabled': True,
    'cutoff_freq': 0.1,
    'r_value': 1e6,              # 手动指定1MΩ
    'c_value': None,             # 自动计算电容
    'bias_reference': 'channel',
    'apply_to_channels': [1, 2], # 仅应用于通道1和2
    'component_prefix': 'filter'
}

circuit = DenseCircuit(
    gains=gains,
    biases=biases,
    use_relu=True,
    use_e96=True,  # 使用标准元件值
    high_pass_filter=high_pass_config
)
```

## 5. 注意事项

### 5.1 兼容性
- 修改保持向后兼容性，现有代码无需修改
- 默认情况下高通滤波器禁用，不影响原有功能

### 5.2 性能影响
- 高通滤波器仅在启用时才会添加至网表
- 元件计算仅在初始化时执行一次

### 5.3 验证建议
- 修改后运行现有的测试用例确保无回归
- 使用SPICE仿真验证滤波器效果
- 检查频率响应和直流偏置补偿效果

## 6. 故障排除

### 6.1 常见问题

**Q: 网表生成失败**
A: 检查 high_pass_filter 配置是否正确，确保 enabled=True

**Q: 元件值计算错误**
A: 检查 cutoff_freq 是否为正数，且在合理范围内

**Q: ReLU激活失效**
A: 确认 activation_input_node 节点名称正确，检查滤波器连接

### 6.2 调试建议

1. 先禁用滤波器测试基本功能
2. 逐步启用滤波器并检查网表
3. 使用简单参数进行初步验证
4. 在SPICE中仿真验证最终效果