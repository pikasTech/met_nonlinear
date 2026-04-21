# Legacy reference: src/core/lstm_qemu_ep_task.py last present in commit c44b43e36eeb4aa39abab42c20795c33fac3060f.
"""Native FRIKAN implementation for board inference.

The goal is to migrate model-specific logic out of `core.lstm_qemu_ep_task`
while reusing the shared platform helpers in `board_inference.platforms`.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import numpy as np

from core.external_path_parser import ExternalPath
from core.qemu_cli import execute_qemu_workflow

from ..platforms import benchmark_common as common

logger = logging.getLogger(__name__)

@dataclass
class FrikanIirSpec:
    """单个 FRIKAN 特征通道对应的二阶 IIR 系数。"""

    b0: float
    b1: float
    b2: float
    a1: float
    a2: float

@dataclass
class FrikanKanLayerSpec:
    """FRIKAN 中单层 DenseKAN 的导出规格。"""

    name: str
    input_dim: int
    output_dim: int
    grid_size: int
    spline_order: int
    grid_range: List[float]
    spline_kernel: List[List[List[float]]]
    bias: List[float]
    scale_factor: List[List[float]]
    use_symmetry: bool
    only_positive: bool
    use_even: bool
    basis_activation: str
    disable_basis_activation: bool
    lut_support_min: float
    lut_support_max: float
    lut_values: List[List[List[float]]]

@dataclass
class FrikanModelSpec:
    """FRIKAN C 生成所需的模型规格。"""

    model_project_name: str
    weights_json_path: Path
    input_dim: int
    feature_count: int
    kan_layers: List[FrikanKanLayerSpec]
    iir_filters: List[FrikanIirSpec]
    output_units: int
    lut_points: int
    lut_interpolation: bool
    use_symmetry: bool
    use_even: bool

def _split_batch_sequences(array: np.ndarray) -> List[Any]:
    values = np.asarray(array, dtype=np.float64)
    if values.ndim == 2:
        values = values[..., np.newaxis]
    if values.ndim != 3:
        raise ValueError(f'中间输出维度非法，期望 3 维张量，实际 {values.ndim}')
    return [values[index].tolist() for index in range(values.shape[0])]

def _run_frikan_reference_from_spec(model_spec: FrikanModelSpec,
                                    x_input: np.ndarray,
                                    input_data_range: float,
                                    output_data_range: float,
                                    use_scaler: bool) -> tuple[np.ndarray, Dict[str, List[Any]]]:
    x_values = np.asarray(x_input, dtype=np.float64)
    if x_values.ndim != 3 or x_values.shape[-1] != 1:
        raise ValueError(f'FRIKAN 参考推理输入维度非法: {x_values.shape}')

    x_scaled = x_values.copy()
    if use_scaler and input_data_range != 0.0:
        x_scaled = x_scaled / input_data_range

    batch_size = int(x_scaled.shape[0])
    seq_len = int(x_scaled.shape[1])
    output_scaled = np.zeros((batch_size, seq_len, 1), dtype=np.float64)
    iir_output = np.zeros((batch_size, seq_len, model_spec.feature_count), dtype=np.float64)
    kan_outputs = [
        np.zeros((batch_size, seq_len, layer.output_dim), dtype=np.float64)
        for layer in model_spec.kan_layers
    ]
    layer_grids = [
        _build_densekan_grid(layer.grid_range, layer.grid_size, layer.spline_order)
        for layer in model_spec.kan_layers
    ]

    for batch_index in range(batch_size):
        x1 = np.zeros(model_spec.feature_count, dtype=np.float64)
        x2 = np.zeros(model_spec.feature_count, dtype=np.float64)
        y1 = np.zeros(model_spec.feature_count, dtype=np.float64)
        y2 = np.zeros(model_spec.feature_count, dtype=np.float64)

        for step_index in range(seq_len):
            scaled_sample = float(x_scaled[batch_index, step_index, 0])
            current_values = np.zeros(model_spec.feature_count, dtype=np.float64)

            for feature_index, iir_spec in enumerate(model_spec.iir_filters):
                response = (
                    iir_spec.b0 * scaled_sample
                    + iir_spec.b1 * x1[feature_index]
                    + iir_spec.b2 * x2[feature_index]
                    - iir_spec.a1 * y1[feature_index]
                    - iir_spec.a2 * y2[feature_index]
                )
                x2[feature_index] = x1[feature_index]
                x1[feature_index] = scaled_sample
                y2[feature_index] = y1[feature_index]
                y1[feature_index] = response
                current_values[feature_index] = response

            iir_output[batch_index, step_index] = current_values

            for layer_index, layer_spec in enumerate(model_spec.kan_layers):
                next_values = np.asarray(layer_spec.bias[:layer_spec.output_dim], dtype=np.float64).copy()
                layer_grid = layer_grids[layer_index]
                for output_index in range(layer_spec.output_dim):
                    for input_index in range(layer_spec.input_dim):
                        next_values[output_index] += _evaluate_frikan_edge_function(
                            x=float(current_values[input_index]),
                            grid=layer_grid,
                            spline_order=layer_spec.spline_order,
                            spline_kernel=np.asarray(layer_spec.spline_kernel[input_index], dtype=np.float64)[:, output_index],
                            scale_factor=float(layer_spec.scale_factor[input_index][output_index]),
                            basis_activation=layer_spec.basis_activation,
                            disable_basis_activation=layer_spec.disable_basis_activation,
                            use_symmetry=layer_spec.use_symmetry,
                            only_positive=layer_spec.only_positive,
                            use_even=layer_spec.use_even,
                        )
                kan_outputs[layer_index][batch_index, step_index] = next_values
                current_values = next_values

            output_scaled[batch_index, step_index, 0] = current_values[0]

    output_values = output_scaled.copy()
    if use_scaler:
        output_values *= output_data_range

    debug_sequences: Dict[str, List[Any]] = {
        'input_scaled': _split_batch_sequences(x_scaled),
        'iir_output': _split_batch_sequences(iir_output),
        'output_scaled': _split_batch_sequences(output_scaled),
    }
    for layer_index, layer_output in enumerate(kan_outputs):
        debug_sequences[f'kan_layer_{layer_index}'] = _split_batch_sequences(layer_output)

    return output_values, debug_sequences

def _load_frikan_model_spec(model_project_name: str,
                            model_dir: Path,
                            weights_json_path: Path,
                            lut_points: int,
                            lut_interpolation: bool) -> FrikanModelSpec:
    with open(weights_json_path, 'r', encoding='utf-8') as file_obj:
        weights = json.load(file_obj)

    project_config: Dict[str, Any] = {}
    config_path = model_dir / 'config.json'
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as file_obj:
            project_config = json.load(file_obj)

    model_subcfg = project_config.get('model_subcfg', {}) if isinstance(project_config.get('model_subcfg', {}), dict) else {}
    use_symmetry = bool(model_subcfg.get('use_symmetry', True))
    only_positive = bool(model_subcfg.get('only_positive', True))
    use_even = bool(model_subcfg.get('use_even', False))
    basis_activation = str(project_config.get('basis_activation', 'silu'))
    disable_basis_activation = bool(project_config.get('disable_basis_activation', True))

    simple_rnn_kernel_entries: List[Dict[str, Any]] = []
    simple_rnn_recurrent_entries: List[Dict[str, Any]] = []
    for item in weights:
        name = str(item.get('name', '')).replace('\\', '/')
        if re.fullmatch(r'simple_rnn(?:_\d+)?/simple_rnn_cell(?:_\d+)?/kernel:0', name):
            simple_rnn_kernel_entries.append(item)
        elif re.fullmatch(r'simple_rnn(?:_\d+)?/simple_rnn_cell(?:_\d+)?/recurrent_kernel:0', name):
            simple_rnn_recurrent_entries.append(item)

    simple_rnn_kernel_entries.sort(key=lambda item: _simple_rnn_sort_key(str(item.get('name', ''))))
    simple_rnn_recurrent_entries.sort(key=lambda item: _simple_rnn_sort_key(str(item.get('name', ''))))
    if not simple_rnn_kernel_entries or len(simple_rnn_kernel_entries) != len(simple_rnn_recurrent_entries):
        raise ValueError('FRIKAN 权重中 simple_rnn kernel / recurrent_kernel 数量不匹配')

    iir_filters: List[FrikanIirSpec] = []
    for kernel_entry, recurrent_entry in zip(simple_rnn_kernel_entries, simple_rnn_recurrent_entries):
        kernel_values = np.asarray(kernel_entry['value'], dtype=np.float64)
        recurrent_values = np.asarray(recurrent_entry['value'], dtype=np.float64)
        if kernel_values.shape != (1, 4):
            raise ValueError(f'FRIKAN simple_rnn kernel 形状非法: {kernel_values.shape}')
        if recurrent_values.shape != (4, 4):
            raise ValueError(f'FRIKAN simple_rnn recurrent_kernel 形状非法: {recurrent_values.shape}')
        iir_filters.append(FrikanIirSpec(
            b0=float(kernel_values[0, 0]),
            b1=float(recurrent_values[2, 0]),
            b2=float(recurrent_values[3, 0]),
            a1=float(-recurrent_values[0, 0]),
            a2=float(-recurrent_values[1, 0]),
        ))

    spline_entries: List[Dict[str, Any]] = []
    for item in weights:
        name = str(item.get('name', '')).replace('\\', '/')
        if re.fullmatch(r'dense_kan(?:_\d+)?/spline_kernel:0', name):
            spline_entries.append(item)

    spline_entries.sort(key=lambda item: _dense_kan_sort_key(str(item.get('name', ''))))
    if not spline_entries:
        raise ValueError('FRIKAN 权重中未找到任何 DenseKAN spline_kernel')

    dense_kan_layers: List[FrikanKanLayerSpec] = []
    for spline_entry in spline_entries:
        layer_name = str(spline_entry.get('name', '')).replace('\\', '/').split('/')[0]
        kernel = np.asarray(spline_entry['value'], dtype=np.float64)
        if kernel.ndim != 3:
            raise ValueError(f'{layer_name} spline_kernel 维度非法: {kernel.shape}')

        bias_entry = _find_weight_entry(weights, f'{layer_name}/bias')
        bias = np.asarray(bias_entry['value'], dtype=np.float64).reshape(-1)

        scale_factor_entry = _find_weight_entry_optional(weights, f'{layer_name}/scale_factor')
        if scale_factor_entry is not None:
            scale_factor = np.asarray(scale_factor_entry['value'], dtype=np.float64)
        else:
            scale_factor = np.ones((kernel.shape[0], kernel.shape[2]), dtype=np.float64)

        if scale_factor.shape != (kernel.shape[0], kernel.shape[2]):
            raise ValueError(
                f'{layer_name} scale_factor 形状非法，期望 {(kernel.shape[0], kernel.shape[2])}，实际 {scale_factor.shape}'
            )

        config = spline_entry.get('config', {}) or {}
        grid_size = int(config.get('grid_size', kernel.shape[1]))
        spline_order = int(config.get('spline_order', 0))
        grid_range = [float(value) for value in config.get('grid_range', [0.0, 1.0])]
        support_min, support_max = _compute_kan_lut_support(grid_range, grid_size, spline_order, use_symmetry)
        lut_values = _build_frikan_lut_values(
            spline_kernel=kernel,
            scale_factor=scale_factor,
            grid_range=grid_range,
            grid_size=grid_size,
            spline_order=spline_order,
            lut_points=lut_points,
            basis_activation=basis_activation,
            disable_basis_activation=disable_basis_activation,
            use_symmetry=use_symmetry,
            only_positive=only_positive,
            use_even=use_even,
            support_min=support_min,
            support_max=support_max,
        )

        dense_kan_layers.append(FrikanKanLayerSpec(
            name=layer_name,
            input_dim=int(kernel.shape[0]),
            output_dim=int(kernel.shape[2]),
            grid_size=grid_size,
            spline_order=spline_order,
            grid_range=grid_range,
            spline_kernel=kernel.tolist(),
            bias=bias.tolist(),
            scale_factor=scale_factor.tolist(),
            use_symmetry=use_symmetry,
            only_positive=only_positive,
            use_even=use_even,
            basis_activation=basis_activation,
            disable_basis_activation=disable_basis_activation,
            lut_support_min=support_min,
            lut_support_max=support_max,
            lut_values=lut_values,
        ))

    if dense_kan_layers[-1].output_dim != 1:
        raise ValueError(f'当前仅支持单输出 FRIKAN，实际 output_dim={dense_kan_layers[-1].output_dim}')

    return FrikanModelSpec(
        model_project_name=model_project_name,
        weights_json_path=weights_json_path,
        input_dim=1,
        feature_count=len(iir_filters),
        kan_layers=dense_kan_layers,
        iir_filters=iir_filters,
        output_units=1,
        lut_points=lut_points,
        lut_interpolation=lut_interpolation,
        use_symmetry=use_symmetry,
        use_even=use_even,
    )

def _find_weight_entry(weights: Iterable[Dict[str, Any]], fragment: str) -> Dict[str, Any]:
    for item in weights:
        name = str(item.get('name', '')).replace('\\', '/')
        if fragment in name:
            return item
    raise KeyError(f'未找到权重项: {fragment}')

def _find_weight_entry_optional(weights: Iterable[Dict[str, Any]], fragment: str) -> Optional[Dict[str, Any]]:
    for item in weights:
        name = str(item.get('name', '')).replace('\\', '/')
        if fragment in name:
            return item
    return None

def _simple_rnn_sort_key(weight_name: str) -> int:
    match = re.match(r'simple_rnn(?:_(\d+))?/', weight_name.replace('\\', '/'))
    if not match or match.group(1) is None:
        return 0
    return int(match.group(1)) + 1

def _dense_kan_sort_key(weight_name: str) -> int:
    match = re.match(r'dense_kan(?:_(\d+))?/', weight_name.replace('\\', '/'))
    if not match:
        return 10_000
    if match.group(1) is None:
        return 10_000
    return int(match.group(1))

def _compute_kan_lut_support(grid_range: Sequence[float],
                             grid_size: int,
                             spline_order: int,
                             use_symmetry: bool) -> tuple[float, float]:
    bound = float(grid_range[1]) - float(grid_range[0])
    expansion = 0.0 if grid_size <= 0 else (spline_order * bound / grid_size)
    support_min = float(grid_range[0]) - expansion
    support_max = float(grid_range[1]) + expansion
    if use_symmetry:
        support_min = max(0.0, float(grid_range[0]))
    return support_min, support_max

def _build_frikan_lut_values(spline_kernel: np.ndarray,
                             scale_factor: np.ndarray,
                             grid_range: Sequence[float],
                             grid_size: int,
                             spline_order: int,
                             lut_points: int,
                             basis_activation: str,
                             disable_basis_activation: bool,
                             use_symmetry: bool,
                             only_positive: bool,
                             use_even: bool,
                             support_min: float,
                             support_max: float) -> List[List[List[float]]]:
    if lut_points < 2:
        raise ValueError(f'FRIKAN LUT 点数必须大于等于 2，实际 {lut_points}')

    grid = _build_densekan_grid(grid_range, grid_size, spline_order)
    sample_axis = np.linspace(support_min, support_max, lut_points, dtype=np.float64)
    lut_values: List[List[List[float]]] = []

    for input_index in range(int(spline_kernel.shape[0])):
        per_input: List[List[float]] = []
        for output_index in range(int(spline_kernel.shape[2])):
            kernel_values = np.asarray(spline_kernel[input_index, :, output_index], dtype=np.float64)
            edge_scale = float(scale_factor[input_index, output_index])
            sampled = [
                _evaluate_frikan_edge_function(
                    x=float(sample_value),
                    grid=grid,
                    spline_order=spline_order,
                    spline_kernel=kernel_values,
                    scale_factor=edge_scale,
                    basis_activation=basis_activation,
                    disable_basis_activation=disable_basis_activation,
                    use_symmetry=use_symmetry,
                    only_positive=only_positive,
                    use_even=use_even,
                )
                for sample_value in sample_axis
            ]
            per_input.append(sampled)
        lut_values.append(per_input)

    return lut_values

def _build_densekan_grid(grid_range: Sequence[float],
                         grid_size: int,
                         spline_order: int) -> np.ndarray:
    bound = float(grid_range[1]) - float(grid_range[0])
    return np.linspace(
        float(grid_range[0]) - spline_order * bound / grid_size,
        float(grid_range[1]) + spline_order * bound / grid_size,
        grid_size + 2 * spline_order + 1,
        dtype=np.float64,
    )

def _evaluate_frikan_edge_function(x: float,
                                   grid: np.ndarray,
                                   spline_order: int,
                                   spline_kernel: np.ndarray,
                                   scale_factor: float,
                                   basis_activation: str,
                                   disable_basis_activation: bool,
                                   use_symmetry: bool,
                                   only_positive: bool,
                                   use_even: bool) -> float:
    eval_x = abs(x) if use_symmetry else x
    basis_values = _calc_bspline_values(eval_x, grid, spline_order)
    kernel_values = np.asarray(spline_kernel, dtype=np.float64)
    if use_symmetry and only_positive:
        kernel_values = np.abs(kernel_values)

    spline_output = float(np.dot(basis_values, kernel_values))
    if use_symmetry and not use_even:
        spline_output *= 1.0 if x >= 0.0 else -1.0

    if disable_basis_activation:
        basis_output = 0.0
    else:
        basis_output = _apply_basis_activation(x, basis_activation)

    return (spline_output + basis_output) * scale_factor

def _calc_bspline_values(x: float,
                         grid: np.ndarray,
                         spline_order: int) -> np.ndarray:
    bases = np.asarray([
        1.0 if grid[index] <= x < grid[index + 1] else 0.0
        for index in range(len(grid) - 1)
    ], dtype=np.float64)

    active_length = int(bases.shape[0])
    for order_index in range(1, spline_order + 1):
        active_length -= 1
        next_bases = np.zeros_like(bases)
        for base_index in range(active_length):
            left_term = 0.0
            right_term = 0.0
            left_denominator = grid[base_index + order_index] - grid[base_index]
            right_denominator = grid[base_index + order_index + 1] - grid[base_index + 1]
            if left_denominator != 0.0:
                left_term = ((x - grid[base_index]) / left_denominator) * bases[base_index]
            if right_denominator != 0.0:
                right_term = ((grid[base_index + order_index + 1] - x) / right_denominator) * bases[base_index + 1]
            next_bases[base_index] = left_term + right_term
        bases = next_bases

    return bases[:active_length]

def _apply_basis_activation(x: float, basis_activation: str) -> float:
    normalized = basis_activation.strip().lower()
    if normalized in {'linear', 'identity', 'none'}:
        return x
    if normalized == 'relu':
        return x if x > 0.0 else 0.0
    if normalized == 'tanh':
        return float(np.tanh(x))
    if normalized == 'sigmoid':
        return float(1.0 / (1.0 + np.exp(-x)))
    if normalized in {'silu', 'swish'}:
        sigmoid = 1.0 / (1.0 + np.exp(-x))
        return float(x * sigmoid)
    raise ValueError(f'当前 qemu-c-inference 尚未支持 basis_activation={basis_activation}')

def _render_initializer(values: Any, indent: int = 0) -> str:
    if isinstance(values, (list, tuple)):
        if values and isinstance(values[0], (list, tuple)):
            inner_indent = '    ' * (indent + 1)
            closing_indent = '    ' * indent
            rendered_rows = []
            for item in values:
                rendered_rows.append(f'{inner_indent}{_render_initializer(item, indent + 1)}')
            return '{\n' + ',\n'.join(rendered_rows) + f'\n{closing_indent}' + '}'
        return '{ ' + ', '.join(_format_c_float(float(item)) for item in values) + ' }'
    return _format_c_float(float(values))

def _format_c_float(value: float) -> str:
    return f'{value:.8f}f'

def _compute_frikan_lut_index_params(support_min: float,
                                     support_max: float,
                                     lut_points: int) -> tuple[float, float]:
    if lut_points < 2:
        raise ValueError(f'FRIKAN LUT 点数必须大于等于 2，实际 {lut_points}')

    support_span = float(support_max) - float(support_min)
    if support_span <= 0.0:
        raise ValueError(
            f'FRIKAN LUT 支撑区间非法: support_min={support_min}, support_max={support_max}'
        )

    scale = float(lut_points - 1) / support_span
    offset = -float(support_min) * scale
    return scale, offset

def _render_frikan_model_data_header(model_spec: FrikanModelSpec,
                                     benchmark_config: Dict[str, Any],
                                     validation_artifacts: ValidationArtifacts) -> str:
    validation_input = [record.input_sequence for record in validation_artifacts.records]
    max_layer_inputs = max(layer.input_dim for layer in model_spec.kan_layers)
    max_layer_outputs = max(layer.output_dim for layer in model_spec.kan_layers)

    padded_bias = [
        _pad_float_vector(layer.bias, max_layer_outputs, 0.0)
        for layer in model_spec.kan_layers
    ]
    padded_luts = [
        _pad_frikan_lut_layer(layer.lut_values, max_layer_inputs, max_layer_outputs, model_spec.lut_points)
        for layer in model_spec.kan_layers
    ]
    lines = [
        '#ifndef GENERATED_FRIKAN_MODEL_DATA_H',
        '#define GENERATED_FRIKAN_MODEL_DATA_H',
        '',
        '#include <stdint.h>',
        '',
        'typedef float port_float;',
        '',
        f'#define FRIKAN_INPUT_DIM {model_spec.input_dim}u',
        f'#define FRIKAN_FEATURES {model_spec.feature_count}u',
        f'#define FRIKAN_KAN_LAYER_COUNT {len(model_spec.kan_layers)}u',
        f'#define FRIKAN_MAX_LAYER_INPUTS {max_layer_inputs}u',
        f'#define FRIKAN_MAX_LAYER_OUTPUTS {max_layer_outputs}u',
        f'#define FRIKAN_LUT_POINTS {model_spec.lut_points}u',
        f'#define FRIKAN_LUT_INTERPOLATION {1 if model_spec.lut_interpolation else 0}u',
        f'#define FRIKAN_USE_SYMMETRY {1 if model_spec.use_symmetry else 0}u',
        f'#define FRIKAN_USE_EVEN {1 if model_spec.use_even else 0}u',
        f'#define OUTPUT_UNITS {model_spec.output_units}u',
        f'#define BENCHMARK_ITERATIONS {int(benchmark_config["iterations"])}u',
        f'#define BENCHMARK_REPEAT_RUNS {int(benchmark_config["repeat_runs"])}u',
        f'#define BENCHMARK_RESET_STATE_EACH_RUN {1 if benchmark_config.get("reset_state_each_run", True) else 0}u',
        f'#define VALIDATION_RECORD_COUNT {validation_artifacts.record_count}u',
        f'#define VALIDATION_SEQ_LEN {validation_artifacts.seq_len}u',
        '',
        f'#define SCALER_INPUT_DATA_RANGE {_format_c_float(validation_artifacts.input_data_range)}',
        f'#define SCALER_OUTPUT_DATA_RANGE {_format_c_float(validation_artifacts.output_data_range)}',
        '',
        f'static const port_float validation_input[VALIDATION_RECORD_COUNT][VALIDATION_SEQ_LEN][FRIKAN_INPUT_DIM] = {_render_initializer(validation_input)};',
        '',
        f'static const uint16_t frikan_layer_input_dims[FRIKAN_KAN_LAYER_COUNT] = {_render_uint_initializer([layer.input_dim for layer in model_spec.kan_layers])};',
        '',
        f'static const uint16_t frikan_layer_output_dims[FRIKAN_KAN_LAYER_COUNT] = {_render_uint_initializer([layer.output_dim for layer in model_spec.kan_layers])};',
        '',
        f'static const port_float frikan_iir_b0[FRIKAN_FEATURES] = {_render_initializer([item.b0 for item in model_spec.iir_filters])};',
        '',
        f'static const port_float frikan_iir_b1[FRIKAN_FEATURES] = {_render_initializer([item.b1 for item in model_spec.iir_filters])};',
        '',
        f'static const port_float frikan_iir_b2[FRIKAN_FEATURES] = {_render_initializer([item.b2 for item in model_spec.iir_filters])};',
        '',
        f'static const port_float frikan_iir_a1[FRIKAN_FEATURES] = {_render_initializer([item.a1 for item in model_spec.iir_filters])};',
        '',
        f'static const port_float frikan_iir_a2[FRIKAN_FEATURES] = {_render_initializer([item.a2 for item in model_spec.iir_filters])};',
        '',
        f'static const port_float frikan_layer_bias[FRIKAN_KAN_LAYER_COUNT][FRIKAN_MAX_LAYER_OUTPUTS] = {_render_initializer(padded_bias)};',
        '',
        f'static const port_float frikan_layer_lut[FRIKAN_KAN_LAYER_COUNT][FRIKAN_MAX_LAYER_INPUTS][FRIKAN_MAX_LAYER_OUTPUTS][FRIKAN_LUT_POINTS] = {_render_initializer(padded_luts)};',
        '',
        '#endif',
        '',
    ]
    return '\n'.join(lines)

def _pad_float_vector(values: Sequence[float],
                      target_length: int,
                      fill_value: float) -> List[float]:
    padded = [float(value) for value in values]
    while len(padded) < target_length:
        padded.append(fill_value)
    return padded

def _pad_frikan_lut_layer(lut_values: Sequence[Sequence[Sequence[float]]],
                          max_inputs: int,
                          max_outputs: int,
                          lut_points: int) -> List[List[List[float]]]:
    padded_inputs: List[List[List[float]]] = []
    for input_index in range(max_inputs):
        padded_outputs: List[List[float]] = []
        if input_index < len(lut_values):
            layer_input = lut_values[input_index]
        else:
            layer_input = []
        for output_index in range(max_outputs):
            if output_index < len(layer_input):
                padded_outputs.append(_pad_float_vector(layer_input[output_index], lut_points, 0.0))
            else:
                padded_outputs.append([0.0] * lut_points)
        padded_inputs.append(padded_outputs)
    return padded_inputs

def _render_uint_initializer(values: Sequence[int], suffix: str = 'u') -> str:
    return '{ ' + ', '.join(f'{int(value)}{suffix}' for value in values) + ' }'

def _render_frikan_forward_body(model_spec: FrikanModelSpec,
                                include_debug_kan_output: bool = True) -> str:
    lines: List[str] = []

    for layer_index, layer_spec in enumerate(model_spec.kan_layers):
        lines.append('    {')
        for output_index in range(layer_spec.output_dim):
            accumulator_name = f'layer_{layer_index}_out_{output_index}'
            lines.append(
                f'        port_float {accumulator_name} = frikan_layer_bias[{layer_index}u][{output_index}u];'
            )
            for input_index in range(layer_spec.input_dim):
                lines.append(
                    f'        {accumulator_name} += FRIKAN_LUT_LOOKUP_LAYER_{layer_index}('
                    f'frikan_layer_lut[{layer_index}u][{input_index}u][{output_index}u], '
                    f'current_values[{input_index}u]);'
                )

        if include_debug_kan_output:
            lines.append('        if (debug_kan_step != 0) {')
            for output_index in range(layer_spec.output_dim):
                lines.append(
                    f'            debug_kan_step[{layer_index}u][{output_index}u] = '
                    f'layer_{layer_index}_out_{output_index};'
                )
            lines.append('        }')

        for output_index in range(layer_spec.output_dim):
            lines.append(
                f'        current_values[{output_index}u] = layer_{layer_index}_out_{output_index};'
            )
        lines.append('    }')

    return '\n'.join(lines)

def _render_frikan_main_c(model_spec: FrikanModelSpec) -> str:
    template = r"""#include <stdint.h>

