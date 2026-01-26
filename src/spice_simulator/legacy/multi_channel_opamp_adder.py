import numpy as np
import matplotlib.pyplot as plt
from spicelib.sim.sim_runner import SimRunner
from spicelib.editor.spice_editor import SpiceEditor
from spicelib.simulators.ngspice_simulator import NGspiceSimulator
from spicelib import RawRead
import tempfile
import os
from pathlib import Path
from scipy.interpolate import interp1d
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from abc import ABC, abstractmethod


class BaseCircuit(ABC):
    """电路基类，定义了电路接口"""
    
    @abstractmethod
    def get_circuit_netlist(self):
        """获取电路的网表文本(不包含仿真指令)"""
        pass
    
    @abstractmethod
    def simulate_numpy(self, t, input_signals):
        """
        使用NumPy进行理论仿真计算
        
        参数:
            t: 时间向量
            input_signals: 输入信号
            
        返回:
            np.ndarray: 输出信号
        """
        pass
    
    def get_input_source_names(self):
        """
        获取输入源的名称列表
        
        返回:
            list: 输入源名称列表，用于设置PWL数据
        """
        # 默认实现：假设输入源名称格式为'Vin1', 'Vin2', ...
        if hasattr(self, 'n_channels') and self.n_channels > 0:
            return [f'Vin{i+1}' for i in range(self.n_channels)]
        return ['Vin1']  # 默认至少返回一个输入源
    
    def get_output_node_name(self):
        """
        获取输出节点名称
        
        返回:
            str: 输出节点名称，用于从仿真结果中提取输出波形
        """
        # 默认实现：假设输出节点名称为'out'
        return 'out'


class OpAmpAdderCircuit(BaseCircuit):
    """运放加法器电路类，封装电路的网表和增益等属性"""
    
    def __init__(self, n_channels, gains=None, R_values=None):
        """
        初始化运放加法器电路
        
        参数:
            n_channels: 通道数量
            gains: 各通道增益列表，默认为None（所有通道增益为1）
            R_values: 电阻基准值，默认为None（使用10kΩ作为基准值）
        """
        self.n_channels = n_channels
        
        # 处理增益
        if gains is None:
            self.gains = [1.0] * n_channels
        else:
            self.gains = gains.copy() if isinstance(gains, list) else gains
            # 扩展增益列表到n_channels
            if len(self.gains) < n_channels:
                self.gains = self.gains + [1.0] * (n_channels - len(self.gains))
        
        # 处理电阻值
        if R_values is None:
            self.R_base = 10e3  # 10kΩ作为基准电阻值
            self.RF = self.R_base
            self.R_channels = [self.R_base / gain if gain != 0 else 1e9 for gain in self.gains]
            self.R_channels = [max(R, 10) for R in self.R_channels]  # 确保最小电阻值不小于10Ω
        else:
            self.RF = R_values.get('RF', 10e3)
            self.R_channels = R_values.get('R_channels', [10e3] * n_channels)
        
        # 生成电路网表文本(不包含仿真指令)
        self.netlist_text = self._create_circuit_netlist()
    
    def _create_circuit_netlist(self):
        """
        创建多通道运放加法器电路网表(仅包含电路部分，不包含仿真指令)
        
        返回:
            str: 电路网表内容
        """
        # 创建网表文本
        netlist_text = f"""* Multi-Channel Op-Amp Adder Circuit - NGspice Simulation
* Using ideal op-amp model with {self.n_channels} input channels

* Power Supply
Vcc vcc 0 15
Vee vee 0 -15

* Define input voltage sources (will be replaced with PWL data)
"""
        
        # 添加电压源定义
        for i in range(self.n_channels):
            netlist_text += f"Vin{i+1} in{i+1} 0 0\n"
        
        netlist_text += "\n* Op-Amp adder circuit\n"
        
        # 添加输入电阻
        for i in range(self.n_channels):
            netlist_text += f"R{i+1} in{i+1} neg {self.R_channels[i]}\n"
        
        # 添加反馈电阻
        netlist_text += f"RF neg out {self.RF}\n"
        
        # 添加增强的理想运放模型
        netlist_text += """
* Enhanced ideal op-amp model
* 将正端接地，使用高增益比较反相和正相端的电压差
Eop out 0 pos neg 1e9
Rpos pos 0 1
* 添加极高阻抗的输入电阻以模拟理想运放
Rin neg pos 1e12
* 添加极小的输出电阻以增强驱动能力
Rout out 0 1e-6
"""
        return netlist_text
    
    def get_circuit_netlist(self):
        """获取电路的网表文本(不包含仿真指令)"""
        return self.netlist_text
    
    def simulate_numpy(self, t, input_signals):
        """
        使用NumPy进行运放加法器的理论仿真计算
        
        参数:
            t: 时间向量
            input_signals: 输入信号矩阵 [channels, time_steps]
            
        返回:
            np.ndarray: 输出信号
        """
        # 检查输入信号的通道数是否匹配
        if input_signals.shape[0] != self.n_channels:
            raise ValueError(f"输入信号通道数({input_signals.shape[0]})与电路通道数({self.n_channels})不匹配")
        
        # 计算理论输出（理想运放加法器）
        output = np.zeros_like(t)
        for i in range(self.n_channels):
            # 反相加法器，输出为负号
            output -= self.gains[i] * input_signals[i]
        
        return output
    
    def get_input_source_names(self):
        """
        获取输入源的名称列表
        
        返回:
            list: 输入源名称列表
        """
        return [f'Vin{i+1}' for i in range(self.n_channels)]
    
    def get_output_node_name(self):
        """
        获取输出节点名称
        
        返回:
            str: 输出节点名称
        """
        return 'out'


