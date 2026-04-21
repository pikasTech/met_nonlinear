"""Shared qemu/keil benchmark helpers for board inference models.

This module is intentionally copied out of the legacy qemu-c-inference task so
new model implementations can reuse the same platform / validation / comparison
plumbing without importing `core.lstm_qemu_ep_task` at runtime.
"""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence
from xml.etree import ElementTree as ET

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from ..paths import REPO_ROOT

logger = logging.getLogger(__name__)
QEMU_HELLO_TEMPLATE_DIR = REPO_ROOT / 'src' / 'tests' / 'qemu' / 'stm32f405_hello'
KEIL_BENCHMARK_BASE_DIR = REPO_ROOT / 'src' / 'tests' / 'keil_projects' / 'met_keil_405'
KEIL_BENCHMARK_BASE_MDK_DIR = KEIL_BENCHMARK_BASE_DIR / 'MDK-ARM'
KEIL_BENCHMARK_BASE_UVPROJX = KEIL_BENCHMARK_BASE_MDK_DIR / 'Electrochemical geophone.uvprojx'
KEIL_BENCHMARK_BASE_UVOPTX = KEIL_BENCHMARK_BASE_MDK_DIR / 'Electrochemical geophone.uvoptx'

DATASET_OVERRIDE_FIELDS = (
    'dataset_type',
    'data_path',
    'sample_rate',
    'time_clipped_s',
    'target_sweep',
    'feature_range',
    'use_scale',
    'use_cache_features',
    'data_base_path',
)

@dataclass
class ValidationRecord:
    """单条验证波形记录。"""

    record_id: str
    magnitude: float
    frequency: float
    input_sequence: List[List[float]]
    target_sequence: List[float]
    tf_output_sequence: List[float]

@dataclass
class ValidationArtifacts:
    """验证任务所需的输入、参考输出与元数据。"""

    dataset_type: str
    full_data_path: str
    sample_rate: float
    time_window: Dict[str, float]
    input_data_range: float
    output_data_range: float
    loaded_weights_path: Path
    records: List[ValidationRecord]
    tf_debug_sequences: Dict[str, List[Any]] = field(default_factory=dict)

    @property
    def record_count(self) -> int:
        return len(self.records)

    @property
    def seq_len(self) -> int:
        if not self.records:
            return 0
        return len(self.records[0].tf_output_sequence)

def _run_keil_build_job(project_file: Path,
                        keil_config: Dict[str, Any]) -> Dict[str, Any]:
    keil_cli_path = _resolve_keil_cli_path(keil_config)
    request = _run_keil_cli_json_command([
        'py', '-3', str(keil_cli_path), 'build',
        '-p', str(project_file),
        '-t', str(keil_config['target']),
    ])
    return _wait_keil_job(
        keil_cli_path=keil_cli_path,
        job_id=str(request['job_id']),
        job_timeout=int(keil_config['job_timeout']),
    )

def _run_keil_program_job(project_file: Path,
                          keil_config: Dict[str, Any]) -> Dict[str, Any]:
    if not str(keil_config.get('probe_uid', '')).strip():
        raise ValueError('Keil bench 缺少 probe_uid，请在 keil_config 或 CLI 中显式提供')

    keil_cli_path = _resolve_keil_cli_path(keil_config)
    command = [
        'py', '-3', str(keil_cli_path), 'program',
        '-p', str(project_file),
        '-m', str(keil_config['programmer']),
        '--program-backend', str(keil_config['program_backend']),
        '-u', str(keil_config['probe_uid']),
        '-t', str(keil_config['target']),
    ]
    request = _run_keil_cli_json_command(command)
    return _wait_keil_job(
        keil_cli_path=keil_cli_path,
        job_id=str(request['job_id']),
        job_timeout=int(keil_config['job_timeout']),
    )

def _resolve_keil_cli_path(keil_config: Dict[str, Any]) -> Path:
    keil_cli_path = Path(str(keil_config['keil_cli_path']))
    if not keil_cli_path.exists():
        raise FileNotFoundError(f'未找到 keil-cli.py: {keil_cli_path}')
    return keil_cli_path

def _run_keil_cli_json_command(command: Sequence[str]) -> Dict[str, Any]:
    completed = subprocess.run(
        list(command),
        check=False,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f'Keil CLI 命令失败: {" ".join(command)}\nstdout={completed.stdout}\nstderr={completed.stderr}'
        )
    stdout = completed.stdout.strip()
    if not stdout:
        raise RuntimeError(f'Keil CLI 命令无输出: {" ".join(command)}')
    try:
        return json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f'Keil CLI 输出不是合法 JSON: {stdout}') from exc

def _wait_keil_job(keil_cli_path: Path,
                   job_id: str,
                   job_timeout: int) -> Dict[str, Any]:
    start_time = time.monotonic()
    last_status: Optional[str] = None
    while True:
        job_status = _run_keil_cli_json_command([
            'py', '-3', str(keil_cli_path), 'job-status', job_id,
        ])
        status_text = str(job_status.get('status', 'unknown'))
        if status_text != last_status:
            logger.info('Keil job %s status=%s', job_id, status_text)
            last_status = status_text

        if status_text == 'completed':
            return job_status
        if status_text in {'failed', 'error', 'cancelled'}:
            return job_status
        if time.monotonic() - start_time > job_timeout:
            raise TimeoutError(f'等待 Keil job 超时: {job_id}')
        time.sleep(1.0)

def _start_keil_serial_capture(output_dir: Path,
                               serial_port: str,
                               baud_rate: int,
                               capture_timeout: int,
                               success_markers: Sequence[str]) -> Dict[str, Any]:
    if not serial_port.strip():
        raise ValueError('Keil bench 缺少 serial_port，请在 keil_config 或 CLI 中显式提供')

    capture_dir = output_dir / '.keil_capture'
    capture_dir.mkdir(parents=True, exist_ok=True)
    serial_monitor_paths = _resolve_serial_monitor_paths()
    if serial_monitor_paths is not None:
        _ensure_serial_monitor_server(serial_monitor_paths)
        _run_serial_monitor_json_command(
            [*serial_monitor_paths['command_prefix'], 'monitor', 'stop'],
            cwd=serial_monitor_paths['skill_dir'],
            allow_failure=True,
        )
        _run_serial_monitor_json_command(
            [
                *serial_monitor_paths['command_prefix'],
                'monitor',
                'start',
                '-p',
                serial_port,
                '-b',
                str(baud_rate),
            ],
            cwd=serial_monitor_paths['skill_dir'],
        )
        time.sleep(0.5)
        return {
            'mode': 'serial-monitor',
            'skill_dir': serial_monitor_paths['skill_dir'],
            'command_prefix': serial_monitor_paths['command_prefix'],
            'capture_start_time': datetime.now().astimezone() - timedelta(seconds=2),
            'capture_timeout': capture_timeout,
            'serial_port': serial_port,
            'baud_rate': baud_rate,
            'success_markers': [str(marker) for marker in success_markers],
            'capture_dir': capture_dir,
            'result_path': capture_dir / 'capture_result.json',
            'all_jsonl_path': capture_dir / 'capture_all.jsonl',
            'jsonl_path': output_dir / 'keil_serial_raw.jsonl',
            'text_path': output_dir / 'keil_serial_stream.txt',
        }

    script_path = capture_dir / 'capture_serial.ps1'
    result_path = capture_dir / 'capture_result.json'
    jsonl_path = output_dir / 'keil_serial_raw.jsonl'
    text_path = output_dir / 'keil_serial_stream.txt'

    _write_text(script_path, _render_keil_serial_capture_script())
    if result_path.exists():
        result_path.unlink()
    if jsonl_path.exists():
        jsonl_path.unlink()
    if text_path.exists():
        text_path.unlink()

    command = [
        'powershell',
        '-NoProfile',
        '-ExecutionPolicy',
        'Bypass',
        '-File',
        str(script_path),
        '-PortName',
        serial_port,
        '-BaudRate',
        str(baud_rate),
        '-TimeoutSeconds',
        str(capture_timeout),
        '-ResultPath',
        str(result_path),
        '-JsonlPath',
        str(jsonl_path),
        '-TextPath',
        str(text_path),
    ]
    for marker in success_markers:
        command.extend(['-SuccessMarker', str(marker)])

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8',
        errors='replace',
    )
    time.sleep(0.5)
    return {
        'process': process,
        'result_path': result_path,
        'jsonl_path': jsonl_path,
        'text_path': text_path,
        'script_path': script_path,
        'command': command,
    }

def _finish_keil_serial_capture(capture_state: Dict[str, Any],
                                timeout_seconds: int) -> Dict[str, Any]:
    if capture_state.get('mode') == 'serial-monitor':
        return _finish_keil_serial_capture_with_serial_monitor(capture_state, timeout_seconds)

    process: subprocess.Popen[str] = capture_state['process']
    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
        raise TimeoutError(f'等待串口抓取进程结束超时: stdout={stdout}\nstderr={stderr}')

    result_path = Path(capture_state['result_path'])
    if process.returncode != 0:
        raise RuntimeError(
            f'串口抓取失败，returncode={process.returncode}\nstdout={stdout}\nstderr={stderr}'
        )
    if not result_path.exists():
        raise FileNotFoundError(f'串口抓取结果文件缺失: {result_path}')

    with open(result_path, 'r', encoding='utf-8') as file_obj:
        result = json.load(file_obj)
    result['stdout'] = stdout
    result['stderr'] = stderr
    return result

