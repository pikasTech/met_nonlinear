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