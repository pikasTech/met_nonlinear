import matplotlib.pyplot as plt
from typing import List
from calibration_analyzer.exam_class import System
from calibration_analyzer import exam_process, exam_class
import numpy as np
import math


def duffing_response():
    # 生成频率范围
    f = np.logspace(math.log10(9), math.log10(11), 300)  # 0.1 Hz 到 1000 Hz
    fs = 1000
    time_length = 100

    # s = System.s
    # ws = System.fromSymbol(
    #     (53882.0 * s) / (s**2 + 624.82*s + 56815.23),
    #     f=f)

    # wf = System.fromSymbol(
    #     (0.0132 * s ** 2 + 6.6*s) / (0.00704 * s ** 2 + 0.252 * s + 1.0),
    #     f=f)

    # wswf = exam_process.cascade_system(ws, wf)
    # wswf.plot(time_domin=True)

    # sin_data = exam_class.TimeSeries.fromSin(
    #     f=1, A=1,  fs=1000, time_length=100)
    # sin_data.plot()

    # x = exam_class.MappingSystem.x
    # f1 = exam_class.MappingSystem.fromFunction(lambda x: x * np.exp(np.abs(x)))
    # f2 = exam_class.MappingSystem.fromFunction(lambda x: x ** 3)

    # f1_response = f1.time_response(sin_data)
    # h_response = wswf.time_response(sin_data)
    # hf1_response = wswf.time_response(f1_response)
    # hf1f2_response = f2.time_response(hf1_response)

    # h_response.plot()
    # hf1f2_response.plot()
    duffing = exam_class.DuffingOscillator(
        amplitude=100, f_0=10, alpha=1000, delta=0.01)
    # duffing_response = duffing.time_response(sin_data)
    # sin_data.plot()
    # duffing_response.plot()
    duffing_amp1 = System.frequency_response_from_time_domain(
        duffing, amplitude=0.1, f=f, fs=fs, time_length=time_length)
    duffing_amp1.plot()
    duffing_amp2 = System.frequency_response_from_time_domain(
        duffing, amplitude=100, f=f, fs=fs, time_length=time_length)
    duffing_amp2.plot()
    plt.show()


def fun_f1(x):
    return x * np.exp(np.abs(x))

# 分段非线性算子


def fun_f3(x: np.array):
    y = np.where(np.abs(x) < 1, x, 2 * x)
    return y


def HW_response():
    f = np.logspace(math.log10(0.5), math.log10(150), 50)  # 0.1 Hz 到 1000 Hz
    fs = 2000
    time_length = 20

    s = System.s
    f0 = 10
    delta = 0.01  # 阻尼比
    omega_n = 2 * np.pi * f0

    h = System.fromSymbol(
        s / (s ** 2 + 2 * delta * omega_n * s + omega_n**2),
        f=f)

    f1 = exam_class.MappingSystem.fromFunction(fun_f1)
    f2 = exam_class.MappingSystem.fromFunction(lambda x: x ** 3)

    f1h = exam_class.TimeDomainSystem.cascade_system2(f1, h)
    f1hf2 = exam_class.TimeDomainSystem.cascade_system2(f1h, f2)
    tr_sin = exam_class.TimeSeries.fromSin(1, 1, fs, time_length)
    tr_wswf = h.time_response(tr_sin)
    tr_f1wswf = f1h.time_response(tr_sin)
    tr_f1hf2 = f1hf2.time_response(tr_sin)

    # tr_wswf.plot()
    # tr_f1wswf.plot()
    # tr_f1wswff2.plot()

    h.plot()
    fr_h = System.frequency_response_from_time_domain(
        h, amplitude=1, f=f, fs=fs, time_length=time_length)
    fr_f1h = System.frequency_response_from_time_domain(
        f1h, amplitude=1, f=f, fs=fs, time_length=time_length)
    fr_f1h_2 = System.frequency_response_from_time_domain(
        f1h, amplitude=2, f=f, fs=fs, time_length=time_length)

    fr_h.plot()
    fr_f1h.plot()
    fr_f1h_2.plot()
    plt.show()


