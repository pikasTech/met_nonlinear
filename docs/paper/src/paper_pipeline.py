from __future__ import annotations

import copy
import json
import math
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LogNorm
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, FancyBboxPatch, Polygon

ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PAPER_DIR / 'data'
FIGURES_DIR = PAPER_DIR / 'figures'
LATEX_DIR = PAPER_DIR / 'latex'
WIENER_PARALLEL_DIR = ROOT / 'ex_projects' / 'compare' / 'wiener_parallel_modeling'
sys.path.insert(0, str(ROOT))

from src.core.metrics_summary import (  # noqa: E402
    DEFAULT_FREQ_DRIFT_INBAND_MAX_HZ,
    DEFAULT_FREQ_DRIFT_INBAND_MIN_HZ,
    _extract_natural_frequency_values,
)
try:
    from src.figure_visual_audit import (  # type: ignore  # noqa: E402
        VISUAL_AUDIT_KEY,
        audit_schematic_geometry,
        audit_image_file,
        audit_matplotlib_figure,
        audit_montage_layout,
        combine_audits,
        validate_raw_visual_quality,
    )
except ImportError:  # pragma: no cover - direct script execution
    from figure_visual_audit import (  # type: ignore  # noqa: E402
        VISUAL_AUDIT_KEY,
        audit_schematic_geometry,
        audit_image_file,
        audit_matplotlib_figure,
        audit_montage_layout,
        combine_audits,
        validate_raw_visual_quality,
    )
from src.visualization.subfigure_montage import PanelSpec, compose_subfigures  # noqa: E402
from src.visualization.paper_plot_style import (  # noqa: E402
    apply_paper_matplotlib_style,
    paper_plot_style_payload,
)

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'figure.dpi': 160,
    'savefig.dpi': 220,
    'font.size': 10,
    'axes.titlesize': 12,
    'axes.labelsize': 10,
    'legend.fontsize': 8.5,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
})
apply_paper_matplotlib_style()

SHORT_CONNECTOR_FRACTION = 2.0 / 3.0


def _polyline_length(points: List[tuple[float, float]]) -> float:
    return sum(math.hypot(end[0] - start[0], end[1] - start[1]) for start, end in zip(points[:-1], points[1:]))


def _point_at_polyline_distance(points: List[tuple[float, float]], distance: float) -> tuple[float, float]:
    if not points:
        return (0.0, 0.0)
    if distance <= 0:
        return points[0]
    travelled = 0.0
    for start, end in zip(points[:-1], points[1:]):
        segment = math.hypot(end[0] - start[0], end[1] - start[1])
        if travelled + segment >= distance:
            ratio = 0.0 if segment <= 0 else (distance - travelled) / segment
            return (start[0] + (end[0] - start[0]) * ratio, start[1] + (end[1] - start[1]) * ratio)
        travelled += segment
    return points[-1]


def _shorten_polyline(points: List[tuple[float, float]], fraction: float = SHORT_CONNECTOR_FRACTION) -> List[tuple[float, float]]:
    if len(points) < 2:
        return points
    total = _polyline_length(points)
    if total <= 0:
        return points
    trim = total * (1.0 - fraction) / 2.0
    start_distance = trim
    end_distance = total - trim
    shortened = [_point_at_polyline_distance(points, start_distance)]
    travelled = 0.0
    for start, end in zip(points[:-1], points[1:]):
        travelled += math.hypot(end[0] - start[0], end[1] - start[1])
        if start_distance < travelled < end_distance:
            shortened.append(end)
    shortened.append(_point_at_polyline_distance(points, end_distance))
    return shortened


def _short_arrow_payload(
    arrow_id: str,
    full_points: List[tuple[float, float]],
    *,
    source: str | None = None,
    target: str | None = None,
    require_axis_aligned: bool = False,
) -> tuple[List[tuple[float, float]], Dict[str, Any]]:
    points = _shorten_polyline(full_points)
    payload: Dict[str, Any] = {
        'id': arrow_id,
        'points': [[float(x), float(y)] for x, y in points],
        'full_points': [[float(x), float(y)] for x, y in full_points],
        'endpoint_policy': 'outside_clearance',
        'max_length_fraction': SHORT_CONNECTOR_FRACTION,
    }
    if source is not None:
        payload['source'] = source
    if target is not None:
        payload['target'] = target
    if require_axis_aligned:
        payload['require_axis_aligned'] = True
    return points, payload


PALETTE = {
    'Wiener-KAN': '#0f6c5c',
    'TCN': '#1f4e79',
    '1DCNN': '#c96b00',
    'LSTM': '#8a3b12',
    'LSTMTransformer': '#6a3d9a',
    'GRU': '#a61c3c',
    'RNN': '#666666',
    'Origin': '#111111',
    'MAE+AFMAE': '#0f6c5c',
    'MAE': '#b54d00',
    'AFMAE': '#3366cc',
    'CNN-KAN': '#1f4e79',
    'No symmetry': '#b54d00',
    'Random trainable IIR': '#6a3d9a',
    'Wiener-MLP': '#a61c3c',
    'No positive (stress)': '#555555',
    'Project default': '#0f6c5c',
    '-O0': '#999999',
    '-O2': '#1f4e79',
    '-Ofast + LTO': '#c96b00',
    'Measured': '#111111',
    'Default 1:1:6': '#777777',
    'Adopted 1:3:20': '#0f6c5c',
}

LINEARITY_INBAND_MAX_HZ = 128.0
RADAR_METRICS = [
    ('Freq Drift', 'freq_drift_hz', 'min'),
    ('Sens Drift', 'sens_drift_percent', 'min'),
    ('Linearity', 'linearity_percent', 'min'),
    ('KEIL FPS', 'board_keil_fps', 'max'),
    ('KEIL RAM', 'ram_bytes', 'min'),
]

MAIN_BENCHMARK = [
    ('Wiener-KAN', 'projects/01_LR_STUDY/FRIKANh8u6l6_e1k_lr7e4/data/metrics.json'),
    ('TCN', 'projects/06_TCN/TCNc4d1248k3_nopd_true_e1k_lr2e3/data/metrics.json'),
    ('1DCNN', 'projects/05_1DCNN/1DCNNc4u8k20l8_e1k_lr18e4_pd8l2_d001_cvtanh_true/data/metrics.json'),
    ('LSTM', 'projects/01_LR_STUDY/LSTMu16_e1k_puremae_r8/data/metrics.json'),
    ('LSTMTransformer', 'projects/01_LR_STUDY/LSTMTransformeru6_e1k_puremae/data/metrics.json'),
    ('RNN', 'projects/07_RNN/RNNu16_e1k_puremae_r15/data/metrics.json'),
    ('GRU', 'projects/01_LR_STUDY/GRNu16_e1k_puremae/data/metrics.json'),
]

LOSS_ABLATION = [
    ('MAE+AFMAE', 'projects/01_LR_STUDY/FRIKANh8u6l6_e1k_lr7e4/data/metrics.json'),
    ('MAE', 'projects/01_LR_STUDY/FRIKANh8u6l6_e1k_lr7e4_puremae/data/metrics.json'),
    ('AFMAE', 'projects/03_FRIKAN_PUREAFME/FRIKANh8u6l6_e1k_lr5e4_pureafmae/data/metrics.json'),
]

STRUCTURE_ABLATION = [
    ('Wiener-KAN', 'projects/01_LR_STUDY/FRIKANh8u6l6_e1k_lr7e4/data/metrics.json'),
    ('CNN-KAN', 'projects/01_LR_STUDY/CNNKANh8u6l6_e1k_lr28e5_c8k5d05/data/metrics.json'),
    ('No symmetry', 'projects/01_LR_STUDY/FRIKANh8u6l6_e1k_lr7e4_nosym_r5/data/metrics.json'),
    ('Random trainable IIR', 'projects/01_LR_STUDY/FRIKANh8u6l6_e1k_lr14e5_randfrirnn_r2/data/metrics.json'),
    ('Wiener-MLP', 'projects/04_FRIMLP/FRIMLPh8u6l6_e1k_lr7e4_mlp20l6_tanh_d00/data/metrics.json'),
    ('No positive (stress)', 'projects/01_LR_STUDY/FRIKANh8u6l6_e1k_lr7e4_nopositive/data/metrics.json'),
]

WIENER_FRONTEND_ABLATION = [
    ('System prior, frozen', 'projects/01_LR_STUDY/FRIKANh8u6l6_e1k_lr7e4/data/metrics.json'),
    ('Random, frozen', 'projects/08_IIR_AB/FRIKANh8u6l6_e1k_lr5e4_randiir_frozen/data/metrics.json'),
    ('System prior, trainable', 'projects/08_IIR_AB/FRIKANh8u6l6_e1k_lr2e4_sysiir_trainable/data/metrics.json'),
    ('Random, trainable', 'projects/08_IIR_AB/FRIKANh8u6l6_e1k_lr1e4_randiir_trainable/data/metrics.json'),
]

DEPLOYMENT = MAIN_BENCHMARK

TRAJECTORY_MODELS = [
    ('Origin', 'projects/01_LR_STUDY/FRIKANh8u6l6_e1k_lr7e4/data/linear_response.json'),
    ('Wiener-KAN', 'projects/01_LR_STUDY/FRIKANh8u6l6_e1k_lr7e4/data/linear_response.json'),
]

LEGACY_IMAGE_MIGRATIONS = []


LUT_VARIANTS = [
    ('LUT nearest', 'ex_projects/inference/qemu-c-inference/frikan_h8u6l6_e1k_lr7e4'),
    ('LUT + interp', 'ex_projects/inference/qemu-c-inference/frikan_h8u6l6_e1k_lr7e4_interp'),
    ('No LUT exact', 'ex_projects/inference/qemu-c-inference/frikan_h8u6l6_e1k_lr7e4_no_lut'),
]

LUT_POINT_SWEEP = [
    {'mode': 'nearest', 'points': 65, 'ep_path': 'ex_projects/inference/qemu-c-inference/frikan_h8u6l6_e1k_lr7e4_lut065'},
    {'mode': 'interp', 'points': 65, 'ep_path': 'ex_projects/inference/qemu-c-inference/frikan_h8u6l6_e1k_lr7e4_lut065_interp'},
    {'mode': 'nearest', 'points': 129, 'ep_path': 'ex_projects/inference/qemu-c-inference/frikan_h8u6l6_e1k_lr7e4_lut129'},
    {'mode': 'interp', 'points': 129, 'ep_path': 'ex_projects/inference/qemu-c-inference/frikan_h8u6l6_e1k_lr7e4_lut129_interp'},
    {'mode': 'nearest', 'points': 257, 'ep_path': 'ex_projects/inference/qemu-c-inference/frikan_h8u6l6_e1k_lr7e4_lut257'},
    {'mode': 'interp', 'points': 257, 'ep_path': 'ex_projects/inference/qemu-c-inference/frikan_h8u6l6_e1k_lr7e4_lut257_interp'},
    {'mode': 'nearest', 'points': 513, 'ep_path': 'ex_projects/inference/qemu-c-inference/frikan_h8u6l6_e1k_lr7e4_lut513'},
    {'mode': 'interp', 'points': 513, 'ep_path': 'ex_projects/inference/qemu-c-inference/frikan_h8u6l6_e1k_lr7e4_lut513_interp'},
    {'mode': 'nearest', 'points': 769, 'ep_path': 'ex_projects/inference/qemu-c-inference/frikan_h8u6l6_e1k_lr7e4'},
    {'mode': 'interp', 'points': 769, 'ep_path': 'ex_projects/inference/qemu-c-inference/frikan_h8u6l6_e1k_lr7e4_interp'},
]

BUILD_PATTERN = re.compile(r'Program Size: Code=(\d+) RO-data=(\d+) RW-data=(\d+) ZI-data=(\d+)')
FIGURE_PIPELINE_CONFIG: Dict[str, Any] = {}



def apply_config() -> Dict[str, Any]:
    config_path = PAPER_DIR / 'config.json'
    if not config_path.exists():
        return {}
    config = json.loads(config_path.read_text(encoding='utf-8'))

    def metric_pairs(key: str, default: List[tuple[str, str]]) -> List[tuple[str, str]]:
        rows = config.get(key)
        if not rows:
            return default
        return [(str(item['label']), str(item['metrics_path'])) for item in rows]

    global MAIN_BENCHMARK, LOSS_ABLATION, STRUCTURE_ABLATION, WIENER_FRONTEND_ABLATION, DEPLOYMENT, LUT_VARIANTS, LUT_POINT_SWEEP, TRAJECTORY_MODELS, LEGACY_IMAGE_MIGRATIONS, FIGURE_PIPELINE_CONFIG
    MAIN_BENCHMARK = metric_pairs('main_benchmark', MAIN_BENCHMARK)
    LOSS_ABLATION = metric_pairs('loss_ablation', LOSS_ABLATION)
    STRUCTURE_ABLATION = metric_pairs('structure_ablation', STRUCTURE_ABLATION)
    WIENER_FRONTEND_ABLATION = metric_pairs('wiener_frontend_ablation', WIENER_FRONTEND_ABLATION)
    DEPLOYMENT = metric_pairs('deployment', DEPLOYMENT)
    if config.get('lut_variants'):
        LUT_VARIANTS = [(str(item['label']), str(item['ep_path'])) for item in config['lut_variants']]
    if config.get('lut_point_sweep'):
        LUT_POINT_SWEEP = [
            {
                'mode': str(item['mode']),
                'points': int(item['points']),
                'ep_path': str(item['ep_path']),
            }
            for item in config['lut_point_sweep']
        ]
    if config.get('trajectory_models'):
        TRAJECTORY_MODELS = [(str(item['label']), str(item['linear_response_path'])) for item in config['trajectory_models']]
    migration_rows = config.get('source_image_migrations') or config.get('legacy_image_migrations')
    if migration_rows:
        LEGACY_IMAGE_MIGRATIONS = [dict(item) for item in migration_rows]
    FIGURE_PIPELINE_CONFIG = copy.deepcopy(config.get('figure_pipeline') or {})
    return config


def _as_float_tuple(value: Any, default: tuple[float, float]) -> tuple[float, float]:
    if isinstance(value, (list, tuple)) and len(value) == 2:
        return (float(value[0]), float(value[1]))
    return default


def _as_int_list(value: Any, default: List[int] | None = None) -> List[int] | None:
    if value is None:
        return default
    if isinstance(value, (list, tuple)):
        return [int(item) for item in value]
    return default


def _as_int_spacing(value: Any, default: int | tuple[int, int] | List[int]) -> int | tuple[int, int] | List[int]:
    if isinstance(default, tuple):
        if isinstance(value, (list, tuple)) and len(value) == len(default):
            return tuple(int(item) for item in value)
        if isinstance(value, (int, float)):
            return int(value)
        return default
    if isinstance(default, list):
        if isinstance(value, (list, tuple)) and len(value) == len(default):
            return [int(item) for item in value]
        if isinstance(value, (int, float)):
            return int(value)
        return default
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, (list, tuple)) and len(value) == 2:
        return tuple(int(item) for item in value)
    return default


def _deep_merge(base: Any, override: Any) -> Any:
    if isinstance(base, dict) and isinstance(override, dict):
        merged = {key: copy.deepcopy(value) for key, value in base.items()}
        for key, value in override.items():
            merged[key] = _deep_merge(merged[key], value) if key in merged else copy.deepcopy(value)
        return merged
    return copy.deepcopy(override)


def _merge_panel_specs(panel_specs: List[Dict[str, Any]], overrides: Any) -> List[Dict[str, Any]]:
    merged_specs: List[Dict[str, Any]] = []
    override_rows = overrides if isinstance(overrides, list) else []
    for index, spec in enumerate(panel_specs):
        merged = dict(spec)
        if index < len(override_rows) and isinstance(override_rows[index], dict):
            merged = _deep_merge(merged, override_rows[index])
        merged_specs.append(merged)
    return merged_specs


def get_figure_config(figure_key: str) -> Dict[str, Any]:
    figures = FIGURE_PIPELINE_CONFIG.get('figures') or {}
    cfg = figures.get(figure_key)
    return copy.deepcopy(cfg) if isinstance(cfg, dict) else {}


def get_palette_color(label: str, *, figure_key: str | None = None, fallback: str = '#444444') -> str:
    if figure_key:
        palette = get_figure_config(figure_key).get('palette') or {}
        if label in palette:
            return str(palette[label])
    return str(PALETTE.get(label, fallback))


def load_json(rel_path: str) -> Dict[str, Any]:
    return json.loads((ROOT / rel_path).read_text(encoding='utf-8'))


