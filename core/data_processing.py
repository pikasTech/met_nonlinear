import os
import hashlib
import numpy as np
import logging
from typing import List, Tuple, Dict, Any, Optional
import matplotlib.pyplot as plt
from typing import List, Tuple
from calibration_analyzer import exam_process, exam_class
from calibration_analyzer.exam_class import TimeSeries, System
from calibration_analyzer.waveprocessor import WaveData, WaveRecord, WaveProcessor
from calibration_analyzer import config as calibration_config
import json
import re

# 创建 logger
logger = logging.getLogger(__name__)


def pre_process_data(
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
) -> Tuple['System', List['TimeSeries'], List['TimeSeries'], List[float]]:
    input_tr_list, output_tr_list, freq_list = exam_class.load_data_json_to_time_sereis(
        data_path)

    # 计算中间索引
    mid_index = len(input_tr_list) // 2

    # 创建 figure（仅在首次使用 debug 时创建一次）
    if use_debug:
        if not plt.get_fignums():
            plt.figure(figsize=(12, 8))
        plt.clf()

    if time_cliped_s is not None:
        # 先截取
        input_tr_list = [input_tr_item.clip(
            start_time=input_tr_item.time_length() - time_cliped_s * 2,
            end_time=input_tr_item.time_length()) for input_tr_item in input_tr_list]

        output_tr_list = [output_tr_item.clip(
            start_time=output_tr_item.time_length() - time_cliped_s * 2,
            end_time=output_tr_item.time_length()) for output_tr_item in output_tr_list]

    if use_resample:
        # 再降采样
        input_tr_list = [input_tr_item.resample(
            fs) for input_tr_item in input_tr_list]
        output_tr_list = [output_tr_item.resample(
            fs) for output_tr_item in output_tr_list]
        if use_debug and False:
            plt.plot(input_tr_list[mid_index].time, input_tr_list[mid_index].samples,
                     label='Input Resampled Mid Index')
            plt.plot(output_tr_list[mid_index].time, output_tr_list[mid_index].samples,
                     label='Output Resampled Mid Index')
            plt.title("Resampled Data")
            plt.legend()
            plt.grid(True)
            plt.pause(0.01)

    output_tr_list = [output_tr_item.apply_gain(
        16*calibration_config.CONF_GAIN_RATIO).apply_gain(amply) for output_tr_item in output_tr_list]
    input_tr_list = [input_tr_item.apply_gain(
        amply) for input_tr_item in input_tr_list]
    if use_debug and False:
        plt.plot(input_tr_list[mid_index].time, input_tr_list[mid_index].samples,
                 label='Input After Gain Mid Index')
        plt.plot(output_tr_list[mid_index].time, output_tr_list[mid_index].samples,
                 label='Output After Gain Mid Index')
        plt.title("Gain Applied")
        plt.legend()
        plt.grid(True)
        plt.pause(0.01)

    # 去掉直流分量
    output_tr_list = [output_tr_item.remove_dc()
                      for output_tr_item in output_tr_list]
    input_tr_list = [input_tr_item.remove_dc()
                     for input_tr_item in input_tr_list]
    if use_debug:
        plt.plot(input_tr_list[mid_index].time, input_tr_list[mid_index].samples,
                 label='Input DC Removed Mid Index')
        plt.plot(output_tr_list[mid_index].time, output_tr_list[mid_index].samples,
                 label='Output DC Removed Mid Index')
        plt.title("DC Removed")
        plt.legend()
        plt.grid(True)
        plt.pause(0.01)

    # 滤波
    if filter_bandpass:
        output_tr_list = [output_tr_item.filter(filter_type='bandpass', cutoff_freq=filter_bandpass_freq)
                          for output_tr_item in output_tr_list]
        input_tr_list = [input_tr_item.filter(filter_type='bandpass', cutoff_freq=filter_bandpass_freq)
                         for input_tr_item in input_tr_list]
        if use_debug:
            plt.plot(input_tr_list[mid_index].time, input_tr_list[mid_index].samples,
                     label='Input Filtered Mid Index')
            plt.plot(output_tr_list[mid_index].time, output_tr_list[mid_index].samples,
                     label='Output Filtered Mid Index')
            plt.title("Filtered Data")
            plt.legend()
            plt.grid(True)
            plt.pause(0.01)

    # 截取时间
    if time_cliped_s is not None:
        output_tr_list = [output_tr_item.clip(
            start_time=0.5*time_cliped_s, end_time=time_cliped_s*1.5) for output_tr_item in output_tr_list]
        input_tr_list = [input_tr_item.clip(
            start_time=0.5*time_cliped_s, end_time=time_cliped_s*1.5) for input_tr_item in input_tr_list]

    # 渐入渐出
    if fade_in > 0 or fade_out > 0:
        output_tr_list = [output_tr_item.apply_fade(
            fade_in, fade_out) for output_tr_item in output_tr_list]
        input_tr_list = [input_tr_item.apply_fade(
            fade_in, fade_out) for input_tr_item in input_tr_list]
        if use_debug:
            plt.plot(input_tr_list[mid_index].time,
                     input_tr_list[mid_index].samples, label='Input Faded Mid Index')
            plt.plot(output_tr_list[mid_index].time,
                     output_tr_list[mid_index].samples, label='Output Faded Mid Index')
            plt.title("Faded Data")
            plt.legend()
            plt.grid(True)
            plt.pause(0.01)

    logger.info(f'freq_list: {freq_list}')
    return input_tr_list, output_tr_list, freq_list


def pre_process_data_M50(
        data_info_list,
        index,
        amply=0.006,
        use_resample=True,
        fade_in=0.3,
        fade_out=0.0,
        time_cliped_s=2.0,
        filter_bandpass=True,
        filter_bandpass_freq=[10, 500],
        fs=2000,
        use_debug=False
) -> Tuple['System', List['TimeSeries'], List['TimeSeries'], List[float]]:
    # 检查数据列表是否为空
    if not data_info_list:
        raise ValueError("数据集为空！请检查数据路径是否正确，以及数据文件是否存在。")
    
    # 检查索引是否有效
    if index >= len(data_info_list):
        raise IndexError(f"数据索引 {index} 超出范围！数据集只有 {len(data_info_list)} 个文件。")
    
    # 检查文件路径是否存在
    file_path = data_info_list[index].data_file_path
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"数据文件不存在: {file_path}")
    
    input_tr, output_tr, freq_list = pre_process_data(
        file_path,
        amply=amply,
        use_resample=use_resample,
        fade_in=fade_in,
        fade_out=fade_out,
        time_cliped_s=time_cliped_s,
        filter_bandpass=filter_bandpass,
        filter_bandpass_freq=filter_bandpass_freq,
        fs=fs,
        use_debug=use_debug
    )
    system = System.fromTimeSeries(
        input_tr, output_tr, frequencies=freq_list, use_parallel=False)
    return system, input_tr, output_tr, freq_list


def generate_cache_hash(params_dict: Dict[str, Any]) -> str:
    """
    根据参数字典生成一个唯一的哈希值

    Args:
        params_dict: 包含关键参数的字典

    Returns:
        str: 哈希字符串(8位)
    """
    # 将参数字典转换为字符串
    param_str = json.dumps(params_dict, sort_keys=True, default=str)
    # 生成哈希
    hash_obj = hashlib.md5(param_str.encode())
    return hash_obj.hexdigest()[:8]  # 取前8位作为简短标识


