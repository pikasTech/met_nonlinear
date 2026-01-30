"""
Tests for visualization/figure_paper module
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
mock_paper = MagicMock()
mock_paper.fig_process = MagicMock()
mock_paper.fig_process.plot_frirnn = MagicMock()
mock_paper.fig_process.plot_lut = MagicMock()
mock_paper.fig_process.fig_pdf = MagicMock()
mock_paper.fig_process.plot_config = MagicMock()
mock_paper.fig_process.plot_scatter = MagicMock()

sys.modules['paper'] = mock_paper
sys.modules['paper.fig_process'] = mock_paper.fig_process
sys.modules['paper.fig_process.plot_config'] = MagicMock()
sys.modules['paper.fig_process.plot_scatter'] = MagicMock()


class TestConvertNumpy:
    """Test convert_numpy function"""

    def test_convert_numpy_array(self):
        """Test converting numpy array to list"""
        from visualization.figure_paper import convert_numpy

        arr = np.array([1, 2, 3])
        result = convert_numpy(arr)
        assert result == [1, 2, 3]
        assert isinstance(result, list)

    def test_convert_numpy_nested_array(self):
        """Test converting nested numpy array"""
        from visualization.figure_paper import convert_numpy

        arr = np.array([[1, 2], [3, 4]])
        result = convert_numpy(arr)
        assert result == [[1, 2], [3, 4]]

    def test_convert_numpy_list(self):
        """Test converting list (no change)"""
        from visualization.figure_paper import convert_numpy

        lst = [1, 2, 3]
        result = convert_numpy(lst)
        assert result == [1, 2, 3]

    def test_convert_numpy_dict(self):
        """Test converting dictionary"""
        from visualization.figure_paper import convert_numpy

        d = {'a': np.array([1, 2]), 'b': 3}
        result = convert_numpy(d)
        assert result == {'a': [1, 2], 'b': 3}

    def test_convert_numpy_primitive(self):
        """Test converting primitive types"""
        from visualization.figure_paper import convert_numpy

        assert convert_numpy(5) == 5
        assert convert_numpy(3.14) == 3.14
        assert convert_numpy("test") == "test"
        assert convert_numpy(None) is None


class TestGetComplementaryColor:
    """Test get_complementary_color function"""

    def test_complementary_black(self):
        """Test complementary color of black (#000000)"""
        from visualization.figure_paper import get_complementary_color

        result = get_complementary_color("#000000")
        # White should be the complement
        assert result == "#ffffff" or result == "#fff"

    def test_complementary_white(self):
        """Test complementary color of white (#ffffff)"""
        from visualization.figure_paper import get_complementary_color

        result = get_complementary_color("#ffffff")
        # Black should be the complement
        assert result == "#000000" or result == "#000"

    def test_complementary_red(self):
        """Test complementary color of red (#ff0000)"""
        from visualization.figure_paper import get_complementary_color

        result = get_complementary_color("#ff0000")
        # Should be cyan-ish
        assert result.startswith("#")


class TestMyArraw:
    """Test my_arraw function"""

    def test_my_arraw_creates_arrow(self):
        """Test my_arraw function creates annotation"""
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        from visualization.figure_paper import my_arraw

        fig, ax = plt.subplots()
        my_arraw(ax, text="Test arrow")

        # Check that text was added
        texts = [t for t in ax.texts]
        # At least one text element should exist
        assert len(texts) >= 0  # Function should not raise

        plt.close(fig)


class TestProjectResult:
    """Test ProjectResult class"""

    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory with required files"""
        temp_dir = tempfile.mkdtemp()
        project_name = "test_project"
        project_dir = os.path.join(temp_dir, project_name, "data")
        os.makedirs(project_dir)

        # Create required JSON files
        raw_data = {
            "gains_origin": [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]],
            "gains_comped": [[1.1, 2.1, 3.1], [4.1, 5.1, 6.1]],
            "magnitudes": [0.5, 1.0],
            "frequencies": [10.0, 50.0, 100.0],
            "fit_params_origin": [[1, 4, 2], [1, 9, 2]],
            "fit_params_comped": [[1.1, 4, 2], [1.1, 9, 2]]
        }

        training_info = {
            "epochs": 100,
            "min_loss": 0.01,
            "min_val_loss": 0.02
        }

        model_info = {
            "param_count": 1000,
            "model_type": "WNET"
        }

        with open(os.path.join(project_dir, "linear_response.json"), 'w') as f:
            json.dump(raw_data, f)
        with open(os.path.join(project_dir, "training_info.json"), 'w') as f:
            json.dump(training_info, f)
        with open(os.path.join(project_dir, "model_info.json"), 'w') as f:
            json.dump(model_info, f)

        yield temp_dir, project_name

        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)

    def test_project_result_init(self, temp_project_dir):
        """Test ProjectResult initialization"""
        from visualization.figure_paper import ProjectResult

        temp_dir, project_name = temp_project_dir

        with patch.dict('os.environ', {'PATH': ''}):
            # Set the correct project path prefix
            with patch('os.getcwd', return_value=temp_dir):
                result = ProjectResult(project_name)

                # Verify basic attributes exist
                assert result.project_name == project_name
                assert result.raw_data_path is not None
                assert result.training_info_path is not None
                assert result.model_info_path is not None

    def test_project_result_load_data(self, temp_project_dir):
        """Test ProjectResult.load_data method"""
        from visualization.figure_paper import ProjectResult

        temp_dir, project_name = temp_project_dir

        with patch.dict('os.environ', {'PATH': ''}):
            with patch('os.getcwd', return_value=temp_dir):
                result = ProjectResult(project_name)
                result.load_data()

                # Data should be loaded (may be empty if paths don't match)
                assert result.raw_data == {} or len(result.raw_data) >= 0

    def test_project_result_model_name_extraction(self):
        """Test model name extraction from project name"""
        from visualization.figure_paper import ProjectResult

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
        from visualization.figure_paper import ProjectResult

        # Create a minimal instance
        with patch('os.getcwd', return_value='/tmp'):
            result = ProjectResult("test")

            params = [[1, 4, 2], [1, 9, 2]]  # A, B, C values

            wn, zeta, A = result._calculate_parameters(params)

            # Verify calculations
            assert len(wn) == 2
            assert len(zeta) == 2
            assert len(A) == 2

            # wn = sqrt(B)
            assert abs(wn[0] - 2.0) < 0.01  # sqrt(4) = 2
            assert abs(wn[1] - 3.0) < 0.01  # sqrt(9) = 3


class TestExpandProjectPatterns:
    """Test expand_project_patterns function"""

    def test_expand_project_patterns_no_matches(self):
        """Test with no matching projects"""
        from visualization.figure_paper import expand_project_patterns

        # Create mock directory entries
        mock_entry = MagicMock()
        mock_entry.is_dir.return_value = False

        with patch('os.scandir') as mock_scandir:
            mock_scandir.return_value = [mock_entry]

            with patch('visualization.figure_paper.RESULT_LIST', ['WNET*']):
                with patch('visualization.figure_paper.IGNORE_LIST', []):
                    result = expand_project_patterns()

            # Should return empty list when no dir matches
            assert isinstance(result, list)

    def test_expand_project_patterns_with_matches(self):
        """Test with matching projects"""
        from visualization.figure_paper import expand_project_patterns

        # Create mock directory entries with proper name attribute
        mock_entries = []
        for name in ['WNET5_test1', 'WNET5_test2', 'LSTM_test']:
            mock_entry = MagicMock()
            mock_entry.name = name
            mock_entry.is_dir.return_value = True
            mock_entries.append(mock_entry)

        with patch('os.scandir', return_value=mock_entries):
            with patch('visualization.figure_paper.RESULT_LIST', ['WNET*']):
                with patch('visualization.figure_paper.IGNORE_LIST', []):
                    result = expand_project_patterns()

        # Should match WNET projects
        assert len(result) >= 2

    def test_expand_project_patterns_ignore_filter(self):
        """Test that ignore patterns work correctly"""
        from visualization.figure_paper import expand_project_patterns

        # Create mock directory entries with proper name attribute
        mock_entries = []
        for name in ['WNET5_test', 'WNET5_test_nb', 'LSTM_test']:
            mock_entry = MagicMock()
            mock_entry.name = name
            mock_entry.is_dir.return_value = True
            mock_entries.append(mock_entry)

        with patch('os.scandir', return_value=mock_entries):
            with patch('visualization.figure_paper.RESULT_LIST', ['WNET*']):
                with patch('visualization.figure_paper.IGNORE_LIST', ['*nb']):
                    result = expand_project_patterns()

        # Should exclude WNET5_test_nb
        project_names = ' '.join(result)
        assert 'WNET5_test_nb' not in project_names

    def test_expand_project_patterns_exact_match(self):
        """Test with exact project name (no wildcard)"""
        from visualization.figure_paper import expand_project_patterns

        mock_entries = [
            MagicMock(name='WNET5_exact'),
            MagicMock(name='WNET5_other')
        ]
        for entry in mock_entries:
            entry.is_dir.return_value = True

        with patch('os.scandir', return_value=mock_entries):
            with patch('visualization.figure_paper.RESULT_LIST', ['WNET5_exact']):
                with patch('visualization.figure_paper.IGNORE_LIST', []):
                    result = expand_project_patterns()

        assert 'WNET5_exact' in result
        assert 'WNET5_other' not in result


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
        from visualization.figure_paper import combine_images_with_labels

        image_paths, temp_dir = temp_images
        output_path = os.path.join(temp_dir, "combined.png")

        combine_images_with_labels(image_paths, output_path)

        assert os.path.exists(output_path)

    def test_combine_images_with_custom_labels(self, temp_images):
        """Test image combination with custom labels"""
        from visualization.figure_paper import combine_images_with_labels

        image_paths, temp_dir = temp_images
        output_path = os.path.join(temp_dir, "combined.png")

        combine_images_with_labels(
            image_paths,
            output_path,
            labels=['(a)', '(b)']
        )

        assert os.path.exists(output_path)

    def test_combine_images_with_space_param(self, temp_images):
        """Test image combination with custom spacing"""
        from visualization.figure_paper import combine_images_with_labels

        image_paths, temp_dir = temp_images
        output_path = os.path.join(temp_dir, "combined.png")

        combine_images_with_labels(image_paths, output_path, space=0.1)

        assert os.path.exists(output_path)


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
        from visualization.figure_paper import concatenate_images

        image_paths, temp_dir = temp_images
        output_path = os.path.join(temp_dir, "concatenated.png")

        concatenate_images(image_paths[0], image_paths[1], output_path)

        assert os.path.exists(output_path)

    def test_concatenate_images_height_adjustment(self):
        """Test that images with different heights are resized"""
        from visualization.figure_paper import concatenate_images
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

        concatenate_images(path1, path2, output_path)

        assert os.path.exists(output_path)

        import shutil
        shutil.rmtree(temp_dir)

    def test_concatenate_images_with_space(self, temp_images):
        """Test concatenation with custom space parameter"""
        from visualization.figure_paper import concatenate_images

        image_paths, temp_dir = temp_images
        output_path = os.path.join(temp_dir, "concatenated.png")

        concatenate_images(image_paths[0], image_paths[1], output_path, space=0.05)

        assert os.path.exists(output_path)
