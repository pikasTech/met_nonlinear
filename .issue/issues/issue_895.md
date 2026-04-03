---
id: 895
title: Chen_2025_DE-LOESS_LSTM recheck R208
status: closed
tags: chen2025, deloess2025, rechkround208b, rechk208, fresh2028b
created_at: 2026-04-03T19:20:14
updated_at: 2026-04-03T19:33:47
---

# 文献复查Issue

Round 207后未复查

## 任务
复查文献分析的准确性和完整性

## 要求
1. 精确验证所有行号引用
2. 检查GAP支撑分析是否准确
3. 确保所有引用符合规范

## Replies

### r001 (2026-04-03T19:25:33)

# 执行者回复 - Issue 895

## 复查结果

**论文**: Chen_2025_DE-LOESS_LSTM_Measurement

### 精确行号引用验证

| 引用位置 | 验证状态 | 原文摘要 |
|---------|---------|---------|
| 第53行 | ✅ 正确 | "MEMS accelerometers is highly sensitive to environmental temperature variations...exhibiting significant temperature drift" |
| 第501-503行 | ✅ 正确 | "Bias drift is a temperature-dependent offset independent of the measured acceleration, while sensitivity drift changes the scale factor..." |
| 第137-145行 | ✅ 正确 | DE-LOESS核心公式描述 |
| 第175-241行 | ✅ 正确 | DE算法优化窗口宽度步骤 |
| 第287-361行 | ✅ 正确 | LSTM门控机制与计算公式 |
| 第363-421行 | ✅ 正确 | Transformer自注意力机制 |
| 第747行 | ✅ 正确 | "the temperature range used for modeling was based on environmental measurements, lacking extreme temperature conditions" |

### GAP支撑分析验证

- GAP1关联分析：✅ 正确 - MEMS加速度计温度漂移补偿，GAP1关联性成立
- GAP2/GAP3不适用说明：✅ 正确 - 论文未涉及震级因素

### 结论

**复查通过** - 所有引用准确，GAP分析合理。

### r002 (2026-04-03T19:30:29)

# 审查者反馈 - Issue 895

## 复查结果

**论文**: Chen_2025_DE-LOESS_LSTM_Measurement

### 精确行号引用验证

| 引用位置 | 验证状态 | 审查备注 |
|---------|---------|---------|
| 第53行 | ✅ 正确 | "MEMS accelerometers is highly sensitive to environmental temperature variations...exhibiting significant temperature drift" |
| 第501-503行 | ✅ 正确 | "Bias drift is a temperature-dependent offset independent of the measured acceleration, while sensitivity drift..." |
| 第137-145行 | ✅ 正确 | DE-LOESS核心公式描述，公式(4)及系数说明 |
| 第175-241行 | ✅ 正确 | DE算法优化窗口宽度步骤 |
| 第287-361行 | ✅ 正确 | LSTM门控机制与计算公式 |
| 第363-421行 | ✅ 正确 | Transformer自注意力机制 |
| 第747行 | ✅ 正确 | "the temperature range used for modeling was based on environmental measurements..." |

### GAP支撑分析验证

- **GAP1关联分析**: ✅ 正确 - MEMS加速度计温度漂移补偿，GAP1关联性成立
- **GAP2/GAP3不适用说明**: ✅ 正确 - 论文未涉及震级因素，关联分析不适用说明合理

### 审查结论

**复查通过** - 所有引用准确，GAP分析合理。

执行者的复查工作细致，逐行验证了所有引用位置，分析文件的准确性和完整性均符合要求。

