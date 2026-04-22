# 论文指标计算方法说明

## 写作定位

本文档用于沉淀论文正式表格与图表在当前仓库中的统一指标计算方法。它既是仓库内的长期参考文档，也是后续撰写论文 `Methods` 章节时可直接展开的中文中间稿。

本文档只描述实验目的、指标体系、生成流程、必要公式与正式取值口径，不记录一次性的实验数值，也不承载人工抄表过程。

## 实验目的

当前指标计算方法服务于四个核心问题：

1. 单一事实来源：为损失消融、结构消融、横向对比与部署子集提供统一的数据出口，避免不同章节分别从不同文件取值。
2. 口径一致性：确保物理指标、复杂度指标和部署指标都遵循同一套代码实现，而不是由论文撰写阶段手工重算。
3. 可复现性：使任意一个 project 的正式表格数字都能回溯到固定的上游产物和固定的 Python 实现。
4. 边界显式化：把“优化类指标”“物理性能指标”“复杂度指标”“部署一致性指标”分层定义，避免不同语义的量被混写为同一类结论。

因此，当前指标计算部分的目标不是给出一张静态结果表，而是定义论文全稿的唯一取值标准。

## 实验设计

### 单一事实来源

当前各类实验虽然由不同 preset 选择 project，但最终都消费同一种单项目 summary 文件：

- `projects/.../data/metrics.json`

长期规则如下：

1. preset 决定某个实验分组包含哪些 project；
2. `metrics.json` 决定该 project 在论文中最终读取哪些数值；
3. `training_info.json`、`linear_response.json`、`compute_analysis.json` 等文件只是上游输入，不是论文主表的独立事实来源；
4. 若要改字段定义或新增指标，应先改代码中的 summary 管线，再改论文，而不是手工补表。

### 四层指标体系

当前 `metrics.json` 的正式字段可按四层组织：

| 层级 | 代表字段 | 主要语义 | 上游来源 |
| --- | --- | --- | --- |
| 优化 / 评估层 | `Loss Function`、`TRAIN_MAE`、`VAL_MAE`、`TRAIN_AFMAE`、`VAL_AFMAE`、`Epochs`、`LR` | 训练目标与离线评估误差 | `training_info.json` + `config.json` |
| 物理性能层 | `Freq Drift (Hz)`、`Sens Drift (%)`、`Linearity (%)` | 补偿后的物理一致性与非线性误差 | `linear_response.json` + `linearity_by_frequency.json` |
| 复杂度层 | `Compute Cost`、`Total Params` | 模型参数规模与单步语义计算代价 | `compute_analysis.json` / `model_info.json` |
| 部署一致性层 | `QEMU-MAE`、`KEIL-MAE`、`KEIL-SPEED` | C 推理与 TensorFlow 参考路径的一致性及板端单位点时延 | 部署 EP 产物 |

### 生成链设计

当前稳定 summary 管线如下：

1. `python cli.py -e PROJECT_NAME` 调用 `ProjectManager.evaluate()` 刷新评估产物；
2. `python cli.py --metrics PROJECT_NAME` 可以在不重跑整套评估的情况下重建 summary；
3. `python cli.py -m PROJECT_NAME` 在导出模型信息后也会刷新同一份 summary；
4. `task_dispatcher._refresh_metrics_summary()` 调用 `ProjectManager.export_metrics_summary()`；
5. `ProjectManager.export_metrics_summary()` 调用 `save_project_metrics_summary(...)`；
6. `save_project_metrics_summary(...)` 内部调用 `build_project_metrics_summary(...)`；
7. `build_project_metrics_summary(...)` 汇总上游文件并写出顶层字段与 `display_metrics`。

因此，论文方法部分应把指标提取写成“文件级汇总管线”，而不是人工整理的结果表流程。

### 上游输入产物

`build_project_metrics_summary(...)` 当前会读取以下输入：

- `projects/.../data/training_info.json`
- `projects/.../data/compute_analysis.json`
- `projects/.../data/model_info.json`
- `projects/.../data/linear_response.json`
- `projects/.../data/linearity_by_frequency.json`
- `projects/.../config.json`

如果 `config.json` 中配置了 `board_inference_ep_path`，则还会进一步读取：

- `ex_projects/.../data/benchmark_summary.json`
- `ex_projects/.../data/keil_benchmark_summary.json`

因此，`metrics.json` 的本质是单项目统一 summary，而不是某一个单独分析模块的直接输出。

## 实验流程

