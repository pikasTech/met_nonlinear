"""
神经网络模型库 - 卷积模型模块

此模块包含RVTDCNN等基于卷积神经网络的模型及相关工具函数。
"""

import os
import hashlib
import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Conv2D, Flatten, Dense, Input
from tensorflow.keras.models import Model
from tqdm import tqdm
import matplotlib.pyplot as plt
from .base_models import BaseModel, LSTM
from .utils import merge_config
from config import CONF_DROPOUT


# 全局变量，用于create_image_batch函数的调试
ax_create_image = None


def create_image_batch(
    X,
    memory_depth,
    nonlinearity_order,
    energy_window=5,
    cache_dir="./cache",
    use_debug=False,
):
    """
    通过向量化加速，将 (B, T, 1) 批量时序数据转换为 (B*T, M, N+1, 1) 的图像数据（最后一列为"能量"），并支持缓存。

    Args:
        X: 输入数据，形状为 (B, T, 1)，其中B为批次大小，T为序列长度
        memory_depth: 记忆深度，即提取的历史样本数量
        nonlinearity_order: 非线性阶数，即计算多少阶非线性特征
        energy_window: 能量窗口大小，用于计算短时能量
        cache_dir: 缓存目录，用于保存中间结果
        use_debug: 是否开启调试模式

    Returns:
        转换后的图像数据，形状为 (B*T, M, N+1, 1)
    """
    global ax_create_image
    VERSION = 4
    if use_debug:
        if ax_create_image is None:
            fig, ax_create_image = plt.subplots(1, 1, figsize=(12, 8))

    # 1) 创建缓存目录
    os.makedirs(cache_dir, exist_ok=True)

    # 2) 根据输入数据和参数生成哈希
    hash_input = (
        X.tobytes() +
        str(memory_depth).encode() +
        str(nonlinearity_order).encode() +
        str(energy_window).encode() +
        str(VERSION).encode()
    )
    hash_value = hashlib.md5(hash_input).hexdigest()
    cache_file = os.path.join(cache_dir, f"cache_{hash_value}.npy")

    # 3) 若缓存存在, 直接读取
    if os.path.exists(cache_file):
        print(f"[Cache Hit] Loading cached data from {cache_file}")
        cached_data = np.load(cache_file)
        # 检查形状是否正确
        if cached_data.shape[1:] != (memory_depth, nonlinearity_order + 1, 1):
            raise ValueError(
                f"Invalid image shape: {cached_data.shape}, "
                f"expected ({memory_depth}, {nonlinearity_order + 1}, 1) at axis=1."
            )
        return cached_data

    # 4) 若缓存不存在，则开始计算
    print(f"[Cache Miss] Generating data and saving to cache: {cache_file}")

    B, T, _ = X.shape

    # ---- 4.1) 预先计算 X^2 的前缀和，用于能量计算 ----
    # prefix_sums[b, t] = sum_{k=0 to t-1} of X[b,k]^2
    # 因此 prefix_sums 的 shape 为 (B, T+1)，前面多留一位0
    prefix_sums = np.zeros((B, T+1), dtype=X.dtype)
    for b in range(B):
        # 注意：np.cumsum 不包含 0，故这里手动在前面补一个 0
        prefix_sums[b, 1:] = np.cumsum(X[b, :, 0]**2)

    # ---- 4.2) 准备输出数组，最后会 reshape 成 (B*T, M, N+1, 1) ----
    # 先用四维 (B, T, M, N+1)，最后加 1 个通道维
    images = np.zeros(
        (B, T, memory_depth, nonlinearity_order + 1), dtype=X.dtype)

    # ---- 4.3) 构造辅助：非线性阶的指数 (1 到 N) ----
    exponents = np.arange(1, nonlinearity_order + 1,
                          dtype=X.dtype)  # shape (N,)

    # ---- 4.4) 逐个 (b,t) 处理，并在内部向量化计算 M 个 memory_depth 样本 ----
    with tqdm(total=B*T, desc="Converting Time Series to Images", unit="images") as pbar:
        for b in range(B):
            # prefix_sums[b] 可在这儿重复使用
            for t_idx in range(T):
                # (a) 构造下标数组: t_idx - [0,1,2,...,M-1]
                #     用来一次性取 memory_depth 个倒序值
                idx_array = t_idx - np.arange(memory_depth)
                # clip 到合法范围 [0, T-1]，并记录哪些是负数（需要置0）
                neg_mask = (idx_array < 0)
                idx_array_clipped = np.clip(idx_array, 0, T-1)

                # (b) 从 X[b, :] 里一次性取出这 M 个值（被 clip 到 >=0）
                signal_vals = X[b, idx_array_clipped, 0].copy()
                # 将超出范围（本该是负索引）的那部分置0
                signal_vals[neg_mask] = 0.0

                # (c) 计算非线性项：sign * abs^j (broadcast)
                #     先取绝对值+符号，再做多阶幂
                val_signs = np.sign(signal_vals)                   # shape (M,)
                abs_vals = np.abs(signal_vals)                     # shape (M,)
                # 利用广播： (M,1) ^ (1,N) => (M,N)
                # powers[i, j] = abs_vals[i]**exponents[j]
                powers = abs_vals.reshape(-1, 1) ** exponents
                # powers = signal_vals.reshape(-1, 1) ** exponents
                # shape (M, N)
                nonlinear_terms = val_signs.reshape(-1, 1) * powers
                # nonlinear_terms = powers  # shape (M, N)

                # (d) 计算能量：prefix_sums 做 O(1) 求区间平方和
                #     对每个 i，能量区间是 [idx-energy_window+1, idx]
                #     这里 idx = idx_array[i], 要先 clip >= 0
                start_array = (idx_array_clipped -
                               (energy_window - 1)).clip(min=0)
                end_array = idx_array_clipped
                # prefix_sums[b, end+1] - prefix_sums[b, start]
                # 注：end+1 是因为 prefix_sums 多预留了一个位置
                energy_vals = prefix_sums[b, end_array +
                                          1] - prefix_sums[b, start_array]
                # 若原本 idx<0，则能量置0
                energy_vals[neg_mask] = 0.0

                # (e) 存入 images[b,t_idx] => shape (M, N+1)
                #     前 N 列为 nonlinear_terms，最后 1 列是 energy
                images[b, t_idx, :, :nonlinearity_order] = nonlinear_terms
                images[b, t_idx, :, nonlinearity_order] = energy_vals

                pbar.update(1)
                if use_debug:
                    if b > 10:
                        ax_create_image.clear()
                        ax_create_image.plot(signal_vals, label="Signal")
                        ax_create_image.plot(
                            nonlinear_terms, label="Nonlinear Terms")
                        ax_create_image.plot(energy_vals, label="Energy")
                        ax_create_image.legend()
                        ax_create_image.set_title(f"Time Step {t_idx} (b={b})")
                        plt.pause(0.001)

    # ---- 4.5) 调整形状为 (B*T, M, N+1, 1) 并存缓存 ----
    images = images.reshape((B*T, memory_depth, nonlinearity_order + 1, 1))

    np.save(cache_file, images)
    return images


