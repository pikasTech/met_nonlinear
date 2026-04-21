from __future__ import annotations

import json

from core.board_inference.models import (
    NATIVE_KEIL_BENCH_EXECUTORS,
    NATIVE_QEMU_EXECUTORS,
)
from core.board_inference.registry import detect_model_type


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as file_obj:
        json.dump(payload, file_obj, indent=2, ensure_ascii=False)
        file_obj.write('\n')


def test_detect_model_type_supports_legacy_lstm_suffix_names(tmp_path):
    model_dir = tmp_path / 'projects' / 'legacy_lstm'
    weights_path = model_dir / 'data' / 'best_val.weights.json'
    _write_json(weights_path, [
        {'name': 'lstm_1/lstm_cell_1/kernel:0', 'value': []},
        {'name': 'lstm_1/lstm_cell_1/recurrent_kernel:0', 'value': []},
    ])

    assert detect_model_type('projects/legacy_lstm', model_dir, weights_path) == 'lstm'


def test_detect_model_type_supports_legacy_gru_suffix_names(tmp_path):
    model_dir = tmp_path / 'projects' / 'legacy_grn'
    weights_path = model_dir / 'data' / 'best_val.weights.json'
    _write_json(weights_path, [
        {'name': 'gru_1/gru_cell_1/kernel:0', 'value': []},
        {'name': 'gru_1/gru_cell_1/recurrent_kernel:0', 'value': []},
    ])

    assert detect_model_type('projects/legacy_grn', model_dir, weights_path) == 'grn'


def test_all_supported_board_inference_model_types_have_native_executors():
    expected = {
        'frikan',
        'grn',
        'lstm',
        'lstm_transformer',
        'onedcnn',
        'tcn',
        'wavenet2',
        'wavenet3',
    }

    assert expected.issubset(set(NATIVE_QEMU_EXECUTORS))
    assert expected.issubset(set(NATIVE_KEIL_BENCH_EXECUTORS))
