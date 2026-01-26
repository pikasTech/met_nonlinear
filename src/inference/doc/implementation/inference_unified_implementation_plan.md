# WaveNet5 推理架构激进重构实施计划

## 执行摘要

本计划详细描述了如何一次性重构推理架构，彻底删除旧接口，统一使用 `InferenceResult` 数据结构。预计工作量：2-3天开发，1天测试。

## 一、改动范围分析

### 1.1 核心改动文件

| 文件 | 改动类型 | 风险等级 |
|------|---------|----------|
| `inference/unified.py` | **新增** | 低 |
| `inference/data_processing.py` | **重写** | 高 |
| `inference/manager.py` | **重构** | 高 |
| `inference/processor.py` | **修改** | 中 |
| `inference/cli.py` | **适配** | 中 |
| `inference.py` | **适配** | 中 |
| `inference/visualizer.py` | **新增方法** | 低 |

### 1.2 影响范围统计

- **直接调用 `infer_and_save` 的位置**：3处
- **处理返回值的代码块**：5处
- **需要更新的测试文件**：预计5-8个
- **特殊逻辑处理点**：4处（WaveNet5相位修正、选择性反缩放、记录ID管理、元数据）

## 二、新的统一数据结构

### 2.1 核心数据模型

```python
# inference/unified.py

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from calibration_analyzer.wavedata import WaveData
import numpy as np

@dataclass
class DataRange:
    """数据范围统计"""
    min_value: float
    max_value: float
    mean_value: float
    std_value: float
    
    @classmethod
    def from_wavedata(cls, wavedata: WaveData) -> 'DataRange':
        """从WaveData计算数据范围"""
        all_data = []
        for record in wavedata.records:
            all_data.append(record.data.flatten())
        data = np.concatenate(all_data)
        return cls(
            min_value=float(data.min()),
            max_value=float(data.max()),
            mean_value=float(data.mean()),
            std_value=float(data.std())
        )

@dataclass
class LayerInfo:
    """单层推理信息"""
    layer_index: int
    layer_name: str
    data: WaveData
    data_range: DataRange
    is_scaled: bool  # 是否处于缩放状态
    file_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class InferenceResult:
    """统一的推理结果容器"""
    # 基本信息
    backend_type: str  # 'nn', 'spice', 'numpy'
    model_name: str
    input_path: str
    output_dir: str
    
    # 推理结果
    layers: List[LayerInfo]  # 始终使用列表，单层时长度为1
    
    # 混合输出支持（SPICE + NumPy）
    numpy_layers: Optional[List[LayerInfo]] = None
    
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # 性能指标
    inference_time_ms: float = 0.0
    
    def get_final_output(self) -> LayerInfo:
        """获取最终输出（最后一层）"""
        return self.layers[-1]
    
    def has_numpy_output(self) -> bool:
        """是否包含NumPy输出"""
        return self.numpy_layers is not None
    
    def validate(self):
        """验证数据完整性，发现问题立即报错"""
        if not self.layers:
            raise ValueError("推理结果不能为空")
        
        if self.backend_type not in ['nn', 'spice', 'numpy']:
            raise ValueError(f"不支持的后端类型: {self.backend_type}")
        
        for i, layer in enumerate(self.layers):
            if layer.layer_index != i:
                raise ValueError(f"层索引不连续: 期望{i}, 实际{layer.layer_index}")
            
            if not layer.data or not layer.data.records:
                raise ValueError(f"第{i}层数据为空")
```

## 三、具体改动方案

### 3.1 新增统一处理器（inference/unified.py）

