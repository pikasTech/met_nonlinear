import tensorflow as tf


def log_division_loss(y_true, y_pred):
    # 确保 y_true 和 y_pred 不为零，避免对数取零的问题
    y_true = tf.where(y_true == 0, tf.keras.backend.epsilon(), y_true)
    y_pred = tf.where(y_pred == 0, tf.keras.backend.epsilon(), y_pred)

    # 检查 y_true 和 y_pred 的符号是否一致
    signs_match = tf.math.equal(tf.sign(y_true), tf.sign(y_pred))

    # 取 y_true 和 y_pred 的绝对值
    abs_y_true = tf.abs(y_true)
    abs_y_pred = tf.abs(y_pred)

    # 计算绝对值后取对数
    log_y_true = tf.math.log(abs_y_true)
    log_y_pred = tf.math.log(abs_y_pred)

    # 计算 log(y_true) 和 log(y_pred) 的差
    log_diff = log_y_true - log_y_pred

    # 使用绝对误差或均方误差
    # 或者使用均方误差
    loss = tf.reduce_mean(tf.abs(log_diff))  # 绝对误差
    # loss = tf.reduce_mean(tf.square(log_diff))

    # 如果符号不一致，则将损失设为 0
    loss = tf.where(signs_match, loss, 0.0)

    return loss


def power_mae_loss(y_true, y_pred, use_balence=False, use_log=True):
    # 将 y_true 和 y_pred 分别计算能量
    power_true = tf.reduce_sum(tf.abs(y_true))
    power_pred = tf.reduce_sum(tf.abs(y_pred))
    if use_log:
        # 对能量取对数，确保偏高和偏低的能量损失对称
        power_true = tf.math.log(power_true)
        power_pred = tf.math.log(power_pred)
    # 计算能量的均方误差
    loss = tf.abs(power_true - power_pred)
    if not use_log and use_balence:
        # 根据 power_true 的大小进行归一化
        # 对数不需要归一化，因为本身对数包含了相除的操作
        loss = loss / power_true

    return loss


def power_log_mae_loss(
    y_true,
    y_pred,
    k=0.2,
    use_balence=True,
    group_points=4000,
    use_debug=False
):
    """
    在计算 power 时，以 group_points 为单位，先计算出能量
    shape: (batch_size, group_num = seq_num / group_points, feature_num)，
    再对 group_num 进行平均。然后进行对数、求差、再平均。
    MAE 部分保留原先逻辑。如果也想按分组来做 MAE，可以同理修改。
    """

    # ============ 1) 以 group_points 为单位拆分序列 ============
    # 假设 seq_num 能被 group_points 整除
    if len(y_true.shape) == 2:
        # shape: (batch_size * group_points, feature_num) -> (batch_size, group_points, feature_num)
        if use_debug:
            tf.print("y_true.shape:", y_true.shape)
        y_true = tf.reshape(y_true, [-1, group_points, y_true.shape[-1]])
        y_pred = tf.reshape(y_pred, [-1, group_points, y_pred.shape[-1]])
        if use_debug:
            tf.print("reshaped y_true.shape:", y_true.shape)

    if use_debug:
        # 添加数值检查，帮助调试
        tf.debugging.check_numerics(y_true, "y_true contains NaN or Inf")
        tf.debugging.check_numerics(y_pred, "y_pred contains NaN or Inf")
        tf.print("batch_size:", y_true.shape[0])
        tf.print("seq_num:", y_true.shape[1])
        tf.print("feature_num:", y_true.shape[2])

    # 计算能量
    power_true = tf.reduce_sum(tf.abs(y_true), axis=1)
    power_pred = tf.reduce_sum(tf.abs(y_pred), axis=1)

    if use_debug:
        tf.print("power_true range:", tf.reduce_min(
            power_true), tf.reduce_max(power_true))
        tf.print("power_pred range:", tf.reduce_min(
            power_pred), tf.reduce_max(power_pred))

    # 对能量取对数，添加小常数避免对零取对数
    power_true_log = tf.math.log(power_true + 1e-8)
    power_pred_log = tf.math.log(power_pred + 1e-8)

    # 计算能量对数的绝对误差
    loss_power_log = tf.abs(power_true_log - power_pred_log)

    # MAE计算
    loss_mae = tf.reduce_mean(tf.abs(y_true - y_pred), axis=1)

    if use_balence:
        # 添加安全除法，避免除以零
        power_true_safe = tf.maximum(power_true, 1e-8)
        loss_mae = loss_mae / power_true_safe * 350

        if use_debug:
            tf.print("loss_mae after balance:", tf.reduce_min(
                loss_mae), tf.reduce_max(loss_mae))

    # 最后加和平均得到最终损失
    loss_power_log_avr = tf.reduce_mean(loss_power_log)
    loss_mae_avr = tf.reduce_mean(loss_mae)

    return k * loss_power_log_avr + (1 - k) * loss_mae_avr


