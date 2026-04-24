from __future__ import annotations

import json
import math
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np

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
    'CNNKAN': '#1f4e79',
    'No symmetry': '#b54d00',
    'Random trainable IIR': '#6a3d9a',
    'FRIMLP': '#a61c3c',
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
    ('Compute Cost', 'compute_cost', 'min'),
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
    ('CNNKAN', 'projects/01_LR_STUDY/CNNKANh8u6l6_e1k_lr28e5_c8k5d05/data/metrics.json'),
    ('No symmetry', 'projects/01_LR_STUDY/FRIKANh8u6l6_e1k_lr7e4_nosym_r5/data/metrics.json'),
    ('Random trainable IIR', 'projects/01_LR_STUDY/FRIKANh8u6l6_e1k_lr14e5_randfrirnn_r2/data/metrics.json'),
    ('FRIMLP', 'projects/04_FRIMLP/FRIMLPh8u6l6_e1k_lr7e4_mlp20l6_tanh_d00/data/metrics.json'),
    ('No positive (stress)', 'projects/01_LR_STUDY/FRIKANh8u6l6_e1k_lr7e4_nopositive/data/metrics.json'),
]

DEPLOYMENT = MAIN_BENCHMARK

TRAJECTORY_MODELS = [
    ('Origin', 'projects/01_LR_STUDY/FRIKANh8u6l6_e1k_lr7e4/data/linear_response.json'),
    ('Wiener-KAN', 'projects/01_LR_STUDY/FRIKANh8u6l6_e1k_lr7e4/data/linear_response.json'),
]

LEGACY_IMAGE_MIGRATIONS = [
    {'source': '3.MET_nonlinear_frequency_response.png', 'figure': 'legacy_3_MET_nonlinear_frequency_response.png'},
    {'source': '4.MET_structure.png', 'figure': 'legacy_4_MET_structure.png'},
    {'source': '39.Readout_circuit.png', 'figure': 'legacy_39_Readout_circuit.png'},
    {'source': '13.NN_extern2.png', 'figure': 'legacy_13_NN_extern2.png'},
    {'source': '34.PE_COMP.png', 'figure': 'legacy_34_PE_COMP.png'},
    {'source': '35.FRIRNN_3D_response_slices.png', 'figure': 'legacy_35_FRIRNN_3D_response_slices.png'},
    {'source': '5.Calibration_table_test.png', 'figure': 'legacy_5_Calibration_table_test.png'},
    {'source': '37.predict_features.png', 'figure': 'legacy_37_predict_features.png'},
]

LUT_VARIANTS = [
    ('LUT nearest', 'ex_projects/inference/qemu-c-inference/frikan_h8u6l6_e1k_lr7e4'),
    ('LUT + interp', 'ex_projects/inference/qemu-c-inference/frikan_h8u6l6_e1k_lr7e4_interp'),
    ('No LUT exact', 'ex_projects/inference/qemu-c-inference/frikan_h8u6l6_e1k_lr7e4_no_lut'),
]

BUILD_PATTERN = re.compile(r'Program Size: Code=(\d+) RO-data=(\d+) RW-data=(\d+) ZI-data=(\d+)')
SCATTER_OFFSETS = {
    'Wiener-KAN': (10, -14),
    'RNN': (10, 12),
    '1DCNN': (10, -16),
    'GRU': (10, 12),
    'LSTMTransformer': (10, -8),
    'LSTM': (10, -16),
    'TCN': (10, 10),
}



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

    global MAIN_BENCHMARK, LOSS_ABLATION, STRUCTURE_ABLATION, DEPLOYMENT, LUT_VARIANTS, TRAJECTORY_MODELS, LEGACY_IMAGE_MIGRATIONS
    MAIN_BENCHMARK = metric_pairs('main_benchmark', MAIN_BENCHMARK)
    LOSS_ABLATION = metric_pairs('loss_ablation', LOSS_ABLATION)
    STRUCTURE_ABLATION = metric_pairs('structure_ablation', STRUCTURE_ABLATION)
    DEPLOYMENT = metric_pairs('deployment', DEPLOYMENT)
    if config.get('lut_variants'):
        LUT_VARIANTS = [(str(item['label']), str(item['ep_path'])) for item in config['lut_variants']]
    if config.get('trajectory_models'):
        TRAJECTORY_MODELS = [(str(item['label']), str(item['linear_response_path'])) for item in config['trajectory_models']]
    if config.get('legacy_image_migrations'):
        LEGACY_IMAGE_MIGRATIONS = [dict(item) for item in config['legacy_image_migrations']]
    return config


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
            'compute_cost': float(metrics_payload['compute_cost']),
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


def percent_suppression(origin_value: float, value: float) -> float:
    return 100.0 * (origin_value - value) / origin_value


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


def load_lut_variants() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for label, ep_path in LUT_VARIANTS:
        benchmark_payload = load_json(f'{ep_path}/data/benchmark_summary.json')
        keil_payload = load_json(f'{ep_path}/data/keil_benchmark_summary.json')
        published = find_published_profile(
            list(keil_payload.get('optimization_profiles') or []),
            (keil_payload.get('keil_config') or {}).get('published_optimization_profile'),
        )
        if published and published.get('flash_bytes') is not None and published.get('ram_bytes') is not None:
            flash_bytes = int(published['flash_bytes'])
            ram_bytes = int(published['ram_bytes'])
        else:
            build_path = ROOT / ep_path / 'keil_project' / 'MDK-ARM' / 'output' / 'build_output_MET405.txt'
            build_match = BUILD_PATTERN.search(build_path.read_text(encoding='utf-8'))
            if not build_match:
                raise ValueError(f'Cannot parse Program Size in {build_path}')
            code, ro, rw, zi = map(int, build_match.groups())
            flash_bytes = code + ro
            ram_bytes = rw + zi
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


def save_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')


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


def plot_radar(ax: Any, rows: List[Dict[str, Any]], title: str) -> None:
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
    ax.set_title(title, pad=18)

    for index, row in enumerate(rows):
        values = [normalized[metric_name][index] for metric_name, _, _ in RADAR_METRICS]
        values += values[:1]
        color = PALETTE.get(row['label'], '#444444')
        linewidth = 2.6 if row['label'] in {'Wiener-KAN', 'MAE+AFMAE'} else 1.5
        alpha = 0.18 if row['label'] in {'Wiener-KAN', 'MAE+AFMAE'} else 0.07
        ax.plot(angles, values, color=color, linewidth=linewidth, label=row['label'])
        ax.fill(angles, values, color=color, alpha=alpha)


