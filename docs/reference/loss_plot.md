# Loss 曲线功能说明

## 功能概述

`python cli.py --loss-plot PROJECT_NAME` 会读取项目训练日志并生成 loss 曲线图，同时在有学习率记录时叠加 lr 曲线。

## 基本用法

```bash
python cli.py --loss-plot PROJECT_NAME
```

## 数据来源

该命令默认读取：

- `projects/PROJECT_NAME/data/training_log.jsonl`

如果日志中没有 `epoch` 数据，命令会直接报错并停止生成图片。

## 输出文件

曲线图保存到：

- `projects/PROJECT_NAME/data/loss_curve.png`

## 图中内容

- `loss`
- `val_loss`
- `lr`（存在时绘制在右侧坐标轴）

## 相关命令

- `python cli.py -t PROJECT_NAME`：生成训练日志。
- `python cli.py -e PROJECT_NAME`：训练后做完整评估。