# 电阻导出功能说明

## 功能概述

`python cli.py -r PROJECT_NAME` 用于从项目权重或网表数据导出电阻表，支持标准化系列输出、BOM 生成和一致性校验。

## 基本用法

```bash
python cli.py -r PROJECT_NAME
python cli.py -r PROJECT_NAME --series E96 E24
```

## 常用选项

```bash
python cli.py -r PROJECT_NAME --output-dir OUTPUT_DIR
python cli.py -r PROJECT_NAME --skip-validation
python cli.py -r PROJECT_NAME --bom --bom-package 0805
python cli.py -r PROJECT_NAME --bom --bom-standardize E24 --bom-numbering grouped
```

## 参数说明

| 参数 | 说明 |
|------|------|
| `--series` | 导出时附带的标准化系列，默认 `E96 E24` |
| `--output-dir` | 指定导出目录，默认项目 `data/resistance_tables` |
| `--skip-validation` | 跳过数据一致性校验，不推荐 |
| `--bom` | 同时生成 BOM 文件 |
| `--bom-package` | 指定 BOM 封装，默认 `0805` |
| `--bom-standardize` | 指定 BOM 使用的标准化系列 |
| `--bom-numbering` | BOM 编号模式，支持 `sequential` 和 `grouped` |

## 输出文件

默认输出目录为 `projects/PROJECT_NAME/data/resistance_tables/`，常见文件包括：

- `all_layers_resistances.csv`
- `all_layers_resistances_bom.csv`
- 各标准化系列的导出 CSV

实际文件名可能因导出模式不同略有差异，但都会集中在 `resistance_tables` 目录下。

## 验证机制

默认会执行导出结果与项目数据的一致性验证，适合在进入电路实现或 BOM 流程前使用。

## 相关命令

- `python cli.py -s PROJECT_NAME --input-csv FILE.csv`：对已有导出表做再次标准化。
- `python cli.py -m PROJECT_NAME`：导出模型信息，用于核对层结构和参数来源。