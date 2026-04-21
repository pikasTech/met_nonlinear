
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