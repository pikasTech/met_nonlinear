"""
waveviewer.py

这个模块是一个wave查看器，用于显示和分析.wave文件中的数据。
wave文件的定义在wavedata.py中，可以使用waveprocessor.py来处理wave文件。

使用adjuster.py来进行UI界面的显示，支持显示wavedata里面的一个record的数据，
同一个record的多个通道绘制在同一张图里面，使用matplotlib来绘制，
使用panel内嵌的plotter来显示和刷新数据。

新增功能：
- 频响分析：使用waveprocessor的analyze_sweep_response方法进行频响分析
- 双标签页界面：波形查看器和频响分析器分别在不同标签页
- 在panel内绘制图像：使用adjuster的Plotter功能
"""

import os
import sys
import numpy as np
import csv
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import messagebox, filedialog
from typing import Dict, Any, List, Optional, Tuple, Union

# 导入相关模块
from calibration_analyzer.adjuster import Panel
from calibration_analyzer.wavedata import WaveData, WaveRecord
from calibration_analyzer.waveprocessor import WaveProcessor
from calibration_analyzer.exam_class import System

# 全局变量
viewer = None
freq_analyzer = None
g_fr_panel = None  # 用于存储当前的Panel引用，方便在不同类中访问
g_view_panel = None  # 用于存储当前的Panel引用，方便在不同类中访问


