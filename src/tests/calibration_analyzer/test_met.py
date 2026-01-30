"""
测试 met.py 模块的功能
"""
import unittest
import pytest
import numpy as np
import json
import tempfile
import os
import sys
from pathlib import Path

# 确保可以导入模块
root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

try:
    from calibration_analyzer.met import loadData
    from calibration_analyzer.met_data import METData
except ImportError as e:
    pytestmark = pytest.mark.skip(reason=f"无法导入met模块: {e}")


class TestLoadData(unittest.TestCase):
    """测试loadData函数"""

    def setUp(self):
        """设置测试数据"""
        # 创建测试用的METData格式数据（包含所有必需字段）
        self.test_data = {
            "par": {
                "name": "测试传感器",
                "sensitivity": 200.0,
                "frequency_range": [0.5, 100],
                "resistance": 5000,
                "fl": 0.5,
                "C1": 1e-6,
                "C2": 1e-6,
                "R1": 1000.0,
                "R2": 1000.0,
                "R3": 1000.0,
                "Kp": 1.0,
                "Kd": 0.5
            },
            "res": {
                "WsWf": {
                    "f": [1, 2, 5, 10, 20, 50, 100],
                    "abs": [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0],
                    "phase": [0, -10, -30, -45, -60, -80, -90],
                    "sensitivity": 200.0,
                    "low_cut_f": 0.5,
                    "high_cut_f": 100
                },
                "Ws": {
                    "f": [1, 2, 5, 10, 20, 50, 100],
                    "abs": [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0],
                    "phase": [0, -10, -30, -45, -60, -80, -90],
                    "sensitivity": 200.0,
                    "low_cut_f": 0.5,
                    "high_cut_f": 100
                },
                "H": {
                    "f": [1, 2, 5, 10, 20, 50, 100],
                    "abs": [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0],
                    "phase": [0, -10, -30, -45, -60, -80, -90],
                    "sensitivity": 200.0,
                    "low_cut_f": 0.5,
                    "high_cut_f": 100
                },
                "H0": {
                    "f": [1, 2, 5, 10, 20, 50, 100],
                    "abs": [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0],
                    "phase": [0, -10, -30, -45, -60, -80, -90],
                    "sensitivity": 200.0,
                    "low_cut_f": 0.5,
                    "high_cut_f": 100
                },
                "Wfb0_simply": {
                    "f": [1, 2, 5, 10, 20, 50, 100],
                    "abs": [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0],
                    "phase": [0, -10, -30, -45, -60, -80, -90],
                    "sensitivity": 200.0,
                    "low_cut_f": 0.5,
                    "high_cut_f": 100
                },
                "Wfb0": {
                    "f": [1, 2, 5, 10, 20, 50, 100],
                    "abs": [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0],
                    "phase": [0, -10, -30, -45, -60, -80, -90],
                    "sensitivity": 200.0,
                    "low_cut_f": 0.5,
                    "high_cut_f": 100
                },
                "Wfb0_kpkd": {
                    "f": [1, 2, 5, 10, 20, 50, 100],
                    "abs": [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0],
                    "phase": [0, -10, -30, -45, -60, -80, -90],
                    "sensitivity": 200.0,
                    "low_cut_f": 0.5,
                    "high_cut_f": 100
                },
                "Wfb0_pars": {
                    "f": [1, 2, 5, 10, 20, 50, 100],
                    "abs": [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0],
                    "phase": [0, -10, -30, -45, -60, -80, -90],
                    "sensitivity": 200.0,
                    "low_cut_f": 0.5,
                    "high_cut_f": 100
                },
                "H_close_simu_simply": {
                    "f": [1, 2, 5, 10, 20, 50, 100],
                    "abs": [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0],
                    "phase": [0, -10, -30, -45, -60, -80, -90],
                    "sensitivity": 200.0,
                    "low_cut_f": 0.5,
                    "high_cut_f": 100
                },
                "H_close_simu": {
                    "f": [1, 2, 5, 10, 20, 50, 100],
                    "abs": [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0],
                    "phase": [0, -10, -30, -45, -60, -80, -90],
                    "sensitivity": 200.0,
                    "low_cut_f": 0.5,
                    "high_cut_f": 100
                },
                "H_close_simu_kpkd": {
                    "f": [1, 2, 5, 10, 20, 50, 100],
                    "abs": [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0],
                    "phase": [0, -10, -30, -45, -60, -80, -90],
                    "sensitivity": 200.0,
                    "low_cut_f": 0.5,
                    "high_cut_f": 100
                },
                "H_close_simu_with_G": {
                    "f": [1, 2, 5, 10, 20, 50, 100],
                    "abs": [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0],
                    "phase": [0, -10, -30, -45, -60, -80, -90],
                    "sensitivity": 200.0,
                    "low_cut_f": 0.5,
                    "high_cut_f": 100
                },
                "fit": {
                    "A": 1.0,
                    "B": 2.0,
                    "C": 3.0
                },
                "Kp0": 1.0,
                "Kd0": 0.5,
                "G": 100.0
            }
        }

        # 创建临时文件
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = os.path.join(self.temp_dir, "test_data.json")

        # 写入测试数据
        with open(self.temp_file, 'w') as f:
            json.dump(self.test_data, f)

    def tearDown(self):
        """清理临时文件"""
        try:
            os.remove(self.temp_file)
            os.rmdir(self.temp_dir)
        except (FileNotFoundError, OSError):
            pass

    def test_loadData_json_format(self):
        """测试JSON格式数据加载"""
        result = loadData(data_path=self.temp_file, format="JSON")

        self.assertIsInstance(result, METData)
        self.assertIsNotNone(result.raw)
        self.assertIsNotNone(result.wswf)
        self.assertIsNotNone(result.ws)
        self.assertIsNotNone(result.h)
        self.assertIsNotNone(result.h0)

    def test_loadData_unknown_format(self):
        """测试未知格式抛出异常"""
        with self.assertRaises(Exception) as context:
            loadData(data_path=self.temp_file, format="UNKNOWN")

        self.assertIn("ERROR", str(context.exception))


