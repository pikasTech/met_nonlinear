import matplotlib.pyplot as plt
import numpy as np


def sample_list(lst, size):
    """
    从给定的列表中，根据指定的采样数量返回采样后的列表。
    保证采样列表的首尾元素和原列表的首尾元素一致。
    """
    if size < 1:
        raise ValueError("采样数必须大于等于2（因为要包含首尾元素）。")

    if size == 1:
        # 返回中间的元素
        return [lst[len(lst) // 2]]

    sampled_indices = [0]  # 首元素的索引
    if size > 2:  # 如果采样数量大于2，才需要选择中间的索引
        step = (len(lst) - 1) / (size - 1)  # 计算步长，确保首尾都包含
        for i in range(1, size - 1):  # 中间的索引均匀分布
            index = int(round(i * step))
            sampled_indices.append(index)
    sampled_indices.append(len(lst) - 1)  # 末元素的索引

    # 返回采样后的列表（可以根据需求修改，这里是返回索引对应的原列表元素）
    return [lst[i] for i in sampled_indices]


def plot_sampling_indices(lst, sample_sizes):
    # 获取原始列表的索引
    total_indices = np.arange(len(lst))

    plt.figure(figsize=(10, 6))

    # 绘制原始列表索引
    plt.plot(total_indices, np.ones_like(total_indices),
             'bo', label='Original Indices', markersize=5)

    # 针对每种采样大小，绘制采样后的索引
    for size in sample_sizes:
        # 使用独立的采样函数
        sampled_list = sample_list(lst, size)
        # 根据采样后的列表反推索引（如果需要显示索引）
        sampled_indices = [lst.index(val) for val in sampled_list]

        # 绘制当前采样的索引
        plt.plot(sampled_indices, np.ones_like(sampled_indices) *
                 size, 'x', label=f'Sample size {size}', markersize=8)

    plt.title("Comparison of Sampling Indices (Including First and Last Elements)")
    plt.xlabel("Original Indices")
    plt.ylabel("Sample Sizes")
    plt.yticks(sample_sizes)
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    # 示例数据
    lst = [i for i in range(1, 21)]  # 一个包含20个元素的列表
    sample_sizes = [2, 4, 6, 8, 10, 12, 16]  # 不同的采样大小

    plot_sampling_indices(lst, sample_sizes)
