from keras.models import Sequential
import pandas as pd
import numpy as np
import logging
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.utils import Sequence
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt
from calibration_analyzer import dataparser
import plotly.graph_objects as go
from tqdm import tqdm
from scipy import signal
from sklearn.utils import shuffle
import config
import os
from calibration_analyzer import exam_process, exam_class
from calibration_analyzer.exam_class import TimeSeries
from typing import List

# 创建logger
logger = logging.getLogger(__name__)


def _log_cuda_diagnostics_when_no_gpu() -> None:
    if os.environ.get('METNL_CUDA_LOST_GPU_DETECTED') != '1':
        logger.warning("Failed to set GPU usage, no GPU found")
        return

    healthy_indices = os.environ.get('METNL_CUDA_HEALTHY_GPU_INDICES', '')
    visible_devices = os.environ.get('CUDA_VISIBLE_DEVICES', '')
    if healthy_indices:
        logger.warning(
            'TensorFlow still failed to initialize CUDA after masking lost GPUs. '
            'This usually means the NVIDIA driver is in a globally poisoned state. '
            'healthy_gpu_indices=%s, CUDA_VISIBLE_DEVICES=%s. '
            'Use an admin device restart for the lost GPU or reboot the machine to recover GPU training.',
            healthy_indices,
            visible_devices,
        )
        return

    logger.warning(
        'Detected lost NVIDIA GPU state and no healthy GPU remained. Falling back to CPU. '
        'Recover the device with an admin device restart or reboot the machine.'
    )


def initialize_device():
    # 检查是否有可用的GPU
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            # 设置TensorFlow仅使用第一块GPU
            tf.config.experimental.set_visible_devices(gpus[0], 'GPU')
            tf.config.experimental.set_memory_growth(gpus[0], True)
            logger.info(f"Using GPU: {gpus[0]}")
        except RuntimeError as e:
            logger.error(f"Error in setting GPU: {e}")
            logger.warning("Error in setting GPU, falling back to CPU")
            # 如果设置GPU失败，则使用CPU
            tf.config.set_visible_devices([], 'GPU')
    else:
        logger.info("No GPU found, using CPU")


# 初始化设备
# initialize_device()

using_gpu = None


def set_using_gpu(enable: bool):
    global using_gpu
    if using_gpu == enable:
        logger.info(f"GPU usage already set to {enable}")
        return
    logger.info(f"Setting GPU usage to {enable}")
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            if enable:
                tf.config.experimental.set_visible_devices(gpus[0], 'GPU')
                tf.config.experimental.set_memory_growth(gpus[0], True)
                logger.info(f"Using GPU: {gpus[0]}")
                using_gpu = True
            else:
                tf.config.set_visible_devices([], 'GPU')
                logger.info("Using CPU")
                using_gpu = False
        except RuntimeError as e:
            logger.error(f"Error in setting GPU: {e}")
            logger.warning("Error in setting GPU, falling back to CPU")
            tf.config.set_visible_devices([], 'GPU')
    else:
        _log_cuda_diagnostics_when_no_gpu()
        using_gpu = False


def load_data(file_path):
    """
    加载数据。

    参数:
    file_path : str
        CSV文件路径。

    返回:
    input_data : ndarray
        输入数据。
    output_data : ndarray
        输出数据。
    """
    data = pd.read_csv(file_path, header=None)
    input_data = data.iloc[:, 0].values
    output_data = data.iloc[:, 1].values
    return input_data, output_data


def load_data_2channel(file_path_input, file_path_output):
    """
    加载 Time series 数据。
    """
    input_list: List[TimeSeries] = exam_class.TimeSeries.load_multichannel_from_binary(
        file_path_input)
    output_list: List[TimeSeries] = exam_class.TimeSeries.load_multichannel_from_binary(
        file_path_output)
    input_data = np.array([ts.samples for ts in input_list])
    output_data = np.array([ts.samples for ts in output_list])

    # 将二维数组拍平为一维
    input_data_flattened = input_data.flatten()
    output_data_flattened = output_data.flatten()

    return input_data_flattened, output_data_flattened


