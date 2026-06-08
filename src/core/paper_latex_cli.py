from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path


DEFAULT_PAPER_LATEX_WORKDIR = Path('docs/paper/latex')
DEFAULT_PAPER_LATEX_TEX = 'main.tex'
DEFAULT_PAPER_LATEX_OUTPUT_DIR = 'build'
DEFAULT_PAPER_LATEX_ENGINE = 'xelatex'
DEFAULT_PAPER_LATEX_PASSES = 3
DEFAULT_REVIEW_HIGHLIGHT_SPEC = 'review_highlight_specs/final-only-marker-highlight.json'
DEFAULT_REVIEW_HIGHLIGHT_OUTPUT = 'build/review-highlight/main.final-only-marker-highlight.tex'
DEFAULT_REVIEW_HIGHLIGHT_COLOR = 'yellow!45'
DEFAULT_REVIEW_HIGHLIGHT_MACRO = 'Change'


def _resolve_repo_path(repo_root: Path, raw_path: str | None, *, base_dir: Path | None = None) -> Path | None:
    if raw_path is None:
        return None

    path = Path(raw_path)
    if path.is_absolute():
        return path.resolve()
    if base_dir is not None:
        return (base_dir / path).resolve()
    return (repo_root / path).resolve()


def _relative_or_absolute(path: Path, workdir: Path) -> str:
    try:
        return os.path.relpath(path, workdir)
    except ValueError:
        return str(path)


def _resolve_executable(name: str) -> str:
    candidate_path = Path(name)
    if candidate_path.is_absolute():
        if candidate_path.exists():
            return str(candidate_path)
        raise FileNotFoundError(f'executable not found: {candidate_path}')

    resolved = shutil.which(name)
    if resolved:
        return resolved

    fallback = Path(r'D:/texlive/2024/bin/windows') / f'{name}.EXE'
    if fallback.exists():
        return str(fallback)

    raise FileNotFoundError(f'{name} executable not found in PATH or TeX Live fallback')


def _read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def _insert_review_highlight_macro(source: str, *, color: str, macro_name: str) -> str:
    macro_command = f'\\DeclareRobustCommand{{\\{macro_name}}}'
    if macro_command in source:
        return source

    preamble = (
        '\\usepackage{xcolor}\n'
        '\\usepackage{soul}\n'
        f'\\sethlcolor{{{color}}}\n'
        f'\\DeclareRobustCommand{{\\{macro_name}}}[1]{{\\begingroup\\sethlcolor{{{color}}}\\hl{{#1}}\\endgroup}}\n'
    )

    insertion_anchor = '\\usepackage{silence}\n'
    if insertion_anchor in source:
        return source.replace(insertion_anchor, insertion_anchor + preamble, 1)

    document_anchor = '\\begin{document}'
    if document_anchor in source:
        return source.replace(document_anchor, preamble + '\n' + document_anchor, 1)

    raise ValueError('could not find a safe preamble insertion point for review highlight macros')


def _load_review_highlight_spec(spec_path: Path) -> dict:
    if not spec_path.exists():
        raise FileNotFoundError(f'review highlight spec not found: {spec_path}')
    with spec_path.open('r', encoding='utf-8') as handle:
        spec = json.load(handle)
    replacements = spec.get('replacements')
    if not isinstance(replacements, list) or not replacements:
        raise ValueError('review highlight spec must contain a non-empty replacements list')
    for index, replacement in enumerate(replacements, start=1):
        if not isinstance(replacement, dict):
            raise ValueError(f'review highlight replacement #{index} must be an object')
        if not isinstance(replacement.get('target'), str) or not isinstance(replacement.get('replacement'), str):
            raise ValueError(f'review highlight replacement #{index} must contain string target and replacement')
    return spec


def _apply_review_highlight_replacements(source: str, replacements: list[dict]) -> tuple[str, list[dict]]:
    applied: list[dict] = []
    highlighted = source
    for index, replacement in enumerate(replacements, start=1):
        target = replacement['target']
        new_text = replacement['replacement']
        expected_count = int(replacement.get('count', 1))
        actual_count = highlighted.count(target)
        if actual_count != expected_count:
            raise ValueError(
                f'review highlight replacement #{index} expected {expected_count} target match(es), '
                f'found {actual_count}'
            )
        highlighted = highlighted.replace(target, new_text, expected_count)
        applied.append({
            'index': index,
            'targetPreview': target[:120],
            'replacementPreview': new_text[:120],
            'count': expected_count,
        })
    return highlighted, applied


def _slice_after_marker(text: str, markers: list[str]) -> tuple[int, str | None]:
    positions = [(text.find(marker), marker) for marker in markers]
    positions = [(position, marker) for position, marker in positions if position >= 0]
    if not positions:
        return -1, None
    return min(positions, key=lambda item: item[0])


