"""
Tests for core modules: external_cli_handler, task_dispatcher, freq_config_manager

Target coverage: > 70% for each module
"""

import pytest
import sys
import os
import json
import tempfile
import logging
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from dataclasses import dataclass
from types import SimpleNamespace

# Add src to path
_SRC_DIR = Path(__file__).parent.parent.parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))


# =============================================================================
# Tests for freq_config_manager module
# =============================================================================

class TestFreqConfigManager:
    """Test FreqConfigManager class"""

    def test_init(self):
        """Test FreqConfigManager initialization"""
        from core.freq_config_manager import FreqConfigManager
        manager = FreqConfigManager()
        assert manager.logger is not None

    def test_get_legacy_range(self):
        """Test legacy range(6, n-4) logic"""
        from core.freq_config_manager import FreqConfigManager
        manager = FreqConfigManager()

        # Test with typical frequency count (e.g., 100)
        result = manager._get_legacy_range(100)
        assert list(result) == list(range(6, 96))

        # Test minimum case
        result = manager._get_legacy_range(10)
        assert list(result) == list(range(6, 6))  # Empty range

        # Test with small n
        result = manager._get_legacy_range(8)
        assert list(result) == list(range(6, 4))  # Empty range

    def test_get_legacy_range_edge_cases(self):
        """Test legacy range edge cases"""
        from core.freq_config_manager import FreqConfigManager
        manager = FreqConfigManager()

        # n < 6: start >= end, should return empty
        for n in [1, 2, 3, 4, 5]:
            result = manager._get_legacy_range(n)
            assert list(result) == []

        # n = 6: range(6, 2) = empty
        result = manager._get_legacy_range(6)
        assert list(result) == []

        # n = 7: range(6, 3) = empty
        result = manager._get_legacy_range(7)
        assert list(result) == []

        # n = 11: range(6, 7) = [6]
        result = manager._get_legacy_range(11)
        assert list(result) == [6]

    def test_calculate_from_hz_range(self):
        """Test Hz range to index calculation"""
        from core.freq_config_manager import FreqConfigManager
        import numpy as np
        manager = FreqConfigManager()

        # Create test frequency list
        freq_list = [0.1, 0.5, 1.0, 5.0, 10.0, 50.0, 100.0, 500.0, 1000.0]

        # Test valid range [1.0, 100.0]
        # valid_indices = [2, 3, 4, 5, 6] for freqs 1.0, 5.0, 10.0, 50.0, 100.0
        # start_idx = 2, end_idx = 6 + 1 = 7
        result = manager._calculate_from_hz_range([1.0, 100.0], freq_list)
        result_list = list(result)
        assert result_list == [2, 3, 4, 5, 6]  # indices for 1.0 to 100.0 Hz

        # Test range [0.1, 0.1] - only 0.1 Hz matches at index 0
        # valid_indices = [0]
        # start_idx = 0, end_idx = 0 + 1 = 1
        result = manager._calculate_from_hz_range([0.1, 0.1], freq_list)
        result_list = list(result)
        assert result_list == [0]  # only index 0 (0.1 Hz)

    def test_calculate_from_hz_range_no_match(self):
        """Test Hz range with no matching frequencies falls back to legacy"""
        from core.freq_config_manager import FreqConfigManager
        manager = FreqConfigManager()

        freq_list = [1.0, 2.0, 3.0, 4.0, 5.0]

        # Range outside data should fall back to legacy
        result = manager._calculate_from_hz_range([100.0, 200.0], freq_list)
        expected = manager._get_legacy_range(len(freq_list))
        assert list(result) == list(expected)

    def test_calculate_from_hz_range_partial_match(self):
        """Test partial frequency match"""
        from core.freq_config_manager import FreqConfigManager
        manager = FreqConfigManager()

        freq_list = [0.1, 0.5, 1.0, 5.0, 10.0, 50.0, 100.0]

        # Range that partially overlaps - indices 3, 4 (5.0, 10.0)
        result = manager._calculate_from_hz_range([2.0, 20.0], freq_list)
        result_list = list(result)
        assert 3 in result_list  # 5.0 Hz
        assert 4 in result_list  # 10.0 Hz
        # 50.0 Hz (index 5) is outside 2-20 range

    def test_get_freq_indices_with_hz_config(self):
        """Test get_freq_indices with Hz configuration"""
        from core.freq_config_manager import FreqConfigManager
        manager = FreqConfigManager()

        freq_list = [0.1, 0.5, 1.0, 5.0, 10.0, 50.0, 100.0]

        # Create mock config with freq_range_hz
        mock_config = MagicMock()
        mock_config.dataset = {'freq_range_hz': [1.0, 50.0]}

        result = manager.get_freq_indices(mock_config, freq_list, len(freq_list))
        expected = range(2, 6)  # indices for 1.0 to 50.0 Hz
        assert list(result) == list(expected)

    def test_get_freq_indices_without_hz_config(self):
        """Test get_freq_indices without Hz configuration (legacy mode)"""
        from core.freq_config_manager import FreqConfigManager
        manager = FreqConfigManager()

        freq_list = [0.1, 0.5, 1.0, 5.0, 10.0, 50.0, 100.0]

        # Create mock config without freq_range_hz
        mock_config = MagicMock()
        mock_config.dataset = {}

        result = manager.get_freq_indices(mock_config, freq_list, 100)
        expected = range(6, 96)
        assert list(result) == list(expected)

    def test_get_freq_indices_empty_dataset(self):
        """Test get_freq_indices with empty dataset config"""
        from core.freq_config_manager import FreqConfigManager
        manager = FreqConfigManager()

        freq_list = [1.0, 2.0, 3.0]

        mock_config = MagicMock()
        mock_config.dataset = {}

        result = manager.get_freq_indices(mock_config, freq_list, len(freq_list))
        # Should use legacy range since no Hz range is configured
        assert list(result) == list(range(6, -1))  # empty for small n

    def test_singleton_instance(self):
        """Test freq_config_manager singleton"""
        from core.freq_config_manager import freq_config_manager, FreqConfigManager
        assert freq_config_manager is not None
        assert isinstance(freq_config_manager, FreqConfigManager)


