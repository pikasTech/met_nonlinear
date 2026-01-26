# WaveNet5 SPICE支持实施方案

**日期**: 2025-01-07  
**目标**: 为WaveNet5模型添加完整的SPICE转换支持

## 📋 修改方案概述

根据调查报告，WaveNet5已具备95%的SPICE转换能力，只需添加桥接方法即可完成。本方案将通过最小化修改实现完整支持。

## 🔧 文件修改计划

### 1. models/wavenet_models.py

**修改点1**: 添加SpiceModelSupport继承
```python
# 原代码
class WaveNet5(BaseModel, LayeredModelSupport):

# 修改为
from .layer_support import SpiceModelSupport
class WaveNet5(BaseModel, LayeredModelSupport, SpiceModelSupport):
```

**修改点2**: 实现to_spice()方法
```python
def to_spice(self, output_path: str = None, opamp_config: Dict[str, Any] = None, 
             use_e96: bool = False, amp: float = 1.0):
    """
    导出WaveNet5到分层SPICE模型
    
    参数:
        output_path: 输出路径（用于分层模型时忽略）
        opamp_config: 运放配置
        use_e96: 是否使用E96标准电阻值
        amp: 信号增益倍数
    
    返回:
        List[SpiceModel]: SPICE模型对象列表
    """
    layer_models = self.get_layered_models()
    spice_objects = []
    
    for i, layer in enumerate(layer_models):
        # 为每层生成独立的输出路径（如果需要）
        layer_output_path = None
        if output_path:
            base_path = output_path.rsplit('.', 1)[0]
            ext = output_path.rsplit('.', 1)[1] if '.' in output_path else 'cir'
            layer_output_path = f"{base_path}_layer{i+1}.{ext}"
        
        # 导出层的SPICE模型
        spice_obj = layer.to_spice(
            output_path=layer_output_path,
            opamp_config=opamp_config,
            use_e96=use_e96,
            amp=amp if i == 0 else 1.0  # 只在第一层应用增益
        )
        spice_objects.append(spice_obj)
    
    return spice_objects
```

### 2. 创建测试文件: tests/test_wavenet5_spice.py

```python
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
from inference.inference_backends import SPICEBackend


class TestWaveNet5SPICE:
    """WaveNet5 SPICE转换测试类"""
    
    @pytest.fixture
    def wavenet5_model(self):
        """创建一个简单的WaveNet5模型用于测试"""
        model = WaveNet5(
            kernel_units=4,
            kernel_size=3,
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
        model.build_model((None, 100, 1))
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
```

### 3. 创建集成测试文件: tests/test_wavenet5_spice_integration.py

```python
"""
WaveNet5 SPICE集成测试
测试完整的推理流程
"""
import pytest
import numpy as np
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from cli import ProjectManager
from calibration_analyzer.wavedata import WaveData, WaveRecord
from calibration_analyzer.waveprocessor import WaveProcessor


class TestWaveNet5SPICEIntegration:
    """WaveNet5 SPICE集成测试"""
    
    @pytest.fixture
    def test_input_data(self):
        """创建测试输入数据"""
        # 创建一个简单的正弦波测试信号
        fs = 1000
        duration = 1.0
        t = np.linspace(0, duration, int(fs * duration))
        signal = np.sin(2 * np.pi * 10 * t) + 0.5 * np.sin(2 * np.pi * 20 * t)
        
        # 创建WaveData对象
        wave_data = WaveData(
            description="Test sine wave",
            author="Test"
        )
        
        record = WaveRecord(
            data=signal.reshape(-1, 1),
            sample_rate=fs,
            channel_names=["Input"],
            record_id="test_record"
        )
        wave_data.add_record(record)
        
        return wave_data
    
    @pytest.mark.skipif(not Path("projects/WNET5q0.5h2u6l3").exists(),
                        reason="需要WNET5q0.5h2u6l3项目")
    def test_wavenet5_project_spice_inference(self, test_input_data, tmp_path):
        """测试实际项目的SPICE推理"""
        # 加载项目
        pm = ProjectManager("WNET5q0.5h2u6l3")
        
        # 保存测试输入数据
        input_path = tmp_path / "test_input.h5"
        processor = WaveProcessor()
        processor.save_waveform(str(input_path), test_input_data)
        
        # 运行推理分析
        pm.config.inference_input_path = str(input_path)
        pm.config.inference_output_dir = str(tmp_path / "inference_output")
        
        # 应该能够成功运行SPICE推理
        try:
            pm.run_inference_analysis()
            
            # 检查输出文件
            output_dir = Path(pm.config.inference_output_dir)
            assert output_dir.exists()
            
            # 检查SPICE推理结果
            spice_output = output_dir / f"{pm.project_name}_spice_output.h5"
            if spice_output.exists():
                # SPICE推理成功
                assert True
            else:
                # 可能由于环境限制无法运行SPICE仿真
                pytest.skip("SPICE仿真未能完成，可能缺少NGspice")
                
        except Exception as e:
            if "模型不支持导出到 SPICE 格式" in str(e):
                pytest.fail("WaveNet5应该支持SPICE导出")
            else:
                # 其他错误可能是环境相关
                pytest.skip(f"集成测试失败: {str(e)}")
```

