# 调研报告：STEP1 Round 191 - 并行文献检索 (2026-03-31早)

## 基本信息
- 日期：2026-03-31
- 阶段：STEP1 调研
- 覆盖范围：GAP1-11 全覆盖，并行三方向检索
- 是否使用子代理：是（3个并行子代理）

## 检索路径

### 子代理1：Wiener/KAN网络与前馈补偿
- 关键词：Wiener model sensor, feedforward nonlinearity compensation, Hammerstein-Wiener actuator, KAN state-space
- 主要数据库：arXiv (cs.LG, stat.ML), IEEE Xplore, Google Scholar
- 新发现：Umeda 2025 (Piezo feedforward), Shen 2024 (Pneumatic feedforward)

### 子代理2：频域损失函数
- 关键词：spectral loss time series, frequency domain loss neural network, KAN efficiency
- 主要数据库：arXiv (cs.LG, eess.SY), IEEE Xplore
- 新发现：SATL, AEFIN, FreDN等2025-2026频域损失变体

### 子代理3：传感器频响漂移
- 关键词：electrochemical sensor amplitude frequency response, seismic sensor magnitude frequency drift
- 主要数据库：arXiv, IEEE Xplore, ScienceDirect
- 新发现：Lin 2020 (温度补偿84%改善), FRIKAN 2025 (幅值173%频偏)

## 发现结果

### 新增文献线索

| 文献 | 类型 | 相关性 | 入口/链接 |
|-----|------|-------|----------|
| Umeda, Kodera 2025 | P0 | 高 | arXiv:2512.18252 (GAP7) |
| Shen et al. 2024 | P0 | 高 | arXiv:2409.06961 (GAP7) |
| Li et al. 2024 | P1 | 高 | arXiv:2412.01092 (GAP7) |
| Willemstein et al. 2023 | P0 | 高 | arXiv:2302.13141 (GAP4) |
| Cruz et al. 2025 | P0 | 高 | arXiv:2506.16392 (GAP4) |
| Lin et al. 2020 | P0 | 高 | Measurement DOI (GAP1/3/5) |
| Chikishev et al. 2019 | P0 | 高 | IEEE ICSENS (GAP1/3/5) |
| FRIKAN Li et al. 2025 | P0 | 高 | IEEE TIM (GAP3/5) |

### 关键发现总结

#### GAP7 前馈补偿利用非线性
- **Umeda 2025 (arXiv:2512.18252)**: 压电执行器前馈补偿非线性，实现数量级定位精度提升
- **Shen 2024 (arXiv:2409.06961)**: 气动软执行器前馈滞后补偿，使用物理储备计算
- **Li et al. 2024 (arXiv:2412.01092)**: 深度学习非线性失真识别与补偿

#### GAP4 Wiener非线性建模
- **Cruz 2025 (arXiv:2506.16392)**: 状态空间KAN用于Wiener-Hammerstein基准
- **Willemstein 2023 (arXiv:2302.13141)**: 软流体执行器Wiener-Hammerstein模型，83%拟合度

#### GAP1/3/5 传感器频响漂移
- **Lin 2020 (Measurement)**: 温度补偿后灵敏度漂移从45%降至7%（84%改善）
- **Chikishev 2019 (IEEE ICSENS)**: 首个宽频(0.1-443Hz)宽温(-35至+70°C) AFR研究
- **FRIKAN Li 2025 (IEEE TIM)**: 幅值0.24→6.0 m/s²导致自然频率34.2→93.4 Hz（173%变化）

## GAP状态确认

| GAP编号 | 主题 | 缺口等级 | 支撑文献数 |
|---------|------|----------|-----------|
| GAP1 | 电化学地震检波器频响漂移 | 低 | 5+ |
| GAP2 | 线性度测量范围 | 低 | 6+ |
| GAP3 | 频率漂移震级因素 | 低 | 6+ |
| GAP4 | 非线性建模 | 低 | 7+ |
| GAP5 | 频率漂移震级建模 | 低 | 3+ |
| GAP6 | 前馈vs反馈量程 | 低 | 5+ |
| GAP7 | 前馈利用非线性 | **无** | 4+ |
| GAP8 | 频率相关补偿 | **无** | 8+ |
| GAP9 | 频率相关计算效率 | **无** | 5+ |
| GAP10 | AFMAE vs 纯MAE | **无** | 5+ |
| GAP11 | AFMAE vs 其他频域损失 | **无** | 4+ |

**缺口统计**：0个高缺口，0个中缺口，6个低缺口，5个无缺口

## 待核实事项

1. **Umeda 2025**: 下载PDF验证前馈补偿细节
2. **Shen 2024**: 物理储备计算用于前馈补偿需验证
3. **Lin 2020 DOI**: 确认DOI 10.1016/j.measurement.2020.107887 可访问

## 对文档的影响

- 更新文件：
  - `raw_literature.md` - 追加R191新文献条目
  - `literature_catalog.md` - 更新索引
  - `GAP文献缺口.md` - 确认GAP7-11无缺口状态

---

## 原始链接
- Umeda 2025: https://arxiv.org/abs/2512.18252
- Shen 2024: https://arxiv.org/abs/2409.06961
- Cruz 2025: https://arxiv.org/abs/2506.16392
- Willemstein 2023: https://arxiv.org/abs/2302.13141
- Lin 2020: https://doi.org/10.1016/j.measurement.2020.107887
- Chikishev 2019: https://doi.org/10.1109/ICSENS.2019.8909305
- FRIKAN: TIM-25-06440

## 报告生成时间：2026-03-31 07:00
## 调研轮次：Round 191
## 文献库状态：600+篇文献，80+PDF，11个GAP全部支撑
