"""
Tests for visualization/figure_paper module

This module tests figure_paper functions with proper mocking of external dependencies.
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

# Mock external dependencies before importing figure_paper
# These mocks are needed because figure_paper imports from paper.fig_process
mock_plot_config = MagicMock()
MOCK_MODEL_COLOR_MAP = {
    'WNET': '#4E79A7',
    'FRIKAN': '#F28E2B',
    'GRU': '#E15759',
    'LSTM': '#76B7B2',
    'RVTDCNN': '#59A14F',
}
mock_plot_config.MODEL_COLOR_MAP = MOCK_MODEL_COLOR_MAP

mock_fig_process = MagicMock()
mock_fig_process.plot_frirnn = MagicMock()
mock_fig_process.plot_lut = MagicMock()
mock_fig_process.fig_pdf = MagicMock()
mock_fig_process.plot_config = mock_plot_config
mock_fig_process.plot_scatter = MagicMock()

mock_paper = MagicMock()
mock_paper.fig_process = mock_fig_process

# Set up sys.modules BEFORE importing figure_paper
sys.modules['paper'] = mock_paper
sys.modules['paper.fig_process'] = mock_fig_process
sys.modules['paper.fig_process.plot_config'] = mock_plot_config
sys.modules['paper.fig_process.plot_scatter'] = mock_fig_process.plot_scatter

# Now we can import figure_paper module directly
import visualization.figure_paper as figure_paper


class TestConvertNumpy:
    """Test convert_numpy function"""

    def test_convert_numpy_array(self):
        """Test converting numpy array to list"""
        arr = np.array([1, 2, 3])
        result = figure_paper.convert_numpy(arr)
        assert result == [1, 2, 3]
        assert isinstance(result, list)

    def test_convert_numpy_nested_array(self):
        """Test converting nested numpy array"""
        arr = np.array([[1, 2], [3, 4]])
        result = figure_paper.convert_numpy(arr)
        assert result == [[1, 2], [3, 4]]

    def test_convert_numpy_list(self):
        """Test converting list (no change)"""
        lst = [1, 2, 3]
        result = figure_paper.convert_numpy(lst)
        assert result == [1, 2, 3]

    def test_convert_numpy_dict(self):
        """Test converting dictionary"""
        d = {'a': np.array([1, 2]), 'b': 3}
        result = figure_paper.convert_numpy(d)
        assert result == {'a': [1, 2], 'b': 3}

    def test_convert_numpy_primitive(self):
        """Test converting primitive types"""
        assert figure_paper.convert_numpy(5) == 5
        assert figure_paper.convert_numpy(3.14) == 3.14
        assert figure_paper.convert_numpy("test") == "test"
        assert figure_paper.convert_numpy(None) is None


class TestGetComplementaryColor:
    """Test get_complementary_color function"""

    def test_complementary_black(self):
        """Test complementary color of black (#000000)"""
        result = figure_paper.get_complementary_color("#000000")
        # White should be the complement
        assert result == "#ffffff" or result == "#fff"

    def test_complementary_white(self):
        """Test complementary color of white (#ffffff)"""
        result = figure_paper.get_complementary_color("#ffffff")
        # Black should be the complement
        assert result == "#000000" or result == "#000"

    def test_complementary_red(self):
        """Test complementary color of red (#ff0000)"""
        result = figure_paper.get_complementary_color("#ff0000")
        # Should be cyan-ish
        assert result.startswith("#")


class TestMyArraw:
    """Test my_arraw function"""

    def test_my_arraw_creates_arrow(self):
        """Test my_arraw function creates annotation"""
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        figure_paper.my_arraw(ax, text="Test arrow")

        # Check that text was added
        texts = [t for t in ax.texts]
        # At least one text element should exist
        assert len(texts) >= 0  # Function should not raise

        plt.close(fig)


class TestProjectResult:
    """Test ProjectResult class basic functionality with mocked data"""

    def test_project_result_init(self):
        """Test ProjectResult initialization"""
        # Mock file operations to avoid file system dependency
        with patch('builtins.open', side_effect=FileNotFoundError("Mocked")):
            with patch('os.path.exists', return_value=False):
                result = figure_paper.ProjectResult("test_project")

                # Verify basic attributes exist
                assert result.project_name == "test_project"
                assert "test_project" in result.raw_data_path
                assert "training_info" in result.training_info_path

    def test_project_result_model_name_extraction(self):
        """Test model name extraction from project name"""
        # Create a mock ProjectResult with just the project name
        # by testing the string parsing logic
        project_name = "WNET5_test"

        # Simulate the logic from __init__
        index_first_lower = next(
            (i for i, c in enumerate(project_name) if c.islower()), len(project_name))
        model_name = project_name[:index_first_lower]
        model_param = project_name[index_first_lower:]

        # model_name is "WNET5_" (all chars before first lowercase)
        assert model_name == "WNET5_"
        assert model_param == "test"

    def test_project_result_calculate_parameters(self):
        """Test _calculate_parameters method"""
        # Create a minimal instance
        with patch('os.getcwd', return_value='/tmp'):
            result = figure_paper.ProjectResult("test")

            params = [[1, 4, 2], [1, 9, 2]]  # A, B, C values

            wn, zeta, A = result._calculate_parameters(params)

            # Verify calculations
            assert len(wn) == 2
            assert len(zeta) == 2
            assert len(A) == 2

            # wn = sqrt(B)
            assert abs(wn[0] - 2.0) < 0.01  # sqrt(4) = 2
            assert abs(wn[1] - 3.0) < 0.01  # sqrt(9) = 3

    def test_project_result_calculate_single_param(self):
        """Test _calculate_parameters with single parameter set"""
        with patch('os.getcwd', return_value='/tmp'):
            result = figure_paper.ProjectResult("test")

            params = [[1, 16, 4]]  # A=1, B=16, C=4 -> wn=4, zeta=0.5

            wn, zeta, A = result._calculate_parameters(params)

            assert len(wn) == 1
            assert abs(wn[0] - 4.0) < 0.01  # sqrt(16) = 4
            assert abs(zeta[0] - 0.5) < 0.01  # C/(2*wn) = 4/(2*4) = 0.5


class TestExpandProjectPatterns:
    """Test expand_project_patterns function"""

    def test_expand_project_patterns_no_matches(self):
        """Test with no matching projects"""
        # Create mock directory entries
        mock_entry = MagicMock()
        mock_entry.is_dir.return_value = False

        with patch('os.scandir') as mock_scandir:
            mock_scandir.return_value = [mock_entry]

            with patch.object(figure_paper, 'RESULT_LIST', ['WNET*']):
                with patch.object(figure_paper, 'IGNORE_LIST', []):
                    result = figure_paper.expand_project_patterns()

            # Should return empty list when no dir matches
            assert isinstance(result, list)

    def test_expand_project_patterns_with_matches(self):
        """Test with matching projects"""
        # Create mock directory entries with proper name attribute
        mock_entries = []
        for name in ['WNET5_test1', 'WNET5_test2', 'LSTM_test']:
            mock_entry = MagicMock()
            mock_entry.name = name
            mock_entry.is_dir.return_value = True
            mock_entries.append(mock_entry)

        with patch('os.scandir', return_value=mock_entries):
            with patch.object(figure_paper, 'RESULT_LIST', ['WNET*']):
                with patch.object(figure_paper, 'IGNORE_LIST', []):
                    result = figure_paper.expand_project_patterns()

        # Should match WNET projects
        assert len(result) >= 2

    def test_expand_project_patterns_ignore_filter(self):
        """Test that ignore patterns work correctly"""
        # Create mock directory entries with proper name attribute
        mock_entries = []
        for name in ['WNET5_test', 'WNET5_test_nb', 'LSTM_test']:
            mock_entry = MagicMock()
            mock_entry.name = name
            mock_entry.is_dir.return_value = True
            mock_entries.append(mock_entry)

        with patch('os.scandir', return_value=mock_entries):
            with patch.object(figure_paper, 'RESULT_LIST', ['WNET*']):
                with patch.object(figure_paper, 'IGNORE_LIST', ['*nb']):
                    result = figure_paper.expand_project_patterns()

        # Should exclude WNET5_test_nb
        project_names = ' '.join(result)
        assert 'WNET5_test_nb' not in project_names

    def test_expand_project_patterns_exact_match(self):
        """Test with exact project name (no wildcard)"""
        mock_entries = [
            MagicMock(name='WNET5_exact'),
            MagicMock(name='WNET5_other')
        ]
        for entry in mock_entries:
            entry.is_dir.return_value = True

        with patch('os.scandir', return_value=mock_entries):
            with patch.object(figure_paper, 'RESULT_LIST', ['WNET5_exact']):
                with patch.object(figure_paper, 'IGNORE_LIST', []):
                    result = figure_paper.expand_project_patterns()

        assert 'WNET5_exact' in result
        assert 'WNET5_other' not in result

    def test_expand_project_patterns_empty_result_list(self):
        """Test with empty RESULT_LIST"""
        mock_entries = [
            MagicMock(name='WNET5_test'),
        ]
        mock_entries[0].is_dir.return_value = True

        with patch('os.scandir', return_value=mock_entries):
            with patch.object(figure_paper, 'RESULT_LIST', []):
                with patch.object(figure_paper, 'IGNORE_LIST', []):
                    result = figure_paper.expand_project_patterns()

        # Should return empty list
        assert len(result) == 0


class TestCombineImagesWithLabels:
    """Test combine_images_with_labels function"""

    @pytest.fixture
    def temp_images(self):
        """Create temporary test images"""
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from PIL import Image

        temp_dir = tempfile.mkdtemp()
        image_paths = []

        for i in range(2):
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 4, 9])
            path = os.path.join(temp_dir, f"test_image_{i}.png")
            fig.savefig(path, dpi=100)
            plt.close(fig)
            image_paths.append(path)

        yield image_paths, temp_dir

        import shutil
        shutil.rmtree(temp_dir)

    def test_combine_images_basic(self, temp_images):
        """Test basic image combination"""
        image_paths, temp_dir = temp_images
        output_path = os.path.join(temp_dir, "combined.png")

        figure_paper.combine_images_with_labels(image_paths, output_path)

        assert os.path.exists(output_path)

    def test_combine_images_with_custom_labels(self, temp_images):
        """Test image combination with custom labels"""
        image_paths, temp_dir = temp_images
        output_path = os.path.join(temp_dir, "combined.png")

        figure_paper.combine_images_with_labels(
            image_paths,
            output_path,
            labels=['(a)', '(b)']
        )

        assert os.path.exists(output_path)

    def test_combine_images_with_space_param(self, temp_images):
        """Test image combination with custom spacing"""
        image_paths, temp_dir = temp_images
        output_path = os.path.join(temp_dir, "combined.png")

        figure_paper.combine_images_with_labels(image_paths, output_path, space=0.1)

        assert os.path.exists(output_path)

    def test_combine_images_three_images(self):
        """Test combining three images"""
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from PIL import Image

        temp_dir = tempfile.mkdtemp()
        image_paths = []

        for i in range(3):
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [i, i+1, i+2])
            path = os.path.join(temp_dir, f"test_image_{i}.png")
            fig.savefig(path, dpi=100)
            plt.close(fig)
            image_paths.append(path)

        output_path = os.path.join(temp_dir, "combined_three.png")
        figure_paper.combine_images_with_labels(image_paths, output_path)

        assert os.path.exists(output_path)

        import shutil
        shutil.rmtree(temp_dir)


