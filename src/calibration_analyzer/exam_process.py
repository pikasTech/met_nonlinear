from __future__ import annotations
import os
import re
import json
import numpy as np
import pandas as pd
import pdb
from scipy.optimize import minimize
from numpy import array
from scipy.optimize import curve_fit
from .exam_class import (
    System, ResultData, ParameterData, ConfigData,
    WsWf, Wf, Ws, H, H0, H0L, H0H, Kp0Kd0, Wa, Wfb, Wfb0, Wfb0_simply, H_close_simu, H_close_simu_with_G
)
from calibration_analyzer.analyzer import DataAnalyzeResultList

CONFIG_DEBUG = False


def debug_print(*args, **kwargs):
    if CONFIG_DEBUG:
        print(*args, **kwargs)


class ExamData:
    f: array
    gain: array
    phase: array
    kp: float
    kd: float

    def __init__(self, f=None, gain=None, phase=None, kp=0, kd=0, gain_ratio=1):
        self.f = f
        self.gain = gain
        self.phase = phase
        self.kp = kp
        self.kd = kd
        self.gain_ratio = gain_ratio

    def loadXlsm(self, xlsx_dir: str, sheetList):
        filename = xlsx_dir
        for sheet in sheetList:
            XLS_data_temp = pd.read_excel(filename,
                                          sheet_name=sheet - 1,
                                          header=None)
            # cut the columns from 0 to 5
        self.xlsmDataSheet = XLS_data_temp.iloc[:, 0:6]

    def standardize(self) -> array:
        data = self.xlsmDataSheet
        iRange = data.shape[0]
        jRange = data.shape[1]
        dataCut = np.zeros((iRange, jRange))
        for i in range(iRange):
            for j in range(jRange):
                dataCut[i][j] = data[j][i]
        return dataCut

    @staticmethod
    def getDataLengthAuto(data_temp):
        f = data_temp[0:99, 0]
        for i in range(99):
            if f[i] != 0:
                data_length_auto = i
        return data_length_auto

    def cut(self, dataRaw: array, dataLen, isAuto):
        if isAuto:
            dataLen = self.getDataLengthAuto(dataRaw)
        f = dataRaw[0:dataLen, 0]
        gain = dataRaw[0:dataLen, 1]
        phase = dataRaw[0:dataLen, 2]
        kp = dataRaw[0, 4]
        kd = dataRaw[0, 5]
        return ExamData(f=f, gain=gain, phase=phase, kp=kp, kd=kd)

    def skip(self, skipFreqList):
        def check_in_skip_freq_list(freq):
            for skip_freq in skipFreqList:
                if abs(freq - skip_freq) < 0.01:
                    return True
            return False

        skip_index = []
        for i in range(len(self.f)):
            if check_in_skip_freq_list(self.f[i]):
                skip_index.append(i)

        self.f = np.delete(self.f, skip_index)
        self.gain = np.delete(self.gain, skip_index)
        self.phase = np.delete(self.phase, skip_index)

    @classmethod
    def fromXlsx(
            cls,
            xlsx_dir,
            sheetList,
            isAutoDataLength,
            dataLengh):
        if hasattr(cls, 'data_cache'):
            return cls.data_cache
        data = ExamData()
        data.loadXlsm(xlsx_dir, sheetList)
        dataStandard = data.standardize()
        data = data.cut(
            dataStandard, dataLengh, isAutoDataLength)
        cls.data_cache = data
        return data

    @classmethod
    def fromJson(cls, json_dir: str):
        dataAnalyzeResultList = DataAnalyzeResultList()
        dataAnalyzeResultList.load_from_json_file(json_dir)
        gain_ratio = dataAnalyzeResultList.dataAnalyzeResults[0].gain_ratio
        ws_gain = np.array(
            [result.gain for result in dataAnalyzeResultList.dataAnalyzeResults])
        ws_freq = np.array(
            [result.freq for result in dataAnalyzeResultList.dataAnalyzeResults])
        ws_phase = np.array(
            [result.phase for result in dataAnalyzeResultList.dataAnalyzeResults])
        data = ExamData(f=ws_freq, gain=ws_gain,
                        phase=ws_phase, gain_ratio=gain_ratio)
        cls.data_cache = data
        return data

    def loadWsWf(self) -> System:
        gain = self.gain
        """ matlab
        Wa = (1/6.28) * 1 ./ Fre_;
        Wfb_phase__C = -90 * ones(1, length(Fre_));
        Gain_ = Gain_ ./ Wa;
        """
        Wa_gain = 1 / (2 * np.pi) * 1 / self.f
        Wa_phase = -90 * np.ones(len(self.f))
        gain = gain / Wa_gain
        WsWf = System()
        WsWf.f = self.f
        WsWf.gain = gain
        WsWf.phase = self.phase - Wa_phase
        return WsWf


