from __future__ import annotations

import argparse
import copy
import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PAPER_DIR = ROOT / 'docs' / 'paper'
PAPER_FIGURES_DIR = PAPER_DIR / 'figures'
PAPER_FIGURES_LEGACY_DIR = PAPER_FIGURES_DIR / 'legacy'
PLOT_ROOT = ROOT / 'ex_projects' / 'plot'

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.visualization.subfigure_montage import PanelSpec, compose_subfigures  # noqa: E402
from src.visualization.paper_plot_style import (  # noqa: E402
    paper_plot_style_payload,
    raw_uses_current_paper_plot_style,
)


@dataclass
class PlotProject:
    figure_id: str
    kind: str
    project_path: Path
    config_path: Path
    output_name: str
    title: str
    description: str
    config: Dict[str, Any]

    @property
    def data_dir(self) -> Path:
        return self.project_path / 'data'

    @property
    def output_path(self) -> Path:
        return self.data_dir / self.output_name


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.name.endswith('.raw.json') and 'paper_plot_style' not in payload:
        payload = {**payload, **paper_plot_style_payload()}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def rel_to_root(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve())).replace('\\', '/')
    except ValueError:
        return str(path).replace('\\', '/')


def resolve_repo_path(value: str | Path, *, base_dir: Optional[Path] = None) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    base = base_dir or ROOT
    return (base / path).resolve()


def _kind_from_config(config_path: Path, paper: Dict[str, Any], payload: Dict[str, Any]) -> str:
    task_info = payload.get('task_info') if isinstance(payload.get('task_info'), dict) else {}
    task_type = str(task_info.get('task_type') or '')
    configured_kind = str(paper.get('kind') or '')
    if configured_kind in {'multi', 'montage'} or task_type == 'paper-figure-multi':
        return 'montage'
    if configured_kind == 'single' or task_type == 'paper-figure-single':
        return 'single'
    try:
        parts = config_path.parent.relative_to(PLOT_ROOT).parts
    except ValueError:
        parts = config_path.parent.parts
    return 'montage' if 'multi' in parts else 'single'


def scan_plot_projects(root: Path = ROOT) -> Dict[str, PlotProject]:
    plot_root = root / 'ex_projects' / 'plot'
    projects: Dict[str, PlotProject] = {}
    if not plot_root.exists():
        return projects
    for config_path in sorted(plot_root.rglob('config.json')):
        if 'data' in config_path.relative_to(plot_root).parts:
            continue
        payload = read_json(config_path)
        paper = payload.get('paper_figure') or {}
        if not isinstance(paper, dict):
            continue
        figure_id = str(paper.get('figure_id') or config_path.parent.name)
        kind = _kind_from_config(config_path, paper, payload)
        output_name = str(paper.get('output_name') or f'{figure_id}.png')
        projects[figure_id] = PlotProject(
            figure_id=figure_id,
            kind='montage' if kind in {'multi', 'montage'} else 'single',
            project_path=config_path.parent,
            config_path=config_path,
            output_name=output_name,
            title=str(paper.get('title') or figure_id),
            description=str(paper.get('description') or ''),
            config=payload,
        )
    return projects


def project_from_path(project_path: str | Path) -> PlotProject:
    full_path = resolve_repo_path(project_path)
    config_path = full_path / 'config.json'
    if not config_path.exists():
        raise FileNotFoundError(f'Missing plot ex_project config: {config_path}')
    payload = read_json(config_path)
    paper = payload.get('paper_figure') or {}
    if not isinstance(paper, dict):
        raise ValueError(f'Plot ex_project config has no paper_figure object: {config_path}')
    figure_id = str(paper.get('figure_id') or full_path.name)
    kind = _kind_from_config(config_path, paper, payload)
    return PlotProject(
        figure_id=figure_id,
        kind='montage' if kind in {'multi', 'montage'} else 'single',
        project_path=full_path,
        config_path=config_path,
        output_name=str(paper.get('output_name') or f'{figure_id}.png'),
        title=str(paper.get('title') or figure_id),
        description=str(paper.get('description') or ''),
        config=payload,
    )


