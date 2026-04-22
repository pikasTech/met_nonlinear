from __future__ import annotations

import json
import math
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[4]
DRAFT_DIR = Path(__file__).resolve().parent

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'figure.dpi': 160,
    'savefig.dpi': 200,
    'font.size': 10,
    'axes.titlesize': 12,
    'axes.labelsize': 10,
    'legend.fontsize': 9,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
})

PALETTE = {
    'Wiener-KAN': '#0f6c5c',
    'TCN': '#1f4e79',
    '1DCNN': '#c96b00',
    '1DCNN(board-ready)': '#c96b00',
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
}

LINEARITY_INBAND_MAX_HZ = 128.0

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

DEPLOYMENT = [
    ('Wiener-KAN', 'projects/01_LR_STUDY/FRIKANh8u6l6_e1k_lr7e4/data/metrics.json'),
    ('GRU', 'projects/01_LR_STUDY/GRNu16_e1k_puremae/data/metrics.json'),
    ('LSTMTransformer', 'projects/01_LR_STUDY/LSTMTransformeru6_e1k_puremae/data/metrics.json'),
    ('LSTM', 'projects/01_LR_STUDY/LSTMu16_e1k_puremae_r8/data/metrics.json'),
    ('1DCNN(board-ready)', 'projects/05_1DCNN/1DCNNc4u8k20l8_e1k_lr18e3_pd8l8_true/data/metrics.json'),
    ('TCN', 'projects/06_TCN/TCNc4d1248k3_nopd_true_e1k_lr2e3/data/metrics.json'),
]

TRAJECTORY_MODELS = [
    ('Origin', 'projects/01_LR_STUDY/FRIKANh8u6l6_e1k_lr7e4/data/linear_response.json'),
    ('Wiener-KAN', 'projects/01_LR_STUDY/FRIKANh8u6l6_e1k_lr7e4/data/linear_response.json'),
    ('TCN', 'projects/06_TCN/TCNc4d1248k3_nopd_true_e1k_lr2e3/data/linear_response.json'),
    ('1DCNN', 'projects/05_1DCNN/1DCNNc4u8k20l8_e1k_lr18e4_pd8l2_d001_cvtanh_true/data/linear_response.json'),
    ('LSTM', 'projects/01_LR_STUDY/LSTMu16_e1k_puremae_r8/data/linear_response.json'),
]

BUILD_PATTERN = re.compile(r'Program Size: Code=(\d+) RO-data=(\d+) RW-data=(\d+) ZI-data=(\d+)')


