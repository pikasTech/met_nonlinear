from spicelib.sim.sim_runner import SimRunner
from spicelib.editor.spice_editor import SpiceEditor
from spicelib.simulators.ngspice_simulator import NGspiceSimulator
from spicelib import RawRead
import matplotlib.pyplot as plt
import tempfile
import os

# 创建一个简单的RC电路网表
netlist_text = """* RC电路示例 - NGspice仿真
V1 in 0 PULSE(0 5 0 1n 1n 1m 2m)
R1 in out 1k
C1 out 0 1u
.tran 1u 5m
.save all
.end
"""

# 创建临时网表文件
with tempfile.NamedTemporaryFile(suffix='.net', delete=False, mode='w') as f:
    f.write(netlist_text)
    temp_netlist_path = f.name

# 指定NGspice路径
ngspice_path = r".\Spice64\bin\ngspice.exe"

# 创建一个SimRunner实例，指定simulator为NGspiceSimulator
runner = SimRunner(output_folder='./temp', simulator=NGspiceSimulator.create_from(ngspice_path))

# 创建网表 - 使用临时文件路径而不是None
netlist = SpiceEditor(temp_netlist_path)

# 可选：修改网表参数
netlist['R1'].value = '2k'  # 将R1电阻值改为2k
netlist['C1'].value = '0.5u'  # 将C1电容值改为0.5uF

# 仿真并等待完成
raw_file, log_file = runner.run_now(netlist)

print(f"仿真完成!\n原始数据文件: {raw_file}\n日志文件: {log_file}")

# 处理仿真结果
if raw_file:
    raw_data = RawRead(raw_file)
    
    # 获取时间轴和输出电压
    time = raw_data.get_trace('time')
    vout = raw_data.get_trace('v(out)')
    vin = raw_data.get_trace('v(in)')
    
    # 绘制结果
    plt.figure(figsize=(10, 6))
    plt.plot(time.get_wave(0), vin.get_wave(0), label='Input Voltage')
    plt.plot(time.get_wave(0), vout.get_wave(0), label='Output Voltage')
    plt.xlabel('Time (s)')
    plt.ylabel('Voltage (V)')
    plt.title('RC Circuit Simulation')
    plt.legend()
    plt.grid(True)
    plt.show()

# 打印仿真统计信息
print('成功/总计仿真: ' + str(runner.okSim) + '/' + str(runner.runno))

# 清理临时文件
os.unlink(temp_netlist_path)