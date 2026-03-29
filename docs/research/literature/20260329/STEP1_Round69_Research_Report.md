# 调研报告：STEP1 Round69 (2026-03-29)

## 基本信息
- 日期：2026-03-29
- 阶段：STEP1 调研（第69轮）
- 覆盖范围：并行三路搜索 - arXiv最新批次(3/27-29)、MEASUREMENT期刊2025-2026年、KAN效率对比文献
- 是否使用子代理：是；并行三个子代理分别执行：arXiv最新批次搜索、MEASUREMENT期刊搜索、KAN效率对比文献搜索

## 检索路径

### 子代理1：arXiv最新批次搜索（3/27-29 2026）
- **数据库**：arXiv (cs.LG, stat.ML, eess.SY)
- **关键词**：KAN, Wiener, sensor drift, time series, frequency domain
- **结果**：无3月27-29日新提交的相关论文

### 子代理2：MEASUREMENT期刊2025-2026年搜索
- **数据库**：ScienceDirect / Google Scholar
- **发现**：大部分论文已在之前轮次收录，仅3篇为新发现

### 子代理3：KAN效率对比文献搜索
- **数据库**：arXiv, Google Scholar
- **发现**：1篇新发现（CKAN效率对比论文）

## 发现结果

### 真正新增MEASUREMENT期刊论文（3篇）

#### 1. Volterra电压互感器谐波补偿
- **作者**：Luca Barbieri, Daniele Palladini, Simone Venturini, Giovanni D'Avanzo, Andrea Villa, Giacomo Buccella, Roberto Malgesini
- **年份**：2025
- **标题**：A novel harmonic compensation technique of voltage transformers through an analytic Volterra-based method
- **DOI**：10.1016/j.measurement.2025.118373
- **相关度**：高
- **说明**：使用解析Volterra方法进行电压互感器谐波补偿，与Wiener/Volterra模型理论直接相关

#### 2. Wiener过程涂层降解建模
- **作者**：Haodi Ji, Yujie Liu, Xiaobing Ma, Han Wang, Yikun Cai, Shuo Jiao
- **年份**：2025
- **标题**：Electrochemical performance monitoring and degradation modeling method for organic coating systems: Integrating three-phase Wiener process and kinetic models
- **DOI**：10.1016/j.measurement.2024.115532
- **相关度**：高
- **说明**：使用三相Wiener过程进行电化学涂层降解建模，与Wiener模型理论相关

#### 3. CNN双传感器校准
- **作者**：Bingqian Li, Hongbin Lin, Mu Li, Rui Zhu, Jie Gao, Fei Xie, Changyin Li, Yungang Zhang
- **年份**：2025
- **标题**：A dual sensor for SO2 concentration and temperature based on ultraviolet differential optical absorption spectroscopy combined with convolutional neural network
- **DOI**：10.1016/j.measurement.2025.117397
- **相关度**：高
- **说明**：使用CNN进行双传感器校准（SO2浓度和温度），与传感器神经网络校准方法相关

### 新增KAN效率对比论文（1篇）

#### 4. CKAN效率分析
- **作者**：Ashim Dahal, Saydul Akbar Murad, Nick Rahimi
- **年份**：2025
- **标题**：Efficiency Bottlenecks of Convolutional Kolmogorov-Arnold Networks: A Comprehensive Scrutiny with ImageNet, AlexNet, LeNet and Tabular Classification
- **DOI**：10.48550/arXiv.2501.15757
- **相关度**：中（重要警示）
- **说明**：系统性分析CKAN效率瓶颈，发现CKAN在小型数据集上比CNN慢，在ImageNet大规模场景下效率远不如CNN

### 已在数据库中的论文（已排除重复）

以下论文经核查已在之前轮次收录：
- 10.1016/j.measurement.2025.117097 - AutoML传感器漂移补偿（已于R21/R35/R51收录）
- 10.1016/j.measurement.2024.115573 - LSTM温度漂移补偿NMR传感器（已于R37收录）
- 10.1016/j.measurement.2025.118227 - Harris鹰优化压阻传感器热漂移（已于R37收录）
- 10.1016/j.measurement.2024.116559 - TPoS微机电气体传感器非线性（已于R21/R35/R51收录）
- 10.1016/j.measurement.2026.120825 - Volterra航磁补偿（已于R68收录）

### 明确排除

- arXiv:2501.15757（CKAN对比CNN效率）— 重要警示：KAN并不总是比CNN高效

## 待核实事项

无新的待核实项。本轮发现的4篇论文均有完整DOI或arXiv编号。

## 对文档的影响

- 更新了哪些文件：
  - raw_literature.md（新增4篇论文）
  - literature_catalog.md（如有需要可更新）
- 是否需要更新raw_literature.md：是
- 是否需要更新literature_catalog.md：否
- 是否需要后续STEP2分析：否

## 原始链接

- Volterra电压互感器：https://doi.org/10.1016/j.measurement.2025.118373
- Wiener过程涂层：https://doi.org/10.1016/j.measurement.2024.115532
- CNN双传感器：https://doi.org/10.1016/j.measurement.2025.117397
- CKAN效率：https://doi.org/10.48550/arXiv.2501.15757

## 结论

第69轮调研通过并行三路搜索，新增4篇论文（3篇MEASUREMENT期刊 + 1篇arXiv KAN效率论文）。

重要发现：CKAN效率论文（arXiv:2501.15757）显示KAN并不总是比CNN高效——在大型数据集（ImageNet）上CKAN效率远不如CNN。这进一步支持了之前的结论：应将效率声称聚焦于特定场景（如边缘LUT加速），而非笼统声称KAN比所有架构更高效。

文献库继续保持完备状态。

---
**调研报告路径**：docs/research/literature/20260329/STEP1_Round69_Research_Report.md
**调研时间**：2026-03-29 09:02