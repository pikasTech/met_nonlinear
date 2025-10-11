import numpy as np
import matplotlib.pyplot as plt
from simulation import CircuitSimulation
from diff_amp_test import SimpleDiffAmpCircuit

# 测试差分运放电路的相位反转问题

def test_diff_amp_phase():
    """测试差分运放的相位反转问题"""

    # 创建仿真环境
    sim = CircuitSimulation(output_folder='./temp')

    # 测试参数
    t_max = 1e-3
    fs = 1e6

    # 生成时间轴和测试信号
    t = np.arange(0, t_max, 1/fs)

    # 创建两个频率不同的信号作为输入
    input_signals = np.zeros((2, len(t)))
    input_signals[0] = 0.5 * np.sin(2 * np.pi * 1e3 * t)  # 1kHz正弦波
    input_signals[1] = 0.2 * np.sin(2 * np.pi * 3e3 * t)  # 3kHz正弦波

    # 创建差分运放电路 - 正常配置
    circuit_normal = SimpleDiffAmpCircuit(inverted=False)
    
    # 运行仿真 - 正常配置
    result_normal = sim.run_simulation_once(t, input_signals, circuit_normal, print_netlist=True)
    
    # 创建差分运放电路 - 反转配置
    circuit_inverted = SimpleDiffAmpCircuit(inverted=True)
    
    # 运行仿真 - 反转配置
    result_inverted = sim.run_simulation_once(t, input_signals, circuit_inverted, print_netlist=True)

    # 绘制差分输入信号
    diff_input = input_signals[0] - input_signals[1]
    
    # 绘制结果比较图
    plt.figure(figsize=(15, 10))
    
    # 1. 绘制输入信号
    plt.subplot(3, 1, 1)
    plt.plot(t*1e3, input_signals[0], 'b-', label='正向输入 (V+)')
    plt.plot(t*1e3, input_signals[1], 'r-', label='负向输入 (V-)')
    plt.plot(t*1e3, diff_input, 'g--', label='差分输入 (V+ - V-)')
    plt.xlabel('时间 (ms)')
    plt.ylabel('电压 (V)')
    plt.title('差分运放输入信号')
    plt.grid(True)
    plt.legend()
    
    # 2. 绘制正常配置输出与反转配置输出对比
    plt.subplot(3, 1, 2)
    plt.plot(t*1e3, result_normal['v_out_numpy'], 'b-', label='正常配置 - NumPy计算')
    plt.plot(t*1e3, result_normal['v_out_spice_resampled'], 'b--', label='正常配置 - SPICE仿真')
    plt.plot(t*1e3, result_inverted['v_out_numpy'], 'r-', label='反转配置 - NumPy计算')
    plt.plot(t*1e3, result_inverted['v_out_spice_resampled'], 'r--', label='反转配置 - SPICE仿真')
    plt.xlabel('时间 (ms)')
    plt.ylabel('电压 (V)')
    plt.title('差分运放输出对比')
    plt.grid(True)
    plt.legend()
    
    # 3. 正常配置与反转配置的和
    plt.subplot(3, 1, 3)
    sum_numpy = result_normal['v_out_numpy'] + result_inverted['v_out_numpy']
    sum_spice = result_normal['v_out_spice_resampled'] + result_inverted['v_out_spice_resampled']
    plt.plot(t*1e3, sum_numpy, 'g-', label='和 (NumPy计算)')
    plt.plot(t*1e3, sum_spice, 'g--', label='和 (SPICE仿真)')
    plt.plot(t*1e3, np.zeros_like(t), 'k--', linewidth=1)  # 零线
    plt.xlabel('时间 (ms)')
    plt.ylabel('电压 (V)')
    plt.title('正常配置与反转配置输出之和 (应接近零)')
    plt.grid(True)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('./temp/diff_amp_phase_test.png', dpi=300)
    plt.show()

    # 显示一些统计信息，帮助判断相位关系
    normal_max = np.max(result_normal['v_out_numpy'])
    inverted_max = np.max(result_inverted['v_out_numpy'])
    sum_max = np.max(np.abs(sum_numpy))
    print(f"正常配置输出最大值: {normal_max:.4f}V")
    print(f"反转配置输出最大值: {inverted_max:.4f}V")
    print(f"两者之和的最大绝对值: {sum_max:.4f}V")
    print(f"两者之和与各自幅度的比例: {sum_max/(normal_max + np.abs(inverted_max)):.4f}")

    # 检查正常配置下SPICE与NumPy计算的相位关系
    normal_numpy_spice_corr = np.corrcoef(result_normal['v_out_numpy'], result_normal['v_out_spice_resampled'])[0,1]
    print(f"正常配置: NumPy与SPICE相关性: {normal_numpy_spice_corr:.6f}")
    
    # 检查反转配置下SPICE与NumPy计算的相位关系
    inverted_numpy_spice_corr = np.corrcoef(result_inverted['v_out_numpy'], result_inverted['v_out_spice_resampled'])[0,1]
    print(f"反转配置: NumPy与SPICE相关性: {inverted_numpy_spice_corr:.6f}")
    
    # 检查正常配置与反转配置的相关性
    normal_inverted_corr = np.corrcoef(result_normal['v_out_numpy'], result_inverted['v_out_numpy'])[0,1]
    print(f"正常配置与反转配置相关性: {normal_inverted_corr:.6f}")

