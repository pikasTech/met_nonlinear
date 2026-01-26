## Inference 基础设施与流程总览（以 WNET5 为例）

本文面向开发者，系统梳理本仓库的推理基础设施：如何从 CLI 发起任务，如何把神经网络模型（以 WaveNet5 为例）转换为电路模型，再通过 SPICE 进行仿真，并完成误差分析与可视化；并总结关键模块、数据结构与安全校验点，便于后续扩展与排错。

---

## 端到端流程一览

- 入口与分发
  - `cli.py` 解析参数并分发到任务处理器。
  - `core/cli_parser.py` 定义所有任务与参数；`core/task_dispatcher.py` 将任务路由到 `ProjectManager`。
  - `core/project_manager.ProjectManager` 再委托给 `inference/management/InferenceManager` 执行推理与分析。

- 推理数据生成（Inference）
  - `InferenceManager.run_inference(force, quick, layers)` → 前置校验 → 定位输入 wave → 调用 `InferenceExecutor.generate_inference_data(...)`。
  - `InferenceExecutor` 内部使用 `inference/processing/InferenceProcessor`：
    - 初始化模型与后端（默认先跑 NN 分层推理，再切换到 SPICE）。
    - 保存输入、输出与元数据到项目的 `data/inference/` 下。
    - 可选：快速模式仅保留最小/最大震级记录；可选：仅推理前 N 层。

- 误差分析（Analyze）
  - `InferenceManager.analyze_errors(force)` 调用 `ErrorAnalyzer.analyze_inference_errors(...)`。
  - 逐层对比 NN vs SPICE（以及 NN vs NumPy，如有），生成误差 wave、统计与报告。

---

## 如何通过 CLI 调用

- 推理（生成 NN 与 SPICE 分层输出、可含 NumPy 仿真）
  - 任务开关：`-i` 或 `--inference`
  - 可选：`-f/--force` 重新生成；`-q/--quick` 快速模式；`--layers N` 仅前 N 层。

- 误差分析
  - 任务开关：`-a` 或 `--analyze`（依赖已存在的 `data/inference/` 推理结果）。
  - 可选：`-f/--force` 重新分析；`--bias-method` 与 `--bias-params` 控制偏置分析方法与参数。

注意：SPICE 仿真需要正确环境（见文末“环境与依赖”）。

---

## 架构与关键模块

### CLI → Dispatcher → Project

- `cli.py`
  - 初始化日志与环境检查（仅主进程）。
  - 解析参数：`core/cli_parser.parse_arguments()`。
  - 分发任务：`core/task_dispatcher.dispatch_task(...)`。

- `core/cli_parser.py`
  - 定义任务枚举 `TaskType` 与结构化参数 `CLIArgs`。
  - 任务开关：训练、评估、清理、模型信息、LUT、inference、analyze、可视化等。
  - 推理参数组：`--layers`、`--quick`、`--force` 等。

- `core/task_dispatcher.py`
  - 路由到 `ProjectManager` 对应方法。
  - Inference 路径：`ProjectManager.run_inference(force, quick, layers)`。
  - Analyze 路径：`ProjectManager.analyze_errors(...)`。

- `core/project_manager.py`
  - 封装项目上下文（`project_path`、`checkpoint_dir`、`config`）。
  - 创建 `InferenceManager` 并委托运行。

### 推理处理总管：InferenceProcessor 族

- `inference/processing/inference_processor.py`
  - 加载模型与数据：`ModelLoader` + `WaveProcessor`。
  - 选择后端：`BackendManager.initialize_backend('batch_predict'|'layer_by_layer'|'spice'|...)`。
  - 提供统一入口 `infer_and_save(...)`，内部委托给 `InferenceDataProcessor`。

- `inference/processing/backend_manager.py`
  - 管理后端实例与切换的原子性，失败自动回滚。
  - 提供智能 SPICE 后端选择：若 `model_name == 'WaveNet5'`，使用 `WaveNet5SPICEBackend`；否则通用 `SPICEBackend`。
  - 为 SPICE 生成项目内 `data/spice_netlists/` 路径。

- `inference/data_processing.py` + `inference/unified.py`
  - `UnifiedInferenceProcessor.process(...)` 统一封装：加载输入、可选缩放、调用后端、统一化结果、保存到磁盘。
  - 输出容器 `InferenceResult`：提供 `backend_type`、分层 `LayerInfo`、可选 `numpy_layers`、数据范围统计等。
  - 严格的后端类型校验，禁止“结果伪装”。

