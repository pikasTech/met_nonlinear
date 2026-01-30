"""
grid_log模块的单元测试

测试对数/线性混合点生成功能
"""

import pytest
import numpy as np
from utils.grid_log import generate_mixed_log_linear_points


class TestGenerateMixedLogLinearPoints:
    """Test cases for generate_mixed_log_linear_points function."""

    def test_basic_generation(self):
        """测试基本点生成。"""
        start = 0.001
        end = 1.0
        points = 10
        result = generate_mixed_log_linear_points(start, end, points)
        assert len(result) == points

    def test_first_point_equals_start(self):
        """测试首点等于start值。"""
        start = 0.001
        end = 1.0
        points = 10
        result = generate_mixed_log_linear_points(start, end, points)
        assert result[0] == start

    def test_last_point_equals_end(self):
        """测试末点等于end值。"""
        start = 0.001
        end = 1.0
        points = 10
        result = generate_mixed_log_linear_points(start, end, points)
        np.testing.assert_almost_equal(result[-1], end)

    def test_points_sorted(self):
        """测试生成的点按升序排列。"""
        start = 0.001
        end = 1.0
        points = 20
        result = generate_mixed_log_linear_points(start, end, points)
        assert np.all(np.diff(result) >= 0)

    def test_start_must_be_positive(self):
        """测试start必须为正数。"""
        with pytest.raises(ValueError, match="必须为正数"):
            generate_mixed_log_linear_points(0, 1.0, 10)

    def test_end_must_be_positive(self):
        """测试end必须为正数。"""
        with pytest.raises(ValueError, match="必须为正数"):
            generate_mixed_log_linear_points(0.001, 0, 10)

    def test_end_must_be_greater_than_start(self):
        """测试end必须大于start。"""
        with pytest.raises(ValueError, match="end 必须大于 start"):
            generate_mixed_log_linear_points(1.0, 0.001, 10)

    def test_start_equals_end_raises_error(self):
        """测试start等于end时抛出错误。"""
        with pytest.raises(ValueError):
            generate_mixed_log_linear_points(0.5, 0.5, 10)

    def test_ratio_log_must_be_in_range(self):
        """测试ratio_log必须在[0, 1]范围内。"""
        with pytest.raises(ValueError, match="ratio_log 必须在 \[0, 1\] 范围内"):
            generate_mixed_log_linear_points(0.001, 1.0, 10, ratio_log=-0.1)

        with pytest.raises(ValueError, match="ratio_log 必须在 \[0, 1\] 范围内"):
            generate_mixed_log_linear_points(0.001, 1.0, 10, ratio_log=1.1)

    def test_ratio_log_points_must_be_in_range(self):
        """测试ratio_log_points必须在[0, 1]范围内。"""
        with pytest.raises(ValueError, match="ratio_log_points 必须在 \[0, 1\] 范围内"):
            generate_mixed_log_linear_points(0.001, 1.0, 10, ratio_log_points=-0.1)

        with pytest.raises(ValueError, match="ratio_log_points 必须在 \[0, 1\] 范围内"):
            generate_mixed_log_linear_points(0.001, 1.0, 10, ratio_log_points=1.1)

    def test_ratio_log_zero(self):
        """测试ratio_log为0时全部为线性点。"""
        start = 0.001
        end = 1.0
        points = 10
        result = generate_mixed_log_linear_points(start, end, points, ratio_log=0)
        # 当ratio_log=0时，log_range_end = start
        # 所有点都在线性区间
        assert len(result) == points
        assert result[0] == start
        np.testing.assert_almost_equal(result[-1], end)

    def test_ratio_log_one(self):
        """测试ratio_log为1时全部为对数点。"""
        start = 0.001
        end = 1.0
        points = 10
        result = generate_mixed_log_linear_points(start, end, points, ratio_log=1)
        # 当ratio_log=1时，linear_range_start = end
        # 所有点都在对数区间
        assert len(result) == points
        assert result[0] == start
        np.testing.assert_almost_equal(result[-1], end)

    def test_ratio_log_points_zero(self):
        """测试ratio_log_points为0时全部为线性点。"""
        start = 0.001
        end = 1.0
        points = 10
        result = generate_mixed_log_linear_points(start, end, points, ratio_log_points=0)
        # 线性点数 = points
        assert len(result) == points

    def test_ratio_log_points_one(self):
        """测试ratio_log_points为1时全部为对数点。"""
        start = 0.001
        end = 1.0
        points = 10
        result = generate_mixed_log_linear_points(start, end, points, ratio_log_points=1)
        # 对数点数 = points
        assert len(result) == points

    def test_small_point_count(self):
        """测试最小点数（2点）。"""
        start = 0.001
        end = 1.0
        points = 2
        result = generate_mixed_log_linear_points(start, end, points)
        assert len(result) == points
        # 首点应该是start
        # 由于ratio_log_points=0.3，log_points_count = int(2 * 0.3) = 0
        # 此时log_points为空，linear_points_count = 2 - 0 = 2
        # 线性区间从start到end
        # 注意：函数实现中，当log_points_count为0时，logspace会返回空数组
        # 当linear_points_count >= 1时，linspace会生成points个点

    def test_large_point_count(self):
        """测试大点数。"""
        start = 0.001
        end = 1000.0
        points = 1000
        result = generate_mixed_log_linear_points(start, end, points)
        assert len(result) == points
        assert result[0] == start
        np.testing.assert_almost_equal(result[-1], end)

    def test_wide_range(self):
        """测试宽范围（多个数量级）。"""
        start = 1e-6
        end = 1e6
        points = 100
        result = generate_mixed_log_linear_points(start, end, points)
        assert len(result) == points
        assert result[0] == start
        np.testing.assert_almost_equal(result[-1], end)

    def test_narrow_range(self):
        """测试窄范围。"""
        start = 0.9
        end = 1.1
        points = 20
        result = generate_mixed_log_linear_points(start, end, points)
        assert len(result) == points
        assert result[0] == start
        np.testing.assert_almost_equal(result[-1], end)

    def test_return_type_is_numpy_array(self):
        """测试返回类型为numpy数组。"""
        result = generate_mixed_log_linear_points(0.001, 1.0, 10)
        assert isinstance(result, np.ndarray)

    def test_all_points_positive(self):
        """测试所有生成点均为正数。"""
        start = 0.001
        end = 1.0
        points = 50
        result = generate_mixed_log_linear_points(start, end, points)
        assert np.all(result > 0)

    def test_no_duplicate_points(self):
        """测试没有重复点。"""
        start = 0.001
        end = 1.0
        points = 100
        result = generate_mixed_log_linear_points(start, end, points)
        # 检查是否有相邻的重复点
        assert np.all(result[:-1] < result[1:])

    def test_custom_ratio_log(self):
        """测试自定义ratio_log值。"""
        start = 0.001
        end = 1.0
        points = 100
        for ratio in [0.25, 0.5, 0.75]:
            result = generate_mixed_log_linear_points(start, end, points, ratio_log=ratio)
            assert len(result) == points
            assert result[0] == start
            np.testing.assert_almost_equal(result[-1], end)

    def test_custom_ratio_log_points(self):
        """测试自定义ratio_log_points值。"""
        start = 0.001
        end = 1.0
        points = 100
        for ratio in [0.25, 0.5, 0.75]:
            result = generate_mixed_log_linear_points(start, end, points, ratio_log_points=ratio)
            assert len(result) == points


class TestGenerateMixedLogLinearPointsEdgeCases:
    """Edge case tests for generate_mixed_log_linear_points function."""

    def test_very_small_start(self):
        """测试非常小的start值。"""
        start = 1e-12
        end = 1.0
        points = 50
        result = generate_mixed_log_linear_points(start, end, points)
        assert len(result) == points
        assert result[0] == start

    def test_large_end(self):
        """测试非常大的end值。"""
        start = 0.001
        end = 1e12
        points = 50
        result = generate_mixed_log_linear_points(start, end, points)
        assert len(result) == points
        np.testing.assert_almost_equal(result[-1], end)

    def test_equal_to_one_point(self):
        """测试点数为1时的边界情况。"""
        start = 0.001
        end = 1.0
        points = 1
        result = generate_mixed_log_linear_points(start, end, points)
        assert len(result) == 1
        # 当ratio_log_points < 1时，线性点数可能为0
        # 当log_points_count = int(points * ratio_log_points) = 0
        # 需要处理这种情况
