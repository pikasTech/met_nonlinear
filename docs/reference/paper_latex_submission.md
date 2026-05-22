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

## 自动化翻译工作流

本项目历史上存在一套面向论文中间稿的自动化翻译链，但它不在当前仓库内，而是依赖外部脚本目录 `D:/Work/agi_mpy/bin`。该链路只适用于仍保留 `\CNEN{中文}{英文}` 宏的中间稿，不适用于已经展开为普通英文正文的最终稿。

当前仓库的 canonical 英文主稿是 `docs/paper/latex/main.tex`。该文件默认视为已脱离 `\CNEN` 工作流的成稿入口；如果要重走自动翻译，应先确认操作对象仍是带 `\CNEN` 宏的中文中间稿副本，而不是直接对当前主稿做抽取。

### 外部入口与职责分工

- `D:/Work/agi_mpy/bin/textran.bat`：调用 `textran.py`，负责抽取 `\CNEN` 条目、生成模板、回填译文，以及在清空翻译时保留中文源文。
- `D:/Work/agi_mpy/bin/llmt.bat`：调用 `llmt.py`，负责把抽取出的条目送入 LLM 翻译流水线，并输出新的译文 JSON。
- `D:/Work/agi_mpy/terms.json`：术语表权威入口。自动翻译默认按该术语表约束大小写无关的术语映射。

职责边界如下：

- `textran` 只负责 `\CNEN` 宏的结构化抽取、增量检测和回填，不直接调用翻译服务。
- `llmt` 才是实际的自动翻译入口；其底层通过 OpenAI 兼容的 chat completions 接口访问 LLM。
- 具体模型名、接口地址和温度等运行参数以 `D:/Work/agi_mpy/config.py` 为准，不要在稿件文档里硬编码某个厂商名或一次性的模型版本。

### 路径与工作目录约束

- 两个 `.bat` 包装脚本只负责定位 Python 入口，不会自动切换当前工作目录。
- `textran.py` 默认把 `translate/`、`status.json`、`translations.json` 和 `template.tex` 写到当前工作目录。
- `llmt.py` 默认把 `translate/translations.json` 作为输入，把 `output/translations_output.json` 作为输出，并从当前工作目录解析 `terms.json`。
- 因此，只要不是在 `D:/Work/agi_mpy` 根目录直接运行，就应优先显式传入 `--terms`、`--translations`、`--output`、`-o`、`-t` 等路径，避免把翻译产物散落到错误目录。

推荐做法是：在目标稿件所在目录或专门的翻译工作目录中运行命令，并显式指定输入、模板、翻译 JSON 和输出 TeX 的路径。

### 推荐顺序

1. 先冻结中文中间稿的技术口径、数据宏、图表顺序和边界声明，再开始自动翻译；不要把自动翻译当成结构整理工具。
2. 对带 `\CNEN` 宏的源 TeX 执行 `textran export`，生成模板和待翻译 JSON。
3. 对导出的 JSON 执行 `llmt`，让 LLM 根据术语表和最近上下文生成英文条目。
4. 用 `textran fill` 把译文 JSON 回填为新的英文 TeX；如需重置英文槽位，才使用 `textran clear`。
5. 回填后的英文 TeX 进入本仓库的常规 LaTeX 校稿与编译链，不再继续依赖 `\CNEN` 作为最终投稿形态。

最小可复用命令顺序如下：

```bash
D:/Work/agi_mpy/bin/textran.bat export path/to/source_with_cnen.tex -o path/to/translate/translations.json -t path/to/translate/template.tex
D:/Work/agi_mpy/bin/llmt.bat --terms D:/Work/agi_mpy/terms.json --translations path/to/translate/translations.json --output path/to/output/translations_output.json
D:/Work/agi_mpy/bin/textran.bat fill -t path/to/translate/template.tex -j path/to/output/translations_output.json -o path/to/output/english.tex
```

### 稳定行为与判定口径

- `textran export` 会按 `\CNEN{中文}{英文}` 抽取条目，并为中文内容计算 `CNHash`；中文未变化的条目可以复用已有英文译文。
- `textran fill` 和 `textran clear` 在覆盖现有输出文件前会先写入同级 `backup/` 目录；如果输出文件本身就是权威稿件，仍应先自行确认目标路径正确。
- `llmt` 的 prompt 已约束模型保留 `\cite`、`\val` 等 LaTeX 标记，并要求遵循术语表与近邻上下文风格；术语一致性问题应优先通过术语表修正，而不是在回填后手工逐段替换。
- 自动翻译阶段允许生成英文中间稿，但不允许改变数值宏、图表引用顺序、实验边界、limitations 和模型命名口径。

### 验收标准

以下条件同时满足时，可判定一次自动化翻译链基本合格：

- 导出的条目数与预期的 `\CNEN` 段落数一致，没有抽取失败或参数错位。
- 回填后的英文 TeX 中不再残留需要继续交互处理的空英文槽位。
- `\cite`、`\ref`、`\val`、数学公式和其他 LaTeX 结构标记保持可编译状态，没有被模型改写成自然语言。
- 术语、模型名和叙事口径与当前稿件的长期约定一致，尤其不重新引入 `FRI`、`QLFRS` 等已收敛的对外命名。
- 英文稿回到本仓库后，能够继续通过本地 `latex` 校稿与编译验证。

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
