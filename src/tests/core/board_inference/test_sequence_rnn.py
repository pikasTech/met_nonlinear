from __future__ import annotations

import json

from core.board_inference.models.sequence import _load_rnn_model_spec


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as file_obj:
        json.dump(payload, file_obj, indent=2, ensure_ascii=False)
        file_obj.write('\n')


def test_load_rnn_model_spec_supports_single_hidden_dense(tmp_path):
    model_dir = tmp_path / 'projects' / 'rnn_demo'
    weights_path = model_dir / 'data' / 'best_val.weights.json'
    _write_json(model_dir / 'config.json', {
        'model_subcfg': {
            'recurrent_units': 2,
            'rnn_layers': 1,
            'dense_layers': 1,
            'dense_units': 3,
            'dense_activation': 'silu',
            'rnn_activation': 'tanh',
            'output_activation': None,
        }
    })
    _write_json(weights_path, [
        {
            'name': 'simple_rnn/simple_rnn_cell/kernel:0',
            'shape': [1, 2],
            'value': [[0.1, 0.2]],
        },
        {
            'name': 'simple_rnn/simple_rnn_cell/recurrent_kernel:0',
            'shape': [2, 2],
            'value': [[0.3, 0.4], [0.5, 0.6]],
        },
        {
            'name': 'simple_rnn/simple_rnn_cell/bias:0',
            'shape': [2],
            'value': [0.01, -0.02],
        },
        {
            'name': 'dense/kernel:0',
            'shape': [2, 3],
            'value': [[0.7, 0.8, 0.9], [1.0, 1.1, 1.2]],
        },
        {
            'name': 'dense/bias:0',
            'shape': [3],
            'value': [0.03, 0.04, 0.05],
        },
        {
            'name': 'dense_1/kernel:0',
            'shape': [3, 1],
            'value': [[1.3], [1.4], [1.5]],
        },
        {
            'name': 'dense_1/bias:0',
            'shape': [1],
            'value': [0.06],
        },
    ])

    spec = _load_rnn_model_spec('projects/rnn_demo', model_dir, weights_path)

    assert spec.input_dim == 1
    assert spec.rnn_units == 2
    assert spec.has_dense is True
    assert spec.dense_units == 3
    assert spec.output_input_units == 3
    assert spec.output_units == 1
    assert spec.rnn_activation == 'tanh'
    assert spec.dense_activation == 'silu'
    assert spec.output_activation == 'linear'
