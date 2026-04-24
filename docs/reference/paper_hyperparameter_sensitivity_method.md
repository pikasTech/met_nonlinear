# 论文超参数敏感性分析方法说明

## 写作定位

本文档用于沉淀论文“超参数敏感性 / 稳健性”部分的长期稳定写法。它只记录可重复复用的实验设计、执行约束、失败分类、结果解释边界和后续分析入口，不记录一次性流水账或临时调参过程。

当前文档对应 TIM 审稿意见中的“超参数敏感性分析”，用于回答主要超参数变化下模型是否仍保持可接受的性能与稳定性，以及哪些超参数已经触碰当前训练环境的可行域边界。

## 审稿意见对应

- `docs/paper/TIM/TIM-25-06440.decision.md` 第 5 条：要求对主要超参数做敏感性分析，以证明框架的鲁棒性和稳定性。
- 当前仓库中的正式任务入口为 `docs/MDTODO/20260327-转投.md` 的 `R15`。

## 基线与控制变量

当前论文超参数敏感性分析以 `projects/09_HPARAM_SENSITIVITY/FRIKANh8u6l6g8s2_e1k_lr7e4_base` 为 canonical 基线，遵循单因素扫描原则：一次只改一个主超参数，其余保持与基线一致。

固定不变的核心条件包括：

- `epoch_train = 1000`
- `learning_rate = 7e-4`
- 损失函数保持基线口径（当前为 `MAE+AFMAE`）
- 数据集、输入长度、采样率和评估链路保持与基线一致
- 每个变体必须放在独立 `projects/...` 路径下，禁止在同一项目内覆盖配置反复重训

当前 canonical 扫描轴为：

- `H_UNITS`: `3, 4, 5, 6, 7, 8, 9, 10`
- `INNER_KAN_UNITS`: `3, 4, 5, 6, 7, 8`
- `INNER_KAN_LAYERS`: `3, 4, 5, 6, 7, 8`
- `GRID_SIZE`: `3, 4, 5, 6, 7, 8`
- `SPLINE_ORDER`: `1, 2, 3`

其中 `h8u6l6g8s2` 为基线点，其他配置均围绕该点做单轴偏移。

## 执行约束

超参数敏感性分析除了遵守一般训练约束外，还应额外满足以下要求：

1. 训练必须以前台可见方式执行，并保持附着在当前会话，详见 [training.md](training.md)。
2. 一次只训练一个项目，不允许并行多项目抢占同一块 GPU。
3. 禁止预先批量 blind sweep；每轮都应读取上一轮项目的真实指标或失败状态后，再决定是否继续扩展该轴。
4. 新变体必须先复制同类项目的 `config.json`，再只修改目标字段，不能手写全新的配置文件。
5. 训练结束后的正式指标统一读取 `metrics.json`，而不是终端输出或一次性草稿表。

当前 R15 任务的 manifest 和状态文件分别为：

- `projects/09_HPARAM_SENSITIVITY/R15_projects.tsv`
- `projects/09_HPARAM_SENSITIVITY/R15_training_status.tsv`

这两个文件应视为该轮敏感性分析的唯一项目清单和状态权威来源。

## 失败分类与判定

超参数敏感性扫描中，失败点不能被简单丢弃，必须先分类，再决定论文写法。

### 1. `completed`

满足以下条件时，才可视为正式完成：

- `training_state.json.completed_epoch = 1000`
- `training_state.json.training_alive = false`
- `metrics.json` 已生成且 `status = complete`

### 2. `recoverable runtime fault`

如果训练在中途因 `CUDA_ERROR_ILLEGAL_ADDRESS`、外层会话中断或 stale lock 问题失败，但已经产生了可用 checkpoint，则应先：

1. 确认没有残留 `cli.py -t` 进程；
2. 将 `training_state.json.training_alive` 改回 `false`；
3. 删除过期 `training.lock`；
4. 重新以前台方式调用 `python cli.py -t ...` 续训。

这种点在论文中仍可按正常完成点使用，但过程报告中必须显式记录为“异常后恢复完成”，避免误判为一次性稳定跑通。

