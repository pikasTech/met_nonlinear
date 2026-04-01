# 消融实验对比报告

**生成时间**: 20260401_202938

---

## 1. 固有频率漂移

| Project | Drift (Hz) | Suppression (%) |
|---------|------------|-----------------|
| LSTMu16_base | 3.0349 | - |
| LSTMu16_base_pureafmae | 1.4444 | 52.41% |
| FRIKANh8u6l6_pureafmae | 85.0656 | -2702.94% |
| LSTMu16_base_puremae | 1.3334 | 56.06% |
| FRIKANh8u6l6_puremae | 626964.7169 | -20658577.25% |
| FRIKANh8u6l6_base | 3.6769 | -21.16% |

## 2. 灵敏度漂移 (100Hz)

| Project | Drift (%) | Suppression (%) |
|---------|-----------|-----------------|
| LSTMu16_base | 6.7112 | - |
| LSTMu16_base_pureafmae | 8.0952 | -20.62% |
| FRIKANh8u6l6_pureafmae | 52.1942 | -677.71% |
| LSTMu16_base_puremae | 8.4853 | -26.43% |
| FRIKANh8u6l6_puremae | 5.4321 | 19.06% |
| FRIKANh8u6l6_base | 18.1270 | -170.10% |

## 3. 线性度 (1 - R²)

| Project | Mean (%) | Max (%) | Min (%) |
|---------|----------|---------|---------|
| LSTMu16_base | 0.5593 | 2.8431 | 0.1027 |
| LSTMu16_base_pureafmae | 0.3834 | 0.8829 | 0.1087 |
| FRIKANh8u6l6_pureafmae | 85.2026 | 99.9504 | 59.0501 |
| LSTMu16_base_puremae | 0.4259 | 1.5200 | 0.0977 |
| FRIKANh8u6l6_puremae | 73.7256 | 99.8998 | 24.3490 |
| FRIKANh8u6l6_base | 0.5044 | 1.4893 | 0.0996 |
