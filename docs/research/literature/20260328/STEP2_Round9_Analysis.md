# 分析报告：STEP2 Round 9 综合分析

## 基本信息
- 日期：2026-03-28
- 阶段：STEP2 分析（Round 9）
- 分析对象：raw_literature.md 中 Pending 条目深度分析
- 是否使用子代理：是（5 个并行子代理）

---

## 并行分析维度

| 子代理 | 覆盖主题 | 条目数 | 状态 |
|--------|----------|--------|------|
| 子代理1 | KAN Pending 论文 | 11 篇 | ✅ |
| 子代理2 | Wiener 传感器论文 | 5 篇 | ✅ |
| 子代理3 | Drift Compensation Pending | 5 篇 | ✅ |
| 子代理4 | Measurement/Dataset Pending | 10 篇 | ✅ |
| 子代理5 | Architecture Efficiency Conflict | 3 篇 | ✅ |

---

## 一、KAN Pending 论文分析结果（11 篇）

### 新增 Verified 条目（10 篇）：

| 论文 | 核心贡献 | 相关度 |
|------|---------|--------|
| **Lee et al. - HiPPO-KAN (2024)** | HiPPO 理论 + KAN，窗口大小无关参数效率；Outperforms KAN at larger window sizes | MEDIUM |
| **Somvanshi et al. - KAN Survey (2025)** | ACM Computing Surveys 综合综述；KAN+CNN/RNN/Transformer 混合架构验证 | **HIGH** |
| **Hasan et al. - Hahn KAN (2026)** | Hahn 多项式激活函数；Channel independence + patching | MEDIUM |
| **Zhang et al. - Time-TK (2026)** | Transformer+KAN 多偏移时间交互框架；MOTE + Interactive KAN | MEDIUM |
| **Wang et al. - WaveTuner (2025)** | 小波子带 + KAN 自适应路由；多分支 KAN 处理不同频带 | **MEDIUM-HIGH** |
| **Jarraya et al. - SOH-KLSTM (2025)** | KAN+LSTM 混合用于电池 SOH 估计；直接验证 RNN→KAN 模式 | **HIGH** |
| **Wang et al. - Fourier-KAN-Mamba (2025)** | Fourier 层 + KAN + Mamba；线性频谱特征 → KAN 非线性 | MEDIUM |
| **Ye - ss-Mamba (2025)** | Spline KAN + Mamba；语义索引嵌入 + 样条时序编码 | MEDIUM |
| **Jiang et al. - KANMixer (2025)** | KAN 作为 LTSF 主干；16/28 实验 SOTA；首个 KAN LTSF 实用指南 | **HIGH** |
| **Zeng et al. - AR-KAN (2025)** | AR 模块 + KAN；线性时序记忆 + 非线性表示；类似 Wiener 结构 | **MEDIUM-HIGH** |

### 保持 Pending（1 篇）：
- **Livieris - C-KAN (2024)** - MDPI Mathematics 返回 403；无法自动验证

### 核心发现：
- **无直接 Wiener-KAN 结构论文**：仍未找到 linear→KAN→linear 的直接论文
- KAN+RNN 混合架构有多个新证据（SOH-KLSTM, AR-KAN）
- KAN 频域应用有多个新证据（WaveTuner, Fourier-KAN-Mamba）

---

## 二、Wiener 传感器论文分析结果（5 篇）

### 新增 Verified（1 篇）：
| 论文 | 核心贡献 | 状态 |
|------|---------|------|
| **Iqbal - Volterra System Analysis (2024)** | MIT DSpace 开放获取；Volterra 级数分析电化学传感器非线性；直接电化学传感器领域 | ✅ VERIFIED |

### 新增 Excluded（2 篇）：
| 论文 | 原因 | 状态 |
|------|------|------|
| **Hsu et al. - WRNN for MEMS Gyroscope (2017)** | 领域不匹配（MEMS 惯性 vs 电化学）；Paywalled | ❌ EXCLUDED |
| **Kumar et al. - E-tongue Nonlinear Modeling (2020)** | IEEE Xplore Paywalled；无法验证详细公式 | ❌ EXCLUDED |

### 保持 Pending（1 篇）：
| 论文 | 原因 |
|------|------|
| **Li et al. - Hammerstein-Wiener for Li-ion (2024)** | ScienceDirect Paywalled；Abstract 确认方法但无法验证完整公式 |

### 已排除（1 篇）：
| 论文 | 状态 |
|------|------|
| **Ang et al. - MEMS Accelerometer (2007)** | 已在 R8 排除 |

### 核心发现：
- **核心 GAP 仍存在**：无直接 block-structured（linear→nonlinear→linear）电化学传感器 Wiener 模型论文
- Kumar 2020（E-tongue）高度相关但无法验证
- Iqbal 2024（MIT）可作为 Volterra/非线性建模方法论参考

---

## 三、Drift Compensation Pending 分析结果（5 篇）

