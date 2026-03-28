# 调研报告：STEP1 系统性文献线索收集（第二轮）

## 基本信息
- 日期：2026-03-28
- 阶段：STEP1 调研
- 覆盖范围：Wiener模型理论、KAN计算效率、频域损失函数、RNN vs CNN效率、漂移补偿
- 是否使用子代理：是；并行5方向检索

---

## 检索路径

### 并行子代理任务分配
| 子代理 | 检索方向 | 主要数据库 | 关键词 |
|--------|----------|-----------|--------|
| 子代理1 | Wiener模型理论 | IEEE Xplore, ScienceDirect, arXiv | Wiener system, nonlinear system identification, Hammerstein-Wiener |
| 子代理2 | KAN计算效率 | arXiv, IEEE Xplore, ACM DL | KAN efficiency, KAN vs LSTM, KAN vs GRU, KAN FLOPs |
| 子代理3 | AFMAE/频域损失 | IEEE Xplore, ScienceDirect, arXiv | AFMAE, frequency domain loss, spectral loss, FFT loss |
| 子代理4 | RNN vs CNN效率 | IEEE Xplore, arXiv, Google Scholar | RNN vs CNN efficiency, TCN, recurrent vs convolutional |
| 子代理5 | 漂移补偿DL方法 | IEEE Xplore, ScienceDirect, arXiv | drift compensation, sensor drift, E-nose, MEMS accelerometer |

---

## 发现结果

### 新增文献线索汇总

#### P0 Wiener模型理论
| 作者 | 年份 | 标题 | DOI/URL | 相关性 | 状态 |
|------|------|------|---------|--------|------|
| Revay, Manchester | 2021 | Recurrent Equilibrium Networks | arXiv:2104.05942 | Medium | 待核实 |
| Xu et al. | 2025 | Kernel for Volterra Wiener-Hammerstein | arXiv:2505.20747 | Medium | 待核实 |
| Beintema et al. | 2020 | Deep encoder networks for Wiener-Hammerstein | arXiv:2012.07697 | Medium | 待核实 |
| Voit, Enzner | 2024 | Multikernel Neural Networks block-structured | arXiv:2412.07370 | High | 待核实 |
| Rufolo et al. | 2024 | Enhanced Transformer for Wiener-Hammerstein | arXiv:2410.03291 | Medium | 待核实 |

#### P0 KAN计算效率
| 作者 | 年份 | 标题 | DOI/URL | 关键发现 | 状态 |
|------|------|------|---------|----------|------|
| Ali et al. | 2025 | KAN vs LSTM Performance | doi:10.48550/arXiv.2511.18613 | LSTM优于标准KAN；KAN优势仅在资源受限场景 | 待核实 |
| Yang, Wang | 2024 | Kolmogorov-Arnold Transformer (KAT) | doi:10.48550/arXiv:2409.10594 | 分析KAN三个挑战；Group KAN减少计算量 | 待核实 |
| Lee et al. | 2024 | HiPPO-KAN | doi:10.48550/arXiv:2410.14939 | 常参数数量vs可变窗口大小 | 待核实 |
| Pu et al. | 2025 | KANet: KAN vs LSTM/GRU FLOPs | IEEE TIM | FLOPs和参数量超过LSTM/GRU | 待核实 |
| Yamak et al. | 2025 | KAN time series review | doi:10.1007/s10586-025-05574-9 | KAN优于Transformer达98%更低MSE | 待核实 |
| Rather et al. | 2025 | KAN-GRU/LSTM hybrid | doi:10.48550/arXiv:2507.13685 | GRU-KAN和LSTM-KAN混合优于纯架构 | 待核实 |

#### P0 频域损失函数
| 作者 | 年份 | 标题 | DOI/URL | 关键发现 | 状态 |
|------|------|------|---------|----------|------|
| Sun et al. | 2025 | FreLE: Low-Frequency Spectral Bias | arXiv:2510.25800 | 频谱偏置校正，频域损失增强 | 待核实 |
| Chakraborty et al. | 2025 | BSP Loss for Chaotic Systems | arXiv:2502.00472 | 自适应频谱bin权重 | 待核实 |
| He et al. | 2025 | FIRE: Unified Frequency Domain | arXiv:2510.10145 | 幅值和相位独立建模 | 待核实 |
| Basalaev et al. | 2024 | CNN Wiener seismic isolation | arXiv:2410.14806 | FFT损失用于地震数据 | 待核实 |
| Feng et al. | 2025 | Fre-CW: Frequency Domain Attack | arXiv:2508.08955 | 时域+频域损失用于对抗攻击 | 待核实 |

**重要结论：AFMAE未找到任何学术文献**

#### P1 RNN vs CNN效率
| 作者 | 年份 | 标题 | DOI/URL | 关键发现 | 状态 |
|------|------|------|---------|----------|------|
| Bai et al. | 2018 | TCN: CNN vs RNN for Sequence | arXiv:1803.01271 | CNN O(1)每步vs RNN O(n)；CNN在序列建模中优于LSTM | 待核实 |
| Lee et al. | 2017 | Recurrent Additive Networks | arXiv:1705.07393 | 纯加性潜状态RNN性能与LSTM相当但计算更简单 | 待核实 |
| Karita et al. | 2019 | Transformer vs RNN Speech | arXiv:1909.06317 | Transformer在15个ASR基准中13个优于RNN | 待核实 |

