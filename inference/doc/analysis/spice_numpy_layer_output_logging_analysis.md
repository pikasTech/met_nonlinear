# SPICE/NumPy层输出数据范围日志缺失分析与改进方案

## 问题描述

从推理日志观察到：
- **NN推理**：正确输出了每层的数据范围（如"第1层输出范围: 最小值=-1.213078, 最大值=1.197002"）
- **SPICE/NumPy推理**：缺少每层数据范围的日志，只有仿真进度和文件保存信息

## 问题分析

### 1. NN推理的日志来源
在`inference/inference_backends.py`的`LayerByLayerBackend`中，第499-505行添加了数据范围日志：
```python
layer_min, layer_max = float('inf'), float('-inf')
for record in layer_output.records:
    data = record.data.flatten()
    layer_min = min(layer_min, data.min())
    layer_max = max(layer_max, data.max())
print(f"  第{layer_idx + 1}层输出范围: 最小值={layer_min:.6f}, 最大值={layer_max:.6f}")
```

### 2. SPICE/NumPy推理日志缺失原因
- SPICE推理的数据流：SPICEBackend.infer → 返回WaveData列表 → data_processing._handle_mixed_output → 保存文件
- 在`_handle_mixed_output`方法中，只处理了文件保存，没有计算和输出数据范围
- NumPy输出也有同样的问题

## 改进方案

### 最小化修改原则
在`inference/data_processing.py`的相关方法中添加数据范围计算和日志输出，保持与NN推理一致的日志格式。

### 具体修改点

#### 1. 添加辅助方法计算WaveData的数据范围
```python
def _log_layer_data_range(self, layer_output, layer_idx):
    """计算并输出层数据范围"""
    layer_min, layer_max = float('inf'), float('-inf')
    for record in layer_output.records:
        data = record.data.flatten()
        layer_min = min(layer_min, data.min())
        layer_max = max(layer_max, data.max())
    print(f"  第{layer_idx + 1}层输出范围: 最小值={layer_min:.6f}, 最大值={layer_max:.6f}")
```

#### 2. 在_handle_mixed_output中添加日志
在保存SPICE层文件的循环中：
```python
for i, layer_output in enumerate(spice_outputs):
    # 输出数据范围
    self._log_layer_data_range(layer_output, i)
    
    # 检查WaveNet5相位修正标记
    if layer_output.user_metadata.get('wavenet5_phase_corrected'):
        print(f"  第{i+1}层已应用WaveNet5相位修正")
```

NumPy层也做相同处理。

#### 3. 在_handle_layer_output中保持一致
虽然这个方法主要用于NN推理（已经有日志），但为了代码一致性，也可以在这里使用相同的方法。

## 实施步骤

1. 在`data_processing.py`中添加`_log_layer_data_range`方法
2. 在`_handle_mixed_output`的SPICE和NumPy处理循环中调用该方法
3. 测试验证日志输出是否正确

## 预期效果

修改后的日志输出示例：
```
正在对第 1/5 层进行 SPICE 仿真...
批量仿真完成，总耗时: 20.7秒，平均每批次耗时: 0.1秒
正在对第 1/5 层进行 NumPy 仿真...
...
对第5层（最终输出层）应用反缩放器
已完成分层输出处理（仅最后一层反缩放）
  第1层输出范围: 最小值=-1.234567, 最大值=1.234567  # 新增
  第1层已应用WaveNet5相位修正
正在保存推理结果到: projects/WNET5q1h2u6l3/data/inference\spice_layers\layer_1.wave
  第2层输出范围: 最小值=0.000000, 最大值=3.456789  # 新增
正在保存推理结果到: projects/WNET5q1h2u6l3/data/inference\spice_layers\layer_2.wave
...
```

## 优势

1. **最小化修改**：只需添加一个方法和几行调用代码
2. **统一性**：所有推理路径的日志格式保持一致
3. **可维护性**：数据范围计算逻辑集中在一个方法中
4. **无破坏性**：不影响现有功能，只是增加日志输出