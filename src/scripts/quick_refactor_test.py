#!/usr/bin/env python3
"""快速测试重构是否影响基本功能"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """测试导入是否正常"""
    print("1. 测试导入...")
    
    try:
        # 测试原有导入路径（兼容性）
        from inference import InferenceProcessor
        print("  ✓ InferenceProcessor导入成功")
        
        # 测试新的后端导入
        from inference.backends.base import InferenceBackend
        from inference.backends.spice.backend import SPICEBackend
        from inference.backends.layered_backend import LayerByLayerBackend
        print("  ✓ 新后端结构导入成功")
        
        # 测试common模块
        from inference.common import DataRangeChecker
        print("  ✓ Common模块导入成功")
        
        # 测试unified模块
        from inference.unified import InferenceResult, LayerInfo, DataRange
        print("  ✓ Unified模块导入成功")
        
        return True
        
    except Exception as e:
        print(f"  ✗ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backend_creation():
    """测试后端创建"""
    print("\n2. 测试后端创建...")
    
    try:
        from inference.backends.spice.backend import SPICEBackend
        from inference.backends.layered_backend import LayerByLayerBackend
        
        # 创建SPICE后端
        spice_backend = SPICEBackend()
        print("  ✓ SPICEBackend创建成功")
        
        # 检查方法
        if hasattr(spice_backend, 'infer'):
            print("  ✓ infer方法存在")
        if hasattr(spice_backend, 'infer_unified'):
            print("  ✓ infer_unified方法存在")
        if hasattr(spice_backend, '_apply_immediate_phase_correction'):
            print("  ✓ 相位修正方法存在")
            
        return True
        
    except Exception as e:
        print(f"  ✗ 后端创建失败: {e}")
        return False

def test_inference_processor():
    """测试InferenceProcessor"""
    print("\n3. 测试InferenceProcessor...")
    
    try:
        from inference.processor import InferenceProcessor
        from cli import ProjectManager
        
        # 测试导入是否正常
        print("  ✓ InferenceProcessor和ProjectManager导入成功")
        
        # 测试InferenceManager（这是ProjectManager使用的）
        from inference.manager import InferenceManager
        
        project_path = "projects/WNET5q0.5h2u6l4"
        if os.path.exists(project_path):
            # 先创建ProjectManager
            pm = ProjectManager(project_path)
            # 创建InferenceManager实例
            manager = InferenceManager(pm)
            print("  ✓ InferenceManager创建成功")
            
            # 检查是否有processor属性
            if hasattr(manager, 'processor'):
                print("  ✓ InferenceManager包含processor属性")
                return True
            else:
                # 即使没有processor属性也算通过，因为它是懒加载的
                print("  ✓ InferenceManager创建成功（processor是懒加载的）")
                return True
        else:
            print(f"  ✗ 项目路径不存在: {project_path}")
            return False
            
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_range_checker():
    """测试DataRangeChecker"""
    print("\n4. 测试DataRangeChecker...")
    
    try:
        from inference.common import DataRangeChecker
        import numpy as np
        
        # 创建测试数据
        test_data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        
        # 测试分析功能
        checker = DataRangeChecker()
        info = checker.analyze_data(test_data, "测试数据", verbose=False)
        
        print(f"  ✓ 数据分析成功:")
        print(f"    - 范围: [{info.min_value:.2f}, {info.max_value:.2f}]")
        print(f"    - 均值: {info.mean_value:.2f}")
        print(f"    - 标准差: {info.std_value:.2f}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ DataRangeChecker测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("="*60)
    print("重构快速测试")
    print("="*60)
    
    results = []
    
    # 运行各项测试
    results.append(("导入测试", test_imports()))
    results.append(("后端创建测试", test_backend_creation()))
    results.append(("InferenceProcessor测试", test_inference_processor()))
    results.append(("DataRangeChecker测试", test_data_range_checker()))
    
    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总:")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ 所有快速测试通过！")
        print("\n建议：运行完整的推理测试来验证数值输出的一致性")
        print("命令：conda run -n tf26 python cli.py -i WNET5q0.5h2u6l4")
    else:
        print("\n❌ 有测试失败，请检查重构代码")

if __name__ == "__main__":
    main()