#include "model_data.h"

#define RCC_BASE 0x40023800u
#define DEMCR (*(volatile uint32_t *)0xE000EDFCu)
#define DWT_CTRL (*(volatile uint32_t *)0xE0001000u)
#define DWT_CYCCNT (*(volatile uint32_t *)0xE0001004u)

#define USART1_BASE 0x40011000u
#define RCC_APB2ENR (*(volatile uint32_t *)(RCC_BASE + 0x44u))
#define USART1_SR (*(volatile uint32_t *)(USART1_BASE + 0x00u))
#define USART1_DR (*(volatile uint32_t *)(USART1_BASE + 0x04u))
#define USART1_BRR (*(volatile uint32_t *)(USART1_BASE + 0x08u))
#define USART1_CR1 (*(volatile uint32_t *)(USART1_BASE + 0x0Cu))

#define RCC_APB2ENR_USART1EN (1u << 4)
#define USART_SR_TXE (1u << 7)
#define USART_CR1_TE (1u << 3)
#define USART_CR1_UE (1u << 13)
#define DEMCR_TRCENA (1u << 24)
#define DWT_CTRL_CYCCNTENA (1u << 0)

static port_float validation_output[VALIDATION_RECORD_COUNT][VALIDATION_SEQ_LEN];
static port_float debug_scaled_input[VALIDATION_SEQ_LEN];
static port_float debug_iir_output[VALIDATION_SEQ_LEN][FRIKAN_FEATURES];
static port_float debug_kan_output[FRIKAN_KAN_LAYER_COUNT][VALIDATION_SEQ_LEN][FRIKAN_MAX_LAYER_OUTPUTS];
static port_float debug_output_scaled[VALIDATION_SEQ_LEN];

