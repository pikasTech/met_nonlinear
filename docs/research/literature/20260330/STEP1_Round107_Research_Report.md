# 调研报告：MEASUREMENT期刊传感器漂移补偿文献（STEP1 Round107）

## 基本信息
- 日期：2026-03-30
- 阶段：STEP1 调研
- 覆盖范围：MEASUREMENT期刊传感器漂移补偿方法（2020-2025）
- 是否使用子代理：是；并行维度：三个独立搜索方向（Feedforward vs Feedback、GAP2线性度、MEASUREMENT期刊）

## 检索路径

### 方向1：Feedforward vs Feedback补偿（针对GAP6）
- 关键词：
  - "feedforward feedback compensation" sensor
  - "force feedback" limitation range
  - "feedforward nonlinear" sensor compensation
- 主要数据库：IEEE Xplore, Google Scholar, JASA

### 方向2：传感器线性度测量范围（针对GAP2）
- 关键词：
  - "sensor linearity" measurement range
  - "linearity calibration" nonlinear
  - "measurement range" sensor
- 主要数据库：Measurement期刊, IEEE Sensors

### 方向3：MEASUREMENT期刊传感器补偿方法
- 关键词：
  - "sensor drift compensation" measurement
  - "temperature compensation" neural network sensor
  - "nonlinear calibration" sensor
- 主要数据库：ScienceDirect (Measurement期刊)

## 发现结果

### 新增文献线索

#### 1. MEASUREMENT期刊传感器漂移补偿方法

| 文献 | 类型 | 相关性 | 入口/链接 |
|-----|------|-------|----------|
| Schaller & Kruse 2025 - AutoML框架用于传感器漂移预测 | P2 | 高 | DOI: 10.1016/j.measurement.2025.117097 |
| Harindranath等 2023 - MEMS IMU校准技术综述 | P2 | 中 | DOI: 10.1016/j.measurement.2023.114001 |
| Shokri-Ghaleh等 2020 - 非线性现场校准方法 | P2 | 高 | DOI: 10.1016/j.measurement.2020.107963 |
| Han等 2020 - BP神经网络温度补偿 | P2 | 中 | DOI: 10.1016/j.measurement.2020.108019 |
| Zhao等 2022 - LSTM用于光纤陀螺校准 | P2 | 中高 | DOI: 10.1016/j.measurement.2022.110783 |

### 新增文献摘要

1. **Schaller & Kruse 2025** (DOI: 10.1016/j.measurement.2025.117097)
   - 主题：AutoML用于传感器漂移预测
   - 方法：自动机器学习框架优化传感器漂移补偿模型
   - 相关度：高（传感器漂移补偿方法论）

2. **Harindranath等 2023** (DOI: 10.1016/j.measurement.2023.114001)
   - 主题：MEMS IMU校准技术综述
   - 方法：综述MEMS惯性测量单元的各种校准技术
   - 相关度：中（校准方法参考）

3. **Shokri-Ghaleh等 2020** (DOI: 10.1016/j.measurement.2020.107963)
   - 主题：非线性现场校准方法
   - 方法：现场条件下非线性传感器的校准方法
   - 相关度：高（直接支撑非线性校准方法）

4. **Han等 2020** (DOI: 10.1016/j.measurement.2020.108019)
   - 主题：BP神经网络温度补偿
   - 方法：使用BP神经网络进行传感器温度漂移补偿
   - 相关度：中（神经网络补偿参考）

5. **Zhao等 2022** (DOI: 10.1016/j.measurement.2022.110783)
   - 主题：LSTM用于光纤陀螺校准
   - 方法：长短期记忆网络用于光纤陀螺仪漂移校准
   - 相关度：中高（深度学习补偿参考）

## 待核实事项

1. **Schaller & Kruse 2025**：需确认AutoML框架是否适用于电化学地震传感器的特定漂移模式
2. **Harindranath 2023**：MEMS IMU与电化学传感器的校准方法差异需进一步分析
3. **Shokri-Ghaleh 2020**：现场校准方法的具体实施细节需进一步核实

## 对文档的影响

- 更新了 `raw_literature.md`：新增5篇MEASUREMENT期刊传感器补偿文献
- 更新了 `literature_catalog.md`：如需要
- 是否需要更新 GAP文献缺口：否（本次搜索为补充性搜索）

## 原始链接

- DOI: 10.1016/j.measurement.2025.117097 (Schaller & Kruse 2025)
- DOI: 10.1016/j.measurement.2023.114001 (Harindranath 2023)
- DOI: 10.1016/j.measurement.2020.107963 (Shokri-Ghaleh 2020)
- DOI: 10.1016/j.measurement.2020.108019 (Han 2020)
- DOI: 10.1016/j.measurement.2022.110783 (Zhao 2022)