class ExamProcessData:
    def __init__(self,
                 h,
                 h0,
                 h0h,
                 h0l,
                 Kd0,
                 Kp0,
                 wa,
                 wf,
                 wfb,
                 wfb0,
                 wfb0_simply,
                 wfb0_kpkd,
                 wfb0_pars,
                 ws_simu,
                 wswf,
                 fit_curve_exam,
                 h_close_simu_simply,
                 h_close_simu,
                 h_close_simu_kpkd,
                 h_close_simu_with_G,
                 sensitive_fix,
                 h_close_simu_with_G_high_cut_fit,
                 h_close_simu_high_cut_correct,
                 h_close_simu_with_G_high_cut_corrected,
                 ws_exam,
                 ws_fit,
                 ws_fit2,
                 Kp0_no_gainratio,
                 Kd0_no_gainratio,
                 G_close,
                 h_close_real_with_G,
                 h_close_real_with_G_high_cut_corrected
                 ):
        self.h: System = h
        self.h0: System = h0
        self.h0h: System = h0h
        self.h0l: System = h0l
        self.Kd0: float = Kd0
        self.Kp0: float = Kp0
        self.wa: System = wa
        self.wf: System = wf
        self.wfb: System = wfb
        self.wfb0: System = wfb0
        self.wfb0_simply: System = wfb0_simply
        self.wfb0_kpkd: System = wfb0_kpkd
        self.wfb0_pars: System = wfb0_pars
        self.ws_simu: System = ws_simu
        self.wswf: System = wswf
        self.fit_curve_exam: System = fit_curve_exam
        self.h_close_simu_simply: System = h_close_simu_simply
        self.h_close_simu: System = h_close_simu
        self.h_close_simu_kpkd: System = h_close_simu_kpkd
        self.h_close_simu_with_G: System = h_close_simu_with_G
        self.sensitive_fix: float = sensitive_fix
        self.h_close_simu_with_G_high_cut_fit: System = h_close_simu_with_G_high_cut_fit
        self.h_close_simu_high_cut_correct: System = h_close_simu_high_cut_correct
        self.h_close_simu_with_G_high_cut_corrected: System = h_close_simu_with_G_high_cut_corrected
        self.ws_exam: System = ws_exam
        self.ws_fit: System = ws_fit
        self.ws_fit2: System = ws_fit2
        self.Kp0_no_gainratio: float = Kp0_no_gainratio
        self.Kd0_no_gainratio: float = Kd0_no_gainratio
        self.G_close: float = G_close
        self.h_close_real_with_G: System = h_close_real_with_G
        self.h_close_real_with_G_high_cut_corrected: System = h_close_real_with_G_high_cut_corrected


def lowpass_system_number(params, freq):
    """ 二阶系统的传递函数"""
    A, omega_n, zeta, group_delay = params
    s = 1j * 2 * np.pi * freq
    H = A * omega_n**2 / (s**2 + 2*zeta*omega_n*s + omega_n**2)
    return H


def highpass_system_number(params, freq):
    # 二阶高通滤波器
    A, omega_n, zeta = params
    s = 1j * 2 * np.pi * freq
    H = A * s**2 / (s**2 + 2*zeta*omega_n*s + omega_n**2)
    return H


def lowpass_system_calculate_gain(params, freq):
    A, omega_n, zeta, group_delay = params
    # 确保参数都是正数
    if A <= 0 or omega_n <= 0 or zeta <= 0:
        return 1e6
    return np.abs(lowpass_system_number(params, freq))


def lowpass_system_number(params, freq):
    """ 相位计算函数"""
    phase = np.angle(lowpass_system_number(params, freq))
    A, omega_n, zeta, group_delay = params
    return np.degrees(phase) + group_delay  # 转换为度


