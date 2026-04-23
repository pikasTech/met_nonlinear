# 论文计算量标定方法说明

## 写作定位

本文档用于沉淀论文中 `Compute Cost` 静态复杂度模型的标定方法。它既是仓库内的长期参考文档，也是后续撰写论文 `Methods` 与部署讨论章节时可直接展开的中文中间稿。

本文档只描述标定目标、配对规则、搜索方法、正式采用口径与写作边界，不记录一次性的调试日志或人工试错过程。

## 实验目的

当前 `Compute Cost` 不是端到端实测时延，而是单样本、单时间步的语义操作加权估算：

$$
C = w_{\mathrm{add}}N_{\mathrm{add}} + w_{\mathrm{mul}}N_{\mathrm{mul}} + w_{\mathrm{map}}N_{\mathrm{map}}
$$

其中 `add`、`multiply` 与 `MAP` 的默认权重决定了静态复杂度是否能较好地反映板端真实代价。计算量标定的目标，是在保持 `add_weight = 1.0` 归一化的前提下，用 STM32F405 真机 `ms/point` 结果反标 `mul_weight` 与 `map_weight`，使静态 `Compute Cost` 与板端时延的相对排序更加一致。

## 标定对象

当前正式标定使用同一平台、同一单位点时延口径下的部署完成模型配对。每一对包含：

1. 一个训练 project，用于提供 `compute_analysis.json` 的 `additions`、`multiplications` 与 `maps`；
2. 一个与之绑定的 `qemu-c-inference` EP，用于提供 `keil_benchmark_summary.json` 中的 `wall_time_per_iter_ms` 与 validation 点数。

长期上，参与标定的样本应满足以下条件：

- 都运行在同一 MCU 平台上，当前平台固定为 `STM32F405`；
- 都采用相同的单位点速度定义，即 `ms/point = wall_time_per_iter_ms / (record_count * seq_len)`；
- 都来自已经完成真实部署的正式模型，而不是临时构造的 toy benchmark；
- 模型集合应覆盖循环、卷积、注意力和 Wiener-KAN 等不同计算特征，以避免只拟合单一家族。

当前正式采用的 STM32F405 标定集覆盖 7 个 canonical models：

- `Wiener-KAN`
- `GRU`
- `LSTM`
- `LSTMTransformer`
- `1DCNN`
- `RNN`
- `TCN`

## 实验设计

### 统一代价模型

当前标定采用 add 归一化写法：

$$
T_{\mathrm{pred}}
=
A\left(
N_{\mathrm{add}}
+ M N_{\mathrm{mul}}
+ P N_{\mathrm{map}}
\right)
$$

其中：

- $A$：整体缩放系数，单位为 `ms / add-equivalent`；
- $M$：乘法相对 add 的权重；
- $P$：MAP 相对 add 的权重。

这里的目标不是直接学习绝对时延黑盒回归器，而是学习“add 归一化的可解释语义成本模型”。

### 搜索策略

当前正式实现对应 `ex_projects/compare/compute_cost_calibration/config.json`，采用以下搜索约束：

- `default_mul_weight = 1.0`
- `default_map_weight = 6.0`
- `mul_weight` 在对数网格上搜索；
- `map_weight` 在对数网格上搜索；
- 以对数域 RMSE 作为拟合误差；
- 再加入轻度正则，避免得到“add 几乎无成本”的不可解释极端比值；
- 最后将正则化最优点按固定步长取整，得到正式默认口径。

长期上，标定流程应保留三层结果：

1. `pure fit`：不加正则，仅追求误差最小；
2. `regularized fit`：加入可解释性正则；
3. `adopted fit`：对正则化最优值做工程化取整后的正式默认模型。

## 正式执行流程

当前稳定工作流如下：

1. 创建 `compare/compute_cost_calibration` EP；
2. 在 `config.json` 中配置 project 与 on-board EP 的一一配对；
3. 运行 `python cli.py ep "compare/compute_cost_calibration"`；
4. 读取每个 project 的 `compute_analysis.json` 与 `metrics.json`，以及每个 EP 的 `keil_benchmark_summary.json`；
5. 搜索 `mul_weight` 与 `map_weight`，同时拟合整体缩放系数 $A$；
6. 输出：
   - `compute_cost_calibration_results.json`
   - `compute_cost_calibration_report.md`
   - 搜索热力图与拟合对照图；