def load_json(rel_path: str):
    with open(ROOT / rel_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_metrics(rows):
    data = []
    for label, rel_path in rows:
        m = load_json(rel_path)
        linearity_rel_path = str(Path(rel_path).with_name('linearity_by_frequency.json')).replace('\\', '/')
        linearity_summary = compute_inband_linearity_summary(linearity_rel_path, LINEARITY_INBAND_MAX_HZ)
        data.append({
            'label': label,
            'project_name': m['project_name'],
            'metrics_path': rel_path,
            'freq_drift_hz': float(m['freq_drift_hz']),
            'sens_drift_percent': float(m['sens_drift_percent']),
            'linearity_percent': float(linearity_summary['comped_mean_percent']),
            'compute_cost': float(m['compute_cost']),
            'total_params': int(m['total_params']),
            'val_mae': float(m['val_mae']),
            'val_afmae': float(m['val_afmae']),
            'epochs': int(m['epochs']),
            'lr': float(m['lr']),
            'loss_function': m['loss_function'],
            'board_qemu_mae': m.get('board_qemu_mae'),
            'board_keil_mae': m.get('board_keil_mae'),
            'board_keil_speed': m.get('board_keil_speed'),
            'board_inference_ep_path': m.get('board_inference_ep_path'),
            'origin_freq_drift_hz': float(m['metric_details']['natural_frequency_drift_origin']['drift']),
            'origin_sens_drift_percent': float(m['metric_details']['sensitivity_drift_origin']['drift']),
            'origin_linearity_percent': float(linearity_summary['origin_mean_percent']),
            'linearity_band_max_hz': float(linearity_summary['band_max_hz']),
            'linearity_band_count': int(linearity_summary['frequency_count']),
            'linearity_band_frequencies_hz': linearity_summary['frequencies_hz'],
            'linearity_full_frequency_count': int(linearity_summary['full_frequency_count']),
            'linearity_full_frequencies_hz': linearity_summary['full_frequencies_hz'],
        })
    return data


def compute_inband_linearity_summary(rel_path: str, band_max_hz: float):
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


def natural_frequency_from_fit_params(fit_params):
    return [math.sqrt(max(row[1], 0.0)) / (2.0 * math.pi) for row in fit_params]


def interpolate_sensitivity_at_100hz(frequencies, gains):
    return [float(np.interp(100.0, frequencies, row)) for row in gains]


def load_trajectories():
    result = {}
    for label, rel_path in TRAJECTORY_MODELS:
        payload = load_json(rel_path)
        magnitudes = payload['magnitudes']
        frequencies = payload['frequencies']
        if label == 'Origin':
            fn = natural_frequency_from_fit_params(payload['fit_params_origin'])
            sens = interpolate_sensitivity_at_100hz(frequencies, payload['gains_origin'])
        else:
            fn = natural_frequency_from_fit_params(payload['fit_params_comped'])
            sens = interpolate_sensitivity_at_100hz(frequencies, payload['gains_comped'])
        result[label] = {
            'magnitudes': magnitudes,
            'natural_frequency_hz': fn,
            'sensitivity_100hz': sens,
        }
    return result


def percent_suppression(origin, value):
    return 100.0 * (origin - value) / origin


def normalize_inverse(values):
    arr = np.asarray(values, dtype=float)
    vmin = arr.min()
    vmax = arr.max()
    if math.isclose(vmin, vmax):
        return np.ones_like(arr)
    return 1.0 - (arr - vmin) / (vmax - vmin)


def parse_build_sizes(metrics_entry):
    ep = metrics_entry.get('board_inference_ep_path')
    if not ep:
        return None
    build_path = ROOT / ep / 'keil_project' / 'MDK-ARM' / 'output' / 'build_output_MET405.txt'
    if not build_path.exists():
        return None
    text = build_path.read_text(encoding='utf-8')
    match = BUILD_PATTERN.search(text)
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


def add_deployment_sizes(rows):
    enriched = []
    for row in rows:
        build = parse_build_sizes(row)
        row = dict(row)
        if build:
            row.update(build)
        enriched.append(row)
    return enriched


def save_json(path: Path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')


def make_trajectory_figure(trajectories):
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8), constrained_layout=True)
    for label, series in trajectories.items():
        color = PALETTE.get(label, '#444444')
        linestyle = '--' if label == 'Origin' else '-'
        linewidth = 2.2 if label == 'Wiener-KAN' else 1.8
        axes[0].plot(series['magnitudes'], series['natural_frequency_hz'], label=label, color=color, linestyle=linestyle, linewidth=linewidth)
        axes[1].plot(series['magnitudes'], series['sensitivity_100hz'], label=label, color=color, linestyle=linestyle, linewidth=linewidth)

    axes[0].set_title('(a) Natural-frequency trajectory')
    axes[0].set_xlabel('Magnitude (m/s^2)')
    axes[0].set_ylabel('Natural frequency (Hz)')
    axes[1].set_title('(b) Sensitivity at 100 Hz')
    axes[1].set_xlabel('Magnitude (m/s^2)')
    axes[1].set_ylabel('Sensitivity (%)')
    axes[1].legend(ncol=3, loc='upper center', bbox_to_anchor=(0.5, 1.18), frameon=True)
    out = DRAFT_DIR / 'fig_01_drift_trajectories.png'
    fig.savefig(out, bbox_inches='tight')
    plt.close(fig)
    return out.name


