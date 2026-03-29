# 调研报告：STEP1 Round 18 综合检索

## 基本信息
- 日期：2026-03-28
- 阶段：STEP1 调研
- 覆盖范围：Wiener模型理论、KAN网络进展、传感器漂移补偿、频域损失函数、数据集构建方法
- 是否使用子代理：是；并行维度：5个方向（Wiener模型、KAN网络、传感器漂移补偿、频域损失、数据集构建）

## 检索路径

### 数据库覆盖
| 数据库 | 访问状态 | 检索结果 |
|--------|----------|----------|
| arXiv | 可用 | 发现多条新文献 |
| IEEE Xplore | 需认证 | 部分受限 |
| ScienceDirect | 需认证 | 部分受限 |
| Google Scholar | 403错误 | 受限 |
| MDPI Sensors | 403错误 | 受限 |

### 关键词覆盖
- Wiener system, Hammerstein-Wiener, nonlinear system identification
- KAN, Kolmogorov-Arnold Networks, spline networks
- sensor drift compensation, deep learning
- frequency domain loss, spectral loss, FFT loss
- sensor dataset construction, benchmark dataset

## 发现结果

### 新增文献线索

#### Wiener模型方向
| 作者 | 年份 | 标题 | DOI/链接 | 状态 |
|------|------|------|----------|------|
| Yin, Müller | 2026 | Data-Driven Prediction and Control of Hammerstein-Wiener Systems with Implicit Gaussian Processes | arXiv:2501.15849 | 待核实 |
| Voit, Enzner | 2024 | Multiplant Nonlinear System Identification by Block-Structured Multikernel Neural Networks | arXiv:2412.07370 | 已存在(Verified R7) |
| Xu et al. | 2025 | Kernel for Volterra Wiener-Hammerstein | arXiv:2505.20747 | 已存在(Verified) |

#### KAN网络方向
| 作者 | 年份 | 标题 | DOI/链接 | 状态 |
|------|------|------|----------|------|
| Vaca-Rubio et al. | 2025 | P-KAN: Probabilistic KAN for Time Series Forecasting | arXiv:2510.16940 | 待核实 |
| Zheng et al. | 2025 | Free-Knots KAN: On the Analysis of Spline Knots and Advancing Stability | arXiv:2501.09283 | 待核实 |
| Shen et al. | 2026 | KAN-FIF: Spline-Parameterized Lightweight Physics-based Tropical Cyclone Estimation | arXiv:2602.12117 | 待核实 |
| Jahin et al. | 2024 | KACQ-DCNN: Uncertainty-Aware Interpretable KAN Classical-Quantum Dual-Channel Neural Network | arXiv:2410.07446 | 待核实 |
| Gaonkar et al. | 2026 | Kolmogorov Arnold Networks and Multi-Layer Perceptrons: A Paradigm Shift | arXiv:2601.10563 | 待核实 |

#### 频域损失函数方向
| 作者 | 年份 | 标题 | DOI/链接 | 状态 |
|------|------|------|----------|------|
| Liu et al. | 2025 | MoFE-Time: Mixture of Frequency Domain Experts | arXiv:2507.06502 | 待核实 |
| Chowdhury et al. | 2025 | T3Time: Tri-Modal Time Series Forecasting | arXiv:2508.04251 | 待核实 |
| Guo, Weng | 2025 | FODEs: Fourier Ordinary Differential Equations | arXiv:2510.04133 | 待核实 |
| Li Qianyang et al. | 2025 | DPWMixer: Dual-Path Wavelet Mixer | arXiv:2512.02070 | 待核实 |
| Ni et al. | 2025 | Ada-MoGE: Adaptive Mixture of Gaussian Expert | arXiv:2512.02061 | 待核实 |
| He et al. | 2025 | FIRE: Unified Frequency Domain Framework | arXiv:2510.10145 | Pending→待核实 |

#### 传感器漂移补偿方向
| 作者 | 年份 | 标题 | DOI/链接 | 状态 |
|------|------|------|----------|------|
| Liang et al. | 2025 | OTTA-DriftNet: Online Test-Time Adaptation | IEEE SMCS | 待核实 |
| Shi et al. | 2022 | EEMD-GRNN for MEMS sensor drift | MDPI Sensors | 待核实 |
| Zhang et al. | 2022 | TDACNN for Gas Sensor Drift | arXiv:2110.07509 | 待核实 |

#### 数据集构建方向
| 作者 | 年份 | 标题 | DOI/链接 | 状态 |
|------|------|------|----------|------|
| Gong et al. | 2026 | SWAN: Seismic Waveforms Dataset for Neural-network Processing | arXiv:2603.13645 | 待核实 |
| Iacob et al. | 2025 | Learning Koopman Models From Data (Schoukens group) | arXiv:2507.09646 | 待核实 |
| Hoekstra et al. | 2026 | Learning-based Augmentation via LFR (Schoukens group) | arXiv:2602.17297 | 待核实 |

### 疑似重复（已存在于literature_catalog.md）
- Voit, Enzner 2024 - Verified (R7)
- Xu et al. 2025 - Verified
- Willemstein et al. 2024 - Verified (R17)
- VIKIN (Ou et al. 2026) - Verified (R11)
- LUT-KAN, IoT KAN (Kuznetsov 2026) - Verified (R4)
- FreDF, SAMFre, BSP Loss - Verified
- Subich ICML 2025 - Verified (R17)
- FreST Loss - Verified (R17)

### 明确排除
- 无新排除文献

## 待核实事项
1. **Yin, Müller 2026 (arXiv:2501.15849)** - 数据驱动Hammerstein-Wiener + Gaussian Processes，高相关性
2. **P-KAN (arXiv:2510.16940)** - 概率KAN时序预测，新型KAN变体
3. **Free-Knots KAN (arXiv:2501.09283)** - B-spline稳定性分析，理论价值高
4. **MoFE-Time (arXiv:2507.06502)** - 频域专家混合，与AFMAE方向相关
5. **OTTA-DriftNet (Liang 2025)** - 在线测试时适应漂移补偿
6. **SWAN (Gong 2026)** - 地震波形数据集

## 对文档的影响
- 更新了 `literature_catalog.md`：新增 "KAN Extended Applications (Round 18)" 分类
- 更新了 `raw_literature.md`：新增本轮检索的待核实文献
- 是否需要更新 SUMMARY：否
- 是否需要后续 STEP2 分析：是（优先核实高相关性文献）

## 原始链接
- https://arxiv.org/abs/2501.15849 (Yin, Müller 2026)
- https://arxiv.org/abs/2510.16940 (P-KAN)
- https://arxiv.org/abs/2501.09283 (Free-Knots KAN)
- https://arxiv.org/abs/2602.12117 (KAN-FIF)
- https://arxiv.org/abs/2410.07446 (KACQ-DCNN)
- https://arxiv.org/abs/2507.06502 (MoFE-Time)
- https://arxiv.org/abs/2508.04251 (T3Time)
- https://arxiv.org/abs/2510.04133 (FODEs)
- https://arxiv.org/abs/2603.13645 (SWAN)
- https://arxiv.org/abs/2507.09646 (Koopman Models)
- https://arxiv.org/abs/2602.17297 (LFR Augmentation)