### 后端层（NN 与 SPICE）

- 神经网络（NN）
  - `inference/backends/layered_backend.py`：按层执行模型（要求实现 `LayeredModelSupport`）。
  - `inference/backends/batch_backend.py`：批量 `model.predict`。

- SPICE 与仿真
  - `inference/backends/spice/backend.py`（通用）：
    - 调用模型的 `to_spice(...)` 导出电路对象（可返回“分层电路对象列表”）。
    - 逐层调用 `SPICESimulator.simulate_with_spice(...)` 仿真；可选并行跑 `simulate_with_numpy(...)`。
    - `PhaseCorrector` 即时相位修正（例如处理 SVF HP/LP 反相）。
  - `inference/backends/spice/simulation.py`：
    - 封装对 `spice_simulator` 与 ngspice 的桥接，缺依赖时抛出明确报错。
    - NumPy 仿真使用电路对象自身的 `simulate_numpy(...)`。
  - `inference/wavenet5_spice_backend.py`（WNET5 专用）：
    - 使用 `UnifiedResistanceCalculator` 统一电阻计算；
    - `ResistanceConsistencyValidator` 强一致性校验（与 CSV 导出一致）；
    - 第一层 IIR/SVF 直接由 `SVFLayer.to_spice()` 生成，其后 Dense 层通过统一计算获取电路对象并保存分层网表。

---

## 模型侧：WNET5 的分层与电路导出

- 定位：`models/wavenet_models.py` → `class WaveNet5(BaseModel, LayeredModelSupport, SpiceModelSupport)`。
- 分层结构（简化描述）：
  1) 第 1 层：IIR/SVF 组（每个 SVF 产出 3 个通道：HP/BP/LP）。
  2) 若配置开启 `post_dense`，则若干 1x1 Conv/Dense 层；最终输出层为单通道 Dense。
- 分层封装：
  - `models/model_layers.py`：
    - `SVFLayer.to_spice(...)` → 生成 `SVFFilter` 电路对象；NumPy 分支中会在 `post_process(...)` 对 HP/LP 进行反相校正。
    - `DenseLayer.to_spice(...)` → 生成 `DenseCircuit` 电路对象；支持 ReLU/高通/电源/运放配置；带偏置时会按 `amp` 放大并应用“临时偏置补偿”钩子（若存在）。
- 模型导出：
  - `WaveNet5.to_spice(...)` 返回“分层电路对象列表”：第 1 个为 IIR/SVF，其余为 Dense/输出层；并按需保存每层网表。

---

## 统一输出与磁盘落地

- 统一结构：`inference/unified.py` → `InferenceResult` 与 `LayerInfo`。
- 保存逻辑：`UnifiedInferenceProcessor._save_results(...)`。
- 目录结构（位于项目的 `projects/<NAME>/data/inference/`）：
  - `input.wave`：输入（快速模式下为筛选后的最小/最大震级数据）。
  - `inference_metadata.json`：推理元数据（层数、后端、时间戳、是否 quick、可选筛选信息等）。
  - `nn_layers/*.wave`：按层的神经网络输出（layer_by_layer）。
  - `spice_layers/*.wave`：按层的 SPICE 仿真输出。
  - `numpy_layers/*.wave`：按层 NumPy 仿真输出（若启用）。

---

## 误差分析与报告

- 入口：`inference/management/error_analyzer.py` → `ErrorAnalyzer.analyze_inference_errors(...)`。
- 功能：
  - 严格校验层文件匹配，逐层对比并计算指标；生成 `nn_spice_error_layers/*.wave` 与（可选）`nn_numpy_error_layers/*.wave`。
  - 统计摘要写入 `error_analysis.json`。
  - 可选偏置分析：`ChannelBiasAnalyzer`（方法 `auto`/`steady_state`/`frequency_domain`），生成通道级误差矩阵与全局统计。
- 报告：`inference/management/report_generator.py` 负责把分析结果渲染为图表与报告文件（路径同 `data/inference/`）。

---

## 快速模式与层数限制

- 快速模式（`--quick`）
  - `InferenceProcessor.data_filter` 仅保留输入 wave 中“最小/最大震级”两组记录，大幅加速 SPICE 与 NumPy 仿真。
  - 元数据会记录筛选前后记录数与阈值，便于复现对照。

