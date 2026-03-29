# AGENTS.md - Agentic Coding Guidelines

## Project Overview

This is a Python project for **MET Nonlinear** - Wiener-KAN neural networks for frequency response drift compensation. Core modules include `models/`, `tfkan/`, `analysis/`, `visualization/`, and `calibration_analyzer/`.

---

## Build, Lint, and Test Commands

### Running Tests

```bash
# Run all tests
pytest

# Run tests in src/tests (default testpaths)
pytest src/tests

# Run a specific test file
pytest src/analysis/tests/test_analysis_comprehensive.py

# Run a specific test class
pytest src/analysis/tests/test_analysis_comprehensive.py::TestAliasSuppression

# Run a specific test function
pytest src/analysis/tests/test_analysis_comprehensive.py::TestAliasSuppression::test_module_import

# Run tests by keyword pattern (-k)
pytest -k "test_module_import"

# Run tests with markers
pytest -m "not slow"              # Skip slow tests
pytest -m "integration"           # Run only integration tests

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run with timeout (single test, default 300s)
pytest --timeout=60

# Quick mode (skip slow tests)
pytest --quick

# Parallel execution (Windows: use --tests-per-worker=1)
pytest --workers=4 --tests-per-worker=1
```

### Virtual Environment

```bash
# Activate conda environment (Windows)
C:\Users\lyon\MiniConda3\condabin\conda.bat run:*
```

---

## Code Style Guidelines

### Formatting

- **Formatter**: `autopep8` (configured in `.vscode/settings.json`)
- **Python Language Server**: Jedi
- **Indentation**: 4 spaces
- **Line Length**: Follow PEP 8 (max 79 characters recommended, autopep8 default)

### Imports

Organize imports in three groups with blank lines between:

```python
# 1. Standard library
import os
import sys
import json
import logging
from typing import Tuple, List, Any, Union, Callable

# 2. Third-party libraries
import tensorflow as tf
import numpy as np
import pytest
from matplotlib import pyplot as plt

# 3. Local project imports
from .ops.spline import calc_spline_values, fit_spline_coef
from ..layers.base import LayerKAN
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Classes | CamelCase | `PiecewiseActivationLayer`, `LayerKAN` |
| Functions/methods | snake_case | `calc_spline_output`, `validate_bias_compensation_config` |
| Variables | snake_case | `spline_kernel`, `layer_idx` |
| Constants | UPPER_SNAKE | `FREQ_LIST`, `GRID_SIZE` |
| Private members | _prefix | `_progress_monitor`, `_src_dir` |
| Type variables | CamelCase | `T`, `AnyStr` |

### Type Annotations

```python
# Use type hints for function signatures
def calc_spline_output_origin(self, inputs: tf.Tensor) -> tf.Tensor:
    pass

def get_layer_bias_adjustment(self, layer_idx: int) -> Optional[List[float]]:
    pass

# For complex types, use typing module
from typing import Tuple, List, Any, Union, Callable, Optional, Dict
```

### Error Handling

```python
# Use specific exception types
raise ValueError("xn and yn must have the same length.")
raise NotImplementedError("Subclasses must implement update_grid_from_samples.")

# Catch and re-raise with context
try:
    config.validate_bias_compensation_config(model=None)
except Exception as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"偏置补偿配置验证警告: {e}")
```

### Docstrings

```python
class PiecewiseActivationLayer(tf.keras.layers.Layer):
    """
    Custom Keras Layer for piecewise activation based on xn and yn.
    
    Args:
        xn (list of float): List of x-coordinates for breakpoints.
        yn (list of float): List of y-coordinates corresponding to xn.
    """

    def call(self, inputs):
        """
        Apply the piecewise linear activation function.
        
        Args:
            x (tf.Tensor): Input tensor.
            
        Returns:
            tf.Tensor: Output tensor with piecewise linear activation applied.
        """
        return self.piecewise_activation(inputs)
```

### Keras/TensorFlow Patterns

```python
# Layer inheritance
class PiecewiseActivationLayer(tf.keras.layers.Layer):
    def __init__(self, xn, yn, **kwargs):
        super(PiecewiseActivationLayer, self).__init__(**kwargs)
    
    def call(self, inputs):
        return self.piecewise_activation(inputs)
    
    def get_config(self):
        config = super().get_config()
        config.update({"xn": self.xn, "yn": self.yn})
        return config
```

---

## Project Structure

```
src/
├── tests/              # Root test directory
├── analysis/           # Analysis module
│   └── tests/         # Analysis tests
├── models/            # Neural network models (FRIKAN, GRN, LSTM, WaveNet, etc.)
├── tfkan/             # TensorFlow KAN implementation
│   ├── layers/        # KAN layer implementations
│   └── ops/           # Spline and grid operations
├── visualization/     # Plotting and visualization
├── calibration_analyzer/  # Calibration analysis tools
├── utils/             # Utility functions
├── logger/            # Logging utilities
└── config.py          # Global configuration
```

---

## Pytest Configuration

Key settings from `pytest.ini`:

- `testpaths = src/tests`
- `python_files = test_*.py *_test.py`
- `python_classes = Test*`
- `python_functions = test_*`
- **Markers**: `slow`, `skip_on_ci`, `requires_gpu`, `integration`
- **Default timeout**: 300 seconds per test

### Test Fixtures (from conftest.py)

```python
@pytest.fixture(scope="session")
def project_root():
    """Return the project root directory."""

@pytest.fixture(scope="session")
def src_dir():
    """Return the src directory."""

@pytest.fixture
def temp_dir(tmp_path):
    """Provide a temporary directory for tests."""

@pytest.fixture
def sample_data():
    """Provide sample test data."""
```

---

## Key Dependencies

```
tensorflow==2.6
keras==2.6
numpy, matplotlib, pandas, scikit-learn
pytest>=7.0.0, pytest-cov, pytest-timeout, pytest-asyncio
```

---

## Common Tasks

### Adding a New Test

1. Create test file in `src/*/tests/test_*.py`
2. Follow naming: `TestClassName` with methods `test_*`
3. Use existing fixtures from `conftest.py`
4. Import modules via absolute import: `from analysis import alias_suppression`

### Adding a New Module

1. Create module in appropriate `src/` subdirectory
2. Add `__init__.py` with public exports
3. Update parent `__init__.py` if needed
4. Add tests in sibling `tests/` directory

### Running Single Test During Development

```bash
# Most reliable pattern - run specific test
pytest src/analysis/tests/test_analysis_comprehensive.py::TestAliasSuppression::test_module_import -v

# Quick verification with minimal output
pytest src/analysis/tests/test_analysis_comprehensive.py::TestAliasSuppression::test_module_import -q
```
