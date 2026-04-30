# Paper Figure Fine-Grained Adjusters

本文档记录为论文图添加 Figure Studio 精细调整能力的模式与约定。当需要在 `ex_projects/plot/**/config.json` 中暴露更多绘图参数供 Figure Studio UI 调节时，遵循本规范。

## 背景

Figure Studio 的 `FigureConfigInspector` 组件自动将 `config.json` 中的字段渲染为可编辑控件。默认行为：
- `figsize: [w, h]` 会被渲染为两个编号输入框（序号 1、2），体验不佳。
- 嵌套对象（如 `legend`、`xy_plot`、`margins`）有专门的控件分组。
- 数字数组（tuple）默认用序号作标签。

精细调整能力通过以下方式实现：
1. 在 `config.json` 的 `figure_config` 中声明可调参数及其默认值。
2. 在 `docs/paper/src/paper_pipeline.py` 的绘图函数中，从 `cfg` 字典读取参数并作为函数参数传递。
3. 前端 `FigureConfigInspector.tsx` 对 `figsize` 有特殊处理，渲染为 "Width" / "Height" 而非序号。

## figsize 的特殊处理

`FigureConfigInspector.tsx` 对 `figsize` 有特殊渲染逻辑：**抽取为独立字段，标注为 "Figure Size (Width / Height)"**。

因此：
- 在任何面板配置（如 `reduction_panel`、`export_panel`、`validate_panel`）中声明 `figsize: [w, h]`，Figure Studio 会自动以宽/高两个输入框呈现。
- 传递方式：在 `paper_pipeline.py` 中通过 `figsize=_as_float_tuple(export_cfg.get('figsize'), (7.15, 3.9))` 读取。

## 嵌套图标位置的精细调整模式

对于示意图中图标的位置和尺寸（如 `icon_wave_reference`、`icon_qemu`），采用**嵌套对象配置**模式：

### config.json 中的坐标约定

**所有图标/卡片位置配置中，`x` 和 `y` 是中心点坐标**，不是左下角。`w` 和 `h` 是宽和高。

`center_to_bottom_left` 转换函数（已在 `paper_pipeline.py` 中定义）：

```python
def center_to_bottom_left(cx: float, cy: float, w: float, h: float) -> tuple[float, float]:
    return cx - w / 2, cy - h / 2
```

因此调整 `w` 或 `h` 时，图保持中心不动，不会"飘"。

### config.json 示例

```json
{
  "validate_panel": {
    "figsize": [7.15, 4.25],
    "icon_wave_reference": { "x": 0.07, "y": 0.45, "w": 0.18, "h": 0.20 },
    "icon_qemu": { "x": 0.41, "y": 0.67, "w": 0.19, "h": 0.17 },
    "icon_metric_card_qemu": { "x": 0.78, "y": 0.67, "w": 0.15, "h": 0.15 },
    "icon_metric_card_keil": { "x": 0.78, "y": 0.24, "w": 0.15, "h": 0.18 }
  }
}
```

### paper_pipeline.py 读取模式

```python
icon_wave_ref = validate_cfg.get('icon_wave_reference', {})
icon_wave_reference(ax_validate,
    float(icon_wave_ref.get('x', 0.07)),
    float(icon_wave_ref.get('y', 0.45)),
    float(icon_wave_ref.get('w', 0.18)),
    float(icon_wave_ref.get('h', 0.20)))
```

每个字段都有默认值保底，与原始硬编码值一致。

## 卡片字体大小的精细调整模式

每个 `draw_card` 调用的 `title_size` 和 `body_size` 应从配置读取。不同卡片有不同默认值时，使用各自的配置键：

```python
# 每个卡片独立的配置键
draw_card(ax, ..., title_size=float(export_cfg.get('card_title_size', 9.5)), body_size=float(export_cfg.get('card_body_size', 7.5)))
draw_card(ax, ..., title_size=float(export_cfg.get('embedded_card_title_size', 9.3)), body_size=float(export_cfg.get('embedded_card_body_size', 7.1)))
draw_card(ax, ..., title_size=float(export_cfg.get('metric_title_size', 9.4)), body_size=7.0)
```

## 箭头线宽的精细调整模式

`routed_arrow` 的 `lw` 参数统一从 panel cfg 读取：

