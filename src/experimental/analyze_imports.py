#!/usr/bin/env python3
"""Analyze imports in Python files to understand dependencies"""

import os
import re
from collections import defaultdict
from pathlib import Path

def extract_imports(file_path):
    """Extract all import statements from a Python file"""
    imports = {
        'standard': [],
        'external': [],
        'local_root': [],
        'local_subdir': []
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find all import statements
        import_pattern = r'^(?:from\s+([\w\.]+)\s+import\s+.*|import\s+([\w\.]+(?:\s*,\s*[\w\.]+)*))'
        matches = re.findall(import_pattern, content, re.MULTILINE)
        
        for match in matches:
            # Handle 'from X import Y' vs 'import X'
            module = match[0] if match[0] else match[1].split(',')[0].strip()
            
            # Classify the import
            if module in ['os', 'sys', 'json', 'time', 'hashlib', 're', 'traceback', 
                         'datetime', 'shutil', 'queue', 'multiprocessing']:
                imports['standard'].append(module)
            elif module.startswith(('tensorflow', 'keras', 'numpy', 'matplotlib', 
                                  'sklearn', 'scipy', 'pandas', 'plotly', 'tqdm', 
                                  'keyboard')):
                imports['external'].append(module)
            elif module in ['config', 'metnl', 'model_engine', 'training', 'ui', 
                           'cli', 'inference', 'data_processing', 'kan_lut',
                           'sample_list', 'model_analysis', 'loss_functions',
                           'training_state', 'training_log', 'data_viewer']:
                imports['local_root'].append(module)
            elif module.startswith(('models.', 'calibration_analyzer.', 'analysis.',
                                  'spice_simulator.', 'legacy.', 'data_utils.',
                                  'fig_process.', 'inference.backends.')):
                imports['local_subdir'].append(module)
            else:
                # Try to determine if it's a local module
                if '.' in module:
                    imports['local_subdir'].append(module)
                else:
                    imports['local_root'].append(module)
                    
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        
    return imports

def analyze_dependencies():
    """Analyze dependencies for main Python files"""
    root_dir = Path('/mnt/f/Work/met_nonlinear')
    main_files = [
        'config.py', 'data_processing.py', 'model_engine.py', 
        'training.py', 'ui.py', 'cli.py', 'metnl.py', 'inference.py'
    ]
    
    results = {}
    
    for file_name in main_files:
        file_path = root_dir / file_name
        if file_path.exists():
            imports = extract_imports(file_path)
            results[file_name] = imports
            
    return results

def print_analysis(results):
    """Print the analysis results"""
    print("=" * 80)
    print("PYTHON IMPORT ANALYSIS")
    print("=" * 80)
    
    # Analyze each file
    for file_name, imports in results.items():
        print(f"\n{file_name}:")
        print("-" * 40)
        
        if imports['standard']:
            print(f"  Standard Library: {', '.join(sorted(set(imports['standard'])))}")
        if imports['external']:
            print(f"  External Packages: {', '.join(sorted(set(imports['external'])))}")
        if imports['local_root']:
            print(f"  Local Root Modules: {', '.join(sorted(set(imports['local_root'])))}")
        if imports['local_subdir']:
            print(f"  Local Subdirectories: {', '.join(sorted(set(imports['local_subdir'])))}")
    
    # Categorize files
    print("\n" + "=" * 80)
    print("FILE CATEGORIES:")
    print("=" * 80)
    
    # Core modules (imported by many others)
    import_counts = defaultdict(int)
    for file_name, imports in results.items():
        for module in imports['local_root']:
            import_counts[module] += 1
    
    core_modules = [m for m, count in import_counts.items() if count >= 3]
    print(f"\nCore Modules (imported by 3+ files): {', '.join(sorted(core_modules))}")
    
    # Entry points (not imported by others)
    all_imported = set()
    for imports in results.values():
        all_imported.update(imports['local_root'])
    
    entry_points = []
    for file_name in results.keys():
        module_name = file_name.replace('.py', '')
        if module_name not in all_imported:
            entry_points.append(file_name)
    
    print(f"\nEntry Points (not imported): {', '.join(sorted(entry_points))}")
    
    # Dependencies from subdirectories to root
    print("\n" + "=" * 80)
    print("REVERSE DEPENDENCIES (subdirs importing from root):")
    print("=" * 80)
    
    # Check models directory
    models_dir = Path('/mnt/f/Work/met_nonlinear/models')
    if models_dir.exists():
        for py_file in models_dir.glob('*.py'):
            if py_file.name != '__init__.py':
                imports = extract_imports(py_file)
                if imports['local_root']:
                    print(f"\nmodels/{py_file.name}: {', '.join(imports['local_root'])}")

if __name__ == '__main__':
    results = analyze_dependencies()
    print_analysis(results)