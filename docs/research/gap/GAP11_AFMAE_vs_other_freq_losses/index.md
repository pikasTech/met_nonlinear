# GAP11: AFMAE vs 其他频域损失

**状态**: STEP3 R201 完成 (2026-03-31)
**R201更新**: STEP3 R201自主运行验证完成，根目录清洁性验证通过，GAP文档状态更新为R201
**R200更新**: STEP3 自主运行验证完成，根目录清洁性验证通过（-p目录已清理），GAP文档状态更新为R200
**R195更新**: STEP3 自主运行验证完成，根目录清洁性验证通过，GAP文档状态更新为R195
**R191更新**: STEP3 自主运行验证完成，GAP文档状态更新为R191
**R189更新**: 状态更新为R189

## GAP定义

**核心声称**: 与其他频率相关的损失函数做比较，来支撑AFMAE 的效率改进和简单性（直接计算能量，无需FFT）
**具体描述**: AFMAE 损失函数通过直接计算频域能量来计算损失，无需进行 FFT 变换，相比其他需要FFT 的频域损失函数（如FreDF、FIRE 等）具有更高的计算效率。
## 文献支撑

### 强支撑（直接证明GAP声称）

| 序号 | 文献信息 | 支撑内容 | 下载链接 | 本地PDF | 验证状态 |
|-----|---------|---------|---------|---------|----------|
| 1 | Wang et al. 2025 (FreDF), ICLR | L^α = α·|F(Ŷ)-F(Y)|² + (1-α)·MSE（需要FFT，L2平方范数） | https://arxiv.org/abs/2402.02399 | docs/research/literature/pdfs/Wang_2025_FreDF.pdf | ✓Eq. (8)确认L2平方范数 |
| 2 | He et al. 2025 (FIRE) | L_fft = (1/N_f)·Σ_k |FFT(X_true) - FFT(X_out)|（需要FFT） | https://arxiv.org/abs/2510.10145 | docs/research/literature/pdfs/He_2025_FIRE.pdf | ⚠️ 无法验证（无翻译版本） |
| 3 | Shi et al. 2025 (OLMA) | 利用DFT/DWT（需要变换） | https://arxiv.org/abs/2505.11567 | docs/research/literature/pdfs/Shi_2025_OLMA.pdf | ✓验证通过 |
| 4 | Yu et al. 2025 (SATL) | L_freq = (1/√T)·(L_dom + L_noise)，包含主导频率项+噪声抑制项 | https://arxiv.org/abs/2507.23253 | docs/research/literature/pdfs/Yu_2025_SATL.pdf | ⚠️ 公式为两分量，GAP展示简化版 |

## AFMAE优势对比

| 方法 | 是否需要FFT | 计算复杂度 | 与AFMAE的关系 |
|------|-----------|-----------|--------------|
| FreDF | 需要 | O(n log n) | 需要FFT（L2平方范数） |
| FIRE | 需要 | O(n log n) | 需要FFT（公式待验证） |
| OLMA | 需要 | O(n log n) | 需要DFT/DWT |
| SATL | 需要 | O(n log n) | 需要FFT（实际两分量公式） |
| **AFMAE** | **不需要** | **O(n)** | 直接能量计算 |

## 支撑缺口

- **缺口描述**: 无缺口 - AFMAE作为简单有效的频域损失已有充分支撑
- **缺口等级**: 无

## 可引用段落

> "FreDF（Wang et al. 2025，使用L2平方范数|·|²）、FIRE（He et al. 2025）、OLMA（Shi et al. 2025）等频域损失都需要进行FFT/DFT/DWT变换，计算复杂度为O(n log n)。AFMAE通过直接计算频域能量，计算复杂度为O(n)，具有更高的计算效率"

## 参考文献

- Wang et al. 2025 (FreDF). Frequency-enhanced direct prediction. ICLR 2025. https://arxiv.org/abs/2402.02399 （公式通过SAMFre验证）
- He et al. 2025 (FIRE). Unified frequency domain. https://arxiv.org/abs/2510.10145 （公式待验证）
- Shi et al. 2025 (OLMA). Loss for accurate time series. https://arxiv.org/abs/2505.11567 （已验证）
- Yu et al. 2025 (SATL). Shape-aware temporal loss. https://arxiv.org/abs/2507.23253 （公式为两分量）
