"""
Logging utility for bias tuner.
Integrates with the project's logging system for consistent output.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
import os

# Try to import the project's logging setup
try:
    # Add parent directories to path to find logger module
    from .path_finder import find_project_root
    current_dir = Path(__file__).resolve().parent
    project_root = find_project_root(current_dir)
    if project_root:
        sys.path.insert(0, str(project_root))
    
    from logger.logging_setup import setup_logging, get_module_logger, ColoredFormatter
    USE_PROJECT_LOGGER = True
except ImportError:
    USE_PROJECT_LOGGER = False
    
    # Fallback to simple logging if project logger not available
    class ColoredFormatter(logging.Formatter):
        """Custom formatter with colors for console output"""
        
        COLORS = {
            'DEBUG': '\033[36m',    # Cyan
            'INFO': '\033[32m',     # Green
            'WARNING': '\033[33m',  # Yellow
            'ERROR': '\033[31m',    # Red
            'CRITICAL': '\033[35m', # Magenta
        }
        RESET = '\033[0m'
        
        def format(self, record):
            log_color = self.COLORS.get(record.levelname, self.RESET)
            record.levelname = f"{log_color}{record.levelname}{self.RESET}"
            return super().format(record)


def setup_logger(name="bias_tuner", log_dir=None, console_level=logging.INFO, file_level=logging.DEBUG):
    """
    Set up logger with console and file handlers.
    
    Args:
        name: Logger name
        log_dir: Directory for log files (created if needed)
        console_level: Logging level for console output
        file_level: Logging level for file output
        
    Returns:
        logging.Logger: Configured logger instance
    """
    if USE_PROJECT_LOGGER and log_dir:
        # Use project's logging setup
        logger = setup_logging(
            log_dir=log_dir,
            default_level=logging.getLevelName(console_level),
            use_timestamp=True
        )
        # Get bias_tuner specific logger
        return get_module_logger('bias_tuner')
    
    # Fallback to simple logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_formatter = ColoredFormatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler if log_dir provided
    if log_dir:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = log_dir / f"bias_tuner_{timestamp}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(file_level)
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        logger.info(f"Logging to file: {log_file}")
    
    return logger


def get_logger(module_name=None):
    """
    Get a logger instance for a specific module.
    
    Args:
        module_name: Module name (e.g., 'bias_tuner.core.analyzer')
        
    Returns:
        Logger instance
    """
    if USE_PROJECT_LOGGER and module_name:
        return get_module_logger(module_name)
    
    name = f"bias_tuner.{module_name}" if module_name else "bias_tuner"
    return logging.getLogger(name)


# Create default logger instance
logger = setup_logger()