# 训练功能说明

## 功能概述

`python cli.py -t PROJECT_NAME` 用于训练 MET Nonlinear 模型，支持实时进度监控、权重保存和训练日志记录。

## 训练流程

1. **数据集加载** - 根据 `config.json` 中的 `dataset_type` 加载数据集
2. **模型构建** - 初始化模型结构（FRIKAN/WNET5/LSTM等）
3. **训练执行** - 使用 TensorFlow Keras 进行训练，支持实时回调
4. **权重保存** - 自动保存最佳验证权重和最终权重
5. **评估输出** - 输出训练集/验证集的 loss、MAE、AFMAE 指标

## 配置参数

在项目 `config.json` 中配置：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `epoch_train` | 训练轮数 | - |
| `dataset_type` | 数据集类型（如 MET_COMP） | - |
| `use_model` | 模型类型（FRIKAN/WNET5/LSTM） | - |
| `H_UNITS` | 隐藏单元数 | - |
| `use_train_model` | 是否使用训练模式 | true |
| `adjust_weight` | 是否启用交互式权重调整 | false |

## 训练前检查

- 启动前先核对 `config.json`、数据路径、目标项目路径和 Python 环境是否一致，避免无效启动。
- 做超参数搜索时优先一次只跑一个项目，避免 GPU/IO 争抢导致结论失真。
- 调参优先做单因素变更，确保结果可解释且便于回退。
- 新增训练经验时优先沉淀可复用规律、限制条件和止损信号，而不是一次性流水账。

## 复现约束

- 历史 project 原样复跑优先保持旧行为，默认训练路径不为单个实验引入新的 batch-size 估算逻辑。
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

## CNNKAN h8u6l6 调参经验

- CNNKAN 变体的卷积超参应优先写入 `model_subcfg`，不要依赖顶层硬编码参数。
- 8k 长序列在 RTX 2060 6GB 上训练时必须设置 `MAX_BATCH_SIZE=4`，否则初始评估或训练阶段很容易 OOM。
- `projects/01_LR_STUDY/CNNKANh8u6l6_e1k_lr25e5_c8k3d05` 跑满 1000 epoch 后 `min_val_loss=0.044458`，可作为该系列的稳定早期基线。
- `projects/01_LR_STUDY/CNNKANh8u6l6_e1k_lr28e5_c8k3d05` 通过修复后的断点续训跑满后 `min_val_loss=0.03916`，说明 `0.00028` 比 `0.00025` 更有潜力。
- `projects/01_LR_STUDY/CNNKANh8u6l6_e1k_lr29e5_c8k3d05` 最终仅到 `min_val_loss=0.075819`，说明继续上调学习率已越过当前最优区间。
- `projects/01_LR_STUDY/CNNKANh8u6l6_e1k_lr28e5_c8k3d03` 最终仅到 `min_val_loss=0.12905`，说明当前配置下减小 `dropout_rate` 会明显恶化结果。
- 把 `cnn_kernel_size` 从 `3` 提到 `5` 是这一轮最有效的单因素改动。
- `projects/01_LR_STUDY/CNNKANh8u6l6_e1k_lr28e5_c8k5d05` 跑满 1000 epoch 后 `min_val_loss=0.028127`，是当前已验证的最佳配置。
- 相关背景与实验上下文可结合 [docs/reference/cnnkan_ablation.md](docs/reference/cnnkan_ablation.md) 和 [docs/reference/lr_tuning_fixed_vs_cosine.md](docs/reference/lr_tuning_fixed_vs_cosine.md) 一起阅读。

## 输出文件

训练完成后在 `projects/PROJECT_NAME/data/` 目录下生成：

- `best_val.weights.h5` - 最佳验证权重
- `best.weights.h5` - 最终权重
- `training_log.jsonl` - 训练日志（loss, val_loss, lr, epoch）
- `training_info.json` - 训练统计摘要
- `model_info.json` - 模型结构信息

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

- `python cli.py -e PROJECT_NAME` - 评估已训练模型
- `python cli.py --loss-plot PROJECT_NAME` - 绘制训练 loss 曲线
