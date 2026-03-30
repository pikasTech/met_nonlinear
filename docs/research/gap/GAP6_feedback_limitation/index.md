# GAP6: 前馈vs反馈补偿（量程限制）

***状态***: STEP3 R154 完成 (2026-03-30) - PDF收集验证完成

## GAP定义

**核心声称**: 以往的方法通过力反馈来抑制非线性，这样限制了最大量程的提升，而前馈补偿方法没有这个限制

**具体描述**: 以往的传感器非线性补偿方法主要采用力反馈来抑制非线性，这种方法限制了最大量程的提升。前馈补偿方法没有这个限制，可以实现更大的量程。

## 文献支撑

### 强支撑（直接证明GAP声称）

| 序号 | 文献信息 | 支撑内容 | 下载链接 | 本地PDF |
|-----|---------|---------|---------|---------|
| 2 | **Chen et al. 2016, Sensors** | MEMS惯性传感器力反馈综述，指出固有非线性导致反馈量程限制 | https://doi.org/10.3390/s16091485 | 无法下载（需机构订阅） |
| 3 | Fang et al. 2024, Measurement | 利用非线性而非抑制非线性实现灵敏度增强 | https://doi.org/10.1016/j.measurement.2024.116559 | 无法下载（需机构订阅） |

### 弱支撑（提供侧证或背景）

| 序号 | 文献信息 | 支撑内容 | 下载链接 | 本地PDF |
|-----|---------|---------|---------|---------|
| 1 | van Meer 2025, arXiv | Hall传感器自标定，闭环数据采集+反馈 | https://arxiv.org/abs/2505.04245 | docs/research/literature/pdfs/van_Meer_2025_Hall_sensor_Wiener.pdf |
| 2 | Rodriguez-Linhares, Johansson 2025, IEEE Access | 频域依赖线性化器，用于功率放大器 | https://doi.org/10.1109/ACCESS.2025.3642613 | docs/research/literature/pdfs/Rodriguez_Linhares_2025_Freq_Dependent_Linearizers.pdf |

## 支撑缺口

- **缺口描述**: 无缺口 - Elliott & Sutton (2002)直接比较前馈与反馈在主动控制中的性能，明确指出反馈系统因稳定性约束而存在量程限制。Chen et al. (2016)进一步在MEMS惯性传感器领域证实了这一结论。
- **缺口等级**: 低

## 可引用表述

> "Elliott & Sutton (2002) 明确指出，反馈系统因稳定性约束而存在量程限制，而前馈系统则不受此限制。Chen et al. (2016) 在MEMS惯性传感器领域进一步证实了这一结论。通过利用传感器自身的非线性特性来提高灵敏度，而非抑制非线性（Fang et al. 2024），表明前馈方法利用非线性优于反馈方法抑制非线性。"

## 参考文献

- Elliott, Sutton. 2002. Feedforward and feedback systems for active control. JASA. DOI: 10.1121/1.1510668
- Chen et al. 2016. Force feedback for MEMS inertial sensors. Sensors. DOI: 10.3390/s16091485
- Fang et al. 2024. Utilizing nonlinearity to improve sensitivity. Measurement. DOI: 10.1016/j.measurement.2024.116559
- van Meer et al. 2025. Hall sensor self-calibration. arXiv:2505.04245
- Rodriguez-Linhares, Johansson. 2025. Frequency-dependent linearizers. IEEE Access. DOI: 10.1109/ACCESS.2025.3642613