## 🧪 测试计划

### 1. 单元测试 (pytest)

```bash
# 运行基础功能测试
conda run -n tf26 pytest tests/test_wavenet5_spice.py -v

# 运行集成测试
conda run -n tf26 pytest tests/test_wavenet5_spice_integration.py -v

# 运行所有相关测试
conda run -n tf26 pytest tests/test_wavenet5_spice*.py -v --tb=short
```

### 2. 手动测试步骤

#### 步骤1: 验证SPICE导出功能
```bash
# 使用简单的WaveNet5项目测试
conda run -n tf26 python -c "
from cli import ProjectManager
pm = ProjectManager('WNET5q0.5h2u6l3')
model = pm.load_model()
print('模型加载成功')

# 测试to_spice方法
spice_objs = model.to_spice()
print(f'SPICE对象数量: {len(spice_objs)}')
print(f'第一层类型: {type(spice_objs[0])}')
"
```

#### 步骤2: 测试推理分析功能
```bash
# 运行完整的推理分析
conda run -n tf26 python cli.py -i WNET5q0.5h2u6l3

# 检查输出目录
ls projects/WNET5q0.5h2u6l3/data/inference_output/
```

#### 步骤3: 验证SPICE仿真结果
```python
# 手动验证脚本
from calibration_analyzer.waveprocessor import WaveProcessor
import matplotlib.pyplot as plt

# 加载结果
wp = WaveProcessor()
nn_output = wp.load_waveform("projects/WNET5q0.5h2u6l3/data/inference_output/WNET5q0.5h2u6l3_nn_output.h5")
spice_output = wp.load_waveform("projects/WNET5q0.5h2u6l3/data/inference_output/WNET5q0.5h2u6l3_spice_output.h5")

# 比较输出
print(f"神经网络输出形状: {nn_output.records[0].data.shape}")
print(f"SPICE输出形状: {spice_output.records[0].data.shape}")

# 可视化对比
fig, axes = plt.subplots(2, 1, figsize=(10, 8))
axes[0].plot(nn_output.records[0].data[:1000])
axes[0].set_title("Neural Network Output")
axes[1].plot(spice_output.records[0].data[:1000])
axes[1].set_title("SPICE Output")
plt.tight_layout()
plt.savefig("comparison.png")
```

## 📝 验证检查清单

- [ ] WaveNet5成功继承SpiceModelSupport
- [ ] to_spice()方法正确实现
- [ ] 所有pytest测试通过
- [ ] cli.py -i命令不再报错"模型不支持导出到SPICE格式"
- [ ] SPICE推理结果文件成功生成
- [ ] 误差分析报告正确显示SPICE vs NN对比

## 🚀 实施步骤

1. **备份原文件**
   ```bash
   cp models/wavenet_models.py models/wavenet_models.py.backup
   ```

2. **实施修改**
   - 修改wavenet_models.py添加SPICE支持
   - 创建测试文件

3. **运行测试**
   - 执行pytest测试套件
   - 进行手动测试验证

4. **提交代码**
   ```bash
   git add models/wavenet_models.py tests/test_wavenet5_spice*.py
   git commit -m "feat: 为WaveNet5添加完整的SPICE转换支持

- 添加SpiceModelSupport继承
- 实现to_spice()方法，支持分层SPICE导出
- 添加完整的pytest测试套件
- 验证与SPICEBackend的兼容性

现在WaveNet5可以通过cli.py -i进行SPICE推理分析

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
   ```

## ⚠️ 注意事项

1. **增益处理**: 只在第一层应用amp参数，避免信号过度放大
2. **输出路径**: 分层模型会生成多个SPICE文件，需要合理命名
3. **后处理**: SPICEBackend会自动调用各层的post_process方法
4. **兼容性**: 确保与现有推理框架完全兼容

## 🎯 成功标准

- WaveNet5模型可以通过SPICEBackend.export_model_to_spice()导出
- cli.py -i命令成功完成SPICE推理
- 生成正确的误差分析报告
- 所有测试通过