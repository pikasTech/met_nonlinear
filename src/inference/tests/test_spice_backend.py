"""
Tests for SPICE backend core classes.

This module contains tests for SPICEBackend, SPICESimulator, and PhaseCorrector classes.
"""
import pytest
import numpy as np
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from pathlib import Path
import tempfile
import os


class TestPhaseCorrector:
    """Tests for PhaseCorrector class."""

    def test_initialization(self):
        """Test PhaseCorrector initialization."""
        from inference.backends.spice.phase_correction import PhaseCorrector

        corrector = PhaseCorrector()
        assert corrector is not None

    def test_apply_immediate_phase_correction_non_wavenet(self):
        """Test phase correction returns original data for non-WaveNet models."""
        from inference.backends.spice.phase_correction import PhaseCorrector
        from calibration_analyzer.wavedata import WaveData, WaveRecord

        corrector = PhaseCorrector()

        # Create mock WaveData
        wave_data = WaveData(description="Test data", author="Test")
        record = WaveRecord(
            data=np.random.randn(100, 3),
            sample_rate=1000,
            channel_names=["HP0", "BP0", "LP0"],
            record_id="test_record"
        )
        wave_data.add_record(record)

        # Non-WaveNet model should return original data
        result = corrector.apply_immediate_phase_correction(wave_data, 1, model=None)
        assert result is wave_data

    def test_apply_immediate_phase_correction_wavenet5_svf_layer(self):
        """Test phase correction for WaveNet5 SVF layer (layer 1)."""
        from inference.backends.spice.phase_correction import PhaseCorrector
        from calibration_analyzer.wavedata import WaveData, WaveRecord

        corrector = PhaseCorrector()

        # Create WaveData with SVF output (3 channels per SVF)
        wave_data = WaveData(description="Test data", author="Test")
        original_data = np.array([[1.0, 2.0, 3.0]] * 10)  # 10 time steps, 3 channels
        record = WaveRecord(
            data=original_data.copy(),
            sample_rate=1000,
            channel_names=["HP0", "BP0", "LP0"],
            record_id="test_record"
        )
        wave_data.add_record(record)

        # Mock WaveNet5 model
        mock_model = Mock()
        mock_model.__class__.__name__ = 'WaveNet5'

        result = corrector.apply_immediate_phase_correction(wave_data, 1, model=mock_model)

        # HP and LP channels should be inverted
        assert result is not wave_data
        assert len(result.records) == 1
        np.testing.assert_array_almost_equal(
            result.records[0].data[:, 0],  # HP channel
            -original_data[:, 0]
        )
        np.testing.assert_array_almost_equal(
            result.records[0].data[:, 1],  # BP channel (unchanged)
            original_data[:, 1]
        )
        np.testing.assert_array_almost_equal(
            result.records[0].data[:, 2],  # LP channel
            -original_data[:, 2]
        )

    def test_apply_immediate_phase_correction_wavenet5_dense_layer(self):
        """Test phase correction for WaveNet5 Dense layer (layers 2-4)."""
        from inference.backends.spice.phase_correction import PhaseCorrector
        from calibration_analyzer.wavedata import WaveData, WaveRecord

        corrector = PhaseCorrector()

        # Create WaveData
        wave_data = WaveData(description="Test data", author="Test")
        original_data = np.array([[1.0, 2.0, 3.0, 4.0]] * 10)
        record = WaveRecord(
            data=original_data.copy(),
            sample_rate=1000,
            channel_names=["CH0", "CH1", "CH2", "CH3"],
            record_id="test_record"
        )
        wave_data.add_record(record)

        # Mock WaveNet5 model
        mock_model = Mock()
        mock_model.__class__.__name__ = 'WaveNet5'

        # Dense layers should invert all channels
        for layer_idx in [2, 3, 4]:
            result = corrector.apply_immediate_phase_correction(wave_data, layer_idx, model=mock_model)
            assert result is not wave_data
            np.testing.assert_array_almost_equal(
                result.records[0].data,
                -original_data
            )

    def test_apply_immediate_phase_correction_wavenet5_layer5(self):
        """Test layer 5 returns original data (no correction)."""
        from inference.backends.spice.phase_correction import PhaseCorrector
        from calibration_analyzer.wavedata import WaveData, WaveRecord

        corrector = PhaseCorrector()

        wave_data = WaveData(description="Test data", author="Test")
        original_data = np.array([[1.0, 2.0, 3.0]] * 10)
        record = WaveRecord(
            data=original_data.copy(),
            sample_rate=1000,
            channel_names=["HP0", "BP0", "LP0"],
            record_id="test_record"
        )
        wave_data.add_record(record)

        mock_model = Mock()
        mock_model.__class__.__name__ = 'WaveNet5'

        # Layer 5 should return original data
        result = corrector.apply_immediate_phase_correction(wave_data, 5, model=mock_model)
        assert result is wave_data

    def test_needs_phase_correction_wavenet5(self):
        """Test needs_phase_correction for WaveNet5 model."""
        from inference.backends.spice.phase_correction import PhaseCorrector

        corrector = PhaseCorrector()
        mock_model = Mock()
        mock_model.__class__.__name__ = 'WaveNet5'

        # Layers 1-4 need correction
        assert corrector.needs_phase_correction(mock_model, 1) is True
        assert corrector.needs_phase_correction(mock_model, 2) is True
        assert corrector.needs_phase_correction(mock_model, 3) is True
        assert corrector.needs_phase_correction(mock_model, 4) is True
        # Layer 5 doesn't need correction
        assert corrector.needs_phase_correction(mock_model, 5) is False
        # Non-WaveNet models don't need correction
        assert corrector.needs_phase_correction(None, 1) is False

    def test_is_wavenet5_model_detection(self):
        """Test _is_wavenet5_model detection logic."""
        from inference.backends.spice.phase_correction import PhaseCorrector

        corrector = PhaseCorrector()

        # Test with various model names
        mock_model = Mock()

        mock_model.__class__.__name__ = 'WaveNet5'
        assert corrector._is_wavenet5_model(mock_model) is True

        mock_model.__class__.__name__ = 'WaveNet5Layer1'
        assert corrector._is_wavenet5_model(mock_model) is True

        mock_model.__class__.__name__ = 'WaveNet'
        assert corrector._is_wavenet5_model(mock_model) is False

        mock_model.__class__.__name__ = 'LSTM'
        assert corrector._is_wavenet5_model(mock_model) is False

        assert corrector._is_wavenet5_model(None) is False

    def test_correct_svf_phase_metadata(self):
        """Test that SVF phase correction adds proper metadata."""
        from inference.backends.spice.phase_correction import PhaseCorrector
        from calibration_analyzer.wavedata import WaveData, WaveRecord

        corrector = PhaseCorrector()

        wave_data = WaveData(description="Test data", author="Test")
        original_data = np.array([[1.0, 2.0, 3.0, 4.0, 5.0, 6.0]] * 10)  # 2 SVFs
        record = WaveRecord(
            data=original_data.copy(),
            sample_rate=1000,
            channel_names=["HP0", "BP0", "LP0", "HP1", "BP1", "LP1"],
            record_id="test_record"
        )
        wave_data.add_record(record)

        result = corrector._correct_svf_phase(wave_data)

        # Check metadata
        assert 'svf_phase_corrected' in result.user_metadata
        assert result.user_metadata['svf_phase_corrected'] is True
        assert 'processed_by' in result.user_metadata
        assert result.user_metadata['processed_by'] == 'PhaseCorrector'


