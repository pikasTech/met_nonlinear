import pandas as pd
import matplotlib.pyplot as plt
from .datastruct import DataRecordList
from .config import CONF_SAMPLING_RATE
from .analyzer import DataAnalyzeResult
import argparse
import traceback


fig = None


def plot_data(index: int, start_time: float, duration: float):
    global fig
    try:
        data_record = dataRecords.dataRecords[index]
    except IndexError:
        print('Index out of range!')
        traceback.print_exc()
        return
    param = data_record.param.params

    # 提取 ch1 和 ch2 数据
    ch1 = data_record.ch1
    ch2 = data_record.ch2
    ch1_integrate = data_record.ch1_integrate

    data_analyze_result = DataAnalyzeResult(data_record)

    try:
        data_analyze_result.analyze(start_time, duration)
    except Exception as e:
        print(e)
        traceback.print_exc()
        return

    fft_ch1 = data_analyze_result.ch1Result.fft_abs
    fft_ch2 = data_analyze_result.ch2Result.fft_abs
    fft_ch1_integrate = data_analyze_result.ch1IntegrateResult.fft_abs
    phase_ch1 = data_analyze_result.ch1Result.phase
    phase_ch2 = data_analyze_result.ch2Result.phase
    phase_ch1_integrate = data_analyze_result.ch1IntegrateResult.phase

    # 计算频率轴
    freq = pd.Index(data_analyze_result.ch1Result.fft_freq)

    # 绘制频谱图（三个子图）
    if fig is None:
        print('Creating new figure...')
        fig, ((ax1, ax2), (ax3, ax)) = plt.subplots(2, 2, figsize=(12, 7))
    else:
        print('Clearing figure...')
        ax1, ax2, ax3, ax = fig.axes
    ax1.cla()
    ax2.cla()
    ax3.cla()

    # 只绘制前半部分（正频率）
    freq = freq[:len(freq) // 2]
    fft_ch1 = fft_ch1[:len(fft_ch1) // 2]
    fft_ch2 = fft_ch2[:len(fft_ch2) // 2]
    fft_ch1_integrate = fft_ch1_integrate[:len(fft_ch1_integrate) // 2]
    ax1.loglog(freq, fft_ch1)
    ax1.set_title(
        f'Channel 1, THD: {data_analyze_result.ch1Result.thd * 100:.2f}%, Phase: {phase_ch1:.2f}°')
    ax1.set_xlabel('Frequency (Hz)')
    ax1.set_ylabel('Amplitude')
    ax2.loglog(freq, fft_ch2)
    ax2.set_title(
        f'Channel 2, THD: {data_analyze_result.ch2Result.thd * 100:.2f}%, Phase: {phase_ch2:.2f}°')
    ax2.set_xlabel('Frequency (Hz)')
    ax2.set_ylabel('Amplitude')
    ax3.loglog(freq, fft_ch1_integrate)
    ax3.set_title(
        f'Channel 1 (integrated), THD: {data_analyze_result.ch1IntegrateResult.thd * 100:.2f}%, Phase: {phase_ch1_integrate:.2f}°')
    ax3.set_xlabel('Frequency (Hz)')
    ax3.set_ylabel('Amplitude')
    plt.tight_layout()

    # 将数据转换为 DataFrame
    df = pd.DataFrame({
        'Channel1': ch1,
        'Channel2': ch2,
        'Channel1_integrate': ch1_integrate
    })

    # 计算时间轴
    time = df.index / sampling_rate

    # 计算起始和结束时间索引
    start_idx = int(start_time * sampling_rate)
    end_idx = start_idx + int(duration * sampling_rate)

    # 清除当前图像
    ax.cla()

    # 绘图
    ax.plot(time[start_idx:end_idx], df['Channel1']
            [start_idx:end_idx], label='Channel 1')
    ax.plot(time[start_idx:end_idx], df['Channel2']
            [start_idx:end_idx], label='Channel 2')
    ax.plot(time[start_idx:end_idx], df['Channel1_integrate']
            [start_idx:end_idx],
            label='Channel 1 (integrated)')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Amplitude')
    ax.set_title(
        f'Index: {index}, Start: {start_time}s, Duration: {duration}s, Frequency: {param["freq"]}Hz')
    ax.legend()
    plt.draw()
    plt.pause(0.001)  # 短暂暂停以更新图像


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', default='data.json',
                        help='JSON file name')
    args = parser.parse_args()

    file_name = args.file
    # data = json.loads(json_data)
    dataRecords = DataRecordList()
    dataRecords.load_from_json_file(file_name)

    # 设置默认参数
    index = 0
    start_time = 0
    duration = 1

    # 采样率（假设）
    sampling_rate = CONF_SAMPLING_RATE

    plt.ion()  # 开启交互模式
    # fig, ax = plt.subplots(figsize=(10, 6))  # 创建初始的 figure 和 axis

    # 交互模式
    plot_data(index, start_time, duration)
    while True:
        cmd = input(
            "Enter command ([i]ndex/[s]tart_time/[d]uration) or 'exit' to quit: ").split()
        if not cmd:
            continue

        if cmd[0] in ['exit', 'q', 'quit', 'exit()']:
            break

        try:
            if cmd[0] in ['index', 'i']:
                if len(cmd) == 1:
                    index += 1
                else:
                    index = int(cmd[1])
            elif cmd[0] in ['start_time', 's']:
                start_time = float(cmd[1])
            elif cmd[0] in ['duration', 'd']:
                duration = float(cmd[1])
            plot_data(index, start_time, duration)
        except:
            print('Invalid command!')
            traceback.print_exc()
            continue
