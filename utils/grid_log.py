import numpy as np
from matplotlib import pyplot as plt


def generate_mixed_log_linear_points(start, end, points, ratio_log=0.1, ratio_log_points=0.3):
    """
    按照对数和线性区间生成点。

    参数：
    start (float): 区间开始值，必须大于 0。
    end (float): 区间结束值，必须大于 start。
    points (int): 总生成点数。
    ratio_log (float): 对数区间长度比例，默认 0.5。
    ratio_log_points (float): 分配给对数区间的点数比例，默认 0.5。

    返回：
    numpy.ndarray: 生成的点数组。
    """
    if start <= 0 or end <= 0:
        raise ValueError("start 和 end 必须为正数！")
    if start >= end:
        raise ValueError("end 必须大于 start！")
    if not (0 <= ratio_log <= 1):
        raise ValueError("ratio_log 必须在 [0, 1] 范围内！")
    if not (0 <= ratio_log_points <= 1):
        raise ValueError("ratio_log_points 必须在 [0, 1] 范围内！")

    # 计算对数区间和线性区间的范围
    log_range_end = start + (end - start) * ratio_log
    linear_range_start = log_range_end

    # 分配对数区间和线性区间的点数
    log_points_count = int(points * ratio_log_points)
    linear_points_count = points - log_points_count

    # 生成对数区间的点
    log_points = np.logspace(np.log10(start), np.log10(
        log_range_end), log_points_count, endpoint=False)

    # 生成线性区间的点
    linear_points = np.linspace(linear_range_start, end, linear_points_count)

    # 合并结果
    result = np.concatenate([log_points, linear_points])
    return result


if __name__ == "__main__":
    # 示例参数
    start = 0.001       # 区间开始
    end = 1      # 区间结束
    points = 64     # 总点数

    mixed_points = generate_mixed_log_linear_points(
        start, end, points)
    print(mixed_points)
    plt.plot(mixed_points, np.zeros_like(mixed_points), 'o')
    plt.show()
