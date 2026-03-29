# 调研报告：STEP1 Round 16 - 传感器补偿与测量方法检索

## 基本信息
- 日期：2026-03-28
- 阶段：STEP1 调研
- 覆盖范围：传感器非线性补偿、测量方法论、数据集构建标准
- 是否使用子代理：是；并行4方向（arXiv新论文、传感器补偿、测量方法、数据集标准）

## 检索路径

### 方向1：arXiv 2026年3月新论文
- 关键词：KAN, Wiener, time series, sensor
- 主要数据库：arXiv cs.LG, eess.SY, stat.ML
- 新发现：无3月新发表KAN/Wiener论文

### 方向2：传感器非线性补偿
- 关键词：sensor nonlinearity compensation neural network, electrochemical sensor drift, feedforward compensation
- 主要数据库：Crossref API, arXiv API
- 新发现：10篇传感器补偿论文（部分未在目录中）

### 方向3：测量方法论
- 关键词：sensor calibration, frequency response measurement, MET methodology
- 主要数据库：IEEE Xplore (受限), Google Scholar (受限)
- 新发现：主要依赖已有目录文献（Xu 2008, Schoukens 2017）

### 方向4：数据集构建标准
- 关键词：benchmark dataset, sensor dataset publication, nonlinear system ID
- 主要数据库：arXiv, Zenodo
- 新发现：主要依赖Schoukens组和已有目录文献

## 发现结果

### 新增文献线索（传感器非线性补偿）

| 作者 | 年份 | 标题 | DOI/链接 | 分类 | 相关性 | 状态 |
|------|------|------|----------|------|--------|------|
| Xiangwu Wei | 2013 | Sensor Temperature Compensation Technique Simulation Based on BP Neural Network | 10.11591/telkomnika.v11i6.2687 | P1 | High | New candidate |
| Nancy Kumari, S. Sathiya | 2023 | Performance Enhanced Nonlinearity Compensation of Thermocouple Using CNN | 10.1007/s40031-023-00854-7 | P1 | High | New candidate |
| Shakeb A. Khan et al. | 2003 | Sensor calibration and compensation using artificial neural network | 10.1016/s0019-0578(07)60138-4 | P1 | High | New candidate |
| Shakeb A. Khan et al. | 2014 | ANN Based Online Sensor Calibration and Compensation | 10.47839/ijc.6.3.454 | P1 | High | New candidate |
| Wei Chen, Yuting Shang | 2021 | Neural Network Based Sensor Dynamic System Compensation Algorithm | 10.46719/dsa20213055 | P1 | Medium | New candidate |
| Lachit Dutta et al. | 2018 | Nonlinearity compensation of DIC-based multi-sensor measurement | 10.1016/j.measurement.2018.05.020 | P2 | High | New candidate |
| M.N. Taib, R. Narayanaswamy | 1997 | Multichannel calibration technique for optical-fibre chemical sensor using ANN | 10.1016/s0925-4005(97)80235-3 | P2 | Medium | New candidate |
| Sibo Li, Fan Wei | 2025 | A Composite Sensor Calibration Algorithm Based on Deep Neural Network | 10.62051/ijcsit.v6n2.06 | P1 | High | New candidate |
| Qinbo Sun et al. | 2023 | Deep Neural Network-Based 4-Quadrant Analog Sun Sensor Calibration | 10.34133/space.0024 | P2 | Medium | New candidate |
| Xiaojun Peng et al. | 2015 | A novel pressure sensor calibration system based on neural network | 10.1088/1674-4926/36/9/095004 | P2 | Medium | New candidate |

### 入口已定位

1. **Khan 2003/2014** - 经典ANN传感器校准方法，ISA Transactions高被引
2. **Wei 2013** - BP神经网络温度补偿，可作为传感器漂移补偿方法参考
3. **Kumari 2023** - CNN用于热电偶非线性补偿，接近MET频率响应补偿场景
4. **Dutta 2018** - Measurement期刊，多传感器非线性补偿方法

### 疑似重复/待核实

1. **Li 2025** - 可能与已有深度学习传感器校准论文重叠
2. **Khan 2003/2014** - 同一作者群的两篇论文，内容可能重叠

### 明确排除

1. 无明确排除

## 待核实事项

1. **传感器补偿论文获取** - 需通过机构图书馆或DOI链接获取完整论文
2. **Kumari 2023 CNN方法** - 是否可作为CNN用于传感器补偿的参考文献
3. **Dutta 2018 Measurement期刊** - 该期刊是MET论文发表期刊，可作为实验方法参考

## 对文档的影响

- 更新文件：raw_literature.md（新增传感器补偿条目）
- 新增 Khan 2003/2014, Wei 2013, Kumari 2023, Li 2025 等条目
- 是否需要更新SUMMARY：否
- 是否需要后续STEP2分析：否（本轮为P2扩展）

## 原始链接

- https://doi.org/10.11591/telkomnika.v11i6.2687 (Wei 2013)
- https://doi.org/10.1007/s40031-023-00854-7 (Kumari 2023)
- https://doi.org/10.1016/s0019-0578(07)60138-4 (Khan 2003)
- https://doi.org/10.47839/ijc.6.3.454 (Khan 2014)
- https://doi.org/10.1016/j.measurement.2018.05.020 (Dutta 2018)
- https://doi.org/10.62051/ijcsit.v6n2.06 (Li 2025)
