import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from matplotlib import rcParams
from scipy.signal import minimum_phase  # 导入minimum_phase函数


if __name__ == "__main__":

    # 设置中文字体和取消负号前的空格
    rcParams['font.sans-serif'] = ['SimHei']  # 设置字体为黑体
    rcParams['axes.unicode_minus'] = False    # 解决负号显示问题

    # 1. 设计欠阻尼的二阶IIR滤波器
    # 定义采样频率
    fs = 1000  # 采样频率，单位Hz

    # 定义模拟滤波器参数
    f_n = 50  # 自然频率，单位Hz
    omega_n = 2 * np.pi * f_n  # 自然角频率
    zeta = 0.1  # 阻尼比

    # 创建模拟滤波器的传递函数
    num = [omega_n**2]
    den = [1, 2 * zeta * omega_n, omega_n**2]

    # 将模拟滤波器转换为数字滤波器（双线性变换）
    b_iir, a_iir = signal.bilinear(num, den, fs)

    # 2. 获取IIR滤波器的频率响应
    w, h = signal.freqz(b_iir, a_iir, worN=8000)
    freq = w * fs / (2 * np.pi)  # 频率轴，单位Hz

    # 归一化频率到 [0, 1]
    freq_points = freq / (fs / 2)

    # 3. 使用最小二乘法设计线性相位FIR滤波器
    numtaps = 125  # FIR滤波器阶数为奇数
    b_fir_linear = signal.firls(numtaps, freq_points, abs(h))

    # 4. 将线性相位FIR滤波器转换为最小相位FIR滤波器
    b_fir_min = minimum_phase(b_fir_linear)  # 计算最小相位滤波器

    # 5. 计算IIR、线性相位FIR和最小相位FIR的频率响应
    w_iir, h_iir = signal.freqz(b_iir, a_iir, worN=8000)  # IIR
    w_fir_linear, h_fir_linear = signal.freqz(b_fir_linear, worN=8000)  # 线性相位FIR
    w_fir_min, h_fir_min = signal.freqz(b_fir_min, worN=8000)  # 最小相位FIR

    # 6. 绘制频率响应对比图
    plt.figure(figsize=(10, 8))

    # 幅度响应
    plt.subplot(2, 1, 1)
    plt.plot(w_iir * fs / (2 * np.pi), 20 * np.log10(abs(h_iir)), label='IIR滤波器')
    plt.plot(w_fir_linear * fs / (2 * np.pi), 20 * np.log10(abs(h_fir_linear)), label='FIR滤波器 (线性相位)', linestyle='-.')
    plt.plot(w_fir_min * fs / (2 * np.pi), 20 * np.log10(abs(h_fir_min)), label='FIR滤波器 (最小相位)', linestyle='--')
    plt.title('滤波器幅度响应')
    plt.xlabel('频率 (Hz)')
    plt.ylabel('幅度 (dB)')
    plt.grid(True)
    plt.legend()

    # 相位响应
    plt.subplot(2, 1, 2)
    plt.plot(w_iir * fs / (2 * np.pi), np.unwrap(np.angle(h_iir)), label='IIR滤波器')
    plt.plot(w_fir_linear * fs / (2 * np.pi), np.unwrap(np.angle(h_fir_linear)), label='FIR滤波器 (线性相位)', linestyle='-.')
    plt.plot(w_fir_min * fs / (2 * np.pi), np.unwrap(np.angle(h_fir_min)), label='FIR滤波器 (最小相位)', linestyle='--')
    plt.title('滤波器相位响应')
    plt.xlabel('频率 (Hz)')
    plt.ylabel('相位 (弧度)')
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    plt.show()
