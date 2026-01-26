#!/usr/bin/env python3
"""
高通滤波器语法测试脚本

测试修改后的代码语法是否正确，基本结构是否完整
"""

import sys
import os
# 添加项目根目录和spice_simulator目录到Python路径
project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
spice_sim_dir = os.path.join(project_root, 'spice_simulator')
sys.path.insert(0, project_root)
sys.path.insert(0, spice_sim_dir)

def test_imports():
    """测试所有相关模块是否可以正常导入"""
    print("🧪 测试1: 模块导入")
    
    try:
        from circuit_dense import DenseCircuit, DenseCircuitFactory
        print("✅ circuit_dense模块导入成功")
        
        from config import Config
        print("✅ config模块导入成功")
        
        from models.model_layers import DenseLayer
        print("✅ model_layers模块导入成功")
        
        from inference.backends.spice.backend import SPICEBackend
        print("✅ spice backend模块导入成功")
        
        from inference.processing.backend_manager import BackendManager
        print("✅ backend_manager模块导入成功")
        
        from inference.processing.inference_processor import InferenceProcessor
        print("✅ inference_processor模块导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_structure():
    """测试配置结构是否正确"""
    print("\n🧪 测试2: 配置结构")
    
    try:
        from config import Config
        config = Config()
        
        # 验证inference_config存在
        assert hasattr(config, 'inference_config'), "Config应该有inference_config属性"
        assert 'high_pass_config' in config.inference_config, "inference_config应该包含high_pass_config"
        
        # 验证高通滤波器配置的默认值
        hp_config = config.inference_config['high_pass_config']
        assert hp_config['enable'] == False, "默认应该禁用高通滤波器"
        assert hp_config['cutoff_freq'] == 1.0, "默认截止频率应该为1.0Hz"
        assert hp_config['bias_voltage'] == 0.0, "默认bias电压应该为0.0V"
        
        print("✅ 配置结构正确")
        return True
        
    except Exception as e:
        print(f"❌ 配置结构测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_circuit_dense_constructor():
    """测试DenseCircuit构造函数是否接受high_pass_config参数"""
    print("\n🧪 测试3: DenseCircuit构造函数")
    
    try:
        from spice_simulator.circuit_dense import DenseCircuit
        
        # 测试没有high_pass_config的情况
        circuit1 = DenseCircuit(gains=[[1.0, -1.0], [0.5, 2.0]])
        assert hasattr(circuit1, 'high_pass_config'), "DenseCircuit应该有high_pass_config属性"
        assert circuit1.high_pass_config['enable'] == False, "默认应该禁用高通滤波器"
        
        # 测试有high_pass_config的情况
        hp_config = {'enable': True, 'cutoff_freq': 0.5, 'bias_voltage': 2.5}
        circuit2 = DenseCircuit(gains=[[1.0, -1.0], [0.5, 2.0]], high_pass_config=hp_config)
        assert circuit2.high_pass_config['enable'] == True, "应该启用高通滤波器"
        assert circuit2.high_pass_config['cutoff_freq'] == 0.5, "截止频率应该为0.5Hz"
        assert circuit2.high_pass_config['bias_voltage'] == 2.5, "bias电压应该为2.5V"
        
        print("✅ DenseCircuit构造函数正确")
        return True
        
    except Exception as e:
        print(f"❌ DenseCircuit构造函数测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_factory_methods():
    """测试工厂方法是否支持high_pass_config"""
    print("\n🧪 测试4: 工厂方法")
    
    try:
        from spice_simulator.circuit_dense import DenseCircuitFactory
        
        hp_config = {'enable': True, 'cutoff_freq': 1.0}
        
        # 测试主要工厂方法
        circuit1 = DenseCircuitFactory.create(gains=[[1.0]], high_pass_config=hp_config)
        assert circuit1.high_pass_config['enable'] == True, "create方法应该支持high_pass_config"
        
        circuit2 = DenseCircuitFactory.create_ideal(gains=[[1.0]], high_pass_config=hp_config)
        assert circuit2.high_pass_config['enable'] == True, "create_ideal方法应该支持high_pass_config"
        
        circuit3 = DenseCircuitFactory.create_with_relu(gains=[[1.0]], high_pass_config=hp_config)
        assert circuit3.high_pass_config['enable'] == True, "create_with_relu方法应该支持high_pass_config"
        
        circuit4 = DenseCircuitFactory.create_ideal_with_relu(gains=[[1.0]], high_pass_config=hp_config)
        assert circuit4.high_pass_config['enable'] == True, "create_ideal_with_relu方法应该支持high_pass_config"
        
        circuit5 = DenseCircuitFactory.create_with_tanh(gains=[[1.0]], high_pass_config=hp_config)
        assert circuit5.high_pass_config['enable'] == True, "create_with_tanh方法应该支持high_pass_config"
        
        circuit6 = DenseCircuitFactory.create_ideal_with_tanh(gains=[[1.0]], high_pass_config=hp_config)
        assert circuit6.high_pass_config['enable'] == True, "create_ideal_with_tanh方法应该支持high_pass_config"
        
        print("✅ 所有工厂方法支持high_pass_config")
        return True
        
    except Exception as e:
        print(f"❌ 工厂方法测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_denselayer_to_spice():
    """测试DenseLayer.to_spice方法是否接受high_pass_config参数"""
    print("\n🧪 测试5: DenseLayer.to_spice方法")
    
    try:
        from models.model_layers import DenseLayer
        
        # 这里我们只测试方法签名，不执行实际的SPICE导出
        # 因为那需要更复杂的模型对象
        
        # 检查to_spice方法是否存在且支持high_pass_config参数
        import inspect
        sig = inspect.signature(DenseLayer.to_spice)
        params = list(sig.parameters.keys())
        
        assert 'high_pass_config' in params, "to_spice方法应该接受high_pass_config参数"
        
        print("✅ DenseLayer.to_spice方法签名正确")
        return True
        
    except Exception as e:
        print(f"❌ DenseLayer.to_spice方法测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_netlist_generation():
    """测试网表生成是否包含高通滤波器"""
    print("\n🧪 测试6: 网表生成")
    
    try:
        from spice_simulator.circuit_dense import DenseCircuitFactory
        
        # 测试禁用高通滤波器的情况
        circuit1 = DenseCircuitFactory.create_ideal(
            gains=[[1.0]], 
            high_pass_config={'enable': False}
        )
        netlist1 = circuit1.get_circuit_netlist()
        assert "C_hp" not in netlist1, "禁用时网表不应包含高通滤波器电容"
        assert "R_hp" not in netlist1, "禁用时网表不应包含高通滤波器电阻"
        
        # 测试启用高通滤波器的情况
        circuit2 = DenseCircuitFactory.create_ideal(
            gains=[[1.0]], 
            high_pass_config={'enable': True, 'cutoff_freq': 1.0, 'bias_voltage': 2.5}
        )
        netlist2 = circuit2.get_circuit_netlist()
        assert "C_hp" in netlist2, "启用时网表应包含高通滤波器电容"
        assert "R_hp" in netlist2, "启用时网表应包含高通滤波器电阻"
        assert "hp_bias" in netlist2, "启用时网表应包含bias电压节点"
        
        print("✅ 网表生成正确")
        return True
        
    except Exception as e:
        print(f"❌ 网表生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 开始高通滤波器语法测试")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config_structure,
        test_circuit_dense_constructor,
        test_factory_methods,
        test_denselayer_to_spice,
        test_netlist_generation
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("🎉 所有语法测试通过！高通滤波器功能已成功集成")
        print("✅ 可以使用以下命令测试完整功能:")
        print("   python cli.py -i WNET5q1h2u6l3")
        print("   修改config.json中的high_pass_config来启用功能")
    else:
        print("❌ 部分测试失败，请检查错误信息")
        sys.exit(1)

if __name__ == "__main__":
    main()