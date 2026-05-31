"""
现代化 CLI 参数解析模块

使用 argparse + dataclass + 类型提示的现代化实现
支持配置文件的默认值设置，提供结构化的参数数据
"""

import argparse
import json
import logging
import os
import fnmatch
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """任务类型枚举"""
    TRAIN = "train"
    EVALUATE = "evaluate"
    METRICS = "metrics"
    CLEAN = "clean"
    MODEL_INFO = "model_info"
    LUT = "lut"
    INFERENCE = "inference"
    ANALYZE = "analyze"
    WAVE = "wave"
    BIAS_VISUALIZATION = "bias_visualization"
    EXPORT_RESISTANCE = "export_resistance"
    STANDARDIZE_RESISTANCE = "standardize_resistance"
    WAVEFORM_VIS = "waveform_vis"
    LOSS_PLOT = "loss_plot"
    TEST = "test"


@dataclass
class CLIArgs:
    """结构化的CLI参数数据类"""
    task_type: TaskType
    project_names: List[str]
    force_mode: bool = False
    quick_inference: bool = False
    layers_param: Optional[int] = None
    bias_method: str = "auto"
    bias_params: Dict[str, Any] = field(default_factory=dict)
    baseline_dir: Optional[str] = None
    compensated_dir: Optional[str] = None
    vis_output_dir: Optional[str] = None
    vis_config_path: Optional[str] = None
    # 频率响应对比参数
    freq_compare_sources: Optional[List[str]] = None
    layout_mode: str = "overlay"
    # 电阻管理参数
    series: List[str] = field(default_factory=lambda: ['E96', 'E24'])
    output_dir: Optional[str] = None
    input_csv: Optional[str] = None
    skip_validation: bool = False
    generate_bom: bool = False
    bom_package: str = '0805'
    bom_standardize: Optional[str] = None
    
    # 子命令支持（简化设计）
    command: Optional[str] = None
    ep_action: Optional[str] = None
    ep_project_path: Optional[str] = None
    ep_probe_uid: Optional[str] = None
    ep_serial_port: Optional[str] = None
    ep_serial_baud_rate: Optional[int] = None
    ep_keil_target: Optional[str] = None
    ep_keil_program_backend: Optional[str] = None
    ep_keil_programmer: Optional[str] = None
    ep_keil_capture_timeout: Optional[int] = None
    ep_keil_job_timeout: Optional[int] = None
    ep_keil_cli_path: Optional[str] = None
    qemu_action: Optional[str] = None
    qemu_project_dir: Optional[str] = None
    qemu_machine: str = 'olimex-stm32-h405'
    qemu_timeout: int = 5
    qemu_output_path: Optional[str] = None
    qemu_qemu_path: Optional[str] = None
    qemu_gcc_path: Optional[str] = None
    qemu_linker_script: Optional[str] = None

    # 测试相关参数
    test_path: Optional[str] = None
    test_workers: int = 4
    test_timeout: int = 300
    no_parallel: bool = False
    recursive_projects: bool = False
    missing_only: bool = False

    # 服务器相关参数
    server_action: Optional[str] = None
    server_port: int = 3000
    server_lines: int = 100
    paper_editor_action: Optional[str] = None
    paper_entry: str = 'main.tex'
    paper_output_path: Optional[str] = None
    paper_wrap_columns: Optional[int] = None
    paper_latex_lines: Optional[List[int]] = None
    paper_view_lines: Optional[List[int]] = None
    paper_markdown_lines: Optional[List[int]] = None
    paper_html_lines: Optional[List[int]] = None
    paper_outline_titles: Optional[List[str]] = None
    paper_latex_action: Optional[str] = None
    paper_latex_workdir: Optional[str] = None
    paper_latex_tex: Optional[str] = None
    paper_latex_output_dir: Optional[str] = None
    paper_latex_engine: Optional[str] = None
    paper_latex_passes: int = 3
    paper_latex_no_bibtex: bool = False


@dataclass
class CLIConfig:
    """CLI默认值配置类"""
    default_project: str = "WNET5q1h2u6l3"
    projects_dir: str = "projects"
    default_bias_method: str = "auto"
    default_layers: Optional[int] = None
    default_force_mode: bool = False
    default_quick_inference: bool = False
    
    # 可视化默认配置
    default_baseline_dir: Optional[str] = None
    default_compensated_dir: Optional[str] = None
    default_vis_output_dir: Optional[str] = None
    
    @classmethod
    def from_file(cls, config_path: str) -> 'CLIConfig':
        """从配置文件加载默认值"""
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f) or {}
            # 只使用类中定义的字段
            valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
            filtered_data = {k: v for k, v in config_data.items() if k in valid_fields}
            return cls(**filtered_data)
        except Exception as e:
            logger.warning(f"配置文件加载失败: {e}，使用默认配置")
            return cls()


class ArgumentParsingError(Exception):
    """参数解析错误"""
    pass


