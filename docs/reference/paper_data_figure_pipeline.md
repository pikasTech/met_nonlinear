# Paper Data And Figure Pipeline

## Scope

This document records the stable workflow for `docs/paper/` and paper figures. The paper data snapshot and the paper figure workflow are separate: values and tables are refreshed from the paper data pipeline, while every paper bitmap referenced by `main.tex` is rendered from an `ex_projects/plot/` project.

## Directory Roles

`docs/paper/` and `ex_projects/plot/` use these responsibilities:

- `docs/paper/config.json`: canonical paper data-source configuration for project metrics, ex_project outputs, legacy image migrations, and plotting-code provenance.
- `docs/paper/gen_data.py`: top-level data entry; refreshes the frozen paper data snapshot, generated tables, and `latex/values.tex`.
- `docs/paper/gen_figures.py`: deprecated compatibility stub. Do not use it for figure refreshes.
- `docs/paper/src/`: implementation code for paper data collection, derived metrics, legacy plotting helpers, and migrated provenance code.
- `docs/paper/src/legacy/`: retired legacy plotting entry points kept for provenance only.
- `docs/paper/data/results.json`: frozen paper data snapshot used by generated tables and value macros.
- `docs/paper/data/values_raw.json`: machine-readable source record for values written into `latex/values.tex`.
- `docs/paper/figures/legacy/`: archived outputs from the retired `gen_figures.py` workflow and pixel-regression baselines for migrated figures; `main.tex` must not reference this directory.
- `docs/paper/image/`: migrated original image assets from the legacy paper workspace.
- `docs/paper/latex/`: manuscript, template, bibliography, and build outputs.
- `ex_projects/plot/**/config.json`: authoritative paper figure project configuration. The WebUI Figure Studio and CLI both discover figures by recursively scanning these files. For fine-grained adjusters (icon positions, card fonts, line widths, figsize), see [paper_figure_studio_adjusters.md](paper_figure_studio_adjusters.md).
- `ex_projects/plot/**/data/`: canonical rendered bitmap, `.raw.json`, and `pixel_regression.json` output directory for each paper figure project.

## Authoritative Data Flow

The stable flow is:

1. `docs/paper/config.json` declares external project paths, ex_project paths, legacy image mappings, and legacy plotting-code provenance used by the paper data snapshot.
2. `python docs/paper/gen_data.py` reads those sources and writes `docs/paper/data/results.json`, generated table fragments, and `docs/paper/latex/values.tex`.
3. Each paper figure is rendered through its own ex_project with `python cli.py ep ex_projects/plot/.../<figure_project>`.
4. A multi-panel paper figure config lists child figure projects in `paper_figure.subfigures[].project_path`; the parent montage reads child `data/` outputs and writes its own `data/` output.
5. `docs/paper/latex/main.tex` references the canonical `ex_projects/plot/**/data/*.png` outputs directly. It must not reference `docs/paper/figures/legacy/`.
6. Pixel regression compares a current `ex_projects/plot/**/data/*.png` output with the corresponding archived baseline under `docs/paper/figures/legacy/` unless the figure config explicitly names another baseline.

A valid paper data and figure flow satisfies these checks:

- Every `\val...` macro used by `main.tex` is defined in `values.tex`.
- Every `\includegraphics` path used by `main.tex` points to an existing `ex_projects/plot/**/data/*.png` output.
- Every referenced paper figure has an `ex_projects/plot/**/config.json` file with `paper_figure.figure_id`, `paper_figure.output_name`, and a same-stem `.raw.json` generated beside the bitmap.
- Every montage config references child ex_projects through `paper_figure.subfigures[].project_path` rather than by hard-coded source bitmap paths.
- Legacy images are archived under `docs/paper/figures/legacy/` before they are used as regression baselines.

## Figure Reproduction Rules

When adding or replacing paper figures:

