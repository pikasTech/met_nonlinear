from __future__ import annotations

import sys

MESSAGE = """docs/paper/gen_figures.py is deprecated.
Use the ex_project workflow instead:
  python cli.py ep ex_projects/plot/<single|multi>/<figure_project>
For figure ids, list ex_projects with:
  python -m src.visualization.paper_figure_projects list
"""


def main() -> None:
    sys.stderr.write(MESSAGE)
    raise SystemExit(2)


if __name__ == '__main__':
    main()