def load_jsonl(rel_path: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with open(ROOT / rel_path, 'r', encoding='utf-8') as file_obj:
        for line in file_obj:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def speed_ms_to_fps(speed_ms_per_point: Any) -> float | None:
    if speed_ms_per_point is None:
        return None
    value = float(speed_ms_per_point)
    if value <= 0.0:
        return None
    return 1000.0 / value


def compute_inband_linearity_summary(rel_path: str, band_max_hz: float) -> Dict[str, Any]:
    payload = load_json(rel_path)
    rows = [
        row
        for row in payload['linearity_by_frequency']
        if float(row['frequency_hz']) <= band_max_hz
    ]
    if not rows:
        raise ValueError(f'No linearity points <= {band_max_hz} Hz in {rel_path}')
    comped = 100.0 * float(np.mean([1.0 - float(row['r_squared_comped']) for row in rows]))
    origin = 100.0 * float(np.mean([1.0 - float(row['r_squared_origin']) for row in rows]))
    return {
        'band_max_hz': band_max_hz,
        'frequency_count': len(rows),
        'frequencies_hz': [float(row['frequency_hz']) for row in rows],
        'full_frequency_count': len(payload['linearity_by_frequency']),
        'full_frequencies_hz': [float(row['frequency_hz']) for row in payload['linearity_by_frequency']],
        'comped_mean_percent': comped,
        'origin_mean_percent': origin,
    }


def load_metrics(rows: List[tuple[str, str]]) -> List[Dict[str, Any]]:
    data: List[Dict[str, Any]] = []
    for label, rel_path in rows:
        metrics_payload = load_json(rel_path)
        linearity_rel_path = str(Path(rel_path).with_name('linearity_by_frequency.json')).replace('\\', '/')
        linearity_summary = compute_inband_linearity_summary(linearity_rel_path, LINEARITY_INBAND_MAX_HZ)
        board_keil_speed_ms = metrics_payload.get('board_keil_speed')
        board_keil_fps = metrics_payload.get('board_keil_fps')
        if board_keil_fps is None:
            board_keil_fps = speed_ms_to_fps(board_keil_speed_ms)
        data.append({
            'label': label,
            'project_name': metrics_payload['project_name'],
            'metrics_path': rel_path,
            'freq_drift_hz': float(metrics_payload['freq_drift_hz']),
            'sens_drift_percent': float(metrics_payload['sens_drift_percent']),
            'linearity_percent': float(linearity_summary['comped_mean_percent']),
            'total_params': int(metrics_payload['total_params']),
            'epochs': int(metrics_payload['epochs']),
            'lr': float(metrics_payload['lr']),
            'loss_function': metrics_payload.get('loss_function', '-'),
            'board_qemu_mae': metrics_payload.get('board_qemu_mae'),
            'board_keil_mae': metrics_payload.get('board_keil_mae'),
            'board_keil_speed_ms': board_keil_speed_ms,
            'board_keil_fps': board_keil_fps,
            'board_inference_ep_path': metrics_payload.get('board_inference_ep_path'),
            'board_inference': metrics_payload.get('board_inference'),
            'origin_freq_drift_hz': float(metrics_payload['metric_details']['natural_frequency_drift_origin']['drift']),
            'origin_sens_drift_percent': float(metrics_payload['metric_details']['sensitivity_drift_origin']['drift']),
            'origin_linearity_percent': float(linearity_summary['origin_mean_percent']),
            'linearity_band_max_hz': float(linearity_summary['band_max_hz']),
            'linearity_band_count': int(linearity_summary['frequency_count']),
            'linearity_band_frequencies_hz': linearity_summary['frequencies_hz'],
            'linearity_full_frequency_count': int(linearity_summary['full_frequency_count']),
            'linearity_full_frequencies_hz': linearity_summary['full_frequencies_hz'],
            'calculation_standard': metrics_payload.get('calculation_standard'),
            'metric_details': metrics_payload.get('metric_details', {}),
        })
    return data


def interpolate_sensitivity_at_100hz(frequencies: List[float], gains: List[List[float]]) -> List[float]:
    return [float(np.interp(100.0, frequencies, row)) for row in gains]


def load_trajectories() -> Dict[str, Dict[str, List[float]]]:
    result: Dict[str, Dict[str, List[float]]] = {}
    for label, rel_path in TRAJECTORY_MODELS:
        payload = load_json(rel_path)
        magnitudes = payload['magnitudes']
        frequencies = payload['frequencies']
        if label == 'Origin':
            fn = _extract_natural_frequency_values(
                payload,
                use_origin=True,
                min_frequency_hz=DEFAULT_FREQ_DRIFT_INBAND_MIN_HZ,
                max_frequency_hz=DEFAULT_FREQ_DRIFT_INBAND_MAX_HZ,
            )
            sens = interpolate_sensitivity_at_100hz(frequencies, payload['gains_origin'])
        else:
            fn = _extract_natural_frequency_values(
                payload,
                use_origin=False,
                min_frequency_hz=DEFAULT_FREQ_DRIFT_INBAND_MIN_HZ,
                max_frequency_hz=DEFAULT_FREQ_DRIFT_INBAND_MAX_HZ,
            )
            sens = interpolate_sensitivity_at_100hz(frequencies, payload['gains_comped'])
        result[label] = {
            'magnitudes': magnitudes,
            'natural_frequency_hz': fn,
            'sensitivity_100hz': sens,
        }
    return result


def find_published_profile(entries: List[Dict[str, Any]], published_key: str | None = None) -> Dict[str, Any] | None:
    for item in entries:
        if bool(item.get('published', False)):
            return item
    if published_key is None:
        return None
    for item in entries:
        if str(item.get('key', '')) == str(published_key):
            return item
    return None


def parse_build_sizes(metrics_entry: Dict[str, Any]) -> Dict[str, Any] | None:
    board_inference = metrics_entry.get('board_inference') or {}
    published = find_published_profile(
        list(board_inference.get('keil_optimization_profiles') or []),
        board_inference.get('published_optimization_profile'),
    )
    if published and published.get('flash_bytes') is not None and published.get('ram_bytes') is not None:
        return {
            'build_output_path': published.get('build_output_path'),
            'flash_bytes': int(published['flash_bytes']),
            'ram_bytes': int(published['ram_bytes']),
        }

    ep = metrics_entry.get('board_inference_ep_path')
    if not ep:
        return None
    build_path = ROOT / ep / 'keil_project' / 'MDK-ARM' / 'output' / 'build_output_MET405.txt'
    if not build_path.exists():
        return None
    match = BUILD_PATTERN.search(build_path.read_text(encoding='utf-8'))
    if not match:
        return None
    code, ro, rw, zi = map(int, match.groups())
    return {
        'build_output_path': str(build_path.relative_to(ROOT)).replace('\\', '/'),
        'flash_bytes': code + ro,
        'ram_bytes': rw + zi,
        'code_bytes': code,
        'ro_bytes': ro,
        'rw_bytes': rw,
        'zi_bytes': zi,
    }


def enrich_with_deployment_fields(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    enriched: List[Dict[str, Any]] = []
    for row in rows:
        merged = dict(row)
        build = parse_build_sizes(row)
        if build:
            merged.update(build)
        enriched.append(merged)
    return enriched


def resolve_keil_build_sizes(ep_path: str, keil_payload: Dict[str, Any]) -> tuple[int, int]:
    published = find_published_profile(
        list(keil_payload.get('optimization_profiles') or []),
        (keil_payload.get('keil_config') or {}).get('published_optimization_profile'),
    )
    if published and published.get('flash_bytes') is not None and published.get('ram_bytes') is not None:
        return int(published['flash_bytes']), int(published['ram_bytes'])

    build_path = ROOT / ep_path / 'keil_project' / 'MDK-ARM' / 'output' / 'build_output_MET405.txt'
    build_match = BUILD_PATTERN.search(build_path.read_text(encoding='utf-8'))
    if not build_match:
        raise ValueError(f'Cannot parse Program Size in {build_path}')
    code, ro, rw, zi = map(int, build_match.groups())
    return code + ro, rw + zi


def load_lut_variants() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for label, ep_path in LUT_VARIANTS:
        benchmark_payload = load_json(f'{ep_path}/data/benchmark_summary.json')
        keil_payload = load_json(f'{ep_path}/data/keil_benchmark_summary.json')
        flash_bytes, ram_bytes = resolve_keil_build_sizes(ep_path, keil_payload)
        speed_ms = keil_payload.get('keil_speed_ms_per_point')
        if speed_ms is None:
            parsed_output = keil_payload.get('parsed_output') or {}
            wall_time_per_iter_ms = parsed_output.get('wall_time_per_iter_ms')
            record_count = int(keil_payload['validation']['record_count'])
            seq_len = int(keil_payload['validation']['seq_len'])
            if wall_time_per_iter_ms is None:
                raise KeyError(f'Cannot resolve keil speed in {ep_path}/data/keil_benchmark_summary.json')
            speed_ms = float(wall_time_per_iter_ms) / float(record_count * seq_len)
        else:
            speed_ms = float(speed_ms)
        rows.append({
            'label': label,
            'ep_path': ep_path,
            'qemu_mae': float(benchmark_payload['comparison']['mae']),
            'keil_mae': float(keil_payload['comparison']['mae']),
            'keil_speed_ms': speed_ms,
            'keil_fps': float(keil_payload.get('keil_speed_points_per_second') or speed_ms_to_fps(speed_ms)),
            'flash_bytes': flash_bytes,
            'ram_bytes': ram_bytes,
        })
    return rows


def load_lut_point_sweep() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    mode_labels = {
        'nearest': 'LUT nearest',
        'interp': 'LUT + interp',
    }
    for item in LUT_POINT_SWEEP:
        mode = str(item['mode'])
        ep_path = str(item['ep_path'])
        points = int(item['points'])
        if mode not in mode_labels:
            raise ValueError(f'Unsupported LUT sweep mode: {mode}')
        benchmark_payload = load_json(f'{ep_path}/data/benchmark_summary.json')
        keil_payload = load_json(f'{ep_path}/data/keil_benchmark_summary.json')
        flash_bytes, ram_bytes = resolve_keil_build_sizes(ep_path, keil_payload)
        rows.append({
            'mode': mode,
            'label': mode_labels[mode],
            'points': points,
            'ep_path': ep_path,
            'qemu_mae': float(benchmark_payload['comparison']['mae']),
            'flash_bytes': flash_bytes,
            'ram_bytes': ram_bytes,
        })
    return sorted(rows, key=lambda row: (row['points'], 0 if row['mode'] == 'nearest' else 1))


def load_convergence_curves(rows: List[tuple[str, str]]) -> List[Dict[str, Any]]:
    curves: List[Dict[str, Any]] = []
    for label, metrics_rel_path in rows:
        log_rel_path = str(Path(metrics_rel_path).with_name('training_log.jsonl')).replace('\\', '/')
        entries = load_jsonl(log_rel_path)
        epochs: List[int] = []
        val_losses: List[float] = []
        for entry in entries:
            epoch = entry.get('epoch')
            val_loss = entry.get('val_loss')
            if epoch is None or val_loss is None:
                continue
            epochs.append(int(epoch))
            val_losses.append(float(val_loss))
        if not epochs:
            raise ValueError(f'No training log rows found in {log_rel_path}')
        normalized = normalize_curve(val_losses)
        curves.append({
            'label': label,
            'epochs': epochs,
            'val_loss': val_losses,
            'normalized_val_loss': normalized,
            'smoothed_normalized_val_loss': smooth_curve(normalized, window=25),
            'training_log_path': log_rel_path,
        })
    return curves


def normalize_curve(values: List[float]) -> List[float]:
    array = np.asarray(values, dtype=float)
    anchor = float(array[0]) if len(array) else 1.0
    if not math.isfinite(anchor) or math.isclose(anchor, 0.0):
        anchor = 1.0
    return (array / anchor).tolist()


def smooth_curve(values: List[float], window: int = 25) -> List[float]:
    array = np.asarray(values, dtype=float)
    if len(array) <= 2 or window <= 1:
        return array.tolist()
    kernel = np.ones(min(window, len(array)), dtype=float)
    kernel /= kernel.sum()
    padded = np.pad(array, (len(kernel) // 2, len(kernel) - 1 - len(kernel) // 2), mode='edge')
    return np.convolve(padded, kernel, mode='valid').tolist()


def sanitize_for_public_json(value: Any) -> Any:
    if isinstance(value, dict):
        cleaned: Dict[str, Any] = {}
        for key, item in value.items():
            if ('compute' + '_cost') in str(key).lower():
                continue
            cleaned_item = sanitize_for_public_json(item)
            if cleaned_item is not None:
                cleaned[key] = cleaned_item
        return cleaned
    if isinstance(value, list):
        return [
            cleaned_item
            for item in value
            if (cleaned_item := sanitize_for_public_json(item)) is not None
        ]
    if isinstance(value, str):
        if ('compute' + '-cost') in value.lower():
            return None
        normalized = value.replace('\\', '/')
        root = str(ROOT).replace('\\', '/')
        if normalized.startswith(root + '/'):
            return normalized[len(root) + 1:]
        return normalized
    return value


def save_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.name.endswith('.raw.json') and 'paper_plot_style' not in payload:
        payload = {**payload, **paper_plot_style_payload()}
    safe_payload = sanitize_for_public_json(payload)
    path.write_text(json.dumps(safe_payload, ensure_ascii=False, indent=2), encoding='utf-8')


FORBIDDEN_RAW_TITLE_KEYS = {
    'title',
    'titles',
    'subtitle',
    'subtitles',
    'suptitle',
    'suptitles',
    'figure_title',
    'figure_titles',
    'panel_title',
    'panel_titles',
    'subplot_title',
    'subplot_titles',
    'axis_title',
    'axes_title',
    'plot_title',
    'plot_titles',
    'legend_title',
    'legend_titles',
}
RAW_TITLE_ARTIFACT_KEYS = {
    'title_artifacts',
    'matplotlib_title_artifacts',
    'manual_title_artifacts',
    'visual_title_artifacts',
}


def _clean_title_text(text: Any) -> str:
    return str(text or '').strip()


def collect_matplotlib_title_artifacts(fig: Any) -> List[Dict[str, Any]]:
    artifacts: List[Dict[str, Any]] = []
    suptitle = getattr(fig, '_suptitle', None)
    if suptitle is not None:
        text = _clean_title_text(suptitle.get_text())
        if text:
            artifacts.append({'kind': 'figure_suptitle', 'text': text})

    for ax_index, ax in enumerate(getattr(fig, 'axes', [])):
        if hasattr(ax, 'get_title'):
            for loc in ('left', 'center', 'right'):
                text = _clean_title_text(ax.get_title(loc=loc))
                if text:
                    artifacts.append({
                        'kind': 'axes_title',
                        'axis_index': ax_index,
                        'location': loc,
                        'text': text,
                    })
        legend = ax.get_legend() if hasattr(ax, 'get_legend') else None
        if legend is not None:
            text = _clean_title_text(legend.get_title().get_text())
            if text:
                artifacts.append({
                    'kind': 'legend_title',
                    'axis_index': ax_index,
                    'text': text,
                })

    for legend_index, legend in enumerate(getattr(fig, 'legends', [])):
        text = _clean_title_text(legend.get_title().get_text())
        if text:
            artifacts.append({
                'kind': 'figure_legend_title',
                'legend_index': legend_index,
                'text': text,
            })
    return artifacts


def _raw_title_audit_payload(fig: Any) -> Dict[str, Any]:
    return {'matplotlib_title_artifacts': collect_matplotlib_title_artifacts(fig)}


def _save_matplotlib_figure(
    fig: Any,
    out: Path,
    *,
    raw_payload: Dict[str, Any] | None = None,
    **savefig_kwargs: Any,
) -> str:
    out.parent.mkdir(parents=True, exist_ok=True)
    merged_raw = dict(raw_payload or {})
    audit_payload = _raw_title_audit_payload(fig)
    visual_audit = audit_matplotlib_figure(fig, context=str(out.relative_to(PAPER_DIR)).replace('\\', '/'))
    existing_visual_audit = merged_raw.pop(VISUAL_AUDIT_KEY, None)
    existing = merged_raw.get('matplotlib_title_artifacts')
    if existing:
        audit_payload['matplotlib_title_artifacts'] = list(existing) + audit_payload['matplotlib_title_artifacts']
    merged_raw.update(audit_payload)
    merged_raw.update(paper_plot_style_payload())
    fig.savefig(out, **savefig_kwargs)
    image_audit = audit_image_file(out, context=str(out.relative_to(PAPER_DIR)).replace('\\', '/'))
    audits_to_combine = [audit for audit in [existing_visual_audit, visual_audit, image_audit] if audit]
    merged_raw[VISUAL_AUDIT_KEY] = combine_audits(*audits_to_combine, context=str(out.relative_to(PAPER_DIR)).replace('\\', '/'))
    plt.close(fig)
    save_json(out.with_suffix('.raw.json'), merged_raw)
    return out.name


def _normalize_raw_key(key: Any) -> str:
    return str(key).strip().lower().replace('-', '_').replace(' ', '_')


def _raw_title_value_present(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip()) and value.strip().lower() not in {'none', 'null', 'n/a', 'na'}
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, list):
        return any(_raw_title_value_present(item) for item in value)
    if isinstance(value, dict):
        return any(_raw_title_value_present(item) for item in value.values())
    return bool(value)


def _summarize_raw_title_value(value: Any) -> str:
    if isinstance(value, dict):
        for key in ('text', 'title', 'subtitle', 'kind'):
            if key in value and _raw_title_value_present(value[key]):
                return str(value[key])
        return json.dumps(value, ensure_ascii=False)[:160]
    if isinstance(value, list):
        first = next((item for item in value if _raw_title_value_present(item)), '')
        return _summarize_raw_title_value(first)
    return str(value)


def _iter_raw_title_violations(value: Any, json_path: tuple[str, ...] = ()):
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = _normalize_raw_key(key)
            child_path = json_path + (str(key),)
            if normalized in RAW_TITLE_ARTIFACT_KEYS and _raw_title_value_present(item):
                yield child_path, _summarize_raw_title_value(item)
            elif normalized in FORBIDDEN_RAW_TITLE_KEYS and _raw_title_value_present(item):
                yield child_path, _summarize_raw_title_value(item)
            yield from _iter_raw_title_violations(item, child_path)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _iter_raw_title_violations(item, json_path + (f'[{index}]',))


def validate_raw_title_free(raw_paths: List[Path] | None = None) -> None:
    paths = raw_paths if raw_paths is not None else sorted(FIGURES_DIR.rglob('*.raw.json'))
    violations: List[str] = []
    for raw_path in paths:
        raw_path = Path(raw_path).resolve()
        try:
            payload = json.loads(raw_path.read_text(encoding='utf-8'))
        except json.JSONDecodeError as exc:
            raise ValueError(f'Invalid figure raw JSON: {raw_path}') from exc
        try:
            rel_path = str(raw_path.relative_to(ROOT)).replace('\\', '/')
        except ValueError:
            rel_path = str(raw_path).replace('\\', '/')
        for json_path, text in _iter_raw_title_violations(payload):
            locator = '.'.join(json_path)
            violations.append(f'{rel_path}:{locator} -> {text}')
    if violations:
        preview = '\n'.join(f' - {item}' for item in violations[:60])
        if len(violations) > 60:
            preview += f'\n - ... {len(violations) - 60} more'
        raise ValueError(
            'Paper figure raw title audit failed. Remove figure, subplot, '
            f'or legend titles before publication.\n{preview}'
        )


def validate_raw_publication_quality(raw_paths: List[Path] | None = None) -> None:
    paths = raw_paths if raw_paths is not None else sorted(FIGURES_DIR.rglob('*.raw.json'))
    validate_raw_visual_quality(paths, root=ROOT)


MONTAGE_PANEL_DIR = FIGURES_DIR / '_montage_panels'
SUBFIGURE_LABEL_TARGET_PT = 8.0
SN_A4_TEXT_WIDTH_PT = 372.0


def panel_source_name(name: str) -> str:
    return str(Path('_montage_panels') / name).replace('\\', '/')


def save_panel_figure(
    fig: Any,
    name: str,
    *,
    dpi: int = 300,
    pad_inches: float = 0.0,
    margin_left: float = 0.0,
    margin_right: float = 0.0,
    margin_top: float = 0.0,
    margin_bottom: float = 0.0,
    raw_payload: Dict[str, Any] | None = None,
) -> str:
    rel_name = panel_source_name(name)
    out = FIGURES_DIR / rel_name
    payload = {
        'figure': rel_name,
        'source_trace': 'docs/paper/src/paper_pipeline.py:save_panel_figure',
    }
    if raw_payload:
        payload.update(raw_payload)

    has_margin = any(m != 0.0 for m in [margin_left, margin_right, margin_top, margin_bottom])
    if has_margin:
        # Save with pad_inches to expand content area (before tight bbox),
        # then crop per-side margins from the result
        tmp_out = out.with_name(out.name + '.tmp.png')
        _save_matplotlib_figure(fig, tmp_out, raw_payload=payload, dpi=dpi, bbox_inches='tight', pad_inches=pad_inches)
        try:
            from PIL import Image
            img = Image.open(tmp_out)
            w_px, h_px = img.size
            left_px = int(round(margin_left * dpi))
            right_px = int(round(margin_right * dpi))
            top_px = int(round(margin_top * dpi))
            bottom_px = int(round(margin_bottom * dpi))
            cropped = img.crop((left_px, top_px, w_px - right_px, h_px - bottom_px))
            cropped.save(out, dpi=(dpi, dpi))
            img.close()
            cropped.close()
            tmp_raw = tmp_out.with_suffix('.raw.json')
            if tmp_raw.exists():
                cropped_raw = json.loads(tmp_raw.read_text(encoding='utf-8'))
                cropped_raw.update({
                    'postprocess': 'per-side margin crop after tight matplotlib save',
                    'crop_margins_inches': {
                        'left': margin_left,
                        'right': margin_right,
                        'top': margin_top,
                        'bottom': margin_bottom,
                    },
                    'cropped_output': str(out.relative_to(PAPER_DIR)).replace('\\', '/'),
                })
                save_json(out.with_suffix('.raw.json'), cropped_raw)
                tmp_raw.unlink()
            tmp_out.unlink()
        except Exception:
            # PIL not available, fall back to tight save with uniform pad_inches
            _save_matplotlib_figure(fig, out, raw_payload=payload, dpi=dpi, bbox_inches='tight', pad_inches=pad_inches)
    else:
        _save_matplotlib_figure(fig, out, raw_payload=payload, dpi=dpi, bbox_inches='tight', pad_inches=pad_inches)
    return rel_name


def format_optional(value: Any, fmt: str) -> str:
    if value is None:
        return '-'
    return fmt.format(value)


def format_profile_note(profile: Dict[str, Any]) -> str:
    status = str(profile.get('status', 'unknown'))
    if status == 'build_failed':
        return 'build failed (flash overflow at -O0)'
    if status == 'completed':
        return 'completed'
    return status.replace('_', ' ')


def plot_radar(ax: Any, rows: List[Dict[str, Any]]) -> None:
    categories = [item[0] for item in RADAR_METRICS]
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]

    normalized: Dict[str, List[float]] = {}
    for metric_name, key, direction in RADAR_METRICS:
        values = [float(row[key]) for row in rows]
        if direction == 'min':
            best = min(values)
            normalized[metric_name] = [best / value if value > 0 else 0.0 for value in values]
        else:
            best = max(values)
            normalized[metric_name] = [value / best if best > 0 else 0.0 for value in values]

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_ylim(0.0, 1.05)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(['0.25', '0.50', '0.75', '1.00'])

    for index, row in enumerate(rows):
        values = [normalized[metric_name][index] for metric_name, _, _ in RADAR_METRICS]
        values += values[:1]
        color = PALETTE.get(row['label'], '#444444')
        linewidth = 2.6 if row['label'] in {'Wiener-KAN', 'MAE+AFMAE'} else 1.5
        alpha = 0.18 if row['label'] in {'Wiener-KAN', 'MAE+AFMAE'} else 0.07
        ax.plot(angles, values, color=color, linewidth=linewidth, label=row['label'])
        ax.fill(angles, values, color=color, alpha=alpha)


def make_trajectory_figure(trajectories: Dict[str, Dict[str, List[float]]]) -> str:
    cfg = get_figure_config('fig_01_drift_trajectories')
    font_scale = float(cfg.get('font_scale', 1.0))
    xy_cfg = cfg.get('xy_plot') if isinstance(cfg.get('xy_plot'), dict) else {}
    label_fontsize = float(xy_cfg.get('label_fontsize', 10.0 * font_scale))
    tick_fontsize = float(xy_cfg.get('tick_fontsize', 9.0 * font_scale))
    labelpad = float(xy_cfg.get('labelpad', 4.0))
    tick_pad = float(xy_cfg.get('tick_pad', 3.0))
    fig, axes = plt.subplots(
        1,
        2,
        figsize=_as_float_tuple(cfg.get('figsize'), (12.5, 4.8)),
        constrained_layout=True,
    )
    for label, series in trajectories.items():
        color = get_palette_color(label, figure_key='fig_01_drift_trajectories')
        linestyle = '--' if label == 'Origin' else '-'
        linewidth = float(cfg.get('wiener_linewidth', 2.6)) if label == 'Wiener-KAN' else float(cfg.get('other_linewidth', 2.0))
        axes[0].plot(series['magnitudes'], series['natural_frequency_hz'], label=label, color=color, linestyle=linestyle, linewidth=linewidth)
        axes[1].plot(series['magnitudes'], series['sensitivity_100hz'], label=label, color=color, linestyle=linestyle, linewidth=linewidth)

    axes[0].set_xlabel('Magnitude (m/s^2)', fontsize=label_fontsize, labelpad=labelpad)
    axes[0].set_ylabel('Peak frequency (Hz)', fontsize=label_fontsize, labelpad=labelpad)
    axes[1].set_xlabel('Magnitude (m/s^2)', fontsize=label_fontsize, labelpad=labelpad)
    axes[1].set_ylabel('Sensitivity at 100 Hz (%)', fontsize=label_fontsize, labelpad=labelpad)
    for ax in axes:
        ax.tick_params(axis='both', which='major', labelsize=tick_fontsize, pad=tick_pad)
    if 'xlim' in xy_cfg:
        xlim = _as_float_tuple(xy_cfg.get('xlim'), axes[0].get_xlim())
        for ax in axes:
            ax.set_xlim(*xlim)
    if 'ylim' in xy_cfg:
        ylim = _as_float_tuple(xy_cfg.get('ylim'), axes[0].get_ylim())
        for ax in axes:
            ax.set_ylim(*ylim)
    if 'left_ylim' in xy_cfg:
        axes[0].set_ylim(*_as_float_tuple(xy_cfg.get('left_ylim'), axes[0].get_ylim()))
    if 'right_ylim' in xy_cfg:
        axes[1].set_ylim(*_as_float_tuple(xy_cfg.get('right_ylim'), axes[1].get_ylim()))
    legend_cfg = cfg.get('legend') or {}
    axes[1].legend(
        loc=str(legend_cfg.get('loc', 'upper center')),
        bbox_to_anchor=tuple(legend_cfg.get('bbox_to_anchor', [0.5, 1.18])),
        ncol=int(legend_cfg.get('ncol', 2)),
        frameon=bool(legend_cfg.get('frameon', True)),
        fontsize=8.5 * font_scale,
    )
    out = FIGURES_DIR / 'fig_01_drift_trajectories.png'
    return _save_matplotlib_figure(
        fig,
        out,
        raw_payload={'trajectories': trajectories},
        bbox_inches='tight',
    )


def make_metric_range_panel_specs(
    main_rows: List[Dict[str, Any]],
    *,
    output_prefix: str,
    label_offset: int = 0,
    fit_width: int = 1650,
    trim_border: int = 28,
    figsize: tuple[float, float] = (4.8, 4.2),
    figure_key: str | None = None,
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    cfg = get_figure_config(figure_key) if figure_key else {}
    range_cfg = cfg.get('range_panels') or {}
    labels = [row['label'] for row in main_rows]
    x = np.arange(len(labels))
    colors = [
        str(range_cfg.get('highlight_color', '#0f6c5c')) if label == 'Wiener-KAN' else str(range_cfg.get('baseline_color', '#777777'))
        for label in labels
    ]
    dist_specs = [
        ('natural_frequency_drift', 'fn', 'Natural frequency (Hz)'),
        ('sensitivity_drift', 'sens', 'Sensitivity at 100 Hz'),
        ('linearity', 'linearity', 'Linearity error (%)'),
    ]
    raw_distribution_rows: List[Dict[str, Any]] = []
    distribution_panels: List[Dict[str, Any]] = []
    for idx, (detail_key, metric_name, ylabel) in enumerate(dist_specs):
        fig_dist, ax = plt.subplots(
            figsize=_as_float_tuple(range_cfg.get('figsize'), figsize),
            constrained_layout=True,
        )
        centers = []
        lower = []
        upper = []
        panel_rows = []
        for row in main_rows:
            detail = row.get('metric_details', {}).get(detail_key, {})
            if detail_key == 'linearity':
                center = float(detail.get('mean', row['linearity_percent']))
            else:
                center = float(detail.get('median', 0.5 * (float(detail.get('min', 0.0)) + float(detail.get('max', 0.0)))))
            min_value = float(detail.get('min', center))
            max_value = float(detail.get('max', center))
            centers.append(center)
            lower.append(max(center - min_value, 0.0))
            upper.append(max(max_value - center, 0.0))
            panel_row = {
                'label': row['label'],
                'metric': metric_name,
                'center': center,
                'min': min_value,
                'max': max_value,
            }
            panel_rows.append(panel_row)
            raw_distribution_rows.append(panel_row)
        ax.bar(x, centers, color=colors, alpha=float(range_cfg.get('bar_alpha', 0.72)))
        ax.errorbar(
            x,
            centers,
            yerr=np.vstack([lower, upper]),
            fmt='none',
            ecolor=str(range_cfg.get('error_color', '#222222')),
            elinewidth=float(range_cfg.get('error_linewidth', 1.1)),
            capsize=float(range_cfg.get('error_capsize', 3.0)),
        )
        ax.set_ylabel(ylabel)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=float(range_cfg.get('xtick_rotation', 45.0)), ha='right')
        ax.grid(axis='y', alpha=float(range_cfg.get('grid_alpha', 0.25)))
        panel = save_panel_figure(
            fig_dist,
            f'{output_prefix}_{idx + 1}_{metric_name}.png',
            raw_payload={
                'source_trace': 'paper results payload metric_details min/median/mean/max fields',
                'metric': metric_name,
                'rows': panel_rows,
            },
        )
        distribution_panels.append({
            'source': panel,
            'label': f'({chr(97 + label_offset + idx)})',
            'fit_width': int(range_cfg.get('fit_width', fit_width)),
            'trim_border': int(range_cfg.get('trim_border', trim_border)),
            'align_y': 'top',
        })
    return distribution_panels, raw_distribution_rows


def make_horizontal_figure(main_rows: List[Dict[str, Any]], origin: Dict[str, float], main_curves: List[Dict[str, Any]]) -> str:
    cfg = get_figure_config('fig_02_horizontal_summary')
    labels = [row['label'] for row in main_rows]
    x = np.arange(len(labels))
    range_cfg = cfg.get('range_panels') or {}
    range_panels, range_rows = make_metric_range_panel_specs(
        main_rows,
        output_prefix='fig_02_horizontal_summary',
        label_offset=0,
        fit_width=int(range_cfg.get('fit_width', 1680)),
        trim_border=int(range_cfg.get('trim_border', 28)),
        figsize=_as_float_tuple(range_cfg.get('figsize'), (4.8, 4.2)),
        figure_key='fig_02_horizontal_summary',
    )

    throughput_cfg = cfg.get('throughput_panel') or {}
    fig_speed, ax_speed = plt.subplots(
        figsize=_as_float_tuple(throughput_cfg.get('figsize'), (7.2, 4.6)),
        constrained_layout=True,
    )
    speed_values = [float(row['board_keil_fps']) for row in main_rows]
    colors = [get_palette_color(row['label'], figure_key='fig_02_horizontal_summary') for row in main_rows]
    ax_speed.bar(
        x,
        speed_values,
        color=colors,
        alpha=float(throughput_cfg.get('bar_alpha', 0.86)),
        edgecolor=str(throughput_cfg.get('edge_color', '#222222')),
        linewidth=float(throughput_cfg.get('edge_linewidth', 0.5)),
    )
    for idx, row in enumerate(main_rows):
        ax_speed.text(
            idx,
            speed_values[idx] * float(throughput_cfg.get('annotation_y_ratio', 1.02)),
            f"MAE={row['board_keil_mae']:.1e}",
            ha='center',
            va='bottom',
            fontsize=float(throughput_cfg.get('annotation_fontsize', 7.8)),
            rotation=90,
        )
    ax_speed.set_xticks(x)
    ax_speed.set_xticklabels(labels, rotation=float(throughput_cfg.get('xtick_rotation', 25)), ha='right')
    ax_speed.set_ylabel('KEIL throughput (points/s; higher is better)')
    ax_speed.set_ylim(0.0, max(speed_values) * float(throughput_cfg.get('ylim_pad_ratio', 1.30)))
    ax_speed.grid(True, axis='y', linestyle='--', alpha=float(throughput_cfg.get('grid_alpha', 0.35)))
    panel_speed = save_panel_figure(fig_speed, 'fig_02_horizontal_summary_4_throughput.png')

    radar_cfg = cfg.get('radar_panel') or {}
    fig_radar = plt.figure(
        figsize=_as_float_tuple(radar_cfg.get('figsize'), (6.8, 5.3)),
        constrained_layout=True,
    )
    ax_radar = fig_radar.add_subplot(111, polar=True)
    plot_radar(ax_radar, main_rows)
    ax_radar.legend(
        loc=str(radar_cfg.get('legend_loc', 'upper center')),
        bbox_to_anchor=tuple(radar_cfg.get('legend_bbox_to_anchor', [0.5, -0.12])),
        ncol=int(radar_cfg.get('legend_ncol', 3)),
        frameon=bool(radar_cfg.get('legend_frameon', False)),
    )
    panel_radar = save_panel_figure(fig_radar, 'fig_02_horizontal_summary_5_radar.png')

    curve_cfg = cfg.get('convergence_panel') or {}
    fig_curve, ax_curve = plt.subplots(
        figsize=_as_float_tuple(curve_cfg.get('figsize'), (7.2, 4.6)),
        constrained_layout=True,
    )
    for curve in main_curves:
        color = get_palette_color(curve['label'], figure_key='fig_02_horizontal_summary')
        linewidth = float(curve_cfg.get('wiener_linewidth', 2.6)) if curve['label'] == 'Wiener-KAN' else float(curve_cfg.get('other_linewidth', 1.5))
        ax_curve.plot(curve['epochs'], curve['smoothed_normalized_val_loss'], color=color, linewidth=linewidth, label=curve['label'])
    ax_curve.set_xlabel('Epoch')
    ax_curve.set_ylabel('Normalized val loss')
    ax_curve.set_xlim(left=0)
    ax_curve.set_ylim(bottom=0)
    ax_curve.legend(
        ncol=int(curve_cfg.get('legend_ncol', 2)),
        frameon=bool(curve_cfg.get('legend_frameon', True)),
    )
    panel_curve = save_panel_figure(fig_curve, 'fig_02_horizontal_summary_6_convergence.png')

    name = make_bitmap_montage(
        'fig_02_horizontal_summary.png',
        range_panels + [
            {'source': panel_speed, 'label': '(d)', 'fit_width': 1680, 'align_y': 'top', 'trim_border': 35},
            {'source': panel_radar, 'label': '(e)', 'fit_width': 1680, 'align_y': 'top', 'trim_border': 35},
            {'source': panel_curve, 'label': '(f)', 'fit_width': 1680, 'align_y': 'top', 'trim_border': 35},
        ],
        layout='matrix',
        rows=2,
        cols=3,
        padding=[75, 70, 75, 70],
        gutter=(85, 95),
        label_font_size=58,
        note='Composes the metric-range, throughput, radar and convergence panels with the unified bitmap montage module.',
        latex_width_fraction=0.98,
        figure_key='fig_02_horizontal_summary',
    )
    raw_path = FIGURES_DIR / 'fig_02_horizontal_summary.raw.json'
    raw_payload = json.loads(raw_path.read_text(encoding='utf-8'))
    raw_payload.update({
        'origin_metric_reference': origin,
        'metric_range_rows': range_rows,
        'panel_policy': 'The previous physical-metric bar panel is replaced by three metric-range panels.',
    })
    save_json(raw_path, raw_payload)
    return name


def _loss_panel_slug(label: str) -> str:
    slug = re.sub(r'[^a-z0-9]+', '', label.lower())
    return slug or 'loss'


def make_loss_ablation_panel_specs(
    loss_rows: List[Dict[str, Any]],
    loss_curves: List[Dict[str, Any]],
    *,
    label_offset: int = 0,
    fit_width: int = 1500,
    trim_border: int = 26,
    figure_key: str | None = None,
) -> List[Dict[str, Any]]:
    cfg = get_figure_config(figure_key) if figure_key else {}
    panel_cfg = cfg.get('curve_panels') or {}
    curve_map = {curve['label']: curve for curve in loss_curves}
    ordered_labels = [row['label'] for row in loss_rows if row['label'] in curve_map]
    ymax = max(
        max(float(value) for value in curve_map[label]['smoothed_normalized_val_loss'])
        for label in ordered_labels
    )
    panel_specs: List[Dict[str, Any]] = []
    for idx, label in enumerate(ordered_labels):
        curve = curve_map[label]
        fig, ax = plt.subplots(
            figsize=_as_float_tuple(panel_cfg.get('figsize'), (4.2, 4.2)),
            constrained_layout=True,
        )
        color = get_palette_color(label, figure_key=figure_key)
        ax.plot(
            curve['epochs'],
            curve['smoothed_normalized_val_loss'],
            color=color,
            linewidth=float(panel_cfg.get('line_width', 2.6)),
            label=label,
        )
        ax.set_xlabel('Epoch')
        ax.set_ylabel('Normalized val loss')
        ax.set_xlim(left=0)
        ax.set_ylim(0.0, ymax * float(panel_cfg.get('ylim_pad_ratio', 1.05)))
        ax.legend(
            frameon=bool(panel_cfg.get('legend_frameon', True)),
            loc=str(panel_cfg.get('legend_loc', 'upper right')),
        )
        ax.grid(True, alpha=float(panel_cfg.get('grid_alpha', 0.25)))
        source = save_panel_figure(fig, f'fig_03_loss_ablation_{idx + 1}_{_loss_panel_slug(label)}.png', raw_payload={
            'source': 'paper results payload',
            'label': label,
            'epoch_count': len(curve['epochs']),
            'final_normalized_val_loss': float(curve['smoothed_normalized_val_loss'][-1]),
        })
        panel_specs.append({
            'source': source,
            'label': f'({chr(97 + label_offset + idx)})',
            'fit_width': int(panel_cfg.get('fit_width', fit_width)),
            'fit_height': int(panel_cfg.get('fit_height', panel_cfg.get('fit_width', fit_width))),
            'trim_border': int(panel_cfg.get('trim_border', trim_border)),
            'align_y': 'top',
        })
    return panel_specs


def make_loss_ablation_figure(loss_rows: List[Dict[str, Any]], loss_curves: List[Dict[str, Any]]) -> str:
    panel_specs = make_loss_ablation_panel_specs(
        loss_rows,
        loss_curves,
        label_offset=0,
        fit_width=1550,
        figure_key='fig_03_loss_ablation',
    )
    name = make_bitmap_montage(
        'fig_03_loss_ablation.png',
        panel_specs,
        layout='horizontal',
        padding=[65, 60, 65, 60],
        gutter=(70, 60),
        label_font_size=46,
        note='Composes the loss-ablation convergence panels as one row of square panels.',
        latex_width_fraction=0.98,
        figure_key='fig_03_loss_ablation',
    )
    raw_path = FIGURES_DIR / 'fig_03_loss_ablation.raw.json'
    raw_payload = json.loads(raw_path.read_text(encoding='utf-8'))
    raw_payload.update({
        'loss_ablation': [row['label'] for row in loss_rows],
        'layout': 'one horizontal row of square convergence panels',
    })
    save_json(raw_path, raw_payload)
    return name


def make_structure_figure(rows: List[Dict[str, Any]]) -> str:
    cfg = get_figure_config('fig_04_structure_ablation')
    fig, axes = plt.subplots(
        1,
        3,
        figsize=_as_float_tuple(cfg.get('figsize'), (14.2, 4.6)),
        constrained_layout=True,
    )
    labels = [row['label'] for row in rows]
    colors = [get_palette_color(row['label'], figure_key='fig_04_structure_ablation') for row in rows]
    specs = [
        ('freq_drift_hz', 'Freq drift (Hz)', True),
        ('sens_drift_percent', 'Sensitivity drift (%)', False),
        ('linearity_percent', 'In-band linearity error (%)', True),
    ]
    for ax, (key, title, use_log) in zip(axes, specs):
        ax.bar(labels, [row[key] for row in rows], color=colors, alpha=float(cfg.get('bar_alpha', 0.88)))
        ax.set_ylabel(title)
        if use_log:
            ax.set_yscale('log')
        ax.tick_params(axis='x', rotation=float(cfg.get('xtick_rotation', 25.0)))
    out = FIGURES_DIR / 'fig_04_structure_ablation.png'
    return _save_matplotlib_figure(
        fig,
        out,
        raw_payload={'structure_ablation': rows},
        bbox_inches='tight',
    )


def load_wiener_optimization_profiles() -> List[Dict[str, Any]]:
    payload = load_json('ex_projects/inference/qemu-c-inference/frikan_h8u6l6_e1k_lr7e4/data/keil_benchmark_summary.json')
    rows: List[Dict[str, Any]] = []
    label_map = {
        'o0': '-O0',
        'o2': '-O2',
        'ofast_lto': '-Ofast + LTO',
        'project_default': 'Project default',
    }
    for item in payload.get('optimization_profiles', []):
        key = str(item.get('key', ''))
        fps = item.get('keil_speed_points_per_second')
        if fps is None and item.get('keil_speed_ms_per_point') is not None:
            fps = speed_ms_to_fps(item.get('keil_speed_ms_per_point'))
        rows.append({
            'key': key,
            'label': label_map.get(key, key),
            'status': str(item.get('status', 'unknown')),
            'published': bool(item.get('published', False)),
            'keil_speed_ms': item.get('keil_speed_ms_per_point'),
            'keil_fps': fps,
            'flash_bytes': item.get('flash_bytes'),
            'ram_bytes': item.get('ram_bytes'),
        })
    return rows


def make_lut_point_tradeoff_figure(rows: List[Dict[str, Any]]) -> str:
    cfg = get_figure_config('fig_05_onboard_inference')
    panel_cfg = cfg.get('lut_tradeoff_panel') or {}
    fig, ax_mae = plt.subplots(figsize=_as_float_tuple(panel_cfg.get('figsize'), (6.8, 4.2)))
    ax_flash = ax_mae.twinx()
    style_map = {
        'nearest': {'label': 'LUT nearest', 'color': str(panel_cfg.get('nearest_color', '#c96b00'))},
        'interp': {'label': 'LUT + interp', 'color': str(panel_cfg.get('interp_color', '#0f6c5c'))},
    }
    legend_handles: List[Any] = []
    legend_labels: List[str] = []
    for mode in ['nearest', 'interp']:
        subset = [row for row in rows if row['mode'] == mode]
        if not subset:
            continue
        subset.sort(key=lambda row: int(row['points']))
        x = np.array([int(row['points']) for row in subset], dtype=float)
        qemu_mae = np.array([float(row['qemu_mae']) for row in subset], dtype=float)
        flash_kb = np.array([float(row['flash_bytes']) / 1024.0 for row in subset], dtype=float)
        style = style_map[mode]
        mae_handle, = ax_mae.plot(
            x,
            qemu_mae,
            color=style['color'],
            marker='o',
            markersize=float(panel_cfg.get('mae_marker_size', 5.2)),
            linewidth=float(panel_cfg.get('mae_linewidth', 2.2)),
            label=f"{style['label']} MAE",
        )
        flash_handle, = ax_flash.plot(
            x,
            flash_kb,
            color=style['color'],
            marker='s',
            markersize=float(panel_cfg.get('flash_marker_size', 4.8)),
            linewidth=float(panel_cfg.get('flash_linewidth', 2.0)),
            linestyle='--',
            label=f"{style['label']} Flash",
        )
        legend_handles.extend([mae_handle, flash_handle])
        legend_labels.extend([f"{style['label']} MAE", f"{style['label']} Flash"])

    unique_points = sorted({int(row['points']) for row in rows})
    ax_mae.set_xlabel('LUT quantization points')
    ax_mae.set_ylabel('QEMU-MAE against TensorFlow')
    ax_mae.set_yscale('log')
    ax_flash.set_ylabel('Flash usage (KB)')
    ax_mae.set_xticks(unique_points)
    ax_mae.set_xlim(
        left=max(unique_points[0] - int(panel_cfg.get('x_left_margin', 30)), 0),
        right=unique_points[-1] + int(panel_cfg.get('x_right_margin', 35)),
    )
    ax_mae.grid(True, axis='both', alpha=float(panel_cfg.get('grid_alpha', 0.22)))
    ax_mae.legend(
        legend_handles,
        legend_labels,
        loc='lower center',
        bbox_to_anchor=(0.5, 1.05),
        frameon=False,
        fontsize=float(panel_cfg.get('legend_fontsize', 7.2)),
        ncol=4,
        borderaxespad=0.0,
        handlelength=1.9,
        columnspacing=1.1,
    )
    margins = panel_cfg.get('margins') or {}
    fig.subplots_adjust(
        left=float(margins.get('left', 0.11)),
        right=float(margins.get('right', 0.90)),
        bottom=float(margins.get('bottom', 0.16)),
        top=float(margins.get('top', 0.77)),
    )
    panel_rows = []
    for row in rows:
        panel_rows.append({
            'mode': row['mode'],
            'label': row['label'],
            'points': int(row['points']),
            'qemu_mae': float(row['qemu_mae']),
            'flash_kb': float(row['flash_bytes']) / 1024.0,
        })
    return save_panel_figure(
        fig,
        'fig_05_onboard_inference_d_lut_point_tradeoff.png',
        raw_payload={
            'source_trace': 'paper results payload lut_point_sweep field',
            'rows': panel_rows,
            'axis_encoding': {
                'x': 'LUT quantization points',
                'left_y': 'QEMU-MAE against TensorFlow',
                'right_y': 'Flash usage (KB)',
                'line_style': 'metric type',
                'color': 'LUT lookup mode',
            },
            'panel_policy': 'Panel d sweeps LUT point count for the same Wiener-KAN weights and compares nearest lookup against linear interpolation.',
        },
    )


def make_onboard_figure(
    deploy_rows: List[Dict[str, Any]],
    lut_rows: List[Dict[str, Any]],
    lut_point_rows: List[Dict[str, Any]],
) -> str:
    cfg = get_figure_config('fig_05_onboard_inference')
    # Always refresh the shared workflow panels so Fig. 12 and the standalone
    # workflow figure stay visually consistent after layout tweaks.
    make_board_inference_validation_workflow_figure()
    panel_export = panel_source_name('fig_17_board_inference_validation_workflow_a_export.png')
    panel_validate = panel_source_name('fig_17_board_inference_validation_workflow_b_validate.png')

    performance_rows: List[Dict[str, Any]] = []
    for row in deploy_rows:
        if row['label'] == 'Wiener-KAN':
            continue
        if row.get('ram_bytes') is None or row.get('board_keil_mae') is None or row.get('board_keil_fps') is None:
            continue
        performance_rows.append({
            'label': row['label'],
            'category': 'Baseline export',
            'ram_kb': float(row['ram_bytes']) / 1024.0,
            'flash_kb': float(row['flash_bytes']) / 1024.0 if row.get('flash_bytes') is not None else None,
            'keil_mae': float(row['board_keil_mae']),
            'qemu_mae': float(row['board_qemu_mae']),
            'keil_fps': float(row['board_keil_fps']),
            'marker': 'o',
        })

    lut_label_map = {
        'LUT nearest': 'Wiener-KAN\n(LUT nearest)',
        'LUT + interp': 'Wiener-KAN\n(LUT interp)',
        'No LUT exact': 'Wiener-KAN\n(No LUT)',
    }
    for row in lut_rows:
        if row.get('ram_bytes') is None or row.get('keil_mae') is None or row.get('keil_fps') is None:
            continue
        performance_rows.append({
            'label': lut_label_map.get(row['label'], f"Wiener-KAN\n({row['label']})"),
            'source_label': row['label'],
            'category': 'Wiener-KAN variant',
            'ram_kb': float(row['ram_bytes']) / 1024.0,
            'flash_kb': float(row['flash_bytes']) / 1024.0 if row.get('flash_bytes') is not None else None,
            'keil_mae': float(row['keil_mae']),
            'qemu_mae': float(row['qemu_mae']),
            'keil_fps': float(row['keil_fps']),
            'marker': 'D',
        })

    perf_cfg = cfg.get('performance_panel') or {}
    fig_perf, ax_perf = plt.subplots(
        figsize=_as_float_tuple(perf_cfg.get('figsize'), (6.0, 4.4)),
        constrained_layout=True,
    )
    speeds = np.array([row['keil_fps'] for row in performance_rows], dtype=float)
    errors = np.array([row['keil_mae'] for row in performance_rows], dtype=float)
    ram_values = np.array([row['ram_kb'] for row in performance_rows], dtype=float)
    mae_norm = LogNorm(
        vmin=max(float(np.nanmin(errors)) * float(perf_cfg.get('mae_vmin_scale', 0.8)), 1e-9),
        vmax=float(np.nanmax(errors)) * float(perf_cfg.get('mae_vmax_scale', 1.2)),
    )
    scatter_for_colorbar = None
    for category, marker in [('Baseline export', 'o'), ('Wiener-KAN variant', 'D')]:
        idx = [i for i, row in enumerate(performance_rows) if row['category'] == category]
        if not idx:
            continue
        scatter_for_colorbar = ax_perf.scatter(
            ram_values[idx],
            speeds[idx],
            s=float(perf_cfg.get('baseline_marker_area', 118)) if category == 'Baseline export' else float(perf_cfg.get('variant_marker_area', 138)),
            c=errors[idx],
            cmap=str(perf_cfg.get('colormap', 'magma')),
            norm=mae_norm,
            marker=marker,
            edgecolor=str(perf_cfg.get('edge_color', '#222222')),
            linewidth=float(perf_cfg.get('edge_linewidth', 0.8)),
            alpha=float(perf_cfg.get('marker_alpha', 0.92)),
            label=category,
        )
    label_offsets = {
        'TCN': (-34, 8),
        '1DCNN': (8, 12),
        'LSTM': (-42, 0),
        'LSTMTransformer': (8, 8),
        'RNN': (8, 8),
        'GRU': (8, -18),
        'Wiener-KAN\n(LUT nearest)': (8, -12),
        'Wiener-KAN\n(LUT interp)': (8, -18),
        'Wiener-KAN\n(No LUT)': (8, 8),
    }
    for row in performance_rows:
        ax_perf.annotate(
            row['label'],
            (row['ram_kb'], row['keil_fps']),
            textcoords='offset points',
            xytext=label_offsets.get(row['label'], (7, 6)),
            ha='left',
            va='center',
            fontsize=float(perf_cfg.get('annotation_fontsize', 7.8)),
            bbox={'boxstyle': 'round,pad=0.18', 'facecolor': 'white', 'edgecolor': 'none', 'alpha': float(perf_cfg.get('annotation_box_alpha', 0.78))},
        )
    ax_perf.set_xlabel('RAM usage (KB)')
    ax_perf.set_ylabel('KEIL throughput (points/s; higher is better)')
    ax_perf.set_yscale('log')
    ax_perf.set_xlim(left=0.0, right=max(float(np.nanmax(ram_values)) * float(perf_cfg.get('xmax_scale', 1.18)), 10.0))
    ax_perf.set_ylim(
        bottom=max(float(np.nanmin(speeds)) * float(perf_cfg.get('ymin_scale', 0.55)), 1.0),
        top=float(np.nanmax(speeds)) * float(perf_cfg.get('ymax_scale', 2.0)),
    )
    ax_perf.grid(True, axis='both', alpha=float(perf_cfg.get('grid_alpha', 0.24)))
    ax_perf.legend(loc=str(perf_cfg.get('legend_loc', 'upper right')), frameon=bool(perf_cfg.get('legend_frameon', True)))
    if scatter_for_colorbar is not None:
        cbar = fig_perf.colorbar(scatter_for_colorbar, ax=ax_perf, fraction=0.046, pad=0.04)
        cbar.set_label('KEIL-MAE against TensorFlow')
    panel_performance = save_panel_figure(
        fig_perf,
        'fig_05_onboard_inference_c_embedded_performance.png',
        raw_payload={
            'source_trace': 'paper results payload deployment and lut_variants fields',
            'rows': performance_rows,
            'axis_encoding': {
                'x': 'RAM usage (KB)',
                'y': 'KEIL throughput (points/s)',
                'color': 'KEIL-MAE against TensorFlow',
                'marker_shape': 'export family',
            },
            'panel_policy': 'Panel c combines exported baseline models and the three Wiener-KAN LUT implementation variants.',
        },
    )

    panel_tradeoff = make_lut_point_tradeoff_figure(lut_point_rows)

    name = make_bitmap_montage(
        'fig_05_onboard_inference.png',
        [
            {'source': panel_export, 'label': '(a)', 'fit_width': 1820, 'trim_border': 120, 'align_x': 'center', 'align_y': 'top'},
            {'source': panel_validate, 'label': '(b)', 'fit_width': 1820, 'trim_border': 120, 'align_x': 'center', 'align_y': 'top'},
            {'source': panel_performance, 'label': '(c)', 'fit_width': 1820, 'trim_border': 35, 'align_x': 'center', 'align_y': 'top'},
            {'source': panel_tradeoff, 'label': '(d)', 'fit_width': 1820, 'trim_border': 35, 'align_x': 'center', 'align_y': 'top'},
        ],
        layout='matrix',
        rows=2,
        cols=2,
        padding=[50, 55, 50, 55],
        gutter=(60, 68),
        cell_widths=[1820, 1820],
        label_font_size=52,
        note='Composes the export, validation, embedded-performance, and LUT trade-off panels in one 2 x 2 montage so all subfigure labels share the same final scaling rule.',
        latex_width_fraction=1.0,
        figure_key='fig_05_onboard_inference',
    )
    raw_path = FIGURES_DIR / 'fig_05_onboard_inference.raw.json'
    raw_payload = json.loads(raw_path.read_text(encoding='utf-8'))
    raw_payload.update({
        'source': 'generated from paper_pipeline.make_onboard_figure',
        'focus': 'Combined embedded validation workflow and deployment performance.',
        'performance_rows': performance_rows,
        'lut_point_sweep_rows': lut_point_rows,
        'panels': ['C export workflow', 'QEMU and STM32F405 validation workflow', 'baseline and Wiener-KAN variant performance', 'LUT point-count trade-off'],
        'layout_policy': 'Single-pass 2 x 2 montage; avoids nested montage rescaling between workflow and metric panels.',
    })
    save_json(raw_path, raw_payload)
    return name


def load_hparam_sensitivity_summary() -> Dict[str, Any]:
    summary = load_json('ex_projects/compare/hparam_sensitivity_r15/data/summary.json')
    primary_metrics = load_json('projects/01_LR_STUDY/FRIKANh8u6l6_e1k_lr7e4/data/metrics.json')
    canonical_row = {
        'name': 'FRIKANh8u6l6_e1k_lr7e4',
        'param': 'canonical_h8u6l6',
        'path': 'projects/01_LR_STUDY/FRIKANh8u6l6_e1k_lr7e4',
        # The main-project metrics file may be marked partial when optional sections are absent,
        # but the hyperparameter plot only needs these four completed metrics.
        'status': 'complete',
        'metrics_status': primary_metrics.get('status', 'complete'),
        'epochs': primary_metrics.get('epochs'),
        'freq_drift_hz': primary_metrics.get('freq_drift_hz'),
        'sens_drift_percent': primary_metrics.get('sens_drift_percent'),
        'linearity_percent': primary_metrics.get('linearity_percent'),
        'val_loss': primary_metrics.get('val_loss'),
        'val_afmae': primary_metrics.get('val_afmae'),
        'source': 'canonical_main_project',
    }
    canonical_values = {
        'H_UNITS': 8,
        'INNER_KAN_UNITS': 6,
        'INNER_KAN_LAYERS': 6,
        'GRID_SIZE': 8,
        'SPLINE_ORDER': 2,
    }
    rows = [row for row in summary.get('rows', []) if row.get('axis') != 'base']
    for axis, value in canonical_values.items():
        rows = [row for row in rows if not (row.get('axis') == axis and int(row.get('value', -999999)) == value)]
        axis_row = dict(canonical_row)
        axis_row.update({'axis': axis, 'value': value})
        rows.append(axis_row)
    baseline = dict(canonical_row)
    baseline.update({'axis': 'base', 'param': '', 'value': None})
    summary['baseline'] = baseline
    summary['baseline_project'] = 'FRIKANh8u6l6_e1k_lr7e4'
    summary['rows'] = [baseline] + sorted(
        rows,
        key=lambda row: (
            ['H_UNITS', 'INNER_KAN_UNITS', 'INNER_KAN_LAYERS', 'GRID_SIZE', 'SPLINE_ORDER'].index(row.get('axis'))
            if row.get('axis') in ['H_UNITS', 'INNER_KAN_UNITS', 'INNER_KAN_LAYERS', 'GRID_SIZE', 'SPLINE_ORDER']
            else 99,
            float(row.get('value', 0) or 0),
        ),
    )
    summary['canonical_main_project'] = canonical_row
    return summary


def make_hparam_sensitivity_figure(summary: Dict[str, Any], loss_rows: List[Dict[str, Any]], loss_curves: List[Dict[str, Any]]) -> str:
    cfg = get_figure_config('fig_18_hparam_sensitivity')
    font_scale = float(cfg.get('font_scale', 1.0))
    rows = [row for row in summary.get('rows', []) if row.get('axis') != 'base' and row.get('status') == 'complete']
    baseline = summary.get('baseline', {})
    axis_order = ['H_UNITS', 'INNER_KAN_UNITS', 'INNER_KAN_LAYERS', 'GRID_SIZE', 'SPLINE_ORDER']
    axis_labels = {
        'H_UNITS': 'Wiener slices $h$',
        'INNER_KAN_UNITS': 'KAN width $u$',
        'INNER_KAN_LAYERS': 'KAN depth $l$',
        'GRID_SIZE': 'Spline grid $g$',
        'SPLINE_ORDER': 'Spline order $s$',
    }
    metric_specs = [
        ('freq_drift_hz', 'Freq drift', '#1f4e79', 'o'),
        ('sens_drift_percent', 'Sens drift', '#0f6c5c', 's'),
        ('linearity_percent', 'Linearity', '#c96b00', '^'),
    ]
    baseline_values = {key: float(baseline.get(key, 1.0) or 1.0) for key, *_ in metric_specs}

    panel_specs: List[Dict[str, Any]] = []
    panel_cfg = cfg.get('metric_panels') or {}
    for panel_idx, axis in enumerate(axis_order):
        fig, ax = plt.subplots(
            figsize=_as_float_tuple(panel_cfg.get('figsize'), (4.5, 3.3)),
            constrained_layout=True,
        )
        axis_rows = sorted([row for row in rows if row.get('axis') == axis], key=lambda r: float(r.get('value', 0)))
        x = np.array([float(row.get('value', 0)) for row in axis_rows], dtype=float)
        for key, label, color, marker in metric_specs:
            y = np.array([float(row.get(key, np.nan)) / baseline_values[key] * 100.0 for row in axis_rows], dtype=float)
            ax.plot(
                x,
                y,
                marker=marker,
                linewidth=float(panel_cfg.get('line_width', 1.7)),
                markersize=float(panel_cfg.get('marker_size', 5.0)),
                color=color,
                label=label,
            )
        ax.axhline(100.0, color='#222222', linestyle='--', linewidth=float(panel_cfg.get('baseline_linewidth', 1.0)), alpha=float(panel_cfg.get('baseline_alpha', 0.65)))
        if baseline.get('axis') == 'base':
            base_value = {
                'H_UNITS': 8,
                'INNER_KAN_UNITS': 6,
                'INNER_KAN_LAYERS': 6,
                'GRID_SIZE': 8,
                'SPLINE_ORDER': 2,
            }.get(axis)
            if base_value is not None and min(x) <= base_value <= max(x):
                ax.axvline(float(base_value), color='#444444', linestyle=':', linewidth=float(panel_cfg.get('canonical_linewidth', 1.0)), alpha=float(panel_cfg.get('canonical_alpha', 0.7)))
        ax.set_xlabel(axis_labels[axis])
        ax.set_ylabel('Relative to baseline (%)')
        ax.set_xticks(x)
        if axis in {'H_UNITS', 'INNER_KAN_UNITS', 'INNER_KAN_LAYERS', 'GRID_SIZE', 'SPLINE_ORDER'}:
            ax.set_xticklabels([str(int(v)) for v in x])
        ax.grid(True, axis='both', alpha=float(panel_cfg.get('grid_alpha', 0.24)))
        ax.margins(x=float(panel_cfg.get('x_margin', 0.08)))
        source = save_panel_figure(fig, f'fig_18_hparam_sensitivity_{panel_idx + 1}_{axis.lower()}.png')
        panel_specs.append({
            'source': source,
            'label': f'({chr(97 + panel_idx)})',
            'fit_width': int(panel_cfg.get('fit_width', 1500)),
            'trim_border': int(panel_cfg.get('trim_border', 26)),
        })

    legend_cfg = cfg.get('legend_panel') or {}
    fig_legend, legend_ax = plt.subplots(
        figsize=_as_float_tuple(legend_cfg.get('figsize'), (4.5, 3.3)),
        constrained_layout=True,
    )
    legend_ax.axis('off')
    handles = [
        Line2D([0], [0], color=color, marker=marker, linewidth=float(panel_cfg.get('line_width', 1.7)), markersize=float(panel_cfg.get('marker_size', 5.0)))
        for _, _, color, marker in metric_specs
    ]
    labels = [label for _, label, _, _ in metric_specs]
    legend_ax.legend(handles, labels, loc='center', frameon=True, fontsize=8.0 * font_scale)
    baseline_text = (
        'Baseline data (h=8, u=6, l=6, g=8, s=2):\n'
        f"Freq drift = {baseline_values['freq_drift_hz']:.2f} Hz; "
        f"Sens drift = {baseline_values['sens_drift_percent']:.2f}%;\n"
        f"Linearity error = {baseline_values['linearity_percent']:.3f}%"
    )
    legend_ax.text(
        0.5,
        0.23,
        'Dashed horizontal line: baseline = 100%\nDotted vertical line: canonical value\n' + baseline_text,
        ha='center',
        va='center',
        fontsize=float(legend_cfg.get('text_fontsize', 8.8)) * font_scale,
    )
    legend_source = save_panel_figure(fig_legend, 'fig_18_hparam_sensitivity_6_legend.png')
    panel_specs.append({
        'source': legend_source,
        'fit_width': int(legend_cfg.get('fit_width', 1500)),
        'trim_border': int(legend_cfg.get('trim_border', 26)),
    })
    panel_specs.extend(make_loss_ablation_panel_specs(
        loss_rows,
        loss_curves,
        label_offset=5,
        fit_width=int(legend_cfg.get('loss_fit_width', 1500)),
        trim_border=int(legend_cfg.get('loss_trim_border', 26)),
        figure_key='fig_18_hparam_sensitivity',
    ))

    name = make_bitmap_montage(
        'fig_18_hparam_sensitivity.png',
        panel_specs,
        layout='matrix',
        rows=3,
        cols=3,
        padding=[70, 65, 70, 65],
        gutter=(70, 80),
        label_font_size=46,
        note='Composes five one-factor hyperparameter panels, one unnumbered legend panel, and three loss-ablation panels in a 3 x 3 unified montage.',
        latex_width_fraction=0.98,
        figure_key='fig_18_hparam_sensitivity',
    )
    raw_path = FIGURES_DIR / 'fig_18_hparam_sensitivity.raw.json'
    raw_payload = json.loads(raw_path.read_text(encoding='utf-8'))
    raw_payload.update({
        'source': 'ex_projects/compare/hparam_sensitivity_r15/data/summary.json',
        'baseline': baseline,
        'axis_summary': summary.get('axis_summary', {}),
        'plot_encoding': 'Each panel uses one hyperparameter as the x-axis; y-values are normalized to the canonical baseline.',
        'loss_ablation': [row['label'] for row in loss_rows],
        'loss_panel_policy': 'The third row contains square convergence panels for the joint, MAE-only and AFMAE-only loss objectives.',
    })
    save_json(raw_path, raw_payload)
    return name


def make_table(lines: List[List[str]], headers: List[str]) -> str:
    rows = ['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---'] * len(headers)) + ' |']
    for line in lines:
        rows.append('| ' + ' | '.join(line) + ' |')
    return '\n'.join(rows)


