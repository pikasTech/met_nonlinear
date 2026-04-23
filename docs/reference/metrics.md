# 指标提取功能说明

## 功能概述

`python cli.py --metrics PROJECT_NAME` 用于在 `-e` 已经生成评估产物之后，按消融实验统一口径计算汇总指标，并写入 `projects/PROJECT_NAME/data/metrics.json`。

统一原则：

- 三个主指标 `Freq Drift (Hz)`、`Sens Drift (%)`、`Linearity (%)` 的定义以消融实验实现为准。
- 其中 `Linearity (%)` 作为统一主字段时，当前默认口径固定为 `<=128 Hz` 的 in-band 平均非线性误差；字段名保留不变，仅语义更新。
- 其他模块只读取 `metrics.json`，不再各自直接读取 `linear_response.json` 或 `linearity_by_frequency.json` 重新计算。

其中 compare / 消融任务对这些指标的消费方式，统一以 [mae_vs_afmae.md](mae_vs_afmae.md) 这类专题文档为准；本文件只负责说明 `metrics.json` 如何生成与如何解释。

## 基本用法

```bash
python cli.py --metrics PROJECT_NAME
python cli.py --metrics --all-projects
python cli.py --metrics --all-projects --missing-only
```

- `python cli.py --metrics --all-projects`：递归遍历 `projects/` 下所有包含 `config.json` 的项目目录，并全量重算 `data/metrics.json`。
- `python cli.py --metrics --all-projects --missing-only`：仅为缺失 `data/metrics.json` 的项目补生成指标文件。

## 输入依赖

该命令默认读取 `projects/PROJECT_NAME/data/` 下的以下文件：

- `training_info.json`
- `compute_analysis.json`
- `linear_response.json`
- `linearity_by_frequency.json`

此外，命令还会读取项目根目录下的 `config.json`。如果其中配置了 `board_inference_ep_path`，则会把该 EP 目录下的在板推理摘要一并汇总到 `metrics.json`。

注意：`linearity_by_frequency.json` 可以保留完整评估频点；`metrics.json.linearity_percent` 只汇总当前默认带内子集，不会自动把带外频点并入主指标。

其中 `training_info.json.evaluation_metrics` 由 `python cli.py -e PROJECT_NAME` 统一写入，loss、MAE、AFMAE 在评估阶段都固定通过单一预测路径重算，与训练时具体挂了哪些 compile metrics 无关。

注意：`--metrics` 不会自行补算 `training_info.json.evaluation_metrics`。如果项目在上一次评估后又继续训练，或 `-e` 在预测/频率响应阶段中断，`training_info.json` 里的该节可能缺失，或者仍然保留旧权重对应的历史快照。

同时，`--metrics` 默认信任 `linear_response.json` 和 `linearity_by_frequency.json` 已经是正确量纲的最终产物；它不会识别“补偿输出仍停留在归一化空间”这类上游推理错误，只会如实汇总错误输入。

建议先运行：

```bash
python cli.py -e PROJECT_NAME
```

当前 CLI 在 `-e` 成功结束后会自动刷新一次 `metrics.json`；而 `-t` 现在又会在训练后自动串联一次 `-e`。因此单项目日常流程通常只需要跑完 `-t`，或在已有权重基础上单独跑完 `-e`。`python cli.py --metrics PROJECT_NAME` 仍然保留，主要用于手动重算、批量补齐、或在不重复执行评估的前提下刷新 summary。

## 统一计算方法

### Freq Drift (Hz)

从 `linear_response.json` 的 `fit_params_comped` 读取每个震级下的二阶拟合参数 `(A, B, C)`，将中心频率按下式恢复为：

$$
f_{\mathrm{center},k}
=
\operatorname{clip}
\left(
\frac{\sqrt{B_k}}{2\pi},
10\ \mathrm{Hz},
128\ \mathrm{Hz}
\right)
$$

也就是说，当前正式口径仍然保留原始 `fit` 路径，但会把恢复出的中心频率限制在当前 band（默认 `10-128 Hz`）之内，避免异常拟合把峰频抛到物理频带之外。随后对全部震级的 $f_{\mathrm{center},k}$ 序列计算：

$$
\mathrm{Freq\ Drift}
=
\max\left(
\left|\max(f_{\mathrm{center}})-\mathrm{median}(f_{\mathrm{center}})\right|,
\left|\mathrm{median}(f_{\mathrm{center}})-\min(f_{\mathrm{center}})\right|
\right)
$$

