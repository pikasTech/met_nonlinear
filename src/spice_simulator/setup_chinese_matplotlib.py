#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置matplotlib支持中文显示
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os
import platform

def check_available_fonts():
    """检查系统中可用的中文字体"""
    print("检查系统中可用的字体...")
    
    # 获取所有字体
    fonts = [f.name for f in fm.fontManager.ttflist]
    
    # 中文字体关键词
    chinese_keywords = ['微黑', 'MicroHei', 'WenQuanYi', 'Noto', 'CJK', 'SimHei', 'Microsoft', 'YaHei']
    
    available_chinese_fonts = []
    for font in fonts:
        for keyword in chinese_keywords:
            if keyword.lower() in font.lower():
                available_chinese_fonts.append(font)
                break
    
    print("可用的中文字体:")
    for font in set(available_chinese_fonts):
        print(f"  - {font}")
    
    return list(set(available_chinese_fonts))

def setup_chinese_fonts():
    """配置matplotlib的中文字体支持"""
    
    print("正在配置matplotlib中文字体...")
    
    # 检查可用字体
    available_fonts = check_available_fonts()
    
    # 设置字体优先级列表
    font_list = []
    
    # 添加检测到的中文字体
    for font in available_fonts:
        font_list.append(font)
    
    # 添加常见的中文字体作为后备
    fallback_fonts = [
        'WenQuanYi Micro Hei',  # 文泉驿微米黑
        'Noto Sans CJK SC',     # 思源黑体简体
        'Noto Sans CJK TC',     # 思源黑体繁体  
        'SimHei',               # 黑体
        'Microsoft YaHei',      # 微软雅黑
        'Arial Unicode MS',     # Arial Unicode
        'DejaVu Sans',          # 默认字体
    ]
    
    for font in fallback_fonts:
        if font not in font_list:
            font_list.append(font)
    
    # 配置matplotlib
    plt.rcParams['font.sans-serif'] = font_list
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    plt.rcParams['font.size'] = 12
    
    print(f"字体配置完成。字体优先级列表:")
    for i, font in enumerate(font_list[:5], 1):  # 只显示前5个
        print(f"  {i}. {font}")
    
    return font_list[0] if font_list else 'DejaVu Sans'

def test_chinese_display():
    """测试中文显示效果"""
    
    # 配置字体
    primary_font = setup_chinese_fonts()
    
    # 创建测试图形
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # 测试1：基本中文文本
    x = np.linspace(0, 2*np.pi, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    
    ax1.plot(x, y1, 'b-', label='正弦波', linewidth=2)
    ax1.plot(x, y2, 'r--', label='余弦波', linewidth=2)
    ax1.set_xlabel('时间 (秒)')
    ax1.set_ylabel('振幅 (伏特)')
    ax1.set_title('三角函数波形图')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 测试2：电路术语
    categories = ['电阻', '电容', '电感', '运放', '二极管']
    values = [10, 15, 8, 12, 6]
    colors = ['red', 'blue', 'green', 'orange', 'purple']
    
    bars = ax2.bar(categories, values, color=colors)
    ax2.set_xlabel('电路元件类型')
    ax2.set_ylabel('数量')
    ax2.set_title('电路元件统计图')
    
    # 添加数值标签
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.2,
                f'{value}个', ha='center', va='bottom')
    
    plt.tight_layout()
    
    # 保存图像
    output_path = './temp/chinese_font_final_test.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n测试图像已保存到: {output_path}")
    
    # 显示图像信息
    print(f"使用的主要字体: {primary_font}")
    print(f"当前matplotlib字体设置: {plt.rcParams['font.sans-serif'][:3]}")
    
    return fig

def create_font_config_file():
    """创建字体配置文件供其他脚本使用"""
    
    config_content = '''# -*- coding: utf-8 -*-
"""
matplotlib中文字体配置
由setup_chinese_matplotlib.py自动生成
"""

import matplotlib.pyplot as plt

def setup_chinese_matplotlib():
    """设置matplotlib中文显示支持"""
    plt.rcParams['font.sans-serif'] = [
        'WenQuanYi Micro Hei',
        'Noto Sans CJK SC', 
        'Noto Sans CJK TC',
        'SimHei',
        'Microsoft YaHei',
        'Arial Unicode MS',
        'DejaVu Sans'
    ]
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['font.size'] = 12

# 自动调用配置
setup_chinese_matplotlib()
'''
    
    config_path = './matplotlib_chinese_config.py'
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"字体配置文件已创建: {config_path}")
    print("在其他脚本中可以使用: import matplotlib_chinese_config")

if __name__ == "__main__":
    print("=== matplotlib中文字体配置和测试 ===")
    print(f"操作系统: {platform.system()}")
    print(f"Python版本: {platform.python_version()}")
    
    # 测试中文显示
    fig = test_chinese_display()
    
    # 创建配置文件
    create_font_config_file()
    
    print("\n=== 配置完成 ===")
    print("如果中文显示正常，说明配置成功！")
    print("如果仍然显示方框，请检查字体安装是否成功。")
    
    # 不显示窗口，只保存图片
    plt.close(fig)