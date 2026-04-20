# ep 子命令说明

## 功能概述

`python cli.py ep "PROJECT/task-type/task-name"` 是拓展项目任务入口，只负责执行已有配置的扩展任务。

`python cli.py ep create "PROJECT/task-type/task-name"` 是显式模板创建入口，仅在需要新建拓展项目模板时使用。

这份文档负责 EP 的入口、路径、目录和产物总览；具体任务内部的长期规则应交叉引用到对应专题文档，而不是在这里重复展开。

## 基本用法

```bash
python cli.py ep create "LSTMu32al_rs300/freq-response-compare/baseline-comparison"
python cli.py ep "LSTMu32al_rs300/freq-response-compare/baseline-comparison"
python cli.py ep "LSTMu32al_rs300/wnet5-circuit-validation/layer2"
python cli.py ep "LSTMu32al_rs300/freq-response-compensator/test"
python cli.py ep "ex_projects/inference/qemu-c-inference/lstm_u16_base"
python cli.py ep "ex_projects/inference/qemu-c-inference/lstm_transformeru6_e1k_1"
python cli.py ep "ex_projects/inference/qemu-c-inference/frikan_h8u6l6_nosym"
```

## 仓库内 EP 索引

当前仓库内的 EP 任务主要分布在以下路径下，查询项目时优先从这些目录定位：

| 路径前缀 | 任务类型 | 说明 | 典型项目 |
|------|------|------|------|
| `ex_projects/visualization/freq-response-compare/` | `freq-response-compare` | 频率响应对比与可视化 | `LSTMu32al_rs300_PS-5`、`PS-5-190_vs_PS-5-360`、`WNET5_EFF2_A1_PS-5_360` |
| `ex_projects/visualization/freq-response-compensator/` | `freq-response-compensator` | 补偿器频率响应可视化 | `WNET5q1h2u6l3` |
| `ex_projects/inference/wnet5-circuit-validation/` | `wnet5-circuit-validation` | WNET5/SPICE 电路验证，包含整体验证和分层验证 | `WNET5q1h2u6l3`、`WNET5_EFF2_A1`、`WNET5_EFF2_B1` |
| `ex_projects/wnet5-circuit-validation/` | `wnet5-circuit-validation` | 通用层级验证模板 | `layer1`、`layer2`、`layer3` |
| `ex_projects/inference/qemu-c-inference/` | `qemu-c-inference` | 裸机 C/QEMU 推理一致性验证 | `lstm_u16_base`、`grnu16`、`frikan_h8u6l6_nosym` |

其中当前可直接复用的 `freq-response-compare` 项目包括：

- `LSTMu32al_rs300_ex2`
- `LSTMu32al_rs300_PS-5`
- `LSTMu32al_rs300_PS-5_160-200Hz`
- `LSTMu32al_rs300_PS-5_160-200Hz_inverse`
- `LSTMu32al_rs300_PS-5_160-200Hz_inverse_ex2`
- `LSTMu32al_rs300_PS-5_50-300Hz_inverse_ex3`
- `LSTMu32al_rs300_PS-5_50-300Hz_inverse_ex3_vs_ex4`
- `LSTMu32al_rs300_PS-5_50-300Hz_inverse_ex4`
- `PS-5-190_vs_PS-5-360`
- `WNET5_EFF2_A1_PS-5_360`

## 执行流程

1. 解析 `ep_project_path`。
2. 确定任务目录、配置文件和输出目录。
3. 若执行 `python cli.py ep create "..."`，则创建模板；若目标 `config.json` 已存在，则拒绝覆盖。
4. 若执行 `python cli.py ep "..."`，则要求 `config.json` 已存在；若不存在，则直接报错退出。

长期约束：

- 新 EP 任务必须先用 `ep create` 建模板，不要手动空建目录后再直接写 `config.json`。
- `ep` 运行态只负责执行已有配置，不承担“边创建边执行”的隐式补全逻辑。

## 架构边界

当前 EP 长期架构边界已经收敛为：

- `cli.py` 只识别 `ep` 子命令并转交 `core.external_cli_handler.handle_ep_command()`。
- `src/core/external_path_parser.py` 负责解析路径格式和归一化任务目录。
- `src/core/config_validator.py` 负责 `config.json` 校验。
- `src/core/external_cli_handler.py` 负责 create/run 分支、配置加载和任务分发。
- 具体任务类型（如 `freq-response-compare`、`wnet5-circuit-validation`、`qemu-c-inference`）只消费“已定位、已校验”的 EP 配置，不再各自重复实现路径猜测。

这意味着后续新增 EP 任务时，优先复用这条 create -> validate -> dispatch 主链，而不是在任务内部额外拼路径或偷偷生成模板。

## 路径格式

支持以下输入形式：