def plot_data(input_data, output_data, start_s, view_length_s, freq_collect, filtered=False):
    """
    抽样画出数据图像。

    参数:
    input_data : ndarray
        输入数据。
    output_data : ndarray
        输出数据。
    start_s : int
        起始时间，单位为秒。
    view_length_s : int
        显示长度，单位为秒。
    freq_collect : int
        采样频率。
    filtered : bool
        是否显示滤波后的数据。
    """
    start_index = int(start_s * freq_collect)
    end_index = int(view_length_s * freq_collect + start_index)
    plt.plot(input_data[start_index:end_index],
             label='Filtered Output' if filtered else 'Output')
    plt.plot(output_data[start_index:end_index],
             label='Filtered Input' if filtered else 'Input')
    plt.legend()
    plt.show()


def filter_data(input_data, output_data, fs=20000, lowcut=0.5, highcut=500, order=2):
    """
    对原始数据进行滤波。

    参数:
    input_data : ndarray
        输入数据。
    output_data : ndarray
        输出数据。
    fs : int
        采样频率。
    lowcut : float
        低频截止频率。
    highcut : float
        高频截止频率。
    order : int
        滤波器阶数。

    返回:
    input_data_filtered : ndarray
        滤波后的输入数据。
    output_data_filtered : ndarray
        滤波后的输出数据。
    """
    b, a = signal.butter(order, [lowcut, highcut], fs=fs, btype='band')
    input_data_filtered = signal.filtfilt(b, a, input_data)
    output_data_filtered = signal.filtfilt(b, a, output_data)
    return input_data_filtered, output_data_filtered


def create_input_features(input_data, n_timesteps, freq_list=config.FREQ_LIST, keep_incomplete=False):
    """
    生成基于给定频率列表和时间步长数的输入特征。

    参数:
    input_data : ndarray
        输入数据，形状为 (n_samples,)。
    n_timesteps : int
        时间步长的数量。
    freq_list : list of int
        要分解的频率列表。
    keep_incomplete : bool, optional
        是否保留数据不足的特征。如果为True，将保留不完整的特征；如果为False（默认），则删除这些特征。

    返回:
    new_input_data : ndarray
        生成的特征，形状为 (有效样本数, n_timesteps, len(freq_list))。
    """
    n_samples = len(input_data)
    n_features = len(freq_list)

    # 计算每个频率所需的最小索引位置
    min_indices = np.array([n_timesteps * freq - 1 for freq in freq_list])

    # 找出满足所有频率条件的样本索引
    valid_indices = np.arange(n_samples) >= min_indices.max()

    # 如果不保留不完整特征，只保留有效样本
    if not keep_incomplete:
        valid_samples = np.arange(n_samples)[valid_indices]
    else:
        valid_samples = np.arange(n_samples)

    # 准备输出矩阵
    new_input_data = np.zeros((len(valid_samples), n_timesteps, n_features))

    # 使用NumPy广播和高级索引提取特征，并添加进度条
    for j, freq in enumerate(tqdm(freq_list, desc="Processing frequencies")):
        indices = np.arange(n_timesteps) * freq
        sample_indices = valid_samples[:, None] - indices[None, :]
        new_input_data[:, :, j] = input_data[sample_indices]

    return new_input_data


def create_features(input_data, output_data, n_timesteps, freq_list=config.FREQ_LIST, using_cache=True):
    """
    Creates features and output data ready for machine learning models.

    Parameters:
    input_data : ndarray
        Input data, shape (n_samples,).
    output_data : ndarray
        Output data, shape (n_samples,).
    n_timesteps : int
        Number of timesteps.
    freq_list : list of int
        List of frequencies.

    Returns:
    new_input_data : ndarray
        Features data, shape (n_samples, n_timesteps, len(freq_list)).
    new_output_data : ndarray
        Supervisory data, shape (n_samples,).
    """
    logger.info("Creating features...")
    data_length = len(input_data)
    if using_cache:
        filename = "cache/cache_" + \
            "_".join(map(str, [n_timesteps] +
                     freq_list + [data_length])) + ".npz"
        if not os.path.exists("cache"):
            logger.info("Creating cache directory")
            os.makedirs("cache")
        if os.path.exists(filename):
            logger.info(f"Loading cache file: {filename}")
            with np.load(filename) as data:
                new_input_data = data['new_input_data'].copy()
                new_output_data = data['new_output_data'].copy()
            return new_input_data, new_output_data
        else:
            logger.info("Cache file not found, creating new features")

    logger.info("Creating new features")
    new_input_data = create_input_features(input_data, n_timesteps, freq_list)

    # 截取 new_output_data，使其长度与 new_input_data 一致
    valid_sample_count = new_input_data.shape[0]
    new_output_data = np.array(output_data.copy())[-valid_sample_count:]
    logger.info(f"Features created, shape: {new_input_data.shape}")

    if using_cache:
        logger.info(f"Saving cache file: {filename}")
        np.savez(filename, new_input_data=new_input_data,
                 new_output_data=new_output_data)
    return new_input_data, new_output_data


