# CNNKAN 替换消融记录

## 实验目标

验证 `projects/01_LR_STUDY/CNNKANh8u6l6_e1k_lr14e5_stable` 在不改变旧项目默认运行行为的前提下，是否可以稳定跑满 1000 epoch。

## 对应项目

- **项目路径**: `projects/01_LR_STUDY/CNNKANh8u6l6_e1k_lr14e5_stable`
- **训练命令**: `<TF26_PYTHON> cli.py -t projects/01_LR_STUDY/CNNKANh8u6l6_e1k_lr14e5_stable`

## 配置摘要

以下信息来自项目 `config.json` 与训练产物：

- **模型类型**: `CNNKAN`
- **训练轮数**: `epoch_train = 1000`
- **每 epoch 步数**: `step_per_epoch = 5`
- **配置学习率**: `learning_rate = 0.00014`
- **训练日志记录学习率**: `2.8e-05`（全程恒定）
- **自动学习率**: `use_auto_lr = false`
- **卷积层配置**: `CNN_FILTERS = 8`, `CNN_KERNEL_SIZE = 3`
- **Dropout**: `CNN_DROPOUT_RATE = 0.1`
- **KAN 主体配置**: `H_UNITS = 8`, `INNER_KAN_UNITS = 6`, `INNER_KAN_LAYERS = 6`

当前长期应区分两层含义：

- 项目配置里可能仍保留 `USE_FAST_MODEL` 字段，这是历史配置兼容的一部分。
- 但 `CNNKAN` 模型类本身会显式将 `self.use_fast_model = false`，因此实际走的是标准 `BaseModel` 推理/缩放路径，而不是 FRIKAN 那条 fast_model 分支。

模型导出结果显示：

- **总参数量**: `2409`
- **可训练参数量**: `2409`
- **主体结构**: `Dropout -> Conv1D(8) -> 6 x DenseKAN -> DenseKAN(1)`

## 当前实现语义

CNNKAN 的长期定位应收敛为：

- 用 `Conv1D` 提取局部时间模式。
- 后接 KAN 主体完成非线性映射。
- 不再复用 FRIKAN 的 `system` 前端语义。

因此它和 FRIMLP / FRIKAND 那种“保留 FRI 前端，只替换主体”的消融不是一回事。CNNKAN 更接近独立结构尝试，而不是严格的 FRI 前端主体替换。

## 配置口径

CNNKAN 长期上应优先通过以下配置面调参：

- `CNN_FILTERS`
- `CNN_KERNEL_SIZE`
- `CNN_DROPOUT_RATE`
- `model_subcfg.cnn_filters`
- `model_subcfg.cnn_kernel_size`
- `model_subcfg.dropout_rate`
- `model_subcfg.dropout_position`

其中 `model_subcfg` 是当前更推荐的细粒度覆盖入口；顶层 `CNN_*` 字段主要承担默认值角色。

## 复用约束

做 CNNKAN 相关实验时，长期上应守住以下约束：

1. 不要把 `USE_FAST_MODEL` 的历史配置字段误解为 CNNKAN 真正启用了 fast_model。
2. 不要把 CNNKAN 结果解释成“已经替代线性前端先验”；它回答的是局部卷积特征是否有帮助。
3. 若要比较不同 CNNKAN 变体，优先固定训练链路，只改卷积和 KAN 相关参数。

## 训练结果

训练产物显示该项目已完整跑满 1000 epoch：

- **completed_epoch**: `1000`
- **min_val_loss**: `0.051821`，出现在 `epoch 744`
- **min_loss**: `0.058259`，出现在 `epoch 738`
- **最终 loss**: `0.064247`
- **最终 val_loss**: `0.060029`
- **最终 power_log_loss**: `0.051791`
- **最终 val_power_log_loss**: `0.066920`

## 复现约束

本实验的文档结论以“旧项目原样复跑优先”为前提：

1. 共享训练代码路径默认保持旧 batch-size 行为，不为历史项目引入新的 batch-size 估算逻辑。
2. 当前仓库运行路径中不启用 `MAX_BATCH_SIZE`、`USE_LEGACY_BATCH_SIZE_ESTIMATE` 之类的额外兼容字段。
3. 该稳定版 CNNKAN 项目当前可以在默认代码路径下跑满 1000 epoch，不依赖专门的 runtime 特判。
4. 如果后续要探索新的 batch-size 策略，应复制新项目变体或单独开分支验证，不直接改历史项目默认行为。

## 结论

`CNNKANh8u6l6_e1k_lr14e5_stable` 已经证明：在当前仓库默认行为下，CNNKAN 替换消融可以稳定完成 1000 epoch 训练；同时旧项目的默认复现路径不需要为了该实验额外改动。