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

## GAP 映射

| GAP | 相关论文 |
|-----|---------|
| GAP1 (温度漂移到非线性漂移) | Chikishev_2019_Temperature_Amplitude_Frequency, Fasmin_2017_Nonlinear_Electrochemical |
| GAP2 (线性度测量范围偏窄) | Chen_2025_DE-LOESS_LSTM_Measurement, Schaller_2025_AutoML_Measurement |
| GAP3 (温度因素有，震级因素缺乏) | Chikishev_2019_Temperature_Amplitude_Frequency, Wahlberg_2015_stochastic_Wiener |
| GAP4 (线性模型有，非线性模型没有) | Wahlberg_2015_stochastic_Wiener, Fasmin_2017_Nonlinear_Electrochemical, van_Meer_2025_Hall_sensor_Wiener |
| GAP5 (温度建模，无震级建模) | Wahlberg_2015_stochastic_Wiener, van_Meer_2025_Hall_sensor_Wiener |
| Wiener-KAN架构选择 | Wahlberg_2015_stochastic_Wiener |
