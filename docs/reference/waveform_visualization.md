# 波形可视化功能说明

## 功能概述

`python cli.py --vis PROJECT_NAME` 用于生成 Origin/Target 波形可视化图，支持并行处理加速。

## 基本用法

```bash
# 基本用法
python cli.py --vis PROJECT_NAME

# 强制覆盖已有图片
python cli.py --vis PROJECT_NAME -f
```

## 可视化内容

1. **Origin 波形** - 原始输入波形
2. **Target 波形** - 目标输出波形
3. **对比图** - Origin vs Target 叠加显示

## 输出目录

波形图片输出到 `projects/PROJECT_NAME/data/visualizations/waveforms/`

## 并行处理

`WaveformVisualizer` 会自动根据当前 CPU 数量选择并行进程数，CLI 当前没有单独暴露 `--max-workers` 参数。

## 支持的波形类型

- 时域波形
- 频域波形
- 误差波形

## 相关命令

- `python cli.py -w PROJECT_NAME` - 波形数据生成
- `python cli.py -i PROJECT_NAME` - 运行推理
