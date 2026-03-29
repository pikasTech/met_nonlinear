# 调研报告：STEP1 Round 4 - 2026-03-28

## 基本信息
- 日期：2026-03-28
- 阶段：STEP1 调研 Round 4
- 覆盖范围：KAN硬件实现/Wiener传感器应用/RNN vs CNN效率/频域损失理论/TKAN系验证
- 是否使用子代理：是（并行4方向搜索）

## 检索路径

### 方向1：Wiener模型在电化学/地震传感器应用
- 关键词：Wiener model electrochemical sensor, Wiener model seismic sensor, MEMS accelerometer nonlinear modeling
- 主要数据库：IEEE Xplore, Google Scholar, ScienceDirect
- 发现数据库：MIT DSpace

### 方向2：KAN硬件实现（LUT/FPGA/ASIC）
- 关键词：KAN FPGA, KAN hardware, KAN LUT, KAN accelerator
- 主要数据库：arXiv, IEEE Xplore, ACM Digital Library
- 发现：多篇KAN硬件实现论文

### 方向3：RNN vs 1D-CNN计算效率
- 关键词：RNN vs CNN efficiency, 1D-CNN parameter count, recurrent vs convolutional FLOPs
- 主要数据库：arXiv, IEEE Xplore
- 关键发现：文献与论文声称**矛盾**

### 方向4：TKAN/TimeKAN/TFKAN验证
- 关键词：Temporal KAN, TimeKAN, TFKAN arXiv
- 主要数据库：arXiv

### 方向5：AFMAE替代理论（频域损失）
- 关键词：spectral loss time series, frequency domain loss neural network, BSP Loss
- 主要数据库：arXiv, Google Scholar

## 发现结果

### 新增文献线索

#### A. Wiener模型在传感器应用（高相关性）
| 作者 | 年份 | 标题 | DOI/URL | 相关性 |
|------|------|------|---------|--------|
| Hsu, Chou, Kuo | 2017 | Drift modeling and compensation for MEMS-based gyroscope using a Wiener-type recurrent neural network | IEEE Inertial Sensors and Systems | High |
| Kumar, Tudu, Ghosh | 2020 | Nonlinear modeling of voltammetric sensor signals: Application to the E-tongue measurement | IEEE Sensors Journal | High |
| Ang, Khosla, Riviere | 2007 | Nonlinear regression model of a low-g MEMS accelerometer | IEEE Sensors Journal | High |
| Iqbal | 2024 | Volterra System Analysis for an Electrochemical Sensor | MIT DSpace | High |
| Li, Zhou, Liu | 2024 | Parameter estimation for the Hammerstein-Wiener nonlinear system and application in lithium-ion batteries | Journal of Energy Storage | Medium |

#### B. KAN硬件/LUT实现（填补P2-1空白）
| 作者 | 年份 | 标题 | DOI/URL | 效率声称 |
|------|------|------|---------|----------|
| Hoang, Gupta, Harris | 2026 | KANELÉ: Kolmogorov-Arnold Networks for Efficient LUT-based Evaluation (ISFPGA 2026) | 10.48550/arXiv.2512.12850 | **2700x FPGA加速** |
| Kuznetsov | 2026 | LUT-KAN: Segment-wise LUT Quantization for Fast KAN Inference | 10.48550/arXiv.2601.03332 | **12x CPU加速** |
| Kuznetsov | 2026 | LUT-Compiled KAN for IoT Edge Devices | 10.48550/arXiv.2601.08044 | **5000x加速( batch=1)** |
| Huang et al. | 2025 | Hardware Acceleration of KAN in Large-Scale Systems (TSMC 22nm) | 10.48550/arXiv.2509.05937 | 芯片实测 |
| Ghosh, Boppu | 2026 | FPGA-based Hardware Acceleration of KAN (IEEE TCAS) | 10.1109/TCAS.2026.11408882 | FPGA实现 |
| Li et al. | 2025 | FRIKAN (IEEE TIM) | TIM-25-06440 | **2.1x LSTM效率提升** |

