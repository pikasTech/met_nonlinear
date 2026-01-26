"""
神经网络模型库 - WaveNet模型模块

此模块包含WaveNet及其变种模型类。
"""

import tensorflow as tf
import logging
from tensorflow.keras import layers, models
from typing import List, Dict, Any, Tuple, Optional, Union
from .base_models import BaseModel, ModelEvent, ModelEventType
from calibration_analyzer.exam_class import System
from .utils import merge_config
from visualization.model_analysis import conv1d_frequency_response
import matplotlib.pyplot as plt
import os
import numpy as np
from experimental.mimoiir import DIAGIIR
from .frikan_models import system2params
from .layer_support import LayeredModelSupport, SpiceModelSupport
from .model_layers import SVFLayer, DenseLayer

# 创建 logger
logger = logging.getLogger(__name__)


class WaveNet(BaseModel):
    """
    WaveNet模型，基于扩张卷积的时序建模网络
    """

    def __init__(self,
                 kernel_units=64,  # 卷积层中的过滤器数量
                 kernel_size=10,  # 卷积核大小
                 dilations=[1, 2, 4, 8, 16],  # WaveNet层的扩张率
                 fs=2000,  # 采样频率
                 checkpoint_dir='data',  # 存储数据的目录
                 activation='relu',  # 激活函数
                 model_subcfg={},
                 inference_config=None,
                 ):
        self.model_name = 'WaveNet'
        self.activation = activation
        self.tf_activation = tf.keras.layers.Activation(activation)
        
        # 存储推理配置
        self.inference_config = inference_config or {
            'bias_compensation': {
                'enabled': False,
                'layer_bias_adjustments': {}
            }
        }
        # 定义WaveNet模型
        self.input_layer = tf.keras.layers.Input(shape=(None, 1))
        x = self.input_layer
        logger.info(f'WaveNet activation: {activation}')
        # 残差块（WaveNet层）
        for dilation in dilations:
            skip_connections = []
            for _ in range(3):  # 每个扩张率有三个残差块
                # 带扩张卷积核的卷积
                x_res = tf.keras.layers.Conv1D(
                    kernel_units, kernel_size, dilation_rate=dilation, padding='causal', use_bias=True)(x)
                x_res = self.tf_activation(x_res)
                skip_connections.append(x_res)
            x = tf.keras.layers.Add()(skip_connections)  # 组合跳跃连接
            x = tf.keras.layers.Conv1D(
                kernel_units, kernel_size, padding='causal', use_bias=True)(x)  # 输出滤波

        # 全连接层
        x = tf.keras.layers.Dense(kernel_units, activation=activation)(x)
        # 输出层
        x = tf.keras.layers.Dense(1, activation="linear")(
            x)  # 最终预测输出

        self.model = tf.keras.Model(inputs=self.input_layer, outputs=x)
        self.model.build(input_shape=(None, None, 1))

        # 存储配置
        self.fs = fs

        # 检查点目录配置
        self.init_checkpoint(checkpoint_dir)


