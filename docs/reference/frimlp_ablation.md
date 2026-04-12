# FRIMLP 真消融修复记录

## 实验目标

验证 FRIKAN 的 KAN 主体替换为 MLP 后，是否能在保持 FRI 前端语义不变的前提下完成真正的消融，并将 `Freq Drift (Hz)` 压到 `10 Hz` 以下。

本轮结论只适用于“前端结构不变，只替换 KAN 部分”的 FRIMLP；如果前端、训练策略或推理路径也一并改掉，就不再是同一类消融。

## 正确架构约束

FRIMLP 的正确语义如下：

1. 保留 FRIKAN 的 IIR/RNN 前端构建路径，不单独重写一套前端。
2. 仅将 KAN 主体替换为 MLP，允许通过 `model_subcfg` 调整 MLP 宽度、层数、激活和 dropout。
3. 若基线使用 `USE_FAST_MODEL = true`，FRIMLP 也必须保留 fast_model 路径，不能为了规避问题直接关闭。
4. `H_UNITS = 8` 对 FRIMLP 仍表示 8 路 FRI 前端输出，而不是 1 路前端加 8 宽 MLP。

## 这次暴露出的根因

此前 FRIMLP 结果长期异常，根因不是单纯超参数问题，而是实现偏离了上述约束：

1. FRIMLP 曾被写成一条独立模型分支，直接脱离 FRIKAN 的前端与 fast_model 构建链。
2. FRIMLP 曾显式关闭 `use_fast_model`，导致训练/推理路径和 FRIKAN 基线不一致。
3. `ProjectManager.prepare_dataset_and_model()` 早先只让模型名包含 `FRIKAN` 的项目走 `prepare_systems()`；FRIMLP 因此拿不到 `self.E`，最终退化成 1 路 `SIMOIIR`。

这个问题的直接症状是：

- `model_info.json` 里 `simoiir` 的输出不是 `(None, None, 8)`，而是 `(None, None, 1)`。
- fast_model 不存在，或者 fast_model 输入宽度不是 8。
- 即便时域 loss 看似下降，频响三指标仍明显失真。

## 修复后的验收信号

修复完成后，应优先检查以下结构信号，而不是先看终端 loss：

1. `model_info.json` 中 `simoiir` 的输出形状应为 `(None, None, 8)`。
2. `fast_model` 必须存在，且输入宽度应与 FRI 特征数一致。
3. 训练产物中应同时出现 `fast_best.weights.h5` 与 `fast_best_val.weights.h5`。
4. 若此前已经用错误架构训练过，必须先清空旧 `data/` 再从头重训。

## 达标项目

- **项目路径**: `projects/04_FRIMLP/FRIMLPh8u6l6_e1k_lr7e4_mlp20l6_tanh_d00`
- **训练命令**: `<TF26_PYTHON> cli.py -t projects/04_FRIMLP/FRIMLPh8u6l6_e1k_lr7e4_mlp20l6_tanh_d00`
- **评估命令**: `<TF26_PYTHON> cli.py -e projects/04_FRIMLP/FRIMLPh8u6l6_e1k_lr7e4_mlp20l6_tanh_d00`
- **指标命令**: `<TF26_PYTHON> cli.py --metrics projects/04_FRIMLP/FRIMLPh8u6l6_e1k_lr7e4_mlp20l6_tanh_d00`

## 配置摘要

- **模型类型**: `FRIMLP`
- **训练轮数**: `epoch_train = 1000`
- **学习率**: `learning_rate = 0.0007`
- **自动学习率**: `use_auto_lr = false`
- **前端配置**: `H_UNITS = 8`, `IIR_INIT_BY_SYSTEM = true`, `USE_FAST_MODEL = true`
- **主体配置**: `model_subcfg = {mlp_hidden_units: 20, mlp_hidden_layers: 6, mlp_activation: tanh, output_activation: linear, dropout_rate: 0.0, dropout_position: inner, use_layer_norm: false}`
- **总参数量**: `2493`

## 最终结果

修复后该项目完整跑满 1000 epoch，并达到目标：

- **completed_epoch**: `1000`
- **weights_source**: `best_val`
- **min_val_loss**: `0.03868239372968674`
- **Freq Drift (Hz)**: `5.817886622907654`
- **Sens Drift (%)**: `27.48032651317834`
- **Linearity (%)**: `1.012014285777051`

这说明之前的主要瓶颈是架构接线错误，而不是“FRIMLP 这个方向天然不行”。

## 经验教训

1. 做 FRIKAN 系列消融时，先验证“前端是否还是同一前端”，再讨论指标。
2. 不要看到 fast_model 报错或指标异常，就直接把 `USE_FAST_MODEL` 关掉；先排查是不是接错了前端或漏做了系统初始化。
3. FRIMLP、FRIKAND 这类共用 FRI 前端的模型，训练前都要确认 `prepare_systems()` 是否真的被调用。
4. 如果结构级错误已经影响过历史训练产物，必须清空旧 `data/` 再重训，否则对比没有意义。
5. 时域 `val_loss` 不能直接替代频响三指标；即使 loss 变好，仍要以 `metrics.json` 为最终验收口径。

## 推荐排查顺序

1. 先看 `model_info.json`，确认 `simoiir` 输出维度是否符合 `H_UNITS`。
2. 再看 fast_model 是否存在，以及输入宽度是否与前端特征数一致。
3. 然后确认 `training_state.json` 和 `training_info.json` 是否来自修复后的全新训练。
4. 最后再以 `metrics.json` 判断 `Freq Drift`、`Sens Drift` 与 `Linearity`。