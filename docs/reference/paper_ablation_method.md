# 论文消融实验方法说明

## 写作定位

本文档用于沉淀论文消融实验部分的长期稳定写法。它既是仓库内的长期参考文档，也是后续撰写论文 `Methods` 章节时可直接展开的中文中间稿。

本文档只描述实验目的、实验设计、执行流程、必要公式与正式取值口径，不记录一次性的实验结果数字，也不承载调参流水账。

## 实验目的

当前消融实验服务于两个核心问题：

1. 训练目标层面：验证 AFMAE 及其与 MAE 组合后的损失设计，是否能够在保持时域误差可控的同时，更稳定地约束幅频响应相关误差。
2. 结构层面：验证 Wiener-KAN 当前实现中的关键设计是否真正贡献于最终性能，包括：
   - Wiener 线性前端是否有必要保留系统初始化先验；
   - 对称性约束是否对当前任务有效；
   - 静态非线性主体使用 KAN 是否优于其他局部替换形式；
   - 若将前端替换为卷积或随机可训练 IIR，模型行为会如何变化。

因此，当前消融实验的目标不是简单“证明所有改动都更强”，而是回答：哪些设计是当前 Wiener-KAN 写法中必须保留的，哪些设计只是可替换实现。

## 实验设计

### 设计原则

当前消融实验遵循以下设计原则：

1. 每个变体都对应独立 `projects/...` 路径，禁止在同一 project 内来回覆盖训练。
2. 正式分组由 preset 决定，project 的真实语义由各自 `config.json` 决定。
3. 所有变体共享同一 CLI 训练入口、同一评估入口和同一指标汇总链。
4. 正式表格统一读取 `metrics.json`，而不是训练日志或一次性脚本。

### 共享控制变量

当前损失消融与结构消融中，被选中的 project 在以下实验协议上保持一致：

- `target_sweep = 2`
- `use_points = 8000`
- `sample_rate = 2000`
- `time_clipped_s = 4.0`

这意味着当前消融实验是在相同任务窗口、相同采样率和相同序列截取长度下进行的局部变体比较。

### 损失函数消融

当前损失函数消融由 `cache/webui/presets/` 下的当前损失函数消融 preset 控制，对应如下 project：

| 角色 | 项目路径 | 代码语义 | 主要配置差异 |
| --- | --- | --- | --- |
| 组合损失基线 | `projects/01_LR_STUDY/FRIKANh8u6l6_e1k_lr7e4` | 标准 Wiener-KAN / FRIKAN 基线 | `use_model=FRIKAN`, `use_power_loss=true` |
| 纯 MAE | `projects/01_LR_STUDY/FRIKANh8u6l6_e1k_lr7e4_puremae` | 同一模型，仅移除 AFMAE 项 | `use_power_loss=false` |
| 纯 AFMAE | `projects/03_FRIKAN_PUREAFME/FRIKANh8u6l6_e1k_lr1e4_pureafmae` | 同一模型，仅保留 AFMAE | `use_pure_power_loss=true` |

这三个 project 共用同一 Wiener-KAN 主干：

- `use_model=FRIKAN`
- `H_UNITS=8`
- `INNER_KAN_UNITS=6`
- `INNER_KAN_LAYERS=6`
- `IIR_INIT_BY_SYSTEM=true`
- `IIR_TRAINABLE=false`
- `USE_FAST_MODEL=true`

因此，这一组实验的自变量是损失函数，而不是模型结构。

需要额外说明的边界是：当前 pure AFMAE project 的学习率为 `1e-4`，而组合损失与 pure MAE 使用 `7e-4`。因此这组实验是“当前仓库 canonical 配置下的损失函数消融”，而不是“完全等学习率的严格单因子对照”。如果论文后续需要更强的因果表述，应额外补一组严格等学习率对照。

### 结构消融

当前结构消融由 `cache/webui/presets/` 下的当前结构消融 preset 控制，对应如下 project：

