# 调研报告：STEP1 Round82 - 系统性文献扩充

## 基本信息
- 日期：2026-03-29
- 阶段：STEP1 调研
- 覆盖范围：arXiv最新论文、LUT硬件实现、传感器漂移补偿
- 是否使用子代理：是（并行搜索arXiv KAN/Wiener和传感器/时间序列）

## 检索路径
- 关键词：
  - KAN, Wiener, frequency domain loss
  - sensor drift, time series, LUT implementation
- 主要数据库：arXiv
- 新发现数据库：IEEE Xplore（用于硬件加速）

## 发现结果

### 新增文献线索

| 作者 | 年份 | 标题 | 链接 | 类别 | 相关度 | 状态 |
|------|------|-------|------|-----|-----|--------|
| Liu et al. | 2026 | GRAU: Generic Reconfigurable Activation Unit Design for Neural Network Hardware Accelerators | https://arxiv.org/abs/2602.22352 | P2 | 高 | 新增 (R82) |
| Bührer et al. | 2026 | BitLogic: Training Framework for Gradient-Based FPGA-Native Neural Networks | https://arxiv.org/abs/2602.07400 | P2 | 高 | 新增 (R82) |

### GRAU核心信息
- 提出可重构激活单元，使用分段线性拟合，power-of-two斜率
- LUT消耗减少超过90%（相比multi-threshold激活器）
- 支持混合精度量化和非线性函数
- 与KAN的LUT实现方向相关

### BitLogic核心信息
- 基于LUT的神经网络计算，替代乘累加操作
- CIFAR-10准确率72.3%，使用少于0.3M逻辑门
- 单样本推理<20ns，仅使用LUT资源
- 与KAN LUT效率声称相关

### 入口已定位
- arXiv搜索入口正常运作
- GRAU和BitLogic提供了LUT硬件实现的新视角

### 疑似重复/已存在
- KAN-FIF (Shen 2026) - 已在R51记录
- KANtize (Errabii 2026) - 已在R47记录
- KANELÉ (Hoang 2026) - 已在R4记录

### 明确排除
- 视觉SLAM类论文（与传感器漂移主题部分相关但不直接）

## 待核实事项
- GRAU和BitLogic的具体技术细节
- 这些LUT实现与KAN的B-spline激活函数的关联性

## 对文档的影响
- 更新了哪些文件：raw_literature.md
- 是否需要更新SUMMARY：否
- 是否需要后续STEP2分析：否（基础调研）

## 原始链接
- https://arxiv.org/abs/2602.22352 (GRAU)
- https://arxiv.org/abs/2602.07400 (BitLogic)
