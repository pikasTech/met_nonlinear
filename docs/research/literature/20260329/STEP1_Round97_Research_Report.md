# STEP1 Round97 研究报告 (2026-03-29)

## 检索范围
- 数据库: arXiv, IEEE Xplore, Google Scholar
- 关键词: KAN, Wiener, frequency domain loss, sensor compensation
- 时间范围: 2024-2026

## 发现结果

### 1. 频域损失函数新论文

| 论文 | 年份 | arXiv ID | 关键贡献 | 相关度 |
|------|------|----------|----------|--------|
| FreLE | 2025 | 2510.25800 | 频谱偏置校正，显式频域损失 | 高 |
| OLMA | 2025 | 2505.11567 | DFT/DWT频域损失函数 | 高 |
| Frequency-Constrained | 2025 | 2508.01508 | FFT引导的约束优化 | 高 |
| TimeAPN | 2026 | 2603.17436 | 相位/幅度时频域建模 | 中 |
| FAIM | 2025 | 2512.07858 | 自适应傅里叶滤波 | 中 |

### 2. Wiener传感器应用

| 论文 | 年份 | DOI | 关键贡献 | 相关度 |
|------|------|-----|----------|--------|
| Hall Sensor Wiener Self-Calibration | 2025 | - | 2.6x RMS改善 | 高 |
| SS-KAN (Cruz) | 2025 | 2506.16392 | 状态空间KAN for Wiener-Hammerstein | 高 |
| Willemstein W-H | 2023 | 2302.13141 | 压阻传感器W-H补偿 | 高 |

### 3. 新增KAN效率论文

| 论文 | 年份 | DOI | 关键贡献 | 相关度 |
|------|------|-----|----------|--------|
| KAN-FIF | 2026 | 2602.12117 | 94.8%参数reduction，68.7%推理加速 | 高 |
| TimeAPN | 2026 | 2603.17436 | 时频域幅度相位建模 | 中 |

## 调研结论

文献库已覆盖:
- P0 KAN/Wiener/频域损失: 130+ 已验证
- P1 漂移补偿/架构效率: 充分覆盖
- P2 MEASUREMENT期刊: 95+ 篇

本轮发现OLMA和FreLE可作为AFMAE的替代参考文献。

## 产出文件

- `docs/research/literature/raw_literature.md` (更新)
- `docs/research/literature/literature_catalog.md` (更新)
