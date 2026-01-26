# 重构测试策略：确保行为一致性

## 1. 测试策略概述

### 1.1 核心原则
- **黄金主原则**：重构前的输出作为"黄金标准"
- **增量验证**：每个小改动都要验证
- **数据驱动**：使用真实项目数据进行测试
- **自动化优先**：所有测试必须可自动运行

### 1.2 测试层次
1. **单元测试**：验证单个函数/方法的行为
2. **集成测试**：验证模块间交互
3. **回归测试**：确保现有功能不被破坏
4. **性能测试**：确保性能不退化

## 2. 关键行为识别与测试

### 2.1 数据范围检查行为

**当前行为特征**：
```python
# 原始代码中的数据范围检查
print(f"  数据范围: 最小值={all_data.min():.6f}, 最大值={all_data.max():.6f}")
```

**测试设计**：
```python
# tests/test_common/test_data_range_compatibility.py
import pytest
import numpy as np
from io import StringIO
import sys

class TestDataRangeCompatibility:
    """验证数据范围检查的向后兼容性"""
    
    @pytest.fixture
    def capture_print_output(self):
        """捕获print输出"""
        def _capture(func, *args, **kwargs):
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            try:
                result = func(*args, **kwargs)
                output = sys.stdout.getvalue()
                return result, output
            finally:
                sys.stdout = old_stdout
        return _capture
    
    def test_data_range_output_format(self, capture_print_output):
        """验证输出格式与原始代码一致"""
        test_data = np.array([1.234567, 2.345678, 3.456789])
        
        # 原始方式
        def old_way():
            print(f"  数据范围: 最小值={test_data.min():.6f}, 最大值={test_data.max():.6f}")
        
        # 新方式
        def new_way():
            from inference.common.data_range import DataRangeChecker
            DataRangeChecker.analyze_data(test_data, name="数据")
        
        _, old_output = capture_print_output(old_way)
        _, new_output = capture_print_output(new_way)
        
        # 验证输出包含相同的信息
        assert f"{test_data.min():.6f}" in new_output
        assert f"{test_data.max():.6f}" in new_output
```

### 2.2 推理后端行为验证

**关键行为**：
1. 层级推理的执行顺序
2. 数据缩放/反缩放的时机
3. 相位修正的应用

**测试设计**：
```python
# tests/test_backends/test_layer_inference_behavior.py
import pytest
import numpy as np
from pathlib import Path
import json

class TestLayerInferenceBehavior:
    """验证层级推理行为的一致性"""
    
    @pytest.fixture
    def golden_results(self):
        """加载黄金标准结果"""
        # 在重构前运行一次，保存结果作为黄金标准
        golden_path = Path("tests/golden_data/layer_inference_results.json")
        if golden_path.exists():
            with open(golden_path) as f:
                return json.load(f)
        return None
    
    def test_layer_by_layer_inference_order(self, golden_results):
        """验证层级推理顺序"""
        from inference.backends.layer_by_layer import LayerByLayerBackend
        
        backend = LayerByLayerBackend()
        
        # 记录层级调用顺序
        called_layers = []
        original_infer = backend._infer_layer
        
        def track_layer_calls(layer_index, *args, **kwargs):
            called_layers.append(layer_index)
            return original_infer(layer_index, *args, **kwargs)
        
        backend._infer_layer = track_layer_calls
        
        # 执行推理
        result = backend.infer(test_model, test_data)
        
        # 验证层级顺序
        expected_order = [1, 2, 3, 4, 5]  # WaveNet5的层级顺序
        assert called_layers == expected_order
    
    def test_phase_correction_timing(self):
        """验证相位修正的时机"""
        from inference.backends.spice import SPICEBackend
        
        backend = SPICEBackend()
        
        # 追踪相位修正调用
        correction_calls = []
        
        original_correct = backend._apply_immediate_phase_correction
        def track_corrections(layer_output, layer_index):
            correction_calls.append({
                'layer': layer_index,
                'before_min': np.min(layer_output),
                'before_max': np.max(layer_output)
            })
            result = original_correct(layer_output, layer_index)
            correction_calls[-1].update({
                'after_min': np.min(result),
                'after_max': np.max(result)
            })
            return result
        
        backend._apply_immediate_phase_correction = track_corrections
        
        # 执行推理
        result = backend.infer(test_model, test_data)
        
        # 验证修正发生在正确的层
        corrected_layers = [c['layer'] for c in correction_calls]
        assert 2 in corrected_layers  # Dense层应该被修正
        assert 3 in corrected_layers
        assert 4 in corrected_layers
        assert 5 not in corrected_layers  # 输出层不应被修正
```

