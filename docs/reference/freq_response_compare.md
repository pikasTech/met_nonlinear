# 频率响应对比功能说明

## 功能概述

`python cli.py --vis-freq-response-compare PROJECT[@STATE] [PROJECT[@STATE]]` 用于基于 `linear_response.json` 直接生成频率响应对比图，支持项目内前后对比和跨项目数据源对比。

## 基本用法

### 项目内补偿前后对比

```bash
python cli.py --vis-freq-response-compare PROJECT
```

### 任意两个数据源对比

```bash
python cli.py --vis-freq-response-compare PROJECT1@origin PROJECT2@compensation
```

## 数据源格式

### 单数据源（项目内对比）

```
PROJECT[@STATE]
```

- `PROJECT` - 项目名称
- `STATE` - 数据状态（origin/compensation），默认 origin

### 双数据源（跨项目对比）

```
PROJECT1[@STATE1] PROJECT2[@STATE2]
```

## 输出

- 对比可视化图（overlay 或 side_by_side 布局）
- 保存到 `projects/results/` 目录

## 布局模式

| 模式 | 说明 |
|------|------|
| `overlay` | 叠加显示（默认） |
| `side_by_side` | 左右并列 |

通过 `--layout` 参数指定：

```bash
python cli.py --vis-freq-response-compare PROJECT1 PROJECT2 --layout side_by_side
```

## 数据来源

从项目的 `linear_response.json` 文件加载频率响应数据。

## 相关文档

- 若需要配置驱动的外部任务工作流，使用 [ep 子命令说明](ep.md)
- EP 架构详见 [拓展项目管理](../project/ep.md)