#### C. RNN vs CNN效率（⚠️重要矛盾发现）
| 作者 | 年份 | 标题 | DOI/URL | 关键发现 |
|------|------|------|---------|----------|
| Saha, Samanta | 2026 | Rethinking Temporal Models for TinyML: LSTM vs 1D-CNN | 10.48550/arXiv.2603.04860 | 1D-CNN: 35%更少RAM, 25%更少Flash, **74x更快推理** |
| Bian et al. | 2025 | TinierHAR | 10.48550/arXiv.2507.07949 | DeepConvLSTM有**43x更多参数**, **58x更多MACs** |
| Bai et al. | 2018 | TCN: CNN vs RNN | 10.48550/arXiv.1803.01271 | CNN**优于**LSTM, 更长有效记忆 |

#### D. TKAN系论文验证（已确认存在）
| 论文 | arXiv ID | 全作者 | 关键声称 |
|------|----------|--------|----------|
| TKAN | 2405.07344 | Genet, Inzirillo | KAN+LSTM混合, 无具体效率指标 |
| TimeKAN | 2502.06910 | Huang et al. | 频率分解, 声称"lightweight" |
| TFKAN | 2506.12696 | Kui et al. | 时频双分支, 无具体效率指标 |

#### E. AFMAE替代理论（BSP Loss最接近）
| 作者 | 年份 | 标题 | DOI/URL | 与AFMAE关系 |
|------|------|------|---------|--------------|
| Chakraborty et al. | 2025 | BSP Loss for Chaotic Systems | 10.48550/arXiv.2502.00472 | **最相似概念**：自适应频域bin权重+MAE |
| Sun et al. | 2025 | FreLE: Low-Frequency Spectral Bias | 10.48550/arXiv.2510.25800 | 频域正则化框架 |
| Rippel et al. | 2015 | Spectral Representations for CNNs (NeurIPS) | - | 频域理论基础 |

### 入口已定位
- KANELÉ (ISFPGA 2026) - KAN LUT效率的**核心证据**
- BSP Loss - AFMAE概念的理论基础
- Hsu 2017 - Wiener型MEMS陀螺仪漂移建模

### 疑似重复/冲突
- RNN vs CNN效率声称与**文献矛盾**：论文声称"RNN参数少于1D-CNN"，但文献显示1D-CNN参数更少、速度更快

### 明确排除
- KAN 2.0 (不同目标)
- Transformer时间序列（与效率声称无关）

## 待核实事项

1. **⚠️ RNN vs CNN效率矛盾**：论文声称"RNN的计算参数少于1D-CNN"，但Saha 2026、Bian 2025等文献显示相反结论。需要重新评估此声称。

2. **KANet IEEE TIM全文**：该论文无arXiv预印本，IEEE TIM付费，获取完整FLOPs数据需要机构权限。

3. **Wiener传感器文献获取**：Hsu 2017、Ang 2007等文献需确认DOI完整性。

4. **BSP Loss vs AFMAE**：确认BSP Loss的adaptive frequency bin weighting是否完全对应AFMAE概念。

## 对文档的影响

- 更新 `raw_literature.md`：新增KAN硬件实现、Wiener传感器应用、RNN效率矛盾等条目
- 更新 `literature_catalog.md`：新增KAN LUT分类，更新Architecture Efficiency冲突标记
- 更新本文件到 `docs/research/literature/20260328/STEP1_Round4_research_report.md`

## 原始链接

- KANELÉ: https://doi.org/10.48550/arXiv.2512.12850
- LUT-KAN: https://doi.org/10.48550/arXiv.2601.03332
- IoT KAN: https://doi.org/10.48550/arXiv.2601.08044
- Saha LSTM vs 1D-CNN: https://doi.org/10.48550/arXiv.2603.04860
- TinierHAR: https://doi.org/10.48550/arXiv.2507.07949
- TCN CNN vs RNN: https://doi.org/10.48550/arXiv.1803.01271
- BSP Loss: https://doi.org/10.48550/arXiv.2502.00472
- FreLE: https://doi.org/10.48550/arXiv.2510.25800
- Hsu 2017: IEEE Inertial Sensors and Systems (无DOI)
- TKAN: https://arxiv.org/abs/2405.07344
- TimeKAN: https://arxiv.org/abs/2502.06910
- TFKAN: https://arxiv.org/abs/2506.12696