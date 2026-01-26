from .analyzer import DataAnalyzeResultList
import numpy as np
import matplotlib.pyplot as plt

# 尝试打开 ws.xlsx 文件
try:
    # 载入数据
    dataAnalyzeResultList = DataAnalyzeResultList()
    dataAnalyzeResultList.load_from_excel_file('ws.xlsx')
except:
    # 载入数据
    dataAnalyzeResultList = DataAnalyzeResultList()
    dataAnalyzeResultList.load_from_json_file('ws_analyze.json')
    dataAnalyzeResultList.save_to_excel_file('ws.xlsx')

# 提取增益和频率数据
ws_gain = np.array(
    [result.gain_integrate for result in dataAnalyzeResultList.dataAnalyzeResults])
ws_freq = np.array(
    [result.freq for result in dataAnalyzeResultList.dataAnalyzeResults])
ws_phase = np.array(
    [result.phase_integrate for result in dataAnalyzeResultList.dataAnalyzeResults])


def Wf_calculate(s, X0, X1, X2, X3, Y0, Y1, Y2, Y3):
    return (X3 * s**3 + X2 * s**2 + X1 * s + X0) / (Y3 * s**3 + Y2 * s**2 + Y1 * s + Y0)


def plot_transfer_function(R1=33e3, R2=130e3, R3=157e3, R4=510e3, C1=2.2e-6, C2=12e-9, C3=0.1e-6):
    A = R3 * C3 * R4
    B = (R3 + R4) * C3
    C = R2 * C1 * C2
    D = R2 * C2 + R2 * C1 + C1

    X3 = A * C
    X2 = R4 * C + A * C1
    X1 = R4 * C1
    X0 = 0
    Y3 = B * C
    Y2 = C + B * D
    Y1 = B + D
    Y0 = 1

    # 输出分子和分母的系数
    print("分子系数:")
    print("X0 =", X0)
    print("X1 =", X1)
    print("X2 =", X2)
    print("X3 =", X3)
    print("\n分母系数:")
    print("Y0 =", Y0)
    print("Y1 =", Y1)
    print("Y2 =", Y2)
    print("Y3 =", Y3)

    freq_start_hz = 0.2  # Hz
    freq_end_hz = 300  # Hz

    freq_start_w = 2 * np.pi * freq_start_hz
    freq_end_w = 2 * np.pi * freq_end_hz

    w = np.logspace(np.log10(freq_start_w), np.log10(freq_end_w), 1000)
    s = 1j * w
    Wf = Wf_calculate(s, X0, X1, X2, X3, Y0, Y1, Y2, Y3)
    Wf_abs = np.abs(Wf)
    Wf_phase = np.angle(Wf, deg=True)  # 相位以度为单位
    f = w / (2 * np.pi)

    ws_wf_freq = ws_freq
    ws_wf_w = 2 * np.pi * ws_wf_freq
    ws_wf_s = 1j * ws_wf_w
    ws_wf_wf = Wf_calculate(ws_wf_s, X0, X1, X2, X3, Y0, Y1, Y2, Y3)
    ws_wf_wf_abs = np.abs(ws_wf_wf)
    ws_wf_wf_phase = np.angle(ws_wf_wf, deg=True)  # 相位以度为单位
    ws_wf_wswf_abs = ws_wf_wf_abs * ws_gain
    ws_wf_wswf_phase = ws_wf_wf_phase + ws_phase

    fig, (ax1, ax2) = plt.subplots(1, 2)  # 调整宽度和高度

    ax1.set_xlabel('Frequency (Hz)')
    ax1.set_ylabel('Amplitude', color='tab:blue')
    ax1.loglog(f, Wf_abs, color='tab:blue')
    ax1.loglog(ws_freq, ws_gain, '-', marker='o', color='m', markersize=2)
    ax1.loglog(ws_freq, ws_wf_wswf_abs, '-',
               marker='o', color='g', markersize=2)
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax1.grid(True, which='both', ls='-.', color='0.65')

    ax2.set_ylabel('Phase (Degrees)', color='tab:red')
    ax2.semilogx(f, Wf_phase, color='tab:red')
    ax2.semilogx(ws_freq, ws_phase, '-', marker='o', color='c', markersize=2)
    ax2.semilogx(ws_freq, ws_wf_wswf_phase, '-',
                 marker='o', color='y', markersize=2)
    ax2.tick_params(axis='y', labelcolor='tab:red')

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
    fig.set_size_inches(16, 6)
    fig.subplots_adjust(top=0.82)  # 调整顶部边距以为标题留出更多空间
    title_str = f"R1={R1 / 1e3}k, R2={R2 / 1e3}k, R3={R3 / 1e3}k, R4={R4 / 1e3}k\n"
    title_str += f"C1={C1 / 1e-6}u, C2={C2 / 1e-9}n, C3={C3 / 1e-6}u\n"
    title_str += f"X0={X0}, X1={X1}, X2={X2}, X3={X3}\n"
    title_str += f"Y0={Y0}, Y1={Y1}, Y2={Y2}, Y3={Y3}"
    # legend
    ax1.legend(['As', 'Af', 'As × Af'], loc='upper left')
    ax2.legend(['Φs', 'Φf', 'Φs + Φf'], loc='upper right')
    # title 放到 fig1
    fig.suptitle(title_str, fontsize=10, y=1.05)
    plt.show()


if __name__ == "__main__":
    plot_transfer_function()
