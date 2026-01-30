"""
Tests for visualization/frequency_response_json_comparator module
"""

import pytest
import sys
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import numpy as np

# Add src to path
_SRC_DIR = Path(__file__).parent.parent.parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from visualization.frequency_response_json_comparator import (
    DataState,
    LayoutMode,
    DataSourceSpec,
    LinearResponseDataLoader,
    FrequencyResponseComparator,
    quick_compare
)


class TestDataState:
    """Test DataState enum"""

    def test_data_state_values(self):
        """Test DataState has correct values"""
        assert DataState.ORIGIN.value == "origin"
        assert DataState.COMPENSATION.value == "compensation"

    def test_data_state_count(self):
        """Test DataState has two states"""
        assert len(DataState) == 2


class TestLayoutMode:
    """Test LayoutMode enum"""

    def test_layout_mode_values(self):
        """Test LayoutMode has correct values"""
        assert LayoutMode.OVERLAY.value == "overlay"
        assert LayoutMode.SIDE_BY_SIDE.value == "side_by_side"

    def test_layout_mode_count(self):
        """Test LayoutMode has two modes"""
        assert len(LayoutMode) == 2


class TestDataSourceSpec:
    """Test DataSourceSpec dataclass"""

    def test_default_state(self):
        """Test default state is ORIGIN"""
        spec = DataSourceSpec("test_project")
        assert spec.state == DataState.ORIGIN

    def test_parse_without_at(self):
        """Test parsing source string without @"""
        spec = DataSourceSpec.parse("test_project")
        assert spec.project_name == "test_project"
        assert spec.state == DataState.ORIGIN

    def test_parse_with_origin(self):
        """Test parsing source string with @origin"""
        spec = DataSourceSpec.parse("test_project@origin")
        assert spec.project_name == "test_project"
        assert spec.state == DataState.ORIGIN

    def test_parse_with_compensation(self):
        """Test parsing source string with @compensation"""
        spec = DataSourceSpec.parse("test_project@compensation")
        assert spec.project_name == "test_project"
        assert spec.state == DataState.COMPENSATION

    def test_str_representation(self):
        """Test string representation of DataSourceSpec"""
        spec = DataSourceSpec("test_project", DataState.ORIGIN)
        assert str(spec) == "test_project@origin"

        spec2 = DataSourceSpec("test_project2", DataState.COMPENSATION)
        assert str(spec2) == "test_project2@compensation"


