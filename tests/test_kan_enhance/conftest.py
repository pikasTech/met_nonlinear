"""
conftest.py - 测试夹具和通用工具

提供用于cli及相关模块测试的夹具和工具函数
"""

import os
import sys
import shutil
import tempfile
import pytest
import numpy as np
from pathlib import Path

# 检查模块可用性
from tests.test_kan_enhance import cli_AVAILABLE, KAN_LUT_AVAILABLE, TENSORFLOW_AVAILABLE

# 如果TensorFlow可用，则导入，否则创建Mock对象
if TENSORFLOW_AVAILABLE:
    import tensorflow as tf
else:
    # 创建TensorFlow的基本Mock
    class MockTF:
        class keras:
            class Model:
                def __init__(self, *args, **kwargs):
                    self.weights = []
                    self.layers = []
                
                def save_weights(self, filepath):
                    with open(filepath, 'w') as f:
                        f.write('mock_weights')
                
                def load_weights(self, filepath):
                    pass
                
                def predict(self, *args, **kwargs):
                    return np.zeros((10, 1))
            
            class Layer:
                def __init__(self, *args, **kwargs):
                    pass
                
                def __call__(self, inputs):
                    return inputs
                
            class losses:
                @staticmethod
                def MeanSquaredError():
                    return lambda y_true, y_pred: np.mean((y_true - y_pred) ** 2)
            
            class optimizers:
                class Adam:
                    def __init__(self, learning_rate=0.001):
                        self.learning_rate = learning_rate
            
            class callbacks:
                class EarlyStopping:
                    def __init__(self, **kwargs):
                        pass
                
                class ModelCheckpoint:
                    def __init__(self, **kwargs):
                        pass
    
    tf = MockTF()

@pytest.fixture
def temp_project_dir():
    """创建临时项目目录结构
    
    Returns:
        str: 临时项目目录路径
    """
    # 创建临时目录
    temp_dir = tempfile.mkdtemp(prefix="kan_test_")
    
    # 创建项目结构
    os.makedirs(os.path.join(temp_dir, "models"), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, "data"), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, "results"), exist_ok=True)
    
    # 创建测试配置文件
    with open(os.path.join(temp_dir, "config.txt"), 'w') as f:
        f.write("project_name=test_project\n")
        f.write("model_type=iir\n")
        f.write("data_path=data/test.csv\n")
    
    # 提供目录路径并在测试结束后清理
    try:
        yield temp_dir
    finally:
        try:
            shutil.rmtree(temp_dir)
        except (PermissionError, OSError):
            print(f"警告: 无法删除临时目录 {temp_dir}")

@pytest.fixture
def mock_dataset():
    """创建模拟数据集
    
    Returns:
        tuple: (X_train, y_train, X_test, y_test)
    """
    # 创建简单的正弦波数据集
    np.random.seed(42)
    t = np.linspace(0, 10, 1000)
    
    # 输入数据 - 正弦波
    X = np.sin(t).reshape(-1, 1)
    
    # 目标数据 - 正弦波的平方
    y = np.square(X)
    
    # 添加一些噪声
    X += np.random.normal(0, 0.1, X.shape)
    y += np.random.normal(0, 0.1, y.shape)
    
    # 划分训练集和测试集
    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    
    return X_train, y_train, X_test, y_test

@pytest.fixture
def mock_project_manager():
    """创建模拟的ProjectManager对象
    
    如果可用，返回真实的ProjectManager实例；
    如果不可用，返回模拟对象
    """
    if not cli_AVAILABLE:
        class MockProjectManager:
            def __init__(self, project_path=None):
                self.project_path = project_path or "mock_project"
                self.project_name = self.project_path.split('/')[-1]
                # 使用类似于Config的对象而不是字典
                class MockConfig:
                    def __init__(self):
                        self.use_model = "IIR"
                        self.using_gpu = True
                        self.data_path = "data/mock.csv"
                
                self.config = MockConfig()
                self.model = None
                self.scaler = None
                
            def prepare_dataset_and_model(self, *args, **kwargs):
                self.model = object()  # 假模型
                return True
                
            def run_prediction(self, *args, **kwargs):
                return np.zeros((100, 1))
                
            def load_base_model_weights(self, *args, **kwargs):
                return True
                
            def evaluate(self, *args, **kwargs):
                return {"loss": 0.1, "mse": 0.1}
                
            def lut(self, *args, **kwargs):
                return True
                
            def model_info(self, *args, **kwargs):
                return "MockProjectManager - 模拟模型"
        
        return MockProjectManager
    
    # 如果cli可用，导入ProjectManager
    from cli import ProjectManager
    return ProjectManager

class TestDataGenerator:
    """测试数据生成器
    
    提供各种测试数据的生成方法
    """
    @staticmethod
    def create_sine_wave(freq=1.0, amplitude=1.0, duration=1.0, fs=1000):
        """创建正弦波测试数据
        
        Args:
            freq: 频率(Hz)
            amplitude: 振幅
            duration: 持续时间(秒)
            fs: 采样率(Hz)
            
        Returns:
            tuple: (t, y) 时间和信号值
        """
        t = np.arange(0, duration, 1/fs)
        y = amplitude * np.sin(2 * np.pi * freq * t)
        return t, y
    
    @staticmethod
    def create_project_config(path, config_dict):
        """创建项目配置文件
        
        Args:
            path: 配置文件路径
            config_dict: 配置字典
            
        Returns:
            str: 配置文件路径
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            for key, value in config_dict.items():
                f.write(f"{key}={value}\n")
        return path
    
    @staticmethod
    def create_dummy_weights_file(path):
        """创建虚拟权重文件
        
        Args:
            path: 权重文件路径
            
        Returns:
            str: 权重文件路径
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            # 创建一些随机数据作为权重
            data = np.random.randn(100, 100).astype(np.float32)
            np.save(f, data)
        return path 