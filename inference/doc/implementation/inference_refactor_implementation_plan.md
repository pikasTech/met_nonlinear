# 推理架构重构实施方案

## 方案概述

基于用户需求的两个关键要求：
1. **只对最后一层做反缩放** - 修复当前NN推理对每层都进行反缩放的问题
2. **SPICE和NumPy推理也应该用infer_and_save架构** - 统一推理接口，获得完整的日志输出

## 当前架构分析

### 现有推理路径对比

#### NN推理路径（完整日志）
```
manager.py:255 -> processor.infer_and_save() 
    ↓
data_processing.py:210 -> infer_and_save()
    ↓ 包含完整的缩放、推理、反缩放、日志流程
    ├─ load_input_wave() + 数据范围日志
    ├─ _apply_input_scaling() + 缩放前后对比日志  
    ├─ backend.infer()
    ├─ _apply_output_inverse_scaling() + 反缩放前后对比日志（问题：对每层都执行）
    └─ save_output_wave()
```

#### SPICE/NumPy推理路径（缺失日志）
```
manager.py:271 -> processor.load_input_wave() # 只有数据范围日志
manager.py:274 -> processor.backend.infer()   # 直接调用，跳过data_processing
manager.py:296-310 -> 手动保存文件           # 跳过完整的反缩放和日志流程
```

### 问题根源

1. **反缩放逻辑问题**：
   - 位置：`data_processing.py:238-240`
   - 当前逻辑：`[self._apply_output_inverse_scaling(layer_output) for layer_output in output_data]`
   - 问题：对分层推理的每一层都执行反缩放和日志输出
   - 正确逻辑：应该只对最后一层（用于最终输出）执行反缩放

2. **架构不一致问题**：
   - NN推理使用高级API（`infer_and_save`），具有完整的生命周期管理
   - SPICE/NumPy推理使用低级API（`backend.infer` + 手动处理），缺失关键功能

## 详细实施方案

### 方案一：修复反缩放逻辑

#### 目标
只对最后一层（最终输出）进行反缩放，中间层保持原始缩放后的数据。

#### 核心设计理念
- **分层数据保持原始缩放状态**：便于后续分析和调试
- **最终输出进行反缩放**：用户看到的是真实的物理量
- **反缩放日志只打印一次**：避免冗余信息

#### 修改文件清单

##### 1. `/mnt/f/Work/met_nonlinear/inference/data_processing.py`

**修改点1：重构反缩放逻辑（第236-243行）**
```python
# 当前代码（问题）
if use_scaler and hasattr(self.model_engine, 'scaler') and self.model_engine.scaler is not None:
    if isinstance(output_data, list):  # 分层推理返回列表
        output_data = [self._apply_output_inverse_scaling(
            layer_output) for layer_output in output_data]  # 对每层都反缩放
    else:  # 普通推理返回单个WaveData
        output_data = self._apply_output_inverse_scaling(output_data)
    print("已对输出数据应用反缩放器")

# 修改后代码
if use_scaler and hasattr(self.model_engine, 'scaler') and self.model_engine.scaler is not None:
    if isinstance(output_data, list):  # 分层推理返回列表
        # 只对最后一层进行反缩放，用于最终输出
        final_layer_unscaled = self._apply_output_inverse_scaling(output_data[-1])
        # 创建新的输出列表：前面的层保持缩放状态，最后一层反缩放
        output_data = output_data[:-1] + [final_layer_unscaled]
    else:  # 普通推理返回单个WaveData
        output_data = self._apply_output_inverse_scaling(output_data)
    print("已对输出数据应用反缩放器")
```

**修改点2：更新`_apply_output_inverse_scaling`方法签名（第145行）**
```python
# 添加参数控制日志输出
def _apply_output_inverse_scaling(self, output_wave_data: WaveData, show_log: bool = True) -> WaveData:
    # 只有当show_log=True时才打印范围对比日志
    if show_log and self.model_engine.scaler is not None:
        # 现有的日志逻辑
        # ...
    # 其余逻辑保持不变
```