def make_horizontal_figure(rows, origin):
    labels = [r['label'] for r in rows]
    freq_sup = [percent_suppression(origin['freq'], r['freq_drift_hz']) for r in rows]
    sens_sup = [percent_suppression(origin['sens'], r['sens_drift_percent']) for r in rows]
    lin_sup = [percent_suppression(origin['linearity'], r['linearity_percent']) for r in rows]

    radar_axes = ['Freq stability', 'Sens stability', 'In-band linearity', 'Compute eff.', 'Param eff.']
    radar_values = np.column_stack([
        normalize_inverse([r['freq_drift_hz'] for r in rows]),
        normalize_inverse([r['sens_drift_percent'] for r in rows]),
        normalize_inverse([r['linearity_percent'] for r in rows]),
        normalize_inverse([r['compute_cost'] for r in rows]),
        normalize_inverse([r['total_params'] for r in rows]),
    ])

    fig = plt.figure(figsize=(13, 5.5), constrained_layout=True)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.2, 1.0])
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
    ax_bar.set_ylim(0, max(max(freq_sup), max(sens_sup), max(lin_sup)) * 1.15)
    ax_bar.legend(loc='upper left', frameon=True)

    ax_radar = fig.add_subplot(gs[0, 1], polar=True)
    angles = np.linspace(0, 2 * np.pi, len(radar_axes), endpoint=False).tolist()
    angles += angles[:1]
    ax_radar.set_theta_offset(np.pi / 2)
    ax_radar.set_theta_direction(-1)
    ax_radar.set_thetagrids(np.degrees(angles[:-1]), radar_axes)
    ax_radar.set_ylim(0, 1)
    ax_radar.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax_radar.set_yticklabels(['0.25', '0.50', '0.75', '1.00'])
    ax_radar.set_title('(b) Normalized comprehensive profile', y=1.12)
    for row, values in zip(rows, radar_values):
        trace = values.tolist() + values[:1].tolist()
        color = PALETTE.get(row['label'], '#444444')
        lw = 2.0 if row['label'] == 'Wiener-KAN' else 1.2
        alpha = 0.10 if row['label'] == 'Wiener-KAN' else 0.05
        ax_radar.plot(angles, trace, color=color, linewidth=lw, label=row['label'])
        if row['label'] == 'Wiener-KAN':
            ax_radar.fill(angles, trace, color=color, alpha=alpha)
    ax_radar.legend(loc='upper center', bbox_to_anchor=(0.5, -0.16), ncol=3, frameon=True)

    out = DRAFT_DIR / 'fig_02_horizontal_summary.png'
    fig.savefig(out, bbox_inches='tight')
    plt.close(fig)
    return out.name


def make_loss_figure(rows):
    fig, axes = plt.subplots(2, 2, figsize=(12.5, 8), constrained_layout=True)
    metrics = [
        ('freq_drift_hz', 'Freq drift (Hz)', False),
        ('sens_drift_percent', 'Sensitivity drift (%)', False),
        ('linearity_percent', 'In-band linearity error (%)', False),
        ('val_mae', 'Validation MAE / AFMAE', False),
    ]
    labels = [r['label'] for r in rows]
    colors = [PALETTE[r['label']] for r in rows]
    for ax, (key, title, use_log) in zip(axes.flatten(), metrics):
        if key == 'val_mae':
            x = np.arange(len(rows))
            width = 0.36
            ax.bar(x - width / 2, [r['val_mae'] for r in rows], width=width, color='#0f6c5c', label='Val MAE')
            ax.bar(x + width / 2, [r['val_afmae'] for r in rows], width=width, color='#1f4e79', label='Val AFMAE')
            ax.set_xticks(x)
            ax.set_xticklabels(labels)
            ax.legend(frameon=True)
        else:
            ax.bar(labels, [r[key] for r in rows], color=colors)
        ax.set_title(title)
        if use_log:
            ax.set_yscale('log')
        ax.tick_params(axis='x', rotation=15)
    out = DRAFT_DIR / 'fig_03_loss_ablation.png'
    fig.savefig(out, bbox_inches='tight')
    plt.close(fig)
    return out.name


