#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的中文显示测试
"""

import matplotlib.pyplot as plt
import numpy as np

# 导入中文字体配置
try:
    import matplotlib_chinese_config
    print("已加载中文字体配置")
except ImportError:
    print("警告: 未找到中文字体配置文件")

# 创建简单的测试图
fig, ax = plt.subplots(figsize=(10, 6))

x = np.linspace(0, 10, 100)
y = np.sin(x)

ax.plot(x, y, 'b-', linewidth=2, label='正弦波')
ax.set_xlabel('时间 (秒)')
ax.set_ylabel('电压 (伏特)')
ax.set_title('SPICE仿真器测试 - 中文显示验证')
ax.grid(True, alpha=0.3)
ax.legend()

# 添加中文注释
ax.text(5, 0.5, '这是中文注释\n电路仿真结果', 
        bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.5),
        fontsize=12, ha='center')

plt.tight_layout()

# 保存图像
output_path = './temp/chinese_simple_test.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"测试图像已保存到: {output_path}")

# 关闭图形，不显示窗口
plt.close(fig)

print("中文显示测试完成")