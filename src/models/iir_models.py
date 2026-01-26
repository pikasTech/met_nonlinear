"""
神经网络模型库 - IIR模型模块

此模块包含基于IIR滤波器的模型实现。
"""

import time
import numpy as np
import tensorflow as tf
from models.iirlnrnn import IIR_LNRNN
from experimental.mimoiir import SIMOIIR
from calibration_analyzer.exam_class import TimeSeries, System


class IIR_ONLY(IIR_LNRNN):
    """
    纯IIR模型，不包含额外的神经网络结构
    
    用于线性系统建模或作为非线性模型的基准
    """
    def __init__(
            self,
            iir_params_list,
            features_select: int,
            fs=2000
    ):
        """
        初始化IIR_ONLY模型
        
        Args:
            iir_params_list: IIR滤波器参数列表
            features_select: 选择的特征索引
            fs: 采样频率
        """
        iir = SIMOIIR(
            units=len(iir_params_list),
            a1_list=[iir_param['a1'] for iir_param in iir_params_list],
            a2_list=[iir_param['a2'] for iir_param in iir_params_list],
            b0_list=[iir_param['b0'] for iir_param in iir_params_list],
            b1_list=[iir_param['b1'] for iir_param in iir_params_list],
            b2_list=[iir_param['b2'] for iir_param in iir_params_list],
            fs=fs
        )
        self.iir = iir
        self.model = tf.keras.Sequential()
        self.units = iir.units
        self.model.add(iir)
        self.fs = fs
        self.features_select = features_select
        self.model.build(input_shape=(None, None, 1))

    def time_response(self, time_series: TimeSeries, show_tick=False, batch_size=1000, direct_layer=False) -> TimeSeries:
        """
        计算时间响应
        
        Args:
            time_series: 输入时间序列
            show_tick: 是否显示计时信息
            batch_size: 批处理大小
            direct_layer: 是否直接使用层而不是模型
            
        Returns:
            输出时间序列
        """
        tic = time.time()
        if time_series.fs != self.fs:
            raise ValueError(
                f'输入时间序列的采样频率 {time_series.fs} 与模型的采样频率 {self.fs} 不一致。')

        # 将输入时间序列分批次处理
        samples = np.array(time_series.samples).reshape(1, -1, 1)
        if direct_layer:
            y_pred = self.iir(samples)
        else:
            y_pred = self.model.predict(samples, batch_size=batch_size)

        # 创建 TimeSeries 对象
        ret = TimeSeries(
            y_pred[0, :, self.features_select], time_series.fs)

        toc = time.time()
        if show_tick:
            print(f'IIR_ONLY time response: {toc - tic:.2f} s')
        return ret

    def set_feature_select(self, features_select):
        """
        设置特征选择索引
        
        Args:
            features_select: 特征索引
        """
        self.features_select = features_select

    @classmethod
    def fromSystem(cls,
                  hi_list,
                  features_select,
                  fs=2000,
                  use_debug=False
                  ):
        """
        从系统参数构建IIR模型
        
        Args:
            hi_list: 系统参数列表
            features_select: 特征索引
            fs: 采样频率
            use_debug: 是否开启调试
            
        Returns:
            IIR_ONLY模型实例
        """
        iir_params_list = cls.system2params(
            hi_list, fs)
        if use_debug:
            for i in range(len(hi_list)):
                hi_list[i].plot(label=f'IIR_ONLYH {i}')
        iir_only = cls(iir_params_list,
                     features_select, fs)
        return iir_only


def simple_iir():
    """
    一个简单的IIR模型示例
    
    构建一个包含两个二阶系统的IIR模型并测试其响应
    
    Returns:
        返回测试结果（不明确返回值，函数内部直接可视化）
    """
    s = System.s
    wn1 = 2 * np.pi * 50
    wn2 = 2 * np.pi * 100
    theta1 = 0.1
    theta2 = 0.8
    H1 = System.fromSymbol((wn1**2) / (s**2 + 2 * theta1 * wn1 * s + wn1**2))
    H2 = System.fromSymbol((wn2**2) / (s**2 + 2 * theta2 * wn2 * s + wn2**2))
    iir_only = IIR_ONLY.fromSystem([H2, H1], 0, fs=2000)

    tr_sin = TimeSeries.fromSin(
        A=0.3, f=50, fs=2000, time_length=1, offset=0)
    tr_iir0 = iir_only.time_response(tr_sin)
    fr_iir0 = iir_only.frequency_response_system()
    iir_only.set_feature_select(1)
    tr_iir1 = iir_only.time_response(tr_sin)
    fr_iir1 = iir_only.frequency_response_system()

    H1.plot(time_domin=False)
    H2.plot(time_domin=False)
    fr_iir0.plot()
    fr_iir1.plot()