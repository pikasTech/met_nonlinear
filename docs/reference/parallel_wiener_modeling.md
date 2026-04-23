# 并联 Wiener 等效建模

## 写作定位

本文档用于收敛电化学检波器大信号幅频耦合非线性的并联 Wiener 等效建模入口、配置约束、产物与判定标准。它既服务于 `ex_projects/compare/wiener_parallel_modeling` 的长期复现，也服务于 Wiener-KAN 方法章节中“Wiener/IIR 前端为何具有物理先验基础”的写作说明。

本文档只记录稳定入口、模型结构和验收口径，不记录一次性的调参过程或带时间戳的实验流水账。

## 功能概述

`python cli.py ep "ex_projects/compare/wiener_parallel_modeling"` 用于复现电化学检波器在不同输入幅值下的幅度依赖频率响应漂移，并输出频响重建图、支路静态映射图、摘要 JSON 与 Markdown 报告。

这类任务的目标不是训练 project 横评，也不参与项目级 `metrics.json` 刷新链；它的作用是把“大信号多物理场耦合非线性”压缩成一个可解释的等效模型，用于支撑方法章节、结构消融解释和 Wiener-KAN 前端先验论证。

## 理论动机

电化学检波器在大信号工况下的非线性至少同时包含四类来源：

1. 橡胶模大位移导致的机械几何非线性，会使等效刚度随振幅增大而上升；
2. 流道内对流项不可忽略后的流体惯性非线性，会使水动力阻力呈现振幅相关变化；
3. 离子输运中的对流项与浓度梯度乘积，会形成典型的乘法非线性；
4. 电极反应在大过电位下服从 Butler-Volmer 指数关系，不再满足小信号线性近似。

因此，系统不仅会出现“幅值依赖的峰频迁移和灵敏度漂移”，还会出现“频率依赖的非线性失真”。并联 Wiener 等效模型的作用，就是在全物理场方程过重、最终补偿器又过于黑盒之间，提供一个更可解释的中间层。

## 模型结构

并联 Wiener 等效模型写为：

$$
y(t) = \sum_{i=1}^{3} f_i\big((h_i * x)(t)\big)
$$

其中三个支路分别对应低幅值、中幅值和高幅值区间的主导动力学。每个支路的线性部分统一近似为二阶动态环节：

$$
W_{\mathrm{w},i}(s) = \frac{A_i s}{s^2 + C_i s + B_i}
$$

其中：

- $A_i$ 控制支路增益比例；
- $B_i$ 对应局部等效固有频率相关系数；
- $C_i$ 对应局部阻尼相关系数。

静态非线性映射不直接手写复杂函数，而是先定义分段斜率函数，再通过积分得到：

$$
f_i(x) = \int_0^x k_i(\xi)\,\mathrm{d}\xi
$$

当前 canonical 配置使用三个支路和三角形斜率控制点：

- 低幅值支路：在原点附近通过 `x_btn` 保持较高斜率，负责维持小信号频响形态；
- 中幅值支路：负责描述峰频与增益开始迁移的主导区间；
- 高幅值支路：通过 `x_top` 在大输入端维持持续作用，负责重建高震级端的峰频右移和通带灵敏度抬升。

## 仓库落点

当前实现固定落在以下位置：

- `src/visualization/wiener_parallel_modeling.py`：并联 Wiener 建模与报告生成主实现；
- `src/core/external_cli_handler.py`：`analysis_type = "wiener-parallel-modeling"` 的 EP 分发入口；
- `ex_projects/compare/wiener_parallel_modeling/config.json`：canonical 复现实例配置；
- `src/tests/core/test_external_cli_handler.py`：EP 分发的定向测试。

长期约束：

- 新建变体时，先执行 `python cli.py ep create "ex_projects/compare/your_task"` 创建模板，再修改生成的 `config.json`；不要手动空建目录或直接手写配置文件。
- `wiener-parallel-modeling` 仍走 EP 主链：`create -> validate -> dispatch -> analyzer`，不要绕开 `cli.py ep` 直接调用内部脚本做正式产物。

