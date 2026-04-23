import json
import subprocess
from pathlib import Path

import pytest

from core.board_inference.platforms import benchmark_common as common
from core.board_inference.platforms.benchmark_common import (
    ValidationArtifacts,
    ValidationRecord,
    _extract_validation_outputs,
    _normalize_keil_config,
    _run_serial_monitor_json_command,
    _run_keil_cli_json_command,
    _render_keil_project_with_optimization_profile,
    _wait_keil_job,
)


def _make_validation_artifacts(seq_len: int) -> ValidationArtifacts:
    return ValidationArtifacts(
        dataset_type='MET',
        full_data_path='data/M50',
        sample_rate=2000.0,
        time_window={'start_time_s': 0.0, 'end_time_s': 0.2},
        input_data_range=1.0,
        output_data_range=1.0,
        loaded_weights_path=Path('weights.json'),
        records=[
            ValidationRecord(
                record_id='record_0',
                magnitude=0.24,
                frequency=10.0,
                input_sequence=[[0.0] for _ in range(seq_len)],
                target_sequence=[0.0 for _ in range(seq_len)],
                tf_output_sequence=[0.0 for _ in range(seq_len)],
            )
        ],
    )


def test_extract_validation_outputs_ignores_trailing_matrix_tail():
    validation_artifacts = _make_validation_artifacts(seq_len=3)
    parsed_output = {
        'validation_record_0': '1.000000,2.000000,3.000000;0.000053;0.000058',
        'validation_complete': 1,
    }

    result = _extract_validation_outputs(parsed_output, validation_artifacts)

    assert result == [[1.0, 2.0, 3.0]]


def test_extract_validation_outputs_recovers_missing_commas_between_fixed6_values():
    validation_artifacts = _make_validation_artifacts(seq_len=3)
    parsed_output = {
        'validation_record_0': '1.0000002.000000,3.000000;0.000053',
        'validation_complete': 1,
    }

    result = _extract_validation_outputs(parsed_output, validation_artifacts)

    assert result == [[1.0, 2.0, 3.0]]


def test_normalize_keil_config_expands_optimization_profile_presets():
    config = _normalize_keil_config({
        'optimization_profiles': ['project_default', 'o0', 'o2', 'ofast_lto'],
        'published_optimization_profile': 'project_default',
    })

    assert [item['key'] for item in config['optimization_profiles']] == [
        'project_default',
        'o0',
        'o2',
        'ofast_lto',
    ]
    assert config['optimization_profiles'][1]['misc_controls'] == '-O0'
    assert config['optimization_profiles'][2]['optim_value'] == '2'
    assert config['optimization_profiles'][3]['enable_lto'] is True
    assert config['published_optimization_profile'] == 'project_default'


def test_render_keil_project_with_optimization_profile_updates_ac6_nodes(tmp_path):
    base_project = Path(
        'C:/work/met_nonlinear_master/src/tests/keil_projects/met_keil_405/MDK-ARM/Electrochemical geophone.uvprojx'
    ).read_text(encoding='utf-8')

    rendered = _render_keil_project_with_optimization_profile(
        base_project_text=base_project,
        profile={
            'key': 'ofast_lto',
            'label': '-Ofast + LTO',
            'use_project_defaults': False,
            'optim_value': '3',
            'misc_controls': '-Ofast',
            'enable_lto': True,
        },
        target_name='MET405',
    )

    assert '<Optim>3</Optim>' in rendered
    assert '<MiscControls>-Ofast</MiscControls>' in rendered
    assert '<v6Lto>1</v6Lto>' in rendered
    assert '<OutputDirectory>output\\MET405_ofast_lto\\</OutputDirectory>' in rendered


def test_run_keil_cli_json_command_accepts_failed_json_when_allowed(monkeypatch):
    def _fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=1,
            stdout='{"status":"failed","success":false,"result":{"message":"build failed"}}',
            stderr='',
        )

    monkeypatch.setattr(common.subprocess, 'run', _fake_run)

    result = _run_keil_cli_json_command(['py', '-3', 'keil-cli.py', 'job-status', 'job-1'], allow_failure=True)

    assert result['status'] == 'failed'
    assert result['success'] is False


def test_wait_keil_job_returns_failed_status_without_raising(monkeypatch):
    def _fake_run_keil_cli_json_command(command, allow_failure=False):
        assert allow_failure is True
        return {
            'job_id': 'job-1',
            'status': 'failed',
            'success': False,
            'result': {'message': 'build failed'},
        }

    monkeypatch.setattr(common, '_run_keil_cli_json_command', _fake_run_keil_cli_json_command)

    result = _wait_keil_job(Path('keil-cli.py'), 'job-1', 5)

    assert result['status'] == 'failed'
    assert result['success'] is False


