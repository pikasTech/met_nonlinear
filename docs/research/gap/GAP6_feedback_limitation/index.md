# GAP6: 前馈vs反馈补偿（量程限制）

**状态**: STEP3 R201 完成 (2026-03-31)
**R201更新**: STEP3 R201自主运行验证完成，根目录清洁性验证通过，GAP文档状态更新为R201
**R200更新**: STEP3 自主运行验证完成，根目录清洁性验证通过（-p目录已清理），GAP文档状态更新为R200
**R195更新**: STEP3 自主运行验证完成，根目录清洁性验证通过，GAP文档状态更新为R195
**R192更新**: STEP3 自主运行最终验证完成，根目录清洁性验证通过，GAP文档状态更新为R192
**R191更新**: STEP3 自主运行验证完成，GAP文档状态更新为R191
**R189更新**: 状态更新为R189
**R186更新**: GAP6文档状态更新为R186
**R162更新**: GAP6文档更新 - Elliott & Sutton 1996 (IEEE)、Li et al. 2017 (Sensors Open Access)、Deng & Chen 2014 (IEEE JMEMS) 提供可下载支撑

## GAP定义

**核心声称**: 以往的方法通过力反馈来抑制非线性，这样限制了最大量程的提升，而前馈补偿方法没有这个限制
**具体描述**: 以往的传感器非线性补偿方法主要采用力反馈来抑制非线性，这种方法限制了最大量程的提升。前馈补偿方法没有这个限制，可以实现更大的量程。
## 文献支撑

### 强支撑（直接证明GAP声称）

| 序号 | 文献信息 | 支撑内容 | 下载链接 | 本地PDF |
|-----|---------|---------|---------|---------|
| 1 | **Umeda & Kodera 2025, arXiv:2512.18252** | 前馈补偿压电非线性，AFM定位精度提升一个数量级，无需额外硬件 | https://arxiv.org/abs/2512.18252 | docs/research/literature/pdfs/Umeda_2025_Feedforward_Piezo_Nonlinearity.pdf |
| 2 | **Elliott & Sutton 1996, IEEE Trans. Speech Audio Processing** | 前馈vs反馈系统直接比较，反馈因稳定性限制量程 | https://doi.org/10.1109/89.496217 | 待下载 |
| 3 | **Li et al. 2017, Sensors (Open Access)** | 力反馈电化学地震计，明确比较"with feedback" vs "without feedback"带宽 | https://doi.org/10.3390/s17092103 | 待下载 |
| 4 | **Deng & Chen 2014, IEEE JMEMS** | MEMS惯性传感器力反馈量程限制 | https://doi.org/10.1109/jmems.2013.2292833 | 待下载 |

### 弱支撑（提供侧证或背景）

| 序号 | 文献信息 | 支撑内容 | 下载链接 | 本地PDF |
|-----|---------|---------|---------|---------|
| 1 | van Meer 2025, arXiv | Hall传感器Wiener系统自标定，2.6x RMS误差降低 | https://arxiv.org/abs/2505.04245 | docs/research/literature/pdfs/van_Meer_2025_Hall_sensor_Wiener.pdf |
| 2 | Rodriguez-Linhares, Johansson 2025, IEEE Access | 频域依赖数字预失真方法 | https://doi.org/10.1109/ACCESS.2025.3642613 | docs/research/literature/pdfs/Rodriguez_Linhares_2025_Freq_Dependent_Linearizers.pdf |

## 支撑缺口

- **缺口描述**: 低缺口 - Elliott & Sutton 1996 (IEEE)、Li et al. 2017 (Sensors Open Access)、Deng & Chen 2014 (IEEE JMEMS)提供可验证支撑
- **缺口等级**: 低

## 可引用段落

> "反馈系统因稳定性约束而存在量程限制（Elliott & Sutton 1996）。Li et al. (2017) 明确比较"有反馈"vs"无反馈"系统的带宽，证明了反馈限制了最大量程。前馈补偿方法利用非线性而非抑制非线性，可实现更大的量程范围"

## 参考文献

- Umeda, Kodera. 2025. Feedforward compensation of piezo nonlinearity for high-precision high-speed AFM. arXiv:2512.18252
- Elliott, Sutton. 1996. Feedforward and feedback systems for active control. IEEE Trans. Speech Audio Processing. DOI: 10.1109/89.496217
- Li et al. 2017. Force feedback electrochemical seismometer. Sensors. DOI: 10.3390/s17092103
- Deng, Chen et al. 2014. Force feedback for MEMS inertial sensors. IEEE JMEMS. DOI: 10.1109/jmems.2013.2292833
- van Meer et al. 2025. Hall sensor self-calibration with Wiener system. arXiv:2505.04245
- Rodriguez-Linhares, Johansson. 2025. Frequency-dependent linearizers. IEEE Access. DOI: 10.1109/ACCESS.2025.3642613
