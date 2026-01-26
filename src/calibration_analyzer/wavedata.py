import numpy as np
import json
import os
from matplotlib import pyplot as plt
import datetime
from typing import Optional, Dict, Any, Tuple, List, Union, Sequence, Callable
# 尝试相对导入，如果失败则使用绝对导入
from .exam_class import TimeSeries

# 当前版本，用于版本校验
CURRENT_VERSION = "1.0"
# 文件扩展名
FILE_EXTENSION = ".wave"

# 标准字段列表
STANDARD_FIELDS_WAVEREACRD = [
    'sample_rate', 'channel_names', 'record_id',
    'creation_date', 'modified_date', 'units'
]

# 标准字段列表
STANDARD_FIELDS_WAVEDATA = [
    'description', 'version', 'creation_date',
    'modified_date', 'author', 'tags'
]


class WaveRecord:
    """
    波形记录类，表示一个时域数据记录
    包含时域数据和相关元数据
    """

    def __init__(self,
                 data: np.ndarray,
                 sample_rate: float,
                 channel_names: List[str] = None,
                 record_id: str = None,
                 creation_date: str = None,
                 modified_date: str = None,
                 units: str = "V",
                 user_metadata: Dict[str, Any] = None):
        """
        初始化波形记录

        参数:
            data: 形状为 (time_steps, channels) 的numpy数组
            sample_rate: 采样率 (Hz)
            channel_names: 通道名称列表
            record_id: 记录ID
            creation_date: 创建日期（如果为None，则使用当前日期）
            modified_date: 修改日期（如果为None，则使用当前日期）
            units: 数据单位
            user_metadata: 用户自定义元数据
        """
        # 确保数据是二维的(time_steps, channels)
        if data.ndim != 2:
            raise ValueError(f"数据维度必须是2，当前为{data.ndim}")

        self.data = data
        self.sample_rate = sample_rate

        # 如果未提供通道名，生成默认名称
        if channel_names is None:
            self.channel_names = [f"通道{i+1}" for i in range(data.shape[1])]
        else:
            if len(channel_names) != data.shape[1]:
                raise ValueError(
                    f"通道名数量({len(channel_names)})与数据通道数({data.shape[1]})不匹配")
            self.channel_names = channel_names

        # 如果未提供记录ID，生成UUID
        self.record_id = record_id if record_id else f"record_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}"

        # 如果未提供日期，则使用当前日期
        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.creation_date = creation_date if creation_date else current_date
        self.modified_date = modified_date if modified_date else current_date

        self.units = units
        self.user_metadata = user_metadata or {}

    @staticmethod
    def from_time_series(
            ts_input: Union[TimeSeries, List[TimeSeries]],
            channel_names: List[str] = None,
            record_id: str = None,
            units: str = "V",
            user_metadata: Dict[str, Any] = None) -> "WaveRecord":
        """
        从一个或多个TimeSeries对象创建WaveRecord

        参数:
            ts_list: 单个TimeSeries对象或TimeSeries对象列表
            channel_names: 通道名称列表
            record_id: 记录ID
            units: 数据单位
            user_metadata: 用户自定义元数据

        返回:
            WaveRecord: 创建的波形记录对象
        """

        # 如果是单个TimeSeries对象，则转换为列表
        if isinstance(ts_input, TimeSeries):
            ts_list = [ts_input]
        else:
            ts_list = ts_input

        # 检查TimeSeries对象列表是否为空
        if not ts_list:
            raise ValueError("TimeSeries对象列表不能为空")

        # 检查每个TimeSeries对象的采样率是否一致
        sample_rate = ts_list[0].fs
        for ts in ts_list:
            if ts.fs != sample_rate:
                raise ValueError(
                    f"所有TimeSeries对象的采样率必须一致，当前为 {ts.fs} Hz")

        # 创建数据数组 shape: (time_steps, channels)
        # 如果长度不一致，则取最大长度，并用0填充

        max_length = max(len(t) for t in ts_list)
        data = np.zeros((max_length, len(ts_list)))
        for i, ts in enumerate(ts_list):
            data[:len(ts), i] = ts.samples[:max_length]
            # 如果长度不一致，则用0填充
            if len(ts) < max_length:
                data[len(ts):, i] = 0

        # 创建WaveRecord对象
        return WaveRecord(
            data=data,
            sample_rate=sample_rate,
            channel_names=channel_names,
            record_id=record_id,
            units=units,
            user_metadata=user_metadata
        )

    @property
    def time_steps(self) -> int:
        """获取时间步数"""
        return self.data.shape[0]

    @property
    def range(self) -> Tuple[float, float]:
        """获取数据范围"""
        return np.min(self.data), np.max(self.data)

    @property
    def num_channels(self) -> int:
        """获取通道数"""
        return self.data.shape[1]

    @property
    def duration(self) -> float:
        """获取记录持续时间(秒)"""
        return self.time_steps / self.sample_rate

    def get_channel(self, channel_index: int) -> np.ndarray:
        """获取指定通道的数据"""
        return self.data[:, channel_index]

    def get_channel_by_name(self, channel_name: str) -> np.ndarray:
        """通过名称获取通道数据"""
        try:
            index = self.channel_names.index(channel_name)
            return self.get_channel(index)
        except ValueError:
            raise ValueError(f"通道名 '{channel_name}' 不存在")

    def get_time_axis(self) -> np.ndarray:
        """获取时间轴数组"""
        return np.arange(self.time_steps) / self.sample_rate

    def update_modified_date(self):
        """更新修改日期为当前时间"""
        self.modified_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def add_user_metadata(self, key: str, value: Any):
        """添加或更新用户自定义元数据"""
        self.user_metadata[key] = value
        self.update_modified_date()

    def get_standard_metadata(self) -> Dict[str, Any]:
        """获取标准元数据字段"""
        return {field: getattr(self, field) for field in STANDARD_FIELDS_WAVEREACRD}

    def get_full_metadata(self) -> Dict[str, Any]:
        """获取完整元数据字典，包括标准和用户自定义字段"""
        return {
            "standard": self.get_standard_metadata(),
            "user": self.user_metadata
        }

    def to_time_series(self, channel_index: Union[int, str] = 0) -> TimeSeries:
        """
        将指定通道的波形记录转换为TimeSeries对象

        参数:
            channel_index: 通道索引或通道名称

        返回:
            TimeSeries: 转换后的TimeSeries对象
        """
        # 获取通道数据
        if isinstance(channel_index, str):
            channel_data = self.get_channel_by_name(channel_index)
        else:
            channel_data = self.get_channel(channel_index)

        # 创建TimeSeries对象
        return TimeSeries(samples=channel_data, fs=int(self.sample_rate))

    def __repr__(self) -> str:
        """对象的字符串表示"""
        return (f"WaveRecord(id='{self.record_id}', shape={self.data.shape}, "
                f"sample_rate={self.sample_rate} Hz, duration={self.duration:.3f} s)")


