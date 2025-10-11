import logging
logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
'\nPhase correction utilities for SPICE inference.\n\nThis module handles phase correction for WaveNet5 and other models\nthat require phase adjustment after SPICE simulation.\n'
import numpy as np
from calibration_analyzer.wavedata import WaveData, WaveRecord

class PhaseCorrector:
    """Handles phase correction for SPICE and NumPy inference results"""

    def __init__(self):
        """Initialize the phase corrector"""
        pass

    def apply_immediate_phase_correction(self, layer_output, layer_index, model=None):
        """
        在每层SPICE推理完成后立即进行相位修正
        
        Args:
            layer_output: 当前层的SPICE推理输出（WaveData格式）
            layer_index: 层索引（1-based，1=第一层）
            model: 模型对象（用于判断模型类型）
            
        Returns:
            修正后的WaveData，可直接传入下一层
        """
        if not self._is_wavenet5_model(model):
            return layer_output
        if layer_index == 1:
            return self._correct_svf_phase_immediate(layer_output)
        elif layer_index in [2, 3, 4]:
            return self._correct_dense_phase_immediate(layer_output)
        elif layer_index == 5:
            return layer_output
        else:
            return layer_output

    def _correct_dense_phase_immediate(self, wave_data):
        """
        对Dense层进行即时相位修正（全通道反相）
        
        Args:
            wave_data: 待修正的WaveData
            
        Returns:
            修正后的WaveData
        """
        try:
            corrected_wave_data = WaveData(description=f'{wave_data.description} (Dense Phase Corrected)', author=wave_data.author)
            corrected_wave_data.user_metadata = wave_data.user_metadata.copy()
            for record in wave_data.records:
                corrected_record_data = record.data.copy()
                corrected_record_data *= -1
                corrected_record = WaveRecord(corrected_record_data, sample_rate=record.sample_rate, channel_names=record.channel_names.copy() if hasattr(record, 'channel_names') else None, record_id=f'{record.record_id}_phase_corrected', creation_date=record.creation_date if hasattr(record, 'creation_date') else None, modified_date=record.modified_date if hasattr(record, 'modified_date') else None, units=record.units if hasattr(record, 'units') else 'V', user_metadata=record.user_metadata.copy() if hasattr(record, 'user_metadata') else {})
                corrected_wave_data.add_record(corrected_record)
            return corrected_wave_data
        except Exception as e:
            logger.info(f'❌ Dense层相位修正失败: {str(e)}')
            return wave_data

    def _correct_svf_phase_immediate(self, wave_data):
        """
        对SVF层进行即时相位修正（复用现有逻辑）
        
        Args:
            wave_data: 待修正的WaveData
            
        Returns:
            修正后的WaveData
        """
        return self._correct_svf_phase(wave_data)

    def _correct_svf_phase(self, wave_data):
        """
        对SVF层输出进行相位修正
        
        修正方案：
        - HP通道（索引 0, 3, 6, ...）：反相
        - BP通道（索引 1, 4, 7, ...）：保持不变
        - LP通道（索引 2, 5, 8, ...）：反相
        
        Args:
            wave_data: 原始WaveData对象
            
        Returns:
            修正后的WaveData对象
        """
        try:
            corrected_data = WaveData(description=f'{wave_data.description} (SVF Phase Corrected)' if wave_data.description else 'SVF Phase Corrected', author=wave_data.author)
            if hasattr(wave_data, 'user_metadata'):
                for key, value in wave_data.user_metadata.items():
                    corrected_data.add_user_metadata(key, value)
            corrected_data.add_user_metadata('svf_phase_corrected', True)
            corrected_data.add_user_metadata('processed_by', 'PhaseCorrector')
            for record in wave_data.records:
                corrected_record_data = record.data.copy()
                num_channels = corrected_record_data.shape[1]
                num_svf = num_channels // 3
                for svf_idx in range(num_svf):
                    hp_channel = svf_idx * 3 + 0
                    lp_channel = svf_idx * 3 + 2
                    corrected_record_data[:, hp_channel] *= -1
                    corrected_record_data[:, lp_channel] *= -1
                corrected_record = WaveRecord(corrected_record_data, sample_rate=record.sample_rate, channel_names=record.channel_names.copy() if hasattr(record, 'channel_names') else None, record_id=f'{record.record_id}_svf_phase_corrected', creation_date=record.creation_date if hasattr(record, 'creation_date') else None, modified_date=record.modified_date if hasattr(record, 'modified_date') else None, units=record.units if hasattr(record, 'units') else 'V', user_metadata={**(record.user_metadata.copy() if hasattr(record, 'user_metadata') else {}), 'phase_corrected': True, 'svf_phase_correction': True})
                corrected_data.add_record(corrected_record)
            return corrected_data
        except Exception as e:
            logger.info(f'❌ SVF层相位修正失败: {str(e)}')
            return wave_data

    def _is_wavenet5_model(self, model):
        """检查当前模型是否为WaveNet5"""
        return model is not None and hasattr(model, '__class__') and ('wavenet5' in str(model.__class__.__name__).lower())

    def needs_phase_correction(self, model, layer_index):
        """检查指定层是否需要相位修正"""
        return self._is_wavenet5_model(model) and layer_index in [1, 2, 3, 4]