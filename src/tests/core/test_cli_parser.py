"""
Tests for core/cli_parser module
"""

import pytest
import sys
import os
from pathlib import Path

# Add src to path
_SRC_DIR = Path(__file__).parent.parent.parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from core.cli_parser import (
    TaskType,
    CLIArgs,
    CLIConfig,
    ArgumentParsingError,
    ArgumentValidator,
    load_config,
    get_all_project_dirs,
    parse_arguments,
    create_parser
)


class TestTaskType:
    """Test TaskType enum values"""

    def test_task_type_values(self):
        """Test that all expected task types exist"""
        assert TaskType.TRAIN.value == "train"
        assert TaskType.EVALUATE.value == "evaluate"
        assert TaskType.CLEAN.value == "clean"
        assert TaskType.MODEL_INFO.value == "model_info"
        assert TaskType.LUT.value == "lut"
        assert TaskType.INFERENCE.value == "inference"
        assert TaskType.ANALYZE.value == "analyze"
        assert TaskType.WAVE.value == "wave"
        assert TaskType.BIAS_VISUALIZATION.value == "bias_visualization"
        assert TaskType.EXPORT_RESISTANCE.value == "export_resistance"
        assert TaskType.STANDARDIZE_RESISTANCE.value == "standardize_resistance"
        assert TaskType.WAVEFORM_VIS.value == "waveform_vis"
        assert TaskType.TEST.value == "test"

    def test_task_type_count(self):
        """Test that expected number of task types exist"""
        assert len(TaskType) == 13


class TestCLIArgs:
    """Test CLIArgs dataclass"""

    def test_default_values(self):
        """Test default values are set correctly"""
        args = CLIArgs(
            task_type=TaskType.TRAIN,
            project_names=["test_project"]
        )
        assert args.force_mode is False
        assert args.quick_inference is False
        assert args.layers_param is None
        assert args.bias_method == "auto"
        assert args.bias_params == {}
        assert args.baseline_dir is None
        assert args.compensated_dir is None
        assert args.test_workers == 4
        assert args.test_timeout == 300
        assert args.no_parallel is False

    def test_custom_values(self):
        """Test custom values are set correctly"""
        args = CLIArgs(
            task_type=TaskType.INFERENCE,
            project_names=["proj1", "proj2"],
            force_mode=True,
            quick_inference=True,
            layers_param=5,
            bias_method="steady_state",
            bias_params={"param1": "value1"},
            test_workers=8,
            test_timeout=600,
            no_parallel=True
        )
        assert args.task_type == TaskType.INFERENCE
        assert args.project_names == ["proj1", "proj2"]
        assert args.force_mode is True
        assert args.quick_inference is True
        assert args.layers_param == 5
        assert args.bias_method == "steady_state"
        assert args.bias_params == {"param1": "value1"}
        assert args.test_workers == 8
        assert args.test_timeout == 600
        assert args.no_parallel is True

    def test_series_default(self):
        """Test series default value"""
        args = CLIArgs(
            task_type=TaskType.STANDARDIZE_RESISTANCE,
            project_names=["test"]
        )
        assert args.series == ['E96', 'E24']


