# 推理功能说明

## 功能概述

`python cli.py -i PROJECT_NAME --layers N` 用于运行模型推理，支持快速推理模式和指定推理层数。

## 推理模式

### 标准推理

```bash
python cli.py -i PROJECT_NAME
```

### 快速推理

```bash
python cli.py -i PROJECT_NAME -q
```

跳过中间过程，直接输出结果。

### 指定推理层数

```bash
python cli.py -i PROJECT_NAME --layers 5
```

仅运行前 N 层推理，常用于调试。

## 推理后端

推理支持多种后端实现：

| 后端 | 说明 |
|------|------|
| `timeseries_backend` | 时序推理后端 |
| `layered_backend` | 分层推理后端 |
| `spice_backend` | SPICE 仿真后端 |
| `batch_backend` | 批量推理后端 |

## 输出文件

推理完成后在 `projects/PROJECT_NAME/data/` 目录下生成：

- `inference_baseline/` - 基线推理结果
- `inference_c123/` - 补偿后推理结果
- `linear_response.json` - 线性响应数据（用于频率响应对比）
- 推理可视化图片

## 推理管理器

`InferenceManager` 类负责协调推理流程：

1. 模型加载
2. 数据预处理
3. 执行推理（支持多后端）
4. 结果后处理
5. 可视化生成

## 相关命令

- `python cli.py -e PROJECT_NAME` - 评估模式（推理+指标计算）
- `python cli.py -a PROJECT_NAME` - 误差分析
- `python cli.py --bias-viz PROJECT_NAME` - 偏置可视化
