from .utilities import stringfy

class CurcuitParameter:
    """
    电路参数
    :param C1: 电容1
    :param C2: 电容2
    :param R1: 电阻1
    :param R2: 电阻2
    :param R3: 电阻3
    """
    C1: float
    C2: float
    R1: float
    R2: float
    R3: float

    def __init__(self, C1: float, C2: float, R1: float, R2: float, R3: float):
        """
        初始化电路参数
        :param C1: 电容1
        :param C2: 电容2
        :param R1: 电阻1
        :param R2: 电阻2
        :param R3: 电阻3
        """
        self.C1 = C1
        self.C2 = C2
        self.R1 = R1
        self.R2 = R2
        self.R3 = R3

    def __str__(self) -> str:
        """
        打印电路参数
        :return: 电路参数
        """
        return stringfy(self)

    def list(self) -> list:
        """
        电路参数列表
        :return: 电路参数列表
        """
        return [self.C1, self.C2, self.R1, self.R2, self.R3]