def load_from_cache(dataset_type: str, cache_hash: str, attributes: List[str],
                    use_debug: bool = True) -> Optional[Dict[str, np.ndarray]]:
    """
    从缓存中加载数据

    Args:
        dataset_type: 数据集类型名称
        cache_hash: 缓存哈希值
        attributes: 要加载的属性列表
        use_debug: 是否启用调试打印

    Returns:
        Dict: 包含加载的属性数据的字典，如果加载失败则返回None
    """
    cache_dir = f'cache/features_{dataset_type}_{cache_hash}'

    try:
        loaded_data = {}
        for attr in attributes:
            loaded_data[attr] = np.load(
                f'{cache_dir}/{attr}.npy', allow_pickle=True)

        if use_debug:
            logger.info(f"已从缓存加载数据: {dataset_type}_{cache_hash}")

        return loaded_data
    except Exception as e:
        if use_debug:
            logger.warning(f"缓存加载失败: {e}")
        return None


def save_to_cache(dataset_type: str, cache_hash: str, data_dict: Dict[str, np.ndarray],
                  use_debug: bool = False) -> None:
    """
    将数据保存到缓存

    Args:
        dataset_type: 数据集类型名称
        cache_hash: 缓存哈希值
        data_dict: 包含要保存的数据的字典，键为属性名，值为要保存的数据
        use_debug: 是否启用调试打印
    """
    cache_dir = f'cache/features_{dataset_type}_{cache_hash}'
    os.makedirs(cache_dir, exist_ok=True)

    for attr, data in data_dict.items():
        np.save(f'{cache_dir}/{attr}.npy', data)

    if use_debug:
        logger.info(f"数据已缓存到: {cache_dir}/")


def select_feature_vector(
    features: List[np.ndarray],
    magn_indices=None,
    freq_indices=None,
    sample_points_per_sweep=None,
    use_debug=False
) -> List[np.ndarray]:
    """
    Select specific features from multiple input arrays using given indices.

    Args:
    features: List of feature arrays, each with shape (magn_num, freq_num, points_num)
    magn_indices: List of magnitude indices to select
    freq_indices: List of frequency indices to select
    sample_points_per_sweep: Number of points to select per sweep
    use_debug: Enable debug printing

    Returns:
    List of selected feature arrays, maintaining input order
    """
    # Validate inputs
    if not features:
        raise ValueError("Features list cannot be empty")

    shape = features[0].shape
    if not all(f.shape == shape for f in features):
        raise ValueError("All feature arrays must have the same shape")

    if len(shape) != 3:
        raise ValueError(f"Features must be 3D arrays. Got shape={shape}")

    # Set default indices if None
    if magn_indices is None:
        magn_indices = list(range(shape[0]))
    if freq_indices is None:
        freq_indices = list(range(shape[1]))

    # Select features
    selected_features = []
    for feature in features:
        selected = feature[np.ix_(magn_indices, freq_indices)]
        if sample_points_per_sweep is not None:
            selected = selected[:, :, :sample_points_per_sweep]
        selected_features.append(selected)

    if use_debug:
        print(f"Original shape: {shape}")
        print(f"Selected shape: {selected_features[0].shape}")

    return selected_features


