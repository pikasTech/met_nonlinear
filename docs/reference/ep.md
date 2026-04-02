# ep 子命令说明

## 功能概述

`python cli.py ep "PROJECT/task-type/task-name"` 是外部项目任务入口，用于创建或执行配置驱动的扩展任务。若配置文件不存在，命令会先自动生成模板；若配置已存在，则直接执行任务。

## 基本用法

```bash
python cli.py ep "LSTMu32al_rs300/freq-response-compare/baseline-comparison"
python cli.py ep "LSTMu32al_rs300/wnet5-circuit-validation/layer2"
python cli.py ep "LSTMu32al_rs300/freq-response-compensator/test"
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
| 外部项目格式 | `external/projects/freq-response-compare/PS-5-190_vs_PS-5-360` | 适用于独立外部工程 |

## 支持的任务类型

当前代码中已支持或内置模板的任务类型包括：

- `freq-response-compare`
- `freq-response-compensator`
- `bias-visualization`
- `waveform-analysis`
- `wnet5-circuit-validation`
- `ablation-study`
- `compare`

## 配置文件与输出目录

对于训练项目路径，通常会生成：

- `projects/PROJECT_NAME/external/TASK_TYPE/TASK_NAME/config.json`
- `projects/PROJECT_NAME/external/TASK_TYPE/TASK_NAME/output/`

## 适用场景

- 需要可复用、可版本化的外部分析任务时使用 `ep`。
- 只想快速对比两个 `linear_response.json` 数据源时，优先使用 `--vis-freq-response-compare`。

## 相关文档

- [频率响应对比功能说明](freq_response_compare.md)
- [EP 架构文档](../project/ep.md)