import argparse
import copy
import json
import math
import os
import re
import shutil
from concurrent.futures import ProcessPoolExecutor, as_completed
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

np.math = math

try:
    from calibration_analyzer import exam_class, exam_process
    from calibration_analyzer.exam_class import System, TimeSeries
except ModuleNotFoundError:
    # Keep the module runnable as a standalone script from src/visualization.
    import sys
    _SRC_ROOT = Path(__file__).resolve().parents[1]
    if str(_SRC_ROOT) not in sys.path:
        sys.path.insert(0, str(_SRC_ROOT))
    from calibration_analyzer import exam_class, exam_process
    from calibration_analyzer.exam_class import System, TimeSeries


DATA_DIR = "data"
CONFIG_FILE = "config.json"
PREPROCESSED_FILE = os.path.join(DATA_DIR, "preprocessed_data.json")
RESULTS_FILE = os.path.join(DATA_DIR, "results.json")
DEFAULT_DATA_DIR = os.path.join(DATA_DIR, "raw")

DEFAULT_CONFIG = {
    "amplitudes": [0.5, 1.257, 3.162, 7.953, 20.0],
    "time_length": 2.5,
    "fs": 20000,
    "f_range": [5, 200],
    "points": 50,
    "branch_indices": [0, -1],
    "fh_branch_names": ["fgm0d12", "fgm6d0"],
    "amplitudes_from_preprocessed": False,
    "magnitude_scale": 1.0,
    "nonlinear_scale": 4.0,
    "fh_kx": [1.0, 1.2, 1.4, 1.6, 1.8, 2.0],
    "fh_ky0": [1, 1, 1, 1, 1, 1],
    "fh_ky1": [0, 0, 0, 0, 0, 0],
    "fh_mode": "proportional",
    "fgm0d12": {"c": 0, "w": 1, "enabled": False},
    "fgm6d0": {"c": 1, "w": 1, "enabled": False},
}


