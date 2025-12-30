"""
Configuration management module for bias tuner.
Handles reading, modifying, and validating project configurations.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import copy

from ..utils import read_json, write_json, backup_file, get_logger

# Module-specific logger
logger = get_logger('bias_tuner.core.config_manager')


class ConfigManager:
    """Manages project configuration with bias compensation settings."""
    
    def __init__(self, project_path: Path):
        """
        Initialize config manager for a project.
        
        Args:
            project_path: Path to project directory
        """
        self.project_path = Path(project_path)
        self.config_path = self.project_path / "config.json"
        self.config = None
        self._original_config = None
        
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from project.
        
        Returns:
            Configuration dictionary
            
        Raises:
            FileNotFoundError: If config.json not found
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        self.config = read_json(self.config_path)
        self._original_config = copy.deepcopy(self.config)
        
        logger.info(f"Loaded config from: {self.config_path}")
        return self.config
    
    def save_config(self, backup: bool = True) -> Path:
        """
        Save current configuration to file.
        
        Args:
            backup: Whether to backup existing config
            
        Returns:
            Path to saved config file
        """
        if backup and self.config_path.exists():
            backup_path = backup_file(self.config_path)
            logger.info(f"Created backup: {backup_path}")
        
        write_json(self.config, self.config_path)
        logger.info(f"Saved config to: {self.config_path}")
        
        return self.config_path
    
    def get_bias_compensation_config(self) -> Dict[str, Any]:
        """
        Get bias compensation configuration.
        
        Returns:
            Bias compensation config dict
        """
        if self.config is None:
            self.load_config()
        
        inference_config = self.config.get("inference_config", {})
        bias_comp = inference_config.get("bias_compensation", {
            "enabled": False,
            "layer_bias_adjustments": {}
        })
        
        return bias_comp
    
    def set_bias_compensation_enabled(self, enabled: bool) -> None:
        """
        Enable or disable bias compensation.
        
        Args:
            enabled: Whether to enable compensation
        """
        if self.config is None:
            self.load_config()
        
        if "inference_config" not in self.config:
            self.config["inference_config"] = {}
        
        if "bias_compensation" not in self.config["inference_config"]:
            self.config["inference_config"]["bias_compensation"] = {
                "enabled": False,
                "layer_bias_adjustments": {}
            }
        
        self.config["inference_config"]["bias_compensation"]["enabled"] = enabled
        logger.info(f"Set bias compensation enabled: {enabled}")
    
    def set_layer_compensation(self, layer_idx: int, compensation_values: List[float]) -> None:
        """
        Set compensation values for a specific layer.
        
        Args:
            layer_idx: Layer index (1-based for Dense layers)
            compensation_values: List of compensation values per channel
        """
        if self.config is None:
            self.load_config()
        
        # Ensure structure exists
        if "inference_config" not in self.config:
            self.config["inference_config"] = {}
        
        if "bias_compensation" not in self.config["inference_config"]:
            self.config["inference_config"]["bias_compensation"] = {
                "enabled": False,
                "layer_bias_adjustments": {}
            }
        
        # Set layer compensation
        layer_key = str(layer_idx)
        self.config["inference_config"]["bias_compensation"]["layer_bias_adjustments"][layer_key] = compensation_values
        
        logger.info(f"Set layer {layer_idx} compensation: {compensation_values}")
    
    def clear_all_compensations(self) -> None:
        """Clear all layer compensation values."""
        if self.config is None:
            self.load_config()
        
        if "inference_config" in self.config:
            if "bias_compensation" in self.config["inference_config"]:
                self.config["inference_config"]["bias_compensation"]["layer_bias_adjustments"] = {}
                logger.info("Cleared all layer compensations")
    
    def get_layer_compensation(self, layer_idx: int) -> Optional[List[float]]:
        """
        Get compensation values for a specific layer.
        
        Args:
            layer_idx: Layer index
            
        Returns:
            List of compensation values or None if not set
        """
        bias_config = self.get_bias_compensation_config()
        layer_key = str(layer_idx)
        return bias_config["layer_bias_adjustments"].get(layer_key)
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model-related configuration.
        
        Returns:
            Dict with model type and subconfiguration
        """
        if self.config is None:
            self.load_config()
        
        return {
            "use_model": self.config.get("use_model", "Unknown"),
            "model_subcfg": self.config.get("model_subcfg", {}),
            "dataset_type": self.config.get("dataset_type", "Unknown")
        }
    
    def validate_config(self) -> bool:
        """
        Validate configuration structure.
        
        Returns:
            True if config is valid
        """
        if self.config is None:
            return False
        
        required_keys = ["use_model", "dataset_type"]
        return all(key in self.config for key in required_keys)
    
    def restore_original(self) -> None:
        """Restore configuration to original state when loaded."""
        if self._original_config is not None:
            self.config = copy.deepcopy(self._original_config)
            logger.info("Restored original configuration")
    
    def apply_compensation_state(self, compensation_state: Dict[int, List[float]]) -> None:
        """
        Apply complete compensation state to config.
        
        Args:
            compensation_state: Dict mapping layer index to compensation values
        """
        self.clear_all_compensations()
        
        for layer_idx, values in compensation_state.items():
            self.set_layer_compensation(layer_idx, values)
        
        # Enable compensation if any values are set
        if compensation_state:
            self.set_bias_compensation_enabled(True)
        
        logger.info(f"Applied compensation state for {len(compensation_state)} layers")