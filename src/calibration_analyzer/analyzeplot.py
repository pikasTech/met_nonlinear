import re
from . import config
from .config import CONF_USING_REF_PHASE, CONF_USING_REF_GAIN, CONF_GAIN_REF, CONF_PHASE_REF, CONF_PHASE_REF_SHIFT
from matplotlib.ticker import MultipleLocator
import colorsys
from .analyzer import DataAnalyzeResultList
from . import analyzer
import matplotlib.pyplot as plt
import argparse
import os
from . import utils


def parse_cmd(cmd):
    # Remove the '@' character from the start
    cmd = cmd.lstrip('@')

    # Use regular expression to find all letter-number pairs
    pairs = re.findall(r'([A-Za-z])([0-9]+\.?[0-9]*)', cmd)

    # Convert these pairs into a dictionary
    return {letter: float(number) if '.' in number else int(number) for letter, number in pairs}


# Set the font to a Chinese font that supports the required glyphs

plt.ioff()


def make_color(base_color, index: int):
    hue_shift = config.CONF_COLOR_HUE_SHIFT  # 色相偏移量
    if isinstance(base_color, str):
        base_color = {
            'r': (1, 0, 0),
            'g': (0, 1, 0),
            'b': (0, 0, 1),
            'c': (0, 1, 1),
            'm': (1, 0, 1),
            'y': (1, 1, 0),
            'k': (0, 0, 0),
            'w': (1, 1, 1)
        }[base_color]

    # 转换 RGB 到 HSV
    hsv_color = colorsys.rgb_to_hsv(*base_color)

    # 计算新的色相值，并确保它在 0 到 1 的范围内
    new_hue = (hsv_color[0] + hue_shift * index) % 1.0

    # 创建新颜色的 HSV 值
    new_color_hsv = (new_hue, hsv_color[1], hsv_color[2])

    # 将 HSV 转换回 RGB
    new_color_rgb = colorsys.hsv_to_rgb(*new_color_hsv)

    return new_color_rgb


fig = None
ax_gain, ax_THD, ax_phase, ax_vibration = None, None, None, None
index = 0
gain_max = -1
gain_min = -1


def update_gain_max_min(gain_list: list[float]):
    global gain_max, gain_min
    if gain_list:  # Check if the list is not empty
        # Update gain_max and gain_min with the max and min of the current list
        current_max = max(gain_list)
        current_min = min(gain_list)

        # If gain_max or gain_min have not been set yet (still -1), update them directly
        if gain_max == -1:
            gain_max = current_max
        else:
            gain_max = max(gain_max, current_max)

        if gain_min == -1:
            gain_min = current_min
        else:
            gain_min = min(gain_min, current_min)
    else:
        print("The input list is empty.")


ax_list = []  # 初始化一个空的轴列表


def create_ax(ax_list, fig):
    """
    创建一个轴(ax)。如果ax_list为空，则创建一个新的ax并加入到列表中。
    如果ax_list已有元素，则在列表的第一个ax上使用twinx()创建一个新的ax。

    参数:
    ax_list: 存储轴对象的列表。
    fig: 当前的Figure对象。

    返回:
    新创建的轴对象。
    """
    if not ax_list:  # 如果列表为空
        ax = fig.add_subplot(111)  # 创建一个新的轴对象
        ax_list.append(ax)  # 将新的轴对象添加到列表中
    else:
        ax = ax_list[0].twinx()  # 使用列表中的第一个轴对象创建twinx
        ax_list.append(ax)  # 将新的轴对象也添加到列表中

    return ax


