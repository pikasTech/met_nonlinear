# SPICE 偏置补偿详细实施方案

## 实施日期: 2025-07-12

## 一、背景与目标

### 1.1 核心目标
**抑制 SPICE 仿真结果与 NN 推理结果之间的系统性偏差**

### 1.2 基本原则
- NN 推理结果是基准（Ground Truth），误差定义为 0
- SPICE 仿真需要通过参数调整来匹配 NN 结果
- 补偿仅在 SPICE 电路生成阶段应用
- 不修改 NN 推理的任何输出

### 1.3 系统偏差来源
- 运放的非理想特性（偏移电压、有限增益等）
- 电阻值的量化误差（E96/E192 系列）
- 电路的寄生参数
- 数值仿真的精度限制

## 二、技术架构

### 2.1 系统架构图

```
┌─────────────────┐
│   config.json   │
│ (bias_compensation)│
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  WaveNet5 Model │
│ (inference_config) │
└────────┬────────┘
         │
         ↓
┌─────────────────────┐
│ WaveNet5SPICEBackend│
│ (读取补偿配置)      │
└────────┬────────────┘
         │
         ↓
┌──────────────────────┐
│ model.to_spice()     │
│ (WaveNet5.to_spice)  │
└────────┬─────────────┘
         │
         ↓
┌────────────────────────┐
│ layer.to_spice()       │
│ (DenseLayer.to_spice)  │
│ ◆ 应用偏置补偿 ◆      │
└────────┬───────────────┘
         │
         ↓
┌─────────────────┐
│ SPICE Circuit   │
│ (调整后的参数)  │
└─────────────────┘
```

### 2.2 数据流

1. **配置读取**：从 config.json 读取 bias_compensation 配置
2. **配置传递**：通过 inference_config 传递到模型
3. **补偿准备**：SPICE 后端准备各层的补偿值
4. **补偿应用**：在 DenseLayer.to_spice() 中应用补偿
5. **电路生成**：生成带有调整参数的 SPICE 电路

## 三、详细实施步骤

### 3.1 第一步：修正 WaveNet5SPICEBackend

**文件**: `inference/wavenet5_spice_backend.py`

**修改内容**:

1. **删除错误的 _prepare_spice_model 方法**
   
   删除第 35-67 行的整个方法，因为它试图修改 Keras 层。

2. **重写 export_model_to_spice 方法**

```python
def export_model_to_spice(self, output_path=None):
    """
    导出模型到 SPICE 时应用偏置补偿
    
    参数:
        output_path: 输出 SPICE 模型文件路径
        
    返回:
        SPICE 模型对象或对象列表
    """
    # 准备偏置补偿数据
    bias_compensations = self._prepare_bias_compensations()
    
    # 应用补偿到相应的层
    self._apply_compensations_to_layers(bias_compensations)
    
    try:
        # 调用父类方法执行实际的 SPICE 导出
        result = super().export_model_to_spice(output_path)
    finally:
        # 清理临时补偿属性
        self._cleanup_compensations()
    
    return result

def _prepare_bias_compensations(self):
    """
    从 inference_config 准备各层的偏置补偿值
    
    返回:
        Dict[int, Any]: 层索引到补偿值的映射
    """
    compensations = {}
    
    if hasattr(self.model, 'inference_config'):
        bias_config = self.model.inference_config.get('bias_compensation', {})
        
        if bias_config.get('enabled', False):
            logger.info("🔧 准备 SPICE 偏置补偿")
            
            # 1. 获取层特定的补偿
            layer_adjustments = bias_config.get('layer_bias_adjustments', {})
            for layer_idx, adjustment in layer_adjustments.items():
                idx = int(layer_idx)
                compensations[idx] = adjustment
                logger.info(f"   层 {idx}: {adjustment}")
            
            # 2. 获取全局补偿矩阵（作为后备）
            global_matrix = bias_config.get('bias_adjustment_matrix', [])
            for i, value in enumerate(global_matrix):
                if i not in compensations and value is not None:
                    compensations[i] = value
                    logger.info(f"   层 {i}: {value} (来自全局矩阵)")
    
    return compensations

def _apply_compensations_to_layers(self, compensations):
    """
    将补偿值应用到相应的层
    
    参数:
        compensations: 层索引到补偿值的映射
    """
    if not compensations:
        return
    
    if hasattr(self.model, 'layer_to_layer_models'):
        layer_models = self.model.layer_to_layer_models
        
        # 找出 DenseLayer 的索引
        dense_layer_indices = []
        for i, layer in enumerate(layer_models):
            layer_type = type(layer).__name__
            if 'Dense' in layer_type:
                dense_layer_indices.append(i)
                logger.info(f"   发现 DenseLayer 在索引 {i}: {layer.name}")
        
        # 应用补偿到 DenseLayer
        for dense_idx, layer_idx in enumerate(dense_layer_indices):
            if dense_idx in compensations:
                layer = layer_models[layer_idx]
                layer._temp_bias_compensation = compensations[dense_idx]
                logger.info(f"   ✓ 应用补偿到 {layer.name}: {compensations[dense_idx]}")

def _cleanup_compensations(self):
    """清理临时补偿属性"""
    if hasattr(self.model, 'layer_to_layer_models'):
        for layer in self.model.layer_to_layer_models:
            if hasattr(layer, '_temp_bias_compensation'):
                delattr(layer, '_temp_bias_compensation')
```

3. **修改 infer 方法**

删除第 85 行的 `self._prepare_spice_model()` 调用，因为补偿现在在 export_model_to_spice 中处理。

### 3.2 第二步：增强 DenseLayer 的补偿处理

**文件**: `models/model_layers.py`

**修改内容**:

在 DenseLayer.to_spice 方法中增强补偿处理逻辑：

