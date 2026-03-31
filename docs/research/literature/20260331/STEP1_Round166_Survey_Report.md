# 调研报告：STEP1 Round 166 - 论文验证与补充调研

## 基本信息
- 日期：2026-03-31
- 阶段：STEP1 调研
- 覆盖范围：R165待核实论文验证、新增论文补充
- 是否使用子代理：否

---

## 一、R165待核实论文验证

### 1.1 Umeda & Kodera 2025 (arXiv:2512.18252)

| 项目 | 内容 |
|------|------|
| 状态 | ✅ 已下载并验证 |
| 标题 | Feedforward Compensation of Piezo Nonlinearity for High-Precision High-Speed Atomic Force Microscopy |
| 作者 | Kenichi Umeda, Noriyuki Kodera |
| 来源 | arXiv:2512.18252 (physics.app-ph) |
| 提交时间 | 2025-12-20, v2修订于2026-03-07 |
| DOI | https://doi.org/10.48550/arXiv.2512.18252 |
| PDF路径 | `docs/research/literature/pdf/2512.18252.pdf` |
| GAP支撑 | GAP6 (前馈vs反馈补偿), GAP7 (前馈利用非线性) |
| 核心发现 | 软件前馈方法补偿压电非线性，定位精度提升一个数量级 |
| 相关度 | **最高** |

**摘要关键内容：**
- 原子力显微镜(AFM)使用压电执行器扫描，非线性响应引入图像缩放误差达20-30%
- 提出简单的软件前馈方法生成扫描波形
- 识别压电扫描仪的四个定位误差源并补偿
- 无需额外硬件，保留成像速度

### 1.2 Fang 2024 (Measurement)

| 项目 | 内容 |
|------|------|
| 状态 | ⚠️ 已在catalog中，需机构订阅 |
| DOI | 10.1016/j.measurement.2024.116559 |
| 标题 | Exploiting nonlinearity for sensitivity enhancement of TPoS micromachined gas sensor |
| GAP支撑 | GAP7 (前馈利用非线性提升灵敏度) |
| 相关度 | 高 |
| 本地PDF | 无（需机构订阅） |

**说明：** 该论文在literature_catalog.md中已收录多次(R21, R35, R51, R111, R128, R139, R165)，标注为"无法下载（需机构订阅）"。核心观点：前馈方法利用非线性提升灵敏度，而非反馈方法抑制非线性。

### 1.3 Barbieri 2025 (Measurement)

| 项目 | 内容 |
|------|------|
| 状态 | ⚠️ 已在catalog中，需机构订阅 |
| DOI | 10.1016/j.measurement.2025.118373 |
| 标题 | A novel harmonic compensation technique of voltage transformers through an analytic Volterra-based method |
| GAP支撑 | GAP4 (线性模型缺乏非线性建模) |
| 相关度 | 高 |
| 本地PDF | 无（需机构订阅） |

**说明：** 该论文在literature_catalog.md中已收录(R69, R139)，标注为"无法下载（需机构订阅）"。Volterra方法用于谐波补偿，体现了非线性建模的重要性。

---

## 二、新增论文记录

### 2.1 本次新增

| 论文 | DOI/来源 | GAP支撑 | PDF状态 |
|------|----------|---------|---------|
| Umeda & Kodera 2025 | arXiv:2512.18252 | GAP6, GAP7 | ✅ 已下载 |

### 2.2 已存在待获取

| 论文 | DOI | GAP支撑 | 获取难度 |
|------|-----|---------|----------|
| Fang 2024 | 10.1016/j.measurement.2024.116559 | GAP7 | 高（需机构订阅） |
| Barbieri 2025 | 10.1016/j.measurement.2025.118373 | GAP4 | 高（需机构订阅） |

---

## 三、GAP文档更新建议

| GAP | 当前状态 | 建议更新 |
|-----|---------|---------|
| GAP6 | 低缺口 | 添加Umeda 2025作为前馈补偿直接证据，PDF路径: pdf/2512.18252.pdf |
| GAP7 | 无缺口 | Fang 2024已有记录，建议标注"利用非线性"核心论点 |

---

## 四、结论

1. **Umeda 2025**验证完成 - 前馈补偿压电非线性直接证据，已下载PDF
2. **Fang 2024**和**Barbieri 2025**因需机构订阅无法下载，但已在catalog中多次记录
3. 所有11个GAP均无高缺口，文献支撑充分

---

**报告生成时间**：2026-03-31
**调研轮次**：Round 166
