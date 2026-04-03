# MAE vs AFMAE 消融实验

## 功能概述

`python cli.py ep "compare/mae_vs_afmae"` 是 MAE 与 AFMAE 损失函数的消融对比任务，通过对多个模型变体进行系统性对比，评估不同损失函数对自然频率漂移、灵敏度漂移和线性度的影响。

## 基本用法

```bash
python cli.py ep "compare/mae_vs_afmae"
```

## 任务配置

任务配置文件位于 `ex_projects/compare/mae_vs_afmae/config.json`，包含以下关键配置：

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
- **线性度 (Linearity)**: 使用 1 - R² 度量

### 输出格式

- JSON 格式: `ablation_results.json`
- Markdown 格式: `ablation_report.md`
- 输出目录: `ex_projects/compare/mae_vs_afmae/results/`

## 执行流程

1. 读取 `ex_projects/compare/mae_vs_afmae/config.json` 配置
2. 遍历配置中的所有项目，加载对应的评估结果
3. 计算各指标相对于参考项目的漂移量
4. 生成 JSON 和 Markdown 格式的对比报告

## 结果解读

| 指标 | 越接近 0 越好 | 说明 |
|------|---------------|------|
| 自然频率漂移 | ✓ | 频率漂移被抑制的程度 |
| 灵敏度漂移 | ✓ | 灵敏度变化被控制的程度 |
| 线性度 | ✓ | 模型线性拟合的误差 |

## 相关文档

- [EP 子命令说明](ep.md)
- [误差分析说明](error_analysis.md)
