# Legacy reference: src/core/lstm_qemu_ep_task.py last present in commit c44b43e36eeb4aa39abab42c20795c33fac3060f.
"""Config helpers for board inference execution."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict


def clone_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Deep-copy a task config so downstream execution cannot mutate caller state."""

    if not isinstance(config, dict):
        raise TypeError(f'config must be a dict, got {type(config)!r}')
    return deepcopy(config)


def validate_task_config(config: Dict[str, Any],
                         task_type: str = "qemu-c-inference") -> Dict[str, Any]:
    """Validate an EP config with the same validator used by the CLI."""

    from core.config_validator import validate_visualization_config_data

    return validate_visualization_config_data(clone_config(config), task_type)


__all__ = [
    "clone_config",
    "validate_task_config",
]