当前指标计算与写回的正式执行流程如下：

1. 训练阶段使用 `python cli.py -t PROJECT_NAME` 生成权重与 `training_info.json`；
2. 评估阶段使用 `python cli.py -e PROJECT_NAME`，由 `ProjectManager.evaluate()` 生成 `compute_analysis.json`、`linear_response.json`、`linearity_by_frequency.json`，并把 `evaluation_metrics` 写回 `training_info.json`；
3. 若某 project 存在合法 `board_inference_ep_path`，则完成对应的 QEMU / Keil 部署评估；
4. `task_dispatcher._refresh_metrics_summary()` 或手动 `python cli.py --metrics PROJECT_NAME` 调用 `build_project_metrics_summary(...)`；
5. `build_project_metrics_summary(...)` 汇总优化、物理、复杂度与部署字段，输出到 `projects/.../data/metrics.json`；
6. 论文正式表格统一从 `metrics.json` 读取，推荐优先读取 `display_metrics`。

## 必要公式与实现口径

### Active loss 与评估类字段

设预测输出为 $\hat{y}$，目标输出为 $y$。当前 `train_loss` 与 `val_loss` 使用 active loss 重新计算：

$$
\mathcal{L}_{\mathrm{active}} \in
\left\{
\mathcal{L}_{\mathrm{MAE}},
\mathcal{L}_{\mathrm{AFMAE}},
\mathcal{L}_{\mathrm{MAE+AFMAE}},
\mathcal{L}_{\mathrm{AFMSE}}
\right\}
$$

其选择顺序为：

1. 优先读取 `config.loss_type`
2. 若无，则看 `config.use_pure_power_loss`
3. 再看 `config.use_power_loss`
4. 若都未启用，则回退到纯 `MAE`

与 active loss 无关，`TRAIN_MAE`、`VAL_MAE` 始终按：

$$
\mathcal{L}_{\mathrm{MAE}}
=
\frac{1}{N}\sum_{i=1}^{N}\left|y_i-\hat{y}_i\right|
$$

重新计算；`TRAIN_AFMAE`、`VAL_AFMAE` 则始终按分组能量对数误差计算：

$$
P_g(y)=\sum_{t=1}^{G}\left|y_{g,t}\right|,
\qquad
P_g(\hat{y})=\sum_{t=1}^{G}\left|\hat{y}_{g,t}\right|
$$

$$
\mathcal{L}_{\mathrm{AFMAE}}
=
\frac{1}{M}\sum_{g=1}^{M}
\left|
\log(P_g(y)+\varepsilon)
-
\log(P_g(\hat{y})+\varepsilon)
\right|
$$

其中当前实现使用 `group_points = 4000`，$\varepsilon = 10^{-8}$。

因此，即便某个 project 的 active loss 不是 AFMAE 系，`TRAIN_AFMAE` 与 `VAL_AFMAE` 仍然是稳定的诊断字段。

### Freq Drift (Hz)

`metrics_summary.py` 会读取 `linear_response.json.fit_params_comped`，对每个震级项取拟合参数中的 $B$ 项，并换算为固有频率：

$$
f_{n,k} = \frac{\sqrt{B_k}}{2\pi}
$$

随后用中位数中心漂移定义：

$$
d_f
=
\max
\left(
\left|\max_k f_{n,k} - \operatorname{median}(f_n)\right|,
\left|\operatorname{median}(f_n) - \min_k f_{n,k}\right|
\right)
$$

因此，`Freq Drift (Hz)` 的实际语义是跨震级 compensated 固有频率漂移。

### Sens Drift (%)

`metrics_summary.py` 会读取 `linear_response.json.frequencies` 与 `gains_comped`，对每个震级的 gain 曲线在 `100 Hz` 处做线性插值，得到灵敏度值 $S_k(100)$，然后按同样的中位数中心漂移定义：

$$
d_s
=
\max
\left(
\left|\max_k S_k(100) - \operatorname{median}(S(100))\right|,
\left|\operatorname{median}(S(100)) - \min_k S(100)\right|
\right)
$$

因此，论文中必须明确写清：当前 `Sens Drift (%)` 固定取 `100 Hz` 处的插值灵敏度，而不是整条曲线的平均值。

### Linearity (%)

`metrics_summary.py` 读取 `linearity_by_frequency.json.linearity_by_frequency[*].r_squared_comped`，先转为非线性误差：

$$
e_k = 1 - R_k^2
$$

再取平均并换算成百分数：

