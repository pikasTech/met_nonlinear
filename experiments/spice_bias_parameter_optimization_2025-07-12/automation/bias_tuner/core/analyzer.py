"""
Error analysis module for bias tuner.
Extracts and analyzes bias errors from cli.py analysis results.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np

from ..utils import read_json, get_logger
from ..config.defaults import NETWORK_CONFIG
from ..exceptions import AnalysisDataError

# Module-specific logger
logger = get_logger('bias_tuner.core.analyzer')


class BiasAnalyzer:
    """Analyzes bias errors from inference results."""
    
    # WaveNet5 architecture constants from config
    LAYER_INFO = NETWORK_CONFIG["layer_info"]
    
    def __init__(self, project_path: Path):
        """
        Initialize analyzer for a project.
        
        Args:
            project_path: Path to project directory
        """
        self.project_path = Path(project_path)
        self.inference_path = self.project_path / "data" / "inference"
        self.error_analysis_path = self.inference_path / "error_analysis.json"
        
    def load_error_analysis(self) -> Dict[str, Any]:
        """
        Load error analysis results.
        
        Returns:
            Error analysis dictionary
            
        Raises:
            FileNotFoundError: If error_analysis.json not found
        """
        if not self.error_analysis_path.exists():
            raise AnalysisDataError(
                f"Error analysis not found: {self.error_analysis_path}\n"
                "Run 'cli.py -a' first to generate analysis."
            )
        
        data = read_json(self.error_analysis_path)
        logger.info(f"Loaded error analysis from: {self.error_analysis_path}")
        return data
    
    def extract_bias_error_matrix(self) -> List[List[float]]:
        """
        Extract bias error matrix from analysis results.
        
        Returns:
            Bias error matrix [layers][channels]
            
        Raises:
            KeyError: If expected data structure not found
        """
        data = self.load_error_analysis()
        
        # Navigate to bias error matrix
        try:
            bias_matrix = data["bias_analysis"]["nn_spice_bias"]["bias_error_matrix"]
            logger.info(f"Extracted bias error matrix: {len(bias_matrix)} layers")
            return bias_matrix
        except KeyError as e:
            raise AnalysisDataError(
                f"Could not find bias_error_matrix in analysis results: {e}\n"
                "Ensure cli.py -a was run with bias analysis enabled."
            ) from e
    
    def get_layer_errors(self, layer_idx: int) -> Optional[List[float]]:
        """
        Get bias errors for a specific layer.
        
        Args:
            layer_idx: Layer index (0-based)
            
        Returns:
            List of bias errors per channel, or None if layer not found
        """
        matrix = self.extract_bias_error_matrix()
        
        if 0 <= layer_idx < len(matrix):
            return matrix[layer_idx]
        
        logger.warning(f"Layer {layer_idx} not found in bias error matrix")
        return None
    
    def get_compensatable_layers(self) -> List[int]:
        """
        Get list of layer indices that support compensation.
        
        Returns:
            List of compensatable layer indices
        """
        return [idx for idx, info in self.LAYER_INFO.items() 
                if info["compensatable"]]
    
    def analyze_layer_statistics(self, layer_idx: int) -> Dict[str, float]:
        """
        Calculate statistics for a layer's bias errors.
        
        Args:
            layer_idx: Layer index
            
        Returns:
            Dict with mean, std, max, min statistics
        """
        errors = self.get_layer_errors(layer_idx)
        if errors is None:
            return {}
        
        errors_array = np.array(errors)
        
        stats = {
            "mean": float(np.mean(errors_array)),
            "std": float(np.std(errors_array)),
            "max": float(np.max(errors_array)),
            "min": float(np.min(errors_array)),
            "abs_mean": float(np.mean(np.abs(errors_array))),
            "channel_count": len(errors)
        }
        
        logger.debug(f"Layer {layer_idx} stats: mean={stats['mean']:.6f}, "
                    f"std={stats['std']:.6f}, max={stats['max']:.6f}")
        
        return stats
    
    def get_worst_layers(self, metric: str = "abs_mean") -> List[Tuple[int, float]]:
        """
        Get layers sorted by error magnitude.
        
        Args:
            metric: Metric to sort by ('abs_mean', 'mean', 'max', 'std')
            
        Returns:
            List of (layer_idx, metric_value) tuples, sorted worst first
        """
        results = []
        
        for layer_idx in self.get_compensatable_layers():
            stats = self.analyze_layer_statistics(layer_idx)
            if stats and metric in stats:
                results.append((layer_idx, stats[metric]))
        
        # Sort by metric value (descending)
        results.sort(key=lambda x: abs(x[1]), reverse=True)
        
        logger.info(f"Worst layers by {metric}: {results}")
        return results
    
    def compare_analyses(self, other_path: Path) -> Dict[str, Any]:
        """
        Compare current analysis with another error analysis file.
        
        Args:
            other_path: Path to another error_analysis.json
            
        Returns:
            Comparison results dictionary
        """
        # Load both analyses
        current = self.load_error_analysis()
        other_data = read_json(other_path)
        
        # Extract matrices
        current_matrix = current["bias_analysis"]["nn_spice_bias"]["bias_error_matrix"]
        other_matrix = other_data["bias_analysis"]["nn_spice_bias"]["bias_error_matrix"]
        
        comparison = {
            "layer_improvements": {},
            "total_improvement": 0.0
        }
        
        # Compare each layer
        for layer_idx in range(min(len(current_matrix), len(other_matrix))):
            if layer_idx not in self.LAYER_INFO:
                continue
                
            current_errors = np.array(current_matrix[layer_idx])
            other_errors = np.array(other_matrix[layer_idx])
            
            # Skip if arrays have different shapes (e.g., output layer)
            if current_errors.shape != other_errors.shape:
                continue
            
            current_mean = float(np.mean(np.abs(current_errors)))
            other_mean = float(np.mean(np.abs(other_errors)))
            
            if other_mean > 0:
                improvement_pct = ((other_mean - current_mean) / other_mean) * 100
            else:
                improvement_pct = 0.0 if current_mean == 0 else 100.0
            
            comparison["layer_improvements"][layer_idx] = {
                "name": self.LAYER_INFO[layer_idx]["name"],
                "before": other_mean,
                "after": current_mean,
                "improvement_percent": improvement_pct
            }
        
        # Calculate total improvement
        total_before = sum(comp["before"] for comp in comparison["layer_improvements"].values())
        total_after = sum(comp["after"] for comp in comparison["layer_improvements"].values())
        
        if total_before > 0:
            comparison["total_improvement"] = ((total_before - total_after) / total_before) * 100
        
        return comparison
    
    def format_bias_errors(self, layer_idx: int) -> str:
        """
        Format bias errors for a layer as a readable string.
        
        Args:
            layer_idx: Layer index
            
        Returns:
            Formatted string
        """
        errors = self.get_layer_errors(layer_idx)
        if errors is None:
            return f"Layer {layer_idx}: No data"
        
        stats = self.analyze_layer_statistics(layer_idx)
        layer_info = self.LAYER_INFO.get(layer_idx, {})
        
        lines = [
            f"Layer {layer_idx} ({layer_info.get('name', 'Unknown')}):",
            f"  Channels: {stats['channel_count']}",
            f"  Mean error: {stats['mean']:.6f}",
            f"  Abs mean: {stats['abs_mean']:.6f}",
            f"  Std dev: {stats['std']:.6f}",
            f"  Range: [{stats['min']:.6f}, {stats['max']:.6f}]",
            f"  Per-channel errors: {[f'{e:.6f}' for e in errors]}"
        ]
        
        return "\n".join(lines)