class FrequencyResponseAnalyzer:
    """频率响应分析器类，用于分析波形文件的频率响应"""

    def __init__(self):
        """初始化频响分析器"""
        self.input_wave_data = None
        self.output_wave_data = None
        self.systems = None  # 分析结果，可能是单个System或System列表
        self.processor = WaveProcessor()

    def load_input_wave_file(self, filepath: str) -> bool:
        """加载输入波形文件"""
        try:
            if not filepath or not os.path.exists(filepath):
                messagebox.showerror("错误", f"输入文件不存在: {filepath}")
                return False

            self.input_wave_data = self.processor.load_waveform(filepath)
            print(f"✅ 已加载输入波形文件: {len(self.input_wave_data.records)} 个记录")
            return True
        except Exception as e:
            messagebox.showerror("错误", f"加载输入波形文件失败: {str(e)}")
            return False

    def load_output_wave_file(self, filepath: str) -> bool:
        """加载输出波形文件"""
        try:
            if not filepath or not os.path.exists(filepath):
                messagebox.showerror("错误", f"输出文件不存在: {filepath}")
                return False

            self.output_wave_data = self.processor.load_waveform(filepath)
            print(f"✅ 已加载输出波形文件: {len(self.output_wave_data.records)} 个记录")
            return True
        except Exception as e:
            messagebox.showerror("错误", f"加载输出波形文件失败: {str(e)}")
            return False

    def analyze_frequency_response(self, input_channel_index=0, output_channel_index=0) -> bool:
        """执行频率响应分析，自动检测是否需要多振幅分析

        参数:
            input_channel_index: 输入通道索引
            output_channel_index: 输出通道索引
        """
        if not self.input_wave_data or not self.output_wave_data:
            messagebox.showerror("错误", "请先加载输入和输出波形文件")
            return False

        try:
            # 检测输入波形数据中是否包含多振幅信息
            has_magnitude = self._check_multi_magnitude_data()

            if has_magnitude:
                print(
                    f"🔍 检测到多振幅数据，开始多振幅频率响应分析... 输入通道: {input_channel_index}, 输出通道: {output_channel_index}")
                # 使用多振幅分析函数
                magnitudes, systems = self.processor.analyze_multi_magnitudes_sweep_response(
                    input_wave_data=self.input_wave_data,
                    output_wave_data=self.output_wave_data,
                    input_channel_index=input_channel_index,
                    output_channel_index=output_channel_index
                )
                # 将结果存储为字典格式，便于后续处理
                self.systems = {
                    'type': 'multi_magnitude',
                    'magnitudes': magnitudes,
                    'systems': systems
                }
                print(f"✅ 多振幅频率响应分析完成，发现 {len(magnitudes)} 个振幅: {magnitudes}")
            else:
                print(
                    f"🔍 开始单振幅频率响应分析... 输入通道: {input_channel_index}, 输出通道: {output_channel_index}")
                # 使用单振幅分析函数
                system = self.processor.analyze_sweep_response(
                    input_wave_data=self.input_wave_data,
                    output_wave_data=self.output_wave_data,
                    input_channel_index=input_channel_index,
                    output_channel_index=output_channel_index
                )
                # 将结果存储为字典格式，保持一致性
                self.systems = {
                    'type': 'single_magnitude',
                    'system': system
                }
                print(
                    f"✅ 单振幅频率响应分析完成，输入通道 {input_channel_index} -> 输出通道 {output_channel_index}")

            return True
        except Exception as e:
            messagebox.showerror("错误", f"频率响应分析失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def _check_multi_magnitude_data(self) -> bool:
        """检查输入波形数据是否包含多振幅信息

        返回:
            bool: 如果存在多振幅数据返回True，否则返回False
        """
        if not self.input_wave_data or not self.input_wave_data.records:
            return False

        # 检查输入记录中是否有振幅或幅度信息
        magnitudes = set()

        for record in self.input_wave_data.records:
            # 检查 "magnitude" 字段
            magnitude = record.user_metadata.get("magnitude")
            if magnitude is not None:
                magnitudes.add(float(magnitude))

        # 如果找到了振幅信息且有多个不同的值，则认为是多振幅数据
        if len(magnitudes) > 1:
            print(
                f"📊 检测到多振幅数据，包含 {len(magnitudes)} 个不同振幅: {sorted(magnitudes)}")
            return True
        elif len(magnitudes) == 1:
            print(f"📊 检测到单振幅数据，振幅值: {list(magnitudes)[0]}")
            return False
        else:
            print("📊 未检测到振幅信息，使用单振幅模式")
            return False

    def plot_frequency_response(self, plot_type="both"):
        """绘制频率响应图，使用panel内的plotter，支持单振幅和多振幅显示

        参数:
            plot_type: 绘图类型 ("magnitude", "phase", "both")
        """
        if not self.systems:
            messagebox.showwarning("警告", "请先执行频率响应分析")
            return

        if not g_fr_panel:
            messagebox.showerror("错误", "未找到绘图面板")
            return

        try:
            # 清除现有绘图
            g_fr_panel.plotter.clear()

            # 根据分析类型选择不同的绘制方式
            if self.systems['type'] == 'single_magnitude':
                self._plot_single_magnitude_response(plot_type)
            else:
                self._plot_multi_magnitude_response(plot_type)

        except Exception as e:
            messagebox.showerror("错误", f"绘制频率响应失败: {str(e)}")
            import traceback
            traceback.print_exc()

    def _plot_single_magnitude_response(self, plot_type="both"):
        """绘制单振幅频率响应"""
        system = self.systems['system']

        # 获取频率和响应数据
        frequencies = system.f
        gains = system.toabs()
        phases_deg = np.degrees(system.tophase())

        # 根据plot_type绘制
        if plot_type in ["magnitude", "both"]:
            # 绘制幅度响应（对数刻度）
            g_fr_panel.plotter.ax.loglog(
                frequencies, gains,
                marker='o', markersize=4,
                label='幅度响应',
                color=(0.75, 0, 0), linestyle='-'
            )

        if plot_type in ["phase", "both"]:
            # 如果需要同时显示幅度和相位，创建第二个y轴
            if plot_type == "both":
                ax2 = g_fr_panel.plotter.ax.twinx()
                ax2.semilogx(
                    frequencies, phases_deg,
                    marker='s', markersize=4,
                    label='相位响应',
                    color=(0, 0, 0.75), linestyle='--'
                )
                ax2.set_ylabel("相位 (度)")
                ax2.legend(loc='upper right')
            else:
                # 仅绘制相位响应
                g_fr_panel.plotter.ax.semilogx(
                    frequencies, phases_deg,
                    marker='o', markersize=4,
                    label='相位响应',
                    color=(0.75, 0, 0), linestyle='-'
                )

        # 设置标签和标题
        g_fr_panel.plotter.set_labels(
            "频率 (Hz)", "幅度" if plot_type != "phase" else "相位 (度)")
        g_fr_panel.plotter.set_title("频率响应")

        # 设置网格和图例
        g_fr_panel.plotter.ax.grid(True, which="both", alpha=0.3)
        if plot_type != "both":
            g_fr_panel.plotter.set_legend()

        # 显示统计信息
        print(f"📊 频率范围: {frequencies[0]:.2f} Hz - {frequencies[-1]:.2f} Hz")
        print(f"📊 频率点数: {len(frequencies)}")
        print(f"📊 幅度范围: {np.min(gains):.2e} - {np.max(gains):.2e}")

    def _plot_multi_magnitude_response(self, plot_type="both"):
        """绘制多振幅频率响应"""
        magnitudes = self.systems['magnitudes']
        systems = self.systems['systems']

        # 创建颜色映射
        import matplotlib.cm as cm
        colors = cm.viridis(np.linspace(0, 1, len(magnitudes)))

        ax2 = None  # 用于相位响应的第二个y轴

        for i, (magnitude, system) in enumerate(zip(magnitudes, systems)):
            # 获取频率和响应数据
            frequencies = system.f
            gains = system.toabs()
            phases_deg = np.degrees(system.tophase())

            # 创建标签
            label_mag = f'幅度响应 (震级={magnitude:.2f})'
            label_phase = f'相位响应 (震级={magnitude:.2f})'

            # 根据plot_type绘制
            if plot_type in ["magnitude", "both"]:
                # 绘制幅度响应（对数刻度）
                g_fr_panel.plotter.ax.loglog(
                    frequencies, gains,
                    marker='o', markersize=3,
                    label=label_mag,
                    color=colors[i], linestyle='-',
                    alpha=0.8
                )

            if plot_type in ["phase", "both"]:
                # 如果需要同时显示幅度和相位，创建第二个y轴
                if plot_type == "both":
                    if ax2 is None:
                        ax2 = g_fr_panel.plotter.ax.twinx()
                    ax2.semilogx(
                        frequencies, phases_deg,
                        marker='s', markersize=3,
                        label=label_phase,
                        color=colors[i], linestyle='--',
                        alpha=0.8
                    )
                else:
                    # 仅绘制相位响应
                    g_fr_panel.plotter.ax.semilogx(
                        frequencies, phases_deg,
                        marker='o', markersize=3,
                        label=label_phase,
                        color=colors[i], linestyle='-',
                        alpha=0.8
                    )

        # 设置标签和标题
        g_fr_panel.plotter.set_labels(
            "频率 (Hz)", "幅度" if plot_type != "phase" else "相位 (度)")
        g_fr_panel.plotter.set_title(f"多振幅频率响应 ({len(magnitudes)} 个振幅)")

        # 设置网格和图例
        g_fr_panel.plotter.ax.grid(True, which="both", alpha=0.3)

        if plot_type == "both":
            # 为两个y轴分别设置图例
            g_fr_panel.plotter.ax.legend(loc='upper left')
            if ax2:
                ax2.set_ylabel("相位 (度)")
                ax2.legend(loc='upper right')
        else:
            g_fr_panel.plotter.set_legend()

        # 显示统计信息
        first_system = systems[0]
        frequencies = first_system.f
        print(f"📊 频率范围: {frequencies[0]:.2f} Hz - {frequencies[-1]:.2f} Hz")
        print(f"📊 频率点数: {len(frequencies)}")
        print(f"📊 振幅数量: {len(magnitudes)}")
        print(f"📊 振幅范围: {min(magnitudes)} - {max(magnitudes)}")

    def get_channel_count(self) -> int:
        """获取输出通道数量"""
        if not self.systems:
            return 0

        if self.systems['type'] == 'multi_magnitude':
            return len(self.systems['systems'])
        else:
            return 1

    def export_frequency_response(self, filepath: str) -> bool:
        """导出频率响应数据到CSV文件，支持单振幅和多振幅数据"""
        if not self.systems:
            messagebox.showwarning("警告", "请先执行频率响应分析")
            return False

        try:
            if self.systems['type'] == 'single_magnitude':
                return self._export_single_magnitude_response(filepath)
            else:
                return self._export_multi_magnitude_response(filepath)

        except Exception as e:
            messagebox.showerror("错误", f"导出频率响应数据失败: {str(e)}")
            return False

    def _export_single_magnitude_response(self, filepath: str) -> bool:
        """导出单振幅频率响应数据"""
        system = self.systems['system']

        # 准备数据
        frequencies = system.f
        gains = system.toabs()
        gains_db = 20 * np.log10(np.abs(gains))
        phases_deg = np.degrees(system.tophase())

        # 创建CSV内容
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['频率(Hz)', '幅度', '幅度(dB)', '相位(度)'])
            for f, g, g_db, p in zip(frequencies, gains, gains_db, phases_deg):
                writer.writerow([f, g, g_db, p])

        print(f"✅ 单振幅频率响应数据已导出到: {filepath}")
        return True

    def _export_multi_magnitude_response(self, filepath: str) -> bool:
        """导出多振幅频率响应数据"""
        magnitudes = self.systems['magnitudes']
        systems = self.systems['systems']

        # 创建CSV内容
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # 写入表头
            header = ['频率(Hz)']
            for amp in magnitudes:
                header.extend([f'幅度_振幅{amp}', f'幅度dB_振幅{amp}', f'相位度_振幅{amp}'])
            writer.writerow(header)

            # 假设所有系统的频率点相同
            frequencies = systems[0].f

            # 准备所有振幅的数据
            all_gains = []
            all_gains_db = []
            all_phases_deg = []

            for system in systems:
                gains = system.toabs()
                gains_db = 20 * np.log10(np.abs(gains))
                phases_deg = np.degrees(system.tophase())

                all_gains.append(gains)
                all_gains_db.append(gains_db)
                all_phases_deg.append(phases_deg)

            # 写入数据行
            for i, freq in enumerate(frequencies):
                row = [freq]
                for j in range(len(magnitudes)):
                    row.extend([
                        all_gains[j][i],
                        all_gains_db[j][i],
                        all_phases_deg[j][i]
                    ])
                writer.writerow(row)

        print(f"✅ 多振幅频率响应数据已导出到: {filepath}")
        print(f"📊 包含 {len(magnitudes)} 个振幅: {magnitudes}")
        return True

    def get_input_channel_info(self) -> List[Tuple[str, int]]:
        """获取输入波形文件的通道信息

        返回:
            包含通道名称和索引的元组列表
        """
        if not self.input_wave_data or not self.input_wave_data.records:
            return []

        channels = []
        first_record = self.input_wave_data.records[0]
        for i, name in enumerate(first_record.channel_names):
            channels.append((f"通道 {i}: {name}", i))
        return channels

    def get_output_channel_info(self) -> List[Tuple[str, int]]:
        """获取输出波形文件的通道信息

        返回:
            包含通道名称和索引的元组列表
        """
        if not self.output_wave_data or not self.output_wave_data.records:
            return []

        channels = []
        first_record = self.output_wave_data.records[0]
        for i, name in enumerate(first_record.channel_names):
            channels.append((f"通道 {i}: {name}", i))
        return channels


