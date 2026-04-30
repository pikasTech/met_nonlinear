# 论文图可追溯与修改工作流

本文档记录 `docs/paper/latex/main.tex` 所引用论文图的长期修改规范，适用于实验曲线图、机理示意图、结构框图，以及从旧论文迁移来的历史图。当前论文图的可编辑入口统一收敛到 `ex_projects/plot/**/config.json`，渲染输出统一落到对应 ex_project 的 `data/` 目录。

## 不可违反的规则

- 修改任何已有论文图之前，必须先追溯原始绘图实现、数据来源和生成入口。
- 修改应落在原始绘图代码或忠实迁移后的等价代码中。
- 禁止在 PNG 上涂抹标签、覆盖文字或通过局部贴图代替源代码级修改。
- 除非已经证明旧实现无法恢复，并且重新核对过数据、公式、坐标定义和布局，否则不要新建独立绘图脚本去仿制旧图。
- 如果当前仓库缺少原始实现，应继续追溯旧论文仓库。本项目优先检查 `C:/work/met_nonlinear_paper`。
- 修改范围应限于用户明确要求的图和标签，不要顺手重生成或替换无关图。

## 追溯顺序

1. 从 `docs/paper/latex/main.tex` 开始，确认图号、caption、`\includegraphics` 路径和正文上下文。
2. 检查 `\includegraphics` 是否指向 `ex_projects/plot/**/data/*.png`，再打开同级或父级 ex_project 的 `config.json`，确认 `paper_figure.figure_id`、`paper_figure.output_name`、`generation_mode` 和 `regression.baseline_path`。
3. 如果是拼图，检查 `paper_figure.subfigures[].project_path`，逐个追溯子图 ex_project；拼图配置不得绕过子图 ex_project 直接引用最终论文位图。
4. 在当前仓库中按图片名、输出文件名、caption 关键词、绘图函数名和数据文件名搜索。优先使用 `rg --files` 和 `rg -n`。
5. 如果当前仓库信息不完整，继续搜索 `C:/work/met_nonlinear_paper`，重点检查 `cli.py`、`plot_*.py`、`figure_paper.py`、`fig_pdf.py`、`data/` 和旧 `projects/`。
6. 只有当输出文件名、输入数据、子图结构、坐标轴、采样方式、图例、视角和最终拼图方式都能对应到稿件图时，才算追溯成功。
7. 将可复现入口迁移到 `ex_projects/plot/`，并在 ex_project 的 `data/` 目录写出 `.raw.json`，记录 `source_trace`、`translation_method` 和 `note`。

## 修改方式

- 标签翻译只修改图例、坐标轴标签、行列标签和面板内文字。已有标题类文本必须按下文的图标题策略处理，而不是继续保留为图内标题。
- 除非用户明确要求，不要改变曲线、数据筛选、采样间隔、坐标范围、视角或子图组合方式。
- 如果标签被裁切或位置不佳，应通过 `figsize`、`subplots_adjust`、`bbox_inches`、`labelpad`、字号或布局参数修复，不要直接编辑位图。
- 如果旧数据位于当前仓库之外，要从已追溯的旧路径显式读取，或把必要数据迁移到可复现的数据位置。不要从截图反推数值。
- 生成后必须目视检查是否仍有非英文标签、裁切、重叠、错误数据、caption 语义不匹配或不必要的布局漂移。
- 正常渲染入口是 `python cli.py ep ex_projects/plot/.../<figure_project>`；`docs/paper/gen_figures.py` 已废弃，不能作为新的修改入口。
- 精细调整约定：若需暴露绘图参数（如图标位置、卡片字体、线宽、figsize）供 Figure Studio 调节，详见 [paper_figure_studio_adjusters.md](paper_figure_studio_adjusters.md)。

## 图标题策略

- 论文图和子图不应包含独立标题区。这里包括 Matplotlib `suptitle`、坐标轴 `set_title()`、legend title、顶部标题、底部标题，以及嵌入位图中的 caption 式说明文字。
- 删除标题是信息迁移，不是信息删除。原本由标题承载的含义必须迁移到 LaTeX caption 或正文中，并用 `(a)`、`(b)`、`(c)`、`(d)` 等子图编号显式说明。
- 多子图 caption 应按顺序说明每个面板的作用。例如写成 `(a) 自然频率轨迹…… (b) 灵敏度轨迹……`，不要依赖画在子图内部的标题文字。
- 坐标轴标签、刻度标签、图例项、曲线标注、行标签、列标签和示意图组件标签可以保留，因为它们属于数据或图示本身；但它们不应重复 caption 层面的标题。
- 如果从代码生成图中移除了标题，要在同一次修改中更新 `docs/paper/latex/main.tex`，确保 caption 或相邻段落保留对应的子图语义。
- 如果移除标题后在 LaTeX 中调整了图的插入宽度，要同步更新 paper pipeline 中对应的 `latex_width_fraction`，保证外置 `(a)/(b)/(c)` 标签在编译后的 PDF 中保持预期物理字号。

## raw 标题审计