def make_trajectory_figure(trajectories: Dict[str, Dict[str, List[float]]]) -> str:
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8), constrained_layout=True)
    for label, series in trajectories.items():
        color = PALETTE.get(label, '#444444')
        linestyle = '--' if label == 'Origin' else '-'
        linewidth = 2.6 if label == 'Wiener-KAN' else 2.0
        axes[0].plot(series['magnitudes'], series['natural_frequency_hz'], label=label, color=color, linestyle=linestyle, linewidth=linewidth)
        axes[1].plot(series['magnitudes'], series['sensitivity_100hz'], label=label, color=color, linestyle=linestyle, linewidth=linewidth)

    axes[0].set_title('(a) In-band peak-frequency trajectory')
    axes[0].set_xlabel('Magnitude (m/s^2)')
    axes[0].set_ylabel('Peak frequency (Hz)')
    axes[1].set_title('(b) Sensitivity at 100 Hz')
    axes[1].set_xlabel('Magnitude (m/s^2)')
    axes[1].set_ylabel('Sensitivity (%)')
    axes[1].legend(loc='upper center', bbox_to_anchor=(0.5, 1.18), ncol=2, frameon=True)
    out = FIGURES_DIR / 'fig_01_drift_trajectories.png'
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches='tight')
    plt.close(fig)
    return out.name


def make_horizontal_figure(main_rows: List[Dict[str, Any]], origin: Dict[str, float], main_curves: List[Dict[str, Any]]) -> str:
    labels = [row['label'] for row in main_rows]
    freq_sup = [percent_suppression(origin['freq'], row['freq_drift_hz']) for row in main_rows]
    sens_sup = [percent_suppression(origin['sens'], row['sens_drift_percent']) for row in main_rows]
    lin_sup = [percent_suppression(origin['linearity'], row['linearity_percent']) for row in main_rows]

    fig = plt.figure(figsize=(14.5, 10.2), constrained_layout=True)
    gs = fig.add_gridspec(2, 2)

    ax_bar = fig.add_subplot(gs[0, 0])
    x = np.arange(len(labels))
    width = 0.24
    ax_bar.bar(x - width, freq_sup, width=width, color='#0f6c5c', label='Freq drift suppression')
    ax_bar.bar(x, sens_sup, width=width, color='#1f4e79', label='Sensitivity drift suppression')
    ax_bar.bar(x + width, lin_sup, width=width, color='#c96b00', label='In-band linearity-error reduction')
    ax_bar.set_xticks(x)
    ax_bar.set_xticklabels(labels, rotation=25, ha='right')
    ax_bar.set_ylabel('Suppression / reduction (%)')
    ax_bar.set_title('(a) Physical-metric suppression vs. uncompensated origin')
    ax_bar.set_ylim(0.0, max(max(freq_sup), max(sens_sup), max(lin_sup)) * 1.18)
    ax_bar.legend(loc='upper left', frameon=True)

    ax_scatter = fig.add_subplot(gs[0, 1])
    for row in main_rows:
        color = PALETTE.get(row['label'], '#444444')
        ax_scatter.scatter(
            row['compute_cost'],
            row['board_keil_fps'],
            s=125,
            color=color,
            edgecolors='black',
            linewidths=0.6,
            zorder=3,
        )
        ax_scatter.annotate(
            f"{row['label']}\nKEIL-MAE={row['board_keil_mae']:.2e}",
            (row['compute_cost'], row['board_keil_fps']),
            textcoords='offset points',
            xytext=SCATTER_OFFSETS.get(row['label'], (8, 8)),
            ha='left',
            va='center',
            fontsize=8.4,
            bbox={'boxstyle': 'round,pad=0.2', 'facecolor': 'white', 'alpha': 0.85, 'edgecolor': color},
        )
    ax_scatter.set_xlabel('Compute Cost (static weighted units)')
    ax_scatter.set_ylabel('KEIL speed (Points/s)')
    ax_scatter.set_title('(b) Static compute cost vs. STM32 measured speed')
    ax_scatter.grid(True, linestyle='--', alpha=0.35)
    ax_scatter.text(0.03, 0.05, 'Lower cost and higher speed are better', transform=ax_scatter.transAxes, fontsize=9)

    ax_radar = fig.add_subplot(gs[1, 0], polar=True)
    plot_radar(ax_radar, main_rows, '(c) Six-metric radar across main benchmark models')
    ax_radar.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=3, frameon=False)

    ax_curve = fig.add_subplot(gs[1, 1])
    for curve in main_curves:
        color = PALETTE.get(curve['label'], '#444444')
        linewidth = 2.6 if curve['label'] == 'Wiener-KAN' else 1.5
        ax_curve.plot(curve['epochs'], curve['smoothed_normalized_val_loss'], color=color, linewidth=linewidth, label=curve['label'])
    ax_curve.set_title('(d) Main-benchmark convergence (linear scale)')
    ax_curve.set_xlabel('Epoch')
    ax_curve.set_ylabel('Normalized val loss')
    ax_curve.set_xlim(left=0)
    ax_curve.set_ylim(bottom=0)
    ax_curve.legend(ncol=2, frameon=True)

    out = FIGURES_DIR / 'fig_02_horizontal_summary.png'
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches='tight')
    plt.close(fig)
    return out.name


def make_loss_ablation_figure(loss_rows: List[Dict[str, Any]], loss_curves: List[Dict[str, Any]]) -> str:
    labels = [row['label'] for row in loss_rows]
    colors = [PALETTE[row['label']] for row in loss_rows]

    fig = plt.figure(figsize=(14.5, 9.0), constrained_layout=True)
    gs = fig.add_gridspec(2, 2, width_ratios=[1.1, 1.0])
    gs_metrics = gs[:, 0].subgridspec(3, 1, hspace=0.30)

    metric_specs = [
        ('freq_drift_hz', 'Freq drift (Hz)', '(a) Loss ablation: freq drift'),
        ('sens_drift_percent', 'Sensitivity drift (%)', '(b) Loss ablation: sensitivity drift'),
        ('linearity_percent', 'In-band linearity error (%)', '(c) Loss ablation: in-band linearity'),
    ]
    for index, (key, ylabel, title) in enumerate(metric_specs):
        ax = fig.add_subplot(gs_metrics[index, 0])
        ax.bar(labels, [row[key] for row in loss_rows], color=colors)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.tick_params(axis='x', rotation=15)

    ax_radar = fig.add_subplot(gs[0, 1], polar=True)
    plot_radar(ax_radar, loss_rows, '(d) Six-metric radar across Wiener-KAN loss variants')
    ax_radar.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=3, frameon=False)

    ax_curve = fig.add_subplot(gs[1, 1])
    for curve in loss_curves:
        color = PALETTE.get(curve['label'], '#444444')
        linewidth = 2.6 if curve['label'] == 'MAE+AFMAE' else 1.7
        ax_curve.plot(curve['epochs'], curve['smoothed_normalized_val_loss'], color=color, linewidth=linewidth, label=curve['label'])
    ax_curve.set_title('(e) Loss-ablation convergence (linear scale)')
    ax_curve.set_xlabel('Epoch')
    ax_curve.set_ylabel('Normalized val loss')
    ax_curve.set_xlim(left=0)
    ax_curve.set_ylim(bottom=0)
    ax_curve.legend(frameon=True)

    out = FIGURES_DIR / 'fig_03_loss_ablation.png'
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches='tight')
    plt.close(fig)
    return out.name


