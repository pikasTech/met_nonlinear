import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import time

# 原始的每通道 IIRFilterLayer 实现


class IIRFilterLayer(tf.keras.layers.Layer):
    def __init__(self, units=1, a1_list=None, a2_list=None, b0_list=None, b1_list=None, b2_list=None,
                 learning_rate=0.1, trainable=True, fs=2000, **kwargs):
        super(IIRFilterLayer, self).__init__(**kwargs)
        self.units = units
        self.a1_list = a1_list if a1_list is not None else [0.0] * units
        self.a2_list = a2_list if a2_list is not None else [0.0] * units
        self.b0_list = b0_list if b0_list is not None else [0.1] * units
        self.b1_list = b1_list if b1_list is not None else [0.2] * units
        self.b2_list = b2_list if b2_list is not None else [0.3] * units
        self.fs = fs
        self.learning_rate = learning_rate
        self.trainable = trainable
        self.filter_models = []

    def build(self, input_shape):
        for i in range(self.units):
            a1 = self.a1_list[i]
            a2 = self.a2_list[i]
            b0 = self.b0_list[i]
            b1 = self.b1_list[i]
            b2 = self.b2_list[i]

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

            W_hh = A.T
            W_xh = B.T

            filter_model = tf.keras.Sequential()
            filter_model.add(tf.keras.layers.SimpleRNN(
                units=4,
                activation='linear',
                use_bias=False,
                return_sequences=True,
                input_shape=(None, 1),
                trainable=self.trainable
            ))
            filter_model.add(tf.keras.layers.Dense(
                1, activation=None, use_bias=False, trainable=False))

            filter_model.layers[0].set_weights([W_xh, W_hh])
            filter_model.layers[1].set_weights([C.T])

            self.filter_models.append(filter_model)

    def call(self, inputs):
        outputs_list = []
        for i in range(self.units):
            x = inputs[:, :, i:i+1]
            y = self.filter_models[i](x)
            outputs_list.append(y)
        outputs = tf.concat(outputs_list, axis=2)
        return outputs

# 高效的多通道 IIRFilterLayer 实现


class DIAGIIR(tf.keras.layers.Layer):
    def __init__(self,
                 units=1,
                 a1_list=None,
                 a2_list=None,
                 b0_list=None,
                 b1_list=None,
                 b2_list=None,
                 learning_rate=0.1,
                 trainable=False,
                 init_by_system=True,
                 fs=2000,
                 debug=False,
                 **kwargs):
        super(DIAGIIR, self).__init__(**kwargs)
        self.units = units
        self.state_size = 4  # 每个滤波器的状态维度
        self.a1_list = a1_list if a1_list is not None else [0.0] * units
        self.a2_list = a2_list if a2_list is not None else [0.0] * units
        self.b0_list = b0_list if b0_list is not None else [0.1] * units
        self.b1_list = b1_list if b1_list is not None else [0.2] * units
        self.b2_list = b2_list if b2_list is not None else [0.3] * units
        self.fs = fs
        self.learning_rate = learning_rate
        self.trainable = trainable
        self.debug = debug
        self.init_by_system = init_by_system
        self.built = False

    def build(self, input_shape):
        if self.built:
            return
        self.built = True
        A_blocks = []
        B_blocks = []
        C_blocks = []

        for i in range(self.units):
            a1 = self.a1_list[i]
            a2 = self.a2_list[i]
            b0 = self.b0_list[i]
            b1 = self.b1_list[i]
            b2 = self.b2_list[i]

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

            A_blocks.append(A)
            B_blocks.append(B)
            C_blocks.append(C)

        # 构建块对角矩阵
        A_block_diag = tf.linalg.LinearOperatorBlockDiag(
            [tf.linalg.LinearOperatorFullMatrix(A) for A in A_blocks]
        ).to_dense().numpy()

        B_block_diag = tf.linalg.LinearOperatorBlockDiag(
            [tf.linalg.LinearOperatorFullMatrix(B) for B in B_blocks]
        ).to_dense().numpy()

        # 构建 Dense 层的权重矩阵
        W_dense = np.zeros((self.units * self.state_size,
                            self.units), dtype=np.float32)
        for i in range(self.units):
            # 将每个通道的 C 矩阵（形状为 (1, state_size)）转置并展平，得到形状为 (state_size,)
            C_i = C_blocks[i].reshape(-1)
            # 将 C_i 放入 W_dense 的对应位置
            W_dense[i * self.state_size:(i + 1) * self.state_size, i] = C_i

        # 转置矩阵以匹配 TensorFlow 的权重形状
        W_hh = A_block_diag.T  # 形状：(units * state_size, units * state_size)
        W_xh = B_block_diag.T  # 形状：(units, units * state_size)

        # 构建滤波器模型
        self.filter_model = tf.keras.Sequential()
        self.filter_model.add(tf.keras.layers.SimpleRNN(
            units=self.units * self.state_size,
            activation='linear',
            use_bias=False,
            return_sequences=True,
            trainable=self.trainable
        ))
        self.filter_model.add(tf.keras.layers.Dense(
            self.units, activation=None, use_bias=False, trainable=False))

        self.filter_model.build(input_shape=(None, None, self.units))
        # 设置权重
        if self.init_by_system:
            self.filter_model.layers[0].set_weights([W_xh, W_hh])
            self.filter_model.layers[1].set_weights([W_dense])

        if self.debug:
            self.filter_model.summary()

    def call(self, inputs):
        # 复制输入数据以匹配通道数
        if self.units > 1:
            inputs = tf.tile(inputs, [1, 1, self.units])
            # inputs 的形状：(batch_size, timesteps, units)
        outputs = self.filter_model(inputs)
        return outputs