因此，该指标的实现语义是“基于 band-limited fitted center frequency 的中位数中心漂移”。与之前的 spline 试验口径不同，当前正式标准重新回到 `fit_params_comped`，但通过 band limit 保留了数值稳定性。这样既能保持原始拟合解释，又能避免某些异常 project 因拟合不稳定而出现带外爆炸值。

### Sens Drift (%)

从 `linear_response.json` 的 `gains_comped` 在 100 Hz 处逐震级插值得到灵敏度序列 $S$，再计算：

$$
\mathrm{Sens\ Drift} = \max\left( |\max(S)-\mathrm{median}(S)|, |\mathrm{median}(S)-\min(S)| \right)
$$

该字段名称保留为 `Sens Drift (%)`，以兼容现有消融实验输出。

### Linearity (%)

从 `linearity_by_frequency.json` 读取每个频点的 `r_squared_comped`，先筛选 `frequency_hz <= 128` 的 in-band 频点，再按频点转换为非线性误差：

$$
e_i = 1 - R_i^2
$$

再汇总为：

$$
\mathrm{Linearity} = \mathrm{mean}(e_i) \times 100
$$

这里的 $i$ 只覆盖 in-band 频点，不再对 `160 Hz`、`200 Hz` 等带外频点求平均。

因此这里的 `Linearity (%)` 实际上表示 `<=128 Hz` in-band 的平均非线性误差百分比，数值越小越好。字段名继续保留为 `Linearity (%)`，以兼容既有 `metrics.json` 消费方。

## 输出文件

命令会生成：

- `metrics.json`：统一指标单一来源文件。

典型字段包括：

- `status`：`complete` 或 `partial`
- `calculation_standard`：当前统一口径版本标识；当前正式值为 `ablation-study-v4-bounded-fit-freq-inband-linearity`
- `sources`：本次汇总实际命中的输入文件布尔状态
- `missing_sources`：缺失的输入文件列表
- `missing_sections`：输入文件存在但关键字段缺失的节名列表
- `freq_drift_hz`、`sens_drift_percent`、`linearity_percent`：供表格/图表直接消费的主字段
- `freq_drift_band_min_hz`、`freq_drift_band_max_hz`：`Freq Drift` 当前采用的 band limit 元数据
- `linearity_band_max_hz`、`linearity_frequency_count`、`linearity_frequency_points_hz`：当前线性度主字段实际采用的 in-band 口径元数据
- `metric_details`：上述三项指标及其 origin 版本的详细统计
- `compute_details`：计算量明细，供其他模块直接读取
- `board_inference_ep_path`：挂载的 `qemu-c-inference` EP 相对路径
- `board_qemu_mae`、`board_keil_mae`、`board_keil_speed`：在板推理汇总字段
- `board_inference`：在板推理明细、来源命中状态与缺失节信息

## 在板推理指标汇总

如果某个训练项目需要把 `qemu-c-inference` / `keil-bench` 结果纳入统一横评，可以在项目根目录 `config.json` 中增加：

```json
{
  "board_inference_ep_path": "ex_projects/inference/qemu-c-inference/your_ep_name"
}
```

`python cli.py -e PROJECT_NAME` 或 `python cli.py --metrics PROJECT_NAME` 在检测到该字段后，会额外读取挂载 EP 的：

- `data/benchmark_summary.json`
- `data/keil_benchmark_summary.json`

并按以下稳定口径汇总：

- `board_qemu_mae` <- `benchmark_summary.json.comparison.mae`
- `board_keil_mae` <- `keil_benchmark_summary.json.comparison.mae`
- `board_keil_speed` <- `keil_benchmark_summary.json.parsed_output.wall_time_per_iter_ms / (record_count * seq_len)`

其中：

- `board_keil_speed` 的单位固定为 `ms/point`
- 1 point = 1 个时间步
- `record_count * seq_len` 表示一次 validation 迭代中实际推理的总时间步数

长期上，板端指标一旦被汇总进 `metrics.json`，下游 compare / WebUI / 表格导出都应继续只读取 `metrics.json`，不要再绕过项目 summary 直接去扫 EP 目录。

## 自动刷新与手动重算

