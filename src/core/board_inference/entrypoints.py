"""Isolated board inference entrypoints.

These entrypoints mirror the legacy signatures but route entirely through the
native `board_inference.models` registry so the refactored path no longer
depends on `core.lstm_qemu_ep_task`.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from core.external_path_parser import ExternalPath

from .config import clone_config, validate_task_config
from .models import get_native_keil_bench_executor, get_native_qemu_executor
from .platforms import benchmark_common
from .registry import detect_model_type
from .types import ExecutionRequest


logger = logging.getLogger(__name__)


def build_execution_request(ep_path: ExternalPath, config: Dict[str, Any]) -> ExecutionRequest:
    """Build a validated immutable request envelope for the isolated entrypoints."""

    return ExecutionRequest(
        ep_path=ep_path,
        config=validate_task_config(config),
    )


def _resolve_model_type(config: Dict[str, Any]) -> str:
    model_project_name = str(config['model_project_name']).replace('\\', '/')
    model_dir = benchmark_common._resolve_model_project_dir(model_project_name)
    weights_json_path = benchmark_common._resolve_weights_json_path(model_dir, config.get('weights_file'))
    return detect_model_type(model_project_name, model_dir, weights_json_path)


def execute_qemu_inference_task(ep_path: ExternalPath, config: Dict[str, Any]) -> bool:
    """Execute the isolated qemu task entrypoint."""

    try:
        request = build_execution_request(ep_path, config)
        model_type = _resolve_model_type(request.config)
        native_executor = get_native_qemu_executor(model_type)
        if native_executor is None:
            raise ValueError(f'模型 {model_type} 尚未注册 native qemu 执行器')
        return bool(native_executor(request.ep_path, request.config))
    except ImportError as exc:
        logger.error('无法导入 QEMU C 推理模块: %s', exc)
        return False
    except Exception as exc:
        logger.exception('QEMU C 推理任务执行失败: %s', exc)
        return False


def execute_qemu_inference_keil_bench_task(ep_path: ExternalPath,
                                           config: Dict[str, Any],
                                           keil_overrides: Optional[Dict[str, Any]] = None) -> bool:
    """Execute the isolated keil-bench entrypoint."""

    try:
        request = build_execution_request(ep_path, config)
        model_type = _resolve_model_type(request.config)
        native_executor = get_native_keil_bench_executor(model_type)
        if native_executor is None:
            raise ValueError(f'模型 {model_type} 尚未注册 native keil 执行器')
        return bool(
            native_executor(
                request.ep_path,
                request.config,
                keil_overrides=clone_config(keil_overrides or {}),
            )
        )
    except ImportError as exc:
        logger.error('无法导入 QEMU C 推理 Keil bench 模块: %s', exc)
        return False
    except Exception as exc:
        logger.exception('QEMU C 推理 Keil bench 任务执行失败: %s', exc)
        return False
