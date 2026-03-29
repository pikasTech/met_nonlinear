# 调研报告：STEP1 Round7 - 并行扩展搜索

## 基本信息
- 日期：2026-03-28
- 阶段：STEP1 调研
- 覆盖范围：P0 Wiener经典论文核实、P1/P2 传感器数据集与方法论、P2 KANet FLOPs核实、P2 MET测量方法论
- 是否使用子代理：是；5个并行搜索维度

## 检索路径

### 子代理1：Wiener模型经典论文核实
- 关键词：Wiener-Hammerstein benchmark, block-oriented nonlinear systems, structure identification
- 主要数据库：Google Scholar, IEEE Xplore, Diva Portal
- 检索式：Schoukens 2009 Wiener-Hammerstein, Haber Unbehauen 1990 structure identification, Bai Giri 2010 block-oriented

### 子代理2：传感器数据集与数据集构建标准
- 关键词：electrochemical sensor dataset, seismic benchmark, E-nose dataset, dataset construction methodology
- 主要数据库：arXiv, Google Scholar, NeurIPS
- 新发现：OpenFWI (NeurIPS 2022), Magrini earthquake dataset, Schoukens & Noël 2017

### 子代理3：传感器非线性补偿方法
- 关键词：sensor nonlinearity compensation, nonlinear calibration, feedforward compensation
- 主要数据库：IEEE Xplore, ScienceDirect, MDPI Sensors
- 状态：已在 raw_literature.md 中有大量文献；确认关键gap：现有工作主要关注DRIFT而非NONLINEARITY

### 子代理4：KANet FLOPs论文与TKAN核实
- 关键词：KANet memory-managed recurrent KAN, TKAN FLOPs, KAN computational efficiency
- 主要数据库：IEEE Xplore, arXiv
- 发现：KANet (Pu 2025 IEEE TIM) - **无法核实**：paywalled，无arXiv preprint；TKAN已核实

### 子代理5：MET测量方法论文献
- 关键词：MET measurement, frequency response measurement, 3D displacement measurement, sensor characterization
- 主要数据库：IEEE TIM, IEEE Sensors, MIT DSpace
- 发现：Xu & Wang 2008 (Measurement), Kumar 2020 (IEEE Sensors), Iqbal 2024 (MIT DSpace)

## 发现结果

### 新增文献线索（已核实）

| 作者 | 年份 | 标题 | DOI/链接 | 分类 | 相关性 | 状态 |
|------|------|------|----------|------|--------|------|
| Schoukens, Ljung | 2009 | Wiener-Hammerstein Benchmark | https://www.diva-portal.org/smash/get/diva2:317004/FULLTEXT01.pdf | P0 | High | Verified |
| Haber, Unbehauen | 1990 | Structure identification of nonlinear dynamic systems—A survey | 10.1016/0005-1098(90)90044-I | P0 | High | Verified |
| Bai, Giri | 2010 | Introduction to Block-oriented Nonlinear Systems | 10.1007/978-1-84996-513-2_1 | P0 | High | Verified |
| Greblicki | 2002 | Nonparametric approach to Wiener system identification | 10.1109/81.983126 | P0 | Medium | Verified |
| Van Mulders et al. | 2013 | Identification of systems with localised nonlinearity | 10.1016/j.automatica.2013.02.006 | P0 | High | Verified |
| Li et al. | 2024 | LSTM-based Wiener model identification | 10.1016/j.ymssp.2024.111386 | P0 | Medium | Verified |
| Deng et al. | 2022 | OpenFWI: Large-Scale Multi-Structural Benchmark Datasets for Seismic FWI | https://arxiv.org/abs/2111.02926 | P2 | High | Pending |
| Magrini et al. | 2020 | Local Earthquakes Detection: A Benchmark Dataset | https://arxiv.org/abs/2008.02903 | P2 | High | Pending |
| Devecioglu et al. | 2024 | High-Quality Seismic Signal Synthesis using Operational GANs | https://arxiv.org/abs/2407.11040 | P2 | Medium | Pending |
| Schoukens, Noël | 2017 | Three Benchmarks for Nonlinear System Identification | 10.1016/j.automatica.2013.02.006 | P2 | High | Pending |
| Xu, Wang | 2008 | Volterra series and frequency response function for sensor block models | 10.1016/j.measurement.2008.03.003 | P2 | High | Pending |

### 待核实线索

| 作者 | 年份 | 标题 | DOI/链接 | 状态 |
|------|------|------|----------|------|
| Pu, Li, Zhou | 2025 | KANet: Memory-Managed Recurrent KAN (IEEE TIM) | 10816574 | **无法核实 - paywalled** |
| Agafonov et al. | 2015 | Electrochemical seismometers (ResearchGate) | - | 待核实 |
| Sun et al. | 2017 | Numerical study of electrochemical seismometer frequency | IEEE | 待核实 |
| Zhou et al. | 2025 | Broadband electrochemical seismometer (IEEE TIM) | IEEE TIM | 待核实 |

### 疑似重复/已排除

- Li et al. 2025 (FRIKAN, TIM-25-06440) - **无法引用**：作者自己的被拒论文，不能作为第三方参考文献

### 明确排除

- KANet FLOPs论文 - 无arXiv preprint，无法独立核实

## 待核实事项

1. **KANet FLOPs数据**：该论文声称KANet比LSTM/GRU有FLOPs优势，但无法核实（paywalled）。建议依赖已验证的TKAN论文作为KAN时序建模基础
2. **FRIKAN论文**：作者自己的TIM-25-06440不能被引用，需通过Kumar 2020、Iqbal 2024等第三方论文来支撑MET测量方法论
3. **电化学地震计MET文献**：Agafonov (2015)、Sun (2017)、Zhou (2025)需进一步核实与MET 3D位移测量的相关性
4. **OpenFWI数据集**：NeurIPS 2022基准数据集，可能与地震信号处理方法有参考价值

## 对文档的影响

- 更新 `docs/research/literature/literature_catalog.md`：
  - 更新 Wiener Model Classical Theory 表格状态：Pending → Verified
  - 新增 Dataset Construction Standards 部分
  - 新增 Sensor Nonlinearity Compensation 部分
- 更新 `docs/research/literature/raw_literature.md`：
  - 新增 Wiener Model Classical Theory 条目（全部Verified）
  - 新增 Dataset Construction Standards 条目
  - 新增 MET Measurement Methodology 条目
- 是否需要更新 SUMMARY：否（SUMMARY反映整体状态，非本轮更新重点）
- 是否需要后续 STEP2 分析：建议对新增的Wiener经典论文做深度分析

## 原始链接

- Wiener-Hammerstein Benchmark: https://www.diva-portal.org/smash/get/diva2:317004/FULLTEXT01.pdf
- Haber 1990: 10.1016/0005-1098(90)90044-I
- Bai 2010: 10.1007/978-1-84996-513-2_1
- Greblicki 2002: 10.1109/81.983126
- Van Mulders 2013: 10.1016/j.automatica.2013.02.006
- Li 2024: 10.1016/j.ymssp.2024.111386
- OpenFWI: https://arxiv.org/abs/2111.02926
- Magrini 2020: https://arxiv.org/abs/2008.02903
- Xu 2008: 10.1016/j.measurement.2008.03.003
- KANet IEEE: https://ieeexplore.ieee.org/abstract/document/10816574/
- TKAN arXiv: https://arxiv.org/abs/2405.07344
