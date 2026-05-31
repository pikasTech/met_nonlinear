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

    tex_for_command = _relative_or_absolute(tex_path, workdir)
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