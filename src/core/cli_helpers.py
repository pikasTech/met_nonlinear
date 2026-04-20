"""
CLI 辅助函数模块

包含从 cli.py 中移动的辅助函数。
"""

import ctypes
from ctypes import wintypes
import logging
import os
import matplotlib.pyplot as plt
import threading
from core.project_manager import ProjectManager

logger = logging.getLogger(__name__)


def _parent_process_is_alive(parent_pid):
    """判断启动当前 CLI 的父进程是否仍然存活。"""
    if parent_pid <= 0:
        return True

    if os.name != 'nt':
        try:
            os.kill(parent_pid, 0)
        except OSError:
            return False
        return True

    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    STILL_ACTIVE = 259

    kernel32 = ctypes.windll.kernel32
    process_handle = kernel32.OpenProcess(
        PROCESS_QUERY_LIMITED_INFORMATION,
        False,
        parent_pid,
    )
    if not process_handle:
        return False

    try:
        exit_code = wintypes.DWORD()
        if not kernel32.GetExitCodeProcess(process_handle, ctypes.byref(exit_code)):
            return True
        return exit_code.value == STILL_ACTIVE
    finally:
        kernel32.CloseHandle(process_handle)


def _abort_if_detached(project, parent_pid):
    """父会话消失后，主动终止当前训练，避免形成不可见后台残留。"""
    logger.error(
        "Foreground CLI parent pid=%s is gone; aborting detached training for '%s'",
        parent_pid,
        project.project_name,
    )
    try:
        project.state_manager.update_state(training_alive=False)
    except Exception as exc:
        logger.warning("Failed to mark training as stopped after parent exit: %s", exc)

    training_lock_path = os.path.join(project.checkpoint_dir, 'training.lock')
    try:
        if os.path.exists(training_lock_path):
            os.remove(training_lock_path)
    except Exception as exc:
        logger.warning("Failed to remove stale training lock after parent exit: %s", exc)

    plt.ioff()
    plt.close('all')
    os._exit(1)


def _watch_parent_session(project, parent_pid, stop_event, poll_interval=1.0):
    """监控父 CLI 会话；一旦脱离当前前台会话就立即终止。"""
    if parent_pid <= 0:
        return

    while not stop_event.wait(poll_interval):
        if _parent_process_is_alive(parent_pid):
            continue
        _abort_if_detached(project, parent_pid)


def met_comp_with_project(project_path):
    """
    使用指定项目路径执行模型计算。

    CLI 训练必须直接运行在当前进程，确保 stdout/stderr、traceback 和
    训练生命周期始终附着在当前会话中；不要再经由旧的 multiprocessing
    包装层启动训练或绘图子进程。

    Args:
        project_path: 项目路径
    """
    project = ProjectManager(project_path)
    parent_pid = os.getppid()
    stop_event = threading.Event()
    watchdog = threading.Thread(
        target=_watch_parent_session,
        args=(project, parent_pid, stop_event),
        name=f'foreground-parent-watchdog-{project.project_name}',
        daemon=True,
    )
    logger.info(
        "Starting foreground training in current CLI process for '%s' (parent pid=%s)",
        project.project_name,
        parent_pid,
    )
    watchdog.start()
    try:
        project.process()
    finally:
        stop_event.set()
        watchdog.join(timeout=2.0)
        plt.ioff()
        plt.close('all')


# get_all_project_dirs 函数已移动到 cli_parser.py 中以避免循环依赖
