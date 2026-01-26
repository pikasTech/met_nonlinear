# Calibration Analyzer Documentation

## Overview
The Calibration Analyzer module provides comprehensive tools for analyzing and adjusting electrochemical sensor calibration data. It includes data parsing, visualization, curve fitting, and parameter adjustment capabilities.

## Quick Start
- [User Guide](user_guide/adjuster_documentation.md) - Complete user manual for the calibration adjuster
- [Installation](user_guide/installation.md) - Setup instructions
- [API Reference](api_reference/README.md) - Programming interface documentation

## Key Features
- **Data Import**: Support for various data formats (Excel, JSON, CSV)
- **Curve Fitting**: Advanced curve fitting algorithms for calibration data
- **Visualization**: Interactive plots and data visualization tools
- **Parameter Adjustment**: Real-time parameter tuning and optimization
- **Export Functions**: Multiple output formats for analysis results

## User Guide
- [Adjuster Documentation](user_guide/adjuster_documentation.md) - Main user guide
- [Data Import Guide](user_guide/data_import.md) - How to import your data
- [Curve Fitting Guide](user_guide/curve_fitting.md) - Fitting procedures
- [Visualization Guide](user_guide/visualization.md) - Creating plots and charts

## API Reference
- [Core Classes](api_reference/core_classes.md) - Main analyzer classes
- [Data Structures](api_reference/data_structures.md) - Data format specifications
- [Utilities](api_reference/utilities.md) - Helper functions
- [Widgets](api_reference/widgets.md) - GUI component reference

## Troubleshooting
- [Common Issues](troubleshooting/common_issues.md) - Frequent problems and solutions
- [Error Messages](troubleshooting/error_messages.md) - Error code explanations
- [Performance Tips](troubleshooting/performance.md) - Optimization recommendations

## Core Components
- `analyzer.py` - Main analysis engine
- `adjuster.py` - Parameter adjustment interface
- `dataparser.py` - Data import and parsing
- `transfer_fit.py` - Transfer function fitting
- `waveviewer.py` - Waveform visualization
- `adjuster_widgets.py` - GUI components

## Data Formats
- **Input**: Excel (.xlsx), JSON, CSV
- **Output**: Analysis reports, fitted parameters, visualization files
- **Configuration**: JSON-based settings files

## Related Modules
- [Core Training](../../core/doc/README.md) - Neural network training
- [Analysis Tools](../../analysis/doc/README.md) - Advanced analysis capabilities
- [SPICE Simulator](../../spice_simulator/doc/README.md) - Circuit simulation

## Support
For technical support and questions, please refer to the troubleshooting section or consult the main project documentation.

---
*Last updated: 2025-01-08*