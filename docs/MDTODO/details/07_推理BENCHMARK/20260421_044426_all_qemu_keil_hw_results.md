# ?? QEMU?Keil????????20260421_044426?

- ?? UID: `205536951525`
- ??: `COM8` @ `115200`
- ????: `5`
- ????: `5 / 5`
- ??????: `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_031714_all_qemu_keil_hw_results.json`
- ????????: `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_manual_recheck_serial_raw`
- ?? JSON: `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_044426_all_qemu_keil_hw_results.json`

| ?? | QEMU | Keil Build | ?? | Validation | QEMU Output | ?? Output | |?| | cycles/iter | wall ms/iter | ?? |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| frikan_h8u6l6_nosym | OK | OK | OK | OK | -0.150343 | -0.150343 | 0 | 3214669 |  | Used the lean direct-register Keil benchmark template to remove HAL/LL overhead and fit STM32F405 flash. / Validated on hardware through DAPLink + pyOCD and serial-monitor history recheck. |
| frikan_h8u6l6_nosym_interp | OK | OK | OK | OK | -0.031542 | -0.031542 | 0 | 4372861 |  | Used the lean direct-register Keil benchmark template to remove HAL/LL overhead and fit STM32F405 flash. / Validated on hardware through DAPLink + pyOCD and serial-monitor history recheck. |
| grnu16 | OK | OK | OK | OK | -0.034183 | -0.034183 | 0 | 6403873 | 38.118396 | Keil build and hardware pass inherited from the 20260421_031714 batch verification record. |
| lstm_transformeru6_e1k_1 | OK | OK | OK | OK | -0.018894 | -0.018894 | 0 | 5936251 | 35.334800 | Keil build and hardware pass inherited from the 20260421_031714 batch verification record. |
| lstm_u16_base | OK | OK | OK | OK | -0.017555 | -0.017555 | 0 | 7500409 | 44.645396 | Keil build and hardware pass inherited from the 20260421_031714 batch verification record. |

## ??

- ????? 5 ? `qemu-c-inference` ????????? `QEMU ???? + Keil ???? + ????????`?
- `frikan_h8u6l6_nosym` ? `frikan_h8u6l6_nosym_interp` ????? 2026-04-21 ???????????? 3/5 ??????
- 3 ?? FRIKAN ????????? `cycles + wall_time_ms` ???2 ? FRIKAN ?????????? Keil ???? DWT `cycles` ??????????

## ????

- ?? JSON: `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_044426_all_qemu_keil_hw_results.json`
- ?? Markdown: `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_044426_all_qemu_keil_hw_results.md`
- FRIKAN nosym ????: `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_manual_recheck_serial_raw\frikan_h8u6l6_nosym_serial_fetch_windowed.json`
- FRIKAN nosym interp ????: `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_manual_recheck_serial_raw\frikan_h8u6l6_nosym_interp_serial_fetch_windowed.json`
- ?? 3/5 ????: `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_031714_all_qemu_keil_hw_results.json`