def compare_with_signed_adder():
    """比较简单差分运放与带符号加法器的相位关系"""
    from cicuit_VMM import SignedAdderCircuit
    
    # 创建仿真环境
    sim = CircuitSimulation(output_folder='./temp')

    # 测试参数
    t_max = 1e-3
    fs = 1e6

    # 生成时间轴和测试信号
    t = np.arange(0, t_max, 1/fs)

    # 创建简单的信号作为输入
    input_signal = 0.5 * np.sin(2 * np.pi * 1e3 * t)  # 1kHz正弦波
    
    # 差分运放测试
    diff_amp_inputs = np.zeros((2, len(t)))
    diff_amp_inputs[0] = input_signal  # 正向输入
    diff_amp_inputs[1] = 0 * t         # 负向输入为零

    # 创建差分运放电路 - 正常配置和反转配置
    circuit_normal = SimpleDiffAmpCircuit(inverted=False)
    circuit_inverted = SimpleDiffAmpCircuit(inverted=True)
    
    # 运行差分运放仿真
    result_normal = sim.run_simulation_once(t, diff_amp_inputs, circuit_normal)
    result_inverted = sim.run_simulation_once(t, diff_amp_inputs, circuit_inverted)
    
    # 带符号加法器测试
    # 测试正增益和负增益的情况
    positive_gain_circuit = SignedAdderCircuit(gains=[1.0])
    negative_gain_circuit = SignedAdderCircuit(gains=[-1.0])
    
    # 运行带符号加法器仿真
    result_pos_gain = sim.run_simulation_once(t, input_signal, positive_gain_circuit)
    result_neg_gain = sim.run_simulation_once(t, input_signal, negative_gain_circuit)
    
    # 绘制结果比较图
    plt.figure(figsize=(15, 10))
    
    # 1. 绘制输入信号
    plt.subplot(3, 1, 1)
    plt.plot(t*1e3, input_signal, 'b-', label='输入信号')
    plt.xlabel('时间 (ms)')
    plt.ylabel('电压 (V)')
    plt.title('测试输入信号')
    plt.grid(True)
    plt.legend()
    
    # 2. 差分运放输出
    plt.subplot(3, 1, 2)
    plt.plot(t*1e3, result_normal['v_out_spice_resampled'], 'b-', label='差分运放(正常配置)')
    plt.plot(t*1e3, result_inverted['v_out_spice_resampled'], 'r-', label='差分运放(反转配置)')
    plt.xlabel('时间 (ms)')
    plt.ylabel('电压 (V)')
    plt.title('差分运放输出')
    plt.grid(True)
    plt.legend()
    
    # 3. 带符号加法器输出
    plt.subplot(3, 1, 3)
    plt.plot(t*1e3, result_pos_gain['v_out_spice_resampled'], 'g-', label='带符号加法器(正增益)')
    plt.plot(t*1e3, result_neg_gain['v_out_spice_resampled'], 'm-', label='带符号加法器(负增益)')
    plt.xlabel('时间 (ms)')
    plt.ylabel('电压 (V)')
    plt.title('带符号加法器输出')
    plt.grid(True)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('./temp/diff_amp_vs_signed_adder.png', dpi=300)
    plt.show()
    
    # 计算相关性来检查相位关系
    # 差分运放正常配置与带符号加法器正增益
    corr_normal_pos = np.corrcoef(result_normal['v_out_spice_resampled'], result_pos_gain['v_out_spice_resampled'])[0,1]
    print(f"差分运放正常配置与带符号加法器正增益的相关性: {corr_normal_pos:.6f}")
    
    # 差分运放反转配置与带符号加法器正增益
    corr_inverted_pos = np.corrcoef(result_inverted['v_out_spice_resampled'], result_pos_gain['v_out_spice_resampled'])[0,1]
    print(f"差分运放反转配置与带符号加法器正增益的相关性: {corr_inverted_pos:.6f}")
    
    # 差分运放正常配置与带符号加法器负增益
    corr_normal_neg = np.corrcoef(result_normal['v_out_spice_resampled'], result_neg_gain['v_out_spice_resampled'])[0,1]
    print(f"差分运放正常配置与带符号加法器负增益的相关性: {corr_normal_neg:.6f}")
    
    # 差分运放反转配置与带符号加法器负增益
    corr_inverted_neg = np.corrcoef(result_inverted['v_out_spice_resampled'], result_neg_gain['v_out_spice_resampled'])[0,1]
    print(f"差分运放反转配置与带符号加法器负增益的相关性: {corr_inverted_neg:.6f}")
    
    # 带符号加法器正增益与负增益的相关性
    corr_pos_neg = np.corrcoef(result_pos_gain['v_out_spice_resampled'], result_neg_gain['v_out_spice_resampled'])[0,1]
    print(f"带符号加法器正增益与负增益的相关性: {corr_pos_neg:.6f}")

if __name__ == "__main__":
    print("=== 测试差分运放的相位反转问题 ===")
    test_diff_amp_phase()
    
    print("\n=== 比较差分运放与带符号加法器的相位关系 ===")
    compare_with_signed_adder()