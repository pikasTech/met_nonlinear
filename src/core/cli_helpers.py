"""
CLI 辅助函数模块

包含从 cli.py 中移动的辅助函数，支持多进程处理和项目管理功能。
"""

import logging
import os
import sys
import matplotlib.pyplot as plt
from core.project_manager import ProjectManager
from core.training import start_process, plot_process_start
import config

logger = logging.getLogger(__name__)


def met_comp_with_project(project_path):
    """
    使用指定项目路径执行模型计算
    
    在 Windows 平台上支持实时绘图的多进程处理
    
    Args:
        project_path: 项目路径
    """
    project = ProjectManager(project_path)
    if sys.platform.startswith('win') and config.USE_REAL_TIME_PLOT:
        plot_process_start(project)
        start_process(project)
    else:
        project.process()
    if sys.platform.startswith('win'):
        plt.ioff()
        plt.close('all')


# get_all_project_dirs 函数已移动到 cli_parser.py 中以避免循环依赖