# 调研报告：STEP1 Round 10 KAN文献扩展调研

## 基本信息
- 日期：2026-03-28
- 阶段：STEP1 调研
- 覆盖范围：2025-2026年新KAN变体架构、Wiener模型传感器应用、测量方法论
- 是否使用子代理：是（4个并行子代理）

## 检索路径

### 子代理1：Wiener模型传感器应用调研
- 目标：搜索Wiener模型在电化学/地震传感器中的应用
- 发现：已有文献涵盖Volterra系统分析(Iqbal 2024)、块模型结构(Xu & Wang 2008)
- 关键文献：Schoukens 2009, Haber 1990, Cruz 2025 (SS-KAN)

### 子代理2：2025-2026 KAN新变体调研
- 目标：搜索最新KAN架构
- 发现：多个新型KAN架构

### 子代理3：测量方法论文献调研
- 目标：传感器频率响应测量、非线性校准、数据集构建
- 发现：Xu & Wang 2008 (Measurement)、Schoukens & Noël 2017等

### 子代理4：频域损失函数调研
- 目标：AFMAE相关文献
- 发现：FreDF (ICLR 2025)已验证

## 新发现文献线索（已通过arXiv核实）

### KAN新变体架构（P0）

| 作者 | 年份 | 标题 | DOI/链接 | 关键发现 | 状态 |
|------|------|------|----------|----------|------|
| Jiang et al. | 2025 | KANMixer: KAN for LTSF | https://doi.org/10.48550/arXiv.2508.01575 | 16/28实验SOTA；首个KAN LTSF实践指南 | Verified |
| Jarraya et al. | 2025 | SOH-KLSTM: KAN+LSTM Hybrid | https://doi.org/10.48550/arXiv.2509.10496 | LSTM长期依赖+KAN非线性；架构模式平行Wiener | Verified |
| Zeng et al. | 2025 | AR-KAN: Autoregressive-Weight-Enhanced KAN | https://doi.org/10.48550/arXiv.2509.02967 | AR(线性)+KAN(非线性)=Wiener结构模式；72%数据集优于其他 | Verified |
| Wang et al. | 2025 | WaveTuner: Wavelet Subband+KAN | https://doi.org/10.48550/arXiv.2511.18846 | 多分支KAN处理不同频带；与滤波器组理论相似 | Verified |
| Wang et al. | 2025 | Fourier-KAN-Mamba | https://doi.org/10.48550/arXiv.2511.15083 | Fourier层+KAN+Mamba；线性频谱特征→非线性 | Verified |
| Hasan et al. | 2026 | HaKAN: Hahn Polynomial KAN | https://doi.org/10.48550/arXiv.2601.18837 | Hahn多项式激活函数；通道独立+patching | Verified |
| Zhang et al. | 2026 | Time-TK: Transformer+KAN | https://doi.org/10.48550/arXiv.2602.11190 | Multi-Offset交互KAN；Transformer+KAN混合 | Verified |
| Ye | 2025 | ss-Mamba: Spline+KAN+Mamba | https://doi.org/10.48550/arXiv.2506.14802 | 语义索引嵌入+spline KAN时序编码 | Verified |
| Somvanshi et al. | 2024 | KAN Survey (ACM) | https://doi.org/10.48550/arXiv.2411.06078 | KAN+CNN/RNN/Transformer集成趋势；300+引用 | Verified |

### KAN Survey (Somvanshi 2024) 关键发现

- KAN原论文300+引用
- KAN+CNN/RNN/Transformer混合是增长趋势
- KAN在时间序列预测、计算生物医学、图学习等应用
- 关键架构：Temporal-KAN, FastKAN, PDE KAN
- KAN的优势：自适应边激活函数、参数效率、可解释性
- KAN的挑战：高维和噪声数据计算

### AR-KAN (Zeng 2025) 重要发现

- **架构模式直接对应Wiener结构**：AR(线性时间记忆)+KAN(非线性表示)
- 实验结果：72%数据集达到最佳，匹配ARIMA在周期函数表现
- 证明了AR(线性)和KAN(非线性)分离设计的有效性
- **与论文Wiener-KAN设计直接相关**

### KANMixer (Jiang 2025) 关键贡献

- 首个KAN作为LTSF主干的系统研究
- 多尺度混合主干充分利用KAN自适应能力
- 16/28实验SOTA
- 提供了KAN在LTSF中有效利用的实践指南

## 待核实事项

1. 这些新KAN变体的具体效率数据（参数量、FLOPs）需要在后续步骤中核实
2. AR-KAN的Wiener类比结构值得进一步分析

## 对文档的影响

- 更新 `docs/research/literature/raw_literature.md`：新增9条KAN文献
- 更新 `docs/research/literature/literature_catalog.md`：新增KAN变体分类
- 不需要更新SUMMARY（STEP1调研阶段）

## 原始链接

- https://doi.org/10.48550/arXiv.2508.01575 (KANMixer)
- https://doi.org/10.48550/arXiv.2509.10496 (SOH-KLSTM)
- https://doi.org/10.48550/arXiv.2509.02967 (AR-KAN)
- https://doi.org/10.48550/arXiv.2511.18846 (WaveTuner)
- https://doi.org/10.48550/arXiv.2511.15083 (Fourier-KAN-Mamba)
- https://doi.org/10.48550/arXiv.2601.18837 (HaKAN)
- https://doi.org/10.48550/arXiv.2602.11190 (Time-TK)
- https://doi.org/10.48550/arXiv.2506.14802 (ss-Mamba)
- https://doi.org/10.48550/arXiv.2411.06078 (KAN Survey)
