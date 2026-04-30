from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable

PAPER_FONT_FAMILY = 'Times New Roman'
PAPER_PLOT_STYLE_VERSION = 'times-new-roman-mathtext-v1'


def paper_font_candidates(*, bold: bool = False, italic: bool = False) -> Iterable[Path]:
    """Return platform font files preferred for paper figure text."""

    if bold and italic:
        names = ('timesbi.ttf', 'timesbd.ttf', 'times.ttf')
    elif bold:
        names = ('timesbd.ttf', 'times.ttf')
    elif italic:
        names = ('timesi.ttf', 'times.ttf')
    else:
        names = ('times.ttf', 'timesbd.ttf')
    for name in names:
        yield Path('C:/Windows/Fonts') / name


def resolve_paper_font_path(*, bold: bool = False, italic: bool = False) -> Path | None:
    for candidate in paper_font_candidates(bold=bold, italic=italic):
        if candidate.exists():
            return candidate
    return None


def paper_matplotlib_rcparams() -> Dict[str, Any]:
    return {
        'text.usetex': False,
        'font.family': ['serif'],
        'font.serif': [PAPER_FONT_FAMILY, 'Times', 'Nimbus Roman', 'DejaVu Serif'],
        'mathtext.fontset': 'custom',
        'mathtext.rm': PAPER_FONT_FAMILY,
        'mathtext.it': f'{PAPER_FONT_FAMILY}:italic',
        'mathtext.bf': f'{PAPER_FONT_FAMILY}:bold',
        'mathtext.fallback': 'stix',
        'mathtext.default': 'regular',
        'axes.unicode_minus': False,
        'pdf.fonttype': 42,
        'ps.fonttype': 42,
        'svg.fonttype': 'none',
    }


def apply_paper_matplotlib_style() -> Dict[str, Any]:
    """Apply the paper-wide Times New Roman + mathtext defaults."""

    import matplotlib as mpl

    rcparams = paper_matplotlib_rcparams()
    mpl.rcParams.update(rcparams)
    return rcparams


def paper_plot_style_payload() -> Dict[str, Any]:
    font_path = resolve_paper_font_path()
    return {
        'paper_plot_style': {
            'version': PAPER_PLOT_STYLE_VERSION,
            'font_family': PAPER_FONT_FAMILY,
            'font_path': str(font_path).replace('\\', '/') if font_path else None,
            'text_usetex': False,
            'latex_symbol_engine': 'matplotlib mathtext',
            'mathtext_fontset': 'custom',
            'mathtext_fallback': 'stix',
        }
    }


def raw_uses_current_paper_plot_style(raw_path: Path) -> bool:
    if not raw_path.exists():
        return False
    try:
        import json

        payload = json.loads(raw_path.read_text(encoding='utf-8'))
    except Exception:
        return False
    style = payload.get('paper_plot_style') if isinstance(payload, dict) else None
    return isinstance(style, dict) and style.get('version') == PAPER_PLOT_STYLE_VERSION
