"""
频率配置统一管理器 - 简化单模式设计

实现统一的频率范围配置管理，支持：
- 传统range(6, n-4)逻辑（默认向后兼容）
- Hz范围自动计算频率索引
- 详细的配置应用日志
"""

import logging
import numpy as np


class FreqConfigManager:
    """频率配置统一管理器 - 简化单模式设计"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_freq_indices(self, config, freq_list, n_total):
        """获取频率索引范围（主要方法）
        
        Args:
            config: 项目配置对象
            freq_list: 频率列表 [Hz]
            n_total: 总频率点数
            
        Returns:
            range对象: 频率索引范围
        """
        # 检查是否配置了dataset.freq_range_hz
        dataset_config = getattr(config, 'dataset', {})
        freq_range_hz = dataset_config.get('freq_range_hz')
        
        if freq_range_hz is not None:
            # 配置了Hz范围，自动计算索引
            return self._calculate_from_hz_range(freq_range_hz, freq_list)
        else:
            # 未配置，使用传统range(6, n-4)逻辑
            return self._get_legacy_range(n_total)
    
    def _calculate_from_hz_range(self, freq_range_hz, freq_list):
        """根据Hz范围自动计算频率索引
        
        Args:
            freq_range_hz: [min_hz, max_hz] 频率范围
            freq_list: 频率列表
            
        Returns:
            range对象: 计算得出的频率索引范围
        """
        min_hz, max_hz = freq_range_hz
        freq_array = np.array(freq_list)
        
        # 找到范围内的频率索引
        valid_indices = np.where((freq_array >= min_hz) & (freq_array <= max_hz))[0]
        
        if len(valid_indices) == 0:
            self.logger.warning(f"配置的频率范围{min_hz}-{max_hz}Hz在数据集中找不到对应点，回退到传统方式")
            return self._get_legacy_range(len(freq_list))
        
        start_idx = valid_indices[0]
        end_idx = valid_indices[-1] + 1
        
        self.logger.info(f"检测到dataset.freq_range_hz配置: [{min_hz}, {max_hz}]Hz")
        self.logger.info(f"数据集频率范围: {freq_array[0]:.1f}Hz - {freq_array[-1]:.1f}Hz (共{len(freq_list)}个频率点)")
        self.logger.info(f"计算得出频率索引范围: range({start_idx}, {end_idx})")
        self.logger.info(f"有效频率点数: {end_idx-start_idx} (从{freq_array[start_idx]:.1f}Hz到{freq_array[end_idx-1]:.1f}Hz)")
        
        return range(start_idx, end_idx)
    
    def _get_legacy_range(self, n_total):
        """传统range(6, n-4)逻辑
        
        Args:
            n_total: 总频率点数
            
        Returns:
            range对象: 传统的频率索引范围
        """
        result = range(6, n_total - 4)
        self.logger.info(f"未配置dataset.freq_range_hz，使用传统range(6, {n_total-4})")
        self.logger.info(f"传统频率配置: 跳过前6个和后4个频率点")
        return result


# 单例实例，方便全局使用
freq_config_manager = FreqConfigManager()