### 2.3 数据处理管道验证

**关键行为**：
1. 数据加载顺序
2. 缩放器应用
3. 批处理逻辑

**测试设计**：
```python
# tests/test_integration/test_data_pipeline.py
import pytest
import numpy as np
from unittest.mock import Mock, patch

class TestDataPipeline:
    """验证数据处理管道的一致性"""
    
    def test_scaler_application_order(self):
        """验证缩放器应用顺序"""
        from inference.data_processing import InferenceDataProcessor
        
        processor = InferenceDataProcessor()
        
        # 追踪处理步骤
        processing_steps = []
        
        # Mock各个处理方法
        with patch.object(processor, 'load_data') as mock_load:
            with patch.object(processor, 'apply_scaling') as mock_scale:
                with patch.object(processor, 'prepare_batches') as mock_batch:
                    
                    # 设置返回值
                    mock_load.return_value = Mock()
                    mock_scale.return_value = Mock()
                    mock_batch.return_value = Mock()
                    
                    # 记录调用顺序
                    mock_load.side_effect = lambda *a, **k: processing_steps.append('load')
                    mock_scale.side_effect = lambda *a, **k: processing_steps.append('scale')
                    mock_batch.side_effect = lambda *a, **k: processing_steps.append('batch')
                    
                    # 执行处理
                    processor.process(test_config)
                    
                    # 验证顺序
                    assert processing_steps == ['load', 'scale', 'batch']
```

## 3. 黄金主测试框架

### 3.1 生成黄金数据

```python
# scripts/generate_golden_data.py
"""在重构前运行此脚本生成黄金标准数据"""

import json
import numpy as np
from pathlib import Path
from inference.processor import InferenceProcessor
from inference.manager import InferenceManager

def generate_golden_data():
    """生成黄金标准测试数据"""
    
    golden_dir = Path("tests/golden_data")
    golden_dir.mkdir(exist_ok=True)
    
    # 测试项目列表
    test_projects = [
        "WNET5q1h2u6l3",
        "WNET5q0.5h6u8l8"
    ]
    
    results = {}
    
    for project in test_projects:
        print(f"生成项目 {project} 的黄金数据...")
        
        manager = InferenceManager(project)
        
        # 执行各种推理
        results[project] = {
            'nn_inference': serialize_result(manager.infer('nn')),
            'spice_inference': serialize_result(manager.infer('spice')),
            'numpy_inference': serialize_result(manager.infer('numpy')),
            'layer_outputs': get_layer_outputs(manager),
            'data_ranges': get_data_ranges(manager)
        }
    
    # 保存结果
    with open(golden_dir / "inference_results.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"黄金数据已保存到 {golden_dir}")

def serialize_result(result):
    """序列化推理结果"""
    return {
        'output_shape': result.output.shape,
        'output_min': float(np.min(result.output)),
        'output_max': float(np.max(result.output)),
        'output_mean': float(np.mean(result.output)),
        'output_std': float(np.std(result.output)),
        'output_samples': result.output[:10].tolist()  # 前10个样本
    }
```

### 3.2 黄金主测试基类

```python
# tests/conftest.py
import pytest
import json
from pathlib import Path

class GoldenMasterTest:
    """黄金主测试基类"""
    
    @pytest.fixture(scope="class")
    def golden_data(self):
        """加载黄金标准数据"""
        golden_path = Path("tests/golden_data/inference_results.json")
        if not golden_path.exists():
            pytest.skip("黄金数据不存在，请先运行 generate_golden_data.py")
        
        with open(golden_path) as f:
            return json.load(f)
    
    def assert_results_match(self, actual, expected, tolerance=1e-6):
        """验证结果匹配"""
        import numpy as np
        
        # 检查形状
        assert actual.shape == tuple(expected['output_shape'])
        
        # 检查统计值
        np.testing.assert_allclose(
            np.min(actual), expected['output_min'], 
            rtol=tolerance
        )
        np.testing.assert_allclose(
            np.max(actual), expected['output_max'], 
            rtol=tolerance
        )
        np.testing.assert_allclose(
            np.mean(actual), expected['output_mean'], 
            rtol=tolerance
        )
        
        # 检查样本值
        actual_samples = actual[:10].tolist()
        expected_samples = expected['output_samples']
        np.testing.assert_allclose(
            actual_samples, expected_samples, 
            rtol=tolerance
        )
```