class Dataset_COMP:
    def __init__(
            self,
            fs=2000,
            time_cliped_s=2.0
    ):
        self.magn_num = 0
        self.fs = fs
        self.time_cliped_s = time_cliped_s
        self.freq_num = 0
        self.magn_list = []
        self.freq_list = []
        self.inputs: np.ndarray = None
        self.output_ori: np.ndarray = None
        self.output_tar: np.ndarray = None
        self.type = 'COMP'  # 默认类型，子类会覆盖
        return

    def apply_inverse_transform(self, config):
        """
        应用波形反相处理（通用方法，所有Dataset子类共享）
        
        Args:
            config: 配置对象，包含dataset.inverse_origin/inverse_target/inverse_input参数
        """
        if not config or not hasattr(config, 'dataset') or not isinstance(config.dataset, dict):
            print("未找到dataset配置，跳过反相处理")
            return
        
        # 提取反相配置
        inverse_origin = config.dataset.get('inverse_origin', False)
        inverse_target = config.dataset.get('inverse_target', False)
        inverse_input = config.dataset.get('inverse_input', False)
        
        # 应用反相处理
        inverse_actions = []
        if inverse_input and self.inputs is not None:
            self.inputs = -self.inputs
            inverse_actions.append("inputs")
        if inverse_origin and self.output_ori is not None:
            self.output_ori = -self.output_ori
            inverse_actions.append("output_ori")
        if inverse_target and self.output_tar is not None:
            self.output_tar = -self.output_tar
            inverse_actions.append("output_tar")
        
        if inverse_actions:
            print(f"波形反相处理完成 - 处理了: {', '.join(inverse_actions)}")
        else:
            print("未启用任何波形反相处理")

    def __len__(self):
        return self.output_ori.shape[0]

    def reshape2feature(self, data):
        # data shaple: (magn_num, freq_num, points_num)
        # feature shape: (seq_num=magn_num*freq_num, points_num, 1)
        seq_num = data.shape[0] * data.shape[1]
        return data.reshape(seq_num, data.shape[2], 1)

    def reshape2sample(self, feature):
        # feature shape: (seq_num, points_num, 1)
        # sample_shape: (magn_num, freq_num, points_num)
        # feature reshape to (magn_num, freq_num, points_num)
        magn_num = self.magn_num
        freq_num = self.freq_num
        return feature.reshape(magn_num, freq_num, -1)

    def select(self, magn_indices=None, freq_indices=None, sample_points_per_sweep=None, use_debug=False) -> 'Dataset_COMP':
        """
        Select a subset of the dataset using specified indices and create a new Dataset_COMP instance.

        Args:
            magn_indices: List of magnitude indices to select
            freq_indices: List of frequency indices to select
            sample_points_per_sweep: Number of points to select per sweep
            use_debug: Enable debug printing

        Returns:
            A new Dataset_COMP instance containing the selected data
        """
        # Create new dataset instance
        new_dataset = Dataset_COMP()

        # Select features using select_feature_vector
        selected_features = select_feature_vector(
            [self.inputs, self.output_ori, self.output_tar],
            magn_indices=magn_indices,
            freq_indices=freq_indices,
            sample_points_per_sweep=sample_points_per_sweep,
            use_debug=use_debug
        )

        # Assign selected features to new dataset
        new_dataset.inputs = selected_features[0]
        new_dataset.output_ori = selected_features[1]
        new_dataset.output_tar = selected_features[2]

        # Update magnitude and frequency lists
        if magn_indices is not None:
            new_dataset.magn_list = [self.magn_list[i] for i in magn_indices]
        else:
            new_dataset.magn_list = self.magn_list.copy()

        if freq_indices is not None:
            new_dataset.freq_list = [self.freq_list[i] for i in freq_indices]
        else:
            new_dataset.freq_list = self.freq_list.copy()

        # Update dimensions
        new_dataset.magn_num = len(new_dataset.magn_list)
        new_dataset.freq_num = len(new_dataset.freq_list)
        new_dataset.fs = self.fs
        new_dataset.time_cliped_s = self.time_cliped_s
        new_dataset.type = self.type  # 复制数据集类型

        return new_dataset

    def to_csv(self, folder_path: str, config=None) -> None:
        """
        将数据集转换为CSV格式并保存。

        文件按照magnitude和frequency的索引命名为magx_freqx.csv，
        每个CSV文件包含两列数据：origin和target。

        Args:
            folder_path: CSV文件的保存路径
            config: 可选配置对象，用于获取频率范围配置
        """
        import os
        import pandas as pd

        # 创建文件夹（如果不存在）
        os.makedirs(folder_path, exist_ok=True)

        # 遍历所有的magnitude和frequency组合
        for mag_idx in range(self.magn_num):
            for freq_idx in range(self.freq_num):
                # 获取当前组合的数据
                origin_data = self.output_ori[mag_idx, freq_idx, :]
                target_data = self.output_tar[mag_idx, freq_idx, :]

                # 创建DataFrame
                df = pd.DataFrame({
                    'origin': origin_data,
                    'target': target_data
                })

                # 使用配置的频率范围或默认值
                default_range = [10, 128]
                if config is not None:
                    freq_range_hz = getattr(config, 'dataset', {}).get('freq_range_hz', default_range)
                else:
                    freq_range_hz = default_range
                    
                if self.freq_list[freq_idx] < freq_range_hz[0] or self.freq_list[freq_idx] > freq_range_hz[1]:
                    continue
                # 生成文件名
                filename = f"mag{self.magn_list[mag_idx]}_freq{self.freq_list[freq_idx]}.csv"
                filepath = os.path.join(folder_path, filename)

                # 保存CSV文件
                df.to_csv(filepath, index=False)

        print(f"数据已成功保存至 {folder_path}")

    def shuffle_and_split_data(
            self,
            random_seed=42,
            use_points=1000,
            copy_train=False) -> Tuple['Dataset_COMP', 'Dataset_COMP', 'Dataset_COMP', 'Dataset_COMP']:
        """
        return dataset_train, dataset_test, dataset_ns_train, dataset_ns_test
        """
        train_features, test_features, ns_train_features, ns_test_features = shuffle_and_split_data(
            [self.inputs, self.output_ori, self.output_tar],
            random_seed=random_seed,
            use_points=use_points,
            copy_train=copy_train
        )
        dataset_train = Dataset_COMP()
        dataset_test = Dataset_COMP()
        dataset_ns_train = Dataset_COMP()
        dataset_ns_test = Dataset_COMP()
        
        # 保留原始数据集的类型
        dataset_train.type = self.type
        dataset_test.type = self.type
        dataset_ns_train.type = self.type
        dataset_ns_test.type = self.type

        dataset_train.inputs = train_features[0]
        dataset_train.output_ori = train_features[1]
        dataset_train.output_tar = train_features[2]
        dataset_train.magn_num = train_features[0].shape[0]
        dataset_train.freq_num = train_features[0].shape[1]
        dataset_train.magn_list = self.magn_list
        dataset_train.freq_list = self.freq_list
        dataset_train.fs = self.fs
        dataset_train.time_cliped_s = train_features[0].shape[2] / self.fs

        dataset_test.inputs = test_features[0]
        dataset_test.output_ori = test_features[1]
        dataset_test.output_tar = test_features[2]
        dataset_test.magn_num = test_features[0].shape[0]
        dataset_test.freq_num = test_features[0].shape[1]
        dataset_test.magn_list = self.magn_list
        dataset_test.freq_list = self.freq_list
        dataset_test.fs = self.fs
        dataset_test.time_cliped_s = test_features[0].shape[2] / self.fs

        dataset_ns_train.inputs = ns_train_features[0]
        dataset_ns_train.output_ori = ns_train_features[1]
        dataset_ns_train.output_tar = ns_train_features[2]
        dataset_ns_train.magn_num = ns_train_features[0].shape[0]
        dataset_ns_train.freq_num = ns_train_features[0].shape[1]
        dataset_ns_train.magn_list = self.magn_list
        dataset_ns_train.freq_list = self.freq_list
        dataset_ns_train.fs = self.fs
        dataset_ns_train.time_cliped_s = ns_train_features[0].shape[2] / self.fs

        dataset_ns_test.inputs = ns_test_features[0]
        dataset_ns_test.output_ori = ns_test_features[1]
        dataset_ns_test.output_tar = ns_test_features[2]
        dataset_ns_test.magn_num = ns_test_features[0].shape[0]
        dataset_ns_test.freq_num = ns_test_features[0].shape[1]
        dataset_ns_test.magn_list = self.magn_list
        dataset_ns_test.freq_list = self.freq_list
        dataset_ns_test.fs = self.fs
        dataset_ns_test.time_cliped_s = ns_test_features[0].shape[2] / self.fs

        return dataset_train, dataset_test, dataset_ns_train, dataset_ns_test

    def plot_target_and_origin(self):
        """
        绘制目标系统和原始系统的频率响应
        inputs: (magn_num, freq_num, points_num)
        output_ori: (magn_num, freq_num, points_num)
        output_tar: (magn_num, freq_num, points_num)
        """
        for i in range(self.magn_num):
            input_tr = [TimeSeries(samples=self.inputs[i, j, :], fs=self.fs)
                        for j in range(self.freq_num)]
            output_ori_tr = [TimeSeries(
                samples=self.output_ori[i, j, :], fs=self.fs) for j in range(self.freq_num)]
            output_tar_tr = [TimeSeries(
                samples=self.output_tar[i, j, :], fs=self.fs) for j in range(self.freq_num)]
            sys_origin = System.fromTimeSeries(
                input_tr, output_ori_tr, self.freq_list, use_parallel=False)
            sys_target = System.fromTimeSeries(
                input_tr, output_tar_tr, self.freq_list, use_parallel=False)
            sys_origin.plot(label=f'Origin@{self.magn_list[i]}')
            sys_target.plot(label=f'Target@{self.magn_list[i]}')
        plt.pause(0.1)

    def export_to_wave(
            self,
            output_folder='./wave_output',
            description=None,
            author=None,
            compress=True
    ):
        """
        将数据集导出为波形文件，支持震级信息

        参数:
            output_folder: 输出文件夹路径
            description: 波形文件描述
            author: 波形文件作者
            compress: 是否压缩文件

        返回:
            输入波形文件路径和输出波形文件路径
        """

        if description is None:
            description = f"数据集波形 - 震级{self.magn_list} 频率{self.freq_list}"

        if author is None:
            author = "Dataset_COMP"

        # 创建输出目录
        os.makedirs(output_folder, exist_ok=True)

        # 创建输入波形数据对象
        input_wave_data = WaveData(
            description=f"输入波形 - {description}",
            author=author,
            tags=["input", "dataset_comp"]
        )

        # 创建输出原始波形数据对象
        output_ori_wave_data = WaveData(
            description=f"原始输出波形 - {description}",
            author=author,
            tags=["output_original", "dataset_comp"]
        )

        # 遍历所有震级和频率组合，将数据转换为波形记录
        for mag_idx in range(self.magn_num):
            for freq_idx in range(self.freq_num):
                # 获取当前频率和震级
                freq = self.freq_list[freq_idx]
                magnitude = self.magn_list[mag_idx]

                # 获取数据
                input_data = self.inputs[mag_idx, freq_idx, :]
                output_ori_data = self.output_ori[mag_idx, freq_idx, :]

                # 创建TimeSeries对象
                input_ts = TimeSeries(samples=input_data, fs=self.fs)
                output_ori_ts = TimeSeries(samples=output_ori_data, fs=self.fs)

                # 创建WaveRecord并添加到波形数据中
                record_id = f"mag{magnitude}_freq{freq}"

                # 输入波形记录
                input_record = WaveRecord.from_time_series(
                    input_ts,
                    channel_names=["Input"],
                    record_id=record_id,
                    user_metadata={
                        "frequency": freq,
                        "magnitude": magnitude,
                        "type": "input"
                    }
                )
                input_wave_data.add_record(input_record)

                # 输出原始波形记录
                output_ori_record = WaveRecord.from_time_series(
                    output_ori_ts,
                    channel_names=["Output_Original"],
                    record_id=record_id,
                    user_metadata={
                        "frequency": freq,
                        "magnitude": magnitude,
                        "type": "output_original"
                    }
                )
                output_ori_wave_data.add_record(output_ori_record)

        # 添加数据集信息到元数据
        dataset_info = {
            "magn_list": [float(m) for m in self.magn_list],
            "freq_list": [float(f) for f in self.freq_list],
            "fs": float(self.fs),
            "time_cliped_s": float(self.time_cliped_s),
            "magn_num": int(self.magn_num),
            "freq_num": int(self.freq_num),
            "dataset_type": type(self).__name__
        }

        input_wave_data.add_user_metadata("dataset_info", dataset_info)
        output_ori_wave_data.add_user_metadata("dataset_info", dataset_info)

        # 保存波形文件
        processor = WaveProcessor()

        input_wave_path = os.path.join(output_folder, f"dataset_{self.type}_input")
        output_ori_wave_path = os.path.join(
            output_folder, f"dataset_{self.type}_output_original")

        processor.save_waveform(
            input_wave_path, input_wave_data, compress=compress)
        processor.save_waveform(output_ori_wave_path,
                                output_ori_wave_data, compress=compress)

        print(f"数据集已成功导出为波形文件至: {output_folder}")

        # 返回文件路径
        result_paths = {
            "input": f"{input_wave_path}.wave",
            "output_original": f"{output_ori_wave_path}.wave"
        }

        return result_paths


