# 文献调研总结

**状态**: STEP3 R149 完成 (2026-03-30)
**R149更新**: 任务执行确认完成 - 根目录清洁性验证通过，68篇arXiv PDF + 71个Markdown文件存在性确认，GAP文档PDF路径一致性检查通过
**R147更新**: PDF收集验证完成 - 68篇arXiv PDF + 71个Markdown文件存在性验证通过；GAP文档PDF路径一致性检查通过
**R139更新**: 文档状态更新，系统性综合整理完成
**R136更新**: 文档状态更新，所有GAP支撑矩阵确认完整
**基于**: R94最终确认，R95最终完成确认
**阶段**: 理论框架就绪，文献调研完成，11个GAP均有文献支撑
**R117操作**: 系统性整理11个GAP支撑矩阵，核心文献清单按GAP主题分类更新
**R116操作**: HiPPO-KAN (Lee 2024) 和 FIRE (He 2025) 已验证，文献调研总览状态更新
**R113操作**: 状态更新确认，所有文献文档一致性检查通过
**R108操作**: GAP2 (线性度) 从"中缺口"降为"低缺口"；新增Sundararajan 2023, Li et al. 2025支撑
**R107操作**: GAP3/GAP5 (震级因素) 从"高缺口"降为"低缺口"；震级因素文献支撑更新
**R104操作**: GAP支撑文档格式统一化（强支撑/弱支撑表 + DOI链接）

---

## 概述

MET 非线性项目（Wiener-KAN 用于频率响应漂移补偿）的文献调研已完成。所有核心文献已验证，理论框架可直接支撑论文修订。

## 核心文献清单

| 文档 | 状态 | 说明 |
|------|------|------|
| key_references.md | STEP3 R117 | 核心文献清单，按GAP主题分类 |
| theory_framework.md | STEP3 R101 | 理论框架，整合所有支撑 |
| paper_draft_segments.md | STEP3 R101 | 可直接使用的论文草稿段落 |
| verified_literature.md | STEP2 R94 | 已验证文献详细记录（130+篇） |
| excluded_literature.md | STEP2 R88 | 已排除文献及冲突记录 |

## 审稿人回复映射

| 审稿意见 | 支撑文献 | 行动 |
|----------|----------|------|
| R3-4/R4-7 对比有限 | Yin 2017, Bai TCN, Rather 2025 | CNN/GRU-KAN/Transformer 架构对比 |
| R3-5 RVTDCNN | **未找到** | **移除此主张** |
| R3-6 数据集 | Xu&Wang 2008, Schoukens 2017 | 已支撑 |
| R4-1 激活函数 | Liu 2024 KAN, Dong 2024 | 已支撑 |
| R4-8 计算成本 | KANtize, LUT-KAN, PolyKAN, lmKAN | 已支持；移除 RNN vs CNN |

## 第二稿主张状态

| 主张 | 状态 | 核心文献 |
|------|------|----------|
| Wiener-KAN 架构 | **已支撑** | Cruz SS-KAN, TFKAN, Schoukens 2009, Haber 1990 |
| KAN+RNN 混合 | **已支撑** | Rather 2025 KAN-GRU, TKAN, Somvanshi 2025 |
| KAN 参数效率 | **已支撑** | Vacca-Rubio 2024 (109k vs 329k) |
| AFMAE 频域损失 | **强支撑** | OLMA (arXiv 2025), Subich (ICML 2025), FreDF (ICLR 2025), PETSA (ICML 2025) |
| KAN LUT 效率 | **强支撑** | **KAN-FIF**(94.8%压缩/68.7%加速/32.5%MAE), PolyKAN, lmKAN, KANtize, LUT-KAN, IoT KAN |
| 漂移补偿 | **已支撑** | Zhang 2022, Lin 2025, Shi 2022, Badawi DCT-CNN, Heng SAD-CNN |
| **RNN vs 1D-CNN 效率** | **冲突** | Saha 2026, Bian 2025 - **必须删除** |
| **KAN 计算效率 vs LSTM/GRU** | **无支撑** | 必须修正为参数效率 |

