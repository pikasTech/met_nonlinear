# 论文边缘设备推理评估方法说明

## 写作定位

本文档用于沉淀论文边缘设备推理评估部分的长期稳定写法。它既是仓库内的长期参考文档，也是后续撰写论文 `Methods` 与部署子章节时可直接展开的中文中间稿。

本文档只描述实验目的、实验设计、执行流程、必要公式与正式取值口径，不记录一次性的 benchmark 数字，也不承载某一轮真机调试流水账。

## 实验目的

当前边缘设备推理评估服务于四个核心问题：

1. 部署可行性：验证候选模型是否能从 TensorFlow 训练路径稳定导出为可在 MCU 侧执行的 C 推理实现。
2. 数值一致性：验证导出的 C 推理在 QEMU 与 Keil 真机环境下，是否保持与 TensorFlow 参考路径一致的输出行为。
3. 资源代价：量化模型在目标平台上的参数规模、语义计算代价、Flash / RAM 占用与板端执行时间。
4. 工程边界：区分“静态复杂度估算”“仿真环境一致性”“真机一致性”和“板端实测耗时”这几个来源不同、物理意义不同的指标，避免把它们混写成单一的“速度”结论。

因此，当前部署评估的目标不是只证明模型“能跑起来”，而是系统回答：该模型是否可部署、是否数值可信、部署代价有多大，以及这些代价来自哪里。

## 实验设计

### 设计原则

当前部署评估遵循以下设计原则：

1. 部署评估只针对已经完成训练与离线评估的正式 project，不单独创建脱离训练结果的临时模型。
2. 训练 project 通过 `config.json.board_inference_ep_path` 绑定对应的部署 EP 任务，部署结果最终再回写到训练 project 的 `metrics.json`。
3. 部署评估拆分为五个互补维度：静态复杂度、QEMU 数值一致性、Keil 真机一致性、编译后资源占用和板端时序测量。
4. 正式论文部署表中，只能使用稳定产物文件中的字段，不能用临时串口日志或屏幕截图代替。

### 五层评估结构

当前部署章节建议按以下五层结构组织：

1. 静态复杂度层
   - 来源：`projects/.../data/compute_analysis.json`
   - 作用：衡量模型单时间步语义运算代价
2. QEMU 一致性层
   - 来源：`ex_projects/.../data/benchmark_summary.json`、`validation_comparison.json`
   - 作用：验证导出的 C 推理在仿真环境中是否与 TensorFlow 输出一致
3. Keil 真机一致性层
   - 来源：`ex_projects/.../data/keil_benchmark_summary.json`、`keil_validation_comparison.json`
   - 作用：验证真机执行结果是否仍与 TensorFlow 参考路径一致
4. 资源占用层
   - 来源：`keil_project/MDK-ARM/output/build_output_<target>.txt`
   - 作用：提取 Flash / RAM 代价
5. 板端时序层
   - 来源：`keil_benchmark_summary.json.parsed_output`
   - 作用：提取 `cycles_per_iter`、`wall_time_per_iter_ms` 等时序量

### 正式对象边界

当前只有具备 native board-inference 支持的模型，才应进入正式部署子章节。当前支持集合包括：

- `frikan`
- `lstm`
- `grn`
- `lstm_transformer`
- `onedcnn`
- `tcn`
- `wavenet2`
- `wavenet3`

因此，`RNN` 当前仍应保留在精度横评部分，而不应写成正式部署对象。

### 稳定产物与自动汇总边界

当前部署相关稳定产物包括：

- 静态复杂度：`projects/.../data/compute_analysis.json`
- 训练项目部署入口：`projects/.../config.json` 中的 `board_inference_ep_path`
- QEMU 汇总：`ex_projects/.../data/benchmark_summary.json`
- QEMU 细节对比：`ex_projects/.../data/validation_comparison.json`
- Keil 汇总：`ex_projects/.../data/keil_benchmark_summary.json`
- Keil 细节对比：`ex_projects/.../data/keil_validation_comparison.json`
- 编译资源输出：`ex_projects/.../keil_project/MDK-ARM/output/build_output_<target>.txt`
- 训练项目统一 summary：`projects/.../data/metrics.json`

这里必须写清一个边界：

- `metrics.json` 目前只自动汇总 `QEMU-MAE`、`KEIL-MAE` 与 `KEIL-SPEED`；
- Flash / RAM、`cycles_per_iter` 与更细的 validation 对比细节，仍保留在部署侧产物中，论文部署子章节需要单独读取。

## 实验流程

当前边缘设备推理评估的正式执行流程如下：

1. 在训练 project 的 `config.json` 中配置合法的 `board_inference_ep_path`；
2. 先完成训练 project 的标准训练与离线评估，确保权重、`compute_analysis.json` 与 `metrics.json` 可用；
3. 调用 `python cli.py ep "ex_projects/inference/qemu-c-inference/TASK_NAME"` 运行 QEMU 侧 benchmark 与 validation；
4. 调用 `python cli.py ep keil-bench "ex_projects/inference/qemu-c-inference/TASK_NAME"` 运行真机构建、烧录、串口抓取与 validation；
5. 从 QEMU / Keil 产物中提取聚合对比指标、编译资源与时序数据；
6. 通过 `python cli.py --metrics PROJECT_NAME` 或自动刷新链，将 `QEMU-MAE`、`KEIL-MAE` 与 `KEIL-SPEED` 回写到训练 project 的 `metrics.json`；
7. 论文部署主表从 `metrics.json` 读取统一字段，资源占用与 cycle 指标则从部署侧产物补充读取。

与代码的对应关系为：

