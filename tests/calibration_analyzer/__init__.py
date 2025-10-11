"""
calibration_analyzer模块测试包

此测试包包含对calibration_analyzer模块的测试。
"""
import sys
import os
from pathlib import Path

# 确保可以导入calibration_analyzer包
module_path = Path(__file__).resolve().parent.parent.parent
if str(module_path) not in sys.path:
    sys.path.insert(0, str(module_path))

# 测试包初始化文件
# 使tests目录可以作为一个Python包被导入 