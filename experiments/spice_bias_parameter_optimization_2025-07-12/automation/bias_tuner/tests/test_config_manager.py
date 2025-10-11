"""Tests for ConfigManager using real test resources."""

import pytest
import shutil
import tempfile
from pathlib import Path

from ..core import ConfigManager


class TestConfigManager:
    """Test ConfigManager functionality."""
    
    @pytest.fixture
    def test_project_path(self, tmp_path):
        """Create test project with config."""
        # Copy baseline config to test project
        test_resources = Path(__file__).parent.parent / "test_resources"
        baseline_config = test_resources / "config_samples" / "config_baseline.json"
        
        project_path = tmp_path / "test_project"
        project_path.mkdir()
        
        shutil.copy(baseline_config, project_path / "config.json")
        
        return project_path
    
    def test_load_config(self, test_project_path):
        """Test loading configuration."""
        manager = ConfigManager(test_project_path)
        config = manager.load_config()
        
        assert config is not None
        assert config["use_model"] == "WaveNet5"
        assert config["dataset_type"] == "MET"
        assert "inference_config" in config
    
    def test_get_bias_compensation_config(self, test_project_path):
        """Test getting bias compensation config."""
        manager = ConfigManager(test_project_path)
        manager.load_config()
        
        bias_config = manager.get_bias_compensation_config()
        
        assert "enabled" in bias_config
        assert "layer_bias_adjustments" in bias_config
        assert bias_config["enabled"] is False  # Baseline has it disabled
    
    def test_set_bias_compensation_enabled(self, test_project_path):
        """Test enabling/disabling bias compensation."""
        manager = ConfigManager(test_project_path)
        manager.load_config()
        
        # Enable
        manager.set_bias_compensation_enabled(True)
        assert manager.get_bias_compensation_config()["enabled"] is True
        
        # Disable
        manager.set_bias_compensation_enabled(False)
        assert manager.get_bias_compensation_config()["enabled"] is False
    
    def test_set_layer_compensation(self, test_project_path):
        """Test setting layer compensation values."""
        manager = ConfigManager(test_project_path)
        manager.load_config()
        
        # Set compensation for layer 1
        compensation = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        manager.set_layer_compensation(1, compensation)
        
        # Verify
        bias_config = manager.get_bias_compensation_config()
        assert "1" in bias_config["layer_bias_adjustments"]
        assert bias_config["layer_bias_adjustments"]["1"] == compensation
    
    def test_apply_compensation_state(self, test_project_path):
        """Test applying complete compensation state."""
        manager = ConfigManager(test_project_path)
        manager.load_config()
        
        # Apply multi-layer compensation
        state = {
            1: [0.005323, 0.002278, 0.005201, 0.014258, 0.003152, 0.003255],
            2: [0.002181, 0.001301, 0.000932, 0.007533, 0.000669, 0.001903]
        }
        
        manager.apply_compensation_state(state)
        
        # Verify
        bias_config = manager.get_bias_compensation_config()
        assert bias_config["enabled"] is True
        assert "1" in bias_config["layer_bias_adjustments"]
        assert "2" in bias_config["layer_bias_adjustments"]
        assert bias_config["layer_bias_adjustments"]["1"] == state[1]
        assert bias_config["layer_bias_adjustments"]["2"] == state[2]
    
    def test_save_config_with_backup(self, test_project_path):
        """Test saving configuration with backup."""
        manager = ConfigManager(test_project_path)
        manager.load_config()
        
        # Modify config
        manager.set_bias_compensation_enabled(True)
        
        # Save with backup
        saved_path = manager.save_config(backup=True)
        
        assert saved_path.exists()
        
        # Check backup was created
        backup_dir = test_project_path / "backups"
        assert backup_dir.exists()
        
        backups = list(backup_dir.glob("config_backup_*.json"))
        assert len(backups) == 1
    
    def test_restore_original(self, test_project_path):
        """Test restoring original configuration."""
        manager = ConfigManager(test_project_path)
        manager.load_config()
        
        # Get original state
        original_enabled = manager.get_bias_compensation_config()["enabled"]
        
        # Modify
        manager.set_bias_compensation_enabled(not original_enabled)
        assert manager.get_bias_compensation_config()["enabled"] != original_enabled
        
        # Restore
        manager.restore_original()
        assert manager.get_bias_compensation_config()["enabled"] == original_enabled
    
    def test_validate_config(self, test_project_path):
        """Test configuration validation."""
        manager = ConfigManager(test_project_path)
        manager.load_config()
        
        # Should be valid
        assert manager.validate_config() is True
        
        # Remove required key
        del manager.config["use_model"]
        assert manager.validate_config() is False
    
    def test_load_real_compensation_configs(self):
        """Test loading real compensation configurations from test resources."""
        test_resources = Path(__file__).parent.parent / "test_resources" / "config_samples"
        
        # Test each sample config
        configs = ["config_baseline.json", "config_layer1.json", 
                   "config_layer12.json", "config_layer123.json"]
        
        expected_layers = [0, 1, 2, 4]  # Number of compensated layers (layer123 includes output)
        
        for config_file, expected_count in zip(configs, expected_layers):
            # Create temp project with this config
            with tempfile.TemporaryDirectory() as tmpdir:
                project_path = Path(tmpdir)
                shutil.copy(test_resources / config_file, project_path / "config.json")
                
                manager = ConfigManager(project_path)
                manager.load_config()
                
                bias_config = manager.get_bias_compensation_config()
                actual_count = len(bias_config["layer_bias_adjustments"])
                
                assert actual_count == expected_count, (
                    f"Config {config_file} should have {expected_count} "
                    f"compensated layers, found {actual_count}"
                )