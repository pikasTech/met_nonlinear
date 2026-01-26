#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test wave_generator.py module - DatasetWaveGenerator class
"""

import unittest
import tempfile
import os
import json
import shutil
from unittest.mock import Mock, patch
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    # Try to import with mocked dependencies if needed
    import sys
    from unittest.mock import Mock
    
    # Mock problematic dependencies
    if 'portalocker' not in sys.modules:
        sys.modules['portalocker'] = Mock()
    
    from core.wave_generator import DatasetWaveGenerator
    from cli import ProjectManager
    wave_generator_available = True
except ImportError as e:
    print(f"Warning: wave_generator module not available: {e}")
    wave_generator_available = False


@unittest.skipIf(not wave_generator_available, "wave_generator module not available")
class TestDatasetWaveGenerator(unittest.TestCase):
    """Test DatasetWaveGenerator class"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = os.path.join(self.temp_dir, 'test_project')
        os.makedirs(self.project_path, exist_ok=True)
        
        # Create test config
        self.config_data = {
            'dataset_type': 'MET',
            'data_path': 'data/test',
            'data_base_path': self.temp_dir,
            'sample_rate': 1000,
            'time_clipped_s': 2.0,
            'target_sweep': 1,
            'use_cache_features': False
        }
        
        config_path = os.path.join(self.project_path, 'config.json')
        with open(config_path, 'w') as f:
            json.dump(self.config_data, f)
        
        # Create data directory
        os.makedirs(os.path.join(self.project_path, 'data'), exist_ok=True)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_wave_generator_init(self):
        """Test wave generator initialization"""
        project_manager = ProjectManager(self.project_path)
        generator = DatasetWaveGenerator(project_manager)
        
        self.assertEqual(generator.project_manager, project_manager)
        self.assertEqual(generator.config, project_manager.config)
        self.assertIsNotNone(generator.logger)
    
    def test_prepare_output_folder_default(self):
        """Test default output folder preparation"""
        project_manager = ProjectManager(self.project_path)
        generator = DatasetWaveGenerator(project_manager)
        
        output_folder = generator._prepare_output_folder(None, False)
        expected_path = os.path.join(self.project_path, 'data', 'wave_output')
        self.assertEqual(output_folder, expected_path)
        self.assertTrue(os.path.exists(output_folder))
    
    def test_find_existing_wave_files(self):
        """Test finding existing wave files"""
        project_manager = ProjectManager(self.project_path)
        generator = DatasetWaveGenerator(project_manager)
        
        # Create test directory and files
        test_dir = os.path.join(self.temp_dir, 'test_files')
        os.makedirs(test_dir, exist_ok=True)
        
        # Create test files
        with open(os.path.join(test_dir, 'test1.wave'), 'w') as f:
            f.write('test')
        with open(os.path.join(test_dir, 'test2.txt'), 'w') as f:
            f.write('test')
        
        # Test find functionality
        wave_files = generator._find_existing_wave_files(test_dir)
        self.assertEqual(len(wave_files), 1)
        self.assertIn('test1.wave', wave_files)
        self.assertNotIn('test2.txt', wave_files)
    
    @patch('core.wave_generator.ModelEngine')
    def test_generate_wave_data_basic(self, mock_model_engine):
        """Test basic wave data generation"""
        # Mock dataset
        mock_dataset = Mock()
        mock_dataset.magn_list = [1.0, 2.0]
        mock_dataset.freq_list = [10, 20, 30]
        mock_dataset.magn_num = 2
        mock_dataset.freq_num = 3
        mock_dataset.fs = 1000
        mock_dataset.time_cliped_s = 2.0
        mock_dataset.type = 'MET'
        mock_dataset.export_to_wave.return_value = {
            'input': os.path.join(self.temp_dir, 'dataset_MET_input.wave'),
            'output_original': os.path.join(self.temp_dir, 'dataset_MET_output_original.wave')
        }
        
        # Mock ModelEngine
        mock_engine = Mock()
        mock_engine.dataset_test = mock_dataset
        mock_model_engine.return_value = mock_engine
        
        # Create generator
        project_manager = ProjectManager(self.project_path)
        generator = DatasetWaveGenerator(project_manager)
        
        # Generate wave data
        result = generator.generate_wave_data()
        
        # Verify results
        self.assertIn('project_name', result)
        self.assertIn('dataset_type', result)
        self.assertIn('files', result)
        self.assertIn('dataset_info', result)
        self.assertEqual(result['dataset_type'], 'MET')
        
        # Verify calls
        mock_dataset.export_to_wave.assert_called_once()


if __name__ == '__main__':
    unittest.main()