# 频域损失函数文献检索报告

**日期**：2026-03-28
**检索范围**：用于时间序列处理的频域损失函数

---

## 1. 检索数据库和关键词

### 1.1 检索的数据库
- arXiv (https://arxiv.org) - 近期论文的主要来源
- Google Scholar - 学术综合搜索
- IEEE Xplore - 工程文献

### 1.2 使用的关键词

| 类别 | 关键词 |
|------|--------|
| 通用 | frequency domain loss, spectral loss, frequency loss |
| 特定 | AFMAE, Focal Frequency Loss, focal frequency, SAMFre |
| 应用 | time series prediction loss, FFT loss, frequency-aware loss |
| 变体 | Fre-CW, FreDF, spectral angle loss |

---

## 2. 发现/验证的关键论文

### 2.1 聚焦频率损失（FFL）- 已验证

| 字段 | 值 |
|------|-----|
| 引用 | Jiang等，图像重建与合成的聚焦频率损失 |
| 年份 | 2020（arXiv），ICCV 2021 |
| arXiv ID | 2012.12821 |
| URL | https://arxiv.org/abs/2012.12821 |
| 会议 | ICCV 2021 |
| 关键贡献 | 首个自适应频率聚焦损失函数 |
| 相关性 | AFMAE设计的理论基础 |
| 状态 | 已验证 |

### 2.2 带SAMFre的TimeCF - 已验证

| 字段 | 值 |
|------|-----|
| 引用 | Wang等，TimeCF：带反事实解释的时间序列预测 |
| 年份 | 2025 |
| arXiv ID | 2505.17532 |
| URL | https://arxiv.org/abs/2505.17532 |
| 关键贡献 | FFT + 锐度感知最小化用于频域损失 |
| 相关性 | AFMAE实现的直接参考 |
| 状态 | 已验证 |

### 2.3 Fre-CW - 已验证

| 字段 | 值 |
|------|-----|
| 引用 | Feng等 |
| 年份 | 2025 |
| arXiv ID | 2508.08955 |
| URL | https://arxiv.org/abs/2508.08955 |
| 状态 | 已验证 |

---

## 3. 需要进一步验证的缺失论文

### 3.1 AFMAE - 未找到

- 论文名称：AFMAE（自适应频率平均绝对误差）
- 原始论文未找到
- 使用聚焦频率损失（Jiang等，2020）作为理论基础

### 3.2 FreDF - 未找到

- 论文名称：FreDF（基于频率的距离函数）
- SAMFre引用为Wang等，2024
- 原始论文未找到

---

## 4. 引用摘要

### 4.1 已验证引用（可使用）

**AFMAE/频域损失理论：**
Jiang等，图像重建与合成的聚焦频率损失
arXiv:2012.12821 (2020)，ICCV 2021

**频域损失实现：**
Wang等，TimeCF：带反事实解释的时间序列预测
arXiv:2505.17532 (2025)

### 4.2 缺失引用（不可使用）

| 论文 | 问题 |
|------|------|
| AFMAE | 原始来源未找到 |
| FreDF | 原始论文未找到 |
---

## 5. 行动项目

| 项目 | 优先级 | 状态 |
|------|--------|------|
| 在IEEE Xplore中搜索AFMAE | 高 | 待处理 |
| 搜索FreDF引用链 | 高 | 待处理 |
| 验证Fre-CW范围相关性 | 中 | 已完成 |
| 通过FFL记录AFMAE理论基础 | 高 | 已完成 |

---

## 6. 参考文献

1. Jiang等，图像重建与合成的聚焦频率损失，arXiv:2012.12821 (2020)
2. Wang等，TimeCF：带反事实解释的时间序列预测，arXiv:2505.17532 (2025)
3. Feng等，Fre-CW，arXiv:2508.08955 (2025)
4. 现有文献文件：key_references.md, verified_literature.md, raw_literature.md

---

**报告状态**：已完成
**最后更新**：2026-03-28
**准备基于**：现有项目文献文件和arXiv搜索