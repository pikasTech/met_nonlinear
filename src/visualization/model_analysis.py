import os
import json
import re
import math
import matplotlib.pyplot as plt
from core.data_processing import Dataset_COMP
from core.freq_config_manager import freq_config_manager
# 假设TimeSeries和System来自signal_processing模块，如果不是请调整
from calibration_analyzer import exam_process, exam_class
from calibration_analyzer.exam_class import TimeSeries, System
import numpy as np


def _compute_linearity_by_frequency(input_rms_by_freq, output_rms_origin_by_freq, output_rms_comped_by_freq, magnitudes, frequencies):
    """按频点计算 R² 线性度（标准定义：1 - SS_res/SS_tot）。

    正确计算：输出 RMS vs 输入 RMS
    - x: input_rms_by_freq[i] - 第 i 个频率点在不同 sweep 下的输入 RMS
    - y: output_rms_origin_by_freq[i] - 第 i 个频率点在不同 sweep 下的输出 RMS
    - 理想线性：y = k*x，R² ≈ 1
    - 非线性：R² < 1
    """
    results = []

    for i, freq in enumerate(frequencies):
        x = np.array(input_rms_by_freq[i], dtype=float)
        y_origin = np.array(output_rms_origin_by_freq[i], dtype=float)
        y_comped = np.array(output_rms_comped_by_freq[i], dtype=float)

        r2_origin, details_origin = _calculate_standard_r2(x, y_origin)
        r2_comped, details_comped = _calculate_standard_r2(x, y_comped)

        improvement = r2_comped - r2_origin

        results.append({
            'frequency_hz': float(freq),
            'magnitudes': [float(v) for v in magnitudes],
            'input_rms': [float(v) for v in x],
            'output_rms_origin': [float(v) for v in y_origin],
            'output_rms_comped': [float(v) for v in y_comped],
            'r_squared_origin': float(r2_origin),
            'r_squared_comped': float(r2_comped),
            'improvement': float(improvement),
            'details_origin': details_origin,
            'details_comped': details_comped,
        })

    return results


