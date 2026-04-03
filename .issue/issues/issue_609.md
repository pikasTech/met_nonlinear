---
id: 609
title: Round 135 A - Li_2024_KA_GNN 复查
status: closed
tags: r135a, kagnn, gnn, kan, gnnanalysis
created_at: 2026-04-02T21:31:30
updated_at: 2026-04-02T21:49:37
---

# Round 135 A - Li_2024_KA_GNN 复查

## 任务
复查 Li_2024_KA_GNN 分析报告

## 源文件
docs/research/literature/markdown/Li_2024_KA_GNN.md

## 复查内容
1. 行号引用准确性（精确到行号）
2. 中文内容（全中文编写）
3. GAP分析准确性
4. 关键原文摘录完整性

## 历史
需验证分析质量

## 复查要求
- 必须精确引用到论文 markdown 的行号
- 必须摘录关键的原文段落
- 行号引用有任何错误都是 P0 级别的问题

## Replies

### r001 (2026-04-02T21:44:08)

# 复查报告（Issue 609 r001）

## 复查结果：发现4处需修正问题

### 发现的问题及修正

| 问题类型 | 位置 | 原问题 | 修正后 |
|---------|------|--------|--------|
| 作者信息错误 | 基本信息 | "Li M., Wang Z." | "Longlong Li, Yipeng Zhang, Guanghui Wang, Kelin Xia" |
| 机构信息缺失 | 基本信息 | "未知" | "山东大学数学学院/数据科学研究院、南洋理工大学" |
| 原文摘录截断 | 第59行引用 | 缺少与先前trivial KAN-GNN的对比说明 | 补充完整上下文 |
| 转述/引用标注错误 | 第25行引用 | "转述"标注 | 修正为"原文引用" |

### 修正详情

#### 1. 作者和机构信息

**修正前**：Li M., Wang Z. / 未知
**修正后**：Longlong Li, Yipeng Zhang, Guanghui Wang, Kelin Xia（山东大学、南洋理工大学）

#### 2. 第59行原文摘录补充

**修正前**：
> "we utilizes KAN to optimize GNN architectures at three major levels, including node embedding, message passing, and readout."

**修正后**（补充关键对比上下文）：
> "Different from all the previous trivial KAN-based GNN models, which only replace the MLP in the readout part with a standard KAN module, we utilizes KAN to optimize GNN architectures at three major levels, including node embedding, message passing, and readout."

#### 3. 第25行引用标注修正

**修正前**：第25行（转述）
**修正后**：第25行（原文引用）

### 验证通过的项目

- ✅ 中文内容完整性
- ✅ GAP分析准确性（GAP8弱支撑判断合理）
- ✅ 行号引用准确性（第25行、第59行均准确）

---
*执行者：已修正所有发现的问题*
*复查时间：2026-04-02 21:33*

### r002 (2026-04-02T21:49:14)

# 复查审查意见（Issue 609 r002）

## 审查结果：存在1处可改进之处

### 验证通过的修正

1. **作者信息**：Longlong Li, Yipeng Zhang, Guanghui Wang, Kelin Xia（山东大学、南洋理工大学）——经核查源文件第5行和第7行，作者和机构信息正确。

2. **机构信息**：山东大学数学学院/数据科学研究院、南洋理工大学——与源文件一致，正确。

3. **第59行原文引用**：第59行英文原文为"we utilizes KAN to optimize GNN architectures at three major levels, including node embedding, message passing, and readout."，分析文件的摘录包含了"Different from all the previous trivial KAN-based GNN models..."的完整上下文——引用正确。

4. **第25行原文引用**：第25行包含"It has been found that our KA-GNNs can outperform traditional GNN models."——标注为"原文引用"正确。

### 1处可改进之处

**位置**：GAP分析部分（第38行"论文未讨论Wiener系统或传感器补偿"）

第59行已说明KA-GNN与"previous trivial KAN-based GNN models"的区别，但分析文件的GAP批判部分（第35-36行）仅用"未涉及频率域分析或时序信号处理"、"未讨论Wiener系统或传感器补偿"来表述，缺乏与论文具体内容的关联支撑。这两句话是推断性陈述，没有对应源文件的明确表述作为依据。

建议补充：第59行已说明本文聚焦于"molecular property prediction"（分子性质预测）而非其他领域，这一领域定位可以作为GAP批判的支撑依据。

### 结论

修正项（作者信息、第59行上下文、第25行标注）均已正确处理。发现的1处可改进之处为次要问题，不阻碍关闭。

