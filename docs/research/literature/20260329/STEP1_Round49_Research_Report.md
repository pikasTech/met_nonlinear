# 调研报告：Round 49 - 文献库最终确认与arXiv新论文核查

## 基本信息
- 日期：2026-03-29
- 阶段：STEP1 调研
- 覆盖范围：arXiv新论文核查、R47条目验证、文献库完整性最终确认
- 是否使用子代理：是（3个并行方向）

---

## 检索路径

### 子代理1：arXiv新论文核查（2026年3月23-27日）
- 关键词：KAN, Wiener, Hammerstein, frequency domain, spectral loss, sensor drift, sensor compensation
- 主要数据库：arXiv (cs.LG 933篇, stat.ML 154篇)
- 检索式：标题关键词匹配

### 子代理2：MEASUREMENT期刊新论文搜索
- 关键词：sensor nonlinearity, sensor drift, electrochemical sensor, neural network calibration
- 主要数据库：CrossRef API, Google Scholar
- 目标：2024-2026年论文

### 子代理3：R47条目验证（PolyKAN, lmKAN）
- 关键词：KAN efficiency, LUT, GPU acceleration, FLOPs reduction
- 主要数据库：arXiv
- 目标：核实R47新增条目的效率声称

---

## 发现结果

### 1. arXiv新论文核查结果

**结论：无新增高相关性文献**

核查范围：
- cs.LG: 933篇（2026年3月23-27日提交）
- stat.ML: 154篇（同期）
- 总计：1087篇

无发现与以下主题直接相关的论文：
- KAN (Kolmogorov-Arnold Networks)
- Wiener模型 / Wiener-Hammerstein
- 频域损失函数
- 传感器漂移补偿

潜在相关论文（已排除或低相关性）：
| arXiv ID | 标题 | 排除原因 |
|----------|------|----------|
| 2603.24916 | HYPERTINYPW: TinyML压缩 for ECG | ECG领域，不涉及KAN |
| 2603.24654 | Spectral methods for ML | 量子计算相关，非时序 |
| 2603.23547 | PDGMM-VAE for Nonlinear ICA | 非线性ICA，非Wiener系统 |

### 2. R47条目验证结果

#### PolyKAN (Yu et al. 2025)
- **arXiv**: 2511.14852
- **核心创新**: GPU融合算子，LUT + 线性插值优化
- **效率数据**:
  - 推理加速: 1.2-10x（对比Triton + cuBLAS基线）
  - 训练加速: 1.4-12x
  - 端到端加速: 1.3-2.2x
  - 吞吐量提升: 1.3-4x
- **与LSTM/GRU比较**: 无直接比较（仅对比Triton + cuBLAS）
- **状态**: 已收录 (R47)，高效用GPU实现

#### lmKAN (Pozdnyakov, Schwaller 2025)
- **arXiv**: 2509.07103
- **核心创新**: 查表多元KAN，推理FLOPs减少
- **效率数据**:
  - 推理FLOPs减少: 最高6.0x（对比MLP）
  - H100吞吐量: >10x提升（甲烷数据集，相同精度）
  - CIFAR-10: 1.6-2.1x FLOPs减少
  - ImageNet-1k: 1.7x FLOPs减少
- **与CNN/LSTM/GRU比较**: 无直接比较（对比MLP和CNN）
- **状态**: 已收录 (R47)，提供6x FLOPs减少证据

**R47验证结论**: PolyKAN和lmKAN均提供KAN配合LUT实现的高效率证据，但均无直接LSTM/GRU比较数据。论文中关于"KAN相对LSTM/GRU有计算效率优势"的声称仍无直接文献支撑。

### 3. MEASUREMENT期刊论文

**结论：大部已收录，新发现有限**

| 论文 | 年份 | DOI | 状态 |
|------|------|-----|------|
| Lin et al. 电化学地震传感器温度效应 | 2020 | 10.1016/j.measurement.2020.107518 | 已在R24收录 |
| Schaller et al. AutoML传感器漂移补偿 | 2025 | 10.1016/j.measurement.2025.117097 | 已在R35收录 |
| Han et al. AGA-BP加速度计温度漂移 | 2020 | 10.1016/j.measurement.2020.108019 | 已在R21收录 |
| Fang et al. TPoS微机电气体传感器非线性 | 2025 | 10.1016/j.measurement.2024.116559 | 已在R35收录 |
| Krikelis et al. 神经网络迟滞算子 | 2024 | 10.1016/j.measurement.2023.113966 | 已在R35收录 |

无新增高相关性MEASUREMENT论文。

---

## 文献库完整性最终确认

| 类别 | 已收录数量 | 目标 | 状态 |
|------|------------|------|------|
| KAN网络 | 50+篇 | - | ✅ 已完备 |
| Wiener模型 | 30+篇 | - | ✅ 已完备 |
| 频域损失函数 | 20+篇 | - | ✅ 已完备 |
| 漂移补偿 | 25+篇 | - | ✅ 已完备 |
| 架构效率 | 15+篇 | - | ✅ 已完备 |
| MEASUREMENT期刊 | 85篇 | 50篇 | ✅ 超额完成 |

---

## 关键结论

1. **arXiv新论文**: 2026年3月23-27日共1087篇，无新增高相关性文献
2. **R47条目验证**: PolyKAN和lmKAN均已核实，提供KAN+LUT效率证据但无直接LSTM/GRU比较
3. **KAN效率声称**: 仍建议删除"KAN相对LSTM/GRU有计算效率优势"，可保留"KAN相对MLP有参数效率优势"
4. **文献库状态**: 所有类别已完备，STEP1调研阶段正式结束

---

## 待核实事项

无新增待核实事项。R47条目已在Round47添加并在本轮验证。

---

## 对文档的影响

- 更新了 literature_catalog.md（添加Round49报告索引）
- 未修改 raw_literature.md（R47条目已在R47添加）
- 未修改 verified_literature.md 或 excluded_literature.md

---

## 原始链接

- PolyKAN: https://arxiv.org/abs/2511.14852
- lmKAN: https://arxiv.org/abs/2509.07103
- arXiv cs.LG: https://arxiv.org/list/cs.LG/recent?show=100
- arXiv stat.ML: https://arxiv.org/list/stat.ML/recent?show=100
