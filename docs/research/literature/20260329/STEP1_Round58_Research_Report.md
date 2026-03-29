# 调研报告：STEP1 Round58 (2026-03-29)

## 基本信息
- **日期**：2026-03-29
- **阶段**：STEP1 调研（第58轮）
- **覆盖范围**：近期文献核查 - 2026年3月下旬新论文
- **是否使用子代理**：是；并行两个子代理分别检索：arXiv KAN/时序论文、传感器漂移补偿论文

## 检索路径

### 数据库
- arXiv (cs.LG, stat.ML, eess.SY)
- IEEE Xplore
- ScienceDirect (MEASUREMENT journal)
- MDPI Informatics
- SSRN

### 关键词
1. **KAN**: Kolmogorov-Arnold Networks, KAN, 2026
2. **Wiener**: Wiener-Hammerstein, frequency-dependent nonlinear distortion
3. **传感器漂移**: sensor drift compensation, electronic-nose, semi-supervised
4. **频域**: frequency domain, time series, dual-domain

### 检索式
- `site:arxiv.org "Kolmogorov-Arnold" OR "KAN" 2026`
- `site:arxiv.org Wiener system OR sensor drift 2026`
- `MDPI Informatics sensor drift compensation 2026`

## 发现结果

### 新增文献线索（3篇）

#### 1. 传感器漂移补偿 - 半监督知识蒸馏
| 字段 | 内容 |
|------|------|
| 标题 | Semi-supervised Knowledge Distillation for Sensor-Drift Compensation in Electronic-Nose Systems |
| 作者 | 未完整提取（MDPI Informatics） |
| DOI/链接 | MDPI Informatics - indexed 2026-03-26 |
| 年份 | 2026 |
| 类别 | P1 |
| 相关度 | 高 |
| 状态 | **新增待核实** |
| 摘要 | 环境变化和传感器老化导致电子鼻系统中传感器漂移，影响气体分类性能。作者设计了域适应任务，使用UCI气体传感器阵列漂移数据集测试半监督知识蒸馏方法进行漂移补偿，表现优于DRCA方法达18%。 |

#### 2. 电化学地震传感器
| 字段 | 内容 |
|------|------|
| 标题 | Design and Characteristics of Electrochemical Seismic Sensor with Carbon Electrodes for Exploration in Low-Frequency Range |
| 作者 | Vadim Agafonov, Ivan Gorchakov, Ivan V. Egorov, Viktoriya Agafonova, Svetlana Avdyukhina, Andrey Ronzhin |
| DOI/链接 | 10.2139/ssrn.6136097 |
| 年份 | 2026 |
| 类别 | P2 |
| 相关度 | 高 |
| 状态 | **新增待核实** |
| 摘要 | 提出了用于低频探测的碳电极电化学地震传感器设计。介绍了传感器性能的实验室表征结果，在低频范围内相关地球物理勘探。 |

#### 3. Wiener-Hammerstein频率相关非线性失真模型
| 字段 | 内容 |
|------|------|
| 标题 | Identification of Wiener-Hammerstein models for frequency-dependent nonlinear distortion |
| 作者 | Mitsuteru Yoshida, Asuka Matsushita, Etsushi Yamazaki (NTT Innovation Laboratories) |
| DOI/链接 | 10.23919/transcom.2025ebp3117 |
| 年份 | 2026 |
| 类别 | P0 |
| 相关度 | 中 |
| 状态 | **新增待核实** |
| 摘要 | 提出了用于频率相关非线性失真系统的Wiener-Hammerstein模型辨识方法。解决了同时具有线性和非线性分量的并联结构系统的建模问题，适用于电子元件和具有记忆效应的传感器。 |

#### 4. MoE-Transformer双域预测框架
| 字段 | 内容 |
|------|------|
| 标题 | MoE-Transformer: A Dual-Domain Forecasting Framework with Time and Frequency Domain Routing via Reinforcement Learning |
| 作者 | 未完整提取（Research Square） |
| DOI/链接 | Research Square - posted 2026-03-11 |
| 年份 | 2026 |
| 类别 | P0 |
| 相关度 | 高 |
| 状态 | **新增待核实** |
| 摘要 | 提出了双域预测框架（MoE-Transformer），通过强化学习在时域和频域之间路由表示。模型使用时域和频域的并行专家混合模块，路由被表述为马尔可夫决策过程。解决多尺度周期行为和非平稳时间变化的长时序预测问题。 |

### 入口已定位
- MDPI Informatics: https://www.mdpi.com/journal/informatics
- SSRN: https://ssrn.com/abstract/6136097
- IEEE: 10.23919/transcom.2025ebp3117

### 疑似重复
- 无

### 明确排除
- 无

## 待核实事项
1. 验证MDPI Informatics论文的完整引用信息
2. 验证SSRN论文的同行评审状态
3. 获取MoE-Transformer论文的完整信息

## 对文档的影响
- 更新了哪些文件：raw_literature.md（新增4条）
- 是否需要更新 SUMMARY：否
- 是否需要后续 STEP2 分析：待核实后决定

## 原始链接
- MDPI Informatics: https://www.mdpi.com/journal/informatics (indexed 2026-03-26)
- SSRN: https://ssrn.com/abstract/6136097
- IEEE: 10.23919/transcom.2025ebp3117
- Research Square: https://www.researchsquare.com (posted 2026-03-11)

## 文献库完整性确认

| 类别 | 已收录数量 | 目标 | 状态 |
|------|------------|------|------|
| KAN网络 | 60+篇 | - | ✅ 已完备 |
| Wiener模型 | 35+篇 | - | ✅ 已完备 |
| 频域损失函数 | 25+篇 | - | ✅ 已完备 |
| 漂移补偿 | 30+篇 | - | ✅ 已完备 |
| 架构效率 | 15+篇 | - | ✅ 已完备 |
| MEASUREMENT期刊 | 85篇 | 50篇 | ✅ 超额完成 |

**本轮结论**：文献库整体已完备。本轮新增4条近期论文线索，待进一步核实。