def _as_spacing(value: Any, default: Any) -> Any:
    return value if value is not None else default


def _merge_panel_specs(base_specs: List[Dict[str, Any]], overrides: Any) -> List[Dict[str, Any]]:
    override_rows = overrides if isinstance(overrides, list) else []
    merged: List[Dict[str, Any]] = []
    for index, spec in enumerate(base_specs):
        row = copy.deepcopy(spec)
        if index < len(override_rows) and isinstance(override_rows[index], dict):
            row.update(copy.deepcopy(override_rows[index]))
        merged.append(row)
    return merged


def _panel_from_spec(spec: Dict[str, Any]) -> PanelSpec:
    return PanelSpec(
        path=resolve_repo_path(str(spec['source'])),
        label=spec.get('label'),
        scale=float(spec.get('scale', 1.0)),
        fit_width=spec.get('fit_width'),
        fit_height=spec.get('fit_height'),
        fit_mode=str(spec.get('fit_mode') or 'both'),
        align_x=str(spec.get('align_x') or 'center'),
        align_y=str(spec.get('align_y') or 'center'),
        offset_x=int(spec.get('offset_x', 0)),
        offset_y=int(spec.get('offset_y', 0)),
        row_span=int(spec.get('row_span', 1)),
        col_span=int(spec.get('col_span', 1)),
        trim_border=spec.get('trim_border'),
        trim_tolerance=int(spec.get('trim_tolerance', 8)),
        margin_left=int(spec.get('margin_left', 0)),
        margin_right=int(spec.get('margin_right', 0)),
        margin_top=int(spec.get('margin_top', 0)),
        margin_bottom=int(spec.get('margin_bottom', 0)),
    )


def _compose(output_path: Path, panel_specs: List[Dict[str, Any]], figure_config: Dict[str, Any], note: str) -> None:
    montage_cfg = figure_config.get('montage') if isinstance(figure_config.get('montage'), dict) else {}
    merged_specs = _merge_panel_specs(panel_specs, figure_config.get('panels'))
    panels = [_panel_from_spec(spec) for spec in merged_specs]
    metadata = compose_subfigures(
        panels,
        output_path,
        layout=str(montage_cfg.get('layout', 'matrix')),
        rows=int(montage_cfg['rows']) if montage_cfg.get('rows') is not None else None,
        cols=int(montage_cfg['cols']) if montage_cfg.get('cols') is not None else None,
        padding=_as_spacing(montage_cfg.get('padding'), 0),
        gutter=_as_spacing(montage_cfg.get('gutter'), 0),
        cell_widths=montage_cfg.get('cell_widths'),
        cell_heights=montage_cfg.get('cell_heights'),
        label_font_size=int(montage_cfg.get('label_font_size', 54)),
        label_font_size_pt=float(montage_cfg.get('label_font_size_pt', 8.0)),
        latex_width_fraction=float(montage_cfg.get('latex_width_fraction', 1.0)),
        label_position=str(montage_cfg.get('label_position', 'outside-top-left')),
        label_inset=int(montage_cfg.get('label_inset', 24)),
        label_gap=int(montage_cfg.get('label_gap', 24)),
        label_box=bool(montage_cfg.get('label_box', False)),
        dpi=(500, 500),
    )
    write_json(output_path.with_suffix('.raw.json'), {
        'source_trace': 'ex_projects/plot paper figure workflow',
        'source_figures': [str(spec['source']).replace('\\', '/') for spec in merged_specs],
        'modification_scope': note,
        **paper_plot_style_payload(),
        'montage': metadata,
    })


