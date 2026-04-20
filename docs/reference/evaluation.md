# 评估功能说明

## 功能概述

`python cli.py -e PROJECT_NAME` 用于评估已训练项目，执行模型加载、指标计算、推理输出和计算量估算，是训练后的标准验收入口。

## 基本用法

```bash
python cli.py -e PROJECT_NAME
```

### Windows 前台启动

在 Windows 本机环境下，如默认 Python 不是 `tf26`，长期优先使用：

```powershell
conda.bat run --no-capture-output -n tf26 python cli.py -e PROJECT_NAME
conda.bat run --no-capture-output -n tf26 python cli.py -e PROJECT_NAME 2>&1 | Tee-Object -FilePath logs/evaluation.stdout.log
```

长期规则是：

- 评估也应保持前台可见；若需要留存输出，优先使用 `Tee-Object` / `tee`，不要只把标准输出完全重定向到文件。
- 额外留存的 stdout/stderr 默认写到仓库根目录的 `logs/` 子目录，不要把 `evaluation.stdout.log` 一类文件直接落在仓库根目录。
- `--no-capture-output` 主要用于降低 Windows 控制台缓冲把错误输出吞掉的概率；更完整的环境边界，详见 [tf26_environment.md](tf26_environment.md)。

## 执行内容

评估流程会依次执行以下步骤：

1. 加载项目配置、数据集和模型结构。
2. 导出 `model_info.json` 与 `compute_analysis.json`。
3. 根据配置选择权重，通常优先加载 `best_val.weights.h5`。
4. 通过统一的预测重算路径计算训练集与验证集上的 loss、MAE、AFMAE。
5. 执行预测流程，生成频率响应、时域响应或特征输出。
6. 在评估成功结束后，自动刷新 `metrics.json`，将当前评估产物汇总为统一表格指标。

只有上述流程完整跑到结束，`training_info.json.evaluation_metrics` 才会作为最终评估结果写回磁盘；如果命令在频率响应拟合、预测导出或其他后处理阶段被中断，`training_info.json` 可能已经被部分刷新，但 `evaluation_metrics` 仍然缺失或保留旧值。

## 常见输出

评估结果通常位于 `projects/PROJECT_NAME/data/`，常见文件包括：

- `compute_analysis.json`：单步推理计算量和平台加权耗时估算。
- `model_info.json`：模型结构与参数信息。
- `training_info.json`：训练摘要、权重来源以及训练/验证集 loss、MAE、AFMAE。
- `linear_response.json`：频率响应对比使用的数据源。
- `linearity_by_frequency.json`：按频点导出的线性度明细，供 `--metrics` 统一汇总使用。
- `inference_baseline/`、`inference_c123/`：推理或评估阶段产生的结果目录。

以 `training_info.json.evaluation_metrics` 为例，只有在终端出现“评估完成”并正常返回后，才应认为该字段已与当前权重、当前推理产物保持一致。

同一次 `-e` 成功结束后，CLI 还会立即重写 `projects/PROJECT_NAME/data/metrics.json`，因此 WebUI 和其他只消费 `metrics.json` 的模块会直接看到最新评估结果，而不需要再手动补一次 `--metrics`。

具体生成内容取决于项目 `config.json` 中启用的预测项。

## 兼容性约定

- `-e` 在计算 loss、MAE、AFMAE 时都不再依赖 `model.evaluate()` 或 compile 时挂了几个 metric，而是固定走 `self.model_comp.predict(..., verbose=0, use_scaler=False)` 的单一路径，再在同一缩放空间内按当前项目配置重算损失与指标。
- 自定义模型包装类的 `predict()` 需要兼容并透传 Keras `predict()` 的额外参数；如果模型本身不使用缩放，也需要兼容 `use_scaler` 参数并安全忽略。
- 如果模型包装类自行重写了 `predict()`，且该模型在训练/推理链路中启用了缩放器，则该实现必须复用 `BaseModel.predict()` 的输入缩放与输出反缩放逻辑；否则会出现 loss、MAE、AFMAE 看似正常，但 `linear_response.json` 里的 `gains_comped` 仍停留在归一化量纲的情况。
- 评估阶段在计算 MAE、AFMAE 前会将 `y_true` 和 `y_pred` 统一转换为 `float32`，避免旧项目或缩放器路径混入 `float64` 后触发 TensorFlow dtype 冲突。

