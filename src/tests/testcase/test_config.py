# 测试配置文件
import os
import sys
import unittest
import numpy as np
import tensorflow as tf

# 添加项目根目录到Python路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# 测试数据目录
TEST_DATA_DIR = os.path.join(ROOT_DIR, 'tests', 'testcase', 'test_data')
os.makedirs(TEST_DATA_DIR, exist_ok=True)

# 配置TensorFlow，避免在测试时显示过多的警告和日志
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 只显示错误信息

def set_up_test_env():
    """为测试设置环境"""
    # 设置随机种子以确保测试可重复
    np.random.seed(42)
    tf.random.set_seed(42)
    
    # 可以在这里添加其他测试环境设置
    pass

class BaseTestCase(unittest.TestCase):
    """所有测试用例的基类"""
    
    def setUp(self):
        """在每个测试方法运行前调用"""
        set_up_test_env()
    
    def tearDown(self):
        """在每个测试方法运行后调用"""
        pass
    
    def assert_arrays_equal(self, arr1, arr2, msg=None):
        """比较两个numpy数组是否相等"""
        self.assertTrue(np.array_equal(arr1, arr2), msg=msg)
    
    def assert_arrays_almost_equal(self, arr1, arr2, decimal=7, msg=None):
        """比较两个numpy数组是否几乎相等"""
        np.testing.assert_almost_equal(arr1, arr2, decimal=decimal, err_msg=msg)
