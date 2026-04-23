# 计算量估算说明

## 功能概述

`cli.py -e PROJECT_NAME` 与 `cli.py -m PROJECT_NAME` 会基于 TensorFlow 模型真实结构导出单步推理计算量，并同时给出面向 STM32F405 的加权耗时估算。

## 输出位置

- 输出文件位于 `projects/PROJECT_NAME/data/compute_analysis.json`。
- `-e` 与 `-m` 都会生成这份文件。

## 统计内容

- 基础计数包含 `additions`、`multiplications`、`maps` 与 `total`。
- 统计范围为单样本、单时间步推理。
- `maps` 定义为一次非线性激活或一次 LUT 语义激活计算记为 1 次 MAP。

## 平台加权耗时

- 平台默认目标为 STM32F405。
- 以 `add` 作为 1 个基准单位。
- 默认权重为 `add_weight = 1.0`、`mul_weight = 3.0`、`map_weight = 20.0`。
- 该默认模型来自 `compare/compute_cost_calibration` 的 STM32F405 真机标定，当前标定集覆盖 `Wiener-KAN / GRU / LSTM / LSTMTransformer / 1DCNN / RNN / TCN` 七类 canonical models；旧的 `1:1:6` 只保留为历史启发式口径，不再作为默认值。
- JSON 中会输出各类操作折算后的 add 等效单位数、总单位数以及占比。

## 配置方式

- 可在项目 `config.json` 中通过 `compute_cost_model` 自定义权重。
- 支持字段包括 `platform`、`unit`、`add_weight`、`mul_weight`、`map_weight`。
- 未填写的字段会回退到默认值。

示例：

```json
{
    "compute_cost_model": {
        "add_weight": 1.0,
        "mul_weight": 1.2,
        "map_weight": 8.0
    }
}
```

## 当前支持范围

- 标准层已覆盖 `Dense`、`Conv1D`、`LSTM`、`GRU`、`SimpleRNN`、`AveragePooling1D`、`LayerNormalization`、`MultiHeadAttention`、推理态 `Dropout`。
- Keras 函数式残差加法若以 `TFOpLambda(tf.__operators__.add*)` 形式出现，也会按逐元素加法计入。
- FRIKAN 已覆盖 `SIMOIIR` / `DIAGIIR` 的 IIR 语义估算与 `DenseKAN` 的 LUT 语义估算。
- `fast_iir` 与 `fast_model` 只影响实现形式，不改变统计口径。

## 已知限制与排查

- `compute_analysis.json` 中若出现 `unsupported_layer_type` 或 `unsupported_layers` 非空，通常表示该模型的 `compute_cost` 偏低，不能直接拿来做横向比较。
- 新产物会额外写出 `estimate_status`、`estimate_warning`、`has_unsupported_layers`、`unsupported_layer_count` 与 `unsupported_layer_details`，便于脚本和 WebUI 直接提示风险。
- `CNNKAN` 前端 `Conv1D` 已纳入单时间步统计，旧产物若曾把 `cnn_filter` 标成 unsupported，需要重跑 `python cli.py -e PROJECT_NAME` 或 `python cli.py -m PROJECT_NAME` 再同步执行 `python cli.py --metrics PROJECT_NAME`。
- `GRN` 当前实际使用 `GRU` 作为主干；如果产物生成于本次修复之前，需要重跑 `python cli.py -e PROJECT_NAME` 或 `python cli.py -m PROJECT_NAME` 更新 compute cost。
- `LSTMTransformer` 当前已覆盖 pooling / attention / layer norm / residual add 的主干路径；如果旧产物里这些层仍显示 unsupported，需要重跑生成。
- 排查时优先打开 `projects/PROJECT_NAME/data/compute_analysis.json`，检查是否存在 `supported: false` 的层，以及这些层是否正好位于模型主干路径上。

## 结果解读

- `totals` 表示未加权的原始运算次数。
- `platform_cost_model` 表示当前采用的平台成本模型。
- `estimated_cost.weighted_units.total` 表示总 add 等效单位数，可作为单步推理耗时的相对估算指标。
- `estimated_cost.weighted_share_pct` 表示不同操作类别对总估算耗时的占比。