static void uart_init(void)
{
    RCC_APB2ENR |= RCC_APB2ENR_USART1EN;
    USART1_BRR = 0x05B2u;
    USART1_CR1 = USART_CR1_UE | USART_CR1_TE;
}

static void uart_putc(char ch)
{
    while ((USART1_SR & USART_SR_TXE) == 0u) {
    }

    USART1_DR = (uint32_t)ch;
}

static void uart_puts(const char *message)
{
    while (*message != '\0') {
        if (*message == '\n') {
            uart_putc('\r');
        }

        uart_putc(*message++);
    }
}

static void uart_put_u32(uint32_t value)
{
    char buffer[11];
    uint32_t index = 0u;

    if (value == 0u) {
        uart_putc('0');
        return;
    }

    while (value > 0u && index < (uint32_t)sizeof(buffer)) {
        buffer[index++] = (char)('0' + (value % 10u));
        value /= 10u;
    }

    while (index > 0u) {
        uart_putc(buffer[--index]);
    }
}

static void uart_put_fixed6(port_float value)
{
    int32_t scaled = (int32_t)(value * 1000000.0f);
    int32_t abs_scaled = scaled;
    int32_t integer_part;
    int32_t fraction;
    int32_t divisor = 100000;

    if (scaled < 0) {
        uart_putc('-');
        abs_scaled = -scaled;
    }

    integer_part = abs_scaled / 1000000;
    fraction = abs_scaled % 1000000;

    uart_put_u32((uint32_t)integer_part);
    uart_putc('.');
    while (divisor > 0) {
        uart_putc((char)('0' + ((fraction / divisor) % 10)));
        divisor /= 10;
    }
}

