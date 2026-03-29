# 调研报告：第28轮文献调研

## 基本信息
- 日期：2026-03-28
- 阶段：STEP1 调研
- 覆盖范围：MEASUREMENT期刊待核实论文验证、IEEE Sensors新论文、PETSA频域损失、Wiener-Hammerstein新进展
- 是否使用子代理：是；4个并行方向

## 检索路径

### 子代理1：MEASUREMENT期刊待核实论文验证
- 关键词：传感器非线性补偿、传感器漂移、神经网络校准
- 主要数据库：ScienceDirect (Measurement期刊)
- 入口已定位：5篇待核实DOI全部验证完毕

### 子代理2：IEEE Sensors Journal 2024-2026
- 关键词：sensor nonlinearity compensation neural network, electrochemical sensor drift, MEMS calibration deep learning
- 主要数据库：IEEE Xplore, Semantic Scholar
- 入口已定位：3篇新论文

### 子代理3：PETSA频域损失与适配
- 关键词：frequency domain loss test-time adaptation, spectral loss time series
- 主要数据库：arXiv
- 入口已定位：PETSA (arXiv:2506.23424)

### 子代理4：Wiener-Hammerstein新进展
- 关键词：Wiener-Hammerstein system identification 2025, block oriented nonlinear system
- 主要数据库：arXiv, Google Scholar
- 入口已定位：大部分论文已在catalog中，新增Rodriguez-Linares等

## 发现结果

### 新增文献线索

#### MEASUREMENT期刊（Round 24待核实DOI验证完成）

| DOI | 论文 | 作者 | 年份 | 相关度 |
|-----|------|------|------|--------|
| 10.1016/j.measurement.2024.115510 | MEMS ASIC加速度传感器高g集成封装与校准 | Shi等 | 2025 | 高 |
| 10.1016/j.measurement.2025.119612 | 神经网络+多目标遗传算法优化自感应角度传感器结构 | Qiu等 | 2026 | 高 |
| 10.1016/j.measurement.2025.119291 | 风洞中可追溯空气温度校准 | Pachinger | 2026 | 中 |
| 10.1016/j.measurement.2025.118420 | 基于虚拟球约束的机器人无传感器运动学标定 | Zhang等 | 2025 | 低 |
| 10.1016/j.measurement.2025.119821 | GF-5-02/DPC传感器在轨相对辐射校准 | Tu等 | 2026 | 中 |

#### IEEE Sensors Journal新论文

| DOI | 论文 | 作者 | 年份 | 相关度 |
|-----|------|------|------|--------|
| 10.1109/JSEN.2024.3370539 | 干扰模型引导的神经网络用于航空磁补偿 | Xu等 | 2024 | 高 |
| 10.1109/JSEN.2024.3472291 | 用于低成本空气质量传感器校准的双路径深度学习模型 | Liu等 | 2024 | 高 |
| 10.1109/LSENS.2025.3591494 | 目标域无数据的模型无关元学习框架用于电子鼻时变漂移校正 | Gupta等 | 2025 | 高 |

#### 频域损失新论文

| arXiv ID | 论文 | 作者 | 年份 | 相关度 |
|----------|------|------|------|--------|
| 2506.23424 | PETSA: 参数高效测试时自适应 | Medeiros等 | 2025 | 高 |

#### Wiener-Hammerstein新增论文

| arXiv ID | 论文 | 作者 | 年份 | 相关度 |
|----------|------|------|------|--------|
| 2412.16210 | 低复杂度频率相关线性化器 | Rodriguez-Linares, Johansson | 2025 | 高 |

## 待核实事项

1. IEEE Sensors论文需要确认DOI是否已在catalog中
2. PETSA论文需要确认是否与现有频域损失论文重复

## 对文档的影响

- 更新文件：
  - `raw_literature.md` - 新增IEEE Sensors论文、PETSA、MEASUREMENT验证结果
  - `literature_catalog.md` - 新增验证后的MEASUREMENT论文
  - 本报告 - `STEP1_Round28_Research_Report.md`

- 是否需要后续 STEP2 分析：否（主要是核实和验证）

## 原始链接

- https://doi.org/10.1109/JSEN.2024.3370539
- https://doi.org/10.1109/JSEN.2024.3472291
- https://doi.org/10.1109/LSENS.2025.3591494
- https://doi.org/10.48550/arXiv.2506.23424
- https://doi.org/10.1016/j.measurement.2024.115510
- https://doi.org/10.1016/j.measurement.2025.119612
- https://doi.org/10.1016/j.measurement.2025.119291
- https://doi.org/10.1016/j.measurement.2025.118420
- https://doi.org/10.1016/j.measurement.2025.119821