| 角色 | 项目路径 | 代码语义 | 主要配置差异 |
| --- | --- | --- | --- |
| Wiener-KAN 基线 | `projects/01_LR_STUDY/FRIKANh8u6l6_e1k_lr7e4` | 系统初始化 IIR 前端 + KAN 主体 | `use_model=FRIKAN` |
| CNN 前端替换 | `projects/01_LR_STUDY/CNNKANh8u6l6_e1k_lr28e5_c8k5d05` | 用 Conv1D 前端替换 FRI / IIR 前端，同时保留 KAN 主体 | `use_model=CNNKAN`, `model_subcfg.cnn_*` |
| 去对称性变体 | `projects/01_LR_STUDY/FRIKANh8u6l6_e1k_lr7e4_nosym_r5` | 保留同一 FRIKAN 路径，但移除对称性约束 | `model_subcfg={only_positive: true, use_even: false, use_symmetry: false}` |
| 随机化可训练前端替换 | `projects/01_LR_STUDY/FRIKANh8u6l6_e1k_lr14e5_randfrirnn_r2` | 改为随机初始化且可训练的 IIR 前端 | `IIR_INIT_BY_SYSTEM=false`, `IIR_TRAINABLE=true`, `model_subcfg.random_iir_seed=20260405` |
| KAN→MLP 替换 | `projects/04_FRIMLP/FRIMLPh8u6l6_e1k_lr2e3_mlp18l7_tanh_d00` | 保留同一 FRI 前端，仅将静态非线性主体从 KAN 换成 MLP | `use_model=FRIMLP`, `model_subcfg.mlp_*` |

这一组实验的设计目标，是沿着“前端先验 / 结构约束 / 静态非线性主体”三个方向，观察 Wiener-KAN 当前实现中哪些局部结构是不可替代的。

需要守住两个语义边界：

1. `FRIMLP` 的正确语义是“同一 FRI 前端、不同静态非线性主体”，不能在论文中把它写成另一种前端模型，详见 [frimlp_ablation.md](frimlp_ablation.md)。
2. `randfrirnn_r2` 同时修改了初始化、可训练性与学习率，因此它不能被写成“仅去掉系统先验”的干净单因子实验，只能表述为“随机化且可训练的前端替换变体”。

## 实验流程

当前消融实验的正式执行流程如下：

1. 由 preset 选择本次进入正式表格的 project 集合；
2. 进入各 project 的 `config.json`，确认该 project 的真实结构语义；
3. 调用 `python cli.py -t PROJECT_NAME` 训练模型；
4. 训练结束后自动串联 `-e`，生成评估产物；
5. 通过 `python cli.py --metrics PROJECT_NAME` 或训练/评估链中的自动刷新逻辑，生成 `metrics.json`；
6. 论文正式表格统一从 `metrics.json` 取值。

与代码的对应关系为：

1. `ProjectManager.prepare_dataset_and_model()` 加载数据并在需要时调用 `prepare_systems()`；
2. `ModelEngine.build_model()` 根据 `config.use_model` 实例化真实模型；
3. `ModelEngine.build_model()` 同时根据 `loss_type`、`use_power_loss` 与 `use_pure_power_loss` 解析训练损失；
4. `ProjectManager.evaluate()` 负责刷新评估产物；
5. `ProjectManager.export_metrics_summary()` 与 `metrics_summary.py` 负责汇总正式表格字段。

## 必要公式与实现口径

### 统一预测形式

对所有消融变体，统一记补偿模型为：

$$
\hat{y}_{1:T} = f_{\theta}(x_{1:T})
$$

其中 $x_{1:T}$ 为输入序列，$\hat{y}_{1:T}$ 为模型预测补偿输出，$y_{1:T}$ 为目标输出。

### 纯 MAE

当前纯 MAE 路径对应代码中的 `pure_mae_metric(...)`，其核心形式为：

