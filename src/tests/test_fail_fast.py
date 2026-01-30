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

from core.project_manager import ProjectManager
from config import Config


class TestFailFast:
    """测试快速失败机制"""

    def test_missing_config_raises_error(self):
        """测试缺少配置文件时是否正确报错"""
        # 创建一个空的临时目录（没有配置文件）
        empty_dir = tempfile.mkdtemp(prefix="test_no_config_")
        try:
            # 应该抛出异常
            with pytest.raises((FileNotFoundError, Exception, ValueError)):
                pm = ProjectManager(project_path=empty_dir)
        finally:
            shutil.rmtree(empty_dir)

    def test_config_initialization(self):
        """测试Config初始化"""
        temp_dir = tempfile.mkdtemp(prefix="test_config_")
        try:
            config_file = os.path.join(temp_dir, "config.json")
            config = Config()
            config.save_to_json(config_file)

            # 验证配置文件存在
            assert os.path.exists(config_file)

            # 验证可以重新加载
            config2 = Config()
            config2.load_from_json(config_file)
            assert config2 is not None
        finally:
            shutil.rmtree(temp_dir)

    def test_project_manager_init_with_config(self):
        """测试带配置文件的ProjectManager初始化"""
        temp_dir = tempfile.mkdtemp(prefix="test_pm_init_")
        try:
            # 创建项目结构
            os.makedirs(os.path.join(temp_dir, "data"), exist_ok=True)

            # 创建配置文件
            config_file = os.path.join(temp_dir, "config.json")
            config_data = {
                "using_gpu": False,
                "use_model": "Dense",
                "learning_rate": 0.01,
                "epoch_train": 10,
                "sample_rate": 1000
            }
            import json
            with open(config_file, 'w') as f:
                json.dump(config_data, f)

            # 创建ProjectManager
            pm = ProjectManager(project_path=temp_dir)
            assert pm is not None
            assert pm.project_path == temp_dir
            assert pm.config is not None
        finally:
            shutil.rmtree(temp_dir)

    def test_project_path_setter(self):
        """测试project_path属性设置"""
        temp_dir = tempfile.mkdtemp(prefix="test_pm_path_")
        try:
            # 创建配置文件
            config_file = os.path.join(temp_dir, "config.json")
            import json
            with open(config_file, 'w') as f:
                json.dump({"using_gpu": False, "use_model": "Dense"}, f)

            # ProjectManager 需要 project_path 参数和配置文件
            pm = ProjectManager(project_path=temp_dir)
            assert pm.project_path == temp_dir
        finally:
            shutil.rmtree(temp_dir)


class TestModuleAvailability:
    """测试模块可用性"""

    def test_core_modules_importable(self):
        """测试核心模块可以正确导入"""
        from core import project_manager
        from core import model_engine
        from config import Config
        assert project_manager is not None
        assert Config is not None

    def test_inference_modules_importable(self):
        """测试推理模块可以正确导入"""
        from inference.processor import InferenceProcessor
        from inference.wavenet5_spice_backend import WaveNet5SPICEBackend
        assert InferenceProcessor is not None
        assert WaveNet5SPICEBackend is not None

    def test_calibration_modules_importable(self):
        """测试校准分析模块可以正确导入"""
        from calibration_analyzer.wavedata import WaveData, WaveRecord
        from calibration_analyzer.waveprocessor import WaveProcessor
        assert WaveData is not None
        assert WaveProcessor is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