class TestSPICESimulator:
    """Tests for SPICESimulator class."""

    @patch('inference.backends.spice.simulation._check_spice_dependencies')
    def test_initialization(self, mock_check_deps):
        """Test SPICESimulator initialization."""
        from inference.backends.spice.simulation import SPICESimulator

        mock_check_deps.return_value = True

        with tempfile.TemporaryDirectory() as tmp_dir:
            simulator = SPICESimulator(tmp_dir, '/path/to/ngspice')
            assert simulator.output_folder == tmp_dir
            assert simulator.ngspice_path == '/path/to/ngspice'

    @patch('inference.backends.spice.simulation._check_spice_dependencies')
    def test_simulate_with_numpy_unsupported_circuit(self, mock_check_deps):
        """Test simulate_with_numpy raises error for unsupported circuit."""
        from inference.backends.spice.simulation import SPICESimulator

        mock_check_deps.return_value = True

        with tempfile.TemporaryDirectory() as tmp_dir:
            simulator = SPICESimulator(tmp_dir, '/path/to/ngspice')

            # Circuit without simulate_numpy method
            unsupported_circuit = Mock(spec=[])  # No methods

            from calibration_analyzer.wavedata import WaveData, WaveRecord

            wave_data = WaveData(description="Test", author="Test")
            record = WaveRecord(
                data=np.array([[1.0, 2.0]] * 10),
                sample_rate=1000,
                channel_names=["CH0", "CH1"],
                record_id="test"
            )
            wave_data.add_record(record)

            with pytest.raises(ValueError, match="不支持NumPy仿真"):
                simulator.simulate_with_numpy(unsupported_circuit, wave_data, 'test_output')

    @patch('inference.backends.spice.simulation._check_spice_dependencies')
    def test_simulate_with_numpy_success(self, mock_check_deps):
        """Test successful NumPy simulation."""
        from inference.backends.spice.simulation import SPICESimulator
        from calibration_analyzer.wavedata import WaveData, WaveRecord

        mock_check_deps.return_value = True

        # Create circuit with simulate_numpy method
        mock_circuit = Mock()
        mock_circuit.simulate_numpy = Mock(return_value=np.array([[0.5, 0.6]] * 10))
        # Use a lambda to avoid TypeError when post_process is None
        mock_circuit.post_process = lambda x, ctx=None: x

        with tempfile.TemporaryDirectory() as tmp_dir:
            simulator = SPICESimulator(tmp_dir, '/path/to/ngspice')

            wave_data = WaveData(description="Test", author="Test")
            record = WaveRecord(
                data=np.array([[1.0, 2.0]] * 10),
                sample_rate=1000,
                channel_names=["CH0", "CH1"],
                record_id="test"
            )
            wave_data.add_record(record)

            result = simulator.simulate_with_numpy(mock_circuit, wave_data, 'test_output')

            assert isinstance(result, WaveData)
            assert len(result.records) == 1
            assert '_numpy' in result.records[0].record_id
            # Check simulate_numpy was called
            mock_circuit.simulate_numpy.assert_called_once()


