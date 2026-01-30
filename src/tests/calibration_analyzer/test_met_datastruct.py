"""
测试 met_datastruct.py 模块的功能
"""
import unittest
import pytest
import sys
from pathlib import Path

# 确保可以导入calibration_analyzer包
root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

try:
    from calibration_analyzer.met_datastruct import (
        convert_capacitance, ComponentValues, process_exam, CFun
    )
except ImportError as e:
    pytestmark = pytest.mark.skip(reason=f"无法导入met_datastruct模块: {e}")


class TestConvertCapacitance(unittest.TestCase):
    """测试convert_capacitance函数"""

    def test_microfarad_range(self):
        """测试微法范围"""
        value, unit = convert_capacitance(1e-6)
        self.assertEqual(unit, "µF")
        self.assertAlmostEqual(value, 1.0)

    def test_nanofarad_range(self):
        """测试纳法范围"""
        value, unit = convert_capacitance(1e-9)
        self.assertEqual(unit, "nF")
        self.assertAlmostEqual(value, 1.0)

    def test_picofarad_range(self):
        """测试皮法范围"""
        value, unit = convert_capacitance(1e-12)
        self.assertEqual(unit, "pF")
        self.assertAlmostEqual(value, 1.0)

    def test_femtofarad_range(self):
        """测试飞法范围"""
        value, unit = convert_capacitance(1e-15)
        self.assertEqual(unit, "fF")
        self.assertAlmostEqual(value, 1.0)

    def test_boundary_values(self):
        """测试边界值"""
        # 1e-6 应该是 µF
        value, unit = convert_capacitance(0.999e-6)
        self.assertEqual(unit, "nF")  # 略小于1e-6，应该用nF

        # 1e-9 应该是 nF
        value, unit = convert_capacitance(1e-9)
        self.assertEqual(unit, "nF")


class TestComponentValues(unittest.TestCase):
    """测试ComponentValues类"""

    def test_init(self):
        """测试初始化"""
        values = ComponentValues(10000, 20000, 30000, 1e-9, 2e-9, 3e-9)

        self.assertEqual(values.R_39, 10000)
        self.assertEqual(values.R_42, 20000)
        self.assertEqual(values.R_43, 30000)
        self.assertEqual(values.C_14, 1e-9)
        self.assertEqual(values.C_15, 2e-9)
        self.assertEqual(values.C_16, 3e-9)


class TestProcessExam(unittest.TestCase):
    """测试process_exam函数"""

    def test_basic_processing(self):
        """测试基本处理"""
        result = process_exam(A_val=100, B_val=50, C_val=10)

        self.assertIsInstance(result, ComponentValues)
        self.assertGreater(result.R_39, 0)
        self.assertGreater(result.R_42, 0)
        self.assertGreater(result.R_43, 0)
        self.assertGreater(result.C_14, 0)
        self.assertGreater(result.C_15, 0)
        self.assertGreater(result.C_16, 0)

    def test_with_custom_r_values(self):
        """测试使用自定义R值"""
        result = process_exam(
            A_val=100, B_val=50, C_val=10,
            R_39_val=20000, R_42_val=15000, R_43_val=10000
        )

        self.assertEqual(result.R_39, 20000)
        self.assertEqual(result.R_42, 15000)
        self.assertEqual(result.R_43, 10000)


class TestCFun(unittest.TestCase):
    """测试CFun类"""

    def test_init(self):
        """测试初始化"""
        cfun = CFun(A=100, B=50, C=10)

        self.assertEqual(cfun.A, 100)
        self.assertEqual(cfun.B, 50)
        self.assertEqual(cfun.C, 10)

    def test_init_with_custom_r(self):
        """测试使用自定义R值初始化"""
        cfun = CFun(A=100, B=50, C=10, R_39_val=20000, R_42_val=15000, R_43_val=10000)

        self.assertEqual(cfun.simu_R_39, 20000)
        self.assertEqual(cfun.simu_R_42, 15000)
        self.assertEqual(cfun.simu_R_43, 10000)

    def test_clone(self):
        """测试克隆功能"""
        cfun = CFun(A=100, B=50, C=10)
        cloned = cfun.clone()

        self.assertEqual(cloned.A, cfun.A)
        self.assertEqual(cloned.B, cfun.B)
        self.assertEqual(cloned.C, cfun.C)

    def test_todict(self):
        """测试转换为字典"""
        cfun = CFun(A=100, B=50, C=10)
        data = cfun.todict()

        self.assertIsInstance(data, dict)
        self.assertIn('A', data)
        self.assertIn('B', data)
        self.assertIn('C', data)
        self.assertIn('simu_R_39', data)
        self.assertIn('simu_R_42', data)
        self.assertIn('simu_R_43', data)
        self.assertIn('simu_C_14', data)
        self.assertIn('simu_C_15', data)
        self.assertIn('simu_C_16', data)

    def test_str_representation(self):
        """测试字符串表示"""
        cfun = CFun(A=100, B=50, C=10)
        str_repr = str(cfun)

        self.assertIsInstance(str_repr, str)
        self.assertGreater(len(str_repr), 0)


# 使用pytest的参数化测试
@pytest.mark.parametrize("value,expected_unit", [
    (1e-6, "µF"),
    (1e-9, "nF"),
    (1e-12, "pF"),
    (1e-15, "fF"),
])
def test_convert_capacitance_params(value, expected_unit):
    """参数化测试convert_capacitance函数"""
    result_value, result_unit = convert_capacitance(value)
    assert result_unit == expected_unit


@pytest.mark.parametrize("A,B,C", [
    (100, 50, 10),
    (50, 25, 5),
    (200, 100, 20),
])
def test_cfun_creation(A, B, C):
    """参数化测试CFun创建"""
    cfun = CFun(A=A, B=B, C=C)
    assert cfun.A == A
    assert cfun.B == B
    assert cfun.C == C


if __name__ == "__main__":
    pytest.main(["-v", __file__])
