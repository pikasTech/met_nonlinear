"""
测试运放模型和ReLU模型自包含参数的功能
"""
from opamp_models import OpAmpModelFactory, IdealOpAmpModel, RealOpAmpModel
from relu_models import ReluModelFactory, DiodeClampReluModel, OpAmpReluModel
from circuit_dense_factory import DenseCircuitFactory
import numpy as np

def test_opamp_models():
    """测试运放模型的参数管理"""
    print("===== 测试运放模型 =====")
    
    # 理想运放模型，自定义参数
    model1 = IdealOpAmpModel(gain=1e6, input_resistance=1e9, output_resistance=1e-3)
    print(f"理想运放模型参数: 增益={model1.gain}, 输入电阻={model1.input_resistance}")
    
    # 使用工厂创建LM324
    model2 = OpAmpModelFactory.create_model({'model': 'lm324'})
    print(f"LM324模型: 名称={model2.model_name}, 包含文件={model2.include_file}")
    
    # 测试生成网表文本
    netlist = model1.get_netlist_text("Xopamp1", "in_pos", "in_neg", "out")
    print("理想运放网表示例:\n", netlist[:100], "...(省略)")
    
    include_text = model2.get_include_text()
    print(f"实际运放包含语句: {include_text}")

def test_relu_models():
    """测试ReLU模型的参数管理"""
    print("\n===== 测试ReLU模型 =====")
    
    # 创建理想运放
    opamp = IdealOpAmpModel()
    
    # 运放ReLU模型，使用自定义参数
    model1 = OpAmpReluModel(opamp, r_value=20e3, gain=2.0, clamp_voltage=0.5)
    print(f"运放ReLU模型参数: 电阻={model1.r_value}, 增益={model1.gain}, 钳位电压={model1.clamp_voltage}")
    
    # 二极管钳位ReLU模型
    model2 = DiodeClampReluModel(input_resistance=15e3, clamp_voltage=-0.2)
    print(f"二极管ReLU模型参数: 输入电阻={model2.input_resistance}, 钳位电压={model2.clamp_voltage}")
    
    # 使用工厂创建ReLU模型
    config = {'type': 'diode_clamp', 'R_value': 12e3, 'clamp_voltage': 0.1}
    model3 = ReluModelFactory.create_model(True, config)
    
    # 检查模型类型和参数
    print(f"工厂创建的模型类型: {type(model3).__name__}")
    if isinstance(model3, DiodeClampReluModel):
        print(f"参数: 输入电阻={model3.input_resistance}, 钳位电压={model3.clamp_voltage}")

def test_dense_circuit():
    """测试DenseCircuit工厂创建整个电路"""
    print("\n===== 测试电路工厂 =====")
    
    gains = np.array([[1, -1], [2, -2]])
    
    # 创建带有特定参数的op_amp_relu电路
    relu_config = {
        'gain': 1.5,
        'R_value': 22e3,
        'clamp_voltage': 0.1
    }
    
    circuit = DenseCircuitFactory.create(
        'op_amp_relu', 
        gains=gains, 
        use_e96=True,
        relu_config=relu_config
    )
    
    print(f"电路类型: op_amp_relu")
    print(f"输入数量: {circuit.n_inputs}")
    print(f"输出数量: {circuit.n_outputs}")
    print(f"使用ReLU: {circuit.use_relu}")
    print(f"运放模型类型: {type(circuit.opamp_model).__name__}")
    print(f"ReLU模型类型: {type(circuit.relu_model).__name__}")
    
    # 检查ReLU模型参数是否正确传递
    if isinstance(circuit.relu_model, OpAmpReluModel):
        print(f"ReLU增益: {circuit.relu_model.gain}")
        print(f"ReLU电阻值: {circuit.relu_model.r_value}")
        print(f"ReLU钳位电压: {circuit.relu_model.clamp_voltage}")

if __name__ == "__main__":
    test_opamp_models()
    test_relu_models()
    test_dense_circuit()
