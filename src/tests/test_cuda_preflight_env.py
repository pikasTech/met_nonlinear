import logging

from utils import cuda_preflight


def test_prepare_tensorflow_runtime_env_sanitizes_cuda_malloc_async_on_windows(monkeypatch):
    logger = logging.getLogger('test_cuda_preflight_env')

    monkeypatch.setattr(cuda_preflight.os, 'name', 'nt')
    monkeypatch.setenv('TF_GPU_ALLOCATOR', 'cuda_malloc_async')
    monkeypatch.delenv('TF_FORCE_GPU_ALLOW_GROWTH', raising=False)
    monkeypatch.delenv('METNL_TF_GPU_ALLOCATOR_SANITIZED', raising=False)

    cuda_preflight.prepare_tensorflow_runtime_env(logger)

    assert 'TF_GPU_ALLOCATOR' not in cuda_preflight.os.environ
    assert cuda_preflight.os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] == 'true'
    assert cuda_preflight.os.environ['METNL_TF_GPU_ALLOCATOR_SANITIZED'] == '1'


def test_prepare_tensorflow_runtime_env_respects_existing_growth_setting(monkeypatch):
    logger = logging.getLogger('test_cuda_preflight_env')

    monkeypatch.setattr(cuda_preflight.os, 'name', 'nt')
    monkeypatch.delenv('TF_GPU_ALLOCATOR', raising=False)
    monkeypatch.setenv('TF_FORCE_GPU_ALLOW_GROWTH', 'false')

    cuda_preflight.prepare_tensorflow_runtime_env(logger)

    assert cuda_preflight.os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] == 'false'
