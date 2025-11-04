## C01

参考基础设施文档，考虑如何增强可视化功能，支持绘制多震级的频率响应的补偿前后对比的时候，可以支持左右图布局，左边是补偿前，右边是补偿后，左右图的y坐标范围一致，x坐标范围一致，图的大小一致，这样可以进行有效的对比，目前已经有了把补偿前后的图绘制到同一张图上的可视化功能，深入调研这个已有的功能，如何通过最小修改，不破坏原有功能的情况下，支持新的绘图选项，绘图功能要集成到cli.py 里面，深入调查已有文档，写一个实施方案文档，给出2~3种实施方案（如果凑不到也没关系，只保留可靠的方案），方案放到 doc/plan/里面

## C02

深入调查当前系统的inference的机制，是如何做到将神经网络模型（WNET5为例）转换为电路模型，对电路模型进行仿真，进行误差分析等操作的，如何用 cli.py 调用这些操作，核心的机制是什么样的，基础设施是什么样的，充分调研以确保后续继续开发的时候可以以当前的基础设施的架构设计作为参考基础，充分利用好已有的基础设施，将调研结果写到 doc/infra/inference.md里面

## C03

目前已经将 WNET5 的电路做出来了，然后我现在需要对电路进行测试，为了测试电路的设计是否符合预期，我设计了频率响应测试法，即在 SVF 层之前输入扫频信号，然后测量 SVF 层 + Dense 层（第一层）的 RELU 前的波形输出，对 RELU 前的波形 vs 输入波形进行频率响应分析，我目前已经测量了实际电路板的频率响应，我需要再通过仿真来计算出 WNET5 理论上的频率响应，来进行对比，所以现在的任务是：**通过仿真来计算出 WNET5 SVF 层 + Dense 层（第一层）的 RELU 前的波形输出 理论上的频率响应**，根据这个需求和基础设施的文档，做一个计划文档，放到doc/plan里面，并更新doc/summary.md

## C03.1

按照一个简化的传递函数仿真思路来仿真，因为到RELU之前都是线性系统，所以可以直接提取WNET5的SVF层的每个SVF通道的传递函数，然后通过DENSE层的加权权重，来对SVF的传递函数的每个通道做传递函数上的加权计算，得到DENSE的每个输出的权重函数，全程采用频率域分析法，不使用时域波形分析法 <--按照这个思路重新调研和修改计划md，更新summary.md

## C03.2

"transfer-function-analysis" 这个任务类型太宽泛，应该根据具体的任务要求再选一个不容易重复的，具体的任务名。2. 文档里面缺少原始需求说明，应该补充
应该大幅简化config的模板，应该只保留最小信息，我觉得就保留一个对应的 model_project_name 和频率范围就可以了，其他的都删除掉。

## C03.3

严格按照计划执行，然后用 WNET5q1h2u6l3 这个模型来测试，独立的 ep 工程创建到 ep_projects\inference\wnet5-circuit-validation\WNET5q1h2u6l3 里面，用 cli.py ep 测试这个 ep 工程确保能用。

## C03.4

每次执行结果都不一样，说明根本没有真正读取权重，完全没有按照计划里面的执行，在搞欺骗，在搞弄虚作假 (tf26) C:\work\met_nonlinear>python cli.py ep ep_projects\inference\wnet5-circuit-validation\WNET5q1h2u6l3
正在配置 logging_setup...
logging_setup 从配置文件加载: C:\work\met_nonlinear\logger\logging_config.yaml
log 文件路径: logs/metnl.log

日志文件已创建：
file: logs/20250917_100040_cli.log
error_file: logs/20250917_100040_cli_errors.log

