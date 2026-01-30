"""
Tests for core/wave_generator module

Note: These tests focus on the DatasetWaveGenerator class structure and interface.
Full integration tests require actual project files.
"""

import pytest
import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from types import SimpleNamespace

# Add src to path
_SRC_DIR = Path(__file__).parent.parent.parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from core.wave_generator import DatasetWaveGenerator


@pytest.fixture
def mock_project_manager():
    """Create a mock ProjectManager (module-level fixture)"""
    pm = MagicMock()
    pm.project_name = 'test_project'
    pm.checkpoint_dir = 'projects/test_project/data'
    pm.config = MagicMock()
    pm.config.dataset_type = 'MET'
    return pm


@pytest.fixture
def wave_generator(mock_project_manager):
    """Create a DatasetWaveGenerator instance"""
    generator = DatasetWaveGenerator(mock_project_manager)
    return generator


class TestDatasetWaveGeneratorStructure:
    """Test DatasetWaveGenerator class structure"""

    def test_init_sets_attributes(self, wave_generator, mock_project_manager):
        """Test initialization sets all required attributes"""
        assert wave_generator.project_manager == mock_project_manager
        assert wave_generator.config == mock_project_manager.config
        assert wave_generator.logger is not None

    def test_logger_name(self, wave_generator):
        """Test logger is named correctly"""
        assert 'wave_generator' in wave_generator.logger.name


class TestDatasetWaveGeneratorPrepareOutputFolder:
    """Test _prepare_output_folder method"""

    def test_default_output_folder_path(self, wave_generator, mock_project_manager):
        """Test default output folder path is derived correctly"""
        with patch('os.path.exists', return_value=False):
            with patch('os.makedirs'):
                with patch('os.access', return_value=True):
                    result = wave_generator._prepare_output_folder(None, force=False)

                    expected_path = os.path.join(
                        mock_project_manager.checkpoint_dir,
                        'wave_output'
                    )
                    assert result == expected_path

    def test_custom_output_folder_path(self, wave_generator):
        """Test custom output folder path is used"""
        custom_path = '/custom/output/path'

        with patch('os.path.exists', return_value=False):
            with patch('os.makedirs'):
                with patch('os.access', return_value=True):
                    result = wave_generator._prepare_output_folder(custom_path, force=False)

                    assert result == custom_path

    def test_force_mode_with_existing_files(self, wave_generator):
        """Test force mode overwrites existing files"""
        custom_path = '/tmp/existing_output'

        with patch('os.path.exists', return_value=True):
            with patch('os.listdir', return_value=['file1.wave', 'file2.wave']):
                with patch('os.makedirs'):
                    with patch('os.access', return_value=True):
                        # Force mode should not raise even with existing files
                        result = wave_generator._prepare_output_folder(custom_path, force=True)

                        assert result == custom_path

    def test_non_force_mode_with_existing_files_raises(self, wave_generator):
        """Test non-force mode raises error with existing files"""
        custom_path = '/tmp/existing_output'

        with patch('os.path.exists', return_value=True):
            with patch('os.listdir', return_value=['file1.wave']):
                with pytest.raises(FileExistsError) as exc_info:
                    wave_generator._prepare_output_folder(custom_path, force=False)

                assert 'contains existing wave files' in str(exc_info.value)

    def test_creates_directory_if_not_exists(self, wave_generator):
        """Test directory is created if it doesn't exist"""
        custom_path = '/new/output/path'

        with patch('os.path.exists', return_value=False):
            with patch('os.makedirs') as mock_makedirs:
                with patch('os.access', return_value=True):
                    result = wave_generator._prepare_output_folder(custom_path, force=False)

                    mock_makedirs.assert_called_once_with(custom_path, exist_ok=True)

    def test_permission_error_if_not_writable(self, wave_generator):
        """Test PermissionError is raised if directory is not writable"""
        custom_path = '/readonly/path'

        # os.path.exists returns False so we skip existing files check
        # os.makedirs succeeds
        # os.access returns False so PermissionError is raised
        with patch('os.path.exists', return_value=False):
            with patch('os.makedirs'):
                with patch('os.access', return_value=False):
                    with pytest.raises(PermissionError) as exc_info:
                        wave_generator._prepare_output_folder(custom_path, force=False)

                    assert 'No write permission' in str(exc_info.value)