static void uart_put_matrix_rows(const port_float *values,
                                 uint32_t row_count,
                                 uint32_t column_count)
{
    uint32_t row_index;
    for (row_index = 0u; row_index < row_count; ++row_index) {
        uint32_t column_index;
        if (row_index > 0u) {
            uart_putc(';');
        }
        for (column_index = 0u; column_index < column_count; ++column_index) {
            if (column_index > 0u) {
                uart_putc(',');
            }
            uart_put_fixed6(values[row_index * column_count + column_index]);
        }
    }
}

static void dwt_init(void)
{
    DEMCR |= DEMCR_TRCENA;
    DWT_CYCCNT = 0u;
    DWT_CTRL |= DWT_CTRL_CYCCNTENA;
}

static uint32_t dwt_read_cycles(void)
{
    return DWT_CYCCNT;
}

static uint32_t dwt_is_counting(void)
{
    volatile uint32_t spin;
    uint32_t before;
    uint32_t after;

    dwt_init();
    before = dwt_read_cycles();
    for (spin = 0u; spin < 64u; ++spin) {
        __asm volatile ("nop");
    }
    after = dwt_read_cycles();
    return after > before ? 1u : 0u;
}

static void zero_buffer(port_float *buffer, uint32_t length)
{
    uint32_t index;
    for (index = 0u; index < length; ++index) {
        buffer[index] = 0.0f;
    }
}

static port_float scale_input(port_float value)
{
    if (SCALER_INPUT_DATA_RANGE == 0.0f) {
        return value;
    }
    return value / SCALER_INPUT_DATA_RANGE;
}

static port_float inverse_scale_output(port_float value)
{
    return value * SCALER_OUTPUT_DATA_RANGE;
}

#define FRIKAN_LUT_LAST_INDEX (FRIKAN_LUT_POINTS - 1u)
#define FRIKAN_LUT_LAST_INDEX_FLOAT ((port_float)(FRIKAN_LUT_POINTS - 1u))

#if FRIKAN_USE_SYMMETRY
#define FRIKAN_LUT_PREPARE_VALUE(raw_value) (((raw_value) < 0.0f) ? -(raw_value) : (raw_value))
#else
#define FRIKAN_LUT_PREPARE_VALUE(raw_value) (raw_value)
#endif

#define FRIKAN_LUT_MAP_INDEX(lookup_value, lut_scale, lut_offset) (((lookup_value) * (lut_scale)) + (lut_offset))

__FRIKAN_LUT_LAYER_FUNCTIONS__

__FRIKAN_LUT_LAYER_MACROS__

static void frikan_iir_reset(port_float x1[FRIKAN_FEATURES],
                             port_float x2[FRIKAN_FEATURES],
                             port_float y1[FRIKAN_FEATURES],
                             port_float y2[FRIKAN_FEATURES])
{
    zero_buffer(x1, FRIKAN_FEATURES);
    zero_buffer(x2, FRIKAN_FEATURES);
    zero_buffer(y1, FRIKAN_FEATURES);
    zero_buffer(y2, FRIKAN_FEATURES);
}

static void frikan_forward_step(port_float input_value,
                                port_float x1[FRIKAN_FEATURES],
                                port_float x2[FRIKAN_FEATURES],
                                port_float y1[FRIKAN_FEATURES],
                                port_float y2[FRIKAN_FEATURES],
                                port_float *output_scaled_value,
                                port_float *debug_scaled_input_value,
                                port_float debug_iir_step[FRIKAN_FEATURES],
                                port_float debug_kan_step[FRIKAN_KAN_LAYER_COUNT][FRIKAN_MAX_LAYER_OUTPUTS],
                                port_float *output_value)
{
    uint32_t feature_index;
    port_float scaled_input = scale_input(input_value);
    port_float current_values[FRIKAN_MAX_LAYER_INPUTS];

    if (debug_scaled_input_value != 0) {
        *debug_scaled_input_value = scaled_input;
    }

    if (debug_iir_step != 0) {
        for (feature_index = 0u; feature_index < FRIKAN_FEATURES; ++feature_index) {
            port_float response = frikan_iir_b0[feature_index] * scaled_input
                + frikan_iir_b1[feature_index] * x1[feature_index]
                + frikan_iir_b2[feature_index] * x2[feature_index]
                - frikan_iir_a1[feature_index] * y1[feature_index]
                - frikan_iir_a2[feature_index] * y2[feature_index];

            x2[feature_index] = x1[feature_index];
            x1[feature_index] = scaled_input;
            y2[feature_index] = y1[feature_index];
            y1[feature_index] = response;
            current_values[feature_index] = response;
            debug_iir_step[feature_index] = response;
        }
    } else {
        for (feature_index = 0u; feature_index < FRIKAN_FEATURES; ++feature_index) {
            port_float response = frikan_iir_b0[feature_index] * scaled_input
                + frikan_iir_b1[feature_index] * x1[feature_index]
                + frikan_iir_b2[feature_index] * x2[feature_index]
                - frikan_iir_a1[feature_index] * y1[feature_index]
                - frikan_iir_a2[feature_index] * y2[feature_index];

            x2[feature_index] = x1[feature_index];
            x1[feature_index] = scaled_input;
            y2[feature_index] = y1[feature_index];
            y1[feature_index] = response;
            current_values[feature_index] = response;
        }
    }

__FRIKAN_FORWARD_BODY__

    if (output_scaled_value != 0) {
        *output_scaled_value = current_values[0u];
    }
    *output_value = inverse_scale_output(current_values[0u]);
}

