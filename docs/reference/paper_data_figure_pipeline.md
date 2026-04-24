# Paper Data And Figure Pipeline

## Scope

This document records the stable workflow for `docs/paper/`. The goal is to keep manuscript tables, figures, value macros, and bibliography tied to one reproducible data snapshot instead of letting `main.tex` read scattered project outputs directly.

## Directory Roles

`docs/paper/` uses these responsibilities:

- `docs/paper/config.json`: canonical paper data-source configuration for project metrics, ex_project outputs, legacy image migrations, and legacy plotting-code provenance.
- `docs/paper/gen_data.py`: top-level data entry; refreshes the frozen paper data snapshot and `latex/values.tex`.
- `docs/paper/gen_figures.py`: top-level figure entry; refreshes generated figures and migrated legacy figures.
- `docs/paper/src/`: implementation code for data collection, derived metrics, plotting, and migration helpers.
- `docs/paper/src/legacy/`: migrated legacy plotting code kept for provenance and future extraction; new execution should still enter through `gen_data.py` or `gen_figures.py`.
- `docs/paper/data/results.json`: frozen paper data snapshot used by generated figures and tables.
- `docs/paper/data/values_raw.json`: machine-readable source record for values written into `latex/values.tex`.
- `docs/paper/figures/`: figure files referenced by LaTeX; every referenced file must have a same-stem `.raw.json`.
- `docs/paper/image/`: migrated original image assets from the legacy paper workspace.
- `docs/paper/latex/`: manuscript, template, bibliography, and build outputs.

## Authoritative Data Flow

The stable flow is:

1. `docs/paper/config.json` declares external project paths, ex_project paths, legacy image mappings, and legacy plotting-code provenance.
2. `python docs/paper/gen_data.py` reads those sources and writes `docs/paper/data/results.json` as a frozen snapshot.
3. The same data entry refreshes `docs/paper/latex/values.tex`; manuscript text should cite numeric values through `\val...` macros.
4. `python docs/paper/gen_figures.py` uses `results.json`, migrated images, and code under `docs/paper/src/` to write `docs/paper/figures/`.
5. `docs/paper/latex/main.tex` references only repository-local `values.tex`, `figures/`, and `latex/nonlinear.bib` resources.

A valid paper data flow satisfies these checks:

- Every `\val...` macro used by `main.tex` is defined in `values.tex`.
- Every figure under `docs/paper/figures/` referenced by `main.tex` has a same-stem `.raw.json`.
- `results.json` records the project or ex_project source for generated metric tables and plots.
- Legacy images are copied into this repository before LaTeX references them.

## Figure Reproduction Rules

When adding or replacing paper figures:

- Add reusable plotting logic under `docs/paper/src/` and call it through `gen_figures.py`.
- Do not put absolute paths or legacy workspace paths in `main.tex`.
- Do not reuse one figure file for two different figure semantics; generate distinct files and distinct raw records.
- Legacy manually composed figures may be kept, but their `.raw.json` must record the migrated source path.
- Tables, figure labels, and text values must come from the same `results.json` snapshot or from an explicit migrated raw record.

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

After migration, the current repository is authoritative. Future edits should update `docs/paper/config.json` and code under `docs/paper/src/`, then run the top-level generation entries.

## Validation Order

After updating paper data, figures, bibliography, or LaTeX references, use this order:

1. `python docs/paper/gen_data.py`
2. `python docs/paper/gen_figures.py`
3. Check that all `main.tex` figure paths exist and have same-stem `.raw.json` files.
4. Check that all `\val...` macros used by `main.tex` exist in `values.tex` and no used value is `TBD`.
5. If bibliography changed, run `xelatex -> bibtex -> xelatex -> xelatex` in `docs/paper/latex`.
6. Run the LaTeX skill build for `docs/paper/latex/main.tex` as the final reproducible build check.

## Acceptance Criteria

A paper pipeline change is complete when:

- `gen_data.py` and `gen_figures.py` finish successfully.
- `results.json`, `values.tex`, generated figures, migrated figures, and `.raw.json` files are internally consistent.
- `main.tex` has no absolute image or bibliography paths.
- The final LaTeX build produces `docs/paper/latex/build/main.pdf` with return code `0`.
