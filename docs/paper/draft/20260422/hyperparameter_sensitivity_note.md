# Wiener-KAN Hyperparameter Sensitivity Draft

## Purpose

This draft consolidates the final R15 hyperparameter sensitivity results for the paper subsection on hyperparameter sensitivity and robustness. The intended paper framing is a controlled one-factor sweep with unified metrics and an accuracy-complexity trade-off.

## Experimental Scope

The canonical baseline is:

- `projects/09_HPARAM_SENSITIVITY/FRIKANh8u6l6g8s2_e1k_lr7e4_base`

The shorthand `h8u6l6g8s2` means:

- `h`: `H_UNITS`, the Wiener/IIR feature dimension passed to the KAN body.
- `u`: `INNER_KAN_UNITS`, the KAN body width.
- `l`: `INNER_KAN_LAYERS`, the KAN body depth.
- `g`: `GRID_SIZE`, the spline grid size.
- `s`: `SPLINE_ORDER`, the spline order.

This experiment compares one-factor perturbations within the same Wiener-KAN design. It should not be described as an exhaustive global search.

## Fixed Conditions

- `epoch_train = 1000`
- `learning_rate = 7e-4`
- Baseline `MAE+AFMAE` loss
- Same dataset, input window, scaler, and evaluation pipeline
- One independent project path per variant under `projects/09_HPARAM_SENSITIVITY/`

## Sweep Range

| Axis | Baseline | Scanned values |
| --- | ---: | --- |
| `H_UNITS` | 8 | 3, 4, 5, 6, 7, 9, 10 |
| `INNER_KAN_UNITS` | 6 | 3, 4, 5, 7, 8 |
| `INNER_KAN_LAYERS` | 6 | 3, 4, 5, 7, 8 |
| `GRID_SIZE` | 8 | 3, 4, 5, 6, 7 |
| `SPLINE_ORDER` | 2 | 1, 3 |

## Formal Data Source

```powershell
conda run --no-capture-output -n tf26 python cli.py ep "compare/hparam_sensitivity_r15"
```

Outputs:

- `ex_projects/compare/hparam_sensitivity_r15/data/summary.json`
- `ex_projects/compare/hparam_sensitivity_r15/data/summary.csv`
- `ex_projects/compare/hparam_sensitivity_r15/data/summary.md`
- `ex_projects/compare/hparam_sensitivity_r15/data/sensitivity_curves.png`
- `ex_projects/compare/hparam_sensitivity_r15/data/compute_cost.png`

## Baseline Result

| Project | Freq Drift (Hz) | Sens Drift (%) | Linearity (%) | Compute Cost |
| --- | ---: | ---: | ---: | ---: |
| `FRIKANh8u6l6g8s2_e1k_lr7e4_base` | 2.6221 | 14.5689 | 0.5570 | 5066 |

## Axis Completion

| Axis | Complete | Missing | Complete values | Compute Cost values |
| --- | ---: | ---: | --- | --- |
| `H_UNITS` | 7/7 | 0 | [3, 4, 5, 6, 7, 9, 10] | [4341.0, 4486.0, 4631.0, 4776.0, 4921.0, 5211.0, 5356.0] |
| `INNER_KAN_UNITS` | 5/5 | 0 | [3, 4, 5, 7, 8] | [1664.0, 2588.0, 3722.0, 6620.0, 8384.0] |
| `INNER_KAN_LAYERS` | 5/5 | 0 | [3, 4, 5, 7, 8] | [2798.0, 3554.0, 4310.0, 5822.0, 6578.0] |
| `GRID_SIZE` | 5/5 | 0 | [3, 4, 5, 6, 7] | [5066.0] |
| `SPLINE_ORDER` | 2/2 | 0 | [1, 3] | [5066.0] |

## Paper Paragraph Draft

> To evaluate the robustness of the proposed Wiener-KAN configuration, we performed a one-factor hyperparameter sensitivity analysis around the canonical `h8u6l6g8s2` baseline. The training epoch, learning rate, loss function, dataset split, and evaluation pipeline were fixed, while one of the five main hyperparameters was changed at a time: the Wiener feature dimension (`H_UNITS`), KAN width (`INNER_KAN_UNITS`), KAN depth (`INNER_KAN_LAYERS`), spline grid size, and spline order. The baseline achieved `Freq Drift = 2.62 Hz`, `Sens Drift = 14.57%`, `Linearity = 0.557%`, and `Compute Cost = 5066`. Across the one-factor sweep, all axes were completed and most nearby configurations produced comparable physical metrics, indicating that the proposed configuration is not a fragile isolated optimum. A deeper KAN variant (`INNER_KAN_LAYERS = 7`) further reduced all three physical errors, but increased the static inference estimate from `5066` to `5822`. We therefore retain the baseline as the default accuracy-complexity trade-off and report the deeper variant as a high-capacity alternative. In contrast, changing the spline grid size or spline order did not change the current LUT-based compute-cost estimate, confirming that these parameters mainly affect the learned static nonlinearity rather than the deployed inference path.

## Writing Boundary

1. Do not describe this as a global tuning search or a theoretical optimum.
2. Report `Freq Drift`, `Sens Drift`, `Linearity`, and `Compute Cost` together.
3. `Compute Cost` is a static estimate, not Keil measured throughput.
4. The `GRID_SIZE` / `SPLINE_ORDER` cost conclusion holds under fixed `H/U/L` and the current cost model.

## Related Files

- `docs/reference/paper_hyperparameter_sensitivity_method.md`
- `docs/reference/paper_metric_calculation_method.md`
- `docs/reference/training.md`
- `projects/09_HPARAM_SENSITIVITY/R15_projects.tsv`
- `ex_projects/compare/hparam_sensitivity_r15/config.json`
- `ex_projects/compare/hparam_sensitivity_r15/data/summary.json`
- `ex_projects/compare/hparam_sensitivity_r15/data/summary.md`
