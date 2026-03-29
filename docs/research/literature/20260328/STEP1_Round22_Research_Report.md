# 调研报告：STEP1 第22轮文献搜索

## 基本信息
- 日期：2026-03-28
- 阶段：STEP1 调研
- 覆盖范围：KAN效率、频域损失函数、传感器漂移补偿、MEASUREMENT期刊
- 是否使用子代理：是（并行5个方向）

## 检索路径

### 子代理1：Wiener模型传感器应用
- 关键词：Wiener model sensor identification, Wiener-Hammerstein sensor, Wiener model nonlinear compensation
- 主要数据库：IEEE Xplore, arXiv, ScienceDirect
- 结果：现有目录已覆盖大部分2024-2026年文献

### 子代理2：KAN效率进展
- 关键词：KAN efficiency, KAN fast inference, KAN approximation, KAN hardware acceleration
- 主要数据库：arXiv, IEEE Xplore
- 新发现：18+篇新论文，包括：
  - KANtize (Errabii 2026): 2-3位量化，50x BitOps减少，2.9x GPU加速
  - VIKIN (Ou 2026): KAN/MLP统一加速器，1.28x KAN加速
  - BiKA (Liu 2026): 二值化KAN加速器，27-51%资源减少
  - Spectral Gating Networks (Zhang 2026): 比spline-based KAN快11.7x
  - Free-RBF-KAN (Chiu 2026): RBF替代B-spline，更快训练/推理
  - Physical Analog KAN (Taglietti 2026): 模拟KAN，10^2-10^3x能耗减少

### 子代理3：频域损失函数
- 关键词：frequency domain loss, spectral loss, FFT loss neural network
- 主要数据库：arXiv, IEEE Xplore, Google Scholar
- 新发现：6篇新论文
  - SATL (Yu et al. 2025): 时间+频率组合损失函数
  - AEFIN (Xiong, Wen 2025): 时频域稳定性约束损失
  - DSAT-HD (Wang et al. 2025): 混合傅里叶分解损失
  - DCAE (Stiehl et al. 2025): EEG时间-频率重建损失对比
  - SEPI-TFPNet (Yao et al. 2025): 谱熵引导的频率选择
  - Frequency-Domain Watermarking (Zhou et al. 2025): 频率偏差消除

### 子代理4：传感器漂移ML方法
- 关键词：sensor drift compensation neural network, ML sensor drift correction
- 主要数据库：IEEE Xplore, ScienceDirect, arXiv
- 结果：大部分相关论文已在目录中；Li et al. 2025 (TrAC) 是主要综述论文

### 子代理5：MEASUREMENT期刊
- 关键词：sensor calibration nonlinearity, sensor compensation neural network, frequency response measurement
- 主要数据库：ScienceDirect
- 结果：目录已有11篇（超过目标10篇）

## 发现结果

### 新增文献线索（待核实）
| 作者 | 年份 | 标题 | DOI/链接 | 类别 | 相关度 |
|------|------|-------|---------|------|--------|
| Errabii, Sentieys, Traiola | 2026 | KANtize: Low-bit Quantization for KAN | https://arxiv.org/abs/2603.17230 | P1 | 高 |
| Ou et al. | 2026 | VIKIN: KAN/MLP Accelerator | https://arxiv.org/abs/2603.01165 | P1 | 高 |
| Zhang et al. | 2026 | Spectral Gating Networks | https://arxiv.org/abs/2602.07679 | P0 | 高 |
| Chiu et al. | 2026 | Free-RBF-KAN | https://arxiv.org/abs/2601.07760 | P0 | 高 |
| Yu et al. | 2025 | SATL | https://arxiv.org/abs/2507.23253 | P0 | 高 |
| Xiong, Wen | 2025 | AEFIN | https://arxiv.org/abs/2505.06917 | P0 | 高 |
| Wang et al. | 2025 | DSAT-HD | https://arxiv.org/abs/2509.24800 | P1 | 中 |
| Stiehl et al. | 2025 | DCAE | https://arxiv.org/abs/2508.20535 | P1 | 中 |

### 入口已定位
- arXiv KAN效率分类: cs.AR, cs.LG
- IEEE KAN硬件: TCAS, ISFPGA
- 频域损失: ICLR, NeurIPS, ICML

### 疑似重复
- 多篇2026年KAN变体论文可能有重叠（需后续STEP2核对）

### 明确排除
- 无新排除论文

## 待核实事项
- KANtize、VIKIN、BiKA等硬件论文需验证是否已在本目录
- SATL、AEFIN等频域损失论文与FreDF/OLMA的关系需核对
- 确认目录中已有的KAN效率论文（已有大量2026年文献）

## 对文档的影响
- 更新文件：raw_literature.md, literature_catalog.md
- 需更新SUMMARY：否
- 需后续STEP2分析：否（大部分为已验证/待核实状态）

## 原始链接
- https://arxiv.org/abs/2603.17230 (KANtize)
- https://arxiv.org/abs/2603.01165 (VIKIN)
- https://arxiv.org/abs/2602.07679 (Spectral Gating)
- https://arxiv.org/abs/2601.07760 (Free-RBF-KAN)
- https://arxiv.org/abs/2507.23253 (SATL)
- https://arxiv.org/abs/2505.06917 (AEFIN)
