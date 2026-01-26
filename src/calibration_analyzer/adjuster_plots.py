# -*- coding: utf-8 -*-
"""
adjuster_plots.py - 绘图相关类模块

包含Plotter类，用于在Panel中显示matplotlib图形。
"""
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Plotter:
    """matplotlib绘图器，集成到tkinter界面中"""
    
    def __init__(self, master, row=0, column=0, rowspan=1, columnspan=1):
        self.master = master

        # 创建主容器框架
        self.frame = tk.Frame(master, bg="#f5f5f5")
        self.frame.grid(row=row, column=column, rowspan=rowspan,
                        columnspan=columnspan, sticky="nsew")
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        # 创建matplotlib图形
        self.figure = Figure(figsize=(9, 6), dpi=100, constrained_layout=True)
        self.ax = self.figure.add_subplot(111)

        # 创建工具栏和画布的容器框架
        self.content_frame = tk.Frame(self.frame)
        self.content_frame.grid(row=0, column=0, sticky="nsew")
        self.content_frame.grid_rowconfigure(1, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # 创建画布
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.content_frame)

        # 添加工具栏
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.content_frame)
        self.toolbar.grid(row=0, column=0, sticky="ew")

        # 添加画布
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=1, column=0, sticky="nsew")

        # 配置网格权重
        master.grid_rowconfigure(row, weight=1)
        master.grid_columnconfigure(column, weight=1)

    def update_layout(self):
        """手动更新布局"""
        try:
            self.figure.tight_layout()
            self.canvas.draw()
        except:
            pass

    def clear(self):
        """清除当前图形"""
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)

    def plot(self, *args, **kwargs):
        """绘制数据"""
        self.ax.plot(*args, **kwargs)
        self.canvas.draw_idle()

    def scatter(self, *args, **kwargs):
        """绘制散点图"""
        self.ax.scatter(*args, **kwargs)
        self.canvas.draw_idle()

    def set_title(self, title):
        """设置图表标题"""
        self.ax.set_title(title)
        self.update_layout()

    def set_labels(self, xlabel, ylabel):
        """设置坐标轴标签"""
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        self.update_layout()

    def set_legend(self):
        """添加图例"""
        self.ax.legend()
        self.update_layout()

    def update_figure(self, fig):
        """更新整个图形"""
        self.figure.clear()
        for ax in fig.axes:
            self.figure.add_axes(ax)
        self.update_layout()

    def refresh(self):
        """刷新图表"""
        self.update_layout()