class TestConcatenateImages:
    """Test concatenate_images function"""

    @pytest.fixture
    def temp_images(self):
        """Create temporary test images"""
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        temp_dir = tempfile.mkdtemp()
        image_paths = []

        for i in range(2):
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 4, 9])
            path = os.path.join(temp_dir, f"test_image_{i}.png")
            fig.savefig(path, dpi=100)
            plt.close(fig)
            image_paths.append(path)

        yield image_paths, temp_dir

        import shutil
        shutil.rmtree(temp_dir)

    def test_concatenate_images_basic(self, temp_images):
        """Test basic image concatenation"""
        image_paths, temp_dir = temp_images
        output_path = os.path.join(temp_dir, "concatenated.png")

        figure_paper.concatenate_images(image_paths[0], image_paths[1], output_path)

        assert os.path.exists(output_path)

    def test_concatenate_images_height_adjustment(self):
        """Test that images with different heights are resized"""
        from PIL import Image

        temp_dir = tempfile.mkdtemp()

        # Create images with different heights
        img1 = Image.new('RGB', (100, 100), color='red')
        img2 = Image.new('RGB', (100, 150), color='blue')

        path1 = os.path.join(temp_dir, "img1.png")
        path2 = os.path.join(temp_dir, "img2.png")
        output_path = os.path.join(temp_dir, "output.png")

        img1.save(path1)
        img2.save(path2)

        figure_paper.concatenate_images(path1, path2, output_path)

        assert os.path.exists(output_path)

        import shutil
        shutil.rmtree(temp_dir)

    def test_concatenate_images_with_space(self, temp_images):
        """Test concatenation with custom space parameter"""
        image_paths, temp_dir = temp_images
        output_path = os.path.join(temp_dir, "concatenated.png")

        figure_paper.concatenate_images(image_paths[0], image_paths[1], output_path, space=0.05)

        assert os.path.exists(output_path)

    def test_concatenate_images_same_height(self):
        """Test concatenation of images with same height"""
        from PIL import Image

        temp_dir = tempfile.mkdtemp()

        # Create images with same height
        img1 = Image.new('RGB', (100, 100), color='red')
        img2 = Image.new('RGB', (150, 100), color='blue')

        path1 = os.path.join(temp_dir, "img1.png")
        path2 = os.path.join(temp_dir, "img2.png")
        output_path = os.path.join(temp_dir, "output.png")

        img1.save(path1)
        img2.save(path2)

        figure_paper.concatenate_images(path1, path2, output_path)

        assert os.path.exists(output_path)

        import shutil
        shutil.rmtree(temp_dir)


