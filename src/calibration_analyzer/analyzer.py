from __future__ import annotations
from .datastruct import DataRecord, DataRecordList
from . import config
from .utilities import shift_phase  # 从 utilities 导入，打破循环依赖
import scipy.signal as signal
import numpy as np
import pandas as pd
import json
import argparse
from typing import List, Union
from math import acos, pi
import re
import matplotlib.pyplot as plt


class ChannelAnalyzeResult:
    def __init__(self,
                 channel: Union[List[float], np.ndarray] = None,
                 sampling_rate: float = config.CONF_SAMPLING_RATE):
        if channel is not None:
            self.channel: np.ndarray = np.array(
                channel, dtype=np.float64) * config.CONF_RAW_VOLTAGE_RATEIO
            self.sampling_rate: float = sampling_rate

    def analyze_fft(self, freq_select: float, start_s=0, time_s=1):
        start_idx = int(start_s * self.sampling_rate)
        # 计算频率所对应的周期的样本数
        period_samples = int(self.sampling_rate / freq_select)

        # 计算在time_s内包含的完整周期数
        full_periods = int((time_s * self.sampling_rate) / period_samples)

        # 确保至少有 2 个完整周期
        full_periods = max(config.CONF_DURATION_PERIOD_MIN, full_periods)

        # 不超过 5 个完整周期
        full_periods = min(config.CONF_DURATION_PERIOD_MAX, full_periods)

        if config.CONF_USING_ANTI_ALIASING:
            full_periods += 1

        # 计算结束索引，使其为完整周期的样本数
        end_idx = start_idx + full_periods * period_samples

        self.start_s = start_s
        # Update time_s to reflect the actual time of the full periods
        self.time_s = end_idx / self.sampling_rate
        # 如果截取范围超过了原数据的范围，则自动从末尾向前截取
        len_select = end_idx - start_idx
        if end_idx > len(self.channel):
            print('Warning: 截取范围超过了原数据的范围，自动从末尾向前截取')
            start_idx = len(self.channel) - len_select
            if start_idx < 0:
                start_idx = 0
            end_idx = start_idx + len_select
        data_selected = self.channel[start_idx:end_idx]

        if config.CONF_USING_ANTI_ALIASING:
            # 设计巴特沃斯滤波器
            nyquist_freq = 0.5 * self.sampling_rate
            cutoff_freq = min(config.CONF_ANTI_ALIASING_FREQ,
                              nyquist_freq)  # 上限5kHz
            b, a = signal.butter(4, cutoff_freq/nyquist_freq, 'low')
            # 应用滤波器
            data_filtered = signal.lfilter(b, a, data_selected)

            if period_samples >= len(data_filtered):
                print('Warning: 抗混叠滤波:采样点数过少，无法去除第一个周期')
                data_filtered = data_selected
            else:
                # 扔掉第一个周期
                data_filtered = data_filtered[period_samples:]
        else:
            data_filtered = data_selected

        USING_DEBUG = False
        if USING_DEBUG:
            # 绘制滤波前的时域波形
            plt.figure(figsize=(10, 6))
            plt.subplot(2, 1, 1)
            plt.plot(data_selected, 'b')
            plt.title('Original Signal')
            plt.xlabel('Sample')
            plt.ylabel('Amplitude')

            # 绘制滤波后的时域波形
            plt.subplot(2, 1, 2)
            plt.plot(data_filtered, 'r')
            plt.title('Filtered Signal')
            plt.xlabel('Sample')
            plt.ylabel('Amplitude')

            plt.tight_layout()
            plt.show()

        if config.CONF_USING_HANNING:
            # fft 前加窗
            data_filtered *= np.hanning(len(data_filtered))

        self.fft = np.fft.fft(data_filtered)

        self.fft_abs = np.abs(self.fft) / len(data_filtered) * 2
        if config.CONF_USING_HANNING:
            # 汉宁窗幅值恢复系数
            self.fft_abs = self.fft_abs * 2
        self.fft_freq = np.fft.fftfreq(
            len(self.fft_abs), 1 / self.sampling_rate)
        self.get_ifft(freq_select)

    def get_index(self, freq_select: float):
        # 计算频率选择与每个频率的距离
        distances = np.abs(self.fft_freq - freq_select)

        # 找到最小距离对应的索引
        index = np.argmin(distances)
        return index

    def get_power(self,
                  freq_select: float,
                  freq_ratio=config.CONF_FREQ_RATIO):
        if freq_ratio == 1:
            # Find the index closest to freq_select
            index = self.get_index(freq_select)
            return self.fft_abs[index]
        else:
            lower_freq = freq_select / freq_ratio
            upper_freq = freq_select * freq_ratio
            lower_index = self.get_index(lower_freq)
            upper_index = self.get_index(upper_freq)
            return sum(self.fft_abs[lower_index:upper_index + 1])

    def get_amp(self,
                freq_select: float,
                freq_ratio=config.CONF_FREQ_RATIO):
        if config.CONF_USING_IFFT:
            return None
        return self.get_power(freq_select, freq_ratio)

    def get_ifft(self, freq_select: float):
        index_p = self.get_index(freq_select)
        index_n = self.get_index(-freq_select)

        # clear all other frequencies
        temp_fft = self.fft.copy()
        temp_fft[:index_p] = 0
        temp_fft[index_p+1:index_n] = 0
        temp_fft[index_n+1:] = 0

        # Perform the inverse FFT
        self.ifft = np.fft.ifft(temp_fft)

        # Optional: Take the real part if the imaginary part is negligible
        self.ifft = np.real(self.ifft)

        # Optional: Plotting
        # import matplotlib.pyplot as plt
        # plt.plot(self.ifft)
        # plt.show()

    def get_phase(self,
                  freq_select: float,
                  freq_ratio=config.CONF_FREQ_RATIO) -> float:
        if config.CONF_USING_IFFT:
            return None

        if freq_ratio == 1:
            # Find the index closest to freq_select
            index = self.get_index(freq_select)
            complex_freq = self.fft[index]
            amplitude = np.abs(complex_freq)
            phase_radians = np.angle(complex_freq)
            phase_degrees = np.degrees(phase_radians)
            return phase_degrees

        lower_freq = freq_select / freq_ratio
        upper_freq = freq_select * freq_ratio
        lower_index = self.get_index(lower_freq)
        upper_index = self.get_index(upper_freq)

        weighted_sin_sum = 0
        weighted_cos_sum = 0
        weight_sum = 0

        for index in range(lower_index, upper_index + 1):
            complex_freq = self.fft[index]
            amplitude = np.abs(complex_freq)
            phase_radians = np.angle(complex_freq)

            # 加权
            weighted_sin_sum += amplitude * np.sin(phase_radians)
            weighted_cos_sum += amplitude * np.cos(phase_radians)
            weight_sum += amplitude

        # 防止除以0
        if weight_sum != 0:
            average_phase_radians = np.arctan2(
                weighted_sin_sum / weight_sum, weighted_cos_sum / weight_sum)
        else:
            average_phase_radians = 0

        # 将平均相位转换为度
        average_phase_degrees = np.degrees(average_phase_radians)

        # 标准化到[0, 360)度范围
        average_phase_degrees = np.mod(average_phase_degrees, 360)
        return average_phase_degrees

    def analyze_indicators(self,
                           freq_select: float,
                           freq_ratio=config.CONF_FREQ_RATIO,
                           dc_threshold=5,
                           high_freq_threshold=5000):
        if dc_threshold > freq_select / 2:
            dc_threshold = freq_select / 2
        if high_freq_threshold < freq_select * 2:
            high_freq_threshold = freq_select * 2
        n = len(self.fft_abs)
        freq_bin = self.sampling_rate / n

        # 确定直流分量阈值和高频阈值对应的索引
        dc_index = int(dc_threshold / freq_bin)
        high_freq_index = int(min(n, high_freq_threshold / freq_bin))

        # 计算主频率及其邻近频率的幅度总和
        main_freq_power = self.get_power(freq_select, freq_ratio)

        # 计算主频率的幅度
        main_freq_amplitude = self.get_amp(freq_select, freq_ratio)
        # 计算freq_select的相位（°）
        phase = self.get_phase(freq_select, freq_ratio)

        # 计算失真度，排除直流分量和高于高频阈值的分量
        total_power = sum(self.fft_abs[dc_index:high_freq_index])
        distortion = (total_power - main_freq_power) / \
            main_freq_power

        # 计算总谐波失真
        base_power = self.get_power(freq_select, freq_ratio)
        harmic_power_sum = 0
        harmic_freq_select = freq_select
        while True:
            harmic_freq_select *= 2
            if harmic_freq_select > high_freq_threshold:
                break
            harmic_power_sum += self.get_power(
                harmic_freq_select, freq_ratio) ** 2
        thd = (harmic_power_sum ** 0.5) / base_power

        # 保存计算结果
        self.thd = thd
        self.main_freq_amplitude = main_freq_amplitude
        self.distortion = distortion
        self.phase = phase

    def to_dict(self):
        return {
            'sampling_rate': self.sampling_rate,
            'start_s': self.start_s,
            'time_s': self.time_s,
            'main_freq_amplitude': self.main_freq_amplitude,
            'distortion': self.distortion,
            'thd': self.thd,
            'phase': self.phase,
            # 'fft_abs': self.fft_abs
        }

    def load_from_dict(self, data: dict):
        self.sampling_rate = data['sampling_rate']
        self.start_s = data['start_s']
        self.time_s = data['time_s']
        self.main_freq_amplitude = data['main_freq_amplitude']
        self.distortion = data['distortion']
        self.thd = data['thd']
        self.phase = data['phase']
        # self.fft_abs = data['fft_abs']