class WaveData:
    """
    波形数据容器，包含多个波形记录和全局元数据
    提供序列化和反序列化功能
    """

    def __init__(self,
                 records: List[WaveRecord] = None,
                 description: str = "",
                 version: str = CURRENT_VERSION,
                 creation_date: str = None,
                 modified_date: str = None,
                 author: str = "",
                 tags: List[str] = None,
                 user_metadata: Dict[str, Any] = None):
        """
        初始化波形数据对象

        参数:
            records: 波形记录列表
            description: 数据描述
            version: 数据版本
            creation_date: 创建日期（如果为None，则使用当前日期）
            modified_date: 修改日期（如果为None，则使用当前日期）
            author: 作者信息
            tags: 标签列表
            user_metadata: 用户自定义元数据
        """
        self.records = records or []
        self.description = description
        self.version = version

        # 如果未提供日期，则使用当前日期
        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.creation_date = creation_date if creation_date else current_date
        self.modified_date = modified_date if modified_date else current_date

        self.author = author
        self.tags = tags or []
        self.user_metadata = user_metadata or {}

    def add_record(self, record: WaveRecord):
        """添加波形记录"""
        # 检查record_id是否重复，如果重复则添加后缀
        original_id = record.record_id
        existing_ids = self.get_record_ids()

        if original_id in existing_ids:
            # 找到合适的后缀数字
            suffix = 1
            new_id = f"{original_id}_{suffix}"
            while new_id in existing_ids:
                suffix += 1
                new_id = f"{original_id}_{suffix}"

            # 更新记录的ID
            record.record_id = new_id
            # print(f"⚠️  记录ID重复，已重命名: {original_id} -> {new_id}")

        self.records.append(record)
        self.update_modified_date()

    def create_record(self, data: np.ndarray, sample_rate: float, **kwargs) -> WaveRecord:
        """创建并添加新的波形记录"""
        record = WaveRecord(data, sample_rate, **kwargs)
        self.add_record(record)
        return record

    def get_record(self, record_id: str) -> Optional[WaveRecord]:
        """通过ID获取记录"""
        for record in self.records:
            if record.record_id == record_id:
                return record
        return None

    def update_modified_date(self):
        """更新修改日期为当前时间"""
        self.modified_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def add_user_metadata(self, key: str, value: Any):
        """添加或更新用户自定义元数据"""
        self.user_metadata[key] = value
        self.update_modified_date()

    def get_standard_metadata(self) -> Dict[str, Any]:
        """获取标准元数据字段"""
        return {field: getattr(self, field) for field in STANDARD_FIELDS_WAVEDATA}

    def get_full_metadata(self) -> Dict[str, Any]:
        """获取完整元数据字典，包括标准和用户自定义字段"""
        return {
            "standard": self.get_standard_metadata(),
            "user": self.user_metadata
        }

    def save(self, filepath: str, compress: bool = True):
        """
        保存波形数据到文件

        参数:
            filepath: 保存路径（可以带.wave后缀也可以不带）
            compress: 是否压缩
        """
        # 处理文件扩展名
        if not filepath.endswith(FILE_EXTENSION):
            filepath += FILE_EXTENSION

        # 获取全局元数据
        global_metadata = self.get_full_metadata()

        # 准备记录数据和元数据
        record_data_dict = {}
        record_metadata_dict = {}

        for i, record in enumerate(self.records):
            record_key = f"record_{i}"
            record_data_dict[record_key] = record.data
            record_metadata_dict[record_key] = record.get_full_metadata()

        # 完整元数据字典
        full_metadata = {
            "__format_version__": CURRENT_VERSION,
            "global": global_metadata,
            "records": record_metadata_dict
        }

        # 序列化元数据
        metadata_str = json.dumps(full_metadata)

        # 保存文件 - 使用文件对象而不是依赖NumPy添加.npz后缀
        save_dict = {
            "metadata": np.array(metadata_str, dtype="object"),
            **record_data_dict
        }

        # 直接使用文件对象
        save_func = np.savez_compressed if compress else np.savez
        with open(filepath, 'wb') as f:
            save_func(f, **save_dict)

    @staticmethod
    def load(filepath: str, version_check: bool = True) -> 'WaveData':
        """
        从文件加载波形数据

        参数:
            filepath: 文件路径
            version_check: 是否校验版本

        返回:
            波形数据对象实例

        异常:
            ValueError: 如果version_check为True且版本不匹配
        """
        # 处理文件扩展名
        if not os.path.exists(filepath) and not filepath.endswith(FILE_EXTENSION):
            filepath += FILE_EXTENSION

        # 加载原始数据
        try:
            with np.load(filepath, allow_pickle=True) as npz_file:
                # 提取元数据
                metadata_str = npz_file["metadata"].item()
                full_metadata = json.loads(metadata_str)

                # 版本校验
                file_version = full_metadata.get("__format_version__", "未知")
                if version_check and file_version != CURRENT_VERSION:
                    raise ValueError(
                        f"版本不匹配: 文件版本为 {file_version}，"
                        f"当前支持的版本为 {CURRENT_VERSION}"
                    )

                # 解析全局元数据
                global_metadata = full_metadata.get("global", {})
                standard_metadata = global_metadata.get("standard", {})
                user_metadata = global_metadata.get("user", {})

                # 创建WaveData对象
                wavedata = WaveData(
                    records=[],  # 稍后添加记录
                    user_metadata=user_metadata,
                    **{k: standard_metadata.get(k, "") for k in STANDARD_FIELDS_WAVEDATA}
                )

                # 处理可能的None值
                if wavedata.tags is None:
                    wavedata.tags = []

                # 加载记录
                records_metadata = full_metadata.get("records", {})
                for record_key, record_meta in records_metadata.items():
                    if record_key in npz_file:
                        # 获取记录数据
                        record_data = npz_file[record_key]

                        # 解析记录元数据
                        record_standard_meta = record_meta.get("standard", {})
                        record_user_meta = record_meta.get("user", {})

                        # 创建WaveRecord对象
                        record = WaveRecord(
                            data=record_data,
                            user_metadata=record_user_meta,
                            **{k: record_standard_meta.get(k, "") for k in STANDARD_FIELDS_WAVEREACRD}
                        )

                        wavedata.add_record(record)

                return wavedata
        except Exception as e:
            # 增加错误诊断信息
            print(f"加载文件 '{filepath}' 时出错: {str(e)}")
            raise

    def __repr__(self) -> str:
        """对象的字符串表示"""
        return f"WaveData(records={len(self.records)}, description='{self.description}')"

    @property
    def range(self) -> Tuple[float, float]:
        """获取所有记录的范围"""
        min_val = float('inf')
        max_val = float('-inf')
        for record in self.records:
            record_min, record_max = record.range
            min_val = min(min_val, record_min)
            max_val = max(max_val, record_max)
        return min_val, max_val

    @property
    def time_steps_range(self) -> Tuple[int, int]:
        """获取所有记录的时间步数范围"""
        min_steps = float('inf')
        max_steps = float('-inf')
        for record in self.records:
            min_steps = min(min_steps, record.time_steps)
            max_steps = max(max_steps, record.time_steps)
        return min_steps, max_steps

    @property
    def num_channels_range(self) -> int:
        """获取所有记录的通道数范围"""
        min_channels = float('inf')
        max_channels = float('-inf')
        for record in self.records:
            min_channels = min(min_channels, record.num_channels)
            max_channels = max(max_channels, record.num_channels)
        return min_channels, max_channels

    @property
    def num_records(self) -> int:
        """获取记录数量"""
        return len(self.records)

    def __len__(self) -> int:
        """获取记录数量"""
        return len(self.records)

    def get_record_ids(self) -> List[str]:
        """获取所有记录的ID"""
        return [record.record_id for record in self.records]

    def __getitem__(self, key) -> 'WaveData':
        """
        实现切片操作，使WaveData支持类似列表的索引和切片操作

        参数:
            key: 整数索引、切片对象或其他索引类型

        返回:
            WaveData: 包含选定记录的新WaveData对象

        示例:
            - wavedata[0]     # 返回只包含第一个记录的WaveData
            - wavedata[:10]   # 返回包含前10个记录的WaveData
            - wavedata[-3:]   # 返回包含最后3个记录的WaveData
        """
        # 创建具有相同元数据的新WaveData对象，但不包含记录
        new_wavedata = WaveData(
            description=self.description,
            version=self.version,
            creation_date=self.creation_date,
            modified_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            author=self.author,
            tags=self.tags.copy() if self.tags else [],
            user_metadata=self.user_metadata.copy() if self.user_metadata else {}
        )

        # 如果是整数索引，只返回单个记录
        if isinstance(key, int):
            # 处理负索引
            if key < 0:
                key = len(self.records) + key

            # 检查索引是否有效
            if key < 0 or key >= len(self.records):
                raise IndexError("WaveData索引超出范围")

            # 添加单个记录
            new_wavedata.add_record(self.records[key])

        # 如果是切片，返回指定范围的记录
        elif isinstance(key, slice):
            # 使用切片获取记录子集
            records_subset = self.records[key]
            for record in records_subset:
                new_wavedata.add_record(record)

        # 如果是其他类型的索引，抛出错误
        else:
            raise TypeError(f"WaveData索引必须是整数或切片，而不是{type(key).__name__}")

        return new_wavedata

    # 支持倍乘
    def __mul__(self, other: Union[int, float]) -> 'WaveData':
        """
        实现波形数据的倍乘操作

        参数:
            other: 乘数，可以是整数或浮点数

        返回:
            WaveData: 乘以指定倍数后的新WaveData对象
        """
        if not isinstance(other, (int, float)):
            raise TypeError(f"乘数必须是整数或浮点数，而不是{type(other).__name__}")

        # 创建新的WaveData对象
        new_wavedata = WaveData(
            description=self.description,
            version=self.version,
            creation_date=self.creation_date,
            modified_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            author=self.author,
            tags=self.tags.copy() if self.tags else [],
            user_metadata=self.user_metadata.copy() if self.user_metadata else {}
        )

        # 对每个记录进行倍乘
        for record in self.records:
            new_data = record.data * other
            new_record = WaveRecord(
                data=new_data,
                sample_rate=record.sample_rate,
                channel_names=record.channel_names,
                record_id=record.record_id,
                creation_date=record.creation_date,
                modified_date=record.modified_date,
                units=record.units,
                user_metadata=record.user_metadata)
            new_wavedata.add_record(new_record)

        return new_wavedata

    def __sub__(self, other: 'WaveData') -> 'WaveData':
        """
        实现两个WaveData对象的减法运算
        
        参数:
            other: 另一个WaveData对象
            
        返回:
            WaveData: 相减后的新WaveData对象（self - other）
        """
        if not isinstance(other, WaveData):
            raise TypeError(f"减数必须是WaveData对象，而不是{type(other).__name__}")
        
        # 检查记录数量是否匹配
        if len(self.records) != len(other.records):
            raise ValueError(f"记录数量不匹配：{len(self.records)} vs {len(other.records)}")
        
        # 创建新的WaveData对象
        new_wavedata = WaveData(
            description=f"{self.description} - {other.description}",
            version=self.version,
            creation_date=self.creation_date,
            modified_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            author=self.author,
            tags=self.tags.copy() if self.tags else [],
            user_metadata=self.user_metadata.copy() if self.user_metadata else {}
        )
        
        # 对每个记录进行减法运算
        for i, (rec1, rec2) in enumerate(zip(self.records, other.records)):
            # 检查数据形状是否匹配
            if rec1.data.shape != rec2.data.shape:
                raise ValueError(f"记录{i}的数据形状不匹配：{rec1.data.shape} vs {rec2.data.shape}")
            
            # 检查采样率是否匹配
            if abs(rec1.sample_rate - rec2.sample_rate) > 1e-6:
                raise ValueError(f"记录{i}的采样率不匹配：{rec1.sample_rate} vs {rec2.sample_rate}")
            
            # 计算差值
            error_data = rec1.data - rec2.data
            
            # 创建新记录
            new_record = WaveRecord(
                data=error_data,
                sample_rate=rec1.sample_rate,
                channel_names=rec1.channel_names,
                record_id=f"error_{rec1.record_id}",
                creation_date=rec1.creation_date,
                modified_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                units=rec1.units,
                user_metadata={
                    **rec1.user_metadata,
                    "error_type": "difference",
                    "source1_id": rec1.record_id,
                    "source2_id": rec2.record_id
                }
            )
            new_wavedata.add_record(new_record)
        
        return new_wavedata

    def filter(self, filter_func: Callable[[WaveRecord], bool]) -> 'WaveData':
        """
        根据传入的筛选函数过滤波形记录

        参数:
            filter_func: 筛选函数，接收一个WaveRecord对象作为参数，返回布尔值表示是否保留该记录
                        可以是lambda表达式或普通函数

        返回:
            WaveData: 包含满足筛选条件的记录的新WaveData对象

        示例:
            # 筛选频率大于50Hz的记录
            filtered_data = wavedata.filter(lambda rec: rec.user_metadata.get('frequency', 0) > 50)

            # 筛选特定通道名称的记录
            filtered_data = wavedata.filter(lambda rec: '输入' in rec.channel_names)

            # 筛选样本数大于1000的记录
            filtered_data = wavedata.filter(lambda rec: rec.time_steps > 1000)
        """
        # 创建新的WaveData对象，保留元数据
        new_wavedata = WaveData(
            description=f"{self.description} (已过滤)",
            version=self.version,
            creation_date=self.creation_date,
            modified_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            author=self.author,
            tags=self.tags.copy() if self.tags else [],
            user_metadata=self.user_metadata.copy() if self.user_metadata else {}
        )

        # 应用筛选函数，保留满足条件的记录
        for record in self.records:
            try:
                if filter_func(record):
                    new_wavedata.add_record(record)
            except Exception as e:
                print(f"筛选记录 '{record.record_id}' 时出错: {str(e)}")
                continue

        return new_wavedata


