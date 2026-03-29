# 传感器漂移补偿深度学习方法 - 文献检索报告

**日期**：2026-03-28
**检索重点**：传感器漂移补偿的深度学习方法
**目标**：MET非线性项目（Wiener-KAN用于频率响应漂移补偿）

---

## 1. 检索范围与方法论

### 1.1 主要检索数据库
- IEEE Xplore：信号处理、传感器、神经网络
- ScienceDirect：电化学传感器、气体传感器
- Google Scholar：跨领域文献
- arXiv：预印本文献（电子印本服务器）

### 1.2 检索关键词
- 传感器类型：sensor drift, electrochemical sensor, gas sensor, seismic sensor, inertial sensor, e-nose
- 补偿方法：drift compensation, drift correction, drift mitigation, domain adaptation
- 深度学习：deep learning, CNN, RNN, LSTM, neural network, transfer learning

---

## 2. 发现并验证的关键论文

### 2.1 用于气体传感器漂移的TDACNN（Zhang等，2022）
- 作者：Zhang, Y. et al.
- 年份：2022
- 标题：TDACNN：用于传感器漂移补偿的无目标域CNN
- arXiv: https://arxiv.org/abs/2110.07509
- 关键贡献：无需目标域数据的传感器漂移域适应方法
- 相关性：高 - 深度学习直接应用于传感器漂移

### 2.2 电子鼻知识蒸馏（Lin, Zhan, 2025）
- 作者：Lin, X.; Zhan, Y.
- 年份：2025
- 标题：用于电子鼻漂移补偿的知识蒸馏
- arXiv: https://arxiv.org/abs/2507.17071
- 关键贡献：电子鼻漂移缓解的首个知识蒸馏方法
- 注：PDF存在于项目根目录（2507.17071.pdf - 7.2MB）

### 2.3 气流-惯性里程计（Tagliabue, How, 2021）
- 作者：Tagliabue, A.; How, J.
- 年份：2021
- 标题：气流-惯性里程计
- arXiv: https://arxiv.org/abs/2105.13506
- 关键贡献：惯性-嗅觉导航中漂移补偿的传感器融合

---

## 3. 核心理论论文

### 3.1 Wiener-KAN架构

**Cruz等，2025 - 用于Wiener-Hammerstein的状态空间KAN**
- arXiv: https://arxiv.org/abs/2506.16392
- 关键贡献：Wiener-KAN架构的直接理论基础

**Liu等，2024 - KAN: Kolmogorov-Arnold网络**
- arXiv: https://arxiv.org/abs/2404.19756
- 关键贡献：边上B样条，基于LUT的计算

**Manavalan, Tronarp, 2026 - Barron-Wiener-Laguerre**
- arXiv: https://arxiv.org/abs/2602.13098
- 关键贡献：Wiener类模型的理论框架

### 3.2 频域损失

**Jiang等，2021 - 聚焦频率损失**
- arXiv: https://arxiv.org/abs/2012.12821
- 关键贡献：频谱精度的自适应频率聚焦
- 相关性：P0 - AFMAE损失函数设计的理论基础

**Wang等，2025 - SAMFre**
- arXiv: https://arxiv.org/abs/2505.17532
- 公式：loss = alpha x |FFT(pred) - FFT(real)|_1 + (1-alpha) x MSE

---

## 4. 架构效率论文

**Yin等，2017 - CNN vs RNN比较研究**
- arXiv: https://arxiv.org/abs/1702.01923
- 关键发现：CNN的O(1)顺序复杂度 vs RNN的O(n)

**Miller, Hardt, 2018 - 稳定循环模型**
- arXiv: https://arxiv.org/abs/1805.10369
- 相关性：P1 - RNN稳定性理论基础

**Xie, Zhang, 2021 - 深度滤波**
- arXiv: https://arxiv.org/abs/2112.12616
- 关键发现：使用深度可分离卷积减少60-70%计算量

---

## 5. 按类别汇总的文献

### 5.1 深度学习漂移补偿论文
| 优先级 | 论文 | 年份 | 方法 | 关键发现 |
|--------|------|------|------|----------|
| P1 | Zhang等 TDACNN | 2022 | 无目标域CNN | 无需目标数据的域适应 |
| P1 | Lin, Zhan KD电子鼻 | 2025 | 知识蒸馏 | 通过师生迁移学习 |
| P1 | Tagliabue, How | 2021 | 传感器融合 | 通过融合减少漂移 |

### 5.2 核心理论论文
| 优先级 | 论文 | 年份 | 联系 |
|--------|------|------|------|
| P0 | Cruz等 SS-KAN | 2025 | Wiener-KAN直接连接 |
| P0 | Liu等 KAN | 2024 | KAN基础 |
| P0 | Manavalan, Tronarp | 2026 | Barron-Wiener理论框架 |
| P0 | Jiang等 FFL | 2021 | AFMAE理论基础 |

---

## 6. 文献空白和待验证项目

### 6.1 无法验证（文献未找到）
| 空白 | 影响 | 状态 |
|------|------|------|
| AFMAE原始来源 | 必须使用FFL作为理论基础 | 未找到 |
| Transformer用于时间序列 | R3-4比较不完整 | 未找到 |
| RVTDCNN PA线性化 | R3-5声明不支持 | 未找到 |
| 数据集构建参考 | R3-6必须使用内部描述 | 未找到 |

### 6.2 待验证
| 论文 | arXiv ID | 状态 |
|------|----------|------|
| TKAN（时间KAN） | 2405.07344 | 无法访问原文 |
| KAN 2.0 | 2408.10205 | 待处理 - 目标不同 |

---

## 7. 完整引用列表

### 深度学习漂移补偿
1. Zhang, Y. et al. (2022). TDACNN: 用于传感器漂移补偿的无目标域CNN. arXiv:2110.07509.
2. Lin, X.; Zhan, Y. (2025). 用于电子鼻漂移补偿的知识蒸馏. arXiv:2507.17071.
3. Tagliabue, A.; How, J. (2021). 气流-惯性里程计. arXiv:2105.13506.

### 核心理论
4. Cruz, R. et al. (2025). 用于Wiener-Hammerstein系统的状态空间KAN. arXiv:2506.16392.
5. Liu, Z. et al. (2024). KAN: Kolmogorov-Arnold网络. arXiv:2404.19756.
6. Manavalan, M.; Tronarp, J. (2026). Barron-Wiener-Laguerre网络. arXiv:2602.13098.
7. Jiang, Y. et al. (2021). 聚焦频率损失. arXiv:2012.12821.

### 架构效率
8. Yin, C. et al. (2017). CNN和RNN架构的比较研究. arXiv:1702.01923.
9. Miller, J.; Hardt, M. (2018). 稳定循环模型. arXiv:1805.10369.
10. Xie, X.; Zhang, Y. (2021). 深度滤波. arXiv:2112.12616.
11. Wang, Y. et al. (2025). 带SAMFre的TimeCF. arXiv:2505.17532.

---

**报告状态**：已完成
**最后更新**：2026-03-28