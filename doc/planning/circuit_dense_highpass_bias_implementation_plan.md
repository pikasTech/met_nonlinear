# Circuit Dense 高通滤波器 + Bias 功能实现计划

## 概述

本文档详细描述了在 `circuit_dense.py` 中增加一个输入后置bias高通滤波功能的实现计划。该功能通过一阶无源高通滤波器，将每个输出通道拉到指定的bias电压上，支持配置开关控制。

## 功能需求

### 核心功能
1. **一阶无源高通滤波器**: 通过电容和电阻实现
2. **Bias电压生成**: 通过VCC/VEE分压产生正负bias电压
3. **位置控制**: 插入在乘加后运放输出和ReLU之前
4. **配置控制**: 通过字典参数控制功能开关

### 技术原理

#### 一阶无源高通滤波器
- **传递函数**: H(s) = sRC / (1 + sRC)
- **截止频率**: fc = 1 / (2πRC)
- **电路结构**: 
  - 电容C串联在信号路径
  - 电阻R连接输出端到bias电压源
  - 输出DC分量稳定在bias电压

#### Bias电压生成
- **正bias**: 通过VCC(+15V)分压获取
  - 分压公式: V_bias = VCC × R2 / (R1 + R2)
- **负bias**: 通过VEE(-15V)分压获取  
  - 分压公式: V_bias = VEE × R2 / (R1 + R2)

## 实现方案

### 1. 配置参数结构设计

在`DenseCircuit.__init__`中添加新的配置参数：

```python
high_pass_config = {
    'enable': False,           # 是否启用高通滤波
    'cutoff_freq': 1.0,        # 截止频率(Hz)
    'capacitance': None,       # 电容值(F)，为None时自动计算
    'resistance': None,        # 电阻值(Ω)，为None时自动计算
    'bias_voltage': 0.0,       # bias电压(V)
    'auto_bias': True,         # 是否根据正负自动选择VCC/VEE分压
    'bias_divider_high': 10e3, # 分压电阻上阻值(Ω)
    'bias_divider_low': 10e3,  # 分压电阻下阻值(Ω)
}
```

### 2. 代码修改位置

#### 2.1 构造函数修改 (`__init__`)
- **位置**: 第29行参数列表
- **修改**: 添加`high_pass_config=None`参数
- **处理逻辑**: 
  ```python
  # 处理高通滤波器配置
  if high_pass_config is None:
      self.high_pass_config = {
          'enable': False,
          'cutoff_freq': 1.0,
          'capacitance': None,
          'resistance': None,
          'bias_voltage': 0.0,
          'auto_bias': True,
          'bias_divider_high': 10e3,
          'bias_divider_low': 10e3,
      }
  else:
      self.high_pass_config = {
          'enable': high_pass_config.get('enable', False),
          'cutoff_freq': high_pass_config.get('cutoff_freq', 1.0),
          'capacitance': high_pass_config.get('capacitance', None),
          'resistance': high_pass_config.get('resistance', None),
          'bias_voltage': high_pass_config.get('bias_voltage', 0.0),
          'auto_bias': high_pass_config.get('auto_bias', True),
          'bias_divider_high': high_pass_config.get('bias_divider_high', 10e3),
          'bias_divider_low': high_pass_config.get('bias_divider_low', 10e3),
      }
  ```

