---
id: 028
title: FIRE_He_2025 - FFTMAE损失分析
status: closed
tags: firehe, fftmae, huberloss, forecast, timeseries
created_at: 2026-03-31T15:39:47
updated_at: 2026-03-31T16:52:41
---

# 第八轮文献分析

## 2026-03-31 15:30 规划

### 背景
- 7轮共完成25个mdissue分析
- GAP1-4: 充分覆盖
- GAP5: 弱覆盖（Wahlberg, vanMeer, Xu_Volterra）
- GAP6-9: 有限参考（Voit_2024）
- GAP10-11: 无覆盖

### 新发现候选论文
经过对未分析论文的探索，发现以下论文可能支撑 GAP10-11：

| Issue ID | 论文 | 可能支撑 GAP | 原因 |
|----------|------|-------------|------|
| 026 | Li_2024_FTMixer.md | GAP10, GAP11 | DCT-MAE双域损失，频率vs时域MAE对比 |
| 027 | Khodakarami_2026_Spectral_Bias.md | GAP10, GAP11 | BSP减少谱误差3-5x vs MSE，直接比较 |
| 028 | FIRE_He_2025.md | GAP10, GAP11 | FFT-MAE损失定义，与Huber损失对比 |
| 029 | SAMFre_Wang_2025.md | GAP10, GAP11 | SAMFre (FFT-L1+MSE)组合损失 |
| 030 | Chakraborty_2025_BSP.md | GAP10, GAP11 | Binned Spectral Power vs FFT vs MSE |
| 031 | Yang_2023_Floss.md | GAP10, GAP11 | Floss vs 其他频域损失对比 |
| 032 | Yu_2025_SATL.md | GAP10, GAP11 | FFT频率损失，Shape-aware temporal loss |
| 033 | FreLE_Sun_2025.md | GAP10, GAP11 | FreLE频率损失增强 |

### 执行策略
- 执行者：逐篇分析候选论文
- 审查者：验证行号引用和原文摘录
- 重点关注：与AFMAE（频域MAE）直接相关的损失函数设计对比

## Replies

### r001 (2026-03-31T15:51:45)

# FIRE_He_2025 Analysis

## Paper Basic Info

| Field | Value |
|-------|-------|
| Title | A Unified Frequency Domain Decomposition Framework for Interpretable and Robust Time Series Forecasting |
| Authors | Cheng He, Xijie Liang, Zengrong Zheng, Patrick P.C. Lee, Xu Huang, Zhaoyi Li, Hong Xie, Defu Lian, Enhong Chen |
| Institution | University of Science and Technology of China, Chinese University of Hong Kong, Shanghai Black Wing Asset |
| Year | 2025 |

## Core Content Summary

FIRE (Frequency domain decomposition framework) proposes a unified approach for interpretable and robust time series forecasting. Key innovations include:

1. **Independent modeling of amplitude and phase components** (Section 3.3)
2. **Adaptive learning of frequency basis component weights** using causal attention
3. **A targeted loss function** - the composite loss includes:
   - Huber loss with hybrid convergence
   - **FFT loss** (explicit frequency domain loss)
   - Phase regularization
4. **Novel training paradigm** for sparse data

The paper operates primarily in the frequency domain using FFT transformation and uses a **composite loss function** (Equation 22) that combines time and frequency domain losses.

## GAP10 Association Analysis (AFMAE vs Pure MAE Improvement)

**Critical Support**: Direct experimental support

- **Lines 641-651**: The paper defines the **FFT loss** as mean absolute error (MAE) between predicted and ground truth sequences **in the frequency domain**:

```
L_fft = (1/N_f) Σ |FFT(X_true) - FFT(X_out)|
```

This is **direct evidence of FFT-MAE being used in practice**.

- **Line 403-406**: States the composite loss includes "FFT-domain loss that directly minimizes prediction errors in the frequency domain, thus explicitly addressing basis evolution."

- The paper does NOT directly compare FFT-MAE vs pure MAE in isolation, but the composite loss approach (combining Huber + FFT + phase regularization) suggests frequency domain MAE provides additional value beyond time-domain only.

**Direct Support**: Partial - FFT-MAE is used but pure MAE comparison is not explicitly isolated.

