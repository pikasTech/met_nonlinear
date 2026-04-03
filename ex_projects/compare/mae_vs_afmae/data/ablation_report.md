# 消融实验对比报告

**生成时间**: 20260402_171746

---

## 1. 固有频率漂移

| Project | Drift (Hz) | Suppression (%) |
|---------|------------|-----------------|
| LSTMu16_base | 3.0349 | - |
| LSTMu12_puremae | 2.0507 | 32.43% |
| FRIKANh8u6l6_base | 3.6769 | -21.16% |
| FRIKANh8u6l6_puremae | 626964.7169 | -20658577.25% |
| FRIKANh8u6l6_pureafmae | 85.0656 | -2702.94% |
| FRIKANh8u6l6_nosym | 2.4708 | 18.59% |
| FRIKANh8u6l6_nosym_puremae | 196339.0207 | -6469330.18% |
| FRIKANh8u6l6_nosym_pureafmae | 645.8287 | -21180.25% |
| FRIKANh8u6l6 | 1.1996 | 60.47% |
| FRIKANh8u6l6_4 | 1.1454 | 62.26% |
| FRIKANh8u6l6_5 | 1.3576 | 55.27% |
| FRIKANh8u6l6_6 | 1.2412 | 59.10% |

## 2. 灵敏度漂移 (100Hz)

| Project | Drift (%) | Suppression (%) |
|---------|-----------|-----------------|
| LSTMu16_base | 6.7112 | - |
| LSTMu12_puremae | 12.6579 | -88.61% |
| FRIKANh8u6l6_base | 18.1270 | -170.10% |
| FRIKANh8u6l6_puremae | 5.4321 | 19.06% |
| FRIKANh8u6l6_pureafmae | 52.1942 | -677.71% |
| FRIKANh8u6l6_nosym | 10.3640 | -54.43% |
| FRIKANh8u6l6_nosym_puremae | 58.3722 | -769.77% |
| FRIKANh8u6l6_nosym_pureafmae | 352.8043 | -5156.92% |
| FRIKANh8u6l6 | 5.5732 | 16.96% |
| FRIKANh8u6l6_4 | 7.1201 | -6.09% |
| FRIKANh8u6l6_5 | 5.6001 | 16.56% |
| FRIKANh8u6l6_6 | 8.6753 | -29.26% |

## 3. 线性度 (1 - R²)

| Project | Mean (%) | Max (%) | Min (%) |
|---------|----------|---------|---------|
| LSTMu16_base | 0.5593 | 2.8431 | 0.1027 |
| LSTMu12_puremae | 0.3298 | 0.8107 | 0.1240 |
| FRIKANh8u6l6_base | 0.5044 | 1.4893 | 0.0996 |
| FRIKANh8u6l6_puremae | 73.7256 | 99.8998 | 24.3490 |
| FRIKANh8u6l6_pureafmae | 85.2026 | 99.9504 | 59.0501 |
| FRIKANh8u6l6_nosym | 0.6697 | 1.4795 | 0.2632 |
| FRIKANh8u6l6_nosym_puremae | 40.0392 | 99.8409 | 9.2453 |
| FRIKANh8u6l6_nosym_pureafmae | 78.9003 | 99.2905 | 38.7267 |
| FRIKANh8u6l6 | 0.4973 | 1.3998 | 0.0702 |
| FRIKANh8u6l6_4 | 0.4996 | 1.5492 | 0.0748 |
| FRIKANh8u6l6_5 | 0.4856 | 1.3425 | 0.0685 |
| FRIKANh8u6l6_6 | 0.5372 | 1.2566 | 0.1261 |
