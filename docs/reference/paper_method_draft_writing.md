# 论文方法中间稿撰写规范

## 写作定位

本文档用于沉淀当前项目在撰写论文方法类中间稿时的长期稳定规范。它服务于 `docs/reference/` 下的论文方法文档编写，目标是让中间稿既能作为项目长期参考文档保留，又能较少改写地转入论文 `Methods`、实验设计说明或正式技术文档。

本文档只规定写法、内容要求、取值口径与边界，不记录某一轮实验结果，不承载一次性任务汇报。

## 适用范围

本规范适用于当前项目中以下类型的文档：

- 论文消融实验方法类中间稿
- 论文横向对比方法类中间稿
- 论文边缘设备推理评估方法类中间稿
- 论文指标计算方法类中间稿
- 其他需要直接支撑论文 `Methods` 的实验设计与指标定义文档

若一次需要多个专题中间稿，应按专题拆成多篇 `docs/reference/*.md` 独立文档，每篇各自完整闭环，不要把多个实验主题混成一篇总说明。

## 撰写方法

### 先落到当前项目事实

中间稿必须先对齐当前项目中的稳定事实来源，再开始写作。优先核对：

- 对应 experiment preset
- 对应 `projects/.../config.json`
- 对应 `python cli.py` 命令入口
- 对应 `src/core/`、`src/analysis/` 中的实现代码
- 对应正式取值文件，如 `metrics.json`、`compute_analysis.json`、`linear_response.json`

换言之，中间稿不是凭记忆概括，也不是按理想实验模板套写，而是先从当前项目的真实实现反推可写成论文方法的稳定表述。

### 先写方法，再写结果

中间稿优先回答以下问题：

1. 为什么做这组实验
2. 这组实验如何分组、如何控制变量
3. 训练、评估、汇总是如何执行的
4. 正式表格最终从哪里取值
5. 哪些公式和指标是按当前代码实现定义的
6. 哪些边界不能夸大

不要先堆结论、先写结果优劣或先贴项目名单，然后再倒推方法描述。

### 优先写成可转正的章节骨架

实验方法类中间稿优先采用以下结构：

1. `写作定位`
2. `实验目的`
3. `实验设计`
4. `实验流程`
5. `必要公式与实现口径`
6. `正式表格字段建议`
7. `写作边界`
8. `相关文档`

如果主题不是实验方法而是总规范，可把 `实验目的` 改为 `适用范围` 或 `目标`，但仍应保留“取值口径”“边界”和“相关文档”三个维度。

## 内容要求

### 实验目的

`实验目的` 必须回答该实验试图验证什么问题，不要只罗列模型名称、配置项或 project 路径。推荐写法是把问题拆成 2 到 4 个可验证的研究问题，例如：

- 验证方法有效性
- 验证精度与复杂度权衡
- 验证部署可行性
- 验证某个关键结构是否真正贡献性能

### 实验设计

`实验设计` 至少要写清：

- 正式分组由什么决定，例如 preset 或 project 集合
- 真实语义由什么决定，例如 `config.json`
- 共享控制变量有哪些
- 当前设计属于严格单因子对照，还是 canonical project comparison
- 哪些设计边界必须显式声明

如果当前实验并非严格等学习率、等损失、等超参设计，必须明确写出，不能在论文中偷换成更强的因果表述。

### 实验流程

`实验流程` 必须写成稳定执行链，而不是模糊口语描述。优先落到当前项目真实入口，例如：

- `python cli.py -t PROJECT_NAME`
- `python cli.py -e PROJECT_NAME`
- `python cli.py --metrics PROJECT_NAME`
- `python cli.py ep ...`

同时要写清代码侧的稳定链路，例如：

- `ProjectManager.prepare_dataset_and_model()`
- `ProjectManager.evaluate()`
- `ProjectManager.export_metrics_summary()`
- `metrics_summary.py`

目标是让读者可以从文档直接追溯到当前项目的实际实现。

### 必要公式与实现口径

`必要公式与实现口径` 是中间稿质量的硬约束，至少应满足：

- 公式对应当前代码实现，而不是教科书上更理想的版本
- 若实现口径与常见定义不同，必须显式说明
- 要说明变量、单位和最终字段的对应关系
- 要写清哪些量是主表字段，哪些量只是诊断量

例如在当前项目中，以下事项应优先按实现口径写清：

- `MAE` / `AFMAE` / 组合损失如何计算
- `Freq Drift (Hz)`、`Sens Drift (%)`、`Linearity (%)` 如何从频响与线性度产物提取
- `Compute Cost` 的单步、加权、非实测时延语义
- `QEMU-MAE`、`KEIL-MAE`、`KEIL-SPEED` 的来源与公式

### 正式表格字段建议

中间稿必须明确论文或正式文档最终读哪些字段，以及这些字段的单一事实来源文件。对当前项目，实验类正式表格默认优先读取：

- `projects/.../data/metrics.json`

必要时再补充说明上游来源，例如：

- `training_info.json`
- `linear_response.json`
- `linearity_by_frequency.json`
- `compute_analysis.json`
- 部署 EP 下的 `benchmark_summary.json`、`keil_benchmark_summary.json`

禁止在中间稿里留下“后续再看哪里取值”这类未闭环写法。

## 项目特定约束

当前项目的论文方法中间稿应特别遵守以下约束：

- 正式取值优先统一到 `metrics.json`，不要让论文主表直接混读日志、脚本输出与截图
- 涉及部署的章节，要区分静态复杂度、QEMU 一致性、Keil 一致性、Flash / RAM 与板端时序，不要混写为一个“速度”
- 涉及横向对比的章节，要明确当前是 canonical project comparison 还是严格单因子设计
- 涉及消融的章节，要避免把多因素同时变化的 project 写成干净单因子实验
- 涉及 FRIKAN / FRIMLP / FRIKAND 等结构语义时，要以当前 `prepare_systems()`、`build_model()` 和实际 project 配置为准

## 写作边界

中间稿必须主动写出边界，至少包括以下几类：

- 不能把临时结果、截图或训练曲线写成正式证据
- 不能把当前实现中不存在的统一总分、统一排序规则写成既成事实
- 不能把非严格控制变量实验夸大成严格正交实验
- 不能把 `Compute Cost` 写成端到端实测时延
- 不能把尚未接入部署链的模型写成正式部署对象
- 不能把一次性任务报告内容直接塞进长期参考文档

## 自检清单

在提交一篇论文方法类中间稿前，至少检查以下问题：

1. 是否明确回答了“实验为什么做”
2. 是否写清了“当前分组如何定义”
3. 是否写清了“训练、评估、汇总如何执行”
4. 是否给出了当前实现口径下的必要公式
5. 是否明确了正式字段和唯一取值来源
6. 是否主动写出了不能夸大的边界
7. 是否整篇文档不依赖一次性结果数字也能独立成立

## 相关文档

- [paper_ablation_method.md](paper_ablation_method.md)
- [paper_horizontal_comparison_method.md](paper_horizontal_comparison_method.md)
- [paper_edge_inference_evaluation_method.md](paper_edge_inference_evaluation_method.md)
- [paper_metric_calculation_method.md](paper_metric_calculation_method.md)
- [training.md](training.md)
- [evaluation.md](evaluation.md)
- [metrics.md](metrics.md)
- [compute_analysis.md](compute_analysis.md)