class SIMOIIR(tf.keras.layers.Layer):
    def __init__(self,
                 units=1,
                 a1_list=None,
                 a2_list=None,
                 b0_list=None,
                 b1_list=None,
                 b2_list=None,
                 trainable=False,
                 init_by_system=True,
                 fs=2000,
                 **kwargs):
        super(SIMOIIR, self).__init__(**kwargs)
        self.units = units
        self.a1_list = a1_list if a1_list is not None else [0.0]*units
        self.a2_list = a2_list if a2_list is not None else [0.0]*units
        self.b0_list = b0_list if b0_list is not None else [0.1]*units
        self.b1_list = b1_list if b1_list is not None else [0.2]*units
        self.b2_list = b2_list if b2_list is not None else [0.3]*units
        self.trainable = trainable
        self.init_by_system = init_by_system
        self.fs = fs
        self.filters = []
        self.need_expansion = False
        self.built = False

    def build(self, input_shape):
        if self.built:
            return
        self.built = True
        input_dim = input_shape[-1]
        # 假设输入是单通道，如果不是，需要在call中处理
        if input_dim != 1:
            self.need_expansion = True

        for i in range(self.units):
            # 针对每个通道创建一个DIAGIIR(units=1)实例
            f = DIAGIIR(
                units=1,
                a1_list=[self.a1_list[i]],
                a2_list=[self.a2_list[i]],
                b0_list=[self.b0_list[i]],
                b1_list=[self.b1_list[i]],
                b2_list=[self.b2_list[i]],
                trainable=self.trainable,
                init_by_system=self.init_by_system,
                fs=self.fs
            )
            # build单通道输入
            f.build((None, None, 1))
            self.filters.append(f)

    def call(self, inputs):
        # 如果输入不是单通道，这里仅取第一通道作为输入信号
        # 或根据需求扩展同一个信号到所有通道
        if self.need_expansion:
            inputs = inputs[:, :, :1]  # 简化处理：只取第一通道作为输入

        # 每个通道使用同一输入信号进行滤波
        outputs = []
        for f in self.filters:
            y = f(inputs)  # (batch_size, timesteps, 1)
            outputs.append(y)

        # 拼接输出 (batch_size, timesteps, units)
        return tf.concat(outputs, axis=-1)


