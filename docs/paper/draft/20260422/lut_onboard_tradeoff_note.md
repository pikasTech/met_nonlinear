# Wiener-KAN LUT 部署权衡专题过程稿

## 写作目标

本稿用于收束 Wiener-KAN 在 STM32F405 上不同导出实现的最终对比结论，服务于 `3.4 On board 推理性能评估` 与 `3.6 Wiener-KAN 的 LUT 实现取舍` 两节。

本稿只保留当前可直接进入总稿的稳定结论：比较对象、正式口径、自动复验后的最终数据和建议写法，不展开一次性的串口抓取与中间调试细节。

## 1. 比较对象与语义边界

当前专题实验固定同一个训练模型：

- `projects/01_LR_STUDY/FRIKANh8u6l6_e1k_lr7e4`

围绕这一训练项目，比较三种 MCU 导出实现：

1. `LUT nearest`
   - `use_lut = true`
   - `lut_interpolation = false`
2. `LUT + interp`
   - `use_lut = true`
   - `lut_interpolation = true`
3. `No LUT exact`
   - `use_lut = false`

因此，这组实验比较的是**同一训练权重下的部署实现取舍**，而不是训练模型横评。

## 2. 当前正式取值口径

当前正文应统一引用以下稳定来源：

- `QEMU-MAE` / `KEIL-MAE`
  - 来源：各 EP 的 `benchmark_summary.json` 与 `keil_benchmark_summary.json`
- `KEIL speed (Points/s)`
  - 来源：`keil_benchmark_summary.json` 中 published/default profile 的单位点 wall-time 换算
- Flash / RAM
  - 对多优化档任务，优先取 published/default profile 聚合结果
  - 不再直接取“最后一次 build_output 覆盖后的当前工程状态”

这一定义非常重要，因为最近一轮 `keil-bench` 已支持多优化档 sweep；若直接读当前 `build_output_MET405.txt`，会把 `-Ofast + LTO` 的体积误当成默认 published 结果。

## 3. 自动复验后的最终结果

### 3.1 最近邻 LUT（published/default）

- `QEMU-MAE = 7.114e-03`
- `KEIL-MAE = 7.114e-03`
- `KEIL speed = 6986.7 Points/s`
- `Flash = 719.2 KB`
- `RAM = 5.6 KB`

这组数字来自自动 `ex` 任务复验后的 published/default profile，不再沿用早期手动验算阶段的 `6048.701 Points/s` 中间值。

### 3.2 LUT + 一阶线性插值

- `QEMU-MAE = 1.902e-04`
- `KEIL-MAE = 1.902e-04`
- `KEIL speed = 3844.8 Points/s`
- `Flash = 723.5 KB`
- `RAM = 5.6 KB`

与最近邻 LUT 相比：

- `KEIL-MAE` 进一步降低约 `97.33%`
- 吞吐保留约 `55.0%`
- Flash 仅增加约 `0.60%`

因此，插值版仍然是当前**精度 / 速度**最平衡的实现。

### 3.3 非 LUT 精确路径

- `QEMU-MAE = 6.517e-07`
- `KEIL-MAE = 6.517e-07`
- `KEIL speed = 45.0 Points/s`
- `Flash = 33.7 KB`
- `RAM = 21.2 KB`

这一路径更适合作为数值一致性的参考上界，而不是默认实时部署方案。

## 4. 最近一轮优化真正改变了什么

本轮优化的核心不是“再调一档编译器开关”，而是把 LUT 路径里原本明显低效的实现改成了更接近板端真实访问模式的写法：

1. LUT 存储改为按层精确尺寸落盘，显著压缩体积；
2. LUT 模型使用 benchmark-only 的专用 KAN/LUT 前向核心；
3. LUT 模型使用 benchmark-only 的 IIR 展开前端；
4. 这些收益对所有 `use_lut = true` 的路径共享，因此最近邻 LUT 与 `LUT + interp` 都同步受益。

这也是为什么最近邻 LUT 会从旧稿中的 `1861.9 Points/s` 提升到当前 `6986.7 Points/s`，而插值版也同步提升到 `3844.8 Points/s`。

同一轮补跑还额外确认：这种共享不仅发生在“最近邻 LUT / 插值 LUT”两种导出实现之间，也发生在**同结构但不同 loss 的 Wiener-KAN 训练变体**之间。对以下两个 loss 消融项目重新执行自动 QEMU/Keil 后：