def _validate_review_highlight_source(source: str, *, macro_name: str) -> list[dict]:
    errors: list[dict] = []
    forbidden_tokens = ['DIFadd', 'DIFdel', '\\color{blue}']
    for token in forbidden_tokens:
        if token in source:
            errors.append({'code': 'forbidden_diff_markup', 'token': token})

    if '\\usepackage{soul}' not in source or '\\hl{#1}' not in source:
        errors.append({'code': 'missing_marker_highlight_macro'})

    change_token = f'\\{macro_name}{{'

    si_start, _ = _slice_after_marker(source, ['Supplementary Information'])
    if si_start >= 0:
        si_end_candidates = [
            source.find('\\section*{Funding}', si_start),
            source.find(f'\\section*{{\\{macro_name}{{Funding}}}}', si_start),
            source.find('\\bibliography', si_start),
            source.find('\\begin{thebibliography}', si_start),
        ]
        si_end_candidates = [position for position in si_end_candidates if position >= 0]
        si_end = min(si_end_candidates) if si_end_candidates else len(source)
        if change_token in source[si_start:si_end]:
            errors.append({'code': 'supplementary_information_highlighted'})

    ref_start, _ = _slice_after_marker(source, ['\\bibliography', '\\begin{thebibliography}', '\\section*{References}'])
    if ref_start >= 0 and change_token in source[ref_start:]:
        errors.append({'code': 'references_highlighted'})

    return errors


def build_review_highlight_plan(args, repo_root: str) -> dict:
    repo_root_path = Path(repo_root).resolve()
    workdir = _resolve_repo_path(repo_root_path, getattr(args, 'paper_latex_workdir', None), base_dir=repo_root_path)
    if workdir is None:
        workdir = (repo_root_path / DEFAULT_PAPER_LATEX_WORKDIR).resolve()
    if not workdir.exists():
        raise FileNotFoundError(f'paper-latex workdir not found: {workdir}')

    tex_path = _resolve_repo_path(repo_root_path, getattr(args, 'paper_latex_tex', None), base_dir=workdir)
    if tex_path is None:
        tex_path = (workdir / DEFAULT_PAPER_LATEX_TEX).resolve()
    if not tex_path.exists():
        raise FileNotFoundError(f'paper-latex tex file not found: {tex_path}')

    spec_path = _resolve_repo_path(
        repo_root_path,
        getattr(args, 'paper_latex_highlight_spec', None) or DEFAULT_REVIEW_HIGHLIGHT_SPEC,
        base_dir=workdir,
    )
    assert spec_path is not None
    spec = _load_review_highlight_spec(spec_path)

    output_from_args = getattr(args, 'paper_latex_highlight_output', None)
    output_from_spec = spec.get('output')
    output_raw = Path(output_from_args or output_from_spec or DEFAULT_REVIEW_HIGHLIGHT_OUTPUT)
    output_path = output_raw if output_raw.is_absolute() else (workdir / output_raw).resolve()

    color = getattr(args, 'paper_latex_highlight_color', None) or spec.get('highlightColor') or DEFAULT_REVIEW_HIGHLIGHT_COLOR
    macro_name = getattr(args, 'paper_latex_highlight_macro', None) or spec.get('macroName') or DEFAULT_REVIEW_HIGHLIGHT_MACRO

    source = _read_text(tex_path)
    highlighted = _insert_review_highlight_macro(source, color=color, macro_name=macro_name)
    highlighted, applied = _apply_review_highlight_replacements(highlighted, spec['replacements'])

    validation_errors = _validate_review_highlight_source(highlighted, macro_name=macro_name)
    if validation_errors:
        raise ValueError(f'review highlight validation failed: {validation_errors}')

    _write_text(output_path, highlighted)

    return {
        'workdir': str(workdir),
        'tex': str(tex_path),
        'spec': str(spec_path),
        'outputTex': str(output_path),
        'highlightColor': color,
        'macroName': macro_name,
        'replacementCount': len(applied),
        'appliedReplacements': applied,
        'validation': {
            'forbiddenLatexdiffMarkup': False,
            'nativeSoulHighlight': True,
            'supplementaryInformationHighlighted': False,
            'referencesHighlighted': False,
        },
    }


