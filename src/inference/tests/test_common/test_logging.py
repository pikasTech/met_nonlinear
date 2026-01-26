"""
Tests for logging utilities.
"""

import pytest
import logging
from pathlib import Path
import tempfile
from io import StringIO

from inference.common.logging import InferenceLogger, get_logger


class TestInferenceLogger:
    """Test InferenceLogger functionality"""
    
    def test_logger_creation(self):
        """Test creating a logger"""
        logger = InferenceLogger("test_module")
        assert logger.name == "test_module"
        assert isinstance(logger.logger, logging.Logger)
    
    def test_singleton_behavior(self):
        """Test that same name returns same logger"""
        logger1 = InferenceLogger("same_name")
        logger2 = InferenceLogger("same_name")
        
        # Should be the same underlying logger
        assert logger1.logger is logger2.logger
    
    def test_log_levels(self, caplog):
        """Test different log levels"""
        logger = InferenceLogger("test_levels", logging.DEBUG)
        
        with caplog.at_level(logging.DEBUG):
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")
        
        assert "Debug message" in caplog.text
        assert "Info message" in caplog.text
        assert "Warning message" in caplog.text
        assert "Error message" in caplog.text
    
    def test_log_inference_start(self, caplog):
        """Test logging inference start"""
        logger = InferenceLogger("test_inference")
        
        with caplog.at_level(logging.INFO):
            logger.log_inference_start("spice", "WaveNet5", "test_project")
        
        assert "Starting spice inference for WaveNet5" in caplog.text
        assert "project: test_project" in caplog.text
    
    def test_log_inference_complete(self, caplog):
        """Test logging inference completion"""
        logger = InferenceLogger("test_inference")
        
        with caplog.at_level(logging.INFO):
            logger.log_inference_complete("nn", 1.234, success=True)
            logger.log_inference_complete("spice", 5.678, success=False)
        
        assert "nn inference completed in 1.234 seconds" in caplog.text
        assert "spice inference failed in 5.678 seconds" in caplog.text
    
    def test_log_layer_processing(self, caplog):
        """Test logging layer processing"""
        logger = InferenceLogger("test_layers", logging.DEBUG)
        
        with caplog.at_level(logging.DEBUG):
            logger.log_layer_processing(
                layer_index=2,
                layer_type="Dense",
                input_shape=(10, 6),
                output_shape=(10, 8)
            )
        
        assert "Processing layer 2 (Dense)" in caplog.text
        assert "input (10, 6) -> output (10, 8)" in caplog.text
    
    def test_log_data_range(self, caplog):
        """Test logging data range"""
        logger = InferenceLogger("test_range")
        
        with caplog.at_level(logging.INFO):
            logger.log_data_range("Test Data", -1.5, 2.5, mean_val=0.5)
        
        assert "Test Data range: [-1.500000, 2.500000]" in caplog.text
        assert "mean: 0.500000" in caplog.text
    
    def test_log_phase_correction(self, caplog):
        """Test logging phase correction"""
        logger = InferenceLogger("test_phase")
        
        with caplog.at_level(logging.INFO):
            logger.log_phase_correction(
                layer_index=3,
                before_range=(-1.2, 0.8),
                after_range=(0.2, 1.8)
            )
        
        assert "Layer 3 phase correction" in caplog.text
        assert "[-1.200000, 0.800000] -> [0.200000, 1.800000]" in caplog.text
    
    def test_file_logger(self):
        """Test creating file logger"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as tmp:
            log_file = Path(tmp.name)
        
        try:
            logger = InferenceLogger.create_file_logger(
                "test_file",
                log_file,
                logging.INFO
            )
            
            logger.info("Test message to file")
            
            # Check file contents
            content = log_file.read_text()
            assert "Test message to file" in content
            assert "test_file" in content
            
        finally:
            # Cleanup
            if log_file.exists():
                log_file.unlink()
    
    def test_global_logger(self):
        """Test global logger access"""
        logger1 = get_logger()
        logger2 = get_logger()
        
        # Should be the same instance
        assert logger1 is logger2
        assert logger1.name == "inference"


class TestLoggerIntegration:
    """Test logger integration scenarios"""
    
    def test_backend_switch_logging(self, caplog):
        """Test logging backend switches"""
        logger = InferenceLogger("backend_test")
        
        with caplog.at_level(logging.INFO):
            logger.log_backend_switch("nn", "spice")
        
        assert "Switching backend: nn -> spice" in caplog.text
    
    def test_validation_error_logging(self, caplog):
        """Test logging validation errors"""
        logger = InferenceLogger("validation_test")
        
        error = ValueError("Invalid input shape")
        
        with caplog.at_level(logging.ERROR):
            logger.log_validation_error(error)
        
        assert "Validation error: Invalid input shape" in caplog.text
    
    def test_complete_inference_flow_logging(self, caplog):
        """Test logging a complete inference flow"""
        logger = InferenceLogger("flow_test")
        
        with caplog.at_level(logging.INFO):
            # Start inference
            logger.log_inference_start("nn", "WaveNet5")
            
            # Log some data ranges
            logger.log_data_range("Input", 0.0, 1.0)
            
            # Log layer processing (debug level, won't show)
            logger.log_layer_processing(1, "SVF", (100, 1), (100, 6))
            
            # Complete inference
            logger.log_inference_complete("nn", 0.456)
        
        log_text = caplog.text
        assert "Starting nn inference" in log_text
        assert "Input range" in log_text
        assert "nn inference completed" in log_text
        # Debug message should not appear at INFO level
        assert "Processing layer" not in log_text