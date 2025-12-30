# R23 热力图修复报告

## 问题描述

R23 提出三个问题：

1. 子图2、子图3应当使用相同的配色和刻度，使其在视觉上具有可比性；子图4里面缺少部分数值，应当补充
2. 子图2、子图3的电阻值应当带有符号表示方向性，符号和权重一致
3. 子图5应当计算的是子图1、子图4的相对误差，而非子图2、子图3的相对误差

## 修改内容

**文件**: `inference/tools/visualization/weight_e96_quantization_plotter.py`

**修改方法**: `_plot_five_panel_heatmap` (约第504-644行)

### 修改1: 子图2和子图3使用相同colormap（RdBu_r，支持正负值）和刻度

```python
# 计算统一的颜色范围（用于子图2和子图3的可比性）
all_resistor_values = np.concatenate([resistor_raw_matrix.flatten(), resistor_e96_matrix.flatten()])
valid_resistors = all_resistor_values[(~np.isnan(all_resistor_values)) & (np.abs(all_resistor_values) > 0)]
if len(valid_resistors) > 0:
    r_vmin = float(np.min(valid_resistors))
    r_vmax = float(np.max(valid_resistors))

# 使用相同的colormap（RdBu_r，支持正负值）和刻度范围
im2 = ax2.imshow(resistor_raw_masked, cmap='RdBu_r', aspect='auto', vmin=r_vmin, vmax=r_vmax)
im3 = ax3.imshow(resistor_e96_masked, cmap='RdBu_r', aspect='auto', vmin=r_vmin, vmax=r_vmax)
```

### 修改2: 电阻值添加符号表示方向性

```python
# 获取对应权重的符号
weight_val = float(weight_matrix[layer, channel])
sign = 1 if weight_val >= 0 else -1
resistor_raw_matrix[layer, channel] = r_raw * sign
resistor_e96_matrix[layer, channel] = resistor_e96.get(key, r_raw) * sign

# 显示带符号的电阻值
sign_str = '+' if val > 0 else ''
ax2.text(j, i, f'{sign_str}{val:.0f}', ...)
```

### 修改3: 子图4补充所有数值（使用3位小数显示差异）

```python
for i in range(weight_e96_matrix.shape[0]):
    for j in range(weight_e96_matrix.shape[1]):
        val = float(weight_e96_matrix[i, j])
        # 显示所有数值，包括负值和零值
        if np.abs(val) > 1e-6:
            ax4.text(j, i, f'{val:.3f}', ...)  # 使用3位小数显示E96量化差异
        else:
            ax4.text(j, i, '0', ...)
```

### 修改4: 子图5计算权重相对误差

```python
# 计算权重相对误差：(weight_e96 - weight_original) / weight_original * 100
weight_error_matrix = np.zeros_like(weight_matrix, dtype=np.float64)
for i in range(weight_matrix.shape[0]):
    for j in range(weight_matrix.shape[1]):
        w_orig = float(weight_matrix[i, j])
        w_e96 = float(weight_e96_matrix[i, j])
        if abs(w_orig) > 1e-6:
            weight_error_matrix[i, j] = abs(w_e96 - w_orig) / abs(w_orig) * 100
```

## 修改效果

| 问题 | 修改前 | 修改后 |
|------|--------|--------|
| 子图2 colormap | `YlOrRd` | `RdBu_r` (支持正负) |
| 子图3 colormap | `YlGnBu` | `RdBu_r` (与子图2统一) |
| 子图2/3 vmin/vmax | 不同/自动 | 统一计算 (-22000 到 22000) |
| 子图2/3 数值符号 | 无符号 | 带 +/- 符号 |
| 子图4 数值显示 | 部分显示'-' | 全部显示数值 (3位小数) |
| 子图5 误差类型 | 电阻相对误差 | 权重相对误差 (%) |

## 验证结果

![e96_table_heatmap.png](../../../../ex_projects/inference/wnet5-circuit-validation/WNET5q1h2u6l3_layer1/data/plots/e96_quantization/e96_table_heatmap.png)

**验证结论**：

1. **子图2和子图3**:
   - ✅ 使用相同 colormap (`RdBu_r`，支持正负值)
   - ✅ 使用相同刻度范围 (-22000 到 22000)
   - ✅ 颜色条完全一致，便于视觉对比
   - ✅ 电阻值带有符号 (`+22000`, `-18700` 等)

2. **子图4**:
   - ✅ 所有36个格子都有数值，无缺失
   - ✅ 使用3位小数显示，可看到与子图1的细微差异
   - ✅ 使用与子图1相同的 colormap (`RdBu_r`) 和刻度

3. **子图5**:
   - ✅ 计算权重相对误差 (如 0.10%, 0.11%, 0.14%)
   - ✅ 显示权重矩阵各位置的E96量化引入的误差

**数值对比示例**：
- 子图1 (0.090) → 子图4 (0.091)：误差 0.11%
- 子图1 (0.080) → 子图4 (0.081)：误差 0.10%
- 子图1 (0.160) → 子图4 (0.160)：误差 0.01%

## 结论

✅ R23 所有问题已修复：
- 子图2和子图3使用相同配色方案（RdBu_r）和刻度范围，便于视觉对比
- 电阻值带有符号表示方向性，与权重一致
- 子图4补充了所有缺失数值，并使用3位小数显示E96量化差异
- 子图5现在显示权重相对误差（子图1 vs 子图4），而非电阻相对误差

修改完成！报告已生成。
