# 评估功能说明

## 功能概述

`python cli.py -e PROJECT_NAME` 用于评估已训练项目，执行模型加载、指标计算、推理输出和计算量估算，是训练后的标准验收入口。

## 基本用法

```bash
python cli.py -e PROJECT_NAME
```

## 执行内容

评估流程会依次执行以下步骤：

1. 加载项目配置、数据集和模型结构。
2. 导出 `model_info.json` 与 `compute_analysis.json`。
3. 根据配置选择权重，通常优先加载 `best_val.weights.h5`。
4. 计算训练集与验证集上的 loss、MAE、AFMAE。
5. 执行预测流程，生成频率响应、时域响应或特征输出。

## 常见输出

评估结果通常位于 `projects/PROJECT_NAME/data/`，常见文件包括：

- `compute_analysis.json`：单步推理计算量和平台加权耗时估算。
- `model_info.json`：模型结构与参数信息。
- `training_info.json`：训练摘要、权重来源以及训练/验证集 loss、MAE、AFMAE。
- `linear_response.json`：频率响应对比使用的数据源。
- `linearity_by_frequency.json`：按频点导出的线性度明细，供 `--metrics` 统一汇总使用。
- `inference_baseline/`、`inference_c123/`：推理或评估阶段产生的结果目录。

具体生成内容取决于项目 `config.json` 中启用的预测项。

## 兼容性约定

- `model_engine` 会通过 `self.model_comp.predict(..., verbose=0)` 计算评估指标，因此自定义模型包装类的 `predict()` 需要兼容并透传 Keras `predict()` 的额外参数，不要只保留固定签名。
- 评估阶段在计算 MAE、AFMAE 前会将 `y_true` 和 `y_pred` 统一转换为 `float32`，避免旧项目或缩放器路径混入 `float64` 后触发 TensorFlow dtype 冲突。

## 常见故障

- 如果 `-e` 失败并报 `predict() got an unexpected keyword argument 'verbose'`，优先检查对应模型包装类的 `predict()` 是否支持 `**kwargs` 或显式支持 `verbose`。
- 如果 `-e` 失败并报 `cannot compute Sub as input #1 was expected to be a double tensor but is a float tensor`，优先检查评估指标计算链上的输入/预测张量是否在进入 loss/metric 前统一为 `float32`。
- 如果评估完成但 `metrics.json` 仍为 `partial`，通常表示 `linear_response.json`、`linearity_by_frequency.json` 或 `training_info.json` 未完整生成，应先重新执行 `python cli.py -e PROJECT_NAME`，再执行 `python cli.py --metrics PROJECT_NAME`。

## 终端输出指标

评估命令会在终端输出以下关键指标：

- 训练集 `loss`、`MAE`、`AFMAE`
- 验证集 `loss`、`MAE`、`AFMAE`
- 评估完成提示与输出目录

## 相关命令

- `python cli.py --metrics PROJECT_NAME`：从 `-e` 已生成的 `training_info.json`、`compute_analysis.json`、`linear_response.json`、`linearity_by_frequency.json` 中按消融实验同口径提取统一指标并导出 `metrics.json`。
- `python cli.py -m PROJECT_NAME`：只导出模型信息和计算量。
- `python cli.py -i PROJECT_NAME`：只运行推理，不计算完整评估指标。
- `python cli.py -a PROJECT_NAME`：在推理结果基础上做误差分析。

## 相关文档

- [计算量估算说明](compute_analysis.md)
- [模型信息功能说明](model_info.md)