class WaveNet2(WaveNet):
    """
    WaveNet2模型，对原始WaveNet进行了扩展和优化

    支持更多的配置选项，如门控机制、密度块等
    """

    def __init__(self,
                 kernel_units=64,  # 卷积层中的过滤器数量
                 fs=2000,
                 activation='relu',  # 激活函数
                 checkpoint_dir='data',  # 存储数据的目录
                 model_subcfg={},
                 ):
        # 默认模型子配置
        model_subcfg_default = {
            # WaveNet层的扩张率
            'dilations': [1, 4, 16, 64, 256],
            'kernel_size': 8,  # 卷积核大小
            'skip_initial_conv': False,  # 是否跳过初始卷积
            'init_conv_units': 4,  # 初始卷积单元数
            'skip_output_conv': False,  # 是否跳过输出卷积
            'use_gating': True,  # 是否使用门控机制
            'final_activation': None,  # 最终层的激活函数
            'block_activation': None,  # 残差块的激活函数
            'gate_activation': 'relu',  # 门控机制的激活函数
            'dropout_rate': 0.0,  # 每个块后的dropout率
            'use_residual': True,  # 是否使用残差连接
            'block_dense': False,  # 是否使用密度块
            'block_dense_units': 1,  # 密度块中的单元数
            'combine_blocks_by_add': True,  # 是否通过加法组合块输出
            'post_dense': False,  # 是否添加后处理全连接层
            'post_dense_units': 1,  # 后处理全连接层单元数
            'post_dense_activation': None,  # 后处理全连接层激活函数
            'post_dense_layers': 1,  # 后处理全连接层数量
            'use_parallel_blocks': False,  # 是否使用并行块
        }

        self.subcfg = merge_config(
            model_subcfg_default, model_subcfg)

        self.model_name = 'WaveNet2'
        self.kernel_units = kernel_units
        self.kernel_size = self.subcfg["kernel_size"]
        self.dilations = self.subcfg["dilations"]
        self.fs = fs

        # 初始化模型
        self.model = self.build_model((None, 1))

        # 存储配置
        self.checkpoint_dir = checkpoint_dir
        self.init_checkpoint(checkpoint_dir)

    def residual_block(self, input_x, dilation_rate):
        """
        构建带扩张卷积和门控机制的残差块

        Args:
            input_x: 输入张量
            dilation_rate: 扩张率

        Returns:
            处理后的张量
        """
        # 带扩张卷积和门控机制的残差块
        skip = input_x

        # 扩张卷积
        x = layers.Conv1D(self.kernel_units, self.kernel_size,
                          dilation_rate=dilation_rate, padding='causal')(input_x)

        if self.subcfg['block_activation']:
            x = layers.Activation(self.subcfg['block_activation'])(x)

        gate = layers.Conv1D(self.kernel_units, self.kernel_size,
                             dilation_rate=dilation_rate, padding='causal')(input_x)
        gate = layers.Activation(self.subcfg['gate_activation'])(gate)
        # 门控机制（可选）
        if self.subcfg['use_gating']:
            x = layers.Multiply()([x, gate])
        else:
            x = gate  # 直接使用门控作为x

        # 应用dropout（如果配置）
        if self.subcfg['dropout_rate'] > 0:
            x = layers.Dropout(self.subcfg['dropout_rate'])(x)

        # 残差连接（可选）
        if self.subcfg['use_residual']:
            x = layers.Add()([x, skip])

        # 块密度到(None, 1)形状
        if self.subcfg['block_dense']:
            # (batch_size, time_steps, kernel_units) -> (batch_size, time_steps, 1)
            x = layers.Conv1D(
                filters=self.subcfg['block_dense_units'], kernel_size=1, padding='same')(x)

        return x

    def build_model(self, input_shape):
        """
        构建WaveNet2模型

        Args:
            input_shape: 输入形状

        Returns:
            构建的模型
        """
        inputs = layers.Input(shape=input_shape)

        # 初始卷积（可选）
        if self.subcfg['skip_initial_conv']:
            # 复制输入通道以匹配kernel_units
            x = tf.tile(inputs, [1, 1, self.subcfg['init_conv_units']])
        else:
            x = layers.Conv1D(self.subcfg['init_conv_units'], self.kernel_size,
                              padding='causal', name='initial_conv')(inputs)

        # 跟踪块输出用于跳跃连接
        blocks = []

        residual_block_input = x
        # 构建残差块
        if len(self.dilations) > 0:
            for i in range(len(self.dilations)):
                x = self.residual_block(
                    residual_block_input, self.dilations[i % len(self.dilations)])
                blocks.append(x)
                if not self.subcfg['use_parallel_blocks']:
                    residual_block_input = x  # 将输出作为下一个块的输入
        else:
            # 无残差块，直接使用输入
            blocks.append(residual_block_input)

        # 组合块输出（跳跃连接）
        if len(blocks) > 1:
            # 应用全连接层将维度减少到1通道
            if self.subcfg['combine_blocks_by_add']:
                x = layers.Add()(blocks)  # 组合所有块输出
            else:
                # 先连接所有块的通道
                # 形状变为(batch_size, time_steps, num_blocks*kernel_units)
                x = layers.Concatenate(axis=-1)(blocks)
        else:
            # 如果只有一个块，使用其输出
            x = blocks[0]

        # 在这里添加后处理全连接层
        if self.subcfg['post_dense']:
            for i in range(self.subcfg['post_dense_layers']):
                x = layers.Conv1D(filters=self.subcfg['post_dense_units'],
                                  kernel_size=1, padding='same', name=f'post_dense_{i+1}')(x)
                if self.subcfg['post_dense_activation']:
                    x = layers.Activation(
                        self.subcfg['post_dense_activation'], name=f'post_dense_activation_{i+1}')(x)

        # 最终激活（如果指定）
        if self.subcfg['final_activation']:
            x = layers.Activation(self.subcfg['final_activation'])(x)

        if x.shape[-1] > 1:
            # 如果输出通道数大于1，需要合并
            # 输出卷积（可选）
            if self.subcfg['skip_output_conv']:
                # 使用无激活函数的全连接实现
                x = layers.Dense(1, activation=None)(x)
            else:
                x = layers.Conv1D(1, 1, padding='same', name='output_conv')(x)

        model = models.Model(inputs=inputs, outputs=x)
        return model

    def callback(self, event: ModelEvent):
        """
        处理模型事件的回调函数

        Args:
            event: 模型事件
        """
        if event.type == ModelEventType.PREDICT_END:
            logger.info(f"WaveNet2 model evaluation completed.")