class Dataset_COMP_MET(Dataset_COMP):
    def __init__(
            self,
            data_info_list: List[exam_process.DataInfo],
            target_sweep,
            sweep_list,
            use_cache=True,
            use_debug=False,
            fs=2000,
            time_cliped_s=2.0
    ):
        self.data_info_list = data_info_list
        self.target_sweep = target_sweep
        self.sweep_list = sweep_list
        self.use_cache = use_cache
        self.use_debug = use_debug
        self.fs = fs
        self.time_cliped_s = time_cliped_s
        self.type = 'MET'
        inputs, output_ori, output_tar, sys_target_fit, magn_list, freq_list = prepare_features_comp(
            data_info_list,
            target_sweep,
            sweep_list,
            use_cache=use_cache,
            fs=fs,
            time_cliped_s=self.time_cliped_s
        )
        self.inputs = inputs
        self.output_ori = output_ori
        self.output_tar = output_tar
        self.sys_target_fit = sys_target_fit
        self.magn_list = magn_list
        self.freq_list = freq_list
        self.magn_num = self.output_ori.shape[0]
        self.freq_num = self.output_ori.shape[1]
        self.points_num = self.output_ori.shape[2]

        # X shape: (magn_num, freq_num, points_num)
        # y shape: (magn_num, freq_num, points_num)
        # self.to_csv('data/MET_data_csv')


def load_and_preprocess_data(
        data_path,
        amply=0.006,
        use_resample=True,
        fade_in=0.3,
        fade_out=0.0,
        time_cliped_s=2.0,
        filter_bandpass=True,
        filter_bandpass_freq=[10, 500],
        fs=2000,
        use_debug=False):
    tr_input_list, tr_output_list, freq_list = pre_process_data(
        data_path,
        amply=amply,
        use_resample=use_resample,
        fade_in=fade_in,
        fade_out=fade_out,
        time_cliped_s=time_cliped_s,
        filter_bandpass=filter_bandpass, filter_bandpass_freq=filter_bandpass_freq,
        fs=fs,
        use_debug=use_debug
    )
    return tr_input_list, tr_output_list, freq_list


def prepare_features_comp(
        data_info_list: List[exam_process.DataInfo],
        target_sweep,
        sweep_list,
        fs=2000,
        time_cliped_s=2.0,
        use_cache=True,
        use_debug=False,
        build_target_with_comp=True
):
    # 构建缓存参数字典
    cache_params = {
        'target_sweep': target_sweep,
        'sweep_list': sweep_list,
        'fs': fs,
        'time_cliped_s': time_cliped_s,
        'build_target_with_comp': build_target_with_comp,
        # 使用数据信息的唯一标识而不是数据对象本身
        'data_info_paths': [info.data_file_path for info in data_info_list if info.data_file_path]
    }

    cache_hash = generate_cache_hash(cache_params)
    dataset_type = 'features_comp'

    X_features = []
    input_features = []
    y_features = []
    magnitude = []

    fade_in = 0.3
    fade_out = 0.0

    if use_cache:
        # 尝试从缓存加载数据
        cache_data = load_from_cache(
            dataset_type,
            cache_hash,
            ['X_features', 'y_features', 'input_features', 'magnitude', 'freq_list']
        )

        if cache_data:
            sys_target, tr_input_target, tr_output_target, freq_list = pre_process_data_M50(
                data_info_list, sweep_list[target_sweep], fade_in=fade_in, fade_out=fade_out, fs=fs, time_cliped_s=time_cliped_s)

            data_info_target: exam_process.DataInfo = data_info_list[sweep_list[target_sweep]]
            target_magnitude = data_info_target.magnitude
            # 使用默认频率范围（若有config可考虑传入）
            sys_target_fit = exam_process.ws_system_fit(
                sys_target, k=1.0, freq_range=(5, 200))

            return (
                cache_data['input_features'],
                cache_data['X_features'],
                cache_data['y_features'],
                sys_target_fit,
                cache_data['magnitude'],
                cache_data['freq_list']
            )

    # 如果没有缓存或加载失败，进行计算
    sys_target, tr_input_target, tr_output_target, freq_list = pre_process_data_M50(
        data_info_list, sweep_list[target_sweep], fade_in=fade_in, fade_out=fade_out, fs=fs, time_cliped_s=time_cliped_s
    )

    data_info_target: exam_process.DataInfo = data_info_list[sweep_list[target_sweep]]
    target_magnitude = data_info_target.magnitude
    # 使用默认频率范围
    sys_target_fit = exam_process.ws_system_fit(
        sys_target, k=1.0, freq_range=(5, 200))

    for i in sweep_list:
        data_info = data_info_list[i]
        magnitude.append(data_info.magnitude)

    for i in sweep_list:
        sys_sweep, tr_input, tr_output, freq_list = pre_process_data_M50(
            data_info_list, i, fade_in=fade_in, fade_out=fade_out, fs=fs, time_cliped_s=time_cliped_s
        )
        data_info: exam_process.DataInfo = data_info_list[i]
        if use_debug:
            if i == 1:
                tr_input[10].plot()
                tr_output[10].plot()
                plt.pause(0.1)
        # 使用默认频率范围
        sys_sweep_fit = exam_process.ws_system_fit(
            sys_sweep, k=1.0, freq_range=(5, 200))

        if build_target_with_comp:
            comp_sys = exam_class.ws_compensator(sys_sweep_fit, sys_target_fit)
        output_np = np.array(
            [tr_output[i].samples for i in range(len(tr_output))])
        input_np = np.array([tr.samples for tr in tr_input])

        if build_target_with_comp:
            # 使用不同震级下的补偿器快照构建目标系统
            # W_target = Ws * W_comp_snapshot
            tr_target = [comp_sys.time_response(tr_output[i])
                         for i in range(len(tr_output))]
        else:
            # 直接使用输入输出构建目标系统
            # W_target = W_target(input)
            logger.info('Using input-output to build target system.')
            tr_input = [tr_input_item.invert()
                        for tr_input_item in tr_input]  # 数据采集的时候 input 的方向是反的
            tr_target = [sys_target_fit.time_response(
                tr_input[i]) for i in range(len(tr_input))]

        target_np = np.array([tr.samples for tr in tr_target])
        if use_debug:
            sys_target = exam_class.System.fromTimeSeries(
                tr_input, tr_target, freq_list)
            # 使用默认频率范围绘图
            sys_target.plot(freq_range=(5, 200), label=f'Target {i}')
            plt.pause(0.1)
        X_features.append(output_np)
        y_features.append(target_np)
        input_features.append(input_np)

    # convert features to numpy array
    # 检查 X_features 的形状和类型
    # 对所有元素补零
    target_shape_X = (
        max(feature.shape[0] for feature in X_features), X_features[0].shape[1])
    X_features = [pad_to_shape(feature, target_shape_X)
                  for feature in X_features]
    input_features = [pad_to_shape(feature, target_shape_X)
                      for feature in input_features]

    target_shape_Y = (
        max(feature.shape[0] for feature in y_features), y_features[0].shape[1])
    y_features = [pad_to_shape(feature, target_shape_Y)
                  for feature in y_features]

    X_features = np.array(X_features)
    y_features = np.array(y_features)
    input_features = np.array(input_features)

    logger.info(f'X_features shape: {X_features.shape}')
    logger.info(f'y_features shape: {y_features.shape}')
    logger.info(f'input_features shape: {input_features.shape}')

    # 保存到缓存
    if use_cache:
        save_to_cache(
            dataset_type,
            cache_hash,
            {
                'X_features': X_features,
                'y_features': y_features,
                'input_features': input_features,
                'magnitude': magnitude,
                'freq_list': freq_list
            },
            use_debug
        )

    return input_features, X_features, y_features, sys_target_fit, magnitude, freq_list