def _calculate_standard_r2(x, y):
    """计算标准 R²（决定系数）：R² = 1 - SS_res/SS_tot。
    
    使用最小二乘法拟合 y = a*x + b，然后计算拟合优度。
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    n = len(x)
    if n < 2:
        return 0.0, {}

    x_mean = np.mean(x)
    y_mean = np.mean(y)

    ss_tot = np.sum((y - y_mean) ** 2)
    if ss_tot < 1e-12:
        return 1.0, {'ss_tot': 0.0, 'ss_res': 0.0, 'r2': 1.0, 'slope': 0.0, 'intercept': 0.0}

    sum_x = np.sum(x)
    sum_y = np.sum(y)
    sum_xy = np.sum(x * y)
    sum_x2 = np.sum(x ** 2)

    denominator = n * sum_x2 - sum_x ** 2
    if abs(denominator) < 1e-12:
        slope = 0.0
        intercept = y_mean
    else:
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / n

    y_pred = slope * x + intercept
    ss_res = np.sum((y - y_pred) ** 2)

    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0

    details = {
        'n': int(n),
        'x_mean': float(x_mean),
        'y_mean': float(y_mean),
        'sum_x': float(sum_x),
        'sum_y': float(sum_y),
        'sum_xy': float(sum_xy),
        'sum_x2': float(sum_x2),
        'denominator': float(denominator),
        'slope': float(slope),
        'intercept': float(intercept),
        'y_pred': [float(v) for v in y_pred],
        'ss_tot': float(ss_tot),
        'ss_res': float(ss_res),
        'r2': float(r_squared),
    }

    return float(r_squared), details


def FR_for_comp_real_data(
    model,
    dataset: Dataset_COMP,
    freq_range=None,
    gain_range=None,
    use_debug=False,
    freq_start_skip=0,
    freq_end_skip=0,
    output_folder='results',
    use_linear_response=True,
    only_origin=False,
    config=None
):
    systems_origin_list = []
    systems_comped_list = []
    input_rms_by_freq = []
    output_rms_origin_by_freq = []
    output_rms_comped_by_freq = []

    # reshape X_features from (magn_num, freq_num, points_num) to (seq_num=magn_num*freq_num, points_num, 1)

    X_features = dataset.reshape2feature(dataset.output_ori)
    # X_features = dataset.X_samples.reshape(1, -1, 1)
    print(f'X_features shape: {X_features.shape}')
    pre_features = model.predict(X_features, batch_size=10)
    pre_samples = dataset.reshape2sample(pre_features)

    freq_num = dataset.inputs.shape[1]

    for freq_i in range(freq_num):
        input_rms_list = []
        output_rms_origin_list = []
        output_rms_comped_list = []
        for sweep_i in range(dataset.magn_num):
            input_signal = dataset.inputs[sweep_i, freq_i, :]
            output_ori_signal = dataset.output_ori[sweep_i, freq_i, :]
            output_cmp_signal = pre_samples[sweep_i, freq_i, :]
            input_rms = float(np.sqrt(np.mean(input_signal ** 2)))
            output_rms_origin = float(np.sqrt(np.mean(output_ori_signal ** 2)))
            output_rms_comped = float(np.sqrt(np.mean(output_cmp_signal ** 2)))
            input_rms_list.append(input_rms)
            output_rms_origin_list.append(output_rms_origin)
            output_rms_comped_list.append(output_rms_comped)
        input_rms_by_freq.append(input_rms_list)
        output_rms_origin_by_freq.append(output_rms_origin_list)
        output_rms_comped_by_freq.append(output_rms_comped_list)

    if use_debug:
        plt.figure(figsize=(12, 8))
    for sweep_i in range(dataset.magn_num):
        inputs = dataset.inputs[sweep_i, :, :]
        output_ori = dataset.output_ori[sweep_i, :, :]
        output_cmp = pre_samples[sweep_i, :, :]
        if use_debug:
            for freq_i in range(inputs.shape[0]):
                output_points = output_ori[freq_i, :]
                comped_points = output_cmp[freq_i, :]
                plt.plot(output_points, label='Output')
                plt.plot(comped_points, label='Compensated')
                plt.legend()
                plt.pause(0.01)
                plt.cla()
        input_trs = [TimeSeries(inputs[freq_i, :], dataset.fs)
                     for freq_i in range(inputs.shape[0])]
        output_trs = [TimeSeries(output_ori[freq_i, :], dataset.fs)
                      for freq_i in range(output_ori.shape[0])]
        comped_trs = [TimeSeries(output_cmp[freq_i, :], dataset.fs)
                      for freq_i in range(output_cmp.shape[0])]
        system_origin = System.fromTimeSeries(
            input_trs,
            output_trs,
            frequencies=dataset.freq_list,
            use_parallel=False
        )
        systems_origin_list.append(system_origin)
        system_comped = System.fromTimeSeries(
            input_trs,
            comped_trs,
            frequencies=dataset.freq_list,
            use_parallel=False
        )
        systems_comped_list.append(system_comped)

    # Plotting the systems
    system_fit_params_list_origin = []
    system_fit_params_list_comped = []
    for sweep_i in range(dataset.magn_num):
        system_origin: System = systems_origin_list[sweep_i]
        system_comped: System = systems_comped_list[sweep_i]
        magnitude = dataset.magn_list[sweep_i]
        system_origin.plot(
            markersize=0, label=f'{magnitude:.2f}mm/s2 origin', legend=True, disable_phase=True)
        if not only_origin:
            system_comped.plot(linestyle='--', marker='x',
                            markersize=4, label=f'{magnitude:.2f}mm/s2 comped', freq_range=freq_range, gain_range=gain_range, legend=True, disable_phase=True)
        # 使用配置的频率范围或默认值
        default_range = (5, 200)
        if config is not None:
            freq_range_hz = freq_config_manager.get_freq_range_hz(config, default_range)
        else:
            freq_range_hz = default_range
        default_center_frequency_bounds_hz = (10, 128)
        if config is not None:
            center_frequency_bounds_hz = freq_config_manager.get_freq_range_hz(
                config, default_center_frequency_bounds_hz)
        else:
            center_frequency_bounds_hz = default_center_frequency_bounds_hz
        system_fit_origin = exam_process.ws_system_fit(
            system_origin,
            k=1.0,
            freq_range=freq_range_hz,
            center_frequency_bounds_hz=center_frequency_bounds_hz,
        )
        # a tuple for (A, B, C)
        system_fit_params_origin = list(system_fit_origin.fit_params)
        # 使用配置的频率范围或默认值
        default_range_comped = (10, 200)
        if config is not None:
            freq_range_hz_comped = freq_config_manager.get_freq_range_hz(config, default_range_comped)
        else:
            freq_range_hz_comped = default_range_comped
        system_fit_comped = exam_process.ws_system_fit(
            system_comped,
            k=1.0,
            freq_range=freq_range_hz_comped,
            direct_guess=False,
            center_frequency_bounds_hz=center_frequency_bounds_hz,
        )
        system_fit_params_comped = list(system_fit_comped.fit_params)
        system_fit_params_list_origin.append(system_fit_params_origin)
        system_fit_params_list_comped.append(system_fit_params_comped)
    gains_origin = [systems_origin_list[i].toabs()
                    for i in range(len(systems_origin_list))]
    gains_comped = [systems_comped_list[i].toabs()
                    for i in range(len(systems_comped_list))]
    magnitudes = [dataset.magn_list[i]
                  for i in range(len(dataset.magn_list))]
    f = dataset.freq_list

    if use_linear_response:
        fig_linear = plt.figure(figsize=(12, 8))

        # Prepare data for saving
        linear_response_data = {
            'gains_origin': [list(g) for g in gains_origin],
            'gains_comped': [list(g) for g in gains_comped],
            'magnitudes': magnitudes,
            'frequencies': f,
            'fit_params_origin': system_fit_params_list_origin,
            'fit_params_comped': system_fit_params_list_comped
        }

        # Ensure the results directory exists
        os.makedirs(output_folder, exist_ok=True)

        # Save the data to a JSON file
        output_path = os.path.join(output_folder, 'linear_response.json')
        with open(output_path, 'w', encoding='utf-8') as json_file:
            json.dump(linear_response_data, json_file)

        linearity_by_frequency = _compute_linearity_by_frequency(
            input_rms_by_freq,
            output_rms_origin_by_freq,
            output_rms_comped_by_freq,
            magnitudes,
            f,
        )
        linearity_output_path = os.path.join(output_folder, 'linearity_by_frequency.json')
        with open(linearity_output_path, 'w', encoding='utf-8') as json_file:
            json.dump({'linearity_by_frequency': linearity_by_frequency}, json_file, indent=2, ensure_ascii=False)

        print('Per-frequency R^2 linearity (markdown table):')
        print('| Frequency (Hz) | Origin R^2 | Comped R^2 | Improvement |')
        print('| :--- | ---: | ---: | ---: |')
        for item in linearity_by_frequency:
            print(
                f"| {item['frequency_hz']:>9.1f} | "
                f"{item['r_squared_origin']:>10.4f} | "
                f"{item['r_squared_comped']:>10.4f} | "
                f"{item['improvement']:>10.4f} |"
            )
        print(f'Linearity-by-frequency results saved to: {linearity_output_path}')

        # 创建颜色映射
        color_map = plt.cm.get_cmap("tab20", len(f))  # 使用 20 种不同颜色
        plotted_labels = set()

        # 原始响应和补偿后响应绘制
        for i in range(freq_start_skip, len(f) - freq_end_skip):
            color = color_map(i)

            # 原始响应绘制
            gain_origin = [gains_origin[k][i]
                        for k in range(len(gains_origin))]
            lineraty = [gain / gain_origin[0] for gain in gain_origin]
            outputs_std = [lineraty[k] * magnitudes[k]
                        for k in range(len(gain_origin))]  # 每个震级下的输出
            plt.plot(
                magnitudes, outputs_std,
                label=f'Origin @ {f[i]} Hz', linestyle='', marker='o', markersize=3, color=color
            )

            # 补偿后响应绘制 - 只在非 only_origin 模式下绘制
            if not only_origin:
                gain_comped = [gains_comped[k][i]
                            for k in range(len(gains_comped))]
                outputs = [gain_comped[k] * magnitudes[k]
                        for k in range(len(gain_comped))]
                lineraty = outputs[0] / magnitudes[0]
                outputs_std = [l / lineraty for l in outputs]
                plt.plot(
                    magnitudes, outputs_std,
                    linestyle='', marker='^', markersize=8, markerfacecolor='none',
                    markeredgewidth=1, color=color, label=f'Compensated @ {f[i]} Hz'
                )

            plotted_labels.add(f[i])

        # 绘制斜率为 1 的参考线
        ideal_line, = plt.plot(
            [min(magnitudes), max(magnitudes)],
            [min(magnitudes), max(magnitudes)],
            linestyle='--', color='black', linewidth=2
        )

        # 获取图例句柄和标签
        handles, labels = plt.gca().get_legend_handles_labels()

        # 提取频率值并按类型分组排序
        def extract_frequency(label):
            match = re.search(r'@ (\d+(?:\.\d+)?) Hz', label)
            return float(match.group(1)) if match else float('inf')

        # 按类型分组
        origin_handles_labels = sorted(
            [(h, l) for h, l in zip(handles, labels) if 'Origin' in l],
            key=lambda x: extract_frequency(x[1])
        )
    
        if only_origin:
            # 在 only_origin 模式下，只使用原始响应数据
            sorted_handles_labels = origin_handles_labels
        else:
            # 在包含补偿数据的模式下，包括两组数据
            compensated_handles_labels = sorted(
                [(h, l) for h, l in zip(handles, labels) if 'Compensated' in l],
                key=lambda x: extract_frequency(x[1])
            )
            # 合并排序结果：Origin 左列，Compensated 右列
            sorted_handles_labels = origin_handles_labels + compensated_handles_labels
    
        sorted_handles, sorted_labels = zip(*sorted_handles_labels)

        # 更新标题以反映当前模式
        title_text = 'Frequency-Dependent Linear Response Analysis'
        if only_origin:
            title_text += '\n(Points: Original)'
        else:
            title_text += '\n(Points: Original, Triangle: Compensated)'

        # 重绘主图例
        ncols = 1 if only_origin else 2  # 如果只有原始数据，只使用一列图例
        main_legend = plt.legend(sorted_handles, sorted_labels, loc='upper left', 
                                bbox_to_anchor=(0.0, 0.9), ncol=ncols, title="Responses")

        # 添加独立图例（Ideal Linear Response）
        plt.gca().add_artist(main_legend)  # 确保主图例仍在图表中
        plt.legend([ideal_line], ['Ideal Linear Response'], loc='upper left',
                bbox_to_anchor=(0.0, 1.0), title="Reference", frameon=True)

        # 添加标签和标题
        plt.xlabel('Magnitude (m/s^2)')
        plt.ylabel('Amplitude (Normalized)')
        plt.title(title_text)
        plt.grid()
        # plt.tight_layout()


def conv1d_frequency_response(conv1d_layer, fs=2000, time_length=10, f_range=(0.5, 150), amplitude=1, points=100, use_parallel=True):
    """
    分析CONV1D层的频率响应并返回System对象

    Args:
        conv1d_layer: Tensorflow/Keras的Conv1D层
        fs: 采样频率
        time_length: 时间长度
        f_range: 频率范围
        amplitude: 输入信号振幅
        points: 频率点数
        use_parallel: 是否使用并行计算

    Returns:
        System: 包含频率响应的System对象
    """
    # 生成频率列表
    if isinstance(f_range, tuple) and len(f_range) == 2:
        f = np.logspace(np.log10(f_range[0]), np.log10(f_range[1]), points)
    else:
        f = f_range

    # 创建一个类似模型的包装类，以便与System.frequency_response_from_time_domain兼容
    class Conv1DWrapper:
        def __init__(self, conv_layer):
            self.conv_layer = conv_layer

        def time_response(self, time_series):
            # 将TimeSeries转换为张量
            x_input = np.array(time_series.samples).reshape(1, -1, 1)
            # 通过卷积层处理
            y_pred = self.conv_layer(x_input).numpy()
            # 创建输出TimeSeries
            return TimeSeries(y_pred[0, :, 0], time_series.fs)

    # 创建包装器
    wrapper = Conv1DWrapper(conv1d_layer)

    # 使用frequency_response_from_time_domain方法获取频率响应
    system = System.frequency_response_from_time_domain(
        wrapper,
        fs=fs,
        time_length=time_length,
        f_range=f_range,
        amplitude=amplitude,
        use_parallel=use_parallel,
        points=points
    )

    return system


def conv1d_frequency_response_multichannel(model, fs=2000, time_length=10, f_range=(5, 200), amplitude=1, points=100, use_parallel=False, batch_size=512):
    """
    分析多通道模型的频率响应并返回多个System对象，使用批处理方式加速计算

    Args:
        model: Tensorflow/Keras模型，输出形状为(batch_size, time_steps, channels)
        fs: 采样频率
        time_length: 时间长度
        f_range: 频率范围
        amplitude: 输入信号振幅
        points: 频率点数
        use_parallel: 是否使用并行计算
        batch_size: 批处理大小，控制一次处理多少个频率点

    Returns:
        list: 包含每个通道频率响应的System对象列表
    """
    # 获取模型输出通道数
    output_channels = model.output_shape[-1]

    # 生成频率列表
    if isinstance(f_range, tuple) and len(f_range) == 2:
        f = np.logspace(np.log10(f_range[0]), np.log10(f_range[1]), points)
    else:
        f = f_range

    # 计算时间序列长度
    n = int(time_length * fs)
    t = np.arange(n) / fs

    # 存储每个频率点的输入和所有通道的输出
    input_series_list = []
    output_series_by_channel = [[] for _ in range(output_channels)]

    # 批量生成输入信号和获取输出响应
    for i in range(0, len(f), batch_size):
        # 取当前批次的频率点
        batch_freqs = f[i:i+batch_size]
        batch_size_actual = len(batch_freqs)

        # 为每个频率创建输入时间序列对象
        for freq in batch_freqs:
            input_ts = TimeSeries.fromSin(
                A=1, f=freq, fs=fs, time_length=time_length, fade_in=0.3, fade_out=0.0)
            input_series_list.append(input_ts)

        # 批量生成所有频率点的正弦波，形状为(batch_size, time_steps, 1)
        batch_inputs = np.zeros((batch_size_actual, n, 1))
        for j, freq in enumerate(batch_freqs):
            batch_inputs[j, :, 0] = amplitude * np.sin(2 * np.pi * freq * t)

        # 通过模型获取多通道输出
        # 形状为(batch_size, time_steps, channels)
        batch_outputs = model(batch_inputs).numpy()

        # 将每个通道的输出存储为TimeSeries对象
        for j, freq in enumerate(batch_freqs):
            for channel in range(output_channels):
                channel_output = batch_outputs[j, :, channel]
                # 只取后半部分数据
                channel_output = channel_output[n//2:]
                output_ts = TimeSeries(channel_output, fs)
                output_series_by_channel[channel].append(output_ts)

        print(f"已处理{i+batch_size_actual}/{len(f)}个频率点")

    # 为每个通道创建System对象
    systems = []
    for channel in range(output_channels):
        # print(f"Processing channel {channel + 1}/{output_channels}")
        system = System.fromTimeSeries(
            input_series_list,
            output_series_by_channel[channel],
            frequencies=f,
            use_parallel=use_parallel
        )
        systems.append(system)

    return systems
    """
    评估假频抑制效果
    
    参数:
        linear_response_data: 包含gains_origin, gains_comped, frequencies的字典
                            或linear_response.json的文件路径
    
    返回:
        evaluation_results: 包含各项评估指标的字典
    """
    
    # 如果输入是文件路径，加载数据
    if isinstance(linear_response_data, str):
        with open(linear_response_data, 'r') as f:
            linear_response_data = json.load(f)
    
    # 1. 提取数据
    gains_origin = np.array(linear_response_data['gains_origin'][0])
    gains_comped = np.array(linear_response_data['gains_comped'][0])
    frequencies = np.array(linear_response_data['frequencies'])
    
    # 2. 定义评估频段
    freq_bands = {
        'core': (90, 100),      # 核心假频区间
        'extended': (85, 105),  # 扩展评估区间
        'full': (10, 120)       # 完整低频段
    }
    
    # 3. 计算各频段指标
    results = {}
    for band_name, (f_min, f_max) in freq_bands.items():
        # 获取频段内的数据索引
        indices = np.where((frequencies >= f_min) & (frequencies <= f_max))[0]
        
        # 提取频段内的增益值
        gains_orig_band = gains_origin[indices]
        gains_comp_band = gains_comped[indices]
        
        # 计算波动幅度（单位：V/m/s）
        ripple_orig = float(np.max(gains_orig_band) - np.min(gains_orig_band))
        ripple_comp = float(np.max(gains_comp_band) - np.min(gains_comp_band))
        
        # 计算抑制率
        if ripple_orig > 0:
            suppression_ratio = (ripple_orig - ripple_comp) / ripple_orig * 100
        else:
            suppression_ratio = 0.0
        
        # 存储结果
        results[f'ASR_{band_name}'] = {
            'suppression_ratio': suppression_ratio,
            'original_ripple': ripple_orig,
            'compensated_ripple': ripple_comp,
            'frequency_range': (f_min, f_max),
            'max_orig': float(np.max(gains_orig_band)),
            'min_orig': float(np.min(gains_orig_band)),
            'max_comp': float(np.max(gains_comp_band)),
            'min_comp': float(np.min(gains_comp_band))
        }
    
    # 4. 计算平滑度指标（基于一阶导数）
    core_indices = np.where((frequencies >= 90) & (frequencies <= 100))[0]
    smoothness_orig = calculate_smoothness(gains_origin, core_indices)
    smoothness_comp = calculate_smoothness(gains_comped, core_indices)
    
    if smoothness_orig > 0:
        smoothness_enhancement = (smoothness_orig - smoothness_comp) / smoothness_orig * 100
    else:
        smoothness_enhancement = 0.0
    
    results['smoothness_enhancement'] = smoothness_enhancement
    
    # 5. 计算峰值改善率
    peak_improvement = calculate_peak_improvement(
        gains_origin[core_indices], 
        gains_comped[core_indices]
    )
    results['peak_improvement_ratio'] = peak_improvement
    
    # 6. 计算综合评分
    weights = {
        'ASR_core': 0.4,
        'ASR_extended': 0.3,
        'peak_improvement_ratio': 0.2,
        'smoothness_enhancement': 0.1
    }
    
    overall_score = calculate_weighted_score(results, weights)
    results['overall_score'] = overall_score
    
    # 7. 确定评级
    results['grade'] = determine_grade(overall_score)
    
    return results


def calculate_smoothness(gains, indices):
    """
    计算频响曲线的平滑度（基于一阶导数的标准差）
    
    参数:
        gains: 增益数组
        indices: 要计算的索引范围
    
    返回:
        smoothness: 平滑度指标（越小越平滑）
    """
    if len(indices) < 2:
        return 0.0
    
    gains_band = gains[indices]
    # 计算一阶差分
    diff = np.diff(gains_band)
    # 返回差分的标准差作为平滑度指标
    return float(np.std(diff))


def calculate_peak_improvement(gains_orig, gains_comp):
    """
    计算峰值改善率
    
    参数:
        gains_orig: 原始增益数组
        gains_comp: 补偿后增益数组
    
    返回:
        peak_improvement: 峰值改善率（百分比）
    """
    # 计算平均值
    mean_orig = np.mean(gains_orig)
    mean_comp = np.mean(gains_comp)
    
    # 计算最大偏离
    max_deviation_orig = float(np.max(np.abs(gains_orig - mean_orig)))
    max_deviation_comp = float(np.max(np.abs(gains_comp - mean_comp)))
    
    if max_deviation_orig > 0:
        improvement = (max_deviation_orig - max_deviation_comp) / max_deviation_orig * 100
    else:
        improvement = 0.0
    
    return improvement


def calculate_weighted_score(results, weights):
    """
    计算加权综合评分
    
    参数:
        results: 包含各项指标的结果字典
        weights: 各项指标的权重字典
    
    返回:
        overall_score: 综合评分（0-100）
    """
    score = 0.0
    total_weight = 0.0
    
    for key, weight in weights.items():
        if key == 'ASR_core':
            value = results['ASR_core']['suppression_ratio']
        elif key == 'ASR_extended':
            value = results['ASR_extended']['suppression_ratio']
        else:
            value = results.get(key, 0.0)
        
        # 确保值在0-100范围内
        value = max(0.0, min(100.0, value))
        score += value * weight
        total_weight += weight
    
    if total_weight > 0:
        return score / total_weight
    else:
        return 0.0


def determine_grade(score):
    """
    根据综合评分确定等级
    
    参数:
        score: 综合评分（0-100）
    
    返回:
        grade: 评级（A/B/C/D）
    """
    if score >= 80:
        return 'A'
    elif score >= 60:
        return 'B'
    elif score >= 40:
        return 'C'
    else:
        return 'D'


def batch_evaluate_experiments(experiment_list, output_file=None):
    """
    批量评估多个实验的假频抑制效果
    
    参数:
        experiment_list: 实验名称列表
        output_file: 输出结果文件路径（可选）
    
    返回:
        results_summary: 评估结果汇总列表
    """
    results_summary = []
    
    for exp_name in experiment_list:
        # 构建数据文件路径
        data_path = f'projects/{exp_name}/data/linear_response.json'
        
        # 检查文件是否存在
        if not os.path.exists(data_path):
            print(f"警告：{data_path} 不存在，跳过实验 {exp_name}")
            continue
        
        try:
            # 执行评估
            evaluation = evaluate_alias_suppression(data_path)
            
            # 汇总结果
            summary = {
                'experiment': exp_name,
                'ASR_core': evaluation['ASR_core']['suppression_ratio'],
                'ASR_extended': evaluation['ASR_extended']['suppression_ratio'],
                'peak_improvement': evaluation['peak_improvement_ratio'],
                'smoothness': evaluation['smoothness_enhancement'],
                'overall_score': evaluation['overall_score'],
                'grade': evaluation['grade'],
                'core_ripple_orig': evaluation['ASR_core']['original_ripple'],
                'core_ripple_comp': evaluation['ASR_core']['compensated_ripple']
            }
            results_summary.append(summary)
            
            # 打印单个实验结果
            print(f"\n实验: {exp_name}")
            print(f"  核心区间抑制率: {summary['ASR_core']:.1f}%")
            print(f"  综合评分: {summary['overall_score']:.1f}")
            print(f"  等级: {summary['grade']}")
            
        except Exception as e:
            print(f"错误：评估实验 {exp_name} 时出错: {str(e)}")
            continue
    
    # 按综合评分排序
    results_summary.sort(key=lambda x: x['overall_score'], reverse=True)
    
    # 保存结果到文件
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results_summary, f, indent=2, ensure_ascii=False)
        print(f"\n评估结果已保存到: {output_file}")
    
    # 打印汇总表格
    print("\n" + "="*80)
    print("实验评估结果汇总")
    print("="*80)
    print(f"{'实验名称':<30} {'核心ASR':<10} {'综合评分':<10} {'等级':<6}")
    print("-"*80)
    for result in results_summary:
        print(f"{result['experiment']:<30} "
              f"{result['ASR_core']:>8.1f}% "
              f"{result['overall_score']:>9.1f} "
              f"{result['grade']:>5}")
    
    return results_summary