[INFO 0.12s] cli.py start... | cli.py:50
[INFO 0.15s] 加载配置文件: core/cli_defaults.yaml | cli_parser.py:144
[INFO 0.17s] 🎯 开始处理外部项目: ep_projects\inference\wnet5-circuit-validation\WNET5q1h2u6l3 | external_cli_handler.py:35
[INFO 0.17s] 📂 项目信息: | external_cli_handler.py:41
[INFO 0.17s] 项目名称: inference | external_cli_handler.py:42
[INFO 0.17s] 任务类型: wnet5-circuit-validation | external_cli_handler.py:43
[INFO 0.17s] 任务名称: WNET5q1h2u6l3 | external_cli_handler.py:44
[INFO 0.17s] 配置文件: C:\work\met_nonlinear\ep_projects\inference\wnet5-circuit-validation\WNET5q1h2u6l3\config.json | external_cli_handler.py:45
[INFO 0.17s] 输出目录: C:\work\met_nonlinear\ep_projects\inference\wnet5-circuit-validation\WNET5q1h2u6l3\data | external_cli_handler.py:46
[INFO 0.17s] 📊 开始处理外部项目任务: WNET5q1h2u6l3 | external_cli_handler.py:68
[INFO 0.18s] 🚀 执行外部项目任务... | external_cli_handler.py:80
[INFO 0.18s] ✅ 配置验证通过: wnet5-circuit-validation | config_validator.py:354
[INFO 0.18s] ✅ 配置验证通过: wnet5-circuit-validation | external_cli_handler.py:287
[INFO 0.88s] 执行WNET5电路验证任务: WNET5q1h2u6l3 | external_cli_handler.py:442
[INFO 0.88s] 开始WNET5电路验证分析... | wnet5_circuit_validator.py:40
[INFO 0.88s] 加载模型: projects/WNET5q1h2u6l3/data/best.weights.h5 | wnet5_circuit_validator.py:74
[INFO 0.88s] 计算SVF传递函数... | wnet5_circuit_validator.py:105
[INFO 1.63s] 计算组合传递函数... | wnet5_circuit_validator.py:130
[INFO 1.64s] 计算频率响应... | wnet5_circuit_validator.py:150
[INFO 1.66s] 生成可视化图表... | wnet5_circuit_validator.py:187
[INFO 3.16s] 图表已保存: C:\work\met_nonlinear\ep_projects\inference\wnet5-circuit-validation\WNET5q1h2u6l3\data\plots\frequency_response.png | wnet5_circuit_validator.py:217
[INFO 3.16s] 生成分析报告... | wnet5_circuit_validator.py:222
[INFO 3.16s] 分析报告已保存: C:\work\met_nonlinear\ep_projects\inference\wnet5-circuit-validation\WNET5q1h2u6l3\data\reports\analysis_report.json | wnet5_circuit_validator.py:251
[INFO 3.16s] 保存计算结果... | wnet5_circuit_validator.py:256
[INFO 3.17s] 频率响应数据已保存: C:\work\met_nonlinear\ep_projects\inference\wnet5-circuit-validation\WNET5q1h2u6l3\data\numerics\frequency_response.json | wnet5_circuit_validator.py:269
[INFO 3.17s] ✅ WNET5电路验证分析完成 | wnet5_circuit_validator.py:63
[INFO 3.17s] ✅ WNET5电路验证任务完成: C:\work\met_nonlinear\ep_projects\inference\wnet5-circuit-validation\WNET5q1h2u6l3\data | external_cli_handler.py:448
[INFO 3.17s] ✅ 任务执行完成 | external_cli_handler.py:84
[INFO 3.17s] 输出目录: C:\work\met_nonlinear\ep_projects\inference\wnet5-circuit-validation\WNET5q1h2u6l3\data | external_cli_handler.py:85


## C04

现在要在 `wnet5-circuit-validation` 的基础上进行拓展，目前已经实现了： `SVF层 + Dense 层（第一层）的 RELU 前的频率响应分析`。

现在的需求是：

1. 支持 SVF 层 + Dense 层（第二层/第三层/第四层）的 RELU 前的频率响应分析。

这个分析的目的是对实际电路板的每一层输出进行频率响应对比分析。因此应该将第二层/第三层/第四层 的模型权重替换到原来的 SVF 层的后面，然后进行同样的频率响应分析。

要求能够通过 `config.json` 来配置需要分析的层数（第二层/第三层/第四层）。例如：

```json
"analysis_layer": 2
```

要注意，Dense 层任何时候有且只有一个被分析，**不要同时分析多个Dense层**。
**永远是 1 个 SVF层 + 1个 Dense层** 的组合进行分析。

请基于现有的 `wnet5-circuit-validation` 功能，设计一个实施方案，放到 `doc/plan/20251104` 目录下，方案中要包含：

- 需要修改或新增的代码文件和函数。
- 需要修改或新增的配置项。
- 预期的输出结果和文件结构。
- 要修改的每个代码文件的每处修改点的简要说明。
- 之前是如何加载和使用 Dense 层的权重，现在要如何修改来加载和使用指定层数的 Dense 层的权重。

