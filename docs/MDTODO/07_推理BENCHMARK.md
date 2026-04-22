
## R1 [completed]

当前已经对部分模型实现了 `qemu` 的推理，下一步要进一步支持 `keil proejct` 的自动构建和编译，实现真机在板的推理的 MAE 和性能测试。

要求：

- 生成工程的 `base project` 是 `src\tests\keil_projects\met_keil_405` 每个生成的工程放到对应的 ex_projects 的对应目录下
- 按照最小生成原则，先提取 `base`，然后生成最小的工程文件和代码文件，尽可能使用 `src\tests\keil_projects\met_keil_405` 已有的文件，对已有文件在工程文件里面做引用而不是复制
- 生成的纯粹 BENCHMARK 推理代码必须同时能够在 `qemu` 和 `keil project` 里编译和运行，且在 `qemu` 上的 MAE 和性能测试结果应该和 `keil project` 上的结果完全一致
- 生成的 `keil project` 要用 SKILL(keil) 来编译和下载测试，要用 SKILL(serial-monitor) 来获取串口输出的 MAE 和性能测试结果，完成验证

完成任务后将详细报告写入[R1](./details/07_推理BENCHMARK/20260420_214038_Task_Report.md)。

### R1.1 [completed]

1. 在 keil project 上，除了 cycle 之外，还要有精确到 ms 的基于定时器的实际耗时数据。这个相关代码修改在 `base` 里面修改。

2. 把几个 qemu 能跑的都用 `keil_project` 跑出来结果。

完成任务后将详细报告写入[R1.1](./details/07_推理BENCHMARK/20260420_223407_Task_Report.md)。

### R1.2 [completed]

补充完成：截至 2026-04-21，仓库内全部已发现 11 个 QEMU EP 均已完成 Keil 编译、真机验证与 MAE/耗时汇总，完成任务后将详细报告写入[任务报告](./details/07_推理BENCHMARK/R1.2_Task_Report.md)。
## R2 [completed]

src\core\lstm_qemu_ep_task.py 实在是太长了，你做一个重构计划，合理拆分，并再做一个回归测试计划，而且文件里面混杂了lstm、keil和除了lstm的多个模型，文件名和文件内容也不一致了，我觉得创建一个 src/core/board_inference/ 然后在里面去重构为多个文件会比较合适，src/core/board_inference/ 下放不同的神经网络模型的通用代码，src/core/board_inference/models/ 里面放每个模型的专门代码，另外 C 代码的模板我建议专门放到单独的文本文件，例如 xxx_template.c/.h 里面，不要都挤占了 py 里面。如果涉及到 xml 也可以放到 xxx_template.xml 里面。然后在 py 里面读取。qemu 和 keil 的部分也要分开，但是两者也可以共同引入公共的逻辑, 完成任务后将详细报告写入[R2](./details/07_推理BENCHMARK/20260421_124302_Task_Report.md)。

### R2.1 [in_progress]

在不修改 `src\core\lstm_qemu_ep_task.py` 的前提下按照 R2 的计划把新架构的代码写好，并且先不把新架构的代码挂载到 cli 主流程里面，增加一个 debug_cli，专门用来测试和旧的 `src\core\lstm_qemu_ep_task.py` 的 cli 主流程的行为一致性，最终要做到完全一致，这一步的目的是避免破坏已有的系统行为，先局部独立测试新重构后的代码，等到局部独立测试彻底通过后，后续可以清理 debug_cli 然后替换到主流程, 完成任务后将详细报告写入[R2.1](./details/07_推理BENCHMARK/20260421_125823_Task_Report.md)。

#### R2.1.1 [completed]

搭建 board_inference 新包骨架与 legacy adapter，不接入旧 CLI 主流程，完成任务后将详细报告写入[任务报告](./details/07_推理BENCHMARK/R2.1.1_Task_Report.md)。
#### R2.1.2 [completed]

增加 debug_cli 与产物比对逻辑，用于验证新旧流程行为一致性，完成任务后将详细报告写入[任务报告](./details/07_推理BENCHMARK/R2.1.2_Task_Report.md)。
#### R2.1.3 [completed]

补齐 board_inference 定向测试与 R2.1 执行报告，完成任务后将详细报告写入[任务报告](./details/07_推理BENCHMARK/R2.1.3_Task_Report.md)。
#### R2.1.4

