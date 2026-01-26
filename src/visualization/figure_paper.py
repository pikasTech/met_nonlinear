from matplotlib import pyplot as plt
import matplotlib.patheffects as path_effects
import matplotlib.patches as mpatches
from paper.fig_process import plot_frirnn
from paper.fig_process import plot_lut
from paper.fig_process import fig_pdf
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset
import config
from matplotlib.colors import to_rgb, to_hex
from matplotlib.patches import Rectangle
import re
import json
import numpy as np
from PIL import Image
import os
from core.training_log import TrainingLogger
from paper.fig_process.plot_config import *
from paper.fig_process.plot_scatter import plot_nonlinearity_scatter

# plt.style.use(['science', 'ieee'])
RESULT_LIST = [
    'FRIKANh6u6l3',
    'FRIKANh6u6l4',
    'FRIKANh8u6l6',
    'FRIKANh8u6l6nsym',
    'GRNu16', 'LSTMu16', 'GRNu22',
    'LSTMu22',
    'LSTMu22_2',  # 'FRIKANh8u6l6_2',
    'LSTMu22_3',  # 'FRIKANh8u6l6_3',
    'LSTMu22',  # 'FRIKANh8u6l6_4',
    'LSTMu22_5',
    # 'WIENER',
    'RVTDCNN',
    'RVTDCNNu12d7m8',
    'RVTDCNN',
    'RVTDCNN',
    'RVTDCNNu12d7m8d0.2',
    'RVTDCNNu12d7m10n2',
    'RVTDCNNu12d7m10n2relu',
    'RVTDCNNstd',
    # 'WNET2u4*',
    # 'WNET2u6*',
    # 'WNET2u8d0*'
    # 'WNET2*',
    'WNET3*',
    'WNET4*',
    'WNET5*'
    'WNET5q0.5*',
    'WNET5*'
    # '*'
]

IGNORE_LIST = [
    # '*nb',
    # '*u2*'
]

# Set matplotlib to support Chinese fonts using SimHei
# 'SimHei' is a common Chinese sans-serif font

# Set font size
plt.rcParams.update({'font.size': 10})


def get_model_color(model_name):
    """根据模型名称返回对应的颜色"""
    for key, color in MODEL_COLOR_MAP.items():
        if model_name.startswith(key):
            return color
    # return "#000000"  # 默认颜色（黑色）
    return "#4E79A7"  # 默认颜色（蓝色）


def my_arraw(ax, xa=0.4, ya=0.8, xt=0.55, yt=0.85, hw=0.02, hl=0.1, lw=0.003,
             text='Model parameter count \nincreases'):
    # 图中放一个向右的箭头，然后标注向右的参数规模增加
    # 在图中绘制向右的箭头
    ylim = ax.get_ylim()
    xlim = ax.get_xlim()
    dly = ylim[1] - ylim[0]
    dlx = xlim[1] - xlim[0]
    xarrow = xlim[0] + xa * dlx
    yarrow = ylim[0] + ya * dly
    xtext = xlim[0] + xt * dlx
    ytext = ylim[0] + yt * dly
    head_width = hw * dly
    head_length = hl * dlx
    dx = 0.2 * dlx
    ax.arrow(
        x=xarrow, y=yarrow,  # 箭头起始点坐标
        dx=dx, dy=0,            # 箭头的长度（x方向）和高度（y方向）
        head_width=head_width,            # 箭头头部的宽度
        head_length=head_length,         # 箭头头部的长度
        fc='black', ec='black',  # 箭头颜色,
        width=lw * dly,  # 箭头线宽
    )

    # 在箭头旁边添加文字
    ax.text(
        xtext, ytext,                   # 文字的位置
        text,  # 文字内容
        fontsize=12,              # 字体大小
        # 剧中
        ha='center',
    )


