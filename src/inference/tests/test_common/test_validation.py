"""
Tests for validation utilities.
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile
import json

from inference.common.validation import (
    ValidationError,
    validate_input,
    validate_backend,
    validate_project_path,
    validate_layer_index,
    validate_inference_result
)


class TestValidateInput:
    """Test input validation functions"""
    
    def test_valid_numpy_array(self):
        """Test validation of valid numpy array"""
        data = np.array([1, 2, 3])
        # Should not raise
        validate_input(data, np.ndarray)
    
    def test_wrong_type(self):
        """Test validation fails for wrong type"""
        data = [1, 2, 3]  # list, not ndarray
        
        with pytest.raises(ValidationError, match="must be ndarray"):
            validate_input(data, np.ndarray)
    
    def test_shape_validation(self):
        """Test shape validation"""
        data = np.array([[1, 2], [3, 4]])
        
        # Correct shape - should not raise
        validate_input(data, np.ndarray, expected_shape=(2, 2))
        
        # Wrong shape - should raise
        with pytest.raises(ValidationError, match="shape mismatch"):
            validate_input(data, np.ndarray, expected_shape=(3, 3))
    
    def test_range_validation(self):
        """Test value range validation"""
        data = np.array([0.1, 0.5, 0.9])
        
        # Within range - should not raise
        validate_input(data, np.ndarray, expected_range=(0.0, 1.0))
        
        # Out of range - should raise
        with pytest.raises(ValidationError, match="values out of range"):
            validate_input(data, np.ndarray, expected_range=(0.2, 0.8))


class TestValidateBackend:
    """Test backend validation"""
    
    def test_valid_backends(self):
        """Test all valid backends"""
        valid_backends = ['nn', 'spice', 'numpy', 'timeseries', 'batch', 'layer']
        
        for backend in valid_backends:
            # Should not raise
            validate_backend(backend)
    
    def test_invalid_backend(self):
        """Test invalid backend name"""
        with pytest.raises(ValidationError, match="Invalid backend"):
            validate_backend('invalid_backend')
    
    def test_wavenet5_spice_validation(self):
        """Test WaveNet5 specific SPICE validation"""
        # Create mock result with execution_time
        class MockResult:
            backend_type = 'spice'
            execution_time = 1.0
            output = np.array([1, 2, 3])
            metadata = {'phase_correction_applied': True}

        result = MockResult()
        # Should not raise
        validate_backend('spice', 'WaveNet5', result)

        # Wrong backend type
        result.backend_type = 'nn'
        with pytest.raises(ValidationError, match="claims to be from"):
            validate_backend('spice', 'WaveNet5', result)


class TestValidateProjectPath:
    """Test project path validation"""
    
    def test_valid_project_path(self):
        """Test validation of valid project path"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            # Create required config.json
            config_file = project_path / "config.json"
            config_file.write_text('{"test": true}')
            
            # Should not raise and return Path object
            validated = validate_project_path(project_path)
            assert isinstance(validated, Path)
            assert validated == project_path
    
    def test_nonexistent_path(self):
        """Test validation fails for nonexistent path"""
        nonexistent = "Z:/nonexistent/path/that/does/not/exist"  # Use a path that's unlikely to exist
        try:
            validate_project_path(nonexistent)
            pytest.fail("Expected ValidationError or OSError")
        except (ValidationError, OSError):
            pass  # Expected
    
    def test_file_instead_of_directory(self):
        """Test validation fails for file instead of directory"""
        with tempfile.NamedTemporaryFile() as tmpfile:
            with pytest.raises(ValidationError, match="not a directory"):
                validate_project_path(tmpfile.name)
    
    def test_missing_config_json(self):
        """Test validation fails when config.json is missing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValidationError, match="missing config.json"):
                validate_project_path(tmpdir)


class TestValidateLayerIndex:
    """Test layer index validation"""
    
    def test_valid_layer_index(self):
        """Test valid layer indices"""
        # Should not raise
        validate_layer_index(1, 'WaveNet5')
        validate_layer_index(5, 'WaveNet5')
        validate_layer_index(3, 'Generic', total_layers=5)
    
    def test_invalid_layer_index(self):
        """Test invalid layer indices"""
        # Less than 1
        with pytest.raises(ValidationError, match="must be >= 1"):
            validate_layer_index(0, 'WaveNet5')
        
        # Exceeds WaveNet5 layers
        with pytest.raises(ValidationError, match="only has 5 layers"):
            validate_layer_index(6, 'WaveNet5')
        
        # Exceeds total layers
        with pytest.raises(ValidationError, match="exceeds total layers"):
            validate_layer_index(10, 'Generic', total_layers=8)


class TestValidateInferenceResult:
    """Test inference result validation"""
    
    def test_valid_result(self):
        """Test validation of valid result"""
        class MockResult:
            backend_type = 'nn'
            execution_time = 1.23
            output_wave = np.array([1, 2, 3])
        
        result = MockResult()
        # Should not raise
        validate_inference_result(result, 'nn')
    
    def test_missing_attributes(self):
        """Test validation fails for missing attributes"""
        class IncompleteResult:
            backend_type = 'nn'
            # Missing execution_time
        
        result = IncompleteResult()
        with pytest.raises(ValidationError, match="missing required attribute"):
            validate_inference_result(result, 'nn')
    
    def test_backend_mismatch(self):
        """Test validation fails for backend mismatch"""
        class MockResult:
            backend_type = 'nn'
            execution_time = 1.23
            output = np.array([1, 2, 3])
        
        result = MockResult()
        with pytest.raises(ValidationError, match="Backend mismatch"):
            validate_inference_result(result, 'spice')
    
    def test_null_output(self):
        """Test validation fails for null output"""
        class MockResult:
            backend_type = 'nn'
            execution_time = 1.23
            output_wave = None

        result = MockResult()
        with pytest.raises(ValidationError, match="null output_wave"):
            validate_inference_result(result, 'nn')


class TestValidateWavenet5SpiceResult:
    """Test WaveNet5 SPICE result validation"""

    def test_valid_spice_result(self):
        """Test valid WaveNet5 SPICE result"""
        from inference.common.validation import validate_wavenet5_spice_result

        class MockResult:
            backend_type = 'spice'
            metadata = {'phase_correction_applied': True}

        result = MockResult()
        # Should not raise
        validate_wavenet5_spice_result(result)

    def test_missing_backend_type(self):
        """Test validation fails for missing backend_type"""
        from inference.common.validation import validate_wavenet5_spice_result

        class MockResult:
            metadata = {'phase_correction_applied': True}

        result = MockResult()
        with pytest.raises(ValidationError, match="missing 'backend_type'"):
            validate_wavenet5_spice_result(result)

    def test_backend_type_mismatch(self):
        """Test validation fails for backend_type mismatch"""
        from inference.common.validation import validate_wavenet5_spice_result

        class MockResult:
            backend_type = 'nn'  # Wrong type
            metadata = {'phase_correction_applied': True}

        result = MockResult()
        with pytest.raises(ValidationError, match="was processed as 'spice'"):
            validate_wavenet5_spice_result(result)


class TestValidationEdgeCases:
    """Test edge cases in validation"""

    def test_validate_input_with_list_conversion(self):
        """Test validate_input converts list to array for validation"""
        # List that can be converted to array
        data = [[1, 2], [3, 4]]
        # Should not raise when expected_type allows conversion
        validate_input(np.array(data), np.ndarray, expected_shape=(2, 2))

    def test_validate_input_empty_range(self):
        """Test validation with edge case ranges"""
        data = np.array([0.0, 0.0, 0.0])
        # Range that exactly matches
        validate_input(data, np.ndarray, expected_range=(0.0, 0.0))

    def test_validate_input_negative_values(self):
        """Test validation with negative values"""
        data = np.array([-1.0, 0.0, 1.0])
        validate_input(data, np.ndarray, expected_range=(-2.0, 2.0))

        # Should fail when out of range
        with pytest.raises(ValidationError, match="values out of range"):
            validate_input(data, np.ndarray, expected_range=(0.0, 1.0))

    def test_validate_layer_index_wavenet5_boundary(self):
        """Test WaveNet5 layer index boundary cases"""
        # Valid boundaries
        validate_layer_index(1, 'WaveNet5')  # Minimum
        validate_layer_index(5, 'WaveNet5')  # Maximum

        # Invalid - just over boundary
        with pytest.raises(ValidationError, match="only has 5 layers"):
            validate_layer_index(6, 'WaveNet5')

    def test_validate_layer_index_generic_model(self):
        """Test generic model layer validation"""
        # With total_layers constraint
        validate_layer_index(3, 'GenericModel', total_layers=5)

        # Exceeds total_layers
        with pytest.raises(ValidationError, match="exceeds total layers 5"):
            validate_layer_index(6, 'GenericModel', total_layers=5)

    def test_validate_backend_with_result_no_model(self):
        """Test backend validation with result but no model type"""
        from inference.common.validation import validate_backend

        class MockResult:
            backend_type = 'spice'
            execution_time = 1.0
            output = np.array([1, 2, 3])
            metadata = {}

        result = MockResult()
        # Should not raise (model is optional)
        validate_backend('spice', inference_result=result)

    def test_validate_backend_result_with_output(self):
        """Test backend validation when result has output attribute"""
        from inference.common.validation import validate_backend

        class MockResult:
            backend_type = 'nn'
            execution_time = 1.0
            output = np.array([1, 2, 3])

        result = MockResult()
        validate_backend('nn', inference_result=result)