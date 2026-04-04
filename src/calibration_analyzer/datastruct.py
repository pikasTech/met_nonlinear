import json
from scipy.integrate import cumulative_trapezoid
from typing import Tuple
import numpy as np
from .config import CONF_SAMPLING_RATE
import numpy as np
import base64
from typing import List, Optional, Union
import traceback


def integrate_signal_remove_dc(signal: list[float],
                               sampling_rate: float) -> np.ndarray:
    # Calculate the time interval between samples
    time_interval = 1.0 / sampling_rate

    # Convert the signal to a numpy array and subtract its mean to remove DC component
    mean = np.mean(signal)
    ac = np.array(signal) - mean

    # Perform the integration using the cumulative trapezoidal rule
    integrated_signal = cumulative_trapezoid(ac, dx=time_interval, initial=0)

    # Add the mean back to the integrated signal
    integrated_signal += mean

    # Return the integrated signal as a list
    return integrated_signal


class DataIdentifierParam:
    # example:var=1,freq=10,ctl=end
    def __init__(self, content: str):
        self.content = content
        self.params = {}
        self.parse()

    def parse(self):
        if self.content is None:
            return
        for param in self.content.split(','):
            try:
                key, value = param.split('=')
            except Exception as e:
                print(f'error parsing param {param}')
                traceback.print_exc()
                continue
            self.params[key] = value


class DataRecord:
    def __init__(self,
                 param: DataIdentifierParam,
                 ch1: Union[List[float], np.ndarray],
                 ch2: Union[List[float], np.ndarray],
                 ch1_integrate: Optional[Union[List[float], np.ndarray]] = None):
        self.param: DataIdentifierParam = param
        self.ch1: np.ndarray = np.array(ch1, dtype=np.float64)
        self.ch2: np.ndarray = np.array(ch2, dtype=np.float64)
        if ch1_integrate is not None:
            self.ch1_integrate: np.ndarray = np.array(
                ch1_integrate, dtype=np.float64)
        else:
            self.ch1_integrate: np.ndarray = integrate_signal_remove_dc(
                self.ch1, CONF_SAMPLING_RATE)

    def to_dict(self) -> dict:
        return {
            "param": self.param.params,
            "ch1": self._encode_array(self.ch1),
            "ch2": self._encode_array(self.ch2),
            "ch1_integrate": self._encode_array(self.ch1_integrate)
        }

    @staticmethod
    def _encode_array(array: np.ndarray) -> str:
        return base64.b64encode(array.tobytes()).decode('utf-8')

    @staticmethod
    def _decode_array(encoded_data: str, dtype: type = np.float64) -> np.ndarray:
        data = base64.b64decode(encoded_data)
        return np.frombuffer(data, dtype=dtype)

    @staticmethod
    def load_from_dict(data: dict) -> 'DataRecord':
        param = DataIdentifierParam(None)
        param.params = data['param']
        return DataRecord(
            param,
            DataRecord._decode_array(data['ch1']),
            DataRecord._decode_array(data['ch2']),
            DataRecord._decode_array(data['ch1_integrate'])
        )


class DataRecordList:
    def __init__(self):
        self.dataRecords: list[DataRecord] = []

    def to_dict(self):
        return {
            "data": [dataRecord.to_dict() for dataRecord in self.dataRecords]
        }

    def load_from_dict(self, data: dict):
        self.dataRecords = []
        for dataRecord in data['data']:
            self.dataRecords.append(DataRecord.load_from_dict(dataRecord))

    def load_from_data_records(self, dataRecords: list[DataRecord]):
        self.dataRecords = dataRecords

    def load_from_json(self, json_data: str):
        print(f'loading from json...')
        data = json.loads(json_data)
        self.load_from_dict(data)

    def load_from_json_file(self, filename: str):
        print(f'loading from {filename}...')
        with open(filename, "r") as f:
            self.load_from_json(f.read())

    def dump_to_json(self) -> str:
        print('converting to json...')
        return json.dumps(self.to_dict(), indent=1)

    def dump_to_json_file(self, filename: str):
        data_json = self.dump_to_json()
        print(f'writing to {filename}...')
        with open(filename, "w") as out_file:
            for i in range(0, len(data_json), 1024 * 1024 * 10):
                out_file.write(data_json[i:i+1024 * 1024 * 10])
                print(f'writing {i} bytes...')


class ByteFile:
    def __init__(self, bytes: bytes):
        self.bytes = bytes
        self.pos = 0

    def read(self, size: int) -> bytes:
        if self.pos + size > len(self.bytes):
            return b""
        self.pos += size
        return self.bytes[self.pos - size:self.pos]

    def __len__(self) -> int:
        return len(self.bytes)
