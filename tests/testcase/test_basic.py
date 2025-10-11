# 基础功能测试
import unittest
from tests.testcase.test_config import BaseTestCase


class TestBasic(BaseTestCase):
    """基础功能测试，确保测试框架正常工作"""
    
    def test_simple_assertion(self):
        """最简单的断言测试"""
        self.assertEqual(1 + 1, 2)
        self.assertTrue(True)
        self.assertFalse(False)
    
    def test_numpy_assertion(self):
        """测试numpy相关断言"""
        import numpy as np
        arr1 = np.array([1, 2, 3])
        arr2 = np.array([1, 2, 3])
        self.assert_arrays_equal(arr1, arr2)


if __name__ == '__main__':
    unittest.main()
