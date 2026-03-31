# 文献分析索引

本文档汇总所有论文分析结果。

## 分析列表

| 论文 | 分析文件 | GAP支撑 | 分析日期 |
|------|---------|---------|---------|
| Wahlberg_2015_stochastic_Wiener | [Wahlberg_2015_stochastic_Wiener_analyze.md](Wahlberg_2015_stochastic_Wiener_analyze.md) | GAP4, GAP5, Wiener-KAN架构 | 2026-03-31 |
| Chikishev_2019_Temperature_Amplitude_Frequency | [Chikishev_2019_Temperature_Amplitude_Frequency_analyze.md](Chikishev_2019_Temperature_Amplitude_Frequency_analyze.md) | GAP1, GAP3 | 2026-03-31 |
| Fasmin_2017_Nonlinear_Electrochemical | [Fasmin_2017_Nonlinear_Electrochemical_analyze.md](Fasmin_2017_Nonlinear_Electrochemical_analyze.md) | GAP1, GAP4 | 2026-03-31 |
| Chen_2025_DE-LOESS_LSTM_Measurement | [Chen_2025_DE-LOESS_LSTM_Measurement_analyze.md](Chen_2025_DE-LOESS_LSTM_Measurement_analyze.md) | GAP2 | 2026-03-31 |
| Schaller_2025_AutoML_Measurement | [Schaller_2025_AutoML_Measurement_analyze.md](Schaller_2025_AutoML_Measurement_analyze.md) | GAP2 | 2026-03-31 |
| van_Meer_2025_Hall_sensor_Wiener | [van_Meer_2025_Hall_sensor_Wiener_analyze.md](van_Meer_2025_Hall_sensor_Wiener_analyze.md) | GAP4, GAP5 | 2026-03-31 |
| Rodriguez_Linhares_2025_Freq_Dependent_Linearizers | [Rodriguez_Linhares_2025_Freq_Dependent_Linearizers_analyze.md](Rodriguez_Linhares_2025_Freq_Dependent_Linearizers_analyze.md) | GAP8, GAP9 | 2026-03-31 |
| Fang_2024_exploiting_nonlinearity | [Fang_2024_exploiting_nonlinearity_analyze.md](Fang_2024_exploiting_nonlinearity_analyze.md) | GAP6, GAP7 | 2026-03-31 |
| FreDF_Wang_2025_ICLR | [FreDF_Wang_2025_ICLR_analyze.md](FreDF_Wang_2025_ICLR_analyze.md) | GAP10, GAP11 | 2026-03-31 |
| OLMA_Shi_2025 | [OLMA_Shi_2025_analyze.md](OLMA_Shi_2025_analyze.md) | GAP10 | 2026-03-31 |
| Subich_2025 | [Subich_2025_analyze.md](Subich_2025_analyze.md) | GAP11 | 2026-03-31 |
| Revay_2021_Recurrent_Equilibrium | [Revay_2021_Recurrent_Equilibrium_analyze.md](Revay_2021_Recurrent_Equilibrium_analyze.md) | GAP6 | 2026-03-31 |
| Willemstein_2023_WH_Piezoresistive | [Willemstein_2023_WH_Piezoresistive_analyze.md](Willemstein_2023_WH_Piezoresistive_analyze.md) | GAP7 | 2026-03-31 |
| Kuznetsov_2026_LUT_Compiled_KAN | [Kuznetsov_2026_LUT_Compiled_KAN_analyze.md](Kuznetsov_2026_LUT_Compiled_KAN_analyze.md) | GAP9 | 2026-03-31 |
| PETSA_Medeiros_2025_ICML | [PETSA_Medeiros_2025_ICML_analyze.md](PETSA_Medeiros_2025_ICML_analyze.md) | GAP8, GAP10, GAP11 | 2026-03-31 |
| Hoekstra_2026_LFR_Learning | [Hoekstra_2026_LFR_Learning_analyze.md](Hoekstra_2026_LFR_Learning_analyze.md) | GAP6 | 2026-03-31 |
| Cruz_2025_SS_KAN | [Cruz_2025_SS_KAN_analyze.md](Cruz_2025_SS_KAN_analyze.md) | GAP7 | 2026-03-31 |
| KFS_Wu_2025 | [KFS_Wu_2025_analyze.md](KFS_Wu_2025_analyze.md) | GAP8, GAP9, GAP10 | 2026-03-31 |
| Wang_2025_WaveTuner | [Wang_2025_WaveTuner_analyze.md](Wang_2025_WaveTuner_analyze.md) | GAP8, GAP9 | 2026-03-31 |

## GAP 映射

| GAP | 相关论文 |
|-----|---------|
| GAP1 (温度漂移到非线性漂移) | Chikishev_2019_Temperature_Amplitude_Frequency, Fasmin_2017_Nonlinear_Electrochemical |
| GAP2 (线性度测量范围偏窄) | Chen_2025_DE-LOESS_LSTM_Measurement, Schaller_2025_AutoML_Measurement |
| GAP3 (温度因素有，震级因素缺乏) | Chikishev_2019_Temperature_Amplitude_Frequency, Wahlberg_2015_stochastic_Wiener |
| GAP4 (线性模型有，非线性模型没有) | Wahlberg_2015_stochastic_Wiener, Fasmin_2017_Nonlinear_Electrochemical, van_Meer_2025_Hall_sensor_Wiener |
| GAP5 (温度建模，无震级建模) | Wahlberg_2015_stochastic_Wiener, van_Meer_2025_Hall_sensor_Wiener |
| GAP6 (力反馈限制最大范围，馈通无限制) | Fang_2024_exploiting_nonlinearity, Revay_2021_Recurrent_Equilibrium, Hoekstra_2026_LFR_Learning |
| GAP7 (馈通利用非线性区域而非避免) | Fang_2024_exploiting_nonlinearity, Willemstein_2023_WH_Piezoresistive, Cruz_2025_SS_KAN |
| GAP8 (频率独立→频率依赖补偿) | Rodriguez_Linhares_2025_Freq_Dependent_Linearizers, PETSA_Medeiros_2025_ICML, KFS_Wu_2025, Wang_2025_WaveTuner |
| GAP9 (频率依赖补偿→计算效率) | Rodriguez_Linhares_2025_Freq_Dependent_Linearizers, Kuznetsov_2026_LUT_Compiled_KAN, KFS_Wu_2025, Wang_2025_WaveTuner |
| GAP10 (AFMAE vs 纯MAE改进) | FreDF_Wang_2025_ICLR, OLMA_Shi_2025, PETSA_Medeiros_2025_ICML, KFS_Wu_2025 |
| GAP11 (AFMAE vs 其他频域损失函数) | FreDF_Wang_2025_ICLR, Subich_2025, PETSA_Medeiros_2025_ICML |
| Wiener-KAN架构选择 | Wahlberg_2015_stochastic_Wiener |
