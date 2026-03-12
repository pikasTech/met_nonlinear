# 2026-03-12 FRIKANh8u6l6 继续训练框架调研

## 结论

- 当前框架本身支持两类“继续训练”：
  1. 同一项目断点续训：依赖 `resume_training=true`、`data/best.weights.h5`、`data/training_state.json`
  2. 新项目分阶段继承训练：依赖 `base_project`，先加载上一阶段的最佳权重，再从新项目配置继续训练
- `FRIKANh8u6l6` 在“模型结构兼容性”层面是支持继续训练的；`FRIKAN` 构建流程与 `LSTMu32al_rs300_ex` 使用的通用训练框架一致。
- 但 `FRIKANh8u6l6` 当前项目目录里的训练状态文件不完整，不能视为“可靠可恢复断点”。如果直接按现状继续训练，框架更像是“加载最佳权重后重新从 epoch 0 计数训练”，而不是严格续接到历史 epoch。

## 代码链路

### 1. 同项目断点续训机制

- `ProjectManager.process()` 会调用 `ModelEngine.train_model()`：`src/core/project_manager.py:38`
- `train_model()` 在 `resume_training=true` 时，会优先加载 `best.weights.h5`：`src/core/model_engine.py:603`
- 实际训练轮数使用：

```python
epochs = self.config.epoch_train - self.state_manager.get('completed_epoch', 0)
```

对应位置：`src/core/model_engine.py:636`

- 学习率调度器也会读取 `completed_epoch`，用于从历史步数继续衰减：`src/core/model_engine.py:411`
- 每个 epoch 结束时，`RealTimeTrainingCallback` 会把 `completed_epoch += 1` 写回 `training_state.json`：`src/core/training.py:128`
- 初始状态文件默认包含 `completed_epoch` 字段：`src/core/training_state.py:27`

### 2. 分阶段继承训练机制（类似 LSTMu32al_rs300_ex）

- 如果配置了 `base_project`，构模后会调用 `load_base_model_weights()`：`src/core/project_manager.py:88`
- 该逻辑会从上一阶段项目复制/加载 `best_val.weights.h5` 与 `best.weights.h5`，但不会复制 `training_state.json`：`src/core/project_manager.py:115`
- 因此这种方式本质是“权重继承 + 新项目重新计数训练”，不是严格意义的同项目断点恢复。
- 历史文档中 `LSTMu32al_rs300_ex -> ex2 -> ex3` 也是通过 `base_project` 串联：`src/archive_legacy/lstm_alas.md:324`、`src/archive_legacy/lstm_alas.md:343`

## FRIKANh8u6l6 当前状态

### 1. 支持继续训练的正面证据

- 配置中已启用 `resume_training=true`：`projects/FRIKANh8u6l6/config.json:10`
- 现有权重文件存在：
  - `projects/FRIKANh8u6l6/data/best.weights.h5`
  - `projects/FRIKANh8u6l6/data/best_val.weights.h5`
  - `projects/FRIKANh8u6l6/data/fast_best.weights.h5`
  - `projects/FRIKANh8u6l6/data/fast_best_val.weights.h5`
- 模型信息文件表明当前结构已固定为 `FRIKAN + 8 个 IIR 特征 + 6 层 inner KAN`：`projects/FRIKANh8u6l6/data/model_info.json:2`

### 2. 阻碍严格断点恢复的问题

- `projects/FRIKANh8u6l6/data/training_state.json` 缺少最关键的 `completed_epoch` 字段：`projects/FRIKANh8u6l6/data/training_state.json:1`
- 该文件同时出现明显不一致现象：
  - `current_epoch=19`，但框架真正用于续训的是 `completed_epoch`
  - `expected_finish_time` 为 2025，但时间戳是 2026
  - `model_name` 记录为 `FRIKAN`，不是项目名
- 相比之下，`projects/LSTMu32al_rs300_ex/data/training_state.json` 含有完整的 `completed_epoch=11480`，这才符合当前框架的续训预期：`projects/LSTMu32al_rs300_ex/data/training_state.json:2`
- `projects/FRIKANh8u6l6/data/training_log.jsonl` 目前只记录到 19 个 epoch：`projects/FRIKANh8u6l6/data/training_log.jsonl:1`
- 因为 `completed_epoch` 缺失，当前代码会在两个关键点退化为“从 0 开始计数”：
  - 学习率调度 `step_begin = 0`
  - 训练 epochs 计算等价于 `epoch_train - 0`

## 与 LSTMu32al_rs300_ex 的差异

- `LSTMu32al_rs300_ex` 更像“规范状态下的同项目续训样本”：有完整 `training_state.json`，可按历史 epoch 续接：`projects/LSTMu32al_rs300_ex/data/training_state.json:2`
- `LSTMu32al_rs300_ex` 同时也是后续多阶段项目的基础项目，靠 `base_project` 向下游项目传递权重：`projects/LSTMu32al_rs300_ex/config.json:2`
- `FRIKANh8u6l6` 当前没有 `base_project`，所以它现在更适合被视为“要么修复本项目断点状态继续训，要么作为新的 base_project 起点”。

