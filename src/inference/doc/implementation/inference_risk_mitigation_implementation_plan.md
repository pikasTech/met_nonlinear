# 推理架构统一风险缓解实施方案

## 概述

基于风险分析报告，本方案提供具体的实施步骤和代码示例，以安全地统一SPICE/NumPy推理架构。采用直接切换策略，确保代码清晰简洁。

## 实施阶段划分

### 🟡 第1阶段：扩展infer_and_save（1周）
增强功能以支持SPICE/NumPy的所有特性。

### 🔴 第2阶段：直接迁移SPICE/NumPy（1周）
一次性切换到新架构，不保留旧代码。

### 🟣 第3阶段：清理冗余代码（2天）
移除旧的手动保存逻辑。

## 第1阶段：扩展infer_and_save功能

### 目标
- 添加SPICE/NumPy支持
- 实现完整的错误处理
- 确保所有特性得到支持

### 具体实施

#### 1.1 扩展方法签名

文件：`inference/data_processing.py`

```python
def infer_and_save(self, input_wave_path: str, output_wave_path: str, 
                   layer_output_dir: str = None, use_scaler=False,
                   # 新增参数
                   return_layers: bool = None,  # None表示自动检测
                   return_numpy: bool = False,
                   numpy_output_dir: str = None,
                   save_intermediate: bool = True,  # 是否保存中间结果
                   **kwargs) -> Union[str, List[str], Dict[str, Union[str, List[str]]]]:
    """
    使用当前后端对输入波形进行推理并保存结果（增强版）
    
    参数:
        input_wave_path: 输入波形文件路径
        output_wave_path: 输出波形文件路径
        layer_output_dir: 分层输出目录路径
        use_scaler: 是否使用缩放器
        return_layers: 是否返回分层结果（None=自动检测）
        return_numpy: 是否同时进行NumPy仿真（SPICE后端专用）
        numpy_output_dir: NumPy输出目录路径
        save_intermediate: 是否保存中间层结果
        **kwargs: 传递给后端的额外参数
    
    返回:
        保存的文件路径（格式取决于输出类型）
    """
```

#### 1.2 添加后端类型检测

```python
    # 自动检测return_layers参数
    if return_layers is None:
        # 如果提供了layer_output_dir，则启用分层返回
        return_layers = layer_output_dir is not None
    
    # 检测后端类型
    backend_type = getattr(self.processor, 'backend_type', 'unknown')
    is_spice_backend = backend_type.lower() == 'spice'
    
    # 验证参数组合
    if return_numpy and not is_spice_backend:
        raise ValueError(f"return_numpy=True仅对SPICE后端有效，当前后端：{backend_type}")
```

#### 1.3 统一缩放处理

```python
    # 加载并应用缩放（统一在外部处理）
    input_wave_data = self.load_input_wave(input_wave_path)
    
    if use_scaler:
        input_wave_data = self._apply_input_scaling(input_wave_data)
        print("已对输入数据应用缩放器")
    
    # 构建推理参数（统一不在内部处理缩放）
    infer_kwargs = {
        'use_scaler': False,  # 缩放已在外部处理
        **kwargs
    }
    
    # 添加后端特定参数
    if hasattr(self.processor.backend, 'infer'):
        import inspect
        sig = inspect.signature(self.processor.backend.infer)
        params = sig.parameters
        
        if 'return_layers' in params:
            infer_kwargs['return_layers'] = return_layers
        if 'return_numpy' in params and is_spice_backend:
            infer_kwargs['return_numpy'] = return_numpy
    
    # 执行推理
    try:
        output_data = self.processor.backend.infer(input_wave_data, **infer_kwargs)
    except Exception as e:
        print(f"推理过程中发生错误：{str(e)}")
        raise
```

#### 1.4 处理复杂返回值

```python
    # 处理不同类型的返回值
    if isinstance(output_data, dict) and 'spice' in output_data:
        # SPICE + NumPy混合结果
        return self._handle_mixed_output(
            output_data, output_wave_path, layer_output_dir, 
            numpy_output_dir, use_scaler, save_intermediate
        )
    elif isinstance(output_data, list):
        # 分层结果
        return self._handle_layer_output(
            output_data, output_wave_path, layer_output_dir, 
            use_scaler, save_intermediate
        )
    else:
        # 单一结果
        return self._handle_single_output(
            output_data, output_wave_path, use_scaler
        )
```

#### 1.5 实现处理方法