### 3. `OOM / train-time infeasible`

如果训练在 `epoch = 0` 即触发 `ResourceExhaustedError` / GPU OOM，且没有形成可用训练进度，则该点应标记为：

- `OOM`
- `train-time infeasible under current environment`

此类点的长期规则是：

- 不要伪造或补齐 `Freq Drift`、`Sens Drift`、`Linearity`；
- 不要把它们静默从扫描图表中删除；
- 不要把“当前机器上 OOM”表述成“理论上该超参数一定更差”；
- 应明确限定为“在当前训练环境中的不可行边界”。

## 论文写作口径

### 可行域优先

当前敏感性分析的正式结论应限定在“可训练区域”内。正文建议使用如下口径：

- “Within the feasible training region...”
- “Larger settings became train-time infeasible on the current training platform...”

而不要写成：

- “larger `U/L/S` are worse”
- “the full hyperparameter space was exhaustively covered”

### OOM 点必须披露

对未完成的扫描点，表格或图中必须保留 `OOM` / `Train-time infeasible` 标记。遗漏这些点会让敏感性分析看起来像是选择性汇报。

### 不可把 OOM 当成性能值

OOM 点只能用于界定训练可行域边界，不能参与最优值排序、均值计算或趋势拟合。

### 可接受的总体结论

如果满足以下条件，则即使存在 OOM 点，剩余数据通常仍足以支撑论文写作：

1. 至少有两条以上主轴已经完整扫描；
2. 其余主轴在基线附近至少覆盖了可训练的低侧或中侧点；
3. 所有 OOM 点都被显式披露；
4. 成功点中没有出现一个同时严格支配基线全部核心指标的替代配置。

在这种情况下，可以将结论写成：“基线位于当前可训练区域内的稳定折中点，而不是依赖单一脆弱超参数的偶然最优。”

## 指标读取与结果组织

当前敏感性分析的正式数值统一来自各项目 `data/metrics.json` 中的 `display_metrics` 字段，主表建议至少包含：

- `Freq Drift (Hz)`
- `Sens Drift (%)`
- `Linearity (%)`
- `Compute Cost`
- `status`

长期建议的组织方式为：

1. 每个轴单独一张表或一组曲线；
2. 基线点始终与该轴的扫描点一起展示；
3. `status` 必须作为正式字段，而不是只在脚注里说明；
4. 对 `GRID_SIZE` 和 `SPLINE_ORDER`，应额外强调其对部署后推理成本的解释口径，避免只看训练误差。

## 后续 ex_project 分析要求

超参数敏感性分析的后处理应由单独的 compare 类 `ex_project` 承担。当前建议使用统一入口，例如：

- `ex_projects/compare/hparam_sensitivity_r15`

该分析任务至少应完成以下输出：

1. 聚合 `R15_projects.tsv`、`R15_training_status.tsv` 和各项目 `metrics.json`，生成带 `status` 字段的统一汇总表；
2. 按 `H / U / L / G / S` 五条主轴分别输出指标曲线或柱状图；
3. 对 OOM 点在图中保留位置并用显式标记表示，不得直接断轴后删除；
4. 输出“基线 vs 各轴最优可训练点”的对比摘要；
5. 输出一份 paper-ready 的 Markdown / JSON 产物，供 `values.tex` 或 `docs/paper/data/results.json` 消费。

建议该 `ex_project` 的核心结论至少覆盖：

- 哪些轴已经完整扫描；
- 哪些轴在高侧触碰训练可行域边界；
- 基线是否被任何可训练点同时严格支配；
- `GRID_SIZE` 与 `SPLINE_ORDER` 是否改变 `Compute Cost`；
- 若只在当前硬件上考虑，哪些配置属于“高成本但无稳定收益”的排除点。

## 相关文件

- 任务定义：`docs/MDTODO/20260327-转投.md`
- 训练约束：`docs/reference/training.md`
- 指标口径：`docs/reference/paper_metric_calculation_method.md`
- 论文方法写作：`docs/reference/paper_method_draft_writing.md`
- 当前 sweep 项目根目录：`projects/09_HPARAM_SENSITIVITY/`
