# board_inference templates

This directory is reserved for the staged extraction of stable text templates
from `src/core/lstm_qemu_ep_task.py`.

Current phase:

- keep the legacy production module untouched
- build the new package skeleton and `debug_cli`
- validate legacy/new behavior in isolation before migrating `.c/.h/.xml/.ps1`
  template bodies here
