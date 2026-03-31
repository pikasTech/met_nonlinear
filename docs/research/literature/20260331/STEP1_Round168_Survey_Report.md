# 调研报告：Round 168 - KAN效率/频域损失/Wiener模型文献调研

## 基本信息
- 日期：2026-03-31
- 阶段：STEP1 调研
- 覆盖范围：KAN效率对比、频域损失函数、Wiener模型传感器应用
- 是否使用子代理：是（3个并行搜索维度）

## 检索路径

### 检索1：频域损失/光谱损失
- 关键词：spectral loss, FFT loss, Fourier domain loss, frequency domain loss, neural network
- 主要数据库：arXiv, Google Scholar
- 检索式：spectral loss neural network, FFT loss training, frequency domain loss time series

### 检索2：Wiener模型传感器应用
- 关键词：Wiener model sensor, Wiener-Hammerstein sensor compensation, electrochemical sensor Wiener
- 主要数据库：arXiv, Google Scholar
- 检索式：Wiener model sensor signal processing, Wiener sensor compensation

### 检索3：KAN效率对比
- 关键词：KAN efficiency, KAN vs MLP, KAN parameter efficiency, KAN time series benchmark
- 主要数据库：arXiv, Google Scholar
- 检索式：KAN efficiency comparison, KAN parameter reduction, Kolmogorov Arnold network benchmark

## 发现结果

### 新增文献线索

#### 频域损失文献 (Round 168新增)
| 文献 | 类型 | 相关性 | 入口/链接 |
|-----|------|-------|----------|
| Du et al. 2024, Neural Spectral Methods | P0 | 高 | https://arxiv.org/abs/2312.05225 |
| Takaki et al. 2018, STFT Spectral Loss | P0 | 高 | https://arxiv.org/abs/1810.11945 |
| Han et al. 2023, PNP Loss | P0 | 高 | https://arxiv.org/abs/2301.02886 |
| Défossez et al. 2022, High Fidelity Neural Audio Compression | P0 | 高 | https://arxiv.org/abs/2210.13438 |
| Wang, Li 2025, TF-TransUNet1D | P0 | 高 | https://arxiv.org/abs/2508.20398 |
| Choi et al. 2023, Spectral Operator Learning | P0 | 高 | https://arxiv.org/abs/2310.02013 |
| Choi et al. 2019, S3 Spectral-Spatial Loss | P1 | 中 | https://arxiv.org/abs/1906.05480 |
| Jose 2020, AMRConvNet Time-Frequency Loss | P1 | 中 | https://arxiv.org/abs/2008.10233 |
| Gurung et al. 2026, SPECTRA for HAR | P1 | 中 | https://arxiv.org/abs/2603.26482 |

#### Wiener模型文献 (Round 168新增)
| 文献 | 类型 | 相关性 | 入口/链接 |
|-----|------|-------|----------|
| Willemstein et al. 2023, Soft insoles + Wiener-Hammerstein | P0 | 高 | https://arxiv.org/abs/2303.04719 |
| Willemstein et al. 2023, 3D printed actuators + Wiener-Hammerstein | P0 | 高 | https://arxiv.org/abs/2302.13141 |
| An et al. 2019, Hybrid Wiener for aerodynamic lift | P0 | 高 | https://arxiv.org/abs/1912.08842 |
| Tiels, Schoukens 2014, Wiener GOBF identification | P0 | 高 | https://doi.org/10.1016/j.automatica.2014.10.010 |
| Wahlberg, Ljung 2018, Stochastic Wiener CRLB | P1 | 中 | https://arxiv.org/abs/1805.09102 |
| Alpert et al. 2016, Wiener filtering calorimetric sensors | P1 | 中 | 10.1007/s10909-015-1402-y |
| Kuang, Lin 2025, Assumed Density Filtering | P1 | 中 | https://arxiv.org/abs/2511.09016 |
| Bai et al. 2025, WaveNet-Volterra ANC | P1 | 中 | https://arxiv.org/abs/2504.04450 |

#### KAN效率文献 (Round 168新增)
| 文献 | 类型 | 相关性 | 入口/链接 |
|-----|------|-------|----------|
| Pozdnyakov, Schwaller 2025, lmKAN | P1 | 高 | https://arxiv.org/abs/2509.07103 |
| Yu et al. 2025, PolyKAN | P1 | 高 | https://arxiv.org/abs/2511.14852 |
| Zhang et al. 2026, Spectral Gating Networks | P1 | 高 | https://arxiv.org/abs/2602.07679 |
| Southworth, Benner et al. 2026, KAN Multi-layer Training | P1 | 高 | https://arxiv.org/abs/2603.04827 |
| Liu et al. 2026, GRAU accelerator | P1 | 高 | https://arxiv.org/abs/2602.22352 |
| Escudero et al. 2026, Physical Analog KAN | P1 | 高 | https://arxiv.org/abs/2602.07518 |
| Bayeh et al. 2026, TruKAN | P1 | 中 | https://arxiv.org/abs/2602.03879 |

### 关键发现

1. **频域损失**：Du 2024的Neural Spectral Methods提出了自监督频域学习方法；TF-TransUNet1D (2025)使用双域损失（时域+频域）进行ECG去噪，验证了联合损失的有效性

2. **Wiener模型传感器应用**：Willemstein 2023的工作将Hammerstein-Wiener模型应用于3D打印泡沫传感器力估计（R²=0.85），证明了Wiener模型在传感器补偿中的实用性

3. **KAN效率**：新增多篇效率对比论文，lmKAN实现6x FLOPs减少，PolyKAN实现1.2-10x推理加速，证明KAN硬件优化是活跃研究方向

### 明确排除
- 无新排除项

## 待核实事项
- 新增文献需下载PDF并验证内容
- 部分新发现文献尚未在GAP文献缺口分析中评估对GAP的支撑能力

## 对文档的影响
- 更新了 `docs/research/literature/raw_literature.md`（新增频域损失、Wiener模型、KAN效率三个Round 168章节）
- 更新了 `docs/research/literature/literature_catalog.md`（新增New (R168)标记的文献条目）
- 是否需要更新 SUMMARY：待确认
- 是否需要后续 STEP2 分析：是（需验证新发现文献并评估GAP支撑能力）

## 原始链接
- https://arxiv.org/abs/2312.05225 (Neural Spectral Methods)
- https://arxiv.org/abs/1810.11945 (STFT Spectral Loss)
- https://arxiv.org/abs/2301.02886 (PNP Loss)
- https://arxiv.org/abs/2210.13438 (High Fidelity Neural Audio Compression)
- https://arxiv.org/abs/2508.20398 (TF-TransUNet1D)
- https://arxiv.org/abs/2303.04719 (Wiener-Hammerstein GRF estimation)
- https://arxiv.org/abs/2302.13141 (Wiener-Hammerstein 3D printed actuators)
- https://arxiv.org/abs/1912.08842 (Hybrid Wiener aerodynamic lift)
- https://doi.org/10.1016/j.automatica.2014.10.010 (Wiener GOBF)
- https://arxiv.org/abs/2509.07103 (lmKAN)
- https://arxiv.org/abs/2511.14852 (PolyKAN)
- https://arxiv.org/abs/2602.07679 (Spectral Gating Networks)
- https://arxiv.org/abs/2603.04827 (KAN Multi-layer Training)
- https://arxiv.org/abs/2602.22352 (GRAU)
- https://arxiv.org/abs/2602.07518 (Physical Analog KAN)