class TestSPICEBackend:
    """Tests for SPICEBackend class."""

    @patch('inference.backends.spice.backend.SPICESimulator')
    @patch('inference.backends.spice.backend.PhaseCorrector')
    @patch('inference.backends.spice.backend.DataRangeChecker')
    @patch('shutil.which')
    def test_initialization(self, mock_which, mock_drc, mock_pc, mock_simulator):
        """Test SPICEBackend initialization."""
        from inference.backends.spice.backend import SPICEBackend

        mock_which.return_value = None

        mock_model = Mock()
        mock_model.project_path = '/test/project'

        mock_backend = SPICEBackend(model=mock_model)

        assert mock_backend.model is mock_model
        assert mock_backend.output_folder.endswith('spice_netlists')
        assert mock_backend.temp_folder.endswith('temp')

    @patch('inference.backends.spice.backend.SPICESimulator')
    @patch('inference.backends.spice.backend.PhaseCorrector')
    @patch('inference.backends.spice.backend.DataRangeChecker')
    @patch('shutil.which')
    def test_initialization_with_ngspice_path(self, mock_which, mock_drc, mock_pc, mock_simulator):
        """Test SPICEBackend initialization with custom ngspice path."""
        from inference.backends.spice.backend import SPICEBackend

        mock_which.return_value = None

        mock_model = Mock()
        mock_model.project_path = '/test/project'

        custom_ngspice = '/custom/path/to/ngspice'
        mock_backend = SPICEBackend(model=mock_model, ngspice_path=custom_ngspice)

        assert mock_backend.ngspice_path == custom_ngspice

    @patch('inference.backends.spice.backend.SPICESimulator')
    @patch('inference.backends.spice.backend.PhaseCorrector')
    @patch('inference.backends.spice.backend.DataRangeChecker')
    @patch('shutil.which')
    def test_setup_ngspice_path_system(self, mock_which, mock_drc, mock_pc, mock_simulator):
        """Test _setup_ngspice_path when system ngspice exists."""
        from inference.backends.spice.backend import SPICEBackend

        mock_which.return_value = '/usr/bin/ngspice'

        mock_model = Mock()
        mock_model.project_path = '/test/project'

        mock_backend = SPICEBackend(model=mock_model)

        assert mock_backend.ngspice_path == '/usr/bin/ngspice'
        mock_which.assert_called_once_with('ngspice')

    @patch('inference.backends.spice.backend.SPICESimulator')
    @patch('inference.backends.spice.backend.PhaseCorrector')
    @patch('inference.backends.spice.backend.DataRangeChecker')
    @patch('shutil.which')
    def test_export_model_to_spice_no_to_spice_method(self, mock_which, mock_drc, mock_pc, mock_simulator):
        """Test export_model_to_spice raises error for model without to_spice."""
        from inference.backends.spice.backend import SPICEBackend

        mock_which.return_value = None

        mock_model = Mock(spec=[])  # No to_spice method
        mock_model.project_path = '/test/project'

        mock_backend = SPICEBackend(model=mock_model)

        with pytest.raises(ValueError, match="模型不支持导出到 SPICE 格式"):
            mock_backend.export_model_to_spice()

    @patch('inference.backends.spice.backend.SPICESimulator')
    @patch('inference.backends.spice.backend.PhaseCorrector')
    @patch('inference.backends.spice.backend.DataRangeChecker')
    @patch('shutil.which')
    def test_export_model_to_spice_success(self, mock_which, mock_drc, mock_pc, mock_simulator):
        """Test successful model export to SPICE."""
        from inference.backends.spice.backend import SPICEBackend

        mock_which.return_value = None

        mock_model = Mock()
        mock_model.project_path = '/test/project'
        mock_model.model_name = 'TestModel'
        mock_model.to_spice = Mock(return_value='/path/to/spice/output')

        mock_backend = SPICEBackend(model=mock_model)

        result = mock_backend.export_model_to_spice()

        assert result == '/path/to/spice/output'
        mock_model.to_spice.assert_called_once()

    @patch('inference.backends.spice.backend.SPICESimulator')
    @patch('inference.backends.spice.backend.PhaseCorrector')
    @patch('inference.backends.spice.backend.DataRangeChecker')
    @patch('shutil.which')
    def test_export_model_to_spice_with_config(self, mock_which, mock_drc, mock_pc, mock_simulator):
        """Test export_model_to_spice with inference_config."""
        from inference.backends.spice.backend import SPICEBackend

        mock_which.return_value = None

        mock_model = Mock()
        mock_model.project_path = '/test/project'
        mock_model.model_name = 'TestModel'
        mock_model.to_spice = Mock(return_value='/path/to/spice/output')

        inference_config = {
            'high_pass_config': {'cutoff_freq': 5.0},
            'opamp_config': {'model': 'OPA1611'}
        }

        mock_backend = SPICEBackend(model=mock_model, inference_config=inference_config)
        mock_backend.export_model_to_spice()

        # Verify to_spice was called with config parameters
        call_kwargs = mock_model.to_spice.call_args.kwargs
        assert 'high_pass_config' in call_kwargs
        assert 'opamp_config' in call_kwargs


