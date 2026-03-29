# 调研报告：STEP1 Round52 - 系统性文献检索扩充

## 基本信息
- 日期：2026-03-29
- 阶段：STEP1 调研
- 覆盖范围：P0/P1/P2核心方向系统检索 + 缺口验证
- 是否使用子代理：是；3个并行方向（arXiv新论文、MEASUREMENT期刊、文献缺口验证）

## 检索路径

### 子代理1：arXiv新论文核查（2026年3月下旬）
- 关键词：KAN, Wiener, Hammerstein, frequency domain, spectral loss, sensor drift
- 主要数据库：arXiv (cs.LG, stat.ML, eess.SY)
- 检索式：标题/摘要关键词匹配
- 结果：无新增高相关性文献

### 子代理2：MEASUREMENT期刊论文搜索
- 关键词：sensor nonlinearity, sensor drift, electrochemical sensor, neural network calibration
- 主要数据库：CrossRef API, PubMed, Google Scholar
- 结果：大部分论文已在数据库中，新发现有限

### 子代理3：文献缺口验证
- 关键词：Wiener model sensor, KAN LUT, frequency domain loss
- 主要数据库：IEEE Xplore, arXiv
- 新发现：Huang et al. 2025 ASP-DAC (KAN硬件加速)

---

## 发现结果

### 1. 新增高相关性论文

#### Wiener模型+传感器应用
| 作者 | 年份 | 标题 | DOI | 类别 | 相关度 | 状态 |
|------|------|-------|-----|------|--------|------|
| Hou et al. | 2024 | A bias-correction modeling method of Hammerstein-Wiener systems with polynomial nonlinearities | 10.1016/j.ymssp.2024.111329 | P0 | 高 | **新增 (R52)** |

#### KAN硬件加速边缘部署
| 作者 | 年份 | 标题 | DOI | 类别 | 相关度 | 状态 |
|------|------|-------|-----|------|--------|------|
| Huang et al. | 2025 | Hardware Acceleration of KAN for Lightweight Edge Inference (ASP-DAC 2025) | 10.1145/3658617.3697677 | P2 | 高 | **新增 (R52)** |

#### 电化学传感器论文（来自PubMed）
| 作者 | 年份 | 标题 | DOI | 类别 | 相关度 | 状态 |
|------|------|-------|-----|------|--------|------|
| Li N et al. | 2026 | Data-Driven Remaining Useful Life Prediction for Pt-Rh Thermocouples Using EKF | 10.3390/s26051483 | P2 | 中 | **新增 (R52)** |
| Liang Z et al. | 2026 | Quantification of nitrite with amperometric biosensor enhanced by MLP | 10.1039/d5ay01922b | P2 | 中 | **新增 (R52)** |
| Yamanouchi et al. | 2025 | ML-Integrated Electrochemical Sensors for Free Chlorine Monitoring | 10.1021/acssensors.5c02634 | P2 | 高 | **新增 (R52)** |
| Sayghe et al. | 2026 | Fourier Neural Operators for Fast Multi-Physics Sensor Response Prediction | 10.3390/s26041165 | P1 | 高 | **新增 (R52)** |

### 2. arXiv新论文确认

**无新增高相关性文献**。共核查2026年3月25-29日arXiv提交论文，无KAN/Wiener/频域损失/传感器漂移直接相关新论文。

### 3. 文献库完整性最终确认

| 类别 | 已收录数量 | 目标 | 状态 |
|------|------------|------|------|
| KAN网络 | 50+篇 | - | ✅ 已完备 |
| Wiener模型 | 30+篇 | - | ✅ 已完备 |
| 频域损失函数 | 20+篇 | - | ✅ 已完备 |
| 漂移补偿 | 25+篇 | - | ✅ 已完备 |
| 架构效率 | 15+篇 | - | ✅ 已完备 |
| MEASUREMENT期刊 | 85篇 | 50篇 | ✅ 超额完成 |

---

## 文献缺口最终确认

| 缺口 | 状态 | 解决方案 |
|------|------|----------|
| AFMAE原始来源 | **已找到** - FreDF (Wang 2025 ICLR) + FIRE (He 2025) | 使用这两个作为理论依据 |
| KAN vs LSTM/GRU效率 | **矛盾** - 无直接证据 | 建议删除此声称，聚焦于KAN相对MLP的优势 |
| RNN vs 1D-CNN效率 | **冲突已确认** - Saha 2026: 1D-CNN快74x | **必须删除此声称** |
| KAN LUT硬件实现 | **已关闭** - KANELÉ, LUT-KAN, PolyKAN, lmKAN | 使用这些作为证据 |
| Wiener模型传感器应用 | **已找到** - Hou 2024 (Hammerstein-Wiener), Willemstein 2023/2024 | 多个传感器应用证据 |

---

## 待核实事项

- 本轮新增论文需在后续STEP2中验证
- Huang et al. 2025 ASP-DAC论文需验证PDF可访问性

---

## 对文档的影响

- 更新了 `raw_literature.md`：新增4篇论文
- 更新了 `literature_catalog.md`：添加Round52报告索引
- 是否需要更新 SUMMARY：否
- 是否需要后续 STEP2 分析：建议对新增论文进行验证

---

## 原始链接

### Wiener模型新论文
- 10.1016/j.ymssp.2024.111329 - Hou et al. (2024) Hammerstein-Wiener bias correction

### KAN硬件加速
- 10.1145/3658617.3697677 - Huang et al. (2025) ASP-DAC KAN edge inference

### 电化学传感器
- 10.3390/s26051483 - Li N et al. (2026) EKF thermocouple
- 10.1039/d5ay01922b - Liang Z et al. (2026) MLP amperometric sensor
- 10.1021/acssensors.5c02634 - Yamanouchi et al. (2025) ML electrochemical
- 10.3390/s26041165 - Sayghe et al. (2026) Fourier neural operators