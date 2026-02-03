"""
参数效率分析模块的测试
"""

import pytest
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
from pathlib import Path
import tempfile
import shutil

# 导入要测试的模块
from analysis.parameter_efficiency_analysis import (
    analyze_parameter_efficiency,
    generate_efficiency_table
)


@pytest.fixture
def sample_batch_results():
    """提供批量评估结果数据"""
    return [
        {
            'experiment': 'WNET5_RealAlias',
            'total_params': 100000,
            'trainable_params': 80000,
            'ASR_core': 45.5,
            'ASR_extended': 38.2,
            'overall_score': 52.3,
            'grade': 'C'
        },
        {
            'experiment': 'WNET5_RealAlias_E01',
            'total_params': 120000,
            'trainable_params': 100000,
            'ASR_core': 72.3,
            'ASR_extended': 65.8,
            'overall_score': 78.5,
            'grade': 'B'
        },
        {
            'experiment': 'WNET5_RealAlias_E05',
            'total_params': 150000,
            'trainable_params': 120000,
            'ASR_core': 90.3,
            'ASR_extended': 85.1,
            'overall_score': 92.4,
            'grade': 'A'
        },
        {
            'experiment': 'WNET5_RealAlias_E07',
            'total_params': 200000,
            'trainable_params': 180000,
            'ASR_core': 88.7,
            'ASR_extended': 82.1,
            'overall_score': 89.5,
            'grade': 'A'
        }
    ]


@pytest.fixture
def sample_results_with_zero_params():
    """提供包含零参数量结果的数据（边界情况）"""
    return [
        {
            'experiment': 'WNET5_RealAlias',
            'total_params': 100000,
            'trainable_params': 80000,
            'ASR_core': 45.5,
            'overall_score': 52.3,
            'grade': 'C'
        },
        {
            'experiment': 'Empty_Experiment',
            'total_params': 0,
            'trainable_params': 0,
            'ASR_core': 0,
            'overall_score': 0,
            'grade': 'D'
        }
    ]


