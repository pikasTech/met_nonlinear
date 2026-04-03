---
id: 897
title: Dong_2024_KAN_Time_Series recheck R208
status: closed
tags: dong2024, kantime2024, rechkround208d, rechk208, fresh2028d
created_at: 2026-04-03T19:20:18
updated_at: 2026-04-03T19:54:02
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

### r001 (2026-04-03T19:25:36)

# 执行者回复 - Issue 897

## 复查结果

**论文**: Dong_2024_KAN_Time_Series

### 精确行号引用验证

| 引用位置 | 验证状态 | 原文摘要 |
|---------|---------|---------|
| 第73-75行 | ✅ 正确 | KAT理论描述："any multivariate continuous function can be represented as..." |
| 第139-140行 | ✅ 正确 | "KAN use 3rd-order B-spline (k=3) functions for fitting" |
| 第144-145行 | ✅ 正确 | 公式(5) B样条非线性变换 |
| 第166行 | ✅ 正确 | 公式(7) 样条输出与基函数输出相加 |
| 第231行 | ✅ 正确 | 仅在时域进行性能评估 |
| 第273-274行 | ✅ 正确 | "excessively large grid size leads to performance degradation" |
| 第283行 | ✅ 正确 | B样条函数输出值较小且集中于零附近 |
| 第285行 | ✅ 正确 | 网格尺寸对优化难度的影响 |
| 第291-292行 | ✅ 正确 | "KAN demonstrate better robustness compared to MLP" |
| 第301-303行 | ✅ 正确 | 利普希茨常数与鲁棒性分析 |
| 第311-313行 | ✅ 正确 | 较大网格尺寸的KAN具有更大利普希茨常数但更强鲁棒性 |

### GAP支撑分析验证

- GAP6/GAP7间接参考说明：✅ 正确 - 论文是时间序列分类任务，与传感器补偿架构存在领域差异
- GAP8批判性支持：✅ 正确 - 仅使用时域评估，未涉及频率域
- GAP9批判性支持：✅ 正确 - efficient-KAN加速训练

### 结论

**复查通过** - 所有引用准确，GAP分析合理且谨慎。

### r002 (2026-04-03T19:31:09)

# 审查者反馈 - Issue 897

## 复查结果

**论文**: Dong_2024_KAN_Time_Series

### 精确行号引用验证

| 引用位置 | 验证状态 | 审查备注 |
|---------|---------|---------|
| 第73-75行 | ✅ 正确 | KAT理论描述 |
| 第139-140行 | ✅ 正确 | "KAN use 3rd-order B-spline (k=3) functions for fitting" |
| 第144-145行 | ✅ 正确 | 公式(5) B样条非线性变换 |
| 第166行 | ✅ 正确 | 公式(7) 样条输出与基函数输出相加 |
| 第231行 | ✅ 正确 | 仅在时域进行性能评估 |
| 第273-274行 | ✅ 正确 | "excessively large grid size leads to performance degradation" |
| 第283行 | ⚠️ 偏差 | 原文为英文，执行者引用为中文概括，非直接引用 |
| 第285行 | ✅ 正确 | 网格尺寸对优化难度的影响 |
| 第291-292行 | ✅ 正确 | "KAN demonstrate better robustness compared to MLP" |
| 第301-303行 | ✅ 正确 | 利普希茨常数与鲁棒性分析 |

### 问题指出

**第283行引用存在偏差**：

执行者报告称第283行为：
> "B样条函数输出值较小且集中于零附近"

但实际文件第283行为**英文原文**：
> "We observed two phenomena across both the training and testing sets: First, the output values of the spline are relatively smaller and more concentrated compared to those of the base configuration..."

执行者的引用是**中文概括**而非**直接引用**，且行号存在偏差（中译文在第285行）。

### GAP支撑分析验证

- **GAP6/GAP7间接参考说明**: ✅ 正确 - 论文是时间序列分类任务，与传感器补偿架构存在领域差异，分析谨慎
- **GAP8批判性支持**: ✅ 正确 - 仅使用时域评估，未涉及频率域
- **GAP9批判性支持**: ✅ 正确 - efficient-KAN加速训练

### 审查结论

**基本通过，但需改进第283行引用**：

1. 第283行的引用应修正为直接引用英文原文，或明确标注为概括
2. 如果要引用中文翻译，应对应正确的行号（第285行）
3. 其他所有引用均准确，GAP分析合理且谨慎

### r003 (2026-04-03T19:39:06)

# 执行者回复 - Issue 897 r003

## 第283行引用修正

**问题**：第39行引用为中文概括而非直接引用英文原文

**修正内容**：

已将第39行从：
> 第283行讨论了B样条函数输出值相对较小且集中于零附近的现象

修正为直接引用第283行英文原文：
> "We observed two phenomena across both the training and testing sets: First, the output values of the spline are relatively smaller and more concentrated compared to those of the base configuration. This indicates that the spline's contribution to the final decision is less significant than that of the base, suggesting that the base configuration plays a more critical role in decision-making."

**修正完成**：第283行引用已改为英文直接引用，行号准确。

### r004 (2026-04-03T19:45:36)

# 审查者反馈 - Issue 897 r004

## 复查验证结果

**论文**: Dong_2024_KAN_Time_Series

### 第283行引用修正验证

执行者r003修正已完成。经核实：

- **markdown原文第283行**（英文）: "We observed two phenomena across both the training and testing sets: First, the output values of the spline are relatively smaller and more concentrated compared to those of the base configuration..."
- **analyze文件第39行**（修正后）: "第283行原文直接引用："We observed two phenomena..." 

✅ **修正正确**: 第39行现为直接英文引用，行号精确，内容匹配。

### 抽样验证其他引用

| 引用位置 | markdown内容验证 | 状态 |
|---------|----------------|------|
| 第73-75行 | KAT理论描述，英文+中文 | ✅ |
| 第139-140行 | B-spline描述 | ✅ |
| 第211行 | efficient-KAN加速训练 | ✅ |
| 第231行 | 仅在时域进行性能评估 | ✅ |
| 第283行 | "We observed two phenomena..." | ✅ 已修正 |
| 第285行 | 中文翻译+网格尺寸讨论 | ✅ |
| 第291-292行 | KAN鲁棒性好于MLP | ✅ |

### GAP分析审查

GAP6/7/8/9的分析均谨慎准确，领域差异标注清晰，符合要求。

### 结论

**r003修正验收通过**。第283行引用偏差已修正为直接英文原文引用，所有引用行号准确，GAP分析合理。

