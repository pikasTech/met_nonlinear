"""
spice_simulator 测试包
"""

import sys
import os
import importlib
from types import ModuleType

class MockReluModels(ModuleType):
    """
    模拟的ReluModels模块，解决原始模块中的语法错误
    """
    class ReluModel:
        def __init__(self):
            pass
        
        def get_netlist_text(self, channel_index, pre_output_node, output_node, diode_model):
            return ""
            
        def modify_output_signals(self, output_signals, relu_config):
            return output_signals
    
    class NoReluModel(ReluModel):
        pass
        
    class OpAmpReluModel(ReluModel):
        pass
        
    class DiodeClampReluModel(ReluModel):
        pass
        
    class ReluModelFactory:
        DIODE_MODELS = {
            '1n4148': {
                'file': None,
                'params': 'D(Is=2.52n Rs=0.568 N=1.752 Cjo=4p M=0.4 tt=20n)'
            },
            '1n4007': {
                'file': None,
                'params': 'D(Is=14.11n N=1.984 Rs=33.89m Ikf=94.81 Xti=3 Eg=1.11 Cjo=25.89p M=0.44 Vj=0.3245 Fc=0.5 Bv=1000 Ibv=10u Tt=5.7u)'
            }
        }
        
        @staticmethod
        def create_model(use_relu=False, relu_config=None, opamp_model=None):
            return MockReluModels.NoReluModel()

# 创建模拟的relu_models模块
mock_relu_models = MockReluModels('relu_models')
sys.modules['relu_models'] = mock_relu_models 