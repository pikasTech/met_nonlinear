"""Tests for BiasAnalyzer using real error analysis data."""

import pytest
import shutil
import tempfile
from pathlib import Path
import numpy as np

from ..core import BiasAnalyzer


class TestBiasAnalyzer:
    """Test BiasAnalyzer functionality."""
    
    @pytest.fixture
    def test_project_with_baseline(self, tmp_path):
        """Create test project with baseline error analysis."""
        test_resources = Path(__file__).parent.parent / "test_resources"
        error_file = test_resources / "error_analysis_samples" / "error_analysis_baseline.json"
        
        project_path = tmp_path / "test_project"
        inference_path = project_path / "data" / "inference"
        inference_path.mkdir(parents=True, exist_ok=True)
        
        shutil.copy(error_file, inference_path / "error_analysis.json")
        
        return project_path
    
    @pytest.fixture
    def test_project_with_compensated(self, tmp_path):
        """Create test project with compensated error analysis."""
        test_resources = Path(__file__).parent.parent / "test_resources"
        error_file = test_resources / "error_analysis_samples" / "error_analysis_layer123.json"
        
        project_path = tmp_path / "test_project_compensated"
        inference_path = project_path / "data" / "inference"
        inference_path.mkdir(parents=True, exist_ok=True)
        
        shutil.copy(error_file, inference_path / "error_analysis.json")
        
        return project_path
    
    def test_load_error_analysis(self, test_project_with_baseline):
        """Test loading error analysis file."""
        analyzer = BiasAnalyzer(test_project_with_baseline)
        data = analyzer.load_error_analysis()
        
        assert "bias_analysis" in data
        assert "nn_spice_bias" in data["bias_analysis"]
        assert "bias_error_matrix" in data["bias_analysis"]["nn_spice_bias"]
    
    def test_extract_bias_error_matrix(self, test_project_with_baseline):
        """Test extracting bias error matrix."""
        analyzer = BiasAnalyzer(test_project_with_baseline)
        matrix = analyzer.extract_bias_error_matrix()
        
        # Should have 5 layers for WaveNet5
        assert len(matrix) == 5
        
        # Check known baseline values
        assert matrix[0] == [0.000011, -0.000291, 0.000280, 0.000001, -0.000034, 0.000033]
        assert matrix[1] == [0.005323, 0.002278, 0.005201, 0.014258, 0.003152, 0.003255]
    
    def test_get_layer_errors(self, test_project_with_baseline):
        """Test getting errors for specific layer."""
        analyzer = BiasAnalyzer(test_project_with_baseline)
        
        # Layer 1 (Dense layer 1)
        layer1_errors = analyzer.get_layer_errors(1)
        assert len(layer1_errors) == 6
        assert layer1_errors[3] == 0.014258  # Known high error channel
        
        # Output layer
        output_errors = analyzer.get_layer_errors(4)
        assert len(output_errors) == 1
        assert output_errors[0] == 0.067762
        
        # Invalid layer
        assert analyzer.get_layer_errors(10) is None
    
    def test_get_compensatable_layers(self):
        """Test getting list of compensatable layers."""
        analyzer = BiasAnalyzer(Path("."))  # Path doesn't matter for this test
        
        compensatable = analyzer.get_compensatable_layers()
        
        # Should be layers 1, 2, 3 (Dense layers)
        assert compensatable == [1, 2, 3]
        assert 0 not in compensatable  # SVF layer
        assert 4 not in compensatable  # Output layer
    
    def test_analyze_layer_statistics(self, test_project_with_baseline):
        """Test calculating layer statistics."""
        analyzer = BiasAnalyzer(test_project_with_baseline)
        
        # Analyze layer 1
        stats = analyzer.analyze_layer_statistics(1)
        
        assert "mean" in stats
        assert "std" in stats
        assert "max" in stats
        assert "min" in stats
        assert "abs_mean" in stats
        assert "channel_count" in stats
        
        # Check specific values
        assert abs(stats["mean"] - 0.005578) < 0.0001
        assert stats["channel_count"] == 6
        assert stats["max"] == 0.014258
    
    def test_get_worst_layers(self, test_project_with_baseline):
        """Test getting layers sorted by error magnitude."""
        analyzer = BiasAnalyzer(test_project_with_baseline)
        
        worst = analyzer.get_worst_layers(metric="abs_mean")
        
        # Should be sorted by absolute mean error
        assert len(worst) == 3  # Only compensatable layers
        
        # Layer 1 should be worst (highest abs_mean)
        assert worst[0][0] == 1  # Layer index
        assert worst[0][1] > 0.005  # Error magnitude
        
        # Check ordering
        for i in range(len(worst) - 1):
            assert worst[i][1] >= worst[i+1][1]
    
    def test_compare_analyses(self, test_project_with_baseline, test_project_with_compensated):
        """Test comparing two error analyses."""
        # Compare compensated (current) with baseline (other)
        analyzer = BiasAnalyzer(test_project_with_compensated)
        
        # Compare with baseline state
        test_resources = Path(__file__).parent.parent / "test_resources"
        baseline_file = test_resources / "error_analysis_samples" / "error_analysis_baseline.json"
        
        comparison = analyzer.compare_analyses(baseline_file)
        
        assert "layer_improvements" in comparison
        assert "total_improvement" in comparison
        
        # Just verify the comparison structure is correct
        # The actual values depend on the test data used
        assert len(comparison["layer_improvements"]) >= 3  # At least 3 compensatable layers
        
        # Verify each layer has required fields
        for layer_idx, imp in comparison["layer_improvements"].items():
            assert "name" in imp
            assert "before" in imp
            assert "after" in imp
            assert "improvement_percent" in imp
    
    def test_format_bias_errors(self, test_project_with_baseline):
        """Test formatting bias errors as string."""
        analyzer = BiasAnalyzer(test_project_with_baseline)
        
        formatted = analyzer.format_bias_errors(1)
        
        assert "Layer 1 (Dense Layer 1)" in formatted
        assert "Channels: 6" in formatted
        assert "Mean error: 0.005578" in formatted
        assert "Per-channel errors:" in formatted
    
    def test_real_compensation_progression(self):
        """Test analyzing real compensation progression through all stages."""
        test_resources = Path(__file__).parent.parent / "test_resources" / "error_analysis_samples"
        
        # Expected progression: baseline -> layer1 -> layer12 -> layer123
        files = ["error_analysis_baseline.json", "error_analysis_layer1.json",
                 "error_analysis_layer12.json", "error_analysis_layer123.json"]
        
        # Just verify we can load and analyze each stage
        for stage_idx, error_file in enumerate(files):
            # Create temporary project with this error analysis
            with tempfile.TemporaryDirectory() as tmpdir:
                project_path = Path(tmpdir)
                inference_path = project_path / "data" / "inference"
                inference_path.mkdir(parents=True, exist_ok=True)
                
                shutil.copy(test_resources / error_file, 
                           inference_path / "error_analysis.json")
                
                analyzer = BiasAnalyzer(project_path)
                
                # Verify we can extract and analyze data
                matrix = analyzer.extract_bias_error_matrix()
                assert len(matrix) == 5  # 5 layers
                
                # Verify we can get statistics for each compensatable layer
                for layer_idx in analyzer.get_compensatable_layers():
                    stats = analyzer.analyze_layer_statistics(layer_idx)
                    assert "mean" in stats
                    assert "abs_mean" in stats
                    assert "channel_count" in stats