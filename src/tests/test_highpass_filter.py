#!/usr/bin/env python3
"""
High-pass filter functionality test script for circuit_dense.py

This script tests the high-pass filter implementation in the DenseCircuit class,
including:
1. Configuration parsing and validation
2. Component value calculations
3. SPICE netlist generation
4. NumPy simulation
"""

import sys
import os
import numpy as np
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from spice_simulator.circuit_dense import DenseCircuit, DenseCircuitFactory


def test_highpass_config_parsing():
    """Test that high-pass filter configuration is correctly parsed"""
    print("\n=== Testing High-Pass Filter Configuration Parsing ===")

    # Test 1: Default configuration (disabled)
    circuit = DenseCircuitFactory.create(
        gains=[[1.0, -1.0], [0.5, 2.0]],
        biases=[0.0, 0.0],
        use_relu=False
    )
    assert circuit.high_pass_config['enable'] == False
    print("✓ Default configuration: high-pass filter disabled")

    # Test 2: Enabled configuration with custom parameters (no bias_voltage)
    # Note: bias is auto-calculated from bias weights, so use non-zero values
    high_pass_config = {
        'enable': True,
        'cutoff_freq': 0.5,
    }
    circuit = DenseCircuitFactory.create(
        gains=[[1.0, -1.0], [0.5, 2.0]],
        biases=[2.5, -2.5],  # Use non-zero biases for HPF
        use_relu=False,
        high_pass_config=high_pass_config
    )
    assert circuit.high_pass_config['enable'] == True
    assert circuit.high_pass_config['cutoff_freq'] == 0.5
    print("✓ Custom configuration parsed correctly")

    # Test 3: Partial configuration (testing defaults)
    high_pass_config = {
        'enable': True,
        'cutoff_freq': 1.0,
    }
    circuit = DenseCircuitFactory.create(
        gains=[[1.0, -1.0], [0.5, 2.0]],
        biases=[1.0, -1.0],
        use_relu=False,
        high_pass_config=high_pass_config
    )
    assert circuit.high_pass_config['enable'] == True
    assert circuit.high_pass_config['cutoff_freq'] == 1.0
    print("✓ Partial configuration with defaults")


def test_component_calculations():
    """Test high-pass filter component calculations"""
    print("\n=== Testing Component Calculations ===")

    # Test with auto-calculated components
    # Note: Use non-zero bias for valid bias divider calculation
    high_pass_config = {
        'enable': True,
        'cutoff_freq': 0.5,  # 0.5 Hz
    }
    circuit = DenseCircuitFactory.create(
        gains=[[1.0], [2.0]],  # 2 input, 1 output
        biases=[2.5],  # Non-zero bias for valid HPF calculation
        use_relu=False,
        high_pass_config=high_pass_config
    )

    # Check calculated values
    channel_config = circuit.channel_configs[0]

    # Expected capacitance (default)
    expected_C = 1e-5  # 10μF
    assert channel_config['hp_capacitance'] == expected_C
    print(f"✓ Capacitance: {channel_config['hp_capacitance']*1e6:.1f} μF")

    # Expected resistance: R = 1 / (2π * f * C)
    expected_R = 1 / (2 * np.pi * 0.5 * expected_C)
    assert abs(channel_config['hp_resistance'] - expected_R) < 1  # Small tolerance
    print(f"✓ Resistance: {channel_config['hp_resistance']/1e3:.1f} kΩ (for fc = 0.5 Hz)")

    # Bias source is auto-determined from bias weights
    assert channel_config['hp_bias_source'] in ['vcc', 'vee']
    print(f"✓ Bias source: {channel_config['hp_bias_source']} (auto-determined from bias)")


def test_netlist_generation():
    """Test SPICE netlist generation with high-pass filter"""
    print("\n=== Testing Netlist Generation ===")

    # Create circuit with high-pass filter enabled
    # Use non-zero biases for valid HPF calculation
    high_pass_config = {
        'enable': True,
        'cutoff_freq': 1.0,
    }
    circuit = DenseCircuitFactory.create(
        gains=[[1.0, -1.0]],  # 1 input, 2 outputs
        biases=[2.5, -2.5],
        use_relu=True,
        high_pass_config=high_pass_config
    )

    netlist = circuit.get_circuit_netlist()

    # Check for high-pass filter components in netlist
    # With bias_voltage removed, the netlist should not contain bias voltage divider
    # but should still contain the HPF circuit
    assert "一阶无源高通滤波器" in netlist
    print("✓ High-pass filter circuit found in netlist")

    # Check for specific components
    assert "C_hp1" in netlist  # Capacitor for channel 1
    assert "R_hp1" in netlist  # Resistor for channel 1
    print("✓ All high-pass filter components present")

    # Check that high-pass filter is between op-amp output and ReLU input
    assert "out1_pre out1_hp" in netlist  # Capacitor connection
    print("✓ High-pass filter correctly positioned in signal path")

    # Test with high-pass filter disabled
    circuit = DenseCircuitFactory.create(
        gains=[[1.0]],
        biases=[0.0],
        use_relu=True,
        high_pass_config={'enable': False}
    )
    netlist = circuit.get_circuit_netlist()
    assert "高通滤波器" not in netlist
    print("✓ High-pass filter not in netlist when disabled")


