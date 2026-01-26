# Dense SPICE层inference_config增强执行计划

## 执行计划概述

基于三个调研报告的发现，本计划将完善inference_config的配置传递机制，使Dense SPICE层支持：
1. 可配置的电源电压（VCC/VEE）
2. 可配置的运放模型
3. 默认禁用高通滤波器（理想仿真环境）

## 一、配置结构设计

### 1.1 完整的inference_config结构
```json
{
  "inference_config": {
    "power_supply": {
      "vcc": 8.0,    // 正电源电压，默认15.0
      "vee": -8.0    // 负电源电压，默认-15.0
    },
    "opamp_config": {
      "model": "ideal",          // 运放模型：ideal, opax205a, ad8622, opa1611等
      "include_file": null,      // 自定义模型文件路径
      "power_pins": true,        // 是否连接电源引脚
      "params": {}               // 自定义参数
    },
    "high_pass_config": {
      "enable": false,           // 默认禁用（理想仿真不需要）
      "cutoff_freq": 0.5,        
      "capacitance": null,
      "resistance": null,
      "auto_bias": true,
      "bias_divider_high": 10000,
      "bias_divider_low": 10000
    },
    "bias_compensation": {
      "enabled": false,
      "layer_bias_adjustments": {}
    }
  }
}
```

## 二、文件修改清单

### 2.1 核心文件修改

#### 文件1：`spice_simulator/circuit_dense.py`
**修改点**：
1. **第80-85行**：在`__init__`方法中添加`power_supply_config`参数
   ```python
   def __init__(self, gains, biases=None, opamp_config=None, 
                use_e96=False, use_relu=False, relu_config=None,
                high_pass_config=None, bias_compensation=None,
                power_supply_config=None):  # 新增参数
   ```

2. **第85-90行**：初始化电源配置
   ```python
   # 电源配置
   self.power_supply_config = power_supply_config or {
       'vcc': 15.0,
       'vee': -15.0
   }
   self.vcc = self.power_supply_config.get('vcc', 15.0)
   self.vee = self.power_supply_config.get('vee', -15.0)
   ```

3. **第124-127行**：修改高通滤波器默认配置
   ```python
   self.high_pass_config = {
       'enable': False,  # 默认禁用
       # ... 其他配置项保持不变
   }
   ```

4. **第324-325行**：替换硬编码的电源电压
   ```python
   # 使用配置的电源电压
   vcc = self.vcc  # 替换原来的 vcc = 15
   vee = self.vee  # 替换原来的 vee = -15
   ```

5. **第381行**：高通滤波器分压计算使用配置值
   ```python
   vcc = self.vcc  # 替换原来的 vcc = 15.0
   ```

6. **第392行**：高通滤波器负分压计算使用配置值
   ```python
   vee = self.vee  # 替换原来的 vee = -15.0
   ```

7. **第499-500行**：网表生成使用配置值
   ```python
   netlist_text += f"""
   * Power Supply
   Vcc vcc 0 {self.vcc}
   Vee vee 0 {self.vee}
   """
   ```

#### 文件2：`spice_simulator/circuit_dense.py` (DenseCircuitFactory类)
**第654-660行**：修改工厂方法签名
```python
@staticmethod
def create(gains, biases=None, opamp_config=None, 
           use_e96=False, use_relu=False, relu_config=None,
           high_pass_config=None, bias_compensation=None,
           power_supply_config=None):  # 新增参数
    # ...
    return DenseCircuit(
        gains=gains,
        biases=biases,
        opamp_config=opamp_config,
        use_e96=use_e96,
        use_relu=use_relu,
        relu_config=relu_config,
        high_pass_config=high_pass_config,
        bias_compensation=bias_compensation,
        power_supply_config=power_supply_config  # 传递参数
    )
```

### 2.2 模型层修改

#### 文件3：`models/model_layers.py`
**第391-399行**：修改`DenseLayerModel.to_spice()`方法签名
```python
def to_spice(self, output_path: str = None, opamp_config: Dict[str, Any] = None, 
             use_e96: bool = False, relu_config: Dict[str, Any] = None, 
             high_pass_config: Dict[str, Any] = None, 
             power_supply_config: Dict[str, Any] = None,  # 新增参数
             amp=1):
```

**第470-485行**：从model_config获取配置并传递
```python
# 从模型配置中获取各项配置
if hasattr(self, 'model_config'):
    inference_config = self.model_config.get('inference_config', {})
    
    # 获取高通滤波器配置（如果未提供）
    if high_pass_config is None:
        high_pass_config = inference_config.get('high_pass_config', None)
    
    # 获取电源配置（新增）
    if power_supply_config is None:
        power_supply_config = inference_config.get('power_supply', None)
    
    # 获取运放配置（新增）
    if opamp_config is None:
        opamp_config = inference_config.get('opamp_config', None)

# 创建DenseCircuit对象
dense_circuit = DenseCircuitFactory.create(
    gains=weight_matrix,
    biases=bias_vector,
    opamp_config=opamp_config,
    use_e96=use_e96,
    use_relu=use_relu,
    relu_config=relu_config,
    high_pass_config=high_pass_config,
    power_supply_config=power_supply_config  # 传递电源配置
)
```

