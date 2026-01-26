"""
waveprocessor 这个模块主要是用于处理扫频波形文件的，主要包括以下几个功能：
1. 对 System 进行仿真，生成扫频波形文件，参考 generate_sin_response
2. 读取扫频波形文件，计算频响，参考 process_frequency_response
3. 处理过程参考 exam_class 的 simulate_frequency 函数，这个函数是对每个频点进行时域仿真，然后立刻计算频率响应（单频点），本模块的不同之处在于，是对多频点进行时域仿真得到 WaveData 对象，保存整个 WaveData 到文件，然后再从文件加载 WaveData 对象，最后计算频率响应。
4. 支持文件加载 WaveData 对象进行频率响应分析的功能，这个功能是因为 WaveData 对象的生成可能是由其他软件，例如 SPICE。

需要进行的测试，将测试写在 __main__ 中：

1. 创建一个 symbel system，然后扫频生成扫频波形，保存为扫频波形文件。
2. 读取扫频波形文件，然后对扫频波形文件进行频率响应分析。
3. 绘制频率响应分析的结果，对比理想频响和扫频波形文件的分析结果。
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional, Dict, Any, Union
import os
from calibration_analyzer.exam_class import TimeSeries, System
from calibration_analyzer.wavedata import WaveData, WaveRecord


class WaveProcessor:
    """
    扫频波形处理器类
    用于系统扫频仿真、波形文件的生成与加载、频响分析等
    """

    def __init__(self):
        """初始化波形处理器"""
        self.wave_data = None

    def save_waveform(self, filepath: str, wave_data: Optional[WaveData] = None, compress: bool = True):
        """
        保存波形数据到文件

        参数:
            filepath: 保存路径
            wave_data: 要保存的波形数据对象，如果为None则使用当前对象中的wave_data
            compress: 是否压缩文件
        """
        if wave_data is None:
            wave_data = self.wave_data

        if wave_data is None:
            raise ValueError("没有可保存的波形数据")

        wave_data.save(filepath, compress=compress)
        # print(f"波形数据已保存到: {filepath}")

    def load_waveform(self, filepath: str) -> WaveData:
        """
        从文件加载波形数据

        参数:
            filepath: 文件路径

        返回:
            WaveData: 加载的波形数据对象
        """
        wave_data = WaveData.load(filepath)
        self.wave_data = wave_data
        return wave_data

    def plot_frequency_response(self,
                                frequencies: List[float],
                                gains: List[float],
                                phases: List[float],
                                title: str = "频率响应分析",
                                save_path: Optional[str] = None):
        """
        绘制频率响应图

        参数:
            frequencies: 频率点列表
            gains: 增益列表
            phases: 相位列表
            title: 图表标题
            save_path: 图表保存路径，如果为None则不保存
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))

        # 绘制增益响应
        ax1.loglog(frequencies, gains, 'b-', marker='.')
        ax1.set_xlabel('Frequency (Hz)')
        ax1.set_ylabel('Gain')
        ax1.set_title(f'{title} - 增益响应')
        ax1.grid(True, which="both", ls="--")

        # 绘制相位响应
        ax2.semilogx(frequencies, phases, 'r-', marker='.')
        ax2.set_xlabel('Frequency (Hz)')
        ax2.set_ylabel('Phase (degrees)')
        ax2.set_title(f'{title} - 相位响应')
        ax2.grid(True, which="both", ls="--")

        plt.tight_layout()

    def generate_sweep_input_waveform(self,
                                      freq_range,
                                      amplitude=1.0,
                                      fs=44100,
                                      time_length=0.1,
                                      min_periods=4,
                                      max_periods=10,
                                      description=None,
                                      output_file_path=None) -> WaveData:
        """
        根据扫频配置生成扫频输入波形的波形文件

        参数:
            freq_range: 频率点列表 [Hz]
            amplitude: 输入信号幅值
            fs: 采样率 [Hz]
            time_length: 每个频点的信号持续时间 [s]
            min_periods: 最小周期数
            max_periods: 最大周期数
            description: 波形文件描述
            output_file_path: 输出波形文件路径

        返回:
            WaveData: 包含扫频输入波形的WaveData对象
        """
        # 创建波形数据对象
        wave_data = WaveData(
            description=description or f"扫频输入波形 - 频率范围: {min(freq_range)}-{max(freq_range)}Hz",
            author="Sweep Generator"
        )

        # 循环处理每个频点
        for freq in freq_range:
            # 计算周期并调整信号长度
            period_time = 1 / freq
            num_periods = max(min_periods, int(time_length * freq))
            num_periods = min(max_periods, num_periods)
            adjusted_time_length = num_periods * period_time

            # 生成时间向量和正弦波信号
            t = np.arange(0, adjusted_time_length, 1/fs)
            input_signal = amplitude * np.sin(2 * np.pi * freq * t)

            # 创建记录数据
            record_data = input_signal.reshape(-1, 1)  # 只有一个通道，输入信号

            # 创建WaveRecord对象
            record = WaveRecord(
                data=record_data,
                sample_rate=fs,
                channel_names=["Input"],
                units="V",
                user_metadata={"frequency": freq}
            )

            # 添加记录到波形数据
            wave_data.add_record(record)

        # 添加元数据
        wave_data.add_user_metadata("type", "input_sweep")
        wave_data.add_user_metadata("amplitude", amplitude)
        wave_data.add_user_metadata(
            "freq_range", [float(f) for f in freq_range])
        # 添加处理记录到元数据
        process_record = {
            "operation": "generate_sweep_input_waveform",
            "timestamp": np.datetime64('now').astype(str),
            "parameters": {
                "amplitude": amplitude,
                "fs": fs,
                "time_length": time_length,
                "min_periods": min_periods,
                "max_periods": max_periods,
                "freq_range": [float(f) for f in freq_range],
                "total_freq_points": len(freq_range)
            },
            "source_info": {
                "function": "generate_sweep_input_waveform",
                "file_path": output_file_path or "未指定路径",
                "description": description
            }
        }

        # 初始化处理记录列表，如果不存在
        if "process_history" not in wave_data.user_metadata:
            wave_data.add_user_metadata("process_history", [])

        # 添加当前处理记录到历史列表
        process_history = wave_data.user_metadata["process_history"]
        process_history.append(process_record)
        wave_data.add_user_metadata("process_history", process_history)

        return wave_data

    def analyze_sweep_response(self,
                               input_wave_data: Union[WaveData, str],
                               output_wave_data: Union[WaveData, str],
                               input_channel_index: int = 0,
                               output_channel_index: int = 0) -> System:
        """
        分析输入和输出波形文件，计算频率响应

        参数:
            input_wave_data: 输入波形数据或波形文件路径
            output_wave_data: 输出波形数据或波形文件路径
            input_channel_index: 输入通道索引，默认为0
            output_channel_index: 输出通道索引，默认为0

        返回:
            System: 分析得到的频率响应系统对象
        """
        # 如果输入是路径，加载波形文件
        if isinstance(input_wave_data, str):
            processor = WaveProcessor()
            input_wave_data = processor.load_waveform(input_wave_data)

        # 如果输出是路径，加载波形文件
        if isinstance(output_wave_data, str):
            processor = WaveProcessor()
            output_wave_data = processor.load_waveform(output_wave_data)

        if input_wave_data is None or output_wave_data is None:
            raise ValueError("缺少输入或输出波形数据")

        # 检查记录数量是否一致
        if len(input_wave_data.records) != len(output_wave_data.records):
            raise ValueError("输入和输出波形记录数量不一致")

        # 检查通道索引是否有效
        num_input_channels = input_wave_data.records[0].num_channels
        num_output_channels = output_wave_data.records[0].num_channels

        if input_channel_index >= num_input_channels:
            raise ValueError(
                f"输入通道索引 {input_channel_index} 超出范围（可用通道：0-{num_input_channels-1}）")

        if output_channel_index >= num_output_channels:
            raise ValueError(
                f"输出通道索引 {output_channel_index} 超出范围（可用通道：0-{num_output_channels-1}）")

        frequencies = []
        inputs = []
        outputs = []

        # 处理每个记录（每个频点）
        for in_rec, out_rec in zip(input_wave_data.records, output_wave_data.records):
            # 检查频率信息是否一致
            in_freq = in_rec.user_metadata.get("frequency")
            out_freq = out_rec.user_metadata.get("frequency")

            if in_freq is None or out_freq is None:
                raise ValueError(f"记录缺少频率信息")

            if in_freq != out_freq:
                raise ValueError(
                    f"输入和输出频率不匹配: {in_freq} Hz vs {out_freq} Hz")

            # 获取指定通道的输入和输出信号
            input_data = in_rec.get_channel(input_channel_index)
            output_data = out_rec.get_channel(output_channel_index)

            # 创建TimeSeries对象
            input_sequence = TimeSeries(input_data, in_rec.sample_rate)
            output_sequence = TimeSeries(output_data, out_rec.sample_rate)
            inputs.append(input_sequence)
            outputs.append(output_sequence)
            frequencies.append(in_freq)

        # 从TimeSeries创建System对象
        system = System.fromTimeSeries(inputs, outputs, frequencies)

        return system

    def analyze_multi_magnitudes_sweep_response(self,
                                               input_wave_data: Union[WaveData, str],
                                               output_wave_data: Union[WaveData, str],
                                               input_channel_index: int = 0,
                                               output_channel_index: int = 0) -> Tuple[List[float], List[System]]:
        """
        分析包含多个震级的输入和输出波形文件，按震级分组计算频率响应

        参数:
            input_wave_data: 输入波形数据或波形文件路径
            output_wave_data: 输出波形数据或波形文件路径
            input_channel_index: 输入通道索引，默认为0
            output_channel_index: 输出通道索引，默认为0

        返回:
            Tuple[List[float], List[System]]: 震级列表和对应的System对象列表，顺序一一对应
        """
        # 如果输入是路径，加载波形文件
        if isinstance(input_wave_data, str):
            processor = WaveProcessor()
            input_wave_data = processor.load_waveform(input_wave_data)

        # 如果输出是路径，加载波形文件
        if isinstance(output_wave_data, str):
            processor = WaveProcessor()
            output_wave_data = processor.load_waveform(output_wave_data)

        if input_wave_data is None or output_wave_data is None:
            raise ValueError("缺少输入或输出波形数据")

        # 检查记录数量是否一致
        if len(input_wave_data.records) != len(output_wave_data.records):
            raise ValueError("输入和输出波形记录数量不一致")

        # 分析输入波形中包含的震级
        input_amplitudes = set()
        for record in input_wave_data.records:
            amplitude = record.user_metadata.get("magnitude")
            if amplitude is None:
                raise ValueError(
                    f"输入记录 '{record.record_id}' 缺少震级(magnitude)信息")
            input_amplitudes.add(float(amplitude))

        # 分析输出波形中包含的震级
        output_amplitudes = set()
        for record in output_wave_data.records:
            amplitude = record.user_metadata.get("magnitude")
            if amplitude is None:
                raise ValueError(
                    f"输出记录 '{record.record_id}' 缺少震级(magnitude)信息")
            output_amplitudes.add(float(amplitude))

        # 核对输入和输出中的震级是否一致
        if input_amplitudes != output_amplitudes:
            missing_in_output = input_amplitudes - output_amplitudes
            missing_in_input = output_amplitudes - input_amplitudes
            error_msg = "输入和输出波形中的震级不一致："
            if missing_in_output:
                error_msg += f"\n输出中缺少震级: {sorted(missing_in_output)}"
            if missing_in_input:
                error_msg += f"\n输入中缺少震级: {sorted(missing_in_input)}"
            raise ValueError(error_msg)

        # 按震级排序
        amplitudes = sorted(list(input_amplitudes))
        systems = []

        print(f"发现 {len(amplitudes)} 个不同的震级: {amplitudes}")

        # 对每个震级进行分析
        for amplitude in amplitudes:
            print(f"正在分析震级 {amplitude} 的频率响应...")

            # 使用filter方法筛选相同震级的记录
            input_filtered = input_wave_data.filter(
                lambda rec: abs(float(rec.user_metadata.get(
                    "magnitude", 0)) - amplitude) < 1e-10
            )
            output_filtered = output_wave_data.filter(
                lambda rec: abs(float(rec.user_metadata.get(
                    "magnitude", 0)) - amplitude) < 1e-10
            )

            # 检查过滤后的记录数量是否一致
            if len(input_filtered.records) != len(output_filtered.records):
                raise ValueError(
                    f"震级 {amplitude} 的输入和输出记录数量不一致: "
                    f"输入 {len(input_filtered.records)} 个，输出 {len(output_filtered.records)} 个"
                )

            if len(input_filtered.records) == 0:
                raise ValueError(f"震级 {amplitude} 没有找到任何记录")

            # 对同震级调用analyze_sweep_response
            try:
                system = self.analyze_sweep_response(
                    input_wave_data=input_filtered,
                    output_wave_data=output_filtered,
                    input_channel_index=input_channel_index,
                    output_channel_index=output_channel_index
                )
                systems.append(system)
                print(
                    f"震级 {amplitude} 分析完成，包含 {len(input_filtered.records)} 个频率点")
            except Exception as e:
                raise ValueError(f"分析震级 {amplitude} 时发生错误: {str(e)}")

        print(f"多震级频率响应分析完成，共分析了 {len(amplitudes)} 个震级")
        return amplitudes, systems


