"""
cli.py - CLI 接口，仅作为内部功能的代理
严格控制启动时序，确保多进程安全
"""

import sys
import os

os.system('chcp 65001 > nul')

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import subprocess
import time
import json

# 将 src 目录加入 Python 路径，实现模块兼容
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.join(_SCRIPT_DIR, 'src') not in sys.path:
    sys.path.insert(0, os.path.join(_SCRIPT_DIR, 'src'))

import logging
import shutil
from logger import setup_logging

logger = logging.getLogger('cli')


def _run_test_command(args) -> None:
    """运行单元测试命令。"""
    from core.cli_parser import TaskType

    if args.task_type != TaskType.TEST:
        return

    logger.info("Running unit tests...")

    # 构建 pytest 命令
    cmd = [sys.executable, '-m', 'pytest']

    # 添加测试路径
    test_path = args.test_path if args.test_path else 'src/tests'
    cmd.append(test_path)

    # 添加超时参数
    cmd.extend(['--timeout', str(args.test_timeout)])

    # 并行测试配置
    if not args.no_parallel:
        cmd.extend(['--workers', str(args.test_workers)])

    logger.info(f"Executing: {' '.join(cmd)}")

    # 记录开始时间
    start_time = time.time()

    # 运行测试
    try:
        result = subprocess.run(cmd, cwd=_SCRIPT_DIR)
        elapsed = time.time() - start_time

        logger.info(f"Tests completed in {elapsed:.2f} seconds")
        sys.exit(result.returncode)
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        sys.exit(1)


def _run_ep_subcommand(args) -> None:
    """仅处理 ep 子命令，避免加载重型依赖（如TensorFlow）。"""
    from core.external_cli_handler import handle_ep_command
    handle_ep_command(args)


def _run_qemu_subcommand(args) -> None:
    """处理 QEMU 子命令，避免加载重型依赖。"""
    from core.qemu_cli import handle_qemu_command

    exit_code = handle_qemu_command(args)
    sys.exit(exit_code)


def _run_server_subcommand(args) -> None:
    """处理 server 子命令，启动可视化服务器。"""
    import importlib.util
    from pathlib import Path
    manager_path = Path(_SCRIPT_DIR) / 'src' / 'webui' / 'server' / 'src' / 'manager.py'
    spec = importlib.util.spec_from_file_location("manager", str(manager_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    manager = module.ServerManager()

    if args.server_action == 'start':
        result = manager.start()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0 if result.get('status') == 'started' else 1)
    elif args.server_action == 'stop':
        result = manager.stop()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0 if result.get('status') in ('stopped', 'not_running') else 1)
    elif args.server_action == 'status':
        result = manager.status()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0 if result.get('status') == 'running' else 1)
    elif args.server_action == 'logs':
        result = manager.logs(args.server_lines)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0)
    else:
        print(json.dumps({'status': 'error', 'message': f'Unknown server action: {args.server_action}'}))
        sys.exit(1)


def _run_main_commands(args) -> None:
    """处理非 ep 的主命令，按原顺序加载重型依赖。"""
    # 第二阶段：环境检查（在重型依赖导入前）
    try:
        from utils.environment_checker import check_environment  # 可能较重，延迟到此处
        # check_environment()  # 如需启用环境自检，取消注释
    except Exception:
        # 环境检查模块缺失不阻塞主流程
        pass

    try:
        from utils.cuda_preflight import prepare_cuda_visible_devices
        prepare_cuda_visible_devices(logger)
    except Exception as exc:
        logger.warning(f'CUDA preflight failed, continuing with default GPU visibility: {exc}')

    # 第三阶段：依赖导入（保持原有导入顺序）
    from models.base_models import ModelEvent, ModelEventType
    import tensorflow as tf
    from core.training import start_process, plot_process_start
    from core.project_manager import ProjectManager
    from core.task_dispatcher import dispatch_task

    # TensorFlow 配置（必须在导入后立即执行）
    tf.config.experimental.enable_tensor_float_32_execution(False)

    # 原有的主命令处理逻辑
    project_names = args.project_names
    dispatch_task(args.task_type.value, project_names, args)


# 主程序入口
if __name__ == '__main__':
    # 第一阶段：日志配置（仅主进程，防止多进程时重复配置）
    setup_logging()
    logger.info("cli.py start...")

    # 轻量导入参数解析器并解析参数（避免提前导入 TensorFlow 等重型依赖）
    from core.cli_parser import parse_arguments
    args = parse_arguments()  # 不传递参数，parse_arguments 会自动处理

    # 子命令优先，若是 ep 则不导入任何重型模块
    if getattr(args, 'command', None) == 'ep':
        _run_ep_subcommand(args)
        sys.exit(0)

    if getattr(args, 'command', None) == 'qemu':
        _run_qemu_subcommand(args)
        sys.exit(0)

    if getattr(args, 'command', None) == 'server':
        _run_server_subcommand(args)
        sys.exit(0)

    # 测试命令（不加载重型依赖）
    from core.cli_parser import TaskType
    if args.task_type == TaskType.TEST:
        _run_test_command(args)
        sys.exit(0)

    # 非 ep 的主命令再加载重型依赖并执行
    _run_main_commands(args)