class RVTDCNN(LSTM):
    """
    时变递归动态CNN模型(Recursive Varying Time-Delay Convolutional Neural Network)

    该模型通过将时间序列转换为图像数据，利用CNN处理非线性时变系统。
    """

    def __init__(self,
                 memory_depth=20,         # m，延迟深度
                 nonlinearity_order=4,    # n，非线性阶数
                 filters=32,              # 卷积核数量
                 kernel_size=(5, 3),      # 卷积核大小
                 activation='tanh',       # 激活函数
                 fs=2000,                 # 采样率 (可根据需求保留)
                 checkpoint_dir='data',   # 保存模型的路径
                 dense_units=64,          # 全连接层单元数
                 dropout=CONF_DROPOUT,    # Dropout 概率
                 model_subcfg={},         # 模型子配置（可选）
                 ):
        """
        初始化 RVTDCNN 模型
        """
        self.model_name = 'RVTDCNN'
        self.fs = fs
        self.checkpoint_dir = checkpoint_dir
        self.dense_units = dense_units

        # 若不存在 checkpoint 目录则创建
        if not os.path.exists(self.checkpoint_dir):
            os.makedirs(self.checkpoint_dir)

        # 构造 CNN 模型（Sequential 方式）
        self.filters = filters
        self.memory_depth = memory_depth
        self.nonlinearity_order = nonlinearity_order
        self.kernel_size = kernel_size
        self.activation = activation
        self.dropout = dropout
        self.model = self.build_model()
        self.init_checkpoint(checkpoint_dir)

    def build_model(self):
        """
        构建CNN模型

        注意: 这里假设输入 shape 是 (B*T, M, N, 1).
        因为我们打算在 Python 端手动把 (B, T, 1) => (B*T, M, N, 1).
        """
        input_layer = Input(shape=(self.memory_depth, self.nonlinearity_order+1, 1),
                            name="ImageInput")

        conv_out = Conv2D(filters=self.filters,
                          kernel_size=self.kernel_size,
                          activation=self.activation,
                          padding='same')(input_layer)
        flat = Flatten()(conv_out)
        # 增加 dropout
        flat = tf.keras.layers.Dropout(self.dropout)(flat)
        # 全连接
        full = Dense(self.dense_units, activation=self.activation)(flat)
        out = Dense(1, activation=None)(full)  # 对每个图输出 1 值

        model = Model(inputs=input_layer, outputs=out)
        return model

    def fit(self, *args, **kwargs):
        """
        重写 fit 方法，以便将输入转换为图像数据
        """
        # 添加回调函数列表
        X = args[0]
        y = args[1]
        if 'callbacks' not in kwargs:
            kwargs['callbacks'] = []
        images = create_image_batch(
            X, self.memory_depth, self.nonlinearity_order)
        y_reshaped = y.reshape(-1, 1)
        # check the shape of images: (B*T, M, N, 1)
        if images.shape[1:] != (self.memory_depth, self.nonlinearity_order+1, 1):
            raise ValueError(
                f"Invalid image shape: {images.shape}, expected {(self.memory_depth, self.nonlinearity_order+1, 1)}")
        T = X.shape[1]
        # adjust batchsize
        if 'batch_size' in kwargs:
            batch_size = kwargs['batch_size']
            kwargs['batch_size'] = batch_size * T
        if 'validation_data' in kwargs:
            validation_data = kwargs['validation_data']
            x_val = validation_data[0]
            images_val = create_image_batch(
                x_val, self.memory_depth, self.nonlinearity_order)
            y_val = validation_data[1]
            y_val_reshaped = y_val.reshape(-1, 1)
            validation_data = (images_val, y_val_reshaped,
                               *validation_data[2:])
            kwargs['validation_data'] = validation_data
        # print shape
        print(f"images.shape: {images.shape}")
        print(f"y_reshaped.shape: {y_reshaped.shape}")
        args = (images, y_reshaped, *args[2:])
        return self.model.fit(*args, **kwargs)

    def predict(self, x_input, batch_size=1000*10, use_debug=False,
                use_scaler=True, **kwargs):
        """
        使用模型进行预测

        Args:
            x_input: 输入数据，形状为 (B, T, 1)
            batch_size: 批次大小
            use_debug: 是否开启调试模式
            use_scaler: 是否使用归一化
            **kwargs: 透传到底层 Keras predict 的额外参数，例如 verbose

        Returns:
            预测结果，形状为 (B, T, 1)
        """
        # 使用训练后的模型进行预测
        # x_features: (batch_size, seq_num, features_num)
        # apply scaler for input
        if use_debug:
            print(
                f'{self.model_name} predict x_range: {x_input.min()} to {x_input.max()}')
        if use_scaler and hasattr(self, 'scaler_x_offset'):
            x_input = (x_input - self.scaler_x_offset) / \
                self.scaler_x_ratio
        if use_debug:
            print(
                f'{self.model_name} predict x_range(scaled): {x_input.min()} to {x_input.max()}')
            print(f'{self.model_name} predict x shape: {x_input.shape}')

        x_images = create_image_batch(
            x_input, self.memory_depth, self.nonlinearity_order)  # (B*T, M, N, 1)

        T = x_input.shape[1]
        # adjust batchsize
        batch_size = batch_size * T
        verbose = kwargs.pop('verbose', 1)
        y_pred = self.model.predict(
            x_images, batch_size=batch_size, verbose=verbose, **kwargs)  # (B * T, 1)
        # reshape to (B, T, 1)
        y_pred = y_pred.reshape(-1, T, 1)

        if use_debug:
            print(f'{self.model_name} predict y shape: {y_pred.shape}')

        if use_debug:
            print(
                f'{self.model_name} predict y_range: {y_pred.min()} to {y_pred.max()}')
        if use_scaler and hasattr(self, 'scaler_y_offset'):
            y_pred = y_pred * self.scaler_y_ratio + self.scaler_y_offset
        if use_debug:
            print(
                f'{self.model_name} predict y_range(scaled): {y_pred.min()} to {y_pred.max()}')
        return y_pred

    def evaluate(self, *args, **kwargs):
        """
        评估模型性能
        """
        x_image = create_image_batch(
            args[0], self.memory_depth, self.nonlinearity_order)
        T = args[0].shape[1]
        # adjust batchsize
        if 'batch_size' in kwargs:
            batch_size = kwargs['batch_size']
            kwargs['batch_size'] = batch_size * T
        y_out = args[1]  # (B, T, 1) -> (B*T, 1)
        y_out = y_out.reshape(-1, 1)
        # check shape
        if x_image.shape[1:] != (self.memory_depth, self.nonlinearity_order+1, 1):
            raise ValueError(
                f"Invalid image shape: {x_image.shape}, expected {(self.memory_depth, self.nonlinearity_order+1, 1)}")
        if y_out.shape[1] != 1:
            raise ValueError(
                f"Invalid y_out shape: {y_out.shape}, expected (B*T, 1)")
        args = (x_image, y_out, *args[2:])
        return self.model.evaluate(*args, **kwargs)



