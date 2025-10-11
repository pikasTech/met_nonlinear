# SPICE SVF层相位修正实施计划（方案2）

## 实施概述

在 `InferenceManager` 中添加SPICE后处理逻辑，对SVF层的HP和LP通道进行相位反转，以修正SPICE输出与NN输出的相位差异。

## 文件修改清单

### 1. **inference/manager.py**

#### 修改点1：在 `_generate_inference_data` 方法中添加相位修正调用
**位置**：约第217行，在解析SPICE推理结果后，保存前
```python
# 解析返回结果
if isinstance(results, dict) and 'spice' in results:
    spice_outputs = results['spice']
    numpy_outputs = results.get('numpy', [])
elif isinstance(results, list):
    spice_outputs = results
    numpy_outputs = []

# [新增] 对SPICE输出应用SVF相位修正
print("\n🔧 检查并应用SPICE SVF层相位修正...")
spice_outputs = self._apply_spice_phase_corrections(spice_outputs)
```

#### 修改点2：添加 `_apply_spice_phase_corrections` 方法
**位置**：在 `_get_timestamp` 方法前添加
```python
def _apply_spice_phase_corrections(self, spice_layer_outputs):
    """
    对SPICE分层输出应用相位修正
    
    参数:
        spice_layer_outputs: SPICE推理的分层输出列表
        
    返回:
        修正后的分层输出列表
    """
```

#### 修改点3：添加 `_is_svf_layer_output` 方法
**位置**：在 `_apply_spice_phase_corrections` 方法后
```python
def _is_svf_layer_output(self, wave_data):
    """
    判断层输出是否为SVF层
    
    判断依据：
    1. 通道数是3的倍数（每个SVF输出HP/BP/LP三个通道）
    2. 通道数大于0
    
    参数:
        wave_data: WaveData对象
        
    返回:
        bool: 是否为SVF层
    """
```

#### 修改点4：添加 `_correct_svf_phase` 方法
**位置**：在 `_is_svf_layer_output` 方法后
```python
def _correct_svf_phase(self, wave_data):
    """
    对SVF层输出进行相位修正
    
    修正规则：
    - HP通道（索引 0, 3, 6, ...）：反相
    - BP通道（索引 1, 4, 7, ...）：保持不变
    - LP通道（索引 2, 5, 8, ...）：反相
    
    参数:
        wave_data: 原始WaveData对象
        
    返回:
        修正后的WaveData对象
    """
```

## 实施细节

### 1. SVF层识别逻辑
- **主要依据**：通道数是3的倍数且大于0
- **验证方法**：检查第一个record的通道数
- **兼容性**：对非SVF层直接返回原始数据，不进行处理

### 2. 相位修正算法
```python
# 对每个SVF单元进行处理
for svf_idx in range(num_svf):
    hp_channel = svf_idx * 3 + 0  # 高通通道索引
    lp_channel = svf_idx * 3 + 2  # 低通通道索引
    # BP通道 (svf_idx * 3 + 1) 保持不变
    
    # 对HP和LP通道数据反相
    corrected_data[:, hp_channel] *= -1
    corrected_data[:, lp_channel] *= -1
```

### 3. 数据完整性保护
- 使用 `record.data.copy()` 创建数据副本，避免修改原始数据
- 保留所有元数据，仅修改数据内容
- 添加 `phase_corrected` 标记到元数据中

### 4. 日志记录
- 记录处理的层数和SVF单元数
- 对每层的处理结果进行日志输出
- 保留原始描述信息，添加相位修正标记

## 测试计划

### 1. 功能测试
```bash
# 使用指定的测试命令
conda run -n tf26 python cli.py -i WNET5q1h2u6l3
```

### 2. 验证点
- ✓ 推理过程正常完成，无报错
- ✓ 生成 spice_layers/ 目录
- ✓ 日志中显示相位修正信息
- ✓ 生成的wave文件包含修正后的数据

### 3. 效果验证
```bash
# 运行误差分析，查看相位修正效果
conda run -n tf26 python cli.py -a WNET5q1h2u6l3
```
期望看到NN-SPICE误差显著降低，特别是SVF层的HP和LP通道。

## 风险控制

### 1. 异常处理
- 对所有新增方法添加try-except块
- 异常时返回原始数据，确保推理流程不中断
- 记录详细的错误信息用于调试

### 2. 向后兼容
- 不修改现有的API接口
- 保持原有的数据结构和格式
- 仅在SPICE推理路径上应用修正

### 3. 性能考虑
- 使用numpy的向量化操作，避免循环
- 仅对需要修正的通道进行操作
- 避免不必要的数据复制

## 实施顺序

1. **第一步**：添加三个辅助方法
   - `_is_svf_layer_output`
   - `_correct_svf_phase`
   - `_apply_spice_phase_corrections`

2. **第二步**：修改 `_generate_inference_data`
   - 在SPICE输出解析后添加相位修正调用

3. **第三步**：测试验证
   - 运行推理命令
   - 检查日志输出
   - 验证生成的数据

## 预期结果

1. **日志输出**
```
🔧 检查并应用SPICE SVF层相位修正...
  第1层是SVF层（6个通道，2个SVF单元），应用相位修正...
  第2层不是SVF层，跳过相位修正
  ...
```

2. **数据效果**
- SVF层的HP和LP通道相位将与NN输出一致
- BP通道保持原有相位不变
- 非SVF层的输出完全不受影响

3. **误差改善**
- NN-SPICE误差分析将显示相位一致性的显著改善
- 特别是通道1,3,4,6的误差将大幅降低