### 新增 Verified（1 篇）：
| 论文 | 核心贡献 | 相关度 |
|------|---------|--------|
| **Margarit-Taulé, Martín-Ezquerra - FET Sensor Drift (2022)** | FET 传感器漂移 + 矩阵效应联合补偿；DNN 实现 73% RMSE 降低 | **HIGH** |

### 保持 Pending（2 篇）：
| 论文 | 原因 |
|------|------|
| **Sinha et al. - ISFET pH Sensor (2020)** | Journal of Computational Electronics（期刊不匹配）；DOI:10.1007/s00542-020-04797-5 |
| **Khatri et al. - Water Quality Sensor Drift (2021)** | DOI:10.1007/s12652-020-02831-0；无法获取全文 |

### 新增 Excluded（2 篇）：
| 论文 | 原因 | 状态 |
|------|------|------|
| **Heng et al. - Semi-supervised Adversarial Domain Adapt CNN (2025)** | 无法验证论文存在；主要数据库无记录 | ❌ EXCLUDED |
| **Ren et al. - Advances in E-nose Drift Compensation (2024)** | 无法验证；Emerald Sensor Review 2024 无匹配记录 | ❌ EXCLUDED |

---

## 四、Measurement/Dataset Pending 分析结果（10 篇）

### 新增 Verified（3 篇）：
| 论文 | 核心贡献 | 相关度 |
|------|---------|--------|
| **Iqbal - Volterra System Analysis for Electrochemical Sensor (2024)** | Volterra 级数分析电化学传感器非线性；MIT DSpace 开放获取 | **HIGH** |
| **Jacob et al. - Exathlon Benchmark (2020)** | 可解释异常检测高维时序基准；Apache Spark 集群数据；92 citations | **HIGH** |
| **Devecioglu et al. - Op-GAN Seismic Signal Synthesis (2024)** | 1D Operational GANs 用于地震信号合成；SimGM benchmark；虚拟传感器创建 | MEDIUM |

### 已验证（2 篇）：
| 论文 | 状态 |
|------|------|
| **Xu, Wang 2008** | 已在 R8 验证 |
| **Schoukens, Noël 2017** | 已在 R8 验证 |

### 新增 Excluded（3 篇）：
| 论文 | 原因 |
|------|------|
| **Kumar et al. - E-tongue (2020)** | IEEE Paywalled |
| **Sun et al. - Electrochemical Seismometer Numerical (2017)** | IEEE Paywalled；领域偏离 |
| **Zhou et al. - Broadband Electrochemical Seismometer (2025)** | IEEE TIM Paywalled；领域偏离 |

### 保持 Pending（1 篇）：
| 论文 | 原因 |
|------|------|
| **Agafonov et al. - Electrochemical Seismometers (2015)** | ResearchGate 403；无法自动验证 |

---

## 五、Architecture Efficiency Conflict 分析结果

### 关键发现：Bai et al. TCN (2018) **错误标记为 CONFLICT**

**问题**：TCN 论文（arXiv:1803.01271）被错误标记为 CONFLICT，但该论文**并不声称**"RNN 参数少于 1D-CNN"。

**TCN 实际发现**：
- 关注**计算复杂度**（O(1) vs O(n) 路径长度），而非参数量
- 核心创新：膨胀因果卷积实现更长记忆而**无需参数增加**
- CNN (TCN) 达到 O(1) 感受野 vs RNN 的 O(n) 顺序依赖
- 结论：CNN 优于 LSTM，同时展示更长有效记忆

**判决**：
- TCN **不是冲突论文**，而是**CNN 效率的支持证据**
- 该论文不支持"RN参数少于1D-CNN"的说法（因为它根本不比较这个）
- 该论文实际上提供了**支持 CNN 效率的证据**：膨胀卷积实现更长记忆而无需参数增加

**重新分类**：~~CONFLICT~~ → **VERIFIED**（证据支持 CNN 效率，但与论文声称方向相反）

### 冲突确认（保持 Excluded）：
| 论文 | 冲突内容 |
|------|---------|
| **Saha, Samanta - LSTM vs 1D-CNN TinyML (2026)** | 1D-CNN 使用 35% 更少 RAM，25% 更少 Flash，74x 更快；直接反驳论文声称 |
| **Bian et al. - TinierHAR (2025)** | CNN 模型比 RNN 模型少 43.3x 参数；直接反驳论文声称 |

---

## 六、本轮决策汇总