7. 将 adopted 模型同时回写为分析模块默认成本模型与 `Config` 默认 `compute_cost_model`；
8. 对需要进入论文表格的 project 重跑 `python cli.py -m PROJECT_NAME` 或 `python cli.py -e PROJECT_NAME`，刷新 `compute_analysis.json` 与 `metrics.json`；
9. 抽查代表性 project 的 `compute_analysis.json.platform_cost_model`，确认落盘权重确实等于 adopted model，而不是停留在旧默认值。

## 当前正式口径

当前 STM32F405 默认平台成本模型采用：

- `add_weight = 1.0`
- `mul_weight = 3.0`
- `map_weight = 20.0`

其直接来源是：

- `pure fit best`: `1 : 652.5750 : 3326.9858`
- `regularized fit best`: `1 : 3.1383 : 20.1587`
- `adopted rounded model`: `1 : 3 : 20`

当前写法中，论文应只把 `1:3:20` 作为正式默认值；`pure fit` 与 `regularized fit` 仅作为“为何不是继续使用旧启发式权重”的方法支撑。

## 趋势异常排查

当静态 `Compute Cost` 与板端 `KEIL-SPEED` 出现明显趋势不一致时，当前推荐排查顺序如下：

1. 先检查参与论文汇总的各 project `compute_analysis.json.platform_cost_model` 是否真的落盘为 adopted model；
2. 再检查 `metrics.json.compute_cost` 是否来自最新重算后的 `compute_analysis.json`；
3. 只有在落盘权重、summary 刷新链都确认无误后，才继续怀疑具体层级公式漏算或模型支持缺失。

这样做的原因是：静态复杂度标定不仅依赖 `model_compute_analysis.py` 的分析默认值，也依赖 CLI 默认配置链是否仍在覆写旧权重。如果 adopted model 只更新了分析模块、却没有同步到 `Config` 默认值，就会出现“说明文字已经是新口径、但实际 project 产物仍是旧口径”的混合状态，从而制造伪趋势异常。

## 论文整合叙事

如果后续要把这部分压缩并入总稿，当前最稳妥的三步叙事是：

1. **先交代为什么需要标定。** `Compute Cost` 不是实测时间，而是 add / multiply / MAP 的单步语义加权估算；旧启发式 `1:1:6` 对 STM32F405 的板端时延拟合不够好，因此需要用 `ms/point` 反标默认权重。
2. **再交代正式采用什么口径。** 当前 adopted model 来自“add 归一化 + 轻度正则 + 工程化取整”，正式默认值为 `1:3:20`，它把 7-model 标定集上的对数域 `RMSE` 从 `0.2266` 降到 `0.1341`。
3. **最后交代为什么要同步默认配置并重刷 project。** adopted model 只有真正进入默认 CLI 刷新链后，`compute_analysis.json` 与 `metrics.json` 才能一致落盘；否则论文图表会混入旧 `1:1:6` 产物，制造伪趋势异常。

压缩后的总稿结论应保持克制：`Compute Cost` 现在已经是**与 STM32F405 板端速度明显更对齐的平台代理指标**，适合支撑 deployment-aware 排序与量级讨论，但不应被写成逐模型都严格单调、也不应被写成真实执行时间预测器。

## 写作建议

论文中推荐这样表述：

1. `Compute Cost` 是单时间步语义操作的静态加权估算，不是完整序列的实测延迟；
2. 默认权重不是拍脑袋设定，而是用 STM32F405 真机 `ms/point` 反标得到；
3. 由于完全自由拟合会把 add 权重推向几乎可忽略，因此正式口径采用“add 归一化 + 轻度正则 + 工程化取整”的可解释模型；
4. 正式默认值为 `add:multiply:MAP = 1:3:20`。

## 写作边界

当前方法章节应避免以下写法：

- 把 `Compute Cost` 直接写成“预测的真实执行时间”；
- 把 `pure fit` 的极端大权重比值当成正式平台模型；
- 在未说明平台前提的情况下，把 `1:3:20` 当作所有 MCU 的普适常数；
- 在未核对 `compute_analysis.json.platform_cost_model` 的情况下，直接把趋势异常归因为层级公式错误；
- 混淆 `QEMU` host 时间、`Keil cycles` 和 `Keil wall-clock ms/point`。

## 相关文档

- [compute_analysis.md](compute_analysis.md)
- [metrics.md](metrics.md)
- [paper_metric_calculation_method.md](paper_metric_calculation_method.md)
- [paper_edge_inference_evaluation_method.md](paper_edge_inference_evaluation_method.md)