```python
def _handle_mixed_output(self, output_data, output_wave_path, layer_output_dir, 
                        numpy_output_dir, use_scaler, save_intermediate):
    """处理SPICE + NumPy混合输出"""
    spice_outputs = output_data['spice']
    numpy_outputs = output_data.get('numpy', [])
    
    saved_paths = {'spice': [], 'numpy': []}
    
    # 处理SPICE输出
    if spice_outputs:
        # 应用反缩放（仅最后一层）
        if use_scaler and self.model_engine.scaler:
            spice_outputs = self._apply_selective_inverse_scaling(spice_outputs)
        
        # 保存文件
        if save_intermediate and layer_output_dir:
            os.makedirs(layer_output_dir, exist_ok=True)
            for i, layer_output in enumerate(spice_outputs):
                # 检查WaveNet5相位修正标记
                if layer_output.user_metadata.get('wavenet5_phase_corrected'):
                    print(f"  第{i+1}层已应用WaveNet5相位修正")
                
                layer_path = os.path.join(layer_output_dir, f"layer_{i+1}.wave")
                saved_path = self.save_output_wave(layer_output, layer_path)
                saved_paths['spice'].append(saved_path)
        
        # 保存最终输出
        if output_wave_path and spice_outputs:
            final_path = self.save_output_wave(spice_outputs[-1], output_wave_path)
            if 'final' not in saved_paths:
                saved_paths['final'] = final_path
    
    # 处理NumPy输出
    if numpy_outputs:
        if use_scaler and self.model_engine.scaler:
            numpy_outputs = self._apply_selective_inverse_scaling(numpy_outputs)
        
        if save_intermediate and numpy_output_dir:
            os.makedirs(numpy_output_dir, exist_ok=True)
            for i, layer_output in enumerate(numpy_outputs):
                layer_path = os.path.join(numpy_output_dir, f"layer_{i+1}.wave")
                saved_path = self.save_output_wave(layer_output, layer_path)
                saved_paths['numpy'].append(saved_path)
    
    return saved_paths

def _apply_selective_inverse_scaling(self, layer_outputs):
    """选择性地对层输出应用反缩放（仅最后一层）"""
    if not layer_outputs:
        return layer_outputs
    
    processed = []
    for i, layer_output in enumerate(layer_outputs):
        if i == len(layer_outputs) - 1:
            # 最后一层：应用反缩放
            processed.append(self._apply_output_inverse_scaling(layer_output))
        else:
            # 中间层：保持缩放状态
            layer_output.add_user_metadata("scaling_status", "scaled")
            processed.append(layer_output)
    
    return processed
```

## 第2阶段：直接迁移SPICE/NumPy调用

### 目标
- 将manager.py中的SPICE/NumPy推理直接迁移到新架构
- 删除旧的手动保存逻辑
- 确保功能完整性

### 实施步骤

#### 2.1 修改InferenceManager

文件：`inference/manager.py`

```python
def _generate_inference_data(self, data_dir):
    """生成推理数据（统一架构）"""
    # ... 前置代码保持不变
    
    # NN分层推理（保持现有逻辑）
    if model_type.startswith("WaveNet"):
        # ... 现有NN推理代码
    
    # SPICE/NumPy分层推理（新架构）
    print("\n--- SPICE/NumPy推理 ---")
    processor.set_backend("spice")
    
    spice_layers_dir = os.path.join(data_dir, 'spice_layers')
    numpy_layers_dir = os.path.join(data_dir, 'numpy_layers')
    
    # 使用统一的infer_and_save架构
    try:
        results = processor.infer_and_save(
            input_wave,
            None,  # 不需要主输出文件
            layer_output_dir=spice_layers_dir,
            use_scaler=True,
            return_layers=True,
            return_numpy=True,
            numpy_output_dir=numpy_layers_dir,
            save_intermediate=True
        )
        
        # 处理返回结果
        if isinstance(results, dict):
            spice_paths = results.get('spice', [])
            numpy_paths = results.get('numpy', [])
            print(f"SPICE分层推理完成，保存了 {len(spice_paths)} 个文件")
            if numpy_paths:
                print(f"NumPy仿真完成，保存了 {len(numpy_paths)} 个文件")
            
            # 更新元数据
            self._spice_layers = len(spice_paths)
            self._numpy_layers = len(numpy_paths)
        else:
            raise ValueError(f"意外的返回格式：{type(results)}")
            
    except Exception as e:
        print(f"SPICE/NumPy推理失败：{str(e)}")
        raise  # 直接抛出异常，不降级处理
```

#### 2.2 删除旧代码

删除以下部分：
- 手动调用`backend.infer`的代码
- 手动保存文件的循环
- 旧的错误处理逻辑

## 第3阶段：清理冗余代码

