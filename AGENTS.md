# AGENTS.md - Agentic Coding Guidelines

## 项目概述

**MET Nonlinear** - 电化学非线性矫正项目。核心模块: `models/`, `tfkan/`, `analysis/`, `visualization/`, `calibration_analyzer/`

---

## AGENTS.md 组织原则

- `AGENTS.md` 只作为项目级顶级索引，用于快速定位命令、入口和文档。
- 每个功能在 `AGENTS.md` 中只保留一句话概括，不在此处展开实现细节、参数说明或背景分析。
- 所有功能的详细说明统一写入 `docs/reference/` 下的独立 Markdown 文档，并在 `AGENTS.md` 中提供对应链接索引。
- 当某项功能需要补充说明时，优先更新 `docs/reference/` 的详细文档，再回到 `AGENTS.md` 维护一句话摘要与链接。

---

## CLI 命令 (cli.py)

### 主命令

```bash
# 训练模型
python cli.py -t PROJECT_NAME

# 评估模型
python cli.py -e PROJECT_NAME
  - 输出单步推理计算量与 STM32F405 加权耗时估算，详见 [docs/reference/compute_analysis.md](docs/reference/compute_analysis.md)。

# 导出模型信息
python cli.py -m PROJECT_NAME
  - 同步输出与 `-e` 一致的计算量估算结果，详见 [docs/reference/compute_analysis.md](docs/reference/compute_analysis.md)。

# 运行推理
python cli.py -i PROJECT_NAME --layers 5

# 分析误差
python cli.py -a PROJECT_NAME --bias-method auto

# 清理项目数据
python cli.py -c PROJECT_NAME

# 波形生成
python cli.py -w PROJECT_NAME

# 偏置可视化
python cli.py --bias-viz PROJECT_NAME

# 导出电阻值
python cli.py -r PROJECT_NAME

# 标准化电阻
python cli.py -s PROJECT_NAME --series E96 E24

# 绘制loss曲线
python cli.py --loss-plot PROJECT_NAME
```

### ep 子命令 (外部项目)

```bash
# 频率响应对比
python cli.py ep "PROJECT/task-type/task-name"

# WNET5电路验证
python cli.py ep "PROJECT/wnet5-circuit-validation/layer2"

# 补偿器频率响应
python cli.py ep "PROJECT/freq-response-compensator/test"
```

### ep 路径格式

| 格式 | 示例 |
|------|------|
| 外部项目 | `external/projects/freq-response-compare/PS-5-190_vs_PS-5-360` |
| 训练项目 | `LSTMu32al_rs300/freq-response-compare/baseline-comparison` |
| 简化格式 | `PROJECT/task-name` (自动检测任务类型) |

### 测试命令

```bash
# 运行单元测试
python cli.py --test

# 指定测试路径
python cli.py --test --test-path src/logger/tests

# 并行测试配置
python cli.py --test --test-workers 4 --test-timeout 300
```

---

## 测试命令 (pytest)

```bash
# 运行所有测试
pytest

# 单个测试文件/函数
pytest src/analysis/tests/test_analysis_comprehensive.py::TestAliasSuppression::test_module_import -v

# 关键字匹配
pytest -k "test_module_import"
```
