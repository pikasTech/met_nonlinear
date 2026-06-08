# 论文数据与图流水线

## 适用范围

本文档记录 `docs/paper/` 与论文图产物的长期稳定工作流。论文数据快照与论文图工作流彼此分离：数值宏和表格通过 paper data pipeline 刷新，而 `main.tex` 引用的每一张论文位图都由对应的 `ex_projects/plot/` 工程渲染生成。

## 目录职责

`docs/paper/` 与 `ex_projects/plot/` 的职责分工如下：

- `docs/paper/config.json`：论文数据源的 canonical 配置，负责声明 project 指标来源、ex_project 输出、旧图迁移映射以及绘图代码溯源信息。
- `docs/paper/gen_data.py`：顶层数据入口，用于刷新冻结的论文数据快照、生成表格片段以及 `latex/values.tex`。
- `docs/paper/gen_figures.py`：已废弃的兼容性 stub，不再作为论文图刷新入口使用。
- `docs/paper/src/`：论文数据采集、派生指标、旧绘图辅助逻辑与迁移后溯源代码的实现目录。
- `docs/paper/src/legacy/`：仅用于保留溯源信息的已退役旧绘图入口。
- `docs/paper/data/results.json`：冻结的论文数据快照，供生成表格和数值宏使用。
- `docs/paper/data/values.generated.json`：可选的机器可读数值覆盖记录；`values_raw.json` 属于已废弃旧缓存，论文构建以 `latex/values.tex` 为准。
- `docs/paper/figures/legacy/`：来自已退役 `gen_figures.py` 工作流的归档输出，以及迁移图使用的像素回归基线；`main.tex` 不得引用该目录。
- `docs/paper/image/`：从旧论文工作区迁移来的原始图片资源。
- `docs/paper/latex/`：稿件、模板、参考文献和构建产物所在目录。
- `ex_projects/plot/**/config.json`：论文图工程的权威配置入口。WebUI Figure Studio 与 CLI 都通过递归扫描这些文件发现论文图工程。若需调节图标位置、卡片字体、线宽、figsize 等细粒度参数，见 [paper_figure_studio_adjusters.md](paper_figure_studio_adjusters.md)。
- `ex_projects/plot/**/data/`：每个论文图工程的 canonical 位图、`.raw.json` 和 `pixel_regression.json` 输出目录。

## 权威数据流

稳定的数据流如下：

1. `docs/paper/config.json` 声明论文数据快照所需的外部 project 路径、ex_project 路径、旧图映射以及旧绘图代码溯源信息。
2. `python docs/paper/gen_data.py` 读取这些来源，并写出 `docs/paper/data/results.json`、生成的表格片段以及 `docs/paper/latex/values.tex`。若生成机器可读宏覆盖记录，应写入 `docs/paper/data/values.generated.json`。
3. 每一张论文图都通过各自的 ex_project，使用 `python cli.py ep ex_projects/plot/.../<figure_project>` 渲染生成。
4. 多面板论文图配置通过 `paper_figure.subfigures[].project_path` 列出子图工程；父级 montage 读取子图 `data/` 输出，再写出自己的 `data/` 输出。
5. `docs/paper/latex/main.tex` 直接引用 canonical 的 `ex_projects/plot/**/data/*.png` 输出，不得引用 `docs/paper/figures/legacy/`。
6. 除非图配置显式指定了其他基线，否则像素回归默认将当前 `ex_projects/plot/**/data/*.png` 输出与 `docs/paper/figures/legacy/` 下对应的归档基线进行比较。

满足以下检查时，可判定 paper data 与 figure 流程有效：

- `main.tex` 中使用的每个 `\val...` 宏都已在 `values.tex` 中定义。
- `main.tex` 中使用的每个 `\includegraphics` 路径都指向存在的 `ex_projects/plot/**/data/*.png` 输出。
- 每张被引用的论文图都拥有对应的 `ex_projects/plot/**/config.json`，并在位图旁生成同名 `.raw.json`，其中包含 `paper_figure.figure_id` 与 `paper_figure.output_name`。
- 每个 montage 配置都通过 `paper_figure.subfigures[].project_path` 引用子图 ex_project，而不是直接硬编码源位图路径。
- 所有 legacy 图片在被用作回归基线前，都已归档到 `docs/paper/figures/legacy/`。

## 图复现规则

当新增或替换论文图时：