class Dataset_COMP_PE(Dataset_COMP):
    # 压电传感器
    def __init__(
            self,
            fs=2000,
            time_cliped_s=4.0,
            # magn_list=[0.1, 0.2, 0.3, 0.4, 0.5, 0.8, 1.0, 2.0, 3.0, 4.0, 5.0],
            magn_list=np.linspace(0.01, 2.5, 50),
            # freq_list=[5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 150, 200],
            freq_list=[10, 20],
            k1=1.0/3.0,
            k3=0.5/3.0,
            use_cache=False,
            use_debug=False
    ):
        """
            output_ori = k_1 * x + k_3 * x^3
            output_tar = k_1 * x
        """
        self.type = 'PE'
        self.magn_list = magn_list
        self.freq_list = freq_list
        self.points_num = int(fs * time_cliped_s)
        self.fs = fs
        self.time_cliped_s = time_cliped_s
        self.k1 = k1
        self.k3 = k3
        self.magn_num = len(magn_list)
        self.freq_num = len(freq_list)

        # 构建缓存参数字典
        cache_params = {
            'fs': fs,
            'time_cliped_s': time_cliped_s,
            'magn_list': list(magn_list),  # 转换为列表以便序列化
            'freq_list': list(freq_list),
            'k1': k1,
            'k3': k3
        }
        cache_hash = generate_cache_hash(cache_params)

        if use_cache:
            # 尝试从缓存加载数据
            cache_data = load_from_cache(
                self.type,
                cache_hash,
                ['inputs', 'output_ori', 'output_tar']
            )

            if cache_data:
                self.inputs = cache_data['inputs']
                self.output_ori = cache_data['output_ori']
                self.output_tar = cache_data['output_tar']
                # 检查形状
                self.check_shape(use_debug=use_debug)
                return

        # 如果没有缓存或加载失败，计算数据
        inputs = []
        output_ori = []
        output_tar = []
        def fn_ori(x): return k1 * x + k3 * x**3
        def fn_tar(x): return x
        if use_debug:
            fig = plt.figure(figsize=(12, 8))
        for j, magn in enumerate(magn_list):
            print(f'Processing magn: {magn}, freq: {freq_list}')
            inputs_magn = []
            output_ori_magn = []
            output_tar_magn = []
            for i, freq in enumerate(freq_list):
                input_tr = TimeSeries.fromSin(
                    A=magn, f=freq, fs=fs, time_length=time_cliped_s, fade_in=0.3, fade_out=0.0)
                output_ori_tr = input_tr.map(fn_ori)
                output_tar_tr = input_tr.map(fn_tar)
                inputs_magn.append(input_tr.samples)
                output_ori_magn.append(output_ori_tr.samples)
                output_tar_magn.append(output_tar_tr.samples)
                if use_debug:
                    plt.plot(input_tr.samples, label='Input')
                    plt.plot(output_ori_tr.samples, label='Output')
                    plt.plot(output_tar_tr.samples, label='Target')
                    plt.legend()
                    plt.pause(0.01)
                    plt.cla()
            inputs.append(np.array(inputs_magn))
            output_ori.append(np.array(output_ori_magn))
            output_tar.append(np.array(output_tar_magn))
        self.inputs = np.array(inputs)
        self.output_ori = np.array(output_ori)
        self.output_tar = np.array(output_tar)
        self.check_shape(use_debug=use_debug)
        if use_debug:
            print(f'inputs shape: {self.inputs.shape}')
            print(f'output_ori shape: {self.output_ori.shape}')
            print(f'output_tar shape: {self.output_tar.shape}')

        # 保存到缓存
        if use_cache:
            save_to_cache(
                self.type,
                cache_hash,
                {
                    'inputs': self.inputs,
                    'output_ori': self.output_ori,
                    'output_tar': self.output_tar
                },
                use_debug
            )

    def check_shape(self, use_debug=False):
        if self.inputs.shape != (self.magn_num, self.freq_num, self.points_num):
            raise ValueError(
                'inputs shape is not correct: {inputs.shape}')
        if self.output_ori.shape != (self.magn_num, self.freq_num, self.points_num):
            raise ValueError(
                'output_ori shape is not correct: {output_ori.shape}')
        if self.output_tar.shape != (self.magn_num, self.freq_num, self.points_num):
            raise ValueError(
                'output_tar shape is not correct: {output_tar.shape}')


