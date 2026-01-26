import numpy as np
import matplotlib.pyplot as plt

# 设置采样率和时间长度
fs = 1000  # 采样率 (Hz)
duration = 10  # 时间 (秒)
t = np.linspace(0, duration, int(fs * duration), endpoint=False)

# 生成不同频率的正弦波组成地震信号
# 模拟低频、中频和高频信号
low_freq = 10  # 低频 (Hz)
mid_freq = 40# 中频 (Hz)
high_freq = 80# 高频 (Hz)

low_amplitude = 0.0
mid_amplitude = 0.5
high_amplitude = 0.5

low_signal = low_amplitude * np.sin(2 * np.pi * low_freq * t)
mid_signal = mid_amplitude * np.sin(2 * np.pi * mid_freq * t)
high_signal = high_amplitude * np.sin(2 * np.pi * high_freq * t)

# 加入随机噪声模拟震动中的不规则性
# noise = np.random.normal(0, 0.05, len(t))  # 均值为0，标准差为0.05的随机噪声

# 合成复合波形
composite_signal = low_signal + mid_signal + high_signal

# 可视化结果
plt.figure(figsize=(10, 6))
plt.plot(t, composite_signal, label='Composite Seismic Signal')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.title('Simulated Seismic Composite Waveform')
plt.legend()
plt.grid(True)
plt.show()