def system_fit_with_gain_phase(
        calculate_gain: callable,
        calculate_phase: callable,
        calculate_number: callable,
        origin_system: System,
        k=0.9,
        freq_range=(5, 200),
        initial_guess=[200, 500, 0.1, 0],
        calculate_number_for_result: callable = None,
        project_params: callable = None,
) -> System:
    """ 
    对高频截止频率附近的传递函数进行拟合 

    origin_system: 原始的传递函数
    k: 增益部分的权重
    freq_range: 拟合的频率范围
    initial_guess: 初始参数猜测
    """
    gain = origin_system.toabs()
    freq = origin_system.f
    phase = origin_system.tophase()

    freq = np.array(freq)  # 频率
    gain = np.array(gain)  # 增益
    phase = np.array(phase)  # 相位(°)

    # 设置拟合的频率范围
    freq_min = freq_range[0]  # 最小频率
    freq_max = freq_range[1]  # 最大频率

    # 过滤出指定频率范围内的数据
    mask = (freq >= freq_min) & (freq <= freq_max)
    freq_filtered = freq[mask]
    gain_filtered = gain[mask]

    # 初始参数猜测
    # initial_guess = [200, 22055320663, 24057037]
    # initial_guess = [200, 1880, -2.56]

    # 计算相邻频率点之间的差距
    freq_diffs = np.diff(np.sort(freq_filtered))
    # 补充第一个点
    freq_diffs = np.insert(freq_diffs, 0, freq_diffs[0])
    # 计算权重，假设权重与频率点之间的距离成反比
    weights = 1 / freq_diffs

    def normalize_params(params):
        normalized = np.array(params, dtype=float)
        if project_params is not None:
            normalized = np.array(project_params(normalized), dtype=float)
        return normalized

    initial_guess = normalize_params(initial_guess)

    # 损失函数，用于优化
    def loss(params, k=k, weidgets=weights, use_weights=True):
        params = normalize_params(params)
        predicted_gain = calculate_gain(
            params, freq_filtered)
        predicted_phase = calculate_phase(
            params, freq_filtered)
        # 使用对数距离来计算增益部分的误差
        # gain_error = np.mean(
        #     (np.log10(gain_filtered) - np.log10(predicted_gain))**2)

        if not use_weights:
            weidgets = 1

        gain_error = np.sum(
            weidgets * (gain_filtered - predicted_gain)**2)

        # 计算相位差，同时确保差值在 -180 到 180 度之间
        # phase_difference = phase[mask] - predicted_phase
        # phase_difference = (phase_difference + 180) % 360 - 180

        # 计算加权相位误差
        if len(phase) > 0:
            phase_error = np.sum(
                weidgets * (phase[mask] - predicted_phase)**2)
        else:
            phase_error = 0

        return k * gain_error + (1-k) * phase_error

    # 进行优化
    result = minimize(loss, initial_guess, method='Nelder-Mead')

    # 最优参数
    params = normalize_params(result.x)
    # A_opt, omega_n_opt, zeta_opt, group_delay_opt = params
    # debug_print('A_opt: ', A_opt)
    # debug_print('omega_n_opt: ', omega_n_opt)
    # debug_print('zeta_opt: ', zeta_opt)
    # debug_print('group_delay: ', group_delay_opt)

    # 使用最优参数生成拟合曲线
    # freq_fit = np.logspace(np.log10(0.1), np.log10(300), 1000)
    freq_fit = freq
    fitted_gain = calculate_gain(params, freq_fit)
    fitted_phase = calculate_phase(params, freq_fit)

    fited_system = System()
    if None == calculate_number_for_result:
        calculate_number_for_result = calculate_number
    fited_system.number = calculate_number_for_result(params, freq_fit)
    fited_system.f = freq_fit
    fited_system.fit_params = params
    return fited_system


def system_fit(
        calculate_number: callable,
        origin_system: System,
        k=0.9,
        freq_range=(5, 200),
        initial_guess=[200, 500, 0.1, 0],
        calculate_number_for_result: callable = None
) -> System:
    """
    根据传递函数进行拟合
    输入：
    calculate_number: 计算传递函数的函数
    origin_system: 被拟合的系统，一般是一个频率响应离散数据
    k: 幅度和相位的权重，1：全幅度，0：全相位
    freq_range: 拟合的频率范围
    initial_guess: 初始参数猜测
    """
    def calculate_gain(params, freq):
        number = calculate_number(params, freq)
        return np.abs(number)

    def calculate_phase(params, freq):
        number = calculate_number(params, freq)
        phase = np.angle(number)
        return np.degrees(phase)

    return system_fit_with_gain_phase(
        calculate_gain,
        calculate_phase,
        calculate_number,
        origin_system,
        k=k,
        freq_range=freq_range,
        initial_guess=initial_guess,
        calculate_number_for_result=calculate_number_for_result
    )


def highpass_fit(
        origin_system: System,
        k=1,
        freq_range=(5, 200),
        initial_guess=[200, 30, 0.1]) -> System:
    """
    对高频截止频率附近的传递函数进行拟合
    """
    sys = system_fit(
        highpass_system_number,
        origin_system,
        k=k,
        freq_range=freq_range,
        initial_guess=initial_guess)
    params = sys.fit_params
    s = System.s
    A, omega_n, zeta = params
    symbol = A * s**2 / (s**2 + 2*zeta*omega_n*s + omega_n**2)
    sys.symbol = symbol
    return sys


def lowpass_fit(
        origin_system: System,
        k=1,
        freq_range=(5, 200),
        initial_guess=[200, 500, 0.1, 0]) -> System:
    """ 
    对高频截止频率附近的传递函数进行拟合 

    origin_system: 原始的传递函数
    k: 增益部分的权重
    freq_range: 拟合的频率范围
    initial_guess: 初始参数猜测
    """
    return system_fit_with_gain_phase(
        lowpass_system_calculate_gain,
        lowpass_system_number,
        lowpass_system_number,
        origin_system,
        k=k,
        freq_range=freq_range,
        initial_guess=initial_guess)


