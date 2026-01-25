## TIPS

测试使用环境 conda tf26
测试使用命令 conda.bat run --no-capture-output -n tf26 python cli.py ep ex_projects/...

可以参考的成功案例 `doc\principle\20251227_SVFNET_E96量化.md`

---

## 任务分类导览

### 核心目标
让 `wnet5-circuit-validation` 的 `task_type` 支持 SVF 层的误差仿真，对比：
- **baseline**: 理想 SVF + 理想 Dense
- **target**: 实测 SVF（含误差） + 理想 Dense

### 调研类任务（5个）

| 类别 | 任务ID | 说明 |
|-----|-------|------|
| SVF仿真基础调研 | R1 | 调查 SVF 层仿真代码实现 |
| 误差仿真设计 | R2 | 设计从实测数据加载误差的配置方案 |
| Dense支持调研 | R5 | 调查如何添加 Dense 层到误差仿真 |
| 数学原理调研 | R8 | 调查带误差/不带误差 SVF 的计算公式差异 |
| 元件参数调研 | R15 | 调查 $f_0$, $Q$ 转电路元件参数的计算公式 |

### 实现类任务（11个）

| 类别 | 任务ID | 说明 |
|-----|-------|------|
| 基础功能 | R3, R4 | 实现 SVF 误差仿真及路径修复 |
| Dense支持 | R6, R7 | 实现 Dense 层支持及结果修复 |
| 拟合改进 | R9, R10, R11 | 设计并实现拟合传递函数，改进拟合算法 |
| 多层支持 | R12 | 支持 Layer1-4 多层误差仿真 |
| 报告生成 | R13, R13.1 | 生成 Markdown 报告及图片验证 |
| 元件对比 | R13.2, R13.3 | 对比理论值、标称值、实测反推值 |

### 关键文件
- 主报告: `doc/todo/details/20251230_SVFNET_SVF层误差/20260125_2304_Task_Report.md`
- 核心代码: `visualization/wnet5_circuit_validator.py`

## 总任务

总的任务是让以 `ex_projects\inference\wnet5-circuit-validation\WNET5q1h2u6l3_layer1` 为例的 `wnet5-circuit-validation` 的 `task_type` 支持 SVF 层的误差仿真。

思路是对比以下两个仿真得到的频率响应曲线：

1. baseline: SVF 层（不考虑误差） + Dense 层（不考虑误差）
2. target: SVF 层（带误差，频响从 实际测量结果 `exam_data\20251230_SVFNET_SVF_ONLY\20251230_SVF_ONLY.xlsx` 中读取） + Dense 层（不考虑误差）

## R1 [completed]

调查 `ex_projects\wnet5-circuit-validation\layer1\config.json` 里面的 SVF 层是如何进行仿真的，代码在哪里？形成一个调查报告到 [R1](./details/20251230_SVFNET_SVF层误差/R1_SVF层仿真调查报告.md) 中。

## R2 [completed]

根据 R1 的调查结果，再深入分析，设计一个从实际测量结果中加载 SVF 层的 config.json 选项和代码实现方案，形成一个设计报告到 [R2](./details/20251230_SVFNET_SVF层误差/R2_SVF层误差仿真设计报告.md) 中。应当充分利用现有的基础设施，仅作最小修改，实现 SVF 层误差仿真功能。要复用 `ex_projects\inference\wnet5-circuit-validation\WNET5q1h2u6l3_layer1\data\plots\frequency_response_comparison_merged.png` 的绘图代码，生成一个新的数据结果和图片，用于对比 target 和 baseline 的频率响应曲线差异。

## R3 [completed]

根据 R1， R2 的报告，实现 SVF 层误差仿真功能，并形成一个实现报告到 [R3](./details/20251230_SVFNET_SVF层误差/R3_SVF层误差仿真实现报告.md) 中。实际运行后要实际查看图像结果，确认其正确性，如果有问题，进行调试，直到正确为止。

## R4 [completed]

`ex_projects\inference\wnet5-circuit-validation\SVF_ERROR_SIM\config.json` 中的路径，在 `met_nonlinear_master` 内部的，应该用相对路径表示，而不是绝对路径，避免换 PC 之后用不了。修改报告写到 [R4](./details/20251230_SVFNET_SVF层误差/R4_SVF层误差仿真相对路径修改报告.md) 中。

