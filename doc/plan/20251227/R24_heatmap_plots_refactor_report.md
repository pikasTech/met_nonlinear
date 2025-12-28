# R24 热力图重构报告

## 问题描述

R23 的问题依然存在：子图1和4应当使用相同的配色和刻度，子图2和3也应当使用相同的配色和刻度。用户建议提取公共绘图函数来解决这个问题。

## 解决方案

提取公共绘图函数 `_plot_table_heatmap_subplot`，通过配置字典控制不同子图的行为。

## 修改内容

**文件**: `inference/tools/visualization/weight_e96_quantization_plotter.py`

### 新增公共函数: `_plot_table_heatmap_subplot` (第323-399行)

```python
def _plot_table_heatmap_subplot(self, ax, matrix, title, config: dict):
    """
    公共热力图子图绘制函数

    统一处理子图1-4的绘制，根据config配置不同行为：
    - 子图1和4: 权重矩阵，配置 {is_weight=True, value_format='.2f'}
    - 子图2和3: 电阻矩阵，配置 {is_weight=False, value_format='.0f', show_sign=True}

    Args:
        ax: matplotlib axes
        matrix: 2D numpy array
        title: 子图标题
        config: 配置字典，包含:
            - cmap: 颜色映射 (默认 'RdBu_r')
            - vmin, vmax: 颜色范围
            - is_weight: 是否为权重矩阵 (决定是否使用masked array)
            - value_format: 数值格式 (默认 '.2f')
            - show_sign: 是否显示正负符号 (默认 False)
            - sign_prefix: 符号前缀 (默认 '+')
    """
```

### 重构 `_plot_five_panel_heatmap` (第439行起)

使用公共函数统一绘制子图1-4：

```python
# ========== 子图1: 原始权重矩阵 ==========
ax1 = axes[0, 0]
self._plot_table_heatmap_subplot(ax1, weight_matrix, '1. Original Weight Matrix', {
    'cmap': 'RdBu_r',
    'vmin': weight_vmin,
    'vmax': weight_vmax,
    'is_weight': True,
    'value_format': '.2f',
    'show_sign': False,
})

# ========== 子图2: 电阻（浮点数） ==========
ax2 = axes[0, 1]
self._plot_table_heatmap_subplot(ax2, resistor_raw_matrix, '2. Resistor Values (Float)', {
    'cmap': 'RdBu_r',
    'vmin': resistor_vmin,
    'vmax': resistor_vmax,
    'is_weight': False,
    'value_format': '.0f',
    'show_sign': True,
})

# ========== 子图3: 电阻（E96量化） ==========
ax3 = axes[0, 2]
self._plot_table_heatmap_subplot(ax3, resistor_e96_matrix, '3. Resistor Values (E96)', {
    'cmap': 'RdBu_r',
    'vmin': resistor_vmin,
    'vmax': resistor_vmax,
    'is_weight': False,
    'value_format': '.0f',
    'show_sign': True,
})

# ========== 子图4: 计算带E96量化误差的权重 ==========
ax4 = axes[1, 0]
self._plot_table_heatmap_subplot(ax4, weight_e96_matrix, '4. Weight with E96 Quantization Error', {
    'cmap': 'RdBu_r',
    'vmin': weight_vmin,
    'vmax': weight_vmax,
    'is_weight': True,
    'value_format': '.3f',
    'show_sign': False,
})
```

## 配置参数说明

| 参数 | 子图1/4 | 子图2/3 | 说明 |
|------|---------|---------|------|
| `cmap` | `RdBu_r` | `RdBu_r` | 颜色映射 |
| `vmin/vmax` | 统一计算 | 统一计算 | 确保可比性 |
| `is_weight` | `True` | `False` | 是否权重矩阵 |
| `value_format` | `.2f`/`.3f` | `.0f` | 数值格式 |
| `show_sign` | `False` | `True` | 是否显示符号 |

## 验证结果

![e96_table_heatmap.png](e96_table_heatmap.png)

**验证结论**：

1. **子图1和子图4**（权重矩阵）:
   - ✅ 使用相同 colormap (`RdBu_r`)
   - ✅ 使用相同刻度范围 (-2.05 到 1.50)
   - ✅ 颜色条完全一致，便于视觉对比

2. **子图2和子图3**（电阻矩阵）:
   - ✅ 使用相同 colormap (`RdBu_r`)
   - ✅ 使用相同刻度范围 (-51700 到 20750)
   - ✅ 颜色条完全一致，便于视觉对比
   - ✅ 电阻值带有符号 (`+492`, `-815`, `+51700` 等)

3. **子图4**:
   - ✅ 所有36个格子都有数值
   - ✅ 使用3位小数显示，可看到与子图1的细微差异

4. **子图5**:
   - ✅ 显示权重相对误差（子图1 vs 子图4）

## 代码优势

1. **DRY原则**: 避免重复代码，子图1-4的绘制逻辑统一
2. **可配置性**: 通过config字典控制行为，易于扩展
3. **可维护性**: 修改公共函数即可影响所有子图
4. **一致性**: 确保相同类型子图使用相同的colormap和刻度

## 结论

✅ R24 问题已解决：
- 提取了公共绘图函数 `_plot_table_heatmap_subplot`
- 子图1和4使用相同的配色和刻度（通过统一计算vmin/vmax）
- 子图2和3使用相同的配色和刻度（通过统一计算vmin/vmax）
- 配置通过字典传入，易于理解和维护

修改完成！报告已生成。
