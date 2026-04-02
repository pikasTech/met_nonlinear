# 电阻管理功能说明

## 功能概述

电阻管理功能包括电阻值导出和标准化，支持 E96/E24 等标准电阻系列。

## 导出电阻值

```bash
# 导出电阻值（包含标准化值）
python cli.py -r PROJECT_NAME --series E96 E24

# 跳过验证步骤
python cli.py -r PROJECT_NAME --skip-validation

# 生成 BOM 清单
python cli.py -r PROJECT_NAME --bom --bom-package 0805
```

## 电阻标准化

```bash
# 标准化已有 CSV 文件
python cli.py -s PROJECT_NAME --series E96 E24 --input-csv INPUT.csv

# 指定输出目录
python cli.py -s PROJECT_NAME --series E96 E24 --output-dir OUTPUT_DIR
```

## BOM 生成选项

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--bom-package` | 封装规格 | 0805 |
| `--bom-standardize` | BOM 标准化系列 | - |
| `--bom-numbering` | 编号模式 (sequential/grouped) | sequential |

## 输出文件

- `resistance_values.csv` - 电阻值 CSV
- `resistance_standardized_E96.csv` - E96 标准化值
- `resistance_standardized_E24.csv` - E24 标准化值
- `weight_resistor_bom.csv` - BOM 清单

## 验证机制

导出过程包含与网表的一致性验证，确保 CSV 数据与 SPICE 网表完全匹配。

## 相关文档

详见 [电阻管理架构文档](../research/weight_resistor_bom_export_implementation_report.md)
