# Inference 模块代码重构计划

## 1. 重构背景与目标

### 1.1 当前状况
- **文件规模问题**：6个文件超过300行，最大的`inference_backends.py`有1085行
- **代码重复问题**：数据范围检查代码在多个模块中重复出现
- **架构一致性**：虽然有`unified.py`提供统一架构，但未被充分利用

### 1.2 重构目标
1. **文件拆分**：将超过300行的文件拆分成更小的模块，每个不超过300行
2. **代码复用**：抽取重复代码到公共基础设施模块
3. **架构统一**：充分利用已定义的统一数据结构
4. **依赖优化**：简化模块间依赖关系，避免循环依赖

## 2. 具体重构计划

### 2.1 第一阶段：基础设施建设（风险最低）

#### 2.1.1 创建通用工具模块 `common/`
```
inference/
├── common/
│   ├── __init__.py
│   ├── data_range.py      # 数据范围检查工具类
│   ├── validation.py       # 通用验证功能
│   └── logging.py          # 统一日志输出
```

#### 2.1.2 数据范围检查工具类设计
```python
# common/data_range.py
from dataclasses import dataclass
from typing import Optional, Union, List
import numpy as np

@dataclass
class DataRangeInfo:
    """统一的数据范围信息"""
    min_value: float
    max_value: float
    mean_value: float
    std_value: float
    shape: tuple
    dtype: str
    
class DataRangeChecker:
    """数据范围检查工具类"""
    @staticmethod
    def analyze_data(data: Union[np.ndarray, List[np.ndarray]], 
                    name: str = "Data",
                    verbose: bool = True) -> DataRangeInfo:
        """分析数据范围并可选打印"""
        pass
    
    @staticmethod
    def compare_ranges(before: DataRangeInfo, 
                      after: DataRangeInfo,
                      operation: str = "Processing") -> None:
        """比较处理前后的数据范围"""
        pass
```

### 2.2 第二阶段：拆分大文件

#### 2.2.1 拆分 `inference_backends.py` (1085行)
```
inference/
├── backends/
│   ├── __init__.py
│   ├── base.py             # 基类定义 (~150行)
│   ├── timeseries.py       # TimeSeriesBackend (~200行)
│   ├── batch_predict.py    # BatchPredictBackend (~200行)
│   ├── layer_by_layer.py   # LayerByLayerBackend (~250行)
│   ├── spice.py           # SPICEBackend (~250行)
│   └── numpy_backend.py    # NumPyBackend (~200行)
```

#### 2.2.2 拆分 `manager.py` (674行)
```
inference/
├── management/
│   ├── __init__.py
│   ├── project_manager.py  # 项目管理功能 (~200行)
│   ├── result_handler.py   # 结果处理功能 (~200行)
│   ├── export_manager.py   # 导出管理功能 (~200行)
│   └── config_manager.py   # 配置管理功能 (~100行)
```

#### 2.2.3 拆分 `visualization.py` (507行)
```
inference/
├── visualization/
│   ├── __init__.py
│   ├── plotter.py          # 基础绘图功能 (~150行)
│   ├── layer_visualizer.py # 层级可视化 (~150行)
│   ├── comparison.py       # 对比可视化 (~150行)
│   └── export.py           # 图像导出功能 (~100行)
```

### 2.3 第三阶段：统一架构应用

#### 2.3.1 充分利用 `unified.py` 中的数据结构
- 所有后端统一使用 `InferenceResult`
- 数据范围检查统一使用 `DataRange`
- 层信息统一使用 `LayerInfo`

#### 2.3.2 重构后的依赖关系
```
┌─────────────────────────────────────────┐
│             unified.py                   │
│        (统一数据结构定义)                 │
└────────────────┬────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼──┐    ┌───▼──┐    ┌───▼──┐
│common│    │backends│   │visual-│
│      │    │       │    │ization│
└──────┘    └───┬───┘    └───────┘
                │
         ┌──────┴──────┐
         │             │
    ┌────▼───┐   ┌────▼────┐
    │processor│   │management│
    └────────┘   └──────────┘
```

## 3. 风险分析与应对措施

### 3.1 主要风险

#### 风险1：破坏现有功能
- **描述**：重构过程中可能意外改变原有行为
- **影响等级**：高
- **应对措施**：
  1. 创建完整的集成测试套件
  2. 使用特征开关，允许切换新旧实现
  3. 分阶段重构，每次只修改一小部分

