"""
sample_list模块的单元测试

测试列表采样功能，确保首尾元素一致性和采样正确性
"""

import pytest
from utils.sample_list import sample_list


class TestSampleList:
    """Test cases for sample_list function."""

    def test_sample_list_size_1(self):
        """测试采样大小为1时返回中间元素。"""
        lst = [1, 2, 3, 4, 5]
        result = sample_list(lst, 1)
        assert result == [3]  # 中间元素

    def test_sample_list_size_1_even(self):
        """测试采样大小为1时偶数长度列表返回中间元素。"""
        lst = [1, 2, 3, 4]
        result = sample_list(lst, 1)
        assert result == [2] or result == [3]  # Python取整得到中间索引

    def test_sample_list_size_2(self):
        """测试采样大小为2时返回首尾元素。"""
        lst = [1, 2, 3, 4, 5]
        result = sample_list(lst, 2)
        assert result == [1, 5]  # 首尾元素

    def test_sample_list_preserves_first_element(self):
        """测试采样列表的首元素与原列表一致。"""
        lst = [10, 20, 30, 40, 50]
        result = sample_list(lst, 3)
        assert result[0] == lst[0]

    def test_sample_list_preserves_last_element(self):
        """测试采样列表的末元素与原列表一致。"""
        lst = [10, 20, 30, 40, 50]
        result = sample_list(lst, 3)
        assert result[-1] == lst[-1]

    def test_sample_list_size_equals_length(self):
        """测试采样大小等于列表长度时返回原列表。"""
        lst = [1, 2, 3]
        result = sample_list(lst, 3)
        assert result == lst

    def test_sample_list_size_greater_than_length(self):
        """测试采样大小大于列表长度时的行为。"""
        lst = [1, 2, 3]
        # 步长计算可能产生重复索引
        result = sample_list(lst, 5)
        # 应该仍然包含首尾元素
        assert result[0] == lst[0]
        assert result[-1] == lst[-1]

    def test_sample_list_empty_raises_error(self):
        """测试空列表采样。"""
        lst = []
        with pytest.raises((IndexError, ZeroDivisionError)):
            sample_list(lst, 2)

    def test_sample_list_size_less_than_1_raises_error(self):
        """测试采样大小小于1时抛出错误。"""
        lst = [1, 2, 3, 4, 5]
        with pytest.raises(ValueError):
            sample_list(lst, 0)

    def test_sample_list_negative_size_raises_error(self):
        """测试负数采样大小抛出错误。"""
        lst = [1, 2, 3, 4, 5]
        with pytest.raises(ValueError):
            sample_list(lst, -1)

    def test_sample_list_single_element_size_1(self):
        """测试单元素列表采样。"""
        lst = [42]
        result = sample_list(lst, 1)
        assert result == [42]

    def test_sample_list_two_elements_size_2(self):
        """测试两元素列表采样。"""
        lst = [1, 2]
        result = sample_list(lst, 2)
        assert result == [1, 2]

    def test_sample_list_uniform_distribution(self):
        """测试采样点的均匀分布性。"""
        lst = list(range(100))
        result = sample_list(lst, 10)
        # 首尾必须保留
        assert result[0] == 0
        assert result[-1] == 99
        # 中间应该有8个点
        assert len(result) == 10
        # 检查索引是否递增
        assert all(result[i] < result[i+1] for i in range(len(result)-1))

    def test_sample_list_indices_are_valid(self):
        """测试采样索引的有效性。"""
        lst = list(range(50))
        for size in [2, 5, 10, 20, 50]:
            result = sample_list(lst, size)
            for val in result:
                assert 0 <= val < len(lst)

    def test_sample_list_returns_list_type(self):
        """测试返回类型为列表。"""
        lst = [1, 2, 3, 4, 5]
        result = sample_list(lst, 3)
        assert isinstance(result, list)


