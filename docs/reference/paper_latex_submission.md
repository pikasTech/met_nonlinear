# 论文 LaTeX 与 MN 投稿稿约定

## 适用范围

本文档用于维护仓库内论文 LaTeX 稿件的长期稳定约定，尤其适用于 `Microsystems & Nanoengineering`（MN）方向的本地整理、翻译和编译验证。

当前 canonical 稿件目录为：

- `docs/paper/latex/`

涉及本地编译 skill 时，只记录本项目与该 skill 的连接关系、入口、前置条件和判定标准；通用 CLI 用法直接参考：

- `C:/Users/lyon/.agents/skills/latex/SKILL.md`

## 稿件目录与权威文件

MN 本地稿件相关文件以 `docs/paper/latex/` 作为唯一权威目录，关键文件包括：

- `docs/paper/latex/main.tex`：主稿件入口。
- `docs/paper/latex/values.md`：稿件级数值宏定义文件，供 `main.tex` 统一引用。
- `docs/paper/latex/sn-jnl.cls`：Springer Nature 期刊模板类文件。
- `docs/paper/latex/bst/sn-nature.bst`：模板对应的参考文献样式文件。
- `docs/paper/latex/build/main.pdf`：本地编译产物。

如果需要保留旧模板下的非当前主稿内容，应单独存放，不要重新并入 `main.tex` 主体流程。

## MN ???????????

MN ??????? Springer Nature `sn-jnl` ????????????? LaTeX ?????? PDF ?????????????MN ???????????????????????????????????????????????Springer Nature LaTeX authoring template ??????????????? `sn-article.tex` ? **single column layout**????????????????????? `iicol` ????? double column?MN ????????????????????????????

???????

- ?????/?????`\documentclass[sn-nature]{sn-jnl}`??? `xelatex` ???
- ?????/????????`\documentclass[lineno,sn-nature]{sn-jnl}`?
- ???????????? double-line spacing????? `referee`?? `\documentclass[referee,lineno,sn-nature]{sn-jnl}`?
- ?????? PDF ??????? `iicol`?`iicol` ??????????? LaTeX ??????
- ?????? `geometry` ????????????? Springer Nature ?????????????????????????????????????

???????

- MN ?? Nature Portfolio ?????? LaTeX ???? `sn-nature`??? `sn-nature.bst` ? numbered Nature Portfolio reference style?
- `sn-basic`?`sn-mathphys-num`?`sn-vancouver-num` ?? Springer Nature ?????????????????????????? MN ???????

?? class ?????

| ?? | ?? | MN ???? |
| --- | --- | --- |
| `sn-nature` | Nature Portfolio numbered reference style | ?? |
| `lineno` | ?????? | ????/?????? |
| `referee` | ??????? | ???????????? |
| `iicol` | ???? | ????????????? |
| `pdflatex` | ????? PDFLaTeX ?? | ??????????? XeLaTeX |
| `sn-basic` / `sn-mathphys-num` / `sn-vancouver-num` | ?? Springer Nature ?????? | ???? |

?????????????

- `main.tex` ?? `\documentclass[sn-nature]{sn-jnl}` ?????????
- ??????????? `sn-jnl.cls`?
- ??? `docs/paper/latex/build/main.pdf`?
- `latex` skill ? layout-check ????????? margin overflow?late float ??? overfull box?

???????????????????????

## 当前稿件叙事基调与命名边界

当前 `docs/paper/latex/main.tex` 的对外叙事应收敛到“经典 Wiener 分解 + KAN 非线性映射”的写法，而不是继续扩张新的命名体系。

对读者可见的稳定约定如下：

