# STAGE - 文献分析阶段

## 当前阶段目标

为 `docs/IDEA.md` 中 "第二稿声称的贡献 3月29修订" 的 11 个 GAP 寻找文献支撑。

## GAP 列表

| GAP | 描述 | 优先级 | 当前覆盖状态 |
|-----|------|--------|-------------|
| GAP1 | 机理分析 - 电化学地震检波器温度漂移到非线性漂移 | 高 | ✅ Chikishev(强), Fasmin(弱) |
| GAP2 | 线性度测量范围偏窄 | 高 | ✅ Chen(中), Schaller(中) |
| GAP3 | 频率漂移研究 - 温度因素有，震级因素缺乏 | 高 | ✅ Chikishev(强) |
| GAP4 | 非频率漂移 - 线性模型有，非线性模型没有 | 中 | ✅ Wahlberg(强), Fasmin(中), vanMeer(强) |
| GAP5 | 频率漂移建模 - 温度因素有，震级因素没有 | 中 | ✅ Wahlberg(弱), vanMeer(弱) |
| GAP6 | 力反馈限制最大量程，前馈补偿无此限制 | 高 | ❌ 待分析 |
| GAP7 | 前馈补偿利用非线性区而非排除 | 高 | ❌ 待分析 |
| GAP8 | 频率无关方法 → 频率相关补偿能力 | 中 | ❌ 待分析 |
| GAP9 | 频率相关补偿方法 → 计算效率提升 | 中 | ❌ 待分析 |
| GAP10 | AFMAE vs 纯 MAE 改进支撑 | 中 | ❌ 待分析 |
| GAP11 | AFMAE vs 其他频率相关损失函数效率 | 低 | ❌ 待分析 |

## 已关闭的 mdissue (第一轮)

| Issue ID | 论文 | 状态 | 支撑 GAP |
|----------|------|------|----------|
| 001 | Wahlberg_2015_stochastic_Wiener.md | closed | GAP4, GAP5 |
| 002 | Chikishev_2019_Temperature_Amplitude_Frequency.md | closed | GAP1, GAP3 |
| 003 | Fasmin_2017_Nonlinear_Electrochemical.md | closed | GAP1, GAP4 |
| 004 | Chen_2025_DELOESS_LSTM_Measurement.md | closed | GAP2 |
| 005 | Schaller_2025_AutoML_Measurement.md | closed | GAP2 |
| 006 | vanMeer_2025_Hall_sensor_Wiener.md | closed | GAP4, GAP5 |

## 当前 mdissue 追踪 (第二轮)

| Issue ID | 论文 | 状态 | 支撑 GAP |
|----------|------|------|----------|
| 007 | Fang_2024_exploiting_nonlinearity.md | open | GAP6, GAP7 |
| 008 | Rodriguez_Linhares_2025_Freq_Dependent_Linearizers.md | open | GAP8, GAP9 |

## 执行记录

### 2026-03-31 第一轮完成

- 关闭 6 个 mdissue (001-006)
- 第一轮分析完成：Wahlberg, Chikishev, Fasmin, Chen, Schaller, vanMeer
- GAP1-5 已覆盖，GAP6-11 仍有缺口

### 2026-03-31 第二轮开始

- Issue 007: 分析 Fang_2024_exploiting_nonlinearity.md
  - 支撑 GAP6 (力反馈限制 vs 前馈无限制)
  - 支撑 GAP7 (前馈利用非线性区而非排除)
- Issue 008: 分析 Rodriguez_Linhares_2025_Freq_Dependent_Linearizers.md
  - 支撑 GAP8 (频率无关 → 频率相关补偿)
  - 支撑 GAP9 (频率相关补偿 → 计算效率)

## 下一步

1. 等待执行者完成 Issue 007-008 的论文分析
2. 审查者审查分析结果
3. 如 GAP10-11 仍未覆盖，补充更多论文分析
