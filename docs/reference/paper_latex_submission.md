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

本项目当前的自动化翻译能力已经统一迁移到 `llmtran` skill，权威入口是 `~/.agents/skills/llmtran/SKILL.md`。当前论文翻译不再依赖 `D:/Work/agi_mpy`，也不再以 `PAPER_TRANSLATE_*` 环境变量作为正式配置入口。

当前仓库的 canonical 英文主稿仍是 `docs/paper/latex/main.tex`。如需重走自动翻译，应先确认操作对象是仍保留 `\CNEN{中文}{英文}` 宏的中文中间稿副本，而不是已经展开为普通英文正文的最终稿。

### llmtran Skill 与本仓库的连接点

- skill 根目录固定为 `~/.agents/skills/llmtran`。
- 用户级翻译配置固定为 `~/.skill_config/llmtran/config.json`；模型、base URL、API key、thinking 和 `max_tokens` 都由该配置驱动。
- 当前论文翻译默认术语表固定由 skill 内置文件 `~/.agents/skills/llmtran/docs/paper_terms.json` 提供；本仓库不再依赖外部 `terms.json`。
- 本仓库不再维护 `paper-translate` 子命令；论文翻译统一直接调用 llmtran skill，本仓库只维护稿件路径约定、缓存路径和验收口径。

本仓库当前稳定使用的路径约定如下：

- 中文中间稿：`docs/paper/latex/main.tex`
- 导出 JSON：`cache/paper-translate/translations.json`
- 模板文件：`cache/paper-translate/template.tex`
- 英文输出 JSON：`cache/paper-translate/translations_output.json`
- 回填英文稿：`docs/paper/latex/main.translated.tex` 或新的对比输出文件

### 推荐顺序

1. 先冻结中文中间稿的技术口径、数据宏、图表顺序和边界声明，再开始自动翻译；不要把自动翻译当成结构整理工具。
2. 使用 llmtran skill 对带 `\CNEN` 宏的源 TeX 执行 `export`，生成模板和待翻译 JSON。
3. 使用 llmtran skill 的 `translate` 生成新的英文条目 JSON。
4. 用 llmtran skill 的 `fill` 把译文 JSON 回填为新的英文 TeX；如需重置英文槽位，才使用 `clear`。
5. 回填后的英文 TeX 进入本仓库的常规 LaTeX 校稿与编译链，不再继续依赖 `\CNEN` 作为最终投稿形态。

针对本仓库的稳定命令形态见下节；长期口径只保留一套 llmtran skill 直连示例，不再在文档中重复维护等价命令块。

### llmtran Skill 直连命令

本项目的长期口径是直接调用 llmtran skill，不再经过任何仓库内转发层。常用命令形态如下：

```bash
python C:/Users/lyon/.agents/skills/llmtran/scripts/llmtran-cli.py dry-run
python C:/Users/lyon/.agents/skills/llmtran/scripts/llmtran-cli.py check
python C:/Users/lyon/.agents/skills/llmtran/scripts/llmtran-cli.py export --input C:/work/met_nonlinear_master/docs/paper/latex/main.tex --translations C:/work/met_nonlinear_master/cache/paper-translate/translations.json --template C:/work/met_nonlinear_master/cache/paper-translate/template.tex
python C:/Users/lyon/.agents/skills/llmtran/scripts/llmtran-cli.py translate --translations C:/work/met_nonlinear_master/cache/paper-translate/translations.json --output C:/work/met_nonlinear_master/cache/paper-translate/translations_output.json
python C:/Users/lyon/.agents/skills/llmtran/scripts/llmtran-cli.py status --job-id <job_id>
python C:/Users/lyon/.agents/skills/llmtran/scripts/llmtran-cli.py logs --job-id <job_id> --tail 30
python C:/Users/lyon/.agents/skills/llmtran/scripts/llmtran-cli.py result --job-id <job_id>
python C:/Users/lyon/.agents/skills/llmtran/scripts/llmtran-cli.py debug prompt --translations C:/work/met_nonlinear_master/cache/paper-translate/translations.json --entry-id 12
```