def build_paper_latex_plan(args, repo_root: str) -> dict:
    repo_root_path = Path(repo_root).resolve()
    workdir = _resolve_repo_path(repo_root_path, getattr(args, 'paper_latex_workdir', None), base_dir=repo_root_path)
    if workdir is None:
        workdir = (repo_root_path / DEFAULT_PAPER_LATEX_WORKDIR).resolve()
    if not workdir.exists():
        raise FileNotFoundError(f'paper-latex workdir not found: {workdir}')

    tex_path = _resolve_repo_path(repo_root_path, getattr(args, 'paper_latex_tex', None), base_dir=workdir)
    if tex_path is None:
        tex_path = (workdir / DEFAULT_PAPER_LATEX_TEX).resolve()
    if not tex_path.exists():
        raise FileNotFoundError(f'paper-latex tex file not found: {tex_path}')

    output_dir_raw = Path(getattr(args, 'paper_latex_output_dir', None) or DEFAULT_PAPER_LATEX_OUTPUT_DIR)
    output_dir = output_dir_raw if output_dir_raw.is_absolute() else (workdir / output_dir_raw).resolve()
    output_dir_for_command = str(output_dir_raw) if not output_dir_raw.is_absolute() else str(output_dir)

    engine_name = getattr(args, 'paper_latex_engine', None) or DEFAULT_PAPER_LATEX_ENGINE
    engine_executable = _resolve_executable(engine_name)

    passes = getattr(args, 'paper_latex_passes', None)
    if passes is None:
        passes = DEFAULT_PAPER_LATEX_PASSES
    if passes < 1:
        raise ValueError('paper-latex passes must be at least 1')

    run_bibtex = not getattr(args, 'paper_latex_no_bibtex', False)
    if run_bibtex and passes < 2:
        raise ValueError('paper-latex build with bibtex requires at least 2 LaTeX passes')

    tex_for_command = _relative_or_absolute(tex_path, workdir).replace('\\', '/')
    latex_command = [
        engine_executable,
        '-interaction=nonstopmode',
        '-file-line-error',
        f'-output-directory={output_dir_for_command}',
        tex_for_command,
    ]

    stages: list[dict] = []
    for latex_pass in range(1, passes + 1):
        stages.append({
            'name': f'latex-pass-{latex_pass}',
            'command': list(latex_command),
        })
        if latex_pass == 1 and run_bibtex:
            bibtex_executable = _resolve_executable('bibtex')
            bibtex_target = _relative_or_absolute(output_dir / tex_path.stem, workdir).replace('\\', '/')
            stages.append({
                'name': 'bibtex',
                'command': [bibtex_executable, bibtex_target],
            })

    return {
        'workdir': str(workdir),
        'tex': str(tex_path),
        'engine': engine_name,
        'passes': passes,
        'runBibtex': run_bibtex,
        'outputDir': str(output_dir),
        'outputPdf': str(output_dir / f'{tex_path.stem}.pdf'),
        'stages': stages,
    }


def run_paper_latex_subcommand(args, repo_root: str) -> int:
    if getattr(args, 'paper_latex_action', None) == 'review-highlight':
        try:
            plan = build_review_highlight_plan(args, repo_root)
        except Exception as exc:
            print(json.dumps({
                'status': 'error',
                'message': str(exc),
                'action': getattr(args, 'paper_latex_action', None),
            }, indent=2, ensure_ascii=False))
            return 1

        print(json.dumps({
            'status': 'ok',
            'tool': 'paper-latex',
            'action': args.paper_latex_action,
            **plan,
        }, indent=2, ensure_ascii=False), flush=True)
        return 0

    try:
        plan = build_paper_latex_plan(args, repo_root)
    except Exception as exc:
        print(json.dumps({
            'status': 'error',
            'message': str(exc),
            'action': getattr(args, 'paper_latex_action', None),
        }, indent=2, ensure_ascii=False))
        return 1

    print(json.dumps({
        'status': 'running',
        'tool': 'paper-latex',
        'action': args.paper_latex_action,
        'workdir': plan['workdir'],
        'tex': plan['tex'],
        'engine': plan['engine'],
        'passes': plan['passes'],
        'runBibtex': plan['runBibtex'],
        'outputDir': plan['outputDir'],
        'stages': plan['stages'],
        'streamedOutput': True,
    }, indent=2, ensure_ascii=False), flush=True)

    stage_returncodes: dict[str, int] = {}
    for stage in plan['stages']:
        completed = subprocess.run(
            stage['command'],
            cwd=plan['workdir'],
            text=True,
            encoding='utf-8',
            errors='replace',
        )
        stage_returncodes[stage['name']] = completed.returncode
        if completed.returncode != 0:
            print(json.dumps({
                'status': 'error',
                'tool': 'paper-latex',
                'action': args.paper_latex_action,
                'workdir': plan['workdir'],
                'tex': plan['tex'],
                'stage': stage['name'],
                'command': stage['command'],
                'stageReturncodes': stage_returncodes,
                'returncode': completed.returncode,
                'streamedOutput': True,
            }, indent=2, ensure_ascii=False), flush=True)
            return completed.returncode

    print(json.dumps({
        'status': 'ok',
        'tool': 'paper-latex',
        'action': args.paper_latex_action,
        'workdir': plan['workdir'],
        'tex': plan['tex'],
        'engine': plan['engine'],
        'passes': plan['passes'],
        'runBibtex': plan['runBibtex'],
        'outputDir': plan['outputDir'],
        'outputPdf': plan['outputPdf'],
        'stageReturncodes': stage_returncodes,
        'streamedOutput': True,
    }, indent=2, ensure_ascii=False), flush=True)
    return 0
