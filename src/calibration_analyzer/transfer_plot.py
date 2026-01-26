import numpy as np
import matplotlib.pyplot as plt


def plot_transfer_function(R1=33e3, R2=130e3, R3=157e3, R4=510e3, C1=2.2e-6, C2=12e-9, C3=0.1e-6):
    A = R3 * C3 * R4
    B = (R3 + R4) * C3
    C = R2 * C1 * C2
    D = R2 * C2 + R2 * C1 + C1

    X1 = A * C
    X2 = R4 * C + A * C1
    X3 = R4 * C1
    Y1 = B * C
    Y2 = C + B * D
    Y3 = B + D

    # 输出分子和分母的系数
    print("分子系数:")
    print("X1 =", X1)
    print("X2 =", X2)
    print("X3 =", X3)
    print("\n分母系数:")
    print("Y1 =", Y1)
    print("Y2 =", Y2)
    print("Y3 =", Y3)

    freq_start_hz = 0.01  # Hz
    freq_end_hz = 100000  # Hz

    freq_start_w = 2 * np.pi * freq_start_hz
    freq_end_w = 2 * np.pi * freq_end_hz

    w = np.logspace(np.log10(freq_start_w), np.log10(freq_end_w), 1000)
    s = 1j * w
    H = (X1 * s ** 3 + X2 * s ** 2 + X3 * s) / \
        (Y1 * s ** 3 + Y2 * s ** 2 + Y3 * s + 1)
    H_abs = np.abs(H)
    H_phase = np.angle(H, deg=True)  # 相位以度为单位
    f = w / (2 * np.pi)

    fig, ax1 = plt.subplots(figsize=(8, 6))  # 调整宽度和高度

    color = 'tab:blue'
    ax1.set_xlabel('Frequency (Hz)')
    ax1.set_ylabel('Amplitude', color=color)
    ax1.loglog(f, H_abs, color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, which='both', ls='-.', color='0.65')

    ax2 = ax1.twinx()  # 实例化第二个y轴
    color = 'tab:red'
    ax2.set_ylabel('Phase (Degrees)', color=color)
    ax2.semilogx(f, H_phase, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    # 每x度画一条虚线（画线函数）
    color_phase_grid = 'tab:red'
    alpha_phase_grid = 0.8
    style_phase_grid = ':'
    # 间隔
    phase_grid_interval = 30
    # 获取y轴上下限
    y1, y2 = ax2.get_ylim()
    # 将 y1, y2 转换为最接近的90的倍数
    y1 = int(y1 / phase_grid_interval) * phase_grid_interval
    y2 = int(y2 / phase_grid_interval) * phase_grid_interval
    for i in range(y1, y2, phase_grid_interval):
        ax2.axhline(y=i, color=color_phase_grid,
                    linestyle=style_phase_grid, alpha=alpha_phase_grid)

    fig.tight_layout()  # 调整布局
    fig.set_size_inches(8, 6)
    fig.subplots_adjust(top=0.82)  # 调整顶部边距以为标题留出更多空间
    title_str = f"R1={R1 / 1e3}k, R2={R2 / 1e3}k, R3={R3 / 1e3}k, R4={R4 / 1e3}k\n"
    title_str += f"C1={C1 / 1e-6}u, C2={C2 / 1e-9}n, C3={C3 / 1e-6}u\n"
    title_str += f"X1={X1}, X2={X2}, X3={X3}\n"
    title_str += f"Y1={Y1}, Y2={Y2}, Y3={Y3}"
    plt.title(title_str, fontsize=10, y=1.05)
    plt.show()


if __name__ == "__main__":
    plot_transfer_function()
