import numpy as np
import matplotlib.pyplot as plt
from simulation import CircuitSimulation

class MultiChannelCircuitSimulation:
    """多通道输出电路的仿真适配器类
    
    这个类包装了基本的CircuitSimulation类，处理多通道输出电路的特殊需求。
    """
    
    def __init__(self, output_folder='./temp'):
        """
        初始化多通道仿真适配器
        
        参数:
            output_folder: 存储仿真结果的文件夹
        """
        self.sim = CircuitSimulation(output_folder=output_folder)
        
    def run_simulation(self, t, input_signals, circuit, print_netlist=False):
        """
        运行多通道电路的仿真
        
        参数:
            t: 时间向量
            input_signals: 输入信号矩阵
            circuit: 电路对象
            print_netlist: 是否打印网表
            
        返回:
            dict: 仿真结果字典
        """
        # 获取输出节点名称列表
        output_nodes = circuit.get_output_node_names()
        
        # 检查是否为多通道输出
        if len(output_nodes) > 1:
            return self._run_multi_channel_simulation(t, input_signals, circuit, output_nodes, print_netlist)
        else:
            # 单通道输出，直接使用原有的仿真函数
            return self.sim.run_simulation_once(t, input_signals, circuit, print_netlist=print_netlist)
    
    def _run_multi_channel_simulation(self, t, input_signals, circuit, output_nodes, print_netlist):
        """
        为多通道输出电路运行仿真
        
        参数:
            t: 时间向量
            input_signals: 输入信号矩阵
            circuit: 电路对象
            output_nodes: 输出节点名称列表
            print_netlist: 是否打印网表
            
        返回:
            dict: 仿真结果字典
        """
        # 创建网表 - 使用CircuitSimulation公开的API
        netlist = self.sim.create_simulation_netlist(
            circuit=circuit,
            t_max=t[-1], 
            t_step=(t[1]-t[0]) if len(t) > 1 else t[-1]/1000
        )
        
        # 如果需要，获取并打印网表
        if print_netlist:
            print("\n生成的NGspice网表:")
            print(netlist)
        
        # 获取PWL输入数据并写入文件
        pwl_data = {}
        temp_dir = self.sim.output_folder
        pwl_files = {}
        
        for i, source_name in enumerate(circuit.get_input_source_names()):
            if i < input_signals.shape[0]:
                # 手动创建PWL数据格式
                file_path = f"{temp_dir}/{source_name}_pwl.txt"
                with open(file_path, "w") as f:
                    # 写入每个时间点和对应的信号值
                    for j in range(len(t)):
                        f.write(f"{t[j]} {input_signals[i][j]}\n")
                pwl_files[source_name] = file_path
        
        # 将偏置电压也写入PWL文件（固定为1V）
        bias_file_path = f"{temp_dir}/Vbias_pwl.txt"
        with open(bias_file_path, "w") as f:
            f.write(f"0 1\n")
            f.write(f"{t[-1]} 1\n")
        pwl_files['Vbias'] = bias_file_path
            
        # 修改网表使用PWL文件
        for source_name, file_path in pwl_files.items():
            node_name = source_name.replace('Vin', 'in') if source_name != 'Vbias' else 'bias'
            netlist = netlist.replace(
                f"{source_name} {node_name} 0 0", 
                f"{source_name} {node_name} 0 PWL file \"{file_path}\""
            )
            
        # 将修改后的网表写入文件
        netlist_file = f"{temp_dir}/multi_channel_circuit.cir"
        with open(netlist_file, "w") as f:
            f.write(netlist)
            
        # 运行NGspice
        import subprocess
        command = [self.sim.ngspice_path, "-b", "-o", f"{temp_dir}/ngspice.log", netlist_file]
        process = subprocess.run(command, capture_output=True, text=True)
        
        # 检查仿真是否成功
        if process.returncode != 0:
            print(f"NGspice仿真失败: {process.stderr}")
            return None
            
        # 读取原始结果文件
        from spicelib import RawRead
        raw_file = f"{temp_dir}/multi_channel_circuit.raw"
        try:
            raw_data = RawRead(raw_file)
        except Exception as e:
            print(f"无法读取结果文件: {str(e)}")
            return None
        
        if raw_data is None:
            print("仿真失败，未能获取结果")
            return None
        
        # 获取时间数据
        t_spice = raw_data.get_time()
        
        # 创建结果字典
        result = {
            't': t,
            't_spice': t_spice
        }
        
        # 获取理论输出结果 - 使用SignedAdderCircuit的simulate_numpy方法
        numpy_outputs = circuit.simulate_numpy(t, input_signals)
        
        # 获取SPICE仿真的输出结果
        for i, node in enumerate(output_nodes):
            # 获取SPICE输出
            try:
                v_out_spice = raw_data.get_trace(f'v({node})').get_wave(0)
                
                # 重采样SPICE结果以匹配原始时间向量
                v_out_spice_resampled = np.interp(t, t_spice, v_out_spice)
                
                # 添加到结果字典
                result[f'v_{node}_spice'] = v_out_spice
                result[f'v_{node}_spice_resampled'] = v_out_spice_resampled
                
                # 添加理论输出到结果字典
                if isinstance(numpy_outputs, dict) and i in numpy_outputs:
                    result[f'v_{node}_numpy'] = numpy_outputs[i]
                
                print(f"通道 {node} 仿真成功")
            except Exception as e:
                print(f"获取通道 {node} 数据时出错: {str(e)}")
                # 继续处理其他通道
        
        return result
    
    def plot_results(self, result, title="电路仿真结果", save_figure=False, figure_name="simulation_result.png"):
        """
        绘制多通道仿真结果
        
        参数:
            result: 仿真结果字典
            title: 图表标题
            save_figure: 是否保存图片
            figure_name: 图片文件名
        """
        if result is None:
            print("没有可绘制的结果")
            return
        
        # 计算需要多少个子图
        output_channels = []
        for key in result.keys():
            if key.startswith('v_out') and key.endswith('_spice_resampled'):
                channel = key.replace('v_', '').replace('_spice_resampled', '')
                output_channels.append(channel)
        
        n_outputs = len(output_channels)
        if n_outputs == 0:
            print("没有找到输出通道数据")
            return
        
        # 创建图表
        fig, axes = plt.subplots(n_outputs, 1, figsize=(10, 4 * n_outputs), sharex=True)
        
        # 确保axes是一个列表，即使只有一个通道
        if n_outputs == 1:
            axes = [axes]
        
        # 绘制每个通道的结果
        for i, channel in enumerate(output_channels):
            ax = axes[i]
            
            # 绘制SPICE仿真结果
            spice_key = f'v_{channel}_spice_resampled'
            if spice_key in result:
                ax.plot(result['t'], result[spice_key], 'r-', label=f'SPICE仿真 ({channel})')
            
            # 绘制理论计算结果
            numpy_key = f'v_{channel}_numpy'
            if numpy_key in result:
                ax.plot(result['t'], result[numpy_key], 'b--', label=f'NumPy计算 ({channel})')
            
            ax.set_ylabel('电压 (V)')
            ax.grid(True)
            ax.legend(loc='upper right')
            
            # 添加通道标题
            ax.set_title(f'输出通道: {channel}')
        
        # 添加整体标题和x轴标签
        fig.suptitle(title, fontsize=16)
        axes[-1].set_xlabel('时间 (s)')
        
        # 调整布局
        plt.tight_layout()
        plt.subplots_adjust(top=0.95)
        
        # 保存图片（如果需要）
        if save_figure:
            plt.savefig(figure_name, dpi=300)
        
        plt.show()
