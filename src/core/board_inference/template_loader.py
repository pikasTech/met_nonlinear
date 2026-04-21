# Legacy reference: src/core/lstm_qemu_ep_task.py last present in commit c44b43e36eeb4aa39abab42c20795c33fac3060f.
"""Template loading helpers for board inference."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping


TEMPLATE_ROOT = Path(__file__).resolve().parent / 'templates'


def load_template(relative_path: str) -> str:
    """Load a UTF-8 template stored under `board_inference/templates`."""

    template_path = TEMPLATE_ROOT / relative_path
    if not template_path.exists():
        raise FileNotFoundError(f'模板不存在: {template_path}')
    return template_path.read_text(encoding='utf-8')


def render_template(relative_path: str,
                    replacements: Mapping[str, object]) -> str:
    """Render a template via simple `{{name}}` placeholder replacement."""

    rendered = load_template(relative_path)
    for key, value in replacements.items():
        rendered = rendered.replace(f'{{{{{key}}}}}', str(value))
    return rendered