## 对 FRIKANh8u6l6 的判断

- 如果目标是“像 `LSTMu32al_rs300_ex` 一样直接在当前项目上继续训练”，当前框架理论支持，但 `FRIKANh8u6l6` 的状态文件不够完整，可靠性不足。
- 如果目标是“像 `LSTMu32al_rs300_ex -> ex2` 那样开一个新阶段项目继续微调”，当前框架支持，而且路径更清晰：
  - 新项目配置兼容的 `FRIKAN` 结构
  - 设置 `base_project = "FRIKANh8u6l6"`
  - 调整新的学习率、衰减周期、训练轮数
  - 这样会继承现有最佳权重，但训练计数从新项目重新开始

## 建议

### 推荐路线

- 更推荐采用“新阶段项目继承训练”的方式，而不是直接依赖 `FRIKANh8u6l6` 当前的 `training_state.json`。
- 原因：现有断点状态文件已表现出字段缺失和时间不一致，继续直接复用会让学习率调度和 epoch 统计失真。

### 若后续要实施

- 方案 A：新建类似 `FRIKANh8u6l6_ex` 的项目，用 `base_project="FRIKANh8u6l6"` 做第二阶段训练
- 方案 B：先修复 `FRIKANh8u6l6/data/training_state.json`，补齐 `completed_epoch` 并确认其与真实训练日志一致，再走同项目断点续训

### 需要重点核对的参数

- `use_model`
- `H_UNITS`
- `INNER_KAN_UNITS`
- `INNER_KAN_LAYERS`
- `GRID_SIZE`
- `SPLINE_ORDER`
- `basis_activation`
- `IIR_TRAINABLE`
- `IIR_INIT_BY_SYSTEM`

以上参数若变化，会影响旧权重是否能无缝加载。

## 2026-03-12 实施更新

- 已对 `src/core/training_state.py` 做最小兼容性修改，使旧项目训练状态在缺少 `completed_epoch` 时，自动回退使用 `current_epoch`
- 兼容逻辑同时会补齐缺失的 `current_epoch`、`model_name`、`training_alive` 字段，并回写到原 `training_state.json`
- 为避免新旧字段再次漂移，后续只更新 `completed_epoch` 时会同步刷新 `current_epoch`，反之亦然
- 该修改的目的不是改变新项目行为，而是让 `FRIKANh8u6l6` 这类旧项目具备“可恢复、可再微调”的最小后向兼容能力

## 新建微调项目

- 已创建 `projects/FRIKANh8u6l6_ex/config.json:1`
- 配置策略参考 `LSTMu32al_rs300_ex2` 的二阶段微调思路，但保留 `FRIKANh8u6l6` 原有结构参数不变
- 关键调整如下：
  - `base_project = "FRIKANh8u6l6"`
  - `learning_rate = 0.002`（从原始 `0.01` 下调）
  - `auto_lr_decay_steps = 5000`（放慢衰减，适合微调）
  - `RESTART_AFTER_N_CYCLES = 300`（降低频繁重启对微调稳定性的影响）
  - `use_best_val_weights = false`（训练阶段优先按 base project 继承逻辑加载）

## 推荐使用方式

- 若希望直接在旧项目上续训：使用 `FRIKANh8u6l6`，现在会兼容旧版 `training_state.json`
- 若希望更稳妥地做二阶段微调：使用 `FRIKANh8u6l6_ex`，保持原项目结果不被覆盖

## 2026-03-12 方案澄清

- 最终采用的是“二阶段微调项目”方案，不直接改动旧项目 `FRIKANh8u6l6` 的项目状态文件
- 为兼容旧项目来源带来的历史状态差异，只保留了框架级最小兼容：`src/core/training_state.py:39`
- 实际微调入口仍应使用 `projects/FRIKANh8u6l6_ex/config.json:1`

## 2026-03-12 AFMSE 扩展

- 按照“AF 表示幅频”的定义，新增了纯 `af_mse_loss`：`src/core/loss_functions.py:219`
- 该损失只保留幅频能量对数项，不包含 MAE 项，计算方式是：
  - 先按组求 `power_true` / `power_pred`
  - 再取 `log(power + 1e-8)`
  - 最后对差值做平方并全局平均
- 也就是把 `power_log_loss` 里的
  - `tf.abs(power_true_log - power_pred_log)`
  - 改成 `tf.square(power_true_log - power_pred_log)`
- 在 `src/core/model_engine.py:424` 的 `loss_type` 选择中新增：
  - `af_mse`
  - `afmse`
- 已删除先前误加的 `power_log_mse_loss`，避免与纯 AFMSE 概念混淆
- 原有默认行为不变：未设置 `loss_type` 时，仍按 `use_power_loss` 决定是否使用 `power_log_mae_loss`

## 新建 AFMSE 微调项目

- 已创建 `projects/FRIKANh8u6l6_ex_afmse/config.json:1`
- 该项目基于 `FRIKANh8u6l6` 做二阶段微调，并显式设置：
  - `loss_type = "afmse"`
- 因此它现在使用的是纯 AFMSE，而不是包含 MAE 项的混合损失
