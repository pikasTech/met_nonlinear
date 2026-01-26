#!/usr/bin/env python3
"""
Demonstration of high-pass filter functionality with corrected design

This script demonstrates:
1. High-pass filter uses neural network bias weights
2. High-pass filter only affects SPICE simulation, not NumPy
3. The purpose of high-pass filter as hardware compensation
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from circuit_dense import DenseCircuit, DenseCircuitFactory


def demonstrate_highpass_design():
    """Demonstrate the correct high-pass filter design and purpose"""
    
    print("=" * 70)
    print("High-Pass Filter Design Demonstration")
    print("=" * 70)
    
    # Create test signal with DC offset and frequency components
    duration = 10.0  # seconds
    dt = 0.001  # 1ms timestep
    t = np.arange(0, duration, dt)
    
    # Signal components:
    # 1. DC offset (3V) - represents input offset error
    # 2. Low frequency sine (0.1 Hz)
    # 3. Higher frequency sine (5 Hz)
    dc_offset = 3.0
    low_freq = 0.5 * np.sin(2 * np.pi * 0.1 * t)
    high_freq = 0.2 * np.sin(2 * np.pi * 5 * t)
    
    input_signal = dc_offset + low_freq + high_freq
    
    # Neural network parameters
    gains = [[2.0]]  # Simple gain of 2
    bias_weight = 1.5  # This is the neural network's trained bias weight
    
    print(f"\nNeural Network Parameters:")
    print(f"  Gain: {gains[0][0]}")
    print(f"  Bias weight: {bias_weight} V")
    
    # Create three circuits for comparison
    # 1. Without high-pass filter (baseline)
    circuit_no_hpf = DenseCircuitFactory.create(
        gains=gains,
        biases=[bias_weight],
        use_relu=False,
        high_pass_config={'enable': False}
    )
    
    # 2. With high-pass filter (for SPICE hardware compensation)
    high_pass_config = {
        'enable': True,
        'cutoff_freq': 0.5,  # 0.5 Hz cutoff
        'auto_bias': True,
        # Note: NO bias_voltage parameter!
        # The circuit will use the neural network bias weight
    }
    circuit_with_hpf = DenseCircuitFactory.create(
        gains=gains,
        biases=[bias_weight],
        use_relu=False,
        high_pass_config=high_pass_config
    )
    
    print(f"\nHigh-Pass Filter Configuration:")
    print(f"  Enabled: {circuit_with_hpf.high_pass_config['enable']}")
    print(f"  Cutoff frequency: {circuit_with_hpf.high_pass_config['cutoff_freq']} Hz")
    print(f"  Will use neural network bias: {bias_weight} V")
    
    # Check the calculated components
    channel_config = circuit_with_hpf.channel_configs[0]
    print(f"\nCalculated High-Pass Components:")
    print(f"  Capacitance: {channel_config['hp_capacitance']*1e6:.1f} μF")
    print(f"  Resistance: {channel_config['hp_resistance']/1e3:.1f} kΩ")
    print(f"  Bias source: {channel_config['hp_bias_source']}")
    
    # Run NumPy simulations
    print("\n" + "-" * 50)
    print("Running NumPy simulations...")
    print("IMPORTANT: NumPy is ideal simulation - high-pass filter should NOT affect it!")
    print("-" * 50)
    
    input_2d = input_signal.reshape(-1, 1)
    output_no_hpf = circuit_no_hpf.simulate_numpy(t, input_2d)
    output_with_hpf = circuit_with_hpf.simulate_numpy(t, input_2d)
    
    # Verify that outputs are identical (high-pass should not affect NumPy)
    diff = np.abs(output_no_hpf - output_with_hpf)
    max_diff = np.max(diff)
    print(f"\nMaximum difference between NumPy outputs: {max_diff:.2e}")
    if max_diff < 1e-10:
        print("✓ Confirmed: High-pass filter does NOT affect NumPy simulation")
    else:
        print("✗ ERROR: High-pass filter is affecting NumPy simulation!")
    
    # Create visualization
    fig, axes = plt.subplots(4, 1, figsize=(12, 12))
    
    # Plot 1: Input signal
    ax1 = axes[0]
    ax1.plot(t[:1000], input_signal[:1000], 'b-', linewidth=1)
    ax1.set_title('Input Signal (DC + 0.1Hz + 5Hz components)', fontsize=12)
    ax1.set_ylabel('Voltage (V)')
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=dc_offset, color='r', linestyle='--', alpha=0.5, 
                label=f'DC level: {dc_offset}V (represents hardware offset error)')
    ax1.legend()
    
    # Plot 2: NumPy output (both circuits produce same result)
    ax2 = axes[1]
    ax2.plot(t[:1000], output_no_hpf[:1000, 0], 'g-', linewidth=2, label='No HPF')
    ax2.plot(t[:1000], output_with_hpf[:1000, 0], 'r--', linewidth=1, label='With HPF')
    ax2.set_title('NumPy Simulation Output (Ideal - No Hardware Errors)', fontsize=12)
    ax2.set_ylabel('Voltage (V)')
    ax2.grid(True, alpha=0.3)
    expected_dc = dc_offset * gains[0][0] + bias_weight
    ax2.axhline(y=expected_dc, color='k', linestyle=':', alpha=0.5, 
                label=f'Expected DC: {expected_dc}V')
    ax2.legend()
    ax2.text(0.5, 0.95, 'Both traces overlap - HPF does not affect NumPy!', 
             transform=ax2.transAxes, ha='center', va='top',
             bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
    
    # Plot 3: Simulated SPICE behavior (what would happen in hardware)
    ax3 = axes[2]
    # Simulate what SPICE would show WITH hardware errors
    hardware_offset_error = 0.3  # Simulated op-amp offset
    spice_no_hpf = output_no_hpf + hardware_offset_error
    ax3.plot(t[:1000], spice_no_hpf[:1000, 0], 'b-', linewidth=1)
    ax3.set_title('Simulated SPICE Output WITHOUT High-Pass Filter (Has Hardware Errors)', fontsize=12)
    ax3.set_ylabel('Voltage (V)')
    ax3.grid(True, alpha=0.3)
    actual_dc = expected_dc + hardware_offset_error
    ax3.axhline(y=actual_dc, color='r', linestyle='--', alpha=0.5, 
                label=f'Actual DC: {actual_dc}V (includes {hardware_offset_error}V error)')
    ax3.axhline(y=expected_dc, color='g', linestyle=':', alpha=0.5, 
                label=f'Desired DC: {expected_dc}V')
    ax3.legend()
    
    # Plot 4: What high-pass filter would do in SPICE
    ax4 = axes[3]
    # High-pass filter would remove DC and restore to bias weight
    # This is a simplified visualization
    time_constant = 1 / (2 * np.pi * 0.5)  # RC time constant
    # Exponential settling to bias level
    settling = np.exp(-t / time_constant)
    # AC coupled signal centered at bias weight
    ac_component = (input_signal - dc_offset) * gains[0][0]
    spice_with_hpf = bias_weight + ac_component * (1 - settling * 0.8)
    
    ax4.plot(t[:2000], spice_with_hpf[:2000], 'r-', linewidth=1)
    ax4.set_title('Simulated SPICE Output WITH High-Pass Filter (Hardware Errors Compensated)', fontsize=12)
    ax4.set_xlabel('Time (s)')
    ax4.set_ylabel('Voltage (V)')
    ax4.grid(True, alpha=0.3)
    ax4.axhline(y=bias_weight, color='g', linestyle='--', alpha=0.5, 
                label=f'Neural network bias: {bias_weight}V (restored by HPF)')
    ax4.legend()
    ax4.set_xlim(0, 2)  # Show first 2 seconds for settling
    
    plt.tight_layout()
    
    # Generate example netlist snippet
    print("\n" + "=" * 70)
    print("Example SPICE Netlist (with high-pass filter):")
    print("=" * 70)
    netlist = circuit_with_hpf.get_circuit_netlist()
    
    # Extract and show relevant parts
    lines = netlist.split('\n')
    hpf_lines = [line for line in lines if any(x in line for x in ['高通滤波器', 'C_hp', 'R_hp', 'hp_bias'])]
    
    print("\nHigh-pass filter components in netlist:")
    for line in hpf_lines[:10]:  # Show first 10 relevant lines
        print(f"  {line.strip()}")
    
    print("\n" + "=" * 70)
    print("Key Insights:")
    print("=" * 70)
    print("1. High-pass filter uses neural network bias weight, not a fixed value")
    print("2. It only affects SPICE simulation (hardware), not NumPy (ideal)")
    print("3. Purpose: Compensate for op-amp offset, diode drops, etc.")
    print("4. Each output channel uses its own bias weight")
    
    return fig


def demonstrate_multi_channel():
    """Demonstrate multi-channel operation with different bias weights"""
    
    print("\n\n" + "=" * 70)
    print("Multi-Channel High-Pass Filter Demonstration")
    print("=" * 70)
    
    # Create a 2-input, 3-output system
    gains = [[1.0, -1.0, 0.5], [2.0, 0.0, -0.5]]
    bias_weights = [2.5, -1.5, 0.0]  # Different bias for each output channel
    
    print(f"\nNeural Network Configuration:")
    print(f"  Inputs: 2")
    print(f"  Outputs: 3")
    print(f"  Bias weights: {bias_weights}")
    
    # Create circuit with high-pass filter
    circuit = DenseCircuitFactory.create(
        gains=gains,
        biases=bias_weights,
        use_relu=False,
        high_pass_config={
            'enable': True,
            'cutoff_freq': 1.0,
            'auto_bias': True,
        }
    )
    
    print(f"\nHigh-Pass Filter Configuration per Channel:")
    for ch in range(3):
        config = circuit.channel_configs[ch]
        print(f"\n  Channel {ch+1} (bias = {bias_weights[ch]}V):")
        print(f"    - Bias source: {config['hp_bias_source']}")
        print(f"    - Divider high: {config['hp_bias_r_high']/1e3:.1f} kΩ")
        print(f"    - Divider low: {config['hp_bias_r_low']/1e3:.1f} kΩ")
        
        # Calculate the actual bias voltage from divider
        if config['hp_bias_source'] == 'vcc':
            v_source = 15.0
        else:
            v_source = -15.0
        
        v_bias = v_source * config['hp_bias_r_low'] / (config['hp_bias_r_high'] + config['hp_bias_r_low'])
        print(f"    - Calculated bias voltage: {v_bias:.3f}V")


def main():
    """Run all demonstrations"""
    try:
        # Run main demonstration
        fig = demonstrate_highpass_design()
        
        # Run multi-channel demonstration
        demonstrate_multi_channel()
        
        # Show plot
        plt.show()
        
        print("\n✅ Demonstration completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()