本仓库侧只保留以下长期约束：

- `dry-run` 和 `check` 用于直接查看 llmtran 当前配置与依赖状态。
- `export`、`fill`、`clear`、`translate` 都使用 llmtran 的异步任务系统；命令返回后应继续用 `status`、`logs`、`result` 查询进度，而不是假定同步完成。
- `debug prompt` 直接调用 llmtran 的真实 prompt 生成逻辑，用于排查术语表、上下文窗口和 LaTeX 保留规则是否生效。

### 续翻、重翻与结果切换

翻译结果管理的长期约束如下：

- `--resume` 只用于同一份 `translations.json`、同一输出 JSON 和同一组关键翻译配置下的中断恢复；如果模型、术语表、配置或中文源内容已经变化，应视为新一轮翻译，而不是续翻旧结果。
- 需要整轮重跑时，使用 `llmtran-cli.py translate --retranslate`，并把 `--output` 指向新的结果文件；不要直接覆盖当前权威 `translations_output.json`。
- 在发起重翻之前，先备份当前权威翻译 JSON 与当前使用中的英文 TeX；skill 自动生成的同级 `backup/` 只覆盖单次写文件保护，不承担版本对比职责。
- 对比不同模型或不同配置的翻译效果时，旧版和新版应同时保留各自的 JSON 与回填 TeX；先比较条目级改写范围、术语一致性、LaTeX 结构完整性与编译结果，再决定是否切换主入口文件。
- 仓库内不再维护翻译转发层；论文翻译统一直接调用 llmtran skill，不要再新增或恢复任何 repo 内包装脚本，也不要把翻译流程重新挂回 `agi_mpy`。

### 稳定行为与判定口径

- llmtran 的 `export` 会按 `\CNEN{中文}{英文}` 抽取条目，并为中文内容计算 `CNHash`；中文未变化的条目可以复用已有英文译文。
- llmtran 的 `fill` 和 `clear` 在覆盖现有输出文件前会先写入同级 `backup/` 目录；如果输出文件本身就是权威稿件，仍应先自行确认目标路径正确。
- llmtran 的 `translate` prompt 已约束模型保留 `\cite`、`\ref`、`\val` 等 LaTeX 标记，并要求遵循术语表与近邻上下文风格；术语一致性问题应优先通过术语表修正，而不是在回填后手工逐段替换。
- 自动翻译阶段允许生成英文中间稿，但不允许改变数值宏、图表引用顺序、实验边界、 limitations 和模型命名口径。

以下条件同时满足时，可判定一次自动化翻译链基本合格：

- 导出的条目数与预期的 `\CNEN` 段落数一致，没有抽取失败或参数错位。
- 回填后的英文 TeX 中不再残留需要继续交互处理的空英文槽位。
- `\cite`、`\ref`、`\val`、数学公式和其他 LaTeX 结构标记保持可编译状态，没有被模型改写成自然语言。
- 术语、模型名和叙事口径与当前稿件的长期约定一致，尤其不重新引入 `FRI`、`QLFRS` 等已收敛的对外命名。
- 英文稿回到本仓库后，能够继续通过本地 `latex` 校稿与编译验证。

llmtran skill 的通用能力、配置 schema 和 debug 细节以 `~/.agents/skills/llmtran/SKILL.md` 为准；本仓库文档只维护与当前论文目录、缓存路径和验收口径相关的长期约束。

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

### 仓库内 paper-latex CLI

仓库内现提供统一的 `paper-latex` 子命令，用于把常用的 `xelatex + bibtex + xelatex + xelatex` 编译链收敛到同一个入口，避免手工漏跑 `bibtex`。

常用命令形态：

