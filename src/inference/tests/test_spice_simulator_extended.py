"""
Tests for SPICESimulator with mock NGspice environment.

This module contains comprehensive tests for SPICESimulator class,
using mock to simulate NGspice behavior without requiring actual ngspice installation.
"""
import pytest
import numpy as np
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from pathlib import Path
import tempfile
import os


class TestSPICESimulatorExtended:
    """Extended tests for SPICESimulator class with mock NGspice."""

    @patch('inference.backends.spice.simulation._check_spice_dependencies')
    def test_initialization_with_dependencies_check(self, mock_check_deps):
        """Test SPICESimulator initialization with successful dependency check."""
        from inference.backends.spice.simulation import SPICESimulator

        mock_check_deps.return_value = True

        with tempfile.TemporaryDirectory() as tmp_dir:
            simulator = SPICESimulator(tmp_dir, '/path/to/ngspice')
            assert simulator.output_folder == tmp_dir
            assert simulator.ngspice_path == '/path/to/ngspice'
            assert hasattr(simulator, 'CircuitSimulation')
            assert hasattr(simulator, 'BaseCircuit')

    @patch('inference.backends.spice.simulation._check_spice_dependencies')
    def test_simulate_with_spice_circuit_with_to_spice(self, mock_check_deps):
        """Test simulate_with_spice with circuit that has to_spice method."""
        from inference.backends.spice.simulation import SPICESimulator
        from calibration_analyzer.wavedata import WaveData, WaveRecord

        mock_check_deps.return_value = True

        # Mock circuit with to_spice method but NO post_process method
        mock_circuit = Mock(spec=['to_spice'])
        mock_circuit.to_spice = Mock(return_value="mock_spice_circuit")

        # Mock simulate_circuit_with_sweep
        mock_output_wave = WaveData(description="Output", author="Test")
        mock_output_record = WaveRecord(
            data=np.array([[0.5, 0.6]] * 10),
            sample_rate=1000,
            channel_names=["CH0", "CH1"],
            record_id="test_output"
        )
        mock_output_wave.add_record(mock_output_record)

        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch('inference.backends.spice.simulation.simulate_circuit_with_sweep', return_value=mock_output_wave):
                simulator = SPICESimulator(tmp_dir, '/path/to/ngspice')

                input_wave = WaveData(description="Input", author="Test")
                input_record = WaveRecord(
                    data=np.array([[1.0, 2.0]] * 10),
                    sample_rate=1000,
                    channel_names=["CH0", "CH1"],
                    record_id="test_input"
                )
                input_wave.add_record(input_record)

                result = simulator.simulate_with_spice(mock_circuit, input_wave, 'test_output')

                # Verify to_spice was called
                mock_circuit.to_spice.assert_called_once()
                assert isinstance(result, WaveData)
                assert len(result.records) == 1

    @patch('inference.backends.spice.simulation._check_spice_dependencies')
    def test_simulate_with_spice_with_post_process_context(self, mock_check_deps):
        """Test simulate_with_spice with circuit that has post_process with context."""
        from inference.backends.spice.simulation import SPICESimulator
        from calibration_analyzer.wavedata import WaveData, WaveRecord

        mock_check_deps.return_value = True

        # Mock circuit with post_process that accepts context
        mock_circuit = Mock()
        mock_circuit.to_spice = Mock(return_value="mock_spice_circuit")

        def post_process_with_context(x, ctx=None):
            return x

        mock_circuit.post_process = Mock(side_effect=post_process_with_context)

        # Mock simulate_circuit_with_sweep
        mock_output_wave = WaveData(description="Output", author="Test")
        mock_output_record = WaveRecord(
            data=np.array([[0.5, 0.6]] * 10),
            sample_rate=1000,
            channel_names=["CH0", "CH1"],
            record_id="test_output"
        )
        mock_output_wave.add_record(mock_output_record)

        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch('inference.backends.spice.simulation.simulate_circuit_with_sweep', return_value=mock_output_wave):
                simulator = SPICESimulator(tmp_dir, '/path/to/ngspice')

                input_wave = WaveData(description="Input", author="Test")
                input_record = WaveRecord(
                    data=np.array([[1.0, 2.0]] * 10),
                    sample_rate=1000,
                    channel_names=["CH0", "CH1"],
                    record_id="test_input"
                )
                input_wave.add_record(input_record)

                result = simulator.simulate_with_spice(mock_circuit, input_wave, 'test_output')

                # Verify post_process was called with context
                mock_circuit.post_process.assert_called()
                assert isinstance(result, WaveData)

    @patch('inference.backends.spice.simulation._check_spice_dependencies')
    def test_simulate_with_numpy_empty_records(self, mock_check_deps):
        """Test simulate_with_numpy with empty input records."""
        from inference.backends.spice.simulation import SPICESimulator
        from calibration_analyzer.wavedata import WaveData, WaveRecord

        mock_check_deps.return_value = True

        # Mock circuit with simulate_numpy
        mock_circuit = Mock()
        mock_circuit.simulate_numpy = Mock(return_value=np.array([[0.5, 0.6]] * 10))
        mock_circuit.post_process = lambda x, ctx=None: x

        with tempfile.TemporaryDirectory() as tmp_dir:
            simulator = SPICESimulator(tmp_dir, '/path/to/ngspice')

            # Empty input wave
            input_wave = WaveData(description="Empty", author="Test")
            # No records added

            result = simulator.simulate_with_numpy(mock_circuit, input_wave, 'test_output')

            # Should return empty WaveData
            assert isinstance(result, WaveData)
            assert len(result.records) == 0
            # simulate_numpy should not be called
            mock_circuit.simulate_numpy.assert_not_called()

    @patch('inference.backends.spice.simulation._check_spice_dependencies')
    def test_simulate_with_numpy_multiple_outputs(self, mock_check_deps):
        """Test simulate_with_numpy with multiple output channels."""
        from inference.backends.spice.simulation import SPICESimulator
        from calibration_analyzer.wavedata import WaveData, WaveRecord

        mock_check_deps.return_value = True

        # Mock circuit with simulate_numpy returning 6 outputs (2 SVFs)
        mock_circuit = Mock()
        mock_circuit.simulate_numpy = Mock(return_value=np.array([[0.1, 0.2, 0.3, 0.4, 0.5, 0.6]] * 10))
        mock_circuit.post_process = lambda x, ctx=None: x

        with tempfile.TemporaryDirectory() as tmp_dir:
            simulator = SPICESimulator(tmp_dir, '/path/to/ngspice')

            input_wave = WaveData(description="Input", author="Test")
            input_record = WaveRecord(
                data=np.array([[1.0, 2.0]] * 10),
                sample_rate=1000,
                channel_names=["CH0", "CH1"],
                record_id="test_input"
            )
            input_wave.add_record(input_record)

            result = simulator.simulate_with_numpy(mock_circuit, input_wave, 'test_output')

            assert isinstance(result, WaveData)
            assert len(result.records) == 1
            # Check channel naming: HP0, BP0, LP0, HP1, BP1, LP1
            expected_channels = ['HP0', 'BP0', 'LP0', 'HP1', 'BP1', 'LP1']
            assert result.records[0].channel_names == expected_channels

    @patch('inference.backends.spice.simulation._check_spice_dependencies')
    def test_simulate_with_numpy_single_output(self, mock_check_deps):
        """Test simulate_with_numpy with single output channel."""
        from inference.backends.spice.simulation import SPICESimulator
        from calibration_analyzer.wavedata import WaveData, WaveRecord

        mock_check_deps.return_value = True

        # Mock circuit with simulate_numpy returning 1 output
        mock_circuit = Mock()
        mock_circuit.simulate_numpy = Mock(return_value=np.array([[0.5]] * 10))
        mock_circuit.post_process = lambda x, ctx=None: x

        with tempfile.TemporaryDirectory() as tmp_dir:
            simulator = SPICESimulator(tmp_dir, '/path/to/ngspice')

            input_wave = WaveData(description="Input", author="Test")
            input_record = WaveRecord(
                data=np.array([[1.0]] * 10),
                sample_rate=1000,
                channel_names=["CH0"],
                record_id="test_input"
            )
            input_wave.add_record(input_record)

            result = simulator.simulate_with_numpy(mock_circuit, input_wave, 'test_output')

            assert isinstance(result, WaveData)
            assert len(result.records) == 1
            # Check channel naming: HP0
            assert result.records[0].channel_names == ['HP0']

    @patch('inference.backends.spice.simulation._check_spice_dependencies')
    def test_simulate_with_numpy_preserves_user_metadata(self, mock_check_deps):
        """Test simulate_with_numpy preserves user metadata from input."""
        from inference.backends.spice.simulation import SPICESimulator
        from calibration_analyzer.wavedata import WaveData, WaveRecord

        mock_check_deps.return_value = True

        # Mock circuit with simulate_numpy
        mock_circuit = Mock()
        mock_circuit.simulate_numpy = Mock(return_value=np.array([[0.5, 0.6]] * 10))
        mock_circuit.post_process = lambda x, ctx=None: x

        with tempfile.TemporaryDirectory() as tmp_dir:
            simulator = SPICESimulator(tmp_dir, '/path/to/ngspice')

            input_wave = WaveData(description="Input", author="Test")
            input_record = WaveRecord(
                data=np.array([[1.0, 2.0]] * 10),
                sample_rate=1000,
                channel_names=["CH0", "CH1"],
                record_id="test_input",
                user_metadata={'test_key': 'test_value'}
            )
            input_wave.add_record(input_record)

            result = simulator.simulate_with_numpy(mock_circuit, input_wave, 'test_output')

            # Check that simulation_type is in user_metadata
            assert 'simulation_type' in result.records[0].user_metadata
            assert result.records[0].user_metadata['simulation_type'] == 'numpy'


class TestSPICESimulatorDependencyCheck:
    """Tests for SPICESimulator dependency checking."""

    @patch('inference.backends.spice.simulation._check_spice_dependencies')
    def test_dependency_check_success(self, mock_check_deps):
        """Test successful dependency check."""
        from inference.backends.spice.simulation import SPICESimulator

        mock_check_deps.return_value = True

        with tempfile.TemporaryDirectory() as tmp_dir:
            simulator = SPICESimulator(tmp_dir, '/path/to/ngspice')
            assert simulator is not None

    @patch('inference.backends.spice.simulation._check_spice_dependencies')
    def test_dependency_check_failure(self, mock_check_deps):
        """Test failed dependency check raises error."""
        from inference.backends.spice.simulation import SPICESimulator

        mock_check_deps.side_effect = ImportError("Mock dependency error")

        with tempfile.TemporaryDirectory() as tmp_dir:
            with pytest.raises(ImportError, match="Mock dependency error"):
                SPICESimulator(tmp_dir, '/path/to/ngspice')