定位 LSTM generate 路径的权重命名兼容问题，并让 debug_cli 在 `lstm_u16_base` 上完成新旧一致性比对，完成任务后将详细报告写入[任务报告](./details/07_推理BENCHMARK/R2.1.4_Task_Report.md)。
#### R2.1.5 [completed]

对齐 debug_cli 与旧 cli 包装行为，并用 frikan_h8u6l6_e1k_lr7e4 完成静态对照后的一致性验证，完成任务后将详细报告写入[任务报告](./details/07_推理BENCHMARK/R2.1.5_Task_Report.md)。
#### R2.1.6 [completed]

独立迁移 FRIKAN 核心逻辑到 board_inference，并完成 qemu build/run、keil-bench、性能数字与串口输出的一致性验证，完成任务后将详细报告写入[任务报告](./details/07_推理BENCHMARK/R2.1.6_Task_Report.md)。
#### R2.1.7 [completed]

按共享骨架迁移旧 qemu-c-inference 路径的全部模型与全部功能，FRIKAN 仅作为首个验证锚点而非专项特例，完成任务后将详细报告写入[任务报告](./details/07_推理BENCHMARK/R2.1.7_Task_Report.md)。
##### R2.1.7.1 [completed]

记录旧/新共享故障清单（LSTM 旧权重命名、FRIKAN keil 串口解析）并冻结为不修复项，完成任务后将详细报告写入[任务报告](./details/07_推理BENCHMARK/R2.1.7.1_Task_Report.md)。
##### R2.1.7.2 [completed]

静态梳理 horizontal reset preset 的 6 个模型覆盖状态，并完成新旧架构 qemu/keil 对照验证，完成任务后将详细报告写入[任务报告](./details/07_推理BENCHMARK/R2.1.7.2_Task_Report.md)。
### R2.2 [completed]

清理所有 legacy fallback，完成 horizontal preset 全模型 native 化，并验证 legacy vs native 在 qemu/keil benchmark 上一致（native 验证前临时移走旧模块），完成任务后将详细报告写入[任务报告](./details/07_推理BENCHMARK/R2.2_Task_Report.md)。

### R2.3 [completed]

将 `src\core\lstm_qemu_ep_task.py` 彻底删除，然后在新的架构的每个.py的头部注释中写入 `src\core\lstm_qemu_ep_task.py` 移除前的最后一个 `commit` id，这样以后如果需要参考阅读的时候还能临时切出来看，然后在移除后将新架构接入 `cli.py` 的主流程，并清理掉 `debug_cli` 和相关的临时脚手架，也清理掉迁移中使用的 `compare` 工具等，完成任务后将详细报告写入[R2.3](./details/07_推理BENCHMARK/20260421_191822_Task_Report.md)。

### R2.4 [completed]

frikan_h8u6l6_e1k_lr7e4 grnu16_e1k_puremae lstm_transformeru6_e1k_puremae lstm_u16_e1k_puremae_r8 onedcnn_c4u8k20l8_e1k_lr18e3_pd8l8_true tcnc4d1248k3_nopd_true_e1k_lr2e3 这些都要新架构下用 cli 正式路径跑完 qemu 和 keil bench，给我 QEMU MAE、KEIL MAE、KEIL TIME SPEND，存在问题就修复, 完成任务后将详细报告写入[R2.4](./details/07_推理BENCHMARK/20260421_195655_Task_Report.md)。

### R2.5 [completed]

继续按照 R2 的要求重构，尤其注意 template 的新架构要求，重构后要重新跑 R2.4 中提到的 QEMU 和 keil benchmark，要和 R2.4 的数据做对比，确保完全一致, 完成任务后将详细报告写入[R2.5](./details/07_推理BENCHMARK/20260421_204654_Task_Report.md)。

## R3 [completed]

支持参与横评preset 的 project 在 config.json 中挂载 board_inference 的 ex_project 相对路径，这样在对应 project 计算指标的时候，将 qemu/keil 的 board_inference 指标也记录进去，指标包括 QEMU-MAE，KEIL-MAE，KEIL-SPEED, 其中 KEIL-SPEED 的单位是 ms/point，每个 point 是一个 **时间步**，例如推理 1000 个点耗时 1s，则KEIL-SPEED 的指标为 1ms/point，修改代码后对横评 preset 中的 project 重新计算指标，确保计算结果包含以上要求的在板推理指标，完成任务后将详细报告写入[R3](./details/07_推理BENCHMARK/20260421_222259_Task_Report.md)。