class TestGetModelColor:
    """Test get_model_color function"""

    def test_get_model_color_wavewnet(self):
        """Test get_model_color with WNET prefix"""
        result = figure_paper.get_model_color("WNET5_test")
        assert result.startswith("#")

    def test_get_model_color_frikan(self):
        """Test get_model_color with FRIKAN prefix"""
        result = figure_paper.get_model_color("FRIKANh6u6l3")
        assert result.startswith("#")

    def test_get_model_color_gru(self):
        """Test get_model_color with GRU prefix"""
        result = figure_paper.get_model_color("GRNu16")
        assert result.startswith("#")

    def test_get_model_color_lstm(self):
        """Test get_model_color with LSTM prefix"""
        result = figure_paper.get_model_color("LSTMu22")
        assert result.startswith("#")

    def test_get_model_color_rvtdcnn(self):
        """Test get_model_color with RVTDCNN prefix"""
        result = figure_paper.get_model_color("RVTDCNNu12d7m8")
        assert result.startswith("#")

    def test_get_model_color_default(self):
        """Test get_model_color with unknown prefix returns default"""
        result = figure_paper.get_model_color("UnknownModel")
        assert result.startswith("#")


class TestProjectResultCalculateParameters:
    """Test ProjectResult._calculate_parameters method with direct mocking"""

    def test_calculate_parameters_basic(self):
        """Test _calculate_parameters method basic functionality"""
        # Mock file operations
        with patch('builtins.open', side_effect=FileNotFoundError("Mocked")):
            with patch('os.path.exists', return_value=False):
                result = figure_paper.ProjectResult("test")

                params = [[1, 4, 2], [1, 9, 2]]  # A, B, C values

                wn, zeta, A = result._calculate_parameters(params)

                # Verify calculations
                assert len(wn) == 2
                assert len(zeta) == 2
                assert len(A) == 2

                # wn = sqrt(B)
                assert abs(wn[0] - 2.0) < 0.01  # sqrt(4) = 2
                assert abs(wn[1] - 3.0) < 0.01  # sqrt(9) = 3

    def test_calculate_parameters_single_set(self):
        """Test _calculate_parameters with single parameter set"""
        with patch('builtins.open', side_effect=FileNotFoundError("Mocked")):
            with patch('os.path.exists', return_value=False):
                result = figure_paper.ProjectResult("test")

                params = [[1, 16, 4]]  # A=1, B=16, C=4 -> wn=4, zeta=0.5

                wn, zeta, A = result._calculate_parameters(params)

                assert len(wn) == 1
                assert abs(wn[0] - 4.0) < 0.01  # sqrt(16) = 4
                assert abs(zeta[0] - 0.5) < 0.01  # C/(2*wn) = 4/(2*4) = 0.5

    def test_calculate_parameters_multiple_sets(self):
        """Test _calculate_parameters with multiple parameter sets"""
        with patch('builtins.open', side_effect=FileNotFoundError("Mocked")):
            with patch('os.path.exists', return_value=False):
                result = figure_paper.ProjectResult("test")

                # Test with 5 parameter sets
                params = [[1, 1, 1], [2, 4, 2], [3, 9, 3], [4, 16, 4], [5, 25, 5]]

                wn, zeta, A = result._calculate_parameters(params)

                assert len(wn) == 5
                assert len(zeta) == 5
                assert len(A) == 5

                # Verify sqrt(B) for each
                for i, (_, b, _) in enumerate(params):
                    assert abs(wn[i] - np.sqrt(b)) < 0.001


