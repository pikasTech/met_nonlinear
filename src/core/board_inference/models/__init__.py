"""Model-specific board inference implementations.

The refactor keeps model-specific execution behind registries so new native
implementations can be added without editing the shared entrypoints again.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from core.external_path_parser import ExternalPath

from .frikan import execute_frikan_keil_bench_task, execute_frikan_qemu_task
from .sequence import (
    SUPPORTED_SEQUENCE_MODEL_TYPES,
    execute_sequence_keil_bench_task,
    execute_sequence_qemu_task,
)


NativeQemuExecutor = Callable[[ExternalPath, Dict[str, Any]], bool]
NativeKeilBenchExecutor = Callable[[ExternalPath, Dict[str, Any], Optional[Dict[str, Any]]], bool]


NATIVE_QEMU_EXECUTORS: Dict[str, NativeQemuExecutor] = {
    'frikan': execute_frikan_qemu_task,
    **{
        model_type: execute_sequence_qemu_task
        for model_type in SUPPORTED_SEQUENCE_MODEL_TYPES
    },
}

NATIVE_KEIL_BENCH_EXECUTORS: Dict[str, NativeKeilBenchExecutor] = {
    'frikan': execute_frikan_keil_bench_task,
    **{
        model_type: execute_sequence_keil_bench_task
        for model_type in SUPPORTED_SEQUENCE_MODEL_TYPES
    },
}

NATIVE_MODEL_TYPES = frozenset(NATIVE_QEMU_EXECUTORS) | frozenset(NATIVE_KEIL_BENCH_EXECUTORS)


def get_native_qemu_executor(model_type: str) -> Optional[NativeQemuExecutor]:
    return NATIVE_QEMU_EXECUTORS.get(model_type)


def get_native_keil_bench_executor(model_type: str) -> Optional[NativeKeilBenchExecutor]:
    return NATIVE_KEIL_BENCH_EXECUTORS.get(model_type)


__all__ = [
    'NATIVE_KEIL_BENCH_EXECUTORS',
    'NATIVE_MODEL_TYPES',
    'NATIVE_QEMU_EXECUTORS',
    'NativeKeilBenchExecutor',
    'NativeQemuExecutor',
    'execute_frikan_keil_bench_task',
    'execute_frikan_qemu_task',
    'execute_sequence_keil_bench_task',
    'execute_sequence_qemu_task',
    'get_native_keil_bench_executor',
    'get_native_qemu_executor',
]
