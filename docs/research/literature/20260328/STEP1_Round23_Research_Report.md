# 调研报告：STEP1 第23轮文献搜索

## 基本信息
- 日期：2026-03-28
- 阶段：STEP1 调研
- 覆盖范围：KAN顶会论文、Wiener模型新论文、传感器校准、MEASUREMENT期刊
- 是否使用子代理：是（并行5个方向）

## 检索路径

### 子代理1：KAN顶会论文 (ICLR/ICML/NeurIPS/AAAI 2025-2026)
- 关键词：KAN, Kolmogorov-Arnold Networks, time series, efficiency
- 主要数据库：arXiv, Google Scholar
- 结果：发现6篇新论文，包括AAAI 2025、ICLR 2025等顶会论文

### 子代理2：Wiener模型2025-2026论文
- 关键词：Wiener model, Wiener-Hammerstein, nonlinear system identification
- 主要数据库：arXiv, IEEE Xplore
- 结果：发现5篇新论文，包括高斯和滤波器、贝叶斯估计等新方向

### 子代理3：传感器ML补偿论文
- 关键词：sensor calibration, neural network, drift compensation
- 主要数据库：IEEE Xplore, arXiv, ScienceDirect
- 结果：确认FRIKAN等直接相关论文

### 子代理4：频域损失函数
- 关键词：frequency domain loss, spectral loss, FFT loss
- 主要数据库：arXiv, Google Scholar
- 结果：确认FIRE、SATL等论文与AFMAE的关联

### 子代理5：MEASUREMENT期刊2024-2026
- 关键词：sensor calibration, nonlinearity, measurement
- 主要数据库：ScienceDirect
- 结果：发现5篇待核实DOI

## 发现结果

### 新增文献线索（待核实/已验证）
| 作者 | 年份 | 标题 | DOI/链接 | 类别 | 相关度 | 状态 |
|------|------|-------|---------|------|--------|------|
| Wu et al. | 2025 | KFS: KAN with Adaptive Frequency Selection | https://arxiv.org/abs/2508.00635 | P0 | 高 | 已验证 |
| Hong et al. | 2025 | TSKANMixer (AAAI 2025) | https://arxiv.org/abs/2502.18410 | P0 | 高 | 已验证 |
| Zhang et al. | 2026 | Spectral Gating Networks | https://arxiv.org/abs/2602.07679 | P0 | 高 | 新增 |
| Chiu et al. | 2026 | Free-RBF-KAN | https://arxiv.org/abs/2601.07760 | P0 | 高 | 新增 |
| Taglietti et al. | 2026 | Physical KAN: Silicon Photonics | https://arxiv.org/abs/2601.15340 | P0 | 高 | 新增 |
| Cedeño et al. | 2025 | Quadrature Gaussian Sum Filter for Wiener | https://arxiv.org/abs/2505.08469 | P1 | 高 | 新增 |
| Vakili et al. | 2025 | Optimal Bayesian Affine Estimator for Wiener | https://arxiv.org/abs/2504.05490 | P1 | 高 | 新增 |
| Yin, Müller | 2026 | Data-Driven H-W with Implicit GPs | https://arxiv.org/abs/2501.15849 | P0 | 高 | 已验证 |
| Zhang et al. | 2026 | Taiji-2 sensor calibration | https://arxiv.org/abs/2603.25327 | P1 | 高 | 新增 |
| Manavalan, Tronarp | 2026 | Barron-Wiener-Laguerre | https://arxiv.org/abs/2602.13098 | P0 | 高 | 新增 |

### 入口已定位
- arXiv KAN分类: cs.LG, cs.AI, cs.AR
- IEEE Xplore: Wiener system identification
- ScienceDirect MEASUREMENT: sensor calibration

### 疑似重复
- 多篇2026年KAN变体论文可能有重叠

### 明确排除
- 无新排除论文

## 待核实事项
- 5篇MEASUREMENT DOI需进一步核实内容相关性
- 部分2026年论文需确认是否已在本目录

## 对文档的影响
- 更新文件：raw_literature.md, literature_catalog.md
- 需更新SUMMARY：否
- 需后续STEP2分析：否（大部分为新增/待核实状态）

## 原始链接
- https://arxiv.org/abs/2508.00635 (KFS)
- https://arxiv.org/abs/2502.18410 (TSKANMixer)
- https://arxiv.org/abs/2602.07679 (Spectral Gating)
- https://arxiv.org/abs/2601.07760 (Free-RBF-KAN)
- https://arxiv.org/abs/2505.08469 (Gaussian Sum Filter)
- https://arxiv.org/abs/2504.05490 (Bayesian Wiener)
- https://arxiv.org/abs/2501.15849 (H-W GP)
- https://arxiv.org/abs/2603.25327 (Taiji-2)
- https://arxiv.org/abs/2602.13098 (Barron-Wiener)