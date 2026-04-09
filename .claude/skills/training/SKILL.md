---
name: training
description: 在进行 cli.py -t 训练和超参数调参时必须加载本 SKILL
---

# 训练技能

- 通用训练指导
  - 开始训练前先确认 `config.json`、数据路径、目标 project 路径和 Python 环境是一致的，避免把时间浪费在无效启动上。
  - 做超参数搜索时应优先一次只跑一个 project，这样更容易基于真实结果及时止损并避免资源争抢。
  - 判断一个变体是否值得继续时应同时看 `training_state.json`、`training_log.jsonl` 和 `training_info.json`，不要只看终端表面输出。
  - 训练异常中断后应先检查残留进程和 `training_state.json` 的 `training_alive`，再决定是否续训。
  - 续训逻辑必须确认实际加载的 checkpoint 与配置一致，否则恢复训练可能从错误权重起步。
  - 调参时应优先做单因素变更，这样实验结果才有可解释性且便于快速回退。
  - 如果某个变体在前几十个 epoch 已明显落后于当前最优同区间轨迹，就应尽早止损而不是机械跑满预设 epoch。
  - 只有在单轮结果已经稳定领先时才值得继续扩展邻域搜索，否则先收口当前最优更划算。
  - 新增训练经验时应优先记录可复用的规律、限制条件和止损信号，而不是堆砌一次性的流水账。

- CNNKAN h8u6l6 专项经验
  - CNNKAN 变体的卷积超参应优先写入 `model_subcfg`，不要再依赖顶层硬编码参数。
  - 8k 长序列在 RTX 2060 6GB 上训练时必须设置 `MAX_BATCH_SIZE=4`，否则初始评估或训练过程很容易 OOM。
  - `projects/01_LR_STUDY/CNNKANh8u6l6_e1k_lr25e5_c8k3d05` 跑满 1000 epoch 后 `min_val_loss=0.044458`，可作为这一系列实验的稳定早期基线。
  - `projects/01_LR_STUDY/CNNKANh8u6l6_e1k_lr28e5_c8k3d05` 通过修复后的断点续训跑满后 `min_val_loss=0.03916`，说明 `0.00028` 比 `0.00025` 更有潜力。
  - `projects/01_LR_STUDY/CNNKANh8u6l6_e1k_lr29e5_c8k3d05` 最终只到 `min_val_loss=0.075819`，说明继续上调 lr 已经越过最优区间。
  - `projects/01_LR_STUDY/CNNKANh8u6l6_e1k_lr28e5_c8k3d03` 最终只到 `min_val_loss=0.12905`，说明在当前配置下减小 `dropout_rate` 会明显恶化结果。
  - 把 `cnn_kernel_size` 从 `3` 提到 `5` 是这轮最有效的单因素改动，因为它把最优结果推进到了新的量级。
  - `projects/01_LR_STUDY/CNNKANh8u6l6_e1k_lr28e5_c8k5d05` 跑满 1000 epoch 后 `min_val_loss=0.028127`，是当前已验证的最佳配置且已达到 0.03 以下目标。