def pure_power_log_mae_loss(y_true, y_pred, group_points=4000, use_debug=False):
    """
    仅包含 Power Log MAE 的损失函数，不包含标准 MAE 部分。
    用于只关注能量对数误差的场景。
    """
    if len(y_true.shape) == 2:
        y_true = tf.reshape(y_true, [-1, group_points, y_true.shape[-1]])
        y_pred = tf.reshape(y_pred, [-1, group_points, y_pred.shape[-1]])

    power_true = tf.reduce_sum(tf.abs(y_true), axis=1)
    power_pred = tf.reduce_sum(tf.abs(y_pred), axis=1)

    power_true_log = tf.math.log(power_true + 1e-8)
    power_pred_log = tf.math.log(power_pred + 1e-8)

    loss_power_log = tf.abs(power_true_log - power_pred_log)
    return tf.reduce_mean(loss_power_log)


def power_log_loss(y_true, y_pred, group_points=4000, use_debug=False):
    # ============ 1) 以 group_points 为单位拆分序列 ============
    # 假设 seq_num 能被 group_points 整除
    if len(y_true.shape) == 2:
        # shape: (batch_size * group_points, feature_num) -> (batch_size, group_points, feature_num)
        if use_debug:
            pass
            # tf.print("y_true.shape:", y_true.shape)
        y_true = tf.reshape(y_true, [-1, group_points, y_true.shape[-1]])
        y_pred = tf.reshape(y_pred, [-1, group_points, y_pred.shape[-1]])
        if use_debug:
            pass
            # tf.print("reshaped y_true.shape:", y_true.shape)
    if use_debug:
        pass
        # tf.print("y_true.shape:", y_true.shape)
        # tf.print("batch_size:", y_true.shape[0])
        # tf.print("seq_num:", y_true.shape[1])
        # tf.print("feature_num:", y_true.shape[2])
    # shape: (batch_size, simple_num, feature_num)
    # 将 y_true 和 y_pred 分别计算能量
    # 计算的能量要以 group_points 为一组，跨 group_points 是错误的
    # 能量 shape: (batch_size, feature_num)
    if use_debug:
        # tf.print("y_true.range:", tf.reduce_min(y_true), tf.reduce_max(y_true))
        # tf.print("y_pred.range:", tf.reduce_min(y_pred), tf.reduce_max(y_pred))
        # hash
        tf.print("y_true.hash:", tf.reduce_sum(y_true))

    power_true = tf.reduce_sum(tf.abs(y_true), axis=1)
    power_pred = tf.reduce_sum(tf.abs(y_pred), axis=1)

    # 对能量取对数，确保偏高和偏低的能量损失对称
    # 对数不需要归一化，因为本身对数包含了相除的操作
    # 能量对数 shape: (batch_size, feature_num)
    power_true_log = tf.math.log(power_true + 1e-8)
    power_pred_log = tf.math.log(power_pred + 1e-8)

    # 计算能量对数的均方误差
    loss_power_log = tf.abs(power_true_log - power_pred_log)

    # 最后加和平均得到最终损失
    loss_power_log_avr = tf.reduce_mean(loss_power_log)

    return loss_power_log_avr


def af_mse_loss(y_true, y_pred, group_points=4000, use_debug=False):
    """幅频损失: 对分组能量对数差使用纯平方误差, 不包含 MAE 项。"""
    if len(y_true.shape) == 2:
        if use_debug:
            tf.print("y_true.shape:", y_true.shape)
        y_true = tf.reshape(y_true, [-1, group_points, y_true.shape[-1]])
        y_pred = tf.reshape(y_pred, [-1, group_points, y_pred.shape[-1]])
        if use_debug:
            tf.print("reshaped y_true.shape:", y_true.shape)

    if use_debug:
        tf.debugging.check_numerics(y_true, "y_true contains NaN or Inf")
        tf.debugging.check_numerics(y_pred, "y_pred contains NaN or Inf")

    power_true = tf.reduce_sum(tf.abs(y_true), axis=1)
    power_pred = tf.reduce_sum(tf.abs(y_pred), axis=1)

    power_true_log = tf.math.log(power_true + 1e-8)
    power_pred_log = tf.math.log(power_pred + 1e-8)

    loss_power_log = tf.square(power_true_log - power_pred_log)
    return tf.reduce_mean(loss_power_log)


def pure_mae_metric(y_true, y_pred):
    """纯MAE指标，用于评估时分离MAE和AFMAE"""
    return tf.reduce_mean(tf.abs(y_true - y_pred))
