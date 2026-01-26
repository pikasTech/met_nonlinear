# Testing Framework Documentation

## Overview
The Testing Framework provides comprehensive testing capabilities for all modules in the electrochemical nonlinear correction project. This includes unit tests, integration tests, coverage analysis, and build verification testing.

## Quick Start
- [Framework Guide](framework/README.md) - Testing framework overview
- [Testing Guidelines](guidelines/README.md) - Best practices and standards
- [Test Reports](reports/README.md) - Historical test results and analysis

## Testing Infrastructure
- **Pytest Framework**: Main testing framework with coverage support
- **Run Tests Script**: `run_tests.py` for executing test suites
- **Coverage Analysis**: Comprehensive code coverage reporting
- **Continuous Integration**: Automated testing workflows

## Framework Components
- [Test Runner](framework/test_runner.md) - Main test execution system
- [Coverage Analysis](framework/coverage.md) - Code coverage tools
- [Test Configuration](framework/configuration.md) - Testing configuration
- [Fixtures and Utilities](framework/fixtures.md) - Common test utilities

## Testing Guidelines
- [Unit Testing](guidelines/unit_testing.md) - Unit test best practices
- [Integration Testing](guidelines/integration_testing.md) - Integration test guidelines
- [Test Organization](guidelines/organization.md) - Test structure and naming
- [Mocking and Fixtures](guidelines/mocking.md) - Mocking strategies

## Test Reports
- [Build Tests](reports/build_test.md) - Build verification results
- [Build Test 2](reports/build_test2.md) - Extended build testing
- [Build Test 3](reports/build_test3.md) - Additional build verification
- [Build Test 4](reports/build_test4.md) - Latest build test results
- [Test Build 5](reports/test_build5.md) - Comprehensive build testing
- [Test Fix 1](reports/test_fix1.md) - Bug fix verification
- [SPICE Test Fix](reports/test_fix_spice.md) - SPICE-related test fixes

## Test Categories

### Unit Tests
- **Model Tests**: Individual model component testing
- **Data Processing**: Dataset and preprocessing tests
- **Utility Functions**: Helper function verification
- **Configuration**: Config system testing

### Integration Tests
- **Pipeline Tests**: End-to-end workflow testing
- **Module Integration**: Cross-module interaction tests
- **API Testing**: Interface compatibility tests
- **Performance Tests**: Speed and memory benchmarks

### System Tests
- **Build Verification**: Complete system build tests
- **Regression Tests**: Preventing functionality regression
- **Compatibility Tests**: Cross-platform compatibility
- **Stress Tests**: System limits and stability

## Running Tests

### Complete Test Suite
```bash
python run_tests.py
```

### Specific Test Categories
```bash
# Run tests for specific directory
python run_tests.py spice_simulator/tests
python run_tests.py tests/calibration_analyzer

# Run with coverage report
python run_tests.py --coverage

# Run specific test pattern
python run_tests.py -k test_kan
```

### Alternative: Direct Pytest
```bash
# Verbose output
pytest -v

# Specific test file
pytest tests/test_cli.py::test_specific_function

# Coverage report
pytest --cov=./ --cov-report=html
```

## Test Configuration
- `pytest.ini` - Main pytest configuration
- `.coveragerc` - Coverage analysis settings
- `run_tests.py` - Custom test runner
- `conftest.py` - Pytest fixtures and configuration

## Module-Specific Testing

### Analysis Module Tests
- Parameter efficiency analysis verification
- Visualization output validation
- Algorithm correctness testing

### Calibration Analyzer Tests
- Data parsing accuracy
- Curve fitting algorithm validation
- GUI component testing

### SPICE Simulator Tests
- Circuit generation verification
- Simulation accuracy testing
- NGspice integration testing

### Core Training Tests
- Model training functionality
- Configuration system testing
- GPU/CPU compatibility testing

### Inference Tests
- Model loading and inference
- Backend compatibility testing
- Performance benchmarking

## Coverage Analysis
- **Target Coverage**: 80% minimum for all modules
- **Coverage Reports**: Generated in `tests/coverage_reports/`
- **Exclusions**: Configuration files and external libraries
- **CI Integration**: Automated coverage tracking

## Continuous Integration
- **Pre-commit Hooks**: Automated testing before commits
- **GitHub Actions**: Automated testing on push/PR
- **Build Verification**: Automated build testing
- **Regression Detection**: Automatic regression testing

## Test Data Management
- **Test Datasets**: Standardized test data in `tests/testcase/`
- **Mock Data**: Generated test data for unit tests
- **Fixtures**: Reusable test configurations
- **Cleanup**: Automatic test artifact cleanup

## Performance Testing
- **Benchmarking**: Performance regression detection
- **Memory Testing**: Memory leak detection
- **Stress Testing**: System limit validation
- **Profiling**: Performance bottleneck identification

## Troubleshooting
- [Common Issues](troubleshooting/common_issues.md) - Frequent test failures
- [Environment Setup](troubleshooting/environment.md) - Test environment issues
- [Debug Tools](troubleshooting/debugging.md) - Test debugging techniques

## Related Modules
- All project modules have associated test suites
- [Development Documentation](../../core/doc/README.md) - Development guidelines
- [Project Documentation](../../doc/project/README.md) - Project management

---
*Last updated: 2025-01-08*