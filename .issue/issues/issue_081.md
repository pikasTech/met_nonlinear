---
id: 081
title: Issue 081: 持续复查发现2个新的P0行号引用错误
status: closed
tags: p0, review, dong, liu, kan
created_at: 2026-03-31T22:21:54
updated_at: 2026-03-31T22:48:09
---

# Issue 081: 持续复查发现2个新的P0行号引用错误

## Issue 类型
P0 - 行号引用错误（违反 PRINCIPLE.md）

## 问题描述

审查者在第二十八阶段持续复查中，随机抽样已关闭 issue 的 analyze 文件进行行号准确性核查，发现以下 P0 错误：

---

### P0-1: Dong_2024_KAN_Time_Series_analyze.md 第37行

**错误类型**：虚假引用（引用内容在原文中不存在）

**analyze 文件声称**（第37行）：
> "第285-291行分析表明B样条能够捕捉Duffing振子的三次刚度非线性，证明KAN可以有效建模非线性动态。"

**原文第285-291行实际内容**：
- 第283-285行：讨论 spline 输出值相对较小且集中，base function 贡献更显著
- 第285-291行：讨论训练/测试集中的两种现象，关于网格大小和输出分布

**问题**：
1. 原文第285-291行**完全没有提及"Duffing振子"或"三次刚度非线性"**
2. 这是一个**虚假引用** - 编造了原文不存在的内容
3. 该错误导致对论文贡献的误判

**修复要求**：
- 删除第37行关于"Duffing振子"的虚假引用
- 找到 B样条能够捕捉非线性动态的正确原文位置进行引用
- 或删除该声称

---

### P0-2: Liu_2024_KAN_analyze.md 第26行

**错误类型**：行号引用错误

**analyze 文件声称**（第26行）：
> "第121行公式(2.1)展示了Kolmogorov-Arnold表示将多元函数分解为单变量函数的叠加"

**事实核查**：
- 公式(2.1)实际位于**第100行**
- 第121行内容是："Suppose we have a supervised learning task..."（监督学习任务描述）

**问题**：
- 行号引用错误：引用第121行，但公式实际在第100行
- 错误相差 **21行**

**修复要求**：
- 将引用行号从"第121行"修正为"第100行"

---

## P0错误判定依据

根据 PRINCIPLE.md：
> 行号引用必须准确，行号引用有任何错误都是 P0 级别的错误

## 执行要求

1. 读取原始 markdown 文件，核实每个引用的正确行号
2. 修正 analyze 文件中的错误引用
3. 确保修正后的引用与原文完全一致
4. 回复本 issue 报告修复进度

## 标签
- p0
- line-reference-error
- review-cycle-continuous
- Dong_2024_KAN_Time_Series
- Liu_2024_KAN

## Replies

### r001 (2026-03-31T22:29:59)

## 审查者补充报告 - Issue 081 新增2个P0致命错误

在 Issue 081 原报告的 2 个 P0 错误基础上，持续复查又发现 2 个 **P0 致命错误** - analyze 文件描述了完全错误的论文：

---

### P0-3: Pozdnyakov_2025_lmKAN_analyze.md - 整个分析文件描述了错误的论文

**错误级别**：P0 - 致命错误

**问题概述**：analyze 文件描述的论文与实际 markdown 文件内容完全不匹配

| 项目 | Analyze 文件声称 | 实际 markdown 文件 |
|------|-----------------|-------------------|
| **标题** | "lmKAN: Learning Mobile KAN for Resource-Constrained Devices" | "Lookup multivariate Kolmogorov-Arnold Networks" |
| **主题** | 面向资源受限设备的可学习移动KAN | 通过查找表实现高维函数逼近的lmKAN |
| **应用** | 移动/嵌入式设备部署 | 参数效率与推理速度优化 |

**问题详情**：
- Analyze 文件第5行声称论文是"面向资源受限设备的可学习移动KAN"
- 但实际论文是关于"通过样条查找表实现高效推理的lmKAN"
- 所有行号引用都是基于错误论文内容进行的，**整个文件无效**

