# 分析报告：STEP2 Round 37（R37 新增论文分析）

## 基本信息
- 日期：2026-03-29
- 阶段：STEP2 分析（第37轮）
- 分析对象：R37 新增论文分析 + 文献库最终确认
- 是否使用子代理：否（本轮为确认性分析）

## R37 新增条目分析

根据 `STEP1_Round37_Research_Report.md`，R37 主要新增了以下类别的论文：

### 1. arXiv 论文（传感器漂移补偿相关）

| 论文 | 状态 | 分析结果 |
|------|------|----------|
| GNIO (2603.15281) | 已在 R27 验证 | **已验证** - 门控神经网络惯性里程计；IMU领域，**与MET电化学传感器不直接相关** |
| DCT-Based Causal CNN (2011.06681) | 已在 R35 验证 | **已验证** - 化学传感器漂移补偿的直接参考 |
| TLIO (2020) | 新增 R35 | **排除** - 惯性导航领域，IMU vs 电化学传感器漂移 |
| milliEgo (2020) | 新增 R35 | **排除** - 毫米波雷达辅助里程计，领域不匹配 |
| DIDO (2022) | 新增 R35 | **排除** - 惯性四旋翼动力学，领域不匹配 |
| Kausar 2024 (Neuromorphic-Bayesian) | 新增 R35 | **排除** - 嗅觉传感，领域不匹配 |
| Golroudbari 2024 (TE-PINN) | 新增 R35 | **排除** - Transformer增强PINN，非直接相关 |

### 2. MEASUREMENT 期刊论文分析（R37 新增约 35 篇）

R37 新增的 MEASUREMENT 期刊论文按主题分类：

#### 神经网络/深度学习传感器补偿（约 17 篇）

| 论文 | DOI | 状态 | 排除原因 |
|------|-----|------|----------|
| Schaller, Kruse 2025 (AutoML 多类异常补偿) | 10.1016/j.measurement.2025.117097 | **排除** | P2背景；AutoML方法非MET直接相关 |
| Wang et al. 2024 (LSTM温度补偿NMR) | 10.1016/j.measurement.2024.115573 | **排除** | 核磁共振传感器，非电化学 |
| Han et al. 2020 (AGA-BP电容加速度计) | 10.1016/j.measurement.2020.108019 | **排除** | MEMS电容加速度计，非电化学；BP方法已有Khan 2003/2014覆盖 |
| Zhu et al. 2025 (IAPSO-RBF石英加速度计) | 10.1016/j.measurement.2024.116603 | **排除** | 石英加速度计，非电化学 |
| 其他12篇 | - | **排除** | 领域不匹配（光纤传感、SAW压力传感、光学运动捕捉等） |

#### 温度漂移补偿（约 10 篇）

| 论文 | DOI | 状态 | 排除原因 |
|------|-----|------|----------|
| Lin et al. 2020 (电化学地震传感器温度) | 10.1016/j.measurement.2020.107518 | **已在R24验证** | 直接相关，已收录 |
| Zhao et al. 2022 (GSA-SVR光纤惯性导航) | 10.1016/j.measurement.2022.111117 | **排除** | 光纤惯性导航，非电化学 |
| 其他温度补偿论文 | - | **排除** | 领域不匹配（高温液体金属、MZI-SPR光纤应变等） |

#### 传感器标定方法（约 12 篇）

| 论文 | DOI | 状态 | 排除原因 |
|------|-----|------|----------|
| Teng, Zhang 2025 (高g加速度计校准) | 10.1016/j.measurement.2025.117987 | **排除** | 高g冲击校准，非电化学 |
| Kokuyama et al. 2022 (两轴加速度计校准) | 10.1016/j.measurement.2022.112044 | **排除** | 加速度计校准，非电化学 |
| 其他标定论文 | - | **排除** | 领域不匹配（视觉惯性、激光轮廓仪等） |

---

## 理论提取

### 核心发现

1. **R37 新增无高相关性突破**
   - 所有 R37 新增论文均为 P2 背景支持论文
   - 无新的 P0/P1 核心理论贡献

2. **领域匹配问题**
   - MET 论文针对电化学地震传感器
   - R37 大部分论文针对 MEMS 加速度计、陀螺仪、光纤传感器等
   - 这些领域的方法可借鉴但不能直接支撑核心声称

3. **已有充分覆盖**
   - 电化学传感器温度漂移：Lin et al. 2020 (R24 验证)
   - Volterra/Wiener 块模型：Xu & Wang 2008 (已验证)
   - BP 神经网络补偿：Khan 2003/2014 (已验证)
   - LSTM 温度补偿：Shi et al. 2025 PI-GRU (R17 验证)

### 与论文的相关点