def _metric_row_for_ablation(
    group: str,
    variant: str,
    contrast: str,
    row: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        'group': group,
        'variant': variant,
        'contrast': contrast,
        'freq_drift_hz': _fmt_float(row['freq_drift_hz'], 2),
        'sens_drift_percent': _fmt_float(row['sens_drift_percent'], 2),
        'linearity_percent': _fmt_float(row['linearity_percent'], 3),
        'emphasize': False,
    }


def _hparam_best_cell(axis_summary: Dict[str, Any], best_key: str, metric_key: str, digits: int) -> str:
    best = axis_summary.get(best_key) or {}
    if best.get('value') is None or best.get(metric_key) is None:
        return '-'
    return f"{best['value']}: {_fmt_float(best[metric_key], digits)}"


def build_ablation_overview_rows(
    loss_rows: List[Dict[str, Any]],
    structure_rows: List[Dict[str, Any]],
    iir_rows: List[Dict[str, Any]],
    _hparam_summary: Dict[str, Any],
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    structure_map = {row['label']: row for row in structure_rows}
    iir_map = {row['label']: row for row in iir_rows}
    loss_map = {row['label']: row for row in loss_rows}

    def add_structure(label: str, group: str, variant: str, contrast: str) -> None:
        if label not in structure_map:
            raise KeyError(f'Missing structure ablation row: {label}')
        rows.append(_metric_row_for_ablation(group, variant, contrast, structure_map[label]))

    def add_iir(label: str, variant: str, contrast: str) -> None:
        if label not in iir_map:
            raise KeyError(f'Missing Wiener front-end ablation row: {label}')
        rows.append(_metric_row_for_ablation('Wiener front', variant, contrast, iir_map[label]))

    def add_loss(label: str, variant: str, contrast: str) -> None:
        if label not in loss_map:
            raise KeyError(f'Missing loss ablation row: {label}')
        rows.append(_metric_row_for_ablation('Loss', variant, contrast, loss_map[label]))

    baseline_reference = _metric_row_for_ablation(
        'Baseline',
        'B-spline + Odd+pos. + System, fixed, + MAE + AFMAE',
        'Shared canonical Wiener-KAN setting',
        structure_map['Wiener-KAN'],
    )
    baseline_candidates = [
        iir_map['System prior, frozen'],
        loss_map['MAE+AFMAE'],
    ]
    for candidate in baseline_candidates:
        if any(
            baseline_reference[key] != _fmt_float(candidate[source_key], digits)
            for key, source_key, digits in (
                ('freq_drift_hz', 'freq_drift_hz', 2),
                ('sens_drift_percent', 'sens_drift_percent', 2),
                ('linearity_percent', 'linearity_percent', 3),
            )
        ):
            raise ValueError('Baseline ablation rows diverged; cannot collapse Table 5 baseline safely.')
    baseline_reference['emphasize'] = True
    rows.append(baseline_reference)

    add_structure('CNN-KAN', 'Struct', 'CNN-KAN', 'Conv front replaces Wiener front')
    add_structure('Wiener-MLP', 'Struct', 'Wiener-MLP', 'MLP replaces KAN mapping')

    add_structure('No symmetry', 'Constr.', 'Positive', 'No odd symmetry')
    add_structure('No positive (stress)', 'Constr.', 'Odd', 'No positive basis')

    add_iir('Random, frozen', 'Random / fixed', 'Random init., frozen')
    add_iir('System prior, trainable', 'System / trainable', 'Measured init., trainable')
    add_iir('Random, trainable', 'Random / trainable', 'Random init., trainable')

    add_loss('MAE', 'MAE', 'Time-domain pointwise loss')
    add_loss('AFMAE', 'AFMAE', 'Amplitude-frequency loss')
    return rows


def latex_escape(text: Any) -> str:
    value = str(text)
    replacements = {
        '\\': r'\textbackslash{}',
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
    }
    return ''.join(replacements.get(char, char) for char in value)


def latex_bold(text: Any) -> str:
    return rf'\textbf{{{latex_escape(text)}}}'


def markdown_bold(text: Any) -> str:
    return f"**{text}**"


def ablation_detail_tex(label: Any) -> str:
    safe_label = re.sub(r'[^A-Za-z0-9_:\-]+', '', str(label))
    return rf"Tab.~\ref{{{safe_label}}}"


def ablation_detail_markdown(label: Any) -> str:
    return str(label)


def write_ablation_overview_tex(rows: List[Dict[str, Any]]) -> None:
    table_dir = LATEX_DIR / 'tables'
    table_dir.mkdir(parents=True, exist_ok=True)

    group_spans: Dict[int, int] = {}
    index = 0
    while index < len(rows):
        group = rows[index]['group']
        span = 1
        while index + span < len(rows) and rows[index + span]['group'] == group:
            span += 1
        group_spans[index] = span
        index += span

    lines = [
        '% Auto-generated table; do not edit manually.',
        r'\begingroup',
        r'\renewcommand{\arraystretch}{1.22}',
        r'\begin{tabular}{@{}p{0.12\textwidth}p{0.18\textwidth}p{0.40\textwidth}ccc@{}}',
        r'\hline\hline',
        r'\textbf{Group} & \textbf{Variant} & \textbf{Controlled contrast} & \makecell{\textbf{Freq}\\\textbf{drift}\\(Hz)} & \makecell{\textbf{Sens}\\\textbf{drift}\\(\%)} & \makecell{\textbf{Linearity}\\(\%)} \\ \hline',
    ]
    for row_index, row in enumerate(rows):
        render_cell = latex_bold if row.get('emphasize') else latex_escape
        if row_index in group_spans:
            if group_spans[row_index] == 1:
                group_cell = render_cell(row['group'])
            else:
                group_cell = rf"\multirow{{{group_spans[row_index]}}}{{=}}{{{render_cell(row['group'])}}}"
        else:
            group_cell = ''
        cells = [
            group_cell,
            render_cell(row['variant']),
            render_cell(row['contrast']),
            render_cell(row['freq_drift_hz']),
            render_cell(row['sens_drift_percent']),
            render_cell(row['linearity_percent']),
        ]
        lines.append(' & '.join(cells) + r' \\')
        if row_index + 1 < len(rows) and rows[row_index + 1]['group'] != row['group']:
            lines.append(r'\hdashline')
    lines.extend([r'\hline\hline', r'\end{tabular}', r'\endgroup', ''])
    (table_dir / 'ablation_overview.tex').write_text('\n'.join(lines), encoding='utf-8')


def build_tables(
    main_rows: List[Dict[str, Any]],
    loss_rows: List[Dict[str, Any]],
    structure_rows: List[Dict[str, Any]],
    iir_rows: List[Dict[str, Any]],
    ablation_overview_rows: List[Dict[str, Any]],
    deploy_rows: List[Dict[str, Any]],
    lut_rows: List[Dict[str, Any]],
    lut_point_rows: List[Dict[str, Any]],
    origin: Dict[str, float],
    optimization_profiles: List[Dict[str, Any]],
) -> None:
    table_main = make_table([
        [
            row['label'],
            f"{row['freq_drift_hz']:.2f}",
            f"{row['sens_drift_percent']:.2f}",
            f"{row['linearity_percent']:.3f}",
            format_optional(row['board_keil_mae'], '{:.2e}'),
            format_optional(row['board_keil_fps'], '{:.1f}'),
            format_optional(row.get('ram_bytes', None) / 1024.0 if row.get('ram_bytes') is not None else None, '{:.1f}'),
        ]
        for row in main_rows
    ], ['Model', 'Freq Drift (Hz)', 'Sens Drift (%)', 'Linearity (in-band, %)', 'KEIL-MAE', 'KEIL speed (Points/s)', 'RAM (KB)'])

    table_loss = make_table([
        [
            row['label'],
            row['loss_function'],
            f"{row['freq_drift_hz']:.2f}",
            f"{row['sens_drift_percent']:.2f}",
            f"{row['linearity_percent']:.3f}",
            format_optional(row['board_qemu_mae'], '{:.3e}'),
            format_optional(row['board_keil_mae'], '{:.3e}'),
            format_optional(row['board_keil_fps'], '{:.1f}'),
        ]
        for row in loss_rows
    ], ['Variant', 'Active loss', 'Freq Drift (Hz)', 'Sens Drift (%)', 'Linearity (in-band, %)', 'QEMU-MAE', 'KEIL-MAE', 'KEIL speed (Points/s)'])

    table_structure = make_table([
        [
            row['label'],
            f"{row['freq_drift_hz']:.2f}",
            f"{row['sens_drift_percent']:.2f}",
            f"{row['linearity_percent']:.3f}",
        ]
        for row in structure_rows
    ], ['Variant', 'Freq Drift (Hz)', 'Sens Drift (%)', 'Linearity (in-band, %)'])

    table_iir = make_table([
        [
            row['label'],
            str(int(row['epochs'])),
            f"{row['freq_drift_hz']:.2f}",
            f"{row['sens_drift_percent']:.2f}",
            f"{row['linearity_percent']:.3f}",
        ]
        for row in iir_rows
    ], ['Variant', 'Epochs', 'Freq Drift (Hz)', 'Sens Drift (%)', 'Linearity (in-band, %)'])

    table_ablation_overview = make_table([
        [
            markdown_bold(row['group']) if row.get('emphasize') else row['group'],
            markdown_bold(row['variant']) if row.get('emphasize') else row['variant'],
            markdown_bold(row['contrast']) if row.get('emphasize') else row['contrast'],
            markdown_bold(row['freq_drift_hz']) if row.get('emphasize') else row['freq_drift_hz'],
            markdown_bold(row['sens_drift_percent']) if row.get('emphasize') else row['sens_drift_percent'],
            markdown_bold(row['linearity_percent']) if row.get('emphasize') else row['linearity_percent'],
        ]
        for row in ablation_overview_rows
    ], ['Group', 'Variant', 'Controlled contrast', 'Freq Drift (Hz)', 'Sens Drift (%)', 'Linearity (in-band, %)'])

    table_deploy = make_table([
        [
            row['label'],
            f"{row['board_qemu_mae']:.3e}",
            f"{row['board_keil_mae']:.3e}",
            f"{row['board_keil_fps']:.1f}",
            f"{row['flash_bytes'] / 1024.0:.1f}",
            f"{row['ram_bytes'] / 1024.0:.1f}",
        ]
        for row in deploy_rows
    ], ['Model', 'QEMU-MAE', 'KEIL-MAE', 'KEIL speed (Points/s)', 'Flash (KB)', 'RAM (KB)'])

    table_opt = make_table([
        [
            item['label'],
            item['status'],
            format_optional(item['keil_fps'], '{:.1f}'),
            format_optional(item['flash_bytes'] / 1024.0 if item.get('flash_bytes') is not None else None, '{:.1f}'),
            format_optional(item['ram_bytes'] / 1024.0 if item.get('ram_bytes') is not None else None, '{:.1f}'),
            format_profile_note(item),
        ]
        for item in optimization_profiles
        if item['key'] in {'project_default', 'o0', 'o2', 'ofast_lto'}
    ], ['Profile', 'Status', 'KEIL speed (Points/s)', 'Flash (KB)', 'RAM (KB)', 'Note'])

    table_lut = make_table([
        [
            row['label'],
            f"{row['qemu_mae']:.3e}",
            f"{row['keil_mae']:.3e}",
            f"{row['keil_fps']:.1f}",
            f"{row['flash_bytes'] / 1024.0:.1f}",
            f"{row['ram_bytes'] / 1024.0:.1f}",
        ]
        for row in lut_rows
    ], ['Variant', 'QEMU-MAE', 'KEIL-MAE', 'KEIL speed (Points/s)', 'Flash (KB)', 'RAM (KB)'])

    lut_point_map = {(row['mode'], int(row['points'])): row for row in lut_point_rows}
    table_lut_point_sweep = make_table([
        [
            str(points),
            f"{lut_point_map[('nearest', points)]['qemu_mae']:.3e}",
            f"{lut_point_map[('interp', points)]['qemu_mae']:.3e}",
            f"{lut_point_map[('nearest', points)]['flash_bytes'] / 1024.0:.1f}",
            f"{lut_point_map[('interp', points)]['flash_bytes'] / 1024.0:.1f}",
        ]
        for points in sorted({int(row['points']) for row in lut_point_rows})
    ], ['LUT points', 'Nearest QEMU-MAE', 'Interp QEMU-MAE', 'Nearest Flash (KB)', 'Interp Flash (KB)'])

    band_freqs = ', '.join(f"{int(value) if float(value).is_integer() else value:g}" for value in main_rows[0]['linearity_band_frequencies_hz'])
    full_grid_desc = (
        f"{main_rows[0]['linearity_full_frequencies_hz'][0]:.0f}-"
        f"{main_rows[0]['linearity_full_frequencies_hz'][-1]:.0f} Hz, "
        f"{main_rows[0]['linearity_full_frequency_count']} sampled points"
    )
    protocol_table = make_table([
        ['Sensor sample', 'MTSS-1001'],
        ['Environment', '25 C'],
        ['Frequency grid (saved evaluation)', full_grid_desc],
        ['Magnitude sweep', '0.24-6.0 m/s^2, 25 levels'],
        ['Sequence duration', '4.0 s'],
        ['Sampling rate', '2000 Hz'],
        ['Window count', '8000 sequences'],
        ['Reference sensitivity point', '100 Hz'],
        ['Freq-drift fitted center-frequency band', '10-128 Hz with band-limited fit_params'],
        ['Linearity band (this draft)', f"<= {main_rows[0]['linearity_band_max_hz']:.0f} Hz, {main_rows[0]['linearity_band_count']} points ({band_freqs} Hz)"],
    ], ['Item', 'Value'])

    write_ablation_overview_tex(ablation_overview_rows)
    note_lines = [
        '# Machine-readable tables for the 20260422 draft',
        '',
        '## Protocol',
        protocol_table,
        '',
        '## Main benchmark',
        table_main,
        '',
        f"Origin metrics: Freq Drift = {origin['freq']:.2f} Hz, Sens Drift = {origin['sens']:.2f} %, In-band linearity = {origin['linearity']:.3f} %.",
        '',
        '## Loss ablation',
        table_loss,
        '',
        '## Structural ablation',
        table_structure,
        '',
        '## Wiener front-end ablation',
        table_iir,
        '',
        '## Ablation overview',
        table_ablation_overview,
        '',
        '## On-board inference evaluation',
        table_deploy,
        '',
        '## Wiener-KAN optimization sweep',
        table_opt,
        '',
        '## LUT implementation variants',
        table_lut,
        '',
        '## LUT quantization-point sweep',
        table_lut_point_sweep,
    ]
    (DATA_DIR / 'generated_tables.md').write_text('\n'.join(note_lines), encoding='utf-8')






def make_mechanism_schematic() -> str:
    src = PAPER_DIR / 'assets' / 'fig_14_met_nonlinear_mechanism_ai.png'
    if not src.exists():
        raise FileNotFoundError(f'Missing AI-rendered mechanism schematic: {src}')
    out = FIGURES_DIR / 'fig_14_met_nonlinear_mechanism.png'
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, out)
    save_json(out.with_suffix('.raw.json'), {
        'source': str(src.relative_to(ROOT)).replace('\\', '/'),
        'generation': 'AI-rendered scientific schematic generated with imagegen and stored as a reproducible paper asset',
        'elements': [
            'large-deflection membrane and mass',
            'electrolyte microchannel with vortical flow',
            'porous anode and cathode',
            'iodide/triiodide ion transport and concentration gradients',
            'redox kinetics at electrode surfaces',
            'amplitude-dependent frequency-response drift',
        ],
    })
    return out.name