**修复要求**：
- **必须完全重写** Pozdnyakov_2025_lmKAN_analyze.md
- 根据实际论文 "Lookup multivariate Kolmogorov-Arnold Networks" 的内容重新分析
- 正确引用原文行号

---

### P0-4: Shen_2026_KAN_FIF_analyze.md - 整个分析文件描述了错误的论文

**错误级别**：P0 - 致命错误

**问题概述**：analyze 文件描述的论文与实际 markdown 文件内容完全不匹配

| 项目 | Analyze 文件声称 | 实际 markdown 文件 |
|------|-----------------|-------------------|
| **标题** | "KAN-FIF: Kolmogorov-Arnold Network with Feature Interaction Fusion for Indoor Localization" | "KAN-FIF: Spline-Parameterized Lightweight Physics-based Tropical Cyclone Estimation on Meteorological Satellite" |
| **主题** | 用于室内定位的特征交互融合KAN | 气象卫星热带气旋估计 |
| **应用** | 室内定位 | 气象卫星数据分析 |

**问题详情**：
- Analyze 文件第5行声称论文是"用于室内定位的KAN-FIF"
- 但实际论文是关于"基于气象卫星的热带气旋估计"
- 所有行号引用都是基于错误论文内容进行的，**整个文件无效**

**修复要求**：
- **必须完全重写** Shen_2026_KAN_FIF_analyze.md
- 根据实际论文 "Spline-Parameterized Lightweight Physics-based Tropical Cyclone Estimation on Meteorological Satellite" 的内容重新分析
- 正确引用原文行号

---

## Issue 081 完整 P0 错误汇总

| # | 文件 | 错误类型 | 严重程度 |
|---|------|----------|---------|
| 1 | Dong_2024_KAN_Time_Series_analyze.md | 虚假引用（第37行） | P0 |
| 2 | Liu_2024_KAN_analyze.md | 行号错误（第26行，121→100） | P0 |
| 3 | Pozdnyakov_2025_lmKAN_analyze.md | **整个文件描述错误论文** | **P0-致命** |
| 4 | Shen_2026_KAN_FIF_analyze.md | **整个文件描述错误论文** | **P0-致命** |

---

*审查者 STEP3 r020 - 2026-03-31 22:28*

### r002 (2026-03-31T22:31:19)

## 审查者补充报告 - Issue 081 新增 Somvanshi P0 错误

持续复查还发现 Somvanshi_2025_KAN_Survey_analyze.md 存在 P0 错误：

---

### P0-5: Somvanshi_2025_KAN_Survey_analyze.md

**两处 P0 错误**：

**错误 A (第42行) - 事实性错误**：
- **analyze 声称**：第25-28行包含 "KAN provides better interpretability compared to traditional MLPs through its node-wise activation functions"
- **实际问题**：
  1. 短语 "node-wise activation functions" 在原文中**不存在**
  2. 原文第25行实际说的是 "adaptive **edge-based** activation functions"（基于自适应边缘的激活函数）
  3. KAN 的核心特征是 **edge-wise** 激活函数，而非 node-wise
  4. 这是对 KAN 基本概念的事实性错误

**错误 B (第43行) - 虚假引用**：
- **analyze 声称**：第45-48行包含 "KAN has shown promising results in time series analysis tasks"
- **原文第45-48行实际内容**：
  - 第45行：## 1 Introduction（章节标题）
  - 第46行：## 1引言（中文标题）
  - 第47-48行：Introduction 的开头几句，关于 Kolmogorov-Arnold Networks 的介绍
- **问题**：该短语**完全不存在**于第45-48行

**修复要求**：
1. 第42行：将 "node-wise" 修正为 "edge-based"，并确保引用准确
2. 第43行：找到关于时间序列内容的正确行号，或删除该声称

---

## Issue 081 完整 P0 错误汇总（共5个）

| # | 文件 | 错误类型 | 严重程度 |
|---|------|----------|---------|
| 1 | Dong_2024_KAN_Time_Series_analyze.md | 虚假引用（第37行） | P0 |
| 2 | Liu_2024_KAN_analyze.md | 行号错误（第26行，121→100） | P0 |
| 3 | Pozdnyakov_2025_lmKAN_analyze.md | **整个文件描述错误论文** | **P0-致命** |
| 4 | Shen_2026_KAN_FIF_analyze.md | **整个文件描述错误论文** | **P0-致命** |
| 5 | Somvanshi_2025_KAN_Survey_analyze.md | 事实错误+虚假引用（第42-43行） | P0 |

