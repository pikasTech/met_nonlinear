# 快速推理功能修订实施计划

**日期**: 2025-07-10  
**版本**: 2.0（基于失败分析后的修订）  
**方案**: Wave数据筛选方案

## 1. 核心思路

**保持模型不变，优化数据输入**

- 模型结构和权重保持原样
- Wave文件包含所有数据（与标准模式相同）
- 在推理时从Wave文件中选择性读取最小和最大震级的数据
- 减少实际处理的数据量，提升推理速度

## 2. 实施方案

### 2.1 命令行参数（已完成）
```bash
python cli.py -i --quick PROJECT_NAME
python cli.py -i -q PROJECT_NAME
```

### 2.2 参数传递链（需要修改）
```
cli.py (-q/--quick) 
    ↓
ProjectManager.run_inference(quick=True)
    ↓
InferenceManager.run_inference(quick=True)
    ↓
InferenceProcessor.__init__(quick_mode=True)
    ↓
推理时筛选数据
```

## 3. 具体修改点

### 3.1 修改 `cli.py`（待实施）
```python
# 添加quick参数解析
quick_inference = '-q' in sys.argv or '--quick' in sys.argv

# 传递到推理函数
project.run_inference(force=force_mode, quick=quick_inference)
```

### 3.2 修改 `ProjectManager.run_inference()`（待实施）
```python
def run_inference(self, force=False, quick=False):
    """委托给推理管理器"""
    self.inference_manager.run_inference(force=force, quick=quick)
```

### 3.3 修改 `InferenceManager.run_inference()`（待实施）
```python
def run_inference(self, force=False, quick=False):
    """运行推理数据生成"""
    print(f'🔍 推理数据生成项目: {self.project_name}')
    if quick:
        print(f'⚡ 快速推理模式：只处理最小和最大震级数据')
    
    self.quick_mode = quick
    # ... 其余代码
```

### 3.4 修改 `InferenceManager._generate_inference_data()`（待实施）
```python
def _generate_inference_data(self, data_dir):
    # 创建推理处理器时传递quick_mode
    processor = InferenceProcessor(
        self.project_path, 
        quick_mode=self.quick_mode
    )
```

### 3.5 修改 `InferenceProcessor`（核心修改）

#### 3.5.1 初始化接收quick_mode参数
```python
def __init__(self, project_path: str, backend_type: str = "batch_predict", quick_mode: bool = False):
    self.quick_mode = quick_mode
    # ... 其余初始化代码
```

#### 3.5.2 修改数据加载方法（新增）
```python
def _load_wave_data_with_filter(self, wave_path):
    """
    加载wave数据，支持快速模式筛选
    
    在快速模式下，只加载最小和最大震级的数据
    """
    wave_data = self.wave_processor.load_waveform(wave_path)
    
    if not self.quick_mode:
        return wave_data
    
    # 快速模式：筛选最小最大震级
    filtered_data = self._filter_min_max_magnitude(wave_data)
    return filtered_data

def _filter_min_max_magnitude(self, wave_data):
    """
    从wave数据中筛选最小和最大震级的记录
    """
    # 获取所有记录的震级信息
    magnitudes = []
    records = []
    
    for record in wave_data.records:
        if 'magnitude' in record.user_metadata:
            mag = record.user_metadata['magnitude']
            magnitudes.append(mag)
            records.append(record)
    
    if len(magnitudes) < 2:
        # 数据太少，返回原始数据
        return wave_data
    
    # 找出最小和最大震级的索引
    min_idx = np.argmin(magnitudes)
    max_idx = np.argmax(magnitudes)
    
    # 创建新的WaveData只包含这两个震级
    filtered_wave_data = WaveData()
    filtered_wave_data.sample_rate = wave_data.sample_rate
    filtered_wave_data.user_metadata = wave_data.user_metadata.copy()
    
    # 添加筛选信息到元数据
    filtered_wave_data.user_metadata['quick_mode'] = True
    filtered_wave_data.user_metadata['original_records'] = len(wave_data.records)
    filtered_wave_data.user_metadata['filtered_records'] = 2
    
    # 只添加最小和最大震级的记录
    for idx in [min_idx, max_idx]:
        filtered_wave_data.add_record(records[idx])
    
    print(f"⚡ 快速模式数据筛选:")
    print(f"   原始记录数: {len(wave_data.records)}")
    print(f"   筛选后记录数: {len(filtered_wave_data.records)}")
    print(f"   最小震级: {magnitudes[min_idx]:.2f}")
    print(f"   最大震级: {magnitudes[max_idx]:.2f}")
    print(f"   预期性能提升: 约 {len(wave_data.records)/2:.0f} 倍")
    
    return filtered_wave_data
```

#### 3.5.3 修改推理方法使用筛选后的数据
```python
def infer_and_save(self, input_wave_path, output_dir, **kwargs):
    """修改此方法使用筛选后的数据"""
    # 使用新的加载方法
    input_wave_data = self._load_wave_data_with_filter(input_wave_path)
    
    # 其余推理逻辑保持不变
    # ...
```

## 4. 测试计划

### 4.1 功能测试
1. 验证参数解析正确
2. 验证快速模式只处理2个震级
3. 验证推理结果的正确性
4. 验证标准模式不受影响

### 4.2 性能测试
1. 对比快速模式和标准模式的执行时间
2. 验证性能提升比例
3. 检查内存使用情况

### 4.3 兼容性测试
1. 确保不影响训练功能
2. 确保不影响标准推理
3. 确保wave文件格式兼容

## 5. 预期效果

- **推理速度**: 提升 10-12 倍（25个震级→2个震级）
- **内存使用**: 推理阶段减少 90%
- **兼容性**: 完全兼容现有系统
- **易用性**: 只需添加 `--quick` 参数

## 6. 注意事项

1. **不修改ModelEngine**：保持模型构建逻辑不变
2. **Wave文件不变**：仍然包含所有数据，只是读取时筛选
3. **模型权重不变**：使用原有的训练好的权重
4. **输出格式一致**：快速模式的输出格式与标准模式相同

## 7. 实施顺序

1. 修改命令行参数传递（cli.py）
2. 修改推理管理器（InferenceManager）
3. 实现Wave数据筛选功能（InferenceProcessor）
4. 测试验证功能
5. 性能优化和调试