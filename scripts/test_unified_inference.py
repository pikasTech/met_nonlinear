#!/usr/bin/env python3
"""测试统一推理接口"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inference.backends.timeseries_backend import TimeSeriesBackend
from inference.backends.layered_backend import LayerByLayerBackend
from inference.backends.batch_backend import BatchPredictBackend

def test_unified_interface():
    """测试统一推理接口的基本功能"""
    
    print("="*60)
    print("统一推理接口测试")
    print("="*60)
    
    # 测试基类的默认实现
    print("\n1. 测试基类默认实现...")
    
    # 创建一个模拟模型
    class MockModel:
        def __init__(self):
            self.model_name = "TestModel"
    
    # 测试TimeSeriesBackend
    try:
        print("\n  - 测试TimeSeriesBackend...")
        backend = TimeSeriesBackend(MockModel())
        
        # 检查是否有infer_unified方法
        if hasattr(backend, 'infer_unified'):
            print("    ✓ infer_unified方法存在")
        else:
            print("    ✗ infer_unified方法不存在")
        
        # 检查返回类型注解
        import inspect
        sig = inspect.signature(backend.infer_unified)
        return_annotation = sig.return_annotation
        print(f"    返回类型: {return_annotation}")
        
    except Exception as e:
        print(f"    ✗ 错误: {e}")
    
    # 测试BatchPredictBackend
    try:
        print("\n  - 测试BatchPredictBackend...")
        backend = BatchPredictBackend(MockModel())
        
        if hasattr(backend, 'infer_unified'):
            print("    ✓ infer_unified方法存在")
            
            # 检查参数
            sig = inspect.signature(backend.infer_unified)
            params = list(sig.parameters.keys())
            print(f"    参数: {params}")
        else:
            print("    ✗ infer_unified方法不存在")
            
    except Exception as e:
        print(f"    ✗ 错误: {e}")
    
    # 测试类型系统
    print("\n2. 测试类型系统...")
    try:
        from inference.unified import InferenceResult, LayerInfo, DataRange
        print("  ✓ 成功导入统一数据结构")
        
        # 检查数据类是否正确定义
        print(f"  - InferenceResult字段: {list(InferenceResult.__annotations__.keys())}")
        print(f"  - LayerInfo字段: {list(LayerInfo.__annotations__.keys())}")
        print(f"  - DataRange字段: {list(DataRange.__annotations__.keys())}")
        
    except Exception as e:
        print(f"  ✗ 导入错误: {e}")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)

if __name__ == "__main__":
    test_unified_interface()