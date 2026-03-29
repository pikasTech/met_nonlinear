# 调研报告：Round 20 文献检索

## 基本信息
- 日期：2026-03-28
- 阶段：STEP1 调研 Round 20
- 覆盖范围：Wiener模型、KAN网络、频域损失函数、传感器漂移补偿、神经网络架构效率
- 是否使用子代理：是（5个子代理并行检索）

## 检索路径
- 关键词：
  - Wiener: "Wiener system identification", "Wiener-Hammerstein neural network", "Wiener model sensor"
  - KAN: "KAN time series", "Kolmogorov-Arnold Networks", "KAN sensor", "KAN hardware"
  - 频域: "frequency domain loss", "spectral loss", "Fourier loss", "FFT loss"
  - 传感器: "sensor drift compensation", "electrochemical sensor drift", "neural network sensor calibration"
  - 效率: "KAN efficiency comparison", "neural network computational efficiency", "TinyML"
- 主要数据库：arXiv, IEEE Xplore, Google Scholar
- 检索式：并行子代理自动生成

## 发现结果

### Wiener模型新文献
| 作者 | 年份 | 标题 | 链接 | 分类 | 相关性 |
|------|------|------|------|------|--------|
| Manavalan, Tronarp | 2026 | Barron-Wiener-Laguerre models | arXiv:2602.13098 | P0 | 高 |
| Cedeño et al. | 2025 | Quadrature Gaussian Sum Filter for Wiener Systems | arXiv:2505.08469 | P1 | 高 |
| Bonassi et al. | 2023 | Structured state-space models are deep Wiener models | arXiv:2312.06211 | P0 | 高 |
| Dželo et al. | 2024 | Black-Box Inverter Using Hammerstein-Wiener | arXiv:2411.13213 | P1 | 高 |

### KAN网络新文献
| 作者 | 年份 | 标题 | 链接 | 分类 | 相关性 |
|------|------|------|------|------|--------|
| Taglietti et al. | 2026 | Physical Kolmogorov-Arnold Networks | arXiv:2601.15340 | P0 | 高 |
| Nithinkumar, Anand | 2026 | LSTM-KAN hybrid for respiratory classification | arXiv:2601.03610 | P0 | 高 |
| Makinde | 2026 | T-KAN for Limit Order Book | arXiv:2601.02310 | P0 | 高 |
| Singh et al. | 2025 | TSKAN for QoE modeling | arXiv:2509.20595 | P1 | 高 |
| Sen et al. | 2025 | Physics-informed KAN under Ehrenfest constraints | arXiv:2509.18483 | P0 | 高 |
| Gao et al. | 2025 | DecoKAN for Crypto Forecasting | arXiv:2512.20028 | P1 | 高 |

### 频域损失函数新文献
| 作者 | 年份 | 标题 | 链接 | 分类 | 相关性 |
|------|------|------|------|------|--------|
| Shi et al. | 2025 | OLMA: One Loss for More Accurate Time Series | arXiv:2505.11567 | P0 | 高 |
| Bai, Kawahara | 2026 | Dualformer: Time-Frequency Dual Domain Learning | arXiv:2601.15669 | P1 | 高 |
| Zhang et al. | 2026 | xCPD: Graph Spectral Decomposition | arXiv:2603.13702 | P0 | 高 |
| Moghadas et al. | 2025 | FreqFlow: Frequency Domain Flow Matching | arXiv:2511.16426 | P1 | 高 |
| Yang et al. | 2025 | FRWKV: Frequency-Domain Linear Attention | arXiv:2512.07539 | P1 | 高 |
| Zhang et al. | 2026 | M²FMoE: Multi-Resolution Multi-View Frequency | arXiv:2601.08631 | P1 | 高 |

### 传感器漂移补偿新文献
| 作者 | 年份 | 标题 | 链接 | 分类 | 相关性 |
|------|------|------|------|------|--------|
| Warner et al. | 2020 | Context adaptation for sensor drift | arXiv:2003.07292 | P1 | 高 |
| Zhang et al. | 2026 | Taiji-2 gravitational reference sensor calibration | arXiv:2603.25327 | P1 | 高 |

### 神经网络架构效率新文献
| 作者 | 年份 | 标题 | 链接 | 分类 | 相关性 |
|------|------|------|------|------|--------|
| Errabii et al. | 2026 | KANtize: Low-bit Quantization for KAN | arXiv:2603.17230 | P0 | 高 |
| Ou et al. | 2026 | VIKIN: KAN/MLP Accelerator | arXiv:2603.01165 | P0 | 高 |
| Liu et al. | 2026 | BiKA: Binary KAN Accelerator | arXiv:2602.23455 | P1 | 高 |
| Shen et al. | 2026 | KAN-FIF: Spline-Parameterized Physics-based | arXiv:2602.12117 | P0 | 高 |
| Gogoi | 2026 | COMET-SG1: Lightweight Autoregressive Regressor | arXiv:2601.20772 | P0 | 高 |
| Birkel | 2025 | Tiny-TSM: Lightweight Time Series Foundation Model | arXiv:2511.19272 | P0 | 高 |
| Cioflan et al. | 2025 | NanoHydra: Energy-Efficient Time-Series | arXiv:2510.20038 | P0 | 高 |
| Gaonkar et al. | 2026 | KAN vs MLP: Paradigm Shift | arXiv:2601.10563 | P1 | 高 |
| Li et al. | 2024 | XNet Outperforms KAN | arXiv:2410.02033 | P1 | 中 |

## 待核实事项
1. 所有arXiv文献需要核实元数据
2. 部分文献可能与已收录文献重复，需交叉核对
3. 部分IEEE Xplore链接需要机构账号访问

## 对文档的影响
- 更新了 `raw_literature.md`：新增约30条文献线索
- 更新了 `literature_catalog.md`：新增文献分类表
- 需要后续STEP2分析高相关性文献

## 原始链接
- arXiv: https://arxiv.org/abs/...
- IEEE Xplore: https://ieeexplore.ieee.org/...