### 3.1 移除冗余方法
- 删除手动保存SPICE/NumPy结果的代码块
- 清理不再需要的辅助方法

### 3.2 更新文档
- 更新API文档说明新的调用方式
- 添加迁移指南

## 测试计划

### 单元测试示例
```python
# test_inference_unification.py
import pytest
from inference.data_processing import InferenceDataProcessor

class TestUnifiedInference:
    
    def test_no_double_scaling(self, processor):
        """确保不会双重缩放"""
        # Mock scaler
        processor.model_engine.scaler = Mock()
        processor.model_engine.scaler.transform_x.return_value = np.array([[1.0]])
        processor.model_engine.scaler.inverse_transform_y.return_value = np.array([[2.0]])
        
        # 执行推理
        result = processor.infer_and_save(
            "input.wave", "output.wave", use_scaler=True
        )
        
        # 验证缩放器只被调用一次
        assert processor.model_engine.scaler.transform_x.call_count == 1
        assert processor.model_engine.scaler.inverse_transform_y.call_count == 1
    
    def test_mixed_output_handling(self, processor):
        """测试Dict返回值处理"""
        # Mock backend返回混合结果
        processor.backend.infer.return_value = {
            'spice': [Mock(WaveData), Mock(WaveData)],
            'numpy': [Mock(WaveData), Mock(WaveData)]
        }
        
        # 执行推理
        result = processor.infer_and_save(
            "input.wave", None, 
            layer_output_dir="spice_out",
            return_numpy=True,
            numpy_output_dir="numpy_out"
        )
        
        # 验证返回格式
        assert isinstance(result, dict)
        assert 'spice' in result and 'numpy' in result
        assert len(result['spice']) == 2
        assert len(result['numpy']) == 2
    
    def test_invalid_return_numpy_raises_error(self, processor):
        """测试非SPICE后端使用return_numpy时抛出错误"""
        processor.backend_type = 'nn'
        
        with pytest.raises(ValueError) as exc_info:
            processor.infer_and_save(
                "input.wave", "output.wave",
                return_numpy=True
            )
        
        assert "return_numpy=True仅对SPICE后端有效" in str(exc_info.value)
```

### 集成测试脚本
```bash
#!/bin/bash
# test_unified_inference.sh

echo "=== 测试统一推理架构 ==="

# 运行推理测试
echo "运行推理测试..."
python cli.py -i -f WNET5q1h2u6l3

# 验证输出文件
echo "验证输出文件..."
if [ -d "projects/WNET5q1h2u6l3/data/inference/spice_layers" ]; then
    echo "✓ SPICE分层输出目录存在"
else
    echo "✗ SPICE分层输出目录不存在"
    exit 1
fi

if [ -d "projects/WNET5q1h2u6l3/data/inference/numpy_layers" ]; then
    echo "✓ NumPy分层输出目录存在"
else
    echo "✗ NumPy分层输出目录不存在"
    exit 1
fi

# 验证文件数量
spice_count=$(ls projects/WNET5q1h2u6l3/data/inference/spice_layers/*.wave 2>/dev/null | wc -l)
numpy_count=$(ls projects/WNET5q1h2u6l3/data/inference/numpy_layers/*.wave 2>/dev/null | wc -l)

echo "SPICE层数: $spice_count"
echo "NumPy层数: $numpy_count"

if [ $spice_count -eq 5 ] && [ $numpy_count -eq 5 ]; then
    echo "✓ 文件数量正确"
else
    echo "✗ 文件数量不正确"
    exit 1
fi

echo "=== 测试完成 ==="
```

## 时间表

| 阶段 | 任务 | 预计时间 | 完成标准 |
|------|------|----------|----------|
| 第1阶段 | 扩展infer_and_save | 3天 | 新功能测试通过 |
| 第1阶段 | 添加错误处理 | 2天 | 异常场景覆盖 |
| 第2阶段 | 迁移SPICE/NumPy | 2天 | 功能正常工作 |
| 第2阶段 | 集成测试 | 2天 | 所有测试通过 |
| 第3阶段 | 清理冗余代码 | 1天 | 代码整洁 |
| 第3阶段 | 文档更新 | 1天 | 文档完整 |

## 成功标准

1. ✅ 所有现有测试通过
2. ✅ 统一架构输出正确
3. ✅ 日志输出符合预期
4. ✅ WaveNet5相位修正正确保留
5. ✅ 错误处理清晰明确
6. ✅ 代码结构简洁清晰

通过这个直接切换的实施方案，我们可以快速实现架构统一，同时保持代码的清晰和简洁。