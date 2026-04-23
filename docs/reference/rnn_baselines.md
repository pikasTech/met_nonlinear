# RNN 时序基线

## 概述

项目 `projects/07_RNN/` 下的 RNN 实验旨在建立时序任务的 canonical 基线，对应 `model_subcfg` 中的 RNN 配置变体。

所有 `RNN` 模型在 `src/models/base_models.py` 中基于 `SimpleRNN` 实现。

- `epoch_train = 1000`
- `loss = MAE`，`use_power_loss = false`
- 纯 MAE 损失函数
- 使用 `python cli.py -t PROJECT_NAME` 训练，使用 `python cli.py -e PROJECT_NAME` 评估
- 指标对应 `data/metrics.json` 中的 `Freq Drift (Hz)`、`Sens Drift (%)`、`Linearity (%)`

## 推荐的 canonical 基线

其中 `07_RNN` 目录下 1000 epoch 训练后的 RNN 推荐配置：

- `projects/07_RNN/RNNu16_e1k_puremae_r15`

基准指标：

| Project | Epochs | Val MAE | Val AFMAE | Freq Drift (Hz) | Sens Drift (%) | Linearity (%) | Compute Cost | Total Params | LR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `RNNu16_e1k_puremae_r15` | 1000 | 0.010006 | 0.094414 | 6.6752 | 23.7510 | 1.0580 | 1280 | 577 | 1.50e-3 |

需要注意的是ensitivity Drift 偏大是 RNN 类模型的固有特性，与 sensor 物理特性无关。

## 实验总结

以下总结了各 RNN 变体模型的性能表现及关键发现。

### 短 1000 epoch 对比

| Project | 配置 | Val MAE | Freq Drift (Hz) | Sens Drift (%) | Linearity (%) | 备注 |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `RNNu16_e1k_puremae_r15` | `u16`, 单层 RNN, 单层 Dense, `lr=1.5e-3` | 0.010006 | 6.6752 | 23.7510 | 1.0580 | 推荐作为 canonical 基线 |
| `RNNu16_e1k_puremae_r7` | `u16`, 单层 RNN, 单层 Dense, `lr=7e-4` | 0.012409 | 10.6091 | 26.6126 | 1.7617 | 收敛较慢，效果不佳 |
| `RNNu16d24l2_e1k_puremae_r7` | `u16`, 双层 RNN, 加 `Dense(24)`, `lr=7e-4` | 0.010785 | 10.0274 | 25.5932 | 1.1280 | 双层加深后性能反而下降 |

### 最佳 snapshot 对比

| Snapshot | 配置 | Freq Drift (Hz) | Sens Drift (%) | Linearity (%) | 备注 |
| --- | --- | ---: | ---: | ---: | --- |
| `_snap_RNNr24d16_ep526` | `recurrent_units=24`, `dense_units=16`, `lr=7e-4` | 9.5895 | 20.5253 | 1.8202 | 双层配置但未收敛到最佳 |
| `_snap_RNNr24d16_r15_ep544` | `recurrent_units=24`, `dense_units=16`, `lr=1.5e-3` | 6.2865 | 25.1161 | 1.2568 | 替代 canonical 候选 |

后续 `RNNu16r2d16_e1k_puremae_r7` 实验采用了 `min_val_loss` 策略选择最优 epoch，但 `u16` 基础模型无法支撑 `rnn_layers = 2` 的更深架构。

## 训练注意事项

本项目的 RNN 模型训练有以下限制和已知问题。

### 1. 学习率敏感性

建议 RNN 模型使用 `learning_rate = 0.0015` 而非 `0.0007`。

对于 `SimpleRNN(16) + Dense(16)` 配置：

- `projects/07_RNN/RNNu16_e1k_puremae_r7`：`10.6091 / 26.6126 / 1.7617`
- `projects/07_RNN/RNNu16_e1k_puremae_r15`：`6.6752 / 23.7510 / 1.0580`

训练 1000 epoch 后，RNN 模型普遍出现 sensitivity drift 偏大的问题，head 结构影响不显著。

### 2. 增加 `u16` 模型复杂度的尝试

性能总结：

- 增加 Dense 层宽度或深度后 `Val MAE` 略有提升，但 `Freq Drift` 与 `Sens Drift` 变化不一致
- 增加 `recurrent_units` 至 `24` 时，`Freq Drift` 改善但 `Sens Drift` 继续恶化
- 增加 `rnn_layers = 2` 后 `val_loss` 出现不收敛现象，模型容量不足
- 设置 `rnn_dropout` 或 `recurrent_dropout` 后性能下降，snapshot 结果显示 `dropout = 0` 时最优

当前 RNN 推荐配置：

- `recurrent_units = 16`
- `rnn_layers = 1`
- `dense_layers = 1`
- `dense_units = 16`

### 3. `Sens Drift (%)` 居高不下

这是 RNN 类模型的固有特性：

- `Linearity (%)` 指标相对稳定
- `Freq Drift (Hz)` 在可接受范围
- `Sens Drift (%)` 始终偏高且无明显改善趋势

从 `Val MAE` 来看，RNN 模型整体性能尚可，但 `Sens Drift (%)` 指标差的问题限制了其实际应用。

### 4. 最佳结果来自 snapshot

RNN 模型的 1000 epoch 训练不一定能获得最佳结果：

操作步骤：

1. 记录训练日志
2. 加载对应 `training_state.json`
3. 取 `min_val_loss` 对应的 epoch 及其权重
4. 加载 `best_val.weights.h5` 后执行 `python cli.py -e PROJECT_NAME`
5. 对比评估指标

该策略对 `recurrent_units = 24` 且 `rnn_layers = 2` 的更深架构不适用。

## 扩展建议

如需进一步优化 RNN 模型性能，可按以下步骤操作：

1. 基于 `projects/07_RNN/RNNu16_e1k_puremae_r15` 进行变体实验
2. 优先尝试更高学习率 `0.0015` 的配置
3. 仅调整 `model_subcfg` 中的 `recurrent_units` 参数，避免 dropout
4. 保持 `rnn_layers = 1` 和 Dense head 的简单架构
5. 使用最佳 snapshot 策略替代完整 1000 epoch

不推荐的改动：

- 增加 `dense_layers`
- 增加 `dense_units`
- 增加 `rnn_layers > 1`
- 增加额外的正则化或 dropout 层
- 同时调整 `learning_rate` 和 `model_subcfg` 参数

## 参见

RNN 时序基线的更多细节参见 [training.md](training.md)，其中 `07_RNN` 目录下的项目配置与指标含义。

- 项目位于 `projects/07_RNN/`
- 训练配置参见 `config.json`
- 关键参数 `learning_rate` 和 `model_subcfg`
- `metrics.json` 包含最终指标，评估前需先执行 `python cli.py -e PROJECT_NAME`
- 训练过程中可参考训练日志获取更多信息。