class Dataset_COMP_Alias(Dataset_COMP):
    """用于处理真实数据中的混叠失真（假频）的数据集类"""

    def __init__(
            self,
            data_info_list: List[exam_process.DataInfo],
            target_sweep,
            sweep_list,
            freq_threshold=80,  # 区分正常频率和假频的频率阈值
            use_cache=True,
            use_debug=False,
            fs=2000,
            time_cliped_s=2.0,
            config=None  # 新增配置参数
    ):
        """
        初始化混叠失真补偿数据集

        Args:
            data_info_list: 数据信息列表
            target_sweep: 目标扫描索引，作为参考系统
            sweep_list: 所有扫描的索引列表
            freq_threshold: 区分正常频率和假频的频率阈值，低于此值视为正常频率
            use_cache: 是否使用缓存数据
            use_debug: 是否启用调试模式
            fs: 采样频率
            time_cliped_s: 时间窗口长度
        """
        self.data_info_list = data_info_list
        self.target_sweep = target_sweep
        self.sweep_list = sweep_list
        self.freq_threshold = freq_threshold
        self.use_cache = use_cache
        self.use_debug = use_debug
        self.fs = fs
        self.time_cliped_s = time_cliped_s
        self.type = 'Alias'

        # 提取波形反相配置 - 传递给基类统一处理，这里只用于日志显示
        if config and hasattr(config, 'dataset') and isinstance(config.dataset, dict):
            # 显示配置信息
            inverse_origin = config.dataset.get('inverse_origin', False)
            inverse_target = config.dataset.get('inverse_target', False)
            inverse_input = config.dataset.get('inverse_input', False)
            print(f"波形反相配置 - origin: {inverse_origin}, target: {inverse_target}, input: {inverse_input}")

        # 构建缓存参数字典
        cache_params = {
            'target_sweep': target_sweep,
            'sweep_list': sweep_list,
            'freq_threshold': freq_threshold,
            'fs': fs,
            'time_cliped_s': time_cliped_s,
            # 使用数据文件路径作为唯一标识
            'data_paths': [info.data_file_path for info in data_info_list if info.data_file_path]
        }
        cache_hash = generate_cache_hash(cache_params)

        # 尝试从缓存加载数据
        if use_cache:
            cache_data = load_from_cache(
                self.type,
                cache_hash,
                ['inputs', 'output_ori', 'output_tar', 'magn_list', 'freq_list']
            )

            if cache_data:
                self.inputs = cache_data['inputs']
                self.output_ori = cache_data['output_ori']
                self.output_tar = cache_data['output_tar']
                self.magn_list = cache_data['magn_list']
                self.freq_list = cache_data['freq_list']

                # 更新相关属性
                self.magn_num = self.output_ori.shape[0]
                self.freq_num = self.output_ori.shape[1]
                self.points_num = self.output_ori.shape[2]

                if use_debug:
                    print(f"已从缓存加载数据: {self.type}_{cache_hash}")
                    print(f"数据形状: {self.inputs.shape}")
                return

        # 处理源数据
        inputs, output_ori, _, sys_target_fit, magn_list, freq_list = prepare_features_comp(
            data_info_list,
            target_sweep,
            sweep_list,
            use_cache=False,  # 这里不使用prepare_features_comp的缓存
            fs=fs,
            time_cliped_s=time_cliped_s,
            use_debug=False
        )
        """
        inputs: (magn_num, freq_num, points_num)
        output_ori: (magn_num, freq_num, points_num)
        """
        target_file_path = data_info_list[target_sweep].data_file_path

        input_tr, output_tr, freq_list = pre_process_data(
            target_file_path, fs=fs, time_cliped_s=time_cliped_s
        )
        sys_target = exam_class.System.fromTimeSeries(
            input_tr, output_tr, freq_list)
        # 使用默认频率范围
        sys_target_fit = exam_process.highpass_fit(
            sys_target, freq_range=(5, 300))

        if use_debug:
            # 使用默认频率范围绘图
            sys_target.plot(freq_range=(5, 200), label='Target')
            sys_target_fit.plot(freq_range=(5, 200), label='Target Fit')
            # plt.pause(0.1)
            plt.show()

        # 为每个震级分别计算目标响应
        output_tar = np.zeros_like(output_ori)
        for i in range(len(magn_list)):
            # 对每个震级的输入分别应用目标系统
            for j in range(len(freq_list)):
                input_ts = TimeSeries(inputs[i, j, :], fs=fs)
                output_ts = sys_target_fit.time_response(input_ts)
                output_tar[i, j, :] = output_ts.samples

        self.inputs = inputs
        self.output_ori = output_ori
        self.output_tar = output_tar
        self.magn_list = magn_list
        self.freq_list = freq_list
        self.magn_num = self.output_ori.shape[0]
        self.freq_num = self.output_ori.shape[1]
        self.points_num = self.output_ori.shape[2]

        # 保存到缓存
        if use_cache:
            save_to_cache(
                self.type,
                cache_hash,
                {
                    'inputs': self.inputs,
                    'output_ori': self.output_ori,
                    'output_tar': self.output_tar,
                    'magn_list': self.magn_list,
                    'freq_list': self.freq_list
                },
                use_debug
            )


class Dataset_COMP_AliasSimu(Dataset_COMP):
    # 压电传感器
    def __init__(
            self,
            fs=2000,
            time_cliped_s=4.0,
            magn_list=[0.1, 0.2, 0.3, 0.4, 0.5, 0.8, 1.0, 2.0, 3.0, 4.0, 5.0],
            # magn_list=np.linspace(1),
            # magn_list=[1],
            # freq_list=[5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 150, 200],
            freq_list=[i for i in range(5, 200, 5)],
            k1=1.0/3.0,
            k3=0.5/3.0,
            use_cache=True,
            use_debug=False
    ):
        """
            output_ori = k_1 * x + k_3 * x^3
            output_tar = k_1 * x
        """
        self.type = 'AliasSimu'
        self.magn_list = magn_list
        self.freq_list = freq_list
        self.points_num = int(fs * time_cliped_s)
        self.fs = fs
        self.time_cliped_s = time_cliped_s
        self.k1 = k1
        self.k3 = k3
        self.magn_num = len(magn_list)
        self.freq_num = len(freq_list)

        # 构建缓存参数字典
        cache_params = {
            'fs': fs,
            'time_cliped_s': time_cliped_s,
            'magn_list': list(magn_list),
            'freq_list': list(freq_list),
            'k1': k1,
            'k3': k3
        }
        cache_hash = generate_cache_hash(cache_params)

        if use_cache:
            # 尝试从缓存加载数据
            cache_data = load_from_cache(
                self.type,
                cache_hash,
                ['inputs', 'output_ori', 'output_tar']
            )

            if cache_data:
                self.inputs = cache_data['inputs']
                self.output_ori = cache_data['output_ori']
                self.output_tar = cache_data['output_tar']
                # 检查形状
                self.check_shape(use_debug=use_debug)
                return

        # 如果没有缓存或加载失败，计算数据
        inputs = []
        output_ori = []
        output_tar = []
        fn0 = 10
        zeta0 = 0.707
        Sn0 = 100

        fn1 = 100
        zeta1 = 0.01
        Sn1 = 100 * 100

        wn0 = 2 * np.pi * fn0
        wn1 = 2 * np.pi * fn1
        s = System.s
        # 二阶系统
        sym_target = Sn0 * s**2 / (s**2 + 2 * zeta0 * wn0 * s + wn0**2)
        sym_aliassimu = Sn1 * s / (s**2 + 2 * zeta1 * wn1 * s + wn1**2)
        sys_target = System.fromSymbol(sym_target)
        sys_aliassimu = System.fromSymbol(sym_aliassimu)
        sys_origin = System.fromSymbol(sym_target + sym_aliassimu)
        if use_debug:
            fig = plt.figure(figsize=(12, 8))
            # sys_target.plot()
            # sys_aliassimu.plot()
            # sys_origin.plot()
            plt.show()
        for j, magn in enumerate(magn_list):
            print(f'Processing magn: {magn}, freq: {freq_list}')
            inputs_magn = []
            output_ori_magn = []
            output_tar_magn = []
            for i, freq in enumerate(freq_list):
                input_tr = TimeSeries.fromSin(
                    A=magn, f=freq, fs=fs, time_length=time_cliped_s, fade_in=0.3, fade_out=0.0)
                output_tar_tr = sys_target.time_response(input_tr)
                output_aliassimu_tr = sys_aliassimu.time_response(input_tr)
                inputs_magn.append(input_tr.samples)
                output_ori_magn.append(
                    output_tar_tr.samples + output_aliassimu_tr.samples)
                output_tar_magn.append(output_tar_tr.samples)
                if use_debug:
                    plt.plot(input_tr.samples, label='Input')
                    plt.plot(output_tar_tr.samples +
                             output_aliassimu_tr.samples, label='Output')
                    plt.plot(output_tar_tr.samples, label='Target')
                    plt.legend()
                    plt.pause(0.01)
                    plt.cla()
            inputs.append(np.array(inputs_magn))
            output_ori.append(np.array(output_ori_magn))
            output_tar.append(np.array(output_tar_magn))
        self.inputs = np.array(inputs)
        self.output_ori = np.array(output_ori)
        self.output_tar = np.array(output_tar)
        self.check_shape(use_debug=use_debug)
        if use_debug:
            print(f'inputs shape: {self.inputs.shape}')
            print(f'output_ori shape: {self.output_ori.shape}')
            print(f'output_tar shape: {self.output_tar.shape}')

        # 保存到缓存
        if use_cache:
            save_to_cache(
                self.type,
                cache_hash,
                {
                    'inputs': self.inputs,
                    'output_ori': self.output_ori,
                    'output_tar': self.output_tar
                },
                use_debug
            )

    def check_shape(self, use_debug=False):
        if self.inputs.shape != (self.magn_num, self.freq_num, self.points_num):
            raise ValueError(
                f'inputs shape is not correct: {self.inputs.shape}')
        if self.output_ori.shape != (self.magn_num, self.freq_num, self.points_num):
            raise ValueError(
                f'output_ori shape is not correct: {self.output_ori.shape}')
        if self.output_tar.shape != (self.magn_num, self.freq_num, self.points_num):
            raise ValueError(
                f'output_tar shape is not correct: {self.output_tar.shape}')


