"""Experimental board inference refactor package.

This package is intentionally not wired into the main CLI yet. It provides
isolated entrypoints and debugging utilities so the refactor can be validated
against the legacy implementation before any production cut-over.
"""

from .entrypoints import (
    execute_qemu_inference_keil_bench_task,
    execute_qemu_inference_task,
)

__all__ = [
    'execute_qemu_inference_keil_bench_task',
    'execute_qemu_inference_task',
]
