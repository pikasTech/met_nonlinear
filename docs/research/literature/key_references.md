# 核心参考文献

**状态**: STEP3 最终确认 (2026-03-29)
**基于**: verified_literature.md (STEP2 R66)
**原则**: 短而精，仅保留能直接支撑论文声称的核心文献

---

## 审稿意见回应映射

| 审稿意见 | 支撑文献 | 行动 |
|----------|----------|------|
| R3-4/R4-7 对比有限 | Yin 2017, Bai TCN, Rather 2025 | CNN/GRU-KAN/Transformer 架构对比 |
| R3-5 RVTDCNN | **未找到** | **移除此主张** |
| R3-6 数据集构建 | Xu&Wang 2008, Schoukens 2017 | 已支持 |
| R4-1 激活函数 | Liu 2024 KAN, Dong 2024 | 已支持 |
| R4-8 计算成本 | KANtize, LUT-KAN, IoT KAN | 已支持；移除 RNN vs CNN |

---

## P0 - Wiener-KAN 架构

| 论文 | 核心贡献 | 支撑声称 |
|------|----------|----------|
| Cruz 2025 SS-KAN | 线性状态空间 + KAN 非线性 | **直接基础**: Wiener 线性 ↔ RNN，Wiener 非线性 ↔ KAN |
| Liu 2024 KAN | B 样条激活，LUT 计算 | KAN 替换 Wiener 静态非线性 |
| Kui 2025 TFKAN | 首个频域 KAN；双分支 FreqKAN + TimeKAN | **直接支持**: Wiener 线性↔非线性分离 |
| Schoukens 2009 WH 基准 | G1(z)→f(·)→G2(z) | **经典基础** |
| Haber 1990 结构识别 | "Wiener = 线性动态 + 静态非线性" | **核心理论** |

---

## P0 - KAN+RNN 混合有效性

| 论文 | 核心贡献 | 支撑声称 |
|------|----------|----------|
| Rather 2025 KAN-GRU | GRU-KAN/LSTM-KAN 混合 | **混合 > LSTM/GRU/LSTM-Attention/LSTM-Transformer** |
| Genet 2024 TKAN | KAN + LSTM 门控记忆 | TKAN > GRU > LSTM 多步预测 |
| Somvanshi 2025 KAN 综述 | KAN+RNN 集成是增长趋势 | **验证 Wiener-KAN 方法** |

---

## P0 - CNN/Transformer/RNN 架构对比（R3-4/R4-7）

| 论文 | 核心贡献 | 支撑声称 |
|------|----------|----------|
| Yin 2017 CNN vs RNN | CNN 实现 O(1) 顺序复杂度 vs RNN O(n) | **CNN 效率证据** |
| Bai 2018 TCN | 膨胀卷积实现更长记忆；CNN 在音频合成上优于 LSTM | CNN 用于序列建模 |
| Rather 2025 KAN-GRU | GRU-KAN > LSTM/GRU/LSTM-Attention/LSTM-Transformer | **KAN+GRU 混合优于 Transformer** |

---

## P0 - AFMAE 频域损失

| 论文 | 核心贡献 | 支撑声称 |
|------|----------|----------|
| **Shi 2025 OLMA (ICLR 2026)** | 熵减定理：酉变换降低边缘熵 | **最强 AFMAE 支撑** |
| **Subich 2025 (ICML)** | MSE 导致"双惩罚"效应 | **直接解释时域 MSE 不足** |
| Wang 2025 FreDF (ICLR) | L^α = α·\|F(Ŷ)-F(Y)\|₁ + (1-α)·MSE | **直接公式匹配 AFMAE** |
| Wu 2025 KFS | ℒ = αℒ_F + (1-α)ℒ_MSE + Parseval 定理 | **完整频域损失匹配 AFMAE** |
| **Medeiros 2025 PETSA (ICML)** | 频域项保持周期性 | **AFMAE 多角度验证** |

---

## P0 - KAN LUT 效率（R4-8）

| 论文 | 核心贡献 | 支撑声称 |
|------|----------|----------|
| **Yu 2025 PolyKAN (R49)** | GPU加速1.2-10x推理、1.4-12x训练 | **LUT量化实际部署效率** |
| **Pozdnyakov 2025 lmKAN (R49)** | **6.0x FLOPs减少**；H100 10x吞吐量 | **迄今最具体效率数据** |
| Errabii 2026 KANtize | **50x BitOps 减少**；2.9x GPU 加速 | 量化 LUT 直接证据 |
| Kuznetsov 2026 LUT-KAN | 分段 LUT 量化 | **比基线 KAN 快 12 倍** |
| Kuznetsov 2026 IoT KAN | 边缘 LUT 编译 KAN | **比原始 KAN 快 5000 倍** |

---

## P1 - 漂移补偿

| 论文 | 核心贡献 | 支撑声称 |
|------|----------|----------|
| Zhang 2022 TDACNN | 目标域无关 CNN 传感器漂移 | 深度学习用于漂移补偿 |
| Lin 2025 KD E-nose | 知识蒸馏用于漂移适应 | 迁移学习用于漂移 |
| Badawi 2020 DCT-CNN | DCT 域因果 CNN 用于化学传感器漂移 | **直接支撑传感器漂移补偿** |
| Shi 2022 EEMD-GRNN | EEMD + GRNN；95.64%→98.00% | 完整漂移补偿框架 |
| Willemstein 2023 WH | Wiener-Hammerstein 用于压阻传感器 | **传感器补偿直接证据** |
| Heng 2025 SAD-CNN | 半监督对抗域适应 CNN（电子鼻） | **电化学传感器漂移直接证据** |

---

## P2 - 测量方法论与数据集（R3-6）

| 论文 | 核心贡献 | 支撑声称 |
|------|----------|----------|
| Xu 2008 Volterra/Wiener | 传感器块模型的 Volterra 级数 | **直接 MET 测量方法论** |
| Schoukens 2017 三个基准 | 非线性系统辨识基准数据集 | 数据集构建标准 |
| Champneys 2024 | 5 个非线性系统 ID 基准 + 10 种基线 | **MET 定位比较框架** |

---

## ⚠️ 必须删除的主张

**RNN vs 1D-CNN 效率**：被以下文献**反驳**
- Saha 2026：1D-CNN 比 LSTM 快 74 倍
- Bian 2025：CNN 比 DeepConvLSTM 少 43.3x 参数

**KAN 计算效率 vs LSTM/GRU**：无文献支撑
- FEKAN 2026："KAN remains computationally demanding"
- KANtize 2026："B-spline computation accounts for up to 98%"

**正确表述**：KAN 的优势是**参数效率**（更少参数达到相当精度），而非计算效率。

---

## 第二稿已废弃主张

| 声明 | 行动 |
|------|------|
| ~~PIKAN 物理约束~~ | 删除 |
| ~~FRIRNN 频率注入~~ | 删除 |
| ~~RNN vs 1D-CNN 效率~~ | **冲突，必须删除** |
| ~~KAN 计算效率 vs LSTM/GRU~~ | **无支撑，必须删除** |

---

## 引用文档

- `docs/research/literature/verified_literature.md` (STEP2 R66)
- `docs/research/literature/20260329/STEP2_Round66_Analysis.md`
- `docs/IDEA.md`
- `docs/FRIKAN_REJECT.md`
