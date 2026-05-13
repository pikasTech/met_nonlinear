from __future__ import annotations
import json

from visualization.ablation_study import AblationStudyAnalyzer


def _write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def test_run_analysis_keeps_missing_metric_details_as_errors(tmp_path):
    full_project = tmp_path / 'full_project'
    missing_project = tmp_path / 'missing_project'

    _write_json(
        full_project / 'config.json',
        {
            'epoch_train': 1000,
            'learning_rate': 7e-4,
        },
    )
    _write_json(
        full_project / 'data' / 'metrics.json',
        {
            'val_mae': 0.1,
            'val_afmae': 0.2,
            'compute_cost': 123.0,
            'compute_details': {'weighted_total': 123.0},
            'metric_details': {
                'natural_frequency_drift': {
                    'drift': 1.0,
                    'min': 1.0,
                    'max': 2.0,
                    'median': 1.5,
                },
                'sensitivity_drift': {
                    'drift': 2.0,
                    'min': 2.0,
                    'max': 3.0,
                    'median': 2.5,
                    'frequency_hz': 100,
                },
                'linearity': {
                    'mean': 0.3,
                    'min': 0.1,
                    'max': 0.5,
                },
            },
        },
    )

    _write_json(
        missing_project / 'config.json',
        {
            'epoch_train': 1000,
            'learning_rate': 8e-4,
        },
    )
    _write_json(
        missing_project / 'data' / 'metrics.json',
        {
            'val_mae': 0.4,
            'val_afmae': 0.5,
            'compute_cost': 456.0,
            'compute_details': {'weighted_total': 456.0},
            'metric_details': {},
        },
    )

    analyzer = AblationStudyAnalyzer(
        {
            'projects': [
                {'name': 'full_project', 'path': str(full_project)},
                {'name': 'missing_project', 'path': str(missing_project)},
            ],
            'metrics': {
                'natural_frequency_drift': {'enabled': True, 'reference': 'full_project'},
                'sensitivity_drift': {'enabled': True, 'reference': 'full_project', 'frequency_hz': 100},
                'linearity': {'enabled': True},
                'compute_cost': {'enabled': True},
                'mae_afmae': {'enabled': True},
            },
        },
        output_dir=tmp_path / 'out',
    )

    results = analyzer.run_analysis()

    freq_missing = results['metrics']['natural_frequency_drift']['missing_project']
    sens_missing = results['metrics']['sensitivity_drift']['missing_project']

    assert 'error' in freq_missing
    assert 'natural_frequency_drift not available' in freq_missing['error']
    assert 'error' in sens_missing
    assert 'sensitivity_drift not available' in sens_missing['error']


def test_generate_markdown_report_marks_missing_metrics_as_error(tmp_path):
    project_path = tmp_path / 'missing_project'
    _write_json(project_path / 'config.json', {'epoch_train': 1000, 'learning_rate': 7e-4})
    _write_json(
        project_path / 'data' / 'metrics.json',
        {
            'val_mae': 0.4,
            'val_afmae': 0.5,
            'compute_cost': 456.0,
            'compute_details': {'weighted_total': 456.0},
            'metric_details': {},
        },
    )

    analyzer = AblationStudyAnalyzer(
        {
            'projects': [{'name': 'missing_project', 'path': str(project_path)}],
            'metrics': {
                'natural_frequency_drift': {'enabled': True},
                'sensitivity_drift': {'enabled': True, 'frequency_hz': 100},
                'linearity': {'enabled': True},
                'compute_cost': {'enabled': True},
                'mae_afmae': {'enabled': True},
            },
        },
        output_dir=tmp_path / 'out',
    )

    report = analyzer.generate_markdown_report()

    assert '| missing_project | 456.0 | 0.4000 | 0.5000 | ERROR | ERROR | ERROR | - | - | - |' in report
    assert '缺少数据的项目可通过' in report


def test_generate_markdown_report_marks_null_mae_values_as_error(tmp_path):
    project_path = tmp_path / 'null_mae_project'
    _write_json(project_path / 'config.json', {'epoch_train': 1000, 'learning_rate': 7e-4})
    _write_json(
        project_path / 'data' / 'metrics.json',
        {
            'val_mae': None,
            'val_afmae': None,
            'compute_cost': 456.0,
            'compute_details': {'weighted_total': 456.0},
            'metric_details': {
                'natural_frequency_drift': {
                    'drift': 1.0,
                    'min': 0.5,
                    'max': 1.5,
                    'median': 1.0,
                },
                'sensitivity_drift': {
                    'drift': 2.0,
                    'min': 1.5,
                    'max': 2.5,
                    'median': 2.0,
                    'frequency_hz': 100,
                },
                'linearity': {
                    'mean': 0.3,
                    'min': 0.1,
                    'max': 0.5,
                },
            },
        },
    )

    analyzer = AblationStudyAnalyzer(
        {
            'projects': [{'name': 'null_mae_project', 'path': str(project_path)}],
            'metrics': {
                'natural_frequency_drift': {'enabled': True},
                'sensitivity_drift': {'enabled': True, 'frequency_hz': 100},
                'linearity': {'enabled': True},
                'compute_cost': {'enabled': True},
                'mae_afmae': {'enabled': True},
            },
        },
        output_dir=tmp_path / 'out',
    )

    results = analyzer.run_analysis()
    report = analyzer.generate_markdown_report()

    assert 'error' in results['metrics']['mae_afmae']['null_mae_project']
    assert '| null_mae_project | 456.0 | ERROR | ERROR | 1.0000 | 2.0000 | 0.3000 | - | - | - |' in report