def convert_numpy(obj):
    """
    Recursively convert numpy arrays in the object to lists.

    Args:
        obj: The object to convert.

    Returns:
        The converted object with all numpy arrays as lists.
    """
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, list):
        return [convert_numpy(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convert_numpy(v) for k, v in obj.items()}
    else:
        return obj


def get_complementary_color(hex_color):
    """
    获取颜色的反色（补色）。

    Args:
        hex_color (str): 颜色的 HEX 编码 (e.g., "#4E79A7").

    Returns:
        str: 补色的 HEX 编码.
    """
    rgb = to_rgb(hex_color)  # 将 HEX 转换为 RGB (0-1)
    complementary_rgb = [(1.0 - c) for c in rgb]  # 计算反色
    return to_hex(complementary_rgb)  # 转换回 HEX 编码


class ProjectResult:
    """
    A class to handle project data loading, processing, and saving.
    """

    def __init__(self, project_name):
        self.project_name = project_name
        self.project_path = os.path.join(
            'projects', self.project_name, 'data')
        self.raw_data_path = os.path.join(
            self.project_path, 'linear_response.json')
        self.processed_data_path = os.path.join(
            self.project_path, 'processed_data.json')
        self.training_info_path = os.path.join(
            self.project_path, 'training_info.json')
        self.model_info_path = os.path.join(
            self.project_path, 'model_info.json')
        self.raw_data = {}
        self.processed_data = {}
        self.training_info = {}
        self.model_info = {}
        self.use_sensitive = True

        index_first_lower = next(
            (i for i, c in enumerate(project_name) if c.islower()), len(project_name))
        self.model_name = project_name[:index_first_lower]
        self.model_param = project_name[index_first_lower:]

        self.load_data()

    def load_data(self):
        """Load raw data from the JSON file."""
        # print(f'Loading raw data from {self.raw_data_path}...')
        try:
            with open(self.raw_data_path, 'r') as json_file:
                self.raw_data = json.load(json_file)
        except Exception as e:
            print(f'Error loading raw data: {e}')
        try:
            with open(self.training_info_path, 'r') as json_file:
                self.training_info = json.load(json_file)
        except Exception as e:
            print(f'Error loading training info: {e}')

        try:
            with open(self.model_info_path, 'r') as json_file:
                self.model_info = json.load(json_file)
        except Exception as e:
            print(f'Error loading model info: {e}')

    def process_data(self, freq_sen=100):
        """Process raw data and store it in processed_data."""
        # print('Processing data...')
        # Process gains
        self.processed_data['gains_origin'] = [
            np.array(g) for g in self.raw_data['gains_origin']]
        self.processed_data['gains_comped'] = [
            np.array(g) for g in self.raw_data['gains_comped']]
        self.processed_data['magnitudes'] = self.raw_data['magnitudes']
        self.processed_data['frequencies'] = self.raw_data['frequencies']

        use_interp = True
        if use_interp:
            # 补充使用插值计算的灵敏度
            freq = np.array(self.processed_data['frequencies'])
            gains_origin = np.array(self.processed_data['gains_origin'])
            gains_comped = np.array(self.processed_data['gains_comped'])
            sensitive_origin = []
            sensitive_comped = []
            for i in range(len(gains_origin)):
                gain_origin = gains_origin[i]
                gain_comped = gains_comped[i]
                gain_origin_interp = np.interp(
                    freq_sen, freq, gain_origin)
                gain_comped_interp = np.interp(
                    freq_sen, freq, gain_comped)
                sensitive_origin.append(gain_origin_interp)
                sensitive_comped.append(gain_comped_interp)
        else:
            freq = np.array(self.processed_data['frequencies'])
            idx_sen = np.where(freq == freq_sen)
            sensitive_origin = np.array(
                self.processed_data['gains_origin'])[:, idx_sen].flatten()
            sensitive_comped = np.array(
                self.processed_data['gains_comped'])[:, idx_sen].flatten()
        self.processed_data['sensitive_origin'] = sensitive_origin
        self.processed_data['sensitive_comped'] = sensitive_comped

        # Process fit parameters
        paramss_origin = self.raw_data.get('fit_params_origin', [])
        paramss_comped = self.raw_data.get('fit_params_comped', [])

        wn_origin, zeta_origin, A_origin = self._calculate_parameters(
            paramss_origin)
        wn_comped, zeta_comped, A_comped = self._calculate_parameters(
            paramss_comped)

        self.processed_data['fn_origin'] = np.array(wn_origin) / (2 * np.pi)
        self.processed_data['fn_comped'] = np.array(wn_comped) / (2 * np.pi)
        self.processed_data['Sn_origin'] = np.array(
            A_origin) / (4 * np.pi * np.array(zeta_origin) * self.processed_data['fn_origin'])
        self.processed_data['Sn_comped'] = np.array(
            A_comped) / (4 * np.pi * np.array(zeta_comped) * self.processed_data['fn_comped'])
        self.processed_data['zeta_origin'] = zeta_origin
        self.processed_data['zeta_comped'] = zeta_comped
        self.compute_linearity_metrics()

    def _calculate_parameters(self, paramss):
        """Helper method to calculate wn, zeta, and A from fit parameters."""
        wn = []
        zeta = []
        A = []
        for A_val, B_val, C_val in paramss:
            wn_val = np.sqrt(B_val)
            zeta_val = C_val / (2 * wn_val)
            wn.append(wn_val)
            zeta.append(zeta_val)
            A.append(A_val)
        return wn, zeta, A

    def save_processed_data(self):
        """Save the processed data to a JSON file."""
        # print(f'Saving processed data to {self.processed_data_path}...')
        # Recursively convert all numpy arrays to lists
        serializable_data = convert_numpy(self.processed_data)
        with open(self.processed_data_path, 'w') as json_file:
            json.dump(serializable_data, json_file, indent=4)

    def load_processed_data(self):
        """Load processed data from the JSON file."""
        # print(f'Loading processed data from {self.processed_data_path}...')
        with open(self.processed_data_path, 'r') as json_file:
            data = json.load(json_file)

        # Convert lists back to NumPy arrays where appropriate
        processed_data = {}
        for key, value in data.items():
            if key in ['gains_origin', 'gains_comped']:
                # These are lists of lists; convert each sublist to a numpy array
                processed_data[key] = [np.array(sublist) for sublist in value]
            elif isinstance(value, list):
                # Convert flat lists to numpy arrays
                processed_data[key] = np.array(value)
            else:
                processed_data[key] = value
        self.processed_data = processed_data

    def compute_linearity_metrics(self, freq_start_skip=config.FREQ_START_SKIP, freq_end_skip=config.FREQ_END_SKIP):
        processed_data = self.processed_data
        """
        计算每个震级的线性度值及其平均值。

        线性度定义为归一化后线性响应与理想响应（1）的绝对差值的平均值。

        Args:
            processed_data (dict): 处理后的数据字典。

        Returns:
            dict: 包含线性度（补偿前后）的字典。
        """
        gains_origin = processed_data['gains_origin']  # 原始增益，列表中每个元素对应一个震级的频率增益数组
        gains_comped = processed_data['gains_comped']  # 补偿后增益，结构同上
        magnitudes = processed_data['magnitudes']  # 震级列表
        frequencies = processed_data['frequencies']  # 频率列表
        f = np.array(frequencies)

        linearitoutput_origin = []
        linearity_comped = []

        for i in range(freq_start_skip, len(f) - freq_end_skip):
            gain_origin = [gains_origin[k][i]
                           for k in range(len(gains_origin))]
            # sweep_target : 0
            gain_std_origin = gain_origin[0]  # np.mean(gain_origin)
            lineritoutput_origin = [
                gain / gain_std_origin for gain in gain_origin]
            gain_comped = [gains_comped[k][i]
                           for k in range(len(gains_comped))]
            gain_std_comped = gain_comped[0]  # np.mean(gain_comed)
            linerity_comped = [gain / gain_std_comped for gain in gain_comped]
            linearitoutput_origin += lineritoutput_origin
            linearity_comped += linerity_comped

        # 将结果存储到processed_data中
        processed_data['linearitoutput_origin'] = linearitoutput_origin
        processed_data['linearity_comped'] = linearity_comped
        nonlinearitoutput_origin = np.abs(
            [np.log(l) for l in linearitoutput_origin])
        nonlinearity_comped = np.abs([np.log(l) for l in linearity_comped])
        processed_data['nonlinearitoutput_origin'] = nonlinearitoutput_origin
        processed_data['nonlinearity_comped'] = nonlinearity_comped

    def plot_linear_response(self, fig_path, use_compensated=False, subtitle='(d)', figsize=(6, 6)):
        processed_data = self.processed_data
        print(
            f'Plotting linear response to {fig_path}..., use_compensated={use_compensated}')
        # Reconstruct the data
        gains_origin = processed_data['gains_origin']
        gains_comped = processed_data['gains_comped']
        magnitudes = processed_data['magnitudes']
        frequencies = processed_data['frequencies']
        f = np.array(frequencies)

        # Begin plotting
        fig_linear = plt.figure(figsize=figsize)
        color_map = plt.cm.get_cmap("tab20", len(f))  # Use 20 different colors

        # Plot original and compensated responses
        for i in range(0, len(f) - 2):
            color = color_map(i)

            # Original response
            gain_origin = [gains_origin[k][i]
                           for k in range(len(gains_origin))]
            linear = [gain_origin[k] * magnitudes[k]
                      for k in range(len(gains_origin))]
            k_standard = linear[0] / magnitudes[0]
            linear = [l / k_standard for l in linear]
            label = f'Origin @ {f[i]} Hz'
            plt.plot(
                magnitudes, linear,
                label=label, linestyle='', marker='o', markersize=3, color=color
            )

            # Compensated response
            gain_comped = [gains_comped[k][i]
                           for k in range(len(gains_comped))]
            linear_comped = [gain_comped[k] * magnitudes[k]
                             for k in range(len(gains_comped))]
            k_standard_comped = linear_comped[0] / magnitudes[0]
            linear_comped = [l / k_standard_comped for l in linear_comped]
            if use_compensated:
                plt.plot(
                    magnitudes, linear_comped,
                    linestyle='', marker='^', markersize=8, markerfacecolor='none',
                    markeredgewidth=1, color=color, label=f'{self.project_name} @ {f[i]} Hz'
                )

        # Plot ideal linear reference line
        ideal_line, = plt.plot(
            [min(magnitudes), max(magnitudes)],
            [min(magnitudes), max(magnitudes)],
            linestyle='--', color='black', linewidth=2
        )

        # Retrieve handles and labels for the legend
        handles, labels = plt.gca().get_legend_handles_labels()

        # Function to extract frequency from label
        def extract_frequency(label):
            match = re.search(r'@ (\d+(?:\.\d+)?) Hz', label)
            return float(match.group(1)) if match else float('inf')

        # Group and sort legend entries
        origin_handles_labels = sorted(
            [(h, l) for h, l in zip(handles, labels)
             if self.project_name not in l],
            key=lambda x: extract_frequency(x[1])
        )
        compensated_handles_labels = sorted(
            [(h, l) for h, l in zip(handles, labels) if self.project_name in l],
            key=lambda x: extract_frequency(x[1])
        )

        # Initialize legends
        if origin_handles_labels:
            origin_handles, origin_labels = zip(*origin_handles_labels)
            origin_labels = [l.replace('Origin', '') for l in origin_labels]
            main_legend1 = plt.legend(origin_handles, origin_labels, loc='upper left', bbox_to_anchor=(
                0.95 if use_compensated else 1.07, 0.8), ncol=1, title="ORIGIN")
        else:
            main_legend1 = None

        if use_compensated and compensated_handles_labels:
            compensated_handles, compensated_labels = zip(
                *compensated_handles_labels)
            compensated_labels = [l.replace(self.project_name, '')
                                  for l in compensated_labels]
            main_legend2 = plt.legend(compensated_handles, compensated_labels, loc='upper left', bbox_to_anchor=(
                1.28, 0.8), ncol=1, title="Compensated")
        else:
            main_legend2 = None

        # Add a separate legend for the ideal line
        if main_legend1:
            plt.gca().add_artist(main_legend1)
        if main_legend2:
            plt.gca().add_artist(main_legend2)
        plt.legend([ideal_line], ['Ideal Linear Response'], loc='upper left',
                   bbox_to_anchor=(1.07 if use_compensated else 1.0, 0.95), title="Reference")

        # Add labels and title
        plt.xlabel('Magnitude ($\\text{m}/\\text{s}^2$)')
        plt.ylabel('Amplitude (Normalized)')
        plt.grid()
        plt.text(0.5, -0.15, subtitle, transform=plt.gca().transAxes,
                 fontsize=21, ha='center', va='top')
        plt.tight_layout()

        # Save the plot
        plt.savefig(fig_path, dpi=500)
        plt.close(fig_linear)

    def plot_frequency_response_by_magnitude(self, fig_path, use_compensated=False,
                                             freq_range=(10, 128), amp_range=(30, 250), figsize=(8, 6), subtitle='(a)', config=None):
        # 支持配置的频率范围
        if config is not None:
            freq_range = getattr(config, 'dataset', {}).get('freq_range_hz', freq_range)
        
        print(
            f'Plotting frequency response by magnitude to {fig_path}..., use_compensated={use_compensated}')
        # 加载数据
        plot_data = self.processed_data
        gains_origin = [np.array(g) for g in plot_data['gains_origin']]
        gains_comped = [np.array(g) for g in plot_data['gains_comped']]
        magnitudes = plot_data['magnitudes']
        frequencies = plot_data['frequencies']
        f = np.array(frequencies)

        fig_freq = plt.figure(figsize=figsize)
        color_map = plt.cm.get_cmap("tab20", len(magnitudes))

        handles = []
        labels = []

        for k, magnitude in enumerate(magnitudes):
            color = color_map(k)

            # Original response
            gain_origin = [gains_origin[k][i] for i in range(len(f))]
            label_original = f'Original @ {magnitude:.02f} m/s^2'
            handle_origin, = plt.loglog(
                f, gain_origin,
                label=label_original, linestyle='-', marker='',  color=color, linewidth=1.5
            )
            handles.append(handle_origin)
            labels.append(label_original)

            # FRIKAN response
            if use_compensated:
                gain_comped = [gains_comped[k][i] for i in range(len(f))]
                label_compensated = f'FRIKAN @ {magnitude:.02f} m/s^2'
                handle_comp, = plt.loglog(
                    f, gain_comped,
                    linestyle='--', color=color, label=label_compensated, linewidth=1.5
                )
                handles.append(handle_comp)
                labels.append(label_compensated)

        plt.xlim(freq_range)
        plt.ylim(amp_range)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel(
            'Sensitivity ($\\mathrm{V} \\cdot \\mathrm{s} / \\mathrm{m}$)')
        if subtitle:
            plt.text(0.5, -0.15, '(a)', transform=plt.gca().transAxes,
                     fontsize=24, ha='center', va='top')

        def extract_magnitude(label):
            match = re.search(r'@ (\d+(?:\.\d+)?) m/s^2', label)
            return float(match.group(1)) if match else float('inf')

        # Dual-column legend for compensated plot
        if use_compensated:
            origin_handle_labels = sorted(
                [(h, l) for h, l in zip(handles, labels) if 'FRIKAN' not in l],
                key=lambda x: extract_magnitude(x[1])
            )
            compensated_handle_labels = sorted(
                [(h, l) for h, l in zip(handles, labels) if 'FRIKAN' in l],
                key=lambda x: extract_magnitude(x[1])
            )
            origin_handles, origin_labels = zip(*origin_handle_labels)
            origin_labels = [l.replace('Original', '').replace(
                'm/s^2', '$\\text{m}/\\text{s}^2$') for l in origin_labels]
            compensated_handles, compensated_labels = zip(
                *compensated_handle_labels)
            compensated_labels = [l.replace('FRIKAN', '').replace('m/s^2', '$\\text{m}/\\text{s}^2$')
                                  for l in compensated_labels]
            legend1 = plt.legend(origin_handles, origin_labels, loc='upper left',
                                 bbox_to_anchor=(1.0, 1.0), ncol=1, title="ORIGIN")
            plt.gca().add_artist(legend1)
            legend2 = plt.legend(compensated_handles, compensated_labels, loc='upper left',
                                 bbox_to_anchor=(1.26, 1.0), ncol=1, title="Compensated")
        else:
            labels = [l.replace('Original', '').replace(
                'm/s^2', '$\\text{m}/\\text{s}^2$') for l in labels]
            plt.legend(handles, labels, loc='upper left',
                       bbox_to_anchor=(1.0, 1.0), ncol=1, title="Response")

        plt.grid(True, which="both", ls="--")
        plt.tight_layout()
        plt.savefig(fig_path, dpi=500)
        plt.close(fig_freq)

    def plot_params_by_magnitude(self, fig_path, use_compensated=False, figsize=(4, 6)):
        processed_data = self.processed_data
        print(
            f'Plotting parameters by magnitude to {fig_path}..., use_compensated={use_compensated}')
        # Reconstruct the data
        magnitudes = processed_data['magnitudes']
        fn_origin = processed_data['fn_origin']
        fn_comped = processed_data.get('fn_comped', [])
        if self.use_sensitive:
            Sn_origin = processed_data['sensitive_origin']
            Sn_comped = processed_data.get('sensitive_comped', [])
        else:
            Sn_origin = processed_data['Sn_origin']
            Sn_comped = processed_data.get('Sn_comped', [])

        # Plot
        fig_params, axes = plt.subplots(2, 1, figsize=figsize)
        markersize = 4

        # Plot S_n
        axes[0].plot(magnitudes, Sn_origin, label='Sensitivity@100Hz (Origin)',
                     marker='o', markersize=markersize)
        if use_compensated and Sn_comped.size > 0:
            axes[0].plot(magnitudes, Sn_comped,
                         label='Sensitivity@100Hz (Comped)', marker='^', markersize=markersize)
        axes[0].legend()
        axes[0].set_xlabel('Magnitude ($\\text{m}/\\text{s}^2$)')
        axes[0].set_ylabel(
            'Sensitivity ($\\mathrm{V} \\cdot \\mathrm{s} / \\mathrm{m}$)')
        axes[0].grid()
        axes[0].text(0.5, -0.25, '(b)', transform=axes[0].transAxes,
                     fontsize=21, ha='center', va='top')

        # Plot f_n
        axes[1].plot(magnitudes, fn_origin,
                     label='Natural Frequency $\eta$ (Origin)', marker='o', markersize=markersize)
        if use_compensated and fn_comped.size > 0:
            axes[1].plot(magnitudes, fn_comped,
                         label='Natural Frequency $\eta$ (Comped)', marker='^', markersize=markersize)
        axes[1].legend()
        axes[1].set_xlabel('Magnitude ($\\text{m}/\\text{s}^2$)')
        axes[1].set_ylabel('Frequency $\eta$(Hz)')
        axes[1].grid()
        axes[1].text(0.5, -0.25, '(c)', transform=axes[1].transAxes,
                     fontsize=21, ha='center', va='top')

        plt.tight_layout()
        plt.savefig(fig_path, dpi=500)
        plt.close(fig_params)

    def plot_comparison_boxplots(self, fig_path, other_project_result=[]):
        """
        绘制 S_n 和 f_n 的箱线图，以及线性度柱状图，不显示异常值，并使用所有数据计算上下限。
        使用combine_images_with_labels将两个图表拼接。

        Args:
            fig_path (str): 保存图像的路径。
            other_project_result (list): 其他项目的结果对象列表，每个对象应有 .processed_data 和 .model_name 属性。
        """
        # 创建 image_data 目录
        os.makedirs('paper/image_data', exist_ok=True)

        # 创建临时图像目录
        temp_dir = os.path.join(os.path.dirname(fig_path), 'temp')
        os.makedirs(temp_dir, exist_ok=True)

        # 生成临时文件路径
        sensitivity_path = os.path.join(
            temp_dir, 'sensitivity_boxplot_temp.png')
        frequency_path = os.path.join(temp_dir, 'frequency_boxplot_temp.png')

        # 当前项目的处理数据
        processed_data = self.processed_data
        if self.use_sensitive:
            Sn_origin = processed_data['sensitive_origin']
        else:
            Sn_origin = processed_data.get('Sn_origin', [])
        fn_origin = processed_data.get('fn_origin', [])

        # 初始化数据和标签
        data_Sn = [Sn_origin]
        data_fn = [fn_origin]

        model_names = ['ORIGIN']
        model_params = ['']

        # 对其他项目（others）：只添加补偿后的数据与其项目名
        for result in other_project_result:
            other_data = result.processed_data
            other_Sn_comped = other_data.get('Sn_comped', [])
            other_fn_comped = other_data.get('fn_comped', [])

            # 将补偿后的数据添加至数据列表
            data_Sn.append(other_Sn_comped)
            data_fn.append(other_fn_comped)

            # 使用 model_name 作为标签
            model_names.append(result.model_name)
            model_params.append(result.model_param)

        labels = [model_name + model_param for model_name,
                  model_param in zip(model_names, model_params)]

        # 绘制敏感度箱线图
        fig_sn, ax_sn = plt.subplots(figsize=(14, 10))
        box_sn = ax_sn.boxplot(
            data_Sn, labels=labels, showfliers=False, whis=[0, 100], patch_artist=True
        )

        # labels 竖直显示
        ax_sn.set_xticklabels(labels, rotation=30, ha='right')
        for patch, model_name in zip(box_sn['boxes'], model_names):
            clr = MODEL_COLOR_MAP.get(model_name, "gray")
            patch.set_facecolor(clr)  # 设置颜色

        # 取消横轴刻度
        ax_sn.xaxis.set_ticks_position('none')
        # 设置线的颜色
        for whisker in box_sn['whiskers']:
            whisker.set_linewidth(0.5)

        # 隐藏中位数线
        for median in box_sn['medians']:
            median.set_linewidth(0)  # 隐藏中位数线

        # 设置边框颜色
        for box in box_sn['boxes']:
            box.set_linewidth(0)

        ax_sn.set_ylabel(
            'Sensitivity($\\mathrm{V} \\cdot \\mathrm{s} / \\mathrm{m}$)')
        my_arraw(ax_sn)

        plt.tight_layout()
        plt.savefig(sensitivity_path, dpi=500)
        plt.close(fig_sn)

        # 绘制频率箱线图
        fig_fn, ax_fn = plt.subplots(figsize=(3.5, 4))
        box_fn = ax_fn.boxplot(
            data_fn, labels=labels, showfliers=False, whis=[0, 100], patch_artist=True
        )

        # labels 竖直显示
        ax_fn.set_xticklabels(labels, rotation=30, ha='right')
        for patch, model_name in zip(box_fn['boxes'], model_names):
            clr = MODEL_COLOR_MAP.get(model_name, "gray")
            patch.set_facecolor(clr)  # 设置颜色

        # 取消横轴刻度
        ax_fn.xaxis.set_ticks_position('none')
        # 设置线的颜色
        for whisker in box_fn['whiskers']:
            whisker.set_linewidth(0.5)

        # 隐藏中位数线
        for median in box_fn['medians']:
            median.set_linewidth(0)  # 隐藏中位数线

        # 设置边框颜色
        for box in box_fn['boxes']:
            box.set_linewidth(0)

        ax_fn.set_ylabel('Frequency (Hz)')
        my_arraw(ax_fn)

        plt.tight_layout()
        plt.savefig(frequency_path, dpi=500)
        plt.close(fig_fn)

        # 使用combine_images_with_labels拼接两个图像
        combine_images_with_labels(
            [sensitivity_path, frequency_path],
            fig_path,
        )

        print(f'Box plot saved to {fig_path}')

        # 准备要导出的数据
        export_data = {}

        # 对每个模型添加敏感度和自然频率数据
        for name, param, s_data, f_data in zip(model_names, model_params, data_Sn, data_fn):
            model_key = name + param
            export_data[model_key] = {
                "sensitivity": {
                    "median": float(np.median(s_data)),
                    "q1": float(np.percentile(s_data, 25)),
                    "q3": float(np.percentile(s_data, 75)),
                    "min": float(np.min(s_data)),
                    "max": float(np.max(s_data))
                },
                "natural_frequency": {
                    "median": float(np.median(f_data)),
                    "q1": float(np.percentile(f_data, 25)),
                    "q3": float(np.percentile(f_data, 75)),
                    "min": float(np.min(f_data)),
                    "max": float(np.max(f_data))
                }
            }

        # 将数据保存为 JSON 文件
        json_path = os.path.join('paper/image_data', 'boxplot_data.json')
        with open(json_path, 'w') as f:
            json.dump(export_data, f, indent=4)


def main():
    project_name = 'WNET5q0.5h6u8l8'
    USE_SORT = True
    project_result = ProjectResult(project_name)

    # Process and save data
    project_result.process_data()
    project_result.save_processed_data()
    # Load processed data for plotting
    project_result.load_processed_data()

    # Define image directory
    image_dir = 'paper/image'
    os.makedirs(image_dir, exist_ok=True)

    # Plot linear responses
    project_result.plot_linear_response(
        os.path.join(image_dir, '2.Dynamic_linear_response.png'),
        use_compensated=False,
        subtitle='(b)',
        figsize=(5, 6)
    )
    project_result.plot_linear_response(
        os.path.join(
            image_dir, '18.Dynamic_linear_response_and_compensated.png'),
        use_compensated=True
    )

    # Plot frequency responses by magnitude
    project_result.plot_frequency_response_by_magnitude(
        os.path.join(image_dir, '3.MET_nonlinear_frequency_response.png'),
        use_compensated=False,
        figsize=(8, 6.5),
        subtitle=None
    )
    project_result.plot_frequency_response_by_magnitude(
        os.path.join(
            image_dir, '19.MET_nonlinear_frequency_response_and_compensated.png'),
        use_compensated=True,
        figsize=(9, 7)
    )

    # Plot parameters by magnitude
    project_result.plot_params_by_magnitude(
        os.path.join(image_dir, '20.MET_nonlinear_parameters.png'),
        use_compensated=False
    )
    project_result.plot_params_by_magnitude(
        os.path.join(
            image_dir, '21.MET_nonlinear_parameters_and_compensated.png'),
        use_compensated=True
    )

    # other_project_names = ['FRIKANh2u8', 'FRIKANh2u12', 'FRIKANh2u24', 'FRIKANh4u8', 'FRIKANh4u12',
    #                         'FRIKANh4u24', 'GRNu8', 'GRNu16', 'GRNu32', 'GRNu64', 'LSTMu8', 'LSTMu16', 'LSTMu32', 'LSTMu64']

    # other_project_names = ['FRIKANh2u24', 'GRNu64', 'LSTMu64']
    other_project_names = expand_project_patterns()
    # other_project_names = [
    #     f.name for f in os.scandir('projects') if f.is_dir()]

    other_project_results = [ProjectResult(
        name) for name in other_project_names]

    other_project_results_success = []
    for other_project_result in other_project_results:
        try:
            other_project_result.process_data()
            other_project_result.save_processed_data()
            other_project_result.load_processed_data()
            other_project_result.model_info[PARAM_COUNT]
            other_project_results_success.append(other_project_result)
        except Exception as e:
            print(f'Error processing {other_project_result.project_name}: {e}')

    total_params_models = [result.model_info[PARAM_COUNT]
                           for result in other_project_results_success]

    if USE_SORT:
        index_sort_by_params = np.argsort(total_params_models)
        other_project_results_success = [
            other_project_results_success[i] for i in index_sort_by_params]

    other_project_results_success = [
        result for result in other_project_results_success if result.model_info[PARAM_COUNT] > 0]

    # Plot box plots
    project_result.plot_comparison_boxplots(
        os.path.join(
            image_dir,
            '24.Boxplots_linearity_Sn_fn.png',
        ),
        other_project_result=other_project_results_success
    )

    # 绘制非线性度值图表
    plot_nonlinearity_scatter(
        project_result,
        os.path.join(
            image_dir,
            '26.Nonlinearity_bar.png',
        ),
        other_project_result=other_project_results_success,
        metric_type='nonlinearity',
        plot_suppress_rate=False,
        subtitle='(a)'
    )

    # 绘制非线性误差抑制率图表
    plot_nonlinearity_scatter(
        project_result,
        os.path.join(
            image_dir,
            '40.Nonlinearity_suppression.png',
        ),
        other_project_result=other_project_results_success,
        metric_type='nonlinearity',
        plot_suppress_rate=True,
        subtitle='(b)'
    )

    # 绘制灵敏度漂移抑制率图表
    plot_nonlinearity_scatter(
        project_result,
        os.path.join(
            image_dir,
            '41.Sensitivity_suppression.png',
        ),
        other_project_result=other_project_results_success,
        metric_type='sensitivity',
        plot_suppress_rate=True,
        subtitle='(c)'
    )

    # 绘制自然频率漂移抑制率图表
    plot_nonlinearity_scatter(
        project_result,
        os.path.join(
            image_dir,
            '42.Frequency_suppression.png',
        ),
        other_project_result=other_project_results_success,
        metric_type='natural_frequency',
        plot_suppress_rate=True,
        subtitle='(d)'
    )

    plot_nonlinearity_scatter(
        project_result,
        os.path.join(
            image_dir,
            '43.Average_suppression.png',  # 新文件名
        ),
        other_project_result=other_project_results_success,
        metric_type='average_suppression',  # 指定使用平均抑制率
        subtitle='(e)'  # 可根据需要设置子标题
    )

    # 返回处理成功的项目
    return other_project_results_success


def analyze_params_total():
    other_project_names = [
        f.name for f in os.scandir('projects') if f.is_dir()]
    other_project_results = [ProjectResult(
        name) for name in other_project_names]

    # 绘制模型参数数量柱状图
    fig, ax = plt.subplots(figsize=(5, 16))
    result_names = []
    result_total_params = []

    for result in other_project_results:
        try:
            result_total_params.append(result.model_info[PARAM_COUNT])
            result_names.append(result.project_name)
        except Exception as e:
            print(f'Error processing {result.project_name}: {e}')

    # 排序处理
    index_sort_by_params = np.argsort(result_total_params)
    result_total_params = [result_total_params[i]
                           for i in index_sort_by_params]
    result_names = [result_names[i] for i in index_sort_by_params]

    # 绘制条形图并保存对象
    bars = ax.barh(result_names, result_total_params)

    # 添加数值标签（带描边效果）
    if result_total_params:  # 确保有数据时执行
        max_value = max(result_total_params)
        x_offset = max_value * 0.02  # 动态偏移量

        for bar in bars:
            width = bar.get_width()
            y_pos = bar.get_y() + bar.get_height()/2  # 垂直居中
            # 添加带千位分隔符的文本
            ax.text(width + x_offset, y_pos,
                    f"{width:,}",  # 格式化数值显示
                    va='center', ha='left',
                    color='black',
                    path_effects=[
                        path_effects.withStroke(
                            linewidth=2, foreground='white'),
                        path_effects.Normal()
                    ])

        # 调整X轴范围确保标签可见
        ax.set_xlim(right=max_value * 1.15)  # 右侧留出15%空间

    ax.set_xlabel('Total Parameters')
    ax.set_ylabel('Model')
    ax.set_title('Total Parameters of Different Models')
    plt.tight_layout()

    print('Saving total params bar plot...')
    plt.savefig('image/25.Total_Params.png', dpi=500)


def training_log_plot(project_names):
    # 假设这里已经载入数据和处理（与原代码一致）
    project_results = [ProjectResult(project) for project in project_names]
    valid_project_results = []
    for project_result in project_results:
        project_result.load_data()
        project_result.process_data()
        project_result.save_processed_data()
        project_result.load_processed_data()
        valid_project_results.append(project_result)

    training_logs = []
    valid_project_names = []
    for i, project_result in enumerate(valid_project_results):
        logger = TrainingLogger(project_result.project_path)
        log_data = logger.load()

        # 检查log_data是否包含'epoch'键
        if 'epoch' in log_data and len(log_data['epoch']) > 0:
            training_logs.append(log_data)
            valid_project_names.append(project_names[i])
        else:
            print(
                f"警告: 跳过项目 {project_result.project_name}, 因为训练日志中没有'epoch'数据")

    # 确保有有效数据
    if not training_logs:
        print("错误: 没有有效的训练日志数据")
        return

    epoch = min([len(training_log['epoch']) for training_log in training_logs])
    epochs = np.arange(1, epoch + 1)
    lr = [training_log['lr'] for training_log in training_logs][0][:epoch]

    fig, ax = plt.subplots(figsize=(8, 6))

    # 绘制训练曲线
    if 0:
        for i, project_name in enumerate(valid_project_names):
            base_color = get_model_color(project_name)
            ax.semilogy(
                epochs,
                training_logs[i]['loss'],
                label=f'{project_name} (training)',
                linestyle='-',  # 实线
                color=base_color,
                marker='',
                linewidth=0.8,
                alpha=1.0
            )

            # 添加训练loss的最低值横线
            min_loss = np.min(training_logs[i]['loss'])
            ax.axhline(
                y=min_loss,
                color=base_color,
                linestyle='--',
                linewidth=0.8,
                alpha=1.0,
                label=f'{project_name} Min Loss'
            )

    # 绘制验证曲线
    for i, project_name in enumerate(valid_project_names):
        base_color = get_model_color(project_name)
        ax.semilogy(
            epochs,
            training_logs[i]['val_loss'][:epoch],
            label=f'{project_name}',
            linestyle='-',  # 虚线
            color=base_color,
            marker='',
            linewidth=0.8,
            alpha=1.0
        )

        # 添加验证loss的最低值横线
        min_val_loss = np.min(training_logs[i]['val_loss'][:epoch])
        min_epoch = epochs[np.argmin(
            training_logs[i]['val_loss'][:epoch])]  # 找到最低值对应的epoch
        x_start = min_epoch / epochs[-1]  # 横线起点（比例）
        ax.axhline(
            y=min_val_loss,
            color=base_color,
            linestyle='--',
            linewidth=0.8,
            alpha=1.0,
        )

        # 在Y轴旁标注最低值
        ax.annotate(
            f'Best@{project_name}',
            xy=(epoch, min_val_loss),   # 在y=min_val_loss处标注
            xytext=(5, 0),        # 偏移量（调整标注位置）
            textcoords='offset points',
            color=base_color,
            fontsize=9,
            ha='left',  # 水平右对齐
            va='center',  # 垂直居中
        )

    # 其余代码保持不变
    # 手动标注 loss 的y轴格点，带文字显示
    ax.set_ylim(None, 15)
    ax.set_yticks([0.5, 0.2, 0.1, 0.05, 0.04, 0.03, 0.02, 0.015, 0.01])
    yticklabels = [str(tick) for tick in ax.get_yticks()]
    ax.set_yticklabels(yticklabels)
    # 绘制学习率
    ax2 = ax.twinx()
    ax2.plot(epochs, lr, label='Learning Rate',
             linestyle='-', color='blue', linewidth=0.5, alpha=0.5)
    ax2.legend(loc='upper right')
    ax2.text(
        0.75, 0.58,
        "Learning Rate:\n"
        "Cosine Annealing + Exponential Decay + Restarts\n"
        "High LR: Helps escape local minima\n"
        "Low LR: Fine-grained convergence\n"
        "Restart: Avoids early convergence",
        transform=ax2.transAxes,
        fontsize=9,
        ha='center', va='top',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.7)
    )

    # 只显示大于 0 的 Y 轴刻度
    yticks = ax2.get_yticks()  # 获取自动生成的刻度
    positive_yticks = [tick for tick in yticks if tick >= 0]  # 筛选大于 0 的刻度
    ax2.set_yticks(positive_yticks)  # 设置筛选后的刻度
    ax2.set_ylim(-0.004, 0.0025)

    # 标记学习率的restart点（局部最大值）
    lr_array = np.array(lr)
    # 寻找局部峰值：当二阶差分由正变负时即可能存在峰值点
    peak_indices = range(20, len(lr_array) - 1, 5000)
    text_x = epochs[-1] * 0.5
    text_y = lr_array.max() * 1.2

    ax2.text(text_x, text_y,
             "LR Restart Points",
             fontsize=9,
             ha='center', va='top',
             bbox=dict(boxstyle='square', facecolor='white',
                       alpha=1, edgecolor='white'),
             zorder=5
             )

    # 为多个峰值点绘制箭头指向上面text位置
    for idx in peak_indices:
        peak_x = epochs[idx]
        peak_y = lr_array[idx]
        # 使用空文本的 annotate 来画箭头，箭头从 text_x,text_y 指向 peak_x,peak_y
        ax2.annotate(
            '',  # 无文本，只画箭头
            xy=(peak_x, peak_y),
            xytext=(text_x, text_y),
            arrowprops=dict(facecolor='black', arrowstyle='->', linewidth=0.8),
            fontsize=8,
            ha='center'
        )

    zoom_start = 5000 + 3500
    zoom_end = zoom_start + 200  # 您可以根据自己的数据范围调整
    zoom_lr = lr_array[(epochs >= zoom_start) & (epochs <= zoom_end)]
    zoom_epochs = epochs[(epochs >= zoom_start) & (epochs <= zoom_end)]
    # 在 ax2 上创建子图
    inset_ax = inset_axes(ax2, width="25%", height="25%", loc='center left',
                          borderpad=2, bbox_to_anchor=(0.33, 0.27, 0.5, 0.5), bbox_transform=ax2.transAxes)

    inset_ax.plot(zoom_epochs, zoom_lr, color='blue', linewidth=1.0, alpha=0.5)
    # inset_ax.set_title('Zoomed LR Detail', fontsize=8)
    inset_ax.tick_params(axis='both', which='major', labelsize=7)
    inset_ax.set_xlim(zoom_start, zoom_end)
    # 根据放大部分LR的范围手动调整y轴范围，以便展示波动细节
    inset_ax.set_ylim(np.min(zoom_lr)*0.9, np.max(zoom_lr)*1.1)

    # 在主图上用矩形框出放大区域
    ax2.set_xlim(epochs.min(), epochs.max())  # 确保主图完整范围
    ax2.set_ylim(-0.004, 0.0025)

    # 使用 mark_inset 连接子图与主图放大区域
    mark_inset(ax2, inset_ax, loc1=2, loc2=3,
               fc="none", ec="0.0", linewidth=0.5)

    ax.set_xlabel('Epoch')
    ax.set_ylabel('Validation Loss (Log Scale)')
    # ax.set_title('Validation Loss and Learning Rate')
    ax.legend(loc='center right', bbox_to_anchor=(1.0, 0.38))
    ax.grid()
    # fig.text(0.5, -0.10, '(b)', transform=ax.transAxes, fontsize=16,
    #  ha='center', va='top')
    plt.tight_layout()
    plt.savefig('image/27.Training_Loss.png', dpi=500)
    plt.close(fig)


