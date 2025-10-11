# 快速推理优化调研报告

**日期**: 2025-07-10  
**作者**: Claude  
**目标**: 为 `cli.py -i` 实现快速推理功能，只加载最小和最大震级数据

## 1. 背景和需求

当前的推理系统在使用 `cli.py -i` 进行推理时，会加载大量的震级数据（约25个震级），这导致推理速度较慢。为了优化推理性能，我们希望实现一个快速推理模式，只加载最小和最大两个震级的数据。

## 2. 现状分析

### 2.1 当前数据加载流程

1. **数据加载入口**: `ModelEngine.load_dataset()` 方法
   - 位置: `core/model_engine.py:52`
   - MET数据集使用 `sweep_list = range(1, 50, 2)` 加载奇数索引的扫描数据

2. **震级数据结构**:
   ```python
   # data_info.magnitude 存储震级值
   # sweep_list 包含要加载的数据索引
   # magn_list 收集所有选中的震级值
   for i in sweep_list:
       data_info = data_info_list[i]
       magnitude.append(data_info.magnitude)
   ```

3. **数据维度**:
   - 输入输出数据形状: `(magn_num, freq_num, points_num)`
   - `magn_num`: 震级数量（当前约25个）
   - `freq_num`: 频率数量
   - `points_num`: 时间序列点数

### 2.2 推理数据生成流程

1. **入口函数**: `cli.py -i` → `ProjectManager.run_inference()`
2. **推理管理器**: `InferenceManager` 负责生成推理数据
3. **数据查找**: 从 `data/wave_output/dataset_MET_output_original.wave` 加载数据
4. **问题点**: 当前会加载所有训练时使用的震级数据

## 3. 技术方案

### 方案一：添加快速推理模式参数（推荐）

**实现思路**:
1. 在配置中添加 `fast_inference_mode` 参数
2. 修改 `ModelEngine.load_dataset()` 方法，根据模式选择不同的 `sweep_list`
3. 在快速模式下，先加载所有 `data_info_list`，找出最小和最大震级的索引

**关键代码修改**:
```python
# core/model_engine.py
def load_dataset(self, dataset_type='MET'):
    if dataset_type == 'MET':
        data_info_list = find_data_info(data_path)
        
        # 快速推理模式：只选择最小和最大震级
        if hasattr(self.config, 'fast_inference_mode') and self.config.fast_inference_mode:
            # 获取所有震级值
            all_magnitudes = [info.magnitude for info in data_info_list]
            min_idx = np.argmin(all_magnitudes)
            max_idx = np.argmax(all_magnitudes)
            sweep_list = [min_idx, max_idx]
            print(f"快速推理模式：只加载震级 {all_magnitudes[min_idx]} 和 {all_magnitudes[max_idx]}")
        else:
            # 标准模式
            sweep_list = range(1, 50, 2)
```

**优点**:
- 实现简单，改动最小
- 向后兼容，不影响现有功能
- 可通过配置灵活控制

**缺点**:
- 需要先加载所有 data_info 来确定最小最大值
- 需要修改配置文件结构

### 方案二：命令行参数控制

**实现思路**:
1. 添加 `-if` (inference fast) 命令行参数
2. 在 `ProjectManager` 中传递快速模式标志
3. 在数据加载时根据标志选择震级

**关键代码修改**:
```python
# cli.py
if '-if' in sys.argv:
    task_type = 'inference'
    fast_inference = True

# 传递到 ProjectManager
project.run_inference(force=force_mode, fast_mode=fast_inference)
```

**优点**:
- 用户使用方便，一个命令即可
- 不需要修改配置文件

**缺点**:
- 需要修改多个函数签名
- 参数传递链较长

### 方案三：独立的快速推理数据集类

**实现思路**:
1. 创建 `Dataset_COMP_MET_Fast` 类
2. 该类自动只加载最小和最大震级
3. 在推理时根据模式选择不同的数据集类

**关键代码**:
```python
class Dataset_COMP_MET_Fast(Dataset_COMP_MET):
    def __init__(self, data_info_list, target_sweep, **kwargs):
        # 找出最小最大震级的索引
        all_magnitudes = [info.magnitude for info in data_info_list]
        min_idx = np.argmin(all_magnitudes)
        max_idx = np.argmax(all_magnitudes)
        
        # 只使用这两个索引
        sweep_list = [min_idx, max_idx]
        
        super().__init__(
            data_info_list,
            target_sweep,
            sweep_list,
            **kwargs
        )
```

**优点**:
- 职责分离，代码清晰
- 易于扩展和维护

**缺点**:
- 需要创建新类
- 可能导致代码重复

## 4. 实施建议

### 4.1 推荐方案

推荐采用**方案一**（添加快速推理模式参数），原因如下：

1. **改动最小**: 只需要修改少量代码
2. **灵活性高**: 可通过配置控制，便于测试和调试
3. **向后兼容**: 不影响现有功能
4. **易于扩展**: 未来可以添加更多推理优化选项

### 4.2 实施步骤

1. **第一阶段**: 在配置中添加 `fast_inference_mode` 参数
2. **第二阶段**: 修改 `ModelEngine.load_dataset()` 实现快速模式
3. **第三阶段**: 在 `cli.py` 中添加命令行支持（可选）
4. **第四阶段**: 测试验证推理结果的一致性

### 4.3 测试计划

1. **功能测试**:
   - 验证快速模式只加载两个震级
   - 验证推理结果的正确性
   - 验证与标准模式的兼容性

2. **性能测试**:
   - 对比快速模式和标准模式的加载时间
   - 对比推理速度提升比例
   - 验证内存使用减少情况

3. **边界测试**:
   - 测试数据文件缺失的情况
   - 测试只有一个或两个震级的特殊情况

## 5. 预期效果

实施快速推理模式后，预期能够实现：

1. **性能提升**: 数据加载时间减少约 90%（从25个震级减少到2个）
2. **内存优化**: 内存使用减少约 90%
3. **推理加速**: 整体推理速度提升 5-10 倍
4. **使用简便**: 用户可通过简单配置启用快速模式

## 6. 风险和注意事项

1. **精度影响**: 只使用最小最大震级可能影响中间震级的推理精度
2. **兼容性**: 需要确保不影响现有的训练和评估流程
3. **数据完整性**: 需要确保最小最大震级的数据质量良好

## 7. 总结

通过实现快速推理模式，我们可以显著提升 `cli.py -i` 的推理性能。推荐采用配置参数控制的方案，这样既能保持系统的灵活性，又能最小化对现有代码的影响。实施后需要进行充分的测试，确保推理结果的准确性和系统的稳定性。