import numpy as np
import logging
import matplotlib.pyplot as plt
from spicelib.sim.sim_runner import SimRunner
from spicelib.editor.spice_editor import SpiceEditor
from spicelib.simulators.ngspice_simulator import NGspiceSimulator
from spicelib import RawRead
import tempfile
import os
import traceback
import platform
import shutil
from pathlib import Path
from scipy.interpolate import interp1d
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
from tqdm import tqdm
from circuit_base import BaseCircuit
from typing import Dict, List, Tuple, Optional, Union, Any, Callable

# 创建 logger
logger = logging.getLogger(__name__)


class CircuitSimulation:
    """电路仿真类，支持任意电路的仿真和批量仿真"""

    def __init__(self,
                 output_folder: str = './temp',
                 ngspice_path: Optional[str] = None,
                 max_workers: int = 16,
                 clean_temp_files: bool = True,
                 show_progress: bool = False) -> None:
        """
        初始化仿真类

        参数:
            output_folder: 输出文件夹路径
            ngspice_path: NGspice可执行文件路径，如果为None则使用默认路径
            max_workers: 并行仿真的最大进程数，默认为8
            clean_temp_files: 是否在仿真后清理临时文件(.raw, .net, .log)，默认为True
            show_progress: 是否显示进度条，默认为False
        """
        self.output_folder: str = output_folder
        os.makedirs(output_folder, exist_ok=True)

        # 设置NGspice路径
        if ngspice_path is None:
            self.ngspice_path: str = self._get_default_ngspice_path()
        else:
            self.ngspice_path: str = ngspice_path

        # 检查NGspice路径是否存在
        if not self._check_ngspice_available():
            raise FileNotFoundError(f"NGspice可执行文件未找到: {self.ngspice_path}")

        # 设置并行进程数
        self.max_workers: int = max_workers

        # 设置是否清理临时文件
        self.clean_temp_files: bool = clean_temp_files
        
        # 设置是否显示进度条
        self.show_progress: bool = show_progress

        # 初始化结果变量
        self.results: Dict[int, Dict[str, Any]] = {}

    def _get_default_ngspice_path(self) -> str:
        """
        根据操作系统自动检测NGspice路径
        
        返回:
            str: NGspice可执行文件路径
        """
        system = platform.system().lower()
        
        if system == "windows":
            # Windows系统，优先查找相对路径，然后查找系统PATH
            windows_paths = [
                r".\Spice64\bin\ngspice_con.exe",
                r"Spice64\bin\ngspice_con.exe",
                "ngspice.exe",
                "ngspice_con.exe"
            ]
            
            for path in windows_paths:
                if os.path.exists(path) or shutil.which(path):
                    return path
                    
        elif system in ["linux", "darwin"]:  # Linux或macOS
            # Unix-like系统，查找系统安装的ngspice
            unix_paths = [
                "ngspice",
                "/usr/bin/ngspice",
                "/usr/local/bin/ngspice",
                "/opt/local/bin/ngspice"
            ]
            
            for path in unix_paths:
                if shutil.which(path) or os.path.exists(path):
                    return path
        
        # 默认返回系统路径中的ngspice
        return "ngspice"
    
    def _check_ngspice_available(self) -> bool:
        """
        检查NGspice是否可用
        
        返回:
            bool: 如果NGspice可用返回True，否则返回False
        """
        # 首先检查文件是否存在
        if os.path.exists(self.ngspice_path):
            return True
            
        # 然后检查是否在系统PATH中
        if shutil.which(self.ngspice_path):
            return True
            
        return False

    def _cleanup_files(self,
                       raw_file: Optional[Path] = None,
                       log_file: Optional[Path] = None,
                       netlist_path: Optional[str] = None,
                       debug: bool = False) -> None:
        return # 临时跳过清理
        """
        清理临时文件

        参数:
            raw_file: .raw文件路径
            log_file: .log文件路径
            netlist_path: .net文件路径
            debug: 是否打印调试信息
        """
        if not self.clean_temp_files:
            return

        files_to_clean = []
        if raw_file and os.path.exists(str(raw_file)):
            files_to_clean.append(str(raw_file))
        if log_file and os.path.exists(str(log_file)):
            files_to_clean.append(str(log_file))
        if netlist_path and os.path.exists(netlist_path):
            files_to_clean.append(netlist_path)

        exe_log_file = str(log_file).replace('.log', '.exe.log')
        local_netlist_file = str(log_file).replace('.log', '.net')
        files_to_clean.extend([exe_log_file, local_netlist_file])

        for file_path in files_to_clean:
            try:
                os.unlink(file_path)
                if debug:
                    print(f"已清理临时文件: {file_path}")
            except Exception as e:
                print(f"清理临时文件 {file_path} 时出错: {str(e)}")

    def generate_sine_signals(self,
                              t_max: float = 1e-3,
                              fs: float = 1e6,
                              n_outputs: int = 2,
                              freqs: Optional[List[float]] = None,
                              amps: Optional[List[float]] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        生成多通道正弦波信号

        参数:
            t_max: 最大仿真时间(秒)
            fs: 采样频率(Hz)
            n_outputs: 输出通道数量
            freqs: 各通道信号频率列表，默认为None（自动生成）
            amps: 各通道信号振幅列表，默认为None（自动生成）

        返回:
            tuple: (时间向量, 信号矩阵[time_steps, outputs])
        """
        t: np.ndarray = np.arange(0, t_max, 1/fs)

        # 如果未指定频率，则自动生成不同频率
        if freqs is None:
            freqs = [5e3 * (i + 1) for i in range(n_outputs)]
        elif len(freqs) < n_outputs:
            # 扩展频率列表到n_outputs
            freqs = freqs + [5e3 * (i + 1)
                             for i in range(len(freqs), n_outputs)]

        # 如果未指定振幅，则使用标准振幅
        if amps is None:
            amps = [0.5 / n_outputs] * n_outputs
        elif len(amps) < n_outputs:
            # 扩展振幅列表到n_outputs
            amps = amps + [0.5 / n_outputs] * (n_outputs - len(amps))

        # 生成多通道信号
        signals: np.ndarray = np.zeros((n_outputs, len(t)))
        for i in range(n_outputs):
            signals[i] = amps[i] * np.sin(2 * np.pi * freqs[i] * t)

        return t, signals.T

    def generate_square_signals(self, t_max: float = 1e-3, fs: float = 1e6,
                                n_outputs: int = 1, freqs: Optional[List[float]] = None,
                                amps: Optional[List[float]] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        生成多通道方波信号

        参数:
            t_max: 最大仿真时间(秒)
            fs: 采样频率(Hz)
            n_outputs: 输出通道数量
            freqs: 各通道信号频率列表，默认为None（自动生成）
            amps: 各通道信号振幅列表，默认为None（自动生成）

        返回:
            tuple: (时间向量, 信号矩阵[outputs, time_steps])
        """
        t: np.ndarray = np.arange(0, t_max, 1/fs)

        # 如果未指定频率，则自动生成不同频率
        if freqs is None:
            freqs = [100 * (i + 1) for i in range(n_outputs)]
        elif len(freqs) < n_outputs:
            # 扩展频率列表到n_outputs
            freqs = freqs + [100 * (i + 1)
                             for i in range(len(freqs), n_outputs)]

        # 如果未指定振幅，则使用标准振幅
        if amps is None:
            amps = [1.0] * n_outputs
        elif len(amps) < n_outputs:
            # 扩展振幅列表到n_outputs
            amps = amps + [1.0] * (n_outputs - len(amps))

        # 生成多通道方波信号
        signals: np.ndarray = np.zeros((n_outputs, len(t)))
        for i in range(n_outputs):
            period_samples: int = int(fs / freqs[i])
            for j in range(len(t)):
                if (j % period_samples) < (period_samples // 2):
                    signals[i, j] = amps[i]
                else:
                    signals[i, j] = 0

        return t, signals

    def create_pwl_data(self, t: np.ndarray, v: np.ndarray, max_points: int = 1000) -> str:
        """
        创建PWL数据字符串，用于替换电压源

        参数:
            t: 时间向量
            v: 电压向量
            max_points: 最大点数，用于减少数据量

        返回:
            str: PWL数据字符串
        """
        decimation: int = max(1, len(t) // max_points)
        pwl_data: str = "PWL("
        for i in range(0, len(t), decimation):
            pwl_data += f"{t[i]} {v[i]} "
        pwl_data += ")"
        return pwl_data

    def create_simulation_netlist(self, circuit: BaseCircuit, t_max: float = 1e-3, t_step: float = 1e-6,
                                  additional_instructions: Optional[List[str]] = None) -> str:
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
        netlist_text: str = circuit.get_circuit_netlist()

        # 获取需要保存的节点
        output_nodes: List[str] = circuit.get_output_node_names()

        # 构建保存指令 - 只保存输出节点而不是所有节点
        save_instructions = [f".save v({node})" for node in output_nodes]

        # 添加仿真指令
        netlist_text += f"""
* Simulation settings
.tran {t_step} {t_max}
{chr(10).join(save_instructions)}

* simulate options
.options method=gear 
.options chgtol=1e-11 
.options reltol=0.01 
* .options rshunt=1G 
* .options rseries=0.05
* .options cshunt=1p 
.options trtol=1
"""

        # 添加额外的仿真指令
        if additional_instructions:
            for instruction in additional_instructions:
                netlist_text += instruction + "\n"

        # 添加结束标记
        netlist_text += ".end\n"

        return netlist_text

    def run_simulation_once(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        运行单次仿真, 并记录仿真耗时

        参数:
            args: 位置参数
            kwargs: 关键字参数
        """
        start_time: float = time.time()
        print("开始单次仿真...")
        result: Dict[str, Any] = self._run_simulation_once(*args, **kwargs)
        end_time: float = time.time()
        elapsed_time: float = end_time - start_time
        print(f"单次仿真耗时: {elapsed_time:.2f}秒")
        return result

    def _run_simulation_once(self,
                             signals: np.ndarray,
                             circuit: BaseCircuit,
                             additional_instructions: Optional[List[str]] = None,
                             print_netlist: bool = False,
                             debug: bool = False,
                             sample_rate: int = 2000,
                             ) -> Dict[str, Any]:
        """
        运行单次仿真

        参数:
            signals: 信号矩阵 [time_steps, inputs] 或一维数组
            circuit: BaseCircuit的子类实例，包含网表和仿真逻辑
            sample_rate: 采样频率(Hz)
            additional_instructions: 额外的仿真指令列表
            print_netlist: 是否打印网表内容
            debug: 是否打印调试信息

        返回:
            dict: 包含仿真结果的字典，包含以下键:
                - 'time': 一维数组 [time_steps]，原始输入时间向量
                - 'signals': 二维数组 [time_steps, inputs]，原始输入信号矩阵
                - 'v_out_numpy': 二维数组 [time_steps, outputs]，NumPy计算的理论输出
                - 'time_spice': 一维数组 [spice_time_steps]，NGspice仿真的实际时间点
                - 'v_out_spice': 二维数组 [time_steps, outputs]，重采样到输入时间轴的NGspice输出
                - 'diff': 字典，键为节点名称，值为一维数组 [time_steps]，理论值与仿真值的差异
                - 'max_diff': 字典，键为节点名称，值为标量，最大差异值
                - 'mean_diff': 字典，键为节点名称，值为标量，平均差异值
                - 'rmse': 字典，键为节点名称，值为标量，均方根误差
        """
        # 处理一维输入信号，转换为二维数组 [time_steps, 1]
        if signals.ndim == 1:
            signals = np.array([signals]).T  # 转置为列向量 [time_steps, 1]

        # 预处理信号 - 使用 preprocess_input_signals 方法（如果存在）
        preprocessed_signals: np.ndarray = signals
        if hasattr(circuit, 'preprocess_input_signals'):
            preprocessed_signals = circuit.preprocess_input_signals(
                signals)

        t_step = 1/sample_rate

        t_max = t_step * len(preprocessed_signals)
        t = np.arange(0, t_max, t_step)

        # 创建完整仿真网表
        netlist_text: str = self.create_simulation_netlist(
            circuit, t_max, t_step, additional_instructions)

        # 创建临时网表文件 - 使用指定的输出目录而不是系统临时目录
        # 确保输出目录存在
        os.makedirs(self.output_folder, exist_ok=True)
        with tempfile.NamedTemporaryFile(suffix='.net', delete=False, mode='w', encoding='utf-8', 
                                          dir=self.output_folder) as f:
            f.write(netlist_text)
            logger.debug(f"临时网表文件创建成功: {f.name}")
            temp_netlist_path: str = f.name

        # 初始化文件路径变量
        raw_file: Optional[Path] = None
        log_file: Optional[Path] = None
        error_occurred: bool = False

        try:
            # 创建网表
            netlist: SpiceEditor = SpiceEditor(temp_netlist_path)

            if print_netlist:
                print("\n===== Netlist Content =====")
                print(netlist_text)
                print("=========================\n")

            # 获取输入源名称
            input_sources: List[str] = circuit.get_input_source_names()

            # 确保输入源数量与信号通道数匹配
            if len(input_sources) != preprocessed_signals.shape[1]:
                raise ValueError(
                    f"输入源数量({len(input_sources)})与预处理后的信号输入数({preprocessed_signals.shape[1]})不匹配")

            # 设置输入电压源为PWL数据
            for i, source_name in enumerate(input_sources):
                netlist[source_name].model = self.create_pwl_data(
                    t, preprocessed_signals[:, i])

            # 创建SimRunner实例
            runner: SimRunner = SimRunner(
                output_folder=self.output_folder,
                simulator=NGspiceSimulator.create_from(self.ngspice_path),
                verbose=False
            )
            # 运行NGspice仿真
            raw_file: Optional[Path] = None
            log_file: Optional[Path] = None
            raw_file, log_file = runner.run_now(netlist, exe_log=True)

            # 打印仿真结果文件路径
            if debug:
                print(f"\n调试信息 - 仿真文件路径:")
                print(f"原始数据文件: {raw_file}")
                print(f"日志文件: {log_file}")

            # 读取NGspice仿真结果
            if raw_file and os.path.exists(str(raw_file)):
                # 在Linux下的ngspice需要指定dialect
                raw_data: RawRead = RawRead(raw_file, dialect='ngspice')

                # 获取仿真数据
                time_spice: np.ndarray = raw_data.get_trace('time').get_wave(0)

                # 获取输出节点名称列表
                output_nodes: List[str] = circuit.get_output_node_names()

                # 处理多通道输出
                v_out_spice: Dict[str, np.ndarray] = {}
                v_out_spice_resampled: Dict[str, np.ndarray] = {}
                diff: Dict[str, np.ndarray] = {}

                # 创建数组存储重采样后的数据，形状为 [time_steps, outputs]
                n_outputs: int = len(output_nodes)
                v_out_spice_array: np.ndarray = np.zeros(
                    (len(time_spice), n_outputs))
                v_out_spice_resampled_array: np.ndarray = np.zeros(
                    (len(t), n_outputs))

                # 获取理论输出值
                v_out_numpy: Union[np.ndarray, Dict[str, np.ndarray]]
                if hasattr(circuit, 'simulate_numpy'):
                    # 尝试使用simulate_numpy方法
                    # 注意：确保信号格式正确 - 预期是 [time_steps, inputs] 格式
                    v_out_numpy = circuit.simulate_numpy(t, signals.copy())
                else:
                    # 如果电路没有提供理论计算方法，使用空数组
                    v_out_numpy = np.zeros((len(t), n_outputs))
                    print("警告：电路未提供理论输出计算方法，无法进行对比分析")

                for i, node in enumerate(output_nodes):
                    v_out_spice[node] = raw_data.get_trace(
                        f'v({node})').get_wave(0)
                    v_out_spice_array[:, i] = v_out_spice[node]

                    # 重采样NGspice数据到numpy的时间轴上进行比较
                    f_interp: interp1d = interp1d(
                        time_spice, v_out_spice[node], kind='linear', bounds_error=False, fill_value=0)
                    v_out_spice_resampled[node] = f_interp(t)
                    v_out_spice_resampled_array[:,
                                                i] = v_out_spice_resampled[node]

                    # 计算差异
                    if isinstance(v_out_numpy, dict):
                        # 字典格式的输出，每个通道有自己的键
                        # 转换节点名称，例如 'out_lp' -> 'lp'
                        node_key: str = node.replace('out_', '')
                        if node_key in v_out_numpy:
                            diff[node] = v_out_numpy[node_key] - \
                                v_out_spice_resampled[node]
                        else:
                            print(f"警告: 在v_out_numpy字典中找不到键'{node_key}'")
                            diff[node] = np.zeros_like(
                                v_out_spice_resampled[node])
                    elif isinstance(v_out_numpy, np.ndarray) and v_out_numpy.ndim > 1:
                        # 多通道NumPy输出
                        diff[node] = v_out_numpy[:, i] - \
                            v_out_spice_resampled[node]
                    else:
                        # 单通道NumPy输出
                        diff[node] = v_out_numpy - \
                            v_out_spice_resampled[node]

                # 计算统计信息
                max_diff: Dict[str, float] = {}
                mean_diff: Dict[str, float] = {}
                rmse: Dict[str, float] = {}

                for node in output_nodes:
                    # 过滤掉无效值，防止计算错误
                    valid_indices: np.ndarray = np.isfinite(diff[node])
                    if np.any(valid_indices):
                        filtered_diff: np.ndarray = diff[node][valid_indices]
                        if len(filtered_diff) > 0:
                            max_diff[node] = np.max(np.abs(filtered_diff))
                            mean_diff[node] = np.mean(np.abs(filtered_diff))
                            rmse[node] = np.sqrt(
                                np.mean(np.square(filtered_diff)))
                        else:
                            max_diff[node] = mean_diff[node] = rmse[node] = 0.0
                    else:
                        max_diff[node] = mean_diff[node] = rmse[node] = 0.0

                # 返回结果
                result: Dict[str, Any] = {
                    # 一维数组 [time_steps]，原始输入时间向量
                    'time': t,
                    # 二维数组 [time_steps, inputs]，原始输入信号矩阵
                    'signals': signals,
                    # 二维数组 [time_steps, outputs]，NumPy计算的理论输出
                    'v_out_numpy': v_out_numpy,
                    # 一维数组 [spice_time_steps]，NGspice仿真的实际时间点
                    'time_spice': time_spice,
                    # 字典，键为节点名称，值为一维数组 [spice_time_steps]，NGspice原始输出
                    'v_out_spice': v_out_spice_resampled_array,
                    # 字典，键为节点名称，值为一维数组 [time_steps]，理论值与仿真值的差异
                    'diff': diff,
                    'max_diff': max_diff,                   # 字典，键为节点名称，值为标量，最大差异值
                    'mean_diff': mean_diff,                 # 字典，键为节点名称，值为标量，平均差异值
                    'rmse': rmse                            # 字典，键为节点名称，值为标量，均方根误差
                }

                return result
            else:
                error_occurred = True
                print("NGspice simulation failed - No raw file generated")
                # 打印 netlist
                print("\n===== Netlist Content =====")
                print(netlist_text)
                print("=========================\n")
                if raw_file:
                    print(f"Expected raw file path: {raw_file}")
                if log_file:
                    print(f"Expected log file path: {log_file}")
                    # 仿真失败，打印 log
                    with open(log_file, 'r', encoding='utf-8') as log_f:
                        log_content: str = log_f.read()
                        print("NGspice Log Content:")
                        print(log_content)
                return {}

        except Exception as e:
            error_occurred = True
            print(f"Error during simulation: {str(e)}")
            traceback.print_exc()
            return {}
        finally:
            # 如果没有出错且选择了清理选项，则清理所有临时文件
            if not error_occurred and self.clean_temp_files:
                self._cleanup_files(raw_file, log_file,
                                    temp_netlist_path, debug)

    def _run_batch_item(self, batch_idx: int,
                        signals: np.ndarray,
                        circuit: BaseCircuit,
                        sample_rate: int,
                        additional_instructions: Optional[List[str]]) -> Tuple[int, Dict[str, Any]]:
        """
        运行单个批次的仿真（用于并行仿真）

        此函数会在单独的进程中执行，所以需要保证所有参数都可以跨进程序列化传递

        参数:
            batch_idx: 批次索引
            signals: 信号矩阵 [time_steps, inputs]
            circuit: BaseCircuit的子类实例，包含网表和仿真逻辑
            additional_instructions: 额外的仿真指令列表

        返回:
            tuple: (batch_idx, 仿真结果)
        """
        # 使用与当前实例相同的输出路径和ngspice路径创建一个新的仿真对象
        # 这样可以避免尝试跨进程传递整个CircuitSimulation对象
        sim_instance: CircuitSimulation = CircuitSimulation(
            output_folder=self.output_folder,
            ngspice_path=self.ngspice_path,
            max_workers=1,  # 子进程中只需要串行执行
            clean_temp_files=self.clean_temp_files  # 继承父进程的清理设置
        )

        # 使用新创建的实例运行仿真
        result: Dict[str, Any] = sim_instance._run_simulation_once(
            signals, circuit, additional_instructions, sample_rate=sample_rate)
        return batch_idx, result

    def run_simulation(self,
                       batch_signals: np.ndarray,
                       circuit: BaseCircuit,
                       additional_instructions: Optional[List[str]] = None,
                       sample_rate: int = 2000,
                       truncate_lengths: Optional[Union[List[int],
                                                        np.ndarray]] = None
                       ) -> Dict[str, Any]:
        """
        运行批量仿真

        参数:
            batch_signals: 批量信号矩阵 [batch_size, time_steps, inputs]
            circuit: BaseCircuit的子类实例，包含网表和仿真逻辑
            additional_instructions: 额外的仿真指令列表
            progress_callback: 进度回调函数，接受一个0-1之间的浮点数表示进度
            truncate_lengths: 截断长度列表，指定每个批次信号的长度

        返回:
            dict: 包含以下键的字典:
                - 'results': 字典，键为批次索引，值为完整的仿真结果字典
                - 'numpy_outputs': 三维数组 [batch_size, time_steps, outputs]，所有批次的NumPy理论输出
                - 'spice_outputs': 三维数组 [batch_size, time_steps, outputs]，所有批次的NGspice仿真输出
                - 'time': 一维数组 [time_steps]，仿真的时间向量
        """
        # 确保输入的批量信号矩阵是3D数组，格式为 [batch_size, time_steps, inputs]
        if batch_signals.ndim == 2:
            # 单输入通道的情况，形状为 [batch_size, time_steps]
            # 扩展为 [batch_size, time_steps, 1]
            batch_signals = np.expand_dims(batch_signals, axis=2)
        elif batch_signals.ndim != 3:
            raise ValueError(
                "batch_signals必须是3维数组，格式应为 [batch_size, time_steps, inputs], 实际格式: {}".format(batch_signals.shape))

        batch_size: int = batch_signals.shape[0]
        # 处理 truncate_lengths，截断每个批次的信号长度
        if truncate_lengths is not None:
            lengths_arr = np.array(truncate_lengths, dtype=int)
            if lengths_arr.ndim != 1 or lengths_arr.size != batch_size:
                raise ValueError(
                    f"truncate_lengths必须为长度{batch_size}的一维数组, 实际形状: {lengths_arr.shape}")
            max_len = batch_signals.shape[1]
            if np.any(lengths_arr <= 0) or np.any(lengths_arr > max_len):
                raise ValueError(f"每个截断长度必须在1到{max_len}之间")
            signals_list = [batch_signals[i, :lengths_arr[i], :]
                            for i in range(batch_size)]
        else:
            signals_list = [batch_signals[i] for i in range(batch_size)]

        # 设置仿真参数
        t = np.arange(0, batch_signals.shape[1] / sample_rate,
                      1 / sample_rate)
        t_max = t[-1] - t[0]

        # 计算步长
        t_step = 1 / sample_rate

        # 使用进程池进行并行仿真
        results: Dict[int, Dict[str, Any]] = {}
        start_time: float = time.time()

        # 并行仿真
        if self.max_workers is None or self.max_workers > 1:
            logger.info(f"使用 {self.max_workers} 个进程进行并行仿真")
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_batch: Dict[Any, int] = {
                    executor.submit(
                        self._run_batch_item,
                        i,
                        signals_list[i],
                        circuit,
                        sample_rate,
                        additional_instructions
                    ): i for i in range(batch_size)
                }

                pbar = tqdm(total=batch_size, desc="批量仿真进度", disable=not self.show_progress)
                completed: int = 0

                for future in as_completed(future_to_batch):
                    batch_idx, result = future.result()
                    results[batch_idx] = result

                    completed += 1
                    pbar.update(1)  # 更新进度条

                    elapsed: float = time.time() - start_time
                    remaining: float = (elapsed / completed) * \
                        (batch_size - completed) if completed > 0 else 0

                    # 更新进度条描述信息以显示时间信息
                    pbar.set_description(
                        f"批量仿真进度 - 耗时: {elapsed:.1f}秒, 预计剩余: {remaining:.1f}秒"
                    )

                # 关闭进度条
                pbar.close()
        else:
            # 串行执行
            # 使用tqdm创建进度条
            pbar = tqdm(total=batch_size, desc="批量仿真进度", disable=not self.show_progress)
            for i in range(batch_size):
                batch_idx, result = self._run_batch_item(
                    i,
                    signals_list[i],
                    circuit,
                    sample_rate,
                    additional_instructions
                )
                results[batch_idx] = result

                # 更新进度条
                pbar.update(1)

                elapsed: float = time.time() - start_time
                remaining: float = (elapsed / (i+1)) * (batch_size - (i+1))
                # 更新进度条描述信息以显示时间信息
                pbar.set_description(
                    f"批量仿真进度 - 耗时: {elapsed:.1f}秒, 预计剩余: {remaining:.1f}秒"
                )

            # 关闭进度条
            pbar.close()

        self.results = results
        total_time: float = time.time() - start_time
        logger.info(
            f"批量仿真完成，总耗时: {total_time:.1f}秒，平均每批次耗时: {total_time/batch_size:.1f}秒")

        # 保存批量仿真的全局时间向量
        self._batch_time = t
        # 提取合并后的输出矩阵
        t_numpy, numpy_outputs = self.get_batch_outputs(use_spice=False)
        t_spice, spice_outputs = self.get_batch_outputs(use_spice=True)

        # 返回字典格式的结果
        return {
            'results': results,                  # 字典，键为批次索引，值为完整的仿真结果字典
            # 三维数组 [batch_size, time_steps, outputs]
            'numpy_outputs': numpy_outputs,
            # 三维数组 [batch_size, time_steps, outputs]
            'spice_outputs': spice_outputs,
            'time': t                            # 一维数组 [time_steps]
        }

    def get_batch_outputs(self, use_spice: bool = True) -> Tuple[np.ndarray, np.ndarray]:
        """
        获取所有批次的输出波形

        参数:
            use_spice: 如果为True，返回NGspice仿真结果；如果为False，返回numpy计算结果

        返回:
            tuple: (t, outputs)，其中t为时间向量，outputs为形状为[batch_size, time_steps, outputs]的输出波形矩阵
        """
        if not self.results:
            raise ValueError("请先运行batch_simulation获取结果")

        batch_size: int = len(self.results)
        
        # 检查仿真结果是否为空
        if batch_size == 0:
            raise RuntimeError(
                "❌ SPICE仿真失败：无仿真结果数据\n"
                "💡 可能原因：\n"
                "  - NGspice进程启动失败\n"
                "  - 电路网表存在语法错误\n"
                "  - 仿真过程异常终止\n"
                "  - 输出节点名称不匹配\n"
                "🔧 建议检查NGspice安装和电路定义"
            )
        
        # 批量仿真时使用全局时间向量，否则使用单次结果时间
        if hasattr(self, '_batch_time'):
            t = self._batch_time
        else:
            if 'time' not in self.results[0]:
                raise RuntimeError(
                    "❌ SPICE仿真失败：结果中缺少时间数据\n"
                    "💡 这表明NGspice仿真过程没有正确完成\n"
                    "🔧 请检查仿真配置和网表文件"
                )
            t = self.results[0]['time']
        n_timesteps: int = len(t)

        # 获取第一个结果以确定输出通道数
        # 先检查SPICE和NumPy结果是否都存在
        has_spice = 'v_out_spice' in self.results[0]
        has_numpy = 'v_out_numpy' in self.results[0]
        
        # 记录详细信息
        if not has_spice:
            logger.error("❌ 结果中缺少v_out_spice数据")
        if not has_numpy:
            logger.error("❌ 结果中缺少v_out_numpy数据")
            
        # 如果两个都缺失，提供更详细的错误信息
        if not has_spice and not has_numpy:
            available_keys = list(self.results[0].keys()) if self.results else []
            raise RuntimeError(
                "❌ 仿真完全失败：SPICE和NumPy结果都缺失\n"
                f"📋 可用的结果键: {available_keys}\n"
                "💡 可能原因：\n"
                "  - 仿真过程中发生严重错误\n"
                "  - 电路配置存在根本性问题\n"
                "  - NGspice执行失败且NumPy实现也有错误\n"
                "🔧 建议：\n"
                "  1. 检查NGspice是否正确安装和运行\n"
                "  2. 验证电路网表的正确性\n"
                "  3. 检查NumPy理论模型实现"
            )
        
        if use_spice:
            if not has_spice:
                raise RuntimeError(
                    "❌ SPICE仿真失败：结果中缺少v_out_spice数据\n"
                    f"📋 可用的结果键: {list(self.results[0].keys()) if self.results else []}\n"
                    "💡 可能原因：\n"
                    "  - SPICE仿真没有成功执行\n"
                    "  - 输出节点名称配置错误\n"
                    "  - .raw文件解析失败\n"
                    "🔧 请检查电路输出节点定义和NGspice配置"
                )
            first_result = self.results[0]['v_out_spice']
        else:
            if not has_numpy:
                raise RuntimeError(
                    "❌ NumPy仿真失败：结果中缺少v_out_numpy数据\n"
                    f"📋 可用的结果键: {list(self.results[0].keys()) if self.results else []}\n"
                    "💡 可能原因：\n"
                    "  - 理论计算模型未正确执行\n"
                    "  - 电路的numpy实现存在错误\n"
                    "  - 数据结构配置问题\n"
                    "🔧 请检查电路的理论模型实现"
                )
            first_result = self.results[0]['v_out_numpy']

        # 判断输出维度
        n_outputs: int = 1  # 默认单输出
        if isinstance(first_result, np.ndarray) and first_result.ndim == 2:
            n_outputs = first_result.shape[1]

        # 创建输出数组，形状为 [batch_size, time_steps, outputs]
        outputs: np.ndarray = np.zeros((batch_size, n_timesteps, n_outputs))

        for i in range(batch_size):
            if use_spice:
                result_data = self.results[i]['v_out_spice']
            else:
                result_data = self.results[i]['v_out_numpy']

            # 处理单输出通道情况
            if isinstance(result_data, np.ndarray):
                if result_data.ndim == 1:
                    # 单通道输出，仅填充有效数据
                    outputs[i, :result_data.shape[0], 0] = result_data
                else:
                    # 多通道输出，仅填充有效数据
                    outputs[i, :result_data.shape[0], :] = result_data
            else:
                # 单值输出，处理为 [time_steps, 1]
                outputs[i, 0, 0] = result_data

        return t, outputs

    def save_results(self, filename: str = 'simulation_results.npz') -> None:
        """
        保存仿真结果到NPZ文件

        参数:
            filename: 输出文件名
        """
        if not self.results:
            print("No results to save. Run simulation first.")
            return

        output_path: str = os.path.join(self.output_folder, filename)

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

    def plot_results(self, result: Dict[str, Any], title: Optional[str] = None,
                     save_figure: bool = False, figure_name: Optional[str] = None) -> None:
        """
        绘制单个仿真结果

        参数:
            result: 仿真结果字典
            title: 图形标题
            save_figure: 是否保存图形到文件
            figure_name: 图形文件名，如果为None则使用默认值
        """
        if not result:
            print("No results to plot.")
            return

        t: np.ndarray = result['time']
        signals: np.ndarray = result['signals']
        v_out_numpy: Union[np.ndarray,
                           Dict[str, np.ndarray]] = result['v_out_numpy']
        v_out_spice: np.ndarray = result['v_out_spice']

        # 计算差异
        diff: Dict[str, np.ndarray] = result['diff']
        max_diff: Dict[str, float] = result['max_diff']
        mean_diff: Dict[str, float] = result['mean_diff']
        rmse: Dict[str, float] = result.get(
            'rmse', np.sqrt(np.mean(np.square(diff))))

        # 创建图形
        fig, axs = plt.subplots(3, 1, figsize=(10, 12))

        # 绘制输入波形
        for i in range(signals.shape[0]):
            axs[0].plot(t*1e3, signals[i], label=f'Input {i+1}')

        axs[0].set_xlabel('Time (ms)')
        axs[0].set_ylabel('Voltage (V)')
        axs[0].grid(True)
        axs[0].legend()
        if title:
            axs[0].set_title(f'{title} - Input Signals')
        else:
            axs[0].set_title('Input Signals')

        # 绘制输出波形
        axs[1].plot(t*1e3, v_out_numpy, 'g-', label='NumPy (ideal)')
        axs[1].plot(t*1e3, v_out_spice, 'r--', label='NGspice')

        axs[1].set_xlabel('Time (ms)')
        axs[1].set_ylabel('Voltage (V)')
        axs[1].grid(True)
        axs[1].legend()
        axs[1].set_title('Output Signals')

        # 绘制差异
        axs[2].plot(t*1e3, diff*1000, 'b-')  # 显示为mV
        axs[2].set_xlabel('Time (ms)')
        axs[2].set_ylabel('Difference (mV)')
        axs[2].grid(True)
        axs[2].set_title(
            f'Difference (Max: {max_diff*1000:.2f} mV, Mean: {mean_diff*1000:.2f} mV, RMSE: {rmse*1000:.2f} mV)')

        plt.tight_layout()

        # 保存图形
        if save_figure:
            if figure_name is None:
                figure_name = 'simulation_result.png'
            figure_path: str = os.path.join(self.output_folder, figure_name)
            plt.savefig(figure_path, dpi=300)
            print(f"Figure saved to {figure_path}")

        plt.show()
