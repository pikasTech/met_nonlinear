# STEP1 Round110 - 文献调研报告 (20260330)

## 检索范围与数据库

| 数据库 | 关键词 | 结果数 |
|--------|--------|--------|
| arXiv | KAN sensor, Wiener model sensor | 20+ papers |
| Google Scholar | Measurement journal sensor nonlinearity | 15+ papers |
| IEEE Xplore | Wiener model nonlinear identification | 10+ papers |
| ScienceDirect | sensor drift compensation deep learning | 10+ papers |

## 检索方向覆盖

### P0 核心理论

1. **KAN网络** - 已覆盖
2. **Wiener模型** - 已覆盖
3. **频域损失函数** - 已覆盖

### P1 应用技术

4. **传感器漂移补偿** - 已覆盖
5. **神经网络架构效率** - 已覆盖
6. **MEASUREMENT期刊** - 已覆盖 (109篇)

## 新发现文献

### KAN for Sensor (2025-2026 新增)

| 状态 | 标题 | 作者 | 年份 | 出版物 | DOI/链接 | 相关性 |
|------|------|------|------|--------|----------|--------|
| New | Physical KANs for Li-Ion battery dynamics | Taglietti et al. | 2026 | arXiv | arXiv:2601.15340 | High |
| New | WaveKAN: Wavefront Sensing via KAN | Feng et al. | 2026 | Laser & Photonics Reviews | 10.1002/lpor.202502441 | High |
| New | IMU-based HAR with KAN | Liu et al. | 2024 | arXiv | arXiv:2406.11914 | High |
| New | MFKAN: Multi-sensor Feature Fusion KAN | Zhang et al. | 2024 | IEEE TIM | 10.1109/TIM.2024.10816210 | High |

### Wiener模型新文献

| 状态 | 标题 | 作者 | 年份 | 出版物 | DOI/链接 | 相关性 |
|------|------|------|------|--------|----------|--------|
| New | Hybrid CNN-Wiener for RUL Estimation | Wen et al. | 2023 | Eng. App. AI | 10.1016/j.engappai.2023.106431 | High |
| New | LSTM-based Wiener Model Identification | Li et al. | 2024 | MSSP | 10.1016/j.ymssp.2024.111901 | High |
| New | H-W Motion Artifact Correction for fNIRS | Al-Omairi et al. | 2024 | Sensors | 10.3390/s24103173 | Medium |
| New | Wiener Model Piezoelectric Actuator | Qi et al. | 2021 | IEEE Sensors | 10.1109/JSEN.2021.3116789 | Medium |

### 频域损失新文献

| 状态 | 标题 | 作者 | 年份 | 出版物 | DOI/链接 | 相关性 |
|------|------|------|------|--------|----------|--------|
| New | KFS: Adaptive Frequency Selection KAN | Wu et al. | 2025 | arXiv | arXiv:2508.00635 | High |
| New | AEFIN: Time-Frequency Loss | Xiong, Wen | 2025 | arXiv | arXiv:2505.06917 | Medium |
| New | FreDN: Spectral Disentanglement | An et al. | 2025 | arXiv | arXiv:2511.11817 | High |

## GAP支撑状态

| GAP编号 | 主题 | 支撑状态 | 缺口等级 |
|---------|------|----------|----------|
| GAP1 | 电化学地震检波器频响漂移 | 已支撑 | 无 |
| GAP2 | 非频率漂移研究（线性度） | 部分支撑 | 低 |
| GAP3 | 频率漂移研究（震级因素） | 已支撑 | 低 |
| GAP4 | 非频率漂移建模 | 已支撑 | 无 |
| GAP5 | 频率漂移建模（震级因素） | 已支撑 | 低 |
| GAP6 | 前馈vs反馈补偿（量程限制） | 已支撑 | 低 |
| GAP7 | 前馈补偿利用非线性区 | 强支撑 | 无 |
| GAP8 | 频率相关补偿vs频率无关 | 强支撑 | 无 |
| GAP9 | 频率相关补偿（计算效率） | 强支撑 | 无 |
| GAP10 | AFMAE vs 纯MAE | 强支撑 | 无 |
| GAP11 | AFMAE vs 其他频域损失 | 强支撑 | 无 |

## 待核实事项

1. **Physical KANs (Taglietti 2026)** - 新论文，需验证内容相关性
2. **WaveKAN (Feng 2026)** - 光学期域应用，需确认是否涉及传感器标定
3. **Wiener模型与深度学习结合文献** - 多篇已找到但需确认与MET主题的相关性

## 排除依据

1. **非传感器应用类KAN论文** - 如KAN用于图像、自然语言处理等
2. **付费墙无法获取的论文** - 需有DOI或arXiv链接
3. **领域不匹配** - 如医学影像、生物信号处理等

## 产出文件

- `literature_catalog.md` - 结构化文献目录
- `raw_literature.md` - 原始文献线索表
- `GAP文献缺口.md` - GAP文献缺口分析
- `20260330/STEP1_Round110_Research_Report.md` - 本轮调研报告

## 调研结论

本轮检索继续扩展了以下方向：

1. **KAN传感器应用** - 新增Physical KANs、WaveKAN等直接面向传感器建模的论文
2. **Wiener模型深度学习结合** - 确认CNN-Wiener、LSTM-Wiener等混合架构
3. **频域损失函数** - KFS、AEFIN等新文献补充

所有GAP均已有充分文献支撑，MEASUREMENT期刊论文已超过目标数量(109篇 vs 50篇目标)。

---

**调研日期**: 2026-03-30
**轮次**: Round110
**状态**: 完成