def loss_and_val_bar(project_results):
    total_params_models = [result.model_info[PARAM_COUNT]
                           for result in project_results]

    index_sort_by_params = np.argsort(total_params_models)
    project_results = [
        project_results[i] for i in index_sort_by_params]

    training_infos = [
        project_result.training_info for project_result in project_results]

    min_losses = [info['min_loss'] for info in training_infos]
    min_val_losses = [info['min_val_loss'] for info in training_infos]
    names = [result.project_name for result in project_results]

    # 设置柱宽度和位置
    width = 0.7  # 柱状图的宽度
    x = np.arange(len(names))  # 横坐标位置

    # 创建一个图形和轴
    fig, ax = plt.subplots(figsize=(9, 12))

    # 绘制loss和val_loss的重叠柱状图，并分别为每个项目添加图例
    loss_colors = [get_model_color(name) for name in names]
    for i, (loss, val_loss, color, name) in enumerate(zip(min_losses, min_val_losses, loss_colors, names)):
        # Draw training loss bar
        loss_bar = ax.bar(x[i], loss, width-0.2,
                          label=f'Loss ({name})', color=color, alpha=0.7, hatch='///', edgecolor='black', linewidth=1)

        # Draw validation loss bar
        val_loss_bar = ax.bar(x[i], val_loss, width,
                              label=f' Val Loss({name})', color=color, alpha=0.6, edgecolor='black', linewidth=1)

        # Add text labels for training loss bar
        def format_scientific(value, precision=2):
            # Format to scientific notation with 2 decimal places
            sci_str = f"{value:.{precision}e}"
            base, exponent = sci_str.split('e')
            # Format as 1.23\nx10^-3
            return f"{float(base):.{precision}f}$\\rm{{e}}^{{{int(exponent)}}}$"

        # Add label for training loss with stroke effect
        ax.text(x[i], loss + 0.00002, format_scientific(loss),
                ha='center', va='bottom', fontsize=8, color='black',
                path_effects=[path_effects.withStroke(linewidth=3, foreground='white')])

        # Position validation loss label higher to avoid overlap
        ax.text(x[i], val_loss + 0.00008, format_scientific(val_loss),
                ha='center', va='bottom', fontsize=8, color='black',
                path_effects=[path_effects.withStroke(linewidth=3, foreground='white')])

    # 取消横轴刻度
    ax.xaxis.set_ticks_position('none')
    # 设置标签和标题
    ax.set_ylabel('Training and Validation Loss (log scale)')
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=30, ha="right")  # 设置项目名称为横坐标，并旋转45度以便显示

    # 自定义图例颜色
    loss_colors = [get_model_color(name) for name in names]
    val_loss_colors = [get_model_color(name) for name in names]
    # 颜色去重
    loss_colors = list(set(loss_colors))
    val_loss_colors = list(set(val_loss_colors))

    # 创建自定义图例
    legend_elements = []

    # 第一行：Loss 的图例
    for color in loss_colors:
        legend_elements.append(
            Rectangle((0, 0), 1, 1, facecolor=color, alpha=0.7, hatch='///',
                      edgecolor='black', linewidth=1)  # 使用斜线填充样式
        )

    # 第二行：Val Loss 的图例
    for color in val_loss_colors:
        legend_elements.append(
            Rectangle((0, 0), 1, 1, facecolor=color, alpha=0.6,
                      edgecolor='black', linewidth=1)  # 纯色填充
        )

    # 按照 Loss, Val Loss, Loss, Val Loss 的顺序排列
    new_handles = []
    for loss_elem, val_loss_elem in zip(legend_elements[:len(loss_colors)], legend_elements[len(loss_colors):]):
        new_handles.append(val_loss_elem)
        new_handles.append(loss_elem)

    # 创建图例分为两行
    labels = [""] * len(new_handles)  # 创建空标签
    labels[-1] = "Best Training Loss"  # 倒数第二个标签为 Training Loss
    labels[-2] = "Best Validation Loss"  # 最后一个标签为 Validation Loss
    ax.legend(
        handles=new_handles,
        labels=labels,
        loc="upper right",  # 图例位置
        # bbox_to_anchor=(0.5,```python
        # bbox_to_anchor=(0.5, -0.1),  # 调整图例位置
        ncol=len(loss_colors),  # 每行的图例数量与模型数量相同
        columnspacing=0.0,
        handletextpad=1.0,
        title=None,  # 不需要标题
    )

    # 设置y轴对数坐标
    ax.set_yscale('log')

    # 调整y轴lim
    y_lim = ax.get_ylim()
    ax.set_ylim(y_lim[0], y_lim[1] * 1.5)

    ax.set_yticks([0.06, 0.05, 0.04, 0.03, 0.02, 0.015, 0.01])
    yticklabels = [str(tick) for tick in ax.get_yticks()]
    ax.set_yticklabels(yticklabels)

    my_arraw(ax, xa=0.5, ya=0.65, xt=0.55, yt=0.69,
             text='Model parameter count increases')

    # fig.text(0.5, -0.15, '(a)', transform=ax.transAxes,
    #          fontsize=16, ha='center', va='top')

    # 显示柱状图
    plt.tight_layout()
    plt.savefig('image/30.Loss_and_Val_Loss.png', dpi=500)