class TestLinearResponseDataLoader:
    """Test LinearResponseDataLoader class"""

    def test_init(self):
        """Test LinearResponseDataLoader initialization"""
        loader = LinearResponseDataLoader("/projects")
        assert loader.projects_root == "/projects"
        assert loader._cache == {}

    def test_init_default_root(self):
        """Test LinearResponseDataLoader with default root"""
        loader = LinearResponseDataLoader()
        assert loader.projects_root == "projects"

    def test_load_project_data_file_not_found(self):
        """Test loading non-existent project data"""
        loader = LinearResponseDataLoader("/nonexistent")
        with pytest.raises(FileNotFoundError):
            loader.load_project_data("nonexistent_project")

    def test_load_project_data_missing_fields(self):
        """Test loading data with missing required fields"""
        temp_dir = tempfile.mkdtemp()
        json_path = os.path.join(temp_dir, "test_project", "data", "linear_response.json")
        os.makedirs(os.path.dirname(json_path), exist_ok=True)

        # Create file with missing fields
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({"only_field": "value"}, f)

        loader = LinearResponseDataLoader(temp_dir)

        with pytest.raises(ValueError) as exc_info:
            loader.load_project_data("test_project")

        assert "Missing required fields" in str(exc_info.value)

        import shutil
        shutil.rmtree(temp_dir)

    def test_load_project_data_success(self):
        """Test successfully loading project data"""
        temp_dir = tempfile.mkdtemp()
        test_data = {
            "gains_origin": [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]],
            "gains_comped": [[1.1, 2.1, 3.1], [4.1, 5.1, 6.1]],
            "magnitudes": [0.5, 1.0],
            "frequencies": [10.0, 50.0, 100.0]
        }

        json_path = os.path.join(temp_dir, "test_project", "data", "linear_response.json")
        os.makedirs(os.path.dirname(json_path), exist_ok=True)

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)

        loader = LinearResponseDataLoader(temp_dir)
        data = loader.load_project_data("test_project")

        assert data["gains_origin"] == test_data["gains_origin"]
        assert data["gains_comped"] == test_data["gains_comped"]
        assert data["magnitudes"] == test_data["magnitudes"]
        assert data["frequencies"] == test_data["frequencies"]

        import shutil
        shutil.rmtree(temp_dir)

    def test_cache_functionality(self):
        """Test that caching works correctly"""
        temp_dir = tempfile.mkdtemp()
        test_data = {
            "gains_origin": [[1.0, 2.0, 3.0]],
            "gains_comped": [[1.1, 2.1, 3.1]],
            "magnitudes": [0.5],
            "frequencies": [10.0, 50.0, 100.0]
        }

        json_path = os.path.join(temp_dir, "test_project", "data", "linear_response.json")
        os.makedirs(os.path.dirname(json_path), exist_ok=True)

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)

        loader = LinearResponseDataLoader(temp_dir)

        # First load
        data1 = loader.load_project_data("test_project")

        # Second load should use cache
        data2 = loader.load_project_data("test_project")

        # Should be the same object (cached)
        assert data1 is data2

        import shutil
        shutil.rmtree(temp_dir)

    def test_extract_data_source_origin(self):
        """Test extracting data source with ORIGIN state"""
        temp_dir = tempfile.mkdtemp()
        test_data = {
            "gains_origin": [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]],
            "gains_comped": [[1.1, 2.1, 3.1], [4.1, 5.1, 6.1]],
            "magnitudes": [0.5, 1.0],
            "frequencies": [10.0, 50.0, 100.0]
        }

        json_path = os.path.join(temp_dir, "test_project", "data", "linear_response.json")
        os.makedirs(os.path.dirname(json_path), exist_ok=True)

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)

        loader = LinearResponseDataLoader(temp_dir)
        spec = DataSourceSpec("test_project", DataState.ORIGIN)
        source_data = loader.extract_data_source(spec)

        assert source_data["gains"] == test_data["gains_origin"]
        assert source_data["project_name"] == "test_project"
        assert source_data["state"] == "origin"

        import shutil
        shutil.rmtree(temp_dir)

    def test_extract_data_source_compensation(self):
        """Test extracting data source with COMPENSATION state"""
        temp_dir = tempfile.mkdtemp()
        test_data = {
            "gains_origin": [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]],
            "gains_comped": [[1.1, 2.1, 3.1], [4.1, 5.1, 6.1]],
            "magnitudes": [0.5, 1.0],
            "frequencies": [10.0, 50.0, 100.0]
        }

        json_path = os.path.join(temp_dir, "test_project", "data", "linear_response.json")
        os.makedirs(os.path.dirname(json_path), exist_ok=True)

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)

        loader = LinearResponseDataLoader(temp_dir)
        spec = DataSourceSpec("test_project", DataState.COMPENSATION)
        source_data = loader.extract_data_source(spec)

        assert source_data["gains"] == test_data["gains_comped"]
        assert source_data["state"] == "compensation"

        import shutil
        shutil.rmtree(temp_dir)


