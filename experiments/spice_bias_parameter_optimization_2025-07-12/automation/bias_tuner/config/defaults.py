"""
Default configuration values for bias tuner.
All hardcoded values are centralized here for easy modification.
"""

# Network architecture configuration
NETWORK_CONFIG = {
    "default_layers": 5,
    "default_channels": 6,
    "compensatable_layers": [1, 2, 3],
    "layer_info": {
        0: {"name": "SVF Layer", "compensatable": False},
        1: {"name": "Dense Layer 1", "compensatable": True},
        2: {"name": "Dense Layer 2", "compensatable": True},
        3: {"name": "Dense Layer 3", "compensatable": True},
        4: {"name": "Output Layer", "compensatable": False}
    }
}

# Execution parameters
EXECUTION_CONFIG = {
    "inference_timeout": 600,        # seconds
    "analysis_timeout": 300,         # seconds
    "layer_delay": 2.0,             # seconds between layer compensations
    "monitoring_interval": 0.1,      # seconds for output monitoring
    "stall_detection_timeout": 60,   # seconds without output
    "thread_join_timeout": 1,        # seconds for thread cleanup
    "max_history_size": 100,         # max execution history entries
    "path_search_depth": 5,          # directory levels to search for cli.py
    "file_wait_timeout": 30,         # seconds to wait for file creation
    "file_check_interval": 0.5       # seconds between file existence checks
}

# Compensation strategy parameters
COMPENSATION_CONFIG = {
    "default_scale_factor": 0.8,
    "conservative_factor": 0.5,
    "adaptive_thresholds": {
        "small_error": 0.5,     # threshold for small errors (relative to mean)
        "large_error": 2.0      # threshold for large errors (relative to mean)
    },
    "adaptive_scales": {
        "small": 0.5,          # scale for small errors
        "medium": 0.8,         # scale for medium errors
        "large": 1.0           # scale for large errors
    },
    "optimization": {
        "search_range": (0.1, 2.0),        # min and max scale factors
        "search_points": 20,               # number of points to search
        "convergence_threshold": 1e-6,     # error threshold for convergence
        "default_target_reduction": 0.9,   # default target error reduction ratio
        "max_scale_factor": 2.0,           # maximum scale factor for optimization
        "divergence_threshold": 1.5        # factor to detect divergence
    },
    "iteration": {
        "max_iterations": 5,           # default max iterations for optimization
        "initial_scale": 0.5,         # scale factor for first iteration
        "subsequent_scale": 0.7       # scale factor for subsequent iterations
    }
}

# Mock mode configuration
MOCK_CONFIG = {
    "inference_delay": 0.1,    # seconds to simulate inference
    "analysis_delay": 0.05,    # seconds to simulate analysis
    "mock_states": {
        "baseline": "error_analysis_baseline.json",
        "layer1": "error_analysis_layer1.json",
        "layer12": "error_analysis_layer12.json",
        "layer123": "error_analysis_layer123.json"
    }
}

# Tuning parameters
TUNING_CONFIG = {
    "default_target_error": 0.001,    # default target error for optimization
    "report_timestamp_format": "%Y%m%d_%H%M%S",
    "dry_run_defaults": {
        "layers": 5,
        "channels": 6,
        "compensatable_layers": [1, 2, 3]
    }
}

# Python environment configuration
ENVIRONMENT_CONFIG = {
    "default_python_env": "python",              # default Python command
    "conda_python_env": "conda run -n tf26 python",  # conda environment command
}

# File and path configuration
PATH_CONFIG = {
    "config_filename": "config.json",
    "error_analysis_filename": "error_analysis.json",
    "inference_dirname": "inference",
    "data_dirname": "data",
    "backup_suffix": ".bak",
    "project_markers": ["cli.py", ".git", "requirements.txt"]  # files that indicate project root
}