class ArgumentValidator:
    """参数验证器"""
    
    @staticmethod
    def validate_layers(layers: Optional[int]) -> None:
        """验证层数参数"""
        if layers is not None and layers <= 0:
            raise ArgumentParsingError("--layers 参数必须是正整数")
    
    @staticmethod
    def validate_bias_params(bias_params_str: Optional[str]) -> Dict[str, Any]:
        """验证偏置参数"""
        if bias_params_str is None:
            return {}
        try:
            return json.loads(bias_params_str)
        except json.JSONDecodeError as e:
            raise ArgumentParsingError(f"无效的偏置参数JSON: {e}")
    
    @staticmethod
    def validate_project_name(project_name: str) -> List[str]:
        """验证并解析项目名称"""
        if '*' in project_name:
            project_names = get_all_project_dirs()
            project_names = fnmatch.filter(project_names, project_name)
            if not project_names:
                raise ArgumentParsingError(f"没有找到匹配的项目: {project_name}")
            return project_names
        return [project_name]


def load_config() -> CLIConfig:
    """加载配置文件中的默认值"""
    config_paths = [
        'cli_config.yaml',                                       # 项目根目录
        'core/cli_defaults.yaml',                               # 核心模块目录
        os.path.expanduser('~/.met_nonlinear/cli_defaults.yaml')  # 用户目录
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            logger.info(f"加载配置文件: {config_path}")
            return CLIConfig.from_file(config_path)
    
    logger.debug("未找到配置文件，使用内置默认值")
    return CLIConfig()


def get_all_project_dirs(base_path: str = 'projects', recursive: bool = True) -> List[str]:
    """
    获取所有项目目录
    
    Args:
        base_path: 项目基础路径，默认为 'projects'
        
    Returns:
        List[str]: 项目目录相对路径列表（相对于 base_path）
    """
    if not os.path.exists(base_path):
        return []

    project_dirs: List[str] = []

    if not recursive:
        for entry in os.scandir(base_path):
            if entry.is_dir() and os.path.exists(os.path.join(entry.path, 'config.json')):
                project_dirs.append(entry.name)
        return sorted(project_dirs)

    for current_root, dir_names, file_names in os.walk(base_path):
        if 'config.json' not in file_names:
            continue
        relative_path = os.path.relpath(current_root, base_path).replace('\\', '/')
        if relative_path == '.':
            continue
        project_dirs.append(relative_path)

    return sorted(project_dirs)


def _create_main_parser_only(config: CLIConfig) -> argparse.ArgumentParser:
    """创建主命令解析器（不包含子命令）"""
    parser = argparse.ArgumentParser(
        description='MET Nonlinear Model Training and Inference CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
任务类型说明：
  train         训练模型
  evaluate      评估模型性能
    metrics       从评估产物提取表格指标并导出 metrics.json
  clean         清理项目数据
  model_info    显示模型信息
  lut           生成查找表
  inference     运行推理
  analyze       分析错误
  wave          生成波形数据
  bias_viz      偏置可视化
  loss_plot     绘制训练loss曲线（lr, loss, val_loss）

示例用法：
  python cli.py -t PROJECT_NAME
  python cli.py -e PROJECT_NAME
    python cli.py --metrics PROJECT_NAME
  python cli.py -i PROJECT_NAME --layers 5
  python cli.py -a PROJECT_NAME --bias-method auto
  python cli.py --loss-plot PROJECT_NAME
  python cli.py ep project/freq-response-compare/task-name
    python cli.py ep create project/freq-response-compare/task-name

配置文件：
  可以在以下位置创建 cli_config.yaml 文件来设置默认值：
  - 项目根目录: cli_config.yaml
  - 核心模块目录: core/cli_defaults.yaml
  - 用户目录: ~/.met_nonlinear/cli_defaults.yaml
        """
    )
    _add_main_arguments(parser, config)
    return parser


def _add_qemu_common_arguments(parser: argparse.ArgumentParser) -> None:
    """添加 QEMU 子命令的通用参数。"""
    parser.add_argument('qemu_project_dir', nargs='?',
                        help='QEMU 工程目录，例如 src/tests/qemu/stm32f405_hello')
    parser.add_argument('--machine', default='olimex-stm32-h405',
                        help='QEMU 机器型号，默认: olimex-stm32-h405')
    parser.add_argument('--timeout', type=int, default=5,
                        help='运行超时时间（秒），0 表示不设超时，默认: 5')
    parser.add_argument('--output', dest='qemu_output_path',
                        help='ELF 输出文件名或路径')
    parser.add_argument('--qemu-path', dest='qemu_qemu_path',
                        help='qemu-system-arm.exe 的绝对路径')
    parser.add_argument('--gcc-path', dest='qemu_gcc_path',
                        help='arm-none-eabi-gcc.exe 的绝对路径')
    parser.add_argument('--linker-script', dest='qemu_linker_script',
                        help='链接脚本文件名或路径，默认自动检测工程目录中的 .ld 文件')


def _create_subcommand_parser(config: CLIConfig) -> argparse.ArgumentParser:
    """创建轻量子命令解析器。"""
    parser = argparse.ArgumentParser(
        description='MET Nonlinear Lightweight Subcommands',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法：
  python cli.py ep project/freq-response-compare/task-name
    python cli.py ep create project/freq-response-compare/task-name
  python cli.py ep LSTMu32al_rs300/freq-response-compare/test
  python cli.py qemu list
    python cli.py qemu build src/tests/qemu/stm32f405_hello
    python cli.py qemu run src/tests/qemu/stm32f405_hello --timeout 5
    python cli.py qemu build-run src/tests/qemu/stm32f405_hello
        """
    )
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    ep_parser = subparsers.add_parser('ep', help='拓展项目管理 (External Project)')
    ep_parser.add_argument(
        'ep_args',
        nargs='+',
        help='执行格式: ep <path>；创建模板格式: ep create <path>；Keil bench: ep keil-bench <path>'
    )
    ep_parser.add_argument('--probe-uid', dest='ep_probe_uid',
                           help='Keil bench 使用的 CMSIS-DAP probe UID')
    ep_parser.add_argument('--serial-port', dest='ep_serial_port',
                           help='Keil bench 验证使用的串口号，例如 COM8')
    ep_parser.add_argument('--baud-rate', dest='ep_serial_baud_rate', type=int,
                           help='Keil bench 串口波特率，默认从配置读取')
    ep_parser.add_argument('--target', dest='ep_keil_target',
                           help='Keil bench 目标名，默认从配置读取')
    ep_parser.add_argument('--program-backend', dest='ep_keil_program_backend',
                           choices=['keil', 'pyocd', 'auto'],
                           help='Keil bench 烧录后端，默认从配置读取')
    ep_parser.add_argument('--programmer', dest='ep_keil_programmer',
                           help='Keil bench programmer 类型，默认从配置读取')
    ep_parser.add_argument('--capture-timeout', dest='ep_keil_capture_timeout', type=int,
                           help='Keil bench 串口抓取超时（秒），默认从配置读取')
    ep_parser.add_argument('--job-timeout', dest='ep_keil_job_timeout', type=int,
                           help='Keil build/program 等待超时（秒），默认从配置读取')
    ep_parser.add_argument('--keil-cli-path', dest='ep_keil_cli_path',
                           help='keil-cli.py 的绝对路径，默认自动探测 ~/.agents/skills/keil/keil-cli.py')

    qemu_parser = subparsers.add_parser('qemu', help='QEMU 边缘设备仿真工具')
    qemu_subparsers = qemu_parser.add_subparsers(dest='qemu_action', help='QEMU 操作')

    qemu_list_parser = qemu_subparsers.add_parser('list', help='列出可用的 QEMU 工程目录')
    qemu_list_parser.add_argument('--qemu-path', dest='qemu_qemu_path',
                                  help='qemu-system-arm.exe 的绝对路径')
    qemu_list_parser.add_argument('--gcc-path', dest='qemu_gcc_path',
                                  help='arm-none-eabi-gcc.exe 的绝对路径')

    qemu_build_parser = qemu_subparsers.add_parser('build', help='编译指定 QEMU 工程')
    _add_qemu_common_arguments(qemu_build_parser)

    qemu_run_parser = qemu_subparsers.add_parser('run', help='运行指定 QEMU 工程的 ELF')
    _add_qemu_common_arguments(qemu_run_parser)

    qemu_build_run_parser = qemu_subparsers.add_parser('build-run', help='编译并运行指定 QEMU 工程')
    _add_qemu_common_arguments(qemu_build_run_parser)

    server_parser = subparsers.add_parser('server', help='可视化服务器管理')
    server_subparsers = server_parser.add_subparsers(dest='server_action', help='服务器操作')
    
    server_start_parser = server_subparsers.add_parser('start', help='启动可视化服务器')
    server_start_parser.add_argument('--port', type=int, default=3000, help='服务器端口，默认: 3000')
    
    server_stop_parser = server_subparsers.add_parser('stop', help='停止可视化服务器')
    
    server_status_parser = server_subparsers.add_parser('status', help='查看服务器状态')
    
    server_logs_parser = server_subparsers.add_parser('logs', help='查看服务器日志')
    server_logs_parser.add_argument('--lines', type=int, default=100, dest='server_lines', help='日志行数，默认: 100')

    paper_editor_parser = subparsers.add_parser('paper-editor', help='论文编辑器辅助命令')
    paper_editor_subparsers = paper_editor_parser.add_subparsers(dest='paper_editor_action', help='论文编辑器操作')

    paper_export_parser = paper_editor_subparsers.add_parser('export-md', help='导出 paper editor 渲染后的 Markdown')
    paper_export_parser.add_argument('--entry', dest='paper_entry', default='main.tex', help='latex 入口文件，默认: main.tex')
    paper_export_parser.add_argument('--output', dest='paper_output_path', default='cache/webui/paper-editor/main.preview.md', help='导出的 Markdown 路径，相对仓库根目录')

    paper_export_html_parser = paper_editor_subparsers.add_parser('export-html', help='导出 paper editor 渲染后的 HTML')
    paper_export_html_parser.add_argument('--entry', dest='paper_entry', default='main.tex', help='latex 入口文件，默认: main.tex')
    paper_export_html_parser.add_argument('--output', dest='paper_output_path', default='cache/webui/paper-editor/main.preview.html', help='导出的 HTML 路径，相对仓库根目录')

    paper_export_map_parser = paper_editor_subparsers.add_parser('export-map', help='导出 paper editor 的 LaTeX/Markdown/HTML 行号映射 JSON')
    paper_export_map_parser.add_argument('--entry', dest='paper_entry', default='main.tex', help='latex 入口文件，默认: main.tex')
    paper_export_map_parser.add_argument('--output', dest='paper_output_path', default='cache/webui/paper-editor/main.line-mappings.json', help='导出的映射 JSON 路径，相对仓库根目录')
    paper_export_map_parser.add_argument('--wrap-columns', dest='paper_wrap_columns', type=int, help='额外导出按指定列宽换行后的 view-line 到 raw-line 映射')

    paper_diagnose_map_parser = paper_editor_subparsers.add_parser('diagnose-map', help='导出 paper editor 的严格映射链路诊断 JSON')
    paper_diagnose_map_parser.add_argument('--entry', dest='paper_entry', default='main.tex', help='latex 入口文件，默认: main.tex')
    paper_diagnose_map_parser.add_argument('--output', dest='paper_output_path', default='cache/webui/paper-editor/main.diagnostic.json', help='导出的诊断 JSON 路径，相对仓库根目录')
    paper_diagnose_map_parser.add_argument('--wrap-columns', dest='paper_wrap_columns', type=int, help='后端按指定列宽生成 view-line 到 raw-line 映射')
    paper_diagnose_map_parser.add_argument('--latex-lines', dest='paper_latex_lines', nargs='*', type=int, help='要诊断的 LaTeX raw line 列表')
    paper_diagnose_map_parser.add_argument('--view-lines', dest='paper_view_lines', nargs='*', type=int, help='要诊断的 wrapped view-line 列表')
    paper_diagnose_map_parser.add_argument('--markdown-lines', dest='paper_markdown_lines', nargs='*', type=int, help='要诊断的 Markdown line 列表')
    paper_diagnose_map_parser.add_argument('--html-lines', dest='paper_html_lines', nargs='*', type=int, help='要诊断的 HTML line 列表')
    paper_diagnose_map_parser.add_argument('--outline-title', dest='paper_outline_titles', action='append', help='要诊断的 outline 标题，可重复传入')

    paper_latex_parser = subparsers.add_parser('paper-latex', help='论文 LaTeX 编译辅助命令')
    paper_latex_subparsers = paper_latex_parser.add_subparsers(dest='paper_latex_action', help='论文 LaTeX 操作')

    paper_latex_build_parser = paper_latex_subparsers.add_parser('build', help='执行本地 LaTeX 编译链')
    paper_latex_build_parser.add_argument('--workdir', dest='paper_latex_workdir', default='docs/paper/latex', help='LaTeX 工作目录，相对仓库根目录')
    paper_latex_build_parser.add_argument('--tex', dest='paper_latex_tex', default='main.tex', help='TeX 入口文件，相对 workdir 或绝对路径')
    paper_latex_build_parser.add_argument('--output-dir', dest='paper_latex_output_dir', default='build', help='编译输出目录，相对 workdir 或绝对路径')
    paper_latex_build_parser.add_argument('--engine', dest='paper_latex_engine', default='xelatex', help='LaTeX 引擎，默认: xelatex')
    paper_latex_build_parser.add_argument('--passes', dest='paper_latex_passes', type=int, default=3, help='LaTeX 总 pass 数，默认: 3')
    paper_latex_build_parser.add_argument('--no-bibtex', dest='paper_latex_no_bibtex', action='store_true', help='跳过 bibtex 步骤')

    return parser


def create_parser(config: Optional[CLIConfig] = None) -> argparse.ArgumentParser:
    """创建命令行参数解析器（向后兼容接口）"""
    if config is None:
        config = load_config()
    # 默认返回主命令解析器
    return _create_main_parser_only(config)




def _add_main_arguments(parser: argparse.ArgumentParser, config: CLIConfig) -> None:
    """添加主命令的所有参数"""
    # 任务类型（互斥组）
    task_group = parser.add_mutually_exclusive_group(required=False)
    task_group.add_argument('-t', '--train', action='store_const', 
                           const=TaskType.TRAIN, dest='task_type',
                           help='训练模型')
    task_group.add_argument('-e', '--evaluate', action='store_const',
                           const=TaskType.EVALUATE, dest='task_type',
                           help='评估模型')
    task_group.add_argument('--metrics', action='store_const',
                           const=TaskType.METRICS, dest='task_type',
                           help='从 -e 生成的产物提取表格指标到 data/metrics.json')
    task_group.add_argument('-c', '--clean', action='store_const',
                           const=TaskType.CLEAN, dest='task_type',
                           help='清理项目数据')
    task_group.add_argument('-m', '--model-info', action='store_const',
                           const=TaskType.MODEL_INFO, dest='task_type',
                           help='显示模型信息')
    task_group.add_argument('-l', '--lut', action='store_const',
                           const=TaskType.LUT, dest='task_type',
                           help='生成查找表')
    task_group.add_argument('-i', '--inference', action='store_const',
                           const=TaskType.INFERENCE, dest='task_type',
                           help='运行推理')
    task_group.add_argument('-a', '--analyze', action='store_const',
                           const=TaskType.ANALYZE, dest='task_type',
                           help='分析错误')
    task_group.add_argument('-w', '--wave', action='store_const',
                           const=TaskType.WAVE, dest='task_type',
                           help='生成波形数据')
    task_group.add_argument('--bias-viz', '--bias-visualization', 
                           action='store_const',
                           const=TaskType.BIAS_VISUALIZATION, dest='task_type',
                           help='偏置可视化')
    task_group.add_argument('-r', '--export-resistance', 
                           action='store_const',
                           const=TaskType.EXPORT_RESISTANCE, dest='task_type',
                           help='导出电阻值到CSV（快速，不运行推理）')
    task_group.add_argument('-s', '--standardize',
                           action='store_const', 
                           const=TaskType.STANDARDIZE_RESISTANCE, dest='task_type',
                           help='标准化电阻值')
    task_group.add_argument('--vis', '--waveform-vis', action='store_const',
                           const=TaskType.WAVEFORM_VIS, dest='task_type',
                           help='生成Origin/Target波形可视化图')
    task_group.add_argument('--test', action='store_const',
                           const=TaskType.TEST, dest='task_type',
                           help='运行单元测试')
    task_group.add_argument('--loss-plot', action='store_const',
                           const=TaskType.LOSS_PLOT, dest='task_type',
                           help='绘制训练loss曲线（lr, loss, val_loss）')

    # 项目名称
    parser.add_argument('project_name', nargs='?', 
                       default=config.default_project,
                       help=f'项目名称（支持通配符），默认: {config.default_project}')
    parser.add_argument('-all', '--all-projects', action='store_true',
                       help='处理所有项目')
    parser.add_argument('--missing-only', action='store_true',
                       help='仅处理缺失目标产物的项目（当前主要用于 --metrics）')
    
    # 通用标志
    parser.add_argument('-f', '--force', action='store_true',
                       default=config.default_force_mode,
                       help=f'强制模式，默认: {config.default_force_mode}')
    parser.add_argument('-q', '--quick', action='store_true',
                       default=config.default_quick_inference,
                       help=f'快速推理模式，默认: {config.default_quick_inference}')
    
    # 推理相关参数
    inference_group = parser.add_argument_group('推理参数')
    inference_group.add_argument('--layers', type=int, metavar='N',
                                default=config.default_layers,
                                help=f'推理层数（必须为正整数），默认: {config.default_layers}')
    
    # 偏置分析参数
    bias_group = parser.add_argument_group('偏置分析参数')
    bias_group.add_argument('--bias-method', 
                           choices=['auto', 'steady_state', 'frequency_domain'],
                           default=config.default_bias_method,
                           help=f'偏置分析方法，默认: {config.default_bias_method}')
    bias_group.add_argument('--bias-params', type=str,
                           metavar='JSON',
                           help='偏置分析参数（JSON格式）')
    
    # 可视化参数
    viz_group = parser.add_argument_group('可视化参数')
    viz_group.add_argument('--baseline', metavar='DIR',
                          default=config.default_baseline_dir,
                          help=f'基线数据目录，默认: {config.default_baseline_dir}')
    viz_group.add_argument('--compensated', metavar='DIR',
                          default=config.default_compensated_dir,
                          help=f'补偿数据目录，默认: {config.default_compensated_dir}')
    viz_group.add_argument('--vis-output', metavar='DIR',
                          default=config.default_vis_output_dir,
                          help=f'可视化输出目录，默认: {config.default_vis_output_dir}')
    viz_group.add_argument('--vis-config', metavar='FILE',
                          help='可视化配置文件')
    viz_group.add_argument('--vis-freq-response-compare', 
                          nargs='*',  # 支持1-2个参数
                          metavar='PROJECT[@STATE]',
                          help='频率响应对比。格式: PROJECT[@STATE]。'
                               '1个参数: 项目内补偿前后对比；'
                               '2个参数: 任意两个数据源对比。'
                               'STATE可以是origin或compensation，默认为origin')
    viz_group.add_argument('--layout',
                          choices=['overlay', 'side_by_side'],
                          default='overlay',
                          help='布局模式: overlay(叠加) 或 side_by_side(左右分布)，默认overlay')
    
    # 电阻管理参数
    resistance_group = parser.add_argument_group('电阻管理参数')
    resistance_group.add_argument('--series',
                                 nargs='+',
                                 choices=['E6', 'E12', 'E24', 'E96'],
                                 default=['E96', 'E24'],
                                 help='标准化系列（默认: E96 E24）')
    resistance_group.add_argument('--output-dir',
                                 metavar='DIR',
                                 help='输出目录（默认：项目data/resistance_tables）')
    resistance_group.add_argument('--bom', action='store_true',
                                 help='生成权重电阻BOM')
    resistance_group.add_argument('--bom-package', type=str, default='0805',
                                 help='BOM封装规格（默认: 0805）')
    resistance_group.add_argument('--bom-standardize', type=str,
                                 choices=['E6', 'E12', 'E24', 'E96', 'E192'],
                                 help='BOM导出时使用的标准化系列（可覆盖config.json中的配置）')
    resistance_group.add_argument('--bom-numbering', type=str,
                                 choices=['sequential', 'grouped'],
                                 default='sequential',
                                 help='BOM编号模式：sequential(顺序) 或 grouped(分组，R1-R7正向，R8-R14负向)')
    resistance_group.add_argument('--input-csv',
                                 metavar='FILE',
                                 help='输入CSV文件（用于标准化）')
    resistance_group.add_argument('--skip-validation',
                                 action='store_true',
                                 help='跳过验证步骤（不推荐）')

    # 测试参数组
    test_group = parser.add_argument_group('测试参数')
    test_group.add_argument('--test-path', type=str, metavar='PATH',
                           help='指定测试路径（默认: src/tests）')
    test_group.add_argument('--test-workers', type=int, metavar='N',
                           default=4,
                           help='并行测试worker数量（默认: 4）')
    test_group.add_argument('--test-timeout', type=int, metavar='SECONDS',
                           default=300,
                           help='单个测试超时时间（默认: 300秒）')
    test_group.add_argument('--no-parallel', action='store_true',
                           help='禁用并行测试')


def parse_arguments(argv: Optional[List[str]] = None) -> CLIArgs:
    """
    解析命令行参数

    Args:
        argv: 命令行参数列表，为None时使用sys.argv

    Returns:
        CLIArgs: 结构化的参数对象

    Raises:
        ArgumentParsingError: 参数解析错误
    """
    # 加载配置文件中的默认值
    config = load_config()

    # 处理 sys.argv 的特殊情况：移除脚本名称
    if argv is None:
        import sys
        argv = sys.argv[1:]  # 跳过脚本名称

    # 预处理：检测是否为轻量子命令
    is_lightweight_subcommand = len(argv) > 0 and argv[0] in {'ep', 'qemu', 'server', 'paper-editor', 'paper-latex'}

    # 根据是否为轻量子命令选择不同的解析器
    if is_lightweight_subcommand:
        parser = _create_subcommand_parser(config)
    else:
        parser = _create_main_parser_only(config)

    try:
        args = parser.parse_args(argv)

        # 检查是否为 ep 子命令
        is_ep_subcommand = getattr(args, 'command', None) == 'ep'
        is_qemu_subcommand = getattr(args, 'command', None) == 'qemu'

        # 如果是 ep 子命令，跳过主命令的验证逻辑
        if is_ep_subcommand:
            ep_args = list(getattr(args, 'ep_args', []) or [])
            ep_action = 'run'
            ep_project_path = None

            if len(ep_args) == 1 and ep_args[0] != 'create':
                ep_project_path = ep_args[0]
            elif len(ep_args) == 2 and ep_args[0] == 'create':
                ep_action = 'create'
                ep_project_path = ep_args[1]
            elif len(ep_args) == 2 and ep_args[0] == 'keil-bench':
                ep_action = 'keil-bench'
                ep_project_path = ep_args[1]
            else:
                raise ArgumentParsingError(
                    'ep 子命令格式错误，应使用 "ep <path>"、"ep create <path>" 或 "ep keil-bench <path>"'
                )

            return CLIArgs(
                task_type=TaskType.INFERENCE,  # 子命令实际不会用到
                project_names=[],
                command='ep',
                ep_action=ep_action,
                ep_project_path=ep_project_path,
                ep_probe_uid=getattr(args, 'ep_probe_uid', None),
                ep_serial_port=getattr(args, 'ep_serial_port', None),
                ep_serial_baud_rate=getattr(args, 'ep_serial_baud_rate', None),
                ep_keil_target=getattr(args, 'ep_keil_target', None),
                ep_keil_program_backend=getattr(args, 'ep_keil_program_backend', None),
                ep_keil_programmer=getattr(args, 'ep_keil_programmer', None),
                ep_keil_capture_timeout=getattr(args, 'ep_keil_capture_timeout', None),
                ep_keil_job_timeout=getattr(args, 'ep_keil_job_timeout', None),
                ep_keil_cli_path=getattr(args, 'ep_keil_cli_path', None),
            )

        if is_qemu_subcommand:
            return CLIArgs(
                task_type=TaskType.INFERENCE,  # 子命令实际不会用到
                project_names=[],
                command='qemu',
                qemu_action=getattr(args, 'qemu_action', None),
                qemu_project_dir=getattr(args, 'qemu_project_dir', None),
                qemu_machine=getattr(args, 'machine', 'olimex-stm32-h405'),
                qemu_timeout=getattr(args, 'timeout', 5),
                qemu_output_path=getattr(args, 'qemu_output_path', None),
                qemu_qemu_path=getattr(args, 'qemu_qemu_path', None),
                qemu_gcc_path=getattr(args, 'qemu_gcc_path', None),
                qemu_linker_script=getattr(args, 'qemu_linker_script', None)
            )

        is_server_subcommand = getattr(args, 'command', None) == 'server'
        if is_server_subcommand:
            return CLIArgs(
                task_type=TaskType.INFERENCE,
                project_names=[],
                command='server',
                server_action=getattr(args, 'server_action', None),
                server_port=getattr(args, 'port', 3000),
                server_lines=getattr(args, 'server_lines', 100)
            )

        is_paper_editor_subcommand = getattr(args, 'command', None) == 'paper-editor'
        if is_paper_editor_subcommand:
            return CLIArgs(
                task_type=TaskType.INFERENCE,
                project_names=[],
                command='paper-editor',
                paper_editor_action=getattr(args, 'paper_editor_action', None),
                paper_entry=getattr(args, 'paper_entry', 'main.tex'),
                paper_output_path=getattr(args, 'paper_output_path', None),
                paper_wrap_columns=getattr(args, 'paper_wrap_columns', None),
                paper_latex_lines=getattr(args, 'paper_latex_lines', None),
                paper_view_lines=getattr(args, 'paper_view_lines', None),
                paper_markdown_lines=getattr(args, 'paper_markdown_lines', None),
                paper_html_lines=getattr(args, 'paper_html_lines', None),
                paper_outline_titles=getattr(args, 'paper_outline_titles', None),
            )

        is_paper_latex_subcommand = getattr(args, 'command', None) == 'paper-latex'
        if is_paper_latex_subcommand:
            return CLIArgs(
                task_type=TaskType.INFERENCE,
                project_names=[],
                command='paper-latex',
                paper_latex_action=getattr(args, 'paper_latex_action', None),
                paper_latex_workdir=getattr(args, 'paper_latex_workdir', None),
                paper_latex_tex=getattr(args, 'paper_latex_tex', None),
                paper_latex_output_dir=getattr(args, 'paper_latex_output_dir', None),
                paper_latex_engine=getattr(args, 'paper_latex_engine', None),
                paper_latex_passes=getattr(args, 'paper_latex_passes', 3),
                paper_latex_no_bibtex=getattr(args, 'paper_latex_no_bibtex', False),
            )

        # 检查是否为测试任务
        is_test_task = getattr(args, 'task_type', None) == TaskType.TEST

        # 检查是否为频率响应对比任务
        is_freq_compare_task = hasattr(args, 'vis_freq_response_compare') and args.vis_freq_response_compare is not None

        # 验证任务类型和频率响应对比的互斥关系
        if is_freq_compare_task and args.task_type is not None:
            raise ArgumentParsingError("不能同时指定任务类型和频率响应对比")

        if not is_freq_compare_task and args.task_type is None and not is_test_task:
            raise ArgumentParsingError("必须指定一个任务类型或使用 --vis-freq-response-compare")

        # 解析项目名称（测试任务不需要项目名称）
        if is_test_task:
            project_names = []
        elif args.all_projects:
            project_names = get_all_project_dirs(config.projects_dir, recursive=True)
            if not project_names:
                raise ArgumentParsingError(f"在目录 '{config.projects_dir}' 中没有找到任何项目")
        else:
            project_names = ArgumentValidator.validate_project_name(args.project_name)
        
        # 验证参数
        ArgumentValidator.validate_layers(args.layers)
        bias_params = ArgumentValidator.validate_bias_params(args.bias_params)
        
        # 验证文件和目录路径
        if args.vis_config and not os.path.exists(args.vis_config):
            logger.warning(f"可视化配置文件不存在: {args.vis_config}")
        
        # 构建结果对象
        # 为频率响应对比任务设置虚拟task_type
        effective_task_type = args.task_type if args.task_type is not None else TaskType.EVALUATE
        
        return CLIArgs(
            task_type=effective_task_type,
            project_names=project_names,
            force_mode=args.force,
            quick_inference=args.quick,
            layers_param=args.layers,
            bias_method=args.bias_method,
            bias_params=bias_params,
            baseline_dir=args.baseline,
            compensated_dir=args.compensated,
            vis_output_dir=args.vis_output,
            vis_config_path=args.vis_config,
            freq_compare_sources=args.vis_freq_response_compare if hasattr(args, 'vis_freq_response_compare') else None,
            layout_mode=args.layout if hasattr(args, 'layout') else 'overlay',
            series=args.series if hasattr(args, 'series') else ['E96', 'E24'],
            output_dir=args.output_dir if hasattr(args, 'output_dir') else None,
            input_csv=args.input_csv if hasattr(args, 'input_csv') else None,
            skip_validation=args.skip_validation if hasattr(args, 'skip_validation') else False,
            generate_bom=args.bom if hasattr(args, 'bom') else False,
            bom_package=args.bom_package if hasattr(args, 'bom_package') else '0805',
            bom_standardize=args.bom_standardize if hasattr(args, 'bom_standardize') else None,
            command=getattr(args, 'command', None),
            ep_action=getattr(args, 'ep_action', None),
            ep_project_path=getattr(args, 'ep_project_path', None),
            ep_probe_uid=getattr(args, 'ep_probe_uid', None),
            ep_serial_port=getattr(args, 'ep_serial_port', None),
            ep_serial_baud_rate=getattr(args, 'ep_serial_baud_rate', None),
            ep_keil_target=getattr(args, 'ep_keil_target', None),
            ep_keil_program_backend=getattr(args, 'ep_keil_program_backend', None),
            ep_keil_programmer=getattr(args, 'ep_keil_programmer', None),
            ep_keil_capture_timeout=getattr(args, 'ep_keil_capture_timeout', None),
            ep_keil_job_timeout=getattr(args, 'ep_keil_job_timeout', None),
            ep_keil_cli_path=getattr(args, 'ep_keil_cli_path', None),
            qemu_action=getattr(args, 'qemu_action', None),
            qemu_project_dir=getattr(args, 'qemu_project_dir', None),
            qemu_machine=getattr(args, 'machine', 'olimex-stm32-h405'),
            qemu_timeout=getattr(args, 'timeout', 5),
            qemu_output_path=getattr(args, 'qemu_output_path', None),
            qemu_qemu_path=getattr(args, 'qemu_qemu_path', None),
            qemu_gcc_path=getattr(args, 'qemu_gcc_path', None),
            qemu_linker_script=getattr(args, 'qemu_linker_script', None),
            test_path=getattr(args, 'test_path', None),
            test_workers=getattr(args, 'test_workers', 4),
            test_timeout=getattr(args, 'test_timeout', 300),
            no_parallel=getattr(args, 'no_parallel', False),
            recursive_projects=True,
            missing_only=getattr(args, 'missing_only', False)
        )
        
    except SystemExit as e:
        # argparse 调用 sys.exit() 时（如 --help 或解析错误）
        raise e
    except (argparse.ArgumentError, ArgumentParsingError) as e:
        raise ArgumentParsingError(f"参数解析错误: {e}")
    except Exception as e:
        logger.error(f"意外错误: {e}")
        raise ArgumentParsingError(f"参数解析时发生意外错误: {e}")


# 向后兼容的遗留接口
def parse_arguments_legacy(argv: List[str]) -> Dict[str, Any]:
    """
    保持向后兼容的参数解析接口
    
    Args:
        argv: 命令行参数列表
        
    Returns:
        dict: 原有格式的参数字典
        
    Deprecated:
        使用新的 parse_arguments() 函数替代
    """
    import warnings
    warnings.warn(
        "parse_arguments_legacy() is deprecated. Use parse_arguments() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    try:
        cli_args = parse_arguments(argv)
        
        # 转换为旧格式
        return {
            'task_type': cli_args.task_type.value,
            'force_mode': cli_args.force_mode,
            'quick_inference': cli_args.quick_inference,
            'bias_method': cli_args.bias_method,
            'bias_params': cli_args.bias_params,
            'baseline_dir': cli_args.baseline_dir,
            'compensated_dir': cli_args.compensated_dir,
            'vis_output_dir': cli_args.vis_output_dir,
            'vis_config_path': cli_args.vis_config_path,
            'layers_param': cli_args.layers_param,
            'default_project_name': cli_args.project_names[0] if cli_args.project_names else "WNET5q1h2u6l3"
        }
    except ArgumentParsingError as e:
        logger.error(f"参数解析失败: {e}")
        import sys
        sys.exit(1)


def get_project_names(args: CLIArgs, argv: List[str]) -> List[str]:
    """
    获取项目名称列表（兼容性函数）
    
    Args:
        args: 解析后的参数对象
        argv: 原始命令行参数列表（未使用，保持兼容性）
        
    Returns:
        List[str]: 项目名称列表
        
    Deprecated:
        项目名称现在直接包含在 CLIArgs 对象中
    """
    import warnings
    warnings.warn(
        "get_project_names() is deprecated. Use CLIArgs.project_names directly.",
        DeprecationWarning,
        stacklevel=2
    )
    return args.project_names


if __name__ == "__main__":
    # 测试用例
    test_args = parse_arguments(['-e', 'test_project', '--layers', '5'])
    print(f"解析结果: {test_args}")
    print(f"任务类型: {test_args.task_type}")
    print(f"项目名称: {test_args.project_names}")
    print(f"层数: {test_args.layers_param}")
