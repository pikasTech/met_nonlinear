# 推理终端输出优化计划

## 概述
本计划旨在优化推理过程的终端输出，提供更详细的数据范围信息，并减少不必要的进度条显示。

## 优化目标
1. 批量仿真的进度条默认配置为不显示
2. 应用缩放器和反缩放器之后，打印缩放前后的数据范围（最大值最小值）
3. 每一层推理完之后，打印输出的数据范围（最大值最小值）
4. 加载输入数据之后，打印数据范围（最大值最小值）

## 需要修改的文件清单

### 1. `/mnt/f/Work/met_nonlinear/inference/data_processing.py`

#### 修改点1：加载输入数据后显示数据范围
- **位置**：`load_input_wave` 方法（第52-55行）
- **修改内容**：在加载波形文件后，添加数据范围统计和输出
- **具体实现**：
  ```python
  # 在第54行后添加
  # 计算并显示数据范围
  all_data = []
  for record in wave_data.records:
      all_data.append(record.data.flatten())
  all_data = np.concatenate(all_data)
  print(f"  数据范围: 最小值={all_data.min():.6f}, 最大值={all_data.max():.6f}")
  ```

#### 修改点2：应用缩放器后显示数据范围变化
- **位置**：`_apply_input_scaling` 方法（第189行）
- **修改内容**：在打印"已对输入数据应用缩放器"之前，添加缩放前后的数据范围对比
- **具体实现**：
  ```python
  # 在第118行前（return之前）添加
  # 计算缩放前后的数据范围
  original_min, original_max = float('inf'), float('-inf')
  scaled_min, scaled_max = float('inf'), float('-inf')
  
  for orig_record, scaled_record in zip(input_wave_data.records, scaled_wave_data.records):
      orig_data = orig_record.data.flatten()
      scaled_data = scaled_record.data.flatten()
      
      original_min = min(original_min, orig_data.min())
      original_max = max(original_max, orig_data.max())
      scaled_min = min(scaled_min, scaled_data.min())
      scaled_max = max(scaled_max, scaled_data.max())
  
  print(f"  缩放前范围: 最小值={original_min:.6f}, 最大值={original_max:.6f}")
  print(f"  缩放后范围: 最小值={scaled_min:.6f}, 最大值={scaled_max:.6f}")
  ```

#### 修改点3：应用反缩放器后显示数据范围变化
- **位置**：`_apply_output_inverse_scaling` 方法（第202行）
- **修改内容**：在返回之前，添加反缩放前后的数据范围对比
- **具体实现**：
  ```python
  # 在第167行前（return之前）添加
  # 计算反缩放前后的数据范围
  scaled_min, scaled_max = float('inf'), float('-inf')
  unscaled_min, unscaled_max = float('inf'), float('-inf')
  
  for scaled_record, unscaled_record in zip(output_wave_data.records, unscaled_wave_data.records):
      scaled_data = scaled_record.data.flatten()
      unscaled_data = unscaled_record.data.flatten()
      
      scaled_min = min(scaled_min, scaled_data.min())
      scaled_max = max(scaled_max, scaled_data.max())
      unscaled_min = min(unscaled_min, unscaled_data.min())
      unscaled_max = max(unscaled_max, unscaled_data.max())
  
  print(f"  反缩放前范围: 最小值={scaled_min:.6f}, 最大值={scaled_max:.6f}")
  print(f"  反缩放后范围: 最小值={unscaled_min:.6f}, 最大值={unscaled_max:.6f}")
  ```

### 2. `/mnt/f/Work/met_nonlinear/inference/inference_backends.py`

#### 修改点4：每层推理完成后显示输出数据范围
- **位置**：`LayerByLayerBackend.infer` 方法（第497行）
- **修改内容**：在打印"已完成第 X 层的推理"之后，添加该层输出的数据范围
- **具体实现**：
  ```python
  # 在第496行后添加
  # 计算并显示该层输出的数据范围
  layer_min, layer_max = float('inf'), float('-inf')
  for record in layer_output.records:
      data = record.data.flatten()
      layer_min = min(layer_min, data.min())
      layer_max = max(layer_max, data.max())
  print(f"  第{layer_idx + 1}层输出范围: 最小值={layer_min:.6f}, 最大值={layer_max:.6f}")
  ```

### 3. `/mnt/f/Work/met_nonlinear/spice_simulator/simulation.py`

#### 修改点5：批量仿真进度条控制
- **位置**：`CircuitSimulation.run_simulation` 方法（第669-686行和第693-712行）
- **修改内容**：添加进度条显示控制参数
- **具体实现**：
  1. 在 `__init__` 方法中添加配置参数：
     ```python
     def __init__(self, output_folder='./temp', ngspice_path=None, max_workers=None, show_progress=True):
         # ... 现有代码 ...
         self.show_progress = show_progress  # 新增参数控制进度条显示
     ```
  
  2. 修改并行仿真部分（第669-686行）：
     ```python
     # 原代码
     pbar = tqdm(total=batch_size, desc="批量仿真进度")
     # 修改为
     pbar = tqdm(total=batch_size, desc="批量仿真进度", disable=not self.show_progress)
     ```
  
  3. 修改串行仿真部分（第693-712行）：
     ```python
     # 原代码
     pbar = tqdm(total=batch_size, desc="批量仿真进度")
     # 修改为
     pbar = tqdm(total=batch_size, desc="批量仿真进度", disable=not self.show_progress)
     ```

### 4. `/mnt/f/Work/met_nonlinear/inference/inference_backends.py`

#### 修改点6：传递进度条控制参数
- **位置**：`SPICEBackend` 类的仿真调用
- **修改内容**：在创建 `CircuitSimulation` 实例时传递 `show_progress=False` 参数
- **说明**：需要找到 `SPICEBackend` 类中调用 `CircuitSimulation` 的具体位置，并传递参数以默认关闭进度条

### 5. 全局配置考虑

为了更好地控制终端输出的详细程度，建议：

1. **在 `config.py` 中添加全局配置**：
   ```python
   class Config:
       # ... 现有配置 ...
       verbose_inference = False  # 控制推理过程的详细输出
       show_progress_bar = False  # 控制进度条显示
   ```

2. **环境变量支持**：
   - 支持通过环境变量 `METNL_SHOW_PROGRESS` 控制进度条
   - 支持通过环境变量 `METNL_VERBOSE_INFERENCE` 控制详细输出

3. **命令行参数支持**（可选）：
   - 在 `cli.py` 中添加 `--verbose` 参数
   - 在 `cli.py` 中添加 `--show-progress` 参数

## 实施建议

1. **分阶段实施**
   - 第一阶段：实现数据范围显示（修改点1-4）
   - 第二阶段：解决批量仿真进度条问题（修改点5）

2. **测试方案**
   - 使用提供的测试命令：`python cli.py -i -f WNET5q1h2u6l3`
   - 验证数据范围显示是否正确
   - 确认进度条控制是否生效

3. **配置选项**
   - 考虑添加配置参数来控制详细程度
   - 例如：`--verbose-inference` 显示详细信息
   - `--no-progress-bar` 隐藏进度条

## 注意事项

1. **性能影响**
   - 计算数据范围会有一定的性能开销
   - 对于大数据集，可以考虑采样计算而非全量计算

2. **向后兼容**
   - 确保修改不影响现有功能
   - 保持原有的输出格式，只是添加新信息

3. **错误处理**
   - 处理空数据或异常数据的情况
   - 确保不会因为计算数据范围而导致程序崩溃