"""
Tests for batch and layered inference backends.

This module contains tests for BatchPredictBackend and LayerByLayerBackend classes.
"""
import pytest
import numpy as np
from unittest.mock import Mock, MagicMock, patch
from calibration_analyzer.wavedata import WaveData, WaveRecord
from calibration_analyzer.exam_class import TimeSeries


class TestBatchPredictBackend:
    """Tests for BatchPredictBackend class."""

    def test_initialization_with_model(self):
        """Test BatchPredictBackend initialization with valid model."""
        from inference.backends.batch_backend import BatchPredictBackend

        mock_model = Mock()
        mock_model.predict = Mock()

        backend = BatchPredictBackend(model=mock_model)
        assert backend.model is mock_model
        assert backend.batch_size == 32

    def test_initialization_with_custom_batch_size(self):
        """Test BatchPredictBackend with custom batch size."""
        from inference.backends.batch_backend import BatchPredictBackend

        mock_model = Mock()
        mock_model.predict = Mock()

        backend = BatchPredictBackend(model=mock_model, batch_size=64)
        assert backend.batch_size == 64

    def test_initialization_without_predict_method_raises(self):
        """Test initialization raises error for model without predict method."""
        from inference.backends.batch_backend import BatchPredictBackend

        mock_model = Mock(spec=[])  # No predict method

        with pytest.raises(ValueError, match="模型必须实现predict方法"):
            BatchPredictBackend(model=mock_model)

    def test_infer_creates_output_container(self):
        """Test infer creates proper output container."""
        from inference.backends.batch_backend import BatchPredictBackend

        mock_model = Mock()
        mock_model.predict = Mock(return_value=np.array([[1.0]] * 10))

        backend = BatchPredictBackend(model=mock_model)

        input_wave = WaveData(description="Input", author="Test")
        input_record = WaveRecord(
            data=np.array([[1.0]] * 10),
            sample_rate=1000,
            channel_names=["CH0"],
            record_id="input"
        )
        input_wave.add_record(input_record)

        result = backend.infer(input_wave, use_scaler=False)

        assert isinstance(result, WaveData)
        assert len(result.records) == 1

    def test_infer_with_empty_records(self):
        """Test infer with empty records returns empty output."""
        from inference.backends.batch_backend import BatchPredictBackend

        mock_model = Mock()
        mock_model.predict = Mock()

        backend = BatchPredictBackend(model=mock_model)

        input_wave = WaveData(description="Input", author="Test")
        # No records added

        result = backend.infer(input_wave, use_scaler=False)

        assert isinstance(result, WaveData)
        assert len(result.records) == 0

    def test_infer_calls_model_predict(self):
        """Test infer calls model.predict with correct arguments."""
        from inference.backends.batch_backend import BatchPredictBackend

        mock_model = Mock()
        mock_model.predict = Mock(return_value=np.array([[1.0]] * 10))

        backend = BatchPredictBackend(model=mock_model, batch_size=16)

        input_wave = WaveData(description="Input", author="Test")
        input_record = WaveRecord(
            data=np.array([[1.0, 2.0]] * 10),  # 2 channels
            sample_rate=1000,
            channel_names=["CH0", "CH1"],
            record_id="input"
        )
        input_wave.add_record(input_record)

        result = backend.infer(input_wave, use_scaler=True)

        mock_model.predict.assert_called_once()
        call_kwargs = mock_model.predict.call_args.kwargs
        assert call_kwargs.get('use_scaler') is True

    def test_infer_with_use_scaler_false(self):
        """Test infer with use_scaler=False."""
        from inference.backends.batch_backend import BatchPredictBackend

        mock_model = Mock()
        mock_model.predict = Mock(return_value=np.array([[1.0]] * 10))

        backend = BatchPredictBackend(model=mock_model)

        input_wave = WaveData(description="Input", author="Test")
        input_record = WaveRecord(
            data=np.array([[1.0]] * 10),
            sample_rate=1000,
            channel_names=["CH0"],
            record_id="input"
        )
        input_wave.add_record(input_record)

        result = backend.infer(input_wave, use_scaler=False)

        call_kwargs = mock_model.predict.call_args.kwargs
        assert call_kwargs.get('use_scaler') is False


class TestLayerByLayerBackend:
    """Tests for LayerByLayerBackend class.

    Note: Full testing of LayerByLayerBackend requires integration tests with
    actual LayeredModelSupport implementations. These tests verify the basic
    interface and behavior patterns.
    """

    def test_class_exists(self):
        """Test that LayerByLayerBackend class can be imported."""
        from inference.backends.layered_backend import LayerByLayerBackend
        assert LayerByLayerBackend is not None

    def test_has_infer_method(self):
        """Test that LayerByLayerBackend has infer method."""
        from inference.backends.layered_backend import LayerByLayerBackend
        assert hasattr(LayerByLayerBackend, 'infer')

    def test_has_get_layered_models_method(self):
        """Test that LayerByLayerBackend references get_layered_models."""
        # This test verifies the expected interface pattern
        from models.layer_support import LayeredModelSupport
        assert hasattr(LayeredModelSupport, 'get_layered_models')
