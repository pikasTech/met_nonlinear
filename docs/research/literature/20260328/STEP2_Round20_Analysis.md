# 分析报告：STEP2 Round 20 综合分析

## 基本信息
- 日期：2026-03-28
- 阶段：STEP2 分析
- 分析对象：Round 20 待核实文献（KAN网络、Wiener模型、频域损失、传感器漂移、架构效率）
- 是否使用子代理：是；并行分析 4 个主题方向

## 理论提取

### KAN 网络新发现

**核心贡献**：
1. **T-KAN (Makinde 2026)** - 高相关：Temporal KAN 使用 B-spline 替代固定线性 LSTM 权重，展示"死区"可解释性，FPGA 优化实现低延迟
2. **物理 KAN (Taglietti 2026)** - 中相关：物理 KAN 在硅光子学器件中实现，训练突触非线性而非固定权重，2 个数量级更少参数
3. **物理信息 KAN (Sen 2025)** - 高相关：强制 Ehrenfest 约束，仅 200 样本 vs TCN 3700 样本
4. **KAN 用于 VIX (Cho 2025)** - 高相关：可解释符号闭合形式，参数效率 vs MLP

**关键发现**：
- KAN 2.0 (Liu 2024) 非新架构，是 pykan 工具包的科学发现功能扩展
- SSM = 深度 Wiener 模型（Bonassi 2023）- 直接支持 Wiener-KAN 架构
- LSTM-KAN 混合架构进一步验证（RNN→KAN 模式）

### Wiener 模型新发现

**核心贡献**：
1. **Bonassi 2023** - 高：SSM 是深度 Wiener 模型（IFAC 2024）- 直接理论桥梁
2. **Colburn 2024** - 高：函数 Wiener 滤波器（FWF）- 闭合形式核自适应滤波
3. **Cedeño 2025** - 中：高斯和滤波器用于 Wiener 系统状态估计
4. **Dželo 2024** - 中：黑盒 Hammerstein-Wiener 逆变器辨识

**关键发现**：
- Wiener 系统与深度 SSM 的形式等价为 Wiener-KAN 提供理论基础
- 函数 Wiener 滤波器概念与 KAN 非线性逼近平行

### 频域损失新发现

**核心贡献**：
1. **OLMA (Shi 2025)** - 高：证明酉变换可降低边缘熵（误差下界），DFT/DWT 监督机制
2. **Dualformer (Bai 2026)** - 中：分层频率采样，保留高频细节
3. **xCPD (Zhang 2026)** - 中：ICLR 2026，频带划分和通道路由机制

**关键发现**：
- OLMA 提供频域损失的理论基础（熵减原理）
- 与 FreDF (Wang ICLR 2025) 理论互补

### 传感器漂移补偿新发现

**核心贡献**：
1. **Warner 2020** - 高：Context+Skill 感知系统，漂移建模为上下文信息
2. **Zhang 2026 Taiji-2** - 中：引力参考传感器标定，工程标定方法

**关键发现**：
- Warner 2020 提供传感器漂移数据驱动方法论参考
- Taiji-2 方法为传统标定，非深度学习

### KAN 效率新发现

**核心贡献**：
1. **BiKA (Liu 2026)** - 高：二进制 KAN 加速器，FPGA 51.54% 资源减少

**冲突确认**：
- Gaonkar 2026 (KAN vs MLP) 与 Spotorno 2026 (MLP > KAN) 冲突
- XNet (Li 2024) 声称优于 KAN - 需进一步核实

## 文献质量评估

### 可靠文献（已验证 R20）
| 论文 | 相关度 | 理由 |
|------|--------|------|
| Bonassi 2023 (SSM=Wiener) | 高 | IFAC 2024，形式等价证明 |
| Colburn 2024 (FWF) | 高 | 直接涉及 Wiener-KAN 概念 |
| Makinde 2026 (T-KAN) | 高 | B-spline 可解释性，FPGA 优化 |
| Sen 2025 (Physics KAN) | 高 | 数据效率， Ehrenfest 约束 |
| Cho 2025 (VIX KAN) | 高 | 可解释性，参数效率 |
| OLMA (Shi 2025) | 高 | 熵减理论，频域损失基础 |
| Warner 2020 | 高 | 传感器漂移上下文自适应 |
| BiKA 2026 | 高 | KAN 硬件效率 |

### 排除文献（Round 20）
| 论文 | 理由 |
|------|------|
| COMET-SG1 (Gogoi 2026) | 非 KAN 相关，轻量级时序模型 |
| Tiny-TSM (Birkel 2025) | 非 KAN 相关，TS 基础模型 |
| NanoHydra (Cioflan 2025) | CNN 基础，非 KAN |
| Shibata 2025 | CNN 基础，FPGA 振动识别 |

## 审稿意见支撑

| 审稿意见 | 支撑文献 | 支撑内容 |
|----------|---------|---------|
| KAN vs MLP 效率 | BiKA 2026, Cho 2025 | KAN 硬件效率，可解释性 |
| Wiener-KAN 架构 | Bonassi 2023 | SSM = 深度 Wiener |
| 频域损失理论基础 | OLMA 2025 | 熵减原理 |
| 传感器漂移 | Warner 2020 | Context+Skill 框架 |

## 对文档的影响

- 更新了 `verified_literature.md`：新增 21 篇验证条目
- 更新了 `raw_literature.md`：Round 20 条目标记为已验证/已排除
- 更新了 `SUMMARY.md`：新增 R20 关键发现
- 是否需要更新 SUMMARY：是

## 原始链接

- Bonassi 2023: https://arxiv.org/abs/2312.06211
- Colburn 2024: https://arxiv.org/abs/2402.03497
- Makinde 2026: https://arxiv.org/abs/2601.02310
- Sen 2025: https://arxiv.org/abs/2509.18483
- Cho 2025: https://arxiv.org/abs/2502.00980
- OLMA 2025: https://arxiv.org/abs/2505.11567
- Warner 2020: https://arxiv.org/abs/2003.07292
- BiKA 2026: https://arxiv.org/abs/2602.23455
- Liu 2024 KAN 2.0: https://arxiv.org/abs/2408.10205
