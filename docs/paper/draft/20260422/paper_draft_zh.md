# 基于 Wiener-KAN 的电化学地震检波器大震级非线性频响校准：方法、横向对比与嵌入式评估（中文草稿）

> 写作说明：本文为 2026-04-22 的内部中文整合稿。正文数字优先取自当前仓库中的统一产物：`metrics.json`、部署 EP summary、`build_output_MET405.txt` 以及本目录下重新生成的 `paper_data.json` / `generated_tables.md`。与上一版相比，本稿已经切换到 `Freq Drift` 的 band-limited fit 口径、`Linearity` 的 `<=128 Hz` in-band 口径，以及 `Compute Cost` 的 `1:3:20` 标定口径；论文正文中的 `KEIL speed` 统一按 `Points/s` 展示，因此相关结论应以本版为准。

## Abstract

电化学地震检波器（MET）在大震级工况下会出现显著的非线性频响漂移，表现为峰频偏移、100 Hz 灵敏度漂移以及输入输出非线性误差同时放大。本文围绕这一问题，基于当前仓库中已经固化的 canonical projects、统一指标汇总链和 MCU 部署产物，整理出一篇带有方法、图表和结果分析的中文论文草稿。本文采用 Wiener-KAN 作为主方法：用系统初始化的 Wiener/IIR 线性前端描述震级相关局部频响，再用 KAN 静态非线性主体完成前馈补偿，并以 MAE+AFMAE 组合损失联合约束时域误差与幅频响应误差。正式物理指标中，`Freq Drift (Hz)` 已更新为按 `fit_params` 恢复并限制在 `10-128 Hz` band 内的中心频率漂移，`Linearity (%)` 则固定为 `<=128 Hz` in-band 平均非线性误差。对比 Wiener-KAN、TCN、1DCNN、LSTM、LSTMTransformer、RNN、GRU 共 7 个代表性模型后可以看到：在当前受限 fit 口径与这组 canonical projects 内，Wiener-KAN 给出了最低的 `Freq Drift = 2.34 Hz`，低于 TCN (`2.65 Hz`) 与 1DCNN (`3.72 Hz`)；同时其 `Sens Drift = 9.09%` 与 in-band `Linearity = 0.511%` 也都是该组中的最低值。进一步结合 `Compute Cost = 5066`、`KEIL speed = 6986.7 Points/s` 与 `RAM = 5.6 KB` 可以看出，Wiener-KAN 当前最值得保留的优势已进一步收束为“在当前 canonical projects 内同时拿到三项正式物理指标最优、最高板端吞吐和最低 RAM 占用”。在 STM32F405 上，它不仅明显快于 TCN (`935.7 Points/s`)、1DCNN (`2009.9 Points/s`) 和 RNN (`3652.9 Points/s`)，也把 deployment-aware 叙事从原先的“综合平衡较好”推进到了“结构先验与工程实现同时成立”；需要单独交代的代价则仍是 `KEIL-MAE = 7.11e-03` 和显著高于序列基线的 Flash 占用。

与未补偿原始响应相比，Wiener-KAN 仍将峰频漂移、灵敏度漂移和带内非线性误差分别压低 `93.23%`、`89.25%` 和 `74.50%`。与部署可比的强基线 TCN 相比，Wiener-KAN 的 `Freq Drift` 再降低 `11.72%`，灵敏度漂移再降低 `43.46%`，带内非线性误差再降低 `1.13%`，静态计算量降低 `41.80%`，板端吞吐提升到 `7.47x`；但 TCN 仍具有更低的 `KEIL-MAE`。新补齐的 RNN / 1DCNN 板端结果进一步说明：更低 `Compute Cost` 或更高的结构简单性并不会自动带来更好的物理校准或更可信的导出一致性。即便拥有最低 `Compute Cost = 2816` 的 RNN，板端吞吐也只有 `3652.9 Points/s`，仍低于优化后的 Wiener-KAN；1DCNN 虽把 `KEIL-MAE` 压到 `5.51e-4`，却同样在三项正式物理指标上落后于 Wiener-KAN。在工程论证上，本文把 `Compute Cost` 收口为三点：先用 STM32F405 真机时延把默认权重从旧启发式 `1:1:6` 标定为 `1:3:20`，再把这一默认值真正同步进 CLI 刷新链，最后按新口径重刷 draft 相关 project。这样处理后，标定集扩展到 Wiener-KAN、GRU、LSTM、LSTMTransformer、1DCNN、RNN 和 TCN 七类模型，默认模型的对数域 `RMSE` 从 `0.2266` 降到 `0.1341`。在 Wiener-KAN 自身部署实现上，最近邻 LUT 经过 LUT 存储压缩与 benchmark-only LUT/IIR 专用路径优化后，published profile 已达到 `6986.7 Points/s`；`LUT + 一阶线性插值` 可将 `KEIL-MAE` 从 `7.11e-3` 压到 `1.90e-4`，同时仍保持 `3844.8 Points/s`；`No-LUT exact` 虽将 `KEIL-MAE` 进一步压到 `6.52e-7` 并把 Flash 降到 `33.7 KB`，但吞吐会降到 `45.0 Points/s`。此外，多优化档真机 benchmark 还表明：`-O0` 现已可以构建并运行（`2234.5 Points/s`、`728.1 KB Flash`、`86.8 KB RAM`），`-O2` 与 project default 基本重合，而 `-Ofast + LTO` 仅把吞吐进一步推到 `7059.3 Points/s`。因此，更稳妥的写法是把 Wiener-KAN 表述为一种**在当前对比集合内同时兼顾三项正式物理指标、最高板端吞吐与最低 RAM 占用的结构化校准方案**，并明确承认其 `KEIL-MAE` 与 Flash 仍是部署边界。

