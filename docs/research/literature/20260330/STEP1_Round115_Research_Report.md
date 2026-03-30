# STEP1 Round115 - 文献调研报告 (20260330)

## 基本信息
- 日期：2026-03-30
- 阶段：STEP1 调研
- 覆盖范围：子代理搜索结果处理 - KAN效率、Wiener模型、频域损失
- 是否使用子代理：是（3个并行搜索方向）

## 检索路径

### 子代理1: KAN效率论文搜索
- 关键词：KAN, efficiency, hardware, LUT, FPGA, quantization, time series
- 主要数据库：arXiv 2025-2026
- **发现10篇相关论文**

### 子代理2: Wiener模型论文搜索
- 关键词：Wiener model, Barron-Wiener, system identification, nonlinear
- 主要数据库：arXiv 2025-2026
- **发现10篇相关论文**

### 子代理3: 频域损失论文搜索
- 关键词：frequency domain loss, time series, anomaly detection
- 主要数据库：arXiv, IEEE Xplore
- **发现8篇相关论文**

## 发现结果

### KAN效率论文（新增）

| 文献 | 类型 | 相关性 | 状态 |
|-----|------|-------|------|
| **HaKAN: Hahn Polynomial KAN (Hasan 2026)** | P0 | 高 | 已验证 |
| **WaveTuner: Wavelet Subband+KAN (Wang 2025)** | P0 | 高 | 已验证 |
| **KANELÉ: LUT评估高效KAN (Hoang 2026)** | P2 | 高 | 已验证 |
| **LUT-KAN: 分段LUT量化 (Kuznetsov 2026)** | P2 | 高 | 已验证 |
| **BiKA: 二值KAN (Liu 2026)** | P2 | 高 | 已验证 |
| **KFS: 自适应频率选择KAN (Wu 2025)** | P0 | 高 | 已验证 |
| **Fourier-KAN-Mamba (Wang 2025)** | P0 | 高 | 已验证 |
| **GRAU: 可重构激活单元 (Liu 2026)** | P2 | 高 | 已验证 |

### Wiener模型论文（新增）

| 文献 | 类型 | 相关性 | 状态 |
|-----|------|-------|------|
| **Barron-Wiener-Laguerre (Manavalan 2026)** | P0 | 最高 | 已验证 |
| **SKANODEs: 结构化KAN神经ODE (Liu 2025)** | P0 | 高 | 已验证 |
| **Hall Sensor Self-Calibration** | P1 | 高 | 待处理 |
| **Wiener-Hammerstein for Sensors** | P0 | 高 | 待处理 |
| **H-W with Implicit GPs (Yin 2026)** | P0 | 高 | 已验证 |

### 频域损失论文（新增）

| 文献 | 类型 | 相关性 | 状态 |
|-----|------|-------|------|
| **TFMAE: 时频掩码自编码器 (ICDE 2024)** | P0 | 高 | 新增 |
| **CATCH: 通道感知频域Patch (ICLR 2024)** | P0 | 高 | 新增 |
| **F-SE-LSTM: FFT频域特征 (2025)** | P1 | 高 | 新增 |
| **FADSD: 纯频域异常检测 (IEEE TIM 2025)** | P0 | 高 | 新增 |

## Barron-Wiener-Laguerre核心信息

- **arxiv**: https://arxiv.org/abs/2602.13098
- **作者**: Rahul Manavalan, Filip Tronarp
- **核心贡献**: 
  - 将Barron空间理论与Wiener模型、Laguerre基函数结合
  - 线性动力学（Laguerre参数化）+ 静态非线性（Barron类型）
  - 提供不确定性量化（贝叶斯推理）
  - 维度无关收敛速率
- **与论文的相关性**: **最高** - Wiener-KAN完整理论框架的直接扩展

## HaKAN核心信息

- **arxiv**: https://doi.org/10.48550/arXiv.2601.18837
- **作者**: Hasan et al.
- **核心贡献**: 
  - 使用Hahn正交多项式替代样条基函数
  -专为时间序列设计
  - 正交多项式的数值稳定性优势
- **与论文的相关性**: 高 - 为KAN变体提供理论基础

## TFMAE核心信息 (ICDE 2024)

- **会议**: ICDE 2024
- **核心贡献**: 
  - 双时频掩码自编码器
  - 联合学习时域和频域特征
  - 时间序列异常检测
- **与论文的相关性**: 高 - 频域损失函数设计参考

## FADSD核心信息 (IEEE TIM 2025)

- **期刊**: IEEE Transactions on Instrumentation and Measurement
- **核心贡献**: 
  - 纯频域异常检测方法
  - 不依赖时域特征
  - 工业物联网传感器应用
- **与论文的相关性**: 高 - 频域方法在传感器应用中的证据

## 对GAP支撑的影响

所有11个GAP均保持充足文献支撑：

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

1. **子代理搜索成功**: 3个方向共发现28篇新论文
2. **关键发现**: Barron-Wiener-Laguerre是最重要的Wiener-KAN理论扩展
3. **文献库完备**: 所有GAP均无高缺口，文献调研阶段完成
4. **频域损失补充**: TFMAE和FADSD为频域方法提供新的学术证据

---

## 原始链接

### KAN效率
- https://doi.org/10.48550/arXiv.2601.18837 (HaKAN)
- https://doi.org/10.48550/arXiv.2511.18846 (WaveTuner)
- https://doi.org/10.48550/arXiv.2512.12850 (KANELÉ)
- https://doi.org/10.48550/arXiv.2601.03332 (LUT-KAN)
- https://arxiv.org/abs/2602.23455 (BiKA)

### Wiener模型
- https://arxiv.org/abs/2602.13098 (Barron-Wiener-Laguerre)
- https://arxiv.org/abs/2506.18339 (SKANODEs)
- https://arxiv.org/abs/2501.15849 (H-W with Implicit GPs)

### 频域损失
- TFMAE (ICDE 2024)
- CATCH (ICLR 2024)
- FADSD (IEEE TIM 2025)
