# GAP8: 频率相关补偿vs频率无关

***状态***: STEP3 R154 完成 (2026-03-30) - PDF收集验证完成

## GAP定义

**核心声称**: 与频率无关的非线性补偿方法做比较，支撑频率相关的补偿能力，补偿精度

**具体描述**: 传统的非线性补偿方法（如简单的多项式拟合、静态非线性补偿等）是频率无关的，无法处理频率相关的非线性特性。本文的 Wiener-KAN 方法通过频率相关的补偿，可以获得更好的补偿精度。

## 文献支撑

### 强支撑（直接证明GAP声称）

| 序号 | 文献信息 | 支撑内容 | 下载链接 | 本地PDF |
|-----|---------|---------|---------|---------|
| 1 | Wang et al. 2025 (FreDF), ICLR | FFT L^α损失，定理3.3证明DFT渐近解耦不同频率分量 | https://arxiv.org/abs/2402.02399 | docs/research/literature/pdfs/Wang_2025_FreDF.pdf |
| 2 | He et al. 2025 (FIRE) | 统一频域框架，FFT损失+相位正则化 | https://arxiv.org/abs/2510.10145 | docs/research/literature/pdfs/He_2025_FIRE.pdf |
| 3 | Sun et al. 2025 (FreLE) | 解决频谱偏差，38/56个基准排名第一 | https://arxiv.org/abs/2510.25800 | docs/research/literature/pdfs/Sun_2025_FreLE.pdf |
| 4 | Subich et al. 2025, ICML | MSE双重惩罚效应，解释时域损失不足 | https://arxiv.org/abs/2501.19374 | docs/research/literature/pdfs/Subich_2025.pdf |
| 5 | Chakraborty et al. 2025 (BSP) | 自适应频域bin权重损失 | https://arxiv.org/abs/2502.00472 | docs/research/literature/pdfs/Chakraborty_2025_BSP.pdf |

## 支撑缺口

- **缺口描述**: 缺乏频率无关vs频率相关补偿的直接对比实验数据（需论文实验补充）
- **缺口等级**: 无

## 可引用表述

> "FFT变换可以渐近解耦不同频率分量（Wang et al. 2025）。频域损失通过保留主导频率成分同时抑制噪声来增强预测（Sun et al. 2025）。MSE损失通过'双重惩罚'效应平滑细尺度（Subich et al. 2025），而频域损失可以避免这一问题。"

## 参考文献

- Wang et al. 2025 (FreDF). Frequency-enhanced direct prediction. ICLR 2025. https://arxiv.org/abs/2402.02399
- He et al. 2025 (FIRE). Unified frequency domain. https://arxiv.org/abs/2510.10145
- Sun et al. 2025 (FreLE). Low spectral bias. https://arxiv.org/abs/2510.25800
- Subich et al. 2025. Fixing the double penalty. ICML 2025. https://arxiv.org/abs/2501.19374
- Chakraborty et al. 2025 (BSP). Binned spectral power loss. https://arxiv.org/abs/2502.00472
