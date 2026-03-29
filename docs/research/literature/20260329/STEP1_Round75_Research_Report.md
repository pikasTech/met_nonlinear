# 调研报告：STEP1 Round75 文献调研

## 基本信息
- 日期：2026-03-29
- 阶段：STEP1 调研
- 覆盖范围：Wiener-KAN混合架构、传感器非线性补偿、MEASUREMENT期刊扩充
- 是否使用子代理：是；**三路并行搜索**

## 检索路径

### 子代理 1：MEASUREMENT期刊传感器论文搜索
- 关键词：sensor nonlinearity compensation, temperature drift, accelerometer calibration, neural network sensor calibration
- 主要数据库：ScienceDirect (Measurement期刊)
- 新发现数据库：CrossRef, OpenAlex
- 检索式：site:sciencedirect.com "sensor nonlinearity" measurement (2020-2026)

### 子代理 2：Wiener-KAN混合架构搜索
- 关键词：Wiener KAN, state-space KAN, temporal KAN, TKAN, functional Wiener filter
- 主要数据库：arXiv
- 新发现数据库：无
- 检索式：site:arxiv.org "Wiener" "KAN" OR "Kolmogorov-Arnold" (2024-2026)

### 子代理 3：传感器非线性补偿搜索
- 关键词：sensor nonlinearity calibration, MEMS accelerometer, deep learning compensation, drift compensation
- 主要数据库：arXiv, IEEE Xplore, Sensors (MDPI)
- 新发现数据库：Results in Engineering
- 检索式：site:arxiv.org "sensor drift" "compensation" neural network

## 发现结果

### 新增文献线索

| 类别 | 数量 | 备注 |
|------|------|------|
| Wiener-KAN混合架构 | 6篇 | Functional Wiener Filter、WormKAN等 |
| 传感器非线性补偿 | 8篇 | 涵盖惯性导航、气体传感器、热稳定 |
| MEASUREMENT期刊 | 7篇 | 温度补偿、加速度计标定、传感器融合 |

### 入口已定位

- arXiv cs.LG, stat.ML 持续有新Wiener-KAN混合论文
- Measurement 期刊有大量传感器标定和补偿论文
- Results in Engineering 有惯性导航深度学习综述

### 疑似重复

- 无高度疑似重复文献

### 明确排除

- 量子计算相关KAN论文（与时序建模不直接相关）
- 计算机视觉KAN应用（YOLOv10 with KAN等）

## 待核实事项

1. **Colburn 2024 (R75)** - Functional Wiener Filter - 可能对Wiener与神经网络闭合解有重要理论价值
2. **Kuang, Lin 2025 (R75)** - Assumed Density Filtering - 神经网络代理模型的贝叶斯滤波
3. **Iafolla 2024 (R75)** - 加速度计温度补偿的ML方法 - Measurement期刊

## 对文档的影响

- 更新了 `raw_literature.md`：新增约21条文献线索
- 更新了 `literature_catalog.md`：新增Round75索引和三个分类表
- 是否需要更新 SUMMARY：否
- 是否需要后续 STEP2 分析：否（主要为新发现，待后续核实）

## 原始链接

### Wiener-KAN混合架构 (6篇)
- https://arxiv.org/abs/2402.03497 (Colburn 2024 - Functional Wiener Filter)
- https://arxiv.org/abs/2511.09016 (Kuang, Lin 2025)
- https://arxiv.org/abs/2504.04450 (Bai et al. 2025)
- https://arxiv.org/abs/2410.10041 (Xu et al. 2024 - WormKAN)
- https://arxiv.org/abs/2601.09811 (Vasilyeva et al. 2026)
- https://arxiv.org/abs/2509.09145 (Mallick et al. 2025)

### 传感器非线性补偿 (8篇)
- https://arxiv.org/abs/2601.19047 (Sakamoto 2026)
- 10.1016/j.measurement.2023.114090 (Iafolla et al. 2024)
- https://arxiv.org/abs/2511.13071 (Levin, Klein 2025)
- 10.1016/j.rineng.2024.103565 (Cohen, Klein 2023)
- https://arxiv.org/abs/2011.06681 (Badawi et al. 2020)
- 10.1016/j.snb.2022.131739 (Zhang et al. 2022)
- https://arxiv.org/abs/2505.20769 (Shi et al. 2025)
- https://arxiv.org/abs/2506.04539 (France et al. 2025)

### MEASUREMENT期刊 (7篇)
- 10.1016/j.measurement.2020.107963
- 10.1016/j.measurement.2022.112387
- 10.1016/j.measurement.2025.117097
- 10.1016/j.measurement.2023.114001
- 10.1016/j.measurement.2020.107958
- 10.1016/j.measurement.2022.111543
- 10.1016/j.measurement.2026.121339
