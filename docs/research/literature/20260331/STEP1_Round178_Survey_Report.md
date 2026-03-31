# 调研报告：STEP1 Round 178 - arXiv KAN/Wiener文献搜索

## 基本信息
- 日期：2026-03-31
- 阶段：STEP1 arXiv文献搜索
- 覆盖范围：KAN网络、Wiener模型、频域损失

## arXiv搜索结果

### KAN论文搜索 (540结果)

| 论文ID | 标题 | 数据库状态 | GAP支撑 |
|--------|------|----------|---------|
| 2603.25755 | KANEL: KAN Ensemble Learning for Virtual Screening | 待添加 | P1 |
| 2603.23854 | Symbolic-KAN: 离散符号结构KAN | 已在库(R35) | P1 (排除) |
| 2603.21807 | Many-body Mobility Edges via KAN | 已在库(R35) | P2 |
| 2603.20184 | KaCGM: KAN因果生成模型 | 已在库(R62) | P1 |
| 2603.18548 | SINDy-KANs: 稀疏非线性动力学 | 已在库(R62) | P2 (排除) |
| 2603.17230 | KANtize: 低比特量化KAN | 已在库(R163) | GAP9 |
| 2603.16679 | HMAR: 医学图像检索+KAN | 待添加 | P2 |
| 2603.15250 | In-Context Symbolic Regression for KAN | 待添加 | P1 |
| 2603.15203 | KAN核质量修正 | 待添加 | P2 |
| 2603.15109 | PAKAN: 像素自适应KAN | 待添加 | P2 |
| 2603.08583 | DFKAN: 双阶段KAN | 已在库(R174) | GAP9 |
| 2603.04827 | Multilevel Training for KAN | 已在库(R168) | GAP9 |
| 2603.03486 | DKD-KAN: 知识蒸馏KAN | 待添加 | GAP9 |
| 2603.01165 | VIKIN: KAN/MLP可重构加速器 | 已在库(R163) | GAP9 |
| 2603.00482 | TokenCom: VLM+KAN | 待添加 | P2 |
| 2602.23455 | BiKA: 二值化KAN硬件 | 待添加 | GAP9 |
| 2602.22777 | KMLP: KAN+gMLP混合 | 待添加 | P1 |
| 2602.22055 | PI-KAN: 物理信息KAN | 待添加 | P0 |
| 2602.20497 | LESA: 扩散模型+KAN | 待添加 | P2 |
| 2602.20413 | KANDy: KAN动力学系统 | 待添加 | P1 |

### Wiener模型搜索 (5结果)

| 论文ID | 标题 | 数据库状态 | GAP支撑 |
|--------|------|----------|---------|
| 2412.07370 | Multiplant Nonlinear System Identification (多核神经网络) | 已在库 | GAP4 |
| 2204.03125 | Deep Transfer Learning for System ID (LSTM) | 待添加 | P1 |
| 2104.05942 | Recurrent Equilibrium Networks (可表示Wiener/Hammerstein) | 待添加 | GAP4 |
| 2012.07697 | Nonlinear State-Space ID via Deep Encoder (Wiener-Hammerstein基准) | 已在库 | GAP4 |
| 1810.06637 | Koopman Operator for Soft Robot (vs Wiener) | 待添加 | P1 |

## 新增候选论文

### 高优先级 (P0-P1)

1. **PI-KAN (2602.22055)** - 物理信息KAN
   - 适用于: 物理约束建模
   - 支撑: Wiener-KAN物理约束融合

2. **KMLP (2602.22777)** - KAN+gMLP混合
   - 适用于: 混合架构设计
   - 支撑: Wiener-KAN架构创新

3. **DKD-KAN (2603.03486)** - 知识蒸馏KAN
   - 适用于: 轻量级部署
   - 支撑: GAP9计算效率

### 中优先级 (P2)

4. **LESA (2602.20497)** - 扩散模型加速
5. **PAKAN (2603.15109)** - 图像融合
6. **BiKA (2602.23455)** - 二值化KAN硬件加速

## GAP支撑状态确认

| GAP编号 | 主题 | 状态 | 本轮搜索补充 |
|---------|------|------|-------------|
| GAP1 | 电化学地震检波器频响漂移 | ✅ 已支撑 | 无 |
| GAP2 | 线性度测量范围 | ⚠️ 低缺口 | PI-KAN物理约束可能适用 |
| GAP3 | 震级因素与频率漂移 | ⚠️ 低缺口 | 需要实验数据 |
| GAP4 | 非线性建模 | ✅ 已支撑 | KMLP混合架构可参考 |
| GAP5 | 震级因子建模 | ⚠️ 低缺口 | 需要实验数据 |
| GAP6 | 力反馈量程限制 | ⚠️ 低缺口 | 已有文献支撑 |
| GAP7-GAP11 | 前馈/频域损失 | ✅ 已支撑 | 无 |

## 结论

1. **arXiv搜索完成**: KAN论文540篇，Wiener论文5篇
2. **文献库状态**: 大部分相关论文已在库(R163-R174轮次已收录)
3. **新增候选**: 识别6篇潜在相关论文待添加到数据库
4. **GAP状态**: 4个低缺口(GAP2/3/5/6)可通过实验数据解决

## 建议行动

1. **优先添加PI-KAN**: 物理信息KAN可能支撑Wiener-KAN物理约束设计
2. **验证新增论文**: 检查6篇候选论文的PDF和摘要
3. **GAP2/3/5**: 低缺口可能需要自己的实验数据来支撑

## 报告生成时间：2026-03-31
## 调研轮次：Round 178
