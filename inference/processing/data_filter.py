"""
数据过滤模块

负责波形数据的过滤和快速模式处理
"""

import logging
from typing import List, Tuple, Optional

from calibration_analyzer.wavedata import WaveData, WaveRecord
from calibration_analyzer.waveprocessor import WaveProcessor

logger = logging.getLogger(__name__)


class DataFilter:
    """数据过滤器类"""
    
    def __init__(self, wave_processor: WaveProcessor, quick_mode: bool = False):
        """
        初始化数据过滤器
        
        参数:
            wave_processor: Wave处理器实例
            quick_mode: 是否使用快速模式
        """
        self.wave_processor = wave_processor
        self.quick_mode = quick_mode
    
    def load_wave_data_with_filter(self, wave_path: str) -> WaveData:
        """
        加载wave数据，支持快速模式筛选
        
        在快速模式下，只加载最小和最大震级的数据
        
        参数:
            wave_path: wave文件路径
            
        返回:
            WaveData: 加载的wave数据，如果是快速模式则只包含最小最大震级
        """
        wave_data = self.wave_processor.load_waveform(wave_path)
        
        if not self.quick_mode:
            return wave_data
        
        # 快速模式：筛选最小最大震级
        filtered_data = self.filter_min_max_magnitude(wave_data)
        return filtered_data
    
    def filter_min_max_magnitude(self, wave_data: WaveData) -> WaveData:
        """
        从wave数据中筛选最小和最大震级的记录
        
        参数:
            wave_data: 原始WaveData对象
            
        返回:
            WaveData: 筛选后的WaveData对象，只包含最小最大震级
        """
        # 获取所有记录的震级信息
        magnitudes = self._extract_magnitudes(wave_data)
        
        if len(magnitudes) < 2:
            # 数据太少，返回原始数据
            logger.warning(
                f"⚠️  数据记录太少({len(magnitudes)}个)，"
                f"无法筛选最小最大震级，返回原始数据"
            )
            return wave_data
        
        # 找出最小和最大震级值
        min_magnitude = min(magnitudes)
        max_magnitude = max(magnitudes)
        
        # 使用WaveData的filter方法筛选记录
        filtered_wave_data = self._apply_magnitude_filter(
            wave_data, min_magnitude, max_magnitude
        )
        
        # 添加筛选信息到元数据
        self._add_filter_metadata(
            filtered_wave_data, wave_data, 
            min_magnitude, max_magnitude
        )
        
        # 记录详细的筛选结果
        self._log_filter_results(
            wave_data, filtered_wave_data, 
            min_magnitude, max_magnitude
        )
        
        return filtered_wave_data
    
    def set_quick_mode(self, enabled: bool):
        """
        设置快速模式
        
        参数:
            enabled: 是否启用快速模式
        """
        self.quick_mode = enabled
        if enabled:
            logger.info("⚡ 快速模式已启用")
        else:
            logger.info("🔄 快速模式已禁用")
    
    def _extract_magnitudes(self, wave_data: WaveData) -> List[float]:
        """从wave数据中提取震级信息"""
        magnitudes = []
        for record in wave_data.records:
            if hasattr(record, 'user_metadata') and 'magnitude' in record.user_metadata:
                magnitudes.append(record.user_metadata['magnitude'])
        return magnitudes
    
    def _apply_magnitude_filter(self, wave_data: WaveData, 
                               min_mag: float, max_mag: float) -> WaveData:
        """应用震级过滤器"""
        return wave_data.filter(
            lambda record: (
                hasattr(record, 'user_metadata') and 
                'magnitude' in record.user_metadata and
                record.user_metadata['magnitude'] in [min_mag, max_mag]
            )
        )
    
    def _add_filter_metadata(self, filtered_data: WaveData, original_data: WaveData,
                           min_mag: float, max_mag: float):
        """添加过滤元数据"""
        filtered_data.user_metadata['quick_mode'] = True
        filtered_data.user_metadata['original_records'] = len(original_data.records)
        filtered_data.user_metadata['filtered_records'] = len(filtered_data.records)
        filtered_data.user_metadata['min_magnitude'] = min_mag
        filtered_data.user_metadata['max_magnitude'] = max_mag
    
    def _log_filter_results(self, original_data: WaveData, filtered_data: WaveData,
                          min_mag: float, max_mag: float):
        """记录过滤结果"""
        # 统计各震级的记录数
        mag_counts = {}
        for record in filtered_data.records:
            if hasattr(record, 'user_metadata') and 'magnitude' in record.user_metadata:
                mag = record.user_metadata['magnitude']
                mag_counts[mag] = mag_counts.get(mag, 0) + 1
        
        # 计算性能提升倍数
        speedup = len(original_data.records) / len(filtered_data.records)
        
        logger.info(f"⚡ 快速模式数据筛选完成:")
        logger.info(f"   原始记录数: {len(original_data.records)}")
        logger.info(f"   筛选后记录数: {len(filtered_data.records)}")
        logger.info(f"   最小震级: {min_mag:.2f} ({mag_counts.get(min_mag, 0)}条记录)")
        logger.info(f"   最大震级: {max_mag:.2f} ({mag_counts.get(max_mag, 0)}条记录)")
        logger.info(f"   预期性能提升: 约 {speedup:.1f} 倍")