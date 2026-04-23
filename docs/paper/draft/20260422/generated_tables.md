# Machine-readable tables for the 20260422 draft

## Protocol
| Item | Value |
| --- | --- |
| Sensor sample | MTSS-1001 |
| Environment | 25 C |
| Frequency grid (saved evaluation) | 10-200 Hz, 14 sampled points |
| Magnitude sweep | 0.24-6.0 m/s^2, 25 levels |
| Sequence duration | 4.0 s |
| Sampling rate | 2000 Hz |
| Window count | 8000 sequences |
| Reference sensitivity point | 100 Hz |
| Freq-drift fitted center-frequency band | 10-128 Hz with band-limited fit_params |
| Linearity band (this draft) | <= 128 Hz, 12 points (10, 13, 16, 20, 25, 32, 40, 50, 64, 80, 100, 128 Hz) |
| Compute cost model | add:multiply:MAP = 1:3:20 |

## Main benchmark
| Model | Freq Drift (Hz) | Sens Drift (%) | Linearity (in-band, %) | Compute Cost | KEIL-MAE | KEIL speed (Points/s) | RAM (KB) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Wiener-KAN | 2.34 | 9.09 | 0.511 | 5066 | 7.11e-03 | 6986.7 | 5.6 |
| TCN | 2.65 | 16.08 | 0.517 | 8704 | 1.20e-06 | 935.7 | 106.7 |
| 1DCNN | 3.72 | 16.24 | 0.920 | 3984 | 5.51e-04 | 2009.9 | 50.9 |
| LSTM | 4.50 | 13.80 | 0.512 | 7520 | 5.07e-02 | 1426.3 | 58.7 |
| LSTMTransformer | 4.72 | 18.38 | 0.567 | 8192 | 5.05e-03 | 1461.5 | 83.7 |
| RNN | 6.68 | 23.75 | 0.726 | 2816 | 8.74e-02 | 3652.9 | 58.7 |
| GRU | 7.40 | 27.15 | 0.726 | 5856 | 2.45e-03 | 1660.1 | 58.7 |

Origin metrics: Freq Drift = 34.50 Hz, Sens Drift = 84.56 %, In-band linearity = 2.004 %.

## Loss ablation
| Variant | Active loss | Freq Drift (Hz) | Sens Drift (%) | Linearity (in-band, %) | Compute Cost | KEIL speed (Points/s) |
| --- | --- | --- | --- | --- | --- | --- |
| MAE+AFMAE | MAE+AFMAE | 2.34 | 9.09 | 0.511 | 5066 | 6986.7 |
| MAE | MAE | 13.00 | 20.28 | 0.793 | 5066 | 1861.9 |
| AFMAE | AFMAE | 4.00 | 21.06 | 1.068 | 5066 | 1861.9 |

## Structure ablation
| Variant | Freq Drift (Hz) | Sens Drift (%) | Linearity (in-band, %) | Compute Cost |
| --- | --- | --- | --- | --- |
| Wiener-KAN | 2.34 | 9.09 | 0.511 | 5066 |
| CNNKAN | 2.43 | 9.22 | 0.883 | 5074 |
| No symmetry | 10.91 | 10.61 | 2.109 | 5066 |
| Random trainable IIR | 5.34 | 21.38 | 3.216 | 5066 |
| FRIMLP | 5.82 | 27.48 | 0.782 | 11272 |
| No positive (stress) | 58.03 | 50.87 | 38.586 | 5066 |

## On-board inference evaluation
| Model | QEMU-MAE | KEIL-MAE | KEIL speed (Points/s) | Flash (KB) | RAM (KB) |
| --- | --- | --- | --- | --- | --- |
| Wiener-KAN | 7.114e-03 | 7.114e-03 | 6986.7 | 721.4 | 5.6 |
| TCN | 1.197e-06 | 1.197e-06 | 935.7 | 16.4 | 106.7 |
| 1DCNN | 5.513e-04 | 5.513e-04 | 2009.9 | 12.3 | 50.9 |
| LSTM | 5.070e-02 | 5.070e-02 | 1426.3 | 13.8 | 58.7 |
| LSTMTransformer | 5.049e-03 | 5.049e-03 | 1461.5 | 19.9 | 83.7 |
| RNN | 8.739e-02 | 8.739e-02 | 3652.9 | 10.0 | 58.7 |
| GRU | 2.451e-03 | 2.451e-03 | 1660.1 | 12.7 | 58.7 |

## Wiener-KAN optimization sweep
| Profile | Status | KEIL speed (Points/s) | Flash (KB) | RAM (KB) | Note |
| --- | --- | --- | --- | --- | --- |
| Project default | completed | 6986.7 | 719.2 | 5.6 | completed |
| -O0 | completed | 2234.5 | 728.1 | 86.8 | completed |
| -O2 | completed | 6986.7 | 719.2 | 5.6 | completed |
| -Ofast + LTO | completed | 7059.3 | 721.4 | 5.6 | completed |

## Compute-cost calibration summary
Default 1:1:6 log-RMSE = 0.2266; adopted 1:3:20 log-RMSE = 0.1341.

| Model | Measured speed (Points/s) | Default 1:1:6 | Adopted 1:3:20 | Default error (%) | Adopted error (%) |
| --- | --- | --- | --- | --- | --- |
| Wiener-KAN | 1861.9 | 2701.1 | 1915.6 | -31.07 | -2.80 |
| GRU | 1660.1 | 1718.4 | 1657.2 | -3.39 | 0.18 |
| LSTM | 1426.3 | 1374.7 | 1290.5 | 3.75 | 10.52 |
| LSTMTransformer | 1461.5 | 1029.2 | 1184.6 | 42.01 | 23.38 |
| 1DCNN | 2009.9 | 2456.9 | 2435.8 | -18.19 | -17.48 |
| RNN | 3652.9 | 3608.5 | 3446.1 | 1.23 | 6.00 |
| TCN | 935.7 | 1183.1 | 1114.9 | -20.91 | -16.07 |

## LUT implementation variants
| Variant | QEMU-MAE | KEIL-MAE | KEIL speed (Points/s) | Flash (KB) | RAM (KB) |
| --- | --- | --- | --- | --- | --- |
| LUT nearest | 7.114e-03 | 7.114e-03 | 6986.7 | 721.4 | 5.6 |
| LUT + interp | 1.902e-04 | 1.902e-04 | 3844.8 | 723.5 | 5.6 |
| No LUT exact | 6.517e-07 | 6.517e-07 | 45.0 | 33.7 | 21.2 |