import matplotlib.pyplot as plt

# 创建一个简单的图
x = [1, 2, 3, 4, 5]
y = [10, 20, 30, 40, 50]
plt.plot(x, y, label='Sample Data')

# 获取当前的坐标轴
ax = plt.gca()

# 在图中绘制向右的箭头
ax.arrow(
    x=1.5, y=35,             # 箭头起始点坐标
    dx=2.5, dy=0,            # 箭头的长度（x方向）和高度（y方向）
    head_width=2,            # 箭头头部的宽度
    head_length=0.3,         # 箭头头部的长度
    fc='black', ec='black'   # 箭头颜色
)

# 在箭头旁边添加文字
plt.text(
    3, 38,                   # 文字的位置
    'Data size increases to the right',  # 文字内容
    fontsize=12              # 字体大小
)

# 设置图的标题和标签
plt.title('Sample Plot with Arrow Annotation')
plt.xlabel('X-axis')
plt.ylabel('Y-axis')

# 显示图例和图形
plt.legend()
plt.show()
