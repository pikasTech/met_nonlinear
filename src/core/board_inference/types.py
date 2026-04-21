"""Shared datatypes for the staged board inference refactor."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from core.external_path_parser import ExternalPath


@dataclass(frozen=True)
class ExecutionRequest:
    """Immutable execution request used by the isolated entrypoints."""

    ep_path: ExternalPath
    config: Dict[str, Any]


@dataclass(frozen=True)
class DebugRun:
    """One isolated debug run rooted at a cloned EP directory."""

    label: str
    root: Path
    ep_path: ExternalPath


@dataclass(frozen=True)
class ArtifactDiff:
    """Represents one differing artifact between legacy and refactor runs."""

    path: str
    reason: str
    left_excerpt: str = ''
    right_excerpt: str = ''

    def to_dict(self) -> Dict[str, Any]:
        return {
            'path': self.path,
            'reason': self.reason,
            'left_excerpt': self.left_excerpt,
            'right_excerpt': self.right_excerpt,
        }


@dataclass
class DirectoryComparison:
    """Normalized comparison result for two generated directory trees."""

    left_root: Path
    right_root: Path
    missing_in_left: List[str] = field(default_factory=list)
    missing_in_right: List[str] = field(default_factory=list)
    differing_files: List[ArtifactDiff] = field(default_factory=list)

    @property
    def matches(self) -> bool:
        return not self.missing_in_left and not self.missing_in_right and not self.differing_files

    def to_dict(self) -> Dict[str, Any]:
        return {
            'left_root': self.left_root.as_posix(),
            'right_root': self.right_root.as_posix(),
            'matches': self.matches,
            'missing_in_left': list(self.missing_in_left),
            'missing_in_right': list(self.missing_in_right),
            'differing_files': [item.to_dict() for item in self.differing_files],
        }
