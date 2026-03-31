# 调研报告：STEP1 Round 194 - 并行子代理文献检索综合

## 基本信息
- 日期：2026-03-31
- 阶段：STEP1 调研
- 覆盖范围：KAN效率冲突、Wiener模型传感器应用、前馈补偿、频域损失函数
- 是否使用子代理：是（4个并行子代理）

## 检索路径

### 子代理1：KAN vs LSTM/GRU效率冲突分析
- 关键词：KAN vs LSTM efficiency, Kolmogorov Arnold Networks computational efficiency
- 主要数据库：arXiv, IEEE Xplore, Google Scholar
- 发现：Ali 2025 vs Rather 2025 冲突可通过混合架构解决

### 子代理2：Wiener模型传感器应用
- 关键词：Wiener model sensor compensation, Wiener Hammerstein electrochemical seismic
- 主要数据库：arXiv, IEEE TIM, Measurement
- 发现：van Meer 2025, FRIKAN 2025, Lin 2020

### 子代理3：前馈补偿研究
- 关键词：feedforward compensation sensor, feedforward vs feedback range limitation
- 主要数据库：arXiv, IEEE, Measurement
- 发现：Fang 2024, Umeda 2025, Elliott 1996

### 子代理4：频域损失函数
- 关键词：AFMAE, frequency domain loss time series, FreDF, FIRE, OLMA
- 主要数据库：arXiv, ICLR, ICML
- 发现：OLMA最强理论支撑，FreDF直接公式匹配

---

## 发现结果

### 新增文献线索

#### KAN vs LSTM效率冲突解决

| 文献 | 类型 | 相关性 | 入口/链接 |
|-----|------|-------|----------|
| Ali et al. 2025 | DOI | P0 | 10.48550/arXiv.2511.18613 |
| Rather et al. 2025 | DOI | P0 | 10.48550/arXiv.2507.13685 |
| Barasin et al. 2025 | arXiv | P1 | arXiv.2411.14904 |

**冲突解决结论**：
- Ali 2025测试**纯KAN vs 纯LSTM**：LSTM准确率优4倍
- Rather 2025测试**KAN-GRU混合 vs 纯LSTM**：混合架构胜出
- **正确表述**：KAN+RNN混合架构 > 纯RNN，而非"KAN比LSTM更高效"

#### Wiener模型传感器应用 (GAP4/GAP5支撑)

| 文献 | 类型 | 相关性 | 入口/链接 |
|-----|------|-------|----------|
| van Meer et al. 2025 | arXiv | P0 | arXiv:2505.04245 |
| Wahlberg 2015 | arXiv | P0 | arXiv:1507.05535 |
| Lin et al. 2020 | DOI | P0 | 10.1016/j.measurement.2020.107887 |
| FRIKAN (Li 2025) | DOI | P0 | TIM-25-06440 |
| Manavalan 2026 | arXiv | P0 | arXiv:2602.13098 |

#### 前馈补偿新论文 (GAP6/GAP7支撑)

| 文献 | 类型 | 相关性 | 入口/链接 |
|-----|------|-------|----------|
| Fang et al. 2024 | DOI | P0 | 10.1016/j.measurement.2024.116559 |
| Umeda & Kodera 2025 | arXiv | P0 | arXiv:2512.18252 |
| Elliott & Sutton 1996 | DOI | P0 | 10.1109/89.496217 |
| KAN-FIF (Shen 2026) | arXiv | P0 | arXiv:2602.12117 |

#### 频域损失函数 (GAP10/GAP11支撑)

| 文献 | 类型 | 相关性 | 入口/链接 |
|-----|------|-------|----------|
| FreDF (Wang 2025) | DOI | P0 | 10.48550/arXiv.2402.02399 |
| OLMA (Shi 2025) | arXiv | P0 | arXiv:2505.11567 |
| FIRE (He 2025) | arXiv | P0 | arXiv:2510.10145 |
| Subich 2025 | arXiv | P0 | arXiv:2501.19374 |

---

## 冲突与争议

### KAN vs LSTM效率冲突

| 论文 | 对比 | 胜者 | 原因 |
|-----|------|------|------|
| Ali 2025 | 纯KAN vs 纯LSTM | LSTM | LSTM准确率4x优 |
| Rather 2025 | KAN-GRU混合 vs 纯LSTM | KAN-GRU混合 | 混合架构胜出 |

**结论**：KAN的优势在于**混合架构**（替换RNN中的非线性层），而非纯KAN vs 纯LSTM的直接比较

---

## 对文档的影响

- 更新了哪些文件：
  - docs/research/literature/20260331/STEP1_Round194_Survey_Report.md（本文）
  - docs/research/literature/raw_literature.md（新增R194节）
  - docs/research/literature/GAP文献缺口.md（确认无新增缺口）
- 是否需要更新 SUMMARY：否
- 是否需要后续 STEP2 分析：否（本轮为调研发现）

---

## 原始链接

### KAN vs LSTM效率
- Ali 2025: https://doi.org/10.48550/arXiv.2511.18613
- Rather 2025: https://doi.org/10.48550/arXiv.2507.13685
- Barasin 2025: https://arxiv.org/abs/2411.14904

### Wiener模型传感器
- van Meer 2025: https://arxiv.org/abs/2505.04245
- Wahlberg 2015: https://arxiv.org/abs/1507.05535
- Lin 2020: https://doi.org/10.1016/j.measurement.2020.107887
- FRIKAN: TIM-25-06440
- Manavalan 2026: https://arxiv.org/abs/2602.13098

### 前馈补偿
- Fang 2024: https://doi.org/10.1016/j.measurement.2024.116559
- Umeda 2025: https://arxiv.org/abs/2512.18252
- Elliott 1996: https://doi.org/10.1109/89.496217
- KAN-FIF: https://arxiv.org/abs/2602.12117

### 频域损失
- FreDF: https://doi.org/10.48550/arXiv.2402.02399
- OLMA: https://arxiv.org/abs/2505.11567
- FIRE: https://arxiv.org/abs/2510.10145
- Subich: https://arxiv.org/abs/2501.19374

---

## 报告生成时间：2026-03-31 08:03
## 调研轮次：Round 194
## 完成状态：已完成