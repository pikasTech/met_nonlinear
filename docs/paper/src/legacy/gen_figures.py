from __future__ import annotations

import argparse

from src.paper_pipeline import list_renderable_figures, main


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Generate paper figures or refresh a selected figure.')
    parser.add_argument(
        '--figure',
        dest='figures',
        action='append',
        help='Render only the specified figure id. Repeat this flag to render multiple figures.',
    )
    parser.add_argument(
        '--list-figures',
        action='store_true',
        help='List figure ids supported by --figure and exit.',
    )
    return parser


def cli() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.list_figures:
        for figure_id in list_renderable_figures():
            print(figure_id)
        return

    main(figure_ids=args.figures)


if __name__ == '__main__':
    cli()
