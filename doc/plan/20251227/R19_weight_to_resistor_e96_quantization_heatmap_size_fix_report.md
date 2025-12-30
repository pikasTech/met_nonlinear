# R19 热力图尺寸修复报告

## 问题描述

R18 中要求热力图的每个子图应该都是 6x6 的，但修改后发现：
- 子图2（电阻值浮点数）：2行 x 12列，尺寸不正确
- 子图3（E96量化电阻）：2行 x 12列，尺寸不正确

## 问题分析

问题出在 `_plot_five_panel_heatmap` 方法中，原代码将电阻数据构建为2行xN列的矩阵，而不是6x6的矩阵。

原代码逻辑：
```python
# 构建电阻对比矩阵 (2行: raw, e96)
n_show = min(len(raw_resistors), 12)
resistor_matrix = np.zeros((2, n_show))
resistor_matrix[0, :n_show] = raw_resistors[:n_show]
resistor_matrix[1, :n_show] = e96_resistors[:n_show]
```

## 修改方案

修改 `inference/tools/visualization/weight_e96_quantization_plotter.py` 文件中的 `_plot_five_panel_heatmap` 方法：

### 修改1：子图2 - 电阻（浮点数）6x6矩阵（第497-543行）

**修改前**：
- 使用2行x12列的电阻对比矩阵
- 标签显示"Raw (Ω)"和"E96 (Ω)"

**修改后**：
- 构建6x6电阻矩阵 `resistor_raw_matrix`
- 从 `resistor_raw` 字典中解析 `layer_channel_type` 格式的数据
- 使用NaN处理无效值（开路电阻）

### 修改2：子图3 - 电阻（E96量化）6x6矩阵（第545-567行）

**修改前**：
- 使用2行xN列的差异矩阵

**修改后**：
- 构建6x6 E96电阻矩阵 `resistor_e96_matrix`
- 与子图2保持一致的6x6矩阵结构

### 修改3：JSON数据保存格式（第655-666行）

**修改前**：
```python
'raw_resistors': raw_resistors[:12],
'e96_resistors': e96_resistors[:12],
```

**修改后**：
```python
'resistor_raw_matrix': resistor_raw_matrix.tolist(),
'resistor_e96_matrix': resistor_e96_matrix.tolist(),
```

## 验证结果

重新生成图表后，所有5个热力图子图现在都是6x6矩阵：

| 子图 | 内容 | 尺寸 |
|------|------|------|
| 1 | 原始权重矩阵 | 6x6 |
| 2 | 电阻值（浮点数） | 6x6 |
| 3 | 电阻值（E96量化） | 6x6 |
| 4 | 带E96量化误差的权重 | 6x6 |
| 5 | E96相对误差 | 6x6 |
| 6 | 统计表格 | 表格形式 |

## 涉及文件

- `inference/tools/visualization/weight_e96_quantization_plotter.py`
  - 第497-543行：子图2修改
  - 第545-567行：子图3修改
  - 第655-666行：JSON数据保存修改

## 生成的文件

- `ex_projects/inference/wnet5-circuit-validation/WNET5q1h2u6l3_layer1/data/plots/e96_quantization/e96_table_heatmap.png`
- `ex_projects/inference/wnet5-circuit-validation/WNET5q1h2u6l3_layer1/data/plots/raw/e96_quantization/e96_table_heatmap.json`
