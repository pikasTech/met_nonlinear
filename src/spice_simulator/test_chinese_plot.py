#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试matplotlib中文显示配置
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

# 配置matplotlib支持中文显示
def setup_chinese_fonts():
    """配置matplotlib的中文字体支持"""
    
    # 设置字体家族，按优先级排列
    plt.rcParams['font.sans-serif'] = [
        'DejaVu Sans',  # 默认字体
        'SimHei',       # 黑体 (Windows)
        'Microsoft YaHei',  # 微软雅黑 (Windows)
        'WenQuanYi Micro Hei',  # 文泉驿微米黑 (Linux)
        'Noto Sans CJK SC',     # 思源黑体 (跨平台)
        'Arial Unicode MS',     # Arial Unicode (macOS)
    ]
    
    # 解决负号显示问题
    plt.rcParams['axes.unicode_minus'] = False
    
    # 设置默认字体大小
    plt.rcParams['font.size'] = 12
    
    print("已配置matplotlib中文字体支持")
    print(f"当前字体设置: {plt.rcParams['font.sans-serif']}")

def test_chinese_plot():
    """测试中文显示的简单绘图"""
    
    # 生成测试数据
    x = np.linspace(0, 2*np.pi, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    
    # 创建图形
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # 第一个子图 - 正弦和余弦曲线
    ax1.plot(x, y1, 'b-', label='正弦波 sin(x)', linewidth=2)
    ax1.plot(x, y2, 'r--', label='余弦波 cos(x)', linewidth=2)
    ax1.set_xlabel('时间 (秒)')
    ax1.set_ylabel('幅值 (伏特)')
    ax1.set_title('三角函数波形对比图')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 第二个子图 - 频率响应示例
    freq = np.logspace(1, 5, 100)  # 10Hz到100kHz
    magnitude = 1 / (1 + (freq/1000)**2)  # 低通滤波器响应
    phase = -np.arctan(freq/1000) * 180/np.pi  # 相位响应
    
    ax2_phase = ax2.twinx()
    
    line1 = ax2.semilogx(freq, 20*np.log10(magnitude), 'b-', linewidth=2, label='幅频响应')
    line2 = ax2_phase.semilogx(freq, phase, 'r-', linewidth=2, label='相频响应')
    
    ax2.set_xlabel('频率 (赫兹)')
    ax2.set_ylabel('幅值 (分贝)', color='b')
    ax2_phase.set_ylabel('相位 (度)', color='r')
    ax2.set_title('低通滤波器的频率响应特性')
    ax2.grid(True, alpha=0.3)
    
    # 合并图例
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax2.legend(lines, labels, loc='upper right')
    
    plt.tight_layout()
    
    # 保存图像
    output_path = './temp/chinese_font_test.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"测试图像已保存到: {output_path}")
    
    # 显示图像
    plt.show()

def test_circuit_terms():
    """测试电路专业术语的显示"""
    
    # 常用的电路术语
    terms = [
        '电阻 (Ω)', '电容 (F)', '电感 (H)', '电压 (V)', '电流 (A)',
        '功率 (W)', '频率 (Hz)', '阻抗 (Ω)', '导纳 (S)', '增益 (dB)'
    ]
    
    values = [10, 22, 15, 8, 12, 18, 25, 14, 16, 20]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    bars = ax.bar(range(len(terms)), values, 
                  color=['red', 'orange', 'yellow', 'green', 'blue', 
                         'indigo', 'violet', 'pink', 'brown', 'gray'])
    
    ax.set_xlabel('电路参数类型')
    ax.set_ylabel('数值大小')
    ax.set_title('电路仿真器中的各种电路参数分布图')
    ax.set_xticks(range(len(terms)))
    ax.set_xticklabels(terms, rotation=45, ha='right')
    
    # 在柱状图上添加数值标签
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{value}', ha='center', va='bottom')
    
    plt.tight_layout()
    
    # 保存图像
    output_path = './temp/circuit_terms_test.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"电路术语测试图像已保存到: {output_path}")
    
    plt.show()

if __name__ == "__main__":
    print("=== matplotlib中文字体配置测试 ===")
    
    # 配置中文字体
    setup_chinese_fonts()
    
    print("\n=== 测试1: 基本中文绘图 ===")
    test_chinese_plot()
    
    print("\n=== 测试2: 电路专业术语显示 ===")
    test_circuit_terms()
    
    print("\n=== 测试完成 ===")
    print("如果图像中的中文正常显示，说明配置成功")
    print("如果显示为方框，可能需要安装中文字体包:")
    print("  Ubuntu: sudo apt-get install fonts-wqy-microhei fonts-noto-cjk")
    print("  CentOS: sudo yum install wqy-microhei-fonts")