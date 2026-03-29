# 调研报告：STEP1 Round 11 并行扩展调研

## 基本信息
- 日期：2026-03-28
- 阶段：STEP1 调研
- 覆盖范围：RNN vs CNN效率冲突核实、传感器补偿文献核实、KAN效率对比、Wiener传感器应用
- 是否使用子代理：是（4个并行子代理）

## 检索路径

### 子代理1：RNN vs CNN效率冲突核实
- 目标：核实RNN vs 1D-CNN效率声称冲突
- 核实论文：Saha 2026, Bian 2025 TCN, Bai 2018
- 发现：**声称被否定** - 1D-CNN实际比RNN更高效

### 子代理2：传感器补偿文献核实
- 目标：核实Pending状态传感器文献
- 核实结果：仅Iqbal 2024可访问（MIT DSpace开放获取）

### 子代理3：KAN效率对比论文
- 目标：搜索2024-2026年KAN效率对比论文
- 发现：多个KAN效率变体论文

### 子代理4：Wiener传感器应用文献
- 目标：搜索Wiener在电化学/地震传感器中的应用
- 发现：文献较少，集中在2020-2022年

---

## 发现结果

### 1. RNN vs 1D-CNN效率冲突 - **声称被否定**

| 论文 | 年份 | 发现 | 与声称关系 |
|------|------|------|-----------|
| Saha, Samanta | 2026 | 1D-CNN: RAM少35%, Flash少25%, **74x更快** (27.6ms vs 2038ms), 准确率95% vs 89% | **否定** |
| Bian et al. TinierHAR | 2025 | CNN比DeepConvLSTM**参数少43.3x**, MACs少58.6x | **否定** |
| Bai et al. TCN | 2018 | 空洞卷积在不增加参数情况下实现更长记忆 | **支持CNN**（不证明RNN更少参数） |
| Yin et al. | 2017 | CNN实现O(1)复杂度 vs RNN的O(n) | **支持CNN** |

**结论：论文声称"RNN的计算参数少于1D-CNN"被**否定**。证据表明1D-CNN（特别是深度可分离卷积和TCN）在参数效率和推理速度上优于RNN/LSTM。**

**来源：** arXiv:2603.04860, arXiv:2507.07949, arXiv:1803.01271

---

### 2. 传感器补偿文献核实结果

| 论文 | 状态 | 备注 |
|------|------|------|
| Iqbal 2024 (MIT DSpace) | **可访问** | 开放获取MIT论文；Volterra系统分析电化学传感器 |
| Kumar 2020 IEEE Sensors | PAYWALLED | E-tongue非线性建模 |
| Shi 2022 Sensors | PAYWALLED | EEMD-GRNN MEMS漂移补偿 |
| Zhou 2025 IEEE Sensors | PAYWALLED | LSTM MEMS海床变形 |
| Sinha 2020 Microelectronics | NOT FOUND | DOI返回404 |
| Khatri 2021 Springer | NOT FOUND | 无DOI，无法定位 |
| Margarit-Taulé 2022 | 已核实 | 已在verified_literature.md |

**关键：** Iqbal 2024 (MIT DSpace) 已可访问，Volterra系统分析直接相关

**来源：** https://handle.dlib.net/1721.1/156552

---

### 3. KAN效率对比新论文（2026）

| 作者 | 年份 | 标题 | DOI | 关键发现 | 状态 |
|------|------|------|-----|----------|------|
| Gaonkar et al. | 2026 | KAN vs MLP: Paradigm Shift | https://doi.org/10.48550/arXiv.2601.10563 | KAN更高精度+更低FLOPs | New |
| DualFlexKAN | 2026 | Dual-stage KAN | https://doi.org/10.48550/arXiv.2603.08583 | 参数少1-2个数量级 | New |
| FEKAN | 2026 | Feature-Enriched KAN | https://doi.org/10.48550/arXiv.2602.16530 | 解决KAN高计算成本问题 | New |
| KANtize | 2026 | Low-bit Quantization | https://doi.org/10.48550/arXiv.2603.17230 | **BitOps减少50x**, GPU加速2.9x, ASIC面积减少72% | New |
| VIKIN | 2026 | Reconfigurable KAN Accelerator | https://doi.org/10.48550/arXiv.2603.01165 | KAN加速1.28x，能效4.87x | New |
| KAN-We-Flow | 2026 | KAN for Robotic Manipulation | https://doi.org/10.48550/arXiv.2602.01115 | 参数比UNets少86.8% | New |
| GAC-KAN | 2026 | GNSS Interference Classifier | https://doi.org/10.48550/arXiv.2602.11186 | 仅0.13M参数，比ViT少660x | New |
| QuantKAN | 2025 | Quantization Framework | https://doi.org/10.48550/arXiv.2511.18689 | 低位量化支持边缘部署 | New |

