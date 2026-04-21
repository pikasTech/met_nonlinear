"""Standalone debug CLI entrypoint.

This script intentionally stays separate from `cli.py` so the refactored board
inference package can be exercised without touching the production CLI flow.
"""

import io
import os
import sys

os.system('chcp 65001 > nul')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.join(_SCRIPT_DIR, 'src')
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from core.board_inference.debug_cli import main


if __name__ == '__main__':
    raise SystemExit(main())