```python
# 在第 428 行之后，增强补偿处理
if bias_vector is not None:
    bias_vector = bias_vector * amp  # 偏置向量放大
    
    # 🔧 应用 SPICE 偏置补偿（仅用于 SPICE 电路生成）
    if hasattr(self, '_temp_bias_compensation'):
        compensation = self._temp_bias_compensation
        
        # 处理不同格式的补偿值
        if isinstance(compensation, (list, tuple)):
            # 列表格式：每个输出单元一个补偿值
            compensation = np.array(compensation)
            if len(compensation) != len(bias_vector):
                logger.warning(f"补偿值数量 ({len(compensation)}) 与偏置数量 ({len(bias_vector)}) 不匹配")
                # 截断或填充
                if len(compensation) < len(bias_vector):
                    compensation = np.pad(compensation, (0, len(bias_vector) - len(compensation)))
                else:
                    compensation = compensation[:len(bias_vector)]
        elif isinstance(compensation, (int, float)):
            # 标量格式：应用到所有输出单元
            compensation = np.full_like(bias_vector, compensation)
        else:
            compensation = np.array(compensation)
        
        logger.info(f"SPICE 偏置补偿 - {self.layer_name}:")
        logger.info(f"  原始偏置: {bias_vector}")
        logger.info(f"  补偿值: {compensation}")
        
        bias_vector = bias_vector + compensation
        
        logger.info(f"  调整后偏置: {bias_vector}")
else:
    bias_vector = None
```

### 3.3 第三步：配置文件示例

**文件**: `projects/WNET5q1h2u6l3/config.json`

确保配置文件包含正确的偏置补偿结构：

```json
{
    "inference_config": {
        "bias_compensation": {
            "enabled": true,
            "bias_adjustment_matrix": [0.5, -0.8, 0.3],
            "layer_bias_adjustments": {
                "0": [0.2, -0.3, 0.1, 0.4],
                "1": [-0.5, 0.7, -0.2],
                "2": [0.3, -0.4, 0.6, -0.1]
            }
        }
    }
}
```

配置说明：
- `enabled`: 是否启用偏置补偿
- `bias_adjustment_matrix`: 全局补偿值（每层一个标量）
- `layer_bias_adjustments`: 层特定的补偿值（每个输出单元一个值）

### 3.4 第四步：添加诊断日志

在关键位置添加日志，便于调试和验证：

1. **配置读取时**：记录读取到的补偿配置
2. **补偿应用时**：记录应用到哪个层
3. **电路生成时**：记录调整前后的参数值

## 四、验证方案

### 4.1 单元测试

创建测试脚本验证补偿机制：

```python
# test_spice_bias_compensation.py
import json
import numpy as np
from inference.wavenet5_spice_backend import WaveNet5SPICEBackend

def test_bias_compensation():
    """测试 SPICE 偏置补偿功能"""
    
    # 1. 创建测试配置
    config = {
        "inference_config": {
            "bias_compensation": {
                "enabled": True,
                "layer_bias_adjustments": {
                    "0": [1.0, -1.0, 0.5],
                    "1": [0.2, -0.3]
                }
            }
        }
    }
    
    # 2. 初始化后端
    backend = WaveNet5SPICEBackend(model=test_model)
    
    # 3. 导出 SPICE 模型
    spice_models = backend.export_model_to_spice()
    
    # 4. 验证补偿被应用
    # 检查生成的 SPICE 文件中的偏置值
    
    return verification_results
```

### 4.2 集成测试

1. **对比测试**：
   - 运行相同输入的 NN 推理
   - 运行无补偿的 SPICE 推理
   - 运行有补偿的 SPICE 推理
   - 比较输出差异

2. **极端值测试**：
   - 使用极大补偿值（±10）
   - 验证 SPICE 输出显著变化
   - 验证 NN 输出保持不变

### 4.3 验证检查点

- [ ] 补偿配置正确读取
- [ ] 补偿值正确传递到 DenseLayer
- [ ] SPICE 电路文件中偏置值已调整
- [ ] SPICE 仿真输出反映补偿效果
- [ ] NN 推理结果未受影响

## 五、风险评估与缓解

### 5.1 潜在风险

1. **补偿值格式不匹配**：层输出维度与补偿值数量不一致
   - 缓解：添加格式验证和自动适配

2. **过度补偿**：补偿值过大导致电路不稳定
   - 缓解：添加补偿值范围检查

3. **性能影响**：额外的处理步骤
   - 缓解：仅在 SPICE 导出时应用，不影响 NN 推理

### 5.2 回滚计划

如果实施出现问题：
1. 通过设置 `enabled: false` 禁用功能
2. 移除临时属性相关代码
3. 恢复原始 SPICE 导出逻辑

## 六、时间表

1. **第 1 天**：实施代码修改
2. **第 2 天**：单元测试和调试
3. **第 3 天**：集成测试和验证
4. **第 4 天**：文档更新和代码审查
5. **第 5 天**：最终验证和部署

## 七、成功标准

1. **功能性**：
   - 偏置补偿配置能正确读取和应用
   - SPICE 电路参数反映补偿值
   - SPICE 仿真结果更接近 NN 基准

2. **兼容性**：
   - 不影响现有功能
   - 向后兼容旧配置
   - 可通过配置开关控制

3. **可维护性**：
   - 代码清晰，易于理解
   - 充分的日志和文档
   - 便于未来扩展

## 八、总结

这个实施方案：
1. 正确理解了 NN 作为基准的原则
2. 在正确的位置（SPICE 电路生成）应用补偿
3. 提供了完整的实施步骤和验证方案
4. 考虑了风险和回滚策略

通过这个方案，我们能够有效地补偿 SPICE 仿真与 NN 推理之间的系统性偏差，提高 SPICE 模型的准确性。