def ws_calculate_number(params, freq):
    w = 2 * np.pi * freq
    A, B, C = params
    s = 1j * w
    number = A * s * (1 / (s**2 + C * s + B))
    return number


def ws_calculate_number_for_result(params, freq):
    w = 2 * np.pi * freq
    A, B, C = params
    s = 1j * w
    number = - A * s * (1 / (s**2 + C * s + B))
    return number


def ws_calculate_gain(params, freq):
    A, B, C = params
    if A <= 0 or B <= 0 or C <= 0:
        return 1e6
    number = ws_calculate_number(params, freq)
    return np.abs(number)


def ws_calculate_phase(params, freq):
    number = ws_calculate_number(params, freq)
    phase = np.angle(number)
    return np.degrees(phase)


def ws_system_fit(
        origin_system: System,
        k=0.9,
        freq_range=(5, 200),
        initial_guess=None,
        direct_guess=False,
        center_frequency_bounds_hz=None,
) -> System:
    """
    对 ws 进行拟合
    """
    if None is initial_guess:
        # calculate the S_n, f_n and zeta
        # calculate the max gain for f_n
        f = np.logspace(np.math.log10(
            freq_range[0]), np.math.log10(freq_range[1]), 100)
        gain = origin_system.calculate_gain(f)
        f_n = f[np.argmax(gain)]
        S_n = np.max(gain)
        zeta = 1.2
        w_n = 2 * np.pi * f_n
        B = w_n**2
        # S_n = np.array(A) / (4 * np.pi * np.array(zeta) * f_n)
        A = S_n * 4 * np.pi * zeta * f_n
        # zeta = C / (2 * wn)
        C = 2 * zeta * w_n
        initial_guess = [A, B, C]
        if direct_guess:
            if center_frequency_bounds_hz is not None:
                min_hz, max_hz = center_frequency_bounds_hz
                if min_hz is not None:
                    B = max(B, (2 * np.pi * float(min_hz)) ** 2)
                if max_hz is not None:
                    B = min(B, (2 * np.pi * float(max_hz)) ** 2)
                initial_guess = [A, B, C]
            s = System.s
            ws = System.fromSymbol(A * s * (1 / (s**2 + C * s + B)))
            ws.fit_params = initial_guess
            return ws

    def project_ws_params(params):
        projected = np.array(params, dtype=float)
        if center_frequency_bounds_hz is not None and len(projected) >= 2:
            min_hz, max_hz = center_frequency_bounds_hz
            min_b = (2 * np.pi * float(min_hz)) ** 2 if min_hz is not None else None
            max_b = (2 * np.pi * float(max_hz)) ** 2 if max_hz is not None else None
            if min_b is not None:
                projected[1] = max(min_b, projected[1])
            if max_b is not None:
                projected[1] = min(max_b, projected[1])
        return projected

    ws = system_fit_with_gain_phase(
        ws_calculate_gain,
        ws_calculate_phase,
        ws_calculate_number,
        origin_system,
        k=k,
        freq_range=freq_range,
        initial_guess=initial_guess,
        calculate_number_for_result=ws_calculate_number_for_result,
        project_params=project_ws_params,
    )
    params = ws.fit_params
    s = System.s
    A, B, C = params
    symbol = A * s * (1 / (s**2 + C * s + B))
    ws.symbol = symbol
    return ws