# =============================================================================
# Tests for task_dispatcher module
# =============================================================================

class TestTaskDispatcher:
    """Test task_dispatcher module functions"""

    def test_get_arg_value_from_object(self):
        """Test _get_arg_value with object having attribute"""
        from core.task_dispatcher import _get_arg_value

        class MockArgs:
            force_mode = True
            quick_inference = False

        args = MockArgs()
        result = _get_arg_value(args, 'force_mode', False)
        assert result is True

        result = _get_arg_value(args, 'nonexistent', 'default')
        assert result == 'default'

    def test_get_arg_value_from_dict(self):
        """Test _get_arg_value with dict"""
        from core.task_dispatcher import _get_arg_value

        args = {'force_mode': True, 'key': 'value'}
        result = _get_arg_value(args, 'force_mode', False)
        assert result is True

        result = _get_arg_value(args, 'missing', 'default')
        assert result == 'default'

    def test_get_arg_value_default(self):
        """Test _get_arg_value with non-dict, non-object"""
        from core.task_dispatcher import _get_arg_value

        result = _get_arg_value(None, 'key', 'default')
        assert result == 'default'

        result = _get_arg_value(123, 'key', 'default')
        assert result == 'default'

    def test_dispatch_task_unknown_type(self, caplog):
        """Test dispatch_task with unknown task type"""
        from core.task_dispatcher import dispatch_task

        with caplog.at_level(logging.ERROR):
            dispatch_task('unknown_type', ['project1'], {})

        assert '未知的任务类型' in caplog.text or 'unknown_type' in caplog.text

    def test_dispatch_task_unknown_type_continues(self, caplog):
        """Test dispatch_task continues after unknown type error"""
        from core.task_dispatcher import dispatch_task

        # Should not raise exception, just log error
        with caplog.at_level(logging.ERROR):
            dispatch_task('unknown_type', ['project1'], {})

        # Function should complete without raising

    @patch('core.task_dispatcher._handle_train_task')
    def test_dispatch_task_train(self, mock_train):
        """Test dispatch_task with train task type"""
        from core.task_dispatcher import dispatch_task

        dispatch_task('train', ['project1'], {})
        mock_train.assert_called_once_with('projects/project1')

    @patch('core.task_dispatcher._handle_evaluate_task')
    def test_dispatch_task_evaluate(self, mock_evaluate):
        """Test dispatch_task with evaluate task type"""
        from core.task_dispatcher import dispatch_task

        mock_args = MagicMock()
        mock_args.freq_compare_sources = None  # Ensure this is None to skip freq compare
        dispatch_task('evaluate', ['project1'], mock_args)
        mock_evaluate.assert_called_once()

    @patch('core.task_dispatcher._handle_clean_task')
    def test_dispatch_task_clean(self, mock_clean):
        """Test dispatch_task with clean task type"""
        from core.task_dispatcher import dispatch_task

        dispatch_task('clean', ['project1'], {})
        mock_clean.assert_called_once()

    @patch('core.task_dispatcher._handle_model_info_task')
    def test_dispatch_task_model_info(self, mock_model_info):
        """Test dispatch_task with model_info task type"""
        from core.task_dispatcher import dispatch_task

        dispatch_task('model_info', ['project1'], {})
        mock_model_info.assert_called_once()

    @patch('core.task_dispatcher._handle_lut_task')
    def test_dispatch_task_lut(self, mock_lut):
        """Test dispatch_task with lut task type"""
        from core.task_dispatcher import dispatch_task

        dispatch_task('lut', ['project1'], {})
        mock_lut.assert_called_once()

    @patch('core.task_dispatcher.ProjectManager')
    def test_dispatch_task_inference(self, mock_pm):
        """Test dispatch_task with inference task type"""
        from core.task_dispatcher import dispatch_task

        mock_instance = MagicMock()
        mock_pm.return_value = mock_instance

        mock_args = MagicMock()
        mock_args.freq_compare_sources = None
        mock_args.force_mode = False
        mock_args.quick_inference = False
        mock_args.layers_param = None

        dispatch_task('inference', ['project1'], mock_args)
        mock_instance.run_inference.assert_called_once()

    @patch('core.task_dispatcher.ProjectManager')
    def test_dispatch_task_analyze(self, mock_pm):
        """Test dispatch_task with analyze task type"""
        from core.task_dispatcher import dispatch_task

        mock_instance = MagicMock()
        mock_pm.return_value = mock_instance

        mock_args = MagicMock()
        mock_args.freq_compare_sources = None
        mock_args.force_mode = False
        mock_args.bias_method = 'auto'
        mock_args.bias_params = {}

        dispatch_task('analyze', ['project1'], mock_args)
        mock_instance.analyze_errors.assert_called_once()

    @patch('core.task_dispatcher.ProjectManager')
    def test_dispatch_task_wave(self, mock_pm):
        """Test dispatch_task with wave task type"""
        from core.task_dispatcher import dispatch_task

        mock_instance = MagicMock()
        mock_instance.generate_wave_data.return_value = {
            'dataset_type': 'MET',
            'output_folder': 'data',
            'files': {}
        }
        mock_pm.return_value = mock_instance

        mock_args = MagicMock()
        mock_args.freq_compare_sources = None
        mock_args.force_mode = False

        dispatch_task('wave', ['project1'], mock_args)
        mock_instance.generate_wave_data.assert_called_once()

    @patch('core.task_dispatcher._handle_freq_response_compare_task')
    def test_dispatch_task_with_freq_compare_sources(self, mock_freq_compare):
        """Test dispatch_task when freq_compare_sources is provided"""
        from core.task_dispatcher import dispatch_task

        mock_args = MagicMock()
        mock_args.freq_compare_sources = ['project1']

        dispatch_task('train', ['project1'], mock_args)
        mock_freq_compare.assert_called_once()

    @patch('core.task_dispatcher._handle_standardize_resistance_task')
    def test_dispatch_task_standardize_resistance(self, mock_standardize):
        """Test dispatch_task with standardize_resistance task type"""
        from core.task_dispatcher import dispatch_task

        mock_args = MagicMock()
        mock_args.freq_compare_sources = None
        mock_args.series = ['E96']
        mock_args.input_csv = None
        mock_args.output_dir = None

        dispatch_task('standardize_resistance', ['project1'], mock_args)
        mock_standardize.assert_called_once()

    @patch('core.task_dispatcher._handle_waveform_vis_task')
    def test_dispatch_task_waveform_vis(self, mock_waveform_vis):
        """Test dispatch_task with waveform_vis task type"""
        from core.task_dispatcher import dispatch_task

        mock_args = MagicMock()
        mock_args.freq_compare_sources = None
        dispatch_task('waveform_vis', ['project1'], mock_args)
        mock_waveform_vis.assert_called_once()


