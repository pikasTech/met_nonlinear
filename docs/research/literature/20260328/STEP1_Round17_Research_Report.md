# 调研报告：STEP1 Round 17 - 新方向拓展

## 基本信息
- 日期：2026-03-28
- 阶段：STEP1 调研
- 覆盖范围：Wiener模型传感器应用、KAN最新进展、传感器非线性补偿、频域损失函数
- 是否使用子代理：是；并行维度：4个子代理分别搜索Wiener传感器应用、KAN最新理论、传感器非线性补偿、频域损失函数

## 检索路径

### 子代理1：Wiener模型传感器应用
- 关键词：Wiener model sensor, Wiener-Hammerstein electrochemical, block-structured nonlinear sensor identification
- 主要数据库：arXiv, IEEE Xplore, Google Scholar
- 新发现：Wiener-Hammerstein用于软体传感器力估计

### 子代理2：KAN最新理论进展（2025-2026）
- 关键词：KAN, Kolmogorov-Arnold Networks, TaylorKAN, WaveletKAN, KAN time series
- 主要数据库：arXiv, Google Scholar
- 新发现：Symbolic-KAN, Multilevel Training KAN, KANDy, SINDy-KANs

### 子代理3：传感器非线性补偿深度学习
- 关键词：sensor nonlinearity compensation neural network, electrochemical sensor ML, MEMS calibration deep learning
- 主要数据库：arXiv, IEEE Xplore, ScienceDirect
- 新发现：Physics-Informed GRU, WING惯性里程计, 葡萄糖传感器ML

### 子代理4：频域损失函数
- 关键词：frequency domain loss time series, spectral loss, FFT loss, focal frequency
- 主要数据库：arXiv, IEEE Xplore
- 新发现：FreST Loss, FreDN, BSP Loss新进展

## 发现结果

### 新增文献线索

#### Wiener模型传感器应用（新增）
| 作者 | 年份 | 标题 | DOI/链接 | 相关性 | 状态 |
|------|------|------|----------|--------|------|
| Willemstein et al. | 2024 | Soft insoles for 3D ground reaction forces using Wiener-Hammerstein | 10.1017/wtc.2024.23 | High | New |
| Yesil, Yilmaz | 2024 | Wiener Hammerstein RF Power Amplifier identification using DFT | 10.13164/re.2024.0265 | Medium | New |
| Li et al. | 2024 | Neural fuzzy Wiener-Hammerstein system identification | 10.1631/fitee.2300058 | Medium | New |
| Kruger et al. | 2026 | Optical Linear Systems Framework for Event Sensing | arXiv:2601.13498 | Medium | New |

#### KAN最新理论进展（新增）
| 作者 | 年份 | 标题 | DOI/链接 | 相关性 | 状态 |
|------|------|------|----------|--------|------|
| Southworth et al. | 2026 | Multilevel Training for Kolmogorov Arnold Networks | arXiv:2603.04827 | High | New |
| Faroughi et al. | 2026 | Symbolic-KAN: Discrete Symbolic Structure | arXiv:2603.23854 | High | New |
| Khodakarami et al. | 2026 | Spectral bias in physics-informed and operator learning | arXiv:2602.19265 | High | New |
| Gao et al. | 2025 | DecoKAN: Interpretable Decomposition for Crypto Forecasting | arXiv:2512.20028 | High | New |
| Mohammed et al. | 2026 | Physics-Informed KAN for Vessel Power Prediction | arXiv:2602.22055 | High | New |
| Slote et al. | 2026 | KANDy: KAN for Dynamical Systems | arXiv:2602.20413 | High | New |
| Howard et al. | 2026 | SINDy-KANs: Sparse Nonlinear Dynamics | arXiv:2603.18548 | High | New |
| Liu et al. | 2026 | BiKA: Binary KAN Accelerator | arXiv:2602.23455 | High | New |
| Zhang et al. | 2026 | KMLP: Hybrid KAN-MLP | arXiv:2602.22777 | Medium | New |

#### 传感器非线性补偿（新增）
| 作者 | 年份 | 标题 | DOI/链接 | 相关性 | 状态 |
|------|------|------|----------|--------|------|
| Shi et al. | 2025 | Physics-Informed NN for Laser Thermal Stabilization | arXiv:2505.20769 | High | New |
| Jiang et al. | 2024 | WING: Wheel-Inertial Neural Odometry | arXiv:2407.10101 | High | New |
| Goncharov et al. | 2024 | Insertable Glucose Sensor with ML | 10.1021/acsnano.4c06527 | Medium | New |
| Chen, Pan | 2023 | Deep Learning for Inertial Positioning: A Survey | arXiv:2303.03757 | High | New |
| France | 2025 | Chronoamperometry with Room-Temperature Ionic Liquids | arXiv:2506.04540 | Medium | New |

#### 频域损失函数（新增）
| 作者 | 年份 | 标题 | DOI/链接 | 相关性 | 状态 |
|------|------|------|----------|--------|------|
| Wang et al. | 2026 | FreST Loss: Joint Frequency Domain Learning | arXiv:2603.04418 | High | New |
| Subich et al. | 2025 | Fixing Double Penalty in Weather Forecasting | arXiv:2501.19374 | High | New |
| An et al. | 2025 | FreDN: Spectral Disentanglement for TS | arXiv:2511.11817 | High | New |
| Zhang et al. | 2026 | Log Focal Frequency Loss | arXiv:2601.20878 | Medium | New |
| Wang et al. | 2025 | Partitioned Focal Frequency Loss | arXiv:2501.01773 | Medium | New |

### 入口已定位
- arXiv:2603.23854 - Symbolic-KAN（符号可解释KAN）
- arXiv:2603.04827 - Multilevel KAN训练
- arXiv:2603.04418 - FreST联合频域损失
- arXiv:2511.11817 - FreDN频域解缠

### 疑似重复
- 无

### 明确排除
- 无

## 待核实事项
1. Willemstein 2024的Wiener-Hammerstein软体传感器应用是否可作为MET传感器参考
2. Symbolic-KAN的可解释性是否对论文有益
3. WING惯性里程计的漂移补偿方法是否可借鉴

## 对文档的影响
- 更新了 `literature_catalog.md`：新增KAN理论、传感器补偿、频域损失条目
- 更新了 `raw_literature.md`：新增原始文献表格条目
- 是否需要更新 SUMMARY：否
- 是否需要后续 STEP2 分析：是（建议分析Symbolic-KAN和FreST Loss）

## 原始链接
- https://arxiv.org/abs/2603.23854 (Symbolic-KAN)
- https://arxiv.org/abs/2603.04827 (Multilevel KAN)
- https://arxiv.org/abs/2603.04418 (FreST Loss)
- https://arxiv.org/abs/2511.11817 (FreDN)
- https://arxiv.org/abs/2407.10101 (WING)
- https://arxiv.org/abs/2303.03757 (Inertial Positioning Survey)
- 10.1017/wtc.2024.23 (Wiener-Hammerstein soft sensors)
