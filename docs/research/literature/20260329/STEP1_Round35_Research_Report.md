# 调研报告：第35轮文献调研

## 基本信息
- 日期：2026-03-29
- 阶段：STEP1 调研
- 覆盖范围：KAN最新进展、传感器漂移补偿、MEASUREMENT期刊论文扩充
- 是否使用子代理：是（并行3方向检索）

## 检索路径

### 子代理1：KAN网络最新进展
- 关键词：KAN, Kolmogorov-Arnold Networks, time series, sensor, efficiency
- 主要数据库：arXiv
- 检索式：KAN标题/摘要搜索（2025-2026）

### 子代理2：传感器漂移补偿深度学习方法
- 关键词：sensor drift compensation, deep learning, MEMS, inertial, electrochemical
- 主要数据库：arXiv, IEEE Xplore
- 检索式：传感器漂移+深度学习组合

### 子代理3：MEASUREMENT期刊论文
- 关键词：sensor nonlinearity, temperature compensation, calibration, neural network
- 主要数据库：Measurement期刊, Crossref, Google Scholar
- 目标：扩充至50篇（当前约15篇）

## 发现结果

### 新增KAN论文（2026年arXiv）

| 论文 | 作者 | 年份 | arXiv ID | 关键贡献 | 分类 |
|------|------|------|----------|----------|------|
| Symbolic-KAN | Faroughi et al. | 2026 | 2603.23854 | 符号结构嵌入KAN可解释学习 | 理论 |
| SINDy-KANs | Howard et al. | 2026 | 2603.18548 | KAN+稀疏非线性动力学辨识 | 理论 |
| KaCGM | Almodóvar et al. | 2026 | 2603.20184 | 因果生成模型，混合型表格数据 | 理论 |
| Many-body Mobility | Dai et al. | 2026 | 2603.21807 | 物理信息KAN用于多体局域化 | 理论 |
| In-Context SINDy-KAN | Sovrano et al. | 2026 | 2603.15250 | 鲁棒符号回归提取 | 优化 |

### 新增传感器漂移补偿论文

| 论文 | 作者 | 年份 | DOI/URL | 方法 | 应用 |
|------|------|------|---------|------|------|
| GNIO | Feng et al. | 2026 | 2603.15281 | 门控神经网络+运动银行 | MEMS IMU，60.21%漂移减少 |
| TE-PINN | Golroudbari | 2024 | 2409.16214 | Transformer+物理信息NN | 陀螺仪方向/偏置估计 |
| EqNIO | Jayanth et al. | 2024 | 2408.06321 | 等变神经网络 | IMU位移估计 |
| DCT-CNN | Badawi et al. | 2020 | 2011.06681 | 离散余弦变换CNN | 化学传感器漂移 |
| DIDO | Zhang et al. | 2022 | 2203.03149 | 级联网络+两阶段EKF | 四旋翼状态估计 |
| TLIO | Liu et al. | 2020 | 10.1109/LRA.2020.3007421 | 网络回归3D位移+不确定度 | IMU无状态估计 |
| milliEgo | Lu et al. | 2020 | 2006.02266 | 深度传感器融合+注意力 | 自我运动估计，1.3%漂移 |
| Neuromorphic Olfaction | Kausar et al. | 2024 | 2407.04714 | 脉冲神经网络+贝叶斯网络 | 电子鼻漂移补偿 |

### 新增MEASUREMENT期刊论文

| 论文 | 作者 | 年份 | DOI | 主题 |
|------|------|------|-----|------|
| AutoML for multi-class anomaly compensation | Schaller, Kruse | 2025 | 10.1016/j.measurement.2025.117097 | 传感器漂移自动补偿 |
| TPoS micromachined gas sensor nonlinearity | Fang et al. | 2025 | 10.1016/j.measurement.2024.116559 | 非线性利用提高灵敏度 |
| Neural network hysteresis operators | Krikelis et al. | 2024 | 10.1016/j.measurement.2023.113966 | 磁滞系统神经网络辨识 |
| Augmented DIC vibration measurement | Neri | 2024 | 10.1016/j.measurement.2024.114565 | 神经网络增强DIC振动测量 |
| Volterra kernels damage detection | Li et al. | 2025 | - | Volterra核用于结构损伤检测 |
| Aeromagnetic compensation Volterra | Zhang et al. | 2026 | - | 稀疏剪枝Volterra系列 |

## 待核实事项

1. **Symbolic-KAN (2603.23854)** - 需核实是否与已有PIKAN等冲突
2. **KaCGM (2603.20184)** - 因果生成模型，需评估与Wiener模型联系
3. **GNIO (2603.15281)** - IMU漂移减少60.21%，高相关性
4. **TE-PINN (2409.16214)** - Transformer用于传感器偏置估计
5. **DCT-CNN (2011.06681)** - 化学传感器漂移，与TDACNN可比较

## 疑似重复/排除

- KANtize (2603.17230) - 已在catalog中为R21新增
- TimeKAN, TFKAN, KANMixer等 - 已在catalog中
- P-KAN, AR-KAN - 已在catalog中

## 对文档的影响

- 更新 `raw_literature.md`：
  - KAN新理论论文：Symbolic-KAN, SINDy-KANs, KaCGM
  - 传感器漂移补偿：DCT-CNN, TLIO, milliEgo, Neuromorphic Olfaction
  - MEASUREMENT期刊：Schaller 2025, Fang 2025, Krikelis 2024
- 更新 `literature_catalog.md`：
  - 新增"R35 KAN理论进展"小节
  - 更新"综述报告索引"

## 原始链接

- https://arxiv.org/abs/2603.23854 (Symbolic-KAN)
- https://arxiv.org/abs/2603.18548 (SINDy-KANs)
- https://arxiv.org/abs/2603.20184 (KaCGM)
- https://arxiv.org/abs/2603.15281 (GNIO)
- https://arxiv.org/abs/2011.06681 (DCT-CNN)
- https://arxiv.org/abs/2407.04714 (Neuromorphic Olfaction)
- https://doi.org/10.1016/j.measurement.2025.117097 (Schaller 2025)

## 产出文件

- `docs/research/literature/20260329/STEP1_Round35_Research_Report.md` (本文件)
- 更新 `docs/research/literature/raw_literature.md`
- 更新 `docs/research/literature/literature_catalog.md`