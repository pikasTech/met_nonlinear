# 调研报告：STEP1 Round 12 - 理论深度拓展

## 基本信息
- 日期：2026-03-28
- 阶段：STEP1 调研
- 覆盖范围：Kolmogorov-Arnold定理理论、Wiener模型基准测试、FreDF频域损失深度分析、Mamba/SSM时序模型、传感器数据集构建
- 是否使用子代理：是；并行4方向（KA定理理论、FreDF深度分析、非线性系统基准、Mamba SSM）+ 3方向（传感器补偿、数据集、Wiener地震应用）

## 检索路径

### 方向1：Kolmogorov-Arnold定理理论
- 关键词：Kolmogorov representation theorem, Barron universal approximation, B-spline neural network, KA theorem neural network
- 主要数据库：arXiv, Google Scholar
- 新发现：Original Kolmogorov 1957, Arnold 1957 papers referenced; Geometric KAN; KAN theoretical analysis

### 方向2：FreDF频域损失深度分析
- 关键词：FreDF, frequency enhanced direct forecast, Wang ICLR 2025, frequency domain loss formula
- 主要数据库：arXiv
- 发现：FreDF完整损失函数公式确认；与AFMAE对应关系明确

### 方向3：非线性系统识别基准
- 关键词：nonlinear system identification benchmark, Wiener-Hammerstein, Schoukens group, block-oriented systems
- 主要数据库：IEEE Xplore, arXiv, Google Scholar
- 发现：NOISE benchmark未找到具体文献；Barron-Wiener-Laguerre (2026)是重大发现

### 方向4：Mamba状态空间模型
- 关键词：Mamba time series, S4 state space, Mamba vs KAN, SSM sensor
- 主要数据库：arXiv
- 发现：Fourier-KAN-Mamba, ss-Mamba, S-Mamba等KANN+SSM混合架构

### 方向5：传感器数据集
- 关键词：sensor dataset benchmark, electrochemical sensor dataset, seismic dataset, MEMS dataset
- 主要数据库：arXiv, Zenodo, IEEE Xplore
- 发现：OpenFWI, SWAN, NanoBench, Nanodrone-SysID等数据集

### 方向6：传感器非线性补偿
- 关键词：sensor nonlinearity compensation, polynomial correction, temperature compensation, LUT calibration
- 主要数据库：IEEE Xplore, MDPI Sensors
- 发现：多项IEEE Sensors相关论文；Xu & Wang 2008是Verified状态

### 方向7：Wiener地震计应用
- 关键词：Wiener model seismic, seismometer nonlinear, accelerometer calibration, Volterra seismic
- 主要数据库：IEEE Xplore, Google Scholar
- 发现：待核实具体论文

## 发现结果

### 新增文献线索（P0 高相关性）

| 作者 | 年份 | 标题 | DOI/链接 | 分类 | 相关性 | 状态 |
|------|------|------|----------|------|--------|------|
| Manavalan, Tronarp | 2026 | Barron-Wiener-Laguerre | arXiv:2602.13098 | P0 | High | New |
| Alesiani et al. | 2025 | Geometric Kolmogorov-Arnold Superposition Theorem | arXiv:2502.16664 | P0 | High | New |
| Jiao et al. | 2025 | Transformers Can Overcome CoD | arXiv:2504.13558 | P0 | Medium | New |
| Wang et al. | 2025 | FreDF: Frequency-enhanced Direct Forecast (ICLR 2025) | arXiv:2402.02399 | P0 | High | Confirmed |
| Puig et al. | 2025 | TKAN: Temporal KAN | arXiv:2405.07344 | P0 | High | Already in catalog |
| Gleyzer et al. | 2025 | Sinusoidal Approximation Theorem for KANs | arXiv:2508.00247 | P0 | Medium | New |
| Freedman, Mulligan | 2025 | Spontaneous KA Geometry in Shallow MLPs | arXiv:2509.12326 | P0 | Medium | New |
| Noorizadegan et al. | 2025 | Practitioner's Guide to KAN | arXiv:2510.25781 | P0 | High | New |
| Liu, Chatzi, Lai | 2025 | Rate of Convergence of KAN | arXiv:2509.19830 | P0 | High | New |
| Toscano et al. | 2024 | KKANs: Kurkova-KAN Networks | arXiv:2412.16738 | P0 | High | New |
| Wang et al. | 2024 | On Expressiveness of KANs | arXiv:2410.01803 | P0 | High | New |
| Zhang | 2025 | PolyKAN: Provable KAN Compression | arXiv:2510.04205 | P1 | Medium | New |

### Mamba/SSM新文献

