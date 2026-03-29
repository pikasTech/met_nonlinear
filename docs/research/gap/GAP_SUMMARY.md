# GAP 支撑汇总

***状态***: 更新 (2026-03-29)
***目的***: 为论文的11个GAP提供文献支撑

## 11个GAP定义

| GAP编号 | GAP主题 | 核心声称 | 支撑状态 |
|---------|---------|---------|---------|
| GAP1 | 电化学地震检波器频响漂移 | 需要引用温度漂移研究，支撑从温度漂移到非线性漂移的GAP | 待支撑 |
| GAP2 | 非频率漂移研究（线性度） | 线性度的测量范围偏窄，已有文献已充分支撑 | 已支撑 |
| GAP3 | 频率漂移研究（震级因素） | 现有研究只关注温度，缺乏震级因素的影响研究 | 待支撑 |
| GAP4 | 非频率漂移建模 | 推导了电化学地震检波器的线性模型，而没有非线性模型 | 待支撑 |
| GAP5 | 频率漂移建模（震级因素） | 建模了温度因素，没有建模震级因素对频率漂移的影响 | 待支撑 |
| GAP6 | 前馈vs反馈补偿（量程限制） | 力反馈限制量程，前馈无此限制 | 待支撑 |
| GAP7 | 前馈补偿利用非线性区 | 前馈方法利用而非排除非线性，可提升量程 | 待支撑 |
| GAP8 | 频率相关补偿vs频率无关 | 支撑频率相关的补偿能力，补偿精度 | 待支撑 |
| GAP9 | 频率相关补偿（计算效率） | 支撑计算效率的提升 | 待支撑 |
| GAP10 | AFMAE vs 纯MAE | 支撑AFMAE损失函数的改进 | 待支撑 |
| GAP11 | AFMAE vs 其他频域损失 | 支撑AFMAE的效率改进和简单性（直接计算能量，无需FFT） | 待支撑 |

## GAP支撑矩阵

| GAP编号 | 核心文献 | 支撑内容 | 来源 |
|---------|---------|---------|------|
| GAP1 | Iqbal 2024 | 电化学传感器Volterra系统分析 | verified_literature.md:L440 |
| GAP1 | Xu & Wang 2008 | 传感器块模型的Volterra级数 | verified_literature.md:L812 |
| GAP1 | Lin et al. 2020 | 电化学地震传感器温度性能 | verified_literature.md:L1316 |
| GAP2 | (已有文献支撑) | 线性度测量范围偏窄 | - |
| GAP3 | 待补充 | 震级因素对频率漂移的影响 | - |
| GAP4 | Iqbal 2024 | 电化学传感器非线性分析 | verified_literature.md:L440 |
| GAP4 | Xu & Wang 2008 | 块模型中非线性动态特性 | verified_literature.md:L812 |
| GAP5 | 待补充 | 温度vs震级建模对比 | - |
| GAP6 | Fang et al. 2024 | 利用非线性提高灵敏度 | verified_literature.md:L1201 |
| GAP6 | Wiener-Hammerstein相关文献 | 反馈补偿的局限性 | 待整理 |
| GAP7 | Fang et al. 2024 | 利用非线性优于抑制非线性 | verified_literature.md:L1201 |
| GAP8 | FreDF (Wang 2025 ICLR) | 频率相关补偿精度优势 | verified_literature.md:L552 |
| GAP8 | FIRE (He 2025) | FFT损失有效性 | verified_literature.md:L560 |
| GAP9 | PolyKAN, lmKAN | KAN LUT计算效率 | verified_literature.md:L351-373 |
| GAP9 | GRAU, BitLogic | LUT硬件实现效率 | verified_literature.md:L1097-1119 |
| GAP10 | FreDF (Wang 2025) | AFMAE直接理论 | verified_literature.md:L552 |
| GAP10 | OLMA (Shi 2025) | 频域损失熵减原理 | verified_literature.md:L1022 |
| GAP11 | FreDF, FIRE, OLMA, SATL | 其他频域损失需要FFT | verified_literature.md |
| GAP11 | AFMAE | 直接计算能量，无需FFT | 待实现 |

## 下一步工作

1. 为每个GAP创建单独的支撑文档
2. 识别GAP支撑缺口
3. 更新GAP支撑矩阵
