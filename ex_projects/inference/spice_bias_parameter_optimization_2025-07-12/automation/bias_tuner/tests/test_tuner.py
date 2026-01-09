"""Integration tests for BiasTuner using mock mode."""

import pytest
import shutil
from pathlib import Path
import json

from ..tuner import BiasTuner
from ..core import CompensationStrategy, set_mock_mode


class TestBiasTuner:
    """Test the main BiasTuner functionality."""
    
    @pytest.fixture
    def mock_project(self, tmp_path):
        """Create a mock project with test resources."""
        # Get test resources
        test_resources = Path(__file__).parent.parent / "test_resources"
        
        # Create project directory
        project_path = tmp_path / "test_project"
        project_path.mkdir()
        
        # Copy baseline config
        shutil.copy(
            test_resources / "config_samples" / "config_baseline.json",
            project_path / "config.json"
        )
        
        return project_path
    
    @pytest.fixture
    def mock_tuner(self, mock_project):
        """Create a BiasTuner in mock mode."""
        # Enable mock mode
        test_resources = Path(__file__).parent.parent / "test_resources"
        set_mock_mode(True, test_resources)
        
        # Change to project directory for mock executor to work properly
        import os
        original_cwd = os.getcwd()
        os.chdir(mock_project.parent)
        
        # Create tuner
        tuner = BiasTuner(
            mock_project,
            strategy=CompensationStrategy.SAME_PHASE,
            dry_run=False  # We want to test the mock execution
        )
        
        yield tuner
        
        # Cleanup
        os.chdir(original_cwd)
        set_mock_mode(False)
    
    def test_tuner_initialization(self, mock_tuner):
        """Test BiasTuner initialization."""
        assert mock_tuner.project_name == "test_project"
        assert mock_tuner.compensator.strategy == CompensationStrategy.SAME_PHASE
        assert not mock_tuner.dry_run
        assert len(mock_tuner.tuning_history) == 0
        assert len(mock_tuner.current_compensation) == 0
    
    def test_run_baseline_measurement(self, mock_tuner):
        """Test baseline measurement."""
        result = mock_tuner.run_baseline_measurement()
        
        assert result["type"] == "baseline"
        assert "bias_errors" in result
        assert "statistics" in result
        
        # Check bias errors match expected baseline
        bias_errors = result["bias_errors"]
        assert len(bias_errors) == 5  # 5 layers
        assert bias_errors[1] == [0.005323, 0.002278, 0.005201, 0.014258, 0.003152, 0.003255]
        
        # Check statistics
        assert 1 in result["statistics"]  # Layer 1
        assert result["statistics"][1]["mean"] == pytest.approx(0.005578, abs=0.0001)
        
        # Check config was updated
        config = mock_tuner.config_manager.get_bias_compensation_config()
        assert config["enabled"] is False
    
    def test_tune_single_layer(self, mock_tuner):
        """Test tuning a single layer."""
        # Run baseline first
        mock_tuner.run_baseline_measurement()
        
        # Set mock state to simulate layer 1 compensation
        mock_tuner.executor.set_mock_state("layer1")
        
        # Tune layer 1
        result = mock_tuner.tune_single_layer(1, scale_factor=1.0)
        
        assert result["type"] == "layer_compensation"
        assert result["layer_idx"] == 1
        assert result["scale_factor"] == 1.0
        
        # Check compensation was applied
        assert 1 in mock_tuner.current_compensation
        expected_comp = [0.005323, 0.002278, 0.005201, 0.014258, 0.003152, 0.003255]
        assert mock_tuner.current_compensation[1] == expected_comp
        
        # Check new errors show improvement
        new_errors = result["bias_errors_after"][1]
        assert new_errors == [0.000011, -0.000291, 0.000280, 0.000001, -0.000034, 0.000033]
        
        # Check config was updated
        config = mock_tuner.config_manager.get_bias_compensation_config()
        assert config["enabled"] is True
        assert "1" in config["layer_bias_adjustments"]
    
    def test_tune_sequential(self, mock_tuner):
        """Test sequential tuning of multiple layers."""
        # Run baseline
        mock_tuner.run_baseline_measurement()
        
        # Define test sequence
        layer_order = [1, 2, 3]
        mock_states = ["layer1", "layer12", "layer123"]
        
        # Mock the progression by updating state before each layer
        original_tune = mock_tuner.tune_single_layer
        call_count = 0
        
        def mock_tune_with_state(*args, **kwargs):
            nonlocal call_count
            if call_count < len(mock_states):
                mock_tuner.executor.set_mock_state(mock_states[call_count])
            call_count += 1
            return original_tune(*args, **kwargs)
        
        mock_tuner.tune_single_layer = mock_tune_with_state
        
        # Run sequential tuning
        results = mock_tuner.tune_sequential(layer_order=layer_order)
        
        assert len(results) == 3
        
        # Check each result
        for i, result in enumerate(results):
            assert result["layer_idx"] == layer_order[i]
            assert result["type"] == "layer_compensation"
        
        # Check final compensation state
        assert len(mock_tuner.current_compensation) == 3
        assert 1 in mock_tuner.current_compensation
        assert 2 in mock_tuner.current_compensation
        assert 3 in mock_tuner.current_compensation
    
    def test_optimize_layer(self, mock_tuner):
        """Test layer optimization."""
        # Run baseline
        mock_tuner.run_baseline_measurement()
        
        # Mock perfect compensation after first iteration
        mock_tuner.executor.set_mock_state("layer1")
        
        # Optimize layer 1
        result = mock_tuner.optimize_layer(
            layer_idx=1,
            target_error=0.001,
            max_iterations=3
        )
        
        assert result["layer_idx"] == 1
        assert result["target_error"] == 0.001
        assert result["success"] is True
        assert result["final_error"] < 0.001
        assert len(result["iterations"]) >= 1
    
    def test_generate_report(self, mock_tuner, tmp_path):
        """Test report generation."""
        # Run some tuning
        mock_tuner.run_baseline_measurement()
        mock_tuner.executor.set_mock_state("layer1")
        mock_tuner.tune_single_layer(1)
        
        # Generate report
        report_path = mock_tuner.generate_report()
        
        assert report_path.exists()
        
        # Load and verify report
        with open(report_path) as f:
            report = json.load(f)
        
        assert report["project"] == "test_project"
        assert "tuning_history" in report
        assert "final_compensation" in report
        assert "summary" in report
        
        # Check summary
        summary = report["summary"]
        assert "total_iterations" in summary
        assert summary["total_iterations"] == 2  # baseline + layer1
        assert "layer_improvements" in summary
    
    def test_reset(self, mock_tuner):
        """Test tuner reset."""
        # Run some tuning
        mock_tuner.run_baseline_measurement()
        mock_tuner.executor.set_mock_state("layer1")
        mock_tuner.tune_single_layer(1)
        
        # Verify state is populated
        assert len(mock_tuner.tuning_history) > 0
        assert len(mock_tuner.current_compensation) > 0
        
        # Reset
        mock_tuner.reset()
        
        # Verify state is cleared
        assert len(mock_tuner.tuning_history) == 0
        assert len(mock_tuner.current_compensation) == 0
        
        # Verify config is restored
        config = mock_tuner.config_manager.get_bias_compensation_config()
        assert config["enabled"] is False
        assert len(config["layer_bias_adjustments"]) == 0
    
    def test_dry_run_mode(self, mock_project):
        """Test dry run mode (no actual execution)."""
        # Disable mock mode for this test
        set_mock_mode(False)
        
        tuner = BiasTuner(
            mock_project,
            dry_run=True
        )
        
        # Should not fail even without cli.py
        result = tuner.run_baseline_measurement()
        
        # Should still return valid structure
        assert result["type"] == "baseline"
        assert "bias_errors" in result
        
        # But no actual execution happened
        assert len(tuner.executor.execution_history) == 0
    
    def test_different_strategies(self, mock_project):
        """Test different compensation strategies."""
        strategies = [
            CompensationStrategy.SAME_PHASE,
            CompensationStrategy.SCALED,
            CompensationStrategy.ADAPTIVE,
            CompensationStrategy.CONSERVATIVE
        ]
        
        import os
        original_cwd = os.getcwd()
        
        for strategy in strategies:
            # Enable mock mode
            test_resources = Path(__file__).parent.parent / "test_resources"
            set_mock_mode(True, test_resources)
            
            # Change to project directory
            os.chdir(mock_project.parent)
            
            try:
                tuner = BiasTuner(mock_project, strategy=strategy)
                
                # Run baseline
                tuner.run_baseline_measurement()
                
                # Tune layer 1
                tuner.executor.set_mock_state("layer1")
                result = tuner.tune_single_layer(1)
                
                # Should succeed with any strategy
                assert result["type"] == "layer_compensation"
                assert 1 in tuner.current_compensation
                
            finally:
                # Cleanup
                os.chdir(original_cwd)
                set_mock_mode(False)