class TestDatasetWaveGeneratorLoadDataset:
    """Test _load_dataset method"""

    def test_load_dataset_uses_model_engine(self, wave_generator, mock_project_manager):
        """Test _load_dataset creates ModelEngine and loads dataset"""
        mock_engine = MagicMock()
        mock_dataset = MagicMock()
        mock_engine.load_dataset.return_value = None
        mock_engine.prepare_training_data.return_value = None
        mock_engine.dataset_test = mock_dataset

        with patch('core.wave_generator.ModelEngine', return_value=mock_engine):
            result = wave_generator._load_dataset()

            # Verify ModelEngine was created with correct arguments
            from core.wave_generator import ModelEngine
            ModelEngine.assert_called_once_with(
                mock_project_manager,
                checkpoint_dir=mock_project_manager.checkpoint_dir
            )

            # Verify load_dataset was called
            mock_engine.load_dataset.assert_called_once()

            # Verify prepare_training_data was called with output_folder=None
            mock_engine.prepare_training_data.assert_called_once_with(
                output_folder=None
            )

            # Verify dataset_test was returned
            assert result == mock_dataset


class TestDatasetWaveGeneratorGenerateWaveFiles:
    """Test _generate_wave_files method"""

    def test_generate_wave_files_calls_export(self, wave_generator, mock_project_manager):
        """Test _generate_wave_files calls dataset.export_to_wave"""
        mock_dataset = MagicMock()
        mock_dataset.export_to_wave.return_value = {
            'input': '/path/to/input.wave',
            'output': '/path/to/output.wave'
        }
        mock_dataset.magn_list = [0.1, 0.2]
        mock_dataset.freq_list = [10, 20]
        mock_dataset.magn_num = 2
        mock_dataset.freq_num = 2
        mock_dataset.fs = 2000
        mock_dataset.time_cliped_s = 2.0
        mock_dataset.type = 'MET'

        with patch('os.makedirs'):
            result = wave_generator._generate_wave_files(
                mock_dataset,
                '/output/path',
                compress=True
            )

            # Verify export_to_wave was called
            mock_dataset.export_to_wave.assert_called_once_with(
                output_folder='/output/path',
                description=f"Wave data for {mock_project_manager.project_name} - {mock_project_manager.config.dataset_type}",
                author="Generated by cli.py",
                compress=True
            )

    def test_generate_wave_files_returns_dict(self, wave_generator, mock_project_manager):
        """Test _generate_wave_files returns expected dictionary"""
        mock_dataset = MagicMock()
        mock_dataset.export_to_wave.return_value = {
            'input': '/path/to/input.wave',
            'output': '/path/to/output.wave'
        }
        mock_dataset.magn_list = [0.1, 0.2]
        mock_dataset.freq_list = [10, 20]
        mock_dataset.magn_num = 2
        mock_dataset.freq_num = 2
        mock_dataset.fs = 2000
        mock_dataset.time_cliped_s = 2.0
        mock_dataset.type = 'MET'

        with patch('os.makedirs'):
            result = wave_generator._generate_wave_files(
                mock_dataset,
                '/output/path',
                compress=True
            )

            # Verify return structure
            assert isinstance(result, dict)
            assert 'project_name' in result
            assert 'dataset_type' in result
            assert 'output_folder' in result
            assert 'compress' in result
            assert 'files' in result
            assert 'dataset_info' in result

            assert result['project_name'] == mock_project_manager.project_name
            assert result['dataset_type'] == mock_project_manager.config.dataset_type