def analyze_plot(file_name: str,
                 show: bool = False,
                 gain_amp: float = 1.0,
                 phase_shift: float = 0.0,
                 legend_prefix: str = '',
                 start_freq: float = None,
                 end_freq: float = None,
                 keep_fig: bool = True,
                 using_gain: bool = True,
                 using_phase: bool = True,
                 using_THD: bool = True,
                 using_vibration: bool = False,
                 using_vibration_speed: bool = False,
                 using_vibration_V: bool = True,
                 ):
    global fig, ax_gain, ax_THD, ax_phase, ax_vibration, index
    global gain_max, gain_min
    global ax_list

    if not keep_fig:
        index = 0

    # Clear the figure if not keeping it
    if not keep_fig and fig is not None:
        fig.clear()
        ax_gain, ax_THD, ax_phase, ax_vibration = None, None, None, None
        ax_list = []
        gain_max, gain_min = -1, -1

    if fig is None:
        fig = plt.figure()

    if using_gain and ax_gain is None:
        ax_gain = create_ax(ax_list, fig)

    if using_phase and ax_phase is None:
        ax_phase = create_ax(ax_list, fig)

    if using_THD and ax_THD is None:
        ax_THD = create_ax(ax_list, fig)

    if using_vibration and ax_vibration is None:
        if using_gain:
            ax_vibration = ax_gain
        else:
            ax_vibration = create_ax(ax_list, fig)

    config.load_keyword_profile(file_name)
    dataAnalyzeResultList = DataAnalyzeResultList()
    dataAnalyzeResultList.load_from_json_file(file_name)

    # 提取增益和失真度数据
    gain_integrate = dataAnalyzeResultList.get_gain_integrate()
    gain = dataAnalyzeResultList.get_gain()
    if config.CONF_USING_INTERGRATE:
        gain_select = gain_integrate
    else:
        gain_select = gain
    gain_select = [gain * gain_amp for gain in gain_select]
    freq = dataAnalyzeResultList.get_freq()
    thd1 = [
        result.ch1IntegrateResult.thd * 100 for result in dataAnalyzeResultList.dataAnalyzeResults]
    thd2 = [
        result.ch2Result.thd * 100 for result in dataAnalyzeResultList.dataAnalyzeResults]

    if using_vibration_speed:
        vibration1 = [
            result.ch1IntegrateResult.main_freq_amplitude for result in dataAnalyzeResultList.dataAnalyzeResults]
    else:
        vibration1 = [
            result.ch1Result.main_freq_amplitude for result in dataAnalyzeResultList.dataAnalyzeResults]

    vibration1_mm_s2 = [item * 9806.65/0.2152 *
                        config.CONF_VIBRATION_CALI_RATIO for item in vibration1]

    vibration2 = [
        result.ch2Result.main_freq_amplitude for result in dataAnalyzeResultList.dataAnalyzeResults]

    phase_intergrate = [
        result.phase_integrate for result in dataAnalyzeResultList.dataAnalyzeResults]

    phase = [result.phase for result in dataAnalyzeResultList.dataAnalyzeResults]

    if config.CONF_USING_INTERGRATE:
        phase_select = phase_intergrate
    else:
        phase_select = phase

    phase_select = [
        phase + phase_shift for phase in phase_select]

    if start_freq is not None:
        # find the first item that is greater than start_freq
        start_index = next(
            (i for i, freq in enumerate(freq) if freq > start_freq), None)
        gain_select = gain_select[start_index:]
        freq = freq[start_index:]
        thd1 = thd1[start_index:]
        thd2 = thd2[start_index:]
        phase_select = phase_select[start_index:]
        phase = phase[start_index:]

    if end_freq is not None:
        end_index = next(
            (i for i, freq in enumerate(freq) if freq > end_freq), None)
        gain_select = gain_select[:end_index]
        freq = freq[:end_index]
        thd1 = thd1[:end_index]
        thd2 = thd2[:end_index]
        phase_select = phase_select[:end_index]
        phase = phase[:end_index]

    if ax_list:
        ax_list[0].set_xlabel('Frequency (Hz)')

    if using_gain:
        ax_gain.set_ylabel('Sensitivity(V/m/s)', color='r')
        ax_gain.tick_params(axis='y', labelcolor='r')
        ax_gain.grid(True, which='both', ls='-.', color='0.65')

        update_gain_max_min(gain_select)
        # 绘制增益图，并为数据点添加圆圈标记
        ax_gain.loglog(freq, gain_select, '-', marker='o',
                       color=make_color('r', index), label=legend_prefix+'Sensitivity')

        # 如果y轴的上下限小于10倍，则设为10倍
        # Adjust y-axis limits if necessary
        if gain_max / gain_min < 10:
            y_min = gain_min / (10 ** (2/3))
            y_max = gain_max * (10 ** (1/3))
        else:
            y_min = gain_min
            y_max = gain_max

        if not using_vibration:
            ax_gain.set_ylim(y_min*0.8, y_max*1.2)

    if using_phase:
        # 创建第三个y轴用于相位
        ax_phase.set_ylabel('Phase (Degrees)', color='b')
        ax_phase.yaxis.set_major_locator(MultipleLocator(15))
        ax_phase.tick_params(axis='y', labelcolor='b')
        # 范围 [-360, 360]
        ax_phase.set_ylim([-360, 360])
        # 每90度画一条虚线（画线函数）
        color_90 = 'b'
        alpha_90 = 0.5
        style_90 = '--'
        ax_phase.axhline(y=0, color=color_90,
                         linestyle=style_90, alpha=alpha_90)
        ax_phase.axhline(y=90, color=color_90,
                         linestyle=style_90, alpha=alpha_90)
        ax_phase.axhline(y=180, color=color_90,
                         linestyle=style_90, alpha=alpha_90)
        ax_phase.axhline(y=270, color=color_90,
                         linestyle=style_90, alpha=alpha_90)
        ax_phase.axhline(y=-90, color=color_90,
                         linestyle=style_90, alpha=alpha_90)
        ax_phase.axhline(y=-180, color=color_90,
                         linestyle=style_90, alpha=alpha_90)
        ax_phase.axhline(y=-270, color=color_90,
                         linestyle=style_90, alpha=alpha_90)
        ax_phase.semilogx(freq, phase_select, '-', color=make_color('b',
                                                                    index), marker='x', label=legend_prefix + 'Phase')  # 使用实线

    if using_THD:
        # 创建第二个y轴用于失真度
        if len(ax_list) >= 3:
            ax_THD.spines["right"].set_position(("axes", 1.07))
        ax_THD.set_ylabel('THD(%)', color='m')
        ax_THD.tick_params(axis='y', labelcolor='m')
        ax_THD.yaxis.set_major_locator(MultipleLocator(5))
        ax_THD.set_ylim([0, 100])  # 设置y轴上限为100%

        ax_THD.semilogx(freq, thd1, '--', marker='o',
                        # 使用虚线
                        color=make_color('m', index), label=legend_prefix + 'REF_THD@CH1')
        ax_THD.semilogx(freq, thd2, '--', marker='o',
                        # 使用虚线
                        color=make_color('g', index), label=legend_prefix + 'TEST_THD@CH2')
        ax_THD.fill_between(freq, thd1, alpha=0.1,
                            color=make_color('b', index))  # 添加失真度的阴影
        ax_THD.fill_between(freq, thd2, alpha=0.1,
                            color=make_color('g', index))  # 添加失真度的阴影

    if using_vibration:
        if using_vibration_V:
            unit = '(V)'
        else:
            unit = '(mm/s)' if using_vibration_speed else '(mm/s^2)'
        if not using_gain:
            ax_vibration.set_ylabel('vibration' + unit, color='c')
            ax_vibration.grid(True, which='both', ls='-.', color='0.65')

        if using_vibration_V:
            vibration1_select = vibration1
        elif using_vibration_speed:
            vibration1_select = vibration1_mm_s2
        else:
            vibration1_select = vibration1_mm_s2

        ax_vibration.loglog(freq, vibration1_select, '--', marker='o',
                            color=make_color('c', index), label=legend_prefix +
                            'vibration' + unit)
        # ax_vibration.loglog(freq, vibration2, '--', marker='o',
        #                     color=make_color('k', index), label=legend_prefix +
        #                     'vibration@CH2')

    if CONF_USING_REF_PHASE:
        # 参考数据
        freq_ref = [item[0] for item in CONF_PHASE_REF]
        phase_ref = [item[1] for item in CONF_PHASE_REF]

        phase_ref_shift = phase_ref.copy()
        phase_ref_shift = [
            phase + CONF_PHASE_REF_SHIFT for phase in phase_ref_shift]

        # ax3.plot(freq_ref, phase_ref, 'c--', marker='o',
        #          label='REF_PHASE')  # 使用实线

        ax_phase.plot(freq_ref, phase_ref_shift, 'y--', marker='o',
                      label=f'REF_PHASE(+{CONF_PHASE_REF_SHIFT})')  # 使用实线

    if CONF_USING_REF_GAIN:
        freq_ref_gain = [item[0] for item in CONF_GAIN_REF]
        gain_ref = [item[1] for item in CONF_GAIN_REF]
        ax_gain.loglog(freq_ref_gain, gain_ref, 'b-', marker='o',
                       label='REF_GAIN')

    # 图例
    lines, labels = ax_gain.get_legend_handles_labels() if using_gain else ([], [])

    lines2, labels2 = ax_THD.get_legend_handles_labels() if using_THD else ([], [])

    lines3, labels3 = ax_phase.get_legend_handles_labels() if using_phase else ([], [])

    lines4, labels4 = ax_vibration.get_legend_handles_labels(
    ) if using_vibration and not using_gain else ([], [])

    if legend_prefix:
        bbox_to_anchor = (-0.42, 1)
    else:
        bbox_to_anchor = (-0.17, 1)

    if using_gain:
        ax_legend = ax_gain
    elif using_phase:
        ax_legend = ax_phase
    elif using_THD:
        ax_legend = ax_THD
    elif using_vibration:
        ax_legend = ax_vibration
    else:
        ax_legend = None

    if ax_legend is not None:
        ax_legend.legend(lines + lines3 + lines2 + lines4, labels +
                         labels3 + labels2 + labels4, loc='upper left', bbox_to_anchor=bbox_to_anchor, fontsize='small')
        # 标题写上文件名
        ax_legend.set_title(os.path.basename(file_name))

    fig.set_size_inches(17, 9)
    if legend_prefix:
        plt.subplots_adjust(left=0.27)
    else:
        plt.subplots_adjust(left=0.15)
    fig.savefig(file_name.replace("_analyze.json", "_analyze.png"))
    if keep_fig:
        index += 1

    utils.activate_interactive_annotations()

    if show:
        plt.draw()
        plt.pause(0.001)  # 短暂暂停以更新图像


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Analyze and plot data from a JSON file')
    parser.add_argument('-f', '--file', type=str, help='path to the JSON file')
    parser.add_argument('-p', '--path', type=str,
                        help='path to the folder containing JSON files')
    parser.add_argument('-ps', '--phase_shift_manual', type=str,
                        help='phase shift manual')
    parser.add_argument('-i', '--interactive', action='store_true',
                        help='interactive mode')
    args = parser.parse_args()

    if args.phase_shift_manual:
        phase_shift_manual = float(args.phase_shift_manual)
        print(f"phase_shift_manual: {phase_shift_manual}")
    else:
        phase_shift_manual = None

    if args.path:
        folder_path = args.path
        if not os.path.exists(folder_path):
            print(f"Error: {folder_path} does not exist.")
            exit(1)
        for file_name in os.listdir(folder_path):
            if file_name.endswith("_data.json"):
                file_path = os.path.join(folder_path, file_name)
                # analyzer.analyze_file(file_path, file_path.replace(
                #     "_data.json", "_analyze.json")
                # )
                analyze_plot(file_path.replace("_data.json", "_analyze.json"))
    elif args.file:
        if args.file.endswith("_data.json"):
            analyzer.analyze_file(args.file, args.file.replace(
                "_data.json", "_analyze.json"), phase_shift_manual=phase_shift_manual)
            analyze_file_path = args.file.replace(
                "_data.json", "_analyze.json")
        else:
            analyze_file_path = args.file
        analyze_plot(analyze_file_path)
    elif args.interactive:
        while True:
            file_path = input("Input file path:")
            cmd = None
            if file_path == 'exit' or file_path == 'quit' or file_path == 'q':
                break
            if '@' in file_path:
                file_path, cmd = file_path.split('@')
                cmd_dict = parse_cmd(cmd)
            else:
                cmd_dict = {}

            if file_path.endswith("_data.json"):
                analyzer.analyze_file(file_path, file_path.replace(
                    "_data.json", "_analyze.json"))
                analyze_file_path = file_path.replace(
                    "_data.json", "_analyze.json")
            else:
                analyze_file_path = file_path
            legend_prefix = os.path.basename(
                file_path).replace("_analyze.json", "").replace("output_", "") + '@'
            if 'A' in cmd_dict:
                # amp
                print(f"gain_amp: {cmd_dict['A']}")
                gain_amp = cmd_dict['A']
            else:
                gain_amp = 1.0
            if 'B' in cmd_dict:
                # begin
                print(f"begin: {cmd_dict['B']}")
                start_freq = cmd_dict['B']
            else:
                start_freq = None
            if 'E' in cmd_dict:
                # end
                print(f"end: {cmd_dict['E']}")
                end_freq = cmd_dict['E']
            else:
                end_freq = None
            analyze_plot(analyze_file_path, gain_amp=gain_amp,
                         show=True, legend_prefix=legend_prefix, start_freq=start_freq, end_freq=end_freq)
    else:
        print("Error: either -f or -p must be specified.")
        exit(1)