- 论文图 ex_project runner 和复用的 paper plotting helper 是 raw 标题防线的权威入口。新增 Matplotlib 生成的论文图时，应使用共享保存路径，使相邻 `.raw.json` 记录 `matplotlib_title_artifacts`。
- paper pipeline 应在 raw 文件生成后调用 `validate_raw_title_free()`。审计必须在发现非空标题痕迹或 raw metadata 中出现 `title`、`subtitle`、`suptitle`、`figure_title`、`panel_title`、`subplot_title`、`axes_title`、`plot_title`、`legend_title` 等字段时失败。
- raw 审计通过只表示 metadata 中没有已知标题痕迹，不能替代目视检查。手工复制图、AI 渲染图或外部位图仍需查看渲染结果，确认没有可见的标题类文字。
- 不要通过重命名 raw metadata 字段绕过审计。如果信息属于论文内容，应写入 LaTeX caption 或正文；如果信息属于溯源，应使用 `source_trace`、`modification_scope`、`note` 或数据专用字段等非标题字段。

## 位图拼图标签

- 多子图位图应通过 `ex_projects/plot/multi/**/config.json` 调用 `src/visualization/subfigure_montage.py`，不要手工把 `(a)`、`(b)`、`(c)` 粘到导出的 PNG 上。
- 拼图的每个子图应优先拥有独立的 `ex_projects/plot/single/**/config.json`；拼图通过 `paper_figure.subfigures[].project_path` 引用子图工程。
- 子图标签的标准目标字号为 `8 pt`，该字号指拼图缩放到 `docs/paper/latex/main.tex` 使用的 Springer Nature A4 正文宽度后的最终物理字号。
- 拼图工具应按 `label_font_size_pt * canvas_width_px / (label_reference_width_pt * latex_width_fraction)` 计算像素字号，使标签大小与源图分辨率无关。
- `label_reference_width_pt` 应与稿件正文宽度保持一致，当前采用 Springer Nature A4 正文宽度作为统一参考。
- `latex_width_fraction` 应来自 LaTeX `\includegraphics` 的插入宽度。比如某图以 `0.5\textwidth` 插入时，应设置 `latex_width_fraction=0.5`，这样位图标签会按比例变大，并在最终 PDF 中仍显示为 `8 pt`。
- 子图标签默认应置于子图内容外部。优先使用 `outside-top-left` 和按行分配的标签带，确保标签不遮挡坐标轴、图例、曲线、示意文字或面板内容。
- 同名 `.raw.json` 应写在 ex_project 的 `data/` 目录，并记录最终像素字号、目标物理字号、参考宽度、LaTeX 宽度比例、标签位置和行标签带高度。

## Fig. 10、Fig. 12 和 Fig. 18 的经验

- Fig. 10 可追溯到 `C:/work/met_nonlinear_paper/plot_epoch_IO.py`，数据来自 `C:/work/met_nonlinear_paper/projects/FRIKANwp/data/epoch_*_IO.json`。有效修改范围限于列语义、epoch 行标签和 caption 中的行列说明。
- Fig. 12 可追溯到 `C:/work/met_nonlinear_paper/plot_frirnn.py`。其数据嵌入在 `zeta_origin`、`fn_origin`、`Sn_origin` 和 `magnitudes` 中；原始代码使用解析传递函数、三维响应切片、固定视角和双面板拼图。有效修改范围限于 `Frequency`、`Magnitude`、`Sensitivity`、`Relative gain` 等轴标签。
- Fig. 18 可追溯到 `C:/work/met_nonlinear_paper/plot_predict.py`，数据来自 `C:/work/met_nonlinear_paper/data/predict_features.json`。有效修改范围限于 `Raw`、`Compensated`、`Target` 图例，以及全局 `Output` 和 `Time` 坐标轴标签。
- 旧仓库 `C:/work/met_nonlinear_paper/cli.py` 是有用索引：`--epoch-io` 对应 Fig. 10，`--frirnn` 对应 Fig. 12，`--predict` 对应 Fig. 18。
- 当前的 `legacy_*.png` 往往只是迁移后的输出图。如果 `docs/paper/src/legacy/figure_paper.py` 缺少依赖模块，应继续到旧仓库追溯，不要直接判定为不可追溯。

## 验收标准

- 每个修改后的图都有可复现 ex_project 入口，并写入稿件实际引用的 `ex_projects/plot/**/data/*.png` 路径。
- 每个修改后的图旁都有 `.raw.json`，记录源代码、源数据和修改范围。
- 对视觉应保持不变的迁移图，`pixel_regression.json` 应显示当前 `data/*.png` 与 `docs/paper/figures/legacy/` 基线像素一致。
- raw 标题审计通过，并通过目视检查确认图和子图中不存在独立的顶部或底部标题。
- 所有被移除的图内标题信息，都已在 `docs/paper/latex/main.tex` 的 caption 或相邻正文中用明确的 `(a)/(b)/(c)` 子图引用保留。
- LaTeX 编译成功，且 `latex` skill 的 layout check 不报告 `question_mark_in_pdf`、`underfilled_page`、`margin_overflow_risk` 或图表布局错误。
- 对 legacy 图，要比较旧图和新图，确认面板结构、绘制数据和视觉逻辑保持一致；只改变用户要求的文字或明确要求的样式细节。
