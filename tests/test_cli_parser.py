"""
CLI Parser 单元测试
"""

import pytest
import json
import tempfile
import os
from unittest.mock import patch, mock_open

from core.cli_parser import (
    parse_arguments, 
    CLIArgs, 
    CLIConfig,
    TaskType,
    ArgumentParsingError,
    ArgumentValidator,
    load_config,
    get_all_project_dirs
)


class TestTaskType:
    """测试任务类型枚举"""
    
    def test_task_type_values(self):
        """测试任务类型的值"""
        assert TaskType.TRAIN.value == "train"
        assert TaskType.EVALUATE.value == "evaluate"
        assert TaskType.INFERENCE.value == "inference"
        assert TaskType.ANALYZE.value == "analyze"


class TestCLIArgs:
    """测试CLI参数数据类"""
    
    def test_cli_args_creation(self):
        """测试CLIArgs创建"""
        args = CLIArgs(
            task_type=TaskType.TRAIN,
            project_names=["test_project"],
            force_mode=True,
            layers_param=5
        )
        assert args.task_type == TaskType.TRAIN
        assert args.project_names == ["test_project"]
        assert args.force_mode is True
        assert args.layers_param == 5
        assert args.bias_method == "auto"  # 默认值
        assert args.bias_params == {}  # 默认值