class TestFrequencyResponseComparator:
    """Test FrequencyResponseComparator class"""

    @pytest.fixture
    def sample_source_data(self):
        """Create sample source data for testing"""
        return {
            'gains': [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]],
            'magnitudes': [0.5, 1.0],
            'frequencies': [10.0, 50.0, 100.0],
            'project_name': 'test_project',
            'state': 'origin',
            'label': 'test_project@origin'
        }

    def test_init_default_layout(self):
        """Test FrequencyResponseComparator initialization with default layout"""
        comparator = FrequencyResponseComparator()
        assert comparator.layout_mode == LayoutMode.OVERLAY

    def test_init_custom_layout(self):
        """Test FrequencyResponseComparator initialization with custom layout"""
        comparator = FrequencyResponseComparator(LayoutMode.SIDE_BY_SIDE)
        assert comparator.layout_mode == LayoutMode.SIDE_BY_SIDE

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary output directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        import shutil
        shutil.rmtree(temp_dir)

    def test_compare_sources_overlay(self, sample_source_data, temp_output_dir):
        """Test compare_sources with OVERLAY layout"""
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend

        comparator = FrequencyResponseComparator(LayoutMode.OVERLAY)

        with patch('matplotlib.pyplot.show'):
            fig, output_path = comparator.compare_sources(
                sample_source_data,
                sample_source_data,
                output_folder=temp_output_dir,
                show_plot=False
            )

        assert fig is not None
        assert os.path.exists(output_path)
        assert 'overlay' in output_path

    def test_compare_sources_side_by_side(self, sample_source_data, temp_output_dir):
        """Test compare_sources with SIDE_BY_SIDE layout"""
        import matplotlib
        matplotlib.use('Agg')

        comparator = FrequencyResponseComparator(LayoutMode.SIDE_BY_SIDE)

        with patch('matplotlib.pyplot.show'):
            fig, output_path = comparator.compare_sources(
                sample_source_data,
                sample_source_data,
                output_folder=temp_output_dir,
                show_plot=False
            )

        assert fig is not None
        assert os.path.exists(output_path)
        assert 'sidebyside' in output_path or 'side_by_side' in output_path

    def test_compare_sources_with_freq_range(self, sample_source_data, temp_output_dir):
        """Test compare_sources with frequency range filter"""
        import matplotlib
        matplotlib.use('Agg')

        comparator = FrequencyResponseComparator(LayoutMode.OVERLAY)

        with patch('matplotlib.pyplot.show'):
            fig, output_path = comparator.compare_sources(
                sample_source_data,
                sample_source_data,
                output_folder=temp_output_dir,
                show_plot=False,
                freq_range=[10, 100]
            )

        assert fig is not None
        assert os.path.exists(output_path)

    def test_compare_sources_with_gain_range(self, sample_source_data, temp_output_dir):
        """Test compare_sources with gain range filter"""
        import matplotlib
        matplotlib.use('Agg')

        comparator = FrequencyResponseComparator(LayoutMode.OVERLAY)

        with patch('matplotlib.pyplot.show'):
            fig, output_path = comparator.compare_sources(
                sample_source_data,
                sample_source_data,
                output_folder=temp_output_dir,
                show_plot=False,
                gain_range=[0, 10]
            )

        assert fig is not None
        assert os.path.exists(output_path)

    def test_sync_axis_limits(self):
        """Test _sync_axis_limits method"""
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        comparator = FrequencyResponseComparator()

        fig, (ax1, ax2) = plt.subplots(1, 2)
        ax1.set_xlim(0, 10)
        ax1.set_ylim(0, 20)
        ax2.set_xlim(5, 15)
        ax2.set_ylim(10, 30)

        comparator._sync_axis_limits(ax1, ax2)

        xlim = ax1.get_xlim()
        ylim = ax1.get_ylim()

        assert xlim[0] == 0  # min
        assert xlim[1] == 15  # max
        assert ylim[0] == 0  # min
        assert ylim[1] == 30  # max

        plt.close(fig)