class WaveViewer:
    """Wave查看器类，用于显示和分析.wave文件"""

    def __init__(self):
        """初始化WaveViewer"""
        self.wave_data = None
        self.current_record_id = None
        self.current_record = None
        self.processor = WaveProcessor()
        # 保存面板引用以便动态更新下拉菜单
        global_panel = None

    def setup_ui(self):
        # 在此处不创建matplotlib图表，而是在需要时使用panel内的plotter
        pass

    def load_wave_file(self, filepath: str) -> bool:
        """加载wave文件"""
        try:
            if not filepath or not os.path.exists(filepath):
                messagebox.showerror("错误", f"文件不存在: {filepath}")
                return False

            self.wave_data = self.processor.load_waveform(filepath)

            # 获取所有记录ID
            record_ids = self.wave_data.get_record_ids()
            if not record_ids:
                messagebox.showwarning("警告", "波形文件中没有记录")
                return False

            # 默认选择第一个记录
            self.current_record_id = record_ids[0]
            self.current_record = self.wave_data.get_record(
                self.current_record_id)

            return True
        except Exception as e:
            messagebox.showerror("错误", f"加载波形文件失败: {str(e)}")
            return False

    def set_current_record(self, record_id: str) -> bool:
        """设置当前要显示的记录"""
        if not self.wave_data:
            return False

        try:
            self.current_record = self.wave_data.get_record(record_id)
            self.current_record_id = record_id
            return True
        except Exception as e:
            messagebox.showerror("错误", f"切换记录失败: {str(e)}")
            return False

    def plot_record(self, selected_channels=None, show_grid=True, show_legend=True):
        """绘制当前记录的波形，使用panel内的plotter

        参数:
            selected_channels: 要显示的通道列表，如果为None则显示所有通道
            show_grid: 是否显示网格
            show_legend: 是否显示图例
        """
        if not self.current_record:
            return

        if not g_view_panel or not hasattr(g_view_panel, 'plotter'):
            messagebox.showerror("错误", "未找到绘图面板")
            return

        try:
            # 清除现有绘图
            g_view_panel.plotter.clear()

            # 获取数据
            data = self.current_record.data
            time_steps = data.shape[0]
            sample_rate = self.current_record.sample_rate

            # 创建时间轴
            time_axis = np.arange(time_steps) / sample_rate

            # 获取通道名称
            channel_names = self.current_record.channel_names

            # 确定要绘制的通道
            if selected_channels is None:
                # 显示所有通道
                channels_to_plot = list(range(data.shape[1]))
            else:
                # 显示指定的通道
                channels_to_plot = selected_channels

            # 绘制选中的通道
            for i in channels_to_plot:
                if i < data.shape[1]:  # 确保通道索引有效
                    g_view_panel.plotter.plot(
                        time_axis, data[:, i], label=channel_names[i])

            # 设置图表属性
            units = getattr(self.current_record, 'units', 'V')
            g_view_panel.plotter.set_labels('时间 (秒)', f'幅度 ({units})')

            # 创建详细的标题
            title = f'记录 ID: {self.current_record_id}\n'
            title += f'采样率: {sample_rate:.1f} Hz, 持续时间: {self.current_record.duration:.3f} s, '
            title += f'总通道数: {self.current_record.num_channels}, 显示通道: {len(channels_to_plot)}'
            g_view_panel.plotter.set_title(title)

            # 根据参数决定是否显示网格和图例
            if show_grid:
                g_view_panel.plotter.ax.grid(True, alpha=0.3)
            else:
                g_view_panel.plotter.ax.grid(False)

            if show_legend and len(channels_to_plot) > 0:
                g_view_panel.plotter.set_legend()

        except Exception as e:
            messagebox.showerror("错误", f"绘制波形失败: {str(e)}")
            import traceback
            traceback.print_exc()

    def get_available_channels(self) -> List[Tuple[str, int]]:
        """获取当前记录的可用通道列表

        返回:
            包含通道名称和索引的元组列表
        """
        if not self.current_record:
            return []

        channels = []
        for i, name in enumerate(self.current_record.channel_names):
            channels.append((name, i))
        return channels

    def update_record_dropdown(self):
        """更新记录选择下拉菜单"""
        if not self.wave_data or not g_view_panel:
            return

        # 获取记录下拉菜单组件
        record_dropdown = None

        for widget in g_view_panel.widgets:
            if widget.get_label() == "record_id@dropdown":
                record_dropdown = widget
                break
        if record_dropdown:
            # 创建记录选项字典
            record_options = {}
            for record_id in self.wave_data.get_record_ids():
                # 更新下拉菜单选项
                record_options[f"{record_id}"] = record_id
            record_dropdown.update_options(record_options)
            print(f"✅ 记录下拉菜单已更新: {len(record_options)} 个记录")

    def update_channel_dropdown(self):
        """更新通道选择下拉菜单"""
        if not self.current_record or not g_view_panel:
            return

        # 获取通道下拉菜单组件
        channel_dropdown = None
        for widget in g_view_panel.widgets:
            if widget.get_label() == "selected_channels@dropdown":
                channel_dropdown = widget
                break

        if channel_dropdown:
            # 保存当前选择的值和回调函数
            current_value = channel_dropdown.get_value()
            original_callback = channel_dropdown.callback

            # 完全禁用回调（包括内部逻辑）
            channel_dropdown.callback = None

            # 临时保存 update_options 方法，替换为不触发回调的版本
            original_update_options = channel_dropdown.update_options

            def silent_update_options(new_options, new_default=None):
                """不触发回调的 update_options 版本"""
                # 处理新选项
                if isinstance(new_options, dict):
                    channel_dropdown.display_options = list(new_options.keys())
                    channel_dropdown.option_values = new_options
                elif isinstance(new_options, list):
                    channel_dropdown.display_options = new_options
                    channel_dropdown.option_values = {
                        opt: opt for opt in new_options}

                # 更新下拉菜单的值列表
                channel_dropdown.dropdown['values'] = channel_dropdown.display_options
                channel_dropdown._update_dropdown_width()

                # 确定要设置的值
                if new_default is not None:
                    target_value = new_default
                elif current_value in channel_dropdown.option_values.values():
                    target_value = current_value
                elif channel_dropdown.display_options:
                    target_value = list(
                        channel_dropdown.option_values.values())[0]
                else:
                    target_value = None

                # 设置新值（不触发回调）
                if target_value is not None:
                    channel_dropdown.set_value(target_value)

            # 替换方法
            channel_dropdown.update_options = silent_update_options

            # 创建通道选项字典
            channel_options = {"所有通道": "all"}  # 添加"显示所有通道"选项
            for i, name in enumerate(self.current_record.channel_names):
                channel_options[f"通道 {i}: {name}"] = i

            # 更新下拉菜单选项（此时不会触发回调）
            if current_value in channel_options.values():
                channel_dropdown.update_options(channel_options, current_value)
            else:
                # 如果当前值不在新选项中，默认选择"all"
                channel_dropdown.update_options(channel_options, "all")

            # 恢复原始方法和回调函数
            channel_dropdown.update_options = original_update_options
            channel_dropdown.callback = original_callback

            print(f"✅ 通道下拉菜单已更新: {len(channel_options)} 个选项（包括'所有通道'）")


