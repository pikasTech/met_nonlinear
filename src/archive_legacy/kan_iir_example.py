from cli import *


def IIR_KAN_base():
    epoch_train = 100
    epoch_mlp = 1000
    units_mlp = 128
    batch_size = 4000

    USE_MPL = False
    USE_TRAIN_KAN = True  # 设置为True时进行训练，否则加载权重文件
    USE_PREDICT = True  # 设置为True时进行预测
    use_spline = True  # 显示样条曲线
    USE_FR = True
    use_scale = True  # 设置为True时进行数据归一化
    sample_rate = 2000

    # 模型权重文件路径
    weights_file = 'kan_model.weights.h5'

    # 导入数据
    X = np.load('data/feature_vector.npy')
    y = np.load('data/output.npy')

    def select_and_reshape_feature_vector(X, y, sweep_indices, point_indices):
        selected_X_slices = []
        selected_y_slices = []
        for sweep_idx in sweep_indices:
            for point_idx in point_indices:
                selected_X_slices.append(X[sweep_idx, point_idx])
                selected_y_slices.append(y[sweep_idx, point_idx])
        reshaped_X = np.concatenate(selected_X_slices, axis=0)
        reshaped_y = np.concatenate(selected_y_slices, axis=0)
        return reshaped_X, reshaped_y

    X, y = select_and_reshape_feature_vector(X, y, range(0, 20), range(0, 20))

    if use_scale:
        # 使用 MinMaxScaler 进行按列归一化
        scaler_x = MinMaxScaler()
        X = scaler_x.fit_transform(X)
        scaler_y = MinMaxScaler()
        y = scaler_y.fit_transform(y.reshape(-1, 1)).reshape(-1)

    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.05)
    print(f'X range: {X.min()} to {X.max()}')
    print(f'y range: {y.min()} to {y.max()}')

    if USE_MPL:
        mlp = tf.keras.models.Sequential([
            tf.keras.layers.Dense(units_mlp, activation='relu'),
            tf.keras.layers.Dense(1)
        ])
        mlp.build(input_shape=(None, 3))
        mlp.summary()
        mlp.compile(optimizer=tf.keras.optimizers.Adam(
            learning_rate=2e-3), loss='mse', metrics=['mae'])
        mlp_history = mlp.fit(x_train, y_train, epochs=epoch_mlp, batch_size=64,
                              verbose=1)

    # KAN模型
    # kan = tf.keras.models.Sequential([
    #     DenseKAN(1, grid_size=20)
    # ])

    data_info_list = find_data_info("data/M50")
    for data_info in data_info_list:
        print(data_info)

    # 取第一个数据
    ws = System.loadFile(data_info_list[0].file_path)
    ws_fit = exam_process.ws_system_fit(ws, k=1.0, freq_range=(5, 200))

    ws2 = System.loadFile(data_info_list[10].file_path)
    ws2_fit = exam_process.ws_system_fit(ws2, k=1.0, freq_range=(5, 200))

    iir_kan = FRIKAN.fromSystem(
        [ws_fit, ws2_fit], fs=sample_rate, learning_rate=0.1, grid_size=20, grid_range=(-1, 2), spline_order=2)
    iir_kan.set_scaler(scaler_x, scaler_y)
    iir_kan.summary()

    # 根据USE_TRAIN_KAN的值来决定是否训练模型或加载权重
    if USE_TRAIN_KAN:
        # 训练模型并保存权重
        iir_kan.compile(optimizer=tf.keras.optimizers.Adam(
            learning_rate=0.1), loss='mse', metrics=['mae'])
        kan_history = iir_kan.fit(
            x_train, y_train,
            epochs=epoch_train,
            batch_size=batch_size,
            verbose=1
        )
        iir_kan.save_weights(weights_file)
    else:
        # 加载权重文件
        if os.path.exists(weights_file):
            iir_kan.load_weights(weights_file)
            print("已成功加载模型权重文件。")
        else:
            print("未找到权重文件，请先将USE_TRAIN_KAN设置为True以训练模型并保存权重。")

    # 绘制训练历史
    if USE_TRAIN_KAN or USE_MPL:
        fig = plt.figure(figsize=(12, 8))
    if USE_TRAIN_KAN and USE_MPL:
        plt.semilogy(mlp_history.history['mae'],
                     label='mlp-train', ls="-", color='red')
    if USE_TRAIN_KAN:
        plt.semilogy(kan_history.history['mae'],
                     label='kan-train', ls="-", color='blue')

    if USE_MPL or USE_TRAIN_KAN:
        plt.xlabel("Epochs")
        plt.ylabel("Mean Absolute Error")
        plt.legend()

    if USE_PREDICT:
        tr_sin = TimeSeries.fromSin(
            A=0.3, f=50, fs=sample_rate, time_length=1, offset=0)
        tr_sin2 = TimeSeries.fromSin(
            A=0.05, f=50, fs=sample_rate, time_length=1, offset=0)
        tr_iir_kan = iir_kan.time_response(tr_sin)
        tr_iir_kan2 = iir_kan.time_response(tr_sin2)
        tr_iir_kan2 = tr_iir_kan2.apply_gain(0.3/0.05)
        tr_sin.plot()
        tr_iir_kan.plot()
        tr_iir_kan2.plot()

    if use_spline:
        # 定义输入的特征数和批次大小
        in_size = 3
        batch_size = 50

        # 构造输入数据，每个特征通道均从 0 到 1 均匀分布
        inputs = tf.linspace(X.min(), X.max(), batch_size)
        # 形状为 (batch_size, in_size)
        inputs = tf.stack([inputs] * in_size, axis=1)

        # 计算样条输出
        spline_out = iir_kan.kan.layers[-1].calc_spline_output(
            inputs)  # 假设输出形状为 (batch_size, in_size, out_size)

        # 绘制每个特征的输入和对应的输出曲线
        plt.figure(figsize=(12, 8))
        for i in range(in_size):
            # 获取形状为 (batch_size, out_size) 的当前特征的输出
            feature_output = spline_out[:, i, :]

            plt.plot(inputs[:, i].numpy(), feature_output[:, 0].numpy(),
                     marker='o', linestyle='-', label=f"Feature {i+1}")
            plt.xlabel(f"Feature {i+1} Input Value (0 to 1)")
            plt.ylabel("Spline Output")
            plt.legend()
            plt.title(f"Spline Output Curves for Feature {i+1}")

        # 计算并绘制斜率（导数）
        plt.figure(figsize=(12, 8))
        for i in range(in_size):
            # 获取当前特征的输出
            feature_output = spline_out[:, i, 0].numpy()  # 取第一个输出通道

            # 计算斜率（近似导数）
            slopes = np.diff(feature_output) / np.diff(inputs[:, i].numpy())
            input_midpoints = (inputs[:-1, i] + inputs[1:, i]) / 2  # 用于绘制斜率的中点

            # 绘制斜率曲线
            plt.plot(input_midpoints.numpy(), slopes, marker='o',
                     linestyle='-', label=f"Feature {i+1} Slope")
            plt.xlabel(f"Feature {i+1} Input Value (0 to 1)")
            plt.ylabel("Slope (Derivative)")
            plt.legend()
            plt.title(f"Slope of Spline Output Curves for Feature {i+1}")

    if USE_FR:
        kan_fr_A1 = iir_kan.frequency_response_system(
            time_length=10, f_range=(5, 200), points=20, amplitude=1)

        kan_fr_A2 = iir_kan.frequency_response_system(
            time_length=10, f_range=(5, 200), points=20, amplitude=50)

        kan_fr_A3 = iir_kan.frequency_response_system(
            time_length=10, f_range=(5, 200), points=20, amplitude=100)

        kan_fr_A4 = iir_kan.frequency_response_system(
            time_length=10, f_range=(5, 200), points=20, amplitude=200)

        ws.plot(markersize=0)
        ws2.plot(markersize=0)

        kan_fr_A1.plot(label=f'A=1')
        kan_fr_A2.plot(label=f'A=50')
        kan_fr_A3.plot(label=f'A=100')
        kan_fr_A4.plot(label=f'A=200')

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    IIR_KAN_base()
