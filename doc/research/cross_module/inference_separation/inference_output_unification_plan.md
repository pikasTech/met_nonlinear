# 推理输出格式统一方案

## 1. 问题分析

当前存在两种不同的推理输出格式：

### 1.1 inference/cli.py 输出格式（目标格式）
```
inference/temp/
├── dataset_inference.wave      # 最终输出
├── layers/                     # 分层输出目录
│   ├── layer_1.wave           # 第1层输出
│   ├── layer_2.wave           # 第2层输出
│   ├── layer_3.wave           # 第3层输出
│   ├── layer_4.wave           # 第4层输出
│   └── layer_5.wave           # 第5层输出
```

### 1.2 cli.py -i 输出格式（当前格式）
```
projects/WNET5q0.5h2u6l3/data/inference/
├── nn_layers.wave             # 所有层合并在一个文件中
├── spice_layers.wave          # 所有层合并在一个文件中
└── input.wave                 # 输入文件副本
```

## 2. 代码实现差异

### 2.1 inference/cli.py 实现路径
```python
InferenceProcessor.infer_and_save()
  └─> InferenceDataProcessor.infer_and_save()
      └─> 当layer_output_dir不为None时：
          └─> 为每一层创建单独的文件：layer_{i+1}.wave
```

### 2.2 cli.py 实现路径
```python
ProjectManager.run_inference()
  └─> _generate_inference_data()
      ├─> 获取分层输出 List[WaveData]
      └─> _combine_layer_outputs()  # 问题所在：合并所有层到一个文件
          └─> 创建单个WaveData，每层作为一个record
```

## 3. 修改方案

### 方案一：复用 InferenceProcessor 的保存逻辑（推荐）

**修改内容：**
1. 修改 `cli.py` 的 `_generate_inference_data` 方法，直接使用 InferenceProcessor 的 `infer_and_save` 方法

**具体改动：**
```python
def _generate_inference_data(self, data_dir):
    """生成推理数据"""
    # ... 前面的导入和初始化代码不变 ...
    
    # 创建推理处理器
    processor = InferenceProcessor(self.project_path)
    
    # 创建子目录
    nn_layers_dir = os.path.join(data_dir, 'nn_layers')
    spice_layers_dir = os.path.join(data_dir, 'spice_layers')
    
    # 使用 InferenceProcessor 的 infer_and_save 方法
    # 神经网络分层推理
    processor.set_backend("layer_by_layer")
    processor.infer_and_save(
        input_wave, 
        None,  # 不需要整体输出
        nn_layers_dir,  # 分层输出目录
        use_scaler=True
    )
    
    # SPICE分层推理（如果SPICEBackend支持分层输出）
    processor.set_backend("spice")
    processor.infer_and_save(
        input_wave,
        None,
        spice_layers_dir,
        use_scaler=True
    )
    
    # 保存原始输入
    import shutil
    shutil.copy2(input_wave, f'{data_dir}/input.wave')
```

**优点：**
- 代码修改量最小
- 充分复用现有基础设施
- 保证输出格式完全一致
- 维护简单，避免重复代码

**缺点：**
- 需要调整误差分析代码以适应新的文件结构

### 方案二：改造 _combine_layer_outputs 方法

**修改内容：**
1. 将 `_combine_layer_outputs` 改为 `_save_layer_outputs`
2. 让其保存每层为单独文件，而不是合并

**具体改动：**
```python
def _save_layer_outputs(self, layer_outputs, output_dir, prefix):
    """保存分层输出，每层一个文件"""
    os.makedirs(output_dir, exist_ok=True)
    
    for i, layer_output in enumerate(layer_outputs):
        layer_file = os.path.join(output_dir, f"{prefix}_layer_{i+1}.wave")
        self.wave_processor.save_waveform(layer_file, layer_output)
    
    print(f"已保存 {len(layer_outputs)} 个层输出到 {output_dir}")
```

**优点：**
- 保持 cli.py 的独立性
- 对现有流程改动较小

**缺点：**
- 需要重新实现已有功能
- 可能与 InferenceProcessor 的实现不一致

### 方案三：创建统一的输出格式管理器

**修改内容：**
1. 创建新的 `InferenceOutputManager` 类
2. 统一管理两种调用方式的输出

**优点：**
- 架构清晰，职责分离
- 便于未来扩展

**缺点：**
- 需要较大改动
- 增加系统复杂度

## 4. 推荐方案

**推荐采用方案一**，理由如下：

1. **最小化修改**：只需要修改 `_generate_inference_data` 方法
2. **充分复用**：利用已经实现和测试过的 InferenceProcessor 功能
3. **格式一致**：确保两种调用方式产生完全相同的输出格式
4. **维护简单**：避免重复代码，降低维护成本

## 5. 实施步骤

1. **备份现有代码**
   ```bash
   cp cli.py cli.py.backup
   ```

2. **修改 _generate_inference_data 方法**
   - 使用 InferenceProcessor.infer_and_save 替代当前实现
   - 调整目录结构

3. **更新误差分析相关代码**
   - 修改 `_analyze_inference_errors` 以适应新的文件结构
   - 更新文件路径查找逻辑

4. **测试验证**
   - 运行 `python cli.py -i WNET5q0.5h2u6l3`
   - 验证输出文件结构
   - 确保误差分析功能正常

5. **更新文档**
   - 更新相关使用说明
   - 记录输出格式变更

## 6. 影响评估

- **向后兼容性**：需要提供迁移脚本，将旧格式转换为新格式
- **性能影响**：多文件输出可能略微增加I/O开销，但影响很小
- **用户体验**：输出更清晰，便于单独查看每层结果