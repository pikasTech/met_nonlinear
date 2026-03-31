# 调研报告：STEP1 Round 181 - PI-KAN文献录入

## 基本信息
- 日期：2026-03-31
- 阶段：STEP1 文献录入
- 覆盖范围：Round 180识别的PI-KAN新候选论文录入
- 是否使用子代理：否

## 检索路径
- 关键词：PI-KAN、物理信息KAN、船舶轴功率预测
- 主要数据库：arXiv
- 检索式：arXiv:2602.22055

---

## 发现结果

### PI-KAN (2602.22055) 论文信息

| 字段 | 内容 |
|------|------|
| **标题** | Physics-Informed Machine Learning for Vessel Shaft Power and Fuel Consumption Prediction: Interpretable KAN-based Approach |
| **作者** | Hamza Haruna Mohammed, Dusica Marijan, Arnbjørn Maressa |
| **arXiv ID** | 2602.22055 |
| **领域** | 海事运输，船舶轴功率与燃油消耗预测 |
| **发布时间** | 2026年2月 |
| **优先级** | P1 |

### 核心贡献
- 提出物理信息KAN (PI-KAN)整合可解释单变量特征变换与物理信息损失函数
- 泄漏-free链式预测流水线
- 在5艘货船上验证，MAE/RMSE最低，R²最高

### 与现有PIKAN的区别
- Shuai/Li 2024 PIKAN (2408.06650): 电力系统物理信息KAN
- 本论文: 海事船舶应用，轴功率预测

### GAP支撑分析
- GAP4(非线性建模): 可参考其KAN+物理约束混合架构
- GAP7(物理约束集成): 物理信息KAN的链式预测设计可参考

---

## 数据库更新

### 需要更新的文件
1. `docs/research/literature/raw_literature.md` - 添加PI-KAN (2602.22055)
2. `docs/research/literature/literature_catalog.md` - 可选添加PI-KAN索引
3. `docs/research/literature/20260331/STEP1_Round181_Survey_Report.md` - 本报告

---

## 报告生成时间：2026-03-31
## 调研轮次：Round 181
## 状态：PI-KAN文献录入完成