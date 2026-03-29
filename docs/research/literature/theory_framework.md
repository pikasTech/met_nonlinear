# 理论框架

**状态**: STEP3 R101 最终完成 (2026-03-29 18:10)
**基于**: verified_literature.md (STEP2 R94)
**原则**: 决策层整理，直接支撑论文声称
**R101更新**: STEP3 R101最终完成，根目录清理(-p→logs/temp/)，文献分析结果已整理为决策层文档

---

## 1. Wiener-KAN 架构

### 1.1 核心概念

Wiener 模型 = **线性动态分量** (RNN) + **静态非线性分量** (KAN)

**理论支撑**：
- Kolmogorov-Arnold 定理 (Liu 2024)：单变量函数逼近
- Barron 空间理论 (Manavalan 2026)：维度无关收敛速率
- 稳定性理论 (Revay 2021)：收缩动力学保证

### 1.2 经典 Wiener 基础

| 论文 | 贡献 |
|------|------|
| Schoukens 2009 WH 基准 | G1(z)→f(·)→G2(z)，157+ 引用 |
| Haber 1990 | "Wiener = 线性动态 + 静态非线性"，500+ 引用 |

### 1.3 深度学习验证

| 论文 | 贡献 |
|------|------|
| Cruz 2025 SS-KAN | 线性状态空间 + KAN 用于 Wiener-Hammerstein |
| Kui 2025 TFKAN | 首个频域 KAN；双分支 FreqKAN + TimeKAN |
| Li 2024 LSTM-Wiener | LSTM 替换 Wiener G(z) |

---

## 2. KAN+RNN 混合有效性

| 论文 | 发现 |
|------|------|
| Rather 2025 KAN-GRU | GRU-KAN/LSTM-KAN **> LSTM/GRU/LSTM-Attention/LSTM-Transformer** |
| Genet 2024 TKAN | TKAN > GRU > LSTM（12步预测） |
| Somvanshi 2025 | KAN+RNN 集成是新兴趋势；300+ 引用 |
| Wang 2025 KAN 频谱偏差 (ICLR) | **KAN 频谱偏差 < MLP** → 更好捕获高频 |

---

## 3. AFMAE 频域损失

### 3.1 AFMAE 公式

```
L_AFMAE = α · |FFT(pred) - FFT(real)|₁ + (1-α) · MAE
```

### 3.2 理论支撑链

```
MSE → "双重惩罚"平滑 (Subich ICML 2025)
         ↓
         FFT 损失 → 保留高频 (KFS/FreDF/FIRE)
         ↓
         AFMAE = FFT L1 + MAE
         ↓
         熵减理论 (OLMA Shi arXiv 2025) → 信息论基础
```

### 3.3 关键文献

| 论文 | 贡献 |
|------|------|
| **Shi 2025 OLMA (arXiv 2025)** | **最强支撑**：Theorem 1 证明酉变换降低边缘熵 |
| **Subich 2025 (ICML)** | MSE"双重惩罚"效应 → 直接解释时域 MSE 不足 |
| Wang 2025 FreDF (ICLR) | **直接公式匹配**：L^α = α·|F(Ŷ)-F(Y)|₁ + (1-α)·MSE |
| Wu 2025 KFS | ℒ = αℒ_F + (1-α)ℒ_MSE + Parseval 定理 |
| **Medeiros 2025 PETSA (ICML)** | 三组件频域损失保留周期性 |

---

## 4. KAN LUT 效率

### 4.1 直接证据

| 论文 | 发现 |
|------|------|
| **Yu 2025 PolyKAN** | GPU加速 1.2-10x 推理，1.4-12x 训练 |
| **Pozdnyakov 2025 lmKAN** | **6.0x FLOPs减少**；H100 10x 吞吐量 |
| Errabii 2026 KANtize | **50x BitOps 减少**，2.9x GPU 加速 |
| Kuznetsov 2026 LUT-KAN | **比基线 KAN 快 12 倍** |
| Kuznetsov 2026 IoT KAN | **比原始 KAN 快 5000 倍** |
| **Liu 2026 GRAU (R83)** | 分段线性拟合，power-of-two 斜率，**>90% LUT消耗减少** |
| **Bührer 2026 BitLogic (R83)** | 基于LUT的NN计算，**<0.3M逻辑门；<20ns推理** |

### 4.2 ⚠️ 必须删除的声称

**KAN 相对 LSTM/GRU 有计算效率优势** - 无文献支撑

| 论文 | 发现 |
|------|------|
| FEKAN 2026 | "KAN remains computationally demanding" |
| KANtize 2026 | "B-spline computation accounts for up to 98%" |

**正确表述**：KAN 的优势是**参数效率**（更少参数达到相当精度）

---

## 5. CNN/Transformer/RNN 架构对比（R3-4/R4-7）

| 论文 | 发现 | 支撑声称 |
|------|------|----------|
| Yin 2017 CNN vs RNN | CNN O(1) vs RNN O(n) | CNN 效率证据 |
| Bai 2018 TCN | 膨胀卷积实现更长记忆 | CNN 用于序列 |
| Rather 2025 KAN-GRU | KAN-GRU > LSTM/GRU/LSTM-Attention/LSTM-Transformer | KAN+GRU 混合优于 Transformer |

