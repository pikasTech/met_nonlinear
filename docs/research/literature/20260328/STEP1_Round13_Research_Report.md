# 调研报告：STEP1 Round 13 - Wiener-KAN架构、传感器补偿与B-spline效率

## 基本信息
- 日期：2026-03-28
- 阶段：STEP1 调研
- 覆盖范围：Wiener-KAN混合架构、传感器前馈补偿、B-spline KAN训练效率、电化学/地震传感器建模
- 是否使用子代理：是；并行4方向（Wiener-KAN混合、前馈补偿、B-spline效率、传感器建模）

## 检索路径

### 方向1：Wiener-KAN混合架构
- 关键词：Wiener KAN, block-oriented KAN, Hammerstein KAN, Wiener-Hammerstein neural network, SS-KAN
- 主要数据库：arXiv, IEEE Xplore, Google Scholar
- 新发现：SS-KAN (Cruz 2025) 是最接近Wiener-KAN的论文，在Wiener-Hammerstein基准上验证

### 方向2：传感器前馈补偿架构
- 关键词：feedforward compensation sensor, neural network sensor drift, forward compensation nonlinear
- 主要数据库：IEEE Xplore, ScienceDirect, Google Scholar, MDPI Sensors
- 新发现：FRIKAN是直接针对MET电化学地震计的前馈补偿论文

### 方向3：B-spline KAN训练效率
- 关键词：B-spline KAN, spline network training, KAN convergence, LUT KAN
- 主要数据库：arXiv, IEEE Xplore
- 新发现：KANtize论文显示B-spline评估占推理时间的98%；LUT-KAN实现12x CPU加速

### 方向4：电化学/地震传感器建模
- 关键词：electrochemical sensor nonlinear model, seismometer calibration, Wiener sensor
- 主要数据库：arXiv, IEEE Xplore, ScienceDirect
- 新发现：Wiener-Hammerstein模型用于传感器化驱动的执行器；Volterra级数估计

## 发现结果

### 新增文献线索（Wiener-KAN混合架构）

| 作者 | 年份 | 标题 | DOI/链接 | 分类 | 相关性 | 状态 |
|------|------|------|----------|------|--------|------|
| Cruz et al. | 2025 | SS-KAN: State-Space KAN for Wiener-Hammerstein | arXiv:2506.16392 | P0 | High | Already verified |
| Liu et al. | 2025 | SKANODEs: Structured KAN Neural ODEs | arXiv:2506.18339 | P0 | High | New |
| Gashi et al. | 2025 | KAN for Buck Converters System ID | arXiv:2506.10434 | P1 | Medium | New |
| Shuai, Li | 2024 | PIKAN: Physics-Informed KAN for Power Systems | arXiv:2408.06650 | P1 | Medium | New |
| Howard et al. | 2026 | SINDy-KANs: Sparse Nonlinear Dynamics | arXiv:2603.18548 | P1 | Medium | New |
| Shen et al. | 2025 | Lyapunov-Based KAN Adaptive Control | arXiv:2512.21437 | P1 | Medium | New |

### 新增文献线索（传感器补偿）

| 作者 | 年份 | 标题 | DOI/链接 | 分类 | 相关性 | 状态 |
|------|------|------|----------|------|--------|------|
| Li et al. (FRIKAN) | 2025 | Feedforward Compensation Network with Frequency Response Prior Injection and Physics-Constrained KAN | TIM-25-06440 | P0 | Very High | Already verified |
| Silva et al. | 2024 | REDOX Reactions Memory Traces | arXiv:2409.07299 | P1 | High | New |
| Willemstein et al. | 2023 | Wiener-Hammerstein for Piezoresistive Sensors | arXiv:2302.13141 | P1 | High | New |
| Badawi et al. | 2021 | TCNN for Chemical Sensor Drift | IEEE 9442748 | P1 | High | Pending |
| Shi et al. | 2022 | EEMD-GRNN for MEMS Sensor Drift | MDPI Sensors | P1 | High | Pending |

### 新增文献线索（B-spline KAN效率）

