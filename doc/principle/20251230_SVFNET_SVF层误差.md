## TIPS

测试使用环境 /c/Users/liang/.conda/envs/tf26/python.exe
测试使用命令 python cli.py ep ex_projects/...

可以参考的成功案例 `doc\principle\20251227_SVFNET_E96量化.md`

## 总任务

总的任务是让以 `ex_projects\inference\wnet5-circuit-validation\WNET5q1h2u6l3_layer1` 为例的 `wnet5-circuit-validation` 的 `task_type` 支持 SVF 层的误差仿真。

思路是对比以下两个仿真得到的频率响应曲线：

1. baseline: SVF 层（不考虑误差） + Dense 层（不考虑误差）
2. target: SVF 层（带误差，频响从 实际测量结果 `exam_data\20251230_SVFNET_SVF_ONLY\20251230_SVF_ONLY.xlsx` 中读取） + Dense 层（不考虑误差）

## R1

调查 `ex_projects\wnet5-circuit-validation\layer1\config.json` 里面的 SVF 层是如何进行仿真的，代码在哪里？形成一个调查报告到 [R1](../../doc/detail/20251230_SVFNET_SVF层误差/R1_SVF层仿真调查报告.md) 中。

## R2

根据 R1 的调查结果，再深入分析，设计一个从实际测量结果中加载 SVF 层的 config.json 选项和代码实现方案，形成一个设计报告到 [R2](../../doc/detail/20251230_SVFNET_SVF层误差/R2_SVF层误差仿真设计报告.md) 中。应当充分利用现有的基础设施，仅作最小修改，实现 SVF 层误差仿真功能。要复用 `ex_projects\inference\wnet5-circuit-validation\WNET5q1h2u6l3_layer1\data\plots\frequency_response_comparison_merged.png` 的绘图代码，生成一个新的数据结果和图片，用于对比 target 和 baseline 的频率响应曲线差异。

## R3

根据 R1， R2 的报告，实现 SVF 层误差仿真功能，并形成一个实现报告到 [R3](../../doc/detail/20251230_SVFNET_SVF层误差/R3_SVF层误差仿真实现报告.md) 中。实际运行后要实际查看图像结果，确认其正确性，如果有问题，进行调试，直到正确为止。

## R4

`ex_projects\inference\wnet5-circuit-validation\SVF_ERROR_SIM\config.json` 中的路径，在 `met_nonlinear_master` 内部的，应该用相对路径表示，而不是绝对路径，避免换 PC 之后用不了。修改报告写到 [R4](../../doc/detail/20251230_SVFNET_SVF层误差/R4_SVF层误差仿真相对路径修改报告.md) 中。

## R5

现在仿真出的结果是 SVF（实际测试误差） vs SVF（无误差），这不是我一开始要的结果，但是也有用，继续保留。我再强调我要的是 SVF（实际测试误差） + Dense（无误差） vs SVF（无误差） + Dense（无误差），也就是必须要带 Dense 层的结果，你再调研，如何在当前的基础上再多仿真出来一个我真实要的结果。形成调查报告 + 实现方案到 [R5](../../doc/detail/20251230_SVFNET_SVF层误差/R5_SVF层误差仿真含Dense调查与实现方案.md) 中。
