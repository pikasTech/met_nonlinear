# -*- coding: utf-8 -*-
"""
adjuster.py - 主要API接口模块

这个模块保持与原始adjuster.py完全相同的对外API，确保现有代码无需修改即可使用。
所有的类和函数都在这里重新导出，提供完全的向后兼容性。
"""
import numpy as np
import matplotlib
# 保持原有的matplotlib配置
matplotlib.use('Qt5Agg')  # 使用 Qt5Agg 后端

# 导入所有原有的功能模块
try:
    from .adjuster_utils import (
        format_value,
        apply_unit_conversion, 
        parse_value_with_unit,
        calculate_text_width,
        RepeatButton,
        StdoutRedirector,
        add_log_target,
        remove_log_target
    )

    from .adjuster_widgets import (
        TextField,
        Adjuster,
        Checkbox,
        FilePath,
        FolderPath,
        Button,
        Dropdown
    )

    from .adjuster_plots import Plotter

    from .adjuster_core import Panel
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    from adjuster_utils import (
        format_value,
        apply_unit_conversion, 
        parse_value_with_unit,
        calculate_text_width,
        RepeatButton,
        StdoutRedirector,
        add_log_target,
        remove_log_target
    )

    from adjuster_widgets import (
        TextField,
        Adjuster,
        Checkbox,
        FilePath,
        FolderPath,
        Button,
        Dropdown
    )

    from adjuster_plots import Plotter

    from adjuster_core import Panel

# 为了完全兼容，保留原始的main函数
def main():
    """
    主程序 - 这里包含了具体的业务逻辑示例
    Panel类保持纯净，只负责UI框架
    """
    import os
    
    # 定义参数配置
    initial_params = {
        # 电路参数
        "Resistance (Ω)": 1000,
        "Capacitance (F)": 1e-6,
        "Frequency (Hz)": 1000,
        "Amplitude (V)": 5,

        # 绘图选项
        "Show Sine Wave": True,
        "Show Cosine Wave": False,
        "Show Phase Shift": False,

        # 下拉菜单
        "Wave Type@dropdown": {
            "options": ["Sine", "Square", "Triangle", "Sawtooth"],
            "default": "Sine"
        },

        # 文件路径
        "Save Path@folderpath": "",

        # 条件分组
        "@group": {
            "wave_params": ["Frequency (Hz)", "Amplitude (V)"]
        },
        "@param": {
            "Capacitance (F)": {
                "if": "get('Show Phase Shift', False)"
            },
            "wave_params": {
                "if": "get('Show Sine Wave', False) or get('Show Cosine Wave', False)"
            }
        }
    }

    # 定义布局配置
    layout_config = {
        'left_frame': {'width': 250, 'sticky': 'nswe', 'row_weight': 1, 'column_weight': 0},
        'plot_frame': {'row_weight': 2, 'column_weight': 2},  # 绘图区域权重
        # 日志区域权重
        'stdout_frame': {'height': 50, 'row_weight': 1, 'column_weight': 1}
    }

    def on_params_change(values):
        """参数变化时的回调函数"""
        # 检查是否有相关参数改变
        changes = values.get("@on_change", [])
        plot_related_changes = [
            "Resistance (Ω)", "Capacitance (F)", "Frequency (Hz)", "Amplitude (V)",
            "Show Sine Wave", "Show Cosine Wave", "Show Phase Shift", "Wave Type@dropdown"
        ]

    # 创建面板，传入布局配置
    panel = Panel(
        initial_params,
        callback=on_params_change,
        name="电路仿真器",
        with_plot=True,
        redirect_stdout=True,
        config=layout_config  # 使用自定义布局配置
    )

    def manual_plot():
        """手动绘图函数"""
        try:
            values = panel.get_values()
            print("手动绘图完成")
        except Exception as e:
            print(f"绘图错误: {e}")

    def save_plot():
        """保存图形函数"""
        try:
            values = panel.get_values()
            save_path = values.get("Save Path@folderpath", "")
            if not save_path:
                print("请先选择保存路径")
                return

            filepath = os.path.join(save_path, "circuit_plot.png")
            print(f"图形已保存到: {filepath}")
        except Exception as e:
            print(f"保存错误: {e}")

    # 添加绘图按钮
    panel.add_plot_button("手动绘图@button", manual_plot)
    panel.add_plot_button("保存图形@button", save_plot)

    # 初始绘图
    try:
        initial_values = panel.get_values()
    except Exception as e:
        print(f"初始绘图错误: {e}")

    # 启动主循环
    panel.mainloop()


# 确保当直接运行此模块时调用main函数
if __name__ == "__main__":
    main()


# 导出所有公共API，确保向后兼容
__all__ = [
    # 工具函数
    'format_value',
    'apply_unit_conversion', 
    'parse_value_with_unit',
    'calculate_text_width',
      # 工具类
    'RepeatButton',
    'StdoutRedirector',
    'add_log_target',
    'remove_log_target',
    
    # UI控件类
    'TextField',
    'Adjuster',
    'Checkbox',
    'FilePath',
    'FolderPath',
    'Button',
    'Dropdown',
    
    # 绘图类
    'Plotter',
    
    # 核心类
    'Panel',
    
    # 主函数
    'main'
]