**Keywords**: electrochemical seismometer; Wiener-KAN; nonlinear frequency-response drift; band-limited fitted center frequency; compute-cost calibration; embedded deployment

## 1 引言

电化学地震检波器在弱振动测量中具有高灵敏度和低噪声优势，但随着输入震级增大，其频率响应会表现出明显的震级依赖性：峰频向高频漂移，100 Hz 处灵敏度随震级变化而偏离，输入输出关系也逐步失去线性。传统的结构优化和力反馈方案能够在局部工况下抑制这类问题，但它们往往面向较窄的工作区间，或者需要附加反馈硬件与系统调试成本。对于目标是扩大动态范围、保持系统结构简洁并支持后续嵌入式部署的场景，前馈型非线性校准仍是一条更具工程吸引力的路径。

在当前项目语境下，本文不再把重点放在“提出一个全新的模型命名”上，而是把问题重新表述为：**如何在宽震级、宽频率测试协议下，构建一个既能抑制 MET 非线性频响漂移，又具备结构可解释性与部署潜力的前馈校准器。** 基于这一主旨，Wiener-KAN 采用“Wiener 线性前端 + KAN 静态非线性主体”的结构化写法：前端负责注入局部频率响应先验，后端负责在共享输入协议下拟合复杂非线性映射；训练阶段再通过 MAE 与 AFMAE 的组合损失，把时域拟合与幅频一致性同时纳入优化目标。

与只看单一时域误差的写法不同，本文把实验目标统一放到四个层面：

1. 物理性能：是否能同时压低峰频漂移、灵敏度漂移和带内平均非线性误差；
2. 收敛行为：训练是否稳定、不同损失写法是否真的带来更好的优化轨迹；
3. 工程代价：性能提升是否建立在可接受的静态计算量与部署代价之上；
4. 实现边界：在 LUT 近似、LUT 插值和非 LUT 精确路径之间，哪一种更适合作为 MCU 主部署写法。

基于这些目标，本文的贡献可概括为四点：

1. 用统一 summary 链、统一图表脚本和统一 markdown 草稿，把当前仓库中的主横评、损失消融、结构消融、计算量标定和部署评估收口到同一套方法-结果链条中；
2. 保留二阶 `fit_params` 的物理解释，同时把 `Freq Drift` 的中心频率限制在 `10-128 Hz` band 内，使其不再出现异常拟合导致的爆炸值；
3. 用 STM32F405 真机时延对 `Compute Cost` 做反标，建立 `1:3:20` 的 add-normalized 默认成本模型；
4. 明确指出 Wiener-KAN 当前最值得保留的主张是“在当前 canonical projects 中同时取得最低的三项正式物理指标、`6986.7 Points/s` 的板端吞吐、`5.6 KB` 的 RAM 占用，以及显式可解释的结构先验”，同时也清楚暴露出 `KEIL-MAE` 与 Flash 仍是部署边界，从而为后续 MN 方向成稿提供更克制、更工程化的叙事基础。

## 2 系统设计与方法

### 2.1 实验数据与任务定义

当前实验协议围绕单器件、单环境、宽震级宽频率扫频测试构建。原始实验条件和后续训练窗口的稳定设置汇总如下。

**表 1  当前实验协议与数据窗口**

| Item | Value |
| --- | --- |
| Sensor sample | MTSS-1001 |
| Environment | 25 C |
| Frequency grid (saved evaluation) | 10-200 Hz, 14 points |
| Magnitude sweep | 0.24-6.0 m/s^2, 25 levels |
| Sequence duration | 4.0 s |
| Sampling rate | 2000 Hz |
| Window count | 8000 sequences |
| Reference sensitivity point | 100 Hz |
| Freq-drift fitted center-frequency band | 10-128 Hz with band-limited fit_params |
| Linearity band (official metric) | <=128 Hz, 12 points |
| Compute cost model | add:multiply:MAP = 1:3:20 |

设输入序列为 $x_{1:T}$，目标线性响应为 $y_{1:T}$，补偿器输出为 $\hat{y}_{1:T}$，则统一监督学习形式写为：

$$
\hat{y}_{1:T} = f_{\theta}(x_{1:T}).
$$

其中 $f_{\theta}(\cdot)$ 对应不同 project 中的具体模型结构。需要强调的是，当前横评中的各 project 共用相同的数据协议，但 active loss 与学习率并不完全相同，因此本稿中的主横评是**共享协议下的代表性项目对比**，而不是严格的 architecture-only 单因子实验。

### 2.2 Wiener-KAN 结构

在更上游的物理层面，MET 的大信号非线性并不是单一的“黑盒失真”。当前理论整理表明，大振幅下至少同时存在四类耦合机制：橡胶模大位移引起的几何刚化会把等效固有频率推向高频；流道内对流项不可忽略后，水动力阻力会随流速呈现振幅相关变化；离子输运中的流速与浓度梯度乘积构成乘法非线性；电极反应在大过电位下又服从 Butler-Volmer 指数关系。四者叠加后，系统同时表现出“幅值依赖的频率响应漂移”和“频率依赖的非线性失真”，因此单一静态映射或纯黑盒时序网络都不容易直接解释这种迁移规律。

为在“全物理场模型过重”和“最终补偿网络过于黑盒”之间建立一个可解释的中间层，当前仓库额外复现了三支路并联 Wiener 等效模型。该模型把不同幅值区间的主导动力学写成局部线性工作点与静态非线性映射的组合：

$$
y(t) = \sum_{i=1}^{3} f_i\big((h_i * x)(t)\big),
$$

并将每个支路的线性部分统一近似为二阶动态环节

