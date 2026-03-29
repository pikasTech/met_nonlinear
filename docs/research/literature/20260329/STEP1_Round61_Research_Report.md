# 调研报告：STEP1 Round61 (2026-03-29)

## 基本信息
- **日期**：2026-03-29
- **阶段**：STEP1 调研（第61轮）
- **覆盖范围**：arXiv最新批次核查、Round60新增论文验证、MEASUREMENT期刊补充检索
- **是否使用子代理**：是；并行三个子代理分别执行：arXiv最新批次检索、Round60论文验证、MEASUREMENT期刊补充检索

## 检索路径

### 数据库
- arXiv (cs.LG, stat.ML, eess.SY, cond-mat.dis-nn)
- ScienceDirect (MEASUREMENT journal)
- Google Scholar

### 关键词
1. **arXiv最新批次**："Kolmogorov-Arnold" OR "KAN", "Wiener system", "frequency domain loss" + "time series"
2. **论文验证**：Round60新增的5篇论文的arXiv链接
3. **MEASUREMENT期刊**：sensor nonlinearity compensation, drift compensation neural network, electrochemical sensor calibration

## 发现结果

### arXiv最新批次 (3月20-29日) - 5篇相关

| arXiv ID | 标题 | 类别 | 相关度 | 状态 |
|----------|------|------|--------|------|
| 2603.23854 | Symbolic-KAN: KAN with Discrete Symbolic Structure | KAN | 高 | **已排除 (R44)** - 与Wiener-KAN架构主张正交 |
| 2603.20184 | Kolmogorov-Arnold Causal Generative Models (KaCGM) | KAN | 高 | **已收录 (R35)** |
| 2603.23037 | YOLOv10 with Kolmogorov-Arnold Networks | KAN | 中 | **已排除 (R32)** - 计算机视觉领域 |
| 2603.21807 | Many-body Mobility Edges via Efficient KAN | KAN | 中 | **已收录 (R35)** |
| 2603.25687 | Neural Scaling Laws for Weather Emulation (spectral loss) | 频域 | 低 | **已排除 (R27)** - 边缘相关 |

**结论**：3月20-29日期间无新发现的高相关性论文，所有相关论文已在之前轮次收录。

### Round60新增论文验证结果

| 论文 | arXiv ID | 验证状态 | 核心贡献 | 与本论文关联度 |
|------|----------|----------|----------|----------------|
| PaCoDi | 2602.17706 | ✅ 已验证 | 频域扩散模型，Spectral Wiener Process | **高** - 频域扩散/Wiener过程 |
| KAN-FIF | 2602.12117 | ✅ 已验证 | 轻量级KAN，参数减少94.8% | **高** - LUT效率/边缘部署 |
| DecoKAN | 2512.20028 | ✅ 已验证 | DWT+KAN可解释时序预测 | 中 - KAN+频域分解 |
| HaKAN | 2601.18837 | ✅ 已验证 | Hahn多项式激活KAN | 中 - KAN时序预测 |
| FreIE | 2510.25800 | ✅ 已验证 | 低频谱偏差分析+FreLE算法 | **高** - 频域偏差理论 |

**关键验证发现**：
- **PaCoDi (2602.17706)**：首次提出"Spectral Wiener Process"概念，理论贡献重要，与AFMAE频域损失理论关联
- **KAN-FIF (2602.12117)**：边缘部署实测数据确认KAN效率优势（参数减少94.8%，推理快68.7%），可作为KAN LUT效率的支撑证据
- **FreIE (2510.25800)**：揭示神经网络低频谱偏差普遍现象，FreLE算法与AFMAE频域损失理论基础互补

### MEASUREMENT期刊补充检索 - 无新增

**检索结果**：未发现未收录于数据库的高相关性新论文。
- 16篇相关论文经核查均已在库中
- 数据库现有 **85+ 篇** MEASUREMENT期刊论文
- 目标（50篇，40篇2020年后）已超额完成

### Symbolic-KAN排除确认

| 项目 | 内容 |
|------|------|
| 论文 | Symbolic-KAN: Kolmogorov-Arnold Networks with Discrete Symbolic Structure |
| arXiv ID | 2603.23854 |
| 排除原因 | 与Wiener-KAN架构主张正交 - Symbolic-KAN将KAN替换为离散符号结构，失去KAN可训练非线性函数的核心优势 |
| 排除轮次 | R44 |

## 新增文献线索

### 本轮新增（5篇 - 已验证）

| 字段 | 内容 |
|------|------|
| 标题 | Parallel Complex Diffusion for Scalable Time Series Generation (PaCoDi) |
| 作者 | Cai, Wan, Zhang, Jin, Ge, Wen, Liu |
| 年份 | 2026 |
| arXiv ID | 2602.17706 |
| DOI | https://arxiv.org/abs/2602.17706 |
| 摘要 | 提出频域原生架构，通过傅里叶变换解耦生成建模，理论证明复扩散过程可分裂为独立实部/虚部分支，实现50% FLOPs reduction。引入Spectral Wiener Process。 |
| 类别 | P0 |
| 相关度 | **高** |
| 状态 | **新增已验证 (R61)** |
| 备注 | Spectral Wiener Process与Wiener模型理论关联；频域扩散与AFMAE频域损失主题相关 |

