from .system import DataSystem
from .met_parameter import METParameter
from .feedback_parameter import FeedbackParameter
from .met_datastruct import CFun
from .utilities import stringfy
import matplotlib.pyplot as plt


class METData:
    def __init__(self, raw: dict):
        """
        加载电化学检波器实验数据
        :param raw: 原始数据
        :return None
        """
        self.raw = raw
        self.wswf = self.load_System("WsWf")
        self.ws = self.load_System("Ws")
        self.h = self.load_System("H")
        self.h0 = self.load_System("H0")
        self.wfb0_simply = self.load_System("Wfb0_simply")
        self.wfb0 = self.load_System("Wfb0")
        self.wfb0_kpkd = self.load_System("Wfb0_kpkd")
        self.wfb0_pars = self.load_System("Wfb0_pars")
        fit = self.raw["res"]["fit"]
        self.fit = CFun(fit["A"], fit["B"], fit["C"])
        self.h_close_simu_simply = self.load_System("H_close_simu_simply")
        self.h_close_simu = self.load_System("H_close_simu")
        self.h_close_simu_kpkd = self.load_System("H_close_simu_kpkd")
        self.h_close_simu_with_G = self.load_System("H_close_simu_with_G")
        self.load_parameters()
        self.load_feedbackSystem()
        self.G = self.raw["res"]["G"]

    def load_System(self, system_name: str) -> DataSystem:
        """
        加载系统响应
        :param system_name: 系统名称
        :return: 系统响应
        """
        system_raw = self.raw["res"][system_name]
        return DataSystem(system_name, system_raw["f"], system_raw["abs"],
                          system_raw["phase"], system_raw["sensitivity"], system_raw["low_cut_f"], system_raw["high_cut_f"])

    def load_parameters(self):
        """
        加载实验参数
        :return: None
        """
        par_raw = self.raw["par"]
        self.parameter = METParameter(par_raw)

    def load_feedbackSystem(self):
        """
        加载反馈网络参数
        :return: None
        """
        res_raw = self.raw["res"]
        self.feedback = FeedbackParameter(res_raw["Kp0"], res_raw["Kd0"])

    def __str__(self) -> str:
        """
        打印实验数据
        :return: 实验数据
        """
        return stringfy(self)

    def plot(self):
        """
        绘制实验数据
        :return: None
        """
        wswf, ws, h, h0 = self.wswf, self.ws, self.h, self.h0
        wswf.plot()
        # ws.plot()
        h.plot()
        h0.plot()
        plt.show()
