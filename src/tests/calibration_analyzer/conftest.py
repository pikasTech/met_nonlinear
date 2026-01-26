"""
conftest.py - pytest配置文件
提供通用的测试夹具和配置
"""

import pytest
import numpy as np
import tempfile
import os
import sys
from pathlib import Path

# 确保可以导入calibration_analyzer包和项目根目录
root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

# 创建测试信号的夹具
@pytest.fixture
def sine_wave_data():
    """
    生成正弦波测试数据
    返回: (数据, 采样率, 频率, 振幅)
    """
    fs = 1000  # 采样率
    freq = 10  # 频率
    amp = 1.0  # 振幅
    t = np.arange(0, 1, 1/fs)  # 1秒的时间数组
    data = amp * np.sin(2 * np.pi * freq * t)
    return data, fs, freq, amp

@pytest.fixture
def square_wave_data():
    """
    生成方波测试数据
    返回: (数据, 采样率, 频率, 振幅)
    """
    fs = 1000  # 采样率
    freq = 5  # 频率
    amp = 1.0  # 振幅
    t = np.arange(0, 1, 1/fs)  # 1秒的时间数组
    data = amp * np.sign(np.sin(2 * np.pi * freq * t))
    return data, fs, freq, amp

@pytest.fixture
def temp_dir():
    """
    创建临时目录
    测试结束后自动删除
    """
    temp_path = tempfile.mkdtemp()
    yield temp_path
    # 测试结束后清理临时目录
    try:
        for file in os.listdir(temp_path):
            os.remove(os.path.join(temp_path, file))
        os.rmdir(temp_path)
    except (FileNotFoundError, PermissionError):
        pass  # 忽略清理错误 