## R5 [completed]

现在仿真出的结果是 SVF（实际测试误差） vs SVF（无误差），这不是我一开始要的结果，但是也有用，继续保留。我再强调我要的是 SVF（实际测试误差） + Dense（无误差） vs SVF（无误差） + Dense（无误差），也就是必须要带 Dense 层的结果，你再调研，如何在当前的基础上再多仿真出来一个我真实要的结果。形成调查报告 + 实现方案到 [R5](./details/20251230_SVFNET_SVF层误差/R5_SVF层误差仿真含Dense调查与实现方案.md) 中。

## R6 [completed]

按照 R5 的方案，完成 SVF（实际测试误差） + Dense（无误差） vs SVF（无误差） + Dense（无误差）的仿真，并形成实现报告到 [R6](./details/20251230_SVFNET_SVF层误差/R6_SVF层误差仿真含Dense实现报告.md) 中。实际运行后要实际查看图像结果，确认其正确性，如果有问题，进行调试，直到正确为止。

## R7 [completed]

R6 运行出来的结果过于离谱，`ex_projects\inference\wnet5-circuit-validation\SVF_ERROR_SIM\data\plots\svf_dense_error_comparison.png` 中的虚线（理想SVF+DENSE）应当与`ex_projects\inference\wnet5-circuit-validation\WNET5q1h2u6l3_layer1\data\plots\frequency_response_e96_comparison.png`中的虚线（理想SVF）完全一致，但是并不一致，差异巨大。你应当实际读取两个图像和数据，分析原因，修复代码，直到两者一致为止。形成调查与修复报告到 [R7](./details/20251230_SVFNET_SVF层误差/R7_SVF层误差仿真含Dense结果修复报告.md) 中。

## R8 [completed]

分别调查带 误差的 SVF 层和不带误差的 SVF 层的计算过程的数学原理，重点分析两者的计算公式的差异，每一个公式都要追溯到特定的代码实现位置，形成调查报告到 [R8](./details/20251230_SVFNET_SVF层误差/R8_SVF层误差仿真数学原理调查报告.md) 中。

## R9 [completed]

R8 中报告的带误差的 SVF 层是通过实测增益+理论相位计算出来的，这个方法不合适，要替换成通过拟合得到实测传递函数，然后使用实测传递函数的参数 + 理论仿真的代码来计算带误差的 SVF 层，按照这个思路先使得 `ep ex_projects/inference/wnet5-circuit-validation/SVF_ERROR_SIM` 能够生成一个新的拟合结果对比图，即对比 SVF 层的实测带误差的原始图形和通过拟合传递函数计算出来的图形，确认两者一致，然后再生成 SVF+DENSE 的最终对比图。形成设计方案，方案要充分调研当前的代码实现，充分利用现有 基础设施，并删除掉 R8 的旧版的实测增益+理论相位的计算方法。设计方案写到 [R9](./details/20251230_SVFNET_SVF层误差/R9_SVF层误差仿真含Dense拟合传递函数设计方案.md) 中。

## R10 [completed]

按照 R9 的方案设计，然后实际运行，查看拟合对比图和最终 SVF+DENSE 对比图，确认其正确性，如果有问题，进行调试，直到正确为止。形成实现报告到 [R10](./details/20251230_SVFNET_SVF层误差/R10_SVF层误差仿真含Dense拟合传递函数实现报告.md) 中。

## R11 [completed]

拟合效果不好，应当只拟合频率响应的幅度，不拟合相位，同时设置好初始值，初始值使用理论计算值。修改报告写到 [R11](./details/20251230_SVFNET_SVF层误差/R11_SVF层误差仿真含Dense拟合传递函数改进报告.md) 中。修改后实际运行，查看拟合结果对比图，确认其正确性，如果有问题，进行调试，直到正确为止。

## R12 [completed]

