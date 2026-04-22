# MAE vs AFMAE 消融实验

## 功能概述

`python cli.py ep "compare/mae_vs_afmae"` 是 MAE 与 AFMAE 损失函数的消融对比任务，通过对多个模型变体进行系统性对比，评估不同损失函数对自然频率漂移、灵敏度漂移和线性度的影响。

这类 compare 任务的长期重点不是重新发明指标计算，而是复用统一评估产物，对多个项目做稳定横向比较。

## 基本用法

```bash
python cli.py -e PROJECT_NAME
python cli.py --metrics PROJECT_NAME
python cli.py ep "compare/mae_vs_afmae"
```

执行对比前，应先为参与项目生成统一指标文件 `metrics.json`。

长期规则是：compare 类任务只消费项目级 `metrics.json`，不应各自重新读取 `linear_response.json` 或训练日志去发明一套新口径。

统一指标文件的生成方式、`partial` 状态含义和批量重算边界，详见 [metrics.md](metrics.md)。

## 任务配置

任务配置文件位于 `ex_projects/compare/mae_vs_afmae/config.json`，包含以下关键配置：

这份配置长期上负责两件事：

- 指定参与比较的多个 project。
- 指定对比时要读取和展示的指标。

也就是说，`mae_vs_afmae` 只是当前的具体实例；它背后的稳定模式是“配置驱动的多项目对比”。

### 对比项目

| 项目 | 标签 | 说明 |
|------|------|------|
| LSTMu16_base | LSTMu16 Base (MAE) | LSTM 基准模型 |
| LSTMu12_puremae | LSTMu12 PureMAE | LSTM PureMAE 变体 |
| FRIKANh8u6l6_base | FRIKAN Base (MAE) | FRIKAN 基准模型 |
| FRIKANh8u6l6_puremae | FRIKAN PureMAE | FRIKAN PureMAE 变体 |
| FRIKANh8u6l6_pureafmae | FRIKAN PureAFMAE | FRIKAN PureAFMAE 变体 |
| FRIKANh8u6l6_nosym | FRIKAN NoSym (MAE) | 非对称 FRIKAN 基准 |
| FRIKANh8u6l6_nosym_puremae | FRIKAN NoSym PureMAE | 非对称 PureMAE 变体 |
| FRIKANh8u6l6_nosym_pureafmae | FRIKAN NoSym PureAFMAE | 非对称 PureAFMAE 变体 |

### 评估指标

- **自然频率漂移 (Natural Frequency Drift)**: 以 `LSTMu16_base` 为参考
- **灵敏度漂移 (Sensitivity Drift)**: 在 100Hz 频率点，以 `LSTMu16_base` 为参考
- **线性度 (Linearity)**: 使用 `mean(1 - R²) * 100` 的统一消融实验口径

如果 compare 配置额外打开：

```json
{
  "metrics": {
    "board_inference": {
      "enabled": true
    }
  }
}
```

则综合表和导出的 Excel 还会增加：

- `QEMU-MAE`
- `KEIL-MAE`
- `KEIL-SPEED (ms/point)`

这些字段都来自各项目已有的 `metrics.json`，而不是 compare 任务再去直接读取 `benchmark_summary.json` 或 `keil_benchmark_summary.json`。

如果某个项目没有配置 `board_inference_ep_path`，则该项目在综合表中的板端列应显示为 `-`；这表示“该项目未参与板端横评”，不表示 compare 失败。

### 输出格式

- JSON 格式: `ablation_results.json`
- Markdown 格式: `ablation_report.md`
- 输出目录: `ex_projects/compare/mae_vs_afmae/results/`

## 执行流程

1. 读取 `ex_projects/compare/mae_vs_afmae/config.json` 配置
2. 遍历配置中的所有项目，读取对应的 `metrics.json`
3. 计算各指标相对于参考项目的漂移量
4. 生成 JSON 和 Markdown 格式的对比报告

## compare 与 metrics 的分工

这类任务里，长期应把 `mae_vs_afmae` 和 `metrics` 分成上下游两层理解：

- [metrics.md](metrics.md) 负责定义统一指标从哪些评估产物生成，以及这些字段在 `metrics.json` 中如何落盘。
- 本文档负责说明 compare 任务如何读取多个项目的 `metrics.json`，并把它们组织成横向对比报告。

也就是说，如果发现 compare 结果异常，先判断是“上游 `metrics.json` 本身不完整或口径错误”，还是“compare 层读错了配置或参考项目”；不要一上来就在 compare 代码里重新实现一套指标。

## 长期约束

1. 做 loss 消融时，优先固定数据集、模型结构和训练链路，只改变 loss 相关变量。
2. compare 任务本身应复用已有指标基础设施，而不是在 compare 层重复实现指标计算。
3. 若某个项目的 `metrics.json` 仍是 `partial` 或来源过旧，应先补完整评估，再纳入横向比较。
4. 对比结论以统一指标和报告为准，不以训练期 `loss` 曲线直接代替。
5. 如果 compare 报告里只出现板端列缺省值 `-`，优先先检查项目是否已在 `config.json` 挂载 `board_inference_ep_path` 并重算 `metrics.json`；不要直接在 compare 层补读 EP 目录。

如果本轮修改同时涉及损失函数定义与对比任务，建议先按 [loss_design.md](loss_design.md) 的约束固定其他变量，再按 [metrics.md](metrics.md) 重算统一指标，最后再执行 compare 任务。

## 结果解读

| 指标 | 越接近 0 越好 | 说明 |
|------|---------------|------|
| 自然频率漂移 | ✓ | 频率漂移被抑制的程度 |
| 灵敏度漂移 | ✓ | 灵敏度变化被控制的程度 |
| 线性度 | ✓ | 模型线性拟合的误差 |

## 相关文档

- [EP 子命令说明](ep.md)
- [误差分析说明](error_analysis.md)
- [metrics.md](metrics.md)
- [loss_design.md](loss_design.md)