def update_frequency_analyzer_ui(values: Dict[str, Any]):
    """频率响应分析器UI回调函数"""
    global freq_analyzer

    print(f"📊 频响分析器UI更新: {list(values.keys())}")

    # 标记是否需要重新绘图
    should_plot = False

    # 检查是否加载了输入文件
    if "input_wave_file@filepath" in values:
        filepath = values.get("input_wave_file@filepath")
        if filepath and filepath.strip():
            print(f"📂 加载输入波形文件: {filepath}")
            if freq_analyzer.load_input_wave_file(filepath):
                # 更新输入通道下拉菜单
                update_input_channel_dropdown()

    # 检查是否加载了输出文件
    if "output_wave_file@filepath" in values:
        filepath = values.get("output_wave_file@filepath")
        if filepath and filepath.strip():
            print(f"📂 加载输出波形文件: {filepath}")
            if freq_analyzer.load_output_wave_file(filepath):
                # 更新输出通道下拉菜单
                update_output_channel_dropdown()

    # 检查是否点击了分析按钮
    if values.get("analyze@button", False):
        print("🔍 开始频率响应分析")
        # 获取选择的通道索引
        input_channel = values.get("input_channel@dropdown", 0)
        output_channel = values.get("output_channel@dropdown", 0)

        # 确保通道索引是整数
        if isinstance(input_channel, str) and input_channel.isdigit():
            input_channel = int(input_channel)
        elif not isinstance(input_channel, int):
            input_channel = 0

        if isinstance(output_channel, str) and output_channel.isdigit():
            output_channel = int(output_channel)
        elif not isinstance(output_channel, int):
            output_channel = 0

        if freq_analyzer.analyze_frequency_response(
            input_channel_index=input_channel,
            output_channel_index=output_channel
        ):
            # 分析完成后自动绘图
            should_plot = True

    # 检查绘图选项是否改变，如果有可用的分析结果则重新绘图
    if ("plot_type@dropdown" in values.get("@on_change", {}) or
            "show_phase" in values.get("@on_change", {})):
        if freq_analyzer.systems:  # 只有在有分析结果时才绘图
            should_plot = True
            print("🎨 绘图选项已更改，自动重新绘制")

    # 如果需要绘图，则执行绘图
    if should_plot and freq_analyzer.systems:
        print("📈 自动绘制频率响应图")
        plot_type = values.get("plot_type@dropdown", "both")
        freq_analyzer.plot_frequency_response(
            plot_type=plot_type,
        )    # 检查是否点击了导出按钮
    if values.get("export@button", False):
        print("💾 导出频率响应数据")
        export_path = values.get("export_path@filepath")

        if export_path:
            freq_analyzer.export_frequency_response(export_path)
        else:
            # 如果没有指定路径，使用文件对话框
            filepath = filedialog.asksaveasfilename(
                title="导出频率响应数据",
                defaultextension=".csv",
                filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
            )
            if filepath:
                freq_analyzer.export_frequency_response(filepath)


