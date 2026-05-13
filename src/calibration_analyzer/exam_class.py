from __future__ import annotations
import os
import sys
from typing import List, Tuple
from .config import CONF_SAMPLING_RATE
from . import datastruct
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from matplotlib.colors import hsv_to_rgb
from .utilities import getname
from pandas.core.frame import DataFrame
from numpy import ndarray as array
from . import utilities
from .utilities import _DictData, shift_phase
from .met_datastruct import CFun
from .analyzer import DataAnalyzeResultList
from scipy.interpolate import CubicSpline
from sympy import symbols, simplify, expand, Rational, sympify
from sympy import Poly
from sympy import lambdify
from scipy.integrate import solve_ivp
from scipy.signal import butter, filtfilt, get_window
import time
from scipy import signal
from typing import Optional

# plt.style.use(['science', 'ieee'])
# plt.style.use(['science'])
# plt.style.use(['ieee'])


class ConfigData(_DictData):
    def __init__(self, data_path=None):
        self.mat_dir = 'data\\main_data'
        self.wf_dir = 'data/Wf.txt'  # Wf数据的路径
        self.main_data_dir = 'data/main_data'  # 原始数据的.mat路径
        self.xlsxDir = None
        self.jsonDir = None
        self.sensitive_expect = 200
        self.skipFreqs = [54.692909]
        if data_path is not None:
            if data_path.endswith('.xlsx'):
                self.xlsxDir = data_path
            if data_path.endswith('.json'):
                self.jsonDir = data_path
        else:
            self.xlsxDir = '../../../met_data/main_data.xlsx'  # 原始数据的xlsx路径
        self.isAutoDataLength = 1  # 设定是否使用自动识别的数据长度，如果使用自动识别，则手动录入的数据长度无效
        # 是否重新读表
        self.get_data_from_xlsx = 0
        # 表内的sheet个数
        self.sheet_num = 58
        # 指定截取的数据长度
        self.dataLength = 33
        # 指定录入的数据序号
        self.hand_data = 65
        # 录入电路参数
        self.WfType = 1
        # 选择拟合的点数
        self.fitRange = range(5, 20)
        self.ws_fit_freq_range = (5, 100)
        self.ws_fit_initial_guess = [
            22185.00016896, 42083.83155983, 784.31825175]
        # 设置低频截止频率
        self.fl = 1
        self.Ka = 1
        self.sheetList: list
        # 设置高频截止频率
        self.high_cut_expected = 100
        self.high_cut_keep_system_num = 1
        self.A_k = 1
        self.B_k = 1
        self.C_k = 1
        self.shell_list: list


def hashtimes33(s: str) -> int:
    """
    计算字符串的哈希值，使用33进制。
    """
    if s is None:
        return 0

    h = 0
    for c in s:
        h = h * 33 + ord(c)
    return h


