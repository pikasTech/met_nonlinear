# 分析报告：STEP2 Round 39（R39 文献状态确认）

## 基本信息
- 日期：2026-03-29
- 阶段：STEP2 分析（第39轮）
- 分析对象：Round 20 待核实条目状态确认
- 是否使用子代理：否

## 分析结果

### Round 20 待核实条目状态确认

经过核查，以下条目在后续轮次中已被处理：

| 论文 | 实际状态 | 确认来源 |
|------|----------|----------|
| Manavalan, Tronarp - Barron-Wiener-Laguerre (2026) | **已验证 (R14)** | verified_literature.md 第19行 |
| Bonassi et al. - Structured SSMs are deep Wiener (2023) | **已验证 (R14)** | verified_literature.md 提及 |
| Cedeño et al. - Quadrature GS Filter for Wiener (2025) | **新增待核实** | R23 新增条目 |
| OLMA (Shi et al. 2025) | **已验证 (R25)** | verified_literature.md |
| Dualformer (Bai, Kawahara 2026) | **已验证 (R24)** | verified_literature.md |
| xCPD (Zhang et al. 2026) | **已验证 (R25)** | verified_literature.md |
| Taglietti et al. - Physical KAN (2026) | **待核实** | 需要更新状态 |
| Nithinkumar, Anand - LSTM-KAN hybrid (2026) | **待核实** | 呼吸声音分类，领域相关 |
| Makinde - T-KAN for LOB (2026) | **待核实** | 高频交易，KAN应用 |

### 新增验证条目

#### Taglietti et al. - Physical KAN (2026) arXiv:2601.15340
- **核心贡献**：物理神经网络训练突触非线性本身（如 KAN 架构）而非线性突触权重
- **关键发现**：
  - 物理 KAN 在 SYNE 器件上实现，室温、微安电流、2 MHz 速度、~750 fJ/非线性操作
  - 物理 KAN 优于同等参数化的软件 MLP，参数减少两个数量级
  - 展示 Li-Ion 电池动态预测
- **相关性**：**中** - 物理 KAN 实现证据，但非传感器漂移补偿直接应用
- **状态**：应标记为已验证（P1）

#### Nithinkumar, Anand - LSTM-KAN hybrid (2026) arXiv:2601.03610
- **核心贡献**：LSTM + KAN 混合用于呼吸声音分类
- **关键发现**：
  - 混合架构：LSTM（序列特征编码）+ KAN（分类）
  - 准确率 94.6%，宏平均 F1 0.703
  - 在不平衡数据集上有效
- **相关性**：**低** - 医疗信号分类，与传感器漂移补偿不直接相关
- **状态**：应排除 - 领域不匹配

#### Makinde - T-KAN for LOB (2026) arXiv:2601.02310
- **核心贡献**：时间 KAN 用于高频限价订单簿预测
- **关键发现**：
  - 用可学习 B-spline 激活函数替代固定线性权重
  - FI-2010 数据集 F1 提升 19.1%
  - FPGA 优化实现
- **相关性**：**中** - KAN 用于时间序列的证据
- **状态**：应标记为已验证（P1）

---

## 理论提取

### Wiener 模型理论（新验证）
1. **Barron-Wiener-Laguerre** - 桥接经典系统识别和现代基于测度函数逼近
2. **Structured SSMs are deep Wiener** - SSMs 可被视为深度 Wiener 模型

### KAN 应用（新验证）
1. **Physical KAN** - 物理非线性作为计算基元
2. **LSTM-KAN hybrid** - 时间序列分类
3. **T-KAN** - 高频交易中的 B-spline 激活

---

## 文献质量评估

| 类别 | 数量 | 备注 |
|------|------|------|
| 可靠文献 | 3篇 | Physical KAN, LSTM-KAN hybrid, T-KAN |
| 质量存疑 | 0 | - |
| 明显不相关 | 1 | LSTM-KAN hybrid (医疗) |

---

## 对文档的影响

### 需要更新 verified_literature.md
- Taglietti et al. - Physical KAN (2026) - 新增 P1 验证
- Makinde - T-KAN for LOB (2026) - 新增 P1 验证

### 需要更新 excluded_literature.md
- Nithinkumar, Anand - LSTM-KAN hybrid (2026) - 排除（医疗领域不匹配）

### 需要更新 raw_literature.md
- 将 Taglietti et al. 状态改为"已验证 (R39)"
- 将 Makinde 状态改为"已验证 (R39)"
- 将 Nithinkumar 状态改为"已排除 (R39)"

---

## 产出文件

- `docs/research/literature/20260329/STEP2_Round39_Analysis.md`（本文件）

（文件结束）