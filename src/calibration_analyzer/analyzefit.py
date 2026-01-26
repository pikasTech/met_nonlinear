from .analyzer import DataAnalyzeResultList
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
import sys

plt.ioff()

# 指定拟合的频率范围
min_freq = 5
max_freq = 100
# fit_model = 'second_order_high'
# fit_model = 'second_order_low'
fit_model = 'combined'

# 载入数据
dataAnalyzeResultList = DataAnalyzeResultList()
dataAnalyzeResultList.load_from_json_file('fitdata.json')

# 提取增益和频率数据
gain = np.array(
    [result.gain_integrate for result in dataAnalyzeResultList.dataAnalyzeResults])
freq = np.array(
    [result.freq for result in dataAnalyzeResultList.dataAnalyzeResults])
phase = np.array(
    [result.phase_integrate for result in dataAnalyzeResultList.dataAnalyzeResults])


# 筛选指定频率范围内的数据点
indices = (min_freq <= freq) & (freq <= max_freq)
filtered_freq = freq[indices]
filtered_gain = gain[indices]

# 转换频率到角频率
w_filtered = 2 * np.pi * filtered_freq
w = 2 * np.pi * freq

# 等对数间隔插值的w值（用于绘制拟合曲线）
freq_fit = np.logspace(np.log10(freq[0]), np.log10(freq[-1]), 1000)
w_fit = 2 * np.pi * freq_fit

# 定义标准二阶系统的幅度响应计算函数
# 传递函数：K * wn**2 / (s**2 + 2*zeta*wn*s + wn**2)


# Corrected gain calculation for a second-order low-pass filter
def second_order_low_transfer_function_gain(w, K, wn, zeta):
    # Avoid division by zero
    denominator = (wn**2 - w**2)**2 + (2 * zeta * wn * w)**2 + 1e-10
    return K * wn**2 / np.sqrt(denominator)

# Corrected phase calculation for a second-order low-pass filter


def second_order_low_transfer_function_phase(w, K, wn, zeta):
    return np.arctan2(2 * zeta * wn * w, wn**2 - w**2) * 180 / np.pi

# Corrected gain calculation for a second-order high-pass filter


def second_order_high_transfer_function_gain(w, K, wn, zeta):
    # Avoid division by zero
    numerator = w**2
    denominator = (wn**2 - w**2)**2 + (2 * zeta * wn * w)**2 + 1e-10
    return K * numerator / np.sqrt(denominator)

# Corrected phase calculation for a second-order high-pass filter


def second_order_high_transfer_function_phase(w, K, wn, zeta):
    # The phase angle of a high-pass filter should be computed based on its numerator, s^2 (which is w^2 in the frequency domain)
    return np.arctan2(w**2, -2 * zeta * wn * w + wn**2) * 180 / np.pi


# 定义一阶高通滤波器乘以二阶系统的幅度响应计算函数
def combined_transfer_function_gain(w, K, wn, zeta, wc):
    # 一阶高通滤波器的分子和分母
    high_pass_num = w
    high_pass_den = w + wc

    # 二阶系统的分子和分母
    second_order_num = K * wn**2
    second_order_den = (wn**2 - w**2)**2 + (2*zeta*wn*w)**2 + 1e-10

    # 组合传递函数的增益
    return (high_pass_num / high_pass_den) * (second_order_num / np.sqrt(second_order_den))

# 定义一阶高通滤波器乘以二阶系统的相位响应计算函数


def combined_transfer_function_phase(w, K, wn, zeta, wc):
    # 避免 w 为零导致的数值问题
    w_safe = np.maximum(w, 1e-10)  # 将 w 的最小值设置为 1e-10
    high_pass_phase = np.arctan(w_safe / wc)
    second_order_phase = np.arctan2(2*zeta*wn*w_safe, wn**2 - w_safe**2)
    return np.degrees(high_pass_phase + second_order_phase)


def fit_gain(w, *params):
    return getattr(sys.modules[__name__], fit_model + '_transfer_function_gain')(w, *params)

# 拟合相位数据


def fit_phase(w, *params):
    return getattr(sys.modules[__name__], fit_model + '_transfer_function_phase')(w, *params)


p0_initial_guss_high = [9.689088379709935,
                        1.190995708685252, 40.17252525628525]

p0_initial_guss_low = [
    3.80468692e+01, 5.53325566e+02, 1.33688245e-01]

if fit_model == 'combined':
    p0_initial_guess = [3.80468692e+01,
                        5.53325566e+02, 1.33688245e-01, 7.08243442e+02]
elif fit_model == 'second_order_low':
    p0_initial_guess = p0_initial_guss_low
elif fit_model == 'second_order_high':
    p0_initial_guess = p0_initial_guss_high

popt_gain, _ = curve_fit(getattr(sys.modules[__name__], fit_model + '_transfer_function_gain'),
                         w_filtered, filtered_gain, p0=p0_initial_guess)


print('拟合结果：')
print(list(popt_gain))

# 计算拟合的幅度和相位
fitted_gain = fit_gain(w_fit, *popt_gain)
fitted_phase = fit_phase(w_fit, *popt_gain)

# 绘图
plt.figure(figsize=(12, 6))

# 绘制增益
plt.subplot(1, 2, 1)
plt.loglog(freq, gain, 'b-', marker='o', label='原始增益')
plt.loglog(freq_fit, fitted_gain, 'r--',  label='拟合增益')
plt.xlabel('频率 (Hz)')
plt.ylabel('增益')
plt.title('增益拟合')
plt.legend()

# 绘制相位拟合图
plt.subplot(1, 2, 2)
plt.semilogx(freq, phase, 'g-', marker='o', label='原始相位')
plt.semilogx(freq_fit, fitted_phase, 'r--', label='拟合相位')
plt.xlabel('频率 (Hz)')
plt.ylabel('相位 (度)')
plt.title('相位拟合')
plt.legend()
plt.ylim(-360, 360)  # 相位通常在 -180 到 180 度之间

plt.tight_layout()
plt.show()
