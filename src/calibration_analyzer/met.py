from .met_data import METData
from . import exam_process
from . import exam_class
import json
def loadData(data_path = "tmp/testout.json", format="JSON") -> METData:
    """
    加载实验数据
    :param data_path: 数据路径
    :param format: 数据格式
    :return: 实验数据
    """
    if format == "JSON":
        with open(data_path, "r") as f:
            return METData(json.load(f))
    else:
        raise Exception("[  ERROR] Unknown format: {}".format(format))
