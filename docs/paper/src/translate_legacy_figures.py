from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from scipy.signal import TransferFunction, freqresp
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.colors as mcolors

try:
    import scienceplots  # noqa: F401
    plt.style.use(['science', 'ieee'])
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[3]
OLD_ROOT = Path(r'C:/work/met_nonlinear_paper')
FIGURES_DIR = ROOT / 'docs' / 'paper' / 'figures'
TMP_DIR = ROOT / 'docs' / 'paper' / 'figures' / '_traced_tmp'
PLOT_PREDICT_CONFIG = {}
sys.path.insert(0, str(ROOT))

from src.visualization.paper_plot_style import (  # noqa: E402
    apply_paper_matplotlib_style,
    paper_plot_style_payload,
    resolve_paper_font_path,
)
from src.visualization.subfigure_montage import PanelSpec, compose_subfigures  # noqa: E402
try:
    from src.figure_visual_audit import (  # type: ignore  # noqa: E402
        VISUAL_AUDIT_KEY,
        audit_image_file,
        audit_matplotlib_figure,
        audit_montage_layout,
        combine_audits,
    )
except ImportError:  # pragma: no cover - direct script execution
    from figure_visual_audit import (  # type: ignore  # noqa: E402
        VISUAL_AUDIT_KEY,
        audit_image_file,
        audit_matplotlib_figure,
        audit_montage_layout,
        combine_audits,
    )

apply_paper_matplotlib_style()
FONT = resolve_paper_font_path() or Path('C:/Windows/Fonts/times.ttf')

red = '#E13723'
blue = '#4B75B1'
green = '#608040'
mycmap = mcolors.LinearSegmentedColormap.from_list(
    'custom_cmap', list(zip([0, 0.5, 1], [red, blue, green])), N=256)

# Traced from C:/work/met_nonlinear_paper/plot_frirnn.py.
zeta_origin = [1.1163184947137288, 0.9308920823940363, 0.8510095448317654, 0.7685737967595504, 0.8067187444545989, 0.8451714035794564, 0.7903564740415322, 0.7876574657115643, 0.8300231338554283, 0.8374533933497949, 0.8978163591146431, 0.9222436200576002, 0.8978193535186013, 0.9664476492867359, 0.9577916907758136, 0.9846056812421196, 0.9878847362511042, 0.9954197021943492, 1.06896297375402, 1.0682539753552884, 1.0933928895319278, 1.0746793126621945, 1.0776564984953971, 1.0248576581755113, 1.0223702680813465]
fn_origin = [35.25644489774976, 34.418797881191345, 34.576789157276444, 36.111533413785246, 38.276754505648206, 40.21396167605361, 42.42183298775108, 45.678584356824736, 47.88017804394588, 50.65866107540093, 53.38874560731289, 56.06783082632998, 58.72969476882683, 61.77044558514168, 64.20690979618865, 67.69896744006212, 70.6823516142407, 74.20466438921513, 78.35843034577556, 81.06726718014916, 85.609351585685, 85.58311848659184, 88.41097423710328, 90.77484971230119, 94.36440906630712]
Sn_origin = [82.3065473476387, 99.07914475866514, 114.29307223621167, 128.37443095532268, 137.1841164013112, 131.01793284609835, 141.558664665535, 162.16894137315018, 162.69133710249986, 168.7557912661652, 161.9693404626006, 163.70321640881903, 167.51232770925992, 162.97358994498575, 158.86450651520792, 165.36634391497495, 169.7496499329651, 173.35645531972125, 174.20481182742802, 176.59669189697144, 179.9380131050336, 179.5040200056095, 181.69406446078153, 185.94818779776816, 190.1925761131536]
magnitudes = np.linspace(0.24, 6.0, 25).tolist()


