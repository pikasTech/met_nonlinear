# WaveNet5 偏置调整功能修复方案

> ⚠️ **重要更新 (2025-07-12)**：
> 
> 本文档的部分内容已被更正。虽然"最小上下文原则"是正确的，
> 但偏置调整应该仅在 SPICE 电路生成时应用，而不是在通用推理层面。
> 
> 请参考最新的正确实施方案：
> - `20250712_spice_bias_compensation_correct_plan.md`
> - `20250712_spice_bias_compensation_implementation_report.md`

## 修复原则

遵循**最小上下文原则**，只传递必要的`inference_config`，而非整个config对象。

## 修复方案：最小权限传递

### 1. 修改 ModelEngine (core/model_engine.py)

```python
# 在 build_model() 方法中，传递 inference_config
elif 'WaveNet' in self.config.use_model:
    mod_class = eval(self.config.use_model)
    self.model_comp = mod_class(
        fs=self.config.sample_rate,
        checkpoint_dir=self.checkpoint_dir,
        kernel_units=self.config.kernal_units,
        activation=self.config.activation,
        model_subcfg=self.config.model_subcfg,
        inference_config=self.config.inference_config,  # ← 只传递推理配置
    )
```

### 2. 修改 WaveNet5 模型 (models/wavenet_models.py)

```python
class WaveNet5(BaseModel, LayeredModelSupport, SpiceModelSupport):
    def __init__(self,
                 fs=2000,
                 checkpoint_dir='data',
                 kernel_units=4,
                 activation=None,
                 model_subcfg={},
                 inference_config=None,  # ← 新增参数
                 ):
        # 存储推理配置
        self.inference_config = inference_config or {
            'bias_compensation': {
                'enabled': False,
                'bias_adjustment_matrix': None,
                'layer_bias_adjustments': {}
            }
        }
        
        # 原有初始化代码...
```

### 3. 修改 SPICE 后端调用 (inference/wavenet5_spice_backend.py)

```python
def _prepare_spice_model(self):
    """准备SPICE模型时应用偏置补偿"""
    # 获取推理配置中的偏置补偿
    if hasattr(self.model, 'inference_config'):
        bias_config = self.model.inference_config.get('bias_compensation', {})
        if bias_config.get('enabled', False):
            for idx, layer in enumerate(self.model.layers):
                if hasattr(layer, 'biases') and layer.biases is not None:
                    # 获取该层的补偿值
                    layer_adjustments = bias_config.get('layer_bias_adjustments', {})
                    layer_compensation = layer_adjustments.get(str(idx))
                    
                    # 如果没有层特定的补偿，使用全局矩阵
                    if layer_compensation is None:
                        global_matrix = bias_config.get('bias_adjustment_matrix')
                        if global_matrix and idx < len(global_matrix):
                            layer_compensation = global_matrix[idx]
                    
                    if layer_compensation is not None:
                        # 传递给SPICE电路生成
                        layer.bias_compensation = {
                            i: comp for i, comp in enumerate(layer_compensation)
                        }
```

### 4. 为 BaseModel 添加辅助方法 (可选)

```python
class BaseModel:
    def __init__(self):
        self.use_fast_model = False
        self.inference_config = None  # 默认值
    
    def get_bias_adjustment(self, layer_idx=None):
        """获取偏置调整值的辅助方法"""
        if not hasattr(self, 'inference_config') or not self.inference_config:
            return None
            
        bias_config = self.inference_config.get('bias_compensation', {})
        if not bias_config.get('enabled', False):
            return None
            
        if layer_idx is not None:
            # 先尝试层特定调整
            layer_adjustments = bias_config.get('layer_bias_adjustments', {})
            layer_value = layer_adjustments.get(str(layer_idx))
            if layer_value is not None:
                return layer_value
                
            # 回退到全局矩阵
            global_matrix = bias_config.get('bias_adjustment_matrix')
            if global_matrix and layer_idx < len(global_matrix):
                return global_matrix[layer_idx]
        
        return bias_config.get('bias_adjustment_matrix')
```

## 修复优势

1. **最小权限**: 只传递`inference_config`，不暴露训练相关配置
2. **向后兼容**: `inference_config`参数是可选的，不影响现有代码
3. **清晰职责**: 推理配置与训练配置分离
4. **易于扩展**: 未来可以添加更多推理时配置

## 实施步骤

1. **第一步**: 修改 ModelEngine，为 WaveNet 模型传递 `inference_config`
2. **第二步**: 修改 WaveNet5 接收并存储 `inference_config`
3. **第三步**: 更新 SPICE 后端使用新的配置访问方式
4. **第四步**: 运行极端偏置测试验证修复效果

## 测试验证

```bash
# 1. 配置极端偏置值
# config.json:
{
    "inference_config": {
        "bias_compensation": {
            "enabled": true,
            "bias_adjustment_matrix": [100.0, -100.0, 100.0, -100.0, 100.0, -100.0]
        }
    }
}

# 2. 运行推理测试
conda run -n tf26 python cli.py -p WNET5q1h2u6l3 -i -f -l 2

# 3. 验证输出范围变化
# 期望看到明显的输出范围偏移
```

## 注意事项

1. **其他模型支持**: 此修复也应用于其他需要推理配置的模型（WaveNet1-4等）
2. **配置验证**: 考虑添加 `inference_config` 格式验证
3. **文档更新**: 更新相关文档说明新的参数传递方式

## 风险评估

- **风险级别**: 低
- **影响范围**: 仅影响推理时偏置调整功能
- **回滚方案**: 如果出现问题，可以简单地将 `inference_config=None` 恢复原状

这个方案遵循了最小上下文原则，避免了过度暴露内部实现细节，同时解决了偏置调整功能失效的问题。