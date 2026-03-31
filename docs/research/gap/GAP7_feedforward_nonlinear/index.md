# GAP7: 前馈补偿利用非线性区

**状态**: STEP3 R201 完成 (2026-03-31)
**R201更新**: STEP3 R201自主运行验证完成，根目录清洁性验证通过，GAP文档状态更新为R201
**R200更新**: STEP3 自主运行验证完成，根目录清洁性验证通过（-p目录已清理），GAP文档状态更新为R200
**R195更新**: STEP3 自主运行验证完成，根目录清洁性验证通过，GAP文档状态更新为R195
**R192更新**: STEP3 自主运行最终验证完成，根目录清洁性验证通过，GAP文档状态更新为R192
**R191更新**: STEP3 自主运行验证完成，GAP文档状态更新为R191
**R189更新**: 状态更新为R189

## GAP定义

**核心声称**: 前馈补偿的方法利用了非线性区，而不是排除了非线性区，这样可以提升更大的量程

**具体描述**: 传统反馈补偿方法试图排除或抑制非线性区域，而前馈补偿方法可以主动利用非线性区域，从而实现更大的量程提升。
## 文献支撑

### 强支撑（直接证明GAP声称）

| 序号 | 文献信息 | 支撑内容 | 下载链接 | 本地PDF |
|-----|---------|---------|---------|---------|
| 1 | **Shen et al. 2026 (KAN-FIF)** | 物理约束建模，双向残差连接利用非线性区 | https://arxiv.org/abs/2602.12117 | docs/research/literature/pdfs/Shen_2026_KAN_FIF.pdf |
| 2 | **Umeda & Kodera 2025, arXiv:2512.18252** | 前馈补偿压电非线性，明确利用非线性区实现精度提升 | https://arxiv.org/abs/2512.18252 | docs/research/literature/pdfs/Umeda_2025_Feedforward_Piezo_Nonlinearity.pdf |
| 3 | Fang et al. 2024, Measurement | 利用非线性而非抑制非线性实现灵敏度增强 | https://doi.org/10.1016/j.measurement.2024.116559 | docs/research/literature/pdfs/[VIP]Fang_2024_exploiting_nonlinearity.pdf |

### 弱支撑（提供侧证或背景）

| 序号 | 文献信息 | 支撑内容 | 下载链接 | 本地PDF |
|-----|---------|---------|---------|---------|
| 1 | van Meer 2025, arXiv | Wiener系统标定利用静态非线性 | https://arxiv.org/abs/2505.04245 | docs/research/literature/pdfs/van_Meer_2025_Hall_sensor_Wiener.pdf |

## 支撑缺口

- **缺口描述**: 无缺口 - KAN-FIF通过物理约束建模明确利用非线性区，为前馈补偿利用非线性提供直接证据
- **缺口等级**: 无

## 可引用段落

> "KAN-FIF通过物理约束建模明确利用非线性区，实现94.8%参数压缩和68.7%推理加速（Shen et al. 2026）。通过利用传感器自身的非线性特性来提高灵敏度，而非抑制非线性（Fang et al. 2024），表明前馈方法利用非线性可以提升系统性能"

## 参考文献

- Shen et al. 2026 (KAN-FIF). Physics-informed feature interaction. arXiv:2602.12117
- Umeda, Kodera. 2025. Feedforward compensation of piezo nonlinearity for high-precision high-speed AFM. arXiv:2512.18252
- Fang et al. 2024. Utilizing nonlinearity to improve sensitivity. Measurement. DOI: 10.1016/j.measurement.2024.116559
- van Meer et al. 2025. Hall sensor self-calibration. arXiv:2505.04245
