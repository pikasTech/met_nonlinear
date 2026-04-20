# 历史过程文档蒸馏索引

## 功能概述

`docs/reference/project/` 与 `docs/reference/archive/` 保存的是开发过程中的计划、排障记录、旧约束和迁移痕迹；它们是历史资料，不是当前仓库的直接权威说明。

当前长期规则是：

- 先从历史文档里提炼稳定规则
- 再把稳定规则写入对应的 `docs/reference/*.md` 权威文档
- 历史文档本身保留原样，不为了“更新口径”去回写或改写原始记录

## 历史资料类型

| 来源 | 主要角色 | 常见内容 | 当前使用方式 |
|------|------|------|------|
| `docs/reference/project/` | 过程计划与实现笔记 | dated implementation plan、某轮重构计划、功能落地清单 | 从中提炼长期入口、约束、判定标准，然后写回对应参考文档 |
| `docs/reference/archive/` | 历史汇总与旧说明 | 旧版 CLAUDE、迁移总结、排障归档、旧 schema 对照 | 只保留历史背景价值；当前口径以 `AGENTS.md` 和 `docs/reference/*.md` 为准 |

## 使用原则

1. 先判断历史文档里哪些是长期稳定规则，哪些只是当时那一轮的 TODO、实验路径或排障流水账。
2. 如果某条历史结论今天仍成立，应更新对应的权威参考文档，而不是把 TODO 原样复制出来。
3. 同一主题若新旧历史文档冲突，以更新阶段、且已经落到当前代码与产物链路中的规则为准。
4. “和某个旧 commit 对比”“对照旧 schema 排障”可以继续作为 troubleshooting 手段，但不应写成当前仓库的日常默认流程。

## 优先查阅的权威文档

| 主题 | 当前权威文档 |
|------|------|
| 项目结构、`cli.py` 边界、project 布局 | [project_structure.md](project_structure.md) |
| 训练入口、project 变体、前台训练约束 | [training.md](training.md) |
| 评估产物、`linear_response.json`、统一指标刷新 | [evaluation.md](evaluation.md)、[metrics.md](metrics.md) |
| 推理输出、`data/inference/`、`data/spice_netlists/` | [inference.md](inference.md)、[wave_layered_inference.md](wave_layered_inference.md) |
| 误差分析 schema 与偏置分析 | [error_analysis.md](error_analysis.md)、[bias_visualization.md](bias_visualization.md) |
| EP create/run、外部任务布局 | [ep.md](ep.md) |
| WNET5 分层电路验证、通道映射、E96、SVF 拟合 | [wnet5_circuit_validation.md](wnet5_circuit_validation.md) |
| 模拟实现、SPICE 配置、电阻 / BOM / 高通偏置 | [circuit_realization.md](circuit_realization.md)、[spice_device_bias_practices.md](spice_device_bias_practices.md)、[export_resistance.md](export_resistance.md)、[standardize_resistance.md](standardize_resistance.md) |
| `tf26`、GPU 与环境边界 | [tf26_environment.md](tf26_environment.md)、[gpu_recovery.md](gpu_recovery.md) |

## 已沉淀的长期规则

### 1. `cli.py` 不再承担 project 权威实现

历史循环导入整改已经收敛为：

- `cli.py` 只保留启动和轻量分发
- `ProjectManager` 的当前权威实现位于 `src/core/project_manager.py`
- 可复用模块应依赖 `core.project_manager` 或注入的 `project_manager`，不再反向依赖 `cli.py`

权威出处：

- [project_structure.md](project_structure.md)
- [inference.md](inference.md)

### 2. project 产物统一落在 `projects/<name>/data/`

长期稳定的 project 布局已经收敛为：

- project 配置位于 `projects/<name>/config.json`
- 训练、评估、推理和网表产物统一落在 `projects/<name>/data/`
- 主权重命名固定为 `best.weights.h5` / `best_val.weights.h5`
- scaler 主文件以 `data/scalers/combined_scaler.json` 为准

权威出处：

- [project_structure.md](project_structure.md)
- [training.md](training.md)
- [inference.md](inference.md)

### 3. EP 入口按 create / run 分工

拓展项目不再靠手工创建目录；长期规则是：

- 新 EP 项目先执行 `python cli.py ep create "..."`
- `python cli.py ep "..."` 只执行已有配置，不负责隐式补模板

权威出处：

- [ep.md](ep.md)

### 4. 误差分析结果按现行 schema 解释

旧过程文档里的 cleanup / schema 迁移问题已经沉淀为统一口径：