## 4. 增量测试策略

### 4.1 特征开关测试

```python
# tests/test_feature_flags.py
import pytest
from unittest.mock import patch

class TestFeatureFlags:
    """测试特征开关功能"""
    
    @pytest.mark.parametrize("use_new_backend", [True, False])
    def test_backend_switching(self, use_new_backend):
        """测试新旧后端切换"""
        with patch.dict('os.environ', {'USE_NEW_INFERENCE_BACKEND': str(use_new_backend)}):
            from inference.processor import get_backend
            
            backend = get_backend('spice')
            
            if use_new_backend:
                assert backend.__module__ == 'inference.backends.spice'
            else:
                assert backend.__module__ == 'inference.inference_backends'
```

### 4.2 A/B测试框架

```python
# tests/test_ab_comparison.py
import pytest
import numpy as np

class TestABComparison:
    """A/B测试比较新旧实现"""
    
    def test_inference_results_comparison(self, test_data):
        """比较新旧实现的推理结果"""
        from inference.processor import InferenceProcessor as OldProcessor
        from inference.refactored.processor import InferenceProcessor as NewProcessor
        
        old_proc = OldProcessor()
        new_proc = NewProcessor()
        
        # 运行推理
        old_result = old_proc.process(test_data)
        new_result = new_proc.process(test_data)
        
        # 详细比较
        differences = self.analyze_differences(old_result, new_result)
        
        # 生成报告
        self.generate_comparison_report(differences)
        
        # 断言差异在可接受范围内
        assert differences['max_absolute_diff'] < 1e-6
        assert differences['max_relative_diff'] < 1e-4
    
    def analyze_differences(self, old_result, new_result):
        """分析结果差异"""
        diff = np.abs(old_result - new_result)
        
        return {
            'max_absolute_diff': np.max(diff),
            'mean_absolute_diff': np.mean(diff),
            'max_relative_diff': np.max(diff / (np.abs(old_result) + 1e-10)),
            'num_different_elements': np.sum(diff > 1e-10)
        }
```


## 5. 测试执行计划

### 5.1 测试执行顺序

1. **阶段1：基准建立**
   ```bash
   # 生成黄金数据
   python scripts/generate_golden_data.py
   ```

2. **阶段2：单元测试**
   ```bash
   # 测试新的工具类
   pytest tests/test_common/ -v
   ```

3. **阶段3：集成测试**
   ```bash
   # 测试完整流程
   pytest tests/test_integration/ -v
   ```

4. **阶段4：回归测试**
   ```bash
   # 验证与黄金数据的一致性
   pytest tests/test_golden_master/ -v
   ```

### 5.2 测试报告模板

```markdown
# 重构测试报告

## 测试概况
- 测试日期：YYYY-MM-DD
- 测试版本：commit_hash
- 测试环境：Python 3.9, TensorFlow 2.6

## 测试结果

### 功能测试
- [ ] 单元测试通过率：XX%
- [ ] 集成测试通过率：XX%
- [ ] 回归测试通过率：XX%

### 兼容性测试
- 输出差异：最大相对误差 X.Xe-X
- 行为一致性：100%

## 问题与风险
1. 问题描述...
2. 解决方案...

## 结论
- [ ] 可以继续下一阶段
- [ ] 需要修复问题后重测
```

## 6. 测试维护指南

### 6.1 添加新测试
1. 识别新的关键行为
2. 在黄金数据中添加对应案例
3. 编写测试验证行为一致性

### 7.2 更新测试
1. 当功能需求变更时，先更新测试
2. 确保测试失败
3. 修改代码使测试通过
4. 更新黄金数据（如果需要）

### 7.3 测试文档
- 每个测试类都要有清晰的文档字符串
- 复杂的测试逻辑要添加注释
- 维护测试用例清单