**修改点3：优化保存逻辑（第246-265行）**
```python
# 处理不同类型的输出
if isinstance(output_data, list):  # 分层推理返回列表
    saved_paths = []

    # 保存主输出（最后一层，已反缩放）
    if output_wave_path:
        os.makedirs(os.path.dirname(output_wave_path), exist_ok=True)
        saved_paths.append(self.save_output_wave(
            output_data[-1], output_wave_path))  # 使用已反缩放的最后一层

    # 保存分层结果（包含未反缩放的中间层和已反缩放的最后一层）
    if layer_output_dir:
        os.makedirs(layer_output_dir, exist_ok=True)
        for i, layer_output in enumerate(output_data):
            layer_path = os.path.join(
                layer_output_dir, f"layer_{i+1}.wave")
            saved_paths.append(self.save_output_wave(
                layer_output, layer_path))

    return saved_paths
```

### 方案二：统一SPICE/NumPy推理架构

#### 目标
让SPICE和NumPy推理也使用`infer_and_save`架构，获得完整的日志输出和生命周期管理。

#### 核心设计理念
- **接口统一**：所有推理类型都通过`infer_and_save`入口
- **参数扩展**：`infer_and_save`支持SPICE/NumPy特有的参数
- **后端能力透传**：将SPICE/NumPy的特殊能力（如`return_layers`, `return_numpy`）透传给底层

#### 修改文件清单

##### 1. `/mnt/f/Work/met_nonlinear/inference/data_processing.py`

**修改点1：扩展`infer_and_save`方法签名（第210行）**
```python
def infer_and_save(self, input_wave_path: str, output_wave_path: str, 
                   layer_output_dir: str = None, use_scaler=False,
                   return_layers=False, return_numpy=False, 
                   numpy_output_dir: str = None) -> Union[str, List[str], Dict[str, List[str]]]:
    """
    使用当前后端对输入波形进行推理并保存结果

    参数:
        input_wave_path: 输入波形文件路径
        output_wave_path: 输出波形文件路径
        layer_output_dir: 分层输出目录路径（如果为None则不保存分层结果）
        use_scaler: 是否使用缩放器进行统一预处理和后处理
        return_layers: 是否返回分层结果（SPICE后端专用）
        return_numpy: 是否同时进行NumPy仿真（SPICE后端专用）
        numpy_output_dir: NumPy输出目录路径（如果return_numpy=True且为None则使用layer_output_dir + '_numpy'）

    返回:
        Union[str, List[str], Dict[str, List[str]]]: 保存的输出文件路径
    """
```

**修改点2：更新推理调用逻辑（第233行）**
```python
# 进行推理，传递SPICE/NumPy专用参数
if self.processor.backend_type == "spice":
    # SPICE后端支持额外参数
    output_data = self.processor.backend.infer(
        input_wave_data, use_scaler=False, 
        return_layers=return_layers, return_numpy=return_numpy)
else:
    # 其他后端使用标准接口
    output_data = self.processor.backend.infer(
        input_wave_data, use_scaler=False)
```

**修改点3：添加SPICE/NumPy结果处理逻辑（第245行后）**
```python
# 处理SPICE/NumPy混合返回结果
if isinstance(output_data, dict) and 'spice' in output_data:
    # SPICE + NumPy混合结果
    spice_outputs = output_data['spice']
    numpy_outputs = output_data.get('numpy', [])
    
    # 应用反缩放逻辑（只对最后一层）
    if use_scaler and hasattr(self.model_engine, 'scaler') and self.model_engine.scaler is not None:
        # 对SPICE输出的最后一层进行反缩放
        if spice_outputs:
            final_spice_unscaled = self._apply_output_inverse_scaling(spice_outputs[-1], show_log=True)
            spice_outputs = spice_outputs[:-1] + [final_spice_unscaled]
        
        # 对NumPy输出的最后一层进行反缩放（如果存在）
        if numpy_outputs:
            final_numpy_unscaled = self._apply_output_inverse_scaling(numpy_outputs[-1], show_log=False)
            numpy_outputs = numpy_outputs[:-1] + [final_numpy_unscaled]
    
    # 保存SPICE分层结果
    saved_paths = {'spice': [], 'numpy': []}
    if layer_output_dir and spice_outputs:
        os.makedirs(layer_output_dir, exist_ok=True)
        for i, layer_output in enumerate(spice_outputs):
            layer_path = os.path.join(layer_output_dir, f"layer_{i+1}.wave")
            saved_paths['spice'].append(self.save_output_wave(layer_output, layer_path))
    
    # 保存NumPy分层结果
    if numpy_outputs:
        if numpy_output_dir is None:
            numpy_output_dir = layer_output_dir + '_numpy' if layer_output_dir else None
        if numpy_output_dir:
            os.makedirs(numpy_output_dir, exist_ok=True)
            for i, layer_output in enumerate(numpy_outputs):
                layer_path = os.path.join(numpy_output_dir, f"layer_{i+1}.wave")
                saved_paths['numpy'].append(self.save_output_wave(layer_output, layer_path))
    
    return saved_paths
```

