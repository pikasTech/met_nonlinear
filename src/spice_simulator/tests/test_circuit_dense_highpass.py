#!/usr/bin/env python3
"""
Test module for high-pass filter functionality in circuit_dense.py

Tests the high-pass filter implementation including:
- Configuration parsing and validation
- Component calculations using neural network bias weights
- SPICE netlist generation
- Verification that NumPy simulation does NOT include high-pass filter effects
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from circuit_dense import DenseCircuit, DenseCircuitFactory


class TestHighPassFilterConfig:
    """Test high-pass filter configuration handling"""
    
    def test_default_config_disabled(self):
        """Test that high-pass filter is disabled by default"""
        circuit = DenseCircuitFactory.create(
            gains=[[1.0, -1.0], [0.5, 2.0]],
            biases=[0.0, 0.0],
            use_relu=False
        )
        assert circuit.high_pass_config['enable'] == False
        
    def test_enabled_config_parsing(self):
        """Test parsing of enabled high-pass filter configuration"""
        high_pass_config = {
            'enable': True,
            'cutoff_freq': 0.5,
            'auto_bias': True,
        }
        circuit = DenseCircuitFactory.create(
            gains=[[1.0, -1.0], [0.5, 2.0]],
            biases=[2.5, -1.5],  # These bias weights will be used by high-pass filter
            use_relu=False,
            high_pass_config=high_pass_config
        )
        assert circuit.high_pass_config['enable'] == True
        assert circuit.high_pass_config['cutoff_freq'] == 0.5
        assert circuit.high_pass_config['auto_bias'] == True
        
    def test_partial_config_with_defaults(self):
        """Test partial configuration fills in defaults correctly"""
        high_pass_config = {
            'enable': True,
            'cutoff_freq': 1.0,
        }
        circuit = DenseCircuitFactory.create(
            gains=[[1.0, -1.0], [0.5, 2.0]],
            biases=[0.0, 0.0],
            use_relu=False,
            high_pass_config=high_pass_config
        )
        assert circuit.high_pass_config['enable'] == True
        assert circuit.high_pass_config['cutoff_freq'] == 1.0
        assert circuit.high_pass_config['auto_bias'] == True  # Default
        assert circuit.high_pass_config['bias_divider_high'] == 10e3  # Default
        assert circuit.high_pass_config['bias_divider_low'] == 10e3  # Default
        
    def test_reject_bias_voltage_parameter(self):
        """Test that configuration with bias_voltage is rejected"""
        high_pass_config = {
            'enable': True,
            'cutoff_freq': 1.0,
            'bias_voltage': 2.5,  # This should cause an error
        }
        
        with pytest.raises(ValueError) as excinfo:
            circuit = DenseCircuitFactory.create(
                gains=[[1.0]],
                biases=[0.0],
                use_relu=False,
                high_pass_config=high_pass_config
            )
        
        assert "不应包含'bias_voltage'参数" in str(excinfo.value)
        assert "神经网络bias权重" in str(excinfo.value)


class TestComponentCalculations:
    """Test high-pass filter component calculations"""
    
    def test_auto_calculated_components(self):
        """Test automatic calculation of capacitance and resistance"""
        high_pass_config = {
            'enable': True,
            'cutoff_freq': 0.5,  # 0.5 Hz
            'auto_bias': True,
        }
        circuit = DenseCircuitFactory.create(
            gains=[[1.0], [2.0]],  # 2 input, 1 output
            biases=[1.5],  # Neural network bias weight
            use_relu=False,
            high_pass_config=high_pass_config
        )
        
        channel_config = circuit.channel_configs[0]
        
        # Check default capacitance
        expected_C = 1e-6  # 1μF
        assert channel_config['hp_capacitance'] == expected_C
        
        # Check calculated resistance: R = 1 / (2π * f * C)
        expected_R = 1 / (2 * np.pi * 0.5 * expected_C)
        assert abs(channel_config['hp_resistance'] - expected_R) < 1
        
    def test_positive_bias_weight_divider(self):
        """Test bias voltage divider calculation for positive neural network bias"""
        high_pass_config = {
            'enable': True,
            'cutoff_freq': 1.0,
            'auto_bias': True,
        }
        circuit = DenseCircuitFactory.create(
            gains=[[1.0]],
            biases=[2.5],  # Positive neural network bias weight
            use_relu=False,
            high_pass_config=high_pass_config
        )
        
        channel_config = circuit.channel_configs[0]
        assert channel_config['hp_bias_source'] == 'vcc'
        
        # Check divider calculation
        vcc = 15.0
        bias_value = 2.5
        R_high = circuit.high_pass_config['bias_divider_high']
        expected_R_low = bias_value * R_high / (vcc - bias_value)
        assert abs(channel_config['hp_bias_r_low'] - expected_R_low) < 0.1
        
    def test_negative_bias_weight_divider(self):
        """Test bias voltage divider calculation for negative neural network bias"""
        high_pass_config = {
            'enable': True,
            'cutoff_freq': 1.0,
            'auto_bias': True,
        }
        circuit = DenseCircuitFactory.create(
            gains=[[1.0]],
            biases=[-3.0],  # Negative neural network bias weight
            use_relu=False,
            high_pass_config=high_pass_config
        )
        
        channel_config = circuit.channel_configs[0]
        assert channel_config['hp_bias_source'] == 'vee'
        
        # Check divider calculation
        vee = -15.0
        bias_value = -3.0
        R_high = circuit.high_pass_config['bias_divider_high']
        expected_R_low = bias_value * R_high / (vee - bias_value)
        assert abs(channel_config['hp_bias_r_low'] - expected_R_low) < 0.1
        
    def test_custom_component_values(self):
        """Test using custom capacitance and resistance values"""
        high_pass_config = {
            'enable': True,
            'cutoff_freq': 1.0,  # This should be ignored
            'capacitance': 10e-6,  # 10μF
            'resistance': 15.9e3,   # 15.9kΩ
        }
        circuit = DenseCircuitFactory.create(
            gains=[[1.0]],
            biases=[1.0],
            use_relu=False,
            high_pass_config=high_pass_config
        )
        
        channel_config = circuit.channel_configs[0]
        assert channel_config['hp_capacitance'] == 10e-6
        assert channel_config['hp_resistance'] == 15.9e3
        
    def test_per_channel_bias_weights(self):
        """Test that each channel uses its own neural network bias weight"""
        high_pass_config = {
            'enable': True,
            'cutoff_freq': 1.0,
            'auto_bias': True,
        }
        circuit = DenseCircuitFactory.create(
            gains=[[1.0, -1.0, 0.5]],  # 1 input, 3 outputs
            biases=[2.5, -1.5, 0.0],   # Different bias for each channel
            use_relu=False,
            high_pass_config=high_pass_config
        )
        
        # Channel 0: positive bias -> VCC
        assert circuit.channel_configs[0]['hp_bias_source'] == 'vcc'
        
        # Channel 1: negative bias -> VEE
        assert circuit.channel_configs[1]['hp_bias_source'] == 'vee'
        
        # Channel 2: zero bias -> VCC (default)
        assert circuit.channel_configs[2]['hp_bias_source'] == 'vcc'


class TestNetlistGeneration:
    """Test SPICE netlist generation with high-pass filter"""
    
    def test_highpass_components_in_netlist(self):
        """Test that high-pass filter components appear in netlist"""
        high_pass_config = {
            'enable': True,
            'cutoff_freq': 1.0,
            'auto_bias': True,
        }
        circuit = DenseCircuitFactory.create(
            gains=[[1.0, -1.0]],  # 1 input, 2 outputs
            biases=[2.5, -1.5],   # Different bias for each channel
            use_relu=True,
            high_pass_config=high_pass_config
        )
        
        netlist = circuit.get_circuit_netlist()
        
        # Check for high-pass filter components
        assert "高通滤波器 Bias 电压分压器" in netlist
        assert "一阶无源高通滤波器" in netlist
        
        # Check for specific components for both channels
        assert "C_hp1" in netlist
        assert "R_hp1" in netlist
        assert "R_hp_bias_high1" in netlist
        assert "R_hp_bias_low1" in netlist
        assert "C_hp2" in netlist
        assert "R_hp2" in netlist
        
    def test_highpass_signal_path(self):
        """Test that high-pass filter is correctly placed in signal path"""
        high_pass_config = {
            'enable': True,
            'cutoff_freq': 1.0,
        }
        circuit = DenseCircuitFactory.create(
            gains=[[1.0]],
            biases=[2.5],
            use_relu=True,
            high_pass_config=high_pass_config
        )
        
        netlist = circuit.get_circuit_netlist()
        
        # Check signal path: op-amp output -> capacitor -> high-pass output
        assert "out1_pre out1_hp" in netlist  # Capacitor connection
        assert "out1_hp hp_bias1" in netlist  # Resistor to bias
        
    def test_highpass_disabled_not_in_netlist(self):
        """Test that high-pass filter components don't appear when disabled"""
        circuit = DenseCircuitFactory.create(
            gains=[[1.0]],
            biases=[0.0],
            use_relu=True,
            high_pass_config={'enable': False}
        )
        
        netlist = circuit.get_circuit_netlist()
        assert "高通滤波器" not in netlist
        assert "C_hp" not in netlist
        assert "R_hp" not in netlist