| 作者 | 年份 | 标题 | DOI/链接 | 分类 | 相关性 | 状态 |
|------|------|------|----------|------|--------|------|
| Liu et al. | 2025 | Rate of Convergence of KAN (minimax-optimal O(n^(-2r/(2r+1)))) | arXiv:2509.19830 | P0 | High | Already in catalog |
| Wang et al. | 2024 | Expressiveness and Spectral Bias of KANs | arXiv:2410.01803 | P0 | High | Already in catalog |
| Errabii et al. | 2026 | KANtize: Low-bit Quantization (50x BitOps reduction) | arXiv:2603.17230 | P1 | High | Already in catalog |
| Kuznetsov | 2026 | LUT-KAN: 12x CPU inference speedup | arXiv:2601.03332 | P1 | High | Already in catalog |
| Kuznetsov | 2026 | LUT-Compiled KAN for IoT: 5000x speedup | arXiv:2601.08044 | P1 | High | Already in catalog |
| Noorizadegan et al. | 2025 | Practitioner's Guide to KAN | arXiv:2510.25781 | P0 | High | Already in catalog |
| Toscano et al. | 2024 | KKANs: Kurkova-KAN Networks | arXiv:2412.16738 | P0 | High | Already in catalog |

### 新增文献线索（电化学/地震传感器基准）

| 作者 | 年份 | 标题 | DOI/链接 | 分类 | 相关性 | 状态 |
|------|------|------|----------|------|--------|------|
| Champneys et al. | 2024 | Baseline Results for Nonlinear System ID Benchmarks | arXiv:2405.10779 | P1 | High | New |
| Birpoutsoukis et al. | 2018 | Efficient Volterra Series Estimation | arXiv:1804.10026 | P1 | High | New |
| Busetto et al. | 2025 | Nonlinear System ID Nano-drone Benchmark | arXiv:2512.14450 | P2 | Medium | New |
| Ullah, Baca | 2026 | NanoBench: Nano-Quadrotor Benchmark | arXiv:2603.09908 | P2 | Medium | New |
| Beintema et al. | 2020 | Deep Encoder Networks for Wiener-Hammerstein | arXiv:2012.07697 | P1 | Medium | Already in catalog |

### 入口已定位

1. SS-KAN (Cruz 2025) - 最接近Wiener-KAN的论文，验证于Wiener-Hammerstein基准
2. FRIKAN (Li 2025) - 直接针对MET电化学地震计的前馈补偿
3. KANtize (Errabii 2026) - B-spline量化，98%推理时间用于B-spline评估
4. LUT-KAN (Kuznetsov 2026) - 12x CPU加速，5000x边缘设备加速

### 疑似重复/待核实

1. SKANODEs (Liu 2025) 与SS-KAN (Cruz 2025) 都提出结构化KAN用于动力学系统，需核实差异
2. PIKAN (Shuai 2024) 与FRIKAN (Li 2025) 都提到物理信息KAN，需确认是否同一工作
3. Nano-drone benchmark与Nanodrone-SysID疑似重复

### 明确排除

1. 无明确排除

## 待核实事项

1. **SKANODEs vs SS-KAN差异** - 需要获取全文对比两者方法论
2. **FRIKAN vs PIKAN关系** - 确认是否为同一工作的不同版本
3. **NanoBench vs Nanodrone-SysID** - 确认是否为同一数据集的不同表述
4. **Wiener-KAN架构设计** - 尚未有论文明确定义Wiener-KAN架构，这是论文的创新空间

## 对文档的影响

- 更新文件：raw_literature.md, literature_catalog.md
- 新增SKANODEs, SINDy-KANs, NanoBench, Baseline Results for Benchmarks等条目
- 是否需要更新SUMMARY：否
- 是否需要后续STEP2分析：
  - Wiener-KAN架构设计空间分析
  - FRIKAN与PIKAN的关系确认

## 原始链接

- https://arxiv.org/abs/2506.18339 (SKANODEs)
- https://arxiv.org/abs/2506.10434 (KAN for Buck Converters)
- https://arxiv.org/abs/2408.06650 (PIKAN)
- https://arxiv.org/abs/2603.18548 (SINDy-KANs)
- https://arxiv.org/abs/2302.13141 (Wiener-Hammerstein Sensors)
- https://arxiv.org/abs/1804.10026 (Volterra Series Estimation)
- https://arxiv.org/abs/2405.10779 (Nonlinear Benchmarks)
- https://arxiv.org/abs/2512.14450 (Nano-drone Benchmark)
- https://arxiv.org/abs/2603.09908 (NanoBench)
