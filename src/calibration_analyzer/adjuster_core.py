# -*- coding: utf-8 -*-
"""
adjuster_core.py - 核心Panel类模块

包含Panel类的核心实现，负责管理UI布局、控件创建和数据绑定。
"""
import os
import sys
import json
import tkinter as tk
from tkinter import font as tkFont
from tkinter import ttk, scrolledtext

try:
    from .adjuster_utils import StdoutRedirector, add_log_target, remove_log_target
    from .adjuster_widgets import (
        TextField, Adjuster, Checkbox, FilePath, FolderPath, Button, Dropdown
    )
    from .adjuster_plots import Plotter
except ImportError:
    from adjuster_utils import StdoutRedirector, add_log_target, remove_log_target
    from adjuster_widgets import (
        TextField, Adjuster, Checkbox, FilePath, FolderPath, Button, Dropdown
    )
    from adjuster_plots import Plotter


class Panel:
    """UI面板核心类，提供完整的数据绑定和控件管理功能"""
    
    main_window = None

    def __init__(self,
                 databinding,
                 callback=None,
                 name='Panel',
                 redirect_stdout=False,
                 always_top=False,
                 with_plot=False,
                 first_update=True,
                 config=None  # 新增全局配置字典参数
                 ):
        # 默认配置
        default_config = {
            'left_frame': {'width': 200, 'sticky': 'ns', 'row_weight': 1, 'column_weight': 0},
            'plot_frame': {'row_weight': 2, 'column_weight': 1},  # 绘图区域权重设为2
            # 日志区域权重设为1，高度比例1:2
            'stdout_frame': {'height': 150, 'row_weight': 1, 'column_weight': 1}
        }

        # 使用提供的配置或默认配置
        self.config = config if config is not None else default_config

        # Check if master is another Panel instance
        if Panel.main_window is None:
            # Create a new window if master is not provided
            Panel.main_window = tk.Tk()
            if not hasattr(Panel.main_window, 'notebook'):
                # Create a Notebook widget if it doesn't exist
                Panel.main_window.notebook = ttk.Notebook(Panel.main_window)
                Panel.main_window.notebook.grid(row=0, column=0, sticky='nsew')
                # 配置主窗口的网格权重，使其能够自适应大小
                Panel.main_window.grid_rowconfigure(0, weight=1)
                Panel.main_window.grid_columnconfigure(0, weight=1)
            Panel.main_window.title(name)
            self.is_tab = False
            # Set the panel to be always on top
            Panel.main_window.attributes('-topmost', always_top)
            Panel.main_window.protocol("WM_DELETE_WINDOW", self.on_close)
            Panel.main_window.notebook.bind(
                "<<NotebookTabChanged>>", self.on_tab_change)
            self.tab_name = "Home"
        else:
            self.is_tab = True  # Flag to indicate this panel is a tab
            self.tab_name = name

        self.tab_frame = ttk.Frame(Panel.main_window.notebook)
        Panel.main_window.notebook.add(self.tab_frame, text=self.tab_name)
        self.master = self.tab_frame
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)        # 配置主网格布局 - 使用配置字典中的设置
        # 行权重设置
        self.master.grid_rowconfigure(
            0, weight=self.config['plot_frame']['row_weight'])  # 绘图区域行
        self.master.grid_rowconfigure(
            1, weight=self.config['stdout_frame']['row_weight'])  # 日志区域行
        # 列权重设置
        self.master.grid_columnconfigure(
            0, weight=self.config['left_frame']['column_weight'])  # 左侧栏
        self.master.grid_columnconfigure(
            1, weight=self.config['plot_frame']['column_weight'])  # 中心区域

        self.data_file_path = f".data/{name}_{self.tab_name}.json"
        self.widgets = []  # General term for both adjusters, checkboxes, and filepaths
        self.callback = callback
        self.widget_conditions = {}  # To store conditions for widgets
        self.with_plot = with_plot  # 是否包含绘图区域
        self.first_update = first_update  # 是否是第一次更新
        self.my_redirector = None  # 跟踪这个Panel的重定向器

        # 初次启动时，记录所有非 @button 的键到 @on_change 中
        self.initial_on_change = [
            k for k in databinding.keys() if (not k.endswith('@button') and not k.startswith('@'))]
        self.previous_databinding = {
            k: v for k, v in databinding.items() if not k.startswith("@")}

        # Ensure the data directory exists
        os.makedirs(os.path.dirname(self.data_file_path), exist_ok=True)

        # Create frames for the different types of widgets
        # 创建带滚动条的左侧栏 - 使用配置字典中的宽度
        self.left_frame = self.create_scrollable_frame(
            self.master, 0, 0, sticky=self.config['left_frame']['sticky'],
            width=self.config['left_frame']['width'])

        # 创建中心区域（绘图）
        if self.with_plot:
            self.plot_frame = tk.Frame(self.master)
            self.plot_frame.grid(row=0, column=1, sticky="nsew")
            self.plotter = Plotter(self.plot_frame)

        # 创建底部区域（日志） - 使用配置字典中的高度
        self.stdout_frame = tk.Frame(
            self.master, height=self.config['stdout_frame']['height'])
        # 日志区域放在绘图区域下方，但只占据中间列
        self.stdout_frame.grid(
            row=1, column=1, sticky="nsew", padx=0, pady=0)

        # 设置全局字体大小
        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(size=12)
        self.master.option_add("*Font", default_font)

        # Load visibility conditions
        group_conditions = databinding.pop("@group", {})
        self.load_conditions(databinding.get("@param", {}), group_conditions)
        databinding.pop("@param", None)

        self.create_widgets(databinding)
        try:
            self.load_data(databinding)
            self.set_values(databinding)
        except Exception as e:
            print(f'Error loading data: {e}')

        # 创建日志区域（如果需要）
        if redirect_stdout:
            self.create_log_area()

        if self.first_update:
            self.on_widget_change(first_init=True)

        self.evaluate_conditions(databinding)

    def create_scrollable_frame(self, parent, row, column, sticky, width=None):
        """创建带滚动条的可滚动框架，支持宽度配置，支持水平和垂直滚动"""
        # 主框架
        frame = tk.Frame(parent, width=width)  # 使用配置的宽度
        frame.grid(row=row, column=column, rowspan=2, sticky=sticky)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # 创建Canvas
        canvas = tk.Canvas(frame, highlightthickness=0)

        # 创建垂直滚动条
        v_scrollbar = ttk.Scrollbar(
            frame, orient="vertical", command=canvas.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")

        # 创建水平滚动条
        h_scrollbar = ttk.Scrollbar(
            frame, orient="horizontal", command=canvas.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        # 可滚动的内部框架
        inner_frame = tk.Frame(canvas)

        def on_frame_configure(event):
            """当内部框架大小改变时更新滚动区域"""
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event):
            """当画布大小改变时调整内部框架的宽度"""
            canvas.configure(scrollregion=canvas.bbox("all"))

        inner_frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)

        # 将内部框架添加到Canvas
        canvas_window = canvas.create_window(
            (0, 0), window=inner_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scrollbar.set,
                         xscrollcommand=h_scrollbar.set)

        # 布局
        canvas.grid(row=0, column=0, sticky="nsew")

        # 配置网格权重
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)        # 绑定鼠标滚轮事件（支持垂直和水平滚动）
        def on_mousewheel(event):
            # 检查是否按住Shift键来进行水平滚动
            if event.state & 0x1:  # Shift键被按下
                canvas.xview_scroll(int(-1*(event.delta/120)), "units")
            else:
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        def on_mouse_enter(event):
            """鼠标进入侧边栏区域时绑定滚轮事件"""
            canvas.bind("<MouseWheel>", on_mousewheel)
            inner_frame.bind("<MouseWheel>", on_mousewheel)

        def on_mouse_leave(event):
            """鼠标离开侧边栏区域时解绑滚轮事件"""
            canvas.unbind("<MouseWheel>")
            inner_frame.unbind("<MouseWheel>")

        # 绑定鼠标进入和离开事件到frame、canvas和inner_frame
        frame.bind("<Enter>", on_mouse_enter)
        frame.bind("<Leave>", on_mouse_leave)
        canvas.bind("<Enter>", on_mouse_enter)
        canvas.bind("<Leave>", on_mouse_leave)
        inner_frame.bind("<Enter>", on_mouse_enter)
        inner_frame.bind("<Leave>", on_mouse_leave)

        return inner_frame

    def create_log_area(self):
        """创建日志输出区域"""
        # 创建等宽字体
        code_font = tkFont.Font(
            family="Consolas", size=15, weight="normal")
            
        # 创建ScrolledText
        self.stdout_text = scrolledtext.ScrolledText(
            self.stdout_frame, wrap=tk.CHAR, font=code_font, state='disabled')
        self.stdout_text.grid(row=0, column=0, sticky="nsew")
        # 设置初始高度和宽度
        self.stdout_text.configure(height=8)

        # 配置日志框架的网格权重，使其能够自适应
        self.stdout_frame.grid_rowconfigure(0, weight=1)
        self.stdout_frame.grid_columnconfigure(0, weight=1)        # 设置One Dark Pro主题的配色
        self.stdout_text.configure(
            bg="#282C34",           # 背景色
            fg="#ABB2BF",           # 前景色（文本颜色）
            insertbackground="#528BFF",  # 光标颜色
            selectbackground="#3E4451",  # 选中背景色
            selectforeground="#FFFFFF"   # 选中文本颜色
        )
        
        # 将这个Panel的log控件添加到全局重定向器
        self.my_redirector = add_log_target(self.stdout_text, self)

    def on_tab_change(self, event):
        # 移除当前活动元素的焦点
        Panel.main_window.focus_force()

    def on_close(self):
        # 清理重定向器
        if self.my_redirector:
            remove_log_target(self.my_redirector)
            self.my_redirector = None
            
        if not self.is_tab:
            Panel.main_window.destroy()
        else:
            # If it's a tab, just hide it instead of closing
            self.master.pack_forget()

    def create_widgets(self, databinding):
        """根据数据类型创建控件并添加到相应的框架"""
        row = 0
        for key, value in databinding.items():
            # 布尔类型和文件/按钮类型放在左侧栏
            frame = self.left_frame

            if key.endswith('@filepath'):
                widget = FilePath(frame, key, value, self.on_widget_change)
            elif key.endswith('@folderpath'):
                widget = FolderPath(frame, key, value, self.on_widget_change)
            elif key.endswith('@button'):
                widget = Button(frame, key, databinding, self.on_widget_change)
            elif key.endswith('@dropdown'):
                if isinstance(value, dict) and 'options' in value:
                    options = value['options']
                    default = value.get('default', None)
                elif isinstance(value, list):
                    options = value
                    default = value[0] if value else None
                else:
                    options = [value] if value else ['选项1', '选项2', '选项3']
                    default = value
                widget = Dropdown(frame, key, options,
                                  default, self.on_widget_change)
            elif key.endswith('@int'):
                widget = Adjuster(frame, key, value,
                                  self.on_widget_change, is_int=True)
            elif isinstance(value, bool):
                widget = Checkbox(frame, key, value, self.on_widget_change)
            elif isinstance(value, (int, float)):
                widget = Adjuster(frame, key, value, self.on_widget_change)
            elif isinstance(value, str):
                widget = TextField(frame, key, value, self.on_widget_change)

            if hasattr(widget, 'grid'):
                widget.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
                self.widgets.append(widget)
                row += 1

    def load_data(self, databinding):
        """从文件加载数据"""
        try:
            with open(self.data_file_path, 'r') as file:
                file_data = json.load(file)
                for key, expected_value in databinding.items():
                    if key in file_data:
                        loaded_value = file_data[key]
                        # Perform type checking
                        if key.endswith('@button') and isinstance(loaded_value, bool):
                            databinding[key] = False
                        elif key.endswith('@dropdown'):
                            # 下拉菜单的值应该是字符串或保存的选择值
                            if isinstance(loaded_value, str):
                                databinding[key] = loaded_value
                        elif isinstance(expected_value, bool) and isinstance(loaded_value, bool):
                            databinding[key] = loaded_value
                        elif key.endswith('@filepath') and isinstance(loaded_value, str):
                            databinding[key] = loaded_value
                        elif key.endswith('@folderpath') and isinstance(loaded_value, str):
                            databinding[key] = loaded_value
                        elif (isinstance(expected_value, (int, float)) and
                              isinstance(loaded_value, (int, float)) and
                              # to distinguish between bool and numeric types
                              not isinstance(loaded_value, bool)):
                            databinding[key] = loaded_value
                        elif isinstance(expected_value, str) and isinstance(loaded_value, str):
                            databinding[key] = loaded_value
                        else:
                            raise TypeError(
                                f"Type mismatch for key '{key}': expected {type(expected_value).__name__}, got {type(loaded_value).__name__}")
        except FileNotFoundError:
            pass  # If the file does not exist, ignore and use the initial databinding
        except json.JSONDecodeError:
            print("Error decoding JSON from the data file.")

    def load_conditions(self, param_config, group_conditions):
        """加载控件显示条件"""
        for group, members in group_conditions.items():
            condition = param_config.get(group, {}).get("if")
            if condition:
                for member in members:
                    self.widget_conditions[member] = condition

        # Override group conditions with specific widget conditions
        for widget_name, conditions in param_config.items():
            if widget_name not in group_conditions:
                condition = conditions.get("if")
                if condition:
                    self.widget_conditions[widget_name] = condition

    def evaluate_conditions(self, updated_values):
        """评估和应用控件显示条件"""
        for widget in self.widgets:
            label = widget.get_label()
            if label in self.widget_conditions:
                try:
                    condition = self.widget_conditions[label]
                    # 使用 eval 计算条件，但提供 get 函数作为安全访问方法
                    result = eval(
                        condition, {"get": updated_values.get}, updated_values)
                    if not result:
                        widget.frame.grid_remove()  # 隐藏控件
                    else:
                        widget.frame.grid()  # 显示控件
                except Exception as e:
                    print(f"Error evaluating condition for {label}: {str(e)}")

    def on_widget_change(self, value=None, first_init=False):
        """控件值变化时的回调处理"""
        updated_values = self.get_values().copy()
        self.evaluate_conditions(updated_values)

        # Determine changes, excluding @on_change and @button itself
        if first_init:
            changes = self.initial_on_change
        else:
            changes = [key for key in updated_values if not key.startswith('@') and not key.endswith(
                '@button') and updated_values[key] != self.previous_databinding.get(key)]

        updated_values["@on_change"] = changes
        self.previous_databinding = {
            k: v for k, v in updated_values.items() if not k.startswith("@")}

        if self.callback:
            self.callback(updated_values)
        self.save_data(updated_values)

    def save_data(self, data):
        """保存数据到文件"""
        data_to_save = {k: v for k, v in data.items() if not k.startswith("@")}
        with open(self.data_file_path, 'w') as file:
            json.dump(data_to_save, file)

    def set_values(self, databinding):
        """设置控件值"""
        callback = self.callback
        self.callback = None  # Temporarily disable callback to prevent multiple updates
        for widget in self.widgets:
            if widget.get_label() in databinding:
                widget.set_value(databinding[widget.get_label()])
        self.callback = callback

    def get_values(self):
        """获取所有控件的当前值"""
        return {widget.get_label(): widget.get_value() for widget in self.widgets}

    def mainloop(self):
        """启动主事件循环"""
        Panel.main_window.mainloop()

    def add_plot_button(self, label, callback):
        """添加绘图按钮的方法，允许外部指定回调函数"""
        if not self.with_plot:
            return None

        # 创建一个临时的 databinding 用于按钮
        temp_databinding = {}
        plot_button = Button(self.left_frame, label,
                             temp_databinding, callback)

        # 获取当前行数
        row = len(self.left_frame.grid_slaves())
        plot_button.grid(row=row, column=0, sticky="ew", padx=5, pady=2)

        # 将按钮添加到widgets列表中以便管理
        self.widgets.append(plot_button)
        return plot_button

    def get_plotter(self):
        """获取绘图器对象，供外部使用"""
        if self.with_plot:
            return self.plotter
        return None

    def update_plot(self, fig):
        """更新绘图区域"""
        if self.with_plot:
            self.plotter.update_figure(fig)
