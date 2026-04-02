# 波形生成功能说明

## 功能概述

`python cli.py -w PROJECT_NAME` 用于从数据集中生成波形数据文件，支持压缩和强制覆盖。

## 基本用法

```bash
# 生成波形数据
python cli.py -w PROJECT_NAME

# 强制覆盖已有文件
python cli.py -w PROJECT_NAME -f
```

## 波形生成器

`DatasetWaveGenerator` 类负责波形生成流程：

1. **数据集加载** - 从项目配置加载原始数据集
2. **波形提取** - 提取 Origin 和 Target 波形
3. **文件生成** - 输出到 `wave_output` 目录
4. **压缩处理** - 可选压缩以节省空间

## 输出目录

默认输出到 `projects/PROJECT_NAME/data/wave_output/`，包含：

- 原始波形文件 (origin)
- 目标波形文件 (target)
- 元数据文件

## 数据集类型

支持多种数据集类型的波形生成，取决于 `config.json` 中的 `dataset_type` 配置。

## 相关命令

- `python cli.py --vis PROJECT_NAME` - 波形可视化
- `python cli.py -i PROJECT_NAME` - 运行推理
