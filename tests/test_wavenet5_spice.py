"""
WaveNet5 SPICE转换功能测试
"""
import pytest
import numpy as np
from pathlib import Path
import sys

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models.wavenet_models import WaveNet5
from models.layer_support import SpiceModelSupport
from calibration_analyzer.wavedata import WaveData, WaveRecord
from inference.backends.spice.backend import SPICEBackend


class TestWaveNet5SPICE:
    """WaveNet5 SPICE转换测试类"""
    
    @pytest.fixture
    def wavenet5_model(self):
        """创建一个简单的WaveNet5模型用于测试"""
        model = WaveNet5(
            kernel_units=4,
            fs=1000,
            activation='relu',
            model_subcfg={
                'init_center_freqs': [10, 20],
                'init_quality_factors': [1.0, 1.5],
                'post_dense': True,
                'post_dense_activation': 'relu',
                'post_dense_units': 4,
                'post_dense_layers': 2
            }
        )
        # 构建模型
        model.build_model((100, 1))
        return model
    
    def test_wavenet5_inherits_spice_support(self):
        """测试WaveNet5是否继承了SpiceModelSupport"""
        assert issubclass(WaveNet5, SpiceModelSupport)
    
    def test_wavenet5_has_to_spice_method(self, wavenet5_model):
        """测试WaveNet5是否有to_spice方法"""
        assert hasattr(wavenet5_model, 'to_spice')
        assert callable(wavenet5_model.to_spice)
    
    def test_to_spice_returns_list(self, wavenet5_model):
        """测试to_spice方法返回列表"""
        spice_objects = wavenet5_model.to_spice()
        assert isinstance(spice_objects, list)
        assert len(spice_objects) > 0
    
    def test_all_layers_support_spice(self, wavenet5_model):
        """测试所有层都支持SPICE转换"""
        layer_models = wavenet5_model.get_layered_models()
        for layer in layer_models:
            assert hasattr(layer, 'to_spice')
            assert isinstance(layer, SpiceModelSupport)
    
    def test_spice_backend_accepts_wavenet5(self, wavenet5_model):
        """测试SPICEBackend可以接受WaveNet5模型"""
        backend = SPICEBackend(wavenet5_model)
        # 不应该抛出异常
        assert backend.model == wavenet5_model
    
    def test_spice_export_with_parameters(self, wavenet5_model):
        """测试带参数的SPICE导出"""
        opamp_config = {
            'model': 'opa1611',
            'include_file': 'test.lib'
        }
        
        spice_objects = wavenet5_model.to_spice(
            output_path=None,
            opamp_config=opamp_config,
            use_e96=True,
            amp=2.0
        )
        
        assert len(spice_objects) == len(wavenet5_model.get_layered_models())
    
    @pytest.mark.skipif(not Path("spice_simulator").exists(), 
                        reason="需要spice_simulator模块")
    def test_spice_backend_export(self, wavenet5_model, tmp_path):
        """测试通过SPICEBackend导出模型"""
        backend = SPICEBackend(
            wavenet5_model, 
            output_folder=str(tmp_path)
        )
        
        # 应该不再抛出"模型不支持导出到SPICE格式"的错误
        try:
            spice_model = backend.export_model_to_spice()
            assert spice_model is not None
            assert isinstance(spice_model, list)
        except ValueError as e:
            pytest.fail(f"导出失败: {str(e)}")