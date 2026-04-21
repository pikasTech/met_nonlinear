# Legacy reference: src/core/lstm_qemu_ep_task.py last present in commit c44b43e36eeb4aa39abab42c20795c33fac3060f.
"""Board inference package for qemu-c-inference production execution."""

from .entrypoints import (
    execute_qemu_inference_keil_bench_task,
    execute_qemu_inference_task,
)

__all__ = [
    "execute_qemu_inference_keil_bench_task",
    "execute_qemu_inference_task",
]
