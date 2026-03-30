# 调研报告：STEP1 Round130 文献调研

## 基本信息
- 日期：2026-03-30
- 阶段：STEP1 调研
- 覆盖范围：KAN时序应用最新进展、传感器漂移补偿、Wiener模型最新应用
- 是否使用子代理：是（3个并行搜索任务）

## 检索路径

### 子代理1：KAN时序应用最新进展搜索
- 关键词：KAN + time series, KAN + sensor, KAN + frequency response, KAN + nonlinear system identification
- 主要数据库：arXiv, IEEE Xplore, Google Scholar
- 检索式：2025-2026年最新KAN论文

### 子代理2：传感器漂移补偿最新论文搜索
- 关键词：deep learning + sensor drift compensation, neural network + electrochemical sensor
- 主要数据库：IEEE Sensors, Measurement, Sensors B, arXiv
- 检索式：2024-2026年传感器漂移补偿论文

### 子代理3：Wiener模型最新应用搜索
- 关键词：Wiener-Hammerstein + deep learning, block-structured nonlinear identification
- 主要数据库：arXiv, IEEE TIM, Automatica, MSSP
- 检索式：2024-2026年Wiener模型论文

## 发现结果

### 新增文献线索

| 文献 | 类型 | 相关性 | 入口/链接 |
|-----|------|-------|----------|
| Enzner et al. 2025 - Cross-Comparison of Neural Architectures for Digital Self-Interference | P0 | 高 | https://arxiv.org/abs/2507.03109 |
| Rodriguez Linares & Johansson 2025 - Low-Complexity Frequency-Dependent Linearizers | P0 | 高 | https://doi.org/10.1109/ACCESS.2025.3642613 |
| Willemstein et al. 2024 - Wiener-Hammerstein for 3D GRF | P1 | 高 | DOI: 10.1017/wtc.2024.23 |
| Massai et al. 2025 - L2RU: Structured SSM with L2-bound | P0 | 高 | https://arxiv.org/abs/2503.23818 |
| Degtyarev et al. 2024 - AI-based models for IMD2 cancellation | P1 | 中 | https://arxiv.org/abs/2406.09531 |

### 入口已定位
- Enzner et al. 2025 - Wiener-Hammerstein全双工自干扰消除
- Rodriguez Linares & Johansson 2025 - 低复杂度频域依赖线性化器
- Massai et al. 2025 - L2RU结构化SSM

### 疑似重复
- Bonassi et al. 2023 (SSM=Deep Wiener) - 已在R128中添加
- Willemstein et al. 2024 - 已在R17中添加

### 明确排除
- 无

## 待核实事项
- Rodriguez Linares & Johansson 2025 的具体DOI需要进一步确认
- Massai et al. 2025 的完整标题需要确认

## 对文档的影响
- 更新了哪些文件：
  - raw_literature.md（新增5条文献线索）
  - literature_catalog.md（更新索引）
  - 本调研报告（新建）
- 是否需要更新 SUMMARY：否
- 是否需要后续 STEP2 分析：否（文献已充分）

## 原始链接
- https://arxiv.org/abs/2507.03109
- https://doi.org/10.1109/ACCESS.2025.3642613
- DOI: 10.1017/wtc.2024.23
- https://arxiv.org/abs/2503.23818
- https://arxiv.org/abs/2406.09531

---

## 调研总结

本次调研通过3个并行子代理搜索，确认了以下关键发现：

1. **现有文献库已非常全面**：130+篇论文覆盖KAN、Wiener模型、频域损失、传感器漂移补偿等各个方向

2. **新增文献**：
   - Enzner et al. 2025: Wiener-Hammerstein全双工自干扰消除（强支撑）
   - Rodriguez Linares & Johansson 2025: 低复杂度频域依赖线性化器（支撑前馈vs反馈对比）
   - Massai et al. 2025: L2RU结构化SSM with L2-bound（非线性基准）

3. **文献库状态**：
   - GAP1-11全部已支撑，无高缺口
   - 所有核心论文已验证或待核实
   - 建议聚焦论文写作而非继续扩展文献

4. **GAP文献缺口状态**（基于GAP文献缺口.md）：
   - 无缺口（7个）：GAP1, GAP4, GAP7, GAP8, GAP9, GAP10, GAP11
   - 低缺口（4个）：GAP2, GAP3, GAP5, GAP6
