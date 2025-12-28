# R21 子图1和子图4配色刻度统一报告

## 问题描述

R20 指出子图1（原始权重矩阵）和子图4（带E96量化误差的权重）需要使用相同的配色和刻度，使其在视觉上具有可比性。

## 问题分析

修改前代码状态：
- **子图1**: 使用 `cmap='RdBu_r'`，无明确的 `vmin/vmax`
- **子图4**: 使用 `cmap='viridis'`，无明确的 `vmin/vmax`

这导致两个问题：
1. 不同的配色方案（colormap）使得视觉对比困难
2. 刻度范围不同，无法直接比较数值差异

## 修改内容

**文件**: `inference/tools/visualization/weight_e96_quantization_plotter.py`

**修改位置**: `_plot_five_panel_heatmap` 方法（约第478-501行和第575-578行）

### 修改1: 子图1 - 计算统一刻度范围

```python
# 计算统一的颜色范围（用于子图1和子图4的可比性）
all_weights = np.concatenate([weight_matrix.flatten(), weight_e96_matrix.flatten()])
valid_weights = all_weights[(all_weights > 0) & (all_weights < 1e8)]
if len(valid_weights) > 0:
    vmin = float(np.min(valid_weights))
    vmax = float(np.max(valid_weights))
else:
    vmin = float(np.min(weight_matrix))
    vmax = float(np.max(weight_matrix))
# 使用相同的colormap和刻度范围，使子图1和子图4可比
im1 = ax1.imshow(weight_matrix, cmap='RdBu_r', aspect='auto', vmin=vmin, vmax=vmax)
```

### 修改2: 子图4 - 使用相同的colormap和刻度

```python
# 使用与子图1相同的colormap和刻度范围，确保视觉可比性
im4 = ax4.imshow(weight_e96_matrix, cmap='RdBu_r', aspect='auto', vmin=vmin, vmax=vmax)
```

## 修改效果

| 特性 | 修改前 | 修改后 |
|------|--------|--------|
| 子图1 colormap | `RdBu_r` | `RdBu_r` |
| 子图4 colormap | `viridis` | `RdBu_r` |
| 子图1 vmin/vmax | 自动 | 统一计算 |
| 子图4 vmin/vmax | 自动 | 与子图1相同 |
| 视觉可比性 | 无 | 有 |

## 验证方法

运行以下命令生成可视化图表，确认子图1和子图4具有相同的颜色条刻度：

```bash
python -m inference.tools.visualization.weight_e96_quantization_plotter --input ex_projects/inference/wnet5-circuit-validation/WNET5q1h2u6l3_layer1/data/results.json --output ex_projects/inference/wnet5-circuit-validation/WNET5q1h2u6l3_layer1/data/plots/e96_quantization
```

## 实际验证结果

![e96_table_heatmap.png](../../../../ex_projects/inference/wnet5-circuit-validation/WNET5q1h2u6l3_layer1/data/plots/e96_quantization/e96_table_heatmap.png)

**验证结论**：
- ✅ 子图1 (1. Original Weight Matrix): `RdBu_r` colormap, 刻度 0-0.25
- ✅ 子图4 (4. Weight with E96 Quantization Error): `RdBu_r` colormap, 刻度 0-0.25
- ✅ 两个子图使用完全相同的颜色条，**可以直接视觉对比**

## 结论

✅ 子图1和子图4现在使用相同的配色方案（`RdBu_r`）和刻度范围（`vmin=0, vmax=0.25`），便于视觉对比 E96 量化前后的权重变化。

修改完成！报告已生成。