class TestCLIConfig:
    """测试CLI配置类"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = CLIConfig()
        assert config.default_project == "WNET5q1h2u6l3"
        assert config.projects_dir == "projects"
        assert config.default_bias_method == "auto"
        assert config.default_force_mode is False
    
    def test_config_from_file(self):
        """测试从文件加载配置"""
        yaml_content = """
        default_project: "test_project"
        default_bias_method: "frequency_domain"
        default_force_mode: true
        """
        
        with patch("builtins.open", mock_open(read_data=yaml_content)):
            with patch("yaml.safe_load") as mock_yaml:
                mock_yaml.return_value = {
                    "default_project": "test_project",
                    "default_bias_method": "frequency_domain",
                    "default_force_mode": True
                }
                
                config = CLIConfig.from_file("test_config.yaml")
                assert config.default_project == "test_project"
                assert config.default_bias_method == "frequency_domain"
                assert config.default_force_mode is True


class TestArgumentValidator:
    """测试参数验证器"""
    
    def test_validate_layers_valid(self):
        """测试有效层数验证"""
        ArgumentValidator.validate_layers(5)  # 应该不抛出异常
        ArgumentValidator.validate_layers(None)  # None 应该是有效的
    
    def test_validate_layers_invalid(self):
        """测试无效层数验证"""
        with pytest.raises(ArgumentParsingError):
            ArgumentValidator.validate_layers(0)
        
        with pytest.raises(ArgumentParsingError):
            ArgumentValidator.validate_layers(-1)
    
    def test_validate_bias_params_valid(self):
        """测试有效偏置参数验证"""
        result = ArgumentValidator.validate_bias_params('{"key": "value"}')
        assert result == {"key": "value"}
        
        result = ArgumentValidator.validate_bias_params(None)
        assert result == {}
    
    def test_validate_bias_params_invalid(self):
        """测试无效偏置参数验证"""
        with pytest.raises(ArgumentParsingError):
            ArgumentValidator.validate_bias_params('invalid json')
    
    @patch('core.cli_parser.get_all_project_dirs')
    def test_validate_project_name_wildcard(self, mock_get_dirs):
        """测试通配符项目名称验证"""
        mock_get_dirs.return_value = ["project1", "project2", "test_project"]
        
        result = ArgumentValidator.validate_project_name("test_*")
        assert result == ["test_project"]
        
        # 测试没有匹配的情况
        with pytest.raises(ArgumentParsingError):
            ArgumentValidator.validate_project_name("nonexistent_*")
    
    def test_validate_project_name_simple(self):
        """测试简单项目名称验证"""
        result = ArgumentValidator.validate_project_name("simple_project")
        assert result == ["simple_project"]


class TestParseArguments:
    """测试参数解析函数"""
    
    def test_parse_train_task(self):
        """测试训练任务解析"""
        args = parse_arguments(['-t', 'test_project'])
        assert args.task_type == TaskType.TRAIN
        assert args.project_names == ['test_project']
    
    def test_parse_evaluate_task(self):
        """测试评估任务解析"""
        args = parse_arguments(['-e', 'test_project'])
        assert args.task_type == TaskType.EVALUATE
        assert args.project_names == ['test_project']
    
    def test_parse_inference_with_layers(self):
        """测试推理任务与层数参数"""
        args = parse_arguments(['-i', 'test_project', '--layers', '5'])
        assert args.task_type == TaskType.INFERENCE
        assert args.project_names == ['test_project']
        assert args.layers_param == 5
    
    def test_parse_analyze_with_bias_method(self):
        """测试分析任务与偏置方法"""
        args = parse_arguments(['-a', 'test_project', '--bias-method', 'frequency_domain'])
        assert args.task_type == TaskType.ANALYZE
        assert args.project_names == ['test_project']
        assert args.bias_method == 'frequency_domain'
    
    def test_parse_bias_params_json(self):
        """测试偏置参数JSON解析"""
        bias_params = '{"param1": "value1", "param2": 42}'
        args = parse_arguments(['-a', 'test_project', '--bias-params', bias_params])
        assert args.bias_params == {"param1": "value1", "param2": 42}
    
    def test_parse_visualization_task(self):
        """测试可视化任务解析"""
        args = parse_arguments([
            '--bias-viz', 'test_project',
            '--baseline', '/path/to/baseline',
            '--compensated', '/path/to/compensated',
            '--vis-output', '/path/to/output'
        ])
        assert args.task_type == TaskType.BIAS_VISUALIZATION
        assert args.baseline_dir == '/path/to/baseline'
        assert args.compensated_dir == '/path/to/compensated'
        assert args.vis_output_dir == '/path/to/output'
    
    def test_parse_force_and_quick_flags(self):
        """测试强制模式和快速模式标志"""
        args = parse_arguments(['-i', 'test_project', '-f', '-q'])
        assert args.force_mode is True
        assert args.quick_inference is True
    
    @patch('core.cli_parser.get_all_project_dirs')
    def test_parse_all_projects(self, mock_get_dirs):
        """测试所有项目标志"""
        mock_get_dirs.return_value = ["project1", "project2"]
        
        args = parse_arguments(['-e', '--all-projects'])
        assert args.project_names == ["project1", "project2"]
    
    def test_parse_invalid_layers(self):
        """测试无效层数参数"""
        with pytest.raises(ArgumentParsingError):
            parse_arguments(['-i', 'test_project', '--layers', '0'])
        
        with pytest.raises(ArgumentParsingError):
            parse_arguments(['-i', 'test_project', '--layers', '-1'])
    
    def test_parse_invalid_bias_params(self):
        """测试无效偏置参数"""
        with pytest.raises(ArgumentParsingError):
            parse_arguments(['-a', 'test_project', '--bias-params', 'invalid json'])


class TestConfigurationLoading:
    """测试配置加载功能"""
    
    @patch('os.path.exists')
    @patch('core.cli_parser.CLIConfig.from_file')
    def test_load_config_from_project_root(self, mock_from_file, mock_exists):
        """测试从项目根目录加载配置"""
        mock_exists.side_effect = lambda path: path == 'cli_config.yaml'
        mock_from_file.return_value = CLIConfig(default_project="from_file")
        
        config = load_config()
        assert config.default_project == "from_file"
        mock_from_file.assert_called_once_with('cli_config.yaml')
    
    @patch('os.path.exists')
    @patch('core.cli_parser.CLIConfig.from_file')
    def test_load_config_from_core_dir(self, mock_from_file, mock_exists):
        """测试从核心目录加载配置"""
        mock_exists.side_effect = lambda path: path == 'core/cli_defaults.yaml'
        mock_from_file.return_value = CLIConfig(default_project="from_core")
        
        config = load_config()
        assert config.default_project == "from_core"
        mock_from_file.assert_called_once_with('core/cli_defaults.yaml')
    
    @patch('os.path.exists')
    def test_load_config_default(self, mock_exists):
        """测试使用默认配置"""
        mock_exists.return_value = False
        
        config = load_config()
        assert config.default_project == "WNET5q1h2u6l3"  # 默认值


class TestGetAllProjectDirs:
    """测试获取所有项目目录功能"""
    
    @patch('os.path.exists')
    @patch('os.scandir')
    def test_get_all_project_dirs(self, mock_scandir, mock_exists):
        """测试获取项目目录"""
        mock_exists.return_value = True
        
        # 模拟目录条目
        class MockDirEntry:
            def __init__(self, name, is_dir=True):
                self.name = name
                self._is_dir = is_dir
            
            def is_dir(self):
                return self._is_dir
        
        mock_scandir.return_value = [
            MockDirEntry("project1", True),
            MockDirEntry("project2", True),
            MockDirEntry("file.txt", False)
        ]
        
        result = get_all_project_dirs("test_projects")
        assert result == ["project1", "project2"]
    
    @patch('os.path.exists')
    def test_get_all_project_dirs_nonexistent(self, mock_exists):
        """测试不存在的项目目录"""
        mock_exists.return_value = False
        
        result = get_all_project_dirs("nonexistent")
        assert result == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])