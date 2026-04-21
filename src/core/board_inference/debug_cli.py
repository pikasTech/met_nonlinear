"""Standalone debug CLI for the staged board inference refactor."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
import logging
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, Optional

from core.external_path_parser import ExternalPath, ExternalPathParser

from .comparison import compare_directory_trees
from .config import clone_config, load_task_config, prepare_debug_config, write_task_config
from .entrypoints import (
    execute_qemu_inference_keil_bench_task,
    execute_qemu_inference_task,
)
from .legacy_adapter import run_legacy_keil_bench_task, run_legacy_qemu_task
from .paths import REPO_ROOT, clone_external_path, ensure_clean_dir
from .types import DebugRun


logger = logging.getLogger(__name__)


def _timestamp() -> str:
    return datetime.now().strftime('%Y%m%d_%H%M%S')


def _build_debug_root(ep_path: ExternalPath, label: str) -> Path:
    return ep_path.full_path / 'debug_cli' / f'{_timestamp()}_{label}'


def _prepare_debug_run(original_ep_path: ExternalPath,
                       debug_root: Path,
                       label: str,
                       config: Dict[str, Any]) -> DebugRun:
    run_root = debug_root / label
    ensure_clean_dir(run_root)
    run_ep_path = clone_external_path(original_ep_path, run_root)
    write_task_config(run_ep_path.config_path, config)
    return DebugRun(label=label, root=run_root, ep_path=run_ep_path)


def _collect_keil_overrides(args: argparse.Namespace) -> Dict[str, Any]:
    return {
        'probe_uid': args.probe_uid,
        'serial_port': args.serial_port,
        'baud_rate': args.baud_rate,
        'target': args.target,
        'program_backend': args.program_backend,
        'programmer': args.programmer,
        'capture_timeout': args.capture_timeout,
        'job_timeout': args.job_timeout,
        'keil_cli_path': args.keil_cli_path,
    }


def _run_legacy_cli(run: DebugRun,
                    flow: str,
                    keil_overrides: Optional[Dict[str, Any]] = None) -> bool:
    relative_ep_path = run.ep_path.full_path.relative_to(REPO_ROOT).as_posix()
    command = [sys.executable, str(REPO_ROOT / 'cli.py'), 'ep']
    if flow == 'keil':
        command.extend(['keil-bench', relative_ep_path])
        overrides = keil_overrides or {}
        option_map = {
            'probe_uid': '--probe-uid',
            'serial_port': '--serial-port',
            'baud_rate': '--baud-rate',
            'target': '--target',
            'program_backend': '--program-backend',
            'programmer': '--programmer',
            'capture_timeout': '--capture-timeout',
            'job_timeout': '--job-timeout',
            'keil_cli_path': '--keil-cli-path',
        }
        for key, option in option_map.items():
            value = overrides.get(key)
            if value is None or (isinstance(value, str) and not value.strip()):
                continue
            command.extend([option, str(value)])
    else:
        command.append(relative_ep_path)

    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
    )
    stdout_log = run.root / 'legacy_cli_stdout.log'
    stderr_log = run.root / 'legacy_cli_stderr.log'
    _write_text(stdout_log, result.stdout)
    _write_text(stderr_log, result.stderr)
    _write_json(
        run.root / 'legacy_cli_process.json',
        {
            'command': command,
            'return_code': result.returncode,
            'stdout_log': stdout_log.as_posix(),
            'stderr_log': stderr_log.as_posix(),
        },
    )
    return result.returncode == 0


def _run_legacy_execution(run: DebugRun,
                          config: Dict[str, Any],
                          flow: str,
                          old_runner: str,
                          keil_overrides: Optional[Dict[str, Any]] = None) -> bool:
    if old_runner == 'cli':
        return _run_legacy_cli(run, flow=flow, keil_overrides=keil_overrides)
    if flow == 'keil':
        return run_legacy_keil_bench_task(run.ep_path, config, keil_overrides=keil_overrides)
    return run_legacy_qemu_task(run.ep_path, config)


def _run_new_execution(run: DebugRun,
                       config: Dict[str, Any],
                       flow: str,
                       keil_overrides: Optional[Dict[str, Any]] = None) -> bool:
    if flow == 'keil':
        return execute_qemu_inference_keil_bench_task(
            run.ep_path,
            config,
            keil_overrides=keil_overrides,
        )
    return execute_qemu_inference_task(run.ep_path, config)


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as file_obj:
        json.dump(payload, file_obj, indent=2, ensure_ascii=False)
        file_obj.write('\n')


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def _parse_ep_path(path_str: str) -> ExternalPath:
    parser = ExternalPathParser(base_dir=REPO_ROOT)
    return parser.parse(path_str)


def _classify_comparison(legacy_success: bool,
                         new_success: bool,
                         artifact_match: bool) -> Dict[str, Any]:
    outcome_match = legacy_success == new_success
    strict_match = bool(legacy_success and new_success and artifact_match)
    behavior_match = bool(outcome_match and (artifact_match or (not legacy_success and not new_success)))

    if legacy_success and new_success:
        classification = 'success_match' if artifact_match else 'artifact_mismatch'
    elif not legacy_success and not new_success:
        classification = 'shared_failure'
    else:
        classification = 'outcome_mismatch'

    return {
        'outcome_match': outcome_match,
        'artifact_match': artifact_match,
        'behavior_match': behavior_match,
        'strict_match': strict_match,
        'classification': classification,
    }


def compare_ep_outputs(ep_path_str: str,
                       flow: str = 'qemu',
                       mode: str = 'generate',
                       old_runner: str = 'cli',
                       keil_overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Run the legacy and refactor paths in isolation, then compare artifacts."""

    original_ep_path = _parse_ep_path(ep_path_str)
    source_config = load_task_config(original_ep_path.config_path)
    prepared_config = prepare_debug_config(
        source_config,
        flow=flow,
        mode=mode,
        keil_overrides=keil_overrides,
    )

    compare_root = _build_debug_root(original_ep_path, 'compare')
    legacy_run = _prepare_debug_run(original_ep_path, compare_root, 'legacy', prepared_config)
    new_run = _prepare_debug_run(original_ep_path, compare_root, 'new', prepared_config)

    legacy_success = _run_legacy_execution(
        legacy_run,
        clone_config(prepared_config),
        flow=flow,
        old_runner=old_runner,
        keil_overrides=clone_config(keil_overrides or {}),
    )
    new_success = _run_new_execution(
        new_run,
        clone_config(prepared_config),
        flow=flow,
        keil_overrides=clone_config(keil_overrides or {}),
    )
    comparison = compare_directory_trees(legacy_run.root, new_run.root)
    classification = _classify_comparison(
        legacy_success=bool(legacy_success),
        new_success=bool(new_success),
        artifact_match=bool(comparison.matches),
    )

    report = {
        'ep_path': ep_path_str,
        'flow': flow,
        'mode': mode,
        'old_runner': old_runner,
        'legacy_success': legacy_success,
        'new_success': new_success,
        'matches': classification['strict_match'],
        'behavior_matches': classification['behavior_match'],
        'outcome_match': classification['outcome_match'],
        'artifact_match': classification['artifact_match'],
        'classification': classification['classification'],
        'compare_root': compare_root.as_posix(),
        'comparison': comparison.to_dict(),
    }
    _write_json(compare_root / 'comparison_report.json', report)
    return report