#### P1 漂移补偿
| 作者 | 年份 | 标题 | DOI/URL | 关键发现 | 状态 |
|------|------|------|---------|----------|------|
| ChakraVarthy et al. | 2026 | ML-enhanced ECG drift | Analytical Letters | ML增强标定算法用于长期电化学监测 | 待核实 |
| Li et al. | 2025 | ML for electrochemical sensors review | TrAC 2025 | ML方法综述含漂移补偿 | 待核实 |
| Badawi et al. | 2021 | Deep NN Hadamard transform for drift | IEEE Sensors | 实时低成本DNN用于化学传感器漂移 | 待核实 |
| Wei, Liu | 2024 | BP NN for MEMS accelerometer drift | Rev Sci Instr | BP神经网络用于MEMS加速度计温度漂移 | 待核实 |
| Pawase, Futane | 2018 | ANN for MEMS seismic sensor drift | Int J Smart Sensing | ANN用于MEMS地震传感器频漂 | 待核实 |
| Shi et al. | 2022 | EEMD-GRNN for MEMS drift | Sensors 2022 | 集合经验模态分解+广义回归NN | 待核实 |
| Zhou et al. | 2025 | LSTM for MEMS seabed deformation | IEEE Sensors | LSTM用于MEMS传感器阵列长期漂移 | 待核实 |
| Zhang, Zhang | 2014 | Domain adaptation ELM for E-nose | IEEE TIM | 迁移学习用于电子鼻漂移补偿先驱工作 | 待核实 |
| Liang et al. | 2025 | OTTA-DriftNet: Online test-time adaptation | IEEE SMCS | 在线测试时适应漂移补偿网络 | 待核实 |

---

## 待核实事项

1. **AFMAE来源不明** - 搜索所有主要学术数据库均未发现"AFMAE"或"Adaptive Frequency Mean Absolute Error"这一术语，极可能为项目内部术语或概念
   - 建议：将AFMAE定位为项目内部术语，参考文献包括Focal Frequency Loss (Jiang 2020)、BSP Loss (Chakraborty 2025)、FreLE (Sun 2025)

2. **KAN效率矛盾** - 部分文献（Ali 2025）表明标准KAN准确性低于LSTM；但另有文献（Yamak 2025 review）表明KAN优于Transformer
   - 建议：需进一步核实KAN vs LSTM/GRU的具体场景效率对比

3. **KANet FLOPs超过LSTM/GRU** - 有文献直接测量FLOPs显示KANet参数量和计算量超过LSTM/GRU
   - 建议：核实KAN计算效率声称的准确性

---

## 排除依据

1. **AFMAE原始论文** - 未找到，不能作为引用文献
2. **RVTDCNN PA线性化** - 搜索未发现，不能支持R3-5声称
3. **Transformer时间序列** - 已存在于excluded_literature.md，无需重复收集

---

## 对文档的影响

- 更新文件：
  - `raw_literature.md` - 新增本轮发现的文献线索表格
  - `literature_catalog.md` - 新增Survey Report Index条目
  - `docs/research/literature/20260328/STEP1_20260328_research_report.md` - 本调研报告
- 是否需要更新SUMMARY：否（STEP1不更新SUMMARY）
- 是否需要后续STEP2分析：是（部分高相关性文献需深度分析）

---

## 原始链接

### Wiener模型
- https://arxiv.org/abs/2104.05942 (Revay, Manchester 2021)
- https://arxiv.org/abs/2505.20747 (Xu et al. 2025)
- https://arxiv.org/abs/2012.07697 (Beintema et al. 2020)
- https://arxiv.org/abs/2412.07370 (Voit, Enzner 2024)
- https://arxiv.org/abs/2410.03291 (Rufolo et al. 2024)

### KAN效率
- https://doi.org/10.48550/arXiv.2511.18613 (Ali et al. 2025)
- https://doi.org/10.48550/arXiv:2409.10594 (Yang, Wang 2024 - KAT)
- https://doi.org/10.48550/arXiv:2410.14939 (Lee et al. 2024 - HiPPO-KAN)
- https://ieeexplore.ieee.org/abstract/document/11146884/ (KANet 2025)
- https://doi.org/10.1007/s10586-025-05574-9 (Yamak et al. 2025)
- https://doi.org/10.48550/arXiv.2507.13685 (Rather et al. 2025)

### 频域损失
- https://arxiv.org/abs/2510.25800 (Sun et al. 2025 - FreLE)
- https://arxiv.org/abs/2502.00472 (Chakraborty et al. 2025 - BSP Loss)
- https://arxiv.org/abs/2510.10145 (He et al. 2025 - FIRE)
- https://arxiv.org/abs/2410.14806 (Basalaev et al. 2024)
- https://arxiv.org/abs/2508.08955 (Feng et al. 2025 - Fre-CW)

### RNN vs CNN
- https://arxiv.org/abs/1803.01271 (Bai et al. 2018 - TCN)
- https://arxiv.org/abs/1705.07393 (Lee et al. 2017 - RAN)
- https://arxiv.org/abs/1909.06317 (Karita et al. 2019)

### 漂移补偿
- https://www.tandfonline.com/doi/abs/10.1080/00032719.2026.2618976 (ChakraVarthy 2026)
- https://www.sciencedirect.com/science/article/pii/S0165993625003371 (Li 2025)
- https://ieeexplore.ieee.org/abstract/document/9442748/ (Badawi 2021)
- https://pubs.aip.org/aip/rsi/article/95/11/115107/3321388 (Wei 2024)
- https://sciendo.com/2/v2/download/article/10.21307/ijssis-2018-001.pdf (Pawase 2018)
- https://www.mdpi.com/1424-8220/22/14/5225 (Shi 2022)
- https://ieeexplore.ieee.org/abstract/document/11122349/ (Zhou 2025)
- https://ieeexplore.ieee.org/abstract/document/6963383/ (Zhang 2014 - Domain adaptation ELM)
- https://ieeexplore.ieee.org/abstract/document/11087654/ (Liang 2025 - OTTA-DriftNet)