"""
Tests for inference backend base classes.

This module contains tests for InferenceBackend abstract base class.
"""
import pytest
import numpy as np
from unittest.mock import Mock, MagicMock, patch
from calibration_analyzer.wavedata import WaveData, WaveRecord


class TestInferenceBackend:
    """Tests for InferenceBackend base class."""

    @pytest.fixture
    def mock_concrete_backend(self):
        """Create a concrete backend for testing base class methods."""
        from inference.backends.base import InferenceBackend
        from inference.backends.batch_backend import BatchPredictBackend

        mock_model = Mock()
        mock_model.predict = Mock(return_value=np.array([[1.0]] * 10))
        return BatchPredictBackend(model=mock_model)

    def test_initialization_with_model(self, mock_concrete_backend):
        """Test InferenceBackend initialization with model."""
        assert mock_concrete_backend.model is not None

    def test_initialization_without_model(self):
        """Test InferenceBackend initialization without model."""
        from inference.backends.base import InferenceBackend
        from inference.backends.batch_backend import BatchPredictBackend

        backend = BatchPredictBackend(model=None)
        assert backend.model is None

    def test_set_model(self, mock_concrete_backend):
        """Test set_model method."""
        mock_model = Mock()
        mock_concrete_backend.set_model(mock_model)
        assert mock_concrete_backend.model is mock_model

    def test_prepare_input_data_with_string_path(self, mock_concrete_backend):
        """Test _prepare_input_data with file path string."""
        mock_model = Mock()
        mock_concrete_backend.set_model(mock_model)

        mock_wave_data = WaveData(description="Loaded", author="Test")
        mock_concrete_backend.wave_processor.load_waveform = Mock(return_value=mock_wave_data)

        result = mock_concrete_backend._prepare_input_data('/path/to/waveform.wav')

        assert result is mock_wave_data
        mock_concrete_backend.wave_processor.load_waveform.assert_called_once_with('/path/to/waveform.wav')

    def test_prepare_input_data_with_wavedata(self, mock_concrete_backend):
        """Test _prepare_input_data with WaveData object."""
        mock_model = Mock()
        mock_concrete_backend.set_model(mock_model)

        input_wave = WaveData(description="Input", author="Test")
        result = mock_concrete_backend._prepare_input_data(input_wave)

        assert result is input_wave

    def test_prepare_input_data_without_model_raises_error(self):
        """Test _prepare_input_data raises error when model is None."""
        from inference.backends.base import InferenceBackend
        from inference.backends.batch_backend import BatchPredictBackend

        backend = BatchPredictBackend(model=None)

        input_wave = WaveData(description="Input", author="Test")

        with pytest.raises(ValueError, match="推理前必须先设置模型"):
            backend._prepare_input_data(input_wave)

    def test_create_output_container(self, mock_concrete_backend):
        """Test _create_output_container creates proper WaveData."""
        mock_model = Mock()
        mock_model.model_name = 'TestModel'
        mock_concrete_backend.set_model(mock_model)

        input_wave = WaveData(description="Input Wave", author="TestAuthor")

        result = mock_concrete_backend._create_output_container(input_wave)

        assert isinstance(result, WaveData)
        assert 'TestModel' in result.description

    def test_create_output_container_with_anonymous_model(self, mock_concrete_backend):
        """Test _create_output_container with model without model_name."""
        mock_model = Mock(spec=[])  # No model_name attribute
        mock_model.__class__.__name__ = 'MockModel'
        mock_concrete_backend.set_model(mock_model)

        input_wave = WaveData(description="Input Wave", author="TestAuthor")

        result = mock_concrete_backend._create_output_container(input_wave)

        assert isinstance(result, WaveData)
        assert 'MockModel' in result.description

    def test_add_metadata(self, mock_concrete_backend):
        """Test _add_metadata adds proper metadata."""
        mock_model = Mock()
        mock_model.model_name = 'TestModel'
        mock_model.__class__.__name__ = 'TestModelClass'
        mock_concrete_backend.set_model(mock_model)

        input_wave = WaveData(description="Input Wave", author="TestAuthor")
        input_wave.add_record(WaveRecord(
            data=np.array([[1.0]] * 10),
            sample_rate=1000,
            channel_names=["CH0"],
            record_id="input"
        ))

        output_wave = WaveData(description="Output Wave", author="Test")

        mock_concrete_backend._add_metadata(output_wave, input_wave, 'TestBackend')

        # Check metadata was added
        assert 'process_history' in output_wave.user_metadata
        assert 'model_info' in output_wave.user_metadata
        assert 'input_info' in output_wave.user_metadata
        assert 'backend_info' in output_wave.user_metadata
        assert output_wave.user_metadata['type'] == 'inference_result'

    def test_create_unified_result_single_wavedata(self, mock_concrete_backend):
        """Test _create_unified_result with single WaveData."""
        mock_model = Mock()
        mock_model.model_name = 'TestModel'
        mock_concrete_backend.set_model(mock_model)

        input_wave = WaveData(description="Input", author="Test")
        input_wave.add_record(WaveRecord(
            data=np.array([[1.0]] * 10),
            sample_rate=1000,
            channel_names=["CH0"],
            record_id="input"
        ))

        single_wave = WaveData(description="Output", author="Test")
        single_wave.add_record(WaveRecord(
            data=np.array([[2.0]] * 10),
            sample_rate=1000,
            channel_names=["CH0"],
            record_id="output"
        ))

        result = mock_concrete_backend._create_unified_result(
            backend_type='spice',
            layers_data=single_wave,
            input_path='/path/to/input.wav'
        )

        assert result.backend_type == 'spice'
        assert result.model_name == 'TestModel'
        assert result.input_path == '/path/to/input.wav'
        assert len(result.layers) == 1

    def test_create_unified_result_list_wavedata(self, mock_concrete_backend):
        """Test _create_unified_result with list of WaveData."""
        mock_model = Mock()
        mock_model.model_name = 'TestModel'
        mock_concrete_backend.set_model(mock_model)

        wave1 = WaveData(description="Layer 1", author="Test")
        wave1.add_record(WaveRecord(
            data=np.array([[1.0]] * 10),
            sample_rate=1000,
            channel_names=["CH0"],
            record_id="layer1"
        ))

        wave2 = WaveData(description="Layer 2", author="Test")
        wave2.add_record(WaveRecord(
            data=np.array([[2.0]] * 10),
            sample_rate=1000,
            channel_names=["CH0"],
            record_id="layer2"
        ))

        result = mock_concrete_backend._create_unified_result(
            backend_type='spice',
            layers_data=[wave1, wave2]
        )

        assert len(result.layers) == 2
        assert result.layers[0].layer_name == 'Layer_1'
        assert result.layers[1].layer_name == 'Layer_2'

    def test_create_unified_result_with_numpy_layers(self, mock_concrete_backend):
        """Test _create_unified_result with NumPy layers."""
        mock_model = Mock()
        mock_model.model_name = 'TestModel'
        mock_concrete_backend.set_model(mock_model)

        wave1 = WaveData(description="SPICE Layer 1", author="Test")
        wave1.add_record(WaveRecord(
            data=np.array([[1.0]] * 10),
            sample_rate=1000,
            channel_names=["CH0"],
            record_id="spice1"
        ))

        numpy_wave = WaveData(description="NumPy Layer 1", author="Test")
        numpy_wave.add_record(WaveRecord(
            data=np.array([[1.5]] * 10),
            sample_rate=1000,
            channel_names=["CH0"],
            record_id="numpy1"
        ))

        result = mock_concrete_backend._create_unified_result(
            backend_type='spice',
            layers_data=wave1,
            numpy_layers=[numpy_wave]
        )

        assert result.backend_type == 'spice'
        assert result.numpy_layers is not None
        assert len(result.numpy_layers) == 1
        assert result.numpy_layers[0].layer_name == 'NumPy_Layer_1'

    def test_infer_abstract_method_raises(self):
        """Test infer raises NotImplementedError for base class."""
        from inference.backends.base import InferenceBackend

        # Test that abstract class cannot be instantiated directly
        with pytest.raises(TypeError, match="abstract class"):
            InferenceBackend(model=None)
