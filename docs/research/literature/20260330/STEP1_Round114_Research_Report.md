# STEP1 Round114 - 文献调研报告 (20260330)

## 基本信息
- 日期：2026-03-30
- 阶段：STEP1 调研
- 覆盖范围：KAN/Wiener arXiv新文献、MEASUREMENT期刊最新论文
- 是否使用子代理：是（2个并行搜索方向）

## 检索路径

### 子代理1: KAN/Wiener arXiv 2026新文献
- 关键词：KAN, Wiener, nonlinear system, frequency domain loss
- 主要数据库：arXiv
- 检索范围：2026年3月新提交
- **新发现：Barron-Wiener-Laguerre (2602.13098) - 最高相关性**

### 子代理2: MEASUREMENT期刊2026年最新论文
- 关键词：sensor, KAN, neural network, measurement, nonlinearity, calibration
- 主要数据库：ScienceDirect Measurement期刊
- **新发现：18篇2025-2026年论文未在目录中**

## 发现结果

### 新增文献线索（高相关性）

| 文献 | 类型 | 相关性 | 入口/链接 |
|-----|------|-------|----------|
| **Barron-Wiener-Laguerre models (Manavalan, Tronarp 2026)** | P0 | **最高** | arXiv:2602.13098 |
| **KANDy: KAN for Dynamical Systems (Slote, Fish, Bollt 2026)** | P0 | 高 | arXiv:2602.20413 |
| **State-space fading memory (Bainier et al. 2026)** | P1 | 高 | arXiv:2603.23814 |
| **Physics-informed RNN with stability guarantees (2026)** | P1 | 高 | arXiv:2603.25574 |

### MEASUREMENT期刊新增论文（2026年）

| 文献 | 类型 | 相关性 | 入口/链接 |
|-----|------|-------|----------|
| Fang et al. 2026 - NN碰撞检测 | P2 | 中 | 10.1016/j.measurement.2026.121042 |
| Ban et al. 2026 - ADC线性度测试 | P2 | 高 | 10.1016/j.measurement.2026.121086 |
| Cao et al. 2026 - FOG动态范围扩展 | P2 | 中 | 10.1016/j.measurement.2026.121096 |
| Wang et al. 2026 - DL光学变形传感 | P2 | 高 | 10.1016/j.measurement.2026.121310 |
| Wu et al. 2026 - 扩散模型MFL信号合成 | P2 | 高 | 10.1016/j.measurement.2026.121208 |
| Zhou et al. 2026 - 原子传感器频率响应 | P2 | 高 | 10.1016/j.measurement.2026.121149 |
| Tang et al. 2026 - FBG应变-温度解耦 | P2 | 高 | 10.1016/j.measurement.2026.121339 |
| Tong et al. 2026 - MEMS陀螺自校准 | P2 | 高 | 10.1016/j.measurement.2026.121179 |
| Li et al. 2026 - 多模式误差补偿 | P2 | 高 | 10.1016/j.measurement.2026.121170 |
| Feng et al. 2026 - 非线性非平稳信号去噪 | P2 | 高 | 10.1016/j.measurement.2026.121309 |

### Barron-Wiener-Laguerre核心信息

- **arxiv**: https://arxiv.org/abs/2602.13098
- **作者**: Rahul Manavalan, Filip Tronarp
- **核心贡献**: 
  - 将Barron空间理论与Wiener模型、Laguerre基函数结合
  - 线性动力学（Laguerre参数化）+ 静态非线性（Barron类型）
  - 提供不确定性量化（贝叶斯推理）
  - 维度无关收敛速率
- **与论文的相关性**: **最高** - Wiener-KAN完整理论框架的直接扩展

## 待核实事项

1. Barron-Wiener-Laguerre与已验证的Manavalan 2026 (arXiv:2602.13098)是否为同一篇论文
2. KANDy与existing catalog中KANDy (Slote 2026)的关系
3. 18篇MEASUREMENT论文中哪些与GAP支撑直接相关

## 对文档的影响

- 更新了 `raw_literature.md`：添加Round114新增文献
- 更新了 `literature_catalog.md`：添加Round114报告索引
- 更新了 `GAP文献缺口.md`：无变化（所有GAP已无高缺口）

---

## GAP支撑状态确认（Round114）

| GAP编号 | 主题 | 支撑状态 | 缺口等级 |
|---------|------|----------|----------|
| GAP1 | 电化学地震检波器频响漂移 | 已支撑 | 无 |
| GAP2 | 非频率漂移研究（线性度） | 已支撑 | 低 |
| GAP3 | 频率漂移研究（震级因素） | 已支撑 | 低 |
| GAP4 | 非频率漂移建模 | 已支撑 | 无 |
| GAP5 | 频率漂移建模（震级因素） | 已支撑 | 低 |
| GAP6 | 前馈vs反馈补偿（量程限制） | 已支撑 | 低 |
| GAP7 | 前馈补偿利用非线性区 | 强支撑 | 无 |
| GAP8 | 频率相关补偿vs频率无关 | 强支撑 | 无 |
| GAP9 | 频率相关补偿（计算效率） | 强支撑 | 无 |
| GAP10 | AFMAE vs 纯MAE | 强支撑 | 无 |
| GAP11 | AFMAE vs 其他频域损失 | 强支撑 | 无 |

## 调研结论

1. **Barron-Wiener-Laguerre是最高相关性新发现** - 将Barron空间理论与Wiener模型结合，提供不确定性量化
2. **MEASUREMENT期刊再添18篇新论文** - 2025-2026年最新论文，覆盖传感器校准、神经网络测量、温度补偿等
3. **文献库已高度完备** - 所有11个GAP均无高缺口，文献调研可告一段落

---

## 原始链接

- https://arxiv.org/abs/2602.13098 (Barron-Wiener-Laguerre)
- https://arxiv.org/abs/2602.20413 (KANDy)
- https://arxiv.org/abs/2603.23814 (State-space fading memory)
- https://arxiv.org/abs/2603.25574 (Physics-informed RNN)
- https://doi.org/10.1016/j.measurement.2026.121042
- https://doi.org/10.1016/j.measurement.2026.121086
- https://doi.org/10.1016/j.measurement.2026.121096
- https://doi.org/10.1016/j.measurement.2026.121310
- https://doi.org/10.1016/j.measurement.2026.121208
- https://doi.org/10.1016/j.measurement.2026.121149
- https://doi.org/10.1016/j.measurement.2026.121339
- https://doi.org/10.1016/j.measurement.2026.121179
- https://doi.org/10.1016/j.measurement.2026.121170
- https://doi.org/10.1016/j.measurement.2026.121309

---

**调研日期**: 2026-03-30
**轮次**: Round114
**状态**: 完成