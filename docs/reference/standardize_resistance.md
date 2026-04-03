# 电阻标准化功能说明

## 功能概述

`python cli.py -s PROJECT_NAME` 用于将已有电阻 CSV 映射到标准电阻系列，适合在已有导出结果基础上重新选择 E6/E12/E24/E96 系列。

## 基本用法

```bash
python cli.py -s PROJECT_NAME --input-csv INPUT.csv --series E96 E24
```

## 常用选项

```bash
python cli.py -s PROJECT_NAME --input-csv INPUT.csv --series E24
python cli.py -s PROJECT_NAME --input-csv INPUT.csv --series E96 E24 --output-dir OUTPUT_DIR
```

## 参数说明

| 参数 | 说明 |
|------|------|
| `--input-csv` | 待标准化的输入 CSV，必填 |
| `--series` | 目标标准系列，可选 `E6`、`E12`、`E24`、`E96` |
| `--output-dir` | 输出目录，默认写回项目的 `data/resistance_tables` |

## 输出内容

标准化完成后会输出：

- 输入文件路径
- 新生成的标准化 CSV 路径
- 实际使用的标准系列列表

## 使用建议

- 先通过 `python cli.py -r PROJECT_NAME` 生成原始电阻表，再使用本命令切换不同标准系列。
- 如果只想对已有 CSV 做后处理，本命令比重新导出更直接。

## 相关命令

- `python cli.py -r PROJECT_NAME`：导出电阻值与 BOM。