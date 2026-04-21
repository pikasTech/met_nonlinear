# Legacy reference: src/core/lstm_qemu_ep_task.py last present in commit c44b43e36eeb4aa39abab42c20795c33fac3060f.
"""Shared datatypes for board inference execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from core.external_path_parser import ExternalPath


@dataclass(frozen=True)
class ExecutionRequest:
    """Immutable execution request used by board inference entrypoints."""

    ep_path: ExternalPath
    config: Dict[str, Any]


__all__ = ["ExecutionRequest"]