#### 2.2 电阻计算修改 (`calculate_resistors`)
- **位置**: 第183行函数内
- **修改**: 在`channel_config`字典中添加高通滤波器参数
- **计算逻辑**:
  ```python
  # 计算高通滤波器参数
  if self.high_pass_config['enable']:
      # 如果未指定电容和电阻值，根据截止频率计算
      if self.high_pass_config['capacitance'] is None or self.high_pass_config['resistance'] is None:
          # 设定默认电容值
          C_default = 1e-6  # 1μF
          # 根据截止频率计算电阻: R = 1 / (2π * f * C)
          R_hp = 1 / (2 * np.pi * self.high_pass_config['cutoff_freq'] * C_default)
          hp_capacitance = C_default
          hp_resistance = R_hp
      else:
          hp_capacitance = self.high_pass_config['capacitance']
          hp_resistance = self.high_pass_config['resistance']
      
      # 计算bias分压电阻
      if self.high_pass_config['auto_bias']:
          bias_voltage = self.high_pass_config['bias_voltage']
          if bias_voltage >= 0:
              # 正bias：从VCC分压
              # V_bias = VCC * R_low / (R_high + R_low)
              # R_low = V_bias * R_high / (VCC - V_bias)
              vcc = 15.0
              R_high = self.high_pass_config['bias_divider_high']
              if bias_voltage < vcc:
                  R_low = bias_voltage * R_high / (vcc - bias_voltage)
              else:
                  R_low = self.high_pass_config['bias_divider_low']
              bias_source = 'vcc'
          else:
              # 负bias：从VEE分压
              # V_bias = VEE * R_low / (R_high + R_low)
              # R_low = V_bias * R_high / (VEE - V_bias)
              vee = -15.0
              R_high = self.high_pass_config['bias_divider_high']
              if bias_voltage > vee:
                  R_low = bias_voltage * R_high / (vee - bias_voltage)
              else:
                  R_low = self.high_pass_config['bias_divider_low']
              bias_source = 'vee'
          
          hp_bias_r_high = R_high
          hp_bias_r_low = R_low
          hp_bias_source = bias_source
      else:
          hp_bias_r_high = self.high_pass_config['bias_divider_high']
          hp_bias_r_low = self.high_pass_config['bias_divider_low']
          hp_bias_source = 'vcc' if self.high_pass_config['bias_voltage'] >= 0 else 'vee'
  else:
      hp_capacitance = None
      hp_resistance = None
      hp_bias_r_high = None
      hp_bias_r_low = None
      hp_bias_source = None
  
  # 添加到channel_config
  channel_config.update({
      'hp_capacitance': hp_capacitance,
      'hp_resistance': hp_resistance,
      'hp_bias_r_high': hp_bias_r_high,
      'hp_bias_r_low': hp_bias_r_low,
      'hp_bias_source': hp_bias_source,
  })
  ```

#### 2.3 网表生成修改 (`_create_circuit_netlist`)
- **位置**: 第431-443行，ReLU激活电路部分
- **修改**: 在运放输出和ReLU之间插入高通滤波器

```python
# 在运放输出后、ReLU之前插入高通滤波器
if self.high_pass_config['enable']:
    # 生成bias电压分压器
    netlist_text += f"""
* 高通滤波器 Bias 电压分压器 - 通道 {ch+1}
R_hp_bias_high{ch+1} {channel_config['hp_bias_source']} hp_bias{ch+1} {channel_config['hp_bias_r_high']}
R_hp_bias_low{ch+1} hp_bias{ch+1} 0 {channel_config['hp_bias_r_low']}
"""
    
    # 生成高通滤波器
    netlist_text += f"""
* 一阶无源高通滤波器 - 通道 {ch+1}
C_hp{ch+1} out{ch+1}_pre out{ch+1}_hp {channel_config['hp_capacitance']}
R_hp{ch+1} out{ch+1}_hp hp_bias{ch+1} {channel_config['hp_resistance']}
"""
    
    # 修改ReLU输入节点
    relu_input_node = f"out{ch+1}_hp"
else:
    relu_input_node = f"out{ch+1}_pre"

# 添加ReLU激活电路
if self.use_relu:
    netlist_text += self.relu_model.get_netlist_text(
        ch+1,
        relu_input_node,  # 使用动态确定的输入节点
        f"out{ch+1}",
        self.relu_config['diode_model']
    )
else:
    # 如果不使用ReLU，直接连接输出
    netlist_text += f"""
* 直接连接输出（无ReLU激活）
Rlink{ch+1} {relu_input_node} out{ch+1} 1e-6
"""
```

#### 2.4 理论仿真修改 (`simulate_numpy`)
- **位置**: 第451行函数内
- **修改**: 在ReLU之前添加高通滤波器的数学模拟

```python
# 在ReLU之前应用高通滤波器效果
if self.high_pass_config['enable']:
    # 简化的高通滤波器模拟：DC分量设为bias电压
    bias_voltage = self.high_pass_config['bias_voltage']
    
    # 对每个通道应用bias调整
    for ch in range(self.n_outputs):
        # 移除DC分量，添加bias电压
        dc_component = np.mean(output[:, ch])
        output[:, ch] = output[:, ch] - dc_component + bias_voltage
```

### 3. 工厂类修改

