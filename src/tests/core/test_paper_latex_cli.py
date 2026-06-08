import sys
import json
from pathlib import Path
from types import SimpleNamespace


_SRC_DIR = Path(__file__).parent.parent.parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))


def test_build_paper_latex_plan_with_bibtex():
    from core.paper_latex_cli import build_paper_latex_plan

    args = SimpleNamespace(
        paper_latex_action='build',
        paper_latex_workdir='docs/paper/latex',
        paper_latex_tex='main.translated.tex',
        paper_latex_output_dir='build',
        paper_latex_engine='xelatex',
        paper_latex_passes=3,
        paper_latex_no_bibtex=False,
    )

    plan = build_paper_latex_plan(args, 'C:/work/met_nonlinear_master')

    assert plan['engine'] == 'xelatex'
    assert plan['runBibtex'] is True
    assert plan['passes'] == 3
    assert [stage['name'] for stage in plan['stages']] == [
        'latex-pass-1',
        'bibtex',
        'latex-pass-2',
        'latex-pass-3',
    ]
    assert plan['stages'][0]['command'][-1] == 'main.translated.tex'
    assert plan['stages'][1]['command'][-1].replace('\\', '/') == 'build/main.translated'


def test_run_paper_latex_subcommand_streams_output(monkeypatch, capsys):
    from core import paper_latex_cli

    args = SimpleNamespace(paper_latex_action='build')
    plan = {
        'workdir': 'C:/work/met_nonlinear_master/docs/paper/latex',
        'tex': 'C:/work/met_nonlinear_master/docs/paper/latex/main.translated.tex',
        'engine': 'xelatex',
        'passes': 3,
        'runBibtex': True,
        'outputDir': 'C:/work/met_nonlinear_master/docs/paper/latex/build',
        'outputPdf': 'C:/work/met_nonlinear_master/docs/paper/latex/build/main.translated.pdf',
        'stages': [
            {'name': 'latex-pass-1', 'command': ['xelatex', 'main.translated.tex']},
            {'name': 'bibtex', 'command': ['bibtex', 'build/main.translated']},
            {'name': 'latex-pass-2', 'command': ['xelatex', 'main.translated.tex']},
        ],
    }

    monkeypatch.setattr(paper_latex_cli, 'build_paper_latex_plan', lambda args, repo_root: plan)

    captured_calls = []

    def fake_run(command, **kwargs):
        captured_calls.append((command, kwargs))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(paper_latex_cli.subprocess, 'run', fake_run)

    returncode = paper_latex_cli.run_paper_latex_subcommand(args, 'C:/work/met_nonlinear_master')

    assert returncode == 0
    assert [call[0] for call in captured_calls] == [stage['command'] for stage in plan['stages']]
    assert all(call[1]['cwd'] == plan['workdir'] for call in captured_calls)
    assert all(call[1]['text'] is True for call in captured_calls)
    assert all(call[1]['encoding'] == 'utf-8' for call in captured_calls)
    assert all(call[1]['errors'] == 'replace' for call in captured_calls)
    assert all('capture_output' not in call[1] for call in captured_calls)

    output = capsys.readouterr().out
    assert '"status": "running"' in output
    assert '"status": "ok"' in output
    assert '"runBibtex": true' in output


def test_build_review_highlight_plan_writes_native_final_only_highlight(tmp_path):
    from core.paper_latex_cli import build_review_highlight_plan

    workdir = tmp_path / 'docs' / 'paper' / 'latex'
    spec_dir = workdir / 'review_highlight_specs'
    spec_dir.mkdir(parents=True)

    tex_source = (
        '\\documentclass{article}\n'
        '\\usepackage{silence}\n'
        '\\begin{document}\n'
        'This sentence changed.\n'
        '\\section*{Supplementary Information}\n'
        'Supplementary information accompanies the manuscript.\n'
        '\\section*{Funding}\n'
        'Funding text.\n'
        '\\bibliography{nonlinear}\n'
        '\\end{document}\n'
    )
    (workdir / 'main.translated.tex').write_text(tex_source, encoding='utf-8')

    spec = {
        'highlightColor': 'yellow!45',
        'macroName': 'Change',
        'output': 'build/review-highlight.tex',
        'replacements': [
            {
                'target': 'This sentence changed.',
                'replacement': '\\Change{This sentence changed.}',
                'count': 1,
            },
            {
                'target': 'Funding text.',
                'replacement': '\\Change{Funding text.}',
                'count': 1,
            },
        ],
    }
    (spec_dir / 'final-only-marker-highlight.json').write_text(json.dumps(spec), encoding='utf-8')

    args = SimpleNamespace(
        paper_latex_action='review-highlight',
        paper_latex_workdir='docs/paper/latex',
        paper_latex_tex='main.translated.tex',
        paper_latex_highlight_spec='review_highlight_specs/final-only-marker-highlight.json',
        paper_latex_highlight_output=None,
        paper_latex_highlight_color=None,
        paper_latex_highlight_macro=None,
    )

    plan = build_review_highlight_plan(args, str(tmp_path))
    output = Path(plan['outputTex']).read_text(encoding='utf-8')

    assert plan['replacementCount'] == 2
    assert '\\usepackage{soul}' in output
    assert '\\hl{#1}' in output
    assert '\\Change{This sentence changed.}' in output
    assert 'DIFadd' not in output
    assert 'DIFdel' not in output
    assert '\\color{blue}' not in output
    si_block = output.split('\\section*{Supplementary Information}', 1)[1].split('\\section*{Funding}', 1)[0]
    references_block = output.split('\\bibliography', 1)[1]
    assert '\\Change{' not in si_block
    assert '\\Change{' not in references_block
