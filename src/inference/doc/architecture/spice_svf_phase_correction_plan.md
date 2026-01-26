# SPICE SVF层相位修正实施方案

## 问题分析

### 当前问题
在 `python cli.py -i` 生成的推理数据中，SPICE 输出与 NN 输出存在特定的相位反转问题：
- **需要反相的通道**：1、3、4、6（对应2个SVF的HP和LP通道）
- **保持不变的通道**：2、5（对应2个SVF的BP通道）
- **通用规律**：每个SVF的HP(高通)和LP(低通)需要反相，BP(带通)保持不变

### 通道模式分析
```
2个SVF的输出模式：
通道1: SVF0_HP (需要反相)
通道2: SVF0_BP (保持不变)  
通道3: SVF0_LP (需要反相)
通道4: SVF1_HP (需要反相)
通道5: SVF1_BP (保持不变)
通道6: SVF1_LP (需要反相)

3个SVF的输出模式：
通道1,3,4,6,7,9: HP和LP通道 (需要反相)
通道2,5,8: BP通道 (保持不变)
```

### 目标
- 对SPICE推理的SVF层输出进行特定通道的相位修正
- 确保修正后的SPICE输出与NN输出相位一致
- 最小化代码修改，充分利用现有基础设施

## 现有基础设施调研

### 1. SPICE推理流程分析
```python
cli.py -i 
  └─> InferenceManager.run_inference()
    └─> InferenceManager._generate_inference_data()
      └─> SPICEBackend.infer(return_layers=True, return_numpy=True)
        └─> SPICEBackend.simulate_with_spice() # 每层
          └─> 返回 WaveData 对象
        └─> 保存到 spice_layers/layer_X.wave
```

### 2. 相关数据结构
- **WaveData**：包含多个 WaveRecord
- **WaveRecord**：包含 `data` (numpy数组)、`channel_names`、`record_id` 等
- **通道操作**：可通过 `record.data[:, channel_idx]` 访问特定通道

### 3. SVF层识别机制
- **输出通道数**：SVF层输出通道数通常是3的倍数（每个SVF输出3个通道）
- **层描述**：WaveData.description 可能包含层类型信息
- **通道名称**：channel_names 可能包含 "HP", "BP", "LP" 等标识

## 实施方案

### 方案1：在 SPICEBackend 中添加SVF特定后处理 ⭐⭐⭐

#### 实现位置
在 `inference/inference_backends.py` 的 `simulate_with_spice` 方法中，SPICE仿真完成后立即处理。

#### 核心逻辑
```python
def simulate_with_spice(self, spice_input, input_wave_data, output_name="spice_simulation_result"):
    # ... 现有SPICE仿真逻辑 ...
    
    # 应用SVF相位修正
    if self._is_svf_layer(output_wave_data):
        output_wave_data = self._apply_svf_phase_correction(output_wave_data)
    
    return output_wave_data

def _is_svf_layer(self, wave_data):
    """判断是否为SVF层"""
    # 方法1: 通过通道数判断（SVF层通道数是3的倍数且>0）
    # 方法2: 通过通道名称判断（包含HP/BP/LP）
    # 方法3: 通过层描述判断
    
def _apply_svf_phase_correction(self, wave_data):
    """对SVF层输出应用相位修正"""
    # 对每个record的HP和LP通道进行反相
    for record in wave_data.records:
        num_channels = record.data.shape[1]
        num_svf = num_channels // 3
        
        for svf_idx in range(num_svf):
            hp_channel = svf_idx * 3 + 0  # HP通道
            lp_channel = svf_idx * 3 + 2  # LP通道
            # BP通道 (svf_idx * 3 + 1) 保持不变
            
            record.data[:, hp_channel] = -record.data[:, hp_channel]
            record.data[:, lp_channel] = -record.data[:, lp_channel]
    
    return wave_data
```

#### 优点
- **逻辑集中**：在SPICE仿真的核心位置处理，便于维护
- **影响范围小**：只影响SPICE推理路径，不影响NN和NumPy路径
- **自动应用**：所有通过SPICEBackend的推理都会自动应用修正

#### 缺点
- **通用性影响**：在通用的SPICEBackend中添加模型特定逻辑
- **层识别复杂性**：需要可靠的SVF层识别机制

#### 修改文件
- `inference/inference_backends.py`：添加 `_is_svf_layer` 和 `_apply_svf_phase_correction` 方法

---

### 方案2：在 InferenceManager 中添加SPICE后处理 ⭐⭐⭐⭐

#### 实现位置
在 `inference/manager.py` 的 `_generate_inference_data` 方法中，保存SPICE层输出之前进行处理。

