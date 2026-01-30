"""
WaveNet5 SPICE集成测试
测试完整的推理流程
"""
import pytest
import numpy as np
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.project_manager import ProjectManager
from calibration_analyzer.wavedata import WaveData, WaveRecord


class TestWaveNet5SPICEIntegration:
    """WaveNet5 SPICE集成测试"""

    @pytest.fixture
    def test_input_data(self):
        """创建测试输入数据"""
        fs = 1000
        duration = 1.0
        t = np.linspace(0, duration, int(fs * duration))
        signal = np.sin(2 * np.pi * 10 * t) + 0.5 * np.sin(2 * np.pi * 20 * t)

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

    @pytest.mark.skip(reason="需要实际项目文件")
    def test_wavenet5_project_spice_inference(self, test_input_data, tmp_path):
        """测试实际项目的SPICE推理"""
        # 此测试需要实际的项目文件
        pytest.skip("需要实际项目文件 WNET5q0.5h2u6l3")

    def test_wavedata_creation(self, test_input_data):
        """测试WaveData对象创建"""
        assert test_input_data is not None
        assert len(test_input_data.records) == 1
        assert test_input_data.records[0].channel_names == ["Input"]

    def test_waveprocessor_import(self):
        """测试WaveProcessor导入"""
        try:
            from calibration_analyzer.waveprocessor import WaveProcessor
            processor = WaveProcessor()
            assert processor is not None
        except ImportError as e:
            pytest.skip(f"WaveProcessor 导入失败: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
