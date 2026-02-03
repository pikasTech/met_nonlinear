# R4: SVF层误差仿真相对路径修改报告

## 任务描述

将 `ex_projects\inference\wnet5-circuit-validation\SVF_ERROR_SIM\config.json` 中的绝对路径改为相对路径，避免换 PC 后无法使用。

## 修改内容

### 修改前

```json
"measured_data_file": "C:/work/met_nonlinear_master/exam_data/20251230_SVFNET_SVF_ONLY/20251230_SVF_ONLY.xlsx"
```

### 修改后

```json
"measured_data_file": "../../../../exam_data/20251230_SVFNET_SVF_ONLY/20251230_SVF_ONLY.xlsx"
```

## 路径计算

- 源文件位置: `ex_projects/inference/wnet5-circuit-validation/SVF_ERROR_SIM/config.json`
- 目标文件位置: `exam_data/20251230_SVFNET_SVF_ONLY/20251230_SVF_ONLY.xlsx`
- 相对路径层级: 从 `SVF_ERROR_SIM` 向上 4 级到达项目根目录

| 层级 | 说明 |
|------|------|
| `../` | SVF_ERROR_SIM → wnet5-circuit-validation |
| `../` | wnet5-circuit-validation → inference |
| `../` | inference → ex_projects |
| `../` | ex_projects → 项目根目录 |
| `exam_data/...` | 进入目标目录 |

## 验证方法

运行以下命令测试配置是否正确：

```bash
python cli.py ep ex_projects/inference/wnet5-circuit-validation/SVF_ERROR_SIM
```

## 修改文件

- `ex_projects/inference/wnet5-circuit-validation/SVF_ERROR_SIM/config.json`

## 总结

成功将绝对路径改为相对路径，配置文件现在可以在不同 PC 上通用。