def load_config(config_path=CONFIG_FILE):
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        config_dir = os.path.dirname(config_path)
        if config_dir:
            os.makedirs(config_dir, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
        print(f"Created default config at {config_path}")
        return DEFAULT_CONFIG


class DataInfo:
    def __init__(self, file_path, magnitude):
        self.file_path = file_path
        self.magnitude = magnitude


def find_data_info(directory):
    data_info_list = []
    pattern = re.compile(r".*震级(\d+\.\d+)_analyze\.json$")
    for root, _, files in os.walk(directory):
        for file_name in files:
            if not file_name.endswith("analyze.json"):
                continue
            match = pattern.match(file_name)
            if not match:
                continue
            magnitude = float(match.group(1))
            full_path = os.path.join(root, file_name)
            data_info_list.append(DataInfo(full_path, magnitude))
    data_info_list.sort(key=lambda item: item.magnitude)
    return data_info_list


class PiecewiseMap:
    def __init__(self, xn, yn):
        self.xn = xn
        self.yn = yn
        self.k = [(yn[i + 1] - yn[i]) / (xn[i + 1] - xn[i]) for i in range(len(xn) - 1)]
        self.b = [yn[i] - self.k[i] * xn[i] for i in range(len(self.k))]

    @classmethod
    def from_xk(cls, x, k):
        x_all = [float(xi) for xi in x]
        k_all = [float(ki) for ki in k]
        if len(x_all) != len(k_all):
            raise ValueError("x and k must have the same length")
        x = []
        k = []
        for xi, ki in zip(x_all, k_all):
            if xi >= 0:
                x.append(xi)
                k.append(ki)
        if not x:
            raise ValueError("x must contain at least one non-negative sample")
        y = [0.0]
        if 0.0 not in x:
            for i, xi in enumerate(x):
                if xi > 0:
                    x.insert(i, 0.0)
                    k = list(k[:i]) + [k[i-1] if i > 0 else 0.0] + list(k[i:])
                    break
        for i in range(1, len(x)):
            y.append(y[i - 1] + k[i - 1] * (x[i] - x[i - 1]))
        return cls(x, y)

    @classmethod
    def from_triangle(cls, c, l):
        xn = [c - l, c, c + l]
        yn = [0.0, 1.0, 0.0]
        return cls(xn, yn)

    @classmethod
    def from_cw_triangle(cls, c, w, n_k=9, x_top=None, x_btn=None, top_k=1.0):
        x_list = np.linspace(c - w, c + w, n_k).tolist()
        k_list = []
        plateau_k = None
        for i, xi in enumerate(x_list):
            if xi <= c:
                current_k = top_k * (xi - (c - w)) / w
            else:
                current_k = top_k * (1 - (xi - c) / w)
            if x_top is not None and plateau_k is None and xi >= x_top:
                plateau_k = current_k
            if x_btn is not None and xi <= x_btn:
                current_k = top_k
            if x_top is not None and xi >= x_top and plateau_k is not None:
                current_k = plateau_k
            k_list.append(current_k)
        return np.array(x_list), np.array(k_list)

    def __call__(self, samples):
        x = np.asarray(samples)
        y = np.zeros_like(x, dtype=float)
        x_pos = np.abs(x)
        for i in range(len(self.k)):
            left = self.xn[i]
            right = self.xn[i + 1]
            mask = (x_pos >= left) & (x_pos < right)
            y[mask] = self.k[i] * x_pos[mask] + self.b[i]
        mask = x_pos >= self.xn[-1]
        y[mask] = self.k[-1] * x_pos[mask] + self.b[-1]
        y = np.where(x < 0, -y, y)
        return y

    def to_dict(self):
        return {"xn": self.xn, "yn": self.yn}

    @classmethod
    def from_dict(cls, d):
        return cls(d["xn"], d["yn"])


def _normalize_index(index, length):
    return index if index >= 0 else length + index


def _get_branch_names(config, branch_count):
    branch_names = list(config.get("fh_branch_names", []))
    if len(branch_names) >= branch_count:
        return branch_names[:branch_count]
    fallback = [f"fh{i}" for i in range(branch_count)]
    if not branch_names:
        return fallback
    return branch_names + fallback[len(branch_names):]


def _get_curve_points(config, branch_name, fallback_index=None):
    curve_cfg = config.get(branch_name, {})
    if not curve_cfg and fallback_index is not None:
        legacy_key = f"fh_cw{fallback_index}"
        curve_cfg = config.get(legacy_key, {})
    if curve_cfg.get("enabled", False):
        c_value = curve_cfg["c"]
        w_value = curve_cfg["w"]
        x_top = curve_cfg.get("x_top")
        x_btn = curve_cfg.get("x_btn")
        top_k = curve_cfg.get("top_k", 1.0)
        n_k = int(curve_cfg.get("n_k", config.get("fh_n_k", 9)))
        if n_k < 2:
            raise ValueError(f"n_k must be >= 2 for branch {branch_name}, got {n_k}")
        fh_kx, fh_ky = PiecewiseMap.from_cw_triangle(c_value, w_value, n_k=n_k, x_top=x_top, x_btn=x_btn, top_k=top_k)
    else:
        fh_kx = config["fh_kx"]
        legacy_index = 0 if fallback_index is None else fallback_index
        fh_ky = config[f"fh_ky{legacy_index}"]
        c_value = None
        w_value = None
        x_top = None
        x_btn = None
        top_k = None
    return {
        "name": branch_name,
        "config": {
            "c": c_value,
            "w": w_value,
            "x_top": x_top,
            "x_btn": x_btn,
            "top_k": top_k,
            "n_k": curve_cfg.get("n_k", config.get("fh_n_k", 9)),
            "enabled": curve_cfg.get("enabled", False),
        },
        "fh_kx": fh_kx,
        "fh_ky": fh_ky,
    }


class PureLNRNN:
    def __init__(self, systems, nonlinear_functions, hammerstein=False, nonlinear_scale=1.0, legacy_frequency_response=False, equal_acceleration=False, fh_mode="proportional"):
        self.systems = systems
        self.nonlinear_functions = nonlinear_functions
        self.hammerstein = hammerstein
        self.nonlinear_scale = nonlinear_scale
        self.legacy_frequency_response = legacy_frequency_response
        self.equal_acceleration = equal_acceleration
        self.fh_mode = fh_mode

    def _apply_nonlinear(self, nonlinear_function, samples):
        if self.fh_mode == "derivative":
            fs = getattr(self, "_fs", 20000)
            derivative = np.zeros_like(samples)
            derivative[1:] = (samples[1:] - samples[:-1]) * fs
            derivative[0] = derivative[1]
            scaled = nonlinear_function(derivative * self.nonlinear_scale)
            return scaled / self.nonlinear_scale
        else:
            scaled = nonlinear_function(samples * self.nonlinear_scale)
            return scaled / self.nonlinear_scale

    def time_response(self, input_sequence):
        outputs = []
        for system, nonlinear_function in zip(self.systems, self.nonlinear_functions):
            if self.hammerstein:
                branch_input = TimeSeries(self._apply_nonlinear(nonlinear_function, input_sequence.samples), input_sequence.fs)
                branch_output = system.time_response(branch_input)
            else:
                system_output = system.time_response(input_sequence)
                branch_output = TimeSeries(self._apply_nonlinear(nonlinear_function, system_output.samples), input_sequence.fs)
            outputs.append(branch_output.samples)
        total_output = np.sum(outputs, axis=0)
        return TimeSeries(total_output, input_sequence.fs)

    def frequency_response_system(self, fs=20000, time_length=1, f_range=(5, 200), points=50, amplitude=1.0, use_parallel=False):
        self._fs = fs
        del use_parallel
        f_list = np.logspace(np.log10(f_range[0]), np.log10(f_range[1]), points)
        gain = []
        phase = []
        for f_sin in f_list:
            period_time = 1.0 / f_sin
            total_time = max(time_length, 8.0 * period_time)
            adjusted_amplitude = amplitude
            if self.equal_acceleration:
                adjusted_amplitude = amplitude / (2 * np.pi * f_sin)
            input_sequence = TimeSeries.fromSin(
                adjusted_amplitude,
                f_sin,
                fs,
                total_time,
                fade_in=0.3,
                fade_out=0.0,
            )
            output_sequence = self.time_response(input_sequence)
            fade_in_samples = int(0.3 * len(output_sequence.samples))
            input_trimmed = input_sequence.samples[fade_in_samples:]
            output_trimmed = output_sequence.samples[fade_in_samples:]
            input_gain = exam_class.amplitude_detection(input_trimmed, fs, f_sin)
            output_gain = exam_class.amplitude_detection(output_trimmed, fs, f_sin)
            gain_value = output_gain / input_gain
            if self.legacy_frequency_response:
                phase_value = 0.0
            else:
                phase_value = exam_class.phase_detection(output_trimmed, input_trimmed, fs, f_sin)
            gain.append(gain_value)
            phase.append(phase_value)
        return System(f=f_list, gain=gain, phase=phase)

    @classmethod
    def from_preprocessed(cls, preprocessed, config):
        s = System.s
        all_systems = preprocessed["all_systems"]
        systems = []
        nonlinear_functions = []
        branch_names = _get_branch_names(config, len(preprocessed["branch_indices"]))

        for branch_position, raw_index in enumerate(preprocessed["branch_indices"]):
            system_info = all_systems[raw_index]
            fit_params = system_info["fit_params"]
            A_value, B_value, C_value = fit_params
            symbol = A_value * s * (1 / (s**2 + C_value * s + B_value))
            system = System.fromSymbol(symbol, f=preprocessed["f_range"])
            system.fit_params = fit_params
            system.branch_name = branch_names[branch_position]
            system.branch_magnitude = system_info["magnitude"]
            systems.append(system)

            curve_info = _get_curve_points(config, branch_names[branch_position], fallback_index=branch_position)
            nonlinear_function = PiecewiseMap.from_xk(curve_info["fh_kx"], curve_info["fh_ky"])
            nonlinear_function.branch_name = branch_names[branch_position]
            nonlinear_functions.append(nonlinear_function)

        return cls(
            systems,
            nonlinear_functions,
            hammerstein=preprocessed.get("hammerstein", False),
            nonlinear_scale=preprocessed["nonlinear_scale"],
            legacy_frequency_response=preprocessed.get("legacy_frequency_response", True),
            equal_acceleration=preprocessed.get("equal_acceleration", True),
            fh_mode=preprocessed.get("fh_mode", "proportional"),
        )


def _build_data_lnrnn(data_dir, branch_indices=None):
    data_info_list = find_data_info(data_dir)
    if not data_info_list:
        raise FileNotFoundError(f"No analyze files found under {data_dir}")
    if branch_indices is None:
        branch_indices = (0, len(data_info_list) - 1)
    i0, i1 = branch_indices
    ws_min = System.loadFile(data_info_list[i0].file_path)
    ws_min_fit = exam_process.ws_system_fit(ws_min, k=1.0, freq_range=(5, 200))
    ws_max = System.loadFile(data_info_list[i1].file_path)
    ws_max_fit = exam_process.ws_system_fit(ws_max, k=1.0, freq_range=(5, 200))
    fh0 = PiecewiseMap.from_xk([1.0, 1.2, 1.4, 1.6, 1.8, 2.0], [1, 0.8, 0.6, 0.4, 0.2, 0.0])
    fh1 = PiecewiseMap.from_xk([1.0, 1.2, 1.4, 1.6, 1.8, 2.0], [0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    return PureLNRNN(
        [ws_min_fit, ws_max_fit],
        [fh0, fh1],
        hammerstein=False,
        nonlinear_scale=4.0,
        legacy_frequency_response=True,
        equal_acceleration=True,
    )


def step1_read_and_process(data_dir=DEFAULT_DATA_DIR, output_path=PREPROCESSED_FILE, config_path=CONFIG_FILE):
    config = load_config(config_path)
    data_info_list = find_data_info(data_dir)
    if not data_info_list:
        raise FileNotFoundError(f"No analyze files found under {data_dir}")

    magnitude_scale = config.get("magnitude_scale", 1.0)
    all_fitted = []
    for info in data_info_list:
        ws = System.loadFile(info.file_path)
        ws_fit = exam_process.ws_system_fit(ws, k=1.0, freq_range=(5, 200))
        scaled_magnitude = info.magnitude * magnitude_scale
        all_fitted.append({
            "magnitude": scaled_magnitude,
            "fit_params": list(ws_fit.fit_params),
        })
        print(f"  fitted magnitude={scaled_magnitude:.2f}")

    branch_indices = tuple(config["branch_indices"])
    f_range = config["f_range"]

    preprocessed = {
        "all_systems": all_fitted,
        "branch_indices": list(branch_indices),
        "nonlinear_scale": config.get("nonlinear_scale", 4.0),
        "hammerstein": config.get("hammerstein", False),
        "legacy_frequency_response": config.get("legacy_frequency_response", True),
        "equal_acceleration": config.get("equal_acceleration", True),
        "fh_mode": config.get("fh_mode", "proportional"),
        "magnitude_scale": magnitude_scale,
        "f_range": f_range,
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(preprocessed, f, indent=2, ensure_ascii=False)
    print(f"Step 1 complete: saved to {output_path}")
    return preprocessed


def step2_simulate(input_path=PREPROCESSED_FILE, output_path=RESULTS_FILE, config_path=CONFIG_FILE):
    config = load_config(config_path)
    with open(input_path, "r", encoding="utf-8") as f:
        preprocessed = json.load(f)

    lnrnn = PureLNRNN.from_preprocessed(preprocessed, config)
    branch_names = _get_branch_names(config, len(preprocessed["branch_indices"]))

    if config.get("amplitudes_from_preprocessed", False):
        amplitudes = [float(item["magnitude"]) for item in preprocessed["all_systems"]]
    else:
        amplitudes = config["amplitudes"]
    time_length = config["time_length"]
    fs = config["fs"]
    f_range = tuple(config["f_range"])
    points = config["points"]

    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_file = os.path.join(log_dir, f"{log_timestamp}.jsonl")
    log_handle = open(log_file, "w", encoding="utf-8")

    def write_log(entry):
        log_handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
        log_handle.flush()

    branch_curve_info = [
        _get_curve_points(config, branch_name, fallback_index=branch_position)
        for branch_position, branch_name in enumerate(branch_names)
    ]
    write_log({
        "event": "simulation_config",
        "branches": [
            {
                "name": curve_info["name"],
                "curve": curve_info["config"],
                "fh_kx": list(curve_info["fh_kx"]),
                "fh_ky": list(curve_info["fh_ky"]),
                "branch_index": preprocessed["branch_indices"][branch_position],
            }
            for branch_position, curve_info in enumerate(branch_curve_info)
        ],
        "nonlinear_scale": config.get("nonlinear_scale", 4.0),
        "fh_mode": config.get("fh_mode", "proportional"),
        "equal_acceleration": config.get("equal_acceleration", True),
        "branch_indices": config["branch_indices"],
        "amplitudes": amplitudes,
        "f_range": list(f_range),
        "points": points,
        "time_length": time_length,
        "fs": fs,
    })

    results = {
        "amplitudes": amplitudes,
        "f_range": config["f_range"],
        "time_length": time_length,
        "fs": fs,
        "responses": [],
    }

    wave_base = os.path.join("image", "wave")

    for amplitude in amplitudes:
        system = lnrnn.frequency_response_system(
            fs=fs,
            time_length=time_length,
            f_range=f_range,
            points=points,
            amplitude=amplitude,
            use_parallel=False,
        )
        f_list = system.f
        gain_list = system.gain
        phase_list = system.phase

        for i, (f_val, g_val, p_val) in enumerate(zip(f_list, gain_list, phase_list)):
            adjusted_amp = amplitude
            if config.get("equal_acceleration", True):
                adjusted_amp = amplitude / (2 * np.pi * f_val)
            write_log({
                "event": "frequency_point",
                "amplitude": amplitude,
                "adjusted_amplitude": adjusted_amp,
                "frequency": f_val,
                "gain": g_val,
                "phase": p_val,
            })

        results["responses"].append({
            "amplitude": amplitude,
            "f": list(system.f) if hasattr(system.f, 'tolist') else system.f,
            "gain": list(system.gain) if hasattr(system.gain, 'tolist') else system.gain,
            "phase": list(system.phase) if hasattr(system.phase, 'tolist') else system.phase,
        })
        print(f"  amplitude={amplitude:.3f} done")

        f_plot = 5.0
        period_time = 1.0 / f_plot
        total_time = max(time_length, 8.0 * period_time)
        adjusted_amplitude = amplitude / (2 * np.pi * f_plot)
        input_seq = TimeSeries.fromSin(adjusted_amplitude, f_plot, fs, total_time, fade_in=0.3, fade_out=0.0)
        output_seq = lnrnn.time_response(input_seq)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
        t = np.arange(len(input_seq.samples)) / fs
        t_trim = t[int(0.3 * len(t)):]
        x_trim = input_seq.samples[int(0.3 * len(input_seq.samples)):]
        y_trim = output_seq.samples[int(0.3 * len(output_seq.samples)):]

        ax1.plot(t_trim, x_trim, color='steelblue', linewidth=0.8)
        ax1.set_ylabel('Input x(t)')
        ax1.set_title(f'Input & Output Waveform @ f=5Hz, amplitude={amplitude}')
        ax1.grid(True, ls='--')
        ax1.set_xlim(t_trim[0], t_trim[min(2000, len(t_trim)-1)])

        ax2.plot(t_trim, y_trim, color='coral', linewidth=0.8)
        ax2.set_ylabel('Output y(t)')
        ax2.set_xlabel('Time (s)')
        ax2.grid(True, ls='--')
        ax2.set_xlim(t_trim[0], t_trim[min(2000, len(t_trim)-1)])

        fig.tight_layout()
        wave_path = f"{wave_base}_amp{amplitude:.3f}.png"
        os.makedirs(os.path.dirname(wave_path), exist_ok=True)
        fig.savefig(wave_path, dpi=150)
        plt.close(fig)
        print(f"  waveform saved to {wave_path}")

    log_handle.close()
    print(f"  log saved to {log_file}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Step 2 complete: saved to {output_path}")
    return results


def step3_plot(input_path=RESULTS_FILE, output_path="image/14.NN_extern_simu_reproduced.png", show=False, preprocessed_path=PREPROCESSED_FILE, mode="both", config_path=CONFIG_FILE):
    base, ext = os.path.splitext(output_path)
    simu_path = f"{base}_simulation{ext}"
    fitted_path = f"{base}_fitted{ext}"

    config = load_config(config_path)

    if mode in ("simulation", "both"):
        with open(input_path, "r", encoding="utf-8") as f:
            results = json.load(f)
        with open(preprocessed_path, "r", encoding="utf-8") as f:
            preprocessed = json.load(f)

        amplitudes = results["amplitudes"]
        responses = results["responses"]

        fig, ax = plt.subplots(figsize=(6.4, 4.8))
        colors = plt.cm.viridis(np.linspace(0.1, 0.95, len(amplitudes)))

        for resp, color in zip(responses, colors):
            ax.loglog(resp["f"], resp["gain"], color=color, marker="o", markersize=4, label=f"lnrnn-A{resp['amplitude']:.3f}")

        s = System.s
        f_range = preprocessed["f_range"]
        f_plot = np.logspace(np.log10(f_range[0]), np.log10(f_range[1]), 100)
        branch_names = _get_branch_names(config, len(preprocessed["branch_indices"]))
        normalized_branch_indices = [_normalize_index(idx, len(preprocessed["all_systems"])) for idx in preprocessed["branch_indices"]]
        for branch_name, idx in zip(branch_names, normalized_branch_indices):
            A, B, C = preprocessed["all_systems"][idx]["fit_params"]
            symbol = A * s * (1 / (s**2 + C * s + B))
            sys_fit = System.fromSymbol(symbol, f=f_plot)
            ax.loglog(f_plot, sys_fit.toabs(), color="black", linestyle="--", linewidth=1.5, label=branch_name)

        ax.set_xlim(5, 200)
        y_values = []
        for resp in responses:
            data = np.asarray(resp["gain"], dtype=float)
            data = data[np.isfinite(data) & (data > 0)]
            if data.size:
                y_values.append(data)
        for idx in preprocessed["branch_indices"]:
            A, B, C = preprocessed["all_systems"][idx]["fit_params"]
            symbol = A * s * (1 / (s**2 + C * s + B))
            sys_fit = System.fromSymbol(symbol, f=f_plot)
            data = np.asarray(sys_fit.toabs(), dtype=float)
            data = data[np.isfinite(data) & (data > 0)]
            if data.size:
                y_values.append(data)
        if y_values:
            y_all = np.concatenate(y_values)
            y_min, y_max = y_all.min(), y_all.max()
            margin = 10 ** 0.06
            ax.set_ylim(max(1, y_min / margin), y_max * margin)

        ax.set_ylabel("Gain")
        ax.set_xlabel("Frequency (Hz)")
        ax.legend(loc="upper left", fontsize=8, frameon=True)
        fig.suptitle("IIR-LNRNN 神经网络仿真结果", fontsize=14)
        fig.tight_layout(rect=(0, 0, 1, 0.94))

        os.makedirs(os.path.dirname(simu_path), exist_ok=True)
        fig.savefig(simu_path, dpi=300)
        simu_json_path = simu_path.replace(ext, ".json")
        simu_data = {
            "amplitudes": amplitudes,
            "responses": responses,
            "branch_indices": preprocessed["branch_indices"],
            "branches": []
        }
        for branch_name, idx in zip(branch_names, normalized_branch_indices):
            A, B, C = preprocessed["all_systems"][idx]["fit_params"]
            symbol = A * s * (1 / (s**2 + C * s + B))
            sys_fit = System.fromSymbol(symbol, f=f_plot)
            simu_data["branches"].append({
                "label": branch_name,
                "idx": idx,
                "fit_params": [A, B, C],
                "f": list(f_plot),
                "gain": list(sys_fit.toabs())
            })
        with open(simu_json_path, "w", encoding="utf-8") as f:
            json.dump(simu_data, f, indent=2, ensure_ascii=False)
        print(f"  simulation plot saved to {simu_path}")
        print(f"  simulation data saved to {simu_json_path}")
        plt.close(fig)

        from scipy.interpolate import interp1d

        target_freq = 100.0
        center_freq_interp_factor = config.get("center_freq_interp_factor", 50)
        analysis_target_metrics = _load_target_metrics(
            config,
            preprocessed,
            config["points"],
            interp_factor=center_freq_interp_factor,
            target_freq=target_freq,
        )
        center_freqs = []
        gain_at_100 = []
        for resp in responses:
            f_arr = np.asarray(resp["f"])
            gain_arr = np.asarray(resp["gain"])
            valid = np.isfinite(gain_arr) & (gain_arr > 0)
            gain_arr_valid = gain_arr[valid]
            f_arr_valid = f_arr[valid]
            center_freqs.append(_estimate_center_frequency(f_arr_valid, gain_arr_valid, interp_factor=center_freq_interp_factor))
            interp_func = interp1d(f_arr_valid, gain_arr_valid, kind="linear", fill_value="extrapolate")
            gain_at_100.append(float(interp_func(target_freq)))

        fitted_magnitudes = analysis_target_metrics["amplitudes"]
        fitted_center_freqs = analysis_target_metrics["center_freqs"]
        fitted_gain_at_100 = analysis_target_metrics["gain_at_target"]
        fitted_label = analysis_target_metrics["label"]

        fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))
        ax1.semilogx(amplitudes, center_freqs, marker="o", markersize=4, color="steelblue", label="Wiener simu")
        ax1.semilogx(fitted_magnitudes, fitted_center_freqs, marker="s", markersize=3, color="coral", linewidth=1.2, label=fitted_label)
        ax1.set_xlabel("Magnitude (m/s^2)")
        ax1.set_ylabel("Center Frequency (Hz)")
        ax1.set_title("Center frequency vs magnitude")
        ax1.grid(True, which="both", ls="--")
        ax1.legend()

        ax2.semilogx(amplitudes, gain_at_100, marker="o", markersize=4, color="steelblue", label="Wiener simu")
        ax2.semilogx(fitted_magnitudes, fitted_gain_at_100, marker="s", markersize=3, color="coral", linewidth=1.2, label=fitted_label)
        ax2.set_xlabel("Magnitude (m/s^2)")
        ax2.set_ylabel("Gain at 100 Hz")
        ax2.set_title("Gain at 100 Hz vs magnitude")
        ax2.grid(True, which="both", ls="--")
        ax2.legend()

        fig2.tight_layout()
        analysis_path = f"{base}_analysis{ext}"
        os.makedirs(os.path.dirname(analysis_path), exist_ok=True)
        fig2.savefig(analysis_path, dpi=300)
        analysis_json_path = analysis_path.replace(ext, ".json")
        analysis_data = {
            "amplitudes": amplitudes,
            "center_freqs": center_freqs,
            "gain_at_100": gain_at_100,
            "fitted_magnitudes": fitted_magnitudes,
            "fitted_center_freqs": fitted_center_freqs,
            "fitted_gain_at_100": fitted_gain_at_100,
            "target_source": analysis_target_metrics["source"],
        }
        with open(analysis_json_path, "w", encoding="utf-8") as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)
        print(f"  analysis plot saved to {analysis_path}")
        print(f"  analysis data saved to {analysis_json_path}")
        plt.close(fig2)

        branch_names = _get_branch_names(config, len(preprocessed["branch_indices"]))
        branch_curve_info = [
            _get_curve_points(config, branch_name, fallback_index=branch_position)
            for branch_position, branch_name in enumerate(branch_names)
        ]
        branch_plot_data = []
        for curve_info in branch_curve_info:
            nonlinear_function = PiecewiseMap.from_xk(curve_info["fh_kx"], curve_info["fh_ky"])
            x_values = np.array([xi for xi in curve_info["fh_kx"] if xi >= 0])
            k_values = np.array([curve_info["fh_ky"][i] for i, xi in enumerate(curve_info["fh_kx"]) if xi >= 0])
            integral_values = np.array([float(nonlinear_function(xi)) for xi in x_values])
            branch_plot_data.append({
                "name": curve_info["name"],
                "x": x_values,
                "k": k_values,
                "integral": integral_values,
                "fh_kx": curve_info["fh_kx"],
                "fh_ky": curve_info["fh_ky"],
                "xn": nonlinear_function.xn,
            })

        color_map = plt.cm.tab10(np.linspace(0.0, 0.9, len(branch_plot_data)))

        fig4, ax = plt.subplots(figsize=(8, 4.8))
        for branch_data, color in zip(branch_plot_data, color_map):
            ax.plot(branch_data["x"], branch_data["k"], "o-", color=color, linewidth=2, markersize=6, label=branch_data["name"])
        ax.set_xlabel("x")
        ax.set_ylabel("k (slope)")
        ax.set_title("fh_kx: x-k (slope)")
        ax.grid(True, ls="--")
        ax.legend()
        fig4.tight_layout()
        fh_kx_path = f"{base}_fh_kx{ext}"
        os.makedirs(os.path.dirname(fh_kx_path), exist_ok=True)
        fig4.savefig(fh_kx_path, dpi=300)
        fh_kx_json_path = fh_kx_path.replace(ext, ".json")
        fh_kx_data = {
            branch_data["name"]: {
                "x": list(branch_data["x"]),
                "k": list(branch_data["k"]),
                "fh_kx": list(branch_data["fh_kx"]),
                "fh_ky": list(branch_data["fh_ky"]),
                "xn": branch_data["xn"],
            }
            for branch_data in branch_plot_data
        }
        with open(fh_kx_json_path, "w", encoding="utf-8") as f:
            json.dump(fh_kx_data, f, indent=2, ensure_ascii=False)
        print(f"  fh_kx plot saved to {fh_kx_path}")
        print(f"  fh_kx data saved to {fh_kx_json_path}")
        plt.close(fig4)

        fig5, ax = plt.subplots(figsize=(8, 4.8))
        for branch_data, color in zip(branch_plot_data, color_map):
            ax.plot(branch_data["x"], branch_data["integral"], "o-", color=color, linewidth=2, markersize=6, label=branch_data["name"])
        ax.set_xlabel("x")
        ax.set_ylabel("integral of k")
        ax.set_title("fh: x-integral(k)")
        ax.grid(True, ls="--")
        ax.legend()
        fig5.tight_layout()
        fh_path = f"{base}_fh{ext}"
        os.makedirs(os.path.dirname(fh_path), exist_ok=True)
        fig5.savefig(fh_path, dpi=300)
        fh_json_path = fh_path.replace(ext, ".json")
        fh_data = {
            branch_data["name"]: {
                "x": list(branch_data["x"]),
                "integral": list(branch_data["integral"]),
                "xn": branch_data["xn"],
            }
            for branch_data in branch_plot_data
        }
        with open(fh_json_path, "w", encoding="utf-8") as f:
            json.dump(fh_data, f, indent=2, ensure_ascii=False)
        print(f"  fh plot saved to {fh_path}")
        print(f"  fh data saved to {fh_json_path}")
        plt.close(fig5)

    if mode in ("fitted", "both"):
        with open(preprocessed_path, "r", encoding="utf-8") as f:
            preprocessed = json.load(f)

        all_systems = preprocessed["all_systems"]
        f_range = preprocessed["f_range"]
        s = System.s
        f_plot = np.logspace(np.log10(f_range[0]), np.log10(f_range[1]), 100)

        fig, ax = plt.subplots(figsize=(6.4, 4.8))
        colors = plt.cm.viridis(np.linspace(0.1, 0.95, len(all_systems)))

        for i, sys_info in enumerate(all_systems):
            A, B, C = sys_info["fit_params"]
            symbol = A * s * (1 / (s**2 + C * s + B))
            sys_fit = System.fromSymbol(symbol, f=f_plot)
            ax.loglog(f_plot, sys_fit.toabs(), color=colors[i], marker="o", markersize=4, label=f"mag={sys_info['magnitude']:.2f}")

        ax.set_xlim(5, 200)
        y_values = []
        for i, sys_info in enumerate(all_systems):
            A, B, C = sys_info["fit_params"]
            symbol = A * s * (1 / (s**2 + C * s + B))
            sys_fit = System.fromSymbol(symbol, f=f_plot)
            data = np.asarray(sys_fit.toabs(), dtype=float)
            data = data[np.isfinite(data) & (data > 0)]
            if data.size:
                y_values.append(data)
        if y_values:
            y_all = np.concatenate(y_values)
            y_min, y_max = y_all.min(), y_all.max()
            margin = 10 ** 0.06
            ax.set_ylim(y_min / margin, y_max * margin)

        ax.set_ylabel("Gain")
        ax.set_xlabel("Frequency (Hz)")
        ax.legend(loc="upper left", fontsize=6, frameon=True, ncol=2)
        fig.suptitle("All Fitted WS Systems", fontsize=14)
        fig.tight_layout(rect=(0, 0, 1, 0.94))

        os.makedirs(os.path.dirname(fitted_path), exist_ok=True)
        fig.savefig(fitted_path, dpi=300)
        fitted_json_path = fitted_path.replace(ext, ".json")
        fitted_data = {
            "f": list(f_plot),
            "systems": []
        }
        for i, sys_info in enumerate(all_systems):
            A, B, C = sys_info["fit_params"]
            symbol = A * s * (1 / (s**2 + C * s + B))
            sys_fit = System.fromSymbol(symbol, f=f_plot)
            fitted_data["systems"].append({
                "magnitude": sys_info["magnitude"],
                "fit_params": [A, B, C],
                "gain": list(sys_fit.toabs())
            })
        with open(fitted_json_path, "w", encoding="utf-8") as f:
            json.dump(fitted_data, f, indent=2, ensure_ascii=False)
        print(f"  fitted plot saved to {fitted_path}")
        print(f"  fitted data saved to {fitted_json_path}")
        plt.close(fig)

    print(f"Step 3 complete.")
    if show:
        plt.show()


def _deep_update_dict(base, updates):
    merged = copy.deepcopy(base)
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_update_dict(merged[key], value)
        else:
            merged[key] = value
    return merged


def _estimate_center_frequency(f_arr, gain_arr, interp_factor=50):
    f_arr = np.asarray(f_arr, dtype=float)
    gain_arr = np.asarray(gain_arr, dtype=float)
    valid = np.isfinite(f_arr) & np.isfinite(gain_arr) & (gain_arr > 0)
    f_valid = f_arr[valid]
    gain_valid = gain_arr[valid]
    if len(f_valid) == 0:
        raise ValueError("No valid frequency samples available for center-frequency estimation")
    if len(f_valid) == 1:
        return float(f_valid[0])

    interp_factor = max(1, int(interp_factor))
    dense_f = [float(f_valid[0])]
    for left, right in zip(f_valid[:-1], f_valid[1:]):
        segment = np.linspace(left, right, interp_factor + 1, endpoint=True)
        dense_f.extend(segment[1:].tolist())
    dense_f = np.asarray(dense_f, dtype=float)
    dense_gain = np.interp(dense_f, f_valid, gain_valid)
    return float(dense_f[np.argmax(dense_gain)])


def _fit_center_frequencies(preprocessed, points, interp_factor=50):
    f_range = tuple(preprocessed["f_range"])
    f_plot = np.logspace(np.log10(f_range[0]), np.log10(f_range[1]), points)
    s = System.s
    fit_center_freqs = []
    for sys_info in preprocessed["all_systems"]:
        A_value, B_value, C_value = sys_info["fit_params"]
        symbol = A_value * s * (1 / (s**2 + C_value * s + B_value))
        gain = np.asarray(System.fromSymbol(symbol, f=f_plot).toabs(), dtype=float)
        fit_center_freqs.append(_estimate_center_frequency(f_plot, gain, interp_factor=interp_factor))
    return fit_center_freqs


def _response_gain_at_frequency(f_arr, gain_arr, target_freq):
    f_arr = np.asarray(f_arr, dtype=float)
    gain_arr = np.asarray(gain_arr, dtype=float)
    valid = np.isfinite(f_arr) & np.isfinite(gain_arr) & (gain_arr > 0)
    f_valid = f_arr[valid]
    gain_valid = gain_arr[valid]
    if len(f_valid) == 0:
        raise ValueError("No valid frequency samples available for gain interpolation")
    return float(np.interp(float(target_freq), f_valid, gain_valid))


def _load_target_metrics(config, preprocessed, points, interp_factor=50, target_freq=100.0):
    target_metrics_path = config.get("target_metrics_path")
    if target_metrics_path:
        with open(target_metrics_path, "r", encoding="utf-8") as f:
            target_data = json.load(f)
        amplitudes = [float(item.get("mag", item.get("freq"))) for item in target_data]
        center_freqs = [float(item["center_freq"]) for item in target_data]
        gain_at_target = [float(item["sen_at_100"]) for item in target_data]
        return {
            "source": "measured",
            "label": "Measured",
            "amplitudes": amplitudes,
            "center_freqs": center_freqs,
            "gain_at_target": gain_at_target,
        }

    amplitudes = [float(item["magnitude"]) for item in preprocessed["all_systems"]]
    center_freqs = _fit_center_frequencies(preprocessed, points, interp_factor=interp_factor)
    gain_at_target = _fit_gain_at_frequency(preprocessed, points, target_freq=target_freq)
    return {
        "source": "fit",
        "label": "WS fit",
        "amplitudes": amplitudes,
        "center_freqs": center_freqs,
        "gain_at_target": gain_at_target,
    }


def _fit_gain_at_frequency(preprocessed, points, target_freq=100.0):
    f_range = tuple(preprocessed["f_range"])
    f_plot = np.logspace(np.log10(f_range[0]), np.log10(f_range[1]), points)
    s = System.s
    fit_gain_values = []
    for sys_info in preprocessed["all_systems"]:
        A_value, B_value, C_value = sys_info["fit_params"]
        symbol = A_value * s * (1 / (s**2 + C_value * s + B_value))
        gain = np.asarray(System.fromSymbol(symbol, f=f_plot).toabs(), dtype=float)
        fit_gain_values.append(_response_gain_at_frequency(f_plot, gain, target_freq))
    return fit_gain_values


def evaluate_tuning_config(preprocessed, config, points=None):
    tuning_points = config.get("tuning_points", config.get("points", 50)) if points is None else points
    interp_factor = config.get("center_freq_interp_factor", 50)
    target_freq = float(config.get("analysis_target_freq", 100.0))
    target_metrics = _load_target_metrics(config, preprocessed, tuning_points, interp_factor=interp_factor, target_freq=target_freq)
    amplitudes = target_metrics["amplitudes"]
    lnrnn = PureLNRNN.from_preprocessed(preprocessed, config)
    sim_center_freqs = []
    sim_gain_at_target = []
    for amplitude in amplitudes:
        response = lnrnn.frequency_response_system(
            fs=config["fs"],
            time_length=config["time_length"],
            f_range=tuple(config["f_range"]),
            points=tuning_points,
            amplitude=amplitude,
        )
        sim_center_freqs.append(_estimate_center_frequency(response.f, response.gain, interp_factor=interp_factor))
        sim_gain_at_target.append(_response_gain_at_frequency(response.f, response.gain, target_freq))
    fit_center_freqs = target_metrics["center_freqs"]
    fit_gain_at_target = target_metrics["gain_at_target"]
    sim_array = np.asarray(sim_center_freqs, dtype=float)
    fit_array = np.asarray(fit_center_freqs, dtype=float)
    sim_gain_array = np.asarray(sim_gain_at_target, dtype=float)
    fit_gain_array = np.asarray(fit_gain_at_target, dtype=float)
    center_freq_mse = float(np.mean((sim_array - fit_array) ** 2))
    gain_mse = float(np.mean((sim_gain_array - fit_gain_array) ** 2))
    center_freq_scale = float(np.mean(fit_array ** 2)) if np.any(fit_array) else 1.0
    gain_scale = float(np.mean(fit_gain_array ** 2)) if np.any(fit_gain_array) else 1.0
    center_freq_nmse = center_freq_mse / center_freq_scale
    gain_nmse = gain_mse / gain_scale
    combined_score = float(center_freq_nmse + gain_nmse)

    def nearest_key_metrics(target):
        idx = min(range(len(amplitudes)), key=lambda i: abs(amplitudes[i] - target))
        return {
            "amplitude": amplitudes[idx],
            "sim": sim_center_freqs[idx],
            "fit": fit_center_freqs[idx],
            "error": sim_center_freqs[idx] - fit_center_freqs[idx],
            "sim_gain_at_target": sim_gain_at_target[idx],
            "fit_gain_at_target": fit_gain_at_target[idx],
            "gain_error": sim_gain_at_target[idx] - fit_gain_at_target[idx],
        }

    return {
        "amplitudes": amplitudes,
        "sim_center_freqs": sim_center_freqs,
        "fit_center_freqs": fit_center_freqs,
        "sim_gain_at_target": sim_gain_at_target,
        "fit_gain_at_target": fit_gain_at_target,
        "target_source": target_metrics["source"],
        "analysis_target_freq": target_freq,
        "center_freq_mse": center_freq_mse,
        "gain_mse": gain_mse,
        "center_freq_nmse": center_freq_nmse,
        "gain_nmse": gain_nmse,
        "combined_score": combined_score,
        "mse": center_freq_mse,
        "key_metrics": {
            "0.12": nearest_key_metrics(0.12),
            "3.0": nearest_key_metrics(3.0),
            "6.0": nearest_key_metrics(6.0),
        },
    }


def _tuning_worker(payload):
    case_config = _deep_update_dict(payload["base_config"], payload["overrides"])
    metrics = evaluate_tuning_config(payload["preprocessed"], case_config, points=payload["points"])
    return {
        "name": payload["name"],
        "overrides": payload["overrides"],
        "metrics": metrics,
    }


def tune_configs(preprocessed_path=PREPROCESSED_FILE, config_path=CONFIG_FILE, batch_path=None, points=None, workers=None):
    with open(preprocessed_path, "r", encoding="utf-8") as f:
        preprocessed = json.load(f)
    base_config = load_config(config_path)

    if batch_path:
        with open(batch_path, "r", encoding="utf-8") as f:
            batch_data = json.load(f)
        if isinstance(batch_data, dict):
            cases = batch_data.get("cases", [])
        else:
            cases = batch_data
    else:
        cases = [{"name": "current", "overrides": {}}]

    payloads = [
        {
            "name": case.get("name", f"case{i + 1}"),
            "overrides": case.get("overrides", {}),
            "preprocessed": preprocessed,
            "base_config": base_config,
            "points": points,
        }
        for i, case in enumerate(cases)
    ]

    if workers is None:
        workers = min(len(payloads), max(1, (os.cpu_count() or 1) - 1))
    workers = max(1, min(workers, len(payloads)))

    results = []

    def emit_result(result):
        metrics = result["metrics"]
        key012 = metrics["key_metrics"]["0.12"]
        key30 = metrics["key_metrics"]["3.0"]
        key60 = metrics["key_metrics"]["6.0"]
        print(
            f"[{result['name']}] score={metrics['combined_score']:.6f} | "
            f"cf_mse={metrics['center_freq_mse']:.6f} cf_nmse={metrics['center_freq_nmse']:.6f} | "
            f"g100_mse={metrics['gain_mse']:.6f} g100_nmse={metrics['gain_nmse']:.6f} | "
            f"0.12 sim={key012['sim']:.2f} fit={key012['fit']:.2f} err={key012['error']:.2f} | "
            f"3.0 sim={key30['sim']:.2f} fit={key30['fit']:.2f} err={key30['error']:.2f} | "
            f"6.0 sim={key60['sim']:.2f} fit={key60['fit']:.2f} err={key60['error']:.2f}"
        )

    if workers == 1:
        for payload in payloads:
            result = _tuning_worker(payload)
            results.append(result)
            emit_result(result)
    else:
        print(f"Running tuning with {workers} worker processes")
        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(_tuning_worker, payload) for payload in payloads]
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                emit_result(result)

    results.sort(key=lambda item: item["metrics"]["combined_score"])
    if len(results) > 1:
        print("Best by combined score:")
        best = results[0]
        print(json.dumps({
            "name": best["name"],
            "combined_score": best["metrics"]["combined_score"],
            "center_freq_mse": best["metrics"]["center_freq_mse"],
            "gain_mse": best["metrics"]["gain_mse"],
            "center_freq_nmse": best["metrics"]["center_freq_nmse"],
            "gain_nmse": best["metrics"]["gain_nmse"],
            "key_metrics": best["metrics"]["key_metrics"],
            "overrides": best["overrides"],
        }, ensure_ascii=False, indent=2))

    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    tune_log_path = os.path.join(log_dir, f"tuning-{log_timestamp}.json")
    with open(tune_log_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": log_timestamp,
            "config_path": config_path,
            "preprocessed_path": preprocessed_path,
            "batch_path": batch_path,
            "points": points,
            "workers": workers,
            "results": results,
        }, f, indent=2, ensure_ascii=False)
    print(f"Tuning log saved to {tune_log_path}")
    return results