def concatenate_images(img1_path, img2_path, output_path, space=0.1):
    """
    Concatenate two images horizontally with height alignment.

    Args:
        img1_path (str): Path to the first image.
        img2_path (str): Path to the second image.
        output_path (str): Path to save the concatenated image.
    """
    # Open the images
    img1 = Image.open(img1_path)
    img2 = Image.open(img2_path)

    # Ensure the heights are the same by resizing img2 to match img1's height
    if img1.height != img2.height:
        img2 = img2.resize(
            (int(img2.width * (img1.height / img2.height)), img1.height))

    # Create a new image with combined width and maximum height
    combined_width = int(img1.width*(1+space)) + img2.width
    combined_height = max(img1.height, img2.height)
    combined_image = Image.new("RGB", (combined_width, combined_height))
    # fill with white
    combined_image.paste(
        (255, 255, 255), (0, 0, combined_width, combined_height))

    # Paste the images side by side
    combined_image.paste(img1, (0, 0))
    combined_image.paste(img2, (img1.width + int(img1.width*space), 0))

    # Save the result
    combined_image.save(output_path, dpi=(500, 500))
    print(f"Concatenated image saved to {output_path}")


def combine_images_with_labels(
        image_paths,
        output_path,
        space=0.05,
        label_width_ratio=0.05,
        labels=None,
        font_path=None,
        font_color="black"
):
    """
    将多个图像水平拼接并在底部添加标签(a), (b), (c)...

    参数:
        image```python
        image_paths (list): 要拼接的图像文件路径列表
        output_path (str): 拼接后图像的保存路径
        space (float): 图像之间的间距比例（相对于平均图像宽度）
        labels (list, optional): 自定义标签列表，默认为(a), (b), (c)...
        font_path (str, optional): 字体文件路径，如果为None则尝试使用arial或默认字体
        font_color (str): 标签文字颜色
    """
    from PIL import Image, ImageDraw, ImageFont
    import os

    # 1. 打开所有图像
    images = [Image.open(path) for path in image_paths]

    # 2. 计算调整后的高度（确保所有图像高度相同）
    max_height = max(img.height for img in images)
    resized_images = []
    for img in images:
        if img.height != max_height:
            new_width = int(img.width * (max_height / img.height))
            resized_images.append(img.resize((new_width, max_height)))
        else:
            resized_images.append(img)

    # 3. 计算总宽度（包括间隔）
    widths = [img.width for img in resized_images]
    avg_width = sum(widths) / len(widths)
    space_width = int(avg_width * space)
    total_width = sum(widths) + space_width * (len(widths) - 1)

    # 4. 计算标签区域高度
    label_height = int(total_width * label_width_ratio)

    # 5. 创建新图像（包括底部标签区域）
    combined_height = max_height + label_height
    combined_image = Image.new(
        "RGB", (total_width, combined_height), (255, 255, 255))

    # 6. 粘贴图像
    x_offset = 0
    for img in resized_images:
        combined_image.paste(img, (x_offset, 0))
        x_offset += img.width + space_width

    # 7. 创建绘图对象
    draw = ImageDraw.Draw(combined_image)

    # 8. 加载字体，字体大小根据图像高度自动调整
    font_size = int(label_height * 0.7)  # 字体大小为标签区域高度的70%
    try:
        if font_path:
            font = ImageFont.truetype(font_path, font_size)
        else:
            # # 尝试加载常见字体
            # try:
            # font = ImageFont.truetype("arial.ttf", font_size)
            # except:
            #     try:
            #         font = ImageFont.truetype("Arial.ttf", font_size)
            #     except:
            #         font = ImageFont.load_default()
            # font = ImageFont.load_default(size=font_size)
            # 加载 times new roman 字体
            font = ImageFont.truetype("times.ttf", font_size)
    except:
        print("无法加载指定字体，使用默认字体")
        font = ImageFont.load_default()

    # 9. 为每个子图添加标签
    if labels is None:
        # 默认标签 (a), (b), (c)...
        labels = [f"({chr(97 + i)})" for i in range(len(resized_images))]

    x_offset = 0
    for i, img in enumerate(resized_images):
        # 计算标签位置（在子图中心下方）
        label_x = x_offset + img.width // 2
        label_y = max_height + label_height // 2

        # 绘制标签
        draw.text((label_x, label_y),
                  labels[i], fill=font_color, font=font, anchor="mm")
        x_offset += img.width + space_width

    # 10. 保存拼接后的图像
    combined_image.save(output_path, dpi=(500, 500))
    print(f"带标签的拼接图像已保存至 {output_path}")

    return combined_image