class TestSPICEBackendInfer:
    """Tests for SPICEBackend.infer method."""

    @patch('inference.backends.spice.backend.SPICESimulator')
    @patch('inference.backends.spice.backend.PhaseCorrector')
    @patch('inference.backends.spice.backend.DataRangeChecker')
    @patch('shutil.which')
    def test_infer_with_non_layered_model(self, mock_which, mock_drc, mock_pc, mock_simulator):
        """Test infer with non-layered model returns single output."""
        from inference.backends.spice.backend import SPICEBackend
        from calibration_analyzer.wavedata import WaveData, WaveRecord

        mock_which.return_value = None

        mock_model = Mock()
        mock_model.project_path = '/test/project'
        mock_model.to_spice = Mock(return_value=Mock())  # Single circuit, not list

        mock_output_wave = WaveData(description="Output", author="Test")
        mock_simulator_instance = Mock()
        mock_simulator_instance.simulate_with_spice = Mock(return_value=mock_output_wave)
        mock_simulator.return_value = mock_simulator_instance

        mock_backend = SPICEBackend(model=mock_model)

        input_wave = WaveData(description="Input", author="Test")
        input_record = WaveRecord(
            data=np.array([[1.0]] * 10),
            sample_rate=1000,
            channel_names=["CH0"],
            record_id="input"
        )
        input_wave.add_record(input_record)

        result = mock_backend.infer(input_wave)

        assert isinstance(result, WaveData)
        mock_simulator_instance.simulate_with_spice.assert_called_once()

    @patch('inference.backends.spice.backend.SPICESimulator')
    @patch('inference.backends.spice.backend.PhaseCorrector')
    @patch('inference.backends.spice.backend.DataRangeChecker')
    @patch('shutil.which')
    def test_infer_with_layered_model(self, mock_which, mock_drc, mock_pc, mock_simulator):
        """Test infer with layered model returns list of outputs."""
        from inference.backends.spice.backend import SPICEBackend
        from calibration_analyzer.wavedata import WaveData, WaveRecord

        mock_which.return_value = None

        mock_model = Mock()
        mock_model.project_path = '/test/project'
        mock_model.to_spice = Mock(return_value=[Mock(), Mock()])  # Layered circuits
        mock_model.__class__.__name__ = 'WaveNet5'

        mock_simulator_instance = Mock()
        mock_output = WaveData(description="Output", author="Test")
        mock_simulator_instance.simulate_with_spice = Mock(return_value=mock_output)
        mock_simulator_instance.simulate_with_numpy = Mock(return_value=mock_output)
        mock_simulator.return_value = mock_simulator_instance

        mock_pc_instance = Mock()
        mock_pc_instance.needs_phase_correction = Mock(return_value=False)
        mock_pc.return_value = mock_pc_instance

        mock_drc_instance = Mock()
        mock_drc.return_value = mock_drc_instance

        mock_backend = SPICEBackend(model=mock_model)

        input_wave = WaveData(description="Input", author="Test")
        input_record = WaveRecord(
            data=np.array([[1.0]] * 10),
            sample_rate=1000,
            channel_names=["CH0"],
            record_id="input"
        )
        input_wave.add_record(input_record)

        result = mock_backend.infer(input_wave, return_layers=True)

        assert isinstance(result, list)
        assert len(result) == 2  # 2 layers
        mock_simulator_instance.simulate_with_spice.assert_called()


