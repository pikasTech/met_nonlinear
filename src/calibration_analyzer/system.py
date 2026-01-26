from .utilities import getname
from .utilities import stringfy
import sys
from matplotlib import pyplot as plt


class DataSystem:
    """
    系统响应
    """
    # 系统名称
    name: str
    # 频率
    freq: list
    # 幅值
    abs: list
    # 相位
    phase: list
    # 插值后的频率
    freq_interp: list
    # 插值后的幅值
    abs_interp: list
    # 插值后的相位 (未使用)
    phase_interp: list
    # 插值点数
    interp_num = 64

    def __init__(self,
                 name: str,
                 freq: list,
                 gain: list,
                 phase: list,
                 sensitivity=None,
                 low_cut_f=None,
                 high_cut_f=None
                 ):
        """
        初始化系统响应
        :param name: 系统名称
        :param freq: 频率
        :param gain: 幅值
        :param phase: 相位
        :return None
        """
        self.name = name
        self.freq = freq
        self.gain = gain
        self.phase = phase
        self.sensitivity = sensitivity
        self.low_cut_f = low_cut_f
        self.high_cut_f = high_cut_f
        self.interp()

    def __str__(self) -> str:
        """
        打印系统响应
        :return: 系统响应
        """
        return stringfy(self)

    def interp(self):
        """
        三次样条插值
        :return: None
        """
        # 频率插值，等对数间隔
        import numpy as np
        from scipy.interpolate import interp1d
        self.freq_interp = np.logspace(
            np.log10(self.freq[0]),
            np.log10(self.freq[-1]),
            self.interp_num
        )

        # 确保插值点不超出原始数据范围 (解决数值精度问题)
        self.freq_interp = np.clip(
            self.freq_interp, self.freq[0], self.freq[-1])

        # 幅值插值
        self.abs_interp = interp1d(
            self.freq,
            self.gain,
            kind="cubic"
        )(self.freq_interp)
        # 转换为 list
        self.abs_interp = self.abs_interp.tolist()
        self.freq_interp = self.freq_interp.tolist()

    def plot(self):
        """
        绘制系统响应
        :return: None
        """
        callingframe = sys._getframe(1)
        locals = callingframe.f_locals
        # 绘制对数散点图
        plt.loglog(
            self.freq,
            # self.abs_interp[0:len(self.freq_interp)],
            self.gain,
            marker=".",
            markersize=3,
        )
        # 获得当前图例
        legend = plt.gca().get_legend()
        # 如果没有图例，则新建图例列表
        if None == legend:
            legend_list = []
        else:
            # 如果有图例，则获取图例列表
            texts = legend.get_texts()
            legend_list = [text.get_text() for text in texts]

        name = getname(self, locals)
        # 使用系统名称
        legend_list.append(name)
        plt.legend(legend_list)
