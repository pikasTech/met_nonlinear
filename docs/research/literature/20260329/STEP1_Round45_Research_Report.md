# 调研报告：Round 45 - 新方向拓展

## 基本信息
- 日期：2026-03-29
- 阶段：STEP1 调研
- 覆盖范围：KAN网络、Wiener模型、频域损失、传感器漂移补偿新文献
- 是否使用子代理：是；并行维度：4个子代理分别搜索KAN/Wiener/频域损失/传感器漂移

## 检索路径
- 关键词：
  - KAN: KAN 2025 2026, Kolmogorov-Arnold Networks, KAN time series, KAN efficiency
  - Wiener: Wiener-Hammerstein 2025 2026, Wiener sensor, block-structured nonlinear systems
  - 频域损失: frequency domain loss, spectral loss time series, AFMAE
  - 传感器漂移: sensor drift compensation, electrochemical sensor, seismic sensor, machine learning calibration
- 主要数据库：arXiv, IEEE Xplore, Google Scholar
- 新发现数据库：无新增
- 检索式：组合关键词 + 年份限制 2024-2026

## 发现结果

### 新增文献线索

#### KAN网络（新发现较少，大部分已存在）
| 标题 | 作者 | 年份 | DOI | 备注 |
|------|------|------|-----|------|
| Spectral Gating Networks | Zhang et al. | 2026 | arXiv:2602.07679 | 已在R21分类 |
| Free-RBF-KAN | Chiu et al. | 2026 | arXiv:2601.07760 | 已在R21分类 |
| BiKA | Liu et al. | 2026 | arXiv:2602.23455 | 已在R17分类 |
| KMLP | Zhang et al. | 2026 | arXiv:2602.22777 | 已在R17分类 |
| Physical KAN | Taglietti et al. | 2026 | arXiv:2601.15340 | 已在R20分类 |

#### Wiener模型（新发现1篇）
| 标题 | 作者 | 年份 | DOI | 相关性 |
|------|------|------|-----|--------|
| Complex-Phase, Data-Driven Identification of Grid-Forming Inverter Dynamics | Büttner et al. | 2024 | arXiv:2409.17132 | 高 - Wiener-Hammerstein系统辨识应用于电力电子 |

#### 频域损失（新发现1篇）
| 标题 | 作者 | 年份 | DOI | 相关性 |
|------|------|------|-----|--------|
| Fourier Head: Helping LLMs Learn Complex Probability Distributions | Gillman et al. | 2024 | arXiv:2410.22269 | 中 - Fourier层用于时序/连续分布建模 |

#### 传感器漂移补偿（新发现12篇）
| 标题 | 作者 | 年份 | DOI | 相关性 |
|------|------|------|-----|--------|
| SNM Module for E-nose Gas Recognition | Chen et al. | 2025/26 | arXiv:2512.22792 | 高 - 电子鼻漂移补偿，几何解耦方法 |
| SAW Gas Sensors Review with ML | Acharya et al. | 2025 | arXiv:2510.04940 | 中 - SAW气体传感器ML漂移补偿综述 |
| Veli: Unsupervised Air Quality Correction | Dalbah et al. | 2025 | arXiv:2508.02724 | 高 - 低成本空气质量传感器无监督校正 |
| XGBoost In-field Sensor Calibration | Yin et al. | 2025 | arXiv:2506.15840 | 高 - XGBoost传感器现场校准 |
| Mitigating Nonlinearities in Homodyne Interferometers | Lehmann et al. | 2025 | arXiv:2511.04386 | 高 - 地震传感器非线性校正 |
| Transformer-Based Predictive Calibration | Parthasarathy et al. | 2026 | arXiv:2603.20297 | 高 - Transformer预测校准调度 |
| IoT AD Benchmark with Drift Augmentations | Zhevnenko et al. | 2026 | arXiv:2602.15457 | 高 - 传感器漂移基准测试协议 |
| ML Calibration: Cape Point Study | Barrett, Mishra | 2025 | arXiv:2503.13487 | 高 - 低成本CO2传感器ML校准实证 |
| PPO with Sequence Models for Sensor Drift | Vogt-Lowell et al. | 2026 | arXiv:2603.04648 | 中 - 强化学习处理传感器漂移 |
| PC2DAE: Physics-Constrained UAV Gas Sensing | Ramadan et al. | 2026 | arXiv:2601.11794 | 高 - 物理约束无人机气体传感器漂移补偿 |
| Contrastive Continual Learning for IoT | Chathoth et al. | 2026 | arXiv:2602.04881 | 中 - 持续学习处理传感器漂移 |
| Unsupervised Domain Adaptation for Sensors | Faghih Niresi et al. | 2024/25 | arXiv:2411.06917 | 高 - 空气质量问题传感器域适应 |

### 入口已定位
- arXiv 持续是最新论文的主要来源
- IEEE TIM, Measurement 期刊有相关传感器补偿论文

### 疑似重复
- KAN相关文献大部分已在本轮前收录

### 明确排除
- 无新排除

## 待核实事项
1. Büttner 2024 arXiv:2409.17132 - 需验证是否与现有Wiener-Hammerstein文献重复
2. Fourier Head - 需确认是否有时序相关应用

## 对文档的影响
- 更新文件：
  - raw_literature.md - 新增12篇传感器漂移补偿论文
  - literature_catalog.md - 新增Wiener模型和传感器漂移分类
- 是否需要更新 SUMMARY：否
- 是否需要后续 STEP2 分析：否（仅为线索收集）

## 原始链接
- https://arxiv.org/abs/2409.17132
- https://arxiv.org/abs/2410.22269
- https://arxiv.org/abs/2512.22792
- https://arxiv.org/abs/2510.04940
- https://arxiv.org/abs/2508.02724
- https://arxiv.org/abs/2506.15840
- https://arxiv.org/abs/2511.04386
- https://arxiv.org/abs/2603.20297
- https://arxiv.org/abs/2602.15457
- https://arxiv.org/abs/2503.13487
- https://arxiv.org/abs/2603.04648
- https://arxiv.org/abs/2601.11794
- https://arxiv.org/abs/2602.04881
- https://arxiv.org/abs/2411.06917