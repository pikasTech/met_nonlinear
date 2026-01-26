"""
Tests for data range checking utilities.
"""

import pytest
import numpy as np
from io import StringIO
import sys
import json
from pathlib import Path

from inference.common.data_range import DataRangeInfo, DataRangeChecker


class TestDataRangeInfo:
    """Test DataRangeInfo dataclass"""
    
    def test_creation(self):
        """Test creating DataRangeInfo"""
        info = DataRangeInfo(
            min_value=0.0,
            max_value=1.0,
            mean_value=0.5,
            std_value=0.25,
            shape=(100,),
            dtype='float32',
            name='test_data'
        )
        
        assert info.min_value == 0.0
        assert info.max_value == 1.0
        assert info.mean_value == 0.5
        assert info.std_value == 0.25
        assert info.shape == (100,)
        assert info.dtype == 'float32'
        assert info.name == 'test_data'
    
    def test_string_representation(self):
        """Test string representation"""
        info = DataRangeInfo(
            min_value=0.0,
            max_value=1.0,
            mean_value=0.5,
            std_value=0.25,
            shape=(100,),
            dtype='float32',
            name='test_data'
        )
        
        str_repr = str(info)
        assert 'test_data' in str_repr
        assert 'Shape: (100,)' in str_repr
        assert 'Range: [0.000000, 1.000000]' in str_repr


class TestDataRangeChecker:
    """Test DataRangeChecker functionality"""
    
    @pytest.fixture
    def capture_print(self):
        """Fixture to capture print output"""
        def _capture():
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            try:
                yield sys.stdout
            finally:
                sys.stdout = old_stdout
        return _capture
    
    def test_analyze_numpy_array(self):
        """Test analyzing a numpy array"""
        data = np.array([1.234567, 2.345678, 3.456789])
        info = DataRangeChecker.analyze_data(data, "test", verbose=False)
        
        assert info.min_value == pytest.approx(1.234567, rel=1e-6)
        assert info.max_value == pytest.approx(3.456789, rel=1e-6)
        assert info.shape == (3,)
        assert 'float' in info.dtype
    
    def test_analyze_with_print(self, capture_print):
        """Test that verbose mode prints correctly"""
        data = np.array([1.234567, 2.345678, 3.456789])
        
        with capture_print() as output:
            DataRangeChecker.analyze_data(data, "测试数据", verbose=True)
            printed = output.getvalue()
        
        # 验证输出格式与原代码兼容
        assert "测试数据范围: 最小值=1.234567, 最大值=3.456789" in printed
    
    def test_analyze_list_of_arrays(self):
        """Test analyzing a list of arrays"""
        data_list = [
            np.array([1, 2, 3]),
            np.array([4, 5, 6]),
            np.array([7, 8, 9])
        ]
        
        info = DataRangeChecker.analyze_data(data_list, verbose=False)
        
        assert info.min_value == 1.0
        assert info.max_value == 9.0
        assert info.shape == (9,)  # All arrays concatenated
    
    def test_compare_ranges(self, capture_print):
        """Test comparing data ranges"""
        before = np.array([-1.5, -0.5, 0.5])
        after = np.array([0.5, 1.5, 2.5])
        
        with capture_print() as output:
            DataRangeChecker.compare_ranges(before, after, "相位修正")
            printed = output.getvalue()
        
        assert "相位修正:" in printed
        assert "修正前范围:" in printed
        assert "修正后范围:" in printed
        assert "数据从负值修正为正值" in printed
    
    def test_check_wave_data_mock(self):
        """Test checking wave data with mock object"""
        # Mock WaveData object
        class MockWaveData:
            def __init__(self):
                self.records = [
                    type('Record', (), {'data': np.array([[1, 2], [3, 4]])})(),
                    type('Record', (), {'data': np.array([[5, 6], [7, 8]])})()
                ]
        
        wave_data = MockWaveData()
        info = DataRangeChecker.check_wave_data(wave_data, "MockWave")
        
        assert info.min_value == 1.0
        assert info.max_value == 8.0
    
    def test_print_layer_range(self, capture_print):
        """Test layer range printing"""
        layer_output = np.random.randn(10, 6)
        
        with capture_print() as output:
            info = DataRangeChecker.print_layer_range(2, layer_output, "Layer")
            printed = output.getvalue()
        
        assert "Layer 2" in printed
        assert "范围:" in printed
        assert info.shape == (10, 6)
    
    def test_empty_list_error(self):
        """Test error handling for empty list"""
        with pytest.raises(ValueError, match="空数据列表"):
            DataRangeChecker.analyze_data([], "empty")
    
    def test_golden_data_compatibility(self, golden_data_dir):
        """Test compatibility with golden data format"""
        golden_file = golden_data_dir / "data_range_golden.json"
        
        if golden_file.exists():
            with open(golden_file) as f:
                golden = json.load(f)
            
            # Test simple array case
            if 'simple_array' in golden:
                data = np.array([1.234567, 2.345678, 3.456789])
                info = DataRangeChecker.analyze_data(data, verbose=False)
                
                assert info.min_value == pytest.approx(golden['simple_array']['min'])
                assert info.max_value == pytest.approx(golden['simple_array']['max'])