def copy_ai_paper_asset(asset_name: str, figure_name: str, elements: List[str]) -> str:
    src = PAPER_DIR / 'assets' / asset_name
    if not src.exists():
        raise FileNotFoundError(f'Missing AI-rendered paper asset: {src}')
    out = FIGURES_DIR / figure_name
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, out)
    save_json(out.with_suffix('.raw.json'), {
        'source': str(src.relative_to(ROOT)).replace('\\', '/'),
        'generation': 'AI-rendered scientific schematic generated with imagegen and stored as a reproducible paper asset',
        'elements': elements,
    })
    return out.name


def make_lut_lookup_principles_figure() -> str:
    cfg = get_figure_config('fig_15_lut_lookup_principles')

    def center_to_bottom_left(cx: float, cy: float, w: float, h: float) -> tuple[float, float]:
        return cx - w / 2, cy - h / 2

    def draw_box(
        ax: Any,
        x: float,
        y: float,
        w: float,
        h: float,
        text: str,
        face: str,
        edge: str,
        size: float = 9.6,
        weight: str = 'normal',
    ) -> None:
        rect = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle='round,pad=0.012,rounding_size=0.018',
            facecolor=face,
            edgecolor=edge,
            lw=1.4,
        )
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, text, ha='center', va='center', fontsize=size, weight=weight, color='#222222')

    def draw_box_center(
        ax: Any,
        cx: float,
        cy: float,
        w: float,
        h: float,
        text: str,
        face: str,
        edge: str,
        size: float = 9.6,
        weight: str = 'normal',
    ) -> None:
        bx, by = center_to_bottom_left(cx, cy, w, h)
        draw_box(ax, bx, by, w, h, text, face, edge, size=size, weight=weight)

    def arrow(ax: Any, start: tuple[float, float], end: tuple[float, float], color: str = '#333333', lw: float = 1.8) -> None:
        ax.annotate('', xy=end, xytext=start, zorder=8, arrowprops=dict(arrowstyle='->', lw=lw, color=color, shrinkA=0, shrinkB=0))

    def draw_lut_table(
        ax: Any,
        x: float,
        y: float,
        w: float,
        h: float,
        *,
        header_q_frac: float = 0.20,
        header_v_frac: float = 0.66,
        header_y_frac: float = 0.84,
        row_q_frac: float = 0.20,
        row_v_frac: float = 0.66,
        row_start_y_frac: float = 0.68,
        row_spacing_frac: float = 0.13,
        row_font_size: float = 7.6,
        header_font_size: float = 8.4,
        line_margin_frac: float = 0.025,
        line_lw: float = 0.8,
        label_font_size: float = 8.0,
        label_y_offset: float = 0.055,
    ) -> None:
        draw_box(ax, x, y, w, h, '', '#eaf6f1', '#0f6c5c')
        rows = 6
        for i in range(1, rows):
            yy = y + h * i / rows
            ax.plot([x + w * line_margin_frac, x + w * (1 - line_margin_frac)], [yy, yy], color='#95bfb2', lw=line_lw)
        ax.text(x + w * header_q_frac, y + h * header_y_frac, 'q', ha='center', va='center', fontsize=header_font_size, weight='bold', color='#0f6c5c')
        ax.text(x + w * header_v_frac, y + h * header_y_frac, r'$v_q$', ha='center', va='center', fontsize=header_font_size, weight='bold', color='#0f6c5c')
        for i, (q_text, v_text) in enumerate([('0', r'$v_0$'), ('1', r'$v_1$'), ('...', '...'), (r'$Q-2$', r'$v_{Q-2}$'), (r'$Q-1$', r'$v_{Q-1}$')]):
            yy = y + h * (row_start_y_frac - row_spacing_frac * i)
            ax.text(x + w * row_q_frac, yy, q_text, ha='center', va='center', fontsize=row_font_size, color='#222222')
            ax.text(x + w * row_v_frac, yy, v_text, ha='center', va='center', fontsize=row_font_size, color='#222222')
        ax.text(x + w / 2, y + h + h * label_y_offset, 'sampled table', ha='center', va='center', fontsize=label_font_size, color='#0f6c5c', weight='bold')

    def draw_flash_chip(ax: Any, x: float, y: float, w: float, h: float) -> None:
        chip = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle='round,pad=0.010,rounding_size=0.018',
            facecolor='#f7fbff',
            edgecolor='#1f4e79',
            lw=1.6,
        )
        ax.add_patch(chip)
        pin_y = np.linspace(y + h * 0.18, y + h * 0.82, 5)
        for yy in pin_y:
            ax.plot([x - 0.022, x], [yy, yy], color='#1f4e79', lw=1.2)
            ax.plot([x + w, x + w + 0.022], [yy, yy], color='#1f4e79', lw=1.2)
        ax.text(x + w / 2, y + h * 0.58, 'Flash', ha='center', va='center', fontsize=10.0, weight='bold', color='#1f4e79')
        ax.text(x + w / 2, y + h * 0.38, 'LUT', ha='center', va='center', fontsize=10.0, weight='bold', color='#1f4e79')

    offline_cfg = cfg.get('offline_panel') or {}
    fig_offline, ax_offline = plt.subplots(
        figsize=_as_float_tuple(offline_cfg.get('figsize'), (6.8, 3.25)),
        constrained_layout=True,
    )
    ax_offline.set_xlim(0, 1)
    ax_offline.set_ylim(0, 1)
    ax_offline.axis('off')
    offline_boxes = [
        {'id': 'activation_curve', 'bbox': [0.05, 0.21, 0.35, 0.81]},
        {'id': 'sampled_table', 'bbox': [0.47, 0.22, 0.69, 0.80]},
        {'id': 'flash_chip', 'bbox': [0.80, 0.30, 0.93, 0.72]},
    ]
    curve_to_table_points, curve_to_table_raw = _short_arrow_payload(
        'curve_to_table',
        [(0.35, 0.51), (0.47, 0.51)],
        source='activation_curve',
        target='sampled_table',
        require_axis_aligned=True,
    )
    table_to_flash_points, table_to_flash_raw = _short_arrow_payload(
        'table_to_flash',
        [(0.69, 0.51), (0.80, 0.51)],
        source='sampled_table',
        target='flash_chip',
        require_axis_aligned=True,
    )
    offline_arrows = [curve_to_table_raw, table_to_flash_raw]
    curve_ax = ax_offline.inset_axes([0.05, 0.21, 0.30, 0.60])
    x_dense = np.linspace(-1.0, 1.0, 300)
    y_dense = 0.65 * np.sin(1.7 * x_dense) + 0.20 * x_dense**3
    x_samples = np.linspace(-1.0, 1.0, 9)
    y_samples = 0.65 * np.sin(1.7 * x_samples) + 0.20 * x_samples**3
    curve_ax.plot(x_dense, y_dense, color='#0f6c5c', lw=2.4, label='trained activation')
    curve_ax.scatter(x_samples, y_samples, s=34, color='#c96b00', edgecolor='white', zorder=4, label='LUT samples')
    curve_ax.set_xticks([])
    curve_ax.set_yticks([])
    curve_ax.grid(True, alpha=0.25)
    curve_ax.text(0.06, 0.86, 'trained\nactivation', transform=curve_ax.transAxes, color='#0f6c5c', fontsize=float(offline_cfg.get('curve_text_fontsize', 8.0)), weight='bold')
    curve_ax.text(0.61, 0.14, 'uniform\nsamples', transform=curve_ax.transAxes, color='#c96b00', fontsize=float(offline_cfg.get('curve_text_fontsize', 8.0)), weight='bold')
    lut = offline_cfg.get('lut_table', {})
    bx, by = center_to_bottom_left(float(lut.get('x', 0.58)), float(lut.get('y', 0.51)), float(lut.get('w', 0.22)), float(lut.get('h', 0.58)))
    draw_lut_table(
        ax_offline, bx, by, float(lut.get('w', 0.22)), float(lut.get('h', 0.58)),
        header_q_frac=float(lut.get('表头Q位置X', 0.20)),
        header_v_frac=float(lut.get('表头V位置X', 0.66)),
        header_y_frac=float(lut.get('表头位置Y', 0.84)),
        row_q_frac=float(lut.get('行列Q位置X', 0.20)),
        row_v_frac=float(lut.get('行列V位置X', 0.66)),
        row_start_y_frac=float(lut.get('首行位置Y', 0.68)),
        row_spacing_frac=float(lut.get('行间距', 0.13)),
        row_font_size=float(lut.get('行列字号', 7.6)),
        header_font_size=float(lut.get('表头字号', 8.4)),
        line_margin_frac=float(lut.get('横线边距', 0.025)),
        line_lw=float(lut.get('横线线宽', 0.8)),
        label_font_size=float(lut.get('标签字号', 8.0)),
        label_y_offset=float(lut.get('标签偏移Y', 0.055)),
    )
    fc = offline_cfg.get('flash_chip', {})
    bx, by = center_to_bottom_left(float(fc.get('x', 0.865)), float(fc.get('y', 0.51)), float(fc.get('w', 0.13)), float(fc.get('h', 0.42)))
    draw_flash_chip(ax_offline, bx, by, float(fc.get('w', 0.13)), float(fc.get('h', 0.42)))
    offline_arrow_lw = float(offline_cfg.get('arrow_lw', 1.8))
    arrow(ax_offline, curve_to_table_points[0], curve_to_table_points[-1], '#0f6c5c')
    arrow(ax_offline, table_to_flash_points[0], table_to_flash_points[-1], '#0f6c5c')
    offline_source = save_panel_figure(
        fig_offline,
        'fig_15_lut_lookup_principles_a_offline.png',
        margin_left=float(offline_cfg.get('margin_left', 0.0)),
        margin_right=float(offline_cfg.get('margin_right', 0.0)),
        margin_top=float(offline_cfg.get('margin_top', 0.0)),
        margin_bottom=float(offline_cfg.get('margin_bottom', 0.0)),
        raw_payload={
            VISUAL_AUDIT_KEY: audit_schematic_geometry(
                offline_boxes,
                offline_arrows,
                context='LUT offline construction schematic geometry',
            )
        },
    )

    runtime_cfg = cfg.get('runtime_panel') or {}

    # Resolve output_scalar position for arrow targets and box bounds
    out_s = runtime_cfg.get('output_scalar', {})
    out_cx = float(out_s.get('x', 0.95))
    out_cy = float(out_s.get('y', 0.52))
    out_w = float(out_s.get('w', 0.075))
    out_h = float(out_s.get('h', 0.20))
    out_left = out_cx - out_w / 2
    out_right = out_cx + out_w / 2
    out_top = out_cy + out_h / 2
    out_bottom = out_cy - out_h / 2

    fig_runtime, ax_runtime = plt.subplots(
        figsize=_as_float_tuple(runtime_cfg.get('figsize'), (6.8, 3.45)),
        constrained_layout=True,
    )
    ax_runtime.set_xlim(0, 1)
    ax_runtime.set_ylim(0, 1)
    ax_runtime.axis('off')
    runtime_boxes = [
        {'id': 'input_scalar', 'bbox': [0.05, 0.42, 0.17, 0.59]},
        {'id': 'address_mapping', 'bbox': [0.26, 0.35, 0.46, 0.67]},
        {'id': 'nearest_lookup', 'bbox': [0.56, 0.62, 0.83, 0.87]},
        {'id': 'linear_interp', 'bbox': [0.56, 0.13, 0.83, 0.43]},
        {'id': 'output_scalar', 'bbox': [out_left, out_bottom, out_right, out_top]},
    ]
    input_to_address_points, input_to_address_raw = _short_arrow_payload(
        'input_to_address',
        [(0.17, 0.51), (0.26, 0.51)],
        source='input_scalar',
        target='address_mapping',
        require_axis_aligned=True,
    )
    address_to_nearest_points, address_to_nearest_raw = _short_arrow_payload(
        'address_to_nearest',
        [(0.46, 0.55), (0.56, 0.73)],
        source='address_mapping',
        target='nearest_lookup',
    )
    address_to_linear_points, address_to_linear_raw = _short_arrow_payload(
        'address_to_linear',
        [(0.46, 0.45), (0.56, 0.28)],
        source='address_mapping',
        target='linear_interp',
    )
    nearest_to_output_points, nearest_to_output_raw = _short_arrow_payload(
        'nearest_to_output',
        [(0.83, 0.74), (out_left, out_cy)],
        source='nearest_lookup',
        target='output_scalar',
    )
    linear_to_output_points, linear_to_output_raw = _short_arrow_payload(
        'linear_to_output',
        [(0.83, 0.27), (out_left, out_cy)],
        source='linear_interp',
        target='output_scalar',
    )
    runtime_arrows = [
        input_to_address_raw,
        address_to_nearest_raw,
        address_to_linear_raw,
        nearest_to_output_raw,
        linear_to_output_raw,
    ]
    runtime_arrow_lw = float(runtime_cfg.get('arrow_lw', 1.8))
    input_s = runtime_cfg.get('input_scalar', {})
    bx, by = center_to_bottom_left(float(input_s.get('x', 0.11)), float(input_s.get('y', 0.505)), float(input_s.get('w', 0.12)), float(input_s.get('h', 0.17)))
    draw_box(ax_runtime, bx, by, float(input_s.get('w', 0.12)), float(input_s.get('h', 0.17)), r'input $x$', '#f7f7f7', '#555555', size=float(runtime_cfg.get('input_box_size', 10.6)), weight='bold')
    ax_runtime.plot([0.07, 0.15], [0.34, 0.34], color='#555555', lw=1.1)
    ax_runtime.scatter([0.12], [0.34], s=42, color='#c96b00', zorder=3)
    ax_runtime.text(0.07, 0.29, r'$x_{\min}$', ha='center', va='center', fontsize=7.4, color='#555555')
    ax_runtime.text(0.15, 0.29, r'$x_{\max}$', ha='center', va='center', fontsize=7.4, color='#555555')
    arrow(ax_runtime, input_to_address_points[0], input_to_address_points[-1], lw=runtime_arrow_lw)
    addr = runtime_cfg.get('address_mapping', {})
    bx, by = center_to_bottom_left(float(addr.get('x', 0.36)), float(addr.get('y', 0.515)), float(addr.get('w', 0.20)), float(addr.get('h', 0.32)))
    draw_box(ax_runtime, bx, by, float(addr.get('w', 0.20)), float(addr.get('h', 0.32)), 'address\nmapping', '#fff7e8', '#c96b00', size=float(runtime_cfg.get('box_font_size', 9.6)), weight='bold')
    for k in range(6):
        xx = 0.29 + 0.026 * k
        ax_runtime.plot([xx, xx], [0.42, 0.48], color='#c96b00', lw=1.0)
    ax_runtime.plot([0.29, 0.42], [0.45, 0.45], color='#c96b00', lw=1.2)
    ax_runtime.scatter([0.36], [0.45], s=48, color='#0f6c5c', edgecolor='white', zorder=4)
    ax_runtime.text(0.36, 0.30, r'$q,\lambda$', ha='center', va='center', fontsize=8.3, weight='bold', color='#c96b00')
    arrow(ax_runtime, address_to_nearest_points[0], address_to_nearest_points[-1], '#c96b00', lw=runtime_arrow_lw)
    arrow(ax_runtime, address_to_linear_points[0], address_to_linear_points[-1], '#1f4e79', lw=runtime_arrow_lw)

    nearest = runtime_cfg.get('nearest_lookup', {})
    bx, by = center_to_bottom_left(float(nearest.get('x', 0.695)), float(nearest.get('y', 0.745)), float(nearest.get('w', 0.27)), float(nearest.get('h', 0.25)))
    draw_box(ax_runtime, bx, by, float(nearest.get('w', 0.27)), float(nearest.get('h', 0.25)), '', '#eaf6f1', '#0f6c5c')
    ax_runtime.text(0.695, 0.82, 'nearest lookup', ha='center', va='center', fontsize=8.9, weight='bold', color='#0f6c5c')
    cell_x = np.linspace(0.60, 0.78, 5)
    ax_runtime.plot([cell_x[0], cell_x[-1]], [0.72, 0.72], color='#0f6c5c', lw=1.1)
    for xx in cell_x:
        ax_runtime.plot([xx, xx], [0.68, 0.76], color='#0f6c5c', lw=1.0)
    ax_runtime.add_patch(plt.Rectangle((cell_x[2] - 0.018, 0.675), 0.036, 0.09, facecolor='#cfe9df', edgecolor='#0f6c5c', lw=1.0))
    ax_runtime.scatter([cell_x[2]], [0.72], s=46, color='#0f6c5c', zorder=4)
    ax_runtime.text(0.695, 0.65, 'one table read', ha='center', va='center', fontsize=7.8, color='#333333')

    linear = runtime_cfg.get('linear_interp', {})
    bx, by = center_to_bottom_left(float(linear.get('x', 0.695)), float(linear.get('y', 0.28)), float(linear.get('w', 0.27)), float(linear.get('h', 0.30)))
    draw_box(ax_runtime, bx, by, float(linear.get('w', 0.27)), float(linear.get('h', 0.30)), '', '#eef3fb', '#1f4e79')
    ax_runtime.text(0.695, 0.37, 'linear interpolation', ha='center', va='center', fontsize=8.6, weight='bold', color='#1f4e79')
    x0, x1 = 0.61, 0.78
    y0, y1 = 0.21, 0.30
    ax_runtime.plot([x0, x1], [y0, y1], color='#1f4e79', lw=1.7)
    ax_runtime.scatter([x0, x1], [y0, y1], s=42, color='#1f4e79', edgecolor='white', zorder=4)
    blend_x = 0.70
    blend_y = y0 + (y1 - y0) * (blend_x - x0) / (x1 - x0)
    ax_runtime.scatter([blend_x], [blend_y], s=58, color='#c96b00', edgecolor='white', zorder=5)
    ax_runtime.text(0.695, 0.17, r'$(1-\lambda)v_q+\lambda v_{q+1}$', ha='center', va='center', fontsize=7.5, color='#333333')

    arrow(ax_runtime, nearest_to_output_points[0], nearest_to_output_points[-1], '#0f6c5c', lw=runtime_arrow_lw)
    arrow(ax_runtime, linear_to_output_points[0], linear_to_output_points[-1], '#1f4e79', lw=runtime_arrow_lw)
    bx, by = center_to_bottom_left(out_cx, out_cy, out_w, out_h)
    draw_box(ax_runtime, bx, by, out_w, out_h, r'$\tilde{\phi}(x)$', '#ffffff', '#333333', size=11.0, weight='bold')
    runtime_source = save_panel_figure(
        fig_runtime,
        'fig_15_lut_lookup_principles_b_runtime.png',
        pad_inches=float(runtime_cfg.get('pad_inches', 0.0)),
        margin_left=float(runtime_cfg.get('margin_left', 0.0)),
        margin_right=float(runtime_cfg.get('margin_right', 0.0)),
        margin_top=float(runtime_cfg.get('margin_top', 0.0)),
        margin_bottom=float(runtime_cfg.get('margin_bottom', 0.0)),
        raw_payload={
            VISUAL_AUDIT_KEY: audit_schematic_geometry(
                runtime_boxes,
                runtime_arrows,
                context='LUT runtime lookup schematic geometry',
            )
        },
    )

    name = make_bitmap_montage(
        'fig_15_lut_lookup_principles.png',
        [
            {'source': offline_source, 'label': '(a)', 'fit_width': 2100, 'trim_border': 120},
            {'source': runtime_source, 'label': '(b)', 'fit_width': 2100, 'trim_border': 120},
        ],
        layout='vertical',
        padding=[60, 55, 60, 55],
        gutter=(60, 60),
        label_font_size=48,
        note='Composes the offline LUT construction and runtime lookup panels with the unified bitmap montage module.',
        latex_width_fraction=0.78,
        figure_key='fig_15_lut_lookup_principles',
    )
    raw_path = FIGURES_DIR / 'fig_15_lut_lookup_principles.raw.json'
    raw_payload = json.loads(raw_path.read_text(encoding='utf-8'))
    raw_payload.update({
        'source': 'generated schematic from paper_pipeline.make_lut_lookup_principles_figure',
        'focus': 'Simplified LUT deployment principle with offline sampling and runtime nearest/linear lookup paths.',
        'omitted_secondary_details': [
            'full MCU memory layout',
            'dense procedural flowchart',
            'auxiliary diagnostic icons',
            'duplicate miniature activation plots',
        ],
        'panels': ['offline table construction', 'runtime MCU lookup'],
    })
    save_json(raw_path, raw_payload)
    return name

