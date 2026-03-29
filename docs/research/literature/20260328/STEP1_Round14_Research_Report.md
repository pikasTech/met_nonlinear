# 调研报告：STEP1 Round 14 - Wiener-KAN架构综合检索

## 基本信息
- 日期：2026-03-28
- 阶段：STEP1 调研
- 覆盖范围：Wiener模型传感器应用、频域损失函数理论、KEN架构效率对比、测量方法论
- 是否使用子代理：是；并行4方向（Wiener+传感器补偿、频域损失、KEN vs RNN效率、测量方法）

## 检索路径

### 方向1：Wiener模型+传感器补偿
- 关键词：Wiener model sensor, Wiener system electrochemical, feedforward compensation sensor
- 主要数据库：arXiv, IEEE Xplore, Google Scholar
- 新发现：Wiener模型用于传感器补偿有多个应用案例（Willemstein 2023/2024, Bo Wahlberg理论）

### 方向2：频域损失函数
- 关键词：frequency domain loss time series, spectral loss, AFMAE, FFT loss
- 主要数据库：arXiv, IEEE Xplore
- 新发现：FIRE (He 2025) 统一FFT域损失框架；FreDF提供AFMAE直接公式

### 方向3：KEN vs RNN/LSTM效率对比
- 关键词：KAN vs LSTM, KAN computational efficiency, RNN efficiency
- 主要数据库：arXiv, IEEE Xplore
- 新发现：KAN-AD显示<1000参数、50%推理加速；Gaonkar 2026显示KEN vs MLP效率优势

### 方向4：MET测量方法论
- 关键词：MET measurement, sensor calibration, frequency response measurement
- 主要数据库：IEEE Xplore, Measurement期刊
- 新发现：Xu & Wang 2008已覆盖；Schoukens 2017基准数据集可参考

## 发现结果

### 新增文献线索（Wiener模型+传感器应用）

| 作者 | 年份 | 标题 | DOI/链接 | 分类 | 相关性 | 状态 |
|------|------|------|----------|------|--------|------|
| Willemstein et al. | 2024 | Soft insoles for estimating 3D ground reaction forces | arXiv:2303.04719 | P1 | High | New |
| Bo Wahlberg et al. | 2015 | Identification of Stochastic Wiener Systems using Indirect Inference | arXiv:1507.05535 | P0 | High | New |
| Bo Wahlberg et al. | 2018 | Algorithms and Performance Analysis for Stochastic Wiener System Identification | arXiv:1805.09102 | P0 | High | New |
| Puyu Wang et al. | 2026 | Optimization, Generalization and DP Bounds for GD on KANs | arXiv:2601.22409 | P0 | High | New |
| Bayeh et al. | 2026 | TruKAN: Truncated Power Functions | arXiv:2602.03879 | P1 | Medium | New |
| Kausar et al. | 2024 | Efficient Hybrid Neuromorphic-Bayesian Model for Olfaction | arXiv:2407.04714 | P1 | Medium | New |
| Aigner & Stöckl | 2023 | ML Compensation for Knitted Force Sensors | arXiv:2306.12129 | P1 | Medium | New |
| Jiang et al. | 2025 | FiberKAN: KAN for Nonlinear Fiber Optics | arXiv:2504.18833 | P1 | Medium | New |
| Abdolazizi et al. | 2025 | CKANs: Constitutive KANs | arXiv:2502.05682 | P1 | Medium | New |
| Nehma & Tiwari | 2024 | KANs for Deep Koopman Operator Discovery | arXiv:2406.02875 | P1 | Medium | New |

### 新增文献线索（频域损失函数）

| 作者 | 年份 | 标题 | DOI/链接 | 分类 | 相关性 | 状态 |
|------|------|------|----------|------|--------|------|
| He et al. | 2025 | FIRE: Unified FFT-Domain Loss Framework | arXiv:2510.10145 | P0 | High | Already Pending |

### 新增文献线索（KEN vs RNN效率）

| 作者 | 年份 | 标题 | DOI/链接 | 分类 | 相关性 | 状态 |
|------|------|------|----------|------|--------|------|
| Dong et al. | 2024 | KAN for Time Series Classification | arXiv:2408.07314 | P0 | High | New |
| KAN-AD | 2025 | Time Series Anomaly Detection with KAN | arXiv:2411.00278 | P1 | High | New |
| Barašin et al. | 2025 | KAN for Interpretable TS Classification | arXiv:2411.14904 | P0 | Medium | New |
| SpectralKAN | 2024 | Weighted Activation Distribution KAN | arXiv:2407.00949 | P1 | Medium | New |
| KA-GNN | 2024 | KAN Graph Neural Networks | arXiv:2410.11323 | P1 | Medium | New |
| Cohen et al. | 2025 | Toto: TS Foundation Model | arXiv:2505.14766 | P1 | Medium | New |

### 入口已定位

1. **FreDF (Wang 2025)** - AFMAE直接公式：L^α = α·|F(Ŷ)-F(Y)|₁ + (1-α)·MSE
2. **FIRE (He 2025)** - 统一FFT域损失框架
3. **KAN-AD (2025)** - <1000参数，50%推理加速
4. **Gaonkar 2026** - KEN vs MLP效率：精度更高+FLOPs更少

### 疑似重复/待核实

1. **Willemstein 2023/2024** - 同一团队同一方法，需确认是否同一数据集
2. **Bo Wahlberg 2015/2018** - 同一主题的延续研究，后者有更详细的CRLB分析
3. **Noorizadegan** - 2025/2026两个版本，可能是修订版

### 明确排除

1. 无明确排除

## 待核实事项

1. **Wiener-KAN架构** - 尚无论文明确定义Wiener-KAN，这是论文创新空间
2. **KAN vs LSTM效率** - Rather (2025)显示KEN-GRU> LSTM；但Ali (2025)显示LSTM>KAN
3. **RNN vs 1D-CNN效率** - 冲突已确认，1D-CNN更快，必须删除原声称
4. **Noorizadegan版本** - 需确认2025还是2026版本更完整

## 对文档的影响

- 更新文件：raw_literature.md, literature_catalog.md
- 新增Bo Wahlberg stochastic Wiener论文、Puyu Wang KAN优化边界、FiberKAN等条目
- 是否需要更新SUMMARY：否
- 是否需要后续STEP2分析：是（频域损失函数理论深度分析）

## 原始链接

- https://arxiv.org/abs/2303.04719 (Wiener sensor)
- https://arxiv.org/abs/1507.05535 (Stochastic Wiener)
- https://arxiv.org/abs/1805.09102 (Wiener CRLB)
- https://arxiv.org/abs/2601.22409 (KAN optimization)
- https://arxiv.org/abs/2510.10145 (FIRE)
- https://arxiv.org/abs/2411.00278 (KAN-AD)
- https://arxiv.org/abs/2408.07314 (Dong KAN)
