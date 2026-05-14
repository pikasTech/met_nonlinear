"""
Tests for core/external_cli_handler module

重点覆盖：
- _execute_*_task 函数（需要 mock visualization 等外部模块）
"""

import pytest
import sys
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, mock_open
from types import SimpleNamespace

# Add src to path
_SRC_DIR = Path(__file__).parent.parent.parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))


class TestExternalCLIHandlerStructure:
    """Test external_cli_handler module structure"""

    def test_module_import(self):
        """Test module can be imported"""
        from core.external_cli_handler import (
            handle_ep_command,
            execute_external_task_auto,
            create_external_template_command,
            create_external_template,
            _execute_task,
            _load_config,
            _validate_config,
            _execute_freq_response_task,
            _execute_freq_response_compensator_task,
            _execute_bias_visualization_task,
            _execute_waveform_analysis_task,
            _execute_wnet5_circuit_validation_task,
            _create_freq_response_template,
            _create_wnet5_circuit_validation_template,
            _create_bias_visualization_template,
            _create_waveform_analysis_template,
            _create_generic_template,
            _create_freq_response_compensator_template,
            _save_task_metadata,
            _calculate_config_hash,
            _show_ep_help
        )
        # All functions should be callable
        assert callable(handle_ep_command)
        assert callable(execute_external_task_auto)
        assert callable(create_external_template_command)
        assert callable(create_external_template)