def run_single_ep_path(ep_path_str: str,
                       flow: str = 'qemu',
                       mode: str = 'generate',
                       runner: str = 'new',
                       keil_overrides: Optional[Dict[str, Any]] = None,
                       old_runner: str = 'cli') -> Dict[str, Any]:
    """Run either the legacy or refactor path in isolation."""

    original_ep_path = _parse_ep_path(ep_path_str)
    source_config = load_task_config(original_ep_path.config_path)
    prepared_config = prepare_debug_config(
        source_config,
        flow=flow,
        mode=mode,
        keil_overrides=keil_overrides,
    )

    debug_root = _build_debug_root(original_ep_path, runner)
    run = _prepare_debug_run(original_ep_path, debug_root, runner, prepared_config)
    if runner == 'legacy':
        success = _run_legacy_execution(
            run,
            clone_config(prepared_config),
            flow=flow,
            old_runner=old_runner,
            keil_overrides=clone_config(keil_overrides or {}),
        )
    elif runner == 'new':
        success = _run_new_execution(
            run,
            clone_config(prepared_config),
            flow=flow,
            keil_overrides=clone_config(keil_overrides or {}),
        )
    else:
        raise ValueError(f'Unsupported runner: {runner}')

    report = {
        'ep_path': ep_path_str,
        'flow': flow,
        'mode': mode,
        'runner': runner,
        'success': bool(success),
        'run_root': run.root.as_posix(),
    }
    _write_json(run.root / 'run_report.json', report)
    return report


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Standalone debug CLI for the staged board_inference refactor',
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    def add_common_arguments(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument(
            'ep_path',
            help='EP 路径，例如 ex_projects/inference/qemu-c-inference/lstm_u16_base',
        )
        subparser.add_argument(
            '--flow',
            choices=['qemu', 'keil'],
            default='qemu',
            help='调试的执行路径，默认 qemu',
        )
        subparser.add_argument(
            '--mode',
            choices=['generate', 'configured'],
            default='generate',
            help='generate 只比对稳定产物；configured 则使用原始 config 动作',
        )
        subparser.add_argument('--probe-uid')
        subparser.add_argument('--serial-port')
        subparser.add_argument('--baud-rate', type=int)
        subparser.add_argument('--target')
        subparser.add_argument('--program-backend')
        subparser.add_argument('--programmer')
        subparser.add_argument('--capture-timeout', type=int)
        subparser.add_argument('--job-timeout', type=int)
        subparser.add_argument('--keil-cli-path')

    compare_parser = subparsers.add_parser(
        'compare',
        help='分别运行 legacy/new 路径并比较产物',
    )
    add_common_arguments(compare_parser)
    compare_parser.add_argument(
        '--old-runner',
        choices=['module', 'cli'],
        default='cli',
        help='legacy 侧使用模块调用还是直接走旧 cli.py 主流程，默认 cli',
    )

    run_new_parser = subparsers.add_parser('run-new', help='单独运行新架构入口')
    add_common_arguments(run_new_parser)

    run_legacy_parser = subparsers.add_parser('run-legacy', help='单独运行 legacy 入口')
    add_common_arguments(run_legacy_parser)
    run_legacy_parser.add_argument(
        '--old-runner',
        choices=['module', 'cli'],
        default='cli',
        help='legacy 侧使用模块调用还是直接走旧 cli.py 主流程，默认 cli',
    )

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = create_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

    keil_overrides = _collect_keil_overrides(args)
    if args.command == 'compare':
        report = compare_ep_outputs(
            ep_path_str=args.ep_path,
            flow=args.flow,
            mode=args.mode,
            old_runner=args.old_runner,
            keil_overrides=keil_overrides,
        )
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0 if report['matches'] else 1

    if args.command == 'run-new':
        report = run_single_ep_path(
            ep_path_str=args.ep_path,
            flow=args.flow,
            mode=args.mode,
            runner='new',
            keil_overrides=keil_overrides,
        )
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0 if report['success'] else 1

    if args.command == 'run-legacy':
        report = run_single_ep_path(
            ep_path_str=args.ep_path,
            flow=args.flow,
            mode=args.mode,
            runner='legacy',
            keil_overrides=keil_overrides,
            old_runner=args.old_runner,
        )
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0 if report['success'] else 1

    parser.error(f'Unknown command: {args.command}')
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