### ⚠️ RNN vs 1D-CNN - 必须删除此声称

| 论文 | 发现 |
|------|------|
| Saha 2026 | 1D-CNN 比 LSTM 快 74x |
| Bian 2025 | CNN 比 DeepConvLSTM 少 43.3x 参数 |

---

## 6. 漂移补偿背景

| 方法 | 论文 | 发现 |
|------|------|------|
| TDACNN | Zhang 2022 | 目标域无关 CNN 用于漂移 |
| 知识蒸馏 | Lin 2025 | 首个漂移补偿知识蒸馏 |
| DCT-CNN | Badawi 2020 | DCT 域因果 CNN 用于化学传感器漂移 |
| EEMD-GRNN | Shi 2022 | 95.64%→98.00% 位移精度 |
| FET 漂移 | Margarit-Taulé 2022 | DNN 实现 73% RMSE 降低 |
| WH 传感器 | Willemstein 2023 | 传感器补偿直接证据 |
| SAD-CNN | Heng 2025 | 半监督对抗域适应；电化学传感器漂移 |
| **Wiener自标定 (R85)** | van Meer 2025 | Hall传感器Wiener系统自标定；**2.6x RMS误差降低** |
| **LSTM迁移学习 (R85)** | Niu 2022 | LSTM用于Wiener-H系统，**10-50%学习加速** |

---

## 7. 审稿人回复映射

| 审稿意见 | 支撑文献 | 行动 |
|----------|----------|------|
| R3-4/R4-7 对比有限 | Yin 2017, Bai TCN, Rather 2025 | CNN/GRU-KAN/Transformer 架构对比 |
| R3-5 RVTDCNN | **未找到** | **移除此主张** |
| R3-6 数据集构建 | Xu&Wang 2008, Schoukens 2017 | 已支撑 |
| R4-1 激活函数 | Liu 2024, Dong 2024 | 已支撑 |
| R4-8 计算成本 | KANtize, LUT-KAN, IoT KAN | 已支持；移除 RNN vs CNN |

---

## 8. 已废弃主张

| 声明 | 行动 |
|------|------|
| PIKAN 物理约束 | 从论文删除 |
| FRIRNN 频率注入 | 从论文删除 |
| RNN vs 1D-CNN 效率 | **冲突，必须删除** |
| KAN 计算效率 > LSTM/GRU | **无支撑，必须删除** |

---

## 分析报告追溯

| 轮次 | 关键分析 |
|------|----------|
| R99 | STEP3 R99确认完成，文档状态更新 |
| R101 | STEP3 R101最终完成，根目录清理(-p→logs/temp/) |
| R88 | 文献库全部核实完毕；Bruder 2019排除(领域不匹配) |
| R85 | van Meer Hall传感器Wiener自标定(2.6x改善)、Niu LSTM迁移学习(10-50%加速)、GRAU/BitLogic LUT效率完善 |
| R83 | GRAU (>90% LUT减少), BitLogic (<20ns推理) - KAN LUT效率证据链完善 |
| R73 | 5条目排除；文献库最终收尾 |
| R70 | CKAN效率冲突归档；MEASUREMENT目标达成 |
| R53 | KAN+RNN混合新证据；Wiener模型新进展 |
| R52 | Wiener模型新进展；频域损失新验证 |
| R49 | PolyKAN、lmKAN效率证据 |
| R35 | DCT-Based Causal CNN化学传感器漂移 |
| R31 | HiPPO-KAN、Somvanshi KAN Survey最终确认 |
| R28 | PETSA（ICML 2025）、Rodriguez-Linares |
| R27 | GNIO门控神经网络；7篇排除 |
| R26 | 130+篇已验证，理论框架完善 |
| R25 | OLMA最强AFMAE支撑（熵减定理） |
| R24 | MEASUREMENT期刊；频域损失 |
| R23 | KAN效率新进展 |
| R21 | Wiener分数阶H-W；KAN效率 |
| R20 | KAN Wiener等价；Wiener函数滤波器 |
| R19 | KAN-HAR、KFS、TSKANMixer |
| R18 | FIRE、HiPPO-KAN、P-KAN |
| R17 | FreST损失、Subich双重惩罚 |
| R16 | KAN频谱偏差；随机Wiener理论 |
| R15 | KAN收敛；时间序列应用 |
| R14 | KAT验证；SKANODEs |
| R11 | KANtize、QuantKAN |
| R7 | Wiener传感器文献；AFMAE理论链 |
| R5 | RNN_CNN_Efficiency_Conflict |
| Deep | 初始深度分析 |

## 引用文档

- `docs/research/literature/verified_literature.md` (STEP2 R94)
- `docs/research/literature/excluded_literature.md` (STEP2 R94)
- `docs/IDEA.md`
- `docs/FRIKAN_REJECT.md`
- `docs/research/literature/key_references.md` (STEP3 R101)