def test_run_serial_monitor_json_command_accepts_multiline_progress_output(monkeypatch, tmp_path):
    def _fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout='\n'.join([
                '{"action":"server_start","status":"starting"}',
                '{"action":"server_start","status":"waiting"}',
                '{"action":"server_start","success":true,"data":{"port":3003}}',
            ]),
            stderr='',
        )

    monkeypatch.setattr(common.subprocess, 'run', _fake_run)

    result = _run_serial_monitor_json_command(['serial-monitor', 'server', 'start'], cwd=tmp_path)

    assert result['action'] == 'server_start'
    assert result['success'] is True
    assert result['data']['port'] == 3003
    assert result['_return_code'] == 0


def test_keil_benchmark_validates_capture_even_when_program_job_fails(tmp_path, monkeypatch):
    output_dir = tmp_path / 'data'
    generated_project_dir = tmp_path / 'qemu_project'
    keil_project_dir = tmp_path / 'keil_project'
    mdk_dir = keil_project_dir / 'MDK-ARM'
    mdk_dir.mkdir(parents=True)
    generated_project_dir.mkdir()
    (mdk_dir / common.KEIL_BENCHMARK_BASE_UVPROJX.name).write_text(
        '<Project></Project>',
        encoding='utf-8',
    )
    output_dir.mkdir()

    stream_text_path = output_dir / 'keil_serial_stream.txt'
    stream_text_path.write_text(
        '\n'.join([
            'iterations=1',
            'record_count=1',
            'seq_len=3',
            'wall_time_per_iter_ms=2.000000',
            'validation_record_0=0.100000,-0.100000,0.200000',
            'validation_complete=1',
        ]),
        encoding='utf-8',
    )
    jsonl_path = output_dir / 'keil_serial_raw.jsonl'
    jsonl_path.write_text('', encoding='utf-8')
    capture_result_path = output_dir / '.keil_capture' / 'keil_capture_result.json'
    capture_result_path.parent.mkdir()
    capture_result_path.write_text('{}', encoding='utf-8')

    class EpPath:
        output_path = output_dir

    monkeypatch.setattr(
        common,
        '_render_keil_project_with_optimization_profile',
        lambda **kwargs: kwargs['base_project_text'],
    )
    monkeypatch.setattr(common, '_run_keil_build_job', lambda **kwargs: {'success': True})
    monkeypatch.setattr(common, '_snapshot_keil_build_output', lambda **kwargs: None)
    monkeypatch.setattr(common, '_run_keil_program_job', lambda **kwargs: {'success': False, 'error': 'mock fail'})
    monkeypatch.setattr(common, '_start_keil_serial_capture', lambda **kwargs: {'started': True})
    monkeypatch.setattr(
        common,
        '_finish_keil_serial_capture',
        lambda *args, **kwargs: {
            'status': 'completed',
            'text_path': str(stream_text_path),
            'jsonl_path': str(jsonl_path),
            'result_path': str(capture_result_path),
        },
    )

    result = common.execute_keil_benchmark_pipeline(
        ep_path=EpPath(),
        task_info={},
        model_type='frikan',
        model_project_name='projects/mock',
        weights_json_path=Path('weights.json'),
        generated_project_dir=generated_project_dir,
        keil_project_dir=keil_project_dir,
        benchmark_config={'iterations': 1},
        validation_artifacts=_make_validation_artifacts(seq_len=3),
        validation_config={'wave_output': {'compress': False}},
        keil_config={
            'action': 'build-program-capture',
            'target': 'MET405',
            'serial_port': 'COM1',
            'baud_rate': 115200,
            'capture_timeout': 1,
            'success_markers': ['validation_complete=1'],
            'optimization_profiles': [
                {
                    'key': 'project_default',
                    'label': 'Project default',
                    'use_project_defaults': True,
                    'optim_value': None,
                    'misc_controls': '',
                    'enable_lto': False,
                }
            ],
            'published_optimization_profile': 'project_default',
        },
        wave_paths={},
    )

    assert result is True
    summary = json.loads((output_dir / 'keil_benchmark_summary.json').read_text(encoding='utf-8'))
    assert summary['status'] == 'completed_with_program_failure'
    assert summary['keil_program']['success'] is False
    assert summary['validation_status'] == 'completed'
    assert summary['comparison']['mae'] == pytest.approx(0.13333333333333333)
    assert summary['keil_speed_ms_per_point'] == pytest.approx(2.0 / 3.0)
    assert summary['keil_speed_points_per_second'] == pytest.approx(1500.0)
    assert summary['comparison_path'].endswith('keil_validation_comparison.json')
    assert summary['optimization_profiles'][0]['comparison']['mae'] == pytest.approx(0.13333333333333333)
    assert (output_dir / 'keil_validation_comparison.json').exists()
    assert (output_dir / 'waves' / 'keil_output.wave').exists()