```python
export_arrow_lw = float(export_cfg.get('arrow_lw', 1.9))
routed_arrow(ax_export, ..., lw=export_arrow_lw, ...)
routed_arrow(ax_export, ..., lw=export_arrow_lw, ...)
```

## 边缘留白的两阶段控制模式

对于示意图中需要精确控制四边留白的场景，采用 **两阶段处理**：
- **`pad_inches`**：在 `bbox_inches='tight'` 计算内容边界之前加到四边，确保内容元素（如最右侧箭头）不被截断
- **`margin_left/right/top/bottom`**：在 tight 之后裁剪，控制最终输出四边的净留白

### 处理流程

```
matplotlib tight bbox 计算
        ↓ (pad_inches 加在 tight 之前，内容边界扩大)
内容边界（含 pad）
        ↓
PIL 裁剪（margin 从各边裁掉多余部分）
        ↓
最终输出（含独立控制的上/下/左/右留白）
```

### 实际效果

| pad_inches | margin_right | 净右侧留白 | 其他三边 |
|------------|-------------|-----------|---------|
| 0.1 | 0.0 | 0.1" | 0.1" |
| 0.1 | 0.2 | 0.1" | 0.1" |
| 0.0 | 0.0 | 0 | 0 |
| 0.0 | 0.2 | 右侧压缩 | 0 |

**注意**：`pad_inches` 为 0 时内容贴边；需确保内容边界在画布范围内。`output_scalar` 等元素的 x+w/2 不应超过 1.0，否则 `bbox_inches='tight'` 会导致元素被截断。

### paper_pipeline.py 实现（save_panel_figure）

```python
def save_panel_figure(
    fig, name, *,
    dpi=300,
    pad_inches=0.0,
    margin_left=0.0, margin_right=0.0, margin_top=0.0, margin_bottom=0.0,
    raw_payload=None,
) -> str:
    # pad_inches 在 tight 之前生效（扩展内容边界）
    # margin 在之后裁剪（精确控制四边留白）
    _save_matplotlib_figure(fig, out, ..., bbox_inches='tight', pad_inches=pad_inches)
    # PIL crop...
```

### config.json 示例

```json
{
  "runtime_panel": {
    "pad_inches": 0.1,
    "margin_left": 0,
    "margin_right": 0.2,
    "margin_top": 0,
    "margin_bottom": 0
  }
}
```

## FigureConfigInspector 的 figsize 识别逻辑

`FigureConfigInspector.tsx` 中，`figsize` 通过以下逻辑被识别并特殊渲染：

```typescript
const figsizeEntry = tupleEntries.find(([key]) => key === 'figsize');
// figsizeEntry 单独用 NumberTupleField 渲染，itemLabels=['Width', 'Height']
// genericTupleEntries 走默认渲染，用序号作标签
```

因此只要配置中字段名为 `figsize`（不论在哪个嵌套层级），都会被自动识别并以 Width/Height 呈现。

## 添加新面板精细调整的检查清单

1. 在 `config.json` 的 `figure_config` 下为该面板添加 `{}`，放入所有可调参数，默认值与原始硬编码一致。
2. 在 `paper_pipeline.py` 的绘图函数中，用 `cfg.get('panel_name') or {}` 获取面板配置，用 `.get('key', default)` 读取每个参数。
3. 如果新增了嵌套对象字段（如 `icon_xxx`），确认 Figure Studio 中渲染为分组展开形式（每个子键 X/Y/W/H 独立输入框）。
4. 如果新增了标量数字字段（如 `card_title_size`、`arrow_lw`），前端自动以 NumberField 呈现。
5. 如果需要控制边缘留白：使用 `pad_inches` + `margin_left/right/top/bottom` 组合，在 `save_panel_figure` 调用时传入对应 panel cfg 的参数。
6. 重建 webui：`cd src/webui && npm run build`。
7. 在 Figure Studio 中选择对应 figure，展开 `figure_config` 验证控件存在且默认值正确。

## 嵌套 montage 子项目管理模式

当 montage 的某个 panel 本身是多个子图的组合时（如 fig_22 的 response row），需要将其建模为独立的子项目（而非仅是 paper_pipeline.py 中的中间 bitmap），这样 Figure Studio 能识别全部子图。

### 模式