- 旧字段 `matrix_shape`、`n_layers`、`n_channels` 等只作为历史兼容痕迹理解
- 当前结果以 `layer_count`、`channels_per_layer`、`global_statistics` 等结构化字段为准
- 新文档不再把旧 schema 当作当前事实重复描述

权威出处：

- [error_analysis.md](error_analysis.md)

### 5. 模拟实现配置统一走 `config.json -> inference_config`

与 SPICE / 电路验证直接相关的 project 级约束，已经收敛到 `inference_config`：

- `power_supply`
- `opamp_config`
- `high_pass_config`
- `bias_compensation`
- `bom_config`（当前也在这一层统一管理）

权威出处：

- [project_structure.md](project_structure.md)
- [circuit_realization.md](circuit_realization.md)
- [spice_device_bias_practices.md](spice_device_bias_practices.md)

### 6. WNET5 推理 / SPICE 回归要守住线性前端契约

历史上的维度错配与一致性排障，已经沉淀为更稳定的工程规则：

- WNET5 的 SPICE 导出必须保留 `输入 1 维 -> SVF/IIR -> 多通道 -> Dense` 这条前端语义
- 自动化测试负责守接口契约；项目级分层图、通道映射、E96 与 SVF 拟合签收仍按 WNET5 验证文档执行
- 与历史 baseline commit 对比属于排障手段，不是日常默认流程

权威出处：

- [circuit_realization.md](circuit_realization.md)
- [testing.md](testing.md)
- [wnet5_circuit_validation.md](wnet5_circuit_validation.md)

### 7. Windows 下前台 train / eval 要保留可见输出

旧说明里的 Conda 启动与日志保留建议，已经沉淀为更稳定的入口规则：

- Windows 本机下的训练、评估和测试优先通过 `conda.bat run --no-capture-output -n tf26` 启动。
- 若需要保留命令输出，优先使用 `Tee-Object` / `tee`，而不是把 stdout 完全重定向到文件后失去当前会话可见性。
- 手工留存的 stdout/stderr 也应默认写到仓库根目录的 `logs/` 子目录，而不是把 `*.log` 平铺到根目录。
- `tf26` 的环境边界与 GPU allocator 风险继续以独立环境文档为准，不再散落在旧助手说明里。

权威出处：

- [training.md](training.md)
- [evaluation.md](evaluation.md)
- [testing.md](testing.md)
- [tf26_environment.md](tf26_environment.md)

### 8. WNET5 的实验对比配置已收敛到 `analysis_layer` + `experiment_comparison`

2025 年后几轮 WNET5 电路验证扩展，已经把更细的配置语义沉淀为：

- `analysis_layer` 负责选择 SVF 前端之后要分析的单个 Dense / 输出层。
- 新的多文件实验对比统一走 `experiment_comparison`，旧的 `compare_with_experiment` 只保留历史兼容角色。
- 图形风格选项继续集中在 `experiment_comparison.plot_config`，而不是向外扩散新的临时顶层配置键。

权威出处：

- [wnet5_circuit_validation.md](wnet5_circuit_validation.md)
- [testing.md](testing.md)

## `project/20241011` 蒸馏映射

下面这些历史文档，已经至少部分沉淀到当前权威文档；后续再遇到同主题问题时，优先回看右侧文档，而不是重复翻过程计划。

