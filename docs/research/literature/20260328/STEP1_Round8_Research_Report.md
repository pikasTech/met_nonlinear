# 调研报告：STEP1 Round 8 综合文献调研

## 基本信息
- 日期：2026-03-28
- 阶段：STEP1 调研
- 覆盖范围：Wiener模型、KAN网络、频域损失函数、漂移补偿、神经网络架构效率
- 是否使用子代理：是（5个并行子代理分别搜索Wiener、KAN、频域损失、漂移补偿、架构效率）

## 检索路径

### 子代理1：Wiener模型检索
- 关键词：Wiener system identification, Wiener-Hammerstein, Wiener model sensor
- 主要数据库：IEEE Xplore, ScienceDirect, arXiv
- 发现：文献已大量存在于本地代码库，补充部分传感器应用文献

### 子代理2：KAN网络检索
- 关键词：KAN, Kolmogorov-Arnold Networks, Temporal KAN, KAN-LSTM, KAN-GRU
- 主要数据库：arXiv（主要）, Google Scholar
- 新发现：
  - Hahn-KAN (arXiv:2601.18837) - 多元时间序列
  - Time-TK (arXiv:2602.11190) - Transformer+KAN组合
  - WaveTuner (arXiv:2511.18846) - 小波子带调谐
  - SOH-KLSTM (arXiv:2509.10496) - 锂离子电池健康监测KAN+LSTM
  - Fourier-KAN-Mamba (arXiv:2511.15083) - KAN+傅里叶+Mamba
  - ss-Mamba (arXiv:2506.14802) - 样条KAMamba
  - KANMixer (arXiv:2508.01575) - KAN作为核心长期预测

### 子代理3：频域损失函数检索
- 关键词：frequency domain loss, spectral loss, AFMAE, focal frequency
- 主要数据库：IEEE Xplore, arXiv, Google Scholar
- 新发现：
  - FreDF (Wang et al. 2024/ICLR 2025) - 频域预测学习，l1损失在频域
  - SAMFre (Wang et al. 2025) - 频域sharpness-aware最小化损失
  - Floss (Yang et al. 2023) - 周期时间序列频域正则化
  - FTMixer (Li et al. 2024) - 时频域融合
  - FreLLM (Zhang et al. 2025/ICASSP 2025) - LLM频域预测
  - FreDN (An et al. 2026/AAAI 2026) - 频域解耦
  - FreST Loss (Wang & Liao 2026) - 联合频域学习

### 子代理4：漂移补偿检索
- 关键词：sensor drift compensation, electrochemical sensor, MEMS accelerometer, deep learning
- 主要数据库：IEEE Xplore, ScienceDirect
- 新发现：
  - ISFET pH传感器：Sinha 2020 (温度和时间漂移补偿), Khatri 2021 (校准寿命延长)
  - FET传感器：Margarit-Taulé 2022 (交叉补偿)
  - 水质传感器：Khatri 2021
  - E-nose：Heng 2025 (半监督对抗域适应CNN)
  - 知识蒸馏：Lin 2025, Liang 2025 (OTTA-DriftNet)
  - 评论：Ren 2024 (漂移补偿算法进展), Li 2025 (电化学传感器ML应用综述)

### 子代理5：神经网络架构效率检索
- 关键词：LSTM vs CNN, RNN vs CNN efficiency, TinyML, KAN efficiency
- 主要数据库：IEEE Xplore, arXiv
- 关键冲突发现：
  - Saha 2026 (TinyML)：1D-CNN比LSTM内存少35%，速度快74倍
  - Bian 2025 (TinierHAR)：CNN比DeepConvLSTM参数少43.3倍
  - 结论：RNN比1D-CNN参数少的声称与文献矛盾

## 发现结果

### 新增文献线索