class TestHandleFunctions:
    """Test individual task handler functions"""

    @patch('core.task_dispatcher.met_comp_with_project')
    @patch('core.task_dispatcher._invalidate_downstream_artifacts_after_training')
    @patch('core.task_dispatcher._handle_evaluate_task')
    def test_handle_train_task(self, mock_evaluate, mock_invalidate, mock_met):
        """Test _handle_train_task"""
        from core.task_dispatcher import _handle_train_task

        _handle_train_task('projects/test_project')
        mock_met.assert_called_once_with('projects/test_project')
        mock_invalidate.assert_called_once_with('projects/test_project')
        mock_evaluate.assert_called_once_with('projects/test_project', ['projects/test_project'], {})

    @patch('core.task_dispatcher.ProjectManager')
    @patch('core.task_dispatcher._refresh_metrics_summary')
    def test_handle_evaluate_task(self, mock_refresh, mock_pm):
        """Test _handle_evaluate_task"""
        from core.task_dispatcher import _handle_evaluate_task

        mock_instance = MagicMock()
        mock_pm.return_value = mock_instance

        _handle_evaluate_task('projects/project1', ['project1'], MagicMock())
        mock_instance.evaluate.assert_called_once()
        mock_refresh.assert_called_once_with(mock_instance, 'evaluation')

    @patch('core.task_dispatcher.ProjectManager')
    @patch('core.task_dispatcher._refresh_metrics_summary')
    def test_handle_model_info_task(self, mock_refresh, mock_pm):
        """Test _handle_model_info_task"""
        from core.task_dispatcher import _handle_model_info_task

        mock_instance = MagicMock()
        mock_pm.return_value = mock_instance

        _handle_model_info_task('projects/project1', 'project1')
        mock_instance.model_info.assert_called_once()
        mock_refresh.assert_called_once_with(mock_instance, 'model info export')

    @patch('core.task_dispatcher.ProjectManager')
    def test_handle_lut_task(self, mock_pm):
        """Test _handle_lut_task"""
        from core.task_dispatcher import _handle_lut_task

        mock_instance = MagicMock()
        mock_pm.return_value = mock_instance

        _handle_lut_task('projects/project1')
        mock_instance.lut.assert_called_once()