class TestCreateExternalTemplate:
    """Test create_external_template function"""

    @pytest.fixture
    def mock_ep_path(self, tmp_path):
        """Create a mock ExternalPath object"""
        from core.external_path_parser import ExternalPath

        ep = ExternalPath(
            project_name="test_project",
            task_type="freq-response-compare",
            task_name="test_task",
            full_path=tmp_path / "test_task",
            config_path=tmp_path / "test_task" / "config.json",
            output_path=tmp_path / "test_task" / "data"
        )
        return ep

    def test_create_freq_response_template(self, mock_ep_path):
        """Test creating frequency response template"""
        from core.external_cli_handler import _create_freq_response_template

        template = _create_freq_response_template(mock_ep_path)

        assert template["task_info"]["task_type"] == "freq-response-compare"
        assert template["visualization_config"]["layout"] == "side_by_side"
        assert template["visualization_config"]["freq_range"] == [10, 200]
        assert len(template["data_sources"]) == 2
        assert template["data_sources"][0]["label"] == "补偿前"
        assert template["data_sources"][1]["label"] == "补偿后"

    def test_create_wnet5_circuit_validation_template(self, mock_ep_path):
        """Test creating WNET5 circuit validation template"""
        from core.external_cli_handler import _create_wnet5_circuit_validation_template

        mock_ep_path.task_type = "wnet5-circuit-validation"
        template = _create_wnet5_circuit_validation_template(mock_ep_path)

        assert template["task_info"]["task_type"] == "wnet5-circuit-validation"
        assert template["model_project_name"] == "test_project"
        assert template["frequency_range"]["start_freq"] == 0.1
        assert template["frequency_range"]["stop_freq"] == 1000

    def test_create_bias_visualization_template(self, mock_ep_path):
        """Test creating bias visualization template"""
        from core.external_cli_handler import _create_bias_visualization_template

        mock_ep_path.task_type = "bias-visualization"
        template = _create_bias_visualization_template(mock_ep_path)

        assert template["task_info"]["task_type"] == "bias-visualization"
        assert template["visualization_config"]["output_format"] == "png"
        assert len(template["data_sources"]) == 1

    def test_create_waveform_analysis_template(self, mock_ep_path):
        """Test creating waveform analysis template"""
        from core.external_cli_handler import _create_waveform_analysis_template

        mock_ep_path.task_type = "waveform-analysis"
        template = _create_waveform_analysis_template(mock_ep_path)

        assert template["task_info"]["task_type"] == "waveform-analysis"
        assert template["visualization_config"]["figsize"] == [14, 8]

    def test_create_freq_response_compensator_template(self, mock_ep_path):
        """Test creating frequency response compensator template"""
        from core.external_cli_handler import _create_freq_response_compensator_template

        mock_ep_path.task_type = "freq-response-compensator"
        template = _create_freq_response_compensator_template(mock_ep_path)

        assert template["task_info"]["task_type"] == "freq-response-compensator"
        assert template["visualization_config"]["log_scale"] is True

    def test_create_generic_template(self, mock_ep_path):
        """Test creating generic template for unknown task type"""
        from core.external_cli_handler import _create_generic_template

        mock_ep_path.task_type = "unknown-type"
        template = _create_generic_template(mock_ep_path)

        assert template["task_info"]["task_type"] == "unknown-type"
        assert template["task_info"]["version"] == "1.0"
        assert template["visualization_config"]["method"] == "unknown-type"

    def test_create_qemu_c_inference_template_contains_keil_config(self, mock_ep_path):
        """Test qemu-c-inference template includes keil bench defaults."""
        from core.external_cli_handler import _create_qemu_c_inference_template

        mock_ep_path.task_type = "qemu-c-inference"
        template = _create_qemu_c_inference_template(mock_ep_path)

        assert template["task_info"]["task_type"] == "qemu-c-inference"
        assert template["keil_config"]["action"] == "build-program-capture"
        assert template["keil_config"]["serial_port"] == "COM8"
        assert template["keil_config"]["probe_uid"] == "205536951525"

    def test_create_external_template_writes_file(self, mock_ep_path, tmp_path):
        """Test that create_external_template writes config file"""
        from core.external_cli_handler import create_external_template

        mock_ep_path.config_path.parent.mkdir(parents=True, exist_ok=True)
        mock_ep_path.output_path.mkdir(parents=True, exist_ok=True)

        create_external_template(mock_ep_path)

        assert mock_ep_path.config_path.exists()
        with open(mock_ep_path.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        assert "task_info" in config
        assert "visualization_config" in config


class TestExecuteTask:
    """Test _execute_task function"""

    @pytest.fixture
    def mock_ep_path(self, tmp_path):
        """Create a mock ExternalPath object"""
        from core.external_path_parser import ExternalPath

        ep = ExternalPath(
            project_name="test_project",
            task_type="freq-response-compare",
            task_name="test_task",
            full_path=tmp_path / "test_task",
            config_path=tmp_path / "test_task" / "config.json",
            output_path=tmp_path / "test_task" / "data"
        )
        ep.config_path.parent.mkdir(parents=True, exist_ok=True)
        ep.output_path.mkdir(parents=True, exist_ok=True)
        return ep

    @pytest.fixture
    def valid_config(self, mock_ep_path):
        """Create a valid config dictionary"""
        return {
            "task_info": {"task_type": mock_ep_path.task_type},
            "visualization_config": {
                "layout": "side_by_side",
                "freq_range": [10, 200],
                "dpi": 300,
                "figsize": [12, 8],
                "title": "Test"
            },
            "data_sources": [
                {"project": "test_project", "state": "origin", "label": "Before"},
                {"project": "test_project", "state": "compensation", "label": "After", "split_magnitudes": True}
            ]
        }

    def test_execute_task_unsupported_type(self, mock_ep_path):
        """Test executing unsupported task type returns False"""
        from core.external_cli_handler import _execute_task

        mock_ep_path.task_type = "unsupported-type"

        # Create a real config file
        mock_ep_path.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(mock_ep_path.config_path, 'w') as f:
            json.dump({"task_info": {"task_type": "unsupported-type"}}, f)

        result = _execute_task(mock_ep_path)

        assert result is False


class TestExecuteAblationStudyTask:
    """Test compare / ablation-study task dispatch."""

    @pytest.fixture
    def mock_ep_path(self, tmp_path):
        from core.external_path_parser import ExternalPath

        ep = ExternalPath(
            project_name="wiener_parallel_modeling",
            task_type="compare",
            task_name="wiener_parallel_modeling",
            full_path=tmp_path / "wiener_parallel_modeling",
            config_path=tmp_path / "wiener_parallel_modeling" / "config.json",
            output_path=tmp_path / "wiener_parallel_modeling" / "data",
        )
        ep.full_path.mkdir(parents=True, exist_ok=True)
        ep.output_path.mkdir(parents=True, exist_ok=True)
        return ep

    def test_execute_ablation_study_task_wiener_parallel_modeling(self, mock_ep_path):
        from core.external_cli_handler import _execute_ablation_study_task

        config = {
            "task_info": {
                "task_type": "compare",
                "analysis_type": "wiener-parallel-modeling",
            }
        }

        mock_analyzer = MagicMock()
        mock_analyzer.run_analysis.return_value = {"ok": True}

        mock_module = SimpleNamespace(WienerParallelModelingAnalyzer=MagicMock(return_value=mock_analyzer))

        with patch.dict(sys.modules, {"visualization.wiener_parallel_modeling": mock_module}):
            result = _execute_ablation_study_task(mock_ep_path, config)

        assert result is True
        mock_module.WienerParallelModelingAnalyzer.assert_called_once_with(
            config=config,
            task_root=mock_ep_path.full_path,
            output_dir=mock_ep_path.output_path,
        )
        mock_analyzer.run_analysis.assert_called_once()
        mock_analyzer.save_results.assert_called_once()

class TestExecuteFreqResponseTask:
    """Test _execute_freq_response_task function"""

    @pytest.fixture
    def mock_ep_path(self, tmp_path):
        """Create a mock ExternalPath object"""
        from core.external_path_parser import ExternalPath

        ep = ExternalPath(
            project_name="test_project",
            task_type="freq-response-compare",
            task_name="test_task",
            full_path=tmp_path / "test_task",
            config_path=tmp_path / "test_task" / "config.json",
            output_path=tmp_path / "test_task" / "data"
        )
        ep.output_path.mkdir(parents=True, exist_ok=True)
        return ep

    @pytest.fixture
    def valid_config(self, mock_ep_path):
        """Create a valid config dictionary"""
        return {
            "task_info": {"task_type": mock_ep_path.task_type},
            "visualization_config": {
                "layout": "side_by_side",
                "freq_range": [10, 200],
                "dpi": 300,
                "figsize": [12, 8],
                "title": "Test"
            },
            "data_sources": [
                {"project": "test_project", "state": "origin", "label": "Before"},
                {"project": "test_project", "state": "compensation", "label": "After", "split_magnitudes": True}
            ]
        }

    @patch('os.path.exists')
    @patch('visualization.frequency_response_json_comparator.quick_compare')
    def test_execute_freq_response_task_success(self, mock_quick_compare, mock_exists, mock_ep_path, valid_config):
        """Test successful frequency response task execution"""
        from core.external_cli_handler import _execute_freq_response_task

        output_file = str(mock_ep_path.output_path / "test.png")
        mock_quick_compare.return_value = output_file
        mock_exists.return_value = True

        result = _execute_freq_response_task(mock_ep_path, valid_config)

        assert result is True
        mock_quick_compare.assert_called_once()
        _, kwargs = mock_quick_compare.call_args
        assert kwargs["label1"] == "Before"
        assert kwargs["label2"] == "After"
        assert kwargs["split_magnitudes1"] is False
        assert kwargs["split_magnitudes2"] is True

    def test_execute_freq_response_task_no_data_sources(self, mock_ep_path):
        """Test frequency response task with no data sources"""
        from core.external_cli_handler import _execute_freq_response_task

        config = {
            "task_info": {"task_type": "freq-response-compare"},
            "visualization_config": {},
            "data_sources": []
        }

        result = _execute_freq_response_task(mock_ep_path, config)

        assert result is False

    @patch('visualization.frequency_response_json_comparator.quick_compare')
    def test_execute_freq_response_task_import_error(self, mock_quick_compare, mock_ep_path, valid_config):
        """Test frequency response task with import error"""
        from core.external_cli_handler import _execute_freq_response_task

        mock_quick_compare.side_effect = ImportError("Module not found")

        result = _execute_freq_response_task(mock_ep_path, valid_config)

        assert result is False


class TestExecuteFreqResponseCompensatorTask:
    """Test _execute_freq_response_compensator_task function"""

    @pytest.fixture
    def mock_ep_path(self, tmp_path):
        """Create a mock ExternalPath object"""
        from core.external_path_parser import ExternalPath

        ep = ExternalPath(
            project_name="test_project",
            task_type="freq-response-compensator",
            task_name="test_task",
            full_path=tmp_path / "test_task",
            config_path=tmp_path / "test_task" / "config.json",
            output_path=tmp_path / "test_task" / "data"
        )
        ep.output_path.mkdir(parents=True, exist_ok=True)
        return ep

    @pytest.fixture
    def valid_linear_response_data(self):
        """Create valid linear response data"""
        import numpy as np
        return {
            "gains_origin": np.random.rand(3, 100).tolist(),
            "gains_comped": np.random.rand(3, 100).tolist(),
            "frequencies": list(range(1, 101)),
            "magnitudes": [0.1, 0.5, 1.0]
        }

    @patch('core.external_cli_handler._save_task_metadata')
    def test_execute_compensator_task_success(self, mock_save_meta, mock_ep_path, tmp_path, valid_linear_response_data, monkeypatch):
        """Test successful compensator task execution"""
        from core.external_cli_handler import _execute_freq_response_compensator_task
        from pathlib import Path

        # Create the linear_response.json file in the correct location
        data_dir = tmp_path / "projects" / "test_project" / "data"
        data_dir.mkdir(parents=True)

        linear_file = data_dir / "linear_response.json"
        with open(linear_file, 'w') as f:
            json.dump(valid_linear_response_data, f)

        config = {
            "project_name": "test_project",
            "visualization_config": {
                "figsize": [10, 6],
                "dpi": 300
            }
        }

        # Change working directory to tmp_path for the test
        monkeypatch.chdir(tmp_path)

        result = _execute_freq_response_compensator_task(mock_ep_path, config)

        assert result is True

    def test_execute_compensator_task_missing_file(self, mock_ep_path):
        """Test compensator task with missing linear_response.json"""
        from core.external_cli_handler import _execute_freq_response_compensator_task

        config = {
            "project_name": "nonexistent_project",
            "visualization_config": {}
        }

        result = _execute_freq_response_compensator_task(mock_ep_path, config)

        assert result is False

    def test_execute_compensator_task_missing_keys(self, mock_ep_path, tmp_path, monkeypatch):
        """Test compensator task with missing required keys"""
        from core.external_cli_handler import _execute_freq_response_compensator_task

        # Create a minimal linear_response.json without required keys
        data_dir = tmp_path / "projects" / "test_project" / "data"
        data_dir.mkdir(parents=True)

        linear_file = data_dir / "linear_response.json"
        with open(linear_file, 'w') as f:
            json.dump({"frequencies": [1, 2, 3]}, f)

        config = {
            "project_name": "test_project",
            "visualization_config": {}
        }

        monkeypatch.chdir(tmp_path)
        result = _execute_freq_response_compensator_task(mock_ep_path, config)

        assert result is False

    def test_execute_compensator_task_empty_frequencies(self, mock_ep_path, tmp_path, monkeypatch):
        """Test compensator task with empty frequencies"""
        from core.external_cli_handler import _execute_freq_response_compensator_task

        import numpy as np

        data_dir = tmp_path / "projects" / "test_project" / "data"
        data_dir.mkdir(parents=True)

        linear_file = data_dir / "linear_response.json"
        with open(linear_file, 'w') as f:
            json.dump({
                "gains_origin": np.random.rand(1, 10).tolist(),
                "gains_comped": np.random.rand(1, 10).tolist(),
                "frequencies": [],
                "magnitudes": [0.5]
            }, f)

        config = {
            "project_name": "test_project",
            "visualization_config": {}
        }

        monkeypatch.chdir(tmp_path)
        result = _execute_freq_response_compensator_task(mock_ep_path, config)

        assert result is False


class TestExecuteNotImplementedTasks:
    """Test functions that return False (not implemented)"""

    @pytest.fixture
    def mock_ep_path(self, tmp_path):
        """Create a mock ExternalPath object"""
        from core.external_path_parser import ExternalPath

        return ExternalPath(
            project_name="test_project",
            task_type="test",
            task_name="test_task",
            full_path=tmp_path / "test_task",
            config_path=tmp_path / "test_task" / "config.json",
            output_path=tmp_path / "test_task" / "data"
        )

    def test_execute_bias_visualization_task_not_implemented(self, mock_ep_path):
        """Test bias visualization task returns False (not implemented)"""
        from core.external_cli_handler import _execute_bias_visualization_task

        result = _execute_bias_visualization_task(mock_ep_path, {})

        assert result is False

    def test_execute_waveform_analysis_task_not_implemented(self, mock_ep_path):
        """Test waveform analysis task returns False (not implemented)"""
        from core.external_cli_handler import _execute_waveform_analysis_task

        result = _execute_waveform_analysis_task(mock_ep_path, {})

        assert result is False


class TestExecuteWNET5CircuitValidationTask:
    """Test _execute_wnet5_circuit_validation_task function"""

    @pytest.fixture
    def mock_ep_path(self, tmp_path):
        """Create a mock ExternalPath object"""
        from core.external_path_parser import ExternalPath

        return ExternalPath(
            project_name="test_project",
            task_type="wnet5-circuit-validation",
            task_name="test_task",
            full_path=tmp_path / "test_task",
            config_path=tmp_path / "test_task" / "config.json",
            output_path=tmp_path / "test_task" / "data"
        )

    @patch('visualization.wnet5_circuit_validator.WNET5CircuitValidator')
    def test_execute_wnet5_task_success(self, mock_validator_class, mock_ep_path):
        """Test successful WNET5 circuit validation task"""
        from core.external_cli_handler import _execute_wnet5_circuit_validation_task

        mock_validator = MagicMock()
        mock_validator.execute_validation.return_value = True
        mock_validator_class.return_value = mock_validator

        config = {"task_info": {}}
        result = _execute_wnet5_circuit_validation_task(mock_ep_path, config)

        assert result is True
        mock_validator_class.assert_called_once_with(config, mock_ep_path.output_path)

    @patch('visualization.wnet5_circuit_validator.WNET5CircuitValidator')
    def test_execute_wnet5_task_import_error(self, mock_validator_class, mock_ep_path):
        """Test WNET5 circuit validation task with import error"""
        from core.external_cli_handler import _execute_wnet5_circuit_validation_task

        mock_validator_class.side_effect = ImportError("Module not found")

        config = {"task_info": {}}
        result = _execute_wnet5_circuit_validation_task(mock_ep_path, config)

        assert result is False

    @patch('visualization.wnet5_circuit_validator.WNET5CircuitValidator')
    def test_execute_wnet5_task_execution_error(self, mock_validator_class, mock_ep_path):
        """Test WNET5 circuit validation task with execution error"""
        from core.external_cli_handler import _execute_wnet5_circuit_validation_task

        mock_validator = MagicMock()
        mock_validator.execute_validation.side_effect = Exception("Execution failed")
        mock_validator_class.return_value = mock_validator

        config = {"task_info": {}}
        result = _execute_wnet5_circuit_validation_task(mock_ep_path, config)

        assert result is False


class TestUtilityFunctions:
    """Test utility functions"""

    def test_calculate_config_hash(self):
        """Test _calculate_config_hash function"""
        from core.external_cli_handler import _calculate_config_hash

        config = {"key": "value", "number": 42}
        hash1 = _calculate_config_hash(config)
        hash2 = _calculate_config_hash(config)
        hash3 = _calculate_config_hash({"key": "other"})

        assert hash1 == hash2
        assert hash1 != hash3
        assert len(hash1) == 32  # MD5 hex digest length

    @pytest.fixture
    def mock_ep_path(self, tmp_path):
        """Create a mock ExternalPath object"""
        from core.external_path_parser import ExternalPath

        return ExternalPath(
            project_name="test_project",
            task_type="test",
            task_name="test_task",
            full_path=tmp_path / "test_task",
            config_path=tmp_path / "test_task" / "config.json",
            output_path=tmp_path / "test_task" / "data"
        )

    def test_save_task_metadata(self, mock_ep_path):
        """Test _save_task_metadata function"""
        from core.external_cli_handler import _save_task_metadata

        # Ensure output directory exists
        mock_ep_path.output_path.mkdir(parents=True, exist_ok=True)

        config = {"task_info": {"type": "test"}}
        output_file = "/path/to/output.png"

        _save_task_metadata(mock_ep_path, config, output_file)

        metadata_file = mock_ep_path.output_path / "task_metadata.json"
        assert metadata_file.exists()

        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        assert "execution_time" in metadata
        assert metadata["task_info"] == config["task_info"]
        assert metadata["output_files"] == [output_file]
        assert "config_hash" in metadata

    def test_show_ep_help(self, capsys):
        """Test _show_ep_help function displays help text"""
        from core.external_cli_handler import _show_ep_help

        _show_ep_help()

        captured = capsys.readouterr()
        assert "ep 命令使用说明" in captured.out
        assert "freq-response-compare" in captured.out


class TestLoadAndValidateConfig:
    """Test _load_config and _validate_config functions"""

    @pytest.fixture
    def temp_config_file(self, tmp_path):
        """Create a temporary config file"""
        config = {"task_info": {"task_type": "test"}, "data": "value"}
        file_path = tmp_path / "config.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config, f)
        return file_path

    def test_load_config(self, temp_config_file):
        """Test _load_config function"""
        from core.external_cli_handler import _load_config

        config = _load_config(temp_config_file)

        assert config["task_info"]["task_type"] == "test"
        assert config["data"] == "value"

    def test_validate_config_success(self):
        """Test _validate_config with valid config - simplified test"""
        from core.external_cli_handler import _validate_config
        from core.config_validator import validate_visualization_config_data
        from unittest.mock import patch

        # Mock the actual validator to avoid validation complexity
        with patch('core.config_validator.validate_visualization_config_data', return_value={}):
            result = _validate_config({}, "freq-response-compare")

        assert result is not None

    def test_validate_config_failure(self):
        """Test _validate_config with invalid config raises ValueError"""
        from core.external_cli_handler import _validate_config

        config = {}

        with pytest.raises(ValueError):
            _validate_config(config, "freq-response-compare")


class TestExecuteExternalTaskAuto:
    """Test execute_external_task_auto function"""

    @pytest.fixture
    def mock_ep_path(self, tmp_path):
        """Create a mock ExternalPath object"""
        from core.external_path_parser import ExternalPath

        return ExternalPath(
            project_name="test_project",
            task_type="test",
            task_name="test_task",
            full_path=tmp_path / "test_task",
            config_path=tmp_path / "test_task" / "config.json",
            output_path=tmp_path / "test_task" / "data"
        )

    def test_execute_task_auto_config_not_exists(self, mock_ep_path):
        """Test execute_external_task_auto when config doesn't exist"""
        from core.external_cli_handler import execute_external_task_auto

        with pytest.raises(SystemExit):
            execute_external_task_auto(mock_ep_path)

        assert not mock_ep_path.config_path.exists()

    @patch('core.external_cli_handler._execute_task')
    def test_execute_task_auto_config_exists_success(self, mock_execute, mock_ep_path):
        """Test execute_external_task_auto when config exists and task succeeds"""
        from core.external_cli_handler import execute_external_task_auto

        # Create config file
        mock_ep_path.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(mock_ep_path.config_path, 'w') as f:
            json.dump({"task_info": {}}, f)

        mock_execute.return_value = True

        execute_external_task_auto(mock_ep_path)

        mock_execute.assert_called_once()

    @patch('core.external_cli_handler._execute_task')
    def test_execute_task_auto_config_exists_failure(self, mock_execute, mock_ep_path):
        """Test execute_external_task_auto when task fails"""
        from core.external_cli_handler import execute_external_task_auto

        # Create config file
        mock_ep_path.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(mock_ep_path.config_path, 'w') as f:
            json.dump({"task_info": {}}, f)

        mock_execute.return_value = False

        with pytest.raises(SystemExit):
            execute_external_task_auto(mock_ep_path)


class TestQemuCInferenceCutover:
    """Test qemu-c-inference cut-over to board_inference entrypoints."""

    @pytest.fixture
    def mock_ep_path(self, tmp_path):
        from core.external_path_parser import ExternalPath

        return ExternalPath(
            project_name="test_project",
            task_type="qemu-c-inference",
            task_name="test_task",
            full_path=tmp_path / "test_task",
            config_path=tmp_path / "test_task" / "config.json",
            output_path=tmp_path / "test_task" / "data",
        )

    def test_execute_qemu_c_inference_task_routes_to_board_inference(self, mock_ep_path):
        from core.external_cli_handler import _execute_qemu_c_inference_task

        config = {"task_info": {"task_type": "qemu-c-inference"}}
        with patch('core.board_inference.entrypoints.execute_qemu_inference_task', return_value=True) as mock_execute:
            assert _execute_qemu_c_inference_task(mock_ep_path, config) is True

        mock_execute.assert_called_once_with(mock_ep_path, config)

    def test_execute_qemu_c_inference_keil_bench_task_routes_to_board_inference(self, mock_ep_path):
        from core.external_cli_handler import _execute_qemu_c_inference_keil_bench_task

        config = {"task_info": {"task_type": "qemu-c-inference"}}
        args = SimpleNamespace(
            ep_probe_uid='ABC123',
            ep_serial_port='COM8',
            ep_serial_baud_rate=115200,
            ep_keil_target='MET405',
            ep_keil_program_backend='keil',
            ep_keil_programmer='daplink',
            ep_keil_capture_timeout=20,
            ep_keil_job_timeout=300,
            ep_keil_cli_path='C:/tool/keil-cli.py',
        )

        with patch('core.board_inference.entrypoints.execute_qemu_inference_keil_bench_task', return_value=True) as mock_execute:
            assert _execute_qemu_c_inference_keil_bench_task(mock_ep_path, config, args) is True

        mock_execute.assert_called_once_with(
            mock_ep_path,
            config,
            keil_overrides={
                'probe_uid': 'ABC123',
                'serial_port': 'COM8',
                'baud_rate': 115200,
                'target': 'MET405',
                'program_backend': 'keil',
                'programmer': 'daplink',
                'capture_timeout': 20,
                'job_timeout': 300,
                'keil_cli_path': 'C:/tool/keil-cli.py',
            },
        )


class TestHandleEPCommand:
    """Test handle_ep_command function"""

    @pytest.fixture
    def mock_args(self):
        """Create mock CLIArgs object"""
        args = MagicMock()
        args.ep_project_path = "test_project/test_task"
        args.ep_action = 'run'
        return args

    def test_handle_ep_command_success(self, mock_args, tmp_path):
        """Test handle_ep_command with successful execution"""
        from core.external_cli_handler import handle_ep_command

        with patch('core.external_cli_handler.execute_external_task_auto') as mock_execute:
            mock_execute.return_value = None

            handle_ep_command(mock_args)

            mock_execute.assert_called_once()

    def test_handle_ep_command_create_success(self, mock_args):
        """Test handle_ep_command routes create action correctly"""
        from core.external_cli_handler import handle_ep_command

        mock_args.ep_action = 'create'

        with patch('core.external_cli_handler.create_external_template_command') as mock_create:
            handle_ep_command(mock_args)

            mock_create.assert_called_once()

    def test_handle_ep_command_keil_bench_success(self, mock_args):
        """Test handle_ep_command routes keil-bench action correctly."""
        from core.external_cli_handler import handle_ep_command

        mock_args.ep_action = 'keil-bench'

        with patch('core.external_cli_handler.execute_external_keil_bench_command') as mock_keil_bench:
            handle_ep_command(mock_args)

            mock_keil_bench.assert_called_once()

    def test_handle_ep_command_invalid_path(self, mock_args):
        """Test handle_ep_command with invalid path"""
        from core.external_cli_handler import handle_ep_command
        from core.external_path_parser import ExternalPathParser

        mock_args.ep_project_path = "invalid//path:::"

        with pytest.raises(SystemExit):
            handle_ep_command(mock_args)

    @patch('core.external_cli_handler.execute_external_task_auto')
    def test_handle_ep_command_task_failure(self, mock_execute, mock_args, tmp_path):
        """Test handle_ep_command when task execution fails"""
        from core.external_cli_handler import handle_ep_command

        # Make execute_external_task_auto trigger the failure path
        mock_execute.side_effect = SystemExit(1)

        with pytest.raises(SystemExit):
            handle_ep_command(mock_args)


class TestCreateExternalTemplateCommand:
    """Test create_external_template_command function"""

    @pytest.fixture
    def mock_ep_path(self, tmp_path):
        from core.external_path_parser import ExternalPath

        return ExternalPath(
            project_name="test_project",
            task_type="freq-response-compare",
            task_name="test_task",
            full_path=tmp_path / "test_task",
            config_path=tmp_path / "test_task" / "config.json",
            output_path=tmp_path / "test_task" / "data"
        )

    @patch('core.external_cli_handler.create_external_template')
    def test_create_external_template_command_success(self, mock_create, mock_ep_path):
        from core.external_cli_handler import create_external_template_command

        create_external_template_command(mock_ep_path)

        mock_create.assert_called_once_with(mock_ep_path)

    def test_create_external_template_command_rejects_existing_config(self, mock_ep_path):
        from core.external_cli_handler import create_external_template_command

        mock_ep_path.config_path.parent.mkdir(parents=True, exist_ok=True)
        mock_ep_path.config_path.write_text('{}', encoding='utf-8')

        with pytest.raises(SystemExit):
            create_external_template_command(mock_ep_path)
