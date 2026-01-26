# -*- coding: utf-8 -*-
"""
adjuster_widgets.py - UI控件类模块

包含各种UI控件类：TextField、Adjuster、Checkbox、FilePath、FolderPath、Button、Dropdown
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog
import traceback

try:
    from .adjuster_utils import (
        format_value, apply_unit_conversion, parse_value_with_unit,
        calculate_text_width, RepeatButton
    )
except ImportError:
    from adjuster_utils import (
        format_value, apply_unit_conversion, parse_value_with_unit,
        calculate_text_width, RepeatButton
    )


class TextField:
    """文本输入框控件"""
    
    def __init__(self, master, label, default="", callback=None):
        self.master = master
        self.value = tk.StringVar(master, value=default)
        self.callback = callback
        self.default = default
        self.frame = tk.Frame(master)
        self.label = tk.Label(self.frame, text=label)
        self.entry = tk.Entry(self.frame, textvariable=self.value, width=20)
        self.skip_next_entry = False

        # 使用grid布局
        self.label.grid(row=0, column=0, sticky="w")
        self.entry.grid(row=0, column=1, sticky="ew")

        # Bind the Return key and FocusOut event to update the value based on manual entry
        self.entry.bind('<Return>', self.manual_entry)
        self.entry.bind('<FocusOut>', self.manual_entry)

        # Update the entry display whenever the internal value changes
        self.value.trace_add("write", self.update_display)
        self.update_display()

    def set_value(self, value):
        self.value.set(value)
        if self.callback:
            self.callback(value)

    def get_value(self):
        return self.value.get()

    def get_label(self):
        return self.label.cget("text")

    def update_display(self, *args):
        current_value = self.value.get()
        self.value.set(current_value)

    def manual_entry(self, event):
        if self.skip_next_entry:
            self.skip_next_entry = False
            return
        # 如果event是由<Return>触发的，将焦点移动到entry以更新值
        if event.keysym == 'Return':
            self.entry.focus_set()  # Set focus to the entry widget to update value
            self.frame.focus()  # Move focus away from the entry widget to stop blinking
            self.skip_next_entry = True
        input_str = self.entry.get()
        self.set_value(input_str)
        print(f"Manually set value to {input_str}")

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)


class Adjuster:
    """数值调节器控件，支持按钮调节和手动输入"""
    
    def __init__(self, master, label, default=1.0, callback=None, is_int=False):
        self.master = master
        self.is_int = is_int
        self.value = tk.DoubleVar(master, value=default)
        self.value_display = tk.StringVar(self.master, value='')
        self.callback = callback
        self.default = default
        self.frame = tk.Frame(master)
        self.label_text = label
        if label.endswith('@int'):
            self.label = tk.Label(self.frame, text=label[:-4])
        else:
            self.label = tk.Label(self.frame, text=label)
        self.entry = tk.Entry(
            self.frame, textvariable=self.value_display, width=10)
        self.skip_next_entry = False

        # Use RepeatButton class for each button
        self.halve_button = RepeatButton(self.frame, "<<", self.halve)
        self.decrease_button = RepeatButton(self.frame, "<", self.decrease)
        self.increase_button = RepeatButton(self.frame, ">", self.increase)
        self.double_button = RepeatButton(self.frame, ">>", self.double)
        self.reset_button = RepeatButton(self.frame, "RST", self.reset)

        # 使用grid布局
        self.label.grid(row=0, column=0, sticky="w")
        self.entry.grid(row=0, column=1, sticky="ew")
        self.halve_button.grid(row=0, column=2, padx=2)
        self.decrease_button.grid(row=0, column=3, padx=2)
        self.increase_button.grid(row=0, column=4, padx=2)
        self.double_button.grid(row=0, column=5, padx=2)
        self.reset_button.grid(row=0, column=6, padx=2)

        # Update the entry display whenever the internal value changes
        self.value.trace_add("write", self.update_display)

        # Bind the Return key to update the value based on manual entry
        self.entry.bind('<Return>', self.manual_entry)
        # Add FocusOut event binding
        self.entry.bind('<FocusOut>', self.manual_entry)
        self.reset_button.disable()
        self.update_display()

    def set_value(self, value):
        if self.is_int:
            value = int(value)
        self.value.set(value)
        if self.callback:
            self.callback(value)

    def get_value(self):
        if self.is_int:
            return int(self.value.get())
        return self.value.get()

    def get_label(self):
        return self.label_text

    def update_display(self, *args):
        current_value = self.value.get()
        if self.is_int:
            value_formatted = str(int(current_value))
        else:
            value_formatted = format_value(current_value)
        self.value_display.set(value_formatted)

        # 禁用或启用重置按钮
        if current_value == self.default:
            self.reset_button.disable()
        else:
            self.reset_button.enable()

    def manual_entry(self, event):
        if self.skip_next_entry:
            self.skip_next_entry = False
            return
        input_raw = self.entry.get()
        current_raw = format_value(self.value.get())
        input_str = self.entry.get().replace(' ', '')
        current_value_str = format_value(self.value.get()).replace(' ', '')
        # 如果event是由<Return>触发的，将焦点移动到entry以更新值
        if event.keysym == 'Return':
            self.entry.focus_set()  # Set focus to the entry widget to update value
            self.frame.focus()  # Move focus away from the entry widget to stop blinking
            self.skip_next_entry = True
        try:
            # Only process if the input string is different from the current value string
            if input_raw != current_raw:
                number, unit = parse_value_with_unit(input_str)
                manual_value = apply_unit_conversion(number, unit)
                self.set_value(manual_value)
                print(f"Manually set value to {format_value(manual_value)}")
        except ValueError as e:
            print(f"Invalid input: {str(e)}. Please enter a valid number with or without a unit.")

    def halve(self):
        current_value = self.value.get()
        self.set_value(current_value * 0.5)

    def decrease(self):
        current_value = self.value.get()
        if self.is_int:
            self.set_value(current_value - 1)
            return
        self.set_value(current_value * 0.9)

    def increase(self):
        current_value = self.value.get()
        if self.is_int:
            self.set_value(current_value + 1)
            return
        self.set_value(current_value * 1.1)

    def double(self):
        current_value = self.value.get()
        self.set_value(current_value * 2)

    def reset(self):
        self.set_value(self.default)

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)


class Checkbox:
    """复选框控件"""
    
    def __init__(self, master, label, default=False, callback=None):
        self.master = master
        self.value = tk.BooleanVar(master, value=default)
        self.callback = callback
        self.frame = tk.Frame(master)
        self.label = tk.Label(self.frame, text=label)
        self.checkbutton = tk.Checkbutton(
            self.frame, variable=self.value, command=self.on_toggle)

        # 使用grid布局
        self.checkbutton.grid(row=0, column=0, sticky="w")
        self.label.grid(row=0, column=1, sticky="w")

        # Bind the label to toggle the checkbox when it is clicked
        self.label.bind("<Button-1>", self.label_click)

    def label_click(self, event):
        # Toggle the value of the checkbox when the label is clicked
        current_value = self.value.get()
        new_value = not current_value
        self.set_value(new_value)
        self.on_toggle()  # Optionally call the toggle callback

    def on_toggle(self):
        # Invoke the callback with the current state when toggled
        if self.callback:
            self.callback(self.value.get())

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

    def set_value(self, value):
        self.value.set(value)

    def get_value(self):
        return self.value.get()

    def get_label(self):
        return self.label.cget("text")


class FilePath:
    """文件路径选择控件"""
    
    def __init__(self, master, label, default='', callback=None):
        self.master = master
        self.full_path = tk.StringVar(master, value=default)
        self.callback = callback
        self.frame = tk.Frame(master)
        self.label = label
        # 创建一个看起来像标签但功能上是按钮的文件选择器
        self.button = tk.Button(self.frame, text=label.split(
            '@')[0], command=self.select_file)

        # 用于显示文件名（不显示完整路径）的文本框，初始宽度设定为较大值以便调整
        self.entry = tk.Entry(
            self.frame, textvariable=self.full_path, width=10, state='readonly')

        # 用于只显示文件名，不显示完整路径的变量
        self.display_filename = tk.StringVar(
            master, value=self.get_filename(default))
        self.entry.config(textvariable=self.display_filename)
        # 监听 display_filename 的变化来调整宽度
        self.display_filename.trace_add("write", self.update_entry_width)

        # 使用grid布局
        self.button.grid(row=0, column=0, sticky="w")
        self.entry.grid(row=0, column=1, sticky="ew")

    def select_file(self):
        # 获取当前文件的目录作为初始目录
        initial_directory = os.path.dirname(self.full_path.get(
        )) if self.full_path.get() else os.path.expanduser("~")
        # 打开文件选择对话框
        filename = filedialog.askopenfilename(
            initialdir=initial_directory, title='Select a file')
        if filename:
            self.full_path.set(filename)
            self.display_filename.set(self.get_filename(filename))
            if self.callback:
                self.callback(filename)

    def get_filename(self, path):
        # 从完整路径中提取文件名
        return os.path.basename(path)

    def set_value(self, path):
        # 设置完整路径并更新显示的文件名
        self.full_path.set(path)
        self.display_filename.set(self.get_filename(path))

    def update_entry_width(self, *args):
        # 根据文件名长度调整文本框的宽度
        filename = self.display_filename.get()
        # 估算宽度：英文字符计1，中文字符计2
        estimated_width = sum(2 if '\u4e00' <= c <=
                              '\u9fff' else 1 for c in filename)
        # 确保宽度至少为10
        new_width = max(10, estimated_width)
        self.entry.config(width=new_width)

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

    def get_value(self):
        # 返回完整的文件路径
        return self.full_path.get()

    def get_label(self):
        return self.label


class FolderPath(FilePath):
    """文件夹路径选择控件，继承自FilePath"""
    
    def get_filename(self, path):
        return path

    def select_file(self):
        # 获取当前文件的目录作为初始目录
        initial_directory = os.path.dirname(self.full_path.get(
        )) if self.full_path.get() else os.path.expanduser("~")
        # 打开文件选择对话框
        filename = filedialog.askdirectory(
            initialdir=initial_directory, title='Select a folder')
        if filename:
            self.full_path.set(filename)
            self.display_filename.set(self.get_filename(filename))
            if self.callback:
                self.callback(filename)


class Button:
    """按钮控件"""
    
    def __init__(self, master, label, databinding, callback=None):
        self.master = master
        self.label = label
        self.databinding = databinding
        self.callback = callback
        self.frame = tk.Frame(master)
        self.button = tk.Button(self.frame, text=label.split(
            '@')[0], command=self.on_click)
        self.button.grid(row=0, column=0, sticky="ew")  # 使用grid
        self.value = False

    def on_click(self):
        # 设置指定的数据绑定键为 True
        self.databinding[self.label] = True
        self.value = True
        if self.callback:
            try:
                self.callback()
            except Exception as e:
                print(f"Error executing callback: {str(e)}")
                traceback.print_exc()

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

    def get_label(self):
        return self.label

    def get_value(self):
        val = self.value
        self.value = False
        return val

    def set_value(self, val):
        self.value = val


class Dropdown:
    """下拉菜单控件"""
    
    def __init__(self, master, label, options, default=None, callback=None):
        """
        创建下拉菜单组件

        参数:
            master: 父窗口
            label: 标签文本，支持 '@dropdown' 后缀来识别为下拉菜单
            options: 选项列表，可以是字符串列表或字典（键为显示文本，值为实际值）
            default: 默认选项，如果为None则选择第一个选项
            callback: 选择改变时的回调函数
        """
        self.master = master
        self.label_text = label
        self.callback = callback
        self.frame = tk.Frame(master)

        # 处理选项
        if isinstance(options, dict):
            self.display_options = list(options.keys())
            self.option_values = options
        elif isinstance(options, list):
            self.display_options = options
            self.option_values = {opt: opt for opt in options}
        else:
            raise ValueError("选项必须是列表或字典")

        # 创建标签
        self.label = tk.Label(self.frame, text=label.split('@')[0])

        # 创建下拉菜单变量
        self.selected_display = tk.StringVar(master)

        # 设置默认值
        if default is not None:
            if default in self.option_values.values():
                # 如果default是实际值，找到对应的显示文本
                for display, value in self.option_values.items():
                    if value == default:
                        self.selected_display.set(display)
                        break
            elif default in self.display_options:
                # 如果default是显示文本
                self.selected_display.set(default)
            else:
                # 如果default不在选项中，使用第一个选项
                self.selected_display.set(self.display_options[0])
        else:
            # 如果没有指定默认值，使用第一个选项
            if self.display_options:
                self.selected_display.set(self.display_options[0])
                
        self.dropdown = ttk.Combobox(
            self.frame,
            textvariable=self.selected_display,
            values=self.display_options,
            state="readonly",  # 只读，不允许手动输入
        )

        # 自动调整宽度以适应最长的选项
        self._update_dropdown_width()

        # 绑定选择改变事件
        self.dropdown.bind('<<ComboboxSelected>>', self.on_selection_change)

        # 使用grid布局
        self.label.grid(row=0, column=0, sticky="w")
        self.dropdown.grid(row=0, column=1, padx=(5, 0), sticky="ew")

    def _update_dropdown_width(self):
        """根据选项内容自动调整下拉菜单宽度"""
        if not self.display_options:
            self.dropdown.config(width=10)  # 默认最小宽度
            return

        # 计算所有选项的最大宽度
        max_width = 0
        for option in self.display_options:
            option_width = calculate_text_width(option)
            max_width = max(max_width, option_width)

        # 设置最小宽度为10，最大宽度为50（避免过宽）
        optimal_width = max(10, min(50, max_width + 2))  # +2 为留出一些边距

        self.dropdown.config(width=optimal_width)

    def on_selection_change(self, event=None):
        """处理选择改变事件"""
        if self.callback:
            self.callback(self.get_value())

    def set_value(self, value):
        """设置下拉菜单的值"""
        if value in self.display_options:
            # 如果是显示文本
            self.selected_display.set(value)
        elif value in self.option_values.values():
            # 如果是实际值，找到对应的显示文本
            for display, val in self.option_values.items():
                if val == value:
                    self.selected_display.set(display)
                    break
        else:
            print(f"警告: 值 '{value}' 不在下拉菜单选项中")

    def get_value(self):
        """获取下拉菜单的当前值"""
        display_text = self.selected_display.get()
        return self.option_values.get(display_text, display_text)

    def get_label(self):
        """获取标签文本"""
        return self.label_text

    def grid(self, **kwargs):
        """打包组件"""
        self.frame.grid(**kwargs)

    def disable(self):
        """禁用下拉菜单"""
        self.dropdown.config(state=tk.DISABLED)

    def enable(self):
        """启用下拉菜单"""
        self.dropdown.config(state="readonly")

    def update_options(self, new_options, new_default=None):
        """动态更新下拉菜单的选项"""
        # 获取当前选择的值
        current_value = self.get_value()

        # 处理新选项
        if isinstance(new_options, dict):
            self.display_options = list(new_options.keys())
            self.option_values = new_options
        elif isinstance(new_options, list):
            self.display_options = new_options
            self.option_values = {opt: opt for opt in new_options}
        else:
            raise ValueError("选项必须是列表或字典")
            
        # 更新下拉菜单的值列表
        self.dropdown['values'] = self.display_options

        # 重新调整下拉菜单宽度
        self._update_dropdown_width()

        # 确定要设置的值
        if new_default is not None:
            target_value = new_default
        elif current_value in self.option_values.values():
            # 如果当前值仍然有效，保持它
            target_value = current_value
        elif self.display_options:
            # 否则选择第一个选项
            target_value = list(self.option_values.values())[0]
        else:
            target_value = None

        # 设置新值
        if target_value is not None:
            self.set_value(target_value)

        # 触发回调（如果值发生了变化）
        if hasattr(self, 'callback') and self.callback and target_value != current_value:
            self.callback(target_value)
