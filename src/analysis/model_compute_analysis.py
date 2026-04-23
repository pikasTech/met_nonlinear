"""
模型单步推理计算量分析。

基于 TensorFlow/Keras 模型的真实层结构与权重张量形状，统计单个时间步
推理过程中的加法、乘法和 MAP 次数。
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

import numpy as np
import tensorflow as tf

from experimental.mimoiir import DIAGIIR, SIMOIIR
from tfkan.layers.dense import DenseKAN

logger = logging.getLogger(__name__)


DEFAULT_COST_MODEL = {
    'platform': 'stm32f405',
    'unit': 'add_equivalent',
    'add_weight': 1.0,
    'mul_weight': 3.0,
    'map_weight': 20.0,
    'basis': (
        'Calibrated for STM32F405 (Cortex-M4F) against measured board latency. '
        'The default add-normalized ratio is 1:3:20 for add:multiply:MAP, '
        'which provides a better fit than the previous heuristic 1:1:6.'
    ),
    'source_notes': [
        'STM32F405 uses an ARM Cortex-M4F core.',
        'The default ratio is calibrated from measured on-board latency of representative deployed models.',
        'The unconstrained fit tends to drive the add term toward negligible weight; the default 1:3:20 model keeps add normalized to 1 while remaining interpretable.',
        'MAP still represents the heaviest semantic operation because it bundles nonlinear evaluation and its surrounding indexing / memory-access overhead.',
    ],
}


def _shape_to_list(shape: Any) -> Optional[List[Optional[int]]]:
    """将 TensorShape 或元组转换为可 JSON 序列化的列表。"""
    if shape is None:
        return None
    if hasattr(shape, 'as_list'):
        return shape.as_list()
    if isinstance(shape, (list, tuple)):
        return [dim for dim in shape]
    return None


def _shape_product(shape: Any) -> Optional[int]:
    """计算形状中已知维度的乘积。"""
    dims = _shape_to_list(shape)
    if dims is None:
        return None

    product = 1
    has_known_dim = False
    for dim in dims:
        if dim is None:
            continue
        product *= int(dim)
        has_known_dim = True

    if not has_known_dim:
        return None
    return product


def _single_sample_timestep_elements(shape: Any) -> int:
    """估计单样本、单时间步下的输出元素数量。"""
    dims = _shape_to_list(shape)
    if dims is None:
        return 1

    relevant_dims = dims[2:] if len(dims) >= 3 else dims[1:]
    product = 1
    has_known_dim = False
    for dim in relevant_dims:
        if dim is None:
            continue
        product *= int(dim)
        has_known_dim = True

    if has_known_dim:
        return product
    return 1


def _convert_np_types(obj: Any) -> Any:
    """递归转换 NumPy 类型，确保 JSON 可序列化。"""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, np.generic):
        return obj.item()
    if isinstance(obj, dict):
        return {key: _convert_np_types(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [_convert_np_types(item) for item in obj]
    return obj


def _normalize_cost_model(cost_model: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """合并默认成本模型与外部覆盖配置。"""
    resolved = dict(DEFAULT_COST_MODEL)
    if cost_model:
        resolved.update({
            key: value for key, value in cost_model.items()
            if value is not None
        })
    resolved['add_weight'] = float(resolved['add_weight'])
    resolved['mul_weight'] = float(resolved['mul_weight'])
    resolved['map_weight'] = float(resolved['map_weight'])
    return resolved


def _estimate_weighted_cost(compute: Dict[str, Any],
                            cost_model: Dict[str, Any]) -> Dict[str, Any]:
    """按平台成本模型将运算次数转换为 add 等效耗时单位。"""
    weighted_units = {
        'additions': compute['additions'] * cost_model['add_weight'],
        'multiplications': compute['multiplications'] * cost_model['mul_weight'],
        'maps': compute['maps'] * cost_model['map_weight'],
    }
    total_units = sum(weighted_units.values())
    if total_units > 0:
        weighted_share_pct = {
            key: weighted_units[key] * 100.0 / total_units
            for key in weighted_units
        }
    else:
        weighted_share_pct = {
            'additions': 0.0,
            'multiplications': 0.0,
            'maps': 0.0,
        }

    return {
        'platform': cost_model['platform'],
        'unit': cost_model['unit'],
        'weights': {
            'additions': cost_model['add_weight'],
            'multiplications': cost_model['mul_weight'],
            'maps': cost_model['map_weight'],
        },
        'weighted_units': {
            **weighted_units,
            'total': total_units,
        },
        'weighted_share_pct': weighted_share_pct,
        'basis': cost_model.get('basis'),
        'source_notes': cost_model.get('source_notes', []),
    }


def _activation_name(activation: Any) -> str:
    """提取激活函数名称。"""
    if activation is None:
        return 'linear'
    if isinstance(activation, str):
        return activation
    return getattr(activation, '__name__', activation.__class__.__name__)


def _map_count_for_activation(activation_name: str, output_size: int) -> int:
    """非线性激活的每个输出元素计为一次 MAP。"""
    if activation_name in ('linear', None):
        return 0
    return output_size


def _base_layer_info(layer: tf.keras.layers.Layer) -> Dict[str, Any]:
    """提取层的通用信息。"""
    return {
        'name': layer.name,
        'type': layer.__class__.__name__,
        'trainable': layer.trainable,
        'input_shape': _shape_to_list(getattr(layer, 'input_shape', None)),
        'output_shape': _shape_to_list(getattr(layer, 'output_shape', None)),
        'num_params': int(layer.count_params()),
    }




def _analyze_dense_layer(layer: tf.keras.layers.Dense) -> Dict[str, Any]:
    """统计 Dense 层单次前向传播的运算量。"""
    kernel_shape = layer.kernel.shape.as_list()
    input_dim = int(kernel_shape[0])
    output_dim = int(kernel_shape[1])
    use_bias = bool(layer.use_bias)
    activation_name = _activation_name(layer.activation)

    multiplications = input_dim * output_dim
    additions = output_dim * ((input_dim - 1) + (1 if use_bias else 0))
    maps = _map_count_for_activation(activation_name, output_dim)

    return {
        'supported': True,
        'operation_scope': 'single_timestep_single_sample',
        'details': {
            'input_dim': input_dim,
            'output_dim': output_dim,
            'use_bias': use_bias,
            'activation': activation_name,
        },
        'compute': {
            'additions': additions,
            'multiplications': multiplications,
            'maps': maps,
            'total': additions + multiplications + maps,
        },
        'formula': (
            'Dense: output_dim * input_dim multiplications, '
            'output_dim * ((input_dim - 1) + bias) additions, '
            'nonlinear activation per output element counted as one MAP.'
        ),
    }


def _analyze_densekan_layer(layer: DenseKAN) -> Dict[str, Any]:
    """将 DenseKAN 视为 LUT 查找后的 KAN 激活求和。"""
    input_dim = int(layer.in_size)
    output_dim = int(layer.units)
    use_bias = bool(layer.use_bias)

    maps = input_dim * output_dim
    additions = output_dim * ((input_dim - 1) + (1 if use_bias else 0))
    multiplications = 0

    return {
        'supported': True,
        'operation_scope': 'single_timestep_single_sample',
        'details': {
            'input_dim': input_dim,
            'output_dim': output_dim,
            'use_bias': use_bias,
            'grid_size': int(layer.grid_size),
            'spline_order': int(layer.spline_order),
            'estimation_mode': 'lut_kan_activation',
        },
        'compute': {
            'additions': additions,
            'multiplications': multiplications,
            'maps': maps,
            'total': additions + multiplications + maps,
        },
        'formula': (
            'DenseKAN(LUT estimate): each input-to-output KAN activation is counted '
            'as one MAP, internal spline details are not expanded; output aggregation '
            'uses additions only, plus optional bias addition.'
        ),
    }


def _analyze_conv1d_layer(layer: tf.keras.layers.Conv1D) -> Dict[str, Any]:
    """统计 Conv1D 层单个输出时间步的运算量。"""
    kernel_shape = layer.kernel.shape.as_list()
    kernel_size = int(kernel_shape[0])
    input_channels_per_group = int(kernel_shape[1])
    output_channels = int(kernel_shape[2])
    groups = int(getattr(layer, 'groups', 1) or 1)
    input_channels = input_channels_per_group * groups
    receptive_field_size = kernel_size * input_channels_per_group
    use_bias = bool(layer.use_bias)
    activation_name = _activation_name(layer.activation)

    multiplications = receptive_field_size * output_channels
    additions = output_channels * max(receptive_field_size - 1, 0)
    if use_bias:
        additions += output_channels
    maps = _map_count_for_activation(activation_name, output_channels)

    return {
        'supported': True,
        'operation_scope': 'single_timestep_single_sample',
        'details': {
            'kernel_size': kernel_size,
            'input_channels': input_channels,
            'input_channels_per_group': input_channels_per_group,
            'output_channels': output_channels,
            'groups': groups,
            'strides': int(layer.strides[0]),
            'dilation_rate': int(layer.dilation_rate[0]),
            'padding': layer.padding,
            'use_bias': use_bias,
            'activation': activation_name,
        },
        'compute': {
            'additions': additions,
            'multiplications': multiplications,
            'maps': maps,
            'total': additions + multiplications + maps,
        },
        'formula': (
            'Conv1D(single output timestep): each output channel computes one '
            'kernel_size * in_channels_per_group dot product, so the layer uses '
            'kernel_size * in_channels_per_group * output_channels '
            'multiplications and output_channels * '
            '((kernel_size * in_channels_per_group - 1) + bias) additions; '
            'nonlinear activation per output element counts as one MAP.'
        ),
    }


def _analyze_activation_layer(layer: tf.keras.layers.Activation) -> Dict[str, Any]:
    """统计显式 Activation 层的单时间步运算量。"""
    activation_name = _activation_name(layer.activation)
    output_elements = _single_sample_timestep_elements(getattr(layer, 'output_shape', None))
    maps = _map_count_for_activation(activation_name, output_elements)

    return {
        'supported': True,
        'operation_scope': 'single_timestep_single_sample',
        'details': {
            'activation': activation_name,
            'output_elements': output_elements,
        },
        'compute': {
            'additions': 0,
            'multiplications': 0,
            'maps': maps,
            'total': maps,
        },
        'formula': (
            'Activation(single timestep): linear activation costs 0; each '
            'nonlinear output element is counted as one MAP.'
        ),
    }


def _analyze_concatenate_layer(layer: tf.keras.layers.Concatenate) -> Dict[str, Any]:
    """拼接层只重排通道，不引入算术运算。"""
    output_elements = _single_sample_timestep_elements(getattr(layer, 'output_shape', None))

    return {
        'supported': True,
        'operation_scope': 'single_timestep_single_sample',
        'details': {
            'axis': int(layer.axis),
            'output_elements': output_elements,
            'reason': 'tensor_concatenation',
        },
        'compute': {
            'additions': 0,
            'multiplications': 0,
            'maps': 0,
            'total': 0,
        },
        'formula': 'Concatenate only reorders tensor views for this arithmetic estimate, so no arithmetic ops are counted.',
    }


def _analyze_lstm_layer(layer: tf.keras.layers.LSTM) -> Dict[str, Any]:
    """统计 Keras LSTM 层单时间步的运算量。"""
    kernel_shape = layer.cell.kernel.shape.as_list()
    recurrent_shape = layer.cell.recurrent_kernel.shape.as_list()
    input_dim = int(kernel_shape[0])
    units = int(layer.units)
    recurrent_units = int(recurrent_shape[0])
    bias_shape = None
    if getattr(layer.cell, 'bias', None) is not None:
        bias_shape = layer.cell.bias.shape.as_list()

    recurrent_activation = _activation_name(layer.recurrent_activation)
    activation_name = _activation_name(layer.activation)

    gate_outputs = 4 * units
    multiplications = gate_outputs * input_dim
    multiplications += gate_outputs * recurrent_units
    multiplications += 3 * units

    additions = gate_outputs * ((input_dim - 1) + (recurrent_units - 1))
    if bias_shape is not None:
        additions += gate_outputs * 2
    else:
        additions += gate_outputs
    additions += units

    maps = units * 3
    maps += units * 2

    return {
        'supported': True,
        'operation_scope': 'single_timestep_single_sample',
        'details': {
            'input_dim': input_dim,
            'units': units,
            'return_sequences': bool(layer.return_sequences),
            'use_bias': bias_shape is not None,
            'activation': activation_name,
            'recurrent_activation': recurrent_activation,
            'kernel_shape': kernel_shape,
            'recurrent_kernel_shape': recurrent_shape,
            'bias_shape': bias_shape,
        },
        'compute': {
            'additions': additions,
            'multiplications': multiplications,
            'maps': maps,
            'total': additions + multiplications + maps,
        },
        'formula': (
            'LSTM(single timestep): 4 gates for input/recurrent affine transforms, '
            'cell update f*c_prev + i*g contributes 2 multiplications + 1 addition '
            'per unit, hidden update o*activation(c_t) contributes 1 multiplication '
            'per unit, MAP counts 3 recurrent activations + 2 main activations per unit.'
        ),
    }
def _analyze_gru_layer(layer: tf.keras.layers.GRU) -> Dict[str, Any]:
    """统计 Keras GRU 层单时间步的运算量。"""
    kernel_shape = layer.cell.kernel.shape.as_list()
    recurrent_shape = layer.cell.recurrent_kernel.shape.as_list()
    input_dim = int(kernel_shape[0])
    units = int(layer.units)
    recurrent_units = int(recurrent_shape[0])
    bias_shape = None
    if getattr(layer.cell, 'bias', None) is not None:
        bias_shape = layer.cell.bias.shape.as_list()

    recurrent_activation = _activation_name(layer.recurrent_activation)
    activation_name = _activation_name(layer.activation)

    gate_outputs = 3 * units
    multiplications = gate_outputs * input_dim
    multiplications += gate_outputs * recurrent_units
    multiplications += 3 * units

    additions = gate_outputs * ((input_dim - 1) + (recurrent_units - 1))
    if bias_shape is not None:
        if len(bias_shape) > 1:
            additions += gate_outputs * int(bias_shape[0])
        else:
            additions += gate_outputs
    additions += 5 * units

    maps = units * 3

    return {
        'supported': True,
        'operation_scope': 'single_timestep_single_sample',
        'details': {
            'input_dim': input_dim,
            'units': units,
            'return_sequences': bool(layer.return_sequences),
            'use_bias': bias_shape is not None,
            'activation': activation_name,
            'recurrent_activation': recurrent_activation,
            'kernel_shape': kernel_shape,
            'recurrent_kernel_shape': recurrent_shape,
            'bias_shape': bias_shape,
            'reset_after': bool(getattr(layer, 'reset_after', False)),
        },
        'compute': {
            'additions': additions,
            'multiplications': multiplications,
            'maps': maps,
            'total': additions + multiplications + maps,
        },
        'formula': (
            'GRU(single timestep): 3 gates for input/recurrent affine transforms, '
            'reset gate modulation contributes 1 multiplication per unit, final '
            'state blend contributes 2 multiplications + 2 additions per unit, '
            'and recurrent activations count as 2 sigmoid + 1 main activation '
            'per unit.'
        ),
    }


def _analyze_iir_layer(layer: tf.keras.layers.Layer) -> Dict[str, Any]:
    """按二阶 IIR 直接型估计自定义 IIR 层的单步计算量。"""
    units = int(layer.units)
    multiplications_per_unit = 5
    additions_per_unit = 4

    multiplications = units * multiplications_per_unit
    additions = units * additions_per_unit

    return {
        'supported': True,
        'operation_scope': 'single_timestep_single_sample',
        'details': {
            'units': units,
            'estimation_mode': 'second_order_iir',
            'difference_equation': (
                'y[n] = -a1*y[n-1] - a2*y[n-2] + '
                'b0*x[n] + b1*x[n-1] + b2*x[n-2]'
            ),
        },
        'compute': {
            'additions': additions,
            'multiplications': multiplications,
            'maps': 0,
            'total': additions + multiplications,
        },
        'formula': (
            'Second-order IIR per channel: 5 multiplications and 4 additions per '
            'timestep. Total counts scale linearly with the number of channels.'
        ),
    }


def _analyze_simple_rnn_layer(layer: tf.keras.layers.SimpleRNN) -> Dict[str, Any]:
    """统计 SimpleRNN 层单时间步的运算量。"""
    kernel_shape = layer.cell.kernel.shape.as_list()
    recurrent_shape = layer.cell.recurrent_kernel.shape.as_list()
    input_dim = int(kernel_shape[0])
    units = int(layer.units)
    recurrent_units = int(recurrent_shape[0])
    use_bias = getattr(layer.cell, 'bias', None) is not None
    activation_name = _activation_name(layer.activation)

    multiplications = units * input_dim + units * recurrent_units
    additions = units * ((input_dim - 1) + (recurrent_units - 1))
    additions += units * (2 if use_bias else 1)
    maps = _map_count_for_activation(activation_name, units)

    return {
        'supported': True,
        'operation_scope': 'single_timestep_single_sample',
        'details': {
            'input_dim': input_dim,
            'units': units,
            'use_bias': use_bias,
            'activation': activation_name,
        },
        'compute': {
            'additions': additions,
            'multiplications': multiplications,
            'maps': maps,
            'total': additions + multiplications + maps,
        },
        'formula': (
            'SimpleRNN: one input affine term and one recurrent affine term per unit, '
            'plus one nonlinear activation per output element.'
        ),
    }


def _analyze_average_pooling1d_layer(
        layer: tf.keras.layers.AveragePooling1D) -> Dict[str, Any]:
    """统计 AveragePooling1D 单个输出时间步的运算量。"""
    input_shape = _shape_to_list(getattr(layer, 'input_shape', None)) or []
    channels = int(input_shape[-1]) if input_shape and input_shape[-1] is not None else 1
    pool_size_raw = layer.pool_size
    pool_size = int(pool_size_raw[0] if isinstance(pool_size_raw, (list, tuple)) else pool_size_raw)

    additions = channels * max(pool_size - 1, 0)
    multiplications = channels if pool_size > 1 else 0

    return {
        'supported': True,
        'operation_scope': 'single_timestep_single_sample',
        'details': {
            'channels': channels,
            'pool_size': pool_size,
            'strides': int(layer.strides[0] if isinstance(layer.strides, (list, tuple)) else layer.strides),
            'padding': layer.padding,
        },
        'compute': {
            'additions': additions,
            'multiplications': multiplications,
            'maps': 0,
            'total': additions + multiplications,
        },
        'formula': (
            'AveragePooling1D(single output timestep): each channel sums pool_size '
            'samples and multiplies once by the reciprocal average factor.'
        ),
    }


def _analyze_layer_normalization_layer(
        layer: tf.keras.layers.LayerNormalization) -> Dict[str, Any]:
    """统计 LayerNormalization 单时间步的运算量。"""
    normalized_size = _shape_product(getattr(layer, 'gamma', None).shape) if getattr(layer, 'gamma', None) is not None else None
    if normalized_size is None:
        normalized_size = _shape_product(getattr(layer, 'beta', None).shape) if getattr(layer, 'beta', None) is not None else None
    if normalized_size is None:
        normalized_size = _single_sample_timestep_elements(getattr(layer, 'input_shape', None))

    additions = max(normalized_size - 1, 0)
    additions += normalized_size
    additions += max(normalized_size - 1, 0)
    additions += 1
    if layer.center:
        additions += normalized_size

    multiplications = 1
    multiplications += normalized_size
    multiplications += normalized_size
    if layer.scale:
        multiplications += normalized_size

    return {
        'supported': True,
        'operation_scope': 'single_timestep_single_sample',
        'details': {
            'normalized_size': normalized_size,
            'epsilon': float(layer.epsilon),
            'center': bool(layer.center),
            'scale': bool(layer.scale),
            'axis': list(layer.axis) if isinstance(layer.axis, (list, tuple)) else [int(layer.axis)],
        },
        'compute': {
            'additions': additions,
            'multiplications': multiplications,
            'maps': 1,
            'total': additions + multiplications + 1,
        },
        'formula': (
            'LayerNormalization(single timestep): estimate mean/variance reduction '
            'over the normalized feature vector, one rsqrt-style MAP, then '
            'elementwise normalization with optional scale and bias.'
        ),
    }


def _analyze_multi_head_attention_layer(
        layer: tf.keras.layers.MultiHeadAttention) -> Dict[str, Any]:
    """统计单查询、单上下文 token 的 MultiHeadAttention 运算量。"""
    query_kernel_shape = layer._query_dense.kernel.shape.as_list()
    key_kernel_shape = layer._key_dense.kernel.shape.as_list()
    value_kernel_shape = layer._value_dense.kernel.shape.as_list()
    output_kernel_shape = layer._output_dense.kernel.shape.as_list()

    query_dim = int(query_kernel_shape[0])
    context_dim = int(key_kernel_shape[0])
    num_heads = int(query_kernel_shape[1])
    key_dim = int(query_kernel_shape[2])
    value_dim = int(value_kernel_shape[2])
    output_dim = int(output_kernel_shape[2])

    projected_query_dim = num_heads * key_dim
    projected_value_dim = num_heads * value_dim

    use_query_bias = getattr(layer._query_dense, 'bias', None) is not None
    use_key_bias = getattr(layer._key_dense, 'bias', None) is not None
    use_value_bias = getattr(layer._value_dense, 'bias', None) is not None
    use_output_bias = getattr(layer._output_dense, 'bias', None) is not None

    multiplications = query_dim * projected_query_dim
    multiplications += context_dim * projected_query_dim
    multiplications += context_dim * projected_value_dim
    multiplications += num_heads * key_dim
    multiplications += num_heads
    multiplications += projected_value_dim
    multiplications += projected_value_dim * output_dim

    additions = projected_query_dim * max(query_dim - 1, 0)
    additions += projected_query_dim * max(context_dim - 1, 0)
    additions += projected_value_dim * max(context_dim - 1, 0)
    additions += num_heads * max(key_dim - 1, 0)
    additions += output_dim * max(projected_value_dim - 1, 0)

    if use_query_bias:
        additions += projected_query_dim
    if use_key_bias:
        additions += projected_query_dim
    if use_value_bias:
        additions += projected_value_dim
    if use_output_bias:
        additions += output_dim

    maps = num_heads

    return {
        'supported': True,
        'operation_scope': 'single_timestep_single_sample',
        'details': {
            'query_dim': query_dim,
            'context_dim': context_dim,
            'num_heads': num_heads,
            'key_dim': key_dim,
            'value_dim': value_dim,
            'output_dim': output_dim,
            'query_kernel_shape': query_kernel_shape,
            'key_kernel_shape': key_kernel_shape,
            'value_kernel_shape': value_kernel_shape,
            'output_kernel_shape': output_kernel_shape,
        },
        'compute': {
            'additions': additions,
            'multiplications': multiplications,
            'maps': maps,
            'total': additions + multiplications + maps,
        },
        'formula': (
            'MultiHeadAttention(single timestep estimate): one query token and one '
            'context token are projected to Q/K/V, per-head dot product and '
            'single-score softmax are applied, then the attended value is '
            'projected back to the output dimension.'
        ),
    }


def _analyze_tfoplambda_add_layer(layer: tf.keras.layers.Layer) -> Dict[str, Any]:
    """统计 Keras 图中由 TFOpLambda 表示的逐元素加法。"""
    output_elements = _single_sample_timestep_elements(getattr(layer, 'output_shape', None))

    return {
        'supported': True,
        'operation_scope': 'single_timestep_single_sample',
        'details': {
            'reason': 'elementwise_add',
            'output_elements': output_elements,
        },
        'compute': {
            'additions': output_elements,
            'multiplications': 0,
            'maps': 0,
            'total': output_elements,
        },
        'formula': 'Elementwise residual add: one addition per output element.',
    }


def _supports_tfoplambda_layer(layer: tf.keras.layers.Layer) -> bool:
    """识别当前已覆盖的 TFOpLambda 算子。"""
    if layer.__class__.__name__ != 'TFOpLambda':
        return False
    return layer.name.startswith('tf.__operators__.add')


def _unsupported_layer_analysis(layer: tf.keras.layers.Layer) -> Dict[str, Any]:
    """生成不支持层的占位分析结果。"""
    return {
        'supported': False,
        'operation_scope': 'single_timestep_single_sample',
        'details': {
            'reason': 'unsupported_layer_type',
        },
        'compute': {
            'additions': 0,
            'multiplications': 0,
            'maps': 0,
            'total': 0,
        },
        'formula': 'No compute formula is implemented for this layer type yet.',
    }


def _analyze_layers(layers: List[tf.keras.layers.Layer],
                    cost_model: Dict[str, Any]) -> Dict[str, Any]:
    """分析一组层并汇总计算量。"""
    layer_entries: List[Dict[str, Any]] = []
    totals = {
        'additions': 0,
        'multiplications': 0,
        'maps': 0,
        'total': 0,
    }
    unsupported_layers: List[str] = []

    for layer in layers:
        base_info = _base_layer_info(layer)

        if isinstance(layer, tf.keras.layers.InputLayer):
            layer_analysis = {
                'supported': True,
                'operation_scope': 'single_timestep_single_sample',
                'details': {'reason': 'input_layer'},
                'compute': {
                    'additions': 0,
                    'multiplications': 0,
                    'maps': 0,
                    'total': 0,
                },
                'formula': 'Input layer does not perform arithmetic operations.',
            }
        elif isinstance(layer, tf.keras.layers.Dropout):
            layer_analysis = {
                'supported': True,
                'operation_scope': 'single_timestep_single_sample',
                'details': {'reason': 'dropout_inactive_in_inference'},
                'compute': {
                    'additions': 0,
                    'multiplications': 0,
                    'maps': 0,
                    'total': 0,
                },
                'formula': 'Dropout is inactive during inference.',
            }
        elif isinstance(layer, tf.keras.layers.Activation):
            layer_analysis = _analyze_activation_layer(layer)
        elif isinstance(layer, tf.keras.layers.Concatenate):
            layer_analysis = _analyze_concatenate_layer(layer)
        elif isinstance(layer, tf.keras.layers.Conv1D):
            layer_analysis = _analyze_conv1d_layer(layer)
        elif isinstance(layer, tf.keras.layers.Dense):
            layer_analysis = _analyze_dense_layer(layer)
        elif isinstance(layer, DenseKAN):
            layer_analysis = _analyze_densekan_layer(layer)
        elif isinstance(layer, tf.keras.layers.LSTM):
            layer_analysis = _analyze_lstm_layer(layer)
        elif isinstance(layer, tf.keras.layers.GRU):
            layer_analysis = _analyze_gru_layer(layer)
        elif isinstance(layer, tf.keras.layers.SimpleRNN):
            layer_analysis = _analyze_simple_rnn_layer(layer)
        elif isinstance(layer, tf.keras.layers.AveragePooling1D):
            layer_analysis = _analyze_average_pooling1d_layer(layer)
        elif isinstance(layer, tf.keras.layers.LayerNormalization):
            layer_analysis = _analyze_layer_normalization_layer(layer)
        elif isinstance(layer, tf.keras.layers.MultiHeadAttention):
            layer_analysis = _analyze_multi_head_attention_layer(layer)
        elif isinstance(layer, (DIAGIIR, SIMOIIR)):
            layer_analysis = _analyze_iir_layer(layer)
        elif _supports_tfoplambda_layer(layer):
            layer_analysis = _analyze_tfoplambda_add_layer(layer)
        else:
            layer_analysis = _unsupported_layer_analysis(layer)
            unsupported_layers.append(layer.name)

        compute = layer_analysis['compute']
        weighted_cost = _estimate_weighted_cost(compute, cost_model)
        totals['additions'] += compute['additions']
        totals['multiplications'] += compute['multiplications']
        totals['maps'] += compute['maps']
        totals['total'] += compute['total']

        layer_entries.append({
            **base_info,
            **layer_analysis,
            'estimated_cost': weighted_cost,
        })

    return {
        'totals': totals,
        'layers': layer_entries,
        'unsupported_layers': unsupported_layers,
        'unsupported_layer_details': [
            {
                'name': layer['name'],
                'type': layer['type'],
                'reason': (layer.get('details') or {}).get('reason', 'unsupported_layer_type'),
            }
            for layer in layer_entries
            if not layer.get('supported', False)
        ],
    }


def analyze_model_compute(model: tf.keras.Model,
                          model_type: Optional[str] = None,
                          cost_model: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """分析 TensorFlow 模型单时间步推理的计算量。"""
    resolved_cost_model = _normalize_cost_model(cost_model)
    layer_analysis = _analyze_layers(model.layers, resolved_cost_model)

    trainable_params = int(np.sum([np.prod(var.shape)
                                   for var in model.trainable_variables]))
    total_params = int(model.count_params())
    non_trainable_params = total_params - trainable_params

    analysis = {
        'analysis_type': 'single_timestep_inference_compute',
        'analysis_method': (
            'Counts are derived from TensorFlow/Keras layer classes, actual '
            'weight tensor shapes, and layer parameter counts.'
        ),
        'model_type': model_type,
        'input_shape': _shape_to_list(model.input_shape),
        'output_shape': _shape_to_list(model.output_shape),
        'total_params': total_params,
        'trainable_params': trainable_params,
        'non_trainable_params': non_trainable_params,
        'assumptions': {
            'batch_size': 1,
            'time_steps': 1,
            'dropout_active': False,
            'maps_definition': 'Each nonlinear activation evaluation counts as one MAP.',
        },
        'analysis_target': 'keras_model',
        'platform_cost_model': resolved_cost_model,
        'estimated_cost': _estimate_weighted_cost(
            layer_analysis['totals'],
            resolved_cost_model,
        ),
        'estimate_status': 'partial' if layer_analysis['unsupported_layers'] else 'complete',
        'totals': layer_analysis['totals'],
        'layers': layer_analysis['layers'],
        'unsupported_layers': layer_analysis['unsupported_layers'],
        'has_unsupported_layers': bool(layer_analysis['unsupported_layers']),
        'unsupported_layer_count': len(layer_analysis['unsupported_layers']),
        'unsupported_layer_details': layer_analysis['unsupported_layer_details'],
    }
    if analysis['has_unsupported_layers']:
        unsupported_names = ', '.join(analysis['unsupported_layers'][:5])
        if analysis['unsupported_layer_count'] > 5:
            unsupported_names += ', ...'
        analysis['estimate_warning'] = (
            'Compute cost may be underestimated because unsupported layers were '
            f'detected: {unsupported_names}.'
        )
    else:
        analysis['estimate_warning'] = None
    return _convert_np_types(analysis)


def analyze_model_component(model_component: Any,
                            model_type: Optional[str] = None,
                            cost_model: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """分析模型组件，统一按模型语义结构统计，不区分 fast 开关。"""
    if isinstance(model_component, tf.keras.Model):
        return analyze_model_compute(
            model_component,
            model_type=model_type,
            cost_model=cost_model,
        )

    fast_model = getattr(model_component, 'fast_model', None)
    fast_iir = getattr(model_component, 'fast_iir', None)
    main_model = getattr(model_component, 'model', None)

    if main_model is not None:
        analysis = analyze_model_compute(
            main_model,
            model_type=model_type,
            cost_model=cost_model,
        )
        if fast_model is not None or fast_iir is not None:
            analysis['analysis_target'] = 'model_semantics'
            analysis['assumptions']['fast_mode_equivalence'] = (
                'Fast IIR / fast model only change implementation form; compute '
                'counts are estimated to be identical to the non-fast semantic model.'
            )
            analysis['deployment_path'] = {
                'fast_model_present': fast_model is not None,
                'fast_iir_present': fast_iir is not None,
            }
        return analysis

    raise TypeError('Unsupported model component for compute analysis.')


def save_model_compute_analysis(model: Any,
                                output_path: str,
                                model_type: Optional[str] = None,
                                cost_model: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """分析模型并保存为 JSON 文件。"""
    analysis = analyze_model_component(
        model,
        model_type=model_type,
        cost_model=cost_model,
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as file_obj:
        json.dump(analysis, file_obj, indent=4, ensure_ascii=False)
    logger.info(f'模型计算量分析已保存到: {output_path}')
    return analysis
