# Wave误差分析具体实施方案

## 实施概要

按照方案一，扩展WaveData类添加减法运算支持，并在误差分析中生成error_layers目录。

## 修改文件清单

### 1. `calibration_analyzer/wavedata.py`
**修改点：在WaveData类中添加__sub__方法**

位置：在`__mul__`方法（第540行）后添加

```python
def __sub__(self, other: 'WaveData') -> 'WaveData':
    """
    实现两个WaveData对象的减法运算
    
    参数:
        other: 另一个WaveData对象
        
    返回:
        WaveData: 相减后的新WaveData对象（self - other）
    """
    if not isinstance(other, WaveData):
        raise TypeError(f"减数必须是WaveData对象，而不是{type(other).__name__}")
    
    # 检查记录数量是否匹配
    if len(self.records) != len(other.records):
        raise ValueError(f"记录数量不匹配：{len(self.records)} vs {len(other.records)}")
    
    # 创建新的WaveData对象
    new_wavedata = WaveData(
        description=f"{self.description} - {other.description}",
        version=self.version,
        creation_date=self.creation_date,
        modified_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        author=self.author,
        tags=self.tags.copy() if self.tags else [],
        user_metadata=self.user_metadata.copy() if self.user_metadata else {}
    )
    
    # 对每个记录进行减法运算
    for i, (rec1, rec2) in enumerate(zip(self.records, other.records)):
        # 检查数据形状是否匹配
        if rec1.data.shape != rec2.data.shape:
            raise ValueError(f"记录{i}的数据形状不匹配：{rec1.data.shape} vs {rec2.data.shape}")
        
        # 检查采样率是否匹配
        if abs(rec1.sample_rate - rec2.sample_rate) > 1e-6:
            raise ValueError(f"记录{i}的采样率不匹配：{rec1.sample_rate} vs {rec2.sample_rate}")
        
        # 计算差值
        error_data = rec1.data - rec2.data
        
        # 创建新记录
        new_record = WaveRecord(
            data=error_data,
            sample_rate=rec1.sample_rate,
            channel_names=rec1.channel_names,
            record_id=f"error_{rec1.record_id}",
            creation_date=rec1.creation_date,
            modified_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            units=rec1.units,
            user_metadata={
                **rec1.user_metadata,
                "error_type": "difference",
                "source1_id": rec1.record_id,
                "source2_id": rec2.record_id
            }
        )
        new_wavedata.add_record(new_record)
    
    return new_wavedata
```

### 2. `cli.py`
**修改点1：在_analyze_inference_errors方法中添加误差wave生成和保存**

位置：在第536行（`error = nn_output - spice_output`）后添加误差wave保存逻辑

```python
# 在第505行的循环开始前，创建error_layers目录
error_layers_dir = os.path.join(inference_data_dir, 'error_layers')
os.makedirs(error_layers_dir, exist_ok=True)

# 在第511-512行加载数据后，保存误差wave（第514行后插入）
# 计算误差wave并保存
error_wave = nn_data - spice_data
error_wave.description = f"Error (NN - SPICE) for Layer {i+1}"
error_wave.add_user_metadata("project_name", self.project_name)
error_wave.add_user_metadata("layer_index", i+1)
error_wave.add_user_metadata("analysis_timestamp", self._get_timestamp())

# 保存误差wave
error_path = os.path.join(error_layers_dir, f"layer_{i+1}.wave")
wave_processor.save_waveform(error_path, error_wave)
print(f"  保存误差wave: {error_path}")
```

**修改点2：更新_generate_analysis_report，添加误差wave路径信息**

位置：在_analyze_inference_errors返回的analysis_results中添加error_wave_path

```python
# 在第539行的layer_stats字典中添加
"error_wave_path": f"error_layers/layer_{i+1}.wave",
```

**修改点3：更新_check_existing_inference_data以包含error_layers检查（可选）**

如果需要在重新分析时检查误差数据是否已存在，可在第344行添加：

```python
# 检查error_layers目录（可选，用于避免重复计算）
error_layers_dir = os.path.join(data_dir, 'error_layers')
if os.path.exists(error_layers_dir):
    error_files = sorted([f for f in os.listdir(error_layers_dir) if f.endswith('.wave')])
    if error_files:
        print(f"  发现已有误差分析数据：{len(error_files)} 个文件")
```

## 完整的修改后代码片段

