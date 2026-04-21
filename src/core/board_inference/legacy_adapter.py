"""Thin adapter around the legacy `lstm_qemu_ep_task` module.

The refactor package uses this adapter during the isolation phase so new code
can be exercised without touching the existing production module.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict, Optional

from core.external_path_parser import ExternalPath


@lru_cache(maxsize=1)
def _load_legacy_module():
    import core.lstm_qemu_ep_task as legacy_module

    return legacy_module


def run_legacy_qemu_task(ep_path: ExternalPath, config: Dict[str, Any]) -> bool:
    """Run the legacy qemu-c-inference task implementation."""

    return bool(_load_legacy_module().execute_qemu_inference_task(ep_path, config))


def run_legacy_keil_bench_task(ep_path: ExternalPath,
                               config: Dict[str, Any],
                               keil_overrides: Optional[Dict[str, Any]] = None) -> bool:
    """Run the legacy qemu-c-inference keil-bench implementation."""

    return bool(
        _load_legacy_module().execute_qemu_inference_keil_bench_task(
            ep_path,
            config,
            keil_overrides=keil_overrides,
        )
    )