1. `ProjectManager.evaluate()` 或 `python cli.py -m PROJECT_NAME` 会生成 `compute_analysis.json`；
2. `metrics_summary.py` 根据训练 project 的 `board_inference_ep_path` 读取 `benchmark_summary.json` 与 `keil_benchmark_summary.json`；
3. `metrics_summary.py` 将 `comparison.mae` 与单位点时延汇总为 `QEMU-MAE`、`KEIL-MAE` 与 `KEIL-SPEED`；
4. 资源占用与更细的串口解析数据保留在部署 EP 自身目录中，不自动回写为所有训练项目的内置字段。

## 必要公式与实现口径

### 静态复杂度

当前 `Compute Cost` 来源于 `compute_analysis.json.estimated_cost.weighted_units.total`，其基本形式为：

$$
C_{\mathrm{step}}
=
w_{\mathrm{add}} N_{\mathrm{add}}
+
w_{\mathrm{mul}} N_{\mathrm{mul}}
+
w_{\mathrm{map}} N_{\mathrm{map}}
$$

其中：

- $N_{\mathrm{add}}$：单样本、单时间步下的加法计数；
- $N_{\mathrm{mul}}$：单样本、单时间步下的乘法计数；
- $N_{\mathrm{map}}$：单样本、单时间步下的非线性映射次数；
- $(w_{\mathrm{add}}, w_{\mathrm{mul}}, w_{\mathrm{map}}) = (1, 1, 6)$ 为当前默认平台成本模型。

因此，论文中应把 `Compute Cost` 表述为“单样本、单时间步语义操作加权估算”，而不是完整序列的端到端实测延迟。

### QEMU 数值一致性

令 $\hat{y}^{\mathrm{TF}}$ 表示 TensorFlow 参考输出，$\hat{y}^{\mathrm{QEMU}}$ 表示 QEMU 环境下的 C 推理输出，则其聚合误差可写为：

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

当前正式自动汇总字段 `QEMU-MAE` 的取值来源是：

- `benchmark_summary.json.comparison.mae`

若论文需要展开更细的逐记录对比过程，再引用 `validation_comparison.json` 作为补充材料；主表仍以自动汇总字段为准。

### Keil 真机数值一致性

令 $\hat{y}^{\mathrm{KEIL}}$ 表示真机环境下的 C 推理输出，则聚合误差定义为：

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

当前正式自动汇总字段 `KEIL-MAE` 的取值来源是：

- `keil_benchmark_summary.json.comparison.mae`

因此，论文中应将 `QEMU-MAE` 与 `KEIL-MAE` 都写成“导出 C 推理相对 TensorFlow 参考路径的聚合一致性误差”，而不是单个采样点误差。

### 编译后资源占用

当前 Flash 与 RAM 占用从 `build_output_<target>.txt` 的 `Program Size` 行提取。推荐公式为：

$$
\mathrm{Flash} = \mathrm{Code} + \mathrm{RO\text{-}data}
$$

$$
\mathrm{RAM} = \mathrm{RW\text{-}data} + \mathrm{ZI\text{-}data}
$$

如果论文需要保留更原始的编译器口径，可以在附录中同时列出 `Code`、`RO-data`、`RW-data` 与 `ZI-data` 四项。

### 板端时序指标

当前 `metrics.json` 中的 `KEIL-SPEED` 定义为单位点 wall-clock 时延：

$$
S_{\mathrm{KEIL}}
=
\frac{t_{\mathrm{iter}}^{\mathrm{ms}}}
{N_{\mathrm{record}} \cdot T_{\mathrm{seq}}}
$$

其中：

- $t_{\mathrm{iter}}^{\mathrm{ms}}$：`wall_time_per_iter_ms`
- $N_{\mathrm{record}}$：benchmark / validation 所覆盖的记录数
- $T_{\mathrm{seq}}$：单条记录的序列长度

也就是说：

$$
\mathrm{KEIL\text{-}SPEED\ (ms/point)}
=
\frac{\mathrm{wall\_time\_per\_iter\_ms}}
{\mathrm{record\_count} \cdot \mathrm{seq\_len}}
$$

`cycles_per_iter` 则是板端 DWT cycle counter 视角下的补充指标，适合同平台横向比较，但不应与 `ms/point` 或 QEMU host 侧时间混写为同一单位。

## 正式表格字段建议

当前部署子章节中最适合进入论文正文或主图表的字段包括：

- `Compute Cost`
- `QEMU-MAE`
- `KEIL-MAE`
- `KEIL-SPEED`
- Flash / ROM
- RAM

建议保留为同平台补充分析字段的包括：

- `cycles_per_iter`
- `cycles_per_point`
- 更细粒度的 `validation_comparison` 图表或逐记录误差

## 写作边界

在论文部署方法章节中，当前写法应严格遵循以下边界：

- 静态复杂度、动态一致性、资源占用与板端时序必须分维度表述；
- 不把 `Compute Cost` 写成完整序列的实测延迟；
- 不把 QEMU host 侧耗时、Keil cycles 和 Keil wall-clock 混写为同一种“速度”；
- 主速度数字应来自 benchmark 主路径，而不是带有额外串口与 validation 开销的调试路径；
- 不为没有合法 `board_inference_ep_path` 的 project 虚构部署字段；
- 当部署产物缺失时，应明确标成“当前未完成部署评估”或“当前平台部署失败”，而不是默默补旧值。

## 相关文档

- [compute_analysis.md](compute_analysis.md)
- [edge_device_emulation.md](edge_device_emulation.md)
- [metrics.md](metrics.md)
- [ep.md](ep.md)
- [keil_stm32f405_programming.md](keil_stm32f405_programming.md)