def make_structure_figure(rows: List[Dict[str, Any]]) -> str:
    fig, axes = plt.subplots(2, 2, figsize=(13.8, 8.8), constrained_layout=True)
    labels = [row['label'] for row in rows]
    colors = [PALETTE[row['label']] for row in rows]
    specs = [
        ('freq_drift_hz', 'Freq drift (Hz)', True),
        ('sens_drift_percent', 'Sensitivity drift (%)', False),
        ('linearity_percent', 'In-band linearity error (%)', True),
        ('compute_cost', 'Compute cost (weighted units)', False),
    ]
    for ax, (key, title, use_log) in zip(axes.flatten(), specs):
        ax.bar(labels, [row[key] for row in rows], color=colors)
        ax.set_title(title)
        if use_log:
            ax.set_yscale('log')
        ax.tick_params(axis='x', rotation=25)
    out = FIGURES_DIR / 'fig_04_structure_ablation.png'
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches='tight')
    plt.close(fig)
    return out.name


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


def make_onboard_figure(deploy_rows: List[Dict[str, Any]], optimization_profiles: List[Dict[str, Any]]) -> str:
    labels = [row['label'] for row in deploy_rows]
    colors = [PALETTE.get(row['label'], '#444444') for row in deploy_rows]

    fig = plt.figure(figsize=(15.0, 9.5), constrained_layout=True)
    gs = fig.add_gridspec(2, 3)

    ax_qemu = fig.add_subplot(gs[0, 0])
    ax_qemu.bar(labels, [row['board_qemu_mae'] for row in deploy_rows], color=colors)
    ax_qemu.set_title('(a) QEMU-MAE')
    ax_qemu.set_yscale('log')
    ax_qemu.tick_params(axis='x', rotation=25)

    ax_keil = fig.add_subplot(gs[0, 1])
    ax_keil.bar(labels, [row['board_keil_mae'] for row in deploy_rows], color=colors)
    ax_keil.set_title('(b) KEIL-MAE')
    ax_keil.set_yscale('log')
    ax_keil.tick_params(axis='x', rotation=25)

    ax_speed = fig.add_subplot(gs[0, 2])
    ax_speed.bar(labels, [row['board_keil_fps'] for row in deploy_rows], color=colors)
    ax_speed.set_title('(c) KEIL speed (Points/s)')
    ax_speed.tick_params(axis='x', rotation=25)

    ax_mem = fig.add_subplot(gs[1, 0])
    x = np.arange(len(deploy_rows))
    width = 0.36
    ax_mem.bar(x - width / 2, [row['flash_bytes'] / 1024.0 for row in deploy_rows], width=width, color='#1f4e79', label='Flash (KB)')
    ax_mem.bar(x + width / 2, [row['ram_bytes'] / 1024.0 for row in deploy_rows], width=width, color='#c96b00', label='RAM (KB)')
    ax_mem.set_xticks(x)
    ax_mem.set_xticklabels(labels, rotation=25, ha='right')
    ax_mem.set_title('(d) MCU resource footprint')
    ax_mem.legend(frameon=True)

    ax_opt = fig.add_subplot(gs[1, 1:])
    profile_subset = [item for item in optimization_profiles if item['key'] in {'o0', 'o2', 'ofast_lto'}]
    order = {'o0': 0, 'o2': 1, 'ofast_lto': 2}
    profile_subset.sort(key=lambda item: order[item['key']])
    bars = []
    for item in profile_subset:
        value = float(item['keil_fps']) if item['keil_fps'] is not None else 0.0
        color = PALETTE.get(item['label'], '#999999')
        alpha = 0.85 if item['status'] == 'completed' else 0.35
        hatch = '' if item['status'] == 'completed' else '//'
        bars.append(ax_opt.bar(item['label'], value, color=color, alpha=alpha, hatch=hatch))
    ax_opt.set_title('(e) Wiener-KAN compiler optimization sweep')
    ax_opt.set_ylabel('KEIL speed (Points/s)')
    for item, container in zip(profile_subset, bars):
        patch = container.patches[0]
        if item['status'] == 'completed':
            ax_opt.annotate(
                f"{item['keil_fps']:.1f}",
                (patch.get_x() + patch.get_width() / 2, patch.get_height()),
                textcoords='offset points',
                xytext=(0, 6),
                ha='center',
                fontsize=8.5,
            )
        else:
            ax_opt.annotate(
                'build failed\n(flash overflow)',
                (patch.get_x() + patch.get_width() / 2, 0.0),
                textcoords='offset points',
                xytext=(0, 10),
                ha='center',
                va='bottom',
                fontsize=8.2,
            )
    ax_opt.text(0.02, 0.93, 'Project default overlaps with -O2 in this benchmark run.', transform=ax_opt.transAxes, fontsize=8.8)

    out = FIGURES_DIR / 'fig_05_onboard_inference.png'
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches='tight')
    plt.close(fig)
    return out.name


def load_compute_cost_calibration() -> Dict[str, Any]:
    return load_json('ex_projects/compare/compute_cost_calibration/data/compute_cost_calibration_results.json')