## 关键冲突（必须处理）

### 冲突 1：RNN vs 1D-CNN 效率
- Saha 2026：1D-CNN 比 LSTM 快 74x；Bian 2025：CNN 比 DeepConvLSTM 参数少 43.3x
- **行动**：必须删除此主张

### 冲突 2：KAN 计算效率 vs LSTM/GRU
- FEKAN 2026："KAN remains computationally demanding"
- KANtize 2026："B-spline computation accounts for up to 98%"
- **行动**：修正为"参数效率优势"而非"计算效率优势"

## 已废弃主张

| 声明 | 行动 |
|------|------|
| PIKAN 物理约束 | 删除 |
| FRIRNN 频率注入 | 删除 |
| RNN vs 1D-CNN 效率 | **冲突，删除** |
| KAN 计算效率 > LSTM/GRU | **无支撑，删除** |
| RVTDCNN | **未找到，删除** |

## MEASUREMENT 期刊目标

**目标**: 50 篇 | **达成**: 85 篇以上

## 理论框架核心结构

```
Wiener-KAN 架构
├── Wiener 模型理论 (Schoukens 2009, Haber 1990)
│   └── G1(z) → f(·) → G2(z)
├── KAN 网络 (Liu 2024)
│   └── B 样条激活 + LUT 计算
├── Wiener-KAN 连接 (Cruz 2025 SS-KAN, TFKAN Kui 2025)
│   └── 线性 RNN → KAN 非线性
└── AFMAE 损失 (OLMA, Subich, FreDF, PETSA)
    └── FFT L1 + MAE
```

## 引用文档

- `docs/research/literature/verified_literature.md` (STEP2 R94)
- `docs/research/literature/key_references.md` (STEP3 R101)
- `docs/research/literature/theory_framework.md` (STEP3 R101)
- `docs/research/literature/paper_draft_segments.md` (STEP3 R101)
- `docs/research/literature/excluded_literature.md` (STEP2 R88)
- `docs/IDEA.md`
- `docs/FRIKAN_REJECT.md`

## 分析报告追溯