class TimeSeries:
    samples: np.array
    plt_fig = None
    fs: int
    _cache = {}

    def __init__(self, samples: np.array, fs: int, params=None):
        # 对 sample 进行拉平
        samples = np.array(samples).flatten()
        self.samples = np.array(samples)
        self.fs = fs
        self.time = np.arange(len(samples)) / fs
        self.params = params if params else {}

    def apply_fade(self, fade_in=0.3, fade_out=0.3):
        samples_faded = self.samples.copy()

        # 处理S型渐入效果
        if fade_in > 0:
            fade_in_samples = int(len(samples_faded) * fade_in)
            fade_in_envelope = 1 / \
                (1 + np.exp(-12 * (np.linspace(0, 1, fade_in_samples) - 0.5)))
            samples_faded[:fade_in_samples] *= fade_in_envelope

        # 处理S型渐出效果
        if fade_out > 0:
            fade_out_samples = int(len(samples_faded) * fade_out)
            fade_out_envelope = 1 / \
                (1 + np.exp(-12 * (np.linspace(0, 1, fade_out_samples) - 0.5)))
            # 渐出需要反转
            samples_faded[-fade_out_samples:] *= fade_out_envelope[::-1]

        # 创建一个新的 TimeSerial 对象并返回
        faded_series = TimeSeries(samples_faded, self.fs)
        faded_series.params = self.params.copy()  # 复制原始参数
        faded_series.set_param('FadeIn', fade_in)
        faded_series.set_param('FadeOut', fade_out)
        return faded_series

    @classmethod
    def fromSin(cls, A, f=10, fs=2000, time_length=1, offset=0, fade_in=0.3, fade_out=0.3, debug=False):
        t = np.arange(0, time_length, 1/fs)
        samples_origin = A * np.sin(2 * np.pi * f * t) + offset
        time_series = cls(samples_origin, fs)

        # 设置初始参数
        time_series.set_param('Type', 'Sin')
        time_series.set_param('Amplitude', A)
        time_series.set_param('Frequency', f)
        time_series.set_param('TimeLength', time_length)
        time_series.set_param('name', f'Sin(A={A:.2f},f={f:.2f})')

        # 应用渐入和渐出效果并生成新的 TimeSeries 对象
        if fade_in > 0 or fade_out > 0:
            time_series = time_series.apply_fade(fade_in, fade_out)

        # 可选调试模式
        if debug:
            plt.figure()
            plt.plot(t, samples_origin, label='Original Time Series')
            plt.plot(time_series.time, time_series.samples,
                     label='Time Series with Fade')
            plt.legend()
            plt.title('Sine Wave')
            plt.show()

        return time_series

    @classmethod
    def fromSquare(cls, A, f=10, fs=2000, time_length=1, offset=0, fade_in=0.3, fade_out=0.3,
                   duty=0.5, debug=False):
        t = np.arange(0, time_length, 1/fs)
        samples_origin = A * \
            signal.square(2 * np.pi * f * t, duty=duty) + offset
        time_series = cls(samples_origin, fs)

        # 设置初始参数
        time_series.set_param('Type', 'Square')
        time_series.set_param('Amplitude', A)
        time_series.set_param('Frequency', f)
        time_series.set_param('DutyCycle', duty)
        time_series.set_param('TimeLength', time_length)
        time_series.set_param(
            'name', f'Square(A={A:.2f},f={f:.2f},duty={duty})')

        # 应用渐入和渐出效果
        if fade_in > 0 or fade_out > 0:
            time_series = time_series.apply_fade(fade_in, fade_out)

        # 可选调试模式
        if debug:
            plt.figure()
            plt.plot(t, samples_origin, label='Original Square Wave')
            plt.plot(time_series.time, time_series.samples,
                     label='Square Wave with Fade')
            plt.legend()
            plt.title('Square Wave')
            plt.show()

        return time_series

    @classmethod
    def fromTriangle(cls, A, f=10, fs=2000, time_length=1, offset=0, fade_in=0.3, fade_out=0.3, debug=False):
        t = np.arange(0, time_length, 1/fs)
        samples_origin = A * \
            signal.sawtooth(2 * np.pi * f * t, 0.5) + offset  # 0.5 确保是三角波
        time_series = cls(samples_origin, fs)

        # 设置初始参数
        time_series.set_param('Type', 'Triangle')
        time_series.set_param('Amplitude', A)
        time_series.set_param('Frequency', f)
        time_series.set_param('TimeLength', time_length)
        time_series.set_param('name', f'Triangle(A={A:.2f},f={f:.2f})')

        # 应用渐入和渐出效果
        if fade_in > 0 or fade_out > 0:
            time_series = time_series.apply_fade(fade_in, fade_out)

        # 可选调试模式
        if debug:
            plt.figure()
            plt.plot(t, samples_origin, label='Original Triangle Wave')
            plt.plot(time_series.time, time_series.samples,
                     label='Triangle Wave with Fade')
            plt.legend()
            plt.title('Triangle Wave')
            plt.show()

        return time_series

    @classmethod
    def fromSawtooth(cls, A, f=10, fs=2000, time_length=1, offset=0, fade_in=0.3, fade_out=0.3,
                     width=1.0, debug=False):
        t = np.arange(0, time_length, 1/fs)
        samples_origin = A * \
            signal.sawtooth(2 * np.pi * f * t, width=width) + offset
        time_series = cls(samples_origin, fs)

        # 设置初始参数
        time_series.set_param('Type', 'Sawtooth')
        time_series.set_param('Amplitude', A)
        time_series.set_param('Frequency', f)
        time_series.set_param('Width', width)
        time_series.set_param('TimeLength', time_length)
        time_series.set_param(
            'name', f'Sawtooth(A={A:.2f},f={f:.2f},width={width})')

        # 应用渐入和渐出效果
        if fade_in > 0 or fade_out > 0:
            time_series = time_series.apply_fade(fade_in, fade_out)

        # 可选调试模式
        if debug:
            plt.figure()
            plt.plot(t, samples_origin, label='Original Sawtooth Wave')
            plt.plot(time_series.time, time_series.samples,
                     label='Sawtooth Wave with Fade')
            plt.legend()
            plt.title('Sawtooth Wave')
            plt.show()

        return time_series

    @classmethod
    def fromLinspace(cls, start, stop, fs=2000, time_length=1, fade_in=0.0, fade_out=0.0, debug=False):
        num_samples = int(time_length * fs)
        t = np.arange(0, time_length, 1/fs)
        samples_origin = np.linspace(start, stop, num=num_samples)
        time_series = cls(samples_origin, fs)

        # 设置初始参数
        time_series.set_param('Type', 'LinSpace')
        time_series.set_param('Start', start)
        time_series.set_param('Stop', stop)
        time_series.set_param('TimeLength', time_length)
        time_series.set_param('name', f'LinSpace(start={start}, stop={stop})')

        # 应用渐入和渐出效果
        if fade_in > 0 or fade_out > 0:
            time_series = time_series.apply_fade(fade_in, fade_out)

        # 可选调试模式
        if debug:
            plt.figure()
            plt.plot(t, samples_origin, label='Original LinSpace')
            plt.plot(time_series.time, time_series.samples,
                     label='LinSpace with Fade')
            plt.legend()
            plt.title('Linear Space')
            plt.show()

        return time_series

    @classmethod
    def fromLogspace(cls, start, stop, fs=2000, time_length=1, fade_in=0.0, fade_out=0.0, debug=False):
        num_samples = int(time_length * fs)
        t = np.arange(0, time_length, 1/fs)
        # 避免log10(0)，从一个非常小的数开始
        samples_origin = np.logspace(np.log10(start) if start > 0 else -6,
                                     np.log10(stop) if stop > 0 else -6,
                                     num=num_samples, endpoint=False)
        time_series = cls(samples_origin, fs)

        # 设置初始参数
        time_series.set_param('Type', 'LogSpace')
        time_series.set_param('Start', start)
        time_series.set_param('Stop', stop)
        time_series.set_param('TimeLength', time_length)
        time_series.set_param('name', f'LogSpace(start={start}, stop={stop})')

        # 应用渐入和渐出效果
        if fade_in > 0 or fade_out > 0:
            time_series = time_series.apply_fade(fade_in, fade_out)

        # 可选调试模式
        if debug:
            plt.figure()
            plt.plot(t, samples_origin, label='Original LogSpace')
            plt.plot(time_series.time, time_series.samples,
                     label='LogSpace with Fade')
            plt.legend()
            plt.title('Logarithmic Space')
            plt.show()

        return time_series

    def plot(self, clear=False, line_style='-', marker=None, markersize=6, label=None):
        """
        Plots the time series data with options for line style, marker, and marker size.

        Parameters:
            clear (bool): Whether to clear the existing plot.
            line_style (str): Line style for the plot (e.g., '-', '--', '-.', ':').
            marker (str): Marker style for the plot (e.g., 'o', 's', '^', None for no marker).
            markersize (int or float): Size of the markers.
        """
        if label is not None:
            system_name = label
        else:
            if "name" in self.params and self.params['name'] is not None:
                system_name = self.params['name']
            else:
                system_name = utilities.getname(
                    self, sys._getframe(1).f_locals)

        if TimeSeries.plt_fig is None:
            TimeSeries.plt_fig = plt.figure()
            TimeSeries.ax_time = TimeSeries.plt_fig.add_subplot(111)

        # Create the time array
        t = np.arange(0, len(self.samples) / self.fs, 1 / self.fs)

        # Clear the plot if requested
        if clear:
            TimeSeries.ax_time.clear()

        # Plot the data with the specified line style, marker, and marker size
        TimeSeries.ax_time.plot(t, self.samples, label=system_name, linestyle=line_style,
                                marker=marker, markersize=markersize)

        # Set plot labels, grid, and legend
        TimeSeries.ax_time.set_xlabel('Time (s)')
        TimeSeries.ax_time.set_ylabel('Amplitude')
        TimeSeries.ax_time.grid(True, which='both', ls='--')
        TimeSeries.ax_time.legend()
        plt.pause(0.01)

    def dumptobinary(self, filename):
        # 检查文件夹是否存在，不存在则创建
        folder_path = os.path.dirname(filename)
        if folder_path and not os.path.exists(folder_path):
            os.makedirs(folder_path)

        with open(filename, 'wb') as f:
            np.save(f, self.fs)
            np.save(f, self.params)
            np.save(f, self.samples)

    @classmethod
    def loadfrombinary(cls, filename):
        if not os.path.exists(filename):
            raise FileNotFoundError(f"File '{filename}' not found.")

        with open(filename, 'rb') as f:
            fs = np.load(f)
            # 读取字典时要加上 allow_pickle=True
            params = np.load(f, allow_pickle=True).item()
            samples = np.load(f)

        return cls(samples, fs, params=params)

    @staticmethod
    def dump_multichannel_to_binary(time_series_list: list['TimeSeries'], filename: str) -> None:
        folder_path = os.path.dirname(filename)
        if folder_path and not os.path.exists(folder_path):
            os.makedirs(folder_path)

        with open(filename, 'wb') as f:
            num_channels = len(time_series_list)
            np.save(f, num_channels)

            for ts in time_series_list:
                np.save(f, ts.fs)
                np.save(f, len(ts.samples))
                np.save(f, ts.params)
                np.save(f, ts.samples)

    @staticmethod
    def load_multichannel_from_binary(filename: str) -> list['TimeSeries']:
        if not os.path.exists(filename):
            raise FileNotFoundError(f"File '{filename}' not found.")

        if filename in TimeSeries._cache:
            print(f'using cache: {filename}')
            return TimeSeries._cache[filename]

        time_series_list = []
        with open(filename, 'rb') as f:
            num_channels = np.load(f)

            for _ in range(num_channels):
                fs = np.load(f)
                sample_length = np.load(f)
                params = np.load(f, allow_pickle=True).item()
                samples = np.load(f)

                time_series_list.append(TimeSeries(samples, fs, params=params))

        TimeSeries._cache[filename] = time_series_list
        return time_series_list

    def set_param(self, key, value):
        self.params[key] = value

    def get_param(self, key):
        if key in self.params:
            return self.params[key]
        callingframe = sys._getframe(1)
        locals = callingframe.f_locals
        name = utilities.getname(self, locals)
        print(f'\'{key}\' not in params from TimeSeries <{name}>')
        return None

    def apply_gain(self, gain) -> 'TimeSeries':
        return TimeSeries(self.samples * gain, self.fs, params=self.params)

    def resample(self, new_fs: int, use_nyquist=False) -> 'TimeSeries':
        """
        Resamples the TimeSeries to a new sampling frequency (new_fs).

        Parameters:
            new_fs (int): The new sampling frequency in Hz.

        Returns:
            TimeSeries: A new TimeSeries object resampled to new_fs.
        """
        if new_fs == self.fs:
            return TimeSeries(self.samples, self.fs, params=self.params)
        if new_fs > self.fs:
            raise ValueError(
                "new_fs must be less than the original fs (downsampling only).")

        # Calculate the resampling ratio
        ratio = new_fs / self.fs

        if use_nyquist:
            # Apply anti-aliasing filter before downsampling
            nyquist = new_fs / 2
            sos = signal.butter(10, nyquist, btype='low',
                                fs=self.fs, output='sos')
            filtered_samples = signal.sosfilt(sos, self.samples)
        else:
            filtered_samples = self.samples

        # Calculate the number of samples after resampling
        num_samples = int(len(self.samples) * ratio)

        # Resample the signal
        resampled_samples = signal.resample(filtered_samples, num_samples)

        # Create new TimeSeries object with resampled data
        new_params = self.params.copy()
        new_params['OriginalFs'] = self.fs
        new_ts = TimeSeries(resampled_samples, new_fs, params=new_params)
        return new_ts

    def clip(self, start_time: Optional[float] = None, end_time: Optional[float] = None,
             start_index: Optional[int] = None, end_index: Optional[int] = None) -> 'TimeSeries':
        """
        截取TimeSeries的指定片段，可以通过时间或样本索引。

        参数：
            start_time (float)：开始时间（秒）。
            end_time (float)：结束时间（秒）。
            start_index (int)：开始索引。
            end_index (int)：结束索引。

        返回：
            TimeSeries：包含截取片段的新TimeSeries对象。
        """
        if start_index is None and start_time is not None:
            start_index = int(start_time * self.fs)
        if end_index is None and end_time is not None:
            end_index = int(end_time * self.fs)

        if start_index is None:
            start_index = 0
        if end_index is None:
            end_index = len(self.samples)

        clipped_samples = self.samples[start_index:end_index]
        new_params = self.params.copy()
        new_params['ClipStart'] = start_index / self.fs
        new_params['ClipEnd'] = end_index / self.fs
        new_ts = TimeSeries(clipped_samples, self.fs, params=new_params)
        return new_ts

    @classmethod
    # 连接两个TimeSeries对象
    def concatenate(cls, time_series_list: List['TimeSeries']) -> 'TimeSeries':
        """
        连接两个TimeSeries对象。

        参数：
            time_series_list (List[TimeSeries])：要连接的TimeSeries对象列表。
            fs (int)：新TimeSeries对象的采样率。

        返回：
            TimeSeries：连接后的新TimeSeries对象。
        """
        # 检查所有TimeSeries对象的采样率是否相同
        fs = time_series_list[0].fs
        for ts in time_series_list:
            if ts.fs != fs:
                raise ValueError(
                    "All TimeSeries objects must have the same sampling rate.")

        # 连接所有TimeSeries对象
        concatenated_samples = np.concatenate(
            [ts.samples for ts in time_series_list])
        new_params = time_series_list[0].params.copy()
        new_params['Concatenated'] = True
        new_ts = TimeSeries(concatenated_samples, fs, params=new_params)
        return new_ts

    def remove_dc(self) -> 'TimeSeries':
        """
        移除TimeSeries的直流偏置。

        返回：
            TimeSeries：移除直流偏置后的新TimeSeries对象。
        """
        mean_value = np.mean(self.samples)
        samples_without_dc = self.samples - mean_value
        new_params = self.params.copy()
        new_params['DCOffset'] = mean_value
        new_ts = TimeSeries(samples_without_dc, self.fs, params=new_params)
        return new_ts

    def filter(self, filter_type='lowpass', cutoff_freq=None, order=4,
               center_freq=None, bandwidth=None, filter_design='butter') -> 'TimeSeries':
        """
        使用指定的滤波参数对TimeSeries进行滤波。

        参数：
            filter_type (str)：滤波器类型（'lowpass'，'highpass'，'bandpass'）。
            cutoff_freq (float or list)：截止频率（Hz）。
                对于'lowpass'和'highpass'，提供一个频率。
                对于'bandpass'，提供[低频， 高频]。
            order (int)：滤波器阶数。
            center_freq (float)：带通滤波器的中心频率。
            bandwidth (float)：带通滤波器的带宽。
            filter_design (str)：滤波器设计类型（'butter'，'cheby1'等）。

        返回：
            TimeSeries：滤波后的新TimeSeries对象。
        """
        nyquist = 0.5 * self.fs

        if filter_type == 'lowpass' or filter_type == 'highpass':
            if cutoff_freq is None:
                raise ValueError("cutoff_freq必须为'lowpass'和'highpass'滤波器指定。")
            normalized_cutoff = cutoff_freq / nyquist
            btype = 'low' if filter_type == 'lowpass' else 'high'
        elif filter_type == 'bandpass':
            if cutoff_freq is None:
                if center_freq is None or bandwidth is None:
                    raise ValueError(
                        "对于带通滤波器，需提供cutoff_freq或center_freq和bandwidth。")
                low = (center_freq - bandwidth / 2) / nyquist
                high = (center_freq + bandwidth / 2) / nyquist
                normalized_cutoff = [low, high]
            else:
                normalized_cutoff = [f / nyquist for f in cutoff_freq]
            btype = 'band'
        else:
            raise ValueError("filter_type必须为'lowpass'，'highpass'或'bandpass'。")

        # 设计滤波器
        if filter_design == 'butter':
            b, a = signal.butter(order, normalized_cutoff, btype=btype)
        elif filter_design == 'cheby1':
            b, a = signal.cheby1(order, 0.5, normalized_cutoff, btype=btype)
        else:
            raise ValueError("不支持的滤波器设计。")

        # 应用滤波器
        filtered_samples = signal.filtfilt(b, a, self.samples)

        new_params = self.params.copy()
        new_params['FilterType'] = filter_type
        new_params['FilterOrder'] = order
        new_params['FilterCutoff'] = cutoff_freq
        new_params['FilterDesign'] = filter_design

        new_ts = TimeSeries(filtered_samples, self.fs, params=new_params)
        return new_ts

    def invert(self) -> 'TimeSeries':
        """
        反转 TimeSeries，即执行 y = -y 操作。

        返回：
            TimeSeries：反转后的新 TimeSeries 对象。
        """
        inverted_samples = -self.samples
        new_params = self.params.copy()
        new_params['Inverted'] = True
        return TimeSeries(inverted_samples, self.fs, params=new_params)

    def flip(self, axis=0) -> 'TimeSeries':
        """
        翻转 TimeSeries 的样本数据，支持沿指定轴翻转，默认轴为 0。

        参数：
            axis (int)：要翻转的轴。

        返回：
            TimeSeries：翻转后的新 TimeSeries 对象。
        """
        flipped_samples = np.flip(self.samples, axis=axis)
        new_params = self.params.copy()
        new_params['FlippedAxis'] = axis
        return TimeSeries(flipped_samples, self.fs, params=new_params)

    # 计算时间长度
    def time_length(self) -> float:
        return len(self.samples) / self.fs

    def normalize(self) -> 'TimeSeries':
        """
        将TimeSeries样本归一化，使其最大绝对值为1。

        返回：
            TimeSeries：归一化后的新TimeSeries对象。
        """
        max_abs_value = np.max(np.abs(self.samples))
        if max_abs_value == 0:
            normalized_samples = self.samples
        else:
            normalized_samples = self.samples / max_abs_value
        new_params = self.params.copy()
        new_params['NormalizationFactor'] = max_abs_value
        new_ts = TimeSeries(normalized_samples, self.fs, params=new_params)
        return new_ts

    def map(self, func) -> 'TimeSeries':
        """
        将指定函数应用于TimeSeries的样本数据。

        参数：
            func (function)：要应用的函数。
            例如：
            def square(x):
                return x**2
        """
        new_samples = func(self.samples)
        new_params = self.params.copy()
        new_params['AppliedFunction'] = func.__name__
        return TimeSeries(new_samples, self.fs, params=new_params)

    def __str__(self):
        params_str = ', '.join([f'{k}={v}' for k, v in self.params.items()])
        len_samples = len(self.samples)
        return f'TimeSeries(samples={len_samples}, fs={self.fs}, {params_str})'

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.samples)

    def numpy(self):
        return self.samples

    def limit(self, lower_limit=None, upper_limit=None) -> 'TimeSeries':
        """
        限制TimeSeries的样本值在指定范围内。

        参数：
            lower_limit (float)：下限。
            upper_limit (float)：上限。

        返回：
            TimeSeries：限制后的新TimeSeries对象。
        """
        limited_samples = np.clip(self.samples, lower_limit, upper_limit)
        new_params = self.params.copy()
        new_params['LowerLimit'] = lower_limit
        new_params['UpperLimit'] = upper_limit
        return TimeSeries(limited_samples, self.fs, params=new_params)

    def tonumpy(self):
        if isinstance(self.samples, np.ndarray):
            return self.samples
        else:
            return np.array(self.samples)