def _resolve_serial_monitor_paths() -> Optional[Dict[str, Any]]:
    skill_dir = Path.home() / '.agents' / 'skills' / 'serial-monitor'
    tsx_cmd = skill_dir / 'node_modules' / '.bin' / 'tsx.cmd'
    cli_path = skill_dir / 'scripts' / 'serial-monitor-cli.ts'
    if not skill_dir.exists() or not tsx_cmd.exists() or not cli_path.exists():
        return None
    return {
        'skill_dir': skill_dir,
        'command_prefix': [str(tsx_cmd), str(cli_path)],
    }

def _ensure_serial_monitor_server(serial_monitor_paths: Dict[str, Any]) -> None:
    status_result = _run_serial_monitor_json_command(
        [*serial_monitor_paths['command_prefix'], 'server', 'status'],
        cwd=serial_monitor_paths['skill_dir'],
        allow_failure=True,
    )
    if bool(status_result.get('success', False)):
        return

    start_result = _run_serial_monitor_json_command(
        [*serial_monitor_paths['command_prefix'], 'server', 'start'],
        cwd=serial_monitor_paths['skill_dir'],
    )
    if not bool(start_result.get('success', False)):
        raise RuntimeError(f'无法启动 serial-monitor 服务: {start_result}')

def _run_serial_monitor_json_command(command: Sequence[str],
                                     cwd: Path,
                                     allow_failure: bool = False) -> Dict[str, Any]:
    completed = subprocess.run(
        list(command),
        cwd=str(cwd),
        check=False,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
    )
    stdout = completed.stdout.strip()
    if completed.returncode != 0 and not allow_failure:
        raise RuntimeError(
            f'serial-monitor 命令失败: {" ".join(command)}\nstdout={completed.stdout}\nstderr={completed.stderr}'
        )
    if not stdout:
        if allow_failure:
            return {
                'success': False,
                'return_code': completed.returncode,
                'stdout': completed.stdout,
                'stderr': completed.stderr,
            }
        raise RuntimeError(f'serial-monitor 命令无输出: {" ".join(command)}')
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f'serial-monitor 输出不是合法 JSON: {stdout}') from exc
    payload['_return_code'] = completed.returncode
    payload['_stderr'] = completed.stderr
    return payload

def _finish_keil_serial_capture_with_serial_monitor(capture_state: Dict[str, Any],
                                                    timeout_seconds: int) -> Dict[str, Any]:
    skill_dir = Path(capture_state['skill_dir'])
    command_prefix = list(capture_state['command_prefix'])
    all_jsonl_path = Path(capture_state['all_jsonl_path'])
    jsonl_path = Path(capture_state['jsonl_path'])
    text_path = Path(capture_state['text_path'])
    result_path = Path(capture_state['result_path'])
    capture_start_time: datetime = capture_state['capture_start_time']
    success_markers = [str(marker) for marker in capture_state.get('success_markers', [])]

    fetch_result: Dict[str, Any] = {}
    filtered_entries: List[Dict[str, Any]] = []
    stream_text = ''
    start_time = time.monotonic()
    while True:
        fetch_result = _run_serial_monitor_json_command(
            [
                *command_prefix,
                'fetch',
                '--all',
                '--format',
                'jsonl',
                '--no-dedup',
                '--out',
                str(all_jsonl_path),
            ],
            cwd=skill_dir,
        )
        filtered_entries = _filter_serial_monitor_entries(
            jsonl_path=all_jsonl_path,
            capture_start_time=capture_start_time,
            expected_port=str(capture_state['serial_port']),
        )
        stream_text = ''.join(str(entry.get('data', '')) for entry in filtered_entries)
        if stream_text and all(marker in stream_text for marker in success_markers):
            break
        if time.monotonic() - start_time > timeout_seconds:
            break
        time.sleep(1.0)

    _run_serial_monitor_json_command(
        [*command_prefix, 'monitor', 'stop'],
        cwd=skill_dir,
        allow_failure=True,
    )

    _write_serial_monitor_capture_files(
        filtered_entries=filtered_entries,
        jsonl_path=jsonl_path,
        text_path=text_path,
    )

    matched_markers = [marker for marker in success_markers if marker in stream_text]
    missing_markers = [marker for marker in success_markers if marker not in stream_text]
    timed_out = bool(missing_markers)
    result = {
        'status': 'completed' if not timed_out else 'timeout',
        'port': str(capture_state['serial_port']),
        'baud_rate': int(capture_state['baud_rate']),
        'timeout_seconds': int(capture_state['capture_timeout']),
        'timed_out': timed_out,
        'record_count': len(filtered_entries),
        'stream_length': len(stream_text),
        'matched_success_markers': matched_markers,
        'missing_success_markers': missing_markers,
        'result_path': str(result_path),
        'jsonl_path': str(jsonl_path),
        'text_path': str(text_path),
        'error': None,
        'fetch_result': fetch_result,
    }
    _write_json(result_path, result)
    return result

def _filter_serial_monitor_entries(jsonl_path: Path,
                                   capture_start_time: datetime,
                                   expected_port: str) -> List[Dict[str, Any]]:
    if not jsonl_path.exists():
        return []

    filtered_entries: List[Dict[str, Any]] = []
    with open(jsonl_path, 'r', encoding='utf-8') as file_obj:
        for raw_line in file_obj:
            line = raw_line.strip()
            if not line:
                continue
            entry = json.loads(line)
            if str(entry.get('port', '')) != expected_port:
                continue
            timestamp_raw = str(entry.get('timestamp', ''))
            try:
                timestamp = datetime.strptime(timestamp_raw, '%Y-%m-%dT%H:%M:%S.%f%z')
            except ValueError:
                continue
            if timestamp >= capture_start_time:
                filtered_entries.append(entry)
    return filtered_entries

def _write_serial_monitor_capture_files(filtered_entries: Sequence[Dict[str, Any]],
                                        jsonl_path: Path,
                                        text_path: Path) -> None:
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with open(jsonl_path, 'w', encoding='utf-8') as file_obj:
        for entry in filtered_entries:
            file_obj.write(json.dumps(entry, ensure_ascii=False))
            file_obj.write('\n')

    stream_text = ''.join(str(entry.get('data', '')) for entry in filtered_entries)
    text_path.parent.mkdir(parents=True, exist_ok=True)
    text_path.write_text(stream_text, encoding='utf-8')

def _render_keil_serial_capture_script() -> str:
    return r"""param(
    [Parameter(Mandatory = $true)][string]$PortName,
    [Parameter(Mandatory = $true)][int]$BaudRate,
    [Parameter(Mandatory = $true)][int]$TimeoutSeconds,
    [Parameter(Mandatory = $true)][string]$ResultPath,
    [Parameter(Mandatory = $true)][string]$JsonlPath,
    [Parameter(Mandatory = $true)][string]$TextPath,
    [string[]]$SuccessMarker = @('validation_complete=1')
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$records = New-Object System.Collections.Generic.List[object]
$streamBuilder = New-Object System.Text.StringBuilder
$matchedMarkers = New-Object System.Collections.Generic.List[string]
$port = New-Object System.IO.Ports.SerialPort $PortName, $BaudRate, ([System.IO.Ports.Parity]::None), 8, ([System.IO.Ports.StopBits]::One)
$port.Encoding = [System.Text.Encoding]::ASCII
$port.ReadTimeout = 200
$port.WriteTimeout = 200
$port.DtrEnable = $false
$port.RtsEnable = $false
$status = 'completed'
$errorMessage = $null
$timedOut = $false
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

try {
    $port.Open()
    $port.DiscardInBuffer()
    while ($stopwatch.Elapsed.TotalSeconds -lt $TimeoutSeconds) {
        $chunk = $port.ReadExisting()
        if (-not [string]::IsNullOrEmpty($chunk)) {
            [void]$streamBuilder.Append($chunk)
            $records.Add([ordered]@{
                timestamp = [DateTimeOffset]::Now.ToString('yyyy-MM-ddTHH:mm:ss.fffzzz')
                port = $PortName
                data = $chunk
            })
            $currentStream = $streamBuilder.ToString()
            $allMatched = $true
            foreach ($marker in $SuccessMarker) {
                if ($currentStream.Contains($marker)) {
                    if (-not $matchedMarkers.Contains($marker)) {
                        $matchedMarkers.Add($marker)
                    }
                } else {
                    $allMatched = $false
                }
            }
            if ($allMatched) {
                break
            }
        } else {
            Start-Sleep -Milliseconds 50
        }
    }
    if ($stopwatch.Elapsed.TotalSeconds -ge $TimeoutSeconds -and $matchedMarkers.Count -lt $SuccessMarker.Count) {
        $timedOut = $true
        $status = 'timeout'
    }
} catch {
    $status = 'error'
    $errorMessage = $_.Exception.Message
} finally {
    if ($port.IsOpen) {
        $port.Close()
    }
}

$streamText = $streamBuilder.ToString()
[System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($ResultPath)) | Out-Null
[System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($JsonlPath)) | Out-Null
[System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($TextPath)) | Out-Null
[System.IO.File]::WriteAllText($TextPath, $streamText, $utf8NoBom)

$jsonlLines = @()
if ($records.Count -gt 0) {
    $jsonlLines = @(
        foreach ($record in $records) {
            $record | ConvertTo-Json -Compress -Depth 4
        }
    )
}
[System.IO.File]::WriteAllLines($JsonlPath, [string[]]$jsonlLines, $utf8NoBom)

$missingMarkers = @()
foreach ($marker in $SuccessMarker) {
    if (-not $matchedMarkers.Contains($marker)) {
        $missingMarkers += $marker
    }
}

$result = [ordered]@{
    status = $status
    port = $PortName
    baud_rate = $BaudRate
    timeout_seconds = $TimeoutSeconds
    timed_out = $timedOut
    record_count = $records.Count
    stream_length = $streamText.Length
    matched_success_markers = @($matchedMarkers)
    missing_success_markers = @($missingMarkers)
    result_path = $ResultPath
    jsonl_path = $JsonlPath
    text_path = $TextPath
    error = $errorMessage
}

$resultJson = $result | ConvertTo-Json -Depth 6
[System.IO.File]::WriteAllText($ResultPath, $resultJson, $utf8NoBom)
Write-Output $resultJson

if ($status -eq 'error') {
    exit 1
}
exit 0
"""

