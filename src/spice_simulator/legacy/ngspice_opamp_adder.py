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


class OpAmpAdderSimulation:
    """运放加法器电路仿真类，可以对比NGspice仿真和NumPy理论计算结果"""
    
    def __init__(self, output_folder='./temp', ngspice_path=None):
        """
        初始化仿真类
        
        参数:
            output_folder: 输出文件夹路径
            ngspice_path: NGspice可执行文件路径，如果为None则使用默认路径
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
            
        # 创建SimRunner实例
        self.runner = SimRunner(
            output_folder=output_folder,
            simulator=NGspiceSimulator.create_from(self.ngspice_path),
            verbose=False
        )
        
        # 初始化结果变量
        self.results = None
    
    def generate_input_signals(self, t_max=1e-3, fs=1e6, freq1=5e3, freq2=10e3, amp1=0.5, amp2=0.3):
        """
        生成输入信号
        
        参数:
            t_max: 最大仿真时间(秒)
            fs: 采样频率(Hz)
            freq1: 第一个信号的频率(Hz)
            freq2: 第二个信号的频率(Hz)
            amp1: 第一个信号的振幅(V)
            amp2: 第二个信号的振幅(V)
            
        返回:
            tuple: (时间向量, 信号1, 信号2)
        """
        t = np.arange(0, t_max, 1/fs)
        v1 = amp1 * np.sin(2 * np.pi * freq1 * t)
        v2 = amp2 * np.sin(2 * np.pi * freq2 * t)
        return t, v1, v2
    
    def create_netlist(self, t_max, R1=10e3, R2=10e3, R3=10e3, RF=10e3):
        """
        创建运放加法器电路网表
        
        参数:
            t_max: 最大仿真时间(秒)
            R1, R2, R3, RF: 电阻值(欧姆)
            
        返回:
            str: 网表内容
        """
        netlist_text = f"""* Op-Amp Adder Circuit - NGspice Simulation
* Using ideal op-amp model
.param R1={R1} R2={R2} R3={R3} RF={RF}

* Power Supply
Vcc vcc 0 15
Vee vee 0 -15

* Define input voltage sources (will be replaced with PWL data)
Vin1 in1 0 0
Vin2 in2 0 0

* Op-Amp adder circuit
R1 in1 neg {{R1}}
R2 in2 neg {{R2}}
R3 0 neg {{R3}}
RF neg out {{RF}}

* Ideal op-amp model
Eop out 0 0 neg 1000000