| 轮次 | 关键分析 |
|------|---------|
| R149 | STEP3 R149完成：任务执行确认完成，根目录清洁性验证通过，68篇arXiv PDF + 71个Markdown文件存在性确认，GAP文档PDF路径一致性检查通过 |
| R147 | STEP3 R147完成：PDF收集验证完成，68篇arXiv PDF + 71个Markdown文件存在性确认，GAP文档PDF路径一致性检查通过 |
| R139 | STEP3 R139完成：系统性综合整理完成，文献调研总览状态更新 |
| R132 | STEP3 R132完成：文献调研总览状态验证完成 |
| R133 | STEP3 R133完成：文档状态更新，文献调研总览确认完整 |
| R136 | STEP3 R136完成：文档状态更新确认 |
| R130 | STEP3 R130完成：文献调研总览状态一致性检查完成 |
| R125 | R125完成：文献调研总览状态更新 |
| R122 | R122完成：文献调研总览状态更新确认 |
| R120 | R120完成：文献调研总览状态更新确认 |
| R118 | R118完成：文献调研总览一致性检查，11个GAP均有文献支撑，状态更新为R118 |
| R117 | R117完成：GAP支撑矩阵系统性整理，11个GAP均有文献支撑，核心文献按GAP主题分类 |
| R116 | R116完成：HiPPO-KAN 和 FIRE 验证完成，文献调研总览状态更新为R116 |
| R113 | R113完成：所有核心文献一致性检查通过，文档状态统一更新为R113 |
| R108 | R108完成：GAP2 (线性度) 降为低缺口，新增Sundararajan 2023, Li et al. 2025支撑 |
| R107 | R107完成：GAP3/GAP5文档和SUMMARY更新（高缺口→低缺口）；震级因素文献支撑更新 |
| R104 | R104完成：GAP支撑文档格式统一化，**添加KAN-FIF强支撑GAP7/GAP9** |
| R103 | R103完成：状态更新确认，**KAN-FIF三维提升证据**(94.8%压缩/68.7%加速/32.5%MAE降低) |
| R101 | R101最终完成：STEP3 R101确认完成，根目录清理(-p→logs/temp/) |
| R95 | R95最终完成确认：130+已验证论文，理论框架就绪 |
| R94 | R94最终确认：根目录清理，文献库完备，130+已验证论文 |
| R92 | R92验证：STEP3 R92确认完成，根目录清理，文档状态更新为R92 |
| R90 | R90最终确认：所有新增论文均已在目录，无高相关性新论文 |
| R86 | R86完成确认：文献库完整性最终核查通过 |
| R85 | R85分析：van Meer Hall传感器Wiener自标定(2.6x改善)、Niu LSTM迁移学习(10-50%加速) |
| R83 | GRAU (>90% LUT减少)、BitLogic (<20ns推理) - KAN LUT效率证据链完善 |
| R73 | 5条目排除；文献库最终收尾 |
| R70 | CKAN 冲突归档；MEASUREMENT 目标达成(85篇) |
| R66 | STEP2 最终分析完成 |
| R53 | KAN+RNN混合新证据；Wiener模型新进展 |
| R52 | Wiener模型新进展；频域损失新验证 |
| R49 | PolyKAN（GPU加速1.2-10x）、lmKAN(6.0x FLOPs减少) |
| R46-52 | Wiener 传感器文献、AFMAE 理论链确认 |
| R35 | DCT-Based Causal CNN化学传感器漂移 |
| R33-44 | KAN LUT 效率、KAN vs CNN/RNN 冲突确认 |
| R31 | HiPPO-KAN、Somvanshi KAN Survey、KAT、FIRE最终确认 |
| R28 | PETSA（ICML 2025）、Rodriguez-Linares频域依赖线性化器 |
| R27 | GNIO门控神经网络惯性里程计；7篇排除 |
| R26 | 130+篇已验证，0篇待核实，理论框架完善 |
| R25 | OLMA最强AFMAE支撑（熵减定理）；MEASUREMENT 85篇目标达成 |
| R24 | MEASUREMENT期刊（Lin电化学地震传感器）；频域损失（SATL） |
| R23 | KAN效率（SGN 11.7x、Free-RBF-KAN 2x、Physical KAN SYNE） |
| R21 | Wiener分数阶H-W；KAN效率（SGN、Free-RBF-KAN、Hoang <100ns） |
| R20 | KAN（Wiener等价、物理KAN、T-KAN）；Wiener函数滤波器、SSM-Wiener |
| R19 | KAN-HAR、KFS（频率损失）、TSKANMixer、KANFormer |
| R18 | FIRE、HiPPO-KAN、P-KAN、自由节点KAN、KAN-FIF |
| R17 | FreST损失、Subich ICML双重惩罚、Southworth多层KAN |
| R16 | KAN频谱偏差（Wang ICLR 2025）；随机Wiener理论（Wahlberg） |
| R15 | KAN收敛；KAN时间序列应用（Dong、KAN-AD、Barašin） |
| R14 | KAT验证；SKANODEs/Wiener-Hammerstein/Volterra/Benchmarks |
| R11 | KANtize、QuantKAN等；9已验证，5排除 |
| R10 | Somvanshi KAN Survey验证；KAT待核实 |
| R9 | 15已验证，7排除，Bai TCN重新分类 |
| R8 | FreDF找到；传感器测量验证 |
| R7 | Wiener传感器文献；AFMAE理论链确认 |
| R5 | RNN_CNN_Efficiency_Conflict确认 |
| R3 | Somvanshi KAN Survey、KAN_LUT_Hardware分析 |
| Deep | 初始深度分析完成 |

**STEP3 R139 完成** (2026-03-30): 系统性综合整理完成，所有GAP均有文献支撑