| 作者 | 年份 | 标题 | DOI/链接 | 分类 | 相关性 | 状态 |
|------|------|------|----------|------|--------|------|
| Wang et al. | 2025 | Fourier-KAN-Mamba | arXiv:2511.15083 | P1 | High | New |
| Ye | 2025 | ss-Mamba: Spline+KAN+Mamba | arXiv:2506.14802 | P1 | High | New |
| Peng et al. | 2024 | Mamba or Transformer? MoU | arXiv:2408.15997 | P1 | Medium | New |
| Wang et al. | 2024 | Is Mamba Effective? S-Mamba | arXiv:2403.11144 | P1 | Medium | New |
| Fan et al. | 2025 | DC-Mamber: Mamba+LinearTransformer | arXiv:2507.04381 | P1 | Medium | New |
| Somvanshi et al. | 2025 | From S4 to Mamba Survey | arXiv:2503.18970 | P1 | High | New |
| Patro, Agneeswaran | 2024 | Mamba-360 Survey | arXiv:2404.16112 | P1 | High | New |
| Zhang, Li | 2025 | ASSM: Adaptive State-Space Mamba | arXiv:2503.22743 | P2 | Medium | New |
| Shihab et al. | 2025 | Efficient Unstructured Pruning of Mamba | arXiv:2505.08299 | P2 | Medium | New |

### 传感器数据集新文献

| 作者 | 年份 | 标题 | DOI/链接 | 分类 | 相关性 | 状态 |
|------|------|------|----------|------|--------|------|
| Deng et al. | 2022 | OpenFWI: Seismic FWI Benchmark | arXiv:2111.02926 | P2 | High | Already in catalog |
| Gong et al. | 2026 | SWAN: Seismic Waveforms Dataset | arXiv:2603.13645 | P2 | High | New |
| Iacob et al. | 2025 | Learning Koopman Models (Schoukens group) | arXiv:2507.09646 | P2 | High | New |
| Hoekstra et al. | 2026 | Learning-based Augmentation LFR (Schoukens) | arXiv:2602.17297 | P2 | High | New |
| Peng et al. | 2025 | S4M: S4 for Multivariate Time Series | arXiv:2503.00900 | P2 | Medium | New |
| Behrouz et al. | 2024 | Chimera: 2D SSM Mamba-2 | arXiv:2406.04320 | P2 | Medium | New |
| Janssen et al. | 2025 | Benchmarking M-LTSF | arXiv:2510.04900 | P2 | Medium | New |

### 传感器补偿传统方法

| 作者 | 年份 | 标题 | DOI/链接 | 分类 | 相关性 | 状态 |
|------|------|------|----------|------|--------|------|
| Xu, Wang | 2008 | Volterra series for sensor block models | 10.1016/j.measurement.2008.03.003 | P2 | High | Verified |
| Iqbal | 2024 | Volterra System Analysis Electrochemical Sensor | MIT DSpace | P2 | High | Verified |
| Popoola et al. | 2016 | Baseline-temperature correction electrochemical | 10.1016/j.atmosenv.2016.01.001 | P2 | High | Verified |

### 疑似重复/待核实
- Schoukens group论文已有多篇，需确认是否有新增基准数据集论文
- NOISE benchmark未找到具体文献

### 明确排除
- NOISE benchmark：具体文献未定位

## 待核实事项

1. **Barron-Wiener-Laguerre (Manavalan 2026)** - 需要获取全文，理论连接最强
2. **Geometric KAN (Alesiani 2025)** - 与物理系统建模的理论连接
3. **FreDF损失函数公式细节** - 已确认公式结构，需要验证α参数选取
4. **NOISE benchmark** - 无法找到具体文献，可能是非正式基准
5. **Wiener地震计应用** - 需要进一步搜索IEEE TGRS等期刊
6. **Nanodrone-SysID** - 非线性系统识别的nano无人机数据集，可能有参考价值

## 对文档的影响

- 更新文件：literature_catalog.md, raw_literature.md
- 需要后续STEP2分析：
  - FreDF损失函数详细分析
  - Barron-Wiener-Laguerre理论框架
  - Mamba+KAN混合架构的效率分析
- 是否需要更新SUMMARY：否

## 原始链接

- https://arxiv.org/abs/2602.13098 (Barron-Wiener-Laguerre)
- https://arxiv.org/abs/2502.16664 (Geometric KAN)
- https://arxiv.org/abs/2402.02399 (FreDF)
- https://arxiv.org/abs/2511.15083 (Fourier-KAN-Mamba)
- https://arxiv.org/abs/2503.18970 (S4 to Mamba Survey)
- https://arxiv.org/abs/2603.13645 (SWAN Seismic Dataset)
- https://arxiv.org/abs/2507.09646 (Koopman Models Schoukens)
- https://arxiv.org/abs/2602.17297 (LFR Augmentation Schoukens)
