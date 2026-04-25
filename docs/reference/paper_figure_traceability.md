# Paper Figure Traceability And Modification Workflow

This document records the long-term workflow for translating, adjusting, or migrating figures used by `docs/paper/latex/main.tex`. It applies to experimental plots, mechanism diagrams, schematic figures, and legacy figures copied from earlier manuscripts.

## Non-Negotiable Rule

- Before modifying any existing paper figure, trace the original plotting implementation, data source, and generation entry point.
- Make the requested change in the original plotting code or a faithful migrated version of that code.
- Do not paint over bitmap labels, paste new text on top of a PNG, or use local image patches as a substitute for source-level modification.
- Do not create a new independent plotting script to mimic an old figure unless the old implementation is proven unrecoverable and the data, equations, coordinate definitions, and layout have been rechecked.
- If the current repository does not contain the original implementation, continue tracing in legacy manuscript repositories. For this project, first check `C:/work/met_nonlinear_paper`.
- Limit the edit scope to the figures and labels explicitly requested by the user. Do not regenerate or replace unrelated figures.

## Trace Order

1. Start from `docs/paper/latex/main.tex`: identify the figure number, caption, `includegraphics` path, and surrounding text.
2. Inspect the referenced asset under `docs/paper/figures/`, then compare with `docs/paper/image/` and `docs/paper/assets/` to decide whether it is migrated or pipeline-generated.
3. Search the current repository for the image name, output file name, caption keywords, plotting function names, and data file names. Prefer `rg --files` and `rg -n`.
4. If the current repository is incomplete, search `C:/work/met_nonlinear_paper` and inspect `cli.py`, `plot_*.py`, `figure_paper.py`, `fig_pdf.py`, `data/`, and legacy `projects/`.
5. Treat tracing as successful only when output filename, input data, panel structure, axes, sampling, legends, camera/view, and final composition all match the manuscript figure.
6. Migrate the reproducible entry point into `docs/paper/src/` or the existing paper pipeline, and emit a `.raw.json` next to the generated figure with `source_trace`, `translation_method`, and `note`.

## How To Modify

- For label translation, change only titles, legends, axis labels, row/column labels, and panel text in the traced source code.
- Keep curves, data selection, sampling intervals, coordinate limits, camera/view settings, and panel composition unchanged unless the user asks for those changes.
- If a label is clipped or badly placed, fix it through plotting parameters such as `figsize`, `subplots_adjust`, `bbox_inches`, `labelpad`, font size, or layout parameters. Do not fix it by editing the bitmap.
- If old data is outside the current repository, either read it explicitly from the traced legacy path or migrate the needed data into a reproducible data location. Do not infer numerical data from screenshots.
- After generation, visually inspect the figure for residual non-English labels, clipping, overlap, wrong data, wrong caption semantics, or unwanted layout drift.

## Experience From Fig. 10, Fig. 12, And Fig. 18

- Fig. 10 traces to `C:/work/met_nonlinear_paper/plot_epoch_IO.py`, with data from `C:/work/met_nonlinear_paper/projects/FRIKANwp/data/epoch_*_IO.json`. The valid English edit is limited to column headers and epoch row labels.
- Fig. 12 traces to `C:/work/met_nonlinear_paper/plot_frirnn.py`. Its data are embedded in `zeta_origin`, `fn_origin`, `Sn_origin`, and `magnitudes`; the original code uses analytical transfer functions, 3-D response slices, fixed view settings, and two-panel composition. The valid English edit is limited to axis labels such as `Frequency`, `Magnitude`, `Sensitivity`, and `Relative gain`.
- Fig. 18 traces to `C:/work/met_nonlinear_paper/plot_predict.py`, with data from `C:/work/met_nonlinear_paper/data/predict_features.json`. The valid English edit is limited to the `Raw`, `Compensated`, and `Target` legend plus global `Output` and `Time` axis labels.
- The legacy `C:/work/met_nonlinear_paper/cli.py` is a useful index: `--epoch-io` maps to Fig. 10, `--frirnn` maps to Fig. 12, and `--predict` maps to Fig. 18.
- A current `legacy_*.png` file is often only the migrated output. If `docs/paper/src/legacy/figure_paper.py` imports missing modules, continue tracing in the legacy repository instead of declaring the figure untraceable.

## Acceptance Criteria

- Each modified figure has a reproducible generation entry point and writes to the exact `docs/paper/figures/` path used by the manuscript.
- Each modified figure has a neighboring `.raw.json` file documenting source code, source data, and modification scope.
- LaTeX compilation succeeds, and the `latex` skill layout check reports no `question_mark_in_pdf`, `underfilled_page`, `margin_overflow_risk`, or figure/table layout errors.
- For legacy figures, compare the old and new versions and confirm that panel structure, plotted data, and visual logic are preserved; only requested text or explicitly requested style details should change.
