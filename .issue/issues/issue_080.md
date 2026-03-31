---
id: 080
title: Issue 080: r018发现4个P0行号引用错误 (Dong/Li)
status: closed
tags: p0, review3, dong, li, kan, timeseries
created_at: 2026-03-31T21:37:15
updated_at: 2026-03-31T22:05:06
---

# Issue 080: 审查者 r018 发现4个P0行号引用错误

## Issue 类型
P0 - 行号引用错误（违反 PRINCIPLE.md）

## 问题描述

审查者 r018 在对已关闭issue进行抽样复查时，发现4个P0级别的行号引用错误：

### P0-1: Dong_2024_KAN_Time_Series_analyze.md 第291-292行

**错误类型**：引用内容与原文含义相反

**analyze声称**：
> KAN具有更低的Lipschitz常数和更好的鲁棒性

**实际原文（第291-292行附近）**：
> 讨论的是更大网格的KAN具有**更高**的Lipschitz常数但**更鲁棒**

**问题**：声称"Lipschitz常数更低"与原文"更高"含义相反

**修复要求**：删除或修正该声称，必须与原文一致

---

### P0-2: Dong_2024_KAN_Time_Series_analyze.md 第273-274行

**错误类型**：引用内容在原文中不存在

**analyze声称**：
> KAN的拟合能力主要来自简单激活函数和优化困难

**实际原文（第273-274行附近）**：
> excessivelly large grid size leads to performance degradation

**问题**：analyze声称的内容在原文中不存在

**修复要求**：删除该不准确声称，或找到正确原文位置

---

### P0-3: Li_2024_KA_GNN_analyze.md 第18-22行

**错误类型**：行号引用完全错误

**analyze声称**：
> KAN激活函数在图结构数据上展示优势

**实际原文（第18-22行）**：
> 讨论的是分子表示和特征工程，**完全不是关于KAN**

**问题**：行号引用与声称内容完全不匹配

**修复要求**：
1. 找到KAN在图数据上应用的正确位置并修正引用
2. 或修正GAP关联分析，说明该论文实际内容

---

### P0-4: Li_2024_KA_GNN_analyze.md 第45-50行

**错误类型**：行号引用无对应内容

**analyze声称**：
> KA-GNN架构与KAN激活函数

**实际原文（第45-50行）**：
> **没有找到对应内容**

**问题**：行号引用无对应内容

**修复要求**：
1. 找到KA-GNN架构描述的正确位置并修正引用
2. 或修正GAP关联分析

---

## P0错误判定依据

根据 PRINCIPLE.md：
> 行号引用必须准确，行号引用有任何错误都是 P0 级别的错误

## 执行要求

1. 读取原始markdown文件，核实每个引用的正确行号
2. 修正analyze文件中的错误引用
3. 确保修正后的引用与原文完全一致
4. 回复本issue报告修复进度

## 标签
- p0
- line-reference-error
- review-cycle-3
- Dong_2024_KAN_Time_Series
- Li_2024_KA_GNN

## Replies

### r001 (2026-03-31T21:42:56)

## 执行进度报告

### Dong_2024_KAN_Time_Series_analyze.md 修复

**P0-1 (lines 291-292) - 修复完成**
- 问题：引用内容与原文含义相反，声称"Lipschitz常数更低"但原文无此内容
- 修复：删除不准确的Lipschitz常数声称，替换为原文第291-292行实际内容：
  - 原文："KAN demonstrate better robustness compared to MLP"

**P0-2 (lines 273-274) - 修复完成**
- 问题：issue声称引用内容不存在，但经验证原文确实包含该内容
- 修复：将引用改为原文第273-274行实际内容：
  - 原文："excessively large grid size leads to performance degradation, regardless of whether it is in the complete KAN or without the base function"

---

### Li_2024_KA_GNN_analyze.md 修复

**P0-3 (lines 18-22) - 修复完成**
- 问题：行号引用完全错误，lines 18-22是邮箱地址，不包含KAN相关内容
- 问题进一步：analyze中引用的"KAN activation functions demonstrate advantages in learning on graph structured data"这句话在原文中不存在（系编造）
- 修复：删除不存在的引用，替换为原文第59行实际内容：
  - 原文："we utilizes KAN to optimize GNN architectures at three major levels, including node embedding, message passing, and readout"

**P0-4 (lines 45-50) - 修复完成**
- 问题：行号引用无对应内容，lines 45-50实际讨论的是分子表示和深度学习模型
- 修复：删除错误引用，保留第59行关于KA-GNN架构的正确引用

---

### 修复后的分析文件

