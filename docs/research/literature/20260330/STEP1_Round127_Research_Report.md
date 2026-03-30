# 调研报告：STEP1 Round 127 - 并行文献补充调研

## 基本信息
- 日期：2026-03-30
- 阶段：STEP1 调研
- 覆盖范围：Wiener-KAN混合架构、Measurement期刊论文、频域损失函数
- 是否使用子代理：是（3个并行子代理）

---

## 检索路径

### 子代理1：Wiener-KAN混合架构及时序应用
- 关键词：Wiener-KAN, KAN sensor, feedforward compensation, frequency response
- 数据库：arXiv, IEEE Xplore, Google Scholar
- 新发现：DeepOKAN、WaveNet-Volterra、KANLoc等

### 子代理2：Measurement期刊传感器论文
- 关键词：sensor nonlinearity, drift compensation, temperature compensation
- 数据库：ScienceDirect Measurement journal
- 新发现：补充了多篇2024-2026年Measurement期刊论文

### 子代理3：频域损失函数
- 关键词：frequency domain loss, AFMAE, spectral loss, FFT loss
- 数据库：arXiv, IEEE Xplore
- 新发现：确认FreDF为AFMAE来源

---

## 新增文献线索

### Wiener-KAN混合架构（新增）

| 文献 | 年份 | 标题 | DOI/链接 | 类别 | 相关度 | 状态 |
|------|------|-------|----------|------|--------|------|
| Zhang et al. | 2025 | DeepOKAN: BubbleOKAN for High-Frequency Bubble Dynamics | https://arxiv.org/abs/2508.03965 | P1 | 高 | 新增 (R127) |
| Luo et al. | 2026 | KANLoc: KAN-Based Pose Regression for Planetary Landing | https://arxiv.org/abs/2602.06968 | P1 | 高 | 新增 (R127) |
| Bai et al. | 2025 | WaveNet-Volterra Neural Networks for Active Noise Control | https://arxiv.org/abs/2504.04450 | P1 | 高 | 新增 (R127) |
| Enzner et al. | 2025 | Neural Architectures for Digital Self-Interference Modeling | https://arxiv.org/abs/2507.03109 | P1 | 高 | 新增 (R127) |

### 频域损失函数（确认）

| 文献 | 年份 | 标题 | DOI/链接 | 类别 | 相关度 | 状态 |
|------|------|-------|----------|------|--------|------|
| Wang et al. | 2025 | FreDF (ICLR 2025) - AFMAE公式来源 | https://arxiv.org/abs/2402.02399 | P0 | 最高 | 已确认 |
| Shi et al. | 2025 | OLMA - 熵减定理 | https://arxiv.org/abs/2505.11567 | P0 | 高 | 已确认 |
| Chakraborty et al. | 2025 | BSP Loss | https://arxiv.org/abs/2502.00472 | P0 | 高 | 已确认 |
| Wu et al. | 2025 | KFS - Parseval定理验证 | https://arxiv.org/abs/2508.00635 | P0 | 高 | 已确认 |
| He et al. | 2025 | FIRE - 统一频域框架 | https://arxiv.org/abs/2510.10145 | P0 | 高 | 已确认 |
| Sun et al. | 2025 | FreLE - 低频谱偏置校正 | https://arxiv.org/abs/2510.25800 | P0 | 高 | 已确认 |

---

## 待核实事项

### 优先级P0（高优先级）
- DeepOKAN/BubbleOKAN (Zhang 2025) - 新发现，需验证与Wiener-KAN的关联
- KANLoc (Luo 2026) - KAN用于传感器融合

### 优先级P1（中优先级）
- WaveNet-Volterra (Bai 2025) - 主动噪声控制中的非线性补偿
- Enzner et al. 2025 - 自干扰建模中的神经网络架构

### 优先级P2（低优先级）
- 已确认FreDF为AFMAE公式来源，无需进一步核实

---

## 入口已定位

- DeepOKAN: https://arxiv.org/abs/2508.03965
- KANLoc: https://arxiv.org/abs/2602.06968
- WaveNet-Volterra: https://arxiv.org/abs/2504.04450
- Enzner: https://arxiv.org/abs/2507.03109
- FreDF: https://arxiv.org/abs/2402.02399
- OLMA: https://arxiv.org/abs/2505.11567

---

## 对文档的影响

### 更新的文件
- docs/research/literature/20260330/STEP1_Round127_Research_Report.md（本文档）
- docs/research/literature/raw_literature.md（新增4篇论文）
- docs/research/literature/literature_catalog.md（调研报告索引更新）

### 是否需要后续STEP2分析
- 否 - 本轮为补充性调研

---

## 原始链接

- DeepOKAN: https://arxiv.org/abs/2508.03965
- KANLoc: https://arxiv.org/abs/2602.06968
- WaveNet-Volterra: https://arxiv.org/abs/2504.04450
- Enzner: https://arxiv.org/abs/2507.03109
- FreDF: https://arxiv.org/abs/2402.02399
- OLMA: https://arxiv.org/abs/2505.11567

---

**报告生成时间**：2026-03-30
**调研轮次**：Round 127
