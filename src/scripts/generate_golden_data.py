"""
在重构前运行此脚本生成黄金标准数据
"""

import json
import numpy as np
from pathlib import Path
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def generate_golden_data():
    """生成黄金标准测试数据"""
    
    golden_dir = Path("inference/tests/golden_data")
    golden_dir.mkdir(parents=True, exist_ok=True)
    
    # 测试项目列表
    test_projects = [
        "WNET5q0.5h2u6l4"  # 使用实际存在的项目
    ]
    
    results = {}
    
    try:
        from inference.manager import InferenceManager
        from inference.processor import InferenceProcessor
        
        for project in test_projects:
            project_path = Path(f"projects/{project}")
            if not project_path.exists():
                print(f"警告: 项目 {project} 不存在，跳过")
                continue
                
            print(f"生成项目 {project} 的黄金数据...")
            
            try:
                manager = InferenceManager(str(project_path))
                
                # 执行各种推理
                results[project] = {}
                
                # NN推理
                try:
                    print(f"  - 执行NN推理...")
                    nn_result = manager.run_inference('nn')
                    if nn_result:
                        results[project]['nn_inference'] = serialize_result(nn_result)
                except Exception as e:
                    print(f"    NN推理失败: {e}")
                
                # SPICE推理
                try:
                    print(f"  - 执行SPICE推理...")
                    spice_result = manager.run_inference('spice')
                    if spice_result:
                        results[project]['spice_inference'] = serialize_result(spice_result)
                except Exception as e:
                    print(f"    SPICE推理失败: {e}")
                
                # NumPy推理
                try:
                    print(f"  - 执行NumPy推理...")
                    numpy_result = manager.run_inference('numpy')
                    if numpy_result:
                        results[project]['numpy_inference'] = serialize_result(numpy_result)
                except Exception as e:
                    print(f"    NumPy推理失败: {e}")
                    
            except Exception as e:
                print(f"  项目 {project} 处理失败: {e}")
                continue
    
    except ImportError as e:
        print(f"导入错误: {e}")
        print("将创建模拟数据用于测试...")
        
        # 创建模拟数据
        for project in test_projects:
            results[project] = {
                'nn_inference': create_mock_result(),
                'spice_inference': create_mock_result(),
                'numpy_inference': create_mock_result()
            }
    
    # 保存结果
    with open(golden_dir / "inference_results.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\\n黄金数据已保存到 {golden_dir}")
    
    # 创建数据范围的黄金数据
    create_data_range_golden_data(golden_dir)

def serialize_result(result):
    """序列化推理结果"""
    # 获取输出数据
    if hasattr(result, 'output_wave'):
        output_data = result.output_wave.get_single_channel_data()
    elif hasattr(result, 'output'):
        output_data = result.output
    else:
        output_data = np.array([])
    
    return {
        'output_shape': list(output_data.shape) if hasattr(output_data, 'shape') else [],
        'output_min': float(np.min(output_data)) if output_data.size > 0 else 0.0,
        'output_max': float(np.max(output_data)) if output_data.size > 0 else 0.0,
        'output_mean': float(np.mean(output_data)) if output_data.size > 0 else 0.0,
        'output_std': float(np.std(output_data)) if output_data.size > 0 else 0.0,
        'output_samples': output_data.flatten()[:10].tolist() if output_data.size > 0 else []
    }

def create_mock_result():
    """创建模拟结果用于测试"""
    mock_data = np.random.randn(1000, 1) * 0.1
    return {
        'output_shape': [1000, 1],
        'output_min': float(np.min(mock_data)),
        'output_max': float(np.max(mock_data)),
        'output_mean': float(np.mean(mock_data)),
        'output_std': float(np.std(mock_data)),
        'output_samples': mock_data.flatten()[:10].tolist()
    }

def create_data_range_golden_data(golden_dir):
    """创建数据范围检查的黄金数据"""
    
    # 测试用例
    test_cases = {
        'simple_array': np.array([1.234567, 2.345678, 3.456789]),
        'negative_values': np.array([-1.5, -0.5, 0.5, 1.5]),
        'large_range': np.array([1e-6, 1e-3, 1, 1e3, 1e6])
    }
    
    range_data = {}
    for name, data in test_cases.items():
        range_data[name] = {
            'min': float(np.min(data)),
            'max': float(np.max(data)),
            'mean': float(np.mean(data)),
            'std': float(np.std(data)),
            'formatted_output': f"  数据范围: 最小值={np.min(data):.6f}, 最大值={np.max(data):.6f}"
        }
    
    with open(golden_dir / "data_range_golden.json", 'w') as f:
        json.dump(range_data, f, indent=2)
    
    print("数据范围黄金数据已生成")

if __name__ == "__main__":
    generate_golden_data()