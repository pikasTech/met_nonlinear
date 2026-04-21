"""Config helpers for the isolated board inference refactor."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Dict, Literal, Optional


FlowKind = Literal['qemu', 'keil']
ModeKind = Literal['generate', 'configured']


def clone_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Deep-copy a task config so debug runs cannot mutate caller state."""

    if not isinstance(config, dict):
        raise TypeError(f'config must be a dict, got {type(config)!r}')
    return deepcopy(config)


def validate_task_config(config: Dict[str, Any],
                         task_type: str = 'qemu-c-inference') -> Dict[str, Any]:
    """Validate an EP config with the same validator used by the legacy CLI."""

    from core.config_validator import validate_visualization_config_data

    return validate_visualization_config_data(clone_config(config), task_type)


def load_task_config(config_path: Path) -> Dict[str, Any]:
    """Load an EP config file as UTF-8 JSON."""

    with open(config_path, 'r', encoding='utf-8') as file_obj:
        return json.load(file_obj)


def write_task_config(config_path: Path, config: Dict[str, Any]) -> None:
    """Write an EP config file as UTF-8 JSON."""

    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w', encoding='utf-8') as file_obj:
        json.dump(config, file_obj, indent=2, ensure_ascii=False)
        file_obj.write('\n')


def merge_non_empty_overrides(base: Optional[Dict[str, Any]],
                              overrides: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge CLI-style overrides while ignoring empty values."""

    merged: Dict[str, Any] = dict(base or {})
    for key, value in (overrides or {}).items():
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        merged[key] = value
    return merged


def prepare_debug_config(config: Dict[str, Any],
                         flow: FlowKind,
                         mode: ModeKind = 'generate',
                         keil_overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Clone and prepare config for isolated debug runs.

    `generate` mode forces artifact-generation only so the debug CLI can compare
    deterministic outputs without requiring QEMU/Keil toolchains.
    """

    prepared = clone_config(config)
    generation_config = prepared.setdefault('generation_config', {})
    generation_config.setdefault('overwrite', True)

    if mode == 'generate':
        if flow == 'qemu':
            prepared.setdefault('qemu_config', {})['action'] = 'generate'
        elif flow == 'keil':
            prepared.setdefault('keil_config', {})['action'] = 'generate'
        else:
            raise ValueError(f'Unsupported debug flow: {flow}')
    elif mode != 'configured':
        raise ValueError(f'Unsupported debug mode: {mode}')

    if flow == 'keil':
        prepared['keil_config'] = merge_non_empty_overrides(prepared.get('keil_config'), keil_overrides)

    return prepared
