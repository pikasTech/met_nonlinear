# SPICE仿真器分析文档

## 目录

### 偏置补偿分析

#### Dense Circuit 偏置滤波完整方案

**📁 [dense_circuit_bias_filtering/](dense_circuit_bias_filtering/)**

完整的dense circuit偏置滤波解决方案，包含：

- **技术分析**：问题分析、解决方案设计、技术原理
- **实施指南**：具体代码修改步骤、配置参数、验证方法  
- **代码示例**：完整实现示例、工厂方法、使用演示
- **仿真验证**：Python仿真代码、性能分析、参数计算

#### 方案概述

在`circuit_dense`的加法器输出与激活函数输入之间插入高通滤波器，用于补偿运放偏置误差：

```
[加法器输出] ----C---- [激活函数输入]
                |
                R
                |
           [bias电压]
```

**关键特点：**
- ✅ 非侵入性：不修改现有激活函数电路
- ✅ 自适应补偿：无需精确知道偏置误差大小
- ✅ 简单可靠：仅需RC无源元件
- ✅ 灵活配置：支持通道级和全局配置

### 其他分析文档

*待添加*

## 快速使用

### 查看偏置滤波方案

1. 📖 **阅读** [完整方案文档](dense_circuit_bias_filtering/) 了解技术原理
2. 🔧 **按照** [实施指南](dense_circuit_bias_filtering/circuit_dense_implementation_guide.md) 修改代码
3. ✅ **运行** [仿真验证](dense_circuit_bias_filtering/bias_compensation_simulation_example.py) 测试效果
4. 🚀 **参考** [代码示例](dense_circuit_bias_filtering/circuit_dense_modification_example.py) 快速上手

### 相关文件

- **源代码**：`spice_simulator/circuit_dense.py`
- **测试代码**：`spice_simulator/tests/`
- **用户指南**：`spice_simulator/doc/user_guide/`