$$
W_{\mathrm{w},i}(s) = \frac{A_i s}{s^2 + C_i s + B_i}.
$$

其中低、中、高幅值支路分别负责保持小信号频响形态、描述峰频迁移过程和重建高震级下“共振峰右移 + 通带增益抬升”的联合变化；静态映射则由分段斜率函数积分得到，以显式刻画各支路在不同输入区间的主导范围。

当前仓库已将这一过程固化为 `ex_projects/compare/wiener_parallel_modeling`，并通过 `python cli.py ep "ex_projects/compare/wiener_parallel_modeling"` 完成复现。在 25 个幅值点（`0.24-6.0 m/s^2`）上，重建结果给出 `center-frequency MAE = 1.87 Hz`、`RMSE = 2.34 Hz`，100 Hz 灵敏度则达到 `MAE = 4.53 V/m/s`、`RMSE = 5.53 V/m/s`；仿真中心频率范围为 `33.44-88.11 Hz`，与实测 `34.25-93.41 Hz` 保持接近，说明该等效模型已经能够较好重建幅值增大时的峰频右移与通带灵敏度抬升趋势。

因此，Wiener-KAN 中的 Wiener/IIR 前端并不是任意选择的工程 trick，而是来自这一并联 Wiener 等效建模所揭示的结构先验：前端负责承接幅值相关的局部线性动态，后端 KAN 再去拟合支路叠加后仍然残留的复杂静态非线性。换言之，Wiener-KAN 可以理解为对并联 Wiener 物理启发的进一步参数共享和可训练化简写，而不是凭空引入的全新黑盒结构。

Wiener-KAN 的核心思想是把 MET 的非线性补偿写成“可解释线性前端 + 灵活静态非线性主体”的级联结构：

$$
\hat{y}_{1:T} = g_{\phi}\bigl(h_{\psi}(x_{1:T})\bigr),
$$

其中 $h_{\psi}(\cdot)$ 表示按局部频率响应初始化的 Wiener/IIR 线性前端，$g_{\phi}(\cdot)$ 表示 KAN 静态非线性映射。与纯黑盒时序模型不同，这种写法将“震级相关频响漂移”优先交给线性前端编码，再把剩余非线性误差交给 KAN 处理，从而使模型在物理解释上更接近 MET 的局部线性化校准过程。

在当前仓库里，结构对照主要围绕三个方向展开：

1. 前端替换：以 CNNKAN 或随机可训练 IIR 变体观察“保留非线性主体但改变前端”的影响；
2. 主体替换：以 FRIMLP 观察“保留同一 FRI/Wiener 前端，仅把 KAN 换成 MLP”的影响；
3. 约束移除：以 `nosym` 与 `nopositive` 观察对称性约束和正定约束的必要性。

这组设计使本稿能够回答：Wiener-KAN 当前的最好综合结果究竟来自哪里，是来自 KAN 主体、线性前端先验，还是来自二者与约束的协同作用。

### 2.3 损失函数、正式指标与复杂度口径

#### 2.3.1 MAE、AFMAE 与组合损失

逐点 MAE 写为：

$$
\mathcal{L}_{\mathrm{MAE}} = \frac{1}{N}\sum_{i=1}^{N}\left|y_i-\hat{y}_i\right|.
$$

AFMAE 则首先对序列做分组能量聚合，再在对数域比较幅频相关误差：

$$
P_g(y)=\sum_{t=1}^{G}|y_{g,t}|,\qquad
P_g(\hat{y})=\sum_{t=1}^{G}|\hat{y}_{g,t}|,
$$

$$
\mathcal{L}_{\mathrm{AFMAE}}=
\frac{1}{M}\sum_{g=1}^{M}
\left|
\log(P_g(y)+\varepsilon)-\log(P_g(\hat{y})+\varepsilon)
\right|.
$$

当前标准 Wiener-KAN 基线采用的不是简单的“MAE + AFMAE 直接相加”，而是当前实现口径下的平衡组合损失：

$$
\mathcal{L}_{\mathrm{comb}} = k\,\mathcal{L}_{\mathrm{AFMAE}} + (1-k)\,\mathcal{L}_{\mathrm{MAE,bal}},\qquad k=0.2.
$$

其中 $\mathcal{L}_{\mathrm{MAE,bal}}$ 是按分组能量重新缩放后的 MAE 项。该写法的目的不是单纯追求更低的逐点误差，而是在训练阶段同时约束时域偏差和幅频响应漂移。

#### 2.3.2 正式物理指标

本文正式表格采用三类物理指标：

1. **Freq Drift (Hz)**：跨震级 compensated `fit_params` 恢复的中心频率漂移，并限制在 `10-128 Hz` band 内；
2. **Sens Drift (%)**：100 Hz 处插值灵敏度的中位数中心漂移；
3. **Linearity (%)**：`<=128 Hz` in-band 的平均非线性误差百分比，其实现形式为

$$
\mathrm{Linearity} = \frac{100}{K}\sum_{k=1}^{K}(1-R_k^2).
$$

其中 $K$ 只覆盖 `frequency_hz <= 128` 的频点，因此该指标越小越好，它不是“越大越好”的正向评分。`Freq Drift` 改用受 band 限制的 fitted center frequency 后，`No positive (stress)` 这类异常 project 不再出现 `3.26e+05` 这类明显不可信的爆炸值，而是稳定在 `58.03 Hz` 的可解释范围。

#### 2.3.3 复杂度与部署指标

当前仓库中的 `Compute Cost` 对应单样本、单时间步的加权语义操作估算：

$$
C = N_{\mathrm{add}} + 3N_{\mathrm{mul}} + 20N_{\mathrm{map}}.
$$