class TimeDomainSystem:
    def __init__(self):
        self.system_chain = []

    @classmethod
    def cascade_system2(cls, system1, system2):
        this = cls()
        this.system_chain.append(system1)
        this.system_chain.append(system2)
        return this

    def time_response(self, input_sequence: TimeSeries) -> TimeSeries:
        output = input_sequence
        for system in self.system_chain:
            output = system.time_response(output)
        system_name = utilities.getname(self, sys._getframe(1).f_locals)
        output.set_param('name', system_name)
        return output

    def frequency_response_system(self, fs=20000, time_length=10, f_range=(0.5, 150), amplitude=1, use_parallel=True, points=100, f=None, parrallel_for_cores=1):
        return System.frequency_response_from_time_domain(self, fs, time_length, f_range, amplitude, use_parallel, points, f, parrallel_for_cores)


class MappingSystem:
    x = symbols('x')
    symbol = None

    @classmethod
    def fromSymbol(cls, symbol):
        this = cls()
        this.symbol = symbol
        try:
            # 尝试使用 lambdify 创建符号表达式的数值计算函数
            this.func = lambdify(cls.x, symbol, 'numpy')
        except Exception as e:
            print(f"lambdify failed: {e}. Using manual evaluation.")

            # 手动创建一个数值计算函数
            def manual_func(x_val):
                try:
                    # 使用 sympy 的 subs 和 evalf 方法进行手动计算
                    return float(symbol.subs(cls.x, x_val).evalf())
                except Exception as ex:
                    print(f"Manual function evaluation failed: {ex}")
                    return np.nan  # 返回 NaN 以指示计算失败

            # 将手动生成的函数作为 this.func
            this.func = manual_func

        return this

    @classmethod
    def fromFunction(cls, func):
        this = cls()
        this.func = func
        return this

    def time_response(self, input_sequence: TimeSeries) -> TimeSeries:
        output_samples = self.func(input_sequence.samples)
        return TimeSeries(output_samples, input_sequence.fs)


# Duffing 振子类
class DuffingOscillator:
    def __init__(self, alpha=1.0, delta=0.2, f_0=1.5, amplitude=1.0):
        self.alpha = alpha     # 非线性系数
        self.delta = delta     # 阻尼系数
        self.f_0 = f_0         # 自然频率（Hz）
        self.amplitude = amplitude  # 振幅
        self.custom_func = None  # 自定义函数

    @classmethod
    def fromParameters(cls, alpha, delta, f_0):
        this = cls()
        this.alpha = alpha
        this.delta = delta
        this.f_0 = f_0
        return this

    def duffing_equation(self, t, y, input_sequence):
        x, v = y
        # 使用 np.interp 从输入时间序列中获取对应时间点的输入信号值 u(t)
        u_t = np.interp(t, input_sequence.time, input_sequence.samples)
        omega_0 = 2 * np.pi * self.f_0  # 将频率转换为角频率
        dxdt = v
        dvdt = u_t - 2 * self.delta * omega_0 * v - omega_0**2 * x - self.alpha * x**3
        return [dxdt, dvdt]

    def time_response(self, input_sequence: TimeSeries) -> TimeSeries:
        # 使用 Duffing 振子方程计算时域响应，输入信号作为外部驱动力
        t_span = (0, len(input_sequence.samples) / input_sequence.fs)
        t_eval = input_sequence.time
        y0 = [0.0, 0.0]  # 初始条件 [位移, 速度]
        # 将 input_sequence 作为参数传递给 duffing_equation 函数
        sol = solve_ivp(self.duffing_equation, t_span, y0,
                        t_eval=t_eval, args=(input_sequence,))

        # 只返回位移作为输出，并应用振幅比例
        output_samples = sol.y[0] * self.amplitude
        return TimeSeries(output_samples, input_sequence.fs)


def butter_lowpass_filter(signal, cutoff, fs, order=5):
    """
    低通滤波器，用于抗混叠滤波
    """
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    filtered_signal = filtfilt(b, a, signal)
    return filtered_signal


def amplitude_correction_factor(window_type, n_samples):
    """
    计算用于幅度校正的因子
    """
    if window_type == 'hann':
        return 2


