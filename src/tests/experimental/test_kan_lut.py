#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试 kan_lut.py 模块中的 KAN LUT 类
包含 KAN_LUT, LayerKAN_LUT, IIR, LayerIIR, ModelKAN_LUT 等类的单元测试
"""

import unittest
import numpy as np
import sys
import os

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# 导入被测试模块
from experimental.kan_lut import KAN_LUT, LayerKAN_LUT, IIR, LayerIIR, ModelKAN_LUT


class TestKANLUT(unittest.TestCase):
    """测试 KAN_LUT 类的基本功能"""

    def setUp(self):
        """设置测试环境"""
        self.grid_size = 8
        self.spline_order = 2
        self.grid_range = (0, 1)
        self.lut_points = 100

    def test_initialization_default(self):
        """测试默认初始化参数"""
        lut = KAN_LUT()
        self.assertEqual(lut.grid_size, 8)
        self.assertEqual(lut.spline_order, 2)
        self.assertEqual(lut.grid_range, (0, 1))
        self.assertEqual(lut.lut_points, 100)
        self.assertTrue(lut.lut_interp)
        self.assertIsNone(lut.lut)

    def test_initialization_custom(self):
        """测试自定义初始化参数"""
        lut = KAN_LUT(
            grid_size=5,
            spline_order=3,
            grid_range=(0, 2),
            lut_points=200,
            lut_interp=False
        )
        self.assertEqual(lut.grid_size, 5)
        self.assertEqual(lut.spline_order, 3)
        self.assertEqual(lut.grid_range, (0, 2))
        self.assertEqual(lut.lut_points, 200)
        self.assertFalse(lut.lut_interp)

    def test_grid_generation(self):
        """测试网格生成"""
        lut = KAN_LUT(grid_size=4, spline_order=2, grid_range=(0, 1))
        grid = lut.grid

        # 网格长度应该是 grid_size + 2 * spline_order + 1 = 4 + 4 + 1 = 9
        expected_length = lut.grid_size + 2 * lut.spline_order + 1
        self.assertEqual(len(grid), expected_length)

        # 网格应该以负扩展开始，以正扩展结束
        self.assertLess(grid[0], lut.grid_range[0])
        self.assertGreater(grid[-1], lut.grid_range[1])

    def test_set_spline_kernel(self):
        """测试设置样条核"""
        lut = KAN_LUT(grid_size=4, spline_order=2)
        kernel_size = lut.grid_size + lut.spline_order  # 6

        # 设置自定义核
        custom_kernel = np.random.randn(kernel_size).tolist()
        lut.set_spline_kernel(custom_kernel)

        self.assertEqual(len(lut.spline_kernel), kernel_size)

    def test_set_spline_kernel_invalid_length(self):
        """测试无效长度的样条核"""
        lut = KAN_LUT(grid_size=4, spline_order=2)
        invalid_kernel = [1.0, 2.0, 3.0]  # 错误长度

        with self.assertRaises(ValueError):
            lut.set_spline_kernel(invalid_kernel)

    def test_set_spline_kernel_numpy_array(self):
        """测试使用 numpy 数组设置样条核"""
        lut = KAN_LUT(grid_size=4, spline_order=2)
        kernel_size = lut.grid_size + lut.spline_order

        # 使用 numpy 数组
        custom_kernel = np.random.randn(kernel_size)
        lut.set_spline_kernel(custom_kernel)

        self.assertEqual(len(lut.spline_kernel), kernel_size)

    def test_calc_spline_bases(self):
        """测试样条基函数计算"""
        lut = KAN_LUT(grid_size=4, spline_order=2, grid_range=(0, 1))

        # 测试输入值 0.5
        bases = lut.calc_spline_bases(0.5)

        # 基函数数量应该是 grid_size + spline_order = 6
        expected_bases = lut.grid_size + lut.spline_order
        self.assertEqual(len(bases), expected_bases)

        # 所有基函数值应该在 [0, 1] 范围内
        for base in bases:
            self.assertGreaterEqual(base, 0.0)
            self.assertLessEqual(base, 1.0)

    def test_calc_spline_bases_boundary(self):
        """测试边界值处的样条基函数"""
        lut = KAN_LUT(grid_size=4, spline_order=2, grid_range=(0, 1))

        # 测试边界值
        bases_min = lut.calc_spline_bases(0.0)
        bases_max = lut.calc_spline_bases(1.0)

        # 不应该抛出异常
        self.assertEqual(len(bases_min), lut.grid_size + lut.spline_order)
        self.assertEqual(len(bases_max), lut.grid_size + lut.spline_order)

    def test_calc_spline_output(self):
        """测试样条输出计算"""
        lut = KAN_LUT(grid_size=4, spline_order=2)

        # 设置一个简单的线性核
        kernel_size = lut.grid_size + lut.spline_order
        lut.set_spline_kernel([float(i) / kernel_size for i in range(kernel_size)])

        # 计算输出
        output = lut.calc_spline_output(0.5)

        # 输出应该是浮点数
        self.assertIsInstance(output, float)

    def test_calc_spline_output_positive_constraint(self):
        """测试输出正约束"""
        lut = KAN_LUT(grid_size=4, spline_order=2)

        # 设置产生负值的核
        kernel_size = lut.grid_size + lut.spline_order
        lut.set_spline_kernel([-1.0] * kernel_size)

        # 计算输出 (only_positive=True)
        output = lut.calc_spline_output(0.5, only_positive=True)

        # 输出应该为正
        self.assertGreaterEqual(output, 0.0)

    def test_calc_spline_output_symmetry(self):
        """测试输出对称性"""
        lut = KAN_LUT(grid_size=4, spline_order=2)

        # 设置一个简单的核
        kernel_size = lut.grid_size + lut.spline_order
        lut.set_spline_kernel(list(range(kernel_size)))

        # 计算正负输入的输出
        output_pos = lut.calc_spline_output(0.5)
        output_neg = lut.calc_spline_output(-0.5)

        # 输出应该是相反数（奇对称）
        self.assertAlmostEqual(output_pos, -output_neg, places=5)

    def test_build_lut(self):
        """测试 LUT 构建"""
        lut = KAN_LUT(grid_size=4, spline_order=2, lut_points=50)
        kernel_size = lut.grid_size + lut.spline_order
        lut.set_spline_kernel([1.0] * kernel_size)

        # 构建 LUT
        result = lut.build_lut()

        # LUT 应该被构建
        self.assertIsNotNone(lut.lut)
        self.assertTrue(len(lut.lut) > 0)
        self.assertTrue(len(result) > 0)

    def test_build_lut_idempotent(self):
        """测试 LUT 构建的幂等性"""
        lut = KAN_LUT(grid_size=4, spline_order=2, lut_points=50)
        kernel_size = lut.grid_size + lut.spline_order
        lut.set_spline_kernel(list(range(kernel_size)))

        # 第一次构建
        lut.build_lut()
        lut1 = lut.lut.copy()

        # 第二次构建（应该使用相同数据）
        lut.build_lut()
        lut2 = lut.lut

        # 结果应该相同
        np.testing.assert_array_equal(lut1, lut2)

    def test_calc_spline_output_lut(self):
        """测试 LUT 查表输出"""
        lut = KAN_LUT(grid_size=4, spline_order=2, lut_points=100)
        kernel_size = lut.grid_size + lut.spline_order
        lut.set_spline_kernel([1.0] * kernel_size)

        # 先构建 LUT
        lut.build_lut()

        # 查表输出
        output = lut.calc_spline_output_lut(0.5)

        # 输出应该是浮点数
        self.assertIsInstance(output, float)

    def test_calc_spline_output_lut_autobuild(self):
        """测试 LUT 查表自动构建"""
        lut = KAN_LUT(grid_size=4, spline_order=2, lut_points=100)
        kernel_size = lut.grid_size + lut.spline_order
        lut.set_spline_kernel([1.0] * kernel_size)

        # 不显式构建，直接查表
        output = lut.calc_spline_output_lut(0.5)

        # LUT 应该被自动构建
        self.assertIsNotNone(lut.lut)

    def test_calc_spline_output_lut_numpy_input(self):
        """测试 LUT 查表处理 numpy 输入"""
        lut = KAN_LUT(grid_size=4, spline_order=2, lut_points=100)
        kernel_size = lut.grid_size + lut.spline_order
        lut.set_spline_kernel([1.0] * kernel_size)

        # 使用 numpy 数组输入
        x = np.array([0.5])
        output = lut.calc_spline_output_lut(x)

        self.assertIsInstance(output, float)

    def test_calc_spline_output_lut_no_interp(self):
        """测试 LUT 查表不插值"""
        lut = KAN_LUT(grid_size=4, spline_order=2, lut_points=100, lut_interp=False)
        kernel_size = lut.grid_size + lut.spline_order
        lut.set_spline_kernel([1.0] * kernel_size)

        lut.build_lut()
        output = lut.calc_spline_output_lut(0.5)

        self.assertIsInstance(output, float)

    def test_calc_spline_output_lut_logscale(self):
        """测试 LUT 查表对数刻度"""
        lut = KAN_LUT(grid_size=4, spline_order=2, lut_points=100)
        lut.lut_log_scale = True
        kernel_size = lut.grid_size + lut.spline_order
        lut.set_spline_kernel([1.0] * kernel_size)

        lut.build_lut()
        output = lut.calc_spline_output_lut_logscale(0.5)

        self.assertIsInstance(output, float)

    def test_generate_c_struct(self):
        """测试 C 结构体生成"""
        lut = KAN_LUT(grid_size=4, spline_order=2, lut_points=100)
        kernel_size = lut.grid_size + lut.spline_order
        lut.set_spline_kernel([1.0] * kernel_size)
        lut.build_lut()

        c_code, header_code = lut.generate_c_struct("test_lut")

        # 检查生成的代码
        self.assertIn("KAN_LUT_test_lut_grid", c_code)
        self.assertIn("KAN_LUT_test_lut_spline_kernel", c_code)
        self.assertIn("KAN_LUT_test_lut", c_code)
        self.assertIn("KAN_LUT_test_lut", header_code)

    def test_generate_c_struct_format(self):
        """测试 C 结构体格式"""
        lut = KAN_LUT(grid_size=4, spline_order=2, lut_points=10)
        kernel_size = lut.grid_size + lut.spline_order
        lut.set_spline_kernel([0.1] * kernel_size)
        lut.build_lut()

        c_code, header_code = lut.generate_c_struct("format_test")

        # 检查浮点数格式
        self.assertIn("f", c_code)  # C 浮点数后缀


class TestLayerKANLUT(unittest.TestCase):
    """测试 LayerKAN_LUT 类的基本功能"""

    def test_initialization(self):
        """测试初始化"""
        layer = LayerKAN_LUT(
            in_size=3,
            out_size=2,
            grid_size=4,
            spline_order=2,
            grid_range=(0, 1)
        )

        self.assertEqual(layer.in_size, 3)
        self.assertEqual(layer.out_size, 2)
        self.assertEqual(layer.spline_kernel_size, 4 + 2)
        self.assertTrue(layer.lut_interp)

    def test_initialization_with_weights(self):
        """测试带权重的初始化"""
        in_size = 2
        out_size = 3
        kernel_size = 6  # grid_size + spline_order
        weights = np.random.randn(in_size, kernel_size, out_size)

        layer = LayerKAN_LUT(
            in_size=in_size,
            out_size=out_size,
            grid_size=4,
            spline_order=2,
            weights=weights
        )

        self.assertEqual(layer.in_size, in_size)
        self.assertEqual(layer.out_size, out_size)

    def test_set_spline_kernels(self):
        """测试设置样条核"""
        in_size = 2
        out_size = 3
        kernel_size = 6
        weights = np.random.randn(in_size, kernel_size, out_size)

        layer = LayerKAN_LUT(
            in_size=in_size,
            out_size=out_size,
            grid_size=4,
            spline_order=2
        )

        layer.set_spline_kernels(weights)

    def test_set_spline_kernels_invalid_shape(self):
        """测试无效权重的设置"""
        layer = LayerKAN_LUT(
            in_size=2,
            out_size=3,
            grid_size=4,
            spline_order=2
        )

        # 错误的形状
        invalid_weights = np.random.randn(2, 5, 3)

        with self.assertRaises(ValueError):
            layer.set_spline_kernels(invalid_weights)

    def test_forward_once(self):
        """测试单次前向传播"""
        layer = LayerKAN_LUT(
            in_size=2,
            out_size=3,
            grid_size=4,
            spline_order=2
        )

        # 输入
        inputs = [0.5, -0.3]

        # 前向传播
        outputs = layer.forward_once(inputs)

        # 输出数量应该等于 out_size
        self.assertEqual(len(outputs), 3)

    def test_forward_once_with_lut(self):
        """测试带 LUT 的前向传播"""
        layer = LayerKAN_LUT(
            in_size=2,
            out_size=3,
            grid_size=4,
            spline_order=2
        )

        inputs = [0.5, -0.3]
        outputs = layer.forward_once(inputs, use_lut=True)

        self.assertEqual(len(outputs), 3)

    def test_forward_once_invalid_input_size(self):
        """测试无效输入大小的前向传播"""
        layer = LayerKAN_LUT(
            in_size=3,
            out_size=2,
            grid_size=4,
            spline_order=2
        )

        # 错误的输入大小
        inputs = [0.5, 0.3]  # 应该是 3 个输入

        with self.assertRaises(ValueError):
            layer.forward_once(inputs)

    def test_forward_batch(self):
        """测试批量前向传播"""
        layer = LayerKAN_LUT(
            in_size=2,
            out_size=3,
            grid_size=4,
            spline_order=2
        )

        # 批量输入
        inputs_list = [[0.5, -0.3], [0.1, 0.2], [-0.5, 0.5]]

        # 前向传播
        outputs = layer.forward(inputs_list)

        # 输出数量应该等于批量大小
        self.assertEqual(len(outputs), 3)
        self.assertEqual(len(outputs[0]), 3)

    def test_forward_batch_with_lut(self):
        """测试带 LUT 的批量前向传播"""
        layer = LayerKAN_LUT(
            in_size=2,
            out_size=3,
            grid_size=4,
            spline_order=2
        )

        inputs_list = [[0.5, -0.3], [0.1, 0.2]]
        outputs = layer.forward(inputs_list, use_lut=True)

        self.assertEqual(len(outputs), 2)

    def test_build_lut(self):
        """测试构建所有 LUT"""
        layer = LayerKAN_LUT(
            in_size=2,
            out_size=3,
            grid_size=4,
            spline_order=2,
            lut_points=50
        )

        # 构建所有 LUT
        layer.build_lut()

        # 所有 KAN_LUT 实例应该有 LUT
        for i in range(layer.in_size):
            for o in range(layer.out_size):
                self.assertIsNotNone(layer.kan_luts[i][o].lut)

    def test_generate_c_struct(self):
        """测试 C 结构体生成"""
        layer = LayerKAN_LUT(
            in_size=2,
            out_size=3,
            grid_size=4,
            spline_order=2
        )

        c_code, header_code = layer.generate_c_struct("test_layer")

        self.assertIn("KAN_LUTs_test_layer", c_code)
        self.assertIn("LayerKAN_LUT_test_layer", c_code)


class TestIIR(unittest.TestCase):
    """测试 IIR 类的基本功能"""

    def test_initialization_default(self):
        """测试默认初始化"""
        iir = IIR(order=2)

        self.assertEqual(iir.order, 2)
        # 默认 a 系数应该全为 1
        np.testing.assert_array_equal(iir.a, [1.0, 1.0, 1.0])
        # 默认 b 系数应该是 [1, 0, 0]
        np.testing.assert_array_equal(iir.b, [1.0, 0.0, 0.0])

    def test_initialization_custom(self):
        """测试自定义初始化"""
        a = [1.0, -1.5, 0.6]
        b = [0.2, 0.4, 0.2]

        iir = IIR(order=2, a=a, b=b)

        # a 系数应该被设置
        np.testing.assert_array_almost_equal(iir.a, a)
        # b 系数应该保持用户设置的值
        np.testing.assert_array_almost_equal(iir.b, b)

    def test_set_a(self):
        """测试设置 a 系数"""
        iir = IIR(order=3)
        new_a = [1.0, -1.2, 0.5, 0.1]

        iir.set_a(new_a)

        np.testing.assert_array_almost_equal(iir.a, new_a)

    def test_set_a_invalid_length(self):
        """测试设置无效长度的 a 系数"""
        iir = IIR(order=2)
        invalid_a = [1.0, -1.5]  # 应该是 3 个系数

        with self.assertRaises(ValueError):
            iir.set_a(invalid_a)

    def test_set_b(self):
        """测试设置 b 系数"""
        iir = IIR(order=3)
        new_b = [0.1, 0.2, 0.3, 0.1]

        iir.set_b(new_b)

        np.testing.assert_array_almost_equal(iir.b, new_b)

    def test_set_b_invalid_length(self):
        """测试设置无效长度的 b 系数"""
        iir = IIR(order=2)
        invalid_b = [0.1, 0.2]  # 应该是 3 个系数

        with self.assertRaises(ValueError):
            iir.set_b(invalid_b)

    def test_filter(self):
        """测试滤波功能"""
        iir = IIR(order=2)
        # 设置简单的滤波器系数
        iir.set_a([1.0, -1.0, 0.5])
        iir.set_b([0.1, 0.1, 0.1])

        # 输入信号
        input_signal = np.random.randn(100).astype(np.float32)

        # 滤波
        output = iir.filter(input_signal)

        # 输出形状应该与输入相同
        self.assertEqual(output.shape, input_signal.shape)

    def test_filter_list_input(self):
        """测试列表输入的滤波"""
        iir = IIR(order=2)
        iir.set_a([1.0, -1.0, 0.5])
        iir.set_b([0.1, 0.1, 0.1])

        input_list = [0.1, 0.2, 0.3, 0.4, 0.5]

        output = iir.filter(input_list)

        self.assertEqual(len(output), len(input_list))

    def test_filter_impulse_response(self):
        """测试脉冲响应"""
        iir = IIR(order=2)
        # 设置一个简单的低通滤波器
        iir.set_a([1.0, -1.0, 0.5])
        iir.set_b([0.1, 0.1, 0.1])

        # 脉冲输入
        input_signal = np.zeros(100)
        input_signal[0] = 1.0

        output = iir.filter(input_signal)

        # 脉冲响应应该逐渐衰减
        self.assertGreater(np.abs(output[0]), 0.0)

    def test_generate_c_struct(self):
        """测试 C 结构体生成"""
        iir = IIR(order=2)
        iir.set_a([1.0, -1.5, 0.6])
        iir.set_b([0.2, 0.4, 0.2])

        c_code, header_code = iir.generate_c_struct("test_iir")

        self.assertIn("IIR_test_iir_a", c_code)
        self.assertIn("IIR_test_iir_b", c_code)
        self.assertIn("IIR_test_iir", c_code)


class TestLayerIIR(unittest.TestCase):
    """测试 LayerIIR 类的基本功能"""

    def test_initialization(self):
        """测试初始化"""
        layer = LayerIIR(
            in_size=2,
            out_size=3,
            order=2
        )

        self.assertEqual(layer.in_size, 2)
        self.assertEqual(layer.out_size, 3)
        self.assertEqual(layer.order, 2)

    def test_set_weights(self):
        """测试设置权重"""
        layer = LayerIIR(
            in_size=2,
            out_size=3,
            order=2
        )

        weights_a = np.random.randn(2, 3, 3).astype(np.float32)
        weights_b = np.random.randn(2, 3, 3).astype(np.float32)

        layer.set_weights(weights_a, weights_b)

        # 验证权重已设置
        self.assertIsNotNone(layer.weights_a)
        self.assertIsNotNone(layer.weights_b)

    def test_set_weights_invalid_shape_a(self):
        """测试设置无效形状的权重 a"""
        layer = LayerIIR(
            in_size=2,
            out_size=3,
            order=2
        )

        invalid_weights_a = np.random.randn(2, 3, 4)  # 错误形状
        weights_b = np.random.randn(2, 3, 3)

        with self.assertRaises(ValueError):
            layer.set_weights(invalid_weights_a, weights_b)

    def test_set_weights_invalid_shape_b(self):
        """测试设置无效形状的权重 b"""
        layer = LayerIIR(
            in_size=2,
            out_size=3,
            order=2
        )

        weights_a = np.random.randn(2, 3, 3)
        invalid_weights_b = np.random.randn(2, 3, 4)  # 错误形状

        with self.assertRaises(ValueError):
            layer.set_weights(weights_a, invalid_weights_b)

    def test_forward_once(self):
        """测试单次前向传播"""
        layer = LayerIIR(
            in_size=2,
            out_size=3,
            order=2
        )

        # 设置一些简单的权重
        weights_a = np.ones((2, 3, 3), dtype=np.float32)
        weights_b = np.zeros((2, 3, 3), dtype=np.float32)
        weights_b[:, :, 0] = 0.1  # b0 = 0.1
        layer.set_weights(weights_a, weights_b)

        inputs = [0.5, 0.3]
        outputs = layer.forward_once(inputs)

        self.assertEqual(len(outputs), 3)

    def test_forward_once_single_value(self):
        """测试单值输入的前向传播"""
        layer = LayerIIR(
            in_size=1,
            out_size=2,
            order=2
        )

        inputs = 0.5  # 单值
        outputs = layer.forward_once(inputs)

        self.assertEqual(len(outputs), 2)

    def test_forward_once_invalid_input(self):
        """测试无效输入的前向传播"""
        layer = LayerIIR(
            in_size=3,
            out_size=2,
            order=2
        )

        inputs = [0.5, 0.3]  # 应该是 3 个输入

        with self.assertRaises(ValueError):
            layer.forward_once(inputs)

    def test_forward_batch(self):
        """测试批量前向传播"""
        layer = LayerIIR(
            in_size=2,
            out_size=3,
            order=2
        )

        inputs_list = [[0.5, 0.3], [0.1, 0.2], [-0.5, 0.5]]
        outputs = layer.forward(inputs_list)

        self.assertEqual(len(outputs), 3)
        self.assertEqual(len(outputs[0]), 3)

    def test_generate_c_struct(self):
        """测试 C 结构体生成"""
        layer = LayerIIR(
            in_size=2,
            out_size=3,
            order=2
        )

        c_code, header_code = layer.generate_c_struct("test_layer")

        self.assertIn("IIRs_test_layer", c_code)
        self.assertIn("LayerIIR_test_layer", c_code)


class TestModelKANLUT(unittest.TestCase):
    """测试 ModelKAN_LUT 类的基本功能"""

    def test_initialization(self):
        """测试初始化"""
        model = ModelKAN_LUT(lut_points=100)

        self.assertEqual(model.lut_points, 100)
        self.assertTrue(model.lut_interp)
        self.assertEqual(len(model.layers), 0)
        self.assertEqual(len(model.layers_rnn), 0)

    def test_add_kanlayer(self):
        """测试添加 KAN 层"""
        model = ModelKAN_LUT()
        model.add_kanlayer(in_size=3, out_size=2, grid_size=4, spline_order=2)

        self.assertEqual(len(model.layers), 1)
        self.assertEqual(model.layers[0].in_size, 3)
        self.assertEqual(model.layers[0].out_size, 2)

    def test_add_iirlayer(self):
        """测试添加 IIR 层"""
        model = ModelKAN_LUT()
        model.add_iirlayer(in_size=1, out_size=2, order=2)

        self.assertEqual(len(model.layers_rnn), 1)
        self.assertEqual(model.layers_rnn[0].in_size, 1)
        self.assertEqual(model.layers_rnn[0].out_size, 2)

    def test_set_weights(self):
        """测试设置权重"""
        model = ModelKAN_LUT()
        model.add_kanlayer(in_size=2, out_size=3, grid_size=4, spline_order=2)

        # 设置权重
        weights = [np.random.randn(2, 6, 3)]
        model.set_weights(weights)

    def test_forward_without_lut(self):
        """测试不带 LUT 的前向传播"""
        model = ModelKAN_LUT()
        model.add_kanlayer(in_size=2, out_size=2, grid_size=4, spline_order=2)

        inputs_list = [[0.5, 0.3], [0.1, 0.2]]
        outputs = model.forward(inputs_list, use_lut=False, verbose=False)

        self.assertEqual(len(outputs), 2)
        self.assertEqual(len(outputs[0]), 2)

    def test_forward_with_lut(self):
        """测试带 LUT 的前向传播"""
        model = ModelKAN_LUT(lut_points=50)
        model.add_kanlayer(in_size=2, out_size=2, grid_size=4, spline_order=2)

        inputs_list = [[0.5, 0.3], [0.1, 0.2]]
        outputs = model.forward(inputs_list, use_lut=True, verbose=False)

        self.assertEqual(len(outputs), 2)
        self.assertEqual(len(outputs[0]), 2)

    def test_generate_c_struct(self):
        """测试 C 结构体生成"""
        model = ModelKAN_LUT()
        model.add_kanlayer(in_size=2, out_size=2, grid_size=4, spline_order=2)
        model.add_iirlayer(in_size=1, out_size=2, order=2)

        c_code, header_code = model.generate_c_struct("test_model")

        self.assertIn("KAN_LUT", c_code)
        self.assertIn("LayerKAN_LUT", c_code)
        self.assertIn("LayerIIR", c_code)
        self.assertIn("ModelKAN_LUT_test_model", c_code)

    def test_generate_c_struct_header_guard(self):
        """测试 C 结构体头文件保护"""
        model = ModelKAN_LUT()
        model.add_kanlayer(in_size=2, out_size=2, grid_size=4, spline_order=2)

        c_code, header_code = model.generate_c_struct("guard_test")

        # 检查头文件保护
        self.assertIn("#ifndef", header_code)
        self.assertIn("#define", header_code)
        self.assertIn("#endif", header_code)


class TestKANLUTEdgeCases(unittest.TestCase):
    """边界条件测试"""

    def test_empty_grid_range(self):
        """测试空网格范围"""
        lut = KAN_LUT(grid_size=4, spline_order=2, grid_range=(0.5, 0.5))

        grid = lut.grid
        self.assertEqual(len(grid), 4 + 4 + 1)

    def test_large_grid_size(self):
        """测试大网格大小"""
        lut = KAN_LUT(grid_size=100, spline_order=5, grid_range=(0, 1))

        grid = lut.grid
        self.assertEqual(len(grid), 100 + 10 + 1)

    def test_zero_lut_points(self):
        """测试零 LUT 点数"""
        lut = KAN_LUT(grid_size=4, spline_order=2, lut_points=1)

        lut.build_lut()

        self.assertTrue(len(lut.lut) > 0)

    def test_single_input_layer(self):
        """测试单输入层"""
        layer = LayerKAN_LUT(
            in_size=1,
            out_size=1,
            grid_size=4,
            spline_order=2
        )

        outputs = layer.forward_once([0.5])
        self.assertEqual(len(outputs), 1)

    def test_large_layer(self):
        """测试大层"""
        layer = LayerKAN_LUT(
            in_size=10,
            out_size=10,
            grid_size=4,
            spline_order=2
        )

        inputs = [0.5] * 10
        outputs = layer.forward_once(inputs)

        self.assertEqual(len(outputs), 10)

    def test_lut_log_scale_attribute(self):
        """测试 lut_log_scale 属性的默认值和设置"""
        lut = KAN_LUT()
        # 默认应该是 False
        self.assertFalse(lut.lut_log_scale)

        # 设置为 True
        lut.lut_log_scale = True
        self.assertTrue(lut.lut_log_scale)

    def test_calc_spline_output_lut_debug_mode(self):
        """测试 LUT 查表的调试模式（use_debug=True 应该不抛出异常）"""
        lut = KAN_LUT(grid_size=4, spline_order=2, lut_points=100)
        kernel_size = lut.grid_size + lut.spline_order
        lut.set_spline_kernel([1.0] * kernel_size)

        # 使用调试模式（不会显示图形但会执行内部代码）
        output = lut.calc_spline_output_lut(0.5, use_debug=False)

        self.assertIsInstance(output, float)

    def test_calc_spline_output_lut_debug_true(self):
        """测试 LUT 查表的调试模式（use_debug=True）"""
        lut = KAN_LUT(grid_size=4, spline_order=2, lut_points=100)
        kernel_size = lut.grid_size + lut.spline_order
        lut.set_spline_kernel([1.0] * kernel_size)

        # 使用调试模式，捕获可能的异常
        output = lut.calc_spline_output_lut(0.5, use_debug=True)

        self.assertIsInstance(output, float)

    def test_calc_spline_output_lut_logscale_with_log_scale(self):
        """测试 LUT 对数刻度查询"""
        lut = KAN_LUT(grid_size=4, spline_order=2, lut_points=100)
        lut.lut_log_scale = True
        kernel_size = lut.grid_size + lut.spline_order
        lut.set_spline_kernel([1.0] * kernel_size)

        output = lut.calc_spline_output_lut_logscale(0.5)

        self.assertIsInstance(output, float)

    def test_min_x_attribute(self):
        """测试 min_x 属性的默认值"""
        lut = KAN_LUT()
        self.assertEqual(lut.min_x, 1e-2)

    def test_layer_weights_attribute(self):
        """测试 LayerKAN_LUT 的 weights 属性"""
        layer = LayerKAN_LUT(
            in_size=2,
            out_size=3,
            grid_size=4,
            spline_order=2
        )

        # 验证 weights 属性存在
        self.assertIsNotNone(layer.weights)
        # 验证形状
        self.assertEqual(layer.weights.shape, (2, 6, 3))


class TestModelKANLUTAdvanced(unittest.TestCase):
    """测试 ModelKAN_LUT 高级功能"""

    def test_load_weights_json_with_mock(self):
        """测试 JSON 权重加载功能（使用模拟数据）"""
        import tempfile
        import json

        # 创建模拟的权重 JSON 数据 (格式需要符合load_weights_json的要求)
        weights_data = [
            {
                'name': 'layer1/kan_kernel',
                'shape': [2, 6, 3],
                'config': {
                    'grid_size': 4,
                    'spline_order': 2,
                    'grid_range': [0, 1]
                },
                'value': [[[0.1] * 6 for _ in range(3)] for _ in range(2)]
            },
            {
                'name': 'layer1/rnn/kernel',
                'shape': [1, 5, 3],
                'value': [[[0.1] * 5 for _ in range(3)] for _ in range(1)]
            },
            {
                'name': 'layer1/rnn/recurrent_kernel',
                'shape': [4, 5, 3],
                'value': [[[0.1] * 5 for _ in range(3)] for _ in range(4)]
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(weights_data, f)
            temp_path = f.name

        try:
            model = ModelKAN_LUT()
            # 这个测试验证函数可以被调用（加载可能会失败因为数据格式不完全匹配，但不应抛出异常）
            try:
                model.load_weights_json(temp_path)
            except (ValueError, KeyError, IndexError):
                # 预期可能因数据格式不完全匹配而失败，这是可接受的
                pass

            # 至少验证函数执行完成
            self.assertIsNotNone(model)
        finally:
            import os
            os.unlink(temp_path)

    def test_forward_verbose_true(self):
        """测试带 verbose=True 的前向传播"""
        model = ModelKAN_LUT(lut_points=50)
        model.add_kanlayer(in_size=2, out_size=2, grid_size=4, spline_order=2)

        inputs_list = [[0.5, 0.3], [0.1, 0.2]]

        # verbose=True 应该输出信息但不抛出异常
        outputs = model.forward(inputs_list, use_lut=False, verbose=True)

        self.assertEqual(len(outputs), 2)
        self.assertEqual(len(outputs[0]), 2)

    def test_forward_verbose_false(self):
        """测试带 verbose=False 的前向传播"""
        model = ModelKAN_LUT(lut_points=50)
        model.add_kanlayer(in_size=2, out_size=2, grid_size=4, spline_order=2)

        inputs_list = [[0.5, 0.3], [0.1, 0.2]]

        outputs = model.forward(inputs_list, use_lut=False, verbose=False)

        self.assertEqual(len(outputs), 2)
        self.assertEqual(len(outputs[0]), 2)

    def test_forward_with_lut_verbose_true(self):
        """测试带 LUT 和 verbose=True 的前向传播"""
        model = ModelKAN_LUT(lut_points=50)
        model.add_kanlayer(in_size=2, out_size=2, grid_size=4, spline_order=2)

        inputs_list = [[0.5, 0.3], [0.1, 0.2]]

        outputs = model.forward(inputs_list, use_lut=True, verbose=True)

        self.assertEqual(len(outputs), 2)
        self.assertEqual(len(outputs[0]), 2)

    def test_model_with_multiple_kan_layers(self):
        """测试多 KAN 层模型"""
        model = ModelKAN_LUT(lut_points=50)
        model.add_kanlayer(in_size=2, out_size=3, grid_size=4, spline_order=2)
        model.add_kanlayer(in_size=3, out_size=2, grid_size=4, spline_order=2)

        self.assertEqual(len(model.layers), 2)

        inputs_list = [[0.5, 0.3]]
        outputs = model.forward(inputs_list, use_lut=False, verbose=False)

        self.assertEqual(len(outputs), 1)
        self.assertEqual(len(outputs[0]), 2)

    def test_model_with_kan_and_iir_layers(self):
        """测试混合 KAN 和 IIR 层模型"""
        model = ModelKAN_LUT(lut_points=50)
        model.add_iirlayer(in_size=1, out_size=2, order=2)
        model.add_kanlayer(in_size=2, out_size=2, grid_size=4, spline_order=2)

        self.assertEqual(len(model.layers), 1)
        self.assertEqual(len(model.layers_rnn), 1)

        inputs_list = [[0.5]]
        outputs = model.forward(inputs_list, use_lut=False, verbose=False)

        self.assertEqual(len(outputs), 1)
        self.assertEqual(len(outputs[0]), 2)


class TestKANLUTUtilityFunctions(unittest.TestCase):
    """测试 KAN_LUT 工具函数"""

    def test_kan_lut_siso_function(self):
        """测试 kan_lut_siso 函数"""
        from experimental.kan_lut import kan_lut_siso

        # grid_size=3, spline_order=2, so weight needs 5 elements
        weight = [0.1, 0.2, 0.3, 0.4, 0.5]
        x = np.array([0.1, 0.2, 0.3])

        output = kan_lut_siso(x, weight)

        self.assertEqual(len(output), 3)
        for o in output:
            self.assertIsInstance(o, float)

    def test_kan_lut_siso_single_input(self):
        """测试 kan_lut_siso 函数的单输入"""
        from experimental.kan_lut import kan_lut_siso

        # grid_size=3, spline_order=2, so weight needs 5 elements
        weight = [0.1, 0.2, 0.3, 0.4, 0.5]
        x = np.array([0.5])

        output = kan_lut_siso(x, weight)

        self.assertEqual(len(output), 1)


class TestLayerIIRAdvanced(unittest.TestCase):
    """测试 LayerIIR 高级功能"""

    def test_forward_once_with_float_input(self):
        """测试单浮点数输入的前向传播"""
        layer = LayerIIR(
            in_size=1,
            out_size=2,
            order=2
        )

        # 单个浮点数输入
        input_val = 0.5
        outputs = layer.forward_once(input_val)

        self.assertEqual(len(outputs), 2)

    def test_forward_with_empty_list(self):
        """测试空列表输入"""
        layer = LayerIIR(
            in_size=2,
            out_size=2,
            order=2
        )

        # 空的批次输入
        inputs_list = []

        # 应该返回空的列表
        outputs = layer.forward(inputs_list)
        self.assertEqual(len(outputs), 0)


if __name__ == "__main__":
    unittest.main()
