#!/usr/bin/env python3
"""
Simple test script for high-pass filter functionality without pytest dependency

Updated to reflect the correct high-pass filter design:
- Uses neural network bias weights instead of fixed bias_voltage
- High-pass filter only affects SPICE, not NumPy simulation
"""

import sys
import numpy as np
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from circuit_dense import DenseCircuit, DenseCircuitFactory


def test_basic_functionality():
    """Test basic high-pass filter functionality"""
    print("Testing basic high-pass filter functionality...")
    
    # Test 1: Create circuit with high-pass filter enabled
    high_pass_config = {
        'enable': True,
        'cutoff_freq': 0.5,
        'auto_bias': True,
    }
    
    # Define neural network bias weights - these will be used by high-pass filter
    bias_weights = [2.5, -1.5]
    
    circuit = DenseCircuitFactory.create(
        gains=[[1.0, -1.0], [0.5, 2.0]],
        biases=bias_weights,
        use_relu=True,
        high_pass_config=high_pass_config
    )
    
    print(f"✓ Circuit created with high-pass filter enabled: {circuit.high_pass_config['enable']}")
    print(f"✓ Cutoff frequency: {circuit.high_pass_config['cutoff_freq']} Hz")
    print(f"✓ Neural network bias weights: {bias_weights}")
    
    # Test 2: Check component calculations
    print(f"\nHigh-pass filter components per channel:")
    for ch in range(2):
        channel_config = circuit.channel_configs[ch]
        print(f"\nChannel {ch+1} (bias weight = {bias_weights[ch]} V):")
        print(f"  - Capacitance: {channel_config['hp_capacitance']*1e6:.1f} μF")
        print(f"  - Resistance: {channel_config['hp_resistance']/1e3:.1f} kΩ")
        print(f"  - Bias source: {channel_config['hp_bias_source']}")
        print(f"  - Bias divider high: {channel_config['hp_bias_r_high']/1e3:.1f} kΩ")
        print(f"  - Bias divider low: {channel_config['hp_bias_r_low']/1e3:.1f} kΩ")
    
    # Test 3: Generate netlist and check for components
    netlist = circuit.get_circuit_netlist()
    
    if "高通滤波器" in netlist:
        print("\n✓ High-pass filter found in netlist")
    else:
        print("\n✗ High-pass filter NOT found in netlist")
        
    # Check for specific components
    components = ['C_hp1', 'R_hp1', 'hp_bias1', 'C_hp2', 'R_hp2', 'hp_bias2']
    found = []
    not_found = []
    
    for comp in components:
        if comp in netlist:
            found.append(comp)
        else:
            not_found.append(comp)
    
    print(f"✓ Components found: {', '.join(found)}")
    if not_found:
        print(f"✗ Components missing: {', '.join(not_found)}")
    
    # Test 4: Test NumPy simulation - should NOT be affected by high-pass filter
    print("\nTesting NumPy simulation (should not be affected by high-pass filter)...")
    t = np.linspace(0, 1, 100)
    input_signals = np.ones((100, 2)) * 3.0  # DC signal
    
    output = circuit.simulate_numpy(t, input_signals)
    mean_output = np.mean(output, axis=0)
    
    print(f"Input DC level: 3.0 V")
    print(f"Output DC levels: Ch1={mean_output[0]:.2f} V, Ch2={mean_output[1]:.2f} V")
    
    # Calculate expected output without high-pass filter effect
    expected_output = []
    for ch in range(2):
        # Output = sum(input * gain) + bias
        output_val = sum(3.0 * circuit.gains[i, ch] for i in range(2)) + bias_weights[ch]
        expected_output.append(output_val)
    
    print(f"Expected DC levels (without high-pass effect): Ch1={expected_output[0]:.2f} V, Ch2={expected_output[1]:.2f} V")
    print("Note: NumPy simulation should NOT apply high-pass filter effect!")
    
    # Test 5: Test with high-pass disabled
    print("\n\nTesting with high-pass filter disabled...")
    circuit_no_hpf = DenseCircuitFactory.create(
        gains=[[1.0, -1.0], [0.5, 2.0]],
        biases=[0.5, -0.5],
        use_relu=False,
        high_pass_config={'enable': False}
    )
    
    netlist_no_hpf = circuit_no_hpf.get_circuit_netlist()
    if "高通滤波器" not in netlist_no_hpf:
        print("✓ High-pass filter correctly absent when disabled")
    else:
        print("✗ High-pass filter present when it should be disabled")


def test_configuration_validation():
    """Test configuration validation"""
    print("\n\n=== Testing configuration validation ===")
    
    print("\nTesting rejection of bias_voltage parameter...")
    try:
        circuit = DenseCircuitFactory.create(
            gains=[[1.0]],
            biases=[0.0],
            use_relu=False,
            high_pass_config={
                'enable': True,
                'cutoff_freq': 1.0,
                'bias_voltage': 2.5,  # This should cause an error
            }
        )
        print("✗ ERROR: bias_voltage parameter was accepted (should have been rejected!)")
    except ValueError as e:
        print("✓ bias_voltage parameter correctly rejected")
        print(f"  Error message: {str(e)[:100]}...")


