# 调研报告：STEP1 Round 126 - 文献调研补充轮

## 基本信息
- 日期：2026-03-30
- 阶段：STEP1 调研
- 覆盖范围：Wiener-Hammerstein传感器补偿、Measurement期刊论文、KAN硬件LUT效率
- 是否使用子代理：是（3个并行子代理）

---

## 检索路径

### 子代理1：Wiener-Hammerstein传感器非线性补偿
- 关键词：Wiener-Hammerstein, electrochemical sensor, seismic sensor, feedforward compensation, amplitude-dependent frequency response
- 数据库：IEEE Xplore, ScienceDirect, Google Scholar, arXiv
- 新发现：确认Fang et al. 2024关于"利用非线性提升灵敏度"的论文

### 子代理2：Measurement期刊传感器论文
- 关键词：sensor nonlinearity calibration, drift compensation, temperature compensation, frequency response measurement
- 数据库：ScienceDirect, Google Scholar, Measurement journal
- 新发现：补充了多篇2024-2026年Measurement期刊论文

### 子代理3：KAN硬件LUT效率
- 关键词：KAN hardware, LUT efficiency, spline network, piecewise linear
- 数据库：arXiv, IEEE Xplore, Google Scholar
- 新发现：确认KAN-FIF、KANtize、LUT-KAN等论文的效率数据

---

## 新增文献线索

### 新发现高相关性论文

| 文献 | 类型 | 相关性 | 入口/链接 |
|-----|------|-------|----------|
| Fang et al. | 2024 | 利用非线性提升灵敏度（Feedforward exploits nonlinearity vs feedback suppresses） | 10.1016/j.measurement.2024.116559 |
| Lin et al. | 2020 | 电化学地震传感器温度与幅度频率特性 | 10.1016/j.measurement.2020.107518 |
| van Meer et al. | 2025 | Hall传感器Wiener系统自标定 | https://arxiv.org/abs/2505.04245 |
| Bensmann et al. | 2010 | 大幅度扰动下高阶频率响应函数 | 10.1016/j.electacta.2010.02.056 |
| Fasmin, Srinivasan | 2017 | 非线性EIS：幅度依赖阻抗 | 10.1149/2.0031712jes |
| Elliott & Sutton | 2002 | 前馈与反馈系统性能对比 | 10.1121/1.1510668 |
| Chen et al. | 2016 | MEMS惯性传感器力反馈综述 | 10.3390/s16030330 |

### KAN硬件效率论文（已有文献库已收录）

| 文献 | 年份 | 关键数据 |
|------|------|----------|
| KAN-FIF (Shen 2026) | 2026 | 94.8%参数压缩，68.7%推理加速 |
| KANtize (Errabii 2026) | 2026 | 50x BitOps减少，2.9x GPU加速 |
| LUT-KAN (Kuznetsov 2026) | 2026 | 12x CPU推理加速 |
| GRAU (Liu 2026) | 2026 | >90% LUT消耗减少 |
| BitLogic (Bührer 2026) | 2026 | <0.3M逻辑门，<20ns推理 |
| PolyKAN (Yu 2025) | 2025 | 1.2-10x GPU加速 |
| lmKAN (Pozdnyakov 2025) | 2025 | 6.0x FLOPs减少，10x H100吞吐量 |

### Measurement期刊论文（2024-2026新增）

| 文献 | 年份 | 标题 | DOI |
|------|------|-------|-----|
| Yuan et al. | 2025 | Dynamic thermal drift compensation for piezoresistive sensors | 10.1016/j.measurement.2025.118227 |
| Tian et al. | 2026 | Compensation strategy of dynamic creep drift for flexible piezoresistive sensors | 10.1016/j.measurement.2025.119846 |
| Wang et al. | 2026 | Multi-parameter fusion compensation for ZRO drift of MEMS gyroscope | 10.1016/j.measurement.2025.118892 |
| Liu et al. | 2026 | Synergistic axial-radial magnetic structure for seismic monitoring | 10.1016/j.measurement.2026.120666 |
| Nozato et al. | 2026 | Reliability evaluation of accelerometers for seismic building monitoring | 10.1016/j.measurement.2026.121200 |

---

## 待核实事项

### 优先级P0（高优先级）
- Fang et al. 2024论文的完整DOI确认：10.1016/j.measurement.2024.116559
- 验证该论文是否直接支撑"GAP7: 前馈补偿利用非线性区"

### 优先级P1（中优先级）
- 确认Measurement期刊新增论文是否已在literature_catalog.md中
- 检查是否有其他Fang et al.相关论文

### 优先级P2（低优先级）
- 补充Wiener-Hammerstein基准测试的具体参考文献格式

---

## 入口已定位

- KAN-FIF: https://arxiv.org/abs/2602.12117
- KANtize: https://arxiv.org/abs/2603.17230
- LUT-KAN: https://arxiv.org/abs/2601.03332
- van Meer 2025: https://arxiv.org/abs/2505.04245
- Fang 2024: 10.1016/j.measurement.2024.116559

---

## 对文档的影响

### 更新的文件
- docs/research/literature/20260330/STEP1_Round126_Research_Report.md（本文档）

### 是否需要更新其他文档
- literature_catalog.md：需要确认Measurement新增论文是否已收录
- raw_literature.md：需要补充Fang 2024等新发现论文

### 是否需要后续STEP2分析
- 否 - 本轮为补充性调研，GAP分析已在之前完成

---

## 原始链接

- Fang 2024: https://doi.org/10.1016/j.measurement.2024.116559
- Lin 2020: https://doi.org/10.1016/j.measurement.2020.107518
- van Meer 2025: https://arxiv.org/abs/2505.04245
- Bensmann 2010: https://doi.org/10.1016/j.electacta.2010.02.056
- Elliott 2002: https://doi.org/10.1121/1.1510668
- KAN-FIF: https://arxiv.org/abs/2602.12117
- KANtize: https://arxiv.org/abs/2603.17230
- LUT-KAN: https://arxiv.org/abs/2601.03332

---

**报告生成时间**：2026-03-30
**调研轮次**：Round 126
