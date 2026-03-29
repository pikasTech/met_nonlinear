# 调研报告：STEP1 Round 9 文献核实与扩展

## 基本信息
- 日期：2026-03-28
- 阶段：STEP1 调研
- 覆盖范围：频域损失函数核实、KAN效率对比、传感器非线性补偿、TDKAN变体
- 是否使用子代理：是（5个并行子代理）

## 检索路径

### 子代理1：FreDF论文核实
- 目标：核实FreDF (ICLR 2025) 论文详细信息
- 发现：FreDF 已确认 ICLR 2025 接收，损失函数公式 L^α = α·|F(Ŷ)-F(Y)|₁ + (1-α)·MSE

### 子代理2：SAMFre/Floss/FTMixer核实
- 目标：核实频域损失相关论文
- 发现：
  - SAMFre: 直接使用与AFMAE相同的公式结构
  - Floss: 使用周期正则化方法，公式结构不同
  - FTMixer: 时频融合架构，非损失函数

### 子代理3：传感器非线性补偿检索
- 关键词：sensor nonlinearity compensation, electrochemical sensor, deep learning
- 发现：多个传感器建模论文

### 子代理4：KAN效率对比核实
- 目标：核实KAN vs LSTM/GRU效率论文
- 发现：
  - Ali 2025: LSTM精度6-10x优于KAN，但KAN训练速度快2.1x
  - Rather 2025: GRU-KAN/LSTM-KAN hybrid优于pure LSTM/GRU
  - 建议：论文声称应聚焦于KAN-GRU hybrid效率

### 子代理5：TKAN变体核实
- 目标：核实TKAN及其变体论文
- 发现：
  - TKAN (Genet 2024): KAN + LSTM gating
  - TimeKAN (Huang 2025): 频率分解 + KAN
  - TFKAN (Kui 2025): 时频双分支架构

## 发现结果

### 新增文献线索（Pending状态升级）

#### 频域损失（P0）
| 作者 | 年份 | 标题 | DOI/链接 | 状态 |
|------|------|------|----------|------|
| Hao Wang et al. | 2025 | FreDF: Learning to Forecast in the Frequency Domain (ICLR 2025) | https://doi.org/10.48550/arXiv.2402.02399 | Verified |
| Bin Wang et al. | 2025 | TimeCF with SAMFre | https://doi.org/10.48550/arXiv.2505.17532 | Verified |
| Yang et al. | 2023 | Floss: Frequency Domain Regularization | https://doi.org/10.48550/arXiv.2308.01011 | Verified |
| Li et al. | 2024 | FTMixer: Frequency+Time Domain Fusion | https://doi.org/10.48550/arXiv.2405.15256 | Verified |

#### TKAN变体（P0）
| 作者 | 年份 | 标题 | DOI/链接 | 状态 |
|------|------|------|----------|------|
| Genet, Inzirillo | 2024 | TKAN: Temporal KAN | https://doi.org/10.48550/arXiv.2405.07344 | Verified |
| Huang et al. | 2025 | TimeKAN: KAN-based Frequency Decomposition | https://doi.org/10.48550/arXiv.2502.06910 | Verified |
| Kui et al. | 2025 | TFKAN: Time-Frequency KAN | https://doi.org/10.48550/arXiv.2506.12696 | Verified |
| Cruz et al. | 2025 | SS-KAN for Wiener-Hammerstein | https://doi.org/10.48550/arXiv.2506.16392 | Verified |

#### KAN效率对比（P1）
| 作者 | 年份 | 标题 | DOI/链接 | 状态 |
|------|------|------|----------|------|
| Ali et al. | 2025 | KAN vs LSTM Performance | https://doi.org/10.48550/arXiv.2511.18613 | Verified |
| Rather et al. | 2025 | GRU-KAN/LSTM-KAN Hybrid | https://doi.org/10.48550/arXiv.2507.13685 | Verified |

### 疑似重复
- 无

### 明确排除
- 无

## 待核实事项
1. FreDF 的 ICLR 2025 官方链接已确认，但建议在论文中谨慎引用
2. TKAN 系列均为 arXiv preprint，未经过 peer-review

## 关键发现总结

### AFMAE 理论基础
- **FreDF (ICLR 2025)** 提供了 α·|F(Ŷ)-F(Y)|₁ + (1-α)·MSE 公式的完整理论支撑
- **SAMFre** 使用相同公式结构并结合 Sharpness-Aware Minimization 优化
- **建议**：使用 FreDF 作为 AFMAE 损失函数的理论依据

### KAN vs LSTM 效率冲突
- **Ali 2025**: Pure KAN 训练快2.1x，但精度不如 LSTM
- **Rather 2025**: GRU-KAN/LSTM-KAN hybrid 优于 pure LSTM/GRU
- **Resolution**: 论文应聚焦于 KAN-GRU hybrid 的效率优势，而非 pure KAN

## 对文档的影响
- 更新了 `docs/research/literature/raw_literature.md`
- 更新了 `docs/research/literature/literature_catalog.md`
- 不需要更新 SUMMARY（本次为STEP1调研阶段）

## 原始链接
- https://doi.org/10.48550/arXiv.2402.02399 (FreDF)
- https://doi.org/10.48550/arXiv.2505.17532 (SAMFre)
- https://doi.org/10.48550/arXiv.2405.07344 (TKAN)
- https://doi.org/10.48550/arXiv.2507.13685 (KAN-GRU hybrid)
- https://doi.org/10.48550/arXiv.2511.18613 (KAN vs LSTM)