def update_input_channel_dropdown():
    """更新频响分析器的输入通道选择下拉菜单"""
    if not g_fr_panel or not freq_analyzer:
        return

    # 查找输入通道下拉菜单组件
    input_channel_dropdown = None
    for widget in g_fr_panel.widgets:
        if widget.get_label() == "input_channel@dropdown":
            input_channel_dropdown = widget
            break

    if input_channel_dropdown:
        # 获取输入通道信息
        channel_info = freq_analyzer.get_input_channel_info()
        if channel_info:
            # 创建通道选项字典
            channel_options = {}
            for name, index in channel_info:
                channel_options[name] = index

            # 更新下拉菜单选项
            input_channel_dropdown.update_options(channel_options)
            print(f"✅ 输入通道下拉菜单已更新: {len(channel_options)} 个通道")
        else:
            # 如果没有通道信息，设置默认选项
            input_channel_dropdown.update_options({"请先选择输入文件": 0})


def update_output_channel_dropdown():
    """更新频响分析器的输出通道选择下拉菜单"""
    if not g_fr_panel or not freq_analyzer:
        return

    # 查找输出通道下拉菜单组件
    output_channel_dropdown = None
    for widget in g_fr_panel.widgets:
        if widget.get_label() == "output_channel@dropdown":
            output_channel_dropdown = widget
            break

    if output_channel_dropdown:
        # 获取输出通道信息
        channel_info = freq_analyzer.get_output_channel_info()
        if channel_info:
            # 创建通道选项字典
            channel_options = {}
            for name, index in channel_info:
                channel_options[name] = index

            # 更新下拉菜单选项
            output_channel_dropdown.update_options(channel_options)
            print(f"✅ 输出通道下拉菜单已更新: {len(channel_options)} 个通道")
        else:
            # 如果没有通道信息，设置默认选项
            output_channel_dropdown.update_options({"请先选择输出文件": 0})


