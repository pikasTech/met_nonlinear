"""Tests for core.metrics_summary."""

import json
import sys
from pathlib import Path

import pytest

# Add src to path
_SRC_DIR = Path(__file__).parent.parent.parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from core.metrics_summary import build_project_metrics_summary, save_project_metrics_summary


def test_build_project_metrics_summary_complete(tmp_path):
    checkpoint_dir = tmp_path / 'data'
    checkpoint_dir.mkdir()

    (checkpoint_dir / 'training_info.json').write_text(json.dumps({
        'total_epochs': 123,
        'min_loss': 0.11,
        'min_val_loss': 0.22,
        'evaluation_metrics': {
            'weights_source': 'best_val',
            'train_loss': 0.31,
            'val_loss': 0.32,
            'train_mae': 0.41,
            'train_afmae': 0.42,
            'val_mae': 0.51,
            'val_afmae': 0.52,
        },
    }), encoding='utf-8')
    (checkpoint_dir / 'compute_analysis.json').write_text(json.dumps({
        'total_params': 4567,
        'totals': {
            'additions': 11,
            'multiplications': 22,
            'maps': 33,
            'total': 66,
        },
        'estimated_cost': {
            'weighted_units': {
                'total': 9876.5,
                'additions': 1.5,
                'multiplications': 2.5,
                'maps': 3.5,
            },
        },
    }), encoding='utf-8')
    (checkpoint_dir / 'linear_response.json').write_text(json.dumps({
        'frequencies': [50, 100, 150],
        'gains_origin': [
            [1, 2.0, 3],
            [1, 2.0, 3],
            [1, 2.0, 3],
        ],
        'gains_comped': [
            [1, 2.0, 3],
            [1, 2.5, 3],
            [1, 1.5, 3],
        ],
        'fit_params_origin': [
            [1, (2 * 3.141592653589793 * 9) ** 2, 1],
            [1, (2 * 3.141592653589793 * 11) ** 2, 1],
            [1, (2 * 3.141592653589793 * 13) ** 2, 1],
        ],
        'fit_params_comped': [
            [1, (2 * 3.141592653589793 * 10) ** 2, 1],
            [1, (2 * 3.141592653589793 * 12) ** 2, 1],
            [1, (2 * 3.141592653589793 * 14) ** 2, 1],
        ],
    }), encoding='utf-8')
    (checkpoint_dir / 'linearity_by_frequency.json').write_text(json.dumps({
        'linearity_by_frequency': [
            {
                'frequency_hz': 50,
                'r_squared_origin': 0.80,
                'r_squared_comped': 0.90,
            },
            {
                'frequency_hz': 100,
                'r_squared_origin': 0.85,
                'r_squared_comped': 0.95,
            },
        ],
    }), encoding='utf-8')

    checkpoint_dir.parent.joinpath('config.json').write_text(json.dumps({
        'learning_rate': 0.002,
        'use_auto_lr': False,
        'use_power_loss': True,
    }), encoding='utf-8')

    summary = build_project_metrics_summary(str(checkpoint_dir), project_name='demo')

    assert summary['status'] == 'complete'
    assert summary['project_name'] == 'demo'
    assert summary['epochs'] == 123
    assert summary['train_mae'] == 0.41
    assert summary['train_afmae'] == 0.42
    assert summary['val_mae'] == 0.51
    assert summary['val_afmae'] == 0.52
    assert summary['loss_function'] == 'MAE+AFMAE'
    assert summary['loss_function_key'] == 'power_log_mae'
    assert summary['loss_function_source'] == 'config.use_power_loss'
    assert summary['compute_cost'] == 9876.5
    assert summary['compute_cost_status'] == 'complete'
    assert summary['compute_has_unsupported_layers'] is False
    assert summary['compute_unsupported_layer_count'] == 0
    assert summary['compute_cost_warning'] is None
    assert summary['total_params'] == 4567
    assert summary['freq_drift_hz'] == pytest.approx(2.0)
    assert summary['sens_drift_percent'] == pytest.approx(0.5)
    assert summary['linearity_percent'] == pytest.approx(7.5)
    assert summary['metric_details']['natural_frequency_drift']['median'] == pytest.approx(12.0)
    assert summary['metric_details']['linearity']['max'] == pytest.approx(10.0)
    assert summary['compute_details']['weighted_maps'] == 3.5
    assert summary['display_metrics']['TRAIN_MAE'] == 0.41
    assert summary['display_metrics']['Loss Function'] == 'MAE+AFMAE'


def test_save_project_metrics_summary_partial(tmp_path):
    checkpoint_dir = tmp_path / 'data'
    checkpoint_dir.mkdir()

    (checkpoint_dir / 'training_info.json').write_text(json.dumps({
        'total_epochs': 10,
        'min_loss': 0.1,
        'min_val_loss': 0.2,
    }), encoding='utf-8')

    output_path = checkpoint_dir / 'metrics.json'
    summary = save_project_metrics_summary(str(checkpoint_dir), str(output_path), project_name='demo')

    assert summary['status'] == 'partial'
    assert summary['loss_function'] is None
    assert 'compute_analysis.json' in summary['missing_sources']
    assert 'linear_response.json' in summary['missing_sources']
    assert 'linearity_by_frequency.json' in summary['missing_sources']
    assert 'training_info.evaluation_metrics' in summary['missing_sections']
    assert output_path.exists()


