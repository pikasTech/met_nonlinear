import tensorflow as tf
from typing import Tuple
from tfkan.layers.base import PiecewiseActivationLayer
from experimental.mimoiir import DIAGIIR
from typing import List
from datetime import datetime
import math
from calibration_analyzer import config
import re
import os
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from calibration_analyzer.exam_class import System, TimeSeries
from calibration_analyzer.exam_process import find_data_info
from calibration_analyzer import exam_process, exam_class
from core.data_processing import pre_process_data_M50, pre_process_data


class IIR_LRNN:
    def __init__(self, a1=0.0, a2=0.0, b0=0.1, b1=0.2, b2=0.3, learning_rate=0.1, trainable=True, fs=2000):
        # 定义滤波器初始系数
        self.a1 = a1
        self.a2 = a2
        self.b0 = b0
        self.b1 = b1
        self.b2 = b2
        self.fs = fs

        # 定义状态空间矩阵
        self.A = np.array([
            [-a1, -a2, b1, b2],
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0]
        ], dtype=np.float32)

        self.B = np.array([
            [b0],
            [0.0],
            [1.0],
            [0.0]
        ], dtype=np.float32)

        # 输出矩阵，直接输出状态向量的第一个元素 h_1[n] = y[n]
        self.C = np.array([[1.0, 0.0, 0.0, 0.0]], dtype=np.float32)
        self.D = np.array([[0.0]], dtype=np.float32)  # D 为零

        # 转置矩阵以匹配 TensorFlow 的权重形状
        W_hh = self.A.T  # 形状：(4, 4)
        W_xh = self.B.T  # 形状：(1, 4)

        # 构建 Sequential 模型
        self.model = tf.keras.Sequential()

        # 添加 RNN 层
        self.model.add(tf.keras.layers.SimpleRNN(
            units=4,
            activation='linear',
            use_bias=False,
            return_sequences=True,
            input_shape=(None, 1),
            trainable=trainable
        ))

        # 添加 Dense 层 直接输出 y[n] = h[n+1][0]
        self.model.add(tf.keras.layers.Dense(
            1, activation=None, use_bias=False, trainable=False))

        # 设置权重
        self.model.layers[0].set_weights([W_xh, W_hh])
        self.model.layers[1].set_weights([self.C.T])

        # 编译模型
        optimizer = tf.keras.optimizers.SGD(learning_rate=learning_rate)
        self.model.compile(optimizer=optimizer, loss='mse')

    def train(self, x_input, output_target, epochs=100):
        # 在 x_input 前补一个零，并去除最后一个时间步
        # Shape: (batch_size, time_steps, 1)

        # 训练模型
        history = self.model.fit(
            x_input, output_target, epochs=epochs, verbose=1)
        return history

    def predict(self, x_input, batch_size=1000, **kwargs):
        # 使用训练后的模型进行预测
        y_pred = self.model.predict(x_input, batch_size=batch_size, **kwargs)
        return y_pred

    def plot_weights(self):
        # 绘制输出比较
        # 打印各个层的权重
        print('RNN 层权重：')
        print(self.model.layers[0].get_weights())
        print('Dense 层权重：')
        print(self.model.layers[1].get_weights())

    @classmethod
    def fromSystem(cls, system: System, fs=2000, learning_rate=0.1, trainable=True):
        # 从系统对象创建 IIR-LRNN 模型
        b0, b1, b2, a0, a1, a2 = system.get_iir_parameters(fs)
        return cls(a1=a1, a2=a2, b0=b0, b1=b1, b2=b2, learning_rate=learning_rate, trainable=trainable, fs=fs)

    def time_response(self, time_series: exam_class.TimeSeries, show_tick=False, batch_size=1000) -> exam_class.TimeSeries:
        tic = time.time()
        if time_series.fs != self.fs:
            raise ValueError(
                f'输入时间序列的采样频率 {time_series.fs} 与模型的采样频率 {self.fs} 不一致。')
        # 计算时间响应
        x_input = np.array(time_series.samples).reshape(1, -1, 1)
        y_pred = self.predict(x_input, batch_size=batch_size)
        ret = exam_class.TimeSeries(y_pred[0, :, 0], time_series.fs)
        toc = time.time()
        if show_tick:
            print(f'rnn time response: {toc - tic:.2f} s')
        return ret

    def frequency_response_system(self, time_length=10, f_range=(5, 250), points=50, use_parallel=False, amplitude=1.0):
        fs = self.fs
        system = System.frequency_response_from_time_domain(
            self, fs, time_length, f_range=f_range, points=points, use_parallel=use_parallel, amplitude=amplitude)
        return system