这里的 `1:3:20` 并非手工猜测，而是通过 `compare/compute_cost_calibration` 用 STM32F405 的板端 `ms/point` 反标得到。当前标定集覆盖 Wiener-KAN、GRU、LSTM、LSTMTransformer、1DCNN、RNN 和 TCN 共 7 个 canonical models；与旧启发式 `1:1:6` 相比，adopted model 把 log-RMSE 从 `0.2266` 降到了 `0.1341`。同时，本轮还修正了 CLI 默认 `compute_cost_model` 可能覆写旧值的问题，使这一口径真正进入默认 `-m` / `metrics` 流程，因此更适合用于 deployment-aware 的横评讨论。

在部署子章节中，进一步引入：

- `QEMU-MAE`：C 推理相对 TensorFlow 参考路径的仿真一致性误差；
- `KEIL-MAE`：真机路径相对 TensorFlow 的一致性误差；
- `KEIL speed (Points/s)`：论文图表中的板端吞吐展示；底层仍保留 `KEIL-SPEED (ms/point)` 便于换算与排障；
- Flash / RAM：由 Keil `Program Size` 行换算得到的资源占用。

### 2.4 横评、消融与部署协议边界

本文实验分为五层：

1. **主横评**：覆盖 Wiener-KAN、TCN、1DCNN、LSTM、LSTMTransformer、RNN 和 GRU；
2. **嵌入式收敛分析**：基于 `training_log.jsonl` 提取归一化 validation loss，并把主横评收敛曲线嵌入图 2、把损失消融收敛曲线嵌入图 3，而不是单独拆出 standalone 子章节；
3. **损失消融**：固定 Wiener-KAN 主体，对比 MAE+AFMAE、MAE 和 AFMAE，并用六指标雷达补充 deployment-aware 视角；
4. **结构消融**：围绕 CNN 前端替换、去对称、随机可训练 IIR、KAN→MLP 替换以及去正定 stress test 展开；
5. **On board 推理性能评估**：同时讨论跨模型部署子集、Wiener-KAN 的多优化档 Keil benchmark，以及同一训练权重下的 LUT/插值/非 LUT 实现取舍。

需要主动说明四条边界：

- 主横评中的 active loss 和学习率并不完全一致，因此这一节应理解为 canonical project comparison；
- 主横评正文中的 KEIL 列只对有合法 `board_inference_ep_path` 的模型填值，缺失项保留为 `-`，不做补旧值；
- 随机可训练 IIR 变体同时改变了初始化、可训练性和学习率，所以它更适合被解释为“前端替换代理”，而不是“仅去掉系统先验”的严格单因子实验；
- LUT 专题比较的是同一训练模型的不同导出实现，不是不同训练 project 的精度横评。

## 3 结果与讨论

### 3.1 物理漂移轨迹与主横向对比

图 1 只保留了未补偿原始响应与 Wiener-KAN 在震级维度上的物理轨迹。这里的峰频轨迹来自 `fit_params` 恢复的中心频率，并限制在 `10-128 Hz` 的正式 band 内。与前一版把多种模型叠加在同一张轨迹图上的写法相比，这种收口更直接地突出本工作的主论点：原始 MET 的峰频和 100 Hz 灵敏度都随震级明显抬升，而 Wiener-KAN 能把这两条轨迹显著压平，尤其在高震级端仍保持较稳定的物理趋势。

![Fig. 1](./fig_01_drift_trajectories.png)

图 2 则把其他模型全部收口到摘要图中。图 2(a) 将三类物理指标转换为相对未补偿原始响应的抑制率；图 2(b) 把 Wiener-KAN、TCN、1DCNN、LSTM、LSTMTransformer、RNN 和 GRU 放到同一个“静态计算量-板端吞吐”平面上，新的 canonical `RNN` 与 `1DCNN` 都已经补齐；图 2(c) 用六指标雷达图同时比较 `Freq Drift`、`Sens Drift`、`Linearity`、`Compute Cost`、`KEIL speed` 和 `KEIL RAM Usage`；图 2(d) 则直接把主横评收敛曲线嵌入同一图组，并统一使用线性坐标。这样处理后，“物理指标最优”“速度最快”“RAM 最省”“部署一致性最好”这几种结论可以在同一页里清楚区分，而不会再因为图表拆散而削弱对比强度。

![Fig. 2](./fig_02_horizontal_summary.png)

**表 2  主横向对比结果（共享协议下的 canonical projects）**

| Model | Freq Drift (Hz) | Sens Drift (%) | Linearity (in-band, %) | Compute Cost | KEIL-MAE | KEIL speed (Points/s) | RAM (KB) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Wiener-KAN | 2.34 | 9.09 | 0.511 | 5066 | 7.11e-03 | 6986.7 | 5.6 |
| TCN | 2.65 | 16.08 | 0.517 | 8704 | 1.20e-06 | 935.7 | 106.7 |
| 1DCNN | 3.72 | 16.24 | 0.920 | 3984 | 5.51e-04 | 2009.9 | 50.9 |
| LSTM | 4.50 | 13.80 | 0.512 | 7520 | 5.07e-02 | 1426.3 | 58.7 |
| LSTMTransformer | 4.72 | 18.38 | 0.567 | 8192 | 5.05e-03 | 1461.5 | 83.7 |
| RNN | 6.68 | 23.75 | 0.726 | 2816 | 8.74e-02 | 3652.9 | 58.7 |
| GRU | 7.40 | 27.15 | 0.726 | 5856 | 2.45e-03 | 1660.1 | 58.7 |

从表 2 和图 2 可以归纳出四个更具体的观察：

