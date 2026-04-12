# 指标提取功能说明

## 功能概述

`python cli.py --metrics PROJECT_NAME` 用于在 `-e` 已经生成评估产物之后，按消融实验统一口径计算汇总指标，并写入 `projects/PROJECT_NAME/data/metrics.json`。

统一原则：

- 三个主指标 `Freq Drift (Hz)`、`Sens Drift (%)`、`Linearity (%)` 的定义以消融实验实现为准。
- 其他模块只读取 `metrics.json`，不再各自直接读取 `linear_response.json` 或 `linearity_by_frequency.json` 重新计算。

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

从 `linear_response.json` 的 `fit_params_comped` 提取各个震级下的拟合参数，计算固有频率：

$$
\omega_n = \sqrt{B}, \quad f_n = \frac{\omega_n}{2\pi}
$$

然后对全部震级的 $f_n$ 序列计算：

$$
\mathrm{Freq\ Drift} = \max\left( |\max(f_n)-\mathrm{median}(f_n)|, |\mathrm{median}(f_n)-\min(f_n)| \right)
$$

### Sens Drift (%)

从 `linear_response.json` 的 `gains_comped` 在 100 Hz 处逐震级插值得到灵敏度序列 $S$，再计算：

$$
\mathrm{Sens\ Drift} = \max\left( |\max(S)-\mathrm{median}(S)|, |\mathrm{median}(S)-\min(S)| \right)
$$

该字段名称保留为 `Sens Drift (%)`，以兼容现有消融实验输出。

### Linearity (%)

从 `linearity_by_frequency.json` 读取每个频点的 `r_squared_comped`，先按频点转换为非线性误差：

$$
e_i = 1 - R_i^2
$$

再汇总为：

$$
\mathrm{Linearity} = \mathrm{mean}(e_i) \times 100
$$

因此这里的 `Linearity (%)` 实际上沿用消融实验口径，表示平均非线性误差百分比，数值越小越好。

## 输出文件

命令会生成：

- `metrics.json`：统一指标单一来源文件。

典型字段包括：

- `status`：`complete` 或 `partial`
- `sources`：本次汇总实际命中的输入文件布尔状态
- `missing_sources`：缺失的输入文件列表
- `missing_sections`：输入文件存在但关键字段缺失的节名列表
- `freq_drift_hz`、`sens_drift_percent`、`linearity_percent`：供表格/图表直接消费的主字段
- `metric_details`：上述三项指标及其 origin 版本的详细统计
- `compute_details`：计算量明细，供其他模块直接读取

## 自动刷新与手动重算

- `python cli.py -e PROJECT_NAME` 成功结束后会自动调用同一套汇总逻辑刷新 `metrics.json`。
- `python cli.py -t PROJECT_NAME` 成功结束后会自动串联执行一次 `-e`，因此也会间接刷新 `metrics.json` 并生成最新评估汇总。
- `python cli.py -m PROJECT_NAME` 在更新 `model_info.json` 与 `compute_analysis.json` 后，也会自动刷新 `metrics.json`，确保 compute cost 等字段同步更新。
- `python cli.py --metrics PROJECT_NAME` 仍是显式重算入口，适合批量修复、历史项目补齐或只想刷新 summary 不想重跑完整评估的场景。

## 统一消费方式

- WebUI 表格和图表只读取 `metrics.json`
- 消融实验对比只读取 `metrics.json`
- 如需查看原始评估产物，仅将 `linear_response.json`、`linearity_by_frequency.json` 视为 `metrics.json` 的上游输入，而不是下游展示入口

## 缺失产物时的行为

如果部分输入文件缺失，命令仍会生成 `metrics.json`，但会将 `status` 标为 `partial`，并在 `missing_sources` / `missing_sections` 中记录缺失项。

`missing_sections` 用于区分“文件存在但内部不完整”的情况。例如 `training_info.json` 存在，但其中缺少 `evaluation_metrics`，此时不会记入 `missing_sources`，而会记入 `missing_sections`。

如果 `evaluation_metrics` 缺失或过旧，应优先重新执行 `python cli.py -e PROJECT_NAME`，让评估阶段按统一口径重写 MAE/AFMAE，再执行 `python cli.py --metrics PROJECT_NAME`。

如果 `metrics.json` 显示 `VAL_MAE`、`VAL_AFMAE` 尚可，但 `Freq Drift (Hz)`、`Sens Drift (%)`、`Linearity (%)` 极差，先不要直接下结论说模型频响能力差；应回看 `linear_response.json` 的 `gains_comped` 是否与 `gains_origin` 处于同一物理量级。若两者量级明显不一致，优先排查模型包装类 `predict()` 是否正确执行了反缩放。

如果需要批量修复历史项目，建议使用“单项目完整跑完 `-e`，再执行 `--metrics`”的顺序，而不要在前一个项目还停留在“预测频率响应...”阶段时并发启动后续项目；否则最容易得到 `metrics.json=status=partial` 或混入旧评估快照。