class IIR_LNRNN(IIR_LRNN):
    def __init__(self, nonlinear_params_list, nonlinear_functions, learning_rate=0.1, Hammerstein=False):
        # 初始化非线性部分（多个 IIR-LRNN）
        self.nonlinear_rnns: List[IIR_LRNN] = []
        for params in nonlinear_params_list:
            rnn = IIR_LRNN(**params, trainable=False)
            self.nonlinear_rnns.append(rnn)

        # 非线性函数列表 f_i
        self.nonlinear_functions = nonlinear_functions

        # # 非线性部分的可训练权重 w_i
        # self.w_i = [tf.Variable(1.0, trainable=True, dtype=tf.float32)
        #             for _ in self.nonlinear_rnns]

        if self.nonlinear_functions is not None:
            # 使用 Functional API 构建模型
            inputs = tf.keras.Input(shape=(None, 1))

            # 非线性部分输出
            nonlinear_outputs = []
            for i, rnn in enumerate(self.nonlinear_rnns):
                if not Hammerstein:
                    # Weienr 模型
                    # 获取第 i 个 IIR_LRNN 的输出
                    rnn_output = rnn.model(inputs)
                    # 应用非线性函数 f_i
                    nonlinear_output = self.nonlinear_functions[i](rnn_output)
                    # 乘以可训练权重 w_i
                    nonlinear_outputs.append(nonlinear_output)
                else:
                    nonlinear_output = self.nonlinear_functions[i](inputs)
                    rnn_output = rnn.model(nonlinear_output)
                    nonlinear_outputs.append(nonlinear_output)

            # 非线性输出的总和
            total_output = tf.keras.layers.Add()(nonlinear_outputs)

            # 创建模型
            self.model = tf.keras.Model(inputs=inputs, outputs=total_output)

            # 编译模型
            optimizer = tf.keras.optimizers.SGD(learning_rate=learning_rate)
            self.model.compile(optimizer=optimizer, loss='mse')
            self.Hammerstein = Hammerstein

    @classmethod
    def fromSystem(cls, nonlinear_systems: list, nonlinear_functions: list, fs, learning_rate=0.1, Hammerstein=False):
        nonlinear_params_list = cls.system2params(
            nonlinear_systems, fs)

        lnrnn = cls(nonlinear_params_list=nonlinear_params_list,
                    nonlinear_functions=nonlinear_functions, learning_rate=learning_rate, Hammerstein=Hammerstein)
        lnrnn.fs = fs
        return lnrnn

    @staticmethod
    def system2params(nonlinear_systems: list, fs):
        # 从系统对象创建 IIR-LNRNN 模型
        if nonlinear_systems is None:
            return None
        nonlinear_params_list = []
        for system in nonlinear_systems:
            b0, b1, b2, a0, a1, a2 = system.get_iir_parameters(fs)
            params = {
                'a1': a1,
                'a2': a2,
                'b0': b0,
                'b1': b1,
                'b2': b2,
            }
            nonlinear_params_list.append(params)
        return nonlinear_params_list

    def train(self, x_input, output_target, epochs=100):
        # 训练模型
        history = self.model.fit(
            x_input, output_target, epochs=epochs, verbose=1)
        return history

    def plot_weights(self):
        # 打印非线性部分的权重 w_i
        print('非线性部分的权重 w_i：')
        for i, w in enumerate(self.w_i):
            print(f'w_{i}: {w.numpy()}')

    def set_weights(self, weights):
        # 设置非线性部分的权重 w_i
        for i, w in enumerate(weights):
            self.w_i[i].assign(w)

    def extract_features_time_response(self, x_input: exam_class.TimeSeries, batch_size=1000) -> list[exam_class.TimeSeries]:
        """
        将输入 x_input 通过每一个 LRNN 子系统，得到一组特征。
        返回值为一个列表，每个元素对应一个子系统的输出特征。
        """
        features = []

        # 非线性部分输出
        for i, rnn in enumerate(self.nonlinear_rnns):
            rnn_output = rnn.time_response(x_input, batch_size=batch_size)
            # 将结果添加到特征列表
            features.append(rnn_output)

        return features

    def extract_features(self, x_input: exam_class.TimeSeries, batch_size=1000) -> np.ndarray:
        x_input_reshape = np.array(x_input.samples).reshape(1, -1, 1)
        features = []
        if self.linear_rnn is not None:
            linear_feature = self.linear_rnn.predict(
                x_input_reshape, batch_size=batch_size)
            linear_feature = linear_feature[0, :, 0]
            features.append(linear_feature)
        for i, rnn in enumerate(self.nonlinear_rnns):
            rnn_output = rnn.predict(x_input_reshape, batch_size=batch_size)
            rnn_output = rnn_output[0, :, 0]
            features.append(rnn_output)

        # feature 是一个 (batch_size, 1) 的列表
        # 多个 feature 组成一个 (batch_size, feature_num) 的特征向量
        features = np.array(features).T
        return features


class IIR_LNRNN_Compensator(IIR_LNRNN):
    def __init__(self, lnrnn, n):
        self.n = n  # 要恢复的非线性分量的索引
        self.w_i = lnrnn.w_i  # 使用与原模型相同的权重

        """
        生成一个补偿器模型，用于从 IIR_LNRNN 模型的输出中恢复线性分量 h_n。
        """

        # 定义补偿器的输入：估计的输入和实际的模型输出
        input_estimate = tf.keras.Input(shape=(None, 1), name='input_estimate')
        real_output = tf.keras.Input(shape=(None, 1), name='real_output')

        # 计算线性部分 h_0
        h_0_output = lnrnn.linear_rnn.model(input_estimate)

        # 初始化列表
        f_i_outputs = []
        h_n_output = None
        f_n = None

        # 计算非线性部分的输出 f_i(h_i)，但排除第 n 个分量
        for i, (rnn, func) in enumerate(zip(lnrnn.nonlinear_rnns, lnrnn.nonlinear_functions)):
            h_i_output = rnn.model(input_estimate)
            if i == self.n:
                # 保存 h_n 和对应的非线性函数 f_n
                h_n_output = h_i_output
                f_n = func
            else:
                # 计算 f_i(h_i)
                f_i_output = func(h_i_output)
                # 乘以可训练权重 w_i
                weighted_output = tf.keras.layers.Lambda(
                    lambda x, w=lnrnn.w_i[i]: x * w)(f_i_output)
                f_i_outputs.append(weighted_output)

        # 计算 sum f_i(h_i) for i != n
        if len(f_i_outputs) > 1:
            sum_f_i = tf.keras.layers.Add()(f_i_outputs)
        elif len(f_i_outputs) == 1:
            sum_f_i = f_i_outputs[0]
        else:
            # 如果没有其他非线性分量，sum_f_i 为零张量
            sum_f_i = tf.keras.layers.Lambda(lambda x: 0.0 * x)(h_0_output)

        # 计算总的非线性和线性输出 sum_h0_fi = h_0 + sum f_i(h_i) for i != n
        sum_h0_fi = tf.keras.layers.Add()([h_0_output, sum_f_i])

        # 计算残差 residual = real_output - sum_h0_fi = f_n(h_n)
        residual = tf.keras.layers.Subtract()([real_output, sum_h0_fi])

        # 应用逆非线性函数 f_n^{-1} 来恢复 h_n
        if hasattr(f_n, 'reverse'):
            f_n_inverse = f_n.reverse()
            h_n = f_n_inverse(residual)
        else:
            raise NotImplementedError(
                "Nonlinear function does not have a reverse() method.")

        # 创建补偿器模型，输入为 [input_estimate, real_output]
        self.model = tf.keras.Model(
            inputs=[input_estimate, real_output], outputs=h_n)

    def predict(self, input_estimate, real_output, batch_size=1000, **kwargs):
        # 使用补偿器模型进行预测
        y_pred = self.model.predict(
            [input_estimate, real_output], batch_size=batch_size, **kwargs)
        return y_pred

    def time_response(self,
                      real_output_series: exam_class.TimeSeries, input_estimate: exam_class.TimeSeries,
                      show_tick=False,
                      batch_size=1000) -> exam_class.TimeSeries:
        tic = time.time()
        # 计算时间响应
        input_estimate_reshape = np.array(
            input_estimate.samples).reshape(1, -1, 1)
        real_output_reshape = np.array(
            real_output_series.samples).reshape(1, -1, 1)
        y_pred = self.predict(input_estimate_reshape,
                              real_output_reshape, batch_size=batch_size)
        ret = exam_class.TimeSeries(y_pred[0, :, 0], input_estimate.fs)
        toc = time.time()
        if show_tick:
            print(f'compensator time response: {toc - tic:.2f} s')
        return ret