def generate_keil_project(ep_path: ExternalPath,
                          qemu_project_dir: Path,
                          overwrite: bool) -> Path:
    """在 EP 目录下生成可直接用于真机 benchmark 的 Keil 工程。"""
    keil_project_dir = ep_path.full_path / 'keil_project'
    application_dir = keil_project_dir / 'Application'
    mdk_dir = keil_project_dir / 'MDK-ARM'
    project_file = mdk_dir / KEIL_BENCHMARK_BASE_UVPROJX.name
    uvoptx_file = mdk_dir / KEIL_BENCHMARK_BASE_UVOPTX.name

    if keil_project_dir.exists() and not overwrite:
        raise FileExistsError(f'Keil 工程目录已存在且未允许覆盖: {keil_project_dir}')

    application_dir.mkdir(parents=True, exist_ok=True)
    mdk_dir.mkdir(parents=True, exist_ok=True)

    _write_text(application_dir / 'main.h', _render_keil_benchmark_main_h())
    _write_text(application_dir / 'benchmark_keil_port.h', _render_keil_benchmark_port_h())
    _write_text(application_dir / 'benchmark_keil_port.c', _render_keil_benchmark_port_c())
    _write_text(application_dir / 'stm32f4xx_it.h', _render_keil_benchmark_it_h())
    _write_text(application_dir / 'stm32f4xx_it.c', _render_keil_benchmark_it_c())

    _write_keil_benchmark_uvprojx(
        project_file=project_file,
        mdk_dir=mdk_dir,
        application_dir=application_dir,
        qemu_project_dir=qemu_project_dir,
    )

    if KEIL_BENCHMARK_BASE_UVOPTX.exists():
        shutil.copy2(KEIL_BENCHMARK_BASE_UVOPTX, uvoptx_file)

    return keil_project_dir

def _make_dual_platform_benchmark_c(main_c: str) -> str:
    adapted = main_c.replace('_QEMU_VALIDATION', '_BENCHMARK_VALIDATION')
    adapted = _replace_once(
        adapted,
        '#include "model_data.h"\n',
        '#include "model_data.h"\n\n#if defined(BENCHMARK_PLATFORM_KEIL)\n#include "benchmark_keil_port.h"\n#endif\n',
    )
    adapted = _replace_once(
        adapted,
        'static void uart_init(void)\n{\n    RCC_APB2ENR |= RCC_APB2ENR_USART1EN;\n    USART1_BRR = 0x05B2u;\n    USART1_CR1 = USART_CR1_UE | USART_CR1_TE;\n}\n',
        'static void uart_init(void)\n{\n#if defined(BENCHMARK_PLATFORM_KEIL)\n    benchmark_keil_uart_init();\n#else\n    RCC_APB2ENR |= RCC_APB2ENR_USART1EN;\n    USART1_BRR = 0x05B2u;\n    USART1_CR1 = USART_CR1_UE | USART_CR1_TE;\n#endif\n}\n',
    )
    adapted = _replace_once(
        adapted,
        'static void uart_putc(char ch)\n{\n    while ((USART1_SR & USART_SR_TXE) == 0u) {\n    }\n\n    USART1_DR = (uint32_t)ch;\n}\n',
        'static void uart_putc(char ch)\n{\n#if defined(BENCHMARK_PLATFORM_KEIL)\n    benchmark_keil_uart_putc(ch);\n#else\n    while ((USART1_SR & USART_SR_TXE) == 0u) {\n    }\n\n    USART1_DR = (uint32_t)ch;\n#endif\n}\n',
    )
    adapted = _replace_once(
        adapted,
        '    uart_init();\n',
        '#if defined(BENCHMARK_PLATFORM_KEIL)\n    benchmark_keil_platform_init();\n#endif\n    uart_init();\n',
    )
    adapted = _replace_once(
        adapted,
        'static void uart_put_fixed6(port_float value)\n',
        'static void uart_put_ms_from_us(uint64_t value_us)\n'
        '{\n'
        '    uint32_t whole_ms = (uint32_t)(value_us / 1000u);\n'
        '    uint32_t frac_us = (uint32_t)(value_us % 1000u);\n'
        '\n'
        '    uart_put_u32(whole_ms);\n'
        '    uart_putc(\'.\');\n'
        '    uart_putc((char)(\'0\' + (frac_us / 100u)));\n'
        '    uart_putc((char)(\'0\' + ((frac_us / 10u) % 10u)));\n'
        '    uart_putc((char)(\'0\' + (frac_us % 10u)));\n'
        '    uart_puts("000");\n'
        '}\n'
        '\n'
        'static void uart_put_fixed6(port_float value)\n',
    )
    optional_replacements = (
        (
            '\n    uint32_t total_cycles = 0u;\n',
            '\n    uint32_t total_cycles = 0u;\n'
            '#if defined(BENCHMARK_PLATFORM_KEIL)\n'
            '    uint64_t total_tick_us = 0u;\n'
            '    uint64_t start_tick_us = 0u;\n'
            '    uint64_t end_tick_us = 0u;\n'
            '#endif\n',
        ),
        (
            '\n            start_cycles = dwt_read_cycles();\n',
            '\n            start_cycles = dwt_read_cycles();\n'
            '#if defined(BENCHMARK_PLATFORM_KEIL)\n'
            '            start_tick_us = benchmark_keil_get_tick_us();\n'
            '#endif\n',
        ),
        (
            '\n        start_cycles = dwt_read_cycles();\n',
            '\n        start_cycles = dwt_read_cycles();\n'
            '#if defined(BENCHMARK_PLATFORM_KEIL)\n'
            '        start_tick_us = benchmark_keil_get_tick_us();\n'
            '#endif\n',
        ),
        (
            '\n            total_cycles += (end_cycles - start_cycles);\n',
            '\n            total_cycles += (end_cycles - start_cycles);\n'
            '#if defined(BENCHMARK_PLATFORM_KEIL)\n'
            '            end_tick_us = benchmark_keil_get_tick_us();\n'
            '            total_tick_us += (end_tick_us - start_tick_us);\n'
            '#endif\n',
        ),
        (
            '\n        total_cycles = end_cycles - start_cycles;\n',
            '\n        total_cycles = end_cycles - start_cycles;\n'
            '#if defined(BENCHMARK_PLATFORM_KEIL)\n'
            '        end_tick_us = benchmark_keil_get_tick_us();\n'
            '        total_tick_us = end_tick_us - start_tick_us;\n'
            '#endif\n',
        ),
        (
            '\n        uart_puts("\\ncycles_per_iter=");\n'
            '        uart_put_u32(BENCHMARK_ITERATIONS == 0u ? 0u : (total_cycles / BENCHMARK_ITERATIONS));\n'
            '    }\n',
            '\n        uart_puts("\\ncycles_per_iter=");\n'
            '        uart_put_u32(BENCHMARK_ITERATIONS == 0u ? 0u : (total_cycles / BENCHMARK_ITERATIONS));\n'
            '#if defined(BENCHMARK_PLATFORM_KEIL)\n'
            '        uart_puts("\\nwall_time_unit=");\n'
            '        uart_puts("ms");\n'
            '        uart_puts("\\nwall_time_total_ms=");\n'
            '        uart_put_ms_from_us(total_tick_us);\n'
            '        uart_puts("\\nwall_time_per_iter_ms=");\n'
            '        uart_put_ms_from_us(BENCHMARK_ITERATIONS == 0u ? 0u : (total_tick_us / (uint64_t)BENCHMARK_ITERATIONS));\n'
            '#endif\n'
            '    }\n',
        ),
    )
    for old, new in optional_replacements:
        if old in adapted:
            adapted = _replace_once(adapted, old, new)
    return _disable_benchmark_uart_helper_inlining(adapted)

def _disable_benchmark_uart_helper_inlining(content: str) -> str:
    """Keep the benchmark text output helpers out-of-line to avoid Keil code bloat."""
    replacements = (
        ('static void uart_putc(char ch)\n', 'static __attribute__((noinline)) void uart_putc(char ch)\n'),
        ('static void uart_puts(const char *message)\n', 'static __attribute__((noinline)) void uart_puts(const char *message)\n'),
        ('static void uart_put_u32(uint32_t value)\n', 'static __attribute__((noinline)) void uart_put_u32(uint32_t value)\n'),
        ('static void uart_put_ms_from_us(uint64_t value_us)\n', 'static __attribute__((noinline)) void uart_put_ms_from_us(uint64_t value_us)\n'),
        ('static void uart_put_fixed6(port_float value)\n', 'static __attribute__((noinline)) void uart_put_fixed6(port_float value)\n'),
        (
            'static void uart_put_matrix_rows(const port_float *values,\n',
            'static __attribute__((noinline)) void uart_put_matrix_rows(const port_float *values,\n',
        ),
    )
    adapted = content
    for old, new in replacements:
        adapted = _replace_once(adapted, old, new)
    return adapted

