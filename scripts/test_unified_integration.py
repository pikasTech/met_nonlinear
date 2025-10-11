#!/usr/bin/env python3
"""集成测试：验证统一推理接口与现有代码的兼容性"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from inference.processor import InferenceProcessor
from inference.unified import UnifiedInferenceProcessor

def test_integration():
    """测试统一推理接口的集成"""
    
    print("="*60)
    print("统一推理接口集成测试")
    print("="*60)
    
    # 测试项目
    project_name = "WNET5q0.5h2u6l4"
    project_path = Path(f"projects/{project_name}")
    
    if not project_path.exists():
        print(f"❌ 项目不存在: {project_path}")
        return
    
    print(f"\n使用项目: {project_name}")
    
    # 1. 测试UnifiedInferenceProcessor是否可以正常导入
    print("\n1. 测试UnifiedInferenceProcessor...")
    try:
        # 检查类是否存在
        print("  ✓ UnifiedInferenceProcessor类成功导入")
        
        # 检查方法
        methods = [m for m in dir(UnifiedInferenceProcessor) if not m.startswith('_')]
        print(f"  公共方法: {methods}")
        
    except Exception as e:
        print(f"  ✗ 导入错误: {e}")
    
    # 2. 测试数据流
    print("\n2. 测试数据流...")
    
    # 输入文件
    input_wave = project_path / "data/wave_output/dataset_MET_output_original.wave"
    
    if input_wave.exists():
        print(f"  ✓ 输入文件存在: {input_wave.name}")
        
        # 测试加载
        try:
            from calibration_analyzer.wavedata import WaveData
            wave_data = WaveData.load(str(input_wave))
            print(f"  ✓ 成功加载wave文件，记录数: {len(wave_data.records)}")
            
            # 测试DataRange计算
            from inference.unified import DataRange
            data_range = DataRange.from_wavedata(wave_data)
            print(f"  ✓ DataRange计算成功:")
            print(f"    - 范围: [{data_range.min_value:.6f}, {data_range.max_value:.6f}]")
            print(f"    - 均值: {data_range.mean_value:.6f}")
            print(f"    - 标准差: {data_range.std_value:.6f}")
            
        except Exception as e:
            print(f"  ✗ 数据处理错误: {e}")
    else:
        print(f"  ✗ 输入文件不存在")
    
    # 3. 测试后端集成
    print("\n3. 测试后端集成...")
    
    # 测试基类的_create_unified_result方法
    try:
        from inference.backends.base import InferenceBackend
        
        # 创建一个测试实例
        class TestBackend(InferenceBackend):
            def infer(self, input_wave_data, use_scaler=False):
                # 返回一个模拟的WaveData
                return WaveData(description="Test", author="Test")
        
        backend = TestBackend()
        
        # 测试_create_unified_result
        if hasattr(backend, '_create_unified_result'):
            print("  ✓ _create_unified_result方法存在")
            
            # 创建测试数据
            test_wave = WaveData(description="Test", author="Test")
            result = backend._create_unified_result(
                backend_type="test",
                layers_data=test_wave,
                input_path="test.wave",
                output_dir="test_output"
            )
            
            print(f"  ✓ 成功创建InferenceResult:")
            print(f"    - 后端类型: {result.backend_type}")
            print(f"    - 模型名称: {result.model_name}")
            print(f"    - 层数: {len(result.layers)}")
            
        else:
            print("  ✗ _create_unified_result方法不存在")
            
    except Exception as e:
        print(f"  ✗ 后端测试错误: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. 测试与现有代码的兼容性
    print("\n4. 测试向后兼容性...")
    
    try:
        # 检查InferenceProcessor是否仍然正常工作
        from cli import ProjectManager
        
        print("  ✓ 现有导入正常工作")
        
        # 检查后端是否保持原有接口
        from inference.backends.timeseries_backend import TimeSeriesBackend
        backend = TimeSeriesBackend()
        
        # 检查infer方法是否存在
        if hasattr(backend, 'infer'):
            print("  ✓ 原有infer方法保留")
        
        # 检查新的infer_unified方法
        if hasattr(backend, 'infer_unified'):
            print("  ✓ 新的infer_unified方法添加成功")
            
    except Exception as e:
        print(f"  ✗ 兼容性错误: {e}")
    
    print("\n" + "="*60)
    print("集成测试完成")
    print("="*60)

if __name__ == "__main__":
    test_integration()