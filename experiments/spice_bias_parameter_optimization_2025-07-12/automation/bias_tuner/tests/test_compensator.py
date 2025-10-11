"""Tests for BiasCompensator."""

import pytest
import numpy as np

from ..core import BiasCompensator, CompensationStrategy


class TestBiasCompensator:
    """Test compensation calculation functionality."""
    
    def test_same_phase_compensation(self):
        """Test same-phase compensation strategy."""
        compensator = BiasCompensator(CompensationStrategy.SAME_PHASE)
        
        errors = [0.005, -0.002, 0.001, -0.008, 0.003, 0.006]
        compensation = compensator.calculate_compensation(errors, scale_factor=1.0)
        
        # Same phase means same sign and magnitude
        assert compensation == errors
    
    def test_same_phase_with_scale(self):
        """Test same-phase compensation with scaling."""
        compensator = BiasCompensator(CompensationStrategy.SAME_PHASE)
        
        errors = [0.01, -0.02, 0.03]
        scale = 0.5
        compensation = compensator.calculate_compensation(errors, scale_factor=scale)
        
        expected = [e * scale for e in errors]
        assert compensation == expected
    
    def test_scaled_compensation(self):
        """Test scaled compensation strategy."""
        compensator = BiasCompensator(CompensationStrategy.SCALED)
        
        errors = [0.01, -0.02, 0.03]
        compensation = compensator.calculate_compensation(errors, scale_factor=0.8)
        
        expected = [0.008, -0.016, 0.024]
        np.testing.assert_array_almost_equal(compensation, expected)
    
    def test_conservative_compensation(self):
        """Test conservative compensation strategy."""
        compensator = BiasCompensator(CompensationStrategy.CONSERVATIVE)
        
        errors = [0.01, -0.02, 0.03]
        compensation = compensator.calculate_compensation(errors)
        
        # Conservative uses 50% compensation
        expected = [0.005, -0.01, 0.015]
        np.testing.assert_array_almost_equal(compensation, expected)
    
    def test_adaptive_compensation(self):
        """Test adaptive compensation strategy."""
        compensator = BiasCompensator(CompensationStrategy.ADAPTIVE)
        
        # Mix of small and large errors
        errors = [0.001, 0.01, 0.1]  # Small, medium, large
        compensation = compensator.calculate_compensation(errors)
        
        # Adaptive should scale differently based on magnitude
        # Small errors get less aggressive compensation
        assert abs(compensation[0]) < abs(errors[0])
        # Large errors get more aggressive compensation
        assert abs(compensation[2]) == abs(errors[2])
    
    def test_constraints_application(self):
        """Test applying constraints to compensation."""
        compensator = BiasCompensator(CompensationStrategy.SAME_PHASE)
        
        errors = [0.01, -0.02, 0.03, -0.001, 0.0005]
        constraints = {
            "max_adjustment": 0.015,
            "min_adjustment": -0.015
        }
        
        compensation = compensator.calculate_compensation(
            errors, 
            scale_factor=1.0,
            constraints=constraints
        )
        
        # Check constraints are applied
        assert max(compensation) <= 0.015
        assert min(compensation) >= -0.015
        # Values within constraints should be unchanged
        assert compensation[0] == 0.01
        assert compensation[3] == -0.001
    
    def test_compensation_history(self):
        """Test that compensation history is tracked."""
        compensator = BiasCompensator(CompensationStrategy.SAME_PHASE)
        
        # Clear history
        compensator.reset_history()
        assert len(compensator.compensation_history) == 0
        
        # Calculate some compensations
        errors1 = [0.01, -0.02]
        compensator.calculate_compensation(errors1, scale_factor=0.5)
        
        errors2 = [0.03, -0.04]
        compensator.calculate_compensation(errors2, scale_factor=0.8)
        
        # Check history
        assert len(compensator.compensation_history) == 2
        
        # Verify history content
        assert compensator.compensation_history[0]["scale_factor"] == 0.5
        assert compensator.compensation_history[1]["scale_factor"] == 0.8
        assert compensator.compensation_history[0]["channels"] == 2
        assert compensator.compensation_history[1]["channels"] == 2
    
    def test_optimize_scale_factor(self):
        """Test scale factor optimization."""
        compensator = BiasCompensator(CompensationStrategy.SAME_PHASE)
        
        errors = [0.01, -0.02, 0.03, -0.01, 0.02]
        target_reduction = 0.8  # Want 80% reduction
        
        optimal_scale, compensation = compensator.optimize_scale_factor(
            errors, 
            target_reduction
        )
        
        # Scale should be reasonable
        assert 0.1 <= optimal_scale <= 2.0
        assert len(compensation) == len(errors)
    
    def test_suggest_iterative_steps(self):
        """Test iterative compensation suggestion."""
        compensator = BiasCompensator(CompensationStrategy.SAME_PHASE)
        
        errors = [0.01, -0.02, 0.03]
        steps = compensator.suggest_iterative_steps(errors, max_iterations=3)
        
        assert len(steps) <= 3
        
        # Each step should have required fields
        for step in steps:
            assert "iteration" in step
            assert "compensation" in step
            assert "expected_residuals" in step
            assert "expected_improvement" in step
        
        # Improvements should be positive
        for step in steps:
            assert step["expected_improvement"] >= 0
    
    def test_real_compensation_values(self):
        """Test with real compensation values from experiments."""
        compensator = BiasCompensator(CompensationStrategy.SAME_PHASE)
        
        # Real layer 1 errors from baseline
        layer1_errors = [0.005323, 0.002278, 0.005201, 0.014258, 0.003152, 0.003255]
        
        # Calculate compensation
        compensation = compensator.calculate_compensation(layer1_errors)
        
        # Should match the errors exactly for same-phase
        assert compensation == layer1_errors
        
        # Test with the actual scale factor used in experiments
        compensation_scaled = compensator.calculate_compensation(
            layer1_errors, 
            scale_factor=1.0
        )
        
        np.testing.assert_array_almost_equal(
            compensation_scaled,
            [0.005323, 0.002278, 0.005201, 0.014258, 0.003152, 0.003255]
        )