# 调研报告：STEP1 Round74 文献调研

## 基本信息
- 日期：2026-03-29
- 阶段：STEP1 调研
- 覆盖范围：P0/P1/P2 全面搜索 - KAN网络、Wiener模型、频域损失、传感器漂移补偿、MEASUREMENT期刊
- 是否使用子代理：是；五路并行搜索

## 检索路径

### 子代理 1：Wiener模型搜索
- 关键词：Wiener system identification, Wiener-Hammerstein, nonlinear system identification block-structured, Volterra Wiener
- 主要数据库：arXiv, IEEE Xplore
- 新发现数据库：无新增
- 检索式：site:arxiv.org "Wiener system identification" OR "Wiener-Hammerstein"

### 子代理 2：KAN网络搜索
- 关键词：Kolmogorov-Arnold Networks, KAN time series, KAN efficiency, spline networks, KAN implementation
- 主要数据库：arXiv
- 新发现数据库：无
- 检索式：site:arxiv.org "Kolmogorov-Arnold" OR "KAN" (2025-2026)

### 子代理 3：频域损失搜索
- 关键词：frequency domain loss, spectral loss time series, FFT loss neural network, AFMAE, focal frequency loss
- 主要数据库：arXiv
- 新发现数据库：无
- 检索式：site:arxiv.org "frequency domain loss" OR "spectral loss" OR "FFT loss"

### 子代理 4：传感器漂移补偿搜索
- 关键词：sensor drift compensation, electrochemical sensor drift, MEMS accelerometer drift, neural network temperature compensation
- 主要数据库：arXiv, IEEE Xplore, Sensors (MDPI)
- 新发现数据库：IEEE Sensors Letters
- 检索式：site:arxiv.org "sensor drift" OR "drift compensation" deep learning

### 子代理 5：MEASUREMENT期刊搜索
- 关键词：sensor nonlinearity measurement, temperature drift compensation sensor, accelerometer calibration neural network
- 主要数据库：ScienceDirect (Measurement期刊)
- 新发现数据库：无
- 检索式：site:sciencedirect.com "sensor nonlinearity" measurement

## 发现结果

### 新增文献线索

| 类别 | 数量 | 备注 |
|------|------|------|
| KAN网络 | 12篇 | 主要是vision/physics应用，time series相关较少 |
| Wiener模型 | 0篇 | 文献库已完备 |
| 频域损失 | 3篇 | FCDNet, HyperTime, FastNet |
| 传感器漂移补偿 | 6篇 | 涵盖电子鼻、磁补偿、惯性导航 |
| MEASUREMENT期刊 | 11篇 | 温度漂移、加速度计标定、光纤传感 |

### 入口已定位

- arXiv cs.LG, cs.CV, eess.SY 持续有新KAN论文
- IEEE Sensors Journal/Sensors Letters 有传感器漂移补偿论文
- Measurement 期刊有传感器标定和补偿论文

### 疑似重复

- 无高度疑似重复文献

### 明确排除

- 量子计算相关KAN论文（与时序建模不直接相关）
- 计算机视觉KAN应用（YOLOv10 with KAN等）

## 待核实事项

1. **DKD-KAN (R74)** - Knowledge-Distilled KAN for Intrusion Detection - arXiv:2603.03486 - 可能对边缘计算效率有参考价值
2. **FCDNet (R74)** - Frequency-Guided Complementary Dependency Modeling - arXiv:2312.16450 - 频域方法可能对频响补偿有参考
3. **HyperTime (R74)** - FFT-based loss for time series - arXiv:2208.05836 - 频域损失函数设计参考

## 对文档的影响

- 更新了 `raw_literature.md`：新增约32条文献线索
- 更新了 `literature_catalog.md`：新增第74轮索引和四个新论文分类表
- 是否需要更新 SUMMARY：否
- 是否需要后续 STEP2 分析：否（主要为新发现，待后续核实）

## 原始链接

### KAN网络 (12篇)
- https://doi.org/10.48550/arXiv.2603.23037
- https://doi.org/10.48550/arXiv.2603.21807
- https://doi.org/10.48550/arXiv.2603.20184
- https://doi.org/10.48550/arXiv.2603.16679
- https://doi.org/10.48550/arXiv.2603.15307
- https://doi.org/10.48550/arXiv.2603.15250
- https://doi.org/10.48550/arXiv.2603.15109
- https://doi.org/10.48550/arXiv.2603.13163
- https://doi.org/10.48550/arXiv.2603.03486
- https://doi.org/10.48550/arXiv.2603.02818
- https://doi.org/10.48550/arXiv.2603.00482

### 频域损失 (3篇)
- https://arxiv.org/abs/2312.16450
- https://arxiv.org/abs/2208.05836
- https://arxiv.org/abs/2509.17601

### 传感器漂移补偿 (6篇)
- 10.3390/s24041319
- 10.1109/JSEN.2024.3370539
- 10.1109/LSENS.2025.3591494
- https://arxiv.org/abs/2603.15281
- 10.1109/TIM.2024.3372211

### MEASUREMENT期刊 (11篇)
- 10.1016/j.measurement.2020.108019
- 10.1016/j.measurement.2025.118227
- 10.1016/j.measurement.2022.112044
- 10.1016/j.measurement.2022.110783
- 10.1016/j.measurement.2024.115510
- 10.1016/j.measurement.2024.114529
- 10.1016/j.measurement.2024.114812
- 10.1016/j.measurement.2020.107935
- 10.1016/j.measurement.2020.108938
- 10.1016/j.measurement.2024.115280
- 10.1016/j.measurement.2020.108776