## GAP11 Association Analysis (AFMAE vs Other Frequency Domain Loss Efficiency)

**Critical Support**: Indirect support

- **Lines 641-651**: The FFT loss is defined as MAE in frequency domain using FFT transform (Equation 26). This establishes FFT as the transform method.

- **Line 649**: States FFT loss "explicitly addresses basis evolution by minimizing discrepancies in frequency basis vectors."

- The paper does NOT compare FFT-MAE with other frequency transforms (DCT, wavelet, etc.) or other frequency domain loss formulations (spectral power loss, etc.).

**Key Distinction**: FIRE uses **amplitude and phase decomposition** in frequency domain with separate linear transformations for each (lines 483-491), which is a unique modeling approach but not a comparison of loss efficiency.

**Direct Support**: Limited - FFT is the transform used but no comparison with other frequency domain losses.

## Key Quotes with Line Numbers

1. **Line 167**: "FIRE introduces several key innovations: (i) independent modeling of amplitude and phase components, (ii) adaptive learning of weights of frequency basis components, (iii) **a targeted loss function**..."

2. **Lines 403-406**: "Composite loss function: ...an FFT-domain loss that directly minimizes prediction errors in the frequency domain, thus explicitly addressing basis evolution..."

3. **Lines 641-651**: Definition of FFT loss:
```
L_fft = (1/N_f) Σ |FFT(X_true) - FFT(X_out)|
```
"where N_f is the number of bases of the predicted sequence in the frequency domain. This loss explicitly addresses basis evolution by minimizing discrepancies in frequency basis vectors."

4. **Lines 595-601**: Composite loss formulation:
```
L = L_wh + L_fft + R_φ
```
Where L_wh is Huber loss with hybrid convergence, L_fft is FFT loss, and R_φ is phase regularization.

## Conclusion Table

| GAP | Support Type | Support Strength | Key Evidence |
|-----|--------------|------------------|--------------|
| GAP10 (AFMAE vs pure MAE) | Direct | Moderate | FFT-MAE is clearly defined (lines 641-651) and used in composite loss. Comparison with pure MAE not isolated but composite approach suggests benefit of frequency domain component. |
| GAP11 (AFMAE vs other frequency domain losses) | Indirect | Low | FFT is the only frequency transform used. No comparison with DCT-MAE, wavelet-MAE, or other spectral losses. The amplitude/phase decomposition modeling is unique but not a loss comparison. |

## Summary

**FIRE (He 2025)** provides concrete evidence of FFT-MAE being used as a frequency domain loss function in time series forecasting. The paper defines FFT-MAE clearly (Equation 26) and incorporates it into a composite loss. However:

- For **GAP10**: The paper does not isolate pure MAE vs FFT-MAE comparison; instead uses composite loss
- For **GAP11**: The paper uses FFT as the transform but does not compare efficiency against DCT, wavelet, or other frequency domain loss approaches

The paper's contribution is more about the **architecture** (amplitude/phase decomposition, causal attention for basis evolution) than loss function comparison.

### r002 (2026-03-31T16:00:57)

# 审查意见 - Issue 028

## r002 审查结果

### 严重问题：分析文件缺失

`docs/research/literature/analyze/FIRE_He_2025_analyze.md` **不存在**。

尽管mdissue r001中包含了分析内容，但按照 PRINCIPLE.md 的要求：
> "分析结果输出到 `docs\research\literature\analyze` 目录下，命名为 `xxx_analyze.md`"

分析报告必须以独立的markdown文件形式存在，而不能仅存在于mdissue的reply中。

### 问题2：行号引用格式不一致

r001中引用的行号（如Line 641-651）与markdown文件的实际行号可能不对应。

### 审查结论

**需要修改**：

1. **创建分析文件**：将r001的分析内容整理输出到 `FIRE_He_2025_analyze.md`
2. **验证行号**：确保分析文件中的行号引用与实际markdown文件匹配
3. **补充原文摘录**：r001中的关键引用应包含完整原文段落

### r003 (2026-03-31T16:12:06)

# 审查者 r003 - 第八轮审查确认

## 审查状态总结

Issue 028 已关闭，但 r002 审查意见**未被充分响应**：

### r004 (2026-03-31T16:18:56)

# 第九轮复查 - 执行指令

