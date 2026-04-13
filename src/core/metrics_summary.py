"""项目指标汇总导出工具。"""

from __future__ import annotations

import json
import math
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


def _load_json_if_exists(file_path: str) -> Optional[Dict[str, Any]]:
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def _to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _calculate_median(values: List[float]) -> Optional[float]:
    if not values:
        return None
    sorted_values = sorted(values)
    middle = len(sorted_values) // 2
    if len(sorted_values) % 2 == 1:
        return sorted_values[middle]
    return (sorted_values[middle - 1] + sorted_values[middle]) / 2.0


def _calculate_drift(metric: Dict[str, float]) -> float:
    median = metric['median']
    return max(abs(metric['max'] - median), abs(median - metric['min']))


def _build_distribution_metric(
    values: List[float],
    unit: str,
    method: str,
    extra: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    if not values:
        return None

    metric: Dict[str, Any] = {
        'min': min(values),
        'max': max(values),
        'median': _calculate_median(values),
        'count': len(values),
        'unit': unit,
        'method': method,
    }
    if metric['median'] is None:
        return None

    metric['drift'] = _calculate_drift(metric)
    if extra:
        metric.update(extra)
    return metric


def _interpolate_value(x_values: List[float], y_values: List[float], target_x: float) -> Optional[float]:
    if len(x_values) != len(y_values) or not x_values:
        return None
    if len(x_values) == 1:
        return y_values[0]
    if target_x <= x_values[0]:
        return y_values[0]
    if target_x >= x_values[-1]:
        return y_values[-1]

    for idx in range(1, len(x_values)):
        left_x = x_values[idx - 1]
        right_x = x_values[idx]
        if target_x <= right_x:
            left_y = y_values[idx - 1]
            right_y = y_values[idx]
            if right_x == left_x:
                return right_y
            ratio = (target_x - left_x) / (right_x - left_x)
            return left_y + ratio * (right_y - left_y)
    return y_values[-1]


def _extract_natural_frequency_values(
    linear_response: Optional[Dict[str, Any]],
    use_origin: bool,
) -> List[float]:
    if not linear_response:
        return []

    fit_params_key = 'fit_params_origin' if use_origin else 'fit_params_comped'
    fit_params = linear_response.get(fit_params_key) or []
    values: List[float] = []
    for params in fit_params:
        if not isinstance(params, list) or len(params) < 3:
            continue
        b_value = _to_float(params[1])
        if b_value is None or b_value <= 0:
            continue
        values.append(math.sqrt(b_value) / (2.0 * math.pi))
    return values


def _extract_sensitivity_values(
    linear_response: Optional[Dict[str, Any]],
    use_origin: bool,
    frequency_hz: float,
) -> List[float]:
    if not linear_response:
        return []

    frequencies_raw = linear_response.get('frequencies') or []
    gain_key = 'gains_origin' if use_origin else 'gains_comped'
    gains_raw = linear_response.get(gain_key) or linear_response.get('gains_compensated') or []

    frequencies = [_to_float(freq) for freq in frequencies_raw]
    if any(freq is None for freq in frequencies):
        return []

    values: List[float] = []
    for gain_curve in gains_raw:
        if not isinstance(gain_curve, list):
            continue
        gain_values = [_to_float(value) for value in gain_curve]
        if any(value is None for value in gain_values):
            continue
        if len(gain_values) != len(frequencies):
            continue
        interpolated = _interpolate_value(frequencies, gain_values, frequency_hz)
        if interpolated is not None:
            values.append(interpolated)
    return values


def _extract_linearity_values(
    linearity_by_frequency: Optional[Dict[str, Any]],
    use_origin: bool,
) -> List[float]:
    if not linearity_by_frequency:
        return []

    key = 'r_squared_origin' if use_origin else 'r_squared_comped'
    values: List[float] = []
    for item in linearity_by_frequency.get('linearity_by_frequency') or []:
        if not isinstance(item, dict):
            continue
        r_squared = _to_float(item.get(key))
        if r_squared is None:
            continue
        values.append(1.0 - r_squared)
    return values


def _build_linearity_metric(
    linearity_by_frequency: Optional[Dict[str, Any]],
    use_origin: bool,
) -> Optional[Dict[str, Any]]:
    nonlinearity_values = _extract_linearity_values(linearity_by_frequency, use_origin)
    if not nonlinearity_values:
        return None

    mean_value = sum(nonlinearity_values) / len(nonlinearity_values)
    return {
        'mean': mean_value * 100.0,
        'max': max(nonlinearity_values) * 100.0,
        'min': min(nonlinearity_values) * 100.0,
        'count': len(nonlinearity_values),
        'unit': '%',
        'method': 'mean(1 - R^2) across frequency points',
    }


def _build_metric_details(
    linear_response: Optional[Dict[str, Any]],
    linearity_by_frequency: Optional[Dict[str, Any]],
    sensitivity_frequency_hz: float = 100.0,
) -> Dict[str, Optional[Dict[str, Any]]]:
    natural_frequency_drift = _build_distribution_metric(
        _extract_natural_frequency_values(linear_response, use_origin=False),
        unit='Hz',
        method='max(|max-median|, |median-min|) from fn_comped',
    )
    natural_frequency_drift_origin = _build_distribution_metric(
        _extract_natural_frequency_values(linear_response, use_origin=True),
        unit='Hz',
        method='max(|max-median|, |median-min|) from fn_origin',
    )
    sensitivity_drift = _build_distribution_metric(
        _extract_sensitivity_values(linear_response, use_origin=False, frequency_hz=sensitivity_frequency_hz),
        unit='%',
        method='max(|max-median|, |median-min|) from interpolated sensitivity',
        extra={'frequency_hz': sensitivity_frequency_hz},
    )
    sensitivity_drift_origin = _build_distribution_metric(
        _extract_sensitivity_values(linear_response, use_origin=True, frequency_hz=sensitivity_frequency_hz),
        unit='%',
        method='max(|max-median|, |median-min|) from interpolated origin sensitivity',
        extra={'frequency_hz': sensitivity_frequency_hz},
    )

    return {
        'natural_frequency_drift': natural_frequency_drift,
        'sensitivity_drift': sensitivity_drift,
        'linearity': _build_linearity_metric(linearity_by_frequency, use_origin=False),
        'natural_frequency_drift_origin': natural_frequency_drift_origin,
        'sensitivity_drift_origin': sensitivity_drift_origin,
        'linearity_origin': _build_linearity_metric(linearity_by_frequency, use_origin=True),
    }


def _build_compute_status(
    compute_analysis: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    if compute_analysis is None:
        return {
            'compute_cost_status': None,
            'compute_has_unsupported_layers': False,
            'compute_unsupported_layer_count': 0,
            'compute_unsupported_layers': [],
            'compute_unsupported_layer_details': [],
            'compute_cost_warning': None,
        }

    unsupported_layers = compute_analysis.get('unsupported_layers') or []
    unsupported_details = compute_analysis.get('unsupported_layer_details') or [
        {'name': name, 'reason': 'unsupported_layer_type'}
        for name in unsupported_layers
    ]
    has_unsupported_layers = bool(
        compute_analysis.get('has_unsupported_layers') or unsupported_layers
    )
    unsupported_layer_count = _to_int(compute_analysis.get('unsupported_layer_count'))
    if unsupported_layer_count is None:
        unsupported_layer_count = len(unsupported_details)

    compute_cost_status = compute_analysis.get('estimate_status')
    if compute_cost_status is None:
        compute_cost_status = 'partial' if has_unsupported_layers else 'complete'

    compute_cost_warning = compute_analysis.get('estimate_warning')
    if compute_cost_warning is None and has_unsupported_layers:
        names = [detail.get('name') for detail in unsupported_details if detail.get('name')]
        preview = ', '.join(names[:5])
        if unsupported_layer_count > 5:
            preview += ', ...'
        compute_cost_warning = (
            'Compute cost may be underestimated because unsupported layers were '
            f'detected: {preview}.'
        )

    return {
        'compute_cost_status': compute_cost_status,
        'compute_has_unsupported_layers': has_unsupported_layers,
        'compute_unsupported_layer_count': unsupported_layer_count,
        'compute_unsupported_layers': unsupported_layers,
        'compute_unsupported_layer_details': unsupported_details,
        'compute_cost_warning': compute_cost_warning,
    }


_LOSS_FUNCTION_LABELS = {
    'mae': 'MAE',
    'pure_power_log_mae': 'AFMAE',
    'power_log_mae': 'MAE+AFMAE',
    'afmse': 'AFMSE',
}


def _extract_loss_function(config: Optional[Dict[str, Any]]) -> Dict[str, Optional[str]]:
    if not config:
        return {
            'loss_function': None,
            'loss_function_key': None,
            'loss_function_source': None,
        }

    loss_type = config.get('loss_type')
    if isinstance(loss_type, str) and loss_type:
        normalized_loss_type = loss_type.strip()
        return {
            'loss_function': _LOSS_FUNCTION_LABELS.get(normalized_loss_type, normalized_loss_type.upper()),
            'loss_function_key': normalized_loss_type,
            'loss_function_source': 'config.loss_type',
        }

    if config.get('use_pure_power_loss'):
        return {
            'loss_function': _LOSS_FUNCTION_LABELS['pure_power_log_mae'],
            'loss_function_key': 'pure_power_log_mae',
            'loss_function_source': 'config.use_pure_power_loss',
        }

    if config.get('use_power_loss'):
        return {
            'loss_function': _LOSS_FUNCTION_LABELS['power_log_mae'],
            'loss_function_key': 'power_log_mae',
            'loss_function_source': 'config.use_power_loss',
        }

    return {
        'loss_function': _LOSS_FUNCTION_LABELS['mae'],
        'loss_function_key': 'mae',
        'loss_function_source': 'config.use_power_loss',
    }


def build_project_metrics_summary(checkpoint_dir: str, project_name: Optional[str] = None) -> Dict[str, Any]:
    training_info_path = os.path.join(checkpoint_dir, 'training_info.json')
    compute_analysis_path = os.path.join(checkpoint_dir, 'compute_analysis.json')
    model_info_path = os.path.join(checkpoint_dir, 'model_info.json')
    linear_response_path = os.path.join(checkpoint_dir, 'linear_response.json')
    linearity_by_frequency_path = os.path.join(checkpoint_dir, 'linearity_by_frequency.json')
    # config.json is in the project root (parent of data/), not in data/
    config_path = os.path.join(os.path.dirname(checkpoint_dir), 'config.json')

    training_info = _load_json_if_exists(training_info_path)
    compute_analysis = _load_json_if_exists(compute_analysis_path)
    model_info = _load_json_if_exists(model_info_path)
    linear_response = _load_json_if_exists(linear_response_path)
    linearity_by_frequency = _load_json_if_exists(linearity_by_frequency_path)
    config = _load_json_if_exists(config_path)

    missing_sources: List[str] = []
    missing_sections: List[str] = []
    for name, data in (
        ('training_info.json', training_info),
        ('compute_analysis.json', compute_analysis),
        ('linear_response.json', linear_response),
        ('linearity_by_frequency.json', linearity_by_frequency),
    ):
        if data is None:
            missing_sources.append(name)

    evaluation_metrics = (training_info or {}).get('evaluation_metrics') or {}
    if training_info is not None and not evaluation_metrics:
        missing_sections.append('training_info.evaluation_metrics')

    metric_details = _build_metric_details(linear_response, linearity_by_frequency)
    if linear_response is not None:
        if metric_details['natural_frequency_drift'] is None:
            missing_sections.append('linear_response.fit_params_comped')
        if metric_details['natural_frequency_drift_origin'] is None:
            missing_sections.append('linear_response.fit_params_origin')
        if metric_details['sensitivity_drift'] is None:
            missing_sections.append('linear_response.gains_comped_or_frequencies')
        if metric_details['sensitivity_drift_origin'] is None:
            missing_sections.append('linear_response.gains_origin_or_frequencies')
    if linearity_by_frequency is not None:
        if metric_details['linearity'] is None:
            missing_sections.append('linearity_by_frequency.r_squared_comped')
        if metric_details['linearity_origin'] is None:
            missing_sections.append('linearity_by_frequency.r_squared_origin')

    total_params = None
    if compute_analysis is not None:
        total_params = _to_int(compute_analysis.get('total_params'))
    if total_params is None and model_info is not None:
        total_params = _to_int(model_info.get('total_params'))

    compute_cost = None
    if compute_analysis is not None:
        compute_cost = _to_float(
            compute_analysis.get('estimated_cost', {})
            .get('weighted_units', {})
            .get('total')
        )

    compute_details = None
    if compute_analysis is not None:
        totals = compute_analysis.get('totals') or {}
        weighted_units = compute_analysis.get('estimated_cost', {}).get('weighted_units', {})
        compute_details = {
            'total_params': total_params,
            'additions': _to_int(totals.get('additions')),
            'multiplications': _to_int(totals.get('multiplications')),
            'maps': _to_int(totals.get('maps')),
            'total_ops': _to_int(totals.get('total')),
            'weighted_total': _to_float(weighted_units.get('total')),
            'weighted_additions': _to_float(weighted_units.get('additions')),
            'weighted_multiplications': _to_float(weighted_units.get('multiplications')),
            'weighted_maps': _to_float(weighted_units.get('maps')),
        }

    compute_status = _build_compute_status(compute_analysis)

    loss_function_details = _extract_loss_function(config)

    summary: Dict[str, Any] = {
        'project_name': project_name,
        'generated_at': datetime.now().astimezone().isoformat(),
        'status': 'complete',
        'calculation_standard': 'ablation-study-v1',
        'sources': {
            'training_info': training_info is not None,
            'compute_analysis': compute_analysis is not None,
            'model_info': model_info is not None,
            'linear_response': linear_response is not None,
            'linearity_by_frequency': linearity_by_frequency is not None,
            'config': config is not None,
        },
        'missing_sources': missing_sources,
        'missing_sections': missing_sections,
        'epochs': _to_int((training_info or {}).get('total_epochs')),
        'min_loss': _to_float((training_info or {}).get('min_loss')),
        'min_val_loss': _to_float((training_info or {}).get('min_val_loss')),
        'train_loss': _to_float(evaluation_metrics.get('train_loss')),
        'val_loss': _to_float(evaluation_metrics.get('val_loss')),
        'train_mae': _to_float(evaluation_metrics.get('train_mae')),
        'train_afmae': _to_float(evaluation_metrics.get('train_afmae')),
        'val_mae': _to_float(evaluation_metrics.get('val_mae')),
        'val_afmae': _to_float(evaluation_metrics.get('val_afmae')),
        'weights_source': evaluation_metrics.get('weights_source'),
        'freq_drift_hz': (metric_details['natural_frequency_drift'] or {}).get('drift'),
        'sens_drift_percent': (metric_details['sensitivity_drift'] or {}).get('drift'),
        'linearity_percent': (metric_details['linearity'] or {}).get('mean'),
        'compute_cost': compute_cost,
        'total_params': total_params,
        'lr': _to_float(config.get('learning_rate')) if config else None,
        'use_cosine_annealing': config.get('use_auto_lr') if config else None,
        'metric_details': metric_details,
        'compute_details': compute_details,
        **compute_status,
        **loss_function_details,
    }

    summary['display_metrics'] = {
        'Loss Function': summary['loss_function'],
        'TRAIN_MAE': summary['train_mae'],
        'TRAIN_AFMAE': summary['train_afmae'],
        'VAL_MAE': summary['val_mae'],
        'VAL_AFMAE': summary['val_afmae'],
        'Freq Drift (Hz)': summary['freq_drift_hz'],
        'Sens Drift (%)': summary['sens_drift_percent'],
        'Linearity (%)': summary['linearity_percent'],
        'Compute Cost': summary['compute_cost'],
        'Total Params': summary['total_params'],
        'Epochs': summary['epochs'],
        'LR': summary['lr'],
        'Cosine Annealing': summary['use_cosine_annealing'],
    }

    if missing_sources or missing_sections:
        summary['status'] = 'partial'

    return summary


def save_project_metrics_summary(
    checkpoint_dir: str,
    output_path: Optional[str] = None,
    project_name: Optional[str] = None,
) -> Dict[str, Any]:
    if output_path is None:
        output_path = os.path.join(checkpoint_dir, 'metrics.json')

    summary = build_project_metrics_summary(checkpoint_dir=checkpoint_dir, project_name=project_name)
    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(summary, file, indent=2, ensure_ascii=False)
    return summary