| 历史文档 / 主题 | 已蒸馏出的稳定结论 | 当前权威文档 |
|------|------|------|
| `alias_dataset_reverse_waveform_implementation_plan.md` | Alias 数据集的反转语义应落到显式数据定义字段，而不是隐含在临时脚本里 | [dataset_design.md](dataset_design.md) |
| `frequency_range_config_improvement_plan.md` | 频率范围定义统一进入 `dataset.freq_range_hz`，由 project 配置显式表达 | [dataset_design.md](dataset_design.md) |
| `waveform_visualization_implementation_plan.md` | `--vis` 的稳定职责是读取当前数据集并把图输出到 `data/visualizations/waveforms/` | [waveform_visualization.md](waveform_visualization.md) |
| `frequency_response_json_based_comparison_plan.md`、`frequency_response_flexible_comparison_plan.md`、`frequency_response_dual_layout_implementation_plan.md` | 频响对比统一基于 `linear_response.json`，并保留 overlay / side-by-side 两种布局 | [freq_response_compare.md](freq_response_compare.md)、[ep.md](ep.md) |
| `visualization_engineering_implementation_plan.md`、`visualization_task_engineering_design.md` | 可视化外部任务应通过 EP create/run 链路管理，而不是散落为临时脚本 | [ep.md](ep.md) |
| `netlist_storage_unification_implementation_plan.md`、`netlist_path_correction_plan.md` | project 专属 SPICE 网表目录统一收敛为 `projects/<PROJECT>/data/spice_netlists/`，不再依赖仓库级临时目录 | [inference.md](inference.md)、[circuit_realization.md](circuit_realization.md) |
| `resistance_export_implementation_plan.md` | 电阻导出、表格目录和后处理边界统一走当前 `-r` / `-s` 链路 | [export_resistance.md](export_resistance.md)、[standardize_resistance.md](standardize_resistance.md)、[circuit_realization.md](circuit_realization.md) |
| `weight_resistor_bom_export_plan.md`、`bom_export_enhancement_plan.md`、`bom_format_standardization_plan.md`、`bom_post_processing_implementation_plan.md`、`bom_numbering_reorganization_plan.md` | BOM 长期以原始导出 + 后处理的双阶段理解，并支持顺序编号 / 分组编号两种口径 | [export_resistance.md](export_resistance.md) |
| `resistance_standardization_relative_error_plan.md` | 电阻标准化的误差解释应基于回算后的相对误差，而不是只看电阻值本身 | [standardize_resistance.md](standardize_resistance.md) |
| `inference_config_enhancement_plan.md` | project 级模拟实现配置统一写在 `config.json -> inference_config`，并覆盖电源、运放、高通、偏置补偿与 BOM 等模拟侧约束 | [project_structure.md](project_structure.md)、[circuit_realization.md](circuit_realization.md)、[spice_device_bias_practices.md](spice_device_bias_practices.md) |
| `inference_dimension_mismatch_fix_plan.md`、`inference_consistency_test_plan.md` | WNET5 SPICE 导出必须保留 IIR / SVF 前端；自动化回归与人工分层签收分层处理，历史 baseline 对比只作为排障手段 | [inference.md](inference.md)、[testing.md](testing.md)、[circuit_realization.md](circuit_realization.md)、[wnet5_circuit_validation.md](wnet5_circuit_validation.md) |
| `circuit_dense_highpass_bias_implementation_plan.md`、`highpass_bias_rectification_plan.md` | 高通属于可选硬件补偿，理想基线默认应先关闭；启用时工作点应优先跟随通道 / 神经元 bias，而不是固定全局 bias | [circuit_realization.md](circuit_realization.md)、[spice_device_bias_practices.md](spice_device_bias_practices.md)、[wnet5_circuit_validation.md](wnet5_circuit_validation.md) |
| `wnet5_frequency_response_simulation_plan.md` | WNET5 的电路验证应先过 SVF / IIR 线性前端，再叠加 Dense；更细的自测试补偿、E96 与 SVF 拟合规则集中在 WNET5 验证文档 | [circuit_realization.md](circuit_realization.md)、[wnet5_circuit_validation.md](wnet5_circuit_validation.md) |
| `cli_implementation_plan.md`、`cli_parser_modernization_plan.md`、`cli_refactoring_plan.md`、`cli_startup_flow_analysis.md`、`refactoring_plan.md` | CLI 只保留入口职责，核心实现继续收敛在 `src/core/`、`src/inference/` 等主代码目录 | [project_structure.md](project_structure.md)、[inference.md](inference.md) |

## `project/` 顶层说明与 `project/organization/` 蒸馏映射

