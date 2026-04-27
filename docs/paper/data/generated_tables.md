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

## Main benchmark
| Model | Freq Drift (Hz) | Sens Drift (%) | Linearity (in-band, %) | KEIL-MAE | KEIL speed (Points/s) | RAM (KB) |
| --- | --- | --- | --- | --- | --- | --- |
| Wiener-KAN | 2.34 | 9.09 | 0.511 | 7.11e-03 | 6986.7 | 5.6 |
| TCN | 2.65 | 16.08 | 0.517 | 1.20e-06 | 935.7 | 106.7 |
| 1DCNN | 3.72 | 16.24 | 0.920 | 5.51e-04 | 2009.9 | 50.9 |
| LSTM | 4.50 | 13.80 | 0.512 | 5.07e-02 | 1426.3 | 58.7 |
| LSTMTransformer | 4.72 | 18.38 | 0.567 | 5.05e-03 | 1461.5 | 83.7 |
| RNN | 6.68 | 23.75 | 0.726 | 8.74e-02 | 3652.9 | 58.7 |
| GRU | 7.40 | 27.15 | 0.726 | 2.45e-03 | 1660.1 | 58.7 |

Origin metrics: Freq Drift = 34.50 Hz, Sens Drift = 84.56 %, In-band linearity = 2.004 %.

## Loss ablation
| Variant | Active loss | Freq Drift (Hz) | Sens Drift (%) | Linearity (in-band, %) | QEMU-MAE | KEIL-MAE | KEIL speed (Points/s) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MAE+AFMAE | MAE+AFMAE | 2.34 | 9.09 | 0.511 | 7.114e-03 | 7.114e-03 | 6986.7 |
| MAE | MAE | 13.00 | 20.28 | 0.793 | 2.137e-02 | 2.137e-02 | 6986.7 |
| AFMAE | AFMAE | 4.00 | 21.06 | 1.068 | 3.968e-03 | 3.968e-03 | 6986.7 |

## Structural ablation
| Variant | Freq Drift (Hz) | Sens Drift (%) | Linearity (in-band, %) |
| --- | --- | --- | --- |
| Wiener-KAN | 2.34 | 9.09 | 0.511 |
| CNN-KAN | 2.43 | 9.22 | 0.883 |
| No symmetry | 10.91 | 10.61 | 2.109 |
| Random trainable IIR | 5.34 | 21.38 | 3.216 |
| Wiener-MLP | 5.82 | 27.48 | 0.782 |
| No positive (stress) | 58.03 | 50.87 | 38.586 |

## Wiener front-end ablation
| Variant | Epochs | Freq Drift (Hz) | Sens Drift (%) | Linearity (in-band, %) |
| --- | --- | --- | --- | --- |
| System prior, frozen | 1000 | 2.34 | 9.09 | 0.511 |
| Random, frozen | 1000 | 5.37 | 22.28 | 1.308 |
| System prior, trainable | 251 | 94.87 | 64.68 | 7.478 |
| Random, trainable | 1000 | 102.57 | 16.65 | 5.144 |

## Ablation overview
| Group | Variant | Controlled contrast | Freq Drift (Hz) | Sens Drift (%) | Linearity (in-band, %) |
| --- | --- | --- | --- | --- | --- |
| **Baseline** | **B-spline + Odd+pos. + System, fixed, + MAE + AFMAE** | **Shared canonical Wiener-KAN setting** | **2.34** | **9.09** | **0.511** |
| Struct | CNN-KAN | Conv front replaces Wiener front | 2.43 | 9.22 | 0.883 |
| Struct | Wiener-MLP | MLP replaces KAN mapping | 5.82 | 27.48 | 0.782 |
| Constr. | Positive | No odd symmetry | 10.91 | 10.61 | 2.109 |
| Constr. | Odd | No positive basis | 58.03 | 50.87 | 38.586 |
| Wiener front | Random / fixed | Random init., frozen | 5.37 | 22.28 | 1.308 |
| Wiener front | System / trainable | Measured init., trainable | 94.87 | 64.68 | 7.478 |
| Wiener front | Random / trainable | Random init., trainable | 102.57 | 16.65 | 5.144 |
| Loss | MAE | Time-domain pointwise loss | 13.00 | 20.28 | 0.793 |
| Loss | AFMAE | Amplitude-frequency loss | 4.00 | 21.06 | 1.068 |

## On-board inference evaluation
| Model | QEMU-MAE | KEIL-MAE | KEIL speed (Points/s) | Flash (KB) | RAM (KB) |
| --- | --- | --- | --- | --- | --- |
| Wiener-KAN | 7.114e-03 | 7.114e-03 | 6986.7 | 719.2 | 5.6 |
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

## LUT implementation variants
| Variant | QEMU-MAE | KEIL-MAE | KEIL speed (Points/s) | Flash (KB) | RAM (KB) |
| --- | --- | --- | --- | --- | --- |
| LUT nearest | 7.114e-03 | 7.114e-03 | 6986.7 | 719.2 | 5.6 |
| LUT + interp | 1.902e-04 | 1.902e-04 | 3844.8 | 723.5 | 5.6 |
| No LUT exact | 6.517e-07 | 6.517e-07 | 45.0 | 33.7 | 21.2 |

## LUT quantization-point sweep
| LUT points | Nearest QEMU-MAE | Interp QEMU-MAE | Nearest Flash (KB) | Interp Flash (KB) |
| --- | --- | --- | --- | --- |
| 65 | 5.071e+00 | 5.426e-02 | 75.7 | 79.8 |
| 129 | 2.279e-01 | 1.391e-02 | 134.2 | 138.2 |
| 257 | 1.155e-01 | 2.801e-03 | 251.3 | 255.3 |
| 513 | 2.278e-02 | 5.259e-04 | 485.2 | 489.5 |
| 769 | 7.114e-03 | 1.902e-04 | 719.2 | 723.5 |