- `python cli.py -e PROJECT_NAME` 成功结束后会自动调用同一套汇总逻辑刷新 `metrics.json`。
- `python cli.py -t PROJECT_NAME` 成功结束后会自动串联执行一次 `-e`，因此也会间接刷新 `metrics.json` 并生成最新评估汇总。
- `python cli.py -m PROJECT_NAME` 在更新 `model_info.json` 与 `compute_analysis.json` 后，也会自动刷新 `metrics.json`，确保 compute cost 等字段同步更新。
- `python cli.py --metrics PROJECT_NAME` 仍是显式重算入口，适合批量修复、历史项目补齐或只想刷新 summary 不想重跑完整评估的场景。

## 统一消费方式

- WebUI 表格和图表只读取 `metrics.json`
- 消融实验对比只读取 `metrics.json`
- 如需查看原始评估产物，仅将 `linear_response.json`、`linearity_by_frequency.json` 视为 `metrics.json` 的上游输入，而不是下游展示入口

## metrics 与 compare 的分工

长期上，统一指标链路应按下面方式理解：

1. `python cli.py -e PROJECT_NAME` 或 `python cli.py --metrics PROJECT_NAME` 负责为单个项目生成 `metrics.json`。
2. compare 类任务再读取多个项目的 `metrics.json`，生成横向表格或 Markdown 报告。

因此：

- 如果单个项目指标明显异常，优先先回查本文件描述的上游评估产物与重算流程。
- 如果单个项目 `metrics.json` 正常，但横向报告异常，再去检查 compare 配置和参考项目选择。

不要把 compare 层的异常和单项目评估链异常混为一谈。

## 缺失产物时的行为

如果部分输入文件缺失，命令仍会生成 `metrics.json`，但会将 `status` 标为 `partial`，并在 `missing_sources` / `missing_sections` 中记录缺失项。

`missing_sections` 用于区分“文件存在但内部不完整”的情况。例如 `training_info.json` 存在，但其中缺少 `evaluation_metrics`，此时不会记入 `missing_sources`，而会记入 `missing_sections`。

如果 `evaluation_metrics` 缺失或过旧，应优先重新执行 `python cli.py -e PROJECT_NAME`，让评估阶段按统一口径重写 MAE/AFMAE，再执行 `python cli.py --metrics PROJECT_NAME`。

对板端指标同样适用类似规则，但边界略有不同：

- 若项目未配置 `board_inference_ep_path`，这是“未接入板端横评”的正常状态，不应把 `metrics.json` 判成 `partial`；下游展示应把板端列视为缺省值，而不是错误。
- 若项目已经配置 `board_inference_ep_path`，但 EP 目录、`benchmark_summary.json`、`keil_benchmark_summary.json` 或关键字段缺失，则应把 `metrics.json` 判为 `partial`，并在 `missing_sources` / `missing_sections` 中记录具体缺口。
- 若 `training_info.json.evaluation_metrics` 缺失，但 `linear_response.json`、`linearity_by_frequency.json` 仍存在，说明旧评估链没有完整写回；此时应优先重跑 `python cli.py -e PROJECT_NAME`，而不是只依赖已有 summary 文件。

如果 `metrics.json` 显示 `VAL_MAE`、`VAL_AFMAE` 尚可，但 `Freq Drift (Hz)`、`Sens Drift (%)`、`Linearity (%)` 极差，先不要直接下结论说模型频响能力差；应回看 `linear_response.json` 的 `gains_comped` 是否与 `gains_origin` 处于同一物理量级，并确认 `linearity_by_frequency.json` 中 `<=128 Hz` 频点是否完整。若两者量级明显不一致，优先排查模型包装类 `predict()` 是否正确执行了反缩放。

如果需要批量修复历史项目，建议使用“单项目完整跑完 `-e`，再执行 `--metrics`”的顺序，而不要在前一个项目还停留在“预测频率响应...”阶段时并发启动后续项目；否则最容易得到 `metrics.json=status=partial` 或混入旧评估快照。

若后续要执行 `compare/mae_vs_afmae` 一类多项目对比，建议先把参与项目全部重算到 `metrics.json=status=complete`，再启动 compare 任务；这样最容易把问题隔离在单项目链路，而不是在横向报告阶段才发现上游产物混杂新旧快照。

## 相关文档

- [evaluation.md](evaluation.md)
- [training.md](training.md)
- [model_info.md](model_info.md)
- [mae_vs_afmae.md](mae_vs_afmae.md)