class TestNumpySimulation:
    """Test NumPy simulation to ensure high-pass filter does NOT affect it"""
    
    def test_numpy_simulation_unchanged(self):
        """Test that NumPy simulation is not affected by high-pass filter configuration"""
        # Create two circuits: one with high-pass enabled, one without
        circuit_without_hp = DenseCircuitFactory.create(
            gains=[[2.0]],  # Simple gain of 2
            biases=[1.0],   # Add 1V bias
            use_relu=False,
            high_pass_config={'enable': False}
        )
        
        circuit_with_hp = DenseCircuitFactory.create(
            gains=[[2.0]],  # Same gain
            biases=[1.0],   # Same bias
            use_relu=False,
            high_pass_config={
                'enable': True,
                'cutoff_freq': 1.0,
            }
        )
        
        # Create test signal with DC offset
        t = np.linspace(0, 10, 1000)
        dc_offset = 3.0
        signal = dc_offset + 0.5 * np.sin(2 * np.pi * 0.1 * t)  # DC + 0.1Hz sine
        input_signals = signal.reshape(-1, 1)
        
        # Run simulations
        output_without_hp = circuit_without_hp.simulate_numpy(t, input_signals)
        output_with_hp = circuit_with_hp.simulate_numpy(t, input_signals)
        
        # Outputs should be identical - high-pass filter should NOT affect NumPy simulation
        np.testing.assert_allclose(output_without_hp, output_with_hp, rtol=1e-10)
        
        # Both should have the expected DC component: DC * gain + bias
        expected_dc = dc_offset * 2.0 + 1.0
        assert abs(np.mean(output_without_hp) - expected_dc) < 0.01
        assert abs(np.mean(output_with_hp) - expected_dc) < 0.01
        
    def test_numpy_preserves_dc_always(self):
        """Test that DC component is always preserved in NumPy simulation"""
        circuit = DenseCircuitFactory.create(
            gains=[[2.0]],
            biases=[1.0],
            use_relu=False,
            high_pass_config={
                'enable': True,  # High-pass enabled but should not affect NumPy
                'cutoff_freq': 0.1,
            }
        )
        
        # Create pure DC signal
        t = np.linspace(0, 10, 1000)
        dc_offset = 3.0
        signal = dc_offset * np.ones_like(t)  # Pure DC
        input_signals = signal.reshape(-1, 1)
        
        # Run simulation
        output = circuit.simulate_numpy(t, input_signals)
        
        # Output should preserve DC: output = input * gain + bias
        expected_output = dc_offset * 2.0 + 1.0
        assert abs(np.mean(output) - expected_output) < 0.01


