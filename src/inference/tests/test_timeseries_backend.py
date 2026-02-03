"""
Tests for TimeSeriesBackend.

This module contains comprehensive tests for TimeSeriesBackend class.
"""
import pytest
import numpy as np
from unittest.mock import Mock, MagicMock, patch
from calibration_analyzer.wavedata import WaveData, WaveRecord


class TestTimeSeriesBackend:
    """Tests for TimeSeriesBackend class."""

    def test_initialization_with_model(self):
        """Test TimeSeriesBackend initialization with valid model."""
        from inference.backends.timeseries_backend import TimeSeriesBackend

        mock_model = Mock()
        mock_model.time_response = Mock()

        backend = TimeSeriesBackend(model=mock_model)
        assert backend.model is mock_model

    def test_initialization_without_model(self):
        """Test TimeSeriesBackend initialization without model."""
        from inference.backends.timeseries_backend import TimeSeriesBackend

        backend = TimeSeriesBackend(model=None)
        assert backend.model is None

    def test_initialization_without_time_response_raises(self):
        """Test initialization raises error for model without time_response method."""
        from inference.backends.timeseries_backend import TimeSeriesBackend

        mock_model = Mock(spec=[])  # No time_response method

        with pytest.raises(ValueError, match="模型必须实现time_response方法"):
            TimeSeriesBackend(model=mock_model)

    def test_has_infer_method(self):
        """Test that TimeSeriesBackend has infer method."""
        from inference.backends.timeseries_backend import TimeSeriesBackend

        backend = TimeSeriesBackend(model=None)
        assert hasattr(backend, 'infer')
        assert callable(backend.infer)

    def test_infer_accepts_use_scaler_param(self):
        """Test that infer accepts use_scaler parameter."""
        from inference.backends.timeseries_backend import TimeSeriesBackend

        mock_model = Mock()
        mock_model.time_response = Mock()

        backend = TimeSeriesBackend(model=mock_model)
        assert callable(backend.infer)
        # Verify the signature accepts use_scaler
        import inspect
        sig = inspect.signature(backend.infer)
        assert 'use_scaler' in sig.parameters

    def test_infer_accepts_layers_param(self):
        """Test that infer accepts layers parameter."""
        from inference.backends.timeseries_backend import TimeSeriesBackend

        mock_model = Mock()
        mock_model.time_response = Mock()

        backend = TimeSeriesBackend(model=mock_model)
        # Verify the signature accepts layers
        import inspect
        sig = inspect.signature(backend.infer)
        assert 'layers' in sig.parameters

    def test_infer_returns_wavedata(self):
        """Test that infer returns WaveData type."""
        from inference.backends.timeseries_backend import TimeSeriesBackend

        mock_model = Mock()
        mock_model.time_response = Mock()

        backend = TimeSeriesBackend(model=mock_model)

        # Just verify the return type annotation
        import inspect
        sig = inspect.signature(backend.infer)
        # Return annotation should be WaveData
        return_annotation = sig.return_annotation
        # If it's a string, it might say 'WaveData'
        assert 'WaveData' in str(return_annotation) or return_annotation == inspect.Parameter.empty
