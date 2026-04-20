# 推理功能说明

## 功能概述

`python cli.py -i PROJECT_NAME [-q] [--layers N]` 用于对已训练 project 生成统一的推理产物。当前长期稳定的主产物目录是 `projects/<PROJECT_NAME>/data/inference/`，其中保存：

- 神经网络逐层输出。
- SPICE 逐层输出。
- 可选 NumPy 仿真逐层输出。
- 输入波形快照与推理元数据。

本文档只保留长期稳定的入口、目录、模块边界和排查口径；`WaveData` 桥接、逐层返回格式和 scaler 细节，详见 [wave_layered_inference.md](wave_layered_inference.md)。

## 命令入口

推荐按仓库相对路径传入项目名，规范写法为 `projects/...`；Windows 下传入反斜杠会先被 CLI 归一化为 `/`。

### 标准推理

```bash
python cli.py -i projects/WNET5q1h2u6l3
```

生成完整的 NN/SPICE/NumPy 推理产物。

### 快速推理

```bash
python cli.py -i projects/WNET5q1h2u6l3 -q
```

只保留输入 wave 中最小和最大震级记录，主要用于快速排查 SPICE/NumPy 链路。

### 指定推理层数

```bash
python cli.py -i projects/WNET5q1h2u6l3 --layers 5
```

只推理前 `N` 层；层数限制会同时作用于 NN 与 SPICE/NumPy，保证逐层对齐。

## 长期调用链

1. `cli.py` 负责注入 `src/` 到 `sys.path`、解析参数并分发任务。
2. `src/core/task_dispatcher.py` 归一化 `PROJECT_NAME` 后，调用 `core.project_manager.ProjectManager.run_inference()`。
3. `src/core/project_manager.py` 创建 `inference.management.InferenceManager`。
4. `InferenceManager` 先通过 `DataValidator` 做前置检查，再由 `InferenceExecutor` 执行 NN 与 SPICE/NumPy 推理。
5. `InferenceExecutor` 内部使用 `processing.InferenceProcessor`、`ModelLoader`、`BackendManager` 和 `UnifiedInferenceProcessor` 完成统一产物落盘。
6. 若后续执行 `python cli.py -a PROJECT_NAME`，则由同一 `InferenceManager` 继续消费 `data/inference/` 下的产物做误差分析。

## 核心模块边界

### ProjectManager 与模型加载

- 当前 project 上下文的权威实现位于 `src/core/project_manager.py`，而不是 `cli.py`。
- `src/inference/processing/model_loader.py` 通过依赖注入接收 `project_manager`，避免重新从 `cli.py` 反向导入 `ProjectManager`。
- 模型加载顺序是：构建 `ModelEngine` -> 尝试加载 scaler -> `build_model()` -> 优先加载 `best_val.weights.h5`，失败后回退 `best.weights.h5`。

这条边界来自历史循环导入整改：可复用库代码应依赖 `core.project_manager` 或注入的 `project_manager`，不要再把 `cli.py` 当业务模块导入。

### 后端管理

`src/inference/processing/backend_manager.py` 是长期稳定的后端切换入口，当前可用后端包括：

- `time_series`
- `batch_predict`
- `layer_by_layer`
- `spice`

CLI 的标准 `-i` 工作流实际使用两段：

1. 先切到 `layer_by_layer` 生成 NN 逐层输出。
2. 再切到 `spice` 生成 SPICE 输出，并在后端支持时同时导出 NumPy 逐层输出。

关键长期约束：

- 后端切换必须是原子的；切换失败时回滚到旧后端，不能留下“请求的是 SPICE、实际还是 NN”的半切换状态。
- WNET5 会优先选择 `WaveNet5SPICEBackend`；其他模型默认走通用 `SPICEBackend`。
- SPICE 网表的长期落点是 `projects/<PROJECT_NAME>/data/spice_netlists/`。

### 统一结果格式

`src/inference/unified.py` 把不同后端的原始返回值统一转换为：

- `InferenceResult`
- `LayerInfo`
- `DataRange`

长期约束：

- `InferenceResult.metadata.actual_backend_class` 必须与期望后端类型一致。
- `UnifiedInferenceProcessor` 会检查实际后端类名，防止把 NN 结果伪装成 SPICE 结果。
- 启用 `use_scaler=True` 时，只在模型边界统一做一次缩放/反缩放；不要在逐层比较时重复缩放。

## 输出目录与文件约定

`python cli.py -i PROJECT_NAME` 的主产物位于 `projects/<PROJECT_NAME>/data/inference/`。

| 路径 | 说明 |
|------|------|
| `input.wave` | 输入波形快照；快速模式下保存过滤后的最小/最大震级记录 |
| `inference_metadata.json` | 推理元数据，包括层数、输入文件、是否 quick mode 等 |
| `nn_layers/*.wave` | 神经网络逐层输出 |
| `spice_layers/*.wave` | SPICE 逐层输出 |
| `numpy_layers/*.wave` | 可选 NumPy 逐层输出 |
| `nn_spice_error_layers/*.wave` | `-a` 后生成的 NN-SPICE 逐层误差 wave |
| `nn_numpy_error_layers/*.wave` | `-a` 后生成的 NN-NumPy 逐层误差 wave |
| `error_analysis.json` | `-a` 后生成的误差分析 JSON 摘要 |

逐层 wave 文件的长期命名规则为 `<ModelName>_<backend>_layerN.wave`，例如 `WaveNet5_nn_layer1.wave`、`WaveNet5_spice_layer1.wave`。

## 元数据与快速模式口径

`inference_metadata.json` 当前长期可依赖的字段包括：

- `project_name`
- `project_path`
- `input_file`
- `num_layers`
- `nn_layers`
- `spice_layers`
- `numpy_layers`
- `quick_mode`

快速模式额外写入 `quick_mode_info`，用于记录：

- `original_records`
- `filtered_records`
- `min_magnitude`
- `max_magnitude`

只要 `quick_mode=true`，就应把 `input.wave` 视为“过滤后的排障输入”，而不是完整输入集。

## 前置条件与环境边界

- 项目目录必须至少具备 `config.json` 和已训练权重；否则 `ModelLoader` 无法完成推理初始化。
- 若 scaler 缺失，`ModelLoader` 会回退到默认 `CombinedScaler(feature_range=(-1, 1))`，但这只适合应急排障，不应用来签收正式结果。
- SPICE 依赖由 `src/inference/backends/spice/simulation.py` 检查；缺依赖时应优先回到 `tf26` 环境排查，详见 [tf26_environment.md](tf26_environment.md)。

## 常见排查

- 找不到 `data/inference/`：先确认项目是否已训练、权重是否存在，以及当前命令是否从仓库根目录运行。
- SPICE 后端初始化失败：先检查 `tf26` 环境、`spice_simulator` 依赖与 ngspice 路径，再决定是否切回纯 NN 排障。
- 报错提示后端类型校验失败：优先按“后端切换失败/结果伪装”处理，不要继续信任这轮产物。
- 逐层数量对不上：先核对 `--layers` 是否一致生效，再核对模型真实层数与配置是否匹配。

## 相关文档

- [wave_layered_inference.md](wave_layered_inference.md)
- [error_analysis.md](error_analysis.md)
- [project_structure.md](project_structure.md)
- [tf26_environment.md](tf26_environment.md)
- [historical_process_docs.md](historical_process_docs.md)
