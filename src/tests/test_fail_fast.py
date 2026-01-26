"""
测试"快速失败"机制
确保在缺少必要文件时系统能正确报错而不是使用假数据
"""
import pytest
import os
import sys
import tempfile
import shutil
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from cli import ProjectManager
from core.model_engine import ModelEngine
from inference.processor import InferenceProcessor
from config import Config


class TestFailFast:
    """测试快速失败机制"""
    
    @pytest.fixture
    def temp_project_dir(self):
        """创建临时项目目录"""
        temp_dir = tempfile.mkdtemp()
        project_name = "test_project"
        project_path = os.path.join(temp_dir, "projects", project_name)
        os.makedirs(project_path, exist_ok=True)
        
        # 创建配置文件
        config_path = os.path.join(project_path, "config.json")
        config = Config()
        config.save_to_json(config_path)
        
        yield project_path
        
        # 清理
        shutil.rmtree(temp_dir)
    
    def test_missing_weights_fails(self, temp_project_dir):
        """测试缺少权重文件时是否正确报错"""
        # 创建ProjectManager但不创建权重文件
        os.chdir(os.path.dirname(temp_project_dir))
        project_name = os.path.basename(temp_project_dir)
        
        with pytest.raises(FileNotFoundError) as exc_info:
            pm = ProjectManager(project_name)
            pm._validate_inference_prerequisites()
        
        assert "未找到任何模型权重文件" in str(exc_info.value)
    
    def test_missing_input_fails(self, temp_project_dir):
        """测试缺少输入文件时是否正确报错"""
        os.chdir(os.path.dirname(temp_project_dir))
        project_name = os.path.basename(temp_project_dir)
        
        # 创建一个假的权重文件以通过权重检查
        data_dir = os.path.join(temp_project_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        weight_file = os.path.join(data_dir, "best.weights.h5")
        Path(weight_file).touch()
        
        pm = ProjectManager(project_name)
        
        # 测试_generate_inference_data中的输入文件检查
        with pytest.raises(FileNotFoundError) as exc_info:
            pm._generate_inference_data(data_dir)
        
        assert "推理输入文件不存在" in str(exc_info.value)
    
    def test_no_silent_fallback(self, temp_project_dir):
        """测试不会静默使用替代文件"""
        os.chdir(os.path.dirname(temp_project_dir))
        project_name = os.path.basename(temp_project_dir)
        
        # 创建output文件但不创建input文件
        output_file = "temp/dataset_output_original.wave"
        os.makedirs("temp", exist_ok=True)
        Path(output_file).touch()
        
        pm = ProjectManager(project_name)
        
        # 应该报错而不是使用output文件
        with pytest.raises(FileNotFoundError) as exc_info:
            # 由于修改后的代码不会尝试使用output文件，应该直接报错
            pm._generate_inference_data("")
        
        assert "dataset_input.wave" in str(exc_info.value)
        assert "dataset_output_original" not in str(exc_info.value)
    
    def test_model_engine_weight_loading_fails(self):
        """测试ModelEngine权重加载失败时报错"""
        from unittest.mock import Mock, patch
        
        # 创建mock对象
        mock_model = Mock()
        mock_model.best_weights_file = "/nonexistent/path/weights.h5"
        
        engine = ModelEngine(Mock())
        engine.model_comp = mock_model
        
        # 测试load_best_weights
        with pytest.raises(FileNotFoundError) as exc_info:
            engine.load_best_weights()
        
        assert "权重文件不存在" in str(exc_info.value)
    
    def test_inference_processor_no_random_weights(self, temp_project_dir):
        """测试InferenceProcessor不会使用随机权重"""
        from unittest.mock import Mock, patch
        
        # 使用真实的项目路径
        os.chdir(os.path.dirname(temp_project_dir))
        project_name = os.path.basename(temp_project_dir)
        
        processor = InferenceProcessor(project_name)
        
        # Mock model_engine的load方法使其抛出异常
        with patch.object(processor.model_engine, 'load_val_best_weights') as mock_val:
            with patch.object(processor.model_engine, 'load_best_weights') as mock_best:
                mock_val.side_effect = Exception("验证集权重不存在")
                mock_best.side_effect = Exception("训练集权重不存在")
                
                # 应该抛出RuntimeError而不是继续
                with pytest.raises(RuntimeError) as exc_info:
                    processor._load_best_weights()
                
                assert "无法加载模型权重，推理无法继续" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])