#### 3.1 `DenseCircuitFactory.create`方法
- **位置**: 第500行
- **修改**: 添加`high_pass_config=None`参数并传递给`DenseCircuit`构造函数

```python
@staticmethod
def create(gains=None, biases=None, R_values=None,
           opamp_config=None, use_e96=False, use_relu=False, 
           relu_config=None, high_pass_config=None):
    # ... 现有代码 ...
    
    # 创建并返回电路实例
    return DenseCircuit(
        gains=gains,
        biases=biases,
        R_values=R_values,
        opamp_config=opamp_config,
        use_e96=use_e96,
        use_relu=local_use_relu,
        relu_config=local_relu_config,
        high_pass_config=high_pass_config  # 新增参数
    )
```

#### 3.2 其他工厂方法
- 在所有相关的工厂方法中添加`high_pass_config`参数支持
- 包括: `create_ideal`, `create_with_relu`, `create_ideal_with_relu`, `create_with_tanh`, `create_ideal_with_tanh`

### 4. 使用示例

```python
# 启用高通滤波器的配置示例
high_pass_config = {
    'enable': True,
    'cutoff_freq': 0.5,        # 0.5Hz 截止频率
    'bias_voltage': 2.5,       # 2.5V bias电压
    'auto_bias': True,         # 自动选择VCC分压
}

# 创建带高通滤波器的电路
circuit = DenseCircuitFactory.create(
    gains=[[1.0, -1.0], [0.5, 2.0]],
    biases=[0.0, 0.0],
    use_relu=True,
    high_pass_config=high_pass_config
)
```

## 实现优势

1. **模块化设计**: 通过配置参数控制，不影响现有功能
2. **向后兼容**: 默认disable状态，现有代码无需修改
3. **灵活配置**: 支持自定义电容、电阻值和bias电压
4. **自动计算**: 可根据截止频率自动计算元件参数
5. **电路级准确性**: 在SPICE仿真中完全准确模拟

## 测试计划

1. **单元测试**: 验证配置参数解析和电路元件计算
2. **集成测试**: 验证与现有ReLU功能的兼容性
3. **仿真测试**: 验证SPICE网表生成和仿真结果
4. **性能测试**: 验证NumPy理论仿真的准确性

## 风险评估

1. **低风险**: 功能默认关闭，不影响现有系统
2. **中风险**: 电路复杂度增加，可能影响仿真性能
3. **缓解措施**: 充分测试，渐进式集成

## 时间估算

- **代码实现**: 2-3天
- **测试验证**: 1-2天
- **文档更新**: 1天
- **总计**: 4-6天

## 配置传递增强计划

### 参数传递链路分析

**完整的参数传递链路**：
```
config.json → ProjectManager → InferenceProcessor → BackendManager → SPICEBackend → DenseLayer.to_spice() → DenseCircuitFactory.create() → DenseCircuit
```

### 详细传递流程

1. **config.json 配置结构**
   - 在 `inference_config` 字段中添加 `high_pass_config` 配置
   - 位置：`/mnt/c/work/met_nonlinear/projects/WNET5q1h2u6l3/config.json`

2. **CLI命令处理**
   - 用户执行: `python cli.py -i PROJECT_NAME`
   - 流程: `cli.py` → `task_dispatcher.py` → `ProjectManager.run_inference()`

3. **推理管理器链路**
   - `ProjectManager.run_inference()` → `InferenceManager.run_inference()` → `InferenceExecutor.generate_inference_data()`

4. **SPICE后端处理**
   - `InferenceExecutor` 创建 `InferenceProcessor` 并设置为 `'spice'` 后端
   - `SPICEBackend.infer()` 调用 `model.to_spice()` 进行模型转换

5. **电路生成**
   - `DenseLayer.to_spice()` 调用 `DenseCircuitFactory.create()` 创建电路
   - 最终传递给 `DenseCircuit.__init__()`

### 需要修改的文件和具体修改点

#### 1. `/mnt/c/work/met_nonlinear/projects/WNET5q1h2u6l3/config.json`
**修改点**: 在 `inference_config` 字段中添加高通滤波器配置
```json
{
  "inference_config": {
    "bias_compensation": {
      "enabled": false,
      "layer_bias_adjustments": {}
    },
    "high_pass_config": {
      "enable": false,
      "cutoff_freq": 1.0,
      "capacitance": null,
      "resistance": null,
      "bias_voltage": 0.0,
      "auto_bias": true,
      "bias_divider_high": 10000,
      "bias_divider_low": 10000
    }
  }
}
```