### 2.3 配置文件修改

#### 文件4：`projects/WNET5q1h2u6l3/config.json`
**修改点**：完善inference_config结构
```json
{
  "inference_config": {
    "power_supply": {
      "vcc": 8.0,
      "vee": -8.0
    },
    "opamp_config": {
      "model": "ideal",
      "include_file": null,
      "power_pins": true,
      "params": {}
    },
    "high_pass_config": {
      "enable": false,
      "cutoff_freq": 0.5,
      "capacitance": null,
      "resistance": null,
      "auto_bias": true,
      "bias_divider_high": 10000,
      "bias_divider_low": 10000
    },
    "bias_compensation": {
      "enabled": false,
      "layer_bias_adjustments": {}
    }
  },
  // ... 其他配置保持不变
}
```

### 2.4 后端修改（确保配置传递）

#### 文件5：`inference/wavenet5_spice_backend.py`
**第105-130行**：在`_apply_compensations_to_layers()`方法中传递所有配置
```python
def _apply_compensations_to_layers(self, compensations):
    """应用补偿值到模型层（包括所有配置）"""
    
    # 准备所有配置
    inference_config = self.inference_config or {}
    power_supply_config = inference_config.get('power_supply', None)
    opamp_config = inference_config.get('opamp_config', None)
    high_pass_config = inference_config.get('high_pass_config', None)
    
    for layer in self.model.layers:
        if hasattr(layer, 'model_config'):
            # 更新层的model_config
            if not hasattr(layer, 'model_config'):
                layer.model_config = {}
            
            # 设置完整的inference_config
            layer.model_config['inference_config'] = {
                'power_supply': power_supply_config,
                'opamp_config': opamp_config,
                'high_pass_config': high_pass_config,
                'bias_compensation': {
                    'enabled': bool(compensations),
                    'layer_bias_adjustments': compensations
                }
            }
```

## 三、测试验证计划

### 3.1 单元测试
1. 创建测试文件：`tests/test_power_supply_config.py`
   - 测试不同电源电压下的网表生成
   - 验证偏置电流计算的一致性
   - 测试高通滤波器分压计算

2. 创建测试文件：`tests/test_opamp_config.py`
   - 测试不同运放模型的配置传递
   - 验证理想运放和实际运放模型

### 3.2 集成测试
1. 使用`python cli.py -i WNET5q1h2u6l3`运行推理
2. 验证生成的SPICE网表中电源电压正确
3. 检查高通滤波器是否按配置启用/禁用
4. 验证运放模型配置是否正确应用

### 3.3 仿真验证
1. 使用±15V运行基准测试
2. 使用±8V运行对比测试
3. 验证推理结果的一致性
4. 记录并分析任何误差

## 四、实施步骤

### 第一步：基础配置支持（优先级：高）
1. 修改`circuit_dense.py`添加电源配置参数
2. 替换所有硬编码的电压值
3. 更新网表生成逻辑

### 第二步：配置传递机制（优先级：高）
1. 修改`DenseCircuitFactory.create()`方法
2. 更新`model_layers.py`中的配置传递
3. 确保后端正确传递配置

### 第三步：默认值优化（优先级：中）
1. 将高通滤波器默认设为禁用
2. 设置合理的电源电压默认值
3. 配置理想运放为默认选项

### 第四步：测试与验证（优先级：高）
1. 编写并运行单元测试
2. 执行集成测试
3. 进行仿真验证
4. 记录测试结果

## 五、风险评估与缓解

### 5.1 潜在风险
1. **兼容性风险**：现有项目可能依赖硬编码的±15V
   - **缓解**：保持±15V为默认值，确保向后兼容

2. **精度风险**：电源电压变化可能影响模拟精度
   - **缓解**：偏置计算公式已验证为自适应，无需补偿

3. **运放兼容性**：某些运放可能不支持低电压
   - **缓解**：在配置中添加电压范围验证

### 5.2 回滚计划
如果出现问题，可以通过以下方式快速回滚：
1. 在config.json中不设置新配置项，系统将使用默认值
2. 保留原始代码的git提交，可随时恢复

## 六、预期成果

### 6.1 功能增强
- ✅ 支持可配置的电源电压（±5V到±18V）
- ✅ 支持多种运放模型配置
- ✅ 高通滤波器可按需启用/禁用

### 6.2 性能优化
- ✅ 理想仿真环境下默认禁用高通滤波器，减少误差
- ✅ 偏置电流计算自动适应不同电压，无需权重转换

### 6.3 可维护性提升
- ✅ 消除硬编码值，提高代码灵活性
- ✅ 统一配置管理，简化系统维护
- ✅ 完整的配置传递链，便于扩展

## 七、时间估算

- 代码修改：2-3小时
- 测试编写：1-2小时
- 集成测试：1小时
- 文档更新：0.5小时
- **总计**：4.5-6.5小时

## 八、注意事项

1. **保持向后兼容**：所有新增参数都应有合理的默认值
2. **充分测试**：特别注意边界条件和异常情况
3. **文档更新**：及时更新相关文档和注释
4. **版本控制**：在开始修改前创建新分支

---

**执行状态**：待执行  
**创建日期**：2025-01-20  
**作者**：Claude Code Assistant