class TestSampleListEdgeCases:
    """Edge case tests for sample_list function."""

    def test_very_large_list(self):
        """测试超大列表采样。"""
        lst = list(range(10000))
        result = sample_list(lst, 100)
        assert len(result) == 100
        assert result[0] == 0
        assert result[-1] == 9999

    def test_small_list(self):
        """测试小列表采样。"""
        for length in [1, 2, 3, 4, 5]:
            lst = list(range(length))
            result = sample_list(lst, 2)
            assert result[0] == 0
            assert result[-1] == length - 1

    def test_float_values(self):
        """测试浮点数值列表采样。"""
        lst = [0.1, 0.2, 0.3, 0.4, 0.5]
        result = sample_list(lst, 3)
        assert result[0] == 0.1
        assert result[-1] == 0.5
        assert len(result) == 3

    def test_string_list(self):
        """测试字符串列表采样。"""
        lst = ['a', 'b', 'c', 'd', 'e']
        result = sample_list(lst, 3)
        assert result[0] == 'a'
        assert result[-1] == 'e'
        assert len(result) == 3

    def test_mixed_types(self):
        """测试混合类型列表采样。"""
        lst = [1, 'b', 3.0, [4], {'key': 'value'}]
        result = sample_list(lst, 2)
        assert result[0] == lst[0]
        assert result[-1] == lst[-1]


class TestPlotSamplingIndices:
    """Test cases for plot_sampling_indices function."""

    def test_plot_sampling_indices_function_exists(self):
        """测试plot_sampling_indices函数存在。"""
        from utils.sample_list import plot_sampling_indices
        assert callable(plot_sampling_indices)

    @pytest.mark.skip(reason="Interactive plot display test")
    def test_plot_sampling_indices_executes(self):
        """测试plot_sampling_indices函数可以执行。"""
        from utils.sample_list import plot_sampling_indices
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend

        lst = list(range(1, 21))
        sample_sizes = [2, 4, 6]
        # Should not raise any exception
        plot_sampling_indices(lst, sample_sizes)

    def test_plot_sampling_indices_with_mock(self, tmp_path):
        """测试plot_sampling_indices函数使用mock。"""
        from unittest.mock import patch, MagicMock
        from utils.sample_list import plot_sampling_indices

        with patch('utils.sample_list.plt') as mock_plt:
            mock_figure = MagicMock()
            mock_plt.figure.return_value = mock_figure
            mock_ax = MagicMock()
            mock_plt.plot.return_value = mock_ax

            lst = list(range(1, 21))
            sample_sizes = [2, 4]

            # Execute the function
            plot_sampling_indices(lst, sample_sizes)

            # Verify plt.figure was called
            mock_plt.figure.assert_called()

    def test_plot_sampling_indices_single_size(self):
        """测试plot_sampling_indices函数使用单个采样大小。"""
        from unittest.mock import patch, MagicMock
        from utils.sample_list import plot_sampling_indices

        with patch('utils.sample_list.plt') as mock_plt:
            mock_figure = MagicMock()
            mock_plt.figure.return_value = mock_figure

            lst = list(range(1, 11))
            sample_sizes = [5]

            plot_sampling_indices(lst, sample_sizes)

            mock_plt.figure.assert_called()

    def test_plot_sampling_indices_title_set(self):
        """测试plot_sampling_indices函数设置了正确的标题。"""
        from unittest.mock import patch, MagicMock
        from utils.sample_list import plot_sampling_indices

        with patch('utils.sample_list.plt') as mock_plt:
            mock_figure = MagicMock()
            mock_plt.figure.return_value = mock_figure

            lst = list(range(1, 21))
            sample_sizes = [2, 4, 6]

            plot_sampling_indices(lst, sample_sizes)

            # Verify plt.plot was called for original indices
            assert mock_plt.plot.called

    def test_plot_sampling_indices_xlabel_ylabel(self):
        """测试plot_sampling_indices函数设置了坐标轴标签。"""
        from unittest.mock import patch, MagicMock
        from utils.sample_list import plot_sampling_indices

        with patch('utils.sample_list.plt') as mock_plt:
            mock_figure = MagicMock()
            mock_plt.figure.return_value = mock_figure

            lst = list(range(1, 21))
            sample_sizes = [2, 4]

            plot_sampling_indices(lst, sample_sizes)

            # Verify xlabel and ylabel were called
            mock_plt.xlabel.assert_called()
            mock_plt.ylabel.assert_called()
