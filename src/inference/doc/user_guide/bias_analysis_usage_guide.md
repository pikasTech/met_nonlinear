# 偏置误差分析使用指南

## 概述

偏置误差分析功能为 `cli.py -a` 命令提供了通道级的DC偏置误差分析能力。该功能可以：

- 分析每个通道的偏置误差
- 生成层数×通道数的偏置误差矩阵
- 支持多种偏置计算方法
- 将结果保存到JSON文件中

## 基本用法

### 1. 使用默认设置（自动选择方法）

```bash
python cli.py -a PROJECT_NAME
```

这将使用自动方法选择器，根据信号特性选择最合适的偏置计算方法。

### 2. 指定稳态段提取法

```bash
python cli.py -a PROJECT_NAME --bias-method steady_state
```

稳态段提取法适用于：
- 带有明显瞬态响应的信号
- 阶跃响应分析
- 系统稳定性验证

### 3. 指定频域滤波法

```bash
python cli.py -a PROJECT_NAME --bias-method frequency_domain
```

频域滤波法适用于：
- 包含多种频率成分的复杂信号
- 需要高精度偏置估计的场合
- 同时需要频谱分析的应用

### 4. 使用自定义参数

```bash
# 稳态段提取法，使用信号后40%作为稳态段
python cli.py -a PROJECT_NAME --bias-method steady_state --bias-params '{"steady_ratio": 0.4}'

# 频域滤波法，设置DC带宽为2Hz
python cli.py -a PROJECT_NAME --bias-method frequency_domain --bias-params '{"dc_bandwidth": 2.0}'
```

## 参数说明

### --bias-method

可选值：
- `auto`: 自动选择最佳方法（默认）
- `steady_state`: 稳态段提取法
- `frequency_domain`: 频域滤波法

### --bias-params

JSON格式的参数字典，不同方法支持的参数：

#### 稳态段提取法参数：
- `steady_ratio`: 用于计算偏置的信号末尾部分比例（0-1），默认0.3
- `stability_threshold`: 稳定性阈值，std/mean的比值，默认0.1

#### 频域滤波法参数：
- `dc_bandwidth`: DC分量的带宽（Hz），默认1.0
- `window`: 窗函数类型（'hann', 'hamming', 'blackman', None），默认'hann'

## 输出解读

### 终端输出示例

```
🎯 偏置误差分析:
  分析方法: frequency_domain
  参数: {'dc_bandwidth': 1.0, 'window': 'hann'}

  📊 NN-SPICE 偏置误差:
    矩阵形状: 5层 × 10通道
    每层平均偏置:
      层1: 0.001234
      层2: 0.002345
      层3: 0.003456
      层4: 0.004567
      层5: 0.005678
    最大偏置误差: 层3, 通道5, 误差=0.012345
    总体统计:
      平均偏置误差: 0.003456
      标准差: 0.001234
      最大绝对误差: 0.012345
      RMS误差: 0.004567
```

### JSON输出结构

分析结果保存在 `data/inference/error_analysis.json` 中：

```json
{
  "bias_analysis": {
    "method": "frequency_domain",
    "parameters": {
      "dc_bandwidth": 1.0,
      "window": "hann"
    },
    "nn_spice_bias": {
      "layer_results": [...],
      "bias_error_matrix": [
        [0.001, -0.002, ...],  // 层1
        [0.003, -0.001, ...],  // 层2
        ...
      ],
      "statistics": {
        "per_layer_mean_bias": [0.001, 0.002, ...],
        "per_channel_mean_bias": [0.002, -0.001, ...],
        "overall_mean_bias": 0.0015,
        "worst_case": {
          "layer": 3,
          "channel": 5,
          "bias_error": 0.012
        }
      }
    }
  }
}
```

## 使用建议

1. **初次分析**：建议使用 `auto` 方法，让系统自动选择最合适的分析方法

2. **精确分析**：如果需要高精度的偏置估计，使用 `frequency_domain` 方法

3. **快速分析**：如果信号有明显的稳态段，使用 `steady_state` 方法可以获得更快的分析速度

4. **参数调优**：
   - 如果稳态段方法报告"可能包含振荡成分"，尝试增加 `steady_ratio`
   - 如果频域方法的结果不稳定，尝试调整 `dc_bandwidth`

## 常见问题

### Q: 偏置分析失败，提示"数据形状不一致"
A: 确保神经网络和SPICE/NumPy推理输出的通道数一致。检查模型配置是否正确。

### Q: 如何禁用偏置分析？
A: 目前偏置分析默认启用。如果需要禁用，可以在项目的 config.json 中设置：
```json
{
  "enable_bias_analysis": false
}
```

### Q: 偏置误差值很大，是否正常？
A: 偏置误差的可接受范围取决于具体应用。一般来说：
- 相对误差 < 1%：优秀
- 相对误差 < 5%：良好
- 相对误差 > 10%：需要检查模型或仿真配置

## 进阶功能

### 批量分析

分析多个项目的偏置误差：

```bash
# 分析所有项目
python cli.py -a -all --bias-method frequency_domain

# 分析匹配模式的项目
python cli.py -a "FRIKAN*" --bias-method auto
```

### 结果后处理

可以使用Python脚本读取JSON结果进行进一步分析：

```python
import json
import numpy as np

# 读取分析结果
with open('projects/PROJECT_NAME/data/inference/error_analysis.json', 'r') as f:
    results = json.load(f)

# 提取偏置误差矩阵
bias_matrix = np.array(results['bias_analysis']['nn_spice_bias']['bias_error_matrix'])

# 绘制热力图
import matplotlib.pyplot as plt
plt.imshow(bias_matrix, aspect='auto', cmap='RdBu_r')
plt.colorbar(label='Bias Error')
plt.xlabel('Channel')
plt.ylabel('Layer')
plt.title('Bias Error Matrix')
plt.show()
```

## 更新日志

- 2025-07-11: 初始版本发布
  - 实现稳态段提取法和频域滤波法
  - 支持多层网络的偏置误差矩阵分析
  - 集成到 `cli.py -a` 命令