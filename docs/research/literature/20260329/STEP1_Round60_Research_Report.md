# 调研报告：STEP1 Round60 (2026-03-29)

## 基本信息
- **日期**：2026-03-29
- **阶段**：STEP1 调研（第60轮）
- **覆盖范围**：系统性文献核查 - MEASUREMENT期刊论文、Wiener/KAN/频域损失新论文、传感器漂移补偿
- **是否使用子代理**：是；并行三个子代理分别检索：MEASUREMENT期刊论文、Wiener/KAN/频域论文、漂移补偿论文

## 检索路径

### 数据库
- arXiv (cs.LG, stat.ML, eess.SY)
- ScienceDirect (MEASUREMENT journal)
- IEEE Xplore
- Google Scholar

### 关键词
1. **MEASUREMENT期刊**：sensor nonlinearity compensation, temperature drift, sensor calibration, electrochemical sensor, e-nose
2. **KAN网络**：Kolmogorov-Arnold Networks, KAN, spline, time series
3. **频域损失**：frequency domain loss, spectral loss, FFT loss, AFMAE
4. **漂移补偿**：sensor drift compensation, electronic-nose, domain adaptation, deep learning

### 检索式
- `site:sciencedirect.com "Measurement" "sensor nonlinearity"`
- `site:arxiv.org "Kolmogorov-Arnold" OR "KAN" 2025 2026`
- `site:arxiv.org "frequency domain" "time series" 2025 2026`
- `Measurement journal "drift compensation" "sensor"`

## 发现结果

### MEASUREMENT期刊论文（已收录库确认）

子代理确认现有数据库已收录 **85+篇** MEASUREMENT期刊论文，关键分类如下：

| 类别 | 数量 | 代表论文 |
|------|------|----------|
| 传感器非线性补偿 | 5篇 | Xu&Wang 2008, Dutta 2018, Fang 2024 |
| 温度漂移补偿 | 5篇 | Lin 2020, Han 2020, Zhao 2022 |
| 传感器校准 | 10篇 | Pietrenko-Dabrowska 2024, Ahmad 2024 |
| 加速度计/陀螺仪 | 12篇 | Li 2024, Fazelinia 2024, Wang 2026 |
| 电化学/地震传感器 | 6篇 | Liu 2026, Nozato 2026, Qiu 2025 |
| 光学传感器 | 8篇 | Li 2024, Xu 2025 |
| 力/压力传感器 | 8篇 | Zhang 2021, Amer 2024, Zhao 2023 |
| 位移/感应传感器 | 6篇 | Nurkowski 2023, Feng 2026 |

**2020年后论文**：65+篇（超过40篇目标）
**高相关性论文**：约40篇

### 新增文献线索（13篇新论文 - 2025-2026）

#### P0 高相关性新论文（5篇）

| 字段 | 内容 |
|------|------|
| 标题 | PaCoDi: Parallel Complex Diffusion for Scalable Time Series Generation |
| 作者 | Cai, Wan, Zhang, Jin, Ge, Wen, Liu |
| 年份 | 2026 |
| arXiv ID | 2602.17706 |
| DOI | https://arxiv.org/abs/2602.17706 |
| 摘要 | 引入谱原生架构，在频域中使用傅里叶变换对复扩散进行对角化，解耦生成建模。推导了扩散的Spectral Wiener Process。 |
| 类别 | P0 |
| 相关度 | **高** |
| 状态 | **新增待核实** |
| 备注 | 频域扩散生成模型，与AFMAE频域损失理论相关 |

| 字段 | 内容 |
|------|------|
| 标题 | FreIE: Low-Frequency Spectral Bias in Neural Networks |
| 作者 | Sun, Ling, Zou, Kang, Zhang |
| 年份 | 2025 |
| arXiv ID | 2510.25800 |
| DOI | https://arxiv.org/abs/2510.25800 |
| 摘要 | 系统性测量各模型频谱偏置，低频优先学习。提出FreLE算法，具有显式/隐式频域正则化。 |
| 类别 | P0 |
| 相关度 | **高** |
| 状态 | **新增待核实** |
| 备注 | 频谱偏置理论，与AFMAE频域损失直接相关 |

