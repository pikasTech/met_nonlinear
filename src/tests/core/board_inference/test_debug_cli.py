import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from core.board_inference.comparison import compare_directory_trees
from core.board_inference.debug_cli import _classify_comparison, compare_ep_outputs, create_parser
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


def test_compare_directory_trees_normalizes_run_roots(tmp_path):
    legacy_root = tmp_path / 'legacy'
    new_root = tmp_path / 'new'
    (legacy_root / 'data').mkdir(parents=True)
    (new_root / 'data').mkdir(parents=True)

    with open(legacy_root / 'data' / 'benchmark_summary.json', 'w', encoding='utf-8') as file_obj:
        json.dump(
            {
                'generated_project_dir': str(legacy_root / 'qemu_project'),
                'summary_path': str(legacy_root / 'data' / 'benchmark_summary.json'),
            },
            file_obj,
            ensure_ascii=False,
            indent=2,
        )

    with open(new_root / 'data' / 'benchmark_summary.json', 'w', encoding='utf-8') as file_obj:
        json.dump(
            {
                'generated_project_dir': str(new_root / 'qemu_project'),
                'summary_path': str(new_root / 'data' / 'benchmark_summary.json'),
            },
            file_obj,
            ensure_ascii=False,
            indent=2,
        )

    comparison = compare_directory_trees(legacy_root, new_root)

    assert comparison.matches is True


def test_compare_ep_outputs_writes_report(monkeypatch, tmp_path):
    import core.board_inference.debug_cli as debug_cli

    ep_root = tmp_path / 'ep'
    ep_root.mkdir(parents=True)
    config_path = ep_root / 'config.json'
    config_path.write_text(
        json.dumps(
            {
                'task_info': {'task_type': 'qemu-c-inference'},
                'generation_config': {'project_dir': 'qemu_project', 'overwrite': True},
                'qemu_config': {'action': 'build-run'},
            },
            ensure_ascii=False,
            indent=2,
        ) + '\n',
        encoding='utf-8',
    )
    original_ep_path = _make_external_path(ep_root)

    monkeypatch.setattr(debug_cli, '_parse_ep_path', lambda _: original_ep_path)

    def fake_legacy(run, config, flow, old_runner, keil_overrides=None):
        (run.root / 'data').mkdir(parents=True, exist_ok=True)
        with open(run.root / 'data' / 'summary.json', 'w', encoding='utf-8') as file_obj:
            json.dump({'generated_project_dir': str(run.root / 'qemu_project')}, file_obj)
        return True

    def fake_new(run, config, flow, keil_overrides=None):
        (run.root / 'data').mkdir(parents=True, exist_ok=True)
        with open(run.root / 'data' / 'summary.json', 'w', encoding='utf-8') as file_obj:
            json.dump({'generated_project_dir': str(run.root / 'qemu_project')}, file_obj)
        return True

    monkeypatch.setattr(debug_cli, '_run_legacy_execution', fake_legacy)
    monkeypatch.setattr(debug_cli, '_run_new_execution', fake_new)

    report = compare_ep_outputs('ignored-path', flow='qemu', mode='generate')

    assert report['matches'] is True
    assert report['behavior_matches'] is True
    assert report['classification'] == 'success_match'
    assert report['old_runner'] == 'cli'
    report_path = Path(report['compare_root']) / 'comparison_report.json'
    assert report_path.exists()


def test_compare_directory_trees_normalizes_wave_timestamps(tmp_path):
    legacy_root = tmp_path / 'legacy'
    new_root = tmp_path / 'new'
    (legacy_root / 'data').mkdir(parents=True)
    (new_root / 'data').mkdir(parents=True)

    legacy_metadata = {
        'global': {
            'standard': {
                'creation_date': '2026-04-21 13:15:32',
                'modified_date': '2026-04-21 13:15:32',
            }
        }
    }
    new_metadata = {
        'global': {
            'standard': {
                'creation_date': '2026-04-21 13:15:36',
                'modified_date': '2026-04-21 13:15:36',
            }
        }
    }

    with open(legacy_root / 'data' / 'sample.wave', 'wb') as file_obj:
        np.savez_compressed(
            file_obj,
            metadata=json.dumps(legacy_metadata, ensure_ascii=False),
            record_0=np.asarray([[1.0], [2.0]], dtype=np.float32),
        )
    with open(new_root / 'data' / 'sample.wave', 'wb') as file_obj:
        np.savez_compressed(
            file_obj,
            metadata=json.dumps(new_metadata, ensure_ascii=False),
            record_0=np.asarray([[1.0], [2.0]], dtype=np.float32),
        )

    comparison = compare_directory_trees(legacy_root, new_root)

    assert comparison.matches is True


def test_create_parser_supports_compare_command():
    parser = create_parser()

    args = parser.parse_args([
        'compare',
        'ex_projects/inference/qemu-c-inference/lstm_u16_base',
        '--flow',
        'keil',
        '--old-runner',
        'cli',
    ])

    assert args.command == 'compare'
    assert args.flow == 'keil'
    assert args.old_runner == 'cli'


def test_create_parser_compare_defaults_to_cli():
    parser = create_parser()

    args = parser.parse_args([
        'compare',
        'ex_projects/inference/qemu-c-inference/frikan_h8u6l6_e1k_lr7e4',
    ])

    assert args.command == 'compare'
    assert args.old_runner == 'cli'


def test_classify_comparison_reports_shared_failure():
    result = _classify_comparison(
        legacy_success=False,
        new_success=False,
        artifact_match=True,
    )

    assert result['classification'] == 'shared_failure'
    assert result['behavior_match'] is True
    assert result['strict_match'] is False


def test_run_legacy_cli_captures_subprocess_logs(tmp_path, monkeypatch):
    import core.board_inference.debug_cli as debug_cli

    run = SimpleNamespace(
        root=tmp_path / 'legacy_run',
        ep_path=SimpleNamespace(full_path=tmp_path / 'legacy_run'),
    )

    monkeypatch.setattr(debug_cli, 'REPO_ROOT', tmp_path)
    monkeypatch.setattr(debug_cli.sys, 'executable', 'python')

    def fake_subprocess_run(command, cwd, check, capture_output, text, encoding, errors):
        assert capture_output is True
        return SimpleNamespace(returncode=0, stdout='legacy stdout', stderr='legacy stderr')

    monkeypatch.setattr(debug_cli.subprocess, 'run', fake_subprocess_run)

    success = debug_cli._run_legacy_cli(run, flow='qemu')

    assert success is True
    assert (run.root / 'legacy_cli_stdout.log').read_text(encoding='utf-8') == 'legacy stdout'
    assert (run.root / 'legacy_cli_stderr.log').read_text(encoding='utf-8') == 'legacy stderr'
    process_payload = json.loads((run.root / 'legacy_cli_process.json').read_text(encoding='utf-8'))
    assert process_payload['return_code'] == 0
