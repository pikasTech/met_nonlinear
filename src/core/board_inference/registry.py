# Legacy reference: src/core/lstm_qemu_ep_task.py last present in commit c44b43e36eeb4aa39abab42c20795c33fac3060f.
"""Model detection and native implementation registry for board inference."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict

from .models import NATIVE_MODEL_TYPES


_LSTM_CELL_PATTERN = re.compile(r'lstm_cell(?:_\d+)?/')
_GRU_CELL_PATTERN = re.compile(r'gru_cell(?:_\d+)?/')


def load_project_config(model_dir: Path) -> Dict[str, object]:
    config_path = model_dir / 'config.json'
    if not config_path.exists():
        return {}
    with open(config_path, 'r', encoding='utf-8') as file_obj:
        return json.load(file_obj)


def detect_model_type(model_project_name: str,
                      model_dir: Path,
                      weights_json_path: Path) -> str:
    project_config = load_project_config(model_dir)
    if project_config:
        use_model = str(project_config.get('use_model', '')).strip().upper()
        if use_model == 'FRIKAN':
            return 'frikan'
        if use_model == 'LSTM':
            return 'lstm'
        if use_model == 'RNN':
            return 'rnn'
        if use_model == 'LSTMTRANSFORMER':
            return 'lstm_transformer'
        if use_model in {'GRN', 'GRU'}:
            return 'grn'
        if use_model == '1DCNN':
            return 'onedcnn'
        if use_model == 'TCN':
            return 'tcn'
        if use_model == 'WAVENET2':
            return 'wavenet2'
        if use_model == 'WAVENET3':
            return 'wavenet3'

    with open(weights_json_path, 'r', encoding='utf-8') as file_obj:
        weights = json.load(file_obj)

    weight_names = [str(item.get('name', '')).replace('\\', '/') for item in weights]
    if any(_LSTM_CELL_PATTERN.search(name) for name in weight_names):
        if any('transformer_mha_' in name for name in weight_names):
            return 'lstm_transformer'
        return 'lstm'
    if any(_GRU_CELL_PATTERN.search(name) for name in weight_names):
        return 'grn'
    if any('dense_kan' in name for name in weight_names) and any('simple_rnn' in name for name in weight_names):
        return 'frikan'
    if any('simple_rnn' in name for name in weight_names):
        return 'rnn'
    if any(re.fullmatch(r'conv_\d+/kernel:0', name) for name in weight_names):
        return 'onedcnn'
    if any(re.fullmatch(r'temporal_block_\d+_conv_1/kernel:0', name) for name in weight_names):
        return 'tcn'
    if any(name.endswith('output_conv/kernel:0') for name in weight_names):
        return 'wavenet2'
    if any(name.endswith('dense_1/kernel:0') for name in weight_names) and any(name.startswith('initial_conv/') for name in weight_names):
        return 'wavenet3'

    raise ValueError(f'无法自动识别 qemu-c-inference 模型类型: {model_project_name}')


def has_native_implementation(model_type: str) -> bool:
    return model_type in NATIVE_MODEL_TYPES
