# -*- coding: utf-8 -*-
"""
adjuster_utils.py - 工具函数和辅助类模块

包含格式化函数、重复按钮类和输出重定向类等工具。
"""
import sys
import tkinter as tk
import re


def format_value(value):
    """格式化数值显示，自动添加适当的单位前缀"""
    abs_value = abs(value)
    if abs_value < 1e-9:
        return f"{value * 1e12:.2f} p"  # pico
    elif abs_value < 1e-6:
        return f"{value * 1e9:.2f} n"  # nano
    elif abs_value < 1e-3:
        return f"{value * 1e6:.2f} u"  # micro
    elif abs_value < 1:
        return f"{value * 1e3:.2f} m"  # milli
    elif abs_value < 1e3:
        return f"{value:.2f}"  # No unit, just the number
    elif abs_value < 1e6:
        return f"{value / 1e3:.2f} k"  # kilo
    elif abs_value < 1e9:
        return f"{value / 1e6:.2f} M"  # Mega
    elif abs_value < 1e12:
        return f"{value / 1e9:.2f} G"  # Giga
    else:
        return f"{value / 1e12:.2f} T"  # Tera


def apply_unit_conversion(number, unit):
    """应用单位转换，将带单位的数值转换为基础数值"""
    return {
        '': number,
        'p': number * 1e-12,
        'n': number * 1e-9,
        'u': number * 1e-6,
        'm': number * 1e-3,
        'k': number * 1e3,
        'M': number * 1e6,
        'G': number * 1e9,
        'T': number * 1e12,
    }.get(unit, number)  # Default to no conversion if unit is unrecognized


def parse_value_with_unit(input_str):
    """解析带单位的输入字符串，返回数值和单位"""
    input_str = input_str.replace(' ', '')
    match = re.match(r"([-+]?\d*\.?\d+)([a-zA-Z]*)", input_str)
    if match:
        number_str, unit = match.groups()
        number = float(number_str)
        return number, unit
    else:
        raise ValueError("Invalid format.")


def calculate_text_width(text):
    """
    计算文本宽度，考虑中英文字符的差异
    
    参数:
        text: 要计算宽度的文本
    
    返回:
        估算的字符宽度（按英文字符为1单位计算）
    """
    if not text:
        return 0

    width = 0
    for char in str(text):
        # 中文字符、全角字符等宽字符计为2个单位，其他字符计为1个单位
        if '\u4e00' <= char <= '\u9fff':  # 中文字符
            width += 2
        elif '\uff00' <= char <= '\uffef':  # 全角字符
            width += 2
        elif char in '，。；：？！（）【】「」《》〈〉':  # 中文标点
            width += 2
        else:
            width += 1
    return width


class RepeatButton:
    """可重复按下的按钮类，按住时会持续触发动作"""
    
    def __init__(self, frame, text, command):
        self.button = tk.Button(frame, text=text)
        self.command = command
        self.action_in_progress = False
        self.after_id = None

        self.button.bind('<ButtonPress-1>', self.on_press)
        self.button.bind('<ButtonRelease-1>', self.on_release)

    def on_press(self, event):
        if not self.action_in_progress:
            self.action_in_progress = True
            self.perform_action()

    def on_release(self, event):
        self.action_in_progress = False
        if self.after_id is not None:
            self.button.after_cancel(self.after_id)
            self.after_id = None

    def perform_action(self):
        if self.action_in_progress:
            self.command()
            self.after_id = self.button.after(250, self.perform_action)

    def grid(self, **kwargs):
        self.button.grid(**kwargs)

    def disable(self):
        self.button.config(state=tk.DISABLED)

    def enable(self):
        self.button.config(state=tk.NORMAL)


class MultiStdoutRedirector:
    """多重标准输出重定向类，支持同时向多个log控件输出"""
    
    def __init__(self):
        self.redirectors = []
    
    def add_redirector(self, text_widget, panel=None):
        """添加一个新的重定向目标"""
        redirector = StdoutRedirector(text_widget, panel)
        self.redirectors.append(redirector)
        return redirector
    
    def remove_redirector(self, redirector):
        """移除一个重定向目标"""
        if redirector in self.redirectors:
            self.redirectors.remove(redirector)
    
    def write(self, message):
        # 向所有活跃的重定向器输出
        for redirector in self.redirectors[:]:  # 使用切片避免迭代时修改列表
            try:
                if hasattr(redirector.text_widget, 'winfo_exists') and redirector.text_widget.winfo_exists():
                    redirector.write(message)
                else:
                    # 如果widget已经不存在，移除这个重定向器
                    self.redirectors.remove(redirector)
            except Exception:
                # 如果出现异常，移除这个重定向器
                try:
                    self.redirectors.remove(redirector)
                except ValueError:
                    pass
        
        # 同时输出到原始stdout
        sys.__stdout__.write(message)
        sys.__stdout__.flush()
    
    def flush(self):
        # 刷新所有重定向器
        for redirector in self.redirectors[:]:
            try:
                if hasattr(redirector.text_widget, 'winfo_exists') and redirector.text_widget.winfo_exists():
                    redirector.flush()
                else:
                    self.redirectors.remove(redirector)
            except Exception:
                try:
                    self.redirectors.remove(redirector)
                except ValueError:
                    pass
        
        # 刷新原始stdout
        sys.__stdout__.flush()


class StdoutRedirector:
    """标准输出重定向类，用于将输出重定向到UI文本框"""
    
    def __init__(self, text_widget, panel=None):
        self.text_widget = text_widget
        self.panel = panel

    def write(self, message):
        # 确保在主线程中更新UI
        if hasattr(self.text_widget, 'winfo_exists') and self.text_widget.winfo_exists():
            self.text_widget.configure(state='normal')  # 设置为可编辑状态
            self.text_widget.insert(tk.END, message)
            self.text_widget.see(tk.END)
            self.text_widget.configure(state='disabled')  # 设置为只读状态

            # 强制更新UI显示
            self.text_widget.update_idletasks()
            # 如果有主窗口，也更新它
            if hasattr(self.text_widget, 'master') and self.text_widget.master:
                try:
                    self.text_widget.master.update_idletasks()
                except:
                    pass

    def flush(self):
        # 强制更新UI
        if hasattr(self.text_widget, 'winfo_exists') and self.text_widget.winfo_exists():
            try:
                self.text_widget.update_idletasks()
                if hasattr(self.text_widget, 'master') and self.text_widget.master:
                    self.text_widget.master.update_idletasks()
            except:
                pass


# 全局多重重定向器实例
_global_redirector = None


def get_global_redirector():
    """获取全局多重重定向器实例"""
    global _global_redirector
    if _global_redirector is None:
        _global_redirector = MultiStdoutRedirector()
        # 设置为sys.stdout和sys.stderr
        sys.stdout = _global_redirector
        sys.stderr = _global_redirector
    return _global_redirector


def add_log_target(text_widget, panel=None):
    """添加一个新的log输出目标"""
    redirector = get_global_redirector()
    return redirector.add_redirector(text_widget, panel)


def remove_log_target(redirector):
    """移除一个log输出目标"""
    global _global_redirector
    if _global_redirector:
        _global_redirector.remove_redirector(redirector)
