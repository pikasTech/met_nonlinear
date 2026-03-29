# 调研报告：第43轮文献调研

## 基本信息
- 日期：2026-03-29
- 阶段：STEP1 调研（第43轮）
- 覆盖范围：并行多方向深度检索（MEASUREMENT期刊论文、KAN效率对比、Wiener模型传感器应用）
- 是否使用子代理：是（3个explore代理并行搜索）

## 检索路径

### 并行搜索方向

#### 1. MEASUREMENT期刊论文搜索
- 关键词：sensor nonlinearity compensation, calibration, drift, temperature compensation, electrochemical sensor, seismic sensor
- 主要数据库：Google Scholar (site:sciencedirect.com/journal/measurement), IEEE Xplore, Crossref
- 新发现：2篇新论文

#### 2. KAN效率对比论文搜索
- 关键词：KAN efficiency, KAN benchmark, KAN computation complexity, KAN vs LSTM, KAN vs GRU
- 主要数据库：arXiv (cs.LG, stat.ML), Google Scholar
- 新发现：多项KAN效率研究论文

#### 3. Wiener模型传感器应用搜索
- 关键词：Wiener-Hammerstein sensor calibration, block-structured nonlinear models, piezoresistive sensors
- 主要数据库：arXiv, IEEE Xplore, Google Scholar
- 新发现：多项Wiener传感器应用论文

## 发现结果

### MEASUREMENT期刊论文发现

**新增论文（2篇）：**

1. **Payo et al. 2022** - Voltage drift compensation in charge amplifiers for DC measurements
   - DOI: 10.1016/j.measurement.2022.111640
   - 主题：漂移补偿
   - 相关性：高

2. **Soy & Toy 2021** - Design and implementation of smart pressure sensor for automotive
   - DOI: 10.1016/j.measurement.2021.109184
   - 主题：校准
   - 相关性：中

**注：** 文献库已相当完备，已包含85+篇MEASUREMENT期刊论文。

### KAN效率对比发现（关键发现）

**重要结论：没有找到KAN相对LSTM/GRU计算效率优势的证据**

主要发现：

1. **KAN vs MLP对比为主**：大多数论文比较KAN与MLP，而非LSTM/GRU

2. **KAN增强型模型关注精度而非效率**：
   - GRU-KAN (arXiv:2507.13685)：关注预测精度提升，非计算效率
   - LSTM-KAN：混合模型性能优于纯LSTM/GRU，但无效率对比数据

3. **KAN计算开销问题被多项研究指出**：
   - FEKAN (arXiv:2602.16530)："existing KAN architectures suffer from high computational cost and slow convergence"
   - KANtize (arXiv:2603.17230)："evaluating spline functions increases computational complexity during inference"
   - Spectral Gating Networks (arXiv:2602.07679)：addresses KAN's "computational inefficiency"

4. **效率声称均为KAN vs MLP**：
   - Gaonkar 2026：KAN vs MLP，FLOPs减少
   - Graph KAN：16.69x参数减少，55.75%运行时间减少（vs GNN，非LSTM/GRU）

**结论：** 论文声称"KAN相对LSTM/GRU有计算效率优势"目前**没有文献支撑**。

### Wiener模型传感器应用发现

**主要新发现论文：**

1. **Willemstein et al. 2023/2024** - Hammerstein-Wiener用于3D打印压阻传感器的力估计
   - DOI: 10.1016/j.measurement.2024.23
   - 已收录：Verified (R17)

2. **Beintema et al. 2020** - 非线性状态空间识别使用深度编码器网络
   - Wiener-Hammerstein基准测试最低仿真误差
   - 已收录：Verified (R7)

3. **Revay et al. 2021** - 递归平衡网络：稳定的Wiener/Hammerstein模型
   - 已收录：Verified

4. **Ross et al. 2021** - 高斯过程学习非参数Volterra核
   - 贝叶斯方法，不确定性量化
   - 新发现

5. **Li et al. 2024** - 深度学习用于扬声器非线性补偿
   - 比较深度学习vs Volterra滤波器
   - DOI: 10.1109/LSP.2025.3553434
   - 新发现

## 待核实事项

1. **KAN效率声称问题**：需要重新评估论文中"KAN相对LSTM/GRU有计算效率优势"的声称是否合适
2. **新增MEASUREMENT论文**：Payo 2022, Soy & Toy 2021需添加到catalog
3. **Wiener模型新论文**：Ross 2021, Li 2024需核实是否已在catalog

## 对文档的影响
- 更新 `literature_catalog.md`：添加本轮报告索引，新增MEASUREMENT论文
- 更新 `raw_literature.md`：添加新发现论文
- 是否需要更新 SUMMARY：否
- 是否需要后续 STEP2 分析：**是** - KAN效率声称需要进一步分析

## 原始链接

### MEASUREMENT期刊
- https://doi.org/10.1016/j.measurement.2022.111640 (Payo 2022)
- https://doi.org/10.1016/j.measurement.2021.109184 (Soy 2021)

### KAN效率论文
- https://arxiv.org/abs/2603.17230 (KANtize)
- https://arxiv.org/abs/2602.16530 (FEKAN)
- https://arxiv.org/abs/2602.07679 (Spectral Gating)
- https://arxiv.org/abs/2507.13685 (GRU-KAN)
- https://arxiv.org/abs/2601.10563 (Gaonkar KAN vs MLP)

### Wiener模型
- https://arxiv.org/abs/2106.05582 (Ross GP Volterra)
- https://arxiv.org/abs/2412.01092 (Li DL Compensation)

## 产出文件
- `docs/research/literature/20260329/STEP1_Round43_Research_Report.md`（本文件）
