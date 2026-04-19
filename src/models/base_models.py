"""
神经网络模型库 - 基础模型模块

此模块包含LSTM、GRN和RNN等基础神经网络模型。
"""

import os
import logging
import matplotlib.pyplot as plt
import os
import json
import time
from calibration_analyzer.exam_class import TimeSeries
import tensorflow as tf
import json
from config import CONF_DROPOUT
import numpy as np
from .utils import merge_config

# 创建 logger
logger = logging.getLogger(__name__)


class ModelEventType:
    # 训练相关事件
    class EPOCH_END:
        ...

    class BEST_LOSS:
        ...

    class BEST_VAL_LOSS:
        ...

    class STOP:
        ...

    # 评估相关事件
    class EVALUATE_START:
        ...

    class EVALUATE_END:
        ...

    # 预测相关事件
    class PREDICT_START:
        ...

    class PREDICT_END:
        ...


class ModelEvent:
    def __init__(self, type: ModelEventType, data=None):
        self.type = type
        self.data = data


class BaseModel:
    def __init__(self):
        self.use_fast_model = False
        self.iir_trainable = False
        self.fast_model_uses_raw_input = False

    def _has_fast_model(self):
        return getattr(self, 'use_fast_model', False) and 'fast_model' in dir(self)

    def _uses_raw_fast_path(self):
        return self._has_fast_model() and getattr(self, 'fast_model_uses_raw_input', False)

    def _uses_feature_fast_path(self):
        return self._has_fast_model() and not getattr(self, 'fast_model_uses_raw_input', False)

    def predict(self, x_input, batch_size=1000*10, use_debug=False, use_scaler=True, **kwargs):
        """
        使用模型进行预测

        Args:
            x_input: 输入数据
            batch_size: 批处理大小
            use_debug: 是否启用调试
            use_scaler: 是否使用缩放
            **kwargs: 透传到底层 Keras predict 的额外参数，例如 verbose

        Returns:
            预测结果
        """
        # 使用训练后的模型进行预测
        # x_features: (batch_size, seq_num, features_num)
        # apply scaler for input
        if use_debug:
            print(
                f'{self.model_name} predict x_range: {x_input.min()} to {x_input.max()}')
        
        # 使用 CombinedScaler 进行输入缩放
        if use_scaler and hasattr(self, 'scaler'):
            x_input = self.scaler.transform_x(x_input.reshape(-1, x_input.shape[-1])).reshape(x_input.shape)
        
        if use_debug:
            print(
                f'{self.model_name} predict x_range(scaled): {x_input.min()} to {x_input.max()}')
            print(f'{self.model_name} predict x shape: {x_input.shape}')
        verbose = kwargs.pop('verbose', 1)
        if self._uses_feature_fast_path():
            print(f'Using fast model to predict')
            iir_out = self.fast_iir(x_input)
            y_pred = self.fast_model.predict(
                iir_out, batch_size=batch_size, verbose=verbose, **kwargs)
        elif self._uses_raw_fast_path():
            print(f'Using fast model to predict')
            y_pred = self.fast_model.predict(
                x_input, batch_size=batch_size, verbose=verbose, **kwargs)
        else:
            y_pred = self.model.predict(
                x_input, batch_size=batch_size, verbose=verbose, **kwargs)
        if use_debug:
            print(f'{self.model_name} predict y shape: {y_pred.shape}')
            plt.figure(figsize=(12, 8))
            plt.plot(x_input[:, 0], label='x_input')
            plt.plot(y_pred[:, 0], label='y_pred')
            plt.legend()
            plt.title(f'{self.model_name} Predict')
            plt.pause(0.1)

        if use_debug:
            print(
                f'{self.model_name} predict y_range: {y_pred.min()} to {y_pred.max()}')
        
        # 使用 CombinedScaler 进行输出反缩放
        if use_scaler and hasattr(self, 'scaler'):
            y_pred = self.scaler.inverse_transform_y(y_pred.reshape(-1, y_pred.shape[-1])).reshape(y_pred.shape)
        
        if use_debug:
            print(
                f'{self.model_name} predict y_range(scaled): {y_pred.min()} to {y_pred.max()}')
        return y_pred

    def exec_callback(self, event: ModelEvent):
        """
        执行回调函数

        Args:
            event: 回调事件
        """
        if getattr(self, 'callback', None) is not None:
            self.callback(event)

    def callback(self, event: ModelEvent):
        """
        回调函数

        Args:
            event: 事件
        """
        pass

    def init_checkpoint(self, checkpoint_dir):
        """
        初始化检查点目录
        """
        self.checkpoint_dir = checkpoint_dir
        # 如果检查点目录不存在，则创建
        if not os.path.exists(self.checkpoint_dir):
            os.makedirs(self.checkpoint_dir)

        # 定义保存最佳权重的路径
        self.best_weights_file = os.path.join(
            self.checkpoint_dir, 'best.weights.h5')

        self.best_val_weights_file = os.path.join(
            self.checkpoint_dir, 'best_val.weights.h5')

    def summary(self):
        """
        打印模型摘要信息
        """
        logger.info(f"{self.model_name} Model:")
        if 'fast_model' in dir(self):
            logger.info(f"{self.model_name} Fast Model:")
            try:
                # 捕获fast_model.summary()的输出
                from io import StringIO
                stream = StringIO()
                self.fast_model.summary(print_fn=lambda x: stream.write(x + '\n'))
                summary_string = stream.getvalue()
                stream.close()
                logger.info(f"\n{summary_string}")
            except Exception as e:
                logger.warning(f"Fast model summary failed: {e}, falling back to direct output")
                self.fast_model.summary()

        try:
            # 捕获model.summary()的输出
            from io import StringIO
            stream = StringIO()
            self.model.summary(print_fn=lambda x: stream.write(x + '\n'))
            summary_string = stream.getvalue()
            stream.close()
            logger.info(f"{summary_string}")
        except Exception as e:
            logger.warning(f"Model summary failed: {e}, falling back to direct output")
            self.model.summary()

    def predict_linspace(
            self,
            start=0.05,
            stop=2,
            fs: int = 2000,
            time_length: float = 1,
            fade_in: float = 0.0,
            fade_out: float = 0.0,
            debug: bool = True,
            save_path=None
    ):
        """
        基于线性间隔生成输入数据并进行预测。

        Args:
            start (float): 生成线性时间序列的起始值。
            stop (float): 生成线性时间序列的终止值。
            fs (int): 采样频率。
            time_length (float): 时间长度（秒）。
            fade_in (float): 渐入比例（0.0 到 1.0）。
            fade_out (float): 渐出比例（0.0 到 1.0）。
            debug (bool): 是否启用调试模式，绘制生成的时间序列和预测结果。
            save_path (str): 保存结果的路径。
        """
        # 生成线性时间序列
        input_tr1 = TimeSeries.fromLinspace(
            start, stop, fs, time_length, fade_in, fade_out)
        input_tr2 = TimeSeries.fromLinspace(
            -stop, -start, fs, time_length, fade_in, fade_out)

        input_tr = TimeSeries.concatenate([input_tr2, input_tr1])

        k1 = 1.0/3.0,
        k3 = 0.5/3.0,
        def fn_ori(x): return k1 * x + k3 * x**3
        def fn_tar(x): return x

        output_ori_tr = input_tr.map(fn_ori)

        # timeseries 预测
        output_comp_tr = self.time_response(
            output_ori_tr)

        # 将numpy数组保存到json文件中
        if save_path is not None:
            data_dict = {
                'input': input_tr.samples.tolist(),
                'output_ori': output_ori_tr.samples.tolist(),
                'output_comp': output_comp_tr.samples.tolist()
            }
            with open(save_path, 'w') as f:
                print(f'Saving predict linspace to {save_path}')
                json.dump(data_dict, f)

        # 绘制预测结果
        if debug:
            if not hasattr(self, 'fig_linspace'):
                self.fig_linspace, (self.ax_origin, self.ax_comp, self.ax_comped) = plt.subplots(
                    1, 3, figsize=(12, 4))
            self.ax_origin.cla()
            self.ax_comp.cla()
            self.ax_comped.cla()

            linewidth = 2.0
            self.ax_origin.plot(
                input_tr.samples, output_ori_tr.samples, label='ORIGIN', marker='', linewidth=linewidth)
            self.ax_origin.set_title('ORIGIN')
            self.ax_origin.legend()

            self.ax_comp.plot(output_ori_tr.samples,
                              output_comp_tr.samples, label='COMP', marker='', linewidth=linewidth)
            self.ax_comp.set_title('COMP')
            self.ax_comp.legend()

            self.ax_comped.plot(
                input_tr.samples, output_comp_tr.samples, label='COMPED', marker='', linewidth=linewidth)
            self.ax_comped.set_title('COMPED')
            self.ax_comped.legend()

            plt.pause(0.1)

    def time_response(self, time_series: TimeSeries, show_tick=False, batch_size=1000, use_scaler=True) -> TimeSeries:
        """
        计算模型对输入时间序列的响应

        Args:
            time_series: 输入时间序列
            show_tick: 是否显示计时信息
            batch_size: 批处理大小

        Returns:
            输出时间序列
        """
        tic = time.time()
        if time_series.fs != self.fs:
            raise ValueError(
                f'输入时间序列的采样频率 {time_series.fs} 与模型的采样频率 {self.fs} 不一致。')
        # 计算时间响应
        x_input = np.array(time_series.samples).reshape(1, -1, 1)
        y_pred = self.predict(
            x_input, batch_size=batch_size, use_scaler=use_scaler)
        ret = TimeSeries(y_pred[0, :, 0], time_series.fs)
        toc = time.time()
        if show_tick:
            print(f'rnn time response: {toc - tic:.2f} s')
        return ret

    def save_weights(self, weights_file):
        """
        保存模型权重

        Args:
            weights_file: 权重文件路径
        """
        if self._uses_feature_fast_path():
            fast_weights_file = weights_file.replace('best', 'fast_best')
            self.fast_model.save_weights(fast_weights_file)
            # 获取 fast_model 的权重，然后拼接上 iir 的权重
            weight_fast = self.fast_model.get_weights()
            weight_normal = self.model.get_weights()
            # 从后往前更新，因为前面的权重是 iir 的权重
            for i in range(-1, -len(weight_fast)-1, -1):
                weight_normal[i] = weight_fast[i]  # 从后往前更新
            self.model.set_weights(weight_normal)
            self.model.save_weights(weights_file)
            self.save_weights_json(weights_file)
            return
        if self._uses_raw_fast_path():
            fast_weights_file = weights_file.replace('best', 'fast_best')
            self.fast_model.save_weights(weights_file)
            self.fast_model.save_weights(fast_weights_file)
            self.save_weights_json(weights_file, model_obj=self.fast_model)
            return
        self.model.save_weights(weights_file)
        self.save_weights_json(weights_file)

    def save_weights_json(self, weights_file, model_obj=None):
        """
        将权重保存为JSON格式

        Args:
            weights_file: 权重文件路径
        """
        json_file_path = weights_file.replace('.h5', '.json')
        target_model = self.model if model_obj is None else model_obj
        weights = target_model.weights
        # 将权重转换为可序列化的 Python 列表
        weights_serializable = []
        for weight in weights:
            weight_name = weight.name
            weight_value = weight.numpy().tolist()
            weight_shape = weight.shape.as_list()
            config_dict = {}
            if 'kan' in weight_name:
                config = self.kan.get_config()
                config_dict = {
                    'units': config['units'],
                    'grid_size': config['grid_size'],
                    'spline_order': config['spline_order'],
                    'grid_range': config['grid_range'],
                }
            weights_serializable.append(
                {
                    'name': weight_name,
                    'shape': weight_shape,
                    'config': config_dict,
                    'value': weight_value
                }
            )
        # 保存为 JSON 文件
        with open(json_file_path, 'w') as json_file:
            json.dump(weights_serializable, json_file, indent=4)

    def load_weights(self, weights_file):
        """
        加载模型权重

        Args:
            weights_file: 权重文件路径
        """
        if self._uses_feature_fast_path():
            fast_weights_file = weights_file.replace('best', 'fast_best')
            logger.info(f'Loading fast model weights from {fast_weights_file}')
            self.fast_model.load_weights(fast_weights_file)
            # 获取 fast_model 的权重，然后拼接上 iir 的权重
            weight_fast = self.fast_model.get_weights()
            weight_normal = self.model.get_weights()
            # update weight_fast to weight_normal
            # 从后往前更新，因为前面的权重是 iir 的权重
            for i in range(-1, -len(weight_fast)-1, -1):
                weight_normal[i] = weight_fast[i]  # 从后往前更新
            # 更新 model 的权重
            self.model.set_weights(weight_normal)
            self.model.load_weights(weights_file)
            self.save_weights_json(weights_file)
            return
        if self._uses_raw_fast_path():
            logger.info(f'Loading fast model weights from {weights_file}')
            self.fast_model.load_weights(weights_file)
            self.save_weights_json(weights_file, model_obj=self.fast_model)
            return
        self.model.load_weights(weights_file)
        self.save_weights_json(weights_file)

    def compile(self, *args, **kwargs):
        """
        编译模型
        """
        self.model.compile(*args, **kwargs)
        if 'fast_model' in dir(self):
            self.fast_model.compile(*args, **kwargs)

    def fit(self,  *args,  **kwargs):
        """
        训练模型
        """
        # 添加回调函数列表
        if 'callbacks' not in kwargs:
            kwargs['callbacks'] = []

        if self._uses_feature_fast_path():
            # 只有固定 IIR 前端时，才能安全地复用预计算特征的 fast path。
            # 将 iir 的输出作为 fast_model 的输入
            iir_features = self.fast_iir(args[0])
            # iir_features shape: (batch_size, seq_num, features_num)
            validation_data = kwargs.get('validation_data')
            if 'validation_data' in kwargs:
                validation_data = kwargs['validation_data']
                x_val = validation_data[0]
                iir_features_val = self.fast_iir(x_val)
                validation_data = (iir_features_val, *validation_data[1:])
            args = (iir_features, *args[1:])
            kwargs['validation_data'] = validation_data
            history = self.fast_model.fit(*args, **kwargs)
        elif self._uses_raw_fast_path():
            history = self.fast_model.fit(*args, **kwargs)
        else:
            history = self.model.fit(*args, **kwargs)

        return history

    def evaluate(self, *args, **kwargs):
        """
        评估模型
        """
        if self._uses_feature_fast_path():
            print('Using fast model to evaluate')
            iir_features = self.fast_iir(args[0])
            args = (iir_features, *args[1:])
            return self.fast_model.evaluate(*args, **kwargs)
        if self._uses_raw_fast_path():
            print('Using fast model to evaluate')
            return self.fast_model.evaluate(*args, **kwargs)
        return self.model.evaluate(*args, **kwargs)

    def set_scaler(self, scaler):
        """
        设置数据缩放器

        Args:
            scaler: 集成缩放器 (CombinedScaler)
        """
        if hasattr(scaler, 'scaler_x') and hasattr(scaler, 'scaler_y'):
            # 使用新的集成缩放器
            self.scaler = scaler
        else:
            raise ValueError("scaler 必须是 CombinedScaler 实例")


