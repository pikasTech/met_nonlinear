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

建议先运行：

```bash
python cli.py -e PROJECT_NAME
python cli.py --metrics PROJECT_NAME
```

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

## 统一消费方式

- WebUI 表格和图表只读取 `metrics.json`
- 消融实验对比只读取 `metrics.json`
- 如需查看原始评估产物，仅将 `linear_response.json`、`linearity_by_frequency.json` 视为 `metrics.json` 的上游输入，而不是下游展示入口

## 缺失产物时的行为

如果部分输入文件缺失，命令仍会生成 `metrics.json`，但会将 `status` 标为 `partial`，并在 `missing_sources` / `missing_sections` 中记录缺失项。

`missing_sections` 用于区分“文件存在但内部不完整”的情况。例如 `training_info.json` 存在，但其中缺少 `evaluation_metrics`，此时不会记入 `missing_sources`，而会记入 `missing_sections`。