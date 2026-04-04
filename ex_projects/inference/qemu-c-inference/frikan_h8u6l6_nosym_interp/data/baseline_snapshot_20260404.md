# FRIKAN QEMU Baseline Snapshot 2026-04-04

## Current validated build

- Config: `lut_points=769`, `lut_interpolation=true`
- Model: `projects/00_MAE_VS_AFMAE/FRIKANh8u6l6_nosym`
- Codegen status: compile-time macro pruning enabled, KAN forward path statically specialized/unrolled
- Validation source: `validation_comparison.json`
- Benchmark source: `benchmark_summary.json`
- Size source: `arm-none-eabi-size main.elf`

## Accuracy

- Overall MAE: `3.887019284811553e-05`
- Max abs error: `0.0002646386293110037`

## Timing

- Benchmark timer source: `host_elapsed`
- Benchmark-only avg host elapsed seconds: `0.8217394999999996`
- Benchmark-only avg measurement per iter: `0.08217394999999997`
- Full validation run host elapsed seconds: `1.2157128999999998`
- Full validation run measurement per iter: `0.12157128999999997`
- Legacy mixed-run baseline: `1.1781909999999982`
- Legacy mixed-run per iter: `0.11781909999999982`
- Note: benchmark-only timing now stops at `benchmark_complete=1`; older `validation_complete=1` numbers included validation UART output and are no longer comparable as pure compute baselines.

## Size

- text: `1045336`
- data: `68`
- bss: `84800`
- dec: `1130204`
- hex: `113edc`

## Historical comparison available

- Pre-unroll text: `1039996`
- Pre-unroll data: `68`
- Pre-unroll bss: `84800`
- Delta text: `+5012`
- Delta bss: `0`
