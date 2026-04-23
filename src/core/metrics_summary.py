"""项目指标汇总导出工具。"""

from __future__ import annotations

import json
import math
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FREQ_DRIFT_INBAND_MIN_HZ = 10.0
DEFAULT_FREQ_DRIFT_INBAND_MAX_HZ = 128.0
DEFAULT_LINEARITY_INBAND_MAX_HZ = 128.0


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


def _relative_to_repo_or_str(path: Path) -> str:
    try:
        return str(path.resolve()).replace(str(REPO_ROOT.resolve()) + os.sep, '').replace('\\', '/')
    except Exception:
        return str(path)


def _resolve_board_inference_project_dir(ep_path: Any) -> Optional[Path]:
    if not isinstance(ep_path, str):
        return None
    normalized_path = ep_path.strip()
    if not normalized_path:
        return None

    candidate = Path(normalized_path)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    return candidate


def _resolve_board_inference_summary_path(project_dir: Path, filename: str) -> Path:
    data_candidate = project_dir / 'data' / filename
    if data_candidate.exists():
        return data_candidate
    return project_dir / filename


def _extract_board_inference_point_count(keil_summary: Dict[str, Any]) -> Optional[int]:
    validation = keil_summary.get('validation') or {}
    record_count = _to_int(validation.get('record_count'))
    seq_len = _to_int(validation.get('seq_len'))
    if record_count is None or seq_len is None:
        parsed_output = keil_summary.get('parsed_output') or {}
        record_count = _to_int(parsed_output.get('record_count'))
        seq_len = _to_int(parsed_output.get('seq_len'))
    if record_count is None or seq_len is None:
        return None
    if record_count <= 0 or seq_len <= 0:
        return None
    return record_count * seq_len


def _speed_points_per_second(speed_ms_per_point: Optional[float]) -> Optional[float]:
    if speed_ms_per_point is None:
        return None
    if speed_ms_per_point <= 0.0:
        return None
    return 1000.0 / speed_ms_per_point