| 字段 | 内容 |
|------|------|
| 标题 | KAN-FIF: Spline-Parameterized Physics-based TC Estimation |
| 作者 | Shen, Chen, Wang, Xu, Zhang, Bai, Zhang |
| 年份 | 2026 |
| arXiv ID | 2602.12117 |
| DOI | https://arxiv.org/abs/2602.12117 |
| 摘要 | KAN用于卫星气象台风估算。相对于基线减少94.8%参数。边缘部署实现14.41ms延迟。 |
| 类别 | P0 |
| 相关度 | **高** |
| 状态 | **新增待核实** |
| 备注 | KAN效率验证：参数减少94.8%，边缘部署14.41ms延迟 |

| 字段 | 内容 |
|------|------|
| 标题 | DecoKAN: Interpretable Decomposition for Crypto Forecasting |
| 作者 | Gao, Dong, Wang, Wang, Zhang, Wang |
| 年份 | 2025 |
| arXiv ID | 2512.20028 |
| DOI | https://arxiv.org/abs/2512.20028 |
| 摘要 | DWT + KAN mixers用于加密货币预测，通过符号分析实现可解释性。 |
| 类别 | P0 |
| 相关度 | **高** |
| 状态 | **新增待核实** |
| 备注 | KAN时序应用+可解释性 |

| 字段 | 内容 |
|------|------|
| 标题 | HaKAN: Hahn Kolmogorov-Arnold Networks |
| 作者 | Hasan, Bouguilia |
| 年份 | 2026 |
| arXiv ID | 2601.18837 |
| DOI | https://arxiv.org/abs/2601.18837 |
| 摘要 | 使用基于Hahn多项式的可学习激活函数，作为多元时序预测的轻量级可解释替代方案。 |
| 类别 | P0 |
| 相关度 | **高** |
| 状态 | **新增待核实** |
| 备注 | KAN变体，用于时序预测 |

#### P1 中相关性新论文（8篇）

| 字段 | 内容 |
|------|------|
| 标题 | SciTS: Scientific Time Series Understanding and Generation with LLMs |
| 作者 | Wu, Zhang, Liu, Xu, Zhuang, Fan, Lv, Liu等 |
| 年份 | 2025/2026 |
| arXiv ID | 2510.03255 |
| DOI | https://arxiv.org/abs/2510.03255 |
| 摘要 | 12领域43任务的科学时序理解基准。引入TimeOmni框架用于LLM时序理解。ICLR 2026接收。 |
| 类别 | P1 |
| 相关度 | 中 |
| 状态 | **新增待核实** |

| 字段 | 内容 |
|------|------|
| 标题 | DeepFeatIoT: IoT Time Series Sensor Data Classification |
| 作者 | Inan, Liao |
| 年份 | 2025 |
| arXiv ID | 2508.09468 |
| DOI | https://arxiv.org/abs/2508.09468 |
| 摘要 | 统一深度学习、随机化和LLM特征用于IoT时序分类。IJCAI 2025接收。 |
| 类别 | P1 |
| 相关度 | 中 |
| 状态 | **新增待核实** |

| 字段 | 内容 |
|------|------|
| 标题 | Fre-CW: Targeted Attack on Time Series using Frequency Domain Loss |
| 作者 | Feng, Chen, Tang, Ding, Li, Bai |
| 年份 | 2025 |
| arXiv ID | 2508.08955 |
| DOI | https://arxiv.org/abs/2508.08955 |
| 摘要 | 使用频域损失对预测进行对抗攻击——首个基于频域的时序攻击工作。 |
| 类别 | P1 |
| 相关度 | 中 |
| 状态 | **新增待核实** |

| 字段 | 内容 |
|------|------|
| 标题 | PETSA: Parameter-Efficient Test-Time Adaptation |
| 作者 | Medeiros, Sharifi-Noghabi, Oliveira, Irandoust |
| 年份 | 2025 |
| arXiv ID | 2506.23424 |
| DOI | https://arxiv.org/abs/2506.23424 |
| 摘要 | 结合鲁棒项+频域损失+逐patch结构项用于测试时适应。 |
| 类别 | P1 |
| 相关度 | 中 |
| 状态 | **新增待核实** |

| 字段 | 内容 |
|------|------|
| 标题 | AEFIN: Non-Stationary TS Forecasting with Fourier Analysis |
| 作者 | Xiong, Wen |
| 年份 | 2025 |
| arXiv ID | 2505.06917 |
| DOI | https://arxiv.org/abs/2505.06917 |
| 摘要 | 傅里叶分析+交叉注意力+MLP用于非平稳序列，结合时域/频域损失。IJCNN 2025接收。 |
| 类别 | P1 |
| 相关度 | 中 |
| 状态 | **新增待核实** |