def run_performance_test(batch_size, timesteps, units):
    print(
        f"\n测试参数: batch_size={batch_size}, timesteps={timesteps}, units={units}")

    # 1. 定义滤波器系数
    # 固定 a1 = 0.1, a2 = 0.2
    a1_list = [0.1] * units
    a2_list = [0.2] * units
    b0_list = np.random.randn(units).tolist()
    b1_list = np.random.randn(units).tolist()
    b2_list = np.random.randn(units).tolist()

    # 2. 创建示例输入数据
    np.random.seed(0)
    input_data = np.random.randn(
        batch_size, timesteps, units).astype(np.float32)

    # 3. 实例化两个模型
    original_layer = IIRFilterLayer(
        units=units,
        a1_list=a1_list,
        a2_list=a2_list,
        b0_list=b0_list,
        b1_list=b1_list,
        b2_list=b2_list,
        trainable=False
    )

    efficient_layer = DIAGIIR(
        units=units,
        a1_list=a1_list,
        a2_list=a2_list,
        b0_list=b0_list,
        b1_list=b1_list,
        b2_list=b2_list,
        trainable=False
    )

    # 构建模型（必要的步骤以设置权重）
    original_layer.build(input_data.shape)
    efficient_layer.build(input_data.shape)

    # 预热（使 JIT 编译器优化）
    _ = original_layer(input_data)
    _ = efficient_layer(input_data)

    # 4. 测试原始模型的运行时间
    start_time = time.perf_counter()
    original_output = original_layer(input_data)
    end_time = time.perf_counter()
    original_time = end_time - start_time

    # 5. 测试高效模型的运行时间
    start_time = time.perf_counter()
    efficient_output = efficient_layer(input_data)
    end_time = time.perf_counter()
    efficient_time = end_time - start_time

    # 6. 比较输出
    difference = np.abs(original_output.numpy() - efficient_output.numpy())
    max_difference = np.max(difference)

    # 7. 输出结果
    print(f"原始模型运行时间: {original_time:.6f} 秒")
    print(f"高效模型运行时间: {efficient_time:.6f} 秒")
    print(f"两者运行时间之比（原始/高效）: {original_time / efficient_time:.2f}")
    print(f"最大输出差异: {max_difference}")


def test_iir_mimoiir():
    # Number of units
    units = 3

    # Filter coefficients for each unit (they are different)
    a1_list = [-1.8, -1.7, -1.6]
    a2_list = [0.81, 0.72, 0.64]
    b0_list = [0.1, 0.2, 0.3]
    b1_list = [0.2, 0.3, 0.4]
    b2_list = [0.3, 0.4, 0.5]

    # Generate input signal (same for all units)
    N = 100
    n = np.arange(N)
    x = np.sin(0.1 * np.pi * n)

    # Compute IIR filter outputs using the standard difference equation for each unit
    y_iir_list = []
    for i in range(units):
        a1 = a1_list[i]
        a2 = a2_list[i]
        b0 = b0_list[i]
        b1 = b1_list[i]
        b2 = b2_list[i]

        y_iir = np.zeros(N)
        for k in range(N):
            x_k = x[k]
            x_k1 = x[k-1] if k-1 >= 0 else 0
            x_k2 = x[k-2] if k-2 >= 0 else 0
            y_k1 = y_iir[k-1] if k-1 >= 0 else 0
            y_k2 = y_iir[k-2] if k-2 >= 0 else 0

            y_iir[k] = b0 * x_k + b1 * x_k1 + b2 * x_k2 - a1 * y_k1 - a2 * y_k2
        y_iir_list.append(y_iir)

    # Stack the outputs to shape (N, units)
    y_iir_array = np.stack(y_iir_list, axis=-1)  # Shape: (N, units)

    # Now, create an instance of EfficientIIRFilterLayer with the given coefficients
    # Instantiate the layer
    efficient_layer = SIMOIIR(
        units=units,
        a1_list=a1_list,
        a2_list=a2_list,
        b0_list=b0_list,
        b1_list=b1_list,
        b2_list=b2_list
    )

    # Build the layer (input_shape is (batch_size, timesteps, units))
    efficient_layer.build(input_shape=(None, None, 1))
    # 打印出模型的参数数量

    # Prepare input data
    # Shape: (batch_size, timesteps, units)
    x_input = x.reshape(1, -1, 1).astype(np.float32)

    # Run the model
    y_pred = efficient_layer(x_input)
    y_efficient = y_pred[0].numpy()  # Shape: (N, units)

    print("EfficientIIRFilterLayer 参数数量:", efficient_layer.count_params())

    # Compare the outputs
    difference = y_iir_array - y_efficient
    max_error = np.max(np.abs(difference))
    print("IIR filter outputs vs EfficientIIRFilterLayer outputs maximum absolute error:", max_error)

    # Plot the outputs for comparison
    plt.figure(figsize=(12, 6))
    for i in range(units):
        plt.plot(n, y_iir_array[:, i], label=f'IIR Filter Output Unit {i+1}')
        plt.plot(n, y_efficient[:, i], 'o',
                 label=f'EfficientIIRFilterLayer Output Unit {i+1}', markersize=4)
    plt.legend()
    plt.title('IIR Filter vs EfficientIIRFilterLayer Outputs Comparison')
    plt.xlabel('Sample Index')
    plt.ylabel('Output')
    plt.grid(True)
    # plt.show()  # 移除以避免测试阻塞

    # Plot the difference
    plt.figure(figsize=(12, 4))
    for i in range(units):
        plt.plot(n, difference[:, i], label=f'Difference Unit {i+1}')
    plt.legend()
    plt.title('Difference between IIR Filter and EfficientIIRFilterLayer Outputs')
    plt.xlabel('Sample Index')
    plt.ylabel('Difference')
    plt.grid(True)
    # plt.show()  # 移除以避免测试阻塞