class TestMultiChannel:
    """Test high-pass filter with multiple output channels"""
    
    def test_multi_channel_configuration(self):
        """Test that each channel gets its own high-pass filter configuration"""
        high_pass_config = {
            'enable': True,
            'cutoff_freq': 0.5,
        }
        circuit = DenseCircuitFactory.create(
            gains=[[1.0, -1.0, 0.5], [2.0, 0.0, -0.5]],  # 2 inputs, 3 outputs
            biases=[0.5, -0.5, 0.0],  # Different bias for each channel
            use_relu=False,
            high_pass_config=high_pass_config
        )
        
        # Check that each channel has its own configuration
        assert len(circuit.channel_configs) == 3
        for i, config in enumerate(circuit.channel_configs):
            assert config['hp_capacitance'] is not None
            assert config['hp_resistance'] is not None
            assert config['hp_bias_source'] in ['vcc', 'vee']
            
    def test_multi_channel_netlist(self):
        """Test netlist generation for multiple channels"""
        high_pass_config = {
            'enable': True,
            'cutoff_freq': 1.0,
        }
        circuit = DenseCircuitFactory.create(
            gains=[[1.0, -1.0], [0.5, 2.0]],  # 2 inputs, 2 outputs
            biases=[1.5, -2.0],  # Different bias for each channel
            use_relu=True,
            high_pass_config=high_pass_config
        )
        
        netlist = circuit.get_circuit_netlist()
        
        # Check that both channels have high-pass filters
        for ch in range(2):
            assert f"C_hp{ch+1}" in netlist
            assert f"R_hp{ch+1}" in netlist
            assert f"hp_bias{ch+1}" in netlist
            
        # Check that channel 1 uses VCC (positive bias) and channel 2 uses VEE (negative bias)
        assert "vcc hp_bias1" in netlist
        assert "vee hp_bias2" in netlist