def make_dataset_preprocessing_workflow_figure() -> str:
    cfg = get_figure_config('fig_19_dataset_preprocessing_workflow')
    fig, ax = plt.subplots(
        figsize=_as_float_tuple(cfg.get('figsize'), (7.2, 9.2)),
        constrained_layout=True,
    )
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    schematic_boxes: List[Dict[str, Any]] = []
    schematic_arrows: List[Dict[str, Any]] = []

    def draw_round_box(x: float, y: float, w: float, h: float, face: str, edge: str) -> None:
        box = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle='round,pad=0.012,rounding_size=0.022',
            facecolor=face,
            edgecolor=edge,
            lw=1.35,
        )
        ax.add_patch(box)

    def draw_sine_icon(x: float, y: float, w: float, h: float, color: str) -> None:
        xs = np.linspace(x, x + w, 120)
        ys = y + h * (0.50 + 0.28 * np.sin(np.linspace(0, 2.5 * np.pi, 120)))
        ax.plot(xs, ys, color=color, lw=1.8)
        ax.plot([x, x + w], [y + h * 0.18, y + h * 0.18], color='#8a96a3', lw=0.8)
        ax.plot([x, x], [y + h * 0.18, y + h * 0.84], color='#8a96a3', lw=0.8)
        ax.scatter([x + w * 0.75], [y + h * 0.78], s=26, color='#c96b00', zorder=4)

    def draw_response_icon(x: float, y: float, w: float, h: float, color: str) -> None:
        xs = np.linspace(x, x + w, 100)
        center = x + w * 0.58
        ys = y + h * (0.22 + 0.58 / (1.0 + ((xs - center) / (w * 0.18)) ** 2))
        ax.plot(xs, ys, color=color, lw=1.8)
        ax.fill_between(xs, y + h * 0.18, ys, color=color, alpha=0.12)
        ax.plot([x, x + w], [y + h * 0.18, y + h * 0.18], color='#8a96a3', lw=0.8)

    def draw_pair_icon(x: float, y: float, w: float, h: float, color: str) -> None:
        xs = np.linspace(x, x + w * 0.78, 90)
        for offset, alpha, line_color in [(0.67, 1.0, color), (0.34, 0.85, '#c96b00')]:
            ys = y + h * (offset + 0.11 * np.sin(np.linspace(0, 2.3 * np.pi, 90)))
            ax.plot(xs, ys, color=line_color, lw=1.45, alpha=alpha)
        for i in range(3):
            ax.add_patch(plt.Rectangle((x + w * (0.82 + i * 0.055), y + h * 0.25), w * 0.035, h * 0.55, facecolor='#ffffff', edgecolor='#9aa6b2', lw=0.8))

    def draw_split_icon(x: float, y: float, w: float, h: float, color: str) -> None:
        ax.add_patch(plt.Rectangle((x, y + h * 0.23), w * 0.42, h * 0.54, facecolor='#dcefe7', edgecolor=color, lw=1.1))
        ax.add_patch(plt.Rectangle((x + w * 0.48, y + h * 0.23), w * 0.42, h * 0.54, facecolor='#f4e8fb', edgecolor='#6a3d9a', lw=1.1))
        ax.plot([x + w * 0.45, x + w * 0.45], [y + h * 0.20, y + h * 0.82], color='#555555', lw=1.0, ls='--')
        ax.text(x + w * 0.21, y + h * 0.50, '50', ha='center', va='center', fontsize=7.0, color=color, weight='bold')
        ax.text(x + w * 0.69, y + h * 0.50, '50', ha='center', va='center', fontsize=7.0, color='#6a3d9a', weight='bold')

    def draw_window_icon(x: float, y: float, w: float, h: float, color: str) -> None:
        xs = np.linspace(x, x + w, 120)
        ys = y + h * (0.50 + 0.22 * np.sin(np.linspace(0, 3.0 * np.pi, 120)))
        ax.plot(xs, ys, color='#617182', lw=1.2)
        win_x = x + w * 0.37
        ax.add_patch(plt.Rectangle((win_x, y + h * 0.17), w * 0.34, h * 0.66, facecolor=color, edgecolor=color, alpha=0.16, lw=1.0))
        ax.plot(xs[(xs >= win_x) & (xs <= win_x + w * 0.34)], ys[(xs >= win_x) & (xs <= win_x + w * 0.34)], color=color, lw=2.0)

    def draw_norm_icon(x: float, y: float, w: float, h: float, color: str) -> None:
        ax.plot([x + w * 0.12, x + w * 0.88], [y + h * 0.34, y + h * 0.34], color='#8a96a3', lw=1.0)
        ax.plot([x + w * 0.12, x + w * 0.12], [y + h * 0.25, y + h * 0.75], color='#8a96a3', lw=1.0)
        ax.plot([x + w * 0.88, x + w * 0.88], [y + h * 0.25, y + h * 0.75], color='#8a96a3', lw=1.0)
        ax.add_patch(plt.Rectangle((x + w * 0.20, y + h * 0.30), w * 0.14, h * 0.34, facecolor='#dfe6ee', edgecolor='#617182', lw=0.8))
        ax.add_patch(plt.Rectangle((x + w * 0.47, y + h * 0.30), w * 0.14, h * 0.48, facecolor='#dfe6ee', edgecolor='#617182', lw=0.8))
        ax.add_patch(plt.Rectangle((x + w * 0.72, y + h * 0.30), w * 0.14, h * 0.24, facecolor=color, edgecolor=color, lw=0.8, alpha=0.65))
        ax.text(x + w * 0.12, y + h * 0.14, '-1', ha='center', va='center', fontsize=6.8, color='#617182')
        ax.text(x + w * 0.88, y + h * 0.14, '1', ha='center', va='center', fontsize=6.8, color='#617182')

    def draw_tensor_icon(x: float, y: float, w: float, h: float, color: str) -> None:
        base = np.array([[x + w * 0.18, y + h * 0.28], [x + w * 0.68, y + h * 0.28], [x + w * 0.68, y + h * 0.65], [x + w * 0.18, y + h * 0.65]])
        shift = np.array([w * 0.16, h * 0.13])
        ax.add_patch(Polygon(base + shift, closed=True, facecolor='#fbe3df', edgecolor='#a61c3c', lw=1.0, alpha=0.78))
        ax.add_patch(Polygon(base, closed=True, facecolor='#ffffff', edgecolor=color, lw=1.1))
        for p0, p1 in zip(base, base + shift):
            ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color='#9aa6b2', lw=0.8)
        for frac in [0.33, 0.66]:
            ax.plot([base[0, 0] + (base[1, 0] - base[0, 0]) * frac, base[3, 0] + (base[2, 0] - base[3, 0]) * frac], [base[0, 1], base[3, 1]], color='#9aa6b2', lw=0.65)
            ax.plot([base[0, 0], base[1, 0]], [base[0, 1] + (base[3, 1] - base[0, 1]) * frac, base[1, 1] + (base[2, 1] - base[1, 1]) * frac], color='#9aa6b2', lw=0.65)

    steps = [
        ('1', 'MET excitation', 'frequency sweep f; magnitude sweep m', draw_sine_icon),
        ('2', 'Ideal reference', 'low-magnitude fitted second-order response', draw_response_icon),
        ('3', 'Paired matrix D', 'measured waveform paired with ideal waveform', draw_pair_icon),
        ('4', '50% / 50% split', '175 train records; 175 validation records', draw_split_icon),
        ('5', 'Windowing', 'steady-state segment, 8000 samples', draw_window_icon),
        ('6', 'Normalization', 'per-channel min-max scaling to [-1, 1]', draw_norm_icon),
        ('7', 'Model tensors', 'paired input and target sequences', draw_tensor_icon),
    ]
    colors = ['#e8f1fb', '#eaf7ee', '#fff4df', '#f1ecfb', '#e8f6f7', '#eef2f7', '#fdeceb']
    ys = np.linspace(0.86, 0.12, len(steps))
    box_x = 0.12
    box_w = 0.78
    box_h = 0.092
    icon_x = 0.17
    icon_w = 0.18
    edge = '#355070'
    for idx, ((number, title, body, icon_func), y_center, color) in enumerate(zip(steps, ys, colors)):
        y = y_center - box_h / 2
        draw_round_box(box_x, y, box_w, box_h, color, edge)
        box_id = f'step_{number}'
        schematic_boxes.append({'id': box_id, 'bbox': [box_x, y, box_x + box_w, y + box_h]})
        ax.text(
            box_x - 0.045,
            y_center,
            number,
            ha='center',
            va='center',
            fontsize=8.8,
            weight='bold',
            color='white',
            bbox=dict(boxstyle='circle,pad=0.25', facecolor=edge, edgecolor='none'),
        )
        icon_func(icon_x, y + box_h * 0.13, icon_w, box_h * 0.74, edge)
        ax.text(0.405, y_center + box_h * 0.18, title, ha='left', va='center', fontsize=10.6, weight='bold', color='#222222')
        ax.text(0.405, y_center - box_h * 0.20, body, ha='left', va='center', fontsize=8.8, color='#333333')
        if idx < len(ys) - 1:
            start = (0.51, y_center - box_h / 2)
            end = (0.51, ys[idx + 1] + box_h / 2)
            ax.annotate(
                '',
                xy=end,
                xytext=start,
                arrowprops=dict(arrowstyle='->', lw=1.45, color='#4a5568'),
            )
            schematic_arrows.append({
                'id': f'step_{number}_to_step_{steps[idx + 1][0]}',
                'points': [list(start), list(end)],
                'source': box_id,
                'target': f'step_{steps[idx + 1][0]}',
                'require_axis_aligned': True,
            })
    out = FIGURES_DIR / 'fig_19_dataset_preprocessing_workflow.png'
    _save_matplotlib_figure(fig, out, raw_payload={
        'source_trace': 'AI-rendered schematic asset existed without editable source; replaced by a code-generated schematic to enforce the documented 50/50 split.',
        'modification_scope': 'vertical illustrated dataset split and data-construction workflow',
        'split': {'train_records': 175, 'validation_records': 175, 'unit': 'frequency--magnitude operating points'},
        'visual_elements': ['sine sweep icon', 'second-order response icon', 'paired waveform icon', 'split icon', 'windowed waveform icon', 'normalization scale icon', 'tensor grid icon'],
        VISUAL_AUDIT_KEY: audit_schematic_geometry(
            schematic_boxes,
            schematic_arrows,
            context='dataset preprocessing workflow schematic geometry',
        ),
    }, bbox_inches='tight')
    return out.name


def copy_manual_paper_asset(source_name: str, target_name: str, note: str) -> str:
    src = PAPER_DIR / 'image_manual' / source_name
    dst = FIGURES_DIR / target_name
    if not src.exists():
        raise FileNotFoundError(f'Missing manual paper figure asset: {src}')
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    save_json(dst.with_suffix('.raw.json'), {
        'source_trace': f'docs/paper/image_manual/{source_name}',
        'generation': 'manual figure asset copied without code redraw',
        'modification_scope': note,
    })
    return dst.name


def _stage_external_bitmap_for_montage(source_path: Path, staged_name: str) -> str:
    if not source_path.exists():
        raise FileNotFoundError(f'Missing source bitmap for Studio wrapper: {source_path}')
    staged = MONTAGE_PANEL_DIR / staged_name
    staged.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, staged)
    return panel_source_name(staged.name)


def make_wrapped_bitmap_figure(
    figure_key: str,
    source_path: Path,
    output_name: str,
    *,
    default_fit_width: int | None = None,
    default_fit_height: int | None = None,
    default_trim_border: int | None = None,
    note: str,
    latex_width_fraction: float = 1.0,
) -> str:
    source_rel = _stage_external_bitmap_for_montage(source_path, f'{figure_key}_source{source_path.suffix}')
    panel: Dict[str, Any] = {'source': source_rel, 'align_x': 'center', 'align_y': 'center'}
    if default_fit_width is not None:
        panel['fit_width'] = default_fit_width
    if default_fit_height is not None:
        panel['fit_height'] = default_fit_height
    if default_trim_border is not None:
        panel['trim_border'] = default_trim_border
    name = make_bitmap_montage(
        output_name,
        [panel],
        layout='matrix',
        rows=1,
        cols=1,
        padding=0,
        gutter=0,
        label_font_size=54,
        note=note,
        latex_width_fraction=latex_width_fraction,
        figure_key=figure_key,
    )
    raw_path = FIGURES_DIR / Path(output_name).with_suffix('.raw.json')
    raw_payload = json.loads(raw_path.read_text(encoding='utf-8'))
    raw_payload['source_bitmap'] = str(source_path.relative_to(ROOT)).replace('\\', '/')
    raw_payload['studio_wrapper'] = True
    save_json(raw_path, raw_payload)
    return name


def make_met_structure_figure() -> str:
    return make_wrapped_bitmap_figure(
        'met_structure',
        PAPER_DIR / 'image' / '4.MET_structure.png',
        'met_structure.png',
        default_fit_width=2500,
        default_trim_border=28,
        note='Studio-adjustable wrapper for the MET structure bitmap used inside Fig. 20.',
    )


def make_readout_circuit_figure() -> str:
    return make_wrapped_bitmap_figure(
        'readout_circuit',
        PAPER_DIR / 'image' / '39.Readout_circuit.png',
        'readout_circuit.png',
        default_fit_width=2500,
        default_trim_border=28,
        note='Studio-adjustable wrapper for the readout circuit bitmap used inside Fig. 20.',
    )


def make_calibration_table_test_figure() -> str:
    return make_wrapped_bitmap_figure(
        'calibration_table_test',
        PAPER_DIR / 'image' / '5.Calibration_table_test.png',
        'calibration_table_test.png',
        default_fit_width=3600,
        default_trim_border=90,
        note='Studio-adjustable wrapper for the experimental setup photograph used inside Fig. 21.',
    )


def make_kan_neuron_compensation_figure() -> str:
    return make_wrapped_bitmap_figure(
        'kan_neuron_compensation',
        FIGURES_DIR / 'fig_07_kan_neuron_compensation.png',
        'kan_neuron_compensation.png',
        default_fit_width=3156,
        note='Studio-adjustable wrapper for the traced KAN-neuron compensation bitmap used inside Fig. 23.',
    )


def make_mechanism_schematic_wrapper() -> str:
    return make_wrapped_bitmap_figure(
        'fig_14_met_nonlinear_mechanism',
        PAPER_DIR / 'assets' / 'fig_14_met_nonlinear_mechanism_ai.png',
        'fig_14_met_nonlinear_mechanism.png',
        default_fit_width=2400,
        note='Studio-adjustable wrapper for the AI-rendered MET nonlinear mechanism schematic.',
    )


def make_wiener_kan_framework_figure() -> str:
    return make_wrapped_bitmap_figure(
        'wiener_kan_framework',
        PAPER_DIR / 'image_manual' / 'wiener_kan_framework.png',
        'wiener_kan_framework.png',
        default_fit_width=3000,
        note='Studio-adjustable wrapper for the manual Wiener-KAN framework schematic.',
    )


def make_met_nonlinear_frequency_response_figure() -> str:
    cfg = get_figure_config('met_nonlinear_frequency_response')
    xy_cfg = cfg.get('xy_plot') if isinstance(cfg.get('xy_plot'), dict) else {}
    legend_cfg = cfg.get('legend') if isinstance(cfg.get('legend'), dict) else {}
    data_path = ROOT / 'projects' / '01_LR_STUDY' / 'FRIKANh8u6l6_e1k_lr7e4' / 'data' / 'linear_response.json'
    with data_path.open('r', encoding='utf-8') as f:
        data = json.load(f)
    frequencies = np.array(data['frequencies'], dtype=float)
    magnitudes_arr = np.array(data['magnitudes'], dtype=float)
    gains_origin = [np.array(row, dtype=float) for row in data['gains_origin']]
    fig, ax = plt.subplots(figsize=_as_float_tuple(cfg.get('figsize'), (7.2, 4.8)))
    cmap = plt.cm.get_cmap(str(cfg.get('colormap', 'tab20')), len(magnitudes_arr))
    handles = []
    labels = []
    for idx, (magnitude, gain) in enumerate(zip(magnitudes_arr, gains_origin)):
        handle, = ax.loglog(
            frequencies,
            gain,
            color=cmap(idx),
            linewidth=float(cfg.get('line_width', 1.35)),
            label=rf'{magnitude:.2f} m/s$^2$',
        )
        handles.append(handle)
        labels.append(rf'{magnitude:.2f} m/s$^2$')
    ax.set_xlabel(
        'Frequency (Hz)',
        fontsize=float(xy_cfg.get('label_fontsize', 12)),
        labelpad=float(xy_cfg.get('labelpad', 4)),
    )
    ax.set_ylabel(
        'Sensitivity (V s/m)',
        fontsize=float(xy_cfg.get('label_fontsize', 12)),
        labelpad=float(xy_cfg.get('labelpad', 4)),
    )
    if 'xlim' in xy_cfg:
        ax.set_xlim(*_as_float_tuple(xy_cfg.get('xlim'), (10.0, 128.0)))
    else:
        ax.set_xlim(10, 128)
    if 'ylim' in xy_cfg:
        ax.set_ylim(*_as_float_tuple(xy_cfg.get('ylim'), (30.0, 250.0)))
    else:
        ax.set_ylim(30, 250)
    ax.grid(True, which='both', linestyle='--', alpha=float(cfg.get('grid_alpha', 0.45)))
    ax.tick_params(
        axis='both',
        which='major',
        labelsize=float(xy_cfg.get('tick_fontsize', 10)),
        pad=float(xy_cfg.get('tick_pad', 3)),
    )
    ax.legend(
        handles,
        labels,
        loc=str(legend_cfg.get('loc', 'center left')),
        bbox_to_anchor=tuple(legend_cfg.get('bbox_to_anchor', [1.02, 0.5])),
        frameon=bool(legend_cfg.get('frameon', False)),
        fontsize=float(legend_cfg.get('fontsize', 8.5)),
        ncol=int(legend_cfg.get('ncol', 1)),
        borderaxespad=0.0,
        handlelength=2.2,
    )
    margins = cfg.get('margins') if isinstance(cfg.get('margins'), dict) else {}
    fig.subplots_adjust(
        left=float(margins.get('left', 0.12)),
        right=float(margins.get('right', 0.72)),
        bottom=float(margins.get('bottom', 0.16)),
        top=float(margins.get('top', 0.96)),
    )
    out = FIGURES_DIR / 'met_nonlinear_frequency_response.png'
    return _save_matplotlib_figure(
        fig,
        out,
        raw_payload={
            'source': 'projects/01_LR_STUDY/FRIKANh8u6l6_e1k_lr7e4/data/linear_response.json:gains_origin',
            'modification_scope': 'Studio-adjustable frequency response redraw with shared X-Y plot and legend controls.',
        },
        bbox_inches='tight',
        pad_inches=0.08,
    )


def make_local_transfer_slices_figure() -> str:
    cfg = get_figure_config('local_transfer_slices')
    panel_cfg = cfg.get('surface_panels') if isinstance(cfg.get('surface_panels'), dict) else {}
    try:
        from src.translate_legacy_figures import (  # type: ignore  # noqa: E402
            TMP_DIR,
            calculate_system_response,
            calculate_system_response_comp,
            plot_frirnn_panel,
        )
    except ImportError:  # pragma: no cover - direct script execution
        from translate_legacy_figures import (  # type: ignore  # noqa: E402
            TMP_DIR,
            calculate_system_response,
            calculate_system_response_comp,
            plot_frirnn_panel,
        )
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    original_path = TMP_DIR / 'response_original_temp.png'
    compensated_path = TMP_DIR / 'response_compensated_temp.png'

    def draw_surface(path: Path, response_fn: Any, z_ticks: List[float], zlabel: str, fallback_left: float) -> Dict[str, Any]:
        fig = plt.figure(figsize=_as_float_tuple(panel_cfg.get('figsize'), (6.8, 5.4)))
        ax = fig.add_subplot(111, projection='3d')
        plot_frirnn_panel(ax, response_fn, z_ticks=z_ticks, zlabel=zlabel)
        ax.view_init(elev=float(panel_cfg.get('elev', 40)), azim=float(panel_cfg.get('azim', -140)))
        ax.tick_params(axis='both', which='major', labelsize=float(panel_cfg.get('tick_fontsize', 9)))
        ax.tick_params(axis='z', which='major', labelsize=float(panel_cfg.get('tick_fontsize', 9)))
        fig.subplots_adjust(
            left=float(panel_cfg.get('left', fallback_left)),
            right=float(panel_cfg.get('right', 0.97)),
            bottom=float(panel_cfg.get('bottom', 0.18)),
            top=float(panel_cfg.get('top', 0.98)),
        )
        audit = audit_matplotlib_figure(fig, context=f'local_transfer_slices panel {path.name}')
        _save_matplotlib_figure(
            fig,
            path,
            raw_payload={
                'source_trace': 'docs/paper/src/paper_pipeline.py:make_local_transfer_slices_figure',
                'panel': path.name,
                VISUAL_AUDIT_KEY: audit,
            },
            dpi=600,
            bbox_inches='tight',
            pad_inches=float(panel_cfg.get('pad_inches', 0.22)),
        )
        return audit

    audit_original = draw_surface(original_path, calculate_system_response, [30, 50, 100, 200], 'Sensitivity (V s/m)', 0.16)
    audit_compensated = draw_surface(compensated_path, calculate_system_response_comp, [0.2, 0.5, 1, 2], 'Relative gain', 0.15)
    out_name = make_bitmap_montage(
        'local_transfer_slices.png',
        [
            {'source': str(original_path), 'label': '(a)', 'fit_width': 2700, 'trim_border': 80},
            {'source': str(compensated_path), 'label': '(b)', 'fit_width': 2700, 'trim_border': 80},
        ],
        layout='horizontal',
        padding=[85, 75, 85, 85],
        gutter=(120, 80),
        label_font_size=62,
        label_font_size_pt=8.0,
        latex_width_fraction=1.0,
        note='Studio-adjustable two-panel local transfer slice montage.',
        figure_key='local_transfer_slices',
    )
    out = FIGURES_DIR / out_name
    raw_path = out.with_suffix('.raw.json')
    raw_payload = json.loads(raw_path.read_text(encoding='utf-8'))
    raw_payload[VISUAL_AUDIT_KEY] = combine_audits(
        audit_original,
        audit_compensated,
        raw_payload.get(VISUAL_AUDIT_KEY, {}),
        context='local_transfer_slices.png',
    )
    save_json(raw_path, raw_payload)
    return out_name


