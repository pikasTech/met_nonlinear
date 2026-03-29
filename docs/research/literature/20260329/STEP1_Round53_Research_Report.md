# 调研报告：STEP1 Round53 - 系统性文献检索扩充

## 基本信息
- 日期：2026-03-29
- 阶段：STEP1 调研
- 覆盖范围：P0/P1/P2核心方向系统检索 + 缺口验证
- 是否使用子代理：是；3个并行方向（arXiv新论文、MEASUREMENT期刊、IEEE/传感器应用）

## 检索路径

### 子代理1：arXiv新论文核查（2026年3月下旬）
- 关键词：KAN, Wiener, Hammerstein, frequency domain, spectral loss, sensor drift
- 主要数据库：arXiv (cs.LG, stat.ML, eess.SY)
- 检索式：标题/摘要关键词匹配
- 结果：无新增高相关性文献

### 子代理2：MEASUREMENT期刊论文搜索
- 关键词：sensor nonlinearity, sensor drift, temperature compensation, neural network calibration
- 主要数据库：Google Scholar, CrossRef
- 结果：大部分论文已在数据库中，新发现1篇（Schaller 2025已收录）

### 子代理3：IEEE/传感器应用KAN论文搜索
- 关键词：Kolmogorov-Arnold Network, KAN, Wiener model, sensor application
- 主要数据库：IEEE Xplore, arXiv
- 结果：发现4篇新论文

---

## 发现结果

### 1. 新增高相关性论文

#### KAN传感器应用（新发现）
| 作者 | 年份 | 标题 | 链接 | 类别 | 相关度 | 状态 |
|------|------|-------|------|-----|-----|--------|
| Cartocci等 | 2025 | 用于工作场所跌倒 injury reduction的AI (RNN+KAN传感器) | https://arxiv.org/abs/2505.24507 | P0 | 高 | **新增 (R53)** |
| Tew等 | 2025 | KANS: 工业过程软传感知识发现图注意力网络 | https://arxiv.org/abs/2501.02015 | P0 | 高 | **新增 (R53)** |
| Lai等 | 2024 | KAN-RCBEVDepth: 自动驾驶多模态融合 | https://arxiv.org/abs/2408.02088 | P1 | 高 | **新增 (R53)** |
| Duarte等 | 2025 | 柔性电子模拟构建模块的函数逼近 | https://arxiv.org/abs/2502.01489 | P1 | 中 | **新增 (R53)** |

#### KAN系统识别/时序应用
| 作者 | 年份 | 标题 | 链接 | 类别 | 相关度 | 状态 |
|------|------|-------|------|-----|-----|--------|
| Cruz等 | 2025 | State-Space KAN for Wiener-Hammerstein系统识别 | https://arxiv.org/abs/2506.16392 | P0 | 高 | 已收录(R53待核实) |
| Liu等 | 2025 | SKANODEs: 结构化KAN神经ODE | https://arxiv.org/abs/2506.18339 | P0 | 高 | 已收录(R53待核实) |
| Gashi等 | 2025 | KAN系统辨识：降压转换器案例 | https://arxiv.org/abs/2506.10434 | P1 | 高 | 已收录(R53待核实) |

### 2. arXiv新论文确认

**无新增高相关性文献**。共核查2026年3月25-29日arXiv提交论文，无KAN/Wiener/频域损失/传感器漂移直接相关新论文。

### 3. 文献库完整性确认

| 类别 | 已收录数量 | 目标 | 状态 |
|------|------------|------|------|
| KAN网络 | 50+篇 | - | ✅ 已完备 |
| Wiener模型 | 30+篇 | - | ✅ 已完备 |
| 频域损失函数 | 20+篇 | - | ✅ 已完备 |
| 漂移补偿 | 25+篇 | - | ✅ 已完备 |
| 架构效率 | 15+篇 | - | ✅ 已完备 |
| MEASUREMENT期刊 | 85篇 | 50篇 | ✅ 超额完成 |

---

## 待核实事项

- Cartocci 2025等4篇新论文需在后续STEP2中验证
- 已有文献库覆盖完整，可进入论文撰写阶段

---

## 对文档的影响

- 更新了 `raw_literature.md`：新增4篇论文
- 更新了 `literature_catalog.md`：添加Round53报告索引
- 是否需要更新 SUMMARY：否
- 是否需要后续 STEP2 分析：建议对新发现论文进行验证

---

## 原始链接

### KAN传感器应用新论文
- https://arxiv.org/abs/2505.24507 - Cartocci等 (2025) RNN+KAN跌倒检测
- https://arxiv.org/abs/2501.02015 - Tew等 (2025) KANS软传感
- https://arxiv.org/abs/2408.02088 - Lai等 (2024) KAN-RCBEVDepth
- https://arxiv.org/abs/2502.01489 - Duarte等 (2025) 模拟KAN