# board_inference templates

Stable board-inference C/H templates now live here and are loaded by the
native Python renderers instead of staying embedded in `sequence.py` /
`frikan.py`.

Current extracted templates:

- `models/lstm_main_template.c`
- `models/grn_main_template.c`
- `models/lstm_transformer_main_template.c`
- `models/frikan_main_template.c`
- `models/generic_conv_main_template.c`
- `models/lstm_model_data_template.h`
- `models/grn_model_data_template.h`
- `models/lstm_transformer_model_data_template.h`
- `models/wavenet_model_data_template.h`
- `models/conv_stack_model_data_template.h`
- `models/tcn_model_data_template.h`
- `models/frikan_model_data_template.h`

Python now mainly keeps numeric initializer generation, topology-dependent
declaration assembly, and model-specific control-flow code.
