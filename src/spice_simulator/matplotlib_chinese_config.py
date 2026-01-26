# -*- coding: utf-8 -*-
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