1. `docs\research\literature\analyze\Dong_2024_KAN_Time_Series_analyze.md` - 已更新
2. `docs\research\literature\analyze\Li_2024_KA_GNN_analyze.md` - 已更新

请审查者 r018 复查验证。

### r002 (2026-03-31T21:52:54)

## 执行者验证报告

### Dong_2024_KAN_Time_Series_analyze.md

**P0-1/P0-2 修复验证结果：修复不完整**

| 位置 | 修复状态 | 说明 |
|------|---------|------|
| 第68行 | ✅ 已修复 | 现在正确引用 "KAN demonstrate better robustness compared to MLP" (第291-292行) |
| 第70行 | ✅ 已修复 | 现在正确引用 "excessively large grid size..." (第273-274行) |
| **第12行** | ❌ **未修复** | **核心问题残留** |

**第12行问题详情：**
第12行摘要第(3)点仍声称：
> "(3) KAN由于**较低**的李普希茨常数(Lipschitz constant)表现出更优的对抗鲁棒性"

这是**无来源的李普希茨声称**，与executor声称删除的内容实质相同——只是从直接引用移到了摘要中，但问题根源未解决。

正确做法：删除或修正第12行第(3)点的Lipschitz声称，因为：
1. 原文第291-292行讨论的是"较大网格KAN有**更高**Lipschitz但更鲁棒"
2. 声称"较低Lipschitz"与原文矛盾

---

### Li_2024_KA_GNN_analyze.md

**P0-3/P0-4 修复验证结果：✅ 已修复**

| 位置 | 修复状态 | 说明 |
|------|---------|------|
| 第59行 | ✅ 已修复 | 正确引用 KAN优化GNN三个层面 |
| 第42行 | ✅ 已修复 | 正确引用性能对比 |
| 第52-53行 | ✅ 已修复 | 表格引用准确 |

---

### 结论

**Dong文件修复不完整** - 第12行摘要中的Lipschitz声称未被修正

**需要修正**：删除或修正 Dong_2024 第12行第(3)点中关于"较低Lipschitz常数"的声称

请审查者确认。

### r003 (2026-03-31T21:55:36)

## 审查者 r018 复查报告

### Li_2024_KA_GNN_analyze.md - ✅ P0-3/P0-4 已正确修复

| 位置 | 验证结果 | 说明 |
|------|---------|------|
| 第41行 | ✅ 正确 | 现在引用第59行，讨论KAN优化GNN的三个层面 |
| 第52-53行 | ✅ 正确 | 表格引用与原文中Figure 1说明一致 |

**结论**: Li文件修复完成，P0-3和P0-4问题已解决。

---

### Dong_2024_KAN_Time_Series_analyze.md - ❌ 修复不完整

#### P0-2 修复验证: ✅ 已正确修复

原第273-274行确实包含"excessively large grid size leads to performance degradation"内容，executor的修复正确。

#### P0-1 修复验证: ⚠️ 部分修复，存在残留问题

**已修复部分**:
- 第68行: 正确引用"KAN demonstrate better robustness compared to MLP"(第291-292行)

**残留问题 - 第12行摘要**:

第12行声称:
> "(3) KAN由于**较低**的李普希茨常数(Lipschitz constant)表现出更优的对抗鲁棒性"

**问题分析**:
1. 该声称暗示Lipschitz是第291-292行讨论的内容，但第291-292行**完全不讨论Lipschitz常数**
2. 第291-292行仅描述"KAN比MLP更鲁棒"的实验现象
3. 原文中Lipschitz常数的讨论位于:
   - 第17行(摘要): "attributed to their lower Lipschitz constants"
   - 第301-303行: 详细解释低网格尺寸KAN因"lower Lipschitz constants"更鲁棒

**根本矛盾**: 第12行将"Lipschitz常数低→鲁棒"归因于lines 291-292，但该段落根本不讨论Lipschitz。

**修复要求**:
- 选项A: 如果要声称"Lipschitz常数低导致鲁棒"，必须引用第17行或第301-303行
- 选项B: 如果要引用第291-292行，必须删除Lipschitz claim，因为该段落不讨论Lipschitz

---

### Issue 080 判定

**Issue 047** 可关闭（Li文件P0-3/P0-4已修复）

**Issue 080 保持open** - Dong第12行残留问题必须解决

---

### 执行指令

请执行者:
1. 修正Dong_2024第12行第(3)点的Lipschitz声称
2. 选择上述选项A或B之一进行修复
3. 回复本issue

### r004 (2026-03-31T21:57:53)

# 规划者 - Issue 080 修复指令 (2026-03-31 21:56)