def amplitude_detection(signal, fs, f_sin, window_type='hann', cutoff=None, debug=False):
    """
    计算信号的幅度，增加抗混叠滤波，加窗并进行幅度修正
    """
    # 去除直流分量
    signal_ac = signal - np.mean(signal)

    # 如果指定了截止频率，进行抗混叠滤波
    if cutoff is not None:
        signal_ac = butter_lowpass_filter(signal_ac, cutoff, fs)

    # 加窗
    window = get_window(window_type, len(signal_ac))
    windowed_signal = signal_ac * window

    # 计算窗口导致的幅度修正因子
    correction_factor = amplitude_correction_factor(
        window_type, len(signal_ac))

    # 计算加窗后的信号的 FFT 幅度
    fft_result = np.fft.fft(windowed_signal)
    fft_abs = np.abs(fft_result) / len(windowed_signal) * 2

    # 只取正频率部分
    freqs = np.fft.fftfreq(len(windowed_signal), d=1/fs)
    positive_freqs = freqs[:len(freqs) // 2]
    positive_fft_abs = fft_abs[:len(fft_abs) // 2]

    # 找到最接近目标频率的频率分量的索引
    target_index = np.argmin(np.abs(positive_freqs - f_sin))

    # 获取目标频率分量的幅度并进行修正
    amplitude = positive_fft_abs[target_index] * correction_factor

    if debug:
        # 如果 figure 尚未创建，则创建
        if not plt.get_fignums():
            plt.figure(figsize=(10, 6))

        plt.clf()  # 清空当前 figure

        plt.subplot(2, 1, 1)
        plt.plot(windowed_signal, label='Windowed Signal')
        plt.legend()
        plt.title('Time Domain')
        plt.grid(True)

        plt.subplot(2, 1, 2)
        plt.loglog(positive_freqs, positive_fft_abs)
        plt.title('FFT')
        plt.grid(True)
        plt.axvline(x=f_sin, color='r', linestyle='--', label='f_sin')
        plt.legend()

        plt.tight_layout()
        plt.pause(0.01)  # Pause to allow plot to update
        plt.cla()

    return amplitude


def phase_detection_shift_correlation(signal, reference, fs, target_frequency, max_shift=None, num_shifts=180, debug=False):
    """
    Use the shift correlation method to calculate the phase difference of the signal at the target frequency.

    Parameters:
    - signal: The output signal from the system (numpy array).
    - reference: The input reference signal (numpy array).
    - fs: Sampling frequency (float).
    - target_frequency: The frequency of interest (float).
    - max_shift: Maximum time shift to consider (float). Defaults to one period of the target frequency.
    - num_shifts: Number of shifts to evaluate (int).

    Returns:
    - delta_phi: The phase difference between the signal and reference at the target frequency (float).
    """
    # Remove DC components
    signal_ac = signal - np.mean(signal)
    reference_ac = reference - np.mean(reference)

    # Number of samples
    n_samples = len(signal_ac)

    # Time vector
    t = np.arange(n_samples) / fs

    # Set the maximum shift
    if max_shift is None:
        # Maximum shift is one period
        max_shift = 1 / target_frequency

    # Generate shift times
    shift_times = np.linspace(-max_shift, max_shift, num_shifts)

    # Calculate the maximum shift in samples
    max_shift_samples = int(np.ceil(abs(max_shift) * fs))

    # Ensure there is an overlapping region after shifts
    if 2 * max_shift_samples >= n_samples:
        raise ValueError("Max shift results in zero overlapping samples.")

    # Define the valid indices where overlapping occurs for all shifts
    valid_indices = np.arange(max_shift_samples, n_samples - max_shift_samples)
    signal_ac_valid = signal_ac[valid_indices]
    t_valid = t[valid_indices]

    # Prepare to store correlation results
    correlations = []

    if debug:
        plt.figure()
    # Loop over each shift value
    for shift in shift_times:
        # Shift the reference signal in time
        shifted_ref = reference_ac[valid_indices + int(shift * fs)]

        # Compute the correlation (dot product) over the overlapping region
        correlation = np.dot(signal_ac_valid, shifted_ref)
        correlations.append(correlation)
        if debug:
            plt.plot(t_valid, signal_ac_valid, label='Signal')
            plt.plot(t_valid, shifted_ref, label='Shifted Reference')
            plt.title(f"Shift = {shift:.2f}, Correlation = {correlation:.2f}")
            plt.legend()
            plt.grid(True)
            plt.pause(0.1)
        continue

    # Convert correlations list to a numpy array
    correlations = np.array(correlations)

    # Find the shift corresponding to the maximum correlation
    max_index = np.argmax(correlations)
    delta_t_max = shift_times[max_index]

    # Calculate the phase difference
    delta_phi = 2 * np.pi * target_frequency * delta_t_max

    # Limit the phase difference to the range [-pi, pi]
    delta_phi = np.arctan2(np.sin(delta_phi), np.cos(delta_phi))

    # transfer to degree
    delta_phi = np.rad2deg(delta_phi)

    # Return the phase difference
    return delta_phi


def phase_detection(signal, reference, fs, target_frequency, window_type='hann', cutoff=None, debug=False):
    """
    计算信号在目标频率上的相位，使用FFT和加窗处理
    """
    # 处理输入信号
    def process_signal(input_signal):
        # 去除直流分量
        signal_ac = input_signal - np.mean(input_signal)

        # 如果指定了截止频率，进行抗混叠滤波
        if cutoff is not None:
            signal_ac = butter_lowpass_filter(signal_ac, cutoff, fs)

        # 加窗
        window = get_window(window_type, len(signal_ac))
        windowed_signal = signal_ac * window

        # 计算 FFT
        n = len(windowed_signal)
        fft_result = np.fft.fft(windowed_signal, n)
        freqs = np.fft.fftfreq(n, d=1/fs)

        return fft_result, freqs

    # 处理信号和参考信号
    fft_signal, freqs_signal = process_signal(signal)
    fft_reference, freqs_reference = process_signal(reference)

    # 找到最接近目标频率的频率分量
    target_index_signal = np.argmin(np.abs(freqs_signal - target_frequency))
    target_index_reference = np.argmin(
        np.abs(freqs_reference - target_frequency))

    # 提取目标频率分量的相位
    phase_signal = np.angle(fft_signal[target_index_signal])
    phase_reference = np.angle(fft_reference[target_index_reference])

    # 计算相位差
    phase_difference = phase_signal - phase_reference

    # 转成角度
    phase_difference = np.rad2deg(phase_difference)

    if debug:
        # 计算目标频率对应的周期（以样本数表示）
        period_samples = int(fs / target_frequency)

        # 打印出参考信号和信号的波形，用竖线标出相位
        plt.figure()
        plt.plot(signal, label='Signal')
        plt.plot(reference, label='Reference')

        # 竖线标记信号和参考信号的下一个周期的起始位置
        plt.axvline(x=target_index_signal + period_samples,
                    color='r', linestyle='--', label='Signal Phase Line')
        plt.axvline(x=target_index_reference + period_samples,
                    color='g', linestyle='--', label='Reference Phase Line')

        plt.legend()
        plt.grid(True)
        plt.title('Time Domain')
        plt.pause(0.1)

    return phase_difference


def process_frequency_response(input_sequence: TimeSeries,
                               output_sequence: TimeSeries,
                               f_sin: float,
                               cutoff: float,
                               window_type='hann',
                               debug=False,
                               period_max=4,
                               period_min=4
                               ) -> Tuple[float, float, float]:
    """
    处理给定的输入和输出序列，计算频率响应。

    参数：
        input_sequence (TimeSeries): 输入信号的 TimeSeries 对象。
        output_sequence (TimeSeries): 输出信号的 TimeSeries 对象。
        f_sin (float): 正弦波频率。
        cutoff (float): 幅值检测的截止频率。
        window_type (str): 幅值检测使用的窗类型。
        debug (bool): 是否启用调试绘图。
        period_max (int): 最大允许周期数。
        period_min (int): 最小允许周期数。

    返回：
        tuple: (f_sin, output_amplitude_ratio, output_phase)
    """
    fs = input_sequence.fs
    # 检查输入和输出序列的采样率是否一致
    if fs != output_sequence.fs:
        raise ValueError("输入和输出序列的采样率必须一致。")

    # 计算每个周期的样本数
    period_samples = int(fs / f_sin)

    # 获取信号的总样本数
    total_samples = len(output_sequence.samples)

    # 计算信号包含的完整周期数
    num_periods_in_signal = total_samples // period_samples

    # 检查信号包含的周期数是否在允许范围内
    if num_periods_in_signal < period_min:
        raise ValueError(
            f"信号包含的周期数 {num_periods_in_signal} 小于最小允许周期数 {period_min}。")
    elif num_periods_in_signal > period_max:
        # 限制信号长度为最大允许周期数
        num_periods_in_signal = period_max

    # 计算截取后的信号长度
    signal_length = num_periods_in_signal * period_samples

    # 截取信号长度为整数周期数(从后往前截取)
    signal_trimmed = output_sequence.samples[-signal_length:]
    input_trimmed = input_sequence.samples[-signal_length:]

    # 取信号的后半部分
    half_length = signal_length // 2
    last_half_signal = signal_trimmed[-half_length:]
    last_half_reference = input_trimmed[-half_length:]

    # 确保后半部分的信号长度是周期的整数倍
    num_periods_last_half = half_length // period_samples
    if num_periods_last_half == 0:
        raise ValueError("用于幅值检测的信号不足一个周期。")
    last_half_length = num_periods_last_half * period_samples
    last_half_signal = last_half_signal[:last_half_length]
    last_half_reference = last_half_reference[:last_half_length]

    # 检查后半部分的信号是否为空
    if len(last_half_signal) == 0:
        raise ValueError("用于幅值检测的信号为空。")

    if debug:
        plt.figure()
        plt.plot(last_half_signal, label='Last Half Signal')
        plt.plot(last_half_reference, label='Last Half Reference')
        plt.legend()
        plt.grid(True)
        plt.show()

    # 调用幅值检测函数
    output_amplitude = amplitude_detection(
        last_half_signal, fs, f_sin, window_type, cutoff)

    input_amplitude = amplitude_detection(
        last_half_reference, fs, f_sin, window_type, cutoff)

    # 调用相位检测函数
    output_phase = phase_detection(
        last_half_signal, last_half_reference, fs, f_sin)

    # 计算输出与输入的幅值比
    output_amplitude_ratio = output_amplitude / input_amplitude

    return f_sin, output_amplitude_ratio, output_phase


def generate_sin_response(f_sin, amplitude, fs, time_length, system, min_periods=4, max_periods=4):
    """
    生成给定频率的正弦波并获取系统响应。

    参数：
        f_sin (float): 正弦波频率。
        amplitude (float): 输入信号的幅值。
        fs (int): 采样率。
        time_length (float): 信号持续时间。
        system: 系统对象，具有 time_response 方法。
        min_periods (int): 最小周期数。
        max_periods (int): 最大周期数。

    返回：
        tuple: (input_sequence_trimmed, output_sequence_trimmed)
    """
    # 计算周期并确保至少有 min_periods 个周期
    period_time = 1 / f_sin
    num_periods = max(min_periods, int(time_length * f_sin))
    num_periods = min(max_periods, num_periods)
    total_time = num_periods * period_time

    # 调整 time_length 为整数周期的总时间，多了一倍的时间为了避免 fade 截取后过短
    time_length = total_time * 2

    # 调整幅值（根据频率）
    adjusted_amplitude = amplitude / (2 * np.pi * f_sin)

    # 生成具有调整后时间长度的正弦波输入序列
    input_sequence = TimeSeries.fromSin(
        adjusted_amplitude, f_sin, fs, time_length, fade_in=0.3, fade_out=0.0)

    # 模拟系统对输入序列的响应
    output_sequence = system.time_response(input_sequence)

    # 移除输入和输出序列的渐入部分
    fade_in_samples = int(0.3 * len(output_sequence.samples))
    input_sequence_trimmed = TimeSeries(
        input_sequence.samples[fade_in_samples:], fs)
    output_sequence_trimmed = TimeSeries(
        output_sequence.samples[fade_in_samples:], fs)

    # 检查系统响应是否为空
    if len(output_sequence_trimmed.samples) == 0:
        raise ValueError("移除渐入后系统响应信号长度为零。")

    return input_sequence_trimmed, output_sequence_trimmed


def simulate_frequency(f_sin, amplitude, fs, time_length, system, cutoff, window_type='hann', debug=False, min_periods=4, max_periods=4):
    """
    使用正弦波模拟系统的频率响应，保持原有的 API。

    参数：
        f_sin (float): 正弦波频率。
        amplitude (float): 输入信号的幅值。
        fs (int): 采样率。
        time_length (float): 信号持续时间。
        system: 系统对象，具有 time_response 方法。
        cutoff (float): 幅值检测的截止频率。
        window_type (str): 幅值检测使用的窗类型。
        debug (bool): 是否启用调试绘图。
        min_periods (int): 最小周期数。
        max_periods (int): 最大周期数。

    返回：
        tuple: (f_sin, output_amplitude, output_phase)
    """
    # 第一步：生成正弦波并获取系统响应
    input_sequence, output_sequence = generate_sin_response(
        f_sin, amplitude, fs, time_length, system, min_periods, max_periods)

    # 第二步：分析频率响应
    _, output_amplitude, output_phase = process_frequency_response(
        input_sequence, output_sequence, f_sin, cutoff, window_type, debug)

    return f_sin, output_amplitude, output_phase


class System:
    # 初始化类属性
    s = symbols('s')
    z = symbols('z')
    fig = None  # 用于存储整个图形的引用
    ax_gain = None  # 用于存储幅度子图的轴
    ax_phase = None  # 用于存储相位子图的轴
    f: array
    """ frequency array """
    gain: array
    """ gain array, usually tested by exam """
    phase: array
    """ phase array """
    w: array
    """ angular frequency array """
    number: array
    """ complex value """
    sensitivity: float
    """ sensitivity of the system """
    low_cut_f: float
    """ low cut frequency """
    high_cut_f: float
    """ high cut frequency """
    params: dict
    """ parameters of the system """
    # Class attribute to store colors assigned to instances
    color_map = {}
    auto_shift_phase = False
    phase_range = None
    gain_range = None
    freq_range = None
    # List of common colors in RGB
    common_colors = [
        (0.75, 0, 0),      # Red
        (0, 0, 0.75),      # Blue
        (0, 0.75, 0),      # Green
        (0.75, 0.75, 0),    # Yellow
        (0.75, 0, 0.75),      # Magenta
        (0, 0.75, 0.75),      # Cyan
        (0.5, 0, 0),    # Maroon
        (0.5, 0.5, 0),  # Olive
        (0, 0.2, 0),    # Dark Green
        (0, 0, 0.5),    # Navy
        (1, 0.65, 0),   # Orange
        (0.5, 0.5, 0.5),  # Grey
        (0.75, 0.75, 0.75),  # Silver
        (0.87, 0.72, 0.53),  # Tan
        (0.54, 0.17, 0.89),  # Dark Violet
        # (0.91, 0.91, 0.91),  # Off White
        # (0.82, 0.41, 0.12),  # Chocolate
        # (0.98, 0.5, 0.45),  # Salmon
        # ... add more as needed
    ]

    # Set to keep track of colors already assigned
    used_colors = set()

    @staticmethod
    def parallel(*impedances):
        """
        计算多个阻抗的并联总阻抗
        :param impedances: 并联的阻抗
        :return: 并联总阻抗
        """
        return 1 / sum(1 / Z for Z in impedances)

    def __init__(self,
                 f=array([0]),
                 gain=array([0]),
                 w=array([0]),
                 number=array([0]),
                 phase=array([0]),
                 symbol=None,
                 debug=False):
        self.f = f
        self.gain = gain
        self.w = w
        self.number = number
        self.phase = phase
        self.debug = debug
        self.symbol = symbol
        self.symbol_z = None
        self.tight_layouted = False
        self.params = {}

    @classmethod
    def fromGainPhase(cls, f, gain, phase):
        w = 2 * np.pi * f
        number = gain * np.exp(1j * np.deg2rad(phase))
        return cls(f=f, gain=gain, w=w, number=number, phase=phase)

    @classmethod
    def fromNumber(cls, f, number):
        return cls(f=f, number=number)

    @classmethod
    def fromSymbol(cls, symbol, f=None, f_range=(5, 250)):
        # Set default frequency range f
        if f is None:
            f = np.logspace(np.log10(f_range[0]), np.log10(f_range[1]), 100)

        # Convert to numpy array to ensure numerical array
        f = np.array(f, dtype=np.float64)

        s = cls.s  # System.s

        # If symbol is numeric, create a SymPy expression
        if isinstance(symbol, (int, float)):
            symbol = sympify(symbol)
        elif s not in symbol.free_symbols:
            # If symbol does not contain 's', try to convert to float and then sympify
            try:
                symbol_value = float(symbol)
                symbol = sympify(symbol_value)
            except:
                raise ValueError(
                    "Symbol expression must be a constant or contain the symbol 's'")
        else:
            # Ensure symbol is a SymPy expression
            symbol = sympify(symbol)

        # Angular frequency
        w = 2 * np.pi * f

        # Use lambdify to convert symbolic expression to numerical function
        symbol_func = lambdify(s, symbol, 'numpy')

        # Calculate numerical values
        number = symbol_func(1j * w)

        # Return class instance
        return cls(symbol=symbol, f=f, number=number)

    def bilinear_transform(self, T_sample):
        if self.symbol is None:
            raise ValueError("No symbol expression provided.")
        s = System.s
        T = symbols('T')
        z = System.z
        """ 使用双线性变换将 s 域传递函数转换为 z 域传递函数 """
        # 双线性变换公式： s = (2 / T) * (1 - z**(-1)) / (1 + z**(-1))
        s_to_z = (2 / T) * (1 - z**(-1)) / (1 + z**(-1))

        # 将 s 替换为双线性变换的表达式
        H_z = self.symbol.subs(s, s_to_z)

        # 简化 z 域表达式
        H_z = simplify(H_z)

        # 将 T 替换为采样时间 T_value
        H_z = H_z.subs(T, T_sample)

        H_z = simplify(H_z)

        return H_z

    def time_response_fs(self, input_sequence, fs):
        """ 
        根据 z 域传递函数对输入时间序列进行仿真 
        input_sequence: 输入时间序列 (list or numpy array)
        """
        T_sample = 1 / fs  # 采样时间
        if self.symbol_z is None:
            self.symbol_z = self.bilinear_transform(T_sample)
        H_z = self.symbol_z
        # 将 z 域传递函数表示为多项式比率
        z = System.z
        num, den = H_z.as_numer_denom()  # 分子和分母
        num = Poly(num, z)  # 将分子多项式化
        den = Poly(den, z)  # 将分母多项式化

        # 获取多项式系数 (从高次到低次)
        b = np.array(num.all_coeffs(), dtype=np.float64)
        a = np.array(den.all_coeffs(), dtype=np.float64)

        # 正常化系数 a[0]，使 a[0] = 1
        fix_ratio = a[0]
        a = a / fix_ratio
        b = b / fix_ratio

        # 仿真输入序列的长度
        N = len(input_sequence)
        # 确保输入序列为 numpy 数组
        input_sequence = np.array(input_sequence, dtype=np.float64)
        # 初始化输出序列
        output_sequence = np.zeros(N, dtype=np.float64)

        # 使用差分方程计算输出 y[n]
        for n in range(N):
            # 输入部分计算
            for i in range(len(b)):
                if n - i >= 0:
                    output_sequence[n] += b[i] * input_sequence[n - i]
            # 输出反馈部分计算
            for j in range(1, len(a)):
                if n - j >= 0:
                    output_sequence[n] -= a[j] * output_sequence[n - j]

        return output_sequence

    def get_iir_parameters(self, fs):
        """
        Returns the IIR filter parameters (b0, b1, b2, a0, a1, a2)
        based on the bilinear transform.
        """
        # Perform bilinear transformation to obtain the z-domain transfer function
        T_sample = 1 / fs  # Sampling time
        H_z = self.bilinear_transform(T_sample)

        # Get the numerator and denominator polynomials in z
        z = System.z
        num, den = H_z.as_numer_denom()  # Get numerator and denominator
        num = Poly(num, z)  # Convert to polynomial form
        den = Poly(den, z)  # Convert to polynomial form

        # Get polynomial coefficients (from highest to lowest order)
        b = np.array(num.all_coeffs(), dtype=np.float64)
        a = np.array(den.all_coeffs(), dtype=np.float64)

        # Normalize coefficients such that a[0] = 1
        fix_ratio = a[0]
        a = a / fix_ratio
        b = b / fix_ratio

        # Pad after the original elements to ensure [a, 0, 0] instead of [0, 0, a]
        b = np.pad(b, (0, 3 - len(b)), 'constant', constant_values=(0, 0))
        a = np.pad(a, (0, 3 - len(a)), 'constant', constant_values=(0, 0))

        # Return IIR parameters (b0, b1, b2, a0, a1, a2)
        b0, b1, b2 = b[:3]
        a0, a1, a2 = a[:3]

        return b0, b1, b2, a0, a1, a2

    def time_response(self, input_sequence: TimeSeries, show_tick=False) -> TimeSeries:
        tic = time.time()
        resposne = self.time_response_fs(
            input_sequence.samples, input_sequence.fs)
        system_name = utilities.getname(self, sys._getframe(1).f_locals)
        ts = TimeSeries(resposne, input_sequence.fs)
        ts.set_param('name', system_name)
        ts.set_param('InputParams', input_sequence.params)
        toc = time.time()
        if show_tick:
            print(f'{system_name} time response: {toc - tic:.2f} s')
        return ts

    def merge_params(self, System: 'System'):
        for key in System.params:
            self.params[key] = System.params[key]

    def set_param(self, key, value):
        self.params[key] = value

    def get_param(self, key):
        if key in self.params:
            return self.params[key]
        callingframe = sys._getframe(1)
        locals = callingframe.f_locals
        name = utilities.getname(self, locals)
        print(f'\'{key}\' not in params from System <{name}>')
        return None

    def calculate_cs(self, f_range=None):
        """
        使用三次样条插值计算系统的增益。
        """
        f = self.f
        gain = self.gain
        if f_range is not None:
            index = np.where((f >= f_range[0]) & (f <= f_range[1]))
            f = f[index]
            gain = gain[index]
        self.cs = CubicSpline(f, gain)
        return self.cs

    def transfer_frequency(self, new_freq: list):
        """
        用新的频率数组替换原有的频率数组。
        然后用插值重新计算增益和相位。
        """
        old_f = self.f
        old_gain = self.toabs()
        old_phase = self.tophase()
        self.calculate_cs()
        self.gain = self.cs(new_freq)
        self.phase = self.cs(new_freq, 1)
        self.f = new_freq
        # reset the number
        self.number = array([0])
        self.number = self.tonumber()
        return self

    def multiply_value(self, value: float):
        self.number = self.number * value
        self.gain = self.gain * value
        return self

    def calculate_sensitivity(self, reference_frequency=3.0):
        """
        计算系统在指定频率（默认为3Hz）的灵敏度。
        """
        # 如果指定频率不在数组中，使用插值
        cs = self.calculate_cs()
        self.sensitivity = cs(reference_frequency)
        if self.debug:
            print('sensitivity: ', self.sensitivity)
        self.sensitivity = float(self.sensitivity)
        return self.sensitivity

    def calculate_high_cut_frequency(self, **args):
        self.calculate_cut_frequency(**args)
        return self.high_cut_f

    def calculate_low_cut_frequency(self, **args):
        self.calculate_cut_frequency(**args)
        return self.low_cut_f

    def calculate_gain(self, frequency):
        """
        使用插值计算指定频率的增益。
        """
        cs = self.calculate_cs(f_range=(min(frequency), max(frequency)))
        return cs(frequency)

    def calculate_cut_frequency(self,
                                sensitivity=None,
                                use_linear_interp=False,
                                below_Hz=3.0
                                ):
        """
        使用插值计算低于3Hz的低频截止频率。
        """
        self.calculate_sensitivity()

        # 只考虑3Hz以下的频率
        below_Hz_indices = np.where(self.f < below_Hz)
        frequencies_below_Hz = self.f[below_Hz_indices]
        gains_below_Hz = self.toabs()[below_Hz_indices]

        if sensitivity is None:
            sensitivity = self.sensitivity

        # -3dB点是灵敏度下降到最大增益的0.707倍
        target_sensitivity = sensitivity * np.sqrt(0.5)

        # 插值（只针对3Hz以下的数据）
        try:
            cs_below_3Hz = CubicSpline(frequencies_below_Hz, gains_below_Hz)
            # 生成更细的频率数据以寻找-3dB点（只在3Hz以下）
            fine_frequencies_below_Hz = np.linspace(
                frequencies_below_Hz.min(), frequencies_below_Hz.max(), 1000)
            if use_linear_interp:
                fine_sensitivities_below_Hz = np.interp(
                    fine_frequencies_below_Hz, frequencies_below_Hz, gains_below_Hz)
            else:
                fine_sensitivities_below_Hz = cs_below_3Hz(
                    fine_frequencies_below_Hz)

            # 找到最接近目标灵敏度的频率点（3Hz以下）
            # 遍历从3Hz开始，向下寻找-3dB点
            self.low_cut_f = min(self.f)
            for i in range(len(fine_frequencies_below_Hz) - 1, -1, -1):
                if fine_sensitivities_below_Hz[i] <= target_sensitivity:
                    self.low_cut_f = fine_frequencies_below_Hz[i]
                    break

            if self.debug:
                print('low cut frequency: ', self.low_cut_f)

        except:
            print(f'Error in calculate_cut_frequency: {sys.exc_info()}')
            self.low_cut_f = -1

        # 查找高频截止频率
        # 只考虑3Hz以上的频率
        above_Hz_indices = np.where(self.f > below_Hz)
        frequencies_above_Hz = self.f[above_Hz_indices]
        gains_above_Hz = self.toabs()[above_Hz_indices]

        # 三次样条插值（只针对3Hz以上的数据）
        cs_above_Hz = CubicSpline(frequencies_above_Hz, gains_above_Hz)

        # 生成更细的频率数据以寻找-3dB点（只在3Hz以上）
        fine_frequencies_above_Hz = np.linspace(
            frequencies_above_Hz.min(), frequencies_above_Hz.max(), 1000)
        if use_linear_interp:
            fine_sensitivities_above_Hz = np.interp(
                fine_frequencies_above_Hz, frequencies_above_Hz, gains_above_Hz)
        else:
            fine_sensitivities_above_Hz = cs_above_Hz(
                fine_frequencies_above_Hz)
            # -3dB点是灵敏度下降到最大增益的0.707倍

        target_sensitivity = sensitivity * np.sqrt(0.5)

        # 找到最接近目标灵敏度的频率点（3Hz以上）
        # 遍历从3Hz开始，向上寻找-3dB点
        self.high_cut_f = max(self.f)
        for i in range(len(fine_frequencies_above_Hz)):
            if fine_sensitivities_above_Hz[i] <= target_sensitivity:
                self.high_cut_f = fine_frequencies_above_Hz[i]
                break

        if self.debug:
            print('high cut frequency: ', self.high_cut_f)

        return self.low_cut_f

    def todict(self):
        self.calculate_sensitivity()
        self.calculate_cut_frequency()
        return {
            'f': self.f.tolist(),
            'gain': self.gain.tolist(),
            'w': self.w.tolist(),
            # 'number': self.number.tolist(),
            'phase': self.tophase().tolist(),
            'abs': self.toabs().tolist(),
            'sensitivity': self.sensitivity,
            "low_cut_f": self.low_cut_f,
            'high_cut_f': self.high_cut_f
        }

    def clone(self) -> 'System':
        return System(self.f, self.gain, self.w, self.number, self.phase)

    def toabs(self):
        if len(self.gain) > 1:
            res = self.gain
        else:
            res = abs(self.number)
        # fix nan or inf to 0
        res = [0 if np.isnan(x) or np.isinf(x) else x for x in res]
        return res

    def tophase(self):
        phase = []
        if len(self.phase) > 1:
            phase = self.phase
        elif len(self.number) > 1:
            phase = np.angle(self.number, deg=True)

        # 调用 shift_phase True来平移和标准化相位
        if self.auto_shift_phase:
            phase = shift_phase(phase)

        return phase

    def tonumber(self):
        if len(self.number) > 1:
            return self.number

        # calculate number from gain and phase
        if len(self.gain) > 1 and len(self.phase) > 1:
            return self.gain * np.exp(1j * np.deg2rad(self.phase))

        raise ValueError("Cannot calculate number from gain and phase")

    @staticmethod
    def makecolor(hash_value: int):
        """
        根据哈希值从预定义的颜色列表中选择一个颜色。
        如果所有颜色都被使用，生成一个新的随机颜色。
        """
        if len(System.used_colors) >= len(System.common_colors):
            # 生成新颜色
            import random
            random.seed(hash_value)
            color = (random.random(), random.random(), random.random())
        else:
            index = (hash_value + 1) % len(System.common_colors)
            color = System.common_colors[index]
            while color in System.used_colors:
                index = (index + 1) % len(System.common_colors)
                color = System.common_colors[index]
            System.used_colors.add(color)
        return color

    def plot(self, marker='o', markersize=7, time_domin=False, label=None,
             use_parallel=False, legend=True, gain_range=None, phase_range=None,
             freq_range=None, linestyle='-', disable_phase=False):
        """
        在同一个图上绘制系统的幅度和相位响应。
        总是使用左右子图来分别展示幅度和相位。
        """

        if time_domin:
            gain_time_domin = self.to_gain_time_domain(
                use_parallel=use_parallel)

        if label is not None:
            system_name = label
        else:
            system_name = utilities.getname(self, sys._getframe(1).f_locals)

        if system_name not in System.color_map:
            System.color_map[system_name] = System.makecolor(
                hashtimes33(system_name))

        instance_color = System.color_map[system_name]

        if not disable_phase:
            if System.fig is None or System.ax_gain is None or System.ax_phase is None:
                System.fig, (System.ax_gain, System.ax_phase) = plt.subplots(
                    1, 2, figsize=(16, 6))
        else:
            if System.fig is None or System.ax_gain is None:
                System.fig, System.ax_gain = plt.subplots(1, 1, figsize=(8, 6))

        # 绘制幅度响应
        System.ax_gain.loglog(
            self.f, self.toabs(), marker=marker, markersize=markersize,
            label=system_name, color=instance_color, linestyle=linestyle
        )
        System.ax_gain.set_xlabel("Frequency (Hz)")
        System.ax_gain.set_ylabel("Amplitude")
        System.ax_gain.grid(True, which="both", ls="--")
        if legend:
            System.ax_gain.legend()

        if not disable_phase:
            # 绘制相位响应
            tophase = self.tophase()
            System.ax_phase.semilogx(
                self.f, tophase, marker=marker, markersize=markersize,
                label=system_name, color=instance_color, linestyle=linestyle
            )

        # 绘制时域仿真结果
        if time_domin:
            System.ax_gain.loglog(
                self.f, gain_time_domin, marker='x', markersize=markersize,
                label=system_name + ' time domin', color='r'
            )
        if not disable_phase:
            System.ax_phase.set_xlabel("Frequency (Hz)")
            System.ax_phase.set_ylabel("Phase (degrees)")
            System.ax_phase.grid(True, which="both", ls="--")
            if legend:
                System.ax_phase.legend()

            # 设置用户指定的显示范围
            if phase_range is not None:
                System.ax_phase.set_ylim(phase_range[0], phase_range[1])

        if freq_range is not None:
            System.ax_gain.set_xlim(freq_range[0], freq_range[1])
            if not disable_phase:
                System.ax_phase.set_xlim(freq_range[0], freq_range[1])

        if gain_range is not None:
            System.ax_gain.set_ylim(gain_range[0], gain_range[1])

        # 调整布局以避免标签重叠
        if not self.tight_layouted:
            # plt.tight_layout()
            self.tight_layouted = True
        # plt.pause(0.01)

    @classmethod
    def loadExcel(cls, file_path) -> "System":
        """
        Class method to load data from an Excel file.

        :param file_path: Path to the Excel file.
        :return: An instance of System populated with data from the Excel file.
        """
        # Read the Excel file
        data = pd.read_excel(file_path)

        # Extract columns into numpy arrays
        f = data['freq'].to_numpy()
        gain = data['gain'].to_numpy()
        phase = data['phase'].to_numpy()

        # Angular frequency (omega) calculation
        w = 2 * np.pi * f

        # Instantiate and return a System object
        return cls(f=f, gain=gain, w=w, phase=phase)

    def saveExcel(self, file_path):
        data = {
            'freq': self.f,
            'gain': self.gain,
            'phase': self.phase
        }
        df = DataFrame(data)
        df.to_excel(file_path, index=False)

    @classmethod
    def loadJson(cls, file_path) -> "System":
        dataAnalyzeResultList = DataAnalyzeResultList()
        dataAnalyzeResultList.load_from_json_file(file_path)
        gain_integrate = np.array(
            [result.gain_integrate for result in dataAnalyzeResultList.dataAnalyzeResults])
        freq = np.array(
            [result.freq for result in dataAnalyzeResultList.dataAnalyzeResults])
        phase_intergrate = np.array(
            [result.phase_integrate for result in dataAnalyzeResultList.dataAnalyzeResults])
        w = 2 * np.pi * freq
        return cls(f=freq, gain=gain_integrate, w=w, phase=phase_intergrate)

    @classmethod
    def loadFile(cls, file_path: str) -> "System":
        # print(f'Loading file: {file_path}')
        if file_path.endswith('.json'):
            return cls.loadJson(file_path)
        if file_path.endswith('.xlsx'):
            return cls.loadExcel(file_path)

    @staticmethod
    def frequency_response_from_time_domain(system: 'System', fs=2000, time_length=10, f_range=(5, 250), amplitude=1, use_parallel=True, points=100, f=None, parrallel_for_cores=1):
        # 记录起始时间
        start_time = time.time()

        # 初始化幅频特性数据
        if f is None:
            f = np.logspace(np.log10(f_range[0]), np.log10(f_range[1]), points)
        f_response = []
        gain = []  # 存储每个频率对应的输出幅值
        phase = []  # 存储每个频率对应的输出相位

        if use_parallel:
            # 获取物理 CPU 核心数
            num_cores = multiprocessing.cpu_count()
            # 限制并行进程数量，建议为物理核心数的1-2倍
            max_workers = min(int(num_cores*parrallel_for_cores), len(f))
            # 使用ProcessPoolExecutor进行并行计算
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(
                    simulate_frequency, f_sin, amplitude, fs, time_length, system, None) for f_sin in f]
                for future in as_completed(futures):
                    result = future.result()
                    f_sin, output_amplitude, output_phase = result
                    gain.append(output_amplitude)
                    phase.append(output_phase)
                    f_response.append(f_sin)
        else:
            # 单线程逐步计算
            for f_sin in f:
                f_sin, output_amplitude, output_phase = simulate_frequency(
                    f_sin, amplitude, fs, time_length, system, None)
                gain.append(output_amplitude)
                phase.append(output_phase)
                f_response.append(f_sin)

        if use_parallel:
            # 确保gain和phase按照频率顺序排列
            sorted_indices = np.argsort(f_response)
            gain = np.array(gain)[sorted_indices]
            phase = np.array(phase)[sorted_indices]

        # 记录结束时间并打印耗时
        end_time = time.time()
        print(
            f"Frequency respose Execution (Parallel:{use_parallel}): {end_time - start_time:.2f} seconds")

        return System(f=f, gain=gain, phase=phase)

    def to_gain_time_domain(self, fs=2000, time_length=10, use_parallel=True):
        system = System.frequency_response_from_time_domain(
            self, fs, time_length, f_range=(self.f[0], self.f[-1]), points=len(self.f), use_parallel=use_parallel)
        return system.toabs()

    def frequency_response_system(self, fs=20000, time_length=10, f_range=(0.5, 150), amplitude=1, use_parallel=True, points=100, f=None, parrallel_for_cores=1):
        return System.frequency_response_from_time_domain(self, fs, time_length, f_range, amplitude, use_parallel, points, f, parrallel_for_cores)

    @classmethod
    def fromTimeSeries(
        cls,
        input_sequences: List[TimeSeries],
        output_sequences: List[TimeSeries],
        frequencies: List[float],
        cutoff: float = None,
        window_type: str = 'hann',
        use_parallel: bool = True,
        parallel_cores: int = 1,
        debug: bool = False
    ) -> 'System':
        """
        使用给定的输入和输出序列列表，以及对应的频率列表，计算系统的频率响应。

        参数：
            input_sequences (List[TimeSeries]): 输入信号的列表。
            output_sequences (List[TimeSeries]): 输出信号的列表。
            frequencies (List[float]): 对应的频率列表。
            cutoff (float): 幅值检测的截止频率。
            window_type (str): 幅值检测使用的窗类型。
            use_parallel (bool): 是否使用并行计算。
            parallel_cores (int): 并行计算的核心数比例。
            debug (bool): 是否启用调试模式。

        """
        # 验证输入列表的长度是否一致
        if not (len(input_sequences) == len(output_sequences) == len(frequencies)):
            raise ValueError("输入序列、输出序列和频率列表的长度必须一致。")

        gain = []  # 存储每个频率对应的增益
        phase = []  # 存储每个频率对应的相位

        if use_parallel:
            # 获取可用的CPU核心数
            num_cores = multiprocessing.cpu_count()
            max_workers = min(
                int(num_cores * parallel_cores), len(frequencies))

            # 使用ProcessPoolExecutor进行并行计算
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for input_seq, output_seq, freq in zip(input_sequences, output_sequences, frequencies):
                    future = executor.submit(
                        process_frequency_response, input_seq, output_seq, freq, cutoff, window_type, debug)
                    futures.append(future)

                for future in as_completed(futures):
                    try:
                        f_sin, output_amplitude, output_phase = future.result()
                        gain.append(output_amplitude)
                        phase.append(output_phase)
                    except Exception as e:
                        print(f"Error processing frequency response: {e}")
                        gain.append(np.nan)
                        phase.append(np.nan)
        else:
            # 单线程计算
            for input_seq, output_seq, freq in zip(input_sequences, output_sequences, frequencies):
                try:
                    f_sin, output_amplitude, output_phase = process_frequency_response(
                        input_seq, output_seq, freq, cutoff, window_type, debug)
                    gain.append(output_amplitude)
                    phase.append(output_phase)
                except Exception as e:
                    print(f"Error processing frequency response: {e}")
                    gain.append(np.nan)
                    phase.append(np.nan)

        # 将结果转换为numpy数组
        frequencies = np.array(frequencies)
        gain = np.array(gain)
        phase = np.array(phase)

        # 按频率排序
        sorted_indices = np.argsort(frequencies)
        frequencies = frequencies[sorted_indices]
        gain = gain[sorted_indices]
        phase = phase[sorted_indices]
        return cls(f=frequencies, gain=gain, phase=phase)


def Wf2_calculate(w, R1, R2, R3, R4, C1, C2, C3):
    s = 1j * w
    Z1 = (1/(s*C1) + R1 + (R2/(s*C2))/(R2+1/(s*C2)))
    Z21 = (1/(s*C3) + R3)
    Z22 = R4
    Z2 = (Z21 * Z22 / (Z21 + Z22))
    H = Z2 / Z1
    return H


class Wf:
    @staticmethod
    def fromPars(f, C1, C2, R1, R2, R3):
        w = 2 * np.pi * f
        s = 1j * w
        number = -(R2 * (R3 + 1 / (C2 * s))) / ((R1 + 1 / (C1 * s)) *
                                                (R2 + R3 + 1 / (C2 * s)))
        Wf = System()
        Wf.number = number
        Wf.f = f
        return Wf

    @staticmethod
    def fromPars2(f, R1=10e3, R2=43e3, R3=100e3, R4=10e6, C1=4.7e-6, C2=12e-9, C3=3.3e-9):
        w = 2 * np.pi * f
        number = Wf2_calculate(w, R1, R2, R3, R4, C1, C2, C3)
        Wf = System()
        Wf.number = number
        Wf.f = f
        return Wf


class WsWf:
    @staticmethod
    def fromData(data):
        return data.loadWsWf()


def fit_fun(w, A, B, C):
    s = 1j * w
    number = A * s * (1 / (s**2 + C * s + B))
    return abs(number)


class Ws:
    @staticmethod
    def fromWsWfAndWf(WsWf: System, Wf: System) -> System:
        f = WsWf.f
        gain = WsWf.gain / Wf.toabs()
        phase = WsWf.phase - Wf.tophase()
        phase = [phase - 360 if phase > 360 else phase for phase in phase]
        w = 2 * np.pi * f
        return System(f=f, gain=gain, w=w, phase=phase)

    def fit(ws: System, fitRange) -> CFun:
        w = ws.w
        gain = ws.gain

        # Check and adjust fitRange to not exceed w's bounds
        start, end = fitRange[0], fitRange[-1]
        max_index = len(w) - 1
        if start < 0:
            start = 0
            print("Adjusted fit range start to 0.")
        if end > max_index:
            end = max_index
            print(f"Adjusted fit range end to {max_index}.")

        # Ensure start is less than end
        start, end = sorted([start, end])

        # Extracting the fitting range based on the adjusted indices
        x = w[start:end+1]
        y = gain[start:end+1]

        # Curve fitting
        popt, pcov = curve_fit(fit_fun, x, y, p0=[2e4, 3e3, 4e1])
        A, B, C = popt

        # Generating expected y values using the fitting function
        y_exp = [fit_fun(i, A, B, C) for i in x]

        return CFun(A, B, C)

    @staticmethod
    def fromFitCurve(ws: System, cfun: CFun):
        ws_fit = System()
        f = ws.f
        w = 2 * np.pi * f
        A = cfun.A
        B = cfun.B
        C = cfun.C
        s = 1j * w
        number = - A * s * (1 / (s**2 + C * s + B))
        ws_fit.f = ws.f
        ws_fit.number = number
        ws_fit.fit_params = [A, B, C]
        return ws_fit

    @staticmethod
    def fromPhysics(f, D0, w0, qenA, wd):
        w = 2 * np.pi * f
        s = 1j * w
        w_mech = s**2 / (s**2 + 2*D0*w0*s + w0**2)
        w_elch = 2*qenA / (1 + s / wd)
        ws_phy = System()
        ws_phy.number = w_mech * w_elch
        ws_phy.f = f
        return ws_phy

    @staticmethod
    def fromCeilPhysics(f, B, l, c, m, k) -> System:
        """
        (B * l * s^2)/(s^2 + c/m * s + k/m)
        """
        w = 2 * np.pi * f
        s = 1j * w
        number = (B * l * s**2) / (s**2 + c/m * s + k/m)
        ws = System()
        ws.number = number
        ws.f = f
        return ws

    @staticmethod
    def fromCeilWithPassive(f, m, B, l, Rc, Cp, Rp, c, k) -> System:
        w = 2 * np.pi * f
        s = 1j * w

        K0 = B * l
        numerator = m * K0 * s**2
        denominator = (m * s**2 + c * s + k) * (Rc * Cp * s +
                                                Rc / Rp + 1) + (K0 * Cp * s + K0 / Rp) * K0 * s

        H1 = numerator / denominator

        system = System()
        system.number = H1
        system.f = f
        return system

    @staticmethod
    def fromCeilWithPoleZero(f, m, B, l, c, k, omega1, zeta1):
        # 计算中间变量
        K0 = B * l
        omega_0 = (k / m) ** 0.5
        eta_0 = c / (2 * m * omega_0)
        w = 2 * np.pi * f
        s = 1j * w
        numerator = s ** 2 + 2 * eta_0 * omega_0 * s + omega_0 ** 2
        denominator = s ** 2 + 2 * zeta1 * omega1 * s + omega1 ** 2
        H = numerator / denominator
        ws = System()
        ws.number = H
        ws.f = f
        return ws


class Wa:
    @staticmethod
    def fromKa(f, Ka):
        wa = System()
        w = 2 * np.pi * f
        s = 1j * w
        wa.number = (1 / Ka) * 1 / s
        wa.f = f
        return wa


class Wfb:
    @staticmethod
    def fromKpKd(w, Kp, Kd):
        wfb = System()
        s = 1j * w
        wfb.number = Kp + Kd * s
        wfb.f = w / 2 / np.pi
        return wfb

    @staticmethod
    def fromCircuit1(f, R1=56e3, R2=29.4e3, R5=90, R10=10, RL=10, C1=0.220e-9, C2=23.5e-6, C3=0.1e-6, L1=14.5e-3):
        # 转换频率为角频率
        w = 2 * np.pi * np.array(f)
        s = 1j * w

        # 定义电阻等效值
        R3 = R1
        R4 = R2
        R334 = R3 / (R3 + R4)

        # 计算复频域中各元件的阻抗
        ZL = (RL * C3 * s + 1) * (L1 * s) / ((RL + L1 * s) * C3 * s + 1)
        Z2 = R2 / (1 + R2 * C1 * s)
        Z5 = R10 + R5 / (1 + R5 * C2 * s)

        # 计算传递函数 H
        number = (Z2) / (R1 * Z5 + ZL * R334 * (R4 + Z5 - Z2))

        # 创建 System 对象并返回
        wfb = System()
        wfb.number = number
        wfb.f = f
        return wfb

    @staticmethod
    def fromCircuit2(f, R1=56e3, R2=29.4e3, C2=220e-12, R5=10, R6=18e3, C6=47e-6, R10=10, C10=100e-9, R11=150, L11=14.5e-3, Ka=1):
        # 转换频率为角频率
        w = 2 * np.pi * np.array(f)
        s = 1j * w

        # 定义电阻和电容等效值
        C7 = C6

        # 计算复频域中各元件的阻抗
        """
            Z5 = (C6 + C7)||(R6) + R5
            Z6 = (R10 + C10) || (R11 + L11)
            \frac{V_x}{v_1} = \frac{R_2}{R_1} * \frac{Z_6}{Z_5} * \frac{R_1 + R_2}{Z_6 - (R_1 + R_2)}
        """
        Z2 = System.parallel(R2, 1 / (C2 * s))
        Z5 = System.parallel(1 / (C6 * s) + 1 / (C7 * s), R6) + R5
        Z6 = System.parallel(R10 + 1 / (C10 * s), R11 + L11 * s)

        # 计算传递函数 H
        number = (Z2 / R1) * (Z6 / Z5) * ((R1 + R2) / (Z6 - (R1 + R2)))
        number = number * 2    # 乘 2 是因为差分输出, Ka 是电流到力的转换系数
        number = number / (R11 + L11 * s)  # 转为负载线圈的电流输出
        number = number * Ka  # 乘 Ka 是因为电流到力的转换系数
        number = number * 1 / s  # 乘 1/s 是转为速度信号
        number = -number  # 变换方向

        # 创建 System 对象并返回
        wfb = System()
        wfb.number = number
        wfb.f = f
        return wfb


class H:
    def fromWsWf(
            Ws: System,
            Wf: System):
        f = Ws.f
        h = System()
        h.number = Ws.number * Wf.number
        h.f = f
        h.w = h.f * 2 * np.pi
        return h


class H0L:
    def fromFitAndPars(cfun: CFun, f, C1, R2):
        A = cfun.A
        B = cfun.B
        C = cfun.C
        s = 1j * 2 * np.pi * f
        h0l = System()
        h0l.number = -A / B * s * C1 * R2 * s
        h0l.f = f
        return h0l


class H0H:
    def fromFitAndPars(cfun: CFun, f, C1, R2, fl):
        A = cfun.A
        B = cfun.B
        C = cfun.C
        phy = (A / B) * C1 * R2
        wl = 2 * np.pi * fl
        S = phy * wl**2
        h0h = System()
        h0h.number = S * np.ones(len(f))
        h0h.f = f
        return h0h


class H0:
    def fromFitAndPars(cfun, f, C1, R2, fl):
        A = cfun.A
        B = cfun.B
        C = cfun.C
        phy = (A / B) * C1 * R2
        wl = 2 * np.pi * fl
        S = phy * wl**2
        s = 1j * 2 * np.pi * f
        h0 = System()
        h0.number = S * s**2 / (s**2 + np.sqrt(2) * np.sqrt(S / phy) * s +
                                S / phy)
        h0.f = f
        return h0


class H_close_simu:
    @staticmethod
    def fromHWfbWa(h: System, wfb: System, Wa: System):
        close = System()
        close.number = h.tonumber() / (
            1 + h.tonumber() * wfb.tonumber() * Wa.tonumber())
        close.f = h.f
        return close

    @staticmethod
    def fromFFb(F: System, Fb: System):
        close = System()
        close.number = F.tonumber() / (1 + F.tonumber() * Fb.tonumber())
        close.f = F.f
        return close

    @staticmethod
    def fromWsWfWfbWa(ws: System, wf: System, wfb0_simply: System, Wa: System):
        h = H.fromWsWf(ws, wf)
        return H_close_simu.fromHWfbWa(h, wfb0_simply, Wa)

    @staticmethod
    def fromHKpKdWa(h: System, Kp, Kd, Wa: System):
        wfb0_simply = Wfb0_simply.fromKpKd(h.f, Kp, Kd)
        return H_close_simu.fromHWfbWa(h, wfb0_simply, Wa)


class H_close_simu_with_G:
    @staticmethod
    def fromHcloseG(h_close_simu: System, G: float):
        h_close_simu_with_G = System()
        h_close_simu_with_G.number = h_close_simu.number * G
        h_close_simu_with_G.gain = h_close_simu.gain * G
        h_close_simu_with_G.f = h_close_simu.f
        return h_close_simu_with_G


class Kp0Kd0:
    @staticmethod
    def fromFitAndPars(cfun: CFun, C1, C2, R1, R2, R3, fl, Ka):
        A = cfun.A
        B = cfun.B
        C = cfun.C
        phy = (A / B) * C1 * R2
        wl = 2 * np.pi * fl
        S = phy * wl**2
        Kp0 = (2**(1 / 2) * Ka * ((B * S) / (A * C1 * R2))**(1 / 2)) / S - (
            B * C2 * Ka) / (A * C1) - (B * Ka * R1) / (A * R2) - (
                C * Ka) / (A * C1 * R2)
        Kd0 = Ka / S - Ka / (A * C1 * R2) - (C * Ka * R1) / (A * R2) - (
            B * C2 * Ka * R1) / A - (C * C2 * Ka) / (A * C1) + (
                B * C2**2 * Ka * R3) / (A * C1)
        return Kp0, Kd0


class Wfb0_simply:
    @staticmethod
    def fromFitAndPars(ws_fit, f, C1, C2, R1, R2, R3, fl, ka):
        Wfb0_simply = System()
        A = ws_fit.A
        B = ws_fit.B
        C = ws_fit.C
        phy = (A / B) * C1 * R2
        wl = 2 * np.pi * fl
        S = phy * wl**2
        s = 1j * 2 * np.pi * f
        number = (ka * s) / S + (2**(1 / 2) * ka * (
            (B * S) /
            (A * C1 * R2))**(1 / 2)) / S - (ka * s) / (A * C1 * R2) - (
                B * C2 * ka) / (A * C1) - (B * ka * R1) / (A * R2) - (
                    C * ka) / (A * C1 * R2) - (C * ka * R1 * s) / (A * R2) - (
                        B * C2 * ka * R1 * s) / A - (C * C2 * ka * s) / (
                            A * C1) + (B * C2**2 * ka * R3 * s) / (A * C1)
        Wfb0_simply.number = number
        Wfb0_simply.f = f
        return Wfb0_simply

    @staticmethod
    def fromKpKd(f, kp: float, kd: float):
        Wfb0_kpkd = System()
        s = 1j * 2 * np.pi * f
        number = kp + kd * s
        abs_ = abs(number)
        Wfb0_kpkd.number = number
        Wfb0_kpkd.f = f
        return Wfb0_kpkd


class Wfb0:

    @staticmethod
    def fromH0WsWfWa(h0: System, ws: System, wf: System, wa: System):
        Wfb0 = System()
        number = (1 / h0.number - 1 / (ws.number * wf.number)) / wa.number
        Wfb0.number = number
        Wfb0.f = ws.f
        return Wfb0

    @staticmethod
    def fromFitAndPars(cfun: CFun, f, C1, C2, R1, R2, R3, fl, ka):
        A = cfun.A
        B = cfun.B
        C = cfun.C
        phy = (A / B) * C1 * R2
        wl = 2 * np.pi * fl
        S = phy * wl**2
        s = 1j * 2 * np.pi * f
        number = (ka / (A * C1 * R2 * s)) * (
            B + (A * C1 * R2 / S) * np.sqrt(2 * B * S / (A * C1 * R2)) * s +
            (A * C1 * R2 / S) * s**2 - (1 / (C2 * R3 * s + 1)) *
            (C1 * R1 * s + 1) * (s**2 + C * s + B))
        Wfb0 = System()
        Wfb0.number = number
        Wfb0.f = f
        return Wfb0


class ParameterData(_DictData):
    pass


class ResultData(_DictData):
    pass


def ws_compensator(ws_origin: System, ws_target: System) -> System:
    A1, B1, C1 = ws_origin.fit_params
    A2, B2, C2 = ws_target.fit_params
    s = System.s
    compensator = System.fromSymbol(
        A2/A1 * (s ** 2 + C1 * s + B1)/(s ** 2 + C2 * s + B2), f=ws_origin.f)
    return compensator


def load_data_json_to_time_sereis(filename) -> Tuple[List[TimeSeries], List[TimeSeries], List[float]]:
    dataRecordList = datastruct.DataRecordList()
    dataRecordList.load_from_json_file(filename)
    input_data = []
    output_data = []
    freq_list = []
    fs = CONF_SAMPLING_RATE
    for dataRecord in dataRecordList.dataRecords:
        input_data.append(TimeSeries(
            dataRecord.ch1_integrate, fs=fs, params=dataRecord.param.params))
        output_data.append(TimeSeries(
            dataRecord.ch2, fs=fs, params=dataRecord.param.params))
        freq_list.append(float(dataRecord.param.params['freq']))
    print(f'loading {len(input_data)} data records')
    return input_data, output_data, freq_list


def test_timeseries_generate():
    # 生成一个正弦波，应用渐入渐出效果并启用调试模式
    sin_wave = TimeSeries.fromSin(
        A=1.0, f=5, fs=1000, time_length=2, fade_in=0.3, fade_out=0.3, debug=True)
    sin_wave.plot()

    # 生成一个方波，应用渐入渐出效果并启用调试模式
    square_wave = TimeSeries.fromSquare(
        A=1.0, f=5, fs=1000, time_length=2, duty=0.3, fade_in=0.3, fade_out=0.3, debug=True)
    square_wave.plot()

    # 生成一个三角波，应用渐入渐出效果并启用调试模式
    triangle_wave = TimeSeries.fromTriangle(
        A=1.0, f=5, fs=1000, time_length=2, fade_in=0.3, fade_out=0.3, debug=True)
    triangle_wave.plot()

    # 生成一个锯齿波，应用渐入渐出效果并启用调试模式
    sawtooth_wave = TimeSeries.fromSawtooth(
        A=1.0, f=5, fs=1000, time_length=2, width=0.7, fade_in=0.3, fade_out=0.3, debug=True)
    sawtooth_wave.plot()

    # 生成一个线性间隔的时间序列，应用渐入渐出效果并启用调试模式
    linspace_ts = TimeSeries.fromLinspace(
        start=-10, stop=10, fs=1000, time_length=2, fade_in=0.0, fade_out=0.0, debug=True)
    linspace_ts.plot()

    # 生成一个对数间隔的时间序列，应用渐入渐出效果并启用调试模式
    logspace_ts = TimeSeries.fromLogspace(
        start=1, stop=1000, fs=1000, time_length=2, fade_in=0.0, fade_out=0.0, debug=True)
    logspace_ts.plot()

    plt.show()


if __name__ == "__main__":
    test_timeseries_generate()
