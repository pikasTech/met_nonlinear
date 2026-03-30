# 调研报告：STEP1 Round118 文献扩展检索

## 基本信息
- 日期：2026-03-30
- 阶段：STEP1 调研
- 覆盖范围：Wiener模型、KAN网络、频域损失、传感器漂移补偿
- 是否使用子代理：是（4个并行方向）

## 检索路径

### 子代理1：Wiener模型最新论文
- 检索数据库：arXiv, IEEE Xplore, ScienceDirect
- 关键词：Wiener system identification, Wiener-Hammerstein neural network, nonlinear block-structured, amplitude-dependent frequency response
- 状态：子代理返回本地文献库结果，无新增arXiv实时发现

### 子代理2：KAN网络最新论文
- 检索数据库：arXiv (cs.LG, stat.ML)
- 关键词：Kolmogorov-Arnold Networks, KAN time series sensor, KAN nonlinear modeling
- 新增论文：
  - Process-Informed Forecasting (Rubini 2025) - P0/高
  - Fourier-KAN-Mamba (Wang 2025) - P0/高
  - Time-TK (Zhang 2026) - P0/高
  - DualFlexKAN (Ortiz 2026) - P1/高
  - FEKAN (Menon 2026) - P1/高
  - Physical Analog KAN (Escudero 2026) - P1/高

### 子代理3：频域损失最新论文
- 检索数据库：arXiv, IEEE Xplore, ICML/ICLR 2025-2026
- 关键词：frequency domain loss, spectral loss, adaptive frequency, Fourier domain training
- 核心发现：
  - FreST Loss (Wang 2026) - https://arxiv.org/abs/2603.04418
  - PaCoDi (Cai 2026) - https://arxiv.org/abs/2602.17706
  - AFMAE公式确认来源：FreDF (Wang 2025, ICLR)

### 子代理4：传感器漂移补偿论文
- 检索数据库：arXiv, IEEE Sensors, Measurement期刊
- 关键词：sensor drift compensation, electrochemical sensor nonlinearity, seismic sensor calibration
- 核心论文：
  - Elliott & Sutton 2002 (前馈vs反馈) - P0/高
  - Chen et al. 2016 (MEMS力反馈) - P0/高
  - Fasmin & Srinivasan 2017 (幅度依赖阻抗) - P0/高

## 发现结果

### 新增文献线索

| 文献 | 类型 | 相关性 | 入口/链接 |
|-----|------|-------|----------|
| Process-Informed Forecasting (Rubini 2025) | P0 | 高 | https://arxiv.org/abs/2509.20349 |
| Fourier-KAN-Mamba (Wang 2025) | P0 | 高 | https://arxiv.org/abs/2511.15083 |
| Time-TK (Zhang 2026) | P0 | 高 | https://arxiv.org/abs/2602.11190 |
| DualFlexKAN (Ortiz 2026) | P1 | 高 | https://arxiv.org/abs/2603.08583 |
| FEKAN (Menon 2026) | P1 | 高 | https://arxiv.org/abs/2602.16530 |
| Physical Analog KAN (Escudero 2026) | P1 | 高 | https://arxiv.org/abs/2602.07518 |
| FreST Loss (Wang 2026) | P0 | 高 | https://arxiv.org/abs/2603.04418 |
| PaCoDi (Cai 2026) | P1 | 高 | https://arxiv.org/abs/2602.17706 |
| Elliott & Sutton 2002 | P0 | 高 | https://doi.org/10.1121/1.1510668 |
| Chen et al. 2016 | P0 | 高 | https://doi.org/10.3390/s16091485 |
| Fasmin & Srinivasan 2017 | P0 | 高 | https://doi.org/10.1149/2.0031712jes |

### 入口已定位
- FreDF (Wang 2025, ICLR) - AFMAE公式直接来源
- KAN-FIF (Shen 2026) - 参数压缩94.8%，推理加速68.7%
- OLMA (Shi 2025) - 频域熵减定理最强理论支撑

### 疑似重复
- 无

### 明确排除
- INR-Bench - 基准测试论文，非直接应用

## 待核实事项
- Physical Analog KAN (Escudero 2026) 能量消耗数据(~250pJ)需进一步核实
- Process-Informed Forecasting 是否与已有Process-Informed KAN重复

## 对文档的影响
- 更新了 `raw_literature.md`：新增10条文献线索
- 更新了 `literature_catalog.md`：新增调研报告索引
- 是否需要更新 GAP文献缺口：否（现有缺口已低）

## 原始链接
- https://arxiv.org/abs/2509.20349
- https://arxiv.org/abs/2511.15083
- https://arxiv.org/abs/2602.11190
- https://arxiv.org/abs/2603.08583
- https://arxiv.org/abs/2602.16530
- https://arxiv.org/abs/2602.07518
- https://arxiv.org/abs/2603.04418
- https://arxiv.org/abs/2602.17706
- https://doi.org/10.1121/1.1510668
- https://doi.org/10.3390/s16091485
- https://doi.org/10.1149/2.0031712jes