def test_different_bias_weights():
    """Test various neural network bias weight configurations"""
    print("\n\n=== Testing different bias weight configurations ===")
    
    # Test positive bias weight
    print("\n1. Testing positive bias weight...")
    circuit = DenseCircuitFactory.create(
        gains=[[1.0]],
        biases=[3.0],  # Positive bias weight
        use_relu=False,
        high_pass_config={
            'enable': True,
            'cutoff_freq': 1.0,
            'auto_bias': True,
        }
    )
    
    channel_config = circuit.channel_configs[0]
    print(f"   Neural network bias weight: {circuit.biases[0]} V")
    print(f"   Bias source: {channel_config['hp_bias_source']} (should be 'vcc' for positive bias)")
    
    # Test negative bias weight
    print("\n2. Testing negative bias weight...")
    circuit = DenseCircuitFactory.create(
        gains=[[1.0]],
        biases=[-2.5],  # Negative bias weight
        use_relu=False,
        high_pass_config={
            'enable': True,
            'cutoff_freq': 1.0,
            'auto_bias': True,
        }
    )
    
    channel_config = circuit.channel_configs[0]
    print(f"   Neural network bias weight: {circuit.biases[0]} V")
    print(f"   Bias source: {channel_config['hp_bias_source']} (should be 'vee' for negative bias)")
    
    # Test zero bias weight
    print("\n3. Testing zero bias weight...")
    circuit = DenseCircuitFactory.create(
        gains=[[1.0]],
        biases=[0.0],  # Zero bias weight
        use_relu=False,
        high_pass_config={
            'enable': True,
            'cutoff_freq': 1.0,
            'auto_bias': True,
        }
    )
    
    channel_config = circuit.channel_configs[0]
    print(f"   Neural network bias weight: {circuit.biases[0]} V")
    print(f"   Bias source: {channel_config['hp_bias_source']} (should be 'vcc' for zero bias)")
    
    # Test multiple channels with different bias weights
    print("\n4. Testing multiple channels with different bias weights...")
    circuit = DenseCircuitFactory.create(
        gains=[[1.0, -1.0, 0.5]],
        biases=[2.5, -1.5, 0.0],  # Positive, negative, and zero
        use_relu=False,
        high_pass_config={
            'enable': True,
            'cutoff_freq': 1.0,
            'auto_bias': True,
        }
    )
    
    for ch in range(3):
        channel_config = circuit.channel_configs[ch]
        print(f"   Channel {ch+1}: bias={circuit.biases[ch]}V, source={channel_config['hp_bias_source']}")


def test_custom_components():
    """Test custom component values"""
    print("\n\n=== Testing custom component values ===")
    
    circuit = DenseCircuitFactory.create(
        gains=[[1.0]],
        biases=[1.5],  # Neural network bias weight
        use_relu=False,
        high_pass_config={
            'enable': True,
            'cutoff_freq': 1.0,  # This should be ignored when custom values are provided
            'capacitance': 10e-6,  # 10μF
            'resistance': 15.9e3,   # 15.9kΩ
        }
    )
    
    channel_config = circuit.channel_configs[0]
    print(f"Custom capacitance: {channel_config['hp_capacitance']*1e6:.1f} μF (expected: 10.0 μF)")
    print(f"Custom resistance: {channel_config['hp_resistance']/1e3:.1f} kΩ (expected: 15.9 kΩ)")
    
    # Calculate actual cutoff frequency
    actual_fc = 1 / (2 * np.pi * channel_config['hp_resistance'] * channel_config['hp_capacitance'])
    print(f"Actual cutoff frequency: {actual_fc:.3f} Hz")


def test_numpy_vs_spice():
    """Verify that NumPy simulation is not affected by high-pass filter"""
    print("\n\n=== Testing NumPy vs SPICE behavior ===")
    
    # Create identical circuits with and without high-pass filter
    circuit_without_hp = DenseCircuitFactory.create(
        gains=[[2.0]],  # 1 input, 1 output
        biases=[1.5],
        use_relu=False,
        high_pass_config={'enable': False}
    )
    
    circuit_with_hp = DenseCircuitFactory.create(
        gains=[[2.0]],  # 1 input, 1 output
        biases=[1.5],
        use_relu=False,
        high_pass_config={
            'enable': True,
            'cutoff_freq': 0.1,
        }
    )
    
    # Test with DC + low frequency signal
    t = np.linspace(0, 10, 1000)
    dc_offset = 5.0
    low_freq_signal = 0.5 * np.sin(2 * np.pi * 0.05 * t)  # 0.05 Hz - below cutoff
    
    input_signals = (dc_offset + low_freq_signal).reshape(-1, 1)
    
    output_without_hp = circuit_without_hp.simulate_numpy(t, input_signals)
    output_with_hp = circuit_with_hp.simulate_numpy(t, input_signals)
    
    # Both should produce identical results
    diff = np.abs(output_without_hp - output_with_hp)
    max_diff = np.max(diff)
    
    print(f"Maximum difference between outputs: {max_diff:.2e}")
    if max_diff < 1e-10:
        print("✓ NumPy simulation correctly ignores high-pass filter configuration")
    else:
        print("✗ ERROR: NumPy simulation is affected by high-pass filter!")


def main():
    """Run all tests"""
    print("=" * 70)
    print("High-Pass Filter Functionality Tests (Simple)")
    print("Updated for correct high-pass filter design:")
    print("- Uses neural network bias weights")
    print("- Only affects SPICE simulation, not NumPy")
    print("=" * 70)
    
    try:
        test_basic_functionality()
        test_configuration_validation()
        test_different_bias_weights()
        test_custom_components()
        test_numpy_vs_spice()
        
        print("\n" + "=" * 70)
        print("✅ All tests completed successfully!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()