$$
e_{\mathrm{lin}}
=
\frac{100}{K}\sum_{k=1}^{K} e_k
=
\frac{100}{K}\sum_{k=1}^{K}\left(1-R_k^2\right)
$$

因此，当前 `Linearity (%)` 的真实语义是“平均非线性误差百分比”，不是越大越好的正向线性度分数。

### Compute Cost

`Compute Cost` 取自 `compute_analysis.estimated_cost.weighted_units.total`，基本形式为：

$$
C
=
w_{\mathrm{add}} N_{\mathrm{add}}
+
w_{\mathrm{mul}} N_{\mathrm{mul}}
+
w_{\mathrm{map}} N_{\mathrm{map}}
$$

当前默认成本模型为：

- `add_weight = 1.0`
- `mul_weight = 1.0`
- `map_weight = 6.0`

它的语义是单样本、单时间步的加权语义操作估算，不是完整序列的端到端实测时延。

### Total Params

`Total Params` 当前按以下顺序解析：

1. 优先读取 `compute_analysis.total_params`
2. 若缺失，则回退到 `model_info.total_params`

因此，论文中应把 `Total Params` 视为统一参数量字段，而不是根据不同分析文件切换口径。

### 部署一致性指标

当且仅当 `config.json` 配置了合法 `board_inference_ep_path`，`metrics.json` 才会自动导入部署字段：

- `QEMU-MAE`
- `KEIL-MAE`
- `KEIL-SPEED`

其对应公式分别为：

$$
E_{\mathrm{QEMU}}
=
\frac{1}{N}
\sum_{i=1}^{N}
\left|
\hat{y}^{\mathrm{QEMU}}_i
-
\hat{y}^{\mathrm{TF}}_i
\right|
$$

$$
E_{\mathrm{KEIL}}
=
\frac{1}{N}
\sum_{i=1}^{N}
\left|
\hat{y}^{\mathrm{KEIL}}_i
-
\hat{y}^{\mathrm{TF}}_i
\right|
$$

$$
S_{\mathrm{KEIL}}
=
\frac{\mathrm{wall\_time\_per\_iter\_ms}}
{\mathrm{record\_count} \cdot \mathrm{seq\_len}}
$$

当前自动取值来源分别为：

- `benchmark_summary.json.comparison.mae`
- `keil_benchmark_summary.json.comparison.mae`
- `keil_benchmark_summary.json.parsed_output.wall_time_per_iter_ms`

Flash、RAM 与 `cycles_per_iter` 当前不自动写入 `metrics.json`，应在部署子章节中单独说明。

## 正式表格字段建议

针对当前 preset 驱动的各实验分组，推荐使用如下字段：

- 损失消融与结构消融：
  - `Loss Function`
  - `Freq Drift (Hz)`
  - `Sens Drift (%)`
  - `Linearity (%)`
  - `Compute Cost`
  - `Total Params`
  - `Epochs`
  - `LR`
- 主横向对比：
  - `Freq Drift (Hz)`
  - `Sens Drift (%)`
  - `Linearity (%)`
  - `Compute Cost`
  - `Total Params`
  - 可选辅助字段：`Loss Function`、`Epochs`、`LR`
- 部署子集：
  - `QEMU-MAE`
  - `KEIL-MAE`
  - `KEIL-SPEED`

当前最安全的正式取值来源是：

- `metrics.json.display_metrics`

## 写作边界

在论文指标方法章节中，当前写法应严格遵循以下边界：

- 明确把 `metrics.json` 定义为唯一正式表格来源；
- 所有公式必须来自当前 `metrics_summary.py` 与相关上游实现，而不是论文阶段手工重算；
- 先写字段定义与公式，再写表格如何取值；
- 不直接从 notebook、图片或一次性脚本拷贝论文主表数字；
- 不把 `min_loss`、`min_val_loss` 当作物理性能指标；
- 不把 `Linearity (%)` 误写成“越大越好”的正向评分；
- 不给没有合法 `board_inference_ep_path` 的 project 强行补部署字段；
- 当 `metrics.json.status = partial` 时，不应把该项目当成完整正式结果引用。

## 相关文档

- [metrics.md](metrics.md)
- [evaluation.md](evaluation.md)
- [compute_analysis.md](compute_analysis.md)
- [paper_ablation_method.md](paper_ablation_method.md)
- [paper_horizontal_comparison_method.md](paper_horizontal_comparison_method.md)
- [paper_edge_inference_evaluation_method.md](paper_edge_inference_evaluation_method.md)
