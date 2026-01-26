# Core Training Module Documentation

## Overview
The Core Training module provides the fundamental training infrastructure for electrochemical nonlinear correction models. This module implements the core training algorithms, model architectures, and optimization strategies for various neural network models including LSTM, GRN, FRIKAN, WaveNet, RNN, and Transformer architectures.

## Quick Start
- [Architecture Overview](architecture/test_principles.md) - Core principles and architecture
- [Developer Guide](developer_guide/test_kan_enhance.md) - KAN enhancement development
- [API Reference](api_reference/README.md) - Programming interface
- [Training Scripts](../training.py) - Main training entry point

## Key Features
- **Multi-Architecture Support**: LSTM, GRN, FRIKAN, WaveNet, RNN, Transformer
- **Real-time Monitoring**: Live training progress and callbacks
- **State Management**: Resumable training with state persistence
- **Cosine Annealing**: Advanced learning rate scheduling
- **GPU Acceleration**: Configurable GPU support via metnl.py

## Architecture
- [Core Principles](architecture/test_principles.md) - Fundamental design principles
- [Model Engine](architecture/model_engine.md) - Training orchestration
- [Dataset System](architecture/dataset_system.md) - Data processing pipeline
- [Training Infrastructure](architecture/training_infrastructure.md) - Training framework

## Developer Guide
- [KAN Enhancement](developer_guide/test_kan_enhance.md) - KAN model development
- [Adding New Models](developer_guide/new_models.md) - Model development guide
- [Configuration System](developer_guide/configuration.md) - Config management
- [Testing Guidelines](developer_guide/testing.md) - Testing procedures

## API Reference
- [Config Class](api_reference/config.md) - Configuration management
- [ModelEngine](api_reference/model_engine.md) - Training orchestration
- [BaseModel](api_reference/base_model.md) - Model interface
- [TrainingCallbacks](api_reference/callbacks.md) - Training callbacks

## Training Workflows
1. **Model Configuration**: Define hyperparameters in config.json
2. **Dataset Preparation**: Load and preprocess training data
3. **Model Initialization**: Create and configure model architecture
4. **Training Execution**: Run training with real-time monitoring
5. **State Persistence**: Save model weights and training state

## Configuration Management
The core module uses a centralized configuration system:
```python
from config import Config
cfg = Config()
cfg.use_model = "WaveNet5"
cfg.dataset_type = "AliasSimu"
cfg.epoch_train = 1000
```

## Model Architectures
- **FRIKAN**: Frequency-domain IIR Kolmogorov-Arnold Networks
- **WaveNet1-5**: Dilated convolution architectures with IIR filters
- **LSTM/GRN/RNN**: Recurrent architectures for time series
- **Transformer**: Attention-based sequence modeling

## Training Infrastructure
- `training.py` - Main training script with real-time callbacks
- `training_state.py` - State management for resumable training
- `training_log.py` - Comprehensive logging system
- `model_engine.py` - Training workflow orchestration

## Dataset Integration
- **Dataset_COMP_MET**: Real electrochemical sensor data
- **Dataset_COMP_PE**: Piezoelectric sensor simulation
- **Dataset_COMP_Alias**: Real aliasing distortion data
- **Dataset_COMP_AliasSimu**: Simulated aliasing data

## GPU Configuration
GPU support is managed through metnl.py:
```python
import metnl
metnl.set_using_gpu(True)  # Enable GPU acceleration
```

## Project Integration
- **Project Management**: Projects stored in `projects/{PROJECT_NAME}/`
- **Configuration**: Project-specific `config.json` files
- **Artifacts**: Training outputs in `data/` subdirectories
- **Weights**: Model weights as `.weights.json` or `.weights.h5`

## Entry Points
- `cli.py -p PROJECT_NAME` - Command-line project training
- `ui.py` - Interactive GUI application
- `core/training.py` - Direct training with monitoring

## Related Modules
- [Analysis Tools](../../analysis/doc/README.md) - Model analysis
- [Inference Engine](../../inference/doc/README.md) - Model inference
- [SPICE Simulator](../../spice_simulator/doc/README.md) - Circuit simulation

## Advanced Features
- **Zero-Code Configuration**: Complete JSON-based configuration
- **Real-time Callbacks**: Live progress monitoring
- **Cosine Annealing**: Adaptive learning rate scheduling
- **State Resumption**: Continue interrupted training sessions

## Dependencies
- TensorFlow 2.6 (required for compatibility)
- NumPy/SciPy for numerical operations
- Matplotlib for visualization
- Custom model implementations

---
*Last updated: 2025-01-08*