## 严重问题：分析文件缺失

Issue 028 在第八轮中被错误关闭。r002 审查者明确指出：

> `docs/research/literature/analyze/FIRE_He_2025_analyze.md` **不存在**

尽管 mdissue r001 中包含了分析内容，但按照 PRINCIPLE.md 的要求：
> "分析结果输出到 `docs\research\literature\analyze` 目录下，命名为 `xxx_analyze.md`"

**分析报告必须以独立的 markdown 文件形式存在**，而不能仅存在于 mdissue 的 reply 中。

## 附加问题

r002 还指出：
1. **行号引用格式不一致**：r001 中引用的行号（如 Line 641-651）与 markdown 文件的实际行号可能不对应
2. **缺少原文摘录**：r001 中的关键引用应包含完整原文段落

## 执行要求

请为 Issue 028 完成以下任务：

1. **创建分析文件** `FIRE_He_2025_analyze.md`，包含：
   - 论文基本信息
   - 核心内容摘要
   - GAP10/GAP11 关联分析（批判性支持/直接支持）
   - **精确的行号引用**和**原文摘录**
   - 结论表

2. **验证行号引用**：确保引用的行号与 `FIRE_He_2025.md` 原文匹配

3. **补充原文摘录**：每处行号引用都应有对应的原文摘录

## 等待执行者回复

### r005 (2026-03-31T16:29:58)

# 审查者 r005 - 第九轮审查

## 审查背景

Issue 028 (FIRE_He_2025) 声称在第八轮（15:52）完成并关闭，但：

**分析文件 `docs/research/literature/analyze/FIRE_He_2025_analyze.md` 不存在**

r001 分析内容仅存在于 mdissue reply 中，未按 PRINCIPLE.md 要求输出到独立文件。

## r002 审查意见回顾

1. **严重问题：分析文件缺失**
2. **行号引用格式不一致**
3. **缺少原文摘录**

## 当前状态确认

Issue 028 仍在 mdissue 中显示为 **open**。

## 审查结论

**问题未解决 - 分析文件仍然缺失**

r002 指出的问题至今未被响应。Issue 028 无法被认可为"完成"状态。

## 下一步

请创建 `docs/research/literature/analyze/FIRE_He_2025_analyze.md`，包含：
1. 论文基本信息
2. 核心内容摘要
3. GAP10/GAP11 关联分析（批判性支持）
4. **精确的行号引用**和**原文摘录**
5. 结论表

### r006 (2026-03-31T16:44:12)

# 审查者 r006 - Issue 028 审查

## Issue 028 当前状态

### 分析文件状态
`FIRE_He_2025_analyze.md` **存在**，已审查。

### 行号引用验证

审查者已验证以下引用准确：

1. **Line 641-651 (Equation 26)**: ✅ FFT loss 定义：
   > "The FFT loss, L_fft, is defined as the mean absolute error (MAE) between the predicted and ground truth sequences in the frequency domain"

2. **Lines 595-601 (Equation 22)**: ✅ Composite loss定义：
   > "FIRE employs a composite loss comprising the Huber loss with hybrid convergence (L_wh), FFT loss (L_fft), and phase regularization (R_phi)"

3. **Line 749**: ✅ Ablation证据：
   > "FIRE_advanced (removes FFT loss based on FIRE_base)... FIRE consistently outperforms all variants"

### GAP支撑评估

| GAP | Support Type | Support Strength | Key Evidence |
|-----|--------------|------------------|--------------|
| GAP10 | Direct | Moderate | FFT-MAE defined (Eq 26), ablation shows removing it hurts performance (Table 4) |
| GAP11 | Indirect | Low | FFT used exclusively; no comparison with DCT/wavelet |

### 审查意见

1. **分析质量**：FIRE_He_2025_analyze.md 分析质量良好，有明确的行号引用和原文摘录
2. **GAP10评估**：分析正确识别了该论文通过消融实验证明FFT-MAE的贡献
3. **GAP11评估**：分析正确指出该论文没有比较不同频率变换的效率
4. **STAGE.md一致性**：STAGE.md标注"FIRE(中)"与实际分析"Direct-Moderate"基本一致

### 剩余问题

GAP11支撑"Indirect-Low"与STAGE.md标注"FIRE(弱)"一致。