def update_channel_dropdown_for_freq_analyzer(channel_count: int):
    """更新频响分析器的通道选择下拉菜单"""
    if not g_fr_panel:
        return

    # 查找通道下拉菜单组件
    channel_dropdown = None
    for widget in g_fr_panel.widgets:
        if widget.get_label() == "channel_index@dropdown":
            channel_dropdown = widget
            break

    if channel_dropdown:
        # 创建通道选项字典
        channel_options = {}
        for i in range(channel_count):
            channel_options[f"通道 {i}"] = i

        # 更新下拉菜单选项
        channel_dropdown.update_options(channel_options)
        print(f"✅ 频响分析器通道下拉菜单已更新: {channel_count} 个通道")


def update_ui(values: Dict[str, Any]):
    """UI回调函数，处理UI交互"""
    global viewer

    print(f"📊 UI更新: {list(values.keys())}")

    # 获取显示选项
    show_grid = values.get("show_grid", True)
    show_legend = values.get("show_legend", True)

    print(f"🎛️ 显示选项 - 网格: {show_grid}, 图例: {show_legend}")

    # 检查是否选择了文件
    if "wave_file@filepath" in values["@on_change"]:
        filepath = values.get("wave_file@filepath")
        if filepath and filepath.strip():
            print(f"📂 尝试加载文件: {filepath}")
            if viewer.load_wave_file(filepath):
                print("✅ 文件加载成功")
                # 文件加载成功后，更新记录和通道下拉菜单
                viewer.update_record_dropdown()
                viewer.update_channel_dropdown()
                # 绘制默认视图（所有通道）
                viewer.plot_record(show_grid=show_grid,
                                   show_legend=show_legend)
            else:
                print("❌ 文件加载失败")    # 检查是否选择了不同的记录
    if "record_id@dropdown" in values["@on_change"]:
        record_id = values.get("record_id@dropdown")
        if record_id and viewer.set_current_record(record_id):
            print(f"🔄 切换到记录: {record_id}")
            # 记录切换后，更新通道下拉菜单
            viewer.update_channel_dropdown()
            # 注意：不在这里立即绘制，避免与通道选择事件冲突
            # 绘制将由后续的通道选择逻辑或显示选项逻辑处理

    # 检查是否选择了不同的通道
    if "selected_channels@dropdown" in values["@on_change"]:
        selected_channels = values.get("selected_channels@dropdown")
        print(f"🎛️ 选择通道: {selected_channels}")

        if selected_channels == "all":
            # 显示所有通道
            viewer.plot_record(show_grid=show_grid, show_legend=show_legend)
        elif isinstance(selected_channels, int):
            # 显示指定的单个通道
            viewer.plot_record([selected_channels],
                               show_grid=show_grid, show_legend=show_legend)

    # 检查显示选项是否发生变化
    if "show_grid" in values["@on_change"] or "show_legend" in values["@on_change"]:
        print("🎨 显示选项已更改，重新绘制图表")
        if viewer.current_record:
            selected_channels = values.get("selected_channels@dropdown")
            if selected_channels == "all" or selected_channels is None:
                viewer.plot_record(show_grid=show_grid,
                                   show_legend=show_legend)
            else:
                viewer.plot_record(
                    [selected_channels], show_grid=show_grid, show_legend=show_legend)    # 检查是否点击了刷新按钮
    if values.get("refresh@button", False):
        print("🔄 刷新视图")
        if viewer.current_record:
            selected_channels = values.get("selected_channels@dropdown")
            if selected_channels == "all" or selected_channels is None:
                viewer.plot_record(show_grid=show_grid,
                                   show_legend=show_legend)
            else:
                viewer.plot_record(
                    [selected_channels], show_grid=show_grid, show_legend=show_legend)

    # 最终检查：如果记录切换了但没有其他UI变化触发绘制，则主动绘制
    if "record_id@dropdown" in values["@on_change"] and viewer.current_record:
        print("🎨 记录切换后主动绘制")
        selected_channels = values.get("selected_channels@dropdown")
        if selected_channels == "all" or selected_channels is None:
            viewer.plot_record(show_grid=show_grid,
                               show_legend=show_legend)
        else:
            viewer.plot_record(
                [selected_channels], show_grid=show_grid, show_legend=show_legend)


