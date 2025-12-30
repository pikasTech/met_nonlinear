"""
Main bias tuner module.
Orchestrates the complete bias compensation tuning workflow.
"""

import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

from .core import (
    ConfigManager, 
    BiasAnalyzer, 
    BiasCompensator, 
    CompensationStrategy,
    CommandExecutor
)
from .utils import get_logger, write_json
from .config.defaults import NETWORK_CONFIG, EXECUTION_CONFIG, TUNING_CONFIG, ENVIRONMENT_CONFIG
from .exceptions import (
    ConvergenceError,
    InferenceError,
    AnalysisError,
    InvalidLayerError,
    CompensationError
)

logger = get_logger('bias_tuner.tuner')


class BiasTuner:
    """Main class for automated bias compensation tuning."""
    
    def __init__(
        self, 
        project_path: Path,
        strategy: CompensationStrategy = CompensationStrategy.SAME_PHASE,
        python_env: Optional[str] = None,
        dry_run: bool = False
    ):
        """
        Initialize bias tuner.
        
        Args:
            project_path: Path to project directory
            strategy: Compensation calculation strategy
            python_env: Python environment command (uses config default if None)
            dry_run: If True, don't execute commands
        """
        if python_env is None:
            python_env = ENVIRONMENT_CONFIG["conda_python_env"]
        self.project_path = Path(project_path)
        self.project_name = self.project_path.name
        self.dry_run = dry_run
        
        # Initialize components
        self.config_manager = ConfigManager(self.project_path)
        self.analyzer = BiasAnalyzer(self.project_path)
        self.compensator = BiasCompensator(strategy)
        self.executor = CommandExecutor(python_env=python_env)
        
        # Tuning state
        self.tuning_history: List[Dict[str, Any]] = []
        self.current_compensation: Dict[int, List[float]] = {}
        
        logger.info(f"Initialized BiasTuner for project: {self.project_name}")
        logger.info(f"Strategy: {strategy.value}, Dry run: {dry_run}")
    
    def run_baseline_measurement(self) -> Dict[str, Any]:
        """
        Run baseline measurement without compensation.
        
        Returns:
            Baseline measurement results
        """
        logger.info("=== Running baseline measurement ===")
        
        # Load and backup config
        self.config_manager.load_config()
        
        # Disable compensation
        self.config_manager.set_bias_compensation_enabled(False)
        self.config_manager.clear_all_compensations()
        self.config_manager.save_config()
        
        # Run inference and analysis
        if not self.dry_run:
            success, msg = self.executor.run_inference(self.project_name)
            if not success:
                raise InferenceError(f"Baseline inference failed: {msg}")
            
            success, msg = self.executor.run_analysis(self.project_name)
            if not success:
                raise AnalysisError(f"Baseline analysis failed: {msg}")
        
        # Extract baseline errors
        bias_matrix = self.analyzer.extract_bias_error_matrix()
        
        baseline_result = {
            "timestamp": datetime.now().isoformat(),
            "type": "baseline",
            "bias_errors": bias_matrix,
            "statistics": {}
        }
        
        # Calculate statistics for each layer
        for layer_idx in self.analyzer.get_compensatable_layers():
            stats = self.analyzer.analyze_layer_statistics(layer_idx)
            baseline_result["statistics"][layer_idx] = stats
        
        self.tuning_history.append(baseline_result)
        logger.info("Baseline measurement completed")
        
        return baseline_result
    
    def tune_single_layer(
        self, 
        layer_idx: int,
        scale_factor: float = 1.0
    ) -> Dict[str, Any]:
        """
        Tune compensation for a single layer.
        
        Args:
            layer_idx: Layer index to tune
            scale_factor: Compensation scale factor
            
        Returns:
            Tuning result dictionary
        """
        logger.info(f"=== Tuning layer {layer_idx} ===")
        
        # Get current errors for this layer
        current_errors = self.analyzer.get_layer_errors(layer_idx)
        if current_errors is None:
            raise InvalidLayerError(f"No error data for layer {layer_idx}")
        
        # Calculate compensation
        compensation = self.compensator.calculate_compensation(
            current_errors, 
            scale_factor
        )
        
        # Update compensation state
        self.current_compensation[layer_idx] = compensation
        
        # Apply to config
        self.config_manager.apply_compensation_state(self.current_compensation)
        self.config_manager.save_config()
        
        logger.info(f"Applied compensation to layer {layer_idx}: {compensation}")
        
        # Run inference and analysis
        if not self.dry_run:
            success, msg = self.executor.run_inference(self.project_name)
            if not success:
                raise InferenceError(f"Inference failed: {msg}")
            
            success, msg = self.executor.run_analysis(self.project_name)
            if not success:
                raise AnalysisError(f"Analysis failed: {msg}")
        
        # Extract new errors
        new_bias_matrix = self.analyzer.extract_bias_error_matrix()
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "type": "layer_compensation",
            "layer_idx": layer_idx,
            "scale_factor": scale_factor,
            "compensation_applied": compensation,
            "bias_errors_after": new_bias_matrix,
            "statistics": {}
        }
        
        # Calculate statistics
        for idx in self.analyzer.get_compensatable_layers():
            stats = self.analyzer.analyze_layer_statistics(idx)
            result["statistics"][idx] = stats
        
        self.tuning_history.append(result)
        
        # Log improvement
        if len(self.tuning_history) >= 2:
            self._log_improvement(layer_idx)
        
        return result
    
    def tune_sequential(
        self,
        layer_order: Optional[List[int]] = None,
        scale_factors: Optional[Dict[int, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Tune layers sequentially in specified order.
        
        Args:
            layer_order: Order of layers to tune (default: by error magnitude)
            scale_factors: Scale factors per layer (default: 1.0)
            
        Returns:
            List of tuning results
        """
        logger.info("=== Starting sequential tuning ===")
        
        # Determine layer order
        if layer_order is None:
            # Order by error magnitude
            worst_layers = self.analyzer.get_worst_layers()
            layer_order = [layer_idx for layer_idx, _ in worst_layers]
        
        # Default scale factors
        if scale_factors is None:
            scale_factors = {idx: 1.0 for idx in layer_order}
        
        results = []
        
        # Tune each layer sequentially
        for layer_idx in layer_order:
            scale = scale_factors.get(layer_idx, 1.0)
            
            try:
                result = self.tune_single_layer(layer_idx, scale)
                results.append(result)
                
                # Small delay between layers
                if not self.dry_run:
                    time.sleep(EXECUTION_CONFIG["layer_delay"])
                    
            except (InferenceError, AnalysisError, CompensationError) as e:
                logger.error(f"Failed to tune layer {layer_idx}: {e}")
                break
        
        logger.info(f"Sequential tuning completed: {len(results)} layers tuned")
        return results
    
    def optimize_layer(
        self,
        layer_idx: int,
        target_error: Optional[float] = None,
        max_iterations: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Iteratively optimize a single layer to target error.
        
        Args:
            layer_idx: Layer to optimize
            target_error: Target mean absolute error (uses config default if None)
            max_iterations: Maximum optimization iterations (uses config default if None)
            
        Returns:
            Optimization result
        """
        if target_error is None:
            target_error = TUNING_CONFIG["default_target_error"]
        if max_iterations is None:
            from .config.defaults import COMPENSATION_CONFIG
            max_iterations = COMPENSATION_CONFIG["iteration"]["max_iterations"]
        logger.info(f"=== Optimizing layer {layer_idx} to target {target_error} ===")
        
        optimization_result = {
            "layer_idx": layer_idx,
            "target_error": target_error,
            "iterations": [],
            "final_error": None,
            "success": False
        }
        
        for iteration in range(max_iterations):
            # Get current errors
            current_errors = self.analyzer.get_layer_errors(layer_idx)
            stats = self.analyzer.analyze_layer_statistics(layer_idx)
            current_mean_error = stats["abs_mean"]
            
            logger.info(f"Iteration {iteration + 1}: current error = {current_mean_error:.6f}")
            
            # Check if target reached
            if current_mean_error <= target_error:
                logger.info(f"Target error reached!")
                optimization_result["success"] = True
                optimization_result["final_error"] = current_mean_error
                break
            
            # Calculate scale factor based on how far we are from target
            from .config.defaults import COMPENSATION_CONFIG
            max_scale = COMPENSATION_CONFIG["optimization"]["max_scale_factor"]
            scale_factor = min(max_scale, target_error / current_mean_error)
            
            # Apply compensation
            result = self.tune_single_layer(layer_idx, scale_factor)
            
            optimization_result["iterations"].append({
                "iteration": iteration + 1,
                "scale_factor": scale_factor,
                "error_before": current_mean_error,
                "error_after": result["statistics"][layer_idx]["abs_mean"]
            })
            
            # Check for divergence
            from .config.defaults import COMPENSATION_CONFIG
            divergence_threshold = COMPENSATION_CONFIG["optimization"]["divergence_threshold"]
            if result["statistics"][layer_idx]["abs_mean"] > current_mean_error * divergence_threshold:
                logger.warning("Optimization diverging, stopping")
                break
        
        optimization_result["final_error"] = self.analyzer.analyze_layer_statistics(layer_idx)["abs_mean"]
        
        return optimization_result
    
    def generate_report(self, output_path: Optional[Path] = None) -> Path:
        """
        Generate comprehensive tuning report.
        
        Args:
            output_path: Path for report (auto-generated if None)
            
        Returns:
            Path to generated report
        """
        if output_path is None:
            timestamp = datetime.now().strftime(TUNING_CONFIG["report_timestamp_format"])
            output_path = self.project_path / f"bias_tuning_report_{timestamp}.json"
        
        # Get final state
        final_matrix = self.analyzer.extract_bias_error_matrix()
        
        report = {
            "project": self.project_name,
            "timestamp": datetime.now().isoformat(),
            "strategy": self.compensator.strategy.value,
            "tuning_history": self.tuning_history,
            "final_compensation": self.current_compensation,
            "final_bias_errors": final_matrix,
            "summary": self._generate_summary()
        }
        
        write_json(report, output_path)
        logger.info(f"Generated report: {output_path}")
        
        return output_path
    
    def _log_improvement(self, layer_idx: int) -> None:
        """Log improvement for a layer."""
        if len(self.tuning_history) < 2:
            return
        
        # Get before/after from history
        before = self.tuning_history[-2]["statistics"].get(layer_idx, {})
        after = self.tuning_history[-1]["statistics"].get(layer_idx, {})
        
        if before and after:
            before_error = before.get("abs_mean", 0)
            after_error = after.get("abs_mean", 0)
            
            if before_error > 0:
                improvement = (before_error - after_error) / before_error * 100
                
                if improvement > 0:
                    logger.info(f"Layer {layer_idx} improved by {improvement:.1f}%")
                else:
                    logger.warning(f"Layer {layer_idx} degraded by {-improvement:.1f}%")
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary of tuning results."""
        if not self.tuning_history:
            return {}
        
        # Find baseline
        baseline = None
        for record in self.tuning_history:
            if record.get("type") == "baseline":
                baseline = record
                break
        
        if not baseline:
            return {}
        
        # Calculate improvements
        summary = {
            "total_iterations": len(self.tuning_history),
            "layers_tuned": list(self.current_compensation.keys()),
            "layer_improvements": {}
        }
        
        # Compare baseline to current
        baseline_stats = baseline.get("statistics", {})
        current_stats = self.tuning_history[-1].get("statistics", {})
        
        for layer_idx in self.analyzer.get_compensatable_layers():
            if layer_idx in baseline_stats and layer_idx in current_stats:
                before = baseline_stats[layer_idx]["abs_mean"]
                after = current_stats[layer_idx]["abs_mean"]
                
                improvement = (before - after) / before * 100 if before > 0 else 0
                
                summary["layer_improvements"][layer_idx] = {
                    "before": before,
                    "after": after,
                    "improvement_percent": improvement
                }
        
        # Overall improvement
        total_before = sum(
            stats["before"] 
            for stats in summary["layer_improvements"].values()
        )
        total_after = sum(
            stats["after"] 
            for stats in summary["layer_improvements"].values()
        )
        
        summary["overall_improvement"] = (
            (total_before - total_after) / total_before * 100 
            if total_before > 0 else 0
        )
        
        return summary
    
    def reset(self) -> None:
        """Reset tuner to initial state."""
        self.tuning_history.clear()
        self.current_compensation.clear()
        self.compensator.reset_history()
        
        # Restore original config
        self.config_manager.restore_original()
        self.config_manager.save_config()
        
        logger.info("Tuner reset to initial state")