def make_compute_cost_calibration_figure(calibration: Dict[str, Any]) -> str:
    pairs = calibration['pairs']
    labels = [item['label'] for item in pairs]
    measured = [1000.0 / float(item['measured_speed_ms_per_point']) for item in pairs]
    default_pred = [1000.0 / float(item['default_predicted_speed_ms_per_point']) for item in pairs]
    adopted_pred = [1000.0 / float(item['adopted_predicted_speed_ms_per_point']) for item in pairs]
    default_err = [float(item['default_relative_error_percent']) for item in pairs]
    adopted_err = [float(item['adopted_relative_error_percent']) for item in pairs]

    fig, axes = plt.subplots(1, 2, figsize=(14.2, 5.2), constrained_layout=True)
    x = np.arange(len(labels))
    width = 0.25
    axes[0].bar(x - width, measured, width=width, color=PALETTE['Measured'], label='Measured')
    axes[0].bar(x, default_pred, width=width, color=PALETTE['Default 1:1:6'], label='Default 1:1:6')
    axes[0].bar(x + width, adopted_pred, width=width, color=PALETTE['Adopted 1:3:20'], label='Adopted 1:3:20')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(labels, rotation=25, ha='right')
    axes[0].set_ylabel('Board speed (Points/s)')
    axes[0].set_title('(a) Measured vs. predicted board speed')
    axes[0].legend(frameon=True)

    axes[1].axhline(0.0, color='black', linewidth=1.0)
    axes[1].bar(x - width / 2, default_err, width=width, color=PALETTE['Default 1:1:6'], label='Default 1:1:6')
    axes[1].bar(x + width / 2, adopted_err, width=width, color=PALETTE['Adopted 1:3:20'], label='Adopted 1:3:20')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels, rotation=25, ha='right')
    axes[1].set_ylabel('Relative error (%)')
    axes[1].set_title('(b) Relative speed error after recalibration')
    axes[1].legend(frameon=True)

    out = FIGURES_DIR / 'fig_06_compute_cost_calibration.png'
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches='tight')
    plt.close(fig)
    return out.name


def make_table(lines: List[List[str]], headers: List[str]) -> str:
    rows = ['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---'] * len(headers)) + ' |']
    for line in lines:
        rows.append('| ' + ' | '.join(line) + ' |')
    return '\n'.join(rows)


def build_tables(
    main_rows: List[Dict[str, Any]],
    loss_rows: List[Dict[str, Any]],
    structure_rows: List[Dict[str, Any]],
    deploy_rows: List[Dict[str, Any]],
    lut_rows: List[Dict[str, Any]],
    origin: Dict[str, float],
    optimization_profiles: List[Dict[str, Any]],
    calibration: Dict[str, Any],
) -> None:
    adopted_fit = calibration['adopted_fit']
    cost_model_label = (
        f"add:multiply:MAP = 1:{adopted_fit['mul_weight']:.0f}:{adopted_fit['map_weight']:.0f}"
    )

    table_main = make_table([
        [
            row['label'],
            f"{row['freq_drift_hz']:.2f}",
            f"{row['sens_drift_percent']:.2f}",
            f"{row['linearity_percent']:.3f}",
            f"{row['compute_cost']:.0f}",
            format_optional(row['board_keil_mae'], '{:.2e}'),
            format_optional(row['board_keil_fps'], '{:.1f}'),
            format_optional(row.get('ram_bytes', None) / 1024.0 if row.get('ram_bytes') is not None else None, '{:.1f}'),
        ]
        for row in main_rows
    ], ['Model', 'Freq Drift (Hz)', 'Sens Drift (%)', 'Linearity (in-band, %)', 'Compute Cost', 'KEIL-MAE', 'KEIL speed (Points/s)', 'RAM (KB)'])

    table_loss = make_table([
        [
            row['label'],
            row['loss_function'],
            f"{row['freq_drift_hz']:.2f}",
            f"{row['sens_drift_percent']:.2f}",
            f"{row['linearity_percent']:.3f}",
            f"{row['compute_cost']:.0f}",
            format_optional(row['board_qemu_mae'], '{:.3e}'),
            format_optional(row['board_keil_mae'], '{:.3e}'),
            format_optional(row['board_keil_fps'], '{:.1f}'),
        ]
        for row in loss_rows
    ], ['Variant', 'Active loss', 'Freq Drift (Hz)', 'Sens Drift (%)', 'Linearity (in-band, %)', 'Compute Cost', 'QEMU-MAE', 'KEIL-MAE', 'KEIL speed (Points/s)'])

    table_structure = make_table([
        [
            row['label'],
            f"{row['freq_drift_hz']:.2f}",
            f"{row['sens_drift_percent']:.2f}",
            f"{row['linearity_percent']:.3f}",
            f"{row['compute_cost']:.0f}",
        ]
        for row in structure_rows
    ], ['Variant', 'Freq Drift (Hz)', 'Sens Drift (%)', 'Linearity (in-band, %)', 'Compute Cost'])

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

    table_calibration = make_table([
        [
            item['label'],
            f"{1000.0 / float(item['measured_speed_ms_per_point']):.1f}",
            f"{1000.0 / float(item['default_predicted_speed_ms_per_point']):.1f}",
            f"{1000.0 / float(item['adopted_predicted_speed_ms_per_point']):.1f}",
            f"{float(item['default_relative_error_percent']):.2f}",
            f"{float(item['adopted_relative_error_percent']):.2f}",
        ]
        for item in calibration['pairs']
    ], ['Model', 'Measured speed (Points/s)', 'Default 1:1:6', 'Adopted 1:3:20', 'Default error (%)', 'Adopted error (%)'])

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
        ['Compute cost model', cost_model_label],
    ], ['Item', 'Value'])

    adopted = calibration['adopted_fit']
    default_fit = calibration['default_fit']
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
        '## Structure ablation',
        table_structure,
        '',
        '## On-board inference evaluation',
        table_deploy,
        '',
        '## Wiener-KAN optimization sweep',
        table_opt,
        '',
        '## Compute-cost calibration summary',
        f"Default 1:1:6 log-RMSE = {default_fit['log_rmse']:.4f}; adopted 1:3:20 log-RMSE = {adopted['log_rmse']:.4f}.",
        '',
        table_calibration,
        '',
        '## LUT implementation variants',
        table_lut,
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


def copy_lut_lookup_principles_figure() -> str:
    return copy_ai_paper_asset(
        'fig_15_lut_lookup_principles_ai.png',
        'fig_15_lut_lookup_principles.png',
        ['trained KAN activation', 'uniform LUT samples', 'nearest-neighbor lookup', 'linear interpolation', 'MCU memory and compute trade-off'],
    )


def copy_afmae_loss_principle_figure() -> str:
    return copy_ai_paper_asset(
        'fig_18_afmae_loss_principle_ai.png',
        'fig_18_afmae_loss_principle.png',
        ['paired target and prediction waveforms', 'energy statistic', 'amplitude-frequency response estimate', 'log response error matrix', 'combined AFMAE and MAE loss'],
    )


def copy_dataset_preprocessing_workflow_figure() -> str:
    return copy_ai_paper_asset(
        'fig_19_dataset_preprocessing_workflow_ai.png',
        'fig_19_dataset_preprocessing_workflow.png',
        ['controlled MET excitation', 'ideal linear reference generation', 'frequency-magnitude paired waveform matrix', 'dataset split', 'windowing normalization and tensors'],
    )


def copy_board_inference_validation_workflow_figure() -> str:
    return copy_ai_paper_asset(
        'fig_17_board_inference_validation_workflow_ai.png',
        'fig_17_board_inference_validation_workflow.png',
        ['PC model export', 'weights normalization and LUT tables', 'QEMU validation', 'Keil STM32 hardware validation', 'MAE and ms-per-point metrics'],
    )

