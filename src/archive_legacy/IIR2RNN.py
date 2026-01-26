import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from matplotlib import rcParams

if __name__ == "__main__":
    # 设置中文字体和取消负号前的空格
    rcParams['font.sans-serif'] = ['SimHei']  # 设置字体为黑体
    rcParams['axes.unicode_minus'] = False    # 解决负号显示问题

    # 滤波器系数
    a1 = -1.8
    a2 = 0.81
    b0 = 0.1
    b1 = 0.2
    b2 = 0.3

    # 生成输入信号
    N = 100
    n = np.arange(N)
    x = np.sin(0.1 * np.pi * n)

    # 计算 IIR 滤波器的输出
    y_iir = np.zeros(N)
    for k in range(N):
        x_k = x[k]
        x_k1 = x[k-1] if k-1 >= 0 else 0
        x_k2 = x[k-2] if k-2 >= 0 else 0
        y_k1 = y_iir[k-1] if k-1 >= 0 else 0
        y_k2 = y_iir[k-2] if k-2 >= 0 else 0

        y_iir[k] = b0 * x_k + b1 * x_k1 + b2 * x_k2 - a1 * y_k1 - a2 * y_k2

    # 定义状态空间矩阵
    A = np.array([
        [-a1, -a2, b1, b2],
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0]
    ], dtype=np.float32)

    B = np.array([
        [b0],
        [0.0],
        [1.0],
        [0.0]
    ], dtype=np.float32)

    C = np.array([[1.0, 0.0, 0.0, 0.0]], dtype=np.float32)

    # 转置矩阵以匹配 TensorFlow 的权重形状
    W_xh = B.T  # Shape: (1, 4)
    W_hh = A.T  # Shape: (4, 4)

    # 创建 Sequential 模型
    model = tf.keras.Sequential()

    # 添加 RNN 层
    rnn_layer = tf.keras.layers.SimpleRNN(
        units=4,
        activation='linear',
        use_bias=False,
        return_sequences=True,
        input_shape=(None, 1)
    )

    model.add(rnn_layer)
    # 手动设置 RNN 层的权重
    rnn_layer.set_weights([W_xh, W_hh])

    # 添加 Dense 层
    dense_layer = tf.keras.layers.Dense(
        units=1,
        activation=None,
        use_bias=False
    )

    model.add(dense_layer)
    # 设置 Dense 层的权重
    dense_layer.set_weights([C.T])

    # 编译模型（这里不需要实际训练，只是为了统一编译）
    model.compile(optimizer='sgd', loss='mse')

    # 准备输入数据
    x_input = x.reshape(1, -1, 1)  # Shape: (batch_size, time_steps, 1)

    # 运行模型
    y_rnn = model.predict(x_input)[0, :, 0]

    # 比较两个输出
    difference = y_iir - y_rnn
    max_error = np.max(np.abs(difference))
    print("IIR 滤波器输出与 TensorFlow RNN 输出的最大绝对误差:", max_error)

    # 绘制输出比较
    plt.figure(figsize=(12, 6))
    plt.plot(n, y_iir, label='IIR 滤波器输出')
    plt.plot(n, y_rnn, 'o', label='TensorFlow RNN 输出', markersize=4)
    plt.legend()
    plt.title('IIR 滤波器与 TensorFlow RNN 输出比较')
    plt.xlabel('样本序号')
    plt.ylabel('输出')
    plt.grid(True)
    plt.show()

    # 绘制误差
    plt.figure(figsize=(12, 4))
    plt.plot(n, difference)
    plt.title('IIR 滤波器与 TensorFlow RNN 输出的差异')
    plt.xlabel('样本序号')
    plt.ylabel('差异')
    plt.grid(True)
    plt.show()
