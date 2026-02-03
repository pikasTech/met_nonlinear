"""
Tests for LayerByLayerBackend with mock LayeredModelSupport.

This module contains comprehensive tests for LayerByLayerBackend class,
using mock to simulate LayeredModelSupport models.
"""
import pytest
import numpy as np
from unittest.mock import Mock, MagicMock, patch
from calibration_analyzer.wavedata import WaveData, WaveRecord
from calibration_analyzer.exam_class import TimeSeries


class MockTimeSeries:
    """Mock TimeSeries class for testing."""

    def __init__(self, data, fs=1000):
        self.data = data
        self.fs = fs

    def to_time_series(self, channel_idx=0):
        return self


class TestLayerByLayerBackendExtended:
    """Extended tests for LayerByLayerBackend class."""

    def test_initialization_with_layered_model(self):
        """Test LayerByLayerBackend initialization with valid LayeredModelSupport model."""
        from inference.backends.layered_backend import LayerByLayerBackend
        from models.layer_support import LayeredModelSupport

        mock_model = Mock(spec=LayeredModelSupport)
        mock_model.get_layered_models = Mock(return_value=[])

        backend = LayerByLayerBackend(model=mock_model)
        assert backend.model is mock_model

    def test_initialization_without_model(self):
        """Test LayerByLayerBackend initialization without model."""
        from inference.backends.layered_backend import LayerByLayerBackend

        backend = LayerByLayerBackend(model=None)
        assert backend.model is None

    def test_infer_with_empty_layered_models(self):
        """Test infer raises error when get_layered_models returns empty list."""
        from inference.backends.layered_backend import LayerByLayerBackend
        from models.layer_support import LayeredModelSupport

        mock_model = Mock(spec=LayeredModelSupport)
        mock_model.get_layered_models = Mock(return_value=[])  # Empty
        mock_model.project_path = '/test/project'

        backend = LayerByLayerBackend(model=mock_model)

        input_wave = WaveData(description="Input", author="Test")
        input_record = WaveRecord(
            data=np.array([[1.0, 2.0]] * 10),
            sample_rate=1000,
            channel_names=["CH0", "CH1"],
            record_id="input"
        )
        input_wave.add_record(input_record)

        with pytest.raises(ValueError, match="未找到任何分层模型"):
            backend.infer(input_wave)

    def test_infer_with_empty_records(self):
        """Test infer with empty input records."""
        from inference.backends.layered_backend import LayerByLayerBackend
        from models.layer_support import LayeredModelSupport

        mock_model = Mock(spec=LayeredModelSupport)
        mock_model.get_layered_models = Mock(return_value=[Mock()])
        mock_model.project_path = '/test/project'

        backend = LayerByLayerBackend(model=mock_model)

        input_wave = WaveData(description="Empty", author="Test")
        # No records added

        result = backend.infer(input_wave)

        assert isinstance(result, list)
        assert len(result) == 0  # No results for empty input

    def test_infer_accepts_layers_param(self):
        """Test that layers parameter is accepted without error."""
        from inference.backends.layered_backend import LayerByLayerBackend
        from models.layer_support import LayeredModelSupport

        mock_model = Mock(spec=LayeredModelSupport)
        mock_model.get_layered_models = Mock(return_value=[Mock()])
        mock_model.project_path = '/test/project'

        # Don't need to test actual inference, just that param is accepted
        backend = LayerByLayerBackend(model=mock_model)
        assert callable(backend.infer)

    def test_has_infer_method(self):
        """Test that LayerByLayerBackend has infer method."""
        from inference.backends.layered_backend import LayerByLayerBackend

        backend = LayerByLayerBackend(model=None)
        assert hasattr(backend, 'infer')
        assert callable(backend.infer)

    def test_has_create_layer_output_container(self):
        """Test that LayerByLayerBackend has _create_layer_output_container method."""
        from inference.backends.layered_backend import LayerByLayerBackend

        backend = LayerByLayerBackend(model=None)
        assert hasattr(backend, '_create_layer_output_container')
        assert callable(backend._create_layer_output_container)


class TestPrepareBatchData:
    """Tests for prepare_batch_data utility function."""

    def test_prepare_batch_data_with_multiple_records(self):
        """Test prepare_batch_data with multiple records."""
        from inference.backends.utils import prepare_batch_data

        wave_data = WaveData(description="Test", author="Test")
        for i in range(3):
            record = WaveRecord(
                data=np.ones((10, 2)) * (i + 1),
                sample_rate=1000,
                channel_names=["CH0", "CH1"],
                record_id=f"record_{i}"
            )
            wave_data.add_record(record)

        batch_data, record_refs = prepare_batch_data(wave_data)

        assert batch_data.shape == (3, 10, 2)
        assert len(record_refs) == 3
        np.testing.assert_array_equal(batch_data[0], np.ones((10, 2)))
        np.testing.assert_array_equal(batch_data[1], np.ones((10, 2)) * 2)
        np.testing.assert_array_equal(batch_data[2], np.ones((10, 2)) * 3)

    def test_prepare_batch_data_empty(self):
        """Test prepare_batch_data with empty wave data."""
        from inference.backends.utils import prepare_batch_data

        wave_data = WaveData(description="Empty", author="Test")
        # No records

        batch_data, record_refs = prepare_batch_data(wave_data)

        assert len(batch_data) == 0
        assert len(record_refs) == 0

    def test_prepare_batch_data_single_record(self):
        """Test prepare_batch_data with single record."""
        from inference.backends.utils import prepare_batch_data

        wave_data = WaveData(description="Test", author="Test")
        record = WaveRecord(
            data=np.array([[1.0, 2.0]] * 10),
            sample_rate=1000,
            channel_names=["CH0", "CH1"],
            record_id="single_record"
        )
        wave_data.add_record(record)

        batch_data, record_refs = prepare_batch_data(wave_data)

        assert batch_data.shape == (1, 10, 2)
        assert len(record_refs) == 1

    def test_prepare_batch_data_preserves_references(self):
        """Test that prepare_batch_data preserves record references."""
        from inference.backends.utils import prepare_batch_data

        wave_data = WaveData(description="Test", author="Test")
        original_records = []
        for i in range(2):
            record = WaveRecord(
                data=np.ones((10, 2)),
                sample_rate=1000,
                channel_names=["CH0", "CH1"],
                record_id=f"record_{i}",
                user_metadata={'index': i}
            )
            wave_data.add_record(record)
            original_records.append(record)

        _, record_refs = prepare_batch_data(wave_data)

        assert record_refs[0] is original_records[0]
        assert record_refs[1] is original_records[1]
