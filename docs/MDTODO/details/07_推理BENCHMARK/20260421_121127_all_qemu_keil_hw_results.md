# All QEMU/Keil Hardware Results (2026-04-21 12:11:27)

- Models: 11
- Probe UID: `205536951525`; serial: `COM8` @ `115200`
- All `validation_complete=1`: `True`
- Max |Keil MAE - QEMU MAE|: `0.000000000065`
- Max HW-vs-QEMU waveform MAE: `0.000000007564`
- All hardware outputs match QEMU closely: `True`

| Model | Family | QEMU MAE | QEMU host ms/iter | Keil MAE | Keil cycles/iter | Keil ms/iter | HW vs QEMU MAE |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1DCNNc4u8k20l8_e1k_lr18e3_pd8l8_true | 1DCNN | 0.000001751 | 80.799 | 0.000001751 | 4461635 | 278.853 | 0.000000007564 |
| FRIKANh8u6l6_e1k_lr7e4 | FRIKAN | 0.007114359 | 105.486 | 0.007114359 | 3437263 | 214.829 | 0.000000000319 |
| FRIKANh8u6l6_nosym | FRIKAN | 0.080590377 | 121.564 | 0.080590377 | 3215071 | 200.942 | 0.000000000676 |
| FRIKANh8u6l6_nosym_interp | FRIKAN | 0.000038875 | 228.566 | 0.000038875 | 4373263 | 273.329 | 0.000000000178 |
| GRNu16 | GRU | 0.004020738 | 156.019 | 0.004020738 | 6413513 | 38.176 | 0.000000000303 |
| GRNu16_e1k_puremae | GRU | 0.002450907 | 149.730 | 0.002450907 | 3855245 | 240.952 | 0.000000001089 |
| LSTMTransformeru6_e1k_1 | LSTMTransformer | 0.000781898 | 165.370 | 0.000781898 | 5936250 | 35.335 | 0.000000000169 |
| LSTMTransformeru6_e1k_puremae | LSTMTransformer | 0.005048725 | 142.756 | 0.005048725 | 4379025 | 273.689 | 0.000000000325 |
| LSTMu16_base | LSTM | 0.000619659 | 185.180 | 0.000619659 | 7502121 | 44.656 | 0.000000000234 |
| LSTMu16_e1k_puremae_r8 | LSTM | 0.050702183 | 169.351 | 0.050702183 | 4487185 | 280.449 | 0.000000001107 |
| TCNc4d1248k3_nopd_true_e1k_lr2e3 | TCN | 0.000001197 | 101.839 | 0.000001197 | 6155520 | 384.721 | 0.000000001906 |

## Source Reports

- `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_120456_legacy_qemu_keil_hw_results.json`
- `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_103441_horizontal_reset_qemu_keil_hw_results.json`

## 1DCNNc4u8k20l8_e1k_lr18e3_pd8l8_true

- QEMU: MAE=`0.000001751`, host ms/iter=`80.799`
- Keil: MAE=`0.000001751`, cycles/iter=`4461635`, ms/iter=`278.853`
- Consistency: |Keil-QEMU| MAE delta=`0.000000000000`, HW-vs-QEMU waveform MAE=`0.000000007564`
- Raw serial: `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_103441_horizontal_reset_serial_raw\onedcnn_c4u8k20l8_e1k_lr18e3_pd8l8_true.jsonl`

## FRIKANh8u6l6_e1k_lr7e4

- QEMU: MAE=`0.007114359`, host ms/iter=`105.486`
- Keil: MAE=`0.007114359`, cycles/iter=`3437263`, ms/iter=`214.829`
- Consistency: |Keil-QEMU| MAE delta=`0.000000000065`, HW-vs-QEMU waveform MAE=`0.000000000319`
- Raw serial: `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_103441_horizontal_reset_serial_raw\frikan_h8u6l6_e1k_lr7e4.jsonl`

## FRIKANh8u6l6_nosym

- QEMU: MAE=`0.080590377`, host ms/iter=`121.564`
- Keil: MAE=`0.080590377`, cycles/iter=`3215071`, ms/iter=`200.942`
- Consistency: |Keil-QEMU| MAE delta=`0.000000000003`, HW-vs-QEMU waveform MAE=`0.000000000676`
- Raw serial: `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_120456_legacy_qemu_keil_serial_raw\frikan_h8u6l6_nosym.jsonl`