### cli.py中_analyze_inference_errors方法的关键修改部分：

```python
def _analyze_inference_errors(self, inference_data_dir):
    # ... 现有代码 ...
    
    # 创建error_layers目录（在第503行后添加）
    error_layers_dir = os.path.join(inference_data_dir, 'error_layers')
    os.makedirs(error_layers_dir, exist_ok=True)
    
    print(f"开始分析 {nn_layers} 层的推理误差...")
    
    # 逐层加载和分析
    for i in range(nn_layers):
        # 加载对应层的数据
        nn_path = os.path.join(nn_layers_dir, nn_files[i])
        spice_path = os.path.join(spice_layers_dir, spice_files[i])
        
        nn_data = wave_processor.load_waveform(nn_path)
        spice_data = wave_processor.load_waveform(spice_path)
        
        print(f"分析第 {i+1} 层...")
        
        # 计算并保存误差wave（新增）
        try:
            error_wave = nn_data - spice_data
            error_wave.description = f"Error (NN - SPICE) for Layer {i+1}"
            error_wave.add_user_metadata("project_name", self.project_name)
            error_wave.add_user_metadata("layer_index", i+1)
            error_wave.add_user_metadata("analysis_timestamp", self._get_timestamp())
            
            error_path = os.path.join(error_layers_dir, f"layer_{i+1}.wave")
            wave_processor.save_waveform(error_path, error_wave)
            print(f"  保存误差wave: layer_{i+1}.wave")
        except Exception as e:
            print(f"  警告：无法生成误差wave - {str(e)}")
        
        # ... 现有的误差统计代码 ...
        
        # 在layer_stats中添加误差wave路径
        layer_stats = {
            "layer_index": i + 1,
            "mean_error": float(np.mean(error)),
            "std_error": float(np.std(error)),
            "rms_error": float(np.sqrt(np.mean(np.square(error)))),
            "max_error": float(np.max(np.abs(error))),
            "num_samples": error.size,
            "error_shape": list(error.shape),
            "nn_records": len(nn_data.records),
            "spice_records": len(spice_data.records),
            "error_wave_path": f"error_layers/layer_{i+1}.wave"  # 新增
        }
        
        # ... 继续现有代码 ...
```

## 测试验证步骤

1. **单元测试WaveData减法运算**：
   ```bash
   # 创建简单的测试脚本验证减法功能
   python -c "
   from calibration_analyzer.wavedata import WaveData, WaveRecord
   import numpy as np
   
   # 创建测试数据
   data1 = WaveData()
   data1.add_record(WaveRecord(np.array([[1,2],[3,4]]), 1000))
   
   data2 = WaveData()
   data2.add_record(WaveRecord(np.array([[0.5,1],[1.5,2]]), 1000))
   
   # 测试减法
   error = data1 - data2
   print('减法测试通过:', error.records[0].data)
   "
   ```

2. **集成测试**：
   ```bash
   # 运行推理
   conda run -n tf26 python cli.py -i WNET5q0.5h2u6l3
   
   # 运行误差分析
   conda run -n tf26 python cli.py -a WNET5q0.5h2u6l3
   
   # 验证输出
   ls -la projects/WNET5q0.5h2u6l3/data/inference/error_layers/
   ```

3. **验证误差wave内容**：
   ```python
   # 验证误差计算正确性
   from calibration_analyzer.waveprocessor import WaveProcessor
   wp = WaveProcessor()
   
   # 加载并比较
   nn = wp.load_waveform('projects/.../nn_layers/layer_1.wave')
   spice = wp.load_waveform('projects/.../spice_layers/layer_1.wave')
   error = wp.load_waveform('projects/.../error_layers/layer_1.wave')
   
   # 验证：error = nn - spice
   assert np.allclose(error.records[0].data, 
                      nn.records[0].data - spice.records[0].data)
   ```

## 代码修改量统计

- **wavedata.py**：新增约60行（__sub__方法）
- **cli.py**：修改约20行（主要是插入代码）
- **总计**：约80行代码修改

## 风险评估

1. **低风险**：新增功能不影响现有功能
2. **中风险**：需要确保两个wave的兼容性检查完善
3. **可回退**：如果__sub__方法出错，可在try-except中捕获，不影响原有统计功能

## 实施优先级

1. 先实现并测试WaveData.__sub__方法
2. 再修改cli.py集成误差wave生成
3. 最后进行完整的端到端测试