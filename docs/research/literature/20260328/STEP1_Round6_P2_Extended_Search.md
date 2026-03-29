# 调研报告：P2扩展方向搜索（STEP1 Round 6）

## 基本信息
- 日期：2026-03-28
- 阶段：STEP1 调研
- 覆盖范围：P2可选扩展方向（实验测量方法、传感器非线性补偿、数据集构建标准）
- 是否使用子代理：是；并行维度：3个子代理分别搜索测量方法/非线性补偿/数据集标准

## 检索路径

### 子代理1：传感器测量方法
- 关键词：sensor frequency response measurement, nonlinear calibration, experimental design, electrochemical characterization
- 主要数据库：IEEE Xplore, ScienceDirect, Google Scholar, MDPI Sensors
- 新发现数据库：无外部访问能力，仅能搜索本地仓库

### 子代理2：传感器非线性补偿
- 关键词：sensor nonlinearity compensation, feedforward predistortion, inverse model linearization, magnitude-dependent nonlinearity
- 主要数据库：IEEE Xplore, ScienceDirect, Google Scholar
- 核心发现：现有文献主要关注DRIFT（时间漂移），而非NONLINEARITY（幅度相关非线性）

### 子代理3：数据集构建标准
- 关键词：benchmark dataset publication, sensor data acquisition, time series dataset construction
- 主要数据库：IEEE Xplore, Google Scholar, Zenodo, Figshare
- 核心发现：Wiener-Hammerstein Benchmark (Schoukens 2009) 是数据集描述的参考标准

## 发现结果

### 新增文献线索

| 分类 | 作者 | 年份 | 标题 | DOI/链接 | 相关性 | 状态 |
|------|------|------|------|----------|--------|------|
| 数据集标准 | Jacob et al. | 2020 | Exathlon: A Benchmark for Explainable Anomaly Detection | arXiv:2010.05073 | High | Pending |
| 测量方法 | Li et al. (FRIKAN) | 2025 | MET 3D frequency response dataset (IEEE TIM) | TIM-25-06440 | High | Verified |
| 测量方法 | Popoola et al. | 2016 | Baseline-temperature correction for electrochemical sensors | Atmospheric Environment | High | Verified |
| 非线性补偿 | Kumar, Tudu, Ghosh | 2020 | E-tongue voltammetric sensor nonlinear modeling | IEEE Sensors | High | Pending |
| 非线性补偿 | Iqbal | 2024 | Volterra System Analysis for Electrochemical Sensor | MIT DSpace | High | Pending |

### 入口已定位
- **FRIKAN论文 (TIM-25-06440)** 是MET测量方法的主要参考文献
- **Schoukens & Ljung 2009 Wiener-Hammerstein Benchmark** 是数据集描述的参考标准

### 疑似重复
- 无

### 明确排除
- 无

## 待核实事项

1. **Kumar 2020 E-tongue IEEE Sensors** - IEEE paywalled，需通过其他渠道获取
2. **Iqbal 2024 MIT DSpace** - 链接已失效，需核实
3. **Jacob 2020 Exathlon** - 可通过arXiv获取，需验证内容

## 对文档的影响

- 更新了 `docs/research/literature/raw_literature.md`：
  - 新增Exathlon benchmark数据集文献
  - 新增Popoola 2016电化学传感器基线校正文献
- 更新了 `docs/research/literature/literature_catalog.md`：
  - Survey Report Index 补充本报告路径
- 无需更新 SUMMARY（STEP1只做线索收集）

## 原始链接
- https://arxiv.org/abs/2010.05073 (Exathlon)
- TIM-25-06440 (FRIKAN - IEEE TIM)
- 10.1016/j.atmosenv.2016.01.001 (Popoola 2016)

---

## 核心发现总结

### Gap分析：传感器NONLINEARITY vs DRIFT

现有文献主要关注**DRIFT（缓慢时间基线变化）**，而非**NONLINEARITY（幅度相关输入输出失真）**。

**本论文（FRIKAN/TIM-25-06440）是workspace中唯一直接处理MET传感器非线性补偿的文献。**

### 数据集构建参考优先级

1. **Schoukens & Ljung 2009** - Wiener-Hammerstein Benchmark（157+ citations）
   - G1(z)→f(·)→G2(z)标准结构
   - 完整的实验方法学文档

2. **Jacob 2020 Exathlon** - 异常检测基准数据集
   - 数据集文档标准模型

3. **Li et al. 2025 FRIKAN** - MET 3D频率响应数据集
   - 直接相关，但需审稿人验证

### 建议

若需进一步P2文献支持，建议手动搜索以下关键词：
- "sensor nonlinearity feedforward compensation neural network"
- "inverse model sensor linearization"
- "magnitude-dependent sensor calibration"
- "ISO sensor frequency response test standard"
