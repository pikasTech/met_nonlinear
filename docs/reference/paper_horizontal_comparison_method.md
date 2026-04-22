# 论文横向对比实验方法说明

## 写作定位

本文档用于沉淀论文主横向对比实验部分的长期稳定写法。它既是仓库内的长期参考文档，也是后续撰写论文 `Methods` 章节时可直接展开的中文中间稿。

本文档只描述实验目的、实验设计、执行流程、必要公式与正式取值口径，不记录一次性的实验结果数字，也不承载训练流水账。

## 实验目的

当前横向对比实验服务于三个核心问题：

1. 方法有效性：验证 Wiener-KAN 相对于主流时序补偿模型，是否能在同一任务协议下取得更优的物理补偿性能。
2. 精度-复杂度权衡：验证 Wiener-KAN 的性能提升是否建立在可接受的参数量与计算代价之上，而不是单纯依赖更大的模型规模。
3. 工程可用性：为后续部署子章节提供候选模型子集，判断哪些模型在保持数值效果的同时具备进一步做 QEMU / Keil 板端验证的价值。

因此，当前横向对比实验的目标不是仅比较时域误差，而是从物理指标、复杂度指标和可部署性三个维度回答：Wiener-KAN 在当前电化学非线性补偿任务中，相比主流时序模型是否更适合作为主方法。

## 实验设计

### 设计原则

当前横向对比实验遵循以下设计原则：

1. 每个对比对象都对应独立 `projects/...` 路径，禁止在单一 project 上反复改结构重训。
2. 正式分组由当前横评 preset 决定，模型的真实语义以各自 `config.json` 为准。
3. 所有模型共享同一训练入口、同一评估入口和同一指标汇总链。
4. 正式论文主表统一读取 `metrics.json`，而不是训练日志、截图或一次性脚本。

### 正式分组

当前横向对比分组由 `cache/webui/presets/20260410-横评.json` 控制，对应如下 project：

| 家族 | 项目路径 | 代码语义 | 当前 active loss | 学习率 | 是否已有板端路径 |
| --- | --- | --- | --- | --- | --- |
| Wiener-KAN / FRIKAN | `projects/01_LR_STUDY/FRIKANh8u6l6_e1k_lr7e4` | 系统初始化 IIR 前端 + KAN 主体 | `MAE+AFMAE` | `7e-4` | 是 |
| LSTMTransformer | `projects/01_LR_STUDY/LSTMTransformeru6_e1k_puremae` | LSTM 主干 + 注意力 + FFN | `MAE` | `1e-2` | 是 |
| LSTM | `projects/01_LR_STUDY/LSTMu16_e1k_puremae_r8` | 标准 LSTM + Dense | `MAE` | `7e-4` | 是 |
| GRN (GRU) | `projects/01_LR_STUDY/GRNu16_e1k_puremae` | GRU 主干 + Dense | `MAE` | `7e-4` | 是 |
| 1DCNN | `projects/05_1DCNN/1DCNNc4u8k20l8_e1k_lr18e4_pd8l2_d001_cvtanh_true` | 卷积时序基线 | `MAE` | `1.8e-3` | 当前这个 project 否 |
| TCN | `projects/06_TCN/TCNc4d1248k3_nopd_true_e1k_lr2e3` | 时序卷积基线 | `MAE` | `2e-3` | 是 |
| RNN | `projects/07_RNN/RNNu16_e1k_puremae_r15` | SimpleRNN + Dense | `MAE` | `1.5e-3` | 否 |

从论文叙述上，这一组实验可概括为“覆盖物理先验型模型、循环时序模型、注意力增强循环模型与卷积时序模型的跨家族横向比较”。

### 共享控制变量

当前横评 preset 中的 project 在以下任务协议上保持一致：

- `target_sweep = 2`
- `use_points = 8000`
- `sample_rate = 2000`
- `time_clipped_s = 4.0`

这意味着当前横向对比是在相同目标任务、相同采样率、相同序列窗口长度和相同数据截取规则下进行的模型家族比较。

### 必须写明的设计边界

当前横向对比不是“严格 architecture-only 单因子实验”，而是“共享任务协议下的 canonical project comparison”。原因有三：

1. 各模型的 active loss 不完全一致，`FRIKAN` 使用 `MAE+AFMAE`，其余多数基线使用 `MAE`。
2. 各模型的学习率不完全一致，当前 preset 中保留的是各自已沉淀下来的 canonical project，而不是人为强行统一后的参数版本。
3. 不同模型的结构归纳偏置不同，当前设计更接近“真实可复现实验对象横评”，而不是只替换单一模块的消融。

因此，论文中应将这一节表述为：在共享数据协议和统一指标汇总链下，对当前仓库内已定型的代表性模型进行横向比较；不应把它夸大成“严格等损失、等学习率、等优化超参的单因子结构比较”。

### 模型实例化语义

当前这些 project 通过 `ModelEngine.build_model()` 中的 `config.use_model` 实例化：

- `FRIKAN`：系统初始化 IIR / FRI 前端 + KAN 静态非线性主体；
- `LSTMTransformer`：LSTM 主干后接注意力与前馈模块；
- `LSTM`：标准 LSTM 路径；
- `GRN`：当前实际由 GRU 主干实现；
- `1DCNN`：真实卷积时序基线；
- `TCN`：时序卷积残差基线；
- `RNN`：`SimpleRNN` 路径。

因此，论文方法部分不需要复述源码细节，但必须明确说明：所有横评对象均来自仓库中的真实 project，而不是从外部论文摘录的离线结果。

## 实验流程

当前横向对比实验的正式执行流程如下：