def make_board_inference_validation_workflow_figure() -> str:
    cfg = get_figure_config('fig_17_board_inference_validation_workflow')
    schematic_boxes: List[Dict[str, Any]] = []
    schematic_arrows: List[Dict[str, Any]] = []

    def reset_schematic_geometry() -> None:
        schematic_boxes.clear()
        schematic_arrows.clear()

    def schematic_payload(context: str) -> Dict[str, Any]:
        return {
            VISUAL_AUDIT_KEY: audit_schematic_geometry(
                list(schematic_boxes),
                list(schematic_arrows),
                context=context,
            )
        }

    def configure_axis(ax: Any) -> None:
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

    def draw_card(
        ax: Any,
        x: float,
        y: float,
        w: float,
        h: float,
        title: str,
        body: str,
        face: str,
        edge: str,
        *,
        card_id: str | None = None,
        title_size: float = 9.2,
        body_size: float = 7.6,
    ) -> None:
        rect = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle='round,pad=0.012,rounding_size=0.020',
            facecolor=face,
            edgecolor=edge,
            lw=1.45,
        )
        ax.add_patch(rect)
        if card_id:
            schematic_boxes.append({'id': card_id, 'bbox': [x, y, x + w, y + h]})
        ax.text(x + w / 2, y + h * 0.34, title, ha='center', va='center', fontsize=title_size, weight='bold', color='#222222')
        ax.text(x + w / 2, y + h * 0.17, body, ha='center', va='center', fontsize=body_size, color='#333333')

    def routed_arrow(
        ax: Any,
        points: List[tuple[float, float]],
        color: str = '#333333',
        lw: float = 1.6,
        *,
        arrow_id: str,
        source: str,
        target: str,
        full_points: List[tuple[float, float]] | None = None,
        require_axis_aligned: bool = True,
    ) -> None:
        for start, end in zip(points[:-2], points[1:-1]):
            ax.plot([start[0], end[0]], [start[1], end[1]], color=color, lw=lw, solid_capstyle='round')
        ax.annotate('', xy=points[-1], xytext=points[-2], arrowprops=dict(arrowstyle='->', lw=lw, color=color, shrinkA=0, shrinkB=0))
        arrow_payload: Dict[str, Any] = {
            'id': arrow_id,
            'points': [[float(x), float(y)] for x, y in points],
            'source': source,
            'target': target,
            'endpoint_policy': 'outside_clearance',
        }
        if require_axis_aligned:
            arrow_payload['require_axis_aligned'] = True
        if full_points is not None:
            arrow_payload['full_points'] = [[float(x), float(y)] for x, y in full_points]
            arrow_payload['max_length_fraction'] = SHORT_CONNECTOR_FRACTION
        schematic_arrows.append(arrow_payload)

    def icon_neural_project(ax: Any, x: float, y: float, w: float, h: float, color: str) -> None:
        xs = [x + w * 0.18, x + w * 0.50, x + w * 0.82]
        ys_left = [y + h * 0.28, y + h * 0.72]
        ys_mid = [y + h * 0.22, y + h * 0.50, y + h * 0.78]
        ys_right = [y + h * 0.50]
        for yy0 in ys_left:
            for yy1 in ys_mid:
                ax.plot([xs[0], xs[1]], [yy0, yy1], color=color, lw=0.75, alpha=0.55)
        for yy0 in ys_mid:
            ax.plot([xs[1], xs[2]], [yy0, ys_right[0]], color=color, lw=0.75, alpha=0.55)
        for xx, y_list in [(xs[0], ys_left), (xs[1], ys_mid), (xs[2], ys_right)]:
            for yy in y_list:
                ax.add_patch(Circle((xx, yy), w * 0.045, facecolor='white', edgecolor=color, lw=1.1))
        t = np.linspace(0.0, 1.0, 80)
        ax.plot(x + w * (0.10 + 0.78 * t), y + h * (0.06 + 0.08 * np.sin(2 * np.pi * t)), color='#c96b00', lw=1.1)

    def icon_c_package(ax: Any, x: float, y: float, w: float, h: float, color: str) -> None:
        sheet = Polygon(
            [[x + w * 0.18, y + h * 0.12], [x + w * 0.74, y + h * 0.12], [x + w * 0.74, y + h * 0.84], [x + w * 0.52, y + h * 0.84], [x + w * 0.18, y + h * 0.64]],
            closed=True,
            facecolor='white',
            edgecolor=color,
            lw=1.2,
        )
        ax.add_patch(sheet)
        ax.plot([x + w * 0.52, x + w * 0.52, x + w * 0.74], [y + h * 0.84, y + h * 0.64, y + h * 0.64], color=color, lw=1.0)
        ax.text(x + w * 0.45, y + h * 0.55, 'C', ha='center', va='center', fontsize=13, weight='bold', color=color)
        for i in range(4):
            yy = y + h * (0.24 + 0.08 * i)
            ax.plot([x + w * 0.30, x + w * 0.62], [yy, yy], color='#9cc7bc', lw=1.0)
        ax.add_patch(plt.Rectangle((x + w * 0.79, y + h * 0.24), w * 0.11, h * 0.12, facecolor='#dcefe7', edgecolor=color, lw=0.9))
        ax.add_patch(plt.Rectangle((x + w * 0.79, y + h * 0.42), w * 0.11, h * 0.12, facecolor='#dcefe7', edgecolor=color, lw=0.9))
        ax.add_patch(plt.Rectangle((x + w * 0.79, y + h * 0.60), w * 0.11, h * 0.12, facecolor='#dcefe7', edgecolor=color, lw=0.9))

    def icon_chip(ax: Any, x: float, y: float, w: float, h: float, color: str, label: str = 'MCU') -> None:
        chip = FancyBboxPatch(
            (x + w * 0.22, y + h * 0.18),
            w * 0.56,
            h * 0.58,
            boxstyle='round,pad=0.006,rounding_size=0.012',
            facecolor='white',
            edgecolor=color,
            lw=1.3,
        )
        ax.add_patch(chip)
        for yy in np.linspace(y + h * 0.27, y + h * 0.67, 4):
            ax.plot([x + w * 0.12, x + w * 0.22], [yy, yy], color=color, lw=1.0)
            ax.plot([x + w * 0.78, x + w * 0.88], [yy, yy], color=color, lw=1.0)
        for xx in np.linspace(x + w * 0.33, x + w * 0.67, 3):
            ax.plot([xx, xx], [y + h * 0.08, y + h * 0.18], color=color, lw=1.0)
            ax.plot([xx, xx], [y + h * 0.76, y + h * 0.86], color=color, lw=1.0)
        ax.text(x + w * 0.50, y + h * 0.49, label, ha='center', va='center', fontsize=8.6, weight='bold', color=color)

    def icon_wave_reference(ax: Any, x: float, y: float, w: float, h: float) -> None:
        t = np.linspace(0.0, 1.0, 120)
        ax.plot(x + w * (0.05 + 0.62 * t), y + h * (0.30 + 0.18 * np.sin(2.5 * np.pi * t)), color='#1f4e79', lw=1.2)
        ax.plot(x + w * (0.05 + 0.62 * t), y + h * (0.64 + 0.12 * np.sin(2.5 * np.pi * t + 0.25)), color='#c96b00', lw=1.2)
        for xx, height in [(0.78, 0.45), (0.86, 0.62), (0.94, 0.34)]:
            ax.add_patch(plt.Rectangle((x + w * xx, y + h * 0.18), w * 0.045, h * height, facecolor='#f7f7f7', edgecolor='#555555', lw=0.8))
        ax.text(x + w * 0.83, y + h * 0.82, 'TF', ha='center', va='center', fontsize=7.3, weight='bold', color='#555555')

    def icon_qemu(ax: Any, x: float, y: float, w: float, h: float) -> None:
        monitor = plt.Rectangle((x + w * 0.12, y + h * 0.34), w * 0.58, h * 0.42, facecolor='white', edgecolor='#0f6c5c', lw=1.1)
        ax.add_patch(monitor)
        t = np.linspace(0.0, 1.0, 50)
        ax.plot(x + w * (0.18 + 0.46 * t), y + h * (0.55 + 0.10 * np.sin(2 * np.pi * t)), color='#0f6c5c', lw=1.1)
        ax.plot([x + w * 0.35, x + w * 0.47], [y + h * 0.25, y + h * 0.25], color='#0f6c5c', lw=1.1)
        ax.plot([x + w * 0.41, x + w * 0.41], [y + h * 0.25, y + h * 0.34], color='#0f6c5c', lw=1.1)
        ax.add_patch(Circle((x + w * 0.82, y + h * 0.55), w * 0.085, facecolor='#eaf6f1', edgecolor='#0f6c5c', lw=1.1))
        ax.text(x + w * 0.82, y + h * 0.55, 'Q', ha='center', va='center', fontsize=8.2, weight='bold', color='#0f6c5c')

    def icon_uart_metrics(ax: Any, x: float, y: float, w: float, h: float) -> None:
        icon_chip(ax, x + w * 0.02, y + h * 0.08, w * 0.50, h * 0.82, '#1f4e79', label='F405')
        ax.plot([x + w * 0.54, x + w * 0.72], [y + h * 0.55, y + h * 0.55], color='#1f4e79', lw=1.0)
        for i in range(3):
            ax.add_patch(Circle((x + w * (0.76 + 0.07 * i), y + h * 0.55), w * 0.018, facecolor='#c96b00', edgecolor='none'))
        ax.text(x + w * 0.77, y + h * 0.72, 'UART', ha='center', va='center', fontsize=6.8, color='#1f4e79', weight='bold')

    def icon_metric_card(ax: Any, x: float, y: float, w: float, h: float, color: str) -> None:
        ax.add_patch(Circle((x + w * 0.24, y + h * 0.54), w * 0.12, facecolor='#ffffff', edgecolor=color, lw=1.1))
        ax.plot([x + w * 0.24, x + w * 0.31], [y + h * 0.54, y + h * 0.62], color=color, lw=1.1)
        bars = [0.30, 0.48, 0.66]
        for idx, xx in enumerate(bars):
            ax.add_patch(plt.Rectangle((x + w * xx, y + h * 0.22), w * 0.055, h * (0.22 + 0.08 * idx), facecolor=color, edgecolor=color, lw=0.8, alpha=0.55))

    export_cfg = cfg.get('export_panel') or {}
    fig_export, ax_export = plt.subplots(
        figsize=_as_float_tuple(export_cfg.get('figsize'), (7.15, 3.9)),
        constrained_layout=True,
    )
    configure_axis(ax_export)
    reset_schematic_geometry()
    draw_card(ax_export, 0.05, 0.17, 0.23, 0.67, 'trained\nWiener-KAN', 'weights + norms', '#eef3fb', '#1f4e79', card_id='trained_project', title_size=float(export_cfg.get('card_title_size', 9.5)), body_size=float(export_cfg.get('card_body_size', 7.5)))
    draw_card(ax_export, 0.37, 0.13, 0.28, 0.75, 'C export\npackage', 'arrays, LUTs,\nscales', '#f1f8f5', '#0f6c5c', card_id='c_export', title_size=float(export_cfg.get('card_title_size', 9.5)), body_size=float(export_cfg.get('c_export_card_body_size', 7.4)))
    draw_card(ax_export, 0.77, 0.17, 0.18, 0.67, 'embedded C\nkernel', 'sample-by-sample\ninference', '#fff7e8', '#c96b00', card_id='embedded_kernel', title_size=float(export_cfg.get('embedded_card_title_size', 9.3)), body_size=float(export_cfg.get('embedded_card_body_size', 7.1)))
    icon_neural = export_cfg.get('icon_neural_project', {})
    icon_neural_project(ax_export, float(icon_neural.get('x', 0.08)), float(icon_neural.get('y', 0.48)), float(icon_neural.get('w', 0.17)), float(icon_neural.get('h', 0.32)), '#1f4e79')
    icon_pkg = export_cfg.get('icon_c_package', {})
    icon_c_package(ax_export, float(icon_pkg.get('x', 0.42)), float(icon_pkg.get('y', 0.41)), float(icon_pkg.get('w', 0.19)), float(icon_pkg.get('h', 0.40)), '#0f6c5c')
    icon_ch = export_cfg.get('icon_chip', {})
    icon_chip(ax_export, float(icon_ch.get('x', 0.79)), float(icon_ch.get('y', 0.47)), float(icon_ch.get('w', 0.13)), float(icon_ch.get('h', 0.33)), '#c96b00', label='C')
    trained_to_export_full = [(0.28, 0.505), (0.37, 0.505)]
    export_to_kernel_full = [(0.65, 0.505), (0.77, 0.505)]
    export_arrow_lw = float(export_cfg.get('arrow_lw', 1.9))
    routed_arrow(
        ax_export,
        _shorten_polyline(trained_to_export_full),
        '#1f4e79',
        lw=export_arrow_lw,
        arrow_id='trained_to_export',
        source='trained_project',
        target='c_export',
        full_points=trained_to_export_full,
    )
    routed_arrow(
        ax_export,
        _shorten_polyline(export_to_kernel_full),
        '#0f6c5c',
        lw=export_arrow_lw,
        arrow_id='export_to_kernel',
        source='c_export',
        target='embedded_kernel',
        full_points=export_to_kernel_full,
    )
    export_source = save_panel_figure(
        fig_export,
        'fig_17_board_inference_validation_workflow_a_export.png',
        raw_payload=schematic_payload('board inference export panel'),
    )

    validate_cfg = cfg.get('validate_panel') or {}
    fig_validate, ax_validate = plt.subplots(
        figsize=_as_float_tuple(validate_cfg.get('figsize'), (7.15, 4.25)),
        constrained_layout=True,
    )
    configure_axis(ax_validate)
    reset_schematic_geometry()
    draw_card(ax_validate, 0.04, 0.33, 0.24, 0.40, 'test window\n+ TF reference', 'same input trace', '#f7f7f7', '#555555', card_id='test_window', title_size=float(validate_cfg.get('test_title_size', 8.9)), body_size=float(validate_cfg.get('test_body_size', 7.0)))
    draw_card(ax_validate, 0.36, 0.56, 0.28, 0.34, 'QEMU run', 'numerical\nconsistency', '#eaf6f1', '#0f6c5c', card_id='qemu_run', title_size=float(validate_cfg.get('card_title_size', 9.2)), body_size=float(validate_cfg.get('card_body_size', 7.0)))
    draw_card(ax_validate, 0.36, 0.10, 0.28, 0.39, 'STM32F405', 'Keil build\n+ UART loop', '#eef3fb', '#1f4e79', card_id='stm32_run', title_size=float(validate_cfg.get('card_title_size', 9.2)), body_size=float(validate_cfg.get('card_body_size', 7.0)))
    draw_card(ax_validate, 0.74, 0.58, 0.21, 0.28, 'QEMU-MAE', 'C vs TF', '#ffffff', '#0f6c5c', card_id='qemu_metric', title_size=float(validate_cfg.get('metric_title_size', 9.4)), body_size=7.0)
    draw_card(ax_validate, 0.74, 0.14, 0.21, 0.34, 'KEIL metrics', 'MAE, speed,\nRAM / Flash', '#ffffff', '#1f4e79', card_id='keil_metric', title_size=float(validate_cfg.get('card_title_size', 9.2)), body_size=float(validate_cfg.get('metric_body_size', 6.8)))
    icon_wave_ref = validate_cfg.get('icon_wave_reference', {})
    icon_wave_reference(ax_validate, float(icon_wave_ref.get('x', 0.07)), float(icon_wave_ref.get('y', 0.45)), float(icon_wave_ref.get('w', 0.18)), float(icon_wave_ref.get('h', 0.20)))
    icon_q = validate_cfg.get('icon_qemu', {})
    icon_qemu(ax_validate, float(icon_q.get('x', 0.41)), float(icon_q.get('y', 0.67)), float(icon_q.get('w', 0.19)), float(icon_q.get('h', 0.17)))
    icon_uart = validate_cfg.get('icon_uart_metrics', {})
    icon_uart_metrics(ax_validate, float(icon_uart.get('x', 0.40)), float(icon_uart.get('y', 0.18)), float(icon_uart.get('w', 0.21)), float(icon_uart.get('h', 0.20)))
    icon_qemu_card = validate_cfg.get('icon_metric_card_qemu', {})
    icon_metric_card(ax_validate, float(icon_qemu_card.get('x', 0.78)), float(icon_qemu_card.get('y', 0.67)), float(icon_qemu_card.get('w', 0.15)), float(icon_qemu_card.get('h', 0.15)), '#0f6c5c')
    icon_keil_card = validate_cfg.get('icon_metric_card_keil', {})
    icon_metric_card(ax_validate, float(icon_keil_card.get('x', 0.78)), float(icon_keil_card.get('y', 0.24)), float(icon_keil_card.get('w', 0.15)), float(icon_keil_card.get('h', 0.18)), '#1f4e79')
    test_to_qemu_full = [(0.28, 0.58), (0.36, 0.72)]
    test_to_stm32_full = [(0.28, 0.48), (0.36, 0.29)]
    qemu_to_metric_full = [(0.64, 0.72), (0.74, 0.72)]
    stm32_to_metric_full = [(0.64, 0.29), (0.74, 0.29)]
    validate_arrow_lw = float(validate_cfg.get('arrow_lw', 1.8))
    routed_arrow(
        ax_validate,
        _shorten_polyline(test_to_qemu_full),
        '#555555',
        lw=validate_arrow_lw,
        arrow_id='test_to_qemu',
        source='test_window',
        target='qemu_run',
        full_points=test_to_qemu_full,
        require_axis_aligned=False,
    )
    routed_arrow(
        ax_validate,
        _shorten_polyline(test_to_stm32_full),
        '#555555',
        lw=validate_arrow_lw,
        arrow_id='test_to_stm32',
        source='test_window',
        target='stm32_run',
        full_points=test_to_stm32_full,
        require_axis_aligned=False,
    )
    routed_arrow(
        ax_validate,
        _shorten_polyline(qemu_to_metric_full),
        '#0f6c5c',
        lw=validate_arrow_lw,
        arrow_id='qemu_to_metric',
        source='qemu_run',
        target='qemu_metric',
        full_points=qemu_to_metric_full,
    )
    routed_arrow(
        ax_validate,
        _shorten_polyline(stm32_to_metric_full),
        '#1f4e79',
        lw=validate_arrow_lw,
        arrow_id='stm32_to_metric',
        source='stm32_run',
        target='keil_metric',
        full_points=stm32_to_metric_full,
    )
    validate_source = save_panel_figure(
        fig_validate,
        'fig_17_board_inference_validation_workflow_b_validate.png',
        raw_payload=schematic_payload('board inference validation panel'),
    )

    name = make_bitmap_montage(
        'fig_17_board_inference_validation_workflow.png',
        [
            {'source': export_source, 'label': '(a)', 'fit_width': 2200, 'trim_border': 120},
            {'source': validate_source, 'label': '(b)', 'fit_width': 2200, 'trim_border': 120},
        ],
        layout='vertical',
        padding=[60, 55, 60, 55],
        gutter=(60, 60),
        label_font_size=50,
        note='Composes the export and two-target validation panels with the unified bitmap montage module.',
        figure_key='fig_17_board_inference_validation_workflow',
    )
    raw_path = FIGURES_DIR / 'fig_17_board_inference_validation_workflow.raw.json'
    raw_payload = json.loads(raw_path.read_text(encoding='utf-8'))
    raw_payload.update({
        'source': 'generated schematic from paper_pipeline.make_board_inference_validation_workflow_figure',
        'focus': 'Simplified embedded validation workflow with one C export and two validation targets.',
        'omitted_secondary_details': [
            'per-file generated C artifacts',
            'normalization formula blocks',
            'UART packet-level steps',
            'dense metric sidebars',
        ],
        'visual_elements': [
            'neural network project icon',
            'C source package and LUT table icons',
            'embedded chip icon',
            'paired waveform and TensorFlow reference icon',
            'QEMU monitor icon',
            'STM32F405 chip and UART dots icon',
            'metric gauge and bar icons',
        ],
        'panels': ['export once', 'validate on two targets'],
    })
    save_json(raw_path, raw_payload)
    return name

def make_parallel_wiener_principle_schematic(figure_key: str = 'fig_22_parallel_wiener_equivalent_montage') -> str:
    cfg = get_figure_config(figure_key)
    principle_cfg = cfg.get('principle_panel') or {}
    label_fs = float(principle_cfg.get('label_fontsize', 11))
    subtitle_fs = float(principle_cfg.get('subtitle_fontsize', 7.5))
    input_arrow_lw = float(principle_cfg.get('input_arrow_lw', 2.0))
    branch_arrow_lw = float(principle_cfg.get('branch_arrow_lw', 1.7))
    h_to_f_arrow_lw = float(principle_cfg.get('h_to_f_arrow_lw', 1.8))
    f_to_sum_arrow_lw = float(principle_cfg.get('f_to_sum_arrow_lw', 1.65))
    input_text = str(principle_cfg.get('input_text', 'input\nx(t)'))
    input_x = float(principle_cfg.get('input_x', 0.08))
    output_text = str(principle_cfg.get('output_text', 'output\ny(t)'))
    output_x = float(principle_cfg.get('output_x', 0.94))
    margin_left = float(principle_cfg.get('margin_left', 0.0))
    margin_right = float(principle_cfg.get('margin_right', 0.0))
    margin_top = float(principle_cfg.get('margin_top', 0.0))
    margin_bottom = float(principle_cfg.get('margin_bottom', 0.0))
    pad_inches = float(principle_cfg.get('pad_inches', 0.08))
    fig, ax = plt.subplots(
        figsize=_as_float_tuple(principle_cfg.get('figsize'), (10.8, 4.5)),
        constrained_layout=True,
    )
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    schematic_boxes: List[Dict[str, Any]] = []
    schematic_arrows: List[Dict[str, Any]] = []
    split_point = (0.15, 0.50)
    ax.text(input_x, 0.50, input_text, ha='center', va='center', fontsize=label_fs, weight='bold')
    input_arrow_points, input_arrow_raw = _short_arrow_payload(
        'input_to_split',
        [(input_x + 0.03, 0.50), split_point],
        require_axis_aligned=True,
    )
    ax.annotate('', xy=input_arrow_points[-1], xytext=input_arrow_points[0], arrowprops=dict(arrowstyle='->', lw=input_arrow_lw, color='#333333', shrinkA=0, shrinkB=0))
    schematic_arrows.append(input_arrow_raw)
    branch_y = [0.72, 0.50, 0.28]
    branch_names = ['low magnitude', 'middle magnitude', 'high magnitude']
    branch_colors = ['#1f4e79', '#0f6c5c', '#c96b00']
    sum_center = (0.82, 0.50)
    sum_radius = 0.052
    sum_circle = Circle(sum_center, sum_radius, facecolor='#f2efe6', edgecolor='#333333', lw=1.3)
    ax.add_patch(sum_circle)
    schematic_boxes.append({'id': 'sum', 'bbox': [sum_center[0] - sum_radius, sum_center[1] - sum_radius, sum_center[0] + sum_radius, sum_center[1] + sum_radius]})
    for i, (y, name, color) in enumerate(zip(branch_y, branch_names, branch_colors), start=1):
        dyn = FancyBboxPatch((0.22, y - 0.07), 0.18, 0.14, boxstyle='round,pad=0.010,rounding_size=0.010', facecolor='#eaf2f8', edgecolor=color, lw=1.4)
        nonlin = FancyBboxPatch((0.48, y - 0.07), 0.18, 0.14, boxstyle='round,pad=0.010,rounding_size=0.010', facecolor='#fff4e6', edgecolor=color, lw=1.4)
        ax.add_patch(dyn)
        ax.add_patch(nonlin)
        schematic_boxes.append({'id': f'h{i}', 'bbox': [0.22, y - 0.07, 0.40, y + 0.07]})
        schematic_boxes.append({'id': f'f{i}', 'bbox': [0.48, y - 0.07, 0.66, y + 0.07]})
        split_to_h_points, split_to_h_raw = _short_arrow_payload(
            f'split_to_h{i}',
            [split_point, (0.22, y)],
            target=f'h{i}',
            require_axis_aligned=(abs(y - split_point[1]) < 1e-9),
        )
        ax.annotate('', xy=split_to_h_points[-1], xytext=split_to_h_points[0], arrowprops=dict(arrowstyle='->', lw=branch_arrow_lw, color='#666666', shrinkA=0, shrinkB=0))
        schematic_arrows.append(split_to_h_raw)
        ax.text(0.31, y + 0.025, f'h{i}(s)', ha='center', va='center', fontsize=label_fs, weight='bold', color=color)
        ax.text(0.31, y - 0.030, 'local IIR\ndynamics', ha='center', va='center', fontsize=subtitle_fs)
        h_to_f_points, h_to_f_raw = _short_arrow_payload(
            f'h{i}_to_f{i}',
            [(0.40, y), (0.48, y)],
            source=f'h{i}',
            target=f'f{i}',
            require_axis_aligned=True,
        )
        ax.annotate('', xy=h_to_f_points[-1], xytext=h_to_f_points[0], arrowprops=dict(arrowstyle='->', lw=h_to_f_arrow_lw, color=color, shrinkA=0, shrinkB=0))
        schematic_arrows.append(h_to_f_raw)
        ax.text(0.57, y + 0.025, f'f{i}(.)', ha='center', va='center', fontsize=label_fs, weight='bold', color=color)
        ax.text(0.57, y - 0.030, name, ha='center', va='center', fontsize=subtitle_fs)
        sum_target_y = 0.50 + (y - 0.50) * 0.10
        f_to_sum_points, f_to_sum_raw = _short_arrow_payload(
            f'f{i}_to_sum',
            [(0.66, y), (sum_center[0] - sum_radius - 0.010, sum_target_y)],
            source=f'f{i}',
            target='sum',
        )
        ax.annotate('', xy=f_to_sum_points[-1], xytext=f_to_sum_points[0], arrowprops=dict(arrowstyle='->', lw=f_to_sum_arrow_lw, color=color, shrinkA=0, shrinkB=0))
        schematic_arrows.append(f_to_sum_raw)
    ax.text(sum_center[0], sum_center[1], r'$\Sigma$', ha='center', va='center', fontsize=16, weight='bold')
    sum_to_output_points, sum_to_output_raw = _short_arrow_payload(
        'sum_to_output',
        [(sum_center[0] + sum_radius + 0.006, 0.50), (output_x - 0.03, 0.50)],
        source='sum',
        require_axis_aligned=True,
    )
    ax.annotate('', xy=sum_to_output_points[-1], xytext=sum_to_output_points[0], arrowprops=dict(arrowstyle='->', lw=input_arrow_lw, color='#333333', shrinkA=0, shrinkB=0))
    schematic_arrows.append(sum_to_output_raw)
    ax.text(output_x, 0.50, output_text, ha='center', va='center', fontsize=label_fs, weight='bold')
    raw_payload = {
        'source': 'R14 parallel Wiener equivalent structure',
        'branches': branch_names,
        'modification_scope': 'shortened all arrows to two-thirds of their original connector lengths and replaced the merge bus with three direct convergence arrows into the summation node',
        VISUAL_AUDIT_KEY: audit_schematic_geometry(
            schematic_boxes,
            schematic_arrows,
            context='parallel Wiener principle schematic geometry',
        ),
    }
    panel_name = 'fig_22_parallel_wiener_equivalent_montage_a_principle.png'
    panel_rel = save_panel_figure(
        fig,
        panel_name,
        dpi=300,
        pad_inches=pad_inches,
        margin_left=margin_left,
        margin_right=margin_right,
        margin_top=margin_top,
        margin_bottom=margin_bottom,
        raw_payload=raw_payload,
    )
    root_png = FIGURES_DIR / 'fig_14_parallel_wiener_principle.png'
    root_raw = root_png.with_suffix('.raw.json')
    panel_png = FIGURES_DIR / panel_rel
    panel_raw = panel_png.with_suffix('.raw.json')
    shutil.copy2(panel_png, root_png)
    shutil.copy2(panel_raw, root_raw)
    return root_png.name

def load_wiener_parallel_summary() -> Dict[str, Any]:
    summary_path = WIENER_PARALLEL_DIR / 'data' / 'wiener_parallel_modeling_summary.json'
    if not summary_path.exists():
        raise FileNotFoundError(f'Missing Wiener parallel modeling summary: {summary_path}')
    return load_json(summary_path)


def copy_wiener_parallel_figures() -> Dict[str, str]:
    image_dir = WIENER_PARALLEL_DIR / 'image'
    parent_cfg = get_figure_config('fig_22_parallel_wiener_equivalent_montage')
    parent_response_cfg = parent_cfg.get('response_panel') or {}
    copied: Dict[str, str] = {}
    for key, stem in {'parallel_wiener_branch_weights': '14.NN_extern_simu_reproduced_fh_kx'}.items():
        src_png = image_dir / f'{stem}.png'
        src_json = image_dir / f'{stem}.json'
        if not src_png.exists():
            raise FileNotFoundError(f'Missing Wiener parallel figure: {src_png}')
        dst_png = FIGURES_DIR / f'fig_14_{key}.png'
        dst_png.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_png, dst_png)
        copied[key] = dst_png.name
        raw_payload: Dict[str, Any] = {
            'source': 'parallel Wiener modeling output',
            'summary': 'parallel Wiener modeling summary',
        }
        if src_json.exists():
            raw_payload['source_json'] = src_json.name
            raw_payload['data'] = load_json(src_json)
        save_json(dst_png.with_suffix('.raw.json'), raw_payload)
    analysis = load_json(str((image_dir / '14.NN_extern_simu_reproduced_analysis.json').relative_to(ROOT)).replace('\\', '/'))

    def plot_response_panel(
        name: str,
        title: str,
        y_label: str,
        sim_key: str,
        measured_key: str,
        *,
        figure_key: str,
    ) -> str:
        cfg = get_figure_config(figure_key)
        response_cfg = cfg.get('response_panel') if isinstance(cfg.get('response_panel'), dict) else cfg
        response_cfg = _deep_merge(parent_response_cfg, response_cfg) if response_cfg else parent_response_cfg
        xy_cfg = response_cfg.get('xy_plot') if isinstance(response_cfg.get('xy_plot'), dict) else {}
        legend_cfg = response_cfg.get('legend') if isinstance(response_cfg.get('legend'), dict) else {}
        fig, ax = plt.subplots(
            figsize=_as_float_tuple(response_cfg.get('figsize'), (5.8, 4.2)),
            constrained_layout=True,
        )
        ax.plot(
            analysis['amplitudes'],
            analysis[sim_key],
            color='#1f77b4',
            marker='o',
            linewidth=float(response_cfg.get('line_width', 2.0)),
            label='Wiener simu',
        )
        ax.plot(
            analysis['fitted_magnitudes'],
            analysis[measured_key],
            color='#ff7f50',
            marker='s',
            linewidth=float(response_cfg.get('line_width', 2.0)),
            label='Measured',
        )
        ax.set_xscale('log')
        ax.set_xlabel('Magnitude (m/s^2)', fontsize=float(xy_cfg.get('label_fontsize', 10)), labelpad=float(xy_cfg.get('labelpad', 4)))
        ax.set_ylabel(y_label, fontsize=float(xy_cfg.get('label_fontsize', 10)), labelpad=float(xy_cfg.get('labelpad', 4)))
        if 'xlim' in xy_cfg:
            ax.set_xlim(*_as_float_tuple(xy_cfg.get('xlim'), ax.get_xlim()))
        if 'ylim' in xy_cfg:
            ax.set_ylim(*_as_float_tuple(xy_cfg.get('ylim'), ax.get_ylim()))
        ax.tick_params(axis='both', which='major', labelsize=float(xy_cfg.get('tick_fontsize', 9)), pad=float(xy_cfg.get('tick_pad', 3)))
        ax.grid(True, which='both', linestyle='--', alpha=float(response_cfg.get('grid_alpha', 0.35)))
        ax.legend(
            frameon=bool(legend_cfg.get('frameon', response_cfg.get('legend_frameon', True))),
            loc=str(legend_cfg.get('loc', response_cfg.get('legend_loc', 'upper left'))),
            fontsize=float(legend_cfg.get('fontsize', response_cfg.get('legend_fontsize', 8.5))),
            ncol=int(legend_cfg.get('ncol', response_cfg.get('legend_ncol', 1))),
        )
        out = FIGURES_DIR / name
        return _save_matplotlib_figure(
            fig,
            out,
            raw_payload={
                'source': 'ex_projects/compare/wiener_parallel_modeling/image/14.NN_extern_simu_reproduced_analysis.json',
                'target_source': analysis.get('target_source'),
                'x': 'amplitudes',
                'y': [sim_key, measured_key],
            },
            bbox_inches='tight',
        )

    copied['parallel_wiener_center_frequency'] = plot_response_panel(
        'fig_14_parallel_wiener_center_frequency.png',
        'Center frequency vs magnitude',
        'Center frequency (Hz)',
        'center_freqs',
        'fitted_center_freqs',
        figure_key='fig_14_parallel_wiener_center_frequency',
    )
    copied['parallel_wiener_gain_100hz'] = plot_response_panel(
        'fig_14_parallel_wiener_gain_100hz.png',
        'Gain at 100 Hz vs magnitude',
        'Gain at 100 Hz',
        'gain_at_100',
        'fitted_gain_at_100',
        figure_key='fig_14_parallel_wiener_gain_100hz',
    )
    return copied


def make_bitmap_montage(
    output_name: str,
    panel_specs: List[Dict[str, Any]],
    *,
    layout: str,
    rows: int | None = None,
    cols: int | None = None,
    padding: int | List[int] = 72,
    gutter: int | tuple[int, int] = 72,
    label_font_size: int = 58,
    label_box: bool = False,
    cell_widths: List[int] | None = None,
    cell_heights: List[int] | None = None,
    note: str,
    latex_width_fraction: float = 1.0,
    label_font_size_pt: float = SUBFIGURE_LABEL_TARGET_PT,
    figure_key: str | None = None,
) -> str:
    if figure_key:
        cfg = get_figure_config(figure_key)
        panel_specs = _merge_panel_specs(panel_specs, cfg.get('panels'))
        montage_cfg = cfg.get('montage') or {}
        layout = str(montage_cfg.get('layout', layout))
        rows = int(montage_cfg['rows']) if montage_cfg.get('rows') is not None else rows
        cols = int(montage_cfg['cols']) if montage_cfg.get('cols') is not None else cols
        padding = _as_int_spacing(montage_cfg.get('padding'), padding)
        gutter = _as_int_spacing(montage_cfg.get('gutter'), gutter)
        label_font_size = int(montage_cfg.get('label_font_size', label_font_size))
        label_font_size_pt = float(montage_cfg.get('label_font_size_pt', label_font_size_pt))
        latex_width_fraction = float(montage_cfg.get('latex_width_fraction', latex_width_fraction))
        cell_widths = _as_int_list(montage_cfg.get('cell_widths'), cell_widths)
        cell_heights = _as_int_list(montage_cfg.get('cell_heights'), cell_heights)
    panels = [
        PanelSpec(
            path=FIGURES_DIR / str(spec['source']),
            label=spec.get('label'),
            scale=float(spec.get('scale', 1.0)),
            fit_width=spec.get('fit_width'),
            fit_height=spec.get('fit_height'),
            align_x=str(spec.get('align_x', 'center')),
            align_y=str(spec.get('align_y', 'center')),
            offset_x=int(spec.get('offset_x', 0)),
            offset_y=int(spec.get('offset_y', 0)),
            row_span=int(spec.get('row_span', 1)),
            col_span=int(spec.get('col_span', 1)),
            trim_border=spec.get('trim_border'),
            trim_border_left=spec.get('trim_border_left'),
            trim_border_right=spec.get('trim_border_right'),
            trim_border_top=spec.get('trim_border_top'),
            trim_border_bottom=spec.get('trim_border_bottom'),
            trim_tolerance=int(spec.get('trim_tolerance', 8)),
        )
        for spec in panel_specs
    ]
    out = FIGURES_DIR / output_name
    metadata = compose_subfigures(
        panels,
        out,
        layout=layout,
        rows=rows,
        cols=cols,
        padding=padding,
        gutter=gutter,
        cell_widths=cell_widths,
        cell_heights=cell_heights,
        label_font_size=label_font_size,
        label_font_size_pt=label_font_size_pt,
        label_reference_width_pt=SN_A4_TEXT_WIDTH_PT,
        latex_width_fraction=latex_width_fraction,
        label_position='outside-top-left',
        label_inset=24,
        label_gap=24,
        label_box=label_box,
        label_box_padding=10,
        dpi=(500, 500),
    )
    visual_audit = combine_audits(
        audit_montage_layout(metadata, context=output_name),
        audit_image_file(out, context=output_name),
        context=output_name,
    )
    save_json(out.with_suffix('.raw.json'), {
        'source_trace': 'bitmap subplot montage generated by src/visualization/subfigure_montage.py',
        'source_figures': [str(spec['source']) for spec in panel_specs],
        'modification_scope': note,
        'montage': metadata,
        VISUAL_AUDIT_KEY: visual_audit,
    })
    return out.name


