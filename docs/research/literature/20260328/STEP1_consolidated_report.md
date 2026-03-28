# Literature Search Report - 20260328

**Date**: 2026-03-28
**Stage**: STEP1 调研

**Coverage**: Wiener模型理论、KAN网络、频域损失函数、漂移补偿、架构效率
**Subagents Used**: 是（5个并行方向）

---

## 检索路线汇总

### 1. Wiener模型理论
- **关键词**: Wiener system, nonlinear system identification, Wiener-Hammerstein, Barron-Wiener
- **主要数据库**: IEEE Xplore, arXiv, ScienceDirect


### 2. KAN网络
- **关键词**: Kolmogorov-Arnold Networks, KAN, spline, time series, efficiency
- **主要数据库**: arXiv, Google Scholar
- **新发现**: KANEL_E (2512.12850) - FPGA LUT实现2700x加速

### 3. 频域损失函数
- **关键词**: frequency domain loss, spectral loss, AFMAE, Focal Frequency Loss, SAMFre
- **主要数据库**: arXiv, IEEE Xplore, Google Scholar
- **发现**: AFMAE原始论文未找到，使用Focal Frequency Loss作为理论依据

### 4. 漂移补偿深度学习
- **关键词**: drift compensation, sensor drift, electrochemical, gas sensor, e-nose
- **主要数据库**: IEEE Xplore, ScienceDirect, arXiv

### 5. 架构效率对比
- **关键词**: RNN vs CNN, parameter count, FLOPs, computational efficiency
- **主要数据库**: arXiv, IEEE Xplore

---

## 发现结果汇总

### 新增文献线索

| 分类 | 作者 | 年份 | 标题 | arXiv ID | 状态 |
|------|------|------|------|----------|------|
| KAN | Liu et al. | 2024 | KAN: Kolmogorov-Arnold Networks | 2404.19756 | 已核实 |
| KAN | Cruz et al. | 2025 | State-Space KAN for Wiener-Hammerstein | 2506.16392 | 已核实 - 核心文献 |
| KAN | Manavalan, Tronarp | 2026 | Barron-Wiener-Laguerre | 2602.13098 | 已核实 |
| KAN | Hoang et al. | 2025 | KANEL_E (LUT-based, FPGA 2700x) | 2512.12850 | 已核实 |
| KAN | Qiu et al. | 2024 | PowerMLP (40x faster than KAN) | 2412.13571 | 已核实 |
| Freq Loss | Jiang et al. | 2020 | Focal Frequency Loss (ICCV 2021) | 2012.12821 | 已核实 - AFMAE理论依据 |
| Freq Loss | Wang et al. | 2025 | TimeCF with SAMFre | 2505.17532 | 已核实 |
| Drift | Zhang et al. | 2022 | TDACNN for Gas Sensor Drift | 2110.07509 | 已核实 |
| Drift | Lin, Zhan | 2025 | Knowledge Distillation E-nose | 2507.17071 | 已核实 |
| Efficiency | Yin et al. | 2017 | Comparative Study CNN vs RNN | 1702.01923 | 已核实 |
| Efficiency | Xie, Zhang | 2021 | Deep Filtering | 2112.12616 | 已核实 |
| Efficiency | Miller, Hardt | 2018 | Stable Recurrent Models | 1805.10369 | 已核实 |


### 入口已定位
- State-Space KAN (2506.16392): 直接连接Wiener-Hammerstein
- Barron-Wiener-Laguerre (2602.13098): 理论框架
- KANEL_E (2512.12850): LUT硬件加速参考

### 明确排除
- AFMAE原始论文未找到（使用Focal Frequency Loss替代）
- FreDF原始论文未找到

---

## 待核实事项

| 项目 | 优先级 | 状态 |
|------|--------|------|
| AFMAE原始论文 | P0 | 未找到 - 使用FFL作为理论依据 |
| FreDF原始论文 | P1 | 未找到 |
| Transformer时间序列文献 | P1 | 已在列表中（待获取） |

---

## 核心文献清单

### P0核心理论（已验证）
1. **State-Space KAN for Wiener-Hammerstein** (Cruz et al., 2025)
   - arXiv: 2506.16392 / DOI: 10.1109/LCSYS.2025.3578019
   - **关键连接**: 直接验证Wiener-KAN架构

2. **Barron-Wiener-Laguerre** (Manavalan, Tronarp, 2026)
   - arXiv: 2602.13098
   - **理论框架**: Wiener类模型的完整理论

3. **KAN: Kolmogorov-Arnold Networks** (Liu et al., 2024)
   - arXiv: 2404.19756
   - **基础**: KAN理论基础

4. **Focal Frequency Loss** (Jiang et al., 2020)
   - arXiv: 2012.12821 / ICCV 2021
   - **AFMAE理论基础**

### P1应用技术（已验证）
1. **TDACNN** (Zhang et al., 2022) - arXiv:2110.07509
2. **Knowledge Distillation E-nose** (Lin, Zhan, 2025) - arXiv:2507.17071
3. **Comparative Study CNN vs RNN** (Yin et al., 2017) - arXiv:1702.01923
4. **Deep Filtering** (Xie, Zhang, 2021) - arXiv:2112.12616


---

## 对文档的影响

- **更新了 raw_literature.md**: 更新待核实状态为"已核实"，补充新发现文献
- **更新了 literature_catalog.md**: 添加新文献条目
- **创建了分方向调研报告**:
  - docs/research/literature/20260328/wiener_model_search.md
  - docs/research/literature/20260328/kan_network_search.md
  - docs/research/literature/20260328/frequency_loss_search.md
  - docs/research/literature/20260328/drift_compensation_search.md
  - docs/research/literature/20260328/architecture_efficiency_search.md

---

## 原始链接

- https://arxiv.org/abs/2506.16392 (State-Space KAN)
- https://arxiv.org/abs/2602.13098 (Barron-Wiener-Laguerre)
- https://arxiv.org/abs/2404.19756 (KAN Original)
- https://arxiv.org/abs/2012.12821 (Focal Frequency Loss)
- https://arxiv.org/abs/2512.12850 (KANEL_E)
- https://arxiv.org/abs/2412.13571 (PowerMLP)
- https://arxiv.org/abs/1702.01923 (CNN vs RNN)
- https://arxiv.org/abs/2112.12616 (Deep Filtering)
- https://arxiv.org/abs/2110.07509 (TDACNN)
- https://arxiv.org/abs/2507.17071 (KD E-nose)