# 使用示例 - 使用TimeSeries类
if __name__ == "__main__":
    # 测试1: 使用TimeSeries创建波形数据
    print("=== 测试1: 使用TimeSeries创建波形数据 ===")

    # 创建波形数据对象
    wavedata = WaveData(
        description="使用TimeSeries测试波形数据",
        author="测试用户",
        tags=["测试", "频率响应", "TimeSeries"]
    )

    # 生成不同频率的正弦波
    freq_list = [10.0, 100.0, 1000.0]
    sample_rate = 44100.0
    duration = 0.1  # 0.1秒

    for i, freq in enumerate(freq_list):
        # 使用TimeSeries.fromSin生成正弦波
        input_ts = TimeSeries.fromSin(
            A=1.0,             # 振幅
            f=freq,            # 频率
            fs=sample_rate,    # 采样率
            time_length=duration,  # 持续时间
            fade_in=0.1,       # 渐入
            fade_out=0.1,      # 渐出
        )

        # 生成人为的"输出"信号 (衰减和相移)
        attenuation = 0.8  # 衰减因子
        phase_shift = np.pi / 4  # 45度相移

        # 应用相位移动
        t = np.arange(0, duration, 1/sample_rate)
        output_samples = attenuation * \
            np.sin(2 * np.pi * freq * t + phase_shift)
        output_ts = TimeSeries(output_samples, int(sample_rate))

        # 使用新的工具函数从TimeSeries创建WaveRecord
        record = WaveRecord.from_time_series(
            [input_ts, output_ts],
            channel_names=["输入", "输出"],
            record_id=f"freq_{freq:.2f}Hz_ts",
            user_metadata={"frequency": freq, "source": "TimeSeries"}
        )

        # 添加记录到WaveData
        wavedata.add_record(record)
        if i == 0:
            input_ts.plot()
            output_ts.plot()

    # 保存到文件
    test_file = "test_wavedata_ts"
    wavedata.save(test_file)
    print(f"已保存波形数据到 {test_file}{FILE_EXTENSION}")

    # 测试2: 加载波形数据并计算频率响应
    print("\n=== 测试2: 加载波形数据并计算频率响应 ===")

    # 加载数据
    loaded_data = WaveData.load(test_file)
    print(f"已加载波形数据: {loaded_data}")
    print(f"记录数量: {len(loaded_data.records)}")

    for i, record in enumerate(loaded_data.records):
        print(f"记录 {i+1}: {record}")
        print(f"  频率: {record.user_metadata.get('frequency')} Hz")
        print(f"  通道: {record.channel_names}")
        print(f"  样本数: {record.time_steps}")

        # 使用新的to_time_series方法将WaveRecord转换回TimeSeries
        load_input_ts = record.to_time_series("输入")  # 使用通道名称
        load_output_ts = record.to_time_series(1)      # 使用通道索引

        print(
            f"  输入TimeSeries: 样本数={len(load_input_ts.samples)}, 采样率={load_input_ts.fs}")
        print(
            f"  输出TimeSeries: 样本数={len(load_output_ts.samples)}, 采样率={load_output_ts.fs}")
        if i == 0:
            load_input_ts.plot()
            load_output_ts.plot()

    # 测试3: 使用不同类型的TimeSeries信号
    print("\n=== 测试3: 使用不同类型的TimeSeries信号 ===")

    # 创建新的波形数据对象
    mixed_data = WaveData(description="混合信号类型测试")

    # 方波信号记录
    square_ts = TimeSeries.fromSquare(
        A=1.0,             # 振幅
        f=50.0,            # 频率
        fs=sample_rate,    # 采样率
        time_length=0.1,   # 持续时间
        duty=0.3,          # 占空比
        fade_in=0.1,       # 渐入
        fade_out=0.1,      # 渐出
    )

    # 三角波信号记录
    triangle_ts = TimeSeries.fromTriangle(
        A=1.0,             # 振幅
        f=75.0,            # 频率
        fs=sample_rate,    # 采样率
        time_length=0.1,   # 持续时间
        fade_in=0.1,       # 渐入
        fade_out=0.1,      # 渐出
    )

    # 锯齿波信号记录
    sawtooth_ts = TimeSeries.fromSawtooth(
        A=1.0,             # 振幅
        f=100.0,           # 频率
        fs=sample_rate,    # 采样率
        time_length=0.1,   # 持续时间
        width=0.5,         # 宽度参数
        fade_in=0.1,       # 渐入
        fade_out=0.1,      # 渐出
    )

    # 使用工具函数添加方波记录
    square_output_ts = TimeSeries(square_ts.samples * 0.7, int(sample_rate))
    square_record = WaveRecord.from_time_series(
        [square_ts, square_output_ts],
        channel_names=["方波输入", "方波输出"],
        record_id="square_50Hz",
        user_metadata={"type": "square", "frequency": 50.0}
    )
    mixed_data.add_record(square_record)

    # 使用工具函数添加三角波记录
    triangle_output_ts = TimeSeries(
        triangle_ts.samples * 0.6, int(sample_rate))
    triangle_record = WaveRecord.from_time_series(
        [triangle_ts, triangle_output_ts],
        channel_names=["三角波输入", "三角波输出"],
        record_id="triangle_75Hz",
        user_metadata={"type": "triangle", "frequency": 75.0}
    )
    mixed_data.add_record(triangle_record)

    # 使用工具函数添加锯齿波记录
    sawtooth_output_ts = TimeSeries(
        sawtooth_ts.samples * 0.5, int(sample_rate))
    sawtooth_record = WaveRecord.from_time_series(
        [sawtooth_ts, sawtooth_output_ts],
        channel_names=["锯齿波输入", "锯齿波输出"],
        record_id="sawtooth_100Hz",
        user_metadata={"type": "sawtooth", "frequency": 100.0}
    )
    mixed_data.add_record(sawtooth_record)

    print(f"已创建混合类型记录: {len(mixed_data.records)} 条")
    for record in mixed_data.records:
        print(f"  {record}")
        print(f"    类型: {record.user_metadata.get('type')}")
        print(f"    频率: {record.user_metadata.get('frequency')} Hz")

        # 测试将记录转换回TimeSeries
        input_ts = record.to_time_series(0)
        print(
            f"    转换回TimeSeries: 样本数={len(input_ts.samples)}, 采样率={input_ts.fs}")

    # 保存到文件
    mixed_file = "mixed_signals_test"
    mixed_data.save(mixed_file)
    print(f"已保存混合信号数据到 {mixed_file}{FILE_EXTENSION}")

    # 清理测试文件
    print("\n=== 清理测试文件 ===")
    for file in [f"{test_file}{FILE_EXTENSION}",
                 f"{mixed_file}{FILE_EXTENSION}"]:
        if os.path.exists(file):
            os.remove(file)
            print(f"已删除测试文件: {file}")

    # 测试4: 测试切片功能
    print("\n=== 测试4: 波形数据切片操作 ===")

    # 创建一个包含5个记录的测试数据
    slice_test_data = WaveData(description="切片测试数据")

    # 添加5个记录，每个记录有不同的频率
    for freq in [10, 20, 30, 40, 50]:
        # 创建简单的测试数据
        time = np.linspace(0, 1, int(sample_rate))
        signal = np.sin(2 * np.pi * freq * time)
        data = np.column_stack([signal, signal * 0.5])  # 输入和输出通道

        # 创建记录
        record = WaveRecord(
            data=data,
            sample_rate=sample_rate,
            channel_names=["输入", "输出"],
            record_id=f"test_freq_{freq}Hz",
            user_metadata={"frequency": freq}
        )

        # 添加到波形数据
        slice_test_data.add_record(record)

    print(f"原始波形数据: {slice_test_data}")
    print(f"记录数量: {len(slice_test_data)}")
    print("记录ID列表:", slice_test_data.get_record_ids())

    # 测试单一索引
    single_record = slice_test_data[2]
    print(f"\n单一索引访问 [2]: {single_record}")
    print(f"记录数量: {len(single_record)}")
    print("记录ID列表:", single_record.get_record_ids())

    # 测试切片 - 前3个记录
    first_three = slice_test_data[:3]
    print(f"\n切片前3个 [:3]: {first_three}")
    print(f"记录数量: {len(first_three)}")
    print("记录ID列表:", first_three.get_record_ids())

    # 测试切片 - 最后2个记录
    last_two = slice_test_data[-2:]
    print(f"\n切片最后2个 [-2:]: {last_two}")
    print(f"记录数量: {len(last_two)}")
    print("记录ID列表:", last_two.get_record_ids())

    # 测试步长切片
    step_slice = slice_test_data[::2]
    print(f"\n隔一个取一个 [::2]: {step_slice}")
    print(f"记录数量: {len(step_slice)}")
    print("记录ID列表:", step_slice.get_record_ids())

    # 测试负数索引
    negative_index = slice_test_data[-1]
    print(f"\n负数索引 [-1]: {negative_index}")
    print(f"记录数量: {len(negative_index)}")
    print("记录ID列表:", negative_index.get_record_ids())

    plt.show()

    # 测试5: 测试filter功能
    print("\n=== 测试5: 波形数据过滤操作 ===")

    # 使用前面创建的slice_test_data进行测试
    print(f"原始波形数据: {slice_test_data}")
    print(f"记录数量: {len(slice_test_data)}")
    print("记录ID列表:", slice_test_data.get_record_ids())

    # 测试1: 根据频率过滤 - 只保留频率大于30Hz的记录
    high_freq = slice_test_data.filter(
        lambda rec: rec.user_metadata.get('frequency', 0) > 30)
    print(f"\n过滤频率>30Hz的记录: {high_freq}")
    print(f"记录数量: {len(high_freq)}")
    print("记录ID列表:", high_freq.get_record_ids())

    # 测试2: 根据ID过滤 - 只保留包含"40"的记录ID
    id_filtered = slice_test_data.filter(lambda rec: "40" in rec.record_id)
    print(f"\n过滤ID包含'40'的记录: {id_filtered}")
    print(f"记录数量: {len(id_filtered)}")
    print("记录ID列表:", id_filtered.get_record_ids())

    # 测试3: 连续过滤 - 先根据频率过滤，再根据另一个条件过滤
    chained_filter = slice_test_data.filter(lambda rec: rec.user_metadata.get('frequency', 0) >= 20) \
        .filter(lambda rec: rec.user_metadata.get('frequency', 0) <= 40)
    print(f"\n连续过滤20Hz<=频率<=40Hz的记录: {chained_filter}")
    print(f"记录数量: {len(chained_filter)}")
    print("记录ID列表:", chained_filter.get_record_ids())

    # 测试4: 使用自定义函数作为过滤条件
    def custom_filter(record):
        """样本示例: 检查记录的时间步数和频率"""
        freq = record.user_metadata.get('frequency', 0)
        return record.time_steps > 100 and freq % 20 == 0  # 只保留频率是20的倍数的记录

    custom_filtered = slice_test_data.filter(custom_filter)
    print(f"\n使用自定义函数过滤: {custom_filtered}")
    print(f"记录数量: {len(custom_filtered)}")
    print("记录ID列表:", custom_filtered.get_record_ids())

    plt.show()