让 ex_projects\inference\wnet5-circuit-validation\WNET5q1h2u6l3_layer1
ex_projects\inference\wnet5-circuit-validation\WNET5q1h2u6l3_layer2
ex_projects\inference\wnet5-circuit-validation\WNET5q1h2u6l3_layer3
ex_projects\inference\wnet5-circuit-validation\WNET5q1h2u6l3_layer4 也配置为带 SVF+Dense，带 SVF_only 误差仿真的功能，要确保其原有的功能不受影响，调整 config.json 后实际运行。形成实现报告到 [R12](./details/20251230_SVFNET_SVF层误差/R12_SVF层误差仿真含Dense多层支持实现报告.md) 中。

## R13 [completed]

**Report 生成**
支持让 `wnet5-circuit-validation` 的 `task_type` 支持生成结果报告md，md中要引用生成的所有图片，对每个图片进行简要说明，报告中不应当包含图片里面的具体数据，只要说明每个图片的设计目的，横轴纵轴，每个数据曲线的含义和来源等。报告生成到 `ex_projects\inference\wnet5-circuit-validation\SVF_ERROR_SIM\data\reports\report.md` 中，只生成一个总报告，不要为每个图单独生成报告。形成设计与实现报告到 [R13](./details/20251230_SVFNET_SVF层误差/R13_SVF层误差仿真含Dense结果报告生成设计与实现报告.md) 中。 确保代码实际运行后，报告正确生成，内容正确。

### R13.1 [completed]

用 `ex_projects\inference\wnet5-circuit-validation\WNET5q1h2u6l3_layer1`
继续完善 R13 的功能，插入图片必须用 []() 的 markdown 格式插入，相对路径，且必须在生成后加入验证代码，确保 data/plots 里面的所有 png 图片都被正确插入到 data/reports/report.md 中，没有遗漏的图片，且路径正确，形成实现报告到 [R13.1](./details/20251230_SVFNET_SVF层误差/R13.1_SVF层误差仿真含Dense结果报告图片插入验证实现报告.md) 中。确保代码实际运行后，报告正确生成，内容正确。

### R13.2 [completed]

调查代码中是否存在根据 SVF 电路的 f0 和 Q 值计算电路的元件参数的代码，调查计算公式，将调查结果写到 [R13.2](./details/20251230_SVFNET_SVF层误差/R13.2_SVF电路元件参数计算调查报告.md) 中。

### R13.3 [completed]

SVF 实际制作的电路中，两个 SVF 电路的电容标称值分别是 1.5uF 和 200nF，现在需要对比三个值：

1. 理论计算值（R13.2 中调查得到的计算公式计算出来的值）
2. 标称值（1.5uF 和 200nF）
3. 实测值，从实测 SVF 频率响应的拟合结果中反推出来的电容值（电阻都视为标称值）

这个计算过程要集成到 `ex_projects\inference\wnet5-circuit-validation\WNET5q1h2u6l3_layer1` 中，形成设计与实现报告到 [R13.3](./details/20251230_SVFNET_SVF层误差/R13.3_SVF电路元件参数对比计算设计与实现报告.md) 中。确保代码实际运行后，能够生成一个对比表格，表格中包含上述三种值的对比。这个表格补充输出到 R13 提到的 `report.md` 中。

## R14 [completed]

**整理**
将之前的这些任务做一个分类导览，写到 TIPS 部分，简要说明做了几个主要任务，这些主要任务涉及到的任务ID 是哪些, 完成任务后将详细报告写入[R17](./details/20251230_SVFNET_SVF层误差/20260125_2304_Task_Report.md)。

### R14.1 [completed]

把R14到R16重命名为### R13.1，### R13.2,### R13.3, 注意相关的文档链接和文档命名也要同步修改，后续的任务命名要顺延修改完成任务后将详细报告写入[R17.1](./details/20251230_SVFNET_SVF层误差/20260125_2309_Task_Report.md)。

### R14.2 [in_progress]

把总任务重命名为 R1，然后将 R2到R12重命名为R1.x，文档链接、文档命名也要同步修改，后续任务顺眼，例如R13顺延为R2，R14顺延为R3, 完成任务后将详细报告写入[R14.2](./details/20251230_SVFNET_SVF层误差/20260125_2314_Task_Report.md)。
