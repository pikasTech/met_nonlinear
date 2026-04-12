# wave 与多后端逐层推理

## 功能概述

本项目在算法推理、逐层调试和 SPICE 电路验证之间，长期依赖同一套 wave / WaveData 桥接层，而不是让每个后端维护各自独立的数据格式。

这份文档收敛以下长期稳定约定：

- `WaveData` / `WaveRecord` 在跨后端对比中的角色
- 多后端推理的选择边界
- `LayeredModelSupport` 的分层输出契约
- `use_scaler` 在普通推理、逐层推理和 SPICE 对比中的统一口径

## 当前代码入口

与 wave 桥接和多后端逐层推理直接相关的主路径如下：

- `src/calibration_analyzer/wavedata.py`：`WaveData`、`WaveRecord` 定义与时域对象桥接
- `src/inference/processing/backend_manager.py`：多后端初始化与切换入口
- `src/inference/backends/timeseries_backend.py`：基于 `time_response()` 的时域推理
- `src/inference/backends/layered_backend.py`：逐层推理后端
- `src/inference/backends/spice/backend.py`：通用 SPICE 推理后端
- `src/inference/wavenet5_spice_backend.py`：WaveNet5 专用 SPICE 后端
- `src/models/layer_support.py`：`LayeredModelSupport` / `SpiceModelSupport` 接口定义

## WaveData 作为桥接层的长期定位

### `WaveRecord` 表示一条记录

`WaveRecord` 的长期稳定约定是：

- `data` 为 `(time_steps, channels)` 的二维数组
- 单条记录内所有通道共享同一 `sample_rate`
- `channel_names` 需要和通道数一一对应
- `record_id` 与 `user_metadata` 用于在不同后端之间保持记录级可追踪性

### `WaveData` 表示一批记录

`WaveData` 用于封装多条 `WaveRecord`，适合作为：

- 推理输入批次
- 逐层输出容器
- TF / NumPy / SPICE 对齐时的统一交换格式

它不是训练集内部张量表示的替代品，而是跨后端、跨层级的验证容器。

## 为什么逐层结果优先返回 `List[WaveData]`

当前长期约定是：逐层推理优先返回“每层一个 `WaveData`”的列表，而不是强行拼成单个四维张量。

原因是：

- 不同层的通道数通常不一致
- 有些层输出更适合保留原始波形语义，而不是强制对齐到固定 feature 维度
- 对 SPICE / TF / NumPy 做逐层对照时，按层保存和比较更直接

因此，层级验证的推荐对象是：

- `List[WaveData]`：第 `i` 个元素对应第 `i` 层输出
- 每个 `WaveData.records[k]` 继续对应输入的第 `k` 条记录

## 多后端的长期分工

`BackendManager` 当前维护四类后端：

- `time_series`：模型实现了 `time_response()` 时优先使用
- `batch_predict`：模型天然支持批量张量推理时使用
- `layer_by_layer`：模型实现了 `LayeredModelSupport` 时使用
- `spice`：需要导出电路并用 SPICE 仿真时使用

长期选择原则如下：

- 能直接走 `time_response()` 的，不要为了统一接口强行改成 batch 路径
- 需要检查中间层语义时，优先走 `layer_by_layer`
- 需要验证硬件映射正确性时，优先走 `spice`
- 不要把“能跑”当成“适合该后端”；后端选择应服从模型接口和验证目标

## `LayeredModelSupport` 的接口约定

实现 `LayeredModelSupport` 的模型，至少需要提供：

- `get_layered_models()`：按数据流顺序返回分层模型列表
- `get_layers_info()`：返回层信息摘要

长期要求是：

- `get_layered_models()` 的顺序必须与真实前向传播顺序一致
- 每个分层模型都应能独立接受上一层输出
- 层级切分应由模型自己定义，不要在通用后端里猜模型结构

这也是当前 `layered_backend` 能稳定工作的前提。

## 分层输出的元数据约定

`LayerByLayerBackend` 当前已经形成相对稳定的输出口径：

- 每一层返回一个新的 `WaveData`
- 每条记录的 `record_id` 追加 `_layerN`
- `WaveData.user_metadata` 写入 `layer_index`、`total_layers_in_model`、`layers_inferred`
- 记录级 `user_metadata` 继续沿用输入记录元数据，并追加当前层信息

长期上，这些元数据应被视为调试和对齐的一部分，而不是可有可无的附属信息。

## `layers` 参数的语义

`--layers N` 或后端 `layers=N` 的长期语义是：

- 只执行前 `N` 层
- 若请求层数超过模型总层数，则退化为执行全部层
- 它用于定位问题，不用于改变模型结构定义

因此，层数裁剪只应被用来缩小排查范围，而不是拿来定义新的实验结论。

## scaler 的统一口径

### `use_scaler` 应只在模型边界生效一次

当前推理链路里最容易复发的问题之一，是同一条数据在不同路径里被重复缩放或漏缩放。

长期规则是：

- `predict()` / `time_response()` 的 `use_scaler` 语义必须清晰且一致
- 分层推理和整模型推理必须共享同一缩放口径
- TF 与 SPICE 对照时，要先确认是否重复执行了 scaler，再比较层间误差

如果出现“整模型输出和逐层串接输出不一致”，第一优先排查项不是权重，而是 scaler 是否被多走或少走了一次。

### 先确认缩放，再比较层输出

在多后端逐层验证里，以下顺序应固定：

1. 先确认输入是否使用了同一份缩放配置。
2. 再确认分层输出是否与整模型输出口径一致。
3. 最后才看数值误差和频响差异。

缩放口径没对齐时，后续所有层级误差都不具备诊断价值。

## SPICE 后端的逐层返回约定

通用 `SPICEBackend` 当前长期支持以下返回模式：

- `return_layers=False`：返回最终 `WaveData`
- `return_layers=True`：返回各层 SPICE 输出列表
- `return_layers=True, return_numpy=True`：同时返回 SPICE 与 NumPy 逐层结果，用于同口径对照

对 WaveNet5 一类模型，专用后端还允许在通用返回结构上追加模型专属后处理，但这些后处理不应改变“按层返回 wave 列表”这一主契约。

## Wave 与 TimeSeries 的桥接边界

`WaveRecord.to_time_series()` 和 `WaveRecord.from_time_series()` 使 `WaveData` 能与 `TimeSeries` 互转。

长期建议是：

- 用 `TimeSeries` 承担单通道时域系统分析与频响测量
- 用 `WaveData` 承担多通道、多记录、跨后端交换
- 不要把本地二进制缓存、训练输入张量和 wave 文件混为同一层概念

## 推荐验证顺序

1. 先用统一输入 wave 跑普通推理，确认最终输出合理。
2. 再切到 `layer_by_layer`，确认逐层串接与整模型输出一致。
3. 需要电路验证时，再切到 `spice` 并打开 `return_layers=True`。
4. 对 SPICE 与 TF 的差异，先看 wave 和 metadata，再做频响或误差统计。

## 快速排查

- 逐层输出数量不对：先检查模型是否正确实现 `get_layered_models()`。
- 分层输出和整模型输出差异很大：先查 `use_scaler` 是否重复执行。
- 记录数或采样率不一致：先查输入 `WaveData` 是否在桥接时被改写。
- SPICE 与 TF 无法逐层对上：先查通道映射、相位约定和 wave 元数据，再查权重。

## 相关文档

- [inference.md](inference.md)
- [timeseries_frequency_analysis.md](timeseries_frequency_analysis.md)
- [circuit_realization.md](circuit_realization.md)
- [wnet5_circuit_validation.md](wnet5_circuit_validation.md)