| 格式 | 示例 | 说明 |
|------|------|------|
| 训练项目完整格式 | `LSTMu32al_rs300/freq-response-compare/baseline-comparison` | 常用形式 |
| 简化格式 | `PROJECT/task-name` | 自动检测任务类型 |
| inference 拓展项目格式 | `ex_projects/inference/qemu-c-inference/lstm_u16_base` | 适用于推理类外部任务 |
| 拓展项目格式 | `external/projects/freq-response-compare/PS-5-190_vs_PS-5-360` | 适用于独立外部工程 |

## 支持的任务类型

当前代码中已支持或内置模板的任务类型包括：

- `freq-response-compare`
- `freq-response-compensator`
- `bias-visualization`
- `waveform-analysis`
- `wnet5-circuit-validation`
- `qemu-c-inference`
- `ablation-study`
- `compare`

### qemu-c-inference 类任务

`qemu-c-inference` 用于把已训练项目的 `best_val.weights.json` 转成裸机 C 语言 QEMU 工程，并基于配置的数据集子集执行 C/TF26 双路径一致性验证。当前任务会自动识别模型类型，已支持 `lstm`、`lstm_transformer`、`grn` 与 `frikan`。

示例：

```bash
python cli.py ep "ex_projects/inference/qemu-c-inference/lstm_u16_base"
python cli.py ep "ex_projects/inference/qemu-c-inference/lstm_transformeru6_e1k_1"
python cli.py ep "ex_projects/inference/qemu-c-inference/frikan_h8u6l6_nosym_interp"
python cli.py ep "ex_projects/inference/qemu-c-inference/frikan_h8u6l6_nosym"
```

执行后会：

1. 从对应项目的 `best_val.weights.json` 读取权重，并自动识别 `model_type`。
2. 读取 `validation_config.dataset` 指定的项目/数据集配置，并按 `magnitudes`、`frequencies`、`start_time_s`、`end_time_s` 选择 MET 数据子集。
3. 在对应 EP 目录下生成 `qemu_project/` 裸机工程。
4. 先执行 benchmark-only 运行，在捕获到 `benchmark_complete=1` 后写入纯推理计时结果到 `data/benchmark_summary.json`。
5. 再执行完整 validation 运行，在捕获到 `validation_complete=1` 后导出最终波形、模型相关中间层波形和对比图，并把波形对比指标、`intermediate_comparison` 和 `plot_paths` 写到 `data/validation_comparison.json` 与 `data/benchmark_summary.json`。

其中 `benchmark_summary.json` 会记录 `model_type`、`timer_source`、`measurement_unit`、`measurement_total`、`measurement_per_iter` 等字段；纯 benchmark 结果位于 `runs` / `aggregated`，完整 validation 运行结果位于 `validation_run`。QEMU 计时回退策略与运行细节详见 [边缘设备推理仿真](edge_device_emulation.md)。

典型配置结构如下：

```json
{
	"benchmark_config": {
		"iterations": 10,
		"reset_state_each_run": true,
		"repeat_runs": 1
	},
	"generation_config": {
		"project_dir": "qemu_project",
		"overwrite": true
	},
	"validation_config": {
		"dataset": {
			"source_project_config": "projects/LSTMu16/config.json",
			"dataset_type": "MET",
			"data_path": "data/M50",
			"sample_rate": 2000,
			"time_clipped_s": 4.0,
			"target_sweep": 2
		},
		"selection": {
			"magnitudes": [0.24],
			"frequencies": [10.0],
			"start_time_s": 0.0,
			"end_time_s": 0.2
		},
		"wave_output": {
			"compress": true,
			"plot_comparison": true,
			"plot_dpi": 200
		}
	}
}
```

其中：

- `generation_config.project_dir` 与 `overwrite` 是通用生成选项。
- FRIKAN 任务还可在 `generation_config` 中增加 `lut_points`、`lut_interpolation` 等 LUT 导出参数。
- `lut_interpolation` 的模板默认值为 `false`，用于优先走更轻的 LUT 查表路径；若某个已训练模型需要更低的 C/TF 偏差，可在具体 EP 配置中显式改回 `true`。
- `wave_output.plot_comparison` 默认开启，用于在每条 validation record 完成后自动生成一张四曲线叠加 PNG；`plot_dpi` 控制导图分辨率。

当前仓库内可直接复用的 `qemu-c-inference` 对比样例包括：

- `lstm_u16_base`：LSTM 基线。
- `lstm_transformeru6_e1k_1`：LSTMTransformer 基线，当前 benchmark-only 约 `0.05666988 s/iter`，MAE 约 `7.8189757e-04`。
- `frikan_h8u6l6_nosym_interp`：FRIKAN 插值版，`lut_points=769` 且 `lut_interpolation=true`，用于低误差对齐。
- `frikan_h8u6l6_nosym`：FRIKAN 非插值版，`lut_points=769` 且 `lut_interpolation=false`，用于性能优先验证。

四者的统一 benchmark-only / validation run / MSE 对比口径，详见 [边缘设备推理仿真](edge_device_emulation.md) 的跨模型比较章节。

### compare 类任务

compare 类任务用于系统性对比分析，支持多种消融实验：