- 主模型名称统一使用 `Wiener-KAN`。
- 线性部分首提应写成“由震级条件局部传递函数初始化的 Wiener 线性层”，后文简写为“Wiener 线性层”。
- 非线性部分首提应写成“带符号与对称性约束的 KAN 非线性映射”，后文简写为“约束 KAN”。
- 默认强调沿用 Wiener 结构中“线性动态 + 静态非线性”的经典分解，不把线性前端包装成新的独立命名模块。
- `QLFRS`、`FRIRNN`、`FRI` 等历史缩写默认不再作为正文主叙事中的新概念使用；如确需出现，应仅作为实现来源、初始化路径或历史上下文说明，而不是新的卖点命名。
- 避免在对外可见文本中继续使用 `Prior-Informed`、`Physics-Constrained` 这类 novelty-heavy 标签，除非是在复述外部文献或做显式对比。
- 项目目录、配置和代码实现中的 `FRIKAN`、`FRIMLP`、`FRIKAND` 等名称仍然是有效模型名；它们在当前论文口径下应理解为 Wiener-KAN 路线下的实现名、变体名或别名，而不是已废弃名称。

允许保留但不应外溢到读者可见面的内容包括：

- 历史遗留的 LaTeX `label`
- 历史宏名，例如 `valFrikanVariant*`
- 旧图文件名、旧中间产物名或实现侧内部标识

判定“命名边界保持正确”的最小标准：

- 标题、摘要、正文、图题、表题中的主模型名统一为 `Wiener-KAN`
- 对读者可见文本中不再把 `FRI` / `QLFRS` 包装成新的主概念
- 读者看到的是“Wiener 线性层 + 约束 KAN”的结构叙事，而不是另一套新缩写体系
- 与此同时，仓库内部的 project 名、配置项和实现类名仍可继续保留 `FRIKAN` 系列命名，不应误判为“这些模型已无效”

## 当前稿件的标题与图表文字风格

在当前稿件中，英文 `section` / `subsection` 标题与图题、表题采用以下长期风格：

- `section` / `subsection` 标题使用简洁的 Title Case 名词短语，避免口号式或营销式措辞。
- figure / table caption 使用 sentence case，而不是整句 Title Case。
- caption 优先描述图表展示的对象和比较关系，避免堆叠过多背景论述。
- 对并列子图，优先使用 `(a) ... (b) ...` 的紧凑说明格式。
- 同一术语在标题、caption、正文中的写法保持一致，例如 `Wiener-KAN`、`Wiener 线性层`、`约束 KAN` 不应混写成多套近义命名。


## 中文定稿与英文翻译原则

论文正文在转投整理阶段默认先维护中文中间稿，等中文叙事、数据口径、图表顺序和审稿意见回应全部定稿后，再进入全文英文翻译与语言润色阶段。

长期约定如下：

- 未明确进入“英文终稿/投稿稿翻译”任务前，不因 MN 或 Springer Nature 目标期刊而提前把正文翻译成英文。
- 中文中间稿阶段优先解决结构、指标、实验设计、数据集说明、图表引用和 limitations 等内容问题。
- 英文标题、section/subsection 标题、caption、表头和参考文献样式可以按模板先保留英文；正文叙述层可以继续使用中文，直到用户明确要求全文翻译。
- 审阅任务中发现“中文正文”本身不作为缺陷处理；只有在进入最终英文投稿稿阶段，才把全文英文一致性作为验收项。
- 英文翻译不得改变已经定稿的技术口径、数据宏、图表顺序和边界声明；翻译阶段只做语言表达和期刊风格适配。

## 正文翻译边界

当英文稿件整理为中文稿时，默认只翻译正文叙述层内容；以下部分保持原语言，不随正文一起翻译：

- figure / table caption
- 作者简介
- `section` / `subsection` 标题
- 标题、作者、单位、投稿元数据

如需改变以上边界，应视为新的写作决策，而不是默认整理动作。

## 数值抽离约定

稿件中的 manuscript-level 数值应统一抽离到 `docs/paper/latex/values.md`，再由 `main.tex` 通过宏引用。

优先抽离的内容包括：