# =============================================================================
# Tests for external_cli_handler module
# =============================================================================

class TestExternalCLIHandler:
    """Test external_cli_handler module functions"""

    @pytest.fixture
    def mock_ep_path_string(self):
        """Create a mock ExternalPath with string attributes for JSON serialization"""
        mock_path = MagicMock()
        mock_path.project_name = 'TestProject'
        mock_path.task_type = 'freq-response-compare'
        mock_path.task_name = 'test-task'
        mock_path.config_path = Path('/tmp/test/config.json')
        mock_path.output_path = Path('/tmp/test/data')
        return mock_path

    def test_create_freq_response_template(self):
        """Test _create_freq_response_template function"""
        from core.external_cli_handler import _create_freq_response_template

        # Create a simple object with required attributes
        class MockPath:
            project_name = 'TestProject'
            task_type = 'freq-response-compare'

        mock_ep_path = MockPath()

        result = _create_freq_response_template(mock_ep_path)

        assert result['task_info']['task_type'] == 'freq-response-compare'
        assert result['visualization_config']['layout'] == 'side_by_side'
        assert result['visualization_config']['freq_range'] == [10, 200]
        assert 'TestProject' in result['visualization_config']['title']
        assert len(result['data_sources']) == 2

    def test_create_wnet5_circuit_validation_template(self):
        """Test _create_wnet5_circuit_validation_template function"""
        from core.external_cli_handler import _create_wnet5_circuit_validation_template

        class MockPath:
            project_name = 'WNET5Test'

        result = _create_wnet5_circuit_validation_template(MockPath())

        assert result['task_info']['task_type'] == 'wnet5-circuit-validation'
        assert result['model_project_name'] == 'WNET5Test'
        assert result['frequency_range']['start_freq'] == 0.1
        assert result['frequency_range']['stop_freq'] == 1000

    def test_create_bias_visualization_template(self):
        """Test _create_bias_visualization_template function"""
        from core.external_cli_handler import _create_bias_visualization_template

        class MockPath:
            project_name = 'BiasTest'

        result = _create_bias_visualization_template(MockPath())

        assert result['task_info']['task_type'] == 'bias-visualization'
        assert 'BiasTest' in result['visualization_config']['title']
        assert result['visualization_config']['output_format'] == 'png'

    def test_create_waveform_analysis_template(self):
        """Test _create_waveform_analysis_template function"""
        from core.external_cli_handler import _create_waveform_analysis_template

        class MockPath:
            project_name = 'WaveTest'

        result = _create_waveform_analysis_template(MockPath())

        assert result['task_info']['task_type'] == 'waveform-analysis'
        assert 'WaveTest' in result['visualization_config']['title']

    def test_create_generic_template(self):
        """Test _create_generic_template function"""
        from core.external_cli_handler import _create_generic_template

        class MockPath:
            project_name = 'GenericProject'
            task_type = 'custom-task'
            task_name = 'custom-name'

        result = _create_generic_template(MockPath())

        assert result['task_info']['task_type'] == 'custom-task'
        assert result['task_info']['task_name'] == 'custom-name'
        assert result['task_info']['version'] == '1.0'
        assert result['visualization_config']['method'] == 'custom-task'

    def test_create_freq_response_compensator_template(self):
        """Test _create_freq_response_compensator_template function"""
        from core.external_cli_handler import _create_freq_response_compensator_template

        class MockPath:
            project_name = 'CompensatorTest'

        result = _create_freq_response_compensator_template(MockPath())

        assert result['task_info']['task_type'] == 'freq-response-compensator'
        assert result['project_name'] == 'CompensatorTest'
        assert result['visualization_config']['log_scale'] is True

    def test_calculate_config_hash(self):
        """Test _calculate_config_hash function"""
        from core.external_cli_handler import _calculate_config_hash

        config = {'key': 'value', 'number': 42}
        hash1 = _calculate_config_hash(config)
        hash2 = _calculate_config_hash(config)

        # Same input should produce same hash
        assert hash1 == hash2
        assert len(hash1) == 32  # MD5 hex digest length

    def test_calculate_config_hash_different(self):
        """Test _calculate_config_hash produces different hashes for different inputs"""
        from core.external_cli_handler import _calculate_config_hash

        config1 = {'key': 'value1'}
        config2 = {'key': 'value2'}

        hash1 = _calculate_config_hash(config1)
        hash2 = _calculate_config_hash(config2)

        assert hash1 != hash2

    def test_load_config(self, temp_dir):
        """Test _load_config function"""
        from core.external_cli_handler import _load_config

        config_data = {'test_key': 'test_value', 'number': 123}
        config_path = temp_dir / 'config.json'

        with open(config_path, 'w') as f:
            json.dump(config_data, f)

        result = _load_config(config_path)

        assert result['test_key'] == 'test_value'
        assert result['number'] == 123

    @patch('core.config_validator.validate_visualization_config_data')
    def test_validate_config_success(self, mock_validate):
        """Test _validate_config with valid config"""
        from core.external_cli_handler import _validate_config

        mock_validate.return_value = {'validated': True}

        config = {'task_info': {'task_type': 'test'}}
        result = _validate_config(config, 'test-task')

        assert result['validated'] is True
        mock_validate.assert_called_once_with(config, 'test-task')

    @patch('core.config_validator.validate_visualization_config_data')
    def test_validate_config_validation_error(self, mock_validate):
        """Test _validate_config with validation error"""
        from core.external_cli_handler import _validate_config
        from core.config_validator import ConfigValidationError

        mock_validate.side_effect = ConfigValidationError('Invalid config')

        config = {'task_info': {'task_type': 'test'}}

        with pytest.raises(ValueError, match='配置验证失败'):
            _validate_config(config, 'test-task')

    @patch('core.config_validator.validate_visualization_config_data')
    def test_validate_config_general_error(self, mock_validate):
        """Test _validate_config with general error"""
        from core.external_cli_handler import _validate_config

        mock_validate.side_effect = Exception('Unexpected error')

        config = {'task_info': {'task_type': 'test'}}

        with pytest.raises(ValueError, match='配置验证过程出错'):
            _validate_config(config, 'test-task')

    @patch('core.external_cli_handler._load_config')
    @patch('core.external_cli_handler._validate_config')
    @patch('core.external_cli_handler._execute_freq_response_task')
    def test_execute_task_freq_response(self, mock_exec, mock_validate, mock_load):
        """Test _execute_task with freq-response-compare task type"""
        from core.external_cli_handler import _execute_task
        from core.external_path_parser import ExternalPath

        mock_path = MagicMock()
        mock_path.task_type = 'freq-response-compare'
        mock_path.config_path = Path('/test/config.json')

        mock_config = {'task_info': {'task_type': 'freq-response-compare'}}
        mock_load.return_value = mock_config
        mock_validate.return_value = mock_config
        mock_exec.return_value = True

        result = _execute_task(mock_path)

        assert result is True
        mock_exec.assert_called_once()

    def test_execute_task_unsupported_type(self):
        """Test _execute_task with unsupported task type"""
        from core.external_cli_handler import _execute_task

        mock_path = MagicMock()
        mock_path.task_type = 'unsupported-type'
        mock_path.config_path = Path('/test/config.json')

        result = _execute_task(mock_path)

        assert result is False

    @patch('core.external_cli_handler._load_config')
    @patch('core.external_cli_handler._validate_config')
    def test_execute_task_load_error(self, mock_validate, mock_load):
        """Test _execute_task when load_config raises exception"""
        from core.external_cli_handler import _execute_task

        mock_path = MagicMock()
        mock_path.task_type = 'test-type'
        mock_path.config_path = Path('/test/config.json')

        mock_load.side_effect = Exception('File not found')

        result = _execute_task(mock_path)

        assert result is False

    @patch('core.external_cli_handler._load_config')
    @patch('core.external_cli_handler._validate_config')
    def test_execute_task_validate_error(self, mock_validate, mock_load):
        """Test _execute_task when validate_config raises exception"""
        from core.external_cli_handler import _execute_task

        mock_path = MagicMock()
        mock_path.task_type = 'test-type'
        mock_path.config_path = Path('/test/config.json')

        mock_load.return_value = {'task_info': {}}
        mock_validate.side_effect = ValueError('Validation failed')

        result = _execute_task(mock_path)

        assert result is False

    def test_execute_external_task_auto_config_not_exists(self, temp_dir, caplog):
        """Test execute_external_task_auto when config doesn't exist"""
        from core.external_cli_handler import execute_external_task_auto

        class MockPath:
            task_name = 'test-task'
            config_path = temp_dir / 'nonexistent' / 'config.json'
            output_path = temp_dir / 'output'
            project_name = 'TestProject'
            task_type = 'freq-response-compare'

        with pytest.raises(SystemExit):
            with caplog.at_level(logging.INFO):
                execute_external_task_auto(MockPath())

        assert '配置文件不存在' in caplog.text
        assert 'ep create' in caplog.text

    def test_create_external_template_creates_directories(self, temp_dir):
        """Test create_external_template creates necessary directories"""
        from core.external_cli_handler import create_external_template

        class MockPath:
            task_type = 'freq-response-compare'
            project_name = 'TestProject'
            config_path = temp_dir / 'config.json'
            output_path = temp_dir / 'data'

        create_external_template(MockPath())

        assert MockPath().config_path.parent.exists()
        assert MockPath().output_path.exists()

    def test_show_ep_help(self, capsys):
        """Test _show_ep_help function"""
        from core.external_cli_handler import _show_ep_help

        _show_ep_help()
        captured = capsys.readouterr()

        assert 'ep 命令使用说明' in captured.out
        assert 'freq-response-compare' in captured.out

    def test_save_task_metadata(self, temp_dir):
        """Test _save_task_metadata function"""
        from core.external_cli_handler import _save_task_metadata

        mock_path = MagicMock()
        mock_path.output_path = temp_dir

        config = {'task_info': {'task_type': 'test'}}

        _save_task_metadata(mock_path, config, '/test/output.png')

        metadata_file = temp_dir / 'task_metadata.json'
        assert metadata_file.exists()

        with open(metadata_file) as f:
            metadata = json.load(f)

        assert 'execution_time' in metadata
        assert metadata['config_hash'] is not None
        assert '/test/output.png' in metadata['output_files']

    @patch('core.external_cli_handler._execute_task')
    def test_execute_external_task_auto_config_exists(self, mock_exec, temp_dir):
        """Test execute_external_task_auto when config exists"""
        from core.external_cli_handler import execute_external_task_auto

        class MockPath:
            task_name = 'test-task'
            config_path = temp_dir / 'config.json'
            output_path = temp_dir / 'output'
            project_name = 'TestProject'
            task_type = 'freq-response-compare'

        # Create config file
        config_path = temp_dir / 'config.json'
        with open(config_path, 'w') as f:
            json.dump({'task_info': {'task_type': 'test'}}, f)

        mock_exec.return_value = True

        execute_external_task_auto(MockPath())

        mock_exec.assert_called_once()

    @patch('core.external_cli_handler._load_config')
    @patch('core.external_cli_handler._validate_config')
    @patch('core.external_cli_handler._execute_wnet5_circuit_validation_task')
    def test_execute_task_wnet5_circuit_validation(self, mock_exec, mock_validate, mock_load):
        """Test _execute_task with wnet5-circuit-validation task type"""
        from core.external_cli_handler import _execute_task

        mock_path = MagicMock()
        mock_path.task_type = 'wnet5-circuit-validation'
        mock_path.config_path = Path('/test/config.json')

        mock_config = {'task_info': {'task_type': 'wnet5-circuit-validation'}}
        mock_load.return_value = mock_config
        mock_validate.return_value = mock_config
        mock_exec.return_value = True

        result = _execute_task(mock_path)

        assert result is True
        mock_exec.assert_called_once()

    @patch('core.external_cli_handler._load_config')
    @patch('core.external_cli_handler._validate_config')
    @patch('core.external_cli_handler._execute_bias_visualization_task')
    def test_execute_task_bias_visualization(self, mock_exec, mock_validate, mock_load):
        """Test _execute_task with bias-visualization task type"""
        from core.external_cli_handler import _execute_task

        mock_path = MagicMock()
        mock_path.task_type = 'bias-visualization'
        mock_path.config_path = Path('/test/config.json')

        mock_config = {'task_info': {'task_type': 'bias-visualization'}}
        mock_load.return_value = mock_config
        mock_validate.return_value = mock_config
        mock_exec.return_value = False  # Not implemented

        result = _execute_task(mock_path)

        assert result is False

    @patch('core.external_cli_handler._load_config')
    @patch('core.external_cli_handler._validate_config')
    @patch('core.external_cli_handler._execute_waveform_analysis_task')
    def test_execute_task_waveform_analysis(self, mock_exec, mock_validate, mock_load):
        """Test _execute_task with waveform-analysis task type"""
        from core.external_cli_handler import _execute_task

        mock_path = MagicMock()
        mock_path.task_type = 'waveform-analysis'
        mock_path.config_path = Path('/test/config.json')

        mock_config = {'task_info': {'task_type': 'waveform-analysis'}}
        mock_load.return_value = mock_config
        mock_validate.return_value = mock_config
        mock_exec.return_value = False  # Not implemented

        result = _execute_task(mock_path)

        assert result is False