class TestDatasetWaveGeneratorFindExistingWaveFiles:
    """Test _find_existing_wave_files method"""

    def test_finds_wave_files(self, wave_generator):
        """Test _find_existing_wave_files finds .wave files"""
        with patch('os.listdir', return_value=['file1.wave', 'file2.wave', 'file3.txt']):
            with patch('os.path.exists', return_value=True):
                result = wave_generator._find_existing_wave_files('/output/path')

                assert len(result) == 2
                assert 'file1.wave' in result
                assert 'file2.wave' in result
                assert 'file3.txt' not in result

    def test_returns_empty_list_for_empty_dir(self, wave_generator):
        """Test _find_existing_wave_files returns empty list for empty directory"""
        with patch('os.listdir', return_value=[]):
            result = wave_generator._find_existing_wave_files('/empty/path')

            assert result == []

    def test_returns_empty_list_for_nonexistent_dir(self, wave_generator):
        """Test _find_existing_wave_files returns empty list for nonexistent directory"""
        with patch('os.path.exists', return_value=False):
            result = wave_generator._find_existing_wave_files('/nonexistent/path')

            assert result == []


class TestDatasetWaveGeneratorLogGenerationResult:
    """Test _log_generation_result method"""

    def test_logs_generation_result(self, wave_generator, caplog):
        """Test _log_generation_result logs info messages"""
        result = {
            'project_name': 'test_project',
            'dataset_type': 'MET',
            'output_folder': '/output/path',
            'files': {'input': '/path/input.wave'},
            'dataset_info': {
                'magn_num': 2,
                'freq_num': 2
            }
        }

        with caplog.at_level('INFO'):
            wave_generator._log_generation_result(result)

        # Verify log messages contain expected info
        assert 'test_project' in caplog.text
        assert 'MET' in caplog.text
        assert '/output/path' in caplog.text


class TestDatasetWaveGeneratorGenerateWaveData:
    """Test generate_wave_data main method"""

    def test_generate_wave_data_success(self, wave_generator):
        """Test generate_wave_data completes successfully"""
        mock_dataset = MagicMock()
        mock_dataset.export_to_wave.return_value = {
            'input': '/path/to/input.wave'
        }
        mock_dataset.magn_list = [0.1]
        mock_dataset.freq_list = [10]
        mock_dataset.magn_num = 1
        mock_dataset.freq_num = 1
        mock_dataset.fs = 2000
        mock_dataset.time_cliped_s = 2.0
        mock_dataset.type = 'MET'

        with patch.object(wave_generator, '_prepare_output_folder', return_value='/output/path'):
            with patch.object(wave_generator, '_load_dataset', return_value=mock_dataset):
                with patch.object(wave_generator, '_generate_wave_files', return_value={'files': {}}):
                    with patch.object(wave_generator, '_log_generation_result'):
                        result = wave_generator.generate_wave_data()

                        assert 'files' in result

    def test_generate_wave_data_propagates_exceptions(self, wave_generator):
        """Test generate_wave_data propagates exceptions from sub-methods"""
        with patch.object(wave_generator, '_prepare_output_folder', side_effect=ValueError("Test error")):
            with pytest.raises(ValueError) as exc_info:
                wave_generator.generate_wave_data()

            assert "Test error" in str(exc_info.value)

    def test_generate_wave_data_with_custom_params(self, wave_generator):
        """Test generate_wave_data passes custom parameters correctly"""
        mock_dataset = MagicMock()
        mock_dataset.export_to_wave.return_value = {}
        mock_dataset.magn_list = []
        mock_dataset.freq_list = []
        mock_dataset.magn_num = 0
        mock_dataset.freq_num = 0
        mock_dataset.fs = 2000
        mock_dataset.time_cliped_s = 2.0
        mock_dataset.type = 'MET'

        with patch.object(wave_generator, '_prepare_output_folder', return_value='/custom/output') as mock_prepare:
            with patch.object(wave_generator, '_load_dataset', return_value=mock_dataset):
                with patch.object(wave_generator, '_generate_wave_files', return_value={'files': {}}):
                    with patch.object(wave_generator, '_log_generation_result'):
                        wave_generator.generate_wave_data(
                            output_folder='/custom/output',
                            compress=False,
                            force=True
                        )

                        mock_prepare.assert_called_once_with('/custom/output', True)