def expand_project_patterns():
    """
    展开项目名称列表中的通配符模式，替换为实际匹配的项目名称，
    并过滤掉在 IGNORE_LIST 中匹配的项目

    Returns:
        list: 展开后的项目名称列表，不包含通配符和被忽略的项目
    """
    expanded_list = []
    # 获取所有实际项目文件夹
    all_projects = [f.name for f in os.scandir('projects') if f.is_dir()]
    patterns = RESULT_LIST
    ignore_patterns = IGNORE_LIST

    # 展开 RESULT_LIST 中的通配符
    for pattern in patterns:
        if '*' in pattern:
            # 将通配符转换为正则表达式
            regex_pattern = pattern.replace('*', '.*')
            matches = [proj for proj in all_projects if re.match(
                regex_pattern, proj)]
            expanded_list.extend(matches)
        else:
            expanded_list.append(pattern)

    # 过滤掉 IGNORE_LIST 中匹配的项目
    filtered_list = []
    for project in expanded_list:
        should_ignore = False
        for ignore_pattern in ignore_patterns:
            # 将通配符转换为正则表达式
            regex_pattern = ignore_pattern.replace('*', '.*')
            if re.match(regex_pattern, project):
                should_ignore = True
                break
        if not should_ignore:
            filtered_list.append(project)

    # 去重
    filtered_list = list(set(filtered_list))

    return filtered_list