## FRIKANh8u6l6_nosym_interp

- QEMU: MAE=`0.000038875`, host ms/iter=`228.566`
- Keil: MAE=`0.000038875`, cycles/iter=`4373263`, ms/iter=`273.329`
- Consistency: |Keil-QEMU| MAE delta=`0.000000000008`, HW-vs-QEMU waveform MAE=`0.000000000178`
- Raw serial: `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_120456_legacy_qemu_keil_serial_raw\frikan_h8u6l6_nosym_interp.jsonl`

## GRNu16

- QEMU: MAE=`0.004020738`, host ms/iter=`156.019`
- Keil: MAE=`0.004020738`, cycles/iter=`6413513`, ms/iter=`38.176`
- Consistency: |Keil-QEMU| MAE delta=`0.000000000000`, HW-vs-QEMU waveform MAE=`0.000000000303`
- Raw serial: `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_120456_legacy_qemu_keil_serial_raw\grnu16.jsonl`

## GRNu16_e1k_puremae

- QEMU: MAE=`0.002450907`, host ms/iter=`149.730`
- Keil: MAE=`0.002450907`, cycles/iter=`3855245`, ms/iter=`240.952`
- Consistency: |Keil-QEMU| MAE delta=`0.000000000000`, HW-vs-QEMU waveform MAE=`0.000000001089`
- Raw serial: `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_103441_horizontal_reset_serial_raw\grnu16_e1k_puremae.jsonl`

## LSTMTransformeru6_e1k_1

- QEMU: MAE=`0.000781898`, host ms/iter=`165.370`
- Keil: MAE=`0.000781898`, cycles/iter=`5936250`, ms/iter=`35.335`
- Consistency: |Keil-QEMU| MAE delta=`0.000000000000`, HW-vs-QEMU waveform MAE=`0.000000000169`
- Raw serial: `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_120456_legacy_qemu_keil_serial_raw\lstm_transformeru6_e1k_1.jsonl`

## LSTMTransformeru6_e1k_puremae

- QEMU: MAE=`0.005048725`, host ms/iter=`142.756`
- Keil: MAE=`0.005048725`, cycles/iter=`4379025`, ms/iter=`273.689`
- Consistency: |Keil-QEMU| MAE delta=`0.000000000000`, HW-vs-QEMU waveform MAE=`0.000000000325`
- Raw serial: `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_103441_horizontal_reset_serial_raw\lstm_transformeru6_e1k_puremae.jsonl`

## LSTMu16_base

- QEMU: MAE=`0.000619659`, host ms/iter=`185.180`
- Keil: MAE=`0.000619659`, cycles/iter=`7502121`, ms/iter=`44.656`
- Consistency: |Keil-QEMU| MAE delta=`0.000000000000`, HW-vs-QEMU waveform MAE=`0.000000000234`
- Raw serial: `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_120456_legacy_qemu_keil_serial_raw\lstm_u16_base.jsonl`

## LSTMu16_e1k_puremae_r8

- QEMU: MAE=`0.050702183`, host ms/iter=`169.351`
- Keil: MAE=`0.050702183`, cycles/iter=`4487185`, ms/iter=`280.449`
- Consistency: |Keil-QEMU| MAE delta=`0.000000000000`, HW-vs-QEMU waveform MAE=`0.000000001107`
- Raw serial: `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_103441_horizontal_reset_serial_raw\lstm_u16_e1k_puremae_r8.jsonl`

## TCNc4d1248k3_nopd_true_e1k_lr2e3

- QEMU: MAE=`0.000001197`, host ms/iter=`101.839`
- Keil: MAE=`0.000001197`, cycles/iter=`6155520`, ms/iter=`384.721`
- Consistency: |Keil-QEMU| MAE delta=`0.000000000000`, HW-vs-QEMU waveform MAE=`0.000000001906`
- Raw serial: `C:\work\met_nonlinear_master\docs\MDTODO\details\07_推理BENCHMARK\20260421_103441_horizontal_reset_serial_raw\tcnc4d1248k3_nopd_true_e1k_lr2e3.jsonl`
