# 文献调研总结

**状态**: STEP3 最终确认 (2026-03-29)
**基于**: STEP2 R66 最终分析（66轮系统性分析）
**阶段**: 理论框架就绪，可进入论文撰写阶段

---

## 概述

MET 非线性项目（Wiener-KAN 用于频率响应漂移补偿）的文献调研已完成。

## 核心文献清单

| 文档 | 状态 | 说明 |
|------|------|------|
| key_references.md | **STEP3** | 核心文献清单，支撑论文声称 |
| theory_framework.md | **STEP3** | 理论框架，整合所有支撑 |
| paper_draft_segments.md | **STEP3** | 可直接使用的论文草稿段落 |
| verified_literature.md | **STEP2 R66** | 已验证文献详细记录 |

## 审稿人回复映射

| 审稿意见 | 支撑文献 | 行动 |
|----------|----------|------|
| R3-4/R4-7 对比有限 | Yin 2017, Bai TCN, Rather 2025 | CNN/GRU-KAN/Transformer 架构对比 |
| R3-5 RVTDCNN | **未找到** | **移除此主张** |
| R3-6 数据集 | Xu&Wang 2008, Schoukens 2017 | 已支持 |
| R4-1 激活函数 | Liu 2024, Dong 2024 | 已支持 |
| R4-8 计算成本 | KANtize, LUT-KAN, IoT KAN | 已支持 |

## 第二稿主张状态

| 主张 | 状态 | 文献 |
|------|------|------|
| Wiener-KAN 架构 | **已支持** | Cruz SS-KAN, TFKAN |
| KAN+RNN 混合 | **已支持** | Rather 2025, TKAN |
| KAN 参数效率 | **已支持** | Vacca-Rubio 2024 (109k vs 329k) |
| AFMAE 频域损失 | **强支持** | OLMA, Subich, FreDF, PETSA |
| KAN LUT 效率 | **已支持** | KANtize, LUT-KAN, PolyKAN, lmKAN |
| 漂移补偿 | **已支持** | Zhang, Lin, Shi, Badawi DCT-CNN, Heng SAD-CNN |
| **RNN vs 1D-CNN 效率** | **⚠️ 冲突** | **必须删除** |
| **KAN 计算效率 vs LSTM/GRU** | **⚠️ 无支撑** | **必须修正为参数效率** |

## ⚠️ 关键冲突（必须处理）

### 冲突 1：RNN vs 1D-CNN 效率
- Saha 2026：1D-CNN 比 LSTM 快 74 倍
- Bian 2025：CNN 比 DeepConvLSTM 少 43.3x 参数
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

## MEASUREMENT 期刊目标

**目标**: 50 篇 | **达成**: 85 篇 ✅

## 引用文档

- `docs/research/literature/verified_literature.md` (STEP2 R66)
- `docs/research/literature/key_references.md` (STEP3)
- `docs/research/literature/theory_framework.md` (STEP3)
- `docs/research/literature/paper_draft_segments.md` (STEP3)
- `docs/IDEA.md`
- `docs/FRIKAN_REJECT.md`

**STEP3 最终确认**: 文献调研完备，理论框架就绪，可进入论文撰写阶段