def clean_cache():
    logger.info("Cleaning cache files in directory")
    for file in os.listdir("cache"):
        logger.info(f"Removing {file}")
        os.remove(os.path.join("cache", file))


def print_data_characteristics(data, name):
    """
    打印数据的统计信息。

    参数:
    data : ndarray
        数据。
    name : str
        数据名称。
    """
    logger.info(f"Characteristics of {name}:")
    logger.info(f"  Shape: {data.shape}")
    logger.info(f"  Max value: {np.max(data)}")
    logger.info(f"  Min value: {np.min(data)}")


def create_or_load_model(n_timesteps, n_features, model_weights_path='model/model.weights.h5', units=128):
    """
    训练模型。

    参数:
    train_X : ndarray
        训练特征数据。
    train_y : ndarray
        训练监督数据。
    n_timesteps : int
        时间步数。
    n_features : int
        特征数。
    model_weights_path : str
        模型权重保存路径。


    返回:
    model : Sequential
        训练好的模型。
    """
    model = Sequential()
    logger.info("Creating model...")
    logger.info(f"Model input shape: {n_timesteps}, {n_features}")
    logger.info(f"Model weights path: {model_weights_path}")
    logger.info(f"Model units: {units}")
    model.add(LSTM(units=units, activation='relu',
              input_shape=(n_timesteps, n_features)))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    logger.info("Model summary:")
    # 捕获model.summary()的输出
    from io import StringIO
    stream = StringIO()
    model.summary(print_fn=lambda x: stream.write(x + '\n'))
    summary_string = stream.getvalue()
    stream.close()
    logger.info(f"\n{summary_string}")

    try:
        model.load_weights(model_weights_path)
    except Exception as e:
        logger.warning(f'Cannot load weights: {e}')

    logger.info("Model created")
    return model


class DataGenerator(Sequence):
    def __init__(self, X_data, Y_data, batch_size=128):
        logger.info("Creating data generator...")
        logger.info(f"Batch size: {batch_size}")
        logger.info(f"Data shape: {X_data.shape}, {Y_data.shape}")
        self.X_data = X_data
        self.Y_data = Y_data
        self.batch_size = batch_size
        self.indices = np.arange(len(X_data))

    def __len__(self):
        return int(np.ceil(len(self.X_data) / self.batch_size))

    def __getitem__(self, index):
        batch_indices = self.indices[index *
                                     self.batch_size:(index + 1) * self.batch_size]
        X_batch = self.X_data[batch_indices]
        Y_batch = self.Y_data[batch_indices]
        return X_batch, Y_batch

    def on_epoch_end(self):
        np.random.shuffle(self.indices)


def train_module(model, train_X, train_Y, model_weights_path='model/model.weights.h5', batch_size=128, epochs=1):
    # create model folder if not exists
    if not os.path.exists("model"):
        os.makedirs("model")
    logger.info("Training model...")
    logger.info(f"Model weights path: {model_weights_path}")
    logger.info(f"Batch size: {batch_size}")
    logger.info(f"Epochs: {epochs}")
    logger.info(f"Train data shape: {train_X.shape}, {train_Y.shape}")
    train_generator = DataGenerator(train_X, train_Y, batch_size=batch_size)

    checkpoint = ModelCheckpoint(model_weights_path, save_weights_only=True)
    checkpoint2 = ModelCheckpoint(
        f'model/model{{epoch:02d}}.weights.h5', save_weights_only=True)

    model.fit(train_generator, epochs=epochs, verbose=1,
              callbacks=[checkpoint, checkpoint2])


