# SPICE 偏置补偿验证测试方案

## 测试日期: 2025-07-12

## 一、测试目标

### 1.1 主要目标
- 验证 SPICE 偏置补偿功能正确实现
- 确认补偿仅影响 SPICE 电路，不影响 NN 推理
- 测量补偿对 SPICE 仿真精度的改善
- 验证系统的稳定性和兼容性

### 1.2 验证原则
- NN 输出必须保持不变（作为基准）
- SPICE 输出应该向 NN 输出靠近
- 补偿机制应该可控且可预测

## 二、测试环境准备

### 2.1 环境要求
```bash
# Python 环境
conda activate tf26

# 依赖检查
python -c "import tensorflow as tf; print(f'TensorFlow: {tf.__version__}')"
python -c "import numpy as np; print(f'NumPy: {np.__version__}')"

# NGspice 检查
ngspice --version
```

### 2.2 测试数据准备
```python
# 创建标准测试输入
import numpy as np
from calibration_analyzer.wavedata import WaveData, WaveRecord

def create_test_input():
    """创建标准测试输入波形"""
    # 正弦波 + 噪声
    t = np.linspace(0, 1, 2000)
    signal = np.sin(2 * np.pi * 10 * t) + 0.1 * np.random.randn(len(t))
    
    wave_data = WaveData(description="Test Input", author="Test")
    record = WaveRecord(
        data=signal.reshape(-1, 1),
        sample_rate=2000,
        channel_names=["input"]
    )
    wave_data.add_record(record)
    
    return wave_data
```

## 三、测试用例设计

### 3.1 单元测试

#### 测试用例 1：配置读取测试
**目的**: 验证偏置补偿配置正确读取

```python
def test_config_reading():
    """测试配置读取功能"""
    config = {
        "inference_config": {
            "bias_compensation": {
                "enabled": True,
                "bias_adjustment_matrix": [0.1, -0.2, 0.3],
                "layer_bias_adjustments": {
                    "0": [0.5, -0.5],
                    "1": [0.2, -0.3, 0.1]
                }
            }
        }
    }
    
    # 测试步骤
    # 1. 创建带配置的模型
    # 2. 初始化 SPICE 后端
    # 3. 验证配置被正确读取
    
    assert backend._prepare_bias_compensations() == expected_compensations
```

#### 测试用例 2：补偿应用测试
**目的**: 验证补偿值正确应用到层

```python
def test_compensation_application():
    """测试补偿值应用"""
    # 1. 准备测试模型
    # 2. 设置补偿值
    # 3. 导出 SPICE
    # 4. 验证层对象的临时属性
    
    backend._apply_compensations_to_layers({0: [0.5, -0.5], 1: [0.2]})
    
    # 验证
    assert hasattr(dense_layer, '_temp_bias_compensation')
    assert dense_layer._temp_bias_compensation == [0.5, -0.5]
```

#### 测试用例 3：SPICE 电路参数测试
**目的**: 验证生成的 SPICE 电路包含调整后的参数

```python
def test_spice_circuit_parameters():
    """测试 SPICE 电路参数"""
    # 1. 应用补偿
    # 2. 生成 SPICE 电路
    # 3. 解析电路文件
    # 4. 验证偏置电压源值
    
    spice_content = read_spice_file("layer1.cir")
    
    # 验证偏置值已调整
    assert "V_bias1 n_bias1 0 DC 0.7" in spice_content  # 原值 0.2 + 补偿 0.5
```

### 3.2 集成测试

#### 测试用例 4：端到端补偿测试
**目的**: 验证完整的补偿流程

```python
def test_end_to_end_compensation():
    """端到端补偿测试"""
    # 配置
    config = create_test_config_with_compensation()
    
    # 创建模型和后端
    model = load_wavenet5_model(config)
    backend = WaveNet5SPICEBackend(model)
    
    # 测试输入
    test_input = create_test_input()
    
    # 1. NN 推理（基准）
    nn_output = model.predict(test_input)
    
    # 2. SPICE 推理（无补偿）
    config['inference_config']['bias_compensation']['enabled'] = False
    spice_output_no_comp = backend.infer(test_input, layers=2)
    
    # 3. SPICE 推理（有补偿）
    config['inference_config']['bias_compensation']['enabled'] = True
    spice_output_with_comp = backend.infer(test_input, layers=2)
    
    # 验证
    # - NN 输出保持不变
    # - SPICE 有补偿的输出更接近 NN
    error_no_comp = compute_error(nn_output, spice_output_no_comp)
    error_with_comp = compute_error(nn_output, spice_output_with_comp)
    
    assert error_with_comp < error_no_comp
```

#### 测试用例 5：多层补偿测试
**目的**: 验证多层模型的补偿

```python
def test_multilayer_compensation():
    """多层补偿测试"""
    config = {
        "inference_config": {
            "bias_compensation": {
                "enabled": True,
                "layer_bias_adjustments": {
                    "0": [0.1, -0.1, 0.2],  # 第一个 Dense 层
                    "1": [0.3, -0.2],       # 第二个 Dense 层
                    "2": [0.5]              # 第三个 Dense 层
                }
            }
        }
    }
    
    # 执行推理并验证每层的补偿效果
    for layer_idx in range(3):
        verify_layer_compensation(layer_idx, expected_compensation[layer_idx])
```

