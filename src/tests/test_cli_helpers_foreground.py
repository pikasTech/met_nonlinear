"""
回归测试：CLI 训练必须在当前进程前台执行。
"""

from pathlib import Path
import sys
from unittest.mock import MagicMock, patch


project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core import cli_helpers


def test_met_comp_with_project_runs_in_current_process():
    fake_project = MagicMock()
    fake_project.project_name = "demo_project"

    with patch.object(cli_helpers, "ProjectManager", return_value=fake_project) as project_manager_cls:
        cli_helpers.met_comp_with_project("projects/demo_project")

    project_manager_cls.assert_called_once_with("projects/demo_project")
    fake_project.process.assert_called_once_with()