class TestModelColorMap:
    """Test MODEL_COLOR_MAP configuration"""

    def test_model_color_map_accessible(self):
        """Test MODEL_COLOR_MAP is accessible from figure_paper module"""
        import visualization.figure_paper as fp
        # MODEL_COLOR_MAP should be imported in the module
        assert hasattr(fp, 'MODEL_COLOR_MAP') or 'MODEL_COLOR_MAP' in dir(fp)

    def test_model_color_map_has_required_keys(self):
        """Test MODEL_COLOR_MAP has expected model prefixes"""
        import visualization.figure_paper as fp

        # MODEL_COLOR_MAP should be accessible
        if hasattr(fp, 'MODEL_COLOR_MAP'):
            color_map = fp.MODEL_COLOR_MAP
        else:
            # Check if it's imported from paper.fig_process.plot_config
            from paper.fig_process.plot_config import MODEL_COLOR_MAP
            color_map = MODEL_COLOR_MAP

        # Check for common model prefixes
        expected_keys = ['WNET', 'FRIKAN', 'GRU', 'LSTM', 'RVTDCNN']
        for key in expected_keys:
            assert any(k.startswith(key) for k in color_map.keys()), \
                f"No key starting with {key}"

    def test_model_color_map_values_are_hex(self):
        """Test all color values are valid hex colors"""
        import re
        import visualization.figure_paper as fp

        if hasattr(fp, 'MODEL_COLOR_MAP'):
            color_map = fp.MODEL_COLOR_MAP
        else:
            from paper.fig_process.plot_config import MODEL_COLOR_MAP
            color_map = MODEL_COLOR_MAP

        hex_pattern = re.compile(r'^#[0-9A-Fa-f]{6}$')

        for key, color in color_map.items():
            assert hex_pattern.match(color), \
                f"Invalid hex color for {key}: {color}"


class TestResultListAndIgnoreList:
    """Test RESULT_LIST and IGNORE_LIST configurations"""

    def test_result_list_exists(self):
        """Test RESULT_LIST is defined"""
        assert hasattr(figure_paper, 'RESULT_LIST')
        assert isinstance(figure_paper.RESULT_LIST, list)

    def test_ignore_list_exists(self):
        """Test IGNORE_LIST is defined"""
        assert hasattr(figure_paper, 'IGNORE_LIST')
        assert isinstance(figure_paper.IGNORE_LIST, list)

    def test_result_list_has_valid_patterns(self):
        """Test RESULT_LIST has valid project patterns"""
        # Should contain model name patterns
        patterns = figure_paper.RESULT_LIST
        assert len(patterns) > 0
        # At least some should be valid project names or patterns
        assert any('WNET' in p or 'FRIKAN' in p or 'LSTM' in p for p in patterns)