class DataAnalyzeResult:
    def __init__(self,
                 record: DataRecord = None,
                 sample_rate=config.CONF_SAMPLING_RATE):
        self.sample_rate = sample_rate
        if record is not None:
            self.record: DataRecord = record
            self.freq: float = float(record.param.params['freq'])
            self.ch1Result = ChannelAnalyzeResult(
                record.ch1, sampling_rate=self.sample_rate)
            self.ch2Result = ChannelAnalyzeResult(
                record.ch2, sampling_rate=self.sample_rate)
            self.ch1IntegrateResult = ChannelAnalyzeResult(
                record.ch1_integrate,
                sampling_rate=self.sample_rate)

    def analyze_delta_ifft(self, ch1: ChannelAnalyzeResult, ch2: ChannelAnalyzeResult):
        # IFFT 已经是纯净的频率分量，不需要再进行频率选择
        # get amp IFFT
        A = np.max(np.abs(ch1.ifft))
        B = np.max(np.abs(ch2.ifft))
        # I = Acos(wt) * Bcos(wt + phi)
        I = ch1.ifft * ch2.ifft
        I_mean = np.mean(I)
        # I_mean = A * B / 2 * cos(phi)
        # get phase by angle of IFFT
        x = I_mean / (A * B / 2)
        # fix x to [-1, 1]
        x = max(-1, min(1, x))
        phi = - np.arccos(x)
        phi = np.degrees(phi)
        gain = B / A
        return (gain, phi)

    def analyze_delta(self):
        if config.CONF_USING_IFFT:
            self.gain, self.phase = self.analyze_delta_ifft(
                self.ch1Result, self.ch2Result)
            self.gain_integrate, self.phase_integrate = self.analyze_delta_ifft(
                self.ch1IntegrateResult, self.ch2Result)
            return

        self.gain: float = self.ch2Result.main_freq_amplitude / \
            self.ch1Result.main_freq_amplitude
        self.gain_integrate: float = self.ch2Result.main_freq_amplitude / \
            self.ch1IntegrateResult.main_freq_amplitude
        self.phase: float = self.ch2Result.phase - self.ch1Result.phase
        self.phase_integrate: float = self.ch2Result.phase - \
            self.ch1IntegrateResult.phase

    def analyze(self,
                start_s=config.CONF_START_TIME,
                time_s=config.CONF_DURATION,
                gain_ratio=config.CONF_GAIN_RATIO):
        freq_select = float(self.freq)
        self.gain_ratio = gain_ratio
        # print(f'gain_ratio: {gain_ratio}')
        # print(f'config.CONF_GAIN_RATIO: {config.CONF_GAIN_RATIO}')
        self.ch2Result.channel *= gain_ratio
        self.ch1Result.analyze_fft(freq_select, start_s, time_s)
        self.ch2Result.analyze_fft(freq_select, start_s, time_s)
        self.ch1IntegrateResult.analyze_fft(freq_select, start_s, time_s)
        self.ch1Result.analyze_indicators(freq_select)
        self.ch2Result.analyze_indicators(freq_select)
        self.ch1IntegrateResult.analyze_indicators(freq_select)
        self.analyze_delta()

    def to_dict(self):
        return {
            'param': self.record.param.params,
            'gain_ratio': self.gain_ratio,
            'freq': self.freq,
            'gain': self.gain,
            'gain_integrate': self.gain_integrate,
            'phase': self.phase,
            'phase_integrate': self.phase_integrate,
            'ch1': self.ch1Result.to_dict(),
            'ch2': self.ch2Result.to_dict(),
            'ch1_integrate': self.ch1IntegrateResult.to_dict(),
        }

    def load_from_dict(self, data: dict):
        self.freq = data['freq']
        self.gain = data['gain']
        self.gain_integrate = data['gain_integrate']
        self.gain_ratio = data['gain_ratio']
        self.ch1Result = ChannelAnalyzeResult()
        self.ch2Result = ChannelAnalyzeResult()
        self.ch1IntegrateResult = ChannelAnalyzeResult()
        self.ch1Result.load_from_dict(data['ch1'])
        self.ch2Result.load_from_dict(data['ch2'])
        self.ch1IntegrateResult.load_from_dict(data['ch1_integrate'])
        self.param = data['param']
        self.phase = data['phase']
        self.phase_integrate = data['phase_integrate']


