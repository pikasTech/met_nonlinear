"""Tests for file utilities."""

import pytest
import json
import tempfile
from pathlib import Path

from ..utils import file_utils


class TestFileUtils:
    """Test file utility functions."""
    
    def test_read_json_success(self, tmp_path):
        """Test successful JSON reading."""
        # Create test JSON file
        test_data = {"key": "value", "number": 42}
        test_file = tmp_path / "test.json"
        
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        
        # Read and verify
        result = file_utils.read_json(test_file)
        assert result == test_data
    
    def test_read_json_file_not_found(self):
        """Test reading non-existent JSON file."""
        with pytest.raises(FileNotFoundError):
            file_utils.read_json(Path("/nonexistent/file.json"))
    
    def test_write_json_success(self, tmp_path):
        """Test JSON writing."""
        test_data = {"test": "data", "nested": {"key": "value"}}
        test_file = tmp_path / "output.json"
        
        file_utils.write_json(test_data, test_file)
        
        # Verify file exists and content is correct
        assert test_file.exists()
        
        with open(test_file) as f:
            loaded = json.load(f)
        
        assert loaded == test_data
    
    def test_write_json_creates_parent_dirs(self, tmp_path):
        """Test that write_json creates parent directories."""
        test_file = tmp_path / "nested" / "dir" / "file.json"
        test_data = {"key": "value"}
        
        file_utils.write_json(test_data, test_file)
        
        assert test_file.exists()
        assert test_file.parent.exists()
    
    def test_backup_file_success(self, tmp_path):
        """Test file backup."""
        # Create original file
        original = tmp_path / "original.txt"
        original.write_text("test content")
        
        # Backup
        backup_path = file_utils.backup_file(original)
        
        # Verify backup
        assert backup_path.exists()
        assert backup_path.parent.name == "backups"
        assert "backup_" in backup_path.name
        assert backup_path.read_text() == "test content"
    
    def test_backup_file_not_found(self):
        """Test backing up non-existent file."""
        with pytest.raises(FileNotFoundError):
            file_utils.backup_file(Path("/nonexistent.txt"))
    
    def test_validate_json_structure(self):
        """Test JSON structure validation."""
        data = {"key1": "value", "key2": 42, "key3": {}}
        
        # Should pass
        assert file_utils.validate_json_structure(data, ["key1", "key2"])
        
        # Should fail
        assert not file_utils.validate_json_structure(data, ["key1", "missing"])
    
    def test_merge_nested_dict(self):
        """Test nested dictionary merging."""
        base = {
            "a": 1,
            "b": {"c": 2, "d": 3},
            "e": [1, 2, 3]
        }
        
        update = {
            "a": 10,
            "b": {"c": 20, "f": 4},
            "g": 5
        }
        
        result = file_utils.merge_nested_dict(base, update)
        
        expected = {
            "a": 10,
            "b": {"c": 20, "d": 3, "f": 4},
            "e": [1, 2, 3],
            "g": 5
        }
        
        assert result == expected
        # Ensure original not modified
        assert base["a"] == 1