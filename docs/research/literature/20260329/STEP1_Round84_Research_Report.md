# 调研报告：STEP1 Round84 - 传感器标定与非线性补偿文献

## 基本信息
- 日期：2026-03-29
- 阶段：STEP1 调研
- 覆盖范围：传感器标定、非线性补偿、温度漂移、神经网络补偿
- 是否使用子代理：否

## 检索路径
- 关键词：
  - sensor nonlinearity compensation measurement
  - temperature drift sensor compensation neural network
  - Wiener Hammerstein system identification neural
  - sensor calibration neural network
- 主要数据库：arXiv, ScienceDirect (Measurement journal)
- 新发现数据库：arXiv
- 检索式：
  - "sensor nonlinearity compensation" + "measurement"
  - "temperature drift" + "sensor" + "compensation"
  - "self-calibrating" + "Hall sensor"

## 发现结果

### 新增文献线索

| 作者 | 年份 | 标题 | 链接 | 类别 | 相关度 | 状态 |
|------|------|-------|------|-----|-----|--------|
| Kim, Ham, Kim | 2026 | Compact Optical Single-axis Joint Torque Sensor Using Redundant Photo-Reflectors and Quadratic-Programming Calibration | https://arxiv.org/abs/2603.16040 | P2 | 高 | 新增 (R84) |
| van Meer et al. | 2025 | Self-Calibrating Position Measurements: Applied to Imperfect Hall Sensors | https://arxiv.org/abs/2505.04245 | P1 | 高 | 新增 (R84) |
| Voit, Enzner | 2024 | Multiplant Nonlinear System Identification by Block-Structured Multikernel Neural Networks | https://arxiv.org/abs/2412.07370 | P0 | 高 | 新增 (R84) |
| Niu et al. | 2022 | Deep Transfer Learning for System Identification Using LSTM | https://arxiv.org/abs/2204.03125 | P1 | 高 | 新增 (R84) |
| Revay, Wang, Manchester | 2021 | Recurrent Equilibrium Networks: Flexible Dynamic Models with Guaranteed Stability | https://arxiv.org/abs/2104.05942 | P0 | 高 | 已存在 (R7) |
| Zhang, Zhang | 2015 | Domain Adaptation ELM for Drift Compensation in E-nose Systems | https://doi.org/10.1109/TIM.2014.2367775 | P1 | 高 | 已存在 (R7) |

### 新增论文核心信息

#### 1. Kim et al. 2026 - Joint Torque Sensor with Temperature Compensation
- **核心发现**：
  - 光学扭矩传感器，使用冗余光电反射器阵列
  - 二次规划标定方法（QP calibration）
  - **温度漂移补偿**：使用rational fitting based compensation
  - 温度室表征 + rational fitting补偿零漂
  - 最大误差0.083%FS，RMS误差0.0266 Nm
- **与论文相关性**：
  - 直接证明了传感器温度漂移可以用数据驱动方法（rational fitting）补偿
  - 为MET传感器温度漂移补偿提供参考

#### 2. van Meer et al. 2025 - Self-Calibrating Hall Sensors
- **核心发现**：
  - 线性Hall传感器自标定方法
  - 闭环数据采集 + 非线性辨识
  - 在线补偿，无需外部编码器
  - RMS误差降低2.6倍
- **与论文相关性**：
  - 自标定方法可用于传感器非线性补偿
  - 数据驱动标定流程参考

#### 3. Voit, Enzner 2024 - Multikernel Neural Networks for Wiener-Hammerstein
- **核心发现**：
  - 块结构多核神经网络用于非线性系统辨识
  - 共享权重 + 特定权重分离
  - 可处理多个不同测量的数据
- **与论文相关性**：
  - 直接关联Wiener-Hammerstein系统辨识
  - 多核方法与KAN的B-spline基函数有相似性

#### 4. Niu et al. 2022 - LSTM for Wiener-Hammerstein
- **核心发现**：
  - 深度迁移学习用于系统辨识
  - 参数微调 + 冻结两种迁移方法
  - 加速学习10%-50%
  - 应用到Wiener-Hammerstein非线性系统
- **与论文相关性**：
  - LSTM用于Wiener-Hammerstein的证据
  - 迁移学习减少数据需求

### 入口已定位
- arXiv搜索正常运作
- ScienceDirect Measurement期刊需登录访问

### 疑似重复/已存在
- Revay et al. 2021 - 已在R7记录为Verified
- Zhang et al. 2015 (DAELM) - 已在R7记录

### 明确排除
- 视觉SLAM类论文（与传感器漂移主题部分相关但不直接）

## 待核实事项
- Voit, Enzner 2024论文中的多核方法与KAN的关系
- 这些新论文是否已收录在literature_catalog.md中

## 对文档的影响
- 更新了哪些文件：raw_literature.md, literature_catalog.md
- 是否需要更新SUMMARY：否
- 是否需要后续STEP2分析：否（基础调研）

## 原始链接
- https://arxiv.org/abs/2603.16040 (Kim 2026)
- https://arxiv.org/abs/2505.04245 (van Meer 2025)
- https://arxiv.org/abs/2412.07370 (Voit 2024)
- https://arxiv.org/abs/2204.03125 (Niu 2022)
- https://arxiv.org/abs/2104.05942 (Revay 2021)
- https://doi.org/10.1109/TIM.2014.2367775 (Zhang 2015)