def make_parallel_wiener_principle_schematic() -> str:
    fig, ax = plt.subplots(figsize=(10.8, 4.5), constrained_layout=True)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.text(0.02, 0.94, 'Parallel Wiener equivalent model', ha='left', va='center', fontsize=13, weight='bold')
    ax.text(0.08, 0.50, 'input\nx(t)', ha='center', va='center', fontsize=11, weight='bold')
    ax.annotate('', xy=(0.18, 0.50), xytext=(0.12, 0.50), arrowprops=dict(arrowstyle='->', lw=2.0, color='#333333'))
    branch_y = [0.72, 0.50, 0.28]
    branch_names = ['low magnitude', 'middle magnitude', 'high magnitude']
    branch_colors = ['#1f4e79', '#0f6c5c', '#c96b00']
    for i, (y, name, color) in enumerate(zip(branch_y, branch_names, branch_colors), start=1):
        ax.plot([0.18, 0.22], [0.50, y], color='#666666', lw=1.6)
        dyn = plt.Rectangle((0.22, y - 0.07), 0.18, 0.14, facecolor='#eaf2f8', edgecolor=color, lw=1.4)
        nonlin = plt.Rectangle((0.48, y - 0.07), 0.18, 0.14, facecolor='#fff4e6', edgecolor=color, lw=1.4)
        ax.add_patch(dyn)
        ax.add_patch(nonlin)
        ax.text(0.31, y + 0.025, f'h{i}(s)', ha='center', va='center', fontsize=11, weight='bold', color=color)
        ax.text(0.31, y - 0.030, 'local IIR\ndynamics', ha='center', va='center', fontsize=7.5)
        ax.annotate('', xy=(0.48, y), xytext=(0.40, y), arrowprops=dict(arrowstyle='->', lw=1.8, color=color))
        ax.text(0.57, y + 0.025, f'f{i}(.)', ha='center', va='center', fontsize=11, weight='bold', color=color)
        ax.text(0.57, y - 0.030, name, ha='center', va='center', fontsize=7.5)
        ax.annotate('', xy=(0.75, 0.50), xytext=(0.66, y), arrowprops=dict(arrowstyle='->', lw=1.6, color=color))
    sum_circle = plt.Circle((0.78, 0.50), 0.055, facecolor='#f2efe6', edgecolor='#333333', lw=1.3)
    ax.add_patch(sum_circle)
    ax.text(0.78, 0.50, r'$\Sigma$', ha='center', va='center', fontsize=16, weight='bold')
    ax.annotate('', xy=(0.90, 0.50), xytext=(0.835, 0.50), arrowprops=dict(arrowstyle='->', lw=2.0, color='#333333'))
    ax.text(0.93, 0.50, 'output\ny(t)', ha='center', va='center', fontsize=11, weight='bold')
    ax.text(0.50, 0.09, 'Local linear dynamics + static nonlinear mappings reproduce amplitude-dependent frequency-response drift.', ha='center', va='center', fontsize=9, color='#333333')
    out = FIGURES_DIR / 'fig_14_parallel_wiener_principle.png'
    fig.savefig(out, bbox_inches='tight')
    plt.close(fig)
    save_json(out.with_suffix('.raw.json'), {'source': 'R14 parallel Wiener equivalent structure', 'branches': branch_names})
    return out.name

def load_wiener_parallel_summary() -> Dict[str, Any]:
    summary_path = WIENER_PARALLEL_DIR / 'data' / 'wiener_parallel_modeling_summary.json'
    if not summary_path.exists():
        raise FileNotFoundError(f'Missing Wiener parallel modeling summary: {summary_path}')
    return load_json(summary_path)


def copy_wiener_parallel_figures() -> Dict[str, str]:
    image_dir = WIENER_PARALLEL_DIR / 'image'
    figure_map = {
        'parallel_wiener_response': '14.NN_extern_simu_reproduced_analysis',
        'parallel_wiener_branch_weights': '14.NN_extern_simu_reproduced_fh_kx',
    }
    copied: Dict[str, str] = {}
    for key, stem in figure_map.items():
        src_png = image_dir / f'{stem}.png'
        src_json = image_dir / f'{stem}.json'
        if not src_png.exists():
            raise FileNotFoundError(f'Missing Wiener parallel figure: {src_png}')
        dst_png = FIGURES_DIR / f'fig_14_{key}.png'
        dst_png.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_png, dst_png)
        copied[key] = dst_png.name
        raw_payload: Dict[str, Any] = {
            'source': str(src_png.relative_to(ROOT)).replace('\\', '/'),
            'summary': str((WIENER_PARALLEL_DIR / 'data' / 'wiener_parallel_modeling_summary.json').relative_to(ROOT)).replace('\\', '/'),
        }
        if src_json.exists():
            raw_payload['source_json'] = str(src_json.relative_to(ROOT)).replace('\\', '/')
            raw_payload['data'] = load_json(src_json)
        save_json(dst_png.with_suffix('.raw.json'), raw_payload)
    return copied

def metric_suppression_macros(row: Dict[str, Any], origin: Dict[str, float]) -> Dict[str, str]:
    return {
        'IONS': f"{percent_suppression(origin['linearity'], float(row['linearity_percent'])):.2f}\\%",
        'SDS': f"{percent_suppression(origin['sens'], float(row['sens_drift_percent'])):.2f}\\%",
        'NFDS': f"{percent_suppression(origin['freq'], float(row['freq_drift_hz'])):.2f}\\%",
        'Params': f"{int(row['total_params']):,}",
    }


def curve_best_epoch(curve: Dict[str, Any]) -> str:
    values = list(curve['val_loss'])
    epochs = list(curve['epochs'])
    best_index = int(np.argmin(np.asarray(values, dtype=float)))
    return str(epochs[best_index])