def cubic_activation(x):
    """Custom activation function: x^3."""
    return tf.pow(x, 3)


class CubicActivationLayer(tf.keras.layers.Layer):
    """Custom Keras Layer for cubic activation."""

    def call(self, inputs):
        return cubic_activation(inputs)


def base_example():
    fs = 2000
    time_length = 10

    s = System.s
    f0 = 10
    delta = 0.1  # 阻尼比
    omega_n = 2 * np.pi * f0
    f = np.logspace(math.log10(1), math.log10(200), 50)  # 1 Hz 到 200 Hz

    # 原始线性系统 h
    h = System.fromSymbol(
        53382.00 * s / (s ** 2 + 624.82 * s + 56715.23),
        f=f)

    # 创建非线性部分的参数
    # 中心频率为 80Hz 的系统
    f1 = 80
    omega_n1 = 2 * np.pi * f1
    h1 = System.fromSymbol(
        s / (s ** 2 + 2 * delta * omega_n1 * s + omega_n1**2),
        f=f)

    # 中心频率为 110Hz 的系统
    f2 = 110
    omega_n2 = 2 * np.pi * f2
    h2 = System.fromSymbol(
        s / (s ** 2 + 2 * delta * omega_n2 * s + omega_n2**2),
        f=f)

    # 创建 IIR_LNRNN 模型实例
    iir_lnrnn_model = IIR_LNRNN.fromSystem(
        linear_system=h,
        nonlinear_systems=[
            # h1,
            h2
        ],
        nonlinear_functions=[
            # CubicActivationLayer(),
            PiecewiseActivationLayer.from_xk([0.01, 2.0], [0.01, 2]),
        ],
        fs=fs,
        learning_rate=0.1
    )

    # 手动赋值组合权重 w_i
    # manual_weights = [0.5, 1.0]  # 例子：w_0 = 0.5, w_1 = -0.3
    manual_weights = [100000.0]  # 例子：w_0 = 0.5, w_1 = -0.3
    iir_lnrnn_model.set_weights(manual_weights)

    # 生成输入信号
    tr_sin = exam_class.TimeSeries.fromSin(1, 10, fs, time_length)
    x_input = np.array(tr_sin.samples).reshape(1, -1, 1)

    # 使用模型进行预测
    y_pred = iir_lnrnn_model.predict(x_input, batch_size=1000)[0, :, 0]
    tr_pred = exam_class.TimeSeries(y_pred, fs)

    # 原始系统的输出
    tr_h = h.time_response(tr_sin)

    # 查看非线性部分的权重
    iir_lnrnn_model.plot_weights()

    def plot_system():
        system_h = h.frequency_response_system(
            fs, time_length, f_range=(1, 200), points=50)
        # 计算频率响应
        lnrnn_system_A1 = iir_lnrnn_model.frequency_response_system(
            fs=fs, time_length=10, f_range=(1, 200), points=50, amplitude=10)

        lnrnn_system_A2 = iir_lnrnn_model.frequency_response_system(
            fs=fs, time_length=10, f_range=(1, 200), points=50, amplitude=20)

        lnrnn_system_A3 = iir_lnrnn_model.frequency_response_system(
            fs=fs, time_length=10, f_range=(1, 200), points=50, amplitude=30.0)

        lnrnn_system_A4 = iir_lnrnn_model.frequency_response_system(
            fs=fs, time_length=10, f_range=(1, 200), points=50, amplitude=40.0)

        # 绘制频率响应
        lnrnn_system_A1.plot()
        lnrnn_system_A2.plot()
        lnrnn_system_A3.plot()
        lnrnn_system_A4.plot()
        # h.plot()
        system_h.plot()

    def plot_time_response():
        # 绘制时间响应
        tr_sin = exam_class.TimeSeries.fromSin(1, 110, fs, 0.1)
        tr_pred = iir_lnrnn_model.time_response(tr_sin)
        tr_h = h.time_response(tr_sin)
        tr_h.plot()
        tr_pred.plot(line_style='--')