#### 风险2：引入新的Bug
- **描述**：新的代码结构可能引入未预见的问题
- **影响等级**：中
- **应对措施**：
  1. 编写详细的单元测试
  2. 进行代码审查
  3. 保留详细的重构日志

#### 风险3：接口变化
- **描述**：新的模块化结构可能影响接口调用
- **影响等级**：中
- **应对措施**：
  1. 保持接口签名不变
  2. 添加适配层处理差异
  3. 充分的集成测试

#### 风险4：依赖关系复杂化
- **描述**：拆分可能导致更复杂的依赖关系
- **影响等级**：低
- **应对措施**：
  1. 明确定义模块接口
  2. 使用依赖注入
  3. 避免循环依赖

### 3.2 风险缓解策略

1. **渐进式重构**：
   - 先重构风险最低的部分（工具类）
   - 逐步推进到核心模块
   - 每个阶段都进行充分测试

2. **代码备份**：
   - 重构前将原有代码移至 `inference/backup/` 目录
   - 新代码直接在原位置实现
   - 完成后可删除备份

3. **版本控制**：
   - 每个重构阶段创建独立分支
   - 详细记录每次改动
   - 便于问题追踪

## 4. 测试策略

### 4.1 测试框架设计
```
inference/
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # pytest配置和fixtures
│   ├── test_common/
│   │   ├── test_data_range.py         # 数据范围工具测试
│   │   └── test_validation.py         # 验证工具测试
│   ├── test_backends/
│   │   ├── test_base.py               # 基类测试
│   │   ├── test_timeseries.py         # 时序后端测试
│   │   └── test_spice.py              # SPICE后端测试
│   ├── test_integration/
│   │   ├── test_inference_flow.py     # 完整推理流程测试
│   │   └── test_backward_compat.py    # 向后兼容性测试
│   └── test_performance/
│       └── test_benchmarks.py         # 性能基准测试
```

### 4.2 关键节点验证

#### 4.2.1 数据一致性验证
```python
# tests/test_integration/test_backward_compat.py
import pytest
import numpy as np
from inference.processor import InferenceProcessor  # 旧实现
from inference.refactored.processor import RefactoredProcessor  # 新实现

class TestBackwardCompatibility:
    """验证重构前后行为一致性"""
    
    @pytest.fixture
    def test_data(self):
        """准备测试数据"""
        return {
            'project_path': 'test_project',
            'input_data': np.random.randn(1000, 6),
            'config': {...}
        }
    
    def test_inference_results_match(self, test_data):
        """验证推理结果一致"""
        old_processor = InferenceProcessor()
        new_processor = RefactoredProcessor()
        
        old_result = old_processor.process(**test_data)
        new_result = new_processor.process(**test_data)
        
        # 验证输出完全一致
        np.testing.assert_allclose(
            old_result.output_data,
            new_result.output_data,
            rtol=1e-7
        )
```


### 4.3 测试覆盖率要求
- 单元测试覆盖率：>90%
- 集成测试覆盖率：>80%
- 关键路径覆盖率：100%

## 5. 实施计划

### 5.1 时间线
1. **第1周**：基础设施建设
   - 创建common模块
   - 编写基础测试框架
   
2. **第2-3周**：文件拆分
   - 拆分inference_backends.py
   - 为每个后端编写测试
   
3. **第4周**：架构统一
   - 应用unified.py中的数据结构
   - 更新所有模块使用统一接口
   
4. **第5周**：集成测试与优化
   - 运行完整测试套件
   - 性能优化
   - 文档更新

### 5.2 检查点
- [ ] 基础设施模块完成且测试通过
- [ ] 所有大文件拆分完成
- [ ] 向后兼容性测试全部通过
- [ ] 功能测试全部通过
- [ ] 文档更新完成

## 6. 备份策略

重构开始前：
1. 将现有 `inference/` 下的所有 `.py` 文件复制到 `inference/backup/` 目录
2. 在原位置直接进行重构
3. 确认重构成功后可删除备份目录
4. 备份仅用于参考，不进行代码混放

## 7. 成功标准

1. **代码质量**：
   - 所有文件小于300行
   - 代码重复率降低50%以上
   
2. **功能完整性**：
   - 所有现有功能正常工作
   - 测试覆盖率达到目标
   
3. **可维护性**：
   - 模块职责清晰
   - 依赖关系简单明了
   - 新功能易于添加