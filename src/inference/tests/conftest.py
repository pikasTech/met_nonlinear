"""
Pytest configuration for inference module tests.

This file provides shared fixtures and configurations for all inference tests.
"""

import pytest
import json
from pathlib import Path
import numpy as np


@pytest.fixture(scope="session")
def test_data_dir():
    """Return the path to test data directory."""
    return Path(__file__).parent / "test_data"


@pytest.fixture(scope="session")
def golden_data_dir():
    """Return the path to golden data directory."""
    return Path(__file__).parent / "golden_data"


@pytest.fixture
def sample_wave_data():
    """Generate sample wave data for testing."""
    return np.random.randn(1000, 1)


@pytest.fixture
def sample_model_config():
    """Provide sample model configuration."""
    return {
        "use_model": "WaveNet5",
        "dataset_type": "AliasSimu",
        "model_subcfg": {
            "init_center_freqs": [10, 30, 60, 100],
            "init_quality_factors": [1.0, 1.5, 2.0, 2.5]
        }
    }


class GoldenMasterTest:
    """Base class for golden master testing."""
    
    @pytest.fixture(scope="class")
    def golden_data(self, golden_data_dir):
        """Load golden standard data."""
        golden_path = golden_data_dir / "inference_results.json"
        if not golden_path.exists():
            pytest.skip("Golden data not available. Run generate_golden_data.py first.")
        
        with open(golden_path) as f:
            return json.load(f)
    
    def assert_results_match(self, actual, expected, tolerance=1e-6):
        """Assert that actual results match expected with given tolerance."""
        import numpy as np
        
        # Check shape
        assert actual.shape == tuple(expected['output_shape'])
        
        # Check statistics
        np.testing.assert_allclose(
            np.min(actual), expected['output_min'], 
            rtol=tolerance
        )
        np.testing.assert_allclose(
            np.max(actual), expected['output_max'], 
            rtol=tolerance
        )
        np.testing.assert_allclose(
            np.mean(actual), expected['output_mean'], 
            rtol=tolerance
        )
        
        # Check sample values if available
        if 'output_samples' in expected:
            actual_samples = actual.flatten()[:10].tolist()
            expected_samples = expected['output_samples']
            np.testing.assert_allclose(
                actual_samples, expected_samples, 
                rtol=tolerance
            )


# Pytest configuration options
def pytest_addoption(parser):
    """Add custom command line options."""
    # Note: --run-slow is already defined in root conftest.py
    # Only add options that are not already defined
    try:
        parser.addoption(
            "--benchmark-save",
            action="store",
            default=None,
            help="Save benchmark results with given name"
        )
    except ValueError:
        # Option already exists, skip
        pass


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on markers."""
    if not config.getoption("--run-slow"):
        skip_slow = pytest.mark.skip(reason="Need --run-slow option to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)