def _copy_raw_if_exists(source: Path, target: Path) -> None:
    raw = source.with_suffix('.raw.json')
    if raw.exists():
        shutil.copy2(raw, target.with_suffix('.raw.json'))


def _json_equivalent(left: Any, right: Any) -> bool:
    return json.dumps(left, ensure_ascii=True, sort_keys=True, separators=(',', ':')) == json.dumps(
        right,
        ensure_ascii=True,
        sort_keys=True,
        separators=(',', ':'),
    )


def _copy_transformed_panel(source: Path, target: Path, transform: Dict[str, Any]) -> None:
    panel = {
        'source': rel_to_root(source),
        'fit_width': transform.get('fit_width'),
        'fit_height': transform.get('fit_height'),
        'scale': transform.get('scale', 1.0),
        'trim_border': transform.get('trim_border'),
        'trim_tolerance': transform.get('trim_tolerance', 8),
    }
    metadata = compose_subfigures(
        [_panel_from_spec(panel)],
        target,
        layout='horizontal',
        padding=0,
        gutter=0,
        label_font_size=1,
        label_box=False,
        dpi=(500, 500),
    )
    write_json(target.with_suffix('.raw.json'), {
        'source_trace': 'ex_projects/plot legacy panel transform',
        'source_panel': rel_to_root(source),
        'transform': transform,
        **paper_plot_style_payload(),
        'montage': metadata,
    })


def _run_legacy(project: PlotProject, paper: Dict[str, Any], figure_config: Dict[str, Any]) -> None:
    if str(PAPER_DIR) not in sys.path:
        sys.path.insert(0, str(PAPER_DIR))
    from src import paper_pipeline  # type: ignore

    legacy_id = str(paper.get('legacy_render_id') or project.figure_id)
    project.data_dir.mkdir(parents=True, exist_ok=True)
    stage_dir = PAPER_FIGURES_LEGACY_DIR / '_generated_stage' / project.figure_id
    if stage_dir.exists():
        shutil.rmtree(stage_dir)
    stage_dir.mkdir(parents=True, exist_ok=True)
    original_figures_dir = paper_pipeline.FIGURES_DIR
    paper_pipeline.FIGURES_DIR = stage_dir
    try:
        generated = paper_pipeline.generate_selected_figures_legacy(
            [legacy_id],
            figure_config_overrides={legacy_id: figure_config},
        )
    finally:
        paper_pipeline.FIGURES_DIR = original_figures_dir
    output_name = str(generated.get(legacy_id) or project.output_name)
    generated_path = stage_dir / output_name
    if not generated_path.exists():
        raise FileNotFoundError(f'Legacy renderer did not create {generated_path}')
    shutil.copy2(generated_path, project.output_path)
    _copy_raw_if_exists(generated_path, project.output_path)


