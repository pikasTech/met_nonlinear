# 误差分析功能说明

## 功能概述

`python cli.py -a PROJECT_NAME [--bias-method METHOD] [--bias-params JSON]` 用于消费 `data/inference/` 下已有的推理产物，计算逐层误差并生成偏置分析摘要。当前长期签收口径以 `projects/<PROJECT_NAME>/data/inference/error_analysis.json` 为准。

## 前置条件

- `-a` 不会自己补做推理；执行前必须先有 `python cli.py -i PROJECT_NAME` 生成的 `data/inference/`。
- 若 `data/inference/error_analysis.json` 已存在，默认不会覆盖；需要重算时使用 `python cli.py -a -f PROJECT_NAME`。
- 如果 `nn_layers/` 或 `spice_layers/` 缺失，会直接报错并要求先跑 `-i`。

## 偏置分析方法

### 自动模式

```bash
python cli.py -a projects/WNET5q1h2u6l3 --bias-method auto
```

自动选择偏置分析器，是默认入口。

### 稳态分析

```bash
python cli.py -a projects/WNET5q1h2u6l3 --bias-method steady_state
```

通过信号末尾稳态段估计通道偏置，适合明显存在稳态区的输出。

### 频域分析

```bash
python cli.py -a projects/WNET5q1h2u6l3 --bias-method frequency_domain
```

通过 DC/低频分量提取偏置，更适合稳态段不明显或低频漂移更重要的场景。

### 自定义参数

```bash
python cli.py -a projects/WNET5q1h2u6l3 --bias-params '{"threshold": 0.5, "window_size": 100}'
```

`--bias-params` 会传给当前偏置分析器；应只传该方法实际支持的参数。

## 主产物目录

误差分析默认在 `projects/<PROJECT_NAME>/data/inference/` 下读写，长期可依赖的主产物包括：

| 路径 | 说明 |
|------|------|
| `error_analysis.json` | 主分析结果 JSON |
| `nn_spice_error_layers/*.wave` | NN 与 SPICE 逐层误差 wave |
| `nn_numpy_error_layers/*.wave` | NN 与 NumPy 逐层误差 wave；只有 NumPy 推理存在时才生成 |

`-a` 还会通过 `ReportGenerator` 在控制台输出摘要，但长期机器可读签收仍以 `error_analysis.json` 为准。

## `error_analysis.json` 长期结构

### 顶层结构

当前长期可依赖的顶层键包括：

- `project_name`
- `timestamp`
- `comparison_summary`
- `nn_spice_analysis`
- `nn_numpy_analysis`（可选）
- `bias_analysis`（默认启用）

其中 `comparison_summary` 至少会记录：

- `has_numpy`
- `comparison_types`

### 逐层误差结构

`nn_spice_analysis.layer_analysis[*]` 与 `nn_numpy_analysis.layer_analysis[*]` 的长期字段包括：

- `layer_index`
- `mean_error`
- `std_error`
- `rms_error`
- `max_error`
- `num_samples`
- `ref_records`
- `comp_records`
- `error_wave_path`

配套的 `validation_info` 会记录本次比较看到的层数和模型类型，例如：

- `nn_layers`
- `spice_layers` 或 `numpy_layers`
- `model_type`
- `validation_passed`

### 偏置分析结构

`bias_analysis` 当前长期结构包括：

- `method`
- `parameters`
- `analysis_timestamp`
- `nn_spice_bias`
- `nn_numpy_bias`（可选）
- `nn_spice_matrix_formatted`
- `nn_numpy_matrix_formatted`（可选）
- `summary`

其中 `nn_spice_bias` / `nn_numpy_bias` 的长期字段包括：

- `layer_count`
- `layer_results`
- `layer_statistics`
- `bias_error_matrix`
- `global_statistics`
- `worst_case`
- `validation_info`
- `method_info`

`global_statistics` 当前应读取：

- `mean_bias_error`
- `std_bias_error`
- `max_bias_error`
- `total_channels`
- `max_channels_per_layer`
- `min_channels_per_layer`

`nn_spice_matrix_formatted` / `nn_numpy_matrix_formatted` 是面向展示的格式化结果，长期字段包括：

- `matrix`
- `layer_count`
- `channels_per_layer`
- `layer_names`
- `per_layer_stats`
- `overall_stats`

## 当前格式与历史格式的边界

历史过程文档和旧测试里曾出现过以下旧字段：

- `matrix_shape`
- `n_layers`
- `n_channels`
- 旧的顶层 `statistics`

当前长期口径已经切换为：

- `layer_count`
- `channels_per_layer`
- `global_statistics`

因此：

- 读取当前仓库产物时，应优先按新字段解析。
- 只有在回看 `docs/reference/archive/` 或更早的实验记录时，才需要把旧字段当作历史兼容信息理解。
- 新文档、新测试和新工具不要再把旧字段写回正式口径。

## 常见排查

- 找不到 `error_analysis.json`：先确认是否真的执行过 `-a`，而不只是跑了 `-i` 或 `-e`。
- `nn_layers` 与 `spice_layers` 数量不一致：先按“逐层对齐失败”处理，不要继续解释误差数值。
- 只有 `nn_spice_analysis`、没有 `nn_numpy_analysis`：说明本轮推理没有产出 NumPy 层结果，不代表 `-a` 本身失败。
- 偏置矩阵看起来形状不规则：优先读取 `channels_per_layer`，不要再假设所有层通道数完全一致。

## 相关命令

- `python cli.py -i PROJECT_NAME` - 先生成推理产物
- `python cli.py --bias-viz PROJECT_NAME` - 基于推理产物做偏置可视化对比

## 相关文档

- [inference.md](inference.md)
- [bias_visualization.md](bias_visualization.md)
- [wave_layered_inference.md](wave_layered_inference.md)
- [historical_process_docs.md](historical_process_docs.md)
