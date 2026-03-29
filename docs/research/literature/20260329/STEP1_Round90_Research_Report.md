# 调研报告：第90轮文献补充调研（2026-03-29）

## 基本信息
- 日期：2026-03-29
- 阶段：STEP1 调研
- 覆盖范围：P0/P1/P2各方向最新文献补充检索
- 是否使用子代理：是（4个并行子代理分别搜索KAN、Wiener模型、频域损失、传感器漂移补偿、LUT实现）

## 检索路径

### 子代理搜索方向

1. **KAN网络最新论文 (2026年3月)**
   - 关键词：KAN, Kolmogorov-Arnold network, site:arxiv.org 2026
   - 数据库：arXiv
   - 结果：大部分论文已在目录中，新增论文均已收录

2. **Wiener模型最新论文 (2025-2026)**
   - 关键词：Wiener system identification nonlinear
   - 数据库：arXiv
   - 结果： Barron-Wiener-Laguerre (2602.13098) 已在目录

3. **频域损失函数**
   - 关键词：frequency domain loss, spectral loss, AFMAE
   - 数据库：arXiv
   - 结果：FreDF、OLMA、FIRE等核心论文已在目录

4. **传感器漂移补偿**
   - 关键词：sensor drift compensation deep learning
   - 数据库：arXiv
   - 结果：TDACNN等核心论文已在目录

5. **LUT神经网络硬件实现**
   - 关键词：LUT neural network, look-up table inference, KAN hardware
   - 数据库：arXiv
   - 结果：KANELÉ、LUT-KAN、GRAU、BitLogic等核心论文已在目录

## 发现结果

### 本轮新增文献线索

| 作者 | 年份 | 标题 | DOI/链接 | 类别 | 相关度 | 状态 |
|------|------|------|---------|------|--------|------|
| Faroughi et al. | 2026 | Symbolic-KAN: Kolmogorov-Arnold Networks with Discrete Symbolic Structure | https://arxiv.org/abs/2603.23854 | P0 | 高 | **已收录** (已排除-R17) |
| Sovrano et al. | 2026 | In-Context Symbolic Regression for Robustness-Improved KAN | https://arxiv.org/abs/2603.15250 | P0 | 高 | **已收录** |
| Almodóvar et al. | 2026 | KaCGM: Kolmogorov-Arnold Causal Generative Models | https://arxiv.org/abs/2603.20184 | P0 | 高 | **已收录** (R62验证) |
| Dai et al. | 2026 | Many-body Mobility Edges via KAN | https://arxiv.org/abs/2603.21807 | P1 | 中 | **已收录** |
| Yuan | 2026 | HMAR: Hierarchical Modality-Aware Expert KAN | https://arxiv.org/abs/2603.16679 | P1 | 中 | **已收录** |
| Huang et al. | 2025 | Hardware Acceleration of KAN (TSMC 22nm) | https://arxiv.org/abs/2509.05937 | P2 | 高 | **已收录** |
| Errabii et al. | 2026 | KANtize: Low-bit Quantization of KAN | https://arxiv.org/abs/2603.17230 | P1 | 高 | **已收录** |

### 已在目录中的核心论文状态

| 论文 | 状态 | 说明 |
|------|------|------|
| Symbolic-KAN (2603.23854) | 已排除 | 符号结构KAN，与传感器应用无关 |
| KaCGM (2603.20184) | 已验证 (R62) | KAN因果生成模型 |
| In-Context SINDy-KAN (2603.15250) | 已收录 | 符号回归，与Wiener-KAN关联有限 |
| KANtize (2603.17230) | 已收录 | KAN低比特量化，效率相关 |
| KANELÉ/LUT-KAN/GRAU | 已验证 | LUT硬件实现，核心支撑 |

## 目录完整性评估

| 类别 | 目录数量 | 评估 |
|------|----------|------|
| KAN网络 | 50+ | **完整** |
| Wiener模型 | 30+ | **完整** |
| 频域损失函数 | 20+ | **完整** |
| 漂移补偿 | 25+ | **完整** |
| 架构效率 | 15+ | **完整** |
| MEASUREMENT期刊 | 85+ (目标50+) | **超额完成** |
| LUT硬件实现 | 8+ | **完整** |

## 待核实事项

本轮检索未发现新的高相关性论文。所有2026年3月提交的KAN相关论文已在前期轮次中被收录或排除。

## 对文档的影响

- 更新了哪些文件：无新增（所有论文均已在目录）
- 是否需要更新 SUMMARY：否
- 是否需要后续 STEP2 分析：否

## 原始链接

- https://arxiv.org/abs/2603.23854 (Symbolic-KAN)
- https://arxiv.org/abs/2603.20184 (KaCGM)
- https://arxiv.org/abs/2603.21807 (Many-body)
- https://arxiv.org/abs/2603.16679 (HMAR)
- https://arxiv.org/abs/2603.15250 (In-Context SINDy)
- https://arxiv.org/abs/2603.17230 (KANtize)
- https://arxiv.org/abs/2509.05937 (KAN Hardware)