def _run_legacy_panel(project: PlotProject, paper: Dict[str, Any], figure_config: Dict[str, Any]) -> None:
    if str(PAPER_DIR) not in sys.path:
        sys.path.insert(0, str(PAPER_DIR))
    from src import paper_pipeline  # type: ignore

    legacy_id = str(paper.get('legacy_render_id') or paper.get('legacy_parent_id') or '')
    panel_output_name = str(paper.get('panel_output_name') or project.output_name)
    if not legacy_id:
        raise ValueError(f'legacy_panel requires paper_figure.legacy_render_id: {project.figure_id}')

    project.data_dir.mkdir(parents=True, exist_ok=True)
    default_source = paper.get('default_source_path')
    default_config = paper.get('default_figure_config')
    if isinstance(default_config, dict) and default_source and _json_equivalent(figure_config, default_config):
        source_path = resolve_repo_path(str(default_source), base_dir=project.project_path)
        if not source_path.exists() and not Path(str(default_source)).is_absolute():
            source_path = resolve_repo_path(str(default_source))
        if not source_path.exists():
            raise FileNotFoundError(f'Missing default panel bitmap: {source_path}')
        if raw_uses_current_paper_plot_style(source_path.with_suffix('.raw.json')):
            shutil.copy2(source_path, project.output_path)
            _copy_raw_if_exists(source_path, project.output_path)
            return

    stage_dir = PAPER_FIGURES_LEGACY_DIR / '_generated_stage' / project.figure_id
    if stage_dir.exists():
        shutil.rmtree(stage_dir)
    stage_dir.mkdir(parents=True, exist_ok=True)
    if legacy_id == 'fig_08_frequency_response_comparison':
        shutil.copy2(PAPER_FIGURES_LEGACY_DIR / 'time_domain_outputs.png', stage_dir / 'time_domain_outputs.png')

    original_figures_dir = paper_pipeline.FIGURES_DIR
    paper_pipeline.FIGURES_DIR = stage_dir
    try:
        paper_pipeline.generate_selected_figures_legacy(
            [legacy_id],
            figure_config_overrides={legacy_id: figure_config},
        )
    finally:
        paper_pipeline.FIGURES_DIR = original_figures_dir

    generated_path = stage_dir / '_montage_panels' / panel_output_name
    if not generated_path.exists():
        generated_path = stage_dir / panel_output_name
    if not generated_path.exists():
        raise FileNotFoundError(f'Legacy panel renderer did not create {stage_dir / "_montage_panels" / panel_output_name}')
    transform = paper.get('panel_transform') if isinstance(paper.get('panel_transform'), dict) else {}
    if transform:
        _copy_transformed_panel(generated_path, project.output_path, transform)
    else:
        shutil.copy2(generated_path, project.output_path)
        _copy_raw_if_exists(generated_path, project.output_path)


def _run_legacy_translate(project: PlotProject, paper: Dict[str, Any], figure_config: Dict[str, Any]) -> None:
    if str(PAPER_DIR) not in sys.path:
        sys.path.insert(0, str(PAPER_DIR))
    from src import translate_legacy_figures  # type: ignore

    function_name = str(paper.get('legacy_function') or '')
    if not function_name:
        raise ValueError(f'legacy_translate requires paper_figure.legacy_function: {project.figure_id}')
    renderer = getattr(translate_legacy_figures, function_name, None)
    if renderer is None:
        raise AttributeError(f'Legacy translate renderer not found: {function_name}')

    project.data_dir.mkdir(parents=True, exist_ok=True)
    default_source = paper.get('default_source_path')
    default_config = paper.get('default_figure_config')
    if isinstance(default_config, dict) and default_source and _json_equivalent(figure_config, default_config):
        source_path = resolve_repo_path(str(default_source), base_dir=project.project_path)
        if not source_path.exists() and not Path(str(default_source)).is_absolute():
            source_path = resolve_repo_path(str(default_source))
        if not source_path.exists():
            raise FileNotFoundError(f'Missing default translated bitmap: {source_path}')
        if raw_uses_current_paper_plot_style(source_path.with_suffix('.raw.json')):
            shutil.copy2(source_path, project.output_path)
            _copy_raw_if_exists(source_path, project.output_path)
            return

    stage_dir = PAPER_FIGURES_LEGACY_DIR / '_generated_stage' / project.figure_id
    if stage_dir.exists():
        shutil.rmtree(stage_dir)
    stage_dir.mkdir(parents=True, exist_ok=True)

    original_figures_dir = translate_legacy_figures.FIGURES_DIR
    original_tmp_dir = translate_legacy_figures.TMP_DIR
    original_predict_cfg = getattr(translate_legacy_figures, 'PLOT_PREDICT_CONFIG', {})
    translate_legacy_figures.FIGURES_DIR = stage_dir
    translate_legacy_figures.TMP_DIR = stage_dir / '_traced_tmp'
    translate_legacy_figures.PLOT_PREDICT_CONFIG = copy.deepcopy(figure_config)
    try:
        renderer()
    finally:
        translate_legacy_figures.FIGURES_DIR = original_figures_dir
        translate_legacy_figures.TMP_DIR = original_tmp_dir
        translate_legacy_figures.PLOT_PREDICT_CONFIG = original_predict_cfg

    generated_path = stage_dir / str(paper.get('translated_output_name') or project.output_name)
    if not generated_path.exists():
        raise FileNotFoundError(f'Legacy translate renderer did not create {generated_path}')
    shutil.copy2(generated_path, project.output_path)
    _copy_raw_if_exists(generated_path, project.output_path)


