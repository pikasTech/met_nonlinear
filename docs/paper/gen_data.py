from __future__ import annotations

from src.paper_pipeline import generate_all


if __name__ == '__main__':
    generate_all()
    print('Generated docs/paper/data/results.json and docs/paper/latex/values.tex')