- Create or update an ex_project under `ex_projects/plot/`. Use `single/` and `multi/` for the current convention, but tools discover any nested `config.json` under `ex_projects/plot/`.
- Run the figure through `python cli.py ep ex_projects/plot/.../<figure_project>`; do not call `docs/paper/gen_figures.py`.
- Put generated bitmap outputs, `.raw.json`, and regression reports in the ex_project `data/` directory.
- For montages, keep reusable single-panel figure projects separate and reference them from the montage config via `project_path`.
- Do not put absolute paths or legacy workspace paths in `main.tex`.
- Do not reuse one figure file for two different figure semantics; generate distinct ex_projects and distinct raw records.
- Archived legacy bitmaps may be used as regression baselines, but the editable and renderable source of truth is the ex_project config.
- Tables, figure labels, and text values must come from the same `results.json` snapshot or from an explicit migrated raw record.
- The canonical main horizontal-comparison summary figure is `ex_projects/plot/multi/fig_02_horizontal_summary/data/fig_02_horizontal_summary.png`; its raw record must include the main benchmark rows, origin metrics, metric-range rows, and convergence curves used by the metric-range, compute-speed, radar, and convergence subplots.

## Figure CLI Entry

Use the project-level EP entry for normal figure rendering:

```bash
python cli.py ep ex_projects/plot/multi/fig_02_horizontal_summary
python cli.py ep ex_projects/plot/single/fig_14_met_nonlinear_mechanism
```

Use the lower-level runner only for diagnostics and regression checks:

```bash
python -m src.visualization.paper_figure_projects list
python -m src.visualization.paper_figure_projects run-id --figure-id fig_02_horizontal_summary --strict-regression
```

`docs/paper/gen_figures.py` is intentionally retired. If an old note mentions that entry, translate it to the corresponding `python cli.py ep ex_projects/plot/...` command.

## Bibliography Rules

The repository-local bibliography source is `docs/paper/latex/nonlinear.bib`.

- `main.tex` should use the real bibliography source rather than an inline placeholder `thebibliography` block.
- When citations or `.bib` entries change, refresh `docs/paper/latex/build/main.bbl` with BibTeX before the final LaTeX build.
- The local LaTeX skill runs XeLaTeX; it does not automatically run BibTeX. Use an explicit `xelatex -> bibtex -> xelatex -> xelatex` chain when bibliography inputs change.
- If the Springer `sn-nature` BibTeX style is needed by BibTeX, keep `docs/paper/latex/sn-nature.bst` available beside `main.tex` or otherwise ensure BibTeX can resolve it.

## Legacy Workspace Migration

The legacy workspace `C:/work/met_nonlinear_paper/` is a migration source, not a runtime dependency.

Stable migration targets:

- `C:/work/met_nonlinear_paper/nonlinear.bib` -> `docs/paper/latex/nonlinear.bib`.
- `C:/work/met_nonlinear_paper/image/` -> `docs/paper/image/`.
- `C:/work/met_nonlinear_paper/figure_paper.py` -> `docs/paper/src/legacy/figure_paper.py`.
- Retired generated paper figures -> `docs/paper/figures/legacy/`.

After migration, the current repository is authoritative. Future figure edits should update `ex_projects/plot/**/config.json` and render through `python cli.py ep ...`.

## Validation Order

After updating paper data, figures, bibliography, or LaTeX references, use this order:

1. Run `python docs/paper/gen_data.py` when metrics, tables, or value macros changed.
2. Run `python cli.py ep ex_projects/plot/.../<figure_project>` for each modified figure project.
3. Run strict pixel regression for referenced figures with `python -m src.visualization.paper_figure_projects run-id --figure-id <figure_id> --strict-regression`.
4. Check that every `main.tex` figure path exists and points to an `ex_projects/plot/**/data/*.png` output.
5. Check that all `\val...` macros used by `main.tex` exist in `values.tex` and no used value is `TBD`.
6. If bibliography changed, run `xelatex -> bibtex -> xelatex -> xelatex` in `docs/paper/latex`.
7. Run the LaTeX skill build for `docs/paper/latex/main.tex` as the final reproducible build check.

## Acceptance Criteria

A paper pipeline change is complete when:

- `gen_data.py` finishes successfully if data or value macros changed.
- Every modified figure renders through `python cli.py ep ex_projects/plot/.../<figure_project>`.
- `results.json`, `values.tex`, generated tables, ex_project figure outputs, and `.raw.json` files are internally consistent.
- Strict pixel regression passes for every paper figure that should remain visually unchanged.
- `main.tex` has no absolute image or bibliography paths and no `docs/paper/figures/legacy/` image references.
- The final LaTeX build produces `docs/paper/latex/build/main.pdf` with return code `0`.
