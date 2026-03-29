# 分析报告：STEP2 Round 14

## 基本信息
- 日期：2026-03-28
- 阶段：STEP2 分析 Round 14
- 分析对象：待分析文献条目（R13新增论文 + Pending条目）
- 是否使用子代理：是；并行维度：4个子代理分别处理(KAT分析、R13 Wiener-KAN混合论文、EEMD-GRNN分析、FET传感器论文)

## 理论提取

### 1. KAT: Kolmogorov-Arnold Transformer (Yang, Wang 2024)

**核心贡献**：
- 将ViT中的MLP层替换为Group-Rational KAN (GR-KAN)层
- 解决KAN规模化的三个挑战：B-spline效率低、参数爆炸、初始化不当
- 创新：Rational基函数（21 FLOPs）vs B-spline（204 FLOPs）

**关键发现**：
- ViT-B + KAT达到82.7% vs ViT-B 79.1%（ImageNet）
- **关键警示**：Naive KAN替换失败（ViT-L + KAN无法收敛）
- 方差保持初始化至关重要

**与论文的相关点**：
- **MEDIUM relevance** - KAN+Transformer混合验证了集成方法可行性
- 效率解决方案（rational函数）可为Wiener-KAN设计提供参考
- **NOT block-structured** - 不是Wiener线性→非线性→线性架构

### 2. SKANODEs: Structured KAN Neural ODEs (Liu et al. 2025)

**核心贡献**：
- Structured KAN + Neural ODEs结合
- 两阶段学习：KANapprox（潜在动态）+ KANsymbolic（符号方程发现）
- 结构化状态空间公式：d[x;v]/dt = [v; KANapprox(x,v,u)]

**关键发现**：
- 恢复Duffing振子中的立方刚度
- 识别Van der Pol振子中的非线性阻尼
- F-16接口动力学与滞回特性

**与论文的相关点**：
- **HIGH relevance** - KAN+Neural ODE框架与状态空间形式直接映射到Wiener架构
- 虚拟传感（从加速度测量）类似于MET传感器补偿

### 3. Wiener-Hammerstein for Piezoresistive Actuators (Willemstein et al. 2023)

**核心贡献**：
- WH模型用于3D打印软执行器的应变估计
- 补偿压阻传感器的非线性滞回
- 结构：H₁(q) → g(.) → H₂(q)

**关键公式**：
```
ε(t) = H₂(q)(g(H₁(q)ΔR(t)))
```

**关键发现**：
- 83%拟合度，6% RMS误差
- 优于线性模型（76.2%/9.4%）

**与论文的相关点**：
- **HIGH relevance** - WH架构用于传感器滞回补偿的直接证据
- 三种执行器类型测试（弯曲、收缩器、3DoF）

### 4. Efficient Volterra Series Estimation (Birpoutsoukis et al. 2018)

**核心贡献**：
- 非参数Volterra级数估计与正则化
- 高效估计无需长瞬态自由测量
- LTV系统的新型瞬态消除

**与论文的相关点**：
- **HIGH relevance** - Volterra级数是Wiener模型的基础
- 正则化技术直接适用于MET AFMAE损失设计

### 5. Baseline Results for Nonlinear System ID (Champneys et al. 2024)

**核心贡献**：
- 五个流行非线性系统ID基准上的十种基线技术
- 包括：Silverbox, Wiener-Hammerstein, EMPS, Cascaded Tanks, CED

**关键结果**：
| 模型 | Silverbox | W-H | EMPS | Tanks | CED |
|------|-----------|-----|------|-------|-----|
| LTI SS | 6.96 | 14.4 | 6.58 | 43.4 | 0.588 |
| pNARX | 0.640 | 2.25 | 0.571 | 27.3 | 5.17 |
| GP NARX | 0.301 | 0.60 | 0.259 | 23.1 | 1690 |

**与论文的相关点**：
- **HIGH relevance** - MET论文定位的基准背景
- W-H基准直接相关

### 6. EEMD-GRNN for MEMS Sensor Drift (Shi et al. 2022)

**核心贡献**：
- EEMD（集成经验模态分解）+ GRNN（通用回归神经网络）
- EEMD分离白噪声与漂移信号
- GRNN对漂移动态建模

**关键结果**：
- 位移精度：95.64% → 98.00%
- EEMD有效分离噪声与漂移分量

