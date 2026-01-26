---
name: ep-tool
description: 当用户需要查询外部项目、执行 EP 任务、了解 ex_projects 结构，或寻求电路验证、频率响应对比、补偿器可视化等方面的帮助时使用此技能。
version: 1.0.0
---

# 外部项目 (EP) 工具技能

此技能提供关于 met_nonlinear_master 项目中外部项目系统的全面知识。处理任何外部项目任务时均可使用。

## 核心功能

### 查询外部项目
- 按任务类型列出所有可用的外部项目
- 按名称或配置路径查找特定项目
- 了解项目结构和组织

### 执行 EP 任务
- 运行频率响应对比任务
- 执行 WNET5 电路验证任务
- 生成频率响应补偿器可视化
- 为每种任务类型使用正确的 CLI 命令

### 任务类型参考
- **freq-response-compare**: 分析和可视化电路频率响应特性
- **wnet5-circuit-validation**: 神经网络 SPICE 电路仿真验证
- **freq-response-compensator**: 生成补偿器频率响应可视化

## 使用示例

**查询所有可用的外部项目：**
```
有哪些外部项目？
显示所有 EP 任务类型
```

**查找特定项目：**
```
查找 WNET5 电路验证项目
显示分层验证选项
```

**执行外部项目任务：**
```
运行 WNET5q1h2u6l3_layer2 电路验证
为 WNET5_EFF2_A1_PS-5_360 执行频率响应对比
```

**了解项目结构：**
```
外部项目是如何组织的？
支持哪些任务类型？
```

## 命令语法

使用以下命令运行外部项目：
```bash
python cli.py ep "ex_projects/{task-type}/{project-name}"
```

示例：
```bash
python cli.py ep "ex_projects/inference/wnet5-circuit-validation/WNET5q1h2u6l3_layer2"
python cli.py ep "ex_projects/visualization/freq-response-compare/WNET5_EFF2_A1_PS-5_360"
```

## 支持的任务类型

| 任务类型 | 类别 | 项目数 | 描述 |
|-----------|------|--------|------|
| freq-response-compare | 可视化 | 10 | 频率响应对比和可视化 |
| wnet5-circuit-validation | 推理 | 8 | WNET5 神经网络 SPICE 电路验证 |
| freq-response-compensator | 可视化 | 1 | 补偿器频率响应可视化 |

## 参考文档

- [外部项目索引](references/ep-readme.md): 所有 19 个外部项目的完整列表，包含配置路径
- [频率响应图片](references/fig-readme.md): 可视化任务的详细图片规格和 CLI 命令

## 最佳实践

1. **始终使用 CLI 工具**: 所有绘图和可视化必须使用 `python cli.py ep`
2. **检查配置路径**: 执行前验证项目配置路径
3. **使用准确的项目名称**: 与 ep-readme.md 中列出的项目名称完全匹配