### 3.3 边界测试

#### 测试用例 6：极端补偿值测试
**目的**: 测试系统对极端补偿值的处理

```python
def test_extreme_compensation_values():
    """极端补偿值测试"""
    extreme_configs = [
        {"compensation": [10.0, -10.0, 5.0]},    # 极大值
        {"compensation": [0.001, -0.001]},       # 极小值
        {"compensation": [1.0] * 100},           # 大量补偿值
    ]
    
    for config in extreme_configs:
        # 验证系统稳定性
        # 验证 SPICE 电路仍能生成
        # 验证仿真不会发散
```

#### 测试用例 7：格式兼容性测试
**目的**: 测试不同补偿值格式

```python
def test_compensation_format_compatibility():
    """补偿格式兼容性测试"""
    test_formats = [
        0.5,                    # 标量
        [0.5, -0.3],           # 列表
        (0.5, -0.3),           # 元组
        np.array([0.5, -0.3]), # NumPy 数组
    ]
    
    for fmt in test_formats:
        # 验证所有格式都能正确处理
```

### 3.4 性能测试

#### 测试用例 8：性能影响测试
**目的**: 测量补偿机制的性能影响

```python
def test_performance_impact():
    """性能影响测试"""
    import time
    
    # 无补偿的 SPICE 导出时间
    start = time.time()
    backend.export_model_to_spice()
    time_no_comp = time.time() - start
    
    # 有补偿的 SPICE 导出时间
    enable_compensation()
    start = time.time()
    backend.export_model_to_spice()
    time_with_comp = time.time() - start
    
    # 性能影响应该很小（< 10%）
    assert (time_with_comp - time_no_comp) / time_no_comp < 0.1
```

## 四、测试执行计划

### 4.1 测试顺序

1. **阶段 1：单元测试**（1 小时）
   - 执行所有单元测试
   - 修复发现的问题

2. **阶段 2：集成测试**（2 小时）
   - 执行端到端测试
   - 验证补偿效果

3. **阶段 3：边界和性能测试**（1 小时）
   - 测试极端情况
   - 评估性能影响

### 4.2 测试命令

```bash
# 运行所有测试
conda run -n tf26 pytest tests/test_spice_bias_compensation.py -v

# 运行特定测试
conda run -n tf26 pytest tests/test_spice_bias_compensation.py::test_end_to_end_compensation -v

# 生成测试报告
conda run -n tf26 pytest tests/test_spice_bias_compensation.py --html=report.html
```

## 五、验证指标

### 5.1 功能指标

| 指标 | 目标 | 验证方法 |
|------|------|----------|
| 配置读取成功率 | 100% | 单元测试 |
| 补偿应用准确性 | 100% | 参数对比 |
| NN 输出不变性 | 100% | 数值对比 |
| SPICE 精度改善 | >20% | 误差分析 |

### 5.2 性能指标

| 指标 | 目标 | 验证方法 |
|------|------|----------|
| 导出时间增加 | <10% | 计时测试 |
| 内存使用增加 | <5% | 资源监控 |
| 代码复杂度 | 低 | 代码审查 |

## 六、测试数据记录

### 6.1 测试结果模板

```markdown
## 测试执行记录

**日期**: 2025-07-12
**执行人**: [姓名]
**环境**: TensorFlow 2.6, Python 3.9

### 测试结果

| 测试用例 | 状态 | 说明 |
|----------|------|------|
| test_config_reading | ✅ 通过 | - |
| test_compensation_application | ✅ 通过 | - |
| test_spice_circuit_parameters | ❌ 失败 | 偏置值格式问题 |
| ... | ... | ... |

### 问题记录

1. **问题 1**: 描述
   - 原因：
   - 解决方案：

### 性能数据

- 无补偿导出时间：X.XX 秒
- 有补偿导出时间：X.XX 秒
- 性能影响：X.X%
```

## 七、问题处理流程

### 7.1 测试失败处理

1. **记录详细错误信息**
   - 错误消息
   - 堆栈跟踪
   - 输入数据

2. **分析根本原因**
   - 代码逻辑错误
   - 配置问题
   - 环境问题

3. **制定修复方案**
   - 代码修改
   - 配置调整
   - 文档更新

### 7.2 回归测试

修复问题后：
1. 重新运行失败的测试
2. 运行相关的测试
3. 执行完整测试套件

## 八、测试完成标准

### 8.1 必须通过的测试

- [ ] 所有单元测试通过
- [ ] 端到端集成测试通过
- [ ] NN 输出保持不变
- [ ] SPICE 精度有改善

### 8.2 可选通过的测试

- [ ] 极端值测试通过
- [ ] 性能影响在可接受范围

## 九、总结

这个测试方案：
1. 覆盖了功能、集成、边界和性能测试
2. 提供了具体的测试代码示例
3. 定义了明确的验证指标
4. 包含了问题处理流程

通过执行这个测试方案，可以全面验证 SPICE 偏置补偿功能的正确性和有效性。