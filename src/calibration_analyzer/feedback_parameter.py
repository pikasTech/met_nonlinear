from .utilities import stringfy

class FeedbackParameter:
    """
    反馈网络参数
    :param kp0: 反馈网络比例增益
    :param kd0: 反馈网络微分增益
    """
    kp0: float
    kd0: float

    def __init__(self, kp: float, kd: float):
        """
        初始化反馈网络参数
        :param kp: 反馈网络比例增益
        :param kd: 反馈网络微分增益
        """
        self.kp0 = kp
        self.kd0 = kd

    def __str__(self) -> str:
        """
        打印反馈网络参数
        :return: 反馈网络参数
        """
        return stringfy(self)