class TestQuickCompare:
    """Test quick_compare convenience function"""

    def test_quick_compare_same_project(self):
        """Test quick_compare with same project for origin vs compensation"""
        import matplotlib
        matplotlib.use('Agg')

        temp_dir = tempfile.mkdtemp()
        test_data = {
            "gains_origin": [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]],
            "gains_comped": [[1.1, 2.1, 3.1], [4.1, 5.1, 6.1]],
            "magnitudes": [0.5, 1.0],
            "frequencies": [10.0, 50.0, 100.0]
        }

        json_path = os.path.join(temp_dir, "test_project", "data", "linear_response.json")
        os.makedirs(os.path.dirname(json_path), exist_ok=True)

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)

        # Note: quick_compare always uses show_plot=False internally
        with patch('matplotlib.pyplot.show'):
            output_path = quick_compare(
                "test_project",
                "test_project",
                state1="origin",
                state2="compensation",
                layout="overlay",
                projects_root=temp_dir
            )

        assert output_path is not None
        assert os.path.exists(output_path)

        import shutil
        shutil.rmtree(temp_dir)

    def test_quick_compare_different_projects(self):
        """Test quick_compare with different projects"""
        import matplotlib
        matplotlib.use('Agg')

        temp_dir = tempfile.mkdtemp()

        # Create two projects
        for proj_name in ["test_project", "test_project2"]:
            test_data = {
                "gains_origin": [[2.0, 3.0, 4.0], [5.0, 6.0, 7.0]],
                "gains_comped": [[2.1, 3.1, 4.1], [5.1, 6.1, 7.1]],
                "magnitudes": [0.5, 1.0],
                "frequencies": [10.0, 50.0, 100.0]
            }

            json_path = os.path.join(temp_dir, proj_name, "data", "linear_response.json")
            os.makedirs(os.path.dirname(json_path), exist_ok=True)

            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(test_data, f)

        # Note: quick_compare always uses show_plot=False internally
        with patch('matplotlib.pyplot.show'):
            output_path = quick_compare(
                "test_project",
                "test_project2",
                state1="origin",
                state2="origin",
                layout="side_by_side",
                projects_root=temp_dir
            )

        assert output_path is not None
        assert os.path.exists(output_path)

        import shutil
        shutil.rmtree(temp_dir)

    def test_quick_compare_side_by_side_layout(self):
        """Test quick_compare with SIDE_BY_SIDE layout"""
        import matplotlib
        matplotlib.use('Agg')

        temp_dir = tempfile.mkdtemp()
        test_data = {
            "gains_origin": [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]],
            "gains_comped": [[1.1, 2.1, 3.1], [4.1, 5.1, 6.1]],
            "magnitudes": [0.5, 1.0],
            "frequencies": [10.0, 50.0, 100.0]
        }

        json_path = os.path.join(temp_dir, "test_project", "data", "linear_response.json")
        os.makedirs(os.path.dirname(json_path), exist_ok=True)

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)

        # Note: quick_compare always uses show_plot=False internally
        with patch('matplotlib.pyplot.show'):
            output_path = quick_compare(
                "test_project",
                layout="side_by_side",
                projects_root=temp_dir
            )

        assert output_path is not None
        assert os.path.exists(output_path)

        import shutil
        shutil.rmtree(temp_dir)

    def test_quick_compare_with_custom_params(self):
        """Test quick_compare with custom parameters"""
        import matplotlib
        matplotlib.use('Agg')

        temp_dir = tempfile.mkdtemp()
        test_data = {
            "gains_origin": [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]],
            "gains_comped": [[1.1, 2.1, 3.1], [4.1, 5.1, 6.1]],
            "magnitudes": [0.5, 1.0],
            "frequencies": [10.0, 50.0, 100.0]
        }

        json_path = os.path.join(temp_dir, "test_project", "data", "linear_response.json")
        os.makedirs(os.path.dirname(json_path), exist_ok=True)

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)

        # Note: quick_compare always uses show_plot=False internally
        with patch('matplotlib.pyplot.show'):
            output_path = quick_compare(
                "test_project",
                layout="overlay",
                projects_root=temp_dir,
                freq_range=[10, 100],
                gain_range=[0, 10],
                figsize=[10, 6],
                dpi=150,
                title="Custom Title"
            )

        assert output_path is not None
        assert os.path.exists(output_path)

        import shutil
        shutil.rmtree(temp_dir)

    def test_quick_compare_with_invalid_project(self):
        """Test quick_compare with non-existent project"""
        import matplotlib
        matplotlib.use('Agg')

        # Note: quick_compare always uses show_plot=False internally
        with pytest.raises(FileNotFoundError):
            quick_compare(
                "nonexistent_project",
                projects_root="/nonexistent"
            )
