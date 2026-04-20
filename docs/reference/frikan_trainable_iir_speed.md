# FRIKAN Trainable-IIR 速度排查

## 适用范围

本页用于排查 `FRIKAN` 在 `IIR_TRAINABLE = true`、`USE_FAST_MODEL = true` 一类变体中的训练速度异常，尤其是：

- 标准 FRIKAN 基线训练速度正常，但某些 trainable-IIR / true-IIR 变体突然只有几十 `epoch/h`
- native Windows `tf26` 环境近期改过 GPU allocator、allow-growth 或前台训练入口，怀疑环境层导致整体训练变慢
- 需要区分“环境全局变慢”和“当前模型语义更重导致局部变慢”

## 核心结论

- 先用标准 FRIKAN 做同机、同环境、前台 `-t` 的 1 分钟测速，再判断是否是环境问题。
- 如果标准 FRIKAN 在进入 epoch 循环后仍能维持 `>1000 epoch/h`，则 `tf26`、GPU、默认 allocator 和前台训练链路通常仍是健康的，不应把某个慢速 trainable-IIR 变体首先归因于 allocator。
- 对 `IIR_TRAINABLE = false` 的固定 IIR 前端，`fast_model` 可以先预计算 `fast_iir(x)` 特征后再训练，因此速度通常明显更高。
- 对 `IIR_TRAINABLE = true` 的语义正确训练路径，IIR 必须留在训练图里参与反向传播；这会天然比“预计算特征再训练”的旧快路径慢。
- 对 `IIR_TRAINABLE = true` 的训练路径，IIR 实现必须保持 `SIMOIIR` 语义；`DIAGIIR` 只适用于块对角结构成立的并行加速实现，不应用作可训练 IIR 的主训练层。
- `MAX_BATCH_SIZE` 会直接改变每个 epoch 的 step 数，常常是 trainable-IIR 变体训练速度骤降的第一可调因素。

## 推荐排查顺序

### 1. 先做标准 FRIKAN 1 分钟对照测速

使用标准 FRIKAN 基线项目复制出的测速副本，前台直接执行 `python cli.py -t PROJECT_NAME`，只跑约 1 分钟。

判定规则：

- 若训练循环内已经回到 `>1000 epoch/h`，说明当前机器的 TensorFlow / GPU / CLI 前台训练主链路基本正常。
- 若标准 FRIKAN 也只有几十 `epoch/h`，才继续沿环境、GPU 坏状态、allocator 或全局代码回归方向排查。

注意：

- 1 分钟测速必须以前台方式直接执行。
- 前 20~30 秒往往包含 TensorFlow 初始化、数据加载、模型构建和初始评估，`training_state.json.smoothed_speed` 会被这些启动开销拉低。
- 读速度时要同时参考终端滚动日志、`training_state.json.smoothed_speed` 和 `training_log.jsonl` 按 epoch 时间戳重算的区间速度。

## 2. 再比较同一变体是否被 `MAX_BATCH_SIZE` 限速

`ModelEngine.prepare_training_data()` 中，默认 batch-size 口径为：

```text
batch_size = floor(seq_num / step_per_epoch)
```

若项目设置了 `MAX_BATCH_SIZE`，则实际 batch-size 会被进一步截断为：

```text
batch_size = min(batch_size, MAX_BATCH_SIZE)
```

因此应优先比较：

- 当前慢速变体
- 仅去掉 `MAX_BATCH_SIZE` 的同配置变体

如果 `seq_num` 不变，而 `MAX_BATCH_SIZE` 把 batch-size 从较大的自然值压到很小的值，就会显著增加每个 epoch 的 step 数，直接拉低 `epoch/h`。

## 3. 最后确认是否切换到了 trainable-IIR 的原始输入训练路径

固定 IIR 前端时，`fast_model.fit()` 可以直接消费预计算好的 IIR 特征。

而在 trainable-IIR 的语义正确路径中，`fast_model` 的输入应回到原始波形，由 IIR 层在图内参与训练。此时：

- 不应再把 IIR 当成固定特征预计算后缓存给 `fit()`
- 不应把 `DIAGIIR` 当成 trainable-IIR 的可训练替身；可训练路径必须直接复用 `SIMOIIR`
- 若为了复用 `fast_model` 而额外保留一份独立 IIR 权重，必须确保它与主模型是同一层或同一语义实现，避免训练和导出权重落在不同 IIR 上
- 训练图会比固定 IIR 前端更重
- 速度下降不一定是缺陷，也可能是“模型语义更完整”的代价

### 为什么 trainable-IIR 不能训练 `DIAGIIR`

`DIAGIIR` 的意义在于把多路独立 IIR 写成块对角并行实现。这个前提只有在各路状态转移和输入耦合都严格保持块对角时才成立，因此它适合作为固定 IIR 的并行计算形式。

一旦把这套块对角参数直接开放为可训练权重，训练过程并不会自动维护“对角外必须为零”的结构不变量；此时学到的递推矩阵已经不再等价于原本那组互不耦合的 IIR。继续把它解释成并行 IIR，会得到与 `SIMOIIR` 不一致的模型语义。

因此，trainable-IIR 的正确做法是：

- 训练时使用 `SIMOIIR` 参与前向和反向传播
- `DIAGIIR` 只保留给固定 IIR 的特征预计算或推理加速语境
- 比较 trainable-IIR 速度时，先确认比较对象没有偷偷切回 `DIAGIIR` 的错误快路径

因此，不能单纯因为旧项目更快，就把更快的旧路径视为正确实现。

## 4. 只有在标准基线也变慢时，才把 allocator 作为主嫌疑

若标准 FRIKAN 前台 1 分钟测速依然正常，则 allocator 更可能是“启动稳定性 / 崩溃风险”问题，而不是当前慢速变体从 `>1000 epoch/h` 掉到几十 `epoch/h` 的主因。

allocator 方向应优先处理的信号是：

- 训练尚未进入 epoch 循环就原生崩溃
- 没有 Python traceback，但系统事件里出现 `python.exe` / `ntdll.dll` / `0xc0000374`
- 加上某个 allocator 变量才崩，去掉后可恢复

这类情况详见 [docs/reference/tf26_environment.md](tf26_environment.md)。

## 速度优化的优先顺序

对 trainable-IIR / true-IIR 变体，优先按以下顺序尝试提速：

1. 先复制新 project，只调整 `MAX_BATCH_SIZE`
2. 仍然以前台 `-t` 运行 1 分钟测速，确认速度是否恢复
3. 若仍明显过慢，再检查当前是否必须保留 IIR 在图内训练
4. 只有在不破坏语义等价的前提下，才继续优化 fast path 或训练图

## 不应采取的做法

- 看到某个 trainable-IIR 变体只有几十 `epoch/h`，就直接认定是 allocator 把全局训练拖慢
- 为了恢复旧速度，重新回到“先预计算 IIR 特征再训练”的错误快路径
- 为了保留原始输入 fast path，而把 trainable-IIR 继续挂到 `DIAGIIR` 上训练
- 在共享代码路径里给单个实验偷偷加特判，却不复制成新的 project 变体
- 用后台、隐藏窗口或脱离当前会话的方式做测速

## 相关文档

- 前台训练与止损规则： [docs/reference/training.md](training.md)
- native Windows `tf26` / allocator 兼容性边界： [docs/reference/tf26_environment.md](tf26_environment.md)