class LSTM(BaseModel):
    def __init__(self,
                 lstm_units=64,  # Number of LSTM units
                 lstm_dropout=CONF_DROPOUT,  # Dropout rate
                 activation='tanh',  # LSTM activation function
                 fs=2000,  # Sampling frequency
                 checkpoint_dir='data',  # Directory for saving data
                 model_subcfg={},
                 ):

        # Initialize LSTM model
        self.model_name = 'LSTM'
        print(f'LSTM activation: {activation}')
        self.model = tf.keras.Sequential()
        self.model.add(tf.keras.layers.LSTM(
            units=lstm_units,
            activation=activation,
            dropout=lstm_dropout,
            return_sequences=True
        ))
        # Optional Dense Layer after LSTM
        self.model.add(tf.keras.layers.Dense(lstm_units, activation='relu'))
        self.model.add(tf.keras.layers.Dense(1))  # Output layer
        self.model.build(input_shape=(None, None, 1))

        # Store configurations
        self.fs = fs
        self.init_checkpoint(checkpoint_dir)

    def fit(self, *args,  **kwargs):
        # 添加回调函数列表
        if 'callbacks' not in kwargs:
            kwargs['callbacks'] = []

        history = self.model.fit(*args, **kwargs)

        return history

    def load_weights(self, filepath):
        """
        Load the model weights from a specified file.
        """
        self.model.load_weights(filepath)
        self.save_weights_json(filepath)

    def save_weights(self, filepath):
        """
        Save the model weights to a specified file.
        """
        self.model.save_weights(filepath)
        self.save_weights_json(filepath)

    def save_weights_json(self, weights_file):
        """
        保存权重为JSON格式
        """
        json_file_path = weights_file.replace('.h5', '.json')
        weights = self.model.weights
        # 将权重转换为可序列化的 Python 列表
        weights_serializable = []
        for weight in weights:
            weight_name = weight.name
            weight_value = weight.numpy().tolist()
            weight_shape = weight.shape.as_list()
            config_dict = {}
            weights_serializable.append(
                {
                    'name': weight_name,
                    'shape': weight_shape,
                    'config': config_dict,
                    'value': weight_value
                }
            )
        # 保存为 JSON 文件
        with open(json_file_path, 'w') as json_file:
            json.dump(weights_serializable, json_file, indent=4)

    def init_checkpoint(self, checkpoint_dir):
        """
        初始化检查点目录
        """
        self.checkpoint_dir = checkpoint_dir
        # 如果检查点目录不存在，则创建
        if not os.path.exists(self.checkpoint_dir):
            os.makedirs(self.checkpoint_dir)

        # 定义保存最佳权重的路径
        self.best_weights_file = os.path.join(
            self.checkpoint_dir, 'best.weights.h5')

        self.best_val_weights_file = os.path.join(
            self.checkpoint_dir, 'best_val.weights.h5')