---

*审查者 STEP3 r021 - 2026-03-31 22:35*

### r003 (2026-03-31T22:39:36)

## Issue 081 P0 错误修复进展报告

所有5个P0错误已修复完成：

### 已修复

1. **P0-1 (Dong_2024)**: 删除了第37行虚假的"Duffing振子"引用（原文中无此内容）

2. **P0-2 (Liu_2024)**: 修正第26行公式(2.1)的行号引用 121→100

3. **P0-3 (Pozdnyakov)**: 完全重写文件，正确描述"Lookup multivariate Kolmogorov-Arnold Networks"（EPFL），而非移动KAN

4. **P0-4 (Shen)**: 完全重写文件，正确描述"KAN-FIF: Spline-Parameterized Lightweight Physics-based Tropical Cyclone Estimation"（山东大学/复旦大学），而非室内定位

5. **P0-5 (Somvanshi)**: 
   - 第25行"node-wise"已更改为"edge-based"（原文）
   - 第42-43行时间序列引用已更正为第391-393行

### 修改文件列表

- `docs/research/literature/analyze/Dong_2024_KAN_Time_Series_analyze.md`
- `docs/research/literature/analyze/Liu_2024_KAN_analyze.md`
- `docs/research/literature/analyze/Pozdnyakov_2025_lmKAN_analyze.md`
- `docs/research/literature/analyze/Shen_2026_KAN_FIF_analyze.md`
- `docs/research/literature/analyze/Somvanshi_2025_KAN_Survey_analyze.md`

所有P0错误已修复，请进行STEP3审查。

### r004 (2026-03-31T22:42:20)

## 审查者复审报告 - Issue 081

### 复审结论

执行者r003报告的5个P0错误修复已全部核实。

---

### P0-1 (Dong_2024) ✅ 已修复

**原错误**：第37行虚假引用"第285-291行分析表明B样条能够捕捉Duffing振子的三次刚度非线性"

**现第37行内容**：
> "第283-285行讨论了B样条函数输出值相对较小且集中于零附近的现象，第285-291行进一步分析了网格尺寸对优化难度的影响。"

**核查结果**：
- 原文中第283-285行确实讨论了spline输出值较小且集中于零的现象
- 第285-291行确实讨论了网格尺寸对优化难度的影响
- "Duffing振子"虚假引用已删除，改为准确的原文内容描述
- ✅ 修复有效

---

### P0-2 (Liu_2024) ✅ 已修复

**原错误**：第26行引用"第121行公式(2.1)"

**现第26行内容**：
> "第100行公式(2.1)展示了Kolmogorov-Arnold表示将多元函数分解为单变量函数的叠加"

**核查结果**：
- 原文第100行确实为公式(2.1)
- 公式内容为 f(x) = Σ Φ_q(Σ φ_q,p(x_p))，确实是Kolmogorov-Arnold表示
- ✅ 行号从121修正为100，修复有效

---

### P0-3 (Pozdnyakov_2025) ✅ 已修复

**原错误**：整个文件描述了错误的论文（移动KAN vs 实际为EPFL的lmKAN）

**核查结果**：
- 标题已修正为"Lookup multivariate Kolmogorov-Arnold Networks"
- 机构已修正为"École Polytechnique Fédérale de Lausanne (EPFL)"
- 行55-57的O(1)查找表描述与原文一致
- 行277-279的"2× FLOPs"描述与原文一致
- ✅ 完全重写有效，文件现正确描述实际论文内容

---

### P0-4 (Shen_2026) ✅ 已修复

**原错误**：整个文件描述了错误的论文（室内定位KAN vs 实际为气象卫星热带气旋估计）

**核查结果**：
- 标题已修正为"KAN-FIF: Spline-Parameterized Lightweight Physics-based Tropical Cyclone Estimation on Meteorological Satellite"
- 机构已修正为"山东大学、浙江工业大学、复旦大学"（与原文一致）
- 行327-329的KAN四方面集成描述与原文一致
- 行609-611的性能数据（94.8%参数减少、68.7%推理时间减少）与原文一致
- ✅ 完全重写有效，文件现正确描述实际论文内容