| 历史文档 / 主题 | 已蒸馏出的稳定结论 | 当前权威文档 |
|------|------|------|
| `ep.md` | 旧文档里“缺配置时自动补模板再执行”的智能入口属于历史方案；当前正式入口已显式分成 `python cli.py ep create "..."` 与 `python cli.py ep "..."` 两步 | [ep.md](ep.md) |
| `inference.md` | 历史性的推理基础设施总览，当前已收敛为 `cli.py -> ProjectManager -> InferenceManager / backend` 的权威链路；project 内 `data/inference/`、`data/spice_netlists/` 与误差分析边界以现行参考文档为准 | [inference.md](inference.md)、[wave_layered_inference.md](wave_layered_inference.md)、[error_analysis.md](error_analysis.md) |
| `visualization.md` | 可视化入口已拆分到波形可视化、偏置可视化、wave 生成、频响对比、WebUI 与 EP 文档；历史架构笔记不再单独定义当前 CLI 入口 | [waveform_visualization.md](waveform_visualization.md)、[bias_visualization.md](bias_visualization.md)、[wave_generation.md](wave_generation.md)、[freq_response_compare.md](freq_response_compare.md)、[webui.md](webui.md)、[ep.md](ep.md) |
| `user_command.md` | 历史命令需求清单不再作为当前命令权威；当前命令入口应回到 `AGENTS.md` 与训练/评估/推理/EP/测试等权威参考文档 | [project_structure.md](project_structure.md)、[training.md](training.md)、[evaluation.md](evaluation.md)、[inference.md](inference.md)、[ep.md](ep.md)、[testing.md](testing.md) |
| `PROJECT_README.md` | 特定 WNET5/PS-5 项目的 README 只保留实验背景；其中 project 复制、dataset 频段/反转、`inference_config` 边界等稳定规则已分别沉淀到当前权威文档 | [training.md](training.md)、[dataset_design.md](dataset_design.md)、[circuit_realization.md](circuit_realization.md)、[spice_device_bias_practices.md](spice_device_bias_practices.md) |
| `organization/README.md`、`ROOT_DIRECTORY_ORGANIZATION_PLAN.md`、`ROOT_DIRECTORY_ORGANIZATION_PROPOSAL.md` | 目录整理提案里真正长期有效的部分，是“从仓库根目录启动”“业务代码统一在 `src/`”“stdout/stderr 留存默认进 `logs/`”；其余迁移方案、数量统计与阶段目标只保留历史背景价值 | [project_structure.md](project_structure.md)、[training.md](training.md)、[evaluation.md](evaluation.md)、[testing.md](testing.md)、[tf26_environment.md](tf26_environment.md) |
| `organization/PATH_ANALYSIS_SUMMARY.md`、`organization/file_path_analysis.md` | “缺文件 / 路径错误”排障时，应先确认是否从仓库根目录运行、project 路径是否为 `projects/...`、目标项目是否已生成权重与 scaler，再怀疑路径逻辑本身 | [project_structure.md](project_structure.md)、[training.md](training.md) |

## `archive/` 蒸馏映射

| 历史文档 | 已蒸馏出的稳定结论 | 当前权威文档 |
|------|------|------|
| `circular_import_analysis.md` | 可复用模块不再反向导入 `cli.py`，project 上下文应来自 `core.project_manager` | [project_structure.md](project_structure.md)、[inference.md](inference.md) |
| `circular_import_final_report.md` | 循环导入整改的最终长期口径已经固化到当前目录边界与依赖方向说明 | [project_structure.md](project_structure.md)、[inference.md](inference.md) |
| `cleanup_locations.md` | cleanup / schema 迁移问题统一按当前 error-analysis schema 解释 | [error_analysis.md](error_analysis.md) |
| `ARCHIVE_SUMMARY.md` | 偏置补偿历史归档只保留实验背景；当前配置字段以 `bias_compensation.layer_bias_adjustments` 与 `inference_config` 为准，旧 wave / 对照统计产物主要用于复盘，不再反向定义当前接口 | [error_analysis.md](error_analysis.md)、[bias_visualization.md](bias_visualization.md)、[circuit_realization.md](circuit_realization.md)、[spice_device_bias_practices.md](spice_device_bias_practices.md) |
| `CLAUDE.old.md` | 旧助手说明里的 `tf26` / `--no-capture-output`、前台日志保留和高通 / 运放配置经验，已分别沉淀到训练、评估、测试、环境与 SPICE 文档；旧文件本身不再作为当前入口 | [training.md](training.md)、[evaluation.md](evaluation.md)、[testing.md](testing.md)、[tf26_environment.md](tf26_environment.md)、[circuit_realization.md](circuit_realization.md)、[spice_device_bias_practices.md](spice_device_bias_practices.md) |

## `project/20251104` 蒸馏映射

| 历史文档 / 主题 | 已蒸馏出的稳定结论 | 当前权威文档 |
|------|------|------|
| `wnet5_multilayer_circuit_validation_implementation_plan.md` | WNET5 分层验证一次只分析 `1 个 SVF 前端 + 1 个 Dense/输出层`；通过 `analysis_layer` 选择要分析的 Dense 层，`analysis_layer=0` 不作为当前正式入口 | [wnet5_circuit_validation.md](wnet5_circuit_validation.md) |
| `wnet5_experiment_comparison_implementation_plan.md` | 新的实验对比流程统一走 `experiment_comparison` 多文件入口，并支持自测试补偿、目录扫描和当前实验文件命名约定；`compare_with_experiment` 只保留单文件兼容角色 | [wnet5_circuit_validation.md](wnet5_circuit_validation.md) |

