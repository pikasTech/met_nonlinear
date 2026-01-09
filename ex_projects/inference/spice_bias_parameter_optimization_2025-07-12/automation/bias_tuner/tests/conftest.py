"""Pytest configuration and shared fixtures."""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture(autouse=True)
def cleanup_mock_mode():
    """Ensure mock mode is disabled after each test."""
    yield
    
    # Import here to avoid circular imports
    from bias_tuner.core import set_mock_mode, is_mock_mode
    
    if is_mock_mode():
        set_mock_mode(False)


@pytest.fixture
def test_resources_path():
    """Path to test resources directory."""
    return Path(__file__).parent.parent / "test_resources"


# Configure pytest to show more details
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )