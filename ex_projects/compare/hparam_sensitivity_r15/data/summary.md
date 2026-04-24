# R15 Hyperparameter Sensitivity Summary

Generated at: `2026-04-24T19:18:37`
Baseline: `FRIKANh8u6l6g8s2_e1k_lr7e4_base`

## Conclusions

- Complete axes: H_UNITS, INNER_KAN_UNITS, INNER_KAN_LAYERS, GRID_SIZE, SPLINE_ORDER.
- Incomplete axes: none.
- Strict dominators found: 1.
- GRID_SIZE and SPLINE_ORDER keep the same current LUT compute-cost estimate when H/U/L are unchanged.

## Baseline

| Axis | Value | Project | Status | Freq Drift | Sens Drift | Linearity | Compute Cost |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: |
| base |  | `FRIKANh8u6l6g8s2_e1k_lr7e4_base` | complete | 2.6221 | 14.5689 | 0.5570 | 5066.0000 |

## Axis Summary

| Axis | Complete | Missing | Best Freq | Best Sens | Best Linearity | Compute Cost Values |
| --- | ---: | ---: | --- | --- | --- | --- |
| `H_UNITS` | 7/7 | [] | `FRIKANh5u6l6g8s2_e1k_lr7e4_axisH` (2.957) | `FRIKANh9u6l6g8s2_e1k_lr7e4_axisH` (10.5) | `FRIKANh5u6l6g8s2_e1k_lr7e4_axisH` (0.5994) | [4341.0, 4486.0, 4631.0, 4776.0, 4921.0, 5211.0, 5356.0] |
| `INNER_KAN_UNITS` | 5/5 | [] | `FRIKANh8u8l6g8s2_e1k_lr7e4_axisU` (2.1) | `FRIKANh8u5l6g8s2_e1k_lr7e4_axisU` (9.69) | `FRIKANh8u7l6g8s2_e1k_lr7e4_axisU` (0.5993) | [1664.0, 2588.0, 3722.0, 6620.0, 8384.0] |
| `INNER_KAN_LAYERS` | 5/5 | [] | `FRIKANh8u6l7g8s2_e1k_lr7e4_axisL` (2.177) | `FRIKANh8u6l3g8s2_e1k_lr7e4_axisL` (11.77) | `FRIKANh8u6l7g8s2_e1k_lr7e4_axisL` (0.4648) | [2798.0, 3554.0, 4310.0, 5822.0, 6578.0] |
| `GRID_SIZE` | 5/5 | [] | `FRIKANh8u6l6g5s2_e1k_lr7e4_axisG` (3.637) | `FRIKANh8u6l6g5s2_e1k_lr7e4_axisG` (12.1) | `FRIKANh8u6l6g7s2_e1k_lr7e4_axisG` (0.6895) | [5066.0] |
| `SPLINE_ORDER` | 2/2 | [] | `FRIKANh8u6l6g8s3_e1k_lr7e4_axisS` (2.281) | `FRIKANh8u6l6g8s1_e1k_lr7e4_axisS` (12.49) | `FRIKANh8u6l6g8s3_e1k_lr7e4_axisS` (0.625) | [5066.0] |

## All Points

