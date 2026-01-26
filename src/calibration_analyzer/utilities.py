import numpy as np
import os


def formater(str, indent_space=4):
    def _indent():
        return " " * indent_space
    """
    格式化字符串
    :param str: 字符串
    :return: 格式化字符串
    """
    # clean
    str = str.replace(" ", "").replace(
        "\t", "").replace("\r", "").replace("\n", "")
    str = str.replace("=", " = ")
    # indent with brankets
    indent = 0
    res = ""
    for char in str:
        if char == "(":
            indent += 1
            res += char + "\n" + _indent() * indent
            continue
        if char == ")":
            indent -= 1
            res += "\n" + _indent() * indent + char
            continue
        if char == ",":
            res += char + "\n" + _indent() * indent
            continue
        res += char
    return res


def stringfy(obj):
    """
    将对象转换为字符串
    :param obj: 对象
    :return: 字符串
    """
    res = "{}(".format(obj.__class__.__name__)
    if isinstance(obj, dict):
        _dict = obj
    else:
        _dict = obj.__dict__
    for item in _dict.items():
        if item[0] == "raw":
            # skip raw
            continue
        if isinstance(item[1], list):
            # len
            if len(item[1]) > 0:
                res += "{}[{}], ".format(item[0], len(item[1]))
            continue
        if isinstance(item[1], str):
            if len(item[1]) > 64:
                # str
                res += "{}=str[{}], ".format(item[0])
                continue
            # str
            res += "{}='{}', ".format(item[0], item[1])
            continue
        if isinstance(item[1], dict):
            # dict
            res += "{}={}, ".format(item[0], stringfy(item[1]))

            continue
        # other
        res += "{}={}, ".format(item[0], item[1])
    res = res[:-2] + ")"
    return formater(res)


def getname(obj, locals=None):
    """
    获取对象名称
    :param obj: 对象
    :param locals: 局部变量
    :return: 对象名称
    """
    for name in globals():
        if globals()[name] is obj:
            return name
    if None != locals:
        for name in locals:
            if locals[name] is obj:
                return name


class _DictData:
    _dict = {}

    def __init__(self, **kwargs):
        self._dict = kwargs

    def add(self, **kwargs):
        self._dict.update(kwargs)

    def todict(self):
        for (key, value) in self._dict.items():
            if isinstance(value, object):
                if hasattr(value, 'todict'):
                    self._dict[key] = value.todict()
        return self._dict

    def __getattr__(self, __name: str):
        return self._dict[__name]


def get_file_size(filename: str) -> str:
    """
    获取文件大小并格式化显示。

    参数:
    filename (str): 文件路径。

    返回:
    str: 文件大小字符串，带单位（B, KB, MB, GB）。
    """
    try:
        size_bytes = os.path.getsize(filename)
        if size_bytes == 0:
            return "0B"

        size_name = ("B", "KB", "MB", "GB", "TB")
        i = int(np.floor(np.log(size_bytes) / np.log(1024)))
        p = np.power(1024, i)
        size = round(size_bytes / p, 2)
        return f"{size} {size_name[i]}"
    except OSError as e:
        return f"Error: {e}"
