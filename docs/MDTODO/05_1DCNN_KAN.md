## 总任务

- 开发一个新的模型，基于 1DCNN + KAN，来进行 MET 非线性补偿任务
- 参考 FRIKAN，将 FRI 的 RNN 部分替换为 1DCNN，形成 1DCNN_KAN 模型
- 用 `FRIKANh8u6l6` 作为参考，其中 h8 指的是有 1 输入 8 个通道输出的 1DCNN
- 在 `projects` 下创建 `1DCNN_KANh8u6l6` 的 `project`，支持 cli.py 做训练和评估

## R1 [done] [completed]

按照总任务做调研，形成一个实现方案, 完成任务后将详细报告写入[R1](./details/05_1DCNN_KAN/20260329_0928_Task_Report.md)。

### R1.1 [completed] 

按照方案2做详细计划，包括修改的文件列表，详细计划每个代码修改点, 完成任务后将详细报告写入[R1.1](./details/05_1DCNN_KAN/20260329_0941_Task_Report.md)。

### R1.1.1 [completed] 

参考 LSTM 的写法，1DCNN_KAN 不需要传入 system, 完成任务后将详细报告写入[R1.1.1](./details/05_1DCNN_KAN/20260329_0950_Task_Report.md)。

### R1.1.2 [done] [completed]

综合R1.1,R1.1.1 编写新的实施细则计划文件，详细计划每个代码修改点, 完成任务后将详细报告写入[R1.1.2](./details/05_1DCNN_KAN/20260329_0955_Task_Report.md)。

## R2 [completed]

按照R1的任务迭代开发和测试，确保完全可用, 完成任务后将详细报告写入[R2](./details/05_1DCNN_KAN/20260329_1008_Task_Report.md)。

### R2.1 [completed]

创建项目目录结构 projects/CNNKANh8u6l6/data/，完成任务后将详细报告写入[任务报告](./details/05_1DCNN_KAN/R2.1_Task_Report.md)。
#### R2.1.1 [done] [completed]

执行创建项目目录结构任务，完成任务后将详细报告写入[任务报告](./details/05_1DCNN_KAN/R2.1.1_Task_Report.md)。
#### R2.1.2 [completed]

审查 R2.1.1 的执行结果，完成任务后将详细报告写入[任务报告](./details/05_1DCNN_KAN/R2.1.2_Task_Report.md)。
### R2.2 [completed]

在 frikan_models.py 末尾添加 CNNKAN 类，完成任务后将详细报告写入[任务报告](./details/05_1DCNN_KAN/R2.2_Task_Report.md)。
#### R2.2.1 [done] [completed]

执行在 frikan_models.py 添加 CNNKAN 类任务，完成任务后将详细报告写入[任务报告](./details/05_1DCNN_KAN/R2.2.1_Task_Report.md)。
#### R2.2.2 [completed]

审查 R2.2.1 的执行结果，完成任务后将详细报告写入[任务报告](./details/05_1DCNN_KAN/R2.2.2_Task_Report.md)。
#### R2.2.3 [done] [completed]

修复 CNNKAN 类的 inner_kan_units 和 inner_kan_layers 默认值，完成任务后将详细报告写入[任务报告](./details/05_1DCNN_KAN/R2.2.3_Task_Report.md)。
#### R2.2.4 [completed]

审查 R2.2.3 的修复结果，完成任务后将详细报告写入[任务报告](./details/05_1DCNN_KAN/R2.2.4_Task_Report.md)。
### R2.3 [completed]

修改 __init__.py 导出 CNNKAN，完成任务后将详细报告写入[任务报告](./details/05_1DCNN_KAN/R2.3_Task_Report.md)。
#### R2.3.1 [done] [completed]

执行修改 __init__.py 导出 CNNKAN 任务，完成任务后将详细报告写入[任务报告](./details/05_1DCNN_KAN/R2.3.1_Task_Report.md)。
#### R2.3.2 [done] [completed]

审查 R2.3.1 的执行结果，完成任务后将详细报告写入[任务报告](./details/05_1DCNN_KAN/R2.3.2_Task_Report.md)。
### R2.4 [completed]

修改 model_engine.py 添加 CNNKAN 分支，完成任务后将详细报告写入[任务报告](./details/05_1DCNN_KAN/R2.4_Task_Report.md)。
#### R2.4.1 [completed]

执行修改 model_engine.py 添加 CNNKAN 分支任务，完成任务后将详细报告写入[任务报告](./details/05_1DCNN_KAN/R2.4.1_Task_Report.md)。
#### R2.4.2 [done] [completed]

审查 R2.4.1 的执行结果，完成任务后将详细报告写入[任务报告](./details/05_1DCNN_KAN/R2.4.2_Task_Report.md)。
### R2.5 [completed]

创建 config.json 配置文件，完成任务后将详细报告写入[任务报告](./details/05_1DCNN_KAN/R2.5_Task_Report.md)。
#### R2.5.1 [done] [completed]

执行创建 config.json 配置文件任务，完成任务后将详细报告写入[任务报告](./details/05_1DCNN_KAN/R2.5.1_Task_Report.md)。
#### R2.5.2 [done] [completed]

审查 R2.5.1 的执行结果，完成任务后将详细报告写入[任务报告](./details/05_1DCNN_KAN/R2.5.2_Task_Report.md)。
### R2.6 [completed]

验证 CLI 训练功能，完成任务后将详细报告写入[任务报告](./details/05_1DCNN_KAN/R2.6_Task_Report.md)。
#### R2.6.1 [completed]

执行验证 CLI 训练功能任务，完成任务后将详细报告写入[任务报告](./details/05_1DCNN_KAN/R2.6.1_Task_Report.md)。
#### R2.6.2 [completed]

审查 R2.6.1 的执行结果，完成任务后将详细报告写入[任务报告](./details/05_1DCNN_KAN/R2.6.2_Task_Report.md)。
### R2.7 [completed]

验证 CLI 评估功能，完成任务后将详细报告写入[任务报告](./details/05_1DCNN_KAN/R2.7_Task_Report.md)。
#### R2.7.1 [completed]

执行验证 CLI 评估功能任务，完成任务后将详细报告写入[任务报告](./details/05_1DCNN_KAN/R2.7.1_Task_Report.md)。
#### R2.7.2 [completed]

审查 R2.7.1 的执行结果，完成任务后将详细报告写入[任务报告](./details/05_1DCNN_KAN/R2.7.2_Task_Report.md)。
## R3

配置相关

### R3.1 [completed]

需要在`config.json`增加配置项，来调整 1DCNN 的卷积的时间步数，完成任务后将详细报告写入[R3.1](./details/05_1DCNN_KAN/20260329_1433_Task_Report.md)。

### R3.1.1

CNN_KERNEL_SIZE 已经实现

### R3.2 [completed]

调查 CNNKAN 里面的 use_fast_model 是否真正生效，开启与不开启有什么区别？CNN 按理说不存在 fast_model, 完成任务后将详细报告写入[R3.2](./details/05_1DCNN_KAN/20260329_1446_Task_Report.md)。

### R3.2.1 [completed] [done]

完全移除 use_fast_model 相关代码以避免混淆, 完成任务后将详细报告写入[R3.2.1](./details/05_1DCNN_KAN/20260329_1453_Task_Report.md)。