```bash
python cli.py paper-latex build
python cli.py paper-latex build --tex main.translated.tex
python cli.py paper-latex build --tex main.translated.tex --output-dir build
```

稳定约定如下：

- 默认工作目录是 `docs/paper/latex`。
- 默认入口文件是 `main.tex`；如需编译翻译稿，显式传入 `--tex main.translated.tex`。
- 默认输出目录是 `docs/paper/latex/build`。
- 默认引擎是 `xelatex`。
- 默认总共执行 3 次 LaTeX pass，并在第 1 次之后自动执行 1 次 `bibtex`。
- 只有在明确确认当前稿件不需要文献收敛时，才使用 `--no-bibtex`。

等价的默认编译链可理解为：

```bash
xelatex -interaction=nonstopmode -file-line-error -output-directory=build main.translated.tex
bibtex build/main.translated
xelatex -interaction=nonstopmode -file-line-error -output-directory=build main.translated.tex
xelatex -interaction=nonstopmode -file-line-error -output-directory=build main.translated.tex
```

使用注意事项如下：

- `--tex` 既可以传工作目录下的相对路径，也可以传绝对路径；相对路径的基准是 `--workdir`，不是当前 shell 的工作目录。
- `--output-dir` 可以是相对目录或绝对目录；相对目录时，产物会落在 `--workdir` 下对应子目录。
- 引擎解析顺序是“显式绝对路径”优先，其次查 `PATH`，最后回退到 `D:/texlive/2024/bin/windows/<engine>.EXE`；如果本机 TeX Live 不在该位置，应优先修正环境而不是在文档里固化临时路径。
- 当启用 `bibtex` 时，`--passes` 至少应为 `2`；当前实现会直接拒绝 `passes < 2` 的组合，避免只跑出半收敛产物。
- 该命令按阶段顺序执行，任意一步返回非 0 就会立即停止并返回当前阶段名；排障时先看失败阶段，而不是先怀疑整个链路都坏了。
- 命令执行过程中输出保持前台可见；如果只想拿到最终 PDF 路径而不关心 warning，不应再人为包一层静默脚本，否则会损失最直接的错误定位信息。

实现架构约定如下：

- [src/core/cli_parser.py](src/core/cli_parser.py) 负责声明 `paper-latex build` 子命令、默认参数和轻量子命令入口，并把解析结果映射回 `CLIArgs`。
- [cli.py](cli.py) 只负责识别 `paper-latex` 命令并调用专用 runner，不负责具体阶段编排。
- [src/core/paper_latex_cli.py](src/core/paper_latex_cli.py) 是编译链的唯一实现入口：`build_paper_latex_plan(...)` 负责解析路径、引擎和 stage 列表，`run_paper_latex_subcommand(...)` 负责顺序执行并输出 JSON 状态。
- 路径解析由 `_resolve_repo_path(...)` 和 `_relative_or_absolute(...)` 统一处理；可执行文件解析由 `_resolve_executable(...)` 统一处理，避免把 PATH 查找、绝对路径和 TeX Live fallback 散落到 CLI 主入口里。
- 运行期输出协议固定为 JSON `running` / `ok` / `error` 包络加实时子进程输出；`ok` 阶段会附带 `outputPdf` 和每个 stage 的 `stageReturncodes`，便于上层自动消费。
- 解析与执行层的回归点分别在 [src/tests/core/test_cli_parser.py](src/tests/core/test_cli_parser.py) 和 [src/tests/core/test_paper_latex_cli.py](src/tests/core/test_paper_latex_cli.py)。

判定仓库内编译命令可复用的最小标准：

- 命令执行过程中子进程输出保持前台可见，便于直接看 warning 与错误位置。
- 命令结束后产物稳定落在 `docs/paper/latex/build/` 或显式指定的输出目录。
- 对有参考文献的稿件，不再需要手工补跑 `bibtex` 才能得到收敛结果。

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
