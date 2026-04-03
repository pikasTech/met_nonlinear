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
    'mul_weight': 1.0,
    'map_weight': 6.0,
    'basis': (
        'Estimated for STM32F405 (Cortex-M4F). Integer/fused pipeline add and '
        'multiply are treated as roughly single-issue baseline operations; '
        'MAP is treated as a heavier activation/LUT-style operation that '
        'typically includes indexing, memory access, and nonlinear evaluation '
        'overhead, so it is assigned 6 add-equivalent units by default.'
    ),
    'source_notes': [
        'STM32F405 uses an ARM Cortex-M4F core.',
        'Cortex-M4 integer ADD/MUL are commonly treated as near single-cycle baseline operations for rough estimation.',
        'Activation/MAP cost varies strongly with implementation; default MAP weight is a conservative heuristic and should be overridden with measured firmware data when available.',
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
        elif isinstance(layer, tf.keras.layers.Dense):
            layer_analysis = _analyze_dense_layer(layer)
        elif isinstance(layer, DenseKAN):
            layer_analysis = _analyze_densekan_layer(layer)
        elif isinstance(layer, tf.keras.layers.LSTM):
            layer_analysis = _analyze_lstm_layer(layer)
        elif isinstance(layer, tf.keras.layers.SimpleRNN):
            layer_analysis = _analyze_simple_rnn_layer(layer)
        elif isinstance(layer, (DIAGIIR, SIMOIIR)):
            layer_analysis = _analyze_iir_layer(layer)
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
        'totals': layer_analysis['totals'],
        'layers': layer_analysis['layers'],
        'unsupported_layers': layer_analysis['unsupported_layers'],
    }
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