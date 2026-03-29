# 调研报告：Round 21 - 并行扩展搜索

## 基本信息
- 日期：2026-03-28
- 阶段：STEP1 调研
- 覆盖范围：MEASUREMENT期刊、FreDF频域损失、Wiener模型传感器应用、KAN时序效率
- 是否使用子代理：是（4个并行方向）

## 检索路径

### 子代理1：MEASUREMENT期刊传感器非线性补偿
- 关键词：sensor nonlinearity compensation measurement, sensor calibration, nonlinear calibration, temperature compensation sensor, drift correction measurement
- 主要数据库：ScienceDirect, Google Scholar, CrossRef
- 结果：找到5篇相关论文

### 子代理2：FreDF和频域损失
- 关键词：FreDF, frequency domain loss time series, spectral loss, AFMAE, focal frequency loss
- 主要数据库：arXiv, Google Scholar
- 结果：多数论文已在catalog中

### 子代理3：Wiener模型传感器应用
- 关键词：Wiener model electrochemical sensor, Wiener model seismic sensor, Wiener-Hammerstein sensor identification
- 主要数据库：IEEE Xplore, ScienceDirect, CrossRef
- 结果：直接匹配较少

### 子代理4：KAN时序效率
- 关键词：KAN time series efficiency, Kolmogorov-Arnold time series, KAN computational efficiency
- 主要数据库：arXiv, Google Scholar
- 结果：发现多篇新论文

## 发现结果

### MEASUREMENT期刊论文（已找到11篇，目标10篇 - 已达成）

| 论文 | 作者 | 年份 | DOI | 备注 |
|------|------|------|-----|------|
| Identification of sensor block model using Volterra series and frequency response function | Xu, Wang | 2008 | 10.1016/j.measurement.2008.03.008 | Volterra系列，传感器块模型 |
| Nonlinearity compensation of DIC-based multi-sensor measurement | Dutta et al. | 2018 | 10.1016/j.measurement.2018.05.020 | 多传感器非线性补偿 |
| Temperature drift modeling and compensation of capacitive accelerometer based on AGA-BP neural network | Han et al. | 2020 | 10.1016/j.measurement.2020.108019 | **2020后论文** |
| Parameter identification of fractional order Hammerstein model with two-stage piecewise nonlinearity | Rui et al. | 2022 | 10.1016/j.measurement.2022.111951 | **2020后论文** |
| Enhanced drift self-calibration of low-cost sensor networks | Ahmad | 2024 | 10.1016/j.measurement.2024.115158 | **2020后论文** |
| Neural network-guided correlation thresholding for WSN | Singh | 2024 | 10.1016/j.measurement.2024.115408 | **2020后论文** |
| Secondary measurement standard for dynamic pressure sensor | Amer et al. | 2024 | 10.1016/j.measurement.2024.116253 | **2020后论文** |
| Exploiting nonlinearity for sensitivity enhancement of TPoS gas sensor | Fang et al. | 2024 | 10.1016/j.measurement.2024.116559 | **2020后论文** |
| AutoML for multi-class anomaly compensation of sensor drift | Schaller, Kruse | 2025 | 10.1016/j.measurement.2025.117097 | **2020后论文** |
| Sensor to segment calibration for magnetic and inertial sensor based motion capture systems | Liu et al. | 2019 | 10.1016/j.measurement.2019.03.048 | 传感器校准方法论 |
| Optimum choice of measurement points for sensor calibration | Betta, Dell'Isola | 1996 | 10.1016/0263-2241(96)00019-x | 测量点优化基础论文 |

**进度**：11/10篇（其中8篇2020后），**目标已达成**

### FreDF和频域损失（已在catalog中）
- TimeCF/SAMFre (arXiv:2505.17532) - 已在R17
- FreIE/FreLE (arXiv:2510.25800) - 已在R17
- BSP Loss (arXiv:2502.00472) - 已在R17
- OLMA (arXiv:2505.11567) - 已在R17
- FIRE (arXiv:2510.10145) - 已在R17
- Fre-CW (arXiv:2508.08955) - 已在R17

### Wiener模型传感器应用（新增）
| 论文 | 作者 | 年份 | DOI | 备注 |
|------|------|------|-----|------|
| Nonlinear system identification using fractional Hammerstein-Wiener models | Hammar, Djamah, Bettayeb | 2019 | 10.1007/s11071-019-05331-9 | 分数阶Hammerstein-Wiener |
| Identification of Hammerstein-Wiener Models Based on Bias Compensation Recursive Least Squares | Li, Mao, Wang, Yuan, Jia | 2010 | 10.3724/sp.j.1004.2010.00163 | 块结构模型辨识 |
| Nonparametric models for Hammerstein-Wiener and Wiener-Hammerstein system identification | Risuleo, Hjalmarsson | 2020 | 10.1016/j.ifacol.2020.12.198 | 非参数方法 |

### KAN时序效率（新增关键论文）

| 论文 | 作者 | 年份 | arXiv ID | 关键贡献 |
|------|------|------|----------|----------|
| KAN-FIF: Spline-Parameterized Lightweight Physics-based Tropical Cyclone Estimation | Shen et al. | 2026 | 2602.12117 | **94.8%参数减少，68.7%推理加速** |
| KANtize: Low-bit Quantization of KAN | Errabii et al. | 2026 | 2603.17230 | **50x BitOps减少，2.9x GPU加速** |
| Spectral Gating Networks | Zhang et al. | 2026 | 2602.07679 | **11.7x推理加速** |
| Free-RBF-KAN | Chiu et al. | 2026 | 2601.07760 | 移除De Boor算法，更快训练推理 |
| Physical Analog KAN | Taglietti et al. | 2026 | 2601.15340 | **~10^2-10^3x能效提升** |
| BiKA: Binary KAN Accelerator | Liu et al. | 2026 | 2602.23455 | 二值化硬件加速器 |
| Ultra-fast On-chip Online Learning via Spline Locality in KAN | Hoang, Gupta, Harris | 2026 | 2602.02056 | **亚微秒在线学习** |
| FEKAN: Feature-Enriched KAN | Menon, Jagtap | 2026 | 2602.16530 | 特征富化无额外参数 |
| TruKAN: Truncated Power Functions | Bayeh et al. | 2026 | 2602.03879 | 更高效的可解释KAN |

## 待核实事项
1. ~~MEASUREMENT期刊目标已达成（11篇）~~
2. 多篇KAN效率论文需验证DOI和正式发表信息
3. FRIKAN (IEEE TIM TIM-25-06440) 需确认与当前工作的直接相关性

## 对文档的影响
- 更新文件：literature_catalog.md, raw_literature.md
- 新增section：KAN效率新进展（第21轮）
- 需要后续STEP2分析：是（特别是KAN效率数据）

## 原始链接
- 10.1016/j.measurement.2020.108019 (Han 2020)
- 10.1016/j.measurement.2019.03.048 (Liu 2019)
- 10.1016/0263-2241(96)00019-x (Betta 1996)
- 10.1007/s11071-019-05331-9 (Hammar 2019)
- 10.1016/j.ifacol.2020.12.198 (Risuleo 2020)
- arXiv:2602.12117 (KAN-FIF)
- arXiv:2603.17230 (KANtize)
- arXiv:2602.07679 (Spectral Gating)
- arXiv:2601.07760 (Free-RBF-KAN)
- arXiv:2601.15340 (Physical Analog KAN)
