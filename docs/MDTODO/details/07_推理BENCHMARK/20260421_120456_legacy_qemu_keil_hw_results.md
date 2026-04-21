# Legacy QEMU/Keil Results (2026-04-21 12:10:01)

- Models: 5
- Probe UID: `205536951525`; serial: `COM8` @ `115200`
- Program backend: `keil`
- Max |Keil MAE - QEMU MAE|: `0.000000000008`
- Max HW-vs-QEMU waveform MAE: `0.000000000676`

| Model | QEMU MAE | QEMU host ms/iter | Keil MAE | Keil cycles/iter | Keil ms/iter | HW vs QEMU MAE | Raw serial |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| FRIKANh8u6l6_nosym | 0.080590377 | 121.564 | 0.080590377 | 3215071 | 200.942 | 0.000000000676 | `frikan_h8u6l6_nosym.jsonl` |
| FRIKANh8u6l6_nosym_interp | 0.000038875 | 228.566 | 0.000038875 | 4373263 | 273.329 | 0.000000000178 | `frikan_h8u6l6_nosym_interp.jsonl` |
| GRNu16 | 0.004020738 | 156.019 | 0.004020738 | 6413513 | 38.176 | 0.000000000303 | `grnu16.jsonl` |
| LSTMTransformeru6_e1k_1 | 0.000781898 | 165.370 | 0.000781898 | 5936250 | 35.335 | 0.000000000169 | `lstm_transformeru6_e1k_1.jsonl` |
| LSTMu16_base | 0.000619659 | 185.180 | 0.000619659 | 7502121 | 44.656 | 0.000000000234 | `lstm_u16_base.jsonl` |