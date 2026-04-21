# 全量 QEMU→Keil→真机验证结果（20260421_031714）

- 探针 UID: `205536951525`
- 串口: `COM8` @ `115200`
- 总模型数: `5`
- 全通过数: `3 / 5`
- 明细 JSON: `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_031714_all_qemu_keil_hw_results.json`

| 模型 | 类型 | Keil Build | 真机烧录 | Benchmark 完成 | Validation 完成 | DWT | cycles/iter | wall ms/iter | 输出 | 与QEMU差值 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| frikan_h8u6l6_nosym | frikan | OK | OK | FAIL | FAIL | None | None | None |  |  |
| frikan_h8u6l6_nosym_interp | frikan | OK | FAIL | FAIL | FAIL | None | None | None |  |  |
| grnu16 | grn | OK | OK | OK | OK | 1 | 6403873 | 38.118396 | -0.034183 |  |
| lstm_transformeru6_e1k_1 | lstm_transformer | OK | OK | OK | OK | 1 | 5936251 | 35.334800 | -0.018894 |  |
| lstm_u16_base | lstm | OK | OK | OK | OK | 1 | 7500409 | 44.645396 | -0.017555 |  |

## frikan_h8u6l6_nosym

- 工程: `C:\work\met_nonlinear_master\ex_projects\inference\qemu-c-inference\frikan_h8u6l6_nosym\data\benchmark_summary.json`
- Keil AXF: `C:\work\met_nonlinear_master\ex_projects\inference\qemu-c-inference\frikan_h8u6l6_nosym\keil_project\MDK-ARM\output\MET405\MET405_BENCHMARK.axf`
- Serial 原始抓取: `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_031714_serial_raw\frikan_h8u6l6_nosym_serial_fetch.json`
- 总结: `FAIL`

## frikan_h8u6l6_nosym_interp

- 工程: `C:\work\met_nonlinear_master\ex_projects\inference\qemu-c-inference\frikan_h8u6l6_nosym_interp\data\benchmark_summary.json`
- Keil AXF: `C:\work\met_nonlinear_master\ex_projects\inference\qemu-c-inference\frikan_h8u6l6_nosym_interp\keil_project\MDK-ARM\output\MET405\MET405_BENCHMARK.axf`
- Serial 原始抓取: `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_031714_serial_raw\frikan_h8u6l6_nosym_interp_serial_fetch.json`
- 总结: `FAIL`

## grnu16

- 工程: `C:\work\met_nonlinear_master\ex_projects\inference\qemu-c-inference\grnu16\data\benchmark_summary.json`
- Keil AXF: `C:\work\met_nonlinear_master\ex_projects\inference\qemu-c-inference\grnu16\keil_project\MDK-ARM\output\MET405\MET405_BENCHMARK.axf`
- Serial 原始抓取: `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_031714_serial_raw\grnu16_serial_fetch.json`
- 总结: `PASS`

## lstm_transformeru6_e1k_1

- 工程: `C:\work\met_nonlinear_master\ex_projects\inference\qemu-c-inference\lstm_transformeru6_e1k_1\data\benchmark_summary.json`
- Keil AXF: `C:\work\met_nonlinear_master\ex_projects\inference\qemu-c-inference\lstm_transformeru6_e1k_1\keil_project\MDK-ARM\output\MET405\MET405_BENCHMARK.axf`
- Serial 原始抓取: `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_031714_serial_raw\lstm_transformeru6_e1k_1_serial_fetch.json`
- 总结: `PASS`

## lstm_u16_base

- 工程: `C:\work\met_nonlinear_master\ex_projects\inference\qemu-c-inference\lstm_u16_base\data\benchmark_summary.json`
- Keil AXF: `C:\work\met_nonlinear_master\ex_projects\inference\qemu-c-inference\lstm_u16_base\keil_project\MDK-ARM\output\MET405\MET405_BENCHMARK.axf`
- Serial 原始抓取: `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_031714_serial_raw\lstm_u16_base_serial_fetch.json`
- 总结: `PASS`
