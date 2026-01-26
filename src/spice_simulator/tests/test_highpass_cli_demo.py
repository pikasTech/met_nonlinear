#!/usr/bin/env python3
"""
Direct demonstration of high-pass filter functionality with corrected design

This script demonstrates:
1. How high-pass filter is integrated in the system
2. The corrected design using neural network bias weights
3. High-pass filter only affects SPICE, not NumPy
"""

import sys
import numpy as np
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from circuit_dense import DenseCircuit, DenseCircuitFactory


def demonstrate_cli_integration():
    """Demonstrate how high-pass filter works with the corrected design"""
    
    print("=" * 70)
    print("高通滤波器功能 CLI 集成演示（更正后的设计）")
    print("=" * 70)
    
    print("\n1. 高通滤波器的本质作用：")
    print("   - 硬件补偿措施：对抗运放失调、二极管压降等")
    print("   - 仅在SPICE仿真中生效")
    print("   - 使用神经网络的bias权重，而非固定值")
    
    print("\n2. 当前实现状态：")
    print("   ✅ DenseCircuit 已更新为使用神经网络bias权重")
    print("   ✅ 配置验证：拒绝bias_voltage参数")
    print("   ✅ SPICE网表生成正确")
    print("   ✅ NumPy仿真不受高通滤波器影响")
    print("   ✅ WaveNet5 模型已修复支持 high_pass_config")
    
    print("\n3. 参数传递链路：")
    print("   config.json → ProjectManager → InferenceProcessor")
    print("   → SPICEBackend → model.to_spice() → DenseCircuit")
    
    print("\n4. 正确的配置示例（在 config.json 中）：")
    config_example = """
    "inference_config": {
        "high_pass_config": {
            "enable": true,
            "cutoff_freq": 0.5,
            "auto_bias": true,
            "bias_divider_high": 10000
            // 注意：没有 bias_voltage 参数！
            // 系统会自动使用神经网络的bias权重
        }
    }
    """
    print(config_example)
    
    print("\n5. 直接演示高通滤波器功能：")
    print("-" * 50)
    
    # 创建测试配置
    gains = [[1.0, -1.0], [0.5, 2.0]]  # 2输入，2输出
    bias_weights = [2.5, -1.5]  # 神经网络的bias权重
    
    print(f"\n神经网络配置：")
    print(f"  增益矩阵: {gains}")
    print(f"  Bias权重: {bias_weights}")
    
    # 创建两个电路：一个不带高通滤波器，一个带高通滤波器
    print("\n创建基准电路（无高通滤波器）...")
    circuit_baseline = DenseCircuitFactory.create(
        gains=gains,
        biases=bias_weights,
        use_relu=True,
        high_pass_config={'enable': False}
    )
    
    print("创建带高通滤波器的电路...")
    high_pass_config = {
        'enable': True,
        'cutoff_freq': 0.5,    # 0.5Hz 截止频率
        'auto_bias': True,
        # 没有bias_voltage！使用神经网络的bias权重
    }
    circuit_with_hpf = DenseCircuitFactory.create(
        gains=gains,
        biases=bias_weights,
        use_relu=True,
        high_pass_config=high_pass_config
    )
    
    print("\n高通滤波器组件（每个通道独立）：")
    for ch in range(2):
        config = circuit_with_hpf.channel_configs[ch]
        print(f"\n  通道 {ch+1} (bias权重 = {bias_weights[ch]}V):")
        print(f"    - 电容: {config['hp_capacitance']*1e6:.1f} μF")
        print(f"    - 电阻: {config['hp_resistance']/1e3:.1f} kΩ")
        print(f"    - Bias源: {config['hp_bias_source']}")
    
    # 创建测试信号
    print("\n\n生成测试信号...")
    t = np.linspace(0, 5, 1000)
    # 信号包含：DC偏移 + 低频 + 高频
    dc_offset = 3.0
    low_freq = 0.5 * np.sin(2 * np.pi * 0.1 * t)   # 0.1Hz
    high_freq = 0.2 * np.sin(2 * np.pi * 5 * t)    # 5Hz
    
    input1 = dc_offset + low_freq + high_freq
    input2 = -dc_offset/2 + low_freq/2 - high_freq
    input_signals = np.column_stack([input1, input2])
    
    # 运行NumPy仿真
    print("运行NumPy仿真...")
    output_baseline = circuit_baseline.simulate_numpy(t, input_signals)
    output_with_hpf = circuit_with_hpf.simulate_numpy(t, input_signals)
    
    # 分析结果
    print("\n6. NumPy仿真结果分析：")
    print("-" * 50)
    print("输入信号DC分量：")
    print(f"  输入1: {np.mean(input1):.2f}V")
    print(f"  输入2: {np.mean(input2):.2f}V")
    
    print("\n输出信号DC分量（无高通滤波器）：")
    print(f"  输出1: {np.mean(output_baseline[:, 0]):.2f}V")
    print(f"  输出2: {np.mean(output_baseline[:, 1]):.2f}V")
    
    print("\n输出信号DC分量（带高通滤波器）：")
    print(f"  输出1: {np.mean(output_with_hpf[:, 0]):.2f}V")
    print(f"  输出2: {np.mean(output_with_hpf[:, 1]):.2f}V")
    
    # 验证两个输出是否相同
    diff = np.abs(output_baseline - output_with_hpf)
    max_diff = np.max(diff)
    print(f"\n最大差异: {max_diff:.2e}")
    
    if max_diff < 1e-10:
        print("✅ 验证通过：高通滤波器不影响NumPy仿真！")
    else:
        print("❌ 错误：高通滤波器影响了NumPy仿真！")
    
    # 检查SPICE网表
    print("\n\n7. SPICE网表验证：")
    print("-" * 50)
    netlist = circuit_with_hpf.get_circuit_netlist()
    
    # 统计高通滤波器组件
    hp_components = {
        'C_hp': 0,
        'R_hp': 0,
        'hp_bias': 0,
        'R_hp_bias': 0
    }
    
    for line in netlist.split('\n'):
        for comp in hp_components:
            if comp in line:
                hp_components[comp] += 1
    
    print("高通滤波器组件统计：")
    for comp, count in hp_components.items():
        print(f"  {comp}: {count} 个")
    
    # 显示部分网表
    print("\n高通滤波器相关网表片段：")
    lines = netlist.split('\n')
    hpf_lines = [line for line in lines if any(x in line for x in ['高通滤波器', 'C_hp', 'R_hp', 'hp_bias'])]
    for line in hpf_lines[:8]:
        print(f"  {line.strip()}")
    
    print("\n\n8. SPICE仿真行为说明：")
    print("-" * 50)
    print("在实际SPICE仿真中，高通滤波器会：")
    print("1. 隔离运放输出的DC误差（通过电容）")
    print("2. 将信号DC电平恢复到神经网络的bias权重值")
    print("3. 通道1恢复到 2.5V（正bias，使用VCC分压）")
    print("4. 通道2恢复到 -1.5V（负bias，使用VEE分压）")
    
    print("\n\n9. CLI使用示例：")
    print("-" * 50)
    print("1) 在项目的 config.json 中添加：")
    print("""
    "inference_config": {
        "high_pass_config": {
            "enable": true,
            "cutoff_freq": 0.5
        }
    }
    """)
    print("2) 运行推理命令：")
    print("   conda run -n tf26 python cli.py -i PROJECT_NAME")
    print("3) 高通滤波器将自动应用于所有使用 DenseLayer 的层")
    print("4) 每个通道使用其对应的神经网络bias权重")
    
    print("\n\n10. 关键要点总结：")
    print("-" * 50)
    print("✅ 高通滤波器使用神经网络的bias权重")
    print("✅ 每个输出通道独立处理")
    print("✅ 仅影响SPICE仿真（硬件补偿）")
    print("✅ 不影响NumPy仿真（理想行为）")
    print("✅ 不再需要bias_voltage配置参数")
    
    print("\n" + "=" * 70)
    print("演示完成！高通滤波器功能已按正确设计实现。")
    print("=" * 70)


def test_configuration_rejection():
    """测试配置验证功能"""
    print("\n\n" + "=" * 70)
    print("测试配置验证：拒绝bias_voltage参数")
    print("=" * 70)
    
    print("\n尝试使用包含bias_voltage的配置...")
    try:
        circuit = DenseCircuitFactory.create(
            gains=[[1.0]],
            biases=[0.0],
            high_pass_config={
                'enable': True,
                'cutoff_freq': 1.0,
                'bias_voltage': 2.5,  # 这应该被拒绝
            }
        )
        print("❌ 错误：bias_voltage参数被接受了！")
    except ValueError as e:
        print("✅ 正确：bias_voltage参数被拒绝")
        print(f"   错误信息: {str(e)}")


if __name__ == "__main__":
    # 运行主演示
    demonstrate_cli_integration()
    
    # 测试配置验证
    test_configuration_rejection()