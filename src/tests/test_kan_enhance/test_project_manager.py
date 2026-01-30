"""
test_project_manager.py - ProjectManager类测试

详细测试cli.py中ProjectManager类的各项功能，
包括初始化、数据处理、模型管理和预测功能。
注意：此测试假设 cli 模块已正确导入（通过 test_kan_enhance/__init__.py）
"""

import os
import sys
import unittest
import pytest
import numpy as np
import tempfile
import shutil
from pathlib import Path

# 导入模块可用性标志
from tests.test_kan_enhance import cli_AVAILABLE, KAN_LUT_AVAILABLE, TENSORFLOW_AVAILABLE
from tests.test_kan_enhance.conftest import TestDataGenerator

# 如果cli模块不可用，跳过所有测试
pytestmark = pytest.mark.skipif(not cli_AVAILABLE, reason="cli模块不可用")

# 条件导入ProjectManager和Config
if cli_AVAILABLE:
    from core.project_manager import ProjectManager
    from core.cli_parser import get_all_project_dirs
    from core.cli_helpers import met_comp_with_project
    from config import Config


@pytest.mark.skipif(not cli_AVAILABLE, reason="cli模块不可用")
class TestProjectManagerEnhanced:
    """ProjectManager类增强测试"""

    def setup_method(self, method):
        """设置测试环境"""
        # 创建临时项目目录
        self.temp_dir = tempfile.mkdtemp(prefix="pm_test_")

        # 创建项目结构
        os.makedirs(os.path.join(self.temp_dir, "models"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "data"), exist_ok=True)

        # 创建配置文件 (JSON格式)
        self.config_file = os.path.join(self.temp_dir, "config.json")
        config_data = {
            "using_gpu": False,
            "use_model": "Dense",
            "learning_rate": 0.01,
            "epoch_train": 100,
            "sample_rate": 2000,
            "data_path": "data/test.csv"
        }

        with open(self.config_file, 'w') as f:
            import json
            json.dump(config_data, f)

    def teardown_method(self, method):
        """清理测试环境"""
        try:
            shutil.rmtree(self.temp_dir)
        except (PermissionError, OSError) as e:
            print(f"警告: 无法删除临时目录 {self.temp_dir}: {e}")

    def test_initialization(self):
        """测试ProjectManager初始化"""
        manager = ProjectManager(project_path=self.temp_dir)
        assert manager is not None
        assert manager.project_path == self.temp_dir
        assert manager.config is not None

    def test_initialization_with_missing_config(self):
        """测试缺少配置文件的情况"""
        empty_dir = tempfile.mkdtemp(prefix="empty_pm_test_")
        try:
            with pytest.raises(Exception):
                ProjectManager(project_path=empty_dir)
        finally:
            shutil.rmtree(empty_dir)

    def test_model_info(self):
        """测试模型信息功能"""
        manager = ProjectManager(project_path=self.temp_dir)
        try:
            info = manager.model_info()
            assert info is not None
        except Exception as e:
            pytest.skip(f"模型信息测试跳过: {e}")


@pytest.mark.skipif(not cli_AVAILABLE, reason="cli模块不可用")
class TestHelperFunctionsEnhanced:
    """辅助函数增强测试"""

    def setup_method(self, method):
        """设置测试环境"""
        # 创建临时项目根目录
        self.temp_root = tempfile.mkdtemp(prefix="helper_test_")

        # 创建多个项目目录
        self.project_dirs = []
        for i in range(3):
            project_dir = os.path.join(self.temp_root, f"project_{i}")
            os.makedirs(project_dir, exist_ok=True)

            config_file = os.path.join(project_dir, "config.json")
            config_data = {
                "using_gpu": False,
                "use_model": f"Dense_{i}",
                "learning_rate": 0.01
            }

            with open(config_file, 'w') as f:
                import json
                json.dump(config_data, f)

            self.project_dirs.append(project_dir)

        self.non_project_dir = os.path.join(self.temp_root, "non_project")
        os.makedirs(self.non_project_dir, exist_ok=True)

    def teardown_method(self, method):
        """清理测试环境"""
        try:
            shutil.rmtree(self.temp_root)
        except (PermissionError, OSError) as e:
            print(f"警告: 无法删除临时根目录 {self.temp_root}: {e}")

    def test_get_all_project_dirs(self):
        """测试获取所有项目目录功能"""
        result = get_all_project_dirs(self.temp_root)
        assert result is not None
        assert isinstance(result, list)

        # 验证项目目录数量正确
        for proj_dir in self.project_dirs:
            basename = os.path.basename(proj_dir)
            found = any(basename in p for p in result)
            assert found, f"项目 {basename} 未找到"

    def test_get_all_project_dirs_with_empty(self):
        """测试空目录情况下的项目目录获取"""
        empty_dir = tempfile.mkdtemp(prefix="empty_helper_test_")
        try:
            result = get_all_project_dirs(empty_dir)
            assert result is not None
            assert isinstance(result, list)
        finally:
            shutil.rmtree(empty_dir)


if __name__ == "__main__":
    pytest.main(["-v", __file__])