R37 论文对 MET 论文的支撑关系：

| R37 论文 | 相关点 | 支撑强度 |
|----------|--------|----------|
| GNIO | 门控机制（软ZUPT） | 方法论参考（门控思想） |
| DCT-Based CNN | 化学传感器漂移补偿 | **直接支撑**（已在R35验证） |
| Schaller 2025 | AutoML 校准 | 方法论参考 |
| Lin 2020 | 电化学地震传感器温度 | **直接支撑**（已在R24验证） |

---

## 文献质量评估

### 可靠文献（已在之前轮次验证）

| 文献 | 验证轮次 | 核心贡献 |
|------|----------|----------|
| GNIO | R27 | 门控神经网络惯性里程计 |
| DCT-Based Causal CNN | R35 | 化学传感器漂移 DCT-CNN 补偿 |
| Lin et al. 2020 | R24 | 电化学地震传感器温度效应与补偿 |
| Xu & Wang 2008 | R8 | Volterra 级数传感器块模型 |

### 排除文献

| 排除项 | 排除原因 |
|--------|----------|
| TLIO, milliEgo, DIDO | IMU 惯性导航 vs 电化学传感器漂移 |
| Kausar 2024 | 嗅觉传感 vs 电化学地震 |
| Golroudbari 2024 | Transformer PINN vs KAN |
| R37 MEASUREMENT 大部分论文 | 领域不匹配（MEMS 陀螺仪、光纤、加速度计等） |

---

## 审稿意见支撑

R37 分析结果不影响现有审稿意见支撑映射：

| 审稿意见类型 | 支撑文献 | 状态 |
|-------------|----------|------|
| KAN 创新性 | Liu 2024 KAN, Cruz 2025 SS-KAN | ✅ 已完备 |
| KAN 效率（LUT） | KANtize, LUT-KAN, IoT KAN | ✅ 已完备 |
| AFMAE 频域损失 | OLMA, FreDF, Subich | ✅ 已完备 |
| Wiener 结构 | Schoukens 2009, Haber 1990 | ✅ 已完备 |
| 漂移补偿 | Zhang, Lin, DCT-Based CNN | ✅ 已完备 |

---

## 对文档的影响

| 文档 | 更新内容 |
|------|----------|
| raw_literature.md | 无需更新（R37 条目已在之前轮次处理） |
| verified_literature.md | 无需更新（R37 新增条目已在之前轮次验证/排除） |
| excluded_literature.md | 补充 R37 IMU 论文排除记录 |
| literature_catalog.md | 更新分析报告索引 |

### 新增 excluded 条目

R37 分析确认以下条目排除：

```
## R37 排除条目 (2026-03-29)

**Feng et al. - GNIO (2026)** arXiv:2603.15281
- 原因: IMU 惯性导航领域，惯性里程计 vs 电化学传感器漂移补偿
- 方法: 门控神经网络 + Motion Bank + ZUPT 机制
- 决定: 排除 R37 - 领域不匹配

**Liu et al. - TLIO (2020)** 10.1109/LRA.2020.3007421
- 原因: IMU 惯性导航，与电化学传感器漂移补偿不相关
- 决定: 排除 R37 - 领域不匹配

**Badawi et al. - DCT-Based Causal CNN (2020)** arXiv:2011.06681
- 状态: **已在 R35 验证** - 化学传感器漂移补偿直接参考
- 注: 保留在 verified_literature.md
```

---

## 原始链接

- GNIO: https://arxiv.org/abs/2603.15281
- DCT-Based CNN: https://arxiv.org/abs/2011.06681
- Lin 2020: https://doi.org/10.1016/j.measurement.2020.107518
- Schaller 2025: https://doi.org/10.1016/j.measurement.2025.117097

---

## 结论

**STEP2 R37 分析完成**：

1. ✅ R37 新增论文分析完成
2. ✅ GNIO 和 DCT-Based CNN 已在之前轮次验证
3. ✅ IMU 相关论文（TLIO, milliEgo, DIDO）确认排除
4. ✅ MEASUREMENT 期刊 R37 新增论文大部分因领域不匹配而排除
5. ✅ 文献库状态维持不变（P0/P1/P2 覆盖完备）

**文献库最终状态**：
- P0 核心理论：✅ 已完备
- P1 应用技术：✅ 已完备  
- P2 测量方法论：✅ 85+ 篇 MEASUREMENT 期刊

**建议**：进入论文撰写阶段。所有核心主张均有充分的文献支撑。

---

## 产出文件

- `docs/research/literature/20260329/STEP2_Round37_Analysis.md`（本文件）
- 更新 `docs/research/literature/excluded_literature.md`（R37 排除记录）

（文件结束）