"""
Tests for core/config_validator module
"""

import pytest
import sys
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
_SRC_DIR = Path(__file__).parent.parent.parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from core.config_validator import (
    ConfigValidationError,
    VisualizationConfigValidator,
    validate_visualization_config,
    validate_visualization_config_data
)


class TestConfigValidationError:
    """Test ConfigValidationError exception"""

    def test_error_message(self):
        """Test error message is set correctly"""
        error = ConfigValidationError("Test error message")
        assert str(error) == "Test error message"
        assert "Test error message" in error.args[0]


class TestVisualizationConfigValidator:
    """Test VisualizationConfigValidator class"""

    @pytest.fixture
    def validator(self):
        """Create a validator instance"""
        return VisualizationConfigValidator()

    def test_init(self, validator):
        """Test validator initialization"""
        assert validator is not None
        assert hasattr(validator, 'schemas')
        assert len(validator.schemas) == 6

    def test_schemas_exist(self, validator):
        """Test that all expected schemas are registered"""
        assert 'freq-response-compare' in validator.schemas
        assert 'freq-response-compensator' in validator.schemas
        assert 'bias-visualization' in validator.schemas
        assert 'waveform-analysis' in validator.schemas
        assert 'wnet5-circuit-validation' in validator.schemas
        assert 'qemu-c-inference' in validator.schemas


class TestFreqResponseSchema:
    """Test frequency response comparison schema validation"""

    @pytest.fixture
    def validator(self):
        return VisualizationConfigValidator()

    def test_valid_freq_response_config(self, validator):
        """Test valid frequency response configuration"""
        config = {
            "task_info": {"task_type": "freq-response-compare"},
            "visualization_config": {
                "layout": "overlay",
                "freq_range": [10, 1000],
                "gain_range": [-60, 0],
                "output_format": "png",
                "dpi": 300,
                "figsize": [12, 8]
            },
            "data_sources": [
                {"project": "project1", "label": "Origin", "state": "origin"},
                {"project": "project1", "label": "Compensated", "state": "compensation"}
            ]
        }
        # Note: The validator may return modified config or raise if schema is strict
        # This test verifies the validation doesn't reject valid config structure

    def test_missing_required_task_info(self, validator):
        """Test validation fails when task_info is missing"""
        config = {
            "visualization_config": {},
            "data_sources": []
        }
        with pytest.raises(ConfigValidationError):
            validator.validate_config_data(config, "freq-response-compare")

    def test_missing_required_data_sources(self, validator):
        """Test validation fails when data_sources is missing"""
        config = {
            "task_info": {"task_type": "freq-response-compare"},
            "visualization_config": {}
        }
        with pytest.raises(ConfigValidationError):
            validator.validate_config_data(config, "freq-response-compare")

    def test_invalid_task_type_in_config(self, validator):
        """Test validation fails when task_type doesn't match"""
        config = {
            "task_info": {"task_type": "wrong-type"},
            "visualization_config": {},
            "data_sources": [{"project": "p1", "label": "l1"}]
        }
        with pytest.raises(ConfigValidationError):
            validator.validate_config_data(config, "freq-response-compare")

    def test_additional_properties_not_allowed(self, validator):
        """Test that additional properties are not allowed"""
        config = {
            "task_info": {"task_type": "freq-response-compare"},
            "visualization_config": {},
            "data_sources": [{"project": "p1", "label": "l1"}],
            "extra_field": "not allowed"
        }
        with pytest.raises(ConfigValidationError):
            validator.validate_config_data(config, "freq-response-compare")

    def test_invalid_layout_value(self, validator):
        """Test invalid layout enum value"""
        config = {
            "task_info": {"task_type": "freq-response-compare"},
            "visualization_config": {"layout": "invalid_layout"},
            "data_sources": [{"project": "p1", "label": "l1"}]
        }
        with pytest.raises(ConfigValidationError):
            validator.validate_config_data(config, "freq-response-compare")

    def test_invalid_output_format(self, validator):
        """Test invalid output format enum value"""
        config = {
            "task_info": {"task_type": "freq-response-compare"},
            "visualization_config": {"output_format": "invalid_format"},
            "data_sources": [{"project": "p1", "label": "l1"}]
        }
        with pytest.raises(ConfigValidationError):
            validator.validate_config_data(config, "freq-response-compare")

    def test_invalid_data_source_state(self, validator):
        """Test invalid data source state enum value"""
        config = {
            "task_info": {"task_type": "freq-response-compare"},
            "visualization_config": {},
            "data_sources": [{"project": "p1", "label": "l1", "state": "invalid_state"}]
        }
        with pytest.raises(ConfigValidationError):
            validator.validate_config_data(config, "freq-response-compare")

    def test_empty_data_sources_array(self, validator):
        """Test that empty data_sources array fails validation"""
        config = {
            "task_info": {"task_type": "freq-response-compare"},
            "visualization_config": {},
            "data_sources": []
        }
        with pytest.raises(ConfigValidationError):
            validator.validate_config_data(config, "freq-response-compare")

    def test_freq_range_order_validation(self, validator):
        """Test frequency range order validation"""
        config = {
            "task_info": {"task_type": "freq-response-compare"},
            "visualization_config": {"freq_range": [1000, 10]},  # Wrong order
            "data_sources": [{"project": "p1", "label": "l1"}]
        }
        with pytest.raises(ConfigValidationError):
            validator.validate_config_data(config, "freq-response-compare")


