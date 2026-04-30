from __future__ import annotations

from src.paper_pipeline import generate_data_only


if __name__ == '__main__':
    generate_data_only()
    print('Generated docs/paper/data/results.json and docs/paper/latex/values.tex')
