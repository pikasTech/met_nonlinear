# 指标提取功能说明

## 功能概述

`python cli.py --metrics PROJECT_NAME` 用于在 `-e` 已经生成评估产物之后，进一步抽取 webui 表格所需的统一指标，并写入 `projects/PROJECT_NAME/data/metrics.json`。

## 基本用法

```bash
python cli.py --metrics PROJECT_NAME
python cli.py --metrics --all-projects --missing-only
```

第二条命令会递归遍历 `projects/` 下所有包含 `config.json` 的项目目录，只为缺失 `data/metrics.json` 的项目补生成指标文件。

## 输入依赖

该命令默认读取 `projects/PROJECT_NAME/data/` 下的以下文件：

- `training_info.json`
- `compute_analysis.json`
- `linear_response.json`

建议先运行：

```bash
python cli.py -e PROJECT_NAME
```

## 输出文件

命令会生成：

- `metrics.json`：供 webui 表格直接读取的统一指标文件。

典型字段包括：

- `sources`：本次汇总实际命中的输入文件布尔状态
- `missing_sources`：缺失的输入文件列表
- `missing_sections`：输入文件存在但关键字段缺失的节名列表
- `status`：`complete` 或 `partial`

## 当前汇总指标

- `TRAIN_MAE`
- `TRAIN_AFMAE`
- `VAL_MAE`
- `VAL_AFMAE`
- `Freq Drift (Hz)`
- `Sens Drift (%)`
- `Linearity (%)`
- `Compute Cost`
- `Total Params`
- `Epochs`

同时也会保留 `min_loss`、`min_val_loss`、`train_loss`、`val_loss`、`weights_source` 等补充字段，便于表格和后续扩展复用。

## WebUI 读取方式

- 表格视图直接读取 `metrics.json`
- 图表视图中的评估指标和计算成本摘要优先读取 `metrics.json`
- R² 频点曲线和按频点 improvement 仍读取 `linearity_by_frequency.json`

## 缺失产物时的行为

如果部分输入文件缺失，命令仍会生成 `metrics.json`，但会将 `status` 标为 `partial`，并在 `missing_sources` / `missing_sections` 中记录缺失项。

`missing_sections` 用于区分“文件存在但内部不完整”的情况。例如 `training_info.json` 存在，但其中缺少 `evaluation_metrics`，此时不会记入 `missing_sources`，而会记入 `missing_sections`。