def predict_and_plot(model, input_data, output_data, start_s, view_length_s, freq_collect, num_features, freq_list=config.FREQ_LIST):
    """
    预测并绘制结果。

    参数:
    model : Sequential
        训练好的模型。
    test_X : ndarray
        测试特征数据。
    test_y : ndarray
        测试监督数据。
    start_s : int
        起始时间，单位为秒。
    view_length_s : int
        显示长度，单位为秒。
    freq_collect : int
        采样频率。
    """
    start_index = start_s * freq_collect
    view_length_index = int(view_length_s * freq_collect)
    end_index = int(start_index + view_length_index)

    test_X, test_Y = create_features(
        input_data[start_index:end_index], output_data[start_index:end_index], num_features, freq_list)

    # 只对需要绘制的部分数据进行预测
    logger.info("Predicting...")
    logger.info(f"Test data shape: {test_X.shape}, {test_Y.shape}")
    predected_Y = model.predict(test_X, batch_size=128*128)

    plt.plot(input_data[start_index:end_index], label='Input')
    plt.plot(test_Y, label='True')
    plt.plot(predected_Y, label='Predicted')
    plt.legend(loc='upper right')
    plt.show()


def generate_sine_wave(freq, sample_rate, duration, A=100):
    """
    生成一个正弦波信号。

    参数:
    freq : float
        正弦波的频率（Hz）。
    sample_rate : int
        采样率（Hz）。
    duration : float
        正弦波的持续时间（秒）。
    """
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return A * np.sin(2 * np.pi * freq * t)


def frequency_response_test(model, freq_start=1, freq_end=500, num_points=30, sample_rate=20000, duration=10, freq_list=config.FREQ_LIST, dump_file_path='data/data.json'):
    """
    对模型进行频率响应测试，输入不同频率的正弦波，记录输出。

    参数:
    model : Sequential
        训练好的神经网络模型。
    freq_start : float
        起始频率（Hz）。
    freq_end : float
        结束频率（Hz）。
    num_points : int
        频率点数。
    sample_rate : int
        采样率（Hz）。
    duration : float
        输入信号的持续时间（秒）。
    """
    # Generate logarithmically spaced frequencies
    freqs = np.logspace(np.log10(freq_start),
                        np.log10(freq_end), num=num_points)
    responses = []
    times = []

    dataRecords: list[dataparser.DataRecord] = []
    for freq in freqs:
        # Generate a sine wave input
        input_signal = generate_sine_wave(freq, sample_rate, duration)

        input_fealures = create_input_features(
            input_signal, model.input_shape[1], freq_list)

        # Predict model output
        output_signal = model.predict(input_fealures)

        response = output_signal.flatten()
        time = np.linspace(0, duration, len(response))
        # Store the output signal
        dataRecord = dataparser.DataRecord(
            dataparser.DataIdentifierParam(f'var=1,freq={freq}'), list(input_signal), list(response))
        dataRecords.append(dataRecord)
        responses.append(response)
        times.append(time)

    dataRecordList = dataparser.DataRecordList()
    dataRecordList.load_from_data_records(dataRecords)
    dataRecordList.dump_to_json_file(dump_file_path)
    # Plot the frequency response
    plt.figure(figsize=(10, 8))
    for i, freq in enumerate(freqs):
        plt.subplot(len(freqs), 1, i+1)
        plt.plot(times[i], responses[i])
        plt.title(f"Frequency: {freq:.2f} Hz")
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
    plt.tight_layout()
    plt.show()

    return responses


def main(data_path):
    input_data, output_data = load_data(data_path)

    # plot_data(input_data, output_data, start_s=136,
    #           view_length_s=10, freq_collect=1000*20)

    input_data_filtered, output_data_filtered = filter_data(
        input_data, output_data)

    # plot_data(input_data_filtered, output_data_filtered, start_s=136,
    #   view_length_s=10, freq_collect=1000*20, filtered=True)

    new_input_data, new_output_data = create_features(
        input_data_filtered, output_data_filtered, 8, [1, 10, 100, 1000])

    print_data_characteristics(input_data_filtered, "Filtered Input data")
    print_data_characteristics(output_data_filtered, "Filtered Output data")
    print_data_characteristics(new_input_data, "New input data")
    print_data_characteristics(new_output_data, "New output data")

    n_train = int(0.8 * len(new_input_data))
    test_X, test_Y = new_input_data[n_train:], new_output_data[n_train:]
    train_X, train_Y = shuffle(
        new_input_data, new_output_data, random_state=42)

    model = create_or_load_model(
        n_timesteps=new_input_data.shape[1], n_features=new_input_data.shape[2])

    train_module(model, train_X, train_Y)

    predict_and_plot(model, test_X, test_Y, start_s=300,
                     view_length_s=5, freq_collect=20*1000)


if __name__ == "__main__":
    main('data/data.csv')
