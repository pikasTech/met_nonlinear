# 电阻标准化相对误差校验修改计划

## 问题分析

### 当前问题
1. **绝对误差误导性统计**：31.5MΩ电阻产生147万欧绝对误差，但相对误差仅4.675%完全合理
2. **过滤逻辑违反校验原则**：代码在两处过滤掉1GΩ电阻，违背完全校验要求
3. **统计指标不合理**：绝对误差对大电阻值不具备工程意义

### 核心需求
- **只校验相对误差**：移除所有绝对误差统计和校验
- **完全校验覆盖**：对所有380个电阻进行相对误差校验，包括133个1GΩ电阻
- **工程意义导向**：相对误差更符合电阻标准化的工程要求

## 修改计划

### 文件1: `spice_simulator/resistance_standardizer.py`

**修改位置**: `analyze_errors()` 方法 (第140-179行)

**当前问题**:
```python
# 第153行 - 错误的过滤逻辑
mask = (original < 1e9) & (original != float('inf')) & (standardized < 1e9) & (standardized != float('inf'))

# 第174-175行 - 不需要的绝对误差统计
'mean_error': float(errors.mean()),
'max_error': float(errors.max()),
```

**修改方案**:
```python
# 移除绝对值过滤，保留必要的无效值过滤
mask = (original != 0) & (original != float('inf')) & (standardized != float('inf')) & (~np.isnan(original)) & (~np.isnan(standardized))

# 只返回相对误差统计
return {
    'total_resistors': len(original),
    'validated_resistors': len(original_filtered),
    'mean_relative_error': float(relative_errors.mean()),
    'max_relative_error': float(relative_errors.max()),
    'within_1pct': float((relative_errors < 1).sum() / len(relative_errors) * 100),
    'within_5pct': float((relative_errors < 5).sum() / len(relative_errors) * 100),
    'within_10pct': float((relative_errors < 10).sum() / len(relative_errors) * 100)
}
```

### 文件2: `core/tasks/resistance_task.py`

**修改位置1**: `_generate_analysis_report()` 方法 (第456-496行)

**当前问题**:
```python
# 第476行 - 错误的过滤逻辑
valid_mask = df['value'] < 1e9
valid_df = df[valid_mask]
```

**修改方案**:
```python
# 移除过滤，对所有电阻进行分析
valid_df = df  # 完全校验，不过滤任何电阻
```

**修改位置2**: `standardize_existing_csv()` 方法 (第252-327行)

**当前问题**:
```python
# 第315行 - 错误的过滤逻辑
valid_errors = df[df['value'] < 1e9][error_col]
```

**修改方案**:
```python
# 移除过滤，计算所有电阻的相对误差
valid_errors = df[error_col]  # 包含所有电阻的误差
```

### 文件3: `projects/WNET5q1h2u6l3/data/resistance_tables/standardization_analysis.json`

**当前输出问题**:
```json
{
  "mean_error": 768.2,        // 移除绝对误差
  "max_error": 128564.4,      // 移除绝对误差  
  "mean_relative_error": 0.375,  // 保留
  "max_relative_error": 1.68,    // 保留
  "within_5pct": 100.0           // 保留并扩展
}
```

**预期输出**:
```json
{
  "total_resistors": 380,
  "validated_resistors": 380,
  "mean_relative_error": 0.375,
  "max_relative_error": 1.68,
  "within_1pct": 95.2,
  "within_5pct": 100.0,
  "within_10pct": 100.0
}
```

## 修改步骤

### 步骤1: 修改标准化器核心逻辑
1. 编辑 `spice_simulator/resistance_standardizer.py`
2. 修改 `analyze_errors()` 方法移除绝对误差统计
3. 移除1GΩ过滤逻辑，确保完全校验

### 步骤2: 修改任务处理器
1. 编辑 `core/tasks/resistance_task.py` 
2. 修改 `_generate_analysis_report()` 移除过滤
3. 修改 `standardize_existing_csv()` 移除过滤

### 步骤3: 验证修改效果
1. 运行 `python cli.py export-resistance --standardized` 
2. 检查生成的 `standardization_analysis.json`
3. 验证380个电阻全部被校验
4. 确认只输出相对误差统计

### 步骤4: 回归测试
1. 对比网表与CSV电阻值一致性
2. 验证1GΩ电阻被正确处理 
3. 确认相对误差统计合理

## 预期效果

### 修改前问题
- 绝对误差: 768.2Ω平均, 128564.4Ω最大 (误导性)
- 过滤133个1GΩ电阻 (违反完全校验)
- 统计不反映工程实际需求

### 修改后效果  
- **只统计相对误差**: 平均0.375%, 最大1.68% (工程意义)
- **完全校验覆盖**: 380个电阻全部校验 (符合要求)
- **分级统计**: 1%/5%/10%误差分布 (更详细)

## 风险评估

### 低风险
- 相对误差计算逻辑成熟稳定
- 不影响网表生成和CSV导出核心功能
- 只改变统计报告格式，不改变数据

### 无风险
- UnifiedResistanceCalculator架构保证数据一致性
- 移除过滤逻辑提高校验完整性
- 相对误差更符合电阻工程标准

## 验证标准

### 成功标准
1. **完全校验**: 所有380个电阻被校验，无过滤
2. **相对误差导向**: 只输出相对误差统计指标
3. **工程合理性**: within_5pct接近100%体现标准化质量
4. **数据一致性**: 网表与CSV电阻值完全一致

### 验收测试
```bash
# 重新生成标准化分析
python cli.py export-resistance --project WNET5q1h2u6l3 --standardized

# 验证结果
# 1. standardization_analysis.json只包含相对误差
# 2. total_resistors = 380 (完全覆盖)
# 3. within_5pct 接近 100% (质量良好)
```

## 实施时机
- 当前阶段立即实施
- 修改涉及统计逻辑，不影响核心推理功能
- 可与现有架构无缝集成