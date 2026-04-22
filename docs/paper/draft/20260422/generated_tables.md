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
| Linearity band (this draft) | <= 128 Hz, 12 sampled points (10, 13, 16, 20, 25, 32, 40, 50, 64, 80, 100, 128 Hz) |

## Main benchmark
| Model | Freq Drift (Hz) | Sens Drift (%) | Linearity (in-band, %) | Compute Cost | Params |
| --- | --- | --- | --- | --- | --- |
| Wiener-KAN | 2.34 | 9.09 | 0.51 | 1710 | 2569 |
| TCN | 2.65 | 16.08 | 0.52 | 3904 | 1697 |
| 1DCNN | 3.72 | 16.24 | 0.92 | 1880 | 885 |
| LSTM | 4.50 | 13.80 | 0.51 | 3360 | 1441 |
| LSTMTransformer | 4.72 | 18.38 | 0.57 | 4488 | 1261 |
| RNN | 6.68 | 23.75 | 0.73 | 1280 | 577 |
| GRU | 7.40 | 27.15 | 0.73 | 2688 | 1201 |

Origin metrics: Freq Drift = 34.50 Hz, Sens Drift = 84.56 %, In-band linearity = 2.00 %.

## Loss ablation
| Variant | Active loss | Freq Drift (Hz) | Sens Drift (%) | Linearity (in-band, %) | Val MAE | Val AFMAE |
| --- | --- | --- | --- | --- | --- | --- |
| MAE+AFMAE | MAE+AFMAE | 2.34 | 9.09 | 0.51 | 0.0225 | 0.0379 |
| MAE | MAE | 13.00 | 20.28 | 0.79 | 0.0105 | 0.0903 |
| AFMAE | AFMAE | 4.00 | 21.06 | 1.07 | 0.0687 | 0.0350 |

## Structure ablation
| Variant | Freq Drift (Hz) | Sens Drift (%) | Linearity (in-band, %) | Compute Cost |
| --- | --- | --- | --- | --- |
| Wiener-KAN | 2.34 | 9.09 | 0.51 | 1710 |
| CNNKAN | 2.43 | 9.22 | 0.88 | 1718 |
| No symmetry | 10.91 | 10.61 | 2.11 | 1710 |
| Random trainable IIR | 5.34 | 21.38 | 3.22 | 1710 |
| FRIMLP | 5.82 | 27.48 | 0.78 | 5152 |
| No positive (stress) | 3.26e+05 | 50.87 | 38.59 | 1710 |

## Deployment subset
| Model | QEMU-MAE | KEIL-MAE | KEIL speed (ms/point) | Flash (KB) | RAM (KB) |
| --- | --- | --- | --- | --- | --- |
| Wiener-KAN | 7.114e-03 | 7.114e-03 | 0.537 | 1022.0 | 21.2 |
| GRU | 2.451e-03 | 2.451e-03 | 0.602 | 12.7 | 58.7 |
| LSTMTransformer | 5.049e-03 | 5.049e-03 | 0.684 | 19.9 | 83.7 |
| LSTM | 5.070e-02 | 5.070e-02 | 0.701 | 13.8 | 58.7 |
| 1DCNN(board-ready) | 1.751e-06 | 1.751e-06 | 0.697 | 17.4 | 125.9 |
| TCN | 1.197e-06 | 1.197e-06 | 1.069 | 16.4 | 106.7 |