## 基本用法

直接复现 canonical 任务：

```bash
python cli.py ep "ex_projects/compare/wiener_parallel_modeling"
```

如果要派生新变体，推荐流程为：

```bash
python cli.py ep create "ex_projects/compare/your_wiener_task"
python cli.py ep "ex_projects/compare/your_wiener_task"
```

然后在生成的 `config.json` 中复用同类 compare 配置的字段组织方式，只改当前试验真正需要变化的参数。

## 关键配置

`ex_projects/compare/wiener_parallel_modeling/config.json` 当前最关键的字段包括：

- `task_info.analysis_type = "wiener-parallel-modeling"`：决定 EP 分发到并联 Wiener analyzer；
- `inputs.preprocessed_source`：预处理后的输入频响数据；
- `inputs.measured_targets_source`：实测提取目标；
- `inputs.rebuild_preprocessed`：若使用任务目录下已复制好的 reference JSON，保持为 `false`；只有明确提供 `raw_data_dir` 时才改为 `true`；
- `amplitudes`：当前 canonical 任务使用 25 个幅值点，范围为 `0.24 - 6.0 m/s^2`；
- `branch_indices` 与 `fh_branch_names`：指定代表性支路及其命名；
- `fgm0d12`、`fgm3d0`、`fgm6d0`：分别控制低、中、高幅值支路的 `c`、`w`、`x_btn/x_top` 与 `top_k`；
- `analysis_target_freq = 100.0`：定义灵敏度提取频点。

长期上，这类配置应优先保持“幅值点、支路角色、目标频点和 reference 数据路径”四部分语义稳定；不要把一次性调参过程写成结构性配置字段。

## 输出产物

执行完成后，典型产物包括：

- `report.md`：本次任务的 Markdown 摘要报告；
- `data/wiener_parallel_modeling_summary.json`：机器可读摘要，包含幅值点数、中心频率/100 Hz 灵敏度范围与误差统计；
- `image/14.NN_extern_simu_reproduced_simulation.png`：多幅值频响重建图；
- `image/14.NN_extern_simu_reproduced_analysis.png`：中心频率与 100 Hz 灵敏度对比图；
- `image/14.NN_extern_simu_reproduced_fh_kx.png`：支路分段斜率函数图；
- `image/14.NN_extern_simu_reproduced_fh.png`：积分后的静态映射图；
- `image/wave_amp*.png`：每个幅值点的波形对比图。

## 结果判定

建议按以下顺序验收：

1. `report.md` 与 `data/wiener_parallel_modeling_summary.json` 必须同时生成；
2. `summary.json.amplitude_count` 应与配置中的幅值点数一致，且对应 `wave_amp*.png` 应完整生成；
3. 中心频率与 100 Hz 灵敏度的 simulated/target 曲线应整体保持同向迁移趋势，而不是只看单个幅值点是否贴合；
4. 最终以 `summary.json` 中的 `MAE`、`RMSE`、`range` 字段和主图叠加效果共同验收，不要仅凭日志或局部截图判断。

对于当前 canonical reference 数据，更重要的验收目标是“正确重建幅值增大时的峰频右移与通带灵敏度抬升趋势”，而不是追求逐点完全重合。

## 与 Wiener-KAN 的关系

并联 Wiener 等效模型是 Wiener-KAN 的上游解释层，不是最终训练模型本身。

长期写作口径应保持：

- 并联 Wiener 负责说明“大信号多物理场耦合非线性可以被局部线性动态 + 幅值相关静态非线性近似”；
- Wiener-KAN 负责把这种先验进一步参数共享、可训练化，并纳入统一训练/评估/部署链；
- 不应把两者写成完全等价，也不应把 Wiener/IIR 前端描述成毫无物理来源的纯工程 trick。

## 相关文档

- [EP 子命令说明](ep.md)
- [论文方法中间稿撰写规范](paper_method_draft_writing.md)
- [论文消融实验方法](paper_ablation_method.md)