- `projects/01_LR_STUDY/FRIKANh8u6l6_e1k_lr7e4_puremae`
- `projects/03_FRIKAN_PUREAFME/FRIKANh8u6l6_e1k_lr5e4_pureafmae`

它们的 published/default profile 都落在同一组部署资源与吞吐上：

- `KEIL speed = 6986.7 Points/s`
- `Flash = 719.2 KB`
- `RAM = 5.6 KB`

差异只体现在数值误差而不是部署开销：

- 纯 `MAE`：`QEMU-MAE = KEIL-MAE = 2.137e-02`
- 纯 `AFMAE`：`QEMU-MAE = KEIL-MAE = 3.968e-03`
- `MAE+AFMAE`：`QEMU-MAE = KEIL-MAE = 7.114e-03`

因此，loss 消融部分不应再写成“不同 loss 造成了明显不同的板端速度”；更准确的表述是：**在当前共享导出链下，loss 主要改变校准质量，不再显著改变同结构 Wiener-KAN 的最近邻 LUT 部署吞吐与资源占用。**

## 5. 多优化档 benchmark 的工程结论

当前最近邻 LUT 的多优化档结果为：

| Profile | KEIL speed (Points/s) | Flash (KB) | RAM (KB) |
| --- | --- | --- | --- |
| Project default | 6986.7 | 719.2 | 5.6 |
| -O0 | 2234.5 | 728.1 | 86.8 |
| -O2 | 6986.7 | 719.2 | 5.6 |
| -Ofast + LTO | 7059.3 | 721.4 | 5.6 |

可以得到三个稳定结论：

1. 当前主实现已经基本吃到结构性优化收益，`project_default` 与 `-O2` 重合；
2. `-Ofast + LTO` 只再带来约 `1%` 的吞吐增益，属于锦上添花，而不是决定性收益；
3. `-O0` 虽然已经不再构建失败，但 RAM 会显著膨胀到 `86.8 KB`，因此不适合作为正文默认结果。

## 6. 对总稿最有价值的三条结论

### 6.1 Wiener-KAN 最近邻 LUT 已经可以支撑“最快板端实现”叙事

在当前 canonical deployment subset 中，优化后的最近邻 LUT 已达到 `6986.7 Points/s`，高于 RNN、1DCNN、GRU、LSTMTransformer、LSTM 和 TCN，因此总稿不必再把 Wiener-KAN 写成“虽然不是最快，但综合平衡最好”。

更稳妥的新写法应改为：

- **Wiener-KAN 同时给出三项正式物理指标最优、最高板端吞吐和最低 RAM 占用；**
- 但 `KEIL-MAE` 与 Flash 仍需单独交代。

### 6.2 插值版仍然是最有说服力的 accuracy/speed compromise

插值版不再像旧稿那样只剩 `1375.1 Points/s`，而是已经提升到 `3844.8 Points/s`，这意味着：

- 它不是“太慢因而只能当补充”；
- 而是一个仍保持 `kPoints/s` 级速度、却能把 `KEIL-MAE` 压到 `1.902e-04` 的可行主展示版本。

### 6.3 当前最该强调的是“实现优化改变了结论边界”

旧稿最大的问题不是某个小数点，而是对部署边界的判断已经过时：

- 旧稿把最近邻 LUT 写成 `1861.9 Points/s`、`1 MB` 级 Flash 风险；
- 新结果表明它已经变成 `6986.7 Points/s`、`719.2 KB` Flash；
- 插值版也从 `1375.1 Points/s` 提升到 `3844.8 Points/s`。

因此，总稿必须同步更新，否则会低估 Wiener-KAN 当前部署实现的工程可行性。

## 7. 建议写法

如果总稿需要在部署部分给出一句最稳妥的总结，当前建议写成：

> 经过 LUT 存储压缩与 LUT/IIR 专用 benchmark-only 前向优化后，Wiener-KAN 的最近邻 LUT 实现已在 STM32F405 上达到 `6986.7 Points/s`，并将 Flash / RAM 压缩到 `719.2 KB / 5.6 KB`；若进一步采用一阶线性插值，则可在仍保持 `3844.8 Points/s` 的前提下，把 `KEIL-MAE` 从 `7.114e-03` 降到 `1.902e-04`。这说明当前 Wiener-KAN 的部署讨论不应再停留在“能否跑起来”，而应转向“速度优先还是 fidelity 优先”的实现取舍。
