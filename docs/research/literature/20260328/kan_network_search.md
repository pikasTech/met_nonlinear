# KAN（Kolmogorov-Arnold网络）文献检索报告

**日期**：2026-03-28
**检索范围**：arXiv，Google Scholar
**关键词**：KAN, Kolmogorov-Arnold, 样条, 时间序列, 效率

---

## 1. 执行摘要

本报告记录KAN网络文献检索情况。

**关键发现**：
- 原始KAN论文（Liu等，2024）已充分验证
- TKAN将KAN扩展到循环机制
- 状态空间KAN为Wiener-KAN提供直接理论基础

---

## 2. 关键论文

### KAN原始论文（Liu等）
- arXiv: 2404.19756
- 链接: https://arxiv.org/abs/2404.19756

### TKAN（Genet, Inzirillo）
- arXiv: 2405.07344
- 链接: https://arxiv.org/abs/2405.07344

### 状态空间KAN（Cruz等）- 关键
- arXiv: 2506.16392
- DOI: 10.1109/LCSYS.2025.3578019
- 链接: https://arxiv.org/abs/2506.16392
- **直接连接**：已在Wiener-Hammerstein基准上验证

### PowerMLP（Qiu等）
- arXiv: 2412.13571
- 比原始KAN快约40倍

### KANEL_E（Hoang等）
- arXiv: 2512.12850
- FPGA上最高加速2700倍

---

## 3. 论文汇总表

| 论文 | 年份 | arXiv ID | 状态 |
|------|------|----------|------|
| KAN原始论文 | 2024 | 2404.19756 | 已验证 |
| TKAN | 2024 | 2405.07344 | 已验证 |
| KAN时间序列 | 2024 | 2405.08790 | 已验证 |
| PowerMLP | 2024 | 2412.13571 | 已验证 |
| KAN 2.0 | 2024 | 2408.10205 | 已验证 |
| 状态空间KAN | 2025 | 2506.16392 | 已验证 |
| Barron-Wiener-Laguerre | 2026 | 2602.13098 | 已验证 |
| KANEL_E | 2025 | 2512.12850 | 已验证 |
| 硬件KAN边缘 | 2024 | 2409.11418 | 已验证 |
| GRU-KAN/LSTM-KAN | 2025 | 2507.13685 | 已验证 |

---

## 4. 计算效率汇总

| 架构 | 相对速度 | 备注 |
|------|----------|------|
| MLP | 1x基线 | 固定激活 |
| 原始KAN | 慢约10倍 | 迭代样条 |
| PowerMLP | 约1x | 比KAN快40倍 |
| KANEL_E（FPGA） | 最高2700x | 基于LUT |

**关键引用**：KAN通常比MLP慢10倍（Liu等 2024）

---

## 5. 待验证项目

| 项目 | 状态 | 备注 |
|------|------|------|
| AFMAE原始论文 | 未找到 | 使用FFL代替 |
| FreDF原始论文 | 未找到 | SAMFre引用 |

---

## 6. 与Wiener-KAN的相关性

### 直接连接
1. 状态空间KAN - Wiener-Hammerstein验证
2. Barron-Wiener-Laguerre - 理论框架
3. TKAN - 用于传感器漂移的时间建模

### SPICE效率
1. KANEL_E - 基于LUT的硬件实现可行
2. 硬件论文 - 面积/功耗权衡
3. PowerMLP - 40倍加速路径

---

## 7. 参考文献

1. Liu等（2024）. KAN. arXiv:2404.19756
2. Genet, Inzirillo（2024）. TKAN. arXiv:2405.07344
3. Cruz等（2025）. SS-KAN. arXiv:2506.16392
4. Qiu等（2024）. PowerMLP. arXiv:2412.13571
5. Hoang等（2025）. KANEL_E. arXiv:2512.12850
6. Huang等（2024）. 硬件KAN边缘. arXiv:2409.11418
7. Yang等（2025）. GRU-KAN/LSTM-KAN. arXiv:2507.13685

---

**状态**：已完成