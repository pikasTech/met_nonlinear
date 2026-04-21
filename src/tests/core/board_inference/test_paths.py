from core.board_inference.paths import REPO_ROOT


def test_repo_root_points_to_workspace_root():
    assert REPO_ROOT.name == "met_nonlinear_master"
    assert (REPO_ROOT / "cli.py").exists()
