"""
Path finding utilities for bias tuner.
Provides flexible path search without hardcoded depth limits.
"""

from pathlib import Path
from typing import List, Optional


def find_project_root(
    start_path: Path, 
    markers: Optional[List[str]] = None,
    max_depth: int = 10
) -> Optional[Path]:
    """
    Find project root directory by looking for marker files.
    
    Args:
        start_path: Starting directory for search
        markers: List of filenames that indicate project root
        max_depth: Maximum directory levels to search up
        
    Returns:
        Path to project root or None if not found
    """
    if markers is None:
        from ..config.defaults import PATH_CONFIG
        markers = PATH_CONFIG["project_markers"]
    
    current = Path(start_path).resolve()
    
    for _ in range(max_depth):
        # Check if any marker exists in current directory
        for marker in markers:
            if (current / marker).exists():
                return current
        
        # Move to parent directory
        parent = current.parent
        if parent == current:  # Reached root of filesystem
            break
        current = parent
    
    return None


def find_cli(
    start_path: Optional[Path] = None, 
    search_depth: Optional[int] = None
) -> Optional[Path]:
    """
    Find cli.py file in parent directories.
    
    Args:
        start_path: Starting directory (current dir if None)
        search_depth: Maximum levels to search (uses config default if None)
        
    Returns:
        Path to cli.py or None if not found
    """
    if start_path is None:
        start_path = Path.cwd()
    
    if search_depth is None:
        from ..config.defaults import EXECUTION_CONFIG
        search_depth = EXECUTION_CONFIG["path_search_depth"]
    
    current = Path(start_path).resolve()
    
    for _ in range(search_depth):
        cli = current / "cli.py"
        if cli.exists():
            return cli
        
        parent = current.parent
        if parent == current:  # Reached root
            break
        current = parent
    
    return None


def find_relative_to_project(
    target_file: str,
    start_path: Optional[Path] = None
) -> Optional[Path]:
    """
    Find a file relative to project root.
    
    Args:
        target_file: Relative path from project root
        start_path: Starting directory for project search
        
    Returns:
        Absolute path to target file or None
    """
    if start_path is None:
        start_path = Path.cwd()
    
    project_root = find_project_root(start_path)
    if project_root is None:
        return None
    
    target_path = project_root / target_file
    return target_path if target_path.exists() else None