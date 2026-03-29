# 调研报告：第33轮arXiv最新文献核查

## 基本信息
- 日期：2026-03-29
- 阶段：STEP1 调研
- 覆盖范围：arXiv最新发表（2026年3月中旬-下旬）
- 是否使用子代理：是；4个并行方向（KAN理论、Wiener/传感器、频域损失、FRIKAN/MET）

## 检索路径
- 关键词：KAN, Wiener, sensor compensation, frequency domain loss, 2026, March
- 主要数据库：arXiv, IEEE Xplore, Google Scholar
- 检索式：组合检索上述关键词

## 发现结果

### 新增文献线索（5条）

| 编号 | 标题 | 作者 | 年份 | arXiv ID | DOI | 相关性 | 状态 |
|------|------|------|------|----------|-----|--------|------|
| 1 | In-Context Symbolic Regression for Robustness-Improved Kolmogorov-Arnold Networks | Sovrano等 | 2026 | 2603.15250 | 10.48550/arXiv.2603.15250 | KAN理论 | 待核实 |
| 2 | A Kolmogorov-Arnold Surrogate Model for Chemical Equilibria: Application to Solid Solutions | Boledi, Bosbach, Poonoosamy | 2026 | 2603.15307 | 10.48550/arXiv.2603.15307 | KAN应用 | 待核实 |
| 3 | Kolmogorov-Arnold causal generative models (KaCGM) | Almodóvar等 | 2026 | 2603.20184 | 10.48550/arXiv.2603.20184 | KAN理论 | 待核实 |
| 4 | Learning to Anchor Visual Odometry: KAN-Based Pose Regression for Planetary Landing (KANLoc) | Luo等 | 2026 | 2602.06968 | 10.48550/arXiv.2602.06968 | KAN传感器 | 待核实 |
| 5 | Radio Map Prediction from Noisy Environment Information and Sparse Observations | Jaensch等 | 2026 | 2602.11950 | 10.48550/arXiv.2602.11950 | 传感器补偿 | 待核实 |

### 已排除/重复（需更新catalog）

| 编号 | 标题 | arXiv ID | 排除原因 |
|------|------|----------|----------|
| 1 | Symbolic-KAN: KAN with Discrete Symbolic Structure | 2603.23854 | 已在catalog为Excluded (R17) |
| 2 | SINDy-KANs | 2603.18548 | 已在catalog为New (R17) |

### 入口已定位（待深入核查）

1. **KANLoc (2602.06968)** - KAN用于视觉里程计，IEEE RA-L接收
   - 32%/45%误差降低，参数效率高
   - 传感器定位应用相关

2. **Radio Map Prediction (2602.11950)** - CNN处理传感器噪声
   - 25%误差降低
   - 传感器噪声补偿方法论相关

## 待核实事项

1. KaCGM (2603.20184) - KAN因果生成模型，需确认是否与现有Wiener-KAN理论有关联
2. KAN surrogate (2603.15307) - 化学平衡代理模型，KAN参数效率证据
3. In-Context Symbolic Regression (2603.15250) - KAN可解释性，XAI 2026接收

## 对文档的影响

- 更新了 `docs/research/literature/literature_catalog.md`：
  - 新增"第33轮新增论文"节
  - 更新"调研报告索引"
- 更新了 `docs/research/literature/raw_literature.md`：
  - 新增KAN新文献条目（5条）
- 是否需要更新 SUMMARY：否
- 是否需要后续 STEP2 分析：待定

## 原始链接

- https://arxiv.org/abs/2603.15250 (In-Context Symbolic Regression for KAN)
- https://arxiv.org/abs/2603.15307 (KAN Surrogate Model for Chemical Equilibria)
- https://arxiv.org/abs/2603.20184 (KaCGM)
- https://arxiv.org/abs/2602.06968 (KANLoc)
- https://arxiv.org/abs/2602.11950 (Radio Map Prediction)

## 产出文件

- `docs/research/literature/20260329/STEP1_Round33_Research_Report.md` (本文件)