##### 2. `/mnt/f/Work/met_nonlinear/inference/manager.py`

**修改点1：重构SPICE/NumPy推理调用（第266-310行）**
```python
# 原有代码（问题）
# SPICE分层推理（带NumPy支持）
processor.set_backend("spice")
# 需要先调用一次普通推理以获取分层结果
processor.backend_type = "spice"
processor._initialize_backend("spice")
input_data = processor.load_input_wave(input_wave)

# 调用带有return_numpy=True的推理
results = processor.backend.infer(input_data, use_scaler=True, return_layers=True, return_numpy=True)
# ... 手动处理和保存逻辑

# 修改后代码（统一架构）
# SPICE分层推理（带NumPy支持）
processor.set_backend("spice")
spice_numpy_paths = processor.infer_and_save(
    input_wave,
    None,  # 不需要主输出文件
    spice_layers_dir,  # SPICE分层输出目录
    use_scaler=True,
    return_layers=True,
    return_numpy=True,
    numpy_output_dir=os.path.join(data_dir, 'numpy_layers')
)

# 解析返回的路径信息
if isinstance(spice_numpy_paths, dict):
    spice_outputs = spice_numpy_paths.get('spice', [])
    numpy_outputs = spice_numpy_paths.get('numpy', [])
    print(f"SPICE分层推理完成，保存了 {len(spice_outputs)} 个文件")
    if numpy_outputs:
        print(f"NumPy仿真完成，保存了 {len(numpy_outputs)} 个文件")
else:
    # 兼容性处理
    print(f"SPICE分层推理完成，保存了 {len(spice_numpy_paths) if spice_numpy_paths else 0} 个文件")
```

**修改点2：移除重复的手动保存逻辑（删除第296-310行）**
```python
# 删除以下重复代码，因为已经在infer_and_save中处理
# # 直接保存SPICE分层输出（相位修正已在WaveNet5SPICEBackend中处理）
# # 手动保存SPICE分层输出
# os.makedirs(spice_layers_dir, exist_ok=True)
# for i, layer_output in enumerate(spice_outputs):
#     layer_path = os.path.join(spice_layers_dir, f"layer_{i+1}.wave")
#     processor.wave_processor.save_waveform(layer_path, layer_output)
# print(f"SPICE分层推理完成，保存了 {len(spice_outputs)} 个文件")

# # 保存NumPy输出（如果有）
# if numpy_outputs:
#     numpy_layers_dir = os.path.join(data_dir, 'numpy_layers')
#     os.makedirs(numpy_layers_dir, exist_ok=True)
#     for i, layer_output in enumerate(numpy_outputs):
#         layer_path = os.path.join(numpy_layers_dir, f"layer_{i+1}.wave")
#         processor.wave_processor.save_waveform(layer_path, layer_output)
#     print(f"NumPy仿真完成，保存了 {len(numpy_outputs)} 个文件")
```

**修改点3：更新元数据保存逻辑（第315行后）**
```python
# 保存推理元数据
metadata = {
    "project_name": self.project_name,
    "project_path": self.project_path,
    "config": self.config.__dict__,
    "timestamp": self._get_timestamp(),
    "input_file": input_wave,
    "num_layers": len(nn_outputs),
    "nn_layers": len(nn_outputs),
    "spice_layers": len(spice_outputs) if 'spice_outputs' in locals() else 0,
    "numpy_layers": len(numpy_outputs) if 'numpy_outputs' in locals() else 0
}
with open(f'{data_dir}/inference_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2, default=str)
```

##### 3. `/mnt/f/Work/met_nonlinear/inference/inference_backends.py`（可选优化）

**修改点1：优化SPICEBackend的分层日志（第784行）**
```python
# 在SPICE分层推理中添加数据范围日志
for i, spice_obj in enumerate(spice_model):
    print(f"正在对第 {i+1}/{len(spice_model)} 层进行 SPICE 仿真...")
    
    # 执行仿真
    layer_output = self.simulate_with_spice(
        circuit, current_input, output_name=f"layer{i+1}")
    
    # 添加数据范围日志（类似NN推理）
    layer_min, layer_max = float('inf'), float('-inf')
    for record in layer_output.records:
        data = record.data.flatten()
        layer_min = min(layer_min, data.min())
        layer_max = max(layer_max, data.max())
    print(f"  第{i+1}层SPICE输出范围: 最小值={layer_min:.6f}, 最大值={layer_max:.6f}")
    
    # 其余逻辑保持不变
```