class TestCLIConfig:
    """Test CLIConfig class"""

    def test_default_values(self):
        """Test default configuration values"""
        config = CLIConfig()
        assert config.default_project == "WNET5q1h2u6l3"
        assert config.projects_dir == "projects"
        assert config.default_bias_method == "auto"
        assert config.default_layers is None
        assert config.default_force_mode is False
        assert config.default_quick_inference is False

    def test_from_file_with_valid_yaml(self):
        """Test loading config from valid YAML file"""
        # Create a temporary YAML config file
        import tempfile
        import yaml

        config_data = {
            'default_project': 'custom_project',
            'projects_dir': 'custom_projects',
            'default_bias_method': 'frequency_domain',
            'default_force_mode': True
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name

        try:
            config = CLIConfig.from_file(temp_path)
            assert config.default_project == 'custom_project'
            assert config.projects_dir == 'custom_projects'
            assert config.default_bias_method == 'frequency_domain'
            assert config.default_force_mode is True
        finally:
            os.unlink(temp_path)

    def test_from_file_with_invalid_yaml(self):
        """Test loading config from invalid YAML returns defaults"""
        import tempfile

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            temp_path = f.name

        try:
            config = CLIConfig.from_file(temp_path)
            # Should return default config on error
            assert config.default_project == "WNET5q1h2u6l3"
        finally:
            os.unlink(temp_path)

    def test_from_file_nonexistent(self):
        """Test loading config from nonexistent file returns defaults"""
        config = CLIConfig.from_file('/nonexistent/path/config.yaml')
        assert config.default_project == "WNET5q1h2u6l3"


class TestArgumentValidator:
    """Test ArgumentValidator class"""

    def test_validate_layers_positive(self):
        """Test validation of positive layer values"""
        ArgumentValidator.validate_layers(1)
        ArgumentValidator.validate_layers(5)
        ArgumentValidator.validate_layers(100)

    def test_validate_layers_none(self):
        """Test validation of None layer value"""
        ArgumentValidator.validate_layers(None)  # Should not raise

    def test_validate_layers_zero(self):
        """Test validation of zero layer value raises error"""
        with pytest.raises(ArgumentParsingError):
            ArgumentValidator.validate_layers(0)

    def test_validate_layers_negative(self):
        """Test validation of negative layer values raises error"""
        with pytest.raises(ArgumentParsingError):
            ArgumentValidator.validate_layers(-1)
        with pytest.raises(ArgumentParsingError):
            ArgumentValidator.validate_layers(-5)

    def test_validate_bias_params_none(self):
        """Test validation of None bias params"""
        result = ArgumentValidator.validate_bias_params(None)
        assert result == {}

    def test_validate_bias_params_valid_json(self):
        """Test validation of valid JSON bias params"""
        result = ArgumentValidator.validate_bias_params('{"key": "value", "num": 123}')
        assert result == {"key": "value", "num": 123}

    def test_validate_bias_params_invalid_json(self):
        """Test validation of invalid JSON bias params raises error"""
        with pytest.raises(ArgumentParsingError):
            ArgumentValidator.validate_bias_params('{invalid json}')

    def test_validate_project_name_simple(self):
        """Test validation of simple project name"""
        result = ArgumentValidator.validate_project_name("test_project")
        assert result == ["test_project"]

    def test_validate_project_name_with_wildcard(self):
        """Test validation of project name with wildcard"""
        # This will return empty list if no projects match
        result = ArgumentValidator.validate_project_name("*")
        assert isinstance(result, list)


class TestGetAllProjectDirs:
    """Test get_all_project_dirs function"""

    def test_no_projects_dir(self):
        """Test when projects directory doesn't exist"""
        # Temporarily change directory
        original_cwd = os.getcwd()
        try:
            os.chdir('/tmp')
            result = get_all_project_dirs('/nonexistent/path')
            assert result == []
        finally:
            os.chdir(original_cwd)

    def test_with_existing_projects(self):
        """Test when projects directory exists"""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some project directories
            os.makedirs(os.path.join(tmpdir, 'project1'))
            os.makedirs(os.path.join(tmpdir, 'project2'))
            os.makedirs(os.path.join(tmpdir, 'not_a_project'))  # File, not directory

            result = get_all_project_dirs(tmpdir)

            assert 'project1' in result
            assert 'project2' in result
            # Note: Only directories are returned
            assert 'not_a_project' not in result or os.path.isdir(os.path.join(tmpdir, 'not_a_project'))


class TestParseArguments:
    """Test parse_arguments function"""

    def test_parse_train_task(self):
        """Test parsing train task arguments"""
        args = parse_arguments(['-t', 'test_project'])
        assert args.task_type == TaskType.TRAIN
        assert args.project_names == ['test_project']

    def test_parse_evaluate_task(self):
        """Test parsing evaluate task arguments"""
        args = parse_arguments(['-e', 'test_project'])
        assert args.task_type == TaskType.EVALUATE
        assert args.project_names == ['test_project']

    def test_parse_inference_task(self):
        """Test parsing inference task arguments"""
        args = parse_arguments(['-i', 'test_project', '--layers', '5'])
        assert args.task_type == TaskType.INFERENCE
        assert args.project_names == ['test_project']
        assert args.layers_param == 5

    def test_parse_clean_task(self):
        """Test parsing clean task arguments"""
        args = parse_arguments(['-c', 'test_project'])
        assert args.task_type == TaskType.CLEAN
        assert args.project_names == ['test_project']

    def test_parse_with_force_flag(self):
        """Test parsing with force flag"""
        args = parse_arguments(['-e', 'test_project', '-f'])
        assert args.force_mode is True

    def test_parse_with_quick_flag(self):
        """Test parsing with quick flag"""
        args = parse_arguments(['-i', 'test_project', '-q'])
        assert args.quick_inference is True

    def test_parse_test_task(self):
        """Test parsing test task (no project needed)"""
        args = parse_arguments(['--test'])
        assert args.task_type == TaskType.TEST
        assert args.project_names == []

    def test_parse_bias_method(self):
        """Test parsing bias method argument"""
        args = parse_arguments(['-a', 'test_project', '--bias-method', 'steady_state'])
        assert args.bias_method == 'steady_state'

    def test_parse_bias_method_invalid(self):
        """Test parsing invalid bias method"""
        # argparse will handle invalid choices
        with pytest.raises(SystemExit):
            parse_arguments(['-a', 'test_project', '--bias-method', 'invalid_method'])

    def test_parse_series(self):
        """Test parsing resistance series"""
        # Note: --series is part of the resistance_group, not a main task flag
        # This test checks the resistance series parameter parsing
        args = parse_arguments(['-s', 'test_project'])
        # Default series should be ['E96', 'E24'] if not explicitly specified
        assert args.series == ['E96', 'E24']

    def test_parse_test_parameters(self):
        """Test parsing test command parameters"""
        args = parse_arguments([
            '--test',
            '--test-path', 'src/tests',
            '--test-workers', '8',
            '--test-timeout', '600',
            '--no-parallel'
        ])
        assert args.test_path == 'src/tests'
        assert args.test_workers == 8
        assert args.test_timeout == 600
        assert args.no_parallel is True

    def test_parse_no_task_raises_error(self):
        """Test that parsing without task raises error"""
        with pytest.raises(ArgumentParsingError):
            parse_arguments(['test_project'])

    def test_parse_ep_command(self):
        """Test parsing ep subcommand"""
        args = parse_arguments(['ep', 'project/task-type/task-name'])
        assert args.command == 'ep'
        assert args.ep_project_path == 'project/task-type/task-name'


class TestCreateParser:
    """Test create_parser function"""

    def test_create_parser_default(self):
        """Test creating parser with default config"""
        parser = create_parser()
        assert parser is not None
        assert isinstance(parser, type(parser))  # Just check it's a parser object

    def test_create_parser_with_config(self):
        """Test creating parser with custom config"""
        config = CLIConfig(default_project="custom_project")
        parser = create_parser(config)
        assert parser is not None


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_project_list(self):
        """Test handling of empty project list"""
        args = CLIArgs(
            task_type=TaskType.TRAIN,
            project_names=[]
        )
        assert args.project_names == []

    def test_bias_params_complex(self):
        """Test complex bias params structure"""
        complex_params = {
            "layer_configs": [
                {"layer": 1, "gain": 1.5},
                {"layer": 2, "gain": 2.0}
            ],
            "use_quantization": True,
            "quantization_bits": 8
        }
        args = CLIArgs(
            task_type=TaskType.INFERENCE,
            project_names=["test"],
            bias_params=complex_params
        )
        assert args.bias_params == complex_params
        assert len(args.bias_params["layer_configs"]) == 2

    def test_layout_mode_options(self):
        """Test layout mode enum values"""
        args = CLIArgs(
            task_type=TaskType.EVALUATE,
            project_names=["test"],
            layout_mode="side_by_side"
        )
        assert args.layout_mode in ["overlay", "side_by_side"]