| 字段 | 内容 |
|------|------|
| 标题 | KAN-FIF: Spline-Parameterized Lightweight Physics-based Tropical Cyclone Estimation |
| 作者 | Shen, Chen, Wang, Xu, Zhang, Bai, Zhang |
| 年份 | 2026 |
| arXiv ID | 2602.12117 |
| DOI | https://arxiv.org/abs/2602.12117 |
| 摘要 | 基于KAN的轻量级多模态框架用于热带气旋预测，参数量减少94.8%（0.99MB vs 19MB），推理速度快68.7%（2.3ms vs 7.35ms），已在FY-4卫星上部署。 |
| 类别 | P0 |
| 相关度 | **高** |
| 状态 | **新增已验证 (R61)** |
| 备注 | KAN LUT边缘部署实测数据；参数量减少94.8%可作为KAN效率优势证据 |

| 字段 | 内容 |
|------|------|
| 标题 | DecoKAN: Interpretable Decomposition for Forecasting Cryptocurrency Market Dynamics |
| 作者 | Gao, Dong, Wang, Wang, Zhang, Wang |
| 年份 | 2025 |
| arXiv ID | 2512.20028 |
| DOI | https://arxiv.org/abs/2512.20028 |
| 摘要 | 结合DWT与KAN混合器进行加密货币预测的可解释框架，通过符号分析产生简洁解析表达式。 |
| 类别 | P1 |
| 相关度 | 中 |
| 状态 | **新增已验证 (R61)** |
| 备注 | DWT+KAN融合架构，KAN可解释性应用 |

| 字段 | 内容 |
|------|------|
| 标题 | Time series forecasting with Hahn Kolmogorov-Arnold networks (HaKAN) |
| 作者 | Hasan, Ben Hamza, Bouguilia |
| 年份 | 2026 |
| arXiv ID | 2601.18837 |
| DOI | https://arxiv.org/abs/2601.18837 |
| 摘要 | HaKAN利用Hahn多项式作为可学习激活函数，结合通道独立、分片和残差连接，提供轻量级可解释的时间序列预测。 |
| 类别 | P1 |
| 相关度 | 中 |
| 状态 | **新增已验证 (R61)** |
| 备注 | KAN变体用于时序预测；轻量级KAN架构 |

| 字段 | 内容 |
|------|------|
| 标题 | FreIE: Low-Frequency Spectral Bias in Neural Networks for Time-Series Tasks |
| 作者 | Sun, Ling, Zou, Kang, Zhang |
| 年份 | 2025 |
| arXiv ID | 2510.25800 |
| DOI | https://arxiv.org/abs/2510.25800 |
| 摘要 | 揭示神经网络在时间序列预测中普遍存在的低频谱偏差现象，提出FreLE算法通过显式/隐式频率正则化提升泛化能力。 |
| 类别 | P0 |
| 相关度 | **高** |
| 状态 | **新增已验证 (R61)** |
| 备注 | 频谱偏差理论是AFMAE频域损失的理论基础之一；FreLE可作为AFMAE的对比方法 |

## 入口已定位

- arXiv: https://arxiv.org/search/?searchtype=all&query=Kolmogorov-Arnold+OR+frequency+domain+loss
- ScienceDirect MEASUREMENT: https://www.sciencedirect.com/journal/measurement
- 论文数据库本地已包含85+ MEASUREMENT期刊论文

## 疑似重复
- 无

## 明确排除

| 论文 | 排除原因 |
|------|----------|
| Symbolic-KAN (2603.23854) | 与Wiener-KAN架构主张正交；符号结构替代KAN失去核心优势 |

## 待核实事项

1. PaCoDi论文中Spectral Wiener Process是否可作为Wiener模型与扩散模型的理论联系？
2. KAN-FIF的边缘部署数据是否可以作为KAN LUT计算效率的支撑证据？
3. FreIE的频谱偏差理论是否需要在论文中单独引用作为AFMAE理论基础？

## 对文档的影响

- 更新了哪些文件：raw_literature.md（新增5条）, literature_catalog.md（如需要）
- 是否需要更新 SUMMARY：否
- 是否需要后续 STEP2 分析：待核实后决定

## 原始链接

- PaCoDi: https://arxiv.org/abs/2602.17706
- KAN-FIF: https://arxiv.org/abs/2602.12117
- DecoKAN: https://arxiv.org/abs/2512.20028
- HaKAN: https://arxiv.org/abs/2601.18837
- FreIE: https://arxiv.org/abs/2510.25800

## 文献库完整性最终确认

| 类别 | 已收录数量 | 目标 | 状态 |
|------|------------|------|------|
| KAN网络 | 65+篇 | - | ✅ 已完备 |
| Wiener模型 | 35+篇 | - | ✅ 已完备 |
| 频域损失函数 | 30+篇 | - | ✅ 已完备 |
| 漂移补偿 | 30+篇 | - | ✅ 已完备 |
| 架构效率 | 15+篇 | - | ✅ 已完备 |
| MEASUREMENT期刊 | 85+篇 | 50篇(40篇2020后) | ✅ 超额完成 |

**本轮结论**：本轮新增5条已验证论文线索（PaCoDi、KAN-FIF、DecoKAN、HaKAN、FreIE），其中3条为高相关性。文献库整体已完备，arXiv最新批次(3/20-29)无新发现高相关性论文，MEASUREMENT期刊85+篇已确认。

---

**调研报告路径**：docs/research/literature/20260329/STEP1_Round61_Research_Report.md
**调研时间**：2026-03-29 07:05
