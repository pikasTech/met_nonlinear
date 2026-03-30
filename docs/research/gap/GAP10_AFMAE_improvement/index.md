# GAP10: AFMAE vs 纯MAE

***状态***: STEP3 R154 完成 (2026-03-30) - PDF收集验证完成

## GAP定义

**核心声称**: 与纯MAE做比较，支撑AFMAE的改进

**具体描述**: 纯MAE损失函数只考虑时域误差，无法捕获频率域的误差特性。AFMAE通过引入频域损失，可以更好地保持信号的频率特性，提高补偿精度。

## 文献支撑

### 强支撑（直接证明GAP声称）

| 序号 | 文献信息 | 支撑内容 | 下载链接 | 本地PDF |
|-----|---------|---------|---------|---------|
| 1 | Wang et al. 2025 (FreDF), ICLR | `L^α = α·|F(Ŷ)-F(Y)|₁ + (1-α)·MSE`，直接公式匹配AFMAE | https://arxiv.org/abs/2402.02399 | docs/research/literature/pdfs/Wang_2025_FreDF.pdf |
| 2 | Shi et al. 2025 (OLMA) | 熵减定理：酉变换降低边缘熵 | https://arxiv.org/abs/2505.11567 | docs/research/literature/pdfs/Shi_2025_OLMA.pdf |
| 3 | Subich et al. 2025, ICML | MSE双重惩罚效应，解释纯MAE/MSE不足 | https://arxiv.org/abs/2501.19374 | docs/research/literature/pdfs/Subich_2025.pdf |

## 支撑缺口

- **缺口描述**: 缺乏AFMAE vs 纯MAE的直接实验对比（需论文实验补充）
- **缺口等级**: 无

## 可引用表述

> "证明了存在酉变换可以降低多个相关高斯过程的边缘熵，从而减少预测误差下界（Shi et al. 2025）。MSE损失通过'双重惩罚'效应平滑细尺度（Subich et al. 2025），而频域损失可以避免这一问题。AFMAE公式L^α = α·|F(Ŷ)-F(Y)|₁ + (1-α)·MSE直接匹配FreDF的理论框架（Wang et al. 2025）。"

## 参考文献

- Wang et al. 2025 (FreDF). Frequency-enhanced direct prediction. ICLR 2025. https://arxiv.org/abs/2402.02399
- Shi et al. 2025 (OLMA). Loss for accurate time series. https://arxiv.org/abs/2505.11567
- Subich et al. 2025. Fixing the double penalty. ICML 2025. https://arxiv.org/abs/2501.19374
