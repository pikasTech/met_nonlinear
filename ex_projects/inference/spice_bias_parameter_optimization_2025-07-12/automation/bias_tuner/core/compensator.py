"""
Compensation calculation module for bias tuner.
Implements various compensation strategies and optimization algorithms.
"""

from typing import List, Dict, Optional, Tuple, Any
import numpy as np
from enum import Enum

from ..utils import get_logger
from ..config.defaults import COMPENSATION_CONFIG

# Module-specific logger
logger = get_logger('bias_tuner.core.compensator')


class CompensationStrategy(Enum):
    """Available compensation strategies."""
    SAME_PHASE = "same_phase"          # Simple same-phase 100% compensation
    SCALED = "scaled"                  # Scaled compensation with factor
    ADAPTIVE = "adaptive"              # Adaptive based on error magnitude
    CONSERVATIVE = "conservative"      # Conservative 50% compensation


class BiasCompensator:
    """Calculates optimal compensation values based on bias errors."""
    
    def __init__(self, strategy: CompensationStrategy = CompensationStrategy.SAME_PHASE):
        """
        Initialize compensator with strategy.
        
        Args:
            strategy: Compensation strategy to use
        """
        self.strategy = strategy
        self.compensation_history: List[Dict[str, Any]] = []
        
    def calculate_compensation(
        self, 
        bias_errors: List[float], 
        scale_factor: float = 1.0,
        constraints: Optional[Dict[str, float]] = None
    ) -> List[float]:
        """
        Calculate compensation values for given bias errors.
        
        Args:
            bias_errors: List of bias errors per channel
            scale_factor: Scaling factor for compensation (0-1)
            constraints: Optional constraints (max_adjustment, min_adjustment)
            
        Returns:
            List of compensation values
        """
        if self.strategy == CompensationStrategy.SAME_PHASE:
            compensation = self._same_phase_compensation(bias_errors, scale_factor)
        elif self.strategy == CompensationStrategy.SCALED:
            compensation = self._scaled_compensation(bias_errors, scale_factor)
        elif self.strategy == CompensationStrategy.ADAPTIVE:
            compensation = self._adaptive_compensation(bias_errors)
        elif self.strategy == CompensationStrategy.CONSERVATIVE:
            compensation = self._conservative_compensation(bias_errors)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")
        
        # Apply constraints if provided
        if constraints:
            compensation = self._apply_constraints(compensation, constraints)
        
        # Log compensation
        self._log_compensation(bias_errors, compensation, scale_factor)
        
        return compensation
    
    def _same_phase_compensation(
        self, 
        bias_errors: List[float], 
        scale_factor: float = 1.0
    ) -> List[float]:
        """
        Same-phase compensation: compensate with same sign and magnitude.
        This is counterintuitive but matches experimental findings.
        
        Args:
            bias_errors: Bias errors
            scale_factor: Scaling factor
            
        Returns:
            Compensation values
        """
        # Same sign compensation (experimentally validated)
        compensation = [error * scale_factor for error in bias_errors]
        
        logger.debug(f"Same-phase compensation with factor {scale_factor}")
        return compensation
    
    def _scaled_compensation(
        self, 
        bias_errors: List[float], 
        scale_factor: Optional[float] = None
    ) -> List[float]:
        """
        Scaled compensation with configurable factor.
        
        Args:
            bias_errors: Bias errors
            scale_factor: Scaling factor (uses config default if None)
            
        Returns:
            Compensation values
        """
        if scale_factor is None:
            scale_factor = COMPENSATION_CONFIG["default_scale_factor"]
        compensation = [error * scale_factor for error in bias_errors]
        
        logger.debug(f"Scaled compensation with factor {scale_factor}")
        return compensation
    
    def _adaptive_compensation(self, bias_errors: List[float]) -> List[float]:
        """
        Adaptive compensation based on error magnitude.
        Larger errors get more aggressive compensation.
        
        Args:
            bias_errors: Bias errors
            
        Returns:
            Compensation values
        """
        errors_array = np.array(bias_errors)
        abs_mean = np.mean(np.abs(errors_array))
        
        compensation = []
        thresholds = COMPENSATION_CONFIG["adaptive_thresholds"]
        scales = COMPENSATION_CONFIG["adaptive_scales"]
        
        for error in bias_errors:
            abs_error = abs(error)
            
            # Adaptive scaling based on error magnitude
            if abs_error < abs_mean * thresholds["small_error"]:
                # Small errors: gentle compensation
                scale = scales["small"]
            elif abs_error < abs_mean * thresholds["large_error"]:
                # Medium errors: standard compensation
                scale = scales["medium"]
            else:
                # Large errors: aggressive compensation
                scale = scales["large"]
            
            compensation.append(error * scale)
        
        logger.debug("Adaptive compensation based on error magnitudes")
        return compensation
    
    def _conservative_compensation(self, bias_errors: List[float]) -> List[float]:
        """
        Conservative compensation to avoid overshooting.
        
        Args:
            bias_errors: Bias errors
            
        Returns:
            Compensation values
        """
        factor = COMPENSATION_CONFIG["conservative_factor"]
        compensation = [error * factor for error in bias_errors]
        
        logger.debug(f"Conservative {factor*100:.0f}% compensation")
        return compensation
    
    def _apply_constraints(
        self, 
        compensation: List[float], 
        constraints: Dict[str, float]
    ) -> List[float]:
        """
        Apply constraints to compensation values.
        
        Args:
            compensation: Raw compensation values
            constraints: Dict with max_adjustment, min_adjustment
            
        Returns:
            Constrained compensation values
        """
        max_adj = constraints.get("max_adjustment", float("inf"))
        min_adj = constraints.get("min_adjustment", -float("inf"))
        
        constrained = []
        for comp in compensation:
            # Clip to constraints
            comp_clipped = max(min_adj, min(max_adj, comp))
            constrained.append(comp_clipped)
        
        # Log if any values were clipped
        if constrained != compensation:
            logger.warning(f"Applied constraints: [{min_adj}, {max_adj}]")
        
        return constrained
    
    def _log_compensation(
        self, 
        errors: List[float], 
        compensation: List[float], 
        scale_factor: float
    ) -> None:
        """Log compensation calculation for history."""
        record = {
            "strategy": self.strategy.value,
            "scale_factor": scale_factor,
            "input_errors": errors,
            "compensation_values": compensation,
            "channels": len(errors)
        }
        
        self.compensation_history.append(record)
        
        logger.info(
            f"Calculated {self.strategy.value} compensation for "
            f"{len(errors)} channels with scale {scale_factor}"
        )
    
    def optimize_scale_factor(
        self, 
        bias_errors: List[float],
        target_reduction: Optional[float] = None
    ) -> Tuple[float, List[float]]:
        """
        Find optimal scale factor to achieve target error reduction.
        
        Args:
            bias_errors: Current bias errors
            target_reduction: Target reduction ratio (0-1) (uses config default if None)
            
        Returns:
            Tuple of (optimal_scale, compensation_values)
        """
        if target_reduction is None:
            target_reduction = COMPENSATION_CONFIG["optimization"]["default_target_reduction"]
        # Simple optimization: try different scales
        opt_config = COMPENSATION_CONFIG["optimization"]
        min_scale, max_scale = opt_config["search_range"]
        num_points = opt_config["search_points"]
        scales = np.linspace(min_scale, max_scale, num_points)
        best_scale = 1.0
        best_score = float("inf")
        
        for scale in scales:
            # Calculate expected residual
            compensation = self.calculate_compensation(bias_errors, scale)
            
            # Estimate residual errors (assuming linear response)
            residuals = [e - c for e, c in zip(bias_errors, compensation)]
            score = np.mean(np.abs(residuals))
            
            # Check if this achieves target
            original_score = np.mean(np.abs(bias_errors))
            reduction = 1 - (score / original_score) if original_score > 0 else 0
            
            if abs(reduction - target_reduction) < abs(best_score - target_reduction):
                best_scale = scale
                best_score = reduction
        
        logger.info(
            f"Optimal scale factor: {best_scale:.2f} "
            f"(expected reduction: {best_score:.1%})"
        )
        
        # Return optimal compensation
        return best_scale, self.calculate_compensation(bias_errors, best_scale)
    
    def suggest_iterative_steps(
        self, 
        bias_errors: List[float],
        max_iterations: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Suggest iterative compensation steps to gradually reduce errors.
        
        Args:
            bias_errors: Initial bias errors
            max_iterations: Maximum iterations (uses config default if None)
            
        Returns:
            List of compensation steps
        """
        if max_iterations is None:
            max_iterations = COMPENSATION_CONFIG["iteration"]["max_iterations"]
        steps = []
        current_errors = bias_errors.copy()
        
        for i in range(max_iterations):
            # Use conservative strategy for iterations
            iter_config = COMPENSATION_CONFIG["iteration"]
            scale = iter_config["initial_scale"] if i == 0 else iter_config["subsequent_scale"]
            
            compensation = self.calculate_compensation(current_errors, scale)
            
            # Estimate residual errors
            residuals = [e - c for e, c in zip(current_errors, compensation)]
            
            step = {
                "iteration": i + 1,
                "compensation": compensation,
                "expected_residuals": residuals,
                "expected_improvement": self._calculate_improvement(
                    current_errors, residuals
                )
            }
            
            steps.append(step)
            
            # Update for next iteration
            current_errors = residuals
            
            # Stop if errors are small enough
            if np.mean(np.abs(residuals)) < COMPENSATION_CONFIG["optimization"]["convergence_threshold"]:
                break
        
        logger.info(f"Suggested {len(steps)} iterative compensation steps")
        return steps
    
    def _calculate_improvement(
        self, 
        before: List[float], 
        after: List[float]
    ) -> float:
        """Calculate percentage improvement."""
        before_mean = np.mean(np.abs(before))
        after_mean = np.mean(np.abs(after))
        
        if before_mean > 0:
            return (before_mean - after_mean) / before_mean
        return 0.0
    
    def reset_history(self) -> None:
        """Reset compensation history."""
        self.compensation_history.clear()
        logger.debug("Reset compensation history")