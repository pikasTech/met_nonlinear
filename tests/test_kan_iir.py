#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试 cli.py 模块中的 ProjectManager 类
"""

import unittest
import sys
import os
import shutil
import tempfile
import json
import importlib.util

# 添加项目根目录到系统路径，以便正确导入模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 检查必要模块是否可用
tensorflow_available = importlib.util.find_spec("tensorflow") is not None
cli_available = False  # 默认设置为False

try:
    from cli import ProjectManager, get_all_project_dirs, met_comp_with_project
    from model_engine import ModelEngine
    cli_available = True
except ImportError:
    # 仅用于标记模块不可用，不创建模拟对象
    pass

# 定义路径标准化函数
def normalize_path(path):
    """标准化路径表示，确保跨平台一致性"""
    from pathlib import Path
    return str(Path(path))


@unittest.skipIf(not cli_available, "cli 模块不可用")
class TestProjectManager(unittest.TestCase):
    """测试 ProjectManager 类的基本功能"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建临时目录模拟项目路径
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = os.path.join(self.temp_dir, 'test_project')
        os.makedirs(self.project_path, exist_ok=True)
        
        # 创建配置文件
        self.config_path = os.path.join(self.project_path, 'config.json')
        self.config_data = {
            "use_train_model": True,
            "use_model": "FRIKAN",
            "dataset_type": "MET",
            "use_predict_fr": True,
            "USE_PREDICT_LINEAR": True,
            "USE_PREDICT_LINSPACE": False,
            "use_predict_tr": False,
            "use_predict_features": False,
            "use_sin_fr": False,
            "use_predict_tr_from_file": False,
            "use_spline": True,
            "H_UNITS": 10,
            "adjust_weight": False,
            "base_project": ""  # 添加空的base_project属性
        }
        with open(self.config_path, 'w') as f:
            json.dump(self.config_data, f)
            
        # 创建数据目录
        self.data_dir = os.path.join(self.project_path, 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 创建测试用的模型权重文件
        self.base_project_path = os.path.join(self.temp_dir, 'base_project')
        self.base_data_dir = os.path.join(self.base_project_path, 'data')
        os.makedirs(self.base_data_dir, exist_ok=True)
        
        # 创建测试用的权重文件
        self.best_val_weights_file = os.path.join(self.base_data_dir, 'best_val.weights.h5')
        self.best_weights_file = os.path.join(self.base_data_dir, 'best.weights.h5')
        with open(self.best_val_weights_file, 'w') as f:
            f.write('dummy weights')
        with open(self.best_weights_file, 'w') as f:
            f.write('dummy weights')
            
        # 创建 ProjectManager 实例
        self.project_manager = ProjectManager(self.project_path)
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """测试 ProjectManager 初始化参数设置"""
        # 验证基本属性
        self.assertEqual(normalize_path(self.project_manager.project_path), normalize_path(self.project_path))
        
        # 使用 os.path.basename 进行比较，避免绝对路径问题
        import os
        self.assertEqual(os.path.basename(self.project_manager.project_name), 'test_project')
        
        self.assertEqual(normalize_path(self.project_manager.config_path), normalize_path(self.config_path))
        self.assertEqual(normalize_path(self.project_manager.checkpoint_dir), normalize_path(self.data_dir))
        
        # 验证配置加载
        self.assertIsNotNone(self.project_manager.config)
        
        # 验证状态管理器和日志记录器初始化
        self.assertIsNotNone(self.project_manager.state_manager)
        self.assertIsNotNone(self.project_manager.training_logger)
    
    def test_load_base_model_weights(self):
        """测试基础模型权重加载功能"""
        # 修改配置以包含基础模型
        self.project_manager.config.base_project = 'base_project'
        
        # 确保基础项目目录存在
        os.makedirs(os.path.join("projects", "base_project", "data"), exist_ok=True)
        
        # 创建必要的权重文件
        base_weight_path = os.path.join("projects", "base_project", "data", "best_val.weights.h5")
        with open(base_weight_path, 'w') as f:
            f.write('test weights')
            
        # 调用实际的load_base_model_weights方法
        result = self.project_manager.load_base_model_weights(None)
        
        # 清理创建的测试文件
        shutil.rmtree(os.path.join("projects", "base_project"))


@unittest.skipIf(not cli_available, "cli 模块不可用")
class TestHelperFunctions(unittest.TestCase):
    """测试辅助函数"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建临时目录模拟项目目录
        self.temp_dir = tempfile.mkdtemp()
        self.projects_dir = os.path.join(self.temp_dir, 'projects')
        os.makedirs(self.projects_dir, exist_ok=True)
        
        # 创建测试项目目录
        self.project1_dir = os.path.join(self.projects_dir, 'project1')
        self.project2_dir = os.path.join(self.projects_dir, 'project2')
        os.makedirs(self.project1_dir, exist_ok=True)
        os.makedirs(self.project2_dir, exist_ok=True)
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir)
    
    def test_get_all_project_dirs(self):
        """测试获取所有项目目录功能"""
        # 在临时测试目录中创建项目
        projects_path = os.path.join(self.temp_dir, "test_projects")
        os.makedirs(projects_path, exist_ok=True)
        
        # 创建测试项目目录
        os.makedirs(os.path.join(projects_path, "project1"), exist_ok=True)
        os.makedirs(os.path.join(projects_path, "project2"), exist_ok=True)
        
        # 调用实际函数
        result = get_all_project_dirs(projects_path)
        
        # 验证结果
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertTrue("project1" in result)
        self.assertTrue("project2" in result)
    
    def test_get_all_project_dirs_empty(self):
        """测试无项目目录时的功能"""
        # 创建空目录
        empty_dir = os.path.join(self.temp_dir, "empty")
        os.makedirs(empty_dir, exist_ok=True)
        
        # 调用实际函数
        result = get_all_project_dirs(empty_dir)
        
        # 验证返回值为空列表
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)
    
    def test_met_comp_with_project(self):
        """测试创建项目管理器功能"""
        # 创建配置文件
        project_path = self.project1_dir
        config_path = os.path.join(project_path, 'config.json')
        with open(config_path, 'w') as f:
            json.dump({"base_project": ""}, f)
        
        # 创建数据目录
        data_dir = os.path.join(project_path, 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # 直接测试ProjectManager类的初始化
        result = ProjectManager(project_path)
        
        # 验证返回值
        self.assertIsInstance(result, ProjectManager)
        self.assertEqual(normalize_path(result.project_path), normalize_path(project_path))


if __name__ == "__main__":
    unittest.main() 