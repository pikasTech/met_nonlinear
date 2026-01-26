from .curcuit_parameter import CurcuitParameter
from .utilities import stringfy


class METParameter:
    """
    实验参数
    :param frequency_low: 低频截止频率
    :param curcuit: 电路参数
    :param kp: 反馈网络比例增益
    :param kd: 反馈网络微分增益
    """
    frequency_low: float
    curcuit: CurcuitParameter
    kp: float
    kd: float

    def __init__(self, raw: dict):
        """
        初始化实验参数
        :param raw: 原始数据
        :return None
        """
        self.frequency_low = raw["fl"]
        self.curcuit = CurcuitParameter(raw["C1"], raw["C2"], raw["R1"],
                                        raw["R2"], raw["R3"])
        self.kp = raw["Kp"]
        self.kd = raw["Kd"]

    def __str__(self) -> str:
        """
        打印实验参数
        :return: 实验参数
        """
        return stringfy(self)


