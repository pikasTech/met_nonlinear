# Horizontal Reset QEMU/Keil Results (2026-04-21 10:38:28)

- Models: 6
- Probe UID: `205536951525`; serial: `COM8` @ `115200`
- Program backend: `keil`
- All `validation_complete=1`: `True`
- Max |Keil MAE - QEMU MAE|: `0.000000000065`
- Max HW-vs-QEMU waveform MAE: `0.000000007564`
- Raw serial captures: `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_103441_horizontal_reset_serial_raw`

| Model | QEMU MAE | QEMU host ms/iter | Keil MAE | Keil cycles/iter | Keil ms/iter | HW vs QEMU MAE | Raw serial |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| FRIKANh8u6l6_e1k_lr7e4 | 0.007114359 | 105.486 | 0.007114359 | 3437263 | 214.829 | 0.000000000319 | `frikan_h8u6l6_e1k_lr7e4.jsonl` |
| GRNu16_e1k_puremae | 0.002450907 | 149.730 | 0.002450907 | 3855245 | 240.952 | 0.000000001089 | `grnu16_e1k_puremae.jsonl` |
| LSTMTransformeru6_e1k_puremae | 0.005048725 | 142.756 | 0.005048725 | 4379025 | 273.689 | 0.000000000325 | `lstm_transformeru6_e1k_puremae.jsonl` |
| LSTMu16_e1k_puremae_r8 | 0.050702183 | 169.351 | 0.050702183 | 4487185 | 280.449 | 0.000000001107 | `lstm_u16_e1k_puremae_r8.jsonl` |
| 1DCNNc4u8k20l8_e1k_lr18e3_pd8l8_true | 0.000001751 | 80.799 | 0.000001751 | 4461635 | 278.853 | 0.000000007564 | `onedcnn_c4u8k20l8_e1k_lr18e3_pd8l8_true.jsonl` |
| TCNc4d1248k3_nopd_true_e1k_lr2e3 | 0.000001197 | 101.839 | 0.000001197 | 6155520 | 384.721 | 0.000000001906 | `tcnc4d1248k3_nopd_true_e1k_lr2e3.jsonl` |

## FRIKANh8u6l6_e1k_lr7e4

- QEMU: MAE=`0.007114359`, host ms/iter=`105.486`, unit=`seconds`
- Keil: MAE=`0.007114359`, cycles/iter=`3437263`, ms/iter=`214.829`, output_last=`-0.004541`
- Consistency: |Keil-QEMU| MAE delta=`0.000000000065`, HW-vs-QEMU waveform MAE=`0.000000000319`
- Artifacts: `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_103441_horizontal_reset_serial_raw\frikan_h8u6l6_e1k_lr7e4.jsonl`, `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_103441_horizontal_reset_serial_raw\frikan_h8u6l6_e1k_lr7e4.txt`

## GRNu16_e1k_puremae

- QEMU: MAE=`0.002450907`, host ms/iter=`149.730`, unit=`seconds`
- Keil: MAE=`0.002450907`, cycles/iter=`3855245`, ms/iter=`240.952`, output_last=`0.005916`
- Consistency: |Keil-QEMU| MAE delta=`0.000000000000`, HW-vs-QEMU waveform MAE=`0.000000001089`
- Artifacts: `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_103441_horizontal_reset_serial_raw\grnu16_e1k_puremae.jsonl`, `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_103441_horizontal_reset_serial_raw\grnu16_e1k_puremae.txt`

## LSTMTransformeru6_e1k_puremae

- QEMU: MAE=`0.005048725`, host ms/iter=`142.756`, unit=`seconds`
- Keil: MAE=`0.005048725`, cycles/iter=`4379025`, ms/iter=`273.689`, output_last=`-0.025312`
- Consistency: |Keil-QEMU| MAE delta=`0.000000000000`, HW-vs-QEMU waveform MAE=`0.000000000325`
- Artifacts: `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_103441_horizontal_reset_serial_raw\lstm_transformeru6_e1k_puremae.jsonl`, `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_103441_horizontal_reset_serial_raw\lstm_transformeru6_e1k_puremae.txt`

## LSTMu16_e1k_puremae_r8

- QEMU: MAE=`0.050702183`, host ms/iter=`169.351`, unit=`seconds`
- Keil: MAE=`0.050702183`, cycles/iter=`4487185`, ms/iter=`280.449`, output_last=`0.047210`
- Consistency: |Keil-QEMU| MAE delta=`0.000000000000`, HW-vs-QEMU waveform MAE=`0.000000001107`
- Artifacts: `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_103441_horizontal_reset_serial_raw\lstm_u16_e1k_puremae_r8.jsonl`, `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_103441_horizontal_reset_serial_raw\lstm_u16_e1k_puremae_r8.txt`

## 1DCNNc4u8k20l8_e1k_lr18e3_pd8l8_true

- QEMU: MAE=`0.000001751`, host ms/iter=`80.799`, unit=`seconds`
- Keil: MAE=`0.000001751`, cycles/iter=`4461635`, ms/iter=`278.853`, output_last=`-0.289342`
- Consistency: |Keil-QEMU| MAE delta=`0.000000000000`, HW-vs-QEMU waveform MAE=`0.000000007564`
- Artifacts: `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_103441_horizontal_reset_serial_raw\onedcnn_c4u8k20l8_e1k_lr18e3_pd8l8_true.jsonl`, `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_103441_horizontal_reset_serial_raw\onedcnn_c4u8k20l8_e1k_lr18e3_pd8l8_true.txt`

## TCNc4d1248k3_nopd_true_e1k_lr2e3

- QEMU: MAE=`0.000001197`, host ms/iter=`101.839`, unit=`seconds`
- Keil: MAE=`0.000001197`, cycles/iter=`6155520`, ms/iter=`384.721`, output_last=`-0.080303`
- Consistency: |Keil-QEMU| MAE delta=`0.000000000000`, HW-vs-QEMU waveform MAE=`0.000000001906`
- Artifacts: `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_103441_horizontal_reset_serial_raw\tcnc4d1248k3_nopd_true_e1k_lr2e3.jsonl`, `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_103441_horizontal_reset_serial_raw\tcnc4d1248k3_nopd_true_e1k_lr2e3.txt`
