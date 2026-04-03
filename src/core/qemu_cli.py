"""QEMU 工程的轻量 CLI 处理器。"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple


logger = logging.getLogger(__name__)

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

QEMU_CANDIDATES = [
    r'C:\Program Files\qemu\qemu-system-arm.exe',
    r'C:\Program Files\QEMU\qemu-system-arm.exe',
]

GCC_CANDIDATES = [
    r'C:\Program Files (x86)\Arm GNU Toolchain arm-none-eabi\14.2 rel1\bin\arm-none-eabi-gcc.exe',
    r'C:\Program Files\Arm GNU Toolchain arm-none-eabi\14.2 rel1\bin\arm-none-eabi-gcc.exe',
    r'C:\Program Files (x86)\GNU Arm Embedded Toolchain\10 2021.10\bin\arm-none-eabi-gcc.exe',
]


@dataclass
class QemuProject:
    """QEMU 工程解析结果。"""

    project_dir: str
    source_files: List[str]
    linker_script: str
    output_elf: str


def _resolve_executable(user_path: Optional[str], program_name: str,
                        candidates: Iterable[str]) -> str:
    """解析可执行文件路径。"""
    if user_path:
        resolved = os.path.abspath(user_path)
        if os.path.exists(resolved):
            return resolved
        raise FileNotFoundError(f'指定的 {program_name} 不存在: {resolved}')

    from_path = shutil.which(program_name)
    if from_path:
        return from_path

    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate

    raise FileNotFoundError(
        f'未找到 {program_name}，请将其加入 PATH，或通过参数显式指定路径'
    )


def _find_qemu_projects(root_dir: str) -> List[str]:
    """搜索仓库内可用的 QEMU 工程目录。"""
    project_dirs: List[str] = []

    for current_root, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [
            dirname for dirname in dirnames
            if dirname not in {'__pycache__', '.git', '.venv', 'node_modules'}
        ]

        has_source = any(name.endswith('.c') for name in filenames)
        has_linker = any(name.endswith('.ld') for name in filenames)
        if has_source and has_linker:
            project_dirs.append(os.path.relpath(current_root, root_dir))

    return sorted(project_dirs)


def _resolve_project_dir(project_dir: Optional[str]) -> str:
    """解析工程目录。"""
    if not project_dir:
        project_dir = 'test_qemu'

    resolved = project_dir
    if not os.path.isabs(resolved):
        resolved = os.path.join(REPO_ROOT, resolved)

    resolved = os.path.abspath(resolved)
    if not os.path.isdir(resolved):
        raise FileNotFoundError(f'QEMU 工程目录不存在: {resolved}')
    return resolved


def _resolve_linker_script(project_dir: str,
                           linker_script: Optional[str]) -> str:
    """解析链接脚本。"""
    if linker_script:
        resolved = linker_script
        if not os.path.isabs(resolved):
            resolved = os.path.join(project_dir, resolved)
        resolved = os.path.abspath(resolved)
        if os.path.exists(resolved):
            return resolved
        raise FileNotFoundError(f'链接脚本不存在: {resolved}')

    linker_files = sorted(
        os.path.join(project_dir, filename)
        for filename in os.listdir(project_dir)
        if filename.endswith('.ld')
    )
    if not linker_files:
        raise FileNotFoundError(f'工程目录中未找到 .ld 链接脚本: {project_dir}')
    if len(linker_files) > 1:
        raise ValueError(
            f'工程目录中存在多个 .ld 文件，请通过 --linker-script 指定: {project_dir}'
        )
    return linker_files[0]


def _choose_output_elf(project_dir: str, source_files: List[str],
                       output_path: Optional[str]) -> str:
    """决定输出 ELF 路径。"""
    if output_path:
        resolved = output_path
        if not os.path.isabs(resolved):
            resolved = os.path.join(project_dir, resolved)
        return os.path.abspath(resolved)

    existing_elfs = sorted(
        os.path.join(project_dir, filename)
        for filename in os.listdir(project_dir)
        if filename.endswith('.elf')
    )
    if len(existing_elfs) == 1:
        return existing_elfs[0]

    primary_source = source_files[0]
    for source_file in source_files:
        if os.path.splitext(os.path.basename(source_file))[0] != 'startup':
            primary_source = source_file
            break

    primary_stem = os.path.splitext(os.path.basename(primary_source))[0]
    return os.path.join(project_dir, f'{primary_stem}.elf')


def _discover_project(project_dir: str, output_path: Optional[str],
                      linker_script: Optional[str]) -> QemuProject:
    """发现工程文件。"""
    source_files = sorted(
        os.path.join(project_dir, filename)
        for filename in os.listdir(project_dir)
        if filename.endswith('.c')
    )
    if not source_files:
        raise FileNotFoundError(f'工程目录中未找到 .c 源文件: {project_dir}')

    resolved_linker = _resolve_linker_script(project_dir, linker_script)
    output_elf = _choose_output_elf(project_dir, source_files, output_path)
    return QemuProject(
        project_dir=project_dir,
        source_files=source_files,
        linker_script=resolved_linker,
        output_elf=output_elf,
    )


def _log_subprocess_output(stdout: str, stderr: str,
                           warn_if_empty: bool = True) -> None:
    """输出子进程日志。"""
    if stdout.strip():
        logger.info('stdout:\n%s', stdout.rstrip())
    if stderr.strip():
        logger.warning('stderr:\n%s', stderr.rstrip())
    if warn_if_empty and not stdout.strip() and not stderr.strip():
        logger.warning('命令执行完成，但没有产生任何输出')


def _build_project(project: QemuProject, gcc_path: str) -> int:
    """编译 QEMU 工程。"""
    os.makedirs(os.path.dirname(project.output_elf), exist_ok=True)

    command = [
        gcc_path,
        '-mcpu=cortex-m4',
        '-mthumb',
        '-mfloat-abi=soft',
        '-ffreestanding',
        '-nostdlib',
        f'-Wl,-T,{project.linker_script}',
        '-Wl,--gc-sections',
        '-o', project.output_elf,
        *project.source_files,
    ]

    logger.info('开始编译 QEMU 工程: %s', os.path.relpath(project.project_dir, REPO_ROOT))
    logger.info('GCC: %s', gcc_path)
    logger.info('链接脚本: %s', project.linker_script)
    logger.info('输出 ELF: %s', project.output_elf)
    logger.info('编译命令: %s', ' '.join(command))

    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
    )
    _log_subprocess_output(result.stdout, result.stderr, warn_if_empty=False)

    if result.returncode != 0:
        logger.error('编译失败，返回码: %s', result.returncode)
        return result.returncode

    logger.info('编译成功: %s', project.output_elf)
    return 0


def _run_project(project: QemuProject, qemu_path: str, machine: str,
                 timeout: int) -> int:
    """运行 QEMU 工程。"""
    if not os.path.exists(project.output_elf):
        logger.error('未找到 ELF 文件，请先执行 build 或 build-run: %s', project.output_elf)
        return 1

    command = [
        qemu_path,
        '-M', machine,
        '-kernel', project.output_elf,
        '-display', 'none',
        '-serial', 'stdio',
        '-monitor', 'none',
    ]

    logger.info('开始运行 QEMU 工程: %s', os.path.relpath(project.project_dir, REPO_ROOT))
    logger.info('QEMU: %s', qemu_path)
    logger.info('机器型号: %s', machine)
    logger.info('运行命令: %s', ' '.join(command))

    process = subprocess.Popen(
        command,
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8',
        errors='replace',
    )

    timed_out = False
    try:
        if timeout > 0:
            stdout, stderr = process.communicate(timeout=timeout)
        else:
            stdout, stderr = process.communicate()
    except subprocess.TimeoutExpired:
        timed_out = True
        logger.info('QEMU 达到超时时间 %s 秒，准备终止进程并收集输出', timeout)
        process.terminate()
        try:
            stdout, stderr = process.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()

    _log_subprocess_output(stdout, stderr)

    stderr_lower = stderr.lower()
    if 'qemu: fatal' in stderr_lower or 'hardfault' in stderr_lower:
        logger.error('QEMU 运行失败，检测到致命错误')
        return 1

    if timed_out:
        if stdout.strip():
            logger.info('QEMU 在超时前已产生输出，视为成功完成冒烟验证')
            return 0
        logger.error('QEMU 超时且未产生可见输出')
        return 1

    if process.returncode != 0:
        logger.error('QEMU 运行失败，返回码: %s', process.returncode)
        return process.returncode

    if not stdout.strip():
        logger.error('QEMU 正常退出，但没有产生可见输出')
        return 1

    logger.info('QEMU 运行完成')
    return 0


def _describe_project(project: QemuProject) -> None:
    """打印工程解析结果。"""
    relative_dir = os.path.relpath(project.project_dir, REPO_ROOT)
    logger.info('工程目录: %s', relative_dir)
    logger.info('源文件: %s', ', '.join(os.path.basename(path) for path in project.source_files))
    logger.info('链接脚本: %s', os.path.basename(project.linker_script))
    logger.info('目标 ELF: %s', os.path.relpath(project.output_elf, REPO_ROOT))


def handle_qemu_command(args) -> int:
    """处理 QEMU 子命令。"""
    try:
        qemu_path = _resolve_executable(args.qemu_qemu_path, 'qemu-system-arm', QEMU_CANDIDATES)
        gcc_path = _resolve_executable(args.qemu_gcc_path, 'arm-none-eabi-gcc', GCC_CANDIDATES)

        logger.info('QEMU 可执行文件: %s', qemu_path)
        logger.info('ARM GCC 可执行文件: %s', gcc_path)

        if args.qemu_action == 'list':
            projects = _find_qemu_projects(REPO_ROOT)
            if not projects:
                logger.error('仓库中未找到包含 .c 和 .ld 的 QEMU 工程目录')
                return 1

            logger.info('发现 %s 个 QEMU 工程目录:', len(projects))
            for project in projects:
                logger.info('- %s', project)
            return 0

        project_dir = _resolve_project_dir(args.qemu_project_dir)
        project = _discover_project(
            project_dir,
            args.qemu_output_path,
            args.qemu_linker_script,
        )
        _describe_project(project)

        if args.qemu_action == 'build':
            return _build_project(project, gcc_path)

        if args.qemu_action == 'run':
            return _run_project(project, qemu_path, args.qemu_machine, args.qemu_timeout)

        if args.qemu_action == 'build-run':
            build_code = _build_project(project, gcc_path)
            if build_code != 0:
                return build_code
            return _run_project(project, qemu_path, args.qemu_machine, args.qemu_timeout)

        logger.error('不支持的 QEMU 操作: %s', args.qemu_action)
        return 1
    except Exception as exc:
        logger.exception('QEMU 子命令执行失败: %s', exc)
        return 1