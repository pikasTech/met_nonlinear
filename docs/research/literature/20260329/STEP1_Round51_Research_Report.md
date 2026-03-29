# 调研报告：STEP1 Round51 - 系统性文献检索扩充

## 基本信息
- 日期：2026-03-29
- 阶段：STEP1 调研
- 覆盖范围：P0/P1/P2核心方向系统检索
- 是否使用子代理：是；5个并行方向（MEASUREMENT期刊、Wiener模型、KAN网络、频域损失、传感器漂移补偿）

## 检索路径

### 方向1：MEASUREMENT期刊传感器非线性论文
- 关键词：sensor nonlinearity compensation, sensor drift, sensor calibration, temperature compensation, electrochemical sensor, seismic sensor
- 主要数据库：Google Scholar (Measurement journal), ScienceDirect, IEEE Xplore
- 发现：85+篇论文，已超额完成50篇目标

### 方向2：Wiener模型理论最新进展
- 关键词：Wiener system identification, Wiener-Hammerstein, nonlinear block-structured, Volterra series
- 主要数据库：IEEE Xplore, ScienceDirect, arXiv (2024-2026)
- 发现：已建立完整Wiener-KAN混合架构文献链

### 方向3：KAN网络最新进展
- 关键词：Kolmogorov-Arnold Networks, KAN, spline, temporal KAN, KAN efficiency
- 主要数据库：arXiv (2024-2026), Google Scholar, IEEE Xplore
- 发现：671篇相关论文，主要聚焦效率优化和时序应用

### 方向4：频域损失函数
- 关键词：frequency domain loss, spectral loss, AFMAE, focal frequency
- 主要数据库：arXiv, IEEE Xplore, Google Scholar
- 发现：FreDF (ICLR 2025)是AFMAE的直接理论依据

### 方向5：传感器漂移补偿深度学习
- 关键词：drift compensation deep learning, sensor drift neural network, e-nose, MEMS accelerometer
- 主要数据库：IEEE Xplore, ScienceDirect, arXiv
- 发现：TDACNN、OTTA-DriftNet等代表性工作

## 发现结果

### 新增MEASUREMENT期刊论文（已找到59篇2020年后）

| 类别 | 篇数 | 代表论文 |
|------|------|----------|
| 传感器非线性补偿 | 10+ | Li 2024 (nano-g accelerometer), Zhao 2024 (nonparametric EKF) |
| 传感器漂移补偿 | 10+ | Lin 2020 (electrochemical seismic), Schaller 2025 (AutoML) |
| 温度补偿 | 5+ | Han 2020 (AGA-BP NN), Zhu 2025 (IAPSO-RBF) |
| 电化学/地震传感器 | 10+ | Liu 2026 (seismic sensor), Qiu 2025 (FBG accelerometer) |
| 神经网络/深度学习补偿 | 10+ | Pietrenko-Dabrowska 2024 (ML NO2), Singh 2024 (NN threshold) |
| 加速度计/陀螺仪校准 | 10+ | Kokuyama 2022, Gaitan 2022, Nan 2025 |

### 新增Wiener模型文献
- SS-KAN (Cruz 2025): 状态空间KAN用于Wiener-Hammerstein
- Barron-Wiener-Laguerre (Manavalan 2026): 理论扩展
- LSTM-based Wiener (Li 2024): 深度学习与Wiener结合

### 新增KAN效率论文
- KANELÉ (Hoang 2026, ISFPGA): FPGA上KAN加速2700倍
- KANtize (Errabii 2026): 2-3位量化，FPGA资源减少36%
- LUT-KAN (Kuznetsov 2026): 分段LUT量化

### 新增频域损失论文
- FreDF (Wang 2025, ICLR): L^α = α·|F(Ŷ)-F(Y)|₁ + (1-α)·MSE
- OLMA (Shi 2025): 熵减定理支持DFT
- FreLE (Sun 2025): 解决低频偏置问题

### 新增传感器漂移补偿论文
- TDACNN (Zhang 2022): 目标域无关域适应CNN
- OTTA-DriftNet (Liang 2025): 在线测试时自适应
- Deep NN Hadamard (Badawi 2021): 化学传感器深度学习

## 待核实事项
- 部分MEASUREMENT论文需验证DOI有效性
- KAN 2.0 (Liu 2024) - 不同目标，已标记排除
- 传感器数据集会话题需继续追踪Schoukens组工作

## 对文档的影响
- 更新了 `raw_literature.md`：新增MEASUREMENT期刊论文59篇
- 更新了 `literature_catalog.md`：新增文献分类
- 是否需要更新 SUMMARY：否
- 是否需要后续 STEP2 分析：建议对高相关性新文献进行深度分析

## 原始链接

### MEASUREMENT期刊核心论文
- 10.1016/j.measurement.2020.107518 - Lin et al. (2020) 电化学地震传感器
- 10.1016/j.measurement.2020.108019 - Han et al. (2020) 电容加速度计温度漂移
- 10.1016/j.measurement.2024.115158 - Ahmad (2024) 低成本传感器漂移自校准
- 10.1016/j.measurement.2025.117097 - Schaller & Kruse (2025) AutoML漂移补偿

### Wiener/KAN核心理论
- https://arxiv.org/abs/2506.16392 - Cruz et al. (2025) SS-KAN
- https://arxiv.org/abs/2602.13098 - Manavalan, Tronarp (2026) Barron-Wiener-Laguerre
- https://arxiv.org/abs/2402.02399 - Wang et al. (2025) FreDF ICLR

### 频域损失
- https://arxiv.org/abs/2012.12821 - Jiang et al. (2020) Focal Frequency Loss
- https://arxiv.org/abs/2505.11567 - Shi et al. (2025) OLMA
- https://arxiv.org/abs/2510.25800 - Sun et al. (2025) FreLE

### 传感器漂移补偿
- https://arxiv.org/abs/2110.07509 - Zhang et al. (2022) TDACNN
- https://arxiv.org/abs/2507.17071 - Lin, Zhan (2025) Knowledge Distillation E-nose
- https://doi.org/10.1016/j.measurement.2018.05.020 - Dutta et al. (2018) DIC多传感器