def _validate_positive_int(value, field_name):
    value = int(value)
    if value <= 0:
        raise ValueError(f"{field_name} must be greater than 0")
    return value


def _validate_non_negative_float(value, field_name):
    value = float(value)
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative")
    return value


def _maybe_apply_activation(x, activation, name):
    if activation:
        return tf.keras.layers.Activation(activation, name=name)(x)
    return x


def _maybe_apply_dropout(x, dropout_rate, name):
    if dropout_rate > 0:
        return tf.keras.layers.Dropout(dropout_rate, name=name)(x)
    return x


def _build_post_dense_stack(x, subcfg):
    if not subcfg['post_dense']:
        return x

    for layer_idx in range(subcfg['post_dense_layers']):
        x = tf.keras.layers.Conv1D(
            filters=subcfg['post_dense_units'],
            kernel_size=1,
            padding='same',
            name=f'post_dense_{layer_idx + 1}'
        )(x)
        x = _maybe_apply_activation(
            x,
            subcfg['post_dense_activation'],
            name=f'post_dense_activation_{layer_idx + 1}'
        )
    return x


class OneDCNN(BaseModel):
    """A plain causal 1D CNN baseline for sequence modeling."""

    def __init__(self,
                 kernel_units=64,
                 fs=2000,
                 activation='relu',
                 checkpoint_dir='data',
                 model_subcfg={},
                 inference_config=None,
                 ):
        super().__init__()

        default_subcfg = {
            'conv_layers': 2,
            'init_conv_units': 4,
            'kernel_size': 8,
            'conv_activation': None,
            'dropout_rate': 0.0,
            'post_dense': False,
            'post_dense_units': 1,
            'post_dense_activation': None,
            'post_dense_layers': 1,
            'final_activation': None,
        }

        self.subcfg = merge_config(default_subcfg, model_subcfg)
        self.model_name = '1DCNN'
        self.fs = fs
        self.kernel_units = _validate_positive_int(kernel_units, 'kernel_units')
        self.conv_layers = _validate_positive_int(self.subcfg['conv_layers'], 'conv_layers')
        self.init_conv_units = _validate_positive_int(self.subcfg['init_conv_units'], 'init_conv_units')
        self.kernel_size = _validate_positive_int(self.subcfg['kernel_size'], 'kernel_size')
        self.dropout_rate = _validate_non_negative_float(self.subcfg['dropout_rate'], 'dropout_rate')
        self.subcfg['post_dense_units'] = _validate_positive_int(self.subcfg['post_dense_units'], 'post_dense_units')
        self.subcfg['post_dense_layers'] = _validate_positive_int(self.subcfg['post_dense_layers'], 'post_dense_layers')
        self.activation = self.subcfg['conv_activation'] or activation
        self.inference_config = inference_config or {}

        self.model = self.build_model()
        self.init_checkpoint(checkpoint_dir)

    def build_model(self):
        inputs = tf.keras.layers.Input(shape=(None, 1), name='input')
        x = inputs

        for layer_idx in range(self.conv_layers):
            filters = self.init_conv_units if layer_idx == 0 else self.kernel_units
            x = tf.keras.layers.Conv1D(
                filters=filters,
                kernel_size=self.kernel_size,
                padding='causal',
                name=f'conv_{layer_idx + 1}'
            )(x)
            x = _maybe_apply_activation(x, self.activation, name=f'conv_activation_{layer_idx + 1}')
            x = _maybe_apply_dropout(x, self.dropout_rate, name=f'conv_dropout_{layer_idx + 1}')

        x = _build_post_dense_stack(x, self.subcfg)
        x = _maybe_apply_activation(x, self.subcfg['final_activation'], name='final_activation')

        outputs = tf.keras.layers.Conv1D(
            filters=1,
            kernel_size=1,
            padding='same',
            name='output_conv'
        )(x)

        return tf.keras.Model(inputs=inputs, outputs=outputs, name=self.model_name)


