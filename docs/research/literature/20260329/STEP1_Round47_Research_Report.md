# 调研报告：Round 47 - 子代理并行文献检索

## 基本信息
- 日期：2026-03-29
- 阶段：STEP1 调研
- 覆盖范围：KAN LUT硬件加速、Wiener模型传感器应用、arXiv最新批次
- 是否使用子代理：是（3个并行方向）

## 检索路径

### 子代理1：Wiener模型电化学/地震传感器应用
- 关键词：Wiener model electrochemical sensor, Wiener model seismic sensor, Wiener-Hammerstein sensor drift compensation, block-structured nonlinear sensor modeling, electrochemical sensor identification
- 主要数据库：IEEE Xplore, ScienceDirect, Google Scholar, arXiv
- 新发现数据库：无

### 子代理2：KAN LUT硬件加速最新进展
- 关键词：KAN LUT implementation, KAN hardware acceleration, KAN FPGA, KAN edge computing, KAN inference speed, KAN lookup table, KAN quantization, KAN efficient inference
- 主要数据库：IEEE Xplore, arXiv, Google Scholar, ACM Digital Library

### 子代理3：arXiv最新批次核查
- 关键词：cs.LG, stat.ML, eess.SY 2026年3月批次
- 主要数据库：arXiv

## 发现结果

### 新增文献线索（3篇）

#### 1. PolyKAN: GPU-Accelerated Polynomial KAN with Fused LUT Operators
- **arXiv**: 2511.14852
- **作者**: Yu, Zhong, Huang, Lu, Jiang
- **年份**: 2025
- **主要内容**: GPU加速的算子库，使用LUT+线性插值优化，1.2-10x推理加速，1.4-12x训练加速
- **相关性**: 高
- **与已有文献关系**: 与raw_literature.md中记录的PolyKAN (2510.04205 "多面体分析")不同，这是另一篇关于GPU加速的论文

#### 2. lmKAN: Lookup Table Multivariate Kolmogorov-Arnold Networks
- **arXiv**: 2509.07103
- **作者**: Pozdnyakov, Schwaller
- **年份**: 2025
- **主要内容**: 使用查找表实现多元KAN，推理FLOPs减少6.0x，H100吞吐量提高10x
- **相关性**: 高
- **与已有文献关系**: 未在raw_literature.md中找到记录，直接涉及LUT实现

#### 3. Concurrent Training Methods for KANs: Disjoint Datasets and FPGA Implementation
- **arXiv**: 2512.18921
- **作者**: Polar, Poluektov
- **年份**: 2025
- **主要内容**: KAN的并行训练方法，FPGA实现测试
- **相关性**: 中
- **与已有文献关系**: 未在raw_literature.md中找到记录

### 明确排除

- **Wiener模型电化学传感器**：未发现直接将Wiener模型应用于电化学传感器/电化学地震计的原始论文
- **arXiv最新批次**：cs.LG 933篇、stat.ML 154篇、eess.SY 171篇中无高相关性新文献

### 已有文献覆盖确认

Wiener模型传感器应用已有文献：
- Willemstein 2023/2024: 软执行器/传感器Wiener-Hammerstein模型
- Iqbal 2024: 电化学传感器Volterra系统分析（MIT DSpace）
- Lin et al. 2020: 电化学地震传感器温度补偿（MEASUREMENT期刊）
- Kumar et al. 2020: 电子舌非线性建模（IEEE Sensors Journal）
- Schoukens组 (2017, 2019): Wiener-Hammerstein基准

## 待核实事项

1. PolyKAN (2511.14852)与已有的PolyKAN (2510.04205)是否为不同论文（已确认不同）
2. lmKAN (2509.07103)是否为LUT-KAN的另一种实现（不同，且lmKAN有明确FLOPs减少数据）

## 对文档的影响

- 更新了 `docs/research/literature/raw_literature.md`：新增3篇KAN LUT硬件加速论文
- 更新了 `docs/research/literature/literature_catalog.md`：新增Round 47章节
- 创建了 `docs/research/literature/20260329/STEP1_Round47_Research_Report.md`

## 原始链接

- https://arxiv.org/abs/2511.14852 (PolyKAN)
- https://arxiv.org/abs/2509.07103 (lmKAN)
- https://arxiv.org/abs/2512.18921 (KAN并行训练FPGA)