$$
\mathcal{L}_{\mathrm{MAE}} = \frac{1}{N}\sum_{i=1}^{N}\left| y_i - \hat{y}_i \right|
$$

它直接约束时域逐点误差。

### 纯 AFMAE

当前纯 AFMAE 路径对应 `pure_power_log_mae_loss(...)`。代码中先把序列按 `group_points = 4000` 分组，再对每组能量做对数差：

$$
P_g(y) = \sum_{t=1}^{G}\left| y_{g,t} \right|,\qquad
P_g(\hat{y}) = \sum_{t=1}^{G}\left| \hat{y}_{g,t} \right|
$$

$$
\mathcal{L}_{\mathrm{AFMAE}}
=
\frac{1}{M}\sum_{g=1}^{M}
\left|
\log\left(P_g(y)+\varepsilon\right)
-
\log\left(P_g(\hat{y})+\varepsilon\right)
\right|
$$

其中 $\varepsilon = 10^{-8}$ 用于避免对数奇异点。该损失的作用是约束分组能量在对数域中的偏差，从而更直接地约束幅频响应相关误差。

### 当前组合损失

当前标准 Wiener-KAN 基线使用 `power_log_mae_loss(...)`。代码里的实现不是简单的“MAE + AFMAE”符号相加，而是：

1. 先计算 AFMAE 部分；
2. 再计算逐点 MAE；
3. 用分组能量对 MAE 做归一化并乘以常数 `350`；
4. 最后按 `k = 0.2` 线性组合。

对应写法可记为：

$$
\mathcal{L}_{\mathrm{comb}}

=
k\cdot \mathcal{L}_{\mathrm{AFMAE}}
+
(1-k)\cdot \mathcal{L}_{\mathrm{MAE,bal}}
,
\qquad k=0.2
$$

其中平衡后的 MAE 项为：

$$
\mathcal{L}_{\mathrm{MAE,bal}}
=
\frac{1}{M}\sum_{g=1}^{M}
\left(
\frac{\frac{1}{G}\sum_{t=1}^{G}\left|y_{g,t}-\hat{y}_{g,t}\right|}
\max(P_g(y),\varepsilon)}
\cdot 350
\right)
$$

因此，论文中若要给出组合损失公式，必须按照当前代码实现写成“对数能量误差项 + 能量归一化 MAE 项”的加权组合，而不能随意简写成模糊的“MAE 和频域项相加”。

## 正式表格字段建议

当前最稳定、最适合进入论文主表的字段为：

- `Loss Function`
- `Freq Drift (Hz)`
- `Sens Drift (%)`
- `Linearity (%)`
- `Compute Cost`
- `Total Params`
- `Epochs`
- `LR`

其中：

- `Freq Drift (Hz)`、`Sens Drift (%)` 与 `Linearity (%)` 用于体现补偿质量；
- `Compute Cost` 与 `Total Params` 用于体现复杂度代价；
- `Epochs` 与 `LR` 适合作为复现实验设置的辅助列。

`TRAIN_MAE`、`VAL_MAE`、`TRAIN_AFMAE`、`VAL_AFMAE` 可以保留为辅助分析字段，但不应替代主表中的物理指标。

## 写作边界

在论文方法章节中，当前消融实验部分应严格遵循以下边界：

- 先定义实验目的，再定义分组设计；
- 正式分组以 preset 为准，真实语义以各自 `config.json` 为准；
- 正式表格只读取 `metrics.json`，不直接引用训练日志；
- 不把调参历史写进方法章节；
- 不把训练曲线写成正式消融证据；
- 不把当前 canonical 配置下的消融夸大成严格正交单因子实验。

## 相关文档

- [training.md](training.md)
- [evaluation.md](evaluation.md)
- [metrics.md](metrics.md)
- [compute_analysis.md](compute_analysis.md)
- [mae_vs_afmae.md](mae_vs_afmae.md)
- [frimlp_ablation.md](frimlp_ablation.md)
- [cnnkan_ablation.md](cnnkan_ablation.md)