class WaveNet3(WaveNet2):
    """
    WaveNet3模型，更简洁的WaveNet变种

    去掉了复杂的残差结构，保留基本的因果卷积功能
    """

    def __init__(self,
                 kernel_units=64,  # 卷积层中的过滤器数量
                 fs=2000,
                 activation='relu',  # 激活函数
                 checkpoint_dir='data',  # 存储数据的目录
                 model_subcfg={},
                 ):
        # 默认模型子配置
        model_subcfg_default = {
            'kernel_size': 8,  # 卷积核大小
            'skip_initial_conv': False,  # 是否跳过初始卷积
            'init_conv_units': 4,  # 初始卷积单元数
            'final_activation': None,  # 最终层的激活函数
            'dropout_rate': 0.0,  # dropout率
            'post_dense': False,  # 是否添加后处理全连接层
            'post_dense_units': 1,  # 后处理全连接层单元数
            'post_dense_activation': None,  # 后处理全连接层激活函数
            'post_dense_layers': 1,  # 后处理全连接层数量
        }

        self.subcfg = merge_config(
            model_subcfg_default, model_subcfg)

        self.model_name = 'WaveNet3'
        self.kernel_units = kernel_units
        self.kernel_size = self.subcfg["kernel_size"]
        self.fs = fs

        # 初始化模型
        self.model = self.build_model((None, 1))

        # 存储配置
        self.checkpoint_dir = checkpoint_dir
        self.init_checkpoint(checkpoint_dir)

    def build_model(self, input_shape):
        """
        构建WaveNet3模型

        Args:
            input_shape: 输入形状

        Returns:
            构建的模型
        """
        inputs = layers.Input(shape=input_shape)

        # 初始卷积（可选）
        if self.subcfg['skip_initial_conv']:
            # 复制输入通道以匹配kernel_units
            x = tf.tile(inputs, [1, 1, self.subcfg['init_conv_units']])
        else:
            x = layers.Conv1D(self.subcfg['init_conv_units'], self.kernel_size,
                              padding='causal', name='initial_conv')(inputs)

        # 在这里添加后处理全连接层
        if self.subcfg['post_dense']:
            for i in range(self.subcfg['post_dense_layers']):
                x = layers.Conv1D(filters=self.subcfg['post_dense_units'],
                                  kernel_size=1, padding='same', name=f'post_dense_{i+1}')(x)
                if self.subcfg['post_dense_activation']:
                    x = layers.Activation(
                        self.subcfg['post_dense_activation'], name=f'post_dense_activation_{i+1}')(x)

        # 最终激活（如果指定）
        if self.subcfg['final_activation']:
            x = layers.Activation(self.subcfg['final_activation'])(x)

        if x.shape[-1] > 1:
            # 如果输出通道数大于1，需要合并
            # 输出为1个通道
            x = layers.Dense(1, activation=None)(x)

        model = models.Model(inputs=inputs, outputs=x)
        return model


