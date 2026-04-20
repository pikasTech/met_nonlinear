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
- native Windows 的 `tf26` 环境默认保持 `TF_GPU_ALLOCATOR` 未设置；如果加上 `TF_GPU_ALLOCATOR=cuda_malloc_async` 后出现 GPU 初始化后无 traceback 退出或 `python.exe` 原生崩溃，应先按环境 / allocator 不兼容处理，详见 [docs/reference/tf26_environment.md](docs/reference/tf26_environment.md)。
- 做超参数搜索时优先一次只跑一个项目，避免 GPU/IO 争抢导致结论失真。
- 训练命令应以前台可见方式直接执行 `python cli.py -t PROJECT_NAME`；禁止使用 `Start-Process`、后台 `&`、`nohup`、计划任务或其他脱离当前 Agent 会话的启动方式。
- 在 Agent Loop 或多轮调参流程中，训练结束后必须能自动回到当前会话继续读取结果并决定下一轮；如果训练被脱离到系统后台，只留下日志文件而不附着在当前会话上，后续调参链路会直接中断。
- 每次调参都必须先复制同类项目为新的 project 变体，只在新项目里改 `learning_rate`、`model_subcfg` 或其他目标参数；禁止直接覆盖已有项目的 `config.json` 或复用已有 `data/` 继续试不同配置。
- 禁止自动批量 sweep 调参；每轮都要先读取上一轮项目的 `metrics.json`、`training_info.json` 或关键图表，再决定下一轮只改哪个 `learning_rate` 或 `model_subcfg` 方向。
- 调参优先做单因素变更，确保结果可解释且便于回退。
- 新增训练经验时优先沉淀可复用规律、限制条件和止损信号，而不是一次性流水账。
- 数据集覆盖、稳态片段、低震级样本平衡和外推边界的长期规则，详见 [docs/reference/dataset_design.md](docs/reference/dataset_design.md)。
- 如果当前实验属于真实卷积时序基线，请先按 [docs/reference/conv_sequence_baselines.md](docs/reference/conv_sequence_baselines.md) 核对 canonical 项目路径与 `use_model` 语义，再开始复制变体或重训。

## 前台可见训练约束

- 只有 `python cli.py -t PROJECT_NAME` 仍附着在当前可见终端、并持续占用当前 Agent 会话时，才算“正在训练”。
- 如果父命令已经返回、外层 shell/tool 已超时、当前会话看不到实时输出，但磁盘上的 `training_log.jsonl` 还在继续增长，这种情况仍按“后台残留进程”处理，不得宣称为前台训练。
- shell 超时后幸存的子进程、仅写日志文件的隐藏任务、`Start-Process` 启动的新窗口、计划任务或其他脱离当前会话的运行方式，都不满足前台训练约束。
- 如果当前环境没有附着的可见终端，就不要声称“已经在前台训练”；应先建立可见终端，再启动训练命令。
- 调参链路里的“继续训练”“等待训练结束”“读取当前进度”都以当前可见会话中的前台命令为准，而不是只看 `training_state.json` 上一次写回的状态。
- 当前 CLI 训练入口需要监控父会话是否仍然存在；如果启动它的前台 shell 已退出或被工具超时回收，训练进程也应立即自终止并把状态回写为非运行中，避免留下不可见后台残留。

## 已知重大缺陷与修复约束

- 旧版 CLI 训练入口曾在 `python cli.py -t PROJECT_NAME` 下额外套一层 `multiprocessing` 训练/绘图子进程包装；这会破坏前台可见性，并且在部分 Windows 当前会话调用链里触发无 Python traceback 的原生崩溃。
- 因此前台训练的正确实现是：CLI 直接在当前进程调用 `ProjectManager.process()`，让训练日志、异常、`training.lock` 生命周期和训练结束后的自动 `-e` 串联都绑定在同一前台命令上。
- 如果再次出现“TensorFlow/GPU 初始化后进程直接消失、没有 traceback、`training_alive` 仍为 false、`training.lock` 没有稳定存在”的现象，应优先按“CLI 启动链路/可见性缺陷”排查，而不是先把问题归因于模型结构或数据集。
- 实时曲线、自动重启或其他额外监控机制若需要存在，不能默认通过脱离当前会话的子进程来承载训练主流程；否则即使磁盘日志继续写入，也不满足本项目的前台训练定义。

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
- 终端可见输出是调参工作流的一部分：它既用于实时观察异常，也用于让 Agent 在命令结束时自动继续后续判断，不能用“仅写日志文件、前台立即返回”的方式替代。
- 训练异常中断后，先检查残留进程、`training.lock` 和 `training_state.json.training_alive`，再决定是否续训。
- 如果训练被强停或外层会话异常退出，且实际训练进程已不存在，就应把残留 `training.lock` / 失真的 `training_alive` 视为过期状态；先清理到“无锁、无残留进程、状态可重新加载”的一致状态，再重新前台启动或续训。
- 续训前必须确认实际加载的 checkpoint 与当前配置一致，否则可能从错误权重继续训练。
- 如果某个变体在前几十个 epoch 已明显落后于当前最优同区间轨迹，应及时止损，不必机械跑满预设 epoch。
- 只有在单轮结果已经稳定领先时，才值得继续向周边超参数扩展搜索。
- 如果标准 FRIKAN 前台 1 分钟测速仍能回到 `>1000 epoch/h`，而某个 trainable-IIR / true-IIR 变体只有几十 `epoch/h`，应优先按 fast path 语义和 `MAX_BATCH_SIZE` 方向排查，而不是先归因于 allocator；详见 [docs/reference/frikan_trainable_iir_speed.md](docs/reference/frikan_trainable_iir_speed.md)。
- 对 `IIR_TRAINABLE = true` 的 FRIKAN 路径，训练图里的 IIR 应保持 `SIMOIIR` 语义；`DIAGIIR` 只能用于固定 IIR 的并行加速或特征预计算，详见 [docs/reference/frikan_trainable_iir_speed.md](docs/reference/frikan_trainable_iir_speed.md)。

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