def test_performance():
    # 调整以下参数以测试不同的数据规模
    batch_size_list = [1, 10, 100]
    timesteps_list = [100, 500, 1000]
    units_list = [2, 10, 50]

    # 对不同的数据规模进行测试
    for batch_size in batch_size_list:
        for timesteps in timesteps_list:
            for units in units_list:
                run_performance_test(batch_size, timesteps, units)


def test_single_unit_iir():
    print("Testing single-unit IIR functionality...")

    # 单通道滤波器系数
    a1_list = [-1.8]
    a2_list = [0.81]
    b0_list = [0.1]
    b1_list = [0.2]
    b2_list = [0.3]

    # 生成输入信号
    N = 100
    n = np.arange(N)
    x = np.sin(0.1 * np.pi * n)

    # 使用标准差分方程计算 IIR 输出
    y_iir = np.zeros(N)
    for k in range(N):
        x_k = x[k]
        x_k1 = x[k - 1] if k - 1 >= 0 else 0
        x_k2 = x[k - 2] if k - 2 >= 0 else 0
        y_k1 = y_iir[k - 1] if k - 1 >= 0 else 0
        y_k2 = y_iir[k - 2] if k - 2 >= 0 else 0

        y_iir[k] = b0_list[0] * x_k + b1_list[0] * x_k1 + \
            b2_list[0] * x_k2 - a1_list[0] * y_k1 - a2_list[0] * y_k2

    # 创建 SIMOIIR 层并设置单通道
    simo_layer = DIAGIIR(
        units=1,
        a1_list=a1_list,
        a2_list=a2_list,
        b0_list=b0_list,
        b1_list=b1_list,
        b2_list=b2_list,
        trainable=False
    )

    # 构建层并运行
    simo_layer.build(input_shape=(None, None, 1))
    x_input = x.reshape(1, -1, 1).astype(np.float32)
    y_pred = simo_layer(x_input).numpy().flatten()

    # 比较输出
    difference = y_iir - y_pred
    max_error = np.max(np.abs(difference))
    print("Maximum absolute error for single-unit test:", max_error)

    # 可视化结果
    plt.figure(figsize=(12, 6))
    plt.plot(n, y_iir, label='IIR Filter Output')
    plt.plot(n, y_pred, 'o', label='SIMOIIR Output', markersize=4)
    plt.legend()
    plt.title('Single-Unit IIR Filter vs SIMOIIR Output')
    plt.xlabel('Sample Index')
    plt.ylabel('Output')
    plt.grid(True)
    # plt.show()  # 移除以避免测试阻塞

    # 差异可视化
    plt.figure(figsize=(12, 4))
    plt.plot(n, difference, label='Difference')
    plt.legend()
    plt.title('Difference between IIR Filter and SIMOIIR Output (Single Unit)')
    plt.xlabel('Sample Index')
    plt.ylabel('Difference')
    plt.grid(True)
    # plt.show()  # 移除以避免测试阻塞


if __name__ == "__main__":
    # test_iir_mimoiir()
    # test_performance()
    test_single_unit_iir()
    # plt.show()  # 移除以避免测试阻塞