def make_paper_bitmap_montages() -> Dict[str, str]:
    montages: Dict[str, str] = {}
    make_met_structure_figure()
    make_readout_circuit_figure()
    montages['met_structure_readout'] = make_bitmap_montage(
        'fig_20_met_structure_readout_montage.png',
        [
            {'source': 'met_structure.png', 'label': '(a)', 'fit_width': 2500, 'align_y': 'top', 'trim_border': 28},
            {'source': 'readout_circuit.png', 'label': '(b)', 'fit_width': 2500, 'align_y': 'top', 'trim_border': 28},
        ],
        layout='horizontal',
        padding=[80, 70, 80, 70],
        gutter=(140, 80),
        label_font_size=66,
        note='Combines the MET structural schematic and the readout circuit into one labeled two-panel figure.',
        figure_key='fig_20_met_structure_readout_montage',
    )
    make_calibration_table_test_figure()
    make_dataset_preprocessing_workflow_figure()
    montages['experimental_setup_dataset_workflow'] = make_bitmap_montage(
        'fig_21_experimental_setup_dataset_workflow_montage.png',
        [
            {'source': 'calibration_table_test.png', 'label': '(a)', 'fit_width': 3600, 'align_x': 'center', 'align_y': 'center', 'trim_border': 90},
            {'source': 'fig_19_dataset_preprocessing_workflow.png', 'label': '(b)', 'fit_height': 2700, 'align_x': 'center', 'align_y': 'top', 'trim_border': 90},
        ],
        layout='horizontal',
        padding=[90, 80, 90, 80],
        gutter=(110, 90),
        label_font_size=64,
        note='Places the experimental setup photograph and vertical illustrated dataset construction workflow side by side.',
        figure_key='fig_21_experimental_setup_dataset_workflow_montage',
    )
    montages['parallel_wiener_response_row'] = make_bitmap_montage(
        'fig_22_parallel_wiener_response_row.png',
        [
            {'source': 'fig_14_parallel_wiener_center_frequency.png', 'label': '(b)', 'fit_width': 1800, 'align_y': 'top', 'trim_border': 40},
            {'source': 'fig_14_parallel_wiener_gain_100hz.png', 'label': '(c)', 'fit_width': 1800, 'align_y': 'top', 'trim_border': 40},
        ],
        layout='horizontal',
        padding=[50, 45, 50, 45],
        gutter=(75, 60),
        label_font_size=50,
        note='Composes the two response-trajectory plots as the second row of the parallel Wiener equivalent figure.',
        figure_key='fig_22_parallel_wiener_response_row',
    )
    montages['parallel_wiener_equivalent'] = make_bitmap_montage(
        'fig_22_parallel_wiener_equivalent_montage.png',
        [
            {'source': panel_source_name('fig_22_parallel_wiener_equivalent_montage_a_principle.png'), 'label': '(a)', 'fit_width': 3600, 'align_x': 'center', 'trim_border': 140},
            {'source': 'fig_22_parallel_wiener_response_row.png', 'label': None, 'fit_width': 3600, 'align_x': 'center', 'trim_border': 0},
        ],
        layout='vertical',
        padding=[90, 80, 90, 80],
        gutter=(90, 105),
        label_font_size=68,
        note='Composes the parallel Wiener principle as the first row and the two response plots as the second row.',
        figure_key='fig_22_parallel_wiener_equivalent_montage',
    )
    make_kan_neuron_compensation_figure()
    montages['kan_neuron_compensation'] = make_bitmap_montage(
        'fig_23_kan_neuron_compensation_montage.png',
        [
            {'source': 'kan_neuron_compensation.png', 'fit_width': 3156, 'align_x': 'center'},
        ],
        layout='matrix',
        rows=1,
        cols=1,
        padding=0,
        gutter=0,
        label_font_size=54,
        note='Normalizes the traced single KAN-neuron compensation bitmap through the same montage module.',
        figure_key='fig_23_kan_neuron_compensation_montage',
    )
    return montages


def metric_value_macros(row: Dict[str, Any]) -> Dict[str, str]:
    ram_bytes = row.get('ram_bytes')
    return {
        'FreqDrift': _fmt_float(row['freq_drift_hz'], 2),
        'SensDrift': _fmt_float(row['sens_drift_percent'], 2),
        'Linearity': _fmt_float(row['linearity_percent'], 3),
        'KeilFps': format_optional(row.get('board_keil_fps'), '{:.1f}'),
        'KeilRamKB': format_optional(ram_bytes / 1024.0 if ram_bytes is not None else None, '{:.1f}'),
        'Params': f"{int(row['total_params']):,}",
    }


def load_project_config_from_metrics(row: Dict[str, Any]) -> Dict[str, Any]:
    metrics_path = ROOT / str(row['metrics_path'])
    project_dir = metrics_path.parents[1]
    config_path = project_dir / 'config.json'
    if not config_path.exists():
        return {}
    return json.loads(config_path.read_text(encoding='utf-8'))


def curve_best_epoch(curve: Dict[str, Any]) -> str:
    values = list(curve['val_loss'])
    epochs = list(curve['epochs'])
    best_index = int(np.argmin(np.asarray(values, dtype=float)))
    return str(epochs[best_index])


def _fmt_float(value: Any, digits: int = 2) -> str:
    return f"{float(value):.{digits}f}"


def _hparam_axis_values(summary: Dict[str, Any], axis: str) -> str:
    vals = sorted({int(row['value']) for row in summary.get('rows', []) if row.get('axis') == axis and row.get('value') is not None})
    return ', '.join(str(v) for v in vals)


def _hparam_best_text(summary: Dict[str, Any], axis: str, key: str, unit: str, digits: int = 2) -> str:
    rows = [row for row in summary.get('rows', []) if row.get('axis') == axis and row.get('status') == 'complete' and row.get(key) is not None]
    if not rows:
        return '-'
    best = min(rows, key=lambda row: float(row[key]))
    return f"{best['value']} ({_fmt_float(best[key], digits)}{unit})"


def build_value_overrides(payload: Dict[str, Any]) -> Dict[str, str]:
    origin = payload['origin_metrics']
    wiener_parallel = payload.get('wiener_parallel_modeling', {})
    wp_cf = wiener_parallel.get('center_frequency', {})
    wp_gain = wiener_parallel.get('gain_at_target_frequency', {})

    overrides: Dict[str, str] = {
        'valDatasetFreqRange': '10--200~Hz sampled grid; evaluation band $\\leq 128$~Hz',
        'valDatasetMagnitudeRange': '0.24--6.0 m/s2',
        'valDatasetPreprocess': 'steady-state clipping, two-window slicing, and normalization to [-1, 1]',
        'valDatasetScenarioMapping': 'frequency--magnitude matrix with paired measured and ideal waveforms',
        'valDatasetSplit': r'50\%/50\% training/validation split',
        'valDatasetTotalRecords': f"{int((payload['main_benchmark'][0].get('linearity_full_frequency_count') or 0) * (len((payload.get('trajectories') or {}).get('Origin', {}).get('magnitudes', [])) or 25))} frequency--magnitude operating points",
        'valTargetCurveSource': 'ideal second-order response fitted from the low-magnitude calibration sweep',
        'valOpenDataPackage': 'processed response matrix and plotting scripts are available with the manuscript materials',
        'valOpenCodePackage': 'analysis and plotting code are available with the manuscript materials',
        'valWienerParallelAmpCount': str(wiener_parallel.get('amplitude_count', 25)),
        'valWienerParallelCfMae': f"{float(wp_cf.get('mae_hz', 1.8713121031247149)):.2f}",
        'valWienerParallelCfRmse': f"{float(wp_cf.get('rmse_hz', 2.3355837762199854)):.2f}",
        'valWienerParallelGainFreq': f"{float(wp_gain.get('frequency_hz', 100.0)):.0f}",
        'valWienerParallelGainMae': f"{float(wp_gain.get('mae', 4.532628218217732)):.2f}",
        'valWienerParallelGainRmse': f"{float(wp_gain.get('rmse', 5.530740547399083)):.2f}",
        'valExternalSensorPlan': 'repeat the frequency--magnitude matrix on a second MET sample',
        'valExternalExcitationPlan': 'repeat the protocol on an independent shaker table',
        'valAblationOverviewRowCount': str(len(payload.get('ablation_overview', []))),
    }

    main_map = {row['label']: row for row in payload['main_benchmark']}
    main_prefix = {
        '1DCNN': 'valMainCNN',
        'TCN': 'valMainTCN',
        'RNN': 'valMainRNN',
        'GRU': 'valMainGRU',
        'LSTM': 'valMainLSTM',
        'LSTMTransformer': 'valMainLSTMTransformer',
        'Wiener-KAN': 'valMainWienerKAN',
    }
    for label, prefix in main_prefix.items():
        if label in main_map:
            row = main_map[label]
            for suffix, value in metric_value_macros(row).items():
                overrides[prefix + suffix] = value

    primary = main_map.get('Wiener-KAN') or next(iter(main_map.values()))
    primary_config = load_project_config_from_metrics(primary)
    sample_rate = float(primary_config.get('sample_rate', 2000))
    clipped_s = float(primary_config.get('time_clipped_s', 4.0))
    points_per_record = int(primary_config.get('use_points') or round(sample_rate * clipped_s))
    window_points = points_per_record
    magnitude_count = len((payload.get('trajectories') or {}).get('Origin', {}).get('magnitudes', [])) or int(primary.get('magnitude_count', 25))
    frequency_count = int(primary.get('linearity_full_frequency_count') or primary.get('linearity_band_count') or 0)
    operating_points = frequency_count * magnitude_count
    window_records = operating_points
    train_records = window_records // 2
    val_records = window_records - train_records
    primary_values = metric_value_macros(primary)
    overrides.update({
        'valPrimaryProject': 'FRIKANh8u6l6\\_e1k\\_lr7e4',
        'valPrimaryFreqDrift': primary_values['FreqDrift'],
        'valPrimarySensDrift': primary_values['SensDrift'],
        'valPrimaryLinearity': primary_values['Linearity'],
        'valPrimaryKeilFps': primary_values['KeilFps'],
        'valPrimaryKeilRamKB': primary_values['KeilRamKB'],
        'valPrimaryParams': primary_values['Params'],
        'valFreqScanPoints': str(frequency_count),
        'valMagScanPoints': str(magnitude_count),
        'valDatasetOperatingPoints': str(operating_points),
        'valDatasetPointsPerRecord': str(points_per_record),
        'valDatasetWindowPoints': str(window_points),
        'valDatasetWindowRecords': str(window_records),
        'valDatasetTrainRecords': str(train_records),
        'valDatasetValRecords': str(val_records),
        'valDatasetSplitUnit': 'frequency--magnitude operating points after steady-state clipping',
        'valEpochs': str(int(primary_config.get('epoch_train', primary.get('epochs', 1000)))),
        'valInitLR': f"{float(primary_config.get('learning_rate', primary.get('lr', 0.0007))):.4g}",
        'valLearningRateSchedule': 'fixed learning rate',
    })
    overrides.update({
        'valMainWienerParams': '-',
        'valMainWienerFreqDrift': _fmt_float(origin['freq'], 2),
        'valMainWienerSensDrift': _fmt_float(origin['sens'], 2),
        'valMainWienerLinearity': _fmt_float(origin['linearity'], 3),
    })

    loss_map = {row['label']: row for row in payload['loss_ablation']}
    loss_curve_map = {row['label']: row for row in payload['loss_convergence_curves']}
    for label, prefix in [('MAE', 'valLossMAE'), ('AFMAE', 'valLossAFMAE'), ('MAE+AFMAE', 'valLossJoint')]:
        if label in loss_map:
            row = loss_map[label]
            for suffix, value in metric_value_macros(row).items():
                overrides[prefix + suffix] = value
        if label in loss_curve_map:
            overrides[prefix + 'Epoch'] = curve_best_epoch(loss_curve_map[label])

    structure_map = {row['label']: row for row in payload['structure_ablation']}
    constraint_sources = {
        'valConFull': 'Wiener-KAN',
        'valConUncon': 'No symmetry',
        'valConOdd': 'No positive (stress)',
        'valConPos': 'CNN-KAN',
    }
    for prefix, label in constraint_sources.items():
        if label in structure_map:
            row = structure_map[label]
            for suffix, value in metric_value_macros(row).items():
                overrides[prefix + suffix] = value

    freq_sources = {
        'valFreqYesYes': 'Wiener-KAN',
        'valFreqNoYes': 'Random trainable IIR',
        'valFreqYesNo': 'Wiener-MLP',
        'valFreqNoNo': 'CNN-KAN',
    }
    for prefix, label in freq_sources.items():
        if label in structure_map:
            row = structure_map[label]
            for suffix, value in metric_value_macros(row).items():
                overrides[prefix + suffix] = value

    activation_sources = {
        'valActBSpline': 'Wiener-KAN',
        'valActReLU': 'CNN-KAN',
        'valActTanh': 'Wiener-MLP',
        'valActSigmoid': 'No symmetry',
    }
    missing_activation = [label for label in activation_sources.values() if label not in structure_map]
    if missing_activation:
        raise KeyError(f"Missing structure_ablation rows for activation macros: {', '.join(missing_activation)}")
    for prefix, label in activation_sources.items():
        row = structure_map[label]
        for suffix, value in metric_value_macros(row).items():
            overrides[prefix + suffix] = value

    iir_map = {row['label']: row for row in payload.get('wiener_frontend_ablation', [])}
    iir_sources = {
        'valIirBase': 'System prior, frozen',
        'valIirRandomFrozen': 'Random, frozen',
        'valIirSystemTrainable': 'System prior, trainable',
        'valIirRandomTrainable': 'Random, trainable',
    }
    missing_iir = [label for label in iir_sources.values() if label not in iir_map]
    if missing_iir:
        raise KeyError(f"Missing wiener_frontend_ablation rows for value macros: {', '.join(missing_iir)}")
    for prefix, label in iir_sources.items():
        row = iir_map[label]
        overrides[prefix + 'Epoch'] = str(int(row['epochs']))
        for suffix, value in metric_value_macros(row).items():
            overrides[prefix + suffix] = value

    deploy_map = {row['label']: row for row in payload['deployment']}
    deploy_sources = {'valDeployRaw': 'Wiener-KAN', 'valDeployGRU': 'GRU', 'valDeployLSTM': 'LSTM'}
    for prefix, label in deploy_sources.items():
        if label in deploy_map:
            row = deploy_map[label]
            overrides[prefix + 'Qemu'] = f"{float(row['board_qemu_mae']):.3e}"
            overrides[prefix + 'KeilFps'] = f"{float(row['board_keil_fps']):.1f}"
            overrides[prefix + 'Mae'] = f"{float(row['board_keil_mae']):.3e}"
            overrides[prefix + 'RamKB'] = format_optional(row.get('ram_bytes') / 1024.0 if row.get('ram_bytes') is not None else None, '{:.1f}')
    lut_map = {row['label']: row for row in payload['lut_variants']}
    lut = lut_map.get('LUT + interp') or payload['lut_variants'][0]
    overrides['valDeployLutQemu'] = f"{float(lut['qemu_mae']):.3e}"
    overrides['valDeployLutKeilFps'] = f"{float(lut['keil_fps']):.1f}"
    overrides['valDeployLutMae'] = f"{float(lut['keil_mae']):.3e}"
    overrides['valDeployLutRamKB'] = format_optional(lut.get('ram_bytes') / 1024.0 if lut.get('ram_bytes') is not None else None, '{:.1f}')
    lut_macro_sources = {
        'valDeployLutNearest': 'LUT nearest',
        'valDeployLutInterp': 'LUT + interp',
        'valDeployNoLut': 'No LUT exact',
    }
    for prefix, label in lut_macro_sources.items():
        if label not in lut_map:
            continue
        row = lut_map[label]
        overrides[prefix + 'Qemu'] = f"{float(row['qemu_mae']):.3e}"
        overrides[prefix + 'KeilFps'] = f"{float(row['keil_fps']):.1f}"
        overrides[prefix + 'Mae'] = f"{float(row['keil_mae']):.3e}"
        overrides[prefix + 'RamKB'] = format_optional(row.get('ram_bytes') / 1024.0 if row.get('ram_bytes') is not None else None, '{:.1f}')

    hparam = payload.get('hparam_sensitivity') or {}
    hp_base = hparam.get('baseline') or {}
    hp_axis_summary = hparam.get('axis_summary') or {}
    hp_complete_axes = [axis for axis, info in hp_axis_summary.items() if info.get('missing_count', 0) == 0]
    if hp_base:
        overrides.update({
            'valHpBaseFreq': _fmt_float(hp_base.get('freq_drift_hz', 0), 2),
            'valHpBaseSens': _fmt_float(hp_base.get('sens_drift_percent', 0), 2),
            'valHpBaseLinearity': _fmt_float(hp_base.get('linearity_percent', 0), 3),
        })
    overrides.update({
        'valHpCompleteAxes': ', '.join(hp_complete_axes) or '-',
        'valHpDominators': str(len(hparam.get('strict_dominators', []))),
        'valHpHSet': _hparam_axis_values(hparam, 'H_UNITS'), 'valHpHBase': '8',
        'valHpUSet': _hparam_axis_values(hparam, 'INNER_KAN_UNITS'), 'valHpUBase': '6',
        'valHpLSet': _hparam_axis_values(hparam, 'INNER_KAN_LAYERS'), 'valHpLBase': '6',
        'valHpGridSet': _hparam_axis_values(hparam, 'GRID_SIZE'), 'valHpOrderSet': _hparam_axis_values(hparam, 'SPLINE_ORDER'),
        'valHpGridOrderBase': '8/2',
        'valHpHBestFreq': _hparam_best_text(hparam, 'H_UNITS', 'freq_drift_hz', ' Hz', 2),
        'valHpHBestSens': _hparam_best_text(hparam, 'H_UNITS', 'sens_drift_percent', '\\%', 2),
        'valHpHBestLinearity': _hparam_best_text(hparam, 'H_UNITS', 'linearity_percent', '\\%', 3),
        'valHpUBestFreq': _hparam_best_text(hparam, 'INNER_KAN_UNITS', 'freq_drift_hz', ' Hz', 2),
        'valHpUBestSens': _hparam_best_text(hparam, 'INNER_KAN_UNITS', 'sens_drift_percent', '\\%', 2),
        'valHpUBestLinearity': _hparam_best_text(hparam, 'INNER_KAN_UNITS', 'linearity_percent', '\\%', 3),
        'valHpLBestFreq': _hparam_best_text(hparam, 'INNER_KAN_LAYERS', 'freq_drift_hz', ' Hz', 2),
        'valHpLBestSens': _hparam_best_text(hparam, 'INNER_KAN_LAYERS', 'sens_drift_percent', '\\%', 2),
        'valHpLBestLinearity': _hparam_best_text(hparam, 'INNER_KAN_LAYERS', 'linearity_percent', '\\%', 3),
        'valHpGridBestFreq': _hparam_best_text(hparam, 'GRID_SIZE', 'freq_drift_hz', ' Hz', 2),
        'valHpGridBestSens': _hparam_best_text(hparam, 'GRID_SIZE', 'sens_drift_percent', '\\%', 2),
        'valHpGridBestLinearity': _hparam_best_text(hparam, 'GRID_SIZE', 'linearity_percent', '\\%', 3),
        'valHpOrderBestFreq': _hparam_best_text(hparam, 'SPLINE_ORDER', 'freq_drift_hz', ' Hz', 2),
        'valHpOrderBestSens': _hparam_best_text(hparam, 'SPLINE_ORDER', 'sens_drift_percent', '\\%', 2),
        'valHpOrderBestLinearity': _hparam_best_text(hparam, 'SPLINE_ORDER', 'linearity_percent', '\\%', 3),
        'valHpHBestMetric': _hparam_best_text(hparam, 'H_UNITS', 'linearity_percent', '\\%', 3),
        'valHpUBestMetric': _hparam_best_text(hparam, 'INNER_KAN_UNITS', 'freq_drift_hz', ' Hz', 2),
        'valHpLBestMetric': _hparam_best_text(hparam, 'INNER_KAN_LAYERS', 'linearity_percent', '\\%', 3),
        'valHpGridOrderSet': f"grid={_hparam_axis_values(hparam, 'GRID_SIZE')}; order={_hparam_axis_values(hparam, 'SPLINE_ORDER')}",
        'valHpSplineBestMetric': _hparam_best_text(hparam, 'SPLINE_ORDER', 'freq_drift_hz', ' Hz', 2),
    })
    return {name: value for name, value in overrides.items() if not re.search(r'(IONS|SDS|NFDS)$', name)}


def write_values_tex(payload: Dict[str, Any]) -> None:
    values_path = LATEX_DIR / 'values.tex'
    text = values_path.read_text(encoding='utf-8')

    stale_macro_patterns = [
        re.compile(pattern)
        for pattern in [
            r'val.*(?:IONS|SDS|NFDS)$',
            'val.*' + 'Supp' + 'ression.*',
            'valFrikan' + 'Variant(?:Small|Medium|Large)$',
            r'val(?:GRU|Frikan|LSTM)(?:Small|Medium|Large)Params$',
            r'val(?:Frikan|LSTM)Latency.*',
            'valLatency' + 'PointCount$',
            r'val(?:Cosine|Restart)Period$',
            'valDeploy(?:Raw|GRU|LSTM|Lut)' + 'K' + 'eil$',
            r'valSpeedup$',
            r'val.*Cost.*',
        ]
    ]

    lines = [
        line for line in text.splitlines()
        if not (
            (match := re.match(r'\\newcommand\{\\(val[A-Za-z0-9]+)\}\{', line.strip()))
            and any(pattern.fullmatch(match.group(1)) for pattern in stale_macro_patterns)
        )
    ]
    text = '\n'.join(lines) + '\n'
    overrides = build_value_overrides(payload)
    for name, value in overrides.items():
        pattern = re.compile(rf"\\(?:newcommand|providecommand)\{{\\{name}\}}\{{[^}}]*\}}")
        replacement = f"\\newcommand{{\\{name}}}{{{value}}}"
        if pattern.search(text):
            text = pattern.sub(lambda _match, repl=replacement: repl, text)
        else:
            text += f"\n\\newcommand{{\\{name}}}{{{value}}}\n"
    text = re.sub(r'\{TBD\}', '{N/A}', text)
    values_path.write_text(text, encoding='utf-8')
    save_json(DATA_DIR / 'values_raw.json', overrides)