if __name__ == '__main__':
    plot_lut.main()
    project_results_success = main()
    analyze_params_total()
    # training_log_plot(['FRIKANh8u6l6', 'LSTMu22'])
    loss_and_val_bar(project_results_success)

    # Concatenate images
    image_dir = 'paper/image'
    concatenate_images(
        os.path.join(image_dir, '20.MET_nonlinear_parameters.png'),
        os.path.join(image_dir, '3.MET_nonlinear_frequency_response.png'),
        os.path.join(image_dir, '22.Combined_3_and_20.png')
    )
    concatenate_images(
        os.path.join(
            image_dir, '19.MET_nonlinear_frequency_response_and_compensated.png'),
        os.path.join(
            image_dir, '21.MET_nonlinear_parameters_and_compensated.png'),
        os.path.join(image_dir, '23.Combined_19_and_21.png'),
        space=0.02
    )
    # 合并18和23
    concatenate_images(
        os.path.join(image_dir, '23.Combined_19_and_21.png'),
        os.path.join(
            image_dir, '18.Dynamic_linear_response_and_compensated.png'),
        os.path.join(image_dir, '32.Combined_18_and_23.png'),
        space=0.0
    )

    # 合并图24和26
    concatenate_images(
        os.path.join(image_dir, '26.Nonlinearity_bar.png'),
        os.path.join(image_dir, '24.Boxplots_linearity_Sn_fn.png'),
        os.path.join(image_dir, '29.Combined_24_and_26.png')
    )

    # 合并图29和28
    concatenate_images(
        os.path.join(image_dir, '24.Boxplots_linearity_Sn_fn.png'),
        os.path.join(image_dir, '28.LUT_Performance.png'),
        os.path.join(image_dir, '33.Combined_29_and_28.png'),
        space=0.0
    )

    # # 合并 27 和 30
    # concatenate_images(
    #     os.path.join('paper/image', '30.Loss_and_Val_Loss.png'),
    #     os.path.join('paper/image', '27.Training_Loss.png'),
    #     os.path.join('paper/image', '31.Combined_27_and_30.png'),
    #     space=0
    # )

    combine_images_with_labels(
        [
            'paper/image/30.Loss_and_Val_Loss.png',
            'paper/image/27.Training_Loss.png',
        ],
        'paper/image/31.Combined_27_and_30.png',
    )

    # 合并 3 和 2
    concatenate_images(
        os.path.join('paper/image', '3.MET_nonlinear_frequency_response.png'),
        os.path.join('paper/image', '2.Dynamic_linear_response.png'),
        os.path.join('paper/image', '38.Combined_2_and_3.png'),
        space=0
    )

    plot_frirnn.main()

    fig_pdf.main()
