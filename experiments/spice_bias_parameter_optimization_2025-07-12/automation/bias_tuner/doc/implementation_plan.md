# 独立调参器实施计划

**创建日期**: 2025-07-13  
**项目**: SPICE偏置补偿独立调参器  
**目标**: 实现一个零依赖、可独立测试的自动化调参工具  

---

## 📁 目录结构设计

```
automation/bias_tuner/
├── doc/                                # 文档目录
│   ├── automation_design_proposals.md  # 移动自 ../
│   └── implementation_plan.md          # 本文档
│
├── test_resources/                     # 测试资源目录
│   ├── config_samples/                 # 配置文件样本
│   │   ├── config_baseline.json       # 基线配置（无补偿）
│   │   ├── config_layer1.json         # 层1补偿后
│   │   ├── config_layer12.json        # 层1+2补偿后
│   │   └── config_layer123.json       # 层1+2+3补偿后
│   │
│   └── error_analysis_samples/         # 误差分析结果样本
│       ├── error_analysis_baseline.json    # 基线误差
│       ├── error_analysis_layer1.json      # 层1补偿后误差
│       ├── error_analysis_layer12.json     # 层1+2补偿后误差
│       └── error_analysis_layer123.json    # 层1+2+3补偿后误差
│
├── src/                                # 源代码目录
│   ├── __init__.py
│   ├── core/                           # 核心功能模块
│   │   ├── __init__.py
│   │   ├── command_runner.py          # subprocess命令执行
│   │   ├── json_handler.py            # JSON读写处理
│   │   ├── config_manager.py          # config.json管理
│   │   └── compensation_calc.py       # 补偿算法
│   │
│   ├── strategies/                     # 补偿策略
│   │   ├── __init__.py
│   │   ├── base_strategy.py           # 策略基类
│   │   └── sequential_same_phase.py   # 顺序同相补偿策略
│   │
│   └── utils/                          # 工具函数
│       ├── __init__.py
│       ├── logger.py                   # 日志工具
│       ├── backup.py                   # 备份恢复
│       └── path_manager.py             # 路径管理
│
├── tests/                              # 测试代码目录
│   ├── __init__.py
│   ├── conftest.py                     # pytest配置
│   ├── test_json_handler.py           # 测试JSON处理
│   ├── test_config_manager.py         # 测试配置管理
│   ├── test_compensation_calc.py      # 测试补偿计算
│   ├── test_sequential_strategy.py    # 测试顺序补偿策略
│   └── test_integration.py            # 集成测试
│
├── results/                            # 结果输出目录
│   └── .gitkeep
│
├── tuner.py                            # 主程序入口
├── requirements.txt                    # 依赖（仅pytest等测试工具）
└── README.md                           # 使用说明
```

---

## 📝 文件创建和修改计划

### 第一步：创建目录结构和移动文件

```bash
# 1. 创建目录结构
mkdir -p automation/bias_tuner/{doc,test_resources/{config_samples,error_analysis_samples},src/{core,strategies,utils},tests,results}

# 2. 移动设计文档
mv automation/automation_design_proposals.md automation/bias_tuner/doc/
mv automation/bias_tuner_implementation_plan.md automation/bias_tuner/doc/implementation_plan.md

# 3. 复制测试资源
# 从实际项目复制配置和误差分析文件作为测试样本
```

### 第二步：核心模块实现

#### 1. **src/utils/path_manager.py**
```python
"""路径管理器 - 统一管理所有文件路径"""
# 功能：
# - 计算项目根目录路径
# - 提供配置文件、分析结果文件的路径
# - 支持测试模式（使用test_resources）和生产模式
```

#### 2. **src/core/json_handler.py**
```python
"""JSON文件处理器"""
# 功能：
# - read_json(path) -> dict
# - write_json(path, data)
# - extract_bias_error_matrix(error_analysis_json) -> List[List[float]]
# - validate_json_structure(data, schema) -> bool
```

#### 3. **src/core/config_manager.py**
```python
"""配置文件管理器"""
# 功能：
# - load_config(path) -> dict
# - save_config(path, config)
# - update_bias_compensation(config, layer_compensations) -> dict
# - disable_bias_compensation(config) -> dict
# - validate_config(config) -> bool
```

#### 4. **src/core/compensation_calc.py**
```python
"""补偿值计算器"""
# 功能：
# - calculate_same_phase_compensation(errors, factor=1.0) -> List[float]
# - validate_compensation_values(values) -> bool
# - calculate_improvement(before_errors, after_errors) -> float
# - get_layer_statistics(errors) -> dict
```

