# 真实 1DCNN / TCN 卷积时序基线

## 功能概述

本专题用于固定仓库内“真实 1DCNN”与“真实 TCN”基线的长期口径，回答以下稳定问题：

- 什么样的项目才算真正的 `1DCNN` 或 `TCN`
- 代码层面的模型入口在哪里
- 当前保留的 canonical 项目路径是什么
- 后续做卷积时序对比时，应如何避免把历史伪基线重新混入对照组

一次性的清理过程、阶段性记录和任务报告不写入本文件；这里只保留长期可复用的判定规则与索引。

## 判定口径

### 真实 1DCNN

满足以下条件时，才视为真实 `1DCNN` 基线：

- `config.json` 中 `use_model` 为 `1DCNN` 或 `OneDCNN`
- `src/core/model_engine.py` 走 `OneDCNN` 分支，而不是复用 `WaveNet2` 或其他历史替身
- 导出的模型结构可对应到 `src/models/conv_models.py` 中的 `OneDCNN`

### 真实 TCN

满足以下条件时，才视为真实 `TCN` 基线：

- `config.json` 中 `use_model` 为 `TCN`
- `src/core/model_engine.py` 走 `TCN` 分支，而不是复用 `WaveNet3` 或其他历史替身
- 导出的模型结构可对应到 `src/models/conv_models.py` 中的 `TCN`

## 代码入口

当前卷积时序基线的稳定代码入口如下：

- 模型定义：`src/models/conv_models.py`
  - `OneDCNN`：`src/models/conv_models.py:392`
  - `TCN`：`src/models/conv_models.py:462`
- 模型导出：`src/models/__init__.py:15`
- 模型分发：`src/core/model_engine.py:387`、`src/core/model_engine.py:396`

如果后续调整卷积层细节、残差结构或 dilation 规则，应继续复用这些入口，而不是再通过别名把项目重定向回历史 `WaveNet` 实现。

## Canonical 项目

当前仓库只保留以下两个真实卷积时序基线项目作为长期对照入口：

- `projects/05_1DCNN/1DCNNc4u8k20l8_e1k_lr18e3_pd8l8_true`
- `projects/06_TCN/TCNc4d1248k3_nopd_true_e1k_lr2e3`

这两个项目分别对应：

- 真实 `1DCNN` 基线
- 真实 `TCN` 基线

后续做横向比较、补算 `metrics.json`、导出 `model_info.json` 或写专题文档时，应优先引用这两个路径。

## 历史项目处理口径

`projects/05_1DCNN/` 与 `projects/06_TCN/` 目录下，只有真正使用 `1DCNN` / `TCN` 分支的项目才应保留为长期参考。

对外说明时，应统一遵循以下口径：

- 历史上若某些目录名写作 `1DCNN` 或 `TCN`，但实际 `use_model` 仍指向 `WaveNet2`、`WaveNet3` 或其他替身，则它们不属于真实卷积时序基线
- 这类历史目录不应再被当作当前 canonical 对照项目引用
- 若未来需要新增新的 `1DCNN` / `TCN` 变体，应从真实同类项目复制配置后再修改，不要从历史伪基线继续派生

## 训练与验收约束

对真实卷积时序基线，长期建议保持以下验收方式：

1. 用 `python cli.py -t PROJECT_NAME` 完整训练，再以自动串联或显式 `-e` / `--metrics` 生成统一指标。
2. 用 `python cli.py -m PROJECT_NAME` 或读取 `model_info.json`，确认导出的结构与目标模型名称一致。
3. 对比结论以 `metrics.json` 和统一评估链路为准，不用目录名替代真实模型语义。

如果目录名、历史备注与实际 `config.json.use_model` 不一致，应始终以配置和模型分发代码为准。

## 相关文档

- [model_architecture_selection.md](model_architecture_selection.md)
- [training.md](training.md)
- [evaluation.md](evaluation.md)
- [metrics.md](metrics.md)
