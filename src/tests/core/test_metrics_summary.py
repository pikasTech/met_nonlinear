"""Tests for core.metrics_summary."""

import json
import sys
from pathlib import Path

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
        'estimated_cost': {
            'weighted_units': {
                'total': 9876.5,
            },
        },
    }), encoding='utf-8')
    (checkpoint_dir / 'linear_response.json').write_text(json.dumps({
        'frequencies': [10, 20, 40, 80],
        'gains_origin': [
            [1, 2, 4, 8],
            [1, 2, 4, 8],
        ],
        'gains_comped': [
            [1, 2, 4, 8],
            [1, 2, 4, 8],
        ],
    }), encoding='utf-8')

    summary = build_project_metrics_summary(str(checkpoint_dir), project_name='demo')

    assert summary['status'] == 'complete'
    assert summary['project_name'] == 'demo'
    assert summary['epochs'] == 123
    assert summary['train_mae'] == 0.41
    assert summary['train_afmae'] == 0.42
    assert summary['val_mae'] == 0.51
    assert summary['val_afmae'] == 0.52
    assert summary['compute_cost'] == 9876.5
    assert summary['total_params'] == 4567
    assert summary['freq_drift_hz'] == 0.0
    assert summary['sens_drift_percent'] == 0.0
    assert summary['linearity_percent'] == 100.0
    assert summary['display_metrics']['TRAIN_MAE'] == 0.41


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
    assert 'compute_analysis.json' in summary['missing_sources']
    assert 'linear_response.json' in summary['missing_sources']
    assert 'training_info.evaluation_metrics' in summary['missing_sections']
    assert output_path.exists()