- `compare/mae_vs_afmae` - MAE 与 AFMAE 损失函数消融对比

长期约束：

- compare 任务应优先复用已有 `metrics.json`，而不是在 EP 层重新实现指标计算。
- 做损失函数消融时，应固定数据与结构，只改变 loss 相关变量。
- `mae_vs_afmae` 的具体配置驱动模式与结果口径，详见 [mae_vs_afmae.md](mae_vs_afmae.md)。

## 配置文件与输出目录

推荐工作流：

1. 运行 `python cli.py ep create "..."` 创建模板。
2. 编辑生成的 `config.json`。
3. 运行 `python cli.py ep "..."` 执行任务。

对于训练项目路径，通常会生成：

- `projects/PROJECT_NAME/external/TASK_TYPE/TASK_NAME/config.json`
- `projects/PROJECT_NAME/external/TASK_TYPE/TASK_NAME/output/`

对于 `ex_projects/inference/qemu-c-inference/...`，会额外生成：

- `.../qemu_project/`：可被 `cli.py qemu` 直接识别的 C 工程
- `.../data/benchmark_summary.json`：QEMU 运行输出、`model_type`、纯 benchmark 结果、完整 validation 结果，以及 `comparison`、`intermediate_comparison`、`plot_paths` 等索引字段
- `.../data/validation_comparison.json`：C/TF 波形对比结果，包含 `overall`、`per_record`、`intermediate` 与 `plot_paths`
- `.../data/waves/*.wave`：最终输出波形，以及模型相关的 TF/C 中间层波形文件；LSTM 常见为 `input_scaled`、`lstm_hidden`、`dense_output`、`output_scaled`，LSTMTransformer 常见为 `input_scaled`、`lstm_hidden`、`transformer_ln_attn_*`、`transformer_ln_ffn_*`、`post_dense`、`output_scaled`，FRIKAN 常见为 `input_scaled`、`iir_output`、`kan_layer_*`、`output_scaled`
- `.../data/plots/*.png`：按 validation record 导出的四曲线对比图，默认叠加 `origin`、`target`、`c_inference`、`tf_inference`

若需要统一比较 MSE，可直接用 `validation_comparison.json` 的 `overall.diff_stats.energy / overall.sample_count` 计算；当前四样例的参考数值已同步写入 [边缘设备推理仿真](edge_device_emulation.md)。

## WNET5 电路验证频响图产物

WNET5 分层电路验证的频率响应图必须通过 `cli.py ep` 生成，不应额外写临时脚本或直接调用可视化模块。

常用命令：

```bash
python cli.py ep "ex_projects/wnet5-circuit-validation/layer1"
python cli.py ep "ex_projects/wnet5-circuit-validation/layer2"
python cli.py ep "ex_projects/wnet5-circuit-validation/layer3"
```

对应产物路径：

- `ex_projects/wnet5-circuit-validation/layer1/data/plots/frequency_response_comparison.png`
- `ex_projects/wnet5-circuit-validation/layer2/data/plots/frequency_response_comparison.png`
- `ex_projects/wnet5-circuit-validation/layer3/data/plots/frequency_response_comparison.png`

这些图的共同约定如下：

- 默认输出 PNG，典型分辨率为 `300 DPI`、约 `3600 x 2400` 像素。
- 坐标系使用 `semilogx`，横轴为频率，纵轴为线性增益。
- 图中对比理论频率响应和实验测量频率响应，常见频率范围为 `2 - 500 Hz`。
- 典型 WNET5 Dense 层验证为 6 通道输出，对应 `layer1`、`layer2`、`layer3` 三组实验 sheet。
- 这类图适合用来核对层级 SPICE 实现是否与理论响应一致；若需要项目级综合频响对比，优先使用 `freq-response-compare` 类 EP。

WNET5 分层验证的长期规则，例如通道映射、SVF 自测试补偿和 Q 值口径，详见 [wnet5_circuit_validation.md](wnet5_circuit_validation.md)。

WNET5 分层验证的其他关键约束也统一收敛在 [wnet5_circuit_validation.md](wnet5_circuit_validation.md)，包括：

- Dense 权重应优先从 project 导出的 JSON 权重读取，而不是手工写入 EP 配置。
- 仓库外实验数据路径应通过 `MET_DATA_BASE` 等环境变量展开。
- E96 量化误差仿真应沿用“权重 -> 电阻 -> E96 -> 回算权重 -> 仿真”的统一链路。
- 热力图、频响图和 Markdown 总报告的产物约束应按专题文档执行。

## 适用场景

- 需要可复用、可版本化的外部分析任务时使用 `ep`。
- 只想快速对比两个 `linear_response.json` 数据源时，优先使用 `--vis-freq-response-compare`。

## 相关文档

- [频率响应对比功能说明](freq_response_compare.md)
- [边缘设备推理仿真](edge_device_emulation.md)
- [wnet5_circuit_validation.md](wnet5_circuit_validation.md)
- [historical_process_docs.md](historical_process_docs.md)
