#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试 tfkan 模块的核心功能
包含 ops/grid.py, ops/spline.py, layers/base.py, layers/dense.py 的单元测试
"""

import unittest
import sys
import os

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import tensorflow as tf
import numpy as np

# 导入被测试模块
from tfkan.ops.grid import build_adaptive_grid
from tfkan.ops.spline import calc_spline_values, fit_spline_coef
from tfkan.layers.base import PiecewiseActivationLayer, LayerKAN
from tfkan.layers.dense import DenseKAN


class TestBuildAdaptiveGrid(unittest.TestCase):
    """测试 build_adaptive_grid 函数"""

    def test_grid_shape(self):
        """测试网格形状"""
        batch_size = 32
        in_size = 5
        grid_size = 8
        spline_order = 3

        x = tf.random.normal((batch_size, in_size))
        grid = build_adaptive_grid(x, grid_size, spline_order)

        # 网格形状应该是 (in_size, grid_size + 2 * spline_order + 1)
        expected_shape = (in_size, grid_size + 2 * spline_order + 1)
        self.assertEqual(grid.shape, expected_shape)

    def test_grid_dtype(self):
        """测试网格数据类型"""
        batch_size = 16
        in_size = 3
        grid_size = 5
        spline_order = 2

        x = tf.random.normal((batch_size, in_size), dtype=tf.float32)
        grid = build_adaptive_grid(x, grid_size, spline_order)

        self.assertEqual(grid.dtype, tf.float32)

    def test_grid_extends_beyond_data_range(self):
        """测试网格范围扩展"""
        batch_size = 32
        in_size = 2
        grid_size = 4
        spline_order = 2

        # 创建有特定范围的数据
        x = tf.constant([[0.2, 0.3], [0.8, 0.7]], dtype=tf.float32)
        # 复制到 batch_size
        x = tf.tile(x, [batch_size // 2, 1])

        grid = build_adaptive_grid(x, grid_size, spline_order)

        # 网格应该扩展到数据范围之外
        # 第一列应该小于最小值，最后一列应该大于最大值
        min_val = tf.reduce_min(x)
        max_val = tf.reduce_max(x)

        self.assertLess(grid[0, 0], min_val)
        self.assertGreater(grid[0, -1], max_val)

    def test_grid_with_single_sample(self):
        """测试单样本网格"""
        in_size = 3
        grid_size = 5
        spline_order = 2

        x = tf.constant([[0.5, 0.6, 0.7]], dtype=tf.float32)
        grid = build_adaptive_grid(x, grid_size, spline_order)

        self.assertEqual(grid.shape, (in_size, grid_size + 2 * spline_order + 1))

    def test_grid_with_different_grid_sizes(self):
        """测试不同网格大小"""
        batch_size = 32
        in_size = 2

        for grid_size in [4, 8, 16]:
            for spline_order in [1, 2, 3]:
                x = tf.random.normal((batch_size, in_size))
                grid = build_adaptive_grid(x, grid_size, spline_order)

                expected_cols = grid_size + 2 * spline_order + 1
                self.assertEqual(grid.shape[1], expected_cols)

    def test_grid_monotonic(self):
        """测试网格单调性"""
        batch_size = 32
        in_size = 1
        grid_size = 8
        spline_order = 3

        x = tf.random.uniform((batch_size, in_size), minval=0.1, maxval=0.9)
        grid = build_adaptive_grid(x, grid_size, spline_order)

        # 每行应该单调递增
        for i in range(grid.shape[0]):
            row = grid[i].numpy()
            for j in range(len(row) - 1):
                self.assertLessEqual(row[j], row[j + 1])


class TestCalcSplineValues(unittest.TestCase):
    """测试 calc_spline_values 函数"""

    def test_output_shape(self):
        """测试输出形状"""
        batch_size = 32
        in_size = 5
        grid_size = 8
        spline_order = 3

        x = tf.random.normal((batch_size, in_size))
        grid = tf.random.uniform((in_size, grid_size + 2 * spline_order + 1))

        bases = calc_spline_values(x, grid, spline_order)

        # 输出形状应该是 (batch_size, in_size, grid_size + spline_order)
        expected_shape = (batch_size, in_size, grid_size + spline_order)
        self.assertEqual(bases.shape, expected_shape)

    def test_bases_non_negative(self):
        """测试基函数非负"""
        batch_size = 16
        in_size = 3
        grid_size = 5
        spline_order = 2

        x = tf.random.uniform((batch_size, in_size), minval=0.0, maxval=1.0)
        grid = tf.linspace(0.0, 1.0, in_size * (grid_size + 2 * spline_order + 1))
        grid = tf.reshape(grid, (in_size, grid_size + 2 * spline_order + 1))

        bases = calc_spline_values(x, grid, spline_order)

        # 所有基函数值应该 >= 0
        self.assertGreaterEqual(tf.reduce_min(bases), 0.0)

    def test_spline_order_0(self):
        """测试 0 阶样条"""
        batch_size = 8
        in_size = 2
        grid_size = 8
        spline_order = 0

        x = tf.random.uniform((batch_size, in_size), minval=0.0, maxval=1.0)
        grid = tf.linspace(0.0, 1.0, in_size * (grid_size + 1))
        grid = tf.reshape(grid, (in_size, grid_size + 1))

        bases = calc_spline_values(x, grid, spline_order)

        # 0 阶样条应该有 grid_size 个基函数
        self.assertEqual(bases.shape[2], grid_size)

    def test_spline_order_1(self):
        """测试 1 阶样条"""
        batch_size = 8
        in_size = 2
        grid_size = 8
        spline_order = 1

        x = tf.random.uniform((batch_size, in_size), minval=0.0, maxval=1.0)
        grid = tf.linspace(0.0, 1.0, in_size * (grid_size + 2 + 1))
        grid = tf.reshape(grid, (in_size, grid_size + 2 * spline_order + 1))

        bases = calc_spline_values(x, grid, spline_order)

        # 1 阶样条应该有 grid_size + 1 个基函数
        self.assertEqual(bases.shape[2], grid_size + spline_order)


class TestFitSplineCoef(unittest.TestCase):
    """测试 fit_spline_coef 函数"""

    def test_coef_shape(self):
        """测试系数形状"""
        batch_size = 64
        in_size = 2
        out_size = 1
        grid_size = 6
        spline_order = 2

        # 使用更大的 batch_size 和 well-conditioned 数据
        x = tf.random.uniform((batch_size, in_size), minval=0.1, maxval=0.9)
        y = tf.random.normal((batch_size, in_size, out_size))
        grid = tf.linspace(0.0, 1.0, in_size * (grid_size + 2 * spline_order + 1))
        grid = tf.reshape(grid, (in_size, grid_size + 2 * spline_order + 1))

        coef = fit_spline_coef(x, y, grid, spline_order)

        # 系数形状应该是 (in_size, grid_size + spline_order, out_size)
        expected_shape = (in_size, grid_size + spline_order, out_size)
        self.assertEqual(coef.shape, expected_shape)


class TestPiecewiseActivationLayer(unittest.TestCase):
    """测试 PiecewiseActivationLayer 类"""

    def test_initialization(self):
        """测试初始化"""
        xn = [0.1, 0.3, 0.5, 0.7, 0.9]
        yn = [0.0, 0.2, 0.4, 0.6, 0.8]

        layer = PiecewiseActivationLayer(xn, yn)

        # 应该自动添加 (0, 0) 点
        self.assertEqual(layer.xn[0], 0.0)
        self.assertEqual(layer.yn[0], 0.0)

    def test_initialization_with_zero(self):
        """测试已包含零点的初始化"""
        xn = [0.0, 0.2, 0.4, 0.6, 0.8]
        yn = [0.0, 0.1, 0.2, 0.3, 0.4]

        layer = PiecewiseActivationLayer(xn, yn)

        # 不应该重复添加 (0, 0) 点
        self.assertEqual(layer.xn[0], 0.0)
        self.assertEqual(layer.yn[0], 0.0)

    def test_piecewise_activation_output_shape(self):
        """测试输出形状"""
        xn = [0.0, 0.5, 1.0]
        yn = [0.0, 0.5, 1.0]

        layer = PiecewiseActivationLayer(xn, yn)

        x = tf.constant([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]], dtype=tf.float32)
        y = layer(x)

        self.assertEqual(y.shape, x.shape)

    def test_piecewise_activation_symmetry(self):
        """测试奇对称性 y(-x) = -y(x)"""
        xn = [0.0, 0.5, 1.0]
        yn = [0.0, 0.5, 1.0]

        layer = PiecewiseActivationLayer(xn, yn)

        x_pos = tf.constant([[0.3, 0.5], [0.7, 0.9]], dtype=tf.float32)
        x_neg = -x_pos

        y_pos = layer(x_pos)
        y_neg = layer(x_neg)

        # 应该满足 y(-x) = -y(x)
        np.testing.assert_array_almost_equal(y_pos, -y_neg)

    def test_piecewise_activation_linear(self):
        """测试线性分段激活"""
        # 线性函数 y = x
        xn = [0.0, 0.5, 1.0]
        yn = [0.0, 0.5, 1.0]

        layer = PiecewiseActivationLayer(xn, yn)

        x = tf.constant([[0.0, 0.25, 0.5, 0.75, 1.0]], dtype=tf.float32)
        y = layer(x)

        # 线性函数应该几乎保持不变（可能有数值误差）
        np.testing.assert_array_almost_equal(y.numpy()[0], x.numpy()[0], decimal=5)

    def test_from_xk(self):
        """测试从 x 和 k 创建层"""
        x = [0.2, 0.4, 0.6, 0.8]
        k = [1.0, 1.0, 1.0, 1.0]  # 斜率

        layer = PiecewiseActivationLayer.from_xk(x, k)

        # 验证输出
        x_test = tf.constant([[0.1, 0.3, 0.5, 0.7, 0.9]], dtype=tf.float32)
        y = layer(x_test)

        # 由于斜率都是 1，输出应该接近 x（通过原点）
        self.assertGreater(y[0, 0].numpy(), 0.0)

    def test_reverse(self):
        """测试反函数"""
        # 线性函数 y = x
        xn = [0.0, 0.5, 1.0]
        yn = [0.0, 0.5, 1.0]

        layer = PiecewiseActivationLayer(xn, yn)
        inverse = layer.reverse()

        # 验证 y = f(x), x = f^{-1}(y)
        x = tf.constant([[0.3, 0.5, 0.7]], dtype=tf.float32)
        y = layer(x)
        x_reconstructed = inverse(y)

        np.testing.assert_array_almost_equal(x, x_reconstructed, decimal=5)

    def test_reverse_non_monotonic(self):
        """测试非单调函数的反函数"""
        # 非单调函数
        xn = [0.0, 0.3, 0.7, 1.0]
        yn = [0.0, 0.5, 0.2, 0.8]

        layer = PiecewiseActivationLayer(xn, yn)

        with self.assertRaises(ValueError):
            layer.reverse()


class TestDenseKAN(unittest.TestCase):
    """测试 DenseKAN 层"""

    def test_initialization(self):
        """测试初始化"""
        layer = DenseKAN(units=8)

        self.assertEqual(layer.units, 8)
        self.assertEqual(layer.grid_size, 5)
        self.assertEqual(layer.spline_order, 3)
        self.assertEqual(layer.grid_range, (-1.0, 1.0))
        self.assertFalse(layer.built)

    def test_initialization_custom(self):
        """测试自定义初始化"""
        layer = DenseKAN(
            units=16,
            grid_size=8,
            spline_order=4,
            grid_range=(0, 1),
            use_bias=True,
            fix_scale_factor=True,
            disable_basis_activation=True
        )

        self.assertEqual(layer.units, 16)
        self.assertEqual(layer.grid_size, 8)
        self.assertEqual(layer.spline_order, 4)
        self.assertEqual(layer.grid_range, (0, 1))
        self.assertTrue(layer.fix_scale_factor)
        self.assertTrue(layer.disable_basis_activation)

    def test_build(self):
        """测试 build"""
        layer = DenseKAN(units=4, grid_size=4, spline_order=2)

        input_shape = (None, 8)  # batch_size, in_size
        layer.build(input_shape)

        self.assertTrue(layer.built)
        self.assertEqual(layer.in_size, 8)

    def test_build_with_int_input_shape(self):
        """测试使用整数输入形状的 build"""
        layer = DenseKAN(units=4)

        layer.build(8)  # in_size = 8

        self.assertTrue(layer.built)
        self.assertEqual(layer.in_size, 8)

    def test_call(self):
        """测试前向传播"""
        layer = DenseKAN(units=4, grid_size=4, spline_order=2)
        layer.build(input_shape=(None, 8))

        x = tf.random.normal((16, 8))
        y = layer(x)

        self.assertEqual(y.shape, (16, 4))

    def test_call_with_different_batch_sizes(self):
        """测试不同批次大小的前向传播"""
        layer = DenseKAN(units=2, grid_size=4, spline_order=2)
        layer.build(input_shape=(None, 4))

        for batch_size in [1, 8, 32, 64]:
            x = tf.random.normal((batch_size, 4))
            y = layer(x)
            self.assertEqual(y.shape[0], batch_size)
            self.assertEqual(y.shape[1], 2)

    def test_call_with_different_input_sizes(self):
        """测试不同输入大小的前向传播"""
        for in_size in [1, 2, 4, 8, 16]:
            layer = DenseKAN(units=2, grid_size=4, spline_order=2)
            layer.build(input_shape=(None, in_size))

            x = tf.random.normal((8, in_size))
            y = layer(x)
            self.assertEqual(y.shape, (8, 2))

    def test_spline_kernel_shape(self):
        """测试样条核形状"""
        in_size = 4
        out_size = 3
        grid_size = 5
        spline_order = 2

        layer = DenseKAN(units=out_size, grid_size=grid_size, spline_order=spline_order)
        layer.build(input_shape=(None, in_size))

        # 核形状应该是 (in_size, grid_size + spline_order, units)
        expected_shape = (in_size, grid_size + spline_order, out_size)
        self.assertEqual(layer.spline_kernel.shape, expected_shape)

    def test_grid_shape(self):
        """测试网格形状"""
        in_size = 5
        grid_size = 6
        spline_order = 3

        layer = DenseKAN(units=4, grid_size=grid_size, spline_order=spline_order)
        layer.build(input_shape=(None, in_size))

        # 网格形状应该是 (in_size, grid_size + 2 * spline_order + 1)
        expected_shape = (in_size, grid_size + 2 * spline_order + 1)
        self.assertEqual(layer.grid.shape, expected_shape)

    def test_compute_spline_output(self):
        """测试样条输出计算"""
        layer = DenseKAN(units=2, grid_size=4, spline_order=2)
        layer.build(input_shape=(None, 4))

        x = tf.random.normal((8, 4))
        spline_out = layer.compute_spline_output(x)

        # 输出形状应该是 (batch_size, in_size, units)
        self.assertEqual(spline_out.shape, (8, 4, 2))

    def test_extend_grid_from_samples(self):
        """测试从样本扩展网格"""
        original_grid_size = 4
        extend_grid_size = 8

        layer = DenseKAN(units=2, grid_size=original_grid_size, spline_order=2)
        layer.build(input_shape=(None, 4))

        # 创建输入样本
        x = tf.random.normal((32, 4))

        # 扩展网格
        layer.extend_grid_from_samples(x, extend_grid_size=extend_grid_size)

        # 网格大小应该被更新
        self.assertEqual(layer.grid_size, extend_grid_size)

    def test_extend_grid_invalid_size(self):
        """测试无效扩展大小的错误处理"""
        layer = DenseKAN(units=2, grid_size=8, spline_order=2)
        layer.build(input_shape=(None, 4))

        x = tf.random.normal((32, 4))

        # 尝试扩展到更小的网格
        with self.assertRaises(ValueError):
            layer.extend_grid_from_samples(x, extend_grid_size=4)

    def test_without_bias(self):
        """测试无偏置的层"""
        layer = DenseKAN(units=4, use_bias=False)
        layer.build(input_shape=(None, 8))

        self.assertIsNone(layer.bias)

        x = tf.random.normal((8, 8))
        y = layer(x)

        self.assertEqual(y.shape, (8, 4))

    def test_with_scale_factor(self):
        """测试带缩放因子的层"""
        layer = DenseKAN(units=4, fix_scale_factor=False)
        layer.build(input_shape=(None, 8))

        self.assertIsNotNone(layer.scale_factor)

        x = tf.random.normal((8, 8))
        y = layer(x)

        self.assertEqual(y.shape, (8, 4))

    def test_model_integration(self):
        """测试模型集成"""
        model = tf.keras.Sequential([
            DenseKAN(units=16, grid_size=5, spline_order=2),
            tf.keras.layers.Dense(8),
            tf.keras.layers.ReLU(),
            DenseKAN(units=4, grid_size=5, spline_order=2)
        ])

        model.build(input_shape=(None, 10))

        x = tf.random.normal((16, 10))
        y = model(x)

        self.assertEqual(y.shape, (16, 4))


class TestLayerKAN(unittest.TestCase):
    """测试 LayerKAN 抽象类方法"""

    def test_calc_spline_output_origin(self):
        """测试原始样条输出"""
        layer = DenseKAN(units=2, grid_size=4, spline_order=2)
        layer.build(input_shape=(None, 4))

        x = tf.random.normal((8, 4))
        spline_out = layer.calc_spline_output_origin(x)

        self.assertEqual(spline_out.shape, (8, 4, 2))

    def test_calc_spline_output_symmetry(self):
        """测试对称样条输出"""
        layer = DenseKAN(units=2, grid_size=4, spline_order=2)
        layer.build(input_shape=(None, 4))

        x = tf.random.normal((8, 4))
        spline_out = layer.calc_spline_output_symmetry(x)

        self.assertEqual(spline_out.shape, (8, 4, 2))

    def test_calc_spline_output_with_even_symmetry(self):
        """测试偶对称样条输出"""
        layer = DenseKAN(units=2, grid_size=4, spline_order=2)
        layer.build(input_shape=(None, 4))

        x = tf.random.normal((8, 4))
        spline_out = layer.calc_spline_output_symmetry(x, use_even=True)

        self.assertEqual(spline_out.shape, (8, 4, 2))

    def test_calc_spline_output_with_zero_point(self):
        """测试过零点的样条输出"""
        layer = DenseKAN(units=2, grid_size=4, spline_order=2)
        layer.build(input_shape=(None, 4))

        x = tf.random.normal((8, 4))
        spline_out = layer.calc_spline_output_symmetry(x, use_zero_point=True)

        self.assertEqual(spline_out.shape, (8, 4, 2))

    def test_calc_spline_output_without_symmetry(self):
        """测试不使用对称的样条输出"""
        layer = DenseKAN(units=2, grid_size=4, spline_order=2)
        layer.build(input_shape=(None, 4))

        x = tf.random.normal((8, 4))
        spline_out = layer.calc_spline_output(x, use_symmetry=False)

        self.assertEqual(spline_out.shape, (8, 4, 2))


if __name__ == "__main__":
    unittest.main()