## 实施效果预期

### 解决的问题

1. **NN推理反缩放问题**：
   - ✅ 只对最后一层进行反缩放，消除冗余日志
   - ✅ 中间层保持缩放状态，便于调试分析
   - ✅ 反缩放日志只输出一次，提高可读性

2. **SPICE/NumPy推理架构问题**：
   - ✅ 统一使用`infer_and_save`接口，架构一致
   - ✅ 获得完整的缩放、反缩放、数据范围日志
   - ✅ 自动化的文件保存和路径管理
   - ✅ 支持NumPy仿真的完整生命周期

### 预期的日志输出

```
# NN推理（优化后）
正在加载输入波形文件: projects/WNET5q1h2u6l3/data/wave_output/dataset_MET_output_original.wave
已加载波形文件，包含 350 个记录
  数据范围: 最小值=-44.712529, 最大值=42.353128
  缩放前范围: 最小值=-44.712529, 最大值=42.353128
  缩放后范围: 最小值=-1.000000, 最大值=0.947232
已对输入数据应用缩放器
正在处理第 1/5 层
已完成第 1/5 层的推理
  第1层输出范围: 最小值=-1.213078, 最大值=1.197002
# ... 其他层
正在处理第 5/5 层
已完成第 5/5 层的推理
  第5层输出范围: 最小值=-0.907890, 最大值=1.021356
  反缩放前范围: 最小值=-0.907890, 最大值=1.021356  # 只有最后一层
  反缩放后范围: 最小值=-48.460323, 最大值=54.516819
已对输出数据应用反缩放器

# SPICE推理（新增日志）
正在加载输入波形文件: projects/WNET5q1h2u6l3/data/wave_output/dataset_MET_output_original.wave
已加载波形文件，包含 350 个记录
  数据范围: 最小值=-44.712529, 最大值=42.353128
  缩放前范围: 最小值=-44.712529, 最大值=42.353128
  缩放后范围: 最小值=-1.000000, 最大值=0.947232
已对输入数据应用缩放器
正在对第 1/5 层进行 SPICE 仿真...
  第1层SPICE输出范围: 最小值=-1.213078, 最大值=1.197002
# ... 其他层
正在对第 5/5 层进行 SPICE 仿真...
  第5层SPICE输出范围: 最小值=-0.907890, 最大值=1.021356
  反缩放前范围: 最小值=-0.907890, 最大值=1.021356  # 只有最后一层
  反缩放后范围: 最小值=-48.460323, 最大值=54.516819
已对输出数据应用反缩放器
SPICE分层推理完成，保存了 5 个文件
NumPy仿真完成，保存了 5 个文件
```

## 实施风险评估

### 低风险修改
- ✅ 反缩放逻辑修复：逻辑清晰，影响范围可控
- ✅ 日志输出优化：纯粹的用户体验改进
- ✅ 接口参数扩展：向后兼容，不影响现有调用

### 中等风险修改
- ⚠️ `infer_and_save`逻辑复杂化：需要仔细测试SPICE/NumPy流程
- ⚠️ `manager.py`中的重构：涉及主要业务逻辑，需要充分测试

### 建议实施顺序
1. **第一阶段**：修复反缩放逻辑（方案一）
2. **第二阶段**：统一SPICE/NumPy架构（方案二）
3. **第三阶段**：优化和完善日志输出

## 测试验证方案

### 单元测试
- 测试反缩放逻辑：确保只对最后一层反缩放
- 测试SPICE/NumPy路径：验证新架构的功能完整性
- 测试日志输出：确认日志格式和内容正确

### 集成测试
- 使用现有项目进行完整推理流程测试
- 对比修改前后的输出文件，确保数据一致性
- 验证不同后端的日志输出统一性

### 回归测试
- 确保现有的NN推理功能不受影响
- 验证所有推理参数组合的正确性
- 测试错误处理和边界情况

本实施方案提供了详细的技术路线和具体的代码修改指导，确保在解决用户提出的两个核心问题的同时，保持系统的稳定性和可扩展性。