class TCN(BaseModel):
    """A temporal convolutional network built from dilated residual blocks."""

    def __init__(self,
                 kernel_units=64,
                 fs=2000,
                 activation='relu',
                 checkpoint_dir='data',
                 model_subcfg={},
                 inference_config=None,
                 ):
        super().__init__()

        default_subcfg = {
            'dilations': [1, 2, 4, 8],
            'kernel_size': 3,
            'skip_initial_conv': False,
            'init_conv_units': 8,
            'skip_output_conv': False,
            'use_gating': False,
            'final_activation': None,
            'block_activation': None,
            'gate_activation': 'relu',
            'dropout_rate': 0.0,
            'use_residual': True,
            'block_dense': False,
            'block_dense_units': 1,
            'combine_blocks_by_add': False,
            'post_dense': False,
            'post_dense_units': 1,
            'post_dense_activation': None,
            'post_dense_layers': 1,
            'use_parallel_blocks': False,
        }

        self.subcfg = merge_config(default_subcfg, model_subcfg)
        if self.subcfg['use_gating']:
            raise ValueError('TCN does not support WaveNet-style gating')
        if self.subcfg['use_parallel_blocks']:
            raise ValueError('TCN does not support parallel WaveNet blocks')
        if self.subcfg['combine_blocks_by_add']:
            raise ValueError('TCN does not support combine_blocks_by_add')

        self.model_name = 'TCN'
        self.fs = fs
        self.kernel_units = _validate_positive_int(kernel_units, 'kernel_units')
        self.kernel_size = _validate_positive_int(self.subcfg['kernel_size'], 'kernel_size')
        self.init_conv_units = _validate_positive_int(self.subcfg['init_conv_units'], 'init_conv_units')
        self.dropout_rate = _validate_non_negative_float(self.subcfg['dropout_rate'], 'dropout_rate')
        self.subcfg['block_dense_units'] = _validate_positive_int(self.subcfg['block_dense_units'], 'block_dense_units')
        self.subcfg['post_dense_units'] = _validate_positive_int(self.subcfg['post_dense_units'], 'post_dense_units')
        self.subcfg['post_dense_layers'] = _validate_positive_int(self.subcfg['post_dense_layers'], 'post_dense_layers')
        self.dilations = [
            _validate_positive_int(dilation, 'dilation')
            for dilation in self.subcfg['dilations']
        ]
        self.block_activation = self.subcfg['block_activation'] or activation
        self.inference_config = inference_config or {}

        self.model = self.build_model()
        self.init_checkpoint(checkpoint_dir)

    def _temporal_block(self, x, dilation_rate, block_idx):
        residual = x
        block_channels = self.kernel_units
        if self.subcfg['block_dense']:
            block_channels = self.subcfg['block_dense_units']

        for conv_idx in range(2):
            x = tf.keras.layers.Conv1D(
                filters=self.kernel_units,
                kernel_size=self.kernel_size,
                dilation_rate=dilation_rate,
                padding='causal',
                name=f'temporal_block_{block_idx}_conv_{conv_idx + 1}'
            )(x)
            x = _maybe_apply_activation(
                x,
                self.block_activation,
                name=f'temporal_block_{block_idx}_activation_{conv_idx + 1}'
            )
            x = _maybe_apply_dropout(
                x,
                self.dropout_rate,
                name=f'temporal_block_{block_idx}_dropout_{conv_idx + 1}'
            )

        if self.subcfg['block_dense']:
            x = tf.keras.layers.Conv1D(
                filters=block_channels,
                kernel_size=1,
                padding='same',
                name=f'temporal_block_{block_idx}_dense'
            )(x)

        if self.subcfg['use_residual']:
            if residual.shape[-1] != block_channels:
                residual = tf.keras.layers.Conv1D(
                    filters=block_channels,
                    kernel_size=1,
                    padding='same',
                    name=f'temporal_block_{block_idx}_residual_projection'
                )(residual)
            x = tf.keras.layers.Add(name=f'temporal_block_{block_idx}_residual_add')([x, residual])

        x = _maybe_apply_activation(
            x,
            self.block_activation,
            name=f'temporal_block_{block_idx}_output_activation'
        )
        return x

    def build_model(self):
        inputs = tf.keras.layers.Input(shape=(None, 1), name='input')

        if self.subcfg['skip_initial_conv']:
            x = inputs
        else:
            x = tf.keras.layers.Conv1D(
                filters=self.init_conv_units,
                kernel_size=1,
                padding='same',
                name='initial_projection'
            )(inputs)
            x = _maybe_apply_activation(x, self.block_activation, name='initial_projection_activation')

        if x.shape[-1] != self.kernel_units:
            x = tf.keras.layers.Conv1D(
                filters=self.kernel_units,
                kernel_size=1,
                padding='same',
                name='channel_projection'
            )(x)

        for block_idx, dilation_rate in enumerate(self.dilations, start=1):
            x = self._temporal_block(x, dilation_rate, block_idx)

        x = _build_post_dense_stack(x, self.subcfg)
        x = _maybe_apply_activation(x, self.subcfg['final_activation'], name='final_activation')

        if self.subcfg['skip_output_conv']:
            outputs = tf.keras.layers.Dense(1, name='output_dense')(x)
        else:
            outputs = tf.keras.layers.Conv1D(
                filters=1,
                kernel_size=1,
                padding='same',
                name='output_conv'
            )(x)

        return tf.keras.Model(inputs=inputs, outputs=outputs, name=self.model_name)
