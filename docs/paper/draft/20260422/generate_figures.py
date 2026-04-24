from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
DRAFT_DIR = Path(__file__).resolve().parent
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
    out = DRAFT_DIR / 'fig_01_drift_trajectories.png'
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

    out = DRAFT_DIR / 'fig_02_horizontal_summary.png'
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

    out = DRAFT_DIR / 'fig_03_loss_ablation.png'
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
    out = DRAFT_DIR / 'fig_04_structure_ablation.png'
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

    out = DRAFT_DIR / 'fig_05_onboard_inference.png'
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

    out = DRAFT_DIR / 'fig_06_compute_cost_calibration.png'
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
    (DRAFT_DIR / 'generated_tables.md').write_text('\n'.join(note_lines), encoding='utf-8')


def main() -> None:
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
    }

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
        'figures': figures,
    }
    save_json(DRAFT_DIR / 'paper_data.json', payload)
    build_tables(main_rows, loss_rows, structure_rows, deploy_rows, lut_rows, origin, optimization_profiles, calibration)
    print('Generated:')
    for name in figures.values():
        print(' -', name)
    print(' - paper_data.json')
    print(' - generated_tables.md')


if __name__ == '__main__':
    main()
