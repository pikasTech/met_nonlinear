from copy import deepcopy
from pathlib import Path

from core.external_path_parser import ExternalPath


def _make_external_path(root: Path) -> ExternalPath:
    return ExternalPath(
        project_name='demo',
        task_type='qemu-c-inference',
        task_name='sample',
        full_path=root,
        config_path=root / 'config.json',
        output_path=root / 'data',
    )


def test_execute_qemu_inference_task_deepcopies_config(monkeypatch, tmp_path):
    import core.board_inference.entrypoints as entrypoints

    received = {}

    def fake_validate(config, task_type='qemu-c-inference'):
        received['validated_input'] = config
        received['task_type'] = task_type
        return deepcopy(config)

    def fake_runner(ep_path, config):
        received['ep_path'] = ep_path
        received['config'] = config
        config['mutated'] = True
        return True

    monkeypatch.setattr(entrypoints, 'validate_task_config', fake_validate)
    monkeypatch.setattr(entrypoints, '_resolve_model_type', lambda config: 'lstm')
    monkeypatch.setattr(entrypoints, 'get_native_qemu_executor', lambda model_type: fake_runner)

    ep_path = _make_external_path(tmp_path / 'demo')
    source_config = {'qemu_config': {'action': 'generate'}}

    assert entrypoints.execute_qemu_inference_task(ep_path, source_config) is True
    assert received['validated_input'] is source_config
    assert received['task_type'] == 'qemu-c-inference'
    assert received['ep_path'] == ep_path
    assert received['config'] is not source_config
    assert source_config == {'qemu_config': {'action': 'generate'}}


def test_execute_qemu_inference_keil_bench_task_forwards_overrides(monkeypatch, tmp_path):
    import core.board_inference.entrypoints as entrypoints

    received = {}

    monkeypatch.setattr(entrypoints, 'validate_task_config', lambda config, task_type='qemu-c-inference': deepcopy(config))
    monkeypatch.setattr(entrypoints, '_resolve_model_type', lambda config: 'lstm')

    def fake_runner(ep_path, config, keil_overrides=None):
        received['ep_path'] = ep_path
        received['config'] = config
        received['keil_overrides'] = keil_overrides
        return True

    monkeypatch.setattr(entrypoints, 'get_native_keil_bench_executor', lambda model_type: fake_runner)

    ep_path = _make_external_path(tmp_path / 'demo')
    source_config = {'keil_config': {'action': 'generate'}}
    source_overrides = {'probe_uid': 'ABC123'}

    assert entrypoints.execute_qemu_inference_keil_bench_task(
        ep_path,
        source_config,
        keil_overrides=source_overrides,
    ) is True
    assert received['ep_path'] == ep_path
    assert received['config'] is not source_config
    assert received['keil_overrides'] == source_overrides
    assert received['keil_overrides'] is not source_overrides


def test_execute_qemu_inference_task_returns_false_on_runner_error(monkeypatch, tmp_path):
    import core.board_inference.entrypoints as entrypoints

    monkeypatch.setattr(entrypoints, 'validate_task_config', lambda config, task_type='qemu-c-inference': deepcopy(config))
    monkeypatch.setattr(entrypoints, '_resolve_model_type', lambda config: 'lstm')
    monkeypatch.setattr(
        entrypoints,
        'get_native_qemu_executor',
        lambda model_type: lambda ep_path, config: (_ for _ in ()).throw(RuntimeError('boom')),
    )

    ep_path = _make_external_path(tmp_path / 'demo')

    assert entrypoints.execute_qemu_inference_task(ep_path, {'qemu_config': {'action': 'generate'}}) is False


def test_execute_qemu_inference_keil_bench_task_returns_false_on_runner_error(monkeypatch, tmp_path):
    import core.board_inference.entrypoints as entrypoints

    monkeypatch.setattr(entrypoints, 'validate_task_config', lambda config, task_type='qemu-c-inference': deepcopy(config))
    monkeypatch.setattr(entrypoints, '_resolve_model_type', lambda config: 'lstm')
    monkeypatch.setattr(
        entrypoints,
        'get_native_keil_bench_executor',
        lambda model_type: lambda ep_path, config, keil_overrides=None: (_ for _ in ()).throw(RuntimeError('boom')),
    )

    ep_path = _make_external_path(tmp_path / 'demo')

    assert entrypoints.execute_qemu_inference_keil_bench_task(
        ep_path,
        {'keil_config': {'action': 'generate'}},
        keil_overrides={'probe_uid': 'ABC123'},
    ) is False


def test_execute_qemu_inference_task_routes_frikan_to_native_impl(monkeypatch, tmp_path):
    import core.board_inference.entrypoints as entrypoints

    received = {}

    monkeypatch.setattr(entrypoints, 'validate_task_config', lambda config, task_type='qemu-c-inference': deepcopy(config))
    monkeypatch.setattr(entrypoints, '_resolve_model_type', lambda config: 'frikan')

    def fake_native(ep_path, config):
        received['ep_path'] = ep_path
        received['config'] = config
        return True

    monkeypatch.setattr(entrypoints, 'get_native_qemu_executor', lambda model_type: fake_native)

    ep_path = _make_external_path(tmp_path / 'demo')
    source_config = {'qemu_config': {'action': 'generate'}}

    assert entrypoints.execute_qemu_inference_task(ep_path, source_config) is True
    assert received['ep_path'] == ep_path
    assert received['config'] is not source_config


def test_execute_qemu_inference_keil_bench_task_routes_frikan_to_native_impl(monkeypatch, tmp_path):
    import core.board_inference.entrypoints as entrypoints

    received = {}

    monkeypatch.setattr(entrypoints, 'validate_task_config', lambda config, task_type='qemu-c-inference': deepcopy(config))
    monkeypatch.setattr(entrypoints, '_resolve_model_type', lambda config: 'frikan')

    def fake_native(ep_path, config, keil_overrides=None):
        received['ep_path'] = ep_path
        received['config'] = config
        received['keil_overrides'] = keil_overrides
        return True

    monkeypatch.setattr(entrypoints, 'get_native_keil_bench_executor', lambda model_type: fake_native)

    ep_path = _make_external_path(tmp_path / 'demo')
    source_config = {'keil_config': {'action': 'generate'}}
    source_overrides = {'probe_uid': 'ABC123'}

    assert entrypoints.execute_qemu_inference_keil_bench_task(
        ep_path,
        source_config,
        keil_overrides=source_overrides,
    ) is True
    assert received['ep_path'] == ep_path
    assert received['config'] is not source_config
    assert received['keil_overrides'] == source_overrides
    assert received['keil_overrides'] is not source_overrides


def test_execute_qemu_inference_task_returns_false_when_native_executor_missing(monkeypatch, tmp_path):
    import core.board_inference.entrypoints as entrypoints

    monkeypatch.setattr(entrypoints, 'validate_task_config', lambda config, task_type='qemu-c-inference': deepcopy(config))
    monkeypatch.setattr(entrypoints, '_resolve_model_type', lambda config: 'lstm')
    monkeypatch.setattr(entrypoints, 'get_native_qemu_executor', lambda model_type: None)

    ep_path = _make_external_path(tmp_path / 'demo')

    assert entrypoints.execute_qemu_inference_task(ep_path, {'qemu_config': {'action': 'generate'}}) is False