class WaveNet4(WaveNet3):
    """
    WaveNet4模型，WaveNet3的增强版本

    特点:
    - 支持多层初始卷积
    - 初始卷积层生成多通道输出
    - 对初始卷积层生成的多通道进行频率响应分析
    """

    def __init__(self,
                 kernel_units=64,  # 卷积层中的过滤器数量
                 fs=2000,
                 activation='relu',  # 激活函数
                 checkpoint_dir='data',  # 存储数据的目录
                 model_subcfg={},
                 ):
        # 默认模型子配置
        model_subcfg_default = {
            'kernel_size': 8,  # 卷积核大小
            'skip_initial_conv': False,  # 是否跳过初始卷积
            'init_conv_units': 4,  # 初始卷积单元数
            'init_conv_layers': 4,  # 初始卷积层数
            'init_conv_activation': None,  # 初始卷积层激活函数
            'final_activation': None,  # 最终层的激活函数
            'dropout_rate': 0.0,  # dropout率
            'post_dense': False,  # 是否添加后处理全连接层
            'post_dense_units': 1,  # 后处理全连接层单元数
            'post_dense_activation': None,  # 后处理全连接层激活函数
            'post_dense_layers': 1,  # 后处理全连接层数量
        }

        self.subcfg = merge_config(
            model_subcfg_default, model_subcfg)

        self.model_name = 'WaveNet4'
        self.kernel_units = kernel_units
        self.kernel_size = self.subcfg["kernel_size"]
        self.fs = fs

        # 初始化模型
        self.model = self.build_model((None, 1))

        # 存储配置
        self.checkpoint_dir = checkpoint_dir
        self.init_checkpoint(checkpoint_dir)

        # 保存初始卷积层的输出模型，用于频率响应分析
        self._create_init_conv_model()

    def _build_init_conv_layers(self, inputs):
        """
        构建初始卷积层

        Args:
            inputs: 输入张量

        Returns:
            处理后的张量
        """
        if self.subcfg['skip_initial_conv']:
            # 复制输入通道以匹配kernel_units
            x = tf.tile(inputs, [1, 1, self.subcfg['init_conv_units']])
        else:
            # 多层初始卷积
            x = inputs
            for i in range(self.subcfg['init_conv_layers']):
                x = layers.Conv1D(self.subcfg['init_conv_units'], self.kernel_size,
                                  padding='causal', name=f'initial_conv_{i+1}')(x)
                if self.subcfg['init_conv_activation']:
                    x = layers.Activation(
                        self.subcfg['init_conv_activation'])(x)

        return x

    def _create_init_conv_model(self):
        """
        创建一个模型，只包含初始卷积层部分，用于频率响应分析
        """
        inputs = layers.Input(shape=(None, 1))

        # 使用辅助方法构建初始卷积层
        x = self._build_init_conv_layers(inputs)

        # 创建只包含初始卷积层的模型
        self.init_conv_model = models.Model(inputs=inputs, outputs=x)

    def build_model(self, input_shape):
        """
        构建WaveNet4模型，支持多层初始卷积和单通道输出

        Args:
            input_shape: 输入形状

        Returns:
            构建的模型
        """
        inputs = layers.Input(shape=input_shape)

        # 使用辅助方法构建初始卷积层
        x = self._build_init_conv_layers(inputs)

        # 在这里添加后处理全连接层
        if self.subcfg['post_dense']:
            for i in range(self.subcfg['post_dense_layers']):
                x = layers.Conv1D(filters=self.subcfg['post_dense_units'],
                                  kernel_size=1, padding='same', name=f'post_dense_{i+1}')(x)
                if self.subcfg['post_dense_activation']:
                    x = layers.Activation(
                        self.subcfg['post_dense_activation'], name=f'post_dense_activation_{i+1}')(x)

        # 最终激活（如果指定）
        if self.subcfg['final_activation']:
            x = layers.Activation(self.subcfg['final_activation'])(x)

        # 如果输出通道数大于1，合并为1通道（与WaveNet3保持一致）
        if x.shape[-1] > 1:
            x = layers.Dense(1, activation=None)(x)

        model = models.Model(inputs=inputs, outputs=x)
        return model

    def callback(self, event: ModelEvent):
        """
        处理模型事件的回调函数，分析初始卷积层各通道的频率响应

        Args:
            event: 模型事件
        """
        if event.type == ModelEventType.PREDICT_END:
            logger.info(f"WaveNet4 model evaluation completed.")

            try:
                # 分析初始卷积层的多通道频率响应
                channels = self.len(
                    self.subcfg['init_conv_units'])  # 初始卷积层的通道数
                logger.info(f"分析初始卷积层的{channels}个通道的频率响应")

                # 创建图表
                plt.figure(figsize=(12, 7))
                plt.title(
                    f"WaveNet4 Initial Conv Layers Channel Frequency Response", fontsize=16)

                # 创建颜色映射
                colors = plt.cm.viridis(np.linspace(0, 1, channels))

                # 为每个通道创建一个子模型进行分析
                for i in range(channels):
                    # 创建一个模型，从初始卷积输出中只提取第i个通道
                    channel_input = layers.Input(shape=(None, 1))
                    channel_output = self.init_conv_model(
                        channel_input)[..., i:i+1]
                    channel_model = models.Model(
                        inputs=channel_input, outputs=channel_output)

                    # 获取频率响应
                    system = conv1d_frequency_response(
                        channel_model,
                        fs=self.fs,
                        f_range=(5, 200),
                        amplitude=1,
                        points=100,
                        use_parallel=False
                    )

                    # 绘制频率响应
                    gain = system.toabs()
                    freq = system.f
                    plt.loglog(freq, gain, linewidth=2,
                               color=colors[i], alpha=0.8, label=f"Channel {i+1}")

                # 设置图表属性
                plt.xlabel("Frequency (Hz)", fontsize=12)
                plt.ylabel("Gain", fontsize=12)
                plt.grid(True, which='both', linestyle='--', linewidth=0.5)
                plt.legend(loc='best', title="Initial Conv Channels")

                # 保存图像
                save_dir = self.checkpoint_dir
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(
                    save_dir, 'initial_conv_channels_frequency_response.png')
                plt.savefig(save_path, dpi=300)
                logger.info(f"已将初始卷积层频率响应图保存到: {save_path}")

            except Exception as e:
                logger.error(f"绘制频率响应时发生错误: {e}")
                import traceback
                traceback.print_exc()

    def load_weights(self, weights_file):
        """
        加载模型权重并同步初始卷积层模型权重

        Args:
            weights_file: 权重文件路径
        """
        # 先加载主模型权重
        self.model.load_weights(weights_file)
        self.save_weights_json(weights_file)

        logger.info("正在同步初始卷积层模型权重...")

        # 从主模型中提取初始卷积层权重并同步到init_conv_model
        for i in range(self.subcfg['init_conv_layers']):
            layer_name = f'initial_conv_{i+1}'

            # 从主模型中查找对应层
            main_layer = None
            for layer in self.model.layers:
                if layer.name == layer_name:
                    main_layer = layer
                    break

            if main_layer is None:
                logger.warning(f"警告: 在主模型中未找到层 '{layer_name}'")
                continue

            # 从init_conv_model中查找对应层
            init_layer = None
            for layer in self.init_conv_model.layers:
                if layer.name == layer_name:
                    init_layer = layer
                    break

            if init_layer is None:
                logger.warning(f"警告: 在初始卷积模型中未找到层 '{layer_name}'")
                continue

            # 获取主模型中该层的权重并设置到初始卷积模型中
            weights = main_layer.get_weights()
            init_layer.set_weights(weights)
            logger.info(f"已同步层 '{layer_name}' 的权重")

        logger.info("初始卷积层模型权重同步完成")