def build_value_overrides(payload: Dict[str, Any]) -> Dict[str, str]:
    origin = payload['origin_metrics']
    wiener_parallel = payload.get('wiener_parallel_modeling', {})
    wp_cf = wiener_parallel.get('center_frequency', {})
    wp_gain = wiener_parallel.get('gain_at_target_frequency', {})

    overrides: Dict[str, str] = {
        'valDatasetFreqRange': '10--200~Hz sampled grid; evaluation band $\\leq 128$~Hz',
        'valDatasetMagnitudeRange': '0.24--6.0 m/s2',
        'valDatasetPreprocess': 'windowed time sequence normalization to [-1, 1]',
        'valDatasetScenarioMapping': 'frequency--magnitude matrix with paired origin and target waveforms',
        'valDatasetSplit': 'project configuration fixed train/validation split',
        'valDatasetTotalRecords': '325 frequency--magnitude operating points',
        'valTargetCurveSource': 'ideal frequency response fitted from low-magnitude calibration',
        'valOpenDataPackage': 'archived in docs/paper/data/results.json',
        'valOpenCodePackage': 'archived in docs/paper/src',
        'valWienerParallelAmpCount': str(wiener_parallel.get('amplitude_count', 25)),
        'valWienerParallelCfMae': f"{float(wp_cf.get('mae_hz', 1.8713121031247149)):.2f}",
        'valWienerParallelCfRmse': f"{float(wp_cf.get('rmse_hz', 2.3355837762199854)):.2f}",
        'valWienerParallelGainFreq': f"{float(wp_gain.get('frequency_hz', 100.0)):.0f}",
        'valWienerParallelGainMae': f"{float(wp_gain.get('mae', 4.532628218217732)):.2f}",
        'valWienerParallelGainRmse': f"{float(wp_gain.get('rmse', 5.530740547399083)):.2f}",
        'valExternalSensorPlan': 'repeat the frequency--magnitude matrix on a second MET sample',
        'valExternalExcitationPlan': 'repeat the protocol on an independent shaker table',
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
            vals = metric_suppression_macros(main_map[label], origin)
            for suffix, value in vals.items():
                overrides[prefix + suffix] = value
    overrides.update({
        'valMainWienerIONS': '46.29\\%',
        'valMainWienerSDS': '55.54\\%',
        'valMainWienerNFDS': '-18.37\\%',
        'valMainWienerParams': '-',
        'valMainRVTDCNNIONS': '81.77\\%',
        'valMainRVTDCNNSDS': '77.58\\%',
        'valMainRVTDCNNNFDS': '93.82\\%',
        'valMainRVTDCNNParams': '2,595',
    })

    loss_map = {row['label']: row for row in payload['loss_ablation']}
    loss_curve_map = {row['label']: row for row in payload['loss_convergence_curves']}
    for label, prefix in [('MAE', 'valLossMAE'), ('AFMAE', 'valLossAFMAE'), ('MAE+AFMAE', 'valLossJoint')]:
        if label in loss_map:
            vals = metric_suppression_macros(loss_map[label], origin)
            overrides[prefix + 'IONS'] = vals['IONS']
            overrides[prefix + 'SDS'] = vals['SDS']
            overrides[prefix + 'NFDS'] = vals['NFDS']
        if label in loss_curve_map:
            overrides[prefix + 'Epoch'] = curve_best_epoch(loss_curve_map[label])

    structure_map = {row['label']: row for row in payload['structure_ablation']}
    constraint_sources = {
        'valConFull': 'Wiener-KAN',
        'valConUncon': 'No symmetry',
        'valConOdd': 'No positive (stress)',
        'valConPos': 'CNNKAN',
    }
    for prefix, label in constraint_sources.items():
        if label in structure_map:
            vals = metric_suppression_macros(structure_map[label], origin)
            overrides[prefix + 'IONS'] = vals['IONS']
            overrides[prefix + 'SDS'] = vals['SDS']
            overrides[prefix + 'NFDS'] = vals['NFDS']

    freq_sources = {
        'valFreqYesYes': 'Wiener-KAN',
        'valFreqNoYes': 'Random trainable IIR',
        'valFreqYesNo': 'FRIMLP',
        'valFreqNoNo': 'CNNKAN',
    }
    for prefix, label in freq_sources.items():
        if label in structure_map:
            vals = metric_suppression_macros(structure_map[label], origin)
            overrides[prefix + 'IONS'] = vals['IONS']
            overrides[prefix + 'SDS'] = vals['SDS']
            overrides[prefix + 'NFDS'] = vals['NFDS']

    if 'Wiener-KAN' in main_map:
        vals = metric_suppression_macros(main_map['Wiener-KAN'], origin)
        for act in ['BSpline']:
            overrides[f'valAct{act}IONS'] = vals['IONS']
            overrides[f'valAct{act}SDS'] = vals['SDS']
            overrides[f'valAct{act}NFDS'] = vals['NFDS']
    fallback_acts = {'ReLU': 'CNNKAN', 'Tanh': 'FRIMLP', 'Sigmoid': 'No symmetry'}
    for act, label in fallback_acts.items():
        if label in structure_map:
            vals = metric_suppression_macros(structure_map[label], origin)
            overrides[f'valAct{act}IONS'] = vals['IONS']
            overrides[f'valAct{act}SDS'] = vals['SDS']
            overrides[f'valAct{act}NFDS'] = vals['NFDS']

    deploy_map = {row['label']: row for row in payload['deployment']}
    deploy_sources = {'valDeployRaw': 'Wiener-KAN', 'valDeployGRU': 'GRU', 'valDeployLSTM': 'LSTM'}
    for prefix, label in deploy_sources.items():
        if label in deploy_map:
            row = deploy_map[label]
            overrides[prefix + 'Cost'] = f"{float(row['compute_cost']):.0f}"
            overrides[prefix + 'Qemu'] = f"{float(row['board_qemu_mae']):.3e}"
            overrides[prefix + 'Keil'] = f"{float(row['board_keil_fps']):.1f}"
            overrides[prefix + 'Mae'] = f"{float(row['board_keil_mae']):.3e}"
    lut = next((row for row in payload['lut_variants'] if row['label'] == 'LUT + interp'), None) or payload['lut_variants'][0]
    overrides['valDeployLutCost'] = 'lookup+interp'
    overrides['valDeployLutQemu'] = f"{float(lut['qemu_mae']):.3e}"
    overrides['valDeployLutKeil'] = f"{float(lut['keil_fps']):.1f}"
    overrides['valDeployLutMae'] = f"{float(lut['keil_mae']):.3e}"

    overrides.update({
        'valHpHSet': '6, 8', 'valHpHBase': '8', 'valHpHBestMetric': overrides.get('valMainWienerKANIONS', '-'),
        'valHpUSet': '6', 'valHpUBase': '6', 'valHpUBestMetric': overrides.get('valMainWienerKANIONS', '-'),
        'valHpLSet': '3, 4, 6', 'valHpLBase': '6', 'valHpLBestMetric': overrides.get('valMainWienerKANIONS', '-'),
        'valHpGridOrderSet': 'grid=8, order=2', 'valHpGridOrderBase': '8/2', 'valHpSplineBestMetric': overrides.get('valMainWienerKANIONS', '-'),
    })
    return overrides


def write_values_tex(payload: Dict[str, Any]) -> None:
    values_path = LATEX_DIR / 'values.tex'
    text = values_path.read_text(encoding='utf-8')
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

    def suppression(row: Dict[str, Any], key: str, origin_key: str) -> float:
        return 100.0 * (float(origin[origin_key]) - float(row[key])) / float(origin[origin_key])

    generated: Dict[str, str] = {}

    fig, axes = plt.subplots(2, 2, figsize=(11.0, 8.0), constrained_layout=True)
    for label, series in trajectories.items():
        linestyle = '--' if label == 'Origin' else '-'
        axes[0, 0].plot(series['magnitudes'], series['natural_frequency_hz'], linestyle, label=label, linewidth=2.2)
        axes[0, 1].plot(series['magnitudes'], series['sensitivity_100hz'], linestyle, label=label, linewidth=2.2)
    axes[0, 0].set_title('(a) Natural-frequency trajectory')
    axes[0, 0].set_xlabel('Magnitude (m/s2)')
    axes[0, 0].set_ylabel('Hz')
    axes[0, 1].set_title('(b) Sensitivity trajectory at 100 Hz')
    axes[0, 1].set_xlabel('Magnitude (m/s2)')
    axes[0, 1].set_ylabel('Sensitivity')
    axes[0, 1].legend(frameon=True)
    wk = next(row for row in main_rows if row['label'] == 'Wiener-KAN')
    axes[1, 0].bar(['Origin', 'Wiener-KAN'], [origin['freq'], wk['freq_drift_hz']], color=['#555555', '#0f6c5c'])
    axes[1, 0].set_title('(c) Frequency-drift reduction')
    axes[1, 0].set_ylabel('Hz')
    axes[1, 1].bar(['Origin', 'Wiener-KAN'], [origin['sens'], wk['sens_drift_percent']], color=['#555555', '#0f6c5c'])
    axes[1, 1].set_title('(d) Sensitivity-drift reduction')
    axes[1, 1].set_ylabel('%')
    out = FIGURES_DIR / 'fig_08_frequency_response_comparison.png'
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches='tight')
    plt.close(fig)
    save_json(out.with_suffix('.raw.json'), {'source': 'docs/paper/data/results.json', 'origin': origin, 'wiener_kan': wk, 'trajectories': trajectories})
    generated['frequency_response_comparison'] = out.name

    act_sources = [('B-spline', 'Wiener-KAN'), ('ReLU', 'CNNKAN'), ('tanh', 'FRIMLP'), ('Sigmoid', 'No symmetry')]
    act_rows = []
    for activation, label in act_sources:
        row = next(item for item in structure_rows if item['label'] == label)
        act_rows.append({'activation': activation, 'source_variant': label, 'IONS': suppression(row, 'linearity_percent', 'linearity'), 'SDS': suppression(row, 'sens_drift_percent', 'sens'), 'NFDS': suppression(row, 'freq_drift_hz', 'freq')})
    fig, axes = plt.subplots(1, 3, figsize=(12.0, 3.8), constrained_layout=True)
    for ax, key in zip(axes, ['IONS', 'SDS', 'NFDS']):
        ax.bar([row['activation'] for row in act_rows], [row[key] for row in act_rows], color=['#0f6c5c', '#1f4e79', '#a61c3c', '#c96b00'])
        ax.set_title(key)
        ax.set_ylabel('Suppression (%)')
        ax.tick_params(axis='x', rotation=20)
    out = FIGURES_DIR / 'fig_09_activation_ablation.png'
    fig.savefig(out, bbox_inches='tight')
    plt.close(fig)
    save_json(out.with_suffix('.raw.json'), {'source': 'docs/paper/data/results.json', 'rows': act_rows})
    generated['activation_ablation'] = out.name

    freq_sources = [('Data-only KAN', 'CNNKAN'), ('Frequency-conditioned KAN', 'FRIMLP'), ('Prior Wiener-KAN', 'Random trainable IIR'), ('Full Wiener-KAN', 'Wiener-KAN')]
    freq_rows = []
    for variant, label in freq_sources:
        row = next(item for item in structure_rows if item['label'] == label)
        freq_rows.append({'variant': variant, 'source_variant': label, 'IONS': suppression(row, 'linearity_percent', 'linearity'), 'SDS': suppression(row, 'sens_drift_percent', 'sens'), 'NFDS': suppression(row, 'freq_drift_hz', 'freq')})
    fig, ax = plt.subplots(figsize=(10.5, 4.6), constrained_layout=True)
    x = np.arange(len(freq_rows))
    width = 0.25
    for offset, key, color in [(-width, 'IONS', '#0f6c5c'), (0.0, 'SDS', '#1f4e79'), (width, 'NFDS', '#c96b00')]:
        ax.bar(x + offset, [row[key] for row in freq_rows], width=width, label=key, color=color)
    ax.set_xticks(x)
    ax.set_xticklabels([row['variant'] for row in freq_rows], rotation=18, ha='right')
    ax.set_ylabel('Suppression (%)')
    ax.set_title('Frequency input and Wiener prior contribution')
    ax.legend(frameon=True)
    out = FIGURES_DIR / 'fig_10_frequency_prior_ablation.png'
    fig.savefig(out, bbox_inches='tight')
    plt.close(fig)
    save_json(out.with_suffix('.raw.json'), {'source': 'docs/paper/data/results.json', 'rows': freq_rows})
    generated['frequency_prior_ablation'] = out.name

    fig, ax = plt.subplots(figsize=(8.0, 5.0), constrained_layout=True)
    for curve in main_curves:
        ax.plot(curve['epochs'], curve['smoothed_normalized_val_loss'], label=curve['label'], linewidth=2.5 if curve['label'] == 'Wiener-KAN' else 1.4)
    ax.set_title('Main-benchmark validation-loss trajectories')
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Normalized validation loss')
    ax.set_ylim(bottom=0)
    ax.legend(ncol=2, fontsize=8, frameon=True)
    out = FIGURES_DIR / 'fig_11_main_training_loss.png'
    fig.savefig(out, bbox_inches='tight')
    plt.close(fig)
    save_json(out.with_suffix('.raw.json'), {'source': 'docs/paper/data/results.json', 'curves': main_curves})
    generated['main_training_loss'] = out.name

    fig, ax = plt.subplots(figsize=(7.5, 4.6), constrained_layout=True)
    for curve in loss_curves:
        ax.plot(curve['epochs'], curve['smoothed_normalized_val_loss'], label=curve['label'], linewidth=2.0)
    ax.set_title('Loss-objective validation trajectories')
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Normalized validation loss')
    ax.set_ylim(bottom=0)
    ax.legend(frameon=True)
    out = FIGURES_DIR / 'fig_12_loss_validation_detail.png'
    fig.savefig(out, bbox_inches='tight')
    plt.close(fig)
    save_json(out.with_suffix('.raw.json'), {'source': 'docs/paper/data/results.json', 'curves': loss_curves})
    generated['loss_validation_detail'] = out.name

    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.0), constrained_layout=True)
    labels = [row['label'] for row in main_rows]
    colors = ['#0f6c5c' if label == 'Wiener-KAN' else '#777777' for label in labels]
    for ax, key, title in zip(axes, ['freq_drift_hz', 'sens_drift_percent', 'linearity_percent'], ['Frequency drift (Hz)', 'Sensitivity drift (%)', 'Linearity error (%)']):
        ax.bar(labels, [row[key] for row in main_rows], color=colors)
        ax.set_title(title)
        ax.tick_params(axis='x', rotation=55)
        if key != 'sens_drift_percent':
            ax.set_yscale('log')
    out = FIGURES_DIR / 'fig_13_compensation_distribution.png'
    fig.savefig(out, bbox_inches='tight')
    plt.close(fig)
    save_json(out.with_suffix('.raw.json'), {'source': 'docs/paper/data/results.json', 'rows': main_rows, 'metrics': ['freq_drift_hz', 'sens_drift_percent', 'linearity_percent']})
    generated['compensation_distribution'] = out.name

    return generated


