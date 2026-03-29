# STEP2 分析报告

**日期**: 2026-03-27
**阶段**: STEP2 - 深度文献分析

## 分析覆盖范围

| 类别 | 分析论文数 | 已验证 | 已排除 |
|------|-----------|--------|--------|
| KAN 网络 | 4 | 4 | 0 |
| Wiener 模型 | 2 | 2 | 0 |
| 频域损失 | 3 | 3 | 0 |
| 漂移补偿 | 3 | 2 | 1 |
| 架构效率 | 3 | 2 | 1 |
| **总计** | **15** | **13** | **2** |

## 关键发现

### 1. KAN 理论 (Liu et al., 2024)

Kolmogorov-Arnold 定理提供理论基础：
- f(x) = sum Phi_q(sum phi_qp(x_p))
- B样条参数化用于可学习的单变量函数
- 基于边的激活（非像 MLP 那样基于节点）

### 2. Wiener-KAN 连接 (Cruz et al., 2025)

项目关键论文：
- 用于 Wiener-Hammerstein 系统的状态空间 KAN
- 架构：SS-KAN = 线性(A,B,C,D) + KAN_f + KAN_g
- 表明 KAN 能学习物理饱和非线性
- 权衡：可解释性 vs 准确性

### 3. 频域损失

未找到 AFMAE - 改用 Focal Frequency Loss：
- FFL (Jiang et al., 2021)：自适应聚焦于困难频率
- SAMFre (Wang et al., 2025)：FFT + 锐度感知最小化
- 设计原则：频域感知 + 自适应加权

### 4. 漂移补偿

已验证方法：
- TDACNN：基于 CNN 的域适应（无需目标数据）
- KD E-nose：用于漂移缓解的知识蒸馏

## 识别的文献空白

| 空白 | 需采取的行动 |
|------|-------------|
| AFMAE 来源 | 使用 FFL 作为理论基础 |
| KAN vs LSTM/GRU 效率 | TKAN 提供部分数据 |
| 用于时间序列的 Transformer | 如需声明则需补充 |
| RVTDCNN PA 线性化 | 如需比较则需补充 |
| 数据集构建 | 如需声明则需补充 |

## 已更新的文档

- verified_literature.md：已验证 13 篇论文
- excluded_literature.md：已排除 2 篇论文
- SUMMARY.md：待用新发现更新

## 下一步

1. 用新的理论发现更新 SUMMARY.md
2. 验证待处理的论文（PowerMLP、KAN 2.0）
3. 如论文声明需要则解决文献空白
4. 如需要考虑搜索 Transformer 时间序列相关文献