1. **Wiener-KAN 当前最有说服力的证据，是它在这组 canonical projects 中同时给出最低的三项正式物理指标，并进一步拿到最高板端吞吐与最低 RAM。** 在主横评中，它的 `Freq Drift = 2.34 Hz`、`Sens Drift = 9.09%` 与 `Linearity = 0.511%` 都是最低值；同时 `Compute Cost = 5066` 明显低于 TCN / LSTM / LSTMTransformer / GRU，`KEIL speed = 6986.7 Points/s` 也是当前最高，而 `RAM = 5.6 KB` 仍是该组最低。
2. **Wiener-KAN 相对 TCN 的对照更适合被写成“物理指标占优，复杂度和板端吞吐也显著占优，但部署一致性仍偏弱”。** 与 TCN 相比，Wiener-KAN 的 `Freq Drift` 再降低 `11.72%`，`Sens Drift` 再降低 `43.46%`，`Linearity` 再降低 `1.13%`，`Compute Cost` 再降低 `41.80%`，板端吞吐提升到 `7.47x`；但 TCN 仍有更低 `KEIL-MAE`。
3. **1DCNN 仍是更强的部署导向卷积基线，但其优势主要体现在一致性而不是速度。** 当前 canonical 1DCNN 已补齐 `KEIL-MAE = 5.51e-04` 与 `KEIL speed = 2009.9 Points/s`，在 board fidelity 上仍优于 Wiener-KAN；但它的 `Freq Drift`、`Sens Drift` 与 `Linearity` 仍分别高出 `59.11%`、`78.63%` 和 `80.01%`，板端吞吐也显著低于优化后的 Wiener-KAN。
4. **RNN 的最低复杂度既没有换来更好的物理指标，也没有换来最高吞吐。** 它拥有最低 `Compute Cost = 2816`，但 `KEIL speed = 3652.9 Points/s` 仍低于 Wiener-KAN，`KEIL-MAE` 还恶化到 `8.74e-2`，且三项物理指标都明显落后于 Wiener-KAN、TCN 和 LSTM，说明在当前任务上，“极简模型”既不能替代结构先验，也不会自动换来最优部署实现。

因此，在新的 band-limited fit 指标、六指标雷达和 deployment-aware 展示下，Wiener-KAN 更适合被写成一种**在当前对比集合内，同时兼顾三项正式物理指标、最高板端吞吐、最低 RAM 与中低静态复杂度的结构化方案**；但 `KEIL-MAE` 与 Flash 仍需单独交代。

### 3.2 收敛曲线与损失函数消融

按照本轮重构后的图表逻辑，收敛曲线不再单独拆出 standalone 小节，而是直接嵌入横评和损失消融图中。图 2(d) 已经给出了主横评 7 个 canonical models 的线性坐标归一化 validation loss 曲线：Wiener-KAN 在大约 `150-200` epoch 后进入更低且更稳的收敛平台，而 RNN / LSTM / 1DCNN 等路径虽然前期下降更快，但后期平台更高或波动更明显。这一现象与表 2 中“三项正式物理指标最低”的结果是一致的：Wiener-KAN 的优势不是来自某个偶然的最终点，而是来自更平稳的整体优化轨迹。

图 3 则把损失消融的正式结果、六指标雷达和线性收敛曲线放在同一张图里。图 3(a)-(c) 直接给出 `Freq Drift`、`Sens Drift` 与 in-band `Linearity`；图 3(d) 用六指标雷达比较三种 Wiener-KAN loss 变体；图 3(e) 则给出三种 loss 的归一化 validation loss 曲线。

![Fig. 3](./fig_03_loss_ablation.png)

**表 3  损失函数消融结果**

