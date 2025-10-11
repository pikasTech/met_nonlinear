"""
File utilities for bias tuner.
Handles JSON reading/writing and file backup operations.
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional


def read_json(filepath: Path) -> Dict[str, Any]:
    """
    Read JSON file with error handling.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Dict containing JSON data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"JSON file not found: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json(data: Dict[str, Any], filepath: Path, indent: int = 4) -> None:
    """
    Write data to JSON file with pretty formatting.
    
    Args:
        data: Dictionary to write
        filepath: Path to output file
        indent: JSON indentation level
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def backup_file(filepath: Path, backup_dir: Optional[Path] = None) -> Path:
    """
    Create backup of file with timestamp.
    
    Args:
        filepath: File to backup
        backup_dir: Directory for backup (default: same as original)
        
    Returns:
        Path to backup file
        
    Raises:
        FileNotFoundError: If original file doesn't exist
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Cannot backup non-existent file: {filepath}")
    
    # Determine backup directory
    if backup_dir is None:
        backup_dir = filepath.parent / "backups"
    else:
        backup_dir = Path(backup_dir)
    
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"{filepath.stem}_backup_{timestamp}{filepath.suffix}"
    backup_path = backup_dir / backup_name
    
    # Copy file
    shutil.copy2(filepath, backup_path)
    
    return backup_path


def ensure_parent_dir(filepath: Path) -> Path:
    """
    Ensure parent directory exists for given file path.
    
    Args:
        filepath: File path
        
    Returns:
        Path object with parent directory created
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    return filepath


def validate_json_structure(data: Dict[str, Any], required_keys: list) -> bool:
    """
    Validate that JSON data contains required keys.
    
    Args:
        data: Dictionary to validate
        required_keys: List of required top-level keys
        
    Returns:
        True if all required keys present
    """
    return all(key in data for key in required_keys)


def merge_nested_dict(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries, with update values taking precedence.
    
    Args:
        base: Base dictionary
        update: Dictionary with updates
        
    Returns:
        Merged dictionary (new object)
    """
    import copy
    result = copy.deepcopy(base)
    
    for key, value in update.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_nested_dict(result[key], value)
        else:
            result[key] = value
    
    return result