def _run_copy_source(project: PlotProject, paper: Dict[str, Any]) -> None:
    source_path = resolve_repo_path(str(paper['source_path']))
    if not source_path.exists():
        raise FileNotFoundError(f'Missing source bitmap: {source_path}')
    project.data_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, project.output_path)
    _copy_raw_if_exists(source_path, project.output_path)


def _run_bitmap_compose(project: PlotProject, paper: Dict[str, Any], figure_config: Dict[str, Any]) -> None:
    source_path = resolve_repo_path(str(paper['source_path']))
    project.data_dir.mkdir(parents=True, exist_ok=True)
    panel = {
        'source': rel_to_root(source_path),
        'label': paper.get('label'),
    }
    _compose(
        project.output_path,
        [panel],
        figure_config,
        f'Single bitmap composed inside {rel_to_root(project.project_path)}.',
    )


def _existing_output_is_current(project: PlotProject) -> bool:
    if not project.output_path.exists():
        return False
    output_mtime = project.output_path.stat().st_mtime
    if project.config_path.exists() and project.config_path.stat().st_mtime > output_mtime:
        return False

    paper = project.config.get('paper_figure') if isinstance(project.config.get('paper_figure'), dict) else {}
    for key in ('source_path', 'default_source_path'):
        source_value = paper.get(key)
        if not source_value:
            continue
        source_path = resolve_repo_path(str(source_value), base_dir=project.project_path)
        if not source_path.exists() and not Path(str(source_value)).is_absolute():
            source_path = resolve_repo_path(str(source_value))
        if source_path.exists() and source_path.stat().st_mtime > output_mtime:
            return False
    return True


def _should_render_child(child: PlotProject, policy: str) -> bool:
    normalized = policy.lower().replace('-', '_')
    if normalized in {'always', 'refresh', 'rerender', 'render'}:
        return True
    if normalized in {'never', 'compose_only', 'existing'}:
        if not child.output_path.exists():
            raise FileNotFoundError(f'Missing child bitmap for compose-only montage: {child.output_path}')
        return False
    if normalized in {'missing', 'missing_only'}:
        return not child.output_path.exists()
    if normalized in {'missing_or_stale', 'stale', 'auto'}:
        return not _existing_output_is_current(child)
    raise ValueError(f'Unsupported child_render_policy={policy!r}')


def _montage_output_is_current(project: PlotProject, child_projects: Sequence[PlotProject]) -> bool:
    if not project.output_path.exists():
        return False
    output_mtime = project.output_path.stat().st_mtime
    if project.config_path.exists() and project.config_path.stat().st_mtime > output_mtime:
        return False
    for child in child_projects:
        if not child.output_path.exists() or child.output_path.stat().st_mtime > output_mtime:
            return False
    return True