class DataAnalyzeResultList:
    def __init__(self):
        self.dataAnalyzeResults: list[DataAnalyzeResult] = []
        self.sample_rate = config.CONF_SAMPLING_RATE

    def append(self, dataAnalyzeResult: DataAnalyzeResult):
        self.dataAnalyzeResults.append(dataAnalyzeResult)

    def to_dict(self):
        return {
            'dataAnalyzeResults': [result.to_dict() for result in self.dataAnalyzeResults]
        }

    def dump_to_json(self):
        print('dumping to json...')
        return json.dumps(self.to_dict(), indent=1)

    def dump_to_json_file(self, filename: str):
        data_json = self.dump_to_json()
        print(f'writing to {filename}...')
        with open(filename, "w", encoding='utf-8') as out_file:
            out_file.write(data_json)

    def load_from_dict(self, data: dict):
        self.dataAnalyzeResults = []
        for result in data['dataAnalyzeResults']:
            dataAnalyzeResult = DataAnalyzeResult()
            dataAnalyzeResult.load_from_dict(result)
            self.append(dataAnalyzeResult)

    def load_from_json(self, json_data: str):
        data = json.loads(json_data)
        self.load_from_dict(data)

    def load_from_json_file(self, filename: str):
        # print(f'loading from {filename}...')
        with open(filename, "r", encoding='utf-8') as in_file:
            json_data = in_file.read()
            self.load_from_json(json_data)

    def save_to_excel_file(self, filename: str):
        print(f'saving to {filename}...')
        freq_vector = np.array(
            [result.freq for result in self.dataAnalyzeResults])
        gain_vector = np.array(
            [result.gain_integrate for result in self.dataAnalyzeResults])
        phase_vector = np.array(
            [result.phase_integrate for result in self.dataAnalyzeResults])
        gain_vector_no_integrate = np.array(
            [result.gain for result in self.dataAnalyzeResults])
        phase_vector_no_integrate = np.array(
            [result.phase for result in self.dataAnalyzeResults])
        sheet1 = pd.DataFrame({
            'freq': freq_vector,
            'gain': gain_vector,
            'phase': phase_vector,
        })
        sheet2 = pd.DataFrame({
            'freq': freq_vector,
            'gain': gain_vector_no_integrate,
            'phase': phase_vector_no_integrate,
        })

        with pd.ExcelWriter(filename) as writer:
            sheet1.to_excel(writer, sheet_name='integrate', index=False)
            sheet2.to_excel(writer, sheet_name='no_integrate', index=False)

    def load_from_excel_file(self, filename: str):
        print(f'loading from {filename}...')
        df = pd.read_excel(filename)
        freq_vector = np.array(df['freq'])
        gain_vector = np.array(df['gain'])
        phase_vector = np.array(df['phase'])
        self.dataAnalyzeResults = []
        for i in range(len(freq_vector)):
            dataAnalyzeResult = DataAnalyzeResult()
            dataAnalyzeResult.freq = freq_vector[i]
            dataAnalyzeResult.gain_integrate = gain_vector[i]
            dataAnalyzeResult.phase_integrate = phase_vector[i]
            self.append(dataAnalyzeResult)

    def get_gain_integrate(self) -> list[float]:
        return [result.gain_integrate for result in self.dataAnalyzeResults]

    def get_gain(self) -> list[float]:
        return [result.gain for result in self.dataAnalyzeResults]

    def get_freq(self) -> list[float]:
        return [result.freq for result in self.dataAnalyzeResults]


