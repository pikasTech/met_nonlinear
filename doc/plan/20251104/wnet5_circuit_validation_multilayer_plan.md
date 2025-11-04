# WNET5 多层频率响应扩展实施方案（C04）

## 1. 背景与目标
- 现有 `wnet5-circuit-validation` 外部任务已支持 **SVF 层 + Dense 第一层** 的频率响应仿真，并能生成 `results.json`、可视化图和报告。
- 新需求要求在同一套基础设施下，按配置切换至 **第二/第三/第四层 Dense 模块**，依旧保持“1 个 SVF 层 + 1 个 Dense 层”的线性频响分析模式，以便与实际电路板逐层比对。
- 目标是在最小化侵入的前提下，扩展配置、执行链路与产物标注，使用户可以通过 `config.json` 中的 `analysis_layer` 字段选择目标 Dense 层。

## 2. 需求拆解
- **配置扩展**：`config.json` 需新增 `"analysis_layer"`（整数，默认 1，可选 1~4），用于指示本次仿真的 Dense 层索引。
- **执行逻辑**：
  - 读取 `analysis_layer`，根据 `WaveNet5.layer_to_layer_models` 选取对应的 Dense 包装器。
  - 确保始终只提取一个 Dense 层的权重（含 bias），并与 SVF 组合计算传递函数。
  - 若请求的层不存在或输入/输出维度与 SVF 展开的 3×N 通道不一致，则提前报错并给出提示。
- **输出产物**：
  - 需要在 `results.json`、报告、图表命名中体现目标层（如 `layer2`）。
  - `results.json` 中补充 `"analysis_layer"` 字段，并在 `dense_layer.layer_name` 中保留真实层名。
  - 数值产物和图表可复用当前结构，但建议在文件名中加入层编号以避免覆盖。

## 3. 设计方案

### 3.1 配置与验证层改造
- **`core/external_cli_handler.py`**
  - `_create_wnet5_circuit_validation_template`：模板中加入 `"analysis_layer": 1`，并在注释或文档中说明可选取 1~4。
- **`core/config_validator.py`**
  - `WNET5_CIRCUIT_VALIDATION_SCHEMA` 新增 `analysis_layer` 属性，类型为整数，范围约束 `[1, 4]`。
  - 在 `_validate_business_logic` 增加针对 `wnet5-circuit-validation` 的扩展校验：
    - 若未提供则默认 1；提供时需为 1~4。
    - 可在此阶段检查 `frequency_range.start_freq < stop_freq`（目前 schema 已确保取值范围，但可补充越界提示）。

### 3.2 执行器与分析引擎
- **`core/external_cli_handler.py`**
  - `_execute_wnet5_circuit_validation_task`：无须改动传参，只需保证新的配置字段能够透传；如需记录日志，可在调用前输出目标层信息。
- **`visualization/wnet5_circuit_validator.py`**（核心改动）
  - `__init__`：解析 `analysis_layer`（默认 1），存为实例属性，并在日志中登记。
  - 新增 `_select_dense_wrapper`：
    - 过滤 `layer_to_layer_models`（索引 1 起）中 `DenseLayer`/`Output_Layer_Model` 类型，按出现顺序映射至层号 1~N。
    - 层号超界时报错，提示可用层与模型配置 (`post_dense_layers`)。
  - `_extract_dense_weights` 调整为依据 `analysis_layer` 选取目标包装器，提取其 `model.get_weights()`。
    - 继续支持 Conv1D kernel_size=1 与 Dense 的权重归一化，确保 shape -> `(input_channels, output_channels)`。
    - 若 input_channels 与 `len(svf_tfs)*3` 不一致，直接抛出异常，引导用户检查模型配置或层选择。
  - `_generate_plots` / `_generate_analysis_report` / `_save_results`：
    - 在标题、输出文件名中拼接 `layer{analysis_layer}`，如 `frequency_response_layer2.png`。
    - `results.json` 中新增顶层 `analysis_layer` 字段，并在 `artifacts` 中同步更新文件路径。

### 3.3 产出结构调整
- 维持既有目录结构 `data/plots`, `data/numerics`, `data/reports`。
- 文件命名建议：
  - `plots/frequency_response_layer{N}.png`
  - `plots/frequency_response_comparison_layer{N}.png`
  - `reports/analysis_report_layer{N}.json`
  - `results_layer{N}.json`（若保留原文件名亦可，但需避免覆盖；推荐追加层号）。
- `results.json` 中将 `dense_layer.layer_name` 与 `analysis_layer` 对齐，便于回溯。

## 4. 实施步骤
1. **模板与验证扩展**
   - 更新 `core/external_cli_handler.py` 模板，加入默认 `analysis_layer`。
   - 修改 `core/config_validator.py` schema 与业务校验，确保新字段合法且默认值兼容旧配置。
2. **分析引擎改造**
   - 在 `visualization/wnet5_circuit_validator.py` 引入层选择与权重提取逻辑。
   - 复用现有频响计算流程，确保输出通道命名、日志信息包含层号。
3. **结果产物命名与元数据**
   - 调整生成与保存函数，避免不同层的产出互相覆盖。
   - 在 `results.json` 记录 `analysis_layer`，并校验旧解析脚本是否依赖既有键名（如有，需要同步调整解析脚本或注明兼容策略）。
4. **文档同步**
   - 在 `doc/guide/user_command.md` 或相关使用说明中补充 `analysis_layer` 参数说明与示例。
   - 若存在自动生成模板的使用文档，确保更新。

## 5. 验证与测试
- **单元/模块测试**：
  - 如无现成测试，可在 `tests/` 下新增针对 `_select_dense_wrapper` 与 `_extract_dense_weights` 的最小化测试（可基于 `unittest.mock` 构造假的 `layer_to_layer_models`）。
- **集成测试**：
  - 准备一个示例项目（如 `WNET5q1h2u6l3`），分别设置 `analysis_layer = 1/2/3/4` 执行 `python cli.py ep ...`，确认：
    - CLI 日志显示指定层。
    - 输出目录下图表、报告、结果文件不覆盖，且内容中层号正确。
    - `results.json` 的 `dense_layer.weight` 维度与指定层匹配。
- **回归验证**：省略 `analysis_layer` 字段（或设置为 1），确认行为等同现有版本。

## 6. 风险与注意事项
- 深层 Dense 层的输入通道数必须与 SVF 输出一致；若模型配置不满足，需在日志中明确提示，并指导用户调整模型或选择其他层。
- 若 `analysis_layer=4` 对应的是最终输出层（可能为 1 通道），频响图形数量会显著减少，需在文档中说明。
- 需确认现有数据消费方（如后续分析脚本）是否依赖固定文件名；如有，需同步更新或提供兼容别名。
- TensorFlow 依赖仍是硬性要求；若未来需要离线模式（通过预导出的权重 JSON），需另起计划。