**重要 Caveat**：
- GRNN是**浅层网络**（单隐层RBF），**不是深度学习**
- 该论文实际上表明：浅层网络+良好预处理可以有效建模复杂漂移信号

**与论文的相关点**：
- **MEDIUM (with caveats)** - 支持"预处理+神经网络"方法
- **NOT深度学习必要性的证据**

### 7. FET Sensor Drift (Margarit-Taulé 2022)

**状态**：已在R9验证
- DNN实现73% RMSE降低
- 90天连续pH监测
- **HIGH relevance** - FET传感器ML漂移补偿的直接证据

## 文献质量评估

### 可靠文献（Verified R14）
1. **KAT (Yang, Wang 2024)** - NUS高质量工作，效率分析详细
2. **SKANODEs (Liu 2025)** - KAN+Neural ODE框架，状态空间解释清晰
3. **Willemstein WH (2023)** - WH架构用于执行器，实验验证充分
4. **Birpoutsoukis Volterra (2018)** - 正则化理论扎实
5. **Champneys Benchmarks (2024)** - 基准测试全面

### 质量存疑
- **EEMD-GRNN** - 浅层网络，不是深度学习

### 明显不相关（Excluded）
- REDOX Reactions (Silva 2024) - 领域不匹配

## 审稿意见支撑

| 审稿意见 | 支撑文献 | 支撑内容 |
|---------|---------|---------|
| KAN+RNN混合有效性 | KAT, SKANODEs | KAN与其他架构集成的可行性验证 |
| Wiener模型在传感器补偿 | Willemstein | WH架构用于传感器滞回补偿 |
| AFMAE理论基础 | Birpoutsoukis | Volterra级数正则化理论 |
| 基准测试定位 | Champneys | W-H基准包含在内 |
| 神经网络方法有效性 | EEMD-GRNN (caveats) | 预处理+NN方法验证 |

## 对文档的影响

### 更新文件：
1. `verified_literature.md` - 新增5个验证条目（KAT, SKANODEs, Willemstein, Birpoutsoukis, Champneys）
2. `raw_literature.md` - 更新状态为Verified (R14)
3. `SUMMARY.md` - 如分析结果改变理论认知

### 新增 verified 条目：
1. **KAT (Yang, Wang 2024)** - MEDIUM relevance - KAN+Transformer混合
2. **SKANODEs (Liu 2025)** - HIGH relevance - KAN+Neural ODE框架
3. **Wiener-Hammerstein Actuators (Willemstein 2023)** - HIGH relevance - WH用于传感器补偿
4. **Volterra Series (Birpoutsoukis 2018)** - HIGH relevance - Volterra理论基础
5. **Benchmarks (Champneys 2024)** - HIGH relevance - 基准测试背景

### 新增 excluded 条目：
1. **REDOX Reactions (Silva 2024)** - 领域不匹配

## 分析报告引用
- 本报告：docs/research/literature/20260328/STEP2_Round14_Analysis.md

## 原始链接
- KAT: https://doi.org/10.48550/arXiv:2409.10594
- SKANODEs: https://arxiv.org/abs/2506.18339
- Willemstein WH: https://arxiv.org/abs/2302.13141
- Birpoutsoukis Volterra: https://arxiv.org/abs/1804.10026
- Champneys Benchmarks: https://arxiv.org/abs/2405.10779
- EEMD-GRNN: https://www.mdpi.com/1424-8220/22/14/5225
- FET Sensor: https://doi.org/10.1016/j.snb.2021.131879

## 关键发现总结

1. **KAT验证了KAN集成可行性** - 但警告naive替换会失败；需要正确的接口设计
2. **SKANODEs提供结构化框架** - KAN+Neural ODE状态空间形式映射到Wiener架构
3. **Wiener-Hammerstein Actuators** - 直接证据表明WH架构成功用于传感器滞回补偿
4. **Volterra Series理论** - 为AFMAE损失函数设计提供正则化理论基础
5. **Benchmarks提供定位框架** - W-H基准是论文比较的重要参考
6. **EEMD-GRNN警告** - 浅层网络+预处理可以达到与深度学习相当的精度

## 理论认知更新

本次分析**未发现需要更新SUMMARY.md的重大发现**：
- KAN稳定性问题（Spotorno 2026）仍然有效
- RNN vs CNN冲突仍然存在
- AFMAE来源（FreDF）仍然有效
- Wiener-KAN架构支撑仍然充分