def extract_values_to_dict(input_str):
    # 使用正则表达式匹配模式
    pattern = r'([A-Z])(\d+(\.\d+)?)'

    # 使用findall来找到所有匹配项
    matches = re.findall(pattern, input_str)

    # 构建字典
    result_dict = {}

    # 将匹配的结果放入字典
    for match in matches:
        key = match[0]  # 匹配的字母作为键
        value = float(match[1]) if match[2] else int(
            match[1])  # 转换匹配的数字部分为整数或浮点数
        result_dict[key] = value

    return result_dict


def analyze_file(input_file: str, output_file: str, phase_shift_manual=None, gain_ratio=None):
    config.load_keyword_profile(input_file)
    if gain_ratio is None:
        gain_ratio = config.CONF_GAIN_RATIO
    for keyword, ratio in config.CONF_GAIN_RATIO_KEYWORD:
        if keyword in input_file:
            gain_ratio *= ratio
            print(f'gain_ratio *= {ratio} = {gain_ratio}')

    ctrl_KW_dict = extract_values_to_dict(input_file)
    if 'A' in ctrl_KW_dict:
        gain_ratio *= ctrl_KW_dict['A']
        print(f'gain_ratio *= {ctrl_KW_dict["A"]} = {gain_ratio}')

    # get param from filename like: output_20231117_121343_S101_震级1@ps=-180
    if phase_shift_manual == None:
        if input_file and '@' in input_file:
            ctrl_str = input_file.split('@')[1].split('_')[0]
            if 'ps=' in ctrl_str:
                phase_shift_manual = float(ctrl_str.split('ps=')[1])
                print(
                    f'get phase_shift_manual from filename: {phase_shift_manual}')
        else:
            phase_shift_manual = 0

    dataRecordList = DataRecordList()
    dataRecordList.load_from_json_file(input_file)

    dataAnalyzeResultList = DataAnalyzeResultList()

    for dataRecord in dataRecordList.dataRecords:
        result = DataAnalyzeResult(
            dataRecord, sample_rate=config.CONF_SAMPLING_RATE)
        result.analyze(gain_ratio=gain_ratio)
        print(f'analyzing {dataRecord.param.params["freq"]} Hz...')
        dataAnalyzeResultList.append(result)

    phase = [result.phase for result in dataAnalyzeResultList.dataAnalyzeResults]
    phase_integrate = [
        result.phase_integrate for result in dataAnalyzeResultList.dataAnalyzeResults]

    # unwrap phase
    phase = shift_phase(phase, period=360,
                        phase_shift_manual=phase_shift_manual)
    phase_integrate = shift_phase(
        phase_integrate, period=360, phase_shift_manual=phase_shift_manual)

    # fix result
    for i in range(len(dataAnalyzeResultList.dataAnalyzeResults)):
        dataAnalyzeResultList.dataAnalyzeResults[i].phase = phase[i]
        dataAnalyzeResultList.dataAnalyzeResults[i].phase_integrate = phase_integrate[i]

    dataAnalyzeResultList.dump_to_json_file(output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--input_file', help='input file path')
    parser.add_argument('-o', '--output_file', help='output file path')
    parser.add_argument('-ps', '--phase_shift_manual',
                        help='phase shift manual')
    # to excel, expected one or zero argument
    # parser.add_argument('-e', '--excel', help='save to excel file')
    parser.add_argument('-e', '--excel', nargs='?',
                        const='<defualt>', help='save to excel file')
    args = parser.parse_args()

    output_file = args.output_file
    input_file = args.input_file
    phase_shift_manual = args.phase_shift_manual
    if phase_shift_manual:
        phase_shift_manual = float(phase_shift_manual)
    else:
        phase_shift_manual = None
    if not input_file:
        input_file = "c:\\Users\\lyon\\Desktop\\calibration\\calibration_analyzer\\output\\output_20231116_111510_2Hz_震级2_data.json"
    if not output_file:
        output_file = input_file.replace('_data.json', '_analyze.json')

    if args.excel:
        if args.excel == '<defualt>':
            args.excel = output_file.replace('_analyze.json', '.xlsx')
        dataAnalyzeResultList = DataAnalyzeResultList()
        dataAnalyzeResultList.load_from_json_file(input_file)
        dataAnalyzeResultList.save_to_excel_file(args.excel)
    else:
        analyze_file(input_file, output_file,
                     phase_shift_manual=phase_shift_manual)