def _replace_once(content: str, old: str, new: str) -> str:
    if old not in content:
        raise ValueError(f'生成代码结构已变化，未找到预期片段: {old.splitlines()[0]}')
    return content.replace(old, new, 1)

def _write_keil_benchmark_uvprojx(project_file: Path,
                                  mdk_dir: Path,
                                  application_dir: Path,
                                  qemu_project_dir: Path) -> None:
    if not KEIL_BENCHMARK_BASE_UVPROJX.exists():
        raise FileNotFoundError(f'Keil ???????: {KEIL_BENCHMARK_BASE_UVPROJX}')

    tree = ET.parse(KEIL_BENCHMARK_BASE_UVPROJX)
    root = tree.getroot()
    target = root.find('./Targets/Target')
    if target is None:
        raise ValueError(f'Keil ????????: {KEIL_BENCHMARK_BASE_UVPROJX}')

    include_paths = [
        _to_keil_relpath(mdk_dir, application_dir),
        _to_keil_relpath(mdk_dir, KEIL_BENCHMARK_BASE_DIR / 'Drivers' / 'CMSIS' / 'Device' / 'ST' / 'STM32F4xx' / 'Include'),
        _to_keil_relpath(mdk_dir, KEIL_BENCHMARK_BASE_DIR / 'Drivers' / 'CMSIS' / 'Include'),
    ]
    defines = ','.join([
        'STM32F405xx',
        'ARM_MATH_CM4',
        '__TARGET_FPU_VFP',
        'BENCHMARK_PLATFORM_KEIL',
    ])

    _set_xml_text(target, './TargetOption/TargetCommonOption/OutputDirectory', 'output\\MET405\\')
    _set_xml_text(target, './TargetOption/TargetCommonOption/ListingPath', 'list\\MET405\\')
    _set_xml_text(target, './TargetOption/TargetCommonOption/OutputName', 'MET405_BENCHMARK')
    _set_xml_text(target, './TargetOption/TargetCommonOption/BeforeMake/RunUserProg1', '0')
    _set_xml_text(target, './TargetOption/TargetCommonOption/BeforeMake/RunUserProg2', '0')
    _set_xml_text(target, './TargetOption/TargetCommonOption/BeforeMake/UserProg1Name', '')
    _set_xml_text(target, './TargetOption/TargetCommonOption/BeforeMake/UserProg2Name', '')
    _set_xml_text(target, './TargetOption/TargetCommonOption/AfterMake/RunUserProg1', '0')
    _set_xml_text(target, './TargetOption/TargetCommonOption/AfterMake/RunUserProg2', '0')
    _set_xml_text(target, './TargetOption/TargetCommonOption/AfterMake/UserProg1Name', '')
    _set_xml_text(target, './TargetOption/TargetCommonOption/AfterMake/UserProg2Name', '')
    _set_xml_text(target, './TargetOption/TargetArmAds/Cads/VariousControls/IncludePath', ';'.join(include_paths))
    _set_xml_text(target, './TargetOption/TargetArmAds/Cads/VariousControls/Define', defines)

    groups = target.find('Groups')
    if groups is None:
        groups = ET.SubElement(target, 'Groups')
    groups.clear()

    startup_files = [
        KEIL_BENCHMARK_BASE_MDK_DIR / 'startup_stm32f405xx.s',
        KEIL_BENCHMARK_BASE_DIR / 'Hardware' / 'system_stm32f4xx.c',
    ]
    application_files = [
        qemu_project_dir / 'main.c',
        qemu_project_dir / 'model_data.h',
        application_dir / 'main.h',
        application_dir / 'benchmark_keil_port.h',
        application_dir / 'benchmark_keil_port.c',
        application_dir / 'stm32f4xx_it.h',
        application_dir / 'stm32f4xx_it.c',
    ]

    groups.extend([
        _create_keil_group('Startup', startup_files, mdk_dir),
        _create_keil_group('Application', application_files, mdk_dir),
    ])

    ET.indent(tree, space='  ')
    tree.write(project_file, encoding='UTF-8', xml_declaration=True)

def _create_keil_group(group_name: str,
                       files: Sequence[Path],
                       mdk_dir: Path) -> ET.Element:
    group = ET.Element('Group')
    ET.SubElement(group, 'GroupName').text = group_name
    files_el = ET.SubElement(group, 'Files')
    for file_path in files:
        file_el = ET.SubElement(files_el, 'File')
        ET.SubElement(file_el, 'FileName').text = file_path.name
        ET.SubElement(file_el, 'FileType').text = str(_guess_keil_file_type(file_path))
        ET.SubElement(file_el, 'FilePath').text = _to_keil_relpath(mdk_dir, file_path)
    return group

def _guess_keil_file_type(path: Path) -> int:
    suffix = path.suffix.lower()
    if suffix == '.s':
        return 2
    if suffix == '.h':
        return 5
    return 1

def _to_keil_relpath(from_dir: Path, target: Path) -> str:
    return os.path.relpath(target.resolve(), from_dir.resolve()).replace('/', '\\')

def _set_xml_text(root: ET.Element, path: str, value: str) -> None:
    node = root.find(path)
    if node is None:
        raise ValueError(f'Keil 工程缺少节点: {path}')
    node.text = value

def _render_keil_benchmark_main_h() -> str:
    return """#ifndef BENCHMARK_MAIN_H
#define BENCHMARK_MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>

void Error_Handler(void);

#ifdef __cplusplus
}
#endif

#endif
"""

def _render_keil_benchmark_port_h() -> str:
    return """#ifndef BENCHMARK_KEIL_PORT_H
#define BENCHMARK_KEIL_PORT_H

#include "main.h"

void benchmark_keil_platform_init(void);
void benchmark_keil_uart_init(void);
void benchmark_keil_uart_putc(char ch);
uint64_t benchmark_keil_get_tick_us(void);

#endif
"""

def _render_keil_benchmark_port_c() -> str:
    return """#include "benchmark_keil_port.h"

#include "stm32f405xx.h"

#define BENCHMARK_USART_BRR_16MHZ 0x008BU
#define BENCHMARK_DEMCR_TRCENA (1UL << 24)
#define BENCHMARK_DWT_CTRL_CYCCNTENA (1UL << 0)

static uint32_t g_benchmark_keil_ready = 0U;

static void benchmark_enable_cycle_counter(void);
static void benchmark_gpio_config_usart(GPIO_TypeDef *gpio_port, uint32_t pin_index);
static void benchmark_uart_config(USART_TypeDef *usart_instance);
static void benchmark_console_write_byte(USART_TypeDef *console_usart, uint8_t ch);
static void benchmark_keil_write_string(const char *message);

void benchmark_keil_uart_init(void)
{
    if (g_benchmark_keil_ready == 0U) {
        benchmark_keil_platform_init();
    }
}

void benchmark_keil_uart_putc(char ch)
{
    if ((USART1->CR1 & USART_CR1_UE) != 0U) {
        benchmark_console_write_byte(USART1, (uint8_t)ch);
    }
    if ((USART3->CR1 & USART_CR1_UE) != 0U) {
        benchmark_console_write_byte(USART3, (uint8_t)ch);
    }
}

uint64_t benchmark_keil_get_tick_us(void)
{
    return (uint64_t)(DWT->CYCCNT / 16U);
}

void benchmark_keil_platform_init(void)
{
    if (g_benchmark_keil_ready != 0U) {
        return;
    }

    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN | RCC_AHB1ENR_GPIOBEN;
    RCC->APB2ENR |= RCC_APB2ENR_USART1EN;
    RCC->APB1ENR |= RCC_APB1ENR_USART3EN;
    __DSB();

    benchmark_gpio_config_usart(GPIOA, 9U);
    benchmark_gpio_config_usart(GPIOA, 10U);
    benchmark_gpio_config_usart(GPIOB, 10U);
    benchmark_gpio_config_usart(GPIOB, 11U);

    benchmark_uart_config(USART1);
    benchmark_uart_config(USART3);
    benchmark_enable_cycle_counter();

    g_benchmark_keil_ready = 1U;

    benchmark_keil_write_string("[  OK]: hardware init ok\\r\\n");
    benchmark_keil_write_string("[Info]: lean benchmark bring-up enabled\\r\\n");
    benchmark_keil_write_string("[Info]: UART1+UART3 mirrored at 115200 baud\\r\\n");
}

void Error_Handler(void)
{
    while (1) {
    }
}

static void benchmark_enable_cycle_counter(void)
{
    CoreDebug->DEMCR |= BENCHMARK_DEMCR_TRCENA;
    DWT->CYCCNT = 0U;
    DWT->CTRL |= BENCHMARK_DWT_CTRL_CYCCNTENA;
}

static void benchmark_gpio_config_usart(GPIO_TypeDef *gpio_port, uint32_t pin_index)
{
    uint32_t mode_shift = pin_index * 2U;
    uint32_t afr_index = pin_index >> 3U;
    uint32_t afr_shift = (pin_index & 7U) * 4U;

    gpio_port->MODER = (gpio_port->MODER & ~(3UL << mode_shift)) | (2UL << mode_shift);
    gpio_port->OSPEEDR = (gpio_port->OSPEEDR & ~(3UL << mode_shift)) | (3UL << mode_shift);
    gpio_port->OTYPER &= ~(1UL << pin_index);
    gpio_port->PUPDR = (gpio_port->PUPDR & ~(3UL << mode_shift)) | (1UL << mode_shift);
    gpio_port->AFR[afr_index] = (gpio_port->AFR[afr_index] & ~(0xFUL << afr_shift)) | (7UL << afr_shift);
}

static void benchmark_uart_config(USART_TypeDef *usart_instance)
{
    usart_instance->CR1 = 0U;
    usart_instance->CR2 = 0U;
    usart_instance->CR3 = 0U;
    usart_instance->BRR = BENCHMARK_USART_BRR_16MHZ;
    usart_instance->CR1 = USART_CR1_UE | USART_CR1_TE | USART_CR1_RE;
}

static void benchmark_console_write_byte(USART_TypeDef *console_usart, uint8_t ch)
{
    while ((console_usart->SR & USART_SR_TXE) == 0U) {
    }
    console_usart->DR = (uint32_t)ch;
}

static void benchmark_keil_write_string(const char *message)
{
    while (*message != '\\0') {
        benchmark_keil_uart_putc(*message++);
    }
}
"""