class TestFactoryMethods:
    """Test that all factory methods support high_pass_config"""
    
    @pytest.mark.parametrize("factory_method,kwargs", [
        (DenseCircuitFactory.create_ideal, {}),
        (DenseCircuitFactory.create_with_relu, {'relu_type': 'op_amp'}),
        (DenseCircuitFactory.create_ideal_with_relu, {}),
        (DenseCircuitFactory.create_with_tanh, {}),
        (DenseCircuitFactory.create_ideal_with_tanh, {}),
    ])
    def test_factory_method_supports_highpass(self, factory_method, kwargs):
        """Test that factory method supports high_pass_config parameter"""
        high_pass_config = {
            'enable': True,
            'cutoff_freq': 1.0,
        }
        
        circuit = factory_method(
            gains=[[1.0]],
            biases=[2.0],  # Neural network bias weight
            high_pass_config=high_pass_config,
            **kwargs
        )
        
        assert circuit.high_pass_config['enable'] == True
        assert circuit.high_pass_config['cutoff_freq'] == 1.0


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_zero_bias_weight(self):
        """Test high-pass filter with zero neural network bias weight"""
        high_pass_config = {
            'enable': True,
            'cutoff_freq': 1.0,
        }
        circuit = DenseCircuitFactory.create(
            gains=[[1.0]],
            biases=[0.0],  # Zero bias weight
            use_relu=False,
            high_pass_config=high_pass_config
        )
        
        channel_config = circuit.channel_configs[0]
        # With zero bias, should still use vcc as source
        assert channel_config['hp_bias_source'] == 'vcc'
        
    def test_no_bias_weights(self):
        """Test high-pass filter when circuit has no bias weights"""
        high_pass_config = {
            'enable': True,
            'cutoff_freq': 1.0,
        }
        circuit = DenseCircuitFactory.create(
            gains=[[1.0]],
            biases=None,  # No bias weights
            use_relu=False,
            high_pass_config=high_pass_config
        )
        
        # Should handle gracefully - using 0.0 as bias
        channel_config = circuit.channel_configs[0]
        assert channel_config['hp_bias_source'] == 'vcc'
        
    def test_very_low_cutoff_frequency(self):
        """Test with very low cutoff frequency"""
        high_pass_config = {
            'enable': True,
            'cutoff_freq': 0.01,  # 0.01 Hz - very low
        }
        circuit = DenseCircuitFactory.create(
            gains=[[1.0]],
            biases=[1.0],
            use_relu=False,
            high_pass_config=high_pass_config
        )
        
        channel_config = circuit.channel_configs[0]
        # Should result in very large resistance
        expected_R = 1 / (2 * np.pi * 0.01 * 1e-6)
        assert abs(channel_config['hp_resistance'] - expected_R) < 100
        assert channel_config['hp_resistance'] > 1e6  # Should be > 1MΩ


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])