# SPICE Simulator Documentation

## Overview
The SPICE Simulator module provides comprehensive circuit simulation capabilities for neural network layer implementations. It enables conversion of trained neural network layers into analog circuit equivalents using SPICE netlists for hardware verification and analysis.

## Quick Start
- [User Guide](user_guide/README.md) - Main user manual
- [Installation](user_guide/installation.md) - Linux setup guide  
- [Developer Guide](developer_guide/CLAUDE.md) - Development documentation
- [Circuit Design](circuit_design/README.md) - Circuit design principles

## Key Features
- **Layer Conversion**: Convert neural network layers to SPICE circuits
- **Multiple Architectures**: Support for Dense, SVF, ReLU, and other layer types
- **NGspice Integration**: Full NGspice simulation engine support
- **Bias Error Testing**: Comprehensive bias error analysis tools
- **Circuit Analysis**: Advanced circuit analysis and optimization

## User Guide
- [Main Guide](user_guide/README.md) - Complete user manual
- [Installation](user_guide/installation.md) - Setup and configuration
- [Basic Usage](user_guide/basic_usage.md) - Getting started
- [Circuit Types](user_guide/circuit_types.md) - Available circuit implementations

## Developer Guide
- [Development Guide](developer_guide/CLAUDE.md) - Core development documentation
- [Architecture](developer_guide/architecture.md) - System architecture
- [API Reference](developer_guide/api_reference.md) - Programming interface
- [Testing](developer_guide/testing.md) - Testing procedures

## Circuit Design
- [Design Principles](circuit_design/principles.md) - Circuit design fundamentals
- [Op-Amp Models](circuit_design/opamp_models.md) - Operational amplifier implementations
- [Activation Functions](circuit_design/activation_functions.md) - ReLU, tanh implementations
- [Bias Compensation](circuit_design/bias_compensation.md) - Bias error correction

## Circuit Types
- **Dense Layers**: Fully connected layer implementations
- **SVF Circuits**: State Variable Filter implementations  
- **ReLU Circuits**: Rectified Linear Unit activation
- **RC Circuits**: Resistor-capacitor filter networks
- **Tanh Models**: Hyperbolic tangent activation functions

## Tools and Utilities
- `simulation.py` - Main simulation engine
- `bias_error_tester.py` - Bias error analysis
- `circuit_base.py` - Base circuit classes
- `opamp_models.py` - Op-amp model library
- `spicelib/` - SPICE utilities and helpers

## Circuit Analysis
- [Sweep Analysis](circuit_analysis/simu_sweep.py) - Parameter sweep analysis
- [SVF Analysis](circuit_analysis/simu_svf_sweep.py) - SVF-specific analysis
- [Bias Feasibility](circuit_analysis/analyze_tanh_bias_feasibility.py) - Bias analysis

## Integration Points
- **NGspice**: Native NGspice simulation support
- **SpiceLib**: Advanced SPICE utilities
- **Matplotlib**: Visualization with Chinese font support
- **NumPy/SciPy**: Numerical analysis backend

## Example Workflows
1. **Neural Layer to Circuit**: Convert trained layer → Generate SPICE netlist → Simulate
2. **Bias Analysis**: Load circuit → Run bias tests → Analyze results
3. **Parameter Optimization**: Define sweep ranges → Run simulations → Optimize parameters

## File Structure
```
spice_simulator/
├── circuit_*.py          # Circuit implementation classes
├── simulation.py          # Main simulation engine
├── bias_error_tester.py   # Bias testing utilities
├── spicelib/             # SPICE utility library
├── circuit_analysis/     # Analysis tools
├── spice_models/         # Op-amp and device models
└── tests/               # Unit tests
```

## Related Modules
- [Inference Engine](../../inference/doc/README.md) - Neural network inference
- [Core Training](../../core/doc/README.md) - Model training
- [Analysis Tools](../../analysis/doc/README.md) - Advanced analysis

## Support and Troubleshooting
For technical support, refer to the troubleshooting section in the user guide or consult the main project documentation.

---
*Last updated: 2025-01-08*