# 定义nrelu激活函数：反向输出的relu，即nrelu(x) = -relu(x)
def nrelu(x):
    """反向relu激活函数，nrelu(x) = -relu(x)"""
    return -tf.nn.relu(x)


# 注册nrelu到TensorFlow自定义对象中
tf.keras.utils.get_custom_objects().update({'nrelu': nrelu})


class WaveNet5(BaseModel, LayeredModelSupport, SpiceModelSupport):
    """
    WaveNet5模型，在WaveNet4的基础上使用带通滤波器IIR作为初始层

    特点:
    - 使用DIAGIIR替代1D卷积作为初始层
    - 使用一系列中心频率为f0，品质因数为Q的带通滤波器
    - 保留WaveNet4的其他功能
    - 支持nrelu激活函数（反向输出的relu）
    - 支持分层模型输出
    """

    def __init__(self,
                 fs=2000,
                 checkpoint_dir='data',
                 kernel_units=4,
                 activation=None,
                 model_subcfg={},
                 inference_config=None,
                 ):
        # 默认模型子配置
        model_subcfg_default = {
            'init_center_freqs': [10, 30, 60, 100],  # 带通滤波器的中心频率列表
            'init_quality_factors': [1.0, 1.0, 1.0, 1.0],  # 带通滤波器的品质因数列表
            'dropout_rate': 0.0,  # dropout率
            'post_dense': False,  # 是否添加后处理全连接层
            'post_dense_units': 1,  # 后处理全连接层单元数
            'post_dense_activation': None,  # 后处理全连接层激活函数
            'use_dense_bias': True,  # 后处理全连接层是否使用偏置
            'post_dense_layers': 1,  # 后处理全连接层数量
        }

        self.subcfg = merge_config(
            model_subcfg_default, model_subcfg)

        self.model_name = 'WaveNet5'
        self.fs = fs
        
        # 存储推理配置
        self.inference_config = inference_config or {
            'bias_compensation': {
                'enabled': False,
                'layer_bias_adjustments': {}
            }
        }

        # 添加fast_model支持标志
        self.use_fast_model = True

        # 使用带通滤波器IIR替代Conv1D初始层
        self._init_filters()

        # 初始化模型
        self.model = self.build_model((None, 1))

        # 存储配置
        self.checkpoint_dir = checkpoint_dir
        self.init_checkpoint(checkpoint_dir)

        # 保存初始IIR层的输出模型，用于频率响应分析
        self.init_iir_model = self._create_init_iir_model()

    def _init_filters(self):
        """
        初始化带通滤波器IIR参数
        """
        s = System.s

        units = len(self.subcfg['init_center_freqs'])  # 滤波器数量
        center_freqs = self.subcfg['init_center_freqs'][:units]  # 确保不超过units个
        # 确保不超过units个
        quality_factors = self.subcfg['init_quality_factors'][:units]

        # 如果提供的频率或Q值数量不足，使用默认值填充
        while len(center_freqs) < units:
            center_freqs.append(30.0)  # 默认中心频率30Hz
        while len(quality_factors) < units:
            quality_factors.append(1.0)  # 默认Q值1.0

        # 创建滤波器系统列表
        filter_systems = []
        for i in range(units):
            f0 = center_freqs[i]
            Q = quality_factors[i]
            omega0 = 2 * np.pi * f0

            # 创建带通滤波器传递函数表达式: (s/(Q*omega0))/(s^2 + (omega0/Q)*s + omega0**2)
            highpass_expr = s**2 / (s**2 + (omega0/Q)*s + omega0**2)
            bandpass_expr = (s*(omega0/Q))/(s**2 + (omega0/Q)*s + omega0**2)
            lowpass_expr = (omega0**2) / (s**2 + (omega0/Q)*s + omega0**2)

            # 创建系统对象
            system_highpass = System.fromSymbol(
                highpass_expr, f_range=(5, 200))
            system_bandpass = System.fromSymbol(
                bandpass_expr, f_range=(5, 200))
            system_lowpass = System.fromSymbol(
                lowpass_expr, f_range=(5, 200))
            # 按照 [高通，带通，低通] 的顺序添加到列表
            filter_systems.append(system_highpass)
            filter_systems.append(system_bandpass)
            filter_systems.append(system_lowpass)

        # 将系统转换为IIR参数
        self.iir_params_list = system2params(filter_systems, self.fs)

        # 提取IIR参数
        a1_list = [params['a1'] for params in self.iir_params_list]
        a2_list = [params['a2'] for params in self.iir_params_list]
        b0_list = [params['b0'] for params in self.iir_params_list]
        b1_list = [params['b1'] for params in self.iir_params_list]
        b2_list = [params['b2'] for params in self.iir_params_list]

        # 创建DIAGIIR层
        self.init_iir = DIAGIIR(
            units=len(self.iir_params_list),
            a1_list=a1_list,
            a2_list=a2_list,
            b0_list=b0_list,
            b1_list=b1_list,
            b2_list=b2_list,
            fs=self.fs,
            trainable=False,  # 不训练IIR参数
            init_by_system=True
        )

        # 添加fast_iir对象，与init_iir参数相同但使用DIAGIIR替代SIMOIIR
        self.fast_iir = self.init_iir
        # 保存滤波器系统，用于分析
        self.filter_systems = filter_systems

    def _create_init_iir_model(self):
        """
        创建一个模型，只包含初始IIR层部分，用于频率响应分析
        """
        inputs = layers.Input(shape=(None, 1))
        x = self.init_iir(inputs)
        return models.Model(inputs=inputs, outputs=x)

    def build_model(self, input_shape):
        """
        构建WaveNet5模型，使用DIAGIIR替代Conv1D作为初始层
        并创建fast_model用于加速训练
        同时构建分层模型，每个分层模型连接两个相邻层

        Args:
            input_shape: 输入形状

        Returns:
            构建的模型
        """

        # 存储层间输出和对应的模型
        # 创建相邻层之间的模型（两两连接）
        self.layer_to_layer_models = []

        inputs = layers.Input(shape=input_shape)
        layer_input = layers.Input(shape=input_shape)

        # 使用初始IIR层替代Conv1D
        x = self.init_iir(inputs)        # 记录IIR层输出
        layer_output = self.init_iir(layer_input)

        # 创建 layer to layer 模型
        tf_layer_model = models.Model(
            inputs=layer_input, outputs=layer_output, name="IIR_Layer_Model")
        # 使用自定义SVFLayer包装
        svf_layer = SVFLayer(
            tf_layer_model,
            "IIR_Layer_Model",
            center_freqs=self.subcfg['init_center_freqs'],
            quality_factors=self.subcfg['init_quality_factors'],
        )
        self.layer_to_layer_models.append(svf_layer)

        layer_input = layers.Input(shape=(None, layer_output.shape[-1]))

        # 创建跳过IIR层的输入（用于fast_model）
        iir_output_shape = x.shape
        fast_inputs = layers.Input(shape=(None, iir_output_shape[-1]))

        # 标记两个处理流的起始点
        full_model_x = x
        fast_model_x = fast_inputs

        # 在这里添加后处理全连接层
        if self.subcfg['post_dense']:
            for i in range(self.subcfg['post_dense_layers']):
                # 创建层
                post_dense = layers.Conv1D(
                    filters=self.subcfg['post_dense_units'],
                    kernel_size=1,
                    padding='same',
                    use_bias=self.subcfg['use_dense_bias'],
                    name=f'post_dense_{i+1}'
                )

                # 应用到3个流
                full_model_x = post_dense(full_model_x)
                fast_model_x = post_dense(fast_model_x)
                layer_output = post_dense(layer_input)

                if self.subcfg['post_dense_activation']:
                    activation_layer = layers.Activation(self.subcfg['post_dense_activation'],
                                                         name=f'post_dense_activation_{i+1}')
                    full_model_x = activation_layer(full_model_x)
                    fast_model_x = activation_layer(fast_model_x)
                    # 创建 layer to layer 模型
                    layer_output = activation_layer(layer_output)
                tf_layer_model = models.Model(
                    inputs=layer_input, outputs=layer_output, name=f"Dense_Layer_Model_{i+1}")
                # 使用自定义DenseLayer包装
                dense_layer = DenseLayer(
                    tf_layer_model,
                    f"Dense_Layer_Model_{i+1}",
                    activation=self.subcfg['post_dense_activation']
                )
                self.layer_to_layer_models.append(dense_layer)
                layer_input = layers.Input(
                    shape=(None, layer_output.shape[-1]))

        # 如果输出通道数大于1，合并为1通道
        if full_model_x.shape[-1] > 1:
            output_dense = layers.Dense(
                1, activation=None, use_bias=self.subcfg['use_dense_bias'])
            full_model_x = output_dense(full_model_x)
            fast_model_x = output_dense(fast_model_x)
            layer_output = output_dense(layer_input)

            # 创建 layer to layer 模型
            tf_layer_model = models.Model(
                inputs=layer_input, outputs=layer_output, name="Output_Layer_Model")
            # 使用自定义DenseLayer包装
            output_layer = DenseLayer(tf_layer_model, "Output_Layer_Model")
            self.layer_to_layer_models.append(output_layer)

        # 创建完整模型和快速模型
        model = models.Model(inputs=inputs, outputs=full_model_x)
        fast_model = models.Model(
            inputs=fast_inputs, outputs=fast_model_x, name='fast_WaveNet5')        # 保存主模型和快速模型
        self.model = model
        self.fast_model = fast_model

        return model

    def load_weights(self, weights_file):
        """
        加载模型权重

        Args:
            weights_file: 权重文件路径
        """

        super().load_weights(weights_file)

        # 更新 layer_to_layer_models 的权重
        logger.info("正在更新 layer_to_layer_models 的权重...")

        # 创建层名称到层对象的映射，便于查找
        layer_dict = {layer.name: layer for layer in self.model.layers}

        # 逐个更新 layer_to_layer_models 中的模型权重
        for i, layer_wrapper in enumerate(self.layer_to_layer_models):
            updated = False
            # 获取当前层模型的名称
            model_name = layer_wrapper.name
            logger.info(f"正在为分层模型 '{model_name}' 更新权重...")

            # 遍历层模型中的每一层
            for layer in layer_wrapper.model.layers:
                # 跳过输入层
                if isinstance(layer, tf.keras.layers.InputLayer):
                    continue

                # 尝试在主模型中查找同名层
                if layer.name in layer_dict:
                    # 找到匹配的层，复制权重
                    source_layer = layer_dict[layer.name]
                    weights = source_layer.get_weights()

                    # 如果有权重，则进行更新
                    if weights:
                        layer.set_weights(weights)
                        logger.info(f"  - 已更新层 '{layer.name}' 的权重")
                        # print(layer.get_weights())
                        updated = True

            if not updated:
                logger.warning(f"  - 警告: 未找到与分层模型 '{model_name}' 匹配的层")

        logger.info("layer_to_layer_models 权重更新完成")

    def callback(self, event: ModelEvent):
        """
        处理模型事件的回调函数，使用并行化的方法分析初始IIR层各通道的频率响应

        Args:
            event: 模型事件
        """
        if event.type == ModelEventType.PREDICT_END:
            logger.info(f"WaveNet5 model evaluation completed.")

            try:
                # 分析初始IIR层的多通道频率响应
                channels = len(self.filter_systems)  # 滤波器数量
                logger.info(f"正在并行分析初始IIR层的{channels}个通道的频率响应")

                # 使用多通道频率响应分析功能
                from visualization.model_analysis import conv1d_frequency_response_multichannel

                # 直接使用init_iir_model进行多通道分析
                systems = conv1d_frequency_response_multichannel(
                    self.init_iir_model,
                    fs=self.fs,
                    f_range=(5, 200),
                    amplitude=1,
                    points=100
                )

                # 创建图表
                plt.figure(figsize=(12, 7))
                plt.title(
                    f"WaveNet5 Initial IIR Layers Channel Frequency Response", fontsize=16)

                # 创建颜色映射
                colors = plt.cm.viridis(np.linspace(0, 1, channels))

                # 绘制每个通道的频率响应
                for i, system in enumerate(systems):
                    # 绘制频率响应
                    gain = system.toabs()
                    freq = system.f
                    plt.loglog(freq, gain, linewidth=2,
                               color=colors[i], alpha=0.8, label=f"Channel {i+1}")

                # 设置图表属性
                plt.xlabel("Frequency (Hz)", fontsize=12)
                plt.ylabel("Gain", fontsize=12)
                plt.grid(True, which='both', linestyle='--', linewidth=0.5)
                plt.legend(loc='best', title="Initial IIR Channels")

                # 保存图像
                save_dir = self.checkpoint_dir
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(
                    save_dir, 'initial_iir_channels_frequency_response.png')
                plt.savefig(save_path, dpi=300)
                logger.info(f"已将初始IIR层频率响应图保存到: {save_path}")

            except Exception as e:
                logger.error(f"绘制频率响应时发生错误: {e}")
                import traceback
                traceback.print_exc()

    def get_layered_models(self):
        """
        获取模型的分层版本列表

        Returns:
            List[tf.keras.Model]: 模型的分层版本列表，按照数据流顺序排列
        """
        return self.layer_to_layer_models

    def get_layers_info(self) -> List[Dict[str, Any]]:
        """
        获取每一层的详细信息，包括精确的输出通道数

        Returns:
            List[Dict[str, Any]]: 包含每一层信息的字典列表
        """
        layers_info = []
        for i, layer in enumerate(self.layer_to_layer_models):
            info = layer.get_layer_info()
            
            # 添加更精确的输出通道数计算
            if i == 0:  # SVF层
                center_freqs = self.model_subcfg.get('init_center_freqs', [])
                info['output_channels'] = len(center_freqs) * 3  # 每个滤波器3个输出：HP、BP、LP
                info['layer_description'] = f"SVF滤波器层 ({len(center_freqs)} 滤波器 × 3 输出)"
            elif i < len(self.layer_to_layer_models) - 1:  # Dense层
                dense_units = self.model_subcfg.get('post_dense_units', 6)
                info['output_channels'] = dense_units
                info['layer_description'] = f"Dense层 {i} ({dense_units} 单元)"
            else:  # 输出层
                info['output_channels'] = 1
                info['layer_description'] = "输出层 (1 单元)"
            
            layers_info.append(info)
        
        return layers_info

    def to_spice(self, output_path: str = None, opamp_config: Dict[str, Any] = None, 
                 use_e96: bool = False, amp: float = 1.0, high_pass_config: Dict[str, Any] = None,
                 power_supply_config: Dict[str, Any] = None):
        """
        导出WaveNet5到分层SPICE模型
        
        参数:
            output_path: 输出路径（用于分层模型时忽略）
            opamp_config: 运放配置
            use_e96: 是否使用E96标准电阻值
            amp: 信号增益倍数
            high_pass_config: 高通滤波器配置字典
            power_supply_config: 电源配置字典，包含vcc和vee电压值
        
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
            # 准备参数字典
            spice_params = {
                'output_path': layer_output_path,
                'use_e96': use_e96,
                'amp': amp if i == 0 else 1.0  # 只在第一层应用增益
            }
            
            # 如果是DenseLayer，添加高通滤波器、运放配置和电源配置参数
            if hasattr(layer, '__class__') and layer.__class__.__name__ == 'DenseLayer':
                if high_pass_config is not None:
                    spice_params['high_pass_config'] = high_pass_config
                if opamp_config is not None:
                    spice_params['opamp_config'] = opamp_config
                if power_supply_config is not None:
                    spice_params['power_supply_config'] = power_supply_config
            
            # 如果是SVFLayer，添加运放配置和电源配置参数
            if hasattr(layer, '__class__') and layer.__class__.__name__ == 'SVFLayer':
                if opamp_config is not None:
                    spice_params['opamp_config'] = opamp_config
                if power_supply_config is not None:
                    spice_params['power_supply_config'] = power_supply_config
            
            spice_obj = layer.to_spice(**spice_params)
            spice_objects.append(spice_obj)
        
        return spice_objects