def plot_2freq_combination():
    f = np.logspace(math.log10(5), math.log10(200), 50)  # 1 Hz 到 200 Hz
    fs = 20000
    s = System.s
    # 定义两个不同的自然频率
    omega_n1 = 2 * np.pi * 30
    omega_n2 = 2 * np.pi * 40
    delta = 1.31

    # 手动归一化增益，以保持相同的谐振峰值
    gain1 = omega_n1**2
    gain2 = omega_n2**2

    # 定义两个系统，并将增益应用于传递函数
    h0 = System.fromSymbol(
        gain1 * s / (s ** 2 + 2 * delta * omega_n1 * s + omega_n1**2),
        f=f)
    h1 = System.fromSymbol(
        gain2 * s / (s ** 2 + 2 * delta * omega_n2 * s + omega_n2**2),
        f=f)

    # 绘制频率响应
    h0.plot(label='h0', marker='x')
    h1.plot(label='h1', marker='x')
    # h0.plot(time_domin=True)
    # h1.plot(time_domin=True)

    fh0 = PiecewiseActivationLayer.from_xk(
        [1.0, 1.2, 1.4, 1.6, 1.8, 2.0],
        [1, 0.8, 0.6, 0.4, 0.2, 0.0])
    fh1 = PiecewiseActivationLayer.from_xk(
        [1.0, 1.2, 1.4, 1.6, 1.8, 2.0],
        [0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    lnrnn = IIR_LNRNN.fromSystem(
        nonlinear_systems=[h0, h1],
        nonlinear_functions=[fh0, fh1],
        fs=fs,
        learning_rate=0.1
    )
    A_list = [0.01, 0.011, 0.012, 0.013, 0.015,
              0.02, 0.04, 0.05, 0.1, 0.2, 0.5, 1]
    t = 0.2
    tr_sin_base = exam_class.TimeSeries.fromSin(1, 30, fs, t)
    # tr_h0 = h0.time_response(tr_sin_base)
    # tr_h1 = h1.time_response(tr_sin_base)
    # tr_h0.plot()
    # tr_h1.plot()
    plot_time_response = False
    for A in A_list:
        if plot_time_response:
            tr_sin = exam_class.TimeSeries.fromSin(A, 30, fs, t)
            tr_lnrnn = lnrnn.time_response(tr_sin).apply_gain(1/A)
            # tr_lnrnn.plot(line_style='--', marker='x', label=f'lnrnn-A{A:.3f}')
            tr_lnrnn.plot(label=f'lnrnn-A{A:.3f}')
        else:
            lnrnn_system = lnrnn.frequency_response_system(
                fs=fs, time_length=1, f_range=(5, 200), points=50, amplitude=A, use_parallel=False)
            lnrnn_system.plot(label=f'lnrnn-A{A:.3f}')


def simulation_and_compentation():
    data_info_list = find_data_info("data/M50")
    for data_info in data_info_list:
        print(data_info)

    # 只取x.n，其中n是双数的数据，例如0.2, 0.4...
    data_info_list = [data_info_list[i]
                      for i in range(1, len(data_info_list), 2)]

    # plot_time_response()
    # plot_system()
    # plot_2freq_combination()

    # 去掉前10个数据
    # data_info_list = data_info_list[10:]

    # for data_info in data_info_list:
    #     system = System.loadFile(data_info.file_path)
    #     system.plot(label=f"震级{data_info.magnitude:.2f}",
    #                 markersize=2, legend=False, freq_range=(10, 200), gain_range=(30, 250))

    # 取第一个数据
    ws = System.loadFile(data_info_list[0].file_path)
    ws_fit = exam_process.ws_system_fit(ws, k=1.0, freq_range=(5, 200))

    ws2 = System.loadFile(data_info_list[10].file_path)
    ws2_fit = exam_process.ws_system_fit(ws2, k=1.0, freq_range=(5, 200))
    ws_comp = exam_class.ws_compensator(ws2_fit, ws_fit)
    sys_one = System.fromSymbol(1)

    fh0 = PiecewiseActivationLayer.from_xk(
        [1.0, 1.2, 1.4, 1.6, 1.8, 2.0],
        [1, 0.8, 0.6, 0.4, 0.2, 0.00])
    fh1 = PiecewiseActivationLayer.from_xk(
        [1.0, 1.2, 1.4, 1.6, 1.8, 2.0],
        [0.00, 0.2, 0.4, 0.6, 0.8, 1.0])

    lnrnn = IIR_LNRNN.fromSystem(
        [ws_fit, ws2_fit], [fh0, fh1], fs=20000, Hammerstein=False)

    lnrnn_comp_one = IIR_LNRNN.fromSystem(
        [sys_one, sys_one], [fh0, fh1], fs=20000, Hammerstein=True)

    lnrnn_comp = IIR_LNRNN.fromSystem(
        [sys_one, ws_comp], [fh0, fh1], fs=20000, Hammerstein=True)

    lrnn_comp_one = IIR_LRNN.fromSystem(sys_one, fs=20000)

    lnrnn_comped = exam_class.TimeDomainSystem.cascade_system2(
        lnrnn, lnrnn_comp)

    lnrnn_cascaded_one = exam_class.TimeDomainSystem.cascade_system2(
        lnrnn, sys_one)

    lnrnn_comped_one = exam_class.TimeDomainSystem.cascade_system2(
        lnrnn, lnrnn_comp_one)

    t = 0.2
    tr_sin_base = exam_class.TimeSeries.fromSin(1, 30, 20000, t)
    tr_sin_small = exam_class.TimeSeries.fromSin(0.01, 30, 20000, t)
    # tr_sin_bios = exam_class.TimeSeries.fromSin(0.9, 30, 20000, t)
    tr_lnrnn = lnrnn.time_response(tr_sin_base)
    tr_h1 = ws_fit.time_response(tr_sin_base)
    tr_h2 = ws2_fit.time_response(tr_sin_base)
    tr_ws_comp = ws_comp.time_response(tr_sin_base)
    tr_lnrnn_comped_splite = lnrnn_comp_one.time_response(tr_lnrnn)
    tr_lnrnn_comped = lnrnn_comped.time_response(tr_sin_base)
    # tr_one = sys_one.time_response(tr_sin_base)
    tr_lnrnn_small = lnrnn.time_response(tr_sin_small)
    tr_lnrnn_one_small = lnrnn_cascaded_one.time_response(tr_sin_small)
    tr_one = sys_one.time_response(tr_sin_base)
    tr_one_lnrnn = lnrnn_comp_one.time_response(tr_sin_base)
    tr_one_lrnn = lrnn_comp_one.time_response(tr_sin_base)
    # tr_h1_bios = ws_fit.time_response(tr_sin_bios)

    # tr_lnrnn_comp.plot()
    # 频率响应
    # ws_fit.plot(label=f"拟合震级{data_info.magnitude:.2f}", markersize=2)
    # ws2_fit.plot(label=f"拟合震级{data_info_list[10].magnitude:.2f}",
    #              markersize=2)
    # ws_comp.plot(label=f"震级{data_info.magnitude:.2f}")

    # 时域响应
    if 0:
        tr_h1.plot(label='h1')
        tr_h2.plot(label='h2')
        tr_lnrnn.plot(label='lnrnn', line_style='--')
        tr_lnrnn_comped_splite.plot(
            label='lnrnn_comped_splite', line_style='--')
        tr_lnrnn_comped.plot(label='lnrnn_comped',
                             line_style='', marker='x', markersize=4)
    # tr_sin_small.plot(label='sin')
    # tr_one_small.plot(label='one')
    # tr_ws_comp.plot(label='ws_comp')
    # tr_one.plot(label='one')

    # tr_lnrnn.plot()
    # tr_h1.plot(label='h1')
    # tr_h1_bios.plot(line_style='--', label='h1_bios')
    # tr_lnrnn_comp.plot(line_style='--')

    if 0:
        tr_one.plot(label='one')
        tr_one_lnrnn.plot(label='one_lnrnn', line_style='--')
        tr_one_lrnn.plot(label='one_lrnn', line_style='--')

    # 批量处理 A_list 中的每个振幅值
    if 1:
        # A_list = [1, 20, 50]
        # A_list = np.logspace(np.log10(100), np.log10(20000), 10)
        A_list = np.logspace(np.log10(1), np.log10(50), 10)
        # A_list = np.linspace(100, 20000, 5)
        for A in A_list:
            lnrnn_system = lnrnn.frequency_response_system(
                fs=20000, time_length=1, f_range=(5, 200), points=50, amplitude=A, use_parallel=False
            )
            lnrnn_system.plot(
                label=f'lnrnn-A{A:.3f}', markersize=0)
        if 1:
            for A in A_list:
                lnrnn_comped_system = lnrnn_comped.frequency_response_system(
                    fs=20000, time_length=1, f_range=(5, 200), points=50, amplitude=A, use_parallel=False
                )
                lnrnn_comped_system.plot(
                    label=f'lnrnn_comped-A{A:.3f}', linestyle='', marker='x', markersize=4)
        # for A in A_list:
        #     lnrnn_comp_system = sys_one.frequency_response_system(
        #         fs=20000, time_length=1, f_range=(5, 200), points=50, amplitude=A, use_parallel=False
        #     )
        #     lnrnn_comp_system.plot(
        #         label=f'sys_one-A{A:.3f}', markersize=4, marker='x', linestyle='--')
        # for A in A_list:
        #     lnrnn_one_system = lnrnn_comp_one.frequency_response_system(
        #         fs=20000, time_length=1, f_range=(5, 200), points=50, amplitude=A, use_parallel=False
        #     )
        #     lnrnn_one_system.plot(
        #         label=f'lnrnn_one-A{A:.3f}', markersize=4, marker='x', linestyle='')

    # # 绘制 ws_fit 和 ws 的响应
    # ws_fit.plot(label=f"拟合震级{data_info.magnitude:.2f}", markersize=2)
    # ws.plot(label=f"震级{data_info.magnitude:.2f}",
    #         freq_range=(10, 200), gain_range=(30, 250))

    # # 绘制 ws2_fit 和 ws2 的响应
    # ws2_fit.plot(label=f"拟合震级{data_info_list[10].magnitude:.2f}", markersize=2)
    # ws2.plot(label=f"震级{data_info_list[10].magnitude:.2f}", freq_range=(
    #     10, 200), gain_range=(30, 250))

    # 显示图表
    plt.show()


def compensate_with_real_data(
        model_comp,
        data_info_list,
        index_list,
        freq_range=(5, 200),
        gain_range=(30, 250)
):
    systems_data = []
    inputs_data = []
    outputs_data = []
    freqs_list = []
    outputs_data_comped_list = []
    systems_comped_list = []

    for index in index_list:
        system_data, input_data, output_data, freq_list = pre_process_data_M50(
            data_info_list, index)
        systems_data.append(system_data)
        inputs_data.append(input_data)
        outputs_data.append(output_data)
        freqs_list.append(freq_list)
        output_data_comped = [model_comp.time_response(output_item)
                              for output_item in output_data]
        outputs_data_comped_list.append(output_data_comped)
        system_comped = System.fromTimeSeries(
            input_data, output_data_comped, frequencies=freq_list, use_parallel=False)
        systems_comped_list.append(system_comped)

    # Plotting the systems
    for idx, index in enumerate(index_list):
        system_data = systems_data[idx]
        system_comped = systems_comped_list[idx]
        magnitude = data_info_list[index].magnitude
        system_data.plot(
            markersize=0, label=f'实际震级{magnitude:.2f}')
        system_comped.plot(linestyle='--', marker='x',
                           markersize=4, label=f'实际震级{magnitude:.2f}（补偿后）', freq_range=freq_range, gain_range=gain_range)


def compensator_real_data():
    data_info_list = find_data_info("data/M50")
    for data_info in data_info_list:
        print(data_info)

    data_info_list = [data_info_list[i]
                      for i in range(1, len(data_info_list), 2)]

    ws = System.loadFile(data_info_list[0].file_path)
    ws_fit = exam_process.ws_system_fit(ws, k=1.0, freq_range=(5, 200))

    ws2 = System.loadFile(data_info_list[10].file_path)
    ws2_fit = exam_process.ws_system_fit(ws2, k=1.0, freq_range=(5, 200))
    sys_one = System.fromSymbol(1)
    ws_comp = exam_class.ws_compensator(ws2_fit, ws_fit)

    # Define the activation functions (same as before)
    if 0:
        fh0 = PiecewiseActivationLayer.from_xk(
            [1.0, 1.2, 1.4, 1.6, 1.8, 2.0],
            [1, 0.8, 0.6, 0.4, 0.2, 0.0])
        fh1 = PiecewiseActivationLayer.from_xk(
            [1.0, 1.2, 1.4, 1.6, 1.8, 2.0],
            [0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    elif 1:  # hammerstein
        fh0 = PiecewiseActivationLayer.from_xk(
            list(np.linspace(0.5, 1.2, 6)),
            list(np.linspace(1.0, 0, 6)))
        fh1 = PiecewiseActivationLayer.from_xk(
            list(np.linspace(0.5, 1.2, 6)),
            list(np.linspace(0.0, 1.0, 6)))
    else:  # weiner
        fh0 = PiecewiseActivationLayer.from_xk(
            list(np.linspace(1.0, 1.5, 6)),
            list(np.linspace(1.0, 0, 6)))
        fh1 = PiecewiseActivationLayer.from_xk(
            list(np.linspace(1.0, 1.5, 6)),
            list(np.linspace(0.0, 1.0, 6)))

    lnrnn_comp = IIR_LNRNN.fromSystem(
        [sys_one, ws_comp], [fh0, fh1], fs=2000, Hammerstein=True)

    # Define process_data function (same as before)

    # Refactored code to process multiple indices
    # index_list = [0, 10]  # Replace with any list of indices you want to process
    index_list = range(0, 10)
    compensate_with_real_data(lnrnn_comp, data_info_list, index_list)

    # Show the plots
    plt.show()


def pad_arrays(arrays):
    """
    对一个包含任意维度的数组的列表进行零填充，使得所有数组的形状与列表中最大的维度长度一致。

    参数：
    arrays (list of np.ndarray): 包含待填充的数组的列表。

    返回：
    list of np.ndarray: 经过零填充后具有相同形状的数组列表。
    """
    # 获取列表中每个数组的形状，并找到最大形状
    max_shape = tuple(max(arr.shape[i] if i < arr.ndim else 0 for arr in arrays)
                      for i in range(max(arr.ndim for arr in arrays)))

    # 对每个数组进行零填充，使其形状达到最大形状
    padded_arrays = [
        np.pad(arr, [(0, max_shape[i] - arr.shape[i]) if i < arr.ndim else (0,
               max_shape[i]) for i in range(len(max_shape))], mode='constant')
        for arr in arrays
    ]

    return padded_arrays


def extract_features_file(debug=False):
    data_info_list = find_data_info("data/M50")
    for data_info in data_info_list:
        print(data_info)

    # 取第一个数据
    ws = System.loadFile(data_info_list[0].file_path)
    ws_fit = exam_process.ws_system_fit(ws, k=1.0, freq_range=(5, 200))

    ws2 = System.loadFile(data_info_list[10].file_path)
    ws2_fit = exam_process.ws_system_fit(ws2, k=1.0, freq_range=(5, 200))

    fh0 = PiecewiseActivationLayer.from_xk(
        [1.0, 1.2, 1.4, 1.6, 1.8, 2.0],
        [1, 0.8, 0.6, 0.4, 0.2, 0.00])
    fh1 = PiecewiseActivationLayer.from_xk(
        [1.0, 1.2, 1.4, 1.6, 1.8, 2.0],
        [0.00, 0.2, 0.4, 0.6, 0.8, 1.0])

    lnrnn = IIR_LNRNN.fromSystem(
        [ws_fit, ws2_fit], [fh0, fh1], fs=2000, Hammerstein=False)

    def process_data(index, amply=0.006, output_reverse=False):
        input_data, output_data, freq_list = exam_class.load_data_json_to_time_sereis(
            data_info_list[index].data_file_path)
        if 1:
            # 降采样
            input_data = [input_data_item.resample(
                2000) for input_data_item in input_data]
            output_data = [output_data_item.resample(
                2000) for output_data_item in output_data]

        output_data = [output_data_item.apply_gain(
            16*config.CONF_GAIN_RATIO).apply_gain(amply) for output_data_item in output_data]
        input_data = [input_data_item.apply_gain(
            amply) for input_data_item in input_data]

        # 去掉直流分量
        output_data = [output_data_item.remove_dc().invert()
                       for output_data_item in output_data]
        input_data = [input_data_item.remove_dc()
                      for input_data_item in input_data]

        output_data = [item.filter(filter_type='bandpass', cutoff_freq=[
                                   10, 500]) for item in output_data]
        input_data = [item.filter(filter_type='bandpass', cutoff_freq=[
            10, 500]) for item in input_data]
        print(f'freq_list: {freq_list}')
        return System.fromTimeSeries(
            input_data, output_data, frequencies=freq_list, use_parallel=False), input_data, output_data, freq_list

    index_list = range(0, len(data_info_list))
    # index_list = range(0, 2)
    features_vector_all = []
    output_all = []
    for index in index_list:
        ws_data, input_data, output_data, freq_list = process_data(index)
        print(f'震级{data_info_list[index].magnitude:.2f}')

        feature_vector_one_scan = []
        output_one_scan = []
        for input_data_item, output_data_item in zip(input_data, output_data):
            # 提取特征（假设返回的是 TimeSeries 对象的列表）
            features = lnrnn.extract_features_time_response(input_data_item)
            print(f'features: {features}')

            # 从每个特征中提取 samples 数组，并将其拼接成一个特征向量
            feature_vector_item = np.array(
                [feature.samples for feature in features])
            # 将 feature_vector 行列转置
            feature_vector_item = feature_vector_item.T
            # 合并特征向量（新增一个维度）
            feature_vector_one_scan.append(feature_vector_item)
            output_one_scan.append(output_data_item.samples)

            if debug:
                input_data_item.plot()
                output_data_item.plot()
                ws_data.plot()
                ws_fit.plot()
                for feature in features:
                    feature.plot()

        feature_vector_one_scan = np.stack(pad_arrays(feature_vector_one_scan))
        output_one_scan = np.stack(pad_arrays(output_one_scan))

        # 将特征向量和输出数据保存到文件
        print(f'feature_vector.shape: {feature_vector_one_scan.shape}')
        print(f'output.shape: {output_one_scan.shape}')
        features_vector_all.append(feature_vector_one_scan)
        output_all.append(output_one_scan)

    # 继续给缺少的数据进行零填充

    features_vector_all = np.stack(pad_arrays(features_vector_all))
    output_all = np.stack(pad_arrays(output_all))
    print(f'features_vector_all.shape: {features_vector_all.shape}')
    print(f'output_all.shape: {output_all.shape}')

    np.save('data/feature_vector.npy', feature_vector_one_scan)
    np.save('data/output.npy', output_one_scan)

    # 显示图表
    plt.show()


def extract_features():
    data_info_list = find_data_info("data/M50")
    for data_info in data_info_list:
        print(data_info)

    # 取第一个数据
    ws = System.loadFile(data_info_list[0].file_path)
    ws_fit = exam_process.ws_system_fit(ws, k=1.0, freq_range=(5, 200))

    ws2 = System.loadFile(data_info_list[10].file_path)
    ws2_fit = exam_process.ws_system_fit(ws2, k=1.0, freq_range=(5, 200))

    fh0 = PiecewiseActivationLayer.from_xk(
        [1.0, 1.2, 1.4, 1.6, 1.8, 2.0],
        [1, 0.8, 0.6, 0.4, 0.2, 0.00])
    fh1 = PiecewiseActivationLayer.from_xk(
        [1.0, 1.2, 1.4, 1.6, 1.8, 2.0],
        [0.00, 0.2, 0.4, 0.6, 0.8, 1.0])

    lnrnn = IIR_LNRNN.fromSystem(
        [ws_fit, ws2_fit], [fh0, fh1], fs=2000, Hammerstein=False)

    tr_sin = exam_class.TimeSeries.fromSin(1, 30, 2000, 0.2)
    features = lnrnn.extract_features(tr_sin)
    print(f'shape: {features.shape}')


def extract_features_from_directory(process_data, lnrnn: IIR_LNRNN, data_info_list, index_list, output_filename, debug=False, is_compensator=False, ws_target=None):
    """
    Extract features from time-series data in a specified directory and save the results.

    Parameters:
    - process_data (callable): A callback function to process data, which should accept (data_info_list, index).
    - lnrnn (IIR_LNRNN): An instance of the IIR_LNRNN model used to extract features from input data.
    - directory (str): Directory path containing the data files.
    - index_list (list of int): List of indices to specify which files to process.
    - output_filename (str): Base name for the output files where features and outputs will be saved.
    - debug (bool): If True, displays debug plots for input and output data.

    """
    # Step 1: Find and load data info list from the specified directory
    for data_info in data_info_list:
        print(data_info)  # Debug print for each data entry

    # Step 2: Initialize lists to store all feature vectors and output data across scans
    features_vector_all = []
    output_all = []
    input_all = []

    # Step 3: Loop through each index in index_list to process specified data files
    for index in index_list:
        # Use process_data callback to get ws_data, input and output data, and frequency list
        ws_data, input_data, output_data, freq_list = process_data(
            data_info_list, index)
        # Print the magnitude of the current data set
        print(f'震级{data_info_list[index].magnitude:.2f}')

        # Step 4: Prepare lists to store feature vectors and output samples for the current scan
        feature_vector_one_scan = []
        output_one_scan = []
        input_one_scan = []

        # Step 5: Loop through each input and output data pair to extract features and build vectors
        for input_data_item, output_data_item in zip(input_data, output_data):
            # Extract features using the lnrnn model (assumes extract_features_time_response returns TimeSeries objects)
            if is_compensator:
                feature_input = output_data_item
            else:
                feature_input = input_data_item
            features = lnrnn.extract_features_time_response(feature_input)
            print(f'features: {features}')  # Debug print for features

            # Convert extracted features to a numpy array and transpose to form the feature vector
            feature_vector_item = np.array(
                [feature.samples for feature in features]).T
            feature_vector_one_scan.append(feature_vector_item)
            if is_compensator:
                # 目标的被补偿数据
                feature_output = ws_target.time_response(
                    input_data_item).samples
            else:
                feature_output = output_data_item.samples
            output_one_scan.append(feature_output)
            input_one_scan.append(input_data_item.samples)

            # Debug plot for input and output data if debug mode is enabled
            if debug:
                feature_input.plot()
                output_data_item.plot()
                ws_data.plot()
                for feature in features:
                    feature.plot()

        # Stack feature and output vectors for the current scan, padding arrays as needed
        feature_vector_one_scan = np.stack(pad_arrays(feature_vector_one_scan))
        input_one_scan = np.stack(pad_arrays(input_one_scan))
        output_one_scan = np.stack(pad_arrays(output_one_scan))

        # Print shapes of the feature vector and output to verify the data
        print(f'input.shape: {input_one_scan.shape}')
        print(f'feature_vector.shape: {feature_vector_one_scan.shape}')
        print(f'output.shape: {output_one_scan.shape}')

        # Append the processed data for this scan to the main lists
        features_vector_all.append(feature_vector_one_scan)
        output_all.append(output_one_scan)

    # Step 6: Stack and pad arrays for all scans
    features_vector_all = np.stack(pad_arrays(features_vector_all))
    output_all = np.stack(pad_arrays(output_all))
    input_all = np.stack(pad_arrays(input_one_scan))

    # Print final shapes to confirm sizes
    print(f'input_all.shape: {input_all.shape}')
    print(f'features_vector_all.shape: {features_vector_all.shape}')
    print(f'output_all.shape: {output_all.shape}')

    # Step 7: Save the processed feature and output data to .npy files
    time_label = datetime.now().strftime('%Y%m%d_%H%M%S')
    np.save(
        f'cache/features/{time_label}_{output_filename}_feature_vector.npy', features_vector_all)
    np.save(
        f'cache/features/{time_label}_{output_filename}_output.npy', output_all)
    np.save(
        f'cache/features/{time_label}_{output_filename}_input.npy', input_all)

    # Step 8: Show all plots (if debug mode is enabled, this will display intermediate plots)
    plt.show()


def extract_features_compensator():
    # Define the `process_data` callback function
    def process_data(data_info_list, index, amply=0.006, output_reverse=False):
        """
        Processes data at a specific index in data_info_list.

        Parameters:
        - data_info_list (list): List of data information entries.
        - index (int): Index of the data file to process.
        - amply (float): Amplification factor for input and output data.
        - output_reverse (bool): Whether to reverse the output data.

        Returns:
        - System: Processed system data.
        - input_data, output_data, freq_list: Lists of processed input and output data and frequency list.
        """
        # Load time-series data from JSON and prepare frequency list
        input_data, output_data, freq_list = exam_class.load_data_json_to_time_sereis(
            data_info_list[index].data_file_path
        )

        # Downsample input and output data to 2000 Hz
        input_data = [input_data_item.resample(
            2000) for input_data_item in input_data]
        output_data = [output_data_item.resample(
            2000) for output_data_item in output_data]

        # Apply gain to input and output data
        output_data = [output_data_item.apply_gain(
            16 * config.CONF_GAIN_RATIO).apply_gain(amply) for output_data_item in output_data]
        input_data = [input_data_item.apply_gain(
            amply) for input_data_item in input_data]

        # Remove DC component and apply inversion to output data if required
        output_data = [output_data_item.remove_dc().invert()
                       for output_data_item in output_data]
        input_data = [input_data_item.remove_dc()
                      for input_data_item in input_data]

        # Apply bandpass filter to both input and output data
        output_data = [item.filter(filter_type='bandpass', cutoff_freq=[
                                   10, 500]) for item in output_data]
        input_data = [item.filter(filter_type='bandpass', cutoff_freq=[
                                  10, 500]) for item in input_data]

        # Print frequency list for debugging
        print(f'freq_list: {freq_list}')

        # Create system from time series
        return (
            System.fromTimeSeries(input_data, output_data,
                                  frequencies=freq_list, use_parallel=False),
            input_data,
            output_data,
            freq_list
        )

    # Directory and file parameters
    data_info_list = find_data_info('data/M50')
    # 只取x.n，其中n是双数的数据，例如0.2, 0.4...
    data_info_list = [data_info_list[i]
                      for i in range(1, len(data_info_list), 2)]
    data_info_list = data_info_list[:11]
    print(f'data_info_list: {data_info_list}')
    index_list = range(0, len(data_info_list))
    # index_list = [0, 1]

    output_filename = 'lnrnn_comp'

    # Initialize `lnrnn` and other necessary objects

    # Load system and fit data for `lnrnn`
    ws = System.loadFile(data_info_list[0].file_path)
    ws_fit = exam_process.ws_system_fit(ws, k=1.0, freq_range=(5, 200))

    ws2 = System.loadFile(data_info_list[10].file_path)
    ws2_fit = exam_process.ws_system_fit(ws2, k=1.0, freq_range=(5, 200))

    H = [ws_fit, ws2_fit]
    ws_target = ws_fit
    E = [exam_class.ws_compensator(hi, ws_target) for hi in H]

    fh0 = PiecewiseActivationLayer.from_xk([1.0, 1.2, 1.4, 1.6, 1.8, 2.0], [
                                           1, 0.8, 0.6, 0.4, 0.2, 0.00])
    fh1 = PiecewiseActivationLayer.from_xk([1.0, 1.2, 1.4, 1.6, 1.8, 2.0], [
                                           0.00, 0.2, 0.4, 0.6, 0.8, 1.0])

    lnrnn = IIR_LNRNN.fromSystem(E, [
                                 fh0, fh1], fs=2000, Hammerstein=False)

    # Call the `extract_features_from_directory` function to process and save features
    extract_features_from_directory(
        process_data=process_data,
        lnrnn=lnrnn,
        data_info_list=data_info_list,
        index_list=index_list,
        output_filename=output_filename,
        is_compensator=True,
        ws_target=ws_target,
        debug=False
    )


def system_from_process_data(
        data_path,
        amply=0.006,
        use_resample=True,
        fade_in=0.3,
        fade_out=0.0,
        time_cliped_s=2.0,
        filter_bandpass=True,
        filter_bandpass_freq=[10, 500],
        fs=2000,
        use_debug=False
) -> System:
    input_tr, output_tr, freq_list = pre_process_data(
        data_path,
        amply=amply,
        use_resample=use_resample,
        fade_in=fade_in,
        fade_out=fade_out,
        time_cliped_s=time_cliped_s,
        filter_bandpass=filter_bandpass,
        filter_bandpass_freq=filter_bandpass_freq,
        fs=fs,
        use_debug=use_debug)

    # 拟合 target_sweep 的系统
    sys_target = exam_class.System.fromTimeSeries(
        input_tr, output_tr, freq_list)
    return sys_target


if __name__ == '__main__':
    # 设置中文字体和取消负号前的空格
    rcParams['font.sans-serif'] = ['SimHei']  # 设置字体为黑体
    rcParams['axes.unicode_minus'] = False    # 解决负号显示问题

    if 1:
        compensator_real_data()
    # simulation_and_compentation()
    # extract_features_file()
    # extract_features()
    if 0:
        extract_features_compensator()
