"""
测试辅助工具函数
"""
import os
import numpy as np
import tempfile
from pathlib import Path
from typing import Tuple, List, Union, Dict, Any, Optional

class TestDataGenerator:
    """测试数据生成器类"""
    
    @staticmethod
    def generate_sine_wave(
        freq: float = 10.0,
        amp: float = 1.0,
        fs: float = 1000.0,
        time_length: float = 1.0,
        phase: float = 0.0,
        dc_offset: float = 0.0
    ) -> Tuple[np.ndarray, np.ndarray]:
        """生成正弦波信号
        
        参数:
            freq: 频率(Hz)
            amp: 振幅
            fs: 采样率(Hz)
            time_length: 信号长度(秒)
            phase: 相位(弧度)
            dc_offset: 直流偏移量
            
        返回:
            (t, y): 时间数组和信号数组
        """
        t = np.arange(0, time_length, 1/fs)
        y = amp * np.sin(2 * np.pi * freq * t + phase) + dc_offset
        return t, y
    
    @staticmethod
    def generate_square_wave(
        freq: float = 5.0,
        amp: float = 1.0,
        fs: float = 1000.0,
        time_length: float = 1.0,
        duty: float = 0.5,
        dc_offset: float = 0.0
    ) -> Tuple[np.ndarray, np.ndarray]:
        """生成方波信号
        
        参数:
            freq: 频率(Hz)
            amp: 振幅
            fs: 采样率(Hz)
            time_length: 信号长度(秒)
            duty: 占空比(0~1)
            dc_offset: 直流偏移量
            
        返回:
            (t, y): 时间数组和信号数组
        """
        t = np.arange(0, time_length, 1/fs)
        # 使用占空比创建方波
        y = amp * ((t * freq) % 1.0 < duty) * 2 - amp + dc_offset
        return t, y
    
    @staticmethod
    def generate_triangle_wave(
        freq: float = 2.0,
        amp: float = 1.0,
        fs: float = 1000.0,
        time_length: float = 1.0,
        dc_offset: float = 0.0
    ) -> Tuple[np.ndarray, np.ndarray]:
        """生成三角波信号
        
        参数:
            freq: 频率(Hz)
            amp: 振幅
            fs: 采样率(Hz)
            time_length: 信号长度(秒)
            dc_offset: 直流偏移量
            
        返回:
            (t, y): 时间数组和信号数组
        """
        t = np.arange(0, time_length, 1/fs)
        # 创建三角波
        y = amp * (2 * np.abs(2 * ((t * freq) % 1.0) - 1) - 1) + dc_offset
        return t, y
    
    @staticmethod
    def generate_sweep_signal(
        f_start: float = 10.0,
        f_end: float = 100.0,
        amp: float = 1.0,
        fs: float = 1000.0,
        time_length: float = 1.0,
        sweep_type: str = 'linear',
        dc_offset: float = 0.0
    ) -> Tuple[np.ndarray, np.ndarray]:
        """生成扫频信号
        
        参数:
            f_start: 起始频率(Hz)
            f_end: 结束频率(Hz)
            amp: 振幅
            fs: 采样率(Hz)
            time_length: 信号长度(秒)
            sweep_type: 'linear'或'log'，分别表示线性扫频和对数扫频
            dc_offset: 直流偏移量
            
        返回:
            (t, y): 时间数组和信号数组
        """
        t = np.arange(0, time_length, 1/fs)
        
        if sweep_type.lower() == 'linear':
            # 线性扫频
            k = (f_end - f_start) / time_length  # 频率变化率
            phase = 2 * np.pi * (f_start * t + 0.5 * k * t * t)
            y = amp * np.sin(phase) + dc_offset
        
        elif sweep_type.lower() == 'log':
            # 对数扫频
            if f_start <= 0 or f_end <= 0:
                raise ValueError("对数扫频的频率必须为正数")
                
            k = np.exp(np.log(f_end / f_start) / time_length)
            phase = 2 * np.pi * f_start * ((k**t - 1) / np.log(k))
            y = amp * np.sin(phase) + dc_offset
        
        else:
            raise ValueError(f"不支持的扫频类型: {sweep_type}")
        
        return t, y
    
    @staticmethod
    def generate_noise(
        amp: float = 0.1,
        fs: float = 1000.0,
        time_length: float = 1.0,
        noise_type: str = 'white',
        dc_offset: float = 0.0
    ) -> Tuple[np.ndarray, np.ndarray]:
        """生成噪声信号
        
        参数:
            amp: 振幅(噪声强度)
            fs: 采样率(Hz)
            time_length: 信号长度(秒)
            noise_type: 'white'(白噪声)或'pink'(粉噪声)
            dc_offset: 直流偏移量
            
        返回:
            (t, y): 时间数组和信号数组
        """
        t = np.arange(0, time_length, 1/fs)
        samples = int(fs * time_length)
        
        if noise_type.lower() == 'white':
            # 白噪声
            y = amp * np.random.randn(samples) + dc_offset
            
        elif noise_type.lower() == 'pink':
            # 粉噪声(近似实现)
            white_noise = np.random.randn(samples)
            # 使用简单滤波器创建粉噪声的近似
            b = np.array([0.049922035, -0.095993537, 0.050612699, -0.004408786])
            a = np.array([1, -2.494956002, 2.017265875, -0.522189400])
            y = amp * np.zeros_like(white_noise)
            for i in range(1, len(white_noise)):
                y[i] = white_noise[i] - b[1]*white_noise[i-1]
                if i > 1:
                    y[i] -= b[2]*white_noise[i-2]
                if i > 2:
                    y[i] -= b[3]*white_noise[i-3]
                if i > 0:
                    y[i] += a[1]*y[i-1]
                if i > 1:
                    y[i] += a[2]*y[i-2]
                if i > 2:
                    y[i] += a[3]*y[i-3]
            y += dc_offset
            
        else:
            raise ValueError(f"不支持的噪声类型: {noise_type}")
        
        return t, y
    
    @staticmethod
    def create_temp_file(extension: str = '.txt') -> Tuple[str, str]:
        """创建临时文件
        
        参数:
            extension: 文件扩展名
            
        返回:
            (temp_dir, temp_file): 临时目录路径和临时文件路径
        """
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, f"temp{extension}")
        return temp_dir, temp_file
    
    @staticmethod
    def cleanup_temp_file(temp_dir: str, temp_file: str) -> None:
        """清理临时文件
        
        参数:
            temp_dir: 临时目录路径
            temp_file: 临时文件路径
        """
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
            os.rmdir(temp_dir)
        except (FileNotFoundError, PermissionError) as e:
            print(f"清理临时文件失败: {e}")


def create_test_waveform(freq: float = 10.0, amp: float = 1.0, fs: float = 1000.0, time_length: float = 1.0) -> np.ndarray:
    """创建测试波形(简化版)
    
    参数:
        freq: 频率(Hz)
        amp: 振幅
        fs: 采样率(Hz)
        time_length: 信号长度(秒)
        
    返回:
        波形数据数组
    """
    _, y = TestDataGenerator.generate_sine_wave(freq, amp, fs, time_length)
    return y 