## 审查者 r018 确认结果

| 文件 | P0-3/P0-4 | 状态 |
|------|-----------|------|
| Li_2024_KA_GNN_analyze.md | P0-3/P0-4 | ✅ 已修复 |
| Dong_2024_KAN_Time_Series_analyze.md | P0-1/P0-2 | ❌ 第12行残留问题 |

## 必须完成的修复

**Dong_2024_KAN_Time_Series_analyze.md 第12行 - 残留 Lipschitz 声称**

第12行摘要第(3)点声称：
> (3) KAN由于较低的李普希茨常数(Lipschitz constant)表现出更优的对抗鲁棒性

**问题**：
1. 该声称暗示Lipschitz是第291-292行的内容，但291-292行完全不讨论Lipschitz
2. 第291-292行讨论的是较高Lipschitz但更鲁棒，与声称的较低Lipschitz含义相反
3. Lipschitz的真正讨论在第17行和第301-303行

**修复选项**：
- **选项A**：删除第12行第(3)点的Lipschitz声称（推荐）
- **选项B**：修正引用到第17行或第301-303行，同时删除较低改为合理

## 执行指令

请执行者修正Dong第12行残留问题后回复。

根据 PRINCIPLE.md：只要审查者还提出了任何修改意见，规划者都不得关闭 mdissue。

### r005 (2026-03-31T22:00:48)

## 执行进度报告 - Issue 080 Dong第12行修复

### 修复内容

**Dong_2024_KAN_Time_Series_analyze.md 第12行 - 已修复**

**修复前**：
> (3) KAN由于较低的李普希茨常数(Lipschitz constant)表现出更优的对抗鲁棒性

**修复后**：
> (3) KAN和MLP_KAN在对抗攻击中表现出显著鲁棒性优势，其利普希茨常数较小（第301-303行），低网格尺寸的KAN因平滑平坦特性使输入微小变化难以导致输出显著变化

**关键改进**：
1. 将无来源的Lipschitz声称改为精确引用原文第301-303行
2. 添加了第311-313行的引用，说明较大网格KAN也有更强的鲁棒性
3. 保持了原文两个发现的完整性

**修复依据**：
- 第301-303行原文说明低网格KAN因"lower Lipschitz constants"和"平滑平坦特性"而鲁棒
- 第311-313行原文说明大网格KAN因"B-spline梯度主要由B样条部分提供"而有更强的鲁棒性
- 现在两处引用准确反映了原文的完整论述

请审查者 r018 复查验证。

### r006 (2026-03-31T22:03:31)

# 审查者 STEP3 r019 - Issue 080 修复核实

## 审查时间
2026-03-31 22:02

## Issue 080 修复核实

### Dong_2024_KAN_Time_Series_analyze.md 第12行修复验证

**修复后第12行第(3)点**：
> (3) KAN和MLP_KAN在对抗攻击中表现出显著鲁棒性优势，其利普希茨常数较小（第301-303行），低网格尺寸的KAN因平滑平坦特性使输入微小变化难以导致输出显著变化

**原文第301-303行核实**：
> "KAN with a low grid size tends to be smooth and flat, making it difficult for small changes in input to cause significant changes in the output"
> "KAN layer generally results in a **decrease** in the Lipschitz constants"

**核实结果**：
- "其利普希茨常数较小" ✅ 准确（原文Lipschitz常数decrease）
- "（第301-303行）" ✅ 引用准确
- "低网格尺寸的KAN因平滑平坦特性..." ✅ 与原文一致

**修复后第12行第(4)点**：
> (4) 较大网格尺寸的KAN虽然有更大的利普希茨常数，但也表现出更强的鲁棒性（第311-313行）

**原文第311-313行核实**：
> "larger Lipschitz constant leads to greater robustness"

**核实结果**：
- "更大的利普希茨常数" ✅ 准确
- "更强的鲁棒性" ✅ 准确
- "（第311-313行）" ✅ 引用准确

### Issue 080 修复确认

| 问题 | 修复状态 | 核实结果 |
|------|---------|---------|
| Dong第12行第(3)点Lipschitz声称 | ✅ 已修复 | 引用第301-303行准确 |
| Dong第12行第(4)点大网格鲁棒性 | ✅ 已修复 | 引用第311-313行准确 |

**结论**：Issue 080 中 Dong_2024_KAN_Time_Series_analyze.md 第12行的Lipschitz声称问题已正确修复。

本审查不给出是否合格的结论，是否关闭由规划者判断。

---
*审查者 STEP3 r019 - 2026-03-31 22:02*

