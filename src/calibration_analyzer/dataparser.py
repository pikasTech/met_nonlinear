import struct
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from .datastruct import DataIdentifierParam, DataRecord, ByteFile, DataRecordList
from . import config
import os
import multiprocessing
import tempfile
import shutil
import json
from pathlib import Path


class DataFile:
    def __init__(self, file_path, output_folder=config.CONF_OUTPUT_FOLDER):
        self.input_file_folder = os.path.dirname(file_path)
        self.output_folder = output_folder
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.data_name = os.path.splitext(self.file_name)[0]
        if self.file_name.endswith('.bin'):
            self.postfix = '.bin'
        elif self.file_name.endswith('_data.json'):
            self.postfix = '_data.json'
        elif self.file_name.endswith('_analyze.json'):
            self.postfix = '_analyze.json'

    def bin_path(self):
        if self.postfix == '.bin':
            return self.input_file_folder
        raise Exception("Not a bin file")

    def data_json_path(self):
        if self.postfix == '_data.json':
            return self.file_path
        elif self.postfix == '.bin':
            return os.path.join(self.output_folder, self.data_name + '_data.json')
        elif self.postfix == '_analyze.json':
            return os.path.join(self.output_folder, self.data_name + '_data.json')

    def analyze_json_path(self):
        if self.postfix == '_analyze.json':
            return self.file_path
        elif self.postfix == '.bin':
            return os.path.join(self.output_folder, self.data_name + '_analyze.json')
        elif self.postfix == '_data.json':
            return os.path.join(self.output_folder, self.data_name + '_analyze.json')


class DataParser:
    def __init__(self):
        self.total_frames = 0
        self.error_frames = 0

    def parse_data_raw(self,
                       data: bytes) -> tuple[list, list]:
        in_file = ByteFile(data)
        ch1 = []
        ch2 = []
        while True:
            header = in_file.read(1)

            # 如果已经到达文件末尾，退出循环
            if not header:
                break

            self.total_frames += 1

            header = struct.unpack(">B", header)[0]

            # 检查帧头
            while header != 0xAA:
                self.error_frames += 1
                print(f"错误的帧头: {header}. 正在跳过此数据包...")
                header = in_file.read(1)
                if not header:  # 如果已经到达文件末尾，退出循环
                    break
                header = struct.unpack(">B", header)[0]

            self.total_frames += 1

            # 读取长度字段
            length_data = in_file.read(1)
            if len(length_data) != 1:  # 如果已经到达文件末尾，退出循环
                break

            length = struct.unpack(">B", length_data)[0]

            # 检查长度字段是否在允许的范围内
            if length > 32:
                print(f"错误的长度字段: {length}. 长度超过32字节. 正在跳过此数据包...")
                in_file.read(length)
                self.error_frames += 1
                continue

            # 读取数据包的数据部分
            data = in_file.read(length)

            # 检查长度字段是否正确
            if len(data) != length:
                print(f"错误的长度字段: {length}. 实际数据长度: {len(data)}. 正在跳过此数据包...")
                self.error_frames += 1
                continue

            # 将数据解析为 I16 型整数并写入 CSV 文件
            try:
                row = []
                for i in range(0, len(data), 2):
                    data_field, = struct.unpack("<h", data[i:i+2])
                    row.append(data_field)
                ch1.append(row[0])
                ch2.append(row[1])
            except:
                self.error_frames += 1
                print(f"数据解析失败: {data}. 正在跳过此数据包...")

        return ch1, ch2


class DataIdentifier:
    def __init__(self, content, start, end):
        self.content = content
        self.start = start
        self.end = end
        self.param = DataIdentifierParam(content)

    def __str__(self):
        return f"<{self.content}> start={self.start}, end={self.end}"

    def __repr__(self) -> str:
        return self.__str__()


def find_data_identifier(byte_data, start_pos=0):
    start_marker = b'```'
    end_marker = b'```'

    start = byte_data.find(start_marker, start_pos)
    if start == -1:
        return None  # 开始标记未找到

    # 调整开始位置，跳过开始标记
    start += len(start_marker)

    end = byte_data.find(end_marker, start)
    if end == -1:
        return None  # 结束标记未找到

    # 提取标识内容
    identifier_raw = byte_data[start:end]
    try:
        identifier_content = byte_data[start:end].decode(
            'utf-8').replace('\r', '').replace('\n', '').strip()
        end_index = end + len(end_marker)
    except:
        print(
            f"标识内容解码失败, (len:{len(identifier_raw)}): {identifier_raw[0:128]}")
        identifier_content = None
        end_index = start

    # 创建数据标识对象
    data_identifier = DataIdentifier(
        identifier_content, start, end_index)
    return data_identifier


def find_all_data_identifiers(byte_data):
    identifiers = []
    pos = 0
    while True:
        identifier = find_data_identifier(byte_data, pos)
        if identifier is None:
            break
        if identifier.content == None:
            pos = identifier.end
            continue
        identifiers.append(identifier)
        pos = identifier.end
    return identifiers