- 在 `ex_projects/plot/` 下创建或更新 ex_project。当前约定使用 `single/` 与 `multi/`，但工具会发现 `ex_projects/plot/` 下任意层级中的 `config.json`。
- 使用 `python cli.py ep ex_projects/plot/.../<figure_project>` 渲染图，不要再调用 `docs/paper/gen_figures.py`。
- 将生成的位图、`.raw.json` 和回归报告写入该 ex_project 的 `data/` 目录。
- 对于拼图，保持可复用的单面板图工程独立存在，并在 montage 配置中通过 `project_path` 引用。
- 不要在 `main.tex` 中写入绝对路径或旧工作区路径。
- 不要让同一个图文件承担两种不同的图语义；应生成彼此独立的 ex_project 与独立 raw 记录。
- 归档 legacy 位图可以作为回归基线，但可编辑、可重渲染的唯一事实来源仍然是 ex_project 配置。
- 表格、图中文字标签以及正文数值必须来自同一个 `results.json` 快照，或来自显式迁移的 raw 记录。
- 主横向对比摘要图的 canonical 路径是 `ex_projects/plot/multi/fig_02_horizontal_summary/data/fig_02_horizontal_summary.png`；其 raw 记录必须包含主 benchmark 行、origin 指标、metric-range 行以及用于 metric-range、compute-speed、radar 与 convergence 子图的收敛曲线。

## 主文与 Supplement 图件边界

主文和 Supplement 的图件不能互相重复。主文用于承载论文结论链条所需的核心图，Supplement 只补充主文没有展示的推导、协议细节、扩展消融、超参数敏感性和部署验证细节。

稳定判定如下：

- 如果一个图或子图已经进入 `main.translated.tex` 的主文图序列，`supplement.tex` 中不得再放同一位图、同义拼图或仅改 caption 的重复版本。
- 如果某个 supplement 图被迁移到主文，supplement 中对应的完整图注、重复解释段和结果再叙述应同步删除；最多保留一句短上下文，把读者指向主文图或保留后续补充分析。
- Supplement 里的图应有独立信息增量，例如更多频点、更多变体、额外推导检查、额外超参数或部署 sweep；不能只是主文图的另一种排版。
- 主文和 supplement 都引用同一组底层数据时，图内显示层应错开：主文展示核心结论，supplement 展示支撑细节。
- 多子图从 supplement 调回主文后，应更新 montage 配置，让主文图直接引用 leaf 子图工程；不要让 supplement montage 继续作为主文 montage 的来源。

投稿前检查图件重复时，按以下顺序进行：

1. 扫描 `main.translated.tex` 与 `supplement.tex` 的 `\includegraphics` 路径，确认没有同一路径重复出现。
2. 对不同路径但相同 `figure_id`、相同源数据或相同视觉语义的图，检查是否属于主文/补充材料重复。
3. 打开相邻正文和 caption，确认 supplement 没有重复解释已经由主文承担的机制、流程或结果。
4. 对迁移过的图，检查旧 supplement 图位、旧 label 和旧 cross-reference 是否已经清理。

可用的粗筛命令：

```bash
rg -n "\\includegraphics" docs/paper/latex/main.translated.tex docs/paper/latex/supplement.tex
rg -n "\\label\\{fig:|\\caption\\{" docs/paper/latex/main.translated.tex docs/paper/latex/supplement.tex
```

粗筛只能发现同路径或同 label 问题；最终仍需目视比较主文和 supplement 的 PDF 页面，确认不存在同义重复。

## 数值与图文一致性检查

投稿前应把正文、caption、表格、`values.tex`、`results.json`、项目级 `metrics.json` 和图件 `.raw.json` 看成同一证据链，而不是分散产物。任何主结果数值、频带、单位或数据划分口径发生变化时，都需要同步检查这些层级。

长期口径如下：

- 论文正式频带收敛到 `10--128 Hz`；不要在主文、caption、表格或 supplement 参数表中混入旧的 `200 Hz` 评价口径。
- 灵敏度漂移当前按 `100 Hz` 处绝对灵敏度漂移表达，单位为 `V s/m` 或等价 LaTeX 单位；不要再把该值写成百分比。
- 未补偿 MET 的自然频率和灵敏度随震级变化，正文优先写 min--max 范围；若百分比不能从当前端点和定义复现，应删除百分比。
- `values_raw.json` 是旧缓存，不作为 TeX 编译事实来源；论文构建以 `docs/paper/latex/values.tex` 为准。若旧缓存不再被 pipeline 引用，应废弃或明确标记，避免旧划分和旧频带回流。
- Fig.2(b) 数据流程图应与当前实现一致：每个工况内时域 train/validation split，输入和目标序列 min--max scaling 到 `[-1, 1]`，并基于相同划分重算指标。
- 表格单位应使用清晰 LaTeX 上标和乘点，不出现 `m/s2` 这类纯文本单位。
- 图内符号必须被正文或 caption 解释；机制图可适度模糊，但不要出现正文从未定义且会被读者视作精确定义的新符号。

推荐检查顺序：