#### 核心逻辑
```python
def _generate_inference_data(self, data_dir):
    # ... 现有逻辑 ...
    
    # SPICE分层推理（带NumPy支持）
    results = processor.backend.infer(input_data, use_scaler=True, return_layers=True, return_numpy=True)
    
    # 解析返回结果
    if isinstance(results, dict) and 'spice' in results:
        spice_outputs = results['spice']
        numpy_outputs = results.get('numpy', [])
    
    # 对SPICE输出应用SVF相位修正
    spice_outputs = self._apply_spice_phase_corrections(spice_outputs)
    
    # 保存SPICE分层输出
    # ... 现有保存逻辑 ...

def _apply_spice_phase_corrections(self, spice_layer_outputs):
    """对SPICE分层输出应用相位修正"""
    corrected_outputs = []
    
    for i, layer_output in enumerate(spice_layer_outputs):
        if self._is_svf_layer_output(layer_output):
            print(f"  对第{i+1}层(SVF)应用相位修正...")
            layer_output = self._correct_svf_phase(layer_output)
        
        corrected_outputs.append(layer_output)
    
    return corrected_outputs

def _is_svf_layer_output(self, wave_data):
    """判断层输出是否为SVF层"""
    if not wave_data.records:
        return False
    
    # 通过通道数判断：SVF层输出通道数是3的倍数
    num_channels = wave_data.records[0].data.shape[1]
    return num_channels > 0 and num_channels % 3 == 0

def _correct_svf_phase(self, wave_data):
    """对SVF层输出进行相位修正"""
    corrected_data = WaveData(
        description=f"{wave_data.description} (Phase Corrected)",
        author=wave_data.author
    )
    
    for record in wave_data.records:
        corrected_record_data = record.data.copy()
        num_channels = corrected_record_data.shape[1]
        num_svf = num_channels // 3
        
        # 对每个SVF的HP和LP通道进行反相
        for svf_idx in range(num_svf):
            hp_channel = svf_idx * 3 + 0  # 高通
            lp_channel = svf_idx * 3 + 2  # 低通
            
            corrected_record_data[:, hp_channel] *= -1
            corrected_record_data[:, lp_channel] *= -1
        
        # 创建修正后的记录
        corrected_record = WaveRecord(
            data=corrected_record_data,
            sample_rate=record.sample_rate,
            channel_names=record.channel_names,
            record_id=f"{record.record_id}_phase_corrected",
            user_metadata={**record.user_metadata, "phase_corrected": True}
        )
        
        corrected_data.add_record(corrected_record)
    
    return corrected_data
```

#### 优点
- **架构清晰**：在数据管理层处理，不影响推理引擎核心逻辑
- **灵活性高**：可以针对不同模型类型添加不同的后处理逻辑
- **可控性好**：只在推理数据生成时应用，不影响其他用途的SPICE推理
- **调试友好**：容易添加日志和调试信息

#### 缺点
- **代码位置**：在数据管理类中添加模型特定逻辑，可能不够纯粹

#### 修改文件
- `inference/manager.py`：添加SVF相位修正相关方法

---

### 方案3：扩展现有的 post_process 机制 ⭐⭐

#### 实现位置
修改 `models/model_layers.py` 中的 `SVFLayer.post_process` 方法，添加上下文感知的相位处理。

#### 核心逻辑
```python
class SVFLayer:
    def post_process(self, result, context=None):
        """后处理方法，支持上下文感知的相位修正"""
        # context 可以包含 {'source': 'spice'|'nn'|'numpy'} 等信息
        
        if context and context.get('source') == 'spice':
            # SPICE路径：只对HP和LP通道反相（因为SPICE仿真已经是反相的）
            # 这样可以抵消SPICE仿真的反相，使结果与NN一致
            return self._apply_selective_phase_inversion(result)
        else:
            # NN和NumPy路径：保持现有逻辑或不处理
            return result
```

#### 优点
- **架构一致**：利用现有的post_process机制，符合设计模式
- **模型特定**：在模型层处理，逻辑归属清晰

#### 缺点
- **复杂性增加**：需要传递上下文信息，增加调用复杂度
- **向后兼容**：需要确保现有调用不受影响
- **实现难度**：需要修改多个调用点以传递上下文

#### 修改文件
- `models/model_layers.py`：修改SVFLayer.post_process方法
- `inference/inference_backends.py`：修改调用以传递上下文
- 其他调用post_process的地方

## 方案对比与推荐

| 方案 | 实现难度 | 代码修改量 | 架构影响 | 维护性 | 推荐度 |
|------|----------|------------|----------|---------|---------|
| 方案1: SPICEBackend后处理 | 中等 | 小 | 中等 | 中等 | ⭐⭐⭐ |
| 方案2: InferenceManager后处理 | 低 | 小 | 小 | 高 | ⭐⭐⭐⭐ |
| 方案3: 扩展post_process | 高 | 大 | 大 | 低 | ⭐⭐ |

## 推荐方案：方案2

### 推荐理由
1. **实现简单**：在数据保存前处理，逻辑直观
2. **影响最小**：只影响推理数据生成，不改变核心推理逻辑
3. **易于调试**：可以方便地添加日志和验证
4. **扩展性好**：未来可以easily添加其他层类型的相位修正

### 实施步骤
1. 在 `InferenceManager` 中添加 `_apply_spice_phase_corrections` 方法
2. 添加 `_is_svf_layer_output` 和 `_correct_svf_phase` 辅助方法
3. 在 `_generate_inference_data` 中调用相位修正
4. 添加适当的日志和元数据标记

### 预期效果
- `python cli.py -i` 生成的 spice_layers 将包含相位修正后的数据
- NN-SPICE 误差分析将显示显著改善的相位一致性
- 不影响其他推理路径（NN、NumPy）的输出

## 风险评估

### 低风险
- 只修改数据生成流程，不影响核心推理引擎
- 有现有的WaveData操作基础设施支持

### 中等风险  
- SVF层识别的准确性需要验证
- 通道索引计算需要确保正确性

### 缓解措施
- 添加详细的日志记录相位修正过程
- 在应用修正前后保存数据以便对比验证
- 先在测试数据上验证修正效果