# FRIKAN QEMU Performance Snapshot 2026-04-04

## Current validated build

- Config: `lut_points=769`, `lut_interpolation=false`
- Model: `projects/00_MAE_VS_AFMAE/FRIKANh8u6l6_nosym`
- Variant intent: performance-first build with compile-time specialized LUT scale/offset and non-interpolated lookup
- Codegen status: compile-time macro pruning enabled, KAN forward path statically specialized/unrolled
- Validation source: `validation_comparison.json`
- Benchmark source: `benchmark_summary.json`
- Size source: `arm-none-eabi-size main.elf`

## Accuracy

- Overall MAE: `0.08059037731442281`
- Overall MSE: `0.009848918444233025`
- Max abs error: `0.17932863176599279`
- Note: current误差主因在 KAN/LUT 非插值近似；IIR 中间层 MAE 仍约 `4.900461445264724e-07`

## Timing

- Benchmark timer source: `host_elapsed`
- Benchmark-only avg host elapsed seconds: `0.4341356999999988`
- Benchmark-only avg measurement per iter: `0.04341356999999988`
- Full validation run host elapsed seconds: `0.8093242000000025`
- Full validation run measurement per iter: `0.08093242000000025`
- Note: benchmark-only timing停在 `benchmark_complete=1`；`validation_run` 口径包含 validation/UART 输出，不能直接当纯推理 benchmark

## Size

- text: `1045240`
- data: `68`
- bss: `84800`
- dec: `1130108`
- hex: `113e7c`

## Related validated variant

- Interpolated sibling project: `ex_projects/inference/qemu-c-inference/frikan_h8u6l6_nosym_interp`
- Interpolated config: `lut_points=769`, `lut_interpolation=true`
- Interpolated benchmark-only per iter: `0.06392591000000003`
- Interpolated validation per iter: `0.09929439000000002`
- Interpolated MAE: `3.887519284811551e-05`
- Interpolated MSE: `4.262743501533182e-09`
- Current non-interpolated snapshot is faster, but accuracy is intentionally much worse than the interpolated sibling

## Historical size comparison

- Pre-unroll text: `1039996`
- Pre-unroll data: `68`
- Pre-unroll bss: `84800`
- Delta text: `+5244`
- Delta bss: `0`