| 字段 | 内容 |
|------|------|
| 标题 | KANFormer: KAN+Transformer for Limit Order Books |
| 作者 | Zhong, Bacry, Guilloux, Muzy |
| 年份 | 2025 |
| arXiv ID | 2512.05734 |
| DOI | https://arxiv.org/abs/2512.05734 |
| 摘要 | KAN增强模型用于订单簿填充概率预测，使用生存分析。 |
| 类别 | P1 |
| 相关度 | 高 |
| 状态 | **新增待核实** |

| 字段 | 内容 |
|------|------|
| 标题 | KASPER: KAN for Stock Prediction and Explainable Regimes |
| 作者 | Oad, Pathak, Innan, D, Shafique |
| 年份 | 2025 |
| arXiv ID | 2507.18983 |
| DOI | https://arxiv.org/abs/2507.18983 |
| 摘要 |  regime检测+sparse spline KAN+符号规则提取用于股价预测。R²=0.89。TMLR 2026发表。 |
| 类别 | P1 |
| 相关度 | 中 |
| 状态 | **新增待核实** |

| 字段 | 内容 |
|------|------|
| 标题 | APRNet: Amplitude-Phase Reconstruct Network |
| 作者 | Liu, Yang, Xiaoxing, Ma, Zhu |
| 年份 | 2025 |
| arXiv ID | 2508.08919 |
| DOI | https://arxiv.org/abs/2508.08919 |
| 摘要 | KAN-based局域相关模块通过振幅-相位关系进行平稳性建模。 |
| 类别 | P1 |
| 相关度 | 中 |
| 状态 | **新增待核实** |

### 入口已定位

- arXiv: https://arxiv.org/search/?searchtype=all&query=frequency+domain+loss+time+series
- ScienceDirect MEASUREMENT: https://www.sciencedirect.com/journal/measurement
- 论文数据库本地已包含85+ MEASUREMENT期刊论文

### 疑似重复
- 无

### 明确排除
- 无

## 待核实事项

1. 验证新增13篇论文的DOI和详细信息
2. 确认KAN-FIF论文的边缘部署延迟数据是否可作为KAN LUT效率支撑
3. FreIE论文的频谱偏置理论是否可作为AFMAE理论基础补充

## 对文档的影响

- 更新了哪些文件：raw_literature.md（新增13条）, literature_catalog.md（如需要）
- 是否需要更新 SUMMARY：否
- 是否需要后续 STEP2 分析：待核实后决定

## 原始链接

- PaCoDi: https://arxiv.org/abs/2602.17706
- FreIE: https://arxiv.org/abs/2510.25800
- KAN-FIF: https://arxiv.org/abs/2602.12117
- DecoKAN: https://arxiv.org/abs/2512.20028
- HaKAN: https://arxiv.org/abs/2601.18837
- SciTS: https://arxiv.org/abs/2510.03255
- DeepFeatIoT: https://arxiv.org/abs/2508.09468
- Fre-CW: https://arxiv.org/abs/2508.08955
- PETSA: https://arxiv.org/abs/2506.23424
- AEFIN: https://arxiv.org/abs/2505.06917
- KANFormer: https://arxiv.org/abs/2512.05734
- KASPER: https://arxiv.org/abs/2507.18983
- APRNet: https://arxiv.org/abs/2508.08919

## 文献库完整性确认

| 类别 | 已收录数量 | 目标 | 状态 |
|------|------------|------|------|
| KAN网络 | 65+篇 | - | ✅ 已完备 |
| Wiener模型 | 35+篇 | - | ✅ 已完备 |
| 频域损失函数 | 30+篇 | - | ✅ 已完备 |
| 漂移补偿 | 30+篇 | - | ✅ 已完备 |
| 架构效率 | 15+篇 | - | ✅ 已完备 |
| MEASUREMENT期刊 | 85+篇 | 50篇(40篇2020后) | ✅ 超额完成 |

**本轮结论**：文献库整体已完备。本轮新增13条新论文线索（主要是2025-2026年频域损失和KAN变体），待进一步核实。MEASUREMENT期刊论文已确认有85+篇，远超50篇目标。