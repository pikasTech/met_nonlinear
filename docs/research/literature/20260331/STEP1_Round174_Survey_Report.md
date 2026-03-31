# 调研报告：KAN 2026最新进展与Wiener模型传感器应用

## 基本信息
- 日期：2026-03-31
- 阶段：STEP1 调研
- 覆盖范围：KAN 2026最新论文、Wiener模型传感器应用、MEASUREMENT期刊传感器非线性补偿
- 是否使用子代理：是（4个子代理并行搜索）

## 检索路径
- 关键词：KAN 2026, Wiener sensor, electrochemical seismic, frequency response drift, feedforward compensation
- 主要数据库：arXiv, IEEE Xplore, Google Scholar
- 新发现数据库：MEASUREMENT期刊
- 检索式：KAN 2026, Wiener-Hammerstein sensor, frequency domain loss, electrochemical sensor compensation

## 发现结果

### 新增文献线索

| 文献 | 类型 | 相关性 | 入口/链接 |
|-----|------|-------|----------|
| FEKAN: Feature-Enriched KAN (Menon, Jagtap 2026) | P0 | 高 | arXiv:2602.16530 |
| DualFlexKAN: Dual-stage KAN (Ortiz et al. 2026) | P0 | 高 | arXiv:2603.08583 |
| KAN-AE with Non-Linearity Score (Perre et al. 2026) | P0 | 高 | arXiv:2601.01598 |
| Physics-informed KAN under Ehrenfest constraints (Sen et al. 2025) | P1 | 高 | arXiv:2509.18483 |
| Symbolic-KAN (Faroughi et al. 2026) | P1 | 高 | arXiv:2603.23854 |
| KAN-Koopman for Battery Thermal Anomalies (Ghosh, Roy 2026) | P1 | 高 | arXiv:2602.21155 |
| Resolvent-based estimation (Jung, Towne 2025) | P1 | 高 | arXiv:2507.18837 |
| Data-Driven Probabilistic FDI (Ibrahim et al. 2026) | P1 | 高 | arXiv:2603.25982 |
| DA-SHRED (Bao, Kutz 2025) | P1 | 高 | arXiv:2512.01170 |
| Barbieri 2025: Volterra voltage transformer harmonic | P1 | 高 | 10.1016/j.measurement.2025.118373 |
| Lin 2020: Electrochemical seismic sensor amplitude-frequency | P0 | 高 | 10.1016/j.measurement.2020.107518 |
| Chen, Wang 2026: DE-LOESS LSTM-Transformer MEMS | P1 | 高 | 10.1016/j.measurement.2026.120823 |

### 关键发现

1. **FEKAN (Feature-Enriched KAN)**: 在PDE和函数逼近任务上优于FastKAN、WavKAN、ReLUKAN、HRKAN、ChebyshevKAN、RBFKAN
2. **DualFlexKAN**: 双阶段KAN，支持多种基函数（正交多项式、B样条、RBF），参数量比标准KAN少1-2个数量级
3. **KAN-Koopman**: KAN用于Koopman算子学习，实现电池热异常快速检测
4. **Barbieri 2025**: Volterra电压互感器谐波补偿，直接关联Wiener/Volterra块模型理论
5. **Lin 2020**: 电化学地震传感器温度和幅度频率特性，是MET传感器的直接论文

### 入口已定位
- arXiv:2602.16530 (FEKAN)
- arXiv:2603.08583 (DualFlexKAN)
- arXiv:2602.21155 (KAN-Koopman)
- 10.1016/j.measurement.2020.107518 (Lin 2020)

### 疑似重复
- Willemstein 2024: 已在R150收录

### 明确排除
- 无

## 待核实事项
- FEKAN和DualFlexKAN具体性能对比待验证
- Symbolic-KAN符号结构与KAN-FIF物理约束建模的关联待分析

## 对文档的影响
- 更新了 `raw_literature.md` (Round 174新增条目)
- 更新了 `literature_catalog.md` (新增7篇KAN论文、4篇Wiener模型论文、2篇MEASUREMENT论文)
- 是否需要更新 SUMMARY：否
- 是否需要后续 STEP2 分析：否（STEP1仅做文献发现）

## 原始链接
- https://arxiv.org/abs/2602.16530 (FEKAN)
- https://arxiv.org/abs/2603.08583 (DualFlexKAN)
- https://arxiv.org/abs/2602.21155 (KAN-Koopman)
- https://arxiv.org/abs/2601.01598 (KAN-AE)
- https://arxiv.org/abs/2509.18483 (Physics-informed KAN)
- https://arxiv.org/abs/2603.23854 (Symbolic-KAN)
- https://arxiv.org/abs/2507.18837 (Resolvent-based estimation)
- https://arxiv.org/abs/2603.25982 (Probabilistic FDI)
- https://arxiv.org/abs/2512.01170 (DA-SHRED)
- 10.1016/j.measurement.2025.118373 (Barbieri 2025)
- 10.1016/j.measurement.2020.107518 (Lin 2020)
- 10.1016/j.measurement.2026.120823 (Chen 2026)
