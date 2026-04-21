from __future__ import annotations

import json

from core.board_inference.comparison import compare_directory_trees


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as file_obj:
        json.dump(payload, file_obj, indent=2, ensure_ascii=False)
        file_obj.write('\n')


def test_compare_directory_trees_ignores_host_elapsed_noise(tmp_path):
    left_root = tmp_path / 'left'
    right_root = tmp_path / 'right'

    left_payload = {
        'build': {'build': {'elapsed_seconds': 1.25}},
        'runs': [
            {
                'workflow': {'run': {'elapsed_seconds': 0.91}},
                'parsed_output': {
                    'timer_source': 'host_elapsed',
                    'measurement_total': 0.91,
                    'measurement_per_iter': 0.091,
                },
            },
        ],
        'aggregated': {
            'measurement_sources': ['host_elapsed'],
            'avg_host_elapsed_seconds': 0.91,
            'avg_measurement_per_iter': 0.091,
        },
        'validation_run': {
            'workflow': {'elapsed_seconds': 2.2},
            'parsed_output': {
                'timer_source': 'host_elapsed',
                'measurement_total': 2.2,
                'measurement_per_iter': 0.22,
            },
        },
    }
    right_payload = {
        'build': {'build': {'elapsed_seconds': 1.61}},
        'runs': [
            {
                'workflow': {'run': {'elapsed_seconds': 0.99}},
                'parsed_output': {
                    'timer_source': 'host_elapsed',
                    'measurement_total': 0.99,
                    'measurement_per_iter': 0.099,
                },
            },
        ],
        'aggregated': {
            'measurement_sources': ['host_elapsed'],
            'avg_host_elapsed_seconds': 0.99,
            'avg_measurement_per_iter': 0.099,
        },
        'validation_run': {
            'workflow': {'elapsed_seconds': 2.6},
            'parsed_output': {
                'timer_source': 'host_elapsed',
                'measurement_total': 2.6,
                'measurement_per_iter': 0.26,
            },
        },
    }

    _write_json(left_root / 'data' / 'benchmark_summary.json', left_payload)
    _write_json(right_root / 'data' / 'benchmark_summary.json', right_payload)

    comparison = compare_directory_trees(left_root, right_root)

    assert comparison.matches is True


def test_compare_directory_trees_keeps_non_host_measurements_strict(tmp_path):
    left_root = tmp_path / 'left'
    right_root = tmp_path / 'right'

    left_payload = {
        'runs': [
            {
                'parsed_output': {
                    'timer_source': 'dwt_cycles',
                    'measurement_total': 12345,
                },
            },
        ],
    }
    right_payload = {
        'runs': [
            {
                'parsed_output': {
                    'timer_source': 'dwt_cycles',
                    'measurement_total': 12346,
                },
            },
        ],
    }

    _write_json(left_root / 'data' / 'benchmark_summary.json', left_payload)
    _write_json(right_root / 'data' / 'benchmark_summary.json', right_payload)

    comparison = compare_directory_trees(left_root, right_root)

    assert comparison.matches is False
    assert comparison.differing_files[0].path == 'data/benchmark_summary.json'


def test_compare_directory_trees_normalizes_jsonl_timestamps(tmp_path):
    left_root = tmp_path / 'left'
    right_root = tmp_path / 'right'
    left_path = left_root / 'data' / 'keil_serial_raw.jsonl'
    right_path = right_root / 'data' / 'keil_serial_raw.jsonl'
    left_path.parent.mkdir(parents=True, exist_ok=True)
    right_path.parent.mkdir(parents=True, exist_ok=True)

    left_path.write_text(
        '{"timestamp":"2026-04-21T12:00:00.000+08:00","port":"COM8","data":"hello"}\n',
        encoding='utf-8',
    )
    right_path.write_text(
        '{"timestamp":"2026-04-21T12:00:01.000+08:00","port":"COM8","data":"hello"}\n',
        encoding='utf-8',
    )

    comparison = compare_directory_trees(left_root, right_root)

    assert comparison.matches is True


def test_compare_directory_trees_ignores_keil_output_noise(tmp_path):
    left_root = tmp_path / 'left'
    right_root = tmp_path / 'right'
    (left_root / 'keil_project' / 'MDK-ARM' / 'output' / 'MET405').mkdir(parents=True)
    (right_root / 'keil_project' / 'MDK-ARM' / 'output' / 'MET405').mkdir(parents=True)

    (left_root / 'keil_project' / 'MDK-ARM' / 'output' / 'MET405' / 'MET405_BENCHMARK.axf').write_bytes(b'left')
    (right_root / 'keil_project' / 'MDK-ARM' / 'output' / 'MET405' / 'MET405_BENCHMARK.axf').write_bytes(b'right')

    comparison = compare_directory_trees(left_root, right_root)

    assert comparison.matches is True


def test_compare_directory_trees_compares_keil_stream_semantically(tmp_path):
    left_root = tmp_path / 'left'
    right_root = tmp_path / 'right'
    left_path = left_root / 'data' / 'keil_serial_stream.txt'
    right_path = right_root / 'data' / 'keil_serial_stream.txt'
    left_path.parent.mkdir(parents=True, exist_ok=True)
    right_path.parent.mkdir(parents=True, exist_ok=True)

    left_path.write_text(
        '[boot] noiseFRIKAN_BENCHMARK_VALIDATIONiterations=10output=1validation_complete=1tail',
        encoding='utf-8',
    )
    right_path.write_text(
        '[boot] differentFRIKAN_BENCHMARK_VALIDATIONiterations=10output=1validation_complete=1other',
        encoding='utf-8',
    )

    comparison = compare_directory_trees(left_root, right_root)

    assert comparison.matches is True


