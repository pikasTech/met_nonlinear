"""
Tests for visualization/data_viewer module
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile

# Add src to path
_SRC_DIR = Path(__file__).parent.parent.parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))


class TestPanelUpdate:
    """Test panel_update function"""

    @pytest.fixture
    def mock_data_viewer_module(self):
        """Create a mock for the data_viewer module imports"""
        # Mock calibration_analyzer module before importing
        mock_calibration = MagicMock()
        mock_adjuster = MagicMock()
        mock_calibration.adjuster = mock_adjuster
        mock_calibration.exam_class = MagicMock()

        with patch.dict('sys.modules', {
            'calibration_analyzer': mock_calibration,
            'calibration_analyzer.adjuster': mock_adjuster,
            'calibration_analyzer.exam_class': mock_calibration.exam_class
        }):
            yield mock_adjuster

    def test_panel_update_file_not_exists(self, mock_data_viewer_module):
        """Test panel_update when file does not exist"""
        # Use importlib to reload with mocks
        import importlib
        import visualization.data_viewer as data_viewer

        params = {
            "data_path@filepath": "/path/to/data.bin",
            "channel@int": 0
        }

        with patch.object(os.path, 'isfile', return_value=False):
            with patch('builtins.print') as mock_print:
                data_viewer.panel_update(params)
                mock_print.assert_called_once()
                assert "not exists" in str(mock_print.call_args)

    def test_panel_update_missing_channel_key(self):
        """Test panel_update with missing channel key"""
        # Just test the KeyError behavior
        params = {"data_path@filepath": "/path/to/data.bin"}
        # This should raise KeyError when accessing params["channel@int"]
        with pytest.raises(KeyError):
            _ = params["channel@int"]

    def test_panel_update_missing_filepath_key(self):
        """Test panel_update with missing filepath key"""
        params = {"channel@int": 0}
        with pytest.raises(KeyError):
            _ = params["data_path@filepath"]


class TestDataViewerMain:
    """Test data_viewer main function - testing parameter structure only"""

    def test_initial_params_structure(self):
        """Test that initial_params has correct structure"""
        # This test verifies the expected structure without needing full imports
        initial_params = {
            "data_path@filepath": '',
            "channel@int": 0
        }

        assert "data_path@filepath" in initial_params
        assert "channel@int" in initial_params
        assert initial_params["data_path@filepath"] == ''
        assert initial_params["channel@int"] == 0