def _extract_board_inference_optimization_profiles(keil_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
    profiles = keil_summary.get('optimization_profiles')
    if not isinstance(profiles, list):
        return []

    extracted: List[Dict[str, Any]] = []
    published_key = str(keil_summary.get('published_optimization_profile', '') or '').strip()
    default_point_count = _extract_board_inference_point_count(keil_summary)

    for item in profiles:
        if not isinstance(item, dict):
            continue
        speed_ms_per_point = _to_float(item.get('keil_speed_ms_per_point'))
        if speed_ms_per_point is None:
            parsed_output = item.get('parsed_output') or {}
            wall_time_per_iter_ms = _to_float(parsed_output.get('wall_time_per_iter_ms'))
            point_count = _to_int(item.get('validation_point_count'))
            if point_count is None or point_count <= 0:
                point_count = default_point_count
            if (
                wall_time_per_iter_ms is not None
                and point_count is not None
                and point_count > 0
            ):
                speed_ms_per_point = wall_time_per_iter_ms / float(point_count)

        extracted.append({
            'key': str(item.get('key', '')),
            'label': str(item.get('label', item.get('key', ''))),
            'status': str(item.get('status', '')),
            'published': bool(item.get('published', False)) or str(item.get('key', '')) == published_key,
            'keil_speed_ms_per_point': speed_ms_per_point,
            'keil_speed_points_per_second': (
                _to_float(item.get('keil_speed_points_per_second'))
                or _speed_points_per_second(speed_ms_per_point)
            ),
            'keil_mae': _to_float((item.get('comparison') or {}).get('mae')),
            'flash_bytes': _to_int(item.get('flash_bytes')),
            'ram_bytes': _to_int(item.get('ram_bytes')),
            'comparison_path': item.get('comparison_path'),
            'build_output_path': item.get('build_output_path'),
        })
    return extracted


def _load_board_inference_metrics(config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    metrics: Dict[str, Any] = {
        'configured': False,
        'ep_path': None,
        'project_dir': None,
        'qemu_summary_path': None,
        'keil_summary_path': None,
        'qemu_summary_exists': False,
        'keil_summary_exists': False,
        'qemu_mae': None,
        'keil_mae': None,
        'keil_wall_time_per_iter_ms': None,
        'keil_point_count_per_iter': None,
        'keil_speed_ms_per_point': None,
        'keil_speed_unit': 'ms/point',
        'keil_speed_points_per_second': None,
        'keil_speed_display_unit': 'points/s',
        'published_optimization_profile': None,
        'keil_optimization_profiles': [],
        'missing_sources': [],
        'missing_sections': [],
    }
    if not config:
        return metrics

    ep_path = config.get('board_inference_ep_path')
    project_dir = _resolve_board_inference_project_dir(ep_path)
    if project_dir is None:
        return metrics

    metrics['configured'] = True
    metrics['ep_path'] = str(ep_path).replace('\\', '/')
    metrics['project_dir'] = _relative_to_repo_or_str(project_dir)

    if not project_dir.exists():
        metrics['missing_sources'].append(f'board_inference_ep_path:{metrics["ep_path"]}')
        return metrics

    qemu_summary_path = _resolve_board_inference_summary_path(project_dir, 'benchmark_summary.json')
    keil_summary_path = _resolve_board_inference_summary_path(project_dir, 'keil_benchmark_summary.json')
    metrics['qemu_summary_path'] = _relative_to_repo_or_str(qemu_summary_path)
    metrics['keil_summary_path'] = _relative_to_repo_or_str(keil_summary_path)

    qemu_summary = _load_json_if_exists(str(qemu_summary_path))
    keil_summary = _load_json_if_exists(str(keil_summary_path))
    metrics['qemu_summary_exists'] = qemu_summary is not None
    metrics['keil_summary_exists'] = keil_summary is not None

    if qemu_summary is None:
        metrics['missing_sources'].append('board_inference.benchmark_summary.json')
    else:
        metrics['qemu_mae'] = _to_float((qemu_summary.get('comparison') or {}).get('mae'))
        if metrics['qemu_mae'] is None:
            metrics['missing_sections'].append('board_inference.qemu.comparison.mae')

    if keil_summary is None:
        metrics['missing_sources'].append('board_inference.keil_benchmark_summary.json')
    else:
        metrics['keil_mae'] = _to_float((keil_summary.get('comparison') or {}).get('mae'))
        if metrics['keil_mae'] is None:
            metrics['missing_sections'].append('board_inference.keil.comparison.mae')

        metrics['published_optimization_profile'] = (
            str(keil_summary.get('published_optimization_profile', '')).strip() or None
        )
        metrics['keil_optimization_profiles'] = _extract_board_inference_optimization_profiles(keil_summary)

        metrics['keil_wall_time_per_iter_ms'] = _to_float(
            (keil_summary.get('parsed_output') or {}).get('wall_time_per_iter_ms')
        )
        if metrics['keil_wall_time_per_iter_ms'] is None:
            metrics['missing_sections'].append('board_inference.keil.parsed_output.wall_time_per_iter_ms')

        metrics['keil_point_count_per_iter'] = _extract_board_inference_point_count(keil_summary)
        if metrics['keil_point_count_per_iter'] is None:
            metrics['missing_sections'].append('board_inference.keil.validation.record_count_seq_len')

        if (
            metrics['keil_wall_time_per_iter_ms'] is not None
            and metrics['keil_point_count_per_iter'] is not None
            and metrics['keil_point_count_per_iter'] > 0
        ):
            metrics['keil_speed_ms_per_point'] = (
                metrics['keil_wall_time_per_iter_ms'] / metrics['keil_point_count_per_iter']
            )
            metrics['keil_speed_points_per_second'] = _speed_points_per_second(
                metrics['keil_speed_ms_per_point']
            )

    return metrics


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


def _build_frequency_gain_pairs(
    linear_response: Optional[Dict[str, Any]],
    use_origin: bool,
    max_frequency_hz: Optional[float],
) -> List[tuple[List[float], List[float]]]:
    if not linear_response:
        return []

    frequencies_raw = linear_response.get('frequencies') or []
    gain_key = 'gains_origin' if use_origin else 'gains_comped'
    gains_raw = linear_response.get(gain_key) or linear_response.get('gains_compensated') or []

    frequencies = [_to_float(freq) for freq in frequencies_raw]
    if any(freq is None for freq in frequencies):
        return []

    selected_indices: List[int] = []
    selected_frequencies: List[float] = []
    for index, frequency_hz in enumerate(frequencies):
        if frequency_hz is None:
            continue
        if max_frequency_hz is not None and frequency_hz > max_frequency_hz:
            continue
        if selected_frequencies and math.isclose(selected_frequencies[-1], frequency_hz):
            continue
        selected_indices.append(index)
        selected_frequencies.append(frequency_hz)

    if len(selected_frequencies) < 2:
        return []

    pairs: List[tuple[List[float], List[float]]] = []
    for gain_curve in gains_raw:
        if not isinstance(gain_curve, list):
            continue
        gain_values = [_to_float(value) for value in gain_curve]
        if any(value is None for value in gain_values):
            continue
        if len(gain_values) != len(frequencies):
            continue
        pairs.append((
            selected_frequencies,
            [gain_values[index] for index in selected_indices],
        ))
    return pairs


def _extract_fit_center_frequency_hz(
    fit_params: Any,
    min_frequency_hz: Optional[float] = DEFAULT_FREQ_DRIFT_INBAND_MIN_HZ,
    max_frequency_hz: Optional[float] = DEFAULT_FREQ_DRIFT_INBAND_MAX_HZ,
) -> Optional[float]:
    if not isinstance(fit_params, list) or len(fit_params) < 2:
        return None

    b_value = _to_float(fit_params[1])
    if b_value is None or b_value <= 0.0:
        return None

    center_frequency_hz = math.sqrt(b_value) / (2.0 * math.pi)
    if min_frequency_hz is not None:
        center_frequency_hz = max(float(min_frequency_hz), center_frequency_hz)
    if max_frequency_hz is not None:
        center_frequency_hz = min(float(max_frequency_hz), center_frequency_hz)
    return center_frequency_hz


def _extract_inband_frequency_points(
    linear_response: Optional[Dict[str, Any]],
    min_frequency_hz: Optional[float],
    max_frequency_hz: Optional[float],
) -> List[float]:
    if not linear_response:
        return []

    points: List[float] = []
    for frequency_raw in linear_response.get('frequencies') or []:
        frequency_hz = _to_float(frequency_raw)
        if frequency_hz is None:
            continue
        if min_frequency_hz is not None and frequency_hz < min_frequency_hz:
            continue
        if max_frequency_hz is not None and frequency_hz > max_frequency_hz:
            continue
        if points and math.isclose(points[-1], frequency_hz):
            continue
        points.append(frequency_hz)
    return points


def _extract_natural_frequency_values(
    linear_response: Optional[Dict[str, Any]],
    use_origin: bool,
    min_frequency_hz: Optional[float] = DEFAULT_FREQ_DRIFT_INBAND_MIN_HZ,
    max_frequency_hz: Optional[float] = DEFAULT_FREQ_DRIFT_INBAND_MAX_HZ,
) -> List[float]:
    values: List[float] = []
    if not linear_response:
        return values

    fit_key = 'fit_params_origin' if use_origin else 'fit_params_comped'
    for fit_params in linear_response.get(fit_key) or []:
        center_frequency_hz = _extract_fit_center_frequency_hz(
            fit_params,
            min_frequency_hz=min_frequency_hz,
            max_frequency_hz=max_frequency_hz,
        )
        if center_frequency_hz is None:
            continue
        values.append(center_frequency_hz)
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
    max_frequency_hz: Optional[float] = DEFAULT_LINEARITY_INBAND_MAX_HZ,
) -> List[float]:
    if not linearity_by_frequency:
        return []

    key = 'r_squared_origin' if use_origin else 'r_squared_comped'
    values: List[float] = []
    for item in linearity_by_frequency.get('linearity_by_frequency') or []:
        if not isinstance(item, dict):
            continue
        frequency_hz = _to_float(item.get('frequency_hz'))
        if max_frequency_hz is not None:
            if frequency_hz is None or frequency_hz > max_frequency_hz:
                continue
        r_squared = _to_float(item.get(key))
        if r_squared is None:
            continue
        values.append(1.0 - r_squared)
    return values


def _build_linearity_metric(
    linearity_by_frequency: Optional[Dict[str, Any]],
    use_origin: bool,
    max_frequency_hz: Optional[float] = DEFAULT_LINEARITY_INBAND_MAX_HZ,
) -> Optional[Dict[str, Any]]:
    nonlinearity_values = _extract_linearity_values(
        linearity_by_frequency,
        use_origin,
        max_frequency_hz=max_frequency_hz,
    )
    if not nonlinearity_values:
        return None

    selected_frequencies_hz: List[float] = []
    selected_rows = (linearity_by_frequency or {}).get('linearity_by_frequency') or []
    for item in selected_rows:
        if not isinstance(item, dict):
            continue
        frequency_hz = _to_float(item.get('frequency_hz'))
        if frequency_hz is None:
            continue
        if max_frequency_hz is not None and frequency_hz > max_frequency_hz:
            continue
        selected_frequencies_hz.append(frequency_hz)

    mean_value = sum(nonlinearity_values) / len(nonlinearity_values)
    return {
        'mean': mean_value * 100.0,
        'max': max(nonlinearity_values) * 100.0,
        'min': min(nonlinearity_values) * 100.0,
        'count': len(nonlinearity_values),
        'unit': '%',
        'method': 'mean(1 - R^2) across in-band frequency points',
        'band_max_hz': max_frequency_hz,
        'frequencies_hz': selected_frequencies_hz,
    }


def _build_metric_details(
    linear_response: Optional[Dict[str, Any]],
    linearity_by_frequency: Optional[Dict[str, Any]],
    sensitivity_frequency_hz: float = 100.0,
    natural_frequency_band_min_hz: float = DEFAULT_FREQ_DRIFT_INBAND_MIN_HZ,
    natural_frequency_band_max_hz: float = DEFAULT_FREQ_DRIFT_INBAND_MAX_HZ,
    linearity_band_max_hz: float = DEFAULT_LINEARITY_INBAND_MAX_HZ,
) -> Dict[str, Optional[Dict[str, Any]]]:
    natural_frequency_source_points = _extract_inband_frequency_points(
        linear_response,
        min_frequency_hz=natural_frequency_band_min_hz,
        max_frequency_hz=natural_frequency_band_max_hz,
    )

    natural_frequency_drift = _build_distribution_metric(
        _extract_natural_frequency_values(
            linear_response,
            use_origin=False,
            min_frequency_hz=natural_frequency_band_min_hz,
            max_frequency_hz=natural_frequency_band_max_hz,
        ),
        unit='Hz',
        method='max(|max-median|, |median-min|) from band-limited fitted center frequency (comped)',
        extra={
            'band_min_hz': natural_frequency_band_min_hz,
            'band_max_hz': natural_frequency_band_max_hz,
            'source_frequency_points_hz': natural_frequency_source_points,
            'fit_param_key': 'fit_params_comped',
        },
    )
    natural_frequency_drift_origin = _build_distribution_metric(
        _extract_natural_frequency_values(
            linear_response,
            use_origin=True,
            min_frequency_hz=natural_frequency_band_min_hz,
            max_frequency_hz=natural_frequency_band_max_hz,
        ),
        unit='Hz',
        method='max(|max-median|, |median-min|) from band-limited fitted center frequency (origin)',
        extra={
            'band_min_hz': natural_frequency_band_min_hz,
            'band_max_hz': natural_frequency_band_max_hz,
            'source_frequency_points_hz': natural_frequency_source_points,
            'fit_param_key': 'fit_params_origin',
        },
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
        'linearity': _build_linearity_metric(
            linearity_by_frequency,
            use_origin=False,
            max_frequency_hz=linearity_band_max_hz,
        ),
        'natural_frequency_drift_origin': natural_frequency_drift_origin,
        'sensitivity_drift_origin': sensitivity_drift_origin,
        'linearity_origin': _build_linearity_metric(
            linearity_by_frequency,
            use_origin=True,
            max_frequency_hz=linearity_band_max_hz,
        ),
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

    metric_details = _build_metric_details(
        linear_response,
        linearity_by_frequency,
        natural_frequency_band_min_hz=DEFAULT_FREQ_DRIFT_INBAND_MIN_HZ,
        natural_frequency_band_max_hz=DEFAULT_FREQ_DRIFT_INBAND_MAX_HZ,
        linearity_band_max_hz=DEFAULT_LINEARITY_INBAND_MAX_HZ,
    )
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
    board_inference_metrics = _load_board_inference_metrics(config)
    missing_sources.extend(board_inference_metrics['missing_sources'])
    missing_sections.extend(board_inference_metrics['missing_sections'])

    summary: Dict[str, Any] = {
        'project_name': project_name,
        'generated_at': datetime.now().astimezone().isoformat(),
        'status': 'complete',
        'calculation_standard': 'ablation-study-v4-bounded-fit-freq-inband-linearity',
        'sources': {
            'training_info': training_info is not None,
            'compute_analysis': compute_analysis is not None,
            'model_info': model_info is not None,
            'linear_response': linear_response is not None,
            'linearity_by_frequency': linearity_by_frequency is not None,
            'config': config is not None,
            'board_inference_config': board_inference_metrics['configured'],
            'board_inference_qemu': board_inference_metrics['qemu_summary_exists'],
            'board_inference_keil': board_inference_metrics['keil_summary_exists'],
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
        'freq_drift_band_min_hz': (metric_details['natural_frequency_drift'] or {}).get('band_min_hz'),
        'freq_drift_band_max_hz': (metric_details['natural_frequency_drift'] or {}).get('band_max_hz'),
        'freq_drift_source_frequency_points_hz': (
            (metric_details['natural_frequency_drift'] or {}).get('source_frequency_points_hz')
        ),
        'freq_drift_interpolation_points': None,
        'sens_drift_percent': (metric_details['sensitivity_drift'] or {}).get('drift'),
        'linearity_percent': (metric_details['linearity'] or {}).get('mean'),
        'linearity_band_max_hz': (metric_details['linearity'] or {}).get('band_max_hz'),
        'linearity_frequency_count': (metric_details['linearity'] or {}).get('count'),
        'linearity_frequency_points_hz': (metric_details['linearity'] or {}).get('frequencies_hz'),
        'compute_cost': compute_cost,
        'total_params': total_params,
        'lr': _to_float(config.get('learning_rate')) if config else None,
        'use_cosine_annealing': config.get('use_auto_lr') if config else None,
        'metric_details': metric_details,
        'compute_details': compute_details,
        **compute_status,
        **loss_function_details,
        'board_inference_ep_path': board_inference_metrics['ep_path'],
        'board_qemu_mae': board_inference_metrics['qemu_mae'],
        'board_keil_mae': board_inference_metrics['keil_mae'],
        'board_keil_speed': board_inference_metrics['keil_speed_ms_per_point'],
        'board_keil_fps': board_inference_metrics['keil_speed_points_per_second'],
        'board_inference': {
            **board_inference_metrics,
        },
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
        'QEMU-MAE': summary['board_qemu_mae'],
        'KEIL-MAE': summary['board_keil_mae'],
        'KEIL-SPEED': summary['board_keil_speed'],
        'KEIL-FPS': summary['board_keil_fps'],
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
