# 训练功能说明

## 功能概述

`python cli.py -t PROJECT_NAME` 用于训练 MET Nonlinear 模型，支持实时进度监控、权重保存和训练日志记录。

## 训练流程

1. **数据集加载** - 根据 `config.json` 中的 `dataset_type` 加载数据集
2. **模型构建** - 初始化模型结构（FRIKAN/WNET5/LSTM/1DCNN/TCN 等）
3. **训练执行** - 使用 TensorFlow Keras 进行训练，支持实时回调
4. **权重保存** - 自动保存最佳验证权重和最终权重
5. **下游评估** - 训练成功结束后自动串联执行一次 `-e`，生成当前权重对应的评估产物
6. **统一汇总** - 评估成功结束后自动刷新 `metrics.json`

## 配置参数

在项目 `config.json` 中配置：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `epoch_train` | 训练轮数 | - |
| `dataset_type` | 数据集类型（如 MET_COMP） | - |
| `use_model` | 模型类型（FRIKAN/WNET5/LSTM/1DCNN/TCN 等） | - |
| `H_UNITS` | 隐藏单元数 | - |
| `use_train_model` | 是否使用训练模式 | true |
| `adjust_weight` | 是否启用交互式权重调整 | false |

## 训练前检查

- 启动前先核对 `config.json`、数据路径、目标项目路径和 Python 环境是否一致，避免无效启动。
- 做超参数搜索时优先一次只跑一个项目，避免 GPU/IO 争抢导致结论失真。
- 每次调参都必须先复制同类项目为新的 project 变体，只在新项目里改 `learning_rate`、`model_subcfg` 或其他目标参数；禁止直接覆盖已有项目的 `config.json` 或复用已有 `data/` 继续试不同配置。
- 禁止自动批量 sweep 调参；每轮都要先读取上一轮项目的 `metrics.json`、`training_info.json` 或关键图表，再决定下一轮只改哪个 `learning_rate` 或 `model_subcfg` 方向。
- 调参优先做单因素变更，确保结果可解释且便于回退。
- 新增训练经验时优先沉淀可复用规律、限制条件和止损信号，而不是一次性流水账。
- 数据集覆盖、稳态片段、低震级样本平衡和外推边界的长期规则，详见 [docs/reference/dataset_design.md](docs/reference/dataset_design.md)。
- 如果当前实验属于真实卷积时序基线，请先按 [docs/reference/conv_sequence_baselines.md](docs/reference/conv_sequence_baselines.md) 核对 canonical 项目路径与 `use_model` 语义，再开始复制变体或重训。

## 特征缓存与序列起始段

- 特征缓存键必须覆盖所有会影响特征结果的参数；如果改了时间步、频点列表、数据裁剪长度或其他特征生成条件，却仍命中旧 cache，训练与评估就可能在不同机器上出现“同配置不同结果”的假复现。
- 如果 `-t` 的结果在训练后看起来正常，但 `-e` 只能在某台机器或某份旧 cache 上复现，优先排查特征缓存来源和生成口径，不要先把问题归因于模型随机性。
- 序列开头若缺少足够历史窗口，最前面的特征往往天然不完整；遇到扫频结果起始段异常时，优先在特征生成阶段跳过不完整窗口，而不是直接继续调模型。
- 对带明显历史依赖的模型，序列起始段的异常通常属于冷启动或上下文不足问题，验收时不要只盯最开始那一小段波形。

## 复现约束

- 历史 project 原样复跑优先保持旧行为，默认训练路径不为单个实验引入新的 batch-size 估算逻辑。
- 调参、消融和横评扩展时必须复制出新的 project 目录保存独立权重与日志，禁止在已有 project 上反复覆盖配置后重训。
- 不在共享代码路径中增加 `MAX_BATCH_SIZE`、兼容开关或仅针对单个项目生效的 batch-size 特判。
- 如果需要探索新的 batch-size 策略，应复制新项目或在独立分支中验证，避免破坏旧实验对比。
- 已归档实验的复盘以项目 `config.json`、`training_log.jsonl` 和 `training_info.json` 为准。
- CNNKAN 替换稳定案例详见 [docs/reference/cnnkan_ablation.md](docs/reference/cnnkan_ablation.md)。

## 训练过程判断与止损