#### 5. **src/core/command_runner.py**
```python
"""命令执行器（初期用于模拟）"""
# 功能：
# - run_inference(project_name, mock=True) -> bool
# - run_analysis(project_name, mock=True) -> bool
# - 模拟模式：返回预定义的成功结果
# - 实际模式：调用subprocess
```

#### 6. **src/strategies/sequential_same_phase.py**
```python
"""顺序同相补偿策略"""
# 功能：
# - execute(project_name, target_layers=[1,2,3], mock=True) -> dict
# - 实现完整的顺序补偿流程
# - 返回优化历史和最终结果
```

### 第三步：测试实现

#### 1. **tests/conftest.py**
```python
"""pytest配置和fixtures"""
# 提供：
# - sample_config fixture
# - sample_error_analysis fixture
# - temp_directory fixture
# - mock_command_runner fixture
```

#### 2. **tests/test_json_handler.py**
```python
"""测试JSON处理功能"""
# 测试：
# - 读写JSON文件
# - 提取bias_error_matrix
# - 处理异常情况（文件不存在、格式错误）
```

#### 3. **tests/test_config_manager.py**
```python
"""测试配置管理功能"""
# 测试：
# - 更新bias_compensation配置
# - 禁用补偿
# - 配置验证
```

#### 4. **tests/test_compensation_calc.py**
```python
"""测试补偿计算功能"""
# 测试：
# - 同相补偿计算
# - 改善率计算
# - 数值验证
```

#### 5. **tests/test_sequential_strategy.py**
```python
"""测试顺序补偿策略"""
# 测试：
# - 完整的3层顺序补偿流程
# - 使用test_resources中的样本数据
# - 验证每步的补偿值和改善率
```

---

## 🧪 测试策略

### 模拟测试流程

1. **准备测试数据**：
   - 使用实际实验中的config.json和error_analysis.json作为测试样本
   - 覆盖基线、层1补偿后、层1+2补偿后、层1+2+3补偿后的各个阶段

2. **Mock命令执行**：
   ```python
   def mock_run_analysis(project_name):
       # 根据当前config.json的补偿配置
       # 返回对应的error_analysis_*.json内容
       # 模拟真实的分析结果
   ```

3. **验证关键数值**：
   - Layer 1补偿后：平均误差应接近0
   - Layer 2补偿值：应该基于Layer 1补偿后的误差
   - Layer 3补偿值：应该基于Layer 1+2补偿后的误差

### pytest测试命令

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_sequential_strategy.py -v

# 查看测试覆盖率
pytest tests/ --cov=src --cov-report=html
```

---

## 🚀 实施步骤

### Day 1: 基础架构（今天）
1. [ ] 创建目录结构
2. [ ] 复制测试资源文件
3. [ ] 实现path_manager.py
4. [ ] 实现json_handler.py
5. [ ] 编写test_json_handler.py
6. [ ] 确保JSON读取测试通过

### Day 2: 核心功能（明天）
1. [ ] 实现config_manager.py
2. [ ] 实现compensation_calc.py
3. [ ] 实现mock command_runner
4. [ ] 编写对应的单元测试
5. [ ] 确保所有单元测试通过

### Day 3: 策略实现
1. [ ] 实现sequential_same_phase.py
2. [ ] 编写集成测试
3. [ ] 使用真实数据验证结果
4. [ ] 与手动实验结果对比

### Day 4: 生产就绪
1. [ ] 实现真实的command_runner
2. [ ] 添加错误处理和日志
3. [ ] 编写tuner.py主程序
4. [ ] 在实际项目上测试

---

## 📊 预期测试数据

基于实验记录，测试应该验证以下数值：

**基线误差** (bias_error_matrix[1]):
```
[0.005323, 0.002278, 0.005201, 0.014258, 0.003152, 0.003255]
```

**Layer 1补偿后误差** (bias_error_matrix[1]):
```
[0.000011, -0.000291, 0.000280, 0.000001, -0.000034, 0.000033]
```

**Layer 1补偿后的Layer 2误差** (bias_error_matrix[2]):
```
[0.002181, 0.001301, 0.000932, 0.007533, 0.000669, 0.001903]
```

---

## ✅ 成功标准

1. **单元测试**：所有核心功能的单元测试通过
2. **集成测试**：模拟的顺序补偿流程产生正确的补偿值
3. **数值验证**：补偿值与手动实验结果一致（误差<0.1%）
4. **代码质量**：测试覆盖率>80%，无循环依赖

---

**文档版本**: v1.0  
**最后更新**: 2025-07-13