def _render_keil_benchmark_it_h() -> str:
    return """#ifndef BENCHMARK_STM32F4XX_IT_H
#define BENCHMARK_STM32F4XX_IT_H

#ifdef __cplusplus
extern "C" {
#endif

void NMI_Handler(void);
void HardFault_Handler(void);
void MemManage_Handler(void);
void BusFault_Handler(void);
void UsageFault_Handler(void);
void SVC_Handler(void);
void DebugMon_Handler(void);
void PendSV_Handler(void);
void SysTick_Handler(void);
void TIM3_IRQHandler(void);
void EXTI15_10_IRQHandler(void);
void USART1_IRQHandler(void);
void USART3_IRQHandler(void);
void DMA1_Stream3_IRQHandler(void);

#ifdef __cplusplus
}
#endif

#endif
"""

def _render_keil_benchmark_it_c() -> str:
    return """#include "stm32f4xx_it.h"

void NMI_Handler(void)
{
}

void HardFault_Handler(void)
{
    while (1) {
    }
}

void MemManage_Handler(void)
{
    while (1) {
    }
}

void BusFault_Handler(void)
{
    while (1) {
    }
}

void UsageFault_Handler(void)
{
    while (1) {
    }
}

void SVC_Handler(void)
{
}

void DebugMon_Handler(void)
{
}

void PendSV_Handler(void)
{
}

void SysTick_Handler(void)
{
}

void TIM3_IRQHandler(void)
{
}

void EXTI15_10_IRQHandler(void)
{
}

void USART1_IRQHandler(void)
{
}

void USART3_IRQHandler(void)
{
}

void DMA1_Stream3_IRQHandler(void)
{
}
"""

def _resolve_model_project_dir(model_project_name: str) -> Path:
    normalized = model_project_name.replace('\\', '/').strip('/').strip()
    candidate = Path(normalized)
    if not candidate.parts or candidate.parts[0] != 'projects':
        candidate = Path('projects') / candidate
    resolved = REPO_ROOT / candidate
    if not resolved.exists():
        raise FileNotFoundError(f'模型项目目录不存在: {resolved}')
    return resolved

def _resolve_weights_json_path(model_dir: Path, weights_file: Optional[str]) -> Path:
    if weights_file:
        specified = Path(str(weights_file))
        if not specified.is_absolute():
            if specified.parts and specified.parts[0] == 'data':
                specified = model_dir / specified
            else:
                specified = model_dir / 'data' / specified
        resolved = specified
        if not resolved.exists():
            raise FileNotFoundError(f'权重 JSON 不存在: {resolved}')
        return resolved

    candidates = [
        model_dir / 'data' / 'best_val.weights.json',
        model_dir / 'data' / 'best.weights.json',
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f'未找到权重 JSON: {candidates}')

def _resolve_generated_project_dir(ep_path: ExternalPath,
                                   generation_config: Dict[str, Any]) -> Path:
    project_dir = generation_config.get('project_dir', 'qemu_project')
    resolved = Path(str(project_dir))
    if not resolved.is_absolute():
        resolved = ep_path.full_path / resolved
    return resolved

