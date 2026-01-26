import numpy as np
from scipy.optimize import least_squares
from scipy.signal import tf2sos, sosfreqz
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 设置字体为 SimHei（或其他支持中文的字体）
rcParams['font.sans-serif'] = ['SimHei']  # Windows 用户
# rcParams['font.sans-serif'] = ['STHeiti']  # macOS 用户
# rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei']  # Linux 用户

rcParams['axes.unicode_minus'] = False

# 已知目标频率响应（复数形式）
fs = 1000  # 采样频率，单位 Hz
w = np.logspace(np.log10(1), np.log10(fs/2), 512)  # 频率范围 [1, fs/2] Hz
Hd = 1 / (1 + 1j * w / 150)     # 示例：复数频率响应

# 定义滤波器的频率响应计算


def freq_response(b, a, w):
    z = np.exp(1j * w)  # z = e^(jω)
    numerator = np.polyval(b[::-1], z)  # 分子多项式
    denominator = np.polyval(a[::-1], z)  # 分母多项式
    return numerator / denominator

# 定义误差函数


def error_function(coeffs, n, m, w, Hd):
    b = coeffs[:n+1]  # 提取分子系数
    a = np.concatenate(([1], coeffs[n+1:]))  # 提取分母系数（a[0] = 1）
    H_fit = freq_response(b, a, w)  # 计算拟合频率响应
    return np.abs(Hd - H_fit)  # 计算误差


# 初始化参数
n = 6  # 分子阶次
m = 6  # 分母阶次
initial_coeffs = np.ones(n + m + 1)  # 初始猜测改为全1

# 使用优化算法拟合滤波器系数
result = least_squares(
    error_function,
    initial_coeffs,
    args=(n, m, w, Hd),
    bounds=(-10, 10),  # 系数的上下界
    ftol=1e-9,  # 函数值变化容忍度
    xtol=1e-9,  # 参数变化容忍度
    gtol=1e-9   # 梯度变化容忍度
)

# 提取拟合结果
b = result.x[:n+1]
a = np.concatenate(([1], result.x[n+1:]))

# 将传递函数转换为 SOS 形式
sos = tf2sos(b, a)

# 计算拟合后的频率响应
w_fit, h_fit = sosfreqz(sos, worN=512)

# 绘图
plt.figure()
plt.plot(w, np.abs(Hd), label="目标幅度响应")
plt.plot(w_fit * fs / (2 * np.pi), np.abs(h_fit), label="拟合幅度响应", linestyle='--')
plt.xscale('log')
plt.yscale('log')
plt.legend()
plt.title("IIR 滤波器拟合（SOS 实现）")
plt.xlabel("频率 (Hz)")
plt.ylabel("幅度")
plt.grid(which='both', linestyle='--')
plt.show()