class GRN(LSTM):
    def __init__(self,
                 grn_units=64,  # Number of GRN units (similar to LSTM units)
                 grn_dropout=CONF_DROPOUT,  # Dropout rate for GRN
                 activation='tanh',  # GRN activation function
                 fs=2000,  # Sampling frequency
                 checkpoint_dir='data',  # Directory for saving data
                 model_subcfg={},
                 ):
        # Initialize GRN model by calling the parent class (LSTM)
        self.model_name = 'GRN'
        self.fs = fs
        self.checkpoint_dir = checkpoint_dir
        if not os.path.exists(self.checkpoint_dir):
            os.makedirs(self.checkpoint_dir)

        # Now, modify the model from LSTM to GRN (using GRU as an approximation)
        self.model = tf.keras.Sequential()

        # Replace LSTM with GRN (GRU as a proxy for GRN for now)
        self.model.add(tf.keras.layers.GRU(
            units=grn_units,
            activation=activation,
            dropout=grn_dropout,
            return_sequences=True,  # Keep sequence output to preserve time steps
        ))

        # Optional Dense Layer after GRN (processing each time step individually)
        self.model.add(tf.keras.layers.Dense(grn_units, activation='silu'))
        # Output layer to match the desired output shape (batch_size, time_steps, 1)
        # Output layer (1 value per time step)
        self.model.add(tf.keras.layers.Dense(1))

        # Build the model with input shape (None, None, 1)
        self.model.build(input_shape=(None, None, 1))

        # Checkpoint directory configuration (using parent's directory and file setup)
        self.init_checkpoint(checkpoint_dir)