```
fig_22_parallel_wiener_equivalent_montage (multi/montage)
├── fig_22_parallel_wiener_equivalent_montage_a_principle (single/legacy_panel)
├── fig_22_parallel_wiener_response_row_b (single/copy_source)
└── fig_22_parallel_wiener_response_row_c (single/copy_source)
```

**注意：不要嵌套拼图（即不要在 montage 中再嵌入一层 montage 作为子项目）。嵌套拼图会导致子图号（如 (a)(b)(c)）的字号不一致，也会增加配置复杂度。所有 leaf 子图应直接在顶层 montage 的 `subfigures` 中平铺声明。**

### config.json 约定

- 如果子项目 bitmap 直接来自已有文件，用 `copy_source`
- 如果子项目需要从 paper_pipeline.py 生成，用 `legacy_panel` + `legacy_render_id`
- 子项目的 `parent_montages` 包含直接父级 montage ID
- **layout 必须设为 `"matrix"`** 才能支持多行多列 grid 布局；`"vertical"` 会强制 col_count=1 导致无法放置跨列 panel

## 已应用精细调整的 figure 一览

| Figure | 面板 | 可调参数 |
|--------|------|---------|
| `fig_08_frequency_response_comparison_c_drift_reduction` | `reduction_panel` | `figsize`, `legend_loc`, `legend_frameon`, `legend_fontsize`, `annotation_fontsize` |
| `fig_17_board_inference_validation_workflow_a_export` | `export_panel` | `figsize`, `card_title_size`, `card_body_size`, `embedded_card_title_size`, `embedded_card_body_size`, `c_export_card_body_size`, `arrow_lw`, `icon_neural_project`, `icon_c_package`, `icon_chip` |
| `fig_17_board_inference_validation_workflow_b_validate` | `validate_panel` | `figsize`, `card_title_size`, `card_body_size`, `metric_title_size`, `metric_body_size`, `test_title_size`, `test_body_size`, `arrow_lw`, `icon_wave_reference`, `icon_qemu`, `icon_uart_metrics`, `icon_metric_card_qemu`, `icon_metric_card_keil` |
| `fig_15_lut_lookup_principles_a_offline` | `offline_panel` | `figsize`, `box_font_size`, `arrow_lw`, `curve_text_fontsize`, `pad_inches`, `margin_left/right/top/bottom`, `lut_table` (x/y/w/h + 表头Q位置X, 表头V位置X, 表头位置Y, 行列Q位置X, 行列V位置X, 首行位置Y, 行间距, 行列字号, 表头字号, 横线边距, 横线线宽, 标签字号, 标签偏移Y), `flash_chip` (x/y/w/h) |
| `fig_15_lut_lookup_principles_b_runtime` | `runtime_panel` | `figsize`, `box_font_size`, `input_box_size`, `arrow_lw`, `pad_inches`, `margin_left/right/top/bottom`, `input_scalar` (x/y/w/h), `address_mapping` (x/y/w/h), `nearest_lookup` (x/y/w/h), `linear_interp` (x/y/w/h), `output_scalar` (x/y/w/h) |
| `fig_22_parallel_wiener_equivalent_montage` | `montage` | `layout` (用 `"matrix"` 支持多行多列), `rows`, `cols`, `padding` (L/T/R/B), `gutter`, `label_font_size`, `label_position`, `label_gap`, `panels[*].fit_width`, `panels[*].fit_height`, `panels[*].fit_mode` (`width`/`height`/`both`), `panels[*].row_span`, `panels[*].col_span`, `panels[*].align_x/align_y`, `panels[*].trim_border`, `panels[*].margin_left/right/top/bottom` |
| `fig_22_parallel_wiener_equivalent_montage_a_principle` | `principle_panel` | `figsize`, `pad_inches`, `input_text`, `input_x`, `output_text`, `output_x`, `label_fontsize`, `subtitle_fontsize`, `input_arrow_lw`, `branch_arrow_lw`, `h_to_f_arrow_lw`, `f_to_sum_arrow_lw` |
| `fig_22_parallel_wiener_response_row_b` | `copy_source` | 无精细调整（直接复制现有 bitmap） |
| `fig_22_parallel_wiener_response_row_c` | `copy_source` | 无精细调整（直接复制现有 bitmap） |