class TestMETData(unittest.TestCase):
    """测试METData类"""

    def setUp(self):
        """设置测试数据"""
        self.test_data = {
            "par": {
                "name": "测试传感器",
                "sensitivity": 200.0,
                "frequency_range": [0.5, 100],
                "resistance": 5000,
                "fl": 0.5,
                "C1": 1e-6,
                "C2": 1e-6,
                "R1": 1000.0,
                "R2": 1000.0,
                "R3": 1000.0,
                "Kp": 1.0,
                "Kd": 0.5
            },
            "res": {
                "WsWf": {
                    "f": [1, 2, 5, 10, 20, 50, 100],
                    "abs": [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0],
                    "phase": [0, -10, -30, -45, -60, -80, -90],
                    "sensitivity": 200.0,
                    "low_cut_f": 0.5,
                    "high_cut_f": 100
                },
                "Ws": {
                    "f": [1, 2, 5, 10, 20, 50, 100],
                    "abs": [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0],
                    "phase": [0, -10, -30, -45, -60, -80, -90],
                    "sensitivity": 200.0,
                    "low_cut_f": 0.5,
                    "high_cut_f": 100
                },
                "H": {
                    "f": [1, 2, 5, 10, 20, 50, 100],
                    "abs": [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0],
                    "phase": [0, -10, -30, -45, -60, -80, -90],
                    "sensitivity": 200.0,
                    "low_cut_f": 0.5,
                    "high_cut_f": 100
                },
                "H0": {
                    "f": [1, 2, 5, 10, 20, 50, 100],
                    "abs": [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0],
                    "phase": [0, -10, -30, -45, -60, -80, -90],
                    "sensitivity": 200.0,
                    "low_cut_f": 0.5,
                    "high_cut_f": 100
                },
                "Wfb0_simply": {
                    "f": [1, 2, 5, 10, 20, 50, 100],
                    "abs": [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0],
                    "phase": [0, -10, -30, -45, -60, -80, -90],
                    "sensitivity": 200.0,
                    "low_cut_f": 0.5,
                    "high_cut_f": 100
                },
                "Wfb0": {
                    "f": [1, 2, 5, 10, 20, 50, 100],
                    "abs": [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0],
                    "phase": [0, -10, -30, -45, -60, -80, -90],
                    "sensitivity": 200.0,
                    "low_cut_f": 0.5,
                    "high_cut_f": 100
                },
                "Wfb0_kpkd": {
                    "f": [1, 2, 5, 10, 20, 50, 100],
                    "abs": [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0],
                    "phase": [0, -10, -30, -45, -60, -80, -90],
                    "sensitivity": 200.0,
                    "low_cut_f": 0.5,
                    "high_cut_f": 100
                },
                "Wfb0_pars": {
                    "f": [1, 2, 5, 10, 20, 50, 100],
                    "abs": [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0],
                    "phase": [0, -10, -30, -45, -60, -80, -90],
                    "sensitivity": 200.0,
                    "low_cut_f": 0.5,
                    "high_cut_f": 100
                },
                "H_close_simu_simply": {
                    "f": [1, 2, 5, 10, 20, 50, 100],
                    "abs": [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0],
                    "phase": [0, -10, -30, -45, -60, -80, -90],
                    "sensitivity": 200.0,
                    "low_cut_f": 0.5,
                    "high_cut_f": 100
                },
                "H_close_simu": {
                    "f": [1, 2, 5, 10, 20, 50, 100],
                    "abs": [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0],
                    "phase": [0, -10, -30, -45, -60, -80, -90],
                    "sensitivity": 200.0,
                    "low_cut_f": 0.5,
                    "high_cut_f": 100
                },
                "H_close_simu_kpkd": {
                    "f": [1, 2, 5, 10, 20, 50, 100],
                    "abs": [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0],
                    "phase": [0, -10, -30, -45, -60, -80, -90],
                    "sensitivity": 200.0,
                    "low_cut_f": 0.5,
                    "high_cut_f": 100
                },
                "H_close_simu_with_G": {
                    "f": [1, 2, 5, 10, 20, 50, 100],
                    "abs": [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0],
                    "phase": [0, -10, -30, -45, -60, -80, -90],
                    "sensitivity": 200.0,
                    "low_cut_f": 0.5,
                    "high_cut_f": 100
                },
                "fit": {
                    "A": 1.0,
                    "B": 2.0,
                    "C": 3.0
                },
                "Kp0": 1.0,
                "Kd0": 0.5,
                "G": 100.0
            }
        }

    def test_met_data_init(self):
        """测试METData初始化"""
        met_data = METData(self.test_data)

        self.assertIsNotNone(met_data.raw)
        self.assertIsNotNone(met_data.wswf)
        self.assertIsNotNone(met_data.ws)
        self.assertIsNotNone(met_data.h)
        self.assertIsNotNone(met_data.h0)

    def test_load_system(self):
        """测试加载系统响应"""
        met_data = METData(self.test_data)

        # 验证系统响应属性
        self.assertIsNotNone(met_data.wswf)
        self.assertIsNotNone(met_data.ws)
        self.assertEqual(len(met_data.wswf.freq), len(self.test_data["res"]["WsWf"]["f"]))
        self.assertEqual(len(met_data.wswf.gain), len(self.test_data["res"]["WsWf"]["abs"]))

    def test_load_parameters(self):
        """测试加载参数"""
        met_data = METData(self.test_data)

        self.assertIsNotNone(met_data.parameter)
        self.assertEqual(met_data.parameter.frequency_low, 0.5)
        self.assertEqual(met_data.parameter.kp, 1.0)
        self.assertEqual(met_data.parameter.kd, 0.5)

    def test_load_feedback_system(self):
        """测试加载反馈系统"""
        met_data = METData(self.test_data)

        self.assertIsNotNone(met_data.feedback)
        self.assertEqual(met_data.feedback.kp0, 1.0)
        self.assertEqual(met_data.feedback.kd0, 0.5)

    def test_fit_function(self):
        """测试拟合函数"""
        met_data = METData(self.test_data)

        self.assertIsNotNone(met_data.fit)
        # CFun是一个类实例，测试其属性
        self.assertEqual(met_data.fit.A, 1.0)
        self.assertEqual(met_data.fit.B, 2.0)
        self.assertEqual(met_data.fit.C, 3.0)
        # 测试计算得到的仿真值
        self.assertIsNotNone(met_data.fit.simu_R_39)
        self.assertIsNotNone(met_data.fit.simu_C_14)

    def test_gain_attribute(self):
        """测试增益属性"""
        met_data = METData(self.test_data)

        self.assertEqual(met_data.G, 100.0)


if __name__ == "__main__":
    pytest.main(["-v", __file__])