def make_lowpass_butterworth_filter(order, fc, f) -> System:
    """ 二阶巴特沃斯低通滤波器 """
    filter = System()
    w = 2 * np.pi * f
    s = 1j * w
    omega_c = 2 * np.pi * fc
    H = omega_c**2 / (s**2 + s * omega_c * np.sqrt(2) + omega_c**2)
    filter.number = H
    for i in range(order//2-1):
        filter.number = filter.number * H
    filter.f = f
    return filter


def make_correct_system_number(T, beta, freq):
    """ 修正高频截止频率的校正系统 """
    w = 2 * np.pi * freq
    s = 1j * w
    H = (T*s+1)/(beta*T * s + 1)
    return H


def make_correct_system_T_beta(T, beta, freq):
    """ 修正高频截止频率的校正系统 """
    system = System()
    system.number = make_correct_system_number(T, beta, freq)
    system.f = freq
    system.set_param('T', T)
    system.set_param('beta', beta)
    return system


def make_correct_system_1st_order(fc, dG, freq,
                                  using_lowpass_butterworth_filter=False,
                                  using_cascade_system=False,
                                  ):
    """ 修正高频截止频率的校正系统 """
    # Ensure each subsystem's gain doesn't exceed sqrt(2)
    # Calculate the number of subsystems needed based on logarithmic scale
    dG_sub_num = int(np.ceil(np.log(dG) / np.log(np.sqrt(2))))
    if dG_sub_num < 1:
        dG_sub_num = 1
    if not using_cascade_system:
        if dG_sub_num > 1:
            dG_sub_num = 1

    debug_print('dG', dG)
    debug_print('system_order', dG_sub_num)

    # Calculate the gain for each subsystem
    dG_sub = dG ** (1 / dG_sub_num)

    # If more than one subsystem is needed, inform the user of the adjusted gain
    if dG_sub_num > 1:
        debug_print(
            f'Fixed dG_sub with system_order {dG_sub_num}: dG_sub = {dG_sub}')
    else:
        debug_print(f'Single system used: dG_sub = {dG_sub}')
    correct_system = System()
    w = 2 * np.pi * freq
    s = 1j * w
    omega_c = 2 * np.pi * fc
    T = 1 / omega_c
    # 确保 2 - dG_sub**2 不为负数
    x = 2-dG_sub**2
    if x < 0:
        x = 0
    beta = np.sqrt(x) / dG_sub
    debug_print('beta', beta)
    debug_print('T', T)
    correct_system = make_correct_system_T_beta(T, beta, freq)
    if using_cascade_system:
        if dG_sub_num > 1:
            correct_system.set_param('correct_system_sub',  correct_system)
        for i in range(dG_sub_num-1):
            correct_system = cascade_system(correct_system, correct_system)

    if using_lowpass_butterworth_filter:
        if dG_sub_num > 1:
            # add butterworth filter
            f_low_pass = fc * 4
            butterworth_filter = make_lowpass_butterworth_filter(
                4, f_low_pass, freq)
            # 补充一个增益为 sqrt(2) 的补偿环节
            correct_post = make_correct_system_T_beta(
                fc, np.sqrt(2), freq)
            debug_print(butterworth_filter.calculate_gain(
                fc))
            debug_print(correct_post.calculate_gain(fc))
            correct_system = cascade_system(correct_system, butterworth_filter)
            # fix_system = cascade_system(fix_system, correct_post)
    if dG_sub_num > 1:
        correct_system.set_param('dG_sub', dG_sub)
        correct_system.set_param('dG_sub_num', dG_sub_num)
    return correct_system


def make_correct_system_2rd_order(fc, dG, freq):
    """ 二阶的修正高频截止频率的校正系统 """
    correct_system = System()
    omiga_n = 2 * np.pi * fc
    Mr = dG
    zeta = 1 / (2 * Mr)
    omiga = freq * 2 * np.pi
    s = 1j * omiga
    H = omiga_n**2 / (s**2 + 2 * zeta * omiga_n * s + omiga_n**2)
    correct_system.number = H
    correct_system.f = freq
    return correct_system


def get_high_cut_correct_system(
        origin_system: System,
        using_lowpass_butterworth_filter_1st=False,
        using_cascade_system_1st=True,
        using_1st=True,
        using_2st=False,
        using_keep_system=True,
        keep_system_num=1,
        high_cut_expected=100) -> System:
    # 调整到给定的高频截止频率
    # 计算高频截止频率处的增益补偿系数

    high_cut_gain_now = origin_system.calculate_gain(
        high_cut_expected)

    # -3dB 点
    high_cut_gain_expected = origin_system.sensitivity * 1 / np.sqrt(2)

    high_cut_gain_ratio = high_cut_gain_expected / high_cut_gain_now
    debug_print('high_cut_gain_ratio', high_cut_gain_ratio)

    # Your original gain, which needs to be cascaded into multiple subsystems
    dG = high_cut_gain_ratio
    debug_print('dG',  dG)

    freq = np.array(origin_system.f)
    # correct_system_number = make_correct_system_number(T, beta, freq)
    if using_1st and using_2st:
        if dG <= 1.414:
            correct_system = make_correct_system_1st_order(
                high_cut_expected, dG, freq, using_lowpass_butterworth_filter_1st, using_cascade_system_1st)
        else:
            correct_system = make_correct_system_2rd_order(
                high_cut_expected, dG, freq)
    elif using_2st:
        correct_system = make_correct_system_2rd_order(
            high_cut_expected, dG, freq)
    elif using_1st:
        correct_system = make_correct_system_1st_order(
            high_cut_expected, dG, freq, using_lowpass_butterworth_filter_1st, using_cascade_system_1st)

    if using_keep_system:

        if keep_system_num > 0:
            # keep the high_cut off frequency, and correct the gain below the high_cut off frequency
            keep_system = make_correct_system_2rd_order(
                high_cut_expected, 1, freq)

            for i in range(keep_system_num - 1):
                keep_system = cascade_system(keep_system, keep_system)

            correct_system.set_param('keep_system_num', keep_system_num)
            correct_system.set_param('keep_system', keep_system)
            correct_system.set_param('correct_system_origin', correct_system)
            correct_system = cascade_system(correct_system, keep_system)

    correct_system.set_param('dG', dG)
    correct_system.set_param('high_cut_gain_ratio', high_cut_gain_ratio)
    return correct_system


def cascade_system2(system1: System, system2: System) -> System:
    """ 级联两个系统 """
    system = System()
    if system1.symbol is not None and system2.symbol is not None:
        system.symbol = system1.symbol * system2.symbol

    if len(system1.number) > 0 and len(system2.number) > 0:
        system.number = system1.number * system2.number
    else:
        system.gain = system1.toabs() * system2.toabs()
        system.phase = system1.tophase() + system2.tophase()
    system.f = system1.f
    system.merge_params(system1)
    system.merge_params(system2)
    return system


def divide_system(system1: System, system2: System) -> System:
    """ 除以另一个系统 """
    system = System()
    if len(system1.number) > 0 and len(system2.number) > 0:
        system.number = system1.number / system2.number  # 假设支持除法操作
    else:
        system.gain = system1.toabs() / system2.toabs()
        system.phase = system1.tophase() - system2.tophase()
    system.f = system1.f
    system.merge_params(system1)
    system.merge_params(system2)
    return system


def cascade_system(*systems):
    """级联任意数量的系统"""
    if not systems:
        return None  # 如果没有系统输入，返回None

    cascaded_system = systems[0]  # 从第一个系统开始

    # 从第二个系统开始，逐一级联
    for system in systems[1:]:
        cascaded_system = cascade_system2(cascaded_system, system)

    return cascaded_system


def amplify_system(system1: System, gain: float) -> System:
    """ 放大系统 """
    system = system1.clone()
    system.gain = system1.gain * gain
    system.number = system1.number * gain
    system.f = system1.f
    return system


class Exam:

    def __init__(self, data_path: str = None):
        if data_path is None:
            self.config = ConfigData()
        else:
            self.config = ConfigData(data_path=data_path)
        self.res: ResultData
        self.par: ParameterData

    def save(self, dir='tmp/testout.json'):
        # mkdir if not exist
        if not os.path.exists(os.path.dirname(dir)):
            os.makedirs(os.path.dirname(dir))

        with open(dir, 'w') as f:
            todict = self.todict()
            json.dump(todict, f, indent=4)

    def getResAndPar(self, res, par):
        self.res = res
        self.par = par

    def loadData(self):
        if self.config.WfType == 1:
            C1 = 2.2e-6
            C2 = 0.01e-6
            R1 = 100e3
            R2 = 3e6
            R3 = 200e3
        elif self.config.WfType == 2:
            C1 = 2.2e-6
            C2 = 0.0168e-6
            R1 = 100e3
            R2 = 1.8e6
            R3 = 120e3

        if self.config.xlsxDir is not None:
            data = ExamData.fromXlsx(
                self.config.xlsxDir,
                self.config.sheetList,
                self.config.isAutoDataLength,
                self.config.dataLength
            )
            debug_print('data loaded from xlsx')

        if self.config.jsonDir is not None:
            data = ExamData.fromJson(
                self.config.jsonDir,
            )
            debug_print('data loaded from json')
        data.skip(self.config.skipFreqs)
        wswf = WsWf.fromData(data)
        wf = Wf.fromPars(wswf.f, C1, C2, R1, R2, R3)
        ws_exam = Ws.fromWsWfAndWf(wswf, wf)
        return C1, C2, R1, R2, R3, data, wswf, wf, ws_exam

    def process(self) -> ExamProcessData:
        # load data from xlsx
        C1, C2, R1, R2, R3, data, wswf, wf, ws_exam = self.loadData()
        f, w = ws_exam.f, ws_exam.w

        ws_exam_nogain_ratio = amplify_system(ws_exam, 1/data.gain_ratio)

        # fit curve for ws
        fit_curve_exam = Ws.fit(ws_exam, self.config.fitRange)

        fit_curve_exam_no_gainratio = Ws.fit(
            ws_exam_nogain_ratio, self.config.fitRange)

        # get ws_fit from fit_curve
        ws_fit = Ws.fromFitCurve(ws_exam, fit_curve_exam)
        ws_fit2 = ws_system_fit(
            ws_exam, freq_range=self.config.ws_fit_freq_range, initial_guess=self.config.ws_fit_initial_guess)

        # modify the fit curve to generate simulated data
        fit_curve_simu = fit_curve_exam.clone()
        fit_curve_simu.A = fit_curve_exam.A * self.config.A_k
        fit_curve_simu.B = fit_curve_exam.B * self.config.B_k
        fit_curve_simu.C = fit_curve_exam.C * self.config.C_k

        # get ws_simu from fit_curve and simu args
        ws_simu = Ws.fromFitCurve(ws_fit, fit_curve_simu)

        ws_fit_used = ws_fit2

        # load data from xlsx
        ka, kp, kd = self.config.Ka, -data.kp, -data.kd

        wa = Wa.fromKa(f, ka)
        wfb = Wfb.fromKpKd(w, kp, kd)

        h = H.fromWsWf(ws_fit_used, wf)
        h0l = H0L.fromFitAndPars(fit_curve_simu, f, C1, R2)
        h0h = H0H.fromFitAndPars(
            fit_curve_simu, f, C1, R2, self.config.fl)
        h0 = H0.fromFitAndPars(fit_curve_simu, f, C1, R2, self.config.fl)

        wfb0 = Wfb0.fromH0WsWfWa(h0, ws_fit_used, wf, wa)
        # pdb.set_trace()
        wfb0_pars = Wfb0.fromFitAndPars(
            fit_curve_simu, f, C1, C2, R1, R2, R3, self.config.fl, ka)

        Kp0, Kd0 = Kp0Kd0.fromFitAndPars(fit_curve_simu,
                                         C1,
                                         C2,
                                         R1,
                                         R2,
                                         R3,
                                         self.config.fl,
                                         ka)

        Kp0_no_gainratio, Kd0_no_gainratio = Kp0Kd0.fromFitAndPars(
            fit_curve_exam_no_gainratio,
            C1,
            C2,
            R1,
            R2,
            R3,
            self.config.fl,
            ka)

        wfb0_simply = Wfb0_simply.fromFitAndPars(fit_curve_simu,
                                                 f,
                                                 C1,
                                                 C2,
                                                 R1,
                                                 R2,
                                                 R3,
                                                 self.config.fl,
                                                 ka)

        wfb0_kpkd = Wfb0_simply.fromKpKd(f, Kp0, Kd0)

        par = ParameterData(C1=C1,
                            C2=C2,
                            data_length=self.config.dataLength,
                            fl=self.config.fl,
                            Ka=ka,
                            Kd=kd,
                            Kp=kp,
                            R1=R1,
                            R2=R2,
                            R3=R3)

        h_close_simu_simply = H_close_simu.fromHWfbWa(h, wfb0_simply, wa)
        # h_close_simu = H_close_simu.fromHWfbWa(h, wfb0, wa)
        h_close_simu = H_close_simu.fromWsWfWfbWa(ws_fit_used, wf, wfb0, wa)
        h_close_simu_kpkd = H_close_simu.fromHKpKdWa(
            h, Kp0, Kd0, wa)

        G = self.config.sensitive_expect / \
            h_close_simu.calculate_sensitivity()

        h_close_simu_with_G = H_close_simu_with_G.fromHcloseG(
            h_close_simu_kpkd, G)

        h_close_simu_with_G_high_cut_fit = lowpass_fit(
            h_close_simu_with_G, freq_range=(5, 200))

        h_close_simu_high_cut_correct = get_high_cut_correct_system(
            h_close_simu_with_G_high_cut_fit, high_cut_expected=self.config.high_cut_expected, keep_system_num=self.config.high_cut_keep_system_num)

        h_close_simu_with_G_high_cut_corrected = cascade_system(
            h_close_simu_with_G, h_close_simu_high_cut_correct)

        # 只有在处理闭环数据时这个结果才是有意义的
        h_close_real: System = wswf.clone()

        h_close_real_high_cut_fit = lowpass_fit(
            h_close_real, freq_range=(5, 200))

        G_close_real = self.config.sensitive_expect / \
            h_close_real.calculate_sensitivity(reference_frequency=4)

        h_close_real_with_G = H_close_simu_with_G.fromHcloseG(
            h_close_real, G_close_real)

        h_close_real_with_G_high_cut_fit = lowpass_fit(
            h_close_real_with_G, freq_range=(5, 200))

        h_close_real_with_G_high_cut_correct = get_high_cut_correct_system(
            h_close_real_with_G_high_cut_fit, high_cut_expected=self.config.high_cut_expected, keep_system_num=self.config.high_cut_keep_system_num)

        h_close_real_with_G_high_cut_corrected = cascade_system(
            h_close_real_with_G, h_close_real_with_G_high_cut_correct)

        res = ResultData(H=h,
                         H0=h0,
                         H0h=h0h,
                         H0l=h0l,
                         Kd0=Kd0,
                         Kp0=Kp0,
                         Wa=wa,
                         Wf=wf,
                         Wfb=wfb,
                         Wfb0=wfb0,
                         Wfb0_simply=wfb0_simply,
                         Wfb0_kpkd=wfb0_kpkd,
                         Wfb0_pars=wfb0_pars,
                         Ws=ws_simu,
                         WsWf=wswf,
                         fit=fit_curve_exam,
                         H_close_simu_simply=h_close_simu_simply,
                         H_close_simu=h_close_simu,
                         H_close_simu_kpkd=h_close_simu_kpkd,
                         H_close_simu_with_G=h_close_simu_with_G,
                         G=G
                         )

        self.config.add(
            range=list(self.config.fitRange))

        self.res = res
        self.par = par
        return ExamProcessData(
            h=h,
            h0=h0,
            h0h=h0h,
            h0l=h0l,
            Kd0=Kd0,
            Kp0=Kp0,
            wa=wa,
            wf=wf,
            wfb=wfb,
            wfb0=wfb0,
            wfb0_simply=wfb0_simply,
            wfb0_kpkd=wfb0_kpkd,
            wfb0_pars=wfb0_pars,
            ws_simu=ws_simu,
            wswf=wswf,
            fit_curve_exam=fit_curve_exam,
            h_close_simu_simply=h_close_simu_simply,
            h_close_simu=h_close_simu,
            h_close_simu_kpkd=h_close_simu_kpkd,
            h_close_simu_with_G=h_close_simu_with_G,
            h_close_simu_with_G_high_cut_fit=h_close_simu_with_G_high_cut_fit,
            sensitive_fix=G,
            h_close_simu_high_cut_correct=h_close_simu_high_cut_correct,
            h_close_simu_with_G_high_cut_corrected=h_close_simu_with_G_high_cut_corrected,
            ws_exam=ws_exam,
            ws_fit=ws_fit,
            ws_fit2=ws_fit2,
            Kp0_no_gainratio=Kp0_no_gainratio,
            Kd0_no_gainratio=Kd0_no_gainratio,
            G_close=G_close_real,
            h_close_real_with_G=h_close_real_with_G,
            h_close_real_with_G_high_cut_corrected=h_close_real_with_G_high_cut_corrected,
        )

    def todict(self):
        return {
            'res': self.res.todict(),
            'par': self.par.todict(),
            'config': self.config.todict()
        }

    @staticmethod
    def get_Wf_from_file(filename):
        f, gain, x1, x2, x3, x4 = np.loadtxt(filename, unpack=True)
        gain = [
            0.19571,
            0.368355,
            0.677523,
            1.045975,
            1.258448,
            1.192925,
            0.862016,
            0.510647,
            0.350564,
            0.249987,
            0.200695,
            0.171912,
            0.153727,
            0.141534,
            0.133032,
            0.126755,
            0.121797,
            0.118407,
            0.115515,
            0.113306,
            0.111361,
            0.110139,
        ] * 21
        gain = np.array(gain)
        return System(f, gain)

    def read_Analize(self, data, i_kp, i_kd):
        Fre, Gain, phase = self.read_data(data, i_kp, i_kd)
        # my_analize(Fre,Gain,phase,0,1,"WsWf",1,0);
        Fre_C, Gain_C, phase_C = self.get_H(Fre, Gain, phase)
        i_3db_1, i_3db_2, low_pass, high_pass, Stive = self.find_3db(
            Gain_C, Fre_C)
        return low_pass, Stive

    @staticmethod
    def find_3db(Gain, Fre):
        Gain_max = 0
        i_max = 1
        for i in range(len(Fre)):
            if Fre[i] < 10:
                if Gain[i] > Gain_max:
                    Gain_max = Gain[i]
                    i_max = i
        Gain_max
        Fre[i_max]
        Gain_3db = Gain_max * 0.707
        i_3db_1 = 1
        for i in range(i_max):
            if Gain[i] < Gain_3db:
                i_3db_1 = i
        i_3db_2 = len(Fre)
        for i in range(len(Fre) - i_max):
            if Gain[len(Fre) - i + 1] < Gain_3db:
                i_3db_2 = len(Fre) - i + 1
        low_pass = Fre[i_3db_1]
        high_pass = Fre[i_3db_2]
        sensitive = Gain_max
        return i_3db_1, i_3db_2, low_pass, high_pass, sensitive

    @staticmethod
    def get_number_and_abs_of_Wfb0(H0, Ws, Wf, Wa):
        number = (1 / H0.number - 1 / (Ws.number * Wf.number)) / Wa.number
        abs_ = abs(number)
        return number, abs_


def process_json_data(path='calibration_analyzer/ws_analyze.json', fitRange=None):
    exam = Exam(path)
    exam.config.get_data_from_xlsx = 1
    exam.config.WfType = 1
    if fitRange is not None:
        exam.config.fitRange = fitRange
    exam.config.Ka = 1
    exam.config.fl = 1
    return exam.process()


class DataInfo:
    def __init__(self, file_path: str, magnitude: float):
        self.file_path = file_path
        self.data_file_path = file_path.replace("_analyze.json", "_data.json")
        self.magnitude = magnitude

    def __repr__(self):
        return f"DataInfo(file_path='{self.file_path}', magnitude={self.magnitude})"


def find_data_info(directory) -> list[DataInfo]:
    data_info_list = []
    pattern = re.compile(r".*震级(\d+\.\d+)_analyze\.json$")

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith("analyze.json"):
                match = pattern.match(file)
                if match:
                    magnitude = float(match.group(1)) * 1.2  # (m/s**2)/震级系数
                    full_path = os.path.join(root, file)
                    data_info_list.append(DataInfo(full_path, magnitude))

    # 按照 magnitude 排序
    data_info_list.sort(key=lambda x: x.magnitude)
    return data_info_list
