from pathlib import Path

from core.board_inference.paths import build_path_aliases, clone_external_path
from core.external_path_parser import ExternalPath


def _make_external_path(root: Path) -> ExternalPath:
    return ExternalPath(
        project_name='demo',
        task_type='qemu-c-inference',
        task_name='sample',
        full_path=root,
        config_path=root / 'config.json',
        output_path=root / 'data',
    )


def test_clone_external_path_rebinds_root(tmp_path):
    original = _make_external_path(tmp_path / 'original')
    cloned = clone_external_path(original, tmp_path / 'clone')

    assert cloned.project_name == original.project_name
    assert cloned.task_type == original.task_type
    assert cloned.task_name == original.task_name
    assert cloned.full_path == tmp_path / 'clone'
    assert cloned.config_path == tmp_path / 'clone' / 'config.json'
    assert cloned.output_path == tmp_path / 'clone' / 'data'


def test_build_path_aliases_contains_absolute_variants(tmp_path):
    aliases = build_path_aliases(tmp_path)

    assert tmp_path.as_posix() in aliases
    assert str(tmp_path) in aliases