static void run_validation_record(const port_float sequence[VALIDATION_SEQ_LEN][FRIKAN_INPUT_DIM],
                                  port_float output_sequence[VALIDATION_SEQ_LEN],
                                  uint32_t reset_state_each_run,
                                  port_float x1[FRIKAN_FEATURES],
                                  port_float x2[FRIKAN_FEATURES],
                                  port_float y1[FRIKAN_FEATURES],
                                  port_float y2[FRIKAN_FEATURES],
                                  port_float debug_scaled_input_buffer[VALIDATION_SEQ_LEN],
                                  port_float debug_iir_output_buffer[VALIDATION_SEQ_LEN][FRIKAN_FEATURES],
                                  port_float debug_kan_output_buffer[FRIKAN_KAN_LAYER_COUNT][VALIDATION_SEQ_LEN][FRIKAN_MAX_LAYER_OUTPUTS],
                                  port_float debug_output_scaled_buffer[VALIDATION_SEQ_LEN])
{
    uint32_t step;

    if (reset_state_each_run != 0u) {
        frikan_iir_reset(x1, x2, y1, y2);
    }

    for (step = 0u; step < VALIDATION_SEQ_LEN; ++step) {
        port_float step_kan_debug[FRIKAN_KAN_LAYER_COUNT][FRIKAN_MAX_LAYER_OUTPUTS];
        uint32_t layer_index;
        uint32_t output_index;

        for (layer_index = 0u; layer_index < FRIKAN_KAN_LAYER_COUNT; ++layer_index) {
            for (output_index = 0u; output_index < FRIKAN_MAX_LAYER_OUTPUTS; ++output_index) {
                step_kan_debug[layer_index][output_index] = 0.0f;
            }
        }

        frikan_forward_step(
            sequence[step][0u],
            x1,
            x2,
            y1,
            y2,
            debug_output_scaled_buffer != 0 ? &debug_output_scaled_buffer[step] : 0,
            debug_scaled_input_buffer != 0 ? &debug_scaled_input_buffer[step] : 0,
            debug_iir_output_buffer != 0 ? debug_iir_output_buffer[step] : 0,
            debug_kan_output_buffer != 0 ? step_kan_debug : 0,
            &output_sequence[step]
        );

        if (debug_kan_output_buffer != 0) {
            for (layer_index = 0u; layer_index < FRIKAN_KAN_LAYER_COUNT; ++layer_index) {
                for (output_index = 0u; output_index < FRIKAN_MAX_LAYER_OUTPUTS; ++output_index) {
                    debug_kan_output_buffer[layer_index][step][output_index] = step_kan_debug[layer_index][output_index];
                }
            }
        }
    }
}

static void run_benchmark_record(const port_float sequence[VALIDATION_SEQ_LEN][FRIKAN_INPUT_DIM],
                                 uint32_t reset_state_each_run,
                                 port_float x1[FRIKAN_FEATURES],
                                 port_float x2[FRIKAN_FEATURES],
                                 port_float y1[FRIKAN_FEATURES],
                                 port_float y2[FRIKAN_FEATURES],
                                 port_float *output_value)
{
    uint32_t step;
    port_float current_output = 0.0f;

    if (reset_state_each_run != 0u) {
        frikan_iir_reset(x1, x2, y1, y2);
    }

    for (step = 0u; step < VALIDATION_SEQ_LEN; ++step) {
        frikan_forward_step(
            sequence[step][0u],
            x1,
            x2,
            y1,
            y2,
            0,
            0,
            0,
            0,
            &current_output
        );
    }

    *output_value = current_output;
}

