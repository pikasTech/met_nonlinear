# ep 子命令说明

## 功能概述

`python cli.py ep "PROJECT/task-type/task-name"` 是外部项目任务入口，用于创建或执行配置驱动的扩展任务。若配置文件不存在，命令会先自动生成模板；若配置已存在，则直接执行任务。

## 基本用法

```bash
python cli.py ep "LSTMu32al_rs300/freq-response-compare/baseline-comparison"
python cli.py ep "LSTMu32al_rs300/wnet5-circuit-validation/layer2"
python cli.py ep "LSTMu32al_rs300/freq-response-compensator/test"
python cli.py ep "ex_projects/inference/qemu-c-inference/lstm_u16_base"
```

## 智能执行流程

1. 解析 `ep_project_path`。
2. 确定任务目录、配置文件和输出目录。
3. 若 `config.json` 不存在，则自动创建模板并提示编辑。
4. 若 `config.json` 已存在，则验证配置并执行任务。

## 路径格式

支持以下输入形式：

| 格式 | 示例 | 说明 |
|------|------|------|
| 训练项目完整格式 | `LSTMu32al_rs300/freq-response-compare/baseline-comparison` | 常用形式 |
| 简化格式 | `PROJECT/task-name` | 自动检测任务类型 |
| inference 外部项目格式 | `ex_projects/inference/qemu-c-inference/lstm_u16_base` | 适用于推理类外部任务 |
| 外部项目格式 | `external/projects/freq-response-compare/PS-5-190_vs_PS-5-360` | 适用于独立外部工程 |

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

`qemu-c-inference` 用于把 LSTM 项目的 `best_val.weights.json` 转成裸机 C 语言 QEMU 工程，并通过 `cli.py qemu` 复用现有的构建与运行链路。

示例：

```bash
python cli.py ep "ex_projects/inference/qemu-c-inference/lstm_u16_base"
```

执行后会：

1. 从 `projects/00_MAE_VS_AFMAE/LSTMu16_base/data/best_val.weights.json` 读取权重。
2. 在对应 EP 目录下生成 `qemu_project/` 裸机工程。
3. 执行 `build-run`，并把 benchmark 汇总写到 `data/benchmark_summary.json`。

其中 `benchmark_summary.json` 会记录 `timer_source`、`measurement_unit`、`measurement_total`、`measurement_per_iter` 等计时字段；QEMU 计时回退策略与运行细节详见 [边缘设备推理仿真](edge_device_emulation.md)。

### compare 类任务

compare 类任务用于系统性对比分析，支持多种消融实验：

- `compare/mae_vs_afmae` - MAE 与 AFMAE 损失函数消融对比

## 配置文件与输出目录

对于训练项目路径，通常会生成：

- `projects/PROJECT_NAME/external/TASK_TYPE/TASK_NAME/config.json`
- `projects/PROJECT_NAME/external/TASK_TYPE/TASK_NAME/output/`

对于 `ex_projects/inference/qemu-c-inference/...`，会额外生成：

- `.../qemu_project/`：可被 `cli.py qemu` 直接识别的 C 工程
- `.../data/benchmark_summary.json`：QEMU 运行输出与汇总指标

## 适用场景

- 需要可复用、可版本化的外部分析任务时使用 `ep`。
- 只想快速对比两个 `linear_response.json` 数据源时，优先使用 `--vis-freq-response-compare`。

## 相关文档

- [频率响应对比功能说明](freq_response_compare.md)
- [边缘设备推理仿真](edge_device_emulation.md)
- [EP 架构文档](../project/ep.md)