def create_additional_paper_figures(payload: Dict[str, Any]) -> Dict[str, str]:
    origin = payload['origin_metrics']
    trajectories = payload['trajectories']
    main_rows = payload['main_benchmark']
    structure_rows = payload['structure_ablation']
    main_curves = payload['main_convergence_curves']
    loss_curves = payload['loss_convergence_curves']

    generated: Dict[str, str] = {}

    freq_cfg = get_figure_config('fig_08_frequency_response_comparison')
    fn_panel_cfg = freq_cfg.get('fn_panel') or {}
    fig_fn, ax_fn = plt.subplots(
        figsize=_as_float_tuple(fn_panel_cfg.get('figsize'), (5.6, 2.67)),
        constrained_layout=True,
    )
    for label, series in trajectories.items():
        linestyle = '--' if label == 'Origin' else '-'
        ax_fn.plot(series['magnitudes'], series['natural_frequency_hz'], linestyle, label=label, linewidth=float(fn_panel_cfg.get('line_width', 2.2)))
    ax_fn.set_xlabel(r'Magnitude (m/s$^2$)')
    ax_fn.set_ylabel('Natural frequency (Hz)')
    ax_fn.legend(
        loc=str(fn_panel_cfg.get('legend_loc', 'best')),
        frameon=bool(fn_panel_cfg.get('legend_frameon', True)),
        fontsize=float(fn_panel_cfg.get('legend_fontsize', plt.rcParams.get('legend.fontsize', 8.5))),
    )
    panel_fn = save_panel_figure(fig_fn, 'fig_08_frequency_response_comparison_a_fn.png')

    sens_panel_cfg = freq_cfg.get('sensitivity_panel') or {}
    fig_sens, ax_sens = plt.subplots(
        figsize=_as_float_tuple(sens_panel_cfg.get('figsize'), (5.6, 2.67)),
        constrained_layout=True,
    )
    for label, series in trajectories.items():
        linestyle = '--' if label == 'Origin' else '-'
        ax_sens.plot(series['magnitudes'], series['sensitivity_100hz'], linestyle, label=label, linewidth=float(sens_panel_cfg.get('line_width', 2.2)))
    ax_sens.set_xlabel(r'Magnitude (m/s$^2$)')
    ax_sens.set_ylabel('Sensitivity at 100 Hz')
    ax_sens.legend(
        loc=str(sens_panel_cfg.get('legend_loc', 'best')),
        frameon=bool(sens_panel_cfg.get('legend_frameon', True)),
        fontsize=float(sens_panel_cfg.get('legend_fontsize', plt.rcParams.get('legend.fontsize', 8.5))),
    )
    panel_sens = save_panel_figure(fig_sens, 'fig_08_frequency_response_comparison_b_sensitivity.png')

    wk = next(row for row in main_rows if row['label'] == 'Wiener-KAN')
    reduction_cfg = freq_cfg.get('reduction_panel') or {}
    fig_reduction, ax_reduction = plt.subplots(
        figsize=_as_float_tuple(reduction_cfg.get('figsize'), (5.8, 4.4)),
        constrained_layout=True,
    )
    metric_groups = ['Freq drift\n(Hz)', 'Sens drift\n(%)']
    x = np.arange(len(metric_groups), dtype=float)
    width = 0.34
    origin_values = [origin['freq'], origin['sens']]
    wk_values = [wk['freq_drift_hz'], wk['sens_drift_percent']]
    bars_origin = ax_reduction.bar(x - width / 2, origin_values, width=width, color='#555555', label='Origin')
    bars_wk = ax_reduction.bar(x + width / 2, wk_values, width=width, color='#0f6c5c', label='Wiener-KAN')
    ax_reduction.set_ylabel('Metric value')
    ax_reduction.set_xticks(x, metric_groups)
    ax_reduction.set_ylim(0, max(origin_values + wk_values) * 1.18)
    ax_reduction.grid(True, axis='y', alpha=0.22)
    ax_reduction.legend(
        frameon=bool(reduction_cfg.get('legend_frameon', True)),
        loc=str(reduction_cfg.get('legend_loc', 'upper right')),
        fontsize=float(reduction_cfg.get('legend_fontsize', 8.0)),
    )
    for bars in (bars_origin, bars_wk):
        for bar in bars:
            value = float(bar.get_height())
            ax_reduction.text(
                bar.get_x() + bar.get_width() / 2,
                value + max(origin_values + wk_values) * 0.028,
                f'{value:.2f}',
                ha='center',
                va='bottom',
                fontsize=float(reduction_cfg.get('annotation_fontsize', 7.8)),
                color='#222222',
            )
    panel_reduction = save_panel_figure(fig_reduction, 'fig_08_frequency_response_comparison_c_drift_reduction.png')

    response_cfg = freq_cfg.get('response_panel') or {}
    response_path = str(response_cfg.get('linear_response_path') or TRAJECTORY_MODELS[0][1])
    response_payload = load_json(response_path)
    response_freqs = np.array(response_payload['frequencies'], dtype=float)
    response_mags = np.array(response_payload['magnitudes'], dtype=float)
    response_origin = [np.array(row, dtype=float) for row in response_payload['gains_origin']]
    response_comped = [np.array(row, dtype=float) for row in response_payload['gains_comped']]
    fig_response, ax_response = plt.subplots(figsize=_as_float_tuple(response_cfg.get('figsize'), (5.35, 5.35)))
    curve_mode = str(response_cfg.get('curve_mode', 'selected_magnitudes'))
    if curve_mode == 'all_magnitudes_dual_legend':
        selected_indices = list(range(len(response_mags)))
        cmap = plt.cm.get_cmap(str(response_cfg.get('colormap', 'tab20')), len(selected_indices))
        origin_handles: List[Line2D] = []
        comped_handles: List[Line2D] = []
        magnitude_labels: List[str] = []
        for color_idx, mag_idx in enumerate(selected_indices):
            color = cmap(color_idx)
            origin_handle, = ax_response.loglog(
                response_freqs,
                response_origin[mag_idx],
                linestyle=str(response_cfg.get('origin_linestyle', '-')),
                color=color,
                lw=float(response_cfg.get('origin_linewidth', 1.5)),
                alpha=float(response_cfg.get('origin_alpha', 0.95)),
            )
            comped_handle, = ax_response.loglog(
                response_freqs,
                response_comped[mag_idx],
                linestyle=str(response_cfg.get('comped_linestyle', '--')),
                color=color,
                lw=float(response_cfg.get('comped_linewidth', 1.5)),
                alpha=float(response_cfg.get('comped_alpha', 0.95)),
            )
            origin_handles.append(origin_handle)
            comped_handles.append(comped_handle)
            magnitude_labels.append(rf'@ {response_mags[mag_idx]:.2f} m/s$^2$')
        origin_anchor = _as_float_tuple(response_cfg.get('origin_legend_bbox_to_anchor'), (1.02, 1.0))
        compensated_anchor = _as_float_tuple(response_cfg.get('compensated_legend_bbox_to_anchor'), (1.38, 1.0))
        if response_cfg.get('legend_column_gap') is not None:
            compensated_anchor = (origin_anchor[0] + float(response_cfg.get('legend_column_gap', 0.36)), compensated_anchor[1])
        origin_legend = ax_response.legend(
            origin_handles,
            magnitude_labels,
            title=str(response_cfg.get('origin_legend_title', 'ORIGIN')),
            loc=str(response_cfg.get('origin_legend_loc', 'upper left')),
            bbox_to_anchor=origin_anchor,
            frameon=bool(response_cfg.get('origin_legend_frameon', False)),
            fontsize=float(response_cfg.get('origin_legend_fontsize', response_cfg.get('legend_fontsize', 7.1))),
            title_fontsize=float(response_cfg.get('origin_legend_title_fontsize', response_cfg.get('legend_title_fontsize', 8.5))),
            ncol=int(response_cfg.get('origin_legend_ncol', 1)),
            borderaxespad=float(response_cfg.get('legend_borderaxespad', 0.0)),
            handlelength=float(response_cfg.get('legend_handlelength', 2.0)),
            labelspacing=float(response_cfg.get('legend_labelspacing', 0.42)),
        )
        ax_response.add_artist(origin_legend)
        ax_response.legend(
            comped_handles,
            magnitude_labels,
            title=str(response_cfg.get('compensated_legend_title', 'Compensated')),
            loc=str(response_cfg.get('compensated_legend_loc', 'upper left')),
            bbox_to_anchor=compensated_anchor,
            frameon=bool(response_cfg.get('compensated_legend_frameon', False)),
            fontsize=float(response_cfg.get('compensated_legend_fontsize', response_cfg.get('legend_fontsize', 7.1))),
            title_fontsize=float(response_cfg.get('compensated_legend_title_fontsize', response_cfg.get('legend_title_fontsize', 8.5))),
            ncol=int(response_cfg.get('compensated_legend_ncol', 1)),
            borderaxespad=float(response_cfg.get('legend_borderaxespad', 0.0)),
            handlelength=float(response_cfg.get('legend_handlelength', 2.0)),
            labelspacing=float(response_cfg.get('legend_labelspacing', 0.42)),
        )
    else:
        selected_indices = np.linspace(0, len(response_mags) - 1, 5, dtype=int).tolist()
        cmap = plt.cm.get_cmap('viridis', len(selected_indices) + 2)
        magnitude_handles: List[Line2D] = []
        magnitude_labels: List[str] = []
        for color_idx, mag_idx in enumerate(selected_indices):
            color = cmap(color_idx + 1)
            ax_response.loglog(response_freqs, response_origin[mag_idx], linestyle='--', color=color, lw=float(response_cfg.get('origin_linewidth', 1.5)), alpha=float(response_cfg.get('origin_alpha', 0.72)))
            handle, = ax_response.loglog(response_freqs, response_comped[mag_idx], linestyle='-', color=color, lw=float(response_cfg.get('comped_linewidth', 1.85)))
            magnitude_handles.append(handle)
            magnitude_labels.append(rf'{response_mags[mag_idx]:.2f} m/s$^2$')
        style_handles = [
            Line2D([0], [0], color='#333333', lw=1.6, linestyle='--', label='Origin'),
            Line2D([0], [0], color='#333333', lw=1.8, linestyle='-', label='Wiener-KAN'),
        ]
        first_legend = ax_response.legend(
            magnitude_handles,
            magnitude_labels,
            loc=str(response_cfg.get('magnitude_legend_loc', 'center left')),
            bbox_to_anchor=tuple(response_cfg.get('magnitude_legend_bbox_to_anchor', [1.02, 0.55])),
            frameon=bool(response_cfg.get('magnitude_legend_frameon', False)),
            fontsize=float(response_cfg.get('magnitude_legend_fontsize', 7.1)),
            ncol=int(response_cfg.get('magnitude_legend_ncol', 1)),
            borderaxespad=0.0,
            handlelength=2.0,
        )
        ax_response.add_artist(first_legend)
        ax_response.legend(
            handles=style_handles,
            loc=str(response_cfg.get('style_legend_loc', 'lower left')),
            bbox_to_anchor=tuple(response_cfg['style_legend_bbox_to_anchor']) if response_cfg.get('style_legend_bbox_to_anchor') else None,
            frameon=bool(response_cfg.get('style_legend_frameon', True)),
            fontsize=float(response_cfg.get('style_legend_fontsize', 7.4)),
            ncol=int(response_cfg.get('style_legend_ncol', 1)),
        )
    xy_cfg = response_cfg.get('xy_plot') if isinstance(response_cfg.get('xy_plot'), dict) else {}
    ax_response.set_xlim(*_as_float_tuple(xy_cfg.get('xlim'), (10, 128)))
    ax_response.set_ylim(*_as_float_tuple(xy_cfg.get('ylim'), (30, 250)))
    ax_response.set_xlabel(str(xy_cfg.get('xlabel', 'Frequency (Hz)')), fontsize=float(xy_cfg.get('label_fontsize', plt.rcParams.get('axes.labelsize', 10))), labelpad=float(xy_cfg.get('labelpad', 4.0)))
    ax_response.set_ylabel(str(xy_cfg.get('ylabel', r'Sensitivity (V $\cdot$ s/m)')), fontsize=float(xy_cfg.get('label_fontsize', plt.rcParams.get('axes.labelsize', 10))), labelpad=float(xy_cfg.get('labelpad', 4.0)))
    ax_response.tick_params(axis='both', which='major', labelsize=float(xy_cfg.get('tick_fontsize', plt.rcParams.get('xtick.labelsize', 9))), pad=float(xy_cfg.get('tick_pad', 3.0)))
    ax_response.set_box_aspect(1.0)
    ax_response.grid(True, which='both', linestyle='--', alpha=float(response_cfg.get('grid_alpha', 0.42)))
    response_margins = response_cfg.get('margins') or {}
    fig_response.subplots_adjust(
        left=float(response_margins.get('left', 0.14)),
        right=float(response_margins.get('right', 0.72)),
        bottom=float(response_margins.get('bottom', 0.14)),
        top=float(response_margins.get('top', 0.97)),
    )
    panel_response = save_panel_figure(fig_response, 'fig_08_frequency_response_comparison_d_response_before_after.png')

    name = make_bitmap_montage(
        'fig_08_frequency_response_comparison.png',
        [
            {'source': panel_response, 'label': '(a)', 'fit_height': 1700, 'trim_border': 28, 'row_span': 2, 'align_x': 'center', 'align_y': 'top', 'offset_x': 113, 'offset_y': 145},
            {'source': panel_fn, 'label': '(b)', 'fit_width': 1720, 'trim_border': 28, 'align_x': 'center', 'align_y': 'bottom'},
            {'source': panel_sens, 'label': '(c)', 'fit_width': 1720, 'trim_border': 28, 'align_x': 'center', 'align_y': 'top'},
            {'source': 'time_domain_outputs.png', 'label': '(d)', 'fit_width': 2140, 'trim_border': 24, 'align_x': 'center', 'align_y': 'top'},
            {'source': panel_reduction, 'label': '(e)', 'fit_width': 1720, 'trim_border': 24, 'align_x': 'center', 'align_y': 'top'},
        ],
        layout='matrix',
        rows=3,
        cols=2,
        padding=[55, 55, 55, 55],
        gutter=(58, 52),
        cell_widths=[2140, 1720],
        label_font_size=48,
        note='Composes the frequency-response comparison figure with panel (d) in the upper-left, panels (a) and (b) vertically stacked on the upper-right, panel (e) at the lower-left, and the four-bar panel (c) at the lower-right.',
        latex_width_fraction=0.85,
        figure_key='fig_08_frequency_response_comparison',
    )
    raw_path = FIGURES_DIR / 'fig_08_frequency_response_comparison.raw.json'
    raw_payload = json.loads(raw_path.read_text(encoding='utf-8'))
    raw_payload.update({
        'source': 'paper results payload',
        'origin': origin,
        'wiener_kan': wk,
        'trajectories': trajectories,
        'response_comparison': {
            'linear_response_path': response_path,
            'selected_magnitudes': [float(response_mags[idx]) for idx in selected_indices],
            'curves': ['gains_origin', 'gains_comped'],
        },
        'time_domain_panel': {
            'source_figure': 'time_domain_outputs.png',
            'panel_role': 'Representative time-domain outputs under selected frequency and magnitude conditions.',
        },
    })
    save_json(raw_path, raw_payload)
    generated['frequency_response_comparison'] = name

    fig, ax = plt.subplots(figsize=(8.0, 5.0), constrained_layout=True)
    for curve in main_curves:
        ax.plot(curve['epochs'], curve['smoothed_normalized_val_loss'], label=curve['label'], linewidth=2.5 if curve['label'] == 'Wiener-KAN' else 1.4)
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Normalized validation loss')
    ax.set_ylim(bottom=0)
    ax.legend(ncol=2, fontsize=8, frameon=True)
    out = FIGURES_DIR / 'fig_11_main_training_loss.png'
    generated['main_training_loss'] = _save_matplotlib_figure(
        fig,
        out,
        raw_payload={'source': 'paper results payload', 'curves': main_curves},
        bbox_inches='tight',
    )

    fig, ax = plt.subplots(figsize=(7.5, 4.6), constrained_layout=True)
    for curve in loss_curves:
        ax.plot(curve['epochs'], curve['smoothed_normalized_val_loss'], label=curve['label'], linewidth=2.0)
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Normalized validation loss')
    ax.set_ylim(bottom=0)
    ax.legend(frameon=True)
    out = FIGURES_DIR / 'fig_12_loss_validation_detail.png'
    generated['loss_validation_detail'] = _save_matplotlib_figure(
        fig,
        out,
        raw_payload={'source': 'paper results payload', 'curves': loss_curves},
        bbox_inches='tight',
    )

    distribution_panels, raw_distribution_rows = make_metric_range_panel_specs(
        main_rows,
        output_prefix='fig_13_compensation_distribution',
        label_offset=0,
        fit_width=1650,
        trim_border=28,
        figure_key='fig_13_compensation_distribution',
    )
    name = make_bitmap_montage(
        'fig_13_compensation_distribution.png',
        distribution_panels,
        layout='horizontal',
        padding=[65, 60, 65, 60],
        gutter=(70, 60),
        label_font_size=46,
        note='Composes the representative metric-range panels with the unified bitmap montage module.',
        latex_width_fraction=0.86,
        figure_key='fig_13_compensation_distribution',
    )
    raw_path = FIGURES_DIR / 'fig_13_compensation_distribution.raw.json'
    raw_payload = json.loads(raw_path.read_text(encoding='utf-8'))
    raw_payload.update({
        'source_trace': 'paper results payload metric_details min/median/mean/max fields',
        'rows': raw_distribution_rows,
        'metrics': ['natural_frequency_range', 'sensitivity_range', 'linearity_error_range'],
        'note': 'Error bars show min--max ranges across magnitudes for fn/sensitivity and across in-band frequencies for linearity.',
    })
    save_json(raw_path, raw_payload)
    generated['compensation_distribution'] = name

    return generated



def copy_legacy_images() -> None:
    # Pure bitmap copy migrations are disabled. Traceable figures must be
    # regenerated from source code; manual figures must live in image_manual.
    return


def save_figure_raw_files(payload: Dict[str, Any]) -> None:
    raw_payloads = {
        'fig_01_drift_trajectories': {'trajectories': payload['trajectories']},
        'fig_02_horizontal_summary': {'main_benchmark': payload['main_benchmark'], 'origin_metrics': payload['origin_metrics'], 'main_convergence_curves': payload['main_convergence_curves']},
        'fig_03_loss_ablation': {'loss_ablation': payload['loss_ablation'], 'loss_convergence_curves': payload['loss_convergence_curves']},
        'fig_04_structure_ablation': {'structure_ablation': payload['structure_ablation']},
        'fig_05_onboard_inference': {'deployment': payload['deployment'], 'lut_variants': payload['lut_variants'], 'lut_point_sweep': payload['lut_point_sweep']},
        'fig_18_hparam_sensitivity': {
            'hparam_sensitivity': payload.get('hparam_sensitivity'),
            'loss_ablation': payload['loss_ablation'],
            'loss_convergence_curves': payload['loss_convergence_curves'],
        },
    }
    for stem, data in raw_payloads.items():
        raw_path = FIGURES_DIR / f'{stem}.raw.json'
        if raw_path.exists():
            try:
                merged = json.loads(raw_path.read_text(encoding='utf-8'))
            except json.JSONDecodeError:
                merged = {}
        else:
            merged = {}
        merged['data_payload'] = data
        save_json(raw_path, merged)


def _origin_metrics_from_main_rows(main_rows: List[Dict[str, Any]]) -> Dict[str, float]:
    return {
        'freq': float(main_rows[0]['origin_freq_drift_hz']),
        'sens': float(main_rows[0]['origin_sens_drift_percent']),
        'linearity': float(main_rows[0]['origin_linearity_percent']),
    }


def _ensure_legacy_response_panels() -> None:
    try:
        from src.translate_legacy_figures import plot_frirnn  # type: ignore  # noqa: E402
    except ImportError:  # pragma: no cover - direct script execution
        from translate_legacy_figures import plot_frirnn  # type: ignore  # noqa: E402
    plot_frirnn()


def _render_additional_figure(ctx: Dict[str, Any], key: str) -> str:
    generated = create_additional_paper_figures({
        'origin_metrics': ctx['origin_metrics'],
        'trajectories': ctx['trajectories'],
        'main_benchmark': ctx['main_rows'],
        'structure_ablation': ctx['structure_rows'],
        'main_convergence_curves': ctx['main_curves'],
        'loss_convergence_curves': ctx['loss_curves'],
    })
    return str(generated[key])


def _render_frequency_response_comparison(ctx: Dict[str, Any]) -> str:
    _ensure_legacy_response_panels()
    return _render_additional_figure(ctx, 'frequency_response_comparison')


def _render_experimental_setup_dataset_workflow_montage() -> str:
    make_dataset_preprocessing_workflow_figure()
    return str(make_paper_bitmap_montages()['experimental_setup_dataset_workflow'])


def _render_parallel_wiener_equivalent_montage() -> str:
    make_parallel_wiener_principle_schematic('fig_14_parallel_wiener_principle')
    copy_wiener_parallel_figures()
    return str(make_paper_bitmap_montages()['parallel_wiener_equivalent'])


def legacy_renderable_figure_catalog() -> Dict[str, Dict[str, Any]]:
    return {
        'calibration_table_test': {
            'needs': set(),
            'render': lambda _ctx: make_calibration_table_test_figure(),
        },
        'fig_01_drift_trajectories': {
            'needs': {'trajectories'},
            'render': lambda ctx: make_trajectory_figure(ctx['trajectories']),
        },
        'fig_02_horizontal_summary': {
            'needs': {'main_rows', 'main_curves', 'origin_metrics'},
            'render': lambda ctx: make_horizontal_figure(ctx['main_rows'], ctx['origin_metrics'], ctx['main_curves']),
        },
        'fig_03_loss_ablation': {
            'needs': {'loss_rows', 'loss_curves'},
            'render': lambda ctx: make_loss_ablation_figure(ctx['loss_rows'], ctx['loss_curves']),
        },
        'fig_04_structure_ablation': {
            'needs': {'structure_rows'},
            'render': lambda ctx: make_structure_figure(ctx['structure_rows']),
        },
        'fig_05_onboard_inference': {
            'needs': {'deploy_rows', 'lut_rows', 'lut_point_rows'},
            'render': lambda ctx: make_onboard_figure(ctx['deploy_rows'], ctx['lut_rows'], ctx['lut_point_rows']),
        },
        'fig_08_frequency_response_comparison': {
            'needs': {'origin_metrics', 'trajectories', 'main_rows', 'structure_rows', 'main_curves', 'loss_curves'},
            'render': _render_frequency_response_comparison,
        },
        'fig_13_compensation_distribution': {
            'needs': {'origin_metrics', 'trajectories', 'main_rows', 'structure_rows', 'main_curves', 'loss_curves'},
            'render': lambda ctx: _render_additional_figure(ctx, 'compensation_distribution'),
        },
        'fig_14_met_nonlinear_mechanism': {
            'needs': set(),
            'render': lambda _ctx: make_mechanism_schematic_wrapper(),
        },
        'fig_14_parallel_wiener_principle': {
            'needs': set(),
            'render': lambda _ctx: make_parallel_wiener_principle_schematic('fig_14_parallel_wiener_principle'),
        },
        'fig_14_parallel_wiener_center_frequency': {
            'needs': set(),
            'render': lambda _ctx: copy_wiener_parallel_figures()['parallel_wiener_center_frequency'],
        },
        'fig_14_parallel_wiener_gain_100hz': {
            'needs': set(),
            'render': lambda _ctx: copy_wiener_parallel_figures()['parallel_wiener_gain_100hz'],
        },
        'fig_15_lut_lookup_principles': {
            'needs': set(),
            'render': lambda _ctx: make_lut_lookup_principles_figure(),
        },
        'fig_17_board_inference_validation_workflow': {
            'needs': set(),
            'render': lambda _ctx: make_board_inference_validation_workflow_figure(),
        },
        'fig_18_hparam_sensitivity': {
            'needs': {'hparam_summary', 'loss_rows', 'loss_curves'},
            'render': lambda ctx: make_hparam_sensitivity_figure(ctx['hparam_summary'], ctx['loss_rows'], ctx['loss_curves']),
        },
        'fig_19_dataset_preprocessing_workflow': {
            'needs': set(),
            'render': lambda _ctx: make_dataset_preprocessing_workflow_figure(),
        },
        'fig_20_met_structure_readout_montage': {
            'needs': set(),
            'render': lambda _ctx: make_paper_bitmap_montages()['met_structure_readout'],
        },
        'fig_21_experimental_setup_dataset_workflow_montage': {
            'needs': set(),
            'render': lambda _ctx: _render_experimental_setup_dataset_workflow_montage(),
        },
        'fig_22_parallel_wiener_equivalent_montage': {
            'needs': set(),
            'render': lambda _ctx: _render_parallel_wiener_equivalent_montage(),
        },
        'fig_23_kan_neuron_compensation_montage': {
            'needs': set(),
            'render': lambda _ctx: make_paper_bitmap_montages()['kan_neuron_compensation'],
        },
        'kan_neuron_compensation': {
            'needs': set(),
            'render': lambda _ctx: make_kan_neuron_compensation_figure(),
        },
        'local_transfer_slices': {
            'needs': set(),
            'render': lambda _ctx: make_local_transfer_slices_figure(),
        },
        'met_nonlinear_frequency_response': {
            'needs': set(),
            'render': lambda _ctx: make_met_nonlinear_frequency_response_figure(),
        },
        'met_structure': {
            'needs': set(),
            'render': lambda _ctx: make_met_structure_figure(),
        },
        'readout_circuit': {
            'needs': set(),
            'render': lambda _ctx: make_readout_circuit_figure(),
        },
        'wiener_kan_framework': {
            'needs': set(),
            'render': lambda _ctx: make_wiener_kan_framework_figure(),
        },
    }


def renderable_figure_catalog() -> Dict[str, Dict[str, Any]]:
    try:
        from src.visualization.paper_figure_projects import scan_plot_projects  # type: ignore  # noqa: E402
    except ImportError:
        return legacy_renderable_figure_catalog()

    registry: Dict[str, Dict[str, Any]] = {}
    for figure_id in scan_plot_projects(ROOT).keys():
        registry[figure_id] = {
            'needs': set(),
            'render': lambda _ctx, fid=figure_id: _render_ex_project_figure(fid),
        }
    if not registry:
        return legacy_renderable_figure_catalog()
    return registry


def _render_ex_project_figure(figure_id: str) -> str:
    from src.visualization.paper_figure_projects import run_project_by_figure_id  # type: ignore  # noqa: E402

    result = run_project_by_figure_id(figure_id, sync_paper=False, strict_regression=False)
    return Path(str(result['output'])).name


def list_renderable_figures() -> List[str]:
    return sorted(renderable_figure_catalog().keys())


def generate_selected_figures_legacy(
    figure_ids: List[str],
    *,
    figure_config_overrides: Dict[str, Dict[str, Any]] | None = None,
) -> Dict[str, str]:
    apply_config()
    if figure_config_overrides:
        figures = FIGURE_PIPELINE_CONFIG.setdefault('figures', {})
        for figure_id, override in figure_config_overrides.items():
            base = figures.get(figure_id) if isinstance(figures.get(figure_id), dict) else {}
            figures[figure_id] = _deep_merge(base, override)
    registry = legacy_renderable_figure_catalog()
    unknown = [figure_id for figure_id in figure_ids if figure_id not in registry]
    if unknown:
        raise KeyError(f'Unknown figure id(s): {", ".join(sorted(unknown))}')

    needs: set[str] = set()
    for figure_id in figure_ids:
        needs.update(registry[figure_id]['needs'])

    ctx: Dict[str, Any] = {}
    if 'main_rows' in needs or 'origin_metrics' in needs:
        ctx['main_rows'] = enrich_with_deployment_fields(load_metrics(MAIN_BENCHMARK))
        ctx['origin_metrics'] = _origin_metrics_from_main_rows(ctx['main_rows'])
    if 'loss_rows' in needs:
        ctx['loss_rows'] = enrich_with_deployment_fields(load_metrics(LOSS_ABLATION))
    if 'structure_rows' in needs:
        ctx['structure_rows'] = enrich_with_deployment_fields(load_metrics(STRUCTURE_ABLATION))
    if 'deploy_rows' in needs:
        ctx['deploy_rows'] = enrich_with_deployment_fields(load_metrics(DEPLOYMENT))
    if 'lut_rows' in needs:
        ctx['lut_rows'] = load_lut_variants()
    if 'lut_point_rows' in needs:
        ctx['lut_point_rows'] = load_lut_point_sweep()
    if 'trajectories' in needs:
        ctx['trajectories'] = load_trajectories()
    if 'main_curves' in needs:
        ctx['main_curves'] = load_convergence_curves(MAIN_BENCHMARK)
    if 'loss_curves' in needs:
        ctx['loss_curves'] = load_convergence_curves(LOSS_ABLATION)
    if 'hparam_summary' in needs:
        ctx['hparam_summary'] = load_hparam_sensitivity_summary()

    generated: Dict[str, str] = {}
    for figure_id in figure_ids:
        generated[figure_id] = str(registry[figure_id]['render'](ctx))
    return generated


def generate_selected_figures(figure_ids: List[str]) -> Dict[str, str]:
    apply_config()
    registry = renderable_figure_catalog()
    unknown = [figure_id for figure_id in figure_ids if figure_id not in registry]
    if unknown:
        # Keep a compatibility fallback for non-migrated figures.
        return generate_selected_figures_legacy(figure_ids)
    generated: Dict[str, str] = {}
    for figure_id in figure_ids:
        generated[figure_id] = str(registry[figure_id]['render']({}))
    return generated


def _ex_project_figure_payload() -> Dict[str, str]:
    try:
        from src.visualization.paper_figure_projects import rel_to_root, scan_plot_projects  # type: ignore  # noqa: E402
    except ImportError:
        return {}
    return {
        figure_id: rel_to_root(project.output_path)
        for figure_id, project in scan_plot_projects(ROOT).items()
    }


def generate_all(*, render_figures: bool = True) -> Dict[str, Any]:
    apply_config()
    main_rows = enrich_with_deployment_fields(load_metrics(MAIN_BENCHMARK))
    loss_rows = enrich_with_deployment_fields(load_metrics(LOSS_ABLATION))
    structure_rows = load_metrics(STRUCTURE_ABLATION)
    iir_rows = load_metrics(WIENER_FRONTEND_ABLATION)
    deploy_rows = enrich_with_deployment_fields(load_metrics(DEPLOYMENT))
    lut_rows = load_lut_variants()
    lut_point_rows = load_lut_point_sweep()
    trajectories = load_trajectories()
    main_curves = load_convergence_curves(MAIN_BENCHMARK)
    loss_curves = load_convergence_curves(LOSS_ABLATION)
    optimization_profiles = load_wiener_optimization_profiles()
    wiener_parallel = load_wiener_parallel_summary()
    hparam_summary = load_hparam_sensitivity_summary()
    ablation_overview_rows = build_ablation_overview_rows(loss_rows, structure_rows, iir_rows, hparam_summary)

    origin = {
        'freq': main_rows[0]['origin_freq_drift_hz'],
        'sens': main_rows[0]['origin_sens_drift_percent'],
        'linearity': main_rows[0]['origin_linearity_percent'],
    }

    figures: Dict[str, str] = {}
    if render_figures:
        figures = {
            'drift_trajectories': make_trajectory_figure(trajectories),
            'horizontal_summary': make_horizontal_figure(main_rows, origin, main_curves),
            'loss_ablation': make_loss_ablation_figure(loss_rows, loss_curves),
            'structure_ablation': make_structure_figure(structure_rows),
            'onboard_inference': make_onboard_figure(deploy_rows, lut_rows, lut_point_rows),
            'hparam_sensitivity': make_hparam_sensitivity_figure(hparam_summary, loss_rows, loss_curves),
            'met_nonlinear_mechanism': make_mechanism_schematic_wrapper(),
            'parallel_wiener_principle': make_parallel_wiener_principle_schematic('fig_14_parallel_wiener_principle'),
            'lut_lookup_principles': make_lut_lookup_principles_figure(),
            'board_inference_validation_workflow': make_board_inference_validation_workflow_figure(),
            'dataset_preprocessing_workflow': make_dataset_preprocessing_workflow_figure(),
            'wiener_kan_framework': make_wiener_kan_framework_figure(),
            'met_nonlinear_frequency_response': make_met_nonlinear_frequency_response_figure(),
            'local_transfer_slices': make_local_transfer_slices_figure(),
        }
        figures.update(copy_wiener_parallel_figures())
        figures.update(make_paper_bitmap_montages())
    else:
        figures = _ex_project_figure_payload()

    payload_stub = {
        'origin_metrics': origin,
        'main_benchmark': main_rows,
        'loss_ablation': loss_rows,
        'structure_ablation': structure_rows,
        'wiener_frontend_ablation': iir_rows,
        'deployment': deploy_rows,
        'lut_variants': lut_rows,
        'lut_point_sweep': lut_point_rows,
        'trajectories': trajectories,
        'main_convergence_curves': main_curves,
        'loss_convergence_curves': loss_curves,
        'wiener_optimization_profiles': optimization_profiles,
        'wiener_parallel_modeling': wiener_parallel,
        'hparam_sensitivity': hparam_summary,
        'ablation_overview': ablation_overview_rows,
    }
    if render_figures:
        figures.update(create_additional_paper_figures(payload_stub))
    payload = {
        'origin_metrics': origin,
        'main_benchmark': main_rows,
        'loss_ablation': loss_rows,
        'structure_ablation': structure_rows,
        'wiener_frontend_ablation': iir_rows,
        'deployment': deploy_rows,
        'lut_variants': lut_rows,
        'lut_point_sweep': lut_point_rows,
        'trajectories': trajectories,
        'main_convergence_curves': main_curves,
        'loss_convergence_curves': loss_curves,
        'wiener_optimization_profiles': optimization_profiles,
        'wiener_parallel_modeling': wiener_parallel,
        'hparam_sensitivity': hparam_summary,
        'ablation_overview': ablation_overview_rows,
        'figures': figures,
    }
    save_json(DATA_DIR / 'results.json', payload)
    write_values_tex(payload)
    if render_figures:
        save_figure_raw_files(payload)
        copy_legacy_images()
        validate_raw_title_free()
        validate_raw_publication_quality()
    build_tables(main_rows, loss_rows, structure_rows, iir_rows, ablation_overview_rows, deploy_rows, lut_rows, lut_point_rows, origin, optimization_profiles)
    return payload


def generate_data_only() -> Dict[str, Any]:
    payload = generate_all(render_figures=False)
    return payload


def main(figure_ids: List[str] | None = None) -> None:
    if figure_ids:
        generated = generate_selected_figures(figure_ids)
        print('Generated selected figures:')
        for figure_id, name in generated.items():
            print(f' - {figure_id}: {name}')
        return

    payload = generate_all()
    print('Generated:')
    for name in payload['figures'].values():
        print(' -', name)
    print(' - data/results.json')
    print(' - data/generated_tables.md')
    print(' - latex/values.tex')



if __name__ == '__main__':
    main()
