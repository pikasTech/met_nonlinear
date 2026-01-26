"""
cli.py - CLI 接口，仅作为内部功能的代理
严格控制启动时序，确保多进程安全
"""

import sys
import os

# 将 src 目录加入 Python 路径，实现模块兼容
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.join(_SCRIPT_DIR, 'src') not in sys.path:
    sys.path.insert(0, os.path.join(_SCRIPT_DIR, 'src'))

import logging
import shutil
from logger import setup_logging

logger = logging.getLogger('cli')


def _run_ep_subcommand(args) -> None:
    """仅处理 ep 子命令，避免加载重型依赖（如 TensorFlow）。"""
    from core.external_cli_handler import handle_ep_command
    handle_ep_command(args)


def _run_main_commands(args) -> None:
    """处理非 ep 的主命令，按原顺序加载重型依赖。"""
    # 第二阶段：环境检查（在重型依赖导入前）
    try:
        from utils.environment_checker import check_environment  # 可能较重，延迟到此处
        # check_environment()  # 如需启用环境自检，取消注释
    except Exception:
        # 环境检查模块缺失不阻塞主流程
        pass

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

    # 非 ep 的主命令再加载重型依赖并执行
    _run_main_commands(args)