| Variant | Active loss | Freq Drift (Hz) | Sens Drift (%) | Linearity (in-band, %) | Compute Cost | QEMU-MAE | KEIL-MAE | KEIL speed (Points/s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MAE+AFMAE | MAE+AFMAE | 2.34 | 9.09 | 0.511 | 5066 | 7.114e-03 | 7.114e-03 | 6986.7 |
| MAE | MAE | 13.00 | 20.28 | 0.793 | 5066 | 2.137e-02 | 2.137e-02 | 6986.7 |
| AFMAE | AFMAE | 4.00 | 21.06 | 1.068 | 5066 | 3.968e-03 | 3.968e-03 | 6986.7 |

受限 fit 峰频口径让这一节的结论重新变得更清晰：**组合损失不仅在 `Sens Drift` 与 `Linearity` 上领先，在 `Freq Drift` 上也重新获得了明显优势。** 相对纯 `MAE`，`MAE+AFMAE` 把 `Freq Drift` 再降低 `82.03%`；相对纯 `AFMAE`，该降幅为 `41.64%`。而另外两项指标上的优势仍然同样显著：

- 相对纯 `MAE`，`MAE+AFMAE` 把 `Sens Drift` 再降低 `55.17%`，把 `Linearity` 再降低 `35.55%`；
- 相对纯 `AFMAE`，`MAE+AFMAE` 把 `Sens Drift` 再降低 `56.82%`，把 `Linearity` 再降低 `52.14%`。

图 3(e) 的线性收敛曲线进一步说明，这种优势不是偶然的最终点差异，而是整个优化过程更稳：组合损失的曲线虽然前期下降稍慢，但在约 `150` epoch 后进入最低平台；纯 `MAE` 与纯 `AFMAE` 的后期平台都更高。表 3 还补入了本轮自动 QEMU/Keil 复验后的部署列，可以更紧凑地读出另一个关键事实：三种同结构 Wiener-KAN loss 变体已经共享优化后的最近邻 LUT / IIR benchmark-only 导出路径，因此板端吞吐统一落在 `6986.7 Points/s`，部署侧差异主要收缩为 `QEMU-MAE` / `KEIL-MAE`。其中纯 `MAE` 为 `2.137e-02`，纯 `AFMAE` 为 `3.968e-03`，组合损失则为 `7.114e-03`。因此，本节的最终表述应收束为：**loss 消融真正区分开的是物理校准质量与优化稳定性，而不是同结构 Wiener-KAN 的最近邻 LUT 部署速度。** 对当前 MET 任务而言，更稳妥的写法仍然是用组合损失同时约束时域和幅频两类误差，并把部署侧结果作为“实现路径已对齐”的辅助证据。

### 3.3 结构消融：受限 fit 指标同时保留稳定性与结构排序

图 4 和表 4 汇总了结构消融结果。与旧版容易被带外异常峰频扭曲的写法相比，band-limited fit 指标同时满足两件事：一方面，`No positive (stress)` 不再出现爆炸值，而是稳定在 `58.03 Hz`；另一方面，Wiener-KAN 重新回到该组最低 `Freq Drift`。也就是说，**新的正式指标既保留了稳定性，也恢复了更符合当前结构直觉的排序。**

![Fig. 4](./fig_04_structure_ablation.png)

**表 4  结构消融结果**

| Variant | Freq Drift (Hz) | Sens Drift (%) | Linearity (in-band, %) | Compute Cost |
| --- | --- | --- | --- | --- |
| Wiener-KAN | 2.34 | 9.09 | 0.511 | 5066 |
| CNNKAN | 2.43 | 9.22 | 0.883 | 5074 |
| No symmetry | 10.91 | 10.61 | 2.109 | 5066 |
| Random trainable IIR | 5.34 | 21.38 | 3.216 | 5066 |
| FRIMLP | 5.82 | 27.48 | 0.782 | 11272 |
| No positive (stress) | 58.03 | 50.87 | 38.586 | 5066 |

可以得到以下判断：

1. **对称性与正定约束仍然是必要约束，只是“不再需要靠爆炸数值来证明它们重要”。** 去掉对称性后，`Freq Drift` 升到 `10.91 Hz`，`Linearity` 升到 `2.109%`；去掉正定约束后，三项物理指标都显著恶化，虽然现在数值被稳定在 `58.03 Hz` 而不是旧稿中的异常爆炸值，但排序和结论仍然清楚。
2. **随机化且可训练的 IIR 前端显著变差。** 该变体的 `Sens Drift = 21.38%`，比 Wiener-KAN 高 `135%` 以上，`Linearity` 也恶化到 `3.216%`，说明“任意可训练前端”不能直接替代当前的系统初始化先验。
3. **FRIMLP 说明仅保留 Wiener/FRI 前端并不够，KAN 主体仍然有明确贡献。** 在新的正式口径下，FRIMLP 的 `Freq Drift = 5.82 Hz`、`Sens Drift = 27.48%`、`Linearity = 0.782%`，且 `Compute Cost = 11272`（约为 Wiener-KAN 的 `2.23x`），三项物理指标与复杂度都明显落后于 Wiener-KAN。
4. **CNNKAN 与 Wiener-KAN 的差距仍然不大，但当前数据更偏向 Wiener-KAN。** CNNKAN 的 `Freq Drift = 2.43 Hz` 接近 Wiener-KAN 的 `2.34 Hz`，但 `Linearity` 明显更差 (`0.883%` vs. `0.511%`)，而 `Compute Cost` 仅略高到 `5074`。因此，当前证据更支持“Wiener-KAN 在这组结构对照里综合更占优”，而不是“Wiener/IIR 前端是唯一可行前端”。

综上，band-limited fit 指标让结构消融同时满足“异常值被压住”和“Wiener-KAN 排序不被反常带外拟合扭曲”两项目标，因此更适合作为后续正式论文口径。

### 3.4 On board 推理性能评估

当前部署子章节直接保留已经完成合法板端路径并刷新 `metrics.json` 的 canonical models，因此已经同时包含 RNN 与 canonical 1DCNN。图 5 与表 5 展示了这些对象在 QEMU / Keil 一致性、板端吞吐和资源占用上的权衡，同时图 5(e) 额外给出了 Wiener-KAN 在多种 Keil 编译优化档下的吞吐对比。

![Fig. 5](./fig_05_onboard_inference.png)

**表 5  MCU 部署子集结果**

| Model | QEMU-MAE | KEIL-MAE | KEIL speed (Points/s) | Flash (KB) | RAM (KB) |
| --- | --- | --- | --- | --- | --- |
| Wiener-KAN | 7.114e-03 | 7.114e-03 | 6986.7 | 719.2 | 5.6 |
| TCN | 1.197e-06 | 1.197e-06 | 935.7 | 16.4 | 106.7 |
| 1DCNN | 5.513e-04 | 5.513e-04 | 2009.9 | 12.3 | 50.9 |
| LSTM | 5.070e-02 | 5.070e-02 | 1426.3 | 13.8 | 58.7 |
| LSTMTransformer | 5.049e-03 | 5.049e-03 | 1461.5 | 19.9 | 83.7 |
| RNN | 8.739e-02 | 8.739e-02 | 3652.9 | 10.0 | 58.7 |
| GRU | 2.451e-03 | 2.451e-03 | 1660.1 | 12.7 | 58.7 |

部署结果显示出非常清晰的工程 trade-off：

- **Wiener-KAN 经过最近一轮 LUT / IIR benchmark-only 优化后，已经成为当前部署子集里最快的板端实现。** 它在 STM32F405 上达到 `6986.7 Points/s`，约为 RNN 的 `1.91x`、TCN 的 `7.47x`，同时 `RAM` 仅 `5.6 KB`；需要单独交代的代价则仍是 `7.11e-3` 的 `KEIL-MAE`。
- **TCN 仍代表当前最强的 board fidelity 基线，但吞吐最低。** 它以 `1.20e-6` 的 `KEIL-MAE` 给出当前最佳一致性，却只有 `935.7 Points/s` 的最低吞吐，说明极致 fidelity 与高吞吐在当前导出链上仍然存在明显张力。
- **1DCNN 仍是更强的卷积部署基线，但优势主要体现在一致性而不是速度。** 当前 canonical 1DCNN 达到 `2009.9 Points/s`，并把 `KEIL-MAE` 压到 `5.51e-4`；但它在三项物理指标上的正式表现仍明显弱于 Wiener-KAN，板端吞吐也只有后者的约 `28.8%`。
- **RNN 的最低复杂度并没有换来最优部署结果。** 它虽然拥有最低 `Compute Cost = 2816`，却只达到 `3652.9 Points/s`，仍低于 Wiener-KAN，且 `KEIL-MAE = 8.74e-2`，说明“结构最简”并不会自动导向“速度最快 + 一致性最好”。
- **Wiener-KAN 的 Flash 占用仍是当前部署子集里最高的一档，但已经不再逼近 1 MB 上限。** 当前 published/default 导出实现约占 `719.2 KB` Flash，明显高于序列模型，但相较旧版 `1 MB` 级风险已经回落到更可控的工程边界。

多优化档 benchmark 则给出了第二层工程结论。对 Wiener-KAN 基线而言，`project_default` 与 `-O2` 在本轮测量中基本重合，均为 `6986.7 Points/s`；`-O0` 现已可以构建并运行，对应 `2234.5 Points/s`、`728.1 KB Flash` 与 `86.8 KB RAM`；`-Ofast + LTO` 仅把吞吐进一步提高到 `7059.3 Points/s`，增幅约 `1.04%`。也就是说，当前主实现已经基本吃到结构性优化收益，继续上探编译器档位只能带来很小的额外吞吐收益，而更值得保留的变化反而是 LUT 存储压缩后所有 profile 都不再受旧版 Flash 溢出问题卡死。

### 3.5 Compute Cost 标定：从启发式 `1:1:6` 更新到真机标定 `1:3:20`

为了让静态 `Compute Cost` 更接近板端真实代价，本文额外对 `add:multiply:MAP` 权重做了平台标定。标定对象覆盖 Wiener-KAN、GRU、LSTM、LSTMTransformer、1DCNN、RNN 和 TCN 共 7 个已经完成 STM32F405 部署的模型。标定时固定 `add_weight = 1.0`，在对数网格上搜索 `mul_weight` 与 `map_weight`，再通过整体缩放系数把静态加权单位拟合到 `ms/point`；图 6 则把最终对照统一换算成 `Points/s`，以便与图 5 的 on-board 展示保持一致。

![Fig. 6](./fig_06_compute_cost_calibration.png)

当前搜索结果为：

- `pure fit best`: `1 : 652.5750 : 3326.9858`
- `regularized fit best`: `1 : 3.1383 : 20.1587`
- `adopted rounded model`: `1 : 3 : 20`

与旧启发式 `1:1:6` 相比，新模型把对数域 `RMSE` 从 `0.2266` 降到 `0.1341`，最大相对误差从 `42.01%` 降到 `23.38%`。更重要的是，新的标定集已经显式纳入 RNN 与 canonical 1DCNN，因此 adopted model 不再只是对循环模型子集拟合得更好，而是对当前正式横评中的 7 类代表模型都更稳妥。同步修正 CLI 默认 `compute_cost_model` 并批量重刷 project 后，主横评的静态复杂度当前分别为 Wiener-KAN `5066`、TCN `8704`、1DCNN `3984`、LSTM `7520`、LSTMTransformer `8192`、RNN `2816`、GRU `5856`；其中 TCN 仍对应最高静态 cost 与最低板端吞吐，RNN 与 1DCNN 则说明“更低 cost / 更高速度”未必意味着更好的物理校准。

换言之，`Compute Cost` 仍然不是实测时间，但它现在已经可以作为与 STM32F405 板端速度明显更对齐的 deployment-aware 代理指标。图 2(b) 中各模型在“静态复杂度-板端吞吐”平面上的相对位置，以及图 6 中 measured vs. predicted 的对照，都应按这套 `1:3:20` 口径解读。

### 3.6 Wiener-KAN 的 LUT 实现取舍：插值是最有说服力的折中点

除了跨模型部署子集外，本文还比较了 Wiener-KAN 同一训练权重下的三种 MCU 导出实现：`LUT nearest`、`LUT + interp` 与 `No LUT exact`。这组实验只改变导出方式，不改变训练 project，因此它反映的是**实现取舍**，而不是训练差异。

**表 6  Wiener-KAN 不同导出实现的 MCU 结果**

| Variant | QEMU-MAE | KEIL-MAE | KEIL speed (Points/s) | Flash (KB) | RAM (KB) |
| --- | --- | --- | --- | --- | --- |
| LUT nearest | 7.114e-03 | 7.114e-03 | 6986.7 | 719.2 | 5.6 |
| LUT + interp | 1.902e-04 | 1.902e-04 | 3844.8 | 723.5 | 5.6 |
| No LUT exact | 6.517e-07 | 6.517e-07 | 45.0 | 33.7 | 21.2 |

这组结果非常有启发性：

1. **最近邻 LUT 现在已经不只是“可接受默认实现”，而是当前最快的 Wiener-KAN 路径。** 它把板端吞吐推到 `6986.7 Points/s`，同时把 Flash 压到 `719.2 KB`、RAM 压到 `5.6 KB`；代价则是 `7.11e-3` 的 `KEIL-MAE`。
2. **LUT + 一阶线性插值仍然是当前最有说服力的工程折中点。** 相对最近邻 LUT，它把 `KEIL-MAE` 再降低 `97.33%`，同时仍保持 `3844.8 Points/s`，相当于保留了最近邻 LUT 约 `55.0%` 的吞吐；换算成低层时延，单位点开销增加约 `81.7%`，Flash 也只增加约 `0.60%`。
3. **No-LUT exact 更像精度上界而不是默认部署方案。** 它把 `KEIL-MAE` 进一步压到 `6.52e-7`，同时把 Flash 降到 `33.7 KB`；但吞吐骤降到 `45.0 Points/s`，约比最近邻 LUT 慢 `155x`。这说明当前 Flash 的主要来源确实是 LUT 表，而精确运行时求值虽然节省存储，却不适合实时 STM32 路径。

因此，如果论文部署部分希望突出“板端吞吐极限”，当前最近邻 LUT 已足以支撑这一叙事；但如果更强调 `KEIL-MAE` 的说服力、同时又不愿放弃 `kPoints/s` 级速度，那么 `LUT + interp` 仍是更平衡、更容易被审稿人接受的主展示版本。

### 3.7 适用范围与局限性

为了避免把当前结果写得超过证据边界，本文最后明确五项局限：

1. **数据边界仍然偏窄。** 当前实验基于单器件（MTSS-1001）和 25 C 单环境，不具备跨器件、跨温度泛化结论。
2. **横评不是严格等超参实验。** Wiener-KAN 使用 MAE+AFMAE，其余多数基线使用 MAE；学习率也并不完全一致，因此表 2 只能支撑“当前 canonical projects 的真实比较”。
3. **虽然新的 band-limited fit 指标让 Wiener-KAN 重新回到三项物理指标第一，但这种领先仍然建立在当前 canonical projects 上。** `KEIL-MAE` 与 Flash 压力仍未解决，因此不能把它写成“毫无代价的全能方案”。
4. **`Compute Cost` 的默认权重已经更合理，但仍然是平台相关代理模型。** `1:3:20` 来自 STM32F405，不应被写成所有 MCU 的普适常数。
5. **部署链条尚未完全收口。** Wiener-KAN 的最近邻 LUT 实现已经把速度推到 `6986.7 Points/s`，并把 Flash 压到约 `719 KB`；但 `KEIL-MAE` 仍明显高于更高保真路径。`LUT + interp` 和 `No-LUT exact` 说明当前仍存在可继续权衡的精度/速度/存储边界，最终实现仍需结合目标应用选择。

## 4 结论

本文整合了当前仓库中与 Wiener-KAN 相关的主横评、收敛曲线、损失消融、结构消融、计算量标定和嵌入式部署结果，形成了一篇适合继续向 MN 方向收敛的中文论文草稿。基于当前正式数据，可以得出以下结论：

1. 在新的 band-limited fit `Freq Drift` 定义下，就当前 canonical projects 而言，Wiener-KAN 同时给出了最低的 `Freq Drift`、`Sens Drift` 与 in-band `Linearity`，因此三项正式物理指标在这组对比中均占优。
2. Wiener-KAN 并不是最低 `Compute Cost` 的模型，但在当前 canonical deployment subset 里已经成为最快 `KEIL speed` 的实现；它以 `5066` 的中低静态成本保住了当前最低的三项正式物理指标，并达到 `6986.7 Points/s` 的板端吞吐与 `5.6 KB` 的 RAM 占用，因此它最主要的证据已进一步收束为**物理指标、速度与内存占用的联合优势**；但 `KEIL-MAE` 与 Flash 仍然提醒我们，它不是“无代价的最优部署实现”。
3. `MAE+AFMAE` 组合损失仍然比纯 `MAE` 或纯 `AFMAE` 更稳，而且在新的正式口径下对 `Freq Drift`、`Sens Drift` 与 `Linearity` 三项指标都表现出明确优势；本轮补跑还说明同结构 loss 变体的最近邻 LUT 部署吞吐已对齐到 `6986.7 Points/s`，因此新的收敛曲线与物理指标，而不是板端速度差异，才是支持这一判断的主要证据。
4. 修正 CLI 默认覆写后，`Compute Cost` 的 `1:3:20` 默认权重已经真正进入默认流程，再配合 Wiener-KAN 的多优化档 Keil benchmark 与 LUT/插值专题实验，使本文的工程论证比旧稿更扎实：前者让静态复杂度更接近板端时延，后者则把速度、精度和存储之间的 trade-off 明确摆到了台面上。

因此，本文更建议把 Wiener-KAN 写成一种**以物理响应稳定化和 deployment-aware 效率为主目标、兼顾结构化建模与 MCU 落地潜力的 MET 前馈校准方案**。沿着这一方向，后续成稿应继续补齐更严格的 protocol、更加干净的前端 2x2 消融，以及以 `LUT + interp` 为候选主线的部署优化。

## 附录：图表与数据复现说明

本草稿对应的图表、源码和机器可读数据都放在同一目录中：

- 绘图脚本：`generate_figures.py`
- 机器可读数据：`paper_data.json`
- 表格导出：`generated_tables.md`
- 图片：`fig_01_drift_trajectories.png`、`fig_02_horizontal_summary.png`、`fig_03_loss_ablation.png`、`fig_04_structure_ablation.png`、`fig_05_onboard_inference.png`、`fig_06_compute_cost_calibration.png`

这意味着后续若需要替换项目、重绘图表或更新正文数字，可以先更新统一数据源，再重新运行绘图脚本，而不必手工逐图改值。