#### KAN网络新增（P0）
| 作者 | 年份 | 标题 | DOI/链接 | 状态 |
|------|------|------|----------|------|
| Kui et al. | 2025 | TFKAN: Time-Frequency KAN | arXiv:2506.12696 | 已验证 |
| Cruz et al. | 2025 | SS-KAN for Wiener-Hammerstein | arXiv:2506.16392 | 已验证 |
| Manavalan, Tronarp | 2026 | Barron-Wiener-Laguerre | arXiv:2602.13098 | 已验证 |
| Rather et al. | 2025 | KAN-GRU/LSTM Hybrid | arXiv:2507.13685 | 已验证 |
| Ali et al. | 2025 | KAN vs LSTM Performance | arXiv:2511.18613 | 待核实 |
| Hasan et al. | 2026 | Hahn KAN for Time Series | arXiv:2601.18837 | 待核实 |
| Zhang et al. | 2026 | Time-TK: Transformer+KAN | arXiv:2602.11190 | 待核实 |
| Wang et al. | 2025 | WaveTuner: Wavelet+KAN | arXiv:2511.18846 | 待核实 |

#### 频域损失新增（P0）
| 作者 | 年份 | 标题 | DOI/链接 | 状态 |
|------|------|------|----------|------|
| Wang et al. | 2025 | FreDF (ICLR 2025) | arXiv:2402.02399 | 待核实 |
| Wang et al. | 2025 | SAMFre | arXiv:2505.17532 | 待核实 |
| Yang et al. | 2023 | Floss | arXiv:2308.01011 | 待核实 |
| Li et al. | 2024 | FTMixer | arXiv:2405.15256 | 待核实 |

#### 漂移补偿新增（P1）
| 作者 | 年份 | 标题 | DOI/链接 | 状态 |
|------|------|------|----------|------|
| ChakraVarthy et al. | 2026 | ML增强校准电化学环境监测 | 10.1080/00032719.2026.2618976 | 待核实 |
| Lin, Zhan | 2025 | 知识蒸馏E-nose漂移补偿 | arXiv:2507.17071 | 待核实 |
| Liang et al. | 2025 | OTTA-DriftNet | IEEE 11087654 | 待核实 |
| Heng et al. | 2025 | 半监督对抗域适应CNN | Sensors B | 待核实 |
| Sinha et al. | 2020 | ISFET pH传感器温度和时间漂移 | Microelectronics Journal | 待核实 |
| Khatri et al. | 2021 | 水质传感器漂移补偿 | Springer | 待核实 |

#### 架构效率确认（P1）
| 作者 | 年份 | 标题 | DOI/链接 | 状态 |
|------|------|------|----------|------|
| Saha, Samanta | 2026 | LSTM vs 1D-CNN TinyML | arXiv:2603.04860 | 已核实-冲突 |
| Bian et al. | 2025 | TinierHAR | arXiv:2507.07949 | 已核实-冲突 |

### 疑似重复
- 无

### 明确排除
- Fre-CW (Feng 2025) - 针对对抗攻击，非传感器补偿

## 待核实事项
1. 新增频域损失论文的完整引用信息（FreDF, SAMFre, Floss, FTMixer）
2. 新增漂移补偿论文的DOI获取
3. Hahn KAN, Time-TK, WaveTuner 等新KAN变体的具体应用场景
4. RNN vs 1D-CNN效率冲突的最终决策：文献显示1D-CNN更高效

## 对文档的影响
- 更新了 `docs/research/literature/literature_catalog.md`
- 更新了 `docs/research/literature/raw_literature.md`
- 不需要更新 SUMMARY（本次为STEP1调研阶段）

## 原始链接
- https://arxiv.org/abs/2404.19756 (KAN原始)
- https://arxiv.org/abs/2506.16392 (SS-KAN)
- https://arxiv.org/abs/2405.07344 (TKAN)
- https://arxiv.org/abs/2511.18613 (KAN vs LSTM)
- https://arxiv.org/abs/2603.04860 (Saha TinyML)
- https://arxiv.org/abs/2507.07949 (TinierHAR)
- https://arxiv.org/abs/2402.02399 (FreDF)
- https://arxiv.org/abs/2505.17532 (SAMFre)
- https://arxiv.org/abs/2510.25800 (FreLE)
- https://doi.org/10.48550/arXiv.2512.12850 (KANELÉ)