def test_build_project_metrics_summary_marks_compute_warning(tmp_path):
    checkpoint_dir = tmp_path / 'data'
    checkpoint_dir.mkdir()

    (checkpoint_dir / 'compute_analysis.json').write_text(json.dumps({
        'total_params': 100,
        'totals': {
            'additions': 1,
            'multiplications': 2,
            'maps': 3,
            'total': 6,
        },
        'estimated_cost': {
            'weighted_units': {
                'total': 21.0,
                'additions': 1.0,
                'multiplications': 2.0,
                'maps': 18.0,
            },
        },
        'unsupported_layers': ['transformer_mha_0'],
        'unsupported_layer_details': [
            {
                'name': 'transformer_mha_0',
                'type': 'MultiHeadAttention',
                'reason': 'unsupported_layer_type',
            }
        ],
    }), encoding='utf-8')

    summary = build_project_metrics_summary(str(checkpoint_dir), project_name='demo')

    assert summary['compute_cost'] == 21.0
    assert summary['compute_cost_status'] == 'partial'
    assert summary['compute_has_unsupported_layers'] is True
    assert summary['compute_unsupported_layer_count'] == 1
    assert summary['compute_unsupported_layers'] == ['transformer_mha_0']
    assert summary['compute_unsupported_layer_details'][0]['type'] == 'MultiHeadAttention'
    assert 'transformer_mha_0' in summary['compute_cost_warning']


def test_build_project_metrics_summary_extracts_board_inference_metrics(tmp_path):
    checkpoint_dir = tmp_path / 'project' / 'data'
    checkpoint_dir.mkdir(parents=True)
    board_project_dir = tmp_path / 'ex_projects' / 'inference' / 'qemu-c-inference' / 'demo_model'
    board_data_dir = board_project_dir / 'data'
    board_data_dir.mkdir(parents=True)

    (board_data_dir / 'benchmark_summary.json').write_text(json.dumps({
        'comparison': {
            'mae': 0.0123,
        },
    }), encoding='utf-8')
    (board_data_dir / 'keil_benchmark_summary.json').write_text(json.dumps({
        'comparison': {
            'mae': 0.0456,
        },
        'parsed_output': {
            'wall_time_per_iter_ms': 200.0,
        },
        'validation': {
            'record_count': 2,
            'seq_len': 100,
        },
    }), encoding='utf-8')

    checkpoint_dir.parent.joinpath('config.json').write_text(json.dumps({
        'board_inference_ep_path': str(board_project_dir),
    }), encoding='utf-8')

    summary = build_project_metrics_summary(str(checkpoint_dir), project_name='demo')

    assert summary['board_inference_ep_path'] == str(board_project_dir).replace('\\', '/')
    assert summary['board_qemu_mae'] == pytest.approx(0.0123)
    assert summary['board_keil_mae'] == pytest.approx(0.0456)
    assert summary['board_keil_speed'] == pytest.approx(1.0)
    assert summary['board_inference']['keil_speed_unit'] == 'ms/point'
    assert summary['sources']['board_inference_qemu'] is True
    assert summary['sources']['board_inference_keil'] is True
    assert summary['display_metrics']['QEMU-MAE'] == pytest.approx(0.0123)
    assert summary['display_metrics']['KEIL-MAE'] == pytest.approx(0.0456)
    assert summary['display_metrics']['KEIL-SPEED'] == pytest.approx(1.0)


def test_build_project_metrics_summary_marks_missing_board_inference_sources(tmp_path):
    checkpoint_dir = tmp_path / 'project' / 'data'
    checkpoint_dir.mkdir(parents=True)
    board_project_dir = tmp_path / 'ex_projects' / 'inference' / 'qemu-c-inference' / 'missing_model'
    board_project_dir.mkdir(parents=True)

    checkpoint_dir.parent.joinpath('config.json').write_text(json.dumps({
        'board_inference_ep_path': str(board_project_dir),
    }), encoding='utf-8')

    summary = build_project_metrics_summary(str(checkpoint_dir), project_name='demo')

    assert summary['status'] == 'partial'
    assert 'board_inference.benchmark_summary.json' in summary['missing_sources']
    assert 'board_inference.keil_benchmark_summary.json' in summary['missing_sources']


@pytest.mark.parametrize(
    ('config_data', 'expected_label', 'expected_key', 'expected_source'),
    [
        ({'use_power_loss': False}, 'MAE', 'mae', 'config.use_power_loss'),
        ({'use_power_loss': False, 'use_pure_power_loss': True}, 'AFMAE', 'pure_power_log_mae', 'config.use_pure_power_loss'),
        ({'use_power_loss': True}, 'MAE+AFMAE', 'power_log_mae', 'config.use_power_loss'),
        ({'loss_type': 'afmse'}, 'AFMSE', 'afmse', 'config.loss_type'),
    ],
)
def test_build_project_metrics_summary_extracts_loss_function(
    tmp_path,
    config_data,
    expected_label,
    expected_key,
    expected_source,
):
    checkpoint_dir = tmp_path / 'data'
    checkpoint_dir.mkdir()
    checkpoint_dir.parent.joinpath('config.json').write_text(json.dumps(config_data), encoding='utf-8')

    summary = build_project_metrics_summary(str(checkpoint_dir), project_name='demo')

    assert summary['loss_function'] == expected_label
    assert summary['loss_function_key'] == expected_key
    assert summary['loss_function_source'] == expected_source
    assert summary['display_metrics']['Loss Function'] == expected_label