def W_response():
    f = np.logspace(math.log10(0.5), math.log10(150), 50)  # 0.1 Hz 到 1000 Hz
    fs = 2000
    time_length = 100
    f_sin = 2
    A_sin = 1

    s = System.s
    f0 = 10
    delta = 0.01  # 阻尼比
    omega_n = 2 * np.pi * f0

    h = System.fromSymbol(
        s / (s ** 2 + 2 * delta * omega_n * s + omega_n**2),
        f=f)

    f1 = exam_class.MappingSystem.fromFunction(fun_f1)
    f2 = exam_class.MappingSystem.fromFunction(lambda x: x ** 3)
    f3 = exam_class.MappingSystem.fromFunction(fun_f3)

    f1h = exam_class.TimeDomainSystem.cascade_system2(f1, h)
    f3h = exam_class.TimeDomainSystem.cascade_system2(f3, h)
    f3hf3 = exam_class.TimeDomainSystem.cascade_system2(f3h, f3)
    fh2 = exam_class.TimeDomainSystem.cascade_system2(h, f2)
    hf1 = exam_class.TimeDomainSystem.cascade_system2(h, f1)

    tr_sin = exam_class.TimeSeries.fromSin(A_sin, f_sin, fs, time_length)
    tr_h = h.time_response(tr_sin)
    tr_f1h = f1h.time_response(tr_sin)
    tr_f3h = f3h.time_response(tr_sin)

    exam_class.TimeSeries.dump_multichannel_to_binary(
        [tr_sin, tr_h, tr_f1h, tr_f3h],
        '.data/tr_sin_h_f1h_f3h.bin')

    # tr_sin.plot()
    # tr_h.plot()
    # tr_f1h.plot()
    # tr_f3h.plot()

    # fr_h = System.frequency_response_from_time_domain(
    #     h, amplitude=1, f=f, fs=fs, time_length=time_length)
    system = hf1
    # fr_fh = System.frequency_response_from_time_domain(
    #     system, amplitude=1, f=f, fs=fs, time_length=time_length)
    # fr_fh_2 = System.frequency_response_from_time_domain(
    #     system, amplitude=2, f=f, fs=fs, time_length=time_length)
    # fr_fh_3 = System.frequency_response_from_time_domain(
    #     system, amplitude=5, f=f, fs=fs, time_length=time_length)
    # fr_fh_4 = System.frequency_response_from_time_domain(
    #     system, amplitude=10, f=f, fs=fs, time_length=time_length)

    # fr_h.plot()
    # fr_fh.plot()
    # fr_fh_2.plot()
    # fr_fh_3.plot()
    # fr_fh_4.plot()

    # tr_sin.plot()
    # tr_fh.plot()

    tr_sin_load, tr_h_load, tr_f1h_load, tr_f3h_load = exam_class.TimeSeries.load_multichannel_from_binary(
        '.data/tr_sin_h_f1h_f3h.bin')
    print(f"tr_sin:{tr_sin_load.params}")
    print(f"tr_h_load:{tr_h_load.params}")
    tr_sin_load.plot()
    tr_h_load.plot()
    plt.show()


def Sin_frequencs_create():
    f = np.logspace(math.log10(0.5), math.log10(150), 50)  # 0.5 Hz 到 150 Hz
    fs = 2000
    tr_sins = []
    time_length = 10
    for f_this in f:
        tr_sin = exam_class.TimeSeries.fromSin(1, f_this, fs, time_length)
        tr_sins.append(tr_sin)
    exam_class.TimeSeries.dump_multichannel_to_binary(
        tr_sins, '.data/tr_sins.bin')


def generate_data():
    s = System.s
    f = np.logspace(math.log10(0.5), math.log10(150), 50)  # 0.5 Hz 到 150 Hz
    A = np.logspace(math.log10(0.01), math.log10(100), 10)
    fs = 2000

    tr_sins = []
    time_length = 10
    for a in A:
        for f_this in f:
            tr_sin = exam_class.TimeSeries.fromSin(a, f_this, fs, time_length)
            tr_sins.append(tr_sin)
    exam_class.TimeSeries.dump_multichannel_to_binary(
        tr_sins, '.data/tr_sins.bin')

    ws = System.fromSymbol(
        (53882.0 * s) / (s**2 + 624.82*s + 56815.23),
        f=f)

    wf = System.fromSymbol(
        (0.0132 * s ** 2 + 6.6*s) / (0.00704 * s ** 2 + 0.252 * s + 1.0),
        f=f)

    wswf = exam_process.cascade_system(ws, wf)

    tr_wswfs = []
    for tr_sin in tr_sins:
        tr_wswf = wswf.time_response(tr_sin)
        A = tr_sin.params['Amplitude']
        f = tr_sin.params['Frequency']
        tr_wswf.set_param('name', f'wswf(A={A:.02f},f={f:.02f})')
        tr_wswfs.append(tr_wswf)

    exam_class.TimeSeries.dump_multichannel_to_binary(
        tr_wswfs, '.data/tr_wswfs.bin')


def base_wswf_time_domin():
    s = System.s
    f = np.logspace(math.log10(0.5), math.log10(150), 50)  # 0.5 Hz 到 150 Hz
    ws = System.fromSymbol(
        (53882.0 * s) / (s**2 + 624.82*s + 56815.23),
        f=f)

    wf = System.fromSymbol(
        (0.0132 * s ** 2 + 6.6*s) / (0.00704 * s ** 2 + 0.252 * s + 1.0),
        f=f)

    wswf = exam_process.cascade_system(ws, wf)
    wswf.plot()
    wswft = wswf.frequency_response_system(
        use_parallel=True)
    wswft.plot()
    plt.show()


if __name__ == '__main__':
    # Sin_frequencs_create()
    # W_response()
    base_wswf_time_domin()