def make_structure_figure(rows):
    fig, axes = plt.subplots(2, 2, figsize=(13, 8.5), constrained_layout=True)
    labels = [r['label'] for r in rows]
    colors = [PALETTE[r['label']] for r in rows]
    specs = [
        ('freq_drift_hz', 'Freq drift (Hz)', True),
        ('sens_drift_percent', 'Sensitivity drift (%)', False),
        ('linearity_percent', 'In-band linearity error (%)', True),
        ('compute_cost', 'Compute cost (weighted units)', False),
    ]
    for ax, (key, title, use_log) in zip(axes.flatten(), specs):
        ax.bar(labels, [r[key] for r in rows], color=colors)
        ax.set_title(title)
        if use_log:
            ax.set_yscale('log')
        ax.tick_params(axis='x', rotation=25)
    out = DRAFT_DIR / 'fig_04_structure_ablation.png'
    fig.savefig(out, bbox_inches='tight')
    plt.close(fig)
    return out.name


def make_deployment_figure(rows):
    fig, axes = plt.subplots(2, 2, figsize=(13, 8.5), constrained_layout=True)
    labels = [r['label'] for r in rows]
    colors = [PALETTE.get(r['label'], '#444444') for r in rows]

    axes[0, 0].bar(labels, [r['board_qemu_mae'] for r in rows], color=colors)
    axes[0, 0].set_title('QEMU-MAE')
    axes[0, 0].set_yscale('log')
    axes[0, 0].tick_params(axis='x', rotation=25)

    axes[0, 1].bar(labels, [r['board_keil_mae'] for r in rows], color=colors)
    axes[0, 1].set_title('KEIL-MAE')
    axes[0, 1].set_yscale('log')
    axes[0, 1].tick_params(axis='x', rotation=25)

    axes[1, 0].bar(labels, [r['board_keil_speed'] for r in rows], color=colors)
    axes[1, 0].set_title('Keil latency (ms/point)')
    axes[1, 0].tick_params(axis='x', rotation=25)

    x = np.arange(len(rows))
    width = 0.36
    axes[1, 1].bar(x - width / 2, [r['flash_bytes'] / 1024.0 for r in rows], width=width, color='#1f4e79', label='Flash (KB)')
    axes[1, 1].bar(x + width / 2, [r['ram_bytes'] / 1024.0 for r in rows], width=width, color='#c96b00', label='RAM (KB)')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(labels, rotation=25, ha='right')
    axes[1, 1].set_title('MCU resource footprint')
    axes[1, 1].legend(frameon=True)

    out = DRAFT_DIR / 'fig_05_edge_tradeoff.png'
    fig.savefig(out, bbox_inches='tight')
    plt.close(fig)
    return out.name


def make_table(lines, headers):
    rows = ['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---'] * len(headers)) + ' |']
    for line in lines:
        rows.append('| ' + ' | '.join(line) + ' |')
    return '\n'.join(rows)