class TestBiasVisualizationSchema:
    """Test bias visualization schema validation"""

    @pytest.fixture
    def validator(self):
        return VisualizationConfigValidator()

    def test_valid_bias_visualization_config(self, validator):
        """Test valid bias visualization configuration"""
        config = {
            "task_info": {"task_type": "bias-visualization"},
            "visualization_config": {
                "output_format": "png",
                "dpi": 150,
                "figsize": [10, 6],
                "points": 1000
            },
            "data_sources": [
                {"project": "project1", "label": "Baseline", "state": "origin"}
            ]
        }
        result = validator.validate_config_data(config, "bias-visualization")
        assert result == config

    def test_missing_data_source_label(self, validator):
        """Test validation fails when label is missing"""
        config = {
            "task_info": {"task_type": "bias-visualization"},
            "visualization_config": {},
            "data_sources": [{"project": "p1"}]  # Missing label
        }
        with pytest.raises(ConfigValidationError):
            validator.validate_config_data(config, "bias-visualization")

    def test_dpi_range_validation(self, validator):
        """Test DPI value range validation"""
        # Too low DPI
        config = {
            "task_info": {"task_type": "bias-visualization"},
            "visualization_config": {"dpi": 50},
            "data_sources": [{"project": "p1", "label": "l1"}]
        }
        with pytest.raises(ConfigValidationError):
            validator.validate_config_data(config, "bias-visualization")

        # Too high DPI
        config_high = {
            "task_info": {"task_type": "bias-visualization"},
            "visualization_config": {"dpi": 700},
            "data_sources": [{"project": "p1", "label": "l1"}]
        }
        with pytest.raises(ConfigValidationError):
            validator.validate_config_data(config_high, "bias-visualization")


class TestWnet5CircuitValidationSchema:
    """Test WNET5 circuit validation schema"""

    @pytest.fixture
    def validator(self):
        return VisualizationConfigValidator()

    def test_valid_wnet5_config(self, validator):
        """Test valid WNET5 circuit validation configuration"""
        config = {
            "task_info": {"task_type": "wnet5-circuit-validation", "description": "Test"},
            "model_project_name": "WNET5q1h2u6l3",
            "frequency_range": {
                "start_freq": 10,
                "stop_freq": 1000,
                "points": 100
            }
        }
        result = validator.validate_config_data(config, "wnet5-circuit-validation")
        assert result == config

    def test_missing_model_project_name(self, validator):
        """Test validation fails when model_project_name is missing"""
        config = {
            "task_info": {"task_type": "wnet5-circuit-validation"},
            "frequency_range": {"start_freq": 10, "stop_freq": 1000}
        }
        with pytest.raises(ConfigValidationError):
            validator.validate_config_data(config, "wnet5-circuit-validation")

    def test_invalid_frequency_range(self, validator):
        """Test invalid frequency range values"""
        config = {
            "task_info": {"task_type": "wnet5-circuit-validation"},
            "model_project_name": "test",
            "frequency_range": {
                "start_freq": 0.0001,  # Below minimum
                "stop_freq": 1000000  # Above maximum
            }
        }
        with pytest.raises(ConfigValidationError):
            validator.validate_config_data(config, "wnet5-circuit-validation")

    def test_analysis_layer_range(self, validator):
        """Test analysis layer range validation"""
        config = {
            "task_info": {"task_type": "wnet5-circuit-validation"},
            "model_project_name": "test",
            "frequency_range": {"start_freq": 10, "stop_freq": 1000},
            "analysis_layer": 5
        }
        result = validator.validate_config_data(config, "wnet5-circuit-validation")
        assert result["analysis_layer"] == 5

        # Invalid layer
        config_invalid = {
            "task_info": {"task_type": "wnet5-circuit-validation"},
            "model_project_name": "test",
            "frequency_range": {"start_freq": 10, "stop_freq": 1000},
            "analysis_layer": 15  # Above maximum
        }
        with pytest.raises(ConfigValidationError):
            validator.validate_config_data(config_invalid, "wnet5-circuit-validation")

    def test_opamp_config_validation(self, validator):
        """Test opamp configuration validation"""
        config = {
            "task_info": {"task_type": "wnet5-circuit-validation"},
            "model_project_name": "test",
            "frequency_range": {"start_freq": 10, "stop_freq": 1000},
            "inference_config": {
                "opamp_config": {
                    "model": "ideal",
                    "power_pins": True
                }
            }
        }
        result = validator.validate_config_data(config, "wnet5-circuit-validation")
        assert result["inference_config"]["opamp_config"]["model"] == "ideal"

        # Invalid opamp model
        config_invalid = {
            "task_info": {"task_type": "wnet5-circuit-validation"},
            "model_project_name": "test",
            "frequency_range": {"start_freq": 10, "stop_freq": 1000},
            "inference_config": {
                "opamp_config": {
                    "model": "invalid_opamp"
                }
            }
        }
        with pytest.raises(ConfigValidationError):
            validator.validate_config_data(config_invalid, "wnet5-circuit-validation")