class RNN(LSTM):
    def __init__(self,
                 rnn_units=64,            # RNN ????
                 rnn_dropout=CONF_DROPOUT,  # RNN ? dropout ?
                 rnn_activation='tanh',   # RNN ?????
                 fs=2000,                 # ????
                 checkpoint_dir='data',  # ????????
                 model_subcfg={},
                 ):
        self.model_name = 'RNN'
        self.fs = fs
        self.checkpoint_dir = checkpoint_dir
        if not os.path.exists(self.checkpoint_dir):
            os.makedirs(self.checkpoint_dir)

        default_subcfg = {
            'recurrent_units': rnn_units,
            'rnn_layers': 1,
            'rnn_dropout': rnn_dropout,
            'recurrent_dropout': 0.0,
            'rnn_activation': rnn_activation,
            'dense_layers': 1,
            'dense_units': rnn_units,
            'dense_activation': 'silu',
            'output_activation': None,
        }
        subcfg = merge_config(default_subcfg, model_subcfg)
        self.subcfg = subcfg
        self.model_subcfg = subcfg

        recurrent_units = int(subcfg['recurrent_units'])
        rnn_layers = int(subcfg['rnn_layers'])
        dense_layers = int(subcfg['dense_layers'])
        dense_units = int(subcfg['dense_units'])
        if recurrent_units <= 0:
            raise ValueError("model_subcfg['recurrent_units'] must be > 0")
        if rnn_layers <= 0:
            raise ValueError("model_subcfg['rnn_layers'] must be > 0")
        if dense_layers < 0:
            raise ValueError("model_subcfg['dense_layers'] must be >= 0")
        if dense_layers > 0 and dense_units <= 0:
            raise ValueError("model_subcfg['dense_units'] must be > 0")

        self.model = tf.keras.Sequential()
        for _ in range(rnn_layers):
            self.model.add(tf.keras.layers.SimpleRNN(
                units=recurrent_units,
                activation=subcfg['rnn_activation'],
                dropout=float(subcfg['rnn_dropout']),
                recurrent_dropout=float(subcfg['recurrent_dropout']),
                return_sequences=True,
            ))

        for _ in range(dense_layers):
            self.model.add(tf.keras.layers.Dense(
                dense_units,
                activation=subcfg['dense_activation']
            ))

        self.model.add(tf.keras.layers.Dense(
            1,
            activation=subcfg['output_activation']
        ))
        self.model.build(input_shape=(None, None, 1))

        self.init_checkpoint(checkpoint_dir)