def _run_multi(project: PlotProject, paper: Dict[str, Any], figure_config: Dict[str, Any], *, sync_paper: bool, strict_regression: bool) -> None:
    subfigures = paper.get('subfigures') if isinstance(paper.get('subfigures'), list) else []
    child_render_policy = str(paper.get('child_render_policy') or figure_config.get('child_render_policy') or 'missing')
    panel_specs: List[Dict[str, Any]] = []
    child_projects: List[PlotProject] = []
    for subfigure in subfigures:
        if not isinstance(subfigure, dict):
            continue
        child_path = resolve_repo_path(str(subfigure['project_path']))
        child = project_from_path(child_path)
        # A montage render needs child bitmaps in the child ex_project data dirs.
        # Do not sync child panels into docs/paper/figures as a side effect of
        # rendering the parent paper figure. Existing current child outputs are
        # reused so parent-only layout changes stay a bitmap compose operation.
        if _should_render_child(child, child_render_policy):
            run_project(child, sync_paper=False, strict_regression=False)
        child_projects.append(child)
        spec = {
            'source': rel_to_root(child.output_path),
            'label': subfigure.get('label'),
        }
        for key, value in subfigure.items():
            if key not in {'project_path', 'label'}:
                spec[key] = value
        panel_specs.append(spec)
    if not panel_specs:
        raise ValueError(f'Multi figure has no subfigures: {project.figure_id}')
    project.data_dir.mkdir(parents=True, exist_ok=True)
    if _montage_output_is_current(project, child_projects):
        return
    _compose(project.output_path, panel_specs, figure_config, f'Multi-panel figure composed inside {rel_to_root(project.project_path)}.')


def compare_pixels(output_path: Path, baseline_path: Path) -> Dict[str, Any]:
    if not output_path.exists() or not baseline_path.exists():
        return {
            'status': 'missing',
            'output': rel_to_root(output_path),
            'baseline': rel_to_root(baseline_path),
            'pixel_exact': False,
        }
    with Image.open(output_path) as output_image, Image.open(baseline_path) as baseline_image:
        output = np.asarray(output_image.convert('RGBA'), dtype=np.int16)
        baseline = np.asarray(baseline_image.convert('RGBA'), dtype=np.int16)
    if output.shape != baseline.shape:
        return {
            'status': 'shape_mismatch',
            'output': rel_to_root(output_path),
            'baseline': rel_to_root(baseline_path),
            'output_shape': list(output.shape),
            'baseline_shape': list(baseline.shape),
            'pixel_exact': False,
        }
    diff = np.abs(output - baseline)
    mismatch_pixels = np.any(diff != 0, axis=2)
    mismatch_count = int(np.count_nonzero(mismatch_pixels))
    total_pixels = int(mismatch_pixels.size)
    return {
        'status': 'pass' if mismatch_count == 0 else 'diff',
        'output': rel_to_root(output_path),
        'baseline': rel_to_root(baseline_path),
        'shape': list(output.shape),
        'pixel_exact': mismatch_count == 0,
        'mismatch_pixels': mismatch_count,
        'total_pixels': total_pixels,
        'mismatch_ratio': mismatch_count / total_pixels if total_pixels else 0.0,
        'max_abs_channel_diff': int(diff.max()) if diff.size else 0,
    }


def _run_regression(project: PlotProject, paper: Dict[str, Any], *, strict: bool) -> Dict[str, Any]:
    regression = paper.get('regression') if isinstance(paper.get('regression'), dict) else {}
    baseline = regression.get('baseline_path') or f'docs/paper/figures/legacy/{project.output_name}'
    report = compare_pixels(project.output_path, resolve_repo_path(str(baseline)))
    write_json(project.data_dir / 'pixel_regression.json', report)
    if strict and not report.get('pixel_exact'):
        raise AssertionError(f'Pixel regression failed for {project.figure_id}: {report}')
    return report


def _sync_to_paper(project: PlotProject) -> None:
    paper_target = PAPER_FIGURES_DIR / project.output_name
    paper_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(project.output_path, paper_target)
    _copy_raw_if_exists(project.output_path, paper_target)


