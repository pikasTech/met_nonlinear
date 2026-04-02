# 偏置可视化功能说明

## 功能概述

`python cli.py --bias-viz PROJECT_NAME` 用于可视化模型偏置补偿效果，对比基线和补偿后的偏置分布。

## 基本用法

```bash
# 基本用法
python cli.py --bias-viz PROJECT_NAME

# 指定基线和补偿数据目录
python cli.py --bias-viz PROJECT_NAME --baseline PATH1 --compensated PATH2

# 自定义输出目录
python cli.py --bias-viz PROJECT_NAME --vis-output OUTPUT_DIR
```

## 数据目录

默认数据目录：

| 数据类型 | 默认路径 |
|----------|----------|
| 基线数据 | `projects/PROJECT_NAME/data/inference_baseline` |
| 补偿数据 | `projects/PROJECT_NAME/data/inference_c123` |

## 可视化内容

1. **偏置分布对比** - 基线 vs 补偿后的偏置分布
2. **改善指标统计** - 平均改善率、标准差、最大改善率
3. **分析报告** - 生成 HTML/JSON 格式的分析报告

## 输出文件

- `bias_comparison_*.png` - 偏置对比图
- `analysis_report.html` - 交互式分析报告
- `bias_improvement_stats.json` - 改善指标统计

## 相关命令

- `python cli.py -a PROJECT_NAME` - 误差分析
- `python cli.py -i PROJECT_NAME` - 运行推理