- 层数限制（`--layers N`）
  - NN 与 SPICE 后端都会仅仿真/推理前 N 层。SPICE 与 NumPy 分支同样受限，确保层对齐。

---

## 安全与一致性校验（强约束）

为防止“结果伪装”或“后端混淆”，系统在多处设置了强校验：

- 后端切换原子性（`BackendManager.switch_backend`）
  - 切换失败则回滚到旧后端，禁止处于不一致状态继续执行。

- 统一处理器校验（`UnifiedInferenceProcessor._convert_to_unified`）
  - 通过实际类名推断 `backend_type`，仅允许期望的后端类名模式；否则立即报错。

- 推理执行器二次校验（`InferenceExecutor._validate_spice_result`）
  - 验证 `InferenceResult.backend_type` 必须为 `spice`，并检查 `actual_backend_class` 含 `spice`。

- 文件落地校验
  - 至少检查首个输出文件存在，缺失立即报错，阻断后续分析。

---

## 环境与依赖（SPICE）

- 依赖加载：`inference/backends/spice/simulation.py::_check_spice_dependencies()`
  - 需要 `spice_simulator` 包，以及 `spice_simulator/circuit_analysis/simu_sweep.py`。
  - 不满足时会给出明确错误信息与环境建议。

- NGspice 路径：`SPICEBackend._setup_ngspice_path()`
  - 优先使用系统的 `ngspice`；在 Windows 上若缺省，回退到仓库内置路径：
    `spice_simulator/Spice64/bin/ngspice_con.exe`。

---

## 常见问题排查（FAQ）

- 现象：SPICE/NumPy 推理失败或提示“无法导入 SPICE 模拟器核心模块”。
  - 排查：检查 `spice_simulator` 是否在 PYTHONPATH 内；是否存在 `simu_sweep.py`；是否已安装对应依赖；在推荐环境中运行。

- 现象：后端类型不匹配（FATAL ERROR: 后端类型验证失败）。
  - 排查：确认后端切换过程中是否报错；检查日志里 `actual_backend_class`；确保未复用旧后端实例。

- 现象：层数不一致，无法逐层误差对齐。
  - 排查：确认 `--layers` 是否对 NN 与 SPICE 同时生效；确认模型配置 `post_dense_layers` 与数据实际层数一致。

---

## 附：WNET5 关键信息速查

- 文件与类：
  - `models/wavenet_models.py::WaveNet5`
  - `models/model_layers.py::SVFLayer`、`DenseLayer`
  - `inference/wavenet5_spice_backend.py::WaveNet5SPICEBackend`

- SVF 三通道顺序：HP、BP、LP（对 HP/LP 做相位反相修正）。

- 分层导出：`WaveNet5.to_spice(...)` 返回 `[SVF, Dense_1, Dense_2, ..., Output]` 电路对象列表。

- SPICE 输出与 NumPy 输出（可选）会与 NN 分层一一对齐，便于误差分析与可视化。

---

如需扩展新模型到 SPICE：
- 实现 `LayeredModelSupport` 与 `SpiceModelSupport`。
- 为每个可映射层提供 `to_spice(...)` 与（必要时）`post_process(...)`。
- 若有特化需求，可仿照 `WaveNet5SPICEBackend` 增加专用后端，写入一致性计算与验证逻辑。

## 流程图（Mermaid）

```mermaid
flowchart LR
  A[cli.py] --> B[core/cli_parser]
  B --> C[core/task_dispatcher]
  C --> D[core/project_manager.ProjectManager]
  D --> E[inference/management.InferenceManager]
  E --> F[InferenceExecutor]
  F --> G[processing.InferenceProcessor]
  G --> H[processing.BackendManager]
  H --> I1[LayerByLayerBackend\n(NN)]
  H --> I2[SPICEBackend /\nWaveNet5SPICEBackend]
  I1 --> J[UnifiedInferenceProcessor]
  I2 --> J
  J --> K[保存到 projects/<NAME>/data/inference]
  K --> L[management.ErrorAnalyzer\n(逐层误差/偏置分析)]
  L --> M[management.ReportGenerator]

  %% 可选分支与运行模式
  subgraph Options[运行选项]
    Q[--quick: 最小/最大震级]:::opt
    N[--layers N: 前 N 层]:::opt
  end
  Q -. 影响 .-> F
  N -. 影响 .-> I1
  N -. 影响 .-> I2

  classDef opt fill:#eef,stroke:#66f,color:#222
```