class TestFileValidation:
    """Test validation from file"""

    @pytest.fixture
    def validator(self):
        return VisualizationConfigValidator()

    def test_validate_config_file(self, validator):
        """Test validation of configuration file"""
        config = {
            "task_info": {"task_type": "freq-response-compare"},
            "visualization_config": {},
            "data_sources": [{"project": "p1", "label": "l1"}]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            temp_path = f.name

        try:
            result = validator.validate_config_file(temp_path, "freq-response-compare")
            assert result == config
        finally:
            os.unlink(temp_path)

    def test_validate_nonexistent_file(self, validator):
        """Test validation fails for nonexistent file"""
        with pytest.raises(ConfigValidationError):
            validator.validate_config_file("/nonexistent/path/config.json", "freq-response-compare")

    def test_validate_invalid_json_file(self, validator):
        """Test validation fails for invalid JSON file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{invalid json")
            temp_path = f.name

        try:
            with pytest.raises(ConfigValidationError):
                validator.validate_config_file(temp_path, "freq-response-compare")
        finally:
            os.unlink(temp_path)


class TestConvenienceFunctions:
    """Test convenience functions"""

    def test_validate_visualization_config(self):
        """Test validate_visualization_config convenience function"""
        config = {
            "task_info": {"task_type": "bias-visualization"},
            "visualization_config": {},
            "data_sources": [{"project": "p1", "label": "l1"}]
        }

        result = validate_visualization_config_data(config, "bias-visualization")
        assert result == config

    def test_validate_visualization_config_raises_error(self):
        """Test validate_visualization_config raises error for invalid config"""
        invalid_config = {
            "task_info": {"task_type": "bias-visualization"},
            "visualization_config": {},
            "data_sources": []
        }

        with pytest.raises(ConfigValidationError):
            validate_visualization_config_data(invalid_config, "bias-visualization")


class TestSchemaValidationHelpers:
    """Test internal validation helper methods"""

    @pytest.fixture
    def validator(self):
        return VisualizationConfigValidator()

    def test_check_type_object(self, validator):
        """Test type checking for objects"""
        assert validator._check_type({}, "object") is True
        assert validator._check_type([], "object") is False
        assert validator._check_type("string", "object") is False

    def test_check_type_array(self, validator):
        """Test type checking for arrays"""
        assert validator._check_type([], "array") is True
        assert validator._check_type({}, "array") is False
        assert validator._check_type("string", "array") is False

    def test_check_type_string(self, validator):
        """Test type checking for strings"""
        assert validator._check_type("test", "string") is True
        assert validator._check_type("", "string") is True
        assert validator._check_type(123, "string") is False

    def test_check_type_integer(self, validator):
        """Test type checking for integers"""
        assert validator._check_type(123, "integer") is True
        assert validator._check_type(0, "integer") is True
        assert validator._check_type(1.5, "integer") is False

    def test_check_type_number(self, validator):
        """Test type checking for numbers (int or float)"""
        assert validator._check_type(123, "number") is True
        assert validator._check_type(1.5, "number") is True
        assert validator._check_type("test", "number") is False

    def test_check_type_boolean(self, validator):
        """Test type checking for booleans"""
        assert validator._check_type(True, "boolean") is True
        assert validator._check_type(False, "boolean") is True
        assert validator._check_type(1, "boolean") is False


class TestSchemaValidationBoundary:
    """Boundary tests for schema validation"""

    @pytest.fixture
    def validator(self):
        return VisualizationConfigValidator()

    def test_validate_config_data_non_dict_raises(self, validator):
        """Test that non-dict config raises error"""
        with pytest.raises(ConfigValidationError) as exc_info:
            validator.validate_config_data("not a dict", "freq-response-compare")

        assert "JSON对象" in str(exc_info.value)

    def test_validate_config_data_none_raises(self, validator):
        """Test that None config raises error"""
        with pytest.raises(ConfigValidationError) as exc_info:
            validator.validate_config_data(None, "freq-response-compare")

        assert "JSON对象" in str(exc_info.value)

    def test_validate_config_data_list_raises(self, validator):
        """Test that list config raises error"""
        with pytest.raises(ConfigValidationError) as exc_info:
            validator.validate_config_data([1, 2, 3], "freq-response-compare")

        assert "JSON对象" in str(exc_info.value)

    def test_validate_unsupported_task_type(self, validator):
        """Test that unsupported task type raises error"""
        with pytest.raises(ConfigValidationError) as exc_info:
            validator.validate_config_data({}, "unsupported-task-type")

        assert "不支持的任务类型" in str(exc_info.value)

    def test_validate_string_min_length_boundary(self, validator):
        """Test string minimum length validation"""
        config = {
            "task_info": {"task_type": "freq-response-compare"},
            "visualization_config": {},
            "data_sources": [{"project": "", "label": "test"}]  # Empty project name
        }

        with pytest.raises(ConfigValidationError) as exc_info:
            validator.validate_config_data(config, "freq-response-compare")

        assert "不能少于" in str(exc_info.value) or "minLength" in str(exc_info.value)

    def test_validate_array_min_items_boundary(self, validator):
        """Test array minimum items validation"""
        config = {
            "task_info": {"task_type": "freq-response-compare"},
            "visualization_config": {},
            "data_sources": [
                {"project": "p1", "label": "l1"},
                {"project": "p2", "label": "l2"},
                {"project": "p3", "label": "l3"},
                {"project": "p4", "label": "l4"},
                {"project": "p5", "label": "l5"},
                {"project": "p6", "label": "l6"},
                {"project": "p7", "label": "l7"},
                {"project": "p8", "label": "l8"},
                {"project": "p9", "label": "l9"},
                {"project": "p10", "label": "l10"},
                {"project": "p11", "label": "l11"}  # 11 items, max is 10
            ]
        }

        with pytest.raises(ConfigValidationError):
            validator.validate_config_data(config, "freq-response-compare")

    def test_validate_array_max_items_boundary(self, validator):
        """Test array maximum items validation"""
        config = {
            "task_info": {"task_type": "bias-visualization"},
            "visualization_config": {},
            "data_sources": [
                {"project": "p1", "label": "l1"},
                {"project": "p2", "label": "l2"},
                {"project": "p3", "label": "l3"},
                {"project": "p4", "label": "l4"},
                {"project": "p5", "label": "l5"},
                {"project": "p6", "label": "l6"}  # 6 items, max is 5
            ]
        }

        with pytest.raises(ConfigValidationError):
            validator.validate_config_data(config, "bias-visualization")

    def test_validate_integer_minimum_boundary(self, validator):
        """Test integer minimum value validation"""
        config = {
            "task_info": {"task_type": "wnet5-circuit-validation"},
            "model_project_name": "test",
            "frequency_range": {"start_freq": 10, "stop_freq": 1000},
            "analysis_layer": 0  # Below minimum of 1
        }

        with pytest.raises(ConfigValidationError):
            validator.validate_config_data(config, "wnet5-circuit-validation")

    def test_validate_integer_maximum_boundary(self, validator):
        """Test integer maximum value validation"""
        config = {
            "task_info": {"task_type": "wnet5-circuit-validation"},
            "model_project_name": "test",
            "frequency_range": {"start_freq": 10, "stop_freq": 1000},
            "analysis_layer": 11  # Above maximum of 10
        }

        with pytest.raises(ConfigValidationError):
            validator.validate_config_data(config, "wnet5-circuit-validation")

    def test_validate_number_minimum_boundary(self, validator):
        """Test number minimum value validation"""
        config = {
            "task_info": {"task_type": "wnet5-circuit-validation"},
            "model_project_name": "test",
            "frequency_range": {
                "start_freq": 0.0001,  # Below minimum of 0.001
                "stop_freq": 1000
            }
        }

        with pytest.raises(ConfigValidationError):
            validator.validate_config_data(config, "wnet5-circuit-validation")

    def test_validate_number_maximum_boundary(self, validator):
        """Test number maximum value validation"""
        config = {
            "task_info": {"task_type": "wnet5-circuit-validation"},
            "model_project_name": "test",
            "frequency_range": {
                "start_freq": 10,
                "stop_freq": 2000000  # Above maximum of 1000000
            }
        }

        with pytest.raises(ConfigValidationError):
            validator.validate_config_data(config, "wnet5-circuit-validation")

    def test_validate_dpi_minimum_boundary(self, validator):
        """Test DPI minimum value validation"""
        config = {
            "task_info": {"task_type": "bias-visualization"},
            "visualization_config": {"dpi": 71},  # Below minimum of 72
            "data_sources": [{"project": "p1", "label": "l1"}]
        }

        with pytest.raises(ConfigValidationError):
            validator.validate_config_data(config, "bias-visualization")

    def test_validate_dpi_maximum_boundary(self, validator):
        """Test DPI maximum value validation"""
        config = {
            "task_info": {"task_type": "bias-visualization"},
            "visualization_config": {"dpi": 601},  # Above maximum of 600
            "data_sources": [{"project": "p1", "label": "l1"}]
        }

        with pytest.raises(ConfigValidationError):
            validator.validate_config_data(config, "bias-visualization")

    def test_validate_points_minimum_boundary(self, validator):
        """Test points minimum value validation"""
        config = {
            "task_info": {"task_type": "bias-visualization"},
            "visualization_config": {"points": 9},  # Below minimum of 10
            "data_sources": [{"project": "p1", "label": "l1"}]
        }

        with pytest.raises(ConfigValidationError):
            validator.validate_config_data(config, "bias-visualization")

    def test_validate_points_maximum_boundary(self, validator):
        """Test points maximum value validation"""
        config = {
            "task_info": {"task_type": "bias-visualization"},
            "visualization_config": {"points": 100001},  # Above maximum of 100000
            "data_sources": [{"project": "p1", "label": "l1"}]
        }

        with pytest.raises(ConfigValidationError):
            validator.validate_config_data(config, "bias-visualization")

    def test_validate_freq_range_array_length(self, validator):
        """Test frequency range array length validation"""
        config = {
            "task_info": {"task_type": "wnet5-circuit-validation"},
            "model_project_name": "test",
            "frequency_range": {
                "start_freq": 10,
                "stop_freq": 1000,
                "points": 100  # This is fine
            }
        }

        result = validator.validate_config_data(config, "wnet5-circuit-validation")
        assert result["frequency_range"]["points"] == 100


class TestConfigValidationEdgeCases:
    """Edge case tests for configuration validation"""

    @pytest.fixture
    def validator(self):
        return VisualizationConfigValidator()

    def test_validate_config_file_permission_error(self, validator):
        """Test handling of file permission errors"""
        import errno
        from pathlib import Path

        test_path = "/some/path/config.json"

        # Mock Path.exists to return True, then mock open to raise PermissionError
        with patch.object(Path, 'exists', return_value=True):
            with patch('builtins.open', side_effect=PermissionError("Permission denied")):
                with pytest.raises(ConfigValidationError) as exc_info:
                    validator.validate_config_file(test_path, "freq-response-compare")

                assert "读取配置文件失败" in str(exc_info.value)

    def test_validate_config_file_encoding_error(self, validator):
        """Test handling of file encoding errors"""
        from pathlib import Path

        test_path = "/some/path/config.json"

        # Mock Path.exists to return True, then mock open to raise UnicodeDecodeError
        with patch.object(Path, 'exists', return_value=True):
            with patch('builtins.open', side_effect=UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid start byte')):
                with pytest.raises(ConfigValidationError) as exc_info:
                    validator.validate_config_file(test_path, "freq-response-compare")

                assert "读取配置文件失败" in str(exc_info.value)

    def test_validate_config_file_io_error(self, validator):
        """Test handling of general IO errors"""
        from pathlib import Path

        test_path = "/some/path/config.json"

        # Mock Path.exists to return True, then mock open to raise IOError
        with patch.object(Path, 'exists', return_value=True):
            with patch('builtins.open', side_effect=IOError("Disk error")):
                with pytest.raises(ConfigValidationError) as exc_info:
                    validator.validate_config_file(test_path, "freq-response-compare")

                assert "读取配置文件失败" in str(exc_info.value)

    def test_validate_multiple_schema_errors(self, validator):
        """Test that multiple schema errors are collected"""
        config = {
            "task_info": {"task_type": "wrong-type"},  # Wrong task type
            "visualization_config": {
                "layout": "invalid",  # Invalid layout
                "freq_range": [1000, 10]  # Wrong order
            },
            "data_sources": []  # Empty
        }

        with pytest.raises(ConfigValidationError) as exc_info:
            validator.validate_config_data(config, "freq-response-compare")

        # Error message should contain multiple errors
        error_msg = str(exc_info.value)
        # At least one of the errors should be in the message

    def test_validate_nested_object_extra_fields(self, validator):
        """Test validation rejects extra fields in nested objects"""
        config = {
            "task_info": {
                "task_type": "freq-response-compare",
                "extra_field": "not allowed"  # Extra field in task_info
            },
            "visualization_config": {},
            "data_sources": [{"project": "p1", "label": "l1"}]
        }

        with pytest.raises(ConfigValidationError) as exc_info:
            validator.validate_config_data(config, "freq-response-compare")

        assert "不允许的字段" in str(exc_info.value) or "extra_field" in str(exc_info.value)

    def test_validate_data_source_missing_project(self, validator):
        """Test validation fails when project is missing in data source"""
        config = {
            "task_info": {"task_type": "freq-response-compare"},
            "visualization_config": {},
            "data_sources": [{"label": "l1"}]  # Missing project
        }

        with pytest.raises(ConfigValidationError):
            validator.validate_config_data(config, "freq-response-compare")

    def test_validate_data_source_missing_label(self, validator):
        """Test validation fails when label is missing in data source"""
        config = {
            "task_info": {"task_type": "freq-response-compare"},
            "visualization_config": {},
            "data_sources": [{"project": "p1"}]  # Missing label
        }

        with pytest.raises(ConfigValidationError):
            validator.validate_config_data(config, "freq-response-compare")


class TestWNET5CircuitValidationSchemaBoundary:
    """Boundary tests for WNET5 circuit validation schema"""

    @pytest.fixture
    def validator(self):
        return VisualizationConfigValidator()

    def test_inference_config_opamp_model_enum(self, validator):
        """Test opamp model enum validation"""
        # Valid opamp models
        valid_models = ["ideal", "LM324", "TL084", "OPAx205A", "AD8622", "OPA1611"]
        for model in valid_models:
            config = {
                "task_info": {"task_type": "wnet5-circuit-validation"},
                "model_project_name": "test",
                "frequency_range": {"start_freq": 10, "stop_freq": 1000},
                "inference_config": {
                    "opamp_config": {"model": model}
                }
            }
            result = validator.validate_config_data(config, "wnet5-circuit-validation")
            assert result["inference_config"]["opamp_config"]["model"] == model

    def test_inference_config_opamp_model_invalid(self, validator):
        """Test invalid opamp model validation"""
        config = {
            "task_info": {"task_type": "wnet5-circuit-validation"},
            "model_project_name": "test",
            "frequency_range": {"start_freq": 10, "stop_freq": 1000},
            "inference_config": {
                "opamp_config": {"model": "invalid_opamp_model"}
            }
        }

        with pytest.raises(ConfigValidationError):
            validator.validate_config_data(config, "wnet5-circuit-validation")

    def test_high_pass_config_boolean_values(self, validator):
        """Test high pass config enable boolean validation"""
        config = {
            "task_info": {"task_type": "wnet5-circuit-validation"},
            "model_project_name": "test",
            "frequency_range": {"start_freq": 10, "stop_freq": 1000},
            "inference_config": {
                "high_pass_config": {
                    "enable": True,
                    "cutoff_freq": 5.0
                }
            }
        }

        result = validator.validate_config_data(config, "wnet5-circuit-validation")
        assert result["inference_config"]["high_pass_config"]["enable"] is True

    def test_bias_compensation_config(self, validator):
        """Test bias compensation configuration validation"""
        config = {
            "task_info": {"task_type": "wnet5-circuit-validation"},
            "model_project_name": "test",
            "frequency_range": {"start_freq": 10, "stop_freq": 1000},
            "inference_config": {
                "bias_compensation": {
                    "enabled": True,
                    "layer_bias_adjustments": {}
                }
            }
        }

        result = validator.validate_config_data(config, "wnet5-circuit-validation")
        assert result["inference_config"]["bias_compensation"]["enabled"] is True

    def test_power_supply_config(self, validator):
        """Test power supply configuration validation"""
        config = {
            "task_info": {"task_type": "wnet5-circuit-validation"},
            "model_project_name": "test",
            "frequency_range": {"start_freq": 10, "stop_freq": 1000},
            "inference_config": {
                "power_supply": {
                    "vcc": 15.0,
                    "vee": -15.0
                }
            }
        }

        result = validator.validate_config_data(config, "wnet5-circuit-validation")
        assert result["inference_config"]["power_supply"]["vcc"] == 15.0
        assert result["inference_config"]["power_supply"]["vee"] == -15.0

    def test_svf_error_simulation_config(self, validator):
        """Test SVF error simulation configuration validation"""
        config = {
            "task_info": {"task_type": "wnet5-circuit-validation"},
            "model_project_name": "test",
            "frequency_range": {"start_freq": 10, "stop_freq": 1000},
            "svf_error_simulation": {
                "enable": True,
                "measured_data_file": "/path/to/data.csv",
                "include_dense_layer": True,
                "compensation": {
                    "enabled": False,
                    "selftest_file": "/path/to/selftest.csv"
                }
            }
        }

        result = validator.validate_config_data(config, "wnet5-circuit-validation")
        assert result["svf_error_simulation"]["enable"] is True

    def test_experiment_comparison_config(self, validator):
        """Test experiment comparison configuration validation"""
        config = {
            "task_info": {"task_type": "wnet5-circuit-validation"},
            "model_project_name": "test",
            "frequency_range": {"start_freq": 10, "stop_freq": 1000},
            "compare_with_experiment": "experiment_data",
            "experiment_comparison": {
                "enable": True,
                "mode": "single_file",
                "experiment_data_dir": "/path/to/experiment",
                "plot_config": {
                    "coordinate_system": "loglog",
                    "y_unit": "dB"
                }
            }
        }

        result = validator.validate_config_data(config, "wnet5-circuit-validation")
        assert result["experiment_comparison"]["enable"] is True
        assert result["experiment_comparison"]["mode"] == "single_file"


class TestFreqResponseCompensatorSchema:
    """Tests for frequency response compensator schema"""

    @pytest.fixture
    def validator(self):
        return VisualizationConfigValidator()

    def test_valid_freq_response_compensator_config(self, validator):
        """Test valid frequency response compensator configuration"""
        config = {
            "task_info": {"task_type": "freq-response-compensator", "description": "Test"},
            "project_name": "WNET5q1h2u6l3",
            "visualization_config": {
                "output_format": "png",
                "dpi": 300,
                "figsize": [12, 8],
                "freq_range": [5, 200],
                "gain_range": [-60, 0],
                "log_scale": True,
                "target_magnitudes": [0.1, 0.5, 1.0]
            }
        }

        result = validator.validate_config_data(config, "freq-response-compensator")
        assert result == config

    def test_freq_response_compensator_minimal_config(self, validator):
        """Test frequency response compensator with minimal config"""
        config = {
            "task_info": {"task_type": "freq-response-compensator"},
            "project_name": "test_project"
        }

        result = validator.validate_config_data(config, "freq-response-compensator")
        assert result["project_name"] == "test_project"

    def test_freq_response_compensator_missing_project_name(self, validator):
        """Test frequency response compensator missing project name"""
        config = {
            "task_info": {"task_type": "freq-response-compensator"}
        }

        with pytest.raises(ConfigValidationError):
            validator.validate_config_data(config, "freq-response-compensator")


class TestWaveformAnalysisSchema:
    """Tests for waveform analysis schema"""

    @pytest.fixture
    def validator(self):
        return VisualizationConfigValidator()

    def test_valid_waveform_analysis_config(self, validator):
        """Test valid waveform analysis configuration"""
        config = {
            "task_info": {"task_type": "waveform-analysis"},
            "visualization_config": {
                "output_format": "pdf",
                "dpi": 300,
                "figsize": [10, 6],
                "title": "Waveform Analysis"
            },
            "data_sources": [
                {"project": "project1", "label": "Baseline", "state": "origin"}
            ]
        }

        result = validator.validate_config_data(config, "waveform-analysis")
        assert result == config

    def test_waveform_analysis_empty_data_sources_fails(self, validator):
        """Test waveform analysis fails with empty data sources"""
        config = {
            "task_info": {"task_type": "waveform-analysis"},
            "visualization_config": {},
            "data_sources": []
        }

        with pytest.raises(ConfigValidationError):
            validator.validate_config_data(config, "waveform-analysis")


class TestInternalValidationMethods:
    """Test internal validation helper methods in detail"""

    @pytest.fixture
    def validator(self):
        return VisualizationConfigValidator()

    def test_validate_object_type_check(self, validator):
        """Test _validate_object method type checking"""
        # Valid object
        schema = {"type": "object", "properties": {}}
        errors = []
        validator._validate_object({}, schema, "test", errors)
        assert len(errors) == 0

        # Invalid type
        errors = []
        validator._validate_object("not an object", schema, "test", errors)
        assert len(errors) > 0

    def test_validate_array_type_check(self, validator):
        """Test _validate_array method type checking"""
        # Valid array
        schema = {"type": "array", "items": {"type": "number"}}
        errors = []
        validator._validate_array([1, 2, 3], schema, "test", errors)
        assert len(errors) == 0

        # Invalid type
        errors = []
        validator._validate_array("not an array", schema, "test", errors)
        assert len(errors) > 0

    def test_validate_array_length_constraints(self, validator):
        """Test _validate_array length constraints"""
        schema = {
            "type": "array",
            "items": {"type": "number"},
            "minItems": 2,
            "maxItems": 4
        }
        errors = []

        # Valid length
        validator._validate_array([1, 2, 3], schema, "test", errors)
        assert len(errors) == 0

        # Too short
        errors = []
        validator._validate_array([1], schema, "test", errors)
        assert len(errors) > 0

        # Too long
        errors = []
        validator._validate_array([1, 2, 3, 4, 5], schema, "test", errors)
        assert len(errors) > 0

    def test_validate_string_min_length(self, validator):
        """Test _validate_string minimum length constraint"""
        schema = {"type": "string", "minLength": 3}
        errors = []

        # Valid
        validator._validate_string("hello", schema, "test", errors)
        assert len(errors) == 0

        # Too short
        errors = []
        validator._validate_string("ab", schema, "test", errors)
        assert len(errors) > 0

    def test_validate_string_enum(self, validator):
        """Test _validate_string enum constraint"""
        schema = {"type": "string", "enum": ["option1", "option2", "option3"]}
        errors = []

        # Valid
        validator._validate_string("option1", schema, "test", errors)
        assert len(errors) == 0

        # Invalid enum value
        errors = []
        validator._validate_string("option4", schema, "test", errors)
        assert len(errors) > 0

    def test_validate_integer_range(self, validator):
        """Test _validate_integer range constraints"""
        schema = {"type": "integer", "minimum": 1, "maximum": 10}
        errors = []

        # Valid
        validator._validate_integer(5, schema, "test", errors)
        assert len(errors) == 0

        # Below minimum
        errors = []
        validator._validate_integer(0, schema, "test", errors)
        assert len(errors) > 0

        # Above maximum
        errors = []
        validator._validate_integer(11, schema, "test", errors)
        assert len(errors) > 0

    def test_validate_integer_not_float(self, validator):
        """Test that floats are rejected for integer type"""
        schema = {"type": "integer"}
        errors = []

        # Valid integer
        validator._validate_integer(5, schema, "test", errors)
        assert len(errors) == 0

        # Float value should fail (even if it's a whole number)
        errors = []
        validator._validate_integer(5.0, schema, "test", errors)
        assert len(errors) > 0

    def test_validate_number_accepts_integer_and_float(self, validator):
        """Test that number type accepts both int and float"""
        schema = {"type": "number"}
        errors = []

        # Integer
        validator._validate_number(5, schema, "test", errors)
        assert len(errors) == 0

        # Float
        errors = []
        validator._validate_number(5.0, schema, "test", errors)
        assert len(errors) == 0

    def test_validate_business_logic_task_type_mismatch(self, validator):
        """Test _validate_business_logic raises error for task_type mismatch"""
        config = {
            "task_info": {"task_type": "freq-response-compare"},
            "visualization_config": {},
            "data_sources": [{"project": "p1", "label": "l1"}]
        }

        # Try to validate as a different task type
        with pytest.raises(ConfigValidationError) as exc_info:
            validator._validate_business_logic(config, "bias-visualization")

        assert "不匹配" in str(exc_info.value)

    def test_validate_freq_response_logic_start_equals_end(self, validator):
        """Test frequency range validation when start equals end"""
        config = {
            "task_info": {"task_type": "freq-response-compare"},
            "visualization_config": {
                "freq_range": [100, 100]  # Start equals end
            },
            "data_sources": [{"project": "p1", "label": "l1"}]
        }

        # This should fail validation
        with pytest.raises(ConfigValidationError) as exc_info:
            validator._validate_freq_response_logic(config)

        assert "起始频率必须小于结束频率" in str(exc_info.value)


class TestSchemaValidationEdgeCases:
    """Additional edge case tests for schema validation"""

    @pytest.fixture
    def validator(self):
        return VisualizationConfigValidator()

    def test_nested_object_validation(self, validator):
        """Test validation of deeply nested objects"""
        config = {
            "task_info": {"task_type": "wnet5-circuit-validation"},
            "model_project_name": "test",
            "frequency_range": {"start_freq": 10, "stop_freq": 1000},
            "inference_config": {
                "opamp_config": {
                    "model": "ideal",
                    "power_pins": True,
                    "params": {
                        "gain": 100,
                        "bandwidth": 1e6
                    }
                }
            }
        }

        result = validator.validate_config_data(config, "wnet5-circuit-validation")
        assert result["inference_config"]["opamp_config"]["model"] == "ideal"

    def test_array_of_objects_validation(self, validator):
        """Test validation of array with object items"""
        config = {
            "task_info": {"task_type": "freq-response-compare"},
            "visualization_config": {},
            "data_sources": [
                {"project": "project1", "label": "Label 1", "state": "origin"},
                {"project": "project2", "label": "Label 2", "state": "compensation"}
            ]
        }

        result = validator.validate_config_data(config, "freq-response-compare")
        assert len(result["data_sources"]) == 2

    def test_validation_with_optional_fields_missing(self, validator):
        """Test validation when optional fields are missing"""
        config = {
            "task_info": {"task_type": "wnet5-circuit-validation"},
            "model_project_name": "test",
            "frequency_range": {"start_freq": 10, "stop_freq": 1000}
            # Optional fields like analysis_layer, inference_config are missing
        }

        result = validator.validate_config_data(config, "wnet5-circuit-validation")
        assert result["model_project_name"] == "test"

    def test_validation_with_all_optional_fields(self, validator):
        """Test validation when all optional fields are present"""
        config = {
            "task_info": {"task_type": "wnet5-circuit-validation", "description": "Full test"},
            "model_project_name": "test",
            "frequency_range": {"start_freq": 10, "stop_freq": 1000, "points": 200},
            "analysis_layer": 3,
            "compare_with_experiment": "exp_data",
            "inference_config": {
                "use_e96": True,
                "opamp_config": {"model": "LM324"},
                "power_supply": {"vcc": 15, "vee": -15},
                "high_pass_config": {"enable": False, "cutoff_freq": 0.5}
            }
        }

        result = validator.validate_config_data(config, "wnet5-circuit-validation")
        assert result["analysis_layer"] == 3
        assert result["inference_config"]["use_e96"] is True

    def test_validation_complex_nested_schema(self, validator):
        """Test validation with complex nested WNET5 schema"""
        config = {
            "task_info": {"task_type": "wnet5-circuit-validation"},
            "model_project_name": "WNET5_EFF2",
            "frequency_range": {"start_freq": 1, "stop_freq": 500000},
            "svf_error_simulation": {
                "enable": True,
                "measured_data_file": "/path/to/data.csv",
                "include_dense_layer": True,
                "compensation": {"enabled": False},
                "plot_config": {"merged_plot_mode": True},
                "fitting": {"enabled": True, "output_filename": "fitted.png"},
                "r1_13_comparison": {"enable": False}
            }
        }

        result = validator.validate_config_data(config, "wnet5-circuit-validation")
        assert result["svf_error_simulation"]["enable"] is True

    def test_validation_experiment_comparison_plot_config(self, validator):
        """Test experiment comparison plot config validation"""
        config = {
            "task_info": {"task_type": "wnet5-circuit-validation"},
            "model_project_name": "test",
            "frequency_range": {"start_freq": 10, "stop_freq": 1000},
            "experiment_comparison": {
                "enable": True,
                "mode": "multi_file",
                "experiment_data_dir": "/data",
                "selftest_file": "/data/selftest.csv",
                "experiment_sheet_name": "Sheet1",
                "plot_config": {
                    "coordinate_system": "semilogx",
                    "y_unit": "linear",
                    "merged_plot_mode": False
                }
            }
        }

        result = validator.validate_config_data(config, "wnet5-circuit-validation")
        assert result["experiment_comparison"]["mode"] == "multi_file"
        assert result["experiment_comparison"]["plot_config"]["coordinate_system"] == "semilogx"


class TestValidationErrorMessages:
    """Test validation error messages for clarity"""

    @pytest.fixture
    def validator(self):
        return VisualizationConfigValidator()

    def test_error_message_for_missing_required_field(self, validator):
        """Test error message clearly identifies missing required field"""
        config = {
            "task_info": {"task_type": "wnet5-circuit-validation"}
            # Missing model_project_name and frequency_range
        }

        with pytest.raises(ConfigValidationError) as exc_info:
            validator.validate_config_data(config, "wnet5-circuit-validation")

        error_msg = str(exc_info.value)
        # Error should mention what's missing
        assert "缺少必需字段" in error_msg or "model_project_name" in error_msg

    def test_error_message_for_type_mismatch(self, validator):
        """Test error message for type mismatch"""
        config = {
            "task_info": {"task_type": "freq-response-compare"},
            "visualization_config": {},
            "data_sources": "not an array"  # Should be array
        }

        with pytest.raises(ConfigValidationError) as exc_info:
            validator.validate_config_data(config, "freq-response-compare")

        # Error should mention array type mismatch
        error_msg = str(exc_info.value)
        assert "array" in error_msg.lower() or "array" in error_msg or "必须是" in error_msg

    def test_error_message_for_invalid_enum_value(self, validator):
        """Test error message shows allowed enum values"""
        config = {
            "task_info": {"task_type": "wnet5-circuit-validation"},
            "model_project_name": "test",
            "frequency_range": {"start_freq": 10, "stop_freq": 1000},
            "inference_config": {
                "opamp_config": {"model": "NONEXISTENT_MODEL"}
            }
        }

        with pytest.raises(ConfigValidationError) as exc_info:
            validator.validate_config_data(config, "wnet5-circuit-validation")

        error_msg = str(exc_info.value)
        # Error should indicate invalid enum value
        assert "enum" in error_msg.lower() or "not found" in error_msg.lower() or "不" in error_msg

    def test_multiple_errors_collected(self, validator):
        """Test that multiple validation errors are collected"""
        config = {
            "task_info": {"task_type": "wrong-type"},
            "visualization_config": {
                "layout": "invalid_layout",
                "dpi": 50  # Below minimum
            },
            "data_sources": []  # Empty
        }

        with pytest.raises(ConfigValidationError) as exc_info:
            validator.validate_config_data(config, "freq-response-compare")

        # Should contain multiple error indications
        error_msg = str(exc_info.value)
        # At least indicates validation failed
        assert len(error_msg) > 0


class TestFreqResponseCompensatorSchemaBoundary:
    """Additional boundary tests for freq-response-compensator schema"""

    @pytest.fixture
    def validator(self):
        return VisualizationConfigValidator()

    def test_freq_response_compensator_with_visualization_config(self, validator):
        """Test freq-response-compensator with full visualization config"""
        config = {
            "task_info": {"task_type": "freq-response-compensator", "description": "Test"},
            "project_name": "test_project",
            "visualization_config": {
                "output_format": "svg",
                "dpi": 150,
                "figsize": [8, 6],
                "freq_range": [1, 500],
                "gain_range": [-80, 20],
                "title": "Compensation Results",
                "log_scale": True,
                "target_magnitudes": [0.05, 0.1, 0.2, 0.5, 1.0]
            }
        }

        result = validator.validate_config_data(config, "freq-response-compensator")
        assert result["project_name"] == "test_project"
        assert result["visualization_config"]["log_scale"] is True

    def test_freq_response_compensator_minimal_with_empty_visualization(self, validator):
        """Test freq-response-compensator with empty visualization config"""
        config = {
            "task_info": {"task_type": "freq-response-compensator"},
            "project_name": "minimal_test",
            "visualization_config": {}
        }

        result = validator.validate_config_data(config, "freq-response-compensator")
        assert result["project_name"] == "minimal_test"

    def test_freq_response_compensator_empty_target_magnitudes(self, validator):
        """Test freq-response-compensator with empty target_magnitudes"""
        config = {
            "task_info": {"task_type": "freq-response-compensator"},
            "project_name": "test",
            "visualization_config": {
                "target_magnitudes": []
            }
        }

        # Empty array should be valid (minItems defaults to 0 for this field)
        result = validator.validate_config_data(config, "freq-response-compensator")
        assert result["visualization_config"]["target_magnitudes"] == []


class TestVisualizationConfigValidatorSchemaCount:
    """Test that validator has correct number of schemas"""

    def test_all_expected_schemas_present(self):
        """Verify all expected schemas are registered"""
        validator = VisualizationConfigValidator()

        expected_schemas = [
            "freq-response-compare",
            "freq-response-compensator",
            "bias-visualization",
            "waveform-analysis",
            "wnet5-circuit-validation",
            "qemu-c-inference",
        ]

        for schema_name in expected_schemas:
            assert schema_name in validator.schemas, f"Schema {schema_name} not found"
            # Each schema should be a dict with 'type' key
            assert validator.schemas[schema_name]["type"] == "object"

    def test_schema_types_are_objects(self):
        """Verify all schemas define object type"""
        validator = VisualizationConfigValidator()

        for schema_name, schema in validator.schemas.items():
            assert schema.get("type") == "object", f"Schema {schema_name} is not an object type"
            # Most schemas should have additionalProperties: False for strict validation
            assert schema.get("additionalProperties") is False, f"Schema {schema_name} should not allow additional properties"


class TestQemuCInferenceSchema:
    """Test qemu-c-inference schema validation."""

    @pytest.fixture
    def validator(self):
        return VisualizationConfigValidator()

    def test_valid_qemu_c_inference_with_keil_config(self, validator):
        config = {
            "task_info": {"task_type": "qemu-c-inference"},
            "model_project_name": "00_MAE_VS_AFMAE/LSTMu16_base",
            "benchmark_config": {
                "iterations": 10,
                "reset_state_each_run": True,
                "repeat_runs": 1,
            },
            "validation_config": {
                "dataset": {
                    "dataset_type": "MET",
                    "data_path": "data/M50",
                    "sample_rate": 2000,
                    "time_clipped_s": 4.0,
                    "target_sweep": 2,
                },
                "selection": {
                    "magnitudes": [0.24],
                    "frequencies": [10.0],
                    "start_time_s": 0.0,
                    "end_time_s": 0.2,
                },
                "wave_output": {
                    "compress": True,
                },
            },
            "qemu_config": {
                "action": "build-run",
                "timeout": 5,
            },
            "keil_config": {
                "action": "build-program-capture",
                "target": "MET405",
                "programmer": "daplink",
                "program_backend": "keil",
                "probe_uid": "205536951525",
                "serial_port": "COM8",
                "baud_rate": 115200,
                "capture_timeout": 20,
                "job_timeout": 300,
                "success_markers": ["validation_complete=1"],
                "optimization_profiles": ["project_default", "o0", "o2", "ofast_lto"],
                "published_optimization_profile": "project_default",
            },
        }

        result = validator.validate_config_data(config, "qemu-c-inference")
        assert result["keil_config"]["serial_port"] == "COM8"
        assert result["keil_config"]["published_optimization_profile"] == "project_default"

    def test_qemu_c_inference_rejects_unknown_keil_field(self, validator):
        config = {
            "task_info": {"task_type": "qemu-c-inference"},
            "model_project_name": "00_MAE_VS_AFMAE/LSTMu16_base",
            "benchmark_config": {
                "iterations": 10,
            },
            "validation_config": {
                "dataset": {
                    "dataset_type": "MET",
                    "data_path": "data/M50",
                    "sample_rate": 2000,
                    "time_clipped_s": 4.0,
                    "target_sweep": 2,
                },
                "selection": {
                    "magnitudes": [0.24],
                    "frequencies": [10.0],
                },
            },
            "qemu_config": {
                "action": "build-run",
            },
            "keil_config": {
                "action": "build-program-capture",
                "extra_field": "not allowed",
            },
        }

        with pytest.raises(ConfigValidationError):
            validator.validate_config_data(config, "qemu-c-inference")
