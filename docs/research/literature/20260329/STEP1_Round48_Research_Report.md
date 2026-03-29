# 调研报告：Round 48 - 文献库最终确认

## 基本信息
- 日期：2026-03-29
- 阶段：STEP1 调研
- 覆盖范围：Fourier-KAN-Mamba、AFMAE损失函数来源、Wiener-KAN结合
- 是否使用子代理：是（3个并行方向）

## 检索路径

### 子代理1：Fourier-KAN-Mamba最新进展
- 关键词：Fourier-KAN-Mamba, time series anomaly detection, KAN, Mamba, state-space model
- 主要数据库：arXiv, Google Scholar

### 子代理2：AFMAE损失函数来源
- 关键词：AFMAE, frequency domain loss, adaptive frequency, spectral loss, time series prediction
- 主要数据库：arXiv, IEEE Xplore, ScienceDirect, Google Scholar

### 子代理3：Wiener模型与KAN网络结合
- 关键词：Wiener KAN, Wiener-Hammerstein KAN, block-structured KAN, nonlinear system identification KAN
- 主要数据库：arXiv, IEEE Xplore, Google Scholar

## 发现结果

### Fourier-KAN-Mamba

**结论**：已在R10验证 (arXiv:2511.15083)
- 论文：Wang et al. 2025 "Fourier-KAN-Mamba: A Novel State-Space Equation Approach for Time-Series Anomaly Detection"
- 核心创新：Fourier + KAN + Mamba混合架构
- 在MSL、SMAP、SWaT数据集上验证
- 与KAN-AD的区别：加入Mamba SSM处理长序列

### AFMAE损失函数

**结论**：未找到"AFMAE"作为学术术语的原始论文

**最相关的替代论文**：
1. **fMAE (Frequency-weighted MAE)**: AirCast论文 (arXiv:2502.17919)
   - 提出了Frequency-weighted Mean Absolute Error损失函数
   - 针对时间序列中的类别不平衡问题

2. **BSP Loss** (arXiv:2502.00472): 
   - 自适应频域bin权重+MAE
   - 已在R11验证

3. **FreLE** (arXiv:2510.25800):
   - 低频谱偏置校正
   - 已在R11验证

**代码库发现**：
- `src/core/loss_functions.py`中有`af_mse_loss`实现
- 这是一个**幅频损失（Amplitude-Frequency Loss）**
- 使用对数能量差异计算，与BSP Loss思想相似

### Wiener-KAN结合

**结论**：直接相关文献非常有限

**唯一直接相关论文**：
- Cruz et al. 2025 "State-Space KAN for Wiener-Hammerstein" (arXiv:2506.16392)
- 已在R10验证
- 将KAN集成到状态空间框架用于Wiener-Hammerstein系统辨识

**其他相关论文**：
- SKANODEs (Liu et al. 2025): 结构化KAN神经ODE
- KAN-ODEs (Koenig et al. 2024): KAN用于动力学系统学习
- KAN-PISF (Pal et al. 2024): 物理信息KAN用于方程发现

## 文献库完整性确认

| 类别 | 已收录数量 | 目标 | 状态 |
|------|------------|------|------|
| KAN网络 | 50+篇 | - | ✅ 已完备 |
| Wiener模型 | 30+篇 | - | ✅ 已完备 |
| 频域损失函数 | 20+篇 | - | ✅ 已完备 |
| 漂移补偿 | 25+篇 | - | ✅ 已完备 |
| 架构效率 | 15+篇 | - | ✅ 已完备 |
| MEASUREMENT期刊 | 85篇 | 50篇 | ✅ 超额完成 |

## 调研结论

1. **AFMAE术语**：代码库中的AFMAE实现与学术文献中的BSP Loss/FreLE/fMAE概念相关，但无直接对应论文
2. **Fourier-KAN-Mamba**：已在R10收录
3. **Wiener-KAN**：仅有Cruz 2025一篇直接相关，已在R10收录

**STEP1调研阶段正式完成**

## 对文档的影响

- 确认了文献库的完整性
- 明确了AFMAE的学术渊源（BSP Loss/fMAE）
- 更新了literature_catalog.md

## 原始链接

- Fourier-KAN-Mamba: https://arxiv.org/abs/2511.15083
- BSP Loss: https://arxiv.org/abs/2502.00472
- fMAE: https://arxiv.org/abs/2502.17919
- Cruz SS-KAN: https://arxiv.org/abs/2506.16392