def build_tables(main_rows, loss_rows, structure_rows, deploy_rows, origin):
    table_main = make_table([
        [
            r['label'],
            f"{r['freq_drift_hz']:.2f}",
            f"{r['sens_drift_percent']:.2f}",
            f"{r['linearity_percent']:.2f}",
            f"{r['compute_cost']:.0f}",
            f"{r['total_params']}",
        ]
        for r in main_rows
    ], ['Model', 'Freq Drift (Hz)', 'Sens Drift (%)', 'Linearity (in-band, %)', 'Compute Cost', 'Params'])

    table_loss = make_table([
        [
            r['label'],
            r['loss_function'],
            f"{r['freq_drift_hz']:.2f}",
            f"{r['sens_drift_percent']:.2f}",
            f"{r['linearity_percent']:.2f}",
            f"{r['val_mae']:.4f}",
            f"{r['val_afmae']:.4f}",
        ]
        for r in loss_rows
    ], ['Variant', 'Active loss', 'Freq Drift (Hz)', 'Sens Drift (%)', 'Linearity (in-band, %)', 'Val MAE', 'Val AFMAE'])

    table_structure = make_table([
        [
            r['label'],
            f"{r['freq_drift_hz']:.2f}" if r['freq_drift_hz'] < 1e4 else f"{r['freq_drift_hz']:.2e}",
            f"{r['sens_drift_percent']:.2f}",
            f"{r['linearity_percent']:.2f}" if r['linearity_percent'] < 1e4 else f"{r['linearity_percent']:.2e}",
            f"{r['compute_cost']:.0f}",
        ]
        for r in structure_rows
    ], ['Variant', 'Freq Drift (Hz)', 'Sens Drift (%)', 'Linearity (in-band, %)', 'Compute Cost'])

    band_freqs = ', '.join(f"{int(v) if float(v).is_integer() else v:g}" for v in main_rows[0]['linearity_band_frequencies_hz'])
    band_desc = (
        f"<= {main_rows[0]['linearity_band_max_hz']:.0f} Hz, "
        f"{main_rows[0]['linearity_band_count']} sampled points "
        f"({band_freqs} Hz)"
    )
    full_grid_desc = (
        f"{main_rows[0]['linearity_full_frequencies_hz'][0]:.0f}-"
        f"{main_rows[0]['linearity_full_frequencies_hz'][-1]:.0f} Hz, "
        f"{main_rows[0]['linearity_full_frequency_count']} sampled points"
    )

    table_deploy = make_table([
        [
            r['label'],
            f"{r['board_qemu_mae']:.3e}",
            f"{r['board_keil_mae']:.3e}",
            f"{r['board_keil_speed']:.3f}",
            f"{r['flash_bytes'] / 1024.0:.1f}",
            f"{r['ram_bytes'] / 1024.0:.1f}",
        ]
        for r in deploy_rows
    ], ['Model', 'QEMU-MAE', 'KEIL-MAE', 'KEIL speed (ms/point)', 'Flash (KB)', 'RAM (KB)'])

    protocol_table = make_table([
        ['Sensor sample', 'MTSS-1001'],
        ['Environment', '25 C'],
        ['Frequency grid (saved evaluation)', full_grid_desc],
        ['Magnitude sweep', '0.24-6.0 m/s^2, 25 levels'],
        ['Sequence duration', '4.0 s'],
        ['Sampling rate', '2000 Hz'],
        ['Window count', '8000 sequences'],
        ['Reference sensitivity point', '100 Hz'],
        ['Linearity band (this draft)', band_desc],
    ], ['Item', 'Value'])

    note_lines = [
        '# Machine-readable tables for the 20260422 draft',
        '',
        '## Protocol',
        protocol_table,
        '',
        '## Main benchmark',
        table_main,
        '',
        f"Origin metrics: Freq Drift = {origin['freq']:.2f} Hz, Sens Drift = {origin['sens']:.2f} %, In-band linearity = {origin['linearity']:.2f} %.",
        '',
        '## Loss ablation',
        table_loss,
        '',
        '## Structure ablation',
        table_structure,
        '',
        '## Deployment subset',
        table_deploy,
    ]
    (DRAFT_DIR / 'generated_tables.md').write_text('\n'.join(note_lines), encoding='utf-8')


def main():
    main_rows = load_metrics(MAIN_BENCHMARK)
    loss_rows = load_metrics(LOSS_ABLATION)
    structure_rows = load_metrics(STRUCTURE_ABLATION)
    deploy_rows = add_deployment_sizes(load_metrics(DEPLOYMENT))
    trajectories = load_trajectories()

    origin = {
        'freq': main_rows[0]['origin_freq_drift_hz'],
        'sens': main_rows[0]['origin_sens_drift_percent'],
        'linearity': main_rows[0]['origin_linearity_percent'],
    }

    figures = {
        'drift_trajectories': make_trajectory_figure(trajectories),
        'horizontal_summary': make_horizontal_figure(main_rows, origin),
        'loss_ablation': make_loss_figure(loss_rows),
        'structure_ablation': make_structure_figure(structure_rows),
        'edge_tradeoff': make_deployment_figure(deploy_rows),
    }

    payload = {
        'origin_metrics': origin,
        'main_benchmark': main_rows,
        'loss_ablation': loss_rows,
        'structure_ablation': structure_rows,
        'deployment': deploy_rows,
        'trajectories': trajectories,
        'figures': figures,
    }
    save_json(DRAFT_DIR / 'paper_data.json', payload)
    build_tables(main_rows, loss_rows, structure_rows, deploy_rows, origin)
    print('Generated:')
    for name in figures.values():
        print(' -', name)
    print(' - paper_data.json')
    print(' - generated_tables.md')


if __name__ == '__main__':
    main()
