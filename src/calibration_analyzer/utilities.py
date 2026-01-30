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


def _unwrap_with_period(phase_array, period):
    """
    实现兼容旧版NumPy的unwrap功能（period参数在NumPy 1.21+才支持）。

    参数:
        phase_array: 相位数组（度）
        period: 相位周期

    返回:
        展开后的相位数组
    """
    # 转换为弧度进行unwrap
    phase_rad = np.deg2rad(phase_array)
    unwrapped_rad = np.unwrap(phase_rad)

    # 转换回度
    unwrapped_deg = np.rad2deg(unwrapped_rad)

    # 考虑到周期边界
    # 对于360度周期，unwrap会处理-180到180的边界
    # 手动调整以确保正确展开
    n = len(phase_array)
    for i in range(1, n):
        diff = phase_array[i] - phase_array[i - 1]
        if diff > period / 2:
            unwrapped_deg[i:] -= period
        elif diff < -period / 2:
            unwrapped_deg[i:] += period

    return unwrapped_deg


def shift_phase(phase_array, period=360, phase_shift_manual=0):
    """
    Shift the entire phase array by a constant offset to center it around zero.

    参数:
        phase_array: 相位数组
        period: 相位周期（默认360度）
        phase_shift_manual: 手动相位偏移

    返回:
        调整后的相位数组
    """
    # 首先进行相位展开（使用兼容旧版NumPy的实现）
    unwrapped_phase = _unwrap_with_period(phase_array, period)

    # 计算平均相位值
    unwrapped_phase_sample = unwrapped_phase[int(
        len(unwrapped_phase) * 0.25):int(len(unwrapped_phase) * 0.75)]
    mean_phase = np.mean(unwrapped_phase_sample)

    # 计算需要移动的周期数
    shift_cycles = np.round(mean_phase / period)

    # 平移整个相位数组
    shifted_phase = unwrapped_phase - shift_cycles * period

    # 判断信号是否是反向的（-180度），通过mean到0度和-180度的距离来判断
    # 求 mean 时只留中间的 50% 的数据
    shifted_phase_sample = shifted_phase[int(len(shifted_phase) * 0.25):int(
        len(shifted_phase) * 0.75)]
    mean_phase_to_0 = np.abs(np.mean(shifted_phase_sample))
    mean_phase_to_180n = np.abs(np.mean(shifted_phase_sample + 180))
    mean_phase_to_180p = np.abs(np.mean(shifted_phase_sample - 180))

    if mean_phase_to_180n < mean_phase_to_0 and mean_phase_to_180n < mean_phase_to_180p:
        shifted_phase += 180
    if mean_phase_to_180p < mean_phase_to_0 and mean_phase_to_180p < mean_phase_to_180n:
        shifted_phase -= 180

    # 重新展开相位（使用兼容旧版NumPy的实现）
    shifted_phase = _unwrap_with_period(shifted_phase, period)

    # 手动调整相位
    shifted_phase += phase_shift_manual

    return shifted_phase