1. 由 `cache/webui/presets/20260410-横评.json` 选择进入正式对比的 project 集合；
2. 逐个检查各 project 的 `config.json`，确认 `use_model`、`learning_rate`、loss 配置与 `board_inference_ep_path`；
3. 使用 `python cli.py -t PROJECT_NAME` 训练各模型；
4. 使用 `python cli.py -e PROJECT_NAME` 刷新评估产物；
5. 通过 `python cli.py --metrics PROJECT_NAME` 或自动刷新链，生成 `metrics.json`；
6. 论文主横评表统一从 `metrics.json` 读取物理指标与复杂度指标；
7. 若某 project 配置了 `board_inference_ep_path`，则其部署指标在部署子章节中单独展开，而不直接与所有横评对象混排。

与代码的对应关系为：

1. `ProjectManager.prepare_dataset_and_model()` 负责加载数据集、在需要时调用 `prepare_systems()` 并构建模型；
2. `ModelEngine.build_model()` 根据 `config.use_model` 实例化真实模型结构；
3. `ProjectManager.evaluate()` 负责生成 `training_info.json`、`compute_analysis.json`、`linear_response.json` 与 `linearity_by_frequency.json` 等评估产物；
4. `task_dispatcher._refresh_metrics_summary()` 与 `ProjectManager.export_metrics_summary()` 负责统一导出 `metrics.json`。

## 必要公式与实现口径

### 统一监督学习形式

设横评中的第 $m$ 个模型记为 $f_{\theta_m}^{(m)}$，输入序列与目标序列分别为 $x_{1:T}$ 与 $y_{1:T}$，则统一预测形式记为：

$$
\hat{y}_{1:T}^{(m)} = f_{\theta_m}^{(m)}(x_{1:T})
$$

训练阶段优化的目标可统一写成：

$$
\theta_m^{\ast}
=
\arg\min_{\theta_m}
\sum_{n=1}^{N}
\mathcal{L}_m
\left(
y_{1:T}^{(n)},
\hat{y}_{1:T}^{(m,n)}
\right)
$$

其中 $\mathcal{L}_m$ 由具体 project 的 active loss 决定。当前代码并未强制所有模型共享同一损失函数，因此这一定义只用于统一问题形式，而不表示当前横评是严格等损失对照。

### 横评指标向量

对任一 project $p$，当前论文主横评最稳定的比较向量可写为：

$$
\mathbf{M}(p)
=
\left[
d_f(p),\,
d_s(p),\,
e_{\mathrm{lin}}(p),\,
C(p),\,
P(p)
\right]^{\top}
$$

其中：

- $d_f(p)$：`Freq Drift (Hz)`；
- $d_s(p)$：`Sens Drift (%)`；
- $e_{\mathrm{lin}}(p)$：`Linearity (%)`，当前语义是 `<=128 Hz` in-band 平均非线性误差百分比；
- $C(p)$：`Compute Cost`；
- $P(p)$：`Total Params`。

若该 project 同时具备合法部署路径，则部署子章节再扩展为：

$$
\widetilde{\mathbf{M}}(p)
=
\left[
\mathbf{M}(p),\,
E_{\mathrm{QEMU}}(p),\,
E_{\mathrm{KEIL}}(p),\,
S_{\mathrm{KEIL}}(p)
\right]^{\top}
$$

其中 $E_{\mathrm{QEMU}}$、$E_{\mathrm{KEIL}}$ 与 $S_{\mathrm{KEIL}}$ 分别对应 `QEMU-MAE`、`KEIL-MAE` 与 `KEIL-SPEED`。

### 当前代码没有单一加权总分

当前仓库没有定义统一的总评分函数，例如：

$$
J(p) = \sum_i w_i M_i(p)
$$

这样的单一标量在当前代码中并不存在。也就是说，横评结论不是由某个隐藏的总分自动排序得到，而是由 `metrics.json` 中的多列指标共同支撑。因此，论文正文应采用“多指标联合比较”或“帕累托式比较”表述，而不是声称存在统一加权得分。

## 正式表格字段建议

当前最稳定、最适合进入论文主横评表的字段为：

- `Freq Drift (Hz)`
- `Sens Drift (%)`
- `Linearity (%)`
- `Compute Cost`
- `Total Params`

建议保留为辅助复现实验设置的字段包括：

- `Loss Function`
- `Epochs`
- `LR`

若某些模型具备合法部署产物，则部署子章节可额外使用：

- `QEMU-MAE`
- `KEIL-MAE`
- `KEIL-SPEED`

## 写作边界

在论文横向对比方法章节中，当前写法应严格遵循以下边界：

- 先定义正式分组，再说明模型家族覆盖范围；
- 正式主表只读取 `metrics.json`，不直接引用训练日志或临时截图；
- 不把当前 canonical project comparison 夸大成严格等损失、等学习率、等超参的单因子结构对照；
- 不在未声明的情况下，把精度横评用的 `1DCNN` project 偷换成另一个部署用 `1DCNN` project；
- 不把 `RNN` 之类尚无 native board-inference 路径的模型强行写进正式部署表；
- 当 `metrics.json.status = partial` 时，不回退到旧表格或手工数字。

## 相关文档

- [training.md](training.md)
- [evaluation.md](evaluation.md)
- [metrics.md](metrics.md)
- [compute_analysis.md](compute_analysis.md)
- [conv_sequence_baselines.md](conv_sequence_baselines.md)
- [rnn_baselines.md](rnn_baselines.md)
- [paper_edge_inference_evaluation_method.md](paper_edge_inference_evaluation_method.md)
