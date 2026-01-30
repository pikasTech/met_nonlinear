"""
Pytest Configuration - Root Level

Provides shared fixtures and configurations for all tests.
"""

import pytest
import sys
import os
import time
import signal
from pathlib import Path
from typing import Optional

# Get project root
_PROJECT_ROOT = Path(__file__).parent.absolute()

# Add src to path
_SRC_DIR = _PROJECT_ROOT / 'src'
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))


# ============================================================================
# Timeout and Progress Monitoring
# ============================================================================

class ProgressMonitor:
    """Monitor test progress and detect stuck tests."""

    def __init__(self, timeout_seconds: int = 60):
        self.timeout_seconds = timeout_seconds
        self.last_output_time = time.time()
        self.test_count = 0

    def record_progress(self):
        """Record test progress (call after each test completes)."""
        self.last_output_time = time.time()
        self.test_count += 1

    def is_stuck(self) -> bool:
        """Check if tests appear to be stuck (no output for timeout period)."""
        return (time.time() - self.last_output_time) > self.timeout_seconds

    def get_elapsed(self) -> float:
        """Get seconds since last output."""
        return time.time() - self.last_output_time


# Global monitor instance
_progress_monitor: Optional[ProgressMonitor] = None


def _get_monitor() -> ProgressMonitor:
    """Get or create the global progress monitor."""
    global _progress_monitor
    if _progress_monitor is None:
        _progress_monitor = ProgressMonitor()
    return _progress_monitor


@pytest.fixture(scope="session")
def progress_monitor():
    """Session-scoped progress monitor fixture."""
    return _get_monitor()


@pytest.fixture
def track_progress(progress_monitor):
    """Fixture to track individual test progress."""
    class ProgressTracker:
        def __init__(self, monitor: ProgressMonitor):
            self.monitor = monitor
            self.start_time = time.time()

        def check_stuck(self) -> bool:
            """Check if tests have been stuck."""
            return self.monitor.is_stuck()

        def get_elapsed(self) -> float:
            """Get elapsed time since tracker creation."""
            return time.time() - self.start_time

    tracker = ProgressTracker(_get_monitor())
    yield tracker
    # Record progress when test completes
    _get_monitor().record_progress()


# ============================================================================
# Standard Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def project_root():
    """Return the project root directory."""
    return _PROJECT_ROOT


@pytest.fixture(scope="session")
def src_dir():
    """Return the src directory."""
    return _SRC_DIR


@pytest.fixture(scope="session")
def tests_dir():
    """Return the tests directory."""
    tests_path = _PROJECT_ROOT / 'src' / 'tests'
    return tests_path if tests_path.exists() else _PROJECT_ROOT / 'tests'


@pytest.fixture
def temp_dir(tmp_path):
    """Provide a temporary directory for tests."""
    return tmp_path


@pytest.fixture
def sample_data():
    """Provide sample test data."""
    return {
        'float_array': [0.1, 0.2, 0.3, 0.4, 0.5],
        'int_array': [1, 2, 3, 4, 5],
        'string_data': 'test_string',
        'nested': {'key': 'value', 'number': 42}
    }


# ============================================================================
# Pytest Hooks
# ============================================================================

def pytest_configure(config):
    """Configure pytest with progress monitoring."""
    # Register custom markers
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "requires_gpu: marks tests requiring GPU"
    )
    config.addinivalue_line(
        "markers", "integration: marks integration tests"
    )

    # Configure coverage for calibration_analyzer module
    # This ensures coverage can track modules imported via sys.path modification
    config.addinivalue_line(
        "addopts",
        f"--cov=src.calibration_analyzer --cov-report=term-missing --cov-report=html "
        f"--cov-config={_SRC_DIR / 'tests' / 'calibration_analyzer' / '.coveragerc'}"
    )


def pytest_sessionstart(session):
    """Called after the Session object has been created and before tests run."""
    monitor = _get_monitor()
    print(f"\n{'='*60}")
    print(f"Test Session Started")
    print(f"  Progress monitor: {monitor.timeout_seconds}s timeout for no output")
    print(f"  Test paths: {session.config.getoption('testpaths', default=[])}")
    print(f"{'='*60}\n")
    session.config._progress_monitor = monitor


def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished, right before returning the exit status."""
    monitor = getattr(session.config, '_progress_monitor', None)
    if monitor:
        print(f"\n{'='*60}")
        print(f"Test Session Finished")
        print(f"  Total tests tracked: {monitor.test_count}")
        print(f"  Exit status: {exitstatus}")
        print(f"{'='*60}\n")


def pytest_runtest_setup(item):
    """Called before running each test."""
    pass


def pytest_runtest_teardown(item, nextitem):
    """Called after running each test."""
    # Record progress after each test
    monitor = getattr(item.config, '_progress_monitor', None)
    if monitor:
        monitor.record_progress()


def pytest_deselected(items):
    """Called when test items are deselected (e.g., with -k)."""
    pass


# ============================================================================
# Timeout Plugin Configuration
# ============================================================================

def pytest_addoption(parser):
    """Add custom command line options."""
    # Note: --timeout is provided by pytest-timeout plugin
    # Note: --workers is provided by pytest-xdist plugin
    parser.addoption(
        "--progress-timeout",
        type=int,
        default=60,
        help="Timeout in seconds for no console output (default: 60)"
    )
    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="Run slow tests"
    )
    parser.addoption(
        "--quick",
        action="store_true",
        default=False,
        help="Quick mode: skip slow tests and reduce output"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on options."""
    quick_mode = config.getoption("--quick", default=False)
    run_slow = config.getoption("--run-slow", default=False)

    if quick_mode and not run_slow:
        skip_slow = pytest.mark.skip(reason="Skipped in quick mode")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)


# ============================================================================
# Error Handling
# ============================================================================

def pytest_runtest_makereport(item, call):
    """Customize test report generation."""
    if call.excinfo is not None:
        # Test failed or errored
        excinfo = call.excinfo
        if excinfo.type == TimeoutError:
            # Add custom handling for timeout
            print(f"\n[TIMEOUT] Test {item.name} timed out!")


# ============================================================================
# Utility Functions
# ============================================================================

def get_test_paths() -> list:
    """Get list of test directories."""
    test_paths = []
    for pattern in ['src/tests', 'src/*/tests', 'tests']:
        path = _PROJECT_ROOT / pattern.replace('/', os.sep)
        if path.exists():
            test_paths.append(str(path))
    return test_paths


def count_tests() -> int:
    """Count total number of tests in the project."""
    count = 0
    for pattern in ['**/test_*.py', '**/*_test.py']:
        for _ in (_PROJECT_ROOT / 'src').rglob(pattern):
            count += 1
    return count
