# 偏置调整功能实施更新

## 当前发现

1. **配置传递成功**: `inference_config` 已成功传递到模型
2. **层结构问题**: Keras层没有直接的 `biases` 属性
3. **SPICE生成流程**: 偏置补偿需要在SPICE电路生成时应用

## 实施方案调整

### 原方案问题
- 试图在Keras层上设置 `bias_compensation` 属性失败
- Keras层是不可变的，不能随意添加属性

### 新方案：运行时偏置调整

#### 方案A：在SPICE生成时调整偏置值
```python
# 在wavenet5_spice_backend.py中重写generate_spice_model方法
def generate_spice_model(self, layer, layer_idx):
    # 获取原始SPICE模型
    spice_model = super().generate_spice_model(layer, layer_idx)
    
    # 如果启用了偏置补偿，修改SPICE模型的偏置值
    if self.is_bias_compensation_enabled():
        adjustment = self.get_bias_adjustment_for_layer(layer_idx)
        if adjustment is not None:
            spice_model.apply_bias_adjustment(adjustment)
    
    return spice_model
```

#### 方案B：Hook机制（推荐）
在SPICE后端中添加一个偏置调整的hook：

```python
class WaveNet5SPICEBackend(SPICEBackend):
    def __init__(self, model=None, output_folder='./temp/spice_output', ngspice_path=None):
        super().__init__(model, output_folder, ngspice_path)
        self.model_type = 'WaveNet5'
        self._bias_adjustments = {}
        self._prepare_bias_adjustments()
    
    def _prepare_bias_adjustments(self):
        """准备偏置调整映射"""
        if hasattr(self.model, 'inference_config'):
            bias_config = self.model.inference_config.get('bias_compensation', {})
            if bias_config.get('enabled', False):
                # 构建层名到偏置调整的映射
                for layer_idx in range(len(self.model.model.layers)):
                    adjustment = self._get_adjustment_for_layer(layer_idx, bias_config)
                    if adjustment is not None:
                        self._bias_adjustments[layer_idx] = adjustment
    
    def get_layer_bias_adjustment(self, layer_idx):
        """获取特定层的偏置调整值"""
        return self._bias_adjustments.get(layer_idx, None)
```

## 下一步行动

1. 实现偏置调整hook机制
2. 在SPICE电路生成时应用调整
3. 验证调整效果

## 技术债务记录

- 需要重构SPICE生成流程以更好地支持运行时参数调整
- 考虑为所有模型添加统一的推理配置接口