class RCLowPassCircuit(BaseCircuit):
    """RC低通滤波器电路类"""
    
    def __init__(self, R=10e3, C=1e-9):
        """
        初始化RC低通滤波器电路
        
        参数:
            R: 电阻值(欧姆)
            C: 电容值(法拉)
        """
        self.R = R
        self.C = C
        self.tau = R * C  # 时间常数
        
        # 生成电路网表
        self.netlist_text = self._create_circuit_netlist()
    
    def _create_circuit_netlist(self):
        """创建RC低通滤波器电路网表"""
        netlist_text = f"""* RC Low-Pass Filter Circuit - NGspice Simulation

* Input voltage source
Vin in 0 0

* RC filter components
R1 in out {self.R}
C1 out 0 {self.C}
"""
        return netlist_text
    
    def get_circuit_netlist(self):
        """获取电路的网表文本"""
        return self.netlist_text
    
    def simulate_numpy(self, t, input_signals):
        """
        使用NumPy进行RC低通滤波器的理论仿真计算
        
        参数:
            t: 时间向量
            input_signals: 输入信号矩阵 [1, time_steps] 或一维数组
            
        返回:
            np.ndarray: 输出信号
        """
        # 确保输入是单通道信号
        if input_signals.ndim > 1 and input_signals.shape[0] != 1:
            raise ValueError(f"RC低通滤波器只接受单通道输入，但收到{input_signals.shape[0]}通道")
        
        # 提取单通道信号
        if input_signals.ndim > 1:
            input_signal = input_signals[0]
        else:
            input_signal = input_signals
        
        # 计算时间步长
        dt = t[1] - t[0] if len(t) > 1 else 1e-6
        
        # 创建输出数组
        output = np.zeros_like(input_signal)
        
        # 使用数值积分模拟RC响应
        # 对于RC低通滤波器，差分方程：output[n] = alpha * output[n-1] + (1-alpha) * input[n]
        # 其中alpha = exp(-dt/tau)
        alpha = np.exp(-dt / self.tau)
        output[0] = input_signal[0]  # 初始值
        
        for i in range(1, len(t)):
            output[i] = alpha * output[i-1] + (1 - alpha) * input_signal[i]
        
        return output
    
    def get_input_source_names(self):
        """
        获取输入源的名称列表
        
        返回:
            list: 输入源名称列表
        """
        return ['Vin']  # RC滤波器只有一个输入源，名为Vin
    
    def get_output_node_name(self):
        """
        获取输出节点名称
        
        返回:
            str: 输出节点名称
        """
        return 'out'