### 新增 Verified 条目（15 篇）：
1. Lee et al. - HiPPO-KAN (2024) arXiv:2410.14939
2. Somvanshi et al. - KAN Survey (2025) arXiv:2411.06078
3. Hasan et al. - Hahn KAN (2026) arXiv:2601.18837
4. Zhang et al. - Time-TK (2026) arXiv:2602.11190
5. Wang et al. - WaveTuner (2025) arXiv:2511.18846
6. Jarraya et al. - SOH-KLSTM (2025) arXiv:2509.10496
7. Wang et al. - Fourier-KAN-Mamba (2025) arXiv:2511.15083
8. Ye - ss-Mamba (2025) arXiv:2506.14802
9. Jiang et al. - KANMixer (2025) arXiv:2508.01575
10. Zeng et al. - AR-KAN (2025) arXiv:2509.02967
11. Iqbal - Volterra System Analysis (2024) MIT DSpace
12. Margarit-Taulé - FET Sensor Drift (2022) DOI:10.1016/j.snb.2021.131879
13. Jacob et al. - Exathlon Benchmark (2020) arXiv:2010.05073
14. Devecioglu et al. - Op-GAN Seismic (2024) arXiv:2407.11040
15. Bai et al. - TCN (2018) arXiv:1803.01271（重新分类）

### 新增 Excluded 条目（7 篇）：
1. Hsu et al. - WRNN for MEMS Gyroscope (2017) - 领域不匹配
2. Kumar et al. - E-tongue (2020) - Paywalled
3. Heng et al. - Semi-supervised (2025) - 无法验证
4. Ren et al. - E-nose Drift Review (2024) - 无法验证
5. Sun et al. - Electrochemical Seismometer (2017) - Paywalled
6. Zhou et al. - Broadband Seismometer (2025) - Paywalled
7. Kumar et al. - E-tongue (2020) [Measurement] - Paywalled

### 保持 Pending（5 篇）：
1. Livieris - C-KAN (2024) - MDPI 403
2. Li et al. - Hammerstein-Wiener for Li-ion (2024) - Paywalled
3. Sinha et al. - ISFET pH Sensor (2020) - 期刊不匹配
4. Khatri et al. - Water Quality Drift (2021) - Paywalled
5. Agafonov et al. - Electrochemical Seismometers (2015) - ResearchGate 403

---

## 七、关键 GAP 更新

| GAP | 状态 | 备注 |
|-----|------|------|
| **AFMAE 理论依据** | ✅ 已解决 | FreDF (Wang 2025 ICLR) + BSP Loss + FreLE |
| **Wiener-KAN 块结构** | ❌ 仍未解决 | 无 linear→KAN→linear 直接论文 |
| **MET 传感器 Wiener 模型** | ⚠️ 部分解决 | Iqbal 2024 (Volterra)；Kumar 2020 (E-tongue) Paywalled |
| **RNN vs CNN 效率声称** | ❌ 仍冲突 | Saha 2026, Bian 2025 直接反驳；建议删除此声称 |
| **KAN 频域应用** | ✅ 新证据 | TFKAN, WaveTuner, Fourier-KAN-Mamba |
| **KAN+RNN 混合** | ✅ 新证据 | SOH-KLSTM, AR-KAN, KANMixer |

---

## 八、对文档的影响

### 需要更新的文档：
- ✅ `docs/research/literature/verified_literature.md` - 新增 15 篇
- ✅ `docs/research/literature/excluded_literature.md` - 新增 7 篇
- ✅ `docs/research/literature/SUMMARY.md` - 更新 GAP 状态
- ✅ `docs/research/literature/20260328/STEP2_Round9_Analysis.md` - 本报告

### raw_literature.md 更新：
- 已验证条目 → 更新 Status
- 无法验证条目 → 标记 Excluded
- 保留 Pending 条目

---

## 原始链接

### KAN Papers (Verified)
- HiPPO-KAN: https://arxiv.org/abs/2410.14939
- KAN Survey: https://arxiv.org/abs/2411.06078
- Hahn KAN: https://arxiv.org/abs/2601.18837
- Time-TK: https://arxiv.org/abs/2602.11190
- WaveTuner: https://arxiv.org/abs/2511.18846
- SOH-KLSTM: https://arxiv.org/abs/2509.10496
- Fourier-KAN-Mamba: https://arxiv.org/abs/2511.15083
- ss-Mamba: https://arxiv.org/abs/2506.14802
- KANMixer: https://arxiv.org/abs/2508.01575
- AR-KAN: https://arxiv.org/abs/2509.02967

### Wiener Sensor (Verified/Excluded)
- Iqbal: https://hdl.handle.net/1721.1/156552
- Hsu 2017: https://ieeexplore.ieee.org/document/8270067 (EXCLUDED)
- Kumar 2020: https://ieeexplore.ieee.org/document/8959536 (EXCLUDED)

### Drift Compensation (Verified/Excluded)
- Margarit-Taulé: DOI 10.1016/j.snb.2021.131879
- Heng 2025: NOT FOUND (EXCLUDED)
- Ren 2024: NOT FOUND (EXCLUDED)

### Measurement/Dataset (Verified/Excluded)
- Exathlon: https://arxiv.org/abs/2010.05073
- Op-GAN: https://arxiv.org/abs/2407.11040

### Architecture
- Bai TCN: https://arxiv.org/abs/1803.01271 (Reclassified: CONFLICT → VERIFIED)
