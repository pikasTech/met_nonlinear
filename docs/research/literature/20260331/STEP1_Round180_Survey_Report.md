# 调研报告：STEP1 Round 180 - Round 178候选论文二次验证

## 基本信息
- 日期：2026-03-31
- 阶段：STEP1 arXiv文献二次验证
- 覆盖范围：Round 178识别的arXiv新候选论文完整验证
- 是否使用子代理：否

## 检索路径
- 关键词：PI-KAN、KMLP、DKD-KAN、BiKA、KANEL、LESA、In-Context Symbolic Regression
- 主要数据库：arXiv
- 检索式：针对Round 178候选论文的逐一验证

---

## 发现结果

### Round 178候选论文验证状态

| 文献ID | 论文名称 | 验证状态 | 数据库记录 | 说明 |
|--------|---------|---------|------------|------|
| 2602.22055 | PI-KAN: Vessel Shaft Power Prediction | **新增候选** | 不冲突 | 不同于已有PIKAN(电力系统)，海事应用物理信息KAN |
| 2602.22777 | KMLP: KAN+gMLP Hybrid | 已在库 | R17/R138 | Web规模表格数据混合架构 |
| 2603.03486 | DKD-KAN: Knowledge Distilled KAN | 已在库 | R22/R74 | 入侵检测轻量化 |
| 2602.23455 | BiKA: Binary KAN Accelerator | 已在库 | R17/R22/R163/R139 | FPGA资源降低27-51% |
| 2603.25755 | KANEL: KAN Ensemble for Virtual Screening | **待定** | R148评估为不相关 | 化学应用，与本研究领域不匹配 |
| 2602.20497 | LESA: Diffusion Model Acceleration | **未收录** | 未找到 | CVPR 2026，扩散模型加速，与GAP无直接关联 |
| 2603.15250 | In-Context Symbolic Regression for KAN | 已在库 | R33/R74/R100 | 已收录，XAI 2026 |
| 2603.15109 | PAKAN: Pixel Adaptive KAN | 已在库 | 已排除 | 计算机视觉图像融合，已排除 |
| 2603.15203 | Nuclear Mass KAN | 已在库 | 已排除 | 核物理领域，已排除 |

---

## 重点论文分析

### 1. PI-KAN (2602.22055) - 新增候选

**标题**: Physics-Informed Machine Learning for Vessel Shaft Power and Fuel Consumption Prediction: Interpretable KAN-based Approach

**作者**: Hamza Haruna Mohammed, Dusica Marijan, Arnbjørn Maressa

**领域**: 海事运输，船舶轴功率与燃油消耗预测

**核心贡献**:
- 提出物理信息KAN (PI-KAN)整合可解释单变量特征变换与物理信息损失函数
- 泄漏-free链式预测流水线
- 在5艘货船上验证，MAE/RMSE最低，R²最高

**与现有PIKAN的区别**:
- Shuai/Li 2024 PIKAN (2408.06650): 电力系统物理信息KAN
- 本论文: 海事船舶应用，轴功率预测

**GAP支撑分析**:
- GAP4(非线性建模): 可参考其KAN+物理约束混合架构
- GAP7(物理约束集成): 物理信息KAN的链式预测设计可参考

**优先级**: P1 (待添加到raw_literature.md)

### 2. LESA (2602.20497) - 新增候选（低优先级）

**标题**: LESA: Learnable Stage-Aware Predictors for Diffusion Model Acceleration

**作者**: Peiliang Cai, Jiacheng Liu, Haowen Xu, Xinyu Wang, Chang Zou, Linfeng Zhang

**会议**: CVPR 2026

**核心贡献**:
- KAN用于学习扩散模型的时间特征映射
- 多阶段多专家架构，不同噪声级别分配专门预测器
- FLUX.1-dev 5x加速，Qwen-Image 6.25x加速，HunyuanVideo 5x加速

**GAP支撑分析**:
- 与传感器频率响应漂移补偿无直接关联
- 低优先级

**优先级**: P2 (低相关性)

---

## 数据库状态确认

### 已在库的论文（Round 178 "待添加"状态已更新）
- KMLP: 新增 (R17/R138)
- DKD-KAN: 新增 (R22/R74)
- BiKA: 新增 (R17/R22/R163/R139)
- In-Context Symbolic Regression: 已收录 (R33/R74/R100)
- PAKAN: 已排除
- Nuclear Mass KAN: 已排除

### 待添加的新论文
- PI-KAN (2602.22055): 需要添加
- LESA (2602.20497): 低优先级，可选

---

## 对文档的影响

### 需要更新的文件
1. `docs/research/literature/raw_literature.md` - 添加PI-KAN (2602.22055)
2. `docs/research/literature/literature_catalog.md` - 可选添加PI-KAN索引
3. `docs/research/literature/20260331/STEP1_Round180_Survey_Report.md` - 本报告

### 不需要更新
- verified_literature.md (STEP1不修改)
- excluded_literature.md (无新排除项)

---

## 下一步行动

1. **立即执行**: 将PI-KAN (2602.22055)添加到raw_literature.md
2. **可选**: LESA (2602.20497)低优先级，可根据需要决定是否添加
3. **继续**: 监控新的arXiv论文，特别是:
   - KAN + 传感器/信号处理结合的工作
   - Wiener/ nonlinear系统辨识相关
   - 频率响应/时频分析相关

---

## 原始链接

- PI-KAN: https://arxiv.org/abs/2602.22055
- LESA: https://arxiv.org/abs/2602.20497

---

## 报告生成时间：2026-03-31
## 调研轮次：Round 180
## 状态：验证完成，1篇新候选论文待添加(PI-KAN)