## `project/20251222` 与 `project/20251230_hyperparams` 蒸馏映射

| 历史文档 / 主题 | 已蒸馏出的稳定结论 | 当前权威文档 |
|------|------|------|
| `hyperparameter_tuning_guide.md` | WNET5 调参继续按控制变量法推进；带 `post_dense_*` 分支时，先比较结构变量，再回到学习率 / epoch / decay 等训练策略变量 | [training.md](training.md) |
| `summary.md`、`wnet5_multi_layer_frequency_response_comparison_report.md` | WNET5 多层实验对比、`merged_plot_mode` 这类绘图风格与层选择语义，应继续收敛在当前 WNET5 分层验证配置里，而不是另起一套报告侧配置口径 | [wnet5_circuit_validation.md](wnet5_circuit_validation.md) |
| `hyperparameter_comparison_table.md` | 超参对比表属于复盘与横向总结产物，不反向定义当前训练配置接口；当前训练决策仍应回到项目 `config.json`、`training_info.json` 与 `metrics.json` | [training.md](training.md)、[metrics.md](metrics.md) |
| `phase1-implementation-summary.md`、`phase1_resistance_export_bom_implementation_summary.md`、`summary-phase1-bom-data-consistency.md` | 第一阶段实现总结、BOM 原始导出 / 后处理、同值合并一致性与 grouped 编号等长期规则，已经收敛到当前电阻导出 / 标准化 / 验证文档；摘要里的阶段效率统计与临时行动项不再反向定义接口 | [export_resistance.md](export_resistance.md)、[standardize_resistance.md](standardize_resistance.md)、[testing.md](testing.md) |
| `SVFNET_Wnet5_weight_to_resistor_development_progress_summary.md` | “权重 -> 电阻 -> BOM” 的历史开发笔记只保留背景；现行接口仍以 `config.json -> inference_config`、project 内 `data/spice_netlists/`、`-r/-s` 与 WNET5 契约验证为准 | [project_structure.md](project_structure.md)、[circuit_realization.md](circuit_realization.md)、[export_resistance.md](export_resistance.md)、[standardize_resistance.md](standardize_resistance.md)、[testing.md](testing.md) |

## 术语与旧口径替换

| 历史术语 | 当前口径 / 去向 | 权威文档 |
|------|------|------|
| `inverse_waveform` | 拆分为 `dataset.inverse_origin`、`dataset.inverse_target`、`dataset.inverse_input` 等显式字段 | [dataset_design.md](dataset_design.md) |
| `temp/spice_output` | `projects/<PROJECT>/data/spice_netlists/` | [inference.md](inference.md)、[circuit_realization.md](circuit_realization.md) |
| `bias_adjustment_matrix` | `bias_compensation.layer_bias_adjustments`；旧字段已移除，不再作为正式配置接口 | [circuit_realization.md](circuit_realization.md)、[spice_device_bias_practices.md](spice_device_bias_practices.md) |
| WNET5 单文件实验对比默认入口 | `experiment_comparison` 为当前推荐入口；`compare_with_experiment` 仅保留历史兼容 | [wnet5_circuit_validation.md](wnet5_circuit_validation.md) |
| 旧 `matrix_shape` / `statistics` 口径 | `layer_count` / `channels_per_layer` / `global_statistics` 等现行 schema | [error_analysis.md](error_analysis.md) |
| 直接扫原始频响数据做一次性图 | 统一读取 `linear_response.json` 做对比 | [freq_response_compare.md](freq_response_compare.md) |
| 旧的反转波形临时参数 | 显式 dataset 定义与 wave/inference 输出约束 | [dataset_design.md](dataset_design.md)、[wave_layered_inference.md](wave_layered_inference.md) |

## 尚未完全蒸馏时的处理方式

如果某份过程文档里仍只有：

- 当时的 TODO 列表
- 一次性实验步骤
- 依赖旧目录或旧脚本的临时命令
- 不能被当前代码和产物链路复现的阶段性结论

则暂时不要把它们原样搬进 `docs/reference/*.md`。正确做法是：只提炼已经稳定、可复用、能被当前代码支持的规则，并在需要时继续补充本索引的映射关系。

## 相关文档

- [project_structure.md](project_structure.md)
- [inference.md](inference.md)
- [testing.md](testing.md)
- [circuit_realization.md](circuit_realization.md)
- [spice_device_bias_practices.md](spice_device_bias_practices.md)
- [wnet5_circuit_validation.md](wnet5_circuit_validation.md)