def pad_to_shape(array, target_shape):
    """
    补零函数
    """
    padded_array = np.zeros(target_shape, dtype=array.dtype)
    padded_array[:array.shape[0], :array.shape[1]] = array
    return padded_array


def shuffle_and_split_data(
    features_list,
    random_seed=42,
    use_points=1000,
    copy_train=False
):
    """
    对数据列表按照 group 进行乱序，并将每个 group 的数据平均分为 train 和 test。

    参数:
    ----------
    features_list : List[np.ndarray]
        数据列表，每个元素形状为 (magn_num, freq_num, points_num)
    random_seed : int
        随机种子，确保重复实验的可复现性 (默认值为 42)
    use_points : int
        截断长度，只使用每个 group 的前 use_points 个数据 (默认值为 1000)
    copy_train : bool
        若为 True，则返回重复的训练集 (默认值为 False)

    返回:
    ----------
    (train_features, test_features, ns_train_features, ns_test_features)
        每个元素都是列表，包含对应的训练/测试数据
    """

    # 设置随机种子
    np.random.seed(random_seed)

    if not features_list:
        raise ValueError("features_list cannot be empty")

    # 获取数据维度
    magn_num, freq_num, points_num = features_list[0].shape
    group_num = magn_num * freq_num

    # 处理 copy_train 情况
    if copy_train:
        train_list = []
        for feature in features_list:
            x_after_clip = []
            for i in range(group_num):
                x_after_clip.append(feature.reshape(
                    group_num, points_num)[i][:use_points])
            x = np.array(x_after_clip).reshape(magn_num, freq_num, use_points)
            train_list.append(x)
        return (train_list, train_list, train_list, train_list)

    # 对每个特征进行处理
    processed_features = []
    for feature in features_list:
        # reshape to (group_num, points_num)
        x = feature.reshape(group_num, points_num)

        # 截断数据
        x_after_clip = []
        for i in range(group_num):
            x_after_clip.append(x[i][:use_points])
        processed_features.append(np.array(x_after_clip))

    # 生成打乱的组索引和交换决策
    shuffled_indices = np.random.permutation(group_num)
    swap_decisions = np.random.rand(group_num) > 0.5

    # 准备存放分割结果的数据结构
    splitted_data = [{} for _ in range(group_num)]

    # 遍历每个特征和组，进行分割
    for feature_idx, feature in enumerate(processed_features):
        for i, idx in enumerate(shuffled_indices):
            group_data = feature[idx]

            # 分半
            mid_point = len(group_data) // 2
            test, train = group_data[:mid_point], group_data[mid_point:]

            # 根据决策交换
            if swap_decisions[i]:
                train, test = test, train

            if feature_idx not in splitted_data[idx]:
                splitted_data[idx][feature_idx] = {}
            splitted_data[idx][feature_idx]['train'] = train
            splitted_data[idx][feature_idx]['test'] = test

    # 准备最终结果
    train_features = [[] for _ in range(len(features_list))]
    test_features = [[] for _ in range(len(features_list))]
    ns_train_features = [[] for _ in range(len(features_list))]
    ns_test_features = [[] for _ in range(len(features_list))]

    # 按打乱顺序构建结果
    for idx in shuffled_indices:
        for feature_idx in range(len(features_list)):
            train_features[feature_idx].append(
                splitted_data[idx][feature_idx]['train'])
            test_features[feature_idx].append(
                splitted_data[idx][feature_idx]['test'])

    # 按原始顺序构建结果
    for idx in range(group_num):
        for feature_idx in range(len(features_list)):
            ns_train_features[feature_idx].append(
                splitted_data[idx][feature_idx]['train'])
            ns_test_features[feature_idx].append(
                splitted_data[idx][feature_idx]['test'])

    # 转换为 numpy 数组并重塑为原始维度
    for feature_idx in range(len(features_list)):
        train_features[feature_idx] = np.array(
            train_features[feature_idx]).reshape(magn_num, freq_num, -1)
        test_features[feature_idx] = np.array(
            test_features[feature_idx]).reshape(magn_num, freq_num, -1)
        ns_train_features[feature_idx] = np.array(
            ns_train_features[feature_idx]).reshape(magn_num, freq_num, -1)
        ns_test_features[feature_idx] = np.array(
            ns_test_features[feature_idx]).reshape(magn_num, freq_num, -1)

    return (train_features, test_features, ns_train_features, ns_test_features)


class CustomScaler:
    def __init__(self, feature_range=(0, 1)):
        self.feature_range = feature_range
        self.data_min_ = None
        self.data_range_ = None

    def fit(self, X):
        # 计算每列的最小值和最大绝对值（data_min_ 和 data_range_）
        self.data_min_ = 0
        # 将多维数据展开为一维
        X_flattened = X.flatten()
        self.data_range_ = np.max(np.abs(X_flattened))
        self.data_range_ = self.data_range_ / max(abs(self.feature_range[1]),
                                                  abs(self.feature_range[0]))

    def transform(self, X):
        # 计算缩放比例，先 copy 一份数据
        X = X.copy()
        return X / self.data_range_

    def fit_transform(self, X):
        self.fit(X)
        return self.transform(X)

    def dump_json(self, file_path):
        """
        将缩放器参数保存到JSON文件

        Args:
            file_path: JSON文件的路径
        """
        # 准备要存储的数据
        data = {
            'feature_range': list(self.feature_range),
            'data_min_': float(self.data_min_) if self.data_min_ is not None else None,
            'data_range_': float(self.data_range_) if self.data_range_ is not None else None
        }

        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

        # 保存到文件
        with open(file_path, 'w') as f:
            json.dump(data, f)

    @classmethod
    def from_json(cls, file_path):
        """
        从JSON文件加载缩放器参数

        Args:
            file_path: JSON文件的路径

        Returns:
            CustomScaler: 加载的缩放器实例
        """
        # 从文件加载数据
        with open(file_path, 'r') as f:
            data = json.load(f)

        # 创建新实例
        scaler = cls(feature_range=tuple(data['feature_range']))

        # 设置属性
        scaler.data_min_ = data['data_min_']
        scaler.data_range_ = data['data_range_']

        return scaler