def _normalize_benchmark_config(config: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(config)
    normalized.setdefault('iterations', 100)
    normalized.setdefault('reset_state_each_run', True)
    normalized.setdefault('repeat_runs', 1)
    return normalized

def _normalize_validation_config(config: Dict[str, Any]) -> Dict[str, Any]:
    dataset_config = dict(config.get('dataset', {}))
    selection_config = dict(config.get('selection', {}))
    wave_output_config = dict(config.get('wave_output', {}))

    selection_config.setdefault('start_time_s', 0.0)
    selection_config.setdefault('end_time_s', None)
    wave_output_config.setdefault('compress', True)
    wave_output_config.setdefault('export_intermediates', True)
    wave_output_config.setdefault('plot_comparison', True)
    wave_output_config.setdefault('plot_dpi', 200)

    return {
        'dataset': dataset_config,
        'selection': selection_config,
        'wave_output': wave_output_config,
    }

def _normalize_keil_config(config: Dict[str, Any],
                           keil_overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    normalized = dict(config)
    normalized.setdefault('action', 'build-program-capture')
    normalized.setdefault('target', 'MET405')
    normalized.setdefault('programmer', 'daplink')
    normalized.setdefault('program_backend', 'keil')
    normalized.setdefault('probe_uid', '')
    normalized.setdefault('serial_port', '')
    normalized.setdefault('baud_rate', 115200)
    normalized.setdefault('capture_timeout', 20)
    normalized.setdefault('job_timeout', 300)
    normalized.setdefault('success_markers', ['validation_complete=1'])
    normalized.setdefault(
        'keil_cli_path',
        str(Path.home() / '.agents' / 'skills' / 'keil' / 'keil-cli.py'),
    )

    for key, value in (keil_overrides or {}).items():
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        normalized[key] = value

    normalized['baud_rate'] = int(normalized['baud_rate'])
    normalized['capture_timeout'] = int(normalized['capture_timeout'])
    normalized['job_timeout'] = int(normalized['job_timeout'])
    normalized['success_markers'] = [str(item) for item in normalized.get('success_markers', []) if str(item)]
    return normalized

def _normalize_project_path(model_project_name: str) -> str:
    normalized = model_project_name.replace('\\', '/').strip('/').strip()
    if not normalized.startswith('projects/'):
        normalized = f'projects/{normalized}'
    return normalized

def _apply_validation_dataset_overrides(config_obj: Any,
                                        dataset_config: Dict[str, Any]) -> None:
    source_project_config = dataset_config.get('source_project_config')
    if source_project_config:
        source_path = _resolve_path(source_project_config)
        with open(source_path, 'r', encoding='utf-8') as file_obj:
            source_config = json.load(file_obj)
        for field_name in DATASET_OVERRIDE_FIELDS:
            if field_name in source_config:
                setattr(config_obj, field_name, source_config[field_name])

    for field_name in DATASET_OVERRIDE_FIELDS:
        if field_name in dataset_config:
            setattr(config_obj, field_name, dataset_config[field_name])

def _resolve_path(path_str: str) -> Path:
    path = Path(str(path_str))
    if path.is_absolute():
        return path
    return REPO_ROOT / path

def _select_validation_dataset(dataset_origin: Any,
                               selection_config: Dict[str, Any]) -> tuple[Any, Dict[str, float]]:
    magnitudes = selection_config.get('magnitudes')
    frequencies = selection_config.get('frequencies')

    magn_indices = _resolve_requested_indices(magnitudes, dataset_origin.magn_list, 'magnitude')
    freq_indices = _resolve_requested_indices(frequencies, dataset_origin.freq_list, 'frequency')
    selected_dataset = dataset_origin.select(magn_indices=magn_indices, freq_indices=freq_indices)
    if selected_dataset.magn_num <= 0 or selected_dataset.freq_num <= 0:
        raise ValueError('筛选后数据集为空，请检查 magnitudes/frequencies 配置')

    return _crop_dataset_time_window(selected_dataset, selection_config)

def _resolve_requested_indices(requested_values: Optional[Sequence[Any]],
                               available_values: Sequence[Any],
                               label: str) -> Optional[List[int]]:
    if requested_values is None:
        return None
    if len(requested_values) == 0:
        raise ValueError(f'{label} 选择列表不能为空')

    indices: List[int] = []
    for requested in requested_values:
        requested_value = float(requested)
        matched_index: Optional[int] = None
        for index, candidate in enumerate(available_values):
            if abs(float(candidate) - requested_value) <= 1e-9:
                matched_index = index
                break
        if matched_index is None:
            raise ValueError(f'未在数据集中找到 {label}={requested_value}，可选值: {list(available_values)}')
        indices.append(matched_index)
    return indices

def _crop_dataset_time_window(dataset: Any,
                              selection_config: Dict[str, Any]) -> tuple[Any, Dict[str, float]]:
    total_points = int(dataset.output_ori.shape[2])
    sample_rate = float(dataset.fs)
    start_time_s = float(selection_config.get('start_time_s', 0.0) or 0.0)
    requested_end = selection_config.get('end_time_s')
    end_time_s = float(requested_end) if requested_end is not None else total_points / sample_rate

    start_idx = max(0, int(round(start_time_s * sample_rate)))
    end_idx = min(total_points, int(round(end_time_s * sample_rate)))
    if end_idx <= start_idx:
        raise ValueError('时间窗口非法，end_time_s 必须大于 start_time_s')

    cropped_dataset = dataset.select()
    cropped_dataset.inputs = dataset.inputs[:, :, start_idx:end_idx].copy()
    cropped_dataset.output_ori = dataset.output_ori[:, :, start_idx:end_idx].copy()
    cropped_dataset.output_tar = dataset.output_tar[:, :, start_idx:end_idx].copy()
    cropped_dataset.time_cliped_s = (end_idx - start_idx) / sample_rate

    return cropped_dataset, {
        'start_time_s': start_idx / sample_rate,
        'end_time_s': end_idx / sample_rate,
        'sample_count': end_idx - start_idx,
    }

def _build_validation_records(selected_dataset: Any,
                              tf_output_2d: np.ndarray) -> List[ValidationRecord]:
    records: List[ValidationRecord] = []
    row_index = 0
    for mag_index, magnitude in enumerate(selected_dataset.magn_list):
        for freq_index, frequency in enumerate(selected_dataset.freq_list):
            input_sequence = np.asarray(selected_dataset.output_ori[mag_index, freq_index], dtype=np.float64)
            target_sequence = np.asarray(selected_dataset.output_tar[mag_index, freq_index], dtype=np.float64)
            tf_output_sequence = np.asarray(tf_output_2d[row_index], dtype=np.float64)
            record_id = f'mag{float(magnitude):g}_freq{float(frequency):g}'
            records.append(ValidationRecord(
                record_id=record_id,
                magnitude=float(magnitude),
                frequency=float(frequency),
                input_sequence=[[float(value)] for value in input_sequence.tolist()],
                target_sequence=target_sequence.tolist(),
                tf_output_sequence=tf_output_sequence.tolist(),
            ))
            row_index += 1
    return records

def _resolve_reference_weights_path(weights_json_path: Path) -> Path:
    weights_h5_path = weights_json_path.with_suffix('.h5')
    if weights_h5_path.exists():
        return weights_h5_path
    return weights_json_path

def _parse_benchmark_stdout(stdout: str) -> Dict[str, Any]:
    parsed: Dict[str, Any] = {}
    start_markers = [
        'iterations=',
        'record_count=',
        'seq_len=',
        'input_dim=',
        'dwt_supported=',
        'timer_source=',
        'measurement_unit=',
    ]
    start_indexes = [stdout.find(marker) for marker in start_markers if stdout.find(marker) >= 0]
    if start_indexes:
        stdout = stdout[min(start_indexes):]

    line_prefix_patterns = [
        r'iterations',
        r'record_count',
        r'seq_len',
        r'input_dim',
        r'lstm_units',
        r'dense_units',
        r'gru_units',
        r'output_units',
        r'feature_count',
        r'kan_layer_count',
        r'transformer_layer_count',
        r'transformer_num_heads',
        r'transformer_key_dim',
        r'transformer_ff_dim',
        r'attention_pool_size',
        r'block_count',
        r'dwt_supported',
        r'timer_source',
        r'measurement_unit',
        r'measurement_total',
        r'measurement_per_iter',
        r'cycles_total',
        r'cycles_per_iter',
        r'wall_time_unit',
        r'wall_time_total_ms',
        r'wall_time_per_iter_ms',
        r'output',
        r'benchmark_complete',
        r'validation_complete',
        r'validation_record_\d+',
        r'validation_[A-Za-z0-9_]+_\d+',
    ]
    normalized_stdout = re.sub(
        r'(?<!^)(?=(?:' + '|'.join(line_prefix_patterns) + r')=)',
        '\n',
        stdout,
    )

    for raw_line in normalized_stdout.splitlines():
        line = raw_line.strip()
        if not line or '=' not in line:
            continue
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        parsed[key] = _coerce_benchmark_scalar(value)
    return parsed

def _coerce_benchmark_scalar(value: str) -> Any:
    try:
        if re.fullmatch(r'[+-]?\d+', value):
            return int(value)
        if re.fullmatch(r'[+-]?(?:\d+\.\d*|\d*\.\d+)(?:[eE][+-]?\d+)?', value):
            return float(value)
    except ValueError:
        pass
    return value

def _extract_validation_outputs(parsed_output: Dict[str, Any],
                                validation_artifacts: ValidationArtifacts) -> List[List[float]]:
    c_output_sequences: List[List[float]] = []
    for record_index in range(validation_artifacts.record_count):
        key = f'validation_record_{record_index}'
        if key not in parsed_output:
            raise ValueError(f'QEMU 输出缺少 {key}')
        raw_value = str(parsed_output[key])
        samples = [float(item) for item in raw_value.split(',') if item]
        if len(samples) != validation_artifacts.seq_len:
            raise ValueError(
                f'{key} 样本数不匹配，期望 {validation_artifacts.seq_len}，实际 {len(samples)}'
            )
        c_output_sequences.append(samples)

    if int(parsed_output.get('validation_complete', 0) or 0) != 1:
        raise ValueError('QEMU 输出未标记 validation_complete=1')
    return c_output_sequences

def _extract_c_debug_sequences(parsed_output: Dict[str, Any],
                               validation_artifacts: ValidationArtifacts) -> Dict[str, List[Any]]:
    debug_sequences: Dict[str, List[Any]] = {}

    stage_names = sorted({
        match.group(1)
        for key in parsed_output
        for match in [re.match(r'^validation_(.+)_(\d+)$', key)]
        if match is not None and match.group(1) != 'record'
    })

    for stage_name in stage_names:
        stage_records: List[Any] = []
        for record_index in range(validation_artifacts.record_count):
            key = f'validation_{stage_name}_{record_index}'
            if key not in parsed_output:
                stage_records = []
                break
            matrix = _parse_float_matrix(str(parsed_output[key]))
            if matrix.shape[0] != validation_artifacts.seq_len:
                raise ValueError(
                    f'{key} 样本数不匹配，期望 {validation_artifacts.seq_len}，实际 {matrix.shape[0]}'
                )
            stage_records.append(matrix.tolist())
        if stage_records:
            debug_sequences[stage_name] = stage_records

    return debug_sequences

def _parse_float_matrix(raw_value: str) -> np.ndarray:
    rows = [row for row in raw_value.split(';') if row]
    parsed_rows: List[List[float]] = []
    expected_columns: Optional[int] = None

    for row in rows:
        values = [float(item) for item in row.split(',') if item]
        if expected_columns is None:
            expected_columns = len(values)
        elif len(values) != expected_columns:
            raise ValueError(f'矩阵列数不一致，期望 {expected_columns}，实际 {len(values)}')
        parsed_rows.append(values)

    if not parsed_rows:
        return np.zeros((0, 0), dtype=np.float64)
    return np.asarray(parsed_rows, dtype=np.float64)

def _enrich_benchmark_output(parsed_output: Dict[str, Any],
                             run_workflow: Dict[str, Any],
                             benchmark_config: Dict[str, Any]) -> Dict[str, Any]:
    enriched = dict(parsed_output)
    if 'measurement_per_iter' in enriched:
        return enriched

    run_details = run_workflow.get('run', {})
    elapsed_seconds = float(run_details.get('elapsed_seconds', 0.0))
    iterations = int(enriched.get('iterations', benchmark_config.get('iterations', 0)) or 0)

    enriched['timer_source'] = 'host_elapsed'
    enriched['measurement_unit'] = 'seconds'
    enriched['measurement_total'] = elapsed_seconds
    if iterations > 0:
        enriched['measurement_per_iter'] = elapsed_seconds / iterations
    return enriched

def _write_validation_wave_files(output_root: Path,
                                 validation_artifacts: ValidationArtifacts,
                                 c_output_sequences: Optional[List[List[float]]],
                                 compress: bool,
                                 export_intermediates: bool,
                                 c_debug_sequences: Optional[Dict[str, List[Any]]] = None) -> Dict[str, str]:
    wave_dir = output_root / 'waves'
    wave_dir.mkdir(parents=True, exist_ok=True)

    output_paths: Dict[str, str] = {}
    tf_wave_path = wave_dir / 'tf_output.wave'
    _save_wave_file(
        tf_wave_path,
        source_name='tf_output',
        sequences=[record.tf_output_sequence for record in validation_artifacts.records],
        validation_artifacts=validation_artifacts,
        compress=compress,
    )
    output_paths['tf_output_wave'] = _relative_or_str(tf_wave_path)

    origin_wave_path = wave_dir / 'origin_input.wave'
    _save_wave_file(
        origin_wave_path,
        source_name='origin_input',
        sequences=[[sample[0] for sample in record.input_sequence] for record in validation_artifacts.records],
        validation_artifacts=validation_artifacts,
        compress=compress,
    )
    output_paths['origin_input_wave'] = _relative_or_str(origin_wave_path)

    target_wave_path = wave_dir / 'target_output.wave'
    _save_wave_file(
        target_wave_path,
        source_name='target_output',
        sequences=[record.target_sequence for record in validation_artifacts.records],
        validation_artifacts=validation_artifacts,
        compress=compress,
    )
    output_paths['target_output_wave'] = _relative_or_str(target_wave_path)

    if c_output_sequences is not None:
        c_wave_path = wave_dir / 'c_output.wave'
        _save_wave_file(
            c_wave_path,
            source_name='c_output',
            sequences=c_output_sequences,
            validation_artifacts=validation_artifacts,
            compress=compress,
        )
        output_paths['c_output_wave'] = _relative_or_str(c_wave_path)

    if export_intermediates:
        output_paths.update(_write_intermediate_wave_files(
            wave_dir=wave_dir,
            prefix='tf',
            debug_sequences=validation_artifacts.tf_debug_sequences,
            validation_artifacts=validation_artifacts,
            compress=compress,
        ))
        if c_debug_sequences:
            output_paths.update(_write_intermediate_wave_files(
                wave_dir=wave_dir,
                prefix='c',
                debug_sequences=c_debug_sequences,
                validation_artifacts=validation_artifacts,
                compress=compress,
            ))

    return output_paths

def _write_intermediate_wave_files(wave_dir: Path,
                                   prefix: str,
                                   debug_sequences: Dict[str, List[Any]],
                                   validation_artifacts: ValidationArtifacts,
                                   compress: bool) -> Dict[str, str]:
    output_paths: Dict[str, str] = {}
    for stage_name, sequences in debug_sequences.items():
        wave_path = wave_dir / f'{prefix}_{stage_name}.wave'
        _save_wave_file(
            wave_path,
            source_name=f'{prefix}_{stage_name}',
            sequences=sequences,
            validation_artifacts=validation_artifacts,
            compress=compress,
            channel_names=_build_channel_names(stage_name, sequences),
        )
        output_paths[f'{prefix}_{stage_name}_wave'] = _relative_or_str(wave_path)
    return output_paths

def _build_channel_names(stage_name: str,
                         sequences: Sequence[Sequence[Any]]) -> List[str]:
    if not sequences:
        return [stage_name]

    first = np.asarray(sequences[0], dtype=np.float64)
    if first.ndim == 1:
        channel_count = 1
    elif first.ndim == 2:
        channel_count = int(first.shape[1])
    else:
        raise ValueError(f'波形维度非法: {first.ndim}')

    if channel_count == 1:
        return [stage_name]
    if stage_name == 'iir_output':
        return [f'iir_{index}' for index in range(channel_count)]
    if stage_name == 'lstm_hidden':
        return [f'hidden_{index}' for index in range(channel_count)]
    if stage_name == 'gru_hidden':
        return [f'hidden_{index}' for index in range(channel_count)]
    if stage_name == 'dense_output':
        return [f'dense_{index}' for index in range(channel_count)]
    if stage_name.startswith('kan_layer_'):
        return [f'{stage_name}_{index}' for index in range(channel_count)]
    return [f'{stage_name}_{index}' for index in range(channel_count)]

def _save_wave_file(path: Path,
                    source_name: str,
                    sequences: Sequence[Sequence[float]],
                    validation_artifacts: ValidationArtifacts,
                    compress: bool,
                    channel_names: Optional[Sequence[str]] = None) -> None:
    target_path = path if path.suffix == '.wave' else path.with_suffix('.wave')
    target_path.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    global_metadata = {
        'standard': {
            'description': f'{source_name} validation waveforms',
            'version': '1.0',
            'creation_date': timestamp,
            'modified_date': timestamp,
            'author': 'qemu-c-inference',
            'tags': ['validation', source_name],
        },
        'user': {
            'dataset_type': validation_artifacts.dataset_type,
            'full_data_path': validation_artifacts.full_data_path,
            'time_window': validation_artifacts.time_window,
        },
    }

    record_data_dict: Dict[str, np.ndarray] = {}
    record_metadata_dict: Dict[str, Dict[str, Any]] = {}
    for index, (record, sequence) in enumerate(zip(validation_artifacts.records, sequences)):
        record_key = f'record_{index}'
        record_values = np.asarray(sequence, dtype=np.float32)
        if record_values.ndim == 1:
            record_values = record_values.reshape(-1, 1)
        if record_values.ndim != 2:
            raise ValueError(f'Wave 数据维度非法，期望 1 或 2 维，实际 {record_values.ndim}')

        resolved_channel_names = list(channel_names) if channel_names is not None else [source_name]
        if len(resolved_channel_names) != int(record_values.shape[1]):
            raise ValueError(
                f'Wave 通道名数量不匹配，期望 {record_values.shape[1]}，实际 {len(resolved_channel_names)}'
            )

        record_data_dict[record_key] = record_values
        record_metadata_dict[record_key] = {
            'standard': {
                'sample_rate': validation_artifacts.sample_rate,
                'channel_names': resolved_channel_names,
                'record_id': record.record_id,
                'creation_date': timestamp,
                'modified_date': timestamp,
                'units': 'V',
            },
            'user': {
                'magnitude': record.magnitude,
                'frequency': record.frequency,
                'source': source_name,
            },
        }

    payload = {
        'metadata': np.array(json.dumps({
            '__format_version__': '1.0',
            'global': global_metadata,
            'records': record_metadata_dict,
        }), dtype='object'),
        **record_data_dict,
    }

    save_func = np.savez_compressed if compress else np.savez
    with open(target_path, 'wb') as file_obj:
        save_func(file_obj, **payload)

def _write_validation_comparison_plots(output_root: Path,
                                       validation_artifacts: ValidationArtifacts,
                                       c_output_sequences: Sequence[Sequence[float]],
                                       dpi: int) -> Dict[str, str]:
    plot_dir = output_root / 'plots'
    plot_dir.mkdir(parents=True, exist_ok=True)

    output_paths: Dict[str, str] = {}
    for index, (record, c_sequence) in enumerate(zip(validation_artifacts.records, c_output_sequences)):
        plot_path = plot_dir / f'{_sanitize_filename(record.record_id)}_comparison.png'
        _save_validation_comparison_plot(
            plot_path=plot_path,
            record=record,
            c_output_sequence=c_sequence,
            sample_rate=validation_artifacts.sample_rate,
            dpi=dpi,
        )
        output_paths[f'comparison_plot_{index}'] = _relative_or_str(plot_path)

    return output_paths

def _save_validation_comparison_plot(plot_path: Path,
                                     record: ValidationRecord,
                                     c_output_sequence: Sequence[float],
                                     sample_rate: float,
                                     dpi: int) -> None:
    origin_values = np.asarray([sample[0] for sample in record.input_sequence], dtype=np.float64)
    target_values = np.asarray(record.target_sequence, dtype=np.float64)
    tf_values = np.asarray(record.tf_output_sequence, dtype=np.float64)
    c_values = np.asarray(c_output_sequence, dtype=np.float64)

    sequence_length = min(len(origin_values), len(target_values), len(tf_values), len(c_values))
    if sequence_length == 0:
        raise ValueError(f'记录 {record.record_id} 没有可绘制的波形数据')

    time_axis = np.arange(sequence_length, dtype=np.float64) / float(sample_rate)

    fig, ax = plt.subplots(figsize=(14, 6))
    try:
        ax.plot(time_axis, origin_values[:sequence_length], label='origin', color='#1f77b4', linewidth=1.4, alpha=0.90)
        ax.plot(time_axis, target_values[:sequence_length], label='target', color='#2ca02c', linewidth=1.4, alpha=0.85)
        ax.plot(time_axis, c_values[:sequence_length], label='c_inference', color='#d62728', linewidth=1.6, alpha=0.85)
        ax.plot(time_axis, tf_values[:sequence_length], label='tf_inference', color='#ff7f0e', linewidth=1.4, alpha=0.85)

        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude')
        ax.set_title(
            f'Waveform Comparison: {record.record_id}\n'
            f'Frequency={record.frequency:.1f} Hz, Magnitude={record.magnitude:.2f}'
        )
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')
        fig.tight_layout()
        fig.savefig(plot_path, dpi=dpi, bbox_inches='tight')
    finally:
        plt.close(fig)

def _sanitize_filename(value: str) -> str:
    sanitized = ''.join(character if character.isalnum() or character in {'-', '_'} else '_' for character in value)
    return sanitized.strip('_') or 'record'

def _compute_wave_comparison(validation_artifacts: ValidationArtifacts,
                             c_output_sequences: Sequence[Sequence[float]]) -> Dict[str, Any]:
    c_arrays = [np.asarray(sequence, dtype=np.float64) for sequence in c_output_sequences]
    tf_arrays = [
        np.asarray(record.tf_output_sequence, dtype=np.float64)
        for record in validation_artifacts.records
    ]

    per_record: List[Dict[str, Any]] = []
    for record, c_array, tf_array in zip(validation_artifacts.records, c_arrays, tf_arrays):
        diff = c_array - tf_array
        per_record.append({
            'record_id': record.record_id,
            'magnitude': record.magnitude,
            'frequency': record.frequency,
            'mae': float(np.mean(np.abs(diff))),
            'mse': float(np.mean(np.square(diff))),
            'max_abs_error': float(np.max(np.abs(diff))),
            'c_output_stats': _compute_signal_stats(c_array),
            'tf_output_stats': _compute_signal_stats(tf_array),
            'diff_stats': _compute_signal_stats(diff),
        })

    c_flat = np.concatenate(c_arrays) if c_arrays else np.asarray([], dtype=np.float64)
    tf_flat = np.concatenate(tf_arrays) if tf_arrays else np.asarray([], dtype=np.float64)
    diff_flat = c_flat - tf_flat
    overall = {
        'record_count': len(per_record),
        'sample_count': int(diff_flat.size),
        'mae': float(np.mean(np.abs(diff_flat))) if diff_flat.size else 0.0,
        'mse': float(np.mean(np.square(diff_flat))) if diff_flat.size else 0.0,
        'max_abs_error': float(np.max(np.abs(diff_flat))) if diff_flat.size else 0.0,
        'c_output_stats': _compute_signal_stats(c_flat),
        'tf_output_stats': _compute_signal_stats(tf_flat),
        'diff_stats': _compute_signal_stats(diff_flat),
    }
    return {
        'overall': overall,
        'per_record': per_record,
    }

def _compute_intermediate_comparison(validation_artifacts: ValidationArtifacts,
                                     c_debug_sequences: Dict[str, List[Any]]) -> Dict[str, Any]:
    comparisons: Dict[str, Any] = {}
    tf_debug_sequences = validation_artifacts.tf_debug_sequences

    for stage_name in sorted(set(tf_debug_sequences) & set(c_debug_sequences)):
        c_arrays = [np.asarray(sequence, dtype=np.float64) for sequence in c_debug_sequences[stage_name]]
        tf_arrays = [np.asarray(sequence, dtype=np.float64) for sequence in tf_debug_sequences[stage_name]]

        if len(c_arrays) != len(tf_arrays):
            raise ValueError(f'{stage_name} 记录数不匹配，TF={len(tf_arrays)}，C={len(c_arrays)}')

        diff_arrays: List[np.ndarray] = []
        for c_array, tf_array in zip(c_arrays, tf_arrays):
            if c_array.shape != tf_array.shape:
                raise ValueError(f'{stage_name} 形状不匹配，TF={tf_array.shape}，C={c_array.shape}')
            diff_arrays.append(c_array - tf_array)

        c_flat = np.concatenate([array.reshape(-1) for array in c_arrays]) if c_arrays else np.asarray([], dtype=np.float64)
        tf_flat = np.concatenate([array.reshape(-1) for array in tf_arrays]) if tf_arrays else np.asarray([], dtype=np.float64)
        diff_flat = np.concatenate([array.reshape(-1) for array in diff_arrays]) if diff_arrays else np.asarray([], dtype=np.float64)
        channel_count = int(c_arrays[0].shape[1]) if c_arrays and c_arrays[0].ndim == 2 else 1

        comparisons[stage_name] = {
            'record_count': len(c_arrays),
            'sample_count': int(diff_flat.size),
            'channel_count': channel_count,
            'mae': float(np.mean(np.abs(diff_flat))) if diff_flat.size else 0.0,
            'mse': float(np.mean(np.square(diff_flat))) if diff_flat.size else 0.0,
            'max_abs_error': float(np.max(np.abs(diff_flat))) if diff_flat.size else 0.0,
            'c_output_stats': _compute_signal_stats(c_flat),
            'tf_output_stats': _compute_signal_stats(tf_flat),
            'diff_stats': _compute_signal_stats(diff_flat),
        }

    return comparisons

def _compute_signal_stats(values: np.ndarray) -> Dict[str, float]:
    if values.size == 0:
        return {
            'min': 0.0,
            'max': 0.0,
            'mean': 0.0,
            'energy': 0.0,
        }
    return {
        'min': float(np.min(values)),
        'max': float(np.max(values)),
        'mean': float(np.mean(values)),
        'energy': float(np.sum(np.square(values))),
    }

def _load_qemu_reference_comparison(output_root: Path,
                                    keil_output_sequences: Sequence[Sequence[float]]) -> Optional[Dict[str, Any]]:
    summary_path = output_root / 'benchmark_summary.json'
    if not summary_path.exists():
        return None

    with open(summary_path, 'r', encoding='utf-8') as file_obj:
        qemu_summary = json.load(file_obj)

    wave_paths = qemu_summary.get('wave_paths', {})
    qemu_wave_path_raw = wave_paths.get('c_output_wave')
    if not qemu_wave_path_raw:
        return None

    qemu_wave_path = REPO_ROOT / str(qemu_wave_path_raw)
    if not qemu_wave_path.exists():
        qemu_wave_path = Path(str(qemu_wave_path_raw))
    if not qemu_wave_path.exists():
        return None

    qemu_output_sequences = _load_single_channel_wave_sequences(qemu_wave_path)
    comparison = _compute_sequence_comparison(qemu_output_sequences, keil_output_sequences)
    comparison['qemu_output_wave'] = _relative_or_str(qemu_wave_path)
    return comparison

def _load_single_channel_wave_sequences(wave_path: Path) -> List[List[float]]:
    with np.load(wave_path, allow_pickle=True) as payload:
        record_keys = sorted(
            [key for key in payload.files if key.startswith('record_')],
            key=lambda item: int(item.split('_', 1)[1]),
        )
        sequences: List[List[float]] = []
        for record_key in record_keys:
            values = np.asarray(payload[record_key], dtype=np.float64)
            if values.ndim == 2 and values.shape[1] == 1:
                values = values[:, 0]
            sequences.append(values.reshape(-1).tolist())
        return sequences

def _compute_sequence_comparison(reference_sequences: Sequence[Sequence[float]],
                                 candidate_sequences: Sequence[Sequence[float]]) -> Dict[str, Any]:
    if len(reference_sequences) != len(candidate_sequences):
        raise ValueError(
            f'序列记录数不匹配，reference={len(reference_sequences)}，candidate={len(candidate_sequences)}'
        )

    reference_arrays = [np.asarray(sequence, dtype=np.float64) for sequence in reference_sequences]
    candidate_arrays = [np.asarray(sequence, dtype=np.float64) for sequence in candidate_sequences]
    for index, (reference_array, candidate_array) in enumerate(zip(reference_arrays, candidate_arrays)):
        if reference_array.shape != candidate_array.shape:
            raise ValueError(
                f'第 {index} 条序列形状不匹配，reference={reference_array.shape}，candidate={candidate_array.shape}'
            )

    reference_flat = np.concatenate(reference_arrays) if reference_arrays else np.asarray([], dtype=np.float64)
    candidate_flat = np.concatenate(candidate_arrays) if candidate_arrays else np.asarray([], dtype=np.float64)
    diff_flat = candidate_flat - reference_flat
    return {
        'record_count': len(reference_arrays),
        'sample_count': int(diff_flat.size),
        'mae': float(np.mean(np.abs(diff_flat))) if diff_flat.size else 0.0,
        'rmse': float(np.sqrt(np.mean(np.square(diff_flat)))) if diff_flat.size else 0.0,
        'max_abs_error': float(np.max(np.abs(diff_flat))) if diff_flat.size else 0.0,
    }

def _aggregate_run_results(run_results: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    host_elapsed = [float(item['workflow'].get('run', {}).get('elapsed_seconds', 0.0)) for item in run_results]
    measurement_values = [
        float(item['parsed_output']['measurement_per_iter'])
        for item in run_results
        if 'measurement_per_iter' in item['parsed_output']
    ]
    cycle_values = [
        int(item['parsed_output']['cycles_per_iter'])
        for item in run_results
        if 'cycles_per_iter' in item['parsed_output'] and int(item['parsed_output']['cycles_per_iter']) > 0
    ]
    measurement_sources = sorted({
        str(item['parsed_output']['timer_source'])
        for item in run_results
        if 'timer_source' in item['parsed_output']
    })
    mae_values = [
        float(item['comparison']['mae'])
        for item in run_results
        if 'comparison' in item and 'mae' in item['comparison']
    ]

    aggregated: Dict[str, Any] = {
        'run_count': len(run_results),
        'avg_host_elapsed_seconds': sum(host_elapsed) / len(host_elapsed) if host_elapsed else 0.0,
    }
    if measurement_values:
        aggregated['avg_measurement_per_iter'] = sum(measurement_values) / len(measurement_values)
    if measurement_sources:
        aggregated['measurement_sources'] = measurement_sources
    if cycle_values:
        aggregated['avg_cycles_per_iter'] = sum(cycle_values) / len(cycle_values)
    if mae_values:
        aggregated['avg_mae'] = sum(mae_values) / len(mae_values)
    return aggregated

def _summarize_qemu_run_workflow(run_workflow: Dict[str, Any]) -> Dict[str, Any]:
    run_details = dict(run_workflow.get('run', {}))
    return {
        'exit_code': int(run_workflow.get('exit_code', 1)),
        'timed_out': bool(run_details.get('timed_out', False)),
        'elapsed_seconds': float(run_details.get('elapsed_seconds', 0.0)),
    }

def _summarize_parsed_output(parsed_output: Dict[str, Any]) -> Dict[str, Any]:
    return {
        key: value
        for key, value in parsed_output.items()
        if not str(key).startswith('validation_')
    }

def _collect_output_files(*paths: Path) -> List[str]:
    output_files: List[str] = []
    for path in paths:
        if path.exists():
            output_files.append(_relative_or_str(path))
    return output_files

def _relative_or_str(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT.resolve())).replace('\\', '/')
    except ValueError:
        return str(path)

def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as file_obj:
        json.dump(payload, file_obj, indent=2, ensure_ascii=False)

def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')

def _copy_runtime_template(filename: str, target: Path) -> None:
    source = QEMU_HELLO_TEMPLATE_DIR / filename
    if not source.exists():
        raise FileNotFoundError(f'QEMU 模板文件不存在: {source}')
    target.write_text(source.read_text(encoding='utf-8'), encoding='utf-8')
