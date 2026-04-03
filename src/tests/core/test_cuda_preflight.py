import logging
import os
import subprocess

from utils import cuda_preflight


def _clear_preflight_env(monkeypatch):
    monkeypatch.delenv('CUDA_VISIBLE_DEVICES', raising=False)
    monkeypatch.delenv('METNL_CUDA_LOST_GPU_DETECTED', raising=False)
    monkeypatch.delenv('METNL_CUDA_HEALTHY_GPU_INDICES', raising=False)


def test_parse_healthy_gpu_indices_extracts_numeric_indices():
    output = '0, NVIDIA GeForce RTX 3090, 00000000:01:00.0\n1, NVIDIA GeForce RTX 2080 Ti, 00000000:07:00.0\n'

    assert cuda_preflight._parse_healthy_gpu_indices(output) == ['0', '1']


def test_ordered_gpu_indices_prefers_2080ti_over_3090():
    records = cuda_preflight._parse_gpu_records(
        '0, NVIDIA GeForce RTX 3090, 00000000:01:00.0\n'
        '1, NVIDIA GeForce RTX 2080 Ti, 00000000:07:00.0\n'
    )

    assert cuda_preflight._ordered_gpu_indices(records) == ['1', '0']


def test_prepare_cuda_visible_devices_respects_existing_env(monkeypatch):
    monkeypatch.setenv('CUDA_VISIBLE_DEVICES', '1')

    def fail_run(*args, **kwargs):
        raise AssertionError('subprocess.run should not be called when env is already set')

    monkeypatch.setattr(cuda_preflight.shutil, 'which', lambda name: 'nvidia-smi')
    monkeypatch.setattr(cuda_preflight.subprocess, 'run', fail_run)

    cuda_preflight.prepare_cuda_visible_devices(logging.getLogger('test'))

    assert os.environ['CUDA_VISIBLE_DEVICES'] == '1'


def test_prepare_cuda_visible_devices_filters_lost_gpu(monkeypatch):
    _clear_preflight_env(monkeypatch)
    monkeypatch.setattr(cuda_preflight.shutil, 'which', lambda name: 'nvidia-smi')

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout='1, NVIDIA GeForce RTX 2080 Ti, 00000000:07:00.0\n',
            stderr='Unable to determine the device handle for GPU0: 0000:01:00.0: GPU is lost. Reboot the system to recover this GPU\n',
        )

    monkeypatch.setattr(cuda_preflight.subprocess, 'run', fake_run)

    cuda_preflight.prepare_cuda_visible_devices(logging.getLogger('test'))

    assert os.environ['CUDA_VISIBLE_DEVICES'] == '1'


def test_prepare_cuda_visible_devices_forces_cpu_when_all_gpus_lost(monkeypatch):
    _clear_preflight_env(monkeypatch)
    monkeypatch.setattr(cuda_preflight.shutil, 'which', lambda name: 'nvidia-smi')

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout='',
            stderr='Unable to determine the device handle for GPU0: 0000:01:00.0: GPU is lost. Reboot the system to recover this GPU\n',
        )

    monkeypatch.setattr(cuda_preflight.subprocess, 'run', fake_run)

    cuda_preflight.prepare_cuda_visible_devices(logging.getLogger('test'))

    assert os.environ['CUDA_VISIBLE_DEVICES'] == '-1'


def test_prepare_cuda_visible_devices_reorders_healthy_multi_gpu(monkeypatch):
    _clear_preflight_env(monkeypatch)
    monkeypatch.setattr(cuda_preflight.shutil, 'which', lambda name: 'nvidia-smi')

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout=(
                '0, NVIDIA GeForce RTX 3090, 00000000:01:00.0\n'
                '1, NVIDIA GeForce RTX 2080 Ti, 00000000:07:00.0\n'
            ),
            stderr='',
        )

    monkeypatch.setattr(cuda_preflight.subprocess, 'run', fake_run)

    cuda_preflight.prepare_cuda_visible_devices(logging.getLogger('test'))

    assert os.environ['CUDA_VISIBLE_DEVICES'] == '1,0'
