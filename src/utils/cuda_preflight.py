import logging
import os
import shutil
import subprocess
from typing import Dict, List


PREFERRED_GPU_NAMES = [
    'NVIDIA GeForce RTX 2080 Ti',
    'NVIDIA GeForce RTX 3090',
]


def prepare_tensorflow_runtime_env(logger: logging.Logger) -> None:
    """Normalize high-risk TensorFlow GPU env vars before importing TF."""
    if os.name == 'nt':
        allocator = os.environ.get('TF_GPU_ALLOCATOR')
        if allocator == 'cuda_malloc_async':
            logger.warning(
                'Native Windows default disables TF_GPU_ALLOCATOR=cuda_malloc_async '
                'for this process because it is a known crash-risk path in tf26. '
                'Falling back to TensorFlow default allocator.'
            )
            os.environ.pop('TF_GPU_ALLOCATOR', None)
            os.environ['METNL_TF_GPU_ALLOCATOR_SANITIZED'] = '1'

    if 'TF_FORCE_GPU_ALLOW_GROWTH' not in os.environ:
        os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
        logger.info('Defaulting TF_FORCE_GPU_ALLOW_GROWTH=true for safer native GPU startup')
    else:
        logger.info(
            'Respecting existing TF_FORCE_GPU_ALLOW_GROWTH=%s',
            os.environ['TF_FORCE_GPU_ALLOW_GROWTH'],
        )


def _parse_gpu_records(output: str) -> List[Dict[str, str]]:
    records: List[Dict[str, str]] = []
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = [part.strip() for part in line.split(',')]
        if len(parts) < 3:
            continue
        index, name, pci_bus_id = parts[0], parts[1], parts[2]
        if not index.isdigit():
            continue
        records.append({
            'index': index,
            'name': name,
            'pci_bus_id': pci_bus_id,
        })
    return records


def _gpu_priority(record: Dict[str, str]) -> tuple[int, int, str]:
    name = record['name']
    try:
        preferred_rank = PREFERRED_GPU_NAMES.index(name)
    except ValueError:
        preferred_rank = len(PREFERRED_GPU_NAMES)
    return preferred_rank, int(record['index']), name


def _ordered_gpu_indices(records: List[Dict[str, str]]) -> List[str]:
    return [record['index'] for record in sorted(records, key=_gpu_priority)]


def _parse_healthy_gpu_indices(output: str) -> List[str]:
    return [record['index'] for record in _parse_gpu_records(output)]


def prepare_cuda_visible_devices(logger: logging.Logger) -> None:
    if 'CUDA_VISIBLE_DEVICES' in os.environ:
        logger.info('Respecting existing CUDA_VISIBLE_DEVICES=%s', os.environ['CUDA_VISIBLE_DEVICES'])
        return

    nvidia_smi = shutil.which('nvidia-smi')
    if not nvidia_smi:
        logger.info('nvidia-smi not found, skipping CUDA preflight')
        return

    try:
        result = subprocess.run(
            [
                nvidia_smi,
                '--query-gpu=index,name,pci.bus_id',
                '--format=csv,noheader',
            ],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=10,
            check=False,
        )
    except Exception as exc:
        logger.warning('CUDA preflight skipped because nvidia-smi failed: %s', exc)
        return

    stdout = result.stdout or ''
    stderr = result.stderr or ''
    gpu_records = _parse_gpu_records(stdout)
    healthy_indices = [record['index'] for record in gpu_records]
    ordered_indices = _ordered_gpu_indices(gpu_records)
    gpu_lost_detected = 'GPU is lost' in stdout or 'GPU is lost' in stderr

    if gpu_lost_detected:
        os.environ['METNL_CUDA_LOST_GPU_DETECTED'] = '1'
        os.environ['METNL_CUDA_HEALTHY_GPU_INDICES'] = ','.join(healthy_indices)

    if gpu_lost_detected and healthy_indices:
        os.environ['CUDA_VISIBLE_DEVICES'] = ','.join(ordered_indices)
        logger.warning(
            'Detected lost NVIDIA GPU state; restricting CUDA_VISIBLE_DEVICES to healthy GPUs: %s',
            os.environ['CUDA_VISIBLE_DEVICES'],
        )
        return

    if gpu_lost_detected and not healthy_indices:
        os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
        logger.warning('Detected lost NVIDIA GPU state and no healthy GPU remained; forcing CPU mode')
        return

    if ordered_indices and ordered_indices != healthy_indices:
        os.environ['CUDA_VISIBLE_DEVICES'] = ','.join(ordered_indices)
        logger.info(
            'Reordered visible GPUs by preference %s -> CUDA_VISIBLE_DEVICES=%s',
            PREFERRED_GPU_NAMES,
            os.environ['CUDA_VISIBLE_DEVICES'],
        )
