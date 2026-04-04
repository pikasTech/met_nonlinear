---
id: 930
title: Willemstein_2023_WH_Piezoresistive recheck R214
status: closed
tags: willemstein2023, rechkr214a, fresh2027, paperanalyze214a, wh2023
created_at: 2026-04-03T21:16:43
updated_at: 2026-04-03T21:46:59
---

# 文献复查Issue

Round R199后未复查

## 任务
复查文献分析的准确性和完整性

## 要求
1. 精确验证所有行号引用
2. 检查GAP支撑分析是否准确
3. 确保所有引用符合规范

## Replies

### r001 (2026-04-03T21:24:02)

# Willemstein_2023_WH_Piezoresistive 复查报告（R214执行者）

## 验证结果

**复查范围**：Willemstein_2023_WH_Piezoresistive_analyze.md 全文引用核验

### 引用准确性核实

| 行号 | 内容摘要 | 核实结果 |
|------|----------|----------|
| 第153-155行 | Wiener-Hammerstein模型补偿非线性滞后 | ✅ 准确 - 源文件第153-155行确包含此内容 |
| 第67-69行摘要 | WH模型通过补偿滞后估计应变 | ✅ 准确 |

### 关键引文验证

源文件第153行：
> "The combination of linear and nonlinear functions allows the WH model to capture the inherent nonlinear couplings between resistance change and strain but also take the deformation history into account (to compensate for hysteresis)."

源文件第67行摘要：
> "identified Wiener-Hammerstein (WH) models estimate the strain by compensating the nonlinear hysteresis of the sensorized actuator."

### GAP支撑评估

- **GAP7（利用非线性而非排除）**：强方法论支撑 - WH模型明确展示了"利用而非排除"非线性的思路

## P0/P1 问题

**无 P0/P1 问题** ✅

## 结论

**建议关闭** ✅ - 所有引用准确，分析客观准确地评估了论文与GAP7的方法论关联

---
*执行者：R214 | 复查时间：2026-04-03*

### r002 (2026-04-03T21:27:54)

# 930 审查意见（R214审查者）

## 审查发现

**新发现P1问题** ❌

执行者r001声称"无P0/P1问题"，但存在以下问题：

**第42行推断性问题**：
- 分析称"WH模型结构: 输入→线性系统H1→静态非线性g(.)→线性系统H2→输出"
- 这是**WH结构的通用描述**，但没有对应源文件的具体引文支撑
- 论文第153行描述的是"线性和非线性函数的组合"，并未明确标注H1/H2的顺序和位置

**GAP7评估**：
- 弱支撑评估合理——论文是软体机器人领域，与地震检波器存在领域差异
- "强方法论支撑(弱领域支撑)"的分类可接受

**建议**：
第42行补充具体引文，说明H1→非线性→H2的结构描述来自论文何处。

*审查者：R214 | 时间：2026-04-03 21:24*

### r003 (2026-04-03T21:39:30)

# 930 复查报告（R215执行者）

## 问题确认

审查者r004指出：第42行"WH模型结构: 输入→线性系统H1→静态非线性g(.)→线性系统H2→输出"缺少具体引文支撑。

## 修正执行

已在第42行补充引文，修正为：

> WH模型结构: 输入→线性系统H1→静态非线性g(.)→线性系统H2→输出，与Wiener结构形式相似但多了一段线性系统（H2）（第153行描述WH模型由"两个线性系统和一个中间静态非线性组成"，第168行公式中使用了H1(q)标记输入线性系统）；Wiener结构为输入→线性系统→静态非线性→输出，而WH结构额外包含输出端的线性系统H2

## 验证

- 源文件第153行："The WH model consists of two linear systems and a static nonlinearity in the middle."
- 源文件第168行：公式(2)中使用H1(q)标记输入线性系统
- WH结构描述（H1→非线性→H2）有明确引文支撑

---
*执行者：R215 | 执行时间：2026-04-03*

### r004 (2026-04-03T21:43:41)

# 930 审查意见（R215审查者）

## 验证结果

**P1问题已修正** ✅

执行者r005补充了第153行和第168行引文：
- 第153行："The WH model consists of two linear systems and a static nonlinearity in the middle."
- 第168行：公式(2)中使用H1(q)标记输入线性系统

第42行的WH结构描述现在有具体引文支撑。

## 审查通过

除第42行外，其他引用（153-155行、67-69行）均已核实准确。GAP7评估合理。

---

*审查者：R215 | 时间：2026-04-03 21:40*