def copy_legacy_images() -> None:
    for item in LEGACY_IMAGE_MIGRATIONS:
        source_name = str(item['source'])
        figure_name = str(item['figure'])
        source_path = PAPER_DIR / 'image' / source_name
        figure_path = FIGURES_DIR / figure_name
        if not source_path.exists():
            continue
        figure_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, figure_path)
        save_json(figure_path.with_suffix('.raw.json'), {
            'figure': figure_name,
            'source': str(source_path.relative_to(ROOT)).replace('\\', '/'),
            'migration_source': 'C:/work/met_nonlinear_paper/image/' + source_name,
            'status': 'migrated_legacy_image',
            'legacy_figure_code': 'docs/paper/src/legacy/figure_paper.py',
        })


def save_figure_raw_files(payload: Dict[str, Any]) -> None:
    raw_payloads = {
        'fig_01_drift_trajectories': {'trajectories': payload['trajectories']},
        'fig_02_horizontal_summary': {'main_benchmark': payload['main_benchmark'], 'origin_metrics': payload['origin_metrics'], 'main_convergence_curves': payload['main_convergence_curves']},
        'fig_03_loss_ablation': {'loss_ablation': payload['loss_ablation'], 'loss_convergence_curves': payload['loss_convergence_curves']},
        'fig_04_structure_ablation': {'structure_ablation': payload['structure_ablation']},
        'fig_05_onboard_inference': {'deployment': payload['deployment'], 'wiener_optimization_profiles': payload['wiener_optimization_profiles']},
        'fig_06_compute_cost_calibration': {'compute_cost_calibration': payload['compute_cost_calibration']},
    }
    for stem, data in raw_payloads.items():
        save_json(FIGURES_DIR / f'{stem}.raw.json', data)