# =============================================================================
# Tests for external_path_parser integration
# =============================================================================

class TestExternalPathParser:
    """Test ExternalPathParser for integration with external_cli_handler"""

    def test_external_path_dataclass(self):
        """Test ExternalPath dataclass properties"""
        from core.external_path_parser import ExternalPath

        path = ExternalPath(
            project_name='TestProject',
            task_type='freq-response-compare',
            task_name='TestTask',
            full_path=Path('/test/full'),
            config_path=Path('/test/config.json'),
            output_path=Path('/test/output')
        )

        # external_dir includes 'external' subdirectory
        assert path.external_dir == Path('projects/TestProject/external')
        assert path.task_dir == Path('projects/TestProject/external/freq-response-compare/TestTask')

    def test_external_path_parser_init(self):
        """Test ExternalPathParser initialization"""
        from core.external_path_parser import ExternalPathParser

        parser = ExternalPathParser()
        assert parser.base_dir == Path.cwd()

        custom_dir = Path('/custom')
        parser2 = ExternalPathParser(custom_dir)
        assert parser2.base_dir == custom_dir

    def test_supported_task_types(self):
        """Test supported task types list"""
        from core.external_path_parser import ExternalPathParser

        parser = ExternalPathParser()

        expected_types = [
            'freq-response-compare',
            'freq-response-compensator',
            'bias-visualization',
            'waveform-analysis',
            'wnet5-circuit-validation',
            'qemu-c-inference',
            'data-analysis',
            'model-export',
            'performance-benchmark',
            'ablation-study',
            'compare'
        ]

        assert parser.SUPPORTED_TASK_TYPES == expected_types

    def test_parse_simple_path(self):
        """Test parsing simple path format"""
        from core.external_path_parser import ExternalPathParser

        parser = ExternalPathParser()
        result = parser.parse('ProjectName/task-name')

        assert result.project_name == 'ProjectName'
        assert result.task_name == 'task-name'
        # Should auto-detect task type based on task name

    def test_parse_full_path(self):
        """Test parsing full path format"""
        from core.external_path_parser import ExternalPathParser

        parser = ExternalPathParser()
        result = parser.parse('projects/TestProject/freq-response-compare/TaskName')

        assert result.project_name == 'TestProject'
        assert result.task_type == 'freq-response-compare'
        assert result.task_name == 'TaskName'

    def test_parse_absolute_path(self):
        """Test parsing absolute path"""
        from core.external_path_parser import ExternalPathParser

        parser = ExternalPathParser()
        # Path format: C:/work/project/freq-response-compare/task
        # When task_type is found at index 2, project_name = parts[1] = 'project'
        abs_path = 'C:/work/project/freq-response-compare/task'
        result = parser.parse(abs_path)

        assert result.task_type == 'freq-response-compare'
        assert result.task_name == 'task'
        # project_name is determined by the path structure

    def test_parse_ex_projects_inference_path(self):
        """Test parsing ex_projects/inference/task_type/task_name path."""
        from core.external_path_parser import ExternalPathParser

        parser = ExternalPathParser()
        result = parser.parse('ex_projects/inference/qemu-c-inference/lstm_u16_base')

        assert result.project_name == 'lstm_u16_base'
        assert result.task_type == 'qemu-c-inference'
        assert result.task_name == 'lstm_u16_base'
        assert result.config_path.name == 'config.json'

    def test_validate_project_name(self):
        """Test project name validation"""
        from core.external_path_parser import validate_project_name

        assert validate_project_name('ValidProject123') is True
        assert validate_project_name('project-name') is True
        assert validate_project_name('') is False
        assert validate_project_name('project name') is False  # Space not allowed

    def test_validate_task_name(self):
        """Test task name validation"""
        from core.external_path_parser import validate_task_name

        assert validate_task_name('ValidTask123') is True
        assert validate_task_name('task-name') is True
        assert validate_task_name('') is False
        assert validate_task_name('task name') is False  # Space not allowed

    def test_detect_task_type_frequency(self):
        """Test automatic task type detection for frequency"""
        from core.external_path_parser import ExternalPathParser

        parser = ExternalPathParser()

        assert parser._detect_task_type('proj', 'frequency-comparison') == 'freq-response-compare'
        assert parser._detect_task_type('proj', 'freq-baseline') == 'freq-response-compare'
        assert parser._detect_task_type('proj', 'response-compare') == 'freq-response-compare'

    def test_detect_task_type_bias(self):
        """Test automatic task type detection for bias"""
        from core.external_path_parser import ExternalPathParser

        parser = ExternalPathParser()

        assert parser._detect_task_type('proj', 'bias-analysis') == 'bias-visualization'
        assert parser._detect_task_type('proj', 'offset-check') == 'bias-visualization'

    def test_detect_task_type_waveform(self):
        """Test automatic task type detection for waveform"""
        from core.external_path_parser import ExternalPathParser

        parser = ExternalPathParser()

        assert parser._detect_task_type('proj', 'waveform-test') == 'waveform-analysis'
        assert parser._detect_task_type('proj', 'signal-processing') == 'waveform-analysis'