def write_raw(out: Path, source: str, note: str, extra=None) -> None:
    payload = {'figure': out.name, 'source_trace': source, 'translation_method': 'traced original plotting code with only text labels translated to English', 'note': note}
    payload.update(paper_plot_style_payload())
    if extra:
        payload.update(extra)
    if VISUAL_AUDIT_KEY not in payload:
        payload[VISUAL_AUDIT_KEY] = audit_image_file(out, context=out.name)
    out.with_suffix('.raw.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')


def combine_images_with_labels(image_paths, output_path, space=0.05, label_width_ratio=0.05, labels=None):
    images = [Image.open(path).convert('RGB') for path in image_paths]
    max_height = max(img.height for img in images)
    resized = [img.resize((int(img.width * max_height / img.height), max_height)) if img.height != max_height else img for img in images]
    widths = [img.width for img in resized]
    space_width = int((sum(widths) / len(widths)) * space)
    total_width = sum(widths) + space_width * (len(widths) - 1)
    label_height = int(total_width * label_width_ratio)
    out = Image.new('RGB', (total_width, max_height + label_height), 'white')
    x = 0
    for img in resized:
        out.paste(img, (x, 0))
        x += img.width + space_width
    draw = ImageDraw.Draw(out)
    if labels is None:
        labels = [f'({chr(97+i)})' for i in range(len(resized))]
    font = ImageFont.truetype(str(FONT), int(label_height * 0.7)) if FONT.exists() else ImageFont.load_default()
    x = 0
    for label, img in zip(labels, resized):
        draw.text((x + img.width // 2, max_height + label_height // 2), label, fill='black', font=font, anchor='mm')
        x += img.width + space_width
    out.save(output_path, dpi=(500, 500))


def plot_epoch_io():
    data_dir = OLD_ROOT / 'projects' / 'FRIKANwp' / 'data'
    epochs = [1, 10, 30, 50]
    fig, axes = plt.subplots(len(epochs), 3, figsize=(5.4, 6.2), sharex=True, sharey=True)
    for i, epoch in enumerate(epochs):
        with (data_dir / f'epoch_{epoch}_IO.json').open('r', encoding='utf-8') as f:
            data = json.load(f)
        input_data = data['input']
        output_ori = data['output_ori']
        output_comp = data['output_comp']
        plot_points = 50
        step = max(1, len(input_data) // plot_points)
        input_data = input_data[::step]
        output_ori = output_ori[::step]
        output_comp = output_comp[::step]
        axes[i, 0].set_ylabel(f'Epoch {epoch}', fontsize=8, weight='bold', rotation=0, labelpad=15)
        axes[i, 0].plot(input_data, output_ori, color='C0', lw=1.5)
        axes[i, 1].plot(output_ori, output_comp, color='C2', lw=1.5)
        axes[i, 2].plot(input_data, output_comp, color='C1', lw=1.5)
        for j in range(3):
            axes[i, j].set_xlim(-2.5, 2.5)
            axes[i, j].set_ylim(-2.5, 2.5)
            axes[i, j].set_xticks([-2, -1, 0, 1, 2])
            axes[i, j].set_yticks([-2, -1, 0, 1, 2])
            axes[i, j].tick_params(axis='both', which='minor', bottom=False, left=False, top=False, right=False)
            axes[i, j].tick_params(axis='both', which='major', labelsize=9)
            axes[i, j].grid(True, linestyle='--', alpha=0.5)
    for ax in axes.flatten():
        ax.label_outer()
    plt.tight_layout()
    plt.subplots_adjust(wspace=0.05, hspace=0.05)
    out = FIGURES_DIR / 'kan_neuron_compensation.png'
    fig.savefig(out, dpi=600)
    plt.close(fig)
    write_raw(out, 'C:/work/met_nonlinear_paper/plot_epoch_IO.py + projects/FRIKANwp/data/epoch_*_IO.json', 'English redraw from traced source; column headers and epoch row labels translated while preserving original epoch IO data and plotting logic.')


def preprocess_data(select_per_sample=3, sort_data=False):
    zeta_selected = zeta_origin[::select_per_sample]
    fn_selected = fn_origin[::select_per_sample]
    amplitude_selected = Sn_origin[::select_per_sample]
    magnitudes_selected = magnitudes[::select_per_sample]
    if sort_data:
        idx = np.argsort(fn_selected)
        fn_selected = np.array(fn_selected)[idx]
        zeta_selected = np.array(zeta_selected)[idx]
        amplitude_selected = np.array(amplitude_selected)[idx]
    return fn_selected, zeta_selected, amplitude_selected, magnitudes_selected


def calculate_system_response(fn, amp, zeta, w, delta_linear):
    system = TransferFunction([amp * 4 * np.pi * fn * zeta, 0], [1, 4 * np.pi * fn * zeta, 4 * (np.pi**2) * (fn ** 2)])
    _, H = freqresp(system, w)
    return abs(H) * delta_linear


def calculate_system_response_comp(fn, amp, zeta, w, delta_linear):
    index0 = 2
    zeta0 = zeta_origin[index0]
    fn0 = fn_origin[index0]
    Sn0 = Sn_origin[index0]
    numerator = [1, 4 * np.pi * fn * zeta, 4 * (np.pi**2) * (fn ** 2)]
    numerator = [(Sn0 * zeta0 * fn0)/(amp * zeta * fn) * num for num in numerator]
    denominator = [1, 4 * np.pi * fn0 * zeta0, 4 * (np.pi**2) * (fn0 ** 2)]
    system = TransferFunction(numerator, denominator)
    _, H = freqresp(system, w)
    return abs(H) * delta_linear


def interpolate_response(f, response, cut):
    return f, np.maximum(response, cut)


def log_transform_data(f, z, z_ticks):
    return np.log10(f), np.log10(np.maximum(z, 1e-12)), np.log10(z_ticks)


def set_log_ticks(ax, f_ticks, z_ticks):
    ax.set_xticks(np.log10(f_ticks))
    ax.set_xticklabels(f'{tick}' for tick in f_ticks)
    ax.xaxis.set_minor_locator(plt.NullLocator())
    ax.set_zticks(np.log10(z_ticks))
    ax.set_zticklabels([f'{tick}' for tick in z_ticks])
    ax.zaxis.set_minor_locator(plt.NullLocator())
    ax.yaxis.set_minor_locator(plt.NullLocator())


def plot_3d_slices(ax, f, fn_sorted, z, z_ticks):
    f_log, z_log, z_ticks_log = log_transform_data(f, z, z_ticks)
    z_min_log = min(z_ticks_log)
    z_max_log = max(z_ticks_log)
    ax.set_zlim(z_min_log, z_max_log)
    verts = []
    for ifn, fn in enumerate(fn_sorted):
        response_log = np.nan_to_num(z_log[ifn, :])
        for j in range(len(f_log)-1):
            poly = [(f_log[j], fn, z_min_log), (f_log[j+1], fn, z_min_log), (f_log[j+1], fn, response_log[j+1]), (f_log[j], fn, response_log[j]), (f_log[j], fn, z_min_log)]
            verts.append((poly, ifn))
    verts_sorted = sorted(verts, key=lambda x: x[1])
    colors = [mycmap(i / len(verts_sorted)) for i in range(len(verts_sorted))]
    colors = [(r, g, b, 0.3) for r, g, b, _ in colors]
    colors_fn = [mycmap(i / len(fn_sorted)) for i in range(len(fn_sorted))]
    len_poly_per_fn = len(verts_sorted) // len(fn_sorted)
    for i, (poly, ifn) in enumerate(verts_sorted):
        zorder = (len(fn_sorted) - ifn) * 10000 + i % len_poly_per_fn + 5000
        ax.add_collection3d(Poly3DCollection([poly], facecolors=colors[i], edgecolors='None', zorder=zorder))
    for ifn, fn in enumerate(fn_sorted):
        response_log = np.nan_to_num(z_log[ifn, :])
        zorder = (len(fn_sorted) - ifn) * 10000
        ax.plot(f_log, [fn]*len(f_log), response_log, color=colors_fn[ifn], zorder=zorder, linewidth=1.5, linestyle='-')


def plot_frirnn_panel(ax, process_data_fn, z_ticks, zlabel):
    f = np.logspace(np.log10(10), np.log10(150), 10)
    w = 2 * np.pi * f
    delta_linear = 1.0
    cut = -30
    fn_sorted, zeta_sorted, amplitude_sorted, magnitudes_sorted = preprocess_data(select_per_sample=3, sort_data=False)
    z = np.zeros((len(fn_sorted), len(f)))
    for i in range(len(fn_sorted)):
        z[i, :] = cut
    for i in range(len(fn_sorted)):
        response = process_data_fn(fn_sorted[i], amplitude_sorted[i], zeta_sorted[i], w, delta_linear)
        f_valid, response_interp = interpolate_response(f, response, cut)
        z[i, (f >= f_valid.min()) & (f <= f_valid.max())] = response_interp
    plot_3d_slices(ax, f, magnitudes_sorted, z, z_ticks)
    ax.set_xlabel('Frequency (Hz)', labelpad=8, fontsize=11)
    ax.set_ylabel(r'Magnitude ($\mathrm{m}/\mathrm{s}^{2}$)', labelpad=9, fontsize=11)
    ax.set_zlabel('')
    ax.text2D(-0.07, 0.52, zlabel, transform=ax.transAxes, rotation=90, va='center', ha='center', fontsize=11)
    set_log_ticks(ax, [10, 20, 50, 100, 150], z_ticks)
    ax.set_xlim(np.log10(f.min()), np.log10(f.max()))
    ax.tick_params(axis='x', which='both', pad=2, labelsize=9)
    ax.tick_params(axis='y', which='both', pad=3, labelsize=9)
    ax.tick_params(axis='z', which='both', pad=2, labelsize=9)


def plot_frirnn():
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    original_path = TMP_DIR / 'response_original_temp.png'
    compensated_path = TMP_DIR / 'response_compensated_temp.png'
    fig1 = plt.figure(figsize=(6.8, 5.4))
    ax1 = fig1.add_subplot(111, projection='3d')
    plot_frirnn_panel(ax1, calculate_system_response, z_ticks=[30, 50, 100, 200], zlabel='Sensitivity (V s/m)')
    ax1.view_init(elev=40, azim=-140)
    fig1.subplots_adjust(left=0.16, right=0.97, bottom=0.18, top=0.98)
    audit_original = audit_matplotlib_figure(fig1, context='local_transfer_slices panel (a)')
    fig1.savefig(original_path, dpi=600, bbox_inches='tight', pad_inches=0.22)
    plt.close(fig1)

    fig2 = plt.figure(figsize=(6.8, 5.4))
    ax2 = fig2.add_subplot(111, projection='3d')
    plot_frirnn_panel(ax2, calculate_system_response_comp, z_ticks=[0.2, 0.5, 1, 2], zlabel='Relative gain')
    ax2.view_init(elev=40, azim=-140)
    fig2.subplots_adjust(left=0.15, right=0.97, bottom=0.18, top=0.98)
    audit_compensated = audit_matplotlib_figure(fig2, context='local_transfer_slices panel (b)')
    fig2.savefig(compensated_path, dpi=600, bbox_inches='tight', pad_inches=0.22)
    plt.close(fig2)

    out = FIGURES_DIR / 'local_transfer_slices.png'
    metadata = compose_subfigures(
        [
            PanelSpec(original_path, label='(a)', fit_width=2700, trim_border=80),
            PanelSpec(compensated_path, label='(b)', fit_width=2700, trim_border=80),
        ],
        out,
        layout='horizontal',
        padding=[85, 75, 85, 85],
        gutter=(120, 80),
        label_font_size=62,
        label_font_size_pt=8.0,
        label_reference_width_pt=372.0,
        latex_width_fraction=1.0,
        label_position='outside-top-left',
        label_inset=24,
        label_gap=24,
        label_box=False,
        dpi=(500, 500),
    )
    visual_audit = combine_audits(
        audit_original,
        audit_compensated,
        audit_montage_layout(metadata, context='local_transfer_slices montage'),
        audit_image_file(out, context='local_transfer_slices.png'),
        context='local_transfer_slices.png',
    )
    write_raw(
        out,
        'C:/work/met_nonlinear_paper/plot_frirnn.py embedded zeta/fn/Sn arrays',
        'Axis labels translated; original analytical response equations, sampled magnitudes, camera, and camera-preserved panels recomposed with the unified montage module.',
        {'montage': metadata, VISUAL_AUDIT_KEY: visual_audit},
    )


def plot_predict():
    panel_cfg = PLOT_PREDICT_CONFIG.get('time_panel') if isinstance(PLOT_PREDICT_CONFIG.get('time_panel'), dict) else PLOT_PREDICT_CONFIG
    sys.path.insert(0, str(ROOT / 'src'))
    sys.path.insert(0, str(OLD_ROOT))
    from calibration_analyzer import exam_class
    json_file = OLD_ROOT / 'data' / 'predict_features.json'
    freq_indices = [float(value) for value in panel_cfg.get('freq_indices', [20, 40, 100])]
    magn_indices = [float(value) for value in panel_cfg.get('magn_indices', [0.72, 1.2, 6.0])]
    with json_file.open('r', encoding='utf-8') as f:
        json_data = json.load(f)
    data_dict = {}
    freq_available = set()
    magn_available = set()
    for item in json_data:
        freq_val = item['freq']
        magn_val = item['magn']
        data_dict[(freq_val, magn_val)] = item
        freq_available.add(freq_val)
        magn_available.add(magn_val)
    freq_available = sorted(freq_available)
    magn_available = sorted(magn_available)
    def find_closest(x, values):
        return min(values, key=lambda v: abs(v - x))
    default_figsize = (len(freq_indices) * 2.3, len(magn_indices) * 1.7)
    figsize = panel_cfg.get('figsize', default_figsize)
    if isinstance(figsize, (list, tuple)) and len(figsize) == 2:
        figsize = (float(figsize[0]), float(figsize[1]))
    else:
        figsize = default_figsize
    fig, axes = plt.subplots(len(magn_indices), len(freq_indices), figsize=figsize, sharex=True, sharey=True)
    global_max = 0.0
    t = np.array([0.0])
    line_width = float(panel_cfg.get('line_width', 1.0))
    grid_alpha = float(panel_cfg.get('grid_alpha', 0.5))
    filter_band = panel_cfg.get('filter_band', [10, 128])
    if isinstance(filter_band, (list, tuple)) and len(filter_band) == 2:
        filter_band = (float(filter_band[0]), float(filter_band[1]))
    else:
        filter_band = (10, 128)
    clip_window = panel_cfg.get('clip_window', [1.0, 1.1])
    if isinstance(clip_window, (list, tuple)) and len(clip_window) == 2:
        clip_window = (float(clip_window[0]), float(clip_window[1]))
    else:
        clip_window = (1.0, 1.1)
    legend_cfg = panel_cfg.get('legend') if isinstance(panel_cfg.get('legend'), dict) else {}
    xy_cfg = panel_cfg.get('xy_plot') if isinstance(panel_cfg.get('xy_plot'), dict) else {}
    for i, m_req in enumerate(magn_indices):
        for j, f_req in enumerate(freq_indices):
            ax = axes[i, j]
            f_match = find_closest(f_req, freq_available)
            m_match = find_closest(m_req, magn_available)
            item = data_dict.get((f_match, m_match))
            if item:
                fs = 2000
                x = item['data']['origin']
                y_pred = item['data']['comped']
                y_tgt = item['data']['target']
                x = exam_class.TimeSeries(x, fs).filter('bandpass', filter_band).numpy()
                y_pred = exam_class.TimeSeries(y_pred, fs).filter('bandpass', filter_band).numpy()
                y_tgt = exam_class.TimeSeries(y_tgt, fs).filter('bandpass', filter_band).numpy()
                x = exam_class.TimeSeries(x, fs).clip(start_time=clip_window[0], end_time=clip_window[1]).tonumpy()
                y_pred = exam_class.TimeSeries(y_pred, fs).clip(start_time=clip_window[0], end_time=clip_window[1]).tonumpy()
                y_tgt = exam_class.TimeSeries(y_tgt, fs).clip(start_time=clip_window[0], end_time=clip_window[1]).tonumpy()
                max_y_tgt = max(abs(val) for val in y_tgt) if len(y_tgt) > 0 else 1.0
                if max_y_tgt < 1e-12:
                    max_y_tgt = 1.0
                scale = 1.0 / max_y_tgt
                x = [val * scale for val in x]
                y_pred = [val * scale for val in y_pred]
                y_tgt = [val * scale for val in y_tgt]
                global_max = max(global_max, max(max(abs(val) for val in x), max(abs(val) for val in y_pred), max(abs(val) for val in y_tgt)))
                t = np.arange(len(x)) / fs
                ax.plot(t, x, label='Raw', linewidth=line_width)
                ax.plot(t, y_pred, label='Compensated', linewidth=line_width)
                ax.plot(t, y_tgt, label='Target', linewidth=line_width)
                ax.text(0.5, 0.90, f'{f_match:g} Hz, {m_match:.02f} $\\mathrm{{m}}/\\mathrm{{s}}^2$', ha='center', transform=ax.transAxes)
            else:
                ax.text(0.5, 0.5, f'No data\nf={f_req}, m={m_req}', ha='center', va='center', transform=ax.transAxes)
            ax.grid(True, linestyle='--', alpha=grid_alpha)
            ax.tick_params(axis='both', which='both', direction='in')
            ax.tick_params(axis='x', which='both', top=False)
            ax.tick_params(axis='y', which='both', right=False)
            if 'tick_fontsize' in xy_cfg:
                ax.tick_params(axis='both', which='major', labelsize=float(xy_cfg.get('tick_fontsize', 10.0)))
            if 'tick_pad' in xy_cfg:
                ax.tick_params(axis='both', which='major', pad=float(xy_cfg.get('tick_pad', 3.0)))
            if i == 0 and j == 0:
                ax.legend(
                    loc=str(legend_cfg.get('loc', 'upper center')),
                    bbox_to_anchor=tuple(legend_cfg.get('bbox_to_anchor', [0.95, 1.18])),
                    fontsize=float(legend_cfg.get('fontsize', 10)),
                    frameon=bool(legend_cfg.get('frameon', False)),
                    ncol=int(legend_cfg.get('ncol', 3)),
                )
    for ax in axes.ravel():
        ylim = xy_cfg.get('ylim', [-global_max - 0.5, global_max + 1.4])
        xlim = xy_cfg.get('xlim', [float(t[0] - 0.01), float(t[-1] + 0.01)])
        ax.set_ylim([float(ylim[0]), float(ylim[1])] if isinstance(ylim, (list, tuple)) and len(ylim) == 2 else [-global_max - 0.5, global_max + 1.4])
        ax.set_xlim([float(xlim[0]), float(xlim[1])] if isinstance(xlim, (list, tuple)) and len(xlim) == 2 else [t[0] - 0.01, t[-1] + 0.01])
    label_fontsize = float(xy_cfg.get('label_fontsize', 12))
    fig.text(0.02, 0.5, 'Output (normalized)', va='center', rotation='vertical', fontsize=label_fontsize)
    fig.text(0.5, 0.02, 'Time (s)', ha='center', fontsize=label_fontsize)
    plt.tight_layout()
    plt.subplots_adjust(wspace=0.07, hspace=0.07)
    margins = panel_cfg.get('margins') if isinstance(panel_cfg.get('margins'), dict) else {}
    plt.subplots_adjust(
        left=float(margins.get('left', 0.11)),
        right=float(margins.get('right', 0.97)),
        top=float(margins.get('top', 0.93)),
        bottom=float(margins.get('bottom', 0.11)),
    )
    out = FIGURES_DIR / 'time_domain_outputs.png'
    legacy_out = FIGURES_DIR / 'legacy_37_predict_features.png'
    save_dpi = int(panel_cfg.get('dpi', 600))
    pad_inches = float(panel_cfg.get('pad_inches', 0.1))
    fig.savefig(out, dpi=save_dpi, bbox_inches='tight', pad_inches=pad_inches)
    fig.savefig(legacy_out, dpi=save_dpi, bbox_inches='tight', pad_inches=pad_inches)
    plt.close(fig)
    source = 'C:/work/met_nonlinear_paper/plot_predict.py + data/predict_features.json'
    note = 'English source-level redraw; legend, global axis labels, and panel text translated while preserving nearest-frequency/magnitude selection, filtering, normalization, and panel layout.'
    write_raw(out, source, note)
    write_raw(legacy_out, source, note)


def plot_met_nonlinear_frequency_response():
    data_path = ROOT / 'projects' / '01_LR_STUDY' / 'FRIKANh8u6l6_e1k_lr7e4' / 'data' / 'linear_response.json'
    with data_path.open('r', encoding='utf-8') as f:
        data = json.load(f)
    frequencies = np.array(data['frequencies'], dtype=float)
    magnitudes_arr = np.array(data['magnitudes'], dtype=float)
    gains_origin = [np.array(row, dtype=float) for row in data['gains_origin']]
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    cmap = plt.cm.get_cmap('tab20', len(magnitudes_arr))
    handles = []
    labels = []
    for idx, (magnitude, gain) in enumerate(zip(magnitudes_arr, gains_origin)):
        handle, = ax.loglog(
            frequencies,
            gain,
            color=cmap(idx),
            linewidth=1.35,
            label=rf'{magnitude:.2f} m/s$^2$',
        )
        handles.append(handle)
        labels.append(rf'{magnitude:.2f} m/s$^2$')
    ax.set_xlim(10, 128)
    ax.set_ylim(30, 250)
    ax.set_xlabel('Frequency (Hz)', fontsize=12)
    ax.set_ylabel('Sensitivity (V s/m)', fontsize=12)
    ax.grid(True, which='both', linestyle='--', alpha=0.45)
    ax.tick_params(axis='both', which='major', labelsize=10)
    ax.legend(
        handles,
        labels,
        loc='center left',
        bbox_to_anchor=(1.02, 0.5),
        frameon=False,
        fontsize=8.5,
        ncol=1,
        borderaxespad=0.0,
        handlelength=2.2,
    )
    fig.subplots_adjust(left=0.12, right=0.72, bottom=0.16, top=0.96)
    out = FIGURES_DIR / 'met_nonlinear_frequency_response.png'
    fig.savefig(out, dpi=600, bbox_inches='tight', pad_inches=0.08)
    plt.close(fig)
    write_raw(out, 'projects/01_LR_STUDY/FRIKANh8u6l6_e1k_lr7e4/data/linear_response.json:gains_origin', 'English source-level redraw; legend placed outside the main axes on the right as requested.')


def main():
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plot_epoch_io()
    plot_frirnn()
    plot_met_nonlinear_frequency_response()
    plot_predict()
    print('generated traced Fig.6, Fig.10, Fig.12, Fig.18')


if __name__ == '__main__':
    main()