* Simulation settings
.tran 1u {t_max} 0 0.1u
.save all
.end
"""
        return netlist_text
    
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
    
    def run_simulation(self, t, v1, v2, netlist_text, print_netlist=False):
        """
        运行仿真并返回结果
        
        参数:
            t: 时间向量
            v1, v2: 输入信号
            netlist_text: 网表内容
            print_netlist: 是否打印网表内容
            
        返回:
            dict: 包含仿真结果的字典
        """
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
            
            # 设置输入电压源为PWL数据
            netlist['Vin1'].model = self.create_pwl_data(t, v1)
            netlist['Vin2'].model = self.create_pwl_data(t, v2)
            
            # 运行仿真
            print("Running NGspice simulation...")
            raw_file, log_file = self.runner.run_now(netlist, exe_log=True)
            
            # 读取NGspice仿真结果
            if raw_file and os.path.exists(str(raw_file)):
                raw_data = RawRead(raw_file)
                
                # 获取仿真数据
                time_spice = raw_data.get_trace('time').get_wave(0)
                v_in1_spice = raw_data.get_trace('v(in1)').get_wave(0)
                v_in2_spice = raw_data.get_trace('v(in2)').get_wave(0)
                v_out_spice = raw_data.get_trace('v(out)').get_wave(0)
                
                print("NGspice simulation completed")
                
                # 计算理论输出（理想运放加法器）
                v_out_numpy = -(v1 + v2)
                
                # 重采样NGspice数据到numpy的时间轴上进行比较
                f_interp = interp1d(time_spice, v_out_spice, kind='linear', bounds_error=False, fill_value=0)
                v_out_spice_resampled = f_interp(t)
                diff = v_out_numpy - v_out_spice_resampled
                
                # 计算统计信息
                max_diff = np.max(np.abs(diff))
                mean_diff = np.mean(np.abs(diff))
                
                # 保存结果
                self.results = {
                    'time': t,
                    'v1': v1,
                    'v2': v2,
                    'v_out_numpy': v_out_numpy,
                    'time_spice': time_spice,
                    'v_in1_spice': v_in1_spice,
                    'v_in2_spice': v_in2_spice,
                    'v_out_spice': v_out_spice,
                    'v_out_spice_resampled': v_out_spice_resampled,
                    'diff': diff,
                    'max_diff': max_diff,
                    'mean_diff': mean_diff
                }
                
                return self.results
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
    
    def save_results(self, filename='opamp_adder_results.npz'):
        """
        保存仿真结果到NPZ文件
        
        参数:
            filename: 输出文件名
        """
        if self.results is None:
            print("No results to save. Run simulation first.")
            return
            
        output_path = os.path.join(self.output_folder, filename)
        np.savez(output_path, **self.results)
        print(f"Results saved to {output_path}")
    
    def plot_results(self, save_figure=True, figure_name='opamp_adder_plot.png'):
        """
        绘制仿真结果
        
        参数:
            save_figure: 是否保存图形到文件
            figure_name: 图形文件名
        """
        if self.results is None:
            print("No results to plot. Run simulation first.")
            return
            
        # 提取结果数据
        t = self.results['time']
        v1 = self.results['v1']
        v2 = self.results['v2']
        v_out_numpy = self.results['v_out_numpy']
        time_spice = self.results['time_spice']
        v_in1_spice = self.results['v_in1_spice']
        v_in2_spice = self.results['v_in2_spice']
        v_out_spice = self.results['v_out_spice']
        diff = self.results['diff']
        max_diff = self.results['max_diff']
        mean_diff = self.results['mean_diff']
        
        # 创建图形
        plt.figure(figsize=(12, 8))
        
        # 绘制输入信号
        plt.subplot(3, 1, 1)
        plt.plot(t*1e3, v1, 'b-', label='Input 1 (Numpy)')
        plt.plot(time_spice*1e3, v_in1_spice, 'b--', label='Input 1 (NGspice)')
        plt.plot(t*1e3, v2, 'r-', label='Input 2 (Numpy)')
        plt.plot(time_spice*1e3, v_in2_spice, 'r--', label='Input 2 (NGspice)')
        plt.grid(True)
        plt.legend()
        plt.title('Op-Amp Adder Input Signals')
        plt.xlabel('Time (ms)')
        plt.ylabel('Voltage (V)')
        
        # 绘制输出信号
        plt.subplot(3, 1, 2)
        plt.plot(t*1e3, v_out_numpy, 'g-', label='Output (Numpy)')
        plt.plot(time_spice*1e3, v_out_spice, 'r--', label='Output (NGspice)')
        plt.grid(True)
        plt.legend()
        plt.title('Op-Amp Adder Output Signal')
        plt.xlabel('Time (ms)')
        plt.ylabel('Voltage (V)')
        
        # 绘制输出差异
        plt.subplot(3, 1, 3)
        plt.plot(t*1e3, diff*1000, 'k-')  # 显示差异，单位为mV
        plt.grid(True)
        plt.title('NGspice vs Numpy Output Difference')
        plt.xlabel('Time (ms)')
        plt.ylabel('Difference (mV)')
        
        plt.tight_layout()
        
        # 打印统计信息
        print(f"Maximum difference: {max_diff*1000:.6f} mV")
        print(f"Average difference: {mean_diff*1000:.6f} mV")
        
        # 保存图形
        if save_figure:
            figure_path = os.path.join(self.output_folder, figure_name)
            plt.savefig(figure_path, dpi=300)
            print(f"Figure saved to {figure_path}")
            
        plt.show()


def main():
    """主函数，演示如何使用OpAmpAdderSimulation类"""
    # 创建仿真实例
    sim = OpAmpAdderSimulation(output_folder='./temp')
    
    # 生成输入信号
    t, v1, v2 = sim.generate_input_signals(
        t_max=1e-3,      # 1ms仿真时间
        fs=1e6,          # 1MHz采样率
        freq1=5e3,       # 5kHz信号1
        freq2=10e3,      # 10kHz信号2
        amp1=0.5,        # 0.5V振幅
        amp2=0.3         # 0.3V振幅
    )
    
    # 创建网表
    netlist = sim.create_netlist(
        t_max=1e-3,      # 1ms仿真时间
        R1=10e3,         # 10kΩ电阻
        R2=10e3,
        R3=10e3,
        RF=10e3
    )
    
    # 运行仿真
    results = sim.run_simulation(t, v1, v2, netlist, print_netlist=True)
    
    if results:
        # 保存结果
        sim.save_results()
        
        # 绘制结果
        sim.plot_results()


if __name__ == "__main__":
    main()