# 测试代码
if __name__ == "__main__":
    # 导入所需模块

    # 创建一个简单的符号系统进行测试
    s = System.s

    # 创建一个二阶低通滤波器系统
    def create_test_system(freqs):
        # 系统参数
        fc = 10  # 截止频率，Hz
        Q = 0.707   # 品质因数

        # 转换为角频率
        wc = 2 * np.pi * fc

        # 创建系统
        system = System.fromSymbol(s**2/(s**2 + (wc/Q)*s + wc**2), f=freqs)

        return system

    def run_test():
        print("开始WaveProcessor测试...")
        freqs = np.logspace(np.math.log10(
            10), np.math.log10(200), 100)  # 10Hz到200Hz，100个点

        # 1. 创建测试系统
        system_ideal = create_test_system(freqs=freqs)
        print("已创建测试系统: 二阶低通滤波器")

        # 创建波形处理器
        processor = WaveProcessor()

        # 2. 生成输入扫频波形
        print("生成扫频输入波形...")
        input_file = "sweep_test_input.wave"
        input_wave_data = processor.generate_sweep_input_waveform(
            freq_range=freqs,
            amplitude=1.0,
            fs=2000,
            time_length=0.5,  # 较短的时间以加快测试
            min_periods=4,
            max_periods=10,
            description="二阶低通滤波器测试输入扫频波形",
            output_file_path=input_file
        )
        # 保存输入波形文件
        print(f"保存输入波形到文件: {input_file}")
        processor.save_waveform(input_file, input_wave_data)

        # 3. 使用理想系统生成输出波形并保存
        print("使用理想系统生成输出波形...")
        output_file = "sweep_test_output.wave"
        output_wave_data = WaveData(
            description="二阶低通滤波器测试输出扫频波形",
            author="Sweep Generator"
        )
        # 遍历每个频点，生成对应响应
        for i, record in enumerate(input_wave_data.records):
            input_tr = record.to_time_series(0)
            output_tr = system_ideal.time_response(input_tr)
            wave_record = WaveRecord.from_time_series(output_tr)
            output_wave_data.add_record(wave_record)
            output_wave_data.records[i].user_metadata = record.user_metadata
            output_wave_data.records[i].user_metadata["frequency"] = record.user_metadata["frequency"]

        # 保存输出波形文件
        print(f"保存输出波形到文件: {output_file}")
        processor.save_waveform(output_file, output_wave_data)

        # 4. 加载波形文件
        print("从文件加载波形...")
        input_wave_loaded = processor.load_waveform(input_file)
        output_wave_loaded = processor.load_waveform(output_file)
        print(
            f"已加载波形文件，输入包含 {len(input_wave_loaded.records)} 个记录，输出包含 {len(output_wave_loaded.records)} 个记录")

        # 5. 分析频响
        print("分析频率响应...")
        system_test = processor.analyze_sweep_response(
            input_wave_data=input_wave_loaded,
            output_wave_data=output_wave_loaded
        )
        print(f"分析完成，得到 {len(freqs)} 个频率点的响应")

        # 6. 绘制结果并与理想系统对比
        print("绘制对比图...")
        system_ideal.plot(label="理想系统")
        system_test.plot(label="分析系统")
        plt.legend()

        print("测试完成!")        # 删除生成的文件
        if os.path.exists(input_file):
            os.remove(input_file)
            print(f"已删除测试文件: {input_file}")

        if os.path.exists(output_file):
            os.remove(output_file)
            print(f"已删除测试文件: {output_file}")

    def test_multi_amplitude():
        """测试多震级频率响应分析功能"""
        print("\n开始多震级WaveProcessor测试...")

        # 测试频率范围
        freqs = np.logspace(np.math.log10(
            10), np.math.log10(200), 20)  # 更少的频点以加快测试
        amplitudes = [0.5, 1.0, 2.0]  # 三个不同的震级

        # 创建测试系统
        system_ideal = create_test_system(freqs=freqs)
        processor = WaveProcessor()

        # 为每个震级生成输入和输出波形
        all_input_records = []
        all_output_records = []

        for amp in amplitudes:
            print(f"生成震级 {amp} 的波形数据...")

            # 生成输入波形
            for freq in freqs:
                # 生成正弦波信号
                fs = 2000
                time_length = 0.5
                t = np.arange(0, time_length, 1/fs)
                input_signal = amp * np.sin(2 * np.pi * freq * t)

                # 创建输入记录
                input_record = WaveRecord(
                    data=input_signal.reshape(-1, 1),
                    sample_rate=fs,
                    channel_names=["Input"],
                    units="V",
                    user_metadata={"frequency": freq, "magnitude": amp}
                )
                all_input_records.append(input_record)

                # 使用理想系统生成输出
                input_ts = TimeSeries(input_signal, fs)
                output_ts = system_ideal.time_response(input_ts)

                # 创建输出记录
                output_record = WaveRecord(
                    data=output_ts.samples.reshape(-1, 1),
                    sample_rate=fs,
                    channel_names=["Output"],
                    units="V",
                    user_metadata={"frequency": freq, "magnitude": amp}
                )
                all_output_records.append(output_record)

        # 创建包含所有震级的波形数据
        input_wave_data = WaveData(
            description="多震级测试输入波形",
            author="Test Generator"
        )
        output_wave_data = WaveData(
            description="多震级测试输出波形",
            author="Test Generator"
        )

        for record in all_input_records:
            input_wave_data.add_record(record)
        for record in all_output_records:
            output_wave_data.add_record(record)

        print(
            f"创建了包含 {len(all_input_records)} 个输入记录和 {len(all_output_records)} 个输出记录的波形数据")

        # 测试多震级分析
        try:
            amplitudes_result, systems_result = processor.analyze_multi_magnitudes_sweep_response(
                input_wave_data=input_wave_data,
                output_wave_data=output_wave_data
            )

            print(f"多震级分析成功！")
            print(f"发现震级: {amplitudes_result}")
            print(f"生成了 {len(systems_result)} 个System对象")

            # 绘制不同震级的频率响应
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

            # 绘制理想系统作为参考
            ideal_gains = system_ideal.toabs()
            ideal_phases = system_ideal.tophase()
            ax1.loglog(freqs, ideal_gains, 'k--', label='理想系统', linewidth=2)
            ax2.semilogx(freqs, ideal_phases, 'k--', label='理想系统', linewidth=2)

            # 绘制每个震级的结果
            colors = ['r', 'g', 'b', 'm', 'c']
            for i, (amp, system) in enumerate(zip(amplitudes_result, systems_result)):
                gains = system.toabs()
                phases = system.tophase()
                color = colors[i % len(colors)]

                ax1.loglog(system.f, gains, color=color,
                           marker='o', label=f'震级 {amp}')
                ax2.semilogx(system.f, phases, color=color,
                             marker='o', label=f'震级 {amp}')

            ax1.set_xlabel('频率 (Hz)')
            ax1.set_ylabel('增益')
            ax1.set_title('多震级频率响应分析 - 增益')
            ax1.grid(True, which="both", ls="--")
            ax1.legend()

            ax2.set_xlabel('频率 (Hz)')
            ax2.set_ylabel('相位 (degrees)')
            ax2.set_title('多震级频率响应分析 - 相位')
            ax2.grid(True, which="both", ls="--")
            ax2.legend()

            plt.tight_layout()
            print("多震级测试完成!")

        except Exception as e:
            print(f"多震级测试失败: {str(e)}")
            import traceback
            traceback.print_exc()

    # 执行测试
    run_test()
    test_multi_amplitude()
    plt.show()