- 核心实验结论数值
- 扫频、扫幅、采样等实验设置
- 训练超参数
- 表格中的模型比较结果
- 嵌入式部署指标
- 正文或 caption 中直接参与论文结论表达的设备型号、平台名、变体名和对比频点

默认不抽离的内容包括：

- 数学推导中的结构常数，如 `1/2`、`2\pi`
- 矩阵维度、状态维度写法中的公式结构数字
- 下标、索引、序列位置编号
- 文献 citation key、邮箱、邮编等元数据数字

判定 `values.md` 已基本分离干净的标准：

- 稿件级实验数值和结论数值不再直接硬编码在正文和 caption 中。
- `main.tex` 中残留的数字主要属于公式结构、索引或元数据，而不是实验口径数字。

当变体名称会直接出现在表格、图题或正文中时，其显示名也应服从当前稿件叙事基调：

- 对外显示名优先使用 `Wiener-KANh...`
- 如需保留旧宏名或旧变量名，只能停留在实现层，不应重新暴露到读者可见文本中

## 本地编译与验证

本项目的 LaTeX 本地验证统一通过本地 `latex` skill 执行，不在仓库内另起一套独立编译规范。

推荐顺序：

1. `check`：确认 skill 自身可运行。
2. `debug probe`：确认目标稿件路径、引擎路径和输出目录都解析正确。
3. `build`：启动后台编译。
4. `status` / `logs`：确认编译结果并检查 warning。

在本项目中，中文稿默认优先使用：

- `xelatex`

标准工作目录与目标文件：

- `docs/paper/latex`
- `docs/paper/latex/main.tex`

## 可接受的本地编译兜底

为保证仓库当前状态下的本地可编译性，允许在主稿中保留以下兜底机制：

- 缺失图片时输出占位框，而不是直接让编译失败。
- 优先读取现有 `.bbl` 产物；若缺失，则回退到可通过编译的空 bibliography 框架。

这些机制的目标是保证本地结构整理、模板迁移和文字修改期间可以持续得到 PDF；如果后续进入正式投稿收尾阶段，应再单独检查是否需要切换到最终投稿态资源链路。

## MN AI+sensor 常用参考论文

以下论文为 MN 期刊在 AI+physical sensors / microsystems 方向的标杆论文，是当前稿件成稿风格的重要参考：

| 论文                             | 核心贡献                         | MN 成稿启示                                                                                     | 路径                                                                                                                                                     |
| ------------------------------ | ---------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Zhang et al. 2026 (Nano Lett.) | ML 驱动 MEMS 电热致动器无传感器线性化元结构设计 | **AI+sensor 论文的canonical范式**：physical sensor 为主角，AI 是实现线性化的计算工具；强调无传感器、无电路的机械结构方案而非 AI 模型创新 | `docs/research/literature/markdown/[MN]Machine_learning_driven_metastructure_design_for_sensor_free_linearization_of_MEMS_electrothermal_actuators.md` |

**成稿启示**：
- MN 的 AI+领域论文核心逻辑是"physical sensor / microsystem 问题 + AI 帮忙解决得更工程化、更高性能"
- 不要把 AI 模型写成主角，要让传感器/微系统站在舞台中央
- 贡献边界落在 sensor system performance enhancement，而不是通用 AI 模型创新

## 编译通过判定标准

对 `docs/paper/latex/main.tex` 的本地编译，满足以下条件即可判定“编译通过”：

- `latex` skill 的 `build` 最终 `status = done`
- `returncode = 0`
- 生成 `docs/paper/latex/build/main.pdf`

以下情况默认视为 warning，而不是编译失败：

- 在缺少完整 `.bib` 数据时出现 undefined citations
- 模板或字体层面的非致命 warning
- 占位图片导致的版面 warning

只有在无法生成 PDF、返回码非 0，或主稿入口、模板或资源路径解析失败时，才视为未通过。