def test_compare_directory_trees_ignores_noisy_keil_marker_preamble(tmp_path):
    left_root = tmp_path / 'left'
    right_root = tmp_path / 'right'
    left_path = left_root / 'data' / 'keil_serial_raw.jsonl'
    right_path = right_root / 'data' / 'keil_serial_raw.jsonl'
    left_path.parent.mkdir(parents=True, exist_ok=True)
    right_path.parent.mkdir(parents=True, exist_ok=True)

    noisy_left = (
        '{"data":"TCN_BENCHMARK_VALIDATION[boot]noise"}\n'
        '{"data":"TCN_BENCHMARK_VALIDATIONiterations=10output=1validation_complete=1"}\n'
    )
    noisy_right = (
        '{"data":"TCN_BENCHMARK_VALIDATION[other]noise"}\n'
        '{"data":"TCN_BENCHMARK_VALIDATIONiterations=10output=1validation_complete=1"}\n'
    )
    left_path.write_text(noisy_left, encoding='utf-8')
    right_path.write_text(noisy_right, encoding='utf-8')

    comparison = compare_directory_trees(left_root, right_root)

    assert comparison.matches is True


def test_compare_directory_trees_ignores_legacy_cli_capture_artifacts(tmp_path):
    left_root = tmp_path / 'left'
    right_root = tmp_path / 'right'
    left_root.mkdir(parents=True)
    right_root.mkdir(parents=True)

    (left_root / 'legacy_cli_stdout.log').write_text('legacy stdout', encoding='utf-8')
    (left_root / 'legacy_cli_stderr.log').write_text('legacy stderr', encoding='utf-8')
    _write_json(left_root / 'legacy_cli_process.json', {'return_code': 0})

    comparison = compare_directory_trees(left_root, right_root)

    assert comparison.matches is True


def test_compare_directory_trees_normalizes_keil_summary_runtime_metadata(tmp_path):
    left_root = tmp_path / 'left'
    right_root = tmp_path / 'right'

    left_payload = {
        'keil_build': {
            'created_at': '2026-04-21T17:31:01.876236',
            'started_at': '2026-04-21T17:31:02.256992',
            'finished_at': '2026-04-21T17:31:55.803251',
            'log_file': r'C:\Users\lyon\.agents\skills\keil\logs\20260421\keil_build_20260421_173102.jsonl',
            'state_file': r'C:\Users\lyon\.agents\skills\keil\.state\jobs\20260421_173101_10a94ca3.json',
        },
        'keil_program': {
            'created_at': '2026-04-21T17:32:00.985397',
            'started_at': '2026-04-21T17:32:01.363160',
            'finished_at': '2026-04-21T17:32:18.478745',
            'log_file': r'C:\Users\lyon\.agents\skills\keil\logs\20260421\keil_program_20260421_173201.jsonl',
            'state_file': r'C:\Users\lyon\.agents\skills\keil\.state\jobs\20260421_173200_ffac8661.json',
            'result': {
                '_log_file': r'C:\Users\lyon\.agents\skills\keil\logs\20260421\keil_program_20260421_173201.jsonl',
                'log_excerpt': 'Flash Load finished at 17:32:18',
            },
        },
        'serial_capture': {
            'stream_length': 4378,
            'record_count': 25,
            'fetch_result': {
                'data': {
                    'count': 1937,
                    'totalCount': 1937,
                    'timeRange': {
                        'end': '2026-04-21T17:32:21.404+0800',
                    },
                },
            },
        },
    }
    right_payload = {
        'keil_build': {
            'created_at': '2026-04-21T17:32:32.609355',
            'started_at': '2026-04-21T17:32:33.049346',
            'finished_at': '2026-04-21T17:32:45.872107',
            'log_file': r'C:\Users\lyon\.agents\skills\keil\logs\20260421\keil_build_20260421_173233.jsonl',
            'state_file': r'C:\Users\lyon\.agents\skills\keil\.state\jobs\20260421_173232_35a514b7.json',
        },
        'keil_program': {
            'created_at': '2026-04-21T17:32:51.754729',
            'started_at': '2026-04-21T17:32:52.138699',
            'finished_at': '2026-04-21T17:33:25.826735',
            'log_file': r'C:\Users\lyon\.agents\skills\keil\logs\20260421\keil_program_20260421_173252.jsonl',
            'state_file': r'C:\Users\lyon\.agents\skills\keil\.state\jobs\20260421_173251_4bd5316a.json',
            'result': {
                '_log_file': r'C:\Users\lyon\.agents\skills\keil\logs\20260421\keil_program_20260421_173252.jsonl',
                'log_excerpt': 'Flash Load finished at 17:33:25',
            },
        },
        'serial_capture': {
            'stream_length': 4379,
            'record_count': 24,
            'fetch_result': {
                'data': {
                    'count': 1966,
                    'totalCount': 1966,
                    'timeRange': {
                        'end': '2026-04-21T17:33:28.534+0800',
                    },
                },
            },
        },
    }

    _write_json(left_root / 'data' / 'keil_benchmark_summary.json', left_payload)
    _write_json(right_root / 'data' / 'keil_benchmark_summary.json', right_payload)

    comparison = compare_directory_trees(left_root, right_root)

    assert comparison.matches is True
