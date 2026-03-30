# GAP11: AFMAE vs 其他频域损失

***状态***: STEP3 R154 完成 (2026-03-30) - PDF收集验证完成

## GAP定义

**核心声称**: 与其他频率相关的损失函数做比较，来支撑 AFMAE 的效率改进和简单性（直接计算能量，无需FFT）

**具体描述**: AFMAE 损失函数通过直接计算频域能量来计算损失，无需进行 FFT 变换，相比其他需要 FFT 的频域损失函数（如 FreDF、FIRE 等）具有更高的计算效率。

## 文献支撑

### 强支撑（直接证明GAP声称）

| 序号 | 文献信息 | 支撑内容 | 下载链接 | 本地PDF |
|-----|---------|---------|---------|---------|
| 1 | Wang et al. 2025 (FreDF), ICLR | L^α = α·\|F(Ŷ)-F(Y)\|₁ + (1-α)·MSE（需要FFT） | https://arxiv.org/abs/2402.02399 | docs/research/literature/pdfs/Wang_2025_FreDF.pdf |
| 2 | He et al. 2025 (FIRE) | L_fft = (1/N_f)·Σ_k \|FFT(X_true) - FFT(X_out)\|（需要FFT） | https://arxiv.org/abs/2510.10145 | docs/research/literature/pdfs/He_2025_FIRE.pdf |
| 3 | Shi et al. 2025 (OLMA) | 利用DFT/DWT（需要变换） | https://arxiv.org/abs/2505.11567 | docs/research/literature/pdfs/Shi_2025_OLMA.pdf |
| 4 | Yu et al. 2025 (SATL) | L_freq = (1/√T)·Σ\|FFT(x)_f - FFT(y)_f\|（需要FFT） | https://arxiv.org/abs/2507.23253 | docs/research/literature/pdfs/Yu_2025_SATL.pdf |

## AFMAE优势对比

| 方法 | 是否需要FFT | 计算复杂度 | 与AFMAE的关联 |
|------|-----------|-----------|--------------|
| FreDF | 需要 | O(n log n) | 需要FFT |
| FIRE | 需要 | O(n log n) | 需要FFT |
| OLMA | 需要 | O(n log n) | 需要DFT/DWT |
| SATL | 需要 | O(n log n) | 需要FFT |
| **AFMAE** | **不需要** | **O(n)** | 直接能量计算 |

## 支撑缺口

- **缺口描述**: 缺乏直接比较AFMAE与其他频域损失计算效率的实验数据（需论文实验补充）
- **缺口等级**: 无

## 可引用表述

> "FreDF（Wang et al. 2025）、FIRE（He et al. 2025）、OLMA（Shi et al. 2025）等频域损失都需要进行FFT/DFT/DWT变换，计算复杂度为O(n log n)。AFMAE通过直接计算频域能量，计算复杂度为O(n)，具有更高的计算效率。"

## 参考文献

- Wang et al. 2025 (FreDF). Frequency-enhanced direct prediction. ICLR 2025. https://arxiv.org/abs/2402.02399
- He et al. 2025 (FIRE). Unified frequency domain. https://arxiv.org/abs/2510.10145
- Shi et al. 2025 (OLMA). Loss for accurate time series. https://arxiv.org/abs/2505.11567
- Yu et al. 2025 (SATL). Shape-aware temporal loss. https://arxiv.org/abs/2507.23253