```python
# 续前面的数据结构定义...

class UnifiedInferenceProcessor:
    """统一的推理处理器"""
    
    def __init__(self, backend, model_engine):
        self.backend = backend
        self.model_engine = model_engine
        self.scaler = model_engine.scaler if hasattr(model_engine, 'scaler') else None
    
    def process(self, 
                input_wave_path: str,
                output_dir: str,
                use_scaler: bool = False,
                return_layers: bool = False,
                return_numpy: bool = False,
                **kwargs) -> InferenceResult:
        """
        统一的推理处理流程
        
        Args:
            input_wave_path: 输入波形文件路径
            output_dir: 输出目录
            use_scaler: 是否使用缩放器
            return_layers: 是否返回分层结果
            return_numpy: 是否同时进行NumPy推理（仅SPICE后端）
            **kwargs: 其他后端特定参数
            
        Returns:
            InferenceResult: 统一格式的推理结果
        """
        import time
        start_time = time.time()
        
        # 1. 加载输入数据
        input_data = self._load_input(input_wave_path)
        print(f"加载输入数据: {input_wave_path}")
        self._log_data_range(input_data, "输入数据")
        
        # 2. 应用输入缩放
        if use_scaler and self.scaler:
            input_data = self._apply_input_scaling(input_data)
            print("已应用输入缩放")
            self._log_data_range(input_data, "缩放后输入")
        
        # 3. 执行推理
        raw_output = self.backend.infer(
            input_data, 
            return_layers=return_layers,
            return_numpy=return_numpy,
            **kwargs
        )
        
        # 4. 转换为统一格式
        result = self._convert_to_unified(
            raw_output, 
            input_wave_path,
            output_dir,
            use_scaler
        )
        
        # 5. 应用输出处理（包括选择性反缩放）
        if use_scaler and self.scaler:
            self._apply_output_processing(result)
        
        # 6. 保存结果
        self._save_results(result, output_dir)
        
        # 7. 记录性能指标
        result.inference_time_ms = (time.time() - start_time) * 1000
        
        # 8. 验证结果
        result.validate()
        
        return result
    
    def _convert_to_unified(self, raw_output, input_path, output_dir, use_scaler):
        """将后端原始输出转换为统一格式"""
        # 这里处理不同后端的返回值差异
        # 具体实现见下面的详细代码
        pass
    
    def _apply_output_processing(self, result: InferenceResult):
        """应用输出处理，包括选择性反缩放"""
        # 只对最后一层应用反缩放
        final_layer = result.get_final_output()
        if not final_layer.metadata.get('inverse_scaled', False):
            final_layer.data = self._apply_inverse_scaling(final_layer.data)
            final_layer.is_scaled = False
            final_layer.metadata['inverse_scaled'] = True
            print(f"对最终输出层应用反缩放")
            self._log_data_range(final_layer.data, f"反缩放后的第{final_layer.layer_index + 1}层")
        
        # 如果有NumPy输出，也只对最后一层反缩放
        if result.has_numpy_output():
            numpy_final = result.numpy_layers[-1]
            if not numpy_final.metadata.get('inverse_scaled', False):
                numpy_final.data = self._apply_inverse_scaling(numpy_final.data)
                numpy_final.is_scaled = False
                numpy_final.metadata['inverse_scaled'] = True
```

### 3.2 重写 InferenceDataProcessor（inference/data_processing.py）

主要改动：
1. 删除 `_handle_mixed_output`、`_handle_layer_output`、`_handle_single_output` 方法
2. 重写 `infer_and_save` 方法，只返回 `InferenceResult`
3. 删除所有 isinstance 类型判断

```python
# inference/data_processing.py 的修改

def infer_and_save(self, 
                   input_wave_path: str, 
                   output_wave_path: str = None,  # 保留参数但标记废弃
                   **kwargs) -> InferenceResult:
    """
    执行推理并保存结果
    
    Args:
        input_wave_path: 输入波形文件路径
        output_wave_path: [已废弃] 输出路径现在由output_dir决定
        **kwargs: 传递给统一处理器的参数
        
    Returns:
        InferenceResult: 统一的推理结果
        
    Raises:
        ValueError: 如果仍在使用旧的调用方式
    """
    # 检查是否使用了废弃的参数
    if output_wave_path and not kwargs.get('output_dir'):
        raise ValueError(
            "output_wave_path参数已废弃。请使用output_dir参数指定输出目录。\n"
            "示例: infer_and_save(input_path, output_dir='./output')"
        )
    
    # 使用统一处理器
    from .unified import UnifiedInferenceProcessor
    processor = UnifiedInferenceProcessor(self.backend, self.model_engine)
    
    # 获取输出目录
    output_dir = kwargs.pop('output_dir', None)
    if not output_dir:
        raise ValueError("必须指定output_dir参数")
    
    # 执行推理
    result = processor.process(
        input_wave_path,
        output_dir,
        **kwargs
    )
    
    return result
```

