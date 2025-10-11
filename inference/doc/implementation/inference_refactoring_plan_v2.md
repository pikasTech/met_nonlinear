# Inference 模块代码重构计划 V2

## 1. 重构背景与现状分析

### 1.1 已完成的重构工作
基于调研，第一阶段的重构工作已经取得显著进展：

1. **后端模块化** - `inference_backends.py` (原1085行) 已成功拆分为：
   - `backends/base.py` (160行)
   - `backends/timeseries_backend.py`
   - `backends/batch_backend.py`
   - `backends/layered_backend.py` (90行)
   - `backends/spice/` 子模块
   - `backends/utils.py`

2. **基础设施建设** - `common/` 模块已创建：
   - `common/data_range.py` (117行)
   - `common/logger.py` (127行)
   - `common/validation.py` (146行)

3. **测试框架建立** - `tests/` 目录结构已完善：
   - 单元测试覆盖了 common 模块
   - 建立了测试基础设施

### 1.2 待完成的重构工作
以下文件仍超过300行限制，需要进一步拆分：

1. **manager.py** (432行) - 推理管理器，职责过多
2. **processor.py** (347行) - 推理处理器，包含多种功能
3. **visualization.py** (306行) - 可视化功能，刚好超过限制

### 1.3 重构目标
1. 将所有文件控制在300行以内
2. 保持模块职责单一
3. 维持向后兼容性
4. 提高代码可维护性和可测试性

## 2. 详细重构计划

### 2.1 第二阶段：拆分 manager.py (432行)

#### 2.1.1 目标模块结构
```
inference/
├── management/
│   ├── __init__.py
│   ├── inference_manager.py    # 主管理器类 (~150行)
│   ├── data_validator.py       # 数据验证功能 (~80行)
│   ├── inference_executor.py   # 推理执行功能 (~100行)
│   ├── error_analyzer.py       # 误差分析功能 (~80行)
│   └── report_generator.py     # 报告生成功能 (~60行)
```

#### 2.1.2 修改文件列表和说明

**1. 创建 `management/__init__.py`**
```python
# 导出主要接口
from .inference_manager import InferenceManager
__all__ = ['InferenceManager']
```

**2. 创建 `management/data_validator.py`**
- 从 `manager.py` 提取验证相关方法
- 包含功能：
  - `validate_inference_prerequisites()` - 验证推理前置条件
  - `check_existing_inference_data()` - 检查已有推理数据
  - `find_input_file()` - 查找输入文件
  - 新增：文件格式验证、数据完整性检查

**3. 创建 `management/inference_executor.py`**
- 从 `manager.py` 提取推理执行逻辑
- 包含功能：
  - `generate_inference_data()` - 生成推理数据
  - `execute_neural_network_inference()` - 执行神经网络推理
  - `execute_spice_inference()` - 执行SPICE推理
  - `save_inference_metadata()` - 保存元数据

**4. 创建 `management/error_analyzer.py`**
- 从 `manager.py` 提取误差分析功能
- 包含功能：
  - `analyze_inference_errors()` - 分析推理误差主方法
  - `compute_layer_errors()` - 计算逐层误差
  - `generate_error_statistics()` - 生成误差统计

**5. 创建 `management/report_generator.py`**
- 从 `manager.py` 提取报告生成功能
- 包含功能：
  - `generate_analysis_report()` - 生成分析报告
  - `generate_visualization()` - 生成可视化图表
  - `format_report_data()` - 格式化报告数据

**6. 修改 `management/inference_manager.py` (原 manager.py)**
- 保留主类框架和公共接口
- 使用组合模式，委托功能到各子模块
- 修改点：
  - 导入各子模块
  - 将原方法改为对子模块的调用
  - 保持公共API不变

### 2.2 第三阶段：拆分 processor.py (347行)

#### 2.2.1 目标模块结构
```
inference/
├── processing/
│   ├── __init__.py
│   ├── inference_processor.py  # 主处理器类 (~120行)
│   ├── model_loader.py         # 模型加载功能 (~80行)
│   ├── backend_manager.py      # 后端管理功能 (~100行)
│   └── data_filter.py          # 数据过滤功能 (~80行)
```

#### 2.2.2 修改文件列表和说明

**1. 创建 `processing/__init__.py`**
```python
from .inference_processor import InferenceProcessor
__all__ = ['InferenceProcessor']
```

**2. 创建 `processing/model_loader.py`**
- 从 `processor.py` 提取模型加载功能
- 包含功能：
  - `initialize_model()` - 初始化模型
  - `load_best_weights()` - 加载最佳权重
  - `load_scaler()` - 加载缩放器
  - `validate_model_config()` - 验证模型配置

**3. 创建 `processing/backend_manager.py`**
- 从 `processor.py` 提取后端管理功能
- 包含功能：
  - `initialize_backend()` - 初始化后端
  - `switch_backend()` - 切换后端
  - `get_spice_backend_class()` - 获取SPICE后端类
  - `get_available_backends()` - 获取可用后端列表