#### 2. `/mnt/c/work/met_nonlinear/core/project_manager.py`
**修改点**: 在 `ProjectManager.__init__` 中确保 `inference_config` 被正确加载
- **位置**: 第33行，`self.config = Config.load_from_json(self.config_path)`
- **说明**: 确保 `inference_config` 字段被正确解析并可通过 `self.config.inference_config` 访问

#### 3. `/mnt/c/work/met_nonlinear/config.py`
**修改点**: 在 `Config` 类中添加对 `inference_config` 的默认处理
- **位置**: Config类的字段定义部分
- **修改**: 添加 `inference_config` 字段的默认值处理

#### 4. `/mnt/c/work/met_nonlinear/inference/processing/inference_processor.py`
**修改点**: 在 `InferenceProcessor.__init__` 中传递项目配置
- **位置**: 第31行构造函数
- **修改**: 确保 `project_manager.config` 被传递给相关组件

#### 5. `/mnt/c/work/met_nonlinear/models/model_layers.py`
**修改点**: 在 `DenseLayer.to_spice()` 方法中读取和传递 `high_pass_config`
- **位置**: 第391行 `to_spice` 方法
- **修改**: 
  ```python
  def to_spice(self, output_path: str = None, opamp_config: Dict[str, Any] = None, 
               use_e96: bool = False, relu_config: Dict[str, Any] = None, 
               high_pass_config: Dict[str, Any] = None, amp=1):
      # ... 现有代码 ...
      
      # 如果没有提供high_pass_config，尝试从模型配置中获取
      if high_pass_config is None and hasattr(self, 'model_config'):
          high_pass_config = self.model_config.get('inference_config', {}).get('high_pass_config', None)
      
      # 创建DenseCircuit对象
      dense_circuit = DenseCircuitFactory.create(
          gains=weight_matrix,
          biases=bias_vector,
          opamp_config=opamp_config,
          use_e96=use_e96,
          use_relu=use_relu,
          relu_config=relu_config,
          high_pass_config=high_pass_config  # 传递高通滤波器配置
      )
  ```

#### 6. `/mnt/c/work/met_nonlinear/inference/backends/spice/backend.py`
**修改点**: 在 `SPICEBackend` 中传递配置信息给模型
- **位置**: 第74-77行，`export_model_to_spice` 方法
- **修改**: 确保在调用 `model.to_spice()` 时传递配置参数

#### 7. `/mnt/c/work/met_nonlinear/spice_simulator/circuit_dense.py`
**修改点**: 按照主实现计划中的所有修改点进行实现
- 构造函数添加 `high_pass_config` 参数
- 电阻计算方法添加高通滤波器参数计算
- 网表生成方法添加高通滤波器电路
- 工厂类方法添加参数支持

### 配置传递的关键步骤

1. **配置文件扩展**: 在 `config.json` 中添加 `high_pass_config` 字段
2. **配置解析**: 确保 `Config` 类正确解析新字段
3. **配置传递**: 在模型转换过程中将配置传递给 `DenseLayer.to_spice()`
4. **参数应用**: 在 `DenseCircuit` 中应用高通滤波器配置

### 配置示例

```json
{
  "inference_config": {
    "bias_compensation": {
      "enabled": false,
      "layer_bias_adjustments": {}
    },
    "high_pass_config": {
      "enable": true,
      "cutoff_freq": 0.5,
      "bias_voltage": 2.5,
      "auto_bias": true,
      "bias_divider_high": 10000,
      "bias_divider_low": 10000
    }
  }
}
```

### 向后兼容性

- 所有新配置参数都有默认值
- 未配置 `high_pass_config` 时功能默认关闭
- 现有项目无需修改即可继续工作

## 结论

本实现计划提供了一个完整的、向后兼容的高通滤波器+bias功能，满足了用户的所有需求。通过配置化设计，既保持了代码的简洁性，又提供了足够的灵活性。增强计划确保了从 `config.json` 到 `circuit_dense.py` 的完整参数传递链路，使得用户可以通过简单的配置文件修改来控制高通滤波器功能。