def main():
    """主函数 - 创建双标签页界面"""
    global viewer, freq_analyzer, g_fr_panel, g_view_panel

    # 创建WaveViewer和FrequencyResponseAnalyzer实例
    viewer = WaveViewer()
    freq_analyzer = FrequencyResponseAnalyzer()

    # 定义波形查看器标签页的参数配置
    waveviewer_params = {
        # 文件选择
        "wave_file@filepath": "",

        # 记录选择下拉菜单（将动态更新）
        "record_id@dropdown": {
            "options": {"请先选择文件": ""},
            "default": ""
        },

        # 通道选择下拉菜单（将动态更新）
        "selected_channels@dropdown": {
            "options": {
                "所有通道": "all",
                "请先选择文件": ""
            },
            "default": "all"
        },

        # 显示选项
        "show_grid": True,
        "show_legend": True,

        # 操作按钮
        "refresh@button": False,
    }    # 定义频率响应分析器标签页的参数配置
    freq_analyzer_params = {
        # 文件选择
        "input_wave_file@filepath": "",
        "output_wave_file@filepath": "",

        # 通道选择
        "input_channel@dropdown": {
            "options": {"请先选择输入文件": 0},
            "default": 0
        },

        "output_channel@dropdown": {
            "options": {"请先选择输出文件": 0},
            "default": 0
        },        # 分析选项
        "analyze@button": False,

        # 绘图选项
        "plot_type@dropdown": {
            "options": {
                "幅度和相位": "both",
                "仅幅度": "magnitude",
                "仅相位": "phase"
            },
            "default": "both"
        },

        # 操作按钮（去掉plot按钮，绘图将自动触发）
        "export@button": False,
        "export_path@filepath": "",
    }

    # 创建波形查看器标签页（主标签页）
    g_view_panel = Panel(
        waveviewer_params,
        update_ui,
        name="Wave查看器",
        redirect_stdout=True,
        with_plot=True,
        first_update=False
    )    # 创建频率响应分析器标签页
    g_fr_panel = Panel(
        freq_analyzer_params,
        update_frequency_analyzer_ui,
        name="频响分析器",
        redirect_stdout=True,
        with_plot=True,
        first_update=False
    )

    # 保存面板引用
    freq_analyzer.panel = g_fr_panel

    # 启动主循环（只需要调用一次，因为使用的是同一个主窗口）
    g_view_panel.on_widget_change(first_init=True)
    g_view_panel.mainloop()


if __name__ == "__main__":
    main()