1. 先查频带、单位和数据划分这类全局口径。
2. 再查主结果表、消融表、横向对比图和摘要中的关键数值是否来自同一批 `metrics.json` / `results.json`。
3. 接着查每张主图的 `.raw.json`，确认 source trace、输入数据和图内标签与正文一致。
4. 最后检查 supplement 的参数表、扩展图和说明段，确认没有把旧主文口径重新带回来。

常用残留搜索：

```bash
rg -n "200\\s*Hz|10--200|10~200|254\\.6|Sens Drift \\(%\\)|m/s2|values_raw" docs/paper/latex docs/paper/data docs/paper/src ex_projects/plot
rg -n "50%|175|350 / 350|\\[-1, 1\\]|min--max|temporal" docs/paper/latex/main.translated.tex docs/paper/latex/supplement.tex ex_projects/plot
```

## 图 CLI 入口

正常渲染论文图时，使用 project 级 EP 入口：

```bash
python cli.py ep ex_projects/plot/multi/fig_02_horizontal_summary
python cli.py ep ex_projects/plot/single/fig_14_met_nonlinear_mechanism
```

仅在诊断和回归检查场景下，才使用更底层的 runner：

```bash
python -m src.visualization.paper_figure_projects list
python -m src.visualization.paper_figure_projects run-id --figure-id fig_02_horizontal_summary --strict-regression
```

`docs/paper/gen_figures.py` 已被明确退役。若旧笔记仍提到该入口，应将其替换理解为对应的 `python cli.py ep ex_projects/plot/...` 命令。

## 参考文献规则

仓库内本地参考文献源为 `docs/paper/latex/nonlinear.bib`。

- `main.tex` 应使用真实的 bibliography 数据源，而不是内联占位的 `thebibliography` 块。
- 当 citation 或 `.bib` 条目发生变化时，最终 LaTeX 构建前必须用 BibTeX 刷新 `docs/paper/latex/build/main.bbl`。
- 本地 LaTeX skill 使用 XeLaTeX，但不会自动运行 BibTeX；当参考文献输入变化时，应显式执行 `xelatex -> bibtex -> xelatex -> xelatex`。
- 若 BibTeX 需要 Springer 的 `sn-nature` 样式，应确保 `docs/paper/latex/sn-nature.bst` 位于 `main.tex` 同级，或通过其他方式保证 BibTeX 能解析到该文件。

## 旧工作区迁移

旧工作区 `C:/work/met_nonlinear_paper/` 仅是迁移来源，不是运行时依赖。

稳定迁移目标如下：

- `C:/work/met_nonlinear_paper/nonlinear.bib` -> `docs/paper/latex/nonlinear.bib`.
- `C:/work/met_nonlinear_paper/image/` -> `docs/paper/image/`.
- `C:/work/met_nonlinear_paper/figure_paper.py` -> `docs/paper/src/legacy/figure_paper.py`.
- 已退役的论文图生成产物 -> `docs/paper/figures/legacy/`.

迁移完成后，当前仓库即为权威来源。后续论文图修改应直接更新 `ex_projects/plot/**/config.json`，并通过 `python cli.py ep ...` 渲染。

## 验证顺序

当更新论文数据、论文图、参考文献或 LaTeX 引用后，按以下顺序验证：

1. 若指标、表格或数值宏发生变化，先运行 `python docs/paper/gen_data.py`。
2. 对每个修改过的图工程运行 `python cli.py ep ex_projects/plot/.../<figure_project>`。
3. 对被引用的图运行严格像素回归：`python -m src.visualization.paper_figure_projects run-id --figure-id <figure_id> --strict-regression`。
4. 检查 `main.tex` 中每个图路径都存在，并且都指向 `ex_projects/plot/**/data/*.png` 输出。
5. 检查 `main.tex` 中使用的全部 `\val...` 宏都存在于 `values.tex` 中，且没有被使用的值是 `TBD`。
6. 若参考文献发生变化，则在 `docs/paper/latex` 中执行 `xelatex -> bibtex -> xelatex -> xelatex`。
7. 最后对 `docs/paper/latex/main.tex` 运行 LaTeX skill build，作为可复现的最终构建检查。

## 验收标准

当满足以下条件时，可判定一次 paper pipeline 修改完成：

- 如果数据或数值宏有变化，`gen_data.py` 能成功完成。
- 每个被修改的图都能通过 `python cli.py ep ex_projects/plot/.../<figure_project>` 成功渲染。
- `results.json`、`values.tex`、生成表格、ex_project 图输出以及 `.raw.json` 之间保持内部一致。
- 对所有视觉上应保持不变的论文图，严格像素回归均通过。
- `main.tex` 中不存在绝对图片路径、绝对 bibliography 路径，也不存在对 `docs/paper/figures/legacy/` 图片的引用。
- 最终 LaTeX 构建能生成 `docs/paper/latex/build/main.pdf`，且返回码为 `0`。