class DataBlock:
    def __init__(self, data: bytes, identierParam: DataIdentifierParam):
        # remove \r\n at the beginning and end of the data
        if data[0] == 0x0d and data[1] == 0x0a:
            data = data[2:]
        if data[-2] == 0x0d and data[-1] == 0x0a:
            data = data[:-2]
        self.data = data
        self.param = identierParam

    def __repr__(self) -> str:
        return f"<{self.param.content}>"


def create_data_blocks(byte_data: bytes,
                       identifiers: list[DataIdentifier]) -> list[DataBlock]:
    data_blocks = []
    start_index = None
    start_param = None

    for identifier in identifiers:
        if 'ctl' in identifier.param.params and identifier.param.params['ctl'] == 'end':
            if start_index is not None:
                # 创建数据块
                data_block = DataBlock(
                    byte_data[start_index:identifier.start - 3], start_param)
                data_blocks.append(data_block)
                # 重置开始索引和参数
                start_index = None
                start_param = None
        else:
            # 设置开始索引和参数，如果已经设置则跳过
            if start_index is None:
                start_index = identifier.end
                start_param = identifier.param

    return data_blocks


def process_block_to_file(block: DataBlock, output_path: str):
    dataParser = DataParser()
    ch1, ch2 = dataParser.parse_data_raw(block.data)
    record = DataRecord(block.param, ch1, ch2)
    
    # 创建临时的DataRecordList并添加记录
    temp_record_list = DataRecordList()
    temp_record_list.load_from_data_records([record])
    
    # 将记录保存为中间JSON文件
    temp_record_list.dump_to_json_file(output_path)
    return dataParser.total_frames, dataParser.error_frames

def merge_json_files(temp_dir: str, output_filename: str):
    all_records = []
    
    # 读取所有中间文件
    for json_file in Path(temp_dir).glob('*.json'):
        # 创建临时DataRecordList来加载文件
        temp_record_list = DataRecordList()
        temp_record_list.load_from_json_file(str(json_file))
        
        # 将加载的记录添加到总列表中
        if temp_record_list.dataRecords:
            all_records.extend(temp_record_list.dataRecords)
    
    # 按频率排序
    if all_records:
        all_records.sort(key=lambda x: float(x.param.params.get('freq', '0')))
    
    # 创建最终的DataRecordList并保存
    final_record_list = DataRecordList()
    final_record_list.load_from_data_records(all_records)
    final_record_list.dump_to_json_file(output_filename)

def parse_data_file(input_filename, output_filename, multi_thread=True, max_processes=None):
    """
    解析数据文件
    
    参数:
        input_filename: 输入文件名
        output_filename: 输出文件名
        multi_thread: 是否使用多进程处理
        max_processes: 最大进程数，默认为None，表示使用CPU核心数的一半
    """
    with open(input_filename, "rb") as in_file:
        file_data = in_file.read()

    ids = find_all_data_identifiers(file_data)
    for id in ids:
        print(id)
    blocks = create_data_blocks(file_data, ids)

    tic = time.time()
    total_frames = 0
    error_frames = 0

    # 创建临时目录
    temp_dir = tempfile.mkdtemp(prefix='data_processing_')
    try:
        if multi_thread:
            # 如果未指定最大进程数，则使用CPU核心数的一半（至少为1）
            if max_processes is None:
                max_processes = max(1, multiprocessing.cpu_count())
                
            print(f"使用多进程处理，进程数: {max_processes}")
            with multiprocessing.Pool(processes=max_processes) as pool:
                # 为每个数据块创建进程
                results = []
                for i, block in enumerate(blocks):
                    temp_file = os.path.join(temp_dir, f'temp_{i}.json')
                    result = pool.apply_async(process_block_to_file, 
                                           args=(block, temp_file))
                    results.append(result)

                # 收集处理结果
                completed = 0
                for result in results:
                    block_frames, block_errors = result.get()
                    total_frames += block_frames
                    error_frames += block_errors
                    completed += 1
                    print(f"已完成 {completed} / {len(blocks)}")

                # 合并所有中间文件
                merge_json_files(temp_dir, output_filename)
        else:
            # 单线程处理
            for i, block in enumerate(blocks):
                temp_file = os.path.join(temp_dir, f'temp_{i}.json')
                block_frames, block_errors = process_block_to_file(block, temp_file)
                total_frames += block_frames
                error_frames += block_errors
                print(f"已完成 {i + 1} / {len(blocks)}")
            
            # 合并所有中间文件
            merge_json_files(temp_dir, output_filename)

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)

    toc = time.time()
    print(f"解析数据耗时：{toc-tic:.2f}s")
    print(f"总数据帧数量：{total_frames}")
    print(f"错误数据帧数量：{error_frames}")
    error_rate = error_frames / total_frames if total_frames > 0 else 0
    print(f"误码率：{error_rate:.2e}")

if __name__ == "__main__":
    # 示例：限制最大进程数为4
    parse_data_file("data.bin", "data.json", multi_thread=True, max_processes=4)
