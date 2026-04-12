# 模型信息功能说明

## 功能概述

`python cli.py -m PROJECT_NAME` 用于导出模型的结构信息、权重信息和计算量分析。

## 基本用法

```bash
python cli.py -m PROJECT_NAME
```

## 输出内容

### 模型结构信息

保存在 `projects/PROJECT_NAME/data/model_info.json`：

- 层类型和数量
- 每层参数数量
- 总参数量
- 模型配置参数

### 计算量分析

同时生成 `compute_analysis.json`，包含：

- 单步推理运算次数 (additions, multiplications, maps)
- STM32F405 加权耗时估算
- 各操作类型占比

详见 [计算量估算说明](compute_analysis.md)

## 自动刷新 summary

- `python cli.py -m PROJECT_NAME` 成功生成 `model_info.json` 与 `compute_analysis.json` 后，会自动刷新 `projects/PROJECT_NAME/data/metrics.json`。
- 这样可以让只消费 `metrics.json` 的 WebUI 和对比脚本立即看到最新的 compute cost、参数量等字段，而不必再额外手动执行一次 `--metrics`。
- 如果项目尚未完成评估，自动刷新的 `metrics.json` 仍可能是 `partial`；这表示 summary 已同步，但上游评估产物本身还不完整。

## 相关命令

- `python cli.py -e PROJECT_NAME` - 评估模式
- `python cli.py -l PROJECT_NAME` - LUT 生成
