# SVF层输出相位归一化实施方案

## 目标

确保SVF层（第一层）的所有输出通道都是正相的，消除HP/BP/LP通道之间的相位不一致性。

## 现状分析

### 当前SVF的相位处理

1. **电路输出特性**：
   - HP通道：电路输出反相
   - BP通道：电路输出正相
   - LP通道：电路输出反相

2. **当前post_process处理**：
   ```python
   # HP (j%3==0) 和 LP (j%3==2) 被反相
   if j % 3 == 0 or j % 3 == 2:
       record.data[:, j] = -record.data[:, j]
   ```

3. **处理后的结果**：
   - HP：反相 → 反相 = 正相
   - BP：正相 → 不处理 = 正相
   - LP：反相 → 反相 = 正相

理论上都是正相，但由于电路仿真和模型训练的差异，实际可能存在问题。

## 解决方案

### 方案：修改SVFLayer的post_process方法

不反转任何通道，让所有通道保持电路的原始输出相位。这样虽然HP/LP是反相的，BP是正相的，但至少保持了一致的处理策略。

## 具体实施

### 修改文件：`models/model_layers.py`

**修改点：SVFLayer.post_process方法（第306-324行）**

```python
def post_process(self, output_wave: WaveData):
    """
    输出的通道顺序是 HP0, BP0, LP0, HP1, BP1, LP1 ...
    为了保持相位一致性，不对任何通道进行反相处理
    """
    # 检查输出波形是否有效
    if output_wave is None or not isinstance(output_wave, WaveData):
        raise ValueError("无效的输出波形数据")
    
    # 不进行任何相位处理，保持原始输出
    # 这样所有通道都保持电路的原始相位
    return output_wave
```

或者，如果需要所有通道都正相：

```python
def post_process(self, output_wave: WaveData):
    """
    输出的通道顺序是 HP0, BP0, LP0, HP1, BP1, LP1 ...
    将所有通道都转换为正相输出
    """
    # 检查输出波形是否有效
    if output_wave is None or not isinstance(output_wave, WaveData):
        raise ValueError("无效的输出波形数据")
    
    # 只反转BP通道，使其与HP/LP保持一致（都变成反相）
    # 然后在后续处理中统一处理
    for i, record in enumerate(output_wave.records):
        if record.data is None:
            raise ValueError("输出波形记录数据不能为空")
        # 反转 BP 通道
        for j in range(record.data.shape[1]):
            if j % 3 == 1:  # BP通道
                record.data[:, j] = -record.data[:, j]
    
    # 现在所有通道都是反相的，统一反相使其都变为正相
    for record in output_wave.records:
        record.data = -record.data
        
    return output_wave
```

## 推荐方案

采用**临时禁用post_process方案**，具体实现：

在`cli.py`的`_generate_inference_data`方法中，在SPICE推理后临时禁用SVF层的post_process：

```python
# SPICE分层推理
processor.set_backend("spice")
processor.backend_type = "spice"
processor._initialize_backend("spice")

# 临时禁用SVF层的post_process
original_post_process = None
if hasattr(processor.model.layers[0], 'post_process') and isinstance(processor.model.layers[0], SVFLayer):
    original_post_process = processor.model.layers[0].post_process
    processor.model.layers[0].post_process = lambda x: x  # 不做任何处理

input_data = processor.load_input_wave(input_wave)
spice_outputs = processor.backend.infer(input_data, use_scaler=True, return_layers=True)

# 恢复原始的post_process
if original_post_process:
    processor.model.layers[0].post_process = original_post_process
```

**优点**：
1. **最小侵入性**：不修改核心模型代码
2. **可逆性**：随时可以恢复原始行为
3. **针对性强**：只影响SPICE推理，不影响正常的神经网络推理
4. **便于测试**：可以快速验证相位问题是否由post_process引起

## 测试验证

1. 修改后运行：
   ```bash
   conda run -n tf26 python cli.py -i WNET5q0.5h2u6l3
   ```