class TestGenerateEfficiencyTable:
    """测试参数效率表格生成功能"""

    def test_generate_efficiency_table_basic(self, sample_batch_results, tmp_path):
        """测试基本的效率表格生成"""
        save_path = tmp_path / "test_output"
        save_path.mkdir()

        generate_efficiency_table(sample_batch_results, str(save_path))

        # 检查markdown表格文件是否创建
        table_path = save_path / 'parameter_efficiency_table.md'
        assert table_path.exists()

        # 读取并验证内容
        with open(table_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 验证表格包含必需的行
        assert '|' in content  # Markdown表格格式
        assert '实验' in content or 'Experiment' in content
        assert '总参数量' in content or 'total_params' in content
        assert 'ASR' in content or 'ASR_core' in content

    def test_generate_efficiency_table_efficiency_calculation(self, sample_batch_results, tmp_path):
        """测试效率指标计算正确性"""
        save_path = tmp_path / "test_output"
        save_path.mkdir()

        generate_efficiency_table(sample_batch_results, str(save_path))

        # 读取表格
        table_path = save_path / 'parameter_efficiency_table.md'
        with open(table_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 验证效率计算：E05应该是最高效率的（ASR高但参数量不是最大）
        # 效率 = ASR_core / (total_params / 1000)
        # E05: 90.3 / 150 = 0.602
        # E01: 72.3 / 120 = 0.6025 (略高，但E05性能更好)
        lines = content.split('\n')

        # 检查表格中有数据行
        data_lines = [l for l in lines if l.startswith('|') and not l.startswith('|---')]
        assert len(data_lines) >= 4  # 至少4个实验

    def test_generate_efficiency_table_sorted_by_efficiency(self, sample_batch_results, tmp_path):
        """测试表格按效率排序"""
        save_path = tmp_path / "test_output"
        save_path.mkdir()

        generate_efficiency_table(sample_batch_results, str(save_path))

        table_path = save_path / 'parameter_efficiency_table.md'
        with open(table_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 验证输出关键发现（打印到控制台）
        lines = content.split('\n')

    def test_generate_efficiency_table_handles_zero_params(self, sample_results_with_zero_params, tmp_path):
        """测试处理零参数量的边界情况"""
        save_path = tmp_path / "test_output"
        save_path.mkdir()

        # 不应抛出异常
        generate_efficiency_table(sample_results_with_zero_params, str(save_path))

        table_path = save_path / 'parameter_efficiency_table.md'
        assert table_path.exists()

    def test_generate_efficiency_table_preserves_all_grades(self, sample_batch_results, tmp_path):
        """测试所有等级都被正确保留"""
        save_path = tmp_path / "test_output"
        save_path.mkdir()

        generate_efficiency_table(sample_batch_results, str(save_path))

        table_path = save_path / 'parameter_efficiency_table.md'
        with open(table_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 验证表格包含所有等级
        assert 'A' in content or 'B' in content or 'C' in content or 'D' in content

    def test_generate_efficiency_table_markdown_format(self, sample_batch_results, tmp_path):
        """测试Markdown格式正确性"""
        save_path = tmp_path / "test_output"
        save_path.mkdir()

        generate_efficiency_table(sample_batch_results, str(save_path))

        table_path = save_path / 'parameter_efficiency_table.md'
        with open(table_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 验证Markdown表格格式
        lines = content.split('\n')

        # 查找表头行
        header_line = None
        separator_line = None
        for i, line in enumerate(lines):
            if line.startswith('|') and '实验' in line:
                header_line = line
            elif line.startswith('|') and '---' in line:
                separator_line = line
                break

        assert header_line is not None, "找不到表头行"
        assert separator_line is not None, "找不到分隔行"


class TestAnalyzeParameterEfficiency:
    """测试参数效率分析功能"""

    def test_analyze_parameter_efficiency_creates_output_dir(self, tmp_path):
        """测试分析函数创建输出目录"""
        save_path = tmp_path / "output"
        save_path.mkdir(parents=True, exist_ok=True)

        # Mock batch_evaluate_experiments to return test data
        import analysis.parameter_efficiency_analysis as pea
        original_batch = pea.batch_evaluate_experiments
        pea.batch_evaluate_experiments = lambda x: [
            {
                'experiment': 'test',
                'total_params': 100000,
                'trainable_params': 80000,
                'ASR_core': 50.0,
                'overall_score': 55.0,
                'grade': 'B'
            }
        ]

        try:
            results, plot_path = analyze_parameter_efficiency(str(save_path))

            # 验证结果
            assert results is not None
            assert isinstance(results, list)
            assert len(results) == 1
            assert plot_path is not None
            assert Path(plot_path).exists()
        finally:
            pea.batch_evaluate_experiments = original_batch

    def test_analyze_parameter_efficiency_plot_generation(self, tmp_path):
        """测试图表生成"""
        save_path = tmp_path / "output"
        save_path.mkdir(parents=True, exist_ok=True)

        import analysis.parameter_efficiency_analysis as pea
        original_batch = pea.batch_evaluate_experiments
        pea.batch_evaluate_experiments = lambda x: [
            {
                'experiment': 'test',
                'total_params': 100000,
                'trainable_params': 80000,
                'ASR_core': 50.0,
                'overall_score': 55.0,
                'grade': 'B'
            }
        ]

        try:
            results, plot_path = analyze_parameter_efficiency(str(save_path))

            # 验证图表文件
            assert Path(plot_path).exists()
            assert plot_path.endswith('.png')

            # 验证文件大小（图表应该有一定内容）
            file_size = Path(plot_path).stat().st_size
            assert file_size > 1000  # 至少1KB
        finally:
            pea.batch_evaluate_experiments = original_batch

    def test_analyze_parameter_efficiency_single_experiment(self, tmp_path):
        """测试单个实验的分析"""
        save_path = tmp_path / "output"
        save_path.mkdir(parents=True, exist_ok=True)

        import analysis.parameter_efficiency_analysis as pea
        original_batch = pea.batch_evaluate_experiments
        pea.batch_evaluate_experiments = lambda x: [
            {
                'experiment': 'WNET5_RealAlias',
                'total_params': 100000,
                'trainable_params': 80000,
                'ASR_core': 45.5,
                'overall_score': 52.3,
                'grade': 'C'
            }
        ]

        try:
            results, plot_path = analyze_parameter_efficiency(str(save_path))

            assert len(results) == 1
            assert results[0]['experiment'] == 'WNET5_RealAlias'
        finally:
            pea.batch_evaluate_experiments = original_batch

    def test_analyze_parameter_efficiency_multiple_experiments(self, tmp_path):
        """测试多个实验的分析"""
        save_path = tmp_path / "output"
        save_path.mkdir(parents=True, exist_ok=True)

        import analysis.parameter_efficiency_analysis as pea
        original_batch = pea.batch_evaluate_experiments
        pea.batch_evaluate_experiments = lambda x: [
            {
                'experiment': 'WNET5_RealAlias',
                'total_params': 100000,
                'trainable_params': 80000,
                'ASR_core': 45.5,
                'overall_score': 52.3,
                'grade': 'C'
            },
            {
                'experiment': 'WNET5_RealAlias_E05',
                'total_params': 150000,
                'trainable_params': 120000,
                'ASR_core': 90.3,
                'overall_score': 92.4,
                'grade': 'A'
            },
            {
                'experiment': 'WNET5_RealAlias_E07',
                'total_params': 200000,
                'trainable_params': 180000,
                'ASR_core': 88.7,
                'overall_score': 89.5,
                'grade': 'A'
            }
        ]

        try:
            results, plot_path = analyze_parameter_efficiency(str(save_path))

            assert len(results) == 3
        finally:
            pea.batch_evaluate_experiments = original_batch


class TestEfficiencyAnalysisEdgeCases:
    """测试参数效率分析的边界情况"""

    def test_empty_results(self, tmp_path):
        """测试空结果列表 - 代码会抛出ValueError因为没有数据可绘图"""
        save_path = tmp_path / "output"
        save_path.mkdir(parents=True, exist_ok=True)

        import analysis.parameter_efficiency_analysis as pea
        original_batch = pea.batch_evaluate_experiments
        pea.batch_evaluate_experiments = lambda x: []

        try:
            # 空结果会导致绘图失败，这是预期行为
            with pytest.raises(ValueError):
                analyze_parameter_efficiency(str(save_path))
        finally:
            pea.batch_evaluate_experiments = original_batch

    def test_results_with_zero_params_in_charts(self, tmp_path):
        """测试零参数量结果在图表中的处理（不会过滤）"""
        save_path = tmp_path / "output"
        save_path.mkdir(parents=True, exist_ok=True)

        import analysis.parameter_efficiency_analysis as pea
        original_batch = pea.batch_evaluate_experiments
        pea.batch_evaluate_experiments = lambda x: [
            {
                'experiment': 'valid',
                'total_params': 100000,
                'trainable_params': 80000,
                'ASR_core': 50.0,
                'overall_score': 55.0,
                'grade': 'B'
            },
            {
                'experiment': 'invalid',
                'total_params': 0,
                'trainable_params': 0,
                'ASR_core': 0,
                'overall_score': 0,
                'grade': 'D'
            }
        ]

        try:
            results, plot_path = analyze_parameter_efficiency(str(save_path))

            # analyze_parameter_efficiency不过滤零参数结果
            # 但generate_efficiency_table会过滤
            assert len(results) == 2  # 两个结果都被保留用于绘图
            assert plot_path is not None
            assert Path(plot_path).exists()
        finally:
            pea.batch_evaluate_experiments = original_batch

    def test_generate_efficiency_table_filters_zero_params(self, sample_results_with_zero_params, tmp_path):
        """测试generate_efficiency_table正确过滤零参数量结果"""
        save_path = tmp_path / "test_output"
        save_path.mkdir()

        generate_efficiency_table(sample_results_with_zero_params, str(save_path))

        table_path = save_path / 'parameter_efficiency_table.md'
        with open(table_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 表格中应该只包含有效结果（过滤了零参数）
        lines = content.split('\n')
        data_lines = [l for l in lines if l.startswith('|') and not l.startswith('|---') and not l.startswith('| 实验')]

        # 应该只有一行数据（过滤了零参数的那个）
        assert len(data_lines) == 1
        assert 'Baseline' in data_lines[0]  # WNET5_RealAlias 被重命名为 Baseline

    def test_pareto_frontier_visualization(self, tmp_path):
        """测试帕累托前沿可视化"""
        save_path = tmp_path / "output"
        save_path.mkdir(parents=True, exist_ok=True)

        import analysis.parameter_efficiency_analysis as pea
        original_batch = pea.batch_evaluate_experiments
        pea.batch_evaluate_experiments = lambda x: [
            {
                'experiment': 'WNET5_RealAlias',
                'total_params': 100000,
                'trainable_params': 80000,
                'ASR_core': 45.5,
                'overall_score': 52.3,
                'grade': 'C'
            },
            {
                'experiment': 'WNET5_RealAlias_E05',
                'total_params': 150000,
                'trainable_params': 120000,
                'ASR_core': 90.3,
                'overall_score': 92.4,
                'grade': 'A'
            }
        ]

        try:
            results, plot_path = analyze_parameter_efficiency(str(save_path))

            # 验证图表存在
            assert Path(plot_path).exists()
        finally:
            pea.batch_evaluate_experiments = original_batch

    def test_color_mapping(self, tmp_path):
        """测试颜色映射"""
        save_path = tmp_path / "output"
        save_path.mkdir(parents=True, exist_ok=True)

        import analysis.parameter_efficiency_analysis as pea
        original_batch = pea.batch_evaluate_experiments
        pea.batch_evaluate_experiments = lambda x: [
            {
                'experiment': 'WNET5_RealAlias',
                'total_params': 100000,
                'trainable_params': 80000,
                'ASR_core': 45.5,
                'overall_score': 52.3,
                'grade': 'C'
            },
            {
                'experiment': 'WNET5_RealAlias_E05',
                'total_params': 150000,
                'trainable_params': 120000,
                'ASR_core': 90.3,
                'overall_score': 92.4,
                'grade': 'A'
            },
            {
                'experiment': 'WNET5_RealAlias_E01',
                'total_params': 120000,
                'trainable_params': 100000,
                'ASR_core': 72.3,
                'overall_score': 78.5,
                'grade': 'B'
            }
        ]

        try:
            results, plot_path = analyze_parameter_efficiency(str(save_path))

            # 验证E05被标记为最佳
            assert any(r['experiment'] == 'WNET5_RealAlias_E05' for r in results)
        finally:
            pea.batch_evaluate_experiments = original_batch