def test_numpy_simulation():
    """Test NumPy simulation with high-pass filter effect"""
    print("\n=== Testing NumPy Simulation ===")

    # Create circuit with high-pass filter
    high_pass_config = {
        'enable': True,
        'cutoff_freq': 1.0,
    }
    circuit = DenseCircuitFactory.create(
        gains=[[2.0]],  # Simple gain of 2
        biases=[1.0],   # Add 1V bias
        use_relu=False,
        high_pass_config=high_pass_config
    )

    # Create test signal with DC offset
    t = np.linspace(0, 10, 1000)
    dc_offset = 3.0
    signal = dc_offset + 0.5 * np.sin(2 * np.pi * 0.1 * t)  # DC + 0.1Hz sine
    input_signals = signal.reshape(-1, 1)

    # Run simulation
    output = circuit.simulate_numpy(t, input_signals)

    # Verify simulation completed successfully
    assert output is not None
    assert len(output) == len(input_signals)
    print(f"✓ Simulation completed successfully, output shape: {output.shape}")

    # Test with high-pass filter disabled
    circuit.high_pass_config['enable'] = False
    output_no_hpf = circuit.simulate_numpy(t, input_signals)
    assert output_no_hpf is not None
    print(f"✓ Simulation without HPF completed successfully")


def test_multi_channel():
    """Test high-pass filter with multiple output channels"""
    print("\n=== Testing Multi-Channel Support ===")

    high_pass_config = {
        'enable': True,
        'cutoff_freq': 0.5,
    }
    circuit = DenseCircuitFactory.create(
        gains=[[1.0, -1.0, 0.5], [2.0, 0.0, -0.5]],  # 2 inputs, 3 outputs
        biases=[1.5, -1.5, 1.0],  # Non-zero biases for valid HPF
        use_relu=False,
        high_pass_config=high_pass_config
    )

    # Check that each channel has its own high-pass filter configuration
    assert len(circuit.channel_configs) == 3
    for i, config in enumerate(circuit.channel_configs):
        assert config['hp_capacitance'] is not None
        assert config['hp_resistance'] is not None
        assert config['hp_bias_source'] in ['vcc', 'vee']
        print(f"✓ Channel {i+1}: HPF components configured (C={config['hp_capacitance']:.1e}, R={config['hp_resistance']:.1e})")

    # Verify that HPF is enabled in the circuit
    assert circuit.high_pass_config['enable'] == True
    assert circuit.high_pass_config['cutoff_freq'] == 0.5
    print("✓ HPF configuration correct for all channels")


def test_factory_methods():
    """Test that all factory methods support high_pass_config"""
    print("\n=== Testing Factory Methods ===")

    high_pass_config = {
        'enable': True,
        'cutoff_freq': 1.0,
    }

    # Use non-zero biases for valid HPF calculation
    biases = [2.0]

    # Test create_ideal
    circuit = DenseCircuitFactory.create_ideal(
        gains=[[1.0]],
        biases=biases,
        use_relu=False,
        high_pass_config=high_pass_config
    )
    assert circuit.high_pass_config['enable'] == True
    print("✓ create_ideal supports high_pass_config")

    # Test create_with_relu
    circuit = DenseCircuitFactory.create_with_relu(
        gains=[[1.0]],
        biases=biases,
        high_pass_config=high_pass_config
    )
    assert circuit.high_pass_config['enable'] == True
    print("✓ create_with_relu supports high_pass_config")

    # Test create_ideal_with_relu
    circuit = DenseCircuitFactory.create_ideal_with_relu(
        gains=[[1.0]],
        biases=biases,
        high_pass_config=high_pass_config
    )
    assert circuit.high_pass_config['enable'] == True
    print("✓ create_ideal_with_relu supports high_pass_config")

    # Test create_with_tanh
    circuit = DenseCircuitFactory.create_with_tanh(
        gains=[[1.0]],
        biases=biases,
        high_pass_config=high_pass_config
    )
    assert circuit.high_pass_config['enable'] == True
    print("✓ create_with_tanh supports high_pass_config")

    # Test create_ideal_with_tanh
    circuit = DenseCircuitFactory.create_ideal_with_tanh(
        gains=[[1.0]],
        biases=biases,
        high_pass_config=high_pass_config
    )
    assert circuit.high_pass_config['enable'] == True
    print("✓ create_ideal_with_tanh supports high_pass_config")


def main():
    """Run all tests"""
    print("=" * 60)
    print("High-Pass Filter Functionality Tests")
    print("=" * 60)

    try:
        test_highpass_config_parsing()
        test_component_calculations()
        test_netlist_generation()
        test_numpy_simulation()
        test_multi_channel()
        test_factory_methods()

        print("\n" + "=" * 60)
        print("All tests passed successfully!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