aug_fig = None


def augment_data(x, y, n=4, times=1, use_debug=False):
    """
    使用多频率增广的方式对数据进行扩充：
    - 随机选取 n 条样本，将它们在特征维度上做逐元素相加，生成一条新的样本。
    - 根据 times 倍数，最终生成 (times-1)*len(x) 条新样本，并与原始 x, y 拼接。
    - 如果 times <= 1，则不进行增广，直接返回原数据。

    参数：
    ----------
    x: np.ndarray
       原始 x 数据, 形状 (样本数, 特征长度, 1) 或 (样本数, 特征长度) 均可
    y: np.ndarray
       原始 y 数据, 形状 (样本数, 特征长度, 1) 或 (样本数, 特征长度) 均可
    n: int
       每次增广时，随机选取的样本数量
    times: int
       增广后希望总数据量为原来的多少倍；若 times=2，增广后样本数是原来的 2 倍

    返回：
    ----------
    x_aug: np.ndarray
       增广后的 x
    y_aug: np.ndarray
       增广后的 y
    """
    global aug_fig
    if use_debug:
        if aug_fig is None:
            aug_fig = plt.figure(figsize=(10, 6))

    # 如果 times <= 1，表示不进行增广，直接返回原数据
    if times <= 1:
        return x, y

    num_samples = x.shape[0]
    # 需要新生成的样本数
    new_sample_count = (times - 1) * num_samples

    new_x_list = []
    new_y_list = []

    for _ in range(new_sample_count):
        # 随机选取 n 个索引
        indices = np.random.randint(0, num_samples, size=n)

        # 将这 n 条样本在特征维度上做逐元素相加
        x_sum = np.sum(x[indices], axis=0)
        y_sum = np.sum(y[indices], axis=0)

        if use_debug:
            plt.cla()
            plt.plot(x_sum, label='x_sum')
            plt.plot(y_sum, label='y_sum')
            plt.legend()
            plt.pause(0.1)

        new_x_list.append(x_sum)
        new_y_list.append(y_sum)

    new_x = np.array(new_x_list)
    new_y = np.array(new_y_list)

    # 与原数据拼接，得到增广后的数据
    x_aug = np.concatenate([x, new_x], axis=0)
    y_aug = np.concatenate([y, new_y], axis=0)

    return x_aug, y_aug


class CombinedScaler:
    """
    集成的缩放器类，同时处理输入 (X) 和输出 (y) 数据的缩放
    """
    
    def __init__(self, feature_range=(0, 1)):
        """
        初始化集成缩放器
        
        Args:
            feature_range: 缩放后的数据范围
        """
        self.feature_range = feature_range
        self.scaler_x = CustomScaler(feature_range=feature_range)
        self.scaler_y = CustomScaler(feature_range=feature_range)
        self._fitted = False
    
    def fit(self, X, y):
        """
        使用数据拟合缩放器
        
        Args:
            X: 输入数据
            y: 输出数据
        """
        self.scaler_x.fit(X)
        self.scaler_y.fit(y)
        self._fitted = True
        return self
    
    def transform(self, X, y=None):
        """
        转换数据
        
        Args:
            X: 输入数据
            y: 输出数据（可选）
            
        Returns:
            如果 y 为 None，返回转换后的 X
            否则返回 (转换后的 X, 转换后的 y)
        """
        if not self._fitted:
            raise ValueError("缩放器尚未拟合，请先调用 fit() 方法")
        
        X_scaled = self.scaler_x.transform(X)
        
        if y is None:
            return X_scaled
        else:
            y_scaled = self.scaler_y.transform(y)
            return X_scaled, y_scaled
    
    def fit_transform(self, X, y):
        """
        拟合并转换数据
        
        Args:
            X: 输入数据
            y: 输出数据
            
        Returns:
            (转换后的 X, 转换后的 y)
        """
        self.fit(X, y)
        return self.transform(X, y)
    
    def inverse_transform(self, X_scaled, y_scaled=None):
        """
        逆转换数据
        
        Args:
            X_scaled: 缩放后的输入数据
            y_scaled: 缩放后的输出数据（可选）
            
        Returns:
            如果 y_scaled 为 None，返回逆转换后的 X
            否则返回 (逆转换后的 X, 逆转换后的 y)
        """
        if not self._fitted:
            raise ValueError("缩放器尚未拟合，请先调用 fit() 方法")
        
        X_original = X_scaled * self.scaler_x.data_range_
        
        if y_scaled is None:
            return X_original
        else:
            y_original = y_scaled * self.scaler_y.data_range_
            return X_original, y_original
    
    def transform_x(self, X):
        """只转换输入数据 X"""
        if not self._fitted:
            raise ValueError("缩放器尚未拟合，请先调用 fit() 方法")
        return self.scaler_x.transform(X)
    
    def transform_y(self, y):
        """只转换输出数据 y"""
        if not self._fitted:
            raise ValueError("缩放器尚未拟合，请先调用 fit() 方法")
        return self.scaler_y.transform(y)
    
    def inverse_transform_x(self, X_scaled):
        """只逆转换输入数据 X"""
        if not self._fitted:
            raise ValueError("缩放器尚未拟合，请先调用 fit() 方法")
        return X_scaled * self.scaler_x.data_range_
    
    def inverse_transform_y(self, y_scaled):
        """只逆转换输出数据 y"""
        if not self._fitted:
            raise ValueError("缩放器尚未拟合，请先调用 fit() 方法")
        return y_scaled * self.scaler_y.data_range_
    
    def dump_json(self, file_path):
        """
        将缩放器参数保存到JSON文件
        
        Args:
            file_path: JSON文件的路径
        """
        if not self._fitted:
            raise ValueError("缩放器尚未拟合，无法保存")
        
        # 准备要存储的数据
        data = {
            'feature_range': list(self.feature_range),
            'fitted': self._fitted,
            'scaler_x': {
                'data_min_': float(self.scaler_x.data_min_) if self.scaler_x.data_min_ is not None else None,
                'data_range_': float(self.scaler_x.data_range_) if self.scaler_x.data_range_ is not None else None
            },
            'scaler_y': {
                'data_min_': float(self.scaler_y.data_min_) if self.scaler_y.data_min_ is not None else None,
                'data_range_': float(self.scaler_y.data_range_) if self.scaler_y.data_range_ is not None else None
            }
        }
        
        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # 保存到文件
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def from_json(cls, file_path):
        """
        从JSON文件加载缩放器参数
        
        Args:
            file_path: JSON文件的路径
            
        Returns:
            CombinedScaler: 加载的缩放器实例
        """
        # 从文件加载数据
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # 创建新实例
        scaler = cls(feature_range=tuple(data['feature_range']))
        
        # 设置属性
        scaler._fitted = data['fitted']
        
        # 设置 scaler_x 属性
        scaler.scaler_x.data_min_ = data['scaler_x']['data_min_']
        scaler.scaler_x.data_range_ = data['scaler_x']['data_range_']
        
        # 设置 scaler_y 属性
        scaler.scaler_y.data_min_ = data['scaler_y']['data_min_']
        scaler.scaler_y.data_range_ = data['scaler_y']['data_range_']
        
        return scaler
    
    def __repr__(self):
        return f"CombinedScaler(feature_range={self.feature_range}, fitted={self._fitted})"