## 频响异常排查

- 如果 `val_mae`、`val_afmae` 看起来正常，但 `Freq Drift (Hz)`、`Sens Drift (%)`、`Linearity (%)` 明显异常，优先检查 `linear_response.json` 中 `gains_comped` 是否与 `gains_origin` 处于同一物理量级。
- 如果 `gains_origin` 在几十到几百的量级，而 `gains_comped` 只有 `0.x` 到几十，通常不是模型“学坏了”，而是频响推理路径漏掉了输出反缩放。
- 这类问题最常见的根因是某个模型包装类覆盖了 `predict()`，但没有透传 `use_scaler`，或直接绕过了 `BaseModel.predict()` 的统一缩放链路。
- 处理顺序建议是：先修复模型包装类 `predict()` 的缩放兼容性，再完整重跑 `python cli.py -e PROJECT_NAME`，最后重新执行 `python cli.py --metrics PROJECT_NAME` 验证频响三项是否恢复到合理范围。

## 常见故障

- 如果 `-e` 失败并报 `predict() got an unexpected keyword argument 'verbose'`，优先检查对应模型包装类的 `predict()` 是否支持 `**kwargs` 或显式支持 `verbose`。
- 如果 `-e` 失败并报 `predict() got an unexpected keyword argument 'use_scaler'`，优先检查对应模型包装类的 `predict()` 是否兼容 `use_scaler` 参数；不使用缩放的模型也应显式忽略该参数。
- 如果某些旧项目在评估阶段使用 `model.evaluate()` 会出现无日志退出、卡死或仅部分数据集可评估的现象，优先确认仓库版本是否已切换到统一预测重算路径；该路径会绕过这类 `evaluate()` 层的 TensorFlow 崩点。
- 如果 `-e` 跑完后 `linear_response.json` 已更新，但 `training_info.json.evaluation_metrics` 仍缺失或保留旧值，说明命令在最终写回前中断；此时不能直接信任旧的 `metrics.json`，应重新完成一次 `-e` 后再导出 `--metrics`。
- 如果 `-e` 成功结束但自动刷新 `metrics.json` 失败，CLI 会直接报错，不会默默保留旧 summary；应先修复错误后重跑 `-e` 或单独执行 `--metrics`。
- 如果 `-e` 失败并报 `cannot compute Sub as input #1 was expected to be a double tensor but is a float tensor`，优先检查评估指标计算链上的输入/预测张量是否在进入 loss/metric 前统一为 `float32`。
- 如果评估完成但 `metrics.json` 仍为 `partial`，通常表示 `linear_response.json`、`linearity_by_frequency.json` 或 `training_info.json` 未完整生成，应先重新执行 `python cli.py -e PROJECT_NAME`，再执行 `python cli.py --metrics PROJECT_NAME`。
- 如果终端停在“预测频率响应...”或频率拟合阶段较久，不要并发再启动新的 `-e` 或 `--metrics`；应等待当前命令完整结束。中断或并发覆盖后，最常见的现象是 `training_info.json.evaluation_metrics` 缺失，或者 `metrics.json` 仍然读取到旧快照。

## 终端输出指标

评估命令会在终端输出以下关键指标：

- 训练集 `loss`、`MAE`、`AFMAE`
- 验证集 `loss`、`MAE`、`AFMAE`
- 评估完成提示与输出目录

## 相关命令

- `python cli.py --metrics PROJECT_NAME`：从 `-e` 已生成的 `training_info.json`、`compute_analysis.json`、`linear_response.json`、`linearity_by_frequency.json` 中按消融实验同口径提取统一指标并导出 `metrics.json`；通常用于单独重算或批量修复历史项目。
- `python cli.py -m PROJECT_NAME`：只导出模型信息和计算量。
- `python cli.py -i PROJECT_NAME`：只运行推理，不计算完整评估指标。
- `python cli.py -a PROJECT_NAME`：在推理结果基础上做误差分析。

## 相关文档

- [计算量估算说明](compute_analysis.md)
- [模型信息功能说明](model_info.md)