2. 检查输出相位：
   ```python
   # 加载第一层输出
   layer1_nn = load_wave('nn_layers/layer_1.wave')
   layer1_spice = load_wave('spice_layers/layer_1.wave')
   
   # 检查相关性
   for ch in range(6):  # 6个通道
       corr = np.corrcoef(layer1_nn[ch], layer1_spice[ch])[0,1]
       print(f"Channel {ch}: correlation = {corr}")
   ```

3. 如果所有通道相关性都是正的，说明相位一致。

## 具体实施步骤

### 文件修改清单

**修改文件：`cli.py`**

**修改位置：`_generate_inference_data`方法（第404-410行附近）**

原代码：
```python
# SPICE分层推理
processor.set_backend("spice")
processor.backend_type = "spice"
processor._initialize_backend("spice")
input_data = processor.load_input_wave(input_wave)
spice_outputs = processor.backend.infer(input_data, use_scaler=True, return_layers=True)
```

修改为：
```python
# SPICE分层推理
processor.set_backend("spice")
processor.backend_type = "spice"
processor._initialize_backend("spice")

# 临时保存并禁用第一层的post_process（如果是SVF层）
original_post_process = None
first_layer = None

# 获取模型的第一层
if hasattr(processor.model, 'get_layered_models'):
    layers = processor.model.get_layered_models()
    if layers and len(layers) > 0:
        first_layer = layers[0]
elif hasattr(processor.model, 'layer_to_layer_models'):
    if processor.model.layer_to_layer_models:
        first_layer = processor.model.layer_to_layer_models[0]

# 如果第一层是SVF层，临时禁用其post_process
if (first_layer is not None and 
    hasattr(first_layer, 'layer_type') and
    first_layer.layer_type == 'SVF' and
    hasattr(first_layer, 'post_process')):
    original_post_process = first_layer.post_process
    first_layer.post_process = lambda x: x
    print("临时禁用SVF层的post_process以测试相位问题")

input_data = processor.load_input_wave(input_wave)
spice_outputs = processor.backend.infer(input_data, use_scaler=True, return_layers=True)

# 恢复原始的post_process
if original_post_process is not None and first_layer is not None:
    first_layer.post_process = original_post_process
```

### 简化版实现（推荐）

如果确定第一层是SVF层，可以使用更简洁的实现：

```python
# SPICE分层推理
processor.set_backend("spice")
processor.backend_type = "spice"
processor._initialize_backend("spice")

# 获取并暂存原始的to_spice方法
model_to_spice = processor.model.to_spice
svf_layers = []

# 包装to_spice方法以禁用SVF的post_process
def to_spice_no_svf_post(*args, **kwargs):
    spice_objs = model_to_spice(*args, **kwargs)
    if isinstance(spice_objs, list) and len(spice_objs) > 0:
        # 保存第一层（SVF）并禁用其post_process
        if hasattr(spice_objs[0], 'post_process'):
            svf_layers.append(spice_objs[0])
            spice_objs[0].post_process = lambda x: x
            print("已禁用SVF层的post_process")
    return spice_objs

# 临时替换to_spice方法
processor.model.to_spice = to_spice_no_svf_post

input_data = processor.load_input_wave(input_wave)
spice_outputs = processor.backend.infer(input_data, use_scaler=True, return_layers=True)

# 恢复原始方法
processor.model.to_spice = model_to_spice
```

## 代码修改量统计

- 修改文件数：1个（`cli.py`）
- 新增代码行数：约20行
- 修改风险：低（仅在SPICE推理时临时修改）

## 影响评估

1. **对神经网络推理无影响**：只在SPICE推理时生效
2. **可逆性强**：代码自动恢复原始行为
3. **易于调试**：添加了打印信息便于跟踪

## 后续步骤

1. 如果禁用post_process后相位问题解决，说明问题在于SVF的相位处理逻辑
2. 可以进一步细化，只禁用特定通道的相位处理
3. 最终可能需要为SPICE仿真创建专门的相位处理策略

## 注意事项

1. **先备份原文件**：在修改`cli.py`之前，建议先备份
2. **逐步测试**：先只测试SVF层输出，确认相位问题是否解决
3. **保留日志**：记录修改前后的输出对比，便于分析
4. **可选方案**：如果上述方法不奏效，可以尝试在`SPICEBackend.simulate_with_spice`中直接跳过SVF层的post_process调用