class LSTMTransformer(BaseModel):
    def __init__(self,
                 lstm_units=64,
                 activation='tanh',
                 fs=2000,
                 checkpoint_dir='data',
                 model_subcfg={},
                 ):
        super().__init__()
        self.model_name = 'LSTMTransformer'
        self.fs = fs

        default_subcfg = {
            'lstm_dropout': CONF_DROPOUT,
            'transformer_num_heads': 2,
            'transformer_ff_dim': max(lstm_units * 4, 8),
            'transformer_layers': 2,
            'transformer_dropout': 0.1,
            'attention_pool_size': 1,
            'dense_units': lstm_units,
            'dense_activation': 'relu',
        }
        subcfg = merge_config(default_subcfg, model_subcfg)

        num_heads = int(subcfg['transformer_num_heads'])
        if num_heads <= 0:
            raise ValueError('transformer_num_heads 必须大于 0')
        if lstm_units % num_heads != 0:
            raise ValueError(
                f'lstm_units({lstm_units}) 必须能被 transformer_num_heads({num_heads}) 整除')

        transformer_layers = int(subcfg['transformer_layers'])
        if transformer_layers <= 0:
            raise ValueError('transformer_layers 必须大于 0')

        attention_pool_size = int(subcfg['attention_pool_size'])
        if attention_pool_size <= 0:
            raise ValueError('attention_pool_size 必须大于 0')

        inputs = tf.keras.Input(shape=(None, 1), name='input')
        x = tf.keras.layers.LSTM(
            units=lstm_units,
            activation=activation,
            dropout=float(subcfg['lstm_dropout']),
            return_sequences=True,
            name='lstm_backbone'
        )(inputs)

        key_dim = lstm_units // num_heads
        dropout_rate = float(subcfg['transformer_dropout'])
        ff_dim = int(subcfg['transformer_ff_dim'])

        for layer_idx in range(transformer_layers):
            attention_context = x
            if attention_pool_size > 1:
                attention_context = tf.keras.layers.AveragePooling1D(
                    pool_size=attention_pool_size,
                    strides=attention_pool_size,
                    padding='same',
                    name=f'transformer_context_pool_{layer_idx}'
                )(attention_context)

            attention_output = tf.keras.layers.MultiHeadAttention(
                num_heads=num_heads,
                key_dim=key_dim,
                dropout=dropout_rate,
                name=f'transformer_mha_{layer_idx}'
            )(x, attention_context, attention_context)
            attention_output = tf.keras.layers.Dropout(
                dropout_rate,
                name=f'transformer_dropout_attn_{layer_idx}'
            )(attention_output)
            x = tf.keras.layers.LayerNormalization(
                epsilon=1e-6,
                name=f'transformer_ln_attn_{layer_idx}'
            )(x + attention_output)

            ff_output = tf.keras.layers.Dense(
                ff_dim,
                activation='relu',
                name=f'transformer_ffn_expand_{layer_idx}'
            )(x)
            ff_output = tf.keras.layers.Dropout(
                dropout_rate,
                name=f'transformer_dropout_ffn_{layer_idx}'
            )(ff_output)
            ff_output = tf.keras.layers.Dense(
                lstm_units,
                name=f'transformer_ffn_project_{layer_idx}'
            )(ff_output)
            x = tf.keras.layers.LayerNormalization(
                epsilon=1e-6,
                name=f'transformer_ln_ffn_{layer_idx}'
            )(x + ff_output)

        dense_units = int(subcfg['dense_units'])
        if dense_units > 0:
            x = tf.keras.layers.Dense(
                dense_units,
                activation=subcfg['dense_activation'],
                name='post_dense'
            )(x)

        outputs = tf.keras.layers.Dense(1, name='output')(x)
        self.model = tf.keras.Model(inputs=inputs, outputs=outputs, name=self.model_name)
        self.init_checkpoint(checkpoint_dir)