def build_and_plot(source="twofreq", data_dir=DEFAULT_DATA_DIR, output_path="image/14.NN_extern_simu_reproduced.png", time_length=2.5, show=False, branch_indices=None):
    if source == "twofreq":
        raise NotImplementedError("twofreq source not supported in 3-step mode")
    elif source == "data":
        step1_read_and_process(data_dir=data_dir, branch_indices=branch_indices)
        step2_simulate(time_length=time_length)
        step3_plot(output_path=output_path, show=show, config_path=CONFIG_FILE)
    else:
        raise ValueError(f"Unsupported source: {source}")


DEFAULT_MAIN_PLOT = "image/14.NN_extern_simu_reproduced.png"


@contextmanager
def _pushd(path: Path):
    previous = Path.cwd()
    os.makedirs(path, exist_ok=True)
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def _resolve_path(base_dir: Path, value: Optional[str]) -> Optional[Path]:
    if value in (None, ""):
        return None
    path = Path(value)
    if not path.is_absolute():
        path = base_dir / path
    return path


def _relative_to_task_root(task_root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(task_root)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


class WienerParallelModelingAnalyzer:
    """Run the parallel Wiener modeling reproduction inside an ex_projects task."""

    def __init__(self, config: Dict[str, Any], task_root: Path, output_dir: Optional[Path] = None):
        self.config = copy.deepcopy(config)
        self.task_root = Path(task_root)
        self.output_dir = Path(output_dir) if output_dir is not None else self.task_root / DATA_DIR
        self.summary: Dict[str, Any] = {}
        self.generated_files: Dict[str, str] = {}

    def _copy_into_workspace(self, source: Path, destination: Path) -> None:
        if not source.exists():
            raise FileNotFoundError(f"Input file not found: {source}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.resolve() != destination.resolve():
            shutil.copy2(source, destination)

    def _prepare_inputs(self) -> Dict[str, Any]:
        inputs_cfg = self.config.get("inputs", {}) or {}
        rebuild_preprocessed = bool(inputs_cfg.get("rebuild_preprocessed", False))
        raw_data_dir = _resolve_path(self.task_root, inputs_cfg.get("raw_data_dir"))

        preprocessed_source = _resolve_path(
            self.task_root,
            inputs_cfg.get("preprocessed_source", "data/reference/preprocessed_data.json"),
        )
        measured_source = _resolve_path(
            self.task_root,
            inputs_cfg.get("measured_targets_source", "data/reference/measured_targets.json"),
        )

        if measured_source is None:
            raise ValueError("measured_targets_source is required")

        data_dir = self.task_root / DATA_DIR
        data_dir.mkdir(parents=True, exist_ok=True)
        (self.task_root / "image").mkdir(parents=True, exist_ok=True)
        (self.task_root / "logs").mkdir(parents=True, exist_ok=True)

        if not rebuild_preprocessed:
            if preprocessed_source is None:
                raise ValueError("preprocessed_source is required when rebuild_preprocessed is false")
            self._copy_into_workspace(preprocessed_source, self.task_root / PREPROCESSED_FILE)
        elif raw_data_dir is None:
            raise ValueError("raw_data_dir is required when rebuild_preprocessed is true")

        self._copy_into_workspace(measured_source, self.task_root / DATA_DIR / "measured_targets.json")

        output_cfg = self.config.get("output", {}) or {}
        return {
            "rebuild_preprocessed": rebuild_preprocessed,
            "raw_data_dir": raw_data_dir,
            "main_plot": output_cfg.get("main_plot", DEFAULT_MAIN_PLOT),
            "mode": output_cfg.get("plot_mode", "both"),
            "show": bool(output_cfg.get("show", False)),
        }

    def _analysis_json_path(self, main_plot: str) -> Path:
        main_plot_path = self.task_root / main_plot
        return main_plot_path.with_name(f"{main_plot_path.stem}_analysis.json")

    def _build_summary(self, main_plot: str) -> Dict[str, Any]:
        analysis_path = self._analysis_json_path(main_plot)
        if not analysis_path.exists():
            raise FileNotFoundError(f"Analysis output not found: {analysis_path}")

        analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
        center_freqs = np.asarray(analysis.get("center_freqs", []), dtype=float)
        fitted_center_freqs = np.asarray(analysis.get("fitted_center_freqs", []), dtype=float)
        gain_at_target = np.asarray(analysis.get("gain_at_100", []), dtype=float)
        fitted_gain_at_target = np.asarray(analysis.get("fitted_gain_at_100", []), dtype=float)

        def _safe_stats(array: np.ndarray) -> Dict[str, Optional[float]]:
            if array.size == 0:
                return {"min": None, "max": None, "mean": None}
            return {
                "min": float(np.min(array)),
                "max": float(np.max(array)),
                "mean": float(np.mean(array)),
            }

        center_diff = center_freqs - fitted_center_freqs
        gain_diff = gain_at_target - fitted_gain_at_target

        expected_suffixes = [
            "simulation.png",
            "fitted.png",
            "analysis.png",
            "fh.png",
            "fh_kx.png",
            "simulation.json",
            "fitted.json",
            "analysis.json",
            "fh.json",
            "fh_kx.json",
        ]
        main_plot_path = self.task_root / main_plot
        generated = {}
        for suffix in expected_suffixes:
            candidate = main_plot_path.with_name(f"{main_plot_path.stem}_{suffix}")
            if candidate.exists():
                generated[suffix] = _relative_to_task_root(self.task_root, candidate)
        for wave_plot in sorted((self.task_root / "image").glob("wave_amp*.png")):
            generated[wave_plot.name] = _relative_to_task_root(self.task_root, wave_plot)

        summary = {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "task_root": str(self.task_root),
            "target_source": analysis.get("target_source", "unknown"),
            "amplitude_count": len(analysis.get("amplitudes", [])),
            "center_frequency": {
                "simulated": _safe_stats(center_freqs),
                "target": _safe_stats(fitted_center_freqs),
                "mae_hz": float(np.mean(np.abs(center_diff))) if center_diff.size else None,
                "rmse_hz": float(np.sqrt(np.mean(center_diff ** 2))) if center_diff.size else None,
                "max_abs_error_hz": float(np.max(np.abs(center_diff))) if center_diff.size else None,
            },
            "gain_at_target_frequency": {
                "frequency_hz": float(self.config.get("analysis_target_freq", 100.0)),
                "simulated": _safe_stats(gain_at_target),
                "target": _safe_stats(fitted_gain_at_target),
                "mae": float(np.mean(np.abs(gain_diff))) if gain_diff.size else None,
                "rmse": float(np.sqrt(np.mean(gain_diff ** 2))) if gain_diff.size else None,
                "max_abs_error": float(np.max(np.abs(gain_diff))) if gain_diff.size else None,
            },
            "generated_files": generated,
        }
        self.generated_files = generated
        return summary

    def run_analysis(self) -> Dict[str, Any]:
        runtime = self._prepare_inputs()
        main_plot = runtime["main_plot"]
        with _pushd(self.task_root):
            if runtime["rebuild_preprocessed"]:
                step1_read_and_process(
                    data_dir=str(runtime["raw_data_dir"]),
                    output_path=PREPROCESSED_FILE,
                    config_path=CONFIG_FILE,
                )
            step2_simulate(
                input_path=PREPROCESSED_FILE,
                output_path=RESULTS_FILE,
                config_path=CONFIG_FILE,
            )
            step3_plot(
                input_path=RESULTS_FILE,
                output_path=main_plot,
                show=runtime["show"],
                preprocessed_path=PREPROCESSED_FILE,
                mode=runtime["mode"],
                config_path=CONFIG_FILE,
            )
        self.summary = self._build_summary(main_plot)
        return self.summary

    def generate_markdown_report(self) -> str:
        if not self.summary:
            raise ValueError("run_analysis must be called before generate_markdown_report")

        center_summary = self.summary["center_frequency"]
        gain_summary = self.summary["gain_at_target_frequency"]
        generated = self.summary.get("generated_files", {})

        lines = [
            "# Parallel Wiener Modeling Reproduction Report",
            "",
            f"- Generated at: {self.summary['generated_at']}",
            f"- Amplitude count: {self.summary['amplitude_count']}",
            f"- Target source: {self.summary['target_source']}",
            "",
            "## Key Fit Errors",
            "",
            f"- Center-frequency MAE: {center_summary['mae_hz']:.4f} Hz" if center_summary['mae_hz'] is not None else "- Center-frequency MAE: -",
            f"- Center-frequency RMSE: {center_summary['rmse_hz']:.4f} Hz" if center_summary['rmse_hz'] is not None else "- Center-frequency RMSE: -",
            f"- 100 Hz sensitivity MAE: {gain_summary['mae']:.4f}" if gain_summary['mae'] is not None else "- 100 Hz sensitivity MAE: -",
            f"- 100 Hz sensitivity RMSE: {gain_summary['rmse']:.4f}" if gain_summary['rmse'] is not None else "- 100 Hz sensitivity RMSE: -",
            "",
            "## Value Ranges",
            "",
            f"- Simulated center-frequency range: {center_summary['simulated']['min']:.4f} - {center_summary['simulated']['max']:.4f} Hz" if center_summary['simulated']['min'] is not None else "- Simulated center-frequency range: -",
            f"- Target center-frequency range: {center_summary['target']['min']:.4f} - {center_summary['target']['max']:.4f} Hz" if center_summary['target']['min'] is not None else "- Target center-frequency range: -",
            f"- Simulated 100 Hz sensitivity range: {gain_summary['simulated']['min']:.4f} - {gain_summary['simulated']['max']:.4f}" if gain_summary['simulated']['min'] is not None else "- Simulated 100 Hz sensitivity range: -",
            f"- Target 100 Hz sensitivity range: {gain_summary['target']['min']:.4f} - {gain_summary['target']['max']:.4f}" if gain_summary['target']['min'] is not None else "- Target 100 Hz sensitivity range: -",
            "",
            "## Main Outputs",
            "",
        ]

        ordered_keys = [
            "simulation.png",
            "fitted.png",
            "analysis.png",
            "fh_kx.png",
            "fh.png",
            "simulation.json",
            "fitted.json",
            "analysis.json",
        ]
        for key in ordered_keys:
            if key in generated:
                lines.append(f"- `{generated[key]}`")
        lines.append("")

        if "simulation.png" in generated:
            lines.extend(["## Frequency-Response Reconstruction", "", f"![simulation]({generated['simulation.png']})", ""])
        if "analysis.png" in generated:
            lines.extend(["## Metric Comparison", "", f"![analysis]({generated['analysis.png']})", ""])
        if "fh_kx.png" in generated:
            lines.extend(["## Piecewise Slope Functions", "", f"![fh_kx]({generated['fh_kx.png']})", ""])
        if "fh.png" in generated:
            lines.extend(["## Integrated Static Maps", "", f"![fh]({generated['fh.png']})", ""])

        return "\n".join(lines)

    def save_results(self) -> None:
        if not self.summary:
            raise ValueError("run_analysis must be called before save_results")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        summary_path = self.output_dir / "wiener_parallel_modeling_summary.json"
        summary_path.write_text(json.dumps(self.summary, indent=2, ensure_ascii=False), encoding="utf-8")

        report_path = self.task_root / "report.md"
        report_path.write_text(self.generate_markdown_report(), encoding="utf-8")


def run_wiener_parallel_modeling(config: Dict[str, Any], task_root: Path, output_dir: Optional[Path] = None) -> Dict[str, Any]:
    analyzer = WienerParallelModelingAnalyzer(config=config, task_root=task_root, output_dir=output_dir)
    results = analyzer.run_analysis()
    analyzer.save_results()
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="3-step plotting pipeline for NN extern simu")
    parser.add_argument("--step", type=int, choices=[1, 2, 3, 4], help="Which step to run (1, 2, 3, or 4=tune)")
    parser.add_argument("--source", default="data", choices=["twofreq", "data"])
    parser.add_argument("--data-dir", default=DEFAULT_DATA_DIR)
    parser.add_argument("--output", default="image/14.NN_extern_simu_reproduced.png")
    parser.add_argument("--show", action="store_true")
    parser.add_argument("--config-path", default=CONFIG_FILE)
    parser.add_argument("--preprocessed-path", default=PREPROCESSED_FILE)
    parser.add_argument("--results-path", default=RESULTS_FILE)
    parser.add_argument("--mode", default="both", choices=["simulation", "fitted", "both"])
    parser.add_argument("--tune-batch", help="JSON file containing a list of tuning cases or {'cases': [...]}.")
    parser.add_argument("--tune-points", type=int, help="Frequency sample count used during tuning evaluation.")
    parser.add_argument("--tune-workers", type=int, help="Worker process count used during tuning evaluation.")
    args = parser.parse_args()

    if args.step == 1:
        step1_read_and_process(data_dir=args.data_dir, output_path=args.preprocessed_path, config_path=args.config_path)
    elif args.step == 2:
        step2_simulate(input_path=args.preprocessed_path, output_path=args.results_path, config_path=args.config_path)
    elif args.step == 3:
        step3_plot(input_path=args.results_path, output_path=args.output, show=args.show, preprocessed_path=args.preprocessed_path, mode=args.mode, config_path=args.config_path)
    elif args.step == 4:
        tune_configs(preprocessed_path=args.preprocessed_path, config_path=args.config_path, batch_path=args.tune_batch, points=args.tune_points, workers=args.tune_workers)
    else:
        step1_read_and_process(data_dir=args.data_dir, output_path=args.preprocessed_path, config_path=args.config_path)
        step2_simulate(input_path=args.preprocessed_path, output_path=args.results_path, config_path=args.config_path)
        step3_plot(input_path=args.results_path, output_path=args.output, show=args.show, preprocessed_path=args.preprocessed_path, mode=args.mode, config_path=args.config_path)
