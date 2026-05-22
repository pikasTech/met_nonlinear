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
- `docs/paper/data/values_raw.json`：写入 `latex/values.tex` 的机器可读数值源记录。
- `docs/paper/figures/legacy/`：来自已退役 `gen_figures.py` 工作流的归档输出，以及迁移图使用的像素回归基线；`main.tex` 不得引用该目录。
- `docs/paper/image/`：从旧论文工作区迁移来的原始图片资源。
- `docs/paper/latex/`：稿件、模板、参考文献和构建产物所在目录。
- `ex_projects/plot/**/config.json`：论文图工程的权威配置入口。WebUI Figure Studio 与 CLI 都通过递归扫描这些文件发现论文图工程。若需调节图标位置、卡片字体、线宽、figsize 等细粒度参数，见 [paper_figure_studio_adjusters.md](paper_figure_studio_adjusters.md)。
- `ex_projects/plot/**/data/`：每个论文图工程的 canonical 位图、`.raw.json` 和 `pixel_regression.json` 输出目录。

## 权威数据流

稳定的数据流如下：

1. `docs/paper/config.json` 声明论文数据快照所需的外部 project 路径、ex_project 路径、旧图映射以及旧绘图代码溯源信息。
2. `python docs/paper/gen_data.py` 读取这些来源，并写出 `docs/paper/data/results.json`、生成的表格片段以及 `docs/paper/latex/values.tex`。
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