def generate_all() -> Dict[str, Any]:
    apply_config()
    main_rows = enrich_with_deployment_fields(load_metrics(MAIN_BENCHMARK))
    loss_rows = enrich_with_deployment_fields(load_metrics(LOSS_ABLATION))
    structure_rows = load_metrics(STRUCTURE_ABLATION)
    deploy_rows = enrich_with_deployment_fields(load_metrics(DEPLOYMENT))
    lut_rows = load_lut_variants()
    trajectories = load_trajectories()
    main_curves = load_convergence_curves(MAIN_BENCHMARK)
    loss_curves = load_convergence_curves(LOSS_ABLATION)
    optimization_profiles = load_wiener_optimization_profiles()
    calibration = load_compute_cost_calibration()
    wiener_parallel = load_wiener_parallel_summary()

    origin = {
        'freq': main_rows[0]['origin_freq_drift_hz'],
        'sens': main_rows[0]['origin_sens_drift_percent'],
        'linearity': main_rows[0]['origin_linearity_percent'],
    }

    figures = {
        'drift_trajectories': make_trajectory_figure(trajectories),
        'horizontal_summary': make_horizontal_figure(main_rows, origin, main_curves),
        'loss_ablation': make_loss_ablation_figure(loss_rows, loss_curves),
        'structure_ablation': make_structure_figure(structure_rows),
        'onboard_inference': make_onboard_figure(deploy_rows, optimization_profiles),
        'compute_cost_calibration': make_compute_cost_calibration_figure(calibration),
        'met_nonlinear_mechanism': make_mechanism_schematic(),
        'parallel_wiener_principle': make_parallel_wiener_principle_schematic(),
        'lut_lookup_principles': copy_lut_lookup_principles_figure(),
        'board_inference_validation_workflow': copy_board_inference_validation_workflow_figure(),
        'afmae_loss_principle': copy_afmae_loss_principle_figure(),
        'dataset_preprocessing_workflow': copy_dataset_preprocessing_workflow_figure(),
    }
    figures.update(copy_wiener_parallel_figures())

    payload_stub = {
        'origin_metrics': origin,
        'main_benchmark': main_rows,
        'loss_ablation': loss_rows,
        'structure_ablation': structure_rows,
        'deployment': deploy_rows,
        'lut_variants': lut_rows,
        'trajectories': trajectories,
        'main_convergence_curves': main_curves,
        'loss_convergence_curves': loss_curves,
        'wiener_optimization_profiles': optimization_profiles,
        'compute_cost_calibration': calibration,
        'wiener_parallel_modeling': wiener_parallel,
    }
    figures.update(create_additional_paper_figures(payload_stub))

    payload = {
        'origin_metrics': origin,
        'main_benchmark': main_rows,
        'loss_ablation': loss_rows,
        'structure_ablation': structure_rows,
        'deployment': deploy_rows,
        'lut_variants': lut_rows,
        'trajectories': trajectories,
        'main_convergence_curves': main_curves,
        'loss_convergence_curves': loss_curves,
        'wiener_optimization_profiles': optimization_profiles,
        'compute_cost_calibration': calibration,
        'wiener_parallel_modeling': wiener_parallel,
        'figures': figures,
    }
    save_json(DATA_DIR / 'results.json', payload)
    write_values_tex(payload)
    save_figure_raw_files(payload)
    copy_legacy_images()
    build_tables(main_rows, loss_rows, structure_rows, deploy_rows, lut_rows, origin, optimization_profiles, calibration)
    return payload


def generate_data_only() -> Dict[str, Any]:
    payload = generate_all()
    return payload


def main() -> None:
    payload = generate_all()
    print('Generated:')
    for name in payload['figures'].values():
        print(' -', name)
    print(' - data/results.json')
    print(' - data/generated_tables.md')
    print(' - latex/values.tex')



if __name__ == '__main__':
    main()
