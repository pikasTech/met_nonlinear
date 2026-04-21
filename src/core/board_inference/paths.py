"""Path helpers for isolated board inference debug runs."""

from __future__ import annotations

from pathlib import Path
import shutil
from typing import Set

from core.external_path_parser import ExternalPath


REPO_ROOT = Path(__file__).resolve().parents[3]


def ensure_clean_dir(path: Path) -> Path:
    """Recreate a directory from scratch."""

    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def clone_external_path(ep_path: ExternalPath, full_path: Path) -> ExternalPath:
    """Clone an `ExternalPath` with a different filesystem root."""

    full_path = Path(full_path)
    return ExternalPath(
        project_name=ep_path.project_name,
        task_type=ep_path.task_type,
        task_name=ep_path.task_name,
        full_path=full_path,
        config_path=full_path / 'config.json',
        output_path=full_path / 'data',
    )


def build_path_aliases(path: Path) -> Set[str]:
    """Build absolute and repo-relative aliases for path normalization."""

    normalized = Path(path)
    aliases = {
        normalized.as_posix(),
        str(normalized),
    }

    try:
        relative = normalized.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        relative = None

    if relative:
        aliases.add(relative)
        aliases.add(relative.replace('/', '\\'))

    return {item for item in aliases if item}
