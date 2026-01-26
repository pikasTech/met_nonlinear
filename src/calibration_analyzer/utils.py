import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backend_bases import MouseButton, cursors
import os
import re


def activate_interactive_annotations():
    annotations = {}  # Dictionary to keep track of annotations

    def on_click(event):
        if event.inaxes:
            ax = event.inaxes
            # Check if the click is on an annotation
            for annot in list(annotations.values()):
                if annot.figure is not None and annot.contains(event)[0]:
                    annot.set_visible(False)  # Hide the annotation
                    # Find the key for this annotation to delete from dictionary
                    key_to_remove = None
                    for key, val in annotations.items():
                        if val == annot:
                            key_to_remove = key
                            break
                    if key_to_remove:
                        del annotations[key_to_remove]
                    plt.draw()
                    return  # Return early to avoid processing other elements

            # Process click on lines
            for line in ax.get_lines():
                cont, ind = line.contains(event)
                if cont:
                    idx = ind['ind'][0]
                    pos = (line.get_data()[0][idx], line.get_data()[1][idx])

                    # Generate a unique key for each point based on its position
                    key = (ax, line, pos)

                    if key in annotations:
                        # Toggle visibility
                        annot = annotations[key]
                        visible = not annot.get_visible()
                        annot.set_visible(visible)
                        if not visible:
                            del annotations[key]
                    else:
                        # Calculate position and adjust if necessary
                        x_disp, y_disp = 20, 20
                        if pos[0] > ax.get_xlim()[1] - 0.1 * (ax.get_xlim()[1] - ax.get_xlim()[0]):
                            x_disp = -120
                        if pos[1] > ax.get_ylim()[1] - 0.1 * (ax.get_ylim()[1] - ax.get_ylim()[0]):
                            y_disp = -50

                        # Create a new annotation
                        annot = ax.annotate(
                            f"({pos[0]:.2f}, {pos[1]:.2f})",
                            xy=pos, xycoords='data',
                            xytext=(x_disp, y_disp), textcoords='offset points',
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"))
                        annot.set_visible(True)
                        annotations[key] = annot

                    plt.draw()
                    break

    def on_hover(event):
        if event.inaxes:
            ax = event.inaxes
            # Check if hover is on an annotation or a data point
            cursor_set = False
            for annot in annotations.values():
                if annot.figure is not None and annot.contains(event)[0]:
                    ax.figure.canvas.set_cursor(cursors.HAND)
                    cursor_set = True
                    break

            if not cursor_set:
                for line in ax.get_lines():
                    if line.contains(event)[0]:
                        ax.figure.canvas.set_cursor(cursors.HAND)
                        cursor_set = True
                        break

            if not cursor_set:
                ax.figure.canvas.set_cursor(cursors.POINTER)

    for fig_number in plt.get_fignums():
        fig = plt.figure(fig_number)
        for ax in fig.get_axes():
            ax._interactive_annotation_click = fig.canvas.mpl_connect(
                'button_press_event', on_click)
            ax._interactive_annotation_hover = fig.canvas.mpl_connect(
                'motion_notify_event', on_hover)


def create_example_figures():
    x = np.logspace(0.1, 2, 100)
    y = np.random.rand(100) * 100

    fig1, ax1 = plt.subplots()
    ax1.loglog(x, y, marker='o')

    fig2, ax2 = plt.subplots()
    ax2.loglog(x, y**2, marker='o')


if __name__ == "__main__":
    create_example_figures()  # Create example figures
    activate_interactive_annotations()  # Activate annotations for all figures

    plt.show()


def find_analyze_json_files_and_temperatures(directory) -> (list, list):
    """
    在指定目录下查找所有符合 '_analyze.json' 结尾的文件，并提取文件名中的温度值。
    返回的文件名和温度值列表按温度从低到高排序。

    :param directory: 要搜索的目录
    :return: (文件名列表, 温度值列表)
    """
    # 文件名匹配模式：包含 '_analyze.json' 结尾和温度值（如 'T10' 或 'TN10'）
    file_pattern = re.compile(r'(T[N]?[-+]?\d+)_analyze\.json$')

    # 存储找到的文件名和对应的温度值
    file_info = []

    # 遍历目录下的所有文件
    for file in os.listdir(directory):
        match = file_pattern.search(file)
        if match:
            # 提取并转换温度值
            temp_str = match.group(1)
            # 处理温度值（例如 'T10' 转换为 10，'TN10' 转换为 -10）
            temperature = int(temp_str.replace('TN', '-').replace('T', ''))
            file_info.append((file, temperature))

    # 按温度从低到高排序
    file_info.sort(key=lambda x: x[1])

    # 分离文件名和温度值
    filenames, temperatures = zip(*file_info) if file_info else ([], [])

    return filenames, temperatures