def run_project(project: PlotProject, *, sync_paper: bool = False, strict_regression: bool = False) -> Dict[str, Any]:
    paper = project.config.get('paper_figure') or {}
    figure_config = paper.get('figure_config') if isinstance(paper.get('figure_config'), dict) else {}
    mode = str(paper.get('generation_mode') or ('multi' if project.kind == 'montage' else 'copy_source'))
    before_mtime_ns = project.output_path.stat().st_mtime_ns if project.output_path.exists() else None

    if project.kind == 'montage' or mode == 'multi':
        _run_multi(project, paper, figure_config, sync_paper=sync_paper, strict_regression=strict_regression)
    elif mode == 'legacy':
        _run_legacy(project, paper, figure_config)
    elif mode == 'legacy_panel':
        _run_legacy_panel(project, paper, figure_config)
    elif mode == 'legacy_translate':
        _run_legacy_translate(project, paper, figure_config)
    elif mode == 'bitmap_compose':
        _run_bitmap_compose(project, paper, figure_config)
    elif mode == 'copy_source':
        _run_copy_source(project, paper)
    else:
        raise ValueError(f'Unsupported paper figure generation_mode={mode!r} for {project.figure_id}')

    regression = _run_regression(project, paper, strict=strict_regression)
    after_mtime_ns = project.output_path.stat().st_mtime_ns if project.output_path.exists() else None
    if sync_paper:
        _sync_to_paper(project)
    return {
        'figure_id': project.figure_id,
        'project_path': rel_to_root(project.project_path),
        'output': rel_to_root(project.output_path),
        'render_status': 'reused' if before_mtime_ns is not None and before_mtime_ns == after_mtime_ns else 'updated',
        'regression': regression,
    }


def run_project_by_figure_id(figure_id: str, *, sync_paper: bool = False, strict_regression: bool = False) -> Dict[str, Any]:
    projects = scan_plot_projects(ROOT)
    project = projects.get(figure_id)
    if not project:
        raise KeyError(f'Plot ex_project not found for figure id: {figure_id}')
    return run_project(project, sync_paper=sync_paper, strict_regression=strict_regression)


def run_projects_by_figure_id(figure_ids: Iterable[str], *, sync_paper: bool = False, strict_regression: bool = False) -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    projects = scan_plot_projects(ROOT)
    for figure_id in figure_ids:
        project = projects.get(figure_id)
        if not project:
            raise KeyError(f'Plot ex_project not found for figure id: {figure_id}')
        results[figure_id] = run_project(project, sync_paper=sync_paper, strict_regression=strict_regression)
    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Run ex_projects/plot paper figure workflows.')
    sub = parser.add_subparsers(dest='command')

    run = sub.add_parser('run', help='Run one plot ex_project by path.')
    run.add_argument('--project', required=True)
    run.add_argument('--sync-paper', action='store_true')
    run.add_argument('--strict-regression', action='store_true')

    by_id = sub.add_parser('run-id', help='Run one plot ex_project by figure id.')
    by_id.add_argument('--figure-id', required=True)
    by_id.add_argument('--sync-paper', action='store_true')
    by_id.add_argument('--strict-regression', action='store_true')

    many = sub.add_parser('run-ids', help='Run multiple plot ex_projects by figure id.')
    many.add_argument('--figure-id', action='append', required=True)
    many.add_argument('--sync-paper', action='store_true')
    many.add_argument('--strict-regression', action='store_true')

    sub.add_parser('list', help='List discovered plot ex_projects.')
    return parser


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == 'list':
        for figure_id, project in scan_plot_projects(ROOT).items():
            print(f'{figure_id}\t{rel_to_root(project.project_path)}\t{project.output_name}')
        return
    if args.command == 'run':
        result = run_project(project_from_path(args.project), sync_paper=args.sync_paper, strict_regression=args.strict_regression)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    if args.command == 'run-id':
        result = run_project_by_figure_id(args.figure_id, sync_paper=args.sync_paper, strict_regression=args.strict_regression)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    if args.command == 'run-ids':
        result = run_projects_by_figure_id(args.figure_id, sync_paper=args.sync_paper, strict_regression=args.strict_regression)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    parser.print_help()
    raise SystemExit(1)


if __name__ == '__main__':
    main()