- 训练过程不要只看终端表面输出，应同时检查 `training_state.json`、`training_log.jsonl` 和 `training_info.json`。
- 训练异常中断后，先检查残留进程以及 `training_state.json.training_alive`，再决定是否续训。
- 续训前必须确认实际加载的 checkpoint 与当前配置一致，否则可能从错误权重继续训练。
- 如果某个变体在前几十个 epoch 已明显落后于当前最优同区间轨迹，应及时止损，不必机械跑满预设 epoch。
- 只有在单轮结果已经稳定领先时，才值得继续向周边超参数扩展搜索。

## FRIMLP / FRIKAND 消融经验

- 做 FRIKAN 系列局部消融时，先守住语义等价：前端、fast_model 和系统初始化路径不要顺手改掉。
- `H_UNITS` 对 FRIMLP/FRIKAND 仍表示前端输出通道数；如果结构输出和这个语义不一致，先检查 `prepare_systems()` 与前端接线。
- 一旦确认历史训练产物来自错误架构，必须先清空项目 `data/` 再重训，不能直接续训或沿用旧指标。
- 通用结构取舍规则见 [docs/reference/model_architecture_selection.md](docs/reference/model_architecture_selection.md)，FRIMLP 真消融修复过程见 [docs/reference/frimlp_ablation.md](docs/reference/frimlp_ablation.md)。

## CNNKAN h8u6l6 调参经验

- CNNKAN 变体的卷积超参应优先写入 `model_subcfg`，不要依赖顶层硬编码参数。
- 8k 长序列在 RTX 2060 6GB 上训练时必须设置 `MAX_BATCH_SIZE=4`，否则初始评估或训练阶段很容易 OOM。
- 把 `cnn_kernel_size` 从 `3` 提到 `5` 是这一轮最有效的单因素改动。
- 结构定位上，CNNKAN 更适合作为主体替换或局部模式提取实验，不应默认替代线性谐振先验；详见 [docs/reference/model_architecture_selection.md](docs/reference/model_architecture_selection.md)。
- 具体稳定项目、学习率区间和调参背景见 [docs/reference/cnnkan_ablation.md](docs/reference/cnnkan_ablation.md) 与 [docs/reference/lr_tuning_fixed_vs_cosine.md](docs/reference/lr_tuning_fixed_vs_cosine.md)。

## 输出文件

训练完成后在 `projects/PROJECT_NAME/data/` 目录下生成：

- `best_val.weights.h5` - 最佳验证权重
- `best.weights.h5` - 最终权重
- `training_log.jsonl` - 训练日志（loss, val_loss, lr, epoch）
- `training_info.json` - 训练统计摘要
- `model_info.json` - 模型结构信息

## 下游串联

- `python cli.py -t PROJECT_NAME` 成功结束后，会先清理当前项目中已经过期的评估汇总快照，包括 `metrics.json`、`linear_response.json`、`linearity_by_frequency.json`，并移除 `training_info.json.evaluation_metrics`。
- 随后 CLI 会自动串联执行一次评估流程，相当于对同一项目继续执行 `python cli.py -e PROJECT_NAME`。
- 由于 `-e` 已内置自动刷新 `metrics.json`，因此 `-t` 完整成功后也会得到与当前权重一致的最新统一指标，不需要再额外手动补跑 `--metrics`。
- 如果训练成功但下游评估失败，旧 summary 已经被失效，CLI 会直接报错，此时应按评估失败处理，而不是继续信任旧的 `metrics.json`。

## 训练监控

训练过程支持：
- 实时 loss 显示
- 平滑速度估算（指数移动平均）
- 剩余时间预测
- 验证 loss 追踪

## GPU 选择与恢复

训练命令在导入 TensorFlow 之前会执行 CUDA 预检查：

- 多卡健康时，默认优先级为 `RTX 2080 Ti > RTX 3090 > 其他 GPU`
- 检测到 `GPU is lost` 时，会自动屏蔽异常 GPU 或回退 CPU
- 当设备进入 `已断开连接` 状态时，应转向设备级重启、冷启动或硬件排查

详见 [docs/reference/gpu_recovery.md](docs/reference/gpu_recovery.md)。

## 相关命令

- `python cli.py -e PROJECT_NAME` - 单独评估已训练模型
- `python cli.py --loss-plot PROJECT_NAME` - 绘制训练 loss 曲线