### 3.3 修改 InferenceManager（inference/manager.py）

```python
# inference/manager.py 的修改

def run_inference(self, project_name, force=False):
    """运行推理数据生成"""
    # ... 前面的代码保持不变 ...
    
    # 生成推理数据
    print(f"\n生成推理数据...")
    processor = InferenceProcessor(
        self.project_dir,
        project_name,
        self.config
    )
    
    # 执行NN推理（始终生成）
    nn_result = processor.data_processor.infer_and_save(
        input_wave=input_wave,
        output_dir=os.path.join(inference_dir, 'nn_output'),
        use_scaler=True,
        return_layers=False
    )
    
    # 保存NN结果路径（用于后续分析）
    nn_output_path = nn_result.get_final_output().file_path
    
    # 执行SPICE推理（如果模型支持）
    if processor.can_export_spice():
        # 切换到SPICE后端
        processor.set_backend_type('spice')
        
        # 执行SPICE + NumPy混合推理
        spice_result = processor.data_processor.infer_and_save(
            input_wave=input_wave,
            output_dir=inference_dir,
            use_scaler=True,
            return_layers=True,
            return_numpy=True
        )
        
        # 提取SPICE和NumPy的输出路径
        spice_outputs = [layer.file_path for layer in spice_result.layers]
        numpy_outputs = [layer.file_path for layer in spice_result.numpy_layers] if spice_result.has_numpy_output() else []
        
        # 生成误差分析
        self._generate_error_analysis(
            nn_output_path,
            spice_outputs,
            numpy_outputs,
            inference_dir
        )
```

### 3.4 更新调用点（inference/cli.py, inference.py）

```python
# inference/cli.py 的修改

def run_inference(args):
    """运行推理"""
    # ... 前面的代码保持不变 ...
    
    # 执行推理
    result = processor.data_processor.infer_and_save(
        input_wave_path=args.input,
        output_dir=args.output_dir or './output',
        use_scaler=not args.no_scaler,
        return_layers=args.layers
    )
    
    # 输出结果信息
    print(f"\n推理完成:")
    print(f"- 后端类型: {result.backend_type}")
    print(f"- 输出层数: {len(result.layers)}")
    print(f"- 推理耗时: {result.inference_time_ms:.2f}ms")
    
    # 如果有分层输出，显示每层信息
    if len(result.layers) > 1:
        print("\n各层输出:")
        for layer in result.layers:
            print(f"  第{layer.layer_index + 1}层 ({layer.layer_name}):")
            print(f"    数据范围: [{layer.data_range.min_value:.6f}, {layer.data_range.max_value:.6f}]")
            print(f"    文件路径: {layer.file_path}")
```

## 四、风险控制措施

### 4.1 特殊逻辑保留策略

| 特殊逻辑 | 原位置 | 新位置 | 保留方式 |
|---------|--------|--------|----------|
| WaveNet5相位修正 | WaveNet5SPICEBackend | 保持不变 | 通过metadata传递标记 |
| 选择性反缩放 | _apply_selective_inverse_scaling | UnifiedInferenceProcessor._apply_output_processing | 统一处理 |
| 记录ID管理 | 分散在多处 | UnifiedInferenceProcessor | 集中管理 |
| 数据范围日志 | _log_layer_data_range | UnifiedInferenceProcessor._log_data_range | 统一接口 |

### 4.2 错误处理增强

```python
class InferenceError(Exception):
    """推理错误基类"""
    pass

class LegacyAPIError(InferenceError):
    """使用废弃API时的错误"""
    def __init__(self, message):
        super().__init__(
            f"检测到使用已废弃的API:\n{message}\n"
            "请参考 documentation/inference_migration_guide.md 进行迁移"
        )

class InvalidReturnFormatError(InferenceError):
    """返回格式不正确时的错误"""
    pass
```

### 4.3 迁移辅助工具