**混合/争议发现：**
| 作者 | 年份 | 发现 | DOI |
|------|------|------|-----|
| Spotorno et al. | 2026 | KAN在深度配置中不稳定，MLP更优 | https://doi.org/10.48550/arXiv.2602.09988 |
| Pérez-Bernal et al. | 2025 | PINNs比PIKAN快1000x | https://doi.org/10.48550/arXiv.2512.12074 |

**关键：** KAN vs LSTM/GRU直接对比文献仍为空白；KAN效率优势主要相对于MLP和Transformer

---

### 4. Wiener传感器应用文献

**新增发现：**

| 作者 | 年份 | 标题 | DOI | 备注 |
|------|------|------|-----|------|
| Risuleo, Hjalmarsson | 2020 | Nonparametric WH models | 10.1016/j.ifacol.2020.12.198 | 块结构非线性系统非参数辨识 |
| 2021 | Fractional-Order Block-Oriented | 10.21203/rs.3.rs-656103/v1 | 电池模型应用 | New |
| 2022 | Wiener-Hammerstein新方法 | 10.1002/rnc.6135 | 两阶段辨识方法 | New |

**结论：** 近期（2020-2026）Wiener模型在电化学/地震传感器中直接应用文献较少，集中在一般系统辨识方法论而非特定传感器应用。

---

## 待核实事项

1. RNN vs CNN效率声称必须从论文中删除
2. KAN vs LSTM/GRU直接对比文献仍存在空白
3. Iqbal 2024已可访问，应更新为Verified状态
4. KAN效率声称应聚焦于KAN vs MLP/Transformer，而非RNN vs CNN

---

## 对文档的影响

- 更新 `docs/research/literature/raw_literature.md`：
  - RNN vs CNN冲突条目更新为"Confirmed CONFLICT - Claim Contradicted"
  - 新增KAN效率论文（Gaonkar, DualFlexKAN, FEKAN, KANtize, VIKIN, KAN-We-Flow, GAC-KAN, QuantKAN）
  - Iqbal 2024状态更新为"Verified"
  - 新增Wiener模型传感器应用文献
- 更新 `docs/research/literature/literature_catalog.md`：
  - 新增KAN效率分类
  - 更新Architecture Efficiency冲突标注
  - 新增Survey Report Index引用
- 创建本调研报告

---

## 原始链接

### RNN vs CNN冲突
- https://arxiv.org/abs/2603.04860 (Saha 2026)
- https://arxiv.org/abs/2507.07949 (Bian 2025 TinierHAR)
- https://arxiv.org/abs/1803.01271 (Bai TCN)

### 传感器文献
- https://handle.dlib.net/1721.1/156552 (Iqbal 2024)

### KAN效率论文
- https://doi.org/10.48550/arXiv.2601.10563 (Gaonkar 2026)
- https://doi.org/10.48550/arXiv.2603.08583 (DualFlexKAN 2026)
- https://doi.org/10.48550/arXiv.2602.16530 (FEKAN 2026)
- https://doi.org/10.48550/arXiv.2603.17230 (KANtize 2026)
- https://doi.org/10.48550/arXiv.2603.01165 (VIKIN 2026)
- https://doi.org/10.48550/arXiv.2602.01115 (KAN-We-Flow 2026)
- https://doi.org/10.48550/arXiv.2602.11186 (GAC-KAN 2026)
- https://doi.org/10.48550/arXiv.2511.18689 (QuantKAN 2025)

### Wiener传感器应用
- https://doi.org/10.1016/j.ifacol.2020.12.198 (Risuleo 2020)
- https://doi.org/10.1002/rnc.6135 (Wiener-Hammerstein 2022)
