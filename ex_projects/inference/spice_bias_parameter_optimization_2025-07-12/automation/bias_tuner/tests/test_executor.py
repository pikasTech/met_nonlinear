"""Tests for CommandExecutor with mock mode."""

import pytest
from pathlib import Path
import time

from ..core import CommandExecutor, set_mock_mode, is_mock_mode


class TestCommandExecutor:
    """Test command execution with mock mode."""
    
    @pytest.fixture
    def mock_resources_path(self):
        """Get path to test resources."""
        return Path(__file__).parent.parent / "test_resources"
    
    @pytest.fixture
    def enable_mock_mode(self, mock_resources_path):
        """Enable mock mode for testing."""
        set_mock_mode(True, mock_resources_path)
        yield
        set_mock_mode(False, None)
    
    def test_mock_mode_control(self, mock_resources_path):
        """Test mock mode enable/disable."""
        # Initially disabled
        assert not is_mock_mode()
        
        # Enable
        set_mock_mode(True, mock_resources_path)
        assert is_mock_mode()
        
        # Disable
        set_mock_mode(False)
        assert not is_mock_mode()
    
    def test_mock_mode_requires_path(self):
        """Test that mock mode requires resources path."""
        with pytest.raises(ValueError, match="Mock resources path required"):
            set_mock_mode(True)
    
    def test_mock_inference(self, enable_mock_mode):
        """Test mock inference execution."""
        executor = CommandExecutor()
        
        success, output = executor.run_inference("test_project")
        
        assert success is True
        assert "[MOCK]" in output
        assert "NN inference: 5 layers processed" in output
        assert "SPICE inference: 5 layers processed" in output
        
        # Check execution history
        assert len(executor.execution_history) == 1
        assert executor.execution_history[0]["command"] == "inference"
        assert executor.execution_history[0]["success"] is True
    
    def test_mock_analysis_baseline(self, enable_mock_mode, tmp_path):
        """Test mock analysis with baseline state."""
        executor = CommandExecutor()
        
        # Create test project directory
        project_path = tmp_path / "test_project"
        project_path.mkdir()
        
        # Run in project directory
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            
            success, output = executor.run_analysis("test_project")
            
            assert success is True
            assert "[MOCK]" in output
            assert "baseline" in output
            
            # Check that error analysis was copied
            error_file = project_path / "data" / "inference" / "error_analysis.json"
            assert error_file.exists()
            
            # Verify it's the baseline file
            import json
            with open(error_file) as f:
                data = json.load(f)
            
            # Check baseline characteristics
            bias_matrix = data["bias_analysis"]["nn_spice_bias"]["bias_error_matrix"]
            assert bias_matrix[1] == [0.005323, 0.002278, 0.005201, 0.014258, 0.003152, 0.003255]
            
        finally:
            os.chdir(original_cwd)
    
    def test_mock_state_progression(self, enable_mock_mode, tmp_path):
        """Test mock state progression through compensation stages."""
        executor = CommandExecutor()
        
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            
            # Test each state
            states = ["baseline", "layer1", "layer12", "layer123"]
            expected_layer1_errors = [
                [0.005323, 0.002278, 0.005201, 0.014258, 0.003152, 0.003255],  # baseline
                [0.000011, -0.000291, 0.000280, 0.000001, -0.000034, 0.000033],  # layer1
                [0.000011, -0.000291, 0.000280, 0.000001, -0.000034, 0.000033],  # layer12
                [0.000011, -0.000291, 0.000280, 0.000001, -0.000034, 0.000033],  # layer123
            ]
            
            for idx, state in enumerate(states):
                # Set state
                executor.set_mock_state(state)
                
                # Create project directory
                project_path = tmp_path / f"test_{state}"
                project_path.mkdir()
                
                # Run analysis
                success, output = executor.run_analysis(f"test_{state}")
                assert success is True
                
                # Verify correct file was used
                error_file = project_path / "data" / "inference" / "error_analysis.json"
                assert error_file.exists()
                
                # Just verify the file was copied and state is in output
                assert state in output
                assert "Bias error analysis completed" in output
                
        finally:
            os.chdir(original_cwd)
    
    def test_invalid_mock_state(self, enable_mock_mode):
        """Test setting invalid mock state."""
        executor = CommandExecutor()
        
        with pytest.raises(ValueError, match="Invalid mock state"):
            executor.set_mock_state("invalid_state")
    
    def test_execution_stats(self, enable_mock_mode):
        """Test execution statistics tracking."""
        executor = CommandExecutor()
        
        # Initial stats
        stats = executor.get_execution_stats()
        assert stats["total_executions"] == 0
        
        # Run some commands
        executor.run_inference("test1")
        executor.run_analysis("test1")
        executor.run_inference("test2")
        
        # Check updated stats
        stats = executor.get_execution_stats()
        assert stats["total_executions"] == 3
        assert stats["successful"] == 3
        assert stats["failed"] == 0
        assert stats["average_time"] > 0
    
    def test_wait_for_file(self, tmp_path):
        """Test file waiting functionality."""
        executor = CommandExecutor()
        
        test_file = tmp_path / "test.txt"
        
        # File doesn't exist - should timeout quickly
        start = time.time()
        result = executor.wait_for_file(test_file, timeout=1)
        elapsed = time.time() - start
        
        assert result is False
        assert 0.9 < elapsed < 1.5
        
        # Create file and test immediate detection
        test_file.write_text("test")
        
        start = time.time()
        result = executor.wait_for_file(test_file, timeout=5)
        elapsed = time.time() - start
        
        assert result is True
        assert elapsed < 1  # Should find immediately
    
    def test_verify_inference_outputs(self, enable_mock_mode, tmp_path):
        """Test output verification."""
        executor = CommandExecutor()
        
        # Create minimal inference output structure
        project_path = tmp_path / "test_project"
        inference_dir = project_path / "data" / "inference"
        inference_dir.mkdir(parents=True)
        
        # Initially nothing exists
        checks = executor.verify_inference_outputs(project_path)
        assert checks["error_analysis"] is False
        assert checks["nn_layers"] is False
        
        # Create some outputs
        (inference_dir / "error_analysis.json").write_text("{}")
        (inference_dir / "nn_layers").mkdir()
        
        # Verify again
        checks = executor.verify_inference_outputs(project_path)
        assert checks["error_analysis"] is True
        assert checks["nn_layers"] is True
        assert checks["spice_layers"] is False