---

### P0-5 (Somvanshi_2025) ✅ 已修复

**原错误A**：第42行"node-wise activation functions"（应为"edge-based"）

**现第42行内容**：
> "KAN在可解释性方面优于MLP（原文第25行）："adaptive edge-based activation functions..."

**核查结果**：
- 原文第25行确实包含"adaptive edge-based activation functions"
- "node-wise"已修正为"edge-based"
- ✅ 修复有效

**原错误B**：第43行引用"第45-48行包含KAN时间序列内容"（虚假引用）

**现第43行内容**：
> "KAN在时间序列预测方面有应用（原文第391-393行）："T-KAN专为单变量时间序列数据设计..."

**核查结果**：
- 原文第391-393行确实包含T-KAN用于单变量时间序列数据的描述
- ✅ 行号从45-48修正为391-393，修复有效

---

### 审查意见

1. **Dong_2024行37**：虽然虚假引用已删除，但GAP支撑结论（原79行）中仍有"证明了B样条函数能够捕捉三次刚度等非线性特征"的声称，这一声称缺乏原文支撑，建议一并删除

2. 其余4个P0错误修复均有效

*审查者 STEP3 - 2026-03-31 22:40*

### r005 (2026-03-31T22:44:10)

## 审查者新发现问题 - Issue 081 继续

审查者复审 r004 确认 P0-1~P0-5 均已修复，但发现新问题：

### Dong_2024_KAN_Time_Series_analyze.md 第79行

**审查者意见**：
> "虽然虚假引用已删除，但GAP支撑结论（原79行）中仍有'证明了B样条函数能够捕捉三次刚度等非线性特征'的声称缺乏原文支撑，建议一并删除"

**修复要求**：
1. 检查第79行附近关于"三次刚度"的声称
2. 找到原文支撑或删除该声称
3. 回复修复进展

**标签**：
- p0
- review
- dong
- fix-in-progress

### r006 (2026-03-31T22:45:47)

## 执行者修复报告 - Issue 081 第79行问题

### 问题核实

审查者 r005 指出的问题属实：

**原第78行内容**：
> "展示了B样条函数能够捕捉三次刚度等非线性特征"

**问题**：原文 Dong_2024_KAN_Time_Series.md 中**完全没有**提及"三次刚度"(cubic stiffness)。该论文研究的是时间序列分类任务，使用B样条函数作为可学习激活函数进行通用函数拟合，但从未涉及Duffing振子或三次刚度等非线性动力学概念。

### 修复内容

已将第78行修改为：

> "展示了B样条函数的非线性变换能力（公式5，第139-145行）"

**修改说明**：原文第139-145行确实描述了KAN使用3rd-order B-spline函数进行拟合，通过控制每个基函数的权重来学习复杂的激活函数。这是原文中有明确记载的内容，与"捕捉三次刚度"的虚假声称不同。

### 修复文件

- `docs/research/literature/analyze/Dong_2024_KAN_Time_Series_analyze.md`

请审查者进行复核。

### r007 (2026-03-31T22:47:02)

## 审查者复核报告 - Issue 081 第79行问题

### 复核结论

执行者 r006 修复有效。

### 核查结果

**原第78行问题**：声称"展示了B样条函数能够捕捉三次刚度等非线性特征"（原文无"三次刚度"内容）

**现第78行内容**：
> "展示了B样条函数的非线性变换能力（公式5，第139-145行）"

**原文第139-145行核查**：
- 第139行：明确说明"KAN use ${3}^{rd}$-order B-spline ... functions for fitting, which allows learning sophisticated activation function by controlling the weight of each basis"
- 第143-145行：包含公式(5)，展示B-spline的数学表达式

**修复评价**：
- "三次刚度"虚假声称已删除
- 替换为原文有明确记载的"B样条函数非线性变换能力"
- 行号引用139-145准确
- 修复有效，Issue 081 全部P0错误已解决

*审查者 STEP3 - 2026-03-31 22:46*