| Axis | Value | Project | Status | Freq Drift | Sens Drift | Linearity | Compute Cost |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: |
| base |  | `FRIKANh8u6l6g8s2_e1k_lr7e4_base` | complete | 2.6221 | 14.5689 | 0.5570 | 5066.0000 |
| H_UNITS | 3 | `FRIKANh3u6l6g8s2_e1k_lr7e4_axisH` | complete | 5.8467 | 15.5800 | 0.8788 | 4341.0000 |
| H_UNITS | 4 | `FRIKANh4u6l6g8s2_e1k_lr7e4_axisH` | complete | 3.9782 | 15.2381 | 0.7298 | 4486.0000 |
| H_UNITS | 5 | `FRIKANh5u6l6g8s2_e1k_lr7e4_axisH` | complete | 2.9568 | 12.7238 | 0.5994 | 4631.0000 |
| H_UNITS | 6 | `FRIKANh6u6l6g8s2_e1k_lr7e4_axisH` | complete | 3.3389 | 16.7806 | 0.6560 | 4776.0000 |
| H_UNITS | 7 | `FRIKANh7u6l6g8s2_e1k_lr7e4_axisH` | complete | 3.2066 | 13.2686 | 0.6905 | 4921.0000 |
| H_UNITS | 9 | `FRIKANh9u6l6g8s2_e1k_lr7e4_axisH` | complete | 3.3085 | 10.4979 | 0.6312 | 5211.0000 |
| H_UNITS | 10 | `FRIKANh10u6l6g8s2_e1k_lr7e4_axisH` | complete | 3.1691 | 16.6152 | 0.7203 | 5356.0000 |
| INNER_KAN_UNITS | 3 | `FRIKANh8u3l6g8s2_e1k_lr7e4_axisU` | complete | 4.8083 | 19.7816 | 0.9205 | 1664.0000 |
| INNER_KAN_UNITS | 4 | `FRIKANh8u4l6g8s2_e1k_lr7e4_axisU` | complete | 3.9999 | 18.5022 | 0.8577 | 2588.0000 |
| INNER_KAN_UNITS | 5 | `FRIKANh8u5l6g8s2_e1k_lr7e4_axisU` | complete | 3.8476 | 9.6899 | 0.9324 | 3722.0000 |
| INNER_KAN_UNITS | 7 | `FRIKANh8u7l6g8s2_e1k_lr7e4_axisU` | complete | 2.6160 | 12.3730 | 0.5993 | 6620.0000 |
| INNER_KAN_UNITS | 8 | `FRIKANh8u8l6g8s2_e1k_lr7e4_axisU` | complete | 2.0998 | 11.0143 | 0.6014 | 8384.0000 |
| INNER_KAN_LAYERS | 3 | `FRIKANh8u6l3g8s2_e1k_lr7e4_axisL` | complete | 2.5880 | 11.7714 | 0.6430 | 2798.0000 |
| INNER_KAN_LAYERS | 4 | `FRIKANh8u6l4g8s2_e1k_lr7e4_axisL` | complete | 3.4905 | 16.2274 | 0.6752 | 3554.0000 |
| INNER_KAN_LAYERS | 5 | `FRIKANh8u6l5g8s2_e1k_lr7e4_axisL` | complete | 2.6401 | 13.3563 | 0.6810 | 4310.0000 |
| INNER_KAN_LAYERS | 7 | `FRIKANh8u6l7g8s2_e1k_lr7e4_axisL` | complete | 2.1767 | 14.4939 | 0.4648 | 5822.0000 |
| INNER_KAN_LAYERS | 8 | `FRIKANh8u6l8g8s2_e1k_lr7e4_axisL` | complete | 2.7318 | 14.9822 | 0.6716 | 6578.0000 |
| GRID_SIZE | 3 | `FRIKANh8u6l6g3s2_e1k_lr7e4_axisG` | complete | 4.5274 | 18.2340 | 0.8900 | 5066.0000 |
| GRID_SIZE | 4 | `FRIKANh8u6l6g4s2_e1k_lr7e4_axisG` | complete | 5.9801 | 17.3043 | 0.9466 | 5066.0000 |
| GRID_SIZE | 5 | `FRIKANh8u6l6g5s2_e1k_lr7e4_axisG` | complete | 3.6372 | 12.0957 | 0.7350 | 5066.0000 |
| GRID_SIZE | 6 | `FRIKANh8u6l6g6s2_e1k_lr7e4_axisG` | complete | 4.3664 | 19.0807 | 0.7092 | 5066.0000 |
| GRID_SIZE | 7 | `FRIKANh8u6l6g7s2_e1k_lr7e4_axisG` | complete | 4.7827 | 19.2147 | 0.6895 | 5066.0000 |
| SPLINE_ORDER | 1 | `FRIKANh8u6l6g8s1_e1k_lr7e4_axisS` | complete | 12.1937 | 12.4934 | 4.1679 | 5066.0000 |
| SPLINE_ORDER | 3 | `FRIKANh8u6l6g8s3_e1k_lr7e4_axisS` | complete | 2.2806 | 14.2774 | 0.6250 | 5066.0000 |

## Figures

- `sensitivity_curves.png`
- `compute_cost.png`