class TestSPICEBackendInferUnified:
    """Tests for SPICEBackend.infer_unified method."""

    @patch('inference.backends.spice.backend.SPICESimulator')
    @patch('inference.backends.spice.backend.PhaseCorrector')
    @patch('inference.backends.spice.backend.DataRangeChecker')
    @patch('shutil.which')
    def test_infer_unified_returns_inference_result(self, mock_which, mock_drc, mock_pc, mock_simulator):
        """Test infer_unified returns InferenceResult."""
        from inference.backends.spice.backend import SPICEBackend
        from inference.unified import InferenceResult
        from calibration_analyzer.wavedata import WaveData, WaveRecord

        mock_which.return_value = None

        mock_model = Mock()
        mock_model.project_path = '/test/project'
        mock_model.model_name = 'TestModel'
        mock_model.to_spice = Mock(return_value=Mock())

        mock_output_wave = WaveData(description="Output", author="Test")
        mock_simulator_instance = Mock()
        mock_simulator_instance.simulate_with_spice = Mock(return_value=mock_output_wave)
        mock_simulator.return_value = mock_simulator_instance

        mock_backend = SPICEBackend(model=mock_model)

        input_wave = WaveData(description="Input", author="Test")
        input_record = WaveRecord(
            data=np.array([[1.0]] * 10),
            sample_rate=1000,
            channel_names=["CH0"],
            record_id="input"
        )
        input_wave.add_record(input_record)

        result = mock_backend.infer_unified(input_wave)

        assert isinstance(result, InferenceResult)