int main(void)
{
    uint32_t iteration;
    uint32_t record_index;
    uint32_t step_index;
    uint32_t layer_index;
    uint32_t dwt_supported;
    uint32_t start_cycles;
    uint32_t end_cycles;
    uint32_t total_cycles = 0u;
    port_float x1[FRIKAN_FEATURES];
    port_float x2[FRIKAN_FEATURES];
    port_float y1[FRIKAN_FEATURES];
    port_float y2[FRIKAN_FEATURES];
    port_float output_value = 0.0f;

    uart_init();
    dwt_supported = dwt_is_counting();
    frikan_iir_reset(x1, x2, y1, y2);

    if (dwt_supported != 0u) {
        start_cycles = dwt_read_cycles();
    }

    for (iteration = 0u; iteration < BENCHMARK_ITERATIONS; ++iteration) {
        for (record_index = 0u; record_index < VALIDATION_RECORD_COUNT; ++record_index) {
            run_benchmark_record(
                validation_input[record_index],
                BENCHMARK_RESET_STATE_EACH_RUN,
                x1,
                x2,
                y1,
                y2,
                &output_value
            );
        }
    }

    if (dwt_supported != 0u) {
        end_cycles = dwt_read_cycles();
        total_cycles = end_cycles - start_cycles;
    }

    uart_puts("FRIKAN_QEMU_VALIDATION\n");
    uart_puts("iterations=");
    uart_put_u32(BENCHMARK_ITERATIONS);
    uart_puts("\nrecord_count=");
    uart_put_u32(VALIDATION_RECORD_COUNT);
    uart_puts("\nseq_len=");
    uart_put_u32(VALIDATION_SEQ_LEN);
    uart_puts("\nfeature_count=");
    uart_put_u32(FRIKAN_FEATURES);
    uart_puts("\nkan_layer_count=");
    uart_put_u32(FRIKAN_KAN_LAYER_COUNT);
    uart_puts("\ndwt_supported=");
    uart_put_u32(dwt_supported);
    uart_puts("\ntimer_source=");
    uart_puts(dwt_supported != 0u ? "dwt" : "host_elapsed");
    if (dwt_supported != 0u) {
        uart_puts("\nmeasurement_unit=");
        uart_puts("cycles");
        uart_puts("\nmeasurement_total=");
        uart_put_u32(total_cycles);
        uart_puts("\nmeasurement_per_iter=");
        uart_put_u32(BENCHMARK_ITERATIONS == 0u ? 0u : (total_cycles / BENCHMARK_ITERATIONS));
        uart_puts("\ncycles_total=");
        uart_put_u32(total_cycles);
        uart_puts("\ncycles_per_iter=");
        uart_put_u32(BENCHMARK_ITERATIONS == 0u ? 0u : (total_cycles / BENCHMARK_ITERATIONS));
    }
    uart_puts("\noutput=");
    uart_put_fixed6(output_value);
    uart_puts("\n");
    uart_puts("benchmark_complete=1\n");

    for (record_index = 0u; record_index < VALIDATION_RECORD_COUNT; ++record_index) {
        frikan_iir_reset(x1, x2, y1, y2);
        run_validation_record(
            validation_input[record_index],
            validation_output[record_index],
            0u,
            x1,
            x2,
            y1,
            y2,
            debug_scaled_input,
            debug_iir_output,
            debug_kan_output,
            debug_output_scaled
        );
    }

    for (record_index = 0u; record_index < VALIDATION_RECORD_COUNT; ++record_index) {
        uart_puts("validation_record_");
        uart_put_u32(record_index);
        uart_puts("=");
        for (step_index = 0u; step_index < VALIDATION_SEQ_LEN; ++step_index) {
            if (step_index > 0u) {
                uart_putc(',');
            }
            uart_put_fixed6(validation_output[record_index][step_index]);
        }
        uart_puts("\n");

#if !defined(BENCHMARK_PLATFORM_KEIL)
        uart_puts("validation_input_scaled_");
        uart_put_u32(record_index);
        uart_puts("=");
        uart_put_matrix_rows(&debug_scaled_input[0u], VALIDATION_SEQ_LEN, 1u);
        uart_puts("\n");

        uart_puts("validation_iir_output_");
        uart_put_u32(record_index);
        uart_puts("=");
        uart_put_matrix_rows(&debug_iir_output[0u][0u], VALIDATION_SEQ_LEN, FRIKAN_FEATURES);
        uart_puts("\n");

        for (layer_index = 0u; layer_index < FRIKAN_KAN_LAYER_COUNT; ++layer_index) {
            uart_puts("validation_kan_layer_");
            uart_put_u32(layer_index);
            uart_putc('_');
            uart_put_u32(record_index);
            uart_puts("=");
            uart_put_matrix_rows(
                &debug_kan_output[layer_index][0u][0u],
                VALIDATION_SEQ_LEN,
                (uint32_t)frikan_layer_output_dims[layer_index]
            );
            uart_puts("\n");
        }

        uart_puts("validation_output_scaled_");
        uart_put_u32(record_index);
        uart_puts("=");
        uart_put_matrix_rows(&debug_output_scaled[0u], VALIDATION_SEQ_LEN, 1u);
        uart_puts("\n");
#endif
    }

    uart_puts("validation_complete=1\n");

    while (1) {
    }
}
"""
    lut_layer_function_lines: List[str] = []
    lut_layer_macro_lines: List[str] = []
    for layer_index, layer_spec in enumerate(model_spec.kan_layers):
        lut_scale, lut_offset = _compute_frikan_lut_index_params(
            layer_spec.lut_support_min,
            layer_spec.lut_support_max,
            model_spec.lut_points,
        )
        lut_layer_function_lines.extend([
            f'#define FRIKAN_LUT_SCALE_LAYER_{layer_index} {_format_c_float(lut_scale)}',
            f'#define FRIKAN_LUT_OFFSET_LAYER_{layer_index} {_format_c_float(lut_offset)}',
            '',
            f'static __attribute__((noinline)) port_float frikan_lut_lookup_fast_layer_{layer_index}(',
            '    const port_float lut_values[FRIKAN_LUT_POINTS],',
            '    port_float raw_value)',
            '{',
            '    port_float lookup_value = FRIKAN_LUT_PREPARE_VALUE(raw_value);',
            '    port_float mapped_index = FRIKAN_LUT_MAP_INDEX(',
            '        lookup_value,',
            f'        FRIKAN_LUT_SCALE_LAYER_{layer_index},',
            f'        FRIKAN_LUT_OFFSET_LAYER_{layer_index}',
            '    );',
            '    port_float result;',
            '',
            '    if ((mapped_index < 0.0f) || (mapped_index > FRIKAN_LUT_LAST_INDEX_FLOAT)) {',
            '        return 0.0f;',
            '    }',
            '',
            '    #if FRIKAN_LUT_INTERPOLATION',
            '    {',
            '        uint32_t lower_index = (uint32_t)mapped_index;',
            '        if (lower_index >= FRIKAN_LUT_LAST_INDEX) {',
            '            result = lut_values[FRIKAN_LUT_LAST_INDEX];',
            '        } else {',
            '            port_float frac = mapped_index - (port_float)lower_index;',
            '            port_float lower_value = lut_values[lower_index];',
            '            port_float upper_value = lut_values[lower_index + 1u];',
            '            result = lower_value + (upper_value - lower_value) * frac;',
            '        }',
            '    }',
            '    #else',
            '    result = lut_values[(uint32_t)mapped_index];',
            '    #endif',
            '',
            '    #if FRIKAN_USE_SYMMETRY && !FRIKAN_USE_EVEN',
            '    if (raw_value < 0.0f) {',
            '        result = -result;',
            '    }',
            '    #endif',
            '',
            '    return result;',
            '}',
            '',
        ])
        lut_layer_macro_lines.append(
            f'#define FRIKAN_LUT_LOOKUP_LAYER_{layer_index}(lut_values, raw_value) '
            f'frikan_lut_lookup_fast_layer_{layer_index}((lut_values), (raw_value))'
        )

    return (
        template
        .replace('__FRIKAN_LUT_LAYER_FUNCTIONS__', '\n'.join(lut_layer_function_lines))
        .replace('__FRIKAN_LUT_LAYER_MACROS__', '\n'.join(lut_layer_macro_lines))
        .replace('__FRIKAN_FORWARD_BODY__', _render_frikan_forward_body(model_spec))
    )

def _prepare_frikan_validation_artifacts(model_project_name: str,
                                        weights_json_path: Path,
                                        validation_config: Dict[str, Any],
                                        model_spec: FrikanModelSpec) -> common.ValidationArtifacts:
    from core.model_engine import ModelEngine
    from core.project_manager import ProjectManager

    project_path = common._normalize_project_path(model_project_name)
    project_manager = ProjectManager(project_path)
    common._apply_validation_dataset_overrides(project_manager.config, validation_config['dataset'])

    model_engine = ModelEngine(project_manager, checkpoint_dir=project_manager.checkpoint_dir)
    model_engine.load_dataset(project_manager.config.dataset_type)
    selected_dataset, time_window = common._select_validation_dataset(
        model_engine.dataset_origin,
        validation_config['selection'],
    )

    if project_manager.config.use_scale:
        if model_engine.load_scalers() is None or model_engine.scaler is None:
            raise FileNotFoundError(
                f'??????? scaler: {project_manager.checkpoint_dir}/scalers/combined_scaler.json'
            )

    x_input = selected_dataset.reshape2feature(selected_dataset.output_ori)

    input_data_range = 1.0
    output_data_range = 1.0
    if project_manager.config.use_scale:
        input_data_range = float(model_engine.scaler.scaler_x.data_range_)
        output_data_range = float(model_engine.scaler.scaler_y.data_range_)

    loaded_weights_path = common._resolve_reference_weights_path(weights_json_path)
    tf_output, tf_debug_sequences = _run_frikan_reference_from_spec(
        model_spec=model_spec,
        x_input=x_input,
        input_data_range=input_data_range,
        output_data_range=output_data_range,
        use_scaler=bool(project_manager.config.use_scale),
    )

    tf_output_2d = np.asarray(tf_output, dtype=np.float64).reshape(x_input.shape[0], x_input.shape[1])
    records = common._build_validation_records(selected_dataset, tf_output_2d)

    return common.ValidationArtifacts(
        dataset_type=str(project_manager.config.dataset_type),
        full_data_path=str(project_manager.config.full_data_path),
        sample_rate=float(selected_dataset.fs),
        time_window=time_window,
        input_data_range=input_data_range,
        output_data_range=output_data_range,
        loaded_weights_path=loaded_weights_path,
        records=records,
        tf_debug_sequences=tf_debug_sequences,
    )


def generate_frikan_qemu_project(output_dir: Path,
                                 model_spec: FrikanModelSpec,
                                 benchmark_config: Dict[str, Any],
                                 validation_artifacts: common.ValidationArtifacts,
                                 overwrite: bool) -> None:
    if output_dir.exists() and not overwrite:
        raise FileExistsError(f'QEMU ?????????????: {output_dir}')

    output_dir.mkdir(parents=True, exist_ok=True)
    common._copy_runtime_template('startup.c', output_dir / 'startup.c')
    common._copy_runtime_template('stm32f405.ld', output_dir / 'stm32f405.ld')

    main_c = common._make_dual_platform_benchmark_c(_render_frikan_main_c(model_spec))
    model_header = _render_frikan_model_data_header(model_spec, benchmark_config, validation_artifacts)
    common._write_text(output_dir / 'main.c', main_c)
    common._write_text(output_dir / 'model_data.h', model_header)


def execute_frikan_qemu_task(ep_path: ExternalPath, config: Dict[str, Any]) -> bool:
    ep_path.output_path.mkdir(parents=True, exist_ok=True)

    model_project_name = str(config['model_project_name']).replace('\\', '/')
    benchmark_config = common._normalize_benchmark_config(config.get('benchmark_config', {}))
    validation_config = common._normalize_validation_config(config.get('validation_config', {}))
    generation_config = config.get('generation_config', {})
    qemu_config = config.get('qemu_config', {})

    model_dir = common._resolve_model_project_dir(model_project_name)
    weights_json_path = common._resolve_weights_json_path(model_dir, config.get('weights_file'))
    model_spec = _load_frikan_model_spec(
        model_project_name=model_project_name,
        model_dir=model_dir,
        weights_json_path=weights_json_path,
        lut_points=int(generation_config.get('lut_points', 513)),
        lut_interpolation=bool(generation_config.get('lut_interpolation', False)),
    )

    validation_artifacts = _prepare_frikan_validation_artifacts(
        model_project_name=model_project_name,
        weights_json_path=weights_json_path,
        validation_config=validation_config,
        model_spec=model_spec,
    )

    generated_project_dir = common._resolve_generated_project_dir(ep_path, generation_config)
    overwrite = bool(generation_config.get('overwrite', True))
    generate_frikan_qemu_project(
        output_dir=generated_project_dir,
        model_spec=model_spec,
        benchmark_config=benchmark_config,
        validation_artifacts=validation_artifacts,
        overwrite=overwrite,
    )
    keil_project_dir = common.generate_keil_project(
        ep_path=ep_path,
        qemu_project_dir=generated_project_dir,
        overwrite=overwrite,
    )

    wave_paths = common._write_validation_wave_files(
        output_root=ep_path.output_path,
        validation_artifacts=validation_artifacts,
        c_output_sequences=None,
        compress=bool(validation_config['wave_output']['compress']),
        export_intermediates=bool(validation_config['wave_output'].get('export_intermediates', True)),
    )
    plot_paths: Dict[str, str] = {}

    execution_summary: Dict[str, Any] = {
        'task_type': 'qemu-c-inference',
        'model_type': 'frikan',
        'model_project_name': model_project_name,
        'weights_json_path': common._relative_or_str(weights_json_path),
        'loaded_weights_path': common._relative_or_str(validation_artifacts.loaded_weights_path),
        'generated_project_dir': common._relative_or_str(generated_project_dir),
        'keil_project_dir': common._relative_or_str(keil_project_dir),
        'benchmark_config': benchmark_config,
        'validation': {
            'dataset': {
                'dataset_type': validation_artifacts.dataset_type,
                'full_data_path': validation_artifacts.full_data_path,
                'sample_rate': validation_artifacts.sample_rate,
            },
            'selection': validation_artifacts.time_window,
            'record_count': validation_artifacts.record_count,
            'seq_len': validation_artifacts.seq_len,
        },
        'qemu_config': qemu_config,
        'wave_paths': wave_paths,
    }

    action = str(qemu_config.get('action', 'build-run'))
    machine = str(qemu_config.get('machine', 'olimex-stm32-h405'))
    timeout = int(qemu_config.get('timeout', 5))
    qemu_path = qemu_config.get('qemu_path')
    gcc_path = qemu_config.get('gcc_path')
    linker_script = qemu_config.get('linker_script')
    output_path = qemu_config.get('output')

    if action == 'generate':
        summary_path = ep_path.output_path / 'benchmark_summary.json'
        common._write_json(summary_path, {**execution_summary, 'action': 'generate', 'status': 'generated'})
        common._write_json(ep_path.output_path / 'task_metadata.json', {
            'task_info': config['task_info'],
            'output_files': common._collect_output_files(
                generated_project_dir,
                keil_project_dir,
                summary_path,
                *[Path(path) for path in wave_paths.values()],
            ),
            'action': 'generate',
        })
        logger.info('QEMU ?????: %s', generated_project_dir)
        return True

    run_results: List[Dict[str, Any]] = []
    build_result: Optional[Dict[str, Any]] = None
    first_c_output_sequences: Optional[List[List[float]]] = None
    first_c_debug_sequences: Dict[str, List[Any]] = {}
    validation_run_summary: Optional[Dict[str, Any]] = None

    if action in {'build', 'build-run'}:
        build_workflow = execute_qemu_workflow(
            action='build',
            project_dir=str(generated_project_dir),
            machine=machine,
            timeout=timeout,
            output_path=output_path,
            qemu_path_override=qemu_path,
            gcc_path_override=gcc_path,
            linker_script=linker_script,
        )
        build_result = build_workflow
        if int(build_workflow.get('exit_code', 1)) != 0:
            execution_summary['build'] = build_workflow
            common._write_json(ep_path.output_path / 'benchmark_summary.json', execution_summary)
            common._write_json(ep_path.output_path / 'task_metadata.json', {
                'task_info': config['task_info'],
                'output_files': common._collect_output_files(ep_path.output_path / 'benchmark_summary.json'),
                'action': action,
            })
            return False

    if action in {'run', 'build-run'}:
        repeat_runs = int(benchmark_config['repeat_runs'])
        for run_index in range(repeat_runs):
            run_workflow = execute_qemu_workflow(
                action='run',
                project_dir=str(generated_project_dir),
                machine=machine,
                timeout=timeout,
                output_path=output_path,
                qemu_path_override=qemu_path,
                gcc_path_override=gcc_path,
                linker_script=linker_script,
                success_patterns=['benchmark_complete=1'],
            )
            parsed_output = common._enrich_benchmark_output(
                common._parse_benchmark_stdout(str(run_workflow.get('run', {}).get('stdout', ''))),
                run_workflow,
                benchmark_config,
            )
            run_results.append({'run_index': run_index, 'workflow': run_workflow, 'parsed_output': parsed_output})
            if int(run_workflow.get('exit_code', 1)) != 0:
                execution_summary['build'] = build_result
                execution_summary['runs'] = run_results
                common._write_json(ep_path.output_path / 'benchmark_summary.json', execution_summary)
                common._write_json(ep_path.output_path / 'task_metadata.json', {
                    'task_info': config['task_info'],
                    'output_files': common._collect_output_files(ep_path.output_path / 'benchmark_summary.json'),
                    'action': action,
                })
                return False

        validation_workflow = execute_qemu_workflow(
            action='run',
            project_dir=str(generated_project_dir),
            machine=machine,
            timeout=timeout,
            output_path=output_path,
            qemu_path_override=qemu_path,
            gcc_path_override=gcc_path,
            linker_script=linker_script,
            success_patterns=['validation_complete=1'],
        )
        validation_parsed_output = common._enrich_benchmark_output(
            common._parse_benchmark_stdout(str(validation_workflow.get('run', {}).get('stdout', ''))),
            validation_workflow,
            benchmark_config,
        )
        c_output_sequences = common._extract_validation_outputs(validation_parsed_output, validation_artifacts)
        c_debug_sequences = common._extract_c_debug_sequences(validation_parsed_output, validation_artifacts)
        comparison_payload = common._compute_wave_comparison(validation_artifacts, c_output_sequences)
        intermediate_comparison = common._compute_intermediate_comparison(validation_artifacts, c_debug_sequences)
        first_c_output_sequences = c_output_sequences
        first_c_debug_sequences = c_debug_sequences
        validation_run_summary = {
            'workflow': common._summarize_qemu_run_workflow(validation_workflow),
            'parsed_output': common._summarize_parsed_output(validation_parsed_output),
            'comparison': comparison_payload['overall'],
            'intermediate_comparison': intermediate_comparison,
        }

        if int(validation_workflow.get('exit_code', 1)) != 0:
            execution_summary['build'] = build_result
            execution_summary['runs'] = run_results
            execution_summary['validation_run'] = validation_run_summary
            common._write_json(ep_path.output_path / 'benchmark_summary.json', execution_summary)
            common._write_json(ep_path.output_path / 'task_metadata.json', {
                'task_info': config['task_info'],
                'output_files': common._collect_output_files(ep_path.output_path / 'benchmark_summary.json'),
                'action': action,
            })
            return False

    execution_summary['build'] = build_result
    execution_summary['runs'] = run_results
    if run_results:
        execution_summary['aggregated'] = common._aggregate_run_results(run_results)
    if validation_run_summary is not None:
        execution_summary['validation_run'] = validation_run_summary

    comparison_file = ep_path.output_path / 'validation_comparison.json'
    if first_c_output_sequences is not None:
        wave_paths = common._write_validation_wave_files(
            output_root=ep_path.output_path,
            validation_artifacts=validation_artifacts,
            c_output_sequences=first_c_output_sequences,
            compress=bool(validation_config['wave_output']['compress']),
            export_intermediates=bool(validation_config['wave_output'].get('export_intermediates', True)),
            c_debug_sequences=first_c_debug_sequences,
        )
        if bool(validation_config['wave_output'].get('plot_comparison', True)):
            plot_paths = common._write_validation_comparison_plots(
                output_root=ep_path.output_path,
                validation_artifacts=validation_artifacts,
                c_output_sequences=first_c_output_sequences,
                dpi=int(validation_config['wave_output'].get('plot_dpi', 200)),
            )
        comparison_payload = common._compute_wave_comparison(validation_artifacts, first_c_output_sequences)
        comparison_payload['intermediate'] = common._compute_intermediate_comparison(validation_artifacts, first_c_debug_sequences)
        comparison_payload['wave_paths'] = wave_paths
        if plot_paths:
            comparison_payload['plot_paths'] = plot_paths
        common._write_json(comparison_file, comparison_payload)
        execution_summary['wave_paths'] = wave_paths
        if plot_paths:
            execution_summary['plot_paths'] = plot_paths
        execution_summary['comparison'] = comparison_payload['overall']
        execution_summary['comparison_path'] = common._relative_or_str(comparison_file)

    summary_path = ep_path.output_path / 'benchmark_summary.json'
    common._write_json(summary_path, execution_summary)
    common._write_json(ep_path.output_path / 'task_metadata.json', {
        'task_info': config['task_info'],
        'output_files': common._collect_output_files(
            summary_path,
            generated_project_dir,
            keil_project_dir,
            comparison_file,
            *[Path(path) for path in execution_summary.get('wave_paths', {}).values()],
            *[Path(path) for path in execution_summary.get('plot_paths', {}).values()],
        ),
        'action': action,
    })
    logger.info('QEMU C ??????: %s', summary_path)
    return True


def execute_frikan_keil_bench_task(ep_path: ExternalPath,
                                    config: Dict[str, Any],
                                    keil_overrides: Optional[Dict[str, Any]] = None) -> bool:
    ep_path.output_path.mkdir(parents=True, exist_ok=True)

    model_project_name = str(config['model_project_name']).replace('\\', '/')
    benchmark_config = common._normalize_benchmark_config(config.get('benchmark_config', {}))
    validation_config = common._normalize_validation_config(config.get('validation_config', {}))
    generation_config = config.get('generation_config', {})
    keil_config = common._normalize_keil_config(config.get('keil_config', {}), keil_overrides)

    model_dir = common._resolve_model_project_dir(model_project_name)
    weights_json_path = common._resolve_weights_json_path(model_dir, config.get('weights_file'))
    model_spec = _load_frikan_model_spec(
        model_project_name=model_project_name,
        model_dir=model_dir,
        weights_json_path=weights_json_path,
        lut_points=int(generation_config.get('lut_points', 513)),
        lut_interpolation=bool(generation_config.get('lut_interpolation', False)),
    )
    validation_artifacts = _prepare_frikan_validation_artifacts(
        model_project_name=model_project_name,
        weights_json_path=weights_json_path,
        validation_config=validation_config,
        model_spec=model_spec,
    )

    generated_project_dir = common._resolve_generated_project_dir(ep_path, generation_config)
    overwrite = bool(generation_config.get('overwrite', True))
    generate_frikan_qemu_project(
        output_dir=generated_project_dir,
        model_spec=model_spec,
        benchmark_config=benchmark_config,
        validation_artifacts=validation_artifacts,
        overwrite=overwrite,
    )
    keil_project_dir = common.generate_keil_project(
        ep_path=ep_path,
        qemu_project_dir=generated_project_dir,
        overwrite=overwrite,
    )

    wave_paths = common._write_validation_wave_files(
        output_root=ep_path.output_path,
        validation_artifacts=validation_artifacts,
        c_output_sequences=None,
        compress=bool(validation_config['wave_output']['compress']),
        export_intermediates=bool(validation_config['wave_output'].get('export_intermediates', True)),
    )

    keil_project_file = keil_project_dir / 'MDK-ARM' / common.KEIL_BENCHMARK_BASE_UVPROJX.name
    summary_path = ep_path.output_path / 'keil_benchmark_summary.json'
    comparison_path = ep_path.output_path / 'keil_validation_comparison.json'
    metadata_path = ep_path.output_path / 'keil_benchmark_metadata.json'

    execution_summary: Dict[str, Any] = {
        'task_type': 'qemu-c-inference',
        'action': 'keil-bench',
        'model_type': 'frikan',
        'model_project_name': model_project_name,
        'weights_json_path': common._relative_or_str(weights_json_path),
        'loaded_weights_path': common._relative_or_str(validation_artifacts.loaded_weights_path),
        'generated_project_dir': common._relative_or_str(generated_project_dir),
        'keil_project_dir': common._relative_or_str(keil_project_dir),
        'keil_project_file': common._relative_or_str(keil_project_file),
        'benchmark_config': benchmark_config,
        'validation': {
            'dataset': {
                'dataset_type': validation_artifacts.dataset_type,
                'full_data_path': validation_artifacts.full_data_path,
                'sample_rate': validation_artifacts.sample_rate,
            },
            'selection': validation_artifacts.time_window,
            'record_count': validation_artifacts.record_count,
            'seq_len': validation_artifacts.seq_len,
        },
        'keil_config': dict(keil_config),
        'wave_paths': wave_paths,
        'status': 'generated',
    }

    action = str(keil_config.get('action', 'build-program-capture'))
    if action == 'generate':
        common._write_json(summary_path, execution_summary)
        common._write_json(metadata_path, {
            'task_info': config['task_info'],
            'output_files': common._collect_output_files(
                summary_path, metadata_path, generated_project_dir, keil_project_dir, *[Path(path) for path in wave_paths.values()]
            ),
            'action': 'keil-bench',
        })
        logger.info('Keil benchmark ?????: %s', keil_project_dir)
        return True

    build_result = common._run_keil_build_job(project_file=keil_project_file, keil_config=keil_config)
    execution_summary['keil_build'] = build_result
    if not bool(build_result.get('success', False)):
        execution_summary['status'] = 'build_failed'
        common._write_json(summary_path, execution_summary)
        common._write_json(metadata_path, {
            'task_info': config['task_info'],
            'output_files': common._collect_output_files(summary_path, metadata_path),
            'action': 'keil-bench',
        })
        return False

    if action == 'build':
        execution_summary['status'] = 'build_completed'
        common._write_json(summary_path, execution_summary)
        common._write_json(metadata_path, {
            'task_info': config['task_info'],
            'output_files': common._collect_output_files(
                summary_path, metadata_path, generated_project_dir, keil_project_dir, *[Path(path) for path in wave_paths.values()]
            ),
            'action': 'keil-bench',
        })
        return True

    capture_state: Optional[Dict[str, Any]] = None
    capture_result: Optional[Dict[str, Any]] = None
    program_result: Optional[Dict[str, Any]] = None

    try:
        if action == 'build-program-capture':
            capture_state = common._start_keil_serial_capture(
                output_dir=ep_path.output_path,
                serial_port=str(keil_config['serial_port']),
                baud_rate=int(keil_config['baud_rate']),
                capture_timeout=int(keil_config['capture_timeout']),
                success_markers=keil_config['success_markers'],
            )

        program_result = common._run_keil_program_job(project_file=keil_project_file, keil_config=keil_config)
        execution_summary['keil_program'] = program_result
    finally:
        if capture_state is not None:
            capture_result = common._finish_keil_serial_capture(
                capture_state,
                timeout_seconds=int(keil_config['capture_timeout']) + 10,
            )
            execution_summary['serial_capture'] = capture_result

    if not bool(program_result and program_result.get('success', False)):
        execution_summary['status'] = 'program_failed'
        common._write_json(summary_path, execution_summary)
        common._write_json(metadata_path, {
            'task_info': config['task_info'],
            'output_files': common._collect_output_files(summary_path, metadata_path),
            'action': 'keil-bench',
        })
        return False

    if action == 'build-program':
        execution_summary['status'] = 'program_completed'
        common._write_json(summary_path, execution_summary)
        common._write_json(metadata_path, {
            'task_info': config['task_info'],
            'output_files': common._collect_output_files(summary_path, metadata_path),
            'action': 'keil-bench',
        })
        return True

    if capture_result is None:
        raise RuntimeError('????????')

    stream_text_path = Path(str(capture_result['text_path']))
    stream_text = stream_text_path.read_text(encoding='utf-8')
    parsed_output = common._parse_benchmark_stdout(stream_text)
    c_output_sequences = common._extract_validation_outputs(parsed_output, validation_artifacts)
    comparison_payload = common._compute_wave_comparison(validation_artifacts, c_output_sequences)
    keil_wave_path = ep_path.output_path / 'waves' / 'keil_output.wave'
    common._save_wave_file(
        keil_wave_path,
        source_name='keil_output',
        sequences=c_output_sequences,
        validation_artifacts=validation_artifacts,
        compress=bool(validation_config['wave_output']['compress']),
    )
    qemu_reference = common._load_qemu_reference_comparison(ep_path.output_path, c_output_sequences)

    comparison_payload['wave_paths'] = {'keil_output_wave': common._relative_or_str(keil_wave_path)}
    common._write_json(comparison_path, comparison_payload)

    execution_summary['status'] = 'completed'
    execution_summary['serial_capture'] = {
        **capture_result,
        'text_path': common._relative_or_str(Path(str(capture_result['text_path']))),
        'jsonl_path': common._relative_or_str(Path(str(capture_result['jsonl_path']))),
        'result_path': common._relative_or_str(Path(str(capture_result['result_path']))),
    }
    execution_summary['parsed_output'] = common._summarize_parsed_output(parsed_output)
    execution_summary['validation_outputs'] = {f'record_{index}': sequence for index, sequence in enumerate(c_output_sequences)}
    execution_summary['comparison'] = comparison_payload['overall']
    execution_summary['comparison_path'] = common._relative_or_str(comparison_path)
    execution_summary['keil_wave_paths'] = comparison_payload['wave_paths']
    if qemu_reference is not None:
        execution_summary['qemu_reference_comparison'] = qemu_reference

    common._write_json(summary_path, execution_summary)
    common._write_json(metadata_path, {
        'task_info': config['task_info'],
        'output_files': common._collect_output_files(
            summary_path, comparison_path, metadata_path, generated_project_dir, keil_project_dir, keil_wave_path, *[Path(path) for path in wave_paths.values()]
        ),
        'action': 'keil-bench',
    })
    logger.info('Keil benchmark ????: %s', summary_path)
    return True
