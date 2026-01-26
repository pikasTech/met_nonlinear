import re
import sys
from .analyzer import DataAnalyzeResultList
import numpy as np
import matplotlib.pyplot as plt
import math


def parse_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # 正则表达式匹配 TABLE_ITEM 宏
    matches = re.findall(r"TABLE_ITEM\((\d+\.?\d*),\s*(\d+\.?\d*)\)", content)

    # 提取频率和幅度到两个列表
    freq = [float(match[0]) for match in matches]
    amp = [float(match[1]) for match in matches]

    return freq, amp


def gen_file(freq, amp, file_path):
    with open(file_path, 'w') as file:
        for i in range(len(freq)):
            file.write(f"TABLE_ITEM({freq[i]:.6f}, {amp[i]:.6f})\n")


def load_amplitude(file_path):
    dataAnalyzeResultList = DataAnalyzeResultList()
    dataAnalyzeResultList.load_from_json_file(file_path)

    freq = np.array(
        [result.freq for result in dataAnalyzeResultList.dataAnalyzeResults])
    amp = np.array(
        [result.ch1IntegrateResult.main_freq_amplitude for result in dataAnalyzeResultList.dataAnalyzeResults])
    return freq, amp


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <path_to_h_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    freq_input, amp_input = parse_file(file_path)

    freq_output, amp_ouput = load_amplitude(sys.argv[2])

    median_amp_output = np.median(amp_ouput)

    ratio_amp_output = amp_ouput / median_amp_output

    # 调整 input 的幅度，freq_output 和 freq_input 要能对应上（绝对值差10%以内）
    amp_input_adjusted = amp_input.copy()
    for i in range(len(freq_output)):
        freq = freq_output[i]
        ratio_amp = ratio_amp_output[i]
        for j in range(len(freq_input)):
            if abs(math.log10(freq) - math.log10(freq_input[j])) < 0.01:
                amp_input_adjusted[j] /= ratio_amp
                break

    gen_file(freq_input, amp_input_adjusted,
             file_path.replace(".h", "_adjusted.h"))

    # 画图
    plt.loglog(freq_input, amp_input, 'b-', label='Input')
    plt.loglog(freq_input, amp_input_adjusted, 'r-', label='Input_adj')
    plt.loglog(freq_output, amp_ouput, 'g-', label='Output')
    plt.legend()
    plt.show()