**4. 创建 `processing/data_filter.py`**
- 从 `processor.py` 提取数据过滤功能
- 包含功能：
  - `load_wave_data_with_filter()` - 带过滤加载数据
  - `filter_min_max_magnitude()` - 筛选最小最大震级
  - `apply_quick_mode_filter()` - 应用快速模式过滤

**5. 修改 `processing/inference_processor.py` (原 processor.py)**
- 保留主类框架和延迟加载模式
- 使用各子模块功能
- 修改点：
  - 导入子模块
  - 简化初始化逻辑
  - 保持代理方法不变

### 2.3 第四阶段：拆分 visualization.py (306行)

#### 2.3.1 目标模块结构
```
inference/
├── visualization/
│   ├── __init__.py
│   ├── base.py                 # 基础可视化器 (~50行)
│   ├── waveform.py            # 波形可视化 (~80行)
│   ├── layered.py             # 分层可视化 (~100行)
│   └── comparison.py          # 对比可视化 (~120行)
```

#### 2.3.2 修改文件列表和说明

**1. 更新 `visualization/__init__.py`**
```python
from .base import InferenceVisualizer
__all__ = ['InferenceVisualizer']
```

**2. 创建 `visualization/base.py`**
- 基础可视化器类和通用功能
- 包含：
  - `InferenceVisualizer` 基类定义
  - 通用初始化方法
  - 共享的绘图设置

**3. 创建 `visualization/waveform.py`**
- 从 `visualization.py` 提取基本波形可视化
- 包含功能：
  - `visualize_results()` - 基本推理结果可视化
  - 输入输出波形对比功能

**4. 创建 `visualization/layered.py`**
- 从 `visualization.py` 提取分层可视化
- 包含功能：
  - `visualize_layer_results()` - 分层推理结果可视化
  - 多通道网格布局显示

**5. 创建 `visualization/comparison.py`**
- 从 `visualization.py` 提取对比分析可视化
- 包含功能：
  - `compare_layer_with_direct_output()` - 层输出对比
  - `visualize_layer_comparison()` - 后端对比可视化
  - 误差统计和显示功能

## 3. 实施步骤

### 3.1 执行顺序
1. **创建新 worktree**
   ```bash
   git worktree add ../met_nonlinear_refactoring refactoring/inference-v2
   ```

2. **第一步：拆分 manager.py**
   - 创建 management/ 目录结构
   - 逐个提取功能到子模块
   - 运行测试确保功能正常
   - 提交："refactor: split manager.py into management modules"

3. **第二步：拆分 processor.py**
   - 创建 processing/ 目录结构
   - 提取各功能模块
   - 更新导入路径
   - 运行测试验证
   - 提交："refactor: split processor.py into processing modules"

4. **第三步：拆分 visualization.py**
   - 更新 visualization/ 目录
   - 拆分可视化功能
   - 确保向后兼容
   - 运行测试验证
   - 提交："refactor: reorganize visualization module"

5. **第四步：更新测试和文档**
   - 更新所有测试的导入路径
   - 添加新模块的单元测试
   - 更新文档
   - 提交："test: update tests for refactored modules"

### 3.2 风险控制措施

1. **保持向后兼容**
   - 所有公共API保持不变
   - 使用 `__init__.py` 维持原有导入路径
   - 例如：`from inference.manager import InferenceManager` 仍然有效

2. **渐进式重构**
   - 每次只重构一个模块
   - 每步都运行完整测试套件
   - 使用 Git worktree 隔离更改

3. **测试覆盖**
   - 重构前运行测试建立基线
   - 重构后确保所有测试通过
   - 为新模块添加单元测试

### 3.3 验证清单

每个阶段完成后检查：
- [ ] 所有文件都在300行以内
- [ ] 原有功能测试全部通过
- [ ] 导入路径向后兼容
- [ ] 新模块有适当的文档字符串
- [ ] 代码风格一致
- [ ] 无循环依赖

## 4. 预期成果

### 4.1 代码质量提升
- 所有模块文件控制在300行以内
- 模块职责更加单一明确
- 提高代码可读性和可维护性

### 4.2 项目结构优化
```
inference/
├── backends/          # 已完成重构
├── common/           # 已完成重构
├── management/       # manager.py 拆分结果
├── processing/       # processor.py 拆分结果
├── visualization/    # visualization.py 拆分结果
└── tests/           # 测试模块
```

### 4.3 维护性改善
- 每个模块都有明确的职责边界
- 便于单元测试和集成测试
- 支持功能的独立演进和优化

## 5. 后续优化建议

重构完成后，可考虑以下优化：

1. **性能优化**
   - 识别性能瓶颈
   - 优化数据处理流程
   - 考虑并行处理可能性

2. **接口统一**
   - 审查各模块接口一致性
   - 考虑引入接口抽象层
   - 标准化错误处理

3. **文档完善**
   - 为每个新模块编写详细文档
   - 更新架构图
   - 添加使用示例

此重构计划遵循原有设计理念，在保持功能完整性的同时，通过模块化改造提升代码质量。