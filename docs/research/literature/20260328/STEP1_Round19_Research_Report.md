# 调研报告：Round 19 文献补充调研

## 基本信息
- 日期：2026-03-28
- 阶段：STEP1 调研
- 覆盖范围：KAN网络最新应用、频域损失函数、传感器漂移补偿深度学习方法
- 是否使用子代理：是；并行维度：4个检索方向（Wiener模型、KAN网络、频域损失、传感器漂移）

## 检索路径
- 关键词：
  - KAN: KAN 2025, Kolmogorov-Arnold Networks time series, KAN sensor
  - 频域损失: frequency domain loss, spectral loss, AFMAE
  - 传感器漂移: deep learning sensor drift compensation, electrochemical sensor drift
- 主要数据库：arXiv, Google Scholar, IEEE Xplore
- 新发现数据库：arXiv (主要来源)
- 检索式：参见各子代理检索结果

## 发现结果
### 新增文献线索：
1. **KAN-HAR** (2508.11186): KAN用于人体活动识别，单3轴加速度计数据集，竞争力精度+更少参数
2. **KANFormer** (2512.05734): KAN+Transformer用于限价订单，膨胀因果卷积+KAN增强
3. **KFS** (2508.00635): KAN自适应频率选择，Parseval定理启发
4. **TSKANMixer** (2502.18410): KAN+MLP-Mixer用于时间序列，AAAI 2025 AI4TS workshop接受
5. **Process-Informed KAN** (2509.20349): 物理信息KAN用于制药业，冻干温度预测
6. **Stiff Circuit KAN** (2510.24727): KAN+Crossformer用于ADC电路建模，SPICE仿真验证
7. **Olfactory LLM** (2502.07796): LLM+图神经网络用于气味识别，带漂移补偿

### 入口已定位：
- arXiv KAN时间序列文献覆盖完整
- 传感器漂移补偿新方法（LLM+图神经网络）

### 疑似重复：
- KAN vs LSTM (2511.18613) 已在catalog中
- Fourier-KAN-Mamba (2511.15083) 已在catalog中
- FREDF/Fire等频域损失文献已覆盖

### 明确排除：
- 无

## 待核实事项
- KAN-HAR (2508.11186): 需要验证是否使用前馈补偿架构
- KANFormer (2512.05734): 金融领域应用，需评估与论文相关性
- Olfactory LLM (2502.07796): 漂移补偿方法是否可借鉴

## 对文档的影响
- 更新了 `literature_catalog.md`：新增 R19 KAN应用和传感器补偿条目
- 更新了 `raw_literature.md`：新增 Round 19 两个表格
- 是否需要更新 SUMMARY：否
- 是否需要后续 STEP2 分析：建议后续核实上述新条目

## 原始链接
- https://arxiv.org/abs/2508.11186
- https://arxiv.org/abs/2512.05734
- https://arxiv.org/abs/2508.00635
- https://arxiv.org/abs/2502.18410
- https://arxiv.org/abs/2509.20349
- https://arxiv.org/abs/2510.24727
- https://arxiv.org/abs/2502.07796
