"""QEMU 工程的轻量 CLI 处理器。"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import threading
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


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


@dataclass
class CommandExecutionResult:
    """单次命令执行结果。"""

    exit_code: int
    stdout: str
    stderr: str
    elapsed_seconds: float
    timed_out: bool = False


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
        project_dir = os.path.join('src', 'tests', 'qemu', 'stm32f405_hello')

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


def _build_project_details(project: QemuProject,
                           gcc_path: str) -> CommandExecutionResult:
    """编译 QEMU 工程并返回详细结果。"""
    os.makedirs(os.path.dirname(project.output_elf), exist_ok=True)

    command = [
        gcc_path,
        '-std=c99',
        '-O2',
        '-mcpu=cortex-m4',
        '-mthumb',
        '-mfloat-abi=soft',
        '-ffreestanding',
        '-ffunction-sections',
        '-fdata-sections',
        '-nostdlib',
        f'-Wl,-T,{project.linker_script}',
        '-Wl,--gc-sections',
        '-o', project.output_elf,
        *project.source_files,
        '-lgcc',
    ]

    logger.info('开始编译 QEMU 工程: %s', os.path.relpath(project.project_dir, REPO_ROOT))
    logger.info('GCC: %s', gcc_path)
    logger.info('链接脚本: %s', project.linker_script)
    logger.info('输出 ELF: %s', project.output_elf)
    logger.info('编译命令: %s', ' '.join(command))

    started_at = time.perf_counter()
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
    )
    elapsed_seconds = time.perf_counter() - started_at
    _log_subprocess_output(result.stdout, result.stderr, warn_if_empty=False)

    if result.returncode != 0:
        logger.error('编译失败，返回码: %s', result.returncode)
        return CommandExecutionResult(
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            elapsed_seconds=elapsed_seconds,
        )

    logger.info('编译成功: %s', project.output_elf)
    return CommandExecutionResult(
        exit_code=0,
        stdout=result.stdout,
        stderr=result.stderr,
        elapsed_seconds=elapsed_seconds,
    )


def _build_project(project: QemuProject, gcc_path: str) -> int:
    """编译 QEMU 工程。"""
    return _build_project_details(project, gcc_path).exit_code


def _stream_reader(stream, sink: List[str], success_patterns: Optional[Sequence[str]],
                   success_event: Optional[threading.Event]) -> None:
    """持续读取子进程输出，并在命中成功模式时发信号。"""
    try:
        for line in iter(stream.readline, ''):
            sink.append(line)
            if success_event is not None and success_patterns:
                if any(pattern in line for pattern in success_patterns):
                    success_event.set()
    finally:
        stream.close()


def _run_project_details(project: QemuProject, qemu_path: str, machine: str,
                         timeout: int,
                         success_patterns: Optional[Sequence[str]] = None) -> CommandExecutionResult:
    """运行 QEMU 工程并返回详细结果。"""
    if not os.path.exists(project.output_elf):
        logger.error('未找到 ELF 文件，请先执行 build 或 build-run: %s', project.output_elf)
        return CommandExecutionResult(
            exit_code=1,
            stdout='',
            stderr=f'未找到 ELF 文件，请先执行 build 或 build-run: {project.output_elf}',
            elapsed_seconds=0.0,
        )

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
    terminated_after_success_output = False
    started_at = time.perf_counter()
    stdout_chunks: List[str] = []
    stderr_chunks: List[str] = []
    success_event = threading.Event() if success_patterns else None
    stdout_thread = threading.Thread(
        target=_stream_reader,
        args=(process.stdout, stdout_chunks, success_patterns, success_event),
        daemon=True,
    )
    stderr_thread = threading.Thread(
        target=_stream_reader,
        args=(process.stderr, stderr_chunks, None, None),
        daemon=True,
    )
    stdout_thread.start()
    stderr_thread.start()

    deadline = started_at + timeout if timeout > 0 else None
    while True:
        if process.poll() is not None:
            break

        if success_event is not None and success_event.is_set():
            terminated_after_success_output = True
            logger.info('QEMU 已捕获成功输出，准备提前终止进程并收集结果')
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            break

        if deadline is not None and time.perf_counter() >= deadline:
            timed_out = True
            logger.info('QEMU 达到超时时间 %s 秒，准备终止进程并收集输出', timeout)
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            break

        time.sleep(0.01)

    stdout_thread.join(timeout=1)
    stderr_thread.join(timeout=1)
    stdout = ''.join(stdout_chunks)
    stderr = ''.join(stderr_chunks)

    elapsed_seconds = time.perf_counter() - started_at

    _log_subprocess_output(stdout, stderr)

    stderr_lower = stderr.lower()
    if 'qemu: fatal' in stderr_lower or 'hardfault' in stderr_lower:
        logger.error('QEMU 运行失败，检测到致命错误')
        return CommandExecutionResult(
            exit_code=1,
            stdout=stdout,
            stderr=stderr,
            elapsed_seconds=elapsed_seconds,
            timed_out=timed_out,
        )

    if terminated_after_success_output and stdout.strip():
        logger.info('QEMU 已输出目标结果并被主动终止，视为成功完成验证')
        return CommandExecutionResult(
            exit_code=0,
            stdout=stdout,
            stderr=stderr,
            elapsed_seconds=elapsed_seconds,
            timed_out=False,
        )

    if timed_out:
        if stdout.strip():
            logger.info('QEMU 在超时前已产生输出，视为成功完成冒烟验证')
            return CommandExecutionResult(
                exit_code=0,
                stdout=stdout,
                stderr=stderr,
                elapsed_seconds=elapsed_seconds,
                timed_out=True,
            )
        logger.error('QEMU 超时且未产生可见输出')
        return CommandExecutionResult(
            exit_code=1,
            stdout=stdout,
            stderr=stderr,
            elapsed_seconds=elapsed_seconds,
            timed_out=True,
        )

    if process.returncode != 0:
        logger.error('QEMU 运行失败，返回码: %s', process.returncode)
        return CommandExecutionResult(
            exit_code=process.returncode,
            stdout=stdout,
            stderr=stderr,
            elapsed_seconds=elapsed_seconds,
        )

    if not stdout.strip():
        logger.error('QEMU 正常退出，但没有产生可见输出')
        return CommandExecutionResult(
            exit_code=1,
            stdout=stdout,
            stderr=stderr,
            elapsed_seconds=elapsed_seconds,
        )

    logger.info('QEMU 运行完成')
    return CommandExecutionResult(
        exit_code=0,
        stdout=stdout,
        stderr=stderr,
        elapsed_seconds=elapsed_seconds,
    )


def _run_project(project: QemuProject, qemu_path: str, machine: str,
                 timeout: int) -> int:
    """运行 QEMU 工程。"""
    return _run_project_details(project, qemu_path, machine, timeout).exit_code


def _describe_project(project: QemuProject) -> None:
    """打印工程解析结果。"""
    relative_dir = os.path.relpath(project.project_dir, REPO_ROOT)
    logger.info('工程目录: %s', relative_dir)
    logger.info('源文件: %s', ', '.join(os.path.basename(path) for path in project.source_files))
    logger.info('链接脚本: %s', os.path.basename(project.linker_script))
    logger.info('目标 ELF: %s', os.path.relpath(project.output_elf, REPO_ROOT))


def execute_qemu_workflow(action: str,
                          project_dir: Optional[str] = None,
                          machine: str = 'olimex-stm32-h405',
                          timeout: int = 5,
                          output_path: Optional[str] = None,
                          qemu_path_override: Optional[str] = None,
                          gcc_path_override: Optional[str] = None,
                          linker_script: Optional[str] = None,
                          success_patterns: Optional[Sequence[str]] = None) -> Dict[str, Any]:
    """执行 QEMU 工作流并返回结构化结果。"""
    result: Dict[str, Any] = {
        'action': action,
        'exit_code': 1,
    }

    if action == 'list':
        projects = _find_qemu_projects(REPO_ROOT)
        result['projects'] = projects
        if not projects:
            logger.error('仓库中未找到包含 .c 和 .ld 的 QEMU 工程目录')
            return result

        logger.info('发现 %s 个 QEMU 工程目录:', len(projects))
        for project in projects:
            logger.info('- %s', project)
        result['exit_code'] = 0
        return result

    resolved_project_dir = _resolve_project_dir(project_dir)
    project = _discover_project(
        resolved_project_dir,
        output_path,
        linker_script,
    )
    _describe_project(project)
    result['project'] = {
        'project_dir': os.path.relpath(project.project_dir, REPO_ROOT),
        'output_elf': os.path.relpath(project.output_elf, REPO_ROOT),
        'linker_script': os.path.relpath(project.linker_script, REPO_ROOT),
        'source_files': [os.path.relpath(path, REPO_ROOT) for path in project.source_files],
    }

    if action in {'build', 'build-run'}:
        gcc_path = _resolve_executable(gcc_path_override, 'arm-none-eabi-gcc', GCC_CANDIDATES)
        logger.info('ARM GCC 可执行文件: %s', gcc_path)
        build_result = _build_project_details(project, gcc_path)
        result['build'] = asdict(build_result)
        if build_result.exit_code != 0:
            result['exit_code'] = build_result.exit_code
            return result

    if action in {'run', 'build-run'}:
        qemu_path = _resolve_executable(qemu_path_override, 'qemu-system-arm', QEMU_CANDIDATES)
        logger.info('QEMU 可执行文件: %s', qemu_path)
        run_result = _run_project_details(project, qemu_path, machine, timeout, success_patterns)
        result['run'] = asdict(run_result)
        result['exit_code'] = run_result.exit_code
        return result

    if action == 'build':
        result['exit_code'] = 0
        return result

    logger.error('不支持的 QEMU 操作: %s', action)
    return result


def handle_qemu_command(args) -> int:
    """处理 QEMU 子命令。"""
    try:
        result = execute_qemu_workflow(
            action=args.qemu_action,
            project_dir=args.qemu_project_dir,
            machine=args.qemu_machine,
            timeout=args.qemu_timeout,
            output_path=args.qemu_output_path,
            qemu_path_override=args.qemu_qemu_path,
            gcc_path_override=args.qemu_gcc_path,
            linker_script=args.qemu_linker_script,
        )
        return int(result.get('exit_code', 1))
    except Exception as exc:
        logger.exception('QEMU 子命令执行失败: %s', exc)
        return 1