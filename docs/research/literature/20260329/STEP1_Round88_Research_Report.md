# 调研报告：第88轮文献补充调研（2026-03-29）

## 基本信息
- 日期：2026-03-29
- 阶段：STEP1 调研
- 覆盖范围：P0/P1/P2各方向最新文献补充检索
- 是否使用子代理：是（5个并行子代理分别搜索Wiener模型传感器应用、KAN 2026论文、频域损失函数、MEASUREMENT期刊、LUT神经网络实现）

## 检索路径

### 子代理搜索方向

1. **Wiener模型传感器应用**
   - 关键词：Wiener model sensor, Wiener-Hammerstein electrochemical, block-structured nonlinear sensor identification
   - 数据库：arXiv, IEEE Xplore, Google Scholar
   - 结果：大部分文献已在目录中，新增van Meer 2025 (Hall传感器Wiener自校准)

2. **KAN 2026最新论文**
   - 关键词：KAN, Kolmogorov-Arnold network, site:arxiv.org 2026
   - 数据库：arXiv
   - 结果：大部分已在目录，新增KAN-SAs (脉动阵列)、FeKAN (FeFET+CAM加速器)

3. **频域损失函数**
   - 关键词：frequency domain loss, spectral loss, FFT loss
   - 数据库：arXiv, IEEE Xplore
   - 结果：目录已包含FreDF、BSP Loss、FreLE等核心论文

4. **MEASUREMENT期刊搜索**
   - 关键词：sensor nonlinearity measurement, drift compensation measurement, electrochemical measurement
   - 数据库：ScienceDirect (MEASUREMENT journal)
   - 结果：目录已有约95篇MEASUREMENT论文，目标50篇已超额完成

5. **LUT神经网络实现**
   - 关键词：LUT neural network, FPGA neural network, KAN LUT
   - 数据库：arXiv, DBLP, IEEE Xplore
   - 结果：发现多篇新文献，包括LUT-NN调研、AmigoLUT、LUTMUL、FeKAN等

## 发现结果

### 新增文献线索（待核实）

#### KAN硬件/LUT实现新文献

| 作者 | 年份 | 标题 | DOI/链接 | 相关度 | 备注 |
|------|------|------|---------|--------|------|
| Guo | 2025 | LUT-based Deep Neural Networks Survey | https://arxiv.org/abs/2506.07367 | 高 | 综合性调研论文 |
| Weng et al. | 2025 | AmigoLUT: Scaling Up LUT-based NN with FPGA | FPGA 2025 | 高 | FPGA原生LUT-NN扩展 |
| Xie et al. | 2025 | LUTMUL: LUT-based Efficient Multiplication | ASP-DAC 2025 | 高 | 突破roofline限制 |
| Yu et al. | 2025 | FeKAN: FeFET+CAM KAN Accelerator | DAC 2025 | 高 | 与KANELÉ不同技术路线 |
| Errabii et al. | 2026 | KAN-SAs: KAN on Systolic Arrays | IEEE/ACM DATE | 高 | 脉动阵列加速 |

#### Wiener模型传感器应用新文献

| 作者 | 年份 | 标题 | DOI/链接 | 相关度 | 备注 |
|------|------|------|---------|--------|------|
| Barbieri et al. | 2025 | Volterra电压互感器谐波补偿 | 10.1016/j.measurement.2025.118373 | 高 | MEASUREMENT期刊 |

### 已在目录中的核心论文状态

| 论文 | 状态 | 说明 |
|------|------|------|
| van Meer 2025 (Hall传感器Wiener) | 已收录 R85 | Wiener系统自校准 |
| KAN-SAs (Errabii 2026) | 待收录 | DATE 2026会议 |
| FeKAN (Yu 2025) | 待收录 | DAC 2025 |
| LUT Survey (Guo 2025) | 待收录 | 综合调研 |

## 目录完整性评估

| 类别 | 目录数量 | 评估 |
|------|----------|------|
| KAN网络 | 50+ | **完整** |
| Wiener模型 | 30+ | **完整** |
| 频域损失函数 | 20+ | **完整** |
| 漂移补偿 | 25+ | **完整** |
| 架构效率 | 15+ | **完整** |
| MEASUREMENT期刊 | 95+ (目标50+) | **超额完成** |
| LUT硬件实现 | 10+ | **完整** |

## 对文档的影响

- 更新了哪些文件：raw_literature.md（新增LUT-KAN调研和FeKAN）
- 是否需要更新 literature_catalog.md：需要添加FeKAN和KAN-SAs
- 是否需要后续 STEP2 分析：否（本轮为补充调研）

## 原始链接

- https://arxiv.org/abs/2506.07367 (Guo - LUT-NN Survey)
- https://dblp.org/rec/conf/fpga/WengAZCGCTFDK25 (AmigoLUT)
- https://dblp.org/rec/conf/aspdac/XieLDHLL25 (LUTMUL)
- https://dblp.org/rec/conf/dac/YuQYZZ25 (FeKAN)
- https://arxiv.org/abs/2512.00055 (KAN-SAs)