class MultiChannelOpAmpAdderSimulation:
    """多通道运放加法器电路仿真类，支持任意多通道信号求和并进行批量仿真"""
    
    def __init__(self, output_folder='./temp', ngspice_path=None, max_workers=None):
        """
        初始化仿真类
        
        参数:
            output_folder: 输出文件夹路径
            ngspice_path: NGspice可执行文件路径，如果为None则使用默认路径
            max_workers: 并行仿真的最大线程数，默认为None（使用系统默认值）
        """
        self.output_folder = output_folder
        os.makedirs(output_folder, exist_ok=True)
        
        # 设置NGspice路径
        if ngspice_path is None:
            self.ngspice_path = r".\Spice64\bin\ngspice.exe"
        else:
            self.ngspice_path = ngspice_path
            
        # 检查NGspice路径是否存在
        if not os.path.exists(self.ngspice_path):
            raise FileNotFoundError(f"NGspice可执行文件未找到: {self.ngspice_path}")
            
        # 设置并行线程数
        self.max_workers = max_workers
        
        # 初始化结果变量
        self.results = {}
    
    def generate_input_signals(self, t_max=1e-3, fs=1e6, n_channels=2, freqs=None, amps=None):
        """
        生成多通道输入信号
        
        参数:
            t_max: 最大仿真时间(秒)
            fs: 采样频率(Hz)
            n_channels: 通道数量
            freqs: 各通道信号频率列表，默认为None（自动生成）
            amps: 各通道信号振幅列表，默认为None（自动生成）
            
        返回:
            tuple: (时间向量, 信号矩阵[channels, time_steps])
        """
        t = np.arange(0, t_max, 1/fs)
        
        # 如果未指定频率，则自动生成不同频率
        if freqs is None:
            freqs = [5e3 * (i + 1) for i in range(n_channels)]
        elif len(freqs) < n_channels:
            # 扩展频率列表到n_channels
            freqs = freqs + [5e3 * (i + 1) for i in range(len(freqs), n_channels)]
        
        # 如果未指定振幅，则使用标准振幅
        if amps is None:
            amps = [0.5 / n_channels] * n_channels
        elif len(amps) < n_channels:
            # 扩展振幅列表到n_channels
            amps = amps + [0.5 / n_channels] * (n_channels - len(amps))
        
        # 生成多通道信号
        signals = np.zeros((n_channels, len(t)))
        for i in range(n_channels):
            signals[i] = amps[i] * np.sin(2 * np.pi * freqs[i] * t)
        
        return t, signals
    
    def create_pwl_data(self, t, v, max_points=1000):
        """
        创建PWL数据字符串，用于替换电压源
        
        参数:
            t: 时间向量
            v: 电压向量
            max_points: 最大点数，用于减少数据量
            
        返回:
            str: PWL数据字符串
        """
        decimation = max(1, len(t) // max_points)
        pwl_data = "PWL("
        for i in range(0, len(t), decimation):
            pwl_data += f"{t[i]} {v[i]} "
        pwl_data += ")"
        return pwl_data
    
    def create_simulation_netlist(self, circuit, t_max=1e-3, t_step=1e-6, 
                                 additional_instructions=None):
        """
        创建完整的仿真网表，包括电路定义和仿真指令
        
        参数:
            circuit: BaseCircuit的子类实例，包含电路定义
            t_max: 最大仿真时间(秒)
            t_step: 仿真步长(秒)
            additional_instructions: 额外的仿真指令列表
            
        返回:
            str: 完整的仿真网表文本
        """
        # 获取电路网表
        netlist_text = circuit.get_circuit_netlist()
        
        # 添加仿真指令
        netlist_text += f"""
* Simulation settings
.tran {t_step} {t_max} 0 {t_step/10}
.save all
"""
        
        # 添加额外的仿真指令
        if additional_instructions:
            for instruction in additional_instructions:
                netlist_text += instruction + "\n"
        
        # 添加结束标记
        netlist_text += ".end\n"
        
        return netlist_text
    
    def run_simulation(self, t, signals, circuit, t_max=None, t_step=None, 
                      additional_instructions=None, print_netlist=False):
        """
        运行单次仿真
        
        参数:
            t: 时间向量
            signals: 信号矩阵 [channels, time_steps] 或一维数组
            circuit: BaseCircuit的子类实例，包含网表和仿真逻辑
            t_max: 最大仿真时间(秒)，如果为None则使用t的最大值
            t_step: 仿真步长(秒)，如果为None则自动计算
            additional_instructions: 额外的仿真指令列表
            print_netlist: 是否打印网表内容
            
        返回:
            dict: 包含仿真结果的字典
        """
        # 处理一维输入信号，转换为二维数组 [1, time_steps]
        if signals.ndim == 1:
            signals = np.array([signals])
            
        # 设置仿真参数
        if t_max is None:
            t_max = t[-1] - t[0]
        if t_step is None:
            # 自动计算步长：取时间向量中相邻点的最小间隔，或时间跨度的1/1000
            if len(t) > 1:
                min_step = min(np.diff(t))
                t_step = min(min_step, t_max / 1000)
            else:
                t_step = t_max / 1000
        
        # 创建完整仿真网表
        netlist_text = self.create_simulation_netlist(
            circuit, t_max, t_step, additional_instructions)
            
        # 创建临时网表文件
        with tempfile.NamedTemporaryFile(suffix='.net', delete=False, mode='w') as f:
            f.write(netlist_text)
            temp_netlist_path = f.name
        
        try:
            # 创建网表
            netlist = SpiceEditor(temp_netlist_path)
            
            if print_netlist:
                print("\n===== Netlist Content =====")
                print(netlist_text)
                print("=========================\n")
            
            # 获取输入源名称
            input_sources = circuit.get_input_source_names()
            
            # 确保输入源数量与信号通道数匹配
            if len(input_sources) != signals.shape[0]:
                if len(input_sources) == 1 and signals.shape[0] > 1:
                    # 特殊情况：单一输入源，多通道信号 - 将所有信号相加
                    combined_signal = np.sum(signals, axis=0)
                    netlist[input_sources[0]].model = self.create_pwl_data(t, combined_signal)
                else:
                    raise ValueError(f"输入源数量({len(input_sources)})与信号通道数({signals.shape[0]})不匹配")
            else:
                # 设置输入电压源为PWL数据
                for i, source_name in enumerate(input_sources):
                    netlist[source_name].model = self.create_pwl_data(t, signals[i])
            
            # 创建SimRunner实例
            runner = SimRunner(
                output_folder=self.output_folder,
                simulator=NGspiceSimulator.create_from(self.ngspice_path),
                verbose=False
            )
            
            # 运行NGspice仿真
            raw_file, log_file = runner.run_now(netlist, exe_log=True)
            
            # 读取NGspice仿真结果
            if raw_file and os.path.exists(str(raw_file)):
                raw_data = RawRead(raw_file)
                
                # 获取仿真数据
                time_spice = raw_data.get_trace('time').get_wave(0)
                
                # 获取输出节点名称
                output_node = circuit.get_output_node_name()
                v_out_spice = raw_data.get_trace(f'v({output_node})').get_wave(0)
                
                # 使用电路对象的方法进行NumPy理论计算
                v_out_numpy = circuit.simulate_numpy(t, signals)
                
                # 重采样NGspice数据到numpy的时间轴上进行比较
                f_interp = interp1d(time_spice, v_out_spice, kind='linear', bounds_error=False, fill_value=0)
                v_out_spice_resampled = f_interp(t)
                diff = v_out_numpy - v_out_spice_resampled
                
                # 计算统计信息
                max_diff = np.max(np.abs(diff))
                mean_diff = np.mean(np.abs(diff))
                
                # 返回结果
                result = {
                    'time': t,
                    'signals': signals,
                    'v_out_numpy': v_out_numpy,
                    'time_spice': time_spice,
                    'v_out_spice': v_out_spice,
                    'v_out_spice_resampled': v_out_spice_resampled,
                    'diff': diff,
                    'max_diff': max_diff,
                    'mean_diff': mean_diff
                }
                
                return result
            else:
                print("NGspice simulation failed - No raw file generated")
                if raw_file:
                    print(f"Expected raw file path: {raw_file}")
                return None
                
        except Exception as e:
            print(f"Error during simulation: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            # 清理临时文件
            if os.path.exists(temp_netlist_path):
                os.unlink(temp_netlist_path)
    
    def _run_batch_item(self, batch_idx, t, signals, circuit, t_max, t_step, additional_instructions):
        """
        运行单个批次的仿真（用于并行仿真）
        
        参数:
            batch_idx: 批次索引
            t: 时间向量
            signals: 信号矩阵 [channels, time_steps]
            circuit: BaseCircuit的子类实例，包含网表和仿真逻辑
            t_max: 最大仿真时间(秒)
            t_step: 仿真步长(秒)
            additional_instructions: 额外的仿真指令列表
            
        返回:
            tuple: (batch_idx, 仿真结果)
        """
        result = self.run_simulation(t, signals, circuit, t_max, t_step, additional_instructions)
        return batch_idx, result
    
    def run_batch_simulation(self, t, batch_signals, circuit, t_max=None, t_step=None, 
                           additional_instructions=None, progress_callback=None):
        """
        运行批量仿真
        
        参数:
            t: 时间向量 [time_steps]
            batch_signals: 批量信号矩阵 [batch_size, channels, time_steps] 或 [batch_size, time_steps, channels]
            circuit: BaseCircuit的子类实例，包含网表和仿真逻辑
            t_max: 最大仿真时间(秒)，如果为None则使用t的最大值
            t_step: 仿真步长(秒)，如果为None则自动计算
            additional_instructions: 额外的仿真指令列表
            progress_callback: 进度回调函数，接受一个0-1之间的浮点数表示进度
            
        返回:
            dict: 包含所有批次仿真结果的字典
        """
        # 处理输入维度，确保格式为 [batch_size, channels, time_steps]
        if batch_signals.ndim == 3:
            if batch_signals.shape[1] == len(t):  # 格式为 [batch_size, time_steps, channels]
                batch_signals = np.transpose(batch_signals, (0, 2, 1))
        elif batch_signals.ndim == 2:
            # 处理单通道情况，扩展为 [batch_size, 1, time_steps]
            batch_signals = np.expand_dims(batch_signals, 1)
        else:
            raise ValueError("batch_signals必须是2维或3维数组")
        
        batch_size = batch_signals.shape[0]
        
        # 设置仿真参数
        if t_max is None:
            t_max = t[-1] - t[0]
        if t_step is None:
            # 自动计算步长
            if len(t) > 1:
                min_step = min(np.diff(t))
                t_step = min(min_step, t_max / 1000)
            else:
                t_step = t_max / 1000
        
        # 使用线程池进行并行仿真
        results = {}
        start_time = time.time()
        
        if self.max_workers is None or self.max_workers > 1:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_batch = {
                    executor.submit(self._run_batch_item, i, t, batch_signals[i], circuit, 
                                    t_max, t_step, additional_instructions): i
                    for i in range(batch_size)
                }
                
                completed = 0
                for future in as_completed(future_to_batch):
                    batch_idx, result = future.result()
                    results[batch_idx] = result
                    
                    completed += 1
                    if progress_callback:
                        progress_callback(completed / batch_size)
                    
                    elapsed = time.time() - start_time
                    remaining = (elapsed / completed) * (batch_size - completed) if completed > 0 else 0
                    print(f"完成批次 {completed}/{batch_size} - 耗时: {elapsed:.1f}秒, 预计剩余: {remaining:.1f}秒")
        else:
            # 串行执行
            for i in range(batch_size):
                batch_idx, result = self._run_batch_item(i, t, batch_signals[i], circuit, 
                                                        t_max, t_step, additional_instructions)
                results[batch_idx] = result
                
                if progress_callback:
                    progress_callback((i+1) / batch_size)
                
                elapsed = time.time() - start_time
                remaining = (elapsed / (i+1)) * (batch_size - (i+1))
                print(f"完成批次 {i+1}/{batch_size} - 耗时: {elapsed:.1f}秒, 预计剩余: {remaining:.1f}秒")
        
        self.results = results
        total_time = time.time() - start_time
        print(f"批量仿真完成，总耗时: {total_time:.1f}秒，平均每批次耗时: {total_time/batch_size:.1f}秒")
        
        return results
    
    def get_batch_outputs(self, use_spice=True):
        """
        获取所有批次的输出波形
        
        参数:
            use_spice: 如果为True，返回NGspice仿真结果；如果为False，返回numpy计算结果
            
        返回:
            tuple: (t, outputs)，其中t为时间向量，outputs为形状为[batch_size, time_steps]的输出波形矩阵
        """
        if not self.results:
            raise ValueError("请先运行batch_simulation获取结果")
            
        batch_size = len(self.results)
        t = self.results[0]['time']
        n_timesteps = len(t)
        
        outputs = np.zeros((batch_size, n_timesteps))
        for i in range(batch_size):
            if use_spice:
                outputs[i] = self.results[i]['v_out_spice_resampled']
            else:
                outputs[i] = self.results[i]['v_out_numpy']
                
        return t, outputs
    
    def save_results(self, filename='opamp_adder_results.npz'):
        """
        保存仿真结果到NPZ文件
        
        参数:
            filename: 输出文件名
        """
        if not self.results:
            print("No results to save. Run simulation first.")
            return
            
        output_path = os.path.join(self.output_folder, filename)
        
        # 提取时间向量和批次输出波形，统一保存
        t, outputs_spice = self.get_batch_outputs(use_spice=True)
        _, outputs_numpy = self.get_batch_outputs(use_spice=False)
        
        # 保存数据
        np.savez(output_path, 
                 time=t, 
                 outputs_spice=outputs_spice,
                 outputs_numpy=outputs_numpy,
                 batch_results=self.results)
        
        print(f"Results saved to {output_path}")
    
    def plot_batch_results(self, batch_indices=None, save_figure=True, figure_name='batch_simulation_results.png'):
        """
        绘制批量仿真结果
        
        参数:
            batch_indices: 要绘制的批次索引列表，默认为None（绘制所有批次）
            save_figure: 是否保存图形到文件
            figure_name: 图形文件名
        """
        if not self.results:
            print("No results to plot. Run simulation first.")
            return
            
        if batch_indices is None:
            # 如果批次数量超过5，只显示前5个批次
            if len(self.results) > 5:
                batch_indices = list(range(5))
            else:
                batch_indices = list(range(len(self.results)))
        
        # 创建图形
        fig, axs = plt.subplots(len(batch_indices), 2, figsize=(15, 4*len(batch_indices)))
        
        # 如果只有一个批次，确保axs是二维数组
        if len(batch_indices) == 1:
            axs = np.array([axs])
        
        # 绘制每个批次的结果
        for i, batch_idx in enumerate(batch_indices):
            if batch_idx not in self.results:
                print(f"Batch {batch_idx} not found in results.")
                continue
                
            result = self.results[batch_idx]
            t = result['time']
            signals = result['signals']
            v_out_numpy = result['v_out_numpy']
            v_out_spice = result['v_out_spice_resampled']
            
            # 绘制输入信号
            for j in range(signals.shape[0]):
                axs[i, 0].plot(t*1e3, signals[j], label=f'Channel {j+1}')
            
            axs[i, 0].set_xlabel('Time (ms)')
            axs[i, 0].set_ylabel('Voltage (V)')
            axs[i, 0].grid(True)
            axs[i, 0].legend()
            
            # 绘制输出信号
            axs[i, 1].plot(t*1e3, v_out_numpy, 'g-', label='NumPy (ideal)')
            axs[i, 1].plot(t*1e3, v_out_spice, 'r--', label='NGspice')
            
            axs[i, 1].set_xlabel('Time (ms)')
            axs[i, 1].set_ylabel('Voltage (V)')
            axs[i, 1].grid(True)
            axs[i, 1].legend()
        
        plt.tight_layout()
        
        # 保存图形
        if save_figure:
            figure_path = os.path.join(self.output_folder, figure_name)
            plt.savefig(figure_path, dpi=300)
            print(f"Figure saved to {figure_path}")
            
        plt.show()


def main():
    """主函数，演示如何使用MultiChannelOpAmpAdderSimulation类和不同的电路类"""
    # 创建仿真实例
    sim = MultiChannelOpAmpAdderSimulation(output_folder='./temp', max_workers=4)
    
    # 示例1：运放加法器电路仿真
    print("\n=== 示例1：运放加法器电路仿真 ===")
    
    # 生成输入信号，4个通道
    n_channels = 4
    t, signals = sim.generate_input_signals(
        t_max=1e-3,     # 1ms仿真时间
        fs=1e6,         # 1MHz采样率
        n_channels=n_channels,
        freqs=[3e3, 7e3, 12e3, 18e3],  # 不同频率的正弦波
        amps=[0.2, 0.3, 0.25, 0.15]    # 不同振幅
    )
    
    # 设置不同通道的增益并创建电路(只包含电路定义，不包含仿真参数)
    gains = [1.0, 2.0, 0.5, 1.5]
    circuit = OpAmpAdderCircuit(n_channels=n_channels, gains=gains)
    
    # 运行仿真，传入电路对象和仿真参数
    result = sim.run_simulation(
        t, signals, circuit, 
        t_max=1e-3,      # 仿真时间显式传递
        t_step=1e-6,     # 仿真步长显式传递
        print_netlist=True
    )
    
    if result:
        # 打印最大和平均差异
        print(f"Maximum difference: {result['max_diff']*1000:.6f} mV")
        print(f"Average difference: {result['mean_diff']*1000:.6f} mV")
        
        # 绘制输入输出波形
        plt.figure(figsize=(12, 8))
        
        # 绘制输入波形
        plt.subplot(2, 1, 1)
        for i in range(n_channels):
            plt.plot(t*1e3, signals[i], label=f'Input {i+1} (Gain={gains[i]})')
        plt.grid(True)
        plt.legend()
        plt.title('Multi-Channel Op-Amp Adder Input Signals')
        plt.xlabel('Time (ms)')
        plt.ylabel('Voltage (V)')
        
        # 绘制输出波形
        plt.subplot(2, 1, 2)
        plt.plot(t*1e3, result['v_out_numpy'], 'g-', label='Output (NumPy)')
        plt.plot(t*1e3, result['v_out_spice_resampled'], 'r--', label='Output (NGspice)')
        plt.grid(True)
        plt.legend()
        plt.title('Multi-Channel Op-Amp Adder Output Signal')
        plt.xlabel('Time (ms)')
        plt.ylabel('Voltage (V)')
        
        plt.tight_layout()
        plt.savefig('./temp/multi_channel_example.png', dpi=300)
        plt.show()
    
    # 示例2：RC低通滤波器仿真
    print("\n=== 示例2：RC低通滤波器仿真 ===")
    
    # 生成输入信号 - 方波
    t = np.linspace(0, 5e-3, 5000)  # 5ms, 5000点
    square_wave = np.zeros_like(t)
    for i in range(len(t)):
        if (i // 500) % 2 == 0:  # 每500点切换一次，产生方波
            square_wave[i] = 1.0
        else:
            square_wave[i] = 0.0
    
    # 创建RC低通滤波器电路
    rc_circuit = RCLowPassCircuit(R=10e3, C=1e-7)  # 10kΩ, 100nF, 时间常数为1ms
    
    # 运行仿真 - 注意：输入信号是一维数组
    result = sim.run_simulation(
        t, square_wave, rc_circuit,
        t_max=5e-3,
        t_step=1e-6,
        print_netlist=True
    )
    
    if result:
        # 打印最大和平均差异
        print(f"RC Filter Maximum difference: {result['max_diff']*1000:.6f} mV")
        print(f"RC Filter Average difference: {result['mean_diff']*1000:.6f} mV")
        
        # 绘制输入输出波形
        plt.figure(figsize=(12, 6))
        
        plt.plot(t*1e3, result['signals'][0], 'b-', label='Input (Square Wave)')
        plt.plot(t*1e3, result['v_out_numpy'], 'g-', label='Output (NumPy)')
        plt.plot(t*1e3, result['v_out_spice_resampled'], 'r--', label='Output (NGspice)')
        
        plt.grid(True)
        plt.legend()
        plt.title('RC Low-Pass Filter Response')
        plt.xlabel('Time (ms)')
        plt.ylabel('Voltage (V)')
        
        plt.tight_layout()
        plt.savefig('./temp/rc_filter_example.png', dpi=300)
        plt.show()
    
    # 示例3：批量仿真演示 - 使用RC低通滤波器
    print("\n=== 示例3：批量仿真演示 - RC低通滤波器 ===")
    
    # 创建批量仿真数据，5个批次，每个批次为一个方波但频率不同
    batch_size = 5
    t_max = 10e-3
    fs = 1e6
    t = np.arange(0, t_max, 1/fs)
    
    # 创建批量数据 [batch_size, time_steps]
    batch_signals = np.zeros((batch_size, len(t)))
    
    # 为每个批次生成不同频率的方波
    for i in range(batch_size):
        freq = 100 * (i + 1)  # 从100Hz到500Hz
        period_samples = int(fs / freq)
        
        for j in range(len(t)):
            if (j % period_samples) < (period_samples // 2):
                batch_signals[i, j] = 1.0
            else:
                batch_signals[i, j] = 0.0
    
    # 创建一组具有不同时间常数的RC滤波器
    rc_circuits = [
        RCLowPassCircuit(R=10e3, C=1e-7),  # tau = 1ms
    ]
    
    # 分别运行每个RC滤波器的批量仿真
    for idx, rc_circuit in enumerate(rc_circuits):
        print(f"\n运行RC滤波器{idx+1} (tau = {rc_circuit.tau*1000:.1f}ms) 的批量仿真:")
        
        # 运行批量仿真
        def progress_update(progress):
            print(f"批量仿真进度: {progress*100:.1f}%")
        
        # 运行批量仿真，仿真参数显式传递
        results = sim.run_batch_simulation(
            t, batch_signals, rc_circuit,
            t_max=t_max,
            t_step=1e-6,
            progress_callback=progress_update
        )
        
        # 保存结果
        sim.save_results(f'rc_filter_{idx+1}_results.npz')
        
        # 绘制批量仿真结果
        sim.plot_batch_results(save_figure=True, figure_name=f'rc_filter_{idx+1}_results.png')
        
        # 获取并打印批量输出结果的形状
        t, outputs_spice = sim.get_batch_outputs(use_spice=True)
        _, outputs_numpy = sim.get_batch_outputs(use_spice=False)
        
        print(f"批量输出结果形状 (NGspice): {outputs_spice.shape}")
        print(f"批量输出结果形状 (NumPy): {outputs_numpy.shape}")


if __name__ == "__main__":
    main()