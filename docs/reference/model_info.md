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

## 相关命令

- `python cli.py -e PROJECT_NAME` - 评估模式
- `python cli.py -l PROJECT_NAME` - LUT 生成
