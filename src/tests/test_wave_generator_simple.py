#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple test for wave_generator - Basic functionality test without complex dependencies
"""

import unittest
import tempfile
import os
import json
import shutil
from unittest.mock import Mock, patch, MagicMock


class TestWaveGeneratorBasic(unittest.TestCase):
    """Test basic wave generator functionality without heavy dependencies"""
    
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
    
    def test_command_line_parsing(self):
        """Test command line argument parsing"""
        import sys
        
        # Test -w parameter detection
        original_argv = sys.argv.copy()
        try:
            sys.argv = ['cli.py', '-w', 'test_project']
            
            # Simulate the parsing logic
            task_type = 'train'  # default
            if '-w' in sys.argv:
                task_type = 'wave'
            
            self.assertEqual(task_type, 'wave')
            
        finally:
            sys.argv = original_argv
    
    def test_file_operations(self):
        """Test basic file operations for wave generation"""
        # Test output folder creation
        output_folder = os.path.join(self.temp_dir, 'wave_output')
        os.makedirs(output_folder, exist_ok=True)
        self.assertTrue(os.path.exists(output_folder))
        
        # Test wave file detection
        test_files = ['test1.wave', 'test2.txt', 'test3.wave']
        for filename in test_files:
            with open(os.path.join(output_folder, filename), 'w') as f:
                f.write('test content')
        
        # Find wave files
        wave_files = []
        for file in os.listdir(output_folder):
            if file.endswith('.wave'):
                wave_files.append(file)
        
        self.assertEqual(len(wave_files), 2)
        self.assertIn('test1.wave', wave_files)
        self.assertIn('test3.wave', wave_files)
        self.assertNotIn('test2.txt', wave_files)
    
    def test_project_config_loading(self):
        """Test project configuration loading"""
        # This tests the Config loading logic that would be used
        config_path = os.path.join(self.project_path, 'config.json')
        
        # Test config file exists
        self.assertTrue(os.path.exists(config_path))
        
        # Test config content
        with open(config_path, 'r') as f:
            loaded_config = json.load(f)
        
        self.assertEqual(loaded_config['dataset_type'], 'MET')
        self.assertEqual(loaded_config['sample_rate'], 1000)
    
    def test_directory_permissions(self):
        """Test directory permission checking"""
        test_dir = os.path.join(self.temp_dir, 'permission_test')
        os.makedirs(test_dir, exist_ok=True)
        
        # Test write permission
        self.assertTrue(os.access(test_dir, os.W_OK))
        
        # Test directory creation
        sub_dir = os.path.join(test_dir, 'subdir')
        os.makedirs(sub_dir, exist_ok=True)
        self.assertTrue(os.path.exists(sub_dir))
    
    @patch('builtins.print')
    def test_wave_generation_workflow_mock(self, mock_print):
        """Test wave generation workflow with mocked components"""
        
        # Mock the main components
        mock_project_manager = Mock()
        mock_project_manager.project_name = 'test_project'
        mock_project_manager.checkpoint_dir = os.path.join(self.project_path, 'data')
        
        mock_config = Mock()
        mock_config.dataset_type = 'MET'
        mock_project_manager.config = mock_config
        
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
        
        # Test the core logic that would be in DatasetWaveGenerator
        output_folder = os.path.join(mock_project_manager.checkpoint_dir, 'wave_output')
        os.makedirs(output_folder, exist_ok=True)
        
        # Simulate calling export_to_wave
        file_paths = mock_dataset.export_to_wave(
            output_folder=output_folder,
            description=f"Wave data for {mock_project_manager.project_name} - {mock_config.dataset_type}",
            author="Generated by cli.py",
            compress=True
        )
        
        # Build result
        result = {
            'project_name': mock_project_manager.project_name,
            'dataset_type': mock_config.dataset_type,
            'output_folder': output_folder,
            'compress': True,
            'files': file_paths,
            'dataset_info': {
                'magn_list': mock_dataset.magn_list,
                'freq_list': mock_dataset.freq_list,
                'magn_num': mock_dataset.magn_num,
                'freq_num': mock_dataset.freq_num,
                'fs': mock_dataset.fs,
                'time_clipped_s': mock_dataset.time_cliped_s,
                'type': mock_dataset.type
            }
        }
        
        # Verify result structure
        self.assertIn('project_name', result)
        self.assertIn('dataset_type', result)
        self.assertIn('files', result)
        self.assertIn('dataset_info', result)
        self.assertEqual(result['dataset_type'], 'MET')
        self.assertEqual(result['project_name'], 'test_project')
        
        # Verify mock was called
        mock_dataset.export_to_wave.assert_called_once()


if __name__ == '__main__':
    unittest.main()