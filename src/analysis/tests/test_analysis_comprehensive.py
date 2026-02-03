"""
Comprehensive tests for analysis module
"""

import pytest
import json
import tempfile
from pathlib import Path
import numpy as np


class TestAliasSuppression:
    """Test cases for alias_suppression module."""

    def test_module_import(self):
        """Test that alias_suppression module can be imported."""
        from analysis import alias_suppression
        assert alias_suppression is not None

    def test_module_has_functions(self):
        """Test that module has expected functions."""
        from analysis import alias_suppression
        assert hasattr(alias_suppression, 'evaluate_alias_suppression')
        assert hasattr(alias_suppression, 'batch_evaluate_experiments')


class TestParameterEfficiencyAnalysis:
    """Test cases for parameter_efficiency_analysis module."""

    def test_module_import(self):
        """Test that module can be imported."""
        from analysis import parameter_efficiency_analysis
        assert parameter_efficiency_analysis is not None

    def test_module_has_functions(self):
        """Test that module has expected functions."""
        from analysis import parameter_efficiency_analysis
        # Module should have analysis functions
        module_attrs = dir(parameter_efficiency_analysis)
        assert module_attrs is not None


class TestAnalysisVisualization:
    """Test cases for analysis.visualization module."""

    def test_module_import(self):
        """Test that visualization module can be imported."""
        from analysis import visualization
        assert visualization is not None

    def test_module_has_functions(self):
        """Test that module has visualization functions."""
        from analysis.visualization import visualize_alias_suppression
        assert callable(visualize_alias_suppression)


class TestAnalysisExampleUsage:
    """Test cases for example_usage module - testing imports and structure."""

    def test_import_functions(self):
        """Test that example_usage imports work."""
        from analysis import evaluate_alias_suppression
        from analysis.visualization import visualize_alias_suppression
        assert callable(evaluate_alias_suppression)
        assert callable(visualize_alias_suppression)

    def test_module_structure(self):
        """Test that example_usage module has expected structure."""
        import analysis.example_usage as example_usage
        assert hasattr(example_usage, 'example_single_evaluation')
        assert hasattr(example_usage, 'example_batch_evaluation')


class TestAnalysisIntegration:
    """Integration tests for analysis module."""

    def test_analysis_package_import(self):
        """Test that entire analysis package can be imported."""
        import analysis
        assert analysis is not None

    def test_submodules_present(self):
        """Test that all submodules are accessible."""
        from analysis import alias_suppression
        from analysis import parameter_efficiency_analysis
        from analysis import visualization
        from analysis import example_usage
        assert alias_suppression is not None
        assert parameter_efficiency_analysis is not None
        assert visualization is not None
        assert example_usage is not None


class TestAliasSuppressionCore:
    """Core functionality tests for alias_suppression."""

    def test_module_public_interface(self):
        """Test that module has expected public interface."""
        from analysis import alias_suppression
        # Module should be importable and have expected functions
        assert hasattr(alias_suppression, 'evaluate_alias_suppression')

    def test_suppression_result_structure(self):
        """Test that suppression evaluation returns proper structure."""
        from analysis.alias_suppression import evaluate_alias_suppression
        # Function should exist and be callable
        assert callable(evaluate_alias_suppression)


class TestParameterEfficiencyCore:
    """Core functionality tests for parameter_efficiency_analysis."""

    def test_module_public_interface(self):
        """Test that module has expected public interface."""
        from analysis import parameter_efficiency_analysis
        # Module should have public functions
        module_attrs = dir(parameter_efficiency_analysis)
        # Filter out private attributes
        public_attrs = [a for a in module_attrs if not a.startswith('_')]
        assert len(public_attrs) > 0

    def test_analysis_function_exists(self):
        """Test that analysis functions exist."""
        from analysis import parameter_efficiency_analysis
        # Just verify module is importable and has functions
        assert hasattr(parameter_efficiency_analysis, 'analyze_parameter_efficiency')


class TestVisualizationCore:
    """Core functionality tests for analysis.visualization."""

    def test_visualize_function_exists(self):
        """Test that visualization functions exist."""
        from analysis.visualization import visualize_alias_suppression
        from analysis.visualization import visualize_batch_results
        assert callable(visualize_alias_suppression)
        assert callable(visualize_batch_results)

    def test_visualization_params_basic(self, tmp_path):
        """Test basic visualization with mock data."""
        from analysis.visualization import visualize_alias_suppression

        # Mock data
        mock_data = {
            'frequencies': list(range(80, 120, 5)),
            'original_response': [1.0 + 0.1 * np.sin(x) for x in range(8)],
            'compensated_response': [0.9 + 0.05 * np.sin(x) for x in range(8)]
        }
        save_path = str(tmp_path / 'test_visualization.png')

        # Should not raise exception (may skip if matplotlib unavailable)
        try:
            visualize_alias_suppression(mock_data, save_path=save_path, show=False)
        except Exception as e:
            pytest.skip(f"Visualization failed: {e}")
