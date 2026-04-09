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


def _compute_drift_metrics(linear_response: Optional[Dict[str, Any]]) -> Dict[str, Optional[float]]:
    if not linear_response:
        return {
            'freq_drift_hz': None,
            'sens_drift_percent': None,
            'linearity_percent': None,
        }

    gains_origin = linear_response.get('gains_origin')
    gains_comped = linear_response.get('gains_comped') or linear_response.get('gains_compensated')
    frequencies = linear_response.get('frequencies')

    if not gains_origin or not gains_comped or not frequencies:
        return {
            'freq_drift_hz': None,
            'sens_drift_percent': None,
            'linearity_percent': None,
        }

    num_freqs = len(frequencies)
    num_mags = len(gains_origin)
    if num_freqs == 0 or num_mags == 0:
        return {
            'freq_drift_hz': None,
            'sens_drift_percent': None,
            'linearity_percent': None,
        }

    mean_gain_origin: List[float] = []
    mean_gain_comped: List[float] = []
    for freq_idx in range(num_freqs):
        origin_sum = 0.0
        comped_sum = 0.0
        for mag_idx in range(num_mags):
            origin_sum += float(gains_origin[mag_idx][freq_idx])
            comped_sum += float(gains_comped[mag_idx][freq_idx])
        mean_gain_origin.append(origin_sum / num_mags)
        mean_gain_comped.append(comped_sum / num_mags)

    peak_idx_origin = max(range(num_freqs), key=lambda idx: mean_gain_origin[idx])
    peak_idx_comped = max(range(num_freqs), key=lambda idx: mean_gain_comped[idx])
    peak_freq_origin = float(frequencies[peak_idx_origin])
    peak_freq_comped = float(frequencies[peak_idx_comped])
    freq_drift = abs(peak_freq_comped - peak_freq_origin)

    window_size = 3
    origin_region = mean_gain_origin[
        max(0, peak_idx_origin - window_size): min(num_freqs, peak_idx_origin + window_size + 1)
    ]
    comped_region = mean_gain_comped[
        max(0, peak_idx_comped - window_size): min(num_freqs, peak_idx_comped + window_size + 1)
    ]

    avg_origin = sum(origin_region) / len(origin_region) if origin_region else 0.0
    avg_comped = sum(comped_region) / len(comped_region) if comped_region else 0.0
    sens_drift = abs((avg_comped - avg_origin) / avg_origin) * 100.0 if avg_origin > 0 else 0.0

    if num_freqs < 2:
        return {
            'freq_drift_hz': freq_drift,
            'sens_drift_percent': sens_drift,
            'linearity_percent': None,
        }

    log_freq = [math.log10(float(freq)) for freq in frequencies]
    log_gain = [math.log10(max(float(gain), 0.001)) for gain in mean_gain_comped]
    count = len(log_freq)
    sum_x = sum(log_freq)
    sum_y = sum(log_gain)
    sum_xy = sum(x * y for x, y in zip(log_freq, log_gain))
    sum_x2 = sum(x * x for x in log_freq)
    denominator = count * sum_x2 - sum_x * sum_x
    if denominator == 0:
        linearity = None
    else:
        slope = (count * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / count
        predicted = [slope * x + intercept for x in log_freq]
        ss_res = sum((y - pred) ** 2 for y, pred in zip(log_gain, predicted))
        mean_y = sum_y / count
        ss_tot = sum((y - mean_y) ** 2 for y in log_gain)
        r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
        linearity = max(0.0, min(100.0, r_squared * 100.0))

    return {
        'freq_drift_hz': freq_drift,
        'sens_drift_percent': sens_drift,
        'linearity_percent': linearity,
    }


def build_project_metrics_summary(checkpoint_dir: str, project_name: Optional[str] = None) -> Dict[str, Any]:
    training_info_path = os.path.join(checkpoint_dir, 'training_info.json')
    compute_analysis_path = os.path.join(checkpoint_dir, 'compute_analysis.json')
    model_info_path = os.path.join(checkpoint_dir, 'model_info.json')
    linear_response_path = os.path.join(checkpoint_dir, 'linear_response.json')

    training_info = _load_json_if_exists(training_info_path)
    compute_analysis = _load_json_if_exists(compute_analysis_path)
    model_info = _load_json_if_exists(model_info_path)
    linear_response = _load_json_if_exists(linear_response_path)

    missing_sources: List[str] = []
    missing_sections: List[str] = []
    for name, data in (
        ('training_info.json', training_info),
        ('compute_analysis.json', compute_analysis),
        ('linear_response.json', linear_response),
    ):
        if data is None:
            missing_sources.append(name)

    evaluation_metrics = (training_info or {}).get('evaluation_metrics') or {}
    if training_info is not None and not evaluation_metrics:
        missing_sections.append('training_info.evaluation_metrics')

    drift_metrics = _compute_drift_metrics(linear_response)
    if linear_response is not None and all(value is None for value in drift_metrics.values()):
        missing_sections.append('linear_response.derived_metrics')

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

    summary: Dict[str, Any] = {
        'project_name': project_name,
        'generated_at': datetime.now().astimezone().isoformat(),
        'status': 'complete',
        'sources': {
            'training_info': training_info is not None,
            'compute_analysis': compute_analysis is not None,
            'model_info': model_info is not None,
            'linear_response': linear_response is not None,
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
        'freq_drift_hz': drift_metrics['freq_drift_hz'],
        'sens_drift_percent': drift_metrics['sens_drift_percent'],
        'linearity_percent': drift_metrics['linearity_percent'],
        'compute_cost': compute_cost,
        'total_params': total_params,
    }

    summary['display_metrics'] = {
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