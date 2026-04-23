# Compute Cost Calibration Report

Generated at: 20260423_132153

## Recommended cost model

- Add : Mul : Map = `1 : 3.0 : 20.0`
- Scale factor `A` = `0.00010305` ms / add-equivalent
- Default log-RMSE = `0.2266`, adopted log-RMSE = `0.1341`
- Default max relative error = `42.01%`, adopted max relative error = `23.38%`

## Search summary

- Pure fit best: `1 : 652.5750 : 3326.9858`
- Regularized fit best: `1 : 3.1383 : 20.1587`
- Adopted rounded model: `1 : 3.0 : 20.0`

## Pair-wise fit

| Model | Add | Mul | Map | Measured (ms/point) | Default pred | Adopted pred | Default err (%) | Adopted err (%) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Wiener-KAN | 266 | 40 | 234 | 0.537073 | 0.370216 | 0.522036 | -31.07 | -2.80 |
| GRU | 1168 | 1136 | 64 | 0.602380 | 0.581953 | 0.603444 | -3.39 | 0.18 |
| LSTM | 1376 | 1408 | 96 | 0.701122 | 0.727442 | 0.774914 | 3.75 | 10.52 |
| LSTMTransformer | 2728 | 1208 | 92 | 0.684223 | 0.971654 | 0.844162 | 42.01 | 23.38 |
| 1DCNN | 856 | 856 | 28 | 0.497525 | 0.407021 | 0.410540 | -18.19 | -17.48 |
| RNN | 544 | 544 | 32 | 0.273755 | 0.277121 | 0.290181 | 1.23 | 6.00 |
| TCN | 1616 | 1616 | 112 | 1.068669 | 0.845218 | 0.896922 | -20.91 | -16.07 |