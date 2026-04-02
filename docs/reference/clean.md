# 清理功能说明

## 功能概述

`python cli.py -c PROJECT_NAME` 用于删除指定项目 `data/` 目录下的训练、推理和分析产物，便于重新训练或重新生成结果。

## 基本用法

```bash
python cli.py -c PROJECT_NAME
```

## 批量清理

项目名参数支持通配符，也支持 `--all-projects`：

```bash
python cli.py -c "FRIKANh8u6l6*"
python cli.py -c --all-projects
```

## 清理范围

命令会直接删除以下目录：

- `projects/PROJECT_NAME/data/`

这通常包含：

- 模型权重
- 训练日志和训练统计
- 推理结果和可视化图片
- 误差分析与电阻导出结果

## 注意事项

- 该命令不会删除 `config.json` 和项目目录本身。
- 删除后不可恢复，适合在确认需要重跑全流程时使用。
- 如果某项目尚未生成 `data/` 目录，执行时会报目录不存在错误。

## 相关命令

- `python cli.py -t PROJECT_NAME`：重新训练并生成新的 `data/` 内容。
- `python cli.py -e PROJECT_NAME`：重新评估并生成推理与分析结果。