```python
# inference/migration_helper.py

def check_legacy_usage(code_path):
    """检查代码中的旧API使用"""
    legacy_patterns = [
        r'isinstance\(.*,\s*dict\)',
        r'isinstance\(.*,\s*list\)',
        r'output\[.spice.\]',
        r'output\[.numpy.\]',
        r'to_legacy_format',
    ]
    
    issues = []
    # 扫描代码找出所有旧模式使用
    return issues

def generate_migration_report(project_path):
    """生成迁移报告"""
    # 扫描整个项目，生成需要修改的位置列表
    pass
```

## 五、测试计划

### 5.1 单元测试更新

需要更新的测试文件：
- `tests/test_inference_data_processing.py`
- `tests/test_inference_manager.py`
- `tests/test_inference_processor.py`

### 5.2 集成测试

```python
# tests/test_unified_inference.py

def test_nn_inference():
    """测试NN推理返回统一格式"""
    result = processor.infer_and_save(
        input_wave_path="test.wave",
        output_dir="./test_output",
        use_scaler=True
    )
    
    assert isinstance(result, InferenceResult)
    assert result.backend_type == 'nn'
    assert len(result.layers) == 1
    assert not result.has_numpy_output()

def test_spice_mixed_inference():
    """测试SPICE混合推理"""
    result = processor.infer_and_save(
        input_wave_path="test.wave",
        output_dir="./test_output",
        use_scaler=True,
        return_layers=True,
        return_numpy=True
    )
    
    assert isinstance(result, InferenceResult)
    assert result.backend_type == 'spice'
    assert len(result.layers) == 5  # WaveNet5有5层
    assert result.has_numpy_output()
    assert len(result.numpy_layers) == 5

def test_legacy_api_error():
    """测试使用旧API时报错"""
    with pytest.raises(ValueError, match="output_wave_path参数已废弃"):
        processor.infer_and_save(
            input_wave_path="test.wave",
            output_wave_path="output.wave"  # 旧参数
        )
```

### 5.3 回归测试

使用 `conda run -n tf26 python cli.py -i WNET5q1h2u6l3 -f` 进行完整的回归测试，确保：
1. 推理流程正常完成
2. 数据范围日志正确输出
3. 文件保存到正确位置
4. 误差分析正常生成

## 六、实施步骤

### 第1天：核心实现
1. **09:00-10:00**: 创建 `inference/unified.py`，实现数据结构
2. **10:00-12:00**: 实现 `UnifiedInferenceProcessor`
3. **14:00-16:00**: 重写 `InferenceDataProcessor.infer_and_save`
4. **16:00-18:00**: 更新 `InferenceManager`

### 第2天：调用点迁移
1. **09:00-10:00**: 更新 `inference/cli.py` 和 `inference.py`
2. **10:00-12:00**: 更新 `inference/processor.py` 委托方法
3. **14:00-16:00**: 编写迁移辅助工具
4. **16:00-18:00**: 更新单元测试

### 第3天：测试和修复
1. **09:00-12:00**: 运行完整测试套件，修复问题
2. **14:00-16:00**: 进行回归测试
3. **16:00-17:00**: 编写迁移文档
4. **17:00-18:00**: 代码审查和最终提交

## 七、回滚计划

如果出现严重问题需要回滚：
1. 使用 Git 回滚到重构前的提交
2. 恢复时间：< 5分钟
3. 回滚后的补救措施：
   - 分析失败原因
   - 调整实施计划
   - 分阶段实施（可考虑先实施部分功能）

## 八、成功标准

1. **功能完整性**：所有原有功能正常工作
2. **性能指标**：推理性能无明显下降（±5%以内）
3. **代码质量**：
   - 无isinstance类型判断
   - 统一的错误处理
   - 清晰的数据流
4. **测试覆盖**：所有测试通过，覆盖率>80%
5. **文档完整**：迁移指南清晰，API文档更新

## 九、后续优化

完成激进重构后，可以进一步：
1. 添加性能监控